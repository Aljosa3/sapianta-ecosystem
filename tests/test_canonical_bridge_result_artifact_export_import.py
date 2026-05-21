from copy import deepcopy
from pathlib import Path

from agol_bridge.runtime.minimal_end_to_end_bridge import (
    BRIDGE_RESULT_ARTIFACT_AUTHORITY,
    BRIDGE_RESULT_ARTIFACT_SCHEMA_VERSION,
    BRIDGE_RESULT_ARTIFACT_TYPE,
    export_minimal_bridge_result_artifact,
    run_minimal_end_to_end_bridge,
)
from agol_bridge.transport.local_governed_transport import canonical_hash


ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT / "browser_companion"
RUNTIME = ROOT / "agol_bridge" / "runtime" / "minimal_end_to_end_bridge.py"


def _html() -> str:
    return (COMPANION / "sidepanel.html").read_text(encoding="utf-8")


def _js() -> str:
    return (COMPANION / "sidepanel.js").read_text(encoding="utf-8")


def _combined() -> str:
    return "\n".join((_html(), _js()))


def _bridge_result() -> dict:
    return run_minimal_end_to_end_bridge(
        human_request="Review canonical bridge result artifact export.",
        session_id="SESSION-CANONICAL-ARTIFACT-1",
    )


def _hash_input(artifact: dict) -> dict:
    artifact_copy = deepcopy(artifact)
    artifact_copy.pop("artifact_hash", None)
    return artifact_copy


def test_python_export_artifact_hash_is_deterministic():
    first = export_minimal_bridge_result_artifact(_bridge_result())
    second = export_minimal_bridge_result_artifact(_bridge_result())

    assert first == second
    assert first["artifact_hash"] == canonical_hash(_hash_input(first))
    assert first["artifact_hash"].startswith("sha256:")


def test_artifact_hash_excludes_itself():
    artifact = export_minimal_bridge_result_artifact(_bridge_result())
    changed_hash_only = deepcopy(artifact)
    changed_hash_only["artifact_hash"] = "sha256:" + ("0" * 64)

    assert canonical_hash(_hash_input(changed_hash_only)) == artifact["artifact_hash"]
    assert changed_hash_only["artifact_hash"] != artifact["artifact_hash"]


def test_exported_artifact_preserves_lifecycle_fields():
    result = _bridge_result()
    artifact = export_minimal_bridge_result_artifact(result)

    assert artifact["artifact_type"] == BRIDGE_RESULT_ARTIFACT_TYPE
    assert artifact["schema_version"] == BRIDGE_RESULT_ARTIFACT_SCHEMA_VERSION
    assert artifact["authority"] == BRIDGE_RESULT_ARTIFACT_AUTHORITY
    assert artifact["session_id"] == result["session_id"]
    assert artifact["proposal_id"] == result["proposal_id"]
    assert artifact["replay_events"] == result["replay_events"]
    assert artifact["task_package"] == result["task_package"]
    assert artifact["mock_codex_result"] == result["mock_codex_result"]
    assert artifact["result_validation"] == result["result_validation"]
    assert artifact["governed_chat_return"] == result["governed_chat_return"]


def test_sidepanel_import_ui_exists():
    html = _html()

    assert 'id="bridge-result-artifact-file"' in html
    assert "bridge_result_artifact.json" in html
    assert 'id="import-canonical-bridge-result"' in html
    assert "Import Canonical Bridge Result" in html
    assert 'id="canonical-bridge-result-artifact-status"' in html


def test_sidepanel_hash_mismatch_is_rejected():
    source = _js()

    assert "function verifyCanonicalBridgeResultArtifactHash" in source
    assert "canonicalBridgeResultArtifactHashInput" in source
    assert "canonical bridge result artifact_hash mismatch" in source
    assert "HASH_MISMATCH" in source
    assert "canonicalBridgeResultBlockedResult" in source


def test_canonical_artifact_labels_render():
    combined = _combined()

    assert "CANONICAL PYTHON RESULT ARTIFACT" in combined
    assert "NO REAL EXECUTION / MOCK CODEX ONLY" in combined
    assert "NON_EXECUTING_NON_AUTHORITATIVE" in combined
    assert "HASH VERIFIED IS INTEGRITY ONLY" in combined
    assert "CANONICAL IMPORT DOES NOT APPROVE, DISPATCH, EXECUTE, OR PERSIST" in combined


def test_sidepanel_import_is_operator_selected_only_without_endpoint_or_listener():
    lowered = _combined().lower()

    forbidden = (
        "fetch(",
        "xmlhttprequest",
        "websocket",
        "eventsource",
        "addeventlistener(\"message\"",
        "addeventlistener('message'",
        "runtime.onmessage",
        "tabs.onupdated",
        "webrequest",
        "threadinghttpserver",
        "httpserver",
        "serviceworker",
        "localstorage",
        "sessionstorage",
        "indexeddb",
        "chrome.storage",
    )
    for token in forbidden:
        assert token not in lowered
    assert "await file.text()" in _js()
    assert "importCanonicalBridgeResultButton.onclick = importCanonicalBridgeResultFromSidepanel;" in _js()


def test_no_provider_dispatch_approval_execution_or_orchestration_is_introduced():
    lowered = "\n".join((_js(), RUNTIME.read_text(encoding="utf-8"))).lower()

    forbidden = (
        "provider.call",
        "dispatchtask",
        "approvetask",
        "executeprovider",
        "orchestrationruntime",
        "autonomouscontinuation",
        "subprocess",
        "socket",
        "requests.",
        "urllib",
        "open(",
    )
    for token in forbidden:
        assert token not in lowered
    assert "provider_calls: false" in _js()
    assert "dispatch: false" in _js()
    assert "approval: false" in _js()
    assert "execution: false" in _js()
    assert "orchestration: false" in _js()
