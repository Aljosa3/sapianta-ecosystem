from sapianta_bridge.governed_runtime_operation_envelope.runtime_operation_policy import (
    create_runtime_operation_policy,
)


def test_policy_forbids_raw_prompt_to_shell():
    policy = create_runtime_operation_policy(runtime_operation_envelope_id="ENV-1")
    assert policy["raw_prompt_to_shell_forbidden"] is True
    assert policy["bounded_operation_required"] is True
