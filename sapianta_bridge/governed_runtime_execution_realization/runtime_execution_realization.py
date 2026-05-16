"""Governed bounded execution realization record."""

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash

ALLOWED_REALIZATION_MODES = {
    "GOVERNED_PYTEST_RUNTIME_SURFACE": "PYTEST_VALIDATION_REALIZATION",
    "GOVERNED_ARTIFACT_WRITE_SURFACE": "ARTIFACT_WRITE_REALIZATION",
    "GOVERNED_STATE_READ_SURFACE": "STATE_READ_REALIZATION",
    "GOVERNED_EXECUTION_PREPARATION_SURFACE": "EXECUTION_PREPARATION_REALIZATION",
    "GOVERNED_RESPONSE_EMISSION_SURFACE": "RESPONSE_EMISSION_REALIZATION",
}
FORBIDDEN_REALIZATION_MODES = (
    "RAW_SHELL_REALIZATION",
    "UNRESTRICTED_SUBPROCESS_REALIZATION",
    "NETWORK_EXECUTION_REALIZATION",
    "DAEMON_REALIZATION",
    "BACKGROUND_WORKER_REALIZATION",
    "PROVIDER_SWITCH_REALIZATION",
    "SELF_MODIFYING_REALIZATION",
    "SYSTEM_MUTATION_REALIZATION",
    "SECRET_EXTRACTION_REALIZATION",
    "UNBOUNDED_FILE_WRITE_REALIZATION",
)


def create_runtime_execution_realization_record(*, activation_evidence: dict) -> dict:
    runtime_surface = activation_evidence["runtime_surface"]
    value = {
        "runtime_surface_activation_id": activation_evidence["runtime_surface_activation_id"],
        "runtime_surface": runtime_surface,
    }
    return {
        "runtime_execution_realization_id": f"RUNTIME-EXECUTION-REALIZATION-{stable_hash(value)[:24]}",
        **value,
        "realization_mode": ALLOWED_REALIZATION_MODES.get(runtime_surface, ""),
    }
