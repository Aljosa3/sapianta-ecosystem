from sapianta_bridge.governed_local_runtime_bridge.local_runtime_bridge_session import (
    create_local_runtime_bridge_session,
    validate_local_runtime_bridge_session,
)


def test_local_runtime_bridge_session_is_deterministic():
    relay = {"execution_relay_session": {"execution_relay_session_id": "REL-1"}}
    first = create_local_runtime_bridge_session(relay_output=relay, runtime_transport_bridge_id="RTB-1").to_dict()
    second = create_local_runtime_bridge_session(relay_output=relay, runtime_transport_bridge_id="RTB-1").to_dict()
    assert first["local_runtime_bridge_session_id"] == second["local_runtime_bridge_session_id"]
    assert validate_local_runtime_bridge_session(first)["valid"] is True
