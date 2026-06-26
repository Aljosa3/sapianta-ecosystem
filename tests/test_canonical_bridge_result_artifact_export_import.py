from copy import deepcopy
from pathlib import Path

import agol_bridge.runtime.minimal_end_to_end_bridge as bridge_runtime
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


def _bridge_result(monkeypatch, tmp_path) -> dict:
    def fake_provider(*, task_package, workspace_path, timeout_seconds=600):
        return {
            "provider": "CODEX_CLI",
            "status": "COMPLETED",
            "stdout": "bounded codex complete",
            "stderr": "",
            "returncode": 0,
            "workspace_path": str(Path(workspace_path).resolve()),
            "task_package_id": task_package["task_id"],
            "non_authority_guarantees": ["NO_AUTO_APPROVAL", "NO_AUTO_CONTINUATION", "NO_SILENT_RETRY"],
            "execution_boundary": {"auto_continue": False, "silent_retry": False, "orchestration": False},
            "errors": [],
            "command": ["codex", "exec", "<bounded_prompt>"],
            "bounded_prompt_hash": "sha256:bounded",
            "retry_count": 0,
        }

    monkeypatch.setattr(bridge_runtime, "run_bounded_codex_cli_task", fake_provider)
    return run_minimal_end_to_end_bridge(
        human_request="Review canonical bridge result artifact export.",
        session_id="SESSION-CANONICAL-ARTIFACT-1",
        workspace_path=str(tmp_path),
    )


def _hash_input(artifact: dict) -> dict:
    artifact_copy = deepcopy(artifact)
    artifact_copy.pop("artifact_hash", None)
    return artifact_copy


def test_python_export_artifact_hash_is_deterministic(monkeypatch, tmp_path):
    first = export_minimal_bridge_result_artifact(_bridge_result(monkeypatch, tmp_path))
    second = export_minimal_bridge_result_artifact(_bridge_result(monkeypatch, tmp_path))

    assert first == second
    assert first["artifact_hash"] == canonical_hash(_hash_input(first))
    assert first["artifact_hash"].startswith("sha256:")


def test_artifact_hash_excludes_itself(monkeypatch, tmp_path):
    artifact = export_minimal_bridge_result_artifact(_bridge_result(monkeypatch, tmp_path))
    changed_hash_only = deepcopy(artifact)
    changed_hash_only["artifact_hash"] = "sha256:" + ("0" * 64)

    assert canonical_hash(_hash_input(changed_hash_only)) == artifact["artifact_hash"]
    assert changed_hash_only["artifact_hash"] != artifact["artifact_hash"]


def test_exported_artifact_preserves_lifecycle_fields(monkeypatch, tmp_path):
    result = _bridge_result(monkeypatch, tmp_path)
    artifact = export_minimal_bridge_result_artifact(result)

    assert artifact["artifact_type"] == BRIDGE_RESULT_ARTIFACT_TYPE
    assert artifact["schema_version"] == BRIDGE_RESULT_ARTIFACT_SCHEMA_VERSION
    assert artifact["authority"] == BRIDGE_RESULT_ARTIFACT_AUTHORITY
    assert artifact["session_id"] == result["session_id"]
    assert artifact["proposal_id"] == result["proposal_id"]
    assert artifact["replay_events"] == result["replay_events"]
    assert artifact["task_package"] == result["task_package"]
    assert artifact["codex_cli_result"] == result["codex_cli_result"]
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
    assert "REAL CODEX EXECUTION / BOUNDED CODEX CLI ONLY" in combined
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
        "localstorage",
        "sessionstorage",
        "indexeddb",
        "chrome.storage",
    )
    for token in forbidden:
        assert token not in lowered
    assert "serviceworker.register" not in lowered
    assert "navigator.serviceworker" not in lowered
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
        "socket",
        "requests.",
        "urllib",
        "open(",
    )
    for token in forbidden:
        assert token not in lowered
    assert "provider_calls: \"CODEX_CLI_ONLY\"" in _js()
    assert "dispatch: false" in _js()
    assert "approval: false" in _js()
    assert "execution: \"BOUNDED_CODEX_CLI_ONLY\"" in _js()
    assert "orchestration: false" in _js()
