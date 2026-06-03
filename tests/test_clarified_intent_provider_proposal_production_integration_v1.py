"""Tests for AIGOL_CLARIFIED_INTENT_PROVIDER_PROPOSAL_PRODUCTION_INTEGRATION_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.clarified_intent_conversation_routing_integration import (
    run_clarified_intent_conversation_routing_integration,
)
from aigol.runtime.clarified_intent_provider_proposal_bridge import (
    bridge_clarified_ppp_intent_to_provider_proposal_request,
)
from aigol.runtime.clarified_intent_provider_proposal_production_integration import (
    CLARIFIED_PROVIDER_PROPOSAL_PRODUCTION_ARTIFACT_V1,
    CLARIFIED_PROVIDER_PROPOSAL_PRODUCTION_CLASSIFICATION_V1,
    CLARIFIED_PROVIDER_PROPOSAL_PRODUCTION_EVIDENCE_V1,
    CLARIFIED_PROVIDER_PROPOSAL_PRODUCTION_READY,
    FAILED_CLOSED,
    integrate_clarified_provider_request_with_proposal_production,
    reconstruct_clarified_intent_provider_proposal_production_integration_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_proposal_production_runtime import PROVIDER_REQUEST_PACKET_V1
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-03T23:59:30+00:00"
CHAIN_ID = "CHAIN-CLARIFIED-PRODUCTION-INTEGRATION-000001"
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


def _response() -> dict:
    return {
        "selected_interpretation": "DOMAIN_FOUNDATION",
        "selected_domain_id": "HR",
        "selected_worker_family_id": "EMPLOYEE_MANAGEMENT",
        "selected_milestone_type": "DOMAIN_FOUNDATION",
        "selected_output_scope": "DOMAIN_FOUNDATION",
        "human_response_text": "Create a new employee-management domain.",
        "resume_stage": "COGNITION",
    }


def _bridge_capture(tmp_path):
    conversation = run_clarified_intent_conversation_routing_integration(
        prompt_id="PROMPT-CLARIFIED-PRODUCTION-INTEGRATION-000001",
        human_prompt="Create a workstation.",
        ambiguity_categories=[
            "DOMAIN_AMBIGUITY",
            "WORKER_AMBIGUITY",
            "CAPABILITY_AMBIGUITY",
            "INTENT_AMBIGUITY",
            "RESOURCE_AMBIGUITY",
        ],
        candidate_interpretations=_candidates(),
        human_response=_response(),
        canonical_chain_id=CHAIN_ID,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "conversation",
    )
    ppp = conversation["clarified_ppp_routing"]
    return bridge_clarified_ppp_intent_to_provider_proposal_request(
        bridge_id="CLARIFIED-PRODUCTION-BRIDGE-000001",
        provider_id=PROVIDER_ID,
        clarified_ppp_routed_intent_artifact=ppp["clarified_ppp_routed_intent_artifact"],
        clarified_ppp_routing_evidence_artifact=ppp["clarified_ppp_routing_evidence_artifact"],
        clarified_ppp_routing_classification_artifact=ppp["clarified_ppp_routing_classification_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "bridge",
    )


def _production_capture(tmp_path, *, bridge: dict | None = None, provider_id: str = PROVIDER_ID, selected_provider_id: str | None = None):
    bridge = bridge or _bridge_capture(tmp_path)
    return integrate_clarified_provider_request_with_proposal_production(
        integration_id="CLARIFIED-PRODUCTION-INTEGRATION-000001",
        provider_id=provider_id,
        selected_provider_id=selected_provider_id,
        clarified_provider_proposal_request_artifact=bridge["clarified_provider_proposal_request_artifact"],
        clarified_provider_proposal_bridge_evidence_artifact=bridge[
            "clarified_provider_proposal_bridge_evidence_artifact"
        ],
        clarified_provider_proposal_bridge_classification_artifact=bridge[
            "clarified_provider_proposal_bridge_classification_artifact"
        ],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "production_integration",
    )


def test_integrates_clarified_provider_request_with_proposal_production(tmp_path) -> None:
    capture = _production_capture(tmp_path)
    reconstructed = reconstruct_clarified_intent_provider_proposal_production_integration_replay(
        tmp_path / "production_integration"
    )
    production = capture["clarified_provider_proposal_production_artifact"]

    assert capture["production_status"] == CLARIFIED_PROVIDER_PROPOSAL_PRODUCTION_READY
    assert capture["clarified_provider_proposal_production_evidence_artifact"]["artifact_type"] == (
        CLARIFIED_PROVIDER_PROPOSAL_PRODUCTION_EVIDENCE_V1
    )
    assert capture["clarified_provider_proposal_production_classification_artifact"]["artifact_type"] == (
        CLARIFIED_PROVIDER_PROPOSAL_PRODUCTION_CLASSIFICATION_V1
    )
    assert production["artifact_type"] == CLARIFIED_PROVIDER_PROPOSAL_PRODUCTION_ARTIFACT_V1
    assert production["provider_request_packet_type"] == PROVIDER_REQUEST_PACKET_V1
    assert production["provider_id"] == PROVIDER_ID
    assert production["selected_interpretation"] == "DOMAIN_FOUNDATION"
    assert production["domain_reference"] == "HR"
    assert production["proposal_validation_status"] == "AWAITING_PROVIDER_RESPONSE"
    assert production["approval_evidence_status"] == "AWAITING_VALIDATED_PROPOSAL"
    assert production["handoff_preparation_status"] == "AWAITING_VALIDATED_PROPOSAL"
    assert production["provider_invoked"] is False
    assert production["worker_invoked"] is False
    assert production["authorization_created"] is False
    assert production["execution_requested"] is False
    assert production["dispatch_requested"] is False
    assert reconstructed["production_status"] == CLARIFIED_PROVIDER_PROPOSAL_PRODUCTION_READY
    assert reconstructed["replay_artifact_count"] == 4


def test_production_integration_fails_closed_when_provider_mismatch(tmp_path) -> None:
    capture = _production_capture(tmp_path, provider_id=PROVIDER_ID, selected_provider_id="ANTHROPIC")

    assert capture["production_status"] == FAILED_CLOSED
    assert "provider mismatch" in capture["failure_reason"]


def test_production_integration_fails_closed_when_provider_lineage_invalid(tmp_path) -> None:
    bridge = _bridge_capture(tmp_path)
    request = dict(bridge["clarified_provider_proposal_request_artifact"])
    request["bridge_evidence_hash"] = "sha256:not-real"
    request.pop("artifact_hash")
    request["artifact_hash"] = replay_hash(request)
    capture = integrate_clarified_provider_request_with_proposal_production(
        integration_id="CLARIFIED-PRODUCTION-INTEGRATION-LINEAGE-000001",
        provider_id=PROVIDER_ID,
        clarified_provider_proposal_request_artifact=request,
        clarified_provider_proposal_bridge_evidence_artifact=bridge[
            "clarified_provider_proposal_bridge_evidence_artifact"
        ],
        clarified_provider_proposal_bridge_classification_artifact=bridge[
            "clarified_provider_proposal_bridge_classification_artifact"
        ],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "lineage",
    )

    assert capture["production_status"] == FAILED_CLOSED
    assert "invalid provider lineage" in capture["failure_reason"]


def test_production_integration_fails_closed_on_replay_corruption(tmp_path) -> None:
    bridge = _bridge_capture(tmp_path)
    request = dict(bridge["clarified_provider_proposal_request_artifact"])
    contract = dict(request["ppp_input_contract"])
    contract["intent_source_visible_to_ppp"] = True
    request["ppp_input_contract"] = contract
    request.pop("artifact_hash")
    request["artifact_hash"] = replay_hash(request)
    capture = integrate_clarified_provider_request_with_proposal_production(
        integration_id="CLARIFIED-PRODUCTION-INTEGRATION-CORRUPTION-000001",
        provider_id=PROVIDER_ID,
        clarified_provider_proposal_request_artifact=request,
        clarified_provider_proposal_bridge_evidence_artifact=bridge[
            "clarified_provider_proposal_bridge_evidence_artifact"
        ],
        clarified_provider_proposal_bridge_classification_artifact=bridge[
            "clarified_provider_proposal_bridge_classification_artifact"
        ],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corruption",
    )

    assert capture["production_status"] == FAILED_CLOSED
    assert "replay corruption" in capture["failure_reason"]


def test_production_integration_fails_closed_when_chain_continuity_fails(tmp_path) -> None:
    bridge = _bridge_capture(tmp_path)
    evidence = dict(bridge["clarified_provider_proposal_bridge_evidence_artifact"])
    evidence["canonical_chain_id"] = "DIFFERENT-CHAIN"
    evidence.pop("artifact_hash")
    evidence["artifact_hash"] = replay_hash(evidence)
    classification = dict(bridge["clarified_provider_proposal_bridge_classification_artifact"])
    classification["bridge_evidence_hash"] = evidence["artifact_hash"]
    classification.pop("artifact_hash")
    classification["artifact_hash"] = replay_hash(classification)
    request = dict(bridge["clarified_provider_proposal_request_artifact"])
    request["bridge_evidence_hash"] = evidence["artifact_hash"]
    request["bridge_classification_hash"] = classification["artifact_hash"]
    request.pop("artifact_hash")
    request["artifact_hash"] = replay_hash(request)
    capture = integrate_clarified_provider_request_with_proposal_production(
        integration_id="CLARIFIED-PRODUCTION-INTEGRATION-CHAIN-000001",
        provider_id=PROVIDER_ID,
        clarified_provider_proposal_request_artifact=request,
        clarified_provider_proposal_bridge_evidence_artifact=evidence,
        clarified_provider_proposal_bridge_classification_artifact=classification,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "chain",
    )

    assert capture["production_status"] == FAILED_CLOSED
    assert "chain continuity failure" in capture["failure_reason"]


def test_reconstruction_detects_corrupt_production_integration_replay(tmp_path) -> None:
    _production_capture(tmp_path)
    path = (
        tmp_path
        / "production_integration"
        / "002_clarified_provider_proposal_production_recorded.json"
    )
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["provider_id"] = "CORRUPTED"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_clarified_intent_provider_proposal_production_integration_replay(
            tmp_path / "production_integration"
        )


def test_production_integration_has_no_authorization_dispatch_execution_or_worker_invocations() -> None:
    import aigol.runtime.clarified_intent_provider_proposal_production_integration as runtime

    source = inspect.getsource(runtime)

    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source
    assert "authorization_created = True" not in source
