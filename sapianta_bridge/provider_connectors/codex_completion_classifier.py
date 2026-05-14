"""Classify Codex exec completion from captured process facts only."""

from __future__ import annotations

from typing import Any

from .codex_completion_state import validate_codex_completion_state


AUTH_MARKERS = (
    "not logged in",
    "authentication",
    "login required",
    "unauthorized",
    "missing api key",
)
INTERACTIVE_MARKERS = (
    "reading additional input from stdin",
    "press enter",
    "select",
    "prompt",
)
APP_SERVER_MARKERS = (
    "app-server",
    "in-process app-server",
    "state db",
    "state runtime",
)
STREAMING_MARKERS = (
    "streaming",
    "stream did not finish",
)


def _contains_any(text: str, markers: tuple[str, ...]) -> bool:
    lower = text.lower()
    return any(marker in lower for marker in markers)


def classify_codex_completion(
    *,
    stdout: str,
    stderr: str,
    exit_code: int,
    timed_out: bool,
    duration_seconds: int,
) -> dict[str, Any]:
    combined = f"{stdout}\n{stderr}"
    suspected_blocker = ""
    if timed_out:
        if _contains_any(combined, APP_SERVER_MARKERS):
            state = "APP_SERVER_WAIT"
            suspected_blocker = "app_server_state_initialization"
        elif _contains_any(combined, AUTH_MARKERS):
            state = "AUTH_WAIT"
            suspected_blocker = "authentication_wait"
        elif _contains_any(combined, INTERACTIVE_MARKERS):
            state = "INTERACTIVE_WAIT"
            suspected_blocker = "interactive_input_wait"
        elif _contains_any(combined, STREAMING_MARKERS):
            state = "STREAMING_WAIT"
            suspected_blocker = "streaming_wait"
        elif stdout or stderr:
            state = "TIMEOUT"
            suspected_blocker = "timeout_with_output"
        else:
            state = "HANGING_PROCESS"
            suspected_blocker = "timeout_without_output"
    elif exit_code == 0:
        state = "COMPLETED"
        suspected_blocker = ""
    elif _contains_any(combined, AUTH_MARKERS):
        state = "AUTH_WAIT"
        suspected_blocker = "authentication_error"
    elif _contains_any(combined, APP_SERVER_MARKERS):
        state = "APP_SERVER_WAIT"
        suspected_blocker = "app_server_error"
    elif _contains_any(combined, INTERACTIVE_MARKERS):
        state = "INTERACTIVE_WAIT"
        suspected_blocker = "interactive_input_error"
    elif _contains_any(combined, STREAMING_MARKERS):
        state = "STREAMING_WAIT"
        suspected_blocker = "streaming_error"
    elif exit_code != 0:
        state = "CLI_ERROR"
        suspected_blocker = "nonzero_exit"
    else:
        state = "UNKNOWN"
        suspected_blocker = "unclassified"
    validation = validate_codex_completion_state(state)
    return {
        "completion_state": state,
        "completion_success": validation["completion_success"],
        "fail_closed": not validation["completion_success"],
        "process_terminated": not timed_out,
        "exit_code": exit_code,
        "timed_out": timed_out,
        "duration_seconds": duration_seconds,
        "stdout_sample": stdout[:240],
        "stderr_sample": stderr[:240],
        "suspected_blocker": suspected_blocker,
        "classification_valid": validation["valid"],
        "classifier_inputs": ("stdout", "stderr", "exit_code", "timed_out", "duration_seconds"),
        "retry_present": False,
        "fallback_present": False,
        "command_mutation_present": False,
    }


def validate_codex_completion_classification(classification: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(classification, dict):
        return {"valid": False, "errors": [{"field": "classification", "reason": "must be an object"}]}
    for field in (
        "completion_state",
        "completion_success",
        "fail_closed",
        "process_terminated",
        "exit_code",
        "timed_out",
        "duration_seconds",
        "stdout_sample",
        "stderr_sample",
        "suspected_blocker",
    ):
        if field not in classification:
            errors.append({"field": field, "reason": "missing classification field"})
    state_validation = validate_codex_completion_state(classification.get("completion_state"))
    if classification.get("completion_state") != "UNKNOWN":
        errors.extend(state_validation["errors"])
    if classification.get("completion_state") == "COMPLETED" and classification.get("exit_code") != 0:
        errors.append({"field": "exit_code", "reason": "completed state requires exit code 0"})
    if classification.get("completion_state") != "COMPLETED" and classification.get("completion_success") is not False:
        errors.append({"field": "completion_success", "reason": "non-completed state cannot be success"})
    for field in ("retry_present", "fallback_present", "command_mutation_present"):
        if classification.get(field) is not False:
            errors.append({"field": field, "reason": "completion classifier cannot alter execution behavior"})
    return {"valid": not errors, "errors": errors}
