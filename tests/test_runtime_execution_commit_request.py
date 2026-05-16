from sapianta_bridge.governed_runtime_execution_commit.runtime_execution_commit_request import create_runtime_execution_commit_request


def test_runtime_execution_commit_request_preserves_activation_identity():
    request = create_runtime_execution_commit_request(
        commit_session={"runtime_execution_commit_id": "COMMIT-1", "runtime_activation_gate_id": "ACT-1"}
    ).to_dict()
    assert request["runtime_activation_gate_id"] == "ACT-1"
