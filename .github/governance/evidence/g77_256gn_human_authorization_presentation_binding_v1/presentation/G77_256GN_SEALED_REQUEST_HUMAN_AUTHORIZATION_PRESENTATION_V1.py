#!/usr/bin/env python3
"""Deterministically project one sealed request into Human-facing text.

This repository-only owner grants no authority.  It imports the existing
GJ/FM canonical-byte owner, validates one exact request envelope, derives all
reviewed constitutional presentation fields from that sealed source, and
proves the rendered presentation equivalent to the request.  It contains no
launcher, QEMU, P11, receipt-writing, or production-route capability.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import re
from types import ModuleType
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
CANONICAL_OWNER_RELATIVE_PATH = (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
REQUEST_SCHEMA_RE = re.compile(
    r"^(G77_256[A-Z0-9]+)_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1$"
)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GIT_ID_RE = re.compile(r"^[0-9a-f]{40}$")
SUPPORTED_VECTORS = frozenset({
    "WRONG_ATTEMPT",
    "WRONG_INPUT",
    "WRONG_CONTRACT",
    "WRONG_PROVENANCE",
})

PRESENTATION_HEADER = "SAPIANTA SEALED AUTHORIZATION REQUEST HUMAN PRESENTATION V1"
PRESENTATION_NOTICE = (
    "NONAUTHORITY: deterministic sealed-request projection; one explicit "
    "Human decision is required."
)
PRESENTATION_BEGIN = "BEGIN CONSTITUTIONAL BINDINGS"
PRESENTATION_END = "END CONSTITUTIONAL BINDINGS"
PRESENTATION_TRAILER = (
    "DERIVATION=VALIDATED_SEALED_REQUEST_ONLY;FIELD_EQUIVALENCE=VERIFIED;"
    "CALLER_OVERRIDE=PROHIBITED"
)

REQUEST_FIELDS = {
    "schema_id",
    "recorded_at_utc",
    "request_class",
    "generation_identity",
    "operation_identity",
    "repository",
    "immutable_assets",
    "live_binding",
    "preauthorization",
    "requested_authority_semantics",
    "authorized_vector_requested",
    "request_is_authority",
    "checkpoint_is_authority",
    "resource_capacity_is_authority",
    "provider_permission_is_authority",
    "provider_permission_confirmation_count",
    "human_constitutional_authorization_count",
    "human_terminal_review_count",
    "governed_launcher_activations",
    "qemu_execution_count",
    "vm_boot_count",
    "operation_attempt_count",
    "wrong_attempt_execution_count",
    "request_count",
    "p11_entry_count",
    "pre_count",
    "post_count",
    "protected_invocation_count",
    "protected_effect_count",
    "retry_count",
    "repair_execution_count",
    "replay_execution_count",
    "auto_continuable",
    "human_review_required",
}
REPOSITORY_FIELDS = {
    "branch", "head", "tree", "remote_head", "stable_ancestry_anchor"
}
LIVE_BINDING_FIELDS = {
    "candidate_sha256",
    "context_sha256",
    "context_file_sha256",
    "canonical_argv_sha256",
    "du",
    "eb",
    "ee",
    "candidate_semantics_changed",
    "candidate_binding_regeneration_required",
    "receipt_parent",
}
PREAUTHORIZATION_FIELDS = {
    "static_readiness_file_sha256",
    "checkpoint_file_sha256",
    "checkpoint_inner_sha256",
    "checkpoint_path",
    "complete_deterministic_readiness",
    "receipt_parent_observation_file_sha256",
    "preauth_final_admission_equivalence_file_sha256",
    "preauth_final_admission_equivalence",
    "gk_receipt_parent_false_positive_blocked",
    "all_operational_counters_zero",
}
SEMANTIC_FIELDS = {
    "authorization_kind",
    "explicit",
    "fresh",
    "one_shot",
    "reusable",
    "transferable",
    "generation_bound",
    "operation_bound",
    "head_bound",
    "tree_bound",
    "candidate_bound",
    "context_bound",
    "canonical_argv_bound",
    "checkpoint_bound",
    "authorization_request_bound",
    "governed_launcher_activation_limit",
    "qemu_execution_limit",
    "vm_boot_limit",
    "operation_attempt_limit",
    "network_authorized",
    "retry_limit",
    "repair_limit",
    "replay_limit",
    "replacement_authority_authorized",
    "second_attempt_authorized",
    "successor_generation_authorized",
}
ZERO_COUNTER_FIELDS = {
    "human_constitutional_authorization_count",
    "governed_launcher_activations",
    "qemu_execution_count",
    "vm_boot_count",
    "operation_attempt_count",
    "wrong_attempt_execution_count",
    "request_count",
    "p11_entry_count",
    "pre_count",
    "post_count",
    "protected_invocation_count",
    "protected_effect_count",
    "retry_count",
    "repair_execution_count",
    "replay_execution_count",
}

# Ordered, exhaustive projection for the exact reviewed GM-shaped boundary.
PRESENTATION_FIELDS = (
    "AUTHORIZATION_REQUEST_ENVELOPE_SCHEMA",
    "AUTHORIZATION_REQUEST_SCHEMA",
    "AUTHORIZATION_REQUEST_SHA256",
    "REQUEST_CLASS",
    "GENERATION_ID",
    "OPERATION_ID",
    "AUTHORIZED_VECTOR_REQUESTED",
    "HEAD",
    "TREE",
    "CANDIDATE_SHA256",
    "CONTEXT_SHA256",
    "CANONICAL_ARGV_SHA256",
    "CHECKPOINT_SHA256",
    "AUTHORIZATION_KIND",
    "EXPLICIT",
    "FRESH",
    "ONE_SHOT",
    "REUSABLE",
    "TRANSFERABLE",
    "GENERATION_BOUND",
    "OPERATION_BOUND",
    "HEAD_BOUND",
    "TREE_BOUND",
    "CANDIDATE_BOUND",
    "CONTEXT_BOUND",
    "CANONICAL_ARGV_BOUND",
    "CHECKPOINT_BOUND",
    "AUTHORIZATION_REQUEST_BOUND",
    "GOVERNED_LAUNCHER_ACTIVATION_LIMIT",
    "QEMU_EXECUTION_LIMIT",
    "VM_BOOT_LIMIT",
    "OPERATION_ATTEMPT_LIMIT",
    "NETWORK_AUTHORIZED",
    "RETRY_LIMIT",
    "REPAIR_LIMIT",
    "REPLAY_LIMIT",
    "REPLACEMENT_AUTHORITY_AUTHORIZED",
    "SECOND_ATTEMPT_AUTHORIZED",
    "SUCCESSOR_GENERATION_AUTHORIZED",
    "REQUEST_IS_AUTHORITY",
    "CHECKPOINT_IS_AUTHORITY",
    "RESOURCE_CAPACITY_IS_AUTHORITY",
    "PROVIDER_PERMISSION_IS_AUTHORITY",
    "AUTO_CONTINUABLE",
    "HUMAN_REVIEW_REQUIRED",
)
LEGACY_WRONG_ATTEMPT_PRESENTATION_FIELDS = tuple(
    field for field in PRESENTATION_FIELDS if field != "AUTHORIZED_VECTOR_REQUESTED"
)


class PresentationBindingError(ValueError):
    """One fail-closed request/presentation binding error."""


def _fail(token: str) -> None:
    raise PresentationBindingError(token)


def _load_canonical_owner() -> ModuleType:
    path = REPOSITORY_ROOT / CANONICAL_OWNER_RELATIVE_PATH
    if path.is_symlink() or not path.is_file():
        _fail("EXISTING_GJ_FM_CANONICAL_OWNER_UNAVAILABLE")
    specification = importlib.util.spec_from_file_location(
        "g77_256gn_existing_gj_fm_canonical_owner", path
    )
    if specification is None or specification.loader is None:
        _fail("EXISTING_GJ_FM_CANONICAL_OWNER_IMPORT_FAILED")
    owner = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(owner)
    return owner


def _canonical_bytes(value: Any) -> bytes:
    return _load_canonical_owner().canonical_bytes(value)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            _fail(f"DUPLICATE_JSON_KEY__{key}")
        value[key] = item
    return value


def _require_exact_fields(value: Any, fields: set[str], token: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        _fail(token)
    return value


def _require_sha256(value: Any, token: str) -> str:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        _fail(token)
    return value


def _require_git_id(value: Any, token: str) -> str:
    if not isinstance(value, str) or GIT_ID_RE.fullmatch(value) is None:
        _fail(token)
    return value


def _validate_request_semantics(envelope: dict[str, Any]) -> None:
    request = _require_exact_fields(
        envelope["request"], REQUEST_FIELDS, "SEALED_REQUEST_FIELDS_INVALID"
    )
    schema_match = REQUEST_SCHEMA_RE.fullmatch(request.get("schema_id", ""))
    if schema_match is None:
        _fail("SEALED_REQUEST_SCHEMA_INVALID")
    expected_envelope_schema = f"{schema_match.group(1)}_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_ENVELOPE_V1"
    if envelope["schema_id"] != expected_envelope_schema:
        _fail("SEALED_REQUEST_SCHEMA_CROSS_BINDING_INVALID")

    repository = _require_exact_fields(
        request["repository"], REPOSITORY_FIELDS, "SEALED_REQUEST_REPOSITORY_INVALID"
    )
    live = _require_exact_fields(
        request["live_binding"], LIVE_BINDING_FIELDS, "SEALED_REQUEST_LIVE_BINDING_INVALID"
    )
    preauthorization = _require_exact_fields(
        request["preauthorization"],
        PREAUTHORIZATION_FIELDS,
        "SEALED_REQUEST_PREAUTHORIZATION_INVALID",
    )
    semantics = _require_exact_fields(
        request["requested_authority_semantics"],
        SEMANTIC_FIELDS,
        "SEALED_REQUEST_AUTHORITY_SEMANTICS_INVALID",
    )

    for field in ("head", "tree", "remote_head", "stable_ancestry_anchor"):
        _require_git_id(repository[field], f"SEALED_REQUEST_{field.upper()}_INVALID")
    if repository["head"] != repository["remote_head"]:
        _fail("SEALED_REQUEST_LOCAL_REMOTE_HEAD_DIVERGENCE")
    for field in (
        "candidate_sha256", "context_sha256", "context_file_sha256",
        "canonical_argv_sha256",
    ):
        _require_sha256(live[field], f"SEALED_REQUEST_{field.upper()}_INVALID")
    for field in (
        "static_readiness_file_sha256", "checkpoint_file_sha256",
        "checkpoint_inner_sha256", "receipt_parent_observation_file_sha256",
        "preauth_final_admission_equivalence_file_sha256",
    ):
        _require_sha256(
            preauthorization[field], f"SEALED_REQUEST_{field.upper()}_INVALID"
        )

    if request["request_class"] != "NON_AUTHORITY__ONE_EXPLICIT_HUMAN_DECISION_REQUIRED":
        _fail("SEALED_REQUEST_CLASS_INVALID")
    if request["authorized_vector_requested"] not in SUPPORTED_VECTORS:
        _fail("SEALED_REQUEST_VECTOR_INVALID")
    if not isinstance(request["generation_identity"], str) or not request["generation_identity"]:
        _fail("SEALED_REQUEST_GENERATION_INVALID")
    if not isinstance(request["operation_identity"], str) or not request["operation_identity"]:
        _fail("SEALED_REQUEST_OPERATION_INVALID")
    if (
        request["authorized_vector_requested"] == "WRONG_INPUT"
        and "WRONG_INPUT" not in request["generation_identity"]
    ):
        _fail("SEALED_REQUEST_VECTOR_GENERATION_BINDING_INVALID")
    if (
        request["authorized_vector_requested"] == "WRONG_CONTRACT"
        and "WRONG_CONTRACT" not in request["generation_identity"]
    ):
        _fail("SEALED_REQUEST_VECTOR_GENERATION_BINDING_INVALID")
    if (
        request["authorized_vector_requested"] == "WRONG_PROVENANCE"
        and "WRONG_PROVENANCE" not in request["generation_identity"]
    ):
        _fail("SEALED_REQUEST_VECTOR_GENERATION_BINDING_INVALID")
    if preauthorization["complete_deterministic_readiness"] != "PASS":
        _fail("SEALED_REQUEST_READINESS_INVALID")
    if preauthorization["all_operational_counters_zero"] is not True:
        _fail("SEALED_REQUEST_OPERATIONAL_COUNTER_SUMMARY_INVALID")
    if live["du"] != "PASS" or live["eb"] != "PASS" or live["ee"] != "PASS":
        _fail("SEALED_REQUEST_LIVE_BINDING_VALIDATION_INVALID")
    if live["candidate_semantics_changed"] is not False:
        _fail("SEALED_REQUEST_CANDIDATE_SEMANTICS_CHANGED")

    expected_true = {
        "explicit", "fresh", "one_shot", "generation_bound", "operation_bound",
        "head_bound", "tree_bound", "candidate_bound", "context_bound",
        "canonical_argv_bound", "checkpoint_bound", "authorization_request_bound",
    }
    expected_false = {
        "reusable", "transferable", "network_authorized",
        "replacement_authority_authorized", "second_attempt_authorized",
        "successor_generation_authorized",
    }
    if any(semantics[field] is not True for field in expected_true):
        _fail("SEALED_REQUEST_REQUIRED_AUTHORITY_BINDING_DISABLED")
    if any(semantics[field] is not False for field in expected_false):
        _fail("SEALED_REQUEST_PROHIBITION_DIVERGENCE")
    if semantics["authorization_kind"] != "FRESH_HUMAN_CONSTITUTIONAL_OPERATIONAL_AUTHORIZATION":
        _fail("SEALED_REQUEST_AUTHORIZATION_KIND_INVALID")
    for field in (
        "governed_launcher_activation_limit", "qemu_execution_limit",
        "vm_boot_limit", "operation_attempt_limit",
    ):
        if semantics[field] != 1:
            _fail(f"SEALED_REQUEST_EXECUTION_BOUND_INVALID__{field}")
    for field in ("retry_limit", "repair_limit", "replay_limit"):
        if semantics[field] != 0:
            _fail(f"SEALED_REQUEST_PROHIBITION_LIMIT_INVALID__{field}")
    for field in ZERO_COUNTER_FIELDS:
        if request[field] != 0:
            _fail(f"SEALED_REQUEST_OPERATIONAL_COUNTER_NONZERO__{field}")
    for field in (
        "request_is_authority", "checkpoint_is_authority",
        "resource_capacity_is_authority", "provider_permission_is_authority",
        "auto_continuable",
    ):
        if request[field] is not False:
            _fail(f"SEALED_REQUEST_NONAUTHORITY_BOUNDARY_INVALID__{field}")
    if request["human_review_required"] is not True:
        _fail("SEALED_REQUEST_HUMAN_REVIEW_BOUNDARY_INVALID")


def load_validated_sealed_request(path: Path) -> dict[str, Any]:
    """Load unique-key canonical JSON and verify its inner request seal."""

    request_path = Path(path)
    if request_path.is_symlink() or not request_path.is_file():
        _fail("SEALED_REQUEST_PATH_INVALID")
    try:
        raw = request_path.read_bytes()
        envelope = json.loads(
            raw,
            object_pairs_hook=_unique_object,
            parse_constant=lambda value: _fail(f"NON_FINITE_JSON__{value}"),
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PresentationBindingError("SEALED_REQUEST_MALFORMED") from exc
    if not isinstance(envelope, dict) or set(envelope) != {
        "schema_id", "request", "request_sha256"
    }:
        _fail("SEALED_REQUEST_ENVELOPE_FIELDS_INVALID")
    if raw != _canonical_bytes(envelope):
        _fail("SEALED_REQUEST_NOT_UNIQUE_KEY_CANONICAL_JSON")
    _require_sha256(envelope["request_sha256"], "SEALED_REQUEST_INNER_SEAL_MALFORMED")
    calculated = hashlib.sha256(_canonical_bytes(envelope["request"])).hexdigest()
    if envelope["request_sha256"] != calculated:
        _fail("SEALED_REQUEST_INNER_SEAL_INVALID")
    _validate_request_semantics(envelope)
    return envelope


def _project(envelope: dict[str, Any]) -> dict[str, Any]:
    request = envelope["request"]
    repository = request["repository"]
    live = request["live_binding"]
    preauthorization = request["preauthorization"]
    semantics = request["requested_authority_semantics"]
    projection = {
        "AUTHORIZATION_REQUEST_ENVELOPE_SCHEMA": envelope["schema_id"],
        "AUTHORIZATION_REQUEST_SCHEMA": request["schema_id"],
        "AUTHORIZATION_REQUEST_SHA256": envelope["request_sha256"],
        "REQUEST_CLASS": request["request_class"],
        "GENERATION_ID": request["generation_identity"],
        "OPERATION_ID": request["operation_identity"],
        "AUTHORIZED_VECTOR_REQUESTED": request["authorized_vector_requested"],
        "HEAD": repository["head"],
        "TREE": repository["tree"],
        "CANDIDATE_SHA256": live["candidate_sha256"],
        "CONTEXT_SHA256": live["context_sha256"],
        "CANONICAL_ARGV_SHA256": live["canonical_argv_sha256"],
        "CHECKPOINT_SHA256": preauthorization["checkpoint_inner_sha256"],
        "AUTHORIZATION_KIND": semantics["authorization_kind"],
        "EXPLICIT": semantics["explicit"],
        "FRESH": semantics["fresh"],
        "ONE_SHOT": semantics["one_shot"],
        "REUSABLE": semantics["reusable"],
        "TRANSFERABLE": semantics["transferable"],
        "GENERATION_BOUND": semantics["generation_bound"],
        "OPERATION_BOUND": semantics["operation_bound"],
        "HEAD_BOUND": semantics["head_bound"],
        "TREE_BOUND": semantics["tree_bound"],
        "CANDIDATE_BOUND": semantics["candidate_bound"],
        "CONTEXT_BOUND": semantics["context_bound"],
        "CANONICAL_ARGV_BOUND": semantics["canonical_argv_bound"],
        "CHECKPOINT_BOUND": semantics["checkpoint_bound"],
        "AUTHORIZATION_REQUEST_BOUND": semantics["authorization_request_bound"],
        "GOVERNED_LAUNCHER_ACTIVATION_LIMIT": semantics["governed_launcher_activation_limit"],
        "QEMU_EXECUTION_LIMIT": semantics["qemu_execution_limit"],
        "VM_BOOT_LIMIT": semantics["vm_boot_limit"],
        "OPERATION_ATTEMPT_LIMIT": semantics["operation_attempt_limit"],
        "NETWORK_AUTHORIZED": semantics["network_authorized"],
        "RETRY_LIMIT": semantics["retry_limit"],
        "REPAIR_LIMIT": semantics["repair_limit"],
        "REPLAY_LIMIT": semantics["replay_limit"],
        "REPLACEMENT_AUTHORITY_AUTHORIZED": semantics["replacement_authority_authorized"],
        "SECOND_ATTEMPT_AUTHORIZED": semantics["second_attempt_authorized"],
        "SUCCESSOR_GENERATION_AUTHORIZED": semantics["successor_generation_authorized"],
        "REQUEST_IS_AUTHORITY": request["request_is_authority"],
        "CHECKPOINT_IS_AUTHORITY": request["checkpoint_is_authority"],
        "RESOURCE_CAPACITY_IS_AUTHORITY": request["resource_capacity_is_authority"],
        "PROVIDER_PERMISSION_IS_AUTHORITY": request["provider_permission_is_authority"],
        "AUTO_CONTINUABLE": request["auto_continuable"],
        "HUMAN_REVIEW_REQUIRED": request["human_review_required"],
    }
    if tuple(projection) != PRESENTATION_FIELDS:
        _fail("PRESENTATION_PROJECTION_FIELD_SET_INVALID")
    return projection


def _render_projection(
    projection: dict[str, Any], fields: tuple[str, ...]
) -> bytes:
    binding_lines = [
        f"{field} {json.dumps(projection[field], ensure_ascii=False, allow_nan=False)}"
        for field in fields
    ]
    lines = [
        PRESENTATION_HEADER,
        PRESENTATION_NOTICE,
        PRESENTATION_BEGIN,
        *binding_lines,
        PRESENTATION_END,
        PRESENTATION_TRAILER,
    ]
    return ("\n".join(lines) + "\n").encode("utf-8")


def render_human_authorization_presentation(request_path: Path) -> bytes:
    """Render only from the sealed path; no constitutional override exists."""

    projection = _project(load_validated_sealed_request(request_path))
    return _render_projection(projection, PRESENTATION_FIELDS)


def parse_human_authorization_presentation(raw: bytes) -> dict[str, Any]:
    """Parse one exact deterministic presentation and reject ambiguity."""

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PresentationBindingError("PRESENTATION_UTF8_INVALID") from exc
    if not text.endswith("\n") or text.endswith("\n\n"):
        _fail("PRESENTATION_TERMINATOR_INVALID")
    lines = text[:-1].split("\n")
    field_sets = {
        len(PRESENTATION_FIELDS) + 5: PRESENTATION_FIELDS,
        len(LEGACY_WRONG_ATTEMPT_PRESENTATION_FIELDS) + 5: (
            LEGACY_WRONG_ATTEMPT_PRESENTATION_FIELDS
        ),
    }
    fields = field_sets.get(len(lines))
    if fields is None:
        _fail("PRESENTATION_STRUCTURE_INVALID")
    if lines[:3] != [PRESENTATION_HEADER, PRESENTATION_NOTICE, PRESENTATION_BEGIN]:
        _fail("PRESENTATION_PREAMBLE_INVALID")
    if lines[-2:] != [PRESENTATION_END, PRESENTATION_TRAILER]:
        _fail("PRESENTATION_POSTAMBLE_INVALID")

    parsed: dict[str, Any] = {}
    for expected_field, line in zip(fields, lines[3:-2], strict=True):
        field, separator, encoded = line.partition(" ")
        if not separator or not field or not encoded:
            _fail("PRESENTATION_BINDING_MALFORMED")
        if field in parsed:
            _fail(f"PRESENTATION_BINDING_DUPLICATE__{field}")
        if field != expected_field:
            if field in fields:
                _fail(f"PRESENTATION_BINDING_DUPLICATE_OR_OUT_OF_ORDER__{field}")
            _fail(f"PRESENTATION_BINDING_UNKNOWN_OR_AMBIGUOUS__{field}")
        try:
            value = json.loads(encoded, parse_constant=lambda item: _fail(
                f"PRESENTATION_NON_FINITE_VALUE__{item}"
            ))
        except json.JSONDecodeError as exc:
            raise PresentationBindingError(
                f"PRESENTATION_BINDING_VALUE_MALFORMED__{field}"
            ) from exc
        if json.dumps(value, ensure_ascii=False, allow_nan=False) != encoded:
            _fail(f"PRESENTATION_BINDING_VALUE_NONCANONICAL__{field}")
        parsed[field] = value
    if tuple(parsed) != fields:
        _fail("PRESENTATION_BINDING_SET_INCOMPLETE")
    return parsed


def validate_human_authorization_presentation(
    request_path: Path,
    presentation: bytes,
) -> dict[str, Any]:
    """Prove exact request/presentation equivalence and deterministic bytes."""

    envelope = load_validated_sealed_request(request_path)
    complete_projection = _project(envelope)
    observed = parse_human_authorization_presentation(presentation)
    fields = tuple(observed)
    if fields == LEGACY_WRONG_ATTEMPT_PRESENTATION_FIELDS:
        if envelope["request"]["authorized_vector_requested"] != "WRONG_ATTEMPT":
            _fail("LEGACY_PRESENTATION_VECTOR_INVALID")
    elif fields != PRESENTATION_FIELDS:
        _fail("PRESENTATION_BINDING_SET_INCOMPLETE")
    expected = {field: complete_projection[field] for field in fields}
    if observed != expected:
        divergent = next(
            field for field in fields
            if observed.get(field) != expected.get(field)
        )
        _fail(f"PRESENTATION_REQUEST_FIELD_DIVERGENCE__{divergent}")
    deterministic = _render_projection(complete_projection, fields)
    if presentation != deterministic:
        _fail("PRESENTATION_POST_DERIVATION_MUTATION")
    return {
        "human_presentation_request_equivalence": (
            "VERIFIED_WITHIN_EXACT_REVIEWED_AUTHORIZATION_BINDING_BOUNDARY"
        ),
        "human_presentation_caller_override_blocked": True,
        "request_sha256": envelope["request_sha256"],
        "presentation_sha256": hashlib.sha256(presentation).hexdigest(),
        "reviewed_field_count": len(fields),
        "human_constitutional_authorization_count": 0,
        "operational_execution_count": 0,
        "qemu_execution_count": 0,
    }
