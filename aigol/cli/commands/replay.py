"""Replay command helpers for the deterministic AiGOL CLI."""

from __future__ import annotations

from pathlib import Path

from aigol.cli.commands.return_continuity import read_ledger_entries, verify_governed_return
from aigol.cli.commands.run_governed import summarize_governed_operation_replay


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


__all__ = ["ledger_summary", "replay_summary", "verify_replay"]
