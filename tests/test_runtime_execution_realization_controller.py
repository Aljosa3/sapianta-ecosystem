from sapianta_bridge.governed_runtime_execution_realization import create_runtime_execution_realization
from sapianta_bridge.governed_runtime_execution_realization.runtime_execution_realization_binding import LINEAGE_FIELDS


def _activation(surface="GOVERNED_STATE_READ_SURFACE", operational=True):
    return {
        "validation": {"valid": True},
        "runtime_surface_activation_evidence": {
            "runtime_surface_activation_id": "ACT-1",
            "runtime_surface": surface,
            "surface_operational": operational,
        },
    }


def _lineage():
    return {field: field for field in LINEAGE_FIELDS}


def test_controller_authorizes_realization():
    result = create_runtime_execution_realization(
        activation_output=_activation(),
        realization_lineage=_lineage(),
    )
    assert result["validation"]["valid"] is True
    assert result["states"][-1] == "EXECUTION_REALIZATION_FINALIZED"


def test_controller_rejects_unknown_realization_mode():
    result = create_runtime_execution_realization(
        activation_output=_activation(surface="UNKNOWN_SURFACE"),
        realization_lineage=_lineage(),
    )
    assert result["states"] == ["EXECUTION_REALIZATION_REJECTED"]


def test_controller_blocks_missing_activation():
    assert create_runtime_execution_realization(activation_output={}, realization_lineage=_lineage())["states"] == ["BLOCKED"]
