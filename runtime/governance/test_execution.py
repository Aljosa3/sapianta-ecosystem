"""Governed targeted test command preparation.

This module validates and prepares a bounded pytest command for
GOVERNED_TEST_EXECUTION_V1. It never executes tests, starts servers, chains
shell commands, or grants arbitrary subprocess authority.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any


ALLOWED_TEST_TARGET = "tests/test_governed_preview_runtime.py"
ALLOWED_TEST_COMMAND = ("pytest", ALLOWED_TEST_TARGET)
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
    approved: bool
    escalation_required: bool
    rejected: bool
    command: tuple[str, ...]
    reason: str
    forbidden_boundary_checks: tuple[str, ...]
    deterministic_hash: str
    executed: bool = False

    def to_dict(self, include_hash: bool = True) -> dict[str, Any]:
        data: dict[str, Any] = {
            "approved": self.approved,
            "command": list(self.command),
            "escalation_required": self.escalation_required,
            "executed": self.executed,
            "forbidden_boundary_checks": list(self.forbidden_boundary_checks),
            "reason": self.reason,
            "rejected": self.rejected,
        }
        if include_hash:
            data["deterministic_hash"] = self.deterministic_hash
        return data


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_hash(data: object) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


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
        "primitive": "GOVERNED_TEST_EXECUTION_V1",
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
    base = {
        "approved": approved,
        "command": list(command),
        "escalation_required": escalation_required,
        "executed": False,
        "forbidden_boundary_checks": list(forbidden_boundary_checks),
        "reason": reason,
        "rejected": rejected,
    }
    return GovernedTestExecutionResult(
        approved=approved,
        escalation_required=escalation_required,
        rejected=rejected,
        command=command,
        reason=reason,
        forbidden_boundary_checks=forbidden_boundary_checks,
        deterministic_hash=stable_hash(base),
    )

