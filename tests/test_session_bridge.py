from sapianta_bridge.active_invocation.invocation_bridge import invoke_provider
from sapianta_bridge.chatgpt_ingress.ingress_bridge import process_chatgpt_ingress
from sapianta_bridge.providers.adapters.deterministic_mock_adapter import DeterministicMockAdapter
from sapianta_bridge.result_loop.result_return_loop import return_invocation_result
from sapianta_bridge.governed_session.session_bridge import create_governed_execution_session


def _outputs() -> tuple[dict, dict, dict]:
    ingress = process_chatgpt_ingress("Inspect governance evidence", provider_id="deterministic_mock")
    invocation = invoke_provider(
        envelope=ingress["envelope_proposal"]["execution_envelope"],
        provider=DeterministicMockAdapter(),
    )
    result = return_invocation_result(
        invocation_result=invocation["invocation_result"],
        invocation_evidence=invocation["invocation_evidence"],
    )
    return ingress, invocation, result


def test_session_bridge_creates_complete_governed_session() -> None:
    ingress, invocation, result = _outputs()
    session = create_governed_execution_session(
        ingress_output=ingress,
        invocation_output=invocation,
        result_output=result,
    )

    assert session["session_validation"]["valid"] is True
    assert session["session_evidence"]["session_status"] == "COMPLETED"
    assert session["session_evidence"]["ingress_bound"] is True
    assert session["session_evidence"]["result_return_bound"] is True


def test_session_bridge_fails_closed_on_missing_artifact() -> None:
    ingress, invocation, _ = _outputs()
    session = create_governed_execution_session(
        ingress_output=ingress,
        invocation_output=invocation,
        result_output={},
    )

    assert session["session_validation"]["valid"] is False
    assert session["session_evidence"]["session_status"] == "BLOCKED"


def test_session_bridge_does_not_orchestrate_or_route() -> None:
    ingress, invocation, result = _outputs()
    session = create_governed_execution_session(
        ingress_output=ingress,
        invocation_output=invocation,
        result_output=result,
    )

    assert session["orchestration_present"] is False
    assert session["retry_present"] is False
    assert session["provider_routing_present"] is False
    assert session["autonomous_execution_present"] is False
    assert session["hidden_memory_mutation_present"] is False
