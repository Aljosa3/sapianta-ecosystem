from sapianta_bridge.governed_runtime_execution_commit.runtime_execution_commit_response import create_runtime_execution_commit_response


def test_runtime_execution_commit_response_preserves_result_and_return():
    response = create_runtime_execution_commit_response(
        binding={"runtime_execution_commit_id": "COMMIT-1", "result_capture_id": "CAP-1", "response_return_id": "RETURN-1"}
    ).to_dict()
    assert response["result_capture_id"] == "CAP-1"
    assert response["response_return_id"] == "RETURN-1"
