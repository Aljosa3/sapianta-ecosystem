"""Governed runtime operation policy artifact."""

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


def create_runtime_operation_policy(*, runtime_operation_envelope_id: str) -> dict:
    value = {"runtime_operation_envelope_id": runtime_operation_envelope_id}
    return {
        "runtime_operation_policy_id": f"RUNTIME-OPERATION-POLICY-{stable_hash(value)[:24]}",
        **value,
        "raw_prompt_to_shell_forbidden": True,
        "bounded_operation_required": True,
    }
