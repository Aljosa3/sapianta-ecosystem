from sapianta_bridge.active_invocation.invocation_bridge import invoke_provider
from sapianta_bridge.chatgpt_ingress.ingress_bridge import process_chatgpt_ingress
from sapianta_bridge.providers.adapters.deterministic_mock_adapter import DeterministicMockAdapter
from sapianta_bridge.result_loop.result_return_loop import return_invocation_result
from sapianta_bridge.governed_session.session_context import create_session_context
from sapianta_bridge.governed_session.session_identity import create_session_identity
from sapianta_bridge.governed_session.session_lifecycle import complete_session_lifecycle
from sapianta_bridge.governed_session.session_validator import validate_session_artifacts


def _session_parts() -> tuple[dict, dict, list[str]]:
    ingress = process_chatgpt_ingress("Inspect governance evidence", provider_id="deterministic_mock")
    invocation = invoke_provider(
        envelope=ingress["envelope_proposal"]["execution_envelope"],
        provider=DeterministicMockAdapter(),
    )
    result = return_invocation_result(
        invocation_result=invocation["invocation_result"],
        invocation_evidence=invocation["invocation_evidence"],
    )
    identity = create_session_identity(
        ingress_output=ingress,
        invocation_output=invocation,
        result_output=result,
    ).to_dict()
    context = create_session_context(
        ingress_output=ingress,
        invocation_output=invocation,
        result_output=result,
    ).to_dict()
    return identity, context, complete_session_lifecycle()


def test_session_validator_accepts_complete_session() -> None:
    identity, context, lifecycle = _session_parts()
    validation = validate_session_artifacts(identity=identity, context=context, lifecycle=lifecycle)

    assert validation["valid"] is True
    assert validation["provider_identity_consistent"] is True


def test_session_validator_rejects_provider_mismatch() -> None:
    identity, context, lifecycle = _session_parts()
    context["provider_invocation_reference"]["provider_id"] = "codex"
    validation = validate_session_artifacts(identity=identity, context=context, lifecycle=lifecycle)

    assert validation["valid"] is False
    assert {"field": "provider_id", "reason": "session provider identity mismatch"} in validation["errors"]


def test_session_validator_rejects_lifecycle_skip() -> None:
    identity, context, _ = _session_parts()
    validation = validate_session_artifacts(identity=identity, context=context, lifecycle=["CREATED", "COMPLETED"])

    assert validation["valid"] is False
    assert {"field": "lifecycle", "reason": "session lifecycle invalid"} in validation["errors"]
