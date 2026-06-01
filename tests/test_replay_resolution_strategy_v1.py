"""Tests for REPLAY_RESOLUTION_STRATEGY_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.proposal_runtime import create_proposal
from aigol.runtime.replay_resolution_strategy import (
    REPLAY_RESOLUTION_ARTIFACT_V1,
    REPLAY_RESOLUTION_CREATED,
    REPLAY_RESOLUTION_RETURNED,
    is_replay_oriented_prompt,
    reconstruct_replay_resolution,
    resolve_replay_question,
)
from aigol.runtime.resolution_strategy_runtime import REPLAY
from aigol.runtime.transport.serialization import replay_hash, write_json_immutable


CREATED_AT = "2026-06-01T03:00:00+00:00"


def _proposal_replay(tmp_path) -> None:
    create_proposal(
        proposal_id="PROPOSAL-REPLAY-000001",
        proposal_type="CAPABILITY_PROPOSAL",
        proposal_source="CONVERSATION",
        proposal_text="Create replay-visible proposal evidence.",
        created_at=CREATED_AT,
        replay_reference="REPLAY-SOURCE-000001",
        replay_dir=tmp_path / "source" / "proposal",
    )


def _approval_like_replay(tmp_path) -> None:
    artifact = {
        "artifact_type": "PROPOSAL_APPROVAL_ARTIFACT_V1",
        "approval_id": "APPROVAL-REPLAY-000001",
        "proposal_id": "PROPOSAL-REPLAY-000001",
        "approval_status": "APPROVED",
        "created_at": "2026-06-01T03:01:00+00:00",
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    wrapper = {
        "replay_index": 0,
        "replay_step": "approval",
        "event_type": "PROPOSAL_APPROVED",
        "artifact": artifact,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(tmp_path / "source" / "approval" / "000_approval.json", wrapper)


def _resolve(tmp_path, prompt: str = "What happened recently?") -> dict:
    _proposal_replay(tmp_path)
    return resolve_replay_question(
        resolution_id="REPLAY-RESOLUTION-000001",
        strategy_id="STRATEGY-REPLAY-000001",
        human_prompt_reference="HUMAN-PROMPT-REPLAY-000001",
        human_prompt=prompt,
        replay_source_dir=tmp_path / "source",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "resolution",
    )


@pytest.mark.parametrize(
    "prompt",
    [
        "What happened recently?",
        "What changed?",
        "Show latest proposal.",
        "Show latest approval.",
        "What was the last operation?",
        "Summarize recent activity.",
    ],
)
def test_detects_replay_oriented_questions(prompt: str) -> None:
    assert is_replay_oriented_prompt(prompt) is True


def test_resolves_replay_question_from_replay_evidence(tmp_path) -> None:
    capture = _resolve(tmp_path)
    strategy = capture["resolution_strategy_artifact"]
    resolution = capture["replay_resolution_artifact"]
    returned = capture["replay_resolution_replay"]
    reconstructed = reconstruct_replay_resolution(tmp_path / "resolution")

    assert strategy["selected_strategy"] == REPLAY
    assert strategy["replay_required"] is True
    assert resolution["artifact_type"] == REPLAY_RESOLUTION_ARTIFACT_V1
    assert resolution["selected_strategy"] == REPLAY
    assert resolution["provider_used"] is False
    assert resolution["worker_invoked"] is False
    assert resolution["execution_requested"] is False
    assert "Replay evidence contains" in resolution["answer_text"]
    assert returned["event_type"] == REPLAY_RESOLUTION_RETURNED
    assert reconstructed["selected_strategy"] == REPLAY
    assert reconstructed["evidence_count"] >= 1


def test_latest_approval_is_selected_by_replay_evidence(tmp_path) -> None:
    _proposal_replay(tmp_path)
    _approval_like_replay(tmp_path)
    capture = resolve_replay_question(
        resolution_id="REPLAY-RESOLUTION-000001",
        strategy_id="STRATEGY-REPLAY-000001",
        human_prompt_reference="HUMAN-PROMPT-REPLAY-000001",
        human_prompt="Show latest approval.",
        replay_source_dir=tmp_path / "source",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "resolution",
    )

    assert capture["replay_resolution_artifact"]["latest_event"]["event_type"] == "PROPOSAL_APPROVED"


def test_replay_resolution_persists_events(tmp_path) -> None:
    _resolve(tmp_path)

    created = tmp_path / "resolution" / "000_replay_resolution_created.json"
    returned = tmp_path / "resolution" / "001_replay_resolution_returned.json"
    assert created.exists()
    assert returned.exists()
    assert json.loads(created.read_text(encoding="utf-8"))["event_type"] == REPLAY_RESOLUTION_CREATED
    assert json.loads(returned.read_text(encoding="utf-8"))["event_type"] == REPLAY_RESOLUTION_RETURNED


def test_non_replay_prompt_fails_closed(tmp_path) -> None:
    _proposal_replay(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="not replay-oriented"):
        resolve_replay_question(
            resolution_id="REPLAY-RESOLUTION-000001",
            strategy_id="STRATEGY-REPLAY-000001",
            human_prompt_reference="HUMAN-PROMPT-REPLAY-000001",
            human_prompt="Explain governance.",
            replay_source_dir=tmp_path / "source",
            created_at=CREATED_AT,
            replay_dir=tmp_path / "resolution",
        )


def test_replay_unavailable_fails_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="replay unavailable"):
        resolve_replay_question(
            resolution_id="REPLAY-RESOLUTION-000001",
            strategy_id="STRATEGY-REPLAY-000001",
            human_prompt_reference="HUMAN-PROMPT-REPLAY-000001",
            human_prompt="What happened recently?",
            replay_source_dir=tmp_path / "missing",
            created_at=CREATED_AT,
            replay_dir=tmp_path / "resolution",
        )


def test_replay_corrupt_fails_closed(tmp_path) -> None:
    path = tmp_path / "source" / "bad.json"
    path.parent.mkdir(parents=True)
    path.write_text("{not-json", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="replay corrupt"):
        resolve_replay_question(
            resolution_id="REPLAY-RESOLUTION-000001",
            strategy_id="STRATEGY-REPLAY-000001",
            human_prompt_reference="HUMAN-PROMPT-REPLAY-000001",
            human_prompt="What happened recently?",
            replay_source_dir=tmp_path / "source",
            created_at=CREATED_AT,
            replay_dir=tmp_path / "resolution",
        )


def test_replay_reference_corruption_fails_closed(tmp_path) -> None:
    _resolve(tmp_path)
    path = tmp_path / "resolution" / "001_replay_resolution_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["resolution_reference"] = "OTHER"
    wrapper["artifact"].pop("artifact_hash")
    wrapper["artifact"]["artifact_hash"] = replay_hash(wrapper["artifact"])
    wrapper.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="reference mismatch"):
        reconstruct_replay_resolution(tmp_path / "resolution")


def test_no_expanded_runtime_surface_imports() -> None:
    import aigol.runtime.replay_resolution_strategy as replay_resolution_strategy

    source = inspect.getsource(replay_resolution_strategy)

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
