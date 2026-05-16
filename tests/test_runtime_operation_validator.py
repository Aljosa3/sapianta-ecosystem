from sapianta_bridge.governed_runtime_operation_envelope import create_runtime_operation_envelope
from sapianta_bridge.governed_runtime_operation_envelope.runtime_operation_validator import (
    validate_runtime_operation_envelope,
)


def _activation(*, authorized=True):
    return {
        "validation": {"valid": True},
        "runtime_activation_gate_binding": {
            "runtime_activation_gate_id": "GATE-1",
            "runtime_activation_boundary_id": "BOUNDARY-1",
            "operational_entry_contract_id": "CONTRACT-1",
            "operational_entry_admission_id": "ADMISSION-1",
            "operational_runtime_entrypoint_id": "ENTRY-1",
            "execution_exchange_session_id": "EXCHANGE-1",
            "execution_relay_session_id": "RELAY-1",
            "runtime_execution_commit_id": "COMMIT-1",
            "runtime_delivery_finalization_id": "FINAL-1",
            "response_return_id": "RETURN-1",
            "activation_authorized": authorized,
            "approved_by": "human",
        },
    }


def _lineage():
    return {
        "runtime_persistent_channel_id": "CHANNEL-1",
        "direct_runtime_interaction_session_id": "DIRECT-1",
        "runtime_surface_session_id": "SURFACE-1",
        "local_runtime_bridge_session_id": "BRIDGE-1",
        "governed_session_id": "GOV-1",
        "execution_gate_id": "EXEC-GATE-1",
        "provider_invocation_id": "PROVIDER-1",
        "bounded_runtime_id": "RUNTIME-1",
        "result_capture_id": "CAPTURE-1",
    }


def _create(**overrides):
    params = {
        "activation_output": _activation(),
        "upstream_lineage": _lineage(),
        "operation_type": "READ_STATE",
        "operation_intent": "read bounded state",
        "target_scope": {"kind": "path", "value": "runtime/state.json"},
        "allowed_inputs": ["state_ref"],
        "expected_outputs": ["state_snapshot"],
        "risk_class": "LOW",
        "requires_human_approval": True,
        "approved_by": "human",
    }
    params.update(overrides)
    return create_runtime_operation_envelope(**params)


def test_unknown_operation_type_fails_closed():
    assert _create(operation_type="SOMETHING_NEW")["validation"]["valid"] is False


def test_missing_activation_authorization_fails_closed():
    assert _create(activation_output=_activation(authorized=False))["validation"]["valid"] is False


def test_non_human_approval_fails_closed():
    assert _create(approved_by="system")["validation"]["valid"] is False


def test_unbounded_scope_fails_closed():
    assert _create(target_scope={"kind": "path", "value": "*"})["validation"]["valid"] is False


def test_missing_explicit_inputs_and_outputs_fail_closed():
    assert _create(allowed_inputs=[])["validation"]["valid"] is False
    assert _create(expected_outputs=[])["validation"]["valid"] is False


def test_envelope_identity_cannot_change_unexpectedly():
    first = _create()
    second = _create(operation_intent="different intent", prior_output=first)
    assert second["validation"]["valid"] is False


def test_incomplete_contract_and_policy_linkage_fail_closed():
    result = _create()
    contract = dict(result["runtime_operation_contract"])
    contract["runtime_operation_envelope_id"] = "OTHER"
    policy = dict(result["runtime_operation_policy"])
    policy["bounded_operation_required"] = False
    validation = validate_runtime_operation_envelope(
        envelope=result["runtime_operation_envelope"],
        contract=contract,
        payload=result["runtime_operation_payload"],
        policy=policy,
        boundary=result["runtime_operation_boundary"],
        activation_output=_activation(),
        upstream_lineage=_lineage(),
    )
    assert validation["valid"] is False
    assert any(error["field"] == "runtime_operation_contract_id" for error in validation["errors"])
    assert any(error["field"] == "runtime_operation_policy_id" for error in validation["errors"])
