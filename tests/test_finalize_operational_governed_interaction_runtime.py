import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FINALIZE_MD = ROOT / ".github/governance/finalize/FINALIZE_OPERATIONAL_GOVERNED_INTERACTION_RUNTIME_V1.md"
FINALIZE_JSON = ROOT / ".github/governance/finalize/FINALIZE_OPERATIONAL_GOVERNED_INTERACTION_RUNTIME_V1.json"
EVIDENCE = ROOT / "runtime/finalization_evidence"

REQUIRED_JSON = [
    FINALIZE_JSON,
    EVIDENCE / "OPERATIONAL_GOVERNED_INTERACTION_RUNTIME_CERTIFICATION.json",
    EVIDENCE / "OPERATIONAL_GOVERNED_INTERACTION_RUNTIME_TOPOLOGY.json",
    EVIDENCE / "OPERATIONAL_GOVERNED_INTERACTION_RUNTIME_REPLAY_CERTIFICATION.json",
    EVIDENCE / "OPERATIONAL_GOVERNED_INTERACTION_RUNTIME_BOUNDARY_GUARANTEES.json",
    EVIDENCE / "OPERATIONAL_GOVERNED_INTERACTION_RUNTIME_CONTINUITY_REPORT.json",
    EVIDENCE / "OPERATIONAL_GOVERNED_INTERACTION_RUNTIME_NEXT_PHASE_BOUNDARY.json",
]


def _load(path):
    return json.loads(path.read_text())


def test_all_required_finalization_artifacts_exist_and_parse():
    assert FINALIZE_MD.exists()
    for path in REQUIRED_JSON:
        assert path.exists()
        assert _load(path)


def test_certification_includes_required_components():
    certification = _load(EVIDENCE / "OPERATIONAL_GOVERNED_INTERACTION_RUNTIME_CERTIFICATION.json")
    assert certification["components"] == [
        "preview runtime",
        "operator CLI",
        "ChatGPT bridge",
        "MCP wrapper",
        "live MCP host entrypoint",
        "browser companion",
        "governed intent interpretation layer",
    ]


def test_topology_declares_browser_companion_and_localhost_runtime():
    topology = _load(EVIDENCE / "OPERATIONAL_GOVERNED_INTERACTION_RUNTIME_TOPOLOGY.json")
    assert "browser companion" in topology["browser_topology"]
    assert "localhost preview runtime" in topology["browser_topology"]
    assert topology["roles"]["browser_companion"] == "local ingress UI"
    assert topology["roles"]["runtime"] == "governance authority"


def test_boundary_guarantees_exclude_codex_execution_and_prohibited_capabilities():
    boundaries = _load(EVIDENCE / "OPERATIONAL_GOVERNED_INTERACTION_RUNTIME_BOUNDARY_GUARANTEES.json")
    assert boundaries["codex_execution_authority"] is False
    assert boundaries["hidden_execution"] is False
    assert boundaries["agentic_continuation"] is False
    assert boundaries["retries"] is False
    assert boundaries["fallbacks"] is False
    assert boundaries["shell_true"] is False
    assert boundaries["unrestricted_subprocess_execution"] is False


def test_next_phase_boundary_defers_codex_task_synthesis():
    next_phase = _load(EVIDENCE / "OPERATIONAL_GOVERNED_INTERACTION_RUNTIME_NEXT_PHASE_BOUNDARY.json")
    assert next_phase["next_phase"] == "GOVERNED_CODEX_TASK_SYNTHESIS_V1"
    assert next_phase["allowed_only_after_finalization"] is True
    assert next_phase["requirements"] == {
        "non_executing": True,
        "preview_only": True,
        "explicit_approval_required": True,
        "replay_visible": True,
        "fail_closed": True,
    }


def test_finalization_declares_no_runtime_behavior_change():
    finalize = _load(FINALIZE_JSON)
    certification = _load(EVIDENCE / "OPERATIONAL_GOVERNED_INTERACTION_RUNTIME_CERTIFICATION.json")
    assert finalize["runtime_behavior_modified"] is False
    assert certification["runtime_behavior_modified"] is False
