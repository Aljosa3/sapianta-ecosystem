from sapianta_bridge.active_chatgpt_bridge.bridge_lifecycle import (
    blocked_bridge_lifecycle,
    complete_bridge_lifecycle,
    validate_bridge_lifecycle,
)


def test_active_chatgpt_bridge_lifecycle_success_path_is_valid() -> None:
    lifecycle = complete_bridge_lifecycle()

    assert lifecycle == [
        "CREATED",
        "INGRESS_BOUND",
        "ENVELOPE_PROPOSED",
        "SESSION_CREATED",
        "PROVIDER_INVOKED",
        "RESULT_RETURNED",
        "RESPONSE_CREATED",
        "EVIDENCE_RECORDED",
        "COMPLETED",
    ]
    assert validate_bridge_lifecycle(lifecycle)["valid"] is True


def test_active_chatgpt_bridge_lifecycle_allows_blocked_path() -> None:
    assert blocked_bridge_lifecycle() == ["CREATED", "BLOCKED"]
    assert validate_bridge_lifecycle(blocked_bridge_lifecycle())["valid"] is True


def test_active_chatgpt_bridge_lifecycle_rejects_multiple_invocations() -> None:
    validation = validate_bridge_lifecycle(["CREATED", "PROVIDER_INVOKED", "PROVIDER_INVOKED"])

    assert validation["valid"] is False
    assert validation["multiple_invocations_present"] is True
