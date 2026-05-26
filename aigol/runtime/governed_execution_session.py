"""Minimal governed execution session lifecycle for AiGOL."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED = "CREATED"
ACTIVE = "ACTIVE"
CLOSED = "CLOSED"
FAILED = "FAILED"

ALLOWED_SESSION_STATUSES = frozenset({CREATED, ACTIVE, CLOSED, FAILED})
ALLOWED_PROVIDER_NAMES = frozenset(
    {
        "readonly_filesystem_provider",
        "readonly_http_get_provider",
        "metadata_inspection_provider",
    }
)
ALLOWED_PROVIDER_OPERATIONS = {
    "readonly_filesystem_provider": frozenset({"inspect_metadata", "read_file", "list_allowed_directory"}),
    "readonly_http_get_provider": frozenset({"fetch"}),
    "metadata_inspection_provider": frozenset({"inspect_runtime", "inspect_environment", "inspect_process"}),
}


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _immutable(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({key: _immutable(value[key]) for key in sorted(value)})
    if isinstance(value, list | tuple):
        return tuple(_immutable(item) for item in value)
    return deepcopy(value)


def _plain(value: Any) -> Any:
    if isinstance(value, MappingProxyType):
        return {key: _plain(value[key]) for key in value}
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    return deepcopy(value)


def _canonical_copy(value: dict[str, Any], field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"{field_name} must be a JSON object")
    try:
        canonical_serialize(value)
    except (TypeError, ValueError) as exc:
        raise FailClosedRuntimeError(f"{field_name} must be JSON serializable") from exc
    return deepcopy(value)


def _require_status(status: str) -> str:
    if status not in ALLOWED_SESSION_STATUSES:
        raise FailClosedRuntimeError("session status must be CREATED, ACTIVE, CLOSED, or FAILED")
    return status


def _session_hash_input(session: "GovernedExecutionSession") -> dict[str, Any]:
    return {
        "session_id": session.session_id,
        "created_at": session.created_at,
        "status": session.status,
        "operations": [_plain(operation) for operation in session.operations],
        "closed_at": session.closed_at,
    }


@dataclass(frozen=True)
class GovernedExecutionSession:
    """Single local session with append-only provider evidence lineage."""

    session_id: str
    created_at: str
    status: str
    operations: tuple[MappingProxyType, ...] = ()
    closed_at: str = ""
    evidence_hash: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.session_id, str) or not self.session_id.strip():
            raise FailClosedRuntimeError("session_id is required")
        if not isinstance(self.created_at, str) or not self.created_at.strip():
            raise FailClosedRuntimeError("created_at is required")
        _require_status(self.status)
        if self.status == CLOSED and not self.closed_at:
            raise FailClosedRuntimeError("closed_at is required for CLOSED sessions")
        if self.status != CLOSED and self.closed_at:
            raise FailClosedRuntimeError("closed_at is only valid for CLOSED sessions")
        immutable_operations = tuple(_immutable(_plain(operation)) for operation in self.operations)
        object.__setattr__(self, "operations", immutable_operations)
        expected_hash = replay_hash(_session_hash_input(self))
        if self.evidence_hash and self.evidence_hash != expected_hash:
            raise FailClosedRuntimeError("session evidence hash mismatch")
        object.__setattr__(self, "evidence_hash", self.evidence_hash or expected_hash)

    def attach_provider_evidence(
        self,
        *,
        provider: str,
        provider_operation: str,
        evidence: dict[str, Any],
        attached_at: str | None = None,
    ) -> "GovernedExecutionSession":
        if self.status == CLOSED:
            raise FailClosedRuntimeError("cannot attach operations after CLOSED")
        if self.status == FAILED:
            raise FailClosedRuntimeError("cannot attach operations after FAILED")
        if self.status not in {CREATED, ACTIVE}:
            raise FailClosedRuntimeError("invalid session state for attach")
        if provider not in ALLOWED_PROVIDER_NAMES:
            raise FailClosedRuntimeError("provider is not allowed for governed execution sessions")
        if not isinstance(provider_operation, str) or not provider_operation.strip():
            raise FailClosedRuntimeError("provider_operation is required")
        if provider_operation not in ALLOWED_PROVIDER_OPERATIONS[provider]:
            raise FailClosedRuntimeError("provider_operation is not allowed for this provider")

        evidence_copy = _canonical_copy(evidence, "provider evidence")
        previous_hash = ""
        if self.operations:
            previous_hash = _plain(self.operations[-1])["operation_hash"]
        operation = {
            "operation_index": len(self.operations),
            "provider": provider,
            "provider_operation": provider_operation,
            "attached_at": attached_at or _utc_timestamp(),
            "previous_operation_hash": previous_hash,
            "evidence": evidence_copy,
        }
        operation["operation_hash"] = replay_hash(operation)
        return GovernedExecutionSession(
            session_id=self.session_id,
            created_at=self.created_at,
            status=ACTIVE,
            operations=self.operations + (_immutable(operation),),
            closed_at="",
        )

    def close_session(self, *, closed_at: str | None = None) -> "GovernedExecutionSession":
        if self.status == CLOSED:
            raise FailClosedRuntimeError("session is already CLOSED")
        if self.status == FAILED:
            raise FailClosedRuntimeError("cannot close FAILED session")
        if self.status not in {CREATED, ACTIVE}:
            raise FailClosedRuntimeError("invalid session state for closure")
        return GovernedExecutionSession(
            session_id=self.session_id,
            created_at=self.created_at,
            status=CLOSED,
            operations=self.operations,
            closed_at=closed_at or _utc_timestamp(),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "status": self.status,
            "operations": [_plain(operation) for operation in self.operations],
            "closed_at": self.closed_at,
            "evidence_hash": self.evidence_hash,
        }


def create_governed_execution_session(
    *,
    session_id: str,
    created_at: str | None = None,
) -> GovernedExecutionSession:
    return GovernedExecutionSession(
        session_id=session_id,
        created_at=created_at or _utc_timestamp(),
        status=CREATED,
    )


def reconstruct_session_lineage(session: GovernedExecutionSession) -> dict[str, Any]:
    if not isinstance(session, GovernedExecutionSession):
        raise FailClosedRuntimeError("session must be a GovernedExecutionSession")
    session_dict = session.to_dict()
    operations = session_dict["operations"]
    for index, operation in enumerate(operations):
        if operation.get("operation_index") != index:
            raise FailClosedRuntimeError("operation order is not deterministic")
        expected_previous = "" if index == 0 else operations[index - 1]["operation_hash"]
        if operation.get("previous_operation_hash") != expected_previous:
            raise FailClosedRuntimeError("operation lineage is broken")
        operation_hash = operation.get("operation_hash")
        operation_input = deepcopy(operation)
        operation_input.pop("operation_hash", None)
        if operation_hash != replay_hash(operation_input):
            raise FailClosedRuntimeError("operation evidence hash mismatch")
    expected_session_hash = replay_hash(
        {
            "session_id": session_dict["session_id"],
            "created_at": session_dict["created_at"],
            "status": session_dict["status"],
            "operations": operations,
            "closed_at": session_dict["closed_at"],
        }
    )
    if session_dict["evidence_hash"] != expected_session_hash:
        raise FailClosedRuntimeError("session evidence hash mismatch")
    return {
        "session_id": session.session_id,
        "status": session.status,
        "operation_count": len(operations),
        "operation_hash_chain": [operation["operation_hash"] for operation in operations],
        "closed_at": session.closed_at,
        "session_evidence_hash": session.evidence_hash,
        "replay_valid": True,
    }
