from copy import deepcopy
from pathlib import Path

import pytest

from agol_bridge.chat_first.chat_first_normalization import (
    AUTHORITY_BOUNDARY_STATEMENT,
    SEMANTIC_BOUNDARY_STATEMENT,
    normalize_human_request_to_semantic_proposal,
    prepare_chat_first_transport_envelope,
)
from agol_bridge.transport.local_governed_transport import (
    TRANSPORT_ACCEPTED,
    TRANSPORT_REJECTED_SESSION,
    handle_local_governed_transport,
    semantic_proposal_hash,
)


def _session_registry():
    return {
        "SESSION-CHAT-FIRST": {
            "operator_visible": True,
            "ambiguous": False,
            "continuation_requested": False,
            "cross_session_mutation": False,
        }
    }


def test_valid_request_normalizes_deterministically():
    first = normalize_human_request_to_semantic_proposal(human_request="Review this governance idea.")
    second = normalize_human_request_to_semantic_proposal(human_request="Review this governance idea.")

    assert first == second
    assert first["proposed_mode"] == "REVIEW_ONLY"
    assert first["requested_action_type"] == "REVIEW_ONLY"
    assert first["authority_boundary_statement"] == AUTHORITY_BOUNDARY_STATEMENT
    assert first["semantic_boundary_statement"] == SEMANTIC_BOUNDARY_STATEMENT
    assert first["proposal_id"].startswith("CHAT-FIRST-PROPOSAL-")


def test_artifact_hash_is_deterministic_and_excludes_artifact_hash_itself():
    proposal = normalize_human_request_to_semantic_proposal(human_request="Review hash semantics.")
    proposal_with_wrong_hash = deepcopy(proposal)
    proposal_with_wrong_hash["artifact_hash"] = "sha256:" + "0" * 64

    assert proposal["artifact_hash"] == semantic_proposal_hash(proposal)
    assert semantic_proposal_hash(proposal) == semantic_proposal_hash(proposal_with_wrong_hash)


def test_empty_request_is_rejected():
    with pytest.raises(ValueError, match="human_request is required"):
        normalize_human_request_to_semantic_proposal(human_request="   ")


def test_unsafe_modes_are_rejected():
    for mode in ("EXECUTE", "AUTO_EXECUTE", "PROVIDER_RUNTIME", "ORCHESTRATION", "AUTONOMOUS"):
        with pytest.raises(ValueError, match="unsafe requested_mode"):
            normalize_human_request_to_semantic_proposal(human_request="Review safely.", requested_mode=mode)


def test_execution_wording_does_not_create_execution_authority():
    proposal = normalize_human_request_to_semantic_proposal(
        human_request="Can you execute this idea? I need a review only.",
        requested_mode="READ_ONLY",
    )

    assert proposal["proposed_mode"] == "READ_ONLY"
    assert "NO_EXECUTION" in proposal["authority_boundary_statement"]
    assert "does not infer execution authority" in proposal["semantic_boundary_statement"]
    assert proposal["requested_action_type"] == "READ_ONLY"


def test_transport_envelope_is_accepted_by_local_handler_with_valid_session_registry():
    envelope = prepare_chat_first_transport_envelope(
        human_request="Review this chat-first request.",
        session_id="SESSION-CHAT-FIRST",
    )

    report = handle_local_governed_transport(envelope=envelope, session_registry=_session_registry())

    assert report["status"] == TRANSPORT_ACCEPTED
    assert envelope["source_label"] == "CHAT_FIRST_LOCAL_NORMALIZATION"
    assert envelope["session_id"] == "SESSION-CHAT-FIRST"
    assert envelope["artifact_hash"] == envelope["semantic_proposal"]["artifact_hash"]
    assert report["hash_verification_status"] == "HASH_VERIFIED"


def test_unknown_session_is_rejected_through_transport_handler():
    envelope = prepare_chat_first_transport_envelope(
        human_request="Review this chat-first request.",
        session_id="UNKNOWN-SESSION",
    )

    report = handle_local_governed_transport(envelope=envelope, session_registry=_session_registry())

    assert report["status"] == TRANSPORT_REJECTED_SESSION


def test_transport_envelope_creation_does_not_mutate_inputs():
    request = "Review immutability."
    session = "SESSION-CHAT-FIRST"

    first = prepare_chat_first_transport_envelope(human_request=request, session_id=session)
    second = prepare_chat_first_transport_envelope(human_request=request, session_id=session)

    assert first == second


def test_no_provider_dispatch_approval_execution_or_orchestration_behavior():
    source = (Path(__file__).resolve().parents[1] / "agol_bridge/chat_first/chat_first_normalization.py").read_text()
    forbidden = (
        "open(",
        "Path(",
        "read_text",
        "write_text",
        "requests.",
        "urllib",
        "socket",
        "subprocess",
        "threading",
        "Timer",
        "fetch",
        "chrome.",
        "provider.call",
        "dispatch_task",
        "approve_task",
        "execute_governed",
        "orchestrate",
        "serve_forever",
        "HTTPServer",
        "localStorage",
        "sessionStorage",
    )
    for token in forbidden:
        assert token not in source


def test_no_persistence_or_endpoint_is_introduced():
    source = (Path(__file__).resolve().parents[1] / "agol_bridge/chat_first/chat_first_normalization.py").read_text()

    assert "HTTP" not in source
    assert "endpoint" not in source.lower()
    assert "storage" not in source.lower()
