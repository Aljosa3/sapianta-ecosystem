"""Deterministic operation-to-executor mappings."""

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash

ALLOWED_CAPABILITY_MAPPINGS = {
    "RUN_VALIDATION": "PYTEST_VALIDATION_EXECUTOR",
    "WRITE_ARTIFACT": "BOUNDED_ARTIFACT_WRITER",
    "READ_STATE": "GOVERNED_STATE_READER",
    "PREPARE_EXECUTION": "GOVERNED_EXECUTION_PREPARER",
    "RETURN_RESPONSE": "GOVERNED_RESPONSE_EMITTER",
}
FORBIDDEN_CAPABILITY_REQUESTS = (
    "RAW_SHELL",
    "UNRESTRICTED_SUBPROCESS",
    "NETWORK_EXECUTION",
    "BACKGROUND_WORKER",
    "DAEMON_EXECUTION",
    "PROVIDER_SWITCH",
    "SELF_MODIFY_RUNTIME",
    "UNBOUNDED_FILE_WRITE",
    "SYSTEM_MUTATION",
    "SECRET_EXTRACTION",
)


def create_runtime_capability_mapping_record(*, operation_evidence: dict) -> dict:
    operation_type = operation_evidence["operation_type"]
    value = {
        "runtime_operation_envelope_id": operation_evidence["runtime_operation_envelope_id"],
        "operation_type": operation_type,
    }
    return {
        "runtime_capability_mapping_id": f"RUNTIME-CAPABILITY-MAPPING-{stable_hash(value)[:24]}",
        **value,
        "executor_primitive": ALLOWED_CAPABILITY_MAPPINGS.get(operation_type, ""),
    }
