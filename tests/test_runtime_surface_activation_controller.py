from sapianta_bridge.governed_runtime_execution_surface.runtime_execution_surface_binding import LINEAGE_FIELDS
from sapianta_bridge.governed_runtime_surface_activation import create_runtime_surface_activation


def _surface():
    return {
        "validation": {"valid": True},
        "runtime_execution_surface": {
            "runtime_execution_surface_id": "SURFACE-1",
            "runtime_surface": "GOVERNED_STATE_READ_SURFACE",
        },
        "runtime_execution_surface_binding": {
            "runtime_execution_surface_id": "SURFACE-1",
            **{field: field for field in LINEAGE_FIELDS},
        },
    }


def test_controller_reaches_operational_state():
    result = create_runtime_surface_activation(surface_output=_surface())
    assert result["validation"]["valid"] is True
    assert result["states"][-1] == "SURFACE_OPERATIONAL"


def test_controller_blocks_incomplete_surface():
    assert create_runtime_surface_activation(surface_output={})["states"] == ["BLOCKED"]
