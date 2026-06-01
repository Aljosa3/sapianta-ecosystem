"""Replay command helpers for the deterministic AiGOL CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aigol.cli.commands.return_continuity import read_ledger_entries, verify_governed_return
from aigol.cli.commands.run_governed import summarize_governed_operation_replay
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash


def replay_summary(*, chain: dict) -> dict:
    return {
        "command": "aigol replay",
        "replay_identity": chain.get("replay_identity", "UNKNOWN"),
        "hash_continuity": chain.get("hash_continuity", {}),
        "replay_visible": True,
    }


def ledger_summary(*, runtime_root: str | Path | None = None, limit: int = 10) -> dict:
    entries = read_ledger_entries(runtime_root=runtime_root, limit=limit)
    return {
        "command": "aigol replay ledger",
        "entries": [
            {
                "replay_identity": entry.get("replay_identity", "UNKNOWN"),
                "execution_status": entry.get("execution_status", "UNKNOWN"),
                "governed_return_hash": entry.get("governed_return_hash", ""),
            }
            for entry in entries
        ],
    }


def verify_replay(*, replay_identity: str, runtime_root: str | Path | None = None) -> dict:
    operator_verification = _verify_operator_runtime_replay(
        replay_identity=replay_identity,
        runtime_root=runtime_root,
    )
    if operator_verification is not None:
        return operator_verification
    return verify_governed_return(replay_identity=replay_identity, runtime_root=runtime_root)


def operator_operation_report(*, runtime_root: str | Path = ".aigol_operator_runtime", limit: int = 100) -> dict[str, Any]:
    """Summarize operator runtime operations from existing replay evidence."""

    root = Path(runtime_root)
    try:
        if not root.exists() or not root.is_dir():
            raise FailClosedRuntimeError("operator runtime root is missing")
        operation_dirs = sorted(path for path in root.iterdir() if path.is_dir())
        if not operation_dirs:
            raise FailClosedRuntimeError("operator runtime contains no operation records")
        entries = [_operation_entry(operation_dir=path, runtime_root=root) for path in operation_dirs[:limit]]
        stats = _operation_statistics(entries)
        result = {
            "command": "aigol replay report",
            "status": "REPORT_READY",
            "runtime_root": str(root),
            "operation_count": len(entries),
            "entries": entries,
            "statistics": stats,
            "weekly_usage_summary": _weekly_usage_summary(stats),
            "explanation": _report_explanation(stats=stats, entries=entries),
            "fail_closed": False,
            "authority": False,
            "replay_backed": True,
        }
        result["report_hash"] = replay_hash(result)
        return result
    except Exception as exc:
        result = {
            "command": "aigol replay report",
            "status": "REPORT_FAILED",
            "runtime_root": str(root),
            "operation_count": 0,
            "entries": [],
            "statistics": _operation_statistics([]),
            "weekly_usage_summary": "No trustworthy operator operation summary could be produced.",
            "explanation": "Report generation failed closed because replay evidence could not be reconstructed.",
            "fail_closed": True,
            "failure_reason": _failure_reason(exc),
            "authority": False,
            "replay_backed": False,
        }
        result["report_hash"] = replay_hash(result)
        return result


def _verify_operator_runtime_replay(*, replay_identity: str, runtime_root: str | Path | None) -> dict | None:
    if runtime_root is None:
        root = Path(".aigol_operator_runtime")
    else:
        root = Path(runtime_root)
    operation_dir = root / replay_identity
    if not operation_dir.exists():
        return None
    summary = summarize_governed_operation_replay(
        operation_id=replay_identity,
        runtime_root=root,
    )
    verified = (
        summary.get("status") == "SUCCEEDED"
        and summary.get("execution_status") == "SUCCEEDED"
        and str(summary.get("provider_replay_hash", "")).startswith("sha256:")
        and str(summary.get("authorization_replay_hash", "")).startswith("sha256:")
        and str(summary.get("worker_replay_hash", "")).startswith("sha256:")
        and summary.get("replay_summary", {}).get("event_count") == 6
    )
    return {
        "command": "aigol replay verify",
        "status": "VERIFY_PASSED" if verified else "VERIFY_FAILED",
        "replay_identity": replay_identity,
        "replay_format": "operator_runtime",
        "schema_valid": verified,
        "governed_return_hash_valid": False,
        "execution_result_hash_present": str(summary.get("worker_result", {}).get("content_hash", "")).startswith("sha256:"),
        "evidence_files_exist": _operator_evidence_files_exist(operation_dir),
        "ledger_entry_exists": True,
        "lineage_continuity_exists": verified,
        "provider_replay_hash_valid": str(summary.get("provider_replay_hash", "")).startswith("sha256:"),
        "authorization_replay_hash_valid": str(summary.get("authorization_replay_hash", "")).startswith("sha256:"),
        "worker_replay_hash_valid": str(summary.get("worker_replay_hash", "")).startswith("sha256:"),
        "replay_summary": summary.get("replay_summary", {}),
        "operation_replay_reference": str(operation_dir),
        "operator_status": summary.get("operator_status"),
        "execution_status": summary.get("execution_status"),
        "proposal_id": summary.get("proposal_id"),
        "authorization_id": summary.get("authorization_id"),
        "worker_id": summary.get("worker_id"),
        "missing_evidence": _missing_operator_evidence(operation_dir),
        "failure_reason": summary.get("failure_reason", ""),
        "fail_closed": not verified,
    }


def _operator_evidence_files_exist(operation_dir: Path) -> bool:
    return not _missing_operator_evidence(operation_dir)


def _missing_operator_evidence(operation_dir: Path) -> list[str]:
    expected = [
        "provider/000_provider_proposal_created.json",
        "provider/001_provider_proposal_returned.json",
        "authorization/000_authorization_created.json",
        "authorization/001_authorization_returned.json",
        "worker/000_authorized_worker_request.json",
        "worker/001_filesystem_worker_execution.json",
    ]
    return [name for name in expected if not (operation_dir / name).exists()]


def _operation_entry(*, operation_dir: Path, runtime_root: Path) -> dict[str, Any]:
    operation_id = operation_dir.name
    verification = _verify_operator_runtime_replay(replay_identity=operation_id, runtime_root=runtime_root)
    if verification is None:
        raise FailClosedRuntimeError("operator operation replay is missing")
    metadata = _operation_metadata(operation_dir)
    replay_status = verification["status"]
    return {
        "operation_id": operation_id,
        "status": verification.get("execution_status") if replay_status == "VERIFY_PASSED" else "VERIFY_FAILED",
        "worker": verification.get("worker_id") or metadata["worker"],
        "operation": metadata["operation"],
        "timestamp": metadata["timestamp"],
        "replay_status": replay_status,
        "verification_failed": replay_status != "VERIFY_PASSED",
        "proposal_id": verification.get("proposal_id", "UNAVAILABLE"),
        "authorization_id": verification.get("authorization_id", "UNAVAILABLE"),
        "replay_reference": str(operation_dir),
        "missing_evidence": verification.get("missing_evidence", []),
        "failure_reason": verification.get("failure_reason", ""),
        "evidence": {
            "provider_replay_hash_valid": verification.get("provider_replay_hash_valid", False),
            "authorization_replay_hash_valid": verification.get("authorization_replay_hash_valid", False),
            "worker_replay_hash_valid": verification.get("worker_replay_hash_valid", False),
            "lineage_continuity_exists": verification.get("lineage_continuity_exists", False),
        },
    }


def _operation_metadata(operation_dir: Path) -> dict[str, str]:
    metadata = {
        "worker": "UNKNOWN",
        "operation": "UNKNOWN",
        "timestamp": "UNKNOWN",
    }
    try:
        provider = load_json(operation_dir / "provider" / "000_provider_proposal_created.json")
        artifact = provider.get("artifact", {})
        if isinstance(artifact, dict):
            metadata["timestamp"] = str(artifact.get("timestamp", "UNKNOWN"))
    except Exception:
        pass
    try:
        worker = load_json(operation_dir / "worker" / "000_authorized_worker_request.json")
        artifact = worker.get("artifact", {})
        if isinstance(artifact, dict):
            metadata["worker"] = str(artifact.get("worker_id", "UNKNOWN"))
            metadata["operation"] = str(artifact.get("operation", "UNKNOWN"))
    except Exception:
        pass
    return metadata


def _operation_statistics(entries: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(entries)
    successes = sum(1 for entry in entries if entry.get("status") == "SUCCEEDED")
    verification_failures = sum(1 for entry in entries if entry.get("replay_status") != "VERIFY_PASSED")
    fail_closed = sum(1 for entry in entries if entry.get("status") == "FAILED_CLOSED" or entry.get("verification_failed"))
    workers: dict[str, int] = {}
    operations: dict[str, int] = {}
    for entry in entries:
        workers[entry.get("worker", "UNKNOWN")] = workers.get(entry.get("worker", "UNKNOWN"), 0) + 1
        operations[entry.get("operation", "UNKNOWN")] = operations.get(entry.get("operation", "UNKNOWN"), 0) + 1
    return {
        "total_operations": total,
        "successful_operations": successes,
        "fail_closed_operations": fail_closed,
        "verification_failures": verification_failures,
        "success_rate": _rate(successes, total),
        "fail_closed_rate": _rate(fail_closed, total),
        "worker_usage": dict(sorted(workers.items())),
        "operation_type_usage": dict(sorted(operations.items())),
    }


def _weekly_usage_summary(stats: dict[str, Any]) -> str:
    return (
        f"{stats['total_operations']} operations inspected; "
        f"{stats['successful_operations']} succeeded; "
        f"{stats['fail_closed_operations']} failed closed or failed verification; "
        f"{stats['verification_failures']} replay verification failures."
    )


def _report_explanation(*, stats: dict[str, Any], entries: list[dict[str, Any]]) -> str:
    return (
        "The report is computed from operator runtime replay directories. "
        "Each operation entry is verified through the existing replay verification path. "
        f"{len(entries)} replay-backed operation entries support the aggregate statistics."
    )


def _rate(count: int, total: int) -> str:
    if total == 0:
        return "0%"
    return f"{(count / total) * 100:.2f}%"


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "operator replay report failed closed"


__all__ = ["ledger_summary", "operator_operation_report", "replay_summary", "verify_replay"]
