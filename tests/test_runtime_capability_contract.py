from sapianta_bridge.governed_runtime_capability_mapping.runtime_capability_contract import (
    create_runtime_capability_contract,
)


def test_contract_requires_deterministic_mapping():
    contract = create_runtime_capability_contract(runtime_capability_mapping_id="MAP-1")
    assert contract["deterministic_mapping_required"] is True
