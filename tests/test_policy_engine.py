from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sapianta_bridge.policy.policy_engine import build_policy_evaluation, evaluate_policy_input
from sapianta_bridge.policy.policy_models import PolicyError
from sapianta_bridge.transport.transport_config import TransportConfig


def _config(tmp_path: Path) -> TransportConfig:
    config = TransportConfig(
        runtime_root=tmp_path / "runtime",
        workspace=tmp_path / "workspace",
        quarantine_root=tmp_path / "quarantine",
    )
    config.ensure_directories()
    config.workspace.mkdir()
    return config


def _proposal(**extra) -> dict:
    value = {
        "input_type": "REFLECTION_PROPOSAL",
        "proposal_id": "PROP-001",
        "proposal_type": "FOLLOW_UP",
        "summary": "improve deterministic observability",
        "requires_human_approval": True,
        "allowed_to_execute_automatically": False,
        "lineage": {"source_reflection_id": "REFLECTION-001", "source_task_id": "TASK-001"},
    }
    value.update(extra)
    return value


def test_advisory_only_proposal_classified_allowed() -> None:
    evaluation = build_policy_evaluation(_proposal(), timestamp="2026-05-12T00:00:00+00:00")

    assert evaluation["classification"]["admissibility"] == "ALLOWED"
    assert evaluation["classification"]["risk_level"] == "LOW"
    assert evaluation["classification"]["allowed_to_execute_automatically"] is False
    assert evaluation["execution_authority_granted"] is False


def test_governance_boundary_proposal_classified_escalate() -> None:
    evaluation = build_policy_evaluation(
        _proposal(summary="modify governance boundary and authority semantics"),
        timestamp="2026-05-12T00:00:00+00:00",
    )

    assert evaluation["classification"]["admissibility"] == "ESCALATE"
    assert evaluation["classification"]["escalation_class"] == "GOVERNANCE_REVIEW"


def test_missing_lineage_fails_closed() -> None:
    value = _proposal()
    del value["lineage"]

    with pytest.raises(PolicyError) as exc_info:
        build_policy_evaluation(value, timestamp="2026-05-12T00:00:00+00:00")

    assert exc_info.value.field == "lineage"


def test_unknown_input_type_fails_closed() -> None:
    value = _proposal(input_type="UNKNOWN")

    with pytest.raises(PolicyError) as exc_info:
        build_policy_evaluation(value, timestamp="2026-05-12T00:00:00+00:00")

    assert exc_info.value.field == "input_type"


def test_policy_evidence_written_append_only(tmp_path: Path) -> None:
    config = _config(tmp_path)

    first = evaluate_policy_input(
        _proposal(proposal_id="PROP-001"),
        config,
        timestamp="2026-05-12T00:00:00+00:00",
    )
    second = evaluate_policy_input(
        _proposal(proposal_id="PROP-002", summary="improve deterministic replay visibility"),
        config,
        timestamp="2026-05-12T00:00:01+00:00",
    )

    assert Path(first["policy_evaluation_path"]).exists()
    assert Path(second["policy_evaluation_path"]).exists()
    assert len(list((config.runtime_root / "policy" / "evaluations").glob("*.json"))) == 2
