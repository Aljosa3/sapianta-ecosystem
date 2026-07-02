"""Tests for G9-13 broader governed validation suites."""

from __future__ import annotations

import pytest

from aigol.runtime.governed_validation_suite_runtime import (
    FAILED_CLOSED,
    GOVERNED_VALIDATION_SUITE_COMPLETED,
    VALIDATION_SUITE_FAILED,
    VALIDATION_SUITE_PASSED,
    create_governed_validation_suite_approval,
    create_governed_validation_suite_candidate,
    execute_governed_validation_suite,
    reconstruct_governed_validation_suite_replay,
)


CREATED_AT = "2026-07-02T00:00:00Z"


def _commands(*command_ids: str) -> list[dict]:
    return [
        {
            "command_id": command_id,
            "validation_purpose": f"targeted validation command {index}",
        }
        for index, command_id in enumerate(command_ids)
    ]


def _candidate(*command_ids: str) -> dict:
    return create_governed_validation_suite_candidate(
        candidate_id="G9-13-SUITE-CANDIDATE-001",
        session_id="G9-13-SESSION-001",
        commands=_commands(*command_ids),
        created_by="OCS",
        created_at=CREATED_AT,
    )


def _approval(candidate: dict) -> dict:
    return create_governed_validation_suite_approval(
        approval_id="G9-13-SUITE-APPROVAL-001",
        candidate_artifact=candidate,
        confirmation_text=f"confirm validation suite {candidate['candidate_id']} {candidate['artifact_hash']}",
        approved_by="HUMAN_OPERATOR",
        approved_at=CREATED_AT,
    )


def test_validation_suite_composes_allowlisted_commands_with_replay(tmp_path) -> None:
    candidate = _candidate("PY_COMPILE_G8_VALIDATION_TARGETS", "PY_COMPILE_G8_VALIDATION_TARGETS")
    approval = _approval(candidate)

    capture = execute_governed_validation_suite(
        execution_id="G9-13-SUITE-EXECUTION-001",
        candidate_artifact=candidate,
        approval_artifact=approval,
        repository_root=".",
        executed_by="PLATFORM_CORE",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "replay",
    )
    reconstructed = reconstruct_governed_validation_suite_replay(tmp_path / "replay")

    assert capture["execution_status"] == GOVERNED_VALIDATION_SUITE_COMPLETED
    assert capture["validation_suite_status"] == VALIDATION_SUITE_PASSED
    assert capture["validation_suite_passed"] is True
    assert capture["worker_invoked_count"] == 2
    assert capture["git_performed"] is False
    assert capture["deployment_performed"] is False
    assert capture["provider_invoked"] is False
    assert capture["repository_mutation_performed"] is False
    assert capture["architectural_health_advisory_artifact"]["advisory_only"] is True
    assert reconstructed["validation_suite_status"] == VALIDATION_SUITE_PASSED
    assert reconstructed["replay_artifact_count"] == 8


def test_validation_suite_requires_hash_bound_human_approval(tmp_path) -> None:
    candidate = _candidate("PY_COMPILE_G8_VALIDATION_TARGETS", "PY_COMPILE_G8_VALIDATION_TARGETS")

    capture = execute_governed_validation_suite(
        execution_id="G9-13-SUITE-NO-APPROVAL",
        candidate_artifact=candidate,
        approval_artifact=None,
        repository_root=".",
        executed_by="PLATFORM_CORE",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "replay",
    )

    assert capture["execution_status"] == FAILED_CLOSED
    assert capture["worker_invoked"] is False
    assert "approval required" in capture["failure_reason"]


def test_validation_suite_stops_on_first_failed_command(tmp_path) -> None:
    candidate = _candidate(
        "PY_COMPILE_G8_VALIDATION_TARGETS",
        "PYTHON_VALIDATION_FAILS_FOR_TEST",
        "PY_COMPILE_G8_VALIDATION_TARGETS",
    )
    approval = _approval(candidate)

    capture = execute_governed_validation_suite(
        execution_id="G9-13-SUITE-FAILS",
        candidate_artifact=candidate,
        approval_artifact=approval,
        repository_root=".",
        executed_by="PLATFORM_CORE",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "replay",
    )

    summary = capture["suite_summary_artifact"]
    assert capture["execution_status"] == GOVERNED_VALIDATION_SUITE_COMPLETED
    assert capture["validation_suite_status"] == VALIDATION_SUITE_FAILED
    assert capture["validation_suite_passed"] is False
    assert capture["worker_invoked_count"] == 2
    assert summary["stopped_on_failure"] is True
    assert summary["executed_command_count"] == 2
    assert summary["failed_command_count"] == 1


def test_validation_suite_rejects_unallowlisted_command() -> None:
    with pytest.raises(Exception, match="command is not allowlisted"):
        _candidate("PY_COMPILE_G8_VALIDATION_TARGETS", "RAW_SHELL_COMMAND")


def test_validation_suite_rejects_unbound_confirmation() -> None:
    candidate = _candidate("PY_COMPILE_G8_VALIDATION_TARGETS", "PY_COMPILE_G8_VALIDATION_TARGETS")

    with pytest.raises(Exception, match="confirmation does not bind candidate hash"):
        create_governed_validation_suite_approval(
            approval_id="G9-13-SUITE-BAD-APPROVAL",
            candidate_artifact=candidate,
            confirmation_text="confirm validation suite please",
            approved_by="HUMAN_OPERATOR",
            approved_at=CREATED_AT,
        )
