"""Tests for CONSTITUTIONAL_MEMORY_CONSULTATION_ACTIVATION_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.constitutional_memory_consultation_activation import (
    CONSULTATION_VERSION,
    CONSULTED,
    FAILED_CLOSED,
    activate_constitutional_memory_consultation,
    reconstruct_constitutional_memory_consultation_replay,
)
from aigol.runtime.intent_classifier import (
    CONSTITUTIONAL_MEMORY_CONSULTATION,
    CONVERSATION,
    classify_intent,
)
from aigol.runtime.intent_routing_attachment import attach_intent_routing
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


CLASSIFIED_AT = "2026-05-30T04:00:00+00:00"
ROUTED_AT = "2026-05-30T04:01:00+00:00"
CONSULTED_AT = "2026-05-30T04:02:00+00:00"


def _routing_record(tmp_path, prompt: str = "Retrieve Constitutional Memory citation.") -> dict:
    classification = classify_intent(
        artifact_id="INTENT-CLASSIFICATION-MEMORY-000001",
        human_request_reference="HUMAN-REQUEST-MEMORY-000001",
        human_prompt=prompt,
        classification_timestamp=CLASSIFIED_AT,
        replay_reference="CLASSIFICATION-REPLAY-MEMORY-000001",
        replay_dir=tmp_path / "classification",
    )
    routing = attach_intent_routing(
        routing_record_id="INTENT-ROUTING-MEMORY-000001",
        intent_classification_artifact=classification["intent_classification_artifact"],
        routing_timestamp=ROUTED_AT,
        replay_reference="ROUTING-REPLAY-MEMORY-000001",
        replay_dir=tmp_path / "routing",
    )
    return routing["intent_routing_attachment_record"]


def _activate(tmp_path, routing_record: dict, **overrides) -> dict:
    args = {
        "consultation_id": "CONSTITUTIONAL-MEMORY-CONSULTATION-000001",
        "intent_routing_attachment_record": routing_record,
        "retrieval_scope": "CONSTITUTIONAL_INVARIANTS",
        "query": "Retrieve constitutional invariant references.",
        "artifact_query": "CONSTITUTIONAL_INVARIANTS",
        "consultation_timestamp": CONSULTED_AT,
        "replay_reference": "CONSULTATION-REPLAY-000001",
        "replay_dir": tmp_path / "consultation",
    }
    args.update(overrides)
    return activate_constitutional_memory_consultation(**args)


def _rehash_artifact(artifact: dict) -> None:
    artifact.pop("artifact_hash", None)
    artifact["artifact_hash"] = replay_hash(artifact)


def test_successful_consultation_returns_reference_only_citation_bundle(tmp_path) -> None:
    routing_record = _routing_record(tmp_path)
    capture = _activate(tmp_path, routing_record)
    record = capture["constitutional_memory_consultation_record"]
    replay = capture["constitutional_memory_consultation_replay"]
    reconstructed = reconstruct_constitutional_memory_consultation_replay(tmp_path / "consultation")
    bundle = record["citation_bundle"]
    citation = bundle["citations"][0]

    assert record["record_type"] == "CONSTITUTIONAL_MEMORY_CONSULTATION_RECORD"
    assert record["consultation_status"] == CONSULTED
    assert record["consultation_version"] == CONSULTATION_VERSION
    assert record["routing_record_reference"] == routing_record["routing_record_id"]
    assert record["routing_record_hash"] == routing_record["artifact_hash"]
    assert bundle["bundle_type"] == "CONSTITUTIONAL_MEMORY_CONSULTATION_CITATION_BUNDLE"
    assert bundle["citation_count"] == 1
    assert citation["artifact_identity"] == "CONSTITUTIONAL_INVARIANTS"
    assert citation["citation_reference"]
    assert citation["authority_status"] == "REFERENCE_ONLY"
    assert replay["reference_only"] is True
    assert reconstructed["consultation_status"] == CONSULTED
    assert reconstructed["citation_count"] == 1
    assert reconstructed["retrieval_performed_during_reconstruction"] is False


def test_consultation_record_contains_no_authority_or_activation_fields(tmp_path) -> None:
    routing_record = _routing_record(tmp_path)
    record = _activate(tmp_path, routing_record)["constitutional_memory_consultation_record"]
    bundle = record["citation_bundle"]

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
    assert forbidden.isdisjoint(record)
    assert forbidden.isdisjoint(bundle)
    assert record["memory_retrieval_id"] == "CONSTITUTIONAL-MEMORY-CONSULTATION-000001:MEMORY_RETRIEVAL"
    assert record["reconstruction_metadata"]["retrieval_performed_during_reconstruction"] is False


def test_replay_generation_includes_wrapper_and_memory_access_evidence(tmp_path) -> None:
    routing_record = _routing_record(tmp_path)
    _activate(tmp_path, routing_record)

    assert (tmp_path / "consultation" / "000_constitutional_memory_consultation_record.json").exists()
    assert (tmp_path / "consultation" / "001_constitutional_memory_consultation_replay.json").exists()
    assert (tmp_path / "consultation" / "constitutional_memory_access" / "000_retrieval_request.json").exists()
    assert (tmp_path / "consultation" / "constitutional_memory_access" / "001_citation_bundle.json").exists()
    assert (tmp_path / "consultation" / "constitutional_memory_access" / "002_retrieval_result.json").exists()


def test_append_only_replay_violation_fails_closed(tmp_path) -> None:
    routing_record = _routing_record(tmp_path)
    first = _activate(tmp_path, routing_record)
    second = _activate(tmp_path, routing_record)
    reconstructed = reconstruct_constitutional_memory_consultation_replay(tmp_path / "consultation")

    assert first["constitutional_memory_consultation_record"]["consultation_status"] == CONSULTED
    assert second["constitutional_memory_consultation_record"]["consultation_status"] == FAILED_CLOSED
    assert "already exists" in second["constitutional_memory_consultation_record"]["failure_reason"]
    assert reconstructed["consultation_status"] == CONSULTED


def test_invalid_routing_record_rejected(tmp_path) -> None:
    capture = _activate(tmp_path, {"record_type": "NOT_ROUTING"})

    assert capture["constitutional_memory_consultation_record"]["consultation_status"] == FAILED_CLOSED
    assert "invalid routing record" in capture["constitutional_memory_consultation_record"]["failure_reason"]


def test_non_memory_destination_rejected(tmp_path) -> None:
    routing_record = _routing_record(tmp_path, prompt="Explain how AiGOL preserves replay.")
    capture = _activate(tmp_path, routing_record)

    assert routing_record["destination"] == CONVERSATION
    assert capture["constitutional_memory_consultation_record"]["consultation_status"] == FAILED_CLOSED
    assert "non-memory destination" in capture["constitutional_memory_consultation_record"]["failure_reason"]


def test_corrupt_routing_record_rejected(tmp_path) -> None:
    routing_record = _routing_record(tmp_path)
    routing_record["destination"] = CONVERSATION
    capture = _activate(tmp_path, routing_record)

    assert capture["constitutional_memory_consultation_record"]["consultation_status"] == FAILED_CLOSED
    assert "hash mismatch" in capture["constitutional_memory_consultation_record"]["failure_reason"]


def test_authority_bearing_routing_record_rejected(tmp_path) -> None:
    routing_record = _routing_record(tmp_path)
    routing_record["execution_request"] = {"execute": True}
    _rehash_artifact(routing_record)
    capture = _activate(tmp_path, routing_record)

    assert capture["constitutional_memory_consultation_record"]["consultation_status"] == FAILED_CLOSED
    assert "authority-bearing routing record" in capture["constitutional_memory_consultation_record"]["failure_reason"]


def test_missing_source_fails_closed(tmp_path) -> None:
    routing_record = _routing_record(tmp_path)
    catalog = {
        "MISSING_ARTIFACT": {
            "path": "governance/DOES_NOT_EXIST.md",
            "classification": "CANONICAL",
            "layer": "M0_CONSTITUTIONAL_SOURCE",
            "scopes": ["CONSTITUTIONAL_INVARIANTS"],
        }
    }
    capture = _activate(
        tmp_path,
        routing_record,
        artifact_query="MISSING_ARTIFACT",
        artifact_catalog=catalog,
    )

    assert capture["constitutional_memory_consultation_record"]["consultation_status"] == FAILED_CLOSED
    assert "citation bundle missing" in capture["constitutional_memory_consultation_record"]["failure_reason"]


def test_replay_reconstruction_detects_record_corruption(tmp_path) -> None:
    routing_record = _routing_record(tmp_path)
    _activate(tmp_path, routing_record)
    path = tmp_path / "consultation" / "000_constitutional_memory_consultation_record.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["retrieval_scope"] = "AUTHORITY_INVARIANTS"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_constitutional_memory_consultation_replay(tmp_path / "consultation")


def test_replay_reconstruction_detects_replay_corruption(tmp_path) -> None:
    routing_record = _routing_record(tmp_path)
    _activate(tmp_path, routing_record)
    path = tmp_path / "consultation" / "001_constitutional_memory_consultation_replay.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["routing_reference"] = "OTHER"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_constitutional_memory_consultation_replay(tmp_path / "consultation")


def test_replay_reconstruction_detects_ordering_corruption(tmp_path) -> None:
    routing_record = _routing_record(tmp_path)
    _activate(tmp_path, routing_record)
    path = tmp_path / "consultation" / "001_constitutional_memory_consultation_replay.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["replay_step"] = "constitutional_memory_consultation_record"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_constitutional_memory_consultation_replay(tmp_path / "consultation")


def test_only_memory_consultation_destination_can_activate(tmp_path) -> None:
    routing_record = _routing_record(tmp_path)
    assert routing_record["destination"] == CONSTITUTIONAL_MEMORY_CONSULTATION

    routing_record["destination"] = "PROVIDER_PROPOSAL"
    _rehash_artifact(routing_record)
    capture = _activate(tmp_path, routing_record)

    assert capture["constitutional_memory_consultation_record"]["consultation_status"] == FAILED_CLOSED
    assert "non-memory destination" in capture["constitutional_memory_consultation_record"]["failure_reason"]


def test_no_expanded_runtime_surface_imports() -> None:
    import aigol.runtime.constitutional_memory_consultation_activation as activation

    source = inspect.getsource(activation)

    assert "subprocess" not in source
    assert "os.system" not in source
    assert "requests" not in source
    assert "urllib" not in source
    assert "socket" not in source
    assert "async " not in source
    assert "await " not in source
    assert "threading" not in source
    assert "multiprocessing" not in source
