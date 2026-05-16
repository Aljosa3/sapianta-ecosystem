"""Governed runtime surface activation policy."""

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


def create_runtime_surface_activation_policy(*, runtime_surface_activation_id: str) -> dict:
    value = {"runtime_surface_activation_id": runtime_surface_activation_id}
    return {
        "runtime_surface_activation_policy_id": f"RUNTIME-SURFACE-ACTIVATION-POLICY-{stable_hash(value)[:24]}",
        **value,
        "adaptive_activation_allowed": False,
        "shell_true_allowed": False,
        "raw_shell_execution_allowed": False,
        "unrestricted_subprocess_allowed": False,
        "unrestricted_network_execution_allowed": False,
    }
