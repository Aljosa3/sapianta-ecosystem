from sapianta_bridge.governed_runtime_capability_mapping.runtime_capability_executor import (
    create_runtime_capability_executor,
)


def test_executor_preserves_primitive():
    executor = create_runtime_capability_executor(
        runtime_capability_mapping_id="MAP-1", executor_primitive="GOVERNED_STATE_READER"
    )
    assert executor["executor_primitive"] == "GOVERNED_STATE_READER"
