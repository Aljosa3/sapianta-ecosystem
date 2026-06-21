"""Tests for AIGOL_HUMAN_INTENT_CLARIFICATION_CERTIFICATION_V1."""

from __future__ import annotations

from pathlib import Path

from aigol.runtime.conversational_cli_runtime import (
    CLARIFICATION_REQUIRED,
    HUMAN_INTENT_CLARIFICATION_INTAKE,
    route_conversational_cli_intent,
)
from aigol.runtime.human_intent_clarification_certification_v1 import (
    AMBIGUOUS_PROMPTS,
    MILESTONE_ID,
    run_human_intent_clarification_certification,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json


def test_required_ambiguous_prompts_route_to_clarification_first(tmp_path):
    for index, prompt in enumerate(AMBIGUOUS_PROMPTS, start=1):
        capture = route_conversational_cli_intent(
            routing_id=f"TEST-HIC-{index}:ROUTING",
            prompt_id=f"TEST-HIC-{index}:PROMPT",
            human_prompt=prompt,
            canonical_chain_id=f"TEST-HIC-{index}:CHAIN",
            created_at="2026-06-21T00:00:00Z",
            replay_dir=tmp_path / f"scenario-{index}" / "conversational_cli_routing",
        )
        selection = capture["workflow_selection_artifact"]

        assert capture["routing_status"] == CLARIFICATION_REQUIRED
        assert capture["workflow_id"] == HUMAN_INTENT_CLARIFICATION_INTAKE
        assert selection["clarification_questions"]
        assert selection["provider_invoked"] is False
        assert selection["worker_invoked"] is False
        assert selection["execution_requested"] is False
        assert selection["approval_bypassed"] is False


def test_human_intent_clarification_certification_produces_required_artifacts(tmp_path):
    result = run_human_intent_clarification_certification(replay_base=tmp_path / "hic")

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_verdict"] == "HUMAN_INTENT_CLARIFICATION_CERTIFIED"
    assert all(result["assertions"].values())

    root = Path(result["cert_root"])
    evidence_path = root / "evidence_package" / "000_human_intent_clarification_evidence_package.json"
    coverage_path = root / "evidence_package" / "001_human_intent_clarification_coverage_report.json"
    replay_path = root / "replay_package" / "000_human_intent_clarification_replay_package.json"
    report_path = root / "certification_report" / "000_human_intent_clarification_certification_report.json"

    assert evidence_path.exists()
    assert coverage_path.exists()
    assert replay_path.exists()
    assert report_path.exists()

    report = load_json(report_path)
    observed = report["observed"]
    assert observed["ambiguous_intent_detected"] is True
    assert observed["clarification_generated"] is True
    assert observed["clarification_response_received"] is True
    assert observed["context_updated"] is True
    assert observed["intent_resolved"] is True
    assert observed["workflow_selected"] is True
    assert observed["execution_summary_generated"] is True
    assert observed["human_confirmation_recorded"] is True
    assert observed["replay_reconstructed"] is True
    assert observed["approval_boundaries_preserved"] is True
    assert observed["secret_free_evidence"] is True


def test_human_intent_clarification_certification_replay_is_secret_free(tmp_path):
    result = run_human_intent_clarification_certification(replay_base=tmp_path / "hic")
    root = Path(result["cert_root"])
    serialized = ""
    for path in sorted(root.rglob("*.json")):
        serialized += canonical_serialize(load_json(path))

    assert "sk-" not in serialized
    assert "Bearer " not in serialized
    assert "api_key" not in serialized.lower()
