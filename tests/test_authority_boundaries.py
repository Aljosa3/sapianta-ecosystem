from sapianta_bridge.architecture.authority_boundaries import (
    authority_boundary_matrix,
    can_perform,
    validate_authority_request,
)


def test_interaction_layer_cannot_execute() -> None:
    result = validate_authority_request("INTERACTION_LAYER", "direct_execution")

    assert can_perform("INTERACTION_LAYER", "direct_execution") is False
    assert result["allowed"] is False
    assert result["required_state"] == "BLOCKED"


def test_execution_layer_cannot_self_authorize() -> None:
    result = validate_authority_request("EXECUTION_LAYER", "self_authorize")

    assert result["allowed"] is False
    assert result["errors"] == [{"field": "action", "reason": "forbidden authority for layer"}]


def test_reflection_layer_cannot_enqueue_tasks() -> None:
    result = validate_authority_request("REFLECTION_LAYER", "task_enqueueing")

    assert result["allowed"] is False
    assert result["required_state"] == "BLOCKED"


def test_validation_layer_cannot_silently_retry_execution() -> None:
    result = validate_authority_request("VALIDATION_LAYER", "silent_execution_retry")

    assert result["allowed"] is False
    assert result["required_state"] == "BLOCKED"


def test_undefined_authority_is_blocked() -> None:
    result = validate_authority_request("GOVERNANCE_LAYER", "provider_routing")

    assert result["allowed"] is False
    assert result["errors"] == [
        {"field": "action", "reason": "undefined authority cannot be inherited"}
    ]


def test_authority_boundary_matrix_is_explicit() -> None:
    matrix = authority_boundary_matrix()

    assert matrix["EXECUTION_LAYER"]["undefined_authority_policy"] == "BLOCK"
    assert "governance_modification" in matrix["EXECUTION_LAYER"]["forbidden"]
    assert "advisory_reasoning" in matrix["REFLECTION_LAYER"]["allowed"]
