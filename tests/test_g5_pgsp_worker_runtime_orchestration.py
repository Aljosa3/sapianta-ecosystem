"""Tests for G5-09 PGSP Worker runtime orchestration."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aigol.runtime.conversation_native_development_intent_routing import (
    run_conversation_native_development_intent_routing,
)
from aigol.runtime.conversation_session_resume_runtime import resume_conversation_session
from aigol.runtime.conversation_to_ppp_handoff_execution import (
    HUMAN_APPROVAL_REQUIRED,
    run_conversation_to_ppp_handoff_execution,
)
from aigol.runtime.execution_authorization_runtime import authorize_execution_ready
from aigol.runtime.g5_pgsp_worker_runtime_orchestration import (
    PGSP_WORKER_ORCHESTRATION_COMPLETED,
    PGSP_WORKER_ORCHESTRATION_FAILED_CLOSED,
    reconstruct_g5_pgsp_worker_orchestration_replay,
    run_g5_pgsp_worker_runtime_orchestration,
)
from aigol.runtime.governed_implementation_dry_run import prepare_governed_implementation_dry_run
from aigol.runtime.implementation_approval_resume import (
    create_human_implementation_approval,
    resume_implementation_after_approval,
)
from aigol.runtime.implementation_handoff_visibility import create_implementation_handoff_visibility_summary
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.post_execution_replay_review_runtime import REVIEW_COMPLETED
from aigol.runtime.worker_assignment_runtime import WORKER_ASSIGNED
from aigol.runtime.worker_dispatch_runtime import WORKER_DISPATCHED
from aigol.runtime.worker_invocation_request_runtime import WORKER_INVOCATION_REQUEST_CREATED
from aigol.runtime.worker_invocation_runtime import WORKER_INVOKED
from aigol.runtime.worker_result_capture_runtime import WORKER_RESULT_CAPTURED
from aigol.runtime.worker_result_validation_runtime import RESULT_VALIDATED


CREATED_AT = "2026-06-04T00:00:00+00:00"
SESSION_ID = "SESSION-G5-09-PGSP-WORKER-000001"


def _ppp_capture(tmp_path: Path, *, prompt: str, suffix: str) -> dict:
    session_id = f"{SESSION_ID}-{suffix}"
    allocation = resume_conversation_session(
        session_id=session_id,
        runtime_root=tmp_path / f"routing_runtime_{suffix}",
        created_at=CREATED_AT,
    )
    prompt_id = f"{session_id}:{allocation['next_turn_id']}"
    routed = run_conversation_native_development_intent_routing(
        routing_id=f"{prompt_id}:NATIVE_DEVELOPMENT_INTENT_ROUTING",
        prompt_id=prompt_id,
        human_prompt=prompt,
        canonical_chain_id=prompt_id,
        turn_allocation_evidence=allocation,
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"routing_{suffix}",
    )
    return run_conversation_to_ppp_handoff_execution(
        execution_id=f"{prompt_id}:CONVERSATION-TO-PPP-HANDOFF",
        native_development_intent_routed_artifact=routed["native_development_intent_routed_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"ppp_{suffix}",
    )


def _execution_ready(tmp_path: Path, *, prompt: str, suffix: str) -> dict:
    ppp = _ppp_capture(tmp_path, prompt=prompt, suffix=suffix)
    upstream = ppp["conversation_to_ppp_handoff_execution_artifact"]
    handoff_replay_reference = ppp.get("handoff_replay_reference")
    approval_status = ppp["approval_status"]
    if ppp["terminal_status"] == HUMAN_APPROVAL_REQUIRED:
        request = upstream["approval_resume_packet"]["approval_request_artifact"]
        approval = create_human_implementation_approval(
            approval_id=f"HUMAN-APPROVAL-G5-09-{suffix}",
            approval_request_artifact=request,
            approving_actor="human.operator",
            approval_timestamp=CREATED_AT,
        )
        resumed = resume_implementation_after_approval(
            resume_id=f"APPROVAL-RESUME-G5-09-{suffix}",
            approval_required_replay_reference=ppp["conversation_to_ppp_handoff_execution_replay_reference"],
            human_approval_artifact=approval,
            created_at=CREATED_AT,
            replay_dir=tmp_path / f"approval_resume_{suffix}",
        )
        upstream = resumed["implementation_approval_resume_artifact"]
        handoff_replay_reference = resumed["implementation_handoff_replay_reference"]
        approval_status = "APPROVED"
    visibility = create_implementation_handoff_visibility_summary(
        visibility_id=f"VISIBILITY-G5-09-{suffix}",
        handoff_replay_reference=handoff_replay_reference,
        approval_status=approval_status,
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"visibility_{suffix}",
    )
    return prepare_governed_implementation_dry_run(
        dry_run_id=f"DRY-RUN-G5-09-{suffix}",
        handoff_replay_reference=handoff_replay_reference,
        handoff_visibility_artifact=visibility["implementation_handoff_visibility_artifact"],
        upstream_lineage_artifact=upstream,
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"dry_run_{suffix}",
    )


def _authorization(tmp_path: Path, *, suffix: str, expires_at: str = "NEVER") -> dict:
    ready = _execution_ready(
        tmp_path,
        prompt="Create a filesystem worker.",
        suffix=suffix,
    )
    return authorize_execution_ready(
        authorization_id=f"AUTHORIZATION-G5-09-{suffix}",
        execution_ready_replay_reference=ready["governed_implementation_dry_run_replay_reference"],
        authorizing_actor="AIGOL_GOVERNANCE",
        authorized_at=CREATED_AT,
        authorization_expires_at=expires_at,
        replay_dir=tmp_path / f"authorization_{suffix}",
    )


def _orchestrate(tmp_path: Path, *, suffix: str, expires_at: str = "NEVER") -> dict:
    authorization = _authorization(tmp_path, suffix=suffix, expires_at=expires_at)
    return run_g5_pgsp_worker_runtime_orchestration(
        session_id=f"G5-09-PGSP-WORKER-SESSION-{suffix}",
        execution_authorization_replay_reference=authorization["execution_authorization_replay_reference"],
        requested_by="AIGOL_GOVERNANCE",
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"g5_09_orchestration_{suffix}",
    )


def test_g5_09_pgsp_orchestration_reuses_existing_worker_stack(tmp_path) -> None:
    capture = _orchestrate(tmp_path, suffix="success")
    reconstructed = reconstruct_g5_pgsp_worker_orchestration_replay(tmp_path / "g5_09_orchestration_success")

    assert capture["orchestration_status"] == PGSP_WORKER_ORCHESTRATION_COMPLETED
    assert capture["worker_invocation_request_status"] == WORKER_INVOCATION_REQUEST_CREATED
    assert capture["worker_assignment_status"] == WORKER_ASSIGNED
    assert capture["worker_dispatch_status"] == WORKER_DISPATCHED
    assert capture["worker_invocation_status"] == WORKER_INVOKED
    assert capture["execution_status"] == "EXECUTING"
    assert capture["result_capture_status"] == WORKER_RESULT_CAPTURED
    assert capture["result_validation_status"] == RESULT_VALIDATED
    assert capture["post_execution_review_status"] == REVIEW_COMPLETED
    assert capture["worker_runtime_reused"] is True
    assert capture["worker_architecture_created"] is False
    assert capture["duplicate_worker_authorization_created"] is False
    assert capture["duplicate_worker_replay_created"] is False
    assert capture["duplicate_worker_identity_created"] is False
    assert capture["repository_mutated"] is False
    assert capture["deployment_performed"] is False
    assert reconstructed["orchestration_status"] == PGSP_WORKER_ORCHESTRATION_COMPLETED
    assert reconstructed["worker_runtime_reused"] is True


def test_g5_09_pgsp_orchestration_persists_replay_and_uhcl_summary_evidence(tmp_path) -> None:
    _orchestrate(tmp_path, suffix="evidence")
    replay_dir = tmp_path / "g5_09_orchestration_evidence"
    summary_wrapper = json.loads((replay_dir / "001_pgsp_worker_orchestration_summary_recorded.json").read_text())
    summary = summary_wrapper["artifact"]

    assert (replay_dir / "000_pgsp_worker_orchestration_context_recorded.json").exists()
    assert summary["governance_checkpoint_status"] == "G5_09_PGSP_WORKER_ORCHESTRATION_GOVERNANCE_PASSED"
    assert summary["uhcl_summary_status"] == "G5_09_UHCL_WORKER_EXECUTION_SUMMARY_AVAILABLE"
    assert summary["worker_assigned"] is True
    assert summary["worker_dispatched"] is True
    assert summary["worker_invoked"] is True
    assert summary["execution_started"] is True
    assert set(summary["nested_replay_references"]) == {
        "worker_invocation_request",
        "worker_assignment",
        "worker_dispatch",
        "worker_invocation",
        "execution",
        "worker_result_capture",
        "worker_result_validation",
        "post_execution_replay_review",
    }


def test_g5_09_pgsp_orchestration_fails_closed_when_authorization_missing(tmp_path) -> None:
    capture = run_g5_pgsp_worker_runtime_orchestration(
        session_id="G5-09-PGSP-WORKER-SESSION-MISSING",
        execution_authorization_replay_reference=str(tmp_path / "missing_authorization"),
        requested_by="AIGOL_GOVERNANCE",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "g5_09_orchestration_missing",
    )
    reconstructed = reconstruct_g5_pgsp_worker_orchestration_replay(tmp_path / "g5_09_orchestration_missing")

    assert capture["orchestration_status"] == PGSP_WORKER_ORCHESTRATION_FAILED_CLOSED
    assert capture["worker_assignment_status"] is None
    assert capture["worker_dispatch_status"] is None
    assert capture["worker_invocation_status"] is None
    assert "missing" in capture["failure_reason"]
    assert reconstructed["orchestration_status"] == PGSP_WORKER_ORCHESTRATION_FAILED_CLOSED


def test_g5_09_pgsp_orchestration_detects_replay_corruption(tmp_path) -> None:
    _orchestrate(tmp_path, suffix="corrupt")
    summary_path = tmp_path / "g5_09_orchestration_corrupt" / "001_pgsp_worker_orchestration_summary_recorded.json"
    wrapper = json.loads(summary_path.read_text(encoding="utf-8"))
    wrapper["artifact"]["repository_mutated"] = True
    summary_path.write_text(json.dumps(wrapper, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_g5_pgsp_worker_orchestration_replay(tmp_path / "g5_09_orchestration_corrupt")


def test_g5_09_pgsp_orchestration_fails_closed_when_authorization_expired(tmp_path) -> None:
    capture = _orchestrate(tmp_path, suffix="expired", expires_at="2026-06-03T23:59:59+00:00")

    assert capture["orchestration_status"] == PGSP_WORKER_ORCHESTRATION_FAILED_CLOSED
    assert "authorization expired" in capture["failure_reason"]
