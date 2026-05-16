from sapianta_bridge.governed_runtime_operational_entrypoint.runtime_operational_entrypoint_transaction import (
    create_runtime_operational_entrypoint_transaction,
)


def test_transaction_preserves_realization_capture_and_response():
    tx = create_runtime_operational_entrypoint_transaction(
        runtime_operational_entrypoint_id="ENTRY-1",
        runtime_execution_realization_id="REAL-1",
        result_capture_id="CAPTURE-1",
        response_return_id="RETURN-1",
    )
    assert tx["runtime_execution_realization_id"] == "REAL-1"
