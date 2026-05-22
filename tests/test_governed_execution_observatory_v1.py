from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT / "browser_companion"
REPORT = ROOT / "GOVERNED_EXECUTION_OBSERVATORY_V1.md"


def _html() -> str:
    return (COMPANION / "sidepanel.html").read_text(encoding="utf-8")


def _js() -> str:
    return (COMPANION / "sidepanel.js").read_text(encoding="utf-8")


def _combined() -> str:
    return "\n".join((_html(), _js()))


def test_observatory_sections_exist():
    html = _html()

    assert 'id="governed-execution-observatory"' in html
    for section_id in (
        "observatory-topology",
        "observatory-classification-legend",
        "observatory-human-request",
        "observatory-semantic-reasoning",
        "observatory-semantic-contract",
        "observatory-semantic-contract-json",
        "observatory-aigol-governance",
        "observatory-task-package",
        "observatory-task-package-json",
        "observatory-codex-execution",
        "observatory-post-verification",
        "observatory-governed-return",
    ):
        assert f'id="{section_id}"' in html


def test_each_layer_exposes_input_output_authority_boundary_status():
    source = _js()

    for function_name in (
        "observatoryHumanRequestSummary",
        "observatorySemanticReasoningSummary",
        "observatorySemanticContractSummary",
        "observatoryAigolGovernanceSummary",
        "observatoryTaskPackageSummary",
        "observatoryCodexExecutionSummary",
        "observatoryPostExecutionVerificationSummary",
        "observatoryGovernedReturnSummary",
    ):
        start = source.index(f"function {function_name}")
        body = source[start : source.index("\n}", start) + 2]
        for label in ("INPUT:", "OUTPUT:", "AUTHORITY:", "BOUNDARY:", "STATUS:"):
            assert label in body


def test_authority_classification_labels_are_visible():
    combined = _combined()

    assert "ENFORCED" in combined
    assert "STRUCTURAL_ONLY" in combined
    assert "ADVISORY_ONLY" in combined
    assert "UI_ONLY" in combined
    assert "REAL ENFORCEMENT" in combined
    assert "DESCRIPTIVE" in combined


def test_semantic_layer_is_honest_about_local_normalization():
    combined = _combined()

    assert "LOCAL DETERMINISTIC NORMALIZATION" in combined
    assert "NON-AUTHORITATIVE" in combined
    assert "SEMANTIC ONLY" in combined
    assert "not live ChatGPT cognition" in combined


def test_task_package_card_shows_what_codex_receives():
    combined = _combined()

    assert "WHAT CODEX ACTUALLY RECEIVES" in combined
    assert "codex_prompt" in combined
    assert "allowed_paths" in combined
    assert "forbidden_operations" in combined
    assert "canonical_artifact_hash" in combined
    assert "provenance" in combined


def test_semantic_contract_card_renders_contract_labels():
    combined = _combined()

    assert "STRUCTURED_SEMANTIC_CONTRACT" in combined
    assert "NON_EXECUTION_AUTHORITY" in combined
    assert "GOVERNANCE_MEDIATED" in combined
    assert "REPLAYABLE_SEMANTIC_CONTRACT" in combined
    assert "observatorySemanticContractSummary" in combined
    assert "observatorySemanticContractJson" in combined


def test_codex_execution_layer_distinguishes_real_and_mock():
    combined = _combined()

    assert "REAL_CODEX_EXECUTION" in combined
    assert "MOCK_EXECUTION" in combined
    assert "NOT_STARTED" in combined
    assert "observatoryExecutionMode" in combined


def test_post_execution_verification_marks_structural_only():
    combined = _combined()

    assert "STRUCTURAL VERIFICATION ONLY" in combined
    assert "semantic correctness is not verified" in combined
    assert "lineage_verification" in combined
    assert "forbidden_authority_flag_detection" in combined


def test_governed_return_not_live_chatgpt_interpretation():
    combined = _combined()

    assert "GOVERNED OPERATOR RETURN" in combined
    assert "NOT LIVE CHATGPT INTERPRETATION" in combined


def test_rendering_wires_observatory_cards_deterministically():
    source = _js()

    assert "setCockpitText(COCKPIT_IDS.observatoryTopology, observatoryTopologySummary(latest));" in source
    assert "setCockpitText(COCKPIT_IDS.observatoryHumanRequest, observatoryHumanRequestSummary(latest));" in source
    assert "setCockpitText(COCKPIT_IDS.observatoryTaskPackageJson, artifactJson(observatoryTaskPackage(latest)));" in source
    assert "Date.now" not in source
    assert "Math.random" not in source
    assert "crypto.randomUUID" not in source
    assert "innerHTML" not in source


def test_no_runtime_architecture_added():
    lowered = _combined().lower().replace("codex dispatch", "codex-dispatch-claim")

    forbidden = (
        "fetch(",
        "xmlhttprequest",
        "websocket",
        "eventsource",
        "setinterval",
        "provider.call",
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
        assert token not in lowered


def test_observatory_document_describes_real_vs_descriptive_governance():
    report = REPORT.read_text(encoding="utf-8")

    assert "GOVERNED_EXECUTION_OBSERVATORY_V1" in report
    assert "Real vs Descriptive Governance" in report
    assert "ENFORCED" in report
    assert "STRUCTURAL_ONLY" in report
    assert "ADVISORY_ONLY" in report
    assert "UI_ONLY" in report
