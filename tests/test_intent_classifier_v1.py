"""Tests for INTENT_CLASSIFIER_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.intent_classifier import (
    CLASSIFIED,
    CLASSIFIER_VERSION,
    CONSTITUTIONAL_MEMORY_CONSULTATION,
    CONVERSATION,
    EXECUTION_REQUEST,
    FAILED_CLOSED,
    PROVIDER_PROPOSAL,
    classify_intent,
    reconstruct_intent_classification_replay,
)
from aigol.runtime.models import FailClosedRuntimeError


CREATED_AT = "2026-05-30T02:00:00+00:00"


def _classify(tmp_path, prompt: str, **overrides) -> dict:
    args = {
        "artifact_id": "INTENT-CLASSIFICATION-000001",
        "human_request_reference": "HUMAN-REQUEST-000001",
        "human_prompt": prompt,
        "classification_timestamp": CREATED_AT,
        "replay_reference": "REPLAY-000001",
        "replay_dir": tmp_path,
    }
    args.update(overrides)
    return classify_intent(**args)


@pytest.mark.parametrize(
    ("prompt", "destination"),
    [
        ("Explain how AiGOL preserves replay.", CONVERSATION),
        ("Retrieve Constitutional Memory citation for the freeze manifest.", CONSTITUTIONAL_MEMORY_CONSULTATION),
        ("Ask OpenAI for an LLM proposal.", PROVIDER_PROPOSAL),
        ("Inspect runtime status.", EXECUTION_REQUEST),
    ],
)
def test_classifies_supported_destinations(tmp_path, prompt: str, destination: str) -> None:
    capture = _classify(tmp_path, prompt)
    artifact = capture["intent_classification_artifact"]
    replay = capture["intent_classification_replay"]
    reconstructed = reconstruct_intent_classification_replay(tmp_path)

    assert artifact["artifact_type"] == "INTENT_CLASSIFICATION_ARTIFACT"
    assert artifact["classification_destination"] == destination
    assert artifact["classification_status"] == CLASSIFIED
    assert artifact["ambiguity_status"] == "UNAMBIGUOUS"
    assert artifact["classifier_version"] == CLASSIFIER_VERSION
    assert artifact["human_request_reference"] == "HUMAN-REQUEST-000001"
    assert artifact["classification_timestamp"] == CREATED_AT
    assert artifact["replay_reference"] == "REPLAY-000001"
    assert replay["destination"] == destination
    assert replay["classification_status"] == CLASSIFIED
    assert reconstructed["classification_destination"] == destination
    assert reconstructed["replay_visible"] is True
    assert reconstructed["non_authoritative"] is True


def test_artifact_contains_no_authority_or_execution_fields(tmp_path) -> None:
    capture = _classify(tmp_path, "Explain AiGOL architecture.")
    artifact = capture["intent_classification_artifact"]

    forbidden = {
        "authorization_decision",
        "governance_decision",
        "execution_request",
        "provider_command",
        "worker_command",
        "memory_retrieval_result",
        "proposal_artifact",
        "correction_instruction",
    }
    assert forbidden.isdisjoint(artifact)


def test_replay_contains_required_visibility_evidence(tmp_path) -> None:
    capture = _classify(tmp_path, "Ask provider for a proposal.")
    replay = capture["intent_classification_replay"]

    assert replay["human_request_reference"] == "HUMAN-REQUEST-000001"
    assert replay["destination"] == PROVIDER_PROPOSAL
    assert replay["artifact_reference"] == "INTENT-CLASSIFICATION-000001"
    assert replay["classifier_version"] == CLASSIFIER_VERSION
    assert replay["classification_status"] == CLASSIFIED
    assert replay["replay_visibility"] == "MANDATORY"


def test_ambiguous_prompt_fails_closed(tmp_path) -> None:
    capture = _classify(tmp_path, "Explain runtime status.")
    artifact = capture["intent_classification_artifact"]
    reconstructed = reconstruct_intent_classification_replay(tmp_path)

    assert artifact["classification_status"] == FAILED_CLOSED
    assert artifact["classification_destination"] is None
    assert "ambiguous intent" in artifact["failure_reason"]
    assert reconstructed["classification_status"] == FAILED_CLOSED


def test_unknown_prompt_fails_closed(tmp_path) -> None:
    capture = _classify(tmp_path, "Make it nice.")
    artifact = capture["intent_classification_artifact"]

    assert artifact["classification_status"] == FAILED_CLOSED
    assert artifact["classification_destination"] is None
    assert "unknown intent" in artifact["failure_reason"]


def test_missing_prompt_fails_closed(tmp_path) -> None:
    capture = _classify(tmp_path, " ")
    artifact = capture["intent_classification_artifact"]

    assert artifact["classification_status"] == FAILED_CLOSED
    assert artifact["classification_destination"] is None
    assert "human_prompt is required" in artifact["failure_reason"]


def test_missing_destination_internal_validation_fails_closed() -> None:
    import aigol.runtime.intent_classifier as classifier

    artifact = {
        "artifact_id": "BAD",
        "artifact_type": "INTENT_CLASSIFICATION_ARTIFACT",
        "human_request_reference": "HUMAN",
        "human_prompt_hash": "sha256:test",
        "normalized_request_reference": None,
        "classification_destination": None,
        "classification_reason": "bad",
        "classifier_version": CLASSIFIER_VERSION,
        "classification_timestamp": CREATED_AT,
        "replay_reference": "REPLAY",
        "ambiguity_status": "UNAMBIGUOUS",
        "classification_status": CLASSIFIED,
        "failure_reason": None,
    }

    with pytest.raises(FailClosedRuntimeError, match="invalid destination"):
        classifier._validate_classification_artifact(artifact)


def test_invalid_destination_internal_validation_fails_closed() -> None:
    import aigol.runtime.intent_classifier as classifier

    artifact = {
        "artifact_id": "BAD",
        "artifact_type": "INTENT_CLASSIFICATION_ARTIFACT",
        "human_request_reference": "HUMAN",
        "human_prompt_hash": "sha256:test",
        "normalized_request_reference": None,
        "classification_destination": "ROUTE_TO_PROVIDER_NOW",
        "classification_reason": "bad",
        "classifier_version": CLASSIFIER_VERSION,
        "classification_timestamp": CREATED_AT,
        "replay_reference": "REPLAY",
        "ambiguity_status": "UNAMBIGUOUS",
        "classification_status": CLASSIFIED,
        "failure_reason": None,
    }

    with pytest.raises(FailClosedRuntimeError, match="invalid destination"):
        classifier._validate_classification_artifact(artifact)


def test_append_only_replay_behavior_fails_closed(tmp_path) -> None:
    first = _classify(tmp_path, "Explain AiGOL architecture.")
    second = _classify(tmp_path, "Inspect runtime status.")
    reconstructed = reconstruct_intent_classification_replay(tmp_path)

    assert first["intent_classification_artifact"]["classification_status"] == CLASSIFIED
    assert second["intent_classification_artifact"]["classification_status"] == FAILED_CLOSED
    assert "already exists" in second["intent_classification_artifact"]["failure_reason"]
    assert reconstructed["classification_destination"] == CONVERSATION


def test_replay_reconstruction_detects_artifact_corruption(tmp_path) -> None:
    _classify(tmp_path, "Inspect runtime status.")
    path = tmp_path / "000_intent_classification_artifact.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["classification_destination"] = CONVERSATION
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_intent_classification_replay(tmp_path)


def test_replay_reconstruction_detects_replay_corruption(tmp_path) -> None:
    _classify(tmp_path, "Inspect runtime status.")
    path = tmp_path / "001_intent_classification_replay.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["artifact_reference"] = "OTHER"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_intent_classification_replay(tmp_path)


def test_replay_reconstruction_detects_ordering_corruption(tmp_path) -> None:
    _classify(tmp_path, "Inspect runtime status.")
    path = tmp_path / "001_intent_classification_replay.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["replay_step"] = "intent_classification_artifact"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_intent_classification_replay(tmp_path)


def test_no_expanded_runtime_surface_imports() -> None:
    import aigol.runtime.intent_classifier as classifier

    source = inspect.getsource(classifier)

    assert "subprocess" not in source
    assert "os.system" not in source
    assert "requests" not in source
    assert "urllib" not in source
    assert "socket" not in source
    assert "async " not in source
    assert "await " not in source
    assert "threading" not in source
    assert "multiprocessing" not in source

