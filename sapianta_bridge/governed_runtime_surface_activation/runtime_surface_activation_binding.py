"""Governed runtime surface activation lineage binding."""

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash

from sapianta_bridge.governed_runtime_execution_surface.runtime_execution_surface_binding import LINEAGE_FIELDS


def create_runtime_surface_activation_binding(*, activation_id: str, surface_output: dict) -> dict:
    surface_binding = surface_output["runtime_execution_surface_binding"]
    value = {
        "runtime_surface_activation_id": activation_id,
        "runtime_execution_surface_id": surface_binding["runtime_execution_surface_id"],
        **{field: surface_binding[field] for field in LINEAGE_FIELDS},
    }
    return {**value, "binding_sha256": stable_hash(value)}
