from sapianta_bridge.governed_runtime_operational_entrypoint.runtime_operational_entrypoint_binding import LINEAGE_FIELDS
from sapianta_bridge.governed_runtime_operational_entrypoint.runtime_operational_entrypoint_validator import (
    validate_runtime_operational_entrypoint,
)


def _artifacts():
    return {
        "entrypoint": {"runtime_operational_entrypoint_id": "ENTRY-1", "runtime_execution_realization_id": "REAL-1", "operational_entry_mode": "GOVERNED_OPERATIONAL_RUNTIME_ENTRY"},
        "contract": {"runtime_operational_entrypoint_contract_id": "CONTRACT-1", "runtime_operational_entrypoint_id": "ENTRY-1", "realization_continuity_required": True},
        "transaction": {"runtime_operational_entrypoint_transaction_id": "TX-1", "runtime_operational_entrypoint_id": "ENTRY-1", "runtime_execution_realization_id": "REAL-1", "result_capture_id": "CAPTURE-1", "response_return_id": "RETURN-1"},
        "binding": {"runtime_operational_entrypoint_id": "ENTRY-1", **{field: field for field in LINEAGE_FIELDS}},
        "policy": {"runtime_operational_entrypoint_policy_id": "POLICY-1", "runtime_operational_entrypoint_id": "ENTRY-1", "shell_true_allowed": False, "raw_shell_execution_allowed": False, "unrestricted_subprocess_allowed": False, "runtime_self_expansion_allowed": False},
        "realization_output": {"validation": {"valid": True}, "runtime_execution_realization_evidence": {"runtime_execution_realization_id": "REAL-1"}},
    }


def test_validator_accepts_valid_operational_entrypoint():
    assert validate_runtime_operational_entrypoint(**_artifacts())["valid"] is True


def test_validator_rejects_missing_response_and_forbidden_mode():
    artifacts = _artifacts()
    artifacts["transaction"]["response_return_id"] = ""
    artifacts["entrypoint"]["operational_entry_mode"] = "RAW_RUNTIME_ENTRY"
    assert validate_runtime_operational_entrypoint(**artifacts)["valid"] is False


def test_validator_rejects_identity_drift():
    assert validate_runtime_operational_entrypoint(
        **_artifacts(),
        prior_output={"runtime_operational_entrypoint": {"runtime_operational_entrypoint_id": "OTHER"}},
    )["valid"] is False
