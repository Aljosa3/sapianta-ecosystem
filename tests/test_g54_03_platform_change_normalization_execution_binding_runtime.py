"""Focused tests for the G54-03 non-authorizing capability execution binder."""

from __future__ import annotations

from copy import deepcopy
import inspect
import json

import pytest

from aigol.runtime.conversation_native_development_intent_routing import (
    run_conversation_native_development_intent_routing,
)
from aigol.runtime.conversation_session_resume_runtime import resume_conversation_session
from aigol.runtime.conversation_to_ppp_handoff_execution import (
    run_conversation_to_ppp_handoff_execution,
)
from aigol.runtime.governed_implementation_dry_run import (
    prepare_governed_implementation_dry_run,
)
from aigol.runtime.implementation_handoff_visibility import (
    create_implementation_handoff_visibility_summary,
)
from aigol.runtime.implementation_manifest_runtime import (
    CREATE_ONLY,
    create_implementation_manifest,
)
from aigol.runtime.platform_change_normalization_execution_binding_runtime import (
    CAPABILITY_EXECUTION_BINDING_READY_FOR_AUTHORIZATION,
    FAILED_CLOSED,
    bind_platform_change_normalization_to_execution_ready,
    reconstruct_platform_change_normalization_execution_binding_replay,
    validate_platform_change_normalization_execution_binding,
)
from aigol.runtime.platform_project_objective_inference import (
    infer_platform_project_objective,
)
from aigol.runtime.project_context_semantic_capability_route import (
    run_project_context_semantic_capability_route,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-07-30T00:00:00Z"
SESSION_ID = "SESSION-G54-03"
NORMALIZE_REQUEST = (
    "work_type: analysis. Review and normalize a repository implementation "
    "change into canonical change evidence."
)


def _hash(label: str) -> str:
    return replay_hash({"label": label})


def _manifest(tmp_path) -> dict:
    return create_implementation_manifest(
        manifest_id="MANIFEST-G54-03-000001",
        canonical_chain_id="CHAIN-G54-03-000001",
        implementation_bundle_id="G54_03_NORMALIZATION",
        source_candidate_reference="CANDIDATE-G54-03-000001",
        source_candidate_hash=_hash("candidate"),
        implementation_handoff_reference="HANDOFF-G54-03-000001",
        implementation_handoff_hash=_hash("handoff"),
        provider_generation_authorization_reference="AUTH-G54-03-000001",
        provider_generation_authorization_hash=_hash("authorization"),
        provider_response_reference="RESPONSE-G54-03-000001",
        provider_response_hash=_hash("response"),
        target_domain="PLATFORM_CORE",
        target_resource="G54_03_BINDING",
        target_worker=None,
        generated_files=[
            {
                "file_entry_id": "FILE-G54-03-000001",
                "target_path": "bounded/g54_03_target.py",
                "artifact_type": "PYTHON_RUNTIME_MODULE",
                "operation": CREATE_ONLY,
                "content": "VALUE = 1\n",
                "validation_requirements": [],
            }
        ],
        generated_tests=[],
        validation_requirements=["git diff --check"],
        known_gaps=[],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "manifest",
    )["implementation_manifest_artifact"]


def _semantic_route(tmp_path) -> tuple[dict, object]:
    objective = infer_platform_project_objective(
        request=NORMALIZE_REQUEST,
        development_intent={
            "requested_work_type": "ANALYSIS",
            "work_type": "ANALYSIS",
            "candidate_capability_discovery": {},
        },
        created_at=CREATED_AT,
    )
    replay_dir = tmp_path / "semantic_route"
    route = run_project_context_semantic_capability_route(
        session_id=SESSION_ID,
        message=NORMALIZE_REQUEST,
        project_objective_artifact=objective,
        project_objective_reference="OBJECTIVE-G54-03-000001",
        explicit_canonical_artifacts=[_manifest(tmp_path)],
        created_at=CREATED_AT,
        replay_dir=replay_dir,
    )
    return route, replay_dir


def _execution_ready(tmp_path) -> tuple[dict, object]:
    session_id = "SESSION-G54-03-EXECUTION-READY"
    allocation = resume_conversation_session(
        session_id=session_id,
        runtime_root=tmp_path / "routing_runtime",
        created_at=CREATED_AT,
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
        native_development_intent_routed_artifact=routed[
            "native_development_intent_routed_artifact"
        ],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "handoff",
    )
    visibility = create_implementation_handoff_visibility_summary(
        visibility_id="VISIBILITY-G54-03-000001",
        handoff_replay_reference=handoff["handoff_replay_reference"],
        approval_status=handoff["approval_status"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "visibility",
    )
    replay_dir = tmp_path / "execution_ready"
    capture = prepare_governed_implementation_dry_run(
        dry_run_id="DRY-RUN-G54-03-000001",
        handoff_replay_reference=handoff["handoff_replay_reference"],
        handoff_visibility_artifact=visibility[
            "implementation_handoff_visibility_artifact"
        ],
        upstream_lineage_artifact=handoff[
            "conversation_to_ppp_handoff_execution_artifact"
        ],
        created_at=CREATED_AT,
        replay_dir=replay_dir,
    )
    return capture, replay_dir


def _binding_inputs(tmp_path) -> dict:
    route, route_dir = _semantic_route(tmp_path)
    ready, ready_dir = _execution_ready(tmp_path)
    return {
        "binding_id": "CAPABILITY-EXECUTION-BINDING-G54-03-000001",
        "semantic_capability_route_artifact": route,
        "semantic_capability_route_replay_reference": route_dir,
        "execution_ready_status_artifact": ready["execution_ready_status_artifact"],
        "execution_ready_replay_reference": ready_dir,
        "requested_by": "HUMAN_OPERATOR",
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / "binding",
    }


def test_binding_is_deterministic_replay_visible_and_non_authorizing(tmp_path) -> None:
    capture = bind_platform_change_normalization_to_execution_ready(**_binding_inputs(tmp_path))
    artifact = capture["capability_execution_binding_artifact"]
    replay = reconstruct_platform_change_normalization_execution_binding_replay(
        capture["capability_execution_binding_replay_reference"]
    )

    assert capture["binding_status"] == CAPABILITY_EXECUTION_BINDING_READY_FOR_AUTHORIZATION
    assert artifact["authorization_required"] is True
    assert artifact["authority_flags"]["execution_authorized"] is False
    assert artifact["authority_flags"]["worker_dispatched"] is False
    assert artifact["authority_flags"]["worker_invoked"] is False
    assert replay["binding_id"] == artifact["binding_id"]
    assert replay["authorization_required"] is True


def test_invalid_capability_identity_fails_closed(tmp_path) -> None:
    args = _binding_inputs(tmp_path)
    invalid = deepcopy(args["semantic_capability_route_artifact"])
    invalid["selected_capability_identifier"] = "UNRELATED_CAPABILITY"
    invalid["artifact_hash"] = replay_hash(
        {key: value for key, value in invalid.items() if key != "artifact_hash"}
    )
    args["semantic_capability_route_artifact"] = invalid
    args["replay_dir"] = tmp_path / "invalid_identity"

    capture = bind_platform_change_normalization_to_execution_ready(**args)

    assert capture["binding_status"] == FAILED_CLOSED
    assert capture["execution_authorized"] is False
    assert capture["worker_invoked"] is False


def test_execution_ready_replay_mismatch_fails_closed(tmp_path) -> None:
    args = _binding_inputs(tmp_path)
    invalid = deepcopy(args["execution_ready_status_artifact"])
    invalid["dry_run_id"] = "SUBSTITUTED-DRY-RUN"
    invalid["artifact_hash"] = replay_hash(
        {key: value for key, value in invalid.items() if key != "artifact_hash"}
    )
    args["execution_ready_status_artifact"] = invalid
    args["replay_dir"] = tmp_path / "ready_mismatch"

    capture = bind_platform_change_normalization_to_execution_ready(**args)

    assert capture["binding_status"] == FAILED_CLOSED
    assert "execution-ready replay mismatch" in capture["failure_reason"]


def test_authorization_input_is_rejected_and_not_created(tmp_path) -> None:
    args = _binding_inputs(tmp_path)
    args["execution_authorization_reference"] = "UNAUTHORIZED-REQUEST"
    args["replay_dir"] = tmp_path / "unauthorized"

    capture = bind_platform_change_normalization_to_execution_ready(**args)

    assert capture["binding_status"] == FAILED_CLOSED
    assert "authorization input is forbidden" in capture["failure_reason"]
    assert capture["execution_authorized"] is False


def test_binding_replay_tampering_fails_closed(tmp_path) -> None:
    capture = bind_platform_change_normalization_to_execution_ready(**_binding_inputs(tmp_path))
    path = (
        capture["capability_execution_binding_replay_reference"]
        + "/001_capability_execution_binding_recorded.json"
    )
    wrapper = json.loads(open(path, encoding="utf-8").read())
    wrapper["artifact"]["authorization_required"] = False
    open(path, "w", encoding="utf-8").write(canonical_serialize(wrapper) + "\n")

    with pytest.raises(Exception, match="replay hash mismatch"):
        reconstruct_platform_change_normalization_execution_binding_replay(
            capture["capability_execution_binding_replay_reference"]
        )


def test_public_validator_rejects_authority_escalation(tmp_path) -> None:
    capture = bind_platform_change_normalization_to_execution_ready(**_binding_inputs(tmp_path))
    invalid = deepcopy(capture["capability_execution_binding_artifact"])
    invalid["authority_flags"]["execution_authorized"] = True
    invalid["artifact_hash"] = replay_hash(
        {key: value for key, value in invalid.items() if key != "artifact_hash"}
    )

    with pytest.raises(Exception, match="authority boundary mismatch"):
        validate_platform_change_normalization_execution_binding(invalid)


def test_binding_has_no_authorization_or_worker_execution_surface() -> None:
    import aigol.runtime.platform_change_normalization_execution_binding_runtime as runtime

    source = inspect.getsource(runtime)
    assert "authorize_execution_ready(" not in source
    assert "dispatch_assigned_worker(" not in source
    assert "invoke_dispatched_worker(" not in source
    assert "start_execution(" not in source
