from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT / "browser_companion"


def _html():
    return (COMPANION / "sidepanel.html").read_text()


def _js():
    return (COMPANION / "sidepanel.js").read_text()


def _combined():
    return "\n".join((_html(), _js()))


def test_semantic_proposal_import_ui_exists():
    html = _html()

    assert "ChatGPT Semantic Proposal" in html
    assert 'id="chatgpt-semantic-proposal"' in html
    assert 'id="import-semantic-proposal"' in html
    assert "Import Semantic Proposal" in html
    assert "Semantic Proposal Validation Status" in html
    assert 'id="semantic-proposal-validation-status"' in html
    assert "Semantic Proposal Artifact" in html
    assert 'id="semantic-proposal-artifact"' in html


def test_required_fields_and_allowed_modes_are_declared():
    source = _js()

    for field in (
        "human_request",
        "semantic_intent",
        "proposed_mode",
        "risk_class",
        "authority_boundary_statement",
        "semantic_boundary_statement",
        "requested_action_type",
    ):
        assert f'"{field}"' in source
    for mode in ("READ_ONLY", "REVIEW_ONLY", "DEMO_ONLY"):
        assert f'"{mode}"' in source


def test_forbidden_modes_are_rejected():
    source = _js()

    for mode in ("EXECUTE", "AUTO_EXECUTE", "AUTONOMOUS", "PROVIDER_RUNTIME", "ORCHESTRATION"):
        assert f'"{mode}"' in source
    assert "REJECTED_SEMANTIC_PROPOSAL_MODES.includes(mode)" in source
    assert "rejected proposed_mode" in source
    assert "unsupported proposed_mode" in source


def test_invalid_json_and_missing_fields_are_rejected():
    source = _js()

    assert "function parseSemanticProposal(rawText)" in source
    assert "JSON.parse(rawText)" in source
    assert 'return { errors: ["invalid JSON"] };' in source
    assert "function validateSemanticProposalShape(proposal)" in source
    assert "missing required field" in source
    assert 'status: "REJECTED"' in source


def test_execution_provider_orchestration_and_continuation_claims_are_rejected():
    source = _js()

    assert "implicit execution authority claim rejected" in source
    assert "provider execution claim rejected" in source
    assert "orchestration claim rejected" in source
    assert "continuation authority claim rejected" in source
    assert "containsClaim(claimText, \"execute\"" in source
    assert "containsClaim(claimText, \"provider\"" in source
    assert "containsClaim(claimText, \"orchestration\"" in source
    assert "containsClaim(claimText, \"autonomous\"" in source


def test_valid_proposal_runs_governed_continuity_flow_without_new_backend_path():
    source = _js()

    assert "function importSemanticProposalFromSidepanel()" in source
    assert "function runSemanticProposalContinuityFlow(validation)" in source
    assert "validateSemanticProposal(proposalInput ? proposalInput.value : \"\")" in source
    assert "runMinimalGovernedOperationalLoopDemo(proposal.human_request)" in source
    assert 'result.demo_id = "CHATGPT_SEMANTIC_PROPOSAL_IMPORT_V1";' in source
    assert "window.sidepanelRenderResult(result);" in source
    assert "importSemanticProposalButton.onclick = importSemanticProposalFromSidepanel;" in source


def test_semantic_proposal_rendering_is_deterministic_and_read_only():
    source = _js()

    assert "deterministicId(\"SEMANTIC-PROPOSAL\", proposal)" in source
    assert "artifactJson(semanticProposalArtifact(latest))" in source
    assert "semanticProposalValidationSummary(latest)" in source
    assert "node.textContent = value;" in source
    assert "innerHTML" not in source
    assert "Date.now" not in source
    assert "Math.random" not in source
    assert "crypto.randomUUID" not in source


def test_import_renders_required_proposal_fields_in_cockpit():
    source = _js()

    assert "proposal.human_request || request.request_text" in source
    assert "`semantic_intent: ${compactValue(proposal.semantic_intent)}`" in source
    assert "`proposed_mode: ${compactValue(proposal.proposed_mode)}`" in source
    assert "`risk_class: ${compactValue(proposal.risk_class)}`" in source
    assert "proposal.semantic_boundary_statement" in source
    assert "proposal.authority_boundary_statement" in source
    assert "continuity_findings" in source
    assert "replay_visibility_summary" in source
    assert "lifecycle_visibility_summary" in source
    assert "lineage_summary" in source


def test_semantic_proposal_import_adds_no_provider_dispatch_approval_execution_or_persistence():
    lowered = _combined().lower()
    forbidden = (
        "fetch(",
        "xmlhttprequest",
        "chrome.storage",
        "localstorage",
        "sessionstorage",
        "indexeddb",
        "provider.call",
        "dispatchtask",
        "approvetask",
        "executeprovider",
        "setinterval",
        "settimeout",
        "websocket",
    )

    for token in forbidden:
        assert token not in lowered


def test_semantic_proposal_import_adds_no_replay_or_lifecycle_mutation_path():
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
    assert "persistence: false" in source
    assert "hidden_authority: false" in source
