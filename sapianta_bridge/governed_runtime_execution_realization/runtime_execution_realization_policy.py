"""Governed execution realization policy."""

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


def create_runtime_execution_realization_policy(*, runtime_execution_realization_id: str) -> dict:
    value = {"runtime_execution_realization_id": runtime_execution_realization_id}
    return {
        "runtime_execution_realization_policy_id": f"RUNTIME-EXECUTION-REALIZATION-POLICY-{stable_hash(value)[:24]}",
        **value,
        "shell_true_allowed": False,
        "raw_shell_execution_allowed": False,
        "unrestricted_subprocess_allowed": False,
        "unrestricted_network_execution_allowed": False,
        "autonomous_execution_allowed": False,
    }
