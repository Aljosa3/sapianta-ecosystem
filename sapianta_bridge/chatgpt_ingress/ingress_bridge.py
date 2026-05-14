"""Canonical ChatGPT ingress bridge.

This bridge performs semantic preparation only. It never invokes providers,
transport, runtime adapters, shell commands, network calls, or background work.
"""

from __future__ import annotations

from typing import Any

from sapianta_bridge.nl_envelope.envelope_generator import generate_envelope_proposal
from sapianta_bridge.nl_envelope.nl_request import create_nl_request

from .ingress_binding import create_ingress_binding
from .ingress_evidence import ingress_evidence
from .ingress_request import create_ingress_request
from .ingress_session import create_ingress_session
from .ingress_validator import validate_ingress_state


def process_chatgpt_ingress(
    raw_text: str,
    *,
    timestamp: str = "1970-01-01T00:00:00Z",
    conversation_id: str = "CHATGPT-SESSION",
    provider_id: str = "deterministic_mock",
) -> dict[str, Any]:
    session = create_ingress_session(
        raw_text=raw_text,
        timestamp=timestamp,
        conversation_id=conversation_id,
    ).to_dict()
    request = create_ingress_request(session=session, raw_text=raw_text).to_dict()
    nl_request = create_nl_request(raw_text)
    proposal = generate_envelope_proposal(nl_request, provider_id=provider_id)
    binding = create_ingress_binding(ingress_request=request, envelope_proposal=proposal).to_dict()
    validation = validate_ingress_state(
        session=session,
        request=request,
        proposal=proposal,
        binding=binding,
    )
    evidence = ingress_evidence(
        session=session,
        request=request,
        proposal=proposal,
        binding=binding,
        validation=validation,
    )
    return {
        "session": session,
        "ingress_request": request,
        "envelope_proposal": proposal,
        "ingress_binding": binding,
        "ingress_validation": validation,
        "ingress_evidence": evidence,
        "provider_invoked": False,
        "transport_executed": False,
        "runtime_executed": False,
        "execution_authority_granted": False,
    }
