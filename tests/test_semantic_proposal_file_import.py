from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT / "browser_companion"


def _html():
    return (COMPANION / "sidepanel.html").read_text()


def _js():
    return (COMPANION / "sidepanel.js").read_text()


def _combined():
    return "\n".join((_html(), _js()))


def test_semantic_proposal_file_input_and_button_exist():
    html = _html()

    assert 'id="semantic-proposal-file"' in html
    assert 'type="file"' in html
    assert 'accept="application/json,.json"' in html
    assert 'id="import-semantic-proposal-file"' in html
    assert "Import semantic_proposal.json" in html


def test_valid_semantic_proposal_file_uses_existing_continuity_path():
    source = _js()

    assert "function localSemanticProposalFileValidation(rawText, fileName)" in source
    assert "validateSemanticProposal(rawText)" in source
    assert 'fileName !== "semantic_proposal.json"' in source
    assert "function importSemanticProposalFileFromSidepanel()" in source
    assert "await file.text()" in source
    assert "runSemanticProposalContinuityFlow(validation)" in source
    assert "window.sidepanelRenderResult(result);" in source
    assert "importSemanticProposalFileButton.onclick = importSemanticProposalFileFromSidepanel;" in source


def test_invalid_json_missing_fields_and_unsafe_modes_are_rejected():
    source = _js()

    assert 'return { errors: ["invalid JSON"] };' in source
    assert "missing required field" in source
    assert "unsupported proposed_mode" in source
    assert "rejected proposed_mode" in source
    for mode in ("EXECUTE", "AUTO_EXECUTE", "AUTONOMOUS", "PROVIDER_RUNTIME", "ORCHESTRATION"):
        assert f'"{mode}"' in source


def test_execution_provider_orchestration_claims_are_rejected_for_file_import():
    source = _js()

    assert "implicit execution authority claim rejected" in source
    assert "provider execution claim rejected" in source
    assert "orchestration claim rejected" in source
    assert "continuation authority claim rejected" in source
    assert "validateSemanticProposalAuthority(proposal)" in source
    assert "localSemanticProposalFileValidation(rawText, fileName)" in source


def test_file_contents_are_not_persisted_or_written():
    lowered = _combined().lower()

    assert "file_persisted: false" in _js()
    assert "durable_storage: false" in _js()
    assert "hidden_persistence: false" in _js()
    forbidden = (
        "localstorage",
        "sessionstorage",
        "indexeddb",
        "chrome.storage",
        "filesystem",
        "showdirectorypicker",
        "createwritestream",
        "writefile",
        "appendfile",
    )
    for token in forbidden:
        assert token not in lowered


def test_no_provider_dispatch_approval_or_execution_path_is_added():
    lowered = _combined().lower()

    forbidden = (
        "fetch(",
        "xmlhttprequest",
        "websocket",
        "provider.call",
        "dispatchtask",
        "approvetask",
        "executeprovider",
        "setinterval",
        "settimeout",
    )
    for token in forbidden:
        assert token not in lowered
    assert "provider_calls: false" in _js()
    assert "dispatch: false" in _js()
    assert "approval: false" in _js()
    assert "execution: false" in _js()


def test_file_import_rendering_is_deterministic_and_safe():
    source = _js()

    assert "deterministicId(\"SEMANTIC-PROPOSAL\", proposal)" in source
    assert "canonicalize({" in source
    assert "artifactJson(semanticProposalArtifact(latest))" in source
    assert "semanticProposalValidationSummary(latest)" in source
    assert "node.textContent = value;" in source
    assert "innerHTML" not in source
    assert "Date.now" not in source
    assert "Math.random" not in source
    assert "crypto.randomUUID" not in source


def test_file_import_does_not_add_replay_or_lifecycle_mutation_path():
    source = _js()

    forbidden = (
        "appendReplay",
        "append_replay",
        "mutateReplay",
        "rewriteReplay",
        "repairReplay",
        "transitionLifecycle",
        "transition_lifecycle",
        "createLifecycleTransition",
        "autonomousContinuation",
        "hiddenPersistence",
    )
    for token in forbidden:
        assert token not in source
    assert "lifecycle_mutation: false" in source
    assert "replay_mutation: false" in source
