"""Replay-visible runtime surface evidence."""
from .runtime_surface_binding import LINEAGE_SOURCE_FIELDS
FIELDS = ("runtime_surface_session_id","surface_ingress_id","surface_egress_id", *LINEAGE_SOURCE_FIELDS)
def runtime_surface_evidence(*, binding: dict, valid: bool, states: tuple[str, ...]) -> dict:
    return {**{field: binding.get(field,"") for field in FIELDS}, "states": list(states), "replay_safe": valid, "operational_surface_integrity": valid, "continuity_fabricated": False, "hidden_provider_memory_trusted": False}
