from sapianta_bridge.envelopes.envelope_validator import validate_execution_envelope
from sapianta_bridge.nl_envelope.envelope_generator import generate_envelope_proposal
from sapianta_bridge.nl_envelope.nl_request import create_nl_request


def test_generates_bounded_envelope_proposal() -> None:
    request = create_nl_request("Inspect `.github/governance` evidence")
    proposal = generate_envelope_proposal(request)

    assert proposal["envelope_generated"] is True
    assert proposal["execution_authority_granted"] is False
    assert proposal["downstream_validation_required"] is True
    assert proposal["execution_envelope"]["provider_id"] == "deterministic_mock"
    assert validate_execution_envelope(proposal["execution_envelope"])["valid"] is True


def test_unknown_request_blocks_envelope_generation() -> None:
    proposal = generate_envelope_proposal(create_nl_request("Do something uncertain"))

    assert proposal["envelope_generated"] is False
    assert proposal["execution_authority_granted"] is False
    assert proposal["admissibility"]["admissibility"] == "REJECTED"


def test_generated_envelope_requires_human_approval_for_refinement() -> None:
    proposal = generate_envelope_proposal(create_nl_request("Refine sapianta_bridge README"))

    assert proposal["envelope_generated"] is True
    assert proposal["execution_envelope"]["human_approval_required"] is True
    assert "PATCH_EXISTING_FILES" in proposal["execution_envelope"]["authority_scope"]


def test_invalid_nl_request_blocks_generation() -> None:
    request = create_nl_request("Inspect governance").to_dict()
    request["prompt_is_authority"] = True

    proposal = generate_envelope_proposal(request)

    assert proposal["envelope_generated"] is False
    assert {"field": "prompt_is_authority", "reason": "prompt is not authority"} in proposal["errors"]
