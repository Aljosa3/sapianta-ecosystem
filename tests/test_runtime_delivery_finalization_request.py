from sapianta_bridge.governed_runtime_delivery_finalization.runtime_delivery_finalization_request import create_runtime_delivery_finalization_request


def test_runtime_delivery_finalization_request_preserves_commit_identity():
    request = create_runtime_delivery_finalization_request(
        finalization_session={"runtime_delivery_finalization_id": "FIN-1", "runtime_execution_commit_id": "COMMIT-1"}
    ).to_dict()
    assert request["runtime_execution_commit_id"] == "COMMIT-1"
