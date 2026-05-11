"""Governed targeted test command preparation.

This module validates and prepares a bounded pytest command for
GOVERNED_TEST_EXECUTION_V1. It never executes tests, starts servers, chains
shell commands, or grants arbitrary subprocess authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .primitive_replay import build_deterministic_result_hash, build_replay_identity


ALLOWED_TEST_TARGET = "tests/test_governed_preview_runtime.py"
ALLOWED_TEST_COMMAND = ("pytest", ALLOWED_TEST_TARGET)
PRIMITIVE_ID = "GOVERNED_TEST_EXECUTION_V1"
SCOPE_ID = "TARGETED_PYTEST_PREVIEW_RUNTIME_ONLY"
REPLAY_LINEAGE = (
    "AGENTS.md",
    "docs/governance/CODEX_TASK_EXECUTION_PROTOCOL_V1.md",
    "docs/governance/GOVERNED_TEST_EXECUTION_V1.md",
    "runtime/governance/test_execution.py",
    "tests/test_governed_test_execution.py",
)
FORBIDDEN_TOKENS = (
    "&&",
    "||",
    ";",
    "|",
    "`",
    "$(",
    ">",
    "<",
    "rm",
    "sudo",
    "systemctl",
    "uvicorn",
    "gunicorn",
    "deploy",
)


@dataclass(frozen=True)
class GovernedTestExecutionRequest:
    test_target: str = ALLOWED_TEST_TARGET
    runner: str = "pytest"
    full_suite: bool = False
    deployment: bool = False
    server_start: bool = False
    shell_chaining: bool = False
    arbitrary_subprocess: bool = False
    destructive: bool = False
    background_execution: bool = False
    production_mutation: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "arbitrary_subprocess": self.arbitrary_subprocess,
            "background_execution": self.background_execution,
            "deployment": self.deployment,
            "destructive": self.destructive,
            "full_suite": self.full_suite,
            "production_mutation": self.production_mutation,
            "runner": self.runner,
            "server_start": self.server_start,
            "shell_chaining": self.shell_chaining,
            "test_target": self.test_target,
        }


@dataclass(frozen=True)
class GovernedTestExecutionResult:
    primitive_id: str
    approved: bool
    escalation_required: bool
    rejected: bool
    command: tuple[str, ...]
    reason: str
    forbidden_boundary_checks: tuple[str, ...]
    request_hash: str
    command_hash: str
    scope_hash: str
    replay_lineage: tuple[str, ...]
    deterministic_hash: str
    executed: bool = False

    def to_dict(self, include_hash: bool = True) -> dict[str, Any]:
        data: dict[str, Any] = {
            "approved": self.approved,
            "command_hash": self.command_hash,
            "command": list(self.command),
            "escalation_required": self.escalation_required,
            "executed": self.executed,
            "forbidden_boundary_checks": list(self.forbidden_boundary_checks),
            "primitive_id": self.primitive_id,
            "reason": self.reason,
            "rejected": self.rejected,
            "replay_lineage": list(self.replay_lineage),
            "request_hash": self.request_hash,
            "scope_hash": self.scope_hash,
        }
        if include_hash:
            data["deterministic_hash"] = self.deterministic_hash
        return data


def describe_test_execution_scope() -> dict[str, object]:
    return {
        "allowed_command": list(ALLOWED_TEST_COMMAND),
        "forbidden": [
            "full test suite by default",
            "deployment",
            "server start",
            "shell chaining",
            "arbitrary subprocess",
            "destructive commands",
            "background execution",
            "production mutation",
        ],
        "primitive": PRIMITIVE_ID,
        "replay_lineage": list(REPLAY_LINEAGE),
        "scope_id": SCOPE_ID,
        "scope_hash": _scope_hash(),
        "tests_executed_by_helper": False,
    }


def build_test_command(
    request: GovernedTestExecutionRequest | None = None,
) -> tuple[str, ...]:
    request = request or GovernedTestExecutionRequest()
    if validate_test_execution_request(request).approved:
        return ALLOWED_TEST_COMMAND
    return ()


def validate_test_execution_request(
    request: GovernedTestExecutionRequest,
) -> GovernedTestExecutionResult:
    forbidden = _forbidden_boundary_checks(request)
    if forbidden:
        return _result(
            approved=False,
            escalation_required=True,
            rejected=False,
            command=(),
            reason="forbidden boundary requires renewed approval",
            forbidden_boundary_checks=forbidden,
        )

    if request.runner != "pytest":
        return _result(
            approved=False,
            escalation_required=True,
            rejected=False,
            command=(),
            reason="runner change requires renewed approval",
            forbidden_boundary_checks=(),
        )

    if request.test_target != ALLOWED_TEST_TARGET:
        return _result(
            approved=False,
            escalation_required=True,
            rejected=False,
            command=(),
            reason="test target change requires renewed approval",
            forbidden_boundary_checks=(),
        )

    return _result(
        approved=True,
        escalation_required=False,
        rejected=False,
        command=ALLOWED_TEST_COMMAND,
        reason="targeted governed pytest command approved",
        forbidden_boundary_checks=(),
    )


def _forbidden_boundary_checks(
    request: GovernedTestExecutionRequest,
) -> tuple[str, ...]:
    checks: list[str] = []
    if request.full_suite or request.test_target in {"tests", "tests/", "."}:
        checks.append("full_test_suite_forbidden_by_default")
    if request.deployment:
        checks.append("deployment_forbidden")
    if request.server_start:
        checks.append("server_start_forbidden")
    if request.shell_chaining or any(token in request.test_target for token in FORBIDDEN_TOKENS):
        checks.append("shell_chaining_forbidden")
    if request.arbitrary_subprocess:
        checks.append("arbitrary_subprocess_forbidden")
    if request.destructive:
        checks.append("destructive_command_forbidden")
    if request.background_execution:
        checks.append("background_execution_forbidden")
    if request.production_mutation:
        checks.append("production_mutation_forbidden")
    return tuple(sorted(checks))


def _result(
    *,
    approved: bool,
    escalation_required: bool,
    rejected: bool,
    command: tuple[str, ...],
    reason: str,
    forbidden_boundary_checks: tuple[str, ...],
) -> GovernedTestExecutionResult:
    request_payload = {
        "command": list(command),
        "forbidden_boundary_checks": list(forbidden_boundary_checks),
        "primitive_id": PRIMITIVE_ID,
        "reason": reason,
        "scope_id": SCOPE_ID,
    }
    replay_identity = build_replay_identity(
        primitive_id=PRIMITIVE_ID,
        request_payload=request_payload,
        command=command,
        scope_payload=_scope_payload(),
        replay_lineage=REPLAY_LINEAGE,
    )
    base = {
        "approved": approved,
        "command": list(command),
        "command_hash": replay_identity["command_hash"],
        "escalation_required": escalation_required,
        "executed": False,
        "forbidden_boundary_checks": list(forbidden_boundary_checks),
        "primitive_id": replay_identity["primitive_id"],
        "reason": reason,
        "replay_lineage": list(REPLAY_LINEAGE),
        "request_hash": replay_identity["request_hash"],
        "rejected": rejected,
        "scope_hash": replay_identity["scope_hash"],
    }
    return GovernedTestExecutionResult(
        primitive_id=str(replay_identity["primitive_id"]),
        approved=approved,
        escalation_required=escalation_required,
        rejected=rejected,
        command=command,
        reason=reason,
        forbidden_boundary_checks=forbidden_boundary_checks,
        request_hash=str(replay_identity["request_hash"]),
        command_hash=str(replay_identity["command_hash"]),
        scope_hash=str(replay_identity["scope_hash"]),
        replay_lineage=REPLAY_LINEAGE,
        deterministic_hash=build_deterministic_result_hash(base),
    )


def _scope_hash() -> str:
    return str(
        build_replay_identity(
            primitive_id=PRIMITIVE_ID,
            request_payload={},
            command=ALLOWED_TEST_COMMAND,
            scope_payload=_scope_payload(),
            replay_lineage=REPLAY_LINEAGE,
        )["scope_hash"]
    )


def _scope_payload() -> dict[str, object]:
    return {
        "allowed_command": list(ALLOWED_TEST_COMMAND),
        "forbidden": [
            "full test suite by default",
            "deployment",
            "server start",
            "shell chaining",
            "arbitrary subprocess",
            "destructive commands",
            "background execution",
            "production mutation",
        ],
        "primitive_id": PRIMITIVE_ID,
        "scope_id": SCOPE_ID,
    }
