import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT / "browser_companion"
MANIFEST = COMPANION / "manifest.json"
SIDEPANEL_JS = COMPANION / "sidepanel.js"
SERVICE_WORKER = COMPANION / "service_worker.js"


def _manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _sidepanel_js() -> str:
    return SIDEPANEL_JS.read_text(encoding="utf-8")


def _worker_js() -> str:
    return SERVICE_WORKER.read_text(encoding="utf-8")


def test_manifest_registers_mv3_service_worker():
    manifest = _manifest()

    assert manifest["manifest_version"] == 3
    assert manifest["background"] == {"service_worker": "service_worker.js"}
    assert "nativeMessaging" in manifest["permissions"]
    assert "sidePanel" in manifest["permissions"]


def test_sidepanel_uses_service_worker_message_passing_only():
    source = _sidepanel_js()

    assert "chrome.runtime.sendMessage({" in source
    assert "SERVICE_WORKER_NATIVE_BRIDGE_ACTION" in source
    assert "native_message: message" in source
    assert "chrome.runtime.sendNativeMessage" not in source
    assert "nativeBridgeLoadingResult()" in source
    assert "nativeBridgeRuntimeFailureResult" in source


def test_service_worker_owns_native_messaging_invocation():
    source = _worker_js()

    assert "chrome.runtime.onMessage.addListener" in source
    assert "chrome.runtime.sendNativeMessage(NATIVE_BRIDGE_HOST, nativeMessage" in source
    assert 'const NATIVE_BRIDGE_HOST = "com.sapianta.aigol_bridge";' in source
    assert 'const SERVICE_WORKER_NATIVE_BRIDGE_ACTION = "RUN_NATIVE_BRIDGE";' in source
    assert "return true;" in source


def test_service_worker_structured_runtime_errors_exist():
    source = _worker_js()

    for code in (
        "NATIVE_HOST_NOT_FOUND",
        "HOST_CRASHED",
        "INVALID_RESPONSE",
        "TIMEOUT",
        "MISSING_PERMISSIONS",
        "MALFORMED_RESULT",
    ):
        assert code in source
    assert "nativeBridgeRuntimeError" in source
    assert "classifyNativeRuntimeError" in source


def test_service_worker_validates_request_and_response_shapes():
    source = _worker_js()

    assert "validateNativeBridgeRequest" in source
    assert "validateNativeBridgeResponse" in source
    assert "operator_triggered must be true" in source
    assert "native_message is required" in source
    assert "accepted native bridge response is missing result_artifact" in source


def test_sidepanel_renders_loading_failure_and_success_states():
    source = _sidepanel_js()

    assert 'status: "RUNNING"' in source
    assert "Native bridge request sent to MV3 service worker." in source
    assert "runtime_failure_state: true" in source
    assert "renderNativeBridgeResponse(response.native_response)" in source
    assert "SERVICE_WORKER_NATIVE_BRIDGE_RETURNED" in source
    assert "NATIVE_BRIDGE_UNAVAILABLE" in source


def test_no_forbidden_runtime_transport_added():
    combined = SERVICE_WORKER.read_text(encoding="utf-8").lower()
    combined = combined.replace("localhost_server", "local-http-server-label")

    forbidden = (
        "fetch(",
        "xmlhttprequest",
        "websocket",
        "eventsource",
        "setinterval",
        "localhost",
        "httpserver",
        "serve_forever",
        "dispatchtask",
        "approvetask",
        "orchestrationruntime",
        "autonomouscontinuation",
        "localstorage",
        "sessionstorage",
        "indexeddb",
        "chrome.storage",
    )
    for token in forbidden:
        assert token not in combined


def test_authority_labels_preserved_in_worker_and_sidepanel():
    combined = "\n".join((SERVICE_WORKER.read_text(encoding="utf-8"), SIDEPANEL_JS.read_text(encoding="utf-8")))

    assert "NATIVE_BRIDGE_LOCAL_ONLY" in combined
    assert "OPERATOR_TRIGGERED" in combined
    assert "SERVICE_WORKER_RUNTIME_CONTROLLER" in combined
    assert "CANONICAL_PYTHON_RUNTIME" in combined
    assert "BOUNDED_CODEX_CLI_PROVIDER" in combined
    assert "NO_AUTONOMOUS_CONTINUATION" in combined
    assert "approval: false" in combined
    assert "orchestration: false" in combined
