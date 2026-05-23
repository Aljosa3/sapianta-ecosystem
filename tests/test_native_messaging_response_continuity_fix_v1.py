import json
import struct
import subprocess
from io import BytesIO
from pathlib import Path

import agol_bridge.native.native_messaging_host as native_host
from agol_bridge.native.native_messaging_host import (
    NATIVE_BRIDGE_ACCEPTED,
    NATIVE_BRIDGE_ERROR,
    NATIVE_BRIDGE_REJECTED,
    handle_native_message,
    read_native_message,
    write_native_message,
)


ROOT = Path(__file__).resolve().parents[1]
HOST = ROOT / "agol_bridge" / "native" / "native_messaging_host.py"
SERVICE_WORKER = ROOT / "browser_companion" / "service_worker.js"
SIDEPANEL = ROOT / "browser_companion" / "sidepanel.js"


def _message(tmp_path):
    return {
        "action": "RUN_MINIMAL_END_TO_END_BRIDGE",
        "request_id": "NATIVE-RESPONSE-CONTINUITY-FIX",
        "human_request": "Verify native response continuity.",
        "session_id": "SESSION-NATIVE-RESPONSE-CONTINUITY",
        "workspace_path": str(tmp_path),
        "timeout_seconds": 30,
        "operator_triggered": True,
        "authority_boundary": "SEMANTIC_TRANSPORT_ONLY",
    }


def _frame(payload: dict) -> bytes:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return struct.pack("<I", len(encoded)) + encoded


def _decode_frame(raw: bytes) -> dict:
    assert len(raw) >= 4
    length = struct.unpack("<I", raw[:4])[0]
    payload = raw[4:]
    assert len(payload) == length
    return json.loads(payload.decode("utf-8"))


def test_write_message_emits_valid_chrome_native_messaging_frame():
    output = BytesIO()

    write_native_message(output, {"status": "OK", "diagnostic_evidence": {"native_bridge": {}}})

    decoded = _decode_frame(output.getvalue())
    assert decoded["status"] == "OK"
    assert decoded["diagnostic_evidence"]["native_bridge"] == {}


def test_write_message_stdout_contains_only_binary_framed_json():
    output = BytesIO()

    write_native_message(output, {"status": "OK"})
    raw = output.getvalue()
    length = struct.unpack("<I", raw[:4])[0]

    assert raw[4:].startswith(b"{")
    assert raw[4 + length :] == b""


def test_no_print_debug_text_contaminates_stdout():
    result = subprocess.run(
        ["python", str(HOST)],
        cwd=str(ROOT),
        input=_frame({"action": "RUN_MINIMAL_END_TO_END_BRIDGE", "human_request": ""}),
        capture_output=True,
        timeout=5,
        check=False,
    )

    decoded = _decode_frame(result.stdout)
    assert result.returncode == 0
    assert decoded["status"] == NATIVE_BRIDGE_REJECTED
    assert result.stdout[4:5] == b"{"
    assert b"Traceback" not in result.stdout


def test_handle_native_message_returns_structured_response_on_success(monkeypatch, tmp_path):
    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(command, 0, stdout="success", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    response = handle_native_message(_message(tmp_path))

    assert response["status"] == NATIVE_BRIDGE_ACCEPTED
    assert response["result_artifact"]["codex_cli_result"]["provider_invoked"] is True
    assert response["diagnostic_evidence"]["native_bridge"]["handle_native_message_called"] is True
    assert response["diagnostic_evidence"]["provider"]["provider_invoked"] is True


def test_handle_native_message_returns_structured_error_on_exception(monkeypatch, tmp_path):
    def raise_bridge(**kwargs):
        raise RuntimeError("forced bridge failure")

    monkeypatch.setattr(native_host, "run_minimal_end_to_end_bridge", raise_bridge)

    response = handle_native_message(_message(tmp_path))

    assert response["status"] == NATIVE_BRIDGE_ERROR
    assert response["error_code"] == "NATIVE_BRIDGE_EXCEPTION"
    assert response["failure_layer"] == "handle_native_message"
    assert response["diagnostic_evidence"]["native_bridge"]["failing_condition"] == "forced bridge failure"


def test_native_response_includes_diagnostic_evidence_native_bridge():
    response = handle_native_message({"action": "RUN_MINIMAL_END_TO_END_BRIDGE", "human_request": ""})

    assert response["status"] == NATIVE_BRIDGE_REJECTED
    assert "native_bridge" in response["diagnostic_evidence"]
    assert response["diagnostic_evidence"]["native_bridge"]["failing_layer"] == "native_message_validation"


def test_service_worker_preserves_native_bridge_diagnostic_evidence():
    source = SERVICE_WORKER.read_text(encoding="utf-8")

    assert "native_bridge: nativeDiagnostics.native_bridge || nativeDiagnostics" in source
    assert "provider: nativeDiagnostics.provider || {}" in source
    assert "NATIVE_BRIDGE_ERROR" in source


def test_malformed_native_request_returns_structured_error_response():
    framed = BytesIO(_frame({"action": "RUN_MINIMAL_END_TO_END_BRIDGE", "human_request": ""}))
    message = read_native_message(framed)
    response = handle_native_message(message)

    assert response["status"] == NATIVE_BRIDGE_REJECTED
    assert response["result_artifact"] == {}
    assert response["diagnostic_evidence"]["provider"] == {}


def test_provider_failure_returns_structured_response_not_broken_framing(monkeypatch, tmp_path):
    def fake_run(command, **kwargs):
        raise FileNotFoundError("codex missing")

    monkeypatch.setattr(subprocess, "run", fake_run)
    response = handle_native_message(_message(tmp_path))
    output = BytesIO()

    write_native_message(output, response)
    decoded = _decode_frame(output.getvalue())

    assert decoded["status"] == NATIVE_BRIDGE_ACCEPTED
    assert decoded["result_artifact"]["codex_cli_result"]["bounded_execution_status"] == "FAILED"
    assert decoded["diagnostic_evidence"]["provider"]["subprocess_invoked"] is True


def test_provider_not_reached_is_explicitly_diagnosed():
    response = handle_native_message({"action": "RUN_MINIMAL_END_TO_END_BRIDGE", "human_request": ""})

    assert response["diagnostic_evidence"]["native_bridge"]["python_runtime_bridge_called"] is False
    assert response["diagnostic_evidence"]["native_bridge"]["provider_invoked"] is False
    assert response["diagnostic_evidence"]["provider"] == {}


def test_response_serialization_never_raises_uncaught_exception():
    output = BytesIO()

    write_native_message(output, {"status": "OK", "path": Path("not-json-native")})
    decoded = _decode_frame(output.getvalue())

    assert decoded["path"] == "not-json-native"


def test_sidepanel_receives_diagnostic_evidence():
    source = SIDEPANEL.read_text(encoding="utf-8")

    assert "nativeDiagnostics.native_bridge || serviceWorkerDiagnostics.native_bridge || nativeDiagnostics" in source
    assert "providerDiagnostics" in source
    assert "`diagnostic_evidence: ${compactValue(summary.diagnostic_evidence || {})}`" in source


def test_fail_closed_behavior_preserved():
    response = handle_native_message({"action": "RUN_MINIMAL_END_TO_END_BRIDGE", "human_request": ""})

    assert response["status"] == NATIVE_BRIDGE_REJECTED
    assert response["governed_return"]["status"] == "REJECTED"
    assert response["diagnostic_evidence"]["provider_invoked"] is False
