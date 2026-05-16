from sapianta_bridge.governed_runtime_operational_entrypoint.runtime_operational_entrypoint_binding import LINEAGE_FIELDS
from sapianta_bridge.governed_runtime_operational_entrypoint.runtime_operational_entrypoint_validator import validate_runtime_operational_entrypoint


def _artifacts():
    return {
        "session": {"runtime_operational_entrypoint_id": "ENTRY-1", "runtime_execution_realization_id": "REAL-1"},
        "request": {"runtime_operational_entrypoint_request_id": "REQ-1", "runtime_operational_entrypoint_id": "ENTRY-1"},
        "response": {"runtime_operational_entrypoint_response_id": "RESP-1", "runtime_operational_entrypoint_id": "ENTRY-1", "response_return_id": "RETURN-1"},
        "binding": {"runtime_operational_entrypoint_id": "ENTRY-1", **{field: field for field in LINEAGE_FIELDS}},
        "realization_output": {"validation": {"valid": True}, "runtime_execution_realization_evidence": {"runtime_execution_realization_id": "REAL-1"}},
    }


def test_validator_accepts_complete_entrypoint():
    assert validate_runtime_operational_entrypoint(**_artifacts())["valid"] is True


def test_validator_rejects_missing_response_return():
    artifacts = _artifacts()
    artifacts["response"]["response_return_id"] = ""
    assert validate_runtime_operational_entrypoint(**artifacts)["valid"] is False


def test_validator_rejects_identity_drift():
    assert validate_runtime_operational_entrypoint(
        **_artifacts(),
        prior_output={"runtime_operational_entrypoint_session": {"runtime_operational_entrypoint_id": "OTHER"}},
    )["valid"] is False
