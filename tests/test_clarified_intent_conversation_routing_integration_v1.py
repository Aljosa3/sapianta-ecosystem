"""Tests for AIGOL_CLARIFIED_INTENT_CONVERSATION_ROUTING_INTEGRATION_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.clarified_intent_conversation_routing_integration import (
    CLARIFIED_INTENT_CONVERSATION_PPP_READY,
    CLARIFIED_INTENT_CONVERSATION_ROUTING_ARTIFACT_V1,
    FAILED_CLOSED,
    reconstruct_clarified_intent_conversation_routing_replay,
    run_clarified_intent_conversation_routing_integration,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize


CREATED_AT = "2026-06-03T23:55:00+00:00"
CHAIN_ID = "CHAIN-CLARIFIED-CONVERSATION-000001"


def _candidates() -> list[dict]:
    return [
        {
            "interpretation_id": "DOMAIN_FOUNDATION",
            "label": "Create a new employee-management domain.",
            "domain_id": "HR",
            "worker_family_id": "EMPLOYEE_MANAGEMENT",
            "milestone_type": "DOMAIN_FOUNDATION",
            "capability_id": "DOMAIN_ARCHITECTURE",
            "resource_category": "DOMAIN_RUNTIME",
            "output_scope": "DOMAIN_FOUNDATION",
            "resume_stage": "COGNITION",
        },
        {
            "interpretation_id": "INFRASTRUCTURE_WORKSTATION",
            "label": "Provision an operator workstation infrastructure component.",
            "domain_id": "AIGOL_CORE",
            "worker_family_id": "INFRASTRUCTURE",
            "milestone_type": "INFRASTRUCTURE_COMPONENT",
            "capability_id": "INFRASTRUCTURE",
            "resource_category": "OPERATOR_TOOL",
            "output_scope": "INFRASTRUCTURE_SPEC",
            "resume_stage": "TASK_INTAKE",
        },
    ]


def _response(**overrides) -> dict:
    response = {
        "selected_interpretation": "DOMAIN_FOUNDATION",
        "selected_domain_id": "HR",
        "selected_worker_family_id": "EMPLOYEE_MANAGEMENT",
        "selected_milestone_type": "DOMAIN_FOUNDATION",
        "selected_output_scope": "DOMAIN_FOUNDATION",
        "human_response_text": "Create a new employee-management domain.",
        "resume_stage": "COGNITION",
    }
    response.update(overrides)
    return response


def _run(tmp_path, *, response: dict | None = None, chain_id: str = CHAIN_ID):
    return run_clarified_intent_conversation_routing_integration(
        prompt_id="PROMPT-CLARIFIED-CONVERSATION-000001",
        human_prompt="Create a workstation.",
        ambiguity_categories=[
            "DOMAIN_AMBIGUITY",
            "WORKER_AMBIGUITY",
            "CAPABILITY_AMBIGUITY",
            "INTENT_AMBIGUITY",
            "RESOURCE_AMBIGUITY",
        ],
        candidate_interpretations=_candidates(),
        human_response=response or _response(),
        canonical_chain_id=chain_id,
        created_at=CREATED_AT,
        replay_dir=tmp_path,
    )


def test_conversation_routes_ambiguous_prompt_through_clarified_path_to_ppp(tmp_path) -> None:
    capture = _run(tmp_path)
    reconstructed = reconstruct_clarified_intent_conversation_routing_replay(tmp_path)
    route = capture["clarified_intent_conversation_routing_artifact"]

    assert capture["route_status"] == CLARIFIED_INTENT_CONVERSATION_PPP_READY
    assert route["artifact_type"] == CLARIFIED_INTENT_CONVERSATION_ROUTING_ARTIFACT_V1
    assert capture["canonical_chain_id"] == CHAIN_ID
    assert capture["clarification_status"] == "CLARIFICATION_RESOLVED"
    assert capture["cognition_status"] == "CLARIFIED_COGNITION_INPUT_CREATED"
    assert capture["resource_selection_routing_status"] == "CLARIFIED_RESOURCE_SELECTION_INTENT_ROUTED"
    assert capture["ppp_routing_status"] == "CLARIFIED_PPP_INTENT_ROUTED"
    assert capture["selected_interpretation"] == "DOMAIN_FOUNDATION"
    assert capture["domain_reference"] == "HR"
    assert capture["proposal_validation_status"] == "AWAITING_PROVIDER_PROPOSAL"
    assert capture["approval_evidence_status"] == "AWAITING_VALIDATED_PROPOSAL"
    assert capture["handoff_status"] == "AWAITING_VALIDATED_PROPOSAL"
    assert route["conversation_orchestration_only"] is True
    assert route["provider_invoked"] is False
    assert route["worker_invoked"] is False
    assert route["authorization_created"] is False
    assert route["execution_requested"] is False
    assert route["dispatch_requested"] is False
    assert reconstructed["route_status"] == CLARIFIED_INTENT_CONVERSATION_PPP_READY
    assert reconstructed["replay_artifact_count"] == 2


def test_conversation_orchestration_fails_closed_when_clarification_unresolved(tmp_path) -> None:
    capture = _run(tmp_path, response=_response(selected_interpretation="UNKNOWN"))

    assert capture["route_status"] == FAILED_CLOSED
    assert capture["fail_closed"] is True
    assert "clarification unresolved" in capture["failure_reason"]
    assert capture["provider_invoked"] is False
    assert capture["execution_requested"] is False


def test_conversation_orchestration_fails_closed_when_ambiguity_not_detected(tmp_path) -> None:
    capture = run_clarified_intent_conversation_routing_integration(
        prompt_id="PROMPT-CLARIFIED-CONVERSATION-NO-AMBIGUITY",
        human_prompt="Create a workstation.",
        ambiguity_categories=[],
        candidate_interpretations=_candidates(),
        human_response=_response(),
        canonical_chain_id=CHAIN_ID,
        created_at=CREATED_AT,
        replay_dir=tmp_path,
    )

    assert capture["route_status"] == FAILED_CLOSED
    assert "ambiguity not detected" in capture["failure_reason"]


def test_conversation_route_reconstruction_detects_corruption(tmp_path) -> None:
    _run(tmp_path)
    path = tmp_path / "clarified_intent_conversation_route" / "000_clarified_intent_conversation_route_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["domain_reference"] = "CORRUPTED"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_clarified_intent_conversation_routing_replay(tmp_path)


def test_conversation_route_preserves_ppp_source_agnostic_contract(tmp_path) -> None:
    capture = _run(tmp_path)
    ppp = capture["clarified_ppp_routing"]
    contract = ppp["ppp_input_contract"]

    assert set(contract) == {
        "intent_reference",
        "workflow_type",
        "required_capability",
        "requested_role_type",
        "domain_id",
        "provider_necessity_classification",
        "confidence",
        "ppp_stage",
        "intent_source_visible_to_ppp",
    }
    assert contract["intent_source_visible_to_ppp"] is False
    assert "HUMAN_CLARIFICATION" not in contract.values()


def test_clarified_conversation_routing_has_no_provider_worker_or_execution_invocations() -> None:
    import aigol.runtime.clarified_intent_conversation_routing_integration as runtime

    source = inspect.getsource(runtime)

    assert "produce_provider_development_proposal(" not in source
    assert "run_provider_attachment(" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source
