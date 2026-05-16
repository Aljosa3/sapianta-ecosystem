"""Operational ingress boundary semantics."""

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash

ENTRYPOINT_STATES = (
    "ENTRYPOINT_CREATED",
    "ENTRYPOINT_ADMISSION_PENDING",
    "ENTRYPOINT_ADMITTED",
    "ENTRYPOINT_RUNTIME_BOUND",
    "ENTRYPOINT_EXECUTION_LINKED",
    "ENTRYPOINT_RESPONSE_LINKED",
    "ENTRYPOINT_OPERATIONAL_READY",
    "ENTRYPOINT_CLOSED",
    "BLOCKED",
    "FAILED",
)
READY_PATH = ENTRYPOINT_STATES[:7]
CLOSED_PATH = ENTRYPOINT_STATES[:8]

FORBIDDEN_CAPABILITIES = (
    "agents",
    "orchestration",
    "retries",
    "fallback",
    "provider_routing",
    "provider_switching",
    "daemon_workers",
    "distributed_runtimes",
    "websocket_infrastructure",
    "async_background_execution",
    "network_apis",
    "public_server_runtime",
    "frontend_runtime",
    "hidden_execution",
    "hidden_memory",
    "autonomous_continuation",
    "shell_true",
    "unrestricted_subprocess_execution",
)


def create_activation_boundary(*, channel_binding: dict) -> dict:
    value = {
        "runtime_persistent_channel_id": channel_binding["runtime_persistent_channel_id"],
        "runtime_surface_session_id": channel_binding["runtime_surface_session_id"],
    }
    return {
        "runtime_activation_boundary_id": f"RUNTIME-ACTIVATION-BOUNDARY-{stable_hash(value)[:24]}",
        **value,
        "operational_ingress_boundary": True,
        "valid": True,
    }
