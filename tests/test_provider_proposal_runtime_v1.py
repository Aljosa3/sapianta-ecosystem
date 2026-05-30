"""Tests for PROVIDER_PROPOSAL_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.intent_classifier import classify_intent
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_proposal_runtime import (
    CREATED,
    FAILED_CLOSED,
    PROVIDER_PROPOSAL_ARTIFACT,
    RETURNED,
    create_provider_proposal,
    reconstruct_provider_proposal_replay,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-30T08:00:00+00:00"


def _proposal(tmp_path, **overrides) -> dict:
    args = {
        "proposal_id": "PROVIDER-PROPOSAL-000001",
        "prompt_id": "HUMAN-PROMPT-PROVIDER-000001",
        "human_prompt": "Ask provider for a proposal.",
        "provider_type": "external_llm",
        "reason": "Provider proposal requested by deterministic intent.",
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / "provider_proposal",
    }
    args.update(overrides)
    return create_provider_proposal(**args)


def _intent(tmp_path, prompt: str = "Ask provider for a proposal.") -> dict:
    return classify_intent(
        artifact_id="INTENT-PROVIDER-000001",
        human_request_reference="HUMAN-PROMPT-PROVIDER-000001",
        human_prompt=prompt,
        classification_timestamp=CREATED_AT,
        replay_reference="INTENT-PROVIDER-REPLAY-000001",
        replay_dir=tmp_path / "intent",
    )["intent_classification_artifact"]


def _rehash_artifact(artifact: dict) -> None:
    artifact.pop("artifact_hash", None)
    artifact["artifact_hash"] = replay_hash(artifact)


def test_provider_proposal_created_from_valid_prompt(tmp_path) -> None:
    capture = _proposal(tmp_path)
    proposal = capture["provider_proposal"]
    returned = capture["provider_proposal_replay"]
    reconstructed = reconstruct_provider_proposal_replay(tmp_path / "provider_proposal")

    assert proposal["artifact_type"] == PROVIDER_PROPOSAL_ARTIFACT
    assert proposal["proposal_id"] == "PROVIDER-PROPOSAL-000001"
    assert proposal["provider_type"] == "EXTERNAL_LLM"
    assert proposal["authority"] is False
    assert proposal["execution_capable"] is False
    assert proposal["provider_invoked"] is False
    assert proposal["worker_invoked"] is False
    assert proposal["proposal_status"] == CREATED
    assert returned["replay_event"] == RETURNED
    assert reconstructed["proposal_status"] == CREATED
    assert reconstructed["provider_invoked"] is False
    assert reconstructed["worker_invoked"] is False


def test_provider_proposal_accepts_preclassified_intent(tmp_path) -> None:
    intent = _intent(tmp_path)
    capture = _proposal(tmp_path, intent_classification_artifact=intent)

    assert capture["provider_proposal"]["intent_id"] == intent["artifact_id"]
    assert capture["provider_proposal_replay"]["intent_artifact_hash"] == intent["artifact_hash"]


def test_non_provider_intent_fails_closed(tmp_path) -> None:
    intent = _intent(tmp_path, prompt="Explain how AiGOL preserves replay.")
    capture = _proposal(tmp_path, intent_classification_artifact=intent)

    assert capture["provider_proposal"]["proposal_status"] == FAILED_CLOSED
    assert "not provider proposal" in capture["provider_proposal"]["failure_reason"]
    assert capture["provider_proposal"]["provider_invoked"] is False


def test_corrupt_intent_fails_closed(tmp_path) -> None:
    intent = _intent(tmp_path)
    intent["classification_reason"] = "tampered"
    capture = _proposal(tmp_path, intent_classification_artifact=intent)

    assert capture["provider_proposal"]["proposal_status"] == FAILED_CLOSED
    assert "hash mismatch" in capture["provider_proposal"]["failure_reason"]


def test_missing_reason_fails_closed(tmp_path) -> None:
    capture = _proposal(tmp_path, reason="")

    assert capture["provider_proposal"]["proposal_status"] == FAILED_CLOSED
    assert "reason is required" in capture["provider_proposal"]["failure_reason"]


def test_no_authority_or_execution_fields_introduced(tmp_path) -> None:
    proposal = _proposal(tmp_path)["provider_proposal"]
    forbidden = {
        "authorization_decision",
        "governance_decision",
        "execution_request",
        "provider_request",
        "worker_request",
        "worker_instruction",
        "provider_command",
        "worker_command",
    }

    assert forbidden.isdisjoint(proposal)
    assert proposal["authority"] is False
    assert proposal["execution_capable"] is False


def test_replay_artifacts_are_created(tmp_path) -> None:
    _proposal(tmp_path)

    created = tmp_path / "provider_proposal" / "000_provider_proposal_created.json"
    returned = tmp_path / "provider_proposal" / "001_provider_proposal_returned.json"
    assert created.exists()
    assert returned.exists()
    assert json.loads(created.read_text(encoding="utf-8"))["event_type"] == CREATED
    assert json.loads(returned.read_text(encoding="utf-8"))["event_type"] == RETURNED


def test_append_only_replay_violation_fails_closed(tmp_path) -> None:
    first = _proposal(tmp_path)
    second = _proposal(tmp_path)
    reconstructed = reconstruct_provider_proposal_replay(tmp_path / "provider_proposal")

    assert first["provider_proposal"]["proposal_status"] == CREATED
    assert second["provider_proposal"]["proposal_status"] == FAILED_CLOSED
    assert "already exists" in second["provider_proposal"]["failure_reason"]
    assert reconstructed["proposal_status"] == CREATED


def test_replay_reconstruction_detects_proposal_corruption(tmp_path) -> None:
    _proposal(tmp_path)
    path = tmp_path / "provider_proposal" / "000_provider_proposal_created.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["provider_invoked"] = True
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_provider_proposal_replay(tmp_path / "provider_proposal")


def test_replay_reconstruction_detects_ordering_corruption(tmp_path) -> None:
    _proposal(tmp_path)
    path = tmp_path / "provider_proposal" / "001_provider_proposal_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["replay_step"] = "provider_proposal_created"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_provider_proposal_replay(tmp_path / "provider_proposal")


def test_no_expanded_runtime_surface_imports() -> None:
    import aigol.runtime.provider_proposal_runtime as provider_proposal

    source = inspect.getsource(provider_proposal)

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
