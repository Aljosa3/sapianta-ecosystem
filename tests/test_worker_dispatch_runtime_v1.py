"""Tests for AIGOL_WORKER_DISPATCH_RUNTIME_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect
import json

import pytest

from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.runtime.conversation_native_development_intent_routing import (
    run_conversation_native_development_intent_routing,
)
from aigol.runtime.conversation_session_resume_runtime import resume_conversation_session
from aigol.runtime.conversation_to_ppp_handoff_execution import (
    HUMAN_APPROVAL_REQUIRED,
    run_conversation_to_ppp_handoff_execution,
)
from aigol.runtime.execution_authorization_runtime import authorize_execution_ready
from aigol.runtime.governed_implementation_dry_run import prepare_governed_implementation_dry_run
from aigol.runtime.implementation_approval_resume import (
    create_human_implementation_approval,
    resume_implementation_after_approval,
)
from aigol.runtime.implementation_handoff_visibility import create_implementation_handoff_visibility_summary
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash
from aigol.runtime.worker_assignment_runtime import (
    assign_worker_from_invocation_request,
    default_worker_registry_for_request,
)
from aigol.runtime.worker_dispatch_runtime import (
    WORKER_DISPATCHED,
    WORKER_DISPATCH_ARTIFACT_V1,
    dispatch_assigned_worker,
    reconstruct_worker_dispatch_replay,
)
from aigol.runtime.worker_invocation_request_runtime import create_worker_invocation_request


CREATED_AT = "2026-06-04T00:00:00+00:00"
SESSION_ID = "SESSION-WORKER-DISPATCH-000001"


def _args(tmp_path, *, session_id: str):
    parser = build_parser()
    return parser.parse_args(
        [
            "conversation",
            "--session-id",
            session_id,
            "--created-at",
            CREATED_AT,
            "--runtime-root",
            str(tmp_path / "interactive_runtime"),
        ]
    )


def _input_sequence(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


def _ppp_capture(tmp_path, *, prompt: str, suffix: str):
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


def _execution_ready(tmp_path, *, prompt: str, suffix: str):
    ppp = _ppp_capture(tmp_path, prompt=prompt, suffix=suffix)
    upstream = ppp["conversation_to_ppp_handoff_execution_artifact"]
    handoff_replay_reference = ppp.get("handoff_replay_reference")
    approval_status = ppp["approval_status"]
    if ppp["terminal_status"] == HUMAN_APPROVAL_REQUIRED:
        request = upstream["approval_resume_packet"]["approval_request_artifact"]
        approval = create_human_implementation_approval(
            approval_id=f"HUMAN-APPROVAL-{suffix}",
            approval_request_artifact=request,
            approving_actor="human.operator",
            approval_timestamp=CREATED_AT,
        )
        resumed = resume_implementation_after_approval(
            resume_id=f"APPROVAL-RESUME-{suffix}",
            approval_required_replay_reference=ppp["conversation_to_ppp_handoff_execution_replay_reference"],
            human_approval_artifact=approval,
            created_at=CREATED_AT,
            replay_dir=tmp_path / f"approval_resume_{suffix}",
        )
        upstream = resumed["implementation_approval_resume_artifact"]
        handoff_replay_reference = resumed["implementation_handoff_replay_reference"]
        approval_status = "APPROVED"
    visibility = create_implementation_handoff_visibility_summary(
        visibility_id=f"VISIBILITY-{suffix}",
        handoff_replay_reference=handoff_replay_reference,
        approval_status=approval_status,
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"visibility_{suffix}",
    )
    return prepare_governed_implementation_dry_run(
        dry_run_id=f"DRY-RUN-{suffix}",
        handoff_replay_reference=handoff_replay_reference,
        handoff_visibility_artifact=visibility["implementation_handoff_visibility_artifact"],
        upstream_lineage_artifact=upstream,
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"dry_run_{suffix}",
    )


def _authorization(tmp_path, *, prompt: str, suffix: str) -> dict:
    ready = _execution_ready(tmp_path, prompt=prompt, suffix=suffix)
    return authorize_execution_ready(
        authorization_id=f"AUTHORIZATION-{suffix}",
        execution_ready_replay_reference=ready["governed_implementation_dry_run_replay_reference"],
        authorizing_actor="AIGOL_GOVERNANCE",
        authorized_at=CREATED_AT,
        replay_dir=tmp_path / f"authorization_{suffix}",
    )


def _invocation_request(tmp_path, *, prompt: str, suffix: str) -> dict:
    authorization = _authorization(tmp_path, prompt=prompt, suffix=suffix)
    return create_worker_invocation_request(
        invocation_request_id=f"WORKER-INVOCATION-REQUEST-{suffix}",
        execution_authorization_replay_reference=authorization["execution_authorization_replay_reference"],
        requested_by="AIGOL_GOVERNANCE",
        requested_at=CREATED_AT,
        replay_dir=tmp_path / f"invocation_request_{suffix}",
    )


def _assignment(tmp_path, *, prompt: str, suffix: str) -> dict:
    request_capture = _invocation_request(tmp_path, prompt=prompt, suffix=suffix)
    request = request_capture["worker_invocation_request_artifact"]
    return assign_worker_from_invocation_request(
        worker_assignment_id=f"WORKER-ASSIGNMENT-{suffix}",
        worker_invocation_request_artifact=request,
        worker_invocation_request_replay_reference=request_capture["worker_invocation_request_replay_reference"],
        worker_registry_artifacts=default_worker_registry_for_request(request, created_at=CREATED_AT),
        assigned_by="AIGOL_GOVERNANCE",
        assigned_at=CREATED_AT,
        replay_dir=tmp_path / f"assignment_{suffix}",
    )


def _dispatch(tmp_path, *, prompt: str, suffix: str, assignment_capture: dict | None = None) -> dict:
    if assignment_capture is None:
        assignment_capture = _assignment(tmp_path, prompt=prompt, suffix=suffix)
    return dispatch_assigned_worker(
        worker_dispatch_id=f"WORKER-DISPATCH-{suffix}",
        worker_assignment_artifact=assignment_capture["worker_assignment_artifact"],
        worker_assignment_replay_reference=assignment_capture["worker_assignment_replay_reference"],
        dispatched_by="AIGOL_GOVERNANCE",
        dispatched_at=CREATED_AT,
        replay_dir=tmp_path / f"dispatch_{suffix}",
    )


@pytest.mark.parametrize(
    ("prompt", "suffix"),
    [
        ("Create a filesystem worker.", "filesystem"),
        ("Create a monitoring worker.", "monitoring"),
        ("Improve trading strategy.", "trading"),
    ],
)
def test_worker_assigned_becomes_worker_dispatched(tmp_path, prompt: str, suffix: str) -> None:
    capture = _dispatch(tmp_path, prompt=prompt, suffix=suffix)
    dispatch = capture["worker_dispatch_artifact"]
    reconstructed = reconstruct_worker_dispatch_replay(tmp_path / f"dispatch_{suffix}")

    assert capture["dispatch_status"] == WORKER_DISPATCHED
    assert dispatch["artifact_type"] == WORKER_DISPATCH_ARTIFACT_V1
    assert dispatch["dispatch_status"] == WORKER_DISPATCHED
    assert dispatch["worker_assignment_reference"] == f"WORKER-ASSIGNMENT-{suffix}"
    assert dispatch["worker_id"]
    assert dispatch["execution_packet_reference"].endswith(":PACKET")
    assert dispatch["worker_assigned"] is True
    assert dispatch["worker_dispatched"] is True
    assert dispatch["worker_invoked"] is False
    assert dispatch["execution_started"] is False
    assert dispatch["result_created"] is False
    assert reconstructed["dispatch_status"] == WORKER_DISPATCHED
    assert reconstructed["worker_id"] == dispatch["worker_id"]


def test_worker_dispatch_persists_replay_evidence(tmp_path) -> None:
    _dispatch(tmp_path, prompt="Create a filesystem worker.", suffix="replay-events")

    replay_dir = tmp_path / "dispatch_replay-events"
    assert (replay_dir / "000_dispatch_evidence_recorded.json").exists()
    assert (replay_dir / "001_dispatch_classification_recorded.json").exists()
    assert (replay_dir / "002_dispatch_artifact_recorded.json").exists()
    assert (replay_dir / "003_dispatch_result_recorded.json").exists()


def test_worker_dispatch_fails_closed_on_worker_identity_mismatch(tmp_path) -> None:
    assignment_capture = _assignment(tmp_path, prompt="Create a filesystem worker.", suffix="identity")
    assignment = deepcopy(assignment_capture["worker_assignment_artifact"])
    assignment["worker_id"] = "OTHER-WORKER"
    assignment.pop("artifact_hash")
    assignment["artifact_hash"] = replay_hash(assignment)
    assignment_capture["worker_assignment_artifact"] = assignment

    capture = _dispatch(
        tmp_path,
        prompt="Create a filesystem worker.",
        suffix="identity",
        assignment_capture=assignment_capture,
    )

    assert capture["dispatch_status"] == "FAILED_CLOSED"
    assert "assignment mismatch" in capture["failure_reason"]


def test_worker_dispatch_fails_closed_on_assignment_mismatch(tmp_path) -> None:
    assignment_capture = _assignment(tmp_path, prompt="Create a filesystem worker.", suffix="assignment")
    assignment = deepcopy(assignment_capture["worker_assignment_artifact"])
    assignment["worker_assignment_id"] = "OTHER-ASSIGNMENT"
    assignment.pop("artifact_hash")
    assignment["artifact_hash"] = replay_hash(assignment)
    assignment_capture["worker_assignment_artifact"] = assignment

    capture = _dispatch(
        tmp_path,
        prompt="Create a filesystem worker.",
        suffix="assignment",
        assignment_capture=assignment_capture,
    )

    assert capture["dispatch_status"] == "FAILED_CLOSED"
    assert "assignment mismatch" in capture["failure_reason"]


def test_worker_dispatch_fails_closed_on_packet_mismatch(tmp_path) -> None:
    assignment_capture = _assignment(tmp_path, prompt="Create a filesystem worker.", suffix="packet")
    assignment = deepcopy(assignment_capture["worker_assignment_artifact"])
    assignment["execution_packet_reference"] = "OTHER-PACKET"
    assignment.pop("artifact_hash")
    assignment["artifact_hash"] = replay_hash(assignment)
    assignment_capture["worker_assignment_artifact"] = assignment

    capture = _dispatch(
        tmp_path,
        prompt="Create a filesystem worker.",
        suffix="packet",
        assignment_capture=assignment_capture,
    )

    assert capture["dispatch_status"] == "FAILED_CLOSED"
    assert "assignment mismatch" in capture["failure_reason"]


def test_worker_dispatch_fails_closed_on_authority_violation(tmp_path) -> None:
    assignment_capture = _assignment(tmp_path, prompt="Create a filesystem worker.", suffix="authority")
    assignment = deepcopy(assignment_capture["worker_assignment_artifact"])
    assignment["worker_invoked"] = True
    assignment.pop("artifact_hash")
    assignment["artifact_hash"] = replay_hash(assignment)
    assignment_capture["worker_assignment_artifact"] = assignment

    capture = _dispatch(
        tmp_path,
        prompt="Create a filesystem worker.",
        suffix="authority",
        assignment_capture=assignment_capture,
    )

    assert capture["dispatch_status"] == "FAILED_CLOSED"
    assert "assignment mismatch" in capture["failure_reason"]


def test_worker_dispatch_reconstruction_detects_replay_corruption(tmp_path) -> None:
    _dispatch(tmp_path, prompt="Create a filesystem worker.", suffix="corrupt")
    path = tmp_path / "dispatch_corrupt" / "002_dispatch_artifact_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["worker_invoked"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_worker_dispatch_replay(tmp_path / "dispatch_corrupt")


def test_worker_dispatch_reconstruction_detects_chain_mismatch(tmp_path) -> None:
    _dispatch(tmp_path, prompt="Create a filesystem worker.", suffix="chain")
    path = tmp_path / "dispatch_chain" / "003_dispatch_result_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["chain_id"] = "OTHER-CHAIN"
    wrapper["artifact"].pop("artifact_hash")
    wrapper["artifact"]["artifact_hash"] = replay_hash(wrapper["artifact"])
    wrapper.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="chain mismatch"):
        reconstruct_worker_dispatch_replay(tmp_path / "dispatch_chain")


def test_cli_acceptance_flows_reach_worker_dispatched(tmp_path) -> None:
    filesystem_output: list[str] = []
    filesystem = run_interactive_conversation(
        _args(tmp_path, session_id="SESSION-DISPATCH-CLI-FILESYSTEM"),
        input_func=_input_sequence(["Create a filesystem worker.", "exit"]),
        output_func=filesystem_output.append,
    )
    trading_output: list[str] = []
    trading = run_interactive_conversation(
        _args(tmp_path, session_id="SESSION-DISPATCH-CLI-TRADING"),
        input_func=_input_sequence(["Improve trading strategy.", "Approve.", "exit"]),
        output_func=trading_output.append,
    )

    assert filesystem["turns"][0]["worker_dispatch_status"] == WORKER_DISPATCHED
    assert filesystem["worker_dispatched"] is True
    assert filesystem["worker_invoked"] is False
    assert "Dispatch Status: WORKER_DISPATCHED" in filesystem_output[0]
    assert "No Worker has been invoked, executed, or produced results." in filesystem_output[0]
    assert trading["turns"][1]["worker_dispatch_status"] == WORKER_DISPATCHED
    assert trading["worker_dispatched"] is True
    assert "Dispatch Status: WORKER_DISPATCHED" in trading_output[1]


def test_worker_dispatch_runtime_preserves_authority_boundaries() -> None:
    import aigol.runtime.worker_dispatch_runtime as runtime

    source = inspect.getsource(runtime)

    assert "invoke_worker(" not in source
    assert "execute_worker(" not in source
    assert "create_result(" not in source
    assert "create_human_implementation_approval(" not in source
    assert "mutate_governance(" not in source
    assert "subprocess" not in source
    assert "requests" not in source
