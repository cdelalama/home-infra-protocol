"""Behavioral safety boundaries for the first Progress source increment."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/validate-progress.py"
spec = importlib.util.spec_from_file_location("progress_validator", SCRIPT)
progress = importlib.util.module_from_spec(spec)
spec.loader.exec_module(progress)


def fixture(name="pending"):
    return json.loads((ROOT / "examples/progress" / f"{name}.json").read_text())


class ProgressTests(unittest.TestCase):
    def test_schema_and_all_examples(self):
        progress.Draft202012Validator.check_schema(progress.SCHEMA)
        for name in ("undefined", "pending", "claimed"):
            with self.subTest(name=name):
                self.assertEqual(progress.validate_record(fixture(name)), [])

    def test_claimed_delivery_remains_unassessed_in_cli(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "--record",
                                 str(ROOT / "examples/progress/claimed.json")], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["delivery"], "not_assessed")
        self.assertEqual(output["authority"], "not_assessed")
        self.assertEqual(output["assessment"], "shape_only")

    def test_no_score_or_delivered_shortcut(self):
        for key, value in (("percent", 98), ("delivered", True), ("ready", True)):
            record = fixture(); record[key] = value
            with self.subTest(key=key): self.assertTrue(progress.validate_record(record))

    def test_unknown_contract_and_version_fail(self):
        for key, value in (("schema_version", 2), ("contract", "unknown")):
            record = fixture(); record[key] = value
            self.assertTrue(progress.validate_record(record))

    def test_undefined_cannot_invent_a_scope(self):
        record = fixture("undefined"); record["target"]["outcome"] = "Claimed useful"
        self.assertTrue(progress.validate_record(record))

    def test_accepted_requires_authority_and_pinned_requirements(self):
        for field in ("scope_ref", "acceptance_ref"):
            record = fixture(); record["target"][field] = None
            self.assertTrue(progress.validate_record(record))
        record = fixture(); record["criteria"][0]["requirement_ref"] = None
        self.assertTrue(progress.validate_record(record))

    def test_verified_without_proof_or_date_fails(self):
        for field, value in (("evidence_refs", []), ("verified_at", None)):
            record = fixture("claimed"); record["criteria"][0][field] = value
            self.assertTrue(progress.validate_record(record))

    def test_real_utc_dates_required(self):
        for value in ("2026-02-30T12:00:00Z", "2026-11-15T12:00:00", "yesterday"):
            record = fixture(); record["reviewed_at"] = value
            self.assertTrue(progress.validate_record(record))

    def test_identity_joins_and_uniqueness(self):
        record = fixture(); record["criteria"].append(copy.deepcopy(record["criteria"][0]))
        self.assertTrue(progress.validate_record(record))
        record = fixture(); record["next_action"]["criterion_id"] = "unknown"
        self.assertTrue(progress.validate_record(record))
        record = fixture(); record["blockers"] = [{"id":"input", "kind":"operator_input",
                "summary":"Choose an input", "criterion_ids":["unknown"]}]
        self.assertTrue(progress.validate_record(record))

    def test_reference_paths_cannot_escape_or_be_commands(self):
        for path in ("../private.json", "/etc/passwd", "docs/../private.json", "docs//scope.md",
                     "C:\\private.json", "https://example.invalid/x", "$(touch marker)"):
            record = fixture(); record["target"]["scope_ref"]["path"] = path
            with self.subTest(path=path): self.assertTrue(progress.validate_record(record))

    def test_routine_proof_update_needs_no_new_scope_decision(self):
        self.assertEqual(progress.validate_transition(fixture(), fixture("claimed")), [])
        record = fixture(); record["target"]["outcome"] = "Faithful translated summary"
        record["criteria"][0]["label"] = "A clearer display label"
        self.assertEqual(progress.validate_transition(fixture(), record), [])

    def test_adding_required_work_needs_new_scope_version_and_reference(self):
        old = fixture(); candidate = fixture()
        extra = copy.deepcopy(candidate["criteria"][0]); extra["id"] = "export"
        candidate["criteria"].append(extra)
        self.assertTrue(progress.validate_transition(old, candidate))
        candidate["target"]["scope_version"] = 2
        self.assertTrue(progress.validate_transition(old, candidate))
        candidate["target"]["acceptance_ref"]["revision"] = "3" * 40
        self.assertTrue(progress.validate_transition(old, candidate))
        candidate["target"]["acceptance_ref"]["anchor"] = "D-002"
        self.assertEqual(progress.validate_transition(old, candidate), [])

    def test_removing_or_redefining_required_work_is_a_scope_change(self):
        old = fixture(); extra = copy.deepcopy(old["criteria"][0]); extra["id"] = "export"
        old["criteria"].append(extra)
        self.assertTrue(progress.validate_transition(old, fixture()))
        candidate = fixture(); candidate["criteria"][0]["requirement_ref"]["revision"] = "4" * 40
        self.assertTrue(progress.validate_transition(fixture(), candidate))

    def test_previous_identity_and_accepted_scope_cannot_be_reset(self):
        candidate = fixture(); candidate["project_id"] = "another-project"
        self.assertTrue(progress.validate_transition(fixture(), candidate))
        self.assertTrue(progress.validate_transition(fixture(), fixture("undefined")))

    def test_pause_or_blocker_does_not_erase_delivery_claim(self):
        record = fixture("claimed")
        record["pause"] = {"since":"2026-11-15T14:00:00Z", "reason":"Explicit maintenance pause",
                           "source_ref":copy.deepcopy(record["target"]["scope_ref"])}
        record["blockers"] = [{"id":"technical", "kind":"technical", "summary":"A separate current limitation",
                                "criterion_ids":[]}]
        self.assertEqual(progress.validate_record(record), [])
        self.assertIsNotNone(record["delivery_claim"])

    def test_delivery_claim_requires_accepted_scope(self):
        for name in ("undefined", "pending"):
            record = fixture(name)
            if name == "pending":
                record["target"]["status"] = "proposed"
                record["target"]["acceptance_ref"] = None
            record["delivery_claim"] = fixture("claimed")["delivery_claim"]
            self.assertTrue(progress.validate_record(record))

    def test_pending_work_needs_action_blocker_or_pause(self):
        record = fixture(); record["next_action"] = None
        self.assertTrue(progress.validate_record(record))
        record["blockers"] = [{"id":"decision", "kind":"operator_decision",
                              "summary":"Choose input", "criterion_ids":[]}]
        self.assertEqual(progress.validate_record(record), [])

    def test_scope_metadata_cannot_drift_without_scope_change(self):
        for field, value in (("scope_version",2),):
            record = fixture(); record["target"][field] = value
            self.assertTrue(progress.validate_transition(fixture(), record))
        for key, value in (("revision", "3" * 40), ("anchor", "D-002")):
            record = fixture(); record["target"]["acceptance_ref"][key] = value
            self.assertEqual(progress.validate_record(record), [])
            self.assertTrue(progress.validate_transition(fixture(), record))

    def test_version_decrease_and_accepted_to_proposed_fail(self):
        old = fixture(); old["target"]["scope_version"] = 2
        self.assertTrue(progress.validate_transition(old, fixture()))
        record = fixture(); record["target"]["status"] = "proposed"
        record["target"]["acceptance_ref"] = None
        self.assertTrue(progress.validate_transition(fixture(), record))

    def test_malformed_cli_inputs_remain_unassessed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text('{"schema_version":1,"schema_version":2}')
            for args in (["--record",str(path)],
                         ["--record",str(ROOT / "examples/progress/pending.json"),"--previous",str(path)]):
                result = subprocess.run([sys.executable,str(SCRIPT),*args],capture_output=True,text=True)
                self.assertEqual(result.returncode, 2)
                output = json.loads(result.stdout)
                self.assertEqual(output["authority"], "not_assessed")
                self.assertEqual(output["delivery"], "not_assessed")

    def test_claim_is_bound_to_scope_and_can_be_corrected_without_freezing_it(self):
        old = fixture("claimed"); candidate = fixture("claimed")
        candidate["target"]["scope_version"] = 2
        candidate["target"]["acceptance_ref"]["anchor"] = "D-002"
        candidate["criteria"][0]["requirement_ref"]["revision"] = "4" * 40
        self.assertTrue(progress.validate_transition(old, candidate))
        candidate["delivery_claim"] = None
        self.assertEqual(progress.validate_transition(old, candidate), [])
        candidate["delivery_claim"] = copy.deepcopy(old["delivery_claim"])
        candidate["delivery_claim"]["scope_version"] = 2
        self.assertEqual(progress.validate_transition(old, candidate), [])
        del candidate["delivery_claim"]["scope_version"]
        self.assertTrue(progress.validate_record(candidate))

    def test_input_bounds_and_duplicate_keys_fail_closed(self):
        for raw in (b'{"schema_version":1,"schema_version":2}', b'{"value":NaN}',
                    b' ' * (progress.MAX_BYTES + 1), b'\xff'):
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "record.json"; path.write_bytes(raw)
                with self.assertRaises((ValueError, UnicodeDecodeError)):
                    progress.load_record(path)

    def test_cli_failure_does_not_echo_rejected_private_value(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "record.json"; record = fixture()
            record["schema_version"] = "private-value-should-not-appear"; path.write_text(json.dumps(record))
            result = subprocess.run([sys.executable, str(SCRIPT), "--record", str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertNotIn("private-value-should-not-appear", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
