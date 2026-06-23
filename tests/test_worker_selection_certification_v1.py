"""Tests for AIGOL_WORKER_SELECTION_CERTIFICATION_V1."""

from __future__ import annotations

from pathlib import Path

from aigol.runtime.transport.serialization import canonical_serialize, load_json
from aigol.runtime.worker_selection_certification_v1 import (
    MILESTONE_ID,
    reconstruct_worker_selection_replay,
    run_worker_selection_certification_v1,
)


def test_worker_selection_certifies_all_required_scenarios(tmp_path):
    result = run_worker_selection_certification_v1(replay_base=tmp_path / "worker_selection")

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_verdict"] == "WORKER_SELECTION_CERTIFIED"
    assert all(result["assertions"].values())

    scenarios = {item["scenario_id"]: item for item in result["scenario_results"]}
    assert set(scenarios) == {"WSG-001", "WSG-002", "WSG-003", "WSG-004", "WSG-005", "WSG-006", "WSG-007"}
    assert all(item["scenario_verdict"] == "CERTIFIED" for item in scenarios.values())


def test_worker_selection_records_rationale_scores_and_rejections(tmp_path):
    result = run_worker_selection_certification_v1(replay_base=tmp_path / "worker_selection")

    for item in result["scenario_results"]:
        assert item["selection_rationale_recorded"] is True
        assert item["suitability_score_recorded"] is True
        assert item["alternative_rejection_visible"] is True

    root = Path(result["cert_root"])
    rationale = load_json(root / "scenarios" / "WSG-003" / "004_worker_selection_rationale.json")
    assert rationale["reviewer_can_determine_why_selected"] is True
    assert rationale["reviewer_can_determine_why_alternatives_rejected"] is True
    assert rationale["alternatives"][0]["rejection_reason"] == "deterministic-first policy or stronger suitability score"


def test_worker_selection_enforces_deterministic_first_policy(tmp_path):
    result = run_worker_selection_certification_v1(replay_base=tmp_path / "worker_selection")
    root = Path(result["cert_root"])

    scenario_001 = load_json(root / "scenarios" / "WSG-001" / "003_worker_selection_decision.json")
    scenario_003 = load_json(root / "scenarios" / "WSG-003" / "003_worker_selection_decision.json")

    assert scenario_001["selected_worker_class"] == "DETERMINISTIC_WORKER"
    assert scenario_001["deterministic_first_policy_enforced"] is True
    assert scenario_003["selected_worker"] == "deterministic_summary_worker"
    assert scenario_003["deterministic_first_policy_enforced"] is True


def test_worker_selection_replay_reconstructs(tmp_path):
    result = run_worker_selection_certification_v1(replay_base=tmp_path / "worker_selection")
    reconstruction = reconstruct_worker_selection_replay(result["cert_root"])

    assert reconstruction["replay_reconstructed"] is True
    assert reconstruction["scenario_count"] == 7
    assert all(item["authority_preserved"] for item in reconstruction["scenario_records"])


def test_worker_selection_evidence_is_secret_free(tmp_path):
    result = run_worker_selection_certification_v1(replay_base=tmp_path / "worker_selection")
    serialized = ""
    for path in sorted(Path(result["cert_root"]).rglob("*.json")):
        serialized += canonical_serialize(load_json(path))

    assert "sk-" not in serialized
    assert "Bearer " not in serialized
    assert "OPENAI_API_KEY=" not in serialized
    assert "ANTHROPIC_API_KEY=" not in serialized
