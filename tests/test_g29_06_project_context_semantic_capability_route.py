"""Focused G29-06 Project Context to semantic capability route tests."""

from __future__ import annotations

from copy import deepcopy
import inspect

import aigol.runtime.project_context_semantic_capability_route as route_runtime
from aigol.runtime.certified_capability_invocation_binding_runtime import (
    PLATFORM_CHANGE_IMPACT_ANALYSIS,
    PLATFORM_CHANGE_NORMALIZATION,
)
from aigol.runtime.implementation_manifest_runtime import (
    CREATE_ONLY,
    create_implementation_manifest,
)
from aigol.runtime.platform_core_project_services import (
    prepare_unified_human_interface_project_context,
)
from aigol.runtime.platform_capability_certification_registry import (
    lookup_platform_capability_certification,
)
from aigol.runtime.platform_knowledge_runtime import query_platform_knowledge
from aigol.runtime.platform_project_objective_inference import (
    infer_platform_project_objective,
)
from aigol.runtime.project_context_semantic_capability_route import (
    ROUTE_CLARIFICATION_REQUIRED,
    ROUTE_COMPLETED,
    ROUTE_FAILED_CLOSED,
    ROUTE_NOT_ELIGIBLE,
    reconstruct_project_context_semantic_capability_route,
    run_project_context_semantic_capability_route,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-07-14T00:00:00Z"
SESSION_ID = "SESSION-G29-06"
NORMALIZE_REQUEST = (
    "work_type: analysis. Review and normalize a repository implementation "
    "change into canonical change evidence."
)


def _hash(label: str) -> str:
    return replay_hash({"label": label})


def _manifest(tmp_path, name: str = "ONE") -> dict:
    capture = create_implementation_manifest(
        manifest_id=f"MANIFEST-G29-06-{name}",
        canonical_chain_id=f"CHAIN-G29-06-{name}",
        implementation_bundle_id=f"G29_06_ROUTE_{name}",
        source_candidate_reference=f"CANDIDATE-G29-06-{name}",
        source_candidate_hash=_hash(f"candidate-{name}"),
        implementation_handoff_reference=f"HANDOFF-G29-06-{name}",
        implementation_handoff_hash=_hash(f"handoff-{name}"),
        provider_generation_authorization_reference=f"AUTH-G29-06-{name}",
        provider_generation_authorization_hash=_hash(f"authorization-{name}"),
        provider_response_reference=f"RESPONSE-G29-06-{name}",
        provider_response_hash=_hash(f"response-{name}"),
        target_domain="PLATFORM_CORE",
        target_resource="SEMANTIC_CAPABILITY_RUNTIME_ROUTE",
        target_worker=None,
        generated_files=[
            {
                "file_entry_id": f"FILE-G29-06-{name}",
                "target_path": f"bounded/example_{name.lower()}.py",
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
        replay_dir=tmp_path / f"manifest-{name}",
    )
    return capture["implementation_manifest_artifact"]


def _objective(request: str = NORMALIZE_REQUEST) -> dict:
    return infer_platform_project_objective(
        request=request,
        development_intent={
            "requested_work_type": "ANALYSIS",
            "work_type": "ANALYSIS",
            "candidate_capability_discovery": {},
        },
        created_at=CREATED_AT,
    )


def _run(tmp_path, *, artifacts, name="route", request=NORMALIZE_REQUEST):
    objective = _objective(request)
    return run_project_context_semantic_capability_route(
        session_id=SESSION_ID,
        message=request,
        project_objective_artifact=objective,
        project_objective_reference=f"OBJECTIVE-G29-06-{name}",
        explicit_canonical_artifacts=artifacts,
        created_at=CREATED_AT,
        replay_dir=tmp_path / name,
    )


def test_eligible_project_context_reaches_g29_g29_04_g28_and_presentation(
    tmp_path, monkeypatch
) -> None:
    lifecycle_calls = 0
    original = route_runtime.run_semantic_capability_invocation_lifecycle

    def counted(**kwargs):
        nonlocal lifecycle_calls
        lifecycle_calls += 1
        return original(**kwargs)

    monkeypatch.setattr(
        route_runtime, "run_semantic_capability_invocation_lifecycle", counted
    )
    route = _run(tmp_path, artifacts=[_manifest(tmp_path)])

    assert route["route_status"] == ROUTE_COMPLETED
    assert route["selected_capability_identifier"] == PLATFORM_CHANGE_NORMALIZATION
    assert route["canonical_platform_presentation"]["presentation_status"] == (
        "PRESENTATION_READY"
    )
    assert lifecycle_calls == 1
    assert route["worker_invoked"] is False
    assert route["provider_invoked"] is False
    assert route["repository_mutated"] is False
    assert reconstruct_project_context_semantic_capability_route(tmp_path / "route") == route


def test_ineligible_request_remains_outside_g29_and_existing_router_is_unchanged(
    tmp_path, monkeypatch
) -> None:
    called = False

    def forbidden(**kwargs):
        nonlocal called
        called = True
        raise AssertionError(kwargs)

    monkeypatch.setattr(route_runtime, "select_semantic_capability", forbidden)
    request = "work_type: analysis. Review the constitutional architecture."
    route = _run(tmp_path, artifacts=[], name="ineligible", request=request)
    assert route["route_status"] == ROUTE_NOT_ELIGIBLE
    assert called is False

    context = prepare_unified_human_interface_project_context(
        interface_name="aicli",
        session_id="SESSION-G29-06-INELIGIBLE",
        message=request,
        runtime_root=tmp_path / "runtime",
        workspace=tmp_path,
        created_at=CREATED_AT,
    )
    result = context["governed_read_only_work_result"]
    assert result["selected_read_only_service"] != (
        "CANONICAL_PROJECT_CONTEXT_TO_SEMANTIC_CAPABILITY_RUNTIME_ROUTE_BINDING"
    )
    assert result["platform_query_router_response"] is not None


def test_g29_and_missing_artifact_clarification_reaches_human_conversation(
    tmp_path,
) -> None:
    context = prepare_unified_human_interface_project_context(
        interface_name="aicli",
        session_id="SESSION-G29-06-CLARIFICATION",
        message=NORMALIZE_REQUEST,
        runtime_root=tmp_path / "runtime",
        workspace=tmp_path,
        created_at=CREATED_AT,
    )
    route = context["semantic_capability_runtime_route"]
    conversation = context["human_conversation_experience"]

    assert route["route_status"] == ROUTE_CLARIFICATION_REQUIRED
    assert route["lifecycle_result_hash"] is None
    assert conversation["response_mode"] == "CLARIFICATION"
    assert len(conversation["clarification_questions"]) == 1
    assert context["governed_read_only_work_result"]["worker_invoked"] is False


def test_exactly_one_artifact_binds_but_multiple_artifacts_clarify(tmp_path) -> None:
    one = _manifest(tmp_path, "ONE")
    completed = _run(tmp_path, artifacts=[one], name="one")
    assert completed["route_status"] == ROUTE_COMPLETED
    assert completed["bound_canonical_artifact_hash"] == one["artifact_hash"]

    two = _manifest(tmp_path, "TWO")
    ambiguous = _run(tmp_path, artifacts=[one, two], name="multiple")
    assert ambiguous["route_status"] == ROUTE_CLARIFICATION_REQUIRED
    assert ambiguous["failure_reason"] == (
        "MULTIPLE_EXPLICIT_COMPATIBLE_CANONICAL_ARTIFACTS"
    )
    assert len(ambiguous["clarification_artifact"]["clarification_questions"]) == 1
    assert ambiguous["lifecycle_result_hash"] is None


def test_platform_knowledge_is_bound_with_exact_identifier(tmp_path) -> None:
    route = _run(tmp_path, artifacts=[_manifest(tmp_path)])
    assert route["platform_knowledge_response_reference"].endswith(
        "platform_knowledge_response.json"
    )
    assert route["platform_knowledge_response_hash"].startswith("sha256:")
    assert route["selected_capability_identifier"] == PLATFORM_CHANGE_NORMALIZATION


def test_platform_knowledge_identifier_mismatch_fails_closed(tmp_path, monkeypatch) -> None:
    mismatch = query_platform_knowledge(
        query="Where is impact analysis implemented?",
        capability_identifier=PLATFORM_CHANGE_IMPACT_ANALYSIS,
    )
    monkeypatch.setattr(
        route_runtime, "query_platform_knowledge", lambda **_: deepcopy(mismatch)
    )
    route = _run(tmp_path, artifacts=[_manifest(tmp_path)], name="mismatch")
    assert route["route_status"] == ROUTE_FAILED_CLOSED
    assert "mismatch" in route["failure_reason"]
    assert route["worker_invoked"] is False
    assert route["provider_invoked"] is False
    assert route["repository_mutated"] is False


def test_g28_is_reached_only_through_g29_04_and_aicli_has_no_semantic_logic() -> None:
    route_source = inspect.getsource(route_runtime)
    from aigol.cli import aicli

    aicli_source = inspect.getsource(aicli)
    assert "invoke_certified_capability(" not in route_source
    assert "select_semantic_capability" not in aicli_source
    assert "run_semantic_capability_invocation_lifecycle" not in aicli_source
    assert "certified_capability_invocation" not in aicli_source


def test_route_binding_is_registered_as_governance_metadata_only() -> None:
    record = lookup_platform_capability_certification(
        "CANONICAL_PROJECT_CONTEXT_TO_SEMANTIC_CAPABILITY_RUNTIME_ROUTE_BINDING"
    )
    assert record["certification_milestone"] == "G29-06"
    assert record["runtime_execution_authority"] is False


def test_aicli_renders_platform_core_presentation_without_semantic_authority(
    tmp_path, monkeypatch
) -> None:
    from aigol.cli import aicli

    manifest = _manifest(tmp_path, "AICLI")
    original = aicli.prepare_unified_human_interface_project_context

    def platform_context(**kwargs):
        return original(**kwargs, explicit_canonical_artifacts=[manifest])

    monkeypatch.setattr(
        aicli, "prepare_unified_human_interface_project_context", platform_context
    )
    lines = iter([NORMALIZE_REQUEST, "/send", "/exit"])
    output: list[str] = []
    result = aicli.run_reference_uhi_session(
        session_id="SESSION-G29-06-AICLI",
        runtime_root=tmp_path / "runtime",
        workspace=tmp_path,
        created_at=CREATED_AT,
        input_reader=lambda _: next(lines),
        output_writer=output.append,
    )

    rendered = "\n".join(output)
    assert "PRESENTATION_READY" in rendered
    assert (
        "CANONICAL_PROJECT_CONTEXT_TO_SEMANTIC_CAPABILITY_RUNTIME_ROUTE_BINDING"
        in rendered
    )
    assert result["aicli_authorizes"] is False
    assert result["aicli_executes"] is False
