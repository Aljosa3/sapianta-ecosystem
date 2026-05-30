"""Tests for MEMORY_BASED_RESPONSE_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.constitutional_memory_consultation_activation import activate_constitutional_memory_consultation
from aigol.runtime.intent_classifier import classify_intent
from aigol.runtime.intent_routing_attachment import attach_intent_routing
from aigol.runtime.memory_based_response import (
    CREATED,
    FAILED_CLOSED,
    MEMORY_BASED_RESPONSE_MODEL_V1,
    RESPONSE_TYPE,
    RETURNED,
    create_memory_based_response,
    reconstruct_memory_based_response_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


CLASSIFIED_AT = "2026-05-30T05:00:00+00:00"
ROUTED_AT = "2026-05-30T05:01:00+00:00"
CONSULTED_AT = "2026-05-30T05:02:00+00:00"
RESPONDED_AT = "2026-05-30T05:03:00+00:00"


def _consultation_record(tmp_path) -> dict:
    classification = classify_intent(
        artifact_id="INTENT-CLASSIFICATION-RESPONSE-000001",
        human_request_reference="HUMAN-PROMPT-000001",
        human_prompt="Retrieve Constitutional Memory citation.",
        classification_timestamp=CLASSIFIED_AT,
        replay_reference="CLASSIFICATION-REPLAY-RESPONSE-000001",
        replay_dir=tmp_path / "classification",
    )
    routing = attach_intent_routing(
        routing_record_id="INTENT-ROUTING-RESPONSE-000001",
        intent_classification_artifact=classification["intent_classification_artifact"],
        routing_timestamp=ROUTED_AT,
        replay_reference="ROUTING-REPLAY-RESPONSE-000001",
        replay_dir=tmp_path / "routing",
    )
    consultation = activate_constitutional_memory_consultation(
        consultation_id="CONSTITUTIONAL-MEMORY-CONSULTATION-RESPONSE-000001",
        intent_routing_attachment_record=routing["intent_routing_attachment_record"],
        retrieval_scope="CONSTITUTIONAL_INVARIANTS",
        query="Retrieve constitutional invariant references.",
        artifact_query="CONSTITUTIONAL_INVARIANTS",
        consultation_timestamp=CONSULTED_AT,
        replay_reference="CONSULTATION-REPLAY-RESPONSE-000001",
        replay_dir=tmp_path / "consultation",
    )
    return consultation["constitutional_memory_consultation_record"]


def _response(tmp_path, consultation_record: dict | None = None, **overrides) -> dict:
    args = {
        "response_id": "MEMORY-BASED-RESPONSE-000001",
        "prompt_id": "HUMAN-PROMPT-000001",
        "constitutional_memory_consultation_record": consultation_record
        if consultation_record is not None
        else _consultation_record(tmp_path),
        "created_at": RESPONDED_AT,
        "replay_dir": tmp_path / "response",
    }
    args.update(overrides)
    return create_memory_based_response(**args)


def _rehash_artifact(artifact: dict) -> None:
    artifact.pop("artifact_hash", None)
    artifact["artifact_hash"] = replay_hash(artifact)


def test_valid_citation_bundle_creates_memory_based_response(tmp_path) -> None:
    consultation_record = _consultation_record(tmp_path)
    capture = _response(tmp_path, consultation_record)
    response = capture["memory_based_response"]
    replay = capture["memory_based_response_replay"]
    reconstructed = reconstruct_memory_based_response_replay(tmp_path / "response")

    assert response["response_id"] == "MEMORY-BASED-RESPONSE-000001"
    assert response["prompt_id"] == "HUMAN-PROMPT-000001"
    assert response["citation_bundle_id"] == consultation_record["citation_bundle"]["retrieval_id"]
    assert response["response_type"] == RESPONSE_TYPE
    assert response["response_model"] == MEMORY_BASED_RESPONSE_MODEL_V1
    assert response["response_status"] == CREATED
    assert response["authority"] is False
    assert response["execution_capable"] is False
    assert response["replay_visible"] is True
    assert replay["replay_event"] == RETURNED
    assert reconstructed["response_status"] == CREATED
    assert reconstructed["citation_count"] == len(response["citations"])


def test_missing_citation_bundle_fails_closed(tmp_path) -> None:
    consultation_record = _consultation_record(tmp_path)
    consultation_record["citation_bundle"] = None
    _rehash_artifact(consultation_record)
    capture = _response(tmp_path, consultation_record)

    assert capture["memory_based_response"]["response_status"] == FAILED_CLOSED
    assert "citation bundle missing" in capture["memory_based_response"]["failure_reason"]
    assert capture["memory_based_response"]["response_text"] == ""
    assert capture["memory_based_response"]["citations"] == []


def test_corrupt_citation_bundle_fails_closed(tmp_path) -> None:
    consultation_record = _consultation_record(tmp_path)
    consultation_record["citation_bundle"]["citation_count"] = 999
    _rehash_artifact(consultation_record)
    capture = _response(tmp_path, consultation_record)

    assert capture["memory_based_response"]["response_status"] == FAILED_CLOSED
    assert "hash mismatch" in capture["memory_based_response"]["failure_reason"]


def test_empty_citation_bundle_fails_closed(tmp_path) -> None:
    consultation_record = _consultation_record(tmp_path)
    consultation_record["citation_bundle"]["citations"] = []
    consultation_record["citation_bundle"]["citation_count"] = 0
    _rehash_artifact(consultation_record["citation_bundle"])
    _rehash_artifact(consultation_record)
    capture = _response(tmp_path, consultation_record)

    assert capture["memory_based_response"]["response_status"] == FAILED_CLOSED
    assert "citation bundle empty" in capture["memory_based_response"]["failure_reason"]


def test_evidence_unavailable_fails_closed(tmp_path) -> None:
    consultation_record = _consultation_record(tmp_path)
    consultation_record["consultation_status"] = FAILED_CLOSED
    _rehash_artifact(consultation_record)
    capture = _response(tmp_path, consultation_record)

    assert capture["memory_based_response"]["response_status"] == FAILED_CLOSED
    assert "evidence unavailable" in capture["memory_based_response"]["failure_reason"]


def test_replay_reconstruction_succeeds(tmp_path) -> None:
    consultation_record = _consultation_record(tmp_path)
    _response(tmp_path, consultation_record)
    reconstructed = reconstruct_memory_based_response_replay(tmp_path / "response")

    assert reconstructed["response_id"] == "MEMORY-BASED-RESPONSE-000001"
    assert reconstructed["prompt_id"] == "HUMAN-PROMPT-000001"
    assert reconstructed["replay_visible"] is True
    assert reconstructed["authority"] is False
    assert reconstructed["execution_capable"] is False
    assert reconstructed["provider_invoked"] is False
    assert reconstructed["worker_invoked"] is False


def test_response_contains_only_cited_evidence(tmp_path) -> None:
    consultation_record = _consultation_record(tmp_path)
    response = _response(tmp_path, consultation_record)["memory_based_response"]
    cited_identities = {citation["artifact_identity"] for citation in response["citations"]}
    cited_paths = {citation["artifact_path"] for citation in response["citations"]}

    assert cited_identities == {"CONSTITUTIONAL_INVARIANTS"}
    assert cited_paths == {"docs/governance/CONSTITUTIONAL_INVARIANTS.md"}
    assert "CONSTITUTIONAL_INVARIANTS" in response["response_text"]
    assert "docs/governance/CONSTITUTIONAL_INVARIANTS.md" in response["response_text"]
    assert "not authorization" in response["response_text"]
    assert "execution request" in response["response_text"]


def test_no_provider_worker_or_authority_fields_introduced(tmp_path) -> None:
    response = _response(tmp_path)["memory_based_response"]
    forbidden = {
        "authorization_decision",
        "governance_decision",
        "execution_request",
        "provider_request",
        "worker_request",
        "worker_instruction",
        "provider_command",
        "worker_command",
        "conversation_response",
    }

    assert forbidden.isdisjoint(response)
    assert response["authority"] is False
    assert response["execution_capable"] is False


def test_replay_artifacts_are_created(tmp_path) -> None:
    _response(tmp_path)

    created = tmp_path / "response" / "000_memory_based_response_created.json"
    returned = tmp_path / "response" / "001_memory_based_response_returned.json"
    assert created.exists()
    assert returned.exists()
    assert json.loads(created.read_text(encoding="utf-8"))["event_type"] == CREATED
    assert json.loads(returned.read_text(encoding="utf-8"))["event_type"] == RETURNED


def test_append_only_replay_violation_fails_closed(tmp_path) -> None:
    consultation_record = _consultation_record(tmp_path)
    first = _response(tmp_path, consultation_record)
    second = _response(tmp_path, consultation_record)
    reconstructed = reconstruct_memory_based_response_replay(tmp_path / "response")

    assert first["memory_based_response"]["response_status"] == CREATED
    assert second["memory_based_response"]["response_status"] == FAILED_CLOSED
    assert "already exists" in second["memory_based_response"]["failure_reason"]
    assert reconstructed["response_status"] == CREATED


def test_replay_reconstruction_detects_response_corruption(tmp_path) -> None:
    _response(tmp_path)
    path = tmp_path / "response" / "000_memory_based_response_created.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["response_text"] = "tampered"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_memory_based_response_replay(tmp_path / "response")


def test_replay_reconstruction_detects_returned_corruption(tmp_path) -> None:
    _response(tmp_path)
    path = tmp_path / "response" / "001_memory_based_response_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["response_reference"] = "OTHER"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_memory_based_response_replay(tmp_path / "response")


def test_replay_reconstruction_detects_ordering_corruption(tmp_path) -> None:
    _response(tmp_path)
    path = tmp_path / "response" / "001_memory_based_response_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["replay_step"] = "memory_based_response_created"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_memory_based_response_replay(tmp_path / "response")


def test_no_provider_worker_execution_or_network_runtime_imports() -> None:
    import aigol.runtime.memory_based_response as response

    source = inspect.getsource(response)

    assert "subprocess" not in source
    assert "os.system" not in source
    assert "requests" not in source
    assert "urllib" not in source
    assert "socket" not in source
    assert "openai" not in source.lower()
    assert "anthropic" not in source.lower()
    assert "async " not in source
    assert "await " not in source
    assert "threading" not in source
    assert "multiprocessing" not in source
