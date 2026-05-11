from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from runtime.governance.test_execution import (
    ALLOWED_TEST_COMMAND,
    PRIMITIVE_ID,
    GovernedTestExecutionRequest,
    build_test_command,
    describe_test_execution_scope,
    validate_test_execution_request,
)


def test_allowed_targeted_pytest_command_is_approved() -> None:
    result = validate_test_execution_request(GovernedTestExecutionRequest())

    assert result.approved is True
    assert result.escalation_required is False
    assert result.command == ALLOWED_TEST_COMMAND
    assert result.executed is False


def test_full_suite_is_forbidden_by_default() -> None:
    result = validate_test_execution_request(
        GovernedTestExecutionRequest(test_target="tests", full_suite=True)
    )

    assert result.approved is False
    assert result.escalation_required is True
    assert "full_test_suite_forbidden_by_default" in result.forbidden_boundary_checks


def test_different_test_target_escalates() -> None:
    result = validate_test_execution_request(
        GovernedTestExecutionRequest(test_target="tests/test_governed_capability_memory.py")
    )

    assert result.approved is False
    assert result.escalation_required is True
    assert result.reason == "test target change requires renewed approval"


def test_deployment_semantics_escalate() -> None:
    result = validate_test_execution_request(GovernedTestExecutionRequest(deployment=True))

    assert result.approved is False
    assert result.escalation_required is True
    assert "deployment_forbidden" in result.forbidden_boundary_checks


def test_server_start_is_forbidden() -> None:
    result = validate_test_execution_request(GovernedTestExecutionRequest(server_start=True))

    assert result.approved is False
    assert "server_start_forbidden" in result.forbidden_boundary_checks


def test_shell_chaining_is_forbidden() -> None:
    result = validate_test_execution_request(
        GovernedTestExecutionRequest(test_target="tests/test_governed_preview_runtime.py && rm -rf /")
    )

    assert result.approved is False
    assert "shell_chaining_forbidden" in result.forbidden_boundary_checks


def test_command_generation_is_deterministic() -> None:
    first = build_test_command(GovernedTestExecutionRequest())
    second = build_test_command(GovernedTestExecutionRequest())

    assert first == second == ALLOWED_TEST_COMMAND
    assert " ".join(first) == "pytest tests/test_governed_preview_runtime.py"


def test_scope_description_is_non_executing() -> None:
    description = describe_test_execution_scope()

    assert description["allowed_command"] == list(ALLOWED_TEST_COMMAND)
    assert description["tests_executed_by_helper"] is False


def test_result_hash_is_stable() -> None:
    first = validate_test_execution_request(GovernedTestExecutionRequest())
    second = validate_test_execution_request(GovernedTestExecutionRequest())

    assert first.deterministic_hash == second.deterministic_hash
    assert first.to_dict() == second.to_dict()


def test_replay_visibility_fields_are_present_and_stable() -> None:
    result = validate_test_execution_request(GovernedTestExecutionRequest())
    repeated = validate_test_execution_request(GovernedTestExecutionRequest())
    description = describe_test_execution_scope()

    assert result.primitive_id == PRIMITIVE_ID
    assert result.request_hash == repeated.request_hash
    assert result.command_hash == repeated.command_hash
    assert result.scope_hash == repeated.scope_hash
    assert result.scope_hash == description["scope_hash"]
    assert "runtime/governance/test_execution.py" in result.replay_lineage
