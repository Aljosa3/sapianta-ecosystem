"""Tests for G3 Product 1 audit packet assembly."""

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
from aigol.runtime.product1_audit_packet import (
    AUDIT_PACKET_ASSEMBLED,
    AUDIT_PACKET_AUTHORITY,
    PRODUCT1_AUDIT_PACKET_ARTIFACT_V1,
    assemble_product1_audit_packet,
    reconstruct_product1_audit_packet_replay,
)
from aigol.runtime.product1_decision_packet import create_product1_decision_packet
from aigol.runtime.product1_ocs_advisory import attach_product1_ocs_advisory
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
AUDIT_AT = "2026-06-29T00:07:00Z"


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
            "replay_reference": f"runtime/g3/product1-audit-packet/{name}.json",
            "replay_hash": replay_hash({"source": name}),
        }
    ]


def _session(tmp_path) -> dict:
    return create_acli_development_session(
        session_id="ACLI-G3-SESSION-AUDIT-000001",
        canonical_semantic_artifact_reference="CSA-SESSION-AUDIT-000001",
        canonical_semantic_artifact_hash=replay_hash({"csa": "session-audit"}),
        replay_lineage=_lineage("session"),
        governance_checkpoints=_governance_checkpoints(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "session",
    )["session_artifact"]


def _conversation_with_turn(tmp_path) -> dict:
    conversation = start_conversational_development_session(
        conversation_id="ACLI-CONVERSATION-AUDIT-000001",
        session_artifact=_session(tmp_path),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "conversation",
    )["conversation_artifact"]
    return record_conversational_development_turn(
        conversation_artifact=conversation,
        turn_id="TURN-AUDIT-000001",
        recorded_at=TURN_AT,
        replay_dir=tmp_path / "conversation",
        prompt_hash=replay_hash({"prompt": "assemble Product 1 audit packet"}),
        canonical_semantic_artifact_reference="CSA-TURN-AUDIT-000001",
        canonical_semantic_artifact_hash=replay_hash({"csa": "turn-audit"}),
        replay_lineage=_lineage("turn"),
        clarification_status="CLARIFICATION_RESOLVED",
        proposal_status="PROPOSAL_CANDIDATE_RECORDED",
        confirmation_status="CONFIRMATION_REQUIRED",
        continuation_status="NEW_CONVERSATION",
        proposal_reference="PRODUCT1-AUDIT-PROPOSAL-000001",
        confirmation_request_reference="PRODUCT1-AUDIT-CONFIRMATION-000001",
    )["conversation_artifact"]


def _workflow(tmp_path, replay_name: str = "workflow") -> dict:
    workflow = create_product1_workflow(
        workflow_id="PRODUCT1-WORKFLOW-AUDIT-000001",
        conversation_artifact=_conversation_with_turn(tmp_path),
        originating_turn_id="TURN-AUDIT-000001",
        rollback_reference="rollback:PRODUCT1-WORKFLOW-AUDIT-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / replay_name,
    )["workflow_artifact"]
    workflow = record_product1_governance_checkpoint(
        workflow_artifact=workflow,
        checkpoint_id="PRODUCT1-AUDIT-GOVERNANCE-000001",
        checkpoint_status=GOVERNANCE_PASSED,
        checkpoint_scope="AI_DECISION_VALIDATOR_AUDIT",
        checkpoint_evidence_hash=replay_hash({"checkpoint": "audit-governance"}),
        recorded_at=GOVERNANCE_AT,
        replay_dir=tmp_path / replay_name,
    )["workflow_artifact"]
    workflow = record_product1_operator_review_checkpoint(
        workflow_artifact=workflow,
        review_id="PRODUCT1-AUDIT-REVIEW-000001",
        review_status=OPERATOR_REVIEW_RECORDED,
        review_evidence_hash=replay_hash({"review": "audit-review"}),
        required_next_action="assemble deterministic audit packet",
        reviewed_at=REVIEW_AT,
        replay_dir=tmp_path / replay_name,
    )["workflow_artifact"]
    return transition_product1_workflow_state(
        workflow_artifact=workflow,
        workflow_status=WORKFLOW_READY_FOR_DECISION_PACKET,
        transition_reason_hash=replay_hash({"transition": "audit-packet-ready"}),
        transitioned_at=TRANSITION_AT,
        replay_dir=tmp_path / replay_name,
    )["workflow_artifact"]


def _evidence() -> list[dict]:
    return [
        {
            "evidence_id": "EVIDENCE-AUDIT-CSA-000001",
            "evidence_type": "CSA_LINEAGE",
            "evidence_reference": "CSA-TURN-AUDIT-000001",
            "evidence_hash": replay_hash({"evidence": "audit-csa"}),
            "evidence_role": "semantic source",
        }
    ]


def _named(prefix: str, statement: str) -> list[dict]:
    return [
        {
            f"{prefix}_id": f"{prefix.upper()}-AUDIT-000001",
            "statement": statement,
            "source_reference": "audit-source",
            "severity": "medium",
        }
    ]


def _recommendation() -> dict:
    return {
        "recommendation_id": "RECOMMENDATION-AUDIT-000001",
        "recommendation_status": "AUDIT_REVIEW_REQUIRED",
        "summary": "Assemble read-only audit evidence for human review.",
        "recommended_next_action": "review audit packet before downstream authorization",
        "confidence": "deterministic",
    }


def _packet(tmp_path) -> dict:
    return create_product1_decision_packet(
        packet_id="PRODUCT1-DECISION-PACKET-AUDIT-000001",
        workflow_artifact=_workflow(tmp_path),
        evidence_references=_evidence(),
        assumptions=_named("assumption", "Audit evidence remains pre-runtime."),
        risks=_named("risk", "Audit packet must not be interpreted as approval."),
        uncertainties=_named("uncertainty", "Provider execution remains deferred."),
        recommendation_summary=_recommendation(),
        created_at=PACKET_AT,
        replay_dir=tmp_path / "packet",
    )["decision_packet_artifact"]


def _advisory(tmp_path, packet: dict | None = None) -> dict:
    return attach_product1_ocs_advisory(
        advisory_id="PRODUCT1-OCS-ADVISORY-AUDIT-000001",
        decision_packet_artifact=packet or _packet(tmp_path),
        ocs_cognition_reference="OCS-COGNITION-AUDIT-000001",
        ocs_cognition_hash=replay_hash({"ocs": "audit-cognition"}),
        provider_provenance=[
            {
                "provider_provenance_id": "PROVIDER-PROVENANCE-AUDIT-000001",
                "provider_id": "provider-deferred",
                "provider_reference": "PROVIDER-NOT-ACTIVATED-G3-03",
                "provider_response_hash": replay_hash({"provider": "not-invoked"}),
                "provider_role": "deferred provenance placeholder",
                "provider_invoked": False,
                "provider_authority": False,
                "advisory_only": True,
            }
        ],
        confidence={
            "confidence_id": "CONFIDENCE-AUDIT-000001",
            "confidence_level": "medium",
            "confidence_score": "0.76",
            "confidence_rationale": "Advisory evidence is deterministic and non-authoritative.",
            "confidence_source_reference": "OCS-COGNITION-AUDIT-000001",
        },
        assumptions=_named("assumption", "OCS advisory remains read-only."),
        risks=_named("risk", "Advisory evidence must not authorize execution."),
        uncertainties=_named("uncertainty", "Real provider activation is deferred."),
        created_at=ADVISORY_AT,
        replay_dir=tmp_path / "advisory",
    )["ocs_advisory_artifact"]


def _governance_evidence() -> list[dict]:
    return [
        {
            "governance_evidence_id": "GOVERNANCE-EVIDENCE-AUDIT-000001",
            "governance_scope": "PRODUCT1_AUDIT_PACKET",
            "governance_status": "GOVERNANCE_PASSED",
            "governance_reference": "PRODUCT1-AUDIT-GOVERNANCE-000001",
            "governance_hash": replay_hash({"governance": "audit"}),
        }
    ]


def _replay_evidence() -> list[dict]:
    return [
        {
            "replay_evidence_id": "REPLAY-EVIDENCE-PACKET-000001",
            "replay_reference": "packet/000_product1_decision_packet_created.json",
            "replay_hash": replay_hash({"replay": "packet"}),
            "replay_role": "decision packet replay",
        },
        {
            "replay_evidence_id": "REPLAY-EVIDENCE-ADVISORY-000001",
            "replay_reference": "advisory/000_product1_ocs_advisory_attached.json",
            "replay_hash": replay_hash({"replay": "advisory"}),
            "replay_role": "OCS advisory replay",
        },
    ]


def _certification_evidence() -> list[dict]:
    return [
        {
            "certification_evidence_id": "CERTIFICATION-EVIDENCE-AUDIT-000001",
            "certification_scope": "G3_03_PHASE_4_AUDIT_PACKET",
            "certification_status": "READY_FOR_REVIEW",
            "certification_reference": "G3_03_IMPLEMENTATION_PHASE_4_AUDIT_PACKET_ASSEMBLY_V1",
            "certification_hash": replay_hash({"certification": "audit"}),
        }
    ]


def _audit_summary() -> dict:
    return {
        "audit_summary_id": "AUDIT-SUMMARY-000001",
        "summary": "Product 1 evidence is assembled for read-only audit review.",
        "readiness_status": "AUDIT_PACKET_ASSEMBLED",
        "required_next_action": "perform human and governance review",
    }


def _audit_packet(tmp_path, packet: dict | None = None, advisory: dict | None = None):
    packet_artifact = packet or _packet(tmp_path)
    advisory_artifact = advisory or _advisory(tmp_path, packet_artifact)
    return assemble_product1_audit_packet(
        audit_packet_id="PRODUCT1-AUDIT-PACKET-000001",
        decision_packet_artifact=packet_artifact,
        ocs_advisory_artifact=advisory_artifact,
        governance_evidence=_governance_evidence(),
        replay_evidence=_replay_evidence(),
        certification_evidence=_certification_evidence(),
        audit_summary=_audit_summary(),
        assembled_at=AUDIT_AT,
        replay_dir=tmp_path / "audit",
    )


def test_assembles_product1_audit_packet(tmp_path) -> None:
    capture = _audit_packet(tmp_path)
    artifact = capture["audit_packet_artifact"]

    assert artifact["artifact_type"] == PRODUCT1_AUDIT_PACKET_ARTIFACT_V1
    assert artifact["audit_packet_id"] == "PRODUCT1-AUDIT-PACKET-000001"
    assert artifact["audit_packet_status"] == AUDIT_PACKET_ASSEMBLED
    assert artifact["workflow_id"] == "PRODUCT1-WORKFLOW-AUDIT-000001"
    assert artifact["decision_packet_id"] == "PRODUCT1-DECISION-PACKET-AUDIT-000001"
    assert artifact["ocs_advisory_id"] == "PRODUCT1-OCS-ADVISORY-AUDIT-000001"
    assert artifact["canonical_semantic_artifact_reference"] == "CSA-TURN-AUDIT-000001"
    assert artifact["governance_evidence_count"] == 1
    assert artifact["replay_evidence_count"] == 2
    assert artifact["certification_evidence_count"] == 1
    assert artifact["audit_packet_authority"] == AUDIT_PACKET_AUTHORITY
    assert artifact["read_only"] is True
    assert artifact["non_authoritative"] is True
    assert artifact["provider_invoked"] is False
    assert artifact["worker_invoked"] is False
    assert artifact["approval_created"] is False
    assert artifact["execution_requested"] is False

    reconstructed = reconstruct_product1_audit_packet_replay(tmp_path / "audit")
    assert reconstructed["audit_packet_id"] == "PRODUCT1-AUDIT-PACKET-000001"
    assert reconstructed["governance_evidence_count"] == 1
    assert reconstructed["replay_evidence_count"] == 2
    assert reconstructed["certification_evidence_count"] == 1
    assert reconstructed["replay_lineage_count"] == 14


def test_audit_packet_rejects_mismatched_advisory(tmp_path) -> None:
    packet = _packet(tmp_path)
    advisory = _advisory(tmp_path, packet)
    advisory["decision_packet_id"] = "DIFFERENT-PACKET"
    advisory.pop("artifact_hash")
    advisory["artifact_hash"] = replay_hash(advisory)

    with pytest.raises(FailClosedRuntimeError, match="advisory does not match decision packet"):
        _audit_packet(tmp_path, packet=packet, advisory=advisory)


def test_audit_packet_rejects_duplicate_replay_evidence_id(tmp_path) -> None:
    packet = _packet(tmp_path)
    advisory = _advisory(tmp_path, packet)
    replay_evidence = _replay_evidence()
    replay_evidence[1] = {**replay_evidence[1], "replay_evidence_id": replay_evidence[0]["replay_evidence_id"]}

    with pytest.raises(FailClosedRuntimeError, match="duplicate replay evidence id"):
        assemble_product1_audit_packet(
            audit_packet_id="PRODUCT1-AUDIT-PACKET-DUPLICATE",
            decision_packet_artifact=packet,
            ocs_advisory_artifact=advisory,
            governance_evidence=_governance_evidence(),
            replay_evidence=replay_evidence,
            certification_evidence=_certification_evidence(),
            audit_summary=_audit_summary(),
            assembled_at=AUDIT_AT,
            replay_dir=tmp_path / "duplicate_audit",
        )


def test_audit_packet_replay_tamper_fails_closed(tmp_path) -> None:
    _audit_packet(tmp_path)
    path = tmp_path / "audit" / "000_product1_audit_packet_assembled.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["repository_mutated"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_product1_audit_packet_replay(tmp_path / "audit")


def test_audit_packet_runtime_has_no_authority_or_execution_surfaces() -> None:
    import aigol.runtime.product1_audit_packet as runtime

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
