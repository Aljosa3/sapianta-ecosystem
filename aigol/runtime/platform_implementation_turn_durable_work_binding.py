"""Bind one canonical implementation turn to existing durable governed work."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_composition_coverage import (
    COVERAGE_FAILED_CLOSED,
    COVERAGE_PARTIAL,
    GENUINELY_NEW_CAPABILITY_REQUIRED,
    MINIMAL_COMPOSITION_SERVICE_REQUIRED,
    discover_platform_capability_composition_coverage,
    validate_platform_capability_composition_coverage,
)
from aigol.runtime.platform_development_composition_plan import (
    DEVELOPMENT_COMPOSITION_PLAN_FAILED_CLOSED,
    compose_platform_development_plan,
    validate_platform_development_composition_plan,
)
from aigol.runtime.platform_durable_governed_work import (
    DURABLE_WORK_READY_FOR_REVIEW,
    compose_durable_governed_work,
    validate_durable_governed_work,
)
from aigol.runtime.platform_knowledge_runtime import validate_platform_knowledge_response
from aigol.runtime.platform_project_objective_inference import (
    validate_platform_project_objective,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


PLATFORM_IMPLEMENTATION_TURN_DURABLE_WORK_BINDING_VERSION = (
    "G31_04_CANONICAL_IMPLEMENTATION_TURN_TO_DURABLE_GOVERNED_WORK_BINDING_V1"
)
PLATFORM_IMPLEMENTATION_TURN_DURABLE_WORK_BINDING_ARTIFACT_V1 = (
    "PLATFORM_IMPLEMENTATION_TURN_DURABLE_WORK_BINDING_ARTIFACT_V1"
)
PLATFORM_IMPLEMENTATION_TURN_PROPOSAL_PREVIEW_ARTIFACT_V1 = (
    "PLATFORM_IMPLEMENTATION_TURN_PROPOSAL_PREVIEW_ARTIFACT_V1"
)
PLATFORM_IMPLEMENTATION_TURN_APPROVAL_CONSUMPTION_ARTIFACT_V1 = (
    "PLATFORM_IMPLEMENTATION_TURN_APPROVAL_CONSUMPTION_ARTIFACT_V1"
)

IMPLEMENTATION_TURN_READY_FOR_APPROVAL = "IMPLEMENTATION_TURN_READY_FOR_APPROVAL"
IMPLEMENTATION_TURN_UNRESOLVED_SCOPE_FAILED_CLOSED = (
    "IMPLEMENTATION_TURN_UNRESOLVED_SCOPE_FAILED_CLOSED"
)
IMPLEMENTATION_TURN_APPROVED_IDENTITIES_CONSUMED = (
    "IMPLEMENTATION_TURN_APPROVED_IDENTITIES_CONSUMED"
)

BOUNDARY_FLAGS = {
    "platform_core_authority": True,
    "human_interface_authority": False,
    "human_interface_semantic_authority": False,
    "human_interface_planning_authority": False,
    "human_interface_approval_authority": False,
    "human_interface_execution_authority": False,
    "provider_invoked": False,
    "worker_invoked": False,
    "execution_authorized": False,
    "repository_mutated": False,
    "validation_executed": False,
    "certification_reached": False,
    "replay_visible": True,
}


def compose_implementation_turn_durable_work_binding(
    *,
    request: str,
    project_objective_artifact: dict[str, Any],
    knowledge_reuse_artifact: dict[str, Any],
    workspace_state: dict[str, Any] | None,
    workspace: str | Path,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Compose existing coverage, plan, and durable-work artifacts before approval."""

    raw_request = _require_string(request, "request")
    objective = validate_platform_project_objective(project_objective_artifact)
    knowledge_reuse = _validate_hash_bound_snapshot(
        knowledge_reuse_artifact,
        "knowledge_reuse_artifact",
    )
    workspace_path = Path(workspace)
    coverage = discover_platform_capability_composition_coverage(
        query=raw_request,
        workspace_state=workspace_state,
        governance_root=workspace_path,
        created_at=created_at,
    )
    if (
        coverage.get("coverage_status") == COVERAGE_FAILED_CLOSED
        and _bounded_project_capability_gap_evidence(
            knowledge_reuse=knowledge_reuse,
            coverage=coverage,
        )
    ):
        coverage = _project_capability_gap_coverage_projection(coverage)
    elif (
        coverage.get("minimal_required_platform_extension", {}).get("required")
        is not True
        and knowledge_reuse.get("new_work_required") is True
    ):
        coverage = _project_required_extension_gap(
            coverage,
            knowledge_reuse=knowledge_reuse,
        )
    validate_platform_capability_composition_coverage(coverage)
    plan = compose_platform_development_plan(
        capability_coverage_artifact=coverage,
        created_at=created_at,
    )
    validate_platform_development_composition_plan(plan)
    durable_dir = Path(replay_dir) / "durable_governed_work"
    durable = compose_durable_governed_work(
        development_plan_artifact=plan,
        project_objective_artifact=objective,
        source_work_type="IMPLEMENTATION",
        created_at=created_at,
        replay_dir=durable_dir,
    )
    validate_durable_governed_work(durable)
    platform_knowledge = coverage.get("platform_knowledge_response")
    if not isinstance(platform_knowledge, dict):
        raise FailClosedRuntimeError(
            "implementation turn durable-work binding failed closed: Platform Knowledge missing"
        )
    validate_platform_knowledge_response(platform_knowledge)
    repository_context = _repository_context(
        workspace=workspace_path,
        project_objective=objective,
        knowledge_reuse=knowledge_reuse,
        coverage=coverage,
    )
    ready = (
        coverage.get("coverage_status") != COVERAGE_FAILED_CLOSED
        and plan.get("plan_status") != DEVELOPMENT_COMPOSITION_PLAN_FAILED_CLOSED
        and plan.get("implementation_required") is True
        and durable.get("work_status") == DURABLE_WORK_READY_FOR_REVIEW
    )
    preview = _proposal_preview(
        request=raw_request,
        objective=objective,
        knowledge_reuse=knowledge_reuse,
        platform_knowledge=platform_knowledge,
        coverage=coverage,
        plan=plan,
        durable=durable,
        repository_context=repository_context,
        created_at=created_at,
        ready=ready,
    )
    status = (
        IMPLEMENTATION_TURN_READY_FOR_APPROVAL
        if ready
        else IMPLEMENTATION_TURN_UNRESOLVED_SCOPE_FAILED_CLOSED
    )
    failure_reason = None
    if not ready:
        failure_reason = _failure_reason(coverage=coverage, plan=plan, durable=durable)
    artifact = {
        "artifact_type": PLATFORM_IMPLEMENTATION_TURN_DURABLE_WORK_BINDING_ARTIFACT_V1,
        "runtime_version": PLATFORM_IMPLEMENTATION_TURN_DURABLE_WORK_BINDING_VERSION,
        "binding_status": status,
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": str(Path(replay_dir)),
        "original_request": raw_request,
        "original_request_hash": replay_hash(raw_request),
        "project_objective_artifact": deepcopy(objective),
        "project_objective_hash": objective["artifact_hash"],
        "knowledge_reuse_artifact": deepcopy(knowledge_reuse),
        "knowledge_reuse_hash": _snapshot_hash(knowledge_reuse),
        "platform_knowledge_artifact": deepcopy(platform_knowledge),
        "platform_knowledge_hash": platform_knowledge["artifact_hash"],
        "capability_composition_coverage_artifact": deepcopy(coverage),
        "capability_composition_coverage_hash": coverage["artifact_hash"],
        "development_composition_plan_artifact": deepcopy(plan),
        "development_composition_plan_hash": plan["artifact_hash"],
        "durable_governed_work_artifact": deepcopy(durable),
        "durable_governed_work_hash": durable["artifact_hash"],
        "durable_governed_work_id": durable["governed_work_id"],
        "proposal_preview_artifact": deepcopy(preview),
        "proposal_preview_hash": preview["artifact_hash"],
        "approval_request": deepcopy(durable["approval_request"]),
        "approval_request_id": durable["approval_request_id"],
        "approval_request_hash": durable["approval_request_hash"],
        "repository_context": repository_context,
        "approval_required": ready,
        "approval_granted": False,
        "approval_is_execution_authorization": False,
        "generic_marker_fallback_used": False,
        "existing_planning_runtime_reused": True,
        "existing_durable_work_runtime_reused": True,
        "failure_reason": failure_reason,
        **BOUNDARY_FLAGS,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    validate_implementation_turn_durable_work_binding(artifact)
    _persist_binding(Path(replay_dir), artifact)
    return deepcopy(artifact)


def validate_implementation_turn_durable_work_binding(
    artifact: dict[str, Any],
    *,
    require_ready: bool = False,
) -> dict[str, Any]:
    """Fail closed unless every nested identity in the binding is unchanged."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("implementation turn durable-work binding must be a dict")
    candidate = deepcopy(artifact)
    if candidate.get("artifact_type") != (
        PLATFORM_IMPLEMENTATION_TURN_DURABLE_WORK_BINDING_ARTIFACT_V1
    ):
        raise FailClosedRuntimeError("implementation turn durable-work binding type is invalid")
    if candidate.get("runtime_version") != (
        PLATFORM_IMPLEMENTATION_TURN_DURABLE_WORK_BINDING_VERSION
    ):
        raise FailClosedRuntimeError("implementation turn durable-work binding version is invalid")
    if candidate.get("binding_status") not in {
        IMPLEMENTATION_TURN_READY_FOR_APPROVAL,
        IMPLEMENTATION_TURN_UNRESOLVED_SCOPE_FAILED_CLOSED,
    }:
        raise FailClosedRuntimeError("implementation turn durable-work binding status is invalid")
    if require_ready and candidate.get("binding_status") != IMPLEMENTATION_TURN_READY_FOR_APPROVAL:
        raise FailClosedRuntimeError("implementation turn durable-work binding is not approval ready")
    for field, expected in BOUNDARY_FLAGS.items():
        if candidate.get(field) is not expected:
            raise FailClosedRuntimeError(
                f"implementation turn durable-work boundary flag invalid: {field}"
            )
    _require_string(candidate.get("replay_reference"), "replay_reference")
    objective = validate_platform_project_objective(candidate.get("project_objective_artifact"))
    knowledge_reuse = _validate_hash_bound_snapshot(
        candidate.get("knowledge_reuse_artifact"),
        "knowledge_reuse_artifact",
    )
    platform_knowledge = validate_platform_knowledge_response(
        candidate.get("platform_knowledge_artifact")
    )
    coverage = validate_platform_capability_composition_coverage(
        candidate.get("capability_composition_coverage_artifact")
    )
    plan = validate_platform_development_composition_plan(
        candidate.get("development_composition_plan_artifact")
    )
    durable = validate_durable_governed_work(
        candidate.get("durable_governed_work_artifact")
    )
    preview = validate_implementation_turn_proposal_preview(
        candidate.get("proposal_preview_artifact")
    )
    expected = {
        "project_objective_hash": objective["artifact_hash"],
        "knowledge_reuse_hash": _snapshot_hash(knowledge_reuse),
        "platform_knowledge_hash": platform_knowledge["artifact_hash"],
        "capability_composition_coverage_hash": coverage["artifact_hash"],
        "development_composition_plan_hash": plan["artifact_hash"],
        "durable_governed_work_hash": durable["artifact_hash"],
        "durable_governed_work_id": durable["governed_work_id"],
        "proposal_preview_hash": preview["artifact_hash"],
        "approval_request_id": durable["approval_request_id"],
        "approval_request_hash": durable["approval_request_hash"],
    }
    for field, value in expected.items():
        if candidate.get(field) != value:
            raise FailClosedRuntimeError(
                f"implementation turn durable-work identity mismatch: {field}"
            )
    if coverage.get("platform_knowledge_response_hash") != platform_knowledge["artifact_hash"]:
        raise FailClosedRuntimeError("implementation turn Platform Knowledge lineage mismatch")
    if plan.get("capability_coverage_hash") != coverage["artifact_hash"]:
        raise FailClosedRuntimeError("implementation turn capability coverage lineage mismatch")
    if durable.get("source_development_plan_hash") != plan["artifact_hash"]:
        raise FailClosedRuntimeError("implementation turn source-plan lineage mismatch")
    if (
        candidate.get("binding_status") == IMPLEMENTATION_TURN_READY_FOR_APPROVAL
        and durable.get("source_project_objective_hash") != objective["artifact_hash"]
    ):
        raise FailClosedRuntimeError("implementation turn Project Objective lineage mismatch")
    _validate_preview_lineage(preview=preview, candidate=candidate)
    body = deepcopy(candidate)
    actual_hash = body.pop("artifact_hash", None)
    if replay_hash(body) != actual_hash:
        raise FailClosedRuntimeError("implementation turn durable-work binding hash mismatch")
    return candidate


def validate_implementation_turn_proposal_preview(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("implementation turn proposal preview must be a dict")
    candidate = deepcopy(artifact)
    if candidate.get("artifact_type") != (
        PLATFORM_IMPLEMENTATION_TURN_PROPOSAL_PREVIEW_ARTIFACT_V1
    ):
        raise FailClosedRuntimeError("implementation turn proposal preview type is invalid")
    if candidate.get("runtime_version") != (
        PLATFORM_IMPLEMENTATION_TURN_DURABLE_WORK_BINDING_VERSION
    ):
        raise FailClosedRuntimeError("implementation turn proposal preview version is invalid")
    if candidate.get("proposal_only") is not True:
        raise FailClosedRuntimeError("implementation turn proposal preview must be proposal only")
    if candidate.get("human_interface_authority") is not False:
        raise FailClosedRuntimeError("implementation turn proposal preview authority is invalid")
    body = deepcopy(candidate)
    actual_hash = body.pop("artifact_hash", None)
    if replay_hash(body) != actual_hash:
        raise FailClosedRuntimeError("implementation turn proposal preview hash mismatch")
    return candidate


def consume_approved_implementation_turn_binding(
    *,
    binding_artifact: dict[str, Any],
    development_composition_plan_hash: str,
    durable_governed_work_hash: str,
    proposal_preview_hash: str,
    approval_request_hash: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Record that canonical continuation consumed the exact approved identities."""

    binding = validate_implementation_turn_durable_work_binding(
        binding_artifact,
        require_ready=True,
    )
    supplied = {
        "development_composition_plan_hash": _require_string(
            development_composition_plan_hash,
            "development_composition_plan_hash",
        ),
        "durable_governed_work_hash": _require_string(
            durable_governed_work_hash,
            "durable_governed_work_hash",
        ),
        "proposal_preview_hash": _require_string(
            proposal_preview_hash,
            "proposal_preview_hash",
        ),
        "approval_request_hash": _require_string(
            approval_request_hash,
            "approval_request_hash",
        ),
    }
    for field, value in supplied.items():
        if binding.get(field) != value:
            raise FailClosedRuntimeError(
                f"approved implementation turn identity mismatch: {field}"
            )
    artifact = {
        "artifact_type": PLATFORM_IMPLEMENTATION_TURN_APPROVAL_CONSUMPTION_ARTIFACT_V1,
        "runtime_version": PLATFORM_IMPLEMENTATION_TURN_DURABLE_WORK_BINDING_VERSION,
        "consumption_status": IMPLEMENTATION_TURN_APPROVED_IDENTITIES_CONSUMED,
        "created_at": _require_string(created_at, "created_at"),
        "binding_hash": binding["artifact_hash"],
        "project_objective_hash": binding["project_objective_hash"],
        "knowledge_reuse_hash": binding["knowledge_reuse_hash"],
        "platform_knowledge_hash": binding["platform_knowledge_hash"],
        "capability_composition_coverage_hash": binding[
            "capability_composition_coverage_hash"
        ],
        **supplied,
        "approval_request_id": binding["approval_request_id"],
        "durable_governed_work_id": binding["durable_governed_work_id"],
        "human_approval_recorded": True,
        "approval_is_execution_authorization": False,
        "canonical_continuation_may_enter": True,
        **BOUNDARY_FLAGS,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    validate_implementation_turn_approval_consumption(artifact)
    _persist_consumption(Path(replay_dir), artifact)
    return deepcopy(artifact)


def validate_implementation_turn_approval_consumption(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("implementation turn approval consumption must be a dict")
    candidate = deepcopy(artifact)
    if candidate.get("artifact_type") != (
        PLATFORM_IMPLEMENTATION_TURN_APPROVAL_CONSUMPTION_ARTIFACT_V1
    ):
        raise FailClosedRuntimeError("implementation turn approval consumption type is invalid")
    if candidate.get("runtime_version") != (
        PLATFORM_IMPLEMENTATION_TURN_DURABLE_WORK_BINDING_VERSION
    ):
        raise FailClosedRuntimeError("implementation turn approval consumption version is invalid")
    if candidate.get("consumption_status") != IMPLEMENTATION_TURN_APPROVED_IDENTITIES_CONSUMED:
        raise FailClosedRuntimeError("implementation turn approval consumption status is invalid")
    if candidate.get("human_approval_recorded") is not True:
        raise FailClosedRuntimeError("implementation turn human approval is missing")
    for field, expected in BOUNDARY_FLAGS.items():
        if candidate.get(field) is not expected:
            raise FailClosedRuntimeError(
                f"implementation turn approval boundary flag invalid: {field}"
            )
    body = deepcopy(candidate)
    actual_hash = body.pop("artifact_hash", None)
    if replay_hash(body) != actual_hash:
        raise FailClosedRuntimeError("implementation turn approval consumption hash mismatch")
    return candidate


def reconstruct_implementation_turn_durable_work_binding(
    replay_dir: str | Path,
) -> dict[str, Any]:
    wrapper = load_json(Path(replay_dir) / "000_implementation_turn_binding_recorded.json")
    _validate_wrapper(wrapper, index=0, step="implementation_turn_binding_recorded")
    return validate_implementation_turn_durable_work_binding(wrapper["artifact"])


def reconstruct_implementation_turn_approval_consumption(
    replay_dir: str | Path,
) -> dict[str, Any]:
    wrapper = load_json(Path(replay_dir) / "001_implementation_turn_approval_consumed.json")
    _validate_wrapper(wrapper, index=1, step="implementation_turn_approval_consumed")
    return validate_implementation_turn_approval_consumption(wrapper["artifact"])


def _proposal_preview(
    *,
    request: str,
    objective: dict[str, Any],
    knowledge_reuse: dict[str, Any],
    platform_knowledge: dict[str, Any],
    coverage: dict[str, Any],
    plan: dict[str, Any],
    durable: dict[str, Any],
    repository_context: dict[str, Any],
    created_at: str,
    ready: bool,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": PLATFORM_IMPLEMENTATION_TURN_PROPOSAL_PREVIEW_ARTIFACT_V1,
        "runtime_version": PLATFORM_IMPLEMENTATION_TURN_DURABLE_WORK_BINDING_VERSION,
        "preview_status": "PROPOSAL_PREVIEW_READY" if ready else "PROPOSAL_SCOPE_UNRESOLVED",
        "created_at": created_at,
        "original_human_goal": request,
        "canonical_project_objective": objective.get("canonical_project_objective"),
        "project_objective_hash": objective["artifact_hash"],
        "project_knowledge_summary": platform_knowledge.get("project_knowledge_summary"),
        "platform_knowledge_hash": platform_knowledge["artifact_hash"],
        "knowledge_reuse_classification": knowledge_reuse.get("classification"),
        "knowledge_reuse_recommended": knowledge_reuse.get("reuse_recommended") is True,
        "knowledge_reuse_hash": _snapshot_hash(knowledge_reuse),
        "existing_relevant_capabilities": deepcopy(plan.get("reusable_certified_capabilities") or []),
        "existing_relevant_compositions": deepcopy(plan.get("reusable_certified_compositions") or []),
        "residual_implementation_gaps": deepcopy(plan.get("residual_capability_gaps") or []),
        "bounded_work_scope": deepcopy(plan.get("minimal_required_platform_extension") or {}),
        "ordered_implementation_sequence": deepcopy(plan.get("ordered_implementation_sequence") or []),
        "required_implementation_work": deepcopy(plan.get("required_implementation_work") or []),
        "repository_scope_status": repository_context["repository_scope_status"],
        "proposed_repository_paths": [],
        "repository_scope_explanation": repository_context["repository_scope_explanation"],
        "focused_tests": [
            item
            for item in plan.get("validation_requirements") or []
            if "FOCUSED" in str(item)
        ],
        "validation_requirements": deepcopy(plan.get("validation_requirements") or []),
        "governance_dependencies": deepcopy(plan.get("governance_dependencies") or []),
        "replay_requirements": deepcopy(plan.get("replay_dependencies") or []),
        "certification_requirements": deepcopy(plan.get("certification_dependencies") or []),
        "approval_meaning": "Approve review of this exact immutable proposal for canonical continuation.",
        "approval_is_execution_authorization": False,
        "development_composition_plan_hash": plan["artifact_hash"],
        "durable_governed_work_id": durable["governed_work_id"],
        "durable_governed_work_hash": durable["artifact_hash"],
        "approval_request_id": durable["approval_request_id"],
        "approval_request_hash": durable["approval_request_hash"],
        "proposal_only": True,
        "generic_marker_fallback_used": False,
        "human_interface_authority": False,
        "execution_authorized": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "repository_mutated": False,
        "validation_executed": False,
        "certification_reached": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _repository_context(
    *,
    workspace: Path,
    project_objective: dict[str, Any],
    knowledge_reuse: dict[str, Any],
    coverage: dict[str, Any],
) -> dict[str, Any]:
    artifact = {
        "workspace": str(workspace),
        "workspace_exists": workspace.exists(),
        "git_directory_present": (workspace / ".git").exists(),
        "project_objective_hash": project_objective["artifact_hash"],
        "knowledge_reuse_hash": _snapshot_hash(knowledge_reuse),
        "capability_composition_coverage_hash": coverage["artifact_hash"],
        "repository_scope_status": "UNRESOLVED_WITHIN_CANONICAL_CAPABILITY_BOUNDARY",
        "repository_scope_explanation": (
            "Canonical capability scope is bounded; exact repository paths are deferred "
            "and were not invented by Platform Core or AiCLI."
        ),
        "invented_repository_paths": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _bounded_project_capability_gap_evidence(
    *, knowledge_reuse: dict[str, Any], coverage: dict[str, Any]
) -> bool:
    discovery = coverage.get("candidate_capability_discovery")
    decisions = {
        str(knowledge_reuse.get("capability_resolution_decision") or ""),
        str(
            discovery.get("capability_resolution_decision")
            if isinstance(discovery, dict)
            else ""
        ),
    }
    return bool(
        decisions.intersection({"NEW_CAPABILITY", "EXTENDS_EXISTING_CAPABILITY"})
    )


def _project_capability_gap_coverage_projection(
    coverage: dict[str, Any],
) -> dict[str, Any]:
    """Project an existing NEW_CAPABILITY decision into the existing gap contract."""

    projected = deepcopy(coverage)
    source_hash = projected.get("artifact_hash")
    discovery = projected.get("candidate_capability_discovery")
    decision = str(
        discovery.get("capability_resolution_decision")
        if isinstance(discovery, dict)
        else "NEW_CAPABILITY"
    )
    extending = decision == "EXTENDS_EXISTING_CAPABILITY"
    facet = (
        "PROJECT_CAPABILITY_EXTENSION_GAP"
        if extending
        else "PROJECT_CAPABILITY_GAP"
    )
    projected["coverage_status"] = COVERAGE_PARTIAL
    projected["request_facets"] = [
        {
            "facet": facet,
            "matched_terms": [],
            "candidate_capability_identifiers": [],
            "source": "EXISTING_PLATFORM_CORE_CANDIDATE_CAPABILITY_DISCOVERY",
        }
    ]
    projected["request_facet_count"] = 1
    projected["discovered_reusable_capabilities"] = []
    projected["capability_coverage"] = [
        {
            "facet": facet,
            "matched_terms": [],
            "covered": False,
            "certified_capability_matches": [],
            "coverage_basis": "EXISTING_NEW_CAPABILITY_DECISION",
        }
    ]
    projected["covered_facet_count"] = 0
    projected["uncovered_residual_gaps"] = [
        {
            "facet": facet,
            "reason": (
                "Existing Platform Core capability discovery classified the bounded "
                "goal as new project capability work."
            ),
            "gap_classification": "UNCOVERED_PROJECT_CAPABILITY_GAP",
        }
    ]
    projected["uncovered_residual_gap_count"] = 1
    projected["minimal_required_platform_extension"] = {
        "classification": (
            MINIMAL_COMPOSITION_SERVICE_REQUIRED
            if extending
            else GENUINELY_NEW_CAPABILITY_REQUIRED
        ),
        "required": True,
        "recommended_components": [],
        "rationale": (
            "Existing Platform Core capability discovery requires bounded new or extension work; "
            "the projection does not invent an implementation target."
        ),
    }
    projected["failure_reason"] = None
    projected["binding_projection"] = {
        "projection_type": "EXISTING_NEW_CAPABILITY_DECISION_TO_COVERAGE_GAP",
        "source_coverage_hash": source_hash,
        "source_capability_resolution_decision": decision,
        "semantic_selection_created": False,
        "planning_engine_created": False,
    }
    projected.pop("artifact_hash", None)
    projected["artifact_hash"] = replay_hash(projected)
    return projected


def _project_required_extension_gap(
    coverage: dict[str, Any],
    *,
    knowledge_reuse: dict[str, Any],
) -> dict[str, Any]:
    """Preserve reuse while projecting existing new-work evidence into the plan."""

    projected = deepcopy(coverage)
    source_hash = projected.get("artifact_hash")
    residual = list(projected.get("uncovered_residual_gaps") or [])
    residual.append(
        {
            "facet": "PROJECT_CAPABILITY_EXTENSION_GAP",
            "reason": str(
                knowledge_reuse.get("reuse_reason")
                or "Existing capability is reusable but bounded extension work remains."
            ),
            "gap_classification": "UNCOVERED_PROJECT_CAPABILITY_EXTENSION_GAP",
        }
    )
    recommended = [
        str(item.get("capability_identifier"))
        for item in projected.get("discovered_reusable_capabilities") or []
        if isinstance(item, dict) and item.get("capability_identifier")
    ]
    projected["coverage_status"] = COVERAGE_PARTIAL
    projected["uncovered_residual_gaps"] = residual
    projected["uncovered_residual_gap_count"] = len(residual)
    projected["minimal_required_platform_extension"] = {
        "classification": MINIMAL_COMPOSITION_SERVICE_REQUIRED,
        "required": True,
        "recommended_components": recommended,
        "rationale": (
            "Existing Knowledge Reuse preserves certified capability reuse while "
            "requiring one bounded project extension."
        ),
    }
    projected["failure_reason"] = None
    projected["binding_projection"] = {
        "projection_type": "EXISTING_KNOWLEDGE_REUSE_NEW_WORK_TO_EXTENSION_GAP",
        "source_coverage_hash": source_hash,
        "knowledge_reuse_hash": _snapshot_hash(knowledge_reuse),
        "semantic_selection_created": False,
        "planning_engine_created": False,
    }
    projected.pop("artifact_hash", None)
    projected["artifact_hash"] = replay_hash(projected)
    return projected


def _failure_reason(
    *, coverage: dict[str, Any], plan: dict[str, Any], durable: dict[str, Any]
) -> str:
    if coverage.get("coverage_status") == COVERAGE_FAILED_CLOSED:
        return str(coverage.get("failure_reason") or "capability scope unresolved")
    if plan.get("plan_status") == DEVELOPMENT_COMPOSITION_PLAN_FAILED_CLOSED:
        return str(plan.get("failure_reason") or "development plan failed closed")
    if plan.get("implementation_required") is not True:
        return "existing capability evidence does not require a new implementation proposal"
    return str(durable.get("failure_reason") or "durable governed work is not approval ready")


def _validate_preview_lineage(*, preview: dict[str, Any], candidate: dict[str, Any]) -> None:
    fields = (
        "project_objective_hash",
        "knowledge_reuse_hash",
        "platform_knowledge_hash",
        "development_composition_plan_hash",
        "durable_governed_work_hash",
        "durable_governed_work_id",
        "approval_request_id",
        "approval_request_hash",
    )
    for field in fields:
        if preview.get(field) != candidate.get(field):
            raise FailClosedRuntimeError(
                f"implementation turn proposal preview lineage mismatch: {field}"
            )


def _validate_hash_bound_snapshot(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"{field_name} must be a dict")
    candidate = deepcopy(value)
    artifact_hash = candidate.get("artifact_hash")
    if artifact_hash is not None:
        body = deepcopy(candidate)
        body.pop("artifact_hash", None)
        if replay_hash(body) != artifact_hash:
            raise FailClosedRuntimeError(f"{field_name} hash mismatch")
    return candidate


def _snapshot_hash(value: dict[str, Any]) -> str:
    artifact_hash = value.get("artifact_hash")
    return str(artifact_hash) if isinstance(artifact_hash, str) else replay_hash(value)


def _persist_binding(replay_dir: Path, artifact: dict[str, Any]) -> None:
    path = replay_dir / "000_implementation_turn_binding_recorded.json"
    wrapper = {
        "replay_index": 0,
        "replay_step": "implementation_turn_binding_recorded",
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(path, wrapper)


def _persist_consumption(replay_dir: Path, artifact: dict[str, Any]) -> None:
    path = replay_dir / "001_implementation_turn_approval_consumed.json"
    wrapper = {
        "replay_index": 1,
        "replay_step": "implementation_turn_approval_consumed",
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(path, wrapper)


def _validate_wrapper(wrapper: dict[str, Any], *, index: int, step: str) -> None:
    if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
        raise FailClosedRuntimeError("implementation turn Replay ordering mismatch")
    body = deepcopy(wrapper)
    actual_hash = body.pop("replay_hash", None)
    if replay_hash(body) != actual_hash:
        raise FailClosedRuntimeError("implementation turn Replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


__all__ = [
    "IMPLEMENTATION_TURN_APPROVED_IDENTITIES_CONSUMED",
    "IMPLEMENTATION_TURN_READY_FOR_APPROVAL",
    "IMPLEMENTATION_TURN_UNRESOLVED_SCOPE_FAILED_CLOSED",
    "PLATFORM_IMPLEMENTATION_TURN_APPROVAL_CONSUMPTION_ARTIFACT_V1",
    "PLATFORM_IMPLEMENTATION_TURN_DURABLE_WORK_BINDING_ARTIFACT_V1",
    "PLATFORM_IMPLEMENTATION_TURN_DURABLE_WORK_BINDING_VERSION",
    "PLATFORM_IMPLEMENTATION_TURN_PROPOSAL_PREVIEW_ARTIFACT_V1",
    "compose_implementation_turn_durable_work_binding",
    "consume_approved_implementation_turn_binding",
    "reconstruct_implementation_turn_approval_consumption",
    "reconstruct_implementation_turn_durable_work_binding",
    "validate_implementation_turn_approval_consumption",
    "validate_implementation_turn_durable_work_binding",
    "validate_implementation_turn_proposal_preview",
]
