from sapianta_bridge.governed_runtime_delivery_finalization.runtime_delivery_finalization_session import (
    create_runtime_delivery_finalization_session,
    validate_runtime_delivery_finalization_session,
)


def test_runtime_delivery_finalization_session_is_deterministic():
    commit = {"runtime_execution_commit_session": {"runtime_execution_commit_id": "COMMIT-1"}}
    first = create_runtime_delivery_finalization_session(commit_output=commit).to_dict()
    second = create_runtime_delivery_finalization_session(commit_output=commit).to_dict()
    assert first["runtime_delivery_finalization_id"] == second["runtime_delivery_finalization_id"]
    assert validate_runtime_delivery_finalization_session(first)["valid"] is True
