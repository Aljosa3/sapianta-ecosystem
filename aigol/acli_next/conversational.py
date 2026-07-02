"""Thin conversational ACLI Next UX over certified runtime capabilities."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.acli_next.daily_dashboard import run_acli_next_daily_dashboard
from aigol.acli_next.execution_plan import run_acli_next_interactive_with_execution_plan
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash, write_json_immutable


ACLI_NEXT_CONVERSATIONAL_SESSION_VERSION = (
    "G11_02_ACLI_NEXT_CONVERSATIONAL_DEVELOPMENT_SESSION_IMPLEMENTATION_V1"
)
ACLI_NEXT_CONVERSATIONAL_COMMAND_NAME = "aigol next"
ACLI_NEXT_CONVERSATIONAL_SESSION_PRESENTED = "ACLI_NEXT_CONVERSATIONAL_SESSION_PRESENTED"


def run_acli_next_conversational_session(
    *,
    prompts: list[str],
    created_at: str,
    replay_dir: str | Path,
    session_id: str | None = None,
    workspace: str | Path = ".",
) -> dict[str, Any]:
    """Run a natural ACLI Next conversational turn set using existing certified components."""

    normalized_prompts = _require_prompts(prompts)
    conversation_id = session_id or _derived_session_id(normalized_prompts, created_at)
    session_root = Path(replay_dir) / conversation_id
    run_index = _next_run_index(session_root)
    run_id = f"RUN-{run_index:06d}"
    run_root = session_root / run_id
    runtime_session_id = f"{conversation_id}:{run_id}"
    turns = [
        {
            "operator_request": prompt,
            "operator_response": _operator_response_for_prompt(prompt, index, len(normalized_prompts)),
        }
        for index, prompt in enumerate(normalized_prompts, start=1)
    ]

    execution_plan = run_acli_next_interactive_with_execution_plan(
        session_id=runtime_session_id,
        turns=turns,
        created_at=created_at,
        replay_dir=run_root / "execution_plan",
        workspace=workspace,
        worker_sequence=["Platform Core", "Governed Development Workflow"],
        requested_capabilities=_requested_capabilities(normalized_prompts),
        expected_artifacts=[
            "workflow_stage_summary",
            "execution_plan_preview",
            "dashboard_snapshot",
            "replay_reference",
        ],
        potential_repository_impacts=["none_from_conversational_layer"],
    )
    _require_non_authoritative_execution_plan(execution_plan)

    dashboard = run_acli_next_daily_dashboard(
        dashboard_id=f"{conversation_id}:{run_id}:DASHBOARD",
        platform_core_state=_platform_core_state(
            conversation_id=conversation_id,
            run_id=run_id,
            prompts=normalized_prompts,
            execution_plan=execution_plan,
        ),
        created_at=created_at,
        replay_dir=run_root / "dashboard",
    )
    _require_non_authoritative_dashboard(dashboard)

    artifact = _conversational_artifact(
        conversation_id=conversation_id,
        run_id=run_id,
        run_index=run_index,
        prompts=normalized_prompts,
        execution_plan=execution_plan,
        dashboard=dashboard,
        session_root=session_root,
        run_root=run_root,
        created_at=created_at,
        workspace=workspace,
    )
    write_json_immutable(run_root / "000_acli_next_conversational_session_presented.json", artifact)
    result = deepcopy(artifact)
    result["replay_hash"] = artifact["artifact_hash"]
    return result


def render_acli_next_conversational_session(result: dict[str, Any]) -> str:
    """Render the conversational ACLI Next session summary."""

    dashboard = result.get("dashboard_summary") if isinstance(result.get("dashboard_summary"), dict) else {}
    hybrid = dashboard.get("hybrid_operation") if isinstance(dashboard.get("hybrid_operation"), dict) else {}
    governance = dashboard.get("governance") if isinstance(dashboard.get("governance"), dict) else {}
    replay = dashboard.get("replay") if isinstance(dashboard.get("replay"), dict) else {}
    health = (
        dashboard.get("architectural_health")
        if isinstance(dashboard.get("architectural_health"), dict)
        else {}
    )
    return "\n".join(
        [
            f"command: {result.get('command')}",
            f"runtime_version: {result.get('runtime_version')}",
            f"session_id: {result.get('session_id')}",
            f"run_id: {result.get('run_id')}",
            f"session_resumed: {result.get('session_resumed')}",
            f"turn_count: {result.get('turn_count')}",
            f"session_status: {result.get('session_status')}",
            f"prompt: {result.get('latest_prompt')}",
            f"current_stage: {dashboard.get('workflow', {}).get('current_stage')}",
            f"next_expected_operation: {dashboard.get('workflow', {}).get('next_expected_operation')}",
            f"approval_state: {governance.get('approval_state')}",
            f"authorization_state: {governance.get('authorization_state')}",
            f"latest_replay_record: {replay.get('latest_replay_record')}",
            f"architectural_health_status: {health.get('health_status')}",
            f"hybrid_status: {hybrid.get('hybrid_status')}",
            f"hybrid_reason: {hybrid.get('reason')}",
            f"execution_plan_replay_reference: {result.get('execution_plan_replay_reference')}",
            f"dashboard_replay_reference: {result.get('dashboard_replay_reference')}",
            f"replay_reference: {result.get('replay_reference')}",
            f"acli_next_authorizes: {result.get('acli_next_authorizes')}",
            f"acli_next_executes: {result.get('acli_next_executes')}",
            f"acli_next_records_replay_evidence: {result.get('acli_next_records_replay_evidence')}",
        ]
    )


def _conversational_artifact(
    *,
    conversation_id: str,
    run_id: str,
    run_index: int,
    prompts: list[str],
    execution_plan: dict[str, Any],
    dashboard: dict[str, Any],
    session_root: Path,
    run_root: Path,
    created_at: str,
    workspace: str | Path,
) -> dict[str, Any]:
    dashboard_snapshot = dashboard.get("platform_core_snapshot", {})
    artifact = {
        "artifact_type": "ACLI_NEXT_CONVERSATIONAL_SESSION_PRESENTATION_ARTIFACT_V1",
        "runtime_version": ACLI_NEXT_CONVERSATIONAL_SESSION_VERSION,
        "command": ACLI_NEXT_CONVERSATIONAL_COMMAND_NAME,
        "session_id": conversation_id,
        "run_id": run_id,
        "run_index": run_index,
        "session_resumed": run_index > 1,
        "session_status": ACLI_NEXT_CONVERSATIONAL_SESSION_PRESENTED,
        "turn_count": len(prompts),
        "latest_prompt": prompts[-1],
        "prompt_hashes": [replay_hash(prompt) for prompt in prompts],
        "workspace": str(Path(workspace)),
        "created_at": _require_string(created_at, "created_at"),
        "execution_plan_hash": execution_plan["replay_hash"],
        "execution_plan_replay_reference": execution_plan.get("replay_reference"),
        "dashboard_hash": dashboard["replay_hash"],
        "dashboard_replay_reference": dashboard.get("replay_reference"),
        "dashboard_summary": deepcopy(dashboard_snapshot),
        "replay_reference": str(run_root),
        "session_root": str(session_root),
        "show_guide_delegate_only": True,
        "minimal_ux_extension_only": True,
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


def _platform_core_state(
    *,
    conversation_id: str,
    run_id: str,
    prompts: list[str],
    execution_plan: dict[str, Any],
) -> dict[str, Any]:
    requested_operation = _requested_operation(prompts)
    hybrid_required = requested_operation in {
        "git_remote",
        "dependency_management",
        "deployment",
        "exceptional_environment",
    }
    return {
        "workflow": {
            "workflow_id": "GOVERNED_DEVELOPMENT_WORKFLOW",
            "current_stage": "Classify Capability Coverage",
            "completed_stages": ["Capture Intent"],
            "current_operation": "present conversational governed development state",
            "next_expected_operation": "Existing Capability Audit",
        },
        "active_task": {
            "task_id": conversation_id,
            "task_objective": prompts[-1],
            "current_milestone": "G11_02",
            "current_generation": "Generation 11",
            "governance_state": "governed",
            "requested_operation": requested_operation,
        },
        "governance": {
            "approval_state": "not_required_for_conversational_presentation",
            "authorization_state": "not_required_for_conversational_presentation",
            "pending_approvals": [],
            "completed_authorizations": [],
        },
        "validation": {
            "latest_validation": "not_run",
            "validation_suite_status": "not_run",
            "validation_summary": "conversational presentation only; no execution validation required",
            "validation_outcome": "not_applicable",
        },
        "replay": {
            "latest_replay_record": str(execution_plan.get("replay_reference")),
            "replay_summary": f"conversational run {run_id} delegated to existing ACLI Next execution plan runtime",
            "reconstruction_available": True,
            "evidence_available": True,
        },
        "architectural_health": {
            "health_status": "advisory_review_required_before_certification",
            "highest_severity": "none",
            "findings": [],
            "recommendations": [
                "verify ACLI Next remains show-guide-delegate only",
                "verify Platform Core remains the orchestration authority",
            ],
        },
        "hybrid": {
            "operation_type": requested_operation,
            "hybrid_required": hybrid_required,
        },
    }


def _requested_capabilities(prompts: list[str]) -> list[str]:
    capabilities = [
        "acli_next_conversational_presentation",
        "governed_development_workflow_visibility",
        "platform_core_execution_plan_preview",
        "daily_operational_dashboard",
    ]
    requested = _requested_operation(prompts)
    if requested != "governed_development":
        capabilities.append(f"hybrid_guidance_for_{requested}")
    return capabilities


def _requested_operation(prompts: list[str]) -> str:
    text = " ".join(prompts).lower()
    if "git remote" in text or "push" in text or "pull request" in text or "remote branch" in text:
        return "git_remote"
    if "dependency" in text or "package" in text or "lockfile" in text:
        return "dependency_management"
    if "deploy" in text or "deployment" in text:
        return "deployment"
    if "environment" in text or "credential" in text or "infrastructure" in text:
        return "exceptional_environment"
    return "governed_development"


def _operator_response_for_prompt(prompt: str, index: int, total: int) -> str:
    if index < total:
        return "please clarify"
    return "confirm"


def _next_run_index(session_root: Path) -> int:
    if not session_root.exists():
        return 1
    existing = []
    for path in session_root.iterdir():
        if not path.is_dir() or not path.name.startswith("RUN-"):
            continue
        suffix = path.name.removeprefix("RUN-")
        if suffix.isdigit():
            existing.append(int(suffix))
    return max(existing, default=0) + 1


def _derived_session_id(prompts: list[str], created_at: str) -> str:
    digest = replay_hash({"prompts": prompts, "created_at": created_at})[7:23].upper()
    return f"ACLI-NEXT-CONVERSATIONAL-{digest}"


def _require_prompts(prompts: list[str]) -> list[str]:
    if not isinstance(prompts, list) or not prompts:
        raise FailClosedRuntimeError("ACLI Next conversational session requires at least one prompt")
    return [_require_string(prompt, "prompt").strip() for prompt in prompts]


def _require_non_authoritative_execution_plan(execution_plan: dict[str, Any]) -> None:
    for key in (
        "execution_authorized",
        "worker_invoked",
        "provider_invoked",
        "repository_mutated",
        "deployment_performed",
    ):
        if execution_plan.get(key) is not False:
            raise FailClosedRuntimeError(f"ACLI Next conversational session failed closed: execution plan {key}")


def _require_non_authoritative_dashboard(dashboard: dict[str, Any]) -> None:
    for key in (
        "acli_next_authorizes",
        "acli_next_executes",
        "acli_next_records_replay_evidence",
        "external_operation_performed",
        "repository_mutated",
        "deployment_performed",
        "dependency_operation_performed",
        "git_remote_operation_performed",
    ):
        if dashboard.get(key) is not False:
            raise FailClosedRuntimeError(f"ACLI Next conversational session failed closed: dashboard {key}")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"ACLI Next conversational session requires {field}")
    return value
