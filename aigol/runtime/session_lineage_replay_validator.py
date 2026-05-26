"""Replay-only validation for governed execution session lineage."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from aigol.runtime.governed_execution_session import (
    ALLOWED_SESSION_STATUSES,
    CLOSED,
    GovernedExecutionSession,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


VALID = "VALID"
INVALID = "INVALID"
ALLOWED_REPLAY_STATUSES = frozenset({VALID, INVALID})


def validate_session_lineage_replay(session: GovernedExecutionSession | dict[str, Any]) -> dict[str, Any]:
    """Validate session replay evidence without executing provider operations."""

    try:
        artifact = _session_artifact(session)
        _require_json_artifact(artifact)
        reconstructed = _reconstruct_operations(artifact.get("operations", []))
        checks = {
            "lineage_valid": _lineage_valid(reconstructed),
            "append_only_valid": _append_only_valid(reconstructed),
            "closure_valid": _closure_valid(artifact, reconstructed),
            "evidence_valid": _evidence_valid(artifact, reconstructed),
        }
        replay_status = VALID if all(checks.values()) else INVALID
        reason = "replay lineage validation succeeded" if replay_status == VALID else _invalid_reason(checks)
        return _result(
            session_id=artifact.get("session_id", ""),
            replay_status=replay_status,
            reconstructed_operations=reconstructed,
            lineage_valid=checks["lineage_valid"],
            append_only_valid=checks["append_only_valid"],
            closure_valid=checks["closure_valid"],
            validation_reason=reason,
        )
    except (TypeError, ValueError, KeyError):
        return _result(
            session_id="",
            replay_status=INVALID,
            reconstructed_operations=[],
            lineage_valid=False,
            append_only_valid=False,
            closure_valid=False,
            validation_reason="session replay artifact is invalid",
        )


def _session_artifact(session: GovernedExecutionSession | dict[str, Any]) -> dict[str, Any]:
    if isinstance(session, GovernedExecutionSession):
        return session.to_dict()
    if isinstance(session, dict):
        return deepcopy(session)
    raise TypeError("session must be a GovernedExecutionSession or JSON object")


def _require_json_artifact(artifact: dict[str, Any]) -> None:
    canonical_serialize(artifact)
    required_fields = {"session_id", "created_at", "status", "operations", "closed_at", "evidence_hash"}
    if set(artifact) < required_fields:
        raise ValueError("session artifact is missing required fields")
    if artifact.get("status") not in ALLOWED_SESSION_STATUSES:
        raise ValueError("session status is invalid")
    if not isinstance(artifact.get("operations"), list):
        raise ValueError("session operations must be a list")


def _reconstruct_operations(operations: list[Any]) -> list[dict[str, Any]]:
    reconstructed = []
    for operation in operations:
        if not isinstance(operation, dict):
            raise ValueError("operation must be a JSON object")
        reconstructed.append(
            {
                "operation_index": operation.get("operation_index"),
                "provider": operation.get("provider"),
                "provider_operation": operation.get("provider_operation"),
                "attached_at": operation.get("attached_at"),
                "previous_operation_hash": operation.get("previous_operation_hash"),
                "operation_hash": operation.get("operation_hash"),
                "evidence_hash": operation.get("evidence", {}).get("evidence_hash") if isinstance(operation.get("evidence"), dict) else "",
                "operation_hash_valid": _operation_hash_valid(operation),
            }
        )
    return reconstructed


def _operation_hash_valid(operation: dict[str, Any]) -> bool:
    operation_hash = operation.get("operation_hash")
    if not isinstance(operation_hash, str) or not operation_hash:
        return False
    operation_input = deepcopy(operation)
    operation_input.pop("operation_hash", None)
    return operation_hash == replay_hash(operation_input)


def _lineage_valid(reconstructed: list[dict[str, Any]]) -> bool:
    for index, operation in enumerate(reconstructed):
        if operation["operation_index"] != index:
            return False
        expected_previous = "" if index == 0 else reconstructed[index - 1]["operation_hash"]
        if operation["previous_operation_hash"] != expected_previous:
            return False
        if not operation["operation_hash_valid"]:
            return False
    return True


def _append_only_valid(reconstructed: list[dict[str, Any]]) -> bool:
    indexes = [operation["operation_index"] for operation in reconstructed]
    hashes = [operation["operation_hash"] for operation in reconstructed]
    if indexes != list(range(len(reconstructed))):
        return False
    if len(set(indexes)) != len(indexes):
        return False
    if len(set(hashes)) != len(hashes):
        return False
    return all(operation["operation_hash_valid"] for operation in reconstructed)


def _closure_valid(artifact: dict[str, Any], reconstructed: list[dict[str, Any]]) -> bool:
    closed_at = artifact.get("closed_at")
    if artifact.get("status") != CLOSED:
        return False
    if not isinstance(closed_at, str) or not closed_at:
        return False
    closure_events = artifact.get("closure_events")
    if closure_events is not None and (not isinstance(closure_events, list) or len(closure_events) != 1):
        return False
    for operation in reconstructed:
        attached_at = operation.get("attached_at")
        if isinstance(attached_at, str) and attached_at and attached_at > closed_at:
            return False
    return True


def _evidence_valid(artifact: dict[str, Any], reconstructed: list[dict[str, Any]]) -> bool:
    if not all(operation["operation_hash_valid"] for operation in reconstructed):
        return False
    evidence_hash = artifact.get("evidence_hash")
    if not isinstance(evidence_hash, str) or not evidence_hash:
        return False
    session_hash_input = {
        "session_id": artifact["session_id"],
        "created_at": artifact["created_at"],
        "status": artifact["status"],
        "operations": artifact["operations"],
        "closed_at": artifact["closed_at"],
    }
    return evidence_hash == replay_hash(session_hash_input)


def _invalid_reason(checks: dict[str, bool]) -> str:
    if not checks["lineage_valid"]:
        return "operation lineage is invalid"
    if not checks["append_only_valid"]:
        return "append-only operation continuity is invalid"
    if not checks["closure_valid"]:
        return "session closure integrity is invalid"
    if not checks["evidence_valid"]:
        return "session or operation evidence hash is invalid"
    return "session replay validation failed closed"


def _result(
    *,
    session_id: str,
    replay_status: str,
    reconstructed_operations: list[dict[str, Any]],
    lineage_valid: bool,
    append_only_valid: bool,
    closure_valid: bool,
    validation_reason: str,
) -> dict[str, Any]:
    result = {
        "session_id": session_id,
        "replay_status": replay_status if replay_status in ALLOWED_REPLAY_STATUSES else INVALID,
        "reconstructed_operations": reconstructed_operations,
        "lineage_valid": lineage_valid,
        "append_only_valid": append_only_valid,
        "closure_valid": closure_valid,
        "validation_reason": validation_reason,
    }
    result["evidence_hash"] = replay_hash(result)
    return result
