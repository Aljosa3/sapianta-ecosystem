from sapianta_bridge.governed_runtime_execution_surface import create_runtime_execution_surface
from sapianta_bridge.governed_runtime_execution_surface.runtime_execution_surface_binding import LINEAGE_FIELDS


def _capability(primitive="PYTEST_VALIDATION_EXECUTOR"):
    return {
        "validation": {"valid": True},
        "runtime_capability_evidence": {
            "runtime_capability_mapping_id": "MAP-1",
            "executor_primitive": primitive,
        },
    }


def _lineage():
    return {field: field for field in LINEAGE_FIELDS}


def test_controller_authorizes_static_surface():
    result = create_runtime_execution_surface(capability_output=_capability(), realization_lineage=_lineage())
    assert result["validation"]["valid"] is True
    assert result["runtime_execution_surface"]["runtime_surface"] == "GOVERNED_PYTEST_RUNTIME_SURFACE"


def test_controller_rejects_unknown_surface_realization():
    result = create_runtime_execution_surface(capability_output=_capability("UNKNOWN"), realization_lineage=_lineage())
    assert result["states"] == ["EXECUTION_SURFACE_REJECTED"]


def test_controller_blocks_incomplete_lineage():
    result = create_runtime_execution_surface(capability_output=_capability(), realization_lineage={})
    assert result["states"] == ["BLOCKED"]
