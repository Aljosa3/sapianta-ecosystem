"""Deterministic authorization gate for governed execution contracts."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any

from aigol.runtime.governed_execution_contract import GovernedExecutionContract
from aigol.runtime.governed_execution_session import (
    ALLOWED_PROVIDER_NAMES,
    ALLOWED_PROVIDER_OPERATIONS,
    CLOSED,
    GovernedExecutionSession,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


AUTHORIZED = "AUTHORIZED"
REJECTED = "REJECTED"
ALLOWED_AUTHORIZATION_STATUSES = frozenset({AUTHORIZED, REJECTED})


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


def _authorization_hash_input(authorization: "ContractAuthorizationResult") -> dict[str, Any]:
    return {
        "authorization_id": authorization.authorization_id,
        "contract_id": authorization.contract_id,
        "session_id": authorization.session_id,
        "requested_providers": list(authorization.requested_providers),
        "authorized_providers": list(authorization.authorized_providers),
        "rejected_providers": list(authorization.rejected_providers),
        "status": authorization.status,
        "created_at": authorization.created_at,
    }


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


@dataclass(frozen=True)
class ContractAuthorizationResult:
    """Replay-visible authorization evidence without execution authority."""

    authorization_id: str
    contract_id: str
    session_id: str
    requested_providers: tuple[str, ...]
    authorized_providers: tuple[str, ...]
    rejected_providers: tuple[str, ...]
    status: str
    created_at: str
    evidence_hash: str = ""

    def __post_init__(self) -> None:
        _require_string(self.authorization_id, "authorization_id")
        _require_string(self.created_at, "created_at")
        if self.status not in ALLOWED_AUTHORIZATION_STATUSES:
            raise FailClosedRuntimeError("authorization status must be AUTHORIZED or REJECTED")
        requested = tuple(sorted(self.requested_providers))
        authorized = tuple(sorted(self.authorized_providers))
        rejected = tuple(sorted(self.rejected_providers))
        object.__setattr__(self, "requested_providers", requested)
        object.__setattr__(self, "authorized_providers", authorized)
        object.__setattr__(self, "rejected_providers", rejected)
        expected_hash = replay_hash(_authorization_hash_input(self))
        if self.evidence_hash and self.evidence_hash != expected_hash:
            raise FailClosedRuntimeError("authorization evidence hash mismatch")
        object.__setattr__(self, "evidence_hash", self.evidence_hash or expected_hash)

    def to_dict(self) -> dict[str, Any]:
        return {
            "authorization_id": self.authorization_id,
            "contract_id": self.contract_id,
            "session_id": self.session_id,
            "requested_providers": list(self.requested_providers),
            "authorized_providers": list(self.authorized_providers),
            "rejected_providers": list(self.rejected_providers),
            "status": self.status,
            "created_at": self.created_at,
            "evidence_hash": self.evidence_hash,
        }

    @classmethod
    def from_dict(cls, artifact: dict[str, Any]) -> "ContractAuthorizationResult":
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("authorization artifact must be a JSON object")
        required = {
            "authorization_id",
            "contract_id",
            "session_id",
            "requested_providers",
            "authorized_providers",
            "rejected_providers",
            "status",
            "created_at",
            "evidence_hash",
        }
        if set(artifact) != required:
            raise FailClosedRuntimeError("authorization artifact has malformed structure")
        return cls(
            authorization_id=artifact["authorization_id"],
            contract_id=artifact["contract_id"],
            session_id=artifact["session_id"],
            requested_providers=tuple(artifact["requested_providers"]),
            authorized_providers=tuple(artifact["authorized_providers"]),
            rejected_providers=tuple(artifact["rejected_providers"]),
            status=artifact["status"],
            created_at=artifact["created_at"],
            evidence_hash=artifact["evidence_hash"],
        )


def authorize_governed_execution_contract(
    *,
    authorization_id: str,
    contract: GovernedExecutionContract | dict[str, Any],
    session: GovernedExecutionSession,
    session_policy: dict[str, Any],
    created_at: str | None = None,
    prior_authorizations: tuple[ContractAuthorizationResult | dict[str, Any], ...] | list[ContractAuthorizationResult | dict[str, Any]] = (),
) -> ContractAuthorizationResult:
    """Authorize contract capabilities against explicit session policy only."""

    created = created_at or _utc_timestamp()
    try:
        _require_string(authorization_id, "authorization_id")
        if not isinstance(session, GovernedExecutionSession):
            raise FailClosedRuntimeError("session must be a GovernedExecutionSession")
        contract_obj = GovernedExecutionContract.from_dict(contract) if isinstance(contract, dict) else contract
        if not isinstance(contract_obj, GovernedExecutionContract):
            raise FailClosedRuntimeError("contract must be a GovernedExecutionContract")
        if session.status == CLOSED:
            return _authorization_result(authorization_id, contract_obj, session, (), _requested_providers(contract_obj), REJECTED, created)
        policy = _normalize_session_policy(session_policy)
        requested_providers = _requested_providers(contract_obj)
        if _duplicate_authorization_exists(contract_obj.contract_id, session.session_id, prior_authorizations):
            return _authorization_result(authorization_id, contract_obj, session, (), requested_providers, REJECTED, created)
        rejected = _rejected_providers(contract_obj, policy)
        authorized = tuple(provider for provider in requested_providers if provider not in rejected)
        status = AUTHORIZED if not rejected else REJECTED
        return _authorization_result(authorization_id, contract_obj, session, authorized, rejected, status, created)
    except (FailClosedRuntimeError, TypeError, ValueError, KeyError):
        return ContractAuthorizationResult(
            authorization_id=authorization_id if isinstance(authorization_id, str) and authorization_id else "AUTHORIZATION-INVALID",
            contract_id="",
            session_id=session.session_id if isinstance(session, GovernedExecutionSession) else "",
            requested_providers=(),
            authorized_providers=(),
            rejected_providers=(),
            status=REJECTED,
            created_at=created,
        )


def reconstruct_authorization_lineage(authorization: ContractAuthorizationResult | dict[str, Any]) -> dict[str, Any]:
    auth_obj = ContractAuthorizationResult.from_dict(authorization) if isinstance(authorization, dict) else authorization
    if not isinstance(auth_obj, ContractAuthorizationResult):
        raise FailClosedRuntimeError("authorization must be a ContractAuthorizationResult")
    artifact = auth_obj.to_dict()
    return {
        "authorization_id": artifact["authorization_id"],
        "contract_id": artifact["contract_id"],
        "session_id": artifact["session_id"],
        "status": artifact["status"],
        "requested_providers": artifact["requested_providers"],
        "authorized_providers": artifact["authorized_providers"],
        "rejected_providers": artifact["rejected_providers"],
        "authorization_evidence_hash": artifact["evidence_hash"],
        "lineage_hash": replay_hash(
            {
                "authorization_id": artifact["authorization_id"],
                "contract_id": artifact["contract_id"],
                "session_id": artifact["session_id"],
                "status": artifact["status"],
                "requested_providers": artifact["requested_providers"],
                "authorized_providers": artifact["authorized_providers"],
                "rejected_providers": artifact["rejected_providers"],
                "authorization_evidence_hash": artifact["evidence_hash"],
            }
        ),
    }


def _authorization_result(
    authorization_id: str,
    contract: GovernedExecutionContract,
    session: GovernedExecutionSession,
    authorized_providers: tuple[str, ...],
    rejected_providers: tuple[str, ...],
    status: str,
    created_at: str,
) -> ContractAuthorizationResult:
    return ContractAuthorizationResult(
        authorization_id=authorization_id,
        contract_id=contract.contract_id,
        session_id=session.session_id,
        requested_providers=_requested_providers(contract),
        authorized_providers=authorized_providers,
        rejected_providers=rejected_providers,
        status=status,
        created_at=created_at,
    )


def _requested_providers(contract: GovernedExecutionContract) -> tuple[str, ...]:
    providers = {_plain(operation)["provider"] for operation in contract.requested_operations}
    return tuple(sorted(providers))


def _normalize_session_policy(policy: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(policy, dict) or set(policy) != {"allowed_providers", "allowed_operations"}:
        raise FailClosedRuntimeError("session policy has malformed structure")
    allowed_providers = policy["allowed_providers"]
    allowed_operations = policy["allowed_operations"]
    if not isinstance(allowed_providers, list) or not isinstance(allowed_operations, dict):
        raise FailClosedRuntimeError("session policy has malformed structure")
    normalized_providers = tuple(sorted(allowed_providers))
    if len(set(normalized_providers)) != len(normalized_providers):
        raise FailClosedRuntimeError("session policy provider list contains duplicates")
    for provider in normalized_providers:
        if provider not in ALLOWED_PROVIDER_NAMES:
            raise FailClosedRuntimeError("session policy contains unknown provider")
    normalized_operations: dict[str, tuple[str, ...]] = {}
    for provider, operations in allowed_operations.items():
        if provider not in ALLOWED_PROVIDER_NAMES or provider not in normalized_providers:
            raise FailClosedRuntimeError("session policy operation provider is not authorized")
        if not isinstance(operations, list) or not operations:
            raise FailClosedRuntimeError("session policy operations must be non-empty lists")
        normalized_operation_list = tuple(sorted(operations))
        if len(set(normalized_operation_list)) != len(normalized_operation_list):
            raise FailClosedRuntimeError("session policy operation list contains duplicates")
        for operation in normalized_operation_list:
            if operation not in ALLOWED_PROVIDER_OPERATIONS[provider]:
                raise FailClosedRuntimeError("session policy contains unsupported operation")
        normalized_operations[provider] = normalized_operation_list
    canonical_serialize({"allowed_providers": normalized_providers, "allowed_operations": normalized_operations})
    return {
        "allowed_providers": normalized_providers,
        "allowed_operations": normalized_operations,
    }


def _rejected_providers(contract: GovernedExecutionContract, policy: dict[str, Any]) -> tuple[str, ...]:
    rejected: set[str] = set()
    allowed_providers = set(policy["allowed_providers"])
    allowed_operations = policy["allowed_operations"]
    for operation_proxy in contract.requested_operations:
        operation = _plain(operation_proxy)
        provider = operation["provider"]
        provider_operation = operation["operation"]
        if provider not in ALLOWED_PROVIDER_NAMES:
            rejected.add(provider)
            continue
        if provider not in allowed_providers:
            rejected.add(provider)
            continue
        if provider_operation not in allowed_operations.get(provider, ()):
            rejected.add(provider)
    return tuple(sorted(rejected))


def _duplicate_authorization_exists(
    contract_id: str,
    session_id: str,
    prior_authorizations: tuple[ContractAuthorizationResult | dict[str, Any], ...] | list[ContractAuthorizationResult | dict[str, Any]],
) -> bool:
    for prior in prior_authorizations:
        prior_obj = ContractAuthorizationResult.from_dict(prior) if isinstance(prior, dict) else prior
        if not isinstance(prior_obj, ContractAuthorizationResult):
            raise FailClosedRuntimeError("prior authorization artifact is invalid")
        if prior_obj.contract_id == contract_id and prior_obj.session_id == session_id:
            return True
    return False
