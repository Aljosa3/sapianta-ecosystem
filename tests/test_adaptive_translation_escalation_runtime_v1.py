"""Tests for ADAPTIVE_TRANSLATION_ESCALATION_RUNTIME_V1."""

from __future__ import annotations

from copy import deepcopy

import pytest

from aigol.runtime.adaptive_translation_escalation_runtime import (
    DETERMINISTIC_FALLBACK_USED,
    DETERMINISTIC_SELECTED,
    PROVIDER_SELECTED,
    TIER_HIGH_CAPABILITY,
    TIER_LOW_COST,
    TIER_MEDIUM_CAPABILITY,
    reconstruct_adaptive_translation_escalation_replay,
    run_adaptive_translation_escalation,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, load_json
from aigol.runtime.universal_translation_artifact_schema import (
    GOVERNANCE_TO_HUMAN,
    HIGH,
    HUMAN_TO_GOVERNANCE,
    LOW,
    MATERIAL_AMBIGUITY,
    NO_AMBIGUITY,
    create_universal_translation_artifact,
    translation_artifact_hash,
)


CREATED_AT = "2026-06-25T00:00:00Z"


def _translation_request() -> dict:
    return {
        "translation_request_id": "ADAPTIVE-REQUEST-001",
        "operator_context": "test-operator",
        "created_at": CREATED_AT,
    }


def _human_to_governance_artifact(*, confidence: str = LOW) -> dict:
    return create_universal_translation_artifact(
        translation_id="HTG-ADAPTIVE-001",
        translation_request=_translation_request(),
        source_direction=HUMAN_TO_GOVERNANCE,
        source_payload={"human_request": "Fix this."},
        normalized_intent={"intent_family": "CLARIFICATION_REQUIRED"},
        translated_governance_payload={
            "workflow_candidate": "HUMAN_INTENT_CLARIFICATION_INTAKE",
            "entities": {"artifact_identifiers": [], "target_paths": []},
            "clarification_required": True,
        },
        ambiguity_flags={
            "ambiguity_status": MATERIAL_AMBIGUITY,
            "clarification_required": True,
            "clarification_questions": ["Which domain should this request use?"],
        },
        confidence=confidence,
        replay_reference="/tmp/replay/htg-adaptive",
        created_at=CREATED_AT,
    )


def _governance_to_human_artifact(*, completeness: str = "COMPLETE") -> dict:
    return create_universal_translation_artifact(
        translation_id="GTH-ADAPTIVE-001",
        translation_request=_translation_request(),
        source_direction=GOVERNANCE_TO_HUMAN,
        source_payload={"governance_state": {"workflow": "GOVERNED_DEVELOPMENT_WORKFLOW"}},
        normalized_intent={"workflow": "GOVERNED_DEVELOPMENT_WORKFLOW"},
        human_readable_payload={
            "summary": "ACLI is waiting for approval.",
            "translation_completeness": completeness,
            "authoritative_state_references": {
                "governance_state_hash": "sha256:governance",
                "proposal_state_hash": "sha256:proposal",
                "replay_reference": "/tmp/replay/gth-adaptive",
            },
        },
        ambiguity_flags={
            "ambiguity_status": NO_AMBIGUITY,
            "clarification_required": False,
            "clarification_questions": [],
        },
        confidence=HIGH,
        replay_reference="/tmp/replay/gth-adaptive",
        created_at=CREATED_AT,
    )


def _provider_response_for_human_to_governance(request: dict) -> dict:
    return {
        "translation_candidate": {
            "translated_governance_payload": {
                "workflow_candidate": "GOVERNED_DEVELOPMENT_WORKFLOW",
                "entities": {"artifact_identifiers": [], "target_paths": []},
                "clarification_required": True,
                "clarification_questions": ["Please describe the desired implementation target."],
            }
        },
        "confidence": "MEDIUM",
        "limitations": ["Provider output remains advisory."],
        "preserved_authoritative_references": request["preservation_requirements"]["authoritative_references"],
        "estimated_cost": 0.001,
        "cost_units": "USD",
        "advisory_only": True,
        "authority_granted": False,
        "approval_authority": False,
        "execution_authority": False,
    }


def _provider_response_for_governance_to_human(request: dict) -> dict:
    return {
        "translation_candidate": {
            "human_readable_payload": {
                "summary": "ACLI has a proposal waiting for your approval.",
                "translation_completeness": "COMPLETE",
                "authoritative_state_references": request["preservation_requirements"]["authoritative_references"],
            }
        },
        "confidence": "HIGH",
        "limitations": [],
        "preserved_authoritative_references": request["preservation_requirements"]["authoritative_references"],
        "estimated_cost": 0.002,
        "cost_units": "USD",
        "advisory_only": True,
        "authority_granted": False,
        "approval_authority": False,
        "execution_authority": False,
    }


def test_deterministic_translation_is_selected_when_no_escalation_required(tmp_path) -> None:
    deterministic = _governance_to_human_artifact()

    result = run_adaptive_translation_escalation(
        translation_request_id="ADAPTIVE-001",
        deterministic_translation_artifact=deterministic,
        replay_dir=tmp_path / "adaptive",
        created_at=CREATED_AT,
    )

    assert result["translation_status"] == DETERMINISTIC_SELECTED
    assert result["selected_translation_artifact"] == deterministic
    assert result["provider_attempts"] == []
    assert result["provider_invoked"] is False
    assert result["authority_granted"] is False


def test_low_cost_provider_is_used_first_when_escalation_required(tmp_path) -> None:
    deterministic = _human_to_governance_artifact()

    result = run_adaptive_translation_escalation(
        translation_request_id="ADAPTIVE-002",
        deterministic_translation_artifact=deterministic,
        provider_candidates=[
            {
                "provider_id": "high-provider",
                "provider_tier": TIER_HIGH_CAPABILITY,
                "estimated_cost": 0.03,
                "provider": _provider_response_for_human_to_governance,
            },
            {
                "provider_id": "low-provider",
                "provider_tier": TIER_LOW_COST,
                "estimated_cost": 0.001,
                "provider": _provider_response_for_human_to_governance,
            },
        ],
        replay_dir=tmp_path / "adaptive",
        created_at=CREATED_AT,
    )

    assert result["translation_status"] == PROVIDER_SELECTED
    assert result["provider_attempts"][0]["provider_id"] == "low-provider"
    assert len(result["provider_attempts"]) == 1
    assert result["selected_translation_artifact"]["source_direction"] == HUMAN_TO_GOVERNANCE
    assert result["selected_translation_artifact"]["provider_metadata"]["provider_used"] is True
    assert result["cost_metrics"]["estimated_total_cost"] == 0.001


def test_provider_authority_claim_is_rejected_and_next_tier_can_succeed(tmp_path) -> None:
    deterministic = _governance_to_human_artifact(completeness="INCOMPLETE")

    def authority_claiming_provider(request: dict) -> dict:
        response = _provider_response_for_governance_to_human(request)
        response["authority_granted"] = True
        return response

    result = run_adaptive_translation_escalation(
        translation_request_id="ADAPTIVE-003",
        deterministic_translation_artifact=deterministic,
        provider_candidates=[
            {
                "provider_id": "low-provider",
                "provider_tier": TIER_LOW_COST,
                "estimated_cost": 0.001,
                "provider": authority_claiming_provider,
            },
            {
                "provider_id": "medium-provider",
                "provider_tier": TIER_MEDIUM_CAPABILITY,
                "estimated_cost": 0.01,
                "provider": _provider_response_for_governance_to_human,
            },
        ],
        replay_dir=tmp_path / "adaptive",
        created_at=CREATED_AT,
    )

    assert result["translation_status"] == PROVIDER_SELECTED
    assert result["provider_attempts"][0]["attempt_status"] == "REJECTED"
    assert "CLAIMS_AUTHORITY" in result["provider_attempts"][0]["rejection_reason"]
    assert result["provider_attempts"][1]["attempt_status"] == "ACCEPTED"
    assert result["selected_translation_artifact"]["human_readable_payload"]["summary"].startswith("ACLI has a proposal")


def test_provider_unavailable_falls_back_to_deterministic_translation(tmp_path) -> None:
    deterministic = _human_to_governance_artifact()

    result = run_adaptive_translation_escalation(
        translation_request_id="ADAPTIVE-004",
        deterministic_translation_artifact=deterministic,
        provider_candidates=[
            {
                "provider_id": "missing-provider",
                "provider_tier": TIER_LOW_COST,
                "estimated_cost": 0.001,
            }
        ],
        replay_dir=tmp_path / "adaptive",
        created_at=CREATED_AT,
    )

    assert result["translation_status"] == DETERMINISTIC_FALLBACK_USED
    assert result["selected_translation_artifact"] == deterministic
    assert result["provider_attempts"][0]["provider_invoked"] is False
    assert "PROVIDER_NOT_CONFIGURED" in result["fallback_reason"]


def test_operator_request_can_trigger_provider_explanation(tmp_path) -> None:
    deterministic = _governance_to_human_artifact()

    result = run_adaptive_translation_escalation(
        translation_request_id="ADAPTIVE-005",
        deterministic_translation_artifact=deterministic,
        operator_requests_improved_explanation=True,
        provider_candidates=[
            {
                "provider_id": "low-provider",
                "provider_tier": TIER_LOW_COST,
                "estimated_cost": 0.002,
                "provider": _provider_response_for_governance_to_human,
            }
        ],
        replay_dir=tmp_path / "adaptive",
        created_at=CREATED_AT,
    )

    assert "OPERATOR_REQUESTED_IMPROVED_EXPLANATION" in result["escalation_reasons"]
    assert result["translation_status"] == PROVIDER_SELECTED
    assert result["selected_translation_artifact"]["source_direction"] == GOVERNANCE_TO_HUMAN


def test_replay_reconstructs_selected_translation_and_attempts(tmp_path) -> None:
    deterministic = _human_to_governance_artifact()
    result = run_adaptive_translation_escalation(
        translation_request_id="ADAPTIVE-006",
        deterministic_translation_artifact=deterministic,
        provider_candidates=[
            {
                "provider_id": "low-provider",
                "provider_tier": TIER_LOW_COST,
                "estimated_cost": 0.001,
                "provider": _provider_response_for_human_to_governance,
            }
        ],
        replay_dir=tmp_path / "adaptive",
        created_at=CREATED_AT,
    )

    reconstructed = reconstruct_adaptive_translation_escalation_replay(tmp_path / "adaptive")

    assert reconstructed["translation_status"] == result["translation_status"]
    assert reconstructed["selected_translation_artifact"] == result["selected_translation_artifact"]
    assert translation_artifact_hash(reconstructed["selected_translation_artifact"]).startswith("sha256:")
    assert reconstructed["provider_attempts"][0]["attempt_status"] == "ACCEPTED"
    assert reconstructed["authority_granted"] is False


def test_malformed_deterministic_translation_fails_closed_before_replay_write(tmp_path) -> None:
    replay_dir = tmp_path / "adaptive"

    with pytest.raises(FailClosedRuntimeError, match="malformed structure"):
        run_adaptive_translation_escalation(
            translation_request_id="ADAPTIVE-007",
            deterministic_translation_artifact={"bad": "artifact"},
            replay_dir=replay_dir,
            created_at=CREATED_AT,
        )

    assert not replay_dir.exists()


def test_replay_tampering_fails_closed(tmp_path) -> None:
    deterministic = _human_to_governance_artifact()
    run_adaptive_translation_escalation(
        translation_request_id="ADAPTIVE-008",
        deterministic_translation_artifact=deterministic,
        provider_candidates=[
            {
                "provider_id": "low-provider",
                "provider_tier": TIER_LOW_COST,
                "estimated_cost": 0.001,
                "provider": _provider_response_for_human_to_governance,
            }
        ],
        replay_dir=tmp_path / "adaptive",
        created_at=CREATED_AT,
    )
    replay_file = tmp_path / "adaptive" / "000_adaptive_translation_escalation_recorded.json"
    wrapper = load_json(replay_file)
    wrapper["artifact"]["final_status"] = "TAMPERED"
    replay_file.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="replay hash mismatch"):
        reconstruct_adaptive_translation_escalation_replay(tmp_path / "adaptive")
