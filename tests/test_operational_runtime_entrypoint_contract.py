from sapianta_bridge.governed_operational_runtime_entrypoint.operational_runtime_entrypoint_contract import (
    create_entry_contract,
)


def test_contract_records_governed_operational_intent():
    contract = create_entry_contract(
        boundary={"runtime_activation_boundary_id": "BOUNDARY-1"},
        operational_intent="bounded_runtime_entry",
    )
    assert contract["operational_entry_contract_id"].startswith("OPERATIONAL-ENTRY-CONTRACT-")
    assert contract["operational_ingress_governed"] is True
    assert contract["replay_safe"] is True
