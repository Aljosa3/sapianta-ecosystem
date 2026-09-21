"""Step69 owner-specific clarification evidence; no ingress or authority issuance.

Callers must independently reauthenticate the supplied Human decision evidence
before recording. Digest integrity is not actor/session authentication. This
module never consumes a Human act, presents Step46, or activates policy.
"""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
from types import MappingProxyType

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash

FIXED = MappingProxyType({
    "contract_version": "STEP69_GOVERNANCE_CLARIFICATION_BINDING_V1",
    "step": "STEP69",
    "decision_class": "STEP46_PRE_PRESENTATION_PROVENANCE_CONTRACT_CLARIFICATION",
    "owner": "CONSTITUTIONAL_GOVERNANCE_OWNER",
    "target": "STEP46_PRE_SOFTWARE_ADMISSION_AUTHORITY_POLICY",
    "semantic_scope": "PRE_PRESENTATION_PROVENANCE_ONLY",
    "implementation_authorized": False,
    "step46_presentation_authorized": False,
    "g70_authorized": False,
    "e05_authorized": False,
    "immediate_constitutional_effect": False,
    "production_connection": False,
})
OUTCOMES = frozenset({"APPROVAL", "REWORK", "REJECT", "CANCEL"})
TEXT_FIELDS = ("human_outcome", "human_acknowledgement",
               "channel_provenance_policy", "target_revision_policy")
EVIDENCE_TEXT_FIELDS = ("decision_reference", "actor_identity", "session_identity",
                        "presentation_reference", "exact_human_response")
PAYLOAD_FIELDS = frozenset(FIXED) | frozenset(TEXT_FIELDS) | {"human_decision_evidence"}
RECORD_FIELDS = PAYLOAD_FIELDS | {"record_identity", "record_digest"}
DIRECTORY = "step69_governance_clarification_evidence_v1"
# Identity deliberately excludes outcome/content: divergent decisions cannot
# evade conflict detection by obtaining a new content-derived locator.
RECORD_IDENTITY = "STEP69-CLARIFICATION-" + replay_hash({
    key: FIXED[key] for key in ("step", "decision_class", "owner", "target", "semantic_scope")
}).removeprefix("sha256:")


def _text(value: object) -> bool:
    return type(value) is str and bool(value.strip()) and "\x00" not in value


def _payload(value: object) -> dict:
    if type(value) is not dict or set(value) != PAYLOAD_FIELDS:
        raise FailClosedRuntimeError("Step69 clarification payload field set is invalid")
    result = deepcopy(value)
    for key, expected in FIXED.items():
        if type(result[key]) is not type(expected) or result[key] != expected:
            raise FailClosedRuntimeError(f"Step69 fixed binding is invalid: {key}")
    if any(not _text(result[key]) for key in TEXT_FIELDS):
        raise FailClosedRuntimeError("Step69 decision and policy text must be explicit")
    if result["human_outcome"] not in OUTCOMES:
        raise FailClosedRuntimeError("Step69 outcome is invalid")
    evidence = result["human_decision_evidence"]
    expected_fields = set(EVIDENCE_TEXT_FIELDS) | {"decision_payload_digest", "response_digest"}
    if type(evidence) is not dict or set(evidence) != expected_fields:
        raise FailClosedRuntimeError("Step69 decision evidence field set is invalid")
    if any(not _text(evidence[key]) for key in EVIDENCE_TEXT_FIELDS):
        raise FailClosedRuntimeError("Step69 decision evidence text is invalid")
    if result["human_acknowledgement"] not in evidence["exact_human_response"]:
        raise FailClosedRuntimeError("Step69 acknowledgement is not in the exact response")
    if evidence["response_digest"] != replay_hash(evidence["exact_human_response"]):
        raise FailClosedRuntimeError("Step69 response digest mismatch")
    decision_payload = {key: result[key] for key in result if key != "human_decision_evidence"}
    if evidence["decision_payload_digest"] != replay_hash(decision_payload):
        raise FailClosedRuntimeError("Step69 decision payload binding mismatch")
    return result


def create_step69_clarification_record_v1(payload: dict) -> dict:
    """Bind supplied evidence, without choosing policy or authenticating a Human."""
    record = _payload(payload)
    record["record_identity"] = RECORD_IDENTITY
    record["record_digest"] = replay_hash(record)
    return record


def validate_step69_clarification_record_v1(record: object) -> dict:
    """Validate the closed owner-specific schema and every canonical binding."""
    if type(record) is not dict or set(record) != RECORD_FIELDS:
        raise FailClosedRuntimeError("Step69 record field set is invalid")
    expected = create_step69_clarification_record_v1({key: record[key] for key in PAYLOAD_FIELDS})
    if record != expected:
        raise FailClosedRuntimeError("Step69 record identity or digest mismatch")
    return expected


def _path(storage_root: Path) -> Path:
    return Path(storage_root) / DIRECTORY / (RECORD_IDENTITY + ".json")


def read_step69_clarification_record_v1(*, storage_root: Path) -> dict:
    """Read and validate exact persisted bytes; never repair or write evidence."""
    path = _path(storage_root)
    try:
        if path.is_symlink():
            raise FailClosedRuntimeError("Step69 record must not be a symlink")
        raw = path.read_bytes()
        record = validate_step69_clarification_record_v1(json.loads(raw))
        if raw != (canonical_serialize(record) + "\n").encode("utf-8"):
            raise FailClosedRuntimeError("Step69 record bytes are not canonical")
        return record
    except (OSError, ValueError, UnicodeError) as exc:
        raise FailClosedRuntimeError("Step69 record is unreadable") from exc


def persist_step69_clarification_record_v1(*, storage_root: Path, record: dict) -> Path:
    """Publish immutable owner evidence using the existing Step62 fsync/link pattern.

    This is not the Step62 API. Storage root is the existing governance evidence
    root supplied by the authorized caller, not a new authority or ingress.
    """
    expected = validate_step69_clarification_record_v1(record)
    path = _path(storage_root)
    temporary_name = ""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        # Persist creation of the owner directory as well as its record entry.
        root_descriptor = os.open(path.parent.parent, os.O_RDONLY)
        try:
            os.fsync(root_descriptor)
        finally:
            os.close(root_descriptor)
        if not path.exists() and not path.is_symlink():
            descriptor, temporary_name = tempfile.mkstemp(prefix=".step69-", suffix=".tmp", dir=path.parent)
            with os.fdopen(descriptor, "wb") as handle:
                handle.write((canonical_serialize(expected) + "\n").encode("utf-8"))
                handle.flush()
                os.fsync(handle.fileno())
            try:
                os.link(temporary_name, path)
            except FileExistsError:
                pass  # Authenticate the winner below; never overwrite it.
        if read_step69_clarification_record_v1(storage_root=storage_root) != expected:
            raise FailClosedRuntimeError("Step69 same-identity content conflict")
        # Also sync on identical retry after a publication/directory-sync failure.
        directory_descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    except OSError as exc:
        raise FailClosedRuntimeError("Step69 immutable publication failed") from exc
    finally:
        if temporary_name and Path(temporary_name).exists():
            Path(temporary_name).unlink()
    return path
