"""Pure deterministic chat-first normalization for governed semantic transport."""

from __future__ import annotations

from copy import deepcopy

from agol_bridge.transport.local_governed_transport import canonical_hash, semantic_proposal_hash

ALLOWED_REQUESTED_MODES = ("REVIEW_ONLY", "DEMO_ONLY", "READ_ONLY")
REJECTED_REQUESTED_MODES = ("EXECUTE", "AUTO_EXECUTE", "PROVIDER_RUNTIME", "ORCHESTRATION", "AUTONOMOUS")

AUTHORITY_BOUNDARY_STATEMENT = (
    "SEMANTIC_TRANSPORT_ONLY_NO_APPROVAL_NO_DISPATCH_NO_EXECUTION; "
    "Chat-first normalization creates no provider calls, no approval, no dispatch, "
    "no execution, no orchestration, and no autonomous continuation."
)
SEMANTIC_BOUNDARY_STATEMENT = (
    "SEMANTIC_COGNITION_NON_AUTHORITATIVE; deterministic normalization preserves request text as "
    "bounded semantic context only and does not infer execution authority."
)


def _normalize_mode(requested_mode: str) -> str:
    mode = str(requested_mode or "").strip().upper()
    if mode in REJECTED_REQUESTED_MODES or mode not in ALLOWED_REQUESTED_MODES:
        raise ValueError(f"unsafe requested_mode: {mode or 'UNKNOWN'}")
    return mode


def _normalize_request(human_request: str) -> str:
    request_text = str(human_request or "").strip()
    if not request_text:
        raise ValueError("human_request is required")
    return request_text


def _proposal_id(*, human_request: str, requested_mode: str, proposal_id: str | None) -> str:
    if proposal_id:
        return str(proposal_id)
    return f"CHAT-FIRST-PROPOSAL-{canonical_hash({'human_request': human_request, 'requested_mode': requested_mode})[7:31]}"


def normalize_human_request_to_semantic_proposal(
    *,
    human_request: str,
    requested_mode: str = "REVIEW_ONLY",
    proposal_id: str | None = None,
    session_id: str | None = None,
) -> dict:
    request_text = _normalize_request(human_request)
    mode = _normalize_mode(requested_mode)
    normalized_proposal_id = _proposal_id(
        human_request=request_text,
        requested_mode=mode,
        proposal_id=proposal_id,
    )
    proposal = {
        "human_request": request_text,
        "semantic_intent": f"Review bounded semantic direction for: {request_text}",
        "proposed_mode": mode,
        "risk_class": "LOW",
        "authority_boundary_statement": AUTHORITY_BOUNDARY_STATEMENT,
        "semantic_boundary_statement": SEMANTIC_BOUNDARY_STATEMENT,
        "requested_action_type": mode,
        "proposal_id": normalized_proposal_id,
    }
    if session_id is not None:
        proposal["session_id"] = str(session_id)
    proposal["artifact_hash"] = semantic_proposal_hash(proposal)
    return proposal


def prepare_chat_first_transport_envelope(
    *,
    human_request: str,
    session_id: str,
    requested_mode: str = "REVIEW_ONLY",
) -> dict:
    session_text = str(session_id or "").strip()
    if not session_text:
        raise ValueError("session_id is required")
    proposal = normalize_human_request_to_semantic_proposal(
        human_request=human_request,
        requested_mode=requested_mode,
        session_id=session_text,
    )
    envelope = {
        "transport_id": f"CHAT-FIRST-TRANSPORT-{canonical_hash({'proposal_id': proposal['proposal_id'], 'session_id': session_text})[7:31]}",
        "session_id": session_text,
        "proposal_id": proposal["proposal_id"],
        "artifact_hash": proposal["artifact_hash"],
        "created_at_policy": "DETERMINISTIC_CHAT_FIRST_NORMALIZATION",
        "source_label": "CHAT_FIRST_LOCAL_NORMALIZATION",
        "semantic_proposal": deepcopy(proposal),
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
    return envelope
