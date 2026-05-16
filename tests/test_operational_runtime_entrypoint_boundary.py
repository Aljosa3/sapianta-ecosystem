from sapianta_bridge.governed_operational_runtime_entrypoint.operational_runtime_entrypoint_boundary import (
    ENTRYPOINT_STATES,
    FORBIDDEN_CAPABILITIES,
    create_activation_boundary,
)


def test_boundary_marks_operational_ingress():
    boundary = create_activation_boundary(
        channel_binding={"runtime_persistent_channel_id": "CHANNEL-1", "runtime_surface_session_id": "SURFACE-1"}
    )
    assert boundary["operational_ingress_boundary"] is True
    assert boundary["runtime_activation_boundary_id"].startswith("RUNTIME-ACTIVATION-BOUNDARY-")


def test_boundary_states_and_forbidden_capabilities_are_explicit():
    assert "ENTRYPOINT_OPERATIONAL_READY" in ENTRYPOINT_STATES
    assert "shell_true" in FORBIDDEN_CAPABILITIES
