from sapianta_bridge.governed_runtime_operational_entrypoint import create_runtime_operational_entrypoint
from sapianta_bridge.governed_runtime_operational_entrypoint.runtime_operational_entrypoint_binding import LINEAGE_FIELDS


def _realization():
    return {
        "validation": {"valid": True},
        "runtime_execution_realization_evidence": {
            "runtime_execution_realization_id": "REAL-1",
            "runtime_execution_commit_id": "COMMIT-1",
            "execution_relay_session_id": "RELAY-1",
            "execution_exchange_session_id": "EXCHANGE-1",
            "result_capture_id": "CAPTURE-1",
            "response_return_id": "RETURN-1",
        },
    }


def _supplemental():
    missing = set(LINEAGE_FIELDS) - {
        "runtime_execution_realization_id",
        "runtime_execution_commit_id",
        "execution_relay_session_id",
        "execution_exchange_session_id",
        "result_capture_id",
        "response_return_id",
    }
    return {field: field for field in missing}


def test_controller_finalizes_unified_operational_entry():
    result = create_runtime_operational_entrypoint(realization_output=_realization(), supplemental_lineage=_supplemental())
    assert result["validation"]["valid"] is True
    assert result["states"][-1] == "RUNTIME_OPERATIONAL_ENTRY_FINALIZED"


def test_controller_blocks_missing_realization():
    assert create_runtime_operational_entrypoint(realization_output={}, supplemental_lineage={})["states"] == ["BLOCKED"]
