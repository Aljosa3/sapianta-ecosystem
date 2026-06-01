"""Tests for RESOLUTION_STRATEGY_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.resolution_strategy_runtime import (
    PROVIDER,
    REPLAY,
    RESOLUTION_STRATEGY_RETURNED,
    RESOLUTION_STRATEGY_SELECTED,
    RESOLUTION_STRATEGY_SELECTION_ARTIFACT_V1,
    SELF_RESOLUTION,
    select_resolution_strategy,
    reconstruct_resolution_strategy_replay,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-06-01T02:00:00+00:00"


def _strategy(tmp_path, **overrides) -> dict:
    args = {
        "strategy_id": "STRATEGY-000001",
        "selected_strategy": SELF_RESOLUTION,
        "selection_reason": "Deterministic self-resolution is sufficient.",
        "human_prompt_reference": "HUMAN-PROMPT-000001",
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / "strategy",
    }
    args.update(overrides)
    return select_resolution_strategy(**args)


@pytest.mark.parametrize(
    ("selected_strategy", "provider_required"),
    [
        (SELF_RESOLUTION, False),
        (PROVIDER, True),
        (REPLAY, False),
    ],
)
def test_resolution_strategy_selection_records_supported_strategy(
    tmp_path, selected_strategy: str, provider_required: bool
) -> None:
    capture = _strategy(tmp_path, selected_strategy=selected_strategy)
    artifact = capture["resolution_strategy_artifact"]
    returned = capture["resolution_strategy_replay"]
    reconstructed = reconstruct_resolution_strategy_replay(tmp_path / "strategy")

    assert artifact["artifact_type"] == RESOLUTION_STRATEGY_SELECTION_ARTIFACT_V1
    assert artifact["strategy_id"] == "STRATEGY-000001"
    assert artifact["selected_strategy"] == selected_strategy
    assert artifact["provider_required"] is provider_required
    assert artifact["provider_used"] is False
    assert artifact["worker_required"] is False
    assert artifact["approval_created"] is False
    assert artifact["execution_requested"] is False
    assert artifact["authority"] is False
    assert returned["event_type"] == RESOLUTION_STRATEGY_RETURNED
    assert reconstructed["selected_strategy"] == selected_strategy
    assert reconstructed["provider_required"] is provider_required
    assert reconstructed["replay_required"] is (selected_strategy == REPLAY)


def test_resolution_strategy_persists_replay_events(tmp_path) -> None:
    _strategy(tmp_path)

    selected = tmp_path / "strategy" / "000_resolution_strategy_selected.json"
    returned = tmp_path / "strategy" / "001_resolution_strategy_returned.json"
    assert selected.exists()
    assert returned.exists()
    assert json.loads(selected.read_text(encoding="utf-8"))["event_type"] == RESOLUTION_STRATEGY_SELECTED
    assert json.loads(returned.read_text(encoding="utf-8"))["event_type"] == RESOLUTION_STRATEGY_RETURNED


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("strategy_id", "", "strategy_id is required"),
        ("selected_strategy", "", "selected_strategy is required"),
        ("selection_reason", "", "selection_reason is required"),
        ("human_prompt_reference", "", "human_prompt_reference is required"),
        ("created_at", "", "created_at is required"),
    ],
)
def test_missing_fields_fail_closed(tmp_path, field: str, value: str, message: str) -> None:
    with pytest.raises(FailClosedRuntimeError, match=message):
        _strategy(tmp_path, **{field: value})


def test_invalid_strategy_fails_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="invalid strategy"):
        _strategy(tmp_path, selected_strategy="WORKER")


def test_invalid_creator_fails_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="creator must be AIGOL"):
        _strategy(tmp_path, created_by="PROVIDER")


def test_duplicate_strategy_replay_fails_closed(tmp_path) -> None:
    _strategy(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="already exists"):
        _strategy(tmp_path)


def test_replay_reconstruction_detects_artifact_corruption(tmp_path) -> None:
    _strategy(tmp_path)
    path = tmp_path / "strategy" / "000_resolution_strategy_selected.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["selected_strategy"] = PROVIDER
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_resolution_strategy_replay(tmp_path / "strategy")


def test_replay_reconstruction_detects_ordering_corruption(tmp_path) -> None:
    _strategy(tmp_path)
    path = tmp_path / "strategy" / "001_resolution_strategy_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["replay_step"] = "resolution_strategy_selected"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_resolution_strategy_replay(tmp_path / "strategy")


def test_replay_reconstruction_detects_reference_mismatch(tmp_path) -> None:
    _strategy(tmp_path)
    path = tmp_path / "strategy" / "001_resolution_strategy_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["strategy_reference"] = "OTHER"
    wrapper["artifact"].pop("artifact_hash")
    wrapper["artifact"]["artifact_hash"] = replay_hash(wrapper["artifact"])
    wrapper.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="strategy reference mismatch"):
        reconstruct_resolution_strategy_replay(tmp_path / "strategy")


def test_no_expanded_runtime_surface_imports() -> None:
    import aigol.runtime.resolution_strategy_runtime as resolution_strategy_runtime

    source = inspect.getsource(resolution_strategy_runtime)

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
