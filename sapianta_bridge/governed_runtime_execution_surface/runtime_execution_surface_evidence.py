"""Replay-visible governed runtime execution surface evidence."""

from .runtime_execution_surface_binding import LINEAGE_FIELDS

STATES = (
    "EXECUTION_SURFACE_CREATED",
    "EXECUTION_SURFACE_CONTRACT_BOUND",
    "EXECUTION_SURFACE_BINDING_VALIDATED",
    "EXECUTION_SURFACE_EXECUTOR_BOUND",
    "EXECUTION_SURFACE_POLICY_VALIDATED",
    "EXECUTION_SURFACE_AUTHORIZED",
    "EXECUTION_SURFACE_REJECTED",
    "BLOCKED",
    "FAILED",
)
AUTHORIZED_PATH = STATES[:6]


def runtime_execution_surface_evidence(
    *,
    surface_record: dict,
    contract: dict,
    binding: dict,
    executor: dict,
    policy: dict,
    valid: bool,
    states: tuple[str, ...],
) -> dict:
    return {
        "runtime_execution_surface_id": surface_record.get("runtime_execution_surface_id", ""),
        "runtime_execution_surface_contract_id": contract.get("runtime_execution_surface_contract_id", ""),
        "runtime_execution_surface_executor_id": executor.get("runtime_execution_surface_executor_id", ""),
        "runtime_execution_surface_policy_id": policy.get("runtime_execution_surface_policy_id", ""),
        **{field: binding.get(field, "") for field in LINEAGE_FIELDS},
        "executor_primitive": surface_record.get("executor_primitive", ""),
        "runtime_surface": surface_record.get("runtime_surface", ""),
        "states": list(states),
        "surface_authorized": valid,
        "dynamic_surface_inference_allowed": False,
        "replay_safe": valid,
    }
