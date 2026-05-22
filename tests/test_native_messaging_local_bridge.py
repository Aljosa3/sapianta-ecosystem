import json
import subprocess
import struct
from copy import deepcopy
from io import BytesIO
from pathlib import Path

from agol_bridge.native.native_messaging_host import (
    NATIVE_BRIDGE_ACCEPTED,
    NATIVE_BRIDGE_REJECTED,
    handle_native_message,
    read_native_message,
    write_native_message,
)
from agol_bridge.runtime.minimal_end_to_end_bridge import BRIDGE_RESULT_ARTIFACT_TYPE
from agol_bridge.transport.local_governed_transport import canonical_hash


ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT / "browser_companion"
HOST = ROOT / "agol_bridge" / "native" / "native_messaging_host.py"
MANIFEST = COMPANION / "manifest.json"
HOST_MANIFEST = COMPANION / "native_host_manifest.example.json"
SIDEPANEL_HTML = COMPANION / "sidepanel.html"
SIDEPANEL_JS = COMPANION / "sidepanel.js"
SERVICE_WORKER = COMPANION / "service_worker.js"


def _hash_input(artifact: dict) -> dict:
    artifact_copy = deepcopy(artifact)
    artifact_copy.pop("artifact_hash", None)
    return artifact_copy


def _valid_message(tmp_path: Path | None = None) -> dict:
    return {
        "action": "RUN_MINIMAL_END_TO_END_BRIDGE",
        "request_id": "NATIVE-BRIDGE-REQUEST-TEST",
        "human_request": "Review this request through the native local bridge.",
        "session_id": "SESSION-NATIVE-BRIDGE-1",
        "workspace_path": str((tmp_path or ROOT).resolve()),
        "timeout_seconds": 30,
        "operator_triggered": True,
        "authority_boundary": "SEMANTIC_TRANSPORT_ONLY",
    }


def _mock_codex(monkeypatch):
    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(command, 0, stdout="native bounded codex complete", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)


def _html() -> str:
    return SIDEPANEL_HTML.read_text(encoding="utf-8")


def _js() -> str:
    return SIDEPANEL_JS.read_text(encoding="utf-8")


def _combined() -> str:
    return "\n".join(
        (
            _html(),
            _js(),
            SERVICE_WORKER.read_text(encoding="utf-8"),
            MANIFEST.read_text(encoding="utf-8"),
            HOST.read_text(encoding="utf-8"),
            HOST_MANIFEST.read_text(encoding="utf-8"),
        )
    )


def test_native_host_accepts_valid_message_and_returns_canonical_artifact(monkeypatch, tmp_path):
    _mock_codex(monkeypatch)
    response = handle_native_message(_valid_message(tmp_path))
    artifact = response["result_artifact"]

    assert response["status"] == NATIVE_BRIDGE_ACCEPTED
    assert response["request_id"] == "NATIVE-BRIDGE-REQUEST-TEST"
    assert artifact["artifact_type"] == BRIDGE_RESULT_ARTIFACT_TYPE
    assert artifact["session_id"] == "SESSION-NATIVE-BRIDGE-1"
    assert artifact["codex_cli_result"]["bounded_execution_status"] == "COMPLETED"
    assert artifact["artifact_hash"] == canonical_hash(_hash_input(artifact))
    assert response["governed_return"]["status"] == "ACCEPTED"


def test_native_host_rejects_malformed_message():
    response = handle_native_message({"action": "RUN_MINIMAL_END_TO_END_BRIDGE", "human_request": ""})

    assert response["status"] == NATIVE_BRIDGE_REJECTED
    assert response["result_artifact"] == {}
    assert response["governed_return"]["status"] == "REJECTED"
    assert "human_request is required" in response["rejection_reason"]


def test_native_host_requires_operator_trigger_and_authority_boundary():
    missing_trigger = _valid_message()
    missing_trigger["operator_triggered"] = False
    bad_authority = _valid_message()
    bad_authority["authority_boundary"] = "EXECUTION_ALLOWED"

    assert handle_native_message(missing_trigger)["status"] == NATIVE_BRIDGE_REJECTED
    assert handle_native_message(bad_authority)["status"] == NATIVE_BRIDGE_REJECTED


def test_native_host_output_is_deterministic(monkeypatch, tmp_path):
    _mock_codex(monkeypatch)
    first = handle_native_message(_valid_message(tmp_path))
    second = handle_native_message(_valid_message(tmp_path))

    assert first == second


def test_native_messaging_protocol_reads_and_writes_length_prefixed_messages():
    message = _valid_message()
    encoded = json.dumps(message, sort_keys=True, separators=(",", ":")).encode("utf-8")
    framed = BytesIO(struct.pack("<I", len(encoded)) + encoded)

    assert read_native_message(framed) == message

    output = BytesIO()
    write_native_message(output, {"status": "OK"})
    output.seek(0)
    response_length = struct.unpack("<I", output.read(4))[0]
    response = json.loads(output.read(response_length).decode("utf-8"))
    assert response == {"status": "OK"}


def test_extension_manifest_declares_native_messaging_and_host_manifest_exists():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    host_manifest = json.loads(HOST_MANIFEST.read_text(encoding="utf-8"))

    assert "nativeMessaging" in manifest["permissions"]
    assert manifest["background"]["service_worker"] == "service_worker.js"
    assert host_manifest["name"] == "com.sapianta.aigol_bridge"
    assert host_manifest["type"] == "stdio"
    assert "allowed_origins" in host_manifest


def test_sidepanel_contains_explicit_native_bridge_button_and_labels():
    combined = _combined()

    assert 'id="run-native-bridge"' in combined
    assert "Run via Native Bridge" in combined
    assert "NATIVE_BRIDGE_LOCAL_ONLY" in combined
    assert "OPERATOR_TRIGGERED" in combined
    assert "CANONICAL_PYTHON_RUNTIME" in combined
    assert "REAL_CODEX_EXECUTION" in combined
    assert "BOUNDED_CODEX_CLI_PROVIDER" in combined
    assert "NO_AUTONOMOUS_CONTINUATION" in combined


def test_sidepanel_sends_native_message_only_from_button_click():
    source = _js()
    worker = SERVICE_WORKER.read_text(encoding="utf-8")

    assert "function runNativeBridgeFromSidepanel()" in source
    assert "chrome.runtime.sendMessage({" in source
    assert "chrome.runtime.sendNativeMessage(NATIVE_BRIDGE_HOST, nativeMessage" in worker
    assert "runNativeBridgeButton.onclick = runNativeBridgeFromSidepanel;" in source
    assert "nativeBridgeMessageFromSidepanel()" in source
    assert "operator_triggered: true" in source


def test_no_fetch_http_server_or_orchestration_added():
    lowered = _combined().lower().replace("localhost_http_server", "localhost-http-server-label")

    forbidden = (
        "fetch(",
        "xmlhttprequest",
        "websocket",
        "eventsource",
        "threadinghttpserver",
        "httpserver(",
        "serve_forever",
        "socket.",
        "requests.",
        "urllib",
        "setinterval",
        "addeventlistener(\"message\"",
        "addeventlistener('message'",
        "dispatchtask",
        "approvetask",
        "executeprovider",
        "orchestrationruntime",
        "autonomouscontinuation",
    )
    for token in forbidden:
        assert token not in lowered


def test_native_response_preserves_bounded_provider_and_no_orchestration(monkeypatch, tmp_path):
    _mock_codex(monkeypatch)
    response = handle_native_message(_valid_message(tmp_path))
    artifact = response["result_artifact"]
    codex_result = artifact["codex_cli_result"]
    guarantees = response["authority_guarantees"]

    assert codex_result["provider_invoked"] is True
    assert codex_result["execution_authority_created"] is False
    assert codex_result["orchestration_created"] is False
    assert guarantees["provider_calls"] == "CODEX_CLI_ONLY"
    assert guarantees["execution"] == "BOUNDED_CODEX_CLI_ONLY"
    assert guarantees["orchestration"] is False
    assert guarantees["autonomous_continuation"] is False
