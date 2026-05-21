#!/usr/bin/env python3
"""Chrome Native Messaging host for the minimal AiGOL bridge.

The host is intentionally one-shot: Chrome launches it, sends one explicit
operator-triggered message, receives one governed response, and the process
exits. It does not start a server, listener, provider call, or orchestration
loop.
"""

from __future__ import annotations

import json
import struct
import sys
from copy import deepcopy
from typing import BinaryIO

from agol_bridge.runtime.minimal_end_to_end_bridge import (
    BRIDGE_ACCEPTED,
    export_minimal_bridge_result_artifact,
    run_minimal_end_to_end_bridge,
)

NATIVE_HOST_NAME = "com.sapianta.aigol_bridge"
NATIVE_BRIDGE_ACCEPTED = "NATIVE_BRIDGE_ACCEPTED"
NATIVE_BRIDGE_REJECTED = "NATIVE_BRIDGE_REJECTED"
NATIVE_BRIDGE_ACTION = "RUN_MINIMAL_END_TO_END_BRIDGE"


def _authority_guarantees() -> dict:
    return {
        "native_bridge": "NATIVE_BRIDGE_LOCAL_ONLY",
        "operator_triggered": True,
        "canonical_python_runtime": True,
        "provider_calls": False,
        "dispatch": False,
        "approval": False,
        "execution": False,
        "real_codex_execution": False,
        "orchestration": False,
        "autonomous_continuation": False,
        "durable_replay_backend": False,
        "localhost_http_server": False,
        "internet_transport": False,
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
            "non_authority_reminder": "No execution occurred. No provider was invoked. No approval, dispatch, or continuation authority was created.",
        },
        "labels": [
            "NATIVE_BRIDGE_LOCAL_ONLY",
            "OPERATOR_TRIGGERED",
            "CANONICAL_PYTHON_RUNTIME",
            "NO_REAL_CODEX_EXECUTION",
            "NO_PROVIDER_CALLS",
            "NO_AUTONOMOUS_CONTINUATION",
        ],
        "authority_guarantees": _authority_guarantees(),
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


def handle_native_message(message: dict) -> dict:
    """Validate a native bridge message and return a canonical result artifact."""

    safe_message = deepcopy(message or {})
    error = _message_error(safe_message)
    if error:
        return _reject(error, message=safe_message if isinstance(safe_message, dict) else {})

    bridge_result = run_minimal_end_to_end_bridge(
        human_request=safe_message["human_request"].strip(),
        session_id=safe_message["session_id"].strip(),
    )
    if bridge_result.get("status") != BRIDGE_ACCEPTED:
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
                "NO_REAL_CODEX_EXECUTION",
                "NO_PROVIDER_CALLS",
                "NO_AUTONOMOUS_CONTINUATION",
            ],
            "authority_guarantees": _authority_guarantees(),
        }

    artifact = export_minimal_bridge_result_artifact(bridge_result)
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
            "NO_REAL_CODEX_EXECUTION",
            "NO_PROVIDER_CALLS",
            "NO_AUTONOMOUS_CONTINUATION",
        ],
        "authority_guarantees": _authority_guarantees(),
    }


def read_native_message(stream: BinaryIO) -> dict | None:
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
        return json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}


def write_native_message(stream: BinaryIO, message: dict) -> None:
    encoded = json.dumps(message, sort_keys=True, separators=(",", ":")).encode("utf-8")
    stream.write(struct.pack("<I", len(encoded)))
    stream.write(encoded)
    stream.flush()


def main() -> int:
    message = read_native_message(sys.stdin.buffer)
    if message is None:
        return 0
    response = handle_native_message(message)
    write_native_message(sys.stdout.buffer, response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
