"""Single-operation governed execution path for readonly metadata inspection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aigol.runtime.governed_cognition_review_gate import REVIEWED, review_translated_cognition_candidate
from aigol.runtime.governed_contract_authorization_gate import AUTHORIZED, authorize_governed_execution_contract
from aigol.runtime.governed_contract_router import ROUTED, route_authorized_contract
from aigol.runtime.governed_execution_contract import create_governed_execution_contract
from aigol.runtime.governed_execution_session import GovernedExecutionSession, create_governed_execution_session, reconstruct_session_lineage
from aigol.runtime.governed_proposal_translation_layer import TRANSLATED, translate_bounded_proposal
from aigol.runtime.minimal_real_llm_proposal_flow import normalize_real_llm_proposal_input
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.providers.metadata_inspection_provider import MetadataInspectionProvider
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


EXECUTED = "EXECUTED"
REJECTED = "REJECTED"
ALLOWED_EXECUTION_STATUSES = frozenset({EXECUTED, REJECTED})

ALLOWED_PROVIDER = "metadata_inspection_provider"
ALLOWED_OPERATION = "inspect_runtime"


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _execution_hash_input(result: "MinimalGovernedExecutionPathResult") -> dict[str, Any]:
    return {
        "execution_id": result.execution_id,
        "proposal_id": result.proposal_id,
        "translation_id": result.translation_id,
        "review_id": result.review_id,
        "contract_id": result.contract_id,
        "authorization_id": result.authorization_id,
        "routing_id": result.routing_id,
        "session_id": result.session_id,
        "execution_status": result.execution_status,
        "execution_reason": result.execution_reason,
        "provider": result.provider,
        "provider_operation": result.provider_operation,
        "provider_evidence_hash": result.provider_evidence_hash,
        "session_lineage_hash": result.session_lineage_hash,
        "governance_authority_separated": result.governance_authority_separated,
        "created_at": result.created_at,
    }


@dataclass(frozen=True)
class MinimalGovernedExecutionPathResult:
    """Replay-visible evidence for one bounded governed provider invocation."""

    execution_id: str
    proposal_id: str
    translation_id: str
    review_id: str
    contract_id: str
    authorization_id: str
    routing_id: str
    session_id: str
    execution_status: str
    execution_reason: str
    provider: str
    provider_operation: str
    provider_evidence_hash: str
    session_lineage_hash: str
    governance_authority_separated: bool
    created_at: str
    evidence_hash: str = ""

    def __post_init__(self) -> None:
        _require_string(self.execution_id, "execution_id")
        _require_string(self.proposal_id, "proposal_id")
        _require_string(self.execution_reason, "execution_reason")
        _require_string(self.created_at, "created_at")
        if self.execution_status not in ALLOWED_EXECUTION_STATUSES:
            raise FailClosedRuntimeError("execution status must be EXECUTED or REJECTED")
        if not isinstance(self.governance_authority_separated, bool):
            raise FailClosedRuntimeError("governance_authority_separated must be boolean")
        expected_hash = replay_hash(_execution_hash_input(self))
        if self.evidence_hash and self.evidence_hash != expected_hash:
            raise FailClosedRuntimeError("minimal governed execution path evidence hash mismatch")
        object.__setattr__(self, "evidence_hash", self.evidence_hash or expected_hash)

    def to_dict(self) -> dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "proposal_id": self.proposal_id,
            "translation_id": self.translation_id,
            "review_id": self.review_id,
            "contract_id": self.contract_id,
            "authorization_id": self.authorization_id,
            "routing_id": self.routing_id,
            "session_id": self.session_id,
            "execution_status": self.execution_status,
            "execution_reason": self.execution_reason,
            "provider": self.provider,
            "provider_operation": self.provider_operation,
            "provider_evidence_hash": self.provider_evidence_hash,
            "session_lineage_hash": self.session_lineage_hash,
            "governance_authority_separated": self.governance_authority_separated,
            "created_at": self.created_at,
            "evidence_hash": self.evidence_hash,
        }

    @classmethod
    def from_dict(cls, artifact: dict[str, Any]) -> "MinimalGovernedExecutionPathResult":
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("minimal governed execution path artifact must be a JSON object")
        required = {
            "execution_id",
            "proposal_id",
            "translation_id",
            "review_id",
            "contract_id",
            "authorization_id",
            "routing_id",
            "session_id",
            "execution_status",
            "execution_reason",
            "provider",
            "provider_operation",
            "provider_evidence_hash",
            "session_lineage_hash",
            "governance_authority_separated",
            "created_at",
            "evidence_hash",
        }
        if set(artifact) != required:
            raise FailClosedRuntimeError("minimal governed execution path artifact has malformed structure")
        return cls(**artifact)


def execute_minimal_governed_path(
    *,
    execution_id: str,
    llm_proposal_input: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    """Run one governed readonly metadata inspection through all governance gates."""

    try:
        _require_string(execution_id, "execution_id")
        _require_string(created_at, "created_at")
        proposal = normalize_real_llm_proposal_input(llm_proposal_input)
        _validate_single_runtime_capability(proposal)
        translation = translate_bounded_proposal(
            translation_id=f"{execution_id}:TRANSLATION",
            proposal=proposal,
            created_at=created_at,
        )
        if translation.translation_status != TRANSLATED:
            return _rejected(execution_id, proposal.proposal_id, translation.translation_id, "", "", "", "", "", "translation rejected", created_at)
        review = review_translated_cognition_candidate(
            review_id=f"{execution_id}:REVIEW",
            translation=translation,
            created_at=created_at,
        )
        if review.review_status != REVIEWED:
            return _rejected(
                execution_id,
                proposal.proposal_id,
                translation.translation_id,
                review.review_id,
                "",
                "",
                "",
                "",
                "cognition review rejected",
                created_at,
            )
        session = create_governed_execution_session(session_id=f"{execution_id}:SESSION", created_at=created_at)
        contract = create_governed_execution_contract(
            contract_id=_contract_id_from_reference(proposal.proposed_contract_reference),
            created_at=created_at,
            requested_operations=[
                {
                    "provider": ALLOWED_PROVIDER,
                    "operation": ALLOWED_OPERATION,
                    "operation_id": f"{execution_id}:OP:001",
                    "created_at": created_at,
                }
            ],
            allowed_providers=[ALLOWED_PROVIDER],
        ).validate_contract()
        authorization = authorize_governed_execution_contract(
            authorization_id=f"{execution_id}:AUTHORIZATION",
            contract=contract,
            session=session,
            session_policy={
                "allowed_providers": [ALLOWED_PROVIDER],
                "allowed_operations": {ALLOWED_PROVIDER: [ALLOWED_OPERATION]},
            },
            created_at=created_at,
        )
        if authorization.status != AUTHORIZED:
            return _rejected(
                execution_id,
                proposal.proposal_id,
                translation.translation_id,
                review.review_id,
                contract.contract_id,
                authorization.authorization_id,
                "",
                session.session_id,
                "authorization rejected",
                created_at,
            )
        routing = route_authorized_contract(
            routing_id=f"{execution_id}:ROUTING",
            contract=contract,
            authorization=authorization,
            session=session,
            created_at=created_at,
        )
        routing_result = routing["routing_result"]
        if routing_result.status != ROUTED:
            return _rejected(
                execution_id,
                proposal.proposal_id,
                translation.translation_id,
                review.review_id,
                contract.contract_id,
                authorization.authorization_id,
                routing_result.routing_id,
                session.session_id,
                "routing rejected",
                created_at,
            )
        provider = MetadataInspectionProvider(timestamp_provider=lambda: created_at)
        provider_evidence = provider.inspect_runtime()
        session_with_execution = session.attach_provider_evidence(
            provider=ALLOWED_PROVIDER,
            provider_operation=ALLOWED_OPERATION,
            evidence=provider_evidence,
            attached_at=created_at,
        )
        lineage = reconstruct_session_lineage(session_with_execution)
        result = MinimalGovernedExecutionPathResult(
            execution_id=execution_id,
            proposal_id=proposal.proposal_id,
            translation_id=translation.translation_id,
            review_id=review.review_id,
            contract_id=contract.contract_id,
            authorization_id=authorization.authorization_id,
            routing_id=routing_result.routing_id,
            session_id=session.session_id,
            execution_status=EXECUTED,
            execution_reason="bounded readonly metadata inspect_runtime executed through governed path",
            provider=ALLOWED_PROVIDER,
            provider_operation=ALLOWED_OPERATION,
            provider_evidence_hash=provider_evidence["evidence_hash"],
            session_lineage_hash=replay_hash(lineage),
            governance_authority_separated=True,
            created_at=created_at,
        )
        return {
            "execution_result": result,
            "proposal": proposal,
            "translation": translation,
            "review": review,
            "contract": contract,
            "authorization": authorization,
            "routing": routing_result,
            "provider_evidence": provider_evidence,
            "session": session_with_execution,
            "session_lineage": lineage,
        }
    except (FailClosedRuntimeError, TypeError, ValueError, KeyError):
        proposal_id = ""
        if isinstance(llm_proposal_input, dict) and isinstance(llm_proposal_input.get("proposal_id"), str):
            proposal_id = llm_proposal_input["proposal_id"]
        return {
            "execution_result": _rejected(
                execution_id if isinstance(execution_id, str) and execution_id else "EXECUTION-INVALID",
                proposal_id or "PROPOSAL-INVALID",
                "",
                "",
                "",
                "",
                "",
                "",
                "minimal governed execution path failed closed",
                created_at if isinstance(created_at, str) and created_at else "1970-01-01T00:00:00+00:00",
            ),
            "proposal": None,
            "translation": None,
            "review": None,
            "contract": None,
            "authorization": None,
            "routing": None,
            "provider_evidence": None,
            "session": None,
            "session_lineage": None,
        }


def reconstruct_minimal_governed_execution_lineage(
    executions: list[MinimalGovernedExecutionPathResult | dict[str, Any]],
) -> dict[str, Any]:
    if not isinstance(executions, list):
        raise FailClosedRuntimeError("minimal governed execution lineage must be a list")
    reconstructed = []
    seen_execution_ids: set[str] = set()
    previous_created_at = ""
    for index, execution in enumerate(executions):
        execution_obj = MinimalGovernedExecutionPathResult.from_dict(execution) if isinstance(execution, dict) else execution
        if not isinstance(execution_obj, MinimalGovernedExecutionPathResult):
            raise FailClosedRuntimeError("minimal governed execution lineage entry is invalid")
        artifact = execution_obj.to_dict()
        if artifact["execution_id"] in seen_execution_ids:
            raise FailClosedRuntimeError("minimal governed execution lineage contains duplicate execution_id")
        if previous_created_at and artifact["created_at"] < previous_created_at:
            raise FailClosedRuntimeError("minimal governed execution lineage ordering is not deterministic")
        canonical_serialize(artifact)
        seen_execution_ids.add(artifact["execution_id"])
        previous_created_at = artifact["created_at"]
        reconstructed.append(
            {
                "execution_index": index,
                "execution_id": artifact["execution_id"],
                "execution_status": artifact["execution_status"],
                "provider": artifact["provider"],
                "provider_operation": artifact["provider_operation"],
                "evidence_hash": artifact["evidence_hash"],
            }
        )
    lineage = {
        "execution_count": len(reconstructed),
        "executions": reconstructed,
        "append_only_valid": True,
        "lineage_valid": True,
        "governance_authority_separated": True,
    }
    lineage["lineage_hash"] = replay_hash(lineage)
    return lineage


def _validate_single_runtime_capability(proposal: Any) -> None:
    if tuple(proposal.requested_capabilities) != (ALLOWED_PROVIDER,):
        raise FailClosedRuntimeError("minimal governed execution path only allows metadata inspection capability")


def _contract_id_from_reference(reference: str) -> str:
    if not isinstance(reference, str) or not reference.startswith("contract:"):
        raise FailClosedRuntimeError("proposal contract reference is invalid")
    contract_id = reference.removeprefix("contract:")
    return _require_string(contract_id, "contract_id")


def _rejected(
    execution_id: str,
    proposal_id: str,
    translation_id: str,
    review_id: str,
    contract_id: str,
    authorization_id: str,
    routing_id: str,
    session_id: str,
    reason: str,
    created_at: str,
) -> MinimalGovernedExecutionPathResult:
    return MinimalGovernedExecutionPathResult(
        execution_id=execution_id,
        proposal_id=proposal_id,
        translation_id=translation_id,
        review_id=review_id,
        contract_id=contract_id,
        authorization_id=authorization_id,
        routing_id=routing_id,
        session_id=session_id,
        execution_status=REJECTED,
        execution_reason=reason,
        provider="",
        provider_operation="",
        provider_evidence_hash="",
        session_lineage_hash="",
        governance_authority_separated=True,
        created_at=created_at,
    )
