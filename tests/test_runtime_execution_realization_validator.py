from sapianta_bridge.governed_runtime_execution_realization.runtime_execution_realization_binding import LINEAGE_FIELDS
from sapianta_bridge.governed_runtime_execution_realization.runtime_execution_realization_validator import (
    validate_runtime_execution_realization,
)


def _artifacts():
    return {
        "realization": {
            "runtime_execution_realization_id": "REAL-1",
            "runtime_surface_activation_id": "ACT-1",
            "runtime_surface": "GOVERNED_STATE_READ_SURFACE",
            "realization_mode": "STATE_READ_REALIZATION",
        },
        "contract": {"runtime_execution_realization_contract_id": "CONTRACT-1", "runtime_execution_realization_id": "REAL-1", "activated_surface_required": True},
        "transaction": {"runtime_execution_realization_transaction_id": "TX-1", "runtime_execution_realization_id": "REAL-1", "result_capture_id": "CAPTURE-1", "response_return_id": "RETURN-1"},
        "binding": {"runtime_execution_realization_id": "REAL-1", **{field: field for field in LINEAGE_FIELDS}},
        "policy": {
            "runtime_execution_realization_policy_id": "POLICY-1",
            "runtime_execution_realization_id": "REAL-1",
            "shell_true_allowed": False,
            "raw_shell_execution_allowed": False,
            "unrestricted_subprocess_allowed": False,
            "unrestricted_network_execution_allowed": False,
            "autonomous_execution_allowed": False,
        },
        "activation_output": {
            "validation": {"valid": True},
            "runtime_surface_activation_evidence": {"runtime_surface_activation_id": "ACT-1", "surface_operational": True},
        },
    }


def test_validator_accepts_valid_realization():
    assert validate_runtime_execution_realization(**_artifacts())["valid"] is True


def test_validator_rejects_inactive_surface_and_missing_capture_return():
    artifacts = _artifacts()
    artifacts["activation_output"]["runtime_surface_activation_evidence"]["surface_operational"] = False
    artifacts["transaction"]["result_capture_id"] = ""
    artifacts["transaction"]["response_return_id"] = ""
    assert validate_runtime_execution_realization(**artifacts)["valid"] is False


def test_validator_rejects_forbidden_and_mismatched_modes():
    artifacts = _artifacts()
    artifacts["realization"]["realization_mode"] = "RAW_SHELL_REALIZATION"
    assert validate_runtime_execution_realization(**artifacts)["valid"] is False
    artifacts = _artifacts()
    artifacts["realization"]["realization_mode"] = "PYTEST_VALIDATION_REALIZATION"
    assert validate_runtime_execution_realization(**artifacts)["valid"] is False


def test_validator_rejects_shell_and_network_policy_drift():
    artifacts = _artifacts()
    artifacts["policy"]["shell_true_allowed"] = True
    artifacts["policy"]["unrestricted_network_execution_allowed"] = True
    assert validate_runtime_execution_realization(**artifacts)["valid"] is False


def test_validator_rejects_identity_drift():
    assert validate_runtime_execution_realization(
        **_artifacts(),
        prior_output={"runtime_execution_realization": {"runtime_execution_realization_id": "OTHER"}},
    )["valid"] is False
