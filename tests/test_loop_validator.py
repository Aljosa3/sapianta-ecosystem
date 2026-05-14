from sapianta_bridge.no_copy_paste_loop.loop_controller import run_no_copy_paste_loop
from sapianta_bridge.no_copy_paste_loop.loop_validator import validate_loop_artifacts


def test_loop_validator_accepts_complete_loop() -> None:
    output = run_no_copy_paste_loop("Inspect governance evidence")
    validation = validate_loop_artifacts(
        request=output["loop_request"],
        binding=output["loop_binding"],
        response=output["loop_response"],
        lifecycle=output["loop_lifecycle"],
    )

    assert validation["valid"] is True
    assert validation["lineage_continuity_valid"] is True


def test_loop_validator_blocks_provider_mismatch() -> None:
    output = run_no_copy_paste_loop("Inspect governance evidence")
    response = output["loop_response"]
    response["provider_id"] = "codex"
    validation = validate_loop_artifacts(
        request=output["loop_request"],
        binding=output["loop_binding"],
        response=response,
        lifecycle=output["loop_lifecycle"],
    )

    assert validation["valid"] is False
    assert {"field": "provider_id", "reason": "loop response binding mismatch"} in validation["errors"]


def test_loop_validator_fails_closed_on_lifecycle_skip() -> None:
    output = run_no_copy_paste_loop("Inspect governance evidence")
    validation = validate_loop_artifacts(
        request=output["loop_request"],
        binding=output["loop_binding"],
        response=output["loop_response"],
        lifecycle=["CREATED", "COMPLETED"],
    )

    assert validation["valid"] is False
