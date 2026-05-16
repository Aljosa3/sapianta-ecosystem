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
    required = set(LINEAGE_FIELDS) - {
        "runtime_execution_realization_id",
        "runtime_execution_commit_id",
        "execution_relay_session_id",
        "execution_exchange_session_id",
        "result_capture_id",
        "response_return_id",
    }
    return {field: field for field in required}


def test_controller_admits_operational_entry():
    result = create_runtime_operational_entrypoint(
        realization_output=_realization(),
        operational_entry_mode="GOVERNED_OPERATIONAL_RUNTIME_ENTRY",
        supplemental_lineage=_supplemental(),
    )
    assert result["validation"]["valid"] is True
    assert result["states"] == ["OPERATIONAL_ENTRYPOINT_ADMITTED"]


def test_controller_rejects_forbidden_mode():
    result = create_runtime_operational_entrypoint(
        realization_output=_realization(),
        operational_entry_mode="RAW_RUNTIME_ENTRY",
        supplemental_lineage=_supplemental(),
    )
    assert result["states"] == ["OPERATIONAL_ENTRYPOINT_REJECTED"]


def test_controller_blocks_incomplete_linkage():
    assert create_runtime_operational_entrypoint(
        realization_output={},
        operational_entry_mode="GOVERNED_OPERATIONAL_RUNTIME_ENTRY",
        supplemental_lineage={},
    )["states"] == ["BLOCKED"]
