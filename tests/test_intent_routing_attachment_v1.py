"""Tests for INTENT_ROUTING_ATTACHMENT_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.intent_classifier import (
    CLASSIFIED,
    CONSTITUTIONAL_MEMORY_CONSULTATION,
    CONVERSATION,
    EXECUTION_REQUEST,
    PROVIDER_PROPOSAL,
    classify_intent,
)
from aigol.runtime.intent_routing_attachment import (
    FAILED_CLOSED,
    ROUTED,
    ROUTING_VERSION,
    attach_intent_routing,
    reconstruct_intent_routing_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


CLASSIFIED_AT = "2026-05-30T03:00:00+00:00"
ROUTED_AT = "2026-05-30T03:01:00+00:00"


def _classification_artifact(tmp_path, prompt: str, artifact_id: str = "INTENT-CLASSIFICATION-000001") -> dict:
    capture = classify_intent(
        artifact_id=artifact_id,
        human_request_reference="HUMAN-REQUEST-000001",
        human_prompt=prompt,
        classification_timestamp=CLASSIFIED_AT,
        replay_reference="CLASSIFICATION-REPLAY-000001",
        replay_dir=tmp_path / "classification",
    )
    return capture["intent_classification_artifact"]


def _attach(tmp_path, artifact: dict, **overrides) -> dict:
    args = {
        "routing_record_id": "INTENT-ROUTING-000001",
        "intent_classification_artifact": artifact,
        "routing_timestamp": ROUTED_AT,
        "replay_reference": "ROUTING-REPLAY-000001",
        "replay_dir": tmp_path / "routing",
    }
    args.update(overrides)
    return attach_intent_routing(**args)


def _rehash_artifact(artifact: dict) -> None:
    artifact.pop("artifact_hash", None)
    artifact["artifact_hash"] = replay_hash(artifact)


@pytest.mark.parametrize(
    ("prompt", "destination"),
    [
        ("Explain how AiGOL preserves replay.", CONVERSATION),
        ("Retrieve Constitutional Memory citation.", CONSTITUTIONAL_MEMORY_CONSULTATION),
        ("Ask provider for a proposal.", PROVIDER_PROPOSAL),
        ("Inspect runtime status.", EXECUTION_REQUEST),
    ],
)
def test_creates_routing_evidence_for_supported_destinations(tmp_path, prompt: str, destination: str) -> None:
    artifact = _classification_artifact(tmp_path, prompt)
    capture = _attach(tmp_path, artifact)
    record = capture["intent_routing_attachment_record"]
    replay = capture["intent_routing_attachment_replay"]
    reconstructed = reconstruct_intent_routing_replay(tmp_path / "routing")

    assert record["record_type"] == "INTENT_ROUTING_ATTACHMENT_RECORD"
    assert record["artifact_reference"] == artifact["artifact_id"]
    assert record["classification_artifact_hash"] == artifact["artifact_hash"]
    assert record["destination"] == destination
    assert record["routing_status"] == ROUTED
    assert record["routing_version"] == ROUTING_VERSION
    assert record["routing_timestamp"] == ROUTED_AT
    assert replay["destination"] == destination
    assert replay["destination_invoked"] is False
    assert reconstructed["destination"] == destination
    assert reconstructed["destination_invoked"] is False
    assert reconstructed["replay_visible"] is True


def test_routing_record_contains_no_activation_fields(tmp_path) -> None:
    artifact = _classification_artifact(tmp_path, "Inspect runtime status.")
    record = _attach(tmp_path, artifact)["intent_routing_attachment_record"]

    forbidden = {
        "authorization_decision",
        "governance_decision",
        "execution_request",
        "provider_command",
        "worker_command",
        "memory_retrieval_result",
        "conversation_response",
    }
    assert forbidden.isdisjoint(record)
    assert record["reconstruction_metadata"]["destination_invoked"] is False


def test_invalid_destination_rejected(tmp_path) -> None:
    artifact = _classification_artifact(tmp_path, "Inspect runtime status.")
    artifact["classification_destination"] = "CUSTOM_DESTINATION"
    _rehash_artifact(artifact)
    capture = _attach(tmp_path, artifact)

    assert capture["intent_routing_attachment_record"]["routing_status"] == FAILED_CLOSED
    assert "invalid destination" in capture["intent_routing_attachment_record"]["failure_reason"]


def test_missing_artifact_rejected(tmp_path) -> None:
    capture = _attach(tmp_path, None)

    assert capture["intent_routing_attachment_record"]["routing_status"] == FAILED_CLOSED
    assert "missing artifact" in capture["intent_routing_attachment_record"]["failure_reason"]


def test_corrupt_artifact_rejected(tmp_path) -> None:
    artifact = _classification_artifact(tmp_path, "Inspect runtime status.")
    artifact["classification_reason"] = "tampered"
    capture = _attach(tmp_path, artifact)

    assert capture["intent_routing_attachment_record"]["routing_status"] == FAILED_CLOSED
    assert "hash mismatch" in capture["intent_routing_attachment_record"]["failure_reason"]


def test_ambiguous_artifact_rejected(tmp_path) -> None:
    artifact = _classification_artifact(tmp_path, "Explain runtime status.")
    capture = _attach(tmp_path, artifact)

    assert artifact["classification_status"] == FAILED_CLOSED
    assert capture["intent_routing_attachment_record"]["routing_status"] == FAILED_CLOSED
    assert "ambiguous artifact" in capture["intent_routing_attachment_record"]["failure_reason"]


def test_multiple_destinations_rejected(tmp_path) -> None:
    artifact = _classification_artifact(tmp_path, "Inspect runtime status.")
    artifact["classification_destination"] = [CONVERSATION, EXECUTION_REQUEST]
    _rehash_artifact(artifact)
    capture = _attach(tmp_path, artifact)

    assert capture["intent_routing_attachment_record"]["routing_status"] == FAILED_CLOSED
    assert "multiple destinations" in capture["intent_routing_attachment_record"]["failure_reason"]


def test_authority_bearing_artifact_rejected(tmp_path) -> None:
    artifact = _classification_artifact(tmp_path, "Inspect runtime status.")
    artifact["execution_request"] = {"run": True}
    _rehash_artifact(artifact)
    capture = _attach(tmp_path, artifact)

    assert capture["intent_routing_attachment_record"]["routing_status"] == FAILED_CLOSED
    assert "authority-bearing artifact" in capture["intent_routing_attachment_record"]["failure_reason"]


def test_append_only_replay_violation_fails_closed(tmp_path) -> None:
    artifact = _classification_artifact(tmp_path, "Inspect runtime status.")
    first = _attach(tmp_path, artifact)
    second = _attach(tmp_path, artifact)
    reconstructed = reconstruct_intent_routing_replay(tmp_path / "routing")

    assert first["intent_routing_attachment_record"]["routing_status"] == ROUTED
    assert second["intent_routing_attachment_record"]["routing_status"] == FAILED_CLOSED
    assert "already exists" in second["intent_routing_attachment_record"]["failure_reason"]
    assert reconstructed["routing_status"] == ROUTED


def test_replay_reconstruction_detects_record_corruption(tmp_path) -> None:
    artifact = _classification_artifact(tmp_path, "Inspect runtime status.")
    _attach(tmp_path, artifact)
    path = tmp_path / "routing" / "000_intent_routing_attachment_record.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["destination"] = CONVERSATION
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_intent_routing_replay(tmp_path / "routing")


def test_replay_reconstruction_detects_replay_corruption(tmp_path) -> None:
    artifact = _classification_artifact(tmp_path, "Inspect runtime status.")
    _attach(tmp_path, artifact)
    path = tmp_path / "routing" / "001_intent_routing_attachment_replay.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["routing_record_reference"] = "OTHER"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_intent_routing_replay(tmp_path / "routing")


def test_replay_reconstruction_detects_ordering_corruption(tmp_path) -> None:
    artifact = _classification_artifact(tmp_path, "Inspect runtime status.")
    _attach(tmp_path, artifact)
    path = tmp_path / "routing" / "001_intent_routing_attachment_replay.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["replay_step"] = "intent_routing_attachment_record"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_intent_routing_replay(tmp_path / "routing")


def test_only_classified_artifacts_can_route(tmp_path) -> None:
    artifact = _classification_artifact(tmp_path, "Make it nice.")
    capture = _attach(tmp_path, artifact)

    assert artifact["classification_status"] != CLASSIFIED
    assert capture["intent_routing_attachment_record"]["routing_status"] == FAILED_CLOSED


def test_no_expanded_runtime_surface_imports() -> None:
    import aigol.runtime.intent_routing_attachment as attachment

    source = inspect.getsource(attachment)

    assert "subprocess" not in source
    assert "os.system" not in source
    assert "requests" not in source
    assert "urllib" not in source
    assert "socket" not in source
    assert "async " not in source
    assert "await " not in source
    assert "threading" not in source
    assert "multiprocessing" not in source
