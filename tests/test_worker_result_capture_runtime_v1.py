"""Tests for AIGOL_WORKER_RESULT_CAPTURE_RUNTIME_V1."""

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
from aigol.runtime.worker_invocation_runtime import invoke_dispatched_worker
from aigol.runtime.worker_result_capture_runtime import (
    WORKER_RESULT_CAPTURED,
    WORKER_RESULT_CAPTURE_ARTIFACT_V1,
    capture_worker_result,
    default_worker_output_for_invocation,
    reconstruct_worker_result_capture_replay,
)


CREATED_AT = "2026-06-04T00:00:00+00:00"
SESSION_ID = "SESSION-WORKER-RESULT-CAPTURE-000001"


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


def _dispatch(tmp_path, *, prompt: str, suffix: str) -> dict:
    assignment_capture = _assignment(tmp_path, prompt=prompt, suffix=suffix)
    return dispatch_assigned_worker(
        worker_dispatch_id=f"WORKER-DISPATCH-{suffix}",
        worker_assignment_artifact=assignment_capture["worker_assignment_artifact"],
        worker_assignment_replay_reference=assignment_capture["worker_assignment_replay_reference"],
        dispatched_by="AIGOL_GOVERNANCE",
        dispatched_at=CREATED_AT,
        replay_dir=tmp_path / f"dispatch_{suffix}",
    )


def _invoke(tmp_path, *, prompt: str, suffix: str, invocation_capture: dict | None = None) -> dict:
    if invocation_capture is not None:
        return invocation_capture
    dispatch_capture = _dispatch(tmp_path, prompt=prompt, suffix=suffix)
    return invoke_dispatched_worker(
        worker_invocation_id=f"WORKER-INVOCATION-{suffix}",
        worker_dispatch_artifact=dispatch_capture["worker_dispatch_artifact"],
        worker_dispatch_replay_reference=dispatch_capture["worker_dispatch_replay_reference"],
        invoked_by="AIGOL_GOVERNANCE",
        invoked_at=CREATED_AT,
        replay_dir=tmp_path / f"invocation_{suffix}",
    )


def _capture(tmp_path, *, prompt: str, suffix: str, invocation_capture: dict | None = None, worker_output: dict | None = None) -> dict:
    invocation_capture = _invoke(tmp_path, prompt=prompt, suffix=suffix, invocation_capture=invocation_capture)
    invocation = invocation_capture["worker_invocation_artifact"]
    if worker_output is None:
        worker_output = default_worker_output_for_invocation(invocation, captured_at=CREATED_AT)
    return capture_worker_result(
        worker_result_capture_id=f"WORKER-RESULT-CAPTURE-{suffix}",
        worker_invocation_artifact=invocation,
        worker_invocation_replay_reference=invocation_capture["worker_invocation_replay_reference"],
        worker_output=worker_output,
        captured_by="AIGOL_GOVERNANCE",
        captured_at=CREATED_AT,
        replay_dir=tmp_path / f"result_capture_{suffix}",
    )


@pytest.mark.parametrize(
    ("prompt", "suffix"),
    [
        ("Create a filesystem worker.", "filesystem"),
        ("Create a monitoring worker.", "monitoring"),
        ("Improve trading strategy.", "trading"),
    ],
)
def test_worker_invoked_becomes_worker_result_captured(tmp_path, prompt: str, suffix: str) -> None:
    result = _capture(tmp_path, prompt=prompt, suffix=suffix)
    artifact = result["worker_result_capture_artifact"]
    reconstructed = reconstruct_worker_result_capture_replay(tmp_path / f"result_capture_{suffix}")

    assert result["result_capture_status"] == WORKER_RESULT_CAPTURED
    assert artifact["artifact_type"] == WORKER_RESULT_CAPTURE_ARTIFACT_V1
    assert artifact["result_capture_status"] == WORKER_RESULT_CAPTURED
    assert artifact["worker_invocation_reference"] == f"WORKER-INVOCATION-{suffix}"
    assert artifact["worker_id"]
    assert artifact["worker_result_captured"] is True
    assert artifact["result_created"] is True
    assert artifact["result_validated"] is False
    assert artifact["post_execution_replay_reviewed"] is False
    assert artifact["terminated"] is False
    assert set(artifact["produced_outputs"]).issubset(set(artifact["allowed_outputs"]))
    assert reconstructed["result_capture_status"] == WORKER_RESULT_CAPTURED
    assert reconstructed["worker_id"] == artifact["worker_id"]


def test_worker_result_capture_persists_replay_events(tmp_path) -> None:
    _capture(tmp_path, prompt="Create a filesystem worker.", suffix="replay-events")

    replay_dir = tmp_path / "result_capture_replay-events"
    assert (replay_dir / "000_result_capture_evidence_recorded.json").exists()
    assert (replay_dir / "001_result_capture_classification_recorded.json").exists()
    assert (replay_dir / "002_result_capture_artifact_recorded.json").exists()
    assert (replay_dir / "003_result_capture_result_recorded.json").exists()


def test_worker_result_capture_fails_closed_on_output_outside_allowed_scope(tmp_path) -> None:
    invocation_capture = _invoke(tmp_path, prompt="Create a filesystem worker.", suffix="outside-scope")
    output = default_worker_output_for_invocation(invocation_capture["worker_invocation_artifact"], captured_at=CREATED_AT)
    output["produced_outputs"] = ["governance/UNAUTHORIZED.md"]
    output.pop("artifact_hash")
    output["artifact_hash"] = replay_hash(output)

    result = _capture(
        tmp_path,
        prompt="Create a filesystem worker.",
        suffix="outside-scope",
        invocation_capture=invocation_capture,
        worker_output=output,
    )

    assert result["result_capture_status"] == "FAILED_CLOSED"
    assert "output outside allowed scope" in result["failure_reason"]


def test_worker_result_capture_fails_closed_on_forbidden_operation(tmp_path) -> None:
    invocation_capture = _invoke(tmp_path, prompt="Create a filesystem worker.", suffix="forbidden-operation")
    invocation = invocation_capture["worker_invocation_artifact"]
    output = default_worker_output_for_invocation(invocation, captured_at=CREATED_AT)
    output["operations"] = [invocation["forbidden_operations"][0]]
    output.pop("artifact_hash")
    output["artifact_hash"] = replay_hash(output)

    result = _capture(
        tmp_path,
        prompt="Create a filesystem worker.",
        suffix="forbidden-operation",
        invocation_capture=invocation_capture,
        worker_output=output,
    )

    assert result["result_capture_status"] == "FAILED_CLOSED"
    assert "forbidden operation detected" in result["failure_reason"]


def test_worker_result_capture_fails_closed_on_worker_mismatch(tmp_path) -> None:
    invocation_capture = _invoke(tmp_path, prompt="Create a filesystem worker.", suffix="worker-mismatch")
    output = default_worker_output_for_invocation(invocation_capture["worker_invocation_artifact"], captured_at=CREATED_AT)
    output["worker_id"] = "OTHER-WORKER"
    output.pop("artifact_hash")
    output["artifact_hash"] = replay_hash(output)

    result = _capture(
        tmp_path,
        prompt="Create a filesystem worker.",
        suffix="worker-mismatch",
        invocation_capture=invocation_capture,
        worker_output=output,
    )

    assert result["result_capture_status"] == "FAILED_CLOSED"
    assert "worker mismatch" in result["failure_reason"]


def test_worker_result_capture_fails_closed_on_replay_corruption(tmp_path) -> None:
    invocation_capture = _invoke(tmp_path, prompt="Create a filesystem worker.", suffix="replay-corruption")
    replay_file = tmp_path / "invocation_replay-corruption" / "002_invocation_artifact_recorded.json"
    wrapper = json.loads(replay_file.read_text(encoding="utf-8"))
    wrapper["artifact"]["worker_id"] = "CORRUPTED-WORKER"
    replay_file.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    result = _capture(
        tmp_path,
        prompt="Create a filesystem worker.",
        suffix="replay-corruption",
        invocation_capture=invocation_capture,
    )

    assert result["result_capture_status"] == "FAILED_CLOSED"
    assert "hash mismatch" in result["failure_reason"]


def test_worker_result_capture_fails_closed_on_chain_mismatch(tmp_path) -> None:
    invocation_capture = _invoke(tmp_path, prompt="Create a filesystem worker.", suffix="chain-mismatch")
    output = default_worker_output_for_invocation(invocation_capture["worker_invocation_artifact"], captured_at=CREATED_AT)
    output["chain_id"] = "OTHER-CHAIN"
    output.pop("artifact_hash")
    output["artifact_hash"] = replay_hash(output)

    result = _capture(
        tmp_path,
        prompt="Create a filesystem worker.",
        suffix="chain-mismatch",
        invocation_capture=invocation_capture,
        worker_output=output,
    )

    assert result["result_capture_status"] == "FAILED_CLOSED"
    assert "chain mismatch" in result["failure_reason"]


def test_worker_result_capture_fails_closed_on_authority_violation(tmp_path) -> None:
    invocation_capture = _invoke(tmp_path, prompt="Create a filesystem worker.", suffix="authority")
    output = default_worker_output_for_invocation(invocation_capture["worker_invocation_artifact"], captured_at=CREATED_AT)
    output["result_validated"] = True
    output.pop("artifact_hash")
    output["artifact_hash"] = replay_hash(output)

    result = _capture(
        tmp_path,
        prompt="Create a filesystem worker.",
        suffix="authority",
        invocation_capture=invocation_capture,
        worker_output=output,
    )

    assert result["result_capture_status"] == "FAILED_CLOSED"
    assert "authority violation" in result["failure_reason"]


def test_worker_result_capture_reconstruction_detects_hash_mismatch(tmp_path) -> None:
    _capture(tmp_path, prompt="Create a filesystem worker.", suffix="reconstruct")
    replay_file = tmp_path / "result_capture_reconstruct" / "002_result_capture_artifact_recorded.json"
    wrapper = json.loads(replay_file.read_text(encoding="utf-8"))
    wrapper["artifact"]["worker_id"] = "CORRUPTED-WORKER"
    replay_file.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_worker_result_capture_replay(tmp_path / "result_capture_reconstruct")


def test_worker_result_capture_runtime_does_not_validate_or_terminate() -> None:
    source = inspect.getsource(capture_worker_result)

    assert "RESULT_VALIDATED" not in source
    assert "POST_EXECUTION_REPLAY_REVIEW" not in source
    assert "TERMINATED" not in source


def test_interactive_cli_reaches_worker_result_capture(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _args(tmp_path, session_id="SESSION-CLI-WORKER-RESULT-CAPTURE-000001"),
        input_func=_input_sequence(["Create a filesystem worker.", "exit"]),
        output_func=output.append,
    )

    assert result["worker_result_captured"] is True
    assert any("Worker Result Capture" in chunk for chunk in output)
    assert any("Result Capture Status: WORKER_RESULT_CAPTURED" in chunk for chunk in output)
    assert any("No semantic validation yet." in chunk for chunk in output)
