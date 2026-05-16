from sapianta_bridge.governed_runtime_operation_envelope.runtime_operation_boundary import (
    ALLOWED_OPERATION_TYPES,
    FORBIDDEN_OPERATION_TYPES,
    create_runtime_operation_boundary,
)


def test_boundary_declares_allowed_and_forbidden_grammar():
    boundary = create_runtime_operation_boundary(runtime_operation_envelope_id="ENV-1")
    assert "READ_STATE" in ALLOWED_OPERATION_TYPES
    assert "RAW_SHELL" in FORBIDDEN_OPERATION_TYPES
    assert boundary["raw_shell_execution_allowed"] is False
