"""Governed runtime capability executor primitive."""

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


def create_runtime_capability_executor(*, runtime_capability_mapping_id: str, executor_primitive: str) -> dict:
    value = {
        "runtime_capability_mapping_id": runtime_capability_mapping_id,
        "executor_primitive": executor_primitive,
    }
    return {
        "runtime_capability_executor_id": f"RUNTIME-CAPABILITY-EXECUTOR-{stable_hash(value)[:24]}",
        **value,
    }
