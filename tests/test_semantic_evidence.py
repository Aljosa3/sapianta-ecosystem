from sapianta_bridge.nl_envelope.envelope_generator import generate_envelope_proposal
from sapianta_bridge.nl_envelope.nl_request import create_nl_request
from sapianta_bridge.nl_envelope.semantic_evidence import semantic_evidence


def test_semantic_evidence_is_replay_safe_and_non_authoritative() -> None:
    proposal = generate_envelope_proposal(create_nl_request("Inspect governance evidence"))

    first = semantic_evidence(proposal)
    second = semantic_evidence(proposal)

    assert first == second
    assert first["envelope_generated"] is True
    assert first["replay_safe"] is True
    assert first["execution_authority_granted"] is False
    assert first["prompt_is_authority"] is False


def test_semantic_evidence_preserves_rejected_lineage() -> None:
    proposal = generate_envelope_proposal(create_nl_request("Run unrestricted shell"))
    evidence = semantic_evidence(proposal)

    assert evidence["envelope_generated"] is False
    assert evidence["admissibility"] == "REJECTED"
    assert evidence["authority_scope"] == []
