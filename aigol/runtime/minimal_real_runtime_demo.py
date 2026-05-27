"""Minimal operational demo for governed OpenAI-to-metadata execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from aigol.runtime.governed_return_interpretation import ACCEPTED, interpret_governed_execution_return
from aigol.runtime.live_openai_runtime_connector import NORMALIZED, invoke_live_openai_runtime_connector
from aigol.runtime.minimal_governed_execution_path import EXECUTED, execute_minimal_governed_path
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.production_isolation_foundation import ISOLATED, validate_production_isolation
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


COMPLETED = "COMPLETED"
REJECTED = "REJECTED"
ALLOWED_DEMO_STATUSES = frozenset({COMPLETED, REJECTED})


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _demo_hash_input(evidence: "MinimalRealRuntimeDemoEvidence") -> dict[str, Any]:
    return {
        "demo_id": evidence.demo_id,
        "human_request": evidence.human_request,
        "connector_evidence_hash": evidence.connector_evidence_hash,
        "execution_evidence_hash": evidence.execution_evidence_hash,
        "return_evidence_hash": evidence.return_evidence_hash,
        "demo_status": evidence.demo_status,
        "demo_reason": evidence.demo_reason,
        "created_at": evidence.created_at,
    }


@dataclass(frozen=True)
class MinimalRealRuntimeDemoEvidence:
    """Immutable replay-visible demo evidence."""

    demo_id: str
    human_request: str
    connector_evidence_hash: str
    execution_evidence_hash: str
    return_evidence_hash: str
    demo_status: str
    demo_reason: str
    created_at: str
    evidence_hash: str = ""

    def __post_init__(self) -> None:
        _require_string(self.demo_id, "demo_id")
        _require_string(self.human_request, "human_request")
        _require_string(self.demo_reason, "demo_reason")
        _require_string(self.created_at, "created_at")
        if self.demo_status not in ALLOWED_DEMO_STATUSES:
            raise FailClosedRuntimeError("demo status must be COMPLETED or REJECTED")
        expected_hash = replay_hash(_demo_hash_input(self))
        if self.evidence_hash and self.evidence_hash != expected_hash:
            raise FailClosedRuntimeError("minimal real runtime demo evidence hash mismatch")
        object.__setattr__(self, "evidence_hash", self.evidence_hash or expected_hash)

    def to_dict(self) -> dict[str, Any]:
        return {
            "demo_id": self.demo_id,
            "human_request": self.human_request,
            "connector_evidence_hash": self.connector_evidence_hash,
            "execution_evidence_hash": self.execution_evidence_hash,
            "return_evidence_hash": self.return_evidence_hash,
            "demo_status": self.demo_status,
            "demo_reason": self.demo_reason,
            "created_at": self.created_at,
            "evidence_hash": self.evidence_hash,
        }

    @classmethod
    def from_dict(cls, evidence: dict[str, Any]) -> "MinimalRealRuntimeDemoEvidence":
        if not isinstance(evidence, dict):
            raise FailClosedRuntimeError("minimal real runtime demo evidence must be a JSON object")
        required = {
            "demo_id",
            "human_request",
            "connector_evidence_hash",
            "execution_evidence_hash",
            "return_evidence_hash",
            "demo_status",
            "demo_reason",
            "created_at",
            "evidence_hash",
        }
        if set(evidence) != required:
            raise FailClosedRuntimeError("minimal real runtime demo evidence has malformed structure")
        return cls(**evidence)


def run_minimal_real_runtime_demo(
    *,
    demo_id: str,
    human_request: str,
    openai_call: Callable[[dict[str, Any]], Any],
    created_at: str,
) -> dict[str, Any]:
    """Run one bounded OpenAI proposal through the existing governed metadata path."""

    try:
        _require_string(demo_id, "demo_id")
        normalized_human_request = " ".join(_require_string(human_request, "human_request").split())
        _require_string(created_at, "created_at")
        connector = invoke_live_openai_runtime_connector(
            inference_id=f"{demo_id}:OPENAI",
            prompt=normalized_human_request,
            openai_call=openai_call,
            created_at=created_at,
        )
        connector_evidence = connector["connector_evidence"]
        if connector_evidence.connector_status != NORMALIZED:
            return _demo_rejected(
                demo_id,
                normalized_human_request,
                connector_evidence.evidence_hash,
                "",
                "",
                "OpenAI proposal normalization rejected",
                created_at,
                connector,
            )
        proposal_payload = connector["external_model_response"]["proposal_payload"]
        execution = execute_minimal_governed_path(
            execution_id=f"{demo_id}:EXECUTION",
            llm_proposal_input=proposal_payload,
            created_at=created_at,
        )
        execution_result = execution["execution_result"]
        if execution_result.execution_status != EXECUTED:
            return _demo_rejected(
                demo_id,
                normalized_human_request,
                connector_evidence.evidence_hash,
                execution_result.evidence_hash,
                "",
                "governed execution rejected",
                created_at,
                connector,
                execution,
            )
        isolation = validate_production_isolation(
            isolation_id=f"{demo_id}:ISOLATION",
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
            return_id=f"{demo_id}:RETURN",
            execution_result=execution_result,
            provider_evidence=execution["provider_evidence"],
            session_lineage=execution["session_lineage"],
            isolation_evidence=isolation,
            created_at=created_at,
        )
        if isolation.isolation_status != ISOLATED or governed_return.return_status != ACCEPTED:
            return _demo_rejected(
                demo_id,
                normalized_human_request,
                connector_evidence.evidence_hash,
                execution_result.evidence_hash,
                governed_return.evidence_hash,
                "governed return rejected",
                created_at,
                connector,
                execution,
                isolation,
                governed_return,
            )
        evidence = MinimalRealRuntimeDemoEvidence(
            demo_id=demo_id,
            human_request=normalized_human_request,
            connector_evidence_hash=connector_evidence.evidence_hash,
            execution_evidence_hash=execution_result.evidence_hash,
            return_evidence_hash=governed_return.evidence_hash,
            demo_status=COMPLETED,
            demo_reason="minimal real runtime demo completed through readonly metadata governance",
            created_at=created_at,
        )
        demo_lineage = reconstruct_minimal_real_runtime_demo_lineage([evidence])
        return {
            "demo_evidence": evidence,
            "connector": connector,
            "execution": execution,
            "isolation": isolation,
            "governed_return": governed_return,
            "return_display": governed_return.normalized_return_summary,
            "demo_lineage": demo_lineage,
            "governance_authority_separated": True,
        }
    except (FailClosedRuntimeError, TypeError, ValueError, KeyError):
        return _demo_rejected(
            demo_id if isinstance(demo_id, str) and demo_id else "DEMO-INVALID",
            human_request if isinstance(human_request, str) and human_request else "REQUEST-INVALID",
            "",
            "",
            "",
            "minimal real runtime demo failed closed",
            created_at if isinstance(created_at, str) and created_at else "1970-01-01T00:00:00+00:00",
        )


def reconstruct_minimal_real_runtime_demo_lineage(
    demos: list[MinimalRealRuntimeDemoEvidence | dict[str, Any]]
    | tuple[MinimalRealRuntimeDemoEvidence | dict[str, Any], ...],
) -> dict[str, Any]:
    if not isinstance(demos, list | tuple):
        raise FailClosedRuntimeError("minimal real runtime demo lineage must be a list")
    reconstructed = []
    seen_demo_ids: set[str] = set()
    previous_created_at = ""
    for index, demo in enumerate(demos):
        demo_obj = MinimalRealRuntimeDemoEvidence.from_dict(demo) if isinstance(demo, dict) else demo
        if not isinstance(demo_obj, MinimalRealRuntimeDemoEvidence):
            raise FailClosedRuntimeError("minimal real runtime demo lineage entry is invalid")
        artifact = demo_obj.to_dict()
        if artifact["demo_id"] in seen_demo_ids:
            raise FailClosedRuntimeError("minimal real runtime demo lineage contains duplicate demo_id")
        if previous_created_at and artifact["created_at"] < previous_created_at:
            raise FailClosedRuntimeError("minimal real runtime demo lineage ordering is not deterministic")
        canonical_serialize(artifact)
        seen_demo_ids.add(artifact["demo_id"])
        previous_created_at = artifact["created_at"]
        reconstructed.append(
            {
                "demo_index": index,
                "demo_id": artifact["demo_id"],
                "demo_status": artifact["demo_status"],
                "evidence_hash": artifact["evidence_hash"],
            }
        )
    lineage = {
        "demo_count": len(reconstructed),
        "demos": reconstructed,
        "append_only_valid": True,
        "lineage_valid": True,
        "governance_authority_separated": True,
    }
    lineage["lineage_hash"] = replay_hash(lineage)
    return lineage


def _demo_rejected(
    demo_id: str,
    human_request: str,
    connector_evidence_hash: str,
    execution_evidence_hash: str,
    return_evidence_hash: str,
    reason: str,
    created_at: str,
    connector: dict[str, Any] | None = None,
    execution: dict[str, Any] | None = None,
    isolation: Any = None,
    governed_return: Any = None,
) -> dict[str, Any]:
    evidence = MinimalRealRuntimeDemoEvidence(
        demo_id=demo_id,
        human_request=human_request,
        connector_evidence_hash=connector_evidence_hash,
        execution_evidence_hash=execution_evidence_hash,
        return_evidence_hash=return_evidence_hash,
        demo_status=REJECTED,
        demo_reason=reason,
        created_at=created_at,
    )
    return {
        "demo_evidence": evidence,
        "connector": connector,
        "execution": execution,
        "isolation": isolation,
        "governed_return": governed_return,
        "return_display": "minimal real runtime demo rejected",
        "demo_lineage": reconstruct_minimal_real_runtime_demo_lineage([evidence]),
        "governance_authority_separated": True,
    }
