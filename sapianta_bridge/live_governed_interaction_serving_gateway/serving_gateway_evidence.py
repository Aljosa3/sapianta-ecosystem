"""Replay-visible serving gateway evidence."""

FIELDS = (
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
    "ingress_id",
    "egress_id",
)


def serving_gateway_evidence(*, binding: dict, valid: bool, states: tuple[str, ...]) -> dict:
    return {
        **{field: binding.get(field, "") for field in FIELDS},
        "states": list(states),
        "ingress_replay_visible": bool(binding.get("ingress_id")),
        "egress_replay_visible": bool(binding.get("egress_id")),
        "replay_safe": valid,
        "continuity_fabricated": False,
        "autonomous_execution_introduced": False,
    }
