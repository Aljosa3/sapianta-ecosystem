from copy import deepcopy
from pathlib import Path

from agol_bridge.transport.local_governed_transport import (
    TRANSPORT_ACCEPTED,
    TRANSPORT_REJECTED_AUTHORITY,
    TRANSPORT_REJECTED_HASH,
    TRANSPORT_REJECTED_REPLAY_POLICY,
    TRANSPORT_REJECTED_SCHEMA,
    TRANSPORT_REJECTED_SESSION,
    TRANSPORT_REJECTED_UNSAFE_MODE,
    handle_local_governed_transport,
    semantic_proposal_hash,
)


def _proposal():
    proposal = {
        "human_request": "Review this governance transport proposal.",
        "semantic_intent": "Create read-only continuity visibility for a bounded semantic proposal.",
        "proposed_mode": "REVIEW_ONLY",
        "risk_class": "LOW",
        "authority_boundary_statement": "Semantic proposal only; no approval, no dispatch, no execution, no continuation.",
        "semantic_boundary_statement": "Semantic cognition is non-authoritative and not deterministic replay.",
        "requested_action_type": "REVIEW_ONLY",
    }
    proposal["artifact_hash"] = semantic_proposal_hash(proposal)
    return proposal


def _envelope():
    proposal = _proposal()
    return {
        "transport_id": "TRANSPORT-1",
        "session_id": "SESSION-1",
        "proposal_id": "PROPOSAL-1",
        "artifact_hash": proposal["artifact_hash"],
        "created_at_policy": "EXPLICIT_FIXTURE_TIME",
        "source_label": "CHATGPT_LOCAL_ARTIFACT",
        "semantic_proposal": proposal,
        "authority_boundary_statement": (
            "Semantic transport only; transport success is not approval, not dispatch, "
            "not execution, and not continuation authority."
        ),
        "replay_policy": {
            "append_only": True,
            "visibility_only": True,
            "rewrite_allowed": False,
            "repair_allowed": False,
            "mutation_allowed": False,
            "inference_allowed": False,
            "durable_backend": False,
        },
        "lifecycle_policy": {
            "visibility_only": True,
            "execution_transition": False,
            "mutation_allowed": False,
        },
    }


def _session_registry():
    return {
        "SESSION-1": {
            "operator_visible": True,
            "ambiguous": False,
            "continuation_requested": False,
            "cross_session_mutation": False,
        }
    }


def test_valid_envelope_is_accepted():
    report = handle_local_governed_transport(envelope=_envelope(), session_registry=_session_registry())

    assert report["status"] == TRANSPORT_ACCEPTED
    assert report["validation"]["valid"] is True
    assert report["hash_verification_status"] == "HASH_VERIFIED"
    assert report["authority_label"] == "SEMANTIC_TRANSPORT_ONLY"
    assert report["transport_event"]["visibility_scope"] == "SESSION_LOCAL_APPEND_CANDIDATE_ONLY"
    assert "SEMANTIC_TRANSPORT_ONLY" in report["non_authority_guarantees"]


def test_missing_fields_are_rejected():
    envelope = _envelope()
    envelope.pop("transport_id")

    report = handle_local_governed_transport(envelope=envelope, session_registry=_session_registry())

    assert report["status"] == TRANSPORT_REJECTED_SCHEMA
    assert "missing required fields" in report["rejection_reason"]


def test_hash_mismatch_is_rejected():
    envelope = _envelope()
    envelope["artifact_hash"] = "sha256:" + "0" * 64

    report = handle_local_governed_transport(envelope=envelope, session_registry=_session_registry())

    assert report["status"] == TRANSPORT_REJECTED_HASH
    assert report["hash_verification_status"] == "HASH_MISMATCH"
    assert report["rejection_reason"] == "artifact_hash mismatch"


def test_malformed_hash_is_rejected():
    envelope = _envelope()
    envelope["artifact_hash"] = "not-a-hash"

    report = handle_local_governed_transport(envelope=envelope, session_registry=_session_registry())

    assert report["status"] == TRANSPORT_REJECTED_HASH
    assert report["hash_verification_status"] == "HASH_INVALID"


def test_missing_unknown_and_non_visible_session_are_rejected():
    envelope = _envelope()
    envelope["session_id"] = "UNKNOWN"
    assert handle_local_governed_transport(envelope=envelope, session_registry=_session_registry())["status"] == (
        TRANSPORT_REJECTED_SESSION
    )

    envelope = _envelope()
    assert handle_local_governed_transport(envelope=envelope, session_registry={})["status"] == TRANSPORT_REJECTED_SESSION

    registry = _session_registry()
    registry["SESSION-1"]["operator_visible"] = False
    assert handle_local_governed_transport(envelope=_envelope(), session_registry=registry)["status"] == (
        TRANSPORT_REJECTED_SESSION
    )


def test_ambiguous_session_is_rejected():
    registry = {"SESSION-1": [{"operator_visible": True}, {"operator_visible": True}]}

    report = handle_local_governed_transport(envelope=_envelope(), session_registry=registry)

    assert report["status"] == TRANSPORT_REJECTED_SESSION
    assert "ambiguous" in report["rejection_reason"]


def test_unsafe_mode_is_rejected():
    envelope = _envelope()
    envelope["semantic_proposal"]["proposed_mode"] = "EXECUTE"
    envelope["semantic_proposal"]["artifact_hash"] = semantic_proposal_hash(envelope["semantic_proposal"])
    envelope["artifact_hash"] = envelope["semantic_proposal"]["artifact_hash"]

    report = handle_local_governed_transport(envelope=envelope, session_registry=_session_registry())

    assert report["status"] == TRANSPORT_REJECTED_UNSAFE_MODE


def test_authority_claims_are_rejected():
    envelope = _envelope()
    envelope["semantic_proposal"]["requested_action_type"] = "dispatch provider execution"
    envelope["semantic_proposal"]["artifact_hash"] = semantic_proposal_hash(envelope["semantic_proposal"])
    envelope["artifact_hash"] = envelope["semantic_proposal"]["artifact_hash"]

    report = handle_local_governed_transport(envelope=envelope, session_registry=_session_registry())

    assert report["status"] == TRANSPORT_REJECTED_AUTHORITY


def test_replay_policy_violations_are_rejected():
    envelope = _envelope()
    envelope["replay_policy"]["rewrite_allowed"] = True

    report = handle_local_governed_transport(envelope=envelope, session_registry=_session_registry())

    assert report["status"] == TRANSPORT_REJECTED_REPLAY_POLICY


def test_lifecycle_policy_mutation_is_rejected_as_replay_policy_boundary():
    envelope = _envelope()
    envelope["lifecycle_policy"]["execution_transition"] = True

    report = handle_local_governed_transport(envelope=envelope, session_registry=_session_registry())

    assert report["status"] == TRANSPORT_REJECTED_REPLAY_POLICY


def test_replay_event_id_is_deterministic():
    first = handle_local_governed_transport(envelope=_envelope(), session_registry=_session_registry())
    second = handle_local_governed_transport(envelope=_envelope(), session_registry=_session_registry())

    assert first["replay_event_id"] == second["replay_event_id"]
    assert first["transport_event"] == second["transport_event"]
    assert first == second


def test_append_candidate_only_no_replay_mutation():
    report = handle_local_governed_transport(envelope=_envelope(), session_registry=_session_registry())

    assert report["transport_event"]["visibility_scope"] == "SESSION_LOCAL_APPEND_CANDIDATE_ONLY"
    assert "append_replay" not in str(report).lower()
    assert "durable" not in report["transport_event"]["visibility_scope"].lower()


def test_inputs_are_not_mutated():
    envelope = _envelope()
    registry = _session_registry()
    before_envelope = deepcopy(envelope)
    before_registry = deepcopy(registry)

    handle_local_governed_transport(envelope=envelope, session_registry=registry)

    assert envelope == before_envelope
    assert registry == before_registry


def test_no_provider_dispatch_approval_execution_or_orchestration_behavior_is_introduced():
    source = (Path(__file__).resolve().parents[1] / "agol_bridge/transport/local_governed_transport.py").read_text()
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
    )
    for token in forbidden:
        assert token not in source
