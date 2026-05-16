from sapianta_bridge.governed_runtime_execution_surface.runtime_execution_surface_binding import LINEAGE_FIELDS
from sapianta_bridge.governed_runtime_execution_surface.runtime_execution_surface_validator import (
    validate_runtime_execution_surface,
)


def _artifacts():
    return {
        "surface_record": {
            "runtime_execution_surface_id": "SURFACE-1",
            "executor_primitive": "GOVERNED_STATE_READER",
            "runtime_surface": "GOVERNED_STATE_READ_SURFACE",
        },
        "contract": {"runtime_execution_surface_contract_id": "CONTRACT-1", "runtime_execution_surface_id": "SURFACE-1", "static_surface_required": True},
        "binding": {"runtime_execution_surface_id": "SURFACE-1", **{field: field for field in LINEAGE_FIELDS}},
        "executor": {
            "runtime_execution_surface_executor_id": "EXEC-1",
            "runtime_execution_surface_id": "SURFACE-1",
            "executor_primitive": "GOVERNED_STATE_READER",
            "runtime_surface": "GOVERNED_STATE_READ_SURFACE",
        },
        "policy": {
            "runtime_execution_surface_policy_id": "POLICY-1",
            "runtime_execution_surface_id": "SURFACE-1",
            "dynamic_surface_inference_allowed": False,
            "shell_true_allowed": False,
            "raw_shell_execution_allowed": False,
            "unrestricted_subprocess_allowed": False,
            "unrestricted_network_execution_allowed": False,
        },
        "capability_output": {
            "validation": {"valid": True},
            "runtime_capability_evidence": {"executor_primitive": "GOVERNED_STATE_READER"},
        },
    }


def test_validator_accepts_valid_surface():
    assert validate_runtime_execution_surface(**_artifacts())["valid"] is True


def test_validator_rejects_executor_surface_mismatch():
    artifacts = _artifacts()
    artifacts["surface_record"]["runtime_surface"] = "GOVERNED_PYTEST_RUNTIME_SURFACE"
    assert validate_runtime_execution_surface(**artifacts)["valid"] is False


def test_validator_rejects_forbidden_surface():
    artifacts = _artifacts()
    artifacts["surface_record"]["runtime_surface"] = "RAW_SHELL_RUNTIME_SURFACE"
    assert validate_runtime_execution_surface(**artifacts)["valid"] is False


def test_validator_rejects_surface_drift():
    assert validate_runtime_execution_surface(
        **_artifacts(),
        prior_output={"runtime_execution_surface": {"runtime_execution_surface_id": "OTHER"}},
    )["valid"] is False
