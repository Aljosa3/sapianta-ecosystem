"""Constitutional bindings across existing production Conversation owners.

This module creates reference-only evidence for the G66 production
Conversation composition.  It owns no Human intent, semantic interpretation,
clarification sufficiency, Platform routing, Objective, Governance,
Authorization, Worker, execution, Replay, or Presentation decision.  Every
decision is delegated to the existing certified owner and then bound here.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime import human_interface_conversation_runtime_v2 as hir_v2
from aigol.runtime import platform_core_conversation_interpreter_proposal_runtime_v2 as proposal_v2
from aigol.runtime import platform_core_conversation_objective_readiness_runtime_v2 as readiness_v2
from aigol.runtime import platform_core_conversation_proposal_commit_runtime_v2 as commit_v2
from aigol.runtime import platform_core_conversation_working_memory_runtime_v2 as cwm_v2
from aigol.runtime.human_execution_intent_detection import (
    GENERIC_GOVERNED_EXECUTION_REQUEST,
    detect_human_execution_intent,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_query_router import (
    PLATFORM_KNOWLEDGE_ROUTE,
    PLATFORM_QUERY_ROUTER_VERSION,
    REQUIRED_EVIDENCE_MISSING,
    ROUTE_CLARIFICATION_REQUIRED,
    SELF_KNOWLEDGE_ROUTE,
    select_platform_query_route,
)
from aigol.runtime.self_knowledge_request_classification import (
    CLARIFICATION_REQUIRED as SELF_KNOWLEDGE_CLARIFICATION_REQUIRED,
    SELF_KNOWLEDGE_QUERY,
    classify_self_knowledge_request,
    validate_self_knowledge_request_classification,
)
from aigol.runtime.transport.serialization import (
    load_json,
    replay_hash,
    write_json_immutable,
)


HUMAN_INTENT_PRECEDENCE_DECISION_V1 = "HUMAN_INTENT_PRECEDENCE_DECISION_V1"
OWNER_BOUND_CLARIFICATION_ENVELOPE_V1 = "OWNER_BOUND_CLARIFICATION_ENVELOPE_V1"
PRODUCTION_CONVERSATION_FLOW_BINDING_V1 = (
    "PRODUCTION_CONVERSATION_FLOW_BINDING_V1"
)

NEW_HUMAN_INTENT = "NEW_HUMAN_INTENT"
CLARIFICATION_REPLY = "CLARIFICATION_REPLY"
AMBIGUOUS_STATE_RELATIONSHIP = "AMBIGUOUS_STATE_RELATIONSHIP"
HUMAN_STOP = "HUMAN_STOP"
PRECEDENCE_DISPOSITIONS = frozenset(
    {
        NEW_HUMAN_INTENT,
        CLARIFICATION_REPLY,
        AMBIGUOUS_STATE_RELATIONSHIP,
        HUMAN_STOP,
    }
)

FLOW_SELECTED = "FLOW_SELECTED"
FLOW_CLARIFICATION_REQUIRED = "FLOW_CLARIFICATION_REQUIRED"
FLOW_FAILED_CLOSED = "FLOW_FAILED_CLOSED"
FLOW_SELECTION_DISPOSITIONS = frozenset(
    {FLOW_SELECTED, FLOW_CLARIFICATION_REQUIRED, FLOW_FAILED_CLOSED}
)

CFA_CLARIFICATION = "CFA-CLARIFICATION-V1"
CFA_OBJECTIVE_COMMITMENT = "CFA-OBJECTIVE-COMMITMENT-V1"
CFA_SELF_KNOWLEDGE = "CFA-SELF-KNOWLEDGE-V1"
CFA_PLATFORM_KNOWLEDGE = "CFA-PLATFORM-KNOWLEDGE-V1"
CFA_DEVELOPMENT_GOVERNANCE = "CFA-DEVELOPMENT-GOVERNANCE-V1"
CFA_EXECUTION = "CFA-EXECUTION-V1"
CFA_FAILURE = "CFA-FAILURE-V1"

FLOW_OWNERS = {
    CFA_CLARIFICATION: "ORIGINATING_OWNER",
    CFA_OBJECTIVE_COMMITMENT: "CONVERSATION_LAYER_PLUS_HUMAN_AUTHORITY",
    CFA_SELF_KNOWLEDGE: "SELF_KNOWLEDGE_RUNTIME_FAMILY_UNDER_PLATFORM_CORE_COMPOSITION",
    CFA_PLATFORM_KNOWLEDGE: "PLATFORM_CORE_PLATFORM_KNOWLEDGE_OWNER",
    CFA_DEVELOPMENT_GOVERNANCE: "DEVELOPMENT_GOVERNANCE",
    CFA_EXECUTION: "EXECUTION_RUNTIME",
    CFA_FAILURE: "FAILING_DECISION_OWNER",
}
SUPPORTED_TARGET_FLOWS = frozenset(
    {
        CFA_SELF_KNOWLEDGE,
        CFA_PLATFORM_KNOWLEDGE,
        CFA_DEVELOPMENT_GOVERNANCE,
        CFA_EXECUTION,
        CFA_CLARIFICATION,
        CFA_FAILURE,
    }
)

PRODUCTION_CONVERSATION_DETERMINISTIC_PARSER_IDENTITY = (
    "production-conversation-source-turn-parser-v1"
)
PRODUCTION_CONVERSATION_DETERMINISTIC_PARSER_VERSION = "1.0.0"

_STOP_CONTROLS = frozenset({"/stop", "/cancel", "/exit", "stop", "cancel"})
_REPLY_PREFIXES = ("/reply ", "reply: ", "answer: ", "/clarify ")

_PRECEDENCE_FIELDS = frozenset(
    {
        "artifact_type",
        "schema_version",
        "decision_owner",
        "request_identity",
        "request_hash",
        "interface_identity",
        "session_identity",
        "workspace_identity_hash",
        "request_classification_identity",
        "request_classification_hash",
        "active_clarification_identity",
        "active_clarification_hash",
        "active_clarification_owner",
        "decision_disposition",
        "decision_reason_code",
        "permitted_next_action",
        "created_at",
        "human_authority_preserved",
        "provider_invoked",
        "platform_flow_selected",
        "objective_created",
        "authorization_created",
        "worker_invoked",
        "execution_invoked",
        "artifact_hash",
    }
)

_CLARIFICATION_FIELDS = frozenset(
    {
        "artifact_type",
        "schema_version",
        "clarification_identity",
        "originating_flow_id",
        "originating_owner",
        "originating_artifact_reference",
        "originating_artifact_hash",
        "workspace_identity_hash",
        "session_identity",
        "conversation_identity",
        "subject_identity",
        "expected_revision",
        "reason_code",
        "required_field_or_evidence_codes",
        "permitted_reply_kind",
        "attempt_identities",
        "status",
        "created_at",
        "expires_at",
        "clarification_authority_created",
        "human_interface_authority",
        "provider_invoked",
        "objective_created",
        "authorization_created",
        "worker_invoked",
        "execution_invoked",
        "artifact_hash",
    }
)

_FLOW_BINDING_FIELDS = frozenset(
    {
        "artifact_type",
        "schema_version",
        "flow_architecture_version",
        "request_identity",
        "request_hash",
        "workspace_identity_hash",
        "session_identity_hash",
        "conversation_identity",
        "cwm_revision",
        "cwm_state_hash",
        "source_turn_identity",
        "source_turn_digest",
        "request_classification_identity",
        "request_classification_hash",
        "proposal_identity",
        "proposal_hash",
        "interpreter_class",
        "proposal_validation_identity",
        "proposal_validation_hash",
        "proposal_validation_disposition",
        "semantic_commit_identity",
        "semantic_commit_hash",
        "route_sufficiency_status",
        "classification_owner",
        "classification_identity",
        "selection_owner",
        "requested_target_flow_id",
        "requested_target_owner",
        "permitted_next_flow_id",
        "permitted_next_owner",
        "selection_disposition",
        "clarification_identity",
        "ordered_predecessor_references",
        "owner_local_replay_references",
        "created_at",
        "objective_commitment_required",
        "platform_service_invoked_by_selection",
        "authority_owner_added",
        "authorization_created",
        "worker_invoked",
        "execution_invoked",
        "artifact_hash",
    }
)


def create_human_intent_precedence_decision_v1(
    *,
    request_text: str,
    interface_identity: str,
    session_identity: str,
    workspace_identity: str | Path,
    request_classification: dict[str, Any],
    active_clarification_envelope: dict[str, Any] | None,
    created_at: str,
) -> dict[str, Any]:
    """Bind the current Human turn before restored clarification can control it."""

    request = _text(request_text, "request_text")
    interface = _text(interface_identity, "interface_identity")
    session = _text(session_identity, "session_identity")
    timestamp = cwm_v2._canonical_timestamp(created_at, "created_at")
    classification = validate_self_knowledge_request_classification(
        request_classification
    )
    if classification["request_text"] != request:
        _fail("request classification does not bind the current Human turn")
    active = (
        deepcopy(active_clarification_envelope)
        if isinstance(active_clarification_envelope, dict)
        else None
    )
    normalized = " ".join(request.lower().split())
    if normalized in _STOP_CONTROLS:
        disposition = HUMAN_STOP
        reason = "EXACT_HUMAN_STOP_CONTROL"
        next_action = "STOP_WITHOUT_DOWNSTREAM_EFFECT"
    elif active is None:
        disposition = NEW_HUMAN_INTENT
        reason = "NO_ACTIVE_CLARIFICATION_STATE"
        next_action = "CREATE_OR_LOAD_CONVERSATION"
    elif classification["request_classification"] in {
        SELF_KNOWLEDGE_QUERY,
        SELF_KNOWLEDGE_CLARIFICATION_REQUIRED,
    }:
        disposition = NEW_HUMAN_INTENT
        reason = "EXACT_CURRENT_REQUEST_CLASSIFICATION_PRECEDENCE"
        next_action = "SUSPEND_ACTIVE_CLARIFICATION_AND_CLASSIFY_NEW_TURN"
    else:
        from aigol.runtime.platform_core_project_services import (
            clarification_explicitly_changes_query_intent,
        )
        from aigol.runtime.platform_project_objective_inference import (
            interpret_request_clause_roles,
        )

        if clarification_explicitly_changes_query_intent(request):
            disposition = NEW_HUMAN_INTENT
            reason = "EXPLICIT_NEW_INTENT_CONTROL"
            next_action = "SUSPEND_ACTIVE_CLARIFICATION_AND_CLASSIFY_NEW_TURN"
        elif normalized.startswith(_REPLY_PREFIXES):
            disposition = CLARIFICATION_REPLY
            reason = "EXPLICIT_CLARIFICATION_REPLY_CONTROL"
            next_action = "RETURN_TO_ORIGINATING_CLARIFICATION_OWNER"
        elif interpret_request_clause_roles(request)["requested_action_clauses"]:
            disposition = AMBIGUOUS_STATE_RELATIONSHIP
            reason = "ACTIONABLE_TURN_RELATIONSHIP_NOT_EXPLICIT"
            next_action = "ASK_NEW_INTENT_OR_CLARIFICATION_REPLY"
        else:
            disposition = CLARIFICATION_REPLY
            reason = "BOUNDED_NON_ACTION_REPLY_TO_ACTIVE_CLARIFICATION"
            next_action = "RETURN_TO_ORIGINATING_CLARIFICATION_OWNER"

    active_hash = active.get("artifact_hash") if active else None
    body = {
        "artifact_type": HUMAN_INTENT_PRECEDENCE_DECISION_V1,
        "schema_version": "V1",
        "decision_owner": "CONVERSATION_LAYER",
        "request_identity": "human-intent-request-sha256:"
        + replay_hash(
            {
                "session_identity": session,
                "request_hash": replay_hash(request),
                "active_clarification_hash": active_hash,
                "created_at": timestamp,
            }
        ).split(":", 1)[1],
        "request_hash": replay_hash(request),
        "interface_identity": interface,
        "session_identity": session,
        "workspace_identity_hash": replay_hash(str(Path(workspace_identity))),
        "request_classification_identity": classification["artifact_type"],
        "request_classification_hash": classification["artifact_hash"],
        "active_clarification_identity": (
            active.get("clarification_identity")
            or active.get("artifact_type")
            if active
            else None
        ),
        "active_clarification_hash": active_hash,
        "active_clarification_owner": (
            active.get("originating_owner")
            or active.get("clarification_owner")
            if active
            else None
        ),
        "decision_disposition": disposition,
        "decision_reason_code": reason,
        "permitted_next_action": next_action,
        "created_at": timestamp,
        "human_authority_preserved": True,
        "provider_invoked": False,
        "platform_flow_selected": False,
        "objective_created": False,
        "authorization_created": False,
        "worker_invoked": False,
        "execution_invoked": False,
    }
    body["artifact_hash"] = replay_hash(body)
    return validate_human_intent_precedence_decision_v1(
        body,
        expected_session_identity=session,
        expected_request_hash=replay_hash(request),
    )


def validate_human_intent_precedence_decision_v1(
    artifact: dict[str, Any],
    *,
    expected_session_identity: str | None = None,
    expected_request_hash: str | None = None,
) -> dict[str, Any]:
    candidate = _closed_hashed_artifact(
        artifact,
        _PRECEDENCE_FIELDS,
        HUMAN_INTENT_PRECEDENCE_DECISION_V1,
        "Human Intent precedence decision",
    )
    if candidate["schema_version"] != "V1":
        _fail("Human Intent precedence schema version is invalid")
    if candidate["decision_owner"] != "CONVERSATION_LAYER":
        _fail("Human Intent precedence owner substitution detected")
    _text(candidate["request_identity"], "request_identity")
    _digest(candidate["request_hash"], "request_hash")
    _text(candidate["interface_identity"], "interface_identity")
    _text(candidate["session_identity"], "session_identity")
    _digest(candidate["workspace_identity_hash"], "workspace_identity_hash")
    _text(
        candidate["request_classification_identity"],
        "request_classification_identity",
    )
    _digest(
        candidate["request_classification_hash"],
        "request_classification_hash",
    )
    _optional_text(
        candidate["active_clarification_identity"],
        "active_clarification_identity",
    )
    _optional_digest(
        candidate["active_clarification_hash"],
        "active_clarification_hash",
    )
    _optional_text(
        candidate["active_clarification_owner"],
        "active_clarification_owner",
    )
    active_values = (
        candidate["active_clarification_identity"],
        candidate["active_clarification_hash"],
        candidate["active_clarification_owner"],
    )
    if any(value is None for value in active_values) and any(
        value is not None for value in active_values
    ):
        _fail("Human Intent precedence active clarification binding is partial")
    if candidate["decision_disposition"] not in PRECEDENCE_DISPOSITIONS:
        _fail("Human Intent precedence disposition is invalid")
    _text(candidate["decision_reason_code"], "decision_reason_code")
    _text(candidate["permitted_next_action"], "permitted_next_action")
    cwm_v2._canonical_timestamp(candidate["created_at"], "created_at")
    if expected_session_identity is not None and candidate[
        "session_identity"
    ] != _text(expected_session_identity, "expected_session_identity"):
        _fail("Human Intent precedence cross-session binding detected")
    if expected_request_hash is not None and candidate["request_hash"] != (
        expected_request_hash
    ):
        _fail("Human Intent precedence request substitution detected")
    if candidate["human_authority_preserved"] is not True:
        _fail("Human Authority preservation is required")
    if candidate["platform_flow_selected"] is not False:
        _fail("Human Intent precedence selected a Platform flow")
    _require_false_boundary_flags(candidate)
    return candidate


def create_owner_bound_clarification_envelope_v1(
    *,
    originating_flow_id: str,
    originating_owner: str,
    originating_artifact_reference: str,
    originating_artifact_hash: str,
    workspace_identity_hash: str,
    session_identity: str,
    conversation_identity: str,
    subject_identity: str,
    expected_revision: int,
    reason_code: str,
    required_field_or_evidence_codes: list[str],
    permitted_reply_kind: str,
    created_at: str,
    expires_at: str,
) -> dict[str, Any]:
    """Create transport evidence without acquiring clarification authority."""

    body = {
        "artifact_type": OWNER_BOUND_CLARIFICATION_ENVELOPE_V1,
        "schema_version": "V1",
        "clarification_identity": "owner-bound-clarification-sha256:"
        + replay_hash(
            {
                "originating_flow_id": originating_flow_id,
                "originating_owner": originating_owner,
                "originating_artifact_hash": originating_artifact_hash,
                "session_identity": session_identity,
                "conversation_identity": conversation_identity,
                "expected_revision": expected_revision,
            }
        ).split(":", 1)[1],
        "originating_flow_id": _flow(originating_flow_id),
        "originating_owner": _text(originating_owner, "originating_owner"),
        "originating_artifact_reference": _text(
            originating_artifact_reference, "originating_artifact_reference"
        ),
        "originating_artifact_hash": _digest(
            originating_artifact_hash, "originating_artifact_hash"
        ),
        "workspace_identity_hash": _digest(
            workspace_identity_hash, "workspace_identity_hash"
        ),
        "session_identity": _text(session_identity, "session_identity"),
        "conversation_identity": _text(
            conversation_identity, "conversation_identity"
        ),
        "subject_identity": _text(subject_identity, "subject_identity"),
        "expected_revision": _revision(expected_revision),
        "reason_code": _text(reason_code, "reason_code"),
        "required_field_or_evidence_codes": _string_list(
            required_field_or_evidence_codes,
            "required_field_or_evidence_codes",
            allow_empty=False,
        ),
        "permitted_reply_kind": _text(
            permitted_reply_kind, "permitted_reply_kind"
        ),
        "attempt_identities": [],
        "status": "ACTIVE",
        "created_at": cwm_v2._canonical_timestamp(created_at, "created_at"),
        "expires_at": cwm_v2._canonical_timestamp(expires_at, "expires_at"),
        "clarification_authority_created": False,
        "human_interface_authority": False,
        "provider_invoked": False,
        "objective_created": False,
        "authorization_created": False,
        "worker_invoked": False,
        "execution_invoked": False,
    }
    body["artifact_hash"] = replay_hash(body)
    return validate_owner_bound_clarification_envelope_v1(
        body, expected_session_identity=session_identity
    )


def validate_owner_bound_clarification_envelope_v1(
    artifact: dict[str, Any],
    *,
    expected_session_identity: str | None = None,
    expected_originating_owner: str | None = None,
) -> dict[str, Any]:
    candidate = _closed_hashed_artifact(
        artifact,
        _CLARIFICATION_FIELDS,
        OWNER_BOUND_CLARIFICATION_ENVELOPE_V1,
        "owner-bound clarification envelope",
    )
    if candidate["schema_version"] != "V1" or candidate["status"] != "ACTIVE":
        _fail("owner-bound clarification state is invalid")
    _flow(candidate["originating_flow_id"])
    _text(candidate["clarification_identity"], "clarification_identity")
    _text(candidate["originating_owner"], "originating_owner")
    _text(
        candidate["originating_artifact_reference"],
        "originating_artifact_reference",
    )
    _digest(candidate["originating_artifact_hash"], "originating_artifact_hash")
    _digest(candidate["workspace_identity_hash"], "workspace_identity_hash")
    _text(candidate["session_identity"], "session_identity")
    _text(candidate["conversation_identity"], "conversation_identity")
    _text(candidate["subject_identity"], "subject_identity")
    _revision(candidate["expected_revision"])
    _text(candidate["reason_code"], "reason_code")
    _string_list(
        candidate["required_field_or_evidence_codes"],
        "required_field_or_evidence_codes",
        allow_empty=False,
    )
    _string_list(
        candidate["attempt_identities"], "attempt_identities", allow_empty=True
    )
    _text(candidate["permitted_reply_kind"], "permitted_reply_kind")
    if expected_session_identity is not None and candidate[
        "session_identity"
    ] != _text(expected_session_identity, "expected_session_identity"):
        _fail("owner-bound clarification cross-session binding detected")
    if expected_originating_owner is not None and candidate[
        "originating_owner"
    ] != _text(expected_originating_owner, "expected_originating_owner"):
        _fail("owner-bound clarification owner substitution detected")
    if cwm_v2._parse_timestamp(
        candidate["expires_at"], "expires_at"
    ) <= cwm_v2._parse_timestamp(candidate["created_at"], "created_at"):
        _fail("owner-bound clarification expiration is invalid")
    if candidate["clarification_authority_created"] is not False or candidate[
        "human_interface_authority"
    ] is not False:
        _fail("owner-bound clarification transport acquired authority")
    _require_false_boundary_flags(candidate)
    return candidate


def create_production_conversation_flow_binding_v1(
    *,
    request_identity: str,
    request_hash: str,
    state: dict[str, Any],
    source_turn_binding: dict[str, Any],
    request_classification: dict[str, Any],
    proposal: dict[str, Any],
    proposal_validation: dict[str, Any],
    proposal_commit: dict[str, Any] | None,
    route_sufficiency_status: str,
    classification_owner: str,
    selection_owner: str,
    requested_target_flow_id: str,
    permitted_next_flow_id: str,
    selection_disposition: str,
    clarification_envelope: dict[str, Any] | None,
    ordered_predecessor_references: list[dict[str, Any]],
    owner_local_replay_references: list[str],
    created_at: str,
) -> dict[str, Any]:
    target = _target_flow(requested_target_flow_id)
    successor = _flow(permitted_next_flow_id)
    validated_state = cwm_v2.validate_conversation_working_memory_state_v2(state)
    classification = validate_self_knowledge_request_classification(
        request_classification
    )
    clarification = (
        validate_owner_bound_clarification_envelope_v1(clarification_envelope)
        if isinstance(clarification_envelope, dict)
        else None
    )
    commit_identity = (
        proposal_commit.get("commit_identity")
        if isinstance(proposal_commit, dict)
        else None
    )
    commit_hash = replay_hash(proposal_commit) if proposal_commit else None
    validation_hash = replay_hash(proposal_validation)
    body = {
        "artifact_type": PRODUCTION_CONVERSATION_FLOW_BINDING_V1,
        "schema_version": "V1",
        "flow_architecture_version": "V1",
        "request_identity": _text(request_identity, "request_identity"),
        "request_hash": _digest(request_hash, "request_hash"),
        "workspace_identity_hash": validated_state["envelope"][
            "workspace_identity_hash"
        ],
        "session_identity_hash": validated_state["envelope"][
            "session_identity_hash"
        ],
        "conversation_identity": validated_state["envelope"][
            "conversation_identity"
        ],
        "cwm_revision": validated_state["revision"],
        "cwm_state_hash": replay_hash(validated_state),
        "source_turn_identity": _text(
            source_turn_binding.get("source_turn_identity"),
            "source_turn_identity",
        ),
        "source_turn_digest": _digest(
            source_turn_binding.get("source_turn_digest"),
            "source_turn_digest",
        ),
        "request_classification_identity": classification["artifact_type"],
        "request_classification_hash": classification["artifact_hash"],
        "proposal_identity": _text(proposal.get("proposal_id"), "proposal_id"),
        "proposal_hash": replay_hash(proposal),
        "interpreter_class": _text(
            proposal.get("interpreter_class"), "interpreter_class"
        ),
        "proposal_validation_identity": "proposal-validation-sha256:"
        + validation_hash.split(":", 1)[1],
        "proposal_validation_hash": validation_hash,
        "proposal_validation_disposition": _text(
            proposal_validation.get("validation_disposition"),
            "proposal_validation_disposition",
        ),
        "semantic_commit_identity": commit_identity,
        "semantic_commit_hash": commit_hash,
        "route_sufficiency_status": _text(
            route_sufficiency_status, "route_sufficiency_status"
        ),
        "classification_owner": _text(
            classification_owner, "classification_owner"
        ),
        "classification_identity": classification["artifact_hash"],
        "selection_owner": _text(selection_owner, "selection_owner"),
        "requested_target_flow_id": target,
        "requested_target_owner": FLOW_OWNERS[target],
        "permitted_next_flow_id": successor,
        "permitted_next_owner": FLOW_OWNERS[successor],
        "selection_disposition": _text(
            selection_disposition, "selection_disposition"
        ),
        "clarification_identity": (
            clarification["clarification_identity"] if clarification else None
        ),
        "ordered_predecessor_references": deepcopy(
            ordered_predecessor_references
        ),
        "owner_local_replay_references": _string_list(
            owner_local_replay_references,
            "owner_local_replay_references",
            allow_empty=False,
        ),
        "created_at": cwm_v2._canonical_timestamp(created_at, "created_at"),
        "objective_commitment_required": target
        in {CFA_DEVELOPMENT_GOVERNANCE, CFA_EXECUTION},
        "platform_service_invoked_by_selection": False,
        "authority_owner_added": False,
        "authorization_created": False,
        "worker_invoked": False,
        "execution_invoked": False,
    }
    body["artifact_hash"] = replay_hash(body)
    return validate_production_conversation_flow_binding_v1(body)


def validate_production_conversation_flow_binding_v1(
    artifact: dict[str, Any],
    *,
    expected_request_hash: str | None = None,
) -> dict[str, Any]:
    candidate = _closed_hashed_artifact(
        artifact,
        _FLOW_BINDING_FIELDS,
        PRODUCTION_CONVERSATION_FLOW_BINDING_V1,
        "production Conversation flow binding",
    )
    if candidate["schema_version"] != "V1" or candidate[
        "flow_architecture_version"
    ] != "V1":
        _fail("production Conversation flow binding version is invalid")
    _text(candidate["request_identity"], "request_identity")
    _digest(candidate["request_hash"], "request_hash")
    _digest(candidate["workspace_identity_hash"], "workspace_identity_hash")
    _digest(candidate["session_identity_hash"], "session_identity_hash")
    _text(candidate["conversation_identity"], "conversation_identity")
    _revision(candidate["cwm_revision"])
    _digest(candidate["cwm_state_hash"], "cwm_state_hash")
    _text(candidate["source_turn_identity"], "source_turn_identity")
    _digest(candidate["source_turn_digest"], "source_turn_digest")
    _text(
        candidate["request_classification_identity"],
        "request_classification_identity",
    )
    _digest(
        candidate["request_classification_hash"],
        "request_classification_hash",
    )
    _text(candidate["proposal_identity"], "proposal_identity")
    _digest(candidate["proposal_hash"], "proposal_hash")
    _text(candidate["interpreter_class"], "interpreter_class")
    _text(
        candidate["proposal_validation_identity"],
        "proposal_validation_identity",
    )
    _digest(
        candidate["proposal_validation_hash"],
        "proposal_validation_hash",
    )
    _optional_text(
        candidate["semantic_commit_identity"], "semantic_commit_identity"
    )
    _optional_digest(candidate["semantic_commit_hash"], "semantic_commit_hash")
    _text(candidate["route_sufficiency_status"], "route_sufficiency_status")
    if candidate["classification_owner"] not in {
        "SELF_KNOWLEDGE_REQUEST_CLASSIFICATION",
        "PLATFORM_QUERY_ROUTER",
    }:
        _fail("production Conversation classification owner is invalid")
    _digest(candidate["classification_identity"], "classification_identity")
    if candidate["selection_owner"] != PLATFORM_QUERY_ROUTER_VERSION:
        _fail("production Conversation selection owner substitution detected")
    _optional_text(candidate["clarification_identity"], "clarification_identity")
    cwm_v2._canonical_timestamp(candidate["created_at"], "created_at")
    target = _target_flow(candidate["requested_target_flow_id"])
    successor = _flow(candidate["permitted_next_flow_id"])
    if candidate["requested_target_owner"] != FLOW_OWNERS[target]:
        _fail("production Conversation target owner substitution detected")
    if candidate["permitted_next_owner"] != FLOW_OWNERS[successor]:
        _fail("production Conversation successor owner substitution detected")
    expected_successor = (
        CFA_OBJECTIVE_COMMITMENT
        if target in {CFA_DEVELOPMENT_GOVERNANCE, CFA_EXECUTION}
        else target
    )
    if successor != expected_successor:
        _fail("production Conversation target-to-successor transition forbidden")
    if candidate["selection_disposition"] not in FLOW_SELECTION_DISPOSITIONS:
        _fail("production Conversation selection disposition is invalid")
    if target == CFA_CLARIFICATION:
        if candidate["selection_disposition"] != FLOW_CLARIFICATION_REQUIRED or not (
            candidate["clarification_identity"]
        ):
            _fail("production Conversation clarification selection is incomplete")
    elif target == CFA_FAILURE:
        if candidate["selection_disposition"] != FLOW_FAILED_CLOSED:
            _fail("production Conversation failure disposition is invalid")
    elif candidate["selection_disposition"] != FLOW_SELECTED:
        _fail("production Conversation selected flow disposition is invalid")
    if expected_request_hash is not None and candidate["request_hash"] != (
        expected_request_hash
    ):
        _fail("production Conversation request substitution detected")
    if candidate["objective_commitment_required"] is not (
        target in {CFA_DEVELOPMENT_GOVERNANCE, CFA_EXECUTION}
    ):
        _fail("production Conversation Objective Commitment gate is invalid")
    predecessor_stages = [
        reference["stage"]
        for reference in candidate["ordered_predecessor_references"]
    ]
    if candidate["objective_commitment_required"] is True:
        if predecessor_stages.count("OBJECTIVE_READINESS") != 1 or (
            predecessor_stages.count("OWNER_BOUND_CLARIFICATION") != 1
        ):
            _fail("actionable flow lacks readiness clarification evidence")
        if candidate["clarification_identity"] is None:
            _fail("actionable flow lacks Objective readiness clarification")
    elif "OBJECTIVE_READINESS" in predecessor_stages:
        _fail("read-only flow contains actionable readiness evidence")
    if candidate["proposal_validation_disposition"] == proposal_v2.ADMISSIBLE:
        if not candidate["semantic_commit_identity"] or not candidate[
            "semantic_commit_hash"
        ]:
            _fail("admissible proposal is not bound to Proposal Commit")
    elif candidate["proposal_validation_disposition"] == (
        proposal_v2.CLARIFICATION_REQUIRED
    ):
        if candidate["semantic_commit_identity"] is not None:
            _fail("clarification proposal commit boundary is invalid")
        if target == CFA_CLARIFICATION and candidate[
            "clarification_identity"
        ] is None:
            _fail("clarification flow has no owner-bound envelope")
    else:
        _fail("production Conversation proposal disposition is invalid")
    _validate_predecessor_references(candidate["ordered_predecessor_references"])
    _string_list(
        candidate["owner_local_replay_references"],
        "owner_local_replay_references",
        allow_empty=False,
    )
    if any(
        candidate[field] is not False
        for field in (
            "platform_service_invoked_by_selection",
            "authority_owner_added",
            "authorization_created",
            "worker_invoked",
            "execution_invoked",
        )
    ):
        _fail("production Conversation binding acquired forbidden authority")
    return candidate


def compose_production_conversation_flow_binding_v1(
    *,
    interface_identity: str,
    session_identity: str,
    request_text: str,
    runtime_root: str | Path,
    workspace_identity: str | Path,
    created_at: str,
    prior_workspace_state: dict[str, Any] | None,
) -> dict[str, Any]:
    """Sequence existing owners before Project Services and persist evidence."""

    request = _text(request_text, "request_text")
    session = _text(session_identity, "session_identity")
    timestamp = cwm_v2._canonical_timestamp(created_at, "created_at")
    active = _active_clarification_envelope(prior_workspace_state)
    if isinstance(active, dict) and active.get("artifact_type") == (
        OWNER_BOUND_CLARIFICATION_ENVELOPE_V1
    ):
        return _restore_owner_bound_clarification_continuation(
            active_envelope=active,
            session_identity=session,
            runtime_root=runtime_root,
            workspace_identity=workspace_identity,
            observed_at=timestamp,
        )
    classification = validate_self_knowledge_request_classification(
        classify_self_knowledge_request(request)
    )
    precedence = create_human_intent_precedence_decision_v1(
        request_text=request,
        interface_identity=interface_identity,
        session_identity=session,
        workspace_identity=workspace_identity,
        request_classification=classification,
        active_clarification_envelope=active,
        created_at=timestamp,
    )
    conversation_session = session + ":production-conversation-v1"
    cwm_root = Path(runtime_root) / "production_conversation_cwm"
    state = cwm_v2.recover_conversation_working_memory_state_v2(
        runtime_root=cwm_root,
        workspace_identity=workspace_identity,
        session_identity=conversation_session,
        observed_at=timestamp,
    )
    if state is None:
        state = hir_v2.create_hir_conversation_session_v2(
            runtime_root=cwm_root,
            workspace_identity=workspace_identity,
            session_identity=conversation_session,
            human_identity="HUMAN_OPERATOR",
            created_at=timestamp,
            interface_identity=interface_identity,
        )["state"]
    source_turn = proposal_v2.create_source_turn_binding_v2(
        conversation_identity=state["envelope"]["conversation_identity"],
        session_identity_hash=state["envelope"]["session_identity_hash"],
        expected_cwm_revision=state["revision"],
        source_turn_text=request,
    )
    operation = _deterministic_source_turn_operation(
        state=state,
        source_turn=source_turn,
        source_turn_text=request,
        clarification_required=precedence["decision_disposition"]
        in {AMBIGUOUS_STATE_RELATIONSHIP, HUMAN_STOP},
    )
    proposal = proposal_v2.create_conversation_interpreter_proposal_v2(
        interpreter_identity=PRODUCTION_CONVERSATION_DETERMINISTIC_PARSER_IDENTITY,
        interpreter_class=proposal_v2.DETERMINISTIC_PARSER,
        interpreter_version=PRODUCTION_CONVERSATION_DETERMINISTIC_PARSER_VERSION,
        conversation_identity=state["envelope"]["conversation_identity"],
        workspace_identity_hash=state["envelope"]["workspace_identity_hash"],
        session_identity_hash=state["envelope"]["session_identity_hash"],
        source_turn_identity=source_turn["source_turn_identity"],
        source_turn_digest=source_turn["source_turn_digest"],
        expected_cwm_revision=state["revision"],
        expected_semantic_revision=state["semantic_revision"],
        proposed_semantic_operations=[operation],
    )
    validation = proposal_v2.validate_conversation_interpreter_proposal_v2(
        proposal,
        current_state=state,
        source_turn_text=request,
        observed_at=timestamp,
        interpreter_registry=[
            {
                "interpreter_identity": (
                    PRODUCTION_CONVERSATION_DETERMINISTIC_PARSER_IDENTITY
                ),
                "interpreter_class": proposal_v2.DETERMINISTIC_PARSER,
                "interpreter_version": (
                    PRODUCTION_CONVERSATION_DETERMINISTIC_PARSER_VERSION
                ),
                "enabled": True,
            }
        ],
    )
    commit = None
    persisted_state = state
    if validation["validation_disposition"] == proposal_v2.ADMISSIBLE:
        commit = commit_v2.commit_proposal_candidate_operations_v2(
            runtime_root=cwm_root,
            workspace_identity=workspace_identity,
            session_identity=conversation_session,
            candidate_operation_set=validation["candidate_operation_set"],
            expected_revision=state["revision"],
            committed_at=timestamp,
        )
        persisted_state = commit["state"]

    target, successor, selection_disposition, route_status, route_capture = (
        _select_flow(
            request=request,
            classification=classification,
            precedence=precedence,
            validation=validation,
            workspace_state=prior_workspace_state,
        )
    )
    objective_readiness = None
    if target in {CFA_DEVELOPMENT_GOVERNANCE, CFA_EXECUTION}:
        objective_readiness = readiness_v2.evaluate_objective_readiness_v2(
            persisted_state,
            expected_revision=persisted_state["revision"],
            expected_semantic_revision=persisted_state["semantic_revision"],
            observed_at=timestamp,
        )
        objective_readiness = readiness_v2.validate_objective_readiness_report_v2(
            objective_readiness
        )
        route_status = objective_readiness["readiness_disposition"]
    turn_root = _turn_root(
        runtime_root=runtime_root,
        session_identity=session,
        source_turn_identity=source_turn["source_turn_identity"],
    )
    precedence_path = turn_root / "000_human_intent_precedence.json"
    proposal_path = turn_root / "001_interpreter_proposal.json"
    validation_path = turn_root / "002_proposal_validation.json"
    write_json_immutable(precedence_path, precedence)
    write_json_immutable(proposal_path, proposal)
    write_json_immutable(validation_path, validation)
    predecessors = [
        _predecessor("HUMAN_INTENT_PRECEDENCE", precedence, precedence_path),
        _predecessor("INTERPRETER_PROPOSAL", proposal, proposal_path),
        _predecessor("PROPOSAL_VALIDATION", validation, validation_path),
    ]
    replay_references = [
        str(precedence_path),
        str(proposal_path),
        str(validation_path),
    ]
    clarification = None
    next_index = 3
    if commit is not None:
        commit_path = turn_root / "003_proposal_commit.json"
        write_json_immutable(commit_path, commit)
        predecessors.append(_predecessor("PROPOSAL_COMMIT", commit, commit_path))
        replay_references.append(str(commit_path))
        next_index = 4
    readiness_path = None
    if objective_readiness is not None:
        readiness_path = turn_root / f"{next_index:03d}_objective_readiness.json"
        write_json_immutable(readiness_path, objective_readiness)
        predecessors.append(
            _predecessor("OBJECTIVE_READINESS", objective_readiness, readiness_path)
        )
        replay_references.append(str(readiness_path))
        next_index += 1
    if target == CFA_CLARIFICATION:
        clarification = _clarification_for_turn(
            active_envelope=active,
            prior_workspace_state=prior_workspace_state,
            precedence=precedence,
            proposal=proposal,
            state=persisted_state,
            turn_root=turn_root,
            created_at=timestamp,
        )
        clarification_path = turn_root / f"{next_index:03d}_clarification.json"
        write_json_immutable(clarification_path, clarification)
        predecessors.append(
            _predecessor("OWNER_BOUND_CLARIFICATION", clarification, clarification_path)
        )
        replay_references.append(str(clarification_path))
        next_index += 1
    elif objective_readiness is not None and objective_readiness[
        "readiness_disposition"
    ] != readiness_v2.READY:
        clarification = _clarification_for_objective_readiness(
            readiness=objective_readiness,
            readiness_reference=str(readiness_path),
            precedence=precedence,
            state=persisted_state,
            created_at=timestamp,
        )
        clarification_path = turn_root / f"{next_index:03d}_clarification.json"
        write_json_immutable(clarification_path, clarification)
        predecessors.append(
            _predecessor(
                "OWNER_BOUND_CLARIFICATION", clarification, clarification_path
            )
        )
        replay_references.append(str(clarification_path))
        next_index += 1
    binding = create_production_conversation_flow_binding_v1(
        request_identity=precedence["request_identity"],
        request_hash=precedence["request_hash"],
        state=persisted_state,
        source_turn_binding=source_turn,
        request_classification=classification,
        proposal=proposal,
        proposal_validation=validation,
        proposal_commit=commit,
        route_sufficiency_status=route_status,
        classification_owner=(
            "SELF_KNOWLEDGE_REQUEST_CLASSIFICATION"
            if classification["request_classification"]
            != "DEVELOPMENT_OBJECTIVE"
            else "PLATFORM_QUERY_ROUTER"
        ),
        selection_owner=PLATFORM_QUERY_ROUTER_VERSION,
        requested_target_flow_id=target,
        permitted_next_flow_id=successor,
        selection_disposition=selection_disposition,
        clarification_envelope=clarification,
        ordered_predecessor_references=predecessors,
        owner_local_replay_references=replay_references,
        created_at=timestamp,
    )
    binding_path = turn_root / f"{next_index:03d}_flow_binding.json"
    write_json_immutable(binding_path, binding)
    return {
        "human_intent_precedence_decision": precedence,
        "request_classification": classification,
        "conversation_identity": persisted_state["envelope"][
            "conversation_identity"
        ],
        "conversation_state": persisted_state,
        "source_turn_binding": source_turn,
        "deterministic_proposal": proposal,
        "g61_proposal_assistance_disposition": (
            "NOT_REQUIRED_DETERMINISTIC_PROPOSAL_VALIDATED"
        ),
        "proposal_validation": validation,
        "proposal_commit": commit,
        "objective_readiness_report": objective_readiness,
        "platform_flow_selection": route_capture,
        "owner_bound_clarification_envelope": clarification,
        "production_conversation_flow_binding": binding,
        "production_conversation_flow_binding_reference": str(binding_path),
        "production_conversation_replay_reference": str(turn_root),
        "proposal_validation_precedes_commit": commit is None
        or replay_references.index(str(validation_path))
        < replay_references.index(str(commit_path)),
        "project_services_invoked": False,
        "new_constitutional_owner_created": False,
    }


def reconstruct_production_conversation_flow_binding_v1(
    replay_reference: str | Path,
) -> dict[str, Any]:
    root = Path(replay_reference)
    precedence = validate_human_intent_precedence_decision_v1(
        load_json(root / "000_human_intent_precedence.json")
    )
    binding_paths = sorted(root.glob("*_flow_binding.json"))
    if len(binding_paths) != 1:
        _fail("production Conversation flow binding Replay is incomplete")
    binding = validate_production_conversation_flow_binding_replay_predecessors_v1(
        load_json(binding_paths[0]),
        expected_request_hash=precedence["request_hash"],
    )
    return {
        "human_intent_precedence_decision": precedence,
        "production_conversation_flow_binding": binding,
        "reconstruction_verified": True,
        "replay_reference": str(root),
        "reconstruction_hash": replay_hash(
            {
                "precedence_hash": precedence["artifact_hash"],
                "flow_binding_hash": binding["artifact_hash"],
            }
        ),
    }


def validate_production_conversation_flow_binding_replay_predecessors_v1(
    artifact: dict[str, Any],
    *,
    expected_request_hash: str | None = None,
) -> dict[str, Any]:
    """Validate the binding and every immutable owner-local predecessor."""

    binding = validate_production_conversation_flow_binding_v1(
        artifact,
        expected_request_hash=expected_request_hash,
    )
    for reference in binding["ordered_predecessor_references"]:
        captured = load_json(Path(reference["replay_reference"]))
        if replay_hash(captured) != reference["artifact_hash"]:
            _fail("production Conversation predecessor Replay tampering detected")
    return binding


def _active_clarification_envelope(
    prior_workspace_state: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if not isinstance(prior_workspace_state, dict):
        return None
    from aigol.runtime.platform_core_project_services import (
        replay_backed_uhi_clarification_state,
    )

    state = replay_backed_uhi_clarification_state(prior_workspace_state)
    envelope = None
    if isinstance(state, dict):
        envelope = state.get("owner_bound_clarification_envelope")
        if not isinstance(envelope, dict):
            envelope = state.get("operational_clarification_envelope")
    return deepcopy(envelope) if isinstance(envelope, dict) else None


def _restore_owner_bound_clarification_continuation(
    *,
    active_envelope: dict[str, Any],
    session_identity: str,
    runtime_root: str | Path,
    workspace_identity: str | Path,
    observed_at: str,
) -> dict[str, Any]:
    """Reconnect existing workspace, CWM, owner, and flow evidence for D1."""

    envelope = validate_owner_bound_clarification_envelope_v1(
        active_envelope,
        expected_session_identity=session_identity,
    )
    if cwm_v2._parse_timestamp(
        envelope["expires_at"], "expires_at"
    ) <= cwm_v2._parse_timestamp(observed_at, "observed_at"):
        _fail("owner-bound clarification restoration is expired")

    prior_context, context_reference = _project_context_for_clarification(
        runtime_root=runtime_root,
        session_identity=session_identity,
        clarification_envelope=envelope,
    )
    binding = validate_production_conversation_flow_binding_replay_predecessors_v1(
        prior_context["production_conversation_flow_binding"]
    )
    precedence = validate_human_intent_precedence_decision_v1(
        prior_context["human_intent_precedence_decision"],
        expected_session_identity=session_identity,
        expected_request_hash=binding["request_hash"],
    )
    if precedence["request_classification_hash"] != binding[
        "request_classification_hash"
    ]:
        _fail("restored clarification Human Intent lineage is inconsistent")
    if envelope["conversation_identity"] != binding["conversation_identity"]:
        _fail("restored clarification Conversation identity substitution detected")
    if envelope["expected_revision"] != binding["cwm_revision"]:
        _fail("restored clarification CWM revision substitution detected")

    conversation_session = session_identity + ":production-conversation-v1"
    cwm_root = Path(runtime_root) / "production_conversation_cwm"
    state = cwm_v2.recover_conversation_working_memory_state_v2(
        runtime_root=cwm_root,
        workspace_identity=workspace_identity,
        session_identity=conversation_session,
        observed_at=observed_at,
    )
    if state is None:
        _fail("restored clarification Conversation Working Memory is absent")
    state = cwm_v2.validate_conversation_working_memory_state_v2(state)
    if state["envelope"]["conversation_identity"] != binding[
        "conversation_identity"
    ]:
        _fail("restored clarification Conversation identity is inconsistent")
    if state["revision"] != binding["cwm_revision"]:
        _fail("restored clarification Conversation revision is stale")
    if replay_hash(state) != binding["cwm_state_hash"]:
        _fail("restored clarification Conversation Working Memory was mutated")

    predecessor_artifacts = {
        reference["stage"]: load_json(Path(reference["replay_reference"]))
        for reference in binding["ordered_predecessor_references"]
    }
    binding_reference = _flow_binding_reference(binding)
    validation_reference = next(
        reference["replay_reference"]
        for reference in binding["ordered_predecessor_references"]
        if reference["stage"] == "PROPOSAL_VALIDATION"
    )
    commit_reference = next(
        (
            reference["replay_reference"]
            for reference in binding["ordered_predecessor_references"]
            if reference["stage"] == "PROPOSAL_COMMIT"
        ),
        None,
    )
    replay_root = str(Path(binding_reference).parent)
    return {
        "human_intent_precedence_decision": precedence,
        "request_classification": None,
        "conversation_identity": state["envelope"]["conversation_identity"],
        "conversation_state": state,
        "source_turn_binding": None,
        "deterministic_proposal": predecessor_artifacts.get(
            "INTERPRETER_PROPOSAL"
        ),
        "g61_proposal_assistance_disposition": (
            "NOT_REINVOKED_EXISTING_CLARIFICATION_CONTINUATION"
        ),
        "proposal_validation": predecessor_artifacts.get("PROPOSAL_VALIDATION"),
        "proposal_commit": predecessor_artifacts.get("PROPOSAL_COMMIT"),
        "objective_readiness_report": predecessor_artifacts.get(
            "OBJECTIVE_READINESS"
        ),
        "platform_flow_selection": {
            "selection_owner": binding["selection_owner"],
            "selection_only": True,
            "route_status": binding["route_sufficiency_status"],
            "service_invoked": False,
            "selection_reused": True,
        },
        "owner_bound_clarification_envelope": envelope,
        "production_conversation_flow_binding": binding,
        "production_conversation_flow_binding_reference": binding_reference,
        "production_conversation_replay_reference": replay_root,
        "proposal_validation_precedes_commit": commit_reference is None
        or binding["owner_local_replay_references"].index(validation_reference)
        < binding["owner_local_replay_references"].index(commit_reference),
        "clarification_continuation_restored": True,
        "clarification_continuation_context_reference": context_reference,
        "originating_owner_restored": envelope["originating_owner"],
        "conversation_working_memory_reused": True,
        "production_flow_binding_reused": True,
        "human_intent_reclassified": False,
        "platform_query_router_reinvoked": False,
        "project_services_invoked": False,
        "new_constitutional_owner_created": False,
    }


def _project_context_for_clarification(
    *,
    runtime_root: str | Path,
    session_identity: str,
    clarification_envelope: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    context_root = Path(runtime_root) / session_identity / "uhi_project_services"
    matches: list[tuple[dict[str, Any], str]] = []
    for path in sorted(context_root.glob("*_uhi_project_context_recorded.json")):
        candidate = load_json(path)
        stored_hash = candidate.get("artifact_hash")
        body = dict(candidate)
        body.pop("artifact_hash", None)
        if stored_hash != replay_hash(body):
            _fail("restored Project Services clarification Replay was tampered")
        envelope = candidate.get("owner_bound_clarification_envelope")
        if not isinstance(envelope, dict) or envelope.get("artifact_hash") != (
            clarification_envelope["artifact_hash"]
        ):
            continue
        if candidate.get("session_id") != session_identity:
            _fail("restored clarification Project Services session mismatch")
        validated = validate_owner_bound_clarification_envelope_v1(
            envelope,
            expected_session_identity=session_identity,
            expected_originating_owner=clarification_envelope[
                "originating_owner"
            ],
        )
        if validated != clarification_envelope:
            _fail("restored clarification owner-bound envelope substitution detected")
        matches.append((candidate, str(path)))
    if not matches:
        _fail("owner-bound clarification has no existing Project Services Replay")
    return matches[-1]


def _flow_binding_reference(binding: dict[str, Any]) -> str:
    replay_roots = {
        Path(reference).parent
        for reference in binding["owner_local_replay_references"]
    }
    for replay_root in sorted(replay_roots):
        for path in sorted(replay_root.glob("*_flow_binding.json")):
            candidate = load_json(path)
            if candidate.get("artifact_hash") == binding["artifact_hash"]:
                return str(path)
    _fail("restored production Conversation flow binding reference is absent")


def _deterministic_source_turn_operation(
    *,
    state: dict[str, Any],
    source_turn: dict[str, Any],
    source_turn_text: str,
    clarification_required: bool,
) -> dict[str, Any]:
    if clarification_required:
        return proposal_v2.create_proposed_semantic_operation_v2(
            conversation_identity=state["envelope"]["conversation_identity"],
            operation_type=proposal_v2.PROPOSE_CLARIFICATION_REQUIREMENT,
            slot_class=cwm_v2.SEMANTIC_REFERENCE,
            slot_role=cwm_v2.SCOPE,
            cardinality_key=source_turn["source_turn_identity"],
            surface_value=None,
            canonical_value=None,
            source_spans=[],
            clarification_reason="UNCONFIRMED",
        )
    return proposal_v2.create_proposed_semantic_operation_v2(
        conversation_identity=state["envelope"]["conversation_identity"],
        operation_type=proposal_v2.PROPOSE_SLOT_CREATION,
        slot_class=cwm_v2.SEMANTIC_REFERENCE,
        slot_role=cwm_v2.SCOPE,
        cardinality_key=source_turn["source_turn_identity"],
        surface_value=source_turn_text,
        canonical_value=source_turn_text,
        source_spans=[
            proposal_v2.create_source_span_v2(
                source_turn_text,
                start_offset=0,
                end_offset=len(source_turn_text),
            )
        ],
    )


def _select_flow(
    *,
    request: str,
    classification: dict[str, Any],
    precedence: dict[str, Any],
    validation: dict[str, Any],
    workspace_state: dict[str, Any] | None,
) -> tuple[str, str, str, str, dict[str, Any]]:
    disposition = precedence["decision_disposition"]
    if disposition == HUMAN_STOP:
        capture = {
            "selection_owner": PLATFORM_QUERY_ROUTER_VERSION,
            "selection_only": True,
            "route_status": "HUMAN_STOP",
            "service_invoked": False,
        }
        return CFA_FAILURE, CFA_FAILURE, FLOW_FAILED_CLOSED, "HUMAN_STOP", capture
    if disposition in {CLARIFICATION_REPLY, AMBIGUOUS_STATE_RELATIONSHIP} or (
        validation["validation_disposition"] == proposal_v2.CLARIFICATION_REQUIRED
    ):
        capture = {
            "selection_owner": PLATFORM_QUERY_ROUTER_VERSION,
            "selection_only": True,
            "route_status": ROUTE_CLARIFICATION_REQUIRED,
            "service_invoked": False,
        }
        return (
            CFA_CLARIFICATION,
            CFA_CLARIFICATION,
            FLOW_CLARIFICATION_REQUIRED,
            ROUTE_CLARIFICATION_REQUIRED,
            capture,
        )
    capture = select_platform_query_route(
        query=request,
        workspace_state=workspace_state,
        request_classification=classification,
    )
    if capture["route_status"] in {
        ROUTE_CLARIFICATION_REQUIRED,
        REQUIRED_EVIDENCE_MISSING,
    }:
        return (
            CFA_CLARIFICATION,
            CFA_CLARIFICATION,
            FLOW_CLARIFICATION_REQUIRED,
            capture["route_status"],
            capture,
        )
    if classification["request_classification"] == SELF_KNOWLEDGE_QUERY:
        return (
            CFA_SELF_KNOWLEDGE,
            CFA_SELF_KNOWLEDGE,
            FLOW_SELECTED,
            capture["route_status"],
            capture,
        )
    execution = detect_human_execution_intent(request)
    if execution["intent_class"] == GENERIC_GOVERNED_EXECUTION_REQUEST:
        return (
            CFA_EXECUTION,
            CFA_OBJECTIVE_COMMITMENT,
            FLOW_SELECTED,
            capture["route_status"],
            capture,
        )
    if capture["selected_service"] in {
        PLATFORM_KNOWLEDGE_ROUTE,
        SELF_KNOWLEDGE_ROUTE,
    }:
        return (
            CFA_PLATFORM_KNOWLEDGE,
            CFA_PLATFORM_KNOWLEDGE,
            FLOW_SELECTED,
            capture["route_status"],
            capture,
        )
    return (
        CFA_DEVELOPMENT_GOVERNANCE,
        CFA_OBJECTIVE_COMMITMENT,
        FLOW_SELECTED,
        capture["route_status"],
        capture,
    )


def _clarification_for_turn(
    *,
    active_envelope: dict[str, Any] | None,
    prior_workspace_state: dict[str, Any] | None,
    precedence: dict[str, Any],
    proposal: dict[str, Any],
    state: dict[str, Any],
    turn_root: Path,
    created_at: str,
) -> dict[str, Any]:
    if active_envelope is not None:
        owner = _text(
            active_envelope.get("clarification_owner"), "clarification_owner"
        )
        origin_hash = _digest(
            active_envelope.get("artifact_hash"), "active clarification hash"
        )
        origin_reference = str(
            prior_workspace_state.get("replay_reference")
            if isinstance(prior_workspace_state, dict)
            else turn_root
        )
        subject = _text(
            active_envelope.get("semantic_slot") or "active_clarification",
            "clarification subject",
        )
        reason = (
            "ACTIVE_OWNER_CLARIFICATION_REPLY"
            if precedence["decision_disposition"] == CLARIFICATION_REPLY
            else "AMBIGUOUS_STATE_RELATIONSHIP"
        )
    else:
        owner = "CONVERSATION_LAYER"
        origin_hash = replay_hash(proposal)
        origin_reference = str(turn_root / "001_interpreter_proposal.json")
        subject = "human_intent_state_relationship"
        reason = "PROPOSAL_REQUIRES_CLARIFICATION"
    return create_owner_bound_clarification_envelope_v1(
        originating_flow_id=CFA_CLARIFICATION,
        originating_owner=owner,
        originating_artifact_reference=origin_reference,
        originating_artifact_hash=origin_hash,
        workspace_identity_hash=state["envelope"]["workspace_identity_hash"],
        session_identity=precedence["session_identity"],
        conversation_identity=state["envelope"]["conversation_identity"],
        subject_identity=subject,
        expected_revision=state["revision"],
        reason_code=reason,
        required_field_or_evidence_codes=[
            "NEW_HUMAN_INTENT_OR_CLARIFICATION_REPLY"
            if reason == "AMBIGUOUS_STATE_RELATIONSHIP"
            else subject
        ],
        permitted_reply_kind="OWNER_BOUND_REPLY",
        created_at=created_at,
        expires_at=state["envelope"]["expires_at"],
    )


def _clarification_for_objective_readiness(
    *,
    readiness: dict[str, Any],
    readiness_reference: str,
    precedence: dict[str, Any],
    state: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    required = sorted(
        {
            str(assessment["slot_class"])
            for assessment in readiness["required_slot_assessments"]
            if assessment["present"] is not True
            or assessment["active_complete"] is not True
        }
    )
    return create_owner_bound_clarification_envelope_v1(
        originating_flow_id=CFA_OBJECTIVE_COMMITMENT,
        originating_owner="CONVERSATION_LAYER_PLUS_HUMAN_AUTHORITY",
        originating_artifact_reference=readiness_reference,
        originating_artifact_hash=readiness["report_checksum"],
        workspace_identity_hash=state["envelope"]["workspace_identity_hash"],
        session_identity=precedence["session_identity"],
        conversation_identity=state["envelope"]["conversation_identity"],
        subject_identity="objective_readiness",
        expected_revision=state["revision"],
        reason_code="OBJECTIVE_READINESS_REQUIRED",
        required_field_or_evidence_codes=required or ["OBJECTIVE_READINESS"],
        permitted_reply_kind="CONVERSATION_SEMANTIC_INPUT_OR_EXACT_COMMIT_ACT",
        created_at=created_at,
        expires_at=state["envelope"]["expires_at"],
    )


def _turn_root(
    *,
    runtime_root: str | Path,
    session_identity: str,
    source_turn_identity: str,
) -> Path:
    return (
        Path(runtime_root)
        / "production_conversation_flow_binding"
        / replay_hash(session_identity).split(":", 1)[1][:24]
        / source_turn_identity.split(":", 1)[-1][:32]
    )


def _predecessor(stage: str, artifact: dict[str, Any], path: Path) -> dict[str, Any]:
    return {
        "stage": stage,
        "artifact_hash": replay_hash(artifact),
        "replay_reference": str(path),
    }


def _validate_predecessor_references(value: Any) -> None:
    if not isinstance(value, list) or len(value) < 3:
        _fail("production Conversation predecessor references are incomplete")
    stages: list[str] = []
    for reference in value:
        if not isinstance(reference, dict) or set(reference) != {
            "stage",
            "artifact_hash",
            "replay_reference",
        }:
            _fail("production Conversation predecessor reference is invalid")
        stages.append(_text(reference["stage"], "predecessor stage"))
        _digest(reference["artifact_hash"], "predecessor artifact_hash")
        _text(reference["replay_reference"], "predecessor replay_reference")
    required = [
        "HUMAN_INTENT_PRECEDENCE",
        "INTERPRETER_PROPOSAL",
        "PROPOSAL_VALIDATION",
    ]
    if stages[:3] != required:
        _fail("production Conversation predecessor order is invalid")
    if "PROPOSAL_COMMIT" in stages and stages.index("PROPOSAL_COMMIT") <= (
        stages.index("PROPOSAL_VALIDATION")
    ):
        _fail("Proposal Commit precedes Proposal Validation")
    if "OBJECTIVE_READINESS" in stages:
        if "PROPOSAL_COMMIT" not in stages or stages.index(
            "OBJECTIVE_READINESS"
        ) <= stages.index("PROPOSAL_COMMIT"):
            _fail("Objective Readiness precedes semantic Proposal Commit")
    if "OWNER_BOUND_CLARIFICATION" in stages and "OBJECTIVE_READINESS" in stages:
        if stages.index("OWNER_BOUND_CLARIFICATION") <= stages.index(
            "OBJECTIVE_READINESS"
        ):
            _fail("Objective clarification precedes readiness evidence")


def _closed_hashed_artifact(
    artifact: Any,
    fields: frozenset[str],
    artifact_type: str,
    label: str,
) -> dict[str, Any]:
    if not isinstance(artifact, dict) or set(artifact) != fields:
        _fail(f"{label} schema is invalid")
    candidate = deepcopy(artifact)
    if candidate.get("artifact_type") != artifact_type:
        _fail(f"{label} type is invalid")
    supplied_hash = candidate.pop("artifact_hash", None)
    if not isinstance(supplied_hash, str) or supplied_hash != replay_hash(candidate):
        _fail(f"{label} hash mismatch")
    candidate["artifact_hash"] = supplied_hash
    return candidate


def _require_false_boundary_flags(candidate: dict[str, Any]) -> None:
    for field in (
        "provider_invoked",
        "objective_created",
        "authorization_created",
        "worker_invoked",
        "execution_invoked",
    ):
        if candidate[field] is not False:
            _fail(f"forbidden boundary flag set: {field}")


def _target_flow(value: Any) -> str:
    flow = _flow(value)
    if flow not in SUPPORTED_TARGET_FLOWS:
        _fail("unsupported production Conversation target flow")
    return flow


def _flow(value: Any) -> str:
    flow = _text(value, "flow_id")
    if flow not in FLOW_OWNERS:
        _fail("unknown constitutional flow identifier")
    return flow


def _digest(value: Any, field_name: str) -> str:
    digest = _text(value, field_name)
    if not digest.startswith("sha256:") or len(digest) != 71:
        _fail(f"{field_name} is not a sha256 digest")
    return digest


def _optional_digest(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    return _digest(value, field_name)


def _revision(value: Any) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        _fail("revision is invalid")
    return value


def _string_list(value: Any, field_name: str, *, allow_empty: bool) -> list[str]:
    if not isinstance(value, list) or (not allow_empty and not value):
        _fail(f"{field_name} is invalid")
    items = [_text(item, field_name) for item in value]
    if items != sorted(set(items)):
        _fail(f"{field_name} must be unique and sorted")
    return items


def _text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _fail(f"{field_name} is required")
    return value.strip()


def _optional_text(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    return _text(value, field_name)


def _fail(message: str) -> None:
    raise FailClosedRuntimeError(message)


__all__ = [
    "AMBIGUOUS_STATE_RELATIONSHIP",
    "CFA_CLARIFICATION",
    "CFA_DEVELOPMENT_GOVERNANCE",
    "CFA_EXECUTION",
    "CFA_OBJECTIVE_COMMITMENT",
    "CFA_PLATFORM_KNOWLEDGE",
    "CFA_SELF_KNOWLEDGE",
    "CLARIFICATION_REPLY",
    "HUMAN_INTENT_PRECEDENCE_DECISION_V1",
    "HUMAN_STOP",
    "NEW_HUMAN_INTENT",
    "OWNER_BOUND_CLARIFICATION_ENVELOPE_V1",
    "PRODUCTION_CONVERSATION_FLOW_BINDING_V1",
    "compose_production_conversation_flow_binding_v1",
    "create_human_intent_precedence_decision_v1",
    "create_owner_bound_clarification_envelope_v1",
    "create_production_conversation_flow_binding_v1",
    "reconstruct_production_conversation_flow_binding_v1",
    "validate_human_intent_precedence_decision_v1",
    "validate_owner_bound_clarification_envelope_v1",
    "validate_production_conversation_flow_binding_v1",
    "validate_production_conversation_flow_binding_replay_predecessors_v1",
]
