"""Detached read-only shadow comparison for the G77-255Q V1 projection.

This module has no production entry point, persistence, routing, semantic,
Human, execution, or mutation authority.  It authenticates one committed
reference projection and compares it with an independently authenticated
current payload.  Failure never repairs or returns projected state.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import subprocess
from types import MappingProxyType
from typing import Any, Mapping

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize


CONTRACT_IDENTITY = (
    "SAPIANTA_CANONICAL_CONSTITUTIONAL_CONTINUATION_REFERENCE_"
    "PROJECTION_CONTRACT"
)
CONTRACT_VERSION = "V1"
DOMAIN_PREFIX = (
    "SAPIANTA_CANONICAL_CONSTITUTIONAL_CONTINUATION_REFERENCE_"
    "PROJECTION_CONTRACT\nCONTRACT_VERSION=V1\n"
)

EQUAL = "EQUAL"
MISMATCH = "MISMATCH"
FAILED_CLOSED = "FAILED_CLOSED"

_FIELDS = (
    "PREDECESSOR_ID",
    "PREDECESSOR_GIT_IDENTITY",
    "PREDECESSOR_SHA256",
    "CURRENT_CONSTITUTIONAL_FRONTIER",
    "CLOSED_COORDINATES",
    "OPEN_COORDINATE",
    "RELEVANT_INVARIANTS",
    "HUMAN_AUTHORITY_STATE",
    "COGNITION_PROVENANCE_STATE",
    "ALLOWED_NEXT_OPERATION",
    "FORBIDDEN_OPERATIONS",
    "TOPOLOGY_COMMITMENT",
    "RELEVANT_REPLAY_OR_EVIDENCE_REFERENCE",
    "STOP_FAIL_CLOSED_CONDITIONS",
)
_FIELD_SET = frozenset(_FIELDS)
_PREDECESSOR_ID_FIELDS = frozenset({"artifact_id", "repository_path"})
_GIT_IDENTITY_FIELDS = frozenset({"commit", "parents", "subject", "tree"})
_HUMAN_AUTHORITY_FIELDS = frozenset(
    {
        "constitutional_authority_owner",
        "constitutional_authority_share",
        "exact_human_act_required_for_semantic_advancement",
        "semantic_advancement_authorized_by_projection",
    }
)
_COGNITION_PROVENANCE_FIELDS = frozenset(
    {
        "admissible_provenance",
        "llm_semantic_authority_share",
        "unknown_provenance_admissible",
    }
)
_TOPOLOGY_FIELDS = frozenset(
    {
        "AUTHORITY_PATHS",
        "HUMAN_ENTRY_PATHS",
        "PARALLEL_PATHS",
        "PRODUCTION_PATHS",
    }
)
_EVIDENCE_REFERENCE_FIELDS = frozenset(
    {"artifact_id", "git_blob", "git_commit", "repository_path", "sha256"}
)
_EXPECTED_TOPOLOGY = {
    "AUTHORITY_PATHS": 1,
    "HUMAN_ENTRY_PATHS": 1,
    "PARALLEL_PATHS": 0,
    "PRODUCTION_PATHS": 1,
}
_GIT_OID = re.compile(r"^[0-9a-f]{40}$")
_SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")

_AUTHORITY_FLAGS = {
    "semantic_authority": False,
    "execution_authority": False,
    "production_authority": False,
    "human_authority": False,
    "routing_authority": False,
    "state_mutation_authority": False,
}


def compare_constitutional_continuation_reference_projection_shadow_v1(
    *,
    serialized_projection: str,
    projection_hash: str,
    authenticated_current_payload: Mapping[str, Any],
    repository_root: str | Path,
    expected_head: str,
) -> Mapping[str, Any]:
    """Return a detached zero-authority comparison result.

    The projection is never returned, persisted, routed, repaired, or treated
    as constitutional state.  The independently authenticated current payload
    remains authoritative regardless of the comparison outcome.
    """

    try:
        projection = _load_canonical_projection(serialized_projection)
        _validate_payload(projection)
        declared_hash = _require_sha256(projection_hash, "projection_hash")
        expected_hash = _projection_hash(projection)
        if declared_hash != expected_hash:
            _fail("PROJECTION_HASH_MISMATCH")

        root = _authenticate_repository_sources(
            projection,
            repository_root=repository_root,
            expected_head=expected_head,
        )
        current = _detached_mapping(authenticated_current_payload, "current payload")
        _validate_payload(current)

        outcome = (
            EQUAL
            if canonical_serialize(projection) == canonical_serialize(current)
            else MISMATCH
        )
        return _freeze(
            _comparison_result(
                outcome=outcome,
                projection_hash=expected_hash,
                current_hash=_projection_hash(current),
                failure_reason=None,
                repository_root=str(root),
            )
        )
    except (FailClosedRuntimeError, OSError, UnicodeError, ValueError) as exc:
        reason = str(exc) or "SHADOW_VALIDATION_FAILED"
        return _freeze(
            _comparison_result(
                outcome=FAILED_CLOSED,
                projection_hash=None,
                current_hash=None,
                failure_reason=reason,
                repository_root=None,
            )
        )


def _projection_hash(payload: Mapping[str, Any]) -> str:
    canonical_payload = canonical_serialize(payload).encode("utf-8")
    digest = hashlib.sha256(DOMAIN_PREFIX.encode("utf-8") + canonical_payload)
    return "sha256:" + digest.hexdigest()


def _load_canonical_projection(serialized: Any) -> dict[str, Any]:
    if not isinstance(serialized, str) or not serialized:
        _fail("PROJECTION_SERIALIZATION_REQUIRED")
    try:
        value = json.loads(
            serialized,
            object_pairs_hook=_reject_duplicate_keys,
            parse_float=_reject_float,
            parse_constant=_reject_constant,
        )
    except FailClosedRuntimeError:
        raise
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise FailClosedRuntimeError("PROJECTION_MALFORMED_JSON") from exc
    if not isinstance(value, dict):
        _fail("PROJECTION_ROOT_NOT_OBJECT")
    if canonical_serialize(value) != serialized:
        _fail("PROJECTION_NON_CANONICAL_SERIALIZATION")
    return value


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _fail("PROJECTION_DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def _reject_float(_value: str) -> Any:
    _fail("PROJECTION_FLOAT_REJECTED")


def _reject_constant(_value: str) -> Any:
    _fail("PROJECTION_NON_JSON_NUMBER_REJECTED")


def _validate_payload(payload: Mapping[str, Any]) -> None:
    value = _detached_mapping(payload, "projection payload")
    _require_exact_fields(value, _FIELD_SET, "projection payload")

    predecessor = _require_mapping(value["PREDECESSOR_ID"], "PREDECESSOR_ID")
    _require_exact_fields(predecessor, _PREDECESSOR_ID_FIELDS, "PREDECESSOR_ID")
    _require_text(predecessor["artifact_id"], "PREDECESSOR_ID.artifact_id")
    _require_repository_path(
        predecessor["repository_path"], "PREDECESSOR_ID.repository_path"
    )

    git_identity = _require_mapping(
        value["PREDECESSOR_GIT_IDENTITY"], "PREDECESSOR_GIT_IDENTITY"
    )
    _require_exact_fields(
        git_identity, _GIT_IDENTITY_FIELDS, "PREDECESSOR_GIT_IDENTITY"
    )
    _require_git_oid(git_identity["commit"], "PREDECESSOR_GIT_IDENTITY.commit")
    parents = _require_array(git_identity["parents"], "PREDECESSOR_GIT_IDENTITY.parents")
    _require_unique(parents, "PREDECESSOR_GIT_IDENTITY.parents")
    for index, parent in enumerate(parents):
        _require_git_oid(parent, f"PREDECESSOR_GIT_IDENTITY.parents[{index}]")
    _require_text(git_identity["subject"], "PREDECESSOR_GIT_IDENTITY.subject")
    _require_git_oid(git_identity["tree"], "PREDECESSOR_GIT_IDENTITY.tree")

    _require_sha256(value["PREDECESSOR_SHA256"], "PREDECESSOR_SHA256")
    _require_text(
        value["CURRENT_CONSTITUTIONAL_FRONTIER"],
        "CURRENT_CONSTITUTIONAL_FRONTIER",
    )
    closed = _require_nonempty_array(value["CLOSED_COORDINATES"], "CLOSED_COORDINATES")
    _validate_text_array(closed, "CLOSED_COORDINATES", sorted_required=False)
    _require_text(value["OPEN_COORDINATE"], "OPEN_COORDINATE")

    invariants = _require_nonempty_array(
        value["RELEVANT_INVARIANTS"], "RELEVANT_INVARIANTS"
    )
    _validate_text_array(invariants, "RELEVANT_INVARIANTS", sorted_required=True)

    human = _require_mapping(value["HUMAN_AUTHORITY_STATE"], "HUMAN_AUTHORITY_STATE")
    _require_exact_fields(human, _HUMAN_AUTHORITY_FIELDS, "HUMAN_AUTHORITY_STATE")
    owner = _require_text(
        human["constitutional_authority_owner"],
        "HUMAN_AUTHORITY_STATE.constitutional_authority_owner",
    )
    _require_text(
        human["constitutional_authority_share"],
        "HUMAN_AUTHORITY_STATE.constitutional_authority_share",
    )
    human_act_required = _require_bool(
        human["exact_human_act_required_for_semantic_advancement"],
        "HUMAN_AUTHORITY_STATE.exact_human_act_required_for_semantic_advancement",
    )
    if _require_bool(
        human["semantic_advancement_authorized_by_projection"],
        "HUMAN_AUTHORITY_STATE.semantic_advancement_authorized_by_projection",
    ):
        _fail("PROJECTION_SEMANTIC_AUTHORITY_PROHIBITED")
    if owner == "HUMAN_CONSTITUTIONAL_AUTHORITY" and not human_act_required:
        _fail("EXACT_HUMAN_ACT_REQUIREMENT_MISSING")

    cognition = _require_mapping(
        value["COGNITION_PROVENANCE_STATE"], "COGNITION_PROVENANCE_STATE"
    )
    _require_exact_fields(
        cognition, _COGNITION_PROVENANCE_FIELDS, "COGNITION_PROVENANCE_STATE"
    )
    provenance = _require_nonempty_array(
        cognition["admissible_provenance"],
        "COGNITION_PROVENANCE_STATE.admissible_provenance",
    )
    _validate_text_array(
        provenance,
        "COGNITION_PROVENANCE_STATE.admissible_provenance",
        sorted_required=True,
    )
    if _require_text(
        cognition["llm_semantic_authority_share"],
        "COGNITION_PROVENANCE_STATE.llm_semantic_authority_share",
    ) != "0_PERCENT":
        _fail("NONZERO_LLM_SEMANTIC_AUTHORITY")
    if _require_bool(
        cognition["unknown_provenance_admissible"],
        "COGNITION_PROVENANCE_STATE.unknown_provenance_admissible",
    ):
        _fail("UNKNOWN_COGNITION_PROVENANCE_PROHIBITED")

    _require_text(value["ALLOWED_NEXT_OPERATION"], "ALLOWED_NEXT_OPERATION")
    forbidden = _require_nonempty_array(
        value["FORBIDDEN_OPERATIONS"], "FORBIDDEN_OPERATIONS"
    )
    _validate_text_array(forbidden, "FORBIDDEN_OPERATIONS", sorted_required=True)

    topology = _require_mapping(value["TOPOLOGY_COMMITMENT"], "TOPOLOGY_COMMITMENT")
    _require_exact_fields(topology, _TOPOLOGY_FIELDS, "TOPOLOGY_COMMITMENT")
    normalized_topology = {}
    for field in sorted(_TOPOLOGY_FIELDS):
        normalized_topology[field] = _require_nonnegative_int(
            topology[field], f"TOPOLOGY_COMMITMENT.{field}"
        )
    if normalized_topology != _EXPECTED_TOPOLOGY:
        _fail("TOPOLOGY_COMMITMENT_MISMATCH")

    references = _require_nonempty_array(
        value["RELEVANT_REPLAY_OR_EVIDENCE_REFERENCE"],
        "RELEVANT_REPLAY_OR_EVIDENCE_REFERENCE",
    )
    for index, reference in enumerate(references):
        item = _require_mapping(
            reference, f"RELEVANT_REPLAY_OR_EVIDENCE_REFERENCE[{index}]"
        )
        _require_exact_fields(
            item,
            _EVIDENCE_REFERENCE_FIELDS,
            f"RELEVANT_REPLAY_OR_EVIDENCE_REFERENCE[{index}]",
        )
        _require_text(
            item["artifact_id"],
            f"RELEVANT_REPLAY_OR_EVIDENCE_REFERENCE[{index}].artifact_id",
        )
        _require_git_oid(
            item["git_blob"],
            f"RELEVANT_REPLAY_OR_EVIDENCE_REFERENCE[{index}].git_blob",
        )
        _require_git_oid(
            item["git_commit"],
            f"RELEVANT_REPLAY_OR_EVIDENCE_REFERENCE[{index}].git_commit",
        )
        _require_repository_path(
            item["repository_path"],
            f"RELEVANT_REPLAY_OR_EVIDENCE_REFERENCE[{index}].repository_path",
        )
        _require_sha256(
            item["sha256"],
            f"RELEVANT_REPLAY_OR_EVIDENCE_REFERENCE[{index}].sha256",
        )
    _require_sorted_unique(references, "RELEVANT_REPLAY_OR_EVIDENCE_REFERENCE")

    stop_conditions = _require_nonempty_array(
        value["STOP_FAIL_CLOSED_CONDITIONS"], "STOP_FAIL_CLOSED_CONDITIONS"
    )
    _validate_text_array(
        stop_conditions, "STOP_FAIL_CLOSED_CONDITIONS", sorted_required=True
    )


def _authenticate_repository_sources(
    payload: Mapping[str, Any],
    *,
    repository_root: str | Path,
    expected_head: str,
) -> Path:
    root = Path(repository_root).resolve()
    if not root.is_dir():
        _fail("REPOSITORY_ROOT_UNAVAILABLE")
    expected = _require_git_oid(expected_head, "expected_head")
    top_level = Path(_git_text(root, "rev-parse", "--show-toplevel")).resolve()
    if top_level != root:
        _fail("REPOSITORY_ROOT_MISMATCH")
    if _git_text(root, "rev-parse", "HEAD") != expected:
        _fail("STALE_OR_WRONG_EXPECTED_HEAD")
    if _git_bytes(root, "status", "--porcelain"):
        _fail("REPOSITORY_NOT_CLEAN")

    identity = payload["PREDECESSOR_GIT_IDENTITY"]
    if identity["commit"] != expected:
        _fail("WRONG_PREDECESSOR_COMMIT")
    actual_tree = _git_text(root, "rev-parse", f"{expected}^{{tree}}")
    if identity["tree"] != actual_tree:
        _fail("PREDECESSOR_TREE_MISMATCH")
    actual_parents_text = _git_text(root, "show", "-s", "--format=%P", expected)
    actual_parents = actual_parents_text.split() if actual_parents_text else []
    if identity["parents"] != actual_parents:
        _fail("PREDECESSOR_PARENT_MISMATCH")
    if identity["subject"] != _git_text(root, "show", "-s", "--format=%s", expected):
        _fail("PREDECESSOR_SUBJECT_MISMATCH")

    predecessor_path = payload["PREDECESSOR_ID"]["repository_path"]
    _predecessor_blob, predecessor_bytes = _read_blob_at(
        root, expected, predecessor_path
    )
    if payload["PREDECESSOR_SHA256"] != _sha256_bytes(predecessor_bytes):
        _fail("PREDECESSOR_SHA256_MISMATCH")

    for reference in payload["RELEVANT_REPLAY_OR_EVIDENCE_REFERENCE"]:
        reference_commit = reference["git_commit"]
        if not _is_ancestor(root, reference_commit, expected):
            _fail("DIVERGENT_EVIDENCE_LINEAGE")
        actual_blob, source_bytes = _read_blob_at(
            root, reference_commit, reference["repository_path"]
        )
        if reference["git_blob"] != actual_blob:
            _fail("EVIDENCE_GIT_BLOB_MISMATCH")
        if reference["sha256"] != _sha256_bytes(source_bytes):
            _fail("EVIDENCE_SHA256_MISMATCH")
    return root


def _read_blob_at(root: Path, commit: str, repository_path: str) -> tuple[str, bytes]:
    listing = _git_bytes(root, "ls-tree", "-r", "-z", commit, "--", repository_path)
    entries = [entry for entry in listing.split(b"\0") if entry]
    if len(entries) != 1:
        _fail("EVIDENCE_PATH_MISSING_OR_AMBIGUOUS")
    try:
        metadata, raw_path = entries[0].split(b"\t", 1)
        _mode, object_type, object_id = metadata.decode("ascii").split()
        resolved_path = raw_path.decode("utf-8")
    except (ValueError, UnicodeError) as exc:
        raise FailClosedRuntimeError("EVIDENCE_GIT_ENTRY_MALFORMED") from exc
    if object_type != "blob" or resolved_path != repository_path:
        _fail("EVIDENCE_PATH_OR_OBJECT_TYPE_MISMATCH")
    _require_git_oid(object_id, "resolved git blob")
    return object_id, _git_bytes(root, "cat-file", "blob", object_id)


def _is_ancestor(root: Path, candidate: str, expected_head: str) -> bool:
    completed = subprocess.run(
        ["git", "merge-base", "--is-ancestor", candidate, expected_head],
        cwd=root,
        check=False,
        capture_output=True,
    )
    if completed.returncode == 0:
        return True
    if completed.returncode == 1:
        return False
    _fail("EVIDENCE_LINEAGE_UNAVAILABLE")


def _git_text(root: Path, *args: str) -> str:
    try:
        return _git_bytes(root, *args).decode("utf-8").rstrip("\n")
    except UnicodeDecodeError as exc:
        raise FailClosedRuntimeError("GIT_TEXT_NOT_UTF8") from exc


def _git_bytes(root: Path, *args: str) -> bytes:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
    )
    if completed.returncode != 0:
        _fail("GIT_READ_FAILED_CLOSED")
    return completed.stdout


def _comparison_result(
    *,
    outcome: str,
    projection_hash: str | None,
    current_hash: str | None,
    failure_reason: str | None,
    repository_root: str | None,
) -> dict[str, Any]:
    if outcome not in {EQUAL, MISMATCH, FAILED_CLOSED}:
        _fail("SHADOW_OUTCOME_INVALID")
    return {
        "outcome": outcome,
        "contract_identity": CONTRACT_IDENTITY,
        "contract_version": CONTRACT_VERSION,
        "projection_hash": projection_hash,
        "authenticated_current_hash": current_hash,
        "failure_reason": failure_reason,
        "repository_root": repository_root,
        "manual_continuation_preserved": True,
        "bounded_cognition_fallback_preserved": True,
        "broader_history_reconstruction_preserved": True,
        "repair_performed": False,
        "state_invented": False,
        "semantic_advancement_performed": False,
        **_AUTHORITY_FLAGS,
    }


def _detached_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        _fail(f"{label.upper().replace(' ', '_')}_NOT_OBJECT")
    return deepcopy(dict(value))


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    return _detached_mapping(value, label)


def _require_exact_fields(
    value: Mapping[str, Any], expected: frozenset[str], label: str
) -> None:
    actual = set(value)
    if actual != expected:
        _fail(f"{label.upper().replace(' ', '_')}_FIELD_SET_MISMATCH")


def _require_array(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        _fail(f"{label.upper().replace(' ', '_')}_NOT_ARRAY")
    return value


def _require_nonempty_array(value: Any, label: str) -> list[Any]:
    result = _require_array(value, label)
    if not result:
        _fail(f"{label.upper().replace(' ', '_')}_EMPTY")
    return result


def _validate_text_array(
    values: list[Any], label: str, *, sorted_required: bool
) -> None:
    for index, value in enumerate(values):
        _require_text(value, f"{label}[{index}]")
    _require_unique(values, label)
    if sorted_required:
        _require_sorted(values, label)


def _require_unique(values: list[Any], label: str) -> None:
    encoded = [canonical_serialize(value) for value in values]
    if len(encoded) != len(set(encoded)):
        _fail(f"{label.upper().replace(' ', '_')}_DUPLICATE")


def _require_sorted(values: list[Any], label: str) -> None:
    encoded = [canonical_serialize(value) for value in values]
    if encoded != sorted(encoded):
        _fail(f"{label.upper().replace(' ', '_')}_NOT_CANONICALLY_SORTED")


def _require_sorted_unique(values: list[Any], label: str) -> None:
    _require_unique(values, label)
    _require_sorted(values, label)


def _require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(f"{label.upper().replace(' ', '_')}_INVALID_TEXT")
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        _fail(f"{label.upper().replace(' ', '_')}_CONTROL_CHARACTER")
    return value


def _require_bool(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        _fail(f"{label.upper().replace(' ', '_')}_NOT_BOOLEAN")
    return value


def _require_nonnegative_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        _fail(f"{label.upper().replace(' ', '_')}_NOT_NONNEGATIVE_INTEGER")
    return value


def _require_git_oid(value: Any, label: str) -> str:
    result = _require_text(value, label)
    if _GIT_OID.fullmatch(result) is None:
        _fail(f"{label.upper().replace(' ', '_')}_INVALID_GIT_OID")
    return result


def _require_sha256(value: Any, label: str) -> str:
    result = _require_text(value, label)
    if _SHA256.fullmatch(result) is None:
        _fail(f"{label.upper().replace(' ', '_')}_INVALID_SHA256")
    return result


def _require_repository_path(value: Any, label: str) -> str:
    result = _require_text(value, label)
    path = Path(result)
    parts = result.split("/")
    if (
        path.is_absolute()
        or "\\" in result
        or not parts
        or any(part in {"", ".", ".."} for part in parts)
    ):
        _fail(f"{label.upper().replace(' ', '_')}_INVALID_REPOSITORY_PATH")
    return result


def _sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def _fail(reason: str) -> None:
    raise FailClosedRuntimeError(reason)


__all__ = [
    "CONTRACT_IDENTITY",
    "CONTRACT_VERSION",
    "EQUAL",
    "FAILED_CLOSED",
    "MISMATCH",
    "compare_constitutional_continuation_reference_projection_shadow_v1",
]
