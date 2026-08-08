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
from datetime import datetime, timezone
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
OBLIGATIONS_PROJECTION_SCHEMA_PATH = (
    ROOT / "schemas" / "operational-obligations-projection.schema.json"
)
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
FORBIDDEN_ACTION_MARKERS = ("`", "$(", "&&", "||", "://", "\n", "\r")
FORBIDDEN_PUBLIC_TEXT_MARKERS = ("`", "://", "/home/", "/share/", "/etc/", "\\")


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


def parse_utc_timestamp(value: str) -> datetime:
    if not isinstance(value, str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z", value
    ):
        raise ValueError(f"{value!r} is not a strict UTC RFC3339 timestamp")
    return datetime.fromisoformat(value[:-1] + "+00:00")


def occurrence_is_terminal(occurrence: dict[str, Any]) -> bool:
    evidence = occurrence.get("evidence")
    if isinstance(evidence, dict) and evidence.get("result") == "verified":
        return True
    return isinstance(occurrence.get("resolution"), dict)


def occurrence_sort_key(
    series_id: str, occurrence: dict[str, Any]
) -> tuple[datetime, datetime, str, str]:
    """Canonical total order for consumer selection; ids are opaque tie-breakers."""
    return (
        parse_utc_timestamp(occurrence.get("due_at")),
        parse_utc_timestamp(occurrence.get("starts_at")),
        series_id,
        str(occurrence.get("id", "")),
    )


def latest_occurrence(
    obligation: dict[str, Any],
) -> dict[str, Any] | None:
    """Select the last materialized occurrence within one series."""
    occurrences = [
        occurrence
        for occurrence in obligation.get("occurrences", [])
        if isinstance(occurrence, dict)
    ]
    if not occurrences:
        return None
    return max(
        occurrences,
        key=lambda occurrence: occurrence_sort_key("", occurrence),
    )


def derive_occurrence_state(
    occurrence: dict[str, Any], now: datetime
) -> dict[str, str | None]:
    """Reference derivation for time, result, and completed timeliness."""
    evidence = occurrence.get("evidence")
    evidence_result = evidence.get("result") if isinstance(evidence, dict) else None
    resolution = occurrence.get("resolution")
    resolution_type = (
        resolution.get("type") if isinstance(resolution, dict) else None
    )
    if evidence_result == "verified":
        due_at = parse_utc_timestamp(occurrence["due_at"])
        observed_at_value = evidence.get("observed_at")
        timeliness = "indeterminate"
        if isinstance(observed_at_value, str):
            observed_at = parse_utc_timestamp(observed_at_value)
            timeliness = "on_time" if observed_at <= due_at else "late"
        return {
            "time_state": None,
            "result_state": "completed",
            "timeliness": timeliness,
        }
    if resolution_type in {"cancelled", "superseded"}:
        return {
            "time_state": None,
            "result_state": resolution_type,
            "timeliness": None,
        }
    starts_at = parse_utc_timestamp(occurrence["starts_at"])
    due_at = parse_utc_timestamp(occurrence["due_at"])
    if now < starts_at:
        time_state = "future"
    elif now <= due_at:
        time_state = "pending"
    else:
        time_state = "overdue"
    return {
        "time_state": time_state,
        "result_state": "open",
        "timeliness": None,
    }


def select_next_occurrence(
    obligations: list[dict[str, Any]],
) -> tuple[str, dict[str, Any]] | None:
    open_occurrences = [
        (str(obligation.get("id", "")), occurrence)
        for obligation in obligations
        if isinstance(obligation, dict)
        for occurrence in obligation.get("occurrences", [])
        if isinstance(occurrence, dict) and not occurrence_is_terminal(occurrence)
    ]
    if not open_occurrences:
        return None
    return min(
        open_occurrences,
        key=lambda item: occurrence_sort_key(item[0], item[1]),
    )


def derive_series_state(
    obligation: dict[str, Any], now: datetime
) -> str | None:
    """Derive recurring-series state; one-time obligations have no series state."""
    if obligation.get("kind") != "recurring":
        return None
    occurrences = [
        occurrence
        for occurrence in obligation.get("occurrences", [])
        if isinstance(occurrence, dict)
    ]
    if any(not occurrence_is_terminal(occurrence) for occurrence in occurrences):
        return "active"
    horizon_at = obligation.get("horizon_at")
    if isinstance(horizon_at, str) and now >= parse_utc_timestamp(horizon_at):
        return "period_ended"
    return "materialization_required"


def derive_projection_channel_state(
    publisher: dict[str, Any], now: datetime
) -> str:
    generated_at = parse_utc_timestamp(publisher["generated_at"])
    stale_after = duration_seconds(publisher["stale_after"])
    age = (now.astimezone(timezone.utc) - generated_at).total_seconds()
    return "fresh" if age <= stale_after else "stale"


def projection_can_authoritatively_withdraw(
    projection: dict[str, Any], channel_state: str, project_id: str
) -> bool:
    """Only a fresh, valid, complete in-scope snapshot can prove omission."""
    scope = projection.get("scope")
    return bool(
        channel_state == "fresh"
        and isinstance(scope, dict)
        and scope.get("complete") is True
        and project_id in scope.get("project_ids", [])
    )


def select_effective_projection(
    last_valid: dict[str, Any] | None,
    candidate: dict[str, Any] | None,
    channel_state: str,
) -> tuple[dict[str, Any] | None, str]:
    """Apply the operational projection's fail-closed retention rule."""
    if candidate is not None and channel_state == "fresh":
        return candidate, "current"
    if last_valid is not None:
        return last_valid, "retained"
    if candidate is not None and channel_state == "stale":
        return candidate, "stale"
    return None, channel_state


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


def obligations_from_contract(
    contract: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    obligations: dict[str, dict[str, Any]] = {}
    for index, obligation in enumerate(contract.get("operational_obligations", [])):
        if not isinstance(obligation, dict):
            continue
        obligation_id = obligation.get("id")
        if not isinstance(obligation_id, str):
            continue
        if obligation_id in obligations:
            raise ValueError(
                "$.operational_obligations"
                f"[{index}].id: duplicate obligation series id {obligation_id!r}"
            )
        obligations[obligation_id] = obligation
    return obligations


def obligation_semantic_errors(
    obligations: dict[str, dict[str, Any]], runbook_keys: set[str]
) -> list[str]:
    errors: list[str] = []
    for obligation_id, obligation in obligations.items():
        runbook_ref = obligation.get("runbook_ref")
        if isinstance(runbook_ref, str) and runbook_ref not in runbook_keys:
            errors.append(
                f"obligation {obligation_id!r}: runbook_ref {runbook_ref!r} "
                "is not declared in $.runbooks"
            )
        action = obligation.get("action")
        if isinstance(action, str):
            marker = next(
                (item for item in FORBIDDEN_ACTION_MARKERS if item in action), None
            )
            if marker is not None:
                errors.append(
                    f"obligation {obligation_id!r}: action contains forbidden "
                    f"executable marker {marker!r}"
                )
        requirement = obligation.get("evidence", {}).get("requirement")
        if isinstance(requirement, str):
            marker = next(
                (
                    item
                    for item in FORBIDDEN_PUBLIC_TEXT_MARKERS
                    if item in requirement
                ),
                None,
            )
            if marker is not None:
                errors.append(
                    f"obligation {obligation_id!r}: evidence requirement "
                    f"contains non-sanitized marker {marker!r}"
                )

        occurrence_ids: set[str] = set()
        horizon_value = obligation.get("horizon_at")
        try:
            horizon_at = (
                parse_utc_timestamp(horizon_value)
                if isinstance(horizon_value, str)
                else None
            )
        except ValueError as exc:
            errors.append(f"obligation {obligation_id!r}: {exc}")
            horizon_at = None
        for index, occurrence in enumerate(obligation.get("occurrences", [])):
            if not isinstance(occurrence, dict):
                continue
            occurrence_id = occurrence.get("id")
            if isinstance(occurrence_id, str):
                if occurrence_id in occurrence_ids:
                    errors.append(
                        f"obligation {obligation_id!r}: duplicate occurrence id "
                        f"{occurrence_id!r} at index {index}"
                    )
                occurrence_ids.add(occurrence_id)
            try:
                starts_at = parse_utc_timestamp(occurrence.get("starts_at"))
                due_at = parse_utc_timestamp(occurrence.get("due_at"))
            except ValueError as exc:
                errors.append(
                    f"obligation {obligation_id!r} occurrence "
                    f"{occurrence_id!r}: {exc}"
                )
                continue
            if starts_at >= due_at:
                errors.append(
                    f"obligation {obligation_id!r} occurrence "
                    f"{occurrence_id!r}: starts_at must be before due_at"
                )
            if horizon_at is not None and starts_at >= horizon_at:
                errors.append(
                    f"obligation {obligation_id!r} occurrence "
                    f"{occurrence_id!r}: starts_at must be before horizon_at"
                )
    return errors


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
    try:
        obligations = obligations_from_contract(contract)
    except ValueError as exc:
        errors.append(str(exc))
        obligations = {}
    errors.extend(obligation_semantic_errors(obligations, runbook_keys))
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
            "$: legacy private operational_review must not enter "
            "the reusable profile"
        )
    if "operational_obligations" in data:
        errors.append(
            "$: optional operational_obligations must remain absent from the "
            "reusable profile template"
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


def projection_semantic_errors(
    projection: dict[str, Any], contract: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    publisher = projection.get("publisher")
    if isinstance(publisher, dict):
        stale_after = publisher.get("stale_after")
        if isinstance(stale_after, str):
            try:
                if duration_seconds(stale_after) <= 0:
                    errors.append("$.publisher.stale_after: must be greater than zero")
            except ValueError as exc:
                errors.append(f"$.publisher.stale_after: {exc}")

    scope = projection.get("scope")
    scoped_ids = (
        scope.get("project_ids", []) if isinstance(scope, dict) else []
    )
    projects = projection.get("projects")
    project_items = projects if isinstance(projects, list) else []
    project_ids = [
        project.get("id")
        for project in project_items
        if isinstance(project, dict) and isinstance(project.get("id"), str)
    ]
    duplicate_projects = sorted(
        {project_id for project_id in project_ids if project_ids.count(project_id) > 1}
    )
    if duplicate_projects:
        errors.append(
            "$.projects: duplicate project ids: " + ", ".join(duplicate_projects)
        )
    if sorted(scoped_ids) != sorted(project_ids):
        errors.append(
            "$.scope.project_ids: must exactly match the complete $.projects set"
        )

    contract_id = contract.get("id")
    if contract_id not in scoped_ids:
        errors.append(
            f"$.scope.project_ids: validated contract id {contract_id!r} is not "
            "included in the complete projection scope"
        )
        return errors
    projected_project = next(
        (
            project
            for project in project_items
            if isinstance(project, dict) and project.get("id") == contract_id
        ),
        None,
    )
    if not isinstance(projected_project, dict):
        return errors

    try:
        declared_obligations = obligations_from_contract(contract)
    except ValueError as exc:
        errors.append(str(exc))
        declared_obligations = {}

    projected_list = projected_project.get("obligations")
    projected_items = projected_list if isinstance(projected_list, list) else []
    projected_ids = [
        obligation.get("id")
        for obligation in projected_items
        if isinstance(obligation, dict) and isinstance(obligation.get("id"), str)
    ]
    duplicates = sorted(
        {item for item in projected_ids if projected_ids.count(item) > 1}
    )
    if duplicates:
        errors.append(
            f"project {contract_id!r}: duplicate projected obligation ids: "
            + ", ".join(duplicates)
        )
    projected_obligations = {
        obligation["id"]: obligation
        for obligation in projected_items
        if isinstance(obligation, dict) and isinstance(obligation.get("id"), str)
    }
    if set(projected_obligations) != set(declared_obligations):
        errors.append(
            f"project {contract_id!r}: projected obligation ids must exactly "
            "match the accepted project declaration"
        )

    declaration_fields = (
        "kind",
        "responsible",
        "action",
        "runbook_ref",
        "horizon_at",
        "evidence",
    )
    for obligation_id, projected in projected_obligations.items():
        declared = declared_obligations.get(obligation_id)
        if not isinstance(declared, dict):
            continue
        for field in declaration_fields:
            if projected.get(field) != declared.get(field):
                errors.append(
                    f"project {contract_id!r} obligation {obligation_id!r}: "
                    f"projected {field} does not match the project declaration"
                )

        declared_occurrences = {
            occurrence.get("id"): occurrence
            for occurrence in declared.get("occurrences", [])
            if isinstance(occurrence, dict)
            and isinstance(occurrence.get("id"), str)
        }
        projected_occurrence_list = projected.get("occurrences")
        projected_occurrence_items = (
            projected_occurrence_list
            if isinstance(projected_occurrence_list, list)
            else []
        )
        projected_occurrence_ids = [
            occurrence.get("id")
            for occurrence in projected_occurrence_items
            if isinstance(occurrence, dict)
            and isinstance(occurrence.get("id"), str)
        ]
        duplicate_occurrences = sorted(
            {
                item
                for item in projected_occurrence_ids
                if projected_occurrence_ids.count(item) > 1
            }
        )
        if duplicate_occurrences:
            errors.append(
                f"project {contract_id!r} obligation {obligation_id!r}: "
                "duplicate projected occurrence ids: "
                + ", ".join(duplicate_occurrences)
            )
        projected_occurrences = {
            occurrence["id"]: occurrence
            for occurrence in projected_occurrence_items
            if isinstance(occurrence, dict)
            and isinstance(occurrence.get("id"), str)
        }
        if set(projected_occurrences) != set(declared_occurrences):
            errors.append(
                f"project {contract_id!r} obligation {obligation_id!r}: "
                "projected occurrence ids must exactly match the project declaration"
            )
        for occurrence_id, occurrence in projected_occurrences.items():
            declared_occurrence = declared_occurrences.get(occurrence_id)
            if isinstance(declared_occurrence, dict):
                for field in ("starts_at", "due_at"):
                    if occurrence.get(field) != declared_occurrence.get(field):
                        errors.append(
                            f"project {contract_id!r} obligation {obligation_id!r} "
                            f"occurrence {occurrence_id!r}: projected {field} "
                            "does not match the project declaration"
                        )
            evidence = occurrence.get("evidence")
            if isinstance(evidence, dict):
                authority = evidence.get("authority")
                if authority is not None and authority != contract_id:
                    errors.append(
                        f"project {contract_id!r} obligation {obligation_id!r} "
                        f"occurrence {occurrence_id!r}: evidence authority must "
                        "match the project id"
                    )
                summary = evidence.get("summary")
                if isinstance(summary, str):
                    marker = next(
                        (
                            item
                            for item in FORBIDDEN_PUBLIC_TEXT_MARKERS
                            if item in summary
                        ),
                        None,
                    )
                    if marker is not None:
                        errors.append(
                            f"project {contract_id!r} obligation {obligation_id!r} "
                            f"occurrence {occurrence_id!r}: evidence summary "
                            f"contains non-sanitized marker {marker!r}"
                        )
            resolution = occurrence.get("resolution")
            if isinstance(resolution, dict):
                if resolution.get("authority") != contract_id:
                    errors.append(
                        f"project {contract_id!r} obligation {obligation_id!r} "
                        f"occurrence {occurrence_id!r}: resolution authority must "
                        "match the project id"
                    )
                if isinstance(evidence, dict) and evidence.get("result") == "verified":
                    errors.append(
                        f"project {contract_id!r} obligation {obligation_id!r} "
                        f"occurrence {occurrence_id!r}: verified completion evidence "
                        "cannot coexist with cancellation or supersession"
                    )
                if resolution.get("type") == "superseded":
                    replacement = resolution.get("replacement_occurrence_id")
                    if replacement == occurrence_id:
                        errors.append(
                            f"project {contract_id!r} obligation {obligation_id!r} "
                            f"occurrence {occurrence_id!r}: supersession cannot "
                            "replace an occurrence with itself"
                        )
                    elif replacement not in projected_occurrences:
                        errors.append(
                            f"project {contract_id!r} obligation {obligation_id!r} "
                            f"occurrence {occurrence_id!r}: replacement occurrence "
                            f"{replacement!r} is not present in the same series"
                        )
    return errors


def projection_identity_mutation_errors(
    previous: dict[str, Any], current: dict[str, Any]
) -> list[str]:
    """Reject reuse of stable series/occurrence ids with changed identity data."""
    errors: list[str] = []
    previous_projects = {
        project.get("id"): project
        for project in previous.get("projects", [])
        if isinstance(project, dict) and isinstance(project.get("id"), str)
    }
    current_projects = {
        project.get("id"): project
        for project in current.get("projects", [])
        if isinstance(project, dict) and isinstance(project.get("id"), str)
    }
    for project_id in sorted(set(previous_projects).intersection(current_projects)):
        previous_obligations = {
            obligation.get("id"): obligation
            for obligation in previous_projects[project_id].get("obligations", [])
            if isinstance(obligation, dict)
            and isinstance(obligation.get("id"), str)
        }
        current_obligations = {
            obligation.get("id"): obligation
            for obligation in current_projects[project_id].get("obligations", [])
            if isinstance(obligation, dict)
            and isinstance(obligation.get("id"), str)
        }
        for obligation_id in sorted(
            set(previous_obligations).intersection(current_obligations)
        ):
            previous_obligation = previous_obligations[obligation_id]
            current_obligation = current_obligations[obligation_id]
            if previous_obligation.get("kind") != current_obligation.get("kind"):
                errors.append(
                    f"project {project_id!r} obligation {obligation_id!r}: stable "
                    "series id cannot change kind"
                )
            previous_occurrences = {
                occurrence.get("id"): occurrence
                for occurrence in previous_obligation.get("occurrences", [])
                if isinstance(occurrence, dict)
                and isinstance(occurrence.get("id"), str)
            }
            current_occurrences = {
                occurrence.get("id"): occurrence
                for occurrence in current_obligation.get("occurrences", [])
                if isinstance(occurrence, dict)
                and isinstance(occurrence.get("id"), str)
            }
            for occurrence_id in sorted(
                set(previous_occurrences).intersection(current_occurrences)
            ):
                for field in ("starts_at", "due_at"):
                    if previous_occurrences[occurrence_id].get(field) != (
                        current_occurrences[occurrence_id].get(field)
                    ):
                        errors.append(
                            f"project {project_id!r} obligation {obligation_id!r} "
                            f"occurrence {occurrence_id!r}: stable occurrence id "
                            f"cannot change {field}; supersede it with a new id"
                        )
    return errors


def validate_obligations_projection(
    path: Path,
    contract: dict[str, Any],
    projection_schema: Any,
) -> list[str]:
    try:
        projection = load_json(path)
    except ValueError as exc:
        return [str(exc)]
    errors = schema_errors(projection, projection_schema)
    if isinstance(projection, dict):
        errors.extend(projection_semantic_errors(projection, contract))
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate infra.contract.yml, optional project-owned status snapshots, "
            "and an optional accepted operational-obligations projection against "
            "the canonical Home Infra Protocol schemas."
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
        "--obligations-projection",
        type=Path,
        help=(
            "validate a complete sanitized operational-obligations projection "
            "and join its project declaration to --contract"
        ),
    )
    parser.add_argument(
        "--previous-obligations-projection",
        type=Path,
        help=(
            "compare the prior accepted projection with --obligations-projection "
            "and reject stable identity reuse with changed kind or windows"
        ),
    )
    parser.add_argument(
        "--template",
        action="store_true",
        help="validate the canonical TODO-bearing homelab profile template",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.template and (
        args.status
        or args.obligations_projection
        or args.previous_obligations_projection
    ):
        print(
            "ERROR usage: --template cannot be combined with --status or "
            "either obligations-projection option",
            file=sys.stderr,
        )
        return 2
    if (
        args.previous_obligations_projection is not None
        and args.obligations_projection is None
    ):
        print(
            "ERROR usage: --previous-obligations-projection requires "
            "--obligations-projection",
            file=sys.stderr,
        )
        return 2

    try:
        contract_text, contract = load_yaml(args.contract)
        project_schema = load_json(PROJECT_SCHEMA_PATH)
        status_schema = load_json(STATUS_SCHEMA_PATH)
        projection_schema = load_json(OBLIGATIONS_PROJECTION_SCHEMA_PATH)
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

    if args.obligations_projection is not None:
        if not isinstance(contract, dict):
            errors.append("obligations projection requires a valid contract mapping")
        else:
            projection_errors = validate_obligations_projection(
                args.obligations_projection,
                contract,
                projection_schema,
            )
            errors.extend(
                f"obligations-projection {error}" for error in projection_errors
            )

    if args.previous_obligations_projection is not None:
        try:
            previous_projection = load_json(args.previous_obligations_projection)
            current_projection = load_json(args.obligations_projection)
        except ValueError as exc:
            errors.append(f"projection-transition {exc}")
        else:
            previous_errors = schema_errors(
                previous_projection, projection_schema
            )
            errors.extend(
                f"previous-obligations-projection {error}"
                for error in previous_errors
            )
            if (
                isinstance(previous_projection, dict)
                and isinstance(current_projection, dict)
            ):
                transition_errors = projection_identity_mutation_errors(
                    previous_projection, current_projection
                )
                errors.extend(
                    f"projection-transition {error}"
                    for error in transition_errors
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
    if args.obligations_projection is not None:
        print(f"PASS obligations projection: {args.obligations_projection}")
    if args.previous_obligations_projection is not None:
        print(
            "PASS obligations projection identity transition: "
            f"{args.previous_obligations_projection} -> "
            f"{args.obligations_projection}"
        )
    print(
        "PASS project interface: 1 contract, "
        f"{len(args.status)} status snapshot(s), "
        f"{1 if args.obligations_projection is not None else 0} obligations projection(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
