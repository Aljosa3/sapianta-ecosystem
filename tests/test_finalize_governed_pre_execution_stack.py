import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FINALIZE_MD = ROOT / ".github/governance/finalize/FINALIZE_GOVERNED_PRE_EXECUTION_STACK_V1.md"
FINALIZE_JSON = ROOT / ".github/governance/finalize/FINALIZE_GOVERNED_PRE_EXECUTION_STACK_V1.json"
EVIDENCE = ROOT / "runtime/finalization_evidence"
STATEMENT = "The system may authorize bounded downstream execution eligibility, but does not execute downstream tasks."

JSON_FILES = [
    FINALIZE_JSON,
    EVIDENCE / "GOVERNED_PRE_EXECUTION_STACK_CERTIFICATION.json",
    EVIDENCE / "GOVERNED_PRE_EXECUTION_STACK_TOPOLOGY.json",
    EVIDENCE / "GOVERNED_PRE_EXECUTION_STACK_REPLAY_CERTIFICATION.json",
    EVIDENCE / "GOVERNED_PRE_EXECUTION_STACK_BOUNDARY_GUARANTEES.json",
    EVIDENCE / "GOVERNED_PRE_EXECUTION_STACK_CONTINUITY_REPORT.json",
    EVIDENCE / "GOVERNED_PRE_EXECUTION_STACK_NEXT_PHASE_BOUNDARY.json",
]


def _load(path):
    return json.loads(path.read_text())


def test_required_finalization_files_exist_and_parse():
    assert FINALIZE_MD.exists()
    for path in JSON_FILES:
        assert path.exists()
        assert _load(path)


def test_required_constitutional_statement_exists_everywhere_required():
    assert STATEMENT in FINALIZE_MD.read_text()
    assert _load(EVIDENCE / "GOVERNED_PRE_EXECUTION_STACK_TOPOLOGY.json")["constitutional_statement"] == STATEMENT
    assert _load(EVIDENCE / "GOVERNED_PRE_EXECUTION_STACK_NEXT_PHASE_BOUNDARY.json")["constitutional_statement"] == STATEMENT


def test_prohibited_capability_exclusions_exist():
    finalize = _load(FINALIZE_JSON)
    for capability in (
        "Codex execution",
        "automatic prompt dispatch",
        "downstream task execution",
        "orchestration",
        "retries/fallbacks",
        "hidden continuation",
        "autonomous loops",
        "unrestricted subprocess execution",
        "shell=True",
        "persistent execution authority",
    ):
        assert capability in finalize["excluded_capabilities"]


def test_next_phase_boundary_names_governed_execution_consumer():
    boundary = _load(EVIDENCE / "GOVERNED_PRE_EXECUTION_STACK_NEXT_PHASE_BOUNDARY.json")
    assert boundary["next_phase"] == "GOVERNED_EXECUTION_CONSUMER_V1"
    assert boundary["authorization_is_execution"] is False
    assert boundary["downstream_execution_still_prohibited"] is True


def test_authorization_is_not_execution_boundary_is_certified():
    certification = _load(EVIDENCE / "GOVERNED_PRE_EXECUTION_STACK_CERTIFICATION.json")
    topology = _load(EVIDENCE / "GOVERNED_PRE_EXECUTION_STACK_TOPOLOGY.json")
    assert certification["downstream_execution_present"] is False
    assert topology["execution_position"] == "constitutionally external"
