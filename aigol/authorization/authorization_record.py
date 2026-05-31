"""Deterministic governed worker authorization record."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


AUTHORIZED = "AUTHORIZED"
AUTHORIZATION_RECORD_TYPE = "GOVERNED_WORKER_AUTHORIZATION_RECORD_V1"

FORBIDDEN_AUTHORIZATION_FIELDS = frozenset(
    {
        "provider_authority",
        "proposal_authority",
        "cognition_authority",
        "replay_authority",
        "worker_self_authorized",
        "dispatch_request",
        "worker_invocation",
        "execution_started",
        "execution_result",
        "orchestration_request",
        "memory_mutation",
        "replay_mutation",
    }
)


@dataclass(frozen=True)
class AuthorizationRecord:
    authorization_id: str
    proposal_id: str
    worker_id: str
    authorization_scope: str
    authorization_timestamp: str
    authorization_status: str
    authorization_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        record = {
            "record_type": AUTHORIZATION_RECORD_TYPE,
            "authorization_id": _require_string(self.authorization_id, "authorization_id"),
            "proposal_id": _require_string(self.proposal_id, "proposal_id"),
            "worker_id": _require_string(self.worker_id, "worker_id"),
            "authorization_scope": _normalize_scope(self.authorization_scope),
            "authorization_timestamp": _require_string(
                self.authorization_timestamp,
                "authorization_timestamp",
            ),
            "authorization_status": _normalize_status(self.authorization_status),
            "replay_visible": True,
            "governed_authorization": True,
            "provider_can_authorize": False,
            "proposal_can_authorize": False,
            "cognition_can_authorize": False,
            "replay_can_authorize": False,
            "worker_can_self_authorize": False,
            "worker_invoked": False,
            "dispatch_performed": False,
            "execution_performed": False,
        }
        record["authorization_hash"] = self.authorization_hash or replay_hash(record)
        return record


def create_authorization_record(
    *,
    authorization_id: str,
    proposal_id: str,
    worker_id: str,
    authorization_scope: str,
    authorization_timestamp: str,
) -> AuthorizationRecord:
    record = AuthorizationRecord(
        authorization_id=authorization_id,
        proposal_id=proposal_id,
        worker_id=worker_id,
        authorization_scope=authorization_scope,
        authorization_timestamp=authorization_timestamp,
        authorization_status=AUTHORIZED,
    )
    record_dict = record.to_dict()
    return AuthorizationRecord(
        authorization_id=record.authorization_id,
        proposal_id=record.proposal_id,
        worker_id=record.worker_id,
        authorization_scope=record.authorization_scope,
        authorization_timestamp=record.authorization_timestamp,
        authorization_status=record.authorization_status,
        authorization_hash=record_dict["authorization_hash"],
    )


def validate_authorization_record(record: AuthorizationRecord | dict[str, Any]) -> dict[str, Any]:
    record_dict = record.to_dict() if isinstance(record, AuthorizationRecord) else deepcopy(record)
    if not isinstance(record_dict, dict):
        raise FailClosedRuntimeError("authorization record must be a JSON object")
    if record_dict.get("record_type") != AUTHORIZATION_RECORD_TYPE:
        raise FailClosedRuntimeError("authorization record type is invalid")
    if FORBIDDEN_AUTHORIZATION_FIELDS.intersection(record_dict):
        raise FailClosedRuntimeError("authorization record contains forbidden authority field")
    _require_string(record_dict.get("authorization_id"), "authorization_id")
    _require_string(record_dict.get("proposal_id"), "proposal_id")
    _require_string(record_dict.get("worker_id"), "worker_id")
    _normalize_scope(record_dict.get("authorization_scope"))
    _require_string(record_dict.get("authorization_timestamp"), "authorization_timestamp")
    if record_dict.get("authorization_status") != AUTHORIZED:
        raise FailClosedRuntimeError("authorization record must be AUTHORIZED")
    if record_dict.get("replay_visible") is not True:
        raise FailClosedRuntimeError("authorization record must be replay visible")
    if record_dict.get("governed_authorization") is not True:
        raise FailClosedRuntimeError("authorization record must be governed")
    if record_dict.get("provider_can_authorize") is not False:
        raise FailClosedRuntimeError("provider cannot authorize execution")
    if record_dict.get("proposal_can_authorize") is not False:
        raise FailClosedRuntimeError("proposal cannot authorize execution")
    if record_dict.get("cognition_can_authorize") is not False:
        raise FailClosedRuntimeError("cognition cannot authorize execution")
    if record_dict.get("replay_can_authorize") is not False:
        raise FailClosedRuntimeError("replay cannot authorize execution")
    if record_dict.get("worker_can_self_authorize") is not False:
        raise FailClosedRuntimeError("worker cannot self-authorize")
    if record_dict.get("worker_invoked") is not False:
        raise FailClosedRuntimeError("authorization record cannot invoke worker")
    if record_dict.get("dispatch_performed") is not False:
        raise FailClosedRuntimeError("authorization record cannot dispatch")
    if record_dict.get("execution_performed") is not False:
        raise FailClosedRuntimeError("authorization record cannot execute")
    actual_hash = _require_string(record_dict.get("authorization_hash"), "authorization_hash")
    expected_input = deepcopy(record_dict)
    expected_input.pop("authorization_hash")
    if actual_hash != replay_hash(expected_input):
        raise FailClosedRuntimeError("authorization record hash mismatch")
    return record_dict


def _normalize_scope(value: Any) -> str:
    return _require_string(value, "authorization_scope").strip().upper().replace("-", "_").replace(" ", "_")


def _normalize_status(value: Any) -> str:
    status = _require_string(value, "authorization_status").strip().upper()
    if status != AUTHORIZED:
        raise FailClosedRuntimeError("authorization status must be AUTHORIZED")
    return status


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value

