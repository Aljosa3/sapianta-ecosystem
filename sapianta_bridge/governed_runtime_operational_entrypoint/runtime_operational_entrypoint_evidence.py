"""Replay-visible governed runtime operational entrypoint evidence."""

from .runtime_operational_entrypoint_binding import LINEAGE_FIELDS


def runtime_operational_entrypoint_evidence(
    *,
    entrypoint: dict,
    contract: dict,
    transaction: dict,
    binding: dict,
    policy: dict,
    valid: bool,
) -> dict:
    return {
        "runtime_operational_entrypoint_id": entrypoint.get("runtime_operational_entrypoint_id", ""),
        "runtime_operational_entrypoint_contract_id": contract.get("runtime_operational_entrypoint_contract_id", ""),
        "runtime_operational_entrypoint_transaction_id": transaction.get("runtime_operational_entrypoint_transaction_id", ""),
        "runtime_operational_entrypoint_policy_id": policy.get("runtime_operational_entrypoint_policy_id", ""),
        "runtime_operational_entrypoint_boundary_id": policy.get("runtime_operational_entrypoint_policy_id", ""),
        **{field: binding.get(field, "") for field in LINEAGE_FIELDS},
        "operational_entry_mode": entrypoint.get("operational_entry_mode", ""),
        "operational_entry_admitted": valid,
        "replay_safe": valid,
        "continuity_fabricated": False,
    }
