from sapianta_bridge.human_interaction_continuity.interaction_controller import run_human_interaction_continuity
from sapianta_bridge.human_interaction_continuity.interaction_binding import validate_interaction_binding


def test_interaction_binding_preserves_governed_lineage():
    output = run_human_interaction_continuity("Inspect governance evidence", execution_gate_id="GATE-1")
    binding = output["interaction_binding"]
    assert validate_interaction_binding(binding)["valid"] is True
    assert binding["provider_id"] == output["interaction_response"]["provider_id"]
    assert binding["execution_gate_id"] == "GATE-1"
