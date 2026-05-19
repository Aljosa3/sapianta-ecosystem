from copy import deepcopy
from pathlib import Path

from agol_bridge.continuity.continuity_report_synthesis import (
    CONTINUITY_AUTHORITY_VIOLATION,
    CONTINUITY_BOUNDARY_VIOLATION,
    CONTINUITY_INCOMPLETE,
    CONTINUITY_LIFECYCLE_GAP,
    CONTINUITY_REPLAY_GAP,
    CONTINUITY_VALID,
    synthesize_continuity_report,
)


def _valid_inputs():
    return {
        "envelope_validation_report": {"validation_id": "VALIDATION-1", "status": "VALID"},
        "validator_composition_report": {"composition_id": "COMPOSITION-1", "aggregate_status": "VALID"},
        "replay_references": [
            {"replay_id": "REPLAY-1", "reference_status": "REFERENCED_NOT_MUTATED"},
        ],
        "lifecycle_references": [
            {
                "previous_state": "APPROVED",
                "next_state": "DISPATCHED",
                "reference_status": "VISIBLE_APPEND_ONLY_REFERENCE",
            },
        ],
        "semantic_boundary_statements": [
            {
                "statement": "Semantic reasoning remains non-authoritative and model-native.",
                "semantic_replay_determinism": False,
                "semantic_authority": False,
            }
        ],
        "authority_boundary_statements": [
            "Validation success is not approval, dispatch, execution, or continuation authority.",
        ],
        "lineage_references": [{"lineage_id": "LINEAGE-1"}],
        "continuity_findings": [],
        "continuity_risks": [],
    }


def test_deterministic_output_for_same_inputs():
    inputs = _valid_inputs()
    assert synthesize_continuity_report(**inputs) == synthesize_continuity_report(**inputs)


def test_valid_inputs_return_continuity_valid():
    report = synthesize_continuity_report(**_valid_inputs())

    assert report["aggregate_governance_status"] == CONTINUITY_VALID
    assert report["replay_visibility_summary"]["visible"] is True
    assert report["lifecycle_visibility_summary"]["visible"] is True
    assert report["authority_boundary_summary"]["authority_created"] is False
    assert report["semantic_boundary_summary"]["semantic_authority_created"] is False


def test_stable_status_precedence_prefers_authority_violation():
    inputs = _valid_inputs()
    inputs["replay_references"] = [{"replay_id": "REPLAY-1", "reference_status": "MUTABLE"}]
    inputs["authority_boundary_statements"] = ["approval authority granted"]

    report = synthesize_continuity_report(**inputs)

    assert report["aggregate_governance_status"] == CONTINUITY_AUTHORITY_VIOLATION


def test_unknown_statuses_fail_closed():
    inputs = _valid_inputs()
    inputs["envelope_validation_report"] = {"validation_id": "VALIDATION-1", "status": "SURPRISE"}

    report = synthesize_continuity_report(**inputs)

    assert report["aggregate_governance_status"] == CONTINUITY_BOUNDARY_VIOLATION
    assert {
        "status": CONTINUITY_BOUNDARY_VIOLATION,
        "field": "envelope_validation_status",
        "detail": "Unknown status: SURPRISE.",
    } in report["continuity_findings"]


def test_missing_evidence_becomes_explicit_findings():
    report = synthesize_continuity_report()

    assert report["aggregate_governance_status"] == CONTINUITY_INCOMPLETE
    fields = {finding["field"] for finding in report["continuity_findings"]}
    assert "envelope_validation_status" in fields
    assert "validator_composition_status" in fields
    assert "replay_references" in fields
    assert "lifecycle_references" in fields
    assert "semantic_boundary_statements" in fields
    assert "authority_boundary_statements" in fields
    assert "lineage_references" in fields


def test_replay_gaps_produce_replay_gap_status():
    inputs = _valid_inputs()
    inputs["replay_references"] = [{"replay_id": "REPLAY-1", "reference_status": "MUTABLE"}]

    report = synthesize_continuity_report(**inputs)

    assert report["aggregate_governance_status"] == CONTINUITY_REPLAY_GAP
    assert report["replay_visibility_summary"]["visible"] is False


def test_lifecycle_gaps_produce_lifecycle_gap_status():
    inputs = _valid_inputs()
    inputs["lifecycle_references"] = [{"previous_state": "APPROVED", "next_state": "DISPATCHED"}]

    report = synthesize_continuity_report(**inputs)

    assert report["aggregate_governance_status"] == CONTINUITY_LIFECYCLE_GAP
    assert report["lifecycle_visibility_summary"]["visible"] is False


def test_authority_violations_produce_authority_violation_status():
    inputs = _valid_inputs()
    inputs["authority_boundary_statements"] = ["execution authority granted"]

    report = synthesize_continuity_report(**inputs)

    assert report["aggregate_governance_status"] == CONTINUITY_AUTHORITY_VIOLATION
    assert report["authority_boundary_summary"]["violations"] == ["execution authority granted"]


def test_no_input_mutation():
    inputs = _valid_inputs()
    before = deepcopy(inputs)

    synthesize_continuity_report(**inputs)

    assert inputs == before


def test_no_synthesized_output_mutation_of_input_lists():
    inputs = _valid_inputs()
    finding = {"status": CONTINUITY_VALID, "field": "seed", "detail": "seed finding"}
    risk = {"status": CONTINUITY_VALID, "field": "seed", "detail": "seed risk"}
    inputs["continuity_findings"] = [finding]
    inputs["continuity_risks"] = [risk]

    report = synthesize_continuity_report(**inputs)
    report["continuity_findings"][0]["detail"] = "mutated output"
    report["continuity_risks"][0]["detail"] = "mutated output"

    assert finding["detail"] == "seed finding"
    assert risk["detail"] == "seed risk"


def test_stable_report_identity_generation():
    inputs = _valid_inputs()
    first = synthesize_continuity_report(**inputs)
    second = synthesize_continuity_report(**inputs)

    assert first["continuity_report_id"] == second["continuity_report_id"]
    assert first["continuity_report_id"].startswith("CONTINUITY-")


def test_no_filesystem_network_subprocess_provider_sidepanel_runtime_calls_are_introduced():
    source = (Path(__file__).resolve().parents[1] / "continuity/continuity_report_synthesis.py").read_text()
    forbidden = (
        "open(",
        "Path(",
        "read_text",
        "write_text",
        "requests",
        "urllib",
        "socket",
        "subprocess",
        "threading",
        "Timer",
        "fetch",
        "chrome.",
        "provider.call",
        "__import__",
        "importlib",
        "globals(",
        "locals(",
    )
    for token in forbidden:
        assert token not in source


def test_no_dispatch_approval_execution_authority_is_introduced():
    source = (Path(__file__).resolve().parents[1] / "continuity/continuity_report_synthesis.py").read_text()
    forbidden_authority_terms = (
        "dispatch(",
        "approve(",
        "execute(",
        "transition_lifecycle",
        "append_replay_event",
        "write_report",
    )
    for token in forbidden_authority_terms:
        assert token not in source
