from sapianta_bridge.governed_runtime_surface_activation.runtime_surface_activation_policy import (
    create_runtime_surface_activation_policy,
)


def test_policy_forbids_adaptive_activation():
    policy = create_runtime_surface_activation_policy(runtime_surface_activation_id="ACT-1")
    assert policy["adaptive_activation_allowed"] is False
