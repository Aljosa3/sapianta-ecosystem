from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT / "browser_companion"
HTML = COMPANION / "sidepanel.html"
JS = COMPANION / "sidepanel.js"
DOC = ROOT / "CHATGPT_INGRESS_NATIVE_IMPORT_PREVIEW_V1.md"


def _html() -> str:
    return HTML.read_text(encoding="utf-8")


def _js() -> str:
    return JS.read_text(encoding="utf-8")


def _combined() -> str:
    return "\n".join((_html(), _js()))


def _preview_section() -> str:
    html = _html()
    start = html.index('id="chatgpt-ingress-preview"')
    end = html.index('id="governed-execution-observatory"', start)
    return html[start:end]


def _preview_source() -> str:
    source = _js()
    start = source.index("function chatgptIngressPreviewArtifact")
    end = source.index("function executeControlledHandoffFromSidepanel", start)
    return source[start:end]


def test_sidepanel_contains_chatgpt_ingress_json_import_control():
    section = _preview_section()

    assert 'id="chatgpt-ingress-artifact-json"' in section
    assert "Paste CHATGPT_INGRESS_ARTIFACT_V1 JSON" in section


def test_import_button_is_preview_import_only_not_run_execute():
    section = _preview_section()

    assert 'id="preview-chatgpt-ingress-import-only"' in section
    assert "Preview Import Only" in section
    button_fragment = section[section.index('id="preview-chatgpt-ingress-import-only"') - 80 : section.index('id="preview-chatgpt-ingress-import-only"') + 160].lower()
    assert "run" not in button_fragment
    assert "execute" not in button_fragment
    assert "dispatch" not in button_fragment
    assert "authorize" not in button_fragment


def test_sidepanel_contains_no_codex_dispatch_in_import_preview_path():
    preview_source = _preview_source().lower()

    assert "send to codex" not in preview_source
    assert "dispatch to codex" in preview_source
    assert "codex_dispatch_performed: false" in preview_source
    assert "codex_dispatch_allowed: false" in preview_source


def test_preview_section_displays_import_preview_non_executing():
    section = _preview_section()

    assert "IMPORT ONLY" in section
    assert "PREVIEW ONLY" in section
    assert "NON-EXECUTING" in section


def test_preview_displays_execution_performed_false():
    assert "execution_performed: false" in _combined()
    assert "execution performed: false" in _preview_section()


def test_preview_displays_codex_dispatch_performed_false():
    assert "codex_dispatch_performed: false" in _combined()
    assert "Codex dispatch: false" in _preview_section()


def test_preview_displays_governance_approved_false():
    assert "governance_approved: false" in _combined()
    assert "governance approved: false" in _preview_section()


def test_preview_displays_semantic_correctness_verified_false():
    assert "semantic_correctness_verified: false" in _combined()
    assert "semantic correctness verified: false" in _preview_section()


def test_preview_renders_accepted_import_status():
    assert "ACCEPTED_FOR_STRUCTURAL_IMPORT" in _js()


def test_preview_renders_rejected_import_status():
    assert "REJECTED" in _js()
    assert "rejection_reason:" in _js()


def test_preview_renders_invalid_json_rejection():
    source = _js()

    assert "INVALID_JSON" in source
    assert "renderChatgptIngressInvalidJsonPreview" in source


def test_preview_renders_replay_identity():
    assert "replay_identity:" in _combined()


def test_preview_renders_ingress_artifact_hash():
    assert "ingress_artifact_hash:" in _combined()


def test_preview_renders_proposal_candidate_hash():
    assert "proposal_candidate_hash:" in _combined()


def test_preview_renders_contract_candidate_hash():
    assert "contract_candidate_hash:" in _combined()


def test_preview_renders_governance_report_hash():
    assert "governance_report_hash:" in _combined()


def test_preview_stop_state_is_visible():
    assert "STOP (No Execution)" in _preview_section()
    assert "STOP: No Execution" in _preview_section()


def test_preview_remains_isolated_from_canonical_native_messaging_runtime():
    section = _preview_section()
    source = _preview_source()

    assert "This preview is isolated from Native Messaging" in section
    assert "sendNativeMessage" not in source
    assert "RUN_NATIVE_BRIDGE" not in source
    assert "runNativeBridgeFromSidepanel" not in source


def test_no_execution_button_exists_in_preview_section():
    section = _preview_section().lower()
    button_start = section.index('id="preview-chatgpt-ingress-import-only"')
    button_text = section[button_start - 120 : button_start + 180]

    assert "preview import only" in button_text
    assert "run" not in button_text
    assert "execute" not in button_text
    assert "dispatch" not in button_text


def test_no_native_messaging_call_is_wired_to_preview_button():
    source = _js()
    assert "previewChatgptIngressImportOnlyButton.onclick = previewImportedChatgptIngressArtifactFromSidepanel;" in source
    preview_source = _preview_source()

    assert "chrome.runtime.sendMessage(" not in preview_source
    assert "chrome.runtime.sendNativeMessage(" not in preview_source


def test_documentation_exists_for_native_import_preview():
    doc = DOC.read_text(encoding="utf-8")

    assert "CHATGPT_INGRESS_NATIVE_IMPORT_PREVIEW_V1" in doc
    assert "import-only" in doc.lower()
    assert "Codex is not dispatched" in doc
