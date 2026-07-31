"""Focused tests for the G54-05 normalization Worker completion adapter."""

from __future__ import annotations

from copy import deepcopy
import inspect

from aigol.cli.aigol_cli import return_platform_change_normalization_completion_to_acli
from aigol.runtime.execution_authorization_runtime import authorize_execution_ready
from aigol.runtime.execution_runtime import start_execution
from aigol.runtime.governed_implementation_dry_run import prepare_governed_implementation_dry_run
from aigol.runtime.human_interface_runtime_entry_service import run_human_interface_runtime_entry
from aigol.runtime.implementation_handoff_visibility import create_implementation_handoff_visibility_summary
from aigol.runtime.implementation_manifest_runtime import CREATE_ONLY, create_implementation_manifest
from aigol.runtime.platform_change_normalization_execution_binding_runtime import (
    bind_platform_change_normalization_to_execution_ready,
)
from aigol.runtime.platform_change_normalization_worker_completion_adapter import (
    FAILED_CLOSED,
    WORKER_CAPABILITY_COMPLETED,
    complete_platform_change_normalization_worker_capability,
    create_platform_change_normalization_worker_completion_evidence,
    reconstruct_platform_change_normalization_worker_completion_replay,
)
from aigol.runtime.platform_project_objective_inference import infer_platform_project_objective
from aigol.runtime.project_context_semantic_capability_route import run_project_context_semantic_capability_route
from aigol.runtime.conversation_native_development_intent_routing import run_conversation_native_development_intent_routing
from aigol.runtime.conversation_session_resume_runtime import resume_conversation_session
from aigol.runtime.conversation_to_ppp_handoff_execution import run_conversation_to_ppp_handoff_execution
from aigol.runtime.transport.serialization import replay_hash
from aigol.runtime.worker_assignment_runtime import assign_worker_from_invocation_request, default_worker_registry_for_request
from aigol.runtime.worker_dispatch_runtime import dispatch_assigned_worker
from aigol.runtime.worker_invocation_request_runtime import create_worker_invocation_request
from aigol.runtime.worker_invocation_runtime import invoke_dispatched_worker
from aigol.runtime.worker_result_capture_runtime import capture_worker_result
from aigol.runtime.worker_result_validation_runtime import validate_worker_result


CREATED_AT = "2026-07-31T00:00:00Z"
REQUEST = "work_type: analysis. Review and normalize a repository implementation change into canonical change evidence."


def _hash(label: str) -> str:
    return replay_hash({"label": label})


def _manifest(tmp_path) -> dict:
    return create_implementation_manifest(
        manifest_id="MANIFEST-G54-05-000001",
        canonical_chain_id="CHAIN-G54-05-000001",
        implementation_bundle_id="G54_05_NORMALIZATION",
        source_candidate_reference="CANDIDATE-G54-05-000001",
        source_candidate_hash=_hash("candidate"),
        implementation_handoff_reference="HANDOFF-G54-05-000001",
        implementation_handoff_hash=_hash("handoff"),
        provider_generation_authorization_reference="AUTH-G54-05-000001",
        provider_generation_authorization_hash=_hash("authorization"),
        provider_response_reference="RESPONSE-G54-05-000001",
        provider_response_hash=_hash("response"),
        target_domain="PLATFORM_CORE",
        target_resource="G54_05_COMPLETION",
        target_worker=None,
        generated_files=[{
            "file_entry_id": "FILE-G54-05-000001",
            "target_path": "bounded/g54_05_target.py",
            "artifact_type": "PYTHON_RUNTIME_MODULE",
            "operation": CREATE_ONLY,
            "content": "VALUE = 1\n",
            "validation_requirements": [],
        }],
        generated_tests=[],
        validation_requirements=["git diff --check"],
        known_gaps=[],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "manifest",
    )["implementation_manifest_artifact"]


def _semantic_route(tmp_path) -> tuple[dict, object]:
    objective = infer_platform_project_objective(
        request=REQUEST,
        development_intent={"requested_work_type": "ANALYSIS", "work_type": "ANALYSIS"},
        created_at=CREATED_AT,
    )
    replay_dir = tmp_path / "semantic_route"
    route = run_project_context_semantic_capability_route(
        session_id="SESSION-G54-05",
        message=REQUEST,
        project_objective_artifact=objective,
        project_objective_reference="OBJECTIVE-G54-05-000001",
        explicit_canonical_artifacts=[_manifest(tmp_path)],
        created_at=CREATED_AT,
        replay_dir=replay_dir,
    )
    return route, replay_dir


def _execution_ready(tmp_path) -> tuple[dict, object]:
    session_id = "SESSION-G54-05-READY"
    allocation = resume_conversation_session(
        session_id=session_id, runtime_root=tmp_path / "routing_runtime", created_at=CREATED_AT
    )
    prompt_id = f"{session_id}:{allocation['next_turn_id']}"
    routed = run_conversation_native_development_intent_routing(
        routing_id=f"{prompt_id}:ROUTING",
        prompt_id=prompt_id,
        human_prompt="Create a filesystem worker.",
        canonical_chain_id=prompt_id,
        turn_allocation_evidence=allocation,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "routing",
    )
    handoff = run_conversation_to_ppp_handoff_execution(
        execution_id=f"{prompt_id}:HANDOFF",
        native_development_intent_routed_artifact=routed["native_development_intent_routed_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "handoff",
    )
    visibility = create_implementation_handoff_visibility_summary(
        visibility_id="VISIBILITY-G54-05-000001",
        handoff_replay_reference=handoff["handoff_replay_reference"],
        approval_status=handoff["approval_status"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "visibility",
    )
    replay_dir = tmp_path / "execution_ready"
    ready = prepare_governed_implementation_dry_run(
        dry_run_id="DRY-RUN-G54-05-000001",
        handoff_replay_reference=handoff["handoff_replay_reference"],
        handoff_visibility_artifact=visibility["implementation_handoff_visibility_artifact"],
        upstream_lineage_artifact=handoff["conversation_to_ppp_handoff_execution_artifact"],
        created_at=CREATED_AT,
        replay_dir=replay_dir,
    )
    return ready, replay_dir


def _completion_inputs(tmp_path) -> dict:
    route, route_dir = _semantic_route(tmp_path)
    ready, ready_dir = _execution_ready(tmp_path)
    binding = bind_platform_change_normalization_to_execution_ready(
        binding_id="BINDING-G54-05-000001",
        semantic_capability_route_artifact=route,
        semantic_capability_route_replay_reference=route_dir,
        execution_ready_status_artifact=ready["execution_ready_status_artifact"],
        execution_ready_replay_reference=ready_dir,
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "binding",
    )
    authorization = authorize_execution_ready(
        authorization_id="AUTHORIZATION-G54-05-000001",
        execution_ready_replay_reference=ready["governed_implementation_dry_run_replay_reference"],
        authorizing_actor="HUMAN_OPERATOR",
        authorized_at=CREATED_AT,
        replay_dir=tmp_path / "authorization",
    )
    request = create_worker_invocation_request(
        invocation_request_id="WORKER-REQUEST-G54-05-000001",
        execution_authorization_replay_reference=authorization["execution_authorization_replay_reference"],
        requested_by="HUMAN_OPERATOR",
        requested_at=CREATED_AT,
        replay_dir=tmp_path / "worker_request",
    )
    assignment = assign_worker_from_invocation_request(
        worker_assignment_id="WORKER-ASSIGNMENT-G54-05-000001",
        worker_invocation_request_artifact=request["worker_invocation_request_artifact"],
        worker_invocation_request_replay_reference=request["worker_invocation_request_replay_reference"],
        worker_registry_artifacts=default_worker_registry_for_request(
            request["worker_invocation_request_artifact"], created_at=CREATED_AT
        ),
        assigned_by="HUMAN_OPERATOR",
        assigned_at=CREATED_AT,
        replay_dir=tmp_path / "assignment",
    )
    dispatch = dispatch_assigned_worker(
        worker_dispatch_id="WORKER-DISPATCH-G54-05-000001",
        worker_assignment_artifact=assignment["worker_assignment_artifact"],
        worker_assignment_replay_reference=assignment["worker_assignment_replay_reference"],
        dispatched_by="HUMAN_OPERATOR",
        dispatched_at=CREATED_AT,
        replay_dir=tmp_path / "dispatch",
    )
    invocation = invoke_dispatched_worker(
        worker_invocation_id="WORKER-INVOCATION-G54-05-000001",
        worker_dispatch_artifact=dispatch["worker_dispatch_artifact"],
        worker_dispatch_replay_reference=dispatch["worker_dispatch_replay_reference"],
        invoked_by="AIGOL_GOVERNANCE",
        invoked_at=CREATED_AT,
        replay_dir=tmp_path / "invocation",
    )
    invoked = invocation["worker_invocation_artifact"]
    execution = start_execution(
        execution_id="EXECUTION-G54-05-000001",
        invocation_artifact=invoked,
        invocation_replay=invocation["invocation_result_artifact"],
        dispatch_artifact=dispatch["worker_dispatch_artifact"],
        worker_assignment_artifact=assignment["worker_assignment_artifact"],
        canonical_chain_id=invoked["chain_id"],
        execution_metadata={"execution_mode": "BOUND_CAPABILITY_COMPLETION"},
        execution_context={"capability_id": "PLATFORM_CHANGE_NORMALIZATION", "allowed_effects": ["RECORD_EXECUTION_START"]},
        started_by="AIGOL",
        started_at=CREATED_AT,
        replay_reference="REPLAY-G54-05-000001",
        replay_dir=tmp_path / "execution",
    )
    output = create_platform_change_normalization_worker_completion_evidence(
        capability_execution_binding_artifact=binding["capability_execution_binding_artifact"],
        capability_execution_binding_replay_reference=binding["capability_execution_binding_replay_reference"],
        worker_invocation_artifact=invoked,
        worker_invocation_replay_reference=invocation["worker_invocation_replay_reference"],
        execution_artifact=execution["execution_artifact"],
        execution_replay_reference=tmp_path / "execution",
        completed_at=CREATED_AT,
    )
    capture = capture_worker_result(
        worker_result_capture_id="WORKER-CAPTURE-G54-05-000001",
        worker_invocation_artifact=invoked,
        worker_invocation_replay_reference=invocation["worker_invocation_replay_reference"],
        worker_output=output,
        captured_by="HUMAN_OPERATOR",
        captured_at=CREATED_AT,
        replay_dir=tmp_path / "result_capture",
        execution_artifact=execution["execution_artifact"],
        execution_replay=execution["execution_replay"],
        execution_replay_reference=str(tmp_path / "execution"),
    )
    validation = validate_worker_result(
        worker_result_validation_id="WORKER-VALIDATION-G54-05-000001",
        worker_result_capture_artifact=capture["worker_result_capture_artifact"],
        worker_result_capture_replay_reference=capture["worker_result_capture_replay_reference"],
        validated_by="HUMAN_OPERATOR",
        validated_at=CREATED_AT,
        replay_dir=tmp_path / "result_validation",
    )
    return {
        "completion_id": "COMPLETION-G54-05-000001",
        "capability_execution_binding_artifact": binding["capability_execution_binding_artifact"],
        "capability_execution_binding_replay_reference": binding["capability_execution_binding_replay_reference"],
        "execution_authorization_replay_reference": authorization["execution_authorization_replay_reference"],
        "worker_completion_evidence": output,
        "worker_result_capture_artifact": capture["worker_result_capture_artifact"],
        "worker_result_capture_replay_reference": capture["worker_result_capture_replay_reference"],
        "worker_result_validation_artifact": validation["worker_result_validation_artifact"],
        "worker_result_validation_replay_reference": validation["worker_result_validation_replay_reference"],
        "completed_by": "HUMAN_OPERATOR",
        "completed_at": CREATED_AT,
        "replay_dir": tmp_path / "completion",
    }


def test_completion_is_authenticated_replay_visible_and_human_returnable(tmp_path) -> None:
    capture = complete_platform_change_normalization_worker_capability(**_completion_inputs(tmp_path))
    reconstructed = reconstruct_platform_change_normalization_worker_completion_replay(
        capture["worker_capability_completion_replay_reference"]
    )

    assert capture["completion_status"] == WORKER_CAPABILITY_COMPLETED
    assert capture["human_visible_result"]["selected_capability_identifier"] == "PLATFORM_CHANGE_NORMALIZATION"
    assert reconstructed["completion_status"] == WORKER_CAPABILITY_COMPLETED
    assert reconstructed["human_visible_result"] == capture["human_visible_result"]
    assert capture["worker_capability_completion_artifact"]["authority_flags"]["authorization_created"] is False


def test_completion_rejects_substituted_worker_evidence(tmp_path) -> None:
    args = _completion_inputs(tmp_path)
    substituted = deepcopy(args["worker_completion_evidence"])
    substituted["payload"]["normalized_change_artifact_hash"] = _hash("substituted")
    substituted["artifact_hash"] = replay_hash({key: value for key, value in substituted.items() if key != "artifact_hash"})
    args["worker_completion_evidence"] = substituted
    args["replay_dir"] = tmp_path / "substituted"

    capture = complete_platform_change_normalization_worker_capability(**args)

    assert capture["completion_status"] == FAILED_CLOSED
    assert "output mismatch" in capture["failure_reason"]


def test_completion_rejects_unauthenticated_authorization_reference(tmp_path) -> None:
    args = _completion_inputs(tmp_path)
    args["execution_authorization_replay_reference"] = tmp_path / "missing_authorization"
    args["replay_dir"] = tmp_path / "missing_authorization_completion"

    capture = complete_platform_change_normalization_worker_capability(**args)

    assert capture["completion_status"] == FAILED_CLOSED
    assert capture["human_visible_result"] is None


def test_human_interface_and_aicli_return_authenticated_completion(tmp_path) -> None:
    capture = complete_platform_change_normalization_worker_capability(**_completion_inputs(tmp_path))
    hir = run_human_interface_runtime_entry(
        interface_name="test interface",
        session_id="SESSION-G54-05-HIR",
        human_requests=[REQUEST],
        created_at=CREATED_AT,
        runtime_root=tmp_path / "hir",
        workspace=str(tmp_path),
        governed_runtime_runner=lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("must not run")),
        worker_capability_completion_capture=capture,
    )
    aicli = return_platform_change_normalization_completion_to_acli(
        session_id="SESSION-G54-05-ACLI",
        human_request=REQUEST,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "aicli",
        workspace=str(tmp_path),
        worker_capability_completion_capture=capture,
    )

    assert hir["human_interface_completion_returned"] is True
    assert hir["human_visible_completion_result"] == capture["human_visible_result"]
    assert aicli["acli_capability_completion_returned"] is True
    assert aicli["human_visible_completion_result"] == capture["human_visible_result"]


def test_completion_adapter_has_no_authorization_or_lifecycle_call_surface() -> None:
    import aigol.runtime.platform_change_normalization_worker_completion_adapter as runtime

    source = inspect.getsource(runtime)
    for forbidden in (
        "authorize_execution_ready(",
        "create_worker_invocation_request(",
        "assign_worker_from_invocation_request(",
        "dispatch_assigned_worker(",
        "invoke_dispatched_worker(",
        "start_execution(",
    ):
        assert forbidden not in source
