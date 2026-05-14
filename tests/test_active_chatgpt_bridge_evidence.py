from sapianta_bridge.active_chatgpt_bridge.bridge_controller import run_active_chatgpt_bridge
from sapianta_bridge.active_chatgpt_bridge.bridge_evidence import validate_bridge_evidence


def test_active_chatgpt_bridge_evidence_is_valid_and_replay_safe() -> None:
    evidence = run_active_chatgpt_bridge("Inspect governance evidence")["bridge_evidence"]

    assert evidence["bridge_status"] == "COMPLETED"
    assert evidence["replay_safe"] is True
    assert evidence["copy_paste_reduction_ready"] is True
    assert validate_bridge_evidence(evidence)["valid"] is True


def test_active_chatgpt_bridge_evidence_rejects_forbidden_behavior_flags() -> None:
    evidence = run_active_chatgpt_bridge("Inspect governance evidence")["bridge_evidence"]
    evidence["provider_routing_introduced"] = True

    assert validate_bridge_evidence(evidence)["valid"] is False
