from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT / "browser_companion"
HTML = COMPANION / "sidepanel.html"
JS = COMPANION / "sidepanel.js"
DOC = ROOT / "CHATGPT_INGRESS_TO_SEMANTIC_CONTRACT_PREVIEW_V1.md"


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


def test_preview_renders_ingress_artifact_card():
    combined = _combined()

    assert 'id="chatgpt-ingress-artifact-preview-card"' in combined
    assert "CHATGPT_INGRESS_ARTIFACT_V1" in combined


def test_preview_renders_import_validation_card():
    combined = _combined()

    assert 'id="chatgpt-ingress-import-validation-card"' in combined
    assert "Import Validation" in combined


def test_preview_renders_proposal_candidate_card():
    combined = _combined()

    assert 'id="chatgpt-ingress-proposal-candidate-card"' in combined
    assert "Semantic Proposal Candidate" in combined
    assert "proposal_candidate_only: true" in combined


def test_preview_renders_contract_candidate_card():
    combined = _combined()

    assert 'id="chatgpt-ingress-contract-candidate-card"' in combined
    assert "Semantic Contract Candidate" in combined
    assert "contract_candidate_only: true" in combined


def test_preview_renders_governance_report_card():
    combined = _combined()

    assert 'id="chatgpt-ingress-governance-report-card"' in combined
    assert "Governance Acceptance Report" in combined


def test_preview_explicitly_displays_structural_or_advisory_only():
    section = _preview_section()

    assert "STRUCTURAL_ONLY" in section
    assert "ADVISORY_ONLY" in section
    assert "REAL_CODEX_EXECUTION" not in section


def test_preview_explicitly_states_execution_not_performed():
    assert "execution_performed: false" in _preview_section()
    assert '"execution_performed: false"' in _js()


def test_preview_explicitly_states_codex_dispatch_not_performed():
    assert "codex_dispatch_performed: false" in _preview_section()
    assert '"codex_dispatch_performed: false"' in _js()


def test_preview_contains_no_execution_button():
    section = _preview_section().lower()
    button_start = section.index('id="preview-chatgpt-ingress-import-only"')
    button_fragment = section[button_start - 80 : button_start + 160]

    assert "preview import only" in section
    assert "run via native bridge" not in section
    assert "run governed codex execution" not in section
    assert "run" not in button_fragment
    assert "execute" not in button_fragment
    assert "dispatch" not in button_fragment


def test_preview_path_never_invokes_native_messaging():
    source = _js()
    start = source.index("function chatgptIngressPreviewArtifact")
    end = source.index("function replaySummaryArtifact", start)
    preview_source = source[start:end]

    assert "sendNativeMessage" not in preview_source
    assert "RUN_NATIVE_BRIDGE" not in preview_source
    assert "runNativeBridgeFromSidepanel" not in preview_source


def test_preview_path_never_invokes_codex_provider():
    source = _js()
    start = source.index("function chatgptIngressPreviewArtifact")
    end = source.index("function replaySummaryArtifact", start)
    preview_source = source[start:end].lower()

    assert "run_bounded_codex_cli_task(" not in preview_source
    assert "codex_cli_provider(" not in preview_source
    assert "codex exec" not in preview_source
    assert "provider_dispatch_authorized: false" in preview_source


def test_preview_preserves_replay_identity_visibility():
    combined = _combined()

    assert "replay_identity:" in combined
    assert "CHATGPT-INGRESS-PREVIEW-REPLAY" in combined


def test_preview_preserves_hash_visibility():
    combined = _combined()

    for token in (
        "ingress_artifact_hash:",
        "proposal_candidate_hash:",
        "contract_candidate_hash:",
        "governance_report_hash:",
    ):
        assert token in combined


def test_preview_remains_isolated_from_canonical_runtime_flow():
    html = _html()
    preview_start = html.index('id="chatgpt-ingress-preview"')
    observatory_start = html.index('id="governed-execution-observatory"')
    core_start = html.index('id="core-flow-controls"')

    assert core_start < preview_start < observatory_start
    assert "This preview is isolated from Native Messaging, Codex, governed task packages, and canonical execution runtime." in html


def test_preview_remains_import_only():
    combined = _combined()

    assert "ChatGPT Ingress Preview (Import-Only)" in combined
    assert "IMPORT_ONLY: true" in combined
    assert "runtime_boundary: no Native Messaging, no service worker execution path, no Python runtime execution, no Codex provider" in combined


def test_preview_document_exists_and_preserves_non_execution_scope():
    doc = DOC.read_text(encoding="utf-8")

    assert "CHATGPT_INGRESS_TO_SEMANTIC_CONTRACT_PREVIEW_V1" in doc
    assert "preview-only" in doc.lower()
    assert "not execution" in doc.lower()
