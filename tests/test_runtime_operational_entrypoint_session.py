from sapianta_bridge.governed_runtime_operational_entrypoint.runtime_operational_entrypoint_session import create_runtime_operational_entrypoint_session


def test_session_is_deterministic():
    first = create_runtime_operational_entrypoint_session(runtime_execution_realization_id="REAL-1")
    second = create_runtime_operational_entrypoint_session(runtime_execution_realization_id="REAL-1")
    assert first == second
