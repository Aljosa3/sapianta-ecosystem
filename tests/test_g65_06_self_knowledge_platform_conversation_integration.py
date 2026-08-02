"""Focused G65-06 Platform Core and Conversation integration regressions."""

from __future__ import annotations

import ast
from copy import deepcopy
import inspect
import json
from pathlib import Path
from types import MappingProxyType

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_presentation_layer import (
    PRESENTATION_MISSING_EVIDENCE,
    PRESENTATION_READY,
    SELF_KNOWLEDGE_SERVICE,
    present_platform_response,
    validate_platform_presentation,
)
from aigol.runtime.platform_query_router import (
    route_explicit_self_knowledge_query,
)
from aigol.runtime.self_knowledge_evidence_manifest import (
    SELF_KNOWLEDGE_EVIDENCE_MANIFEST_PATH,
)
from aigol.runtime.self_knowledge_platform_conversation_integration import (
    SELF_KNOWLEDGE_INTEGRATION_BOUNDARY_FLAGS,
    create_explicit_self_knowledge_conversation_request,
    run_platform_core_self_knowledge_query,
    validate_explicit_self_knowledge_conversation_request,
    validate_platform_core_self_knowledge_response,
)
from aigol.runtime.self_knowledge_query_runtime import SUPPORTED_QUERY_SUBJECTS
from aigol.runtime.self_knowledge_snapshot_runtime import build_self_knowledge_snapshot
from aigol.runtime.transport.serialization import replay_hash
import aigol.runtime.self_knowledge_platform_conversation_integration as integration
import aigol.runtime.self_knowledge_query_runtime as query_runtime


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("subject", SUPPORTED_QUERY_SUBJECTS)
def test_each_subject_reaches_self_knowledge_through_platform_core(subject: str) -> None:
    response = route_explicit_self_knowledge_query(
        request=f"/self-knowledge {subject}",
        repository_root=str(REPOSITORY_ROOT),
    )

    assert validate_platform_core_self_knowledge_response(response) == response
    assert response["query_subject"] == subject
    assert response["projection_status"] == "AVAILABLE"
    assert response["query_response"]["query_subject"] == subject
    assert response["snapshot_hash"] == response["query_response"]["snapshot_hash"]
    assert response["boundary_flags"] == SELF_KNOWLEDGE_INTEGRATION_BOUNDARY_FLAGS
    assert response["source_references"]


def test_both_explicit_bounded_request_forms_map_deterministically() -> None:
    slash = create_explicit_self_knowledge_conversation_request(
        "/self-knowledge ARCHITECTURE"
    )
    token = create_explicit_self_knowledge_conversation_request(
        "SELF_KNOWLEDGE:ARCHITECTURE"
    )

    assert slash["query_subject"] == token["query_subject"] == "ARCHITECTURE"
    assert slash["mapping_rule"] == "EXPLICIT_SLASH_COMMAND"
    assert token["mapping_rule"] == "EXPLICIT_TOKEN_BINDING"
    assert validate_explicit_self_knowledge_conversation_request(slash) == slash
    assert validate_explicit_self_knowledge_conversation_request(token) == token


def test_repeated_platform_and_conversation_responses_are_deterministic() -> None:
    first = route_explicit_self_knowledge_query(
        request="/self-knowledge OWNERSHIP",
        repository_root=str(REPOSITORY_ROOT),
    )
    second = route_explicit_self_knowledge_query(
        request="/self-knowledge OWNERSHIP",
        repository_root=str(REPOSITORY_ROOT),
    )
    first_presentation = present_platform_response(first)
    second_presentation = present_platform_response(second)

    assert first == second
    assert first_presentation == second_presentation
    assert validate_platform_presentation(first_presentation) == first_presentation


def test_source_references_and_digests_are_preserved_exactly() -> None:
    response = route_explicit_self_knowledge_query(
        request="/self-knowledge EXECUTION_BOUNDARIES",
        repository_root=str(REPOSITORY_ROOT),
    )
    expected = [
        {
            "source_id": fact["source_id"],
            "source_class": fact["source_class"],
            "path": fact["path"],
            "sha256": fact["sha256"],
            "authority_class": fact["authority_class"],
            "schema_or_section_identifier": fact["schema_or_section_identifier"],
            "evidence_record_hash": fact["evidence_record_hash"],
        }
        for fact in response["query_response"]["facts"]
    ]

    assert response["source_references"] == expected
    presentation = present_platform_response(response)
    assert presentation["answer"]["source_references"] == expected
    assert presentation["evidence"] == expected
    assert presentation["sources"] == [reference["path"] for reference in expected]


def test_invalid_manifest_is_rejected(monkeypatch) -> None:
    manifest = json.loads(
        (REPOSITORY_ROOT / SELF_KNOWLEDGE_EVIDENCE_MANIFEST_PATH).read_text(encoding="utf-8")
    )
    manifest["sources"][0]["sha256"] = "sha256:" + "0" * 64
    manifest_body = deepcopy(manifest)
    manifest_body.pop("manifest_hash")
    manifest["manifest_hash"] = replay_hash(manifest_body)
    monkeypatch.setattr(integration, "_load_authenticated_manifest", lambda _root: manifest)

    with pytest.raises(FailClosedRuntimeError, match="source inventory or digest binding"):
        run_platform_core_self_knowledge_query(
            request_text="/self-knowledge ARCHITECTURE",
            repository_root=REPOSITORY_ROOT,
        )


def test_invalid_snapshot_is_rejected(monkeypatch) -> None:
    manifest = integration._load_authenticated_manifest(REPOSITORY_ROOT)
    invalid_snapshot = build_self_knowledge_snapshot(
        manifest=manifest,
        repository_root=REPOSITORY_ROOT,
    )
    invalid_snapshot["artifact_type"] = "INVALID_SNAPSHOT"
    monkeypatch.setattr(
        integration,
        "build_self_knowledge_snapshot",
        lambda **_kwargs: deepcopy(invalid_snapshot),
    )

    with pytest.raises(FailClosedRuntimeError, match="snapshot artifact_type binding is invalid"):
        run_platform_core_self_knowledge_query(
            request_text="/self-knowledge ARCHITECTURE",
            repository_root=REPOSITORY_ROOT,
        )


@pytest.mark.parametrize(
    "request_text",
    (
        "/self-knowledge UNKNOWN",
        "/self-knowledge architecture",
        "/self-knowledge ARCHITECTURE OWNERSHIP",
        "SELF_KNOWLEDGE:",
        "Tell me about the architecture",
        "ARCHITECTURE",
    ),
)
def test_unknown_ambiguous_and_free_form_requests_fail_closed(request_text: str) -> None:
    with pytest.raises(FailClosedRuntimeError, match="explicit bounded|unknown, ambiguous"):
        route_explicit_self_knowledge_query(
            request=request_text,
            repository_root=str(REPOSITORY_ROOT),
        )


def test_authority_shaped_request_artifact_is_rejected() -> None:
    request = create_explicit_self_knowledge_conversation_request(
        "/self-knowledge ARCHITECTURE"
    )
    request["authorization"] = {"requested": True}

    with pytest.raises(FailClosedRuntimeError, match="request schema is invalid"):
        validate_explicit_self_knowledge_conversation_request(request)


def test_platform_response_tampering_is_rejected() -> None:
    response = route_explicit_self_knowledge_query(
        request="/self-knowledge GOVERNANCE_STATE",
        repository_root=str(REPOSITORY_ROOT),
    )
    response["source_references"][0]["sha256"] = "sha256:" + "f" * 64

    with pytest.raises(FailClosedRuntimeError, match="source references are invalid"):
        validate_platform_core_self_knowledge_response(response)


def test_conversation_rendering_is_explicitly_non_authoritative() -> None:
    response = route_explicit_self_knowledge_query(
        request="/self-knowledge KNOWN_LIMITATIONS",
        repository_root=str(REPOSITORY_ROOT),
    )
    presentation = present_platform_response(response)

    assert presentation["presentation_status"] == PRESENTATION_READY
    assert presentation["service"] == SELF_KNOWLEDGE_SERVICE
    assert presentation["summary"].startswith(
        "NON-AUTHORITATIVE READ-ONLY SELF KNOWLEDGE"
    )
    assert presentation["answer"]["authority_label"] == (
        "NON_AUTHORITATIVE_READ_ONLY_SELF_KNOWLEDGE"
    )
    assert presentation["answer"]["conversation_authority"] is False
    assert presentation["answer"]["snapshot_identity"]["hash"] == response["snapshot_hash"]
    assert presentation["answer"]["snapshot_digest"] == response["snapshot_hash"]
    assert presentation["answer"]["limitation_state"] == (
        "AUTHENTICATED_LIMITATIONS_PRESENT"
    )
    for field in (
        "objective_created",
        "g47_evidence_created",
        "authorization_created",
        "worker_invoked",
        "provider_invoked",
        "replay_authority",
        "execution_evidence_created",
    ):
        assert presentation["answer"][field] is False
    assert validate_platform_presentation(presentation) == presentation


def test_unavailable_projection_renders_without_inference(monkeypatch) -> None:
    mapping = dict(query_runtime._VIEW_SOURCE_CLASSES)
    mapping["KNOWN_LIMITATIONS"] = ("AUTHENTICATED_CLASS_WITH_NO_RECORDS",)
    monkeypatch.setattr(query_runtime, "_VIEW_SOURCE_CLASSES", MappingProxyType(mapping))
    response = route_explicit_self_knowledge_query(
        request="/self-knowledge KNOWN_LIMITATIONS",
        repository_root=str(REPOSITORY_ROOT),
    )
    presentation = present_platform_response(response)

    assert presentation["presentation_status"] == PRESENTATION_MISSING_EVIDENCE
    assert presentation["answer"]["projection_status"] == "UNAVAILABLE"
    assert presentation["answer"]["facts"] == []
    assert presentation["answer"]["limitation_state"] == (
        "AUTHENTICATED_LIMITATIONS_UNAVAILABLE"
    )
    assert presentation["recommended_next_step"] == (
        "The requested authenticated evidence is unavailable; no answer was inferred."
    )


def test_integration_imports_no_authority_or_execution_owners() -> None:
    source = (
        REPOSITORY_ROOT
        / "aigol/runtime/self_knowledge_platform_conversation_integration.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    explicit_router_source = inspect.getsource(route_explicit_self_knowledge_query)

    assert not any(
        forbidden in imported
        for imported in imports
        for forbidden in (
            "objective",
            "reuse_proof",
            "development_governance",
            "authorization",
            "worker",
            "provider",
            "replay_runtime",
            "execution_runtime",
        )
    )
    assert "route_platform_query(" not in explicit_router_source
    assert "resolve_development_intent" not in explicit_router_source
    assert "query_platform_knowledge" not in explicit_router_source
    assert "os.walk" not in source
    assert ".rglob(" not in source
    assert ".glob(" not in source
