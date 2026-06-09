from __future__ import annotations

import json

import pytest

from aigol.runtime.clarification_continuity_runtime import run_clarification_continuity
from aigol.runtime.clarified_domain_intent_handoff_review_runtime import (
    WORKER_BINDING_APPROVED,
    review_clarified_domain_intent,
)
from aigol.runtime.conversational_cli_runtime import route_conversational_cli_intent
from aigol.runtime.domain_approval_entry_to_execution_ready_authorization_bridge_runtime import (
    DOMAIN_EXECUTION_READY_BRIDGED,
    bridge_domain_approval_entry_to_execution_ready,
    reconstruct_domain_execution_ready_bridge_replay,
)
from aigol.runtime.domain_handoff_review_approval_binding_runtime import bind_domain_handoff_review_approval
from aigol.runtime.execution_authorization_runtime import authorize_execution_ready
from aigol.runtime.governed_implementation_dry_run import EXECUTION_READY
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize
from aigol.runtime.unknown_domain_clarification_runtime import run_unknown_domain_clarification_workflow


CREATED_AT = "2026-06-09T00:00:00Z"
SESSION_ID = "SESSION-DOMAIN-READY-BRIDGE-000001"
PROMPT = "Create a new governed domain called FreshDomain."
REPLY = "\n".join(
    [
        "Primary purpose: Create a safe pilot governed domain.",
        "Expected capabilities: Clarification handling and bounded workflow resume.",
        "Target users: Internal operators.",
    ]
)
APPROVAL_PROMPT = "Approve FreshDomain for domain artifact creation."


def _seed_open_clarification(session_root, turn_id: str = "TURN-000001") -> str:
    prompt_id = f"{SESSION_ID}:{turn_id}"
    turn_root = session_root / turn_id
    route_conversational_cli_intent(
        routing_id=f"{prompt_id}:CONVERSATIONAL-CLI-ROUTING",
        prompt_id=prompt_id,
        human_prompt=PROMPT,
        canonical_chain_id=prompt_id,
        created_at=CREATED_AT,
        replay_dir=turn_root / "conversational_cli_routing",
    )
    run_unknown_domain_clarification_workflow(
        clarification_id=f"{prompt_id}:UNKNOWN-DOMAIN-CLARIFICATION",
        prompt_id=prompt_id,
        human_prompt=PROMPT,
        canonical_chain_id=prompt_id,
        created_at=CREATED_AT,
        replay_dir=turn_root / "unknown_domain_clarification",
    )
    return prompt_id


def _approval_entry(tmp_path):
    session_root = tmp_path / "runtime" / SESSION_ID
    prompt_id = _seed_open_clarification(session_root)
    continuity = run_clarification_continuity(
        continuity_id=f"{SESSION_ID}:TURN-000002:CLARIFICATION-CONTINUITY",
        session_root=session_root,
        turn_id="TURN-000002",
        prompt_id=f"{SESSION_ID}:TURN-000002",
        operator_reply=REPLY,
        current_chain_id=prompt_id,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "continuity",
    )
    review = review_clarified_domain_intent(
        review_id="HANDOFF-REVIEW-FRESHDOMAIN-000001",
        clarification_continuity_replay_reference=continuity["clarification_continuity_replay_reference"],
        review_decision=WORKER_BINDING_APPROVED,
        reviewed_by="AIGOL_GOVERNANCE_REVIEW",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "handoff_review",
    )
    return bind_domain_handoff_review_approval(
        approval_entry_id="DOMAIN-APPROVAL-FRESHDOMAIN-000001",
        handoff_review_replay_reference=review["handoff_review_replay_reference"],
        operator_prompt=APPROVAL_PROMPT,
        approved_domain="FreshDomain",
        approving_actor="HUMAN_OPERATOR",
        approved_at=CREATED_AT,
        replay_dir=tmp_path / "approval_binding",
        latest_handoff_review_replay_reference=review["handoff_review_replay_reference"],
    )


def _bridge(tmp_path, *, domain: str = "FreshDomain"):
    approval = _approval_entry(tmp_path)
    return bridge_domain_approval_entry_to_execution_ready(
        bridge_id="DOMAIN-READY-BRIDGE-FRESHDOMAIN-000001",
        domain_approval_binding_replay_reference=approval["domain_approval_binding_replay_reference"],
        approved_domain=domain,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "ready_bridge",
    )


def test_domain_approval_entry_converts_to_execution_ready_packet(tmp_path) -> None:
    capture = _bridge(tmp_path)
    replay = reconstruct_domain_execution_ready_bridge_replay(tmp_path / "ready_bridge")

    assert capture["bridge_status"] == DOMAIN_EXECUTION_READY_BRIDGED
    assert capture["execution_status"] == EXECUTION_READY
    assert capture["execution_ready_replay_reference"]
    assert capture["execution_ready_replay_hash"].startswith("sha256:")
    assert capture["authorization_runtime_compatible"] is True
    assert capture["authorization_created"] is False
    assert capture["worker_request_created"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_started"] is False
    assert replay["bridge_status"] == DOMAIN_EXECUTION_READY_BRIDGED
    assert replay["authorization_runtime_compatible"] is True


def test_bridge_output_feeds_existing_execution_authorization_runtime(tmp_path) -> None:
    bridge = _bridge(tmp_path)
    authorization = authorize_execution_ready(
        authorization_id="DOMAIN-AUTHORIZATION-FRESHDOMAIN-000001",
        execution_ready_replay_reference=bridge["execution_ready_replay_reference"],
        authorizing_actor="human_authorizer",
        authorized_at=CREATED_AT,
        replay_dir=tmp_path / "authorization",
    )

    assert authorization["authorization_status"] == "EXECUTION_AUTHORIZED"
    assert authorization["approval_status"] == "APPROVED"
    assert authorization["approval_reference"] == "DOMAIN-APPROVAL-FRESHDOMAIN-000001"
    assert authorization["worker_invoked"] is False
    assert authorization["execution_started"] is False


def test_bridge_replay_tampering_is_detected(tmp_path) -> None:
    _bridge(tmp_path)
    path = tmp_path / "ready_bridge" / "execution_ready" / "000_execution_candidate_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["target_domain"] = "OtherDomain"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_domain_execution_ready_bridge_replay(tmp_path / "ready_bridge")


def test_domain_mismatch_fails_closed(tmp_path) -> None:
    capture = _bridge(tmp_path, domain="OtherDomain")

    assert capture["fail_closed"] is True
    assert "approved-domain mismatch" in capture["failure_reason"]
    assert capture["authorization_created"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_started"] is False


def test_approval_lineage_mismatch_fails_closed(tmp_path) -> None:
    approval = _approval_entry(tmp_path)
    path = tmp_path / "approval_binding" / "000_domain_approval_binding_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["approval_reference"] = "OTHER-APPROVAL"
    wrapper["artifact"]["artifact_hash"] = "sha256:broken"
    wrapper["replay_hash"] = "sha256:broken"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    capture = bridge_domain_approval_entry_to_execution_ready(
        bridge_id="DOMAIN-READY-BRIDGE-FRESHDOMAIN-000002",
        domain_approval_binding_replay_reference=approval["domain_approval_binding_replay_reference"],
        approved_domain="FreshDomain",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "approval_mismatch_bridge",
    )

    assert capture["fail_closed"] is True
    assert "hash mismatch" in capture["failure_reason"]
