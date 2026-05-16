"""Governed runtime execution surface lineage binding."""

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash

LINEAGE_FIELDS = (
    "runtime_execution_commit_id",
    "execution_relay_session_id",
    "execution_exchange_session_id",
    "live_request_ingestion_session_id",
    "serving_gateway_session_id",
    "runtime_serving_session_id",
    "terminal_attachment_session_id",
    "session_runtime_id",
    "interaction_loop_session_id",
    "interaction_turn_id",
    "live_runtime_session_id",
    "runtime_attachment_session_id",
    "transport_session_id",
    "governed_session_id",
    "execution_gate_id",
    "provider_invocation_id",
    "bounded_runtime_id",
    "result_capture_id",
    "response_return_id",
)


def create_runtime_execution_surface_binding(
    *,
    runtime_execution_surface_id: str,
    realization_lineage: dict,
) -> dict:
    value = {
        "runtime_execution_surface_id": runtime_execution_surface_id,
        **{field: realization_lineage[field] for field in LINEAGE_FIELDS},
    }
    return {**value, "binding_sha256": stable_hash(value)}
