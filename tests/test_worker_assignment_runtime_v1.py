"""Tests for AIGOL_WORKER_ASSIGNMENT_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json
from copy import deepcopy

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
from aigol.runtime.external_resource_registry_runtime import (
    ACTIVE,
    COGNITION_PROVIDER,
    EXECUTION_WORKER,
    INACTIVE,
    MOCK_FILESYSTEM_WORKER_ID,
    MOCK_PROVIDER_ID,
    create_err_v0_registry,
    register_resource,
)
from aigol.runtime.governed_implementation_dry_run import prepare_governed_implementation_dry_run
from aigol.runtime.implementation_approval_resume import (
    create_human_implementation_approval,
    resume_implementation_after_approval,
)
from aigol.runtime.implementation_handoff_visibility import create_implementation_handoff_visibility_summary
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash
from aigol.runtime.worker_assignment_runtime import (
    WORKER_ASSIGNED,
    assign_worker_from_invocation_request,
    default_worker_registry_for_request,
    reconstruct_worker_assignment_runtime_replay,
)
from aigol.runtime.worker_invocation_request_runtime import create_worker_invocation_request
from aigol.runtime.worker_runtime import WORKER_ASSIGNMENT_ARTIFACT_V1


CREATED_AT = "2026-06-04T00:00:00+00:00"
SESSION_ID = "SESSION-WORKER-ASSIGNMENT-000001"


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


def _assignment(tmp_path, *, prompt: str, suffix: str, worker_registry_artifacts=None) -> dict:
    request_capture = _invocation_request(tmp_path, prompt=prompt, suffix=suffix)
    request = request_capture["worker_invocation_request_artifact"]
    if worker_registry_artifacts is None:
        worker_registry_artifacts = default_worker_registry_for_request(request, created_at=CREATED_AT)
    return assign_worker_from_invocation_request(
        worker_assignment_id=f"WORKER-ASSIGNMENT-{suffix}",
        worker_invocation_request_artifact=request,
        worker_invocation_request_replay_reference=request_capture["worker_invocation_request_replay_reference"],
        worker_registry_artifacts=worker_registry_artifacts,
        assigned_by="AIGOL_GOVERNANCE",
        assigned_at=CREATED_AT,
        replay_dir=tmp_path / f"assignment_{suffix}",
    )


@pytest.mark.parametrize(
    ("prompt", "suffix"),
    [
        ("Create a filesystem worker.", "filesystem"),
        ("Create a monitoring worker.", "monitoring"),
        ("Improve trading strategy.", "trading"),
    ],
)
def test_worker_invocation_request_becomes_worker_assigned(tmp_path, prompt: str, suffix: str) -> None:
    capture = _assignment(tmp_path, prompt=prompt, suffix=suffix)
    assignment = capture["worker_assignment_artifact"]
    reconstructed = reconstruct_worker_assignment_runtime_replay(tmp_path / f"assignment_{suffix}")

    assert capture["assignment_status"] == WORKER_ASSIGNED
    assert assignment["artifact_type"] == WORKER_ASSIGNMENT_ARTIFACT_V1
    assert assignment["assignment_status"] == WORKER_ASSIGNED
    assert assignment["worker_id"]
    assert assignment["worker_family"]
    assert assignment["worker_role"]
    assert assignment["authorization_reference"] == f"AUTHORIZATION-{suffix}"
    assert assignment["execution_packet_reference"].endswith(":PACKET")
    assert assignment["allowed_outputs"]
    assert "INVOKE_WORKER" in assignment["forbidden_operations"]
    assert assignment["worker_assigned"] is True
    assert assignment["worker_dispatched"] is False
    assert assignment["worker_invoked"] is False
    assert assignment["execution_started"] is False
    assert reconstructed["assignment_status"] == WORKER_ASSIGNED
    assert reconstructed["worker_id"] == assignment["worker_id"]


def test_worker_assignment_persists_replay_evidence(tmp_path) -> None:
    _assignment(tmp_path, prompt="Create a filesystem worker.", suffix="replay-events")

    replay_dir = tmp_path / "assignment_replay-events"
    assert (replay_dir / "000_assignment_evidence_recorded.json").exists()
    assert (replay_dir / "001_assignment_classification_recorded.json").exists()
    assert (replay_dir / "002_assignment_artifact_recorded.json").exists()
    assert (replay_dir / "003_assignment_result_recorded.json").exists()


def test_worker_assignment_resolves_filesystem_worker_through_err_v0(tmp_path) -> None:
    request_capture = _invocation_request(tmp_path, prompt="Create a filesystem worker.", suffix="err-filesystem")
    request = request_capture["worker_invocation_request_artifact"]
    registry = create_err_v0_registry()
    register_resource(
        registry,
        {
            "resource_id": MOCK_PROVIDER_ID,
            "resource_type": COGNITION_PROVIDER,
            "capabilities": ["reasoning"],
            "status": ACTIVE,
        },
    )
    register_resource(
        registry,
        {
            "resource_id": MOCK_FILESYSTEM_WORKER_ID,
            "resource_type": EXECUTION_WORKER,
            "capabilities": ["file_write"],
            "status": ACTIVE,
        },
    )

    capture = assign_worker_from_invocation_request(
        worker_assignment_id="WORKER-ASSIGNMENT-ERR-FILESYSTEM",
        worker_invocation_request_artifact=request,
        worker_invocation_request_replay_reference=request_capture["worker_invocation_request_replay_reference"],
        worker_registry_artifacts=[],
        assigned_by="AIGOL_GOVERNANCE",
        assigned_at=CREATED_AT,
        replay_dir=tmp_path / "assignment_err_filesystem",
        use_err_worker_lookup=True,
        err_required_capability="file_write",
        err_registry=registry,
    )
    reconstructed = reconstruct_worker_assignment_runtime_replay(tmp_path / "assignment_err_filesystem")
    err_capture = capture["err_worker_selection_capture"]

    assert capture["assignment_status"] == WORKER_ASSIGNED
    assert capture["worker_id"] == MOCK_FILESYSTEM_WORKER_ID
    assert capture["worker_assignment_artifact"]["capability_id"] == "file_write"
    assert err_capture["selected_resource_id"] == MOCK_FILESYSTEM_WORKER_ID
    assert err_capture["required_capability"] == "file_write"
    assert err_capture["provider_invoked"] is False
    assert err_capture["worker_invoked"] is False
    assert err_capture["orchestration_performed"] is False
    assert reconstructed["worker_id"] == MOCK_FILESYSTEM_WORKER_ID
    assert reconstructed["err_worker_selection_enabled"] is True
    assert reconstructed["err_selected_resource_id"] == MOCK_FILESYSTEM_WORKER_ID
    assert reconstructed["err_required_capability"] == "file_write"
    assert reconstructed["err_worker_selection_replay"]["selected_resource_id"] == MOCK_FILESYSTEM_WORKER_ID
    assert (tmp_path / "assignment_err_filesystem" / "stages" / "err_worker_selection").exists()


def test_worker_assignment_err_lookup_fails_closed_without_active_filesystem_worker(tmp_path) -> None:
    request_capture = _invocation_request(tmp_path, prompt="Create a filesystem worker.", suffix="err-inactive")
    request = request_capture["worker_invocation_request_artifact"]
    registry = create_err_v0_registry()
    register_resource(
        registry,
        {
            "resource_id": MOCK_FILESYSTEM_WORKER_ID,
            "resource_type": EXECUTION_WORKER,
            "capabilities": ["file_write"],
            "status": INACTIVE,
        },
    )

    capture = assign_worker_from_invocation_request(
        worker_assignment_id="WORKER-ASSIGNMENT-ERR-INACTIVE",
        worker_invocation_request_artifact=request,
        worker_invocation_request_replay_reference=request_capture["worker_invocation_request_replay_reference"],
        worker_registry_artifacts=[],
        assigned_by="AIGOL_GOVERNANCE",
        assigned_at=CREATED_AT,
        replay_dir=tmp_path / "assignment_err_inactive",
        use_err_worker_lookup=True,
        err_required_capability="file_write",
        err_registry=registry,
    )

    assert capture["assignment_status"] == "FAILED_CLOSED"
    assert capture["fail_closed"] is True
    assert "no active resource for capability" in capture["failure_reason"]
    assert capture["worker_id"] is None
    assert capture["err_worker_selection_capture"] == {}


def test_worker_assignment_fails_closed_when_no_worker_exists(tmp_path) -> None:
    capture = _assignment(
        tmp_path,
        prompt="Create a filesystem worker.",
        suffix="missing-worker",
        worker_registry_artifacts=[],
    )

    assert capture["assignment_status"] == "FAILED_CLOSED"
    assert "no compatible worker exists" in capture["failure_reason"]


def test_worker_assignment_fails_closed_on_worker_family_mismatch(tmp_path) -> None:
    request_capture = _invocation_request(tmp_path, prompt="Create a filesystem worker.", suffix="family")
    request = request_capture["worker_invocation_request_artifact"]
    worker = default_worker_registry_for_request(request, created_at=CREATED_AT)[0]
    worker["worker_family"] = "MONITORING"
    worker.pop("artifact_hash")
    worker["artifact_hash"] = replay_hash(worker)

    capture = assign_worker_from_invocation_request(
        worker_assignment_id="WORKER-ASSIGNMENT-FAMILY",
        worker_invocation_request_artifact=request,
        worker_invocation_request_replay_reference=request_capture["worker_invocation_request_replay_reference"],
        worker_registry_artifacts=[worker],
        assigned_by="AIGOL_GOVERNANCE",
        assigned_at=CREATED_AT,
        replay_dir=tmp_path / "assignment_family",
    )

    assert capture["assignment_status"] == "FAILED_CLOSED"
    assert "worker family mismatch" in capture["failure_reason"]


def test_worker_assignment_fails_closed_on_worker_role_mismatch(tmp_path) -> None:
    request_capture = _invocation_request(tmp_path, prompt="Create a filesystem worker.", suffix="role")
    request = request_capture["worker_invocation_request_artifact"]
    worker = default_worker_registry_for_request(request, created_at=CREATED_AT)[0]
    worker["worker_roles"] = ["OTHER_ROLE"]
    worker.pop("artifact_hash")
    worker["artifact_hash"] = replay_hash(worker)

    capture = assign_worker_from_invocation_request(
        worker_assignment_id="WORKER-ASSIGNMENT-ROLE",
        worker_invocation_request_artifact=request,
        worker_invocation_request_replay_reference=request_capture["worker_invocation_request_replay_reference"],
        worker_registry_artifacts=[worker],
        assigned_by="AIGOL_GOVERNANCE",
        assigned_at=CREATED_AT,
        replay_dir=tmp_path / "assignment_role",
    )

    assert capture["assignment_status"] == "FAILED_CLOSED"
    assert "worker role mismatch" in capture["failure_reason"]


def test_worker_assignment_fails_closed_on_packet_mismatch(tmp_path) -> None:
    request_capture = _invocation_request(tmp_path, prompt="Create a filesystem worker.", suffix="packet")
    request = request_capture["worker_invocation_request_artifact"]
    worker = default_worker_registry_for_request(request, created_at=CREATED_AT)[0]
    worker["compatible_execution_packets"] = ["OTHER-PACKET"]
    worker.pop("artifact_hash")
    worker["artifact_hash"] = replay_hash(worker)

    capture = assign_worker_from_invocation_request(
        worker_assignment_id="WORKER-ASSIGNMENT-PACKET",
        worker_invocation_request_artifact=request,
        worker_invocation_request_replay_reference=request_capture["worker_invocation_request_replay_reference"],
        worker_registry_artifacts=[worker],
        assigned_by="AIGOL_GOVERNANCE",
        assigned_at=CREATED_AT,
        replay_dir=tmp_path / "assignment_packet",
    )

    assert capture["assignment_status"] == "FAILED_CLOSED"
    assert "packet mismatch" in capture["failure_reason"]


def test_worker_assignment_fails_closed_on_authority_violation(tmp_path) -> None:
    request_capture = _invocation_request(tmp_path, prompt="Create a filesystem worker.", suffix="authority")
    request = deepcopy(request_capture["worker_invocation_request_artifact"])
    request["worker_invoked"] = True
    request.pop("artifact_hash")
    request["artifact_hash"] = replay_hash(request)

    capture = assign_worker_from_invocation_request(
        worker_assignment_id="WORKER-ASSIGNMENT-AUTHORITY",
        worker_invocation_request_artifact=request,
        worker_invocation_request_replay_reference=request_capture["worker_invocation_request_replay_reference"],
        worker_registry_artifacts=default_worker_registry_for_request(
            request_capture["worker_invocation_request_artifact"],
            created_at=CREATED_AT,
        ),
        assigned_by="AIGOL_GOVERNANCE",
        assigned_at=CREATED_AT,
        replay_dir=tmp_path / "assignment_authority",
    )

    assert capture["assignment_status"] == "FAILED_CLOSED"
    assert "authority violation" in capture["failure_reason"]


def test_worker_assignment_reconstruction_detects_replay_corruption(tmp_path) -> None:
    _assignment(tmp_path, prompt="Create a filesystem worker.", suffix="corrupt")
    path = tmp_path / "assignment_corrupt" / "002_assignment_artifact_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["worker_invoked"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_worker_assignment_runtime_replay(tmp_path / "assignment_corrupt")


def test_cli_acceptance_flows_reach_worker_assigned(tmp_path) -> None:
    filesystem_output: list[str] = []
    filesystem = run_interactive_conversation(
        _args(tmp_path, session_id="SESSION-ASSIGNMENT-CLI-FILESYSTEM"),
        input_func=_input_sequence(["Create a filesystem worker.", "exit"]),
        output_func=filesystem_output.append,
    )
    trading_output: list[str] = []
    trading = run_interactive_conversation(
        _args(tmp_path, session_id="SESSION-ASSIGNMENT-CLI-TRADING"),
        input_func=_input_sequence(["Improve trading strategy.", "Approve.", "exit"]),
        output_func=trading_output.append,
    )

    assert filesystem["turns"][0]["worker_assignment_status"] == WORKER_ASSIGNED
    assert filesystem["worker_assigned"] is True
    assert "Assignment Status: WORKER_ASSIGNED" in filesystem_output[0]
    assert "No Worker has been dispatched, invoked, or executed." in filesystem_output[0]
    assert trading["turns"][1]["worker_assignment_status"] == WORKER_ASSIGNED
    assert trading["worker_assigned"] is True
    assert "Assignment Status: WORKER_ASSIGNED" in trading_output[1]


def test_worker_assignment_runtime_preserves_authority_boundaries() -> None:
    import aigol.runtime.worker_assignment_runtime as runtime

    source = inspect.getsource(runtime)

    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_result(" not in source
    assert "create_human_implementation_approval(" not in source
    assert "mutate_governance(" not in source
    assert "subprocess" not in source
    assert "requests" not in source
