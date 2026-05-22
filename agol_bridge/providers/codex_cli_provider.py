"""Bounded Codex CLI provider invocation.

This module is the first real Codex CLI provider boundary for AGOL Bridge. It
invokes only the fixed ``codex exec <bounded_prompt>`` contract and returns a
captured result package. It does not approve, retry, route, orchestrate, or
continue work.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json
import subprocess
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

CODEX_CLI_PROVIDER = "CODEX_CLI"
CODEX_EXECUTABLE = "codex"
CODEX_EXEC_CONTRACT = "codex exec <bounded_prompt>"

STATUS_COMPLETED = "COMPLETED"
STATUS_FAILED = "FAILED"
STATUS_TIMEOUT = "TIMEOUT"
STATUS_REJECTED = "REJECTED"

NON_AUTHORITY_GUARANTEES = (
    "AIGOL_TASK_PACKAGE_REQUIRED",
    "NO_AUTO_APPROVAL",
    "NO_AUTO_CONTINUATION",
    "NO_SILENT_RETRY",
    "NO_ORCHESTRATION",
    "NO_PROVIDER_ROUTING",
    "CODEX_CLI_ONLY",
)

EXECUTION_BOUNDARY = {
    "provider": CODEX_CLI_PROVIDER,
    "contract": CODEX_EXEC_CONTRACT,
    "auto_approval": False,
    "auto_continue": False,
    "silent_retry": False,
    "orchestration": False,
    "cloud_required": False,
}


def _canonical_copy(value: Any) -> Any:
    return deepcopy(value)


def _reject(*, reason: str, task_package_id: str = "UNKNOWN", workspace_path: str = "") -> dict:
    return {
        "provider": CODEX_CLI_PROVIDER,
        "status": STATUS_REJECTED,
        "stdout": "",
        "stderr": "",
        "returncode": None,
        "workspace_path": workspace_path,
        "task_package_id": task_package_id,
        "non_authority_guarantees": list(NON_AUTHORITY_GUARANTEES),
        "execution_boundary": _canonical_copy(EXECUTION_BOUNDARY),
        "errors": [reason],
        "command": [],
        "bounded_prompt_hash": "",
        "retry_count": 0,
    }


def _allowed_roots_from_task(task_package: dict) -> list[Path]:
    metadata = task_package.get("metadata", {})
    roots = metadata.get("allowed_workspace_roots", metadata.get("allowed_workspace_root", []))
    if isinstance(roots, str):
        roots = [roots]
    if not isinstance(roots, list):
        roots = []
    return [Path(root).expanduser().resolve() for root in roots if isinstance(root, str) and root.strip()]


def _workspace_allowed(*, workspace: Path, task_package: dict) -> bool:
    allowed_roots = _allowed_roots_from_task(task_package)
    if not allowed_roots:
        allowed_roots = [Path.cwd().resolve()]
    return any(workspace == root or root in workspace.parents for root in allowed_roots)


def _task_package_id(task_package: dict) -> str:
    return str(task_package.get("task_id") or task_package.get("task_package_id") or "UNKNOWN")


def _validate_task_package(task_package: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(task_package, dict) or not task_package:
        return ["task_package must be a non-empty governed package"]
    if not isinstance(task_package.get("task_id"), str) or not task_package["task_id"].strip():
        errors.append("task_package.task_id is required")
    if not isinstance(task_package.get("codex_prompt"), str) or not task_package["codex_prompt"].strip():
        errors.append("task_package.codex_prompt is required")
    metadata = task_package.get("metadata", {})
    if not isinstance(metadata, dict):
        errors.append("task_package.metadata must be an object")
    elif metadata.get("approved") is True:
        errors.append("task_package must not carry auto-approval")
    return errors


def build_bounded_codex_prompt(*, task_package: dict) -> str:
    """Create the deterministic prompt passed to ``codex exec``."""

    task_copy = _canonical_copy(task_package)
    task_hash = canonical_hash(task_copy)
    canonical_task = json.dumps(task_copy, sort_keys=True, separators=(",", ":"))
    semantic_contract = task_copy.get("semantic_contract", {})
    canonical_contract = json.dumps(semantic_contract, sort_keys=True, separators=(",", ":")) if isinstance(semantic_contract, dict) else "{}"
    return (
        "AGOL Bridge bounded Codex CLI task.\n"
        "Execute only the governed semantic contract inside the task package below within the provided workspace.\n"
        "Do not approve, dispatch, retry, orchestrate, or continue autonomously.\n"
        "Use the semantic contract as structured intent, not as execution authority.\n"
        f"Semantic contract JSON: {canonical_contract}\n"
        "Return a concise result summary with files changed, commands run, tests, errors, and residual risk.\n"
        f"Task package sha256: {task_hash}\n"
        f"Task package JSON: {canonical_task}\n"
        "End with: AIGOL_CODEX_TASK_COMPLETE"
    )


def run_bounded_codex_cli_task(
    *,
    task_package: dict,
    workspace_path: str,
    timeout_seconds: int = 600,
) -> dict:
    """Invoke Codex CLI through a bounded, governed task package contract."""

    task_copy = _canonical_copy(task_package)
    task_id = _task_package_id(task_copy) if isinstance(task_copy, dict) else "UNKNOWN"
    workspace_text = str(workspace_path or "")
    validation_errors = _validate_task_package(task_copy)
    if validation_errors:
        return _reject(reason="; ".join(validation_errors), task_package_id=task_id, workspace_path=workspace_text)
    if not isinstance(timeout_seconds, int) or timeout_seconds < 1 or timeout_seconds > 3600:
        return _reject(reason="timeout_seconds must be an integer between 1 and 3600", task_package_id=task_id, workspace_path=workspace_text)
    if not workspace_text.strip():
        return _reject(reason="workspace_path is required", task_package_id=task_id, workspace_path=workspace_text)

    workspace = Path(workspace_text).expanduser().resolve()
    if not workspace.exists() or not workspace.is_dir():
        return _reject(reason="workspace_path must be an existing directory", task_package_id=task_id, workspace_path=str(workspace))
    if not _workspace_allowed(workspace=workspace, task_package=task_copy):
        return _reject(reason="workspace_path is outside allowed root", task_package_id=task_id, workspace_path=str(workspace))

    bounded_prompt = build_bounded_codex_prompt(task_package=task_copy)
    command = [CODEX_EXECUTABLE, "exec", bounded_prompt]
    try:
        completed = subprocess.run(
            command,
            cwd=str(workspace),
            input="",
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "provider": CODEX_CLI_PROVIDER,
            "status": STATUS_TIMEOUT,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "returncode": None,
            "workspace_path": str(workspace),
            "task_package_id": task_id,
            "non_authority_guarantees": list(NON_AUTHORITY_GUARANTEES),
            "execution_boundary": _canonical_copy(EXECUTION_BOUNDARY),
            "errors": [f"Codex CLI timed out after {timeout_seconds} seconds"],
            "command": [CODEX_EXECUTABLE, "exec", "<bounded_prompt>"],
            "bounded_prompt_hash": canonical_hash({"bounded_prompt": bounded_prompt}),
            "retry_count": 0,
        }
    except OSError as exc:
        return {
            "provider": CODEX_CLI_PROVIDER,
            "status": STATUS_FAILED,
            "stdout": "",
            "stderr": str(exc),
            "returncode": None,
            "workspace_path": str(workspace),
            "task_package_id": task_id,
            "non_authority_guarantees": list(NON_AUTHORITY_GUARANTEES),
            "execution_boundary": _canonical_copy(EXECUTION_BOUNDARY),
            "errors": ["Codex CLI invocation failed"],
            "command": [CODEX_EXECUTABLE, "exec", "<bounded_prompt>"],
            "bounded_prompt_hash": canonical_hash({"bounded_prompt": bounded_prompt}),
            "retry_count": 0,
        }

    status = STATUS_COMPLETED if completed.returncode == 0 else STATUS_FAILED
    return {
        "provider": CODEX_CLI_PROVIDER,
        "status": status,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "returncode": completed.returncode,
        "workspace_path": str(workspace),
        "task_package_id": task_id,
        "non_authority_guarantees": list(NON_AUTHORITY_GUARANTEES),
        "execution_boundary": _canonical_copy(EXECUTION_BOUNDARY),
        "errors": [] if status == STATUS_COMPLETED else ["Codex CLI returned non-zero exit status"],
        "command": [CODEX_EXECUTABLE, "exec", "<bounded_prompt>"],
        "bounded_prompt_hash": canonical_hash({"bounded_prompt": bounded_prompt}),
        "retry_count": 0,
    }
