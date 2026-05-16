"""Governed executable surface declaration."""

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


def create_runtime_capability_surface(*, runtime_capability_mapping_id: str) -> dict:
    value = {"runtime_capability_mapping_id": runtime_capability_mapping_id}
    return {
        "runtime_capability_surface_id": f"RUNTIME-CAPABILITY-SURFACE-{stable_hash(value)[:24]}",
        **value,
        "raw_shell_execution_allowed": False,
        "unrestricted_subprocess_allowed": False,
        "unrestricted_network_execution_allowed": False,
    }
