"""Tests for SOURCE_OF_TRUTH_ROUTER_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.source_of_truth_router_runtime import (
    CONSTITUTIONAL_MEMORY,
    GOVERNANCE,
    PROVIDER,
    REPLAY,
    SELF_RESOLUTION,
    SOURCE_OF_TRUTH_ROUTER_RETURNED,
    SOURCE_OF_TRUTH_ROUTER_SELECTED,
    SOURCE_OF_TRUTH_ROUTER_SELECTION_ARTIFACT_V1,
    route_source_of_truth,
    reconstruct_source_of_truth_router_replay,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-06-01T08:00:00+00:00"


def _route(tmp_path, **overrides) -> dict:
    args = {
        "router_id": "SOURCE-ROUTER-000001",
        "human_prompt_reference": "HUMAN-PROMPT-000001",
        "human_prompt": "Hello",
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / "source_router",
    }
    args.update(overrides)
    return route_source_of_truth(**args)


@pytest.mark.parametrize(
    ("prompt", "expected_source"),
    [
        ("What happened recently?", REPLAY),
        ("Show latest proposal", REPLAY),
        ("What was certified recently?", GOVERNANCE),
        ("What governance exists?", GOVERNANCE),
        ("What is AiGOL?", CONSTITUTIONAL_MEMORY),
        ("Explain worker boundaries", CONSTITUTIONAL_MEMORY),
        ("Hello", SELF_RESOLUTION),
        ("Explain simply", SELF_RESOLUTION),
        ("Explain AI alignment", PROVIDER),
        ("Write a poem", PROVIDER),
    ],
)
def test_source_router_selects_supported_sources_by_prompt(tmp_path, prompt: str, expected_source: str) -> None:
    capture = _route(tmp_path, human_prompt=prompt)
    artifact = capture["source_of_truth_router_artifact"]
    reconstructed = reconstruct_source_of_truth_router_replay(tmp_path / "source_router")

    assert artifact["artifact_type"] == SOURCE_OF_TRUTH_ROUTER_SELECTION_ARTIFACT_V1
    assert artifact["router_id"] == "SOURCE-ROUTER-000001"
    assert artifact["selected_source"] == expected_source
    assert artifact["human_prompt_reference"] == "HUMAN-PROMPT-000001"
    assert artifact["provider_required"] is (expected_source == PROVIDER)
    assert artifact["provider_used"] is False
    assert artifact["worker_required"] is False
    assert artifact["execution_required"] is False
    assert artifact["proposal_lifecycle_required"] is False
    assert reconstructed["selected_source"] == expected_source
    assert reconstructed["replay_visible"] is True


def test_source_router_applies_priority_over_provider(tmp_path) -> None:
    capture = _route(tmp_path, human_prompt="What happened recently? Write a poem about it.")
    artifact = capture["source_of_truth_router_artifact"]

    assert artifact["selected_source"] == REPLAY
    assert artifact["candidate_sources"] == [REPLAY, PROVIDER]


def test_source_router_applies_governance_priority_over_provider(tmp_path) -> None:
    capture = _route(tmp_path, human_prompt="What governance exists? Draft a summary.")
    artifact = capture["source_of_truth_router_artifact"]

    assert artifact["selected_source"] == GOVERNANCE
    assert artifact["candidate_sources"] == [GOVERNANCE, PROVIDER]


def test_source_router_applies_constitutional_memory_priority_over_self_and_provider(tmp_path) -> None:
    capture = _route(tmp_path, human_prompt="What is AiGOL? Explain simply.")
    artifact = capture["source_of_truth_router_artifact"]

    assert artifact["selected_source"] == CONSTITUTIONAL_MEMORY
    assert artifact["candidate_sources"] == [CONSTITUTIONAL_MEMORY, SELF_RESOLUTION]


def test_source_router_persists_replay_events(tmp_path) -> None:
    _route(tmp_path, human_prompt="What governance exists?")

    selected = tmp_path / "source_router" / "000_source_of_truth_router_selected.json"
    returned = tmp_path / "source_router" / "001_source_of_truth_router_returned.json"
    assert selected.exists()
    assert returned.exists()
    assert json.loads(selected.read_text(encoding="utf-8"))["event_type"] == SOURCE_OF_TRUTH_ROUTER_SELECTED
    assert json.loads(returned.read_text(encoding="utf-8"))["event_type"] == SOURCE_OF_TRUTH_ROUTER_RETURNED


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("router_id", "", "router_id is required"),
        ("human_prompt_reference", "", "human_prompt_reference is required"),
        ("human_prompt", "", "human_prompt is required"),
        ("created_at", "", "created_at is required"),
    ],
)
def test_missing_fields_fail_closed(tmp_path, field: str, value: str, message: str) -> None:
    with pytest.raises(FailClosedRuntimeError, match=message):
        _route(tmp_path, **{field: value})


def test_missing_references_fail_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="missing references"):
        _route(tmp_path, human_prompt="What happened recently?", evidence_refs=[])


def test_duplicate_replay_fails_closed(tmp_path) -> None:
    _route(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="already exists"):
        _route(tmp_path)


def test_replay_reconstruction_detects_artifact_corruption(tmp_path) -> None:
    _route(tmp_path)
    path = tmp_path / "source_router" / "000_source_of_truth_router_selected.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["selected_source"] = PROVIDER
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_source_of_truth_router_replay(tmp_path / "source_router")


def test_replay_reconstruction_detects_ordering_corruption(tmp_path) -> None:
    _route(tmp_path)
    path = tmp_path / "source_router" / "001_source_of_truth_router_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["replay_step"] = "source_of_truth_router_selected"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_source_of_truth_router_replay(tmp_path / "source_router")


def test_replay_reconstruction_detects_reference_mismatch(tmp_path) -> None:
    _route(tmp_path)
    path = tmp_path / "source_router" / "001_source_of_truth_router_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["router_reference"] = "OTHER"
    wrapper["artifact"].pop("artifact_hash")
    wrapper["artifact"]["artifact_hash"] = replay_hash(wrapper["artifact"])
    wrapper.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="reference mismatch"):
        reconstruct_source_of_truth_router_replay(tmp_path / "source_router")


def test_replay_reconstruction_detects_invalid_source(tmp_path) -> None:
    _route(tmp_path)
    path = tmp_path / "source_router" / "000_source_of_truth_router_selected.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["selected_source"] = "WORKER"
    wrapper["artifact"]["candidate_sources"] = ["WORKER"]
    wrapper["artifact"].pop("artifact_hash")
    wrapper["artifact"]["artifact_hash"] = replay_hash(wrapper["artifact"])
    wrapper.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")
    returned_path = tmp_path / "source_router" / "001_source_of_truth_router_returned.json"
    returned = json.loads(returned_path.read_text(encoding="utf-8"))
    returned["artifact"]["router_hash"] = wrapper["artifact"]["artifact_hash"]
    returned["artifact"].pop("artifact_hash")
    returned["artifact"]["artifact_hash"] = replay_hash(returned["artifact"])
    returned.pop("replay_hash")
    returned["replay_hash"] = replay_hash(returned)
    returned_path.write_text(json.dumps(returned, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="invalid source"):
        reconstruct_source_of_truth_router_replay(tmp_path / "source_router")


def test_replay_reconstruction_detects_ambiguous_routing(tmp_path) -> None:
    _route(tmp_path)
    path = tmp_path / "source_router" / "000_source_of_truth_router_selected.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["candidate_sources"] = [SELF_RESOLUTION, SELF_RESOLUTION]
    wrapper["artifact"].pop("artifact_hash")
    wrapper["artifact"]["artifact_hash"] = replay_hash(wrapper["artifact"])
    wrapper.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")
    returned_path = tmp_path / "source_router" / "001_source_of_truth_router_returned.json"
    returned = json.loads(returned_path.read_text(encoding="utf-8"))
    returned["artifact"]["router_hash"] = wrapper["artifact"]["artifact_hash"]
    returned["artifact"].pop("artifact_hash")
    returned["artifact"]["artifact_hash"] = replay_hash(returned["artifact"])
    returned.pop("replay_hash")
    returned["replay_hash"] = replay_hash(returned)
    returned_path.write_text(json.dumps(returned, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ambiguous routing"):
        reconstruct_source_of_truth_router_replay(tmp_path / "source_router")


def test_no_expanded_runtime_surface_imports() -> None:
    import aigol.runtime.source_of_truth_router_runtime as source_of_truth_router_runtime

    source = inspect.getsource(source_of_truth_router_runtime)

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
