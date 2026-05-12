from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sapianta_bridge.policy.policy_engine import build_policy_evaluation


def test_normal_approval_candidate_classified_human_review() -> None:
    evaluation = build_policy_evaluation(
        {
            "input_type": "APPROVAL_CANDIDATE",
            "approval_id": "APPROVAL-001",
            "decision": "PENDING",
            "allowed_to_execute_automatically": False,
            "lineage": {"source_reflection_id": "REFLECTION-001", "source_task_id": "TASK-001"},
        },
        timestamp="2026-05-12T00:00:00+00:00",
    )

    assert evaluation["classification"]["admissibility"] == "ALLOWED"
    assert evaluation["classification"]["escalation_class"] == "HUMAN_REVIEW"
