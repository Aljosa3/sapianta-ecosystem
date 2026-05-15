from sapianta_bridge.human_interaction_continuity.interaction_controller import run_human_interaction_continuity
from sapianta_bridge.human_interaction_continuity.interaction_evidence import validate_interaction_evidence


def test_interaction_evidence_is_replay_safe():
    output = run_human_interaction_continuity("Inspect governance evidence", execution_gate_id="GATE-1")
    evidence = output["interaction_evidence"]
    assert validate_interaction_evidence(evidence)["valid"] is True
    assert evidence["lineage_preserved"] is True
    assert evidence["replay_safe"] is True
    assert evidence["orchestration_introduced"] is False
