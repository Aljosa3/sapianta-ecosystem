"""Tests for AIGOL_EXECUTION_READINESS_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from aigol.runtime.execution_authorization_runtime import authorize_execution_ready
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.multi_provider_cognition_runtime import create_default_cognition_provider_contract
from aigol.runtime.ocs_execution_readiness_runtime import (
    EXECUTION_READY,
    FAILED_CLOSED,
    MILESTONE_ID,
    evaluate_ocs_execution_readiness,
    reconstruct_ocs_execution_readiness_replay,
)
from aigol.runtime.ocs_llm_cognition_end_to_end_runtime import run_ocs_llm_cognition_end_to_end
from aigol.runtime.ocs_to_execution_handoff_runtime import create_ocs_execution_handoff
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-08T00:00:00Z"


def _source_context() -> dict:
    artifact = {
        "artifact_type": "HUMAN_REQUEST_ARTIFACT_V1",
        "artifact_id": "HUMAN-REQUEST-OCS-READINESS-001",
        "status": "REPLAY_VISIBLE",
        "summary": "Human asks OCS to identify execution-ready candidate context.",
        "replay_visible": True,
        "authority": False,
        "execution_requested": False,
        "worker_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return {"conversation_context": [artifact]}


def _ocs_capture(tmp_path: Path) -> dict:
    response = json.dumps(
        {
            "findings": ["OCS found a bounded execution candidate for human review."],
            "assumptions": ["Execution must remain downstream of approval."],
            "risks": ["Worker selection must remain bounded."],
            "uncertainties": ["Exact worker implementation scope requires review."],
            "clarification_questions": ["Should this become an execution intake candidate?"],
            "recommended_next_milestone": "Create OCS execution handoff artifact.",
            "confidence": "MEDIUM",
        },
        sort_keys=True,
    )

    def transport(_payload: dict, metadata: dict) -> dict:
        assert metadata["provider_role"] == "COGNITION_PROVIDER"
        return {
            "model": "gpt-5.1",
            "output_text": response,
            "usage": {"input_tokens": 100, "output_tokens": 50, "total_tokens": 150},
        }

    return run_ocs_llm_cognition_end_to_end(
        end_to_end_id="OCS-READINESS-E2E-001",
        human_question="Turn this OCS cognition into a bounded execution candidate.",
        source_context=_source_context(),
        provider_contracts=[create_default_cognition_provider_contract(provider_id="openai", created_at=CREATED_AT)],
        transport_registry={"openai": transport},
        created_at=CREATED_AT,
        replay_dir=tmp_path / "ocs_e2e",
        source_chain_id="CHAIN-OCS-READINESS-001",
        source_request_reference="HUMAN-REQUEST-OCS-READINESS-001",
        single_provider_primary_mode=True,
    )


def _handoff_capture(tmp_path: Path) -> dict:
    ocs = _ocs_capture(tmp_path)
    assert ocs["fail_closed"] is False
    return create_ocs_execution_handoff(
        handoff_id="OCS-HANDOFF-READINESS-001",
        ocs_cognition_replay_reference=ocs["replay_reference"],
        execution_intake_id="OCS-EXECUTION-INTAKE-READINESS-001",
        execution_intent_summary="Prepare a bounded execution candidate for readiness validation.",
        execution_candidate_scope={
            "mode": "EXECUTION_INTAKE_ONLY",
            "domain": "product_build",
            "execution_authorized": False,
        },
        requested_outcomes=["execution intake candidate"],
        non_goals=["approval creation", "authorization", "worker dispatch"],
        allowed_outputs=["execution-ready candidate proposal"],
        forbidden_operations=["AUTHORIZE_EXECUTION", "INVOKE_WORKER", "DISPATCH_WORKER", "RETRY", "REPAIR"],
        worker_role_requirements=["bounded implementation worker"],
        target_worker_family="IMPLEMENTATION",
        candidate_worker_constraints={"single_worker_only": True, "human_review_required": True},
        worker_capability_requirements=["bounded file generation after downstream authorization"],
        worker_exclusion_rules=["no provider-as-worker", "no unregistered worker"],
        worker_registry_requirements=["registered worker identity required"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "ocs_handoff",
        source_chain_id="CHAIN-OCS-READINESS-001",
    )


def _ready_args(tmp_path: Path) -> dict:
    handoff = _handoff_capture(tmp_path)
    assert handoff["fail_closed"] is False
    return {
        "readiness_id": "OCS-READINESS-001",
        "ocs_handoff_replay_reference": handoff["ocs_execution_handoff_replay_reference"],
        "approval_status": "APPROVED",
        "approval_reference": "HUMAN-APPROVAL-OCS-READINESS-001",
        "approval_hash": "sha256:approvalhash000000000000000000000000000000000000000000000000000001",
        "approving_actor": "human_operator",
        "approved_at": CREATED_AT,
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / "ocs_readiness",
    }


def test_ocs_execution_readiness_artifact_is_created_without_authorization_or_worker(tmp_path):
    capture = evaluate_ocs_execution_readiness(**_ready_args(tmp_path))
    replay = reconstruct_ocs_execution_readiness_replay(tmp_path / "ocs_readiness")
    candidate = capture["execution_candidate_artifact"]
    packet = capture["execution_packet_artifact"]
    validation = capture["execution_validation_artifact"]
    ready = capture["execution_ready_status_artifact"]

    assert capture["milestone_id"] == MILESTONE_ID
    assert capture["execution_status"] == EXECUTION_READY
    assert candidate["approval_status"] == "APPROVED"
    assert candidate["approval_reference"] == "HUMAN-APPROVAL-OCS-READINESS-001"
    assert candidate["approval_hash"].startswith("sha256:")
    assert candidate["execution_scope"]["execution_authorized"] is False
    assert packet["execution_contract"]["execution_state"] == "NOT_STARTED"
    assert packet["execution_contract"]["execution_authorized"] is False
    assert validation["validation_status"] == "OCS_EXECUTION_READINESS_VALIDATED"
    assert all(validation["validation_checks"].values())
    assert ready["artifact_type"] == "EXECUTION_READY_STATUS_ARTIFACT_V1"
    assert ready["execution_started"] is False
    assert ready["authorization_created"] is False
    assert ready["worker_request_created"] is False
    assert ready["worker_assigned"] is False
    assert ready["worker_dispatched"] is False
    assert ready["worker_invoked"] is False
    assert replay["execution_status"] == EXECUTION_READY
    assert replay["authorization_created"] is False
    assert replay["worker_invoked"] is False
    assert replay["execution_started"] is False


def test_missing_approval_fails_closed(tmp_path):
    args = _ready_args(tmp_path)
    args["approval_status"] = "PENDING_HUMAN_REVIEW"
    args["replay_dir"] = tmp_path / "missing_approval_readiness"
    capture = evaluate_ocs_execution_readiness(**args)

    assert capture["execution_status"] == FAILED_CLOSED
    assert capture["fail_closed"] is True
    assert "approval missing" in capture["failure_reason"]
    assert capture["authorization_created"] is False
    assert capture["worker_request_created"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_started"] is False


def test_invalid_approval_actor_fails_closed(tmp_path):
    args = _ready_args(tmp_path)
    args["approving_actor"] = "openai"
    args["replay_dir"] = tmp_path / "provider_actor_readiness"
    capture = evaluate_ocs_execution_readiness(**args)

    assert capture["execution_status"] == FAILED_CLOSED
    assert "approval actor invalid" in capture["failure_reason"]


def test_execution_readiness_replay_tampering_is_detected(tmp_path):
    evaluate_ocs_execution_readiness(**_ready_args(tmp_path))
    path = tmp_path / "ocs_readiness" / "000_execution_candidate_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["worker_invoked"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_ocs_execution_readiness_replay(tmp_path / "ocs_readiness")


def test_ocs_execution_readiness_can_feed_existing_authorization_runtime(tmp_path):
    capture = evaluate_ocs_execution_readiness(**_ready_args(tmp_path))
    authorization = authorize_execution_ready(
        authorization_id="OCS-AUTHORIZATION-001",
        execution_ready_replay_reference=capture["ocs_execution_readiness_replay_reference"],
        authorizing_actor="human_authorizer",
        authorized_at=CREATED_AT,
        replay_dir=tmp_path / "ocs_authorization",
    )

    assert authorization["authorization_status"] == "EXECUTION_AUTHORIZED"
    assert authorization["approval_status"] == "APPROVED"
    assert authorization["approval_reference"] == "HUMAN-APPROVAL-OCS-READINESS-001"
    assert authorization["worker_assigned"] is False
    assert authorization["worker_dispatched"] is False
    assert authorization["worker_invoked"] is False
    assert authorization["execution_started"] is False


def test_ocs_execution_readiness_runtime_preserves_downstream_boundaries() -> None:
    import aigol.runtime.ocs_execution_readiness_runtime as runtime

    source = inspect.getsource(runtime)

    forbidden_calls = (
        "authorize_execution_ready(",
        "create_worker_invocation_request(",
        "assign_worker(",
        "dispatch_worker(",
        "invoke_worker(",
        "repair(",
        "retry(",
    )
    for forbidden in forbidden_calls:
        assert forbidden not in source
