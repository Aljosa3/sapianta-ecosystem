from sapianta_bridge.governed_runtime_operational_entrypoint.runtime_operational_entrypoint import (
    ALLOWED_OPERATIONAL_ENTRY_MODES,
    create_runtime_operational_entrypoint_record,
)


def test_allowed_modes_create_deterministic_entrypoints():
    for mode in ALLOWED_OPERATIONAL_ENTRY_MODES:
        record = create_runtime_operational_entrypoint_record(
            realization_evidence={"runtime_execution_realization_id": "REAL-1"},
            operational_entry_mode=mode,
        )
        assert record["operational_entry_mode"] == mode
