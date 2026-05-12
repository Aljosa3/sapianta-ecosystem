from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sapianta_bridge.policy.policy_engine import build_policy_evaluation
from sapianta_bridge.policy.policy_rules import detect_forbidden_capabilities


def _request(summary: str, **extra) -> dict:
    value = {
        "input_type": "GOVERNANCE_REQUEST",
        "request_id": "REQ-001",
        "summary": summary,
        "allowed_to_execute_automatically": False,
        "lineage": {"source_task_id": "TASK-001"},
    }
    value.update(extra)
    return value


def test_automatic_execution_request_blocked() -> None:
    evaluation = build_policy_evaluation(
        _request("run automatically", allowed_to_execute_automatically=True),
        timestamp="2026-05-12T00:00:00+00:00",
    )

    assert evaluation["classification"]["admissibility"] == "BLOCKED"
    assert "automatic_execution" in evaluation["evidence"]["blocked_capabilities"]


def test_execution_authority_granted_true_blocked() -> None:
    evaluation = build_policy_evaluation(
        _request("grant execution", execution_authority_granted=True),
        timestamp="2026-05-12T00:00:00+00:00",
    )

    assert evaluation["classification"]["admissibility"] == "BLOCKED"
    assert "execution_authority_granted" in evaluation["evidence"]["blocked_capabilities"]


def test_codex_invocation_request_blocked() -> None:
    assert "codex_invocation" in detect_forbidden_capabilities(_request("invoke Codex now"))


def test_transport_invocation_request_blocked() -> None:
    assert "transport_invocation" in detect_forbidden_capabilities(_request("trigger transport"))


def test_self_modifying_governance_request_blocked() -> None:
    assert "self_modifying_governance" in detect_forbidden_capabilities(
        _request("enable self-modifying governance")
    )


def test_auto_merge_auto_push_request_blocked() -> None:
    blocked = detect_forbidden_capabilities(_request("allow auto-merge and auto-push"))

    assert "auto_merge" in blocked
    assert "auto_push" in blocked
