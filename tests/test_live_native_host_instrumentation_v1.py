import json
import os
import struct
import subprocess
from io import BytesIO
from pathlib import Path

import agol_bridge.native.native_messaging_host as native_host
from agol_bridge.native.native_messaging_host import (
    NATIVE_BRIDGE_ACCEPTED,
    NATIVE_BRIDGE_REJECTED,
    NATIVE_STAGE_HANDLE_ENTERED,
    NATIVE_STAGE_JSON_PARSED,
    NATIVE_STAGE_PROVIDER_ATTEMPT,
    NATIVE_STAGE_READ_MESSAGE,
    NATIVE_STAGE_RESPONSE_FLUSHED,
    NATIVE_STAGE_RUNTIME_BRIDGE_ENTERED,
    NATIVE_STAGE_WRITE_RESPONSE,
    handle_native_message,
    read_native_message,
    write_native_message,
)


ROOT = Path(__file__).resolve().parents[1]
HOST = ROOT / "agol_bridge" / "native" / "native_messaging_host.py"
SERVICE_WORKER = ROOT / "browser_companion" / "service_worker.js"


def _message(tmp_path):
    return {
        "action": "RUN_MINIMAL_END_TO_END_BRIDGE",
        "request_id": "LIVE-NATIVE-HOST-INSTRUMENTATION",
        "human_request": "Trace live native host continuity.",
        "session_id": "SESSION-LIVE-NATIVE-HOST-INSTRUMENTATION",
        "workspace_path": str(tmp_path),
        "timeout_seconds": 30,
        "operator_triggered": True,
        "authority_boundary": "SEMANTIC_TRANSPORT_ONLY",
    }


def _frame(payload: dict) -> bytes:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return struct.pack("<I", len(encoded)) + encoded


def _decode_frame(raw: bytes) -> dict:
    length = struct.unpack("<I", raw[:4])[0]
    assert len(raw[4:]) == length
    return json.loads(raw[4:].decode("utf-8"))


def test_read_message_stage_recorded(tmp_path):
    stages = native_host._native_stage_context()
    read_native_message(BytesIO(_frame(_message(tmp_path))), native_stages=stages)

    assert NATIVE_STAGE_READ_MESSAGE in stages["stages"]


def test_json_parse_stage_recorded(tmp_path):
    stages = native_host._native_stage_context()
    read_native_message(BytesIO(_frame(_message(tmp_path))), native_stages=stages)

    assert NATIVE_STAGE_JSON_PARSED in stages["stages"]


def test_handle_native_message_stage_recorded(monkeypatch, tmp_path):
    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(command, 0, stdout="traced", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    stages = native_host._native_stage_context()
    response = handle_native_message(_message(tmp_path), native_stages=stages)

    assert response["status"] == NATIVE_BRIDGE_ACCEPTED
    assert NATIVE_STAGE_HANDLE_ENTERED in response["diagnostic_evidence"]["native_bridge"]["stages"]


def test_write_native_message_stage_recorded():
    stages = native_host._native_stage_context()
    output = BytesIO()

    write_native_message(output, {"status": "OK"}, native_stages=stages)
    response = _decode_frame(output.getvalue())

    assert NATIVE_STAGE_WRITE_RESPONSE in response["diagnostic_evidence"]["native_bridge"]["stages"]


def test_structured_response_flush_recorded():
    stages = native_host._native_stage_context()
    output = BytesIO()

    write_native_message(output, {"status": "OK"}, native_stages=stages)
    response = _decode_frame(output.getvalue())

    native_bridge = response["diagnostic_evidence"]["native_bridge"]
    assert NATIVE_STAGE_RESPONSE_FLUSHED in native_bridge["stages"]
    assert native_bridge["response_written"] is True
    assert native_bridge["response_flushed"] is True


def test_stderr_instrumentation_does_not_contaminate_stdout(tmp_path):
    env = os.environ.copy()
    env["AIGOL_NATIVE_TRACE"] = "1"

    result = subprocess.run(
        ["python", str(HOST)],
        cwd=str(ROOT),
        input=_frame({"action": "RUN_MINIMAL_END_TO_END_BRIDGE", "human_request": ""}),
        capture_output=True,
        timeout=5,
        check=False,
        env=env,
    )

    response = _decode_frame(result.stdout)
    assert response["status"] == NATIVE_BRIDGE_REJECTED
    assert result.stdout[4:5] == b"{"
    assert b"[NATIVE_STAGE_READ_MESSAGE]" not in result.stdout
    assert b"[NATIVE_STAGE_READ_MESSAGE]" in result.stderr


def test_stdout_still_contains_only_framed_payload(tmp_path):
    result = subprocess.run(
        ["python", str(HOST)],
        cwd=str(ROOT),
        input=_frame({"action": "RUN_MINIMAL_END_TO_END_BRIDGE", "human_request": ""}),
        capture_output=True,
        timeout=5,
        check=False,
    )

    length = struct.unpack("<I", result.stdout[:4])[0]
    assert len(result.stdout[4:]) == length
    assert result.stdout[4 + length :] == b""


def test_structured_exception_response_preserves_failure_stage(monkeypatch, tmp_path):
    def raise_bridge(**kwargs):
        raise RuntimeError("instrumented failure")

    monkeypatch.setattr(native_host, "run_minimal_end_to_end_bridge", raise_bridge)
    stages = native_host._native_stage_context()

    response = handle_native_message(_message(tmp_path), native_stages=stages)

    native_bridge = response["diagnostic_evidence"]["native_bridge"]
    assert native_bridge["failure_stage"] == NATIVE_STAGE_RUNTIME_BRIDGE_ENTERED
    assert native_bridge["stage_reached"] == NATIVE_STAGE_RUNTIME_BRIDGE_ENTERED
    assert native_bridge["exception_summary"] == "instrumented failure"
    assert response["failure_layer"] == "handle_native_message"


def test_service_worker_preserves_native_bridge_diagnostics():
    source = SERVICE_WORKER.read_text(encoding="utf-8")

    assert "native_bridge: nativeDiagnostics.native_bridge || nativeDiagnostics" in source
    assert "provider: nativeDiagnostics.provider || {}" in source
    assert "response_serialization_ready" in source


def test_provider_attempt_stage_visible_when_reached(monkeypatch, tmp_path):
    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(command, 0, stdout="provider traced", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    stages = native_host._native_stage_context()
    response = handle_native_message(_message(tmp_path), native_stages=stages)

    assert NATIVE_STAGE_PROVIDER_ATTEMPT in response["diagnostic_evidence"]["native_bridge"]["stages"]
    assert response["diagnostic_evidence"]["provider_invoked"] is True


def test_provider_not_reached_explicitly_diagnosed():
    stages = native_host._native_stage_context()
    response = handle_native_message({"action": "RUN_MINIMAL_END_TO_END_BRIDGE", "human_request": ""}, native_stages=stages)

    native_bridge = response["diagnostic_evidence"]["native_bridge"]
    assert response["status"] == NATIVE_BRIDGE_REJECTED
    assert native_bridge["provider_invoked"] is False
    assert response["diagnostic_evidence"]["provider"] == {}


def test_fail_closed_behavior_preserved():
    response = handle_native_message({"action": "RUN_MINIMAL_END_TO_END_BRIDGE", "human_request": ""})

    assert response["status"] == NATIVE_BRIDGE_REJECTED
    assert response["governed_return"]["status"] == "REJECTED"


def test_native_messaging_framing_remains_valid():
    output = BytesIO()
    write_native_message(output, {"status": "OK"}, native_stages=native_host._native_stage_context())

    assert _decode_frame(output.getvalue())["status"] == "OK"
