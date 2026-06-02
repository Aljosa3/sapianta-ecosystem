"""Read-only bridge authorization command group for the deterministic AiGOL CLI."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


BRIDGE_AUTHORIZATION_COMMAND_GROUP_VERSION = "BRIDGE_AUTHORIZATION_COMMAND_GROUP_V1"
BRIDGE_LINK_ARTIFACT = "IMPLEMENTATION_PLAN_EXECUTION_REQUEST_LINK_ARTIFACT_V1"
EXECUTION_REQUEST_ARTIFACT = "EXECUTION_REQUEST_ARTIFACT_V1"
IMPLEMENTATION_PLAN_SOURCE = "IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1"
STATUS_FILTERS = frozenset({"ALL", "PENDING", "APPROVED", "REJECTED"})


def bridge_list_command(*, replay_root: str | Path = ".") -> dict[str, Any]:
    """List bridge authorization transitions from replay evidence."""

    return _bridge_result(command="aigol bridge list", replay_root=replay_root, status_filter="ALL")


def bridge_show_command(*, bridge_id: str, replay_root: str | Path = ".") -> dict[str, Any]:
    """Show one bridge authorization transition."""

    return _bridge_result(
        command="aigol bridge show",
        replay_root=replay_root,
        bridge_id=_require_string(bridge_id, "bridge_id"),
        status_filter="ALL",
    )


def bridge_pending_command(*, replay_root: str | Path = ".") -> dict[str, Any]:
    """Show pending bridge transitions when replay-visible evidence exists."""

    return _bridge_result(command="aigol bridge pending", replay_root=replay_root, status_filter="PENDING")


def bridge_approved_command(*, replay_root: str | Path = ".") -> dict[str, Any]:
    """Show approved bridge transitions."""

    return _bridge_result(command="aigol bridge approved", replay_root=replay_root, status_filter="APPROVED")


def bridge_rejected_command(*, replay_root: str | Path = ".") -> dict[str, Any]:
    """Show rejected bridge transitions when replay-visible evidence exists."""

    return _bridge_result(command="aigol bridge rejected", replay_root=replay_root, status_filter="REJECTED")


def bridge_chain_command(*, canonical_chain_id: str, replay_root: str | Path = ".") -> dict[str, Any]:
    """Show bridge transitions associated with a canonical chain id."""

    return _bridge_result(
        command="aigol bridge chain",
        replay_root=replay_root,
        canonical_chain_id=_require_string(canonical_chain_id, "canonical_chain_id"),
        status_filter="ALL",
    )


def bridge_execution_request_command(
    *, execution_request_id: str, replay_root: str | Path = "."
) -> dict[str, Any]:
    """Show bridge transitions for an execution request id."""

    return _bridge_result(
        command="aigol bridge execution-request",
        replay_root=replay_root,
        execution_request_id=_require_string(execution_request_id, "execution_request_id"),
        status_filter="ALL",
    )


def render_bridge_summary(result: dict[str, Any]) -> str:
    """Render deterministic human-readable bridge summary lines."""

    lines = [
        f"status: {result.get('status')}",
        f"replay_root: {result.get('replay_root')}",
        f"bridge_count: {result.get('bridge_count')}",
        f"status_filter: {result.get('status_filter')}",
        f"bridge_id: {result.get('bridge_id') or ''}",
        f"canonical_chain_id: {result.get('canonical_chain_id') or ''}",
        f"execution_request_id: {result.get('execution_request_id') or ''}",
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
    for entry in result.get("bridges", []):
        lines.append(
            "bridge: "
            f"{entry.get('bridge_id')} | "
            f"{entry.get('authorization_status')} | "
            f"{entry.get('canonical_chain_id') or 'NO_CHAIN'} | "
            f"{entry.get('execution_request_id') or 'NO_REQUEST'} | "
            f"{entry.get('created_at')}"
        )
    return "\n".join(lines)


def _bridge_result(
    *,
    command: str,
    replay_root: str | Path,
    status_filter: str,
    bridge_id: str | None = None,
    canonical_chain_id: str | None = None,
    execution_request_id: str | None = None,
) -> dict[str, Any]:
    root = Path(replay_root)
    try:
        entries = _scan_bridges(root)
        entries = _filter_entries(
            entries,
            status_filter=status_filter,
            bridge_id=bridge_id,
            canonical_chain_id=canonical_chain_id,
            execution_request_id=execution_request_id,
        )
        if bridge_id is not None and not entries:
            raise FailClosedRuntimeError("bridge command failed closed: bridge not found")
        if execution_request_id is not None and not entries:
            raise FailClosedRuntimeError("bridge command failed closed: execution request not found")
        result = {
            "command": command,
            "bridge_authorization_command_group_version": BRIDGE_AUTHORIZATION_COMMAND_GROUP_VERSION,
            "status": "READY",
            "replay_root": str(root),
            "bridge_id": bridge_id,
            "canonical_chain_id": canonical_chain_id,
            "execution_request_id": execution_request_id,
            "status_filter": status_filter,
            "bridge_count": len(entries),
            "bridges": entries,
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
            "bridge_authorization_command_group_version": BRIDGE_AUTHORIZATION_COMMAND_GROUP_VERSION,
            "status": "FAILED_CLOSED",
            "replay_root": str(root),
            "bridge_id": bridge_id,
            "canonical_chain_id": canonical_chain_id,
            "execution_request_id": execution_request_id,
            "status_filter": status_filter,
            "bridge_count": 0,
            "bridges": [],
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
    result["human_readable_summary"] = render_bridge_summary(result)
    result["bridge_summary_hash"] = replay_hash(result)
    return result


def _scan_bridges(root: Path) -> list[dict[str, Any]]:
    if not root.exists():
        return []
    if not root.is_dir():
        raise FailClosedRuntimeError("bridge command failed closed: replay root is not a directory")
    links: dict[str, dict[str, Any]] = {}
    requests: dict[str, dict[str, Any]] = {}
    for path in sorted(root.rglob("*.json")):
        wrapper = _load_json_object(path)
        if wrapper is None:
            continue
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            continue
        artifact_type = artifact.get("artifact_type")
        if not _is_bridge_related(artifact):
            continue
        _verify_wrapper_hash(wrapper)
        _verify_artifact_hash(artifact, "bridge artifact")
        if artifact_type == BRIDGE_LINK_ARTIFACT:
            entry = _entry_from_link(artifact=artifact, path=path)
            links[entry["bridge_id"]] = entry
        elif artifact_type == EXECUTION_REQUEST_ARTIFACT:
            requests[artifact["execution_request_id"]] = {
                "artifact_path": str(path),
                "artifact_hash": artifact.get("artifact_hash"),
                "request_status": artifact.get("status"),
                "request_payload_hash": artifact.get("request_payload_hash"),
            }
    for entry in links.values():
        request = requests.get(entry.get("execution_request_id"))
        if request is not None:
            entry["execution_request_artifact_path"] = request["artifact_path"]
            entry["execution_request_artifact_hash"] = request["artifact_hash"]
            entry["execution_request_status"] = request["request_status"]
            entry["request_payload_hash"] = request["request_payload_hash"]
    return sorted(links.values(), key=lambda entry: (entry["created_at"], entry["bridge_id"]))


def _entry_from_link(*, artifact: dict[str, Any], path: Path) -> dict[str, Any]:
    return {
        "bridge_id": artifact["bridge_id"],
        "authorization_status": _authorization_status(artifact),
        "canonical_chain_id": artifact.get("canonical_chain_id"),
        "execution_request_id": artifact.get("execution_request_reference"),
        "execution_request_hash": artifact.get("execution_request_hash"),
        "implementation_plan_reference": artifact.get("implementation_plan_reference"),
        "implementation_plan_hash": artifact.get("implementation_plan_hash"),
        "improvement_approval_reference": artifact.get("improvement_approval_reference"),
        "improvement_approval_hash": artifact.get("improvement_approval_hash"),
        "human_authorization_reference": artifact.get("human_authorization_reference"),
        "requested_by": artifact.get("requested_by"),
        "created_at": artifact.get("created_at"),
        "replay_reference": artifact.get("replay_reference"),
        "artifact_hash": artifact.get("artifact_hash"),
        "artifact_path": str(path),
        "execution_request_artifact_path": None,
        "execution_request_artifact_hash": None,
        "execution_request_status": None,
        "request_payload_hash": None,
        "execution_request_created": artifact.get("execution_request_created") is True,
        "automatic_execution_request": artifact.get("automatic_execution_request") is True,
        "automatic_authorization": artifact.get("automatic_authorization") is True,
        "worker_dispatched": artifact.get("worker_dispatched") is True,
        "worker_invoked": artifact.get("worker_invoked") is True,
        "execution_performed": artifact.get("execution_performed") is True,
        "governance_mutated": artifact.get("governance_mutated") is True,
        "replay_mutated": artifact.get("replay_mutated") is True,
        "replay_visible": artifact.get("replay_visible") is True,
    }


def _filter_entries(
    entries: list[dict[str, Any]],
    *,
    status_filter: str,
    bridge_id: str | None,
    canonical_chain_id: str | None,
    execution_request_id: str | None,
) -> list[dict[str, Any]]:
    if status_filter not in STATUS_FILTERS:
        raise FailClosedRuntimeError("bridge command failed closed: invalid status filter")
    filtered = list(entries)
    if status_filter != "ALL":
        filtered = [entry for entry in filtered if entry["authorization_status"] == status_filter]
    if bridge_id is not None:
        filtered = [entry for entry in filtered if entry["bridge_id"] == bridge_id]
    if canonical_chain_id is not None:
        filtered = [entry for entry in filtered if entry.get("canonical_chain_id") == canonical_chain_id]
    if execution_request_id is not None:
        filtered = [entry for entry in filtered if entry.get("execution_request_id") == execution_request_id]
    return deepcopy(filtered)


def _authorization_status(artifact: dict[str, Any]) -> str:
    for field in ("authorization_status", "bridge_status", "approval_status", "decision", "status"):
        value = artifact.get(field)
        if isinstance(value, str) and value.strip():
            normalized = value.strip().upper()
            if normalized in {"APPROVED", "AUTHORIZED", "CREATED"}:
                return "APPROVED"
            if normalized in {"REJECTED", "REJECT"}:
                return "REJECTED"
            if normalized in {"PENDING", "READY", "REQUESTED"}:
                return "PENDING"
    if artifact.get("execution_request_created") is True and artifact.get("automatic_authorization") is False:
        return "APPROVED"
    if artifact.get("execution_request_created") is False:
        return "PENDING"
    return "PENDING"


def _is_bridge_related(artifact: dict[str, Any]) -> bool:
    artifact_type = artifact.get("artifact_type")
    if artifact_type == BRIDGE_LINK_ARTIFACT:
        return True
    return (
        artifact_type == EXECUTION_REQUEST_ARTIFACT
        and artifact.get("execution_request_source_type") == IMPLEMENTATION_PLAN_SOURCE
    )


def _load_json_object(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise FailClosedRuntimeError(f"bridge command failed closed: invalid JSON artifact {path.name}") from exc
    return value if isinstance(value, dict) else None


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash", None)
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("bridge command failed closed: replay hash mismatch")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash", None)
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"bridge command failed closed: {field_name} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    return str(exc) or exc.__class__.__name__


__all__ = [
    "BRIDGE_AUTHORIZATION_COMMAND_GROUP_VERSION",
    "bridge_approved_command",
    "bridge_chain_command",
    "bridge_execution_request_command",
    "bridge_list_command",
    "bridge_pending_command",
    "bridge_rejected_command",
    "bridge_show_command",
    "render_bridge_summary",
]
