"""Tests for AIGOL_WORKER_INVOCATION_RUNTIME_V1."""

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
from aigol.runtime.worker_dispatch_runtime import dispatch_assigned_worker
from aigol.runtime.worker_invocation_request_runtime import create_worker_invocation_request
from aigol.runtime.worker_invocation_runtime import (
    WORKER_INVOCATION_ARTIFACT_V1,
    WORKER_INVOKED,
    invoke_dispatched_worker,
    invoke_worker,
    reconstruct_worker_invocation_replay,
)


CREATED_AT = "2026-06-04T00:00:00+00:00"
SESSION_ID = "SESSION-WORKER-INVOCATION-000001"


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


def _invoke(tmp_path, *, prompt: str, suffix: str, dispatch_capture: dict | None = None) -> dict:
    if dispatch_capture is None:
        dispatch_capture = _dispatch(tmp_path, prompt=prompt, suffix=suffix)
    return invoke_dispatched_worker(
        worker_invocation_id=f"WORKER-INVOCATION-{suffix}",
        worker_dispatch_artifact=dispatch_capture["worker_dispatch_artifact"],
        worker_dispatch_replay_reference=dispatch_capture["worker_dispatch_replay_reference"],
        invoked_by="AIGOL_GOVERNANCE",
        invoked_at=CREATED_AT,
        replay_dir=tmp_path / f"invocation_{suffix}",
    )


@pytest.mark.parametrize(
    ("prompt", "suffix"),
    [
        ("Create a filesystem worker.", "filesystem"),
        ("Create a monitoring worker.", "monitoring"),
        ("Improve trading strategy.", "trading"),
    ],
)
def test_worker_dispatched_becomes_worker_invoked(tmp_path, prompt: str, suffix: str) -> None:
    capture = _invoke(tmp_path, prompt=prompt, suffix=suffix)
    invocation = capture["worker_invocation_artifact"]
    reconstructed = reconstruct_worker_invocation_replay(tmp_path / f"invocation_{suffix}")

    assert capture["invocation_status"] == WORKER_INVOKED
    assert invocation["artifact_type"] == WORKER_INVOCATION_ARTIFACT_V1
    assert invocation["invocation_status"] == WORKER_INVOKED
    assert invocation["worker_dispatch_reference"] == f"WORKER-DISPATCH-{suffix}"
    assert invocation["worker_id"]
    assert invocation["execution_packet_reference"].endswith(":PACKET")
    assert invocation["worker_assigned"] is True
    assert invocation["worker_dispatched"] is True
    assert invocation["worker_invoked"] is True
    assert invocation["execution_started"] is False
    assert invocation["result_created"] is False
    assert invocation["result_validated"] is False
    assert invocation["post_execution_replay_reviewed"] is False
    assert invocation["terminated"] is False
    assert reconstructed["invocation_status"] == WORKER_INVOKED
    assert reconstructed["worker_id"] == invocation["worker_id"]


def test_worker_invocation_compatibility_wrapper_uses_current_chain(tmp_path) -> None:
    dispatch_capture = _dispatch(tmp_path, prompt="Create a filesystem worker.", suffix="wrapper")
    capture = invoke_worker(
        worker_invocation_id="WORKER-INVOCATION-wrapper",
        worker_dispatch_artifact=dispatch_capture["worker_dispatch_artifact"],
        worker_dispatch_replay_reference=dispatch_capture["worker_dispatch_replay_reference"],
        invoked_by="AIGOL_GOVERNANCE",
        invoked_at=CREATED_AT,
        replay_dir=tmp_path / "invocation_wrapper",
    )

    assert capture["invocation_status"] == WORKER_INVOKED


def test_worker_invocation_persists_replay_evidence(tmp_path) -> None:
    _invoke(tmp_path, prompt="Create a filesystem worker.", suffix="replay-events")

    replay_dir = tmp_path / "invocation_replay-events"
    assert (replay_dir / "000_invocation_evidence_recorded.json").exists()
    assert (replay_dir / "001_invocation_classification_recorded.json").exists()
    assert (replay_dir / "002_invocation_artifact_recorded.json").exists()
    assert (replay_dir / "003_invocation_result_recorded.json").exists()


def test_worker_invocation_fails_closed_on_dispatch_mismatch(tmp_path) -> None:
    dispatch_capture = _dispatch(tmp_path, prompt="Create a filesystem worker.", suffix="dispatch")
    dispatch = deepcopy(dispatch_capture["worker_dispatch_artifact"])
    dispatch["worker_dispatch_id"] = "OTHER-DISPATCH"
    dispatch.pop("artifact_hash")
    dispatch["artifact_hash"] = replay_hash(dispatch)
    dispatch_capture["worker_dispatch_artifact"] = dispatch

    capture = _invoke(
        tmp_path,
        prompt="Create a filesystem worker.",
        suffix="dispatch",
        dispatch_capture=dispatch_capture,
    )

    assert capture["invocation_status"] == "FAILED_CLOSED"
    assert "dispatch mismatch" in capture["failure_reason"]


def test_worker_invocation_fails_closed_on_assignment_mismatch(tmp_path) -> None:
    dispatch_capture = _dispatch(tmp_path, prompt="Create a filesystem worker.", suffix="assignment")
    dispatch = deepcopy(dispatch_capture["worker_dispatch_artifact"])
    dispatch["worker_assignment_hash"] = "sha256:assignment-mismatch"
    dispatch.pop("artifact_hash")
    dispatch["artifact_hash"] = replay_hash(dispatch)
    dispatch_capture["worker_dispatch_artifact"] = dispatch

    capture = _invoke(
        tmp_path,
        prompt="Create a filesystem worker.",
        suffix="assignment",
        dispatch_capture=dispatch_capture,
    )

    assert capture["invocation_status"] == "FAILED_CLOSED"
    assert "dispatch mismatch" in capture["failure_reason"]


def test_worker_invocation_fails_closed_on_authorization_mismatch(tmp_path) -> None:
    dispatch_capture = _dispatch(tmp_path, prompt="Create a filesystem worker.", suffix="authorization")
    dispatch = deepcopy(dispatch_capture["worker_dispatch_artifact"])
    dispatch["authorization_hash"] = "sha256:authorization-mismatch"
    dispatch.pop("artifact_hash")
    dispatch["artifact_hash"] = replay_hash(dispatch)
    dispatch_capture["worker_dispatch_artifact"] = dispatch

    capture = _invoke(
        tmp_path,
        prompt="Create a filesystem worker.",
        suffix="authorization",
        dispatch_capture=dispatch_capture,
    )

    assert capture["invocation_status"] == "FAILED_CLOSED"
    assert "dispatch mismatch" in capture["failure_reason"]


def test_worker_invocation_fails_closed_on_packet_mismatch(tmp_path) -> None:
    dispatch_capture = _dispatch(tmp_path, prompt="Create a filesystem worker.", suffix="packet")
    dispatch = deepcopy(dispatch_capture["worker_dispatch_artifact"])
    dispatch["execution_packet_reference"] = "OTHER-PACKET"
    dispatch.pop("artifact_hash")
    dispatch["artifact_hash"] = replay_hash(dispatch)
    dispatch_capture["worker_dispatch_artifact"] = dispatch

    capture = _invoke(
        tmp_path,
        prompt="Create a filesystem worker.",
        suffix="packet",
        dispatch_capture=dispatch_capture,
    )

    assert capture["invocation_status"] == "FAILED_CLOSED"
    assert "dispatch mismatch" in capture["failure_reason"]


def test_worker_invocation_fails_closed_on_worker_mismatch(tmp_path) -> None:
    dispatch_capture = _dispatch(tmp_path, prompt="Create a filesystem worker.", suffix="worker")
    dispatch = deepcopy(dispatch_capture["worker_dispatch_artifact"])
    dispatch["worker_id"] = "OTHER-WORKER"
    dispatch.pop("artifact_hash")
    dispatch["artifact_hash"] = replay_hash(dispatch)
    dispatch_capture["worker_dispatch_artifact"] = dispatch

    capture = _invoke(
        tmp_path,
        prompt="Create a filesystem worker.",
        suffix="worker",
        dispatch_capture=dispatch_capture,
    )

    assert capture["invocation_status"] == "FAILED_CLOSED"
    assert "dispatch mismatch" in capture["failure_reason"]


def test_worker_invocation_fails_closed_on_replay_corruption(tmp_path) -> None:
    dispatch_capture = _dispatch(tmp_path, prompt="Create a filesystem worker.", suffix="replay-corruption")
    replay_file = tmp_path / "dispatch_replay-corruption" / "002_dispatch_artifact_recorded.json"
    wrapper = json.loads(replay_file.read_text(encoding="utf-8"))
    wrapper["artifact"]["worker_id"] = "CORRUPTED-WORKER"
    replay_file.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    capture = _invoke(
        tmp_path,
        prompt="Create a filesystem worker.",
        suffix="replay-corruption",
        dispatch_capture=dispatch_capture,
    )

    assert capture["invocation_status"] == "FAILED_CLOSED"
    assert "hash mismatch" in capture["failure_reason"]


def test_worker_invocation_fails_closed_on_authority_violation(tmp_path) -> None:
    dispatch_capture = _dispatch(tmp_path, prompt="Create a filesystem worker.", suffix="authority")
    dispatch = deepcopy(dispatch_capture["worker_dispatch_artifact"])
    dispatch["governance_mutated"] = True
    dispatch.pop("artifact_hash")
    dispatch["artifact_hash"] = replay_hash(dispatch)
    dispatch_capture["worker_dispatch_artifact"] = dispatch

    capture = _invoke(
        tmp_path,
        prompt="Create a filesystem worker.",
        suffix="authority",
        dispatch_capture=dispatch_capture,
    )

    assert capture["invocation_status"] == "FAILED_CLOSED"
    assert "dispatch mismatch" in capture["failure_reason"]


def test_worker_invocation_fails_closed_on_chain_mismatch(tmp_path) -> None:
    dispatch_capture = _dispatch(tmp_path, prompt="Create a filesystem worker.", suffix="chain")
    dispatch = deepcopy(dispatch_capture["worker_dispatch_artifact"])
    dispatch["chain_id"] = "OTHER-CHAIN"
    dispatch.pop("artifact_hash")
    dispatch["artifact_hash"] = replay_hash(dispatch)
    dispatch_capture["worker_dispatch_artifact"] = dispatch

    capture = _invoke(
        tmp_path,
        prompt="Create a filesystem worker.",
        suffix="chain",
        dispatch_capture=dispatch_capture,
    )

    assert capture["invocation_status"] == "FAILED_CLOSED"
    assert "dispatch mismatch" in capture["failure_reason"]


def test_worker_invocation_reconstruction_detects_hash_mismatch(tmp_path) -> None:
    _invoke(tmp_path, prompt="Create a filesystem worker.", suffix="reconstruct")
    replay_file = tmp_path / "invocation_reconstruct" / "002_invocation_artifact_recorded.json"
    wrapper = json.loads(replay_file.read_text(encoding="utf-8"))
    wrapper["artifact"]["worker_id"] = "CORRUPTED-WORKER"
    replay_file.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_worker_invocation_replay(tmp_path / "invocation_reconstruct")


def test_worker_invocation_runtime_does_not_validate_results_or_terminate() -> None:
    source = inspect.getsource(invoke_dispatched_worker)

    assert "RESULT_VALIDATED" not in source
    assert "POST_EXECUTION_REPLAY_REVIEW" not in source
    assert "TERMINATED" not in source


def test_interactive_cli_reaches_worker_invocation(tmp_path) -> None:
    args = _args(tmp_path, session_id="SESSION-CLI-WORKER-INVOCATION-000001")
    output: list[str] = []

    result = run_interactive_conversation(
        args,
        input_func=_input_sequence(["Create a filesystem worker.", "exit"]),
        output_func=output.append,
    )

    assert result["worker_invoked"] is True
    assert any("Worker Invocation" in chunk for chunk in output)
    assert any("Invocation Status: WORKER_INVOKED" in chunk for chunk in output)
    assert any("No result validation yet." in chunk for chunk in output)
