from sapianta_bridge.human_interaction_continuity.interaction_request import (
    create_interaction_request,
    validate_interaction_request,
)


def test_interaction_request_is_deterministic():
    request = create_interaction_request("Inspect", conversation_id="C-1", execution_gate_id="G-1", replay_identity="R-1").to_dict()
    assert request == create_interaction_request("Inspect", conversation_id="C-1", execution_gate_id="G-1", replay_identity="R-1").to_dict()
    assert validate_interaction_request(request)["valid"] is True


def test_interaction_request_requires_gate_reference():
    request = create_interaction_request("Inspect", conversation_id="C-1", execution_gate_id="", replay_identity="R-1").to_dict()
    assert validate_interaction_request(request)["valid"] is False
