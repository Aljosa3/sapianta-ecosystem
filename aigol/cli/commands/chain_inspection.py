"""Operator-facing chain inspection commands for AiGOL CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash
from aigol.runtime.unified_replay_reconstruction_runtime import (
    reconstruct_chain_by_id,
    reconstruct_execution_lifecycle,
    reconstruct_full_lineage,
    reconstruct_latest_chain,
    reconstruct_learning_lifecycle,
    reconstruct_unified_replay_reconstruction_report,
)


CLI_CHAIN_INSPECTION_RUNTIME_VERSION = "CLI_CHAIN_INSPECTION_RUNTIME_V1"


def show_latest_chain_command(
    *, replay_root: str | Path, report_root: str | Path, created_at: str
) -> dict[str, Any]:
    """Show the latest canonical chain using unified replay reconstruction."""

    return _inspect(
        command="aigol show-latest-chain",
        reconstruction_name="latest_chain",
        reconstruction_func=reconstruct_latest_chain,
        replay_root=replay_root,
        report_root=report_root,
        created_at=created_at,
    )


def show_chain_command(
    *, canonical_chain_id: str, replay_root: str | Path, report_root: str | Path, created_at: str
) -> dict[str, Any]:
    """Show one canonical chain using unified replay reconstruction."""

    return _inspect(
        command="aigol show-chain",
        reconstruction_name="chain",
        reconstruction_func=reconstruct_chain_by_id,
        canonical_chain_id=canonical_chain_id,
        replay_root=replay_root,
        report_root=report_root,
        created_at=created_at,
    )


def show_execution_lifecycle_command(
    *, canonical_chain_id: str, replay_root: str | Path, report_root: str | Path, created_at: str
) -> dict[str, Any]:
    """Show execution lifecycle evidence for one chain."""

    return _inspect(
        command="aigol show-execution-lifecycle",
        reconstruction_name="execution_lifecycle",
        reconstruction_func=reconstruct_execution_lifecycle,
        canonical_chain_id=canonical_chain_id,
        replay_root=replay_root,
        report_root=report_root,
        created_at=created_at,
    )


def show_learning_lifecycle_command(
    *, canonical_chain_id: str, replay_root: str | Path, report_root: str | Path, created_at: str
) -> dict[str, Any]:
    """Show governed learning lifecycle evidence for one chain."""

    return _inspect(
        command="aigol show-learning-lifecycle",
        reconstruction_name="learning_lifecycle",
        reconstruction_func=reconstruct_learning_lifecycle,
        canonical_chain_id=canonical_chain_id,
        replay_root=replay_root,
        report_root=report_root,
        created_at=created_at,
    )


def show_full_lineage_command(
    *, canonical_chain_id: str, replay_root: str | Path, report_root: str | Path, created_at: str
) -> dict[str, Any]:
    """Show full replay lineage for one chain."""

    return _inspect(
        command="aigol show-full-lineage",
        reconstruction_name="full_lineage",
        reconstruction_func=reconstruct_full_lineage,
        canonical_chain_id=canonical_chain_id,
        replay_root=replay_root,
        report_root=report_root,
        created_at=created_at,
    )


def show_chain_summary_command(
    *, canonical_chain_id: str, replay_root: str | Path, report_root: str | Path, created_at: str
) -> dict[str, Any]:
    """Show a compact human-readable chain summary."""

    result = _inspect(
        command="aigol show-chain-summary",
        reconstruction_name="chain_summary",
        reconstruction_func=reconstruct_full_lineage,
        canonical_chain_id=canonical_chain_id,
        replay_root=replay_root,
        report_root=report_root,
        created_at=created_at,
    )
    result["summary_only"] = True
    result["summary_hash"] = replay_hash(result["human_readable_summary"])
    return result


def render_chain_inspection_summary(result: dict[str, Any]) -> str:
    """Render a deterministic human-readable chain inspection summary."""

    lines = [
        f"status: {result.get('status')}",
        f"canonical_chain_id: {result.get('canonical_chain_id')}",
        f"scope: {result.get('reconstruction_scope')}",
        f"report_id: {result.get('report_id')}",
        f"replay_root: {result.get('replay_root')}",
        f"report_dir: {result.get('report_dir')}",
        f"source_replay_read_only: {result.get('source_replay_read_only')}",
        f"inspection_report_persisted: {result.get('inspection_report_persisted')}",
        f"operationally_read_only: {result.get('operationally_read_only')}",
        f"conversation: {result.get('conversation_present')}",
        f"source_routing: {result.get('source_routing_present')}",
        f"execution_lifecycle_artifacts: {result.get('execution_lifecycle_artifact_count')}",
        f"learning_lifecycle_artifacts: {result.get('learning_lifecycle_artifact_count')}",
        f"bridge_artifacts: {result.get('bridge_artifact_count')}",
        f"worker_evidence_artifacts: {result.get('worker_evidence_artifact_count')}",
        f"replay_evidence_artifacts: {result.get('replay_evidence_artifact_count')}",
        f"read_only: {result.get('read_only')}",
        f"execution_requests_created: {result.get('execution_requests_created')}",
        f"workers_dispatched: {result.get('workers_dispatched')}",
        f"workers_invoked: {result.get('workers_invoked')}",
        f"fail_closed: {result.get('fail_closed')}",
        f"failure_reason: {result.get('failure_reason') or ''}",
    ]
    return "\n".join(lines)


def _inspect(
    *,
    command: str,
    reconstruction_name: str,
    reconstruction_func: Callable[..., dict[str, Any]],
    replay_root: str | Path,
    report_root: str | Path,
    created_at: str,
    canonical_chain_id: str | None = None,
) -> dict[str, Any]:
    replay_path = Path(replay_root)
    report_dir = _report_dir(
        report_root=Path(report_root),
        command=command,
        canonical_chain_id=canonical_chain_id,
        created_at=created_at,
    )
    try:
        kwargs: dict[str, Any] = {
            "replay_root": replay_path,
            "report_dir": report_dir,
            "created_at": created_at,
        }
        if canonical_chain_id is not None:
            kwargs["canonical_chain_id"] = canonical_chain_id
        kwargs["persist_report"] = False
        report = reconstruction_func(**kwargs)
        return _operator_result(
            command=command,
            reconstruction_name=reconstruction_name,
            report=report,
            replay_root=replay_path,
            report_dir=report_dir,
            fail_closed=False,
            failure_reason=None,
        )
    except Exception as exc:
        report = _load_failed_report(report_dir)
        return _operator_result(
            command=command,
            reconstruction_name=reconstruction_name,
            report=report,
            replay_root=replay_path,
            report_dir=report_dir,
            fail_closed=True,
            failure_reason=_failure_reason(exc),
        )


def _operator_result(
    *,
    command: str,
    reconstruction_name: str,
    report: dict[str, Any],
    replay_root: Path,
    report_dir: Path,
    fail_closed: bool,
    failure_reason: str | None,
) -> dict[str, Any]:
    authority = report.get("authority_boundary", {}) if isinstance(report.get("authority_boundary"), dict) else {}
    result = {
        "command": command,
        "cli_chain_inspection_runtime_version": CLI_CHAIN_INSPECTION_RUNTIME_VERSION,
        "status": "FAILED_CLOSED" if fail_closed else "READY",
        "reconstruction_name": reconstruction_name,
        "canonical_chain_id": report.get("canonical_chain_id"),
        "reconstruction_scope": report.get("reconstruction_scope"),
        "reconstruction_status": report.get("reconstruction_status"),
        "report_id": report.get("report_id"),
        "report_hash": report.get("artifact_hash"),
        "replay_root": str(replay_root),
        "report_dir": str(report_dir),
        "source_replay_read_only": True,
        "inspection_report_persisted": report.get("report_persisted") is True,
        "operationally_read_only": report.get("operationally_read_only") is not False,
        "conversation_present": _present(report, "conversation"),
        "source_routing_present": _present(report, "source_routing"),
        "execution_lifecycle_artifact_count": _count(report, "execution_lifecycle"),
        "learning_lifecycle_artifact_count": _count(report, "learning_lifecycle"),
        "bridge_artifact_count": _count(report, "implementation_execution_bridge"),
        "worker_evidence_artifact_count": _count(report, "worker_evidence"),
        "replay_evidence_artifact_count": _replay_count(report),
        "read_only": True,
        "authority": False,
        "replay_mutated": False,
        "governance_mutated": False,
        "execution_state_modified": False,
        "learning_state_modified": False,
        "execution_requests_created": authority.get("execution_requests_created", False),
        "workers_dispatched": authority.get("workers_dispatched", False),
        "workers_invoked": authority.get("workers_invoked", False),
        "fail_closed": fail_closed,
        "failure_reason": failure_reason or report.get("failure_reason"),
        "replay_visible": True,
    }
    result["human_readable_summary"] = render_chain_inspection_summary(result)
    result["inspection_hash"] = replay_hash(result)
    return result


def _load_failed_report(report_dir: Path) -> dict[str, Any]:
    try:
        persisted = reconstruct_unified_replay_reconstruction_report(report_dir)
        return {
            "canonical_chain_id": persisted.get("canonical_chain_id"),
            "reconstruction_scope": persisted.get("reconstruction_scope"),
            "reconstruction_status": persisted.get("reconstruction_status"),
            "report_id": persisted.get("report_id"),
            "artifact_hash": None,
            "failure_reason": persisted.get("failure_reason"),
            "authority_boundary": {
                "execution_requests_created": False,
                "workers_dispatched": False,
                "workers_invoked": False,
            },
        }
    except Exception as exc:
        return {
            "canonical_chain_id": "UNAVAILABLE",
            "reconstruction_scope": "UNAVAILABLE",
            "reconstruction_status": "FAILED_CLOSED",
            "report_id": "UNAVAILABLE",
            "artifact_hash": None,
            "failure_reason": _failure_reason(exc),
            "authority_boundary": {
                "execution_requests_created": False,
                "workers_dispatched": False,
                "workers_invoked": False,
            },
        }


def _report_dir(*, report_root: Path, command: str, canonical_chain_id: str | None, created_at: str) -> Path:
    identity = canonical_chain_id if isinstance(canonical_chain_id, str) and canonical_chain_id.strip() else "LATEST"
    slug = command.replace("aigol ", "").replace("-", "_")
    suffix = replay_hash({"command": command, "canonical_chain_id": identity, "created_at": created_at})[7:19]
    return report_root / slug / identity / suffix


def _present(report: dict[str, Any], section: str) -> bool:
    value = report.get(section)
    return bool(isinstance(value, dict) and value.get("present") is True)


def _count(report: dict[str, Any], section: str) -> int:
    value = report.get(section)
    if not isinstance(value, dict):
        return 0
    count = value.get("artifact_count")
    return count if isinstance(count, int) else 0


def _replay_count(report: dict[str, Any]) -> int:
    value = report.get("replay_evidence")
    if not isinstance(value, dict):
        return 0
    count = value.get("artifact_count")
    return count if isinstance(count, int) else 0


def _failure_reason(exc: Exception) -> str:
    return str(exc) or exc.__class__.__name__


__all__ = [
    "CLI_CHAIN_INSPECTION_RUNTIME_VERSION",
    "render_chain_inspection_summary",
    "show_chain_command",
    "show_chain_summary_command",
    "show_execution_lifecycle_command",
    "show_full_lineage_command",
    "show_latest_chain_command",
    "show_learning_lifecycle_command",
]
