from sapianta_bridge.governed_runtime_execution_surface.runtime_execution_surface_contract import (
    create_runtime_execution_surface_contract,
)


def test_contract_requires_static_surface():
    contract = create_runtime_execution_surface_contract(runtime_execution_surface_id="SURFACE-1")
    assert contract["static_surface_required"] is True
