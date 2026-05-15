"""Replay-visible governed terminal attachment evidence."""

FIELDS = (
    "terminal_attachment_session_id",
    "runtime_serving_session_id",
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
    "stdin_binding_id",
    "stdout_binding_id",
)


def terminal_attachment_evidence(*, binding: dict, valid: bool, states: tuple[str, ...]) -> dict:
    return {
        **{field: binding.get(field, "") for field in FIELDS},
        "states": list(states),
        "stdin_bounded": bool(binding.get("stdin_binding_id")),
        "stdout_bounded": bool(binding.get("stdout_binding_id")),
        "replay_safe": valid,
        "continuity_fabricated": False,
        "hidden_execution_introduced": False,
    }
