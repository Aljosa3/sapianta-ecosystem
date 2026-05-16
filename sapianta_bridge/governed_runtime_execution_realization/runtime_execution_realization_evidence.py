"""Replay-visible governed execution realization evidence."""

from .runtime_execution_realization_binding import LINEAGE_FIELDS

REALIZATION_STATES = (
    "EXECUTION_REALIZATION_CREATED",
    "EXECUTION_REALIZATION_SURFACE_VALIDATED",
    "EXECUTION_REALIZATION_ACTIVATION_VALIDATED",
    "EXECUTION_REALIZATION_CONTRACT_BOUND",
    "EXECUTION_REALIZATION_TRANSACTION_BOUND",
    "EXECUTION_REALIZATION_AUTHORIZED",
    "EXECUTION_REALIZATION_REJECTED",
    "EXECUTION_REALIZATION_CAPTURED",
    "EXECUTION_REALIZATION_FINALIZED",
    "BLOCKED",
    "FAILED",
)
AUTHORIZED_PATH = REALIZATION_STATES[:6] + REALIZATION_STATES[7:9]


def runtime_execution_realization_evidence(
    *,
    realization: dict,
    contract: dict,
    transaction: dict,
    binding: dict,
    policy: dict,
    valid: bool,
    states: tuple[str, ...],
) -> dict:
    return {
        "runtime_execution_realization_id": realization.get("runtime_execution_realization_id", ""),
        "runtime_execution_realization_contract_id": contract.get("runtime_execution_realization_contract_id", ""),
        "runtime_execution_realization_transaction_id": transaction.get("runtime_execution_realization_transaction_id", ""),
        "runtime_execution_realization_policy_id": policy.get("runtime_execution_realization_policy_id", ""),
        "runtime_execution_realization_boundary_id": policy.get("runtime_execution_realization_policy_id", ""),
        **{field: binding.get(field, "") for field in LINEAGE_FIELDS},
        "realization_mode": realization.get("realization_mode", ""),
        "states": list(states),
        "realization_authorized": valid,
        "surface_activation_is_execution_realization": False,
        "autonomous_execution_allowed": False,
        "replay_safe": valid,
    }
