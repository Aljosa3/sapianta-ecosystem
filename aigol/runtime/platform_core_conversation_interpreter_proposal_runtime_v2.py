"""Pure, non-authoritative Conversation Interpreter proposal boundary.

Interpreters submit bounded data.  This module validates, compares, and
reduces that data only into non-authoritative candidate operations.  It never
mutates Conversation Working Memory, advances the Conversation State Machine,
creates an Objective, or invokes any execution-pipeline owner or provider.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime import platform_core_conversation_working_memory_runtime_v2 as cwm_v2


PLATFORM_CORE_CONVERSATION_INTERPRETER_PROPOSAL_RUNTIME_V2 = (
    "PLATFORM_CORE_CONVERSATION_INTERPRETER_PROPOSAL_RUNTIME_V2"
)
PLATFORM_CORE_CONVERSATION_INTERPRETER_PROPOSAL_SCHEMA_V1 = (
    "PLATFORM_CORE_CONVERSATION_INTERPRETER_PROPOSAL_SCHEMA_V1"
)
PLATFORM_CORE_PROPOSED_SEMANTIC_OPERATION_SCHEMA_V1 = (
    "PLATFORM_CORE_PROPOSED_SEMANTIC_OPERATION_SCHEMA_V1"
)
PLATFORM_CORE_VALIDATED_CANDIDATE_OPERATION_SET_SCHEMA_V1 = (
    "PLATFORM_CORE_VALIDATED_CANDIDATE_OPERATION_SET_SCHEMA_V1"
)
PLATFORM_CORE_INTERPRETER_COMPARISON_SCHEMA_V1 = (
    "PLATFORM_CORE_INTERPRETER_COMPARISON_SCHEMA_V1"
)

DETERMINISTIC_PARSER = "DETERMINISTIC_PARSER"
EXTERNAL_LANGUAGE_MODEL = "EXTERNAL_LANGUAGE_MODEL"
RULE_BASED_INTERPRETER = "RULE_BASED_INTERPRETER"
OTHER_CERTIFIED_INTERPRETER = "OTHER_CERTIFIED_INTERPRETER"
INTERPRETER_CLASSES = frozenset(
    {
        DETERMINISTIC_PARSER,
        EXTERNAL_LANGUAGE_MODEL,
        RULE_BASED_INTERPRETER,
        OTHER_CERTIFIED_INTERPRETER,
    }
)

PROPOSE_SLOT_CREATION = "PROPOSE_SLOT_CREATION"
PROPOSE_SLOT_REVISION = "PROPOSE_SLOT_REVISION"
PROPOSE_SEMANTIC_EQUIVALENCE = "PROPOSE_SEMANTIC_EQUIVALENCE"
PROPOSE_CONFLICT = "PROPOSE_CONFLICT"
PROPOSE_CLARIFICATION_REQUIREMENT = "PROPOSE_CLARIFICATION_REQUIREMENT"
PROPOSE_REFERENCE_ATTACHMENT = "PROPOSE_REFERENCE_ATTACHMENT"
PROPOSED_OPERATION_TYPES = frozenset(
    {
        PROPOSE_SLOT_CREATION,
        PROPOSE_SLOT_REVISION,
        PROPOSE_SEMANTIC_EQUIVALENCE,
        PROPOSE_CONFLICT,
        PROPOSE_CLARIFICATION_REQUIREMENT,
        PROPOSE_REFERENCE_ATTACHMENT,
    }
)

ADMISSIBLE = "ADMISSIBLE"
CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"
REJECTED = "REJECTED"
CONSENSUS_NON_AUTHORITATIVE = "CONSENSUS_NON_AUTHORITATIVE"
COMPATIBLE_UNION_NON_AUTHORITATIVE = "COMPATIBLE_UNION_NON_AUTHORITATIVE"
MATERIAL_CONFLICT = "MATERIAL_CONFLICT"

MAX_PROPOSAL_BYTES = 65_536
MAX_SOURCE_TURN_CHARACTERS = 16_384
MAX_PROPOSED_OPERATIONS = 32
MAX_SOURCE_SPANS = 8
MAX_EVIDENCE_REFERENCES = 32
MAX_DECLARATION_OPERATION_IDS = 32
MAX_INTERPRETER_REGISTRY_ENTRIES = 32
MAX_COMPARISON_INPUTS = 16
MAX_TOKEN_CHARACTERS = 256

_PROPOSAL_FIELDS = frozenset(
    {
        "proposal_type",
        "proposal_version",
        "proposal_id",
        "interpreter_identity",
        "interpreter_class",
        "interpreter_version",
        "conversation_identity",
        "workspace_identity_hash",
        "session_identity_hash",
        "source_turn_identity",
        "source_turn_digest",
        "expected_cwm_revision",
        "expected_semantic_revision",
        "proposed_semantic_operations",
        "evidence_references",
        "advisory_confidence",
        "ambiguity_declaration",
        "conflict_declaration",
        "boundary_flags",
        "integrity_checksum",
    }
)

_OPERATION_FIELDS = frozenset(
    {
        "operation_type",
        "operation_id",
        "slot_class",
        "slot_role",
        "cardinality_key",
        "proposed_slot_id",
        "target_slot_id",
        "surface_value",
        "canonical_value",
        "proposed_equivalence_key",
        "source_spans",
        "depends_on_slot_ids",
        "evidence_reference_ids",
        "clarification_reason",
    }
)

_SOURCE_SPAN_FIELDS = frozenset(
    {"start_offset", "end_offset", "exact_surface_value", "surface_digest"}
)
_EVIDENCE_REFERENCE_FIELDS = frozenset(
    {"reference_id", "reference_kind", "reference_digest", "verification_status"}
)
_CONFIDENCE_FIELDS = frozenset(
    {"scale_id", "reported_value", "limitations", "authority_effect"}
)
_DECLARATION_FIELDS = frozenset({"declared", "operation_ids"})
_REGISTRY_ENTRY_FIELDS = frozenset(
    {"interpreter_identity", "interpreter_class", "interpreter_version", "enabled"}
)

_BOUNDARY_FLAGS = {
    "constitutional_artifact": False,
    "constitutional_authority": False,
    "semantic_cwm_mutation_authority": False,
    "conversation_state_transition_authority": False,
    "human_confirmation_authority": False,
    "objective_commitment_authority": False,
    "objective_creation_supported": False,
    "capability_routing_supported": False,
    "platform_core_invocation_supported": False,
    "replay_visible": False,
    "replay_mutation_supported": False,
    "development_governance_supported": False,
    "authorization_eligible": False,
    "worker_eligible": False,
    "tool_execution_supported": False,
}

_FORBIDDEN_AUTHORITY_KEYS = frozenset(
    {
        "semantic_cwm_mutation",
        "semantic_cwm_state",
        "conversation_state_transition",
        "confirm_candidate",
        "human_confirmation",
        "objective",
        "objective_id",
        "objective_commitment",
        "objective_commitment_request",
        "platform_core",
        "platform_core_request",
        "development_governance",
        "capability_selection",
        "capability_id",
        "authorization",
        "authorization_id",
        "worker",
        "worker_request",
        "worker_request_id",
        "replay",
        "replay_id",
        "replay_identity",
        "execution",
        "execution_authority",
        "execution_payload",
        "execution_request",
        "execute",
        "cwm_mutation",
        "tool_call",
        "tool_calls",
        "shell_command",
        "approval_decision",
    }
)

_FORBIDDEN_CONTROL_OPERATIONS = frozenset(
    {
        "CONFIRM",
        "CONFIRMED",
        "CONFIRM_CANDIDATE",
        "HUMAN_CONFIRMATION",
        "COMMIT",
        "COMMIT_EXACT_CANDIDATE",
        "OBJECTIVE_COMMITMENT",
        "CREATE_OBJECTIVE",
        "EXECUTE",
        "INVOKE_PLATFORM_CORE",
    }
)

_CANDIDATE_SET_FIELDS = frozenset(
    {
        "candidate_operation_set_type",
        "candidate_operation_set_id",
        "proposal_id",
        "interpreter_identity",
        "interpreter_class",
        "conversation_identity",
        "workspace_identity_hash",
        "session_identity_hash",
        "source_turn_identity",
        "source_turn_digest",
        "expected_cwm_revision",
        "expected_semantic_revision",
        "candidate_operations",
        "semantic_reduction_digest",
        "ambiguity_operation_ids",
        "conflict_operation_ids",
        "validation_disposition",
        "clarification_required",
        "reduction_allowed",
        "confidence_authority_effect",
        "majority_authority_effect",
        "semantic_cwm_mutated",
        "conversation_transition_applied",
        "objective_created",
        "execution_invoked",
        "integrity_checksum",
    }
)

_CANDIDATE_OPERATION_FIELDS = frozenset(
    {
        "candidate_operation_type",
        "operation_id",
        "slot_class",
        "slot_role",
        "cardinality_key",
        "proposed_slot_id",
        "target_slot_id",
        "surface_value",
        "canonical_value",
        "validator_derived_equivalence_key",
        "source_spans",
        "depends_on_slot_ids",
        "evidence_reference_ids",
        "clarification_reason",
        "advisory_confidence",
        "authority_effect",
    }
)

_CANDIDATE_OPERATION_TYPE = {
    PROPOSE_SLOT_CREATION: "CREATE_CANDIDATE",
    PROPOSE_SLOT_REVISION: "REVISE_CANDIDATE",
    PROPOSE_SEMANTIC_EQUIVALENCE: "EQUIVALENCE_CANDIDATE",
    PROPOSE_CONFLICT: "CONFLICT_CANDIDATE",
    PROPOSE_CLARIFICATION_REQUIREMENT: "CLARIFICATION_CANDIDATE",
    PROPOSE_REFERENCE_ATTACHMENT: "REFERENCE_ATTACHMENT_CANDIDATE",
}


class ProposalValidationError(FailClosedRuntimeError):
    """Fail-closed proposal error with one stable rejection reason."""

    def __init__(self, reason_code: str, message: str) -> None:
        super().__init__(message)
        self.reason_code = reason_code


def create_source_turn_binding_v2(
    *,
    conversation_identity: str,
    session_identity_hash: str,
    expected_cwm_revision: int,
    source_turn_text: str,
) -> dict[str, str]:
    """Create one local identity/digest binding for the exact current turn."""

    text = _bounded_text(source_turn_text, "source turn", MAX_SOURCE_TURN_CHARACTERS)
    digest = _checksum(text)
    body = {
        "conversation_identity": _token(conversation_identity, "conversation identity"),
        "session_identity_hash": _digest(
            session_identity_hash, "session identity hash", "sha256:"
        ),
        "expected_cwm_revision": _nonnegative_integer(
            expected_cwm_revision, "expected CWM revision"
        ),
        "source_turn_digest": digest,
    }
    identity = "conversation-turn-local-sha256:" + hashlib.sha256(
        _canonical_bytes(body)
    ).hexdigest()
    return {"source_turn_identity": identity, "source_turn_digest": digest}


def create_source_span_v2(
    source_turn_text: str,
    *,
    start_offset: int,
    end_offset: int,
) -> dict[str, Any]:
    """Create an exact Unicode-codepoint source span from the current turn."""

    text = _bounded_text(source_turn_text, "source turn", MAX_SOURCE_TURN_CHARACTERS)
    start = _nonnegative_integer(start_offset, "source span start")
    end = _nonnegative_integer(end_offset, "source span end")
    if end <= start or end > len(text):
        _reject("SOURCE_SPAN_INVALID", "source span bounds are invalid")
    surface = text[start:end]
    if not surface:
        _reject("SOURCE_SPAN_INVALID", "source span is empty")
    return {
        "start_offset": start,
        "end_offset": end,
        "exact_surface_value": surface,
        "surface_digest": _checksum(surface),
    }


def create_evidence_reference_v2(
    *,
    reference_kind: str,
    reference_digest: str,
    verification_status: str,
) -> dict[str, str]:
    """Create one bounded advisory evidence reference."""

    body = {
        "reference_kind": reference_kind,
        "reference_digest": reference_digest,
        "verification_status": verification_status,
    }
    identity = "proposal-evidence-sha256:" + hashlib.sha256(
        _canonical_bytes(body)
    ).hexdigest()
    return {"reference_id": identity, **body}


def create_proposed_semantic_operation_v2(
    *,
    conversation_identity: str,
    operation_type: str,
    slot_class: str,
    slot_role: str,
    cardinality_key: str,
    surface_value: str | None,
    canonical_value: str | None,
    source_spans: list[dict[str, Any]],
    target_slot_id: str | None = None,
    proposed_slot_id: str | None = None,
    proposed_equivalence_key: str | None = None,
    depends_on_slot_ids: list[str] | None = None,
    evidence_reference_ids: list[str] | None = None,
    clarification_reason: str | None = None,
) -> dict[str, Any]:
    """Package an untrusted operation and assign proposal-local integrity."""

    if proposed_slot_id is None and slot_class in cwm_v2.SEMANTIC_SLOT_CLASSES:
        proposed_slot_id = cwm_v2._slot_identity(
            conversation_identity, slot_class, cardinality_key
        )
    if (
        proposed_equivalence_key is None
        and canonical_value is not None
        and slot_class in cwm_v2.SEMANTIC_SLOT_CLASSES
    ):
        proposed_equivalence_key = cwm_v2._equivalence_key(
            slot_class, slot_role, canonical_value
        )
    body = {
        "operation_type": operation_type,
        "slot_class": slot_class,
        "slot_role": slot_role,
        "cardinality_key": cardinality_key,
        "proposed_slot_id": proposed_slot_id,
        "target_slot_id": target_slot_id,
        "surface_value": surface_value,
        "canonical_value": canonical_value,
        "proposed_equivalence_key": proposed_equivalence_key,
        "source_spans": deepcopy(source_spans),
        "depends_on_slot_ids": sorted(depends_on_slot_ids or []),
        "evidence_reference_ids": sorted(evidence_reference_ids or []),
        "clarification_reason": clarification_reason,
    }
    operation_id = "interpreter-operation-local-sha256:" + hashlib.sha256(
        _canonical_bytes(body)
    ).hexdigest()
    return {"operation_id": operation_id, **body}


def create_conversation_interpreter_proposal_v2(
    *,
    interpreter_identity: str,
    interpreter_class: str,
    interpreter_version: str,
    conversation_identity: str,
    workspace_identity_hash: str,
    session_identity_hash: str,
    source_turn_identity: str,
    source_turn_digest: str,
    expected_cwm_revision: int,
    expected_semantic_revision: int,
    proposed_semantic_operations: list[dict[str, Any]],
    evidence_references: list[dict[str, Any]] | None = None,
    advisory_confidence: dict[str, Any] | None = None,
    ambiguity_declaration: dict[str, Any] | None = None,
    conflict_declaration: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create one canonical proposal envelope without accepting its meaning."""

    proposal = {
        "proposal_type": PLATFORM_CORE_CONVERSATION_INTERPRETER_PROPOSAL_SCHEMA_V1,
        "proposal_version": "V1",
        "proposal_id": None,
        "interpreter_identity": interpreter_identity,
        "interpreter_class": interpreter_class,
        "interpreter_version": interpreter_version,
        "conversation_identity": conversation_identity,
        "workspace_identity_hash": workspace_identity_hash,
        "session_identity_hash": session_identity_hash,
        "source_turn_identity": source_turn_identity,
        "source_turn_digest": source_turn_digest,
        "expected_cwm_revision": expected_cwm_revision,
        "expected_semantic_revision": expected_semantic_revision,
        "proposed_semantic_operations": sorted(
            deepcopy(proposed_semantic_operations),
            key=lambda operation: operation.get("operation_id", ""),
        ),
        "evidence_references": sorted(
            deepcopy(evidence_references or []),
            key=lambda reference: reference.get("reference_id", ""),
        ),
        "advisory_confidence": deepcopy(
            advisory_confidence or _default_confidence()
        ),
        "ambiguity_declaration": deepcopy(
            ambiguity_declaration or _empty_declaration()
        ),
        "conflict_declaration": deepcopy(
            conflict_declaration or _empty_declaration()
        ),
        "boundary_flags": deepcopy(_BOUNDARY_FLAGS),
        "integrity_checksum": None,
    }
    return _with_proposal_identity_and_integrity(proposal)


def validate_conversation_interpreter_proposal_v2(
    proposal: dict[str, Any],
    *,
    current_state: dict[str, Any],
    source_turn_text: str,
    observed_at: str,
    interpreter_registry: list[dict[str, Any]],
) -> dict[str, Any]:
    """Validate one proposal and return candidate operations without mutation."""

    candidate = _validate_proposal_envelope(proposal)
    registry = _validate_interpreter_registry(interpreter_registry)
    descriptor = registry.get(candidate["interpreter_identity"])
    if descriptor is None or not descriptor["enabled"]:
        _reject("UNKNOWN_INTERPRETER_IDENTITY", "interpreter identity is not enabled")
    if descriptor["interpreter_class"] != candidate["interpreter_class"]:
        _reject("INTERPRETER_CLASS_MISMATCH", "interpreter class binding is invalid")
    if descriptor["interpreter_version"] != candidate["interpreter_version"]:
        _reject("INTERPRETER_VERSION_MISMATCH", "interpreter version binding is invalid")

    state = _validated_current_state(current_state, observed_at=observed_at)
    envelope = state["envelope"]
    if candidate["expected_cwm_revision"] != state["revision"] or candidate[
        "expected_semantic_revision"
    ] != state["semantic_revision"]:
        _reject("STALE_CWM_REVISION", "proposal CWM revision binding is stale")
    expected_bindings = {
        "conversation_identity": envelope["conversation_identity"],
        "workspace_identity_hash": envelope["workspace_identity_hash"],
        "session_identity_hash": envelope["session_identity_hash"],
    }
    for field, expected in expected_bindings.items():
        if candidate[field] != expected:
            _reject("CONVERSATION_BINDING_MISMATCH", f"{field} binding is invalid")

    turn_text = _bounded_text(
        source_turn_text, "source turn", MAX_SOURCE_TURN_CHARACTERS
    )
    turn_binding = create_source_turn_binding_v2(
        conversation_identity=envelope["conversation_identity"],
        session_identity_hash=envelope["session_identity_hash"],
        expected_cwm_revision=state["revision"],
        source_turn_text=turn_text,
    )
    if candidate["source_turn_digest"] != turn_binding["source_turn_digest"] or (
        candidate["source_turn_identity"] != turn_binding["source_turn_identity"]
    ):
        _reject("MISSING_SOURCE_BINDING", "proposal source-turn binding is invalid")

    evidence = _validate_evidence_references(candidate["evidence_references"])
    confidence = _validate_confidence(candidate["advisory_confidence"])
    operations = _validate_proposed_operations(
        candidate["proposed_semantic_operations"],
        state=state,
        source_turn_text=turn_text,
        evidence=evidence,
        advisory_confidence=confidence,
    )
    ambiguity = _validate_declaration(
        candidate["ambiguity_declaration"],
        "ambiguity",
        operation_ids={operation["operation_id"] for operation in operations},
    )
    conflict = _validate_declaration(
        candidate["conflict_declaration"],
        "conflict",
        operation_ids={operation["operation_id"] for operation in operations},
    )
    detected_conflicts = _detect_internal_conflicts(operations)
    if set(conflict["operation_ids"]) != detected_conflicts:
        _reject(
            "CONFLICT_DECLARATION_MISMATCH",
            "proposal conflict declaration is not deterministic",
        )
    clarification_ids = {
        operation["operation_id"]
        for operation in operations
        if operation["candidate_operation_type"]
        == _CANDIDATE_OPERATION_TYPE[PROPOSE_CLARIFICATION_REQUIREMENT]
    }
    clarification_required = bool(
        ambiguity["operation_ids"] or conflict["operation_ids"] or clarification_ids
    )
    candidate_set = _candidate_operation_set(
        proposal=candidate,
        operations=operations,
        ambiguity_operation_ids=ambiguity["operation_ids"],
        conflict_operation_ids=conflict["operation_ids"],
        clarification_required=clarification_required,
    )
    return {
        "conversation_interpreter_proposal_runtime_version": (
            PLATFORM_CORE_CONVERSATION_INTERPRETER_PROPOSAL_RUNTIME_V2
        ),
        "validation_disposition": (
            CLARIFICATION_REQUIRED if clarification_required else ADMISSIBLE
        ),
        "proposal_id": candidate["proposal_id"],
        "rejection_reasons": [],
        "candidate_operation_set": candidate_set,
        "semantic_cwm_mutated": False,
        "conversation_transition_applied": False,
        "objective_created": False,
        "execution_invoked": False,
    }


def assess_conversation_interpreter_proposal_v2(
    proposal: dict[str, Any],
    *,
    current_state: dict[str, Any],
    source_turn_text: str,
    observed_at: str,
    interpreter_registry: list[dict[str, Any]],
) -> dict[str, Any]:
    """Return one stable rejection reason instead of raising to a host."""

    try:
        return validate_conversation_interpreter_proposal_v2(
            proposal,
            current_state=current_state,
            source_turn_text=source_turn_text,
            observed_at=observed_at,
            interpreter_registry=interpreter_registry,
        )
    except ProposalValidationError as exc:
        return {
            "conversation_interpreter_proposal_runtime_version": (
                PLATFORM_CORE_CONVERSATION_INTERPRETER_PROPOSAL_RUNTIME_V2
            ),
            "validation_disposition": REJECTED,
            "proposal_id": (
                proposal.get("proposal_id") if isinstance(proposal, dict) else None
            ),
            "rejection_reasons": [exc.reason_code],
            "candidate_operation_set": None,
            "semantic_cwm_mutated": False,
            "conversation_transition_applied": False,
            "objective_created": False,
            "execution_invoked": False,
        }


def compare_validated_candidate_operation_sets_v2(
    candidate_operation_sets: list[dict[str, Any]],
) -> dict[str, Any]:
    """Compare interpreters as an unordered set with no vote or confidence rule."""

    if not isinstance(candidate_operation_sets, list) or not (
        1 <= len(candidate_operation_sets) <= MAX_COMPARISON_INPUTS
    ):
        _reject("COMPARISON_INPUT_INVALID", "candidate comparison input is invalid")
    validated = [
        _validate_candidate_operation_set(item) for item in candidate_operation_sets
    ]
    validated = sorted(validated, key=lambda item: item["candidate_operation_set_id"])
    binding = {
        (
            item["conversation_identity"],
            item["workspace_identity_hash"],
            item["session_identity_hash"],
            item["source_turn_identity"],
            item["source_turn_digest"],
            item["expected_cwm_revision"],
            item["expected_semantic_revision"],
        )
        for item in validated
    }
    if len(binding) != 1:
        _reject("COMPARISON_BINDING_MISMATCH", "candidate sets have different bindings")

    operations_by_semantic_key: dict[bytes, dict[str, Any]] = {}
    values_by_position: dict[tuple[str, str, str], set[str | None]] = {}
    for item in validated:
        for operation in item["candidate_operations"]:
            semantic = _candidate_semantic_projection(operation)
            operations_by_semantic_key[_canonical_bytes(semantic)] = deepcopy(operation)
            position = (
                operation["slot_class"],
                operation["slot_role"],
                operation["cardinality_key"],
            )
            if operation["canonical_value"] is not None:
                values_by_position.setdefault(position, set()).add(
                    operation["canonical_value"]
                )
    material_conflicts = sorted(
        ":".join(position)
        for position, values in values_by_position.items()
        if len(values) > 1
    )
    merged_operations = [
        operations_by_semantic_key[key] for key in sorted(operations_by_semantic_key)
    ]
    semantic_digests = {item["semantic_reduction_digest"] for item in validated}
    if material_conflicts:
        disposition = MATERIAL_CONFLICT
        clarification_required = True
        reduction_allowed = False
    elif len(semantic_digests) == 1:
        disposition = CONSENSUS_NON_AUTHORITATIVE
        clarification_required = any(
            item["clarification_required"] for item in validated
        )
        reduction_allowed = not clarification_required
    else:
        disposition = COMPATIBLE_UNION_NON_AUTHORITATIVE
        clarification_required = any(
            item["clarification_required"] for item in validated
        )
        reduction_allowed = not clarification_required
    comparison = {
        "comparison_type": PLATFORM_CORE_INTERPRETER_COMPARISON_SCHEMA_V1,
        "comparison_disposition": disposition,
        "candidate_operation_set_ids": [
            item["candidate_operation_set_id"] for item in validated
        ],
        "candidate_operations": merged_operations,
        "material_conflict_positions": material_conflicts,
        "clarification_required": clarification_required,
        "reduction_allowed": reduction_allowed,
        "interpreter_count": len(validated),
        "majority_authority_effect": False,
        "confidence_authority_effect": False,
        "selected_by_majority": False,
        "semantic_cwm_mutated": False,
        "conversation_transition_applied": False,
        "objective_created": False,
        "execution_invoked": False,
    }
    comparison["integrity_checksum"] = _checksum(comparison)
    return comparison


def validate_candidate_operation_set_v2(
    candidate_operation_set: dict[str, Any],
) -> dict[str, Any]:
    """Revalidate one candidate set without granting commit authority."""

    return _validate_candidate_operation_set(candidate_operation_set)


def _validate_proposal_envelope(proposal: Any) -> dict[str, Any]:
    if not isinstance(proposal, dict):
        _reject("PROPOSAL_SCHEMA_INVALID", "proposal must be an object")
    try:
        encoded = _canonical_bytes(proposal)
    except (TypeError, ValueError):
        _reject("PROPOSAL_SCHEMA_INVALID", "proposal is not canonical JSON")
    if len(encoded) > MAX_PROPOSAL_BYTES:
        _reject("PROPOSAL_TOO_LARGE", "proposal exceeds byte bound")
    _reject_forbidden_authority_keys(proposal)
    candidate = _closed_object(proposal, _PROPOSAL_FIELDS, "proposal")
    if candidate["proposal_type"] != (
        PLATFORM_CORE_CONVERSATION_INTERPRETER_PROPOSAL_SCHEMA_V1
    ) or candidate["proposal_version"] != "V1":
        _reject("UNKNOWN_PROPOSAL_VERSION", "proposal type or version is unknown")
    supplied_integrity = candidate["integrity_checksum"]
    integrity_body = deepcopy(candidate)
    integrity_body.pop("integrity_checksum")
    if supplied_integrity != _checksum(integrity_body):
        _reject("INVALID_INTEGRITY", "proposal integrity is invalid")
    identity_body = deepcopy(candidate)
    identity_body["proposal_id"] = None
    identity_body["integrity_checksum"] = None
    expected_id = "interpreter-proposal-local-sha256:" + hashlib.sha256(
        _canonical_bytes(identity_body)
    ).hexdigest()
    if candidate["proposal_id"] != expected_id:
        _reject("INVALID_PROPOSAL_IDENTITY", "proposal identity is invalid")
    _token(candidate["interpreter_identity"], "interpreter identity")
    if candidate["interpreter_class"] not in INTERPRETER_CLASSES:
        _reject("UNKNOWN_INTERPRETER_CLASS", "interpreter class is unknown")
    _token(candidate["interpreter_version"], "interpreter version")
    _token(candidate["conversation_identity"], "conversation identity")
    _digest(candidate["workspace_identity_hash"], "workspace identity hash", "sha256:")
    _digest(candidate["session_identity_hash"], "session identity hash", "sha256:")
    _digest(
        candidate["source_turn_identity"],
        "source turn identity",
        "conversation-turn-local-sha256:",
    )
    _digest(candidate["source_turn_digest"], "source turn digest", "sha256:")
    _nonnegative_integer(candidate["expected_cwm_revision"], "expected CWM revision")
    _nonnegative_integer(
        candidate["expected_semantic_revision"], "expected semantic revision"
    )
    if candidate["boundary_flags"] != _BOUNDARY_FLAGS:
        _reject("FORBIDDEN_AUTHORITY_FIELD", "proposal boundary flags are invalid")
    return candidate


def _validated_current_state(state: Any, *, observed_at: str) -> dict[str, Any]:
    try:
        candidate = cwm_v2.validate_conversation_working_memory_state_v2(state)
        observed = cwm_v2._canonical_timestamp(observed_at, "observed_at")
    except FailClosedRuntimeError as exc:
        _reject("STATE_VALIDATION_FAILED", str(exc))
    if cwm_v2._is_v2_expired(candidate, observed):
        _reject("STATE_NOT_ACTIVE", "conversation state is expired")
    if candidate["envelope"]["availability_state"] != cwm_v2.ACTIVE:
        _reject("STATE_NOT_ACTIVE", "conversation state is not active")
    if candidate["envelope"]["conversation_phase"] not in {
        cwm_v2.COLLECTING,
        cwm_v2.CLARIFYING,
        cwm_v2.CANDIDATE_REVIEW,
    }:
        _reject("STATE_PHASE_FORBIDDEN", "conversation phase rejects interpretation")
    return candidate


def _validate_interpreter_registry(
    value: Any,
) -> dict[str, dict[str, Any]]:
    if not isinstance(value, list) or len(value) > MAX_INTERPRETER_REGISTRY_ENTRIES:
        _reject("INTERPRETER_REGISTRY_INVALID", "interpreter registry is invalid")
    registry: dict[str, dict[str, Any]] = {}
    for raw in value:
        item = _closed_object(raw, _REGISTRY_ENTRY_FIELDS, "interpreter registry entry")
        identity = _token(item["interpreter_identity"], "interpreter identity")
        if item["interpreter_class"] not in INTERPRETER_CLASSES:
            _reject("UNKNOWN_INTERPRETER_CLASS", "registry interpreter class is unknown")
        _token(item["interpreter_version"], "interpreter version")
        if not isinstance(item["enabled"], bool):
            _reject("INTERPRETER_REGISTRY_INVALID", "interpreter enabled state is invalid")
        if identity in registry:
            _reject("INTERPRETER_REGISTRY_INVALID", "interpreter registry contains duplicates")
        registry[identity] = item
    return registry


def _validate_proposed_operations(
    value: Any,
    *,
    state: dict[str, Any],
    source_turn_text: str,
    evidence: dict[str, dict[str, Any]],
    advisory_confidence: dict[str, Any],
) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not (
        1 <= len(value) <= MAX_PROPOSED_OPERATIONS
    ):
        _reject("PROPOSAL_CONTENT_INVALID", "proposed operation count is invalid")
    current_slots = {
        slot["slot_id"]: slot
        for slot in state["semantic_memory"]["semantic_slots"]
    }
    validated: list[dict[str, Any]] = []
    operation_ids: set[str] = set()
    for raw in value:
        _reject_forbidden_authority_keys(raw)
        item = _closed_object(raw, _OPERATION_FIELDS, "proposed semantic operation")
        operation_type = item["operation_type"]
        if operation_type in _FORBIDDEN_CONTROL_OPERATIONS:
            _reject("FORBIDDEN_CONTROL_ACT", "proposal attempts a control act")
        if operation_type not in PROPOSED_OPERATION_TYPES:
            _reject("FORBIDDEN_OPERATION", "proposed operation is not supported")
        expected_operation_id = _operation_identity(item)
        if item["operation_id"] != expected_operation_id:
            _reject("INVALID_OPERATION_IDENTITY", "proposed operation identity is invalid")
        if item["operation_id"] in operation_ids:
            _reject("CONTRADICTORY_OPERATIONS", "proposal contains duplicate operations")
        operation_ids.add(item["operation_id"])
        slot_class = item["slot_class"]
        if slot_class not in cwm_v2.SEMANTIC_SLOT_CLASSES:
            _reject("UNKNOWN_SLOT_CLASS", "proposed slot class is unknown")
        try:
            slot_role = cwm_v2._slot_role(slot_class, item["slot_role"])
            cardinality = cwm_v2._cardinality_key(
                slot_class, slot_role, item["cardinality_key"]
            )
        except FailClosedRuntimeError as exc:
            _reject("SLOT_TAXONOMY_INVALID", str(exc))
        expected_slot_id = cwm_v2._slot_identity(
            state["envelope"]["conversation_identity"], slot_class, cardinality
        )
        if item["proposed_slot_id"] != expected_slot_id:
            _reject("INVALID_SLOT_IDENTITY", "proposed slot identity is invalid")
        depends_on = _canonical_slot_ids(
            item["depends_on_slot_ids"], "operation dependencies"
        )
        if any(slot_id not in current_slots for slot_id in depends_on):
            _reject("INVALID_SLOT_DEPENDENCY", "operation dependency is absent")
        evidence_ids = _canonical_identifiers(
            item["evidence_reference_ids"],
            "evidence reference ids",
            "proposal-evidence-sha256:",
            MAX_EVIDENCE_REFERENCES,
        )
        if any(reference_id not in evidence for reference_id in evidence_ids):
            _reject("EVIDENCE_REFERENCE_INVALID", "operation evidence is absent")

        if operation_type == PROPOSE_CLARIFICATION_REQUIREMENT:
            _validate_clarification_operation(item)
            canonical_value = None
            equivalence_key = None
            spans: list[dict[str, Any]] = []
        else:
            spans = _validate_source_spans(item["source_spans"], source_turn_text)
            if not spans:
                _reject("MISSING_SOURCE_BINDING", "material operation has no source span")
            expected_surface = " ".join(
                span["exact_surface_value"] for span in spans
            )
            if item["surface_value"] != expected_surface:
                _reject("SOURCE_SPAN_INVALID", "surface value is not source anchored")
            try:
                canonical_value = cwm_v2._canonical_slot_value(
                    slot_class, slot_role, item["canonical_value"]
                )
            except FailClosedRuntimeError as exc:
                _reject("CANONICAL_VALUE_INVALID", str(exc))
            equivalence_key = cwm_v2._equivalence_key(
                slot_class, slot_role, canonical_value
            )
            if item["proposed_equivalence_key"] != equivalence_key:
                _reject(
                    "SEMANTIC_EQUIVALENCE_INVALID",
                    "proposed equivalence key is not validator-derived",
                )
            if item["clarification_reason"] is not None:
                _reject("PROPOSAL_CONTENT_INVALID", "material operation has clarification reason")

        target = item["target_slot_id"]
        _validate_operation_relationship(
            operation_type,
            proposed_slot_id=expected_slot_id,
            target_slot_id=target,
            current_slots=current_slots,
            slot_class=slot_class,
            equivalence_key=equivalence_key,
            evidence_reference_ids=evidence_ids,
        )
        validated.append(
            {
                "candidate_operation_type": _CANDIDATE_OPERATION_TYPE[operation_type],
                "operation_id": item["operation_id"],
                "slot_class": slot_class,
                "slot_role": slot_role,
                "cardinality_key": cardinality,
                "proposed_slot_id": expected_slot_id,
                "target_slot_id": target,
                "surface_value": item["surface_value"],
                "canonical_value": canonical_value,
                "validator_derived_equivalence_key": equivalence_key,
                "source_spans": spans,
                "depends_on_slot_ids": depends_on,
                "evidence_reference_ids": evidence_ids,
                "clarification_reason": item["clarification_reason"],
                "advisory_confidence": deepcopy(advisory_confidence),
                "authority_effect": False,
            }
        )
    validated = sorted(validated, key=lambda operation: operation["operation_id"])
    _reject_contradictory_operations(validated)
    return validated


def _validate_operation_relationship(
    operation_type: str,
    *,
    proposed_slot_id: str,
    target_slot_id: Any,
    current_slots: dict[str, dict[str, Any]],
    slot_class: str,
    equivalence_key: str | None,
    evidence_reference_ids: list[str],
) -> None:
    if target_slot_id is not None:
        _digest(target_slot_id, "target slot identity", "conversation-slot-sha256:")
    if operation_type == PROPOSE_SLOT_CREATION:
        if target_slot_id is not None or proposed_slot_id in current_slots:
            _reject("OPERATION_RELATIONSHIP_INVALID", "slot creation target is invalid")
        return
    if operation_type in {
        PROPOSE_SLOT_REVISION,
        PROPOSE_SEMANTIC_EQUIVALENCE,
        PROPOSE_CONFLICT,
    }:
        if target_slot_id != proposed_slot_id or target_slot_id not in current_slots:
            _reject("OPERATION_RELATIONSHIP_INVALID", "target slot is absent or mismatched")
        current_equivalence = current_slots[target_slot_id]["equivalence_key"]
        if operation_type == PROPOSE_SEMANTIC_EQUIVALENCE and (
            equivalence_key != current_equivalence
        ):
            _reject(
                "SEMANTIC_EQUIVALENCE_INVALID",
                "equivalence proposal differs from the active slot",
            )
        if operation_type == PROPOSE_CONFLICT and equivalence_key == current_equivalence:
            _reject(
                "CONFLICT_DECLARATION_MISMATCH",
                "conflict proposal is semantically equivalent",
            )
        return
    if operation_type == PROPOSE_REFERENCE_ATTACHMENT:
        if slot_class != cwm_v2.SEMANTIC_REFERENCE or not evidence_reference_ids:
            _reject("OPERATION_RELATIONSHIP_INVALID", "reference attachment is invalid")
        if target_slot_id is None or target_slot_id not in current_slots:
            _reject("OPERATION_RELATIONSHIP_INVALID", "reference target is absent")
        if proposed_slot_id in current_slots:
            _reject("OPERATION_RELATIONSHIP_INVALID", "reference slot already exists")
        return
    if operation_type == PROPOSE_CLARIFICATION_REQUIREMENT:
        if target_slot_id is not None and target_slot_id not in current_slots:
            _reject("OPERATION_RELATIONSHIP_INVALID", "clarification target is absent")


def _validate_clarification_operation(item: dict[str, Any]) -> None:
    if any(
        item[field] is not None
        for field in ("surface_value", "canonical_value", "proposed_equivalence_key")
    ) or item["source_spans"]:
        _reject("PROPOSAL_CONTENT_INVALID", "clarification operation carries semantics")
    if item["clarification_reason"] not in {
        "MISSING",
        "PARTIAL",
        "CONFLICTED",
        "STALE",
        "UNCONFIRMED",
        "UNSUPPORTED",
    }:
        _reject("PROPOSAL_CONTENT_INVALID", "clarification reason is invalid")


def _validate_source_spans(value: Any, source_turn_text: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or len(value) > MAX_SOURCE_SPANS:
        _reject("SOURCE_SPAN_INVALID", "source span count is invalid")
    spans: list[dict[str, Any]] = []
    prior_end = -1
    for raw in value:
        item = _closed_object(raw, _SOURCE_SPAN_FIELDS, "source span")
        start = _nonnegative_integer(item["start_offset"], "source span start")
        end = _nonnegative_integer(item["end_offset"], "source span end")
        if end <= start or end > len(source_turn_text) or start < prior_end:
            _reject("SOURCE_SPAN_INVALID", "source span bounds overlap or exceed turn")
        surface = source_turn_text[start:end]
        if item["exact_surface_value"] != surface or item["surface_digest"] != _checksum(surface):
            _reject("SOURCE_SPAN_INVALID", "source span content binding is invalid")
        spans.append(item)
        prior_end = end
    if spans != sorted(spans, key=lambda span: (span["start_offset"], span["end_offset"])):
        _reject("SOURCE_SPAN_INVALID", "source spans are not canonical")
    return spans


def _validate_evidence_references(value: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(value, list) or len(value) > MAX_EVIDENCE_REFERENCES:
        _reject("EVIDENCE_REFERENCE_INVALID", "evidence reference count is invalid")
    references: dict[str, dict[str, Any]] = {}
    for raw in value:
        item = _closed_object(raw, _EVIDENCE_REFERENCE_FIELDS, "evidence reference")
        if item["reference_kind"] not in {
            "SOURCE_TURN",
            "EXISTING_SLOT",
            "EXTERNAL_EVIDENCE",
        } or item["verification_status"] not in {
            "SOURCE_BOUND",
            "STATE_BOUND",
            "UNVERIFIED",
        }:
            _reject("EVIDENCE_REFERENCE_INVALID", "evidence reference vocabulary is invalid")
        _digest(item["reference_digest"], "evidence reference digest", "sha256:")
        identity_body = deepcopy(item)
        identity_body.pop("reference_id")
        expected_id = "proposal-evidence-sha256:" + hashlib.sha256(
            _canonical_bytes(identity_body)
        ).hexdigest()
        if item["reference_id"] != expected_id or expected_id in references:
            _reject("EVIDENCE_REFERENCE_INVALID", "evidence reference identity is invalid")
        references[expected_id] = item
    if value != [references[key] for key in sorted(references)]:
        _reject("EVIDENCE_REFERENCE_INVALID", "evidence references are not canonical")
    return references


def _validate_confidence(value: Any) -> dict[str, Any]:
    item = _closed_object(value, _CONFIDENCE_FIELDS, "advisory confidence")
    _token(item["scale_id"], "confidence scale")
    _bounded_text(item["reported_value"], "confidence value", MAX_TOKEN_CHARACTERS)
    limitations = item["limitations"]
    if not isinstance(limitations, list) or len(limitations) > 16:
        _reject("CONFIDENCE_INVALID", "confidence limitations are invalid")
    normalized = [_token(entry, "confidence limitation") for entry in limitations]
    if limitations != sorted(set(normalized)) or item["authority_effect"] is not False:
        _reject("CONFIDENCE_AUTHORITY_FORBIDDEN", "confidence cannot carry authority")
    return item


def _validate_declaration(
    value: Any,
    name: str,
    *,
    operation_ids: set[str],
) -> dict[str, Any]:
    item = _closed_object(value, _DECLARATION_FIELDS, f"{name} declaration")
    if not isinstance(item["declared"], bool):
        _reject("DECLARATION_INVALID", f"{name} declaration flag is invalid")
    identifiers = _canonical_identifiers(
        item["operation_ids"],
        f"{name} operation ids",
        "interpreter-operation-local-sha256:",
        MAX_DECLARATION_OPERATION_IDS,
    )
    if item["declared"] != bool(identifiers) or any(
        identifier not in operation_ids for identifier in identifiers
    ):
        _reject("DECLARATION_INVALID", f"{name} declaration binding is invalid")
    return item


def _detect_internal_conflicts(operations: list[dict[str, Any]]) -> set[str]:
    conflict_ids = {
        operation["operation_id"]
        for operation in operations
        if operation["candidate_operation_type"]
        == _CANDIDATE_OPERATION_TYPE[PROPOSE_CONFLICT]
    }
    by_position: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for operation in operations:
        if operation["canonical_value"] is not None:
            position = (
                operation["slot_class"],
                operation["slot_role"],
                operation["cardinality_key"],
            )
            by_position.setdefault(position, []).append(operation)
    for positioned in by_position.values():
        if len({operation["canonical_value"] for operation in positioned}) > 1:
            conflict_ids.update(operation["operation_id"] for operation in positioned)
    return conflict_ids


def _reject_contradictory_operations(operations: list[dict[str, Any]]) -> None:
    by_slot: dict[str, set[str]] = {}
    for operation in operations:
        by_slot.setdefault(operation["proposed_slot_id"], set()).add(
            operation["candidate_operation_type"]
        )
    for operation_types in by_slot.values():
        if "CREATE_CANDIDATE" in operation_types and "REVISE_CANDIDATE" in operation_types:
            _reject("CONTRADICTORY_OPERATIONS", "create and revise contradict")
        if "EQUIVALENCE_CANDIDATE" in operation_types and "CONFLICT_CANDIDATE" in operation_types:
            _reject("CONTRADICTORY_OPERATIONS", "equivalence and conflict contradict")


def _candidate_operation_set(
    *,
    proposal: dict[str, Any],
    operations: list[dict[str, Any]],
    ambiguity_operation_ids: list[str],
    conflict_operation_ids: list[str],
    clarification_required: bool,
) -> dict[str, Any]:
    semantic_projection = [
        _candidate_semantic_projection(operation) for operation in operations
    ]
    body = {
        "candidate_operation_set_type": (
            PLATFORM_CORE_VALIDATED_CANDIDATE_OPERATION_SET_SCHEMA_V1
        ),
        "candidate_operation_set_id": None,
        "proposal_id": proposal["proposal_id"],
        "interpreter_identity": proposal["interpreter_identity"],
        "interpreter_class": proposal["interpreter_class"],
        "conversation_identity": proposal["conversation_identity"],
        "workspace_identity_hash": proposal["workspace_identity_hash"],
        "session_identity_hash": proposal["session_identity_hash"],
        "source_turn_identity": proposal["source_turn_identity"],
        "source_turn_digest": proposal["source_turn_digest"],
        "expected_cwm_revision": proposal["expected_cwm_revision"],
        "expected_semantic_revision": proposal["expected_semantic_revision"],
        "candidate_operations": deepcopy(operations),
        "semantic_reduction_digest": _checksum(semantic_projection),
        "ambiguity_operation_ids": sorted(ambiguity_operation_ids),
        "conflict_operation_ids": sorted(conflict_operation_ids),
        "validation_disposition": (
            CLARIFICATION_REQUIRED if clarification_required else ADMISSIBLE
        ),
        "clarification_required": clarification_required,
        "reduction_allowed": not clarification_required,
        "confidence_authority_effect": False,
        "majority_authority_effect": False,
        "semantic_cwm_mutated": False,
        "conversation_transition_applied": False,
        "objective_created": False,
        "execution_invoked": False,
        "integrity_checksum": None,
    }
    identity_body = deepcopy(body)
    identity_body["candidate_operation_set_id"] = None
    identity_body["integrity_checksum"] = None
    body["candidate_operation_set_id"] = (
        "candidate-operation-set-local-sha256:"
        + hashlib.sha256(_canonical_bytes(identity_body)).hexdigest()
    )
    integrity_body = deepcopy(body)
    integrity_body.pop("integrity_checksum")
    body["integrity_checksum"] = _checksum(integrity_body)
    return body


def _validate_candidate_operation_set(value: Any) -> dict[str, Any]:
    item = _closed_object(value, _CANDIDATE_SET_FIELDS, "candidate operation set")
    if item["candidate_operation_set_type"] != (
        PLATFORM_CORE_VALIDATED_CANDIDATE_OPERATION_SET_SCHEMA_V1
    ):
        _reject("COMPARISON_INPUT_INVALID", "candidate set type is invalid")
    integrity_body = deepcopy(item)
    supplied = integrity_body.pop("integrity_checksum")
    if supplied != _checksum(integrity_body):
        _reject("COMPARISON_INPUT_INVALID", "candidate set integrity is invalid")
    identity_body = deepcopy(item)
    identity_body["candidate_operation_set_id"] = None
    identity_body["integrity_checksum"] = None
    expected_id = "candidate-operation-set-local-sha256:" + hashlib.sha256(
        _canonical_bytes(identity_body)
    ).hexdigest()
    if item["candidate_operation_set_id"] != expected_id:
        _reject("COMPARISON_INPUT_INVALID", "candidate set identity is invalid")
    _digest(
        item["candidate_operation_set_id"],
        "candidate operation set identity",
        "candidate-operation-set-local-sha256:",
    )
    _digest(item["proposal_id"], "proposal identity", "interpreter-proposal-local-sha256:")
    _token(item["interpreter_identity"], "interpreter identity")
    if item["interpreter_class"] not in INTERPRETER_CLASSES:
        _reject("COMPARISON_INPUT_INVALID", "candidate interpreter class is invalid")
    _token(item["conversation_identity"], "conversation identity")
    _digest(item["workspace_identity_hash"], "workspace identity hash", "sha256:")
    _digest(item["session_identity_hash"], "session identity hash", "sha256:")
    _digest(
        item["source_turn_identity"],
        "source turn identity",
        "conversation-turn-local-sha256:",
    )
    _digest(item["source_turn_digest"], "source turn digest", "sha256:")
    _nonnegative_integer(item["expected_cwm_revision"], "expected CWM revision")
    _nonnegative_integer(
        item["expected_semantic_revision"], "expected semantic revision"
    )
    if not isinstance(item["candidate_operations"], list) or not (
        1 <= len(item["candidate_operations"]) <= MAX_PROPOSED_OPERATIONS
    ):
        _reject("COMPARISON_INPUT_INVALID", "candidate operations are invalid")
    operations = [
        _validate_candidate_operation_for_comparison(
            operation,
            conversation_identity=item["conversation_identity"],
        )
        for operation in item["candidate_operations"]
    ]
    operation_ids = [operation["operation_id"] for operation in operations]
    if operation_ids != sorted(operation_ids) or len(set(operation_ids)) != len(
        operation_ids
    ):
        _reject("COMPARISON_INPUT_INVALID", "candidate operation order is invalid")
    expected_semantic_digest = _checksum(
        [_candidate_semantic_projection(operation) for operation in operations]
    )
    if item["semantic_reduction_digest"] != expected_semantic_digest:
        _reject("COMPARISON_INPUT_INVALID", "candidate semantic digest is invalid")

    operation_id_set = set(operation_ids)
    ambiguity_ids = _canonical_identifiers(
        item["ambiguity_operation_ids"],
        "candidate ambiguity operation ids",
        "interpreter-operation-local-sha256:",
        MAX_DECLARATION_OPERATION_IDS,
    )
    conflict_ids = _canonical_identifiers(
        item["conflict_operation_ids"],
        "candidate conflict operation ids",
        "interpreter-operation-local-sha256:",
        MAX_DECLARATION_OPERATION_IDS,
    )
    if any(identifier not in operation_id_set for identifier in ambiguity_ids):
        _reject("COMPARISON_INPUT_INVALID", "candidate ambiguity binding is invalid")
    if set(conflict_ids) != _detect_internal_conflicts(operations):
        _reject("COMPARISON_INPUT_INVALID", "candidate conflict binding is invalid")
    explicit_clarification = any(
        operation["candidate_operation_type"]
        == _CANDIDATE_OPERATION_TYPE[PROPOSE_CLARIFICATION_REQUIREMENT]
        for operation in operations
    )
    expected_clarification = bool(
        ambiguity_ids or conflict_ids or explicit_clarification
    )
    expected_disposition = (
        CLARIFICATION_REQUIRED if expected_clarification else ADMISSIBLE
    )
    if (
        item["validation_disposition"] != expected_disposition
        or item["clarification_required"] is not expected_clarification
        or item["reduction_allowed"] is expected_clarification
    ):
        _reject("COMPARISON_INPUT_INVALID", "candidate disposition is invalid")
    for field in (
        "confidence_authority_effect",
        "majority_authority_effect",
        "semantic_cwm_mutated",
        "conversation_transition_applied",
        "objective_created",
        "execution_invoked",
    ):
        if item[field] is not False:
            _reject("COMPARISON_INPUT_INVALID", "candidate set has authority")
    return item


def _validate_candidate_operation_for_comparison(
    value: Any,
    *,
    conversation_identity: str,
) -> dict[str, Any]:
    operation = _closed_object(
        value, _CANDIDATE_OPERATION_FIELDS, "candidate operation"
    )
    if operation["candidate_operation_type"] not in set(
        _CANDIDATE_OPERATION_TYPE.values()
    ):
        _reject("COMPARISON_INPUT_INVALID", "candidate operation type is invalid")
    _digest(
        operation["operation_id"],
        "candidate operation identity",
        "interpreter-operation-local-sha256:",
    )
    slot_class = operation["slot_class"]
    if slot_class not in cwm_v2.SEMANTIC_SLOT_CLASSES:
        _reject("COMPARISON_INPUT_INVALID", "candidate slot class is invalid")
    try:
        slot_role = cwm_v2._slot_role(slot_class, operation["slot_role"])
        cardinality = cwm_v2._cardinality_key(
            slot_class, slot_role, operation["cardinality_key"]
        )
    except FailClosedRuntimeError as exc:
        _reject("COMPARISON_INPUT_INVALID", str(exc))
    expected_slot_id = cwm_v2._slot_identity(
        conversation_identity, slot_class, cardinality
    )
    if operation["proposed_slot_id"] != expected_slot_id:
        _reject("COMPARISON_INPUT_INVALID", "candidate slot identity is invalid")
    if operation["target_slot_id"] is not None:
        _digest(
            operation["target_slot_id"],
            "candidate target slot identity",
            "conversation-slot-sha256:",
        )
    _canonical_slot_ids(operation["depends_on_slot_ids"], "candidate dependencies")
    _canonical_identifiers(
        operation["evidence_reference_ids"],
        "candidate evidence reference ids",
        "proposal-evidence-sha256:",
        MAX_EVIDENCE_REFERENCES,
    )
    _validate_confidence(operation["advisory_confidence"])
    if operation["authority_effect"] is not False:
        _reject("COMPARISON_INPUT_INVALID", "candidate operation has authority")

    if operation["candidate_operation_type"] == _CANDIDATE_OPERATION_TYPE[
        PROPOSE_CLARIFICATION_REQUIREMENT
    ]:
        if any(
            operation[field] is not None
            for field in (
                "surface_value",
                "canonical_value",
                "validator_derived_equivalence_key",
            )
        ) or operation["source_spans"]:
            _reject("COMPARISON_INPUT_INVALID", "clarification candidate is semantic")
        if operation["clarification_reason"] not in {
            "MISSING",
            "PARTIAL",
            "CONFLICTED",
            "STALE",
            "UNCONFIRMED",
            "UNSUPPORTED",
        }:
            _reject("COMPARISON_INPUT_INVALID", "clarification reason is invalid")
        return operation

    spans = _validate_detached_source_spans(operation["source_spans"])
    if not spans or operation["surface_value"] != " ".join(
        span["exact_surface_value"] for span in spans
    ):
        _reject("COMPARISON_INPUT_INVALID", "candidate source binding is invalid")
    try:
        canonical_value = cwm_v2._canonical_slot_value(
            slot_class, slot_role, operation["canonical_value"]
        )
    except FailClosedRuntimeError as exc:
        _reject("COMPARISON_INPUT_INVALID", str(exc))
    expected_equivalence = cwm_v2._equivalence_key(
        slot_class, slot_role, canonical_value
    )
    if (
        operation["canonical_value"] != canonical_value
        or operation["validator_derived_equivalence_key"] != expected_equivalence
        or operation["clarification_reason"] is not None
    ):
        _reject("COMPARISON_INPUT_INVALID", "candidate canonical value is invalid")
    return operation


def _validate_detached_source_spans(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not (1 <= len(value) <= MAX_SOURCE_SPANS):
        _reject("COMPARISON_INPUT_INVALID", "candidate source spans are invalid")
    spans: list[dict[str, Any]] = []
    prior_end = -1
    for raw in value:
        span = _closed_object(raw, _SOURCE_SPAN_FIELDS, "candidate source span")
        start = _nonnegative_integer(span["start_offset"], "source span start")
        end = _nonnegative_integer(span["end_offset"], "source span end")
        surface = _bounded_text(
            span["exact_surface_value"], "source span surface", MAX_SOURCE_TURN_CHARACTERS
        )
        if end <= start or start < prior_end or len(surface) != end - start:
            _reject("COMPARISON_INPUT_INVALID", "candidate source span is invalid")
        if span["surface_digest"] != _checksum(surface):
            _reject("COMPARISON_INPUT_INVALID", "candidate source digest is invalid")
        spans.append(span)
        prior_end = end
    return spans


def _candidate_semantic_projection(operation: dict[str, Any]) -> dict[str, Any]:
    return {
        field: deepcopy(operation[field])
        for field in (
            "candidate_operation_type",
            "slot_class",
            "slot_role",
            "cardinality_key",
            "proposed_slot_id",
            "target_slot_id",
            "surface_value",
            "canonical_value",
            "validator_derived_equivalence_key",
            "source_spans",
            "depends_on_slot_ids",
            "evidence_reference_ids",
            "clarification_reason",
        )
    }


def _operation_identity(operation: dict[str, Any]) -> str:
    body = deepcopy(operation)
    body.pop("operation_id", None)
    return "interpreter-operation-local-sha256:" + hashlib.sha256(
        _canonical_bytes(body)
    ).hexdigest()


def _with_proposal_identity_and_integrity(proposal: dict[str, Any]) -> dict[str, Any]:
    candidate = deepcopy(proposal)
    identity_body = deepcopy(candidate)
    identity_body["proposal_id"] = None
    identity_body["integrity_checksum"] = None
    candidate["proposal_id"] = "interpreter-proposal-local-sha256:" + hashlib.sha256(
        _canonical_bytes(identity_body)
    ).hexdigest()
    integrity_body = deepcopy(candidate)
    integrity_body.pop("integrity_checksum", None)
    candidate["integrity_checksum"] = _checksum(integrity_body)
    return candidate


def _canonical_slot_ids(value: Any, name: str) -> list[str]:
    return _canonical_identifiers(
        value,
        name,
        "conversation-slot-sha256:",
        cwm_v2.MAX_SEMANTIC_SLOTS,
    )


def _canonical_identifiers(
    value: Any,
    name: str,
    prefix: str,
    maximum: int,
) -> list[str]:
    if not isinstance(value, list) or len(value) > maximum:
        _reject("PROPOSAL_CONTENT_INVALID", f"{name} exceeds item bound")
    normalized = [_digest(item, name, prefix) for item in value]
    if value != sorted(set(normalized)):
        _reject("PROPOSAL_CONTENT_INVALID", f"{name} is not canonical")
    return normalized


def _default_confidence() -> dict[str, Any]:
    return {
        "scale_id": "UNSPECIFIED",
        "reported_value": "UNSPECIFIED",
        "limitations": ["NOT_CALIBRATED"],
        "authority_effect": False,
    }


def _empty_declaration() -> dict[str, Any]:
    return {"declared": False, "operation_ids": []}


def _closed_object(value: Any, fields: frozenset[str], name: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        _reject("PROPOSAL_SCHEMA_INVALID", f"{name} schema fields are invalid")
    return deepcopy(value)


def _reject_forbidden_authority_keys(value: Any) -> None:
    pending = [value]
    while pending:
        item = pending.pop()
        if isinstance(item, dict):
            forbidden = _FORBIDDEN_AUTHORITY_KEYS.intersection(item)
            if forbidden:
                _reject(
                    "FORBIDDEN_AUTHORITY_FIELD",
                    f"proposal contains forbidden field {sorted(forbidden)[0]}",
                )
            pending.extend(item.values())
        elif isinstance(item, list):
            pending.extend(item)


def _token(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value or len(value) > MAX_TOKEN_CHARACTERS:
        _reject("PROPOSAL_CONTENT_INVALID", f"{name} is invalid")
    if any(character.isspace() for character in value):
        _reject("PROPOSAL_CONTENT_INVALID", f"{name} contains whitespace")
    return value


def _bounded_text(value: Any, name: str, maximum: int) -> str:
    if not isinstance(value, str) or not value or len(value) > maximum:
        _reject("PROPOSAL_CONTENT_INVALID", f"{name} is invalid")
    return value


def _nonnegative_integer(value: Any, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        _reject("PROPOSAL_CONTENT_INVALID", f"{name} is invalid")
    return value


def _digest(value: Any, name: str, prefix: str) -> str:
    if not isinstance(value, str) or not value.startswith(prefix):
        _reject("PROPOSAL_CONTENT_INVALID", f"{name} is invalid")
    suffix = value.removeprefix(prefix)
    if len(suffix) != 64 or any(character not in "0123456789abcdef" for character in suffix):
        _reject("PROPOSAL_CONTENT_INVALID", f"{name} is invalid")
    return value


def _canonical_bytes(value: Any) -> bytes:
    return cwm_v2._canonical_bytes(value)


def _checksum(value: Any) -> str:
    return cwm_v2._checksum(value)


def _reject(reason_code: str, message: str) -> None:
    raise ProposalValidationError(reason_code, message)


__all__ = [
    "ADMISSIBLE",
    "CLARIFICATION_REQUIRED",
    "COMPATIBLE_UNION_NON_AUTHORITATIVE",
    "CONSENSUS_NON_AUTHORITATIVE",
    "DETERMINISTIC_PARSER",
    "EXTERNAL_LANGUAGE_MODEL",
    "INTERPRETER_CLASSES",
    "MATERIAL_CONFLICT",
    "OTHER_CERTIFIED_INTERPRETER",
    "PLATFORM_CORE_CONVERSATION_INTERPRETER_PROPOSAL_RUNTIME_V2",
    "PROPOSE_CLARIFICATION_REQUIREMENT",
    "PROPOSE_CONFLICT",
    "PROPOSE_REFERENCE_ATTACHMENT",
    "PROPOSE_SEMANTIC_EQUIVALENCE",
    "PROPOSE_SLOT_CREATION",
    "PROPOSE_SLOT_REVISION",
    "ProposalValidationError",
    "REJECTED",
    "RULE_BASED_INTERPRETER",
    "assess_conversation_interpreter_proposal_v2",
    "compare_validated_candidate_operation_sets_v2",
    "create_conversation_interpreter_proposal_v2",
    "create_evidence_reference_v2",
    "create_proposed_semantic_operation_v2",
    "create_source_span_v2",
    "create_source_turn_binding_v2",
    "validate_candidate_operation_set_v2",
    "validate_conversation_interpreter_proposal_v2",
]
