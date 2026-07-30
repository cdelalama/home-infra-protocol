import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate-project-interface.py"
TEMPLATE = ROOT / "integrations" / "dockit" / "templates" / "infra.contract.yml"


def valid_contract() -> dict:
    return {
        "id": "example-project",
        "name": "Example Project",
        "repository": "https://github.com/example/example-project",
        "services": ["example-service"],
        "sync_jobs": [],
        "telemetry_jobs": [
            {
                "id": "example-telemetry",
                "schedule": {"mode": "cron", "cadence": "PT24H"},
                "stale_after": "PT27H",
                "runtime": {
                    "host_id": "example-host",
                    "service_id": "example-service",
                },
                "status_url": "https://status.example.invalid/example.json",
            }
        ],
        "capabilities": [
            {
                "id": "messaging.channels",
                "label": "Channel messaging",
                "category": "messaging",
                "support": "supported",
                "policy": "enabled",
                "risk": "low",
                "scope": {"mode": "all"},
                "observation_job_id": "example-telemetry",
            },
            {
                "id": "workflows.execute",
                "label": "Workflow execution",
                "category": "automation",
                "support": "supported",
                "policy": "sandbox_only",
                "risk": "high",
                "scope": {
                    "mode": "sandbox",
                    "targets": ["example-playground"],
                },
                "reason_code": "production-runner-not-approved",
                "enablement": {
                    "mode": "operator_approval",
                    "target_policy": "approval_required",
                    "gate": "verify-runner-isolation",
                    "runbook": "capabilities",
                },
                "review_at": "2026-09-30T12:00:00Z",
                "observation_job_id": "example-telemetry",
            },
        ],
        "runbooks": {
            "verify": "docs/operations/VERIFY.md",
            "capabilities": "docs/operations/CAPABILITIES.md",
        },
        "secret_refs": [],
    }


def valid_status() -> dict:
    return {
        "observed_at": "2026-07-28T12:00:00Z",
        "next_run_at": "2026-07-29T12:00:00Z",
        "condition": "ok",
        "severity": "none",
        "summary": "The scheduled observation completed successfully.",
        "checks": [
            {
                "name": "producer-run",
                "label": "Producer run",
                "condition": "ok",
            }
        ],
        "capabilities": [
            {
                "id": "messaging.channels",
                "availability": "available",
                "verification": "serving",
                "summary": "Authenticated channel messaging passed.",
            },
            {
                "id": "workflows.execute",
                "availability": "available",
                "verification": "serving",
                "summary": "The isolated workflow runner accepted its canary.",
            },
        ],
    }


class ProjectInterfaceValidatorTest(unittest.TestCase):
    def run_validator(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def write_yaml(self, directory: Path, value: dict) -> Path:
        path = directory / "infra.contract.yml"
        path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")
        return path

    def write_json(self, directory: Path, value: dict) -> Path:
        path = directory / "status.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def test_canonical_profile_template_is_current(self) -> None:
        result = self.run_validator("--contract", str(TEMPLATE), "--template")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_profile_version_drift_fails(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            current_version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
            text = TEMPLATE.read_text(encoding="utf-8").replace(
                f"# home-infra-protocol-profile: {current_version}",
                "# home-infra-protocol-profile: 0.0.0",
            )
            path = directory / "infra.contract.yml"
            path.write_text(text, encoding="utf-8")
            result = self.run_validator("--contract", str(path), "--template")
        self.assertEqual(result.returncode, 1)
        self.assertIn(f"does not match protocol {current_version}", result.stderr)

    def test_profile_shape_drift_fails_schema_validation(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            text = TEMPLATE.read_text(encoding="utf-8").replace(
                "      host_id: TODO-host-id\n",
                "",
                1,
            )
            path = directory / "infra.contract.yml"
            path.write_text(text, encoding="utf-8")
            result = self.run_validator("--contract", str(path), "--template")
        self.assertEqual(result.returncode, 1)
        self.assertIn("'host_id' is a required property", result.stderr)

    def test_contract_and_status_pass_together(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            contract = self.write_yaml(directory, valid_contract())
            status = self.write_json(directory, valid_status())
            result = self.run_validator(
                "--contract",
                str(contract),
                "--status",
                f"example-telemetry={status}",
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("1 status snapshot(s)", result.stdout)

    def test_unresolved_todo_fails_strict_validation(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            candidate = valid_contract()
            candidate["repository"] = "TODO repository"
            contract = self.write_yaml(directory, candidate)
            result = self.run_validator("--contract", str(contract))
        self.assertEqual(result.returncode, 1)
        self.assertIn("unresolved TODO placeholder", result.stderr)

    def test_periodic_stale_after_must_exceed_cadence(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            candidate = valid_contract()
            candidate["telemetry_jobs"][0]["stale_after"] = "PT24H"
            contract = self.write_yaml(directory, candidate)
            result = self.run_validator("--contract", str(contract))
        self.assertEqual(result.returncode, 1)
        self.assertIn("must be greater than cadence", result.stderr)

    def test_status_must_join_declared_job(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            contract = self.write_yaml(directory, valid_contract())
            status = self.write_json(directory, valid_status())
            result = self.run_validator(
                "--contract",
                str(contract),
                "--status",
                f"unknown-job={status}",
            )
        self.assertEqual(result.returncode, 1)
        self.assertIn("is not declared in the contract", result.stderr)

    def test_producer_cannot_self_declare_freshness(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            contract = self.write_yaml(directory, valid_contract())
            snapshot = valid_status()
            snapshot["freshness"] = "fresh"
            status = self.write_json(directory, snapshot)
            result = self.run_validator(
                "--contract",
                str(contract),
                "--status",
                f"example-telemetry={status}",
            )
        self.assertEqual(result.returncode, 1)
        self.assertIn("consumer-derived freshness fields", result.stderr)

    def test_duplicate_check_names_fail(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            contract = self.write_yaml(directory, valid_contract())
            snapshot = valid_status()
            snapshot["checks"].append(dict(snapshot["checks"][0]))
            status = self.write_json(directory, snapshot)
            result = self.run_validator(
                "--contract",
                str(contract),
                "--status",
                f"example-telemetry={status}",
            )
        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicate stable check names", result.stderr)

    def test_duplicate_capability_declarations_fail(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            candidate = valid_contract()
            candidate["capabilities"].append(dict(candidate["capabilities"][0]))
            contract = self.write_yaml(directory, candidate)
            result = self.run_validator("--contract", str(contract))
        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicate capability id", result.stderr)

    def test_capability_observation_must_join_declared_job(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            candidate = valid_contract()
            candidate["capabilities"][0]["observation_job_id"] = "missing-job"
            contract = self.write_yaml(directory, candidate)
            result = self.run_validator("--contract", str(contract))
        self.assertEqual(result.returncode, 1)
        self.assertIn("must reference a telemetry job", result.stderr)

    def test_restricted_capability_requires_reason_and_enablement(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            candidate = valid_contract()
            del candidate["capabilities"][1]["reason_code"]
            del candidate["capabilities"][1]["enablement"]
            contract = self.write_yaml(directory, candidate)
            result = self.run_validator("--contract", str(contract))
        self.assertEqual(result.returncode, 1)
        self.assertIn("'reason_code' is a required property", result.stderr)
        self.assertIn("'enablement' is a required property", result.stderr)

    def test_status_rejects_undeclared_capability(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            contract = self.write_yaml(directory, valid_contract())
            snapshot = valid_status()
            snapshot["capabilities"].append(
                {
                    "id": "unknown.capability",
                    "availability": "available",
                }
            )
            status = self.write_json(directory, snapshot)
            result = self.run_validator(
                "--contract",
                str(contract),
                "--status",
                f"example-telemetry={status}",
            )
        self.assertEqual(result.returncode, 1)
        self.assertIn("is not declared in the contract", result.stderr)

    def test_status_rejects_policy_fields_in_runtime_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            contract = self.write_yaml(directory, valid_contract())
            snapshot = valid_status()
            snapshot["capabilities"][0]["policy"] = "enabled"
            status = self.write_json(directory, snapshot)
            result = self.run_validator(
                "--contract",
                str(contract),
                "--status",
                f"example-telemetry={status}",
            )
        self.assertEqual(result.returncode, 1)
        self.assertIn("must not redeclare project policy fields", result.stderr)

    def test_status_requires_every_capability_assigned_to_job(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            contract = self.write_yaml(directory, valid_contract())
            snapshot = valid_status()
            snapshot["capabilities"].pop()
            status = self.write_json(directory, snapshot)
            result = self.run_validator(
                "--contract",
                str(contract),
                "--status",
                f"example-telemetry={status}",
            )
        self.assertEqual(result.returncode, 1)
        self.assertIn("missing observations declared for this job", result.stderr)


if __name__ == "__main__":
    unittest.main()
