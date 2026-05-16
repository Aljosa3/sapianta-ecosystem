from sapianta_bridge.governed_runtime_execution_realization.runtime_execution_realization_policy import (
    create_runtime_execution_realization_policy,
)


def test_policy_forbids_unbounded_execution():
    policy = create_runtime_execution_realization_policy(runtime_execution_realization_id="REAL-1")
    assert policy["shell_true_allowed"] is False
    assert policy["unrestricted_network_execution_allowed"] is False
