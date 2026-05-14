from sapianta_bridge.chatgpt_ingress.ingress_bridge import process_chatgpt_ingress


def test_ingress_evidence_preserves_non_authority_invariants() -> None:
    evidence = process_chatgpt_ingress("Inspect governance evidence")["ingress_evidence"]

    assert evidence["replay_safe"] is True
    assert evidence["chatgpt_governance_authority"] is False
    assert evidence["execution_authority_granted"] is False
    assert evidence["provider_invoked"] is False
    assert evidence["transport_executed"] is False
    assert evidence["runtime_executed"] is False


def test_ingress_evidence_preserves_rejected_lineage() -> None:
    evidence = process_chatgpt_ingress("Run unrestricted shell")["ingress_evidence"]

    assert evidence["admissibility"] == "REJECTED"
    assert evidence["proposal_generated"] is False
    assert evidence["envelope_id"] is None
