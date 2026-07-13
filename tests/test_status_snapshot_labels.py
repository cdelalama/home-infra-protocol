import json
import unittest
from pathlib import Path

from jsonschema import ValidationError, validate


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas/status-snapshot.schema.json").read_text())


def snapshot(check: dict) -> dict:
    return {
        "observed_at": "2026-07-13T10:00:00Z",
        "condition": "ok",
        "severity": "none",
        "summary": "The scheduled job completed successfully.",
        "checks": [check],
    }


class StatusSnapshotLabelTest(unittest.TestCase):
    def test_accepts_optional_human_label(self) -> None:
        validate(
            snapshot(
                {
                    "name": "last-sync",
                    "label": "Latest sync",
                    "condition": "ok",
                    "severity": "none",
                    "summary": "The latest sync completed without errors.",
                }
            ),
            SCHEMA,
        )

    def test_remains_compatible_without_label(self) -> None:
        validate(snapshot({"name": "last-sync", "condition": "ok"}), SCHEMA)

    def test_rejects_empty_label(self) -> None:
        with self.assertRaises(ValidationError):
            validate(
                snapshot(
                    {
                        "name": "last-sync",
                        "label": "",
                        "condition": "ok",
                    }
                ),
                SCHEMA,
            )


if __name__ == "__main__":
    unittest.main()
