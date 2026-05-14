from sapianta_bridge.chatgpt_ingress.ingress_binding import create_ingress_binding
from sapianta_bridge.chatgpt_ingress.ingress_request import create_ingress_request
from sapianta_bridge.chatgpt_ingress.ingress_session import create_ingress_session
from sapianta_bridge.chatgpt_ingress.ingress_validator import validate_ingress_state
from sapianta_bridge.nl_envelope.envelope_generator import generate_envelope_proposal
from sapianta_bridge.nl_envelope.nl_request import create_nl_request


def _state(text: str = "Inspect governance evidence") -> tuple[dict, dict, dict, dict]:
    session = create_ingress_session(raw_text=text).to_dict()
    request = create_ingress_request(session=session, raw_text=text).to_dict()
    proposal = generate_envelope_proposal(create_nl_request(text))
    binding = create_ingress_binding(ingress_request=request, envelope_proposal=proposal).to_dict()
    return session, request, proposal, binding


def test_ingress_validator_accepts_valid_state() -> None:
    session, request, proposal, binding = _state()
    result = validate_ingress_state(session=session, request=request, proposal=proposal, binding=binding)

    assert result["valid"] is True
    assert result["chatgpt_is_governance"] is False
    assert result["ingress_is_execution_authority"] is False


def test_ingress_validator_blocks_rejected_proposal_generation() -> None:
    session, request, proposal, binding = _state("Run unrestricted shell")
    proposal["envelope_generated"] = True

    result = validate_ingress_state(session=session, request=request, proposal=proposal, binding=binding)

    assert result["valid"] is False
    assert {"field": "admissibility", "reason": "rejected ingress cannot generate envelope"} in result["errors"]


def test_ingress_validator_blocks_binding_mismatch() -> None:
    session, request, proposal, binding = _state()
    binding["envelope_id"] = "ENV-OTHER"

    result = validate_ingress_state(session=session, request=request, proposal=proposal, binding=binding)

    assert result["valid"] is False
    assert {"field": "binding", "reason": "invalid ingress binding"} in result["errors"]
