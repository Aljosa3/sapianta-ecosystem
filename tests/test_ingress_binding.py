from sapianta_bridge.chatgpt_ingress.ingress_binding import (
    create_ingress_binding,
    validate_ingress_binding,
)
from sapianta_bridge.chatgpt_ingress.ingress_request import create_ingress_request
from sapianta_bridge.chatgpt_ingress.ingress_session import create_ingress_session
from sapianta_bridge.nl_envelope.envelope_generator import generate_envelope_proposal
from sapianta_bridge.nl_envelope.nl_request import create_nl_request


def _binding() -> dict:
    session = create_ingress_session(raw_text="Inspect governance evidence").to_dict()
    request = create_ingress_request(session=session, raw_text="Inspect governance evidence").to_dict()
    proposal = generate_envelope_proposal(create_nl_request("Inspect governance evidence"))
    return create_ingress_binding(ingress_request=request, envelope_proposal=proposal).to_dict()


def test_ingress_binding_is_deterministic_and_replay_safe() -> None:
    first = _binding()
    second = _binding()

    assert first == second
    assert first["replay_safe"] is True
    assert validate_ingress_binding(first)["valid"] is True


def test_ingress_binding_hash_mismatch_fails_closed() -> None:
    binding = _binding()
    binding["ingress_binding_sha256"] = "bad"

    result = validate_ingress_binding(binding)

    assert result["valid"] is False
    assert {"field": "ingress_binding_sha256", "reason": "ingress binding hash mismatch"} in result["errors"]


def test_ingress_binding_requires_semantic_lineage() -> None:
    binding = _binding()
    binding["semantic_request_id"] = ""

    result = validate_ingress_binding(binding)

    assert result["valid"] is False
    assert {"field": "semantic_request_id", "reason": "binding field must be non-empty"} in result["errors"]
