from sapianta_bridge.governed_runtime_execution_commit.runtime_execution_commit_session import (
    create_runtime_execution_commit_session,
    validate_runtime_execution_commit_session,
)


def test_runtime_execution_commit_session_is_deterministic():
    activation = {"runtime_activation_gate_session": {"runtime_activation_gate_id": "ACT-1"}}
    first = create_runtime_execution_commit_session(activation_output=activation).to_dict()
    second = create_runtime_execution_commit_session(activation_output=activation).to_dict()
    assert first["runtime_execution_commit_id"] == second["runtime_execution_commit_id"]
    assert validate_runtime_execution_commit_session(first)["valid"] is True
