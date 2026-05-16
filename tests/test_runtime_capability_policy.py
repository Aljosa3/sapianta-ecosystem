from sapianta_bridge.governed_runtime_capability_mapping.runtime_capability_policy import (
    create_runtime_capability_policy,
)


def test_policy_disallows_dynamic_executor_generation():
    policy = create_runtime_capability_policy(runtime_capability_mapping_id="MAP-1")
    assert policy["dynamic_executor_generation_allowed"] is False
