"""Isolated mutable Conversation Working Memory for Platform Core.

This runtime stores provisional conversation understanding only.  It creates
no constitutional artifact, Replay identity, Objective, capability route,
authorization, or Worker request.
"""

from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import stat
import tempfile
from typing import Any, Iterator

from aigol.runtime.models import FailClosedRuntimeError


PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_RUNTIME_V1 = (
    "PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_RUNTIME_V1"
)
PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_SCHEMA_V1 = (
    "PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_SCHEMA_V1"
)
PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_OWNER = (
    "PLATFORM_CORE_HUMAN_INTENT_CONVERSATION"
)

ABSENT = "ABSENT"
EXPLORING = "EXPLORING"
CANDIDATE_READY = "CANDIDATE_READY"
COMMITTING = "COMMITTING"
COMMITTED = "COMMITTED"

STORED_LIFECYCLE_STATES = frozenset(
    {EXPLORING, CANDIDATE_READY, COMMITTING, COMMITTED}
)
MUTABLE_LIFECYCLE_STATES = frozenset({EXPLORING, CANDIDATE_READY})

DEFAULT_TTL_SECONDS = 86_400
MAX_TTL_SECONDS = 2_592_000
MAX_STATE_BYTES = 65_536
MAX_CANDIDATE_BYTES = 16_384
MAX_COLLECTION_ITEMS = 64
MAX_COLLECTION_ITEM_CHARACTERS = 512
MAX_TEXT_CHARACTERS = 4_096

_STATE_FILENAME = "state.json"
_LOCK_FILENAME = ".cwm.lock"
_WORKING_ROOT = ".platform-core-working"
_CONVERSATION_ROOT = "conversation"
_INTEGRITY_ALGORITHM = "SHA256_CANONICAL_JSON"
_UNSET = object()

_BOUNDARY_FIELDS = {
    "runtime_owner": PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_OWNER,
    "constitutional_artifact": False,
    "constitutional_authority": False,
    "replay_visible": False,
    "authorization_eligible": False,
    "worker_eligible": False,
    "objective_creation_supported": False,
    "capability_routing_supported": False,
}

_COLLECTION_FIELDS = (
    "entities",
    "confirmed_facts",
    "assumptions",
    "unresolved_ambiguity",
    "discarded_interpretations",
    "context_references",
)

_STATE_FIELDS = frozenset(
    {
        "working_memory_type",
        "runtime_version",
        "schema_version",
        "runtime_owner",
        "workspace_identity",
        "workspace_identity_hash",
        "session_identity",
        "session_identity_hash",
        "revision",
        "lifecycle_state",
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
        "created_at",
        "updated_at",
        "expires_at",
        "commitment_metadata",
        "constitutional_artifact",
        "constitutional_authority",
        "replay_visible",
        "authorization_eligible",
        "worker_eligible",
        "objective_creation_supported",
        "capability_routing_supported",
        "integrity_algorithm",
        "integrity_checksum",
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


def create_conversation_working_memory_state(
    *,
    runtime_root: str | Path,
    workspace_identity: str | Path,
    session_identity: str,
    created_at: str,
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
    topic: str | None = None,
    entities: list[str] | tuple[str, ...] = (),
    inferred_intent: str | None = None,
    confirmed_facts: list[str] | tuple[str, ...] = (),
    assumptions: list[str] | tuple[str, ...] = (),
    unresolved_ambiguity: list[str] | tuple[str, ...] = (),
    confidence: float | int | None = None,
    discarded_interpretations: list[str] | tuple[str, ...] = (),
    context_references: list[str] | tuple[str, ...] = (),
    candidate_objective_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create revision zero and fail closed if the session already exists."""

    workspace = _normalize_workspace_identity(workspace_identity)
    session = _require_identity(session_identity, "session_identity")
    created = _canonical_timestamp(created_at, "created_at")
    expires = _expiration_timestamp(created, ttl_seconds)
    state = {
        "working_memory_type": (
            PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_SCHEMA_V1
        ),
        "runtime_version": (
            PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_RUNTIME_V1
        ),
        "schema_version": (
            PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_SCHEMA_V1
        ),
        "workspace_identity": workspace,
        "workspace_identity_hash": _identity_hash(workspace),
        "session_identity": session,
        "session_identity_hash": _identity_hash(session),
        "revision": 0,
        "lifecycle_state": EXPLORING,
        "topic": _optional_text(topic, "topic"),
        "entities": _string_collection(entities, "entities"),
        "inferred_intent": _optional_text(
            inferred_intent, "inferred_intent"
        ),
        "confirmed_facts": _string_collection(
            confirmed_facts, "confirmed_facts"
        ),
        "assumptions": _string_collection(assumptions, "assumptions"),
        "unresolved_ambiguity": _string_collection(
            unresolved_ambiguity, "unresolved_ambiguity"
        ),
        "confidence": _confidence(confidence),
        "discarded_interpretations": _string_collection(
            discarded_interpretations, "discarded_interpretations"
        ),
        "context_references": _string_collection(
            context_references, "context_references"
        ),
        "candidate_objective_snapshot": _candidate_snapshot(
            candidate_objective_snapshot
        ),
        "candidate_digest": _candidate_digest(
            candidate_objective_snapshot
        ),
        "created_at": created,
        "updated_at": created,
        "expires_at": expires,
        "commitment_metadata": _empty_commitment_metadata(),
        **_BOUNDARY_FIELDS,
        "integrity_algorithm": _INTEGRITY_ALGORITHM,
    }
    state = _with_integrity(state)
    validated = validate_conversation_working_memory_state(
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


def load_conversation_working_memory_state(
    *,
    runtime_root: str | Path,
    workspace_identity: str | Path,
    session_identity: str,
    observed_at: str,
) -> dict[str, Any] | None:
    """Load current mutable state, returning None only when it is absent."""

    workspace = _normalize_workspace_identity(workspace_identity)
    session = _require_identity(session_identity, "session_identity")
    observed = _canonical_timestamp(observed_at, "observed_at")
    root = _conversation_root(runtime_root)
    with _store_lock(root):
        path = _state_path(root, workspace, session)
        if not path.exists():
            return None
        state = _read_and_validate_state(
            path,
            expected_workspace_identity=workspace,
            expected_session_identity=session,
        )
        _reject_expired(state, observed)
        return deepcopy(state)


def recover_conversation_working_memory_state(
    *,
    runtime_root: str | Path,
    workspace_identity: str | Path,
    session_identity: str,
    observed_at: str,
) -> dict[str, Any] | None:
    """Restore after restart, cleaning an expired state deterministically."""

    workspace = _normalize_workspace_identity(workspace_identity)
    session = _require_identity(session_identity, "session_identity")
    observed = _canonical_timestamp(observed_at, "observed_at")
    root = _conversation_root(runtime_root)
    with _store_lock(root):
        path = _state_path(root, workspace, session)
        if not path.exists():
            return None
        state = _read_and_validate_state(
            path,
            expected_workspace_identity=workspace,
            expected_session_identity=session,
        )
        if _is_expired(state, observed):
            _remove_state(path, root)
            return None
        return deepcopy(state)


def update_conversation_working_memory_state(
    *,
    runtime_root: str | Path,
    workspace_identity: str | Path,
    session_identity: str,
    expected_revision: int,
    updated_at: str,
    lifecycle_state: str | object = _UNSET,
    ttl_seconds: int | None = None,
    topic: str | None | object = _UNSET,
    entities: list[str] | tuple[str, ...] | object = _UNSET,
    inferred_intent: str | None | object = _UNSET,
    confirmed_facts: list[str] | tuple[str, ...] | object = _UNSET,
    assumptions: list[str] | tuple[str, ...] | object = _UNSET,
    unresolved_ambiguity: list[str] | tuple[str, ...] | object = _UNSET,
    confidence: float | int | None | object = _UNSET,
    discarded_interpretations: (
        list[str] | tuple[str, ...] | object
    ) = _UNSET,
    context_references: list[str] | tuple[str, ...] | object = _UNSET,
    candidate_objective_snapshot: dict[str, Any] | None | object = _UNSET,
) -> dict[str, Any]:
    """Apply one bounded update using optimistic revision control."""

    workspace = _normalize_workspace_identity(workspace_identity)
    session = _require_identity(session_identity, "session_identity")
    updated = _canonical_timestamp(updated_at, "updated_at")
    root = _conversation_root(runtime_root)
    with _store_lock(root):
        path = _state_path(root, workspace, session)
        if not path.exists():
            raise FailClosedRuntimeError(
                "conversation working memory state is absent"
            )
        current = _read_and_validate_state(
            path,
            expected_workspace_identity=workspace,
            expected_session_identity=session,
        )
        _reject_expired(current, updated)
        _require_expected_revision(current, expected_revision)
        replacement = deepcopy(current)
        replacement["revision"] = expected_revision + 1
        replacement["updated_at"] = updated
        if ttl_seconds is not None:
            replacement["expires_at"] = _expiration_timestamp(
                updated, ttl_seconds
            )
        updates = {
            "topic": topic,
            "entities": entities,
            "inferred_intent": inferred_intent,
            "confirmed_facts": confirmed_facts,
            "assumptions": assumptions,
            "unresolved_ambiguity": unresolved_ambiguity,
            "confidence": confidence,
            "discarded_interpretations": discarded_interpretations,
            "context_references": context_references,
            "candidate_objective_snapshot": (
                candidate_objective_snapshot
            ),
        }
        _apply_mutable_fields(replacement, updates)
        if candidate_objective_snapshot is not _UNSET:
            replacement["candidate_digest"] = _candidate_digest(
                replacement["candidate_objective_snapshot"]
            )
        next_lifecycle = (
            replacement["lifecycle_state"]
            if lifecycle_state is _UNSET
            else _mutable_lifecycle(lifecycle_state)
        )
        _validate_lifecycle_transition(
            current["lifecycle_state"], next_lifecycle
        )
        replacement["lifecycle_state"] = next_lifecycle
        replacement = _with_integrity(replacement)
        validated = validate_conversation_working_memory_state(
            replacement,
            expected_workspace_identity=workspace,
            expected_session_identity=session,
        )
        _write_state_atomically(path, validated)
        return deepcopy(validated)


def replace_conversation_working_memory_state_atomically(
    *,
    runtime_root: str | Path,
    workspace_identity: str | Path,
    session_identity: str,
    expected_revision: int,
    replacement_state: dict[str, Any],
    observed_at: str,
) -> dict[str, Any]:
    """Replace a caller-prepared next revision after full invariant checks."""

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
        current = _read_and_validate_state(
            path,
            expected_workspace_identity=workspace,
            expected_session_identity=session,
        )
        _reject_expired(current, observed)
        _require_expected_revision(current, expected_revision)
        candidate = validate_conversation_working_memory_state(
            replacement_state,
            expected_workspace_identity=workspace,
            expected_session_identity=session,
        )
        if candidate["revision"] != expected_revision + 1:
            raise FailClosedRuntimeError(
                "replacement revision must increment exactly once"
            )
        for field in (
            "working_memory_type",
            "runtime_version",
            "schema_version",
            "runtime_owner",
            "workspace_identity",
            "workspace_identity_hash",
            "session_identity",
            "session_identity_hash",
            "created_at",
            "commitment_metadata",
            *_BOUNDARY_FIELDS,
        ):
            if candidate.get(field) != current.get(field):
                raise FailClosedRuntimeError(
                    "replacement changes immutable working-memory fields"
                )
        if candidate["updated_at"] != observed:
            raise FailClosedRuntimeError(
                "replacement updated_at must equal observed_at"
            )
        if _parse_timestamp(
            candidate["updated_at"], "updated_at"
        ) < _parse_timestamp(current["updated_at"], "current updated_at"):
            raise FailClosedRuntimeError(
                "replacement updated_at precedes current state"
            )
        _validate_lifecycle_transition(
            current["lifecycle_state"], candidate["lifecycle_state"]
        )
        _write_state_atomically(path, candidate)
        return deepcopy(candidate)


def cleanup_conversation_working_memory_state(
    *,
    runtime_root: str | Path,
    workspace_identity: str | Path,
    session_identity: str,
    expected_revision: int | None = None,
) -> bool:
    """Remove validated mutable state without producing lifecycle evidence."""

    workspace = _normalize_workspace_identity(workspace_identity)
    session = _require_identity(session_identity, "session_identity")
    root = _conversation_root(runtime_root)
    with _store_lock(root):
        path = _state_path(root, workspace, session)
        if not path.exists():
            return False
        state = _read_and_validate_state(
            path,
            expected_workspace_identity=workspace,
            expected_session_identity=session,
        )
        if expected_revision is not None:
            _require_expected_revision(state, expected_revision)
        _remove_state(path, root)
        return True


def validate_conversation_working_memory_state(
    state: dict[str, Any],
    *,
    expected_workspace_identity: str | Path | None = None,
    expected_session_identity: str | None = None,
) -> dict[str, Any]:
    """Fail closed unless state is bounded, isolated, and non-authoritative."""

    if not isinstance(state, dict):
        raise FailClosedRuntimeError(
            "conversation working memory state must be an object"
        )
    candidate = deepcopy(state)
    unexpected = set(candidate).difference(_STATE_FIELDS)
    missing = _STATE_FIELDS.difference(candidate)
    if unexpected or missing:
        raise FailClosedRuntimeError(
            "conversation working memory schema fields are invalid"
        )
    if _FORBIDDEN_IDENTITY_FIELDS.intersection(candidate):
        raise FailClosedRuntimeError(
            "conversation working memory contains forbidden identity"
        )
    if candidate.get("working_memory_type") != (
        PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_SCHEMA_V1
    ):
        raise FailClosedRuntimeError(
            "conversation working memory type is invalid"
        )
    if candidate.get("runtime_version") != (
        PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_RUNTIME_V1
    ):
        raise FailClosedRuntimeError(
            "conversation working memory runtime version is invalid"
        )
    if candidate.get("schema_version") != (
        PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_SCHEMA_V1
    ):
        raise FailClosedRuntimeError(
            "conversation working memory schema version is invalid"
        )
    for field, expected in _BOUNDARY_FIELDS.items():
        if candidate.get(field) is not expected and candidate.get(field) != expected:
            raise FailClosedRuntimeError(
                "conversation working memory authority boundary is invalid"
            )
    workspace = _normalize_workspace_identity(
        candidate.get("workspace_identity")
    )
    session = _require_identity(
        candidate.get("session_identity"), "session_identity"
    )
    if candidate.get("workspace_identity") != workspace:
        raise FailClosedRuntimeError(
            "conversation working memory workspace identity is not canonical"
        )
    if candidate.get("workspace_identity_hash") != _identity_hash(workspace):
        raise FailClosedRuntimeError(
            "conversation working memory workspace identity mismatch"
        )
    if candidate.get("session_identity_hash") != _identity_hash(session):
        raise FailClosedRuntimeError(
            "conversation working memory session identity mismatch"
        )
    if expected_workspace_identity is not None and workspace != (
        _normalize_workspace_identity(expected_workspace_identity)
    ):
        raise FailClosedRuntimeError(
            "conversation working memory workspace mismatch"
        )
    if expected_session_identity is not None and session != (
        _require_identity(expected_session_identity, "expected_session_identity")
    ):
        raise FailClosedRuntimeError(
            "conversation working memory session mismatch"
        )
    revision = candidate.get("revision")
    if (
        not isinstance(revision, int)
        or isinstance(revision, bool)
        or revision < 0
    ):
        raise FailClosedRuntimeError(
            "conversation working memory revision is invalid"
        )
    lifecycle = candidate.get("lifecycle_state")
    if lifecycle not in STORED_LIFECYCLE_STATES:
        raise FailClosedRuntimeError(
            "conversation working memory lifecycle state is invalid"
        )
    candidate["topic"] = _optional_text(candidate.get("topic"), "topic")
    candidate["inferred_intent"] = _optional_text(
        candidate.get("inferred_intent"), "inferred_intent"
    )
    for field in _COLLECTION_FIELDS:
        normalized = _string_collection(candidate.get(field), field)
        if candidate.get(field) != normalized:
            raise FailClosedRuntimeError(
                f"conversation working memory {field} is not canonical"
            )
    candidate["confidence"] = _confidence(candidate.get("confidence"))
    snapshot = _candidate_snapshot(
        candidate.get("candidate_objective_snapshot")
    )
    if candidate.get("candidate_objective_snapshot") != snapshot:
        raise FailClosedRuntimeError(
            "conversation working memory candidate snapshot is not canonical"
        )
    if candidate.get("candidate_digest") != _candidate_digest(snapshot):
        raise FailClosedRuntimeError(
            "conversation working memory candidate digest mismatch"
        )
    if lifecycle == CANDIDATE_READY and not snapshot:
        raise FailClosedRuntimeError(
            "candidate-ready working memory requires an Objective snapshot"
        )
    if candidate.get("commitment_metadata") != _empty_commitment_metadata():
        raise FailClosedRuntimeError(
            "conversation working memory commitment placeholder is invalid"
        )
    created = _parse_timestamp(candidate.get("created_at"), "created_at")
    updated = _parse_timestamp(candidate.get("updated_at"), "updated_at")
    expires = _parse_timestamp(candidate.get("expires_at"), "expires_at")
    if updated < created:
        raise FailClosedRuntimeError(
            "conversation working memory updated_at precedes created_at"
        )
    if expires <= updated:
        raise FailClosedRuntimeError(
            "conversation working memory expiration is invalid"
        )
    if expires - created > timedelta(seconds=MAX_TTL_SECONDS):
        raise FailClosedRuntimeError(
            "conversation working memory expiration exceeds TTL bound"
        )
    if candidate.get("integrity_algorithm") != _INTEGRITY_ALGORITHM:
        raise FailClosedRuntimeError(
            "conversation working memory integrity algorithm is invalid"
        )
    supplied_integrity = candidate.get("integrity_checksum")
    body = deepcopy(candidate)
    body.pop("integrity_checksum", None)
    if supplied_integrity != _checksum(body):
        raise FailClosedRuntimeError(
            "conversation working memory integrity mismatch"
        )
    if len(_canonical_bytes(candidate)) > MAX_STATE_BYTES:
        raise FailClosedRuntimeError(
            "conversation working memory state exceeds storage bound"
        )
    return candidate


def conversation_working_memory_state_path(
    *,
    runtime_root: str | Path,
    workspace_identity: str | Path,
    session_identity: str,
) -> Path:
    """Return the path-safe mutable state location."""

    workspace = _normalize_workspace_identity(workspace_identity)
    session = _require_identity(session_identity, "session_identity")
    return _state_path(_conversation_root(runtime_root), workspace, session)


def _apply_mutable_fields(
    replacement: dict[str, Any], updates: dict[str, Any]
) -> None:
    for field, value in updates.items():
        if value is _UNSET:
            continue
        if field in {"topic", "inferred_intent"}:
            replacement[field] = _optional_text(value, field)
        elif field in _COLLECTION_FIELDS:
            replacement[field] = _string_collection(value, field)
        elif field == "confidence":
            replacement[field] = _confidence(value)
        elif field == "candidate_objective_snapshot":
            replacement[field] = _candidate_snapshot(value)
        else:  # pragma: no cover - the map above is closed by construction.
            raise FailClosedRuntimeError(
                "unsupported conversation working memory update"
            )


def _mutable_lifecycle(value: Any) -> str:
    if value not in MUTABLE_LIFECYCLE_STATES:
        raise FailClosedRuntimeError(
            "commit lifecycle is reserved for a future commitment runtime"
        )
    return str(value)


def _validate_lifecycle_transition(current: str, next_state: str) -> None:
    if current not in MUTABLE_LIFECYCLE_STATES:
        raise FailClosedRuntimeError(
            "committing and committed working memory are not mutable"
        )
    if next_state not in MUTABLE_LIFECYCLE_STATES:
        raise FailClosedRuntimeError(
            "commit lifecycle is reserved for a future commitment runtime"
        )
    if current == EXPLORING and next_state not in {
        EXPLORING,
        CANDIDATE_READY,
    }:
        raise FailClosedRuntimeError(
            "conversation working memory lifecycle transition is invalid"
        )
    if current == CANDIDATE_READY and next_state not in {
        EXPLORING,
        CANDIDATE_READY,
    }:
        raise FailClosedRuntimeError(
            "conversation working memory lifecycle transition is invalid"
        )


def _require_expected_revision(
    state: dict[str, Any], expected_revision: int
) -> None:
    if (
        not isinstance(expected_revision, int)
        or isinstance(expected_revision, bool)
        or expected_revision < 0
        or state.get("revision") != expected_revision
    ):
        raise FailClosedRuntimeError(
            "conversation working memory revision is stale"
        )


def _read_and_validate_state(
    path: Path,
    *,
    expected_workspace_identity: str,
    expected_session_identity: str,
) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise FailClosedRuntimeError(
            "conversation working memory state path is unsafe"
        )
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise FailClosedRuntimeError(
            "conversation working memory state is unreadable"
        ) from exc
    if len(raw) > MAX_STATE_BYTES:
        raise FailClosedRuntimeError(
            "conversation working memory state exceeds storage bound"
        )
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FailClosedRuntimeError(
            "conversation working memory state is corrupt"
        ) from exc
    return validate_conversation_working_memory_state(
        value,
        expected_workspace_identity=expected_workspace_identity,
        expected_session_identity=expected_session_identity,
    )


def _write_state_atomically(path: Path, state: dict[str, Any]) -> None:
    data = _canonical_bytes(state) + b"\n"
    if len(data) > MAX_STATE_BYTES:
        raise FailClosedRuntimeError(
            "conversation working memory state exceeds storage bound"
        )
    _secure_directory(path.parent.parent)
    _secure_directory(path.parent)
    descriptor = -1
    temporary_name: str | None = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=".state.",
            suffix=".tmp",
            dir=path.parent,
        )
        os.fchmod(descriptor, stat.S_IRUSR | stat.S_IWUSR)
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            descriptor = -1
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
        temporary_name = None
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
        _fsync_directory(path.parent)
    except OSError as exc:
        raise FailClosedRuntimeError(
            "conversation working memory atomic write failed"
        ) from exc
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if temporary_name is not None:
            try:
                Path(temporary_name).unlink()
            except FileNotFoundError:
                pass


def _remove_state(path: Path, root: Path) -> None:
    try:
        path.unlink()
        _fsync_directory(path.parent)
    except OSError as exc:
        raise FailClosedRuntimeError(
            "conversation working memory cleanup failed"
        ) from exc
    current = path.parent
    while current != root and root in current.parents:
        try:
            current.rmdir()
        except OSError:
            break
        current = current.parent


@contextmanager
def _store_lock(root: Path) -> Iterator[None]:
    _secure_directory(root)
    lock_path = root / _LOCK_FILENAME
    flags = os.O_CREAT | os.O_RDWR
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(
            lock_path,
            flags,
            stat.S_IRUSR | stat.S_IWUSR,
        )
        os.fchmod(descriptor, stat.S_IRUSR | stat.S_IWUSR)
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
    except OSError as exc:
        raise FailClosedRuntimeError(
            "conversation working memory lock failed"
        ) from exc
    finally:
        if "descriptor" in locals():
            try:
                fcntl.flock(descriptor, fcntl.LOCK_UN)
            finally:
                os.close(descriptor)


def _conversation_root(runtime_root: str | Path) -> Path:
    try:
        base = Path(runtime_root).expanduser().resolve(strict=False)
    except (OSError, RuntimeError) as exc:
        raise FailClosedRuntimeError(
            "conversation working memory runtime root is invalid"
        ) from exc
    working_root = base / _WORKING_ROOT
    _secure_directory(working_root)
    root = working_root / _CONVERSATION_ROOT
    _secure_directory(root)
    return root


def _state_path(root: Path, workspace: str, session: str) -> Path:
    workspace_key = _identity_hash(workspace).removeprefix("sha256:")
    session_key = _identity_hash(session).removeprefix("sha256:")
    return root / workspace_key / session_key / _STATE_FILENAME


def _secure_directory(path: Path) -> None:
    try:
        path.mkdir(mode=0o700, parents=True, exist_ok=True)
        if path.is_symlink() or not path.is_dir():
            raise FailClosedRuntimeError(
                "conversation working memory directory is unsafe"
            )
        os.chmod(path, stat.S_IRWXU)
    except OSError as exc:
        raise FailClosedRuntimeError(
            "conversation working memory directory is unavailable"
        ) from exc


def _fsync_directory(path: Path) -> None:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    descriptor = os.open(path, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _with_integrity(state: dict[str, Any]) -> dict[str, Any]:
    candidate = deepcopy(state)
    candidate.pop("integrity_checksum", None)
    candidate["integrity_checksum"] = _checksum(candidate)
    return candidate


def _checksum(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _identity_hash(value: str) -> str:
    return _checksum(value)


def _candidate_digest(snapshot: dict[str, Any] | None) -> str | None:
    return _checksum(snapshot) if snapshot is not None else None


def _canonical_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
    except (RecursionError, TypeError, ValueError) as exc:
        raise FailClosedRuntimeError(
            "conversation working memory value is not JSON serializable"
        ) from exc


def _normalize_workspace_identity(value: str | Path | Any) -> str:
    if not isinstance(value, (str, Path)) or not str(value).strip():
        raise FailClosedRuntimeError("workspace_identity is required")
    try:
        return str(Path(value).expanduser().resolve(strict=False))
    except (OSError, RuntimeError) as exc:
        raise FailClosedRuntimeError(
            "workspace_identity is invalid"
        ) from exc


def _require_identity(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    normalized = value.strip()
    if len(normalized) > MAX_TEXT_CHARACTERS:
        raise FailClosedRuntimeError(f"{field_name} exceeds storage bound")
    return normalized


def _optional_text(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise FailClosedRuntimeError(f"{field_name} must be text or null")
    normalized = " ".join(value.split())
    if not normalized:
        return None
    if len(normalized) > MAX_TEXT_CHARACTERS:
        raise FailClosedRuntimeError(f"{field_name} exceeds storage bound")
    return normalized


def _string_collection(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, (list, tuple)):
        raise FailClosedRuntimeError(f"{field_name} must be a collection")
    if len(value) > MAX_COLLECTION_ITEMS:
        raise FailClosedRuntimeError(f"{field_name} exceeds item bound")
    normalized: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise FailClosedRuntimeError(
                f"{field_name} must contain non-empty text"
            )
        text = " ".join(item.split())
        if len(text) > MAX_COLLECTION_ITEM_CHARACTERS:
            raise FailClosedRuntimeError(
                f"{field_name} item exceeds storage bound"
            )
        if text in normalized:
            raise FailClosedRuntimeError(
                f"{field_name} contains duplicate values"
            )
        normalized.append(text)
    return normalized


def _confidence(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise FailClosedRuntimeError(
            "confidence must be a number between zero and one"
        )
    normalized = float(value)
    if (
        not math.isfinite(normalized)
        or normalized < 0.0
        or normalized > 1.0
    ):
        raise FailClosedRuntimeError(
            "confidence must be a number between zero and one"
        )
    return normalized


def _candidate_snapshot(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(
            "candidate Objective snapshot must be an object or null"
        )
    snapshot = deepcopy(value)
    encoded = _canonical_bytes(snapshot)
    if len(encoded) > MAX_CANDIDATE_BYTES:
        raise FailClosedRuntimeError(
            "candidate Objective snapshot exceeds storage bound"
        )
    if json.loads(encoded.decode("utf-8")) != snapshot:
        raise FailClosedRuntimeError(
            "candidate Objective snapshot is not canonical JSON"
        )
    pending: list[Any] = [snapshot]
    while pending:
        item = pending.pop()
        if isinstance(item, dict):
            for key, nested in item.items():
                if key in _FORBIDDEN_IDENTITY_FIELDS:
                    raise FailClosedRuntimeError(
                        "candidate Objective snapshot contains forbidden identity"
                    )
                pending.append(nested)
        elif isinstance(item, list):
            pending.extend(item)
    return snapshot


def _empty_commitment_metadata() -> dict[str, Any]:
    return {
        "commit_logic_implemented": False,
        "commitment_id": None,
        "objective_reference": None,
    }


def _canonical_timestamp(value: Any, field_name: str) -> str:
    timestamp = _parse_timestamp(value, field_name)
    return (
        timestamp.astimezone(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )


def _parse_timestamp(value: Any, field_name: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    try:
        timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise FailClosedRuntimeError(f"{field_name} is invalid") from exc
    if timestamp.tzinfo is None:
        raise FailClosedRuntimeError(f"{field_name} must include timezone")
    return timestamp.astimezone(timezone.utc)


def _expiration_timestamp(created_at: str, ttl_seconds: int) -> str:
    if (
        not isinstance(ttl_seconds, int)
        or isinstance(ttl_seconds, bool)
        or ttl_seconds < 1
        or ttl_seconds > MAX_TTL_SECONDS
    ):
        raise FailClosedRuntimeError(
            "conversation working memory TTL is invalid"
        )
    expires = _parse_timestamp(created_at, "created_at") + timedelta(
        seconds=ttl_seconds
    )
    return (
        expires.isoformat(timespec="seconds").replace("+00:00", "Z")
    )


def _is_expired(state: dict[str, Any], observed_at: str) -> bool:
    return _parse_timestamp(
        observed_at, "observed_at"
    ) >= _parse_timestamp(state["expires_at"], "expires_at")


def _reject_expired(state: dict[str, Any], observed_at: str) -> None:
    if _is_expired(state, observed_at):
        raise FailClosedRuntimeError(
            "conversation working memory state is expired"
        )


__all__ = [
    "ABSENT",
    "CANDIDATE_READY",
    "COMMITTED",
    "COMMITTING",
    "DEFAULT_TTL_SECONDS",
    "EXPLORING",
    "MAX_CANDIDATE_BYTES",
    "MAX_COLLECTION_ITEMS",
    "MAX_STATE_BYTES",
    "MAX_TTL_SECONDS",
    "PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_OWNER",
    "PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_RUNTIME_V1",
    "PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_SCHEMA_V1",
    "cleanup_conversation_working_memory_state",
    "conversation_working_memory_state_path",
    "create_conversation_working_memory_state",
    "load_conversation_working_memory_state",
    "recover_conversation_working_memory_state",
    "replace_conversation_working_memory_state_atomically",
    "update_conversation_working_memory_state",
    "validate_conversation_working_memory_state",
]
