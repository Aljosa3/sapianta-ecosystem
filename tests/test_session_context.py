from sapianta_bridge.active_invocation.invocation_bridge import invoke_provider
from sapianta_bridge.chatgpt_ingress.ingress_bridge import process_chatgpt_ingress
from sapianta_bridge.providers.adapters.deterministic_mock_adapter import DeterministicMockAdapter
from sapianta_bridge.result_loop.result_return_loop import return_invocation_result
from sapianta_bridge.governed_session.session_context import create_session_context, validate_session_context


def _context() -> dict:
    ingress = process_chatgpt_ingress("Inspect governance evidence", provider_id="deterministic_mock")
    invocation = invoke_provider(
        envelope=ingress["envelope_proposal"]["execution_envelope"],
        provider=DeterministicMockAdapter(),
    )
    result = return_invocation_result(
        invocation_result=invocation["invocation_result"],
        invocation_evidence=invocation["invocation_evidence"],
    )
    return create_session_context(
        ingress_output=ingress,
        invocation_output=invocation,
        result_output=result,
    ).to_dict()


def test_session_context_contains_required_references() -> None:
    context = _context()

    assert context["ingress_reference"]["session_id"]
    assert context["envelope_reference"]["envelope_id"]
    assert context["provider_invocation_reference"]["invocation_id"]
    assert context["result_loop_reference"]["result_return_id"]
    assert validate_session_context(context)["valid"] is True


def test_session_context_rejects_hidden_memory_or_plans() -> None:
    context = _context()
    context["autonomous_plan_present"] = True

    assert validate_session_context(context)["valid"] is False
