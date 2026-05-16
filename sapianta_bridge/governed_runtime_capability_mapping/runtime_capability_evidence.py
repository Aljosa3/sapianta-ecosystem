"""Replay-visible governed runtime capability evidence."""

from .runtime_capability_validator import LINEAGE_FIELDS

CAPABILITY_STATES = (
    "CAPABILITY_MAPPING_CREATED",
    "CAPABILITY_CONTRACT_BOUND",
    "CAPABILITY_EXECUTOR_BOUND",
    "CAPABILITY_POLICY_VALIDATED",
    "CAPABILITY_SURFACE_VALIDATED",
    "CAPABILITY_AUTHORIZED",
    "CAPABILITY_REJECTED",
    "BLOCKED",
    "FAILED",
)
AUTHORIZED_PATH = CAPABILITY_STATES[:6]


def runtime_capability_evidence(
    *,
    mapping: dict,
    contract: dict,
    executor: dict,
    surface: dict,
    policy: dict,
    operation_evidence: dict,
    valid: bool,
    states: tuple[str, ...],
) -> dict:
    return {
        "runtime_capability_mapping_id": mapping.get("runtime_capability_mapping_id", ""),
        "runtime_capability_contract_id": contract.get("runtime_capability_contract_id", ""),
        "runtime_capability_executor_id": executor.get("runtime_capability_executor_id", ""),
        "runtime_capability_surface_id": surface.get("runtime_capability_surface_id", ""),
        "runtime_capability_policy_id": policy.get("runtime_capability_policy_id", ""),
        **{field: operation_evidence.get(field, "") for field in LINEAGE_FIELDS},
        "operation_type": mapping.get("operation_type", ""),
        "executor_primitive": executor.get("executor_primitive", ""),
        "states": list(states),
        "capability_authorized": valid,
        "dynamic_executor_generation_allowed": False,
        "replay_safe": valid,
    }
