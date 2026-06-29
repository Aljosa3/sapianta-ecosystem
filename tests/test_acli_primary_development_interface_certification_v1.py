"""Tests for G3-02 ACLI primary development interface certification."""

from __future__ import annotations

from copy import deepcopy
import inspect
import json

import pytest

from aigol.runtime.acli_authorization_bridge import create_conversational_authorization_bridge
from aigol.runtime.acli_conversational_development_session import (
    record_conversational_development_turn,
    start_conversational_development_session,
)
from aigol.runtime.acli_development_session_lifecycle import create_acli_development_session
from aigol.runtime.acli_operator_rendering_and_confirmation import (
    classify_operator_confirmation,
    render_operator_response,
)
from aigol.runtime.acli_primary_development_interface_certification import (
    ACLI_PRIMARY_DEVELOPMENT_INTERFACE_CERTIFICATION_ARTIFACT_V1,
    FAILED_CLOSED,
    G3_02_RUNTIME_CERTIFIED,
    certify_acli_primary_development_interface,
    reconstruct_acli_primary_development_interface_certification_replay,
)
from aigol.runtime.acli_proposal_approval_bridge import (
    create_conversational_development_proposal,
    generate_conversational_approval_request,
    record_conversational_approval_decision,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-29T00:00:00Z"
TURN_AT = "2026-06-29T00:01:00Z"
RENDERED_AT = "2026-06-29T00:02:00Z"
PROPOSAL_AT = "2026-06-29T00:03:00Z"
REQUESTED_AT = "2026-06-29T00:04:00Z"
DECIDED_AT = "2026-06-29T00:05:00Z"
BRIDGED_AT = "2026-06-29T00:06:00Z"
CERTIFIED_AT = "2026-06-29T00:07:00Z"


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
            "replay_reference": f"runtime/g3/certification/{name}.json",
            "replay_hash": replay_hash({"source": name}),
        }
    ]


def _g3_02_chain(tmp_path) -> dict[str, dict]:
    session = create_acli_development_session(
        session_id="ACLI-G3-SESSION-CERT-000001",
        canonical_semantic_artifact_reference="CSA-SESSION-CERT-000001",
        canonical_semantic_artifact_hash=replay_hash({"csa": "session-cert"}),
        replay_lineage=_lineage("session"),
        governance_checkpoints=_governance_checkpoints(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "session",
    )["session_artifact"]
    conversation = start_conversational_development_session(
        conversation_id="ACLI-CONVERSATION-CERT-000001",
        session_artifact=session,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "conversation",
    )["conversation_artifact"]
    conversation = record_conversational_development_turn(
        conversation_artifact=conversation,
        turn_id="TURN-CERT-000001",
        recorded_at=TURN_AT,
        replay_dir=tmp_path / "conversation",
        prompt_hash=replay_hash({"prompt": "prepare certified ACLI proposal"}),
        canonical_semantic_artifact_reference="CSA-TURN-CERT-000001",
        canonical_semantic_artifact_hash=replay_hash({"csa": "turn-cert"}),
        replay_lineage=_lineage("turn"),
        clarification_status="CLARIFICATION_RESOLVED",
        proposal_status="PROPOSAL_CONFIRMATION_REQUIRED",
        confirmation_status="CONFIRMATION_REQUIRED",
        continuation_status="NEW_CONVERSATION",
        proposal_reference="PROPOSAL-CERT-000001",
        confirmation_request_reference="CONFIRM-CERT-000001",
    )["conversation_artifact"]
    rendering = render_operator_response(
        render_id="RENDER-CERT-000001",
        conversation_artifact=conversation,
        rendered_at=RENDERED_AT,
        replay_dir=tmp_path / "operator",
    )["artifact"]
    confirmation = classify_operator_confirmation(
        classification_id="CLASSIFY-CERT-000001",
        conversation_artifact=conversation,
        operator_input="approve this proposal",
        classified_at=RENDERED_AT,
        replay_dir=tmp_path / "operator",
    )["artifact"]
    proposal = create_conversational_development_proposal(
        proposal_id="ACLI-PROPOSAL-CERT-000001",
        conversation_artifact=conversation,
        originating_turn_id="TURN-CERT-000001",
        proposal_version=1,
        proposal_summary="Certify ACLI primary development interface runtime chain.",
        rollback_reference="rollback:ACLI-PROPOSAL-CERT-000001:v1",
        created_at=PROPOSAL_AT,
        replay_dir=tmp_path / "proposal",
    )["proposal_artifact"]
    proposal = generate_conversational_approval_request(
        proposal_artifact=proposal,
        approval_request_id="ACLI-APPROVAL-REQUEST-CERT-000001",
        requested_at=REQUESTED_AT,
        replay_dir=tmp_path / "proposal",
    )["proposal_artifact"]
    proposal = record_conversational_approval_decision(
        proposal_artifact=proposal,
        approval_decision_id="ACLI-APPROVAL-DECISION-CERT-000001",
        decision="APPROVED",
        decision_rationale_hash=replay_hash({"rationale": "operator approved certification chain"}),
        decided_at=DECIDED_AT,
        replay_dir=tmp_path / "proposal",
    )["proposal_artifact"]
    authorization = create_conversational_authorization_bridge(
        authorization_bridge_id="ACLI-AUTHORIZATION-BRIDGE-CERT-000001",
        proposal_artifact=proposal,
        created_at=BRIDGED_AT,
        replay_dir=tmp_path / "authorization",
    )["authorization_bridge_artifact"]
    return {
        "session": session,
        "conversation": conversation,
        "rendering": rendering,
        "confirmation": confirmation,
        "proposal": proposal,
        "authorization": authorization,
    }


def _certify(chain: dict[str, dict], tmp_path):
    return certify_acli_primary_development_interface(
        certification_id="G3-02-CERTIFICATION-000001",
        session_artifact=chain["session"],
        conversation_artifact=chain["conversation"],
        operator_rendering_artifact=chain["rendering"],
        confirmation_classification_artifact=chain["confirmation"],
        proposal_artifact=chain["proposal"],
        authorization_bridge_artifact=chain["authorization"],
        created_at=CERTIFIED_AT,
        replay_dir=tmp_path / "certification",
    )


def _rehash(artifact: dict) -> dict:
    artifact["artifact_hash"] = replay_hash({key: value for key, value in artifact.items() if key != "artifact_hash"})
    return artifact


def test_certifies_complete_g3_02_runtime_chain(tmp_path) -> None:
    capture = _certify(_g3_02_chain(tmp_path), tmp_path)
    artifact = capture["certification_artifact"]

    assert artifact["artifact_type"] == ACLI_PRIMARY_DEVELOPMENT_INTERFACE_CERTIFICATION_ARTIFACT_V1
    assert artifact["certification_status"] == G3_02_RUNTIME_CERTIFIED
    assert artifact["recommended_certification"] is True
    assert artifact["certification_check_count"] == 10
    assert artifact["passed_check_count"] == 10
    assert artifact["failed_check_count"] == 0
    assert artifact["session_id"] == "ACLI-G3-SESSION-CERT-000001"
    assert artifact["proposal_id"] == "ACLI-PROPOSAL-CERT-000001"
    assert artifact["authorization_bridge_id"] == "ACLI-AUTHORIZATION-BRIDGE-CERT-000001"
    assert artifact["rollback_reference"] == "rollback:ACLI-PROPOSAL-CERT-000001:v1"
    assert artifact["worker_invoked"] is False
    assert artifact["execution_requested"] is False
    assert artifact["repository_mutated"] is False

    reconstructed = reconstruct_acli_primary_development_interface_certification_replay(tmp_path / "certification")
    assert reconstructed["certification_status"] == G3_02_RUNTIME_CERTIFIED
    assert reconstructed["passed_check_count"] == 10
    assert reconstructed["recommended_certification"] is True


def test_certification_fails_closed_on_lineage_mismatch(tmp_path) -> None:
    chain = _g3_02_chain(tmp_path)
    chain["rendering"] = deepcopy(chain["rendering"])
    chain["rendering"]["session_id"] = "ACLI-G3-SESSION-CERT-MISMATCH"
    _rehash(chain["rendering"])

    capture = _certify(chain, tmp_path)
    artifact = capture["certification_artifact"]

    assert artifact["certification_status"] == FAILED_CLOSED
    assert artifact["recommended_certification"] is False
    assert artifact["failed_check_count"] == 1
    assert "conversational_continuity" in artifact["failure_reason"]
    assert artifact["execution_requested"] is False


def test_certification_replay_tamper_fails_closed(tmp_path) -> None:
    _certify(_g3_02_chain(tmp_path), tmp_path)
    path = tmp_path / "certification" / "000_acli_primary_development_interface_certification_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["worker_invoked"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_acli_primary_development_interface_certification_replay(tmp_path / "certification")


def test_certification_runtime_has_no_execution_provider_worker_deployment_or_mutation_surfaces() -> None:
    import aigol.runtime.acli_primary_development_interface_certification as runtime

    source = inspect.getsource(runtime)

    assert "authorize_execution(" not in source
    assert "invoke_worker(" not in source
    assert "execute_worker(" not in source
    assert "invoke_live_external_llm_provider(" not in source
    assert "subprocess." not in source
    assert "os.system" not in source
    assert "deploy(" not in source
    assert "write_text(" not in source
    assert '"authorization_created": True' not in source
    assert '"execution_requested": True' not in source
