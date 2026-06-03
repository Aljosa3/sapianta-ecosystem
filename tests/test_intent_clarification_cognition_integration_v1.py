"""Tests for AIGOL_INTENT_CLARIFICATION_COGNITION_INTEGRATION_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.intent_clarification_cognition_integration import (
    CLARIFICATION_COGNITION_CLASSIFICATION_V1,
    CLARIFICATION_COGNITION_EVIDENCE_V1,
    CLARIFIED_COGNITION_INPUT_ARTIFACT_V1,
    CLARIFIED_COGNITION_INPUT_CREATED,
    FAILED_CLOSED,
    integrate_clarification_resolution_with_cognition,
    reconstruct_intent_clarification_cognition_integration_replay,
)
from aigol.runtime.intent_clarification_dialog_runtime import run_intent_clarification_dialog
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-03T22:15:00+00:00"
CHAIN_ID = "CHAIN-CLARIFICATION-COGNITION-000001"


def _candidates() -> list[dict]:
    return [
        {
            "interpretation_id": "WORKER_FOUNDATION",
            "label": "Create a Trading Risk Analysis worker foundation.",
            "domain_id": "TRADING",
            "worker_family_id": "RISK_ANALYSIS",
            "milestone_type": "WORKER_FOUNDATION",
            "capability_id": "ANALYSIS",
            "resource_category": "WORKER",
            "output_scope": "GOVERNANCE_FOUNDATION",
            "resume_stage": "COGNITION",
        },
        {
            "interpretation_id": "REPORTING_PORTAL",
            "label": "Create a Marketing reporting portal foundation.",
            "domain_id": "MARKETING",
            "worker_family_id": None,
            "milestone_type": "PORTAL_FOUNDATION",
            "capability_id": "REPORTING",
            "resource_category": "DOMAIN_RUNTIME",
            "output_scope": "PORTAL_FOUNDATION",
            "resume_stage": "TASK_INTAKE",
        },
    ]


def _response(**overrides) -> dict:
    response = {
        "selected_interpretation": "WORKER_FOUNDATION",
        "selected_domain_id": "TRADING",
        "selected_worker_family_id": "RISK_ANALYSIS",
        "selected_milestone_type": "WORKER_FOUNDATION",
        "selected_output_scope": "GOVERNANCE_FOUNDATION",
        "human_response_text": "Use Trading Risk Analysis worker foundation.",
        "resume_stage": "COGNITION",
    }
    response.update(overrides)
    return response


def _clarification_capture(tmp_path, *, response: dict | None = None, chain_id: str = CHAIN_ID):
    return run_intent_clarification_dialog(
        clarification_id="CLARIFICATION-COGNITION-000001",
        canonical_chain_id=chain_id,
        human_prompt_reference="PROMPT-CLARIFICATION-COGNITION-000001",
        human_prompt="Add analysis.",
        ambiguity_categories=["INTENT_AMBIGUITY", "WORKER_AMBIGUITY", "CAPABILITY_AMBIGUITY"],
        candidate_interpretations=_candidates(),
        human_response=response or _response(),
        clarification_history=[
            {
                "clarification_request_reference": "PRIOR-REQUEST",
                "clarification_response_reference": "PRIOR-RESPONSE",
                "resolution_status": "ADDITIONAL_CLARIFICATION_REQUIRED",
            }
        ],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "clarification",
    )


def test_integrates_resolved_clarification_into_cognition_input(tmp_path) -> None:
    clarification = _clarification_capture(tmp_path)
    capture = integrate_clarification_resolution_with_cognition(
        integration_id="CLARIFICATION-COGNITION-INTEGRATION-000001",
        clarification_request_artifact=clarification["human_clarification_request_artifact"],
        clarification_response_artifact=clarification["human_clarification_response_artifact"],
        clarification_resolution_artifact=clarification["human_clarification_resolution_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "integration",
    )
    reconstructed = reconstruct_intent_clarification_cognition_integration_replay(tmp_path / "integration")
    evidence = capture["clarification_cognition_evidence_artifact"]
    classification = capture["clarification_cognition_classification_artifact"]
    clarified = capture["clarified_cognition_input_artifact"]

    assert evidence["artifact_type"] == CLARIFICATION_COGNITION_EVIDENCE_V1
    assert classification["artifact_type"] == CLARIFICATION_COGNITION_CLASSIFICATION_V1
    assert clarified["artifact_type"] == CLARIFIED_COGNITION_INPUT_ARTIFACT_V1
    assert capture["integration_status"] == CLARIFIED_COGNITION_INPUT_CREATED
    assert clarified["cognition_input_type"] == "STRUCTURED_INTENT"
    assert clarified["normalized_intent_class"] == "WORKER_FOUNDATION"
    assert clarified["domain_id"] == "TRADING"
    assert clarified["worker_family_id"] == "RISK_ANALYSIS"
    assert clarified["confidence"] == "DETERMINISTIC"
    assert clarified["source_lineage_preserved"] is True
    assert clarified["intent_source_visible_to_cognition"] is False
    assert len(clarified["clarification_history"]) == 2
    assert capture["cognition_invoked"] is False
    assert capture["ppp_invoked"] is False
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["authorization_created"] is False
    assert capture["execution_requested"] is False
    assert capture["dispatch_requested"] is False
    assert reconstructed["integration_status"] == CLARIFIED_COGNITION_INPUT_CREATED
    assert reconstructed["replay_artifact_count"] == 4


def test_resolved_and_direct_intent_are_equivalent_cognition_inputs(tmp_path) -> None:
    clarification = _clarification_capture(tmp_path)
    capture = integrate_clarification_resolution_with_cognition(
        integration_id="CLARIFICATION-COGNITION-EQUIVALENCE-000001",
        clarification_request_artifact=clarification["human_clarification_request_artifact"],
        clarification_response_artifact=clarification["human_clarification_response_artifact"],
        clarification_resolution_artifact=clarification["human_clarification_resolution_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "equivalence",
    )
    contract = capture["cognition_input_contract"]

    assert set(contract) == {
        "intent_reference",
        "normalized_intent",
        "normalized_intent_class",
        "domain_id",
        "worker_family_id",
        "milestone_type",
        "capability_id",
        "resource_category",
        "confidence",
        "intent_source_visible_to_cognition",
    }
    assert contract["intent_source_visible_to_cognition"] is False
    assert "HUMAN_CLARIFICATION" not in contract.values()


def test_integration_fails_closed_when_clarification_unresolved(tmp_path) -> None:
    clarification = _clarification_capture(tmp_path, response=_response(selected_interpretation="UNKNOWN"))
    capture = integrate_clarification_resolution_with_cognition(
        integration_id="CLARIFICATION-COGNITION-UNRESOLVED-000001",
        clarification_request_artifact=clarification["human_clarification_request_artifact"],
        clarification_response_artifact=clarification["human_clarification_response_artifact"],
        clarification_resolution_artifact=clarification["human_clarification_resolution_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "unresolved_integration",
    )

    assert capture["integration_status"] == FAILED_CLOSED
    assert "clarification unresolved" in capture["failure_reason"]


def test_integration_fails_closed_when_clarification_contradictory(tmp_path) -> None:
    clarification = _clarification_capture(tmp_path, response=_response(selected_domain_id="MARKETING"))
    capture = integrate_clarification_resolution_with_cognition(
        integration_id="CLARIFICATION-COGNITION-CONTRADICTION-000001",
        clarification_request_artifact=clarification["human_clarification_request_artifact"],
        clarification_response_artifact=clarification["human_clarification_response_artifact"],
        clarification_resolution_artifact=clarification["human_clarification_resolution_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "contradiction_integration",
    )

    assert capture["integration_status"] == FAILED_CLOSED
    assert "contradictory clarification" in capture["failure_reason"]


def test_integration_fails_closed_on_replay_corruption(tmp_path) -> None:
    clarification = _clarification_capture(tmp_path)
    request = dict(clarification["human_clarification_request_artifact"])
    response = dict(clarification["human_clarification_response_artifact"])
    response["clarification_request_hash"] = "sha256:not-real"
    response.pop("artifact_hash")
    response["artifact_hash"] = replay_hash(response)

    capture = integrate_clarification_resolution_with_cognition(
        integration_id="CLARIFICATION-COGNITION-CORRUPTION-000001",
        clarification_request_artifact=request,
        clarification_response_artifact=response,
        clarification_resolution_artifact=clarification["human_clarification_resolution_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corruption",
    )

    assert capture["integration_status"] == FAILED_CLOSED
    assert "replay corruption" in capture["failure_reason"]


def test_integration_fails_closed_on_chain_continuity_failure(tmp_path) -> None:
    clarification = _clarification_capture(tmp_path)
    response = dict(clarification["human_clarification_response_artifact"])
    response["canonical_chain_id"] = "DIFFERENT-CHAIN"
    response.pop("artifact_hash")
    response["artifact_hash"] = replay_hash(response)
    resolution = dict(clarification["human_clarification_resolution_artifact"])
    resolution["clarification_response_hash"] = response["artifact_hash"]
    resolution.pop("artifact_hash")
    resolution["artifact_hash"] = replay_hash(resolution)

    capture = integrate_clarification_resolution_with_cognition(
        integration_id="CLARIFICATION-COGNITION-CHAIN-000001",
        clarification_request_artifact=clarification["human_clarification_request_artifact"],
        clarification_response_artifact=response,
        clarification_resolution_artifact=resolution,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "chain",
    )

    assert capture["integration_status"] == FAILED_CLOSED
    assert "invalid chain continuity" in capture["failure_reason"]


def test_reconstruction_detects_corrupt_integration_replay(tmp_path) -> None:
    clarification = _clarification_capture(tmp_path)
    integrate_clarification_resolution_with_cognition(
        integration_id="CLARIFICATION-COGNITION-CORRUPT-REPLAY-000001",
        clarification_request_artifact=clarification["human_clarification_request_artifact"],
        clarification_response_artifact=clarification["human_clarification_response_artifact"],
        clarification_resolution_artifact=clarification["human_clarification_resolution_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt_replay",
    )
    path = tmp_path / "corrupt_replay" / "002_clarified_cognition_input_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["normalized_intent"] = "corrupted"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_intent_clarification_cognition_integration_replay(tmp_path / "corrupt_replay")


def test_intent_clarification_cognition_integration_has_no_cognition_ppp_provider_worker_or_execution_invocations() -> None:
    import aigol.runtime.intent_clarification_cognition_integration as runtime

    source = inspect.getsource(runtime)

    assert "route_improvement_intent_to_cognition(" not in source
    assert "produce_provider_development_proposal(" not in source
    assert "run_provider_attachment(" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source
