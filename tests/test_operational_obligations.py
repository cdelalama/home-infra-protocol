import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate-project-interface.py"
PROJECT_SCHEMA = json.loads(
    (ROOT / "schemas/project-contract.schema.json").read_text(encoding="utf-8")
)
PROJECTION_SCHEMA = json.loads(
    (
        ROOT / "schemas/operational-obligations-projection.schema.json"
    ).read_text(encoding="utf-8")
)
PROJECT_VALIDATOR = Draft202012Validator(
    PROJECT_SCHEMA, format_checker=FormatChecker()
)
PROJECTION_VALIDATOR = Draft202012Validator(
    PROJECTION_SCHEMA, format_checker=FormatChecker()
)

SPEC = importlib.util.spec_from_file_location(
    "project_interface_validator", VALIDATOR
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def occurrence(
    occurrence_id: str = "review-2027-01",
    starts_at: str = "2027-01-01T00:00:00Z",
    due_at: str = "2027-01-15T23:59:59Z",
) -> dict:
    return {
        "id": occurrence_id,
        "starts_at": starts_at,
        "due_at": due_at,
    }


def obligation(
    obligation_id: str = "pilot-review",
    kind: str = "one_time",
) -> dict:
    value = {
        "id": obligation_id,
        "kind": kind,
        "responsible": "operator",
        "action": "Decide whether the bounded pilot should remain enabled.",
        "runbook_ref": "operational-readiness",
        "evidence": {
            "ref": "pilot-decision-record",
            "requirement": "A project decision record for this exact review.",
        },
        "occurrences": [occurrence()],
    }
    if kind == "recurring":
        value["horizon_at"] = "2027-07-01T00:00:00Z"
    return value


def contract(*obligations: dict) -> dict:
    return {
        "id": "example-project",
        "name": "Example Project",
        "repository": "https://example.invalid/example-project",
        "operational_obligations": list(obligations),
        "runbooks": {
            "operational-readiness": "docs/OPERATIONAL_READINESS.md",
        },
    }


def projection(project_contract: dict) -> dict:
    projected_obligations = []
    for declaration in project_contract.get("operational_obligations", []):
        projected = {
            key: deepcopy(value)
            for key, value in declaration.items()
            if key != "occurrences"
        }
        projected["occurrences"] = [
            {**deepcopy(item), "evidence": {"result": "missing"}}
            for item in declaration["occurrences"]
        ]
        projected_obligations.append(projected)
    return {
        "publisher": {
            "id": "home-infra",
            "generated_at": "2027-01-10T12:00:00Z",
            "stale_after": "PT15M",
        },
        "scope": {
            "complete": True,
            "project_ids": [project_contract["id"]],
        },
        "projects": [
            {
                "id": project_contract["id"],
                "declaration_revision": "example-revision-1",
                "accepted_at": "2027-01-01T00:05:00Z",
                "obligations": projected_obligations,
            }
        ],
    }


def assert_valid(test: unittest.TestCase, value: dict, validator) -> None:
    errors = list(validator.iter_errors(value))
    test.assertEqual(errors, [], [error.message for error in errors])


class OperationalObligationsSchemaTest(unittest.TestCase):
    def test_existing_contract_remains_compatible_without_obligations(self) -> None:
        assert_valid(self, contract(), PROJECT_VALIDATOR)

    def test_accepts_one_time_and_recurring_declarations(self) -> None:
        recurring = obligation("restore-readiness-weekly", "recurring")
        recurring["occurrences"].append(
            occurrence(
                "review-2027-02",
                "2027-01-16T00:00:00Z",
                "2027-01-22T23:59:59Z",
            )
        )
        candidate = contract(obligation(), recurring)
        assert_valid(self, candidate, PROJECT_VALIDATOR)

    def test_one_time_rejects_multiple_occurrences(self) -> None:
        candidate = contract(obligation())
        candidate["operational_obligations"][0]["occurrences"].append(
            occurrence("second-review")
        )
        self.assertTrue(list(PROJECT_VALIDATOR.iter_errors(candidate)))

    def test_one_time_rejects_horizon(self) -> None:
        candidate = contract(obligation())
        candidate["operational_obligations"][0]["horizon_at"] = (
            "2027-07-01T00:00:00Z"
        )
        self.assertTrue(list(PROJECT_VALIDATOR.iter_errors(candidate)))

    def test_projection_accepts_verified_evidence_without_observed_at(self) -> None:
        candidate_contract = contract(obligation())
        candidate = projection(candidate_contract)
        evidence = candidate["projects"][0]["obligations"][0]["occurrences"][0][
            "evidence"
        ]
        evidence.update(
            {
                "result": "verified",
                "authority": "example-project",
                "ref": "result-1",
                "summary": "The project result passed without a trusted event time.",
            }
        )
        assert_valid(self, candidate, PROJECTION_VALIDATOR)

    def test_projection_rejects_notification_or_derived_fields(self) -> None:
        candidate = projection(contract(obligation()))
        candidate["provider"] = "example-messenger"
        occurrence_value = candidate["projects"][0]["obligations"][0][
            "occurrences"
        ][0]
        occurrence_value["time_state"] = "pending"
        errors = list(PROJECTION_VALIDATOR.iter_errors(candidate))
        self.assertGreaterEqual(len(errors), 2)

    def test_projection_rejects_hermes_acknowledgement_as_project_truth(self) -> None:
        candidate = projection(contract(obligation()))
        candidate["projects"][0]["obligations"][0]["occurrences"][0][
            "acknowledged"
        ] = True
        self.assertTrue(list(PROJECTION_VALIDATOR.iter_errors(candidate)))

    def test_full_sanitized_example_matches_projection_schema(self) -> None:
        value = json.loads(
            (
                ROOT / "examples/home-infra/operational-obligations.json"
            ).read_text(encoding="utf-8")
        )
        assert_valid(self, value, PROJECTION_VALIDATOR)


class OperationalObligationsValidatorTest(unittest.TestCase):
    def run_validator(
        self,
        project_contract: dict,
        accepted_projection: dict | None = None,
        previous_projection: dict | None = None,
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            contract_path = directory / "infra.contract.yml"
            contract_path.write_text(
                yaml.safe_dump(project_contract, sort_keys=False), encoding="utf-8"
            )
            args = [sys.executable, str(VALIDATOR), "--contract", str(contract_path)]
            if accepted_projection is not None:
                projection_path = directory / "operational-obligations.json"
                projection_path.write_text(
                    json.dumps(accepted_projection), encoding="utf-8"
                )
                args.extend(["--obligations-projection", str(projection_path)])
            if previous_projection is not None:
                previous_path = directory / "previous-operational-obligations.json"
                previous_path.write_text(
                    json.dumps(previous_projection), encoding="utf-8"
                )
                args.extend(
                    ["--previous-obligations-projection", str(previous_path)]
                )
            return subprocess.run(
                args,
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

    def test_contract_and_projection_join(self) -> None:
        candidate_contract = contract(obligation())
        result = self.run_validator(
            candidate_contract, projection(candidate_contract)
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS obligations projection", result.stdout)

    def test_duplicate_series_id_fails(self) -> None:
        duplicate = obligation()
        result = self.run_validator(contract(obligation(), duplicate))
        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicate obligation series id", result.stderr)

    def test_duplicate_occurrence_id_fails(self) -> None:
        recurring = obligation("restore-readiness-weekly", "recurring")
        recurring["occurrences"].append(deepcopy(recurring["occurrences"][0]))
        result = self.run_validator(contract(recurring))
        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicate occurrence id", result.stderr)

    def test_invalid_window_and_horizon_fail(self) -> None:
        recurring = obligation("restore-readiness-weekly", "recurring")
        recurring["occurrences"][0]["starts_at"] = "2027-07-01T00:00:00Z"
        recurring["occurrences"][0]["due_at"] = "2027-06-30T00:00:00Z"
        result = self.run_validator(contract(recurring))
        self.assertEqual(result.returncode, 1)
        self.assertIn("starts_at must be before due_at", result.stderr)
        self.assertIn("starts_at must be before horizon_at", result.stderr)

    def test_recurring_windows_may_overlap(self) -> None:
        recurring = obligation("restore-readiness-weekly", "recurring")
        recurring["occurrences"].append(
            occurrence(
                "overlapping-review",
                "2027-01-10T00:00:00Z",
                "2027-01-20T23:59:59Z",
            )
        )
        result = self.run_validator(contract(recurring))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_runbook_must_be_declared(self) -> None:
        candidate = contract(obligation())
        candidate["runbooks"] = {}
        result = self.run_validator(candidate)
        self.assertEqual(result.returncode, 1)
        self.assertIn("is not declared in $.runbooks", result.stderr)

    def test_action_rejects_executable_marker(self) -> None:
        candidate = contract(obligation())
        candidate["operational_obligations"][0]["action"] = (
            "Open the runbook && run its command."
        )
        result = self.run_validator(candidate)
        self.assertEqual(result.returncode, 1)
        self.assertIn("forbidden executable marker", result.stderr)

    def test_action_rejects_embedded_endpoint(self) -> None:
        candidate = contract(obligation())
        candidate["operational_obligations"][0]["action"] = (
            "Send a request to https://example.invalid/mutate."
        )
        result = self.run_validator(candidate)
        self.assertEqual(result.returncode, 1)
        self.assertIn("forbidden executable marker", result.stderr)

    def test_projection_rejects_private_path_in_evidence_summary(self) -> None:
        candidate_contract = contract(obligation())
        accepted = projection(candidate_contract)
        evidence = accepted["projects"][0]["obligations"][0]["occurrences"][0][
            "evidence"
        ]
        evidence.update(
            {
                "result": "failed",
                "authority": "example-project",
                "ref": "result-1",
                "summary": "The report under /home/operator/private failed.",
            }
        )
        result = self.run_validator(candidate_contract, accepted)
        self.assertEqual(result.returncode, 1)
        self.assertIn("non-sanitized marker", result.stderr)

    def test_projection_scope_must_match_projects_and_contract(self) -> None:
        candidate_contract = contract(obligation())
        accepted = projection(candidate_contract)
        accepted["scope"]["project_ids"] = ["different-project"]
        result = self.run_validator(candidate_contract, accepted)
        self.assertEqual(result.returncode, 1)
        self.assertIn("must exactly match", result.stderr)
        self.assertIn("is not included", result.stderr)

    def test_projection_must_match_declaration(self) -> None:
        candidate_contract = contract(obligation())
        accepted = projection(candidate_contract)
        accepted["projects"][0]["obligations"][0]["action"] = "Different action."
        result = self.run_validator(candidate_contract, accepted)
        self.assertEqual(result.returncode, 1)
        self.assertIn("projected action does not match", result.stderr)

    def test_occurrence_identity_cannot_reuse_a_changed_window(self) -> None:
        candidate_contract = contract(obligation())
        previous = projection(candidate_contract)
        candidate_contract["operational_obligations"][0]["occurrences"][0][
            "due_at"
        ] = "2027-01-20T23:59:59Z"
        current = projection(candidate_contract)
        result = self.run_validator(candidate_contract, current, previous)
        self.assertEqual(result.returncode, 1)
        self.assertIn("stable occurrence id cannot change due_at", result.stderr)

    def test_evidence_authority_must_match_project(self) -> None:
        candidate_contract = contract(obligation())
        accepted = projection(candidate_contract)
        evidence = accepted["projects"][0]["obligations"][0]["occurrences"][0][
            "evidence"
        ]
        evidence.update(
            {
                "result": "verified",
                "authority": "different-project",
                "observed_at": "2027-01-10T00:00:00Z",
                "ref": "result-1",
                "summary": "The project result passed.",
            }
        )
        result = self.run_validator(candidate_contract, accepted)
        self.assertEqual(result.returncode, 1)
        self.assertIn("evidence authority must match", result.stderr)

    def test_supersession_requires_existing_distinct_replacement(self) -> None:
        recurring = obligation("restore-readiness-weekly", "recurring")
        candidate_contract = contract(recurring)
        accepted = projection(candidate_contract)
        occurrence_value = accepted["projects"][0]["obligations"][0][
            "occurrences"
        ][0]
        occurrence_value["resolution"] = {
            "type": "superseded",
            "authority": "example-project",
            "resolved_at": "2027-01-10T00:00:00Z",
            "ref": "decision-1",
            "replacement_occurrence_id": "missing-occurrence",
        }
        result = self.run_validator(candidate_contract, accepted)
        self.assertEqual(result.returncode, 1)
        self.assertIn("is not present in the same series", result.stderr)

    def test_verified_evidence_cannot_coexist_with_resolution(self) -> None:
        candidate_contract = contract(obligation())
        accepted = projection(candidate_contract)
        occurrence_value = accepted["projects"][0]["obligations"][0][
            "occurrences"
        ][0]
        occurrence_value["evidence"] = {
            "result": "verified",
            "authority": "example-project",
            "observed_at": "2027-01-10T00:00:00Z",
            "ref": "result-1",
            "summary": "The project result passed.",
        }
        occurrence_value["resolution"] = {
            "type": "cancelled",
            "authority": "example-project",
            "resolved_at": "2027-01-09T00:00:00Z",
            "ref": "decision-1",
        }
        result = self.run_validator(candidate_contract, accepted)
        self.assertEqual(result.returncode, 1)
        self.assertIn("cannot coexist", result.stderr)


class OperationalObligationsDerivationTest(unittest.TestCase):
    def test_future_pending_and_overdue_use_consumer_clock(self) -> None:
        value = {**occurrence(), "evidence": {"result": "missing"}}
        future = MODULE.derive_occurrence_state(
            value, datetime(2026, 12, 31, tzinfo=timezone.utc)
        )
        pending = MODULE.derive_occurrence_state(
            value, datetime(2027, 1, 10, tzinfo=timezone.utc)
        )
        overdue = MODULE.derive_occurrence_state(
            value, datetime(2027, 1, 16, tzinfo=timezone.utc)
        )
        self.assertEqual(future["time_state"], "future")
        self.assertEqual(pending["time_state"], "pending")
        self.assertEqual(overdue["time_state"], "overdue")

    def test_start_and_due_boundaries_are_pending(self) -> None:
        value = {**occurrence(), "evidence": {"result": "missing"}}
        at_start = MODULE.derive_occurrence_state(
            value, datetime(2027, 1, 1, tzinfo=timezone.utc)
        )
        at_due = MODULE.derive_occurrence_state(
            value, datetime(2027, 1, 15, 23, 59, 59, tzinfo=timezone.utc)
        )
        self.assertEqual(at_start["time_state"], "pending")
        self.assertEqual(at_due["time_state"], "pending")

    def test_verified_evidence_derives_completed_on_time_or_late(self) -> None:
        value = {
            **occurrence(),
            "evidence": {
                "result": "verified",
                "observed_at": "2027-01-15T12:00:00Z",
            },
        }
        on_time = MODULE.derive_occurrence_state(
            value, datetime(2027, 2, 1, tzinfo=timezone.utc)
        )
        value["evidence"]["observed_at"] = "2027-01-16T12:00:00Z"
        late = MODULE.derive_occurrence_state(
            value, datetime(2027, 2, 1, tzinfo=timezone.utc)
        )
        self.assertEqual(on_time["result_state"], "completed")
        self.assertEqual(on_time["timeliness"], "on_time")
        self.assertEqual(late["result_state"], "completed")
        self.assertEqual(late["timeliness"], "late")

    def test_verified_evidence_without_observed_at_has_indeterminate_timeliness(
        self,
    ) -> None:
        value = {**occurrence(), "evidence": {"result": "verified"}}
        derived = MODULE.derive_occurrence_state(
            value, datetime(2027, 2, 1, tzinfo=timezone.utc)
        )
        self.assertEqual(derived["result_state"], "completed")
        self.assertEqual(derived["timeliness"], "indeterminate")

    def test_failed_evidence_leaves_temporal_state_open(self) -> None:
        value = {
            **occurrence(),
            "evidence": {
                "result": "failed",
                "observed_at": "2027-01-16T12:00:00Z",
            },
        }
        derived = MODULE.derive_occurrence_state(
            value, datetime(2027, 1, 16, tzinfo=timezone.utc)
        )
        self.assertEqual(derived["result_state"], "open")
        self.assertEqual(derived["time_state"], "overdue")

    def test_administrative_resolution_is_terminal_but_not_completed(self) -> None:
        value = {
            **occurrence(),
            "evidence": {"result": "missing"},
            "resolution": {"type": "cancelled"},
        }
        derived = MODULE.derive_occurrence_state(
            value, datetime(2027, 2, 1, tzinfo=timezone.utc)
        )
        self.assertEqual(derived["result_state"], "cancelled")
        self.assertIsNone(derived["time_state"])
        self.assertNotEqual(derived["result_state"], "completed")

    def test_next_selection_has_stable_total_order(self) -> None:
        first = obligation("series-b", "recurring")
        first["occurrences"][0]["id"] = "occurrence-a"
        second = obligation("series-a", "recurring")
        second["occurrences"][0]["id"] = "occurrence-z"
        for value in (first, second):
            value["occurrences"][0]["evidence"] = {"result": "missing"}
        selected = MODULE.select_next_occurrence([first, second])
        self.assertIsNotNone(selected)
        self.assertEqual(selected[0], "series-a")

    def test_next_selection_uses_occurrence_id_as_final_tie_breaker(self) -> None:
        value = obligation("series-a", "recurring")
        value["occurrences"] = [
            {
                **occurrence("occurrence-z"),
                "evidence": {"result": "missing"},
            },
            {
                **occurrence("occurrence-a"),
                "evidence": {"result": "missing"},
            },
        ]
        selected = MODULE.select_next_occurrence([value])
        self.assertIsNotNone(selected)
        self.assertEqual(selected[1]["id"], "occurrence-a")

    def test_next_selection_compares_due_at_as_utc_instants(self) -> None:
        value = obligation("series-a", "recurring")
        value["occurrences"] = [
            {
                **occurrence(
                    "earlier",
                    due_at="2027-01-15T00:00:00Z",
                ),
                "evidence": {"result": "missing"},
            },
            {
                **occurrence(
                    "later-fractional",
                    due_at="2027-01-15T00:00:00.500Z",
                ),
                "evidence": {"result": "missing"},
            },
        ]
        selected = MODULE.select_next_occurrence([value])
        self.assertIsNotNone(selected)
        self.assertEqual(selected[1]["id"], "earlier")

    def test_next_selection_compares_starts_at_as_secondary_utc_instant(
        self,
    ) -> None:
        value = obligation("series-a", "recurring")
        value["occurrences"] = [
            {
                **occurrence(
                    "earlier-start",
                    starts_at="2027-01-01T00:00:00Z",
                ),
                "evidence": {"result": "missing"},
            },
            {
                **occurrence(
                    "later-fractional-start",
                    starts_at="2027-01-01T00:00:00.500Z",
                ),
                "evidence": {"result": "missing"},
            },
        ]
        selected = MODULE.select_next_occurrence([value])
        self.assertIsNotNone(selected)
        self.assertEqual(selected[1]["id"], "earlier-start")

    def test_latest_occurrence_has_stable_reverse_total_order(self) -> None:
        value = obligation("restore-readiness-weekly", "recurring")
        value["occurrences"] = [
            occurrence("occurrence-a"),
            occurrence("occurrence-c"),
            occurrence("occurrence-b"),
        ]
        latest = MODULE.latest_occurrence(value)
        self.assertIsNotNone(latest)
        self.assertEqual(latest["id"], "occurrence-c")

    def test_latest_occurrence_compares_due_at_as_utc_instants(self) -> None:
        value = obligation("restore-readiness-weekly", "recurring")
        value["occurrences"] = [
            occurrence("earlier", due_at="2027-01-15T00:00:00Z"),
            occurrence(
                "later-fractional",
                due_at="2027-01-15T00:00:00.500Z",
            ),
        ]
        latest = MODULE.latest_occurrence(value)
        self.assertIsNotNone(latest)
        self.assertEqual(latest["id"], "later-fractional")

    def test_latest_occurrence_compares_starts_at_as_secondary_utc_instant(
        self,
    ) -> None:
        value = obligation("restore-readiness-weekly", "recurring")
        value["occurrences"] = [
            occurrence(
                "earlier-start",
                starts_at="2027-01-01T00:00:00Z",
            ),
            occurrence(
                "later-fractional-start",
                starts_at="2027-01-01T00:00:00.500Z",
            ),
        ]
        latest = MODULE.latest_occurrence(value)
        self.assertIsNotNone(latest)
        self.assertEqual(latest["id"], "later-fractional-start")

    def test_one_time_obligation_has_no_recurring_series_state(self) -> None:
        value = obligation("pilot-review", "one_time")
        state = MODULE.derive_series_state(
            value, datetime(2027, 1, 10, tzinfo=timezone.utc)
        )
        self.assertIsNone(state)

    def test_recurring_gap_and_period_end_are_distinct(self) -> None:
        value = obligation("restore-readiness-weekly", "recurring")
        value["occurrences"][0]["evidence"] = {
            "result": "verified",
            "observed_at": "2027-01-10T00:00:00Z",
        }
        before_horizon = MODULE.derive_series_state(
            value, datetime(2027, 2, 1, tzinfo=timezone.utc)
        )
        after_horizon = MODULE.derive_series_state(
            value, datetime(2027, 8, 1, tzinfo=timezone.utc)
        )
        self.assertEqual(before_horizon, "materialization_required")
        self.assertEqual(after_horizon, "period_ended")

    def test_open_occurrence_survives_the_series_horizon(self) -> None:
        value = obligation("restore-readiness-weekly", "recurring")
        value["occurrences"][0]["evidence"] = {"result": "missing"}
        state = MODULE.derive_series_state(
            value, datetime(2027, 8, 1, tzinfo=timezone.utc)
        )
        derived = MODULE.derive_occurrence_state(
            value["occurrences"][0],
            datetime(2027, 8, 1, tzinfo=timezone.utc),
        )
        self.assertEqual(state, "active")
        self.assertEqual(derived["time_state"], "overdue")

    def test_three_frequency_series_remain_independent_through_horizon(self) -> None:
        series = [
            obligation("restore-readiness-weekly", "recurring"),
            obligation("restore-readiness-monthly", "recurring"),
            obligation("restore-readiness-quarterly", "recurring"),
        ]
        for value in series:
            value["occurrences"][0]["evidence"] = {
                "result": "verified",
                "observed_at": "2027-01-10T00:00:00Z",
            }
        states = [
            MODULE.derive_series_state(
                value, datetime(2027, 7, 1, tzinfo=timezone.utc)
            )
            for value in series
        ]
        self.assertEqual(states, ["period_ended", "period_ended", "period_ended"])

    def test_channel_freshness_and_authoritative_omission_are_separate(self) -> None:
        accepted = projection(contract(obligation()))
        fresh_now = datetime(2027, 1, 10, 12, 10, tzinfo=timezone.utc)
        stale_now = datetime(2027, 1, 10, 12, 16, tzinfo=timezone.utc)
        publisher = accepted["publisher"]
        self.assertEqual(
            MODULE.derive_projection_channel_state(publisher, fresh_now), "fresh"
        )
        self.assertEqual(
            MODULE.derive_projection_channel_state(publisher, stale_now), "stale"
        )
        self.assertTrue(
            MODULE.projection_can_authoritatively_withdraw(
                accepted, "fresh", "example-project"
            )
        )
        for channel_state in ("stale", "invalid", "unavailable"):
            self.assertFalse(
                MODULE.projection_can_authoritatively_withdraw(
                    accepted, channel_state, "example-project"
                )
            )

    def test_stateful_consumer_retains_last_valid_on_channel_failure(self) -> None:
        previous = projection(contract(obligation()))
        stale_candidate = projection(contract())
        effective, source = MODULE.select_effective_projection(
            previous, stale_candidate, "stale"
        )
        self.assertIs(effective, previous)
        self.assertEqual(source, "retained")

        effective, source = MODULE.select_effective_projection(
            previous, stale_candidate, "fresh"
        )
        self.assertIs(effective, stale_candidate)
        self.assertEqual(source, "current")

    def test_stateless_consumer_reports_unavailable_instead_of_empty(self) -> None:
        effective, source = MODULE.select_effective_projection(
            None, None, "unavailable"
        )
        self.assertIsNone(effective)
        self.assertEqual(source, "unavailable")


if __name__ == "__main__":
    unittest.main()
