import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FINALIZE_MD = ROOT / ".github/governance/finalize/FINALIZE_GOVERNED_EXECUTION_RUNTIME_V1.md"
FINALIZE_JSON = ROOT / ".github/governance/finalize/FINALIZE_GOVERNED_EXECUTION_RUNTIME_V1.json"
EVIDENCE = ROOT / "runtime/finalization_evidence"
STATEMENT = "The system can perform bounded governance-controlled Codex execution, but does not perform autonomous execution."

JSON_FILES = [
    FINALIZE_JSON,
    EVIDENCE / "GOVERNED_EXECUTION_RUNTIME_CERTIFICATION.json",
    EVIDENCE / "GOVERNED_EXECUTION_RUNTIME_TOPOLOGY.json",
    EVIDENCE / "GOVERNED_EXECUTION_RUNTIME_REPLAY_CERTIFICATION.json",
    EVIDENCE / "GOVERNED_EXECUTION_RUNTIME_BOUNDARY_GUARANTEES.json",
    EVIDENCE / "GOVERNED_EXECUTION_RUNTIME_CONTINUITY_REPORT.json",
    EVIDENCE / "GOVERNED_EXECUTION_RUNTIME_NEXT_PHASE_BOUNDARY.json",
]


def _load(path):
    return json.loads(path.read_text())


def test_required_finalization_artifacts_exist_and_parse():
    assert FINALIZE_MD.exists()
    for path in JSON_FILES:
        assert path.exists()
        assert _load(path)


def test_certification_includes_required_execution_components():
    finalize = _load(FINALIZE_JSON)
    for component in (
        "Execution Consumer",
        "Codex Execution Adapter",
        "Authority Token Validation",
        "Bounded Codex Dispatch",
        "Deterministic Execution Receipts",
        "shell=False enforcement",
        "bounded timeout enforcement",
    ):
        assert component in finalize["included_components"]


def test_topology_declares_bounded_codex_execution():
    topology = _load(EVIDENCE / "GOVERNED_EXECUTION_RUNTIME_TOPOLOGY.json")
    assert "Bounded Codex Execution" in topology["topology"]
    assert topology["codex_execution_is_authority_token_gated"] is True
    assert topology["roles"]["execution_adapter"] == "not an agent"
    assert topology["roles"]["execution_consumer"] == "not an orchestrator"


def test_boundary_guarantees_exclude_autonomy_orchestration_and_enforce_shell_false():
    boundaries = _load(EVIDENCE / "GOVERNED_EXECUTION_RUNTIME_BOUNDARY_GUARANTEES.json")
    assert boundaries["autonomous_continuation"] is False
    assert boundaries["orchestration"] is False
    assert boundaries["shell_false_enforced"] is True
    assert boundaries["authority_token_required"] is True


def test_next_phase_boundary_references_observability_or_chatgpt_bridge():
    boundary = _load(EVIDENCE / "GOVERNED_EXECUTION_RUNTIME_NEXT_PHASE_BOUNDARY.json")
    assert boundary["next_phase"] == "GOVERNED_EXECUTION_OBSERVABILITY_V1"
    assert boundary["alternate_future_boundary"] == "GOVERNED_CHATGPT_INTERPRETATION_BRIDGE_V2"


def test_constitutional_statement_exists_exactly():
    assert STATEMENT in FINALIZE_MD.read_text()
    assert _load(EVIDENCE / "GOVERNED_EXECUTION_RUNTIME_TOPOLOGY.json")["constitutional_statement"] == STATEMENT
    assert _load(EVIDENCE / "GOVERNED_EXECUTION_RUNTIME_BOUNDARY_GUARANTEES.json")["constitutional_statement"] == STATEMENT
    assert _load(EVIDENCE / "GOVERNED_EXECUTION_RUNTIME_NEXT_PHASE_BOUNDARY.json")["constitutional_statement"] == STATEMENT
