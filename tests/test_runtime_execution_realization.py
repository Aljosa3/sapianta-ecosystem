from sapianta_bridge.governed_runtime_execution_realization.runtime_execution_realization import (
    ALLOWED_REALIZATION_MODES,
    create_runtime_execution_realization_record,
)


def test_realization_modes_are_deterministic():
    for surface, mode in ALLOWED_REALIZATION_MODES.items():
        realization = create_runtime_execution_realization_record(
            activation_evidence={"runtime_surface_activation_id": "ACT-1", "runtime_surface": surface}
        )
        assert realization["realization_mode"] == mode
