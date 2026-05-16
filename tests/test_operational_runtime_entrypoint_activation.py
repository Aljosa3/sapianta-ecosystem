from sapianta_bridge.governed_operational_runtime_entrypoint.operational_runtime_entrypoint_activation import (
    create_entrypoint_activation,
)


def test_activation_is_deterministic():
    boundary = {"runtime_activation_boundary_id": "BOUNDARY-1"}
    contract = {"operational_entry_contract_id": "CONTRACT-1"}
    admission = {"operational_entry_admission_id": "ADMISSION-1"}
    first = create_entrypoint_activation(boundary=boundary, contract=contract, admission=admission)
    second = create_entrypoint_activation(boundary=boundary, contract=contract, admission=admission)
    assert first == second
    assert first["operational_runtime_entrypoint_id"].startswith("OPERATIONAL-RUNTIME-ENTRYPOINT-")
