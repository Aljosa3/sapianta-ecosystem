from sapianta_bridge.governed_runtime_execution_commit.runtime_execution_commit_state import RUNTIME_EXECUTION_COMMIT_STATES, SUCCESS_PATH


def test_runtime_execution_commit_states_are_explicit():
    assert SUCCESS_PATH[-1] == "RUNTIME_EXECUTION_COMMIT_FINALIZED"
    assert "RUNTIME_EXECUTION_COMMIT_BLOCKED" in RUNTIME_EXECUTION_COMMIT_STATES
    assert "RUNTIME_EXECUTION_COMMIT_REJECTED" in RUNTIME_EXECUTION_COMMIT_STATES
