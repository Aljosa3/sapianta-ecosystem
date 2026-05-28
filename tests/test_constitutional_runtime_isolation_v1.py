"""Tests for CONSTITUTIONAL_RUNTIME_ISOLATION_V1."""

from __future__ import annotations

from copy import deepcopy
import json

import pytest

from aigol.runtime.constitutional_runtime_isolation import (
    block_constitutional_mutation,
    read_constitutional_substrate_references,
    validate_cross_session_isolation,
    validate_no_constitutional_drift,
    validate_replay_isolation,
    validate_runtime_sandbox_containment,
)
from aigol.runtime.minimal_executable_real_llm_session import (
    BOUNDED_SEMANTIC_CONTRIBUTION,
    execute_minimal_real_llm_session,
    external_llm_contribution_hash,
)
from aigol.runtime.models import FailClosedRuntimeError


CREATED_AT = "2026-05-28T02:00:00+00:00"


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
        human_input="Produce one bounded isolated contribution.",
        contribution_callable=infer,
        created_at=CREATED_AT,
        replay_dir=replay_dir,
    )


def test_constitutional_readonly_reference_is_deterministic(tmp_path) -> None:
    substrate = tmp_path / "CONSTITUTION.md"
    substrate.write_text("immutable governance boundary\n", encoding="utf-8")

    first = read_constitutional_substrate_references([substrate])
    second = read_constitutional_substrate_references([substrate])

    assert first == second
    assert first["runtime_may_write"] is False
    assert first["runtime_access"] == "READ_ONLY"
    assert first["artifact_hash"].startswith("sha256:")


def test_constitutional_mutation_blocking_records_violation(tmp_path) -> None:
    violation_dir = tmp_path / "violation"

    with pytest.raises(FailClosedRuntimeError, match="mutation attempt blocked"):
        block_constitutional_mutation(
            session_id="ISOLATION-SESSION-000001",
            attempted_target="governance/CONSTITUTIONAL_RUNTIME_ISOLATION_V1.md",
            attempted_action="write",
            violation_dir=violation_dir,
        )

    artifact = json.loads((violation_dir / "000_isolation_violation.json").read_text(encoding="utf-8"))
    assert artifact["artifact_type"] == "ISOLATION_VIOLATION"
    assert artifact["constitutional_substrate_mutated"] is False
    assert artifact["failed_closed"] is True


def test_runtime_sandbox_containment_validates_non_authority(tmp_path) -> None:
    capture = _execute(tmp_path, "ISOLATION-SESSION-000001")
    containment = validate_runtime_sandbox_containment(capture)

    assert containment["sandbox_contained"] is True
    assert containment["governance_authority_delegated"] is False
    assert containment["execution_authority_activated"] is False
    assert containment["hidden_state_persisted"] is False


def test_runtime_sandbox_rejects_authority_escape(tmp_path) -> None:
    capture = _execute(tmp_path, "ISOLATION-SESSION-000001")
    capture["egress"]["governance_authority_delegated"] = True

    with pytest.raises(FailClosedRuntimeError, match="authority escalation"):
        validate_runtime_sandbox_containment(capture)


def test_cross_session_state_leak_is_prevented(tmp_path) -> None:
    first = _execute(tmp_path / "first", "ISOLATION-SESSION-000001")
    second = _execute(tmp_path / "second", "ISOLATION-SESSION-000002")

    isolation = validate_cross_session_isolation([first, second])

    assert isolation["cross_session_isolated"] is True
    assert isolation["hidden_continuity_detected"] is False
    assert isolation["replay_contamination_detected"] is False


def test_cross_session_hidden_lineage_carryover_fails_closed(tmp_path) -> None:
    first = _execute(tmp_path / "first", "ISOLATION-SESSION-000001")
    second = _execute(tmp_path / "second", "ISOLATION-SESSION-000002")
    second["ingress"]["lineage_parent"] = first["egress"]["artifact_hash"]

    with pytest.raises(FailClosedRuntimeError, match="hidden lineage carryover"):
        validate_cross_session_isolation([first, second])


def test_replay_lineage_isolation_validates_distinct_chains(tmp_path) -> None:
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"
    _execute(first_dir, "ISOLATION-SESSION-000001")
    _execute(second_dir, "ISOLATION-SESSION-000002")

    isolation = validate_replay_isolation([first_dir, second_dir])

    assert isolation["isolated_replay_chains"] is True
    assert isolation["replay_contamination_detected"] is False
    assert len(isolation["lineages"]) == 2


def test_replay_contamination_duplicate_session_fails_closed(tmp_path) -> None:
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"
    _execute(first_dir, "ISOLATION-SESSION-000001")
    _execute(second_dir, "ISOLATION-SESSION-000001")

    with pytest.raises(FailClosedRuntimeError, match="duplicate session lineage"):
        validate_replay_isolation([first_dir, second_dir])


def test_replay_mutation_in_isolated_chain_fails_closed(tmp_path) -> None:
    replay_dir = tmp_path / "session"
    _execute(replay_dir, "ISOLATION-SESSION-000001")
    artifact_path = replay_dir / "004_egress.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    artifact["artifact"]["status"] = "MUTATED"
    artifact_path.write_text(json.dumps(artifact, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        validate_replay_isolation([replay_dir])


def test_constitutional_drift_detection(tmp_path) -> None:
    substrate = tmp_path / "CONSTITUTION.md"
    substrate.write_text("immutable governance boundary\n", encoding="utf-8")
    before = read_constitutional_substrate_references([substrate])
    after = read_constitutional_substrate_references([substrate])

    drift = validate_no_constitutional_drift(before, after)

    assert drift["constitutional_substrate_immutable"] is True
    assert drift["runtime_access"] == "READ_ONLY"


def test_constitutional_drift_fails_closed(tmp_path) -> None:
    substrate = tmp_path / "CONSTITUTION.md"
    substrate.write_text("immutable governance boundary\n", encoding="utf-8")
    before = read_constitutional_substrate_references([substrate])
    substrate.write_text("mutated governance boundary\n", encoding="utf-8")
    after = read_constitutional_substrate_references([substrate])

    with pytest.raises(FailClosedRuntimeError, match="drift"):
        validate_no_constitutional_drift(before, after)
