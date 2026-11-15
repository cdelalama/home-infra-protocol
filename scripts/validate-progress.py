#!/usr/bin/env python3
"""Validate Progress record shape and optional published-to-candidate transitions.

This canonical protocol tool never resolves evidence references, contacts a
service, executes project content, or certifies delivery or operator authority.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas/progress-record.schema.json").read_text())
FORMATS = FormatChecker()


@FORMATS.checks("date-time", raises=ValueError)
def _utc_calendar_date(value: Any) -> bool:
    # FormatChecker's default RFC3339 plugin may be absent. Never silently
    # accept an impossible date merely because an optional package is missing.
    if not isinstance(value, str):
        return True  # JSON Schema's type constraint reports this separately.
    datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    return True


VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FORMATS)
MAX_BYTES = 262_144


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _invalid_constant(_: str) -> None:
    raise ValueError("non-finite JSON number")


def load_record(path: Path) -> Any:
    with path.open("rb") as source:
        raw = source.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("record exceeds 262144 bytes")
    return json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object,
                      parse_constant=_invalid_constant)


def _path(parts: Any) -> str:
    return "$" + "".join(f"[{p}]" if isinstance(p, int) else f".{p}" for p in parts)


def _reference_errors(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        if set(value) == {"project_id", "path", "revision", "anchor"}:
            # No resolution: these are data, never filenames to open or commands.
            if any(part in ("", ".", "..") for part in value["path"].split("/")):
                errors.append(f"{path}.path: reference must be a normalized relative path")
        for key, child in value.items():
            errors.extend(_reference_errors(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_reference_errors(child, f"{path}[{index}]"))
    return errors


def validate_record(record: Any) -> list[str]:
    # Do not print rejected values: a malformed record may contain private text.
    errors = [f"{_path(e.absolute_path)}: violates {e.validator}"
              for e in sorted(VALIDATOR.iter_errors(record),
                              key=lambda e: tuple(map(str, e.absolute_path)))]
    if errors:
        return errors
    errors.extend(_reference_errors(record))
    target = record["target"]
    criteria = record["criteria"]
    if target["status"] == "undefined":
        if any(target[k] is not None for k in ("outcome", "scope_ref", "acceptance_ref")) or criteria:
            errors.append("$.target: undefined scope cannot carry an outcome, authority or criteria")
    elif target["outcome"] is None:
        errors.append("$.target.outcome: defined scope needs an outcome")
    if target["status"] == "proposed" and target["acceptance_ref"] is not None:
        errors.append("$.target.acceptance_ref: proposed scope cannot claim acceptance")
    if target["status"] == "accepted":
        if target["scope_ref"] is None or target["acceptance_ref"] is None or not criteria:
            errors.append("$.target: accepted scope needs pinned scope, acceptance and criteria")
        if any(c["requirement_ref"] is None for c in criteria):
            errors.append("$.criteria: accepted requirements need pinned definitions")
    if record["delivery_claim"] is not None and target["status"] != "accepted":
        errors.append("$.delivery_claim: a delivery claim needs an accepted target")
    if record["delivery_claim"] is not None and record["delivery_claim"]["scope_version"] != target["scope_version"]:
        errors.append("$.delivery_claim.scope_version: claim must match the current target scope")
    if (target["status"] == "accepted" and any(c["status"] == "pending" for c in criteria)
            and not any(record[k] for k in ("next_action", "blockers", "pause"))):
        errors.append("$.next_action: pending accepted work needs an action, blocker or pause")
    ids = [c["id"] for c in criteria]
    if len(ids) != len(set(ids)):
        errors.append("$.criteria: duplicate criterion identity")
    for index, criterion in enumerate(criteria):
        if criterion["status"] == "verified":
            if criterion["verified_at"] is None or not criterion["evidence_refs"]:
                errors.append(f"$.criteria[{index}]: verified claim needs date and evidence references")
        elif criterion["verified_at"] is not None or criterion["evidence_refs"]:
            errors.append(f"$.criteria[{index}]: pending criterion cannot carry a current verified result")
    action = record["next_action"]
    if action and action["criterion_id"] is not None and action["criterion_id"] not in ids:
        errors.append("$.next_action.criterion_id: unknown criterion")
    blocker_ids = [b["id"] for b in record["blockers"]]
    if len(blocker_ids) != len(set(blocker_ids)):
        errors.append("$.blockers: duplicate blocker identity")
    for index, blocker in enumerate(record["blockers"]):
        refs = blocker["criterion_ids"]
        if len(refs) != len(set(refs)) or not set(refs).issubset(ids):
            errors.append(f"$.blockers[{index}].criterion_ids: duplicate or unknown criterion")
    return errors


def _scope_identity(record: dict[str, Any]) -> dict[str, Any]:
    return {"scope_ref": record["target"]["scope_ref"],
            "criteria": {c["id"]: c["requirement_ref"] for c in record["criteria"]}}


def decision_identity(ref: Any) -> Any:
    return None if ref is None else tuple(ref[k] for k in ("project_id", "path", "anchor"))


def validate_transition(previous: Any, candidate: Any) -> list[str]:
    errors = ["previous " + e for e in validate_record(previous)] + validate_record(candidate)
    if errors:
        return errors
    if previous["project_id"] != candidate["project_id"] or previous["target"]["id"] != candidate["target"]["id"]:
        return ["$.target: cannot compare different project/release identities"]
    old, new = previous["target"], candidate["target"]
    if new["scope_version"] < old["scope_version"]:
        errors.append("$.target.scope_version: cannot decrease")
    if old["status"] == "accepted":
        if new["status"] != "accepted":
            errors.append("$.target.status: keep accepted scope; draft alternatives separately")
        if _scope_identity(previous) != _scope_identity(candidate):
            if new["scope_version"] <= old["scope_version"]:
                errors.append("$.target.scope_version: changed accepted scope needs a new version")
            if decision_identity(new["acceptance_ref"]) == decision_identity(old["acceptance_ref"]) or new["acceptance_ref"] is None:
                errors.append("$.target.acceptance_ref: changed accepted scope needs a distinct decision identity")
        elif (new["scope_version"] != old["scope_version"] or new["acceptance_ref"] != old["acceptance_ref"]):
            errors.append("$.target: unchanged scope must retain its version and acceptance reference")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", required=True, type=Path)
    parser.add_argument("--previous", type=Path,
                        help="Previously published record acquired by the trusted caller")
    args = parser.parse_args()
    try:
        record = load_record(args.record)
        errors = (validate_transition(load_record(args.previous), record)
                  if args.previous else validate_record(record))
    except (OSError, ValueError, RecursionError):
        print(json.dumps({"validation": "unavailable", "reason": "input could not be read as bounded strict JSON",
                          "authority": "not_assessed", "delivery": "not_assessed"}))
        return 2
    print(json.dumps({"validation": "invalid" if errors else "valid",
                      "assessment": "shape_and_transition" if args.previous else "shape_only",
                      "authority": "not_assessed", "delivery": "not_assessed", "errors": errors}))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
