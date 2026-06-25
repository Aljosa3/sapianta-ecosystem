"""Tests for ACLI_HARDENING_RUNTIME_V1."""

from __future__ import annotations

import json

import pytest

from aigol.runtime.acli_hardening_runtime import (
    FAIL,
    PARTIAL_PASS,
    PASS,
    record_acli_hardening_interaction,
    reconstruct_acli_hardening_replay,
    render_platform_hardening_progress,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-25T12:00:00Z"


def _completed_interaction(**overrides) -> dict:
    interaction = {
        "prompt": "Create governance artifact ACLI_USAGE_GUIDELINES_V1.",
        "workflow_id": "GOVERNED_DEVELOPMENT_WORKFLOW",
        "intent_family": "DEVELOPMENT_INTENT",
        "runtime_path": [
            "Universal Translation Runtime",
            "HIRR",
            "Workflow Routing",
            "Proposal Runtime",
            "Approval Runtime",
            "Worker Runtime",
            "Validation Runtime",
            "Replay Runtime",
        ],
        "normalized_intent": {"requested_actions": ["CREATE"], "artifact_identifier": "ACLI_USAGE_GUIDELINES_V1"},
        "proposal": {
            "proposal_id": "PROPOSAL-001",
            "proposal_hash": "sha256:proposal",
            "target_paths": ["docs/governance/ACLI_USAGE_GUIDELINES_V1.md"],
            "proposal_preview": "Create governance artifact.",
        },
        "approval_required": True,
        "approval_status": "APPROVED",
        "executed": True,
        "execution_performed": True,
        "worker_status": "DISPATCHED",
        "validation_status": "PASSED",
        "validated": True,
        "explanation_status": "SHOWN",
        "replay_reference": "/tmp/replay/acli-001",
        "replay_hash": "sha256:" + "a" * 64,
    }
    interaction.update(overrides)
    return interaction


def test_records_pass_for_completed_governed_development_interaction(tmp_path) -> None:
    result = record_acli_hardening_interaction(
        hardening_id="HARDENING-001",
        interaction_id="INTERACTION-001",
        completed_interaction=_completed_interaction(),
        operator_feedback={"clarity": "Very Clear"},
        replay_dir=tmp_path / "hardening",
        created_at=CREATED_AT,
    )

    scenario_ids = {item["scenario_id"] for item in result["hardening_scenarios"]}

    assert result["result"] == PASS
    assert "GOVERNED_DEVELOPMENT_WORKFLOW" in result["workflows_executed"]
    assert "HUMAN_TO_GOVERNANCE_TRANSLATION" in scenario_ids
    assert "PROPOSAL_GENERATION" in scenario_ids
    assert "APPROVAL" in scenario_ids
    assert "WORKER_DISPATCH" in scenario_ids
    assert "VALIDATION" in scenario_ids
    assert "REPLAY" in scenario_ids
    assert result["issues"] == []
    assert result["operator_feedback"]["feedback_requested"] is True
    assert result["operator_feedback"]["feedback_provided"] is True
    assert result["evidence_completeness"]["operator_prompt"]["prompt_text"] == (
        "Create governance artifact ACLI_USAGE_GUIDELINES_V1."
    )
    assert result["evidence_completeness"]["workflow"]["workflow_id"] == "GOVERNED_DEVELOPMENT_WORKFLOW"
    assert result["evidence_completeness"]["workflow"]["routing_confidence"] is None
    assert result["evidence_completeness"]["replay"]["source_replay_reference"] == "/tmp/replay/acli-001"
    assert result["evidence_completeness"]["approval_summary"]["approval_required"] is True
    assert result["evidence_completeness"]["worker_path_summary"]["worker_invoked"] is False
    assert result["hardening_scenario_identifiers"] == [
        scenario["scenario_id"] for scenario in result["hardening_scenarios"]
    ]
    assert result["authority_flags"]["authorizes_execution"] is False
    assert result["execution_authorized"] is False


def test_rejection_records_pass_without_execution(tmp_path) -> None:
    result = record_acli_hardening_interaction(
        hardening_id="HARDENING-002",
        interaction_id="INTERACTION-002",
        completed_interaction=_completed_interaction(
            approval_status="REJECTED",
            executed=False,
            execution_performed=False,
            worker_status="NOT_INVOKED",
            validation_status="NOT_RUN",
            validated=False,
        ),
        replay_dir=tmp_path / "hardening",
        created_at=CREATED_AT,
    )

    scenario_ids = {item["scenario_id"] for item in result["hardening_scenarios"]}

    assert result["result"] == PASS
    assert "REJECT" in scenario_ids
    assert result["operator_journey"]["rejected"] is True
    assert result["operator_journey"]["executed"] is False
    assert result["issues"] == []


def test_request_modification_records_no_execution_pass(tmp_path) -> None:
    result = record_acli_hardening_interaction(
        hardening_id="HARDENING-003",
        interaction_id="INTERACTION-003",
        completed_interaction=_completed_interaction(
            approval_status="MODIFICATION_REQUESTED",
            executed=False,
            execution_performed=False,
            worker_status="NOT_INVOKED",
            validation_status="NOT_RUN",
            validated=False,
        ),
        replay_dir=tmp_path / "hardening",
        created_at=CREATED_AT,
    )

    scenario_ids = {item["scenario_id"] for item in result["hardening_scenarios"]}

    assert result["result"] == PASS
    assert "REQUEST_MODIFICATION" in scenario_ids
    assert result["operator_journey"]["modification_requested"] is True
    assert result["operator_journey"]["executed"] is False


def test_execution_missing_replay_reference_is_p0_fail(tmp_path) -> None:
    interaction = _completed_interaction()
    interaction.pop("replay_reference")
    interaction.pop("replay_hash")

    result = record_acli_hardening_interaction(
        hardening_id="HARDENING-004",
        interaction_id="INTERACTION-004",
        completed_interaction=interaction,
        replay_dir=tmp_path / "hardening",
        created_at=CREATED_AT,
    )

    assert result["result"] == FAIL
    assert result["issues"][0]["severity"] == "P0"
    assert result["issues"][0]["category"] == "REPLAY"
    assert result["dashboards"]["remaining_production_blockers"]["open_critical_issues"] == 1


def test_provider_unavailable_records_partial_pass_with_fallback_evidence(tmp_path) -> None:
    result = record_acli_hardening_interaction(
        hardening_id="HARDENING-005",
        interaction_id="INTERACTION-005",
        completed_interaction=_completed_interaction(
            llm_assisted_explanation=True,
            provider_status="PROVIDER_UNAVAILABLE",
            deterministic_fallback_used=True,
        ),
        replay_dir=tmp_path / "hardening",
        created_at=CREATED_AT,
    )

    scenario_ids = {item["scenario_id"] for item in result["hardening_scenarios"]}

    assert result["result"] == PARTIAL_PASS
    assert "LLM_ASSISTED_EXPLANATION" in scenario_ids
    assert result["issues"][0]["category"] == "PROVIDER"
    assert result["issues"][0]["severity"] == "P1"


def test_worker_unavailable_records_partial_pass_and_blocker(tmp_path) -> None:
    result = record_acli_hardening_interaction(
        hardening_id="HARDENING-006",
        interaction_id="INTERACTION-006",
        completed_interaction=_completed_interaction(
            executed=False,
            execution_performed=False,
            worker_status="WORKER_UNAVAILABLE",
            worker_unavailable=True,
            validation_status="NOT_RUN",
            validated=False,
        ),
        replay_dir=tmp_path / "hardening",
        created_at=CREATED_AT,
    )

    assert result["result"] == PARTIAL_PASS
    assert result["issues"][0]["category"] == "WORKER"
    assert result["dashboards"]["remaining_production_blockers"]["open_major_issues"] == 1


def test_operator_feedback_confusion_records_p2_without_blocking_production(tmp_path) -> None:
    result = record_acli_hardening_interaction(
        hardening_id="HARDENING-007",
        interaction_id="INTERACTION-007",
        completed_interaction=_completed_interaction(),
        operator_feedback={"clarity": "Somewhat Confusing", "free_text": "The approval explanation was too technical."},
        replay_dir=tmp_path / "hardening",
        created_at=CREATED_AT,
    )

    assert result["result"] == PASS
    assert result["issues"][0]["severity"] == "P2"
    assert result["issues"][0]["category"] == "UX"
    assert result["dashboards"]["remaining_production_blockers"]["production_blockers"] == 0


def test_prior_state_accumulates_statistics_coverage_and_dashboards(tmp_path) -> None:
    first = record_acli_hardening_interaction(
        hardening_id="HARDENING-008",
        interaction_id="INTERACTION-008",
        completed_interaction=_completed_interaction(),
        replay_dir=tmp_path / "hardening-1",
        created_at=CREATED_AT,
    )
    second = record_acli_hardening_interaction(
        hardening_id="HARDENING-009",
        interaction_id="INTERACTION-009",
        completed_interaction=_completed_interaction(
            approval_status="REJECTED",
            executed=False,
            execution_performed=False,
            worker_status="NOT_INVOKED",
            validation_status="NOT_RUN",
            validated=False,
        ),
        prior_hardening_state=first,
        replay_dir=tmp_path / "hardening-2",
        created_at=CREATED_AT,
    )
    rendered = render_platform_hardening_progress(second)

    assert second["hardening_statistics"]["total_interactions"] == 2
    assert second["hardening_statistics"]["result_counts"][PASS] == 2
    assert second["scenario_coverage"]["covered_scenarios"]["APPROVAL"] == 1
    assert second["scenario_coverage"]["covered_scenarios"]["REJECT"] == 1
    assert "Platform Hardening Progress" in rendered
    assert "Production Readiness Score" in rendered


def test_replay_reconstructs_hardening_evidence(tmp_path) -> None:
    result = record_acli_hardening_interaction(
        hardening_id="HARDENING-010",
        interaction_id="INTERACTION-010",
        completed_interaction=_completed_interaction(),
        replay_dir=tmp_path / "hardening",
        created_at=CREATED_AT,
    )

    reconstructed = reconstruct_acli_hardening_replay(tmp_path / "hardening")

    assert reconstructed["hardening_id"] == result["hardening_id"]
    assert reconstructed["interaction_id"] == result["interaction_id"]
    assert reconstructed["result"] == PASS
    assert reconstructed["artifact_hash"] == result["hardening_artifact"]["artifact_hash"]
    assert reconstructed["authority_flags"]["authorizes_execution"] is False


def test_replay_tampering_fails_closed(tmp_path) -> None:
    record_acli_hardening_interaction(
        hardening_id="HARDENING-011",
        interaction_id="INTERACTION-011",
        completed_interaction=_completed_interaction(),
        replay_dir=tmp_path / "hardening",
        created_at=CREATED_AT,
    )
    path = tmp_path / "hardening" / "000_acli_hardening_evidence_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["result"] = FAIL
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_acli_hardening_replay(tmp_path / "hardening")


def test_malformed_completed_interaction_fails_before_replay_write(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="completed_interaction must be a JSON object"):
        record_acli_hardening_interaction(
            hardening_id="HARDENING-012",
            interaction_id="INTERACTION-012",
            completed_interaction=[],  # type: ignore[arg-type]
            replay_dir=tmp_path / "hardening",
            created_at=CREATED_AT,
        )

    assert not (tmp_path / "hardening").exists()


def test_invalid_operator_feedback_choice_fails_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="operator feedback clarity choice is invalid"):
        record_acli_hardening_interaction(
            hardening_id="HARDENING-013",
            interaction_id="INTERACTION-013",
            completed_interaction=_completed_interaction(),
            operator_feedback={"clarity": "Sort Of Fine"},
            replay_dir=tmp_path / "hardening",
            created_at=CREATED_AT,
        )

    assert not (tmp_path / "hardening").exists()


def test_hardening_artifact_hash_is_stable_and_replay_visible(tmp_path) -> None:
    result = record_acli_hardening_interaction(
        hardening_id="HARDENING-014",
        interaction_id="INTERACTION-014",
        completed_interaction=_completed_interaction(),
        replay_dir=tmp_path / "hardening",
        created_at=CREATED_AT,
    )
    artifact = dict(result["hardening_artifact"])
    actual = artifact.pop("artifact_hash")

    assert actual == replay_hash(artifact)
    assert result["hardening_artifact"]["replay_visible"] is True
    assert result["hardening_artifact"]["read_only"] is True


def test_fail_closed_interaction_records_comparable_evidence(tmp_path) -> None:
    result = record_acli_hardening_interaction(
        hardening_id="HARDENING-015",
        interaction_id="INTERACTION-015",
        completed_interaction=_completed_interaction(
            prompt="continue ppp",
            workflow_id="OCS_LLM_COGNITION",
            routing_confidence="MEDIUM",
            fail_closed=True,
            response_status="FAILED_CLOSED",
            failure_reason="OCS cognition failed closed: no provider cognition artifacts available",
            executed=False,
            execution_performed=False,
            worker_status="NOT_INVOKED",
            validation_status="NOT_RUN",
            validated=False,
        ),
        replay_dir=tmp_path / "hardening",
        created_at=CREATED_AT,
    )

    evidence = result["evidence_completeness"]

    assert result["result"] == PARTIAL_PASS
    assert evidence["operator_prompt"]["prompt_text"] == "continue ppp"
    assert evidence["workflow"]["workflow_id"] == "OCS_LLM_COGNITION"
    assert evidence["workflow"]["routing_confidence"] == "MEDIUM"
    assert evidence["fail_closed"]["fail_closed"] is True
    assert evidence["fail_closed"]["fail_closed_reason"] == (
        "OCS cognition failed closed: no provider cognition artifacts available"
    )
    assert evidence["execution_status"]["execution_performed"] is False
    assert "ARCHITECTURE" in {issue["category"] for issue in result["issues"]}
