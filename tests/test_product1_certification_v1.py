"""Tests for G3 Product 1 runtime certification."""

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
from aigol.runtime.product1_audit_packet import assemble_product1_audit_packet
from aigol.runtime.product1_certification import (
    CERTIFICATION_RECOMMENDATION,
    PRODUCT1_CERTIFICATION_ARTIFACT_V1,
    PRODUCT1_CERTIFIED,
    certify_product1_runtime,
    reconstruct_product1_certification_replay,
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
CERTIFIED_AT = "2026-06-29T00:08:00Z"


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
            "replay_reference": f"runtime/g3/product1-certification/{name}.json",
            "replay_hash": replay_hash({"source": name}),
        }
    ]


def _named(prefix: str, statement: str) -> list[dict]:
    return [
        {
            f"{prefix}_id": f"{prefix.upper()}-CERTIFICATION-000001",
            "statement": statement,
            "source_reference": "certification-source",
            "severity": "medium",
        }
    ]


def _workflow(tmp_path) -> dict:
    session = create_acli_development_session(
        session_id="ACLI-G3-SESSION-CERTIFICATION-000001",
        canonical_semantic_artifact_reference="CSA-SESSION-CERTIFICATION-000001",
        canonical_semantic_artifact_hash=replay_hash({"csa": "session-certification"}),
        replay_lineage=_lineage("session"),
        governance_checkpoints=_governance_checkpoints(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "session",
    )["session_artifact"]
    conversation = start_conversational_development_session(
        conversation_id="ACLI-CONVERSATION-CERTIFICATION-000001",
        session_artifact=session,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "conversation",
    )["conversation_artifact"]
    conversation = record_conversational_development_turn(
        conversation_artifact=conversation,
        turn_id="TURN-CERTIFICATION-000001",
        recorded_at=TURN_AT,
        replay_dir=tmp_path / "conversation",
        prompt_hash=replay_hash({"prompt": "certify Product 1 runtime"}),
        canonical_semantic_artifact_reference="CSA-TURN-CERTIFICATION-000001",
        canonical_semantic_artifact_hash=replay_hash({"csa": "turn-certification"}),
        replay_lineage=_lineage("turn"),
        clarification_status="CLARIFICATION_RESOLVED",
        proposal_status="PROPOSAL_CANDIDATE_RECORDED",
        confirmation_status="CONFIRMATION_REQUIRED",
        continuation_status="NEW_CONVERSATION",
        proposal_reference="PRODUCT1-CERTIFICATION-PROPOSAL-000001",
        confirmation_request_reference="PRODUCT1-CERTIFICATION-CONFIRMATION-000001",
    )["conversation_artifact"]
    workflow = create_product1_workflow(
        workflow_id="PRODUCT1-WORKFLOW-CERTIFICATION-000001",
        conversation_artifact=conversation,
        originating_turn_id="TURN-CERTIFICATION-000001",
        rollback_reference="rollback:PRODUCT1-WORKFLOW-CERTIFICATION-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "workflow",
    )["workflow_artifact"]
    workflow = record_product1_governance_checkpoint(
        workflow_artifact=workflow,
        checkpoint_id="PRODUCT1-CERTIFICATION-GOVERNANCE-000001",
        checkpoint_status=GOVERNANCE_PASSED,
        checkpoint_scope="AI_DECISION_VALIDATOR_CERTIFICATION",
        checkpoint_evidence_hash=replay_hash({"checkpoint": "certification-governance"}),
        recorded_at=GOVERNANCE_AT,
        replay_dir=tmp_path / "workflow",
    )["workflow_artifact"]
    workflow = record_product1_operator_review_checkpoint(
        workflow_artifact=workflow,
        review_id="PRODUCT1-CERTIFICATION-REVIEW-000001",
        review_status=OPERATOR_REVIEW_RECORDED,
        review_evidence_hash=replay_hash({"review": "certification-review"}),
        required_next_action="certify Product 1 runtime",
        reviewed_at=REVIEW_AT,
        replay_dir=tmp_path / "workflow",
    )["workflow_artifact"]
    return transition_product1_workflow_state(
        workflow_artifact=workflow,
        workflow_status=WORKFLOW_READY_FOR_DECISION_PACKET,
        transition_reason_hash=replay_hash({"transition": "certification-ready"}),
        transitioned_at=TRANSITION_AT,
        replay_dir=tmp_path / "workflow",
    )["workflow_artifact"]


def _packet(tmp_path) -> dict:
    return create_product1_decision_packet(
        packet_id="PRODUCT1-DECISION-PACKET-CERTIFICATION-000001",
        workflow_artifact=_workflow(tmp_path),
        evidence_references=[
            {
                "evidence_id": "EVIDENCE-CERTIFICATION-CSA-000001",
                "evidence_type": "CSA_LINEAGE",
                "evidence_reference": "CSA-TURN-CERTIFICATION-000001",
                "evidence_hash": replay_hash({"evidence": "certification-csa"}),
                "evidence_role": "semantic source",
            }
        ],
        assumptions=_named("assumption", "Certification remains pre-execution."),
        risks=_named("risk", "Certification must not authorize execution."),
        uncertainties=_named("uncertainty", "Real provider activation is deferred."),
        recommendation_summary={
            "recommendation_id": "RECOMMENDATION-CERTIFICATION-000001",
            "recommendation_status": "CERTIFICATION_REVIEW_REQUIRED",
            "summary": "Product 1 evidence is ready for runtime certification.",
            "recommended_next_action": "record certification evidence",
            "confidence": "deterministic",
        },
        created_at=PACKET_AT,
        replay_dir=tmp_path / "packet",
    )["decision_packet_artifact"]


def _advisory(tmp_path, packet: dict) -> dict:
    return attach_product1_ocs_advisory(
        advisory_id="PRODUCT1-OCS-ADVISORY-CERTIFICATION-000001",
        decision_packet_artifact=packet,
        ocs_cognition_reference="OCS-COGNITION-CERTIFICATION-000001",
        ocs_cognition_hash=replay_hash({"ocs": "certification-cognition"}),
        provider_provenance=[
            {
                "provider_provenance_id": "PROVIDER-PROVENANCE-CERTIFICATION-000001",
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
            "confidence_id": "CONFIDENCE-CERTIFICATION-000001",
            "confidence_level": "medium",
            "confidence_score": "0.78",
            "confidence_rationale": "Certification evidence is deterministic and non-authoritative.",
            "confidence_source_reference": "OCS-COGNITION-CERTIFICATION-000001",
        },
        assumptions=_named("assumption", "OCS advisory remains read-only."),
        risks=_named("risk", "Advisory evidence must not authorize execution."),
        uncertainties=_named("uncertainty", "Provider activation remains later work."),
        created_at=ADVISORY_AT,
        replay_dir=tmp_path / "advisory",
    )["ocs_advisory_artifact"]


def _audit_packet(tmp_path) -> dict:
    packet = _packet(tmp_path)
    advisory = _advisory(tmp_path, packet)
    return assemble_product1_audit_packet(
        audit_packet_id="PRODUCT1-AUDIT-PACKET-CERTIFICATION-000001",
        decision_packet_artifact=packet,
        ocs_advisory_artifact=advisory,
        governance_evidence=[
            {
                "governance_evidence_id": "GOVERNANCE-EVIDENCE-CERTIFICATION-000001",
                "governance_scope": "PRODUCT1_CERTIFICATION",
                "governance_status": "GOVERNANCE_PASSED",
                "governance_reference": "PRODUCT1-CERTIFICATION-GOVERNANCE-000001",
                "governance_hash": replay_hash({"governance": "certification"}),
            }
        ],
        replay_evidence=[
            {
                "replay_evidence_id": "REPLAY-EVIDENCE-CERTIFICATION-PACKET-000001",
                "replay_reference": "packet/000_product1_decision_packet_created.json",
                "replay_hash": replay_hash({"replay": "packet"}),
                "replay_role": "decision packet replay",
            },
            {
                "replay_evidence_id": "REPLAY-EVIDENCE-CERTIFICATION-ADVISORY-000001",
                "replay_reference": "advisory/000_product1_ocs_advisory_attached.json",
                "replay_hash": replay_hash({"replay": "advisory"}),
                "replay_role": "OCS advisory replay",
            },
        ],
        certification_evidence=[
            {
                "certification_evidence_id": "CERTIFICATION-EVIDENCE-CERTIFICATION-000001",
                "certification_scope": "G3_03_PHASE_5_PRODUCT_1_CERTIFICATION",
                "certification_status": "READY_FOR_CERTIFICATION",
                "certification_reference": "G3_03_IMPLEMENTATION_PHASE_5_PRODUCT_1_CERTIFICATION_V1",
                "certification_hash": replay_hash({"certification": "phase-5"}),
            }
        ],
        audit_summary={
            "audit_summary_id": "AUDIT-SUMMARY-CERTIFICATION-000001",
            "summary": "Product 1 audit evidence is ready for certification review.",
            "readiness_status": "READY_FOR_CERTIFICATION",
            "required_next_action": "record Product 1 certification",
        },
        assembled_at=AUDIT_AT,
        replay_dir=tmp_path / "audit",
    )["audit_packet_artifact"]


def _limitations() -> list[dict]:
    return [
        {
            "limitation_id": "LIMITATION-PROVIDER-ACTIVATION-000001",
            "limitation_scope": "G3_PROVIDER_ACTIVATION",
            "statement": "Real provider execution remains deferred to a later Generation 3 workstream.",
            "owner": "Generation 3 provider activation",
            "planned_resolution": "G3-04 real provider activation roadmap",
        }
    ]


def _certification(tmp_path, audit_packet: dict | None = None):
    return certify_product1_runtime(
        certification_id="PRODUCT1-CERTIFICATION-000001",
        audit_packet_artifact=audit_packet or _audit_packet(tmp_path),
        remaining_limitations=_limitations(),
        certified_at=CERTIFIED_AT,
        replay_dir=tmp_path / "certification",
    )


def test_certifies_product1_runtime_from_audit_packet(tmp_path) -> None:
    capture = _certification(tmp_path)
    artifact = capture["certification_artifact"]

    assert artifact["artifact_type"] == PRODUCT1_CERTIFICATION_ARTIFACT_V1
    assert artifact["certification_id"] == "PRODUCT1-CERTIFICATION-000001"
    assert artifact["certification_status"] == PRODUCT1_CERTIFIED
    assert artifact["certification_recommendation"] == CERTIFICATION_RECOMMENDATION
    assert artifact["audit_packet_id"] == "PRODUCT1-AUDIT-PACKET-CERTIFICATION-000001"
    assert artifact["workflow_id"] == "PRODUCT1-WORKFLOW-CERTIFICATION-000001"
    assert artifact["decision_packet_id"] == "PRODUCT1-DECISION-PACKET-CERTIFICATION-000001"
    assert artifact["ocs_advisory_id"] == "PRODUCT1-OCS-ADVISORY-CERTIFICATION-000001"
    assert artifact["certification_check_count"] == 11
    assert artifact["remaining_limitation_count"] == 1
    assert artifact["product_workflow_integrity_verified"] is True
    assert artifact["non_authority_guarantees_verified"] is True
    assert artifact["read_only"] is True
    assert artifact["non_authoritative"] is True
    assert artifact["provider_invoked"] is False
    assert artifact["worker_invoked"] is False
    assert artifact["approval_created"] is False
    assert artifact["execution_requested"] is False

    reconstructed = reconstruct_product1_certification_replay(tmp_path / "certification")
    assert reconstructed["certification_id"] == "PRODUCT1-CERTIFICATION-000001"
    assert reconstructed["certification_check_count"] == 11
    assert reconstructed["remaining_limitation_count"] == 1
    assert reconstructed["replay_lineage_count"] == 29


def test_product1_certification_rejects_chain_binding_mismatch(tmp_path) -> None:
    audit_packet = _audit_packet(tmp_path)
    audit_packet["source_ocs_advisory"]["workflow_id"] = "DIFFERENT-WORKFLOW"
    audit_packet["source_ocs_advisory"].pop("artifact_hash")
    audit_packet["source_ocs_advisory"]["artifact_hash"] = replay_hash(audit_packet["source_ocs_advisory"])
    audit_packet["ocs_advisory_hash"] = audit_packet["source_ocs_advisory"]["artifact_hash"]
    audit_packet.pop("artifact_hash")
    audit_packet["artifact_hash"] = replay_hash(audit_packet)

    with pytest.raises(FailClosedRuntimeError, match="certification chain binding mismatch"):
        _certification(tmp_path, audit_packet=audit_packet)


def test_product1_certification_rejects_duplicate_limitation_id(tmp_path) -> None:
    limitations = _limitations()
    limitations.append({**limitations[0]})

    with pytest.raises(FailClosedRuntimeError, match="duplicate limitation id"):
        certify_product1_runtime(
            certification_id="PRODUCT1-CERTIFICATION-DUPLICATE-LIMITATION",
            audit_packet_artifact=_audit_packet(tmp_path),
            remaining_limitations=limitations,
            certified_at=CERTIFIED_AT,
            replay_dir=tmp_path / "duplicate_limitation",
        )


def test_product1_certification_replay_tamper_fails_closed(tmp_path) -> None:
    _certification(tmp_path)
    path = tmp_path / "certification" / "000_product1_runtime_certified.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["approval_created"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_product1_certification_replay(tmp_path / "certification")


def test_product1_certification_runtime_has_no_authority_or_execution_surfaces() -> None:
    import aigol.runtime.product1_certification as runtime

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
