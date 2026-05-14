from sapianta_bridge.no_copy_paste_loop.loop_lifecycle import (
    blocked_loop_lifecycle,
    complete_loop_lifecycle,
    validate_loop_lifecycle,
)


def test_loop_lifecycle_success_path_is_valid() -> None:
    lifecycle = complete_loop_lifecycle()

    assert lifecycle == [
        "CREATED",
        "REQUEST_ACCEPTED",
        "BRIDGE_REQUEST_CREATED",
        "INGRESS_PROPAGATED",
        "SESSION_BOUND",
        "PROVIDER_INVOKED",
        "RESULT_PROPAGATED",
        "RESPONSE_DELIVERED",
        "EVIDENCE_RECORDED",
        "COMPLETED",
    ]
    assert validate_loop_lifecycle(lifecycle)["valid"] is True


def test_loop_lifecycle_allows_blocked_path() -> None:
    assert blocked_loop_lifecycle() == ["CREATED", "BLOCKED"]
    assert validate_loop_lifecycle(blocked_loop_lifecycle())["valid"] is True


def test_loop_lifecycle_rejects_recursive_or_repeated_invocation() -> None:
    validation = validate_loop_lifecycle(["CREATED", "PROVIDER_INVOKED", "PROVIDER_INVOKED"])

    assert validation["valid"] is False
    assert validation["multiple_invocations_present"] is True
