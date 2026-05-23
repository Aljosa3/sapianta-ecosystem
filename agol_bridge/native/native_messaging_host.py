#!/usr/bin/env python3
"""Chrome Native Messaging host for the minimal AiGOL bridge.

The host is intentionally one-shot: Chrome launches it, sends one explicit
operator-triggered message, receives one governed response, and the process
exits. It does not start a server, listener, autonomous continuation, or
orchestration loop.
"""

from __future__ import annotations

import json
import os
import struct
import sys
import traceback
from copy import deepcopy
from pathlib import Path
from typing import Any, BinaryIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agol_bridge.runtime.minimal_end_to_end_bridge import (
    BRIDGE_ACCEPTED,
    export_minimal_bridge_result_artifact,
    run_minimal_end_to_end_bridge,
)

NATIVE_HOST_NAME = "com.sapianta.aigol_bridge"
NATIVE_BRIDGE_ACCEPTED = "NATIVE_BRIDGE_ACCEPTED"
NATIVE_BRIDGE_REJECTED = "NATIVE_BRIDGE_REJECTED"
NATIVE_BRIDGE_ERROR = "NATIVE_BRIDGE_ERROR"
NATIVE_BRIDGE_ACTION = "RUN_MINIMAL_END_TO_END_BRIDGE"
NATIVE_STAGE_READ_MESSAGE = "NATIVE_STAGE_READ_MESSAGE"
NATIVE_STAGE_JSON_PARSED = "NATIVE_STAGE_JSON_PARSED"
NATIVE_STAGE_HANDLE_ENTERED = "NATIVE_STAGE_HANDLE_ENTERED"
NATIVE_STAGE_RUNTIME_BRIDGE_ENTERED = "NATIVE_STAGE_RUNTIME_BRIDGE_ENTERED"
NATIVE_STAGE_PROVIDER_ATTEMPT = "NATIVE_STAGE_PROVIDER_ATTEMPT"
NATIVE_STAGE_WRITE_RESPONSE = "NATIVE_STAGE_WRITE_RESPONSE"
NATIVE_STAGE_RESPONSE_FLUSHED = "NATIVE_STAGE_RESPONSE_FLUSHED"


def _native_stage_context() -> dict:
    return {
        "stage_reached": "",
        "last_successful_stage": "",
        "failure_stage": "",
        "exception_type": "",
        "exception_summary": "",
        "stdout_contamination_detected": False,
        "response_written": False,
        "response_flushed": False,
        "stages": [],
    }


def _trace_stage(stage: str) -> None:
    if os.environ.get("AIGOL_NATIVE_TRACE") == "1":
        sys.stderr.write(f"[{stage}]\n")
        sys.stderr.flush()


def _mark_stage(diagnostics: dict | None, stage: str) -> None:
    if diagnostics is None:
        return
    diagnostics["stage_reached"] = stage
    diagnostics["last_successful_stage"] = stage
    stages = diagnostics.setdefault("stages", [])
    if stage not in stages:
        stages.append(stage)
    _trace_stage(stage)


def _mark_failure(diagnostics: dict | None, *, stage: str, exc: BaseException | None = None, summary: str = "") -> None:
    if diagnostics is None:
        return
    diagnostics["failure_stage"] = stage
    if exc is not None:
        diagnostics["exception_type"] = type(exc).__name__
        diagnostics["exception_summary"] = str(exc)
    elif summary:
        diagnostics["exception_summary"] = summary
    _trace_stage(stage)


def _authority_guarantees() -> dict:
    return {
        "native_bridge": "NATIVE_BRIDGE_LOCAL_ONLY",
        "operator_triggered": True,
        "canonical_python_runtime": True,
        "provider_calls": "CODEX_CLI_ONLY",
        "dispatch": False,
        "approval": False,
        "execution": "BOUNDED_CODEX_CLI_ONLY",
        "real_codex_execution": True,
        "orchestration": False,
        "autonomous_continuation": False,
        "durable_replay_backend": False,
        "localhost_http_server": False,
        "internet_transport": False,
    }


def _diagnostic_evidence(
    *,
    failing_layer: str,
    failing_function: str,
    failing_condition: str,
    python_runtime_bridge_called: bool,
    provider_invoked: bool,
    subprocess_invoked: bool,
    response_serialization_ready: bool,
    provider: dict | None = None,
    traceback_summary: str = "",
    native_stages: dict | None = None,
) -> dict:
    stage_state = deepcopy(native_stages or _native_stage_context())
    native_bridge = {
        "failing_layer": failing_layer,
        "failing_function": failing_function,
        "failing_condition": failing_condition,
        "handle_native_message_called": True,
        "python_runtime_bridge_called": python_runtime_bridge_called,
        "provider_invoked": provider_invoked,
        "subprocess_invoked": subprocess_invoked,
        "response_serialization_ready": response_serialization_ready,
        "traceback_summary": traceback_summary,
        **stage_state,
    }
    return {
        "failing_layer": failing_layer,
        "failing_function": failing_function,
        "failing_condition": failing_condition,
        "python_runtime_bridge_called": python_runtime_bridge_called,
        "provider_invoked": provider_invoked,
        "subprocess_invoked": subprocess_invoked,
        "response_serialization_ready": response_serialization_ready,
        "traceback_summary": traceback_summary,
        "native_bridge": native_bridge,
        "provider": deepcopy(provider or {}),
    }


def _reject(reason: str, *, message: dict | None = None) -> dict:
    safe_message = deepcopy(message or {})
    return {
        "status": NATIVE_BRIDGE_REJECTED,
        "rejection_reason": reason,
        "request_id": safe_message.get("request_id", "UNKNOWN"),
        "session_id": safe_message.get("session_id", "UNKNOWN"),
        "result_artifact": {},
        "governed_return": {
            "status": "REJECTED",
            "reason": reason,
            "non_authority_reminder": "No approval, dispatch, orchestration, retry, or autonomous continuation authority was created.",
        },
        "labels": [
            "NATIVE_BRIDGE_LOCAL_ONLY",
            "OPERATOR_TRIGGERED",
            "CANONICAL_PYTHON_RUNTIME",
            "REAL_CODEX_EXECUTION",
            "BOUNDED_CODEX_CLI_PROVIDER",
            "NO_AUTONOMOUS_CONTINUATION",
        ],
        "authority_guarantees": _authority_guarantees(),
        "diagnostic_evidence": _diagnostic_evidence(
            failing_layer="native_message_validation",
            failing_function="handle_native_message",
            failing_condition=reason,
            python_runtime_bridge_called=False,
            provider_invoked=False,
            subprocess_invoked=False,
            response_serialization_ready=True,
            native_stages=safe_message.get("_native_stages") if isinstance(safe_message.get("_native_stages"), dict) else None,
        ),
    }


def _message_error(message: object) -> str:
    if not isinstance(message, dict) or isinstance(message, list):
        return "native bridge message must be a JSON object"
    if message.get("action") != NATIVE_BRIDGE_ACTION:
        return "unsupported native bridge action"
    if not isinstance(message.get("human_request"), str) or not message.get("human_request", "").strip():
        return "human_request is required"
    if not isinstance(message.get("session_id"), str) or not message.get("session_id", "").strip():
        return "session_id is required"
    if message.get("operator_triggered") is not True:
        return "operator_triggered must be true"
    if message.get("authority_boundary") != "SEMANTIC_TRANSPORT_ONLY":
        return "authority_boundary must be SEMANTIC_TRANSPORT_ONLY"
    return ""


def handle_native_message(message: dict, native_stages: dict | None = None) -> dict:
    """Validate a native bridge message and return a canonical result artifact."""

    safe_message = deepcopy(message or {})
    _mark_stage(native_stages, NATIVE_STAGE_HANDLE_ENTERED)
    if isinstance(safe_message, dict) and native_stages is not None:
        safe_message["_native_stages"] = native_stages
    try:
        error = _message_error(safe_message)
        if error:
            return _reject(error, message=safe_message if isinstance(safe_message, dict) else {})

        _mark_stage(native_stages, NATIVE_STAGE_RUNTIME_BRIDGE_ENTERED)
        bridge_result = run_minimal_end_to_end_bridge(
            human_request=safe_message["human_request"].strip(),
            session_id=safe_message["session_id"].strip(),
            workspace_path=str(Path(safe_message.get("workspace_path") or Path.cwd()).expanduser().resolve()),
            timeout_seconds=int(safe_message.get("timeout_seconds", 600)),
        )
    except Exception as exc:  # noqa: BLE001 - Native Messaging must return structured errors.
        failure_stage = native_stages.get("stage_reached") if native_stages else NATIVE_STAGE_HANDLE_ENTERED
        _mark_failure(native_stages, stage=failure_stage or NATIVE_STAGE_HANDLE_ENTERED, exc=exc)
        return _error_response(
            error_code="NATIVE_BRIDGE_EXCEPTION",
            error_message=str(exc),
            message=safe_message if isinstance(safe_message, dict) else {},
            failure_layer="handle_native_message",
            failing_function="handle_native_message",
            traceback_summary="".join(traceback.format_exception_only(type(exc), exc)).strip(),
            native_stages=native_stages,
        )
    _mark_stage(native_stages, NATIVE_STAGE_PROVIDER_ATTEMPT)
    if bridge_result.get("status") != BRIDGE_ACCEPTED:
        provider_diagnostics = (
            bridge_result.get("codex_cli_result", {})
            .get("provider_result", {})
            .get("diagnostic_evidence", {})
        )
        return {
            "status": NATIVE_BRIDGE_REJECTED,
            "rejection_reason": bridge_result.get("governed_chat_return", {}).get("reason", "canonical bridge runtime rejected request"),
            "request_id": safe_message.get("request_id", "UNKNOWN"),
            "session_id": safe_message["session_id"].strip(),
            "result_artifact": {},
            "bridge_result": bridge_result,
            "governed_return": bridge_result.get("governed_chat_return", {}),
            "labels": [
                "NATIVE_BRIDGE_LOCAL_ONLY",
                "OPERATOR_TRIGGERED",
                "CANONICAL_PYTHON_RUNTIME",
                "REAL_CODEX_EXECUTION",
                "BOUNDED_CODEX_CLI_PROVIDER",
                "NO_AUTONOMOUS_CONTINUATION",
            ],
            "authority_guarantees": _authority_guarantees(),
            "diagnostic_evidence": _diagnostic_evidence(
                failing_layer="python_runtime_bridge",
                failing_function="run_minimal_end_to_end_bridge",
                failing_condition=bridge_result.get("governed_chat_return", {}).get("reason", "canonical bridge runtime rejected request"),
                python_runtime_bridge_called=True,
                provider_invoked=bool(bridge_result.get("codex_cli_result", {}).get("provider_invoked")),
                subprocess_invoked=bool(provider_diagnostics.get("subprocess_invoked")),
                response_serialization_ready=True,
                provider=provider_diagnostics,
                native_stages=native_stages,
            ),
        }

    artifact = export_minimal_bridge_result_artifact(bridge_result)
    provider_diagnostics = (
        artifact.get("codex_cli_result", {})
        .get("provider_result", {})
        .get("diagnostic_evidence", {})
    )
    return {
        "status": NATIVE_BRIDGE_ACCEPTED,
        "rejection_reason": "",
        "request_id": safe_message.get("request_id", "UNKNOWN"),
        "session_id": safe_message["session_id"].strip(),
        "proposal_id": artifact["proposal_id"],
        "result_artifact": artifact,
        "governed_return": artifact["governed_chat_return"],
        "labels": [
            "NATIVE_BRIDGE_LOCAL_ONLY",
            "OPERATOR_TRIGGERED",
            "CANONICAL_PYTHON_RUNTIME",
            "REAL_CODEX_EXECUTION",
            "BOUNDED_CODEX_CLI_PROVIDER",
            "NO_AUTONOMOUS_CONTINUATION",
        ],
        "authority_guarantees": _authority_guarantees(),
        "diagnostic_evidence": _diagnostic_evidence(
            failing_layer="",
            failing_function="",
            failing_condition="",
            python_runtime_bridge_called=True,
            provider_invoked=bool(artifact.get("codex_cli_result", {}).get("provider_invoked")),
            subprocess_invoked=bool(provider_diagnostics.get("subprocess_invoked")),
            response_serialization_ready=True,
            provider=provider_diagnostics,
            native_stages=native_stages,
        ),
    }


def _error_response(
    *,
    error_code: str,
    error_message: str,
    message: dict | None = None,
    failure_layer: str,
    failing_function: str,
    traceback_summary: str = "",
    native_stages: dict | None = None,
) -> dict:
    safe_message = deepcopy(message or {})
    return {
        "status": NATIVE_BRIDGE_ERROR,
        "error_code": error_code,
        "error_message": error_message,
        "failure_layer": failure_layer,
        "traceback_summary": traceback_summary,
        "request_id": safe_message.get("request_id", "UNKNOWN"),
        "session_id": safe_message.get("session_id", "UNKNOWN"),
        "result_artifact": {},
        "governed_return": {
            "status": "ERROR",
            "reason": error_message,
            "non_authority_reminder": "No approval, dispatch, orchestration, retry, or autonomous continuation authority was created.",
        },
        "labels": [
            "NATIVE_BRIDGE_LOCAL_ONLY",
            "OPERATOR_TRIGGERED",
            "CANONICAL_PYTHON_RUNTIME",
            "REAL_CODEX_EXECUTION",
            "BOUNDED_CODEX_CLI_PROVIDER",
            "NO_AUTONOMOUS_CONTINUATION",
        ],
        "authority_guarantees": _authority_guarantees(),
        "diagnostic_evidence": _diagnostic_evidence(
            failing_layer=failure_layer,
            failing_function=failing_function,
            failing_condition=error_message,
            python_runtime_bridge_called=False,
            provider_invoked=False,
            subprocess_invoked=False,
            response_serialization_ready=True,
            traceback_summary=traceback_summary,
            native_stages=native_stages,
        ),
    }


def read_native_message(stream: BinaryIO, native_stages: dict | None = None) -> dict | None:
    _mark_stage(native_stages, NATIVE_STAGE_READ_MESSAGE)
    raw_length = stream.read(4)
    if not raw_length:
        return None
    if len(raw_length) != 4:
        return {}
    message_length = struct.unpack("<I", raw_length)[0]
    if message_length == 0:
        return {}
    payload = stream.read(message_length)
    if len(payload) != message_length:
        return {}
    try:
        message = json.loads(payload.decode("utf-8"))
        _mark_stage(native_stages, NATIVE_STAGE_JSON_PARSED)
        return message
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        _mark_failure(native_stages, stage=NATIVE_STAGE_JSON_PARSED, exc=exc)
        return {}


def _json_default(value: Any) -> str:
    return str(value)


def _attach_write_stages(message: dict, native_stages: dict | None) -> dict:
    response = deepcopy(message or {})
    if native_stages is None:
        return response
    native_stages["response_written"] = True
    native_stages["response_flushed"] = True
    diagnostics = response.setdefault("diagnostic_evidence", {})
    native_bridge = diagnostics.setdefault("native_bridge", {})
    native_bridge.update(deepcopy(native_stages))
    diagnostics["response_serialization_ready"] = True
    diagnostics["native_bridge"] = native_bridge
    return response


def write_native_message(stream: BinaryIO, message: dict, native_stages: dict | None = None) -> None:
    _mark_stage(native_stages, NATIVE_STAGE_WRITE_RESPONSE)
    _mark_stage(native_stages, NATIVE_STAGE_RESPONSE_FLUSHED)
    response = _attach_write_stages(message, native_stages)
    encoded = json.dumps(response, sort_keys=True, separators=(",", ":"), default=_json_default).encode("utf-8")
    stream.write(struct.pack("<I", len(encoded)))
    stream.write(encoded)
    stream.flush()


def main() -> int:
    native_stages = _native_stage_context()
    try:
        message = read_native_message(sys.stdin.buffer, native_stages=native_stages)
        if message is None:
            return 0
        response = handle_native_message(message, native_stages=native_stages)
    except Exception as exc:  # noqa: BLE001 - stdout must still receive one framed response.
        _mark_failure(native_stages, stage=native_stages.get("stage_reached") or "native_host_main", exc=exc)
        response = _error_response(
            error_code="NATIVE_HOST_UNCAUGHT_EXCEPTION",
            error_message=str(exc),
            message={},
            failure_layer="native_host_main",
            failing_function="main",
            traceback_summary="".join(traceback.format_exception_only(type(exc), exc)).strip(),
            native_stages=native_stages,
        )
    write_native_message(sys.stdout.buffer, response, native_stages=native_stages)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
