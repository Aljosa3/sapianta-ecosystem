"""Sequential operator interaction validation over the live governed runtime."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aigol.runtime.first_real_operator_usage import (
    OPERATOR_COMPLETED,
    FirstRealOperatorUsageEvidence,
    reconstruct_first_real_operator_usage_lineage,
    run_first_real_operator_usage,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


LOOP_COMPLETED = "COMPLETED"
LOOP_REJECTED = "REJECTED"
LOOP_MODE = "SEQUENTIAL_READONLY_OPERATOR_INTERACTION"
ALLOWED_LOOP_STATUSES = frozenset({LOOP_COMPLETED, LOOP_REJECTED})


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _loop_hash_input(evidence: "OperatorInteractionLoopEvidence") -> dict[str, Any]:
    return {
        "loop_id": evidence.loop_id,
        "operator_id": evidence.operator_id,
        "loop_mode": evidence.loop_mode,
        "request_count": evidence.request_count,
        "completed_count": evidence.completed_count,
        "rejected_count": evidence.rejected_count,
        "replay_continuity_valid": evidence.replay_continuity_valid,
        "return_continuity_valid": evidence.return_continuity_valid,
        "loop_status": evidence.loop_status,
        "loop_reason": evidence.loop_reason,
        "created_at": evidence.created_at,
    }


@dataclass(frozen=True)
class OperatorInteractionLoopEvidence:
    """Immutable replay-visible sequential operator interaction evidence."""

    loop_id: str
    operator_id: str
    loop_mode: str
    request_count: int
    completed_count: int
    rejected_count: int
    replay_continuity_valid: bool
    return_continuity_valid: bool
    loop_status: str
    loop_reason: str
    created_at: str
    evidence_hash: str = ""

    def __post_init__(self) -> None:
        _require_string(self.loop_id, "loop_id")
        _require_string(self.operator_id, "operator_id")
        _require_string(self.loop_mode, "loop_mode")
        _require_string(self.loop_reason, "loop_reason")
        _require_string(self.created_at, "created_at")
        if self.loop_mode != LOOP_MODE:
            raise FailClosedRuntimeError("operator interaction loop mode is not allowed")
        if self.loop_status not in ALLOWED_LOOP_STATUSES:
            raise FailClosedRuntimeError("operator interaction loop status is not allowed")
        for field_name in ("request_count", "completed_count", "rejected_count"):
            value = getattr(self, field_name)
            if not isinstance(value, int) or value < 0:
                raise FailClosedRuntimeError(f"{field_name} must be a non-negative integer")
        if self.completed_count + self.rejected_count != self.request_count:
            raise FailClosedRuntimeError("operator interaction loop counts are inconsistent")
        if not isinstance(self.replay_continuity_valid, bool):
            raise FailClosedRuntimeError("replay_continuity_valid must be boolean")
        if not isinstance(self.return_continuity_valid, bool):
            raise FailClosedRuntimeError("return_continuity_valid must be boolean")
        expected_hash = replay_hash(_loop_hash_input(self))
        if self.evidence_hash and self.evidence_hash != expected_hash:
            raise FailClosedRuntimeError("operator interaction loop evidence hash mismatch")
        object.__setattr__(self, "evidence_hash", self.evidence_hash or expected_hash)

    def to_dict(self) -> dict[str, Any]:
        return {
            "loop_id": self.loop_id,
            "operator_id": self.operator_id,
            "loop_mode": self.loop_mode,
            "request_count": self.request_count,
            "completed_count": self.completed_count,
            "rejected_count": self.rejected_count,
            "replay_continuity_valid": self.replay_continuity_valid,
            "return_continuity_valid": self.return_continuity_valid,
            "loop_status": self.loop_status,
            "loop_reason": self.loop_reason,
            "created_at": self.created_at,
            "evidence_hash": self.evidence_hash,
        }

    @classmethod
    def from_dict(cls, evidence: dict[str, Any]) -> "OperatorInteractionLoopEvidence":
        if not isinstance(evidence, dict):
            raise FailClosedRuntimeError("operator interaction loop evidence must be a JSON object")
        required = {
            "loop_id",
            "operator_id",
            "loop_mode",
            "request_count",
            "completed_count",
            "rejected_count",
            "replay_continuity_valid",
            "return_continuity_valid",
            "loop_status",
            "loop_reason",
            "created_at",
            "evidence_hash",
        }
        if set(evidence) != required:
            raise FailClosedRuntimeError("operator interaction loop evidence has malformed structure")
        return cls(**evidence)


def run_operator_interaction_loop(
    *,
    loop_id: str,
    operator_id: str,
    operator_prompts: list[str] | tuple[str, ...],
    created_at: str,
    timeout_seconds: int = 20,
) -> dict[str, Any]:
    """Run a bounded sequential list of readonly operator prompts."""

    try:
        _require_string(loop_id, "loop_id")
        normalized_operator_id = " ".join(_require_string(operator_id, "operator_id").split())
        _require_string(created_at, "created_at")
        if not isinstance(operator_prompts, list | tuple) or not operator_prompts:
            raise FailClosedRuntimeError("operator_prompts must be a non-empty list")
        usage_records = []
        usage_evidence = []
        for index, operator_prompt in enumerate(operator_prompts):
            prompt = " ".join(_require_string(operator_prompt, "operator_prompt").split())
            usage = run_first_real_operator_usage(
                operator_usage_id=f"{loop_id}:OPERATOR_USAGE:{index + 1:03d}",
                operator_id=normalized_operator_id,
                operator_request=prompt,
                created_at=f"{created_at}:OPERATOR_USAGE:{index + 1:03d}",
                timeout_seconds=timeout_seconds,
            )
            usage_records.append(usage)
            usage_evidence.append(usage["operator_usage_evidence"])
        operator_usage_lineage = reconstruct_first_real_operator_usage_lineage(usage_evidence)
        completed_count = sum(1 for usage in usage_records if usage["operator_usage_evidence"].operator_usage_status == OPERATOR_COMPLETED)
        rejected_count = len(usage_records) - completed_count
        replay_continuity_valid = (
            operator_usage_lineage["append_only_valid"] is True
            and operator_usage_lineage["lineage_valid"] is True
            and operator_usage_lineage["operator_usage_count"] == len(usage_records)
        )
        return_continuity_valid = _returns_are_continuous(usage_records, completed_count)
        loop_status = LOOP_COMPLETED if completed_count == len(usage_records) and return_continuity_valid else LOOP_REJECTED
        evidence = OperatorInteractionLoopEvidence(
            loop_id=loop_id,
            operator_id=normalized_operator_id,
            loop_mode=LOOP_MODE,
            request_count=len(usage_records),
            completed_count=completed_count,
            rejected_count=rejected_count,
            replay_continuity_valid=replay_continuity_valid,
            return_continuity_valid=return_continuity_valid,
            loop_status=loop_status,
            loop_reason=(
                "sequential operator interaction completed"
                if loop_status == LOOP_COMPLETED
                else "sequential operator interaction failed closed"
            ),
            created_at=created_at,
        )
        return {
            "loop_evidence": evidence,
            "usage_records": usage_records,
            "operator_usage_lineage": operator_usage_lineage,
            "loop_lineage": reconstruct_operator_interaction_loop_lineage([evidence]),
            "governance_authority_separated": True,
        }
    except (FailClosedRuntimeError, TypeError, ValueError, KeyError):
        evidence = OperatorInteractionLoopEvidence(
            loop_id=loop_id if isinstance(loop_id, str) and loop_id else "OPERATOR-LOOP-INVALID",
            operator_id=operator_id if isinstance(operator_id, str) and operator_id else "OPERATOR-INVALID",
            loop_mode=LOOP_MODE,
            request_count=0,
            completed_count=0,
            rejected_count=0,
            replay_continuity_valid=False,
            return_continuity_valid=False,
            loop_status=LOOP_REJECTED,
            loop_reason="sequential operator interaction failed closed",
            created_at=created_at if isinstance(created_at, str) and created_at else "1970-01-01T00:00:00+00:00",
        )
        return {
            "loop_evidence": evidence,
            "usage_records": [],
            "operator_usage_lineage": None,
            "loop_lineage": reconstruct_operator_interaction_loop_lineage([evidence]),
            "governance_authority_separated": True,
        }


def reconstruct_operator_interaction_loop_lineage(
    loops: list[OperatorInteractionLoopEvidence | dict[str, Any]]
    | tuple[OperatorInteractionLoopEvidence | dict[str, Any], ...],
) -> dict[str, Any]:
    if not isinstance(loops, list | tuple):
        raise FailClosedRuntimeError("operator interaction loop lineage must be a list")
    reconstructed = []
    seen_loop_ids: set[str] = set()
    previous_created_at = ""
    for index, loop in enumerate(loops):
        loop_obj = OperatorInteractionLoopEvidence.from_dict(loop) if isinstance(loop, dict) else loop
        if not isinstance(loop_obj, OperatorInteractionLoopEvidence):
            raise FailClosedRuntimeError("operator interaction loop lineage entry is invalid")
        artifact = loop_obj.to_dict()
        if artifact["loop_id"] in seen_loop_ids:
            raise FailClosedRuntimeError("operator interaction loop lineage contains duplicate loop_id")
        if previous_created_at and artifact["created_at"] < previous_created_at:
            raise FailClosedRuntimeError("operator interaction loop lineage ordering is not deterministic")
        canonical_serialize(artifact)
        seen_loop_ids.add(artifact["loop_id"])
        previous_created_at = artifact["created_at"]
        reconstructed.append(
            {
                "loop_index": index,
                "loop_id": artifact["loop_id"],
                "operator_id": artifact["operator_id"],
                "loop_status": artifact["loop_status"],
                "request_count": artifact["request_count"],
                "evidence_hash": artifact["evidence_hash"],
            }
        )
    lineage = {
        "loop_count": len(reconstructed),
        "operator_interaction_loops": reconstructed,
        "append_only_valid": True,
        "lineage_valid": True,
        "governance_authority_separated": True,
    }
    lineage["lineage_hash"] = replay_hash(lineage)
    return lineage


def _returns_are_continuous(usage_records: list[dict[str, Any]], completed_count: int) -> bool:
    if completed_count == 0:
        return False
    completed_records = [
        usage for usage in usage_records if usage["operator_usage_evidence"].operator_usage_status == OPERATOR_COMPLETED
    ]
    if len(completed_records) != completed_count:
        return False
    for usage in completed_records:
        operator_return = usage["operator_return"]
        if not isinstance(operator_return, str) or not operator_return.startswith("operation=inspect_runtime"):
            return False
    return True
