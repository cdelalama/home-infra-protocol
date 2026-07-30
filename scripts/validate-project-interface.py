#!/usr/bin/env python3
"""Validate a Home Infra project contract and optional status snapshots.

The validator lives with the protocol schemas. Orchestrators and adopters call
it across the repository boundary; they must not copy it into downstream
projects.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

try:
    import yaml
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError as exc:  # pragma: no cover - exercised only on missing deps
    print(
        "ERROR dependencies: install Python packages PyYAML and jsonschema",
        file=sys.stderr,
    )
    raise SystemExit(2) from exc


ROOT = Path(__file__).resolve().parents[1]
PROJECT_SCHEMA_PATH = ROOT / "schemas" / "project-contract.schema.json"
STATUS_SCHEMA_PATH = ROOT / "schemas" / "status-snapshot.schema.json"
VERSION_PATH = ROOT / "VERSION"
PROFILE_VERSION_RE = re.compile(
    r"^# home-infra-protocol-profile: (?P<version>\d+\.\d+\.\d+)\s*$",
    re.MULTILINE,
)
FIXED_DURATION_RE = re.compile(
    r"^P"
    r"(?:(?P<weeks>\d+(?:\.\d+)?)W)?"
    r"(?:(?P<days>\d+(?:\.\d+)?)D)?"
    r"(?:T"
    r"(?:(?P<hours>\d+(?:\.\d+)?)H)?"
    r"(?:(?P<minutes>\d+(?:\.\d+)?)M)?"
    r"(?:(?P<seconds>\d+(?:\.\d+)?)S)?"
    r")?$"
)
FORBIDDEN_PRODUCER_FRESHNESS_FIELDS = {"freshness", "is_stale", "stale"}
FORBIDDEN_CAPABILITY_OBSERVATION_FIELDS = {
    "support",
    "policy",
    "risk",
    "scope",
    "reason_code",
    "enablement",
    "review_at",
    "observation_job_id",
}


@dataclass(frozen=True)
class StatusInput:
    job_id: str
    path: Path


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"{path}: file not found") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON: {exc.msg}") from exc


def load_yaml(path: Path) -> tuple[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"{path}: file not found") from exc
    try:
        return text, yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ValueError(f"{path}: invalid YAML: {exc}") from exc


def format_path(parts: Iterable[Any]) -> str:
    rendered = "$"
    for part in parts:
        if isinstance(part, int):
            rendered += f"[{part}]"
        else:
            rendered += f".{part}"
    return rendered


def schema_errors(instance: Any, schema: Any) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [
        f"{format_path(error.absolute_path)}: {error.message}"
        for error in sorted(
            validator.iter_errors(instance),
            key=lambda item: tuple(str(part) for part in item.absolute_path),
        )
    ]


def find_todos(value: Any, path: tuple[Any, ...] = ()) -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            errors.extend(find_todos(child, (*path, key)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(find_todos(child, (*path, index)))
    elif isinstance(value, str) and "TODO" in value.upper():
        errors.append(f"{format_path(path)}: unresolved TODO placeholder")
    return errors


def materialize_template(value: Any) -> Any:
    """Replace TODO tokens while preserving the starter's declared shape."""
    if isinstance(value, dict):
        return {key: materialize_template(child) for key, child in value.items()}
    if isinstance(value, list):
        return [materialize_template(child) for child in value]
    if isinstance(value, str):
        return value.replace("TODO", "example").replace("todo", "example")
    return value


def duration_seconds(value: str) -> float:
    match = FIXED_DURATION_RE.fullmatch(value)
    if not match or not any(match.groupdict().values()):
        raise ValueError(
            f"{value!r} is not a comparable fixed ISO 8601 duration; "
            "use weeks, days, hours, minutes, or seconds"
        )
    values = {
        key: float(raw) if raw is not None else 0.0
        for key, raw in match.groupdict().items()
    }
    return (
        values["weeks"] * 604800
        + values["days"] * 86400
        + values["hours"] * 3600
        + values["minutes"] * 60
        + values["seconds"]
    )


def jobs_from_contract(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    jobs: dict[str, dict[str, Any]] = {}
    for collection in ("sync_jobs", "telemetry_jobs"):
        for index, job in enumerate(contract.get(collection, [])):
            if not isinstance(job, dict):
                continue
            job_id = job.get("id")
            if isinstance(job_id, str):
                if job_id in jobs:
                    raise ValueError(
                        f"$.{collection}[{index}].id: duplicate job id {job_id!r}"
                    )
                jobs[job_id] = job
    return jobs


def capabilities_from_contract(
    contract: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    capabilities: dict[str, dict[str, Any]] = {}
    for index, capability in enumerate(contract.get("capabilities", [])):
        if not isinstance(capability, dict):
            continue
        capability_id = capability.get("id")
        if not isinstance(capability_id, str):
            continue
        if capability_id in capabilities:
            raise ValueError(
                "$.capabilities"
                f"[{index}].id: duplicate capability id {capability_id!r}"
            )
        capabilities[capability_id] = capability
    return capabilities


def contract_semantic_errors(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    try:
        jobs = jobs_from_contract(contract)
    except ValueError as exc:
        errors.append(str(exc))
        jobs = {}

    for job_id, job in jobs.items():
        schedule = job.get("schedule")
        if not isinstance(schedule, dict):
            continue
        if schedule.get("mode") not in {"cron", "internal-loop"}:
            continue
        cadence = schedule.get("cadence")
        stale_after = job.get("stale_after")
        if not isinstance(cadence, str) or not isinstance(stale_after, str):
            continue
        try:
            cadence_seconds = duration_seconds(cadence)
            stale_seconds = duration_seconds(stale_after)
        except ValueError as exc:
            errors.append(f"job {job_id!r}: {exc}")
            continue
        if stale_seconds <= cadence_seconds:
            errors.append(
                f"job {job_id!r}: stale_after ({stale_after}) must be greater "
                f"than cadence ({cadence})"
            )

    try:
        capabilities = capabilities_from_contract(contract)
    except ValueError as exc:
        errors.append(str(exc))
        capabilities = {}

    telemetry_job_ids = {
        job.get("id")
        for job in contract.get("telemetry_jobs", [])
        if isinstance(job, dict) and isinstance(job.get("id"), str)
    }
    runbooks = contract.get("runbooks")
    runbook_keys = set(runbooks) if isinstance(runbooks, dict) else set()

    for capability_id, capability in capabilities.items():
        observation_job_id = capability.get("observation_job_id")
        if (
            isinstance(observation_job_id, str)
            and observation_job_id not in telemetry_job_ids
        ):
            errors.append(
                f"capability {capability_id!r}: observation_job_id "
                f"{observation_job_id!r} must reference a telemetry job"
            )

        support = capability.get("support")
        policy = capability.get("policy")
        if support == "unsupported" and policy != "disabled":
            errors.append(
                f"capability {capability_id!r}: unsupported capabilities "
                "must use policy 'disabled'"
            )

        scope = capability.get("scope")
        if policy == "sandbox_only":
            if not isinstance(scope, dict) or scope.get("mode") != "sandbox":
                errors.append(
                    f"capability {capability_id!r}: sandbox_only policy requires "
                    "scope.mode 'sandbox'"
                )

        enablement = capability.get("enablement")
        if isinstance(enablement, dict):
            runbook = enablement.get("runbook")
            if isinstance(runbook, str) and runbook not in runbook_keys:
                errors.append(
                    f"capability {capability_id!r}: enablement runbook "
                    f"{runbook!r} is not declared in $.runbooks"
                )
    return errors


def validate_template(
    path: Path,
    text: str,
    data: Any,
    project_schema: Any,
) -> list[str]:
    errors: list[str] = []
    marker = PROFILE_VERSION_RE.search(text)
    protocol_version = VERSION_PATH.read_text(encoding="utf-8").strip()
    if marker is None:
        errors.append(
            "$: missing '# home-infra-protocol-profile: X.Y.Z' marker"
        )
    elif marker.group("version") != protocol_version:
        errors.append(
            "$: profile marker "
            f"{marker.group('version')} does not match protocol {protocol_version}"
        )

    if not isinstance(data, dict):
        return [*errors, "$: template root must be a mapping"]

    expected_shapes = {
        "id": str,
        "name": str,
        "repository": str,
        "services": list,
        "sync_jobs": list,
        "telemetry_jobs": list,
        "capabilities": list,
        "runbooks": dict,
        "secret_refs": list,
    }
    for key, expected_type in expected_shapes.items():
        if key not in data:
            errors.append(f"$.{key}: required profile template section is missing")
        elif not isinstance(data[key], expected_type):
            errors.append(
                f"$.{key}: expected {expected_type.__name__} in profile template"
            )

    for collection in ("sync_jobs", "telemetry_jobs"):
        value = data.get(collection)
        if isinstance(value, list) and not value:
            errors.append(
                f"$.{collection}: profile template must include one removable example"
            )
    capabilities = data.get("capabilities")
    if isinstance(capabilities, list) and not capabilities:
        errors.append(
            "$.capabilities: profile template must include one removable example"
        )

    if "operational_review" in text:
        errors.append(
            "$: operational_review is incubating privately and must not enter "
            "the reusable profile"
        )
    if "TODO" not in text:
        errors.append("$: profile template must retain explicit TODO placeholders")

    materialized = materialize_template(data)
    errors.extend(
        f"template {error}" for error in schema_errors(materialized, project_schema)
    )
    if isinstance(materialized, dict):
        errors.extend(
            f"template {error}"
            for error in contract_semantic_errors(materialized)
        )

    return errors


def parse_status_arg(raw: str) -> StatusInput:
    if "=" not in raw:
        raise argparse.ArgumentTypeError("expected JOB_ID=PATH")
    job_id, path = raw.split("=", 1)
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", job_id):
        raise argparse.ArgumentTypeError(f"invalid job id: {job_id!r}")
    if not path:
        raise argparse.ArgumentTypeError("status path is empty")
    return StatusInput(job_id=job_id, path=Path(path))


def validate_status(
    status_input: StatusInput,
    jobs: dict[str, dict[str, Any]],
    declared_capabilities: dict[str, dict[str, Any]],
    status_schema: Any,
) -> list[str]:
    if status_input.job_id not in jobs:
        return [
            f"$: status job {status_input.job_id!r} is not declared in the contract"
        ]

    try:
        snapshot = load_json(status_input.path)
    except ValueError as exc:
        return [str(exc)]
    errors = schema_errors(snapshot, status_schema)
    if isinstance(snapshot, dict):
        forbidden = sorted(
            FORBIDDEN_PRODUCER_FRESHNESS_FIELDS.intersection(snapshot)
        )
        if forbidden:
            errors.append(
                "$: producer snapshots must not declare consumer-derived "
                f"freshness fields: {', '.join(forbidden)}"
            )
        checks = snapshot.get("checks")
        if isinstance(checks, list):
            names = [
                check.get("name")
                for check in checks
                if isinstance(check, dict) and isinstance(check.get("name"), str)
            ]
            duplicates = sorted({name for name in names if names.count(name) > 1})
            if duplicates:
                errors.append(
                    "$.checks: duplicate stable check names: "
                    + ", ".join(duplicates)
                )

        observations = snapshot.get("capabilities")
        observed_ids: list[str] = []
        if isinstance(observations, list):
            for index, observation in enumerate(observations):
                if not isinstance(observation, dict):
                    continue
                capability_id = observation.get("id")
                if not isinstance(capability_id, str):
                    continue
                observed_ids.append(capability_id)
                declaration = declared_capabilities.get(capability_id)
                if declaration is None:
                    errors.append(
                        f"$.capabilities[{index}].id: capability "
                        f"{capability_id!r} is not declared in the contract"
                    )
                elif declaration.get("observation_job_id") != status_input.job_id:
                    errors.append(
                        f"$.capabilities[{index}].id: capability "
                        f"{capability_id!r} belongs to observation job "
                        f"{declaration.get('observation_job_id')!r}, not "
                        f"{status_input.job_id!r}"
                    )
                forbidden = sorted(
                    FORBIDDEN_CAPABILITY_OBSERVATION_FIELDS.intersection(
                        observation
                    )
                )
                if forbidden:
                    errors.append(
                        f"$.capabilities[{index}]: runtime capability evidence "
                        "must not redeclare project policy fields: "
                        + ", ".join(forbidden)
                    )

            duplicates = sorted(
                {
                    capability_id
                    for capability_id in observed_ids
                    if observed_ids.count(capability_id) > 1
                }
            )
            if duplicates:
                errors.append(
                    "$.capabilities: duplicate capability ids: "
                    + ", ".join(duplicates)
                )

        expected_ids = sorted(
            capability_id
            for capability_id, declaration in declared_capabilities.items()
            if declaration.get("observation_job_id") == status_input.job_id
        )
        missing_ids = sorted(set(expected_ids).difference(observed_ids))
        if missing_ids:
            errors.append(
                "$.capabilities: missing observations declared for this job: "
                + ", ".join(missing_ids)
            )
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate infra.contract.yml and optional project-owned status snapshots "
            "against the canonical Home Infra Protocol schemas."
        )
    )
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument(
        "--status",
        action="append",
        default=[],
        type=parse_status_arg,
        metavar="JOB_ID=PATH",
        help="validate a snapshot and join it to a declared job; repeatable",
    )
    parser.add_argument(
        "--template",
        action="store_true",
        help="validate the canonical TODO-bearing homelab profile template",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.template and args.status:
        print("ERROR usage: --template cannot be combined with --status", file=sys.stderr)
        return 2

    try:
        contract_text, contract = load_yaml(args.contract)
        project_schema = load_json(PROJECT_SCHEMA_PATH)
        status_schema = load_json(STATUS_SCHEMA_PATH)
    except ValueError as exc:
        print(f"ERROR load: {exc}", file=sys.stderr)
        return 2

    errors: list[str] = []
    if args.template:
        errors.extend(
            validate_template(
                args.contract,
                contract_text,
                contract,
                project_schema,
            )
        )
    elif not isinstance(contract, dict):
        errors.append("$: contract root must be a mapping")
    else:
        errors.extend(find_todos(contract))
        errors.extend(schema_errors(contract, project_schema))
        errors.extend(contract_semantic_errors(contract))

    jobs: dict[str, dict[str, Any]] = {}
    declared_capabilities: dict[str, dict[str, Any]] = {}
    if isinstance(contract, dict):
        try:
            jobs = jobs_from_contract(contract)
        except ValueError:
            pass
        try:
            declared_capabilities = capabilities_from_contract(contract)
        except ValueError:
            pass

    for status_input in args.status:
        status_errors = validate_status(
            status_input,
            jobs,
            declared_capabilities,
            status_schema,
        )
        errors.extend(
            f"status[{status_input.job_id}] {error}" for error in status_errors
        )

    if errors:
        for error in errors:
            print(f"FAIL {error}", file=sys.stderr)
        print(f"FAIL project interface: {len(errors)} error(s)", file=sys.stderr)
        return 1

    mode = "profile template" if args.template else "project contract"
    print(f"PASS {mode}: {args.contract}")
    for status_input in args.status:
        print(f"PASS status[{status_input.job_id}]: {status_input.path}")
    print(f"PASS project interface: 1 contract, {len(args.status)} status snapshot(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
