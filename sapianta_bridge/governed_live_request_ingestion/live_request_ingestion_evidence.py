"""Replay-visible governed live request ingestion evidence."""

FIELDS = (
    "live_request_ingestion_session_id",
    "serving_gateway_session_id",
    "runtime_serving_session_id",
    "terminal_attachment_session_id",
    "session_runtime_id",
    "interaction_loop_session_id",
    "interaction_turn_id",
    "live_runtime_session_id",
    "runtime_attachment_session_id",
    "transport_session_id",
    "governed_session_id",
    "execution_gate_id",
    "provider_invocation_id",
    "bounded_runtime_id",
    "result_capture_id",
    "response_return_id",
    "request_activation_id",
)


def live_request_ingestion_evidence(*, binding: dict, valid: bool, states: tuple[str, ...]) -> dict:
    return {
        **{field: binding.get(field, "") for field in FIELDS},
        "states": list(states),
        "request_activation_bound": bool(binding.get("request_activation_id")),
        "replay_safe": valid,
        "continuity_fabricated": False,
        "hidden_memory_introduced": False,
    }
