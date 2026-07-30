from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from aigol.runtime import platform_core_conversation_boundary as conversation_boundary
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_conversation_boundary import (
    APPROVAL_AWAITING_HUMAN,
    BOUNDARY_COMPLETED,
    BOUNDARY_FAILED_CLOSED,
    CLARIFICATION_AWAITING_REPLY,
    CLARIFICATION_REPLY_SUBMITTED,
    CONVERSATION_CANCELED,
    CONVERSATION_FAILED_CLOSED,
    HUMAN_APPROVAL_SUBMITTED,
    HUMAN_CANCEL_SUBMITTED,
    HUMAN_EXIT_REQUESTED,
    HUMAN_REQUEST_SUBMITTED,
    INPUT_EOF_OBSERVED,
    REPLAY_STATE_RESTORED,
    RESULT_DELIVERED,
    create_platform_core_conversation_event,
    reconstruct_platform_core_conversation_projection,
    run_platform_core_conversation_boundary,
    validate_platform_core_conversation_event,
    validate_platform_core_conversation_projection,
    validate_platform_core_conversation_session_checkpoint,
    validate_platform_core_conversation_turn_evidence_manifest,
)
from aigol.runtime.transport.serialization import (
    canonical_serialize,
    load_json,
    replay_hash,
)


CREATED_AT = "2026-07-30T00:00:00Z"


def _event(
    *,
    tmp_path: Path,
    session_id: str,
    event_type: str,
    payload: dict,
    source_interface: str = "test-interface",
    created_at: str = CREATED_AT,
) -> dict:
    return create_platform_core_conversation_event(
        event_type=event_type,
        session_id=session_id,
        payload=payload,
        created_at=created_at,
        runtime_root=tmp_path,
        source_interface=source_interface,
    )


def _submit(
    *,
    tmp_path: Path,
    session_id: str,
    message: str,
    event_type: str = HUMAN_REQUEST_SUBMITTED,
) -> dict:
    return run_platform_core_conversation_boundary(
        event=_event(
            tmp_path=tmp_path,
            session_id=session_id,
            event_type=event_type,
            payload={"message": message},
        ),
        runtime_root=tmp_path,
        workspace=".",
    )


def _successful_runtime(calls: list[dict]):
    def run(args, input_func, output_func):
        prompt = input_func("")
        calls.append(
            {
                "prompt": prompt,
                "operator_context": args.operator_context,
                "approved_binding_hash": (
                    args.approved_implementation_turn_binding_hash
                ),
            }
        )
        output_func("certified runtime completed")
        return {
            "command": "test governed runtime",
            "runtime_root": args.runtime_root,
            "turn_count": 1,
            "failed_turns": 0,
            "exit_reason": "EXIT_COMMAND",
            "auto_continue_enabled": True,
            "turns": [
                {
                    "worker_invoked": True,
                    "replay_certification_reached": True,
                    "execution_authorization_status": "EXECUTION_AUTHORIZED",
                    "openai_provider_reached": True,
                    "execution_preparation_status": "EXECUTION_READY",
                    "worker_assignment_status": "WORKER_ASSIGNED",
                    "worker_dispatch_status": "WORKER_DISPATCHED",
                    "worker_invocation_status": "WORKER_INVOKED",
                    "result_validation_status": "RESULT_VALIDATION_COMPLETED",
                    "replay_certification_status": "REPLAY_CERTIFICATION_COMPLETED",
                    "execution_summary_reference": "summary",
                    "human_confirmation_reference": "approval",
                    "replay_reference": str(
                        Path(args.runtime_root) / "runtime" / "TURN-000001"
                    ),
                }
            ],
        }

    return run


def test_canonical_event_validation_is_deterministic_and_fail_closed(
    tmp_path: Path,
) -> None:
    event = _event(
        tmp_path=tmp_path,
        session_id="G49-EVENT",
        event_type=HUMAN_REQUEST_SUBMITTED,
        payload={"message": "What is Replay?"},
    )
    identical = _event(
        tmp_path=tmp_path,
        session_id="G49-EVENT",
        event_type=HUMAN_REQUEST_SUBMITTED,
        payload={"message": "What is Replay?"},
    )

    assert event == identical
    assert validate_platform_core_conversation_event(event) == event

    tampered = deepcopy(event)
    tampered["payload"]["message"] = "Changed after hashing."
    with pytest.raises(FailClosedRuntimeError, match="payload hash mismatch"):
        validate_platform_core_conversation_event(tampered)

    unexpected = deepcopy(event)
    unexpected["payload"]["semantic_decision"] = "APPROVED"
    unexpected["payload_hash"] = replay_hash(unexpected["payload"])
    unexpected["event_id"] = (
        f"G49-EVENT:TURN:000001:{HUMAN_REQUEST_SUBMITTED}:"
        f"{unexpected['payload_hash'].removeprefix('sha256:')[:16]}"
    )
    unexpected.pop("artifact_hash")
    unexpected["artifact_hash"] = replay_hash(unexpected)
    with pytest.raises(FailClosedRuntimeError, match="unsupported fields"):
        validate_platform_core_conversation_event(unexpected)


def test_runtime_entry_pending_action_uses_existing_valid_values_contract() -> None:
    runtime_state = {
        "g31_pending_action": {
            "action_type": "EXECUTION_AUTHORIZATION_DECISION",
            "valid_values": ["APPROVE", "REJECT"],
            "context": {},
        }
    }

    assert conversation_boundary._pending_runtime_actions(runtime_state) == [
        "APPROVE",
        "REJECT",
    ]


def test_boundary_projects_clarification_and_records_reference_only_evidence(
    tmp_path: Path,
) -> None:
    result = _submit(
        tmp_path=tmp_path,
        session_id="G49-CLARIFICATION",
        message="I have an idea.",
    )
    projection = result["conversation_projection"]
    manifest = load_json(Path(result["turn_evidence_manifest_reference"]))
    checkpoint = result["session_checkpoint"]

    assert result["boundary_status"] == BOUNDARY_COMPLETED
    assert projection["conversation_state"] == CLARIFICATION_AWAITING_REPLY
    assert projection["expected_event"] == CLARIFICATION_REPLY_SUBMITTED
    assert projection["next_action"] == "COLLECT_CLARIFICATION_REPLY"
    assert projection["clarification_state"]["clarification_required"] is True
    assert projection["clarification_state"]["clarification_questions"]
    assert projection["completion_state"]["completion_status"] == (
        "AWAITING_HUMAN_INPUT"
    )
    assert projection["session_close_allowed"] is False
    assert projection["ownership"]["platform_core_owns_conversation"] is True
    assert projection["ownership"]["human_interface_owns_workflow"] is False
    assert projection["boundary_flags"]["planner_modified"] is False
    assert projection["boundary_flags"]["replay_protocol_modified"] is False

    assert manifest["artifacts_embedded"] is False
    assert manifest["evidence_references"]
    assert all("artifact" not in reference for reference in manifest["evidence_references"])
    assert [item["role"] for item in manifest["evidence_references"]][:2] == [
        "EVENT",
        "PROJECT_SERVICES_CONTEXT",
    ]
    assert checkpoint["conversation_state"] == CLARIFICATION_AWAITING_REPLY
    assert checkpoint["projection_hash"] == projection["artifact_hash"]
    assert checkpoint["session_owner"] == "PLATFORM_CORE"
    assert checkpoint["interface_state_required_for_reconstruction"] is False

    validate_platform_core_conversation_projection(projection)
    validate_platform_core_conversation_turn_evidence_manifest(manifest)
    validate_platform_core_conversation_session_checkpoint(checkpoint)


def test_clarification_reply_uses_replay_state_and_reaches_existing_g47_barrier(
    tmp_path: Path,
) -> None:
    session_id = "G49-CONTINUATION"
    first = _submit(
        tmp_path=tmp_path,
        session_id=session_id,
        message="I have an idea.",
    )
    second = _submit(
        tmp_path=tmp_path,
        session_id=session_id,
        event_type=CLARIFICATION_REPLY_SUBMITTED,
        message="Implement governance validation utility.",
    )
    projection = second["conversation_projection"]
    reconstruction = reconstruct_platform_core_conversation_projection(
        runtime_root=tmp_path,
        session_id=session_id,
    )

    assert first["conversation_projection"]["conversation_state"] == (
        CLARIFICATION_AWAITING_REPLY
    )
    assert projection["conversation_state"] == APPROVAL_AWAITING_HUMAN
    assert projection["expected_event"] == HUMAN_APPROVAL_SUBMITTED
    assert projection["approval_state"]["approval_required"] is True
    assert projection["approval_summary"]["summary_authority"] == "PLATFORM_CORE"
    assert projection["approval_summary"][
        "constitutional_development_governance_planning_eligible"
    ] is True
    assert projection["approval_summary"][
        "canonical_implementation_turn_binding"
    ]
    assert reconstruction["reconstruction_verified"] is True
    assert reconstruction["reconstruction_turn_count"] == 2
    assert reconstruction["conversation_projection"] == projection
    assert reconstruction["interface_state_required"] is False


def test_grounded_question_projects_read_only_result_without_runtime_entry(
    tmp_path: Path,
) -> None:
    result = _submit(
        tmp_path=tmp_path,
        session_id="G49-READ-ONLY",
        message="What is Replay?",
    )
    projection = result["conversation_projection"]

    assert result["canonical_runtime_entry_reused"] is False
    assert projection["conversation_state"] == RESULT_DELIVERED
    assert projection["next_action"] == "DISPLAY_NON_DEVELOPMENT_RESPONSE"
    assert projection["runtime_result"]["binding_status"] == (
        "GOVERNED_READ_ONLY_WORK_BOUND"
    )
    assert projection["approval_state"]["approval_required"] is False
    assert projection["session_close_allowed"] is True


def test_human_approval_delegates_to_unchanged_runtime_entry(
    tmp_path: Path,
) -> None:
    calls: list[dict] = []
    session_id = "G49-APPROVAL"
    prepared = _submit(
        tmp_path=tmp_path,
        session_id=session_id,
        message="Implement governance validation utility.",
    )
    event = _event(
        tmp_path=tmp_path,
        session_id=session_id,
        event_type=HUMAN_APPROVAL_SUBMITTED,
        payload={"human_actor_id": "HUMAN-REVIEWER"},
        created_at="2026-07-30T00:01:00Z",
    )
    completed = run_platform_core_conversation_boundary(
        event=event,
        runtime_root=tmp_path,
        workspace=".",
        governed_runtime_runner=_successful_runtime(calls),
    )
    projection = completed["conversation_projection"]

    assert prepared["conversation_projection"]["conversation_state"] == (
        APPROVAL_AWAITING_HUMAN
    )
    assert completed["boundary_status"] == BOUNDARY_COMPLETED
    assert completed["canonical_runtime_entry_reused"] is True
    assert projection["conversation_state"] == RESULT_DELIVERED
    assert projection["completion_state"]["completion_status"] == (
        "RUNTIME_COMPLETED"
    )
    assert projection["runtime_result"]["runtime_entered"] is True
    assert projection["runtime_result"]["governance_authority_preserved"] is True
    assert projection["runtime_result"]["replay_authority_preserved"] is True
    assert calls == [
        {
            "prompt": "Implement governance validation utility.",
            "operator_context": "PLATFORM_CORE_CONVERSATION_BOUNDARY",
            "approved_binding_hash": (
                prepared["conversation_projection"]["approval_summary"][
                    "canonical_implementation_turn_binding_hash"
                ]
            ),
        }
    ]


def test_approval_without_runtime_owner_fails_closed_and_is_reconstructable(
    tmp_path: Path,
) -> None:
    session_id = "G49-APPROVAL-FAIL"
    _submit(
        tmp_path=tmp_path,
        session_id=session_id,
        message="Implement governance validation utility.",
    )
    failed = run_platform_core_conversation_boundary(
        event=_event(
            tmp_path=tmp_path,
            session_id=session_id,
            event_type=HUMAN_APPROVAL_SUBMITTED,
            payload={"human_actor_id": "HUMAN-REVIEWER"},
        ),
        runtime_root=tmp_path,
        workspace=".",
    )
    projection = failed["conversation_projection"]
    reconstructed = reconstruct_platform_core_conversation_projection(
        runtime_root=tmp_path,
        session_id=session_id,
    )

    assert failed["boundary_status"] == BOUNDARY_FAILED_CLOSED
    assert failed["canonical_runtime_entry_reused"] is False
    assert projection["conversation_state"] == CONVERSATION_FAILED_CLOSED
    assert projection["completion_state"]["completion_status"] == "FAILED_CLOSED"
    assert "governed_runtime_runner is required" in projection["user_explanation"]
    assert reconstructed["conversation_projection"] == projection


def test_eof_preserves_pending_state_and_cancel_clears_it(
    tmp_path: Path,
) -> None:
    session_id = "G49-PENDING"
    _submit(
        tmp_path=tmp_path,
        session_id=session_id,
        message="I have an idea.",
    )
    eof_result = run_platform_core_conversation_boundary(
        event=_event(
            tmp_path=tmp_path,
            session_id=session_id,
            event_type=INPUT_EOF_OBSERVED,
            payload={},
        ),
        runtime_root=tmp_path,
        workspace=".",
    )
    canceled = run_platform_core_conversation_boundary(
        event=_event(
            tmp_path=tmp_path,
            session_id=session_id,
            event_type=HUMAN_CANCEL_SUBMITTED,
            payload={"reason": "Human canceled the pending clarification."},
        ),
        runtime_root=tmp_path,
        workspace=".",
    )
    replacement = _submit(
        tmp_path=tmp_path,
        session_id=session_id,
        message="What is Replay?",
    )

    assert eof_result["conversation_projection"]["conversation_state"] == (
        CLARIFICATION_AWAITING_REPLY
    )
    assert eof_result["conversation_projection"]["next_action"] == "WAIT_FOR_HUMAN"
    assert eof_result["conversation_projection"]["session_close_allowed"] is False
    assert canceled["conversation_projection"]["conversation_state"] == (
        CONVERSATION_CANCELED
    )
    assert canceled["conversation_projection"]["terminal"] is True
    assert replacement["conversation_projection"]["conversation_state"] == (
        RESULT_DELIVERED
    )


def test_replay_restoration_is_platform_core_only_and_preserves_projection(
    tmp_path: Path,
) -> None:
    session_id = "G49-RESTORE"
    original = _submit(
        tmp_path=tmp_path,
        session_id=session_id,
        message="What is Replay?",
    )
    checkpoint = original["session_checkpoint"]
    restore_event = _event(
        tmp_path=tmp_path,
        session_id=session_id,
        event_type=REPLAY_STATE_RESTORED,
        payload={
            "checkpoint_reference": checkpoint["checkpoint_reference"],
            "checkpoint_hash": checkpoint["artifact_hash"],
        },
        source_interface="PLATFORM_CORE",
    )
    restored = run_platform_core_conversation_boundary(
        event=restore_event,
        runtime_root=tmp_path,
        workspace=".",
    )

    assert restored["conversation_projection"]["conversation_state"] == (
        original["conversation_projection"]["conversation_state"]
    )
    assert "restored the prior state" in (
        restored["conversation_projection"]["user_explanation"]
    )
    assert reconstruct_platform_core_conversation_projection(
        runtime_root=tmp_path,
        session_id=session_id,
    )["reconstruction_turn_count"] == 2


def test_reconstruction_rejects_projection_tampering(tmp_path: Path) -> None:
    session_id = "G49-TAMPER"
    result = _submit(
        tmp_path=tmp_path,
        session_id=session_id,
        message="What is Replay?",
    )
    projection_path = Path(result["conversation_projection_reference"])
    projection = json.loads(projection_path.read_text(encoding="utf-8"))
    projection["conversation_state"] = CONVERSATION_CANCELED
    projection_path.write_text(
        canonical_serialize(projection) + "\n", encoding="utf-8"
    )

    with pytest.raises(FailClosedRuntimeError, match="projection state|hash mismatch"):
        reconstruct_platform_core_conversation_projection(
            runtime_root=tmp_path,
            session_id=session_id,
        )


def test_event_not_admissible_in_active_state_is_rejected_before_persistence(
    tmp_path: Path,
) -> None:
    session_id = "G49-ADMISSIBILITY"
    _submit(
        tmp_path=tmp_path,
        session_id=session_id,
        message="I have an idea.",
    )
    invalid = _event(
        tmp_path=tmp_path,
        session_id=session_id,
        event_type=HUMAN_APPROVAL_SUBMITTED,
        payload={"human_actor_id": "HUMAN-REVIEWER"},
    )

    with pytest.raises(FailClosedRuntimeError, match="not admissible"):
        run_platform_core_conversation_boundary(
            event=invalid,
            runtime_root=tmp_path,
            workspace=".",
            governed_runtime_runner=_successful_runtime([]),
        )
    assert not (
        tmp_path
        / session_id
        / "conversation_boundary"
        / "turns"
        / "000002_turn"
    ).exists()


def test_exit_without_pending_state_allows_session_close(tmp_path: Path) -> None:
    session_id = "G49-EXIT"
    _submit(
        tmp_path=tmp_path,
        session_id=session_id,
        message="What is Replay?",
    )
    result = run_platform_core_conversation_boundary(
        event=_event(
            tmp_path=tmp_path,
            session_id=session_id,
            event_type=HUMAN_EXIT_REQUESTED,
            payload={},
        ),
        runtime_root=tmp_path,
        workspace=".",
    )

    assert result["conversation_projection"]["conversation_state"] == (
        "CONVERSATION_COMPLETED"
    )
    assert result["conversation_projection"]["session_close_allowed"] is True
    assert result["conversation_projection"]["next_action"] == (
        "CLOSE_INTERFACE_SESSION"
    )
