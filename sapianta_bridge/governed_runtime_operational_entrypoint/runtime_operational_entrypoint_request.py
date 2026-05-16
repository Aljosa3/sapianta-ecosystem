"""Governed runtime operational entrypoint request."""

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


def create_runtime_operational_entrypoint_request(*, session: dict) -> dict:
    value = {"runtime_operational_entrypoint_id": session["runtime_operational_entrypoint_id"]}
    return {
        "runtime_operational_entrypoint_request_id": f"RUNTIME-OPERATIONAL-ENTRYPOINT-REQUEST-{stable_hash(value)[:24]}",
        **value,
    }
