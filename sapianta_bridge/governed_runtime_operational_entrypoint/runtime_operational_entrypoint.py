"""Governed runtime operational entrypoint record."""

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash

ALLOWED_OPERATIONAL_ENTRY_MODES = (
    "GOVERNED_OPERATIONAL_RUNTIME_ENTRY",
    "GOVERNED_RUNTIME_TRANSACTION_ENTRY",
    "GOVERNED_RUNTIME_RESPONSE_ENTRY",
    "GOVERNED_RUNTIME_VALIDATION_ENTRY",
    "GOVERNED_RUNTIME_EXECUTION_ENTRY",
)
FORBIDDEN_OPERATIONAL_ENTRY_MODES = (
    "RAW_RUNTIME_ENTRY",
    "AUTONOMOUS_RUNTIME_ENTRY",
    "BACKGROUND_RUNTIME_ENTRY",
    "ASYNC_RUNTIME_ENTRY",
    "NETWORK_RUNTIME_ENTRY",
    "DISTRIBUTED_RUNTIME_ENTRY",
    "SELF_MODIFYING_RUNTIME_ENTRY",
    "DAEMON_RUNTIME_ENTRY",
    "RAW_SHELL_ENTRY",
    "UNRESTRICTED_SUBPROCESS_ENTRY",
    "PROVIDER_SWITCH_ENTRY",
    "AGENT_RUNTIME_ENTRY",
)


def create_runtime_operational_entrypoint_record(*, realization_evidence: dict, operational_entry_mode: str) -> dict:
    value = {
        "runtime_execution_realization_id": realization_evidence["runtime_execution_realization_id"],
        "operational_entry_mode": operational_entry_mode,
    }
    return {
        "runtime_operational_entrypoint_id": f"RUNTIME-OPERATIONAL-ENTRYPOINT-{stable_hash(value)[:24]}",
        **value,
    }
