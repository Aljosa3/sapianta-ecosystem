from sapianta_bridge.active_invocation.invocation_lifecycle import (
    complete_invocation_lifecycle,
    next_lifecycle_state,
    validate_lifecycle,
)


def test_invocation_lifecycle_is_fixed_and_ordered() -> None:
    assert complete_invocation_lifecycle() == [
        "PROPOSED",
        "VALIDATED",
        "INVOKED",
        "RESULT_RECEIVED",
        "EVIDENCE_RECORDED",
    ]
    assert next_lifecycle_state("PROPOSED") == "VALIDATED"


def test_invocation_lifecycle_blocks_hidden_states() -> None:
    validation = validate_lifecycle(["PROPOSED", "RETRYING"])

    assert validation["valid"] is False
    assert validation["hidden_states_present"] is True
    assert validation["retry_present"] is False
