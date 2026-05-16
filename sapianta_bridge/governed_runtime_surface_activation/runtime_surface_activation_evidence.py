"""Replay-visible governed runtime surface activation evidence."""

from sapianta_bridge.governed_runtime_execution_surface.runtime_execution_surface_binding import LINEAGE_FIELDS


def runtime_surface_activation_evidence(
    *,
    activation: dict,
    contract: dict,
    binding: dict,
    policy: dict,
    valid: bool,
    states: tuple[str, ...],
) -> dict:
    return {
        "runtime_surface_activation_id": activation.get("runtime_surface_activation_id", ""),
        "runtime_surface_activation_contract_id": contract.get("runtime_surface_activation_contract_id", ""),
        "runtime_surface_activation_policy_id": policy.get("runtime_surface_activation_policy_id", ""),
        "runtime_execution_surface_id": activation.get("runtime_execution_surface_id", ""),
        **{field: binding.get(field, "") for field in LINEAGE_FIELDS},
        "runtime_surface": activation.get("runtime_surface", ""),
        "states": list(states),
        "surface_operational": valid,
        "adaptive_activation_allowed": False,
        "replay_safe": valid,
    }
