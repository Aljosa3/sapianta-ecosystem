"""Replay-visible governed runtime activation gate evidence."""

FIELDS = (
    "runtime_activation_gate_id",
    "runtime_activation_boundary_id",
    "operational_entry_contract_id",
    "operational_entry_admission_id",
    "execution_exchange_session_id",
    "execution_relay_session_id",
    "runtime_execution_commit_id",
    "runtime_delivery_finalization_id",
    "operational_runtime_entrypoint_id",
    "response_return_id",
    "activation_source_kind",
    "approved_by",
)


def runtime_activation_gate_evidence(*, binding: dict, valid: bool, states: tuple[str, ...]) -> dict:
    return {
        **{field: binding.get(field, "") for field in FIELDS},
        "activation_authorized": binding.get("activation_authorized") is True,
        "runtime_activatable": valid,
        "states": list(states),
        "replay_safe": valid,
        "continuity_fabricated": False,
        "hidden_provider_state_trusted": False,
        "autonomous_activation_introduced": False,
    }
