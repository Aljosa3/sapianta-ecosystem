from sapianta_bridge.governed_operational_runtime_entrypoint.operational_runtime_entrypoint_evidence import (
    operational_entrypoint_evidence,
)


def test_evidence_records_operational_ingress_and_boundaries():
    evidence = operational_entrypoint_evidence(
        activation={"operational_runtime_entrypoint_id": "ENTRYPOINT-1"},
        boundary={"runtime_activation_boundary_id": "BOUNDARY-1"},
        contract={"operational_entry_contract_id": "CONTRACT-1", "operational_ingress_governed": True},
        admission={"operational_entry_admission_id": "ADMISSION-1", "admitted": True, "approved_by": "human"},
        binding={},
        valid=True,
        states=("ENTRYPOINT_CREATED",),
        closed=False,
    )
    assert evidence["operational_ingress_governed"] is True
    assert evidence["operational_activation_authorized"] is True
    assert evidence["continuity_fabricated"] is False
    assert evidence["shell_true_introduced"] is False
