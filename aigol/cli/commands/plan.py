"""Read-only implementation plan inspection command group for AiGOL CLI."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


IMPLEMENTATION_PLAN_INSPECTION_COMMAND_GROUP_VERSION = (
    "IMPLEMENTATION_PLAN_INSPECTION_COMMAND_GROUP_V1"
)
IMPLEMENTATION_PLAN_ARTIFACT = "IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1"
BRIDGE_LINK_ARTIFACT = "IMPLEMENTATION_PLAN_EXECUTION_REQUEST_LINK_ARTIFACT_V1"
EXECUTION_REQUEST_ARTIFACT = "EXECUTION_REQUEST_ARTIFACT_V1"
PLAN_RETURNED_EVENT = "IMPROVEMENT_IMPLEMENTATION_PLAN_RETURNED"
APPROVED_STATUSES = frozenset({"IMPLEMENTATION_PLAN_CREATED", "APPROVED", "AUTHORIZED", "CREATED"})


def plan_list_command(*, replay_root: str | Path = ".") -> dict[str, Any]:
    """List replay-visible implementation plans."""

    return _plan_result(command="aigol plan list", replay_root=replay_root)


def plan_show_command(*, implementation_plan_id: str, replay_root: str | Path = ".") -> dict[str, Any]:
    """Show a single replay-visible implementation plan."""

    return _plan_result(
        command="aigol plan show",
        replay_root=replay_root,
        implementation_plan_id=_require_string(implementation_plan_id, "implementation_plan_id"),
    )


def plan_approved_command(*, replay_root: str | Path = ".") -> dict[str, Any]:
    """List implementation plans authorized by governed approval evidence."""

    return _plan_result(command="aigol plan approved", replay_root=replay_root, approved_only=True)


def plan_chain_command(*, canonical_chain_id: str, replay_root: str | Path = ".") -> dict[str, Any]:
    """List implementation plans for a canonical chain id."""

    return _plan_result(
        command="aigol plan chain",
        replay_root=replay_root,
        canonical_chain_id=_require_string(canonical_chain_id, "canonical_chain_id"),
    )


def plan_bridge_command(*, bridge_id: str, replay_root: str | Path = ".") -> dict[str, Any]:
    """List implementation plans linked to a bridge authorization id."""

    return _plan_result(
        command="aigol plan bridge",
        replay_root=replay_root,
        bridge_id=_require_string(bridge_id, "bridge_id"),
    )


def plan_execution_request_command(
    *, execution_request_id: str, replay_root: str | Path = "."
) -> dict[str, Any]:
    """List implementation plans linked to an execution request id."""

    return _plan_result(
        command="aigol plan execution-request",
        replay_root=replay_root,
        execution_request_id=_require_string(execution_request_id, "execution_request_id"),
    )


def plan_latest_command(*, replay_root: str | Path = ".") -> dict[str, Any]:
    """Show the latest replay-visible implementation plan."""

    return _plan_result(command="aigol plan latest", replay_root=replay_root, latest_only=True)


def render_plan_summary(result: dict[str, Any]) -> str:
    """Render deterministic human-readable implementation plan summary lines."""

    lines = [
        f"status: {result.get('status')}",
        f"replay_root: {result.get('replay_root')}",
        f"plan_count: {result.get('plan_count')}",
        f"implementation_plan_id: {result.get('implementation_plan_id') or ''}",
        f"canonical_chain_id: {result.get('canonical_chain_id') or ''}",
        f"bridge_id: {result.get('bridge_id') or ''}",
        f"execution_request_id: {result.get('execution_request_id') or ''}",
        f"approved_only: {result.get('approved_only')}",
        f"latest_only: {result.get('latest_only')}",
        f"read_only: {result.get('read_only')}",
        f"execution_requests_created: {result.get('execution_requests_created')}",
        f"worker_dispatched: {result.get('worker_dispatched')}",
        f"worker_invoked: {result.get('worker_invoked')}",
        f"execution_performed: {result.get('execution_performed')}",
        f"governance_mutated: {result.get('governance_mutated')}",
        f"replay_mutated: {result.get('replay_mutated')}",
        f"fail_closed: {result.get('fail_closed')}",
        f"failure_reason: {result.get('failure_reason') or ''}",
    ]
    for entry in result.get("plans", []):
        lines.append(
            "plan: "
            f"{entry.get('implementation_plan_id')} | "
            f"{entry.get('plan_status')} | "
            f"{entry.get('canonical_chain_id') or 'NO_CHAIN'} | "
            f"{entry.get('bridge_id') or 'NO_BRIDGE'} | "
            f"{entry.get('execution_request_id') or 'NO_REQUEST'} | "
            f"{entry.get('created_at')}"
        )
    return "\n".join(lines)


def _plan_result(
    *,
    command: str,
    replay_root: str | Path,
    implementation_plan_id: str | None = None,
    canonical_chain_id: str | None = None,
    bridge_id: str | None = None,
    execution_request_id: str | None = None,
    approved_only: bool = False,
    latest_only: bool = False,
) -> dict[str, Any]:
    root = Path(replay_root)
    try:
        entries = _scan_plans(root)
        entries = _filter_entries(
            entries,
            implementation_plan_id=implementation_plan_id,
            canonical_chain_id=canonical_chain_id,
            bridge_id=bridge_id,
            execution_request_id=execution_request_id,
            approved_only=approved_only,
            latest_only=latest_only,
        )
        if implementation_plan_id is not None and not entries:
            raise FailClosedRuntimeError("plan command failed closed: implementation plan not found")
        if bridge_id is not None and not entries:
            raise FailClosedRuntimeError("plan command failed closed: bridge reference not found")
        if execution_request_id is not None and not entries:
            raise FailClosedRuntimeError("plan command failed closed: execution request reference not found")
        if latest_only and not entries:
            raise FailClosedRuntimeError("plan command failed closed: latest implementation plan not found")
        result = {
            "command": command,
            "implementation_plan_inspection_command_group_version": (
                IMPLEMENTATION_PLAN_INSPECTION_COMMAND_GROUP_VERSION
            ),
            "status": "READY",
            "replay_root": str(root),
            "implementation_plan_id": implementation_plan_id,
            "canonical_chain_id": canonical_chain_id,
            "bridge_id": bridge_id,
            "execution_request_id": execution_request_id,
            "approved_only": approved_only,
            "latest_only": latest_only,
            "plan_count": len(entries),
            "plans": entries,
            "read_only": True,
            "authority": False,
            "execution_requests_created": False,
            "worker_dispatched": False,
            "worker_invoked": False,
            "execution_performed": False,
            "governance_mutated": False,
            "replay_mutated": False,
            "replay_visible": True,
            "fail_closed": False,
            "failure_reason": None,
        }
    except Exception as exc:
        result = {
            "command": command,
            "implementation_plan_inspection_command_group_version": (
                IMPLEMENTATION_PLAN_INSPECTION_COMMAND_GROUP_VERSION
            ),
            "status": "FAILED_CLOSED",
            "replay_root": str(root),
            "implementation_plan_id": implementation_plan_id,
            "canonical_chain_id": canonical_chain_id,
            "bridge_id": bridge_id,
            "execution_request_id": execution_request_id,
            "approved_only": approved_only,
            "latest_only": latest_only,
            "plan_count": 0,
            "plans": [],
            "read_only": True,
            "authority": False,
            "execution_requests_created": False,
            "worker_dispatched": False,
            "worker_invoked": False,
            "execution_performed": False,
            "governance_mutated": False,
            "replay_mutated": False,
            "replay_visible": True,
            "fail_closed": True,
            "failure_reason": _failure_reason(exc),
        }
    result["human_readable_summary"] = render_plan_summary(result)
    result["plan_summary_hash"] = replay_hash(result)
    return result


def _scan_plans(root: Path) -> list[dict[str, Any]]:
    if not root.exists():
        return []
    if not root.is_dir():
        raise FailClosedRuntimeError("plan command failed closed: replay root is not a directory")

    plans: dict[str, dict[str, Any]] = {}
    bridge_links: dict[str, dict[str, Any]] = {}
    requests_by_plan: dict[str, dict[str, Any]] = {}

    for path in sorted(root.rglob("*.json")):
        wrapper = _load_json_object(path)
        if wrapper is None:
            continue
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            continue
        if not _is_plan_related(artifact, wrapper):
            continue
        _verify_wrapper_hash(wrapper)
        _verify_artifact_hash(artifact, "implementation plan inspection artifact")
        artifact_type = artifact.get("artifact_type")
        if artifact_type == IMPLEMENTATION_PLAN_ARTIFACT:
            entry = _entry_from_plan_artifact(artifact=artifact, path=path)
            plans[entry["implementation_plan_id"]] = entry
        elif artifact_type == BRIDGE_LINK_ARTIFACT:
            plan_id = artifact.get("implementation_plan_reference")
            if isinstance(plan_id, str) and plan_id.strip():
                bridge_links[plan_id] = _bridge_reference(artifact=artifact, path=path)
        elif artifact_type == EXECUTION_REQUEST_ARTIFACT:
            plan_id = artifact.get("implementation_plan_reference")
            if isinstance(plan_id, str) and plan_id.strip():
                requests_by_plan[plan_id] = _request_reference(artifact=artifact, path=path)

    for plan_id, entry in plans.items():
        bridge = bridge_links.get(plan_id)
        if bridge is not None:
            entry.update(bridge)
        request = requests_by_plan.get(plan_id)
        if request is not None:
            entry.update(request)
        _validate_plan_entry_continuity(entry)
    return sorted(plans.values(), key=lambda entry: (entry["created_at"], entry["implementation_plan_id"]))


def _entry_from_plan_artifact(*, artifact: dict[str, Any], path: Path) -> dict[str, Any]:
    _verify_nested_hashes(artifact)
    return {
        "implementation_plan_id": artifact["implementation_plan_id"],
        "artifact_type": artifact.get("artifact_type"),
        "plan_status": artifact.get("plan_status"),
        "canonical_chain_id": artifact.get("canonical_chain_id"),
        "improvement_approval_reference": artifact.get("improvement_approval_reference"),
        "improvement_approval_hash": artifact.get("improvement_approval_hash"),
        "improvement_review_reference": artifact.get("improvement_review_reference"),
        "improvement_review_hash": artifact.get("improvement_review_hash"),
        "improvement_proposal_reference": artifact.get("improvement_proposal_reference"),
        "improvement_proposal_hash": artifact.get("improvement_proposal_hash"),
        "evaluation_reference": artifact.get("evaluation_reference"),
        "evaluation_hash": artifact.get("evaluation_hash"),
        "result_reference": artifact.get("result_reference"),
        "result_hash": artifact.get("result_hash"),
        "worker_reference": artifact.get("worker_reference"),
        "human_authorization_reference": artifact.get("human_authorization_reference"),
        "plan_source": artifact.get("plan_source"),
        "plan_text_hash": artifact.get("plan_text_hash"),
        "plan_scope": deepcopy(artifact.get("plan_scope")),
        "plan_scope_hash": artifact.get("plan_scope_hash"),
        "plan_constraints": deepcopy(artifact.get("plan_constraints")),
        "plan_constraints_hash": artifact.get("plan_constraints_hash"),
        "planned_artifact_targets": list(artifact.get("planned_artifact_targets") or []),
        "planned_artifact_targets_hash": artifact.get("planned_artifact_targets_hash"),
        "planned_validation": list(artifact.get("planned_validation") or []),
        "planned_validation_hash": artifact.get("planned_validation_hash"),
        "implementation_authorized": artifact.get("implementation_authorized") is True,
        "implementation_performed": artifact.get("implementation_performed") is True,
        "execution_request_created": artifact.get("execution_request_created") is True,
        "execution_request_id": artifact.get("execution_request_reference"),
        "bridge_id": None,
        "bridge_artifact_hash": None,
        "bridge_artifact_path": None,
        "execution_request_artifact_hash": None,
        "execution_request_artifact_path": None,
        "execution_request_status": None,
        "created_by": artifact.get("created_by"),
        "created_at": artifact.get("created_at"),
        "replay_reference": artifact.get("replay_reference"),
        "replay_visible": artifact.get("replay_visible") is True,
        "artifact_hash": artifact.get("artifact_hash"),
        "artifact_path": str(path),
        "provider_authority": artifact.get("provider_authority") is True,
        "worker_authority": artifact.get("worker_authority") is True,
        "worker_dispatched": artifact.get("worker_dispatched") is True,
        "worker_invoked": artifact.get("worker_invoked") is True,
        "governance_mutated": artifact.get("governance_mutated") is True,
        "replay_mutated": artifact.get("replay_mutated") is True,
    }


def _bridge_reference(*, artifact: dict[str, Any], path: Path) -> dict[str, Any]:
    return {
        "bridge_id": artifact.get("bridge_id"),
        "bridge_artifact_hash": artifact.get("artifact_hash"),
        "bridge_artifact_path": str(path),
        "execution_request_id": artifact.get("execution_request_reference"),
        "execution_request_created": artifact.get("execution_request_created") is True,
    }


def _request_reference(*, artifact: dict[str, Any], path: Path) -> dict[str, Any]:
    return {
        "execution_request_id": artifact.get("execution_request_id"),
        "execution_request_artifact_hash": artifact.get("artifact_hash"),
        "execution_request_artifact_path": str(path),
        "execution_request_status": artifact.get("status"),
    }


def _filter_entries(
    entries: list[dict[str, Any]],
    *,
    implementation_plan_id: str | None,
    canonical_chain_id: str | None,
    bridge_id: str | None,
    execution_request_id: str | None,
    approved_only: bool,
    latest_only: bool,
) -> list[dict[str, Any]]:
    filtered = list(entries)
    if implementation_plan_id is not None:
        filtered = [entry for entry in filtered if entry["implementation_plan_id"] == implementation_plan_id]
    if canonical_chain_id is not None:
        filtered = [entry for entry in filtered if entry.get("canonical_chain_id") == canonical_chain_id]
    if bridge_id is not None:
        filtered = [entry for entry in filtered if entry.get("bridge_id") == bridge_id]
    if execution_request_id is not None:
        filtered = [entry for entry in filtered if entry.get("execution_request_id") == execution_request_id]
    if approved_only:
        filtered = [
            entry
            for entry in filtered
            if entry.get("implementation_authorized") is True
            and str(entry.get("plan_status") or "").upper() in APPROVED_STATUSES
        ]
    filtered = sorted(
        filtered,
        key=lambda entry: (entry.get("created_at") or "", entry.get("implementation_plan_id") or ""),
        reverse=latest_only,
    )
    if latest_only:
        filtered = filtered[:1]
    return deepcopy(filtered)


def _is_plan_related(artifact: dict[str, Any], wrapper: dict[str, Any]) -> bool:
    artifact_type = artifact.get("artifact_type")
    if artifact_type == IMPLEMENTATION_PLAN_ARTIFACT:
        return True
    if wrapper.get("event_type") == PLAN_RETURNED_EVENT:
        return True
    if artifact_type == BRIDGE_LINK_ARTIFACT:
        return artifact.get("execution_request_source_type") == IMPLEMENTATION_PLAN_ARTIFACT
    return (
        artifact_type == EXECUTION_REQUEST_ARTIFACT
        and artifact.get("execution_request_source_type") == IMPLEMENTATION_PLAN_ARTIFACT
    )


def _validate_plan_entry_continuity(entry: dict[str, Any]) -> None:
    if entry.get("replay_visible") is not True:
        raise FailClosedRuntimeError("plan command failed closed: replay visibility missing")
    for field in (
        "provider_authority",
        "worker_authority",
        "worker_dispatched",
        "worker_invoked",
        "implementation_performed",
        "governance_mutated",
        "replay_mutated",
    ):
        if entry.get(field) is True:
            raise FailClosedRuntimeError("plan command failed closed: invalid implementation plan authority")
    if entry.get("bridge_id") and not entry.get("execution_request_id"):
        raise FailClosedRuntimeError("plan command failed closed: invalid bridge reference")


def _verify_nested_hashes(artifact: dict[str, Any]) -> None:
    nested_fields = (
        ("plan_text", "plan_text_hash"),
        ("plan_scope", "plan_scope_hash"),
        ("plan_constraints", "plan_constraints_hash"),
        ("planned_artifact_targets", "planned_artifact_targets_hash"),
        ("planned_validation", "planned_validation_hash"),
    )
    for value_field, hash_field in nested_fields:
        if hash_field in artifact and artifact.get(hash_field) != replay_hash(artifact.get(value_field)):
            raise FailClosedRuntimeError("plan command failed closed: implementation plan nested hash mismatch")


def _load_json_object(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise FailClosedRuntimeError(f"plan command failed closed: invalid JSON artifact {path.name}") from exc
    return value if isinstance(value, dict) else None


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash", None)
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("plan command failed closed: replay hash mismatch")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash", None)
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"plan command failed closed: {field_name} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    return str(exc) or exc.__class__.__name__


__all__ = [
    "IMPLEMENTATION_PLAN_INSPECTION_COMMAND_GROUP_VERSION",
    "plan_approved_command",
    "plan_bridge_command",
    "plan_chain_command",
    "plan_execution_request_command",
    "plan_latest_command",
    "plan_list_command",
    "plan_show_command",
    "render_plan_summary",
]
