"""Fail-closed operational entrypoint validation."""

LINKAGE_FIELDS = (
    "runtime_persistent_channel_id",
    "direct_runtime_interaction_session_id",
    "runtime_surface_session_id",
    "execution_exchange_session_id",
    "execution_relay_session_id",
    "runtime_execution_commit_id",
    "runtime_delivery_finalization_id",
    "response_return_id",
)


def _missing_text(value: object) -> bool:
    return not isinstance(value, str) or not value.strip()


def validate_operational_runtime_entrypoint(
    *,
    activation: dict,
    boundary: dict,
    contract: dict,
    admission: dict,
    channel_output: dict,
    prior_output: dict | None = None,
) -> dict:
    errors = []
    binding = channel_output.get("runtime_persistent_channel_binding", {})

    if channel_output.get("validation", {}).get("valid") is not True:
        errors.append({"field": "runtime_persistent_channel", "reason": "runtime activation linkage invalid"})
    if (
        boundary.get("valid") is not True
        or boundary.get("operational_ingress_boundary") is not True
        or boundary.get("runtime_persistent_channel_id") != binding.get("runtime_persistent_channel_id")
    ):
        errors.append({"field": "runtime_activation_boundary_id", "reason": "operational activation boundary invalid"})

    for field in ("operational_entry_contract_id", "runtime_activation_boundary_id", "operational_intent"):
        if _missing_text(contract.get(field)):
            errors.append({"field": field, "reason": "entry admission contract incomplete"})
    if contract.get("runtime_activation_boundary_id") != boundary.get("runtime_activation_boundary_id"):
        errors.append({"field": "operational_entry_contract_id", "reason": "entry admission contract boundary mismatch"})
    if contract.get("operational_ingress_governed") is not True or contract.get("replay_safe") is not True:
        errors.append({"field": "operational_entry_contract_id", "reason": "entry admission contract incomplete"})

    if admission.get("admitted") is not True or admission.get("approved_by") != "human":
        errors.append({"field": "operational_entry_admission_id", "reason": "operational admission invalid"})
    if admission.get("operational_entry_contract_id") != contract.get("operational_entry_contract_id"):
        errors.append({"field": "operational_entry_admission_id", "reason": "operational admission contract mismatch"})

    for field in (
        "operational_runtime_entrypoint_id",
        "runtime_activation_boundary_id",
        "operational_entry_admission_id",
        "operational_entry_contract_id",
    ):
        if _missing_text(activation.get(field)):
            errors.append({"field": field, "reason": "required operational ingress evidence missing"})
    if activation.get("runtime_activation_boundary_id") != boundary.get("runtime_activation_boundary_id"):
        errors.append({"field": "runtime_activation_boundary_id", "reason": "runtime activation linkage invalid"})
    if activation.get("operational_entry_contract_id") != contract.get("operational_entry_contract_id"):
        errors.append({"field": "operational_entry_contract_id", "reason": "entry admission contract incomplete"})
    if activation.get("operational_entry_admission_id") != admission.get("operational_entry_admission_id"):
        errors.append({"field": "operational_entry_admission_id", "reason": "entry admission contract incomplete"})

    for field in LINKAGE_FIELDS:
        if _missing_text(binding.get(field)):
            errors.append({"field": field, "reason": "entrypoint linkage missing"})

    if prior_output is not None:
        previous = prior_output.get("activation", {})
        if previous.get("operational_runtime_entrypoint_id") != activation.get("operational_runtime_entrypoint_id"):
            errors.append({"field": "operational_runtime_entrypoint_id", "reason": "entrypoint identity changed"})
        if prior_output.get("closed") is True:
            errors.append({"field": "closed", "reason": "closed entrypoint cannot reopen implicitly"})

    return {"valid": not errors, "errors": errors}
