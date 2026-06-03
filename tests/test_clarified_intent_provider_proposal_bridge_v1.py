"""Tests for AIGOL_CLARIFIED_INTENT_PROVIDER_PROPOSAL_BRIDGE_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.clarified_intent_conversation_routing_integration import (
    run_clarified_intent_conversation_routing_integration,
)
from aigol.runtime.clarified_intent_provider_proposal_bridge import (
    CLARIFIED_PROVIDER_PROPOSAL_BRIDGE_CLASSIFICATION_V1,
    CLARIFIED_PROVIDER_PROPOSAL_BRIDGE_EVIDENCE_V1,
    CLARIFIED_PROVIDER_PROPOSAL_REQUEST_ARTIFACT_V1,
    CLARIFIED_PROVIDER_PROPOSAL_REQUEST_READY,
    FAILED_CLOSED,
    bridge_clarified_ppp_intent_to_provider_proposal_request,
    reconstruct_clarified_intent_provider_proposal_bridge_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_proposal_production_runtime import PROVIDER_REQUEST_PACKET_V1
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-03T23:59:00+00:00"
CHAIN_ID = "CHAIN-CLARIFIED-PROVIDER-BRIDGE-000001"
PROVIDER_ID = "OPENAI"


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


def _conversation_capture(tmp_path, *, response: dict | None = None):
    return run_clarified_intent_conversation_routing_integration(
        prompt_id="PROMPT-CLARIFIED-PROVIDER-BRIDGE-000001",
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
        canonical_chain_id=CHAIN_ID,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "conversation",
    )


def _bridge_capture(tmp_path, *, conversation: dict | None = None, provider_id: str = PROVIDER_ID, selected_provider_id: str | None = None):
    conversation = conversation or _conversation_capture(tmp_path)
    ppp = conversation["clarified_ppp_routing"]
    return bridge_clarified_ppp_intent_to_provider_proposal_request(
        bridge_id="CLARIFIED-PROVIDER-BRIDGE-000001",
        provider_id=provider_id,
        selected_provider_id=selected_provider_id,
        clarified_ppp_routed_intent_artifact=ppp["clarified_ppp_routed_intent_artifact"],
        clarified_ppp_routing_evidence_artifact=ppp["clarified_ppp_routing_evidence_artifact"],
        clarified_ppp_routing_classification_artifact=ppp["clarified_ppp_routing_classification_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "bridge",
    )


def test_bridges_clarified_ppp_intent_to_provider_proposal_request(tmp_path) -> None:
    capture = _bridge_capture(tmp_path)
    reconstructed = reconstruct_clarified_intent_provider_proposal_bridge_replay(tmp_path / "bridge")
    request = capture["clarified_provider_proposal_request_artifact"]

    assert capture["request_status"] == CLARIFIED_PROVIDER_PROPOSAL_REQUEST_READY
    assert capture["clarified_provider_proposal_bridge_evidence_artifact"]["artifact_type"] == (
        CLARIFIED_PROVIDER_PROPOSAL_BRIDGE_EVIDENCE_V1
    )
    assert capture["clarified_provider_proposal_bridge_classification_artifact"]["artifact_type"] == (
        CLARIFIED_PROVIDER_PROPOSAL_BRIDGE_CLASSIFICATION_V1
    )
    assert request["artifact_type"] == CLARIFIED_PROVIDER_PROPOSAL_REQUEST_ARTIFACT_V1
    assert request["provider_request_packet_type"] == PROVIDER_REQUEST_PACKET_V1
    assert request["provider_id"] == PROVIDER_ID
    assert request["selected_interpretation"] == "DOMAIN_FOUNDATION"
    assert request["domain_reference"] == "HR"
    assert request["provider_necessity_classification"] == "PROVIDER_REQUIRED"
    assert request["clarification_history"]
    assert request["provider_invoked"] is False
    assert request["worker_invoked"] is False
    assert request["authorization_created"] is False
    assert request["execution_requested"] is False
    assert request["dispatch_requested"] is False
    assert reconstructed["request_status"] == CLARIFIED_PROVIDER_PROPOSAL_REQUEST_READY
    assert reconstructed["replay_artifact_count"] == 4


def test_bridge_fails_closed_when_provider_mismatch(tmp_path) -> None:
    capture = _bridge_capture(tmp_path, provider_id=PROVIDER_ID, selected_provider_id="ANTHROPIC")

    assert capture["request_status"] == FAILED_CLOSED
    assert "provider mismatch" in capture["failure_reason"]
    assert capture["provider_invoked"] is False


def test_bridge_fails_closed_when_ppp_lineage_invalid(tmp_path) -> None:
    conversation = _conversation_capture(tmp_path)
    ppp = conversation["clarified_ppp_routing"]
    routed = dict(ppp["clarified_ppp_routed_intent_artifact"])
    routed["routing_evidence_hash"] = "sha256:not-real"
    routed.pop("artifact_hash")
    routed["artifact_hash"] = replay_hash(routed)
    capture = bridge_clarified_ppp_intent_to_provider_proposal_request(
        bridge_id="CLARIFIED-PROVIDER-BRIDGE-LINEAGE-000001",
        provider_id=PROVIDER_ID,
        clarified_ppp_routed_intent_artifact=routed,
        clarified_ppp_routing_evidence_artifact=ppp["clarified_ppp_routing_evidence_artifact"],
        clarified_ppp_routing_classification_artifact=ppp["clarified_ppp_routing_classification_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "lineage",
    )

    assert capture["request_status"] == FAILED_CLOSED
    assert "invalid PPP lineage" in capture["failure_reason"]


def test_bridge_fails_closed_on_replay_corruption(tmp_path) -> None:
    conversation = _conversation_capture(tmp_path)
    ppp = conversation["clarified_ppp_routing"]
    routed = dict(ppp["clarified_ppp_routed_intent_artifact"])
    contract = dict(routed["ppp_input_contract"])
    contract["intent_source_visible_to_ppp"] = True
    routed["ppp_input_contract"] = contract
    routed.pop("artifact_hash")
    routed["artifact_hash"] = replay_hash(routed)
    capture = bridge_clarified_ppp_intent_to_provider_proposal_request(
        bridge_id="CLARIFIED-PROVIDER-BRIDGE-CORRUPTION-000001",
        provider_id=PROVIDER_ID,
        clarified_ppp_routed_intent_artifact=routed,
        clarified_ppp_routing_evidence_artifact=ppp["clarified_ppp_routing_evidence_artifact"],
        clarified_ppp_routing_classification_artifact=ppp["clarified_ppp_routing_classification_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corruption",
    )

    assert capture["request_status"] == FAILED_CLOSED
    assert "replay corruption" in capture["failure_reason"]


def test_bridge_fails_closed_when_chain_continuity_fails(tmp_path) -> None:
    conversation = _conversation_capture(tmp_path)
    ppp = conversation["clarified_ppp_routing"]
    evidence = dict(ppp["clarified_ppp_routing_evidence_artifact"])
    evidence["canonical_chain_id"] = "DIFFERENT-CHAIN"
    evidence.pop("artifact_hash")
    evidence["artifact_hash"] = replay_hash(evidence)
    classification = dict(ppp["clarified_ppp_routing_classification_artifact"])
    classification["routing_evidence_hash"] = evidence["artifact_hash"]
    classification.pop("artifact_hash")
    classification["artifact_hash"] = replay_hash(classification)
    routed = dict(ppp["clarified_ppp_routed_intent_artifact"])
    routed["routing_evidence_hash"] = evidence["artifact_hash"]
    routed["routing_classification_hash"] = classification["artifact_hash"]
    routed.pop("artifact_hash")
    routed["artifact_hash"] = replay_hash(routed)
    capture = bridge_clarified_ppp_intent_to_provider_proposal_request(
        bridge_id="CLARIFIED-PROVIDER-BRIDGE-CHAIN-000001",
        provider_id=PROVIDER_ID,
        clarified_ppp_routed_intent_artifact=routed,
        clarified_ppp_routing_evidence_artifact=evidence,
        clarified_ppp_routing_classification_artifact=classification,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "chain",
    )

    assert capture["request_status"] == FAILED_CLOSED
    assert "chain continuity failure" in capture["failure_reason"]


def test_reconstruction_detects_corrupt_bridge_replay(tmp_path) -> None:
    _bridge_capture(tmp_path)
    path = tmp_path / "bridge" / "002_clarified_provider_proposal_request_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["provider_id"] = "CORRUPTED"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_clarified_intent_provider_proposal_bridge_replay(tmp_path / "bridge")


def test_bridge_has_no_provider_worker_or_execution_invocations() -> None:
    import aigol.runtime.clarified_intent_provider_proposal_bridge as runtime

    source = inspect.getsource(runtime)

    assert "produce_provider_development_proposal(" not in source
    assert "run_provider_attachment(" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source
