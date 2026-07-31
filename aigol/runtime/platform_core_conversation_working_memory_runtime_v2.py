"""Isolated Conversation Working Memory V2 foundation.

This module extends the G55-03 persistence substrate with a closed Conversation
Envelope and typed Semantic CWM document.  It remains local mutable working
state.  It does not implement a conversation state machine, interpretation,
Objective commitment, Platform Core integration, Replay, Authorization,
capability selection, Development Governance, or Worker execution.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import timedelta
import hashlib
import json
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_conversation_working_memory_runtime import (
    COMMITTED,
    COMMITTING,
    DEFAULT_TTL_SECONDS,
    MAX_COLLECTION_ITEM_CHARACTERS,
    MAX_COLLECTION_ITEMS,
    MAX_STATE_BYTES,
    MAX_TEXT_CHARACTERS,
    MAX_TTL_SECONDS,
    PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_OWNER,
    PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_RUNTIME_V1,
    PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_SCHEMA_V1,
    _BOUNDARY_FIELDS,
    _INTEGRITY_ALGORITHM,
    _canonical_bytes,
    _canonical_timestamp,
    _checksum,
    _conversation_root,
    _expiration_timestamp,
    _identity_hash,
    _is_expired,
    _normalize_workspace_identity,
    _parse_timestamp,
    _remove_state,
    _require_expected_revision,
    _require_identity,
    _state_path,
    _store_lock,
    _with_integrity,
    _write_state_atomically,
    validate_conversation_working_memory_state,
)


PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_RUNTIME_V2 = (
    "PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_RUNTIME_V2"
)
PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_SCHEMA_V2 = (
    "PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_SCHEMA_V2"
)
PLATFORM_CORE_CONVERSATION_ENVELOPE_SCHEMA_V1 = (
    "PLATFORM_CORE_CONVERSATION_ENVELOPE_SCHEMA_V1"
)
PLATFORM_CORE_CONVERSATION_ENVELOPE_RUNTIME_V1 = (
    "PLATFORM_CORE_CONVERSATION_ENVELOPE_RUNTIME_V1"
)
PLATFORM_CORE_SEMANTIC_CWM_SCHEMA_V2 = (
    "PLATFORM_CORE_SEMANTIC_CWM_SCHEMA_V2"
)
PLATFORM_CORE_SEMANTIC_CWM_RUNTIME_V2 = (
    "PLATFORM_CORE_SEMANTIC_CWM_RUNTIME_V2"
)
PLATFORM_CORE_SEMANTIC_NORMALIZATION_RULESET_V1 = (
    "PLATFORM_CORE_SEMANTIC_NORMALIZATION_RULESET_V1"
)
PLATFORM_CORE_CWM_V1_TO_V2_MIGRATION_V1 = (
    "PLATFORM_CORE_CWM_V1_TO_V2_MIGRATION_V1"
)

OPERATIVE_ACTION = "OPERATIVE_ACTION"
OPERATIVE_SUBJECT = "OPERATIVE_SUBJECT"
DESIRED_OUTCOME = "DESIRED_OUTCOME"
WORK_TYPE = "WORK_TYPE"
GOVERNING_QUALIFIER = "GOVERNING_QUALIFIER"
SEMANTIC_REFERENCE = "SEMANTIC_REFERENCE"

SEMANTIC_SLOT_CLASSES = (
    OPERATIVE_ACTION,
    OPERATIVE_SUBJECT,
    DESIRED_OUTCOME,
    WORK_TYPE,
    GOVERNING_QUALIFIER,
    SEMANTIC_REFERENCE,
)

PRIMARY = "PRIMARY"
SECONDARY = "SECONDARY"
PRESERVATION = "PRESERVATION"
OUTPUT = "OUTPUT"
ACCEPTANCE = "ACCEPTANCE"
ASSUMPTION = "ASSUMPTION"
SCOPE = "SCOPE"
CAPABILITY_HINT = "CAPABILITY_HINT"
EVIDENCE = "EVIDENCE"

CANONICAL_GOVERNED_WORK_TYPES = (
    "AUDIT_ONLY",
    "IMPLEMENTATION",
    "REVIEW",
    "CERTIFICATION",
    "ANALYSIS",
    "DOCUMENTATION",
)

SLOT_ROLES = {
    OPERATIVE_ACTION: frozenset({PRIMARY}),
    OPERATIVE_SUBJECT: frozenset({PRIMARY}),
    DESIRED_OUTCOME: frozenset({PRIMARY, SECONDARY}),
    WORK_TYPE: frozenset(CANONICAL_GOVERNED_WORK_TYPES),
    GOVERNING_QUALIFIER: frozenset(
        {PRESERVATION, OUTPUT, ACCEPTANCE, ASSUMPTION}
    ),
    SEMANTIC_REFERENCE: frozenset({SCOPE, CAPABILITY_HINT, EVIDENCE}),
}

PROPOSED = "PROPOSED"
ASSERTED = "ASSERTED"
CONFIRMED = "CONFIRMED"
CONFLICTED = "CONFLICTED"
STALE = "STALE"
SLOT_STATUSES = frozenset(
    {PROPOSED, ASSERTED, CONFIRMED, CONFLICTED, STALE}
)

EMPTY = "EMPTY"
PARTIAL = "PARTIAL"
COMPLETE = "COMPLETE"
SLOT_COMPLETENESS = frozenset(
    {EMPTY, PARTIAL, COMPLETE, CONFLICTED, STALE}
)

CONTEXT_DERIVED = "CONTEXT_DERIVED"
DETERMINISTIC_NORMALIZATION = "DETERMINISTIC_NORMALIZATION"
HUMAN_ASSERTED = "HUMAN_ASSERTED"
HUMAN_CONFIRMED = "HUMAN_CONFIRMED"
CONFIDENCE_CLASSES = frozenset(
    {
        CONTEXT_DERIVED,
        DETERMINISTIC_NORMALIZATION,
        HUMAN_ASSERTED,
        HUMAN_CONFIRMED,
        CONFLICTED,
    }
)

REQUIRED = "REQUIRED"
CONDITIONAL = "CONDITIONAL"
OPTIONAL = "OPTIONAL"
MATERIALITY_VALUES = frozenset({REQUIRED, CONDITIONAL, OPTIONAL})

HUMAN_TURN = "HUMAN_TURN"
CLARIFICATION_REPLY = "CLARIFICATION_REPLY"
PRIOR_SLOT = "PRIOR_SLOT"
OWNER_DISPOSITION = "OWNER_DISPOSITION"
PROVENANCE_SOURCE_KINDS = frozenset(
    {HUMAN_TURN, CLARIFICATION_REPLY, PRIOR_SLOT, OWNER_DISPOSITION}
)

ASSERTED_NOT_AUTHENTICATED = "ASSERTED_NOT_AUTHENTICATED"
HUMAN_ORIGINATOR = "HUMAN_ORIGINATOR"
INTERFACE_TRANSPORT = "INTERFACE_TRANSPORT"
CONVERSATION_OWNER_RUNTIME = "CONVERSATION_OWNER_RUNTIME"
PARTICIPANT_ROLES = frozenset(
    {HUMAN_ORIGINATOR, INTERFACE_TRANSPORT, CONVERSATION_OWNER_RUNTIME}
)
LOCAL_ASSERTION = "LOCAL_ASSERTION"
RUNTIME_DECLARATION = "RUNTIME_DECLARATION"
PARTICIPANT_IDENTITY_SOURCES = frozenset(
    {LOCAL_ASSERTION, RUNTIME_DECLARATION}
)

LOCAL_CONVERSATION_V2 = "LOCAL_CONVERSATION_V2"
UNBOUND_MIGRATION = "UNBOUND_MIGRATION"
INTERFACE_IDENTITIES = frozenset(
    {LOCAL_CONVERSATION_V2, UNBOUND_MIGRATION}
)

ACTIVE = "ACTIVE"
COLLECTING = "COLLECTING"
BOUND = "BOUND"
LEGACY_REVIEW_REQUIRED = "LEGACY_REVIEW_REQUIRED"
NATIVE_V2 = "NATIVE_V2"
PARTICIPANT_BINDING_REQUIRED = "PARTICIPANT_BINDING_REQUIRED"
NOT_REQUIRED = "NOT_REQUIRED"

MAX_SEMANTIC_SLOTS = 64
MAX_SLOT_PROVENANCE_ENTRIES = 16
MAX_SLOT_HISTORY_ENTRIES = 32
MAX_NORMALIZATION_RULE_IDS = 16
MAX_PARTICIPANTS = 8
MAX_CARDINALITY_KEY_CHARACTERS = 256

_V2_STATE_FIELDS = frozenset(
    {
        "working_memory_type",
        "runtime_version",
        "schema_version",
        "runtime_owner",
        "revision",
        "envelope_revision",
        "semantic_revision",
        "envelope",
        "semantic_memory",
        "migration_metadata",
        *_BOUNDARY_FIELDS,
        "integrity_algorithm",
        "integrity_checksum",
    }
)

_ENVELOPE_FIELDS = frozenset(
    {
        "envelope_type",
        "envelope_runtime_version",
        "conversation_identity",
        "workspace_identity",
        "workspace_identity_hash",
        "session_identity",
        "session_identity_hash",
        "origin_interface_identity",
        "current_interface_identity",
        "participants",
        "context_scope",
        "availability_state",
        "conversation_phase",
        "semantic_memory_binding",
        "active_objective_candidate_binding",
        "created_at",
        "updated_at",
        "expires_at",
        "suspended_at",
        "restored_at",
        "closed_at",
        *_BOUNDARY_FIELDS,
    }
)

_SEMANTIC_MEMORY_FIELDS = frozenset(
    {
        "semantic_memory_type",
        "semantic_memory_runtime_version",
        "normalization_ruleset_version",
        "semantic_slots",
        "legacy_import",
    }
)

_SLOT_FIELDS = frozenset(
    {
        "slot_id",
        "slot_class",
        "slot_role",
        "cardinality_key",
        "value_kind",
        "surface_value",
        "canonical_value",
        "equivalence_key",
        "status",
        "completeness",
        "confidence_class",
        "materiality",
        "provenance",
        "depends_on",
        "slot_revision",
        "history",
    }
)

_PROVENANCE_FIELDS = frozenset(
    {
        "source_kind",
        "turn_number",
        "source_revision",
        "source_span",
        "content_digest",
        "normalization_rule_ids",
        "human_disposition",
    }
)

_HISTORY_FIELDS = frozenset(
    {
        "slot_revision",
        "changed_at",
        "change_kind",
        "prior_value_digest",
        "resulting_value_digest",
    }
)

_PARTICIPANT_FIELDS = frozenset(
    {
        "participant_role",
        "asserted_identity",
        "identity_source",
        "binding_disposition",
        "first_bound_revision",
        "last_confirmed_revision",
    }
)

_CONTEXT_SCOPE_FIELDS = frozenset(
    {
        "workspace_identity_hash",
        "session_identity_hash",
        "current_interface_identity",
        "scope_revision",
        "scope_status",
    }
)

_SEMANTIC_BINDING_FIELDS = frozenset(
    {
        "semantic_memory_type",
        "global_revision",
        "semantic_revision",
        "semantic_memory_digest",
    }
)

_MIGRATION_FIELDS = frozenset(
    {
        "migration_type",
        "migration_status",
        "source_schema_version",
        "source_runtime_version",
        "source_revision",
        "migrated_at",
        "review_disposition",
        "participant_binding_status",
    }
)

_LEGACY_IMPORT_FIELDS = frozenset(
    {
        "topic",
        "entities",
        "inferred_intent",
        "confirmed_facts",
        "assumptions",
        "unresolved_ambiguity",
        "confidence",
        "discarded_interpretations",
        "context_references",
        "candidate_objective_snapshot",
        "candidate_digest",
        "source_lifecycle_state",
    }
)

_FORBIDDEN_IDENTITY_FIELDS = frozenset(
    {
        "artifact_hash",
        "artifact_type",
        "replay_hash",
        "replay_identity",
        "replay_reference",
        "objective_id",
        "authorization_id",
        "worker_request_id",
    }
)

_VALUE_KINDS = {
    OPERATIVE_ACTION: "TEXT",
    OPERATIVE_SUBJECT: "TEXT",
    DESIRED_OUTCOME: "TEXT",
    WORK_TYPE: "ENUM",
    GOVERNING_QUALIFIER: "CLAUSE",
    SEMANTIC_REFERENCE: "REFERENCE",
}

_CLASS_ORDER = {value: index for index, value in enumerate(SEMANTIC_SLOT_CLASSES)}


def create_semantic_cwm_slot_v2(
    *,
    conversation_identity: str,
    slot_class: str,
    slot_role: str,
    cardinality_key: str,
    surface_value: str,
    canonical_value: str,
    status: str,
    completeness: str,
    confidence_class: str,
    materiality: str,
    provenance: list[dict[str, Any]] | tuple[dict[str, Any], ...],
    depends_on: list[str] | tuple[str, ...] = (),
    created_at: str,
) -> dict[str, Any]:
    """Create one revision-zero session-local semantic slot."""

    conversation = _require_local_identity(
        conversation_identity,
        "conversation_identity",
        prefix="conversation-local-sha256:",
    )
    slot_class_value = _closed_value(
        slot_class, SEMANTIC_SLOT_CLASSES, "slot_class"
    )
    slot_role_value = _slot_role(slot_class_value, slot_role)
    cardinality = _cardinality_key(
        slot_class_value, slot_role_value, cardinality_key
    )
    surface = _exact_text(surface_value, "surface_value")
    canonical = _canonical_slot_value(
        slot_class_value, slot_role_value, canonical_value
    )
    slot_id = _slot_identity(
        conversation,
        slot_class_value,
        cardinality,
    )
    equivalence_key = _equivalence_key(
        slot_class_value, slot_role_value, canonical
    )
    changed = _canonical_timestamp(created_at, "created_at")
    resulting_digest = _checksum(canonical)
    slot = {
        "slot_id": slot_id,
        "slot_class": slot_class_value,
        "slot_role": slot_role_value,
        "cardinality_key": cardinality,
        "value_kind": _VALUE_KINDS[slot_class_value],
        "surface_value": surface,
        "canonical_value": canonical,
        "equivalence_key": equivalence_key,
        "status": status,
        "completeness": completeness,
        "confidence_class": confidence_class,
        "materiality": materiality,
        "provenance": list(provenance),
        "depends_on": list(depends_on),
        "slot_revision": 0,
        "history": [
            {
                "slot_revision": 0,
                "changed_at": changed,
                "change_kind": "INITIALIZED",
                "prior_value_digest": None,
                "resulting_value_digest": resulting_digest,
            }
        ],
    }
    return validate_semantic_cwm_slot_v2(
        slot, conversation_identity=conversation
    )


def conversation_working_memory_conversation_identity_v2(
    *,
    workspace_identity: str | Path,
    session_identity: str,
    created_at: str,
) -> str:
    """Derive the deterministic local Envelope identity without persistence."""

    workspace = _normalize_workspace_identity(workspace_identity)
    session = _require_identity(session_identity, "session_identity")
    created = _canonical_timestamp(created_at, "created_at")
    return _conversation_identity(
        workspace_identity_hash=_identity_hash(workspace),
        session_identity_hash=_identity_hash(session),
        created_at=created,
    )


def create_conversation_working_memory_state_v2(
    *,
    runtime_root: str | Path,
    workspace_identity: str | Path,
    session_identity: str,
    created_at: str,
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
    origin_interface_identity: str = LOCAL_CONVERSATION_V2,
    participants: list[dict[str, Any]] | tuple[dict[str, Any], ...] = (),
    semantic_slots: list[dict[str, Any]] | tuple[dict[str, Any], ...] = (),
) -> dict[str, Any]:
    """Create one native V2 state in the existing isolated atomic store."""

    workspace = _normalize_workspace_identity(workspace_identity)
    session = _require_identity(session_identity, "session_identity")
    created = _canonical_timestamp(created_at, "created_at")
    expires = _expiration_timestamp(created, ttl_seconds)
    interface = _closed_value(
        origin_interface_identity,
        INTERFACE_IDENTITIES,
        "origin_interface_identity",
    )
    conversation = _conversation_identity(
        workspace_identity_hash=_identity_hash(workspace),
        session_identity_hash=_identity_hash(session),
        created_at=created,
    )
    semantic_memory = _semantic_memory(
        conversation_identity=conversation,
        semantic_slots=semantic_slots,
        legacy_import=None,
    )
    state = _compose_state(
        workspace=workspace,
        session=session,
        conversation=conversation,
        origin_interface=interface,
        participants=participants,
        semantic_memory=semantic_memory,
        revision=0,
        envelope_revision=0,
        semantic_revision=0,
        created_at=created,
        updated_at=created,
        expires_at=expires,
        migration_metadata=_native_migration_metadata(),
    )
    validated = validate_conversation_working_memory_state_v2(
        state,
        expected_workspace_identity=workspace,
        expected_session_identity=session,
    )
    root = _conversation_root(runtime_root)
    with _store_lock(root):
        path = _state_path(root, workspace, session)
        if path.exists():
            raise FailClosedRuntimeError(
                "conversation working memory state already exists"
            )
        _write_state_atomically(path, validated)
    return deepcopy(validated)


def load_conversation_working_memory_state_v2(
    *,
    runtime_root: str | Path,
    workspace_identity: str | Path,
    session_identity: str,
    observed_at: str,
) -> dict[str, Any] | None:
    """Load exact V2 state; V1 is never auto-migrated."""

    workspace = _normalize_workspace_identity(workspace_identity)
    session = _require_identity(session_identity, "session_identity")
    observed = _canonical_timestamp(observed_at, "observed_at")
    root = _conversation_root(runtime_root)
    with _store_lock(root):
        path = _state_path(root, workspace, session)
        if not path.exists():
            return None
        state = _read_json_state(path)
        validated = validate_conversation_working_memory_state_v2(
            state,
            expected_workspace_identity=workspace,
            expected_session_identity=session,
        )
        _reject_v2_expired(validated, observed)
        return deepcopy(validated)


def recover_conversation_working_memory_state_v2(
    *,
    runtime_root: str | Path,
    workspace_identity: str | Path,
    session_identity: str,
    observed_at: str,
) -> dict[str, Any] | None:
    """Recover exact V2 state and clean it only when it is expired."""

    workspace = _normalize_workspace_identity(workspace_identity)
    session = _require_identity(session_identity, "session_identity")
    observed = _canonical_timestamp(observed_at, "observed_at")
    root = _conversation_root(runtime_root)
    with _store_lock(root):
        path = _state_path(root, workspace, session)
        if not path.exists():
            return None
        state = validate_conversation_working_memory_state_v2(
            _read_json_state(path),
            expected_workspace_identity=workspace,
            expected_session_identity=session,
        )
        if _is_v2_expired(state, observed):
            _remove_state(path, root)
            return None
        return deepcopy(state)


def replace_conversation_working_memory_state_v2_atomically(
    *,
    runtime_root: str | Path,
    workspace_identity: str | Path,
    session_identity: str,
    expected_revision: int,
    replacement_state: dict[str, Any],
    observed_at: str,
) -> dict[str, Any]:
    """Replace a caller-prepared V2 revision after closed invariant checks."""

    workspace = _normalize_workspace_identity(workspace_identity)
    session = _require_identity(session_identity, "session_identity")
    observed = _canonical_timestamp(observed_at, "observed_at")
    root = _conversation_root(runtime_root)
    with _store_lock(root):
        path = _state_path(root, workspace, session)
        if not path.exists():
            raise FailClosedRuntimeError(
                "conversation working memory state is absent"
            )
        current = validate_conversation_working_memory_state_v2(
            _read_json_state(path),
            expected_workspace_identity=workspace,
            expected_session_identity=session,
        )
        _reject_v2_expired(current, observed)
        _require_expected_revision(current, expected_revision)
        candidate = validate_conversation_working_memory_state_v2(
            replacement_state,
            expected_workspace_identity=workspace,
            expected_session_identity=session,
        )
        _validate_v2_replacement(current, candidate, observed)
        _write_state_atomically(path, candidate)
        return deepcopy(candidate)


def migrate_conversation_working_memory_state_v1_to_v2(
    *,
    runtime_root: str | Path,
    workspace_identity: str | Path,
    session_identity: str,
    expected_revision: int,
    migrated_at: str,
) -> dict[str, Any]:
    """Explicitly migrate validated V1 state into review-required V2 state."""

    workspace = _normalize_workspace_identity(workspace_identity)
    session = _require_identity(session_identity, "session_identity")
    migrated = _canonical_timestamp(migrated_at, "migrated_at")
    root = _conversation_root(runtime_root)
    with _store_lock(root):
        path = _state_path(root, workspace, session)
        if not path.exists():
            raise FailClosedRuntimeError(
                "conversation working memory state is absent"
            )
        raw_v1 = _read_json_state(path)
        source = validate_conversation_working_memory_state(
            raw_v1,
            expected_workspace_identity=workspace,
            expected_session_identity=session,
        )
        _require_expected_revision(source, expected_revision)
        if _is_expired(source, migrated):
            raise FailClosedRuntimeError(
                "conversation working memory state is expired"
            )
        if source["lifecycle_state"] in {COMMITTING, COMMITTED}:
            raise FailClosedRuntimeError(
                "reserved commitment lifecycle cannot be migrated"
            )
        candidate = _migrate_v1_document(source, migrated)
        validated = validate_conversation_working_memory_state_v2(
            candidate,
            expected_workspace_identity=workspace,
            expected_session_identity=session,
        )
        backup_path = path.with_name("state.v1.migration-backup.json")
        if backup_path.exists():
            raise FailClosedRuntimeError(
                "conversation working memory migration backup already exists"
            )
        _write_state_atomically(backup_path, source)
        try:
            _write_state_atomically(path, validated)
            stored = validate_conversation_working_memory_state_v2(
                _read_json_state(path),
                expected_workspace_identity=workspace,
                expected_session_identity=session,
            )
        except Exception:
            _write_state_atomically(path, source)
            raise
        finally:
            if backup_path.exists():
                backup_path.unlink()
        return deepcopy(stored)


def validate_conversation_working_memory_state_v2(
    state: dict[str, Any],
    *,
    expected_workspace_identity: str | Path | None = None,
    expected_session_identity: str | None = None,
) -> dict[str, Any]:
    """Fail closed unless a V2 document is closed, bounded, and isolated."""

    candidate = _closed_object(state, _V2_STATE_FIELDS, "V2 state")
    _reject_forbidden_keys(candidate)
    if candidate["working_memory_type"] != (
        PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_SCHEMA_V2
    ):
        raise FailClosedRuntimeError("V2 working memory type is invalid")
    if candidate["runtime_version"] != (
        PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_RUNTIME_V2
    ):
        raise FailClosedRuntimeError("V2 runtime version is invalid")
    if candidate["schema_version"] != (
        PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_SCHEMA_V2
    ):
        raise FailClosedRuntimeError("V2 schema version is invalid")
    if candidate["runtime_owner"] != (
        PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_OWNER
    ):
        raise FailClosedRuntimeError("V2 runtime owner is invalid")
    _validate_boundary_fields(candidate, "V2 state")
    revision = _nonnegative_integer(candidate["revision"], "revision")
    envelope_revision = _nonnegative_integer(
        candidate["envelope_revision"], "envelope_revision"
    )
    semantic_revision = _nonnegative_integer(
        candidate["semantic_revision"], "semantic_revision"
    )
    if envelope_revision > revision or semantic_revision > revision:
        raise FailClosedRuntimeError("V2 component revision exceeds global revision")
    envelope = _validate_envelope(
        candidate["envelope"],
        revision=revision,
        semantic_revision=semantic_revision,
        semantic_memory=candidate["semantic_memory"],
    )
    semantic_memory = _validate_semantic_memory(
        candidate["semantic_memory"],
        conversation_identity=envelope["conversation_identity"],
    )
    migration = _validate_migration_metadata(
        candidate["migration_metadata"], semantic_memory=semantic_memory
    )
    _validate_cross_component_bindings(
        revision=revision,
        semantic_revision=semantic_revision,
        envelope=envelope,
        semantic_memory=semantic_memory,
        migration=migration,
    )
    workspace = envelope["workspace_identity"]
    session = envelope["session_identity"]
    if expected_workspace_identity is not None and workspace != (
        _normalize_workspace_identity(expected_workspace_identity)
    ):
        raise FailClosedRuntimeError("V2 working memory workspace mismatch")
    if expected_session_identity is not None and session != (
        _require_identity(expected_session_identity, "expected_session_identity")
    ):
        raise FailClosedRuntimeError("V2 working memory session mismatch")
    candidate["envelope"] = envelope
    candidate["semantic_memory"] = semantic_memory
    candidate["migration_metadata"] = migration
    if candidate["integrity_algorithm"] != _INTEGRITY_ALGORITHM:
        raise FailClosedRuntimeError("V2 integrity algorithm is invalid")
    supplied = candidate["integrity_checksum"]
    body = deepcopy(candidate)
    body.pop("integrity_checksum", None)
    if supplied != _checksum(body):
        raise FailClosedRuntimeError("V2 working memory integrity mismatch")
    if len(_canonical_bytes(candidate)) + 1 > MAX_STATE_BYTES:
        raise FailClosedRuntimeError("V2 working memory exceeds storage bound")
    return candidate


def validate_semantic_cwm_slot_v2(
    slot: dict[str, Any], *, conversation_identity: str
) -> dict[str, Any]:
    """Validate one canonical six-class semantic slot record."""

    candidate = _closed_object(slot, _SLOT_FIELDS, "semantic slot")
    _reject_forbidden_keys(candidate)
    conversation = _require_local_identity(
        conversation_identity,
        "conversation_identity",
        prefix="conversation-local-sha256:",
    )
    slot_class = _closed_value(
        candidate["slot_class"], SEMANTIC_SLOT_CLASSES, "slot_class"
    )
    slot_role = _slot_role(slot_class, candidate["slot_role"])
    cardinality = _cardinality_key(
        slot_class, slot_role, candidate["cardinality_key"]
    )
    expected_slot_id = _slot_identity(
        conversation, slot_class, cardinality
    )
    if candidate["slot_id"] != expected_slot_id:
        raise FailClosedRuntimeError("semantic slot identity is invalid")
    if candidate["value_kind"] != _VALUE_KINDS[slot_class]:
        raise FailClosedRuntimeError("semantic slot value kind is invalid")
    _exact_text(candidate["surface_value"], "surface_value")
    canonical = _canonical_slot_value(
        slot_class, slot_role, candidate["canonical_value"]
    )
    if candidate["equivalence_key"] != _equivalence_key(
        slot_class, slot_role, canonical
    ):
        raise FailClosedRuntimeError("semantic slot equivalence key is invalid")
    status = _closed_value(candidate["status"], SLOT_STATUSES, "status")
    completeness = _closed_value(
        candidate["completeness"], SLOT_COMPLETENESS, "completeness"
    )
    confidence = _closed_value(
        candidate["confidence_class"],
        CONFIDENCE_CLASSES,
        "confidence_class",
    )
    _closed_value(candidate["materiality"], MATERIALITY_VALUES, "materiality")
    _validate_slot_materiality(
        slot_class,
        slot_role,
        candidate["materiality"],
    )
    if status == CONFLICTED and (
        completeness != CONFLICTED or confidence != CONFLICTED
    ):
        raise FailClosedRuntimeError("conflicted semantic slot metadata is invalid")
    if status == STALE and completeness != STALE:
        raise FailClosedRuntimeError("stale semantic slot metadata is invalid")
    if completeness == COMPLETE and not canonical:
        raise FailClosedRuntimeError("complete semantic slot requires a value")
    provenance = _bounded_objects(
        candidate["provenance"],
        MAX_SLOT_PROVENANCE_ENTRIES,
        _validate_provenance,
        "provenance",
    )
    if not provenance:
        raise FailClosedRuntimeError("semantic slot requires provenance")
    dependencies = _slot_dependencies(candidate["depends_on"])
    if candidate["slot_id"] in dependencies:
        raise FailClosedRuntimeError("semantic slot cannot depend on itself")
    slot_revision = _nonnegative_integer(
        candidate["slot_revision"], "slot_revision"
    )
    history = _bounded_objects(
        candidate["history"],
        MAX_SLOT_HISTORY_ENTRIES,
        _validate_history,
        "history",
    )
    if not history or history[-1]["slot_revision"] != slot_revision:
        raise FailClosedRuntimeError("semantic slot history revision is invalid")
    expected_revisions = list(range(slot_revision + 1))
    actual_revisions = [entry["slot_revision"] for entry in history]
    if actual_revisions != expected_revisions:
        raise FailClosedRuntimeError("semantic slot history is not contiguous")
    if history[-1]["resulting_value_digest"] != _checksum(canonical):
        raise FailClosedRuntimeError("semantic slot history digest is invalid")
    candidate["provenance"] = provenance
    candidate["depends_on"] = dependencies
    candidate["history"] = history
    return candidate


def _compose_state(
    *,
    workspace: str,
    session: str,
    conversation: str,
    origin_interface: str,
    participants: list[dict[str, Any]] | tuple[dict[str, Any], ...],
    semantic_memory: dict[str, Any],
    revision: int,
    envelope_revision: int,
    semantic_revision: int,
    created_at: str,
    updated_at: str,
    expires_at: str,
    migration_metadata: dict[str, Any],
) -> dict[str, Any]:
    semantic_digest = _checksum(semantic_memory)
    envelope = {
        "envelope_type": PLATFORM_CORE_CONVERSATION_ENVELOPE_SCHEMA_V1,
        "envelope_runtime_version": PLATFORM_CORE_CONVERSATION_ENVELOPE_RUNTIME_V1,
        "conversation_identity": conversation,
        "workspace_identity": workspace,
        "workspace_identity_hash": _identity_hash(workspace),
        "session_identity": session,
        "session_identity_hash": _identity_hash(session),
        "origin_interface_identity": origin_interface,
        "current_interface_identity": origin_interface,
        "participants": list(participants),
        "context_scope": {
            "workspace_identity_hash": _identity_hash(workspace),
            "session_identity_hash": _identity_hash(session),
            "current_interface_identity": origin_interface,
            "scope_revision": 0,
            "scope_status": BOUND,
        },
        "availability_state": ACTIVE,
        "conversation_phase": COLLECTING,
        "semantic_memory_binding": {
            "semantic_memory_type": PLATFORM_CORE_SEMANTIC_CWM_SCHEMA_V2,
            "global_revision": revision,
            "semantic_revision": semantic_revision,
            "semantic_memory_digest": semantic_digest,
        },
        "active_objective_candidate_binding": None,
        "created_at": created_at,
        "updated_at": updated_at,
        "expires_at": expires_at,
        "suspended_at": None,
        "restored_at": None,
        "closed_at": None,
        **_BOUNDARY_FIELDS,
    }
    state = {
        "working_memory_type": PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_SCHEMA_V2,
        "runtime_version": PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_RUNTIME_V2,
        "schema_version": PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_SCHEMA_V2,
        "runtime_owner": PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_OWNER,
        "revision": revision,
        "envelope_revision": envelope_revision,
        "semantic_revision": semantic_revision,
        "envelope": envelope,
        "semantic_memory": semantic_memory,
        "migration_metadata": migration_metadata,
        **_BOUNDARY_FIELDS,
        "integrity_algorithm": _INTEGRITY_ALGORITHM,
    }
    return _with_integrity(state)


def _semantic_memory(
    *,
    conversation_identity: str,
    semantic_slots: list[dict[str, Any]] | tuple[dict[str, Any], ...],
    legacy_import: dict[str, Any] | None,
) -> dict[str, Any]:
    if not isinstance(semantic_slots, (list, tuple)):
        raise FailClosedRuntimeError("semantic slots must be a collection")
    if len(semantic_slots) > MAX_SEMANTIC_SLOTS:
        raise FailClosedRuntimeError("semantic slots exceed item bound")
    slots = [
        validate_semantic_cwm_slot_v2(
            item, conversation_identity=conversation_identity
        )
        for item in semantic_slots
    ]
    slots = sorted(slots, key=_slot_sort_key)
    if len({item["slot_id"] for item in slots}) != len(slots):
        raise FailClosedRuntimeError("semantic slots contain duplicate identity")
    _validate_semantic_cardinality(slots)
    slot_ids = {item["slot_id"] for item in slots}
    for item in slots:
        if not set(item["depends_on"]).issubset(slot_ids):
            raise FailClosedRuntimeError("semantic slot dependency is absent")
    return {
        "semantic_memory_type": PLATFORM_CORE_SEMANTIC_CWM_SCHEMA_V2,
        "semantic_memory_runtime_version": PLATFORM_CORE_SEMANTIC_CWM_RUNTIME_V2,
        "normalization_ruleset_version": (
            PLATFORM_CORE_SEMANTIC_NORMALIZATION_RULESET_V1
        ),
        "semantic_slots": slots,
        "legacy_import": deepcopy(legacy_import),
    }


def _validate_semantic_memory(
    value: Any, *, conversation_identity: str
) -> dict[str, Any]:
    candidate = _closed_object(
        value, _SEMANTIC_MEMORY_FIELDS, "semantic memory"
    )
    _reject_forbidden_keys(candidate)
    if candidate["semantic_memory_type"] != PLATFORM_CORE_SEMANTIC_CWM_SCHEMA_V2:
        raise FailClosedRuntimeError("semantic memory type is invalid")
    if candidate["semantic_memory_runtime_version"] != (
        PLATFORM_CORE_SEMANTIC_CWM_RUNTIME_V2
    ):
        raise FailClosedRuntimeError("semantic memory runtime version is invalid")
    if candidate["normalization_ruleset_version"] != (
        PLATFORM_CORE_SEMANTIC_NORMALIZATION_RULESET_V1
    ):
        raise FailClosedRuntimeError("semantic normalization ruleset is invalid")
    normalized = _semantic_memory(
        conversation_identity=conversation_identity,
        semantic_slots=candidate["semantic_slots"],
        legacy_import=_validate_legacy_import(candidate["legacy_import"]),
    )
    if candidate != normalized:
        raise FailClosedRuntimeError("semantic memory is not canonical")
    return candidate


def _validate_envelope(
    value: Any,
    *,
    revision: int,
    semantic_revision: int,
    semantic_memory: Any,
) -> dict[str, Any]:
    candidate = _closed_object(value, _ENVELOPE_FIELDS, "Envelope")
    _reject_forbidden_keys(candidate)
    if candidate["envelope_type"] != PLATFORM_CORE_CONVERSATION_ENVELOPE_SCHEMA_V1:
        raise FailClosedRuntimeError("Envelope type is invalid")
    if candidate["envelope_runtime_version"] != (
        PLATFORM_CORE_CONVERSATION_ENVELOPE_RUNTIME_V1
    ):
        raise FailClosedRuntimeError("Envelope runtime version is invalid")
    _validate_boundary_fields(candidate, "Envelope")
    workspace = _normalize_workspace_identity(candidate["workspace_identity"])
    session = _require_identity(candidate["session_identity"], "session_identity")
    if candidate["workspace_identity"] != workspace:
        raise FailClosedRuntimeError("Envelope workspace is not canonical")
    workspace_hash = _identity_hash(workspace)
    session_hash = _identity_hash(session)
    if candidate["workspace_identity_hash"] != workspace_hash:
        raise FailClosedRuntimeError("Envelope workspace identity mismatch")
    if candidate["session_identity_hash"] != session_hash:
        raise FailClosedRuntimeError("Envelope session identity mismatch")
    created = _canonical_timestamp(candidate["created_at"], "created_at")
    updated = _canonical_timestamp(candidate["updated_at"], "updated_at")
    expires = _canonical_timestamp(candidate["expires_at"], "expires_at")
    if candidate["created_at"] != created or candidate["updated_at"] != updated:
        raise FailClosedRuntimeError("Envelope timestamps are not canonical")
    if candidate["expires_at"] != expires:
        raise FailClosedRuntimeError("Envelope expiration is not canonical")
    if _parse_timestamp(updated, "updated_at") < _parse_timestamp(
        created, "created_at"
    ):
        raise FailClosedRuntimeError("Envelope updated_at precedes created_at")
    if _parse_timestamp(expires, "expires_at") <= _parse_timestamp(
        updated, "updated_at"
    ):
        raise FailClosedRuntimeError("Envelope expiration is invalid")
    if _parse_timestamp(expires, "expires_at") - _parse_timestamp(
        created, "created_at"
    ) > timedelta(seconds=MAX_TTL_SECONDS):
        raise FailClosedRuntimeError("Envelope expiration exceeds TTL bound")
    expected_conversation = _conversation_identity(
        workspace_identity_hash=workspace_hash,
        session_identity_hash=session_hash,
        created_at=created,
    )
    if candidate["conversation_identity"] != expected_conversation:
        raise FailClosedRuntimeError("Envelope conversation identity is invalid")
    origin = _closed_value(
        candidate["origin_interface_identity"],
        INTERFACE_IDENTITIES,
        "origin_interface_identity",
    )
    current = _closed_value(
        candidate["current_interface_identity"],
        INTERFACE_IDENTITIES,
        "current_interface_identity",
    )
    if origin != current:
        raise FailClosedRuntimeError("interface rebind is not implemented in V2 foundation")
    participants = _bounded_objects(
        candidate["participants"],
        MAX_PARTICIPANTS,
        _validate_participant,
        "participants",
    )
    participants = sorted(
        participants,
        key=lambda item: (item["participant_role"], item["asserted_identity"]),
    )
    if any(
        item["first_bound_revision"] > revision
        or item["last_confirmed_revision"] > revision
        for item in participants
    ):
        raise FailClosedRuntimeError("participant revision exceeds global revision")
    if candidate["participants"] != participants:
        raise FailClosedRuntimeError("Envelope participants are not canonical")
    participant_keys = {
        (item["participant_role"], item["asserted_identity"])
        for item in participants
    }
    if len(participant_keys) != len(participants):
        raise FailClosedRuntimeError("Envelope participants contain duplicates")
    context = _closed_object(
        candidate["context_scope"], _CONTEXT_SCOPE_FIELDS, "context scope"
    )
    if context != {
        "workspace_identity_hash": workspace_hash,
        "session_identity_hash": session_hash,
        "current_interface_identity": current,
        "scope_revision": 0,
        "scope_status": BOUND,
    }:
        raise FailClosedRuntimeError("Envelope context scope is invalid")
    if candidate["availability_state"] != ACTIVE:
        raise FailClosedRuntimeError("Envelope state machine is not implemented")
    if candidate["conversation_phase"] != COLLECTING:
        raise FailClosedRuntimeError("conversation state machine is not implemented")
    if candidate["active_objective_candidate_binding"] is not None:
        raise FailClosedRuntimeError("Objective candidate binding is not implemented")
    for field in ("suspended_at", "restored_at", "closed_at"):
        if candidate[field] is not None:
            raise FailClosedRuntimeError("Envelope lifecycle transitions are not implemented")
    binding = _closed_object(
        candidate["semantic_memory_binding"],
        _SEMANTIC_BINDING_FIELDS,
        "semantic memory binding",
    )
    if binding != {
        "semantic_memory_type": PLATFORM_CORE_SEMANTIC_CWM_SCHEMA_V2,
        "global_revision": revision,
        "semantic_revision": semantic_revision,
        "semantic_memory_digest": _checksum(semantic_memory),
    }:
        raise FailClosedRuntimeError("Envelope semantic memory binding is invalid")
    candidate["participants"] = participants
    candidate["context_scope"] = context
    candidate["semantic_memory_binding"] = binding
    return candidate


def _validate_v2_replacement(
    current: dict[str, Any], candidate: dict[str, Any], observed_at: str
) -> None:
    if current["migration_metadata"]["migration_status"] != NATIVE_V2:
        raise FailClosedRuntimeError(
            "legacy semantic review is reserved for a future runtime"
        )
    if candidate["revision"] != current["revision"] + 1:
        raise FailClosedRuntimeError("V2 replacement revision must increment exactly once")
    for field in (
        "working_memory_type",
        "runtime_version",
        "schema_version",
        "runtime_owner",
        "migration_metadata",
        *_BOUNDARY_FIELDS,
    ):
        if candidate[field] != current[field]:
            raise FailClosedRuntimeError("V2 replacement changes immutable fields")
    for field in (
        "conversation_identity",
        "workspace_identity",
        "workspace_identity_hash",
        "session_identity",
        "session_identity_hash",
        "origin_interface_identity",
        "created_at",
    ):
        if candidate["envelope"][field] != current["envelope"][field]:
            raise FailClosedRuntimeError("V2 replacement changes Envelope identity")
    if candidate["envelope"]["updated_at"] != observed_at:
        raise FailClosedRuntimeError("V2 replacement updated_at must equal observed_at")
    if candidate["envelope_revision"] != current["envelope_revision"] + 1:
        raise FailClosedRuntimeError(
            "Envelope revision transition is invalid"
        )
    if candidate["semantic_revision"] not in {
        current["semantic_revision"],
        current["semantic_revision"] + 1,
    }:
        raise FailClosedRuntimeError("semantic revision transition is invalid")
    if _envelope_owned_projection(candidate) != _envelope_owned_projection(
        current
    ):
        raise FailClosedRuntimeError(
            "Envelope mutation is reserved for the future state machine"
        )
    semantics_changed = candidate["semantic_memory"] != current["semantic_memory"]
    if semantics_changed != (
        candidate["semantic_revision"] == current["semantic_revision"] + 1
    ):
        raise FailClosedRuntimeError("semantic revision does not match its change")
    if not semantics_changed:
        raise FailClosedRuntimeError("V2 foundation replacement requires a semantic change")
    _validate_slot_revision_transitions(current, candidate)


def _validate_slot_revision_transitions(
    current: dict[str, Any], candidate: dict[str, Any]
) -> None:
    current_slots = {
        item["slot_id"]: item
        for item in current["semantic_memory"]["semantic_slots"]
    }
    candidate_slots = {
        item["slot_id"]: item
        for item in candidate["semantic_memory"]["semantic_slots"]
    }
    if set(current_slots).difference(candidate_slots):
        raise FailClosedRuntimeError(
            "semantic slots cannot be deleted by the V2 foundation"
        )
    for slot_id, slot in candidate_slots.items():
        prior = current_slots.get(slot_id)
        if prior is None:
            if slot["slot_revision"] != 0:
                raise FailClosedRuntimeError("new semantic slot revision is invalid")
            continue
        changed = slot != prior
        expected = prior["slot_revision"] + (1 if changed else 0)
        if slot["slot_revision"] != expected:
            raise FailClosedRuntimeError("semantic slot revision transition is invalid")


def _migrate_v1_document(source: dict[str, Any], migrated_at: str) -> dict[str, Any]:
    workspace = source["workspace_identity"]
    session = source["session_identity"]
    conversation = _conversation_identity(
        workspace_identity_hash=source["workspace_identity_hash"],
        session_identity_hash=source["session_identity_hash"],
        created_at=source["created_at"],
    )
    legacy_import = {
        "topic": deepcopy(source["topic"]),
        "entities": deepcopy(source["entities"]),
        "inferred_intent": deepcopy(source["inferred_intent"]),
        "confirmed_facts": deepcopy(source["confirmed_facts"]),
        "assumptions": deepcopy(source["assumptions"]),
        "unresolved_ambiguity": deepcopy(source["unresolved_ambiguity"]),
        "confidence": deepcopy(source["confidence"]),
        "discarded_interpretations": deepcopy(source["discarded_interpretations"]),
        "context_references": deepcopy(source["context_references"]),
        "candidate_objective_snapshot": deepcopy(
            source["candidate_objective_snapshot"]
        ),
        "candidate_digest": deepcopy(source["candidate_digest"]),
        "source_lifecycle_state": source["lifecycle_state"],
    }
    semantic_memory = _semantic_memory(
        conversation_identity=conversation,
        semantic_slots=(),
        legacy_import=legacy_import,
    )
    migration = {
        "migration_type": PLATFORM_CORE_CWM_V1_TO_V2_MIGRATION_V1,
        "migration_status": LEGACY_REVIEW_REQUIRED,
        "source_schema_version": PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_SCHEMA_V1,
        "source_runtime_version": PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_RUNTIME_V1,
        "source_revision": source["revision"],
        "migrated_at": migrated_at,
        "review_disposition": LEGACY_REVIEW_REQUIRED,
        "participant_binding_status": PARTICIPANT_BINDING_REQUIRED,
    }
    return _compose_state(
        workspace=workspace,
        session=session,
        conversation=conversation,
        origin_interface=UNBOUND_MIGRATION,
        participants=(),
        semantic_memory=semantic_memory,
        revision=source["revision"] + 1,
        envelope_revision=0,
        semantic_revision=0,
        created_at=source["created_at"],
        updated_at=source["updated_at"],
        expires_at=source["expires_at"],
        migration_metadata=migration,
    )


def _native_migration_metadata() -> dict[str, Any]:
    return {
        "migration_type": None,
        "migration_status": NATIVE_V2,
        "source_schema_version": None,
        "source_runtime_version": None,
        "source_revision": None,
        "migrated_at": None,
        "review_disposition": NOT_REQUIRED,
        "participant_binding_status": NOT_REQUIRED,
    }


def _validate_migration_metadata(
    value: Any, *, semantic_memory: dict[str, Any]
) -> dict[str, Any]:
    candidate = _closed_object(value, _MIGRATION_FIELDS, "migration metadata")
    if candidate["migration_status"] == NATIVE_V2:
        if candidate != _native_migration_metadata():
            raise FailClosedRuntimeError("native V2 migration metadata is invalid")
        if semantic_memory["legacy_import"] is not None:
            raise FailClosedRuntimeError("native V2 state cannot contain legacy import")
        return candidate
    expected_fixed = {
        "migration_type": PLATFORM_CORE_CWM_V1_TO_V2_MIGRATION_V1,
        "migration_status": LEGACY_REVIEW_REQUIRED,
        "source_schema_version": PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_SCHEMA_V1,
        "source_runtime_version": PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_RUNTIME_V1,
        "review_disposition": LEGACY_REVIEW_REQUIRED,
        "participant_binding_status": PARTICIPANT_BINDING_REQUIRED,
    }
    for field, expected in expected_fixed.items():
        if candidate[field] != expected:
            raise FailClosedRuntimeError("V1 migration metadata is invalid")
    _nonnegative_integer(candidate["source_revision"], "source_revision")
    migrated = _canonical_timestamp(candidate["migrated_at"], "migrated_at")
    if candidate["migrated_at"] != migrated:
        raise FailClosedRuntimeError("migration timestamp is not canonical")
    if semantic_memory["legacy_import"] is None:
        raise FailClosedRuntimeError("V1 migration requires legacy import")
    return candidate


def _validate_cross_component_bindings(
    *,
    revision: int,
    semantic_revision: int,
    envelope: dict[str, Any],
    semantic_memory: dict[str, Any],
    migration: dict[str, Any],
) -> None:
    created = _parse_timestamp(envelope["created_at"], "created_at")
    updated = _parse_timestamp(envelope["updated_at"], "updated_at")
    for slot in semantic_memory["semantic_slots"]:
        if slot["slot_revision"] > semantic_revision:
            raise FailClosedRuntimeError(
                "semantic slot revision exceeds semantic revision"
            )
        if any(
            entry["source_revision"] > revision
            for entry in slot["provenance"]
        ):
            raise FailClosedRuntimeError(
                "slot provenance revision exceeds global revision"
            )
        for entry in slot["history"]:
            changed = _parse_timestamp(entry["changed_at"], "changed_at")
            if changed < created or changed > updated:
                raise FailClosedRuntimeError(
                    "semantic slot history timestamp is outside Envelope bounds"
                )
    if migration["migration_status"] == NATIVE_V2:
        if envelope["origin_interface_identity"] != LOCAL_CONVERSATION_V2:
            raise FailClosedRuntimeError("native V2 interface binding is invalid")
        return
    if revision < migration["source_revision"] + 1:
        raise FailClosedRuntimeError("migration revision anchor is invalid")
    if envelope["origin_interface_identity"] != UNBOUND_MIGRATION:
        raise FailClosedRuntimeError("migrated V2 interface binding is invalid")
    if envelope["participants"]:
        raise FailClosedRuntimeError(
            "migrated V2 participant binding is not implemented"
        )
    migrated = _parse_timestamp(migration["migrated_at"], "migrated_at")
    if migrated < updated:
        raise FailClosedRuntimeError(
            "migration timestamp precedes source update"
        )


def _validate_legacy_import(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    candidate = _closed_object(value, _LEGACY_IMPORT_FIELDS, "legacy import")
    _reject_forbidden_keys(candidate)
    encoded = _canonical_bytes(candidate)
    if json.loads(encoded.decode("utf-8")) != candidate:
        raise FailClosedRuntimeError("legacy import is not canonical JSON")
    return candidate


def _validate_provenance(value: Any) -> dict[str, Any]:
    candidate = _closed_object(value, _PROVENANCE_FIELDS, "slot provenance")
    _reject_forbidden_keys(candidate)
    _closed_value(candidate["source_kind"], PROVENANCE_SOURCE_KINDS, "source_kind")
    _nonnegative_integer(candidate["turn_number"], "turn_number")
    _nonnegative_integer(candidate["source_revision"], "source_revision")
    source_span = _exact_text(candidate["source_span"], "source_span")
    _require_digest(candidate["content_digest"], "content_digest", "sha256:")
    if candidate["content_digest"] != _checksum(source_span):
        raise FailClosedRuntimeError("slot provenance content digest is invalid")
    rules = candidate["normalization_rule_ids"]
    if not isinstance(rules, list) or len(rules) > MAX_NORMALIZATION_RULE_IDS:
        raise FailClosedRuntimeError("normalization rule ids are invalid")
    normalized_rules = [_bounded_token(item, "normalization rule id") for item in rules]
    if rules != sorted(set(normalized_rules)):
        raise FailClosedRuntimeError("normalization rule ids are not canonical")
    _closed_value(
        candidate["human_disposition"],
        {"NOT_APPLICABLE", "ASSERTED", "CONFIRMED"},
        "human_disposition",
    )
    return candidate


def _validate_history(value: Any) -> dict[str, Any]:
    candidate = _closed_object(value, _HISTORY_FIELDS, "slot history")
    _nonnegative_integer(candidate["slot_revision"], "slot history revision")
    changed = _canonical_timestamp(candidate["changed_at"], "changed_at")
    if candidate["changed_at"] != changed:
        raise FailClosedRuntimeError("slot history timestamp is not canonical")
    _closed_value(
        candidate["change_kind"],
        {"INITIALIZED", "REFINED", "CONFIRMED", "CONFLICTED", "STALE", "WITHDRAWN"},
        "change_kind",
    )
    if candidate["prior_value_digest"] is not None:
        _require_digest(candidate["prior_value_digest"], "prior_value_digest", "sha256:")
    _require_digest(
        candidate["resulting_value_digest"], "resulting_value_digest", "sha256:"
    )
    return candidate


def _validate_participant(value: Any) -> dict[str, Any]:
    candidate = _closed_object(value, _PARTICIPANT_FIELDS, "participant")
    _reject_forbidden_keys(candidate)
    _closed_value(candidate["participant_role"], PARTICIPANT_ROLES, "participant_role")
    _require_identity(candidate["asserted_identity"], "asserted_identity")
    _closed_value(candidate["identity_source"], PARTICIPANT_IDENTITY_SOURCES, "identity_source")
    if candidate["binding_disposition"] != ASSERTED_NOT_AUTHENTICATED:
        raise FailClosedRuntimeError("participant authentication is not implemented")
    first = _nonnegative_integer(candidate["first_bound_revision"], "first_bound_revision")
    last = _nonnegative_integer(candidate["last_confirmed_revision"], "last_confirmed_revision")
    if last < first:
        raise FailClosedRuntimeError("participant revision binding is invalid")
    return candidate


def _closed_object(value: Any, fields: frozenset[str], name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"{name} must be an object")
    candidate = deepcopy(value)
    if set(candidate) != fields:
        raise FailClosedRuntimeError(f"{name} schema fields are invalid")
    return candidate


def _bounded_objects(
    value: Any,
    maximum: int,
    validator: Any,
    name: str,
) -> list[dict[str, Any]]:
    if not isinstance(value, list) or len(value) > maximum:
        raise FailClosedRuntimeError(f"{name} exceeds item bound")
    return [validator(item) for item in value]


def _closed_value(value: Any, allowed: Any, field_name: str) -> str:
    if not isinstance(value, str) or value not in allowed:
        raise FailClosedRuntimeError(f"{field_name} is invalid")
    return value


def _slot_role(slot_class: str, value: Any) -> str:
    return _closed_value(value, SLOT_ROLES[slot_class], "slot_role")


def _cardinality_key(slot_class: str, slot_role: str, value: Any) -> str:
    token = _bounded_token(value, "cardinality_key", MAX_CARDINALITY_KEY_CHARACTERS)
    if slot_class in {OPERATIVE_ACTION, OPERATIVE_SUBJECT, WORK_TYPE} and token != PRIMARY:
        raise FailClosedRuntimeError("single-valued slot requires PRIMARY cardinality")
    if slot_class == DESIRED_OUTCOME and slot_role == PRIMARY and token != PRIMARY:
        raise FailClosedRuntimeError("primary outcome requires PRIMARY cardinality")
    return token


def _validate_slot_materiality(
    slot_class: str,
    slot_role: str,
    materiality: str,
) -> None:
    required = slot_class in {
        OPERATIVE_ACTION,
        OPERATIVE_SUBJECT,
        WORK_TYPE,
    } or (slot_class == DESIRED_OUTCOME and slot_role == PRIMARY)
    if required and materiality != REQUIRED:
        raise FailClosedRuntimeError("required semantic slot materiality is invalid")
    if slot_class in {GOVERNING_QUALIFIER, SEMANTIC_REFERENCE} and (
        materiality == REQUIRED
    ):
        raise FailClosedRuntimeError(
            "conditional semantic slot cannot be globally required"
        )


def _validate_semantic_cardinality(slots: list[dict[str, Any]]) -> None:
    single_counts = {
        OPERATIVE_ACTION: 0,
        OPERATIVE_SUBJECT: 0,
        WORK_TYPE: 0,
    }
    primary_outcomes = 0
    for slot in slots:
        if slot["slot_class"] in single_counts:
            single_counts[slot["slot_class"]] += 1
        if (
            slot["slot_class"] == DESIRED_OUTCOME
            and slot["slot_role"] == PRIMARY
        ):
            primary_outcomes += 1
    if any(count > 1 for count in single_counts.values()):
        raise FailClosedRuntimeError("single-valued semantic slot cardinality is invalid")
    if primary_outcomes > 1:
        raise FailClosedRuntimeError("primary outcome cardinality is invalid")


def _canonical_slot_value(slot_class: str, slot_role: str, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError("canonical_value is required")
    if slot_class == WORK_TYPE:
        if value != slot_role or value not in CANONICAL_GOVERNED_WORK_TYPES:
            raise FailClosedRuntimeError("WORK_TYPE canonical value is invalid")
        return value
    if slot_class == SEMANTIC_REFERENCE:
        return _exact_text(value, "canonical_value")
    normalized = " ".join(value.split())
    if value != normalized:
        raise FailClosedRuntimeError("canonical_value is not canonical")
    if len(normalized) > MAX_TEXT_CHARACTERS:
        raise FailClosedRuntimeError("canonical_value exceeds storage bound")
    return normalized


def _exact_text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    if len(value) > MAX_TEXT_CHARACTERS:
        raise FailClosedRuntimeError(f"{field_name} exceeds storage bound")
    return value


def _bounded_token(
    value: Any,
    field_name: str,
    maximum: int = MAX_COLLECTION_ITEM_CHARACTERS,
) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise FailClosedRuntimeError(f"{field_name} is invalid")
    if len(value) > maximum:
        raise FailClosedRuntimeError(f"{field_name} exceeds storage bound")
    return value


def _nonnegative_integer(value: Any, field_name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise FailClosedRuntimeError(f"{field_name} is invalid")
    return value


def _slot_dependencies(value: Any) -> list[str]:
    if not isinstance(value, list) or len(value) > MAX_COLLECTION_ITEMS:
        raise FailClosedRuntimeError("semantic slot dependencies are invalid")
    normalized = [
        _require_local_identity(item, "slot dependency", prefix="conversation-slot-sha256:")
        for item in value
    ]
    if normalized != sorted(set(normalized)):
        raise FailClosedRuntimeError("semantic slot dependencies are not canonical")
    return normalized


def _slot_sort_key(slot: dict[str, Any]) -> tuple[Any, ...]:
    return (
        _CLASS_ORDER[slot["slot_class"]],
        slot["slot_role"],
        slot["cardinality_key"],
        slot["slot_id"],
    )


def _conversation_identity(
    *, workspace_identity_hash: str, session_identity_hash: str, created_at: str
) -> str:
    body = {
        "envelope_schema": PLATFORM_CORE_CONVERSATION_ENVELOPE_SCHEMA_V1,
        "workspace_identity_hash": workspace_identity_hash,
        "session_identity_hash": session_identity_hash,
        "created_at": created_at,
    }
    return "conversation-local-sha256:" + hashlib.sha256(_canonical_bytes(body)).hexdigest()


def _slot_identity(
    conversation_identity: str,
    slot_class: str,
    cardinality_key: str,
) -> str:
    body = {
        "conversation_identity": conversation_identity,
        "slot_class": slot_class,
        "cardinality_key": cardinality_key,
    }
    return "conversation-slot-sha256:" + hashlib.sha256(_canonical_bytes(body)).hexdigest()


def _equivalence_key(slot_class: str, slot_role: str, canonical_value: str) -> str:
    body = {
        "slot_class": slot_class,
        "slot_role": slot_role,
        "canonical_value": canonical_value,
    }
    return "semantic-equivalence-sha256:" + hashlib.sha256(_canonical_bytes(body)).hexdigest()


def _require_local_identity(value: Any, field_name: str, *, prefix: str) -> str:
    if not isinstance(value, str) or not value.startswith(prefix):
        raise FailClosedRuntimeError(f"{field_name} is invalid")
    digest = value.removeprefix(prefix)
    if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
        raise FailClosedRuntimeError(f"{field_name} is invalid")
    return value


def _require_digest(value: Any, field_name: str, prefix: str) -> str:
    if not isinstance(value, str) or not value.startswith(prefix):
        raise FailClosedRuntimeError(f"{field_name} is invalid")
    digest = value.removeprefix(prefix)
    if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
        raise FailClosedRuntimeError(f"{field_name} is invalid")
    return value


def _validate_boundary_fields(value: dict[str, Any], name: str) -> None:
    for field, expected in _BOUNDARY_FIELDS.items():
        if value[field] != expected:
            raise FailClosedRuntimeError(f"{name} authority boundary is invalid")


def _reject_forbidden_keys(value: Any) -> None:
    pending = [value]
    while pending:
        item = pending.pop()
        if isinstance(item, dict):
            if _FORBIDDEN_IDENTITY_FIELDS.intersection(item):
                raise FailClosedRuntimeError("V2 state contains forbidden identity")
            pending.extend(item.values())
        elif isinstance(item, list):
            pending.extend(item)


def _read_json_state(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise FailClosedRuntimeError("conversation working memory state path is unsafe")
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise FailClosedRuntimeError("conversation working memory state is unreadable") from exc
    if len(raw) > MAX_STATE_BYTES:
        raise FailClosedRuntimeError("conversation working memory state exceeds storage bound")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FailClosedRuntimeError("conversation working memory state is corrupt") from exc
    if not isinstance(value, dict):
        raise FailClosedRuntimeError("conversation working memory state must be an object")
    return value


def _is_v2_expired(state: dict[str, Any], observed_at: str) -> bool:
    return _parse_timestamp(observed_at, "observed_at") >= _parse_timestamp(
        state["envelope"]["expires_at"], "expires_at"
    )


def _reject_v2_expired(state: dict[str, Any], observed_at: str) -> None:
    if _is_v2_expired(state, observed_at):
        raise FailClosedRuntimeError("conversation working memory state is expired")


def _envelope_owned_projection(state: dict[str, Any]) -> dict[str, Any]:
    envelope = deepcopy(state["envelope"])
    envelope.pop("semantic_memory_binding", None)
    envelope.pop("updated_at", None)
    return envelope


__all__ = [
    "ACCEPTANCE",
    "ACTIVE",
    "ASSERTED",
    "ASSERTED_NOT_AUTHENTICATED",
    "BOUND",
    "CAPABILITY_HINT",
    "COLLECTING",
    "COMPLETE",
    "CONDITIONAL",
    "CONFIRMED",
    "DETERMINISTIC_NORMALIZATION",
    "DESIRED_OUTCOME",
    "EVIDENCE",
    "GOVERNING_QUALIFIER",
    "HUMAN_ASSERTED",
    "HUMAN_CONFIRMED",
    "HUMAN_ORIGINATOR",
    "HUMAN_TURN",
    "LOCAL_ASSERTION",
    "LOCAL_CONVERSATION_V2",
    "OPERATIVE_ACTION",
    "OPERATIVE_SUBJECT",
    "OUTPUT",
    "PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_RUNTIME_V2",
    "PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_SCHEMA_V2",
    "PLATFORM_CORE_SEMANTIC_CWM_SCHEMA_V2",
    "PRESERVATION",
    "PRIMARY",
    "PROPOSED",
    "REQUIRED",
    "RUNTIME_DECLARATION",
    "SCOPE",
    "SECONDARY",
    "SEMANTIC_REFERENCE",
    "SEMANTIC_SLOT_CLASSES",
    "WORK_TYPE",
    "conversation_working_memory_conversation_identity_v2",
    "create_conversation_working_memory_state_v2",
    "create_semantic_cwm_slot_v2",
    "load_conversation_working_memory_state_v2",
    "migrate_conversation_working_memory_state_v1_to_v2",
    "recover_conversation_working_memory_state_v2",
    "replace_conversation_working_memory_state_v2_atomically",
    "validate_conversation_working_memory_state_v2",
    "validate_semantic_cwm_slot_v2",
]
