"""OCS-owned candidate helpers for governed validation suites."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_validation_candidate import (
    create_governed_validation_candidate,
    validate_governed_validation_candidate,
)
from aigol.runtime.transport.serialization import replay_hash
from aigol.workers.validation_command_worker import AUTHORIZED_VALIDATION_SCOPE, VALIDATION_COMMAND_WORKER_ID


VALIDATION_SUITE_CANDIDATE_VERSION = "G9_13_BROADER_GOVERNED_VALIDATION_SUITES_IMPLEMENTATION_V1"
VALIDATION_SUITE_CANDIDATE_ARTIFACT_V1 = "VALIDATION_SUITE_CANDIDATE_ARTIFACT_V1"
RUN_GOVERNED_VALIDATION_SUITE = "RUN_GOVERNED_VALIDATION_SUITE"


def create_governed_validation_suite_candidate(
    *,
    candidate_id: str,
    session_id: str,
    commands: list[dict[str, Any]],
    created_by: str,
    created_at: str,
    associated_reference: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a deterministic validation suite candidate from single-command candidates."""

    if not isinstance(commands, list) or len(commands) < 2:
        raise FailClosedRuntimeError("governed validation suite requires at least two commands")
    suite_candidate_id = _require_string(candidate_id, "candidate_id")
    command_records = [
        _command_record(
            suite_candidate_id=suite_candidate_id,
            session_id=session_id,
            command=command,
            index=index,
            created_by=created_by,
            created_at=created_at,
        )
        for index, command in enumerate(commands)
    ]
    artifact = {
        "artifact_type": VALIDATION_SUITE_CANDIDATE_ARTIFACT_V1,
        "runtime_version": VALIDATION_SUITE_CANDIDATE_VERSION,
        "candidate_id": suite_candidate_id,
        "session_id": _require_string(session_id, "session_id"),
        "operation": RUN_GOVERNED_VALIDATION_SUITE,
        "command_count": len(command_records),
        "command_order": [record["command_record_id"] for record in command_records],
        "command_ids": [record["command_id"] for record in command_records],
        "commands": command_records,
        "deterministic_ordering": True,
        "suite_envelope_only": True,
        "composes_single_command_validation": True,
        "worker_id": VALIDATION_COMMAND_WORKER_ID,
        "worker_scope": AUTHORIZED_VALIDATION_SCOPE,
        "worker_execution_only": True,
        "ocs_ordering_owner": True,
        "human_approval_required": True,
        "governance_authorization_required": True,
        "replay_required": True,
        "architectural_health_advisory_consumption": True,
        "shell_allowed": False,
        "raw_command_string_allowed": False,
        "git_allowed": False,
        "commit_allowed": False,
        "deployment_allowed": False,
        "provider_invocation_allowed": False,
        "package_install_allowed": False,
        "network_allowed": False,
        "repository_mutation_allowed": False,
        "associated_reference": deepcopy(associated_reference or {}),
        "created_by": _require_string(created_by, "created_by"),
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def validate_governed_validation_suite_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    artifact = deepcopy(candidate)
    _verify_artifact_hash(artifact)
    if artifact.get("artifact_type") != VALIDATION_SUITE_CANDIDATE_ARTIFACT_V1:
        raise FailClosedRuntimeError("governed validation suite failed closed: candidate artifact required")
    if artifact.get("operation") != RUN_GOVERNED_VALIDATION_SUITE:
        raise FailClosedRuntimeError("governed validation suite failed closed: operation mismatch")
    commands = artifact.get("commands")
    if not isinstance(commands, list) or len(commands) < 2:
        raise FailClosedRuntimeError("governed validation suite failed closed: multiple commands required")
    if artifact.get("command_count") != len(commands):
        raise FailClosedRuntimeError("governed validation suite failed closed: command count mismatch")
    command_order: list[str] = []
    command_ids: list[str] = []
    for index, record in enumerate(commands):
        _validate_command_record(record, index)
        command_order.append(record["command_record_id"])
        command_ids.append(record["command_id"])
    if artifact.get("command_order") != command_order:
        raise FailClosedRuntimeError("governed validation suite failed closed: command order mismatch")
    if artifact.get("command_ids") != command_ids:
        raise FailClosedRuntimeError("governed validation suite failed closed: command id order mismatch")
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
            raise FailClosedRuntimeError(f"governed validation suite failed closed: {flag} must be false")
    if artifact.get("worker_id") != VALIDATION_COMMAND_WORKER_ID:
        raise FailClosedRuntimeError("governed validation suite failed closed: Worker mismatch")
    if artifact.get("worker_scope") != AUTHORIZED_VALIDATION_SCOPE:
        raise FailClosedRuntimeError("governed validation suite failed closed: Worker scope mismatch")
    return artifact


def _command_record(
    *,
    suite_candidate_id: str,
    session_id: str,
    command: dict[str, Any],
    index: int,
    created_by: str,
    created_at: str,
) -> dict[str, Any]:
    if not isinstance(command, dict):
        raise FailClosedRuntimeError("governed validation suite command must be an object")
    command_id = _require_string(command.get("command_id"), "command_id")
    purpose = _require_string(command.get("validation_purpose"), "validation_purpose")
    single_candidate = create_governed_validation_candidate(
        candidate_id=f"{suite_candidate_id}:COMMAND-{index:03d}",
        session_id=session_id,
        command_id=command_id,
        validation_purpose=purpose,
        created_by=created_by,
        created_at=created_at,
        associated_reference=command.get("associated_reference"),
    )
    return {
        "command_record_id": f"COMMAND-{index:03d}",
        "command_index": index,
        "command_id": single_candidate["command_id"],
        "validation_purpose": purpose,
        "single_command_candidate": single_candidate,
        "single_command_candidate_hash": single_candidate["artifact_hash"],
        "argv_hash": single_candidate["argv_hash"],
        "command_spec_hash": single_candidate["command_spec_hash"],
        "worker_id": single_candidate["worker_id"],
        "worker_scope": single_candidate["worker_scope"],
        "worker_operation": single_candidate["worker_operation"],
        "worker_execution_only": True,
        "replay_visible": True,
    }


def _validate_command_record(record: dict[str, Any], index: int) -> None:
    if not isinstance(record, dict):
        raise FailClosedRuntimeError("governed validation suite command record must be an object")
    if record.get("command_index") != index:
        raise FailClosedRuntimeError("governed validation suite failed closed: command index mismatch")
    if record.get("command_record_id") != f"COMMAND-{index:03d}":
        raise FailClosedRuntimeError("governed validation suite failed closed: command record id mismatch")
    single_candidate = validate_governed_validation_candidate(record.get("single_command_candidate"))
    if record.get("single_command_candidate_hash") != single_candidate["artifact_hash"]:
        raise FailClosedRuntimeError("governed validation suite failed closed: single command hash mismatch")
    for field in ("command_id", "argv_hash", "command_spec_hash", "worker_id", "worker_scope", "worker_operation"):
        if record.get(field) != single_candidate[field]:
            raise FailClosedRuntimeError(f"governed validation suite failed closed: {field} mismatch")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("governed validation suite artifact must be a JSON object")
    actual = _require_string(artifact.get("artifact_hash"), "artifact_hash")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("governed validation suite artifact hash mismatch")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"governed validation suite requires {field}")
    return value
