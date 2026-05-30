"""Tests for CONSTITUTIONAL_MEMORY_ACCESS_PATH_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.constitutional_memory_access import (
    FAILED,
    REFERENCE_RESULT,
    REQUESTED,
    RETRIEVED,
    RETURNED,
    retrieve_constitutional_memory,
    reconstruct_constitutional_memory_retrieval_replay,
)
from aigol.runtime.models import FailClosedRuntimeError


CREATED_AT = "2026-05-30T01:00:00+00:00"


def _run(tmp_path, **overrides) -> dict:
    args = {
        "retrieval_id": "CONSTITUTIONAL-MEMORY-RETRIEVAL-000001",
        "requested_by": "OPERATOR",
        "retrieval_scope": "AUTHORITY_INVARIANTS",
        "query": "Retrieve authority boundary references.",
        "artifact_query": "CANONICAL_AUTHORITY_MODEL",
        "created_at": CREATED_AT,
        "replay_dir": tmp_path,
    }
    args.update(overrides)
    return retrieve_constitutional_memory(**args)


def test_successful_retrieval_returns_reference_only_citation_bundle(tmp_path) -> None:
    capture = _run(tmp_path)
    replay = reconstruct_constitutional_memory_retrieval_replay(tmp_path)
    result = capture["retrieval_result"]
    citation = capture["citation_bundle"]["citations"][0]

    assert result["state"] == RETURNED
    assert result["result_type"] == REFERENCE_RESULT
    assert result["authorization_decision"] is None
    assert result["governance_decision"] is None
    assert result["execution_request"] is None
    assert citation["artifact_identity"] == "CANONICAL_AUTHORITY_MODEL"
    assert citation["artifact_classification"] == "CANONICAL"
    assert citation["artifact_path"] == "governance/CANONICAL_AUTHORITY_MODEL_V1.md"
    assert citation["retrieval_timestamp"] == CREATED_AT
    assert citation["authority_status"] == "REFERENCE_ONLY"
    assert replay["lifecycle_transitions"] == [REQUESTED, RETRIEVED, RETURNED]
    assert replay["citation_count"] == 1


def test_scope_retrieval_can_return_multiple_citations(tmp_path) -> None:
    capture = _run(tmp_path, artifact_query=None, retrieval_scope="OPERATIONAL_BASELINES")

    assert capture["retrieval_result"]["state"] == RETURNED
    assert capture["retrieval_result"]["citation_count"] >= 2
    assert all(citation["citation_reference"] for citation in capture["retrieval_result"]["returned_citations"])


def test_multiple_retrievals_are_replay_visible(tmp_path) -> None:
    first = _run(tmp_path / "first")
    second = _run(
        tmp_path / "second",
        retrieval_id="CONSTITUTIONAL-MEMORY-RETRIEVAL-000002",
        artifact_query="CONSTITUTIONAL_INVARIANTS",
        retrieval_scope="CONSTITUTIONAL_INVARIANTS",
    )

    assert first["retrieval_result"]["final_status"] == "RETURNED_REFERENCE_RESULT"
    assert second["retrieval_result"]["final_status"] == "RETURNED_REFERENCE_RESULT"
    assert reconstruct_constitutional_memory_retrieval_replay(tmp_path / "first")["replay_visible"] is True
    assert reconstruct_constitutional_memory_retrieval_replay(tmp_path / "second")["replay_visible"] is True


def test_missing_artifact_fails_closed(tmp_path) -> None:
    catalog = {
        "MISSING_ARTIFACT": {
            "path": "governance/DOES_NOT_EXIST.md",
            "classification": "CANONICAL",
            "layer": "M0_CONSTITUTIONAL_SOURCE",
            "scopes": ["CONSTITUTIONAL_INVARIANTS"],
        }
    }
    capture = _run(
        tmp_path,
        retrieval_scope="CONSTITUTIONAL_INVARIANTS",
        artifact_query="MISSING_ARTIFACT",
        artifact_catalog=catalog,
    )

    assert capture["retrieval_result"]["state"] == FAILED
    assert "artifact missing" in capture["retrieval_result"]["failure_reason"]
    assert reconstruct_constitutional_memory_retrieval_replay(tmp_path)["final_status"] == FAILED


def test_ambiguous_artifact_fails_closed(tmp_path) -> None:
    capture = _run(
        tmp_path,
        retrieval_scope="CONSTITUTIONAL_INVARIANTS",
        artifact_query="CONSTITUTIONAL",
    )

    assert capture["retrieval_result"]["state"] == FAILED
    assert "ambiguous" in capture["retrieval_result"]["failure_reason"]


def test_multiple_canonical_matches_fail_closed(tmp_path) -> None:
    capture = _run(
        tmp_path,
        retrieval_scope="GOVERNANCE_REVIEWS",
        artifact_query="MODEL",
    )

    assert capture["retrieval_result"]["state"] == FAILED
    assert "ambiguous" in capture["retrieval_result"]["failure_reason"]


def test_invalid_artifact_fails_closed(tmp_path) -> None:
    invalid = tmp_path / "invalid.json"
    invalid.write_text("{not valid json", encoding="utf-8")
    catalog = {
        "INVALID_ARTIFACT": {
            "path": str(invalid),
            "classification": "CANONICAL",
            "layer": "M0_CONSTITUTIONAL_SOURCE",
            "scopes": ["CONSTITUTIONAL_INVARIANTS"],
        }
    }
    capture = _run(
        tmp_path / "replay",
        retrieval_scope="CONSTITUTIONAL_INVARIANTS",
        artifact_query="INVALID_ARTIFACT",
        artifact_catalog=catalog,
        repository_root="/",
    )

    assert capture["retrieval_result"]["state"] == FAILED
    assert "not valid JSON" in capture["retrieval_result"]["failure_reason"]


def test_invalid_classification_fails_closed(tmp_path) -> None:
    catalog = {
        "BAD_CLASSIFICATION": {
            "path": "docs/governance/CONSTITUTIONAL_INVARIANTS.md",
            "classification": "AUTHORITATIVE_EXECUTION",
            "layer": "M0_CONSTITUTIONAL_SOURCE",
            "scopes": ["CONSTITUTIONAL_INVARIANTS"],
        }
    }
    capture = _run(
        tmp_path,
        retrieval_scope="CONSTITUTIONAL_INVARIANTS",
        artifact_query="BAD_CLASSIFICATION",
        artifact_catalog=catalog,
    )

    assert capture["retrieval_result"]["state"] == FAILED
    assert "classification" in capture["retrieval_result"]["failure_reason"]


@pytest.mark.parametrize("requested_by", ["PROVIDER", "WORKER"])
def test_provider_and_worker_retrieval_are_forbidden(tmp_path, requested_by: str) -> None:
    capture = _run(tmp_path, requested_by=requested_by)

    assert capture["retrieval_request"]["state"] == FAILED
    assert capture["retrieval_result"]["state"] == FAILED
    assert "forbidden" in capture["retrieval_result"]["failure_reason"]
    assert reconstruct_constitutional_memory_retrieval_replay(tmp_path)["lifecycle_transitions"] == [
        FAILED,
        FAILED,
        FAILED,
    ]


def test_runtime_validation_requires_governance_context(tmp_path) -> None:
    capture = _run(tmp_path, requested_by="RUNTIME_VALIDATION_STEP", governance_context=False)

    assert capture["retrieval_result"]["state"] == FAILED
    assert "governance context" in capture["retrieval_result"]["failure_reason"]
    assert reconstruct_constitutional_memory_retrieval_replay(tmp_path)["final_status"] == FAILED


def test_runtime_validation_with_governance_context_is_allowed(tmp_path) -> None:
    capture = _run(tmp_path, requested_by="RUNTIME_VALIDATION_STEP", governance_context=True)

    assert capture["retrieval_result"]["state"] == RETURNED


@pytest.mark.parametrize(
    "query",
    [
        "authorize execution",
        "create an execution request",
        "write governance changes",
        "return worker command",
        "generate proposal generation",
        "provide correction instruction",
    ],
)
def test_authority_or_execution_bearing_request_rejected(tmp_path, query: str) -> None:
    capture = _run(tmp_path, query=query)

    assert capture["retrieval_request"]["state"] == FAILED
    assert capture["retrieval_result"]["state"] == FAILED
    assert "authority-bearing" in capture["retrieval_result"]["failure_reason"]
    replay = reconstruct_constitutional_memory_retrieval_replay(tmp_path)
    assert replay["lifecycle_transitions"] == [FAILED, FAILED, FAILED]


def test_invalid_index_reference_fails_closed(tmp_path) -> None:
    capture = _run(tmp_path, retrieval_scope="VECTOR_MEMORY")

    assert capture["retrieval_result"]["state"] == FAILED
    assert "index reference" in capture["retrieval_result"]["failure_reason"]


def test_replay_reconstruction_detects_corruption(tmp_path) -> None:
    _run(tmp_path)
    artifact_path = tmp_path / "001_citation_bundle.json"
    wrapper = json.loads(artifact_path.read_text(encoding="utf-8"))
    wrapper["artifact"]["citation_count"] = 999
    artifact_path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_constitutional_memory_retrieval_replay(tmp_path)


def test_replay_reconstruction_detects_ordering_corruption(tmp_path) -> None:
    _run(tmp_path)
    artifact_path = tmp_path / "001_citation_bundle.json"
    wrapper = json.loads(artifact_path.read_text(encoding="utf-8"))
    wrapper["replay_step"] = "retrieval_result"
    artifact_path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_constitutional_memory_retrieval_replay(tmp_path)


def test_append_only_replay_violation_fails_closed(tmp_path) -> None:
    _run(tmp_path)
    capture = _run(tmp_path)

    assert capture["retrieval_result"]["state"] == FAILED
    assert "already exists" in capture["retrieval_result"]["failure_reason"]


def test_no_expanded_runtime_surface_imports() -> None:
    import aigol.runtime.constitutional_memory_access as access

    source = inspect.getsource(access)

    assert "subprocess" not in source
    assert "os.system" not in source
    assert "requests" not in source
    assert "urllib" not in source
    assert "socket" not in source
    assert "async " not in source
    assert "await " not in source
    assert "threading" not in source
    assert "multiprocessing" not in source
