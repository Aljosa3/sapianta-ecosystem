from sapianta_bridge.envelopes.envelope_constraints import (
    default_constraints,
    validate_constraints,
)


def test_default_constraints_are_valid() -> None:
    result = validate_constraints(default_constraints(), 300)

    assert result["valid"] is True
    assert result["hidden_execution_allowed"] is False
    assert result["adaptive_retry_allowed"] is False


def test_unknown_constraint_fails_closed() -> None:
    constraints = default_constraints() + ["ALLOW_NETWORK"]
    result = validate_constraints(constraints, 300)

    assert result["valid"] is False
    assert {"field": "constraints", "reason": "undefined constraint: ALLOW_NETWORK"} in result["errors"]


def test_missing_required_constraint_fails_closed() -> None:
    constraints = [constraint for constraint in default_constraints() if constraint != "NO_HIDDEN_EXECUTION"]
    result = validate_constraints(constraints, 300)

    assert result["valid"] is False
    assert {"field": "constraints", "reason": "required constraint missing: NO_HIDDEN_EXECUTION"} in result["errors"]


def test_invalid_timeout_fails_closed() -> None:
    result = validate_constraints(default_constraints(), 0)

    assert result["valid"] is False
    assert {"field": "timeout_seconds", "reason": "timeout must be integer between 1 and 3600"} in result["errors"]
