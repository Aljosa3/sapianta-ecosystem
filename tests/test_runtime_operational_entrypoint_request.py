from sapianta_bridge.governed_runtime_operational_entrypoint.runtime_operational_entrypoint_request import create_runtime_operational_entrypoint_request


def test_request_binds_session():
    request = create_runtime_operational_entrypoint_request(session={"runtime_operational_entrypoint_id": "ENTRY-1"})
    assert request["runtime_operational_entrypoint_id"] == "ENTRY-1"
