"""Governed execution realization lineage binding."""

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash

LINEAGE_FIELDS = (
    "runtime_surface_activation_id",
    "runtime_execution_surface_id",
    "runtime_capability_mapping_id",
    "runtime_operation_envelope_id",
    "runtime_activation_gate_id",
    "operational_runtime_entrypoint_id",
    "runtime_persistent_channel_id",
    "direct_runtime_interaction_session_id",
    "runtime_surface_session_id",
    "execution_exchange_session_id",
    "execution_relay_session_id",
    "runtime_execution_commit_id",
    "runtime_delivery_finalization_id",
    "governed_session_id",
    "execution_gate_id",
    "provider_invocation_id",
    "bounded_runtime_id",
    "result_capture_id",
    "response_return_id",
)


def create_runtime_execution_realization_binding(
    *,
    runtime_execution_realization_id: str,
    realization_lineage: dict,
) -> dict:
    value = {
        "runtime_execution_realization_id": runtime_execution_realization_id,
        **{field: realization_lineage[field] for field in LINEAGE_FIELDS},
    }
    return {**value, "binding_sha256": stable_hash(value)}
