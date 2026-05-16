from sapianta_bridge.governed_runtime_operational_entrypoint.runtime_operational_entrypoint_contract import (
    create_runtime_operational_entrypoint_contract,
)


def test_contract_requires_realization_continuity():
    contract = create_runtime_operational_entrypoint_contract(runtime_operational_entrypoint_id="ENTRY-1")
    assert contract["realization_continuity_required"] is True
