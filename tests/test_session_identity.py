from sapianta_bridge.active_invocation.invocation_bridge import invoke_provider
from sapianta_bridge.chatgpt_ingress.ingress_bridge import process_chatgpt_ingress
from sapianta_bridge.providers.adapters.deterministic_mock_adapter import DeterministicMockAdapter
from sapianta_bridge.result_loop.result_return_loop import return_invocation_result
from sapianta_bridge.governed_session.session_identity import create_session_identity, validate_session_identity


def _artifacts() -> tuple[dict, dict, dict]:
    ingress = process_chatgpt_ingress("Inspect governance evidence", provider_id="deterministic_mock")
    envelope = ingress["envelope_proposal"]["execution_envelope"]
    invocation = invoke_provider(envelope=envelope, provider=DeterministicMockAdapter())
    result = return_invocation_result(
        invocation_result=invocation["invocation_result"],
        invocation_evidence=invocation["invocation_evidence"],
    )
    return ingress, invocation, result


def test_session_identity_is_deterministic_and_valid() -> None:
    ingress, invocation, result = _artifacts()
    first = create_session_identity(
        ingress_output=ingress,
        invocation_output=invocation,
        result_output=result,
    ).to_dict()
    second = create_session_identity(
        ingress_output=ingress,
        invocation_output=invocation,
        result_output=result,
    ).to_dict()

    assert first["session_id"] == second["session_id"]
    assert first["session_id"].startswith("SESSION-")
    assert validate_session_identity(first)["valid"] is True


def test_session_identity_rejects_mutation() -> None:
    ingress, invocation, result = _artifacts()
    identity = create_session_identity(
        ingress_output=ingress,
        invocation_output=invocation,
        result_output=result,
    ).to_dict()
    identity["provider_id"] = "codex"

    assert validate_session_identity(identity)["valid"] is False
