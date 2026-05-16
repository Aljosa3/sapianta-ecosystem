"""Replay-visible governed runtime operational entrypoint evidence."""

from .runtime_operational_entrypoint_binding import LINEAGE_FIELDS


def runtime_operational_entrypoint_evidence(
    *,
    session: dict,
    request: dict,
    response: dict,
    binding: dict,
    valid: bool,
    states: tuple[str, ...],
) -> dict:
    return {
        "runtime_operational_entrypoint_id": session.get("runtime_operational_entrypoint_id", ""),
        "runtime_operational_entrypoint_request_id": request.get("runtime_operational_entrypoint_request_id", ""),
        "runtime_operational_entrypoint_response_id": response.get("runtime_operational_entrypoint_response_id", ""),
        "runtime_operational_entrypoint_binding_id": binding.get("runtime_operational_entrypoint_binding_id", ""),
        "runtime_operational_entrypoint_controller_id": f"RUNTIME-OPERATIONAL-ENTRYPOINT-CONTROLLER-{session.get('runtime_operational_entrypoint_id', '')}",
        **{field: binding.get(field, "") for field in LINEAGE_FIELDS},
        "states": list(states),
        "operational_entry_finalized": valid,
        "replay_safe": valid,
        "continuity_fabricated": False,
    }
