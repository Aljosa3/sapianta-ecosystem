"""Persistent governed return continuity for the AiGOL CLI."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

ALLOWED_EXECUTION_STATUSES = ("EXECUTION_COMPLETED", "EXECUTION_FAILED", "EXECUTION_BLOCKED")
ARTIFACT_TYPE = "GOVERNED_RETURN_ARTIFACT_V1"
SCHEMA_VERSION = "1.0"
DEFAULT_RUNTIME_ROOT = Path(".runtime") / "aigol"
DEFAULT_LEDGER_PATH = DEFAULT_RUNTIME_ROOT / "ledger" / "governed_returns.jsonl"
DEFAULT_EVIDENCE_ROOT = DEFAULT_RUNTIME_ROOT / "evidence"


def _canonical_copy(value: Any) -> Any:
    return deepcopy(value)


def _sha_text(value: str) -> str:
    return canonical_hash(str(value or ""))


def _hash_input(artifact: dict) -> dict:
    safe = _canonical_copy(artifact)
    safe.pop("governed_return_hash", None)
    diagnostics = safe.get("diagnostic_evidence")
    if isinstance(diagnostics, dict):
        diagnostics.pop("governed_return_hash", None)
    lineage = safe.get("lineage")
    if isinstance(lineage, dict):
        lineage.pop("governed_return_hash", None)
    return safe


def _lineage(*, execution_artifact: dict, chain: dict | None) -> dict:
    hash_continuity = (chain or {}).get("hash_continuity", {}) if isinstance(chain, dict) else {}
    return {
        "ingress_artifact_hash": hash_continuity.get("ingress_artifact_hash", "UNKNOWN"),
        "proposal_candidate_hash": hash_continuity.get("proposal_candidate_hash", "UNKNOWN"),
        "contract_candidate_hash": hash_continuity.get("contract_candidate_hash", "UNKNOWN"),
        "acceptance_gate_hash": hash_continuity.get("acceptance_gate_hash", "UNKNOWN"),
        "task_package_preview_hash": hash_continuity.get("task_preview_hash", "UNKNOWN"),
        "human_approval_hash": hash_continuity.get("human_approval_hash", "UNKNOWN"),
        "handoff_preview_hash": hash_continuity.get("handoff_preview_hash", "UNKNOWN"),
        "dispatch_authorization_hash": hash_continuity.get("dispatch_authorization_hash", execution_artifact.get("source_dispatch_authorization_hash", "UNKNOWN")),
        "execution_governance_hash": execution_artifact.get("execution_governance_hash", "UNKNOWN"),
        "governed_return_hash": "PENDING",
    }


def generate_governed_return_artifact(
    *,
    execution_artifact: dict,
    cli_governed_return: dict,
    chain: dict | None = None,
    created_at: str = "1970-01-01T00:00:00Z",
) -> dict:
    execution_status = str(execution_artifact.get("execution_status", "EXECUTION_BLOCKED"))
    if execution_status not in ALLOWED_EXECUTION_STATUSES:
        return {
            "artifact_type": ARTIFACT_TYPE,
            "schema_version": SCHEMA_VERSION,
            "status": "PERSISTENCE_REJECTED",
            "rejection_reason": "invalid execution status",
            "execution_status": execution_status,
            "fail_closed": True,
        }
    replay_identity = str(execution_artifact.get("replay_identity", "")).strip()
    if not replay_identity or replay_identity == "UNKNOWN":
        return {
            "artifact_type": ARTIFACT_TYPE,
            "schema_version": SCHEMA_VERSION,
            "status": "PERSISTENCE_REJECTED",
            "rejection_reason": "missing replay identity",
            "execution_status": execution_status,
            "fail_closed": True,
        }
    governed_return_hash = str(cli_governed_return.get("governed_return_hash", "")).strip()
    if not governed_return_hash.startswith("sha256:"):
        return {
            "artifact_type": ARTIFACT_TYPE,
            "schema_version": SCHEMA_VERSION,
            "status": "PERSISTENCE_REJECTED",
            "rejection_reason": "missing governed return hash",
            "execution_status": execution_status,
            "replay_identity": replay_identity,
            "fail_closed": True,
        }

    provider_result = cli_governed_return.get("provider_result", {}) if isinstance(cli_governed_return.get("provider_result"), dict) else {}
    provider_stdout = str(provider_result.get("stdout", ""))
    provider_stderr = str(provider_result.get("stderr", ""))
    artifact = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "replay_identity": replay_identity,
        "lineage": _lineage(execution_artifact=execution_artifact, chain=chain),
        "execution_status": execution_status,
        "provider_invoked": execution_artifact.get("provider_invoked") is True,
        "provider_command": (cli_governed_return.get("diagnostic_evidence", {}) or {}).get("provider_command", provider_result.get("command", [])),
        "provider_exit_code": provider_result.get("returncode"),
        "provider_stdout_hash": _sha_text(provider_stdout),
        "provider_stderr_hash": _sha_text(provider_stderr),
        "execution_result_hash": execution_artifact.get("execution_result_hash", "UNKNOWN"),
        "execution_governance_hash": execution_artifact.get("execution_governance_hash", "UNKNOWN"),
        "governed_return_hash": governed_return_hash,
        "continuity_verified": cli_governed_return.get("continuity_verified") is True,
        "fail_closed": cli_governed_return.get("fail_closed") is True,
        "diagnostic_evidence": _canonical_copy(cli_governed_return.get("diagnostic_evidence", {})),
        "created_at": str(created_at),
    }
    artifact["lineage"]["governed_return_hash"] = artifact["governed_return_hash"]
    artifact["governed_return_hash"] = canonical_hash(_hash_input(artifact))
    artifact["lineage"]["governed_return_hash"] = artifact["governed_return_hash"]
    artifact["diagnostic_evidence"]["governed_return_hash"] = artifact["governed_return_hash"]
    return artifact


def _canonical_json(value: dict) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _runtime_paths(*, runtime_root: str | Path | None = None, replay_identity: str) -> dict[str, Path]:
    root = Path(runtime_root) if runtime_root is not None else DEFAULT_RUNTIME_ROOT
    return {
        "runtime_root": root,
        "ledger_path": root / "ledger" / "governed_returns.jsonl",
        "evidence_dir": root / "evidence" / replay_identity,
    }


def persist_governed_return_artifact(*, artifact: dict, provider_result: dict | None = None, runtime_root: str | Path | None = None) -> dict:
    if artifact.get("artifact_type") != ARTIFACT_TYPE or artifact.get("governed_return_hash", "").startswith("sha256:") is not True:
        return {"status": "PERSISTENCE_FAILED", "fail_closed": True, "errors": ["invalid governed return artifact"]}
    replay_identity = str(artifact.get("replay_identity", "")).strip()
    if not replay_identity or replay_identity == "UNKNOWN":
        return {"status": "PERSISTENCE_FAILED", "fail_closed": True, "errors": ["missing replay identity"]}

    provider = provider_result or {}
    paths = _runtime_paths(runtime_root=runtime_root, replay_identity=replay_identity)
    try:
        paths["ledger_path"].parent.mkdir(parents=True, exist_ok=True)
        paths["evidence_dir"].mkdir(parents=True, exist_ok=True)
        (paths["evidence_dir"] / "governed_return.json").write_text(_canonical_json(artifact) + "\n", encoding="utf-8")
        (paths["evidence_dir"] / "provider_stdout.txt").write_text(str(provider.get("stdout", "")), encoding="utf-8")
        (paths["evidence_dir"] / "provider_stderr.txt").write_text(str(provider.get("stderr", "")), encoding="utf-8")
        (paths["evidence_dir"] / "diagnostic_evidence.json").write_text(_canonical_json(artifact.get("diagnostic_evidence", {})) + "\n", encoding="utf-8")
        (paths["evidence_dir"] / "lineage.json").write_text(_canonical_json(artifact.get("lineage", {})) + "\n", encoding="utf-8")
        with paths["ledger_path"].open("a", encoding="utf-8") as ledger:
            ledger.write(_canonical_json(artifact) + "\n")
    except (OSError, TypeError, ValueError) as exc:
        return {
            "status": "PERSISTENCE_FAILED",
            "fail_closed": True,
            "errors": [str(exc)],
            "ledger_path": str(paths["ledger_path"]),
            "evidence_path": str(paths["evidence_dir"]),
        }
    return {
        "status": "PERSISTED",
        "fail_closed": False,
        "ledger_path": str(paths["ledger_path"]),
        "evidence_path": str(paths["evidence_dir"]),
        "governed_return_hash": artifact["governed_return_hash"],
        "replay_identity": replay_identity,
    }


def read_ledger_entries(*, runtime_root: str | Path | None = None, limit: int = 10) -> list[dict]:
    ledger_path = (Path(runtime_root) if runtime_root is not None else DEFAULT_RUNTIME_ROOT) / "ledger" / "governed_returns.jsonl"
    if not ledger_path.exists():
        return []
    entries = []
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            entries.append(json.loads(line))
    return entries[-limit:]


def inspect_governed_return(*, replay_identity: str, runtime_root: str | Path | None = None) -> dict:
    paths = _runtime_paths(runtime_root=runtime_root, replay_identity=replay_identity)
    artifact_path = paths["evidence_dir"] / "governed_return.json"
    if not artifact_path.exists():
        return {"command": "aigol return inspect", "status": "NOT_FOUND", "replay_identity": replay_identity, "fail_closed": True}
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    return {
        "command": "aigol return inspect",
        "status": "FOUND",
        "replay_identity": replay_identity,
        "execution_status": artifact.get("execution_status", "UNKNOWN"),
        "provider_invoked": artifact.get("provider_invoked") is True,
        "governed_return_hash": artifact.get("governed_return_hash", ""),
        "continuity_verified": artifact.get("continuity_verified") is True,
        "fail_closed": artifact.get("fail_closed") is True,
        "evidence_path": str(paths["evidence_dir"]),
    }


def verify_governed_return(*, replay_identity: str, runtime_root: str | Path | None = None) -> dict:
    paths = _runtime_paths(runtime_root=runtime_root, replay_identity=replay_identity)
    evidence_files = [
        "governed_return.json",
        "provider_stdout.txt",
        "provider_stderr.txt",
        "diagnostic_evidence.json",
        "lineage.json",
    ]
    missing = [name for name in evidence_files if not (paths["evidence_dir"] / name).exists()]
    entries = read_ledger_entries(runtime_root=runtime_root, limit=100000)
    ledger_matches = [entry for entry in entries if entry.get("replay_identity") == replay_identity]
    if missing or not ledger_matches:
        return {
            "command": "aigol replay verify",
            "status": "VERIFY_FAILED",
            "replay_identity": replay_identity,
            "missing_evidence": missing,
            "ledger_entry_exists": bool(ledger_matches),
            "fail_closed": True,
        }
    artifact = json.loads((paths["evidence_dir"] / "governed_return.json").read_text(encoding="utf-8"))
    expected_hash = canonical_hash(_hash_input(artifact))
    hash_valid = artifact.get("governed_return_hash") == expected_hash
    ledger_hash_valid = any(entry.get("governed_return_hash") == artifact.get("governed_return_hash") for entry in ledger_matches)
    lineage = json.loads((paths["evidence_dir"] / "lineage.json").read_text(encoding="utf-8"))
    lineage_valid = lineage.get("governed_return_hash") == artifact.get("governed_return_hash")
    verified = hash_valid and ledger_hash_valid and lineage_valid
    return {
        "command": "aigol replay verify",
        "status": "VERIFY_PASSED" if verified else "VERIFY_FAILED",
        "replay_identity": replay_identity,
        "governed_return_hash_valid": hash_valid,
        "execution_result_hash_present": str(artifact.get("execution_result_hash", "")).startswith("sha256:"),
        "evidence_files_exist": not missing,
        "ledger_entry_exists": bool(ledger_matches),
        "lineage_continuity_exists": lineage_valid,
        "fail_closed": not verified,
    }


__all__ = [
    "ALLOWED_EXECUTION_STATUSES",
    "ARTIFACT_TYPE",
    "DEFAULT_EVIDENCE_ROOT",
    "DEFAULT_LEDGER_PATH",
    "DEFAULT_RUNTIME_ROOT",
    "SCHEMA_VERSION",
    "generate_governed_return_artifact",
    "inspect_governed_return",
    "persist_governed_return_artifact",
    "read_ledger_entries",
    "verify_governed_return",
]
