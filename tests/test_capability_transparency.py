import json
import unittest
from pathlib import Path

from jsonschema import ValidationError, validate


ROOT = Path(__file__).resolve().parents[1]
PROJECT_SCHEMA = json.loads(
    (ROOT / "schemas/project-contract.schema.json").read_text()
)
STATUS_SCHEMA = json.loads(
    (ROOT / "schemas/status-snapshot.schema.json").read_text()
)


def project_contract(capability: dict) -> dict:
    return {
        "id": "example-project",
        "name": "Example Project",
        "repository": "https://github.com/example/example-project",
        "capabilities": [capability],
    }


def capability() -> dict:
    return {
        "id": "agents.orchestrate",
        "label": "Agent orchestration",
        "category": "agents",
        "support": "supported",
        "policy": "approval_required",
        "risk": "high",
        "scope": {
            "mode": "allowlist",
            "targets": ["infra-agent", "development-agent"],
        },
        "reason_code": "write-scope-review-required",
        "enablement": {
            "mode": "operator_approval",
            "target_policy": "enabled",
            "gate": "approve-agent-write-scope",
        },
        "review_at": "2026-09-30T12:00:00Z",
    }


class CapabilityTransparencySchemaTest(unittest.TestCase):
    def test_accepts_restricted_capability_with_visible_path(self) -> None:
        validate(project_contract(capability()), PROJECT_SCHEMA)

    def test_rejects_restricted_capability_without_reason(self) -> None:
        candidate = capability()
        del candidate["reason_code"]
        with self.assertRaises(ValidationError):
            validate(project_contract(candidate), PROJECT_SCHEMA)

    def test_rejects_restricted_capability_without_enablement_path(self) -> None:
        candidate = capability()
        del candidate["enablement"]
        with self.assertRaises(ValidationError):
            validate(project_contract(candidate), PROJECT_SCHEMA)

    def test_accepts_runtime_capability_evidence(self) -> None:
        validate(
            {
                "observed_at": "2026-07-30T12:00:00Z",
                "condition": "ok",
                "severity": "none",
                "summary": "Capability verification completed.",
                "capabilities": [
                    {
                        "id": "agents.orchestrate",
                        "availability": "available",
                        "verification": "serving",
                        "summary": "The orchestrator completed its canary.",
                    }
                ],
            },
            STATUS_SCHEMA,
        )

    def test_rejects_unknown_availability(self) -> None:
        with self.assertRaises(ValidationError):
            validate(
                {
                    "observed_at": "2026-07-30T12:00:00Z",
                    "condition": "ok",
                    "severity": "none",
                    "summary": "Capability verification completed.",
                    "capabilities": [
                        {
                            "id": "agents.orchestrate",
                            "availability": "sometimes",
                        }
                    ],
                },
                STATUS_SCHEMA,
            )


if __name__ == "__main__":
    unittest.main()
