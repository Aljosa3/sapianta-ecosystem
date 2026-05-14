"""Classify and stabilize Codex process termination."""

from __future__ import annotations

from typing import Any

from .codex_completion_marker import detect_completion_marker
from .codex_output_quiescence import classify_output_quiescence
from .codex_process_state import validate_codex_process_state


AUTH_MARKERS = ("login required", "authentication", "unauthorized", "not logged in")
INTERACTIVE_MARKERS = ("reading additional input from stdin", "press enter", "select")
STREAMING_MARKERS = ("streaming", "stream did not finish")


def _contains_any(text: str, markers: tuple[str, ...]) -> bool:
    lower = text.lower()
    return any(marker in lower for marker in markers)


def classify_codex_process_termination(
    *,
    stdout: str,
    stderr: str,
    exit_code: int,
    timed_out: bool,
    process_terminated: bool,
    idle_window_seconds: int = 0,
) -> dict[str, Any]:
    combined = f"{stdout}\n{stderr}"
    marker = detect_completion_marker(stdout=stdout, stderr=stderr)
    quiescence = classify_output_quiescence(
        stdout=stdout,
        stderr=stderr,
        marker_detected=marker["marker_detected"],
        process_running=not process_terminated,
        idle_window_seconds=idle_window_seconds,
    )
    gracefully_terminated = False
    if process_terminated and exit_code == 0:
        state = "TERMINATED_COMPLETED"
    elif process_terminated and exit_code != 0:
        if _contains_any(combined, AUTH_MARKERS):
            state = "AUTH_WAIT"
        elif _contains_any(combined, INTERACTIVE_MARKERS):
            state = "INTERACTIVE_WAIT"
        else:
            state = "TERMINATED_CLI_ERROR"
    elif timed_out and marker["marker_detected"] and quiescence["output_quiescent"]:
        state = "OUTPUT_COMPLETED_PROCESS_RUNNING"
        gracefully_terminated = True
    elif timed_out and _contains_any(combined, AUTH_MARKERS):
        state = "AUTH_WAIT"
    elif timed_out and _contains_any(combined, INTERACTIVE_MARKERS):
        state = "INTERACTIVE_WAIT"
    elif timed_out and _contains_any(combined, STREAMING_MARKERS):
        state = "STREAMING_WAIT"
    elif timed_out and (stdout or stderr):
        state = "TIMEOUT_NO_COMPLETION"
    elif timed_out:
        state = "TIMEOUT_NO_COMPLETION"
    elif stdout or stderr:
        state = "OUTPUT_ACTIVE_PROCESS_RUNNING"
    else:
        state = "UNKNOWN"
    state_validation = validate_codex_process_state(state)
    return {
        "process_state": state,
        "bounded_result_available": state_validation["bounded_result_available"],
        "process_terminated": process_terminated,
        "timed_out": timed_out,
        "exit_code": exit_code,
        "completion_marker_detected": marker["marker_detected"],
        "output_quiescent": quiescence["output_quiescent"],
        "graceful_termination_performed": gracefully_terminated,
        "termination_required": state == "OUTPUT_COMPLETED_PROCESS_RUNNING",
        "suspected_blocker": state.lower(),
        "fail_closed": state_validation["fail_closed"],
        "completion_marker": marker,
        "output_quiescence": quiescence,
        "retry_present": False,
        "fallback_present": False,
        "command_mutation_present": False,
    }


def validate_codex_process_termination(classification: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(classification, dict):
        return {"valid": False, "errors": [{"field": "process_termination", "reason": "must be an object"}]}
    for field in (
        "process_state",
        "bounded_result_available",
        "process_terminated",
        "timed_out",
        "exit_code",
        "completion_marker_detected",
        "output_quiescent",
        "graceful_termination_performed",
        "termination_required",
    ):
        if field not in classification:
            errors.append({"field": field, "reason": "missing process termination field"})
    state_validation = validate_codex_process_state(classification.get("process_state"))
    if classification.get("process_state") != "UNKNOWN":
        errors.extend(state_validation["errors"])
    if classification.get("process_state") == "TERMINATED_COMPLETED":
        if classification.get("exit_code") != 0 or classification.get("process_terminated") is not True:
            errors.append({"field": "process_state", "reason": "terminated completed requires exit_code 0 and termination"})
    for field in ("retry_present", "fallback_present", "command_mutation_present"):
        if classification.get(field) is not False:
            errors.append({"field": field, "reason": "process termination classifier cannot alter execution behavior"})
    return {"valid": not errors, "errors": errors}
