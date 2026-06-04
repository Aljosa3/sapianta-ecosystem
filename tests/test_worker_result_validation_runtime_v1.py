"""Tests for AIGOL_WORKER_RESULT_VALIDATION_RUNTIME_V1."""

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
    capture_worker_result,
    default_worker_output_for_invocation,
)
from aigol.runtime.worker_result_validation_runtime import (
    RESULT_VALIDATED,
    WORKER_RESULT_VALIDATION_ARTIFACT_V1,
    reconstruct_worker_result_validation_replay,
    validate_worker_result,
)


CREATED_AT = "2026-06-04T00:00:00+00:00"
SESSION_ID = "SESSION-WORKER-RESULT-VALIDATION-000001"


def _args(tmp_path, *, session_id: str):
    (tmp_path / "governance").mkdir(exist_ok=True)
    (tmp_path / "aigol" / "runtime").mkdir(parents=True, exist_ok=True)
    (tmp_path / "tests").mkdir(exist_ok=True)
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
            "--workspace",
            str(tmp_path),
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


def _invoke(tmp_path, *, prompt: str, suffix: str) -> dict:
    dispatch_capture = _dispatch(tmp_path, prompt=prompt, suffix=suffix)
    return invoke_dispatched_worker(
        worker_invocation_id=f"WORKER-INVOCATION-{suffix}",
        worker_dispatch_artifact=dispatch_capture["worker_dispatch_artifact"],
        worker_dispatch_replay_reference=dispatch_capture["worker_dispatch_replay_reference"],
        invoked_by="AIGOL_GOVERNANCE",
        invoked_at=CREATED_AT,
        replay_dir=tmp_path / f"invocation_{suffix}",
    )


def _result_capture(tmp_path, *, prompt: str, suffix: str) -> dict:
    invocation_capture = _invoke(tmp_path, prompt=prompt, suffix=suffix)
    invocation = invocation_capture["worker_invocation_artifact"]
    return capture_worker_result(
        worker_result_capture_id=f"WORKER-RESULT-CAPTURE-{suffix}",
        worker_invocation_artifact=invocation,
        worker_invocation_replay_reference=invocation_capture["worker_invocation_replay_reference"],
        worker_output=default_worker_output_for_invocation(invocation, captured_at=CREATED_AT),
        captured_by="AIGOL_GOVERNANCE",
        captured_at=CREATED_AT,
        replay_dir=tmp_path / f"result_capture_{suffix}",
    )


def _validate(tmp_path, *, prompt: str, suffix: str, capture: dict | None = None) -> dict:
    if capture is None:
        capture = _result_capture(tmp_path, prompt=prompt, suffix=suffix)
    return validate_worker_result(
        worker_result_validation_id=f"WORKER-RESULT-VALIDATION-{suffix}",
        worker_result_capture_artifact=capture["worker_result_capture_artifact"],
        worker_result_capture_replay_reference=capture["worker_result_capture_replay_reference"],
        validated_by="AIGOL_GOVERNANCE",
        validated_at=CREATED_AT,
        replay_dir=tmp_path / f"result_validation_{suffix}",
    )


def _replace_result_capture_replay_artifact(tmp_path, *, suffix: str, artifact: dict) -> dict:
    artifact = deepcopy(artifact)
    artifact.pop("artifact_hash", None)
    artifact["artifact_hash"] = replay_hash(artifact)
    artifact_path = tmp_path / f"result_capture_{suffix}" / "002_result_capture_artifact_recorded.json"
    wrapper = json.loads(artifact_path.read_text(encoding="utf-8"))
    wrapper["artifact"] = artifact
    wrapper.pop("replay_hash", None)
    wrapper["replay_hash"] = replay_hash(wrapper)
    artifact_path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    result_path = tmp_path / f"result_capture_{suffix}" / "003_result_capture_result_recorded.json"
    result_wrapper = json.loads(result_path.read_text(encoding="utf-8"))
    result_wrapper["artifact"]["worker_result_capture_hash"] = artifact["artifact_hash"]
    result_wrapper["artifact"].pop("artifact_hash", None)
    result_wrapper["artifact"]["artifact_hash"] = replay_hash(result_wrapper["artifact"])
    result_wrapper.pop("replay_hash", None)
    result_wrapper["replay_hash"] = replay_hash(result_wrapper)
    result_path.write_text(canonical_serialize(result_wrapper) + "\n", encoding="utf-8")
    return artifact


@pytest.mark.parametrize(
    ("prompt", "suffix"),
    [
        ("Create a filesystem worker.", "filesystem"),
        ("Create a monitoring worker.", "monitoring"),
        ("Improve trading strategy.", "trading"),
    ],
)
def test_worker_result_captured_becomes_result_validated(tmp_path, prompt: str, suffix: str) -> None:
    result = _validate(tmp_path, prompt=prompt, suffix=suffix)
    artifact = result["worker_result_validation_artifact"]
    reconstructed = reconstruct_worker_result_validation_replay(tmp_path / f"result_validation_{suffix}")

    assert result["validation_status"] == RESULT_VALIDATED
    assert artifact["artifact_type"] == WORKER_RESULT_VALIDATION_ARTIFACT_V1
    assert artifact["validation_status"] == RESULT_VALIDATED
    assert artifact["worker_result_capture_reference"] == f"WORKER-RESULT-CAPTURE-{suffix}"
    assert artifact["worker_id"]
    assert artifact["result_validated"] is True
    assert artifact["post_execution_replay_reviewed"] is False
    assert artifact["terminated"] is False
    assert set(artifact["produced_outputs"]).issubset(set(artifact["allowed_outputs"]))
    assert reconstructed["validation_status"] == RESULT_VALIDATED
    assert reconstructed["worker_id"] == artifact["worker_id"]


def test_worker_result_validation_persists_replay_events(tmp_path) -> None:
    _validate(tmp_path, prompt="Create a filesystem worker.", suffix="replay-events")

    replay_dir = tmp_path / "result_validation_replay-events"
    assert (replay_dir / "000_validation_evidence_recorded.json").exists()
    assert (replay_dir / "001_validation_classification_recorded.json").exists()
    assert (replay_dir / "002_validation_artifact_recorded.json").exists()
    assert (replay_dir / "003_validation_result_recorded.json").exists()


def test_worker_result_validation_fails_closed_on_output_outside_allowed_scope(tmp_path) -> None:
    capture = _result_capture(tmp_path, prompt="Create a filesystem worker.", suffix="outside-scope")
    artifact = deepcopy(capture["worker_result_capture_artifact"])
    artifact["produced_outputs"] = ["governance/UNAUTHORIZED.md"]
    artifact = _replace_result_capture_replay_artifact(tmp_path, suffix="outside-scope", artifact=artifact)
    capture["worker_result_capture_artifact"] = artifact

    result = _validate(tmp_path, prompt="Create a filesystem worker.", suffix="outside-scope", capture=capture)

    assert result["validation_status"] == "FAILED_CLOSED"
    assert "output outside allowed scope" in result["failure_reason"]


def test_worker_result_validation_fails_closed_on_forbidden_operation(tmp_path) -> None:
    capture = _result_capture(tmp_path, prompt="Create a filesystem worker.", suffix="forbidden-operation")
    artifact = deepcopy(capture["worker_result_capture_artifact"])
    artifact["operations"] = [artifact["forbidden_operations"][0]]
    artifact = _replace_result_capture_replay_artifact(tmp_path, suffix="forbidden-operation", artifact=artifact)
    capture["worker_result_capture_artifact"] = artifact

    result = _validate(tmp_path, prompt="Create a filesystem worker.", suffix="forbidden-operation", capture=capture)

    assert result["validation_status"] == "FAILED_CLOSED"
    assert "forbidden operation detected" in result["failure_reason"]


def test_worker_result_validation_fails_closed_on_missing_validation_requirement(tmp_path) -> None:
    capture = _result_capture(tmp_path, prompt="Create a filesystem worker.", suffix="missing-requirement")
    artifact = deepcopy(capture["worker_result_capture_artifact"])
    artifact["validation_requirements"] = []
    artifact = _replace_result_capture_replay_artifact(tmp_path, suffix="missing-requirement", artifact=artifact)
    capture["worker_result_capture_artifact"] = artifact

    result = _validate(tmp_path, prompt="Create a filesystem worker.", suffix="missing-requirement", capture=capture)

    assert result["validation_status"] == "FAILED_CLOSED"
    assert "validation requirements missing" in result["failure_reason"]


def test_worker_result_validation_fails_closed_on_worker_mismatch(tmp_path) -> None:
    capture = _result_capture(tmp_path, prompt="Create a filesystem worker.", suffix="worker-mismatch")
    artifact = deepcopy(capture["worker_result_capture_artifact"])
    artifact["worker_id"] = "OTHER-WORKER"
    artifact.pop("artifact_hash")
    artifact["artifact_hash"] = replay_hash(artifact)
    capture["worker_result_capture_artifact"] = artifact

    result = _validate(tmp_path, prompt="Create a filesystem worker.", suffix="worker-mismatch", capture=capture)

    assert result["validation_status"] == "FAILED_CLOSED"
    assert "result capture mismatch" in result["failure_reason"]


def test_worker_result_validation_fails_closed_on_packet_mismatch(tmp_path) -> None:
    capture = _result_capture(tmp_path, prompt="Create a filesystem worker.", suffix="packet-mismatch")
    artifact = deepcopy(capture["worker_result_capture_artifact"])
    artifact["execution_packet_reference"] = "OTHER-PACKET"
    artifact.pop("artifact_hash")
    artifact["artifact_hash"] = replay_hash(artifact)
    capture["worker_result_capture_artifact"] = artifact

    result = _validate(tmp_path, prompt="Create a filesystem worker.", suffix="packet-mismatch", capture=capture)

    assert result["validation_status"] == "FAILED_CLOSED"
    assert "result capture mismatch" in result["failure_reason"]


def test_worker_result_validation_fails_closed_on_replay_corruption(tmp_path) -> None:
    capture = _result_capture(tmp_path, prompt="Create a filesystem worker.", suffix="replay-corruption")
    replay_file = tmp_path / "result_capture_replay-corruption" / "002_result_capture_artifact_recorded.json"
    wrapper = json.loads(replay_file.read_text(encoding="utf-8"))
    wrapper["artifact"]["worker_id"] = "CORRUPTED-WORKER"
    replay_file.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    result = _validate(tmp_path, prompt="Create a filesystem worker.", suffix="replay-corruption", capture=capture)

    assert result["validation_status"] == "FAILED_CLOSED"
    assert "hash mismatch" in result["failure_reason"]


def test_worker_result_validation_fails_closed_on_chain_mismatch(tmp_path) -> None:
    capture = _result_capture(tmp_path, prompt="Create a filesystem worker.", suffix="chain-mismatch")
    artifact = deepcopy(capture["worker_result_capture_artifact"])
    artifact["chain_id"] = "OTHER-CHAIN"
    artifact.pop("artifact_hash")
    artifact["artifact_hash"] = replay_hash(artifact)
    capture["worker_result_capture_artifact"] = artifact

    result = _validate(tmp_path, prompt="Create a filesystem worker.", suffix="chain-mismatch", capture=capture)

    assert result["validation_status"] == "FAILED_CLOSED"
    assert "result capture mismatch" in result["failure_reason"]


def test_worker_result_validation_fails_closed_on_authority_violation(tmp_path) -> None:
    capture = _result_capture(tmp_path, prompt="Create a filesystem worker.", suffix="authority")
    artifact = deepcopy(capture["worker_result_capture_artifact"])
    artifact["governance_mutated"] = True
    artifact.pop("artifact_hash")
    artifact["artifact_hash"] = replay_hash(artifact)
    capture["worker_result_capture_artifact"] = artifact

    result = _validate(tmp_path, prompt="Create a filesystem worker.", suffix="authority", capture=capture)

    assert result["validation_status"] == "FAILED_CLOSED"
    assert "result capture mismatch" in result["failure_reason"]


def test_worker_result_validation_reconstruction_detects_hash_mismatch(tmp_path) -> None:
    _validate(tmp_path, prompt="Create a filesystem worker.", suffix="reconstruct")
    replay_file = tmp_path / "result_validation_reconstruct" / "002_validation_artifact_recorded.json"
    wrapper = json.loads(replay_file.read_text(encoding="utf-8"))
    wrapper["artifact"]["worker_id"] = "CORRUPTED-WORKER"
    replay_file.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_worker_result_validation_replay(tmp_path / "result_validation_reconstruct")


def test_worker_result_validation_runtime_does_not_approve_review_or_terminate() -> None:
    source = inspect.getsource(validate_worker_result)

    assert "APPROVED" not in source
    assert "POST_EXECUTION_REPLAY_REVIEW" not in source
    assert "TERMINATED" not in source
    assert "create_work" not in source


def test_interactive_cli_reaches_worker_result_validation(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _args(tmp_path, session_id="SESSION-CLI-WORKER-RESULT-VALIDATION-000001"),
        input_func=_input_sequence(["Create a filesystem worker.", "exit"]),
        output_func=output.append,
    )

    assert result["worker_result_validated"] is True
    assert any("Worker Result Validation" in chunk for chunk in output)
    assert any("Validation Status: RESULT_VALIDATED" in chunk for chunk in output)
    assert any("No replay review yet." in chunk for chunk in output)
