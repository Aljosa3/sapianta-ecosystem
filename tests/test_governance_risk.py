from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sapianta_bridge.reflection.governance_risk import governance_risk_from_evidence


def test_governance_risk_deterministic() -> None:
    replay = {"final_state": "COMPLETED"}
    summary = {"failed_executions": 0, "total_executions": 1}
    transitions = {"invalid_transition_detected": False}

    first = governance_risk_from_evidence(replay, summary, transitions)
    second = governance_risk_from_evidence(replay, summary, transitions)

    assert first == second
    assert first == {
        "level": "LOW",
        "summary": "bounded transport stable; no governance escalation detected",
    }
