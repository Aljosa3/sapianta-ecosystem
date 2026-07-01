"""Tests for G8-14 governed validation execution runtime."""

from __future__ import annotations

import inspect

import pytest

from aigol.runtime.governed_validation_runtime import (
    GOVERNED_VALIDATION_COMPLETED,
    FAILED_CLOSED,
    create_governed_validation_approval,
    create_governed_validation_candidate,
    execute_governed_validation,
    reconstruct_governed_validation_replay,
)
from aigol.workers.validation_command_worker import (
    VALIDATION_FAILED,
    VALIDATION_PASSED,
    VALIDATION_TIMED_OUT,
)


CREATED_AT = "2026-07-01T00:00:00Z"


def _candidate(command_id: str = "PY_COMPILE_G8_VALIDATION_TARGETS") -> dict:
    return create_governed_validation_candidate(
        candidate_id=f"G8-14-CANDIDATE-{command_id}",
        session_id="G8-14-SESSION-001",
        command_id=command_id,
        validation_purpose="targeted governed validation",
        created_by="OCS",
        created_at=CREATED_AT,
    )


def _approval(candidate: dict) -> dict:
    return create_governed_validation_approval(
        approval_id=f"{candidate['candidate_id']}:APPROVAL",
        candidate_artifact=candidate,
        confirmation_text=f"confirm validation {candidate['candidate_id']} {candidate['artifact_hash']}",
        approved_by="HUMAN_OPERATOR",
        approved_at=CREATED_AT,
    )


def test_governed_validation_executes_allowlisted_command_with_replay(tmp_path) -> None:
    candidate = _candidate()
    approval = _approval(candidate)

    capture = execute_governed_validation(
        execution_id="G8-14-EXECUTION-001",
        candidate_artifact=candidate,
        approval_artifact=approval,
        repository_root=".",
        executed_by="PLATFORM_CORE",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "replay",
    )
    reconstructed = reconstruct_governed_validation_replay(tmp_path / "replay")

    assert capture["execution_status"] == GOVERNED_VALIDATION_COMPLETED
    assert capture["validation_status"] == VALIDATION_PASSED
    assert capture["validation_passed"] is True
    assert capture["exit_code"] == 0
    assert capture["timed_out"] is False
    assert capture["worker_invoked"] is True
    assert capture["git_performed"] is False
    assert capture["commit_created"] is False
    assert capture["deployment_performed"] is False
    assert capture["provider_invoked"] is False
    assert reconstructed["validation_status"] == VALIDATION_PASSED
    assert reconstructed["replay_artifact_count"] == 8


def test_governed_validation_records_nonzero_exit_as_validation_failure(tmp_path) -> None:
    candidate = _candidate("PYTHON_VALIDATION_FAILS_FOR_TEST")
    approval = _approval(candidate)

    capture = execute_governed_validation(
        execution_id="G8-14-EXECUTION-FAILS",
        candidate_artifact=candidate,
        approval_artifact=approval,
        repository_root=".",
        executed_by="PLATFORM_CORE",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "replay",
    )

    assert capture["execution_status"] == GOVERNED_VALIDATION_COMPLETED
    assert capture["validation_status"] == VALIDATION_FAILED
    assert capture["validation_passed"] is False
    assert capture["exit_code"] == 2
    assert "validation failed" in capture["validation_result_artifact"]["stdout_excerpt"]


def test_governed_validation_records_timeout(tmp_path) -> None:
    candidate = _candidate("PYTHON_VALIDATION_TIMEOUT_FOR_TEST")
    approval = _approval(candidate)

    capture = execute_governed_validation(
        execution_id="G8-14-EXECUTION-TIMEOUT",
        candidate_artifact=candidate,
        approval_artifact=approval,
        repository_root=".",
        executed_by="PLATFORM_CORE",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "replay",
    )

    assert capture["execution_status"] == GOVERNED_VALIDATION_COMPLETED
    assert capture["validation_status"] == VALIDATION_TIMED_OUT
    assert capture["validation_passed"] is False
    assert capture["exit_code"] is None
    assert capture["timed_out"] is True


def test_governed_validation_requires_hash_bound_human_approval(tmp_path) -> None:
    candidate = _candidate()

    capture = execute_governed_validation(
        execution_id="G8-14-EXECUTION-NO-APPROVAL",
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


def test_governed_validation_rejects_unbound_confirmation() -> None:
    candidate = _candidate()

    with pytest.raises(Exception, match="confirmation does not bind candidate hash"):
        create_governed_validation_approval(
            approval_id="G8-14-APPROVAL-BAD",
            candidate_artifact=candidate,
            confirmation_text="confirm validation please",
            approved_by="HUMAN_OPERATOR",
            approved_at=CREATED_AT,
        )


def test_governed_validation_rejects_unallowlisted_command() -> None:
    with pytest.raises(Exception, match="command is not allowlisted"):
        create_governed_validation_candidate(
            candidate_id="G8-14-CANDIDATE-BAD",
            session_id="G8-14-SESSION-001",
            command_id="RAW_SHELL_COMMAND",
            validation_purpose="bad validation",
            created_by="OCS",
            created_at=CREATED_AT,
        )


def test_governed_validation_has_no_shell_git_provider_or_deployment_surface() -> None:
    import aigol.runtime.governed_validation_runtime as runtime
    import aigol.workers.validation_command_worker as worker

    source = inspect.getsource(runtime) + inspect.getsource(worker)
    filtered = source.replace('"git_allowed"', "")
    filtered = filtered.replace('"git_operation"', "")
    filtered = filtered.replace('"git_performed"', "")
    filtered = filtered.replace('"commit_allowed"', "")
    filtered = filtered.replace('"commit_request"', "")
    filtered = filtered.replace('"commit_created"', "")
    filtered = filtered.replace('"deployment_allowed"', "")
    filtered = filtered.replace('"deployment_request"', "")
    filtered = filtered.replace('"deployment_performed"', "")
    filtered = filtered.replace('"provider_invocation_allowed"', "")
    filtered = filtered.replace('"provider_invoked"', "")

    assert "os.system" not in source
    assert "shell=True" not in source
    assert "raw_command=" not in source
    assert "git " not in filtered.lower()
    assert "commit(" not in filtered
    assert "deploy" not in filtered
    assert "invoke_live_external_llm_provider(" not in source
