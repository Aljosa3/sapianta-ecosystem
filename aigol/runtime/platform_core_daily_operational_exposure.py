"""Platform Core daily operational exposure snapshot for ACLI Next."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


PLATFORM_CORE_DAILY_OPERATIONAL_EXPOSURE_VERSION = (
    "G10_04_ACLI_NEXT_DAILY_OPERATIONAL_EXPOSURE_IMPLEMENTATION_V1"
)
DAILY_OPERATIONAL_EXPOSURE_SNAPSHOT_ARTIFACT_V1 = "DAILY_OPERATIONAL_EXPOSURE_SNAPSHOT_ARTIFACT_V1"
DAILY_OPERATIONAL_EXPOSURE_READY = "DAILY_OPERATIONAL_EXPOSURE_READY"
FULLY_GOVERNED = "FULLY_GOVERNED"
HYBRID_REQUIRED = "HYBRID_REQUIRED"

WORKFLOW_STAGES = (
    "Capture Intent",
    "Classify Capability Coverage",
    "Show Workflow Stage",
    "Form Candidate / Proposal",
    "Request Human Approval",
    "Request Governance Authorization",
    "Delegate Worker Execution",
    "Show Replay Evidence",
    "Show Validation Result",
    "Show Architectural Health Advisory",
    "Prepare Review / Certification Artifact",
    "Show Completion Or Hybrid Exception",
)

HYBRID_OPERATION_GUIDANCE = {
    "git_remote": {
        "reason": "Git remote workflow exceeds certified local Git commit coverage.",
        "external_tool": "git",
        "certified_coverage_ends_at": "governed local Git commit",
        "return_condition": "return after remote command output and repository state are captured",
    },
    "dependency_management": {
        "reason": "Dependency operation requires package manager, registry, network, and lockfile policy.",
        "external_tool": "package manager",
        "certified_coverage_ends_at": "governed repository mutation and validation suite",
        "return_condition": "return after lockfile changes and validation evidence are captured",
    },
    "deployment": {
        "reason": "Deployment crosses release, environment authority, and runtime activation boundaries.",
        "external_tool": "deployment tool",
        "certified_coverage_ends_at": "governed local repository development",
        "return_condition": "return after deployment evidence and rollback readiness are captured",
    },
    "exceptional_environment": {
        "reason": "Exceptional environment work is outside certified Worker Platform scope.",
        "external_tool": "operator-selected environment tool",
        "certified_coverage_ends_at": "certified governed development workflow",
        "return_condition": "return after scope, result, and continuity evidence are captured",
    },
}


def create_daily_operational_exposure_snapshot(
    *,
    dashboard_id: str,
    platform_core_state: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    """Create a deterministic Platform Core presentation snapshot for ACLI Next."""

    state = _require_mapping(platform_core_state, "platform_core_state")
    workflow = _workflow_summary(state.get("workflow", {}))
    active_task = _active_task_summary(state.get("active_task", {}))
    governance = _governance_summary(state.get("governance", {}))
    validation = _validation_summary(state.get("validation", {}))
    replay = _replay_summary(state.get("replay", {}))
    architectural_health = _architectural_health_summary(state.get("architectural_health", {}))
    hybrid = _hybrid_summary(state.get("hybrid", {}), active_task)
    artifact = {
        "artifact_type": DAILY_OPERATIONAL_EXPOSURE_SNAPSHOT_ARTIFACT_V1,
        "runtime_version": PLATFORM_CORE_DAILY_OPERATIONAL_EXPOSURE_VERSION,
        "dashboard_id": _require_string(dashboard_id, "dashboard_id"),
        "created_at": _require_string(created_at, "created_at"),
        "exposure_status": DAILY_OPERATIONAL_EXPOSURE_READY,
        "workflow": workflow,
        "active_task": active_task,
        "governance": governance,
        "validation": validation,
        "replay": replay,
        "architectural_health": architectural_health,
        "hybrid_operation": hybrid,
        "dashboard_sections": [
            "workflow",
            "active_task",
            "governance",
            "validation",
            "replay",
            "architectural_health",
            "hybrid_operation",
        ],
        "platform_core_coordinates": True,
        "acli_next_presentation_only": True,
        "governance_authority_preserved": True,
        "replay_authority_preserved": True,
        "worker_execution_authority_preserved": True,
        "architectural_health_advisory_only": True,
        "platform_digital_twin_evidence_source_preserved": True,
        "acli_next_authorizes": False,
        "acli_next_executes": False,
        "acli_next_records_replay_evidence": False,
        "acli_next_repairs_architecture": False,
        "acli_next_certifies": False,
        "external_operation_performed": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "dependency_operation_performed": False,
        "git_remote_operation_performed": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _workflow_summary(raw: Any) -> dict[str, Any]:
    workflow = _mapping_or_empty(raw)
    current_stage = _workflow_stage(workflow.get("current_stage") or WORKFLOW_STAGES[0])
    completed = [_workflow_stage(stage) for stage in _string_list(workflow.get("completed_stages"))]
    if current_stage not in completed and workflow.get("current_stage_complete") is True:
        completed.append(current_stage)
    pending = [stage for stage in WORKFLOW_STAGES if stage not in completed]
    return {
        "workflow_id": _string_or_default(workflow.get("workflow_id"), "GOVERNED_DEVELOPMENT_WORKFLOW"),
        "current_stage": current_stage,
        "completed_stages": completed,
        "pending_stages": pending,
        "current_operation": _string_or_default(workflow.get("current_operation"), "present daily operational status"),
        "next_expected_operation": _string_or_default(
            workflow.get("next_expected_operation"), _next_stage_after(current_stage)
        ),
        "stage_count": len(WORKFLOW_STAGES),
        "completed_stage_count": len(completed),
        "pending_stage_count": len(pending),
        "source_owner": "Platform Core",
    }


def _active_task_summary(raw: Any) -> dict[str, Any]:
    task = _mapping_or_empty(raw)
    return {
        "task_id": _string_or_default(task.get("task_id"), "UNSPECIFIED_TASK"),
        "task_objective": _string_or_default(task.get("task_objective"), "show governed development status"),
        "current_milestone": _string_or_default(task.get("current_milestone"), "G10_04"),
        "current_generation": _string_or_default(task.get("current_generation"), "Generation 10"),
        "governance_state": _string_or_default(task.get("governance_state"), "governed"),
        "requested_operation": _string_or_default(task.get("requested_operation"), "governed_development"),
        "source_owner": "Platform Core",
    }


def _governance_summary(raw: Any) -> dict[str, Any]:
    governance = _mapping_or_empty(raw)
    return {
        "approval_state": _string_or_default(governance.get("approval_state"), "not_required_for_display"),
        "authorization_state": _string_or_default(governance.get("authorization_state"), "not_required_for_display"),
        "pending_approvals": _string_list(governance.get("pending_approvals")),
        "completed_authorizations": _string_list(governance.get("completed_authorizations")),
        "governance_authority": "Governance",
        "acli_next_authorizes": False,
    }


def _validation_summary(raw: Any) -> dict[str, Any]:
    validation = _mapping_or_empty(raw)
    return {
        "latest_validation": _string_or_default(validation.get("latest_validation"), "none"),
        "validation_suite_status": _string_or_default(validation.get("validation_suite_status"), "not_run"),
        "validation_summary": _string_or_default(validation.get("validation_summary"), "validation not yet available"),
        "validation_outcome": _string_or_default(validation.get("validation_outcome"), "unknown"),
        "execution_owner": "Worker Platform",
        "evidence_owner": "Replay",
        "acli_next_executes": False,
    }


def _replay_summary(raw: Any) -> dict[str, Any]:
    replay = _mapping_or_empty(raw)
    return {
        "latest_replay_record": _string_or_default(replay.get("latest_replay_record"), "none"),
        "replay_summary": _string_or_default(replay.get("replay_summary"), "replay evidence not yet available"),
        "reconstruction_available": bool(replay.get("reconstruction_available", False)),
        "evidence_available": bool(replay.get("evidence_available", False)),
        "replay_authority": "Replay",
        "acli_next_records_replay_evidence": False,
    }


def _architectural_health_summary(raw: Any) -> dict[str, Any]:
    health = _mapping_or_empty(raw)
    return {
        "health_status": _string_or_default(health.get("health_status"), "not_run"),
        "findings": [_normalize_finding(finding) for finding in _list_or_empty(health.get("findings"))],
        "highest_severity": _string_or_default(health.get("highest_severity"), "none"),
        "recommendations": _string_list(health.get("recommendations")),
        "advisory_only": True,
        "repair_authority": False,
        "source_owner": "Architectural Health",
    }


def _hybrid_summary(raw: Any, active_task: dict[str, Any]) -> dict[str, Any]:
    hybrid = _mapping_or_empty(raw)
    requested = _string_or_default(hybrid.get("operation_type"), active_task["requested_operation"])
    explicit_required = hybrid.get("hybrid_required")
    hybrid_required = bool(explicit_required) if explicit_required is not None else requested in HYBRID_OPERATION_GUIDANCE
    guidance = HYBRID_OPERATION_GUIDANCE.get(
        requested,
        {
            "reason": "operation remains inside certified Platform Core coverage",
            "external_tool": "none",
            "certified_coverage_ends_at": "not_applicable",
            "return_condition": "not_applicable",
        },
    )
    return {
        "hybrid_status": HYBRID_REQUIRED if hybrid_required else FULLY_GOVERNED,
        "operation_type": requested,
        "reason": _string_or_default(hybrid.get("reason"), guidance["reason"]),
        "external_tool": _string_or_default(hybrid.get("external_tool"), guidance["external_tool"]),
        "certified_coverage_ends_at": _string_or_default(
            hybrid.get("certified_coverage_ends_at"), guidance["certified_coverage_ends_at"]
        ),
        "return_condition": _string_or_default(hybrid.get("return_condition"), guidance["return_condition"]),
        "replay_continuity_required": hybrid_required,
        "governance_continuity_required": hybrid_required,
        "guidance_only": True,
        "external_operation_performed": False,
    }


def _normalize_finding(raw: Any) -> dict[str, Any]:
    finding = _mapping_or_empty(raw)
    return {
        "finding_id": _string_or_default(finding.get("finding_id"), "UNSPECIFIED_FINDING"),
        "severity": _string_or_default(finding.get("severity"), "info"),
        "summary": _string_or_default(finding.get("summary"), "no finding summary provided"),
        "recommendation": _string_or_default(finding.get("recommendation"), "human review if needed"),
    }


def _next_stage_after(stage: str) -> str:
    try:
        index = WORKFLOW_STAGES.index(stage)
    except ValueError:
        return WORKFLOW_STAGES[0]
    if index + 1 >= len(WORKFLOW_STAGES):
        return "workflow complete"
    return WORKFLOW_STAGES[index + 1]


def _workflow_stage(value: Any) -> str:
    stage = _require_string(value, "workflow stage")
    if stage not in WORKFLOW_STAGES:
        raise FailClosedRuntimeError(f"daily operational exposure failed closed: unknown workflow stage {stage}")
    return stage


def _require_mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"daily operational exposure requires {field} mapping")
    return deepcopy(value)


def _mapping_or_empty(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise FailClosedRuntimeError("daily operational exposure expected mapping")
    return deepcopy(value)


def _list_or_empty(value: Any) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise FailClosedRuntimeError("daily operational exposure expected list")
    return deepcopy(value)


def _string_list(value: Any) -> list[str]:
    return [_require_string(item, "list item") for item in _list_or_empty(value)]


def _string_or_default(value: Any, default: str) -> str:
    if value is None:
        return default
    return _require_string(value, "string field")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"daily operational exposure requires {field}")
    return value
