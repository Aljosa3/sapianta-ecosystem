from sapianta_bridge.active_chatgpt_bridge.bridge_controller import run_active_chatgpt_bridge
from sapianta_bridge.active_chatgpt_bridge.bridge_validator import validate_bridge_artifacts


def test_active_chatgpt_bridge_validator_accepts_complete_bridge() -> None:
    output = run_active_chatgpt_bridge("Inspect governance evidence")
    validation = validate_bridge_artifacts(
        request=output["bridge_request"],
        binding=output["bridge_binding"],
        response=output["bridge_response"],
        lifecycle=output["bridge_lifecycle"],
    )

    assert validation["valid"] is True
    assert validation["provider_identity_consistent"] is True


def test_active_chatgpt_bridge_validator_rejects_provider_mismatch() -> None:
    output = run_active_chatgpt_bridge("Inspect governance evidence")
    response = output["bridge_response"]
    response["provider_id"] = "codex"
    validation = validate_bridge_artifacts(
        request=output["bridge_request"],
        binding=output["bridge_binding"],
        response=response,
        lifecycle=output["bridge_lifecycle"],
    )

    assert validation["valid"] is False
    assert {"field": "provider_id", "reason": "bridge response lineage mismatch"} in validation["errors"]


def test_active_chatgpt_bridge_validator_rejects_lifecycle_skip() -> None:
    output = run_active_chatgpt_bridge("Inspect governance evidence")
    validation = validate_bridge_artifacts(
        request=output["bridge_request"],
        binding=output["bridge_binding"],
        response=output["bridge_response"],
        lifecycle=["CREATED", "COMPLETED"],
    )

    assert validation["valid"] is False
