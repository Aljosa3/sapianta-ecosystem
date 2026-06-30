"""Tests for G4 governed development loop execution scaffold."""

from __future__ import annotations

import json

import pytest

from aigol.runtime.g4_governed_development_loop_execution_scaffold import (
    ADVISORY_ONLY_CHECKPOINT_PASSED,
    BLOCKED_PENDING_GOVERNANCE,
    G4_GOVERNED_DEVELOPMENT_LOOP_SCAFFOLD_VERSION,
    SCAFFOLD_RECORDED,
    reconstruct_g4_governed_development_loop_scaffold_replay,
    run_g4_governed_development_loop_scaffold,
)
from aigol.runtime.models import FailClosedRuntimeError


CREATED_AT = "2026-06-30T00:00:00Z"


def _run(tmp_path, *, operator_response: str = "confirm") -> dict:
    return run_g4_governed_development_loop_scaffold(
        scaffold_id="G4-02-SCAFFOLD-001",
        human_intent=(
            "Create governance artifact G4_02_LOOP_FIXTURE_V1 describing replay, "
            "approval, authorization, and mutation boundaries."
        ),
        operator_response=operator_response,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "g4_loop",
    )


def test_g4_scaffold_connects_platform_core_components_without_execution(tmp_path) -> None:
    capture = _run(tmp_path)
    summary = capture["summary_artifact"]

    assert capture["runtime_version"] == G4_GOVERNED_DEVELOPMENT_LOOP_SCAFFOLD_VERSION
    assert capture["scaffold_status"] == SCAFFOLD_RECORDED
    assert capture["integrated_components"] == ["ACLI", "UBTR", "CSA", "OCS", "GOVERNANCE", "UHCL", "REPLAY"]
    assert capture["governance_checkpoint_status"] == ADVISORY_ONLY_CHECKPOINT_PASSED
    assert capture["canonical_response_class"] == "CONFIRMATION"
    assert capture["execution_intent_status"] == BLOCKED_PENDING_GOVERNANCE
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_authorized"] is False
    assert capture["repository_mutated"] is False
    assert capture["deployment_performed"] is False
    assert summary["ubtr_translation_hash"].startswith("sha256:")
    assert summary["csa_structured_intent_hash"].startswith("sha256:")
    assert summary["ocs_proposal_hash"].startswith("sha256:")
    assert summary["uhcl_communication_hash"].startswith("sha256:")
    assert summary["human_response_hash"].startswith("sha256:")


def test_g4_scaffold_replay_reconstructs_full_advisory_loop(tmp_path) -> None:
    _run(tmp_path, operator_response="continue")

    replay = reconstruct_g4_governed_development_loop_scaffold_replay(tmp_path / "g4_loop")

    assert replay["scaffold_status"] == SCAFFOLD_RECORDED
    assert replay["replay_artifact_count"] == 10
    assert replay["sub_replay_artifact_count"] == 7
    assert replay["integrated_components"] == ["ACLI", "UBTR", "CSA", "OCS", "GOVERNANCE", "UHCL", "REPLAY"]
    assert replay["governance_checkpoint_status"] == ADVISORY_ONLY_CHECKPOINT_PASSED
    assert replay["canonical_response_class"] == "CONTINUATION"
    assert replay["execution_intent_status"] == BLOCKED_PENDING_GOVERNANCE
    assert replay["provider_invoked"] is False
    assert replay["worker_invoked"] is False
    assert replay["execution_authorized"] is False
    assert replay["repository_mutated"] is False


@pytest.mark.parametrize(
    ("operator_response", "expected_class"),
    [
        ("please clarify", "CLARIFICATION"),
        ("modify scope", "MODIFICATION"),
        ("reject", "REJECTION"),
    ],
)
def test_g4_scaffold_maps_human_responses_to_uhcl_classes(
    tmp_path,
    operator_response: str,
    expected_class: str,
) -> None:
    capture = run_g4_governed_development_loop_scaffold(
        scaffold_id=f"G4-02-SCAFFOLD-{expected_class}",
        human_intent="Create governance artifact G4_02_LOOP_RESPONSE_V1.",
        operator_response=operator_response,
        created_at=CREATED_AT,
        replay_dir=tmp_path / expected_class.lower(),
    )

    assert capture["canonical_response_class"] == expected_class
    assert capture["execution_intent_status"] == BLOCKED_PENDING_GOVERNANCE
    assert capture["repository_mutated"] is False


def test_g4_scaffold_rejects_unmapped_human_response(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="does not map"):
        _run(tmp_path, operator_response="sounds interesting")


def test_g4_scaffold_replay_tampering_fails_closed(tmp_path) -> None:
    _run(tmp_path)
    path = tmp_path / "g4_loop" / "009_g4_loop_scaffold_summary_recorded.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["artifact"]["repository_mutated"] = True
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="replay hash mismatch"):
        reconstruct_g4_governed_development_loop_scaffold_replay(tmp_path / "g4_loop")
