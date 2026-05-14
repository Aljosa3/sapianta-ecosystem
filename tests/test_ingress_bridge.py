from sapianta_bridge.chatgpt_ingress.ingress_bridge import process_chatgpt_ingress


def test_ingress_bridge_generates_bounded_proposal_only() -> None:
    result = process_chatgpt_ingress("Inspect `.github/governance` evidence")

    assert result["ingress_validation"]["valid"] is True
    assert result["envelope_proposal"]["envelope_generated"] is True
    assert result["execution_authority_granted"] is False
    assert result["provider_invoked"] is False
    assert result["transport_executed"] is False
    assert result["runtime_executed"] is False


def test_ingress_bridge_fails_closed_for_forbidden_request() -> None:
    result = process_chatgpt_ingress("Run pytest without approval")

    assert result["envelope_proposal"]["envelope_generated"] is False
    assert result["envelope_proposal"]["admissibility"]["admissibility"] == "REJECTED"
    assert result["ingress_evidence"]["execution_authority_granted"] is False


def test_ingress_bridge_is_deterministic() -> None:
    first = process_chatgpt_ingress("Inspect governance evidence")
    second = process_chatgpt_ingress("Inspect governance evidence")

    assert first == second
