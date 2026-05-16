from sapianta_bridge.governed_runtime_execution_surface.runtime_execution_surface_policy import (
    create_runtime_execution_surface_policy,
)


def test_policy_forbids_unrestricted_execution():
    policy = create_runtime_execution_surface_policy(runtime_execution_surface_id="SURFACE-1")
    assert policy["shell_true_allowed"] is False
    assert policy["raw_shell_execution_allowed"] is False
    assert policy["unrestricted_network_execution_allowed"] is False
