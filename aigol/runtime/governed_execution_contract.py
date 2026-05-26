"""Minimal governed execution contract model for AiGOL."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any

from aigol.runtime.governed_execution_session import (
    ALLOWED_PROVIDER_NAMES,
    ALLOWED_PROVIDER_OPERATIONS,
    CLOSED,
    GovernedExecutionSession,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED = "CREATED"
VALIDATED = "VALIDATED"
REJECTED = "REJECTED"
ATTACHED = "ATTACHED"

ALLOWED_CONTRACT_STATUSES = frozenset({CREATED, VALIDATED, REJECTED, ATTACHED})


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


def _contract_hash_input(contract: "GovernedExecutionContract") -> dict[str, Any]:
    return {
        "contract_id": contract.contract_id,
        "created_at": contract.created_at,
        "requested_operations": [_plain(operation) for operation in contract.requested_operations],
        "allowed_providers": list(contract.allowed_providers),
        "session_id": contract.session_id,
        "status": contract.status,
    }


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _normalize_allowed_providers(allowed_providers: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    if not isinstance(allowed_providers, list | tuple) or not allowed_providers:
        raise FailClosedRuntimeError("allowed_providers must be a non-empty list")
    normalized = tuple(allowed_providers)
    if len(set(normalized)) != len(normalized):
        raise FailClosedRuntimeError("allowed_providers must not contain duplicates")
    for provider in normalized:
        if provider not in ALLOWED_PROVIDER_NAMES:
            raise FailClosedRuntimeError("unknown provider is not authorized")
    return tuple(sorted(normalized))


def _normalize_requested_operations(requested_operations: list[dict[str, Any]] | tuple[dict[str, Any], ...]) -> tuple[MappingProxyType, ...]:
    if not isinstance(requested_operations, list | tuple) or not requested_operations:
        raise FailClosedRuntimeError("requested_operations must be a non-empty list")
    normalized = []
    seen_operation_ids: set[str] = set()
    previous_created_at = ""
    for index, operation in enumerate(requested_operations):
        if not isinstance(operation, dict):
            raise FailClosedRuntimeError("requested operation must be a JSON object")
        if set(operation) != {"provider", "operation", "operation_id", "created_at"}:
            raise FailClosedRuntimeError("requested operation has malformed structure")
        provider = _require_string(operation.get("provider"), "provider")
        provider_operation = _require_string(operation.get("operation"), "operation")
        operation_id = _require_string(operation.get("operation_id"), "operation_id")
        created_at = _require_string(operation.get("created_at"), "operation created_at")
        if provider not in ALLOWED_PROVIDER_NAMES:
            raise FailClosedRuntimeError("unknown provider is not authorized")
        if provider_operation not in ALLOWED_PROVIDER_OPERATIONS[provider]:
            raise FailClosedRuntimeError("unsupported provider operation is not authorized")
        if operation_id in seen_operation_ids:
            raise FailClosedRuntimeError("requested_operations must be append-only and unique")
        if previous_created_at and created_at < previous_created_at:
            raise FailClosedRuntimeError("requested_operations ordering must be deterministic")
        seen_operation_ids.add(operation_id)
        previous_created_at = created_at
        normalized.append(
            {
                "provider": provider,
                "operation": provider_operation,
                "operation_id": operation_id,
                "created_at": created_at,
            }
        )
    canonical_serialize(normalized)
    return tuple(_immutable(operation) for operation in normalized)


@dataclass(frozen=True)
class GovernedExecutionContract:
    """Declarative execution intent contract without execution authority."""

    contract_id: str
    created_at: str
    requested_operations: tuple[MappingProxyType, ...]
    allowed_providers: tuple[str, ...]
    session_id: str
    status: str
    evidence_hash: str = ""

    def __post_init__(self) -> None:
        _require_string(self.contract_id, "contract_id")
        _require_string(self.created_at, "created_at")
        if self.status not in ALLOWED_CONTRACT_STATUSES:
            raise FailClosedRuntimeError("contract status must be CREATED, VALIDATED, REJECTED, or ATTACHED")
        if self.status == ATTACHED and not self.session_id:
            raise FailClosedRuntimeError("session_id is required for ATTACHED contracts")
        if self.status != ATTACHED and self.session_id:
            raise FailClosedRuntimeError("session_id is only valid for ATTACHED contracts")
        normalized_operations = _normalize_requested_operations([_plain(operation) for operation in self.requested_operations])
        normalized_providers = _normalize_allowed_providers(list(self.allowed_providers))
        for operation in normalized_operations:
            if _plain(operation)["provider"] not in normalized_providers:
                raise FailClosedRuntimeError("requested operation provider is not in allowed_providers")
        object.__setattr__(self, "requested_operations", normalized_operations)
        object.__setattr__(self, "allowed_providers", normalized_providers)
        expected_hash = replay_hash(_contract_hash_input(self))
        if self.evidence_hash and self.evidence_hash != expected_hash:
            raise FailClosedRuntimeError("contract evidence hash mismatch")
        object.__setattr__(self, "evidence_hash", self.evidence_hash or expected_hash)

    def validate_contract(self) -> "GovernedExecutionContract":
        if self.status == ATTACHED:
            raise FailClosedRuntimeError("attached contract cannot be revalidated")
        if self.status == REJECTED:
            raise FailClosedRuntimeError("rejected contract cannot be validated")
        return GovernedExecutionContract(
            contract_id=self.contract_id,
            created_at=self.created_at,
            requested_operations=self.requested_operations,
            allowed_providers=self.allowed_providers,
            session_id="",
            status=VALIDATED,
        )

    def attach_to_session(
        self,
        *,
        session: GovernedExecutionSession,
        attached_at: str | None = None,
    ) -> dict[str, Any]:
        if not isinstance(session, GovernedExecutionSession):
            raise FailClosedRuntimeError("session must be a GovernedExecutionSession")
        if self.status == ATTACHED:
            raise FailClosedRuntimeError("contract is already ATTACHED")
        if self.status != VALIDATED:
            raise FailClosedRuntimeError("contract must be VALIDATED before attachment")
        if session.status == CLOSED:
            raise FailClosedRuntimeError("cannot attach contract to CLOSED session")
        attached_contract = GovernedExecutionContract(
            contract_id=self.contract_id,
            created_at=self.created_at,
            requested_operations=self.requested_operations,
            allowed_providers=self.allowed_providers,
            session_id=session.session_id,
            status=ATTACHED,
        )
        attachment_evidence = {
            "operation": "attach_governed_execution_contract",
            "contract_id": attached_contract.contract_id,
            "session_id": session.session_id,
            "attached_at": attached_at or _utc_timestamp(),
            "contract_evidence_hash": attached_contract.evidence_hash,
            "session_evidence_hash": session.evidence_hash,
            "status": "ATTACHED",
            "reason": "contract attached to governed execution session lineage",
        }
        attachment_evidence["evidence_hash"] = replay_hash(attachment_evidence)
        return {
            "contract": attached_contract,
            "attachment_evidence": attachment_evidence,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_id": self.contract_id,
            "created_at": self.created_at,
            "requested_operations": [_plain(operation) for operation in self.requested_operations],
            "allowed_providers": list(self.allowed_providers),
            "session_id": self.session_id,
            "status": self.status,
            "evidence_hash": self.evidence_hash,
        }

    @classmethod
    def from_dict(cls, artifact: dict[str, Any]) -> "GovernedExecutionContract":
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("contract artifact must be a JSON object")
        required = {"contract_id", "created_at", "requested_operations", "allowed_providers", "session_id", "status", "evidence_hash"}
        if set(artifact) != required:
            raise FailClosedRuntimeError("contract artifact has malformed structure")
        return cls(
            contract_id=artifact["contract_id"],
            created_at=artifact["created_at"],
            requested_operations=tuple(_immutable(operation) for operation in artifact["requested_operations"]),
            allowed_providers=tuple(artifact["allowed_providers"]),
            session_id=artifact["session_id"],
            status=artifact["status"],
            evidence_hash=artifact["evidence_hash"],
        )


def create_governed_execution_contract(
    *,
    contract_id: str,
    created_at: str,
    requested_operations: list[dict[str, Any]],
    allowed_providers: list[str],
) -> GovernedExecutionContract:
    return GovernedExecutionContract(
        contract_id=contract_id,
        created_at=created_at,
        requested_operations=_normalize_requested_operations(requested_operations),
        allowed_providers=_normalize_allowed_providers(allowed_providers),
        session_id="",
        status=CREATED,
    )


def reconstruct_contract_lineage(contract: GovernedExecutionContract | dict[str, Any]) -> dict[str, Any]:
    contract_obj = GovernedExecutionContract.from_dict(contract) if isinstance(contract, dict) else contract
    if not isinstance(contract_obj, GovernedExecutionContract):
        raise FailClosedRuntimeError("contract must be a GovernedExecutionContract")
    artifact = contract_obj.to_dict()
    operation_order = [operation["operation_id"] for operation in artifact["requested_operations"]]
    return {
        "contract_id": artifact["contract_id"],
        "session_id": artifact["session_id"],
        "status": artifact["status"],
        "allowed_providers": artifact["allowed_providers"],
        "operation_order": operation_order,
        "operation_count": len(operation_order),
        "contract_evidence_hash": artifact["evidence_hash"],
        "lineage_hash": replay_hash(
            {
                "contract_id": artifact["contract_id"],
                "session_id": artifact["session_id"],
                "operation_order": operation_order,
                "allowed_providers": artifact["allowed_providers"],
                "contract_evidence_hash": artifact["evidence_hash"],
            }
        ),
    }
