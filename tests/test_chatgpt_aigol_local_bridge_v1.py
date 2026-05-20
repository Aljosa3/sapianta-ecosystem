from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT / "browser_companion"


def _html():
    return (COMPANION / "sidepanel.html").read_text()


def _js():
    return (COMPANION / "sidepanel.js").read_text()


def _combined():
    return "\n".join((_html(), _js()))


def test_local_bridge_section_exists():
    html = _html()

    assert "Local Bridge" in html
    assert 'id="local-bridge-status"' in html
    assert "Explicit ChatGPT to AiGOL local file handoff" in html
    assert "Operator-selected import only" in html


def test_bridge_mode_and_authority_labels_exist():
    html = _html()

    assert "BRIDGE MODE: LOCAL_FILE_HANDOFF" in html
    assert "BRIDGE AUTHORITY: SEMANTIC_TRANSPORT_ONLY" in html


def test_hash_certification_and_replay_labels_exist():
    html = _html()

    assert "INTEGRITY LABEL: HASH_VERIFIED_IS_INTEGRITY_ONLY" in html
    assert "CERTIFICATION LABEL: CERTIFIED_FOR_CONTINUITY_INGESTION_IS_NOT_APPROVAL" in html
    assert "REPLAY LABEL: SESSION_LOCAL_REPLAY_ONLY" in html


def test_valid_file_import_still_uses_hash_verified_continuity_path():
    source = _js()

    assert "function importSemanticProposalFileFromSidepanel()" in source
    assert "await file.text()" in source
    assert "await localSemanticProposalFileValidation(rawText, file.name)" in source
    assert "verifySemanticProposalArtifactHash(validation.proposal)" in source
    assert 'hashVerification.status !== "HASH_VERIFIED"' in source
    assert "runSemanticProposalContinuityFlow(validation)" in source
    assert "window.sidepanelRenderResult(result);" in source


def test_unsafe_proposals_still_rejected():
    source = _js()

    assert "validateSemanticProposalAuthority(proposal)" in source
    assert "implicit execution authority claim rejected" in source
    assert "provider execution claim rejected" in source
    assert "orchestration claim rejected" in source
    assert "continuation authority claim rejected" in source
    for mode in ("EXECUTE", "AUTO_EXECUTE", "AUTONOMOUS", "PROVIDER_RUNTIME", "ORCHESTRATION"):
        assert f'"{mode}"' in source


def test_no_new_transport_endpoints_or_background_listeners_are_introduced():
    lowered = _html().lower()

    forbidden = (
        "semantic-proposal-endpoint",
        "http://localhost",
        "http://127.0.0.1",
        "addeventlistener(\"message\"",
        "addeventlistener('message'",
        "runtime.onmessage",
        "tabs.onupdated",
        "webrequest",
        "websocket",
        "eventsource",
    )
    for token in forbidden:
        assert token not in lowered


def test_no_provider_dispatch_approval_execution_or_orchestration_behavior_is_added():
    lowered = _combined().lower().replace("codex dispatch", "codex-dispatch-claim")

    forbidden = (
        "provider.call",
        "dispatchtask",
        "approvetask",
        "executeprovider",
        "automaticexecution",
        "approvalautomation",
        "orchestrationruntime",
        "autonomouscontinuation",
        "setinterval",
        "settimeout",
    )
    for token in forbidden:
        assert token not in lowered
    assert "provider_calls: false" in _js()
    assert "dispatch: false" in _js()
    assert "approval: false" in _js()
    assert "execution: false" in _js()


def test_no_durable_persistence_is_introduced():
    lowered = _combined().lower()

    forbidden = (
        "localstorage",
        "sessionstorage",
        "indexeddb",
        "chrome.storage",
        "showdirectorypicker",
        "createwritestream",
        "writefile",
        "appendfile",
        "durable replay backend enabled",
    )
    for token in forbidden:
        assert token not in lowered
    assert "durable_storage: false" in _js()
    assert "hidden_persistence: false" in _js()
