from sapianta_bridge.governed_runtime_execution_surface.runtime_execution_surface_binding import LINEAGE_FIELDS
from sapianta_bridge.governed_runtime_execution_surface.runtime_execution_surface_evidence import (
    runtime_execution_surface_evidence,
)


def test_evidence_is_replay_visible():
    evidence = runtime_execution_surface_evidence(
        surface_record={"runtime_execution_surface_id": "SURFACE-1", "executor_primitive": "GOVERNED_STATE_READER", "runtime_surface": "GOVERNED_STATE_READ_SURFACE"},
        contract={"runtime_execution_surface_contract_id": "CONTRACT-1"},
        binding={field: field for field in LINEAGE_FIELDS},
        executor={"runtime_execution_surface_executor_id": "EXEC-1"},
        policy={"runtime_execution_surface_policy_id": "POLICY-1"},
        valid=True,
        states=("EXECUTION_SURFACE_AUTHORIZED",),
    )
    assert evidence["runtime_execution_commit_id"] == "runtime_execution_commit_id"
    assert evidence["replay_safe"] is True
