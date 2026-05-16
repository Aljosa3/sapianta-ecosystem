from sapianta_bridge.governed_runtime_execution_realization.runtime_execution_realization_binding import LINEAGE_FIELDS
from sapianta_bridge.governed_runtime_execution_realization.runtime_execution_realization_evidence import (
    runtime_execution_realization_evidence,
)


def test_evidence_distinguishes_activation_from_realization():
    evidence = runtime_execution_realization_evidence(
        realization={"runtime_execution_realization_id": "REAL-1", "realization_mode": "STATE_READ_REALIZATION"},
        contract={"runtime_execution_realization_contract_id": "CONTRACT-1"},
        transaction={"runtime_execution_realization_transaction_id": "TX-1"},
        binding={field: field for field in LINEAGE_FIELDS},
        policy={"runtime_execution_realization_policy_id": "POLICY-1"},
        valid=True,
        states=("EXECUTION_REALIZATION_FINALIZED",),
    )
    assert evidence["surface_activation_is_execution_realization"] is False
    assert evidence["result_capture_id"] == "result_capture_id"
