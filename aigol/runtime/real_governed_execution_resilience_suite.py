"""Deterministic resilience checks for the governed execution path."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from aigol.runtime.governed_execution_session import reconstruct_session_lineage
from aigol.runtime.minimal_governed_execution_path import (
    EXECUTED,
    REJECTED,
    MinimalGovernedExecutionPathResult,
    execute_minimal_governed_path,
    reconstruct_minimal_governed_execution_lineage,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


PASSED = "PASSED"
FAILED = "FAILED"

MALFORMED_PROPOSAL_LINEAGE = "MALFORMED_PROPOSAL_LINEAGE"
UNAUTHORIZED_CAPABILITY_ESCALATION = "UNAUTHORIZED_CAPABILITY_ESCALATION"
REPLAY_CORRUPTION_ATTEMPT = "REPLAY_CORRUPTION_ATTEMPT"
ROUTING_MISMATCH_ATTEMPT = "ROUTING_MISMATCH_ATTEMPT"
PROVIDER_BOUNDARY_VIOLATION = "PROVIDER_BOUNDARY_VIOLATION"
DUPLICATE_EXECUTION_ATTEMPT = "DUPLICATE_EXECUTION_ATTEMPT"
INVALID_SESSION_LINEAGE_CONTINUATION = "INVALID_SESSION_LINEAGE_CONTINUATION"

ALLOWED_RESILIENCE_STATUSES = frozenset({PASSED, FAILED})
ALLOWED_PRESSURE_TYPES = frozenset(
    {
        MALFORMED_PROPOSAL_LINEAGE,
        UNAUTHORIZED_CAPABILITY_ESCALATION,
        REPLAY_CORRUPTION_ATTEMPT,
        ROUTING_MISMATCH_ATTEMPT,
        PROVIDER_BOUNDARY_VIOLATION,
        DUPLICATE_EXECUTION_ATTEMPT,
        INVALID_SESSION_LINEAGE_CONTINUATION,
    }
)


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _evidence_hash_input(evidence: "RealGovernedExecutionResilienceEvidence") -> dict[str, Any]:
    return {
        "resilience_id": evidence.resilience_id,
        "pressure_type": evidence.pressure_type,
        "status": evidence.status,
        "expected_result": evidence.expected_result,
        "observed_result": evidence.observed_result,
        "execution_evidence_hash": evidence.execution_evidence_hash,
        "reason": evidence.reason,
        "created_at": evidence.created_at,
    }


@dataclass(frozen=True)
class RealGovernedExecutionResilienceEvidence:
    """Immutable replay-visible resilience validation evidence."""

    resilience_id: str
    pressure_type: str
    status: str
    expected_result: str
    observed_result: str
    execution_evidence_hash: str
    reason: str
    created_at: str
    evidence_hash: str = ""

    def __post_init__(self) -> None:
        _require_string(self.resilience_id, "resilience_id")
        _require_string(self.reason, "reason")
        _require_string(self.created_at, "created_at")
        if self.pressure_type not in ALLOWED_PRESSURE_TYPES:
            raise FailClosedRuntimeError("unknown resilience pressure type")
        if self.status not in ALLOWED_RESILIENCE_STATUSES:
            raise FailClosedRuntimeError("resilience status must be PASSED or FAILED")
        expected_hash = replay_hash(_evidence_hash_input(self))
        if self.evidence_hash and self.evidence_hash != expected_hash:
            raise FailClosedRuntimeError("real governed execution resilience evidence hash mismatch")
        object.__setattr__(self, "evidence_hash", self.evidence_hash or expected_hash)

    def to_dict(self) -> dict[str, Any]:
        return {
            "resilience_id": self.resilience_id,
            "pressure_type": self.pressure_type,
            "status": self.status,
            "expected_result": self.expected_result,
            "observed_result": self.observed_result,
            "execution_evidence_hash": self.execution_evidence_hash,
            "reason": self.reason,
            "created_at": self.created_at,
            "evidence_hash": self.evidence_hash,
        }

    @classmethod
    def from_dict(cls, artifact: dict[str, Any]) -> "RealGovernedExecutionResilienceEvidence":
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("real governed execution resilience artifact must be a JSON object")
        required = {
            "resilience_id",
            "pressure_type",
            "status",
            "expected_result",
            "observed_result",
            "execution_evidence_hash",
            "reason",
            "created_at",
            "evidence_hash",
        }
        if set(artifact) != required:
            raise FailClosedRuntimeError("real governed execution resilience artifact has malformed structure")
        return cls(**artifact)


def run_real_governed_execution_resilience_suite(
    *,
    suite_id: str,
    created_at: str,
) -> dict[str, Any]:
    """Validate deterministic fail-closed behavior for the operational path."""

    _require_string(suite_id, "suite_id")
    _require_string(created_at, "created_at")
    scenarios: list[Callable[[str, str], RealGovernedExecutionResilienceEvidence]] = [
        _malformed_proposal_lineage,
        _unauthorized_capability_escalation,
        _replay_corruption_attempt,
        _routing_mismatch_attempt,
        _provider_boundary_violation,
        _duplicate_execution_attempt,
        _invalid_session_lineage_continuation,
    ]
    evidence = [scenario(suite_id, created_at) for scenario in scenarios]
    lineage = reconstruct_real_governed_execution_resilience_lineage(evidence)
    suite_result = {
        "suite_id": suite_id,
        "created_at": created_at,
        "status": PASSED if all(item.status == PASSED for item in evidence) else FAILED,
        "pressure_count": len(evidence),
        "resilience_evidence_hashes": [item.evidence_hash for item in evidence],
        "lineage_hash": lineage["lineage_hash"],
        "governance_authority_separated": True,
    }
    suite_result["evidence_hash"] = replay_hash(suite_result)
    return {
        "suite_result": suite_result,
        "resilience_evidence": tuple(evidence),
        "resilience_lineage": lineage,
    }


def reconstruct_real_governed_execution_resilience_lineage(
    evidence: list[RealGovernedExecutionResilienceEvidence | dict[str, Any]]
    | tuple[RealGovernedExecutionResilienceEvidence | dict[str, Any], ...],
) -> dict[str, Any]:
    if not isinstance(evidence, list | tuple):
        raise FailClosedRuntimeError("real governed execution resilience lineage must be a list")
    reconstructed = []
    seen_resilience_ids: set[str] = set()
    previous_created_at = ""
    for index, item in enumerate(evidence):
        evidence_obj = RealGovernedExecutionResilienceEvidence.from_dict(item) if isinstance(item, dict) else item
        if not isinstance(evidence_obj, RealGovernedExecutionResilienceEvidence):
            raise FailClosedRuntimeError("real governed execution resilience lineage entry is invalid")
        artifact = evidence_obj.to_dict()
        if artifact["resilience_id"] in seen_resilience_ids:
            raise FailClosedRuntimeError("real governed execution resilience lineage contains duplicate resilience_id")
        if previous_created_at and artifact["created_at"] < previous_created_at:
            raise FailClosedRuntimeError("real governed execution resilience lineage ordering is not deterministic")
        canonical_serialize(artifact)
        seen_resilience_ids.add(artifact["resilience_id"])
        previous_created_at = artifact["created_at"]
        reconstructed.append(
            {
                "resilience_index": index,
                "resilience_id": artifact["resilience_id"],
                "pressure_type": artifact["pressure_type"],
                "status": artifact["status"],
                "evidence_hash": artifact["evidence_hash"],
            }
        )
    lineage = {
        "resilience_count": len(reconstructed),
        "resilience_checks": reconstructed,
        "append_only_valid": True,
        "lineage_valid": True,
        "governance_authority_separated": True,
    }
    lineage["lineage_hash"] = replay_hash(lineage)
    return lineage


def _base_llm_input(*, proposal_id: str, contract_id: str, created_at: str) -> dict[str, Any]:
    return {
        "proposal_id": proposal_id,
        "natural_language_input": "Propose bounded runtime metadata inspection.",
        "proposal_type": "CONTRACT_PROPOSAL",
        "requested_capabilities": ["metadata_inspection_provider"],
        "proposed_contract_reference": f"contract:{contract_id}",
        "created_at": created_at,
    }


def _execute_valid(execution_id: str, created_at: str) -> dict[str, Any]:
    return execute_minimal_governed_path(
        execution_id=execution_id,
        llm_proposal_input=_base_llm_input(
            proposal_id=f"{execution_id}:PROPOSAL",
            contract_id=f"{execution_id}:CONTRACT",
            created_at=created_at,
        ),
        created_at=created_at,
    )


def _pressure_evidence(
    *,
    suite_id: str,
    pressure_type: str,
    index: int,
    passed: bool,
    expected_result: str,
    observed_result: str,
    execution_evidence_hash: str,
    reason: str,
    created_at: str,
) -> RealGovernedExecutionResilienceEvidence:
    return RealGovernedExecutionResilienceEvidence(
        resilience_id=f"{suite_id}:{index:03d}:{pressure_type}",
        pressure_type=pressure_type,
        status=PASSED if passed else FAILED,
        expected_result=expected_result,
        observed_result=observed_result,
        execution_evidence_hash=execution_evidence_hash,
        reason=reason,
        created_at=f"{created_at}:{index:03d}",
    )


def _malformed_proposal_lineage(suite_id: str, created_at: str) -> RealGovernedExecutionResilienceEvidence:
    proposal = _base_llm_input(proposal_id=f"{suite_id}:MALFORMED", contract_id=f"{suite_id}:MALFORMED-CONTRACT", created_at=created_at)
    proposal.pop("natural_language_input")
    result = execute_minimal_governed_path(execution_id=f"{suite_id}:MALFORMED", llm_proposal_input=proposal, created_at=created_at)
    execution = result["execution_result"]
    return _pressure_evidence(
        suite_id=suite_id,
        pressure_type=MALFORMED_PROPOSAL_LINEAGE,
        index=1,
        passed=execution.execution_status == REJECTED and result["provider_evidence"] is None,
        expected_result=REJECTED,
        observed_result=execution.execution_status,
        execution_evidence_hash=execution.evidence_hash,
        reason="malformed cognition proposal rejected without provider execution",
        created_at=created_at,
    )


def _unauthorized_capability_escalation(suite_id: str, created_at: str) -> RealGovernedExecutionResilienceEvidence:
    proposal = _base_llm_input(proposal_id=f"{suite_id}:ESCALATION", contract_id=f"{suite_id}:ESCALATION-CONTRACT", created_at=created_at)
    proposal["requested_capabilities"] = ["readonly_http_get_provider"]
    result = execute_minimal_governed_path(execution_id=f"{suite_id}:ESCALATION", llm_proposal_input=proposal, created_at=created_at)
    execution = result["execution_result"]
    return _pressure_evidence(
        suite_id=suite_id,
        pressure_type=UNAUTHORIZED_CAPABILITY_ESCALATION,
        index=2,
        passed=execution.execution_status == REJECTED and result["provider_evidence"] is None,
        expected_result=REJECTED,
        observed_result=execution.execution_status,
        execution_evidence_hash=execution.evidence_hash,
        reason="unauthorized capability request rejected before provider execution",
        created_at=created_at,
    )


def _replay_corruption_attempt(suite_id: str, created_at: str) -> RealGovernedExecutionResilienceEvidence:
    result = _execute_valid(f"{suite_id}:REPLAY", created_at)
    artifact = result["execution_result"].to_dict()
    artifact["execution_status"] = REJECTED
    rejected = False
    try:
        MinimalGovernedExecutionPathResult.from_dict(artifact)
    except FailClosedRuntimeError:
        rejected = True
    return _pressure_evidence(
        suite_id=suite_id,
        pressure_type=REPLAY_CORRUPTION_ATTEMPT,
        index=3,
        passed=rejected,
        expected_result=REJECTED,
        observed_result=REJECTED if rejected else EXECUTED,
        execution_evidence_hash=result["execution_result"].evidence_hash,
        reason="mutated execution evidence rejected by replay hash validation",
        created_at=created_at,
    )


def _routing_mismatch_attempt(suite_id: str, created_at: str) -> RealGovernedExecutionResilienceEvidence:
    result = _execute_valid(f"{suite_id}:ROUTING", created_at)
    artifact = result["execution_result"].to_dict()
    artifact["routing_id"] = "MISMATCHED-ROUTING"
    rejected = False
    try:
        MinimalGovernedExecutionPathResult.from_dict(artifact)
    except FailClosedRuntimeError:
        rejected = True
    return _pressure_evidence(
        suite_id=suite_id,
        pressure_type=ROUTING_MISMATCH_ATTEMPT,
        index=4,
        passed=rejected,
        expected_result=REJECTED,
        observed_result=REJECTED if rejected else EXECUTED,
        execution_evidence_hash=result["execution_result"].evidence_hash,
        reason="routing mismatch rejected by execution evidence continuity",
        created_at=created_at,
    )


def _provider_boundary_violation(suite_id: str, created_at: str) -> RealGovernedExecutionResilienceEvidence:
    proposal = _base_llm_input(proposal_id=f"{suite_id}:PROVIDER", contract_id=f"{suite_id}:PROVIDER-CONTRACT", created_at=created_at)
    proposal["requested_capabilities"] = ["readonly_filesystem_provider"]
    result = execute_minimal_governed_path(execution_id=f"{suite_id}:PROVIDER", llm_proposal_input=proposal, created_at=created_at)
    execution = result["execution_result"]
    return _pressure_evidence(
        suite_id=suite_id,
        pressure_type=PROVIDER_BOUNDARY_VIOLATION,
        index=5,
        passed=execution.execution_status == REJECTED and result["provider_evidence"] is None,
        expected_result=REJECTED,
        observed_result=execution.execution_status,
        execution_evidence_hash=execution.evidence_hash,
        reason="provider boundary violation rejected before provider execution",
        created_at=created_at,
    )


def _duplicate_execution_attempt(suite_id: str, created_at: str) -> RealGovernedExecutionResilienceEvidence:
    first = _execute_valid(f"{suite_id}:DUPLICATE", created_at)["execution_result"]
    duplicate = _execute_valid(f"{suite_id}:DUPLICATE", f"{created_at}:DUP")["execution_result"]
    rejected = False
    try:
        reconstruct_minimal_governed_execution_lineage([first, duplicate])
    except FailClosedRuntimeError:
        rejected = True
    return _pressure_evidence(
        suite_id=suite_id,
        pressure_type=DUPLICATE_EXECUTION_ATTEMPT,
        index=6,
        passed=rejected,
        expected_result=REJECTED,
        observed_result=REJECTED if rejected else EXECUTED,
        execution_evidence_hash=first.evidence_hash,
        reason="duplicate execution lineage rejected by append-only validation",
        created_at=created_at,
    )


def _invalid_session_lineage_continuation(suite_id: str, created_at: str) -> RealGovernedExecutionResilienceEvidence:
    result = _execute_valid(f"{suite_id}:SESSION", created_at)
    session = result["session"].close_session(closed_at=f"{created_at}:CLOSED")
    rejected = False
    try:
        session.attach_provider_evidence(
            provider="metadata_inspection_provider",
            provider_operation="inspect_runtime",
            evidence=result["provider_evidence"],
            attached_at=f"{created_at}:AFTER-CLOSE",
        )
    except FailClosedRuntimeError:
        rejected = True
    try:
        reconstruct_session_lineage(session)
    except FailClosedRuntimeError:
        rejected = False
    return _pressure_evidence(
        suite_id=suite_id,
        pressure_type=INVALID_SESSION_LINEAGE_CONTINUATION,
        index=7,
        passed=rejected,
        expected_result=REJECTED,
        observed_result=REJECTED if rejected else EXECUTED,
        execution_evidence_hash=result["execution_result"].evidence_hash,
        reason="session continuation after closure rejected by session lifecycle",
        created_at=created_at,
    )
