"""Bounded runtime operation grammar and boundary semantics."""

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash

ALLOWED_OPERATION_TYPES = (
    "READ_STATE",
    "WRITE_ARTIFACT",
    "RUN_VALIDATION",
    "PREPARE_EXECUTION",
    "RETURN_RESPONSE",
)
FORBIDDEN_OPERATION_TYPES = (
    "RAW_SHELL",
    "UNRESTRICTED_SUBPROCESS",
    "NETWORK_CALL",
    "BACKGROUND_WORKER",
    "DAEMON_START",
    "PROVIDER_SWITCH",
    "SELF_MODIFY_RUNTIME",
    "UNBOUNDED_FILE_WRITE",
    "SECRET_READ",
    "SYSTEM_MUTATION",
)
OPERATION_STATES = (
    "OPERATION_ENVELOPE_CREATED",
    "OPERATION_CONTRACT_BOUND",
    "OPERATION_PAYLOAD_BOUND",
    "OPERATION_POLICY_VALIDATED",
    "OPERATION_BOUNDARY_VALIDATED",
    "OPERATION_AUTHORIZED",
    "OPERATION_REJECTED",
    "BLOCKED",
    "FAILED",
)
AUTHORIZED_PATH = OPERATION_STATES[:6]


def create_runtime_operation_boundary(*, runtime_operation_envelope_id: str) -> dict:
    value = {"runtime_operation_envelope_id": runtime_operation_envelope_id}
    return {
        "runtime_operation_boundary_id": f"RUNTIME-OPERATION-BOUNDARY-{stable_hash(value)[:24]}",
        **value,
        "raw_shell_execution_allowed": False,
        "unrestricted_subprocess_allowed": False,
    }
