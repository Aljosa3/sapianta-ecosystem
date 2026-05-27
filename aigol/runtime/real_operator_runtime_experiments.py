"""Readonly operator experiment validation over the governed CLI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.operator_cli import (
    CLI_COMPLETED,
    RuntimeOperatorCLIEvidence,
    reconstruct_runtime_operator_cli_lineage,
    run_runtime_operator_cli,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


EXPERIMENT_COMPLETED = "COMPLETED"
EXPERIMENT_REJECTED = "REJECTED"
EXPERIMENT_MODE = "SEQUENTIAL_READONLY_OPERATOR_RUNTIME_EXPERIMENTS"
ALLOWED_EXPERIMENT_STATUSES = frozenset({EXPERIMENT_COMPLETED, EXPERIMENT_REJECTED})


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _experiment_hash_input(evidence: "RealOperatorRuntimeExperimentsEvidence") -> dict[str, Any]:
    return {
        "experiment_id": evidence.experiment_id,
        "operator_id": evidence.operator_id,
        "experiment_mode": evidence.experiment_mode,
        "scenario_count": evidence.scenario_count,
        "completed_count": evidence.completed_count,
        "rejected_count": evidence.rejected_count,
        "replay_continuity_valid": evidence.replay_continuity_valid,
        "return_consistency_valid": evidence.return_consistency_valid,
        "experiment_status": evidence.experiment_status,
        "experiment_reason": evidence.experiment_reason,
        "created_at": evidence.created_at,
    }


@dataclass(frozen=True)
class RealOperatorRuntimeExperimentsEvidence:
    """Immutable replay-visible readonly runtime experiment evidence."""

    experiment_id: str
    operator_id: str
    experiment_mode: str
    scenario_count: int
    completed_count: int
    rejected_count: int
    replay_continuity_valid: bool
    return_consistency_valid: bool
    experiment_status: str
    experiment_reason: str
    created_at: str
    evidence_hash: str = ""

    def __post_init__(self) -> None:
        _require_string(self.experiment_id, "experiment_id")
        _require_string(self.operator_id, "operator_id")
        _require_string(self.experiment_mode, "experiment_mode")
        _require_string(self.experiment_reason, "experiment_reason")
        _require_string(self.created_at, "created_at")
        if self.experiment_mode != EXPERIMENT_MODE:
            raise FailClosedRuntimeError("operator runtime experiment mode is not allowed")
        if self.experiment_status not in ALLOWED_EXPERIMENT_STATUSES:
            raise FailClosedRuntimeError("operator runtime experiment status is not allowed")
        for field_name in ("scenario_count", "completed_count", "rejected_count"):
            value = getattr(self, field_name)
            if not isinstance(value, int) or value < 0:
                raise FailClosedRuntimeError(f"{field_name} must be a non-negative integer")
        if self.completed_count + self.rejected_count != self.scenario_count:
            raise FailClosedRuntimeError("operator runtime experiment counts are inconsistent")
        if not isinstance(self.replay_continuity_valid, bool):
            raise FailClosedRuntimeError("replay_continuity_valid must be boolean")
        if not isinstance(self.return_consistency_valid, bool):
            raise FailClosedRuntimeError("return_consistency_valid must be boolean")
        expected_hash = replay_hash(_experiment_hash_input(self))
        if self.evidence_hash and self.evidence_hash != expected_hash:
            raise FailClosedRuntimeError("operator runtime experiment evidence hash mismatch")
        object.__setattr__(self, "evidence_hash", self.evidence_hash or expected_hash)

    def to_dict(self) -> dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "operator_id": self.operator_id,
            "experiment_mode": self.experiment_mode,
            "scenario_count": self.scenario_count,
            "completed_count": self.completed_count,
            "rejected_count": self.rejected_count,
            "replay_continuity_valid": self.replay_continuity_valid,
            "return_consistency_valid": self.return_consistency_valid,
            "experiment_status": self.experiment_status,
            "experiment_reason": self.experiment_reason,
            "created_at": self.created_at,
            "evidence_hash": self.evidence_hash,
        }

    @classmethod
    def from_dict(cls, evidence: dict[str, Any]) -> "RealOperatorRuntimeExperimentsEvidence":
        if not isinstance(evidence, dict):
            raise FailClosedRuntimeError("operator runtime experiment evidence must be a JSON object")
        required = {
            "experiment_id",
            "operator_id",
            "experiment_mode",
            "scenario_count",
            "completed_count",
            "rejected_count",
            "replay_continuity_valid",
            "return_consistency_valid",
            "experiment_status",
            "experiment_reason",
            "created_at",
            "evidence_hash",
        }
        if set(evidence) != required:
            raise FailClosedRuntimeError("operator runtime experiment evidence has malformed structure")
        return cls(**evidence)


def run_real_operator_runtime_experiments(
    *,
    experiment_id: str,
    operator_id: str,
    operator_prompts: list[str] | tuple[str, ...],
    created_at: str,
    timeout_seconds: int = 20,
) -> dict[str, Any]:
    """Run sequential readonly operator prompts through the existing CLI path."""

    try:
        _require_string(experiment_id, "experiment_id")
        normalized_operator_id = " ".join(_require_string(operator_id, "operator_id").split())
        _require_string(created_at, "created_at")
        if not isinstance(operator_prompts, list | tuple) or not operator_prompts:
            raise FailClosedRuntimeError("operator_prompts must be a non-empty list")
        cli_records = []
        cli_evidence: list[RuntimeOperatorCLIEvidence] = []
        for index, operator_prompt in enumerate(operator_prompts):
            prompt = " ".join(_require_string(operator_prompt, "operator_prompt").split())
            cli_result = run_runtime_operator_cli(
                cli_invocation_id=f"{experiment_id}:CLI:{index + 1:03d}",
                operator_id=normalized_operator_id,
                operator_prompt=prompt,
                created_at=f"{created_at}:CLI:{index + 1:03d}",
                timeout_seconds=timeout_seconds,
            )
            cli_records.append(cli_result)
            cli_evidence.append(cli_result["cli_evidence"])
        cli_lineage = reconstruct_runtime_operator_cli_lineage(cli_evidence)
        completed_count = sum(1 for cli_result in cli_records if cli_result["cli_evidence"].cli_status == CLI_COMPLETED)
        rejected_count = len(cli_records) - completed_count
        replay_continuity_valid = (
            cli_lineage["append_only_valid"] is True
            and cli_lineage["lineage_valid"] is True
            and cli_lineage["cli_invocation_count"] == len(cli_records)
        )
        return_consistency_valid = _returns_are_consistent(cli_records, completed_count)
        experiment_status = (
            EXPERIMENT_COMPLETED
            if completed_count == len(cli_records) and return_consistency_valid
            else EXPERIMENT_REJECTED
        )
        evidence = RealOperatorRuntimeExperimentsEvidence(
            experiment_id=experiment_id,
            operator_id=normalized_operator_id,
            experiment_mode=EXPERIMENT_MODE,
            scenario_count=len(cli_records),
            completed_count=completed_count,
            rejected_count=rejected_count,
            replay_continuity_valid=replay_continuity_valid,
            return_consistency_valid=return_consistency_valid,
            experiment_status=experiment_status,
            experiment_reason=(
                "readonly operator runtime experiments completed"
                if experiment_status == EXPERIMENT_COMPLETED
                else "readonly operator runtime experiments failed closed"
            ),
            created_at=created_at,
        )
        return {
            "experiment_evidence": evidence,
            "cli_records": cli_records,
            "cli_lineage": cli_lineage,
            "experiment_lineage": reconstruct_real_operator_runtime_experiments_lineage([evidence]),
            "governance_authority_separated": True,
        }
    except (FailClosedRuntimeError, TypeError, ValueError, KeyError):
        evidence = RealOperatorRuntimeExperimentsEvidence(
            experiment_id=experiment_id if isinstance(experiment_id, str) and experiment_id else "OPERATOR-EXPERIMENT-INVALID",
            operator_id=operator_id if isinstance(operator_id, str) and operator_id else "OPERATOR-INVALID",
            experiment_mode=EXPERIMENT_MODE,
            scenario_count=0,
            completed_count=0,
            rejected_count=0,
            replay_continuity_valid=False,
            return_consistency_valid=False,
            experiment_status=EXPERIMENT_REJECTED,
            experiment_reason="readonly operator runtime experiments failed closed",
            created_at=created_at if isinstance(created_at, str) and created_at else "1970-01-01T00:00:00+00:00",
        )
        return {
            "experiment_evidence": evidence,
            "cli_records": [],
            "cli_lineage": None,
            "experiment_lineage": reconstruct_real_operator_runtime_experiments_lineage([evidence]),
            "governance_authority_separated": True,
        }


def reconstruct_real_operator_runtime_experiments_lineage(
    experiments: list[RealOperatorRuntimeExperimentsEvidence | dict[str, Any]]
    | tuple[RealOperatorRuntimeExperimentsEvidence | dict[str, Any], ...],
) -> dict[str, Any]:
    if not isinstance(experiments, list | tuple):
        raise FailClosedRuntimeError("operator runtime experiment lineage must be a list")
    reconstructed = []
    seen_experiment_ids: set[str] = set()
    previous_created_at = ""
    for index, experiment in enumerate(experiments):
        experiment_obj = (
            RealOperatorRuntimeExperimentsEvidence.from_dict(experiment)
            if isinstance(experiment, dict)
            else experiment
        )
        if not isinstance(experiment_obj, RealOperatorRuntimeExperimentsEvidence):
            raise FailClosedRuntimeError("operator runtime experiment lineage entry is invalid")
        artifact = experiment_obj.to_dict()
        if artifact["experiment_id"] in seen_experiment_ids:
            raise FailClosedRuntimeError("operator runtime experiment lineage contains duplicate experiment_id")
        if previous_created_at and artifact["created_at"] < previous_created_at:
            raise FailClosedRuntimeError("operator runtime experiment lineage ordering is not deterministic")
        canonical_serialize(artifact)
        seen_experiment_ids.add(artifact["experiment_id"])
        previous_created_at = artifact["created_at"]
        reconstructed.append(
            {
                "experiment_index": index,
                "experiment_id": artifact["experiment_id"],
                "operator_id": artifact["operator_id"],
                "experiment_status": artifact["experiment_status"],
                "scenario_count": artifact["scenario_count"],
                "evidence_hash": artifact["evidence_hash"],
            }
        )
    lineage = {
        "experiment_count": len(reconstructed),
        "operator_runtime_experiments": reconstructed,
        "append_only_valid": True,
        "lineage_valid": True,
        "governance_authority_separated": True,
    }
    lineage["lineage_hash"] = replay_hash(lineage)
    return lineage


def _returns_are_consistent(cli_records: list[dict[str, Any]], completed_count: int) -> bool:
    if completed_count == 0:
        return False
    completed_records = [
        cli_result for cli_result in cli_records if cli_result["cli_evidence"].cli_status == CLI_COMPLETED
    ]
    if len(completed_records) != completed_count:
        return False
    for cli_result in completed_records:
        rendered_return = cli_result["cli_evidence"].rendered_return
        if not isinstance(rendered_return, str) or not rendered_return.startswith("operation=inspect_runtime"):
            return False
    return True
