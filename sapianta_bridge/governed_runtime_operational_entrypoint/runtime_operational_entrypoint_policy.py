"""Governed runtime operational entrypoint policy."""

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


def create_runtime_operational_entrypoint_policy(*, runtime_operational_entrypoint_id: str) -> dict:
    value = {"runtime_operational_entrypoint_id": runtime_operational_entrypoint_id}
    return {
        "runtime_operational_entrypoint_policy_id": f"RUNTIME-OPERATIONAL-ENTRYPOINT-POLICY-{stable_hash(value)[:24]}",
        **value,
        "shell_true_allowed": False,
        "raw_shell_execution_allowed": False,
        "unrestricted_subprocess_allowed": False,
        "runtime_self_expansion_allowed": False,
    }
