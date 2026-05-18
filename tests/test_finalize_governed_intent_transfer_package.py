import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FINALIZE_MD = ROOT / ".github/governance/finalize/FINALIZE_GOVERNED_INTENT_TRANSFER_PACKAGE_V1.md"
FINALIZE_JSON = ROOT / ".github/governance/finalize/FINALIZE_GOVERNED_INTENT_TRANSFER_PACKAGE_V1.json"
EVIDENCE = ROOT / "runtime/finalization_evidence"
STATEMENT = "Governed intent transfer packages are non-executing and require explicit governance preview and confirmation."

JSON_FILES = [
    FINALIZE_JSON,
    EVIDENCE / "GOVERNED_INTENT_TRANSFER_PACKAGE_CERTIFICATION.json",
    EVIDENCE / "GOVERNED_INTENT_TRANSFER_PACKAGE_TOPOLOGY.json",
    EVIDENCE / "GOVERNED_INTENT_TRANSFER_PACKAGE_REPLAY_CERTIFICATION.json",
    EVIDENCE / "GOVERNED_INTENT_TRANSFER_PACKAGE_BOUNDARY_GUARANTEES.json",
    EVIDENCE / "GOVERNED_INTENT_TRANSFER_PACKAGE_CONTINUITY_REPORT.json",
    EVIDENCE / "GOVERNED_INTENT_TRANSFER_PACKAGE_NEXT_PHASE_BOUNDARY.json",
]


def _load(path):
    return json.loads(path.read_text())


def test_required_finalization_artifacts_exist_and_parse():
    assert FINALIZE_MD.exists()
    for path in JSON_FILES:
        assert path.exists()
        assert _load(path)


def test_certification_includes_required_transfer_components():
    finalize = _load(FINALIZE_JSON)
    for component in (
        "governed intent transfer package layer",
        "deterministic transfer identity",
        "replay identity continuity",
        "explicit preview requirement",
        "explicit confirmation requirement",
        "Browser Companion transfer export",
    ):
        assert component in finalize["included_components"]


def test_topology_declares_transfer_packages_inert():
    topology = _load(EVIDENCE / "GOVERNED_INTENT_TRANSFER_PACKAGE_TOPOLOGY.json")
    assert topology["roles"]["transfer_packages"] == "inert"
    assert topology["roles"]["transfer_packages_trigger_runtime_execution"] is False
    assert topology["roles"]["ingestion_implemented"] is False


def test_boundary_guarantees_preserve_preview_confirmation_and_no_auto_ingest():
    boundaries = _load(EVIDENCE / "GOVERNED_INTENT_TRANSFER_PACKAGE_BOUNDARY_GUARANTEES.json")
    assert boundaries["chatgpt_authority"] is False
    assert boundaries["execution_authority"] is False
    assert boundaries["requires_preview"] is True
    assert boundaries["requires_confirmation"] is True
    assert boundaries["automatic_transfer_ingestion"] is False
    assert boundaries["automatic_dispatch"] is False


def test_next_phase_boundary_references_governed_ingestion():
    boundary = _load(EVIDENCE / "GOVERNED_INTENT_TRANSFER_PACKAGE_NEXT_PHASE_BOUNDARY.json")
    assert boundary["next_phase"] == "GOVERNED_INTENT_TRANSFER_INGESTION_V1"
    assert boundary["ingestion_must_be_explicit"] is True
    assert boundary["ingestion_must_validate_transfer_identity"] is True
    assert boundary["ingestion_must_preserve_confirmation_requirement"] is True


def test_constitutional_statement_exists_exactly():
    assert STATEMENT in FINALIZE_MD.read_text()
    assert _load(EVIDENCE / "GOVERNED_INTENT_TRANSFER_PACKAGE_TOPOLOGY.json")["constitutional_statement"] == STATEMENT
    assert _load(EVIDENCE / "GOVERNED_INTENT_TRANSFER_PACKAGE_BOUNDARY_GUARANTEES.json")["constitutional_statement"] == STATEMENT
    assert _load(EVIDENCE / "GOVERNED_INTENT_TRANSFER_PACKAGE_REPLAY_CERTIFICATION.json")["constitutional_statement"] == STATEMENT
    assert _load(EVIDENCE / "GOVERNED_INTENT_TRANSFER_PACKAGE_NEXT_PHASE_BOUNDARY.json")["constitutional_statement"] == STATEMENT
