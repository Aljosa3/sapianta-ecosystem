"""Read-only session dashboard for the deterministic AiGOL CLI."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from aigol.cli.commands.approval import approval_list_command, approval_pending_command
from aigol.cli.commands.bridge import bridge_list_command, bridge_pending_command
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


SESSION_DASHBOARD_RUNTIME_VERSION = "SESSION_DASHBOARD_RUNTIME_V1"

EXECUTION_ARTIFACT_TYPES = frozenset(
    {
        "EXECUTION_REQUEST_ARTIFACT_V1",
        "READY_FOR_DISPATCH_ARTIFACT_V1",
        "DISPATCH_ARTIFACT_V1",
        "WORKER_INVOCATION_ARTIFACT_V1",
        "EXECUTION_ARTIFACT_V1",
        "COMPLETION_ARTIFACT_V1",
        "RESULT_ARTIFACT_V1",
        "RESULT_EVALUATION_ARTIFACT_V1",
    }
)
LEARNING_ARTIFACT_TYPES = frozenset(
    {
        "RESULT_EVALUATION_ARTIFACT_V1",
        "IMPROVEMENT_PROPOSAL_ARTIFACT_V1",
        "IMPROVEMENT_REVIEW_ARTIFACT_V1",
        "IMPROVEMENT_APPROVAL_ARTIFACT_V1",
        "IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1",
    }
)
CHAIN_ID_FIELDS = ("canonical_chain_id", "current_chain_id", "latest_chain_id", "related_chain_id")
TIME_FIELDS = ("created_at", "recorded_at", "started_at", "completed_at", "evaluated_at", "assigned_at", "invoked_at")


def dashboard_command(*, replay_root: str | Path = ".", limit: int = 10) -> dict[str, Any]:
    """Return a full read-only operator dashboard."""

    return _dashboard_result(command="aigol dashboard", replay_root=replay_root, section="summary", limit=limit)


def dashboard_summary_command(*, replay_root: str | Path = ".", limit: int = 10) -> dict[str, Any]:
    """Return a read-only operator dashboard summary."""

    return _dashboard_result(command="aigol dashboard summary", replay_root=replay_root, section="summary", limit=limit)


def dashboard_approvals_command(*, replay_root: str | Path = ".", limit: int = 10) -> dict[str, Any]:
    """Return dashboard approval section."""

    return _dashboard_result(command="aigol dashboard approvals", replay_root=replay_root, section="approvals", limit=limit)


def dashboard_bridges_command(*, replay_root: str | Path = ".", limit: int = 10) -> dict[str, Any]:
    """Return dashboard bridge section."""

    return _dashboard_result(command="aigol dashboard bridges", replay_root=replay_root, section="bridges", limit=limit)


def dashboard_chains_command(*, replay_root: str | Path = ".", limit: int = 10) -> dict[str, Any]:
    """Return dashboard chain section."""

    return _dashboard_result(command="aigol dashboard chains", replay_root=replay_root, section="chains", limit=limit)


def dashboard_learning_command(*, replay_root: str | Path = ".", limit: int = 10) -> dict[str, Any]:
    """Return dashboard learning section."""

    return _dashboard_result(command="aigol dashboard learning", replay_root=replay_root, section="learning", limit=limit)


def dashboard_execution_command(*, replay_root: str | Path = ".", limit: int = 10) -> dict[str, Any]:
    """Return dashboard execution section."""

    return _dashboard_result(command="aigol dashboard execution", replay_root=replay_root, section="execution", limit=limit)


def render_dashboard_summary(result: dict[str, Any]) -> str:
    """Render deterministic human-readable dashboard summary lines."""

    counts = result.get("counts", {})
    lines = [
        f"status: {result.get('status')}",
        f"section: {result.get('section')}",
        f"replay_root: {result.get('replay_root')}",
        f"latest_chain_id: {result.get('latest_chain_id') or ''}",
        f"chain_count: {counts.get('chains')}",
        f"pending_approvals: {counts.get('pending_approvals')}",
        f"pending_bridges: {counts.get('pending_bridges')}",
        f"recent_execution_requests: {counts.get('recent_execution_requests')}",
        f"recent_learning_artifacts: {counts.get('recent_learning_artifacts')}",
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
    for action in result.get("suggested_safe_next_actions", []):
        lines.append(f"safe_next_action: {action}")
    for chain in result.get("latest_chains", []):
        lines.append(f"chain: {chain.get('canonical_chain_id')} | {chain.get('latest_at')} | {chain.get('artifact_count')}")
    return "\n".join(lines)


def _dashboard_result(*, command: str, replay_root: str | Path, section: str, limit: int) -> dict[str, Any]:
    root = Path(replay_root)
    try:
        if limit <= 0:
            raise FailClosedRuntimeError("dashboard failed closed: limit must be positive")
        artifacts = _scan_replay_artifacts(root)
        approvals = approval_list_command(replay_root=root)
        pending_approvals = approval_pending_command(replay_root=root)
        bridges = bridge_list_command(replay_root=root)
        pending_bridges = bridge_pending_command(replay_root=root)
        _raise_if_section_failed(approvals, "approval")
        _raise_if_section_failed(pending_approvals, "pending approval")
        _raise_if_section_failed(bridges, "bridge")
        _raise_if_section_failed(pending_bridges, "pending bridge")
        latest_chains = _latest_chains(artifacts, limit=limit)
        execution_requests = _recent_execution_requests(artifacts, limit=limit)
        learning = _recent_learning_artifacts(artifacts, limit=limit)
        result = {
            "command": command,
            "session_dashboard_runtime_version": SESSION_DASHBOARD_RUNTIME_VERSION,
            "status": "READY",
            "section": section,
            "replay_root": str(root),
            "latest_chain_id": latest_chains[0]["canonical_chain_id"] if latest_chains else None,
            "latest_chains": latest_chains,
            "pending_approvals": pending_approvals.get("approvals", [])[:limit],
            "approvals": approvals.get("approvals", [])[:limit],
            "pending_bridges": pending_bridges.get("bridges", [])[:limit],
            "bridges": bridges.get("bridges", [])[:limit],
            "recent_execution_requests": execution_requests,
            "recent_learning_artifacts": learning,
            "suggested_safe_next_actions": _safe_next_actions(
                latest_chains=latest_chains,
                pending_approval_count=pending_approvals.get("approval_count", 0),
                pending_bridge_count=pending_bridges.get("bridge_count", 0),
            ),
            "counts": {
                "chains": len(latest_chains),
                "pending_approvals": pending_approvals.get("approval_count", 0),
                "approvals": approvals.get("approval_count", 0),
                "pending_bridges": pending_bridges.get("bridge_count", 0),
                "bridges": bridges.get("bridge_count", 0),
                "recent_execution_requests": len(execution_requests),
                "recent_learning_artifacts": len(learning),
            },
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
            "session_dashboard_runtime_version": SESSION_DASHBOARD_RUNTIME_VERSION,
            "status": "FAILED_CLOSED",
            "section": section,
            "replay_root": str(root),
            "latest_chain_id": None,
            "latest_chains": [],
            "pending_approvals": [],
            "approvals": [],
            "pending_bridges": [],
            "bridges": [],
            "recent_execution_requests": [],
            "recent_learning_artifacts": [],
            "suggested_safe_next_actions": [],
            "counts": {
                "chains": 0,
                "pending_approvals": 0,
                "approvals": 0,
                "pending_bridges": 0,
                "bridges": 0,
                "recent_execution_requests": 0,
                "recent_learning_artifacts": 0,
            },
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
    result["human_readable_summary"] = render_dashboard_summary(result)
    result["dashboard_hash"] = replay_hash(result)
    return result


def _scan_replay_artifacts(root: Path) -> list[dict[str, Any]]:
    if not root.exists():
        return []
    if not root.is_dir():
        raise FailClosedRuntimeError("dashboard failed closed: replay root is not a directory")
    artifacts: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*.json")):
        wrapper = _load_json_object(path)
        if wrapper is None:
            continue
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            continue
        artifact_type = artifact.get("artifact_type") or artifact.get("event_type") or wrapper.get("event_type")
        if not _is_dashboard_relevant(artifact):
            continue
        _verify_wrapper_hash(wrapper)
        if "artifact_hash" in artifact:
            _verify_artifact_hash(artifact, "dashboard artifact")
        artifacts.append(
            {
                "artifact": artifact,
                "artifact_type": artifact_type,
                "artifact_path": str(path),
                "created_at": _artifact_time(artifact),
            }
        )
    return artifacts


def _latest_chains(artifacts: list[dict[str, Any]], *, limit: int) -> list[dict[str, Any]]:
    chains: dict[str, dict[str, Any]] = {}
    for item in artifacts:
        artifact = item["artifact"]
        for field in CHAIN_ID_FIELDS:
            chain_id = artifact.get(field)
            if isinstance(chain_id, str) and chain_id.strip():
                entry = chains.setdefault(
                    chain_id,
                    {"canonical_chain_id": chain_id, "artifact_count": 0, "latest_at": "", "artifact_types": set()},
                )
                entry["artifact_count"] += 1
                entry["latest_at"] = max(entry["latest_at"], item["created_at"])
                entry["artifact_types"].add(item["artifact_type"])
    normalized = []
    for entry in chains.values():
        normalized.append(
            {
                "canonical_chain_id": entry["canonical_chain_id"],
                "artifact_count": entry["artifact_count"],
                "latest_at": entry["latest_at"],
                "artifact_types": sorted(entry["artifact_types"]),
            }
        )
    return sorted(normalized, key=lambda entry: (entry["latest_at"], entry["canonical_chain_id"]), reverse=True)[:limit]


def _recent_execution_requests(artifacts: list[dict[str, Any]], *, limit: int) -> list[dict[str, Any]]:
    entries = []
    for item in artifacts:
        artifact = item["artifact"]
        if artifact.get("artifact_type") != "EXECUTION_REQUEST_ARTIFACT_V1":
            continue
        entries.append(
            {
                "execution_request_id": artifact.get("execution_request_id"),
                "canonical_chain_id": artifact.get("canonical_chain_id"),
                "status": artifact.get("status"),
                "source_type": artifact.get("execution_request_source_type"),
                "created_at": artifact.get("created_at"),
                "artifact_path": item["artifact_path"],
            }
        )
    return sorted(entries, key=lambda entry: (entry.get("created_at") or "", entry.get("execution_request_id") or ""), reverse=True)[:limit]


def _recent_learning_artifacts(artifacts: list[dict[str, Any]], *, limit: int) -> list[dict[str, Any]]:
    entries = []
    for item in artifacts:
        artifact = item["artifact"]
        if artifact.get("artifact_type") not in LEARNING_ARTIFACT_TYPES:
            continue
        entries.append(
            {
                "artifact_type": artifact.get("artifact_type"),
                "artifact_id": _artifact_id(artifact),
                "canonical_chain_id": artifact.get("canonical_chain_id"),
                "created_at": item["created_at"],
                "artifact_path": item["artifact_path"],
            }
        )
    return sorted(entries, key=lambda entry: (entry.get("created_at") or "", entry.get("artifact_id") or ""), reverse=True)[:limit]


def _safe_next_actions(
    *,
    latest_chains: list[dict[str, Any]],
    pending_approval_count: int,
    pending_bridge_count: int,
) -> list[str]:
    actions: list[str] = []
    if pending_approval_count:
        actions.append("approval pending")
    if pending_bridge_count:
        actions.append("bridge pending")
    if latest_chains:
        chain_id = latest_chains[0]["canonical_chain_id"]
        actions.extend(
            [
                f"show-chain {chain_id}",
                f"show-full-lineage {chain_id}",
                f"show-learning-lifecycle {chain_id}",
                f"show-execution-lifecycle {chain_id}",
            ]
        )
    if not actions:
        actions.append("conversation")
    return actions


def _is_dashboard_relevant(artifact: dict[str, Any]) -> bool:
    artifact_type = artifact.get("artifact_type") or artifact.get("event_type")
    if artifact_type in EXECUTION_ARTIFACT_TYPES or artifact_type in LEARNING_ARTIFACT_TYPES:
        return True
    return any(isinstance(artifact.get(field), str) and artifact.get(field).strip() for field in CHAIN_ID_FIELDS)


def _raise_if_section_failed(section: dict[str, Any], label: str) -> None:
    if section.get("fail_closed") is True:
        raise FailClosedRuntimeError(section.get("failure_reason") or f"dashboard failed closed: {label} failed")


def _artifact_id(artifact: dict[str, Any]) -> str | None:
    for field in (
        "evaluation_id",
        "improvement_proposal_id",
        "improvement_review_id",
        "improvement_approval_id",
        "implementation_plan_id",
        "result_id",
    ):
        value = artifact.get(field)
        if isinstance(value, str) and value.strip():
            return value
    return None


def _artifact_time(artifact: dict[str, Any]) -> str:
    for field in TIME_FIELDS:
        value = artifact.get(field)
        if isinstance(value, str) and value.strip():
            return value
    return ""


def _load_json_object(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise FailClosedRuntimeError(f"dashboard failed closed: invalid JSON artifact {path.name}") from exc
    return value if isinstance(value, dict) else None


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash", None)
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("dashboard failed closed: replay hash mismatch")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash", None)
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _failure_reason(exc: Exception) -> str:
    return str(exc) or exc.__class__.__name__


__all__ = [
    "SESSION_DASHBOARD_RUNTIME_VERSION",
    "dashboard_approvals_command",
    "dashboard_bridges_command",
    "dashboard_chains_command",
    "dashboard_command",
    "dashboard_execution_command",
    "dashboard_learning_command",
    "dashboard_summary_command",
    "render_dashboard_summary",
]
