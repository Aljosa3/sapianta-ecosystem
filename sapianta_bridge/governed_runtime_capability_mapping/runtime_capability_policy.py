"""Governed executable capability policy."""

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


def create_runtime_capability_policy(*, runtime_capability_mapping_id: str) -> dict:
    value = {"runtime_capability_mapping_id": runtime_capability_mapping_id}
    return {
        "runtime_capability_policy_id": f"RUNTIME-CAPABILITY-POLICY-{stable_hash(value)[:24]}",
        **value,
        "dynamic_executor_generation_allowed": False,
        "bounded_executor_required": True,
    }
