from sapianta_bridge.governed_runtime_execution_realization.runtime_execution_realization_contract import (
    create_runtime_execution_realization_contract,
)


def test_contract_requires_activated_surface():
    contract = create_runtime_execution_realization_contract(runtime_execution_realization_id="REAL-1")
    assert contract["activated_surface_required"] is True
