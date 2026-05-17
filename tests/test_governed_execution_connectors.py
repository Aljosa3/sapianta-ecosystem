from copy import deepcopy

from sapianta_system.runtime.connectors import execute_governed_connector
from sapianta_system.runtime.connectors.governed_execution_connector import register_governed_connector
from sapianta_system.runtime.connectors.governed_connector_validator import validate_connector_result


def _transport(surface="GOVERNED_PYTEST_RUNTIME_SURFACE"):
    return {
        "transport_status": "COMPLETED",
        "request": {
            "governed_transport_request_id": "REQ-1",
            "replay_identity": "REPLAY-1",
        },
        "response": {
            "result_payload": {
                "runtime_surface": surface,
            }
        },
    }


def test_connector_identity_is_deterministic():
    first = register_governed_connector(connector_name="local_execution")
    second = register_governed_connector(connector_name="local_execution")
    assert first["connector_id"] == second["connector_id"]
    assert first["registration_sha256"] == second["registration_sha256"]


def test_connector_handoff_and_result_are_deterministic():
    first = execute_governed_connector(connector_name="local_execution", transport_output=_transport())
    second = execute_governed_connector(connector_name="local_execution", transport_output=_transport())
    assert first["connector_status"] == "COMPLETED"
    assert first["envelope"]["connector_envelope_id"] == second["envelope"]["connector_envelope_id"]
    assert first["result"]["connector_result_id"] == second["result"]["connector_result_id"]
    assert first["evidence"]["replay_safe"] is True


def test_connector_blocks_unregistered_connector():
    assert execute_governed_connector(connector_name="unknown", transport_output=_transport())["connector_status"] == "BLOCKED"


def test_connector_blocks_invalid_surface():
    assert execute_governed_connector(
        connector_name="codex_execution",
        transport_output=_transport("GOVERNED_PYTEST_RUNTIME_SURFACE"),
    )["connector_status"] == "BLOCKED"


def test_connector_blocks_unauthorized_execution():
    assert execute_governed_connector(
        connector_name="local_execution",
        transport_output=_transport(),
        authorized_execution=False,
    )["connector_status"] == "BLOCKED"


def test_connector_blocks_malformed_envelope_input():
    assert execute_governed_connector(
        connector_name="local_execution",
        transport_output={"transport_status": "COMPLETED"},
    )["connector_status"] == "BLOCKED"


def test_connector_result_validation_rejects_replay_mismatch():
    output = execute_governed_connector(connector_name="local_execution", transport_output=_transport())
    broken = deepcopy(output["result"])
    broken["replay_identity"] = "MISMATCH"
    assert validate_connector_result(result=broken, envelope=output["envelope"])["valid"] is False


def test_connector_lineage_and_boundary_evidence_are_preserved():
    output = execute_governed_connector(connector_name="local_execution", transport_output=_transport())
    evidence = output["evidence"]
    assert evidence["governed_transport_request_id"] == "REQ-1"
    assert evidence["lineage_preserved"] is True
    assert evidence["orchestration_present"] is False
    assert evidence["retry_present"] is False
    assert evidence["fallback_present"] is False
