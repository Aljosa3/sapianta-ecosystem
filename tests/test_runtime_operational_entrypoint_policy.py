from sapianta_bridge.governed_runtime_operational_entrypoint.runtime_operational_entrypoint_policy import (
    create_runtime_operational_entrypoint_policy,
)


def test_policy_forbids_expansion():
    policy = create_runtime_operational_entrypoint_policy(runtime_operational_entrypoint_id="ENTRY-1")
    assert policy["runtime_self_expansion_allowed"] is False
