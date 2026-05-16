from sapianta_bridge.governed_runtime_execution_realization.runtime_execution_realization_transaction import (
    create_runtime_execution_realization_transaction,
)


def test_transaction_preserves_capture_and_response():
    tx = create_runtime_execution_realization_transaction(
        runtime_execution_realization_id="REAL-1",
        result_capture_id="CAPTURE-1",
        response_return_id="RETURN-1",
    )
    assert tx["result_capture_id"] == "CAPTURE-1"
    assert tx["response_return_id"] == "RETURN-1"
