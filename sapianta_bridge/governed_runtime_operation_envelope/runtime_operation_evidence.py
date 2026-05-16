"""Replay-visible governed runtime operation envelope evidence."""

from .runtime_operation_validator import UPSTREAM_LINEAGE_FIELDS


def runtime_operation_evidence(
    *,
    envelope: dict,
    contract: dict,
    payload: dict,
    policy: dict,
    boundary: dict,
    lineage: dict,
    valid: bool,
    states: tuple[str, ...],
) -> dict:
    return {
        "runtime_operation_envelope_id": envelope.get("runtime_operation_envelope_id", ""),
        "runtime_operation_contract_id": contract.get("runtime_operation_contract_id", ""),
        "runtime_operation_payload_id": payload.get("runtime_operation_payload_id", ""),
        "runtime_operation_policy_id": policy.get("runtime_operation_policy_id", ""),
        "runtime_operation_boundary_id": boundary.get("runtime_operation_boundary_id", ""),
        **{field: lineage.get(field, "") for field in UPSTREAM_LINEAGE_FIELDS},
        "operation_type": payload.get("operation_type", ""),
        "states": list(states),
        "operation_authorized": valid,
        "activation_authorization_is_operation_authorization": False,
        "raw_prompt_to_shell_forbidden": True,
        "replay_safe": valid,
        "continuity_fabricated": False,
    }
