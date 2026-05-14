from sapianta_bridge.governed_session.session_lifecycle import (
    blocked_session_lifecycle,
    complete_session_lifecycle,
    validate_session_lifecycle,
)


def test_session_lifecycle_success_path_is_valid() -> None:
    lifecycle = complete_session_lifecycle()

    assert lifecycle == [
        "CREATED",
        "INGRESS_CAPTURED",
        "ENVELOPE_PROPOSED",
        "ENVELOPE_VALIDATED",
        "PROVIDER_INVOKED",
        "RESULT_RETURNED",
        "EVIDENCE_RECORDED",
        "COMPLETED",
    ]
    assert validate_session_lifecycle(lifecycle)["valid"] is True


def test_session_lifecycle_allows_blocked_terminal_path() -> None:
    assert blocked_session_lifecycle() == ["CREATED", "BLOCKED"]
    assert validate_session_lifecycle(blocked_session_lifecycle())["valid"] is True


def test_session_lifecycle_rejects_skipped_state_and_retries() -> None:
    validation = validate_session_lifecycle(["CREATED", "PROVIDER_INVOKED", "PROVIDER_INVOKED"])

    assert validation["valid"] is False
    assert validation["multiple_provider_invocations_present"] is True
