from sapianta_bridge.active_chatgpt_bridge.bridge_binding import validate_bridge_binding
from sapianta_bridge.active_chatgpt_bridge.bridge_controller import run_active_chatgpt_bridge


def test_active_chatgpt_bridge_binding_is_valid_and_replay_safe() -> None:
    output = run_active_chatgpt_bridge("Inspect governance evidence")
    binding = output["bridge_binding"]

    assert binding["bridge_id"].startswith("CHATGPT-BRIDGE-")
    assert binding["replay_safe"] is True
    assert validate_bridge_binding(binding)["valid"] is True


def test_active_chatgpt_bridge_binding_rejects_identity_mutation() -> None:
    output = run_active_chatgpt_bridge("Inspect governance evidence")
    binding = output["bridge_binding"]
    binding["bridge_id"] = "CHATGPT-BRIDGE-MUTATED"

    assert validate_bridge_binding(binding)["valid"] is False
