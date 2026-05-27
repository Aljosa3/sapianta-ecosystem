"""First readonly domain experiment for governed runtime inspection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from aigol.runtime.minimal_real_runtime_demo import COMPLETED, run_minimal_real_runtime_demo
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


EXPERIMENT_COMPLETED = "COMPLETED"
EXPERIMENT_REJECTED = "REJECTED"
DOMAIN_NAME = "Governance Runtime Inspector"
DOMAIN_SURFACE = "readonly_runtime_metadata_inspection"
ALLOWED_EXPERIMENT_STATUSES = frozenset({EXPERIMENT_COMPLETED, EXPERIMENT_REJECTED})


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _experiment_hash_input(evidence: "ReadonlyDomainExperimentEvidence") -> dict[str, Any]:
    return {
        "experiment_id": evidence.experiment_id,
        "domain_name": evidence.domain_name,
        "domain_surface": evidence.domain_surface,
        "human_request": evidence.human_request,
        "demo_evidence_hash": evidence.demo_evidence_hash,
        "return_evidence_hash": evidence.return_evidence_hash,
        "experiment_status": evidence.experiment_status,
        "experiment_reason": evidence.experiment_reason,
        "created_at": evidence.created_at,
    }


@dataclass(frozen=True)
class ReadonlyDomainExperimentEvidence:
    """Immutable replay-visible domain experiment evidence."""

    experiment_id: str
    domain_name: str
    domain_surface: str
    human_request: str
    demo_evidence_hash: str
    return_evidence_hash: str
    experiment_status: str
    experiment_reason: str
    created_at: str
    evidence_hash: str = ""

    def __post_init__(self) -> None:
        _require_string(self.experiment_id, "experiment_id")
        _require_string(self.domain_name, "domain_name")
        _require_string(self.domain_surface, "domain_surface")
        _require_string(self.human_request, "human_request")
        _require_string(self.experiment_reason, "experiment_reason")
        _require_string(self.created_at, "created_at")
        if self.domain_name != DOMAIN_NAME:
            raise FailClosedRuntimeError("domain experiment name is not allowed")
        if self.domain_surface != DOMAIN_SURFACE:
            raise FailClosedRuntimeError("domain experiment surface is not allowed")
        if self.experiment_status not in ALLOWED_EXPERIMENT_STATUSES:
            raise FailClosedRuntimeError("domain experiment status is not allowed")
        expected_hash = replay_hash(_experiment_hash_input(self))
        if self.evidence_hash and self.evidence_hash != expected_hash:
            raise FailClosedRuntimeError("readonly domain experiment evidence hash mismatch")
        object.__setattr__(self, "evidence_hash", self.evidence_hash or expected_hash)

    def to_dict(self) -> dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "domain_name": self.domain_name,
            "domain_surface": self.domain_surface,
            "human_request": self.human_request,
            "demo_evidence_hash": self.demo_evidence_hash,
            "return_evidence_hash": self.return_evidence_hash,
            "experiment_status": self.experiment_status,
            "experiment_reason": self.experiment_reason,
            "created_at": self.created_at,
            "evidence_hash": self.evidence_hash,
        }

    @classmethod
    def from_dict(cls, evidence: dict[str, Any]) -> "ReadonlyDomainExperimentEvidence":
        if not isinstance(evidence, dict):
            raise FailClosedRuntimeError("readonly domain experiment evidence must be a JSON object")
        required = {
            "experiment_id",
            "domain_name",
            "domain_surface",
            "human_request",
            "demo_evidence_hash",
            "return_evidence_hash",
            "experiment_status",
            "experiment_reason",
            "created_at",
            "evidence_hash",
        }
        if set(evidence) != required:
            raise FailClosedRuntimeError("readonly domain experiment evidence has malformed structure")
        return cls(**evidence)


def run_governance_runtime_inspector_experiment(
    *,
    experiment_id: str,
    human_request: str,
    openai_call: Callable[[dict[str, Any]], Any],
    created_at: str,
) -> dict[str, Any]:
    """Run one readonly runtime metadata inspection domain experiment."""

    try:
        _require_string(experiment_id, "experiment_id")
        normalized_human_request = " ".join(_require_string(human_request, "human_request").split())
        _require_string(created_at, "created_at")
        demo = run_minimal_real_runtime_demo(
            demo_id=f"{experiment_id}:DEMO",
            human_request=normalized_human_request,
            openai_call=openai_call,
            created_at=created_at,
        )
        demo_evidence = demo["demo_evidence"]
        governed_return = demo.get("governed_return")
        return_evidence_hash = governed_return.evidence_hash if governed_return is not None else demo_evidence.return_evidence_hash
        if demo_evidence.demo_status != COMPLETED:
            return _experiment_rejected(
                experiment_id,
                normalized_human_request,
                demo_evidence.evidence_hash,
                return_evidence_hash,
                "readonly domain experiment rejected by governed runtime",
                created_at,
                demo,
            )
        evidence = ReadonlyDomainExperimentEvidence(
            experiment_id=experiment_id,
            domain_name=DOMAIN_NAME,
            domain_surface=DOMAIN_SURFACE,
            human_request=normalized_human_request,
            demo_evidence_hash=demo_evidence.evidence_hash,
            return_evidence_hash=return_evidence_hash,
            experiment_status=EXPERIMENT_COMPLETED,
            experiment_reason="readonly runtime metadata domain experiment completed",
            created_at=created_at,
        )
        return {
            "experiment_evidence": evidence,
            "domain_name": DOMAIN_NAME,
            "domain_surface": DOMAIN_SURFACE,
            "demo": demo,
            "domain_return": demo["return_display"],
            "experiment_lineage": reconstruct_readonly_domain_experiment_lineage([evidence]),
            "governance_authority_separated": True,
        }
    except (FailClosedRuntimeError, TypeError, ValueError, KeyError):
        return _experiment_rejected(
            experiment_id if isinstance(experiment_id, str) and experiment_id else "EXPERIMENT-INVALID",
            human_request if isinstance(human_request, str) and human_request else "REQUEST-INVALID",
            "",
            "",
            "readonly domain experiment failed closed",
            created_at if isinstance(created_at, str) and created_at else "1970-01-01T00:00:00+00:00",
        )


def reconstruct_readonly_domain_experiment_lineage(
    experiments: list[ReadonlyDomainExperimentEvidence | dict[str, Any]]
    | tuple[ReadonlyDomainExperimentEvidence | dict[str, Any], ...],
) -> dict[str, Any]:
    if not isinstance(experiments, list | tuple):
        raise FailClosedRuntimeError("readonly domain experiment lineage must be a list")
    reconstructed = []
    seen_experiment_ids: set[str] = set()
    previous_created_at = ""
    for index, experiment in enumerate(experiments):
        experiment_obj = ReadonlyDomainExperimentEvidence.from_dict(experiment) if isinstance(experiment, dict) else experiment
        if not isinstance(experiment_obj, ReadonlyDomainExperimentEvidence):
            raise FailClosedRuntimeError("readonly domain experiment lineage entry is invalid")
        artifact = experiment_obj.to_dict()
        if artifact["experiment_id"] in seen_experiment_ids:
            raise FailClosedRuntimeError("readonly domain experiment lineage contains duplicate experiment_id")
        if previous_created_at and artifact["created_at"] < previous_created_at:
            raise FailClosedRuntimeError("readonly domain experiment lineage ordering is not deterministic")
        canonical_serialize(artifact)
        seen_experiment_ids.add(artifact["experiment_id"])
        previous_created_at = artifact["created_at"]
        reconstructed.append(
            {
                "experiment_index": index,
                "experiment_id": artifact["experiment_id"],
                "domain_surface": artifact["domain_surface"],
                "experiment_status": artifact["experiment_status"],
                "evidence_hash": artifact["evidence_hash"],
            }
        )
    lineage = {
        "experiment_count": len(reconstructed),
        "experiments": reconstructed,
        "append_only_valid": True,
        "lineage_valid": True,
        "governance_authority_separated": True,
    }
    lineage["lineage_hash"] = replay_hash(lineage)
    return lineage


def _experiment_rejected(
    experiment_id: str,
    human_request: str,
    demo_evidence_hash: str,
    return_evidence_hash: str,
    reason: str,
    created_at: str,
    demo: dict[str, Any] | None = None,
) -> dict[str, Any]:
    evidence = ReadonlyDomainExperimentEvidence(
        experiment_id=experiment_id,
        domain_name=DOMAIN_NAME,
        domain_surface=DOMAIN_SURFACE,
        human_request=human_request,
        demo_evidence_hash=demo_evidence_hash,
        return_evidence_hash=return_evidence_hash,
        experiment_status=EXPERIMENT_REJECTED,
        experiment_reason=reason,
        created_at=created_at,
    )
    return {
        "experiment_evidence": evidence,
        "domain_name": DOMAIN_NAME,
        "domain_surface": DOMAIN_SURFACE,
        "demo": demo,
        "domain_return": "readonly domain experiment rejected",
        "experiment_lineage": reconstruct_readonly_domain_experiment_lineage([evidence]),
        "governance_authority_separated": True,
    }
