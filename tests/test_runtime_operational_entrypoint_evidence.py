from sapianta_bridge.governed_runtime_operational_entrypoint.runtime_operational_entrypoint_binding import LINEAGE_FIELDS
from sapianta_bridge.governed_runtime_operational_entrypoint.runtime_operational_entrypoint_evidence import (
    runtime_operational_entrypoint_evidence,
)


def test_evidence_is_replay_visible():
    evidence = runtime_operational_entrypoint_evidence(
        entrypoint={"runtime_operational_entrypoint_id": "ENTRY-1", "operational_entry_mode": "GOVERNED_OPERATIONAL_RUNTIME_ENTRY"},
        contract={"runtime_operational_entrypoint_contract_id": "CONTRACT-1"},
        transaction={"runtime_operational_entrypoint_transaction_id": "TX-1"},
        binding={field: field for field in LINEAGE_FIELDS},
        policy={"runtime_operational_entrypoint_policy_id": "POLICY-1"},
        valid=True,
    )
    assert evidence["operational_entry_admitted"] is True
    assert evidence["runtime_execution_realization_id"] == "runtime_execution_realization_id"
