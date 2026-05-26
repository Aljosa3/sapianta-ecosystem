"""Minimal deterministic router for authorized governed execution contracts."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from aigol.runtime.governed_contract_authorization_gate import (
    AUTHORIZED,
    ContractAuthorizationResult,
)
from aigol.runtime.governed_execution_contract import ATTACHED, VALIDATED, GovernedExecutionContract
from aigol.runtime.governed_execution_session import CLOSED, FAILED, GovernedExecutionSession
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


ROUTED = "ROUTED"
REJECTED = "REJECTED"
ALLOWED_ROUTING_STATUSES = frozenset({ROUTED, REJECTED})


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _routing_hash_input(result: "ContractRoutingResult") -> dict[str, Any]:
    return {
        "routing_id": result.routing_id,
        "contract_id": result.contract_id,
        "session_id": result.session_id,
        "authorization_id": result.authorization_id,
        "status": result.status,
        "reason": result.reason,
        "attached": result.attached,
        "created_at": result.created_at,
    }


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


@dataclass(frozen=True)
class ContractRoutingResult:
    """Replay-visible routing evidence without execution authority."""

    routing_id: str
    contract_id: str
    session_id: str
    authorization_id: str
    status: str
    reason: str
    attached: bool
    created_at: str
    evidence_hash: str = ""

    def __post_init__(self) -> None:
        _require_string(self.routing_id, "routing_id")
        _require_string(self.created_at, "created_at")
        if self.status not in ALLOWED_ROUTING_STATUSES:
            raise FailClosedRuntimeError("routing status must be ROUTED or REJECTED")
        if not isinstance(self.attached, bool):
            raise FailClosedRuntimeError("attached must be boolean")
        expected_hash = replay_hash(_routing_hash_input(self))
        if self.evidence_hash and self.evidence_hash != expected_hash:
            raise FailClosedRuntimeError("routing evidence hash mismatch")
        object.__setattr__(self, "evidence_hash", self.evidence_hash or expected_hash)

    def to_dict(self) -> dict[str, Any]:
        return {
            "routing_id": self.routing_id,
            "contract_id": self.contract_id,
            "session_id": self.session_id,
            "authorization_id": self.authorization_id,
            "status": self.status,
            "reason": self.reason,
            "attached": self.attached,
            "evidence_hash": self.evidence_hash,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, artifact: dict[str, Any]) -> "ContractRoutingResult":
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("routing artifact must be a JSON object")
        required = {"routing_id", "contract_id", "session_id", "authorization_id", "status", "reason", "attached", "evidence_hash", "created_at"}
        if set(artifact) != required:
            raise FailClosedRuntimeError("routing artifact has malformed structure")
        return cls(
            routing_id=artifact["routing_id"],
            contract_id=artifact["contract_id"],
            session_id=artifact["session_id"],
            authorization_id=artifact["authorization_id"],
            status=artifact["status"],
            reason=artifact["reason"],
            attached=artifact["attached"],
            created_at=artifact["created_at"],
            evidence_hash=artifact["evidence_hash"],
        )


def route_authorized_contract(
    *,
    routing_id: str,
    contract: GovernedExecutionContract | dict[str, Any],
    authorization: ContractAuthorizationResult | dict[str, Any] | None,
    session: GovernedExecutionSession,
    created_at: str | None = None,
    prior_routes: tuple[ContractRoutingResult | dict[str, Any], ...] | list[ContractRoutingResult | dict[str, Any]] = (),
) -> dict[str, Any]:
    """Route an authorized contract into session lineage evidence only."""

    created = created_at or _utc_timestamp()
    try:
        _require_string(routing_id, "routing_id")
        if authorization is None:
            return _rejected(routing_id, "", "", "", "authorization evidence is required", created)
        if not isinstance(session, GovernedExecutionSession):
            raise FailClosedRuntimeError("session must be a GovernedExecutionSession")
        contract_obj = GovernedExecutionContract.from_dict(contract) if isinstance(contract, dict) else contract
        auth_obj = ContractAuthorizationResult.from_dict(authorization) if isinstance(authorization, dict) else authorization
        if not isinstance(contract_obj, GovernedExecutionContract):
            raise FailClosedRuntimeError("contract must be a GovernedExecutionContract")
        if not isinstance(auth_obj, ContractAuthorizationResult):
            raise FailClosedRuntimeError("authorization must be a ContractAuthorizationResult")
        reason = _routing_rejection_reason(contract_obj, auth_obj, session, prior_routes)
        if reason:
            return {
                "routing_result": _rejected(
                    routing_id,
                    contract_obj.contract_id,
                    session.session_id,
                    auth_obj.authorization_id,
                    reason,
                    created,
                ),
                "attached_contract": None,
                "attachment_evidence": None,
            }
        attachment = contract_obj.attach_to_session(session=session, attached_at=created)
        return {
            "routing_result": ContractRoutingResult(
                routing_id=routing_id,
                contract_id=contract_obj.contract_id,
                session_id=session.session_id,
                authorization_id=auth_obj.authorization_id,
                status=ROUTED,
                reason="authorized contract routed to governed session lineage",
                attached=True,
                created_at=created,
            ),
            "attached_contract": attachment["contract"],
            "attachment_evidence": attachment["attachment_evidence"],
        }
    except (FailClosedRuntimeError, TypeError, ValueError, KeyError):
        return {
            "routing_result": _rejected(
                routing_id if isinstance(routing_id, str) and routing_id else "ROUTING-INVALID",
                "",
                session.session_id if isinstance(session, GovernedExecutionSession) else "",
                "",
                "routing validation failed closed",
                created,
            ),
            "attached_contract": None,
            "attachment_evidence": None,
        }


def _routing_rejection_reason(
    contract: GovernedExecutionContract,
    authorization: ContractAuthorizationResult,
    session: GovernedExecutionSession,
    prior_routes: tuple[ContractRoutingResult | dict[str, Any], ...] | list[ContractRoutingResult | dict[str, Any]],
) -> str:
    if contract.status not in {VALIDATED, ATTACHED}:
        return "contract is not VALIDATED or ATTACHED-ready"
    if contract.status == ATTACHED:
        return "contract is already ATTACHED"
    if authorization.status != AUTHORIZED:
        return "authorization status is not AUTHORIZED"
    if authorization.contract_id != contract.contract_id:
        return "authorization contract_id does not match contract_id"
    if authorization.session_id != session.session_id:
        return "authorization session_id does not match session_id"
    if session.status in {CLOSED, FAILED}:
        return "session is CLOSED or FAILED"
    if _duplicate_route_exists(contract.contract_id, session.session_id, prior_routes):
        return "duplicate routing detected"
    requested_providers = tuple(sorted({operation["provider"] for operation in contract.to_dict()["requested_operations"]}))
    if requested_providers != authorization.requested_providers:
        return "requested providers differ from authorization requested providers"
    if requested_providers != authorization.authorized_providers:
        return "requested providers differ from authorized providers"
    return ""


def _duplicate_route_exists(
    contract_id: str,
    session_id: str,
    prior_routes: tuple[ContractRoutingResult | dict[str, Any], ...] | list[ContractRoutingResult | dict[str, Any]],
) -> bool:
    for prior in prior_routes:
        prior_obj = ContractRoutingResult.from_dict(prior) if isinstance(prior, dict) else prior
        if not isinstance(prior_obj, ContractRoutingResult):
            raise FailClosedRuntimeError("prior routing artifact is invalid")
        if prior_obj.contract_id == contract_id and prior_obj.session_id == session_id and prior_obj.status == ROUTED:
            return True
    return False


def _rejected(
    routing_id: str,
    contract_id: str,
    session_id: str,
    authorization_id: str,
    reason: str,
    created_at: str,
) -> ContractRoutingResult:
    return ContractRoutingResult(
        routing_id=routing_id,
        contract_id=contract_id,
        session_id=session_id,
        authorization_id=authorization_id,
        status=REJECTED,
        reason=reason,
        attached=False,
        created_at=created_at,
    )


def reconstruct_routing_lineage(routing: ContractRoutingResult | dict[str, Any]) -> dict[str, Any]:
    routing_obj = ContractRoutingResult.from_dict(routing) if isinstance(routing, dict) else routing
    if not isinstance(routing_obj, ContractRoutingResult):
        raise FailClosedRuntimeError("routing must be a ContractRoutingResult")
    artifact = routing_obj.to_dict()
    return {
        "routing_id": artifact["routing_id"],
        "contract_id": artifact["contract_id"],
        "session_id": artifact["session_id"],
        "authorization_id": artifact["authorization_id"],
        "status": artifact["status"],
        "attached": artifact["attached"],
        "routing_evidence_hash": artifact["evidence_hash"],
        "lineage_hash": replay_hash(
            {
                "routing_id": artifact["routing_id"],
                "contract_id": artifact["contract_id"],
                "session_id": artifact["session_id"],
                "authorization_id": artifact["authorization_id"],
                "status": artifact["status"],
                "attached": artifact["attached"],
                "routing_evidence_hash": artifact["evidence_hash"],
            }
        ),
    }
