"""Advisory execution planning for ACLI Next confirmed sessions."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.acli_next.interactive import ACLI_NEXT_INTERACTIVE_COMPLETED, run_acli_next_interactive_session
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash, write_json_immutable


ACLI_NEXT_EXECUTION_PLAN_VERSION = "G8_06_EXECUTION_PLAN_AND_MUTATION_PREVIEW_V1"
EXECUTION_PLAN_COMMAND_NAME = "aigol next execution-plan"

ACLI_NEXT_EXECUTION_PLAN_REQUESTED = "ACLI_NEXT_EXECUTION_PLAN_REQUESTED"
ACLI_NEXT_EXECUTION_PLAN_RECORDED = "ACLI_NEXT_EXECUTION_PLAN_RECORDED"
ACLI_NEXT_MUTATION_PREVIEW_RECORDED = "ACLI_NEXT_MUTATION_PREVIEW_RECORDED"
ACLI_NEXT_EXECUTION_PLAN_COMPLETED = "ACLI_NEXT_EXECUTION_PLAN_COMPLETED"

AUTHORIZED_ADVISORY_EXECUTION_PLAN = "AUTHORIZED_ADVISORY_EXECUTION_PLAN"

DEFAULT_WORKER_SEQUENCE = ["ACLI_NEXT_READONLY_WORKER_HANDOFF"]
DEFAULT_REQUESTED_CAPABILITIES = ["replay_inspection", "validation_summary"]
DEFAULT_EXPECTED_ARTIFACTS = [
    "ACLI_NEXT_EXECUTION_PLAN_ARTIFACT_V1",
    "ACLI_NEXT_MUTATION_PREVIEW_ARTIFACT_V1",
]
DEFAULT_REPOSITORY_IMPACTS = ["DESCRIPTIVE_MUTATION_PREVIEW_ONLY"]


def run_acli_next_execution_plan(
    *,
    session_id: str,
    interactive_result: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
    worker_sequence: list[str] | None = None,
    requested_capabilities: list[str] | None = None,
    expected_artifacts: list[str] | None = None,
    potential_repository_impacts: list[str] | None = None,
) -> dict[str, Any]:
    """Produce a replay-visible advisory execution plan without execution."""

    replay_path = Path(replay_dir)
    _require_confirmed_interactive_session(interactive_result)
    normalized_workers = _normalize_list(worker_sequence, DEFAULT_WORKER_SEQUENCE, "worker_sequence")
    normalized_capabilities = _normalize_list(
        requested_capabilities,
        DEFAULT_REQUESTED_CAPABILITIES,
        "requested_capabilities",
    )
    normalized_artifacts = _normalize_list(expected_artifacts, DEFAULT_EXPECTED_ARTIFACTS, "expected_artifacts")
    normalized_impacts = _normalize_list(
        potential_repository_impacts,
        DEFAULT_REPOSITORY_IMPACTS,
        "potential_repository_impacts",
    )
    authorization = _governance_plan_authorization(
        session_id=session_id,
        interactive_result=interactive_result,
        created_at=created_at,
    )
    request = _plan_request_artifact(
        session_id=session_id,
        interactive_result=interactive_result,
        authorization=authorization,
        worker_sequence=normalized_workers,
        requested_capabilities=normalized_capabilities,
        expected_artifacts=normalized_artifacts,
        potential_repository_impacts=normalized_impacts,
        created_at=created_at,
    )
    _persist(replay_path, "000_acli_next_execution_plan_request.json", request)

    plan = _execution_plan_artifact(
        session_id=session_id,
        interactive_result=interactive_result,
        request=request,
        worker_sequence=normalized_workers,
        requested_capabilities=normalized_capabilities,
        expected_artifacts=normalized_artifacts,
        potential_repository_impacts=normalized_impacts,
        created_at=created_at,
    )
    _persist(replay_path, "001_acli_next_execution_plan_recorded.json", plan)

    preview = _mutation_preview_artifact(
        session_id=session_id,
        interactive_result=interactive_result,
        plan=plan,
        created_at=created_at,
    )
    _persist(replay_path, "002_acli_next_mutation_preview_recorded.json", preview)

    completion = _completion_artifact(
        session_id=session_id,
        interactive_result=interactive_result,
        request=request,
        plan=plan,
        preview=preview,
        replay_path=replay_path,
        created_at=created_at,
    )
    _persist(replay_path, "003_acli_next_execution_plan_completed.json", completion)
    return _result(completion)


def run_acli_next_interactive_with_execution_plan(
    *,
    session_id: str,
    turns: list[dict[str, str]],
    created_at: str,
    replay_dir: str | Path,
    workspace: str | Path = ".",
    worker_sequence: list[str] | None = None,
    requested_capabilities: list[str] | None = None,
    expected_artifacts: list[str] | None = None,
    potential_repository_impacts: list[str] | None = None,
) -> dict[str, Any]:
    """Run an interactive session and record an advisory execution plan."""

    replay_path = Path(replay_dir)
    interactive_result = run_acli_next_interactive_session(
        session_id=session_id,
        turns=turns,
        created_at=created_at,
        replay_dir=replay_path / "interactive_session",
        workspace=workspace,
    )
    return run_acli_next_execution_plan(
        session_id=session_id,
        interactive_result=interactive_result,
        created_at=created_at,
        replay_dir=replay_path / "execution_plan",
        worker_sequence=worker_sequence,
        requested_capabilities=requested_capabilities,
        expected_artifacts=expected_artifacts,
        potential_repository_impacts=potential_repository_impacts,
    )


def render_acli_next_execution_plan_summary(result: dict[str, Any]) -> str:
    """Render ACLI Next execution plan evidence."""

    return "\n".join(
        [
            f"command: {result.get('command')}",
            f"runtime_version: {result.get('runtime_version')}",
            f"session_id: {result.get('session_id')}",
            f"plan_status: {result.get('plan_status')}",
            f"risk_level: {result.get('execution_risk_summary', {}).get('risk_level')}",
            f"worker_sequence: {', '.join(result.get('selected_worker_sequence', []))}",
            f"requested_capabilities: {', '.join(result.get('requested_capabilities', []))}",
            f"mutation_preview_status: {result.get('mutation_preview', {}).get('preview_status')}",
            f"replay_reference: {result.get('replay_reference')}",
            f"interactive_replay_reference: {result.get('interactive_replay_reference')}",
            f"execution_authorized: {result.get('execution_authorized')}",
            f"worker_invoked: {result.get('worker_invoked')}",
            f"provider_invoked: {result.get('provider_invoked')}",
            f"repository_mutated: {result.get('repository_mutated')}",
            f"deployment_performed: {result.get('deployment_performed')}",
        ]
    )


def _governance_plan_authorization(
    *,
    session_id: str,
    interactive_result: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    authorization = {
        "artifact_type": "ACLI_NEXT_EXECUTION_PLAN_GOVERNANCE_AUTHORIZATION_V1",
        "runtime_version": ACLI_NEXT_EXECUTION_PLAN_VERSION,
        "session_id": _require_string(session_id, "session_id"),
        "authorization_status": AUTHORIZED_ADVISORY_EXECUTION_PLAN,
        "authorization_scope": "ADVISORY_PLAN_AND_DESCRIPTIVE_MUTATION_PREVIEW_ONLY",
        "authorization_basis": {
            "interactive_session_status": interactive_result.get("session_status"),
            "final_response_class": interactive_result.get("final_response_class"),
            "interactive_replay_reference": interactive_result.get("replay_reference"),
            "interactive_replay_hash": interactive_result.get("replay_hash"),
        },
        "human_confirmation_required": True,
        "human_confirmation_observed": True,
        "execution_authorized": False,
        "mutation_authorized": False,
        "worker_dispatch_authorized": False,
        "provider_authorized": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    authorization["artifact_hash"] = replay_hash(authorization)
    return authorization


def _plan_request_artifact(
    *,
    session_id: str,
    interactive_result: dict[str, Any],
    authorization: dict[str, Any],
    worker_sequence: list[str],
    requested_capabilities: list[str],
    expected_artifacts: list[str],
    potential_repository_impacts: list[str],
    created_at: str,
) -> dict[str, Any]:
    request = {
        "artifact_type": "ACLI_NEXT_EXECUTION_PLAN_REQUEST_V1",
        "runtime_version": ACLI_NEXT_EXECUTION_PLAN_VERSION,
        "command": EXECUTION_PLAN_COMMAND_NAME,
        "session_id": _require_string(session_id, "session_id"),
        "interactive_replay_reference": interactive_result["replay_reference"],
        "interactive_replay_hash": interactive_result["replay_hash"],
        "governance_authorization_hash": authorization["artifact_hash"],
        "governance_authorization_status": authorization["authorization_status"],
        "selected_worker_sequence": deepcopy(worker_sequence),
        "requested_capabilities": deepcopy(requested_capabilities),
        "expected_artifacts": deepcopy(expected_artifacts),
        "potential_repository_impacts": deepcopy(potential_repository_impacts),
        "created_at": _require_string(created_at, "created_at"),
        "plan_status": ACLI_NEXT_EXECUTION_PLAN_REQUESTED,
        "advisory_only": True,
        "execution_authorized": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "replay_visible": True,
    }
    request["artifact_hash"] = replay_hash(request)
    return request


def _execution_plan_artifact(
    *,
    session_id: str,
    interactive_result: dict[str, Any],
    request: dict[str, Any],
    worker_sequence: list[str],
    requested_capabilities: list[str],
    expected_artifacts: list[str],
    potential_repository_impacts: list[str],
    created_at: str,
) -> dict[str, Any]:
    replay_plan = _replay_plan(interactive_result)
    plan = {
        "artifact_type": "ACLI_NEXT_EXECUTION_PLAN_ARTIFACT_V1",
        "runtime_version": ACLI_NEXT_EXECUTION_PLAN_VERSION,
        "command": EXECUTION_PLAN_COMMAND_NAME,
        "session_id": _require_string(session_id, "session_id"),
        "execution_plan_request_hash": request["artifact_hash"],
        "selected_worker_sequence": deepcopy(worker_sequence),
        "requested_capabilities": deepcopy(requested_capabilities),
        "expected_artifacts": deepcopy(expected_artifacts),
        "potential_repository_impact": deepcopy(potential_repository_impacts),
        "replay_plan": replay_plan,
        "governance_checkpoints": _governance_checkpoints(),
        "execution_risk_summary": _risk_summary(worker_sequence, requested_capabilities, potential_repository_impacts),
        "mutation_preview_required": True,
        "created_at": _require_string(created_at, "created_at"),
        "plan_status": ACLI_NEXT_EXECUTION_PLAN_RECORDED,
        "advisory_only": True,
        "execution_authorized": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "replay_visible": True,
    }
    plan["artifact_hash"] = replay_hash(plan)
    return plan


def _mutation_preview_artifact(
    *,
    session_id: str,
    interactive_result: dict[str, Any],
    plan: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    preview = {
        "artifact_type": "ACLI_NEXT_MUTATION_PREVIEW_ARTIFACT_V1",
        "runtime_version": ACLI_NEXT_EXECUTION_PLAN_VERSION,
        "command": EXECUTION_PLAN_COMMAND_NAME,
        "session_id": _require_string(session_id, "session_id"),
        "execution_plan_hash": plan["artifact_hash"],
        "interactive_replay_reference": interactive_result["replay_reference"],
        "preview_status": ACLI_NEXT_MUTATION_PREVIEW_RECORDED,
        "mutation_preview": {
            "preview_status": ACLI_NEXT_MUTATION_PREVIEW_RECORDED,
            "descriptive_only": True,
            "repository_files_to_modify": [],
            "git_operations": [],
            "deployment_operations": [],
            "potential_repository_impact": deepcopy(plan["potential_repository_impact"]),
            "requires_future_mutation_certification": True,
        },
        "created_at": _require_string(created_at, "created_at"),
        "advisory_only": True,
        "execution_authorized": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "replay_visible": True,
    }
    preview["artifact_hash"] = replay_hash(preview)
    return preview


def _completion_artifact(
    *,
    session_id: str,
    interactive_result: dict[str, Any],
    request: dict[str, Any],
    plan: dict[str, Any],
    preview: dict[str, Any],
    replay_path: Path,
    created_at: str,
) -> dict[str, Any]:
    _require_advisory_non_mutating(plan)
    _require_advisory_non_mutating(preview)
    completion = {
        "artifact_type": "ACLI_NEXT_EXECUTION_PLAN_COMPLETION_V1",
        "runtime_version": ACLI_NEXT_EXECUTION_PLAN_VERSION,
        "command": EXECUTION_PLAN_COMMAND_NAME,
        "session_id": _require_string(session_id, "session_id"),
        "plan_status": ACLI_NEXT_EXECUTION_PLAN_COMPLETED,
        "execution_plan_request_hash": request["artifact_hash"],
        "execution_plan_hash": plan["artifact_hash"],
        "mutation_preview_hash": preview["artifact_hash"],
        "selected_worker_sequence": deepcopy(plan["selected_worker_sequence"]),
        "requested_capabilities": deepcopy(plan["requested_capabilities"]),
        "expected_artifacts": deepcopy(plan["expected_artifacts"]),
        "potential_repository_impact": deepcopy(plan["potential_repository_impact"]),
        "replay_plan": deepcopy(plan["replay_plan"]),
        "governance_checkpoints": deepcopy(plan["governance_checkpoints"]),
        "execution_risk_summary": deepcopy(plan["execution_risk_summary"]),
        "mutation_preview": deepcopy(preview["mutation_preview"]),
        "interactive_replay_reference": interactive_result["replay_reference"],
        "interactive_replay_hash": interactive_result["replay_hash"],
        "replay_reference": str(replay_path),
        "created_at": _require_string(created_at, "created_at"),
        "advisory_only": True,
        "execution_authorized": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "fail_closed": False,
        "replay_visible": True,
    }
    completion["artifact_hash"] = replay_hash(completion)
    return completion


def _replay_plan(interactive_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "interactive_replay_reference": interactive_result["replay_reference"],
        "interactive_replay_hash": interactive_result["replay_hash"],
        "planned_artifacts": [
            "000_acli_next_execution_plan_request.json",
            "001_acli_next_execution_plan_recorded.json",
            "002_acli_next_mutation_preview_recorded.json",
            "003_acli_next_execution_plan_completed.json",
        ],
        "replay_append_only": True,
        "replay_reconstruction_owner": "Replay",
    }


def _governance_checkpoints() -> list[dict[str, str]]:
    return [
        {"checkpoint": "human_confirmation", "required_state": "CONFIRMATION"},
        {"checkpoint": "execution_authorization", "required_state": "not_created"},
        {"checkpoint": "worker_dispatch", "required_state": "not_performed"},
        {"checkpoint": "provider_invocation", "required_state": "not_performed"},
        {"checkpoint": "repository_mutation", "required_state": "not_performed"},
        {"checkpoint": "deployment", "required_state": "not_performed"},
    ]


def _risk_summary(
    worker_sequence: list[str],
    requested_capabilities: list[str],
    potential_repository_impacts: list[str],
) -> dict[str, Any]:
    has_mutation_language = any(
        token in item.lower()
        for item in [*worker_sequence, *requested_capabilities, *potential_repository_impacts]
        for token in ("mutat", "write", "patch", "commit", "deploy")
    )
    return {
        "risk_level": "MEDIUM" if has_mutation_language else "LOW",
        "risk_basis": "descriptive mutation preview only",
        "mutation_possible_in_this_milestone": False,
        "requires_future_certification_before_execution": True,
        "fail_closed_if_execution_requested": True,
    }


def _require_confirmed_interactive_session(interactive_result: dict[str, Any]) -> None:
    if interactive_result.get("session_status") != ACLI_NEXT_INTERACTIVE_COMPLETED:
        raise FailClosedRuntimeError("ACLI Next execution plan failed closed: interactive session incomplete")
    if interactive_result.get("final_response_class") != "CONFIRMATION":
        raise FailClosedRuntimeError("ACLI Next execution plan failed closed: human confirmation missing")
    if not interactive_result.get("replay_reference") or not interactive_result.get("replay_hash"):
        raise FailClosedRuntimeError("ACLI Next execution plan failed closed: interactive replay evidence missing")
    _require_advisory_non_mutating(interactive_result)


def _require_advisory_non_mutating(artifact: dict[str, Any]) -> None:
    for key in (
        "provider_invoked",
        "worker_invoked",
        "execution_authorized",
        "repository_mutated",
        "deployment_performed",
    ):
        if artifact.get(key) is not False:
            raise FailClosedRuntimeError(f"ACLI Next execution plan failed closed: {key} was not false")
    for optional_key in ("approval_created", "authorization_created"):
        if optional_key in artifact and artifact.get(optional_key) is not False:
            raise FailClosedRuntimeError(f"ACLI Next execution plan failed closed: {optional_key} was not false")


def _normalize_list(value: list[str] | None, default: list[str], field: str) -> list[str]:
    source = default if value is None else value
    if not isinstance(source, list) or not source:
        raise FailClosedRuntimeError(f"ACLI Next execution plan requires {field}")
    normalized = [_require_string(item, field).strip() for item in source]
    if len(set(normalized)) != len(normalized):
        raise FailClosedRuntimeError(f"ACLI Next execution plan requires unique {field}")
    return normalized


def _result(completion: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(completion)
    result["replay_hash"] = completion["artifact_hash"]
    return result


def _persist(replay_path: Path, name: str, artifact: dict[str, Any]) -> None:
    write_json_immutable(replay_path / name, artifact)


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"ACLI Next execution plan requires {field}")
    return value
