"""Live operational usage validation for the governed cognition runtime."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aigol.runtime.governed_return_interpretation import ACCEPTED, interpret_governed_execution_return
from aigol.runtime.minimal_governed_execution_path import EXECUTED, execute_minimal_governed_path
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.production_isolation_foundation import ISOLATED, validate_production_isolation
from aigol.runtime.real_openai_api_invocation import (
    INVOKED,
    RealOpenAIAPIInvocationEvidence,
    invoke_real_openai_api,
    reconstruct_real_openai_api_invocation_lineage,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


VALIDATED = "VALIDATED"
REJECTED = "REJECTED"
ALLOWED_USAGE_VALIDATION_STATUSES = frozenset({VALIDATED, REJECTED})


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _usage_hash_input(evidence: "LiveRuntimeUsageValidationEvidence") -> dict[str, Any]:
    return {
        "validation_id": evidence.validation_id,
        "usage_count": evidence.usage_count,
        "successful_count": evidence.successful_count,
        "rejected_count": evidence.rejected_count,
        "replay_continuity_valid": evidence.replay_continuity_valid,
        "governed_return_consistent": evidence.governed_return_consistent,
        "validation_status": evidence.validation_status,
        "reason": evidence.reason,
        "created_at": evidence.created_at,
    }


@dataclass(frozen=True)
class LiveRuntimeUsageValidationEvidence:
    """Immutable replay-visible operational usage validation evidence."""

    validation_id: str
    usage_count: int
    successful_count: int
    rejected_count: int
    replay_continuity_valid: bool
    governed_return_consistent: bool
    validation_status: str
    reason: str
    created_at: str
    evidence_hash: str = ""

    def __post_init__(self) -> None:
        _require_string(self.validation_id, "validation_id")
        _require_string(self.reason, "reason")
        _require_string(self.created_at, "created_at")
        if self.validation_status not in ALLOWED_USAGE_VALIDATION_STATUSES:
            raise FailClosedRuntimeError("usage validation status is not allowed")
        for field_name in ("usage_count", "successful_count", "rejected_count"):
            value = getattr(self, field_name)
            if not isinstance(value, int) or value < 0:
                raise FailClosedRuntimeError(f"{field_name} must be a non-negative integer")
        if self.successful_count + self.rejected_count != self.usage_count:
            raise FailClosedRuntimeError("usage validation counts are inconsistent")
        if not isinstance(self.replay_continuity_valid, bool):
            raise FailClosedRuntimeError("replay_continuity_valid must be boolean")
        if not isinstance(self.governed_return_consistent, bool):
            raise FailClosedRuntimeError("governed_return_consistent must be boolean")
        expected_hash = replay_hash(_usage_hash_input(self))
        if self.evidence_hash and self.evidence_hash != expected_hash:
            raise FailClosedRuntimeError("live runtime usage validation evidence hash mismatch")
        object.__setattr__(self, "evidence_hash", self.evidence_hash or expected_hash)

    def to_dict(self) -> dict[str, Any]:
        return {
            "validation_id": self.validation_id,
            "usage_count": self.usage_count,
            "successful_count": self.successful_count,
            "rejected_count": self.rejected_count,
            "replay_continuity_valid": self.replay_continuity_valid,
            "governed_return_consistent": self.governed_return_consistent,
            "validation_status": self.validation_status,
            "reason": self.reason,
            "created_at": self.created_at,
            "evidence_hash": self.evidence_hash,
        }

    @classmethod
    def from_dict(cls, evidence: dict[str, Any]) -> "LiveRuntimeUsageValidationEvidence":
        if not isinstance(evidence, dict):
            raise FailClosedRuntimeError("live runtime usage validation evidence must be a JSON object")
        required = {
            "validation_id",
            "usage_count",
            "successful_count",
            "rejected_count",
            "replay_continuity_valid",
            "governed_return_consistent",
            "validation_status",
            "reason",
            "created_at",
            "evidence_hash",
        }
        if set(evidence) != required:
            raise FailClosedRuntimeError("live runtime usage validation evidence has malformed structure")
        return cls(**evidence)


def validate_live_runtime_usage(
    *,
    validation_id: str,
    human_prompts: list[str] | tuple[str, ...],
    created_at: str,
    timeout_seconds: int = 20,
) -> dict[str, Any]:
    """Validate repeated readonly governed runtime usage through real OpenAI invocation."""

    try:
        _require_string(validation_id, "validation_id")
        _require_string(created_at, "created_at")
        if not isinstance(human_prompts, list | tuple) or not human_prompts:
            raise FailClosedRuntimeError("human_prompts must be a non-empty list")
        usage_records = []
        invocation_evidence = []
        returns = []
        for index, human_prompt in enumerate(human_prompts):
            request = " ".join(_require_string(human_prompt, "human_prompt").split())
            usage = _run_one_usage(
                usage_id=f"{validation_id}:USAGE:{index + 1:03d}",
                human_request=request,
                created_at=f"{created_at}:USAGE:{index + 1:03d}",
                timeout_seconds=timeout_seconds,
            )
            usage_records.append(usage)
            invocation_evidence.append(usage["invocation"]["invocation_evidence"])
            if usage["governed_return"] is not None:
                returns.append(usage["governed_return"])
        invocation_lineage = reconstruct_real_openai_api_invocation_lineage(invocation_evidence)
        successful_count = sum(1 for usage in usage_records if usage["usage_status"] == VALIDATED)
        rejected_count = len(usage_records) - successful_count
        governed_return_consistent = _governed_returns_are_consistent(returns, successful_count)
        replay_continuity_valid = (
            invocation_lineage["append_only_valid"] is True
            and invocation_lineage["lineage_valid"] is True
            and len(invocation_lineage["openai_api_invocations"]) == len(usage_records)
        )
        validation_status = VALIDATED if successful_count == len(usage_records) and governed_return_consistent else REJECTED
        evidence = LiveRuntimeUsageValidationEvidence(
            validation_id=validation_id,
            usage_count=len(usage_records),
            successful_count=successful_count,
            rejected_count=rejected_count,
            replay_continuity_valid=replay_continuity_valid,
            governed_return_consistent=governed_return_consistent,
            validation_status=validation_status,
            reason=(
                "live runtime usage validation completed"
                if validation_status == VALIDATED
                else "live runtime usage validation failed closed"
            ),
            created_at=created_at,
        )
        return {
            "usage_validation_evidence": evidence,
            "usage_records": usage_records,
            "invocation_lineage": invocation_lineage,
            "governance_authority_separated": True,
        }
    except (FailClosedRuntimeError, TypeError, ValueError, KeyError):
        evidence = LiveRuntimeUsageValidationEvidence(
            validation_id=validation_id if isinstance(validation_id, str) and validation_id else "USAGE-VALIDATION-INVALID",
            usage_count=0,
            successful_count=0,
            rejected_count=0,
            replay_continuity_valid=False,
            governed_return_consistent=False,
            validation_status=REJECTED,
            reason="live runtime usage validation failed closed",
            created_at=created_at if isinstance(created_at, str) and created_at else "1970-01-01T00:00:00+00:00",
        )
        return {
            "usage_validation_evidence": evidence,
            "usage_records": [],
            "invocation_lineage": None,
            "governance_authority_separated": True,
        }


def reconstruct_live_runtime_usage_validation_lineage(
    validations: list[LiveRuntimeUsageValidationEvidence | dict[str, Any]]
    | tuple[LiveRuntimeUsageValidationEvidence | dict[str, Any], ...],
) -> dict[str, Any]:
    if not isinstance(validations, list | tuple):
        raise FailClosedRuntimeError("live runtime usage validation lineage must be a list")
    reconstructed = []
    seen_validation_ids: set[str] = set()
    previous_created_at = ""
    for index, validation in enumerate(validations):
        validation_obj = LiveRuntimeUsageValidationEvidence.from_dict(validation) if isinstance(validation, dict) else validation
        if not isinstance(validation_obj, LiveRuntimeUsageValidationEvidence):
            raise FailClosedRuntimeError("live runtime usage validation lineage entry is invalid")
        artifact = validation_obj.to_dict()
        if artifact["validation_id"] in seen_validation_ids:
            raise FailClosedRuntimeError("live runtime usage validation lineage contains duplicate validation_id")
        if previous_created_at and artifact["created_at"] < previous_created_at:
            raise FailClosedRuntimeError("live runtime usage validation lineage ordering is not deterministic")
        canonical_serialize(artifact)
        seen_validation_ids.add(artifact["validation_id"])
        previous_created_at = artifact["created_at"]
        reconstructed.append(
            {
                "validation_index": index,
                "validation_id": artifact["validation_id"],
                "validation_status": artifact["validation_status"],
                "usage_count": artifact["usage_count"],
                "evidence_hash": artifact["evidence_hash"],
            }
        )
    lineage = {
        "validation_count": len(reconstructed),
        "usage_validations": reconstructed,
        "append_only_valid": True,
        "lineage_valid": True,
        "governance_authority_separated": True,
    }
    lineage["lineage_hash"] = replay_hash(lineage)
    return lineage


def _run_one_usage(*, usage_id: str, human_request: str, created_at: str, timeout_seconds: int) -> dict[str, Any]:
    invocation = invoke_real_openai_api(
        invocation_id=f"{usage_id}:OPENAI",
        human_request=human_request,
        created_at=created_at,
        timeout_seconds=timeout_seconds,
    )
    if invocation["invocation_evidence"].invocation_status != INVOKED:
        return _usage_rejected(usage_id, invocation, "real OpenAI invocation rejected")
    proposal_payload = invocation["connector"]["external_model_response"]["proposal_payload"]
    execution = execute_minimal_governed_path(
        execution_id=f"{usage_id}:EXECUTION",
        llm_proposal_input=proposal_payload,
        created_at=created_at,
    )
    execution_result = execution["execution_result"]
    if execution_result.execution_status != EXECUTED:
        return _usage_rejected(usage_id, invocation, "governed execution rejected", execution=execution)
    isolation = validate_production_isolation(
        isolation_id=f"{usage_id}:ISOLATION",
        execution_result=execution_result,
        quota_policy={
            "max_provider_invocations": 1,
            "allowed_provider": "metadata_inspection_provider",
            "allowed_operation": "inspect_runtime",
        },
        isolation_metadata={
            "isolation_mode": "LOCAL_READONLY_SINGLE_PROVIDER",
            "provider_state_mutation_allowed": False,
            "runtime_state_mutation_allowed": False,
            "network_mutation_allowed": False,
            "replay_durability": "APPEND_ONLY_HASHED_EVIDENCE",
            "governance_authority_separated": True,
        },
        created_at=created_at,
    )
    governed_return = interpret_governed_execution_return(
        return_id=f"{usage_id}:RETURN",
        execution_result=execution_result,
        provider_evidence=execution["provider_evidence"],
        session_lineage=execution["session_lineage"],
        isolation_evidence=isolation,
        created_at=created_at,
    )
    if isolation.isolation_status != ISOLATED or governed_return.return_status != ACCEPTED:
        return _usage_rejected(
            usage_id,
            invocation,
            "governed return rejected",
            execution=execution,
            isolation=isolation,
            governed_return=governed_return,
        )
    return {
        "usage_id": usage_id,
        "usage_status": VALIDATED,
        "usage_reason": "readonly runtime usage completed",
        "invocation": invocation,
        "execution": execution,
        "isolation": isolation,
        "governed_return": governed_return,
        "return_display": governed_return.normalized_return_summary,
    }


def _usage_rejected(
    usage_id: str,
    invocation: dict[str, Any],
    reason: str,
    execution: dict[str, Any] | None = None,
    isolation: Any = None,
    governed_return: Any = None,
) -> dict[str, Any]:
    return {
        "usage_id": usage_id,
        "usage_status": REJECTED,
        "usage_reason": reason,
        "invocation": invocation,
        "execution": execution,
        "isolation": isolation,
        "governed_return": governed_return,
        "return_display": "live runtime usage rejected",
    }


def _governed_returns_are_consistent(returns: list[Any], successful_count: int) -> bool:
    if successful_count == 0:
        return False
    if len(returns) != successful_count:
        return False
    for governed_return in returns:
        if governed_return.return_status != ACCEPTED:
            return False
        if governed_return.provider_reference != "metadata_inspection_provider.inspect_runtime":
            return False
        if not governed_return.normalized_return_summary.startswith("operation=inspect_runtime"):
            return False
    return True
