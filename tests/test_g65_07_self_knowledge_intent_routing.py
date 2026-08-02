"""Focused regression coverage for G65-07 Self Knowledge intent routing."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from aigol.cli import aicli
from aigol.runtime import platform_core_project_services as project_services
from aigol.runtime import platform_query_router
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_project_services import (
    prepare_unified_human_interface_project_context,
)
from aigol.runtime.platform_query_router import (
    ROUTE_CLARIFICATION_REQUIRED,
    ROUTE_READY,
    SELF_KNOWLEDGE_ROUTE,
    route_platform_query,
    validate_platform_query_router_response,
)
from aigol.runtime.self_knowledge_request_classification import (
    CLARIFICATION_REQUIRED,
    DEVELOPMENT_OBJECTIVE,
    SELF_KNOWLEDGE_QUERY,
    classify_self_knowledge_request,
    validate_self_knowledge_request_classification,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CREATED_AT = "2026-08-02T00:00:00Z"
SUPPORTED_REQUESTS = (
    ("Show architecture.", "ARCHITECTURE"),
    ("Show runtime inventory.", "RUNTIME_INVENTORY"),
    ("Show certified capabilities.", "CERTIFIED_CAPABILITIES"),
    ("Show governance state.", "GOVERNANCE_STATE"),
    ("Show execution boundaries.", "EXECUTION_BOUNDARIES"),
    ("Show certified history.", "CERTIFIED_HISTORY"),
    ("Show known limitations.", "KNOWN_LIMITATIONS"),
    ("Show ownership.", "OWNERSHIP"),
)


@pytest.mark.parametrize(("request_text", "subject"), SUPPORTED_REQUESTS)
def test_closed_conversation_request_vocabulary_routes_before_objective_inference(
    request_text: str,
    subject: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def objective_inference_forbidden(*_args, **_kwargs):
        raise AssertionError("Project Objective inference must not run")

    monkeypatch.setattr(
        project_services,
        "infer_platform_project_objective",
        objective_inference_forbidden,
    )
    context = prepare_unified_human_interface_project_context(
        interface_name="aicli",
        session_id=f"G65-07-{subject}",
        message=request_text,
        runtime_root=tmp_path,
        workspace=REPOSITORY_ROOT,
        created_at=CREATED_AT,
    )

    turn = context["operational_turn_binding"]
    read_only = context["governed_read_only_work_result"]
    router = read_only["platform_query_router_response"]
    presentation = read_only["canonical_presentation"]
    response = router["service_response"]

    assert context["project_objective_inference"] is None
    assert context["admission_precedence"] is None
    assert context["constitutional_development_governance"] is None
    assert context["reuse_proof_production_admission"] is None
    assert turn["selected_service"] == SELF_KNOWLEDGE_ROUTE
    assert turn["selected_query_class"] == SELF_KNOWLEDGE_QUERY
    assert router["route_status"] == ROUTE_READY
    assert router["service_invoked"] is True
    assert response["query_subject"] == subject
    assert presentation["service"] == SELF_KNOWLEDGE_ROUTE
    assert presentation["presentation_status"] == "PRESENTATION_READY"
    assert presentation["answer"]["query_subject"] == subject
    assert presentation["answer"]["snapshot_digest"] == response["snapshot_hash"]
    assert presentation["answer"]["source_references"] == response[
        "source_references"
    ]
    assert response["boundary_flags"]["provider_invoked"] is False
    assert response["boundary_flags"]["worker_invoked"] is False
    assert response["boundary_flags"]["replay_modified"] is False


@pytest.mark.parametrize(("request_text", "subject"), SUPPORTED_REQUESTS)
def test_classifier_is_exact_deterministic_and_version_bound(
    request_text: str,
    subject: str,
) -> None:
    first = classify_self_knowledge_request(request_text)
    second = classify_self_knowledge_request(request_text)

    assert first == second
    assert validate_self_knowledge_request_classification(first) == first
    assert first["request_classification"] == SELF_KNOWLEDGE_QUERY
    assert first["query_subject"] == subject
    assert first["canonical_self_knowledge_request"] == (
        f"/self-knowledge {subject}"
    )
    assert first["objective_inference_allowed"] is False
    assert first["deterministic_exact_match"] is True


def test_router_reuses_g65_06_without_generic_query_or_intent_inference(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden(*_args, **_kwargs):
        raise AssertionError("generic inference owner must not run")

    monkeypatch.setattr(platform_query_router, "query_platform_knowledge", forbidden)
    monkeypatch.setattr(platform_query_router, "resolve_development_intent", forbidden)

    first = route_platform_query(
        query="Show architecture.",
        repository_root=str(REPOSITORY_ROOT),
        created_at=CREATED_AT,
    )
    second = route_platform_query(
        query="Show architecture.",
        repository_root=str(REPOSITORY_ROOT),
        created_at=CREATED_AT,
    )

    assert first == second
    assert validate_platform_query_router_response(first) == first
    assert first["selected_service"] == SELF_KNOWLEDGE_ROUTE
    assert first["service_response"]["query_subject"] == "ARCHITECTURE"
    evidence = first["classification_evidence"]
    assert evidence["classification_before_objective_inference"] is True
    assert evidence["project_objective_inference_invoked"] is False
    assert evidence["development_intent_resolution_invoked_by_router"] is False


@pytest.mark.parametrize(
    "request_text",
    ("/self-knowledge ARCHITECTURE", "SELF_KNOWLEDGE:ARCHITECTURE"),
)
def test_g65_06_explicit_request_forms_remain_compatible(
    request_text: str,
) -> None:
    classification = classify_self_knowledge_request(request_text)
    response = route_platform_query(
        query=request_text,
        repository_root=str(REPOSITORY_ROOT),
        created_at=CREATED_AT,
    )

    assert classification["request_classification"] == SELF_KNOWLEDGE_QUERY
    assert classification["query_subject"] == "ARCHITECTURE"
    assert response["selected_service"] == SELF_KNOWLEDGE_ROUTE
    assert response["service_response"]["query_subject"] == "ARCHITECTURE"


def test_real_aicli_request_returns_read_only_presentation_without_approval(
    tmp_path: Path,
) -> None:
    output: list[str] = []
    values = iter(["Show architecture.", "/send", "/exit"])

    result = aicli.run_reference_uhi_session(
        session_id="G65-07-REAL-AICLI",
        runtime_root=tmp_path,
        workspace=REPOSITORY_ROOT,
        input_reader=lambda _prompt: next(values),
        output_writer=output.append,
    )

    context = result["platform_core_project_services_context"]
    assert result["pending_approval"] is False
    assert result["runtime_entered"] is False
    assert result["clarification_question_count"] == 0
    assert context["project_objective_inference"] is None
    assert context["governed_read_only_work_result"][
        "selected_read_only_service"
    ] == SELF_KNOWLEDGE_ROUTE
    assert any(
        "NON-AUTHORITATIVE READ-ONLY SELF KNOWLEDGE: ARCHITECTURE — AVAILABLE"
        in line
        for line in output
    )
    assert not any(
        "Clarification required before governed execution." in line
        for line in output
    )


def test_development_request_preserves_existing_objective_path(
    tmp_path: Path,
) -> None:
    request = "Implement a governed validation utility for replay evidence."
    classification = classify_self_knowledge_request(request)
    context = prepare_unified_human_interface_project_context(
        interface_name="aicli",
        session_id="G65-07-DEVELOPMENT-CONTROL",
        message=request,
        runtime_root=tmp_path,
        workspace=REPOSITORY_ROOT,
        created_at=CREATED_AT,
    )

    assert classification["request_classification"] == DEVELOPMENT_OBJECTIVE
    assert classification["objective_inference_allowed"] is True
    assert context["admission_precedence"] is not None
    assert isinstance(context["project_objective_inference"], dict)
    assert context["operational_turn_binding"]["selected_service"] != (
        SELF_KNOWLEDGE_ROUTE
    )


@pytest.mark.parametrize(
    "request_text",
    (
        "Show architecture and ownership.",
        "Show me architecture.",
        "Show known limitations and certified history.",
    ),
)
def test_ambiguous_self_knowledge_wording_requires_clarification_before_objective(
    request_text: str,
    tmp_path: Path,
) -> None:
    classification = classify_self_knowledge_request(request_text)
    context = prepare_unified_human_interface_project_context(
        interface_name="aicli",
        session_id=(
            "G65-07-AMBIGUOUS-"
            + request_text.upper().replace(" ", "-").replace(".", "")
        ),
        message=request_text,
        runtime_root=tmp_path,
        workspace=REPOSITORY_ROOT,
        created_at=CREATED_AT,
    )
    read_only = context["governed_read_only_work_result"]
    router = read_only["platform_query_router_response"]

    assert classification["request_classification"] == CLARIFICATION_REQUIRED
    assert classification["objective_inference_allowed"] is False
    assert context["project_objective_inference"] is None
    assert context["admission_precedence"] is None
    assert router["route_status"] == ROUTE_CLARIFICATION_REQUIRED
    assert router["selected_service"] == SELF_KNOWLEDGE_ROUTE
    assert router["service_invoked"] is False
    assert read_only["canonical_presentation"]["presentation_status"] == (
        "PRESENTATION_CLARIFICATION_REQUIRED"
    )


def test_classification_tampering_fails_closed() -> None:
    classification = classify_self_knowledge_request("Show ownership.")
    tampered = deepcopy(classification)
    tampered["query_subject"] = "ARCHITECTURE"

    with pytest.raises(
        FailClosedRuntimeError,
        match="deterministic reconstruction mismatch",
    ):
        validate_self_knowledge_request_classification(tampered)


def test_classifier_has_no_execution_or_discovery_owner_imports() -> None:
    source = (
        REPOSITORY_ROOT
        / "aigol/runtime/self_knowledge_request_classification.py"
    ).read_text(encoding="utf-8")
    forbidden = (
        "os.walk",
        ".glob(",
        ".rglob(",
        "subprocess",
        "conversation_layer",
        "provider_selection",
        "worker_invocation",
        "development_governance",
        "infer_platform_project_objective",
    )

    assert all(token not in source for token in forbidden)
