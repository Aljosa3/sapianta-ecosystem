from sapianta_bridge.governed_runtime_operational_entrypoint.runtime_operational_entrypoint_response import create_runtime_operational_entrypoint_response


def test_response_binds_return_continuity():
    response = create_runtime_operational_entrypoint_response(
        session={"runtime_operational_entrypoint_id": "ENTRY-1"},
        binding={"response_return_id": "RETURN-1"},
    )
    assert response["response_return_id"] == "RETURN-1"
