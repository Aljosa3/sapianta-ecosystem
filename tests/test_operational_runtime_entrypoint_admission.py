from sapianta_bridge.governed_operational_runtime_entrypoint.operational_runtime_entrypoint_admission import (
    create_entry_admission,
)


def test_admission_is_explicit_and_deterministic():
    contract = {"operational_entry_contract_id": "CONTRACT-1"}
    first = create_entry_admission(contract=contract, admitted=True, approved_by="human")
    second = create_entry_admission(contract=contract, admitted=True, approved_by="human")
    assert first == second
    assert first["admitted"] is True
    assert first["approved_by"] == "human"
