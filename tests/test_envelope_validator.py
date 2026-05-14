from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.envelopes.envelope_validator import validate_execution_envelope


def _valid_envelope() -> dict:
    return create_execution_envelope(
        envelope_id="ENV-VALID",
        provider_id="codex",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-VALID",
        validation_requirements=["pytest"],
    ).to_dict()


def test_valid_envelope_passes() -> None:
    result = validate_execution_envelope(_valid_envelope())

    assert result["envelope_valid"] is True
    assert result["provider_bound"] is True
    assert result["authority_scope_valid"] is True
    assert result["workspace_scope_valid"] is True
    assert result["replay_binding_valid"] is True
    assert result["hidden_authority_detected"] is False
    assert result["provider_independent_semantics"] is True


def test_envelope_rejects_undefined_authority() -> None:
    envelope = _valid_envelope()
    envelope["authority_scope"] = ["ROOT_ACCESS", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"]
    envelope.pop("replay_binding_sha256")
    result = validate_execution_envelope(envelope)

    assert result["envelope_valid"] is False
    assert {"field": "authority_scope", "reason": "undefined authority scope: ROOT_ACCESS"} in result["errors"]


def test_envelope_rejects_ambiguous_workspace() -> None:
    envelope = _valid_envelope()
    envelope["workspace_scope"] = {"allowed_roots": ["../outside"], "forbidden_roots": []}
    envelope.pop("replay_binding_sha256")
    result = validate_execution_envelope(envelope)

    assert result["envelope_valid"] is False
    assert {"field": "workspace_scope.allowed_roots", "reason": "unsafe path: ../outside"} in result["errors"]


def test_envelope_rejects_mutable_provider_identity() -> None:
    envelope = _valid_envelope()
    envelope["provider_id"] = "Codex"
    envelope.pop("replay_binding_sha256")
    result = validate_execution_envelope(envelope)

    assert result["envelope_valid"] is False
    assert {"field": "provider_id", "reason": "provider_id must be normalized"} in result["errors"]


def test_envelope_rejects_action_overlap() -> None:
    envelope = _valid_envelope()
    envelope["forbidden_actions"] = ["inspect"]
    envelope.pop("replay_binding_sha256")
    result = validate_execution_envelope(envelope)

    assert result["envelope_valid"] is False
    assert {"field": "actions", "reason": "action cannot be both allowed and forbidden"} in result["errors"]


def test_envelope_exposes_no_orchestration_or_routing() -> None:
    result = validate_execution_envelope(_valid_envelope())

    assert result["routing_present"] is False
    assert result["orchestration_present"] is False
