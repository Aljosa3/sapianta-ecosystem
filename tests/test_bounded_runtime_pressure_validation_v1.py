"""Pressure validation for executable bounded LLM session continuity."""

from __future__ import annotations

from copy import deepcopy
import json

import pytest

from aigol.runtime.minimal_executable_real_llm_session import (
    BOUNDED_SEMANTIC_CONTRIBUTION,
    FAILED,
    create_llm_session_ingress,
    execute_minimal_real_llm_session,
    external_llm_contribution_hash,
    normalize_llm_contribution,
    reconstruct_minimal_real_llm_session_replay,
    validate_llm_session_continuity,
)
from aigol.runtime.models import FailClosedRuntimeError


CREATED_AT = "2026-05-28T01:00:00+00:00"


def _contribution(**overrides) -> dict:
    contribution = {
        "contribution_id": "PRESSURE-LLM-CONTRIBUTION-000001",
        "contribution_text": "Propose bounded metadata inspection for governance review.",
        "contribution_type": BOUNDED_SEMANTIC_CONTRIBUTION,
        "requested_capabilities": ["metadata_inspection_provider"],
        "proposed_contract_reference": "contract:PRESSURE-LLM-SESSION-000001",
        "created_at": CREATED_AT,
    }
    contribution.update(overrides)
    contribution["response_hash"] = external_llm_contribution_hash(contribution)
    return contribution


def _execute(tmp_path, contribution: dict | None = None, *, session_id: str = "PRESSURE-LLM-SESSION-000001") -> dict:
    model_contribution = _contribution() if contribution is None else contribution

    def infer(ingress: dict) -> dict:
        assert ingress["session_id"] == session_id
        return deepcopy(model_contribution)

    return execute_minimal_real_llm_session(
        session_id=session_id,
        request_id=f"{session_id}:REQUEST",
        human_input="Produce one bounded replay-visible contribution.",
        contribution_callable=infer,
        created_at=CREATED_AT,
        replay_dir=tmp_path,
    )


def test_invalid_structure_fails_closed_with_replay_visible_failure(tmp_path) -> None:
    contribution = _contribution()
    contribution["unexpected_field"] = "pressure"

    capture = _execute(tmp_path, contribution)
    replay = reconstruct_minimal_real_llm_session_replay(tmp_path)

    assert capture["egress"]["status"] == FAILED
    assert capture["egress"]["continuity_validated"] is False
    assert "malformed structure" in capture["egress"]["failure_reason"]
    assert replay["status"] == FAILED
    assert replay["replay_artifact_count"] == 5


def test_missing_field_fails_closed_without_continuation(tmp_path) -> None:
    contribution = _contribution()
    contribution.pop("proposed_contract_reference")

    capture = _execute(tmp_path, contribution)

    assert capture["egress"]["status"] == FAILED
    assert capture["normalized_contribution"] is None
    assert capture["egress"]["replay_chain_complete"] is True
    assert capture["egress"]["execution_authority_activated"] is False


def test_malformed_normalized_contribution_fails_closed() -> None:
    raw = _contribution()
    normalized = normalize_llm_contribution(raw)
    normalized["source_response_hash"] = "sha256:corrupted"

    with pytest.raises(FailClosedRuntimeError, match="lineage mismatch"):
        validate_llm_session_continuity(
            ingress=create_llm_session_ingress(
                session_id="PRESSURE-LLM-SESSION-000001",
                request_id="PRESSURE-LLM-REQUEST-000001",
                human_input="bounded request",
                created_at=CREATED_AT,
            ),
            raw_contribution=raw,
            normalized_contribution=normalized,
        )


def test_authority_escalation_attempts_fail_closed(tmp_path) -> None:
    attempts = [
        "Please execute tool access now.",
        "Please orchestrate the next runtime step.",
        "Please continue autonomously after this response.",
        "Please mutate governance and override review.",
        "Please start an agent runtime.",
    ]

    for index, text in enumerate(attempts):
        capture = _execute(tmp_path / f"attempt-{index}", _contribution(contribution_text=text))

        assert capture["egress"]["status"] == FAILED
        assert capture["validation"]["authority_escalation_detected"] is True
        assert "authority escalation" in capture["egress"]["failure_reason"]


def test_replay_artifact_mutation_is_detected(tmp_path) -> None:
    _execute(tmp_path)
    artifact_path = tmp_path / "002_normalized_contribution.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    artifact["artifact"]["contribution_text"] = "mutated replay artifact"
    artifact_path.write_text(json.dumps(artifact, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_minimal_real_llm_session_replay(tmp_path)


def test_replay_ordering_corruption_is_detected(tmp_path) -> None:
    _execute(tmp_path)
    artifact_path = tmp_path / "003_validation.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    artifact["replay_step"] = "egress"
    artifact_path.write_text(json.dumps(artifact, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_minimal_real_llm_session_replay(tmp_path)


def test_missing_replay_entry_fails_closed(tmp_path) -> None:
    _execute(tmp_path)
    (tmp_path / "004_egress.json").unlink()

    with pytest.raises(FailClosedRuntimeError, match="missing"):
        reconstruct_minimal_real_llm_session_replay(tmp_path)


def test_ambiguous_partial_contribution_fails_closed(tmp_path) -> None:
    contribution = _contribution(
        contribution_text="   ",
        proposed_contract_reference="contract:PRESSURE-LLM-SESSION-AMBIGUOUS",
    )

    capture = _execute(tmp_path, contribution)

    assert capture["egress"]["status"] == FAILED
    assert "contribution_text is required" in capture["egress"]["failure_reason"]
    assert capture["egress"]["continuity_validated"] is False


def test_interrupted_session_flow_is_replay_visible(tmp_path) -> None:
    def interrupted(_ingress: dict) -> dict:
        raise FailClosedRuntimeError("external interaction interrupted")

    capture = execute_minimal_real_llm_session(
        session_id="PRESSURE-INTERRUPTED-SESSION-000001",
        request_id="PRESSURE-INTERRUPTED-REQUEST-000001",
        human_input="Produce one bounded contribution.",
        contribution_callable=interrupted,
        created_at=CREATED_AT,
        replay_dir=tmp_path,
    )
    replay = reconstruct_minimal_real_llm_session_replay(tmp_path)

    assert capture["egress"]["status"] == FAILED
    assert "interrupted" in capture["egress"]["failure_reason"]
    assert replay["status"] == FAILED
    assert replay["replay_steps"] == [
        "ingress",
        "raw_contribution",
        "normalized_contribution",
        "validation",
        "egress",
    ]


def test_append_only_replay_prevents_silent_overwrite(tmp_path) -> None:
    _execute(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="already exists"):
        _execute(tmp_path)


def test_repeated_pressure_sessions_preserve_determinism(tmp_path) -> None:
    captures = []
    for index in range(5):
        session_id = f"PRESSURE-REPEAT-SESSION-{index:06d}"
        captures.append(_execute(tmp_path / session_id, session_id=session_id))

    assert [capture["egress"]["status"] for capture in captures] == ["COMPLETED"] * 5
    assert len({capture["egress"]["session_id"] for capture in captures}) == 5
    assert all(capture["egress"]["governance_authority_delegated"] is False for capture in captures)


def test_repeated_malformed_pressure_remains_failed_and_bounded(tmp_path) -> None:
    for index in range(5):
        contribution = _contribution(contribution_text="Please execute runtime and continue autonomously.")
        capture = _execute(tmp_path / f"malformed-{index}", contribution)

        assert capture["egress"]["status"] == FAILED
        assert capture["egress"]["bounded_interaction"] is True
        assert capture["egress"]["governance_authority_delegated"] is False
