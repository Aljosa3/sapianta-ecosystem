"""Focused G65-05 regressions for bounded Self Knowledge projection."""

from __future__ import annotations

import ast
from copy import deepcopy
import json
from pathlib import Path
from types import MappingProxyType

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.self_knowledge_evidence_manifest import (
    SELF_KNOWLEDGE_EVIDENCE_MANIFEST_PATH,
)
from aigol.runtime.self_knowledge_query_runtime import (
    AUTHENTICATED_EVIDENCE_UNAVAILABLE,
    AVAILABLE,
    SELF_KNOWLEDGE_QUERY_RESPONSE_BOUNDARY_FLAGS,
    SUPPORTED_QUERY_SUBJECTS,
    UNAVAILABLE,
    create_self_knowledge_query_request,
    execute_self_knowledge_query,
    validate_self_knowledge_query_request,
    validate_self_knowledge_query_response,
)
from aigol.runtime.self_knowledge_snapshot_runtime import (
    build_self_knowledge_snapshot,
)
from aigol.runtime.self_knowledge_snapshot_validation_runtime import (
    validate_authenticated_self_knowledge_snapshot,
)
from aigol.runtime.transport.serialization import replay_hash
import aigol.runtime.self_knowledge_query_runtime as query_runtime


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

EXPECTED_VIEW_CLASSES = {
    "ARCHITECTURE": ("CONSTITUTION", "ENFORCEMENT_AND_LINEAGE"),
    "RUNTIME_INVENTORY": ("CAPABILITY_REGISTRY",),
    "CERTIFIED_CAPABILITIES": ("CAPABILITY_REGISTRY",),
    "OWNERSHIP": ("OWNER_AND_BOUNDARY",),
    "GOVERNANCE_STATE": ("GOVERNANCE_STATE",),
    "EXECUTION_BOUNDARIES": ("ENFORCEMENT_AND_LINEAGE", "OWNER_AND_BOUNDARY"),
    "CERTIFIED_HISTORY": ("CERTIFIED_HISTORY",),
    "KNOWN_LIMITATIONS": ("KNOWN_LIMITATION",),
}


@pytest.fixture(scope="module")
def manifest() -> dict:
    return json.loads(
        (REPOSITORY_ROOT / SELF_KNOWLEDGE_EVIDENCE_MANIFEST_PATH).read_text(encoding="utf-8")
    )


@pytest.fixture(scope="module")
def snapshot(manifest: dict) -> dict:
    return build_self_knowledge_snapshot(
        manifest=manifest,
        repository_root=REPOSITORY_ROOT,
    )


@pytest.fixture(scope="module")
def snapshot_validation(manifest: dict, snapshot: dict) -> dict:
    return validate_authenticated_self_knowledge_snapshot(
        snapshot=snapshot,
        manifest=manifest,
        repository_root=REPOSITORY_ROOT,
    )


def _request(subject: str, snapshot: dict, snapshot_validation: dict) -> dict:
    return create_self_knowledge_query_request(
        query_subject=subject,
        snapshot=snapshot,
        snapshot_validation=snapshot_validation,
    )


@pytest.mark.parametrize("subject", SUPPORTED_QUERY_SUBJECTS)
def test_every_supported_query_subject_projects_only_its_fixed_view(
    subject: str,
    snapshot: dict,
    snapshot_validation: dict,
) -> None:
    request = _request(subject, snapshot, snapshot_validation)
    response = execute_self_knowledge_query(
        request=request,
        snapshot=snapshot,
        snapshot_validation=snapshot_validation,
    )

    assert validate_self_knowledge_query_request(
        request,
        snapshot=snapshot,
        snapshot_validation=snapshot_validation,
    ) == request
    assert validate_self_knowledge_query_response(
        response,
        request=request,
        snapshot=snapshot,
        snapshot_validation=snapshot_validation,
    ) == response
    assert response["query_subject"] == subject
    assert response["projection_status"] == AVAILABLE
    assert response["unavailable_reason"] is None
    assert tuple(response["projected_source_classes"]) == EXPECTED_VIEW_CLASSES[subject]
    assert response["fact_count"] == len(response["facts"]) > 0
    assert response["boundary_flags"] == SELF_KNOWLEDGE_QUERY_RESPONSE_BOUNDARY_FLAGS
    assert all(
        fact["source_class"] in EXPECTED_VIEW_CLASSES[subject]
        for fact in response["facts"]
    )


def test_repeated_query_is_deterministic_and_preserves_exact_sources(
    snapshot: dict,
    snapshot_validation: dict,
) -> None:
    request = _request("EXECUTION_BOUNDARIES", snapshot, snapshot_validation)
    first = execute_self_knowledge_query(
        request=request,
        snapshot=snapshot,
        snapshot_validation=snapshot_validation,
    )
    second = execute_self_knowledge_query(
        request=request,
        snapshot=snapshot,
        snapshot_validation=snapshot_validation,
    )
    expected_facts = [
        record
        for record in snapshot["evidence_records"]
        if record["source_class"] in EXPECTED_VIEW_CLASSES["EXECUTION_BOUNDARIES"]
    ]

    assert first == second
    assert first["facts"] == expected_facts
    assert [
        (fact["source_class"], fact["source_id"], fact["path"])
        for fact in first["facts"]
    ] == sorted(
        (fact["source_class"], fact["source_id"], fact["path"])
        for fact in first["facts"]
    )


def test_request_and_response_bind_exact_snapshot_and_validation_identity(
    snapshot: dict,
    snapshot_validation: dict,
) -> None:
    request = _request("ARCHITECTURE", snapshot, snapshot_validation)
    response = execute_self_knowledge_query(
        request=request,
        snapshot=snapshot,
        snapshot_validation=snapshot_validation,
    )

    assert request["snapshot_hash"] == snapshot["snapshot_hash"]
    assert request["snapshot_validation_hash"] == snapshot_validation["validation_hash"]
    assert response["snapshot_hash"] == snapshot["snapshot_hash"]
    assert response["manifest_hash"] == snapshot["manifest_hash"]
    assert response["snapshot_validation_hash"] == snapshot_validation["validation_hash"]
    response_body = deepcopy(response)
    response_body.pop("response_hash")
    assert response["response_hash"] == replay_hash(response_body)


@pytest.mark.parametrize(
    "subject",
    (
        "architecture",
        "What is the architecture?",
        "ARCHITECTURE OR OWNERSHIP",
        "",
        None,
        ["ARCHITECTURE"],
    ),
)
def test_unsupported_free_form_and_ambiguous_subjects_fail_closed(
    subject,
    snapshot: dict,
    snapshot_validation: dict,
) -> None:
    with pytest.raises(FailClosedRuntimeError, match="unsupported, malformed, free-form, or ambiguous"):
        create_self_knowledge_query_request(
            query_subject=subject,
            snapshot=snapshot,
            snapshot_validation=snapshot_validation,
        )


def test_invalid_and_tampered_snapshots_fail_closed(
    snapshot: dict,
    snapshot_validation: dict,
) -> None:
    invalid = deepcopy(snapshot)
    invalid["artifact_type"] = "NOT_A_SELF_KNOWLEDGE_SNAPSHOT"
    with pytest.raises(FailClosedRuntimeError, match="snapshot artifact type is invalid"):
        create_self_knowledge_query_request(
            query_subject="ARCHITECTURE",
            snapshot=invalid,
            snapshot_validation=snapshot_validation,
        )

    tampered = deepcopy(snapshot)
    original = tampered["evidence_records"][0]["content"]
    tampered["evidence_records"][0]["content"] = (
        ("X" if original[0] != "X" else "Y") + original[1:]
    )
    with pytest.raises(FailClosedRuntimeError, match="content digest mismatch"):
        create_self_knowledge_query_request(
            query_subject="ARCHITECTURE",
            snapshot=tampered,
            snapshot_validation=snapshot_validation,
        )


def test_malformed_request_and_unsuccessful_validation_fail_closed(
    snapshot: dict,
    snapshot_validation: dict,
) -> None:
    malformed = _request("ARCHITECTURE", snapshot, snapshot_validation)
    malformed.pop("snapshot_hash")
    with pytest.raises(FailClosedRuntimeError, match="query request schema is invalid"):
        validate_self_knowledge_query_request(
            malformed,
            snapshot=snapshot,
            snapshot_validation=snapshot_validation,
        )

    unsuccessful = deepcopy(snapshot_validation)
    unsuccessful["validation_status"] = "FAILED"
    body = deepcopy(unsuccessful)
    body.pop("validation_hash")
    unsuccessful["validation_hash"] = replay_hash(body)
    with pytest.raises(FailClosedRuntimeError, match="validation_status binding is invalid"):
        create_self_knowledge_query_request(
            query_subject="ARCHITECTURE",
            snapshot=snapshot,
            snapshot_validation=unsuccessful,
        )


def test_response_tampering_fails_closed(
    snapshot: dict,
    snapshot_validation: dict,
) -> None:
    request = _request("OWNERSHIP", snapshot, snapshot_validation)
    response = execute_self_knowledge_query(
        request=request,
        snapshot=snapshot,
        snapshot_validation=snapshot_validation,
    )
    response["facts"][0]["source_id"] = "TAMPERED"

    with pytest.raises(FailClosedRuntimeError, match="query response hash mismatch"):
        validate_self_knowledge_query_response(
            response,
            request=request,
            snapshot=snapshot,
            snapshot_validation=snapshot_validation,
        )


@pytest.mark.parametrize(
    "authority_field",
    ("objective", "reuse_proof", "authorization", "worker_request", "provider_request", "replay_event", "governance_mutation", "execution_request"),
)
def test_authority_shaped_request_fields_fail_closed(
    authority_field: str,
    snapshot: dict,
    snapshot_validation: dict,
) -> None:
    request = _request("ARCHITECTURE", snapshot, snapshot_validation)
    request[authority_field] = {"requested": True}

    with pytest.raises(FailClosedRuntimeError, match="authority-shaped query field is forbidden"):
        validate_self_knowledge_query_request(
            request,
            snapshot=snapshot,
            snapshot_validation=snapshot_validation,
        )


def test_unavailable_evidence_returns_bounded_unavailable_response(
    monkeypatch,
    snapshot: dict,
    snapshot_validation: dict,
) -> None:
    mapping = dict(query_runtime._VIEW_SOURCE_CLASSES)
    mapping["KNOWN_LIMITATIONS"] = ("AUTHENTICATED_CLASS_WITH_NO_RECORDS",)
    monkeypatch.setattr(query_runtime, "_VIEW_SOURCE_CLASSES", MappingProxyType(mapping))
    request = _request("KNOWN_LIMITATIONS", snapshot, snapshot_validation)
    response = execute_self_knowledge_query(
        request=request,
        snapshot=snapshot,
        snapshot_validation=snapshot_validation,
    )

    assert response["projection_status"] == UNAVAILABLE
    assert response["unavailable_reason"] == AUTHENTICATED_EVIDENCE_UNAVAILABLE
    assert response["fact_count"] == 0
    assert response["facts"] == []
    assert validate_self_knowledge_query_response(
        response,
        request=request,
        snapshot=snapshot,
        snapshot_validation=snapshot_validation,
    ) == response


def test_query_runtime_performs_no_repository_io(
    monkeypatch,
    snapshot: dict,
    snapshot_validation: dict,
) -> None:
    def fail_io(*_args, **_kwargs):
        raise AssertionError("query runtime must not inspect the repository")

    monkeypatch.setattr(Path, "read_bytes", fail_io)
    monkeypatch.setattr(Path, "read_text", fail_io)
    request = _request("GOVERNANCE_STATE", snapshot, snapshot_validation)
    response = execute_self_knowledge_query(
        request=request,
        snapshot=snapshot,
        snapshot_validation=snapshot_validation,
    )
    assert validate_self_knowledge_query_response(
        response,
        request=request,
        snapshot=snapshot,
        snapshot_validation=snapshot_validation,
    ) == response


def test_query_runtime_has_no_discovery_or_constitutional_owner_imports() -> None:
    source = (
        REPOSITORY_ROOT / "aigol/runtime/self_knowledge_query_runtime.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }

    assert "subprocess" not in imports
    assert not any(
        forbidden in imported
        for imported in imports
        for forbidden in (
            "conversation",
            "provider",
            "worker",
            "authorization",
            "governance",
            "replay_runtime",
            "execution_runtime",
        )
    )
    assert "os.walk" not in source
    assert ".rglob(" not in source
    assert ".glob(" not in source
