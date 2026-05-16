"""Governed runtime operational entrypoint response."""

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


def create_runtime_operational_entrypoint_response(*, session: dict, binding: dict) -> dict:
    value = {
        "runtime_operational_entrypoint_id": session["runtime_operational_entrypoint_id"],
        "response_return_id": binding["response_return_id"],
    }
    return {
        "runtime_operational_entrypoint_response_id": f"RUNTIME-OPERATIONAL-ENTRYPOINT-RESPONSE-{stable_hash(value)[:24]}",
        **value,
    }
