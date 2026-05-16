from sapianta_bridge.governed_runtime_operational_entrypoint.runtime_operational_entrypoint_state import FINALIZED_PATH, RUNTIME_OPERATIONAL_ENTRYPOINT_STATES


def test_states_are_bounded_and_finalized():
    assert FINALIZED_PATH[-1] == "RUNTIME_OPERATIONAL_ENTRY_FINALIZED"
    assert "BLOCKED" in RUNTIME_OPERATIONAL_ENTRYPOINT_STATES
