"""Replay-visible governed execution exchange evidence."""

FIELDS = (
    "execution_exchange_session_id",
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
)


def execution_exchange_evidence(*, binding: dict, valid: bool, states: tuple[str, ...]) -> dict:
    return {
        **{field: binding.get(field, "") for field in FIELDS},
        "states": list(states),
        "governed_execution_result_paired": bool(binding.get("result_capture_id") and binding.get("response_return_id")),
        "replay_safe": valid,
        "continuity_fabricated": False,
        "hidden_provider_memory_trusted": False,
    }
