"""Tests for CONSTITUTIONAL_RUNTIME_IDENTITY_CONTINUITY_V1."""

from __future__ import annotations

from copy import deepcopy
import json

import pytest

from aigol.runtime.constitutional_runtime_identity_continuity import (
    AUTHORITY_SCOPE,
    create_identity_violation_artifact,
    create_runtime_identity,
    persist_identity_violation,
    terminate_runtime_identity,
    validate_authority_identity_continuity,
    validate_identity_immutability,
    validate_replay_identity_integrity,
    validate_runtime_identity_transition,
    validate_session_not_resurrected,
)
from aigol.runtime.minimal_executable_real_llm_session import (
    BOUNDED_SEMANTIC_CONTRIBUTION,
    execute_minimal_real_llm_session,
    external_llm_contribution_hash,
)
from aigol.runtime.models import FailClosedRuntimeError


CREATED_AT = "2026-05-28T03:00:00+00:00"


def _identity(session_id: str) -> dict:
    return create_runtime_identity(
        session_id=session_id,
        replay_scope=f"replay:{session_id}",
        created_at=CREATED_AT,
    )


def _contribution(session_id: str) -> dict:
    contribution = {
        "contribution_id": f"{session_id}:CONTRIBUTION",
        "contribution_text": "Propose bounded metadata inspection for governance review.",
        "contribution_type": BOUNDED_SEMANTIC_CONTRIBUTION,
        "requested_capabilities": ["metadata_inspection_provider"],
        "proposed_contract_reference": f"contract:{session_id}",
        "created_at": CREATED_AT,
    }
    contribution["response_hash"] = external_llm_contribution_hash(contribution)
    return contribution


def _execute(replay_dir, session_id: str) -> dict:
    contribution = _contribution(session_id)

    def infer(_ingress: dict) -> dict:
        return deepcopy(contribution)

    return execute_minimal_real_llm_session(
        session_id=session_id,
        request_id=f"{session_id}:REQUEST",
        human_input="Produce one bounded identity-safe contribution.",
        contribution_callable=infer,
        created_at=CREATED_AT,
        replay_dir=replay_dir,
    )


def test_deterministic_identity_creation() -> None:
    first = _identity("IDENTITY-SESSION-000001")
    second = _identity("IDENTITY-SESSION-000001")

    assert first == second
    assert first["state"] == "OPEN"
    assert first["authority_scope"] == AUTHORITY_SCOPE
    assert first["governance_authority"] is False
    assert first["execution_authority"] is False


def test_identity_immutability_rejects_mutation() -> None:
    identity = _identity("IDENTITY-SESSION-000001")
    mutated = deepcopy(identity)
    mutated["session_id"] = "IDENTITY-SESSION-MUTATED"

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        validate_identity_immutability(mutated)


def test_explicit_identity_termination() -> None:
    identity = _identity("IDENTITY-SESSION-000001")
    terminated = terminate_runtime_identity(identity, terminated_at="2026-05-28T03:01:00+00:00")

    assert terminated["state"] == "TERMINATED"
    assert terminated["lineage_parent"] == identity["identity_hash"]
    assert terminated["governance_authority"] is False


def test_session_resurrection_is_prevented() -> None:
    identity = _identity("IDENTITY-SESSION-000001")
    terminated = terminate_runtime_identity(identity, terminated_at="2026-05-28T03:01:00+00:00")
    candidate = _identity("IDENTITY-SESSION-000001")

    with pytest.raises(FailClosedRuntimeError, match="cannot continue"):
        validate_session_not_resurrected(terminated, candidate)


def test_hidden_identity_carryover_fails_closed() -> None:
    previous = _identity("IDENTITY-SESSION-000001")
    next_identity = _identity("IDENTITY-SESSION-000002")
    next_identity["lineage_parent"] = previous["identity_hash"]
    next_identity["identity_hash"] = "sha256:stale"

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        validate_runtime_identity_transition(previous, next_identity)


def test_implicit_identity_reuse_fails_closed() -> None:
    previous = _identity("IDENTITY-SESSION-000001")
    next_identity = _identity("IDENTITY-SESSION-000001")

    with pytest.raises(FailClosedRuntimeError, match="reuses session_id"):
        validate_runtime_identity_transition(previous, next_identity)


def test_authority_identity_continuity_is_non_authoritative() -> None:
    identity = _identity("IDENTITY-SESSION-000001")
    authority = validate_authority_identity_continuity(identity)

    assert authority["authority_continuity_valid"] is True
    assert authority["authority_drift_detected"] is False
    assert authority["authority_escalation_detected"] is False


def test_authority_drift_fails_closed() -> None:
    identity = _identity("IDENTITY-SESSION-000001")
    identity["authority_scope"] = "GOVERNANCE_AUTHORITY"

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        validate_authority_identity_continuity(identity)


def test_replay_identity_integrity_validates_isolated_replays(tmp_path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    _execute(first, "IDENTITY-SESSION-000001")
    _execute(second, "IDENTITY-SESSION-000002")

    integrity = validate_replay_identity_integrity([first, second])

    assert integrity["replay_identity_integrity"] is True
    assert integrity["replay_identity_contamination_detected"] is False
    assert integrity["append_only_integrity_preserved"] is True


def test_replay_identity_overlap_fails_closed(tmp_path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    _execute(first, "IDENTITY-SESSION-000001")
    _execute(second, "IDENTITY-SESSION-000001")

    with pytest.raises(FailClosedRuntimeError, match="contamination"):
        validate_replay_identity_integrity([first, second])


def test_cross_session_replay_mutation_fails_closed(tmp_path) -> None:
    replay_dir = tmp_path / "session"
    _execute(replay_dir, "IDENTITY-SESSION-000001")
    artifact_path = replay_dir / "000_ingress.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    artifact["artifact"]["session_id"] = "IDENTITY-SESSION-CORRUPTED"
    artifact_path.write_text(json.dumps(artifact, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        validate_replay_identity_integrity([replay_dir])


def test_identity_violation_artifact_is_replay_visible(tmp_path) -> None:
    artifact = create_identity_violation_artifact(
        session_id="IDENTITY-SESSION-000001",
        violation_type="HIDDEN_IDENTITY_CARRYOVER",
        reason="runtime identity attempted hidden continuation",
    )
    persist_identity_violation(violation_dir=tmp_path, artifact=artifact)

    persisted = json.loads((tmp_path / "000_identity_violation.json").read_text(encoding="utf-8"))
    assert persisted["artifact_type"] == "IDENTITY_VIOLATION"
    assert persisted["failed_closed"] is True
    assert persisted["hidden_continuity_created"] is False
