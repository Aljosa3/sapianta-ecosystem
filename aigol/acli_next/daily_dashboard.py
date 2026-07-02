"""ACLI Next daily operational exposure dashboard adapter."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.platform_core_daily_operational_exposure import (
    PLATFORM_CORE_DAILY_OPERATIONAL_EXPOSURE_VERSION,
    create_daily_operational_exposure_snapshot,
)
from aigol.runtime.transport.serialization import replay_hash, write_json_immutable


ACLI_NEXT_DAILY_OPERATIONAL_EXPOSURE_VERSION = (
    "G10_04_ACLI_NEXT_DAILY_OPERATIONAL_EXPOSURE_IMPLEMENTATION_V1"
)
ACLI_NEXT_DAILY_DASHBOARD_COMMAND_NAME = "aigol next dashboard"
ACLI_NEXT_DAILY_DASHBOARD_PRESENTED = "ACLI_NEXT_DAILY_DASHBOARD_PRESENTED"


def run_acli_next_daily_dashboard(
    *,
    dashboard_id: str,
    platform_core_state: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Render a daily operational dashboard from Platform Core state."""

    replay_path = Path(replay_dir)
    snapshot = create_daily_operational_exposure_snapshot(
        dashboard_id=dashboard_id,
        platform_core_state=platform_core_state,
        created_at=created_at,
    )
    presentation = _presentation_artifact(
        dashboard_id=dashboard_id,
        snapshot=snapshot,
        created_at=created_at,
        replay_path=replay_path,
    )
    write_json_immutable(replay_path / "000_acli_next_daily_dashboard_presented.json", presentation)
    result = deepcopy(presentation)
    result["replay_hash"] = presentation["artifact_hash"]
    return result


def render_acli_next_daily_dashboard(result: dict[str, Any]) -> str:
    """Render the ACLI Next daily development dashboard."""

    snapshot = result.get("platform_core_snapshot")
    if not isinstance(snapshot, dict):
        snapshot = {}
    workflow = snapshot.get("workflow") if isinstance(snapshot.get("workflow"), dict) else {}
    task = snapshot.get("active_task") if isinstance(snapshot.get("active_task"), dict) else {}
    governance = snapshot.get("governance") if isinstance(snapshot.get("governance"), dict) else {}
    validation = snapshot.get("validation") if isinstance(snapshot.get("validation"), dict) else {}
    replay = snapshot.get("replay") if isinstance(snapshot.get("replay"), dict) else {}
    health = (
        snapshot.get("architectural_health")
        if isinstance(snapshot.get("architectural_health"), dict)
        else {}
    )
    hybrid = snapshot.get("hybrid_operation") if isinstance(snapshot.get("hybrid_operation"), dict) else {}
    return "\n".join(
        [
            f"command: {result.get('command')}",
            f"runtime_version: {result.get('runtime_version')}",
            f"platform_core_service_version: {result.get('platform_core_service_version')}",
            f"dashboard_id: {result.get('dashboard_id')}",
            f"dashboard_status: {result.get('dashboard_status')}",
            f"workflow_id: {workflow.get('workflow_id')}",
            f"current_stage: {workflow.get('current_stage')}",
            f"current_operation: {workflow.get('current_operation')}",
            f"next_expected_operation: {workflow.get('next_expected_operation')}",
            f"completed_stages: {', '.join(workflow.get('completed_stages', []))}",
            f"pending_stages: {', '.join(workflow.get('pending_stages', []))}",
            f"active_task: {task.get('task_objective')}",
            f"current_milestone: {task.get('current_milestone')}",
            f"current_generation: {task.get('current_generation')}",
            f"governance_state: {task.get('governance_state')}",
            f"approval_state: {governance.get('approval_state')}",
            f"authorization_state: {governance.get('authorization_state')}",
            f"pending_approvals: {', '.join(governance.get('pending_approvals', []))}",
            f"completed_authorizations: {', '.join(governance.get('completed_authorizations', []))}",
            f"latest_validation: {validation.get('latest_validation')}",
            f"validation_suite_status: {validation.get('validation_suite_status')}",
            f"validation_outcome: {validation.get('validation_outcome')}",
            f"validation_summary: {validation.get('validation_summary')}",
            f"latest_replay_record: {replay.get('latest_replay_record')}",
            f"reconstruction_available: {replay.get('reconstruction_available')}",
            f"evidence_available: {replay.get('evidence_available')}",
            f"architectural_health_status: {health.get('health_status')}",
            f"architectural_health_highest_severity: {health.get('highest_severity')}",
            f"architectural_health_findings: {len(health.get('findings', []))}",
            f"hybrid_status: {hybrid.get('hybrid_status')}",
            f"hybrid_reason: {hybrid.get('reason')}",
            f"hybrid_external_tool: {hybrid.get('external_tool')}",
            f"hybrid_return_condition: {hybrid.get('return_condition')}",
            f"acli_next_authorizes: {result.get('acli_next_authorizes')}",
            f"acli_next_executes: {result.get('acli_next_executes')}",
            f"acli_next_records_replay_evidence: {result.get('acli_next_records_replay_evidence')}",
            f"external_operation_performed: {result.get('external_operation_performed')}",
            f"replay_reference: {result.get('replay_reference')}",
        ]
    )


def _presentation_artifact(
    *,
    dashboard_id: str,
    snapshot: dict[str, Any],
    created_at: str,
    replay_path: Path,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": "ACLI_NEXT_DAILY_DASHBOARD_PRESENTATION_ARTIFACT_V1",
        "runtime_version": ACLI_NEXT_DAILY_OPERATIONAL_EXPOSURE_VERSION,
        "platform_core_service_version": PLATFORM_CORE_DAILY_OPERATIONAL_EXPOSURE_VERSION,
        "command": ACLI_NEXT_DAILY_DASHBOARD_COMMAND_NAME,
        "dashboard_id": dashboard_id,
        "dashboard_status": ACLI_NEXT_DAILY_DASHBOARD_PRESENTED,
        "platform_core_snapshot": deepcopy(snapshot),
        "platform_core_snapshot_hash": snapshot["artifact_hash"],
        "replay_reference": str(replay_path),
        "created_at": created_at,
        "show_guide_delegate_only": True,
        "platform_core_coordinates": True,
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
