"""Single-task bounded bridge listener for governed Codex transport."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

from sapianta_bridge.protocol.enforcement import enforce_artifact_path
from sapianta_bridge.protocol.hashing import compute_hash
from sapianta_bridge.protocol.quarantine import quarantine_artifact
from sapianta_bridge.protocol.validator import validate_artifact

from .codex_runner import CodexExecutionResult, CodexRunner
from .replay_log import append_replay_log, replay_entry
from .task_lock import TaskLock
from .task_queue import load_task, move_to_failed, move_to_processing, queued_tasks
from .transport_config import TransportConfig


class RunnerProtocol(Protocol):
    def run(self, task: dict[str, Any]) -> CodexExecutionResult:
        ...


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _result_artifact(task: dict[str, Any], execution: CodexExecutionResult) -> dict[str, Any]:
    status = "PASS" if execution.exit_code == 0 and not execution.failed_closed else "FAIL"
    errors = []
    warnings = []
    if status != "PASS":
        errors.append(
            {
                "field": "codex_execution",
                "reason": execution.error or execution.stderr or "codex execution failed",
            }
        )
    if execution.stderr and status == "PASS":
        warnings.append({"field": "stderr", "reason": execution.stderr[-500:]})

    result = {
        "protocol_version": "0.1",
        "task_id": task["task_id"],
        "result_id": f"RESULT-{task['task_id']}",
        "status": status,
        "execution_summary": "Bounded Codex execution completed."
        if status == "PASS"
        else "Bounded Codex execution failed closed.",
        "files_created": [],
        "files_modified": [],
        "files_deleted": [],
        "tests": {
            "pytest": {"executed": False, "passed": None},
            "py_compile": {"executed": False, "passed": None},
            "git_diff_check": {"executed": False, "passed": None},
        },
        "errors": errors,
        "warnings": warnings,
        "diff_summary": "",
        "execution_details": {
            "exit_code": execution.exit_code,
            "stdout_tail": execution.stdout[-2000:],
            "stderr_tail": execution.stderr[-2000:],
            "timed_out": execution.timed_out,
            "failed_closed": execution.failed_closed,
        },
        "artifact_hashes": {
            "result_sha256": "0" * 64,
            "task_sha256": compute_hash(task),
        },
        "lineage": {
            "source_task_id": task["task_id"],
            "parent_result_id": None,
        },
    }
    result["artifact_hashes"]["result_sha256"] = compute_hash(
        result,
        omit_hash_fields={"result_sha256"},
    )
    return result


def _finalize_success(
    processing_task_path: Path,
    result_path: Path,
    config: TransportConfig,
) -> tuple[Path, Path]:
    task_destination = config.completed_dir / processing_task_path.name
    result_destination = config.completed_dir / result_path.name
    shutil.move(str(processing_task_path), str(task_destination))
    shutil.move(str(result_path), str(result_destination))
    return task_destination, result_destination


def _finalize_failure(
    processing_task_path: Path,
    result_path: Path | None,
    config: TransportConfig,
) -> tuple[Path, Path | None]:
    task_destination = move_to_failed(processing_task_path, config)
    result_destination = None
    if result_path is not None and result_path.exists():
        result_destination = config.failed_dir / result_path.name
        shutil.move(str(result_path), str(result_destination))
    return task_destination, result_destination


def process_one_task(
    config: TransportConfig | None = None,
    *,
    runner: RunnerProtocol | None = None,
) -> dict[str, Any]:
    active_config = config or TransportConfig()
    active_config.ensure_directories()
    selected = None
    selected_enforcement = None
    for candidate in queued_tasks(active_config):
        enforcement = enforce_artifact_path(
            candidate,
            current_state="CREATED",
            next_state="VALIDATED",
        )
        if enforcement.allowed_to_continue:
            selected = candidate
            selected_enforcement = enforcement
            break
        quarantine_artifact(
            candidate,
            reason="task failed protocol enforcement",
            validation_errors=enforcement.reasons,
            quarantine_root=active_config.quarantine_root,
        )
        move_to_failed(candidate, active_config)

    if selected is None:
        return {"processed": False, "final_state": "NO_TASK"}

    lock = TaskLock(active_config.lock_path, owner=selected.name)
    if not lock.acquire():
        return {
            "processed": False,
            "final_state": "BLOCKED",
            "reason": "task lock unavailable",
        }

    processing_task_path: Path | None = None
    result_path: Path | None = None
    try:
        processing_task_path = move_to_processing(selected, active_config)
        task = load_task(processing_task_path)
        execution_runner = runner or CodexRunner(active_config)
        started_at = datetime.now(timezone.utc).isoformat()
        execution = execution_runner.run(task)
        result = _result_artifact(task, execution)
        result_path = active_config.processing_dir / "result.json"
        _write_json(result_path, result)

        result_validation = validate_artifact(result, "result.json")
        if not result_validation.valid:
            quarantine_artifact(
                result_path,
                reason="generated result failed protocol validation",
                validation_errors=result_validation.errors,
                quarantine_root=active_config.quarantine_root,
            )
            final_state = "FAILED"
        elif result["status"] == "PASS":
            final_state = "COMPLETED"
        else:
            final_state = "FAILED"

        entry = replay_entry(
            task_id=task["task_id"],
            execution_timestamp=started_at,
            codex_exit_code=execution.exit_code,
            task_hash=result["artifact_hashes"]["task_sha256"],
            result_hash=result["artifact_hashes"]["result_sha256"],
            processing_duration_seconds=execution.duration_seconds,
            final_state=final_state,
        )
        append_replay_log(active_config.replay_log_path, entry)
        if final_state == "COMPLETED":
            task_destination, result_destination = _finalize_success(
                processing_task_path,
                result_path,
                active_config,
            )
        else:
            task_destination, result_destination = _finalize_failure(
                processing_task_path,
                result_path,
                active_config,
            )
        return {
            "processed": True,
            "task_path": str(task_destination),
            "result_path": str(result_destination) if result_destination else None,
            "final_state": final_state,
            "enforcement": selected_enforcement.to_dict() if selected_enforcement else None,
        }
    except Exception as exc:
        if processing_task_path is not None and processing_task_path.exists():
            _finalize_failure(processing_task_path, result_path, active_config)
        return {
            "processed": True,
            "final_state": "FAILED",
            "reason": f"bridge listener failed closed: {exc.__class__.__name__}",
        }
    finally:
        lock.release()
