from sapianta_bridge.governed_runtime_operation_envelope.runtime_operation_payload import (
    create_runtime_operation_payload,
)


def test_payload_contains_required_authorization_fields():
    payload = create_runtime_operation_payload(
        runtime_operation_envelope_id="ENV-1",
        operation_type="RUN_VALIDATION",
        operation_intent="run bounded validation",
        target_scope={"kind": "path", "value": "tests"},
        allowed_inputs=["test_spec"],
        expected_outputs=["validation_report"],
        risk_class="LOW",
        requires_human_approval=True,
        approved_by="human",
        activation_authorized=True,
        runtime_activation_gate_id="GATE-1",
    )
    assert payload["approved_by"] == "human"
    assert payload["runtime_activation_gate_id"] == "GATE-1"
