"""Tests for G3 Product 1 OCS advisory integration."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.acli_conversational_development_session import (
    record_conversational_development_turn,
    start_conversational_development_session,
)
from aigol.runtime.acli_development_session_lifecycle import create_acli_development_session
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.product1_decision_packet import create_product1_decision_packet
from aigol.runtime.product1_ocs_advisory import (
    DECISION_AUTHORITY,
    OCS_ADVISORY_ATTACHED,
    PRODUCT1_OCS_ADVISORY_ARTIFACT_V1,
    attach_product1_ocs_advisory,
    reconstruct_product1_ocs_advisory_replay,
)
from aigol.runtime.product1_workflow_foundation import (
    GOVERNANCE_PASSED,
    OPERATOR_REVIEW_RECORDED,
    WORKFLOW_READY_FOR_DECISION_PACKET,
    create_product1_workflow,
    record_product1_governance_checkpoint,
    record_product1_operator_review_checkpoint,
    transition_product1_workflow_state,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-29T00:00:00Z"
TURN_AT = "2026-06-29T00:01:00Z"
GOVERNANCE_AT = "2026-06-29T00:02:00Z"
REVIEW_AT = "2026-06-29T00:03:00Z"
TRANSITION_AT = "2026-06-29T00:04:00Z"
PACKET_AT = "2026-06-29T00:05:00Z"
ADVISORY_AT = "2026-06-29T00:06:00Z"


def _governance_checkpoints() -> dict:
    return {
        "semantic_authority_preserved": True,
        "governance_authority_preserved": True,
        "approval_boundary_preserved": True,
        "provider_boundary_preserved": True,
        "worker_boundary_preserved": True,
        "replay_boundary_preserved": True,
        "execution_boundary_preserved": True,
    }


def _lineage(name: str) -> list[dict]:
    return [
        {
            "replay_reference": f"runtime/g3/product1-ocs-advisory/{name}.json",
            "replay_hash": replay_hash({"source": name}),
        }
    ]


def _session(tmp_path) -> dict:
    return create_acli_development_session(
        session_id="ACLI-G3-SESSION-ADVISORY-000001",
        canonical_semantic_artifact_reference="CSA-SESSION-ADVISORY-000001",
        canonical_semantic_artifact_hash=replay_hash({"csa": "session-advisory"}),
        replay_lineage=_lineage("session"),
        governance_checkpoints=_governance_checkpoints(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "session",
    )["session_artifact"]


def _conversation_with_turn(tmp_path) -> dict:
    conversation = start_conversational_development_session(
        conversation_id="ACLI-CONVERSATION-ADVISORY-000001",
        session_artifact=_session(tmp_path),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "conversation",
    )["conversation_artifact"]
    return record_conversational_development_turn(
        conversation_artifact=conversation,
        turn_id="TURN-ADVISORY-000001",
        recorded_at=TURN_AT,
        replay_dir=tmp_path / "conversation",
        prompt_hash=replay_hash({"prompt": "attach advisory OCS evidence to decision packet"}),
        canonical_semantic_artifact_reference="CSA-TURN-ADVISORY-000001",
        canonical_semantic_artifact_hash=replay_hash({"csa": "turn-advisory"}),
        replay_lineage=_lineage("turn"),
        clarification_status="CLARIFICATION_RESOLVED",
        proposal_status="PROPOSAL_CANDIDATE_RECORDED",
        confirmation_status="CONFIRMATION_REQUIRED",
        continuation_status="NEW_CONVERSATION",
        proposal_reference="PRODUCT1-ADVISORY-PROPOSAL-000001",
        confirmation_request_reference="PRODUCT1-ADVISORY-CONFIRMATION-000001",
    )["conversation_artifact"]


def _workflow(tmp_path, replay_name: str = "workflow") -> dict:
    workflow = create_product1_workflow(
        workflow_id="PRODUCT1-WORKFLOW-ADVISORY-000001",
        conversation_artifact=_conversation_with_turn(tmp_path),
        originating_turn_id="TURN-ADVISORY-000001",
        rollback_reference="rollback:PRODUCT1-WORKFLOW-ADVISORY-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / replay_name,
    )["workflow_artifact"]
    workflow = record_product1_governance_checkpoint(
        workflow_artifact=workflow,
        checkpoint_id="PRODUCT1-ADVISORY-GOVERNANCE-000001",
        checkpoint_status=GOVERNANCE_PASSED,
        checkpoint_scope="AI_DECISION_VALIDATOR_ADVISORY",
        checkpoint_evidence_hash=replay_hash({"checkpoint": "advisory-governance"}),
        recorded_at=GOVERNANCE_AT,
        replay_dir=tmp_path / replay_name,
    )["workflow_artifact"]
    workflow = record_product1_operator_review_checkpoint(
        workflow_artifact=workflow,
        review_id="PRODUCT1-ADVISORY-REVIEW-000001",
        review_status=OPERATOR_REVIEW_RECORDED,
        review_evidence_hash=replay_hash({"review": "advisory-review"}),
        required_next_action="attach advisory OCS evidence",
        reviewed_at=REVIEW_AT,
        replay_dir=tmp_path / replay_name,
    )["workflow_artifact"]
    return transition_product1_workflow_state(
        workflow_artifact=workflow,
        workflow_status=WORKFLOW_READY_FOR_DECISION_PACKET,
        transition_reason_hash=replay_hash({"transition": "advisory-packet-ready"}),
        transitioned_at=TRANSITION_AT,
        replay_dir=tmp_path / replay_name,
    )["workflow_artifact"]


def _evidence() -> list[dict]:
    return [
        {
            "evidence_id": "EVIDENCE-ADVISORY-CSA-000001",
            "evidence_type": "CSA_LINEAGE",
            "evidence_reference": "CSA-TURN-ADVISORY-000001",
            "evidence_hash": replay_hash({"evidence": "advisory-csa"}),
            "evidence_role": "semantic source",
        }
    ]


def _assumptions() -> list[dict]:
    return [
        {
            "assumption_id": "ASSUMPTION-ADVISORY-000001",
            "statement": "OCS advisory evidence remains pre-runtime.",
            "source_reference": "OCS-COGNITION-ADVISORY-000001",
            "severity": "medium",
        }
    ]


def _risks() -> list[dict]:
    return [
        {
            "risk_id": "RISK-ADVISORY-000001",
            "statement": "Advisory confidence must not be interpreted as approval.",
            "source_reference": "governance-boundary",
            "severity": "high",
        }
    ]


def _uncertainties() -> list[dict]:
    return [
        {
            "uncertainty_id": "UNCERTAINTY-ADVISORY-000001",
            "statement": "Real provider execution is deferred to later workstreams.",
            "source_reference": "G3-03 phase 3 scope",
            "severity": "low",
        }
    ]


def _recommendation() -> dict:
    return {
        "recommendation_id": "RECOMMENDATION-ADVISORY-000001",
        "recommendation_status": "ADVISORY_REVIEW_REQUIRED",
        "summary": "Use OCS advisory evidence as non-authoritative decision support.",
        "recommended_next_action": "retain human and governance decision authority",
        "confidence": "deterministic",
    }


def _packet(tmp_path) -> dict:
    return create_product1_decision_packet(
        packet_id="PRODUCT1-DECISION-PACKET-ADVISORY-000001",
        workflow_artifact=_workflow(tmp_path),
        evidence_references=_evidence(),
        assumptions=_assumptions(),
        risks=_risks(),
        uncertainties=_uncertainties(),
        recommendation_summary=_recommendation(),
        created_at=PACKET_AT,
        replay_dir=tmp_path / "packet",
    )["decision_packet_artifact"]


def _provider_provenance() -> list[dict]:
    return [
        {
            "provider_provenance_id": "PROVIDER-PROVENANCE-ADVISORY-000001",
            "provider_id": "provider-deferred",
            "provider_reference": "PROVIDER-NOT-ACTIVATED-G3-03",
            "provider_response_hash": replay_hash({"provider": "not-invoked"}),
            "provider_role": "deferred provenance placeholder",
            "provider_invoked": False,
            "provider_authority": False,
            "advisory_only": True,
        }
    ]


def _confidence() -> dict:
    return {
        "confidence_id": "CONFIDENCE-ADVISORY-000001",
        "confidence_level": "medium",
        "confidence_score": "0.74",
        "confidence_rationale": "Deterministic OCS advisory evidence is complete but provider execution is deferred.",
        "confidence_source_reference": "OCS-COGNITION-ADVISORY-000001",
    }


def _advisory(tmp_path, packet: dict | None = None):
    return attach_product1_ocs_advisory(
        advisory_id="PRODUCT1-OCS-ADVISORY-000001",
        decision_packet_artifact=packet or _packet(tmp_path),
        ocs_cognition_reference="OCS-COGNITION-ADVISORY-000001",
        ocs_cognition_hash=replay_hash({"ocs": "advisory-cognition"}),
        provider_provenance=_provider_provenance(),
        confidence=_confidence(),
        assumptions=_assumptions(),
        risks=_risks(),
        uncertainties=_uncertainties(),
        created_at=ADVISORY_AT,
        replay_dir=tmp_path / "advisory",
    )


def test_attaches_ocs_advisory_to_decision_packet(tmp_path) -> None:
    capture = _advisory(tmp_path)
    artifact = capture["ocs_advisory_artifact"]

    assert artifact["artifact_type"] == PRODUCT1_OCS_ADVISORY_ARTIFACT_V1
    assert artifact["advisory_id"] == "PRODUCT1-OCS-ADVISORY-000001"
    assert artifact["advisory_status"] == OCS_ADVISORY_ATTACHED
    assert artifact["decision_packet_id"] == "PRODUCT1-DECISION-PACKET-ADVISORY-000001"
    assert artifact["canonical_semantic_artifact_reference"] == "CSA-TURN-ADVISORY-000001"
    assert artifact["ocs_cognition_reference"] == "OCS-COGNITION-ADVISORY-000001"
    assert artifact["provider_provenance_count"] == 1
    assert artifact["confidence"]["confidence_level"] == "medium"
    assert artifact["assumption_count"] == 1
    assert artifact["risk_count"] == 1
    assert artifact["uncertainty_count"] == 1
    assert artifact["decision_authority"] == DECISION_AUTHORITY
    assert artifact["provider_invoked"] is False
    assert artifact["worker_invoked"] is False
    assert artifact["approval_created"] is False
    assert artifact["execution_requested"] is False

    reconstructed = reconstruct_product1_ocs_advisory_replay(tmp_path / "advisory")
    assert reconstructed["advisory_id"] == "PRODUCT1-OCS-ADVISORY-000001"
    assert reconstructed["provider_provenance_count"] == 1
    assert reconstructed["decision_authority"] == DECISION_AUTHORITY
    assert reconstructed["replay_lineage_count"] == 8


def test_ocs_advisory_rejects_authoritative_provider_provenance(tmp_path) -> None:
    provenance = _provider_provenance()
    provenance[0] = {**provenance[0], "provider_authority": True}

    with pytest.raises(FailClosedRuntimeError, match="must not be authoritative"):
        attach_product1_ocs_advisory(
            advisory_id="PRODUCT1-OCS-ADVISORY-AUTHORITATIVE",
            decision_packet_artifact=_packet(tmp_path),
            ocs_cognition_reference="OCS-COGNITION-ADVISORY-000001",
            ocs_cognition_hash=replay_hash({"ocs": "advisory-cognition"}),
            provider_provenance=provenance,
            confidence=_confidence(),
            assumptions=_assumptions(),
            risks=_risks(),
            uncertainties=_uncertainties(),
            created_at=ADVISORY_AT,
            replay_dir=tmp_path / "authoritative_advisory",
        )


def test_ocs_advisory_requires_created_decision_packet(tmp_path) -> None:
    packet = _packet(tmp_path)
    packet["packet_status"] = "FAILED_CLOSED"
    packet.pop("artifact_hash")
    packet["artifact_hash"] = replay_hash(packet)

    with pytest.raises(FailClosedRuntimeError, match="decision packet is not created"):
        _advisory(tmp_path, packet=packet)


def test_ocs_advisory_replay_tamper_fails_closed(tmp_path) -> None:
    _advisory(tmp_path)
    path = tmp_path / "advisory" / "000_product1_ocs_advisory_attached.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["worker_invoked"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_product1_ocs_advisory_replay(tmp_path / "advisory")


def test_ocs_advisory_runtime_has_no_authority_or_execution_surfaces() -> None:
    import aigol.runtime.product1_ocs_advisory as runtime

    source = inspect.getsource(runtime)

    assert "invoke_worker(" not in source
    assert "execute_worker(" not in source
    assert "invoke_live_external_llm_provider(" not in source
    assert "subprocess." not in source
    assert "os.system" not in source
    assert "deploy(" not in source
    assert "write_text(" not in source
    assert '"provider_invoked": True' not in source
    assert '"worker_invoked": True' not in source
    assert '"approval_created": True' not in source
    assert '"execution_requested": True' not in source
