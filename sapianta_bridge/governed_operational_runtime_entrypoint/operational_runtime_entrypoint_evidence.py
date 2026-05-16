from .operational_runtime_entrypoint_boundary import FORBIDDEN_CAPABILITIES
from .operational_runtime_entrypoint_validator import LINKAGE_FIELDS


def operational_entrypoint_evidence(
    *,
    activation: dict,
    boundary: dict,
    contract: dict,
    admission: dict,
    binding: dict,
    valid: bool,
    states: tuple[str, ...],
    closed: bool,
) -> dict:
    return {
        **activation,
        **{field: binding.get(field, "") for field in LINKAGE_FIELDS},
        "runtime_activation_boundary_id": boundary.get("runtime_activation_boundary_id", ""),
        "operational_entry_contract_id": contract.get("operational_entry_contract_id", ""),
        "operational_entry_admission_id": admission.get("operational_entry_admission_id", ""),
        "states": list(states),
        "closed": closed,
        "replay_safe": valid,
        "operational_ingress_governed": contract.get("operational_ingress_governed") is True,
        "operational_activation_authorized": admission.get("admitted") is True and admission.get("approved_by") == "human",
        "continuity_fabricated": False,
        **{f"{capability}_introduced": False for capability in FORBIDDEN_CAPABILITIES},
    }
