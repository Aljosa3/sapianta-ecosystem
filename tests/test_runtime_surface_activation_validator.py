from sapianta_bridge.governed_runtime_execution_surface.runtime_execution_surface_binding import LINEAGE_FIELDS
from sapianta_bridge.governed_runtime_surface_activation.runtime_surface_activation_gate import OPERATIONAL_PATH
from sapianta_bridge.governed_runtime_surface_activation.runtime_surface_activation_validator import (
    validate_runtime_surface_activation,
)


def _artifacts():
    return {
        "activation": {
            "runtime_surface_activation_id": "ACT-1",
            "runtime_execution_surface_id": "SURFACE-1",
            "runtime_surface": "GOVERNED_STATE_READ_SURFACE",
        },
        "contract": {"runtime_surface_activation_contract_id": "CONTRACT-1", "runtime_surface_activation_id": "ACT-1", "surface_validation_required": True},
        "binding": {"runtime_surface_activation_id": "ACT-1", "runtime_execution_surface_id": "SURFACE-1", **{field: field for field in LINEAGE_FIELDS}},
        "policy": {
            "runtime_surface_activation_policy_id": "POLICY-1",
            "runtime_surface_activation_id": "ACT-1",
            "adaptive_activation_allowed": False,
            "shell_true_allowed": False,
            "raw_shell_execution_allowed": False,
            "unrestricted_subprocess_allowed": False,
            "unrestricted_network_execution_allowed": False,
        },
        "surface_output": {"validation": {"valid": True}, "runtime_execution_surface": {"runtime_execution_surface_id": "SURFACE-1"}},
        "states": OPERATIONAL_PATH,
    }


def test_validator_accepts_valid_activation():
    assert validate_runtime_surface_activation(**_artifacts())["valid"] is True


def test_validator_rejects_forbidden_transition_and_surface():
    artifacts = _artifacts()
    artifacts["states"] = ("SURFACE_REGISTERED", "SURFACE_VALIDATED")
    artifacts["activation"]["runtime_surface"] = "RAW_SHELL_RUNTIME_SURFACE"
    assert validate_runtime_surface_activation(**artifacts)["valid"] is False


def test_validator_rejects_activation_drift():
    assert validate_runtime_surface_activation(
        **_artifacts(),
        prior_output={"runtime_surface_activation": {"runtime_surface_activation_id": "OTHER"}},
    )["valid"] is False
