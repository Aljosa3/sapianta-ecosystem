"""Focused G54-09 Platform Core admission precedence tests."""

from __future__ import annotations

from copy import deepcopy
import json

import pytest

from aigol.cli.aigol_cli import build_parser, run_command
from aigol.runtime.implementation_manifest_runtime import (
    CREATE_ONLY,
    create_implementation_manifest,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_admission_precedence_runtime import (
    CAPABILITY_ADMISSION_CLARIFICATION_REQUIRED,
    EXPLICIT_CERTIFIED_CAPABILITY_REQUEST_ADMITTED,
    GENERIC_GOVERNED_DEVELOPMENT_ADMISSION,
    determine_platform_core_admission_precedence,
    reconstruct_platform_core_admission_precedence,
    validate_platform_core_admission_precedence,
)
from aigol.runtime.platform_core_project_services import (
    latest_platform_core_workspace_state,
    prepare_unified_human_interface_project_context,
    record_unified_human_interface_workspace_state,
    resolve_development_intent,
)
from aigol.runtime.project_context_semantic_capability_route import (
    ROUTE_COMPLETED,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-07-31T00:00:00Z"
SESSION_ID = "SESSION-G54-09"
EXPLICIT_REQUEST = (
    'Normalize this platform change:\n\n'
    'Add a comment saying "Hello".\n\n'
    "Return only the normalized platform change."
)
CONTINUATION_REQUEST = "Continue implementing the current runtime workflow."


def _hash(label: str) -> str:
    return replay_hash({"label": label})


def _manifest(tmp_path) -> dict:
    return create_implementation_manifest(
        manifest_id="MANIFEST-G54-09-000001",
        canonical_chain_id="CHAIN-G54-09-000001",
        implementation_bundle_id="G54_09_ADMISSION_PRECEDENCE",
        source_candidate_reference="CANDIDATE-G54-09-000001",
        source_candidate_hash=_hash("candidate"),
        implementation_handoff_reference="HANDOFF-G54-09-000001",
        implementation_handoff_hash=_hash("handoff"),
        provider_generation_authorization_reference="AUTH-G54-09-000001",
        provider_generation_authorization_hash=_hash("authorization"),
        provider_response_reference="RESPONSE-G54-09-000001",
        provider_response_hash=_hash("response"),
        target_domain="PLATFORM_CORE",
        target_resource="G54_09_ADMISSION_PRECEDENCE",
        target_worker=None,
        generated_files=[
            {
                "file_entry_id": "FILE-G54-09-000001",
                "target_path": "bounded/g54_09_target.py",
                "artifact_type": "PYTHON_RUNTIME_MODULE",
                "operation": CREATE_ONLY,
                "content": "# Hello\n",
                "validation_requirements": [],
            }
        ],
        generated_tests=[],
        validation_requirements=["git diff --check"],
        known_gaps=[],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "manifest",
    )["implementation_manifest_artifact"]


def _seed_active_workspace(runtime_root, workspace) -> dict:
    return record_unified_human_interface_workspace_state(
        interface_name="aicli",
        session_id=SESSION_ID,
        runtime_root=runtime_root,
        workspace=workspace,
        created_at=CREATED_AT,
        completion={
            "artifact_hash": _hash("completion"),
            "replay_reference": "REPLAY-G54-09-SEED",
        },
        turn_results=[
            {
                "runtime_binding_status": "AIGOL_NEXT_RUNTIME_BOUND",
                "runtime_replay_reference": "REPLAY-G54-09-RUNTIME",
                "latest_prompt": "Seed the active workspace objective.",
                "replay_certification_reached": True,
            }
        ],
        pending_clarification=None,
        pending_summary=None,
    )


def test_explicit_authenticated_capability_preempts_active_workspace_and_routes(
    tmp_path,
) -> None:
    runtime_root = tmp_path / "runtime"
    workspace_state = _seed_active_workspace(runtime_root, tmp_path)
    assert workspace_state["active_development_objective"] == (
        "recent governed development runtime completed"
    )

    context = prepare_unified_human_interface_project_context(
        interface_name="aicli",
        session_id=SESSION_ID,
        message=EXPLICIT_REQUEST,
        runtime_root=runtime_root,
        workspace=tmp_path,
        created_at=CREATED_AT,
        explicit_canonical_artifacts=[_manifest(tmp_path)],
    )
    admission = context["admission_precedence"]
    resolution = context["development_intent_resolution"]
    route = context["semantic_capability_runtime_route"]
    reconstructed = reconstruct_platform_core_admission_precedence(
        context["admission_precedence_reference"]
    )

    assert admission["admission_status"] == (
        EXPLICIT_CERTIFIED_CAPABILITY_REQUEST_ADMITTED
    )
    assert admission["admission_candidate_identifier"] == (
        "PLATFORM_CHANGE_NORMALIZATION"
    )
    assert admission["active_workspace_continuation_available"] is True
    assert admission["active_workspace_fallback_allowed"] is False
    assert admission["operative_action_clauses"] == [
        "Normalize this platform change:"
    ]
    assert admission["output_constraint_clauses"] == [
        "Return only the normalized platform change."
    ]
    assert resolution["governed_request"] == EXPLICIT_REQUEST
    assert resolution["canonical_runtime_prompt"] == EXPLICIT_REQUEST
    assert resolution["requested_work_type"] == "ANALYSIS"
    assert resolution["goal_mapping"]["goal_target"] == "general_project_goal"
    assert route["route_status"] == ROUTE_COMPLETED
    assert route["selected_capability_identifier"] == (
        "PLATFORM_CHANGE_NORMALIZATION"
    )
    assert route["selection_treated_as_authorization"] is False
    assert reconstructed["artifact_hash"] == admission["artifact_hash"]
    assert reconstructed["admission_decision_hash"] == (
        admission["admission_decision_hash"]
    )


def test_exact_request_traverses_aicli_and_hir_without_active_objective_expansion(
    tmp_path,
) -> None:
    runtime_root = tmp_path / "runtime"
    _seed_active_workspace(runtime_root, tmp_path)
    result = run_command(
        build_parser().parse_args(
            [
                "next",
                "--session-id",
                SESSION_ID,
                "--prompt",
                EXPLICIT_REQUEST,
                "--canonical-artifact-json",
                json.dumps(_manifest(tmp_path), sort_keys=True),
                "--created-at",
                CREATED_AT,
                "--runtime-root",
                str(runtime_root),
                "--workspace",
                str(tmp_path),
                "--json",
            ]
        )
    )
    context = result["platform_core_project_services_context"]
    admission = context["admission_precedence"]
    resolution = context["development_intent_resolution"]

    assert admission["admission_status"] == (
        EXPLICIT_CERTIFIED_CAPABILITY_REQUEST_ADMITTED
    )
    assert resolution["governed_request"] == EXPLICIT_REQUEST
    assert resolution["canonical_runtime_prompt"] == EXPLICIT_REQUEST
    assert context["semantic_capability_runtime_route"]["route_status"] == (
        ROUTE_COMPLETED
    )
    assert result["runtime_prompts"] == []
    assert result["governed_read_only_work_result"][
        "selected_capability_identifier"
    ] == "PLATFORM_CHANGE_NORMALIZATION"


def test_admission_decision_is_identical_across_replay_locations(
    tmp_path,
) -> None:
    manifest = _manifest(tmp_path)
    first = determine_platform_core_admission_precedence(
        request=EXPLICIT_REQUEST,
        explicit_canonical_artifacts=[manifest],
        active_workspace_objective="active governed objective",
        replay_reference=tmp_path / "first" / "admission.json",
    )
    second = determine_platform_core_admission_precedence(
        request=EXPLICIT_REQUEST,
        explicit_canonical_artifacts=[manifest],
        active_workspace_objective="active governed objective",
        replay_reference=tmp_path / "second" / "admission.json",
    )

    assert first == second
    assert first["admission_decision_hash"] == second[
        "admission_decision_hash"
    ]
    assert first["artifact_hash"] == second["artifact_hash"]


def test_normal_workspace_continuation_remains_unchanged(tmp_path) -> None:
    runtime_root = tmp_path / "runtime"
    _seed_active_workspace(runtime_root, tmp_path)
    prior = latest_platform_core_workspace_state(
        runtime_root / SESSION_ID
    )
    historical_resolution = resolve_development_intent(
        message=CONTINUATION_REQUEST,
        workspace_state=prior,
    )

    context = prepare_unified_human_interface_project_context(
        interface_name="aicli",
        session_id=SESSION_ID,
        message=CONTINUATION_REQUEST,
        runtime_root=runtime_root,
        workspace=tmp_path,
        created_at=CREATED_AT,
    )
    admission = context["admission_precedence"]
    resolution = context["development_intent_resolution"]

    assert admission["admission_status"] == (
        GENERIC_GOVERNED_DEVELOPMENT_ADMISSION
    )
    assert admission["active_workspace_fallback_allowed"] is True
    assert admission["generic_continuation_preserved"] is True
    assert resolution["governed_request"] == historical_resolution[
        "governed_request"
    ]
    assert resolution["goal_mapping"] == historical_resolution["goal_mapping"]
    assert resolution["candidate_capability_discovery"] == (
        historical_resolution["candidate_capability_discovery"]
    )
    assert resolution["goal_mapping"]["goal_target"] == "active_objective"


def test_ambiguous_explicit_capability_request_requires_clarification(
    tmp_path,
) -> None:
    runtime_root = tmp_path / "runtime"
    _seed_active_workspace(runtime_root, tmp_path)
    request = (
        "Normalize this platform change and analyze its platform impact. "
        "Return the governed result."
    )

    context = prepare_unified_human_interface_project_context(
        interface_name="aicli",
        session_id=SESSION_ID,
        message=request,
        runtime_root=runtime_root,
        workspace=tmp_path,
        created_at=CREATED_AT,
    )
    admission = context["admission_precedence"]
    resolution = context["development_intent_resolution"]

    assert admission["admission_status"] == (
        CAPABILITY_ADMISSION_CLARIFICATION_REQUIRED
    )
    assert admission["clarification_reason"] == (
        "MULTIPLE_EXPLICIT_CERTIFIED_CAPABILITY_REQUESTS"
    )
    assert admission["active_workspace_fallback_allowed"] is False
    assert resolution["clarification_required"] is True
    assert resolution["summary_admissible"] is False
    assert context["semantic_capability_runtime_route"] is None
    assert context["governed_read_only_work_result"] is None


def test_explicit_capability_without_canonical_input_does_not_infer_artifact(
    tmp_path,
) -> None:
    runtime_root = tmp_path / "runtime"
    _seed_active_workspace(runtime_root, tmp_path)

    context = prepare_unified_human_interface_project_context(
        interface_name="aicli",
        session_id=SESSION_ID,
        message=EXPLICIT_REQUEST,
        runtime_root=runtime_root,
        workspace=tmp_path,
        created_at=CREATED_AT,
    )
    admission = context["admission_precedence"]

    assert admission["admission_status"] == (
        CAPABILITY_ADMISSION_CLARIFICATION_REQUIRED
    )
    assert admission["clarification_reason"] == (
        "AUTHENTICATED_CANONICAL_CAPABILITY_INPUT_REQUIRED"
    )
    assert admission["canonical_artifact_inferred_from_text"] is False
    assert admission["capability_selection_performed"] is False
    assert context["development_intent_resolution"][
        "clarification_required"
    ] is True
    assert context["semantic_capability_runtime_route"] is None


def test_invalid_canonical_capability_input_fails_closed_before_selection(
    tmp_path,
) -> None:
    invalid_manifest = deepcopy(_manifest(tmp_path))
    invalid_manifest["artifact_hash"] = "0" * 64

    context = prepare_unified_human_interface_project_context(
        interface_name="aicli",
        session_id=SESSION_ID,
        message=EXPLICIT_REQUEST,
        runtime_root=tmp_path / "runtime",
        workspace=tmp_path,
        created_at=CREATED_AT,
        explicit_canonical_artifacts=[invalid_manifest],
    )
    admission = context["admission_precedence"]

    assert admission["admission_status"] == (
        CAPABILITY_ADMISSION_CLARIFICATION_REQUIRED
    )
    assert admission["clarification_reason"] == (
        "INVALID_CANONICAL_CAPABILITY_INPUT_EVIDENCE"
    )
    assert admission["invalid_canonical_artifact_count"] == 1
    assert admission["capability_selection_performed"] is False
    assert context["development_intent_resolution"][
        "clarification_required"
    ] is True
    assert context["semantic_capability_runtime_route"] is None


def test_admission_replay_rejects_tampering(tmp_path) -> None:
    context = prepare_unified_human_interface_project_context(
        interface_name="aicli",
        session_id=SESSION_ID,
        message=CONTINUATION_REQUEST,
        runtime_root=tmp_path / "runtime",
        workspace=tmp_path,
        created_at=CREATED_AT,
    )
    reference = context["admission_precedence_reference"]
    tampered = deepcopy(context["admission_precedence"])
    tampered["execution_authorized"] = True
    tampered.pop("artifact_hash")
    tampered["artifact_hash"] = replay_hash(tampered)

    with pytest.raises(
        FailClosedRuntimeError,
        match="authority boundary invalid",
    ):
        validate_platform_core_admission_precedence(tampered)

    assert reconstruct_platform_core_admission_precedence(reference)[
        "execution_authorized"
    ] is False


def test_admission_validator_rejects_forged_semantic_reduction(tmp_path) -> None:
    context = prepare_unified_human_interface_project_context(
        interface_name="aicli",
        session_id=SESSION_ID,
        message=EXPLICIT_REQUEST,
        runtime_root=tmp_path / "runtime",
        workspace=tmp_path,
        created_at=CREATED_AT,
        explicit_canonical_artifacts=[_manifest(tmp_path)],
    )
    tampered = deepcopy(context["admission_precedence"])
    tampered.update(
        {
            "semantic_candidates": [],
            "compatible_candidate_identifiers": [],
            "admission_status": GENERIC_GOVERNED_DEVELOPMENT_ADMISSION,
            "admission_candidate_identifier": None,
            "admission_work_type_override": None,
            "clarification_reason": None,
            "active_workspace_fallback_allowed": True,
            "operative_request_preserved_exactly": False,
            "generic_continuation_preserved": True,
        }
    )
    decision_fields = (
        "source_request_hash",
        "operative_action_clauses",
        "output_constraint_clauses",
        "canonical_artifact_evidence",
        "invalid_canonical_artifact_count",
        "semantic_candidates",
        "compatible_candidate_identifiers",
        "admission_status",
        "admission_candidate_identifier",
        "admission_work_type_override",
        "clarification_reason",
        "active_workspace_continuation_available",
        "active_workspace_fallback_allowed",
    )
    tampered["admission_decision_hash"] = replay_hash(
        {field: tampered.get(field) for field in decision_fields}
    )
    tampered.pop("artifact_hash")
    tampered["artifact_hash"] = replay_hash(tampered)

    with pytest.raises(
        FailClosedRuntimeError,
        match="semantic reduction mismatch",
    ):
        validate_platform_core_admission_precedence(tampered)
