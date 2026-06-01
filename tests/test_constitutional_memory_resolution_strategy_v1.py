"""Tests for CONSTITUTIONAL_MEMORY_RESOLUTION_STRATEGY_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.constitutional_memory_resolution_strategy import (
    CONSTITUTIONAL_MEMORY_RESOLUTION_ARTIFACT_V1,
    CONSTITUTIONAL_MEMORY_RESOLUTION_CREATED,
    CONSTITUTIONAL_MEMORY_RESOLUTION_RETURNED,
    is_constitutional_memory_prompt,
    reconstruct_constitutional_memory_resolution,
    resolve_constitutional_memory_question,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.resolution_strategy_runtime import CONSTITUTIONAL_MEMORY
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-06-01T05:00:00+00:00"


def _resolve(tmp_path, **overrides) -> dict:
    args = {
        "resolution_id": "CONSTITUTIONAL-MEMORY-RESOLUTION-000001",
        "strategy_id": "STRATEGY-CONSTITUTIONAL-MEMORY-000001",
        "retrieval_id": "CONSTITUTIONAL-MEMORY-RETRIEVAL-000001",
        "human_prompt_reference": "HUMAN-PROMPT-000001",
        "human_prompt": "What is AiGOL?",
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / "constitutional_memory_resolution",
    }
    args.update(overrides)
    return resolve_constitutional_memory_question(**args)


@pytest.mark.parametrize(
    "prompt",
    [
        "What is AiGOL?",
        "What is replay?",
        "What are provider boundaries?",
        "What are worker boundaries?",
        "What is proposal approval?",
        "What is the purpose of governance?",
        "What are constitutional guarantees?",
    ],
)
def test_detects_constitutional_memory_questions(prompt: str) -> None:
    assert is_constitutional_memory_prompt(prompt) is True


def test_constitutional_memory_resolution_records_citation_bound_answer(tmp_path) -> None:
    capture = _resolve(tmp_path)
    artifact = capture["constitutional_memory_resolution_artifact"]
    reconstructed = reconstruct_constitutional_memory_resolution(tmp_path / "constitutional_memory_resolution")

    assert artifact["artifact_type"] == CONSTITUTIONAL_MEMORY_RESOLUTION_ARTIFACT_V1
    assert artifact["selected_strategy"] == CONSTITUTIONAL_MEMORY
    assert artifact["citation_count"] >= 1
    assert "Primary citation:" in artifact["answer_text"]
    assert artifact["provider_used"] is False
    assert artifact["worker_invoked"] is False
    assert artifact["execution_requested"] is False
    assert artifact["approval_created"] is False
    assert reconstructed["selected_strategy"] == CONSTITUTIONAL_MEMORY
    assert reconstructed["citation_count"] >= 1
    assert reconstructed["provider_used"] is False
    assert reconstructed["worker_invoked"] is False
    assert reconstructed["execution_requested"] is False


def test_constitutional_memory_resolution_persists_replay_events(tmp_path) -> None:
    _resolve(tmp_path, human_prompt="What are provider boundaries?")

    replay_dir = tmp_path / "constitutional_memory_resolution"
    created = replay_dir / "000_constitutional_memory_resolution_created.json"
    returned = replay_dir / "001_constitutional_memory_resolution_returned.json"
    strategy = replay_dir / "strategy_selection" / "000_resolution_strategy_selected.json"
    memory_request = replay_dir / "constitutional_memory_access" / "000_retrieval_request.json"

    assert created.exists()
    assert returned.exists()
    assert strategy.exists()
    assert memory_request.exists()
    assert json.loads(created.read_text(encoding="utf-8"))["event_type"] == CONSTITUTIONAL_MEMORY_RESOLUTION_CREATED
    assert json.loads(returned.read_text(encoding="utf-8"))["event_type"] == CONSTITUTIONAL_MEMORY_RESOLUTION_RETURNED


def test_resolution_fails_closed_when_prompt_is_not_constitutional(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="not constitutional-memory-oriented"):
        _resolve(tmp_path, human_prompt="Tell me a joke.")


def test_resolution_fails_closed_when_constitutional_evidence_missing(tmp_path) -> None:
    catalog_without_requested_memory = {
        "OTHER_MEMORY": {
            "path": "docs/governance/CONSTITUTIONAL_INVARIANTS.md",
            "classification": "CANONICAL",
            "layer": "M0_CONSTITUTIONAL_SOURCE",
            "scopes": ["CONSTITUTIONAL_INVARIANTS"],
        }
    }

    with pytest.raises(FailClosedRuntimeError, match="constitutional evidence missing"):
        _resolve(tmp_path, artifact_catalog=catalog_without_requested_memory)


def test_reconstruction_detects_corrupt_constitutional_memory_replay(tmp_path) -> None:
    _resolve(tmp_path)
    path = (
        tmp_path
        / "constitutional_memory_resolution"
        / "constitutional_memory_access"
        / "001_citation_bundle.json"
    )
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["citation_count"] = 0
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_constitutional_memory_resolution(tmp_path / "constitutional_memory_resolution")


def test_reconstruction_detects_invalid_resolution_reference(tmp_path) -> None:
    _resolve(tmp_path)
    path = tmp_path / "constitutional_memory_resolution" / "001_constitutional_memory_resolution_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["resolution_reference"] = "OTHER"
    wrapper["artifact"].pop("artifact_hash")
    wrapper["artifact"]["artifact_hash"] = replay_hash(wrapper["artifact"])
    wrapper.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="resolution reference mismatch"):
        reconstruct_constitutional_memory_resolution(tmp_path / "constitutional_memory_resolution")


def test_reconstruction_detects_invalid_citation_reference(tmp_path) -> None:
    _resolve(tmp_path)
    path = tmp_path / "constitutional_memory_resolution" / "000_constitutional_memory_resolution_created.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["citations"][0]["citation_reference"] = ""
    wrapper["artifact"].pop("artifact_hash")
    wrapper["artifact"]["artifact_hash"] = replay_hash(wrapper["artifact"])
    wrapper.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")
    returned_path = (
        tmp_path / "constitutional_memory_resolution" / "001_constitutional_memory_resolution_returned.json"
    )
    returned = json.loads(returned_path.read_text(encoding="utf-8"))
    returned["artifact"]["resolution_hash"] = wrapper["artifact"]["artifact_hash"]
    returned["artifact"].pop("artifact_hash")
    returned["artifact"]["artifact_hash"] = replay_hash(returned["artifact"])
    returned.pop("replay_hash")
    returned["replay_hash"] = replay_hash(returned)
    returned_path.write_text(json.dumps(returned, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="citation_reference is required"):
        reconstruct_constitutional_memory_resolution(tmp_path / "constitutional_memory_resolution")


def test_no_expanded_runtime_surface_imports() -> None:
    import aigol.runtime.constitutional_memory_resolution_strategy as constitutional_memory_resolution_strategy

    source = inspect.getsource(constitutional_memory_resolution_strategy)

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
