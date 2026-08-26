#!/usr/bin/env python3
"""Fail-closed SPCE continuation-manifest V1 producer/consumer validator."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any


ENVELOPE_SCHEMA_ID = "SAPIANTA_SPCE_CONTINUATION_MANIFEST_ENVELOPE_V1"
MANIFEST_SCHEMA_ID = "SAPIANTA_SPCE_CONTINUATION_MANIFEST_V1"
SCHEMA_IDENTITY = "SAPIANTA_SPCE_CONTINUATION_MANIFEST_SCHEMA_V1"
MANIFEST_VERSION = "1.0.0"
SCHEMA_RELATIVE_PATH = (
    ".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/"
    "G77_256DU_CANONICAL_CONTINUATION_MANIFEST_SCHEMA_V1.json"
)
SCHEMA_SHA256 = "a21ba1567c65101a5f178afdfefb5d500c97fc2cc6a9eb9da6c9fb4cc914478e"
PRODUCER_IDENTITY = "G77_256DU_CANONICAL_MANIFEST_PRODUCER_V1"
CONSUMER_IDENTITY = "G77_256DU_PRE_MATERIALIZATION_CONSUMER_VALIDATOR_V1"
REQUIRED_PROHIBITED_ACTIONS = frozenset({
    "VM_CREATION",
    "VM_BOOT",
    "HUMAN_OPERATIONAL_ACT_CREATION",
    "P11_ENTRY",
    "P12_ENTRY",
    "E05_EXECUTION",
    "PRODUCTION_ROUTE",
    "EXECUTION_REPLAY",
})

ENVELOPE_FIELDS = frozenset({"schema_id", "manifest", "manifest_sha256"})
REQUIRED_MANIFEST_FIELDS = frozenset({
    "schema_id",
    "manifest_version",
    "generation_identity",
    "required_head",
    "source_tree",
    "current_spce_phase",
    "phase_sequence",
    "prior_manifest_sha256",
    "completed_phase_seals",
    "execution_counters",
    "case_counters",
    "authority_state",
    "lineage_bindings",
    "producer_binding",
    "consumer_binding",
    "schema_binding",
    "frontier_state",
    "selected_case",
    "first_failure_or_current_result",
    "teardown_state",
    "final_execution_seal",
    "prohibited_actions",
    "checkpoint_is_authority",
    "manifest_is_authority",
    "auto_continuable",
})
OPTIONAL_MANIFEST_FIELDS = frozenset({"observations", "extension_bindings"})
MANIFEST_FIELDS = REQUIRED_MANIFEST_FIELDS | OPTIONAL_MANIFEST_FIELDS

EXECUTION_COUNTER_FIELDS = frozenset({
    "vm_creation_count",
    "vm_boot_count",
    "second_vm_count",
    "automatic_retry_count",
    "repair_and_continue_count",
    "commissioning_execution_count",
    "commissioning_pass_count",
    "human_operational_act_created_count",
    "human_operational_act_submitted_count",
    "human_operational_act_claimed_count",
    "human_operational_act_invoked_count",
    "human_operational_act_terminally_bound_count",
    "human_operational_act_permanently_exhausted_count",
    "p11_entry_count",
    "p11_operational_invocation_count",
    "p12_entry_count",
    "production_route_count",
    "full_history_reconstruction_count",
    "execution_replay_count",
})

AUTHORITY_FIELDS = frozenset({
    "lifecycle_state",
    "act_identity",
    "owner_revision",
    "authority_survives",
    "transferable",
    "reusable",
})
AUTHORITY_STATES = frozenset({
    "NOT_CREATED",
    "AUTHORIZED_NOT_CREATED",
    "AVAILABLE",
    "CLAIMED",
    "CONSUMED",
    "RECONCILIATION_REQUIRED",
    "REVOKED",
    "SUPERSEDED",
    "EXPIRED",
    "NO_AUTHORITY_SURVIVES",
})
LIVE_AUTHORITY_STATES = frozenset({"AVAILABLE", "CLAIMED"})
NO_ACT_STATES = frozenset({
    "NOT_CREATED", "AUTHORIZED_NOT_CREATED", "NO_AUTHORITY_SURVIVES"
})
TERMINAL_AUTHORITY_STATES = AUTHORITY_STATES - LIVE_AUTHORITY_STATES - NO_ACT_STATES

FRONTIER_FIELDS = frozenset({
    "constitutional_frontier",
    "exact_next_legal_action",
    "continuation_mode",
    "requires_human_review",
})
CONTINUATION_MODES = frozenset({
    "PRE_MATERIALIZATION_VALIDATION_ONLY",
    "SAME_LIVE_GENERATION_ONLY",
    "FINALIZATION_ONLY",
    "HUMAN_REVIEW_ONLY",
})
TEARDOWN_STATES = frozenset({"NOT_APPLICABLE", "PENDING", "COMPLETE", "FAILED"})
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GIT_OBJECT_RE = re.compile(r"^[0-9a-f]{40}$")
CASE_COUNTER_RE = re.compile(r"^[a-z][a-z0-9_]*_count$")


class CompatibilityError(ValueError):
    """One deterministic pre-materialization compatibility rejection."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    ).encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _duplicate_free_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise CompatibilityError("DUPLICATE_KEY", f"duplicate JSON key: {key}")
        value[key] = item
    return value


def _reject_nonfinite(value: str) -> None:
    raise CompatibilityError("JSON_NONFINITE_NUMBER", f"forbidden JSON constant: {value}")


def load_json_bytes(value: bytes) -> Any:
    try:
        return json.loads(
            value,
            object_pairs_hook=_duplicate_free_object,
            parse_constant=_reject_nonfinite,
        )
    except UnicodeDecodeError as exc:
        raise CompatibilityError("UTF8_INVALID", "manifest is not UTF-8") from exc
    except json.JSONDecodeError as exc:
        raise CompatibilityError("JSON_INVALID", "manifest is not JSON") from exc


def _fail(code: str, message: str) -> None:
    raise CompatibilityError(code, message)


def _object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail("WRONG_TYPE", f"{field} must be an object")
    return value


def _array(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        _fail("WRONG_TYPE", f"{field} must be an array")
    return value


def _string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        _fail("WRONG_TYPE", f"{field} must be a non-empty string")
    return value


def _integer(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        _fail("WRONG_TYPE", f"{field} must be a non-negative integer")
    return value


def _boolean(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        _fail("WRONG_TYPE", f"{field} must be boolean")
    return value


def _sha256(value: Any, field: str) -> str:
    text = _string(value, field)
    if SHA256_RE.fullmatch(text) is None:
        _fail("HASH_FORMAT_INVALID", f"{field} must be lowercase SHA-256")
    return text


def _git_object(value: Any, field: str) -> str:
    text = _string(value, field)
    if GIT_OBJECT_RE.fullmatch(text) is None:
        _fail("GIT_OBJECT_INVALID", f"{field} must be a 40-character Git object")
    return text


def _exact_fields(
    value: dict[str, Any], required: frozenset[str], optional: frozenset[str], field: str
) -> None:
    missing = required - value.keys()
    unknown = value.keys() - required - optional
    if missing:
        _fail("REQUIRED_FIELD_ABSENT", f"{field} missing {sorted(missing)}")
    if unknown:
        _fail("UNKNOWN_FIELD", f"{field} has unknown fields {sorted(unknown)}")


def _repository_path(repository_root: Path, raw_path: Any, field: str) -> Path:
    text = _string(raw_path, field)
    relative = Path(text)
    if relative.is_absolute() or ".." in relative.parts:
        _fail("PATH_OUTSIDE_REPOSITORY", f"{field} must be repository-relative")
    root = repository_root.resolve()
    path = (root / relative).resolve()
    try:
        path.relative_to(root)
    except ValueError:
        _fail("PATH_OUTSIDE_REPOSITORY", f"{field} escapes repository")
    if not path.is_file():
        _fail("BOUND_FILE_ABSENT", f"{field} does not identify a file")
    return path


def _validate_file_binding(
    value: Any,
    repository_root: Path,
    field: str,
    *,
    schema: bool = False,
    expected_identity: str | None = None,
    expected_path: str | None = None,
    expected_sha256: str | None = None,
) -> dict[str, Any]:
    binding = _object(value, field)
    required = {"identity", "path", "sha256"}
    if schema:
        required.add("version")
    _exact_fields(binding, frozenset(required), frozenset(), field)
    identity = _string(binding["identity"], f"{field}.identity")
    if expected_identity is not None and identity != expected_identity:
        _fail("IMPLEMENTATION_BINDING_MISMATCH", f"{field} identity mismatch")
    if schema:
        if binding["identity"] != SCHEMA_IDENTITY or binding["version"] != MANIFEST_VERSION:
            _fail("SCHEMA_VERSION_INCOMPATIBLE", f"{field} identity/version mismatch")
    if expected_path is not None and binding["path"] != expected_path:
        _fail("IMPLEMENTATION_BINDING_MISMATCH", f"{field} path mismatch")
    path = _repository_path(repository_root, binding["path"], f"{field}.path")
    expected = _sha256(binding["sha256"], f"{field}.sha256")
    if expected_sha256 is not None and expected != expected_sha256:
        _fail("IMPLEMENTATION_BINDING_MISMATCH", f"{field} digest mismatch")
    if sha256_path(path) != expected:
        _fail("BOUND_FILE_HASH_MISMATCH", f"{field} SHA-256 mismatch")
    return binding


def _validate_seal_binding(
    value: Any, repository_root: Path, field: str
) -> dict[str, Any]:
    binding = _object(value, field)
    required = frozenset({"identity", "path", "inner_sha256", "file_sha256"})
    _exact_fields(binding, required, frozenset(), field)
    _string(binding["identity"], f"{field}.identity")
    path = _repository_path(repository_root, binding["path"], f"{field}.path")
    file_sha = _sha256(binding["file_sha256"], f"{field}.file_sha256")
    inner_sha = _sha256(binding["inner_sha256"], f"{field}.inner_sha256")
    if sha256_path(path) != file_sha:
        _fail("COMPLETED_SEAL_FILE_HASH_MISMATCH", f"{field} file hash mismatch")
    envelope = load_json_bytes(path.read_bytes())
    if not isinstance(envelope, dict) or set(envelope) != {"schema_id", "seal", "seal_sha256"}:
        _fail("COMPLETED_SEAL_ENVELOPE_INVALID", f"{field} envelope shape invalid")
    recomputed = sha256_bytes(canonical_bytes(envelope["seal"]))
    if envelope["seal_sha256"] != inner_sha or recomputed != inner_sha:
        _fail("COMPLETED_SEAL_AUTHENTICATION_FAILED", f"{field} inner seal mismatch")
    return binding


def _validate_lineage_binding(
    value: Any, repository_root: Path, field: str
) -> dict[str, Any]:
    binding = _object(value, field)
    required = frozenset({"identity", "path", "sha256", "git_blob"})
    _exact_fields(binding, required, frozenset(), field)
    _string(binding["identity"], f"{field}.identity")
    path = _repository_path(repository_root, binding["path"], f"{field}.path")
    expected_sha = _sha256(binding["sha256"], f"{field}.sha256")
    expected_blob = _git_object(binding["git_blob"], f"{field}.git_blob")
    relative = str(path.relative_to(repository_root.resolve()))
    try:
        committed_blob = subprocess.check_output(
            ["git", "rev-parse", f"HEAD:{relative}"], cwd=repository_root, text=True
        ).strip()
        worktree_blob = subprocess.check_output(
            ["git", "hash-object", relative], cwd=repository_root, text=True
        ).strip()
    except subprocess.CalledProcessError as exc:
        raise CompatibilityError(
            "LINEAGE_GIT_AUTHENTICATION_FAILED", f"{field} is not committed at HEAD"
        ) from exc
    if sha256_path(path) != expected_sha or committed_blob != expected_blob:
        _fail("LINEAGE_BINDING_MISMATCH", f"{field} committed identity mismatch")
    if worktree_blob != committed_blob:
        _fail("LINEAGE_WORKTREE_MISMATCH", f"{field} differs from committed bytes")
    return binding


def _validate_counters(value: Any, field: str) -> dict[str, int]:
    counters = _object(value, field)
    _exact_fields(counters, EXECUTION_COUNTER_FIELDS, frozenset(), field)
    for key, item in counters.items():
        _integer(item, f"{field}.{key}")
    if counters["vm_boot_count"] > counters["vm_creation_count"]:
        _fail("COUNTER_SEMANTICS_INVALID", "VM boot count exceeds creation count")
    if counters["commissioning_pass_count"] > counters["commissioning_execution_count"]:
        _fail("COUNTER_SEMANTICS_INVALID", "commissioning pass count exceeds execution count")
    if counters["p11_operational_invocation_count"] > counters["p11_entry_count"]:
        _fail("COUNTER_SEMANTICS_INVALID", "P11 invocation count exceeds entry count")
    return counters


def _validate_case_counters(value: Any) -> dict[str, int]:
    counters = _object(value, "manifest.case_counters")
    for key, item in counters.items():
        if CASE_COUNTER_RE.fullmatch(key) is None:
            _fail("CASE_COUNTER_NAME_INVALID", f"invalid case counter: {key}")
        _integer(item, f"manifest.case_counters.{key}")
    return counters


def _validate_authority(value: Any) -> dict[str, Any]:
    authority = _object(value, "manifest.authority_state")
    _exact_fields(authority, AUTHORITY_FIELDS, frozenset(), "manifest.authority_state")
    state = _string(authority["lifecycle_state"], "authority lifecycle state")
    if state not in AUTHORITY_STATES:
        _fail("AUTHORITY_STATE_INVALID", "unknown authority lifecycle state")
    survives = _boolean(authority["authority_survives"], "authority_survives")
    if authority["transferable"] is not False or authority["reusable"] is not False:
        _fail("AUTHORITY_SEMANTICS_INVALID", "manifest authority cannot transfer or reuse")
    act = authority["act_identity"]
    revision = authority["owner_revision"]
    if state in NO_ACT_STATES:
        if act is not None or revision is not None or survives:
            _fail("AUTHORITY_SEMANTICS_INVALID", "no-act state has live authority fields")
    else:
        _string(act, "authority act_identity")
        _integer(revision, "authority owner_revision")
        if (state in LIVE_AUTHORITY_STATES) != survives:
            _fail("AUTHORITY_SEMANTICS_INVALID", "authority survival disagrees with state")
        if state in TERMINAL_AUTHORITY_STATES and survives:
            _fail("AUTHORITY_SEMANTICS_INVALID", "terminal authority survives")
    return authority


def validate_envelope(
    envelope: Any,
    repository_root: Path,
    *,
    prior_envelope: dict[str, Any] | None = None,
    expected_head: str | None = None,
    required_prohibited_actions: frozenset[str] = frozenset(),
) -> dict[str, str]:
    required_prohibited_actions = (
        REQUIRED_PROHIBITED_ACTIONS | required_prohibited_actions
    )
    value = _object(envelope, "envelope")
    _exact_fields(value, ENVELOPE_FIELDS, frozenset(), "envelope")
    if value["schema_id"] != ENVELOPE_SCHEMA_ID:
        _fail("SCHEMA_VERSION_INCOMPATIBLE", "envelope schema identity mismatch")
    manifest = _object(value["manifest"], "manifest")
    _exact_fields(manifest, REQUIRED_MANIFEST_FIELDS, OPTIONAL_MANIFEST_FIELDS, "manifest")
    if manifest["schema_id"] != MANIFEST_SCHEMA_ID or manifest["manifest_version"] != MANIFEST_VERSION:
        _fail("SCHEMA_VERSION_INCOMPATIBLE", "manifest schema identity/version mismatch")
    embedded = _sha256(value["manifest_sha256"], "manifest_sha256")
    recomputed = sha256_bytes(canonical_bytes(manifest))
    if embedded != recomputed:
        _fail("CRYPTOGRAPHIC_AUTHENTICITY_FAILED", "manifest digest mismatch")
    _string(manifest["generation_identity"], "generation_identity")
    head = _git_object(manifest["required_head"], "required_head")
    source_tree = _git_object(manifest["source_tree"], "source_tree")
    if expected_head is not None and head != expected_head:
        _fail("REQUIRED_HEAD_MISMATCH", "manifest required HEAD differs")
    try:
        required_tree = subprocess.check_output(
            ["git", "rev-parse", f"{head}^{{tree}}"],
            cwd=repository_root,
            text=True,
        ).strip()
    except subprocess.CalledProcessError as exc:
        raise CompatibilityError(
            "REQUIRED_HEAD_UNAUTHENTICATED", "manifest required HEAD is unavailable"
        ) from exc
    if source_tree != required_tree:
        _fail("SOURCE_TREE_MISMATCH", "source tree does not belong to required HEAD")
    _string(manifest["current_spce_phase"], "current_spce_phase")
    _integer(manifest["phase_sequence"], "phase_sequence")
    prior_digest = manifest["prior_manifest_sha256"]
    if prior_digest is not None:
        _sha256(prior_digest, "prior_manifest_sha256")

    completed = _array(manifest["completed_phase_seals"], "completed_phase_seals")
    completed_bindings = [
        _validate_seal_binding(item, repository_root, f"completed_phase_seals[{index}]")
        for index, item in enumerate(completed)
    ]
    completed_ids = [item["identity"] for item in completed_bindings]
    if len(completed_ids) != len(set(completed_ids)):
        _fail("COMPLETED_SEAL_DUPLICATE", "completed seal identities must be unique")

    counters = _validate_counters(manifest["execution_counters"], "execution_counters")
    case_counters = _validate_case_counters(manifest["case_counters"])
    _validate_authority(manifest["authority_state"])

    lineage = _array(manifest["lineage_bindings"], "lineage_bindings")
    if not lineage:
        _fail("LINEAGE_EMPTY", "minimum lineage must not be empty")
    lineage_bindings = [
        _validate_lineage_binding(item, repository_root, f"lineage_bindings[{index}]")
        for index, item in enumerate(lineage)
    ]
    lineage_ids = [item["identity"] for item in lineage_bindings]
    if len(lineage_ids) != len(set(lineage_ids)):
        _fail("LINEAGE_DUPLICATE", "lineage identities must be unique")

    validator_relative = str(Path(__file__).resolve().relative_to(repository_root.resolve()))
    _validate_file_binding(
        manifest["producer_binding"],
        repository_root,
        "producer_binding",
        expected_identity=PRODUCER_IDENTITY,
        expected_path=validator_relative,
    )
    _validate_file_binding(
        manifest["consumer_binding"],
        repository_root,
        "consumer_binding",
        expected_identity=CONSUMER_IDENTITY,
        expected_path=validator_relative,
    )
    _validate_file_binding(
        manifest["schema_binding"],
        repository_root,
        "schema_binding",
        schema=True,
        expected_identity=SCHEMA_IDENTITY,
        expected_path=SCHEMA_RELATIVE_PATH,
        expected_sha256=SCHEMA_SHA256,
    )

    frontier = _object(manifest["frontier_state"], "frontier_state")
    _exact_fields(frontier, FRONTIER_FIELDS, frozenset(), "frontier_state")
    _string(frontier["constitutional_frontier"], "constitutional_frontier")
    _string(frontier["exact_next_legal_action"], "exact_next_legal_action")
    if frontier["continuation_mode"] not in CONTINUATION_MODES:
        _fail("FRONTIER_MODE_INVALID", "unknown continuation mode")
    if frontier["requires_human_review"] is not True:
        _fail("FRONTIER_SEMANTICS_INVALID", "V1 requires Human review")

    selected = manifest["selected_case"]
    if selected is not None:
        selected = _object(selected, "selected_case")
        _exact_fields(
            selected, frozenset({"case_class", "case_id"}), frozenset(), "selected_case"
        )
        _string(selected["case_class"], "selected_case.case_class")
        _string(selected["case_id"], "selected_case.case_id")
    result = manifest["first_failure_or_current_result"]
    if result is not None:
        _string(result, "first_failure_or_current_result")
    if manifest["teardown_state"] not in TEARDOWN_STATES:
        _fail("TEARDOWN_STATE_INVALID", "unknown teardown state")
    final_seal = manifest["final_execution_seal"]
    if final_seal is not None:
        _validate_seal_binding(final_seal, repository_root, "final_execution_seal")
    prohibited = _array(manifest["prohibited_actions"], "prohibited_actions")
    if any(not isinstance(item, str) or not item for item in prohibited):
        _fail("PROHIBITED_ACTION_INVALID", "prohibited actions must be non-empty strings")
    if len(prohibited) != len(set(prohibited)):
        _fail("PROHIBITED_ACTION_DUPLICATE", "prohibited actions must be unique")
    if not required_prohibited_actions.issubset(prohibited):
        _fail("CONSTITUTIONAL_ADMISSIBILITY_FAILED", "required prohibitions are absent")
    if manifest["checkpoint_is_authority"] is not False:
        _fail("AUTHORITY_SEMANTICS_INVALID", "checkpoint cannot be authority")
    if manifest["manifest_is_authority"] is not False:
        _fail("AUTHORITY_SEMANTICS_INVALID", "manifest cannot be authority")
    if manifest["auto_continuable"] is not False:
        _fail("AUTO_CONTINUABLE_INCONSISTENT", "V1 is never auto-continuable")

    observations = manifest.get("observations", [])
    if not isinstance(observations, list) or any(
        not isinstance(item, str) or not item for item in observations
    ):
        _fail("OPTIONAL_FIELD_INVALID", "observations must be non-empty strings")
    extensions = manifest.get("extension_bindings", [])
    if not isinstance(extensions, list):
        _fail("OPTIONAL_FIELD_INVALID", "extension_bindings must be an array")
    for index, item in enumerate(extensions):
        _validate_file_binding(item, repository_root, f"extension_bindings[{index}]")

    if prior_envelope is None:
        if prior_digest is not None:
            _fail("PRIOR_MANIFEST_BINDING_INVALID", "initial manifest names a prior digest")
    else:
        prior_result = validate_envelope(
            prior_envelope,
            repository_root,
            expected_head=expected_head,
            required_prohibited_actions=required_prohibited_actions,
        )
        if prior_digest != prior_envelope["manifest_sha256"]:
            _fail("PRIOR_MANIFEST_BINDING_INVALID", "prior manifest digest mismatch")
        prior = prior_envelope["manifest"]
        if manifest["generation_identity"] != prior["generation_identity"]:
            _fail("GENERATION_IDENTITY_DRIFT", "generation identity changed")
        if manifest["required_head"] != prior["required_head"]:
            _fail("REQUIRED_HEAD_MISMATCH", "required HEAD changed")
        if manifest["phase_sequence"] < prior["phase_sequence"]:
            _fail("PHASE_SEQUENCE_REGRESSION", "phase sequence regressed")
        for key, prior_value in prior["execution_counters"].items():
            if counters[key] < prior_value:
                _fail("COUNTER_REGRESSION", f"execution counter regressed: {key}")
        for key, prior_value in prior["case_counters"].items():
            if key not in case_counters or case_counters[key] < prior_value:
                _fail("COUNTER_REGRESSION", f"case counter regressed: {key}")
        if completed_bindings[: len(prior["completed_phase_seals"])] != prior[
            "completed_phase_seals"
        ]:
            _fail("COMPLETED_SEAL_REGRESSION", "completed seal prefix changed")
        if prior_result["constitutional_admissibility"] != "PASS":
            _fail("PRIOR_MANIFEST_INVALID", "prior manifest was inadmissible")

    return {
        "cryptographic_authenticity": "PASS",
        "structural_schema_validity": "PASS",
        "semantic_contract_compatibility": "PASS",
        "constitutional_admissibility": "PASS",
    }


def validate_file(
    path: Path,
    repository_root: Path,
    *,
    prior_path: Path | None = None,
    expected_head: str | None = None,
    required_prohibited_actions: frozenset[str] = frozenset(),
) -> dict[str, str]:
    raw = path.read_bytes()
    envelope = load_json_bytes(raw)
    if raw != canonical_bytes(envelope):
        _fail("CANONICAL_SERIALIZATION_INVALID", "manifest bytes are not canonical V1 JSON")
    prior = load_json_bytes(prior_path.read_bytes()) if prior_path else None
    return validate_envelope(
        envelope,
        repository_root,
        prior_envelope=prior,
        expected_head=expected_head,
        required_prohibited_actions=required_prohibited_actions,
    )


def _git(cwd: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def _lineage_binding(repository_root: Path, identity: str, relative: str) -> dict[str, str]:
    path = repository_root / relative
    return {
        "identity": identity,
        "path": relative,
        "sha256": sha256_path(path),
        "git_blob": _git(repository_root, "rev-parse", f"HEAD:{relative}"),
    }


def _seal_binding(repository_root: Path, identity: str, relative: str) -> dict[str, str]:
    path = repository_root / relative
    envelope = load_json_bytes(path.read_bytes())
    return {
        "identity": identity,
        "path": relative,
        "inner_sha256": envelope["seal_sha256"],
        "file_sha256": sha256_path(path),
    }


def zero_execution_counters() -> dict[str, int]:
    return {key: 0 for key in sorted(EXECUTION_COUNTER_FIELDS)}


def build_du_fixture(repository_root: Path) -> dict[str, Any]:
    validator_path = Path(__file__).resolve()
    validator_relative = str(validator_path.relative_to(repository_root.resolve()))
    lineage_paths = [
        (
            "G77_256DT_G48_REPORT",
            "docs/governance/G77_256DT_ONE_FRESH_BOUNDED_E05_CONCURRENCY_GENERATION_AFTER_DS_FAIL_CLOSED_RECOVERY_WITH_PRE_MATERIALIZATION_SELF_AUTHENTICATION_AND_CROSS_ACCOUNT_RESUMABLE_SPCE_EVIDENCE_V1.md",
        ),
        (
            "G77_256DT_FINAL_EXECUTION_SEAL",
            ".github/governance/evidence/g77_256dt_p11_operational_v1/G77_256DT_SPCE_FINAL_EXECUTION_SEAL_V1.json",
        ),
        (
            "G77_256DT_MATERIALIZED_MANIFEST",
            ".github/governance/evidence/g77_256dt_p11_operational_v1/raw/G77_256DT_CONTINUATION_MANIFEST_MATERIALIZED_V1.json",
        ),
        (
            "G77_256DT_HARNESS",
            ".github/governance/evidence/g77_256dt_p11_operational_v1/harness/G77_256DT_P11_OPERATIONAL_HARNESS_V1.py",
        ),
        (
            "G77_256DQ_G48_REPORT",
            "docs/governance/G77_256DQ_CROSS_ACCOUNT_SPCE_RESUMABLE_FINALIZATION_OF_COMPLETED_G2_E05_FROM_PERSISTENT_REPOSITORY_EVIDENCE_V1.md",
        ),
        (
            "G77_256DQ_TERMINAL_MANIFEST",
            ".github/governance/evidence/g77_256dq_p11_operational_v1/raw/G77_256DQ_CONTINUATION_MANIFEST_V1.json",
        ),
        (
            "G77_256DQ_HARNESS",
            ".github/governance/evidence/g77_256dq_p11_operational_v1/harness/G77_256DQ_P11_OPERATIONAL_HARNESS_V1.py",
        ),
        (
            "G77_256DP_G48_REPORT",
            "docs/governance/G77_256DP_CROSS_ACCOUNT_SPCE_RESUMABLE_FINALIZATION_FROM_PERSISTENT_EXECUTION_EVIDENCE_V1.md",
        ),
        (
            "G48_REPORTING_STANDARD",
            "docs/governance/G48_00_CONSTITUTIONAL_EVIDENCE_REPORTING_STANDARD_V1.md",
        ),
    ]
    head = _git(repository_root, "rev-parse", "HEAD")
    tree = _git(repository_root, "rev-parse", "HEAD^{tree}")
    manifest = {
        "schema_id": MANIFEST_SCHEMA_ID,
        "manifest_version": MANIFEST_VERSION,
        "generation_identity": "G77_256DU_CANONICAL_CONTINUATION_MANIFEST_CONTRACT_V1",
        "required_head": head,
        "source_tree": tree,
        "current_spce_phase": "PHASE_D_PRE_MATERIALIZATION_COMPATIBILITY_CERTIFIED",
        "phase_sequence": 0,
        "prior_manifest_sha256": None,
        "completed_phase_seals": [
            _seal_binding(
                repository_root,
                "G77_256DT_SPCE_PHASE_A_CHECKPOINT_V1",
                ".github/governance/evidence/g77_256dt_p11_operational_v1/G77_256DT_SPCE_PHASE_A_CHECKPOINT_V1.json",
            )
        ],
        "execution_counters": zero_execution_counters(),
        "case_counters": {
            "e05_case_execution_count": 0,
            "e05_concurrency_contender_count": 0,
            "e05_concurrency_loser_count": 0,
            "e05_concurrency_winner_count": 0,
        },
        "authority_state": {
            "lifecycle_state": "NOT_CREATED",
            "act_identity": None,
            "owner_revision": None,
            "authority_survives": False,
            "transferable": False,
            "reusable": False,
        },
        "lineage_bindings": [
            _lineage_binding(repository_root, identity, relative)
            for identity, relative in lineage_paths
        ],
        "producer_binding": {
            "identity": PRODUCER_IDENTITY,
            "path": validator_relative,
            "sha256": sha256_path(validator_path),
        },
        "consumer_binding": {
            "identity": CONSUMER_IDENTITY,
            "path": validator_relative,
            "sha256": sha256_path(validator_path),
        },
        "schema_binding": {
            "identity": SCHEMA_IDENTITY,
            "version": MANIFEST_VERSION,
            "path": SCHEMA_RELATIVE_PATH,
            "sha256": sha256_path(repository_root / SCHEMA_RELATIVE_PATH),
        },
        "frontier_state": {
            "constitutional_frontier": "DT_MANIFEST_PRODUCER_CONSUMER_SCHEMA_INCOMPATIBILITY_CLOSED_BY_DU_V1",
            "exact_next_legal_action": "HUMAN_REVIEW_AND_OPTIONAL_COMMIT__THEN_SEPARATE_AUTHORIZATION_FOR_ANY_FUTURE_PRE_MATERIALIZATION_GENERATION",
            "continuation_mode": "PRE_MATERIALIZATION_VALIDATION_ONLY",
            "requires_human_review": True,
        },
        "selected_case": None,
        "first_failure_or_current_result": "PASS__CANONICAL_PRODUCER_CONSUMER_COMPATIBILITY_PRE_MATERIALIZATION",
        "teardown_state": "NOT_APPLICABLE",
        "final_execution_seal": None,
        "prohibited_actions": [
            "E05_EXECUTION",
            "EXECUTION_REPLAY",
            "HUMAN_OPERATIONAL_ACT_CREATION",
            "P11_ENTRY",
            "P12_ENTRY",
            "PRODUCTION_ROUTE",
            "VM_BOOT",
            "VM_CREATION",
        ],
        "checkpoint_is_authority": False,
        "manifest_is_authority": False,
        "auto_continuable": False,
        "observations": [
            "CRYPTOGRAPHIC_AUTHENTICITY_IS_NOT_STRUCTURAL_OR_SEMANTIC_COMPATIBILITY",
            "DQ_AND_DT_CONTAINED_INCOMPATIBLE_CONTINUATION_MANIFEST_DIALECTS",
            "DP_PERSISTED_SPCE_SEALS_WITHOUT_A_CONTINUATION_MANIFEST_DIALECT",
            "CLREC_REMAINS_CANDIDATE_ONLY",
        ],
        "extension_bindings": [],
    }
    return {
        "schema_id": ENVELOPE_SCHEMA_ID,
        "manifest": manifest,
        "manifest_sha256": sha256_bytes(canonical_bytes(manifest)),
    }


def _rehash(envelope: dict[str, Any]) -> None:
    envelope["manifest_sha256"] = sha256_bytes(canonical_bytes(envelope["manifest"]))


def run_self_test(repository_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    fixture = build_du_fixture(repository_root)
    prohibitions = REQUIRED_PROHIBITED_ACTIONS
    positive = validate_envelope(
        fixture,
        repository_root,
        expected_head=fixture["manifest"]["required_head"],
        required_prohibited_actions=prohibitions,
    )
    negative_cases: list[tuple[str, str, str]] = []

    def rejected(name: str, expected_code: str, candidate: dict[str, Any], **kwargs: Any) -> None:
        try:
            validate_envelope(
                candidate,
                repository_root,
                expected_head=fixture["manifest"]["required_head"],
                required_prohibited_actions=prohibitions,
                **kwargs,
            )
        except CompatibilityError as exc:
            if exc.code != expected_code:
                raise AssertionError(f"{name}: expected {expected_code}, got {exc.code}") from exc
            negative_cases.append((name, expected_code, "PASS__REJECTED_PRE_MATERIALIZATION"))
            return
        raise AssertionError(f"{name}: incompatible candidate was accepted")

    candidate = deepcopy(fixture)
    del candidate["manifest"]["completed_phase_seals"]
    _rehash(candidate)
    rejected("MISSING_REQUIRED_FIELD", "REQUIRED_FIELD_ABSENT", candidate)

    candidate = deepcopy(fixture)
    candidate["manifest"]["execution_counters"] = "ZERO"
    _rehash(candidate)
    rejected("WRONG_FIELD_TYPE", "WRONG_TYPE", candidate)

    candidate = deepcopy(fixture)
    candidate["manifest"]["manifest_version"] = "2.0.0"
    _rehash(candidate)
    rejected("INCOMPATIBLE_SCHEMA_VERSION", "SCHEMA_VERSION_INCOMPATIBLE", candidate)

    candidate = deepcopy(fixture)
    candidate["manifest"]["completed_phase_seals"][0]["inner_sha256"] = "0" * 64
    _rehash(candidate)
    rejected(
        "UNAUTHENTICATABLE_COMPLETED_SEAL",
        "COMPLETED_SEAL_AUTHENTICATION_FAILED",
        candidate,
    )

    candidate = deepcopy(fixture)
    candidate["manifest"]["lineage_bindings"][0]["git_blob"] = "0" * 40
    _rehash(candidate)
    rejected("LINEAGE_BINDING_DIFFERENCE", "LINEAGE_BINDING_MISMATCH", candidate)

    candidate = deepcopy(fixture)
    candidate["manifest"]["authority_state"]["transferable"] = True
    _rehash(candidate)
    rejected("INVALID_AUTHORITY_SEMANTICS", "AUTHORITY_SEMANTICS_INVALID", candidate)

    prior = deepcopy(fixture)
    prior["manifest"]["execution_counters"]["vm_creation_count"] = 1
    _rehash(prior)
    candidate = deepcopy(fixture)
    candidate["manifest"]["phase_sequence"] = 1
    candidate["manifest"]["prior_manifest_sha256"] = prior["manifest_sha256"]
    _rehash(candidate)
    rejected("COUNTER_REGRESSION", "COUNTER_REGRESSION", candidate, prior_envelope=prior)

    candidate = deepcopy(fixture)
    candidate["manifest"]["auto_continuable"] = True
    _rehash(candidate)
    rejected("AUTO_CONTINUABLE_INCONSISTENCY", "AUTO_CONTINUABLE_INCONSISTENT", candidate)

    candidate = deepcopy(fixture)
    candidate["manifest"]["unknown_dialect_field"] = "FORBIDDEN"
    _rehash(candidate)
    rejected("UNKNOWN_FIELD_DRIFT", "UNKNOWN_FIELD", candidate)

    candidate = deepcopy(fixture)
    candidate["manifest_sha256"] = "0" * 64
    rejected(
        "CRYPTOGRAPHIC_DIGEST_MISMATCH",
        "CRYPTOGRAPHIC_AUTHENTICITY_FAILED",
        candidate,
    )

    evidence = {
        "schema_id": "G77_256DU_COMPATIBILITY_VALIDATION_EVIDENCE_V1",
        "required_head": fixture["manifest"]["required_head"],
        "source_tree": fixture["manifest"]["source_tree"],
        "canonical_manifest_schema_id": MANIFEST_SCHEMA_ID,
        "manifest_schema_version": MANIFEST_VERSION,
        "producer_output_sha256": sha256_bytes(canonical_bytes(fixture)),
        "producer_consumer_compatibility": "PASS",
        "positive_validation": positive,
        "negative_validation": [
            {"case": name, "expected_rejection": code, "result": result}
            for name, code, result in negative_cases
        ],
        "negative_case_count": len(negative_cases),
        "pre_materialization_failure_detection_ready": True,
        "vm_creation_count": 0,
        "vm_boot_count": 0,
        "human_operational_act_created_count": 0,
        "p11_entry_count": 0,
        "e05_case_execution_count": 0,
        "p12_entry_count": 0,
        "production_route_count": 0,
        "execution_replay_count": 0,
        "auto_continuable": False,
    }
    return fixture, evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[5])
    parser.add_argument("--validate", type=Path)
    parser.add_argument("--prior", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--fixture-output", type=Path)
    parser.add_argument("--evidence-output", type=Path)
    args = parser.parse_args()
    repository_root = args.repo_root.resolve()
    if args.self_test:
        fixture, evidence = run_self_test(repository_root)
        if args.fixture_output is not None:
            args.fixture_output.write_bytes(canonical_bytes(fixture))
        if args.evidence_output is not None:
            args.evidence_output.write_bytes(canonical_bytes(evidence))
        print(canonical_bytes(evidence).decode(), end="")
        return 0
    if args.validate is None:
        parser.error("--validate or --self-test is required")
    result = validate_file(
        args.validate,
        repository_root,
        prior_path=args.prior,
        expected_head=_git(repository_root, "rev-parse", "HEAD"),
    )
    print(canonical_bytes(result).decode(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
