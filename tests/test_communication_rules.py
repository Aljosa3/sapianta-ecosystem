from sapianta_bridge.architecture.communication_rules import (
    communication_rules,
    validate_communication,
)


def test_canonical_communication_flow_is_allowed() -> None:
    for edge in communication_rules()["allowed_flow"]:
        result = validate_communication(edge["source"], edge["target"])
        assert result["allowed"] is True
        assert result["required_state"] == "ALLOWED"


def test_execution_cannot_communicate_directly_with_user() -> None:
    result = validate_communication("EXECUTION_LAYER", "USER")

    assert result["allowed"] is False
    assert result["required_state"] == "BLOCKED"


def test_reflection_cannot_trigger_execution() -> None:
    result = validate_communication("REFLECTION_LAYER", "EXECUTION_LAYER")

    assert result["allowed"] is False
    assert result["errors"] == [
        {"field": "communication", "reason": "reflection cannot trigger execution"}
    ]


def test_execution_cannot_mutate_governance() -> None:
    result = validate_communication("EXECUTION_LAYER", "GOVERNANCE_LAYER")

    assert result["allowed"] is False
    assert result["required_state"] == "BLOCKED"


def test_undefined_communication_path_is_blocked() -> None:
    result = validate_communication("USER", "EXECUTION_LAYER")

    assert result["allowed"] is False
    assert result["errors"] == [
        {"field": "communication", "reason": "undefined communication path"}
    ]
