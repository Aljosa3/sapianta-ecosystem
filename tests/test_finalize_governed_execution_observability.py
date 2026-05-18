import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FINALIZE_MD = ROOT / ".github/governance/finalize/FINALIZE_GOVERNED_EXECUTION_OBSERVABILITY_V1.md"
FINALIZE_JSON = ROOT / ".github/governance/finalize/FINALIZE_GOVERNED_EXECUTION_OBSERVABILITY_V1.json"
EVIDENCE = ROOT / "runtime/finalization_evidence"
STATEMENT = "Governed execution observability is read-only and does not trigger execution."

JSON_FILES = [
    FINALIZE_JSON,
    EVIDENCE / "GOVERNED_EXECUTION_OBSERVABILITY_CERTIFICATION.json",
    EVIDENCE / "GOVERNED_EXECUTION_OBSERVABILITY_TOPOLOGY.json",
    EVIDENCE / "GOVERNED_EXECUTION_OBSERVABILITY_REPLAY_CERTIFICATION.json",
    EVIDENCE / "GOVERNED_EXECUTION_OBSERVABILITY_BOUNDARY_GUARANTEES.json",
    EVIDENCE / "GOVERNED_EXECUTION_OBSERVABILITY_CONTINUITY_REPORT.json",
    EVIDENCE / "GOVERNED_EXECUTION_OBSERVABILITY_NEXT_PHASE_BOUNDARY.json",
]


def _load(path):
    return json.loads(path.read_text())


def test_required_finalization_artifacts_exist_and_parse():
    assert FINALIZE_MD.exists()
    for path in JSON_FILES:
        assert path.exists()
        assert _load(path)


def test_certification_includes_required_observability_components():
    finalize = _load(FINALIZE_JSON)
    for component in (
        "Browser Companion execution inspection",
        "Local Preview Runtime observability endpoint",
        "Execution Observability Layer",
        "Execution trace generation",
        "Execution timeline generation",
        "read-only observability response",
    ):
        assert component in finalize["included_components"]


def test_topology_declares_read_only_observability():
    topology = _load(EVIDENCE / "GOVERNED_EXECUTION_OBSERVABILITY_TOPOLOGY.json")
    assert "Read-only Execution Observability" in topology["topology"]
    assert topology["roles"]["observability"] == "inspection-only"
    assert topology["roles"]["observability_executor"] is False
    assert topology["roles"]["observability_orchestrator"] is False
    assert topology["roles"]["observability_can_create_authority"] is False


def test_boundary_guarantees_preserve_read_only_non_execution_semantics():
    boundaries = _load(EVIDENCE / "GOVERNED_EXECUTION_OBSERVABILITY_BOUNDARY_GUARANTEES.json")
    assert boundaries["read_only"] is True
    assert boundaries["execution_triggered"] is False
    assert boundaries["codex_dispatch_path_exists"] is False
    assert boundaries["subprocess_path_exists"] is False
    assert boundaries["orchestration"] is False
    assert boundaries["autonomous_execution"] is False


def test_next_phase_boundary_keeps_chatgpt_non_authoritative():
    boundary = _load(EVIDENCE / "GOVERNED_EXECUTION_OBSERVABILITY_NEXT_PHASE_BOUNDARY.json")
    assert boundary["next_phase"] == "GOVERNED_CHATGPT_INTERPRETATION_BRIDGE_V2"
    assert boundary["chatgpt_integration_must_remain_non_authoritative"] is True
    assert boundary["aigol_remains_governance_authority"] is True
    assert boundary["observability_must_remain_read_only"] is True


def test_constitutional_statement_exists_exactly():
    assert STATEMENT in FINALIZE_MD.read_text()
    assert _load(EVIDENCE / "GOVERNED_EXECUTION_OBSERVABILITY_TOPOLOGY.json")["constitutional_statement"] == STATEMENT
    assert _load(EVIDENCE / "GOVERNED_EXECUTION_OBSERVABILITY_BOUNDARY_GUARANTEES.json")["constitutional_statement"] == STATEMENT
    assert _load(EVIDENCE / "GOVERNED_EXECUTION_OBSERVABILITY_NEXT_PHASE_BOUNDARY.json")["constitutional_statement"] == STATEMENT
