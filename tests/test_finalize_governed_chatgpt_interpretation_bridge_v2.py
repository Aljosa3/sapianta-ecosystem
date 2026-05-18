import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FINALIZE_MD = ROOT / ".github/governance/finalize/FINALIZE_GOVERNED_CHATGPT_INTERPRETATION_BRIDGE_V2.md"
FINALIZE_JSON = ROOT / ".github/governance/finalize/FINALIZE_GOVERNED_CHATGPT_INTERPRETATION_BRIDGE_V2.json"
EVIDENCE = ROOT / "runtime/finalization_evidence"
STATEMENT = "ChatGPT reasoning is non-authoritative and cannot directly trigger execution."

JSON_FILES = [
    FINALIZE_JSON,
    EVIDENCE / "GOVERNED_CHATGPT_BRIDGE_V2_CERTIFICATION.json",
    EVIDENCE / "GOVERNED_CHATGPT_BRIDGE_V2_TOPOLOGY.json",
    EVIDENCE / "GOVERNED_CHATGPT_BRIDGE_V2_REPLAY_CERTIFICATION.json",
    EVIDENCE / "GOVERNED_CHATGPT_BRIDGE_V2_BOUNDARY_GUARANTEES.json",
    EVIDENCE / "GOVERNED_CHATGPT_BRIDGE_V2_CONTINUITY_REPORT.json",
    EVIDENCE / "GOVERNED_CHATGPT_BRIDGE_V2_NEXT_PHASE_BOUNDARY.json",
]


def _load(path):
    return json.loads(path.read_text())


def test_required_finalization_artifacts_exist_and_parse():
    assert FINALIZE_MD.exists()
    for path in JSON_FILES:
        assert path.exists()
        assert _load(path)


def test_certification_includes_required_bridge_components():
    finalize = _load(FINALIZE_JSON)
    for component in (
        "ChatGPT-style conversational input normalization",
        "bounded conversational request mapping",
        "replay identity generation",
        "browser companion conversational mode",
        "explicit confirmation preservation",
        "exact-match bounded vocabulary",
    ):
        assert component in finalize["included_components"]


def test_topology_declares_chatgpt_non_authoritative():
    topology = _load(EVIDENCE / "GOVERNED_CHATGPT_BRIDGE_V2_TOPOLOGY.json")
    assert topology["roles"]["chatgpt"] == "reasoning and decomposition surface only"
    assert topology["roles"]["aigol"] == "governance authority"
    assert topology["roles"]["chatgpt_can_issue_authority_tokens"] is False
    assert topology["roles"]["chatgpt_can_dispatch_codex"] is False


def test_boundary_guarantees_exclude_transfer_scraping_and_dispatch():
    boundaries = _load(EVIDENCE / "GOVERNED_CHATGPT_BRIDGE_V2_BOUNDARY_GUARANTEES.json")
    assert boundaries["chatgpt_authority"] is False
    assert boundaries["execution_authority"] is False
    assert boundaries["automatic_chatgpt_to_runtime_transfer"] is False
    assert boundaries["hidden_page_reading"] is False
    assert boundaries["full_conversation_scraping"] is False
    assert boundaries["direct_codex_dispatch"] is False


def test_next_phase_boundary_requires_explicit_intent_transfer():
    boundary = _load(EVIDENCE / "GOVERNED_CHATGPT_BRIDGE_V2_NEXT_PHASE_BOUNDARY.json")
    assert boundary["next_phase"] == "GOVERNED_INTENT_TRANSFER_PACKAGE_V1"
    assert boundary["future_intent_transfer_must_be_explicit"] is True
    assert boundary["hidden_chatgpt_page_scraping_allowed"] is False
    assert boundary["user_confirmation_remains_mandatory"] is True


def test_constitutional_statement_exists_exactly():
    assert STATEMENT in FINALIZE_MD.read_text()
    assert _load(EVIDENCE / "GOVERNED_CHATGPT_BRIDGE_V2_TOPOLOGY.json")["constitutional_statement"] == STATEMENT
    assert _load(EVIDENCE / "GOVERNED_CHATGPT_BRIDGE_V2_BOUNDARY_GUARANTEES.json")["constitutional_statement"] == STATEMENT
    assert _load(EVIDENCE / "GOVERNED_CHATGPT_BRIDGE_V2_REPLAY_CERTIFICATION.json")["constitutional_statement"] == STATEMENT
    assert _load(EVIDENCE / "GOVERNED_CHATGPT_BRIDGE_V2_NEXT_PHASE_BOUNDARY.json")["constitutional_statement"] == STATEMENT
