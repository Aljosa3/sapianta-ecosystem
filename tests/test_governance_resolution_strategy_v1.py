"""Tests for GOVERNANCE_RESOLUTION_STRATEGY_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.governance_resolution_strategy import (
    GOVERNANCE_RESOLUTION_ARTIFACT_V1,
    GOVERNANCE_RESOLUTION_CREATED,
    GOVERNANCE_RESOLUTION_RETURNED,
    is_governance_oriented_prompt,
    reconstruct_governance_resolution,
    resolve_governance_question,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.resolution_strategy_runtime import GOVERNANCE
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-06-01T06:00:00+00:00"


def _resolve(tmp_path, **overrides) -> dict:
    args = {
        "resolution_id": "GOVERNANCE-RESOLUTION-000001",
        "strategy_id": "STRATEGY-GOVERNANCE-000001",
        "human_prompt_reference": "HUMAN-PROMPT-000001",
        "human_prompt": "What governance exists?",
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / "governance_resolution",
    }
    args.update(overrides)
    return resolve_governance_question(**args)


@pytest.mark.parametrize(
    "prompt",
    [
        "What governance exists?",
        "What was certified?",
        "Which milestone was completed?",
        "What governance guarantees exist?",
        "What ADRs define this capability?",
        "What is the status of a governance milestone?",
    ],
)
def test_detects_governance_questions(prompt: str) -> None:
    assert is_governance_oriented_prompt(prompt) is True


def test_governance_resolution_records_governance_artifact_answer(tmp_path) -> None:
    capture = _resolve(tmp_path)
    artifact = capture["governance_resolution_artifact"]
    reconstructed = reconstruct_governance_resolution(tmp_path / "governance_resolution")

    assert artifact["artifact_type"] == GOVERNANCE_RESOLUTION_ARTIFACT_V1
    assert artifact["selected_strategy"] == GOVERNANCE
    assert artifact["evidence_count"] == 1
    assert "Primary governance artifact:" in artifact["answer_text"]
    assert artifact["provider_used"] is False
    assert artifact["worker_invoked"] is False
    assert artifact["execution_requested"] is False
    assert artifact["approval_created"] is False
    assert reconstructed["selected_strategy"] == GOVERNANCE
    assert reconstructed["evidence_count"] == 1
    assert reconstructed["provider_used"] is False
    assert reconstructed["worker_invoked"] is False
    assert reconstructed["execution_requested"] is False


def test_governance_resolution_persists_replay_events(tmp_path) -> None:
    _resolve(tmp_path, human_prompt="What ADRs define this capability?")

    replay_dir = tmp_path / "governance_resolution"
    created = replay_dir / "000_governance_resolution_created.json"
    returned = replay_dir / "001_governance_resolution_returned.json"
    strategy = replay_dir / "strategy_selection" / "000_resolution_strategy_selected.json"

    assert created.exists()
    assert returned.exists()
    assert strategy.exists()
    assert json.loads(created.read_text(encoding="utf-8"))["event_type"] == GOVERNANCE_RESOLUTION_CREATED
    assert json.loads(returned.read_text(encoding="utf-8"))["event_type"] == GOVERNANCE_RESOLUTION_RETURNED


@pytest.mark.parametrize(
    ("prompt", "expected_artifact"),
    [
        ("What was certified?", "CONVERSATIONAL_RUNTIME_CERTIFICATION"),
        ("Which milestone was completed?", "FIFTH_REAL_CONVERSATIONAL_USAGE_CERTIFICATION"),
        ("What governance guarantees exist?", "OPERATIONAL_EPOCH_GUARANTEES"),
        ("What ADRs define this capability?", "RESOLUTION_STRATEGY_ADR"),
        ("What is the status of a governance milestone?", "MILESTONE_CONTINUITY_MODEL"),
    ],
)
def test_governance_questions_map_to_governance_sources(
    tmp_path, prompt: str, expected_artifact: str
) -> None:
    capture = _resolve(tmp_path, human_prompt=prompt)
    artifact = capture["governance_resolution_artifact"]

    assert artifact["source_references"][0]["artifact_identity"] == expected_artifact


def test_resolution_fails_closed_when_prompt_is_not_governance_oriented(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="not governance-oriented"):
        _resolve(tmp_path, human_prompt="Tell me a story.")


def test_resolution_fails_closed_when_governance_evidence_is_missing(tmp_path) -> None:
    catalog_without_requested_artifact = {
        "OTHER_GOVERNANCE": {
            "path": "governance/RESOLUTION_STRATEGY_ADR_V1.md",
            "classification": "ADR",
            "question_scope": "CAPABILITY_ADRS",
        }
    }

    with pytest.raises(FailClosedRuntimeError, match="missing governance evidence"):
        _resolve(tmp_path, artifact_catalog=catalog_without_requested_artifact)


def test_resolution_fails_closed_when_governance_artifact_is_corrupt(tmp_path) -> None:
    repo = tmp_path / "repo"
    evidence_dir = repo / "governance"
    evidence_dir.mkdir(parents=True)
    corrupt = evidence_dir / "CORRUPT_CERTIFICATION.json"
    corrupt.write_text("{not-json", encoding="utf-8")
    catalog = {
        "CONVERSATIONAL_RUNTIME_CERTIFICATION": {
            "path": "governance/CORRUPT_CERTIFICATION.json",
            "classification": "CERTIFICATION",
            "question_scope": "CERTIFIED_STATUS",
        }
    }

    with pytest.raises(FailClosedRuntimeError, match="corrupt governance artifacts"):
        _resolve(tmp_path, human_prompt="What was certified?", repository_root=repo, artifact_catalog=catalog)


def test_reconstruction_detects_invalid_resolution_reference(tmp_path) -> None:
    _resolve(tmp_path)
    path = tmp_path / "governance_resolution" / "001_governance_resolution_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["resolution_reference"] = "OTHER"
    wrapper["artifact"].pop("artifact_hash")
    wrapper["artifact"]["artifact_hash"] = replay_hash(wrapper["artifact"])
    wrapper.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="resolution reference mismatch"):
        reconstruct_governance_resolution(tmp_path / "governance_resolution")


def test_reconstruction_detects_invalid_source_reference(tmp_path) -> None:
    _resolve(tmp_path)
    path = tmp_path / "governance_resolution" / "000_governance_resolution_created.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["source_references"][0]["source_reference"] = ""
    wrapper["artifact"].pop("artifact_hash")
    wrapper["artifact"]["artifact_hash"] = replay_hash(wrapper["artifact"])
    wrapper.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")
    returned_path = tmp_path / "governance_resolution" / "001_governance_resolution_returned.json"
    returned = json.loads(returned_path.read_text(encoding="utf-8"))
    returned["artifact"]["resolution_hash"] = wrapper["artifact"]["artifact_hash"]
    returned["artifact"].pop("artifact_hash")
    returned["artifact"]["artifact_hash"] = replay_hash(returned["artifact"])
    returned.pop("replay_hash")
    returned["replay_hash"] = replay_hash(returned)
    returned_path.write_text(json.dumps(returned, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="source_reference is required"):
        reconstruct_governance_resolution(tmp_path / "governance_resolution")


def test_reconstruction_detects_corrupt_governance_resolution_replay(tmp_path) -> None:
    _resolve(tmp_path)
    path = tmp_path / "governance_resolution" / "000_governance_resolution_created.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["evidence_count"] = 0
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_governance_resolution(tmp_path / "governance_resolution")


def test_no_expanded_runtime_surface_imports() -> None:
    import aigol.runtime.governance_resolution_strategy as governance_resolution_strategy

    source = inspect.getsource(governance_resolution_strategy)

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
