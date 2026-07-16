import json
import unittest
from pathlib import Path

from jsonschema import ValidationError, validate


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas/status-snapshot.schema.json").read_text())


def snapshot() -> dict:
    return {
        "observed_at": "2026-07-16T16:00:00Z",
        "condition": "ok",
        "severity": "none",
        "summary": "The scheduled job completed successfully.",
    }


class StatusSnapshotNextRunTest(unittest.TestCase):
    def test_accepts_authoritative_utc_next_run(self) -> None:
        candidate = snapshot()
        candidate["next_run_at"] = "2026-07-16T16:15:00Z"
        validate(candidate, SCHEMA)

    def test_remains_compatible_without_next_run(self) -> None:
        validate(snapshot(), SCHEMA)

    def test_rejects_non_utc_next_run(self) -> None:
        candidate = snapshot()
        candidate["next_run_at"] = "2026-07-16T18:15:00+02:00"
        with self.assertRaises(ValidationError):
            validate(candidate, SCHEMA)


if __name__ == "__main__":
    unittest.main()
