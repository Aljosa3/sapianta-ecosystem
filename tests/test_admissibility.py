from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sapianta_bridge.policy.policy_engine import build_policy_evaluation


def test_runtime_boundary_proposal_classified_restricted() -> None:
    evaluation = build_policy_evaluation(
        {
            "input_type": "REFLECTION_PROPOSAL",
            "proposal_id": "PROP-001",
            "summary": "improve runtime observability coverage",
            "requires_human_approval": True,
            "allowed_to_execute_automatically": False,
            "lineage": {"source_reflection_id": "REFLECTION-001", "source_task_id": "TASK-001"},
        },
        timestamp="2026-05-12T00:00:00+00:00",
    )

    assert evaluation["classification"]["admissibility"] == "RESTRICTED"
    assert evaluation["classification"]["risk_level"] == "MEDIUM"
