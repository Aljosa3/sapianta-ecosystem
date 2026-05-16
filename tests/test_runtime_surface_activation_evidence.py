from sapianta_bridge.governed_runtime_execution_surface.runtime_execution_surface_binding import LINEAGE_FIELDS
from sapianta_bridge.governed_runtime_surface_activation.runtime_surface_activation_evidence import (
    runtime_surface_activation_evidence,
)


def test_evidence_records_operational_surface():
    evidence = runtime_surface_activation_evidence(
        activation={"runtime_surface_activation_id": "ACT-1", "runtime_execution_surface_id": "SURFACE-1", "runtime_surface": "GOVERNED_STATE_READ_SURFACE"},
        contract={"runtime_surface_activation_contract_id": "CONTRACT-1"},
        binding={field: field for field in LINEAGE_FIELDS},
        policy={"runtime_surface_activation_policy_id": "POLICY-1"},
        valid=True,
        states=("SURFACE_OPERATIONAL",),
    )
    assert evidence["surface_operational"] is True
    assert evidence["replay_safe"] is True
