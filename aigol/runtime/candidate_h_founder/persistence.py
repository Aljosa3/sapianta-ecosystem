"""Durable Candidate H immutable records and one-winner CAS slots.

Only Stage-2-validated canonical models may cross this write boundary.  The
module provides mechanical persistence and authoritative read-back; it does
not authenticate, sign, select a Human disposition, orchestrate, replay,
execute BEGIN, or mutate a constitutional root.
"""

from __future__ import annotations

import fcntl
import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from tempfile import mkstemp

from .cj1 import CJ1Error, cj1_decode, cj1_digest, cj1_encode, sha256_hex
from .models import FrozenCanonicalModel
from .validators import (
    ARTIFACT_IDENTITY_SPECS,
    CandidateValidationError,
    validate_artifact,
)


IMMUTABLE_AFTER_TEMP_FSYNC = "IMMUTABLE_AFTER_TEMP_FSYNC"
IMMUTABLE_AFTER_PUBLISH = "IMMUTABLE_AFTER_PUBLISH"
SLOT_AFTER_GENERATION_FSYNC = "SLOT_AFTER_GENERATION_FSYNC"
SLOT_AFTER_GENERATION_PUBLISH = "SLOT_AFTER_GENERATION_PUBLISH"
SLOT_AFTER_POINTER_FSYNC = "SLOT_AFTER_POINTER_FSYNC"
SLOT_AFTER_POINTER_REPLACE = "SLOT_AFTER_POINTER_REPLACE"

CRASH_POINTS = (
    IMMUTABLE_AFTER_TEMP_FSYNC,
    IMMUTABLE_AFTER_PUBLISH,
    SLOT_AFTER_GENERATION_FSYNC,
    SLOT_AFTER_GENERATION_PUBLISH,
    SLOT_AFTER_POINTER_FSYNC,
    SLOT_AFTER_POINTER_REPLACE,
)

CrashHook = Callable[[str], None]


class CandidatePersistenceError(RuntimeError):
    """Stable fail-closed persistence or read-back failure."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}:{detail}")


class InjectedPersistenceCrash(RuntimeError):
    """Fixture-only process-crash surrogate used at declared write boundaries."""


@dataclass(frozen=True, slots=True)
class ArtifactAddress:
    """Mechanical address of one already validated constitutional artifact."""

    artifact_identity: str
    artifact_digest: str


@dataclass(frozen=True, slots=True)
class ImmutableReadBack:
    """Non-canonical operational view of exact persisted artifact bytes."""

    address: ArtifactAddress
    storage_digest: str
    canonical_bytes: bytes


@dataclass(frozen=True, slots=True)
class ImmutableWriteResult:
    outcome: str
    read_back: ImmutableReadBack


@dataclass(frozen=True, slots=True)
class SlotReadBack:
    """Validated current-pointer view; not a constitutional artifact family."""

    owner: str
    slot_identity: str
    slot_epoch: object
    generation: int
    predecessor_slot_digest: str | None
    predecessor_status: str | None
    current_status: str
    artifact_identity: str
    artifact_digest: str
    artifact_storage_digest: str
    logical_instant: str
    slot_digest: str


@dataclass(frozen=True, slots=True)
class CompareAndSwapResult:
    outcome: str
    read_back: SlotReadBack


def _fail(code: str, detail: str) -> None:
    raise CandidatePersistenceError(code, detail)


def _require_text(value: object, detail: str) -> str:
    if not isinstance(value, str) or not value:
        _fail("INVALID_PERSISTENCE_INPUT", detail)
    try:
        cj1_encode(value)
    except CJ1Error as exc:
        _fail("INVALID_PERSISTENCE_INPUT", f"{detail}:{exc}")
    return value


def _write_all(fd: int, data: bytes) -> None:
    view = memoryview(data)
    written = 0
    while written < len(view):
        count = os.write(fd, view[written:])
        if count <= 0:
            _fail("DURABLE_WRITE_FAILED", "zero-byte write")
        written += count


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


class CandidateHReadOnlyStore:
    """Capability-limited read interface with no write or CAS methods."""

    __slots__ = ("_store",)

    def __init__(self, store: "CandidateHStore") -> None:
        self._store = store

    def read_immutable(
        self,
        model_type: type[FrozenCanonicalModel],
        address: ArtifactAddress,
        *,
        owner_bindings: Mapping[str, str] | None = None,
    ) -> tuple[FrozenCanonicalModel, ImmutableReadBack]:
        return self._store.read_immutable(
            model_type, address, owner_bindings=owner_bindings
        )

    def read_slot(self, owner: str, slot_identity: str, slot_epoch: object) -> SlotReadBack:
        return self._store.read_slot(owner, slot_identity, slot_epoch)


class CandidateHStore:
    """Filesystem-backed immutable record store with serialized CAS slots."""

    def __init__(self, root: str | os.PathLike[str]) -> None:
        self._root = Path(root)
        self._records = self._root / "records"
        self._slots = self._root / "slots"
        self._generations = self._root / "slot-generations"
        self._locks = self._root / "locks"
        for path in (self._root, self._records, self._slots, self._generations, self._locks):
            path.mkdir(mode=0o700, parents=True, exist_ok=True)
            if path.is_symlink() or not path.is_dir():
                _fail("UNSAFE_STORE_PATH", str(path))

    def readonly(self) -> CandidateHReadOnlyStore:
        return CandidateHReadOnlyStore(self)

    @staticmethod
    def _key(*parts: object) -> str:
        return sha256_hex(cj1_encode(list(parts)))

    def _record_path(self, artifact_identity: str) -> Path:
        return self._records / f"{self._key(artifact_identity)}.cj1"

    def _slot_key(self, owner: str, slot_identity: str, slot_epoch: object) -> str:
        return self._key(owner, slot_identity, slot_epoch)

    def _pointer_path(self, slot_key: str) -> Path:
        return self._slots / f"{slot_key}.current.cj1"

    def _generation_path(self, slot_key: str, generation: int, slot_digest: str) -> Path:
        digest_hex = slot_digest.removeprefix("sha256:")
        return self._generations / f"{slot_key}.{generation}.{digest_hex}.cj1"

    @staticmethod
    def _invoke(hook: CrashHook | None, point: str) -> None:
        if hook is not None:
            hook(point)

    @staticmethod
    def _artifact_address(
        model: FrozenCanonicalModel,
        artifact_identity: str | None,
        artifact_digest: str | None,
    ) -> ArtifactAddress:
        spec = ARTIFACT_IDENTITY_SPECS.get(type(model))
        if spec is not None:
            expected_identity = getattr(model, spec.identity_field)
            expected_digest = getattr(model, spec.digest_field)
            if artifact_identity is not None and artifact_identity != expected_identity:
                _fail("ARTIFACT_ADDRESS_MISMATCH", "identity")
            if artifact_digest is not None and artifact_digest != expected_digest:
                _fail("ARTIFACT_ADDRESS_MISMATCH", "digest")
            artifact_identity = expected_identity
            artifact_digest = expected_digest
        else:
            if artifact_identity is None or artifact_digest is None:
                _fail("ARTIFACT_ADDRESS_REQUIRED", type(model).__name__)
            expected_digest = cj1_digest(model.to_cj1_object())
            if artifact_digest != expected_digest:
                _fail("ARTIFACT_ADDRESS_MISMATCH", "digest")
            identity_parts = artifact_identity.rsplit(":", 1)
            if len(identity_parts) != 2 or not identity_parts[0] or identity_parts[1] != expected_digest[7:]:
                _fail("ARTIFACT_ADDRESS_MISMATCH", "content identity")
        identity = _require_text(artifact_identity, "artifact_identity")
        digest = _require_text(artifact_digest, "artifact_digest")
        if not digest.startswith("sha256:") or len(digest) != 71:
            _fail("ARTIFACT_ADDRESS_MISMATCH", "digest format")
        return ArtifactAddress(identity, digest)

    def _publish_immutable_bytes(
        self,
        path: Path,
        data: bytes,
        *,
        hook: CrashHook | None,
        fsync_point: str,
        publish_point: str,
    ) -> str:
        if path.exists():
            existing = self._read_exact(path, "CORRUPT_IMMUTABLE_RECORD")
            if existing != data:
                _fail("IMMUTABLE_RECORD_CONFLICT", path.name)
            return "IDEMPOTENT"
        fd, temporary_name = mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
        temporary = Path(temporary_name)
        published = False
        try:
            _write_all(fd, data)
            os.fsync(fd)
            self._invoke(hook, fsync_point)
        finally:
            os.close(fd)
        try:
            os.link(temporary, path)
            published = True
            self._invoke(hook, publish_point)
            _fsync_directory(path.parent)
        except FileExistsError:
            existing = self._read_exact(path, "CORRUPT_IMMUTABLE_RECORD")
            if existing != data:
                _fail("IMMUTABLE_RECORD_CONFLICT", path.name)
        finally:
            if temporary.exists() and (published or path.exists()):
                temporary.unlink()
        return "CREATED" if published else "IDEMPOTENT"

    @staticmethod
    def _read_exact(path: Path, corruption_code: str) -> bytes:
        try:
            data = path.read_bytes()
        except FileNotFoundError:
            raise
        try:
            value = cj1_decode(data)
        except CJ1Error as exc:
            _fail(corruption_code, f"{path.name}:{exc}")
        if cj1_encode(value) != data:
            _fail(corruption_code, path.name)
        return data

    def write_immutable(
        self,
        model: FrozenCanonicalModel,
        *,
        artifact_identity: str | None = None,
        artifact_digest: str | None = None,
        owner_bindings: Mapping[str, str] | None = None,
        _fixture_crash_hook: CrashHook | None = None,
    ) -> ImmutableWriteResult:
        validate_artifact(model, owner_bindings=owner_bindings)
        address = self._artifact_address(model, artifact_identity, artifact_digest)
        canonical_bytes = model.to_cj1_bytes()
        outcome = self._publish_immutable_bytes(
            self._record_path(address.artifact_identity),
            canonical_bytes,
            hook=_fixture_crash_hook,
            fsync_point=IMMUTABLE_AFTER_TEMP_FSYNC,
            publish_point=IMMUTABLE_AFTER_PUBLISH,
        )
        _, read_back = self.read_immutable(
            type(model), address, owner_bindings=owner_bindings
        )
        if read_back.canonical_bytes != canonical_bytes:
            _fail("WRITE_READ_BACK_MISMATCH", address.artifact_identity)
        return ImmutableWriteResult(outcome, read_back)

    def read_immutable(
        self,
        model_type: type[FrozenCanonicalModel],
        address: ArtifactAddress,
        *,
        owner_bindings: Mapping[str, str] | None = None,
    ) -> tuple[FrozenCanonicalModel, ImmutableReadBack]:
        if not isinstance(model_type, type) or not issubclass(model_type, FrozenCanonicalModel):
            _fail("UNKNOWN_SCHEMA_VERSION", getattr(model_type, "__name__", repr(model_type)))
        identity = _require_text(address.artifact_identity, "artifact_identity")
        try:
            canonical_bytes = self._read_exact(
                self._record_path(identity), "CORRUPT_IMMUTABLE_RECORD"
            )
        except FileNotFoundError:
            _fail("MISSING_IMMUTABLE_RECORD", identity)
        try:
            value = cj1_decode(canonical_bytes)
            if not isinstance(value, dict):
                _fail("CORRUPT_IMMUTABLE_RECORD", identity)
            model = model_type(**value)
            validate_artifact(model, owner_bindings=owner_bindings)
        except (CJ1Error, CandidateValidationError, TypeError, ValueError) as exc:
            if isinstance(exc, CandidatePersistenceError):
                raise
            _fail("CORRUPT_IMMUTABLE_RECORD", f"{identity}:{exc}")
        actual_address = self._artifact_address(
            model, address.artifact_identity, address.artifact_digest
        )
        storage_digest = cj1_digest(value)
        return model, ImmutableReadBack(actual_address, storage_digest, canonical_bytes)

    @staticmethod
    def _slot_payload(
        *,
        owner: str,
        slot_identity: str,
        slot_epoch: object,
        generation: int,
        predecessor_slot_digest: str | None,
        predecessor_status: str | None,
        current_status: str,
        address: ArtifactAddress,
        artifact_storage_digest: str,
        logical_instant: str,
    ) -> dict[str, object]:
        return {
            "owner": owner,
            "slot_identity": slot_identity,
            "slot_epoch": slot_epoch,
            "generation": generation,
            "predecessor_slot_digest": predecessor_slot_digest,
            "predecessor_status": predecessor_status,
            "current_status": current_status,
            "artifact_identity": address.artifact_identity,
            "artifact_digest": address.artifact_digest,
            "artifact_storage_digest": artifact_storage_digest,
            "logical_instant": logical_instant,
        }

    @staticmethod
    def _slot_from_payload(payload: object, expected_digest: str) -> SlotReadBack:
        if not isinstance(payload, dict):
            _fail("CORRUPT_SLOT", "generation is not an object")
        expected_fields = (
            "artifact_digest",
            "artifact_identity",
            "artifact_storage_digest",
            "current_status",
            "generation",
            "logical_instant",
            "owner",
            "predecessor_slot_digest",
            "predecessor_status",
            "slot_epoch",
            "slot_identity",
        )
        if tuple(sorted(payload)) != expected_fields:
            _fail("CORRUPT_SLOT", "generation schema")
        if cj1_digest(payload) != expected_digest:
            _fail("CORRUPT_SLOT", "generation digest")
        if not isinstance(payload["generation"], int) or isinstance(payload["generation"], bool) or payload["generation"] < 1:
            _fail("CORRUPT_SLOT", "generation number")
        for name in (
            "owner", "slot_identity", "current_status", "artifact_identity",
            "artifact_digest", "artifact_storage_digest", "logical_instant",
        ):
            _require_text(payload[name], name)
        for name in ("predecessor_slot_digest", "predecessor_status"):
            if payload[name] is not None:
                _require_text(payload[name], name)
        return SlotReadBack(
            owner=payload["owner"],
            slot_identity=payload["slot_identity"],
            slot_epoch=payload["slot_epoch"],
            generation=payload["generation"],
            predecessor_slot_digest=payload["predecessor_slot_digest"],
            predecessor_status=payload["predecessor_status"],
            current_status=payload["current_status"],
            artifact_identity=payload["artifact_identity"],
            artifact_digest=payload["artifact_digest"],
            artifact_storage_digest=payload["artifact_storage_digest"],
            logical_instant=payload["logical_instant"],
            slot_digest=expected_digest,
        )

    def _read_slot_key(self, slot_key: str) -> SlotReadBack:
        pointer_path = self._pointer_path(slot_key)
        try:
            pointer_bytes = self._read_exact(pointer_path, "CORRUPT_SLOT_POINTER")
        except FileNotFoundError:
            _fail("MISSING_SLOT", slot_key)
        pointer = cj1_decode(pointer_bytes)
        if not isinstance(pointer, dict) or tuple(sorted(pointer)) != ("generation", "slot_digest"):
            _fail("CORRUPT_SLOT_POINTER", slot_key)
        generation = pointer["generation"]
        slot_digest = pointer["slot_digest"]
        if not isinstance(generation, int) or isinstance(generation, bool) or generation < 1:
            _fail("CORRUPT_SLOT_POINTER", "generation")
        if not isinstance(slot_digest, str) or not slot_digest.startswith("sha256:"):
            _fail("CORRUPT_SLOT_POINTER", "slot_digest")
        generation_path = self._generation_path(slot_key, generation, slot_digest)
        try:
            generation_bytes = self._read_exact(generation_path, "CORRUPT_SLOT")
        except FileNotFoundError:
            _fail("PARTIAL_SLOT", slot_key)
        return self._slot_from_payload(cj1_decode(generation_bytes), slot_digest)

    def read_slot(self, owner: str, slot_identity: str, slot_epoch: object) -> SlotReadBack:
        owner = _require_text(owner, "owner")
        slot_identity = _require_text(slot_identity, "slot_identity")
        cj1_encode(slot_epoch)
        slot_key = self._slot_key(owner, slot_identity, slot_epoch)
        current = self._read_slot_key(slot_key)
        if (current.owner, current.slot_identity, current.slot_epoch) != (
            owner, slot_identity, slot_epoch
        ):
            _fail("SLOT_BINDING_MISMATCH", slot_key)
        record_path = self._record_path(current.artifact_identity)
        try:
            record_bytes = self._read_exact(record_path, "CORRUPT_IMMUTABLE_RECORD")
        except FileNotFoundError:
            _fail("PARTIAL_SLOT", current.artifact_identity)
        if cj1_digest(cj1_decode(record_bytes)) != current.artifact_storage_digest:
            _fail("SLOT_ARTIFACT_MISMATCH", current.artifact_identity)
        return current

    def _replace_pointer(
        self,
        path: Path,
        data: bytes,
        hook: CrashHook | None,
    ) -> None:
        fd, temporary_name = mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
        temporary = Path(temporary_name)
        replaced = False
        try:
            _write_all(fd, data)
            os.fsync(fd)
            self._invoke(hook, SLOT_AFTER_POINTER_FSYNC)
        finally:
            os.close(fd)
        try:
            os.replace(temporary, path)
            replaced = True
            self._invoke(hook, SLOT_AFTER_POINTER_REPLACE)
            _fsync_directory(path.parent)
        finally:
            if temporary.exists() and replaced:
                temporary.unlink()

    def compare_and_swap(
        self,
        *,
        owner: str,
        slot_identity: str,
        slot_epoch: object,
        expected_slot_digest: str | None,
        expected_status: str | None,
        successor_status: str,
        model: FrozenCanonicalModel,
        artifact_identity: str | None = None,
        artifact_digest: str | None = None,
        logical_instant: str,
        owner_bindings: Mapping[str, str] | None = None,
        _fixture_crash_hook: CrashHook | None = None,
    ) -> CompareAndSwapResult:
        owner = _require_text(owner, "owner")
        slot_identity = _require_text(slot_identity, "slot_identity")
        successor_status = _require_text(successor_status, "successor_status")
        logical_instant = _require_text(logical_instant, "logical_instant")
        cj1_encode(slot_epoch)
        if (expected_slot_digest is None) != (expected_status is None):
            _fail("INVALID_EXPECTED_SLOT", "digest/status half-pair")
        if expected_slot_digest is not None:
            _require_text(expected_slot_digest, "expected_slot_digest")
        validate_artifact(model, owner_bindings=owner_bindings)
        if getattr(model, "producing_owner", owner) != owner:
            _fail("PERSISTENCE_OWNER_MISMATCH", type(model).__name__)
        address = self._artifact_address(model, artifact_identity, artifact_digest)
        canonical_bytes = model.to_cj1_bytes()
        storage_digest = cj1_digest(model.to_cj1_object())
        slot_key = self._slot_key(owner, slot_identity, slot_epoch)
        lock_path = self._locks / f"{slot_key}.lock"
        lock_fd = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o600)
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX)
            try:
                current = self._read_slot_key(slot_key)
            except CandidatePersistenceError as exc:
                if exc.code != "MISSING_SLOT":
                    raise
                current = None
            if current is not None:
                identical = (
                    current.predecessor_slot_digest == expected_slot_digest
                    and current.predecessor_status == expected_status
                    and current.current_status == successor_status
                    and current.artifact_identity == address.artifact_identity
                    and current.artifact_digest == address.artifact_digest
                    and current.artifact_storage_digest == storage_digest
                    and current.logical_instant == logical_instant
                )
                if identical:
                    return CompareAndSwapResult("IDEMPOTENT", self.read_slot(owner, slot_identity, slot_epoch))
            actual_digest = None if current is None else current.slot_digest
            actual_status = None if current is None else current.current_status
            if actual_digest != expected_slot_digest or actual_status != expected_status:
                if current is None:
                    _fail("CAS_CONFLICT_WITH_ABSENT_SLOT", slot_key)
                return CompareAndSwapResult("CONFLICT", self.read_slot(owner, slot_identity, slot_epoch))
            record_outcome = self._publish_immutable_bytes(
                self._record_path(address.artifact_identity),
                canonical_bytes,
                hook=_fixture_crash_hook,
                fsync_point=IMMUTABLE_AFTER_TEMP_FSYNC,
                publish_point=IMMUTABLE_AFTER_PUBLISH,
            )
            if record_outcome not in {"CREATED", "IDEMPOTENT"}:
                _fail("DURABLE_WRITE_FAILED", address.artifact_identity)
            generation = 1 if current is None else current.generation + 1
            payload = self._slot_payload(
                owner=owner,
                slot_identity=slot_identity,
                slot_epoch=slot_epoch,
                generation=generation,
                predecessor_slot_digest=expected_slot_digest,
                predecessor_status=expected_status,
                current_status=successor_status,
                address=address,
                artifact_storage_digest=storage_digest,
                logical_instant=logical_instant,
            )
            slot_digest = cj1_digest(payload)
            generation_path = self._generation_path(slot_key, generation, slot_digest)
            self._publish_immutable_bytes(
                generation_path,
                cj1_encode(payload),
                hook=_fixture_crash_hook,
                fsync_point=SLOT_AFTER_GENERATION_FSYNC,
                publish_point=SLOT_AFTER_GENERATION_PUBLISH,
            )
            pointer = cj1_encode({"generation": generation, "slot_digest": slot_digest})
            self._replace_pointer(self._pointer_path(slot_key), pointer, _fixture_crash_hook)
            read_back = self.read_slot(owner, slot_identity, slot_epoch)
            if read_back.slot_digest != slot_digest:
                _fail("WRITE_READ_BACK_MISMATCH", slot_key)
            return CompareAndSwapResult("WON", read_back)
        finally:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            os.close(lock_fd)


__all__ = [
    "ArtifactAddress",
    "CRASH_POINTS",
    "CandidateHReadOnlyStore",
    "CandidateHStore",
    "CandidatePersistenceError",
    "CompareAndSwapResult",
    "IMMUTABLE_AFTER_PUBLISH",
    "IMMUTABLE_AFTER_TEMP_FSYNC",
    "ImmutableReadBack",
    "ImmutableWriteResult",
    "InjectedPersistenceCrash",
    "SLOT_AFTER_GENERATION_FSYNC",
    "SLOT_AFTER_GENERATION_PUBLISH",
    "SLOT_AFTER_POINTER_FSYNC",
    "SLOT_AFTER_POINTER_REPLACE",
    "SlotReadBack",
]
