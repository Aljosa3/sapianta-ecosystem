from sapianta_bridge.provider_connectors.bounded_execution_timeout import validate_bounded_execution_timeout


def test_bounded_execution_timeout_accepts_explicit_timeout():
    validation = validate_bounded_execution_timeout(30)

    assert validation["valid"] is True
    assert validation["timeout_bounded"] is True


def test_bounded_execution_timeout_rejects_missing_timeout():
    validation = validate_bounded_execution_timeout(None)

    assert validation["valid"] is False
    assert any(error["field"] == "timeout_seconds" for error in validation["errors"])


def test_bounded_execution_timeout_rejects_unbounded_timeout():
    validation = validate_bounded_execution_timeout(999)

    assert validation["valid"] is False
