"""Fail-closed governed runtime surface validation."""
from typing import Any
from .runtime_surface_session import validate_runtime_surface_session

LINEAGE_FIELDS = ("runtime_surface_session_id","surface_ingress_id","surface_egress_id",
    "interaction_loop_session_id","interaction_turn_id","live_runtime_session_id","runtime_attachment_session_id",
    "session_runtime_id","runtime_serving_session_id","terminal_attachment_session_id","serving_gateway_session_id",
    "live_request_ingestion_session_id","execution_exchange_session_id","execution_relay_session_id",
    "runtime_execution_commit_id","runtime_delivery_finalization_id","transport_session_id","governed_session_id",
    "execution_gate_id","provider_invocation_id","bounded_runtime_id","result_capture_id","response_return_id",
    "stdin_relay_id","stdout_relay_id","runtime_transport_bridge_id","runtime_activation_gate_id","local_runtime_bridge_session_id")

def validate_runtime_surface(*, surface_session: dict, binding: dict, finalization_output: dict, prior_output: dict | None = None) -> dict[str, Any]:
    errors = list(validate_runtime_surface_session(surface_session)["errors"])
    if finalization_output.get("validation", {}).get("valid") is not True:
        errors.append({"field":"runtime_delivery_finalization","reason":"delivery finalization continuity absent"})
    fb = finalization_output.get("runtime_delivery_finalization_binding", {})
    if fb.get("runtime_delivery_finalization_id") != surface_session.get("runtime_delivery_finalization_id"):
        errors.append({"field":"runtime_delivery_finalization_id","reason":"finalization linkage mismatch"})
    if prior_output is not None and prior_output.get("runtime_surface_session",{}).get("runtime_surface_session_id") != surface_session.get("runtime_surface_session_id"):
        errors.append({"field":"runtime_surface_session_id","reason":"runtime surface identity changed"})
    for field in LINEAGE_FIELDS:
        if not isinstance(binding.get(field), str) or not binding[field].strip():
            errors.append({"field":field,"reason":"runtime surface lineage missing"})
    return {"valid": not errors, "errors": errors}
