from sapianta_bridge.governed_runtime_surface_activation.runtime_surface_activation_contract import (
    create_runtime_surface_activation_contract,
)


def test_contract_requires_surface_validation():
    contract = create_runtime_surface_activation_contract(runtime_surface_activation_id="ACT-1")
    assert contract["surface_validation_required"] is True
