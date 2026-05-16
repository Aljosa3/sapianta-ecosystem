"""Deterministic executable runtime surface mappings."""

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash

ALLOWED_EXECUTION_SURFACES = {
    "PYTEST_VALIDATION_EXECUTOR": "GOVERNED_PYTEST_RUNTIME_SURFACE",
    "BOUNDED_ARTIFACT_WRITER": "GOVERNED_ARTIFACT_WRITE_SURFACE",
    "GOVERNED_STATE_READER": "GOVERNED_STATE_READ_SURFACE",
    "GOVERNED_EXECUTION_PREPARER": "GOVERNED_EXECUTION_PREPARATION_SURFACE",
    "GOVERNED_RESPONSE_EMITTER": "GOVERNED_RESPONSE_EMISSION_SURFACE",
}
FORBIDDEN_EXECUTION_SURFACES = (
    "RAW_SHELL_RUNTIME_SURFACE",
    "UNRESTRICTED_SUBPROCESS_SURFACE",
    "UNRESTRICTED_NETWORK_SURFACE",
    "DYNAMIC_EXECUTOR_DISCOVERY_SURFACE",
)


def create_runtime_execution_surface_record(*, capability_evidence: dict) -> dict:
    executor_primitive = capability_evidence["executor_primitive"]
    value = {
        "runtime_capability_mapping_id": capability_evidence["runtime_capability_mapping_id"],
        "executor_primitive": executor_primitive,
    }
    return {
        "runtime_execution_surface_id": f"RUNTIME-EXECUTION-SURFACE-{stable_hash(value)[:24]}",
        **value,
        "runtime_surface": ALLOWED_EXECUTION_SURFACES.get(executor_primitive, ""),
    }
