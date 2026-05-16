from sapianta_bridge.governed_runtime_operation_envelope.runtime_operation_contract import (
    create_runtime_operation_contract,
)


def test_contract_binds_to_envelope():
    contract = create_runtime_operation_contract(runtime_operation_envelope_id="ENV-1")
    assert contract["runtime_operation_envelope_id"] == "ENV-1"
    assert contract["structured_operation_required"] is True
