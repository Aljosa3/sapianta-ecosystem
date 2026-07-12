"""Durable governed-work handoff composition for validated Platform plans."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.approval.approval_contract import ApprovalContract
from aigol.runtime.approval.approval_engine import ApprovalEngine
from aigol.runtime.models import AUTHORIZED
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_development_composition_plan import (
    DEVELOPMENT_COMPOSITION_PLAN_FAILED_CLOSED,
    PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_VERSION,
    validate_platform_development_composition_plan,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


PLATFORM_DURABLE_GOVERNED_WORK_VERSION = (
    "G21_05_DURABLE_GOVERNED_WORK_ARTIFACT_RUNTIME_V1"
)
PLATFORM_DURABLE_GOVERNED_WORK_ARTIFACT_V1 = (
    "PLATFORM_DURABLE_GOVERNED_WORK_ARTIFACT_V1"
)

DURABLE_WORK_READY_FOR_REVIEW = "DURABLE_GOVERNED_WORK_READY_FOR_REVIEW"
DURABLE_WORK_NO_IMPLEMENTATION_REQUIRED = (
    "DURABLE_GOVERNED_WORK_NO_IMPLEMENTATION_REQUIRED"
)
DURABLE_WORK_FAILED_CLOSED = "DURABLE_GOVERNED_WORK_FAILED_CLOSED"

BOUNDARY_FLAGS = {
    "read_only": True,
    "platform_core_authority": True,
    "human_interface_authority": False,
    "proposal_only": True,
    "approval_required_before_implementation": True,
    "approval_granted": False,
    "approval_created": False,
    "authorization_created": False,
    "execution_authorized": False,
    "provider_invoked": False,
    "worker_invoked": False,
    "repository_mutated": False,
    "governance_modified": False,
    "replay_modified": False,
}


def compose_durable_governed_work(
    *,
    development_plan_artifact: dict[str, Any],
    project_objective_artifact: dict[str, Any] | None = None,
    source_work_type: str = "AUDIT_ONLY",
    created_at: str = "2026-07-12T00:00:00Z",
    replay_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Convert a validated advisory plan into one reviewable work artifact."""

    try:
        plan = validate_platform_development_composition_plan(development_plan_artifact)
        if plan.get("plan_status") == DEVELOPMENT_COMPOSITION_PLAN_FAILED_CLOSED:
            raise FailClosedRuntimeError("durable governed work failed closed: source plan failed")
        objective = (
            deepcopy(project_objective_artifact)
            if isinstance(project_objective_artifact, dict)
            else {}
        )
        work_id = _stable_work_id(str(plan["artifact_hash"]))
        implementation_required = plan.get("implementation_required") is True
        status = (
            DURABLE_WORK_READY_FOR_REVIEW
            if implementation_required
            else DURABLE_WORK_NO_IMPLEMENTATION_REQUIRED
        )
        approval_evidence = _approval_evidence(
            work_id=work_id,
            created_at=created_at,
            approval_required=implementation_required,
            source_plan_hash=str(plan["artifact_hash"]),
        )
        artifact = _artifact(
            work_id=work_id,
            plan=plan,
            objective=objective,
            source_work_type=source_work_type,
            created_at=created_at,
            status=status,
            implementation_required=implementation_required,
            approval_evidence=approval_evidence,
            failure_reason=None,
        )
    except Exception as exc:
        artifact = _failed_artifact(
            development_plan_artifact=development_plan_artifact,
            source_work_type=source_work_type,
            created_at=created_at,
            failure_reason=str(exc) or "durable governed work failed closed",
        )
    if replay_dir is not None:
        artifact = deepcopy(artifact)
        artifact["replay_reference"] = str(Path(replay_dir))
        artifact["artifact_hash"] = replay_hash(
            {key: value for key, value in artifact.items() if key != "artifact_hash"}
        )
    validate_durable_governed_work(artifact)
    if replay_dir is not None:
        _persist_or_validate(Path(replay_dir), artifact)
    return artifact


def validate_durable_governed_work(artifact: dict[str, Any]) -> dict[str, Any]:
    """Fail closed unless a durable governed-work artifact is canonical."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("durable governed work artifact must be a dict")
    if artifact.get("artifact_type") != PLATFORM_DURABLE_GOVERNED_WORK_ARTIFACT_V1:
        raise FailClosedRuntimeError("durable governed work artifact type is invalid")
    if artifact.get("runtime_version") != PLATFORM_DURABLE_GOVERNED_WORK_VERSION:
        raise FailClosedRuntimeError("durable governed work runtime version is invalid")
    if artifact.get("work_status") not in {
        DURABLE_WORK_READY_FOR_REVIEW,
        DURABLE_WORK_NO_IMPLEMENTATION_REQUIRED,
        DURABLE_WORK_FAILED_CLOSED,
    }:
        raise FailClosedRuntimeError("durable governed work status is invalid")
    for name, expected in BOUNDARY_FLAGS.items():
        if artifact.get(name) is not expected:
            raise FailClosedRuntimeError("durable governed work boundary flags are invalid")
        flags = artifact.get("boundary_flags")
        if not isinstance(flags, dict) or flags.get(name) is not expected:
            raise FailClosedRuntimeError("durable governed work boundary flags are invalid")
    body = deepcopy(artifact)
    actual_hash = body.pop("artifact_hash", None)
    if not isinstance(actual_hash, str) or replay_hash(body) != actual_hash:
        raise FailClosedRuntimeError("durable governed work artifact hash mismatch")
    return deepcopy(artifact)


def reconstruct_durable_governed_work(replay_dir: str | Path) -> dict[str, Any]:
    """Load and validate the immutable durable-work replay wrapper."""

    wrapper = load_json(Path(replay_dir) / "000_durable_governed_work_recorded.json")
    if wrapper.get("replay_index") != 0 or wrapper.get("replay_step") != "durable_governed_work_recorded":
        raise FailClosedRuntimeError("durable governed work replay ordering mismatch")
    wrapper_body = deepcopy(wrapper)
    wrapper_hash = wrapper_body.pop("replay_hash", None)
    if replay_hash(wrapper_body) != wrapper_hash:
        raise FailClosedRuntimeError("durable governed work replay hash mismatch")
    artifact = wrapper.get("artifact")
    validate_durable_governed_work(artifact)
    return deepcopy(artifact)


def _artifact(
    *,
    work_id: str,
    plan: dict[str, Any],
    objective: dict[str, Any],
    source_work_type: str,
    created_at: str,
    status: str,
    implementation_required: bool,
    approval_evidence: dict[str, Any],
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": PLATFORM_DURABLE_GOVERNED_WORK_ARTIFACT_V1,
        "runtime_version": PLATFORM_DURABLE_GOVERNED_WORK_VERSION,
        "governed_work_id": work_id,
        "governed_work_version": 1,
        "work_status": status,
        "created_at": _require_string(created_at, "created_at"),
        "source_work_type": _require_string(source_work_type, "source_work_type"),
        "proposed_next_phase_work_type": (
            "IMPLEMENTATION" if implementation_required else source_work_type
        ),
        "source_development_plan_artifact_type": plan.get("artifact_type"),
        "source_development_plan_runtime_version": (
            PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_VERSION
        ),
        "source_development_plan_hash": plan.get("artifact_hash"),
        "source_project_objective_artifact_type": objective.get("artifact_type"),
        "source_project_objective_hash": objective.get("artifact_hash"),
        "source_request": plan.get("source_request"),
        "source_request_hash": plan.get("source_request_hash"),
        "canonical_project_objective": objective.get("canonical_project_objective"),
        "implementation_required": implementation_required,
        "reusable_certified_capabilities": deepcopy(
            plan.get("reusable_certified_capabilities") or []
        ),
        "reusable_certified_compositions": deepcopy(
            plan.get("reusable_certified_compositions") or []
        ),
        "residual_capability_gaps": deepcopy(plan.get("residual_capability_gaps") or []),
        "minimal_required_platform_extension": deepcopy(
            plan.get("minimal_required_platform_extension") or {}
        ),
        "ordered_implementation_sequence": deepcopy(
            plan.get("ordered_implementation_sequence") or []
        ),
        "required_implementation_work": deepcopy(
            plan.get("required_implementation_work") or []
        ),
        "dependency_graph": deepcopy(plan.get("dependency_graph") or {}),
        "governance_dependencies": deepcopy(plan.get("governance_dependencies") or []),
        "certification_dependencies": deepcopy(
            plan.get("certification_dependencies") or []
        ),
        "replay_dependencies": deepcopy(plan.get("replay_dependencies") or []),
        "validation_requirements": deepcopy(plan.get("validation_requirements") or []),
        "implementation_boundary": deepcopy(plan.get("implementation_boundary") or {}),
        "review_state": "PENDING_HUMAN_REVIEW" if implementation_required else "REVIEW_NOT_REQUIRED",
        "approval_contract": deepcopy(approval_evidence["approval_contract"]),
        "approval_request": deepcopy(approval_evidence["approval_request"]),
        "approval_result": deepcopy(approval_evidence["approval_result"]),
        "approval_validation": deepcopy(approval_evidence["approval_validation"]),
        "approval_request_id": approval_evidence["approval_request"]["approval_request_id"],
        "approval_request_hash": approval_evidence["approval_request"]["replay_hash"],
        "approval_request_ready": implementation_required,
        "approval_contract_reused": True,
        "proposal_contract_compatibility": {
            "proposal_type": "CAPABILITY_PROPOSAL",
            "proposal_source": "COMBINED",
            "proposal_text": _proposal_text(plan),
            "created_by": "AIGOL",
            "authority": False,
        },
        "downstream_contract_target": "PROPOSAL_RUNTIME_V1",
        "execution_authorization_required_separately": implementation_required,
        "supersedes_governed_work_id": None,
        "canceled": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
        "reused_platform_core_services": [
            "PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_RUNTIME",
            "PROPOSAL_RUNTIME_V1",
            "APPROVAL_REQUEST_CONTRACT",
            "EXECUTION_AUTHORIZATION_RUNTIME",
            "PLATFORM_CORE_REPLAY",
            "GENERATION_CERTIFICATION_COMPOSITION_SERVICE",
        ],
        "boundary_flags": deepcopy(BOUNDARY_FLAGS),
        **BOUNDARY_FLAGS,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_artifact(
    *,
    development_plan_artifact: dict[str, Any],
    source_work_type: str,
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    source = development_plan_artifact if isinstance(development_plan_artifact, dict) else {}
    return _artifact(
        work_id=_stable_work_id(str(source.get("artifact_hash") or replay_hash(source))),
        plan={
            "artifact_type": source.get("artifact_type"),
            "artifact_hash": source.get("artifact_hash"),
            "source_request": source.get("source_request"),
            "source_request_hash": source.get("source_request_hash"),
        },
        objective={},
        source_work_type=source_work_type or "UNSPECIFIED",
        created_at=created_at,
        status=DURABLE_WORK_FAILED_CLOSED,
        implementation_required=False,
        approval_evidence=_approval_evidence(
            work_id="FAILED-DURABLE-WORK",
            created_at=created_at,
            approval_required=False,
            source_plan_hash=str(source.get("artifact_hash") or replay_hash(source)),
        ),
        failure_reason=failure_reason,
    )


def _approval_evidence(
    *, work_id: str, created_at: str, approval_required: bool, source_plan_hash: str
) -> dict[str, Any]:
    contract = ApprovalContract(
        approval_contract_id=f"{work_id}:APPROVAL-CONTRACT",
        runtime_id=PLATFORM_DURABLE_GOVERNED_WORK_VERSION,
        goal_id=work_id,
        requested_capability="REVIEW_DURABLE_GOVERNED_WORK",
        execution_surface="PROPOSAL_REVIEW_ONLY",
        approval_scope=("HUMAN_APPROVAL_REQUIRED" if approval_required else "READ_ONLY_AUTO_ALLOWED"),
        governance_state=AUTHORIZED,
        lineage_refs=[source_plan_hash],
        created_at=_require_string(created_at, "created_at"),
    )
    request, result, validation = ApprovalEngine().evaluate(contract)
    return {
        "approval_contract": contract.to_dict(),
        "approval_request": request.to_dict(),
        "approval_result": result.to_dict(),
        "approval_validation": validation,
    }


def _proposal_text(plan: dict[str, Any]) -> str:
    sequence = ", ".join(str(item) for item in plan.get("ordered_implementation_sequence") or [])
    return (
        "Governed implementation proposal derived from Development Composition Plan. "
        f"Ordered work: {sequence or 'no implementation work required'}."
    )


def _stable_work_id(plan_hash: str) -> str:
    value = _require_string(plan_hash, "source_development_plan_hash")
    digest = value.split(":", 1)[-1]
    return f"PLATFORM-GOVERNED-WORK-{digest[:24].upper()}"


def _persist_or_validate(replay_dir: Path, artifact: dict[str, Any]) -> None:
    path = replay_dir / "000_durable_governed_work_recorded.json"
    if path.exists():
        existing = reconstruct_durable_governed_work(replay_dir)
        if existing.get("artifact_hash") != artifact.get("artifact_hash"):
            raise FailClosedRuntimeError("durable governed work replay identity collision")
        return
    wrapper = {
        "replay_index": 0,
        "replay_step": "durable_governed_work_recorded",
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(path, wrapper)


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


__all__ = [
    "DURABLE_WORK_FAILED_CLOSED",
    "DURABLE_WORK_NO_IMPLEMENTATION_REQUIRED",
    "DURABLE_WORK_READY_FOR_REVIEW",
    "PLATFORM_DURABLE_GOVERNED_WORK_ARTIFACT_V1",
    "PLATFORM_DURABLE_GOVERNED_WORK_VERSION",
    "compose_durable_governed_work",
    "reconstruct_durable_governed_work",
    "validate_durable_governed_work",
]
