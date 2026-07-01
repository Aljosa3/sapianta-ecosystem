"""OCS-owned validation candidate helpers."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_validation_allowlist import get_validation_command_spec
from aigol.runtime.transport.serialization import replay_hash
from aigol.workers.validation_command_worker import (
    AUTHORIZED_VALIDATION_SCOPE,
    OPERATION_RUN_VALIDATION_COMMAND,
    VALIDATION_COMMAND_WORKER_ID,
)


VALIDATION_CANDIDATE_VERSION = "G8_14_GOVERNED_VALIDATION_EXECUTION_IMPLEMENTATION_V1"
VALIDATION_CANDIDATE_ARTIFACT_V1 = "VALIDATION_CANDIDATE_ARTIFACT_V1"
RUN_SINGLE_ALLOWLISTED_VALIDATION_COMMAND = "RUN_SINGLE_ALLOWLISTED_VALIDATION_COMMAND"


def create_governed_validation_candidate(
    *,
    candidate_id: str,
    session_id: str,
    command_id: str,
    validation_purpose: str,
    created_by: str,
    created_at: str,
    associated_reference: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create an OCS validation execution candidate from a static allowlist command."""

    command_spec = get_validation_command_spec(command_id)
    artifact = {
        "artifact_type": VALIDATION_CANDIDATE_ARTIFACT_V1,
        "runtime_version": VALIDATION_CANDIDATE_VERSION,
        "candidate_id": _require_string(candidate_id, "candidate_id"),
        "session_id": _require_string(session_id, "session_id"),
        "operation": RUN_SINGLE_ALLOWLISTED_VALIDATION_COMMAND,
        "validation_purpose": _require_string(validation_purpose, "validation_purpose"),
        "command_id": command_spec["command_id"],
        "argv_hash": command_spec["argv_hash"],
        "command_spec_hash": command_spec["spec_hash"],
        "command_spec": command_spec,
        "worker_id": VALIDATION_COMMAND_WORKER_ID,
        "worker_scope": AUTHORIZED_VALIDATION_SCOPE,
        "worker_operation": OPERATION_RUN_VALIDATION_COMMAND,
        "command_count": 1,
        "shell_allowed": False,
        "raw_command_string_allowed": False,
        "git_allowed": False,
        "commit_allowed": False,
        "deployment_allowed": False,
        "provider_invocation_allowed": False,
        "package_install_allowed": False,
        "network_allowed": False,
        "repository_mutation_allowed": False,
        "human_approval_required": True,
        "governance_authorization_required": True,
        "replay_required": True,
        "associated_reference": deepcopy(associated_reference or {}),
        "created_by": _require_string(created_by, "created_by"),
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def validate_governed_validation_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    artifact = deepcopy(candidate)
    _verify_artifact_hash(artifact)
    if artifact.get("artifact_type") != VALIDATION_CANDIDATE_ARTIFACT_V1:
        raise FailClosedRuntimeError("governed validation failed closed: candidate artifact required")
    if artifact.get("operation") != RUN_SINGLE_ALLOWLISTED_VALIDATION_COMMAND:
        raise FailClosedRuntimeError("governed validation failed closed: operation not authorized")
    if artifact.get("worker_id") != VALIDATION_COMMAND_WORKER_ID:
        raise FailClosedRuntimeError("governed validation failed closed: Worker mismatch")
    if artifact.get("worker_scope") != AUTHORIZED_VALIDATION_SCOPE:
        raise FailClosedRuntimeError("governed validation failed closed: Worker scope mismatch")
    if artifact.get("worker_operation") != OPERATION_RUN_VALIDATION_COMMAND:
        raise FailClosedRuntimeError("governed validation failed closed: Worker operation mismatch")
    if artifact.get("command_count") != 1:
        raise FailClosedRuntimeError("governed validation failed closed: exactly one command required")
    for flag in (
        "shell_allowed",
        "raw_command_string_allowed",
        "git_allowed",
        "commit_allowed",
        "deployment_allowed",
        "provider_invocation_allowed",
        "package_install_allowed",
        "network_allowed",
        "repository_mutation_allowed",
    ):
        if artifact.get(flag) is not False:
            raise FailClosedRuntimeError(f"governed validation failed closed: {flag} must be false")
    command_spec = get_validation_command_spec(artifact.get("command_id"))
    if artifact.get("argv_hash") != command_spec["argv_hash"]:
        raise FailClosedRuntimeError("governed validation failed closed: argv hash mismatch")
    if artifact.get("command_spec_hash") != command_spec["spec_hash"]:
        raise FailClosedRuntimeError("governed validation failed closed: command spec hash mismatch")
    if artifact.get("command_spec") != command_spec:
        raise FailClosedRuntimeError("governed validation failed closed: command spec mismatch")
    return artifact


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("governed validation artifact must be a JSON object")
    actual = _require_string(artifact.get("artifact_hash"), "artifact_hash")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("governed validation artifact hash mismatch")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"governed validation requires {field}")
    return value
