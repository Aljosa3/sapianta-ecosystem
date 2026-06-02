"""Read-only approval command group for the deterministic AiGOL CLI."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


APPROVAL_COMMAND_GROUP_VERSION = "APPROVAL_COMMAND_GROUP_V1"

APPROVAL_ARTIFACT_TYPES = frozenset(
    {
        "PROPOSAL_APPROVAL_ARTIFACT_V1",
        "IMPROVEMENT_APPROVAL_ARTIFACT_V1",
    }
)
RETURNED_EVENTS = frozenset(
    {
        "PROPOSAL_APPROVAL_RETURNED",
        "IMPROVEMENT_APPROVAL_RETURNED",
    }
)
STATUS_FILTERS = frozenset({"ALL", "PENDING", "APPROVED", "REJECTED"})


def approval_list_command(*, replay_root: str | Path = ".") -> dict[str, Any]:
    """List governed approval artifacts from replay evidence."""

    return _approval_result(command="aigol approval list", replay_root=replay_root, status_filter="ALL")


def approval_show_command(*, approval_id: str, replay_root: str | Path = ".") -> dict[str, Any]:
    """Show one governed approval artifact from replay evidence."""

    return _approval_result(
        command="aigol approval show",
        replay_root=replay_root,
        approval_id=_require_string(approval_id, "approval_id"),
        status_filter="ALL",
    )


def approval_pending_command(*, replay_root: str | Path = ".") -> dict[str, Any]:
    """Show pending approval artifacts when present."""

    return _approval_result(command="aigol approval pending", replay_root=replay_root, status_filter="PENDING")


def approval_approved_command(*, replay_root: str | Path = ".") -> dict[str, Any]:
    """Show approved approval artifacts."""

    return _approval_result(command="aigol approval approved", replay_root=replay_root, status_filter="APPROVED")


def approval_rejected_command(*, replay_root: str | Path = ".") -> dict[str, Any]:
    """Show rejected approval artifacts."""

    return _approval_result(command="aigol approval rejected", replay_root=replay_root, status_filter="REJECTED")


def approval_chain_command(*, canonical_chain_id: str, replay_root: str | Path = ".") -> dict[str, Any]:
    """Show approvals associated with a canonical chain id."""

    return _approval_result(
        command="aigol approval chain",
        replay_root=replay_root,
        canonical_chain_id=_require_string(canonical_chain_id, "canonical_chain_id"),
        status_filter="ALL",
    )


def render_approval_summary(result: dict[str, Any]) -> str:
    """Render deterministic human-readable approval summary lines."""

    lines = [
        f"status: {result.get('status')}",
        f"replay_root: {result.get('replay_root')}",
        f"approval_count: {result.get('approval_count')}",
        f"status_filter: {result.get('status_filter')}",
        f"canonical_chain_id: {result.get('canonical_chain_id') or ''}",
        f"approval_id: {result.get('approval_id') or ''}",
        f"read_only: {result.get('read_only')}",
        f"execution_requested: {result.get('execution_requested')}",
        f"worker_dispatched: {result.get('worker_dispatched')}",
        f"worker_invoked: {result.get('worker_invoked')}",
        f"governance_mutated: {result.get('governance_mutated')}",
        f"replay_mutated: {result.get('replay_mutated')}",
        f"fail_closed: {result.get('fail_closed')}",
        f"failure_reason: {result.get('failure_reason') or ''}",
    ]
    for entry in result.get("approvals", []):
        lines.append(
            "approval: "
            f"{entry.get('approval_id')} | "
            f"{entry.get('approval_type')} | "
            f"{entry.get('approval_status')} | "
            f"{entry.get('canonical_chain_id') or 'NO_CHAIN'} | "
            f"{entry.get('created_at')}"
        )
    return "\n".join(lines)


def _approval_result(
    *,
    command: str,
    replay_root: str | Path,
    status_filter: str,
    approval_id: str | None = None,
    canonical_chain_id: str | None = None,
) -> dict[str, Any]:
    root = Path(replay_root)
    try:
        entries = _scan_approvals(root)
        entries = _filter_entries(
            entries,
            status_filter=status_filter,
            approval_id=approval_id,
            canonical_chain_id=canonical_chain_id,
        )
        if approval_id is not None and not entries:
            raise FailClosedRuntimeError("approval command failed closed: approval not found")
        result = {
            "command": command,
            "approval_command_group_version": APPROVAL_COMMAND_GROUP_VERSION,
            "status": "READY",
            "replay_root": str(root),
            "approval_id": approval_id,
            "canonical_chain_id": canonical_chain_id,
            "status_filter": status_filter,
            "approval_count": len(entries),
            "approvals": entries,
            "read_only": True,
            "authority": False,
            "execution_requested": False,
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
            "approval_command_group_version": APPROVAL_COMMAND_GROUP_VERSION,
            "status": "FAILED_CLOSED",
            "replay_root": str(root),
            "approval_id": approval_id,
            "canonical_chain_id": canonical_chain_id,
            "status_filter": status_filter,
            "approval_count": 0,
            "approvals": [],
            "read_only": True,
            "authority": False,
            "execution_requested": False,
            "worker_dispatched": False,
            "worker_invoked": False,
            "execution_performed": False,
            "governance_mutated": False,
            "replay_mutated": False,
            "replay_visible": True,
            "fail_closed": True,
            "failure_reason": _failure_reason(exc),
        }
    result["human_readable_summary"] = render_approval_summary(result)
    result["approval_summary_hash"] = replay_hash(result)
    return result


def _scan_approvals(root: Path) -> list[dict[str, Any]]:
    if not root.exists():
        return []
    if not root.is_dir():
        raise FailClosedRuntimeError("approval command failed closed: replay root is not a directory")
    entries: dict[str, dict[str, Any]] = {}
    for path in sorted(root.rglob("*.json")):
        wrapper = _load_json_object(path)
        if wrapper is None:
            continue
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            continue
        artifact_type = artifact.get("artifact_type")
        event_type = wrapper.get("event_type") or artifact.get("event_type")
        if artifact_type not in APPROVAL_ARTIFACT_TYPES and event_type not in RETURNED_EVENTS:
            continue
        _verify_wrapper_hash(wrapper)
        _verify_artifact_hash(artifact, "approval artifact")
        if artifact_type not in APPROVAL_ARTIFACT_TYPES:
            continue
        entry = _entry_from_artifact(artifact=artifact, path=path)
        entries[entry["approval_id"]] = entry
    return sorted(entries.values(), key=lambda entry: (entry["created_at"], entry["approval_id"]))


def _load_json_object(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise FailClosedRuntimeError(f"approval command failed closed: invalid JSON artifact {path.name}") from exc
    return value if isinstance(value, dict) else None


def _entry_from_artifact(*, artifact: dict[str, Any], path: Path) -> dict[str, Any]:
    artifact_type = artifact["artifact_type"]
    if artifact_type == "PROPOSAL_APPROVAL_ARTIFACT_V1":
        approval_id = artifact["approval_id"]
        approval_type = "PROPOSAL_APPROVAL"
        created_at = artifact["created_at"]
        decision = artifact["human_decision"]
        references = {"proposal_id": artifact.get("proposal_id")}
        implementation_authorized = False
    elif artifact_type == "IMPROVEMENT_APPROVAL_ARTIFACT_V1":
        approval_id = artifact["improvement_approval_id"]
        approval_type = "IMPROVEMENT_APPROVAL"
        created_at = artifact["recorded_at"]
        decision = artifact["decision"]
        references = {
            "improvement_review_reference": artifact.get("improvement_review_reference"),
            "improvement_proposal_reference": artifact.get("improvement_proposal_reference"),
            "evaluation_reference": artifact.get("evaluation_reference"),
            "result_reference": artifact.get("result_reference"),
        }
        implementation_authorized = artifact.get("implementation_authorized") is True
    else:
        raise FailClosedRuntimeError("approval command failed closed: unknown approval artifact")
    return {
        "approval_id": approval_id,
        "approval_type": approval_type,
        "artifact_type": artifact_type,
        "approval_status": _approval_status(artifact),
        "decision": decision,
        "canonical_chain_id": artifact.get("canonical_chain_id"),
        "created_at": created_at,
        "replay_reference": artifact.get("replay_reference"),
        "artifact_hash": artifact.get("artifact_hash"),
        "artifact_path": str(path),
        "references": references,
        "implementation_authorized": implementation_authorized,
        "execution_requested": artifact.get("execution_requested") is True,
        "execution_request_created": artifact.get("execution_request_created") is True,
        "worker_dispatched": artifact.get("worker_dispatched") is True,
        "worker_invoked": artifact.get("worker_invoked") is True,
        "governance_mutated": artifact.get("governance_mutated") is True,
        "replay_mutated": artifact.get("replay_mutated") is True,
        "replay_visible": artifact.get("replay_visible") is True,
    }


def _filter_entries(
    entries: list[dict[str, Any]],
    *,
    status_filter: str,
    approval_id: str | None,
    canonical_chain_id: str | None,
) -> list[dict[str, Any]]:
    if status_filter not in STATUS_FILTERS:
        raise FailClosedRuntimeError("approval command failed closed: invalid status filter")
    filtered = list(entries)
    if status_filter != "ALL":
        filtered = [entry for entry in filtered if entry["approval_status"] == status_filter]
    if approval_id is not None:
        filtered = [entry for entry in filtered if entry["approval_id"] == approval_id]
    if canonical_chain_id is not None:
        filtered = [entry for entry in filtered if entry.get("canonical_chain_id") == canonical_chain_id]
    return deepcopy(filtered)


def _approval_status(artifact: dict[str, Any]) -> str:
    status = artifact.get("approval_status")
    if isinstance(status, str) and status.strip():
        return status
    decision = artifact.get("decision")
    if isinstance(decision, str) and decision.strip():
        return decision
    return "PENDING"


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash", None)
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("approval command failed closed: replay hash mismatch")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash", None)
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"approval command failed closed: {field_name} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    return str(exc) or exc.__class__.__name__


__all__ = [
    "APPROVAL_COMMAND_GROUP_VERSION",
    "approval_approved_command",
    "approval_chain_command",
    "approval_list_command",
    "approval_pending_command",
    "approval_rejected_command",
    "approval_show_command",
    "render_approval_summary",
]
