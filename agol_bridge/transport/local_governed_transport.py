"""Pure local governed semantic transport handler."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any

TRANSPORT_ACCEPTED = "TRANSPORT_ACCEPTED"
TRANSPORT_REJECTED_SCHEMA = "TRANSPORT_REJECTED_SCHEMA"
TRANSPORT_REJECTED_HASH = "TRANSPORT_REJECTED_HASH"
TRANSPORT_REJECTED_SESSION = "TRANSPORT_REJECTED_SESSION"
TRANSPORT_REJECTED_AUTHORITY = "TRANSPORT_REJECTED_AUTHORITY"
TRANSPORT_REJECTED_UNSAFE_MODE = "TRANSPORT_REJECTED_UNSAFE_MODE"
TRANSPORT_REJECTED_REPLAY_POLICY = "TRANSPORT_REJECTED_REPLAY_POLICY"

TRANSPORT_STATUSES = (
    TRANSPORT_ACCEPTED,
    TRANSPORT_REJECTED_SCHEMA,
    TRANSPORT_REJECTED_HASH,
    TRANSPORT_REJECTED_SESSION,
    TRANSPORT_REJECTED_AUTHORITY,
    TRANSPORT_REJECTED_UNSAFE_MODE,
    TRANSPORT_REJECTED_REPLAY_POLICY,
)

REQUIRED_ENVELOPE_FIELDS = (
    "transport_id",
    "session_id",
    "proposal_id",
    "artifact_hash",
    "created_at_policy",
    "source_label",
    "semantic_proposal",
    "authority_boundary_statement",
    "replay_policy",
    "lifecycle_policy",
)

REQUIRED_PROPOSAL_FIELDS = (
    "human_request",
    "semantic_intent",
    "proposed_mode",
    "risk_class",
    "authority_boundary_statement",
    "semantic_boundary_statement",
    "requested_action_type",
)

ALLOWED_PROPOSED_MODES = ("READ_ONLY", "REVIEW_ONLY", "DEMO_ONLY")
ALLOWED_REQUESTED_ACTION_TYPES = ("READ_ONLY", "REVIEW_ONLY", "DEMO_ONLY", "OBSERVE_ONLY", "OBSERVE_CONTINUITY_ONLY")
UNSAFE_PROPOSED_MODES = ("EXECUTE", "AUTO_EXECUTE", "AUTONOMOUS", "PROVIDER_RUNTIME", "ORCHESTRATION")
AUTHORITY_FORBIDDEN_TERMS = (
    "approve",
    "approval",
    "approved",
    "dispatch",
    "execute",
    "execution",
    "provider runtime",
    "provider dispatch",
    "orchestration",
    "autonomous continuation",
    "continuation authority",
)

NON_AUTHORITY_LABELS = (
    "SEMANTIC_TRANSPORT_ONLY",
    "SESSION_REPLAY_ONLY",
    "HASH_VERIFIED_IS_INTEGRITY_ONLY",
    "CERTIFIED_FOR_CONTINUITY_INGESTION_IS_NOT_APPROVAL",
    "CONTINUITY_VISIBLE_IS_NOT_EXECUTION_AUTHORIZATION",
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def canonical_hash(value: Any) -> str:
    return f"sha256:{hashlib.sha256(canonical_json(value).encode('utf-8')).hexdigest()}"


def semantic_proposal_hash(proposal: dict) -> str:
    proposal_copy = deepcopy(proposal)
    proposal_copy.pop("artifact_hash", None)
    return canonical_hash(proposal_copy)


def _blank_report(envelope: Any, status: str, rejection_reason: str) -> dict:
    transport_id = _field(envelope, "transport_id")
    session_id = _field(envelope, "session_id")
    proposal_id = _field(envelope, "proposal_id")
    artifact_hash = _field(envelope, "artifact_hash")
    source_label = _field(envelope, "source_label")
    created_at_policy = _field(envelope, "created_at_policy")
    event = _transport_event(
        status=status,
        transport_id=transport_id,
        session_id=session_id,
        proposal_id=proposal_id,
        artifact_hash=artifact_hash,
        source_label=source_label,
        created_at_policy=created_at_policy,
        hash_verification_status="HASH_NOT_VERIFIED" if status == TRANSPORT_REJECTED_SCHEMA else "HASH_PENDING",
        rejection_reason=rejection_reason,
    )
    return {
        "status": status,
        "transport_id": transport_id,
        "session_id": session_id,
        "proposal_id": proposal_id,
        "replay_event_id": event["replay_event_id"],
        "hash_verification_status": event["hash_verification_status"],
        "authority_label": "SEMANTIC_TRANSPORT_ONLY",
        "rejection_reason": rejection_reason,
        "validation": {"valid": status == TRANSPORT_ACCEPTED, "errors": [] if status == TRANSPORT_ACCEPTED else [rejection_reason]},
        "transport_event": event,
        "operator_visibility": _operator_visibility(event),
        "non_authority_guarantees": list(NON_AUTHORITY_LABELS),
    }


def _field(envelope: Any, field: str) -> str:
    if isinstance(envelope, dict):
        value = envelope.get(field, "UNKNOWN")
        if isinstance(value, str) and value:
            return value
    return "UNKNOWN"


def _transport_event(
    *,
    status: str,
    transport_id: str,
    session_id: str,
    proposal_id: str,
    artifact_hash: str,
    source_label: str,
    created_at_policy: str,
    hash_verification_status: str,
    rejection_reason: str,
) -> dict:
    seed = {
        "artifact_hash": artifact_hash,
        "created_at_policy": created_at_policy,
        "proposal_id": proposal_id,
        "session_id": session_id,
        "source_label": source_label,
        "transport_id": transport_id,
        "transport_status": status,
    }
    return {
        "replay_event_id": f"TRANSPORT-REPLAY-{canonical_hash(seed)[7:31]}",
        "event_type": "LOCAL_GOVERNED_SEMANTIC_TRANSPORT",
        "transport_status": status,
        "transport_id": transport_id,
        "session_id": session_id,
        "proposal_id": proposal_id,
        "artifact_hash": artifact_hash,
        "hash_verification_status": hash_verification_status,
        "source_label": source_label,
        "authority_label": "SEMANTIC_TRANSPORT_ONLY",
        "rejection_reason": rejection_reason,
        "lineage_refs": {
            "transport_id": transport_id,
            "session_id": session_id,
            "proposal_id": proposal_id,
            "artifact_hash": artifact_hash,
        },
        "visibility_scope": "SESSION_LOCAL_APPEND_CANDIDATE_ONLY",
        "created_at_policy": created_at_policy,
    }


def _operator_visibility(event: dict) -> dict:
    return {
        "transport_event_visible": True,
        "session_attachment_visible": event["session_id"] != "UNKNOWN",
        "replay_event_id_visible": True,
        "hash_verification_visible": True,
        "authority_label_visible": True,
        "rejection_reason_visible": event["rejection_reason"] != "",
        "source_label_visible": event["source_label"] != "UNKNOWN",
        "proposal_id_visible": event["proposal_id"] != "UNKNOWN",
        "transport_id_visible": event["transport_id"] != "UNKNOWN",
    }


def _schema_error(envelope: Any) -> str | None:
    if not isinstance(envelope, dict):
        return "transport envelope must be an object"
    missing = [field for field in REQUIRED_ENVELOPE_FIELDS if field not in envelope]
    if missing:
        return f"missing required fields: {', '.join(missing)}"
    string_fields = ("transport_id", "session_id", "proposal_id", "artifact_hash", "created_at_policy", "source_label")
    invalid_strings = [field for field in string_fields if not isinstance(envelope.get(field), str) or not envelope.get(field)]
    if invalid_strings:
        return f"invalid string fields: {', '.join(invalid_strings)}"
    if not isinstance(envelope.get("semantic_proposal"), dict):
        return "semantic_proposal must be an object"
    if not isinstance(envelope.get("authority_boundary_statement"), str):
        return "authority_boundary_statement must be a string"
    if not isinstance(envelope.get("replay_policy"), dict):
        return "replay_policy must be an object"
    if not isinstance(envelope.get("lifecycle_policy"), dict):
        return "lifecycle_policy must be an object"
    proposal = envelope["semantic_proposal"]
    missing_proposal = [field for field in REQUIRED_PROPOSAL_FIELDS if field not in proposal]
    if missing_proposal:
        return f"missing semantic proposal fields: {', '.join(missing_proposal)}"
    return None


def _session_error(session_id: str, session_registry: Any) -> str | None:
    if not isinstance(session_registry, dict):
        return "session_registry must be an object"
    if session_id not in session_registry:
        return "session_id is missing or unknown"
    session = session_registry[session_id]
    if isinstance(session, list):
        return "session_id is ambiguous"
    if not isinstance(session, dict):
        return "session attachment must be an object"
    if session.get("operator_visible") is not True:
        return "session attachment is not operator-visible"
    if session.get("ambiguous") is True:
        return "session_id is ambiguous"
    if session.get("continuation_requested") is True:
        return "session requests continuation"
    if session.get("cross_session_mutation") is True:
        return "session requests cross-session mutation"
    return None


def _unsafe_mode_error(proposal: dict) -> str | None:
    mode = proposal.get("proposed_mode")
    if mode in UNSAFE_PROPOSED_MODES:
        return f"unsafe proposed_mode: {mode}"
    if mode not in ALLOWED_PROPOSED_MODES:
        return f"unsupported proposed_mode: {mode}"
    return None


def _hash_error(envelope: dict) -> tuple[str | None, str]:
    artifact_hash = envelope["artifact_hash"]
    if not isinstance(artifact_hash, str) or not artifact_hash.startswith("sha256:") or len(artifact_hash) != 71:
        return "artifact_hash is missing or malformed", "HASH_INVALID"
    expected = semantic_proposal_hash(envelope["semantic_proposal"])
    if artifact_hash != expected:
        return "artifact_hash mismatch", "HASH_MISMATCH"
    return None, "HASH_VERIFIED"


def _contains_forbidden_authority_claim(value: Any) -> bool:
    lowered = canonical_json(value).lower()
    for term in AUTHORITY_FORBIDDEN_TERMS:
        allowed_negations = (
            f"no {term}",
            f"not {term}",
            f"non-{term}",
            f"without {term}",
            f"{term} is not",
            f"grants no {term}",
            f"grant no {term}",
            "grants no approval, dispatch, execution",
            "does not create governance decisions or execution authority",
        )
        if term in lowered and not any(negation in lowered for negation in allowed_negations):
            return True
    return False


def _authority_error(envelope: dict) -> str | None:
    statement = envelope["authority_boundary_statement"].lower()
    required = ("transport", "not approval", "not dispatch", "not execution", "not continuation")
    if not all(term in statement for term in required):
        return "authority boundary statement is incomplete"
    requested_action = str(envelope["semantic_proposal"].get("requested_action_type", ""))
    if requested_action not in ALLOWED_REQUESTED_ACTION_TYPES:
        return "requested action type is outside semantic transport authority"
    authority_values = {
        "envelope_authority_boundary_statement": envelope["authority_boundary_statement"],
        "proposal_authority_boundary_statement": envelope["semantic_proposal"].get("authority_boundary_statement", ""),
        "semantic_intent": envelope["semantic_proposal"].get("semantic_intent", ""),
    }
    if _contains_forbidden_authority_claim(authority_values):
        return "authority, execution, dispatch, provider, orchestration, or continuation claim detected"
    return None


def _policy_error(envelope: dict) -> str | None:
    replay_policy = envelope["replay_policy"]
    lifecycle_policy = envelope["lifecycle_policy"]
    if replay_policy.get("append_only") is not True:
        return "replay policy must be append-only"
    if replay_policy.get("visibility_only") is not True:
        return "replay policy must be visibility-only"
    forbidden_replay_flags = ("rewrite_allowed", "repair_allowed", "mutation_allowed", "inference_allowed", "durable_backend")
    for flag in forbidden_replay_flags:
        if replay_policy.get(flag) is True:
            return f"replay policy violates bounded transport: {flag}"
    if lifecycle_policy.get("visibility_only") is not True:
        return "lifecycle policy must be visibility-only"
    if lifecycle_policy.get("execution_transition") is True or lifecycle_policy.get("mutation_allowed") is True:
        return "lifecycle policy requests mutation or execution transition"
    return None


def _accepted_report(envelope: dict) -> dict:
    event = _transport_event(
        status=TRANSPORT_ACCEPTED,
        transport_id=envelope["transport_id"],
        session_id=envelope["session_id"],
        proposal_id=envelope["proposal_id"],
        artifact_hash=envelope["artifact_hash"],
        source_label=envelope["source_label"],
        created_at_policy=envelope["created_at_policy"],
        hash_verification_status="HASH_VERIFIED",
        rejection_reason="",
    )
    return {
        "status": TRANSPORT_ACCEPTED,
        "transport_id": envelope["transport_id"],
        "session_id": envelope["session_id"],
        "proposal_id": envelope["proposal_id"],
        "replay_event_id": event["replay_event_id"],
        "hash_verification_status": "HASH_VERIFIED",
        "authority_label": "SEMANTIC_TRANSPORT_ONLY",
        "rejection_reason": "",
        "validation": {"valid": True, "errors": []},
        "transport_event": event,
        "operator_visibility": _operator_visibility(event),
        "non_authority_guarantees": list(NON_AUTHORITY_LABELS),
    }


def _rejected_report(envelope: Any, status: str, rejection_reason: str, hash_status: str | None = None) -> dict:
    report = _blank_report(envelope, status, rejection_reason)
    if hash_status is not None:
        report["hash_verification_status"] = hash_status
        report["transport_event"]["hash_verification_status"] = hash_status
    return report


def handle_local_governed_transport(*, envelope: dict, session_registry: dict) -> dict:
    envelope_copy = deepcopy(envelope)
    session_registry_copy = deepcopy(session_registry)

    schema_error = _schema_error(envelope_copy)
    if schema_error is not None:
        return _rejected_report(envelope_copy, TRANSPORT_REJECTED_SCHEMA, schema_error)

    session_error = _session_error(envelope_copy["session_id"], session_registry_copy)
    if session_error is not None:
        return _rejected_report(envelope_copy, TRANSPORT_REJECTED_SESSION, session_error)

    unsafe_mode_error = _unsafe_mode_error(envelope_copy["semantic_proposal"])
    if unsafe_mode_error is not None:
        return _rejected_report(envelope_copy, TRANSPORT_REJECTED_UNSAFE_MODE, unsafe_mode_error)

    hash_error, hash_status = _hash_error(envelope_copy)
    if hash_error is not None:
        return _rejected_report(envelope_copy, TRANSPORT_REJECTED_HASH, hash_error, hash_status)

    authority_error = _authority_error(envelope_copy)
    if authority_error is not None:
        return _rejected_report(envelope_copy, TRANSPORT_REJECTED_AUTHORITY, authority_error, "HASH_VERIFIED")

    policy_error = _policy_error(envelope_copy)
    if policy_error is not None:
        return _rejected_report(envelope_copy, TRANSPORT_REJECTED_REPLAY_POLICY, policy_error, "HASH_VERIFIED")

    return _accepted_report(envelope_copy)


__all__ = [
    "ALLOWED_PROPOSED_MODES",
    "ALLOWED_REQUESTED_ACTION_TYPES",
    "TRANSPORT_ACCEPTED",
    "TRANSPORT_REJECTED_AUTHORITY",
    "TRANSPORT_REJECTED_HASH",
    "TRANSPORT_REJECTED_REPLAY_POLICY",
    "TRANSPORT_REJECTED_SCHEMA",
    "TRANSPORT_REJECTED_SESSION",
    "TRANSPORT_REJECTED_UNSAFE_MODE",
    "TRANSPORT_STATUSES",
    "canonical_hash",
    "handle_local_governed_transport",
    "semantic_proposal_hash",
]
