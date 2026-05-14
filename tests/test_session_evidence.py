from sapianta_bridge.active_invocation.invocation_bridge import invoke_provider
from sapianta_bridge.chatgpt_ingress.ingress_bridge import process_chatgpt_ingress
from sapianta_bridge.providers.adapters.deterministic_mock_adapter import DeterministicMockAdapter
from sapianta_bridge.result_loop.result_return_loop import return_invocation_result
from sapianta_bridge.governed_session.session_bridge import create_governed_execution_session
from sapianta_bridge.governed_session.session_evidence import validate_session_evidence


def _session_evidence() -> dict:
    ingress = process_chatgpt_ingress("Inspect governance evidence", provider_id="deterministic_mock")
    invocation = invoke_provider(
        envelope=ingress["envelope_proposal"]["execution_envelope"],
        provider=DeterministicMockAdapter(),
    )
    result = return_invocation_result(
        invocation_result=invocation["invocation_result"],
        invocation_evidence=invocation["invocation_evidence"],
    )
    session = create_governed_execution_session(
        ingress_output=ingress,
        invocation_output=invocation,
        result_output=result,
    )
    return session["session_evidence"]


def test_session_evidence_is_replay_safe_and_valid() -> None:
    evidence = _session_evidence()

    assert evidence["replay_safe"] is True
    assert evidence["session_status"] == "COMPLETED"
    assert validate_session_evidence(evidence)["valid"] is True


def test_session_evidence_rejects_forbidden_behavior_flags() -> None:
    evidence = _session_evidence()
    evidence["orchestration_introduced"] = True

    assert validate_session_evidence(evidence)["valid"] is False
