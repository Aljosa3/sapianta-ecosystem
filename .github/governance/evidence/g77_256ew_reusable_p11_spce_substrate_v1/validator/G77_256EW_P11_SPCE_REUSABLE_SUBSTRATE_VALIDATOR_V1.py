#!/usr/bin/env python3
"""Repository-only validator for P11_SPCE_REUSABLE_SUBSTRATE_V1.

This validator authenticates and reduces evidence contracts. It has no launch,
VM, materialization, commissioning, P11, E05, P12, production, retry, replay,
credit, staging, commit, or push function.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
from types import ModuleType
from typing import Any, Callable


sys.dont_write_bytecode = True

EXPECTED_HEAD = "27f0e4a93a1eabb2d048c9196046b0491af8a665"
EXPECTED_TREE = "d85e34df17f9cbe06e07d68ca4b0d12be16c2d61"
EXPECTED_ENVELOPE_SCHEMA = "G77_256EW_P11_SPCE_REUSABLE_SUBSTRATE_MANIFEST_ENVELOPE_V1"
EXPECTED_MANIFEST_SCHEMA = "G77_256EW_P11_SPCE_REUSABLE_SUBSTRATE_MANIFEST_V1"
MANIFEST_FILENAME = "G77_256EW_P11_SPCE_REUSABLE_SUBSTRATE_MANIFEST_V1.json"
REPO_ROOT = Path(__file__).resolve().parents[5]
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
ALLOWED_CLASSIFICATIONS = {
    "CERTIFIED",
    "EVIDENCE_SUPPORTED",
    "REQUIRES_HARDENING",
    "VECTOR_SPECIFIC",
}
ALLOWED_BLOCKER_STATES = {
    "CLOSED",
    "PARTIALLY_CLOSED",
    "OPEN__HUMAN_AUTHORITY_REQUIRED",
    "OPEN__OPERATIONAL_EVIDENCE_REQUIRED",
}
COUNTER_FIELDS = (
    "boundary_request_count",
    "pre_attempt_denial_count",
    "p11_entry_count",
    "p11_operational_invocation_count",
    "protected_effect_count",
    "second_protected_effect_count",
)
LAUNCH_RECEIPT_FIELDS = {
    "schema_id",
    "receipt_kind",
    "launcher_identity",
    "launcher_sha256",
    "canonical_argv",
    "canonical_argv_sha256",
    "vm_generation_identity",
    "required_head",
    "required_tree",
    "pre_boot_authorization_identity",
    "pre_boot_authorization_sha256",
    "pre_boot_authorization_authenticated",
    "sequence",
    "execution_invoked",
    "exit_status",
    "receipt_is_authority",
}
CUSTODY_RECEIPT_FIELDS = {
    "schema_id",
    "policy_identity",
    "base_image_id",
    "base_image_sha256",
    "format",
    "qemu_img_check_before",
    "qemu_img_check_after",
    "read_only_observed",
    "overlay_only_mutation_observed",
    "path",
    "path_class",
    "custody_version",
    "base_image_unchanged",
    "receipt_is_authority",
}


class SubstrateValidationError(ValueError):
    """One fail-closed substrate validation error."""


def _fail(token: str) -> None:
    raise SubstrateValidationError(token)


def _object_no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            _fail(f"DUPLICATE_JSON_KEY__{key}")
        value[key] = item
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256(value: Any, token: str) -> str:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        _fail(token)
    return value


def _nonempty(value: Any, token: str) -> str:
    if not isinstance(value, str) or not value:
        _fail(token)
    return value


def load_json(path: Path) -> Any:
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_object_no_duplicate_keys,
            parse_constant=lambda value: (_ for _ in ()).throw(
                SubstrateValidationError(f"NON_FINITE_JSON__{value}")
            ),
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SubstrateValidationError(f"JSON_INVALID__{path}") from exc


def _component(manifest: dict[str, Any], identity: str) -> dict[str, Any]:
    matches = [
        item for item in manifest["component_bindings"]
        if isinstance(item, dict) and item.get("identity") == identity
    ]
    if len(matches) != 1:
        _fail(f"COMPONENT_IDENTITY_CARDINALITY_INVALID__{identity}")
    return matches[0]


def _bound_path(component: dict[str, Any]) -> Path:
    relative = Path(_nonempty(component.get("path"), "COMPONENT_PATH_INVALID"))
    if relative.is_absolute() or ".." in relative.parts:
        _fail("COMPONENT_PATH_NOT_REPOSITORY_RELATIVE")
    path = REPO_ROOT / relative
    if path.is_symlink() or not path.is_file():
        _fail(f"COMPONENT_NOT_REGULAR_FILE__{relative}")
    return path


def _load_module(component: dict[str, Any], module_name: str) -> ModuleType:
    path = _bound_path(component)
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        _fail(f"MODULE_LOAD_SPEC_INVALID__{component['identity']}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_manifest(path: Path) -> dict[str, Any]:
    envelope = load_json(path)
    if not isinstance(envelope, dict) or set(envelope) != {
        "schema_id", "manifest", "manifest_sha256"
    }:
        _fail("MANIFEST_ENVELOPE_STRUCTURE_INVALID")
    if envelope["schema_id"] != EXPECTED_ENVELOPE_SCHEMA:
        _fail("MANIFEST_ENVELOPE_SCHEMA_INVALID")
    manifest = envelope["manifest"]
    if not isinstance(manifest, dict) or manifest.get("schema_id") != EXPECTED_MANIFEST_SCHEMA:
        _fail("MANIFEST_SCHEMA_INVALID")
    preimage = copy.deepcopy(envelope)
    preimage["manifest_sha256"] = ""
    calculated = sha256_bytes(canonical_bytes(preimage))
    if envelope["manifest_sha256"] != calculated:
        _fail("MANIFEST_INNER_HASH_INVALID")
    baseline = manifest.get("required_baseline")
    if not isinstance(baseline, dict):
        _fail("REQUIRED_BASELINE_INVALID")
    if baseline.get("head") != EXPECTED_HEAD or baseline.get("tree") != EXPECTED_TREE:
        _fail("REQUIRED_BASELINE_MISMATCH")
    authority = manifest.get("authority")
    if not isinstance(authority, dict):
        _fail("AUTHORITY_BLOCK_INVALID")
    required_false = (
        "manifest_is_authority",
        "substrate_certified",
        "operational_execution_authorized",
        "e05_credit_authorized",
        "p12_authorized",
        "production_route_authorized",
        "auto_continuable",
    )
    if any(authority.get(field) is not False for field in required_false):
        _fail("AUTHORITY_FALSE_BOUNDARY_INVALID")
    return envelope


def validate_components(manifest: dict[str, Any]) -> dict[str, int]:
    components = manifest.get("component_bindings")
    if not isinstance(components, list) or not components:
        _fail("COMPONENT_BINDINGS_ABSENT")
    identities: set[str] = set()
    counts = {value: 0 for value in sorted(ALLOWED_CLASSIFICATIONS)}
    for component in components:
        if not isinstance(component, dict) or set(component) != {
            "identity", "path", "sha256", "classification", "scope", "limitation"
        }:
            _fail("COMPONENT_BINDING_STRUCTURE_INVALID")
        identity = _nonempty(component["identity"], "COMPONENT_IDENTITY_INVALID")
        if identity in identities:
            _fail(f"COMPONENT_IDENTITY_DUPLICATE__{identity}")
        identities.add(identity)
        classification = component["classification"]
        if classification not in ALLOWED_CLASSIFICATIONS:
            _fail(f"COMPONENT_CLASSIFICATION_INVALID__{identity}")
        path = _bound_path(component)
        expected = _sha256(component["sha256"], f"COMPONENT_SHA256_INVALID__{identity}")
        if sha256_bytes(path.read_bytes()) != expected:
            _fail(f"COMPONENT_HASH_MISMATCH__{identity}")
        _nonempty(component["scope"], f"COMPONENT_SCOPE_INVALID__{identity}")
        _nonempty(component["limitation"], f"COMPONENT_LIMITATION_INVALID__{identity}")
        counts[classification] += 1
    required = set(manifest.get("required_component_identities", []))
    if required != identities:
        _fail("REQUIRED_COMPONENT_IDENTITY_SET_MISMATCH")
    return counts


def validate_blockers(manifest: dict[str, Any]) -> dict[str, str]:
    blockers = manifest.get("blocker_status")
    if not isinstance(blockers, dict) or set(blockers) != {f"B{index}" for index in range(1, 7)}:
        _fail("BLOCKER_SET_INVALID")
    expected = {
        "B1": "OPEN__OPERATIONAL_EVIDENCE_REQUIRED",
        "B2": "PARTIALLY_CLOSED",
        "B3": "CLOSED",
        "B4": "CLOSED",
        "B5": "OPEN__HUMAN_AUTHORITY_REQUIRED",
        "B6": "PARTIALLY_CLOSED",
    }
    result: dict[str, str] = {}
    for identity, value in blockers.items():
        if not isinstance(value, dict) or set(value) != {"status", "basis", "remaining_requirement"}:
            _fail(f"BLOCKER_STRUCTURE_INVALID__{identity}")
        status = value["status"]
        if status not in ALLOWED_BLOCKER_STATES or status != expected[identity]:
            _fail(f"BLOCKER_STATUS_INVALID__{identity}")
        _nonempty(value["basis"], f"BLOCKER_BASIS_INVALID__{identity}")
        _nonempty(value["remaining_requirement"], f"BLOCKER_REMAINDER_INVALID__{identity}")
        result[identity] = status
    return result


def validate_legacy_matrix(manifest: dict[str, Any]) -> dict[str, int]:
    matrix = manifest.get("legacy_22_component_matrix")
    if not isinstance(matrix, dict) or set(matrix) != {
        "baseline_counts", "counts_after_ew", "classification_delta_count", "items"
    }:
        _fail("LEGACY_COMPONENT_MATRIX_STRUCTURE_INVALID")
    expected_before = {
        "CERTIFIED": 4,
        "EVIDENCE_SUPPORTED": 12,
        "REQUIRES_HARDENING": 3,
        "VECTOR_SPECIFIC": 3,
    }
    expected_after = {
        "CERTIFIED": 4,
        "EVIDENCE_SUPPORTED": 13,
        "REQUIRES_HARDENING": 2,
        "VECTOR_SPECIFIC": 3,
    }
    if matrix["baseline_counts"] != expected_before or matrix["counts_after_ew"] != expected_after:
        _fail("LEGACY_COMPONENT_MATRIX_COUNTS_INVALID")
    items = matrix["items"]
    if not isinstance(items, list) or len(items) != 22:
        _fail("LEGACY_COMPONENT_MATRIX_ITEM_COUNT_INVALID")
    if {item.get("id") for item in items if isinstance(item, dict)} != set(range(1, 23)):
        _fail("LEGACY_COMPONENT_MATRIX_IDENTIFIERS_INVALID")
    before_counts = {value: 0 for value in ALLOWED_CLASSIFICATIONS}
    after_counts = {value: 0 for value in ALLOWED_CLASSIFICATIONS}
    changed: list[int] = []
    for item in items:
        if not isinstance(item, dict) or set(item) != {
            "id", "component", "classification_before", "classification_after", "delta_basis"
        }:
            _fail("LEGACY_COMPONENT_MATRIX_ITEM_STRUCTURE_INVALID")
        before = item["classification_before"]
        after = item["classification_after"]
        if before not in ALLOWED_CLASSIFICATIONS or after not in ALLOWED_CLASSIFICATIONS:
            _fail(f"LEGACY_COMPONENT_CLASSIFICATION_INVALID__{item['id']}")
        _nonempty(item["component"], f"LEGACY_COMPONENT_NAME_INVALID__{item['id']}")
        _nonempty(item["delta_basis"], f"LEGACY_COMPONENT_BASIS_INVALID__{item['id']}")
        before_counts[before] += 1
        after_counts[after] += 1
        if before != after:
            changed.append(item["id"])
    if before_counts != expected_before or after_counts != expected_after:
        _fail("LEGACY_COMPONENT_MATRIX_RECOMPUTED_COUNTS_INVALID")
    if changed != [16] or matrix["classification_delta_count"] != 1:
        _fail("LEGACY_COMPONENT_MATRIX_DELTA_INVALID")
    if items[15]["classification_before"] != "REQUIRES_HARDENING" or items[15]["classification_after"] != "EVIDENCE_SUPPORTED":
        _fail("RAW_EVIDENCE_PROFILE_TRANSITION_INVALID")
    return after_counts


def validate_contracts(manifest: dict[str, Any]) -> None:
    contracts = manifest.get("contracts")
    if not isinstance(contracts, dict) or set(contracts) != {
        "launch_receipt", "base_image_custody", "raw_evidence_profile", "counter_binding"
    }:
        _fail("CONTRACT_SET_INVALID")
    launch = contracts["launch_receipt"]
    if not isinstance(launch, dict):
        _fail("LAUNCH_CONTRACT_INVALID")
    if set(launch.get("exact_fields", [])) != LAUNCH_RECEIPT_FIELDS:
        _fail("LAUNCH_CONTRACT_FIELD_SET_INVALID")
    if launch.get("canonicalizer_identity") != "ER_QEMU_ARGV_CANONICALIZER":
        _fail("LAUNCH_CANONICALIZER_BINDING_INVALID")
    if launch.get("persistence_identity") != "ER_ATOMIC_CHECKPOINT_WRITER":
        _fail("LAUNCH_PERSISTENCE_BINDING_INVALID")
    if launch.get("launcher_implemented_by_ew") is not False or launch.get("operational_evidence_required") is not True:
        _fail("LAUNCH_IMPLEMENTATION_BOUNDARY_INVALID")
    if launch.get("launch_authority") is not False:
        _fail("LAUNCH_AUTHORITY_INVALID")
    custody = contracts["base_image_custody"]
    if not isinstance(custody, dict):
        _fail("CUSTODY_CONTRACT_INVALID")
    _sha256(custody.get("base_image_sha256"), "CUSTODY_BASE_IMAGE_SHA256_INVALID")
    expected_custody = {
        "format": "QCOW2",
        "qemu_img_check_requirement": "PASS_BEFORE_AND_AFTER_BOUNDED_USE",
        "read_only_expectation": True,
        "overlay_only_mutation_policy": "REQUIRED",
        "allowed_path_or_path_class": "HUMAN_CONFIGURED_ABSOLUTE_REGULAR_NONSYMLINK_PATH_OUTSIDE_GENERATION_TRANSIENT_ROOT",
        "custody_version": "1.0.0",
        "change_authority": "EXPLICIT_HUMAN_AUTHORIZATION_PLUS_NEW_VERSIONED_MANIFEST",
        "fail_closed_mismatch_policy": "DENY_MATERIALIZATION_AND_BOOT",
        "actual_versioned_custody_established": False,
        "historical_reference_only": True,
    }
    if any(custody.get(key) != value for key, value in expected_custody.items()):
        _fail("CUSTODY_POLICY_VALUE_INVALID")
    _nonempty(custody.get("policy_identity"), "CUSTODY_POLICY_IDENTITY_INVALID")
    _nonempty(custody.get("base_image_id"), "CUSTODY_BASE_IMAGE_ID_INVALID")
    profile = contracts["raw_evidence_profile"]
    if not isinstance(profile, dict):
        _fail("RAW_EVIDENCE_PROFILE_INVALID")
    common = profile.get("common_required_fields")
    vector = profile.get("vector_specific_required_fields")
    if not isinstance(common, list) or len(common) != len(set(common)) or not all(isinstance(item, str) and item for item in common):
        _fail("COMMON_PROFILE_FIELDS_INVALID")
    if not isinstance(vector, list) or len(vector) != len(set(vector)) or not all(isinstance(item, str) and item for item in vector):
        _fail("VECTOR_PROFILE_FIELDS_INVALID")
    if set(common) & set(vector):
        _fail("COMMON_VECTOR_FIELD_OVERLAP")
    if profile.get("independent_results") is not True or profile.get("fresh_operational_evidence_required") is not True:
        _fail("COMMON_VECTOR_RESULT_BOUNDARY_INVALID")
    counter = contracts["counter_binding"]
    if not isinstance(counter, dict):
        _fail("COUNTER_CONTRACT_INVALID")
    expected_counter_names = {
        "BOUNDARY_REQUEST_COUNT", "PRE_ATTEMPT_DENIAL_COUNT", "P11_ENTRY_COUNT",
        "P11_OPERATIONAL_INVOCATION_COUNT", "PROTECTED_EFFECT_COUNT",
        "SECOND_PROTECTED_EFFECT_COUNT",
    }
    if set(counter.get("counter_fields", [])) != expected_counter_names:
        _fail("COUNTER_CONTRACT_FIELD_SET_INVALID")
    if counter.get("semantic_definition_id") != "P11_ENTRY_DEFINITION_V1":
        _fail("COUNTER_CONTRACT_SEMANTIC_IDENTITY_INVALID")
    if counter.get("denial_count_canonical_name") != "PRE_ATTEMPT_DENIAL_COUNT":
        _fail("COUNTER_DENIAL_NAME_INVALID")
    if counter.get("distinct_source_binding_required") is not True:
        _fail("COUNTER_SOURCE_UNIQUENESS_POLICY_INVALID")
    if counter.get("historical_aggregate_allowed_as_prospective") is not False:
        _fail("COUNTER_HISTORICAL_POLICY_INVALID")
    if counter.get("operational_producer_consumer_integrated") is not False:
        _fail("COUNTER_OPERATIONAL_INTEGRATION_CLAIM_INVALID")


def validate_launch_receipt(
    receipt: Any,
    manifest: dict[str, Any],
    qemu_module: ModuleType,
) -> dict[str, Any]:
    if not isinstance(receipt, dict) or set(receipt) != LAUNCH_RECEIPT_FIELDS:
        _fail("LAUNCH_RECEIPT_STRUCTURE_INVALID")
    if receipt["schema_id"] != "P11_SPCE_QEMU_LAUNCH_RECEIPT_V1":
        _fail("LAUNCH_RECEIPT_SCHEMA_INVALID")
    kind = receipt["receipt_kind"]
    if kind not in {"PRE_LAUNCH", "POST_EXECUTION"}:
        _fail("LAUNCH_RECEIPT_KIND_INVALID")
    _nonempty(receipt["launcher_identity"], "LAUNCHER_IDENTITY_INVALID")
    _sha256(receipt["launcher_sha256"], "LAUNCHER_SHA256_INVALID")
    argv = receipt["canonical_argv"]
    try:
        calculated = qemu_module.argv_sha256(argv)
    except Exception as exc:
        raise SubstrateValidationError("CANONICAL_ARGV_INVALID") from exc
    if receipt["canonical_argv_sha256"] != calculated:
        _fail("CANONICAL_ARGV_DIGEST_MISMATCH")
    _nonempty(receipt["vm_generation_identity"], "VM_GENERATION_IDENTITY_INVALID")
    if receipt["required_head"] != EXPECTED_HEAD or receipt["required_tree"] != EXPECTED_TREE:
        _fail("LAUNCH_RECEIPT_BASELINE_MISMATCH")
    _nonempty(receipt["pre_boot_authorization_identity"], "PREBOOT_IDENTITY_INVALID")
    _sha256(receipt["pre_boot_authorization_sha256"], "PREBOOT_SHA256_INVALID")
    if receipt["pre_boot_authorization_authenticated"] is not True:
        _fail("PREBOOT_AUTHENTICATION_REQUIRED")
    if not isinstance(receipt["sequence"], int) or isinstance(receipt["sequence"], bool) or receipt["sequence"] < 0:
        _fail("LAUNCH_RECEIPT_SEQUENCE_INVALID")
    if receipt["receipt_is_authority"] is not False:
        _fail("LAUNCH_RECEIPT_CANNOT_BE_AUTHORITY")
    if kind == "PRE_LAUNCH":
        if receipt["execution_invoked"] is not False or receipt["exit_status"] is not None:
            _fail("PRE_LAUNCH_EXECUTION_STATE_INVALID")
    else:
        if receipt["execution_invoked"] is not True:
            _fail("POST_EXECUTION_INVOCATION_STATE_INVALID")
        if not isinstance(receipt["exit_status"], int) or isinstance(receipt["exit_status"], bool):
            _fail("POST_EXECUTION_EXIT_STATUS_INVALID")
    return {"receipt_kind": kind, "argv_sha256": calculated, "result": "PASS"}


def validate_launch_pair(
    pre: Any,
    post: Any,
    manifest: dict[str, Any],
    qemu_module: ModuleType,
) -> dict[str, str]:
    pre_result = validate_launch_receipt(pre, manifest, qemu_module)
    post_result = validate_launch_receipt(post, manifest, qemu_module)
    if pre_result["receipt_kind"] != "PRE_LAUNCH" or post_result["receipt_kind"] != "POST_EXECUTION":
        _fail("LAUNCH_RECEIPT_PAIR_KIND_INVALID")
    same_fields = (
        "launcher_identity", "launcher_sha256", "canonical_argv",
        "canonical_argv_sha256", "vm_generation_identity", "required_head",
        "required_tree", "pre_boot_authorization_identity",
        "pre_boot_authorization_sha256", "pre_boot_authorization_authenticated",
    )
    if any(pre[field] != post[field] for field in same_fields):
        _fail("LAUNCH_RECEIPT_PAIR_BINDING_MISMATCH")
    if post["sequence"] != pre["sequence"] + 1:
        _fail("LAUNCH_RECEIPT_PAIR_SEQUENCE_INVALID")
    return {"pre_launch": "PASS", "post_execution": "PASS", "pair_binding": "PASS"}


def validate_custody_receipt(receipt: Any, manifest: dict[str, Any]) -> dict[str, str]:
    if not isinstance(receipt, dict) or set(receipt) != CUSTODY_RECEIPT_FIELDS:
        _fail("CUSTODY_RECEIPT_STRUCTURE_INVALID")
    policy = manifest["contracts"]["base_image_custody"]
    if receipt["schema_id"] != "P11_SPCE_BASE_IMAGE_CUSTODY_RECEIPT_V1":
        _fail("CUSTODY_RECEIPT_SCHEMA_INVALID")
    if receipt["policy_identity"] != policy["policy_identity"]:
        _fail("CUSTODY_POLICY_IDENTITY_MISMATCH")
    if receipt["base_image_id"] != policy["base_image_id"]:
        _fail("BASE_IMAGE_ID_MISMATCH")
    if receipt["base_image_sha256"] != policy["base_image_sha256"]:
        _fail("BASE_IMAGE_SHA256_MISMATCH")
    if receipt["format"] != policy["format"] or receipt["custody_version"] != policy["custody_version"]:
        _fail("BASE_IMAGE_FORMAT_OR_VERSION_MISMATCH")
    if receipt["qemu_img_check_before"] != "PASS" or receipt["qemu_img_check_after"] != "PASS":
        _fail("QEMU_IMG_CHECK_REQUIRED")
    if receipt["read_only_observed"] is not True or receipt["overlay_only_mutation_observed"] is not True:
        _fail("BASE_IMAGE_READ_ONLY_OVERLAY_POLICY_VIOLATION")
    path = receipt["path"]
    if not isinstance(path, str) or not path.startswith("/") or path.startswith("/tmp/"):
        _fail("BASE_IMAGE_PATH_CLASS_INVALID")
    if receipt["path_class"] != policy["allowed_path_or_path_class"]:
        _fail("BASE_IMAGE_DECLARED_PATH_CLASS_MISMATCH")
    if receipt["base_image_unchanged"] is not True:
        _fail("BASE_IMAGE_MUTATION_DETECTED")
    if receipt["receipt_is_authority"] is not False:
        _fail("CUSTODY_RECEIPT_CANNOT_BE_AUTHORITY")
    return {"custody_policy": "PASS", "receipt_binding": "PASS"}


def validate_counter_bundle(
    bundle: Any,
    manifest: dict[str, Any],
    eu_module: ModuleType,
) -> dict[str, int]:
    if not isinstance(bundle, dict) or set(bundle) != {
        "schema_id", "semantic_definition_id", "events", "observed_counters",
        "counter_source_bindings", "historical_aggregate_semantics_presented_as_prospective",
    }:
        _fail("COUNTER_BUNDLE_STRUCTURE_INVALID")
    if bundle["schema_id"] != "P11_SPCE_PROSPECTIVE_COUNTER_EVIDENCE_V1":
        _fail("COUNTER_BUNDLE_SCHEMA_INVALID")
    if bundle["semantic_definition_id"] != "P11_ENTRY_DEFINITION_V1":
        _fail("COUNTER_SEMANTIC_DEFINITION_INVALID")
    if bundle["historical_aggregate_semantics_presented_as_prospective"] is not False:
        _fail("HISTORICAL_AGGREGATE_PRESENTED_AS_PROSPECTIVE")
    observed = bundle["observed_counters"]
    sources = bundle["counter_source_bindings"]
    if not isinstance(observed, dict) or set(observed) != set(COUNTER_FIELDS):
        _fail("OBSERVED_COUNTER_SET_INVALID")
    if not isinstance(sources, dict) or set(sources) != set(COUNTER_FIELDS):
        _fail("COUNTER_SOURCE_BINDING_SET_INVALID")
    source_values = list(sources.values())
    if not all(isinstance(value, str) and value for value in source_values):
        _fail("COUNTER_SOURCE_BINDING_INVALID")
    if len(set(source_values)) != len(source_values):
        _fail("COUNTER_SOURCE_ALIASING_FORBIDDEN")
    try:
        actual = eu_module.aggregate_events(bundle["events"])
    except Exception as exc:
        raise SubstrateValidationError(str(exc)) from exc
    for field in COUNTER_FIELDS:
        value = observed[field]
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            _fail(f"OBSERVED_COUNTER_VALUE_INVALID__{field}")
        if value != actual[field]:
            _fail(f"OBSERVED_COUNTER_MISMATCH__{field}")
    return {field: actual[field] for field in COUNTER_FIELDS}


def _profile_result(
    value: Any,
    required_fields: list[str],
    checks: Callable[[dict[str, Any]], bool],
) -> str:
    if not isinstance(value, dict) or set(value) != set(required_fields):
        return "FAIL"
    return "PASS" if checks(value) else "FAIL"


def validate_evidence_bundle(bundle: Any, manifest: dict[str, Any]) -> dict[str, str]:
    if not isinstance(bundle, dict) or set(bundle) != {"schema_id", "common_profile", "vector_delta"}:
        _fail("EVIDENCE_BUNDLE_STRUCTURE_INVALID")
    if bundle["schema_id"] != "P11_SPCE_COMMON_PLUS_VECTOR_EVIDENCE_V1":
        _fail("EVIDENCE_BUNDLE_SCHEMA_INVALID")
    contract = manifest["contracts"]["raw_evidence_profile"]
    common_fields = contract["common_required_fields"]
    vector_fields = contract["vector_specific_required_fields"]

    def common_checks(value: dict[str, Any]) -> bool:
        required_pass = ("du_result", "eb_result", "ee_result", "commissioning_result", "guest_teardown_result", "host_teardown_result")
        required_strings = (
            "human_authorization_identity", "execution_budget_identity", "materialization_identity",
            "pre_launch_receipt_identity", "post_execution_receipt_identity",
            "counter_evidence_identity", "terminal_manifest_identity", "fail_closed_state",
        )
        return (
            value["required_head"] == EXPECTED_HEAD
            and value["required_tree"] == EXPECTED_TREE
            and all(value[field] == "PASS" for field in required_pass)
            and all(isinstance(value[field], str) and value[field] for field in required_strings)
            and value["no_nic"] is True
            and value["pre_boot_authorization_authenticated"] is True
            and value["p12_entry_count"] == 0
            and value["production_route_count"] == 0
        )

    def vector_checks(value: dict[str, Any]) -> bool:
        return all(isinstance(value[field], str) and value[field] for field in vector_fields)

    return {
        "common_profile": _profile_result(bundle["common_profile"], common_fields, common_checks),
        "vector_delta": _profile_result(bundle["vector_delta"], vector_fields, vector_checks),
    }


def _expect_failure(token: str, function: Callable[[], Any]) -> None:
    try:
        function()
    except SubstrateValidationError as exc:
        if str(exc) != token:
            _fail(f"NEGATIVE_REASON_MISMATCH__EXPECTED_{token}__ACTUAL_{exc}")
    else:
        _fail(f"NEGATIVE_ACCEPTED__{token}")


def run_regressions(manifest: dict[str, Any]) -> dict[str, Any]:
    eu_component = _component(manifest, "EU_SEMANTIC_VALIDATOR")
    qemu_component = _component(manifest, "ER_QEMU_ARGV_CANONICALIZER")
    eu_module = _load_module(eu_component, "g77_256eu_semantics_for_ew")
    qemu_module = _load_module(qemu_component, "g77_256er_qemu_argv_for_ew")
    model_envelope = eu_module.load_model(_bound_path(_component(manifest, "EU_SEMANTIC_MODEL")))
    cases = model_envelope["model"]["semantic_regression_matrix"]
    canonical = next(case for case in cases if case["id"] == "T06")
    denial = next(case for case in cases if case["id"] == "T05")
    canonical_actual = eu_module.aggregate_events(canonical["events"])
    source_bindings = {field: f"DURABLE_EVENT_SOURCE__{field.upper()}" for field in COUNTER_FIELDS}
    positive_counter = {
        "schema_id": "P11_SPCE_PROSPECTIVE_COUNTER_EVIDENCE_V1",
        "semantic_definition_id": "P11_ENTRY_DEFINITION_V1",
        "events": copy.deepcopy(canonical["events"]),
        "observed_counters": {field: canonical_actual[field] for field in COUNTER_FIELDS},
        "counter_source_bindings": source_bindings,
        "historical_aggregate_semantics_presented_as_prospective": False,
    }
    results: list[dict[str, str]] = []

    def passed(identity: str, function: Callable[[], Any]) -> None:
        try:
            function()
        except Exception as exc:
            results.append({"id": identity, "result": "FAIL", "reason": str(exc)})
        else:
            results.append({"id": identity, "result": "PASS", "reason": "EXPECTED_CONTRACT_OBSERVED"})

    passed("C01_COUNTER_POSITIVE", lambda: validate_counter_bundle(positive_counter, manifest, eu_module))

    denied_actual = eu_module.aggregate_events(denial["events"])
    denied_bundle = copy.deepcopy(positive_counter)
    denied_bundle["events"] = copy.deepcopy(denial["events"])
    denied_bundle["observed_counters"] = {field: denied_actual[field] for field in COUNTER_FIELDS}

    wrong = copy.deepcopy(denied_bundle)
    wrong["observed_counters"]["p11_entry_count"] = 1
    passed("C02_DENIED_REQUEST_ENTRY_FAILS", lambda: _expect_failure(
        "OBSERVED_COUNTER_MISMATCH__p11_entry_count",
        lambda: validate_counter_bundle(wrong, manifest, eu_module),
    ))
    wrong = copy.deepcopy(denied_bundle)
    wrong["observed_counters"]["p11_operational_invocation_count"] = 1
    passed("C03_DENIED_REQUEST_INVOCATION_FAILS", lambda: _expect_failure(
        "OBSERVED_COUNTER_MISMATCH__p11_operational_invocation_count",
        lambda: validate_counter_bundle(wrong, manifest, eu_module),
    ))
    wrong = copy.deepcopy(denied_bundle)
    wrong["observed_counters"]["second_protected_effect_count"] = 1
    passed("C04_DENIED_REUSE_SECOND_EFFECT_FAILS", lambda: _expect_failure(
        "OBSERVED_COUNTER_MISMATCH__second_protected_effect_count",
        lambda: validate_counter_bundle(wrong, manifest, eu_module),
    ))
    wrong = copy.deepcopy(denied_bundle)
    wrong["events"][0]["p11_operational_invocation_increment"] = 1
    passed("C05_INVOCATION_WITHOUT_ENTRY_FAILS", lambda: _expect_failure(
        "INVOCATION_REQUIRES_P11_ENTRY",
        lambda: validate_counter_bundle(wrong, manifest, eu_module),
    ))
    wrong = copy.deepcopy(positive_counter)
    wrong["events"][0]["p11_operational_invocation_increment"] = 0
    passed("C06_EFFECT_WITHOUT_INVOCATION_FAILS", lambda: _expect_failure(
        "PROTECTED_EFFECT_REQUIRES_INVOCATION",
        lambda: validate_counter_bundle(wrong, manifest, eu_module),
    ))
    wrong = copy.deepcopy(positive_counter)
    wrong["events"][0]["pre_attempt_gates_pass"] = False
    passed("C07_ENTRY_WITHOUT_GATES_FAILS", lambda: _expect_failure(
        "ATTEMPT_START_REQUIRES_GATES_PASS_AND_AUTHORIZATION",
        lambda: validate_counter_bundle(wrong, manifest, eu_module),
    ))
    wrong = copy.deepcopy(positive_counter)
    wrong["counter_source_bindings"]["p11_entry_count"] = wrong["counter_source_bindings"]["boundary_request_count"]
    passed("C08_COUNTER_ALIAS_FAILS", lambda: _expect_failure(
        "COUNTER_SOURCE_ALIASING_FORBIDDEN",
        lambda: validate_counter_bundle(wrong, manifest, eu_module),
    ))
    wrong = copy.deepcopy(positive_counter)
    wrong["historical_aggregate_semantics_presented_as_prospective"] = True
    passed("C09_HISTORICAL_AS_PROSPECTIVE_FAILS", lambda: _expect_failure(
        "HISTORICAL_AGGREGATE_PRESENTED_AS_PROSPECTIVE",
        lambda: validate_counter_bundle(wrong, manifest, eu_module),
    ))

    argv = ["/usr/bin/qemu-system-x86_64", "-nic", "none", "-no-reboot"]
    digest = qemu_module.argv_sha256(argv)
    pre = {
        "schema_id": "P11_SPCE_QEMU_LAUNCH_RECEIPT_V1",
        "receipt_kind": "PRE_LAUNCH",
        "launcher_identity": "REPOSITORY_ONLY_VALIDATION_FIXTURE_LAUNCHER",
        "launcher_sha256": sha256_bytes(b"REPOSITORY_ONLY_VALIDATION_FIXTURE_LAUNCHER"),
        "canonical_argv": argv,
        "canonical_argv_sha256": digest,
        "vm_generation_identity": "REPOSITORY_ONLY_VALIDATION_FIXTURE_VM",
        "required_head": EXPECTED_HEAD,
        "required_tree": EXPECTED_TREE,
        "pre_boot_authorization_identity": "REPOSITORY_ONLY_VALIDATION_FIXTURE_PREBOOT",
        "pre_boot_authorization_sha256": sha256_bytes(b"REPOSITORY_ONLY_VALIDATION_FIXTURE_PREBOOT"),
        "pre_boot_authorization_authenticated": True,
        "sequence": 0,
        "execution_invoked": False,
        "exit_status": None,
        "receipt_is_authority": False,
    }
    post = copy.deepcopy(pre)
    post.update({"receipt_kind": "POST_EXECUTION", "sequence": 1, "execution_invoked": True, "exit_status": 0})
    passed("L01_LAUNCH_PAIR_POSITIVE", lambda: validate_launch_pair(pre, post, manifest, qemu_module))
    wrong_post = copy.deepcopy(post)
    wrong_post["canonical_argv_sha256"] = "0" * 64
    passed("L02_ARGV_TAMPER_FAILS", lambda: _expect_failure(
        "CANONICAL_ARGV_DIGEST_MISMATCH",
        lambda: validate_launch_pair(pre, wrong_post, manifest, qemu_module),
    ))
    wrong_pre = copy.deepcopy(pre)
    wrong_pre["pre_boot_authorization_authenticated"] = False
    passed("L03_PREBOOT_REQUIRED", lambda: _expect_failure(
        "PREBOOT_AUTHENTICATION_REQUIRED",
        lambda: validate_launch_pair(wrong_pre, post, manifest, qemu_module),
    ))
    wrong_post = copy.deepcopy(post)
    wrong_post["sequence"] = 3
    passed("L04_SEQUENCE_BINDING_FAILS", lambda: _expect_failure(
        "LAUNCH_RECEIPT_PAIR_SEQUENCE_INVALID",
        lambda: validate_launch_pair(pre, wrong_post, manifest, qemu_module),
    ))

    policy = manifest["contracts"]["base_image_custody"]
    custody = {
        "schema_id": "P11_SPCE_BASE_IMAGE_CUSTODY_RECEIPT_V1",
        "policy_identity": policy["policy_identity"],
        "base_image_id": policy["base_image_id"],
        "base_image_sha256": policy["base_image_sha256"],
        "format": policy["format"],
        "qemu_img_check_before": "PASS",
        "qemu_img_check_after": "PASS",
        "read_only_observed": True,
        "overlay_only_mutation_observed": True,
        "path": "/var/lib/sapianta/base-images/v1/noble-amd64.qcow2",
        "path_class": policy["allowed_path_or_path_class"],
        "custody_version": policy["custody_version"],
        "base_image_unchanged": True,
        "receipt_is_authority": False,
    }
    passed("B201_CUSTODY_CONTRACT_POSITIVE", lambda: validate_custody_receipt(custody, manifest))
    wrong_custody = copy.deepcopy(custody)
    wrong_custody["path"] = "/tmp/transient-base.img"
    passed("B202_TRANSIENT_PATH_FAILS", lambda: _expect_failure(
        "BASE_IMAGE_PATH_CLASS_INVALID",
        lambda: validate_custody_receipt(wrong_custody, manifest),
    ))

    profile = manifest["contracts"]["raw_evidence_profile"]
    common = {field: f"VALUE__{field.upper()}" for field in profile["common_required_fields"]}
    common.update({
        "required_head": EXPECTED_HEAD,
        "required_tree": EXPECTED_TREE,
        "du_result": "PASS", "eb_result": "PASS", "ee_result": "PASS",
        "commissioning_result": "PASS", "guest_teardown_result": "PASS", "host_teardown_result": "PASS",
        "no_nic": True, "pre_boot_authorization_authenticated": True,
        "p12_entry_count": 0, "production_route_count": 0,
    })
    vector = {field: f"VALUE__{field.upper()}" for field in profile["vector_specific_required_fields"]}
    evidence = {"schema_id": "P11_SPCE_COMMON_PLUS_VECTOR_EVIDENCE_V1", "common_profile": common, "vector_delta": vector}
    wrong_vector = copy.deepcopy(evidence)
    del wrong_vector["vector_delta"][profile["vector_specific_required_fields"][0]]
    passed("R01_COMMON_PASS_VECTOR_FAIL_INDEPENDENT", lambda: (
        None if validate_evidence_bundle(wrong_vector, manifest) == {"common_profile": "PASS", "vector_delta": "FAIL"}
        else _fail("COMMON_VECTOR_INDEPENDENCE_INVALID")
    ))
    wrong_common = copy.deepcopy(evidence)
    wrong_common["common_profile"]["required_head"] = "0" * 40
    passed("R02_COMMON_FAIL_VECTOR_PASS_INDEPENDENT", lambda: (
        None if validate_evidence_bundle(wrong_common, manifest) == {"common_profile": "FAIL", "vector_delta": "PASS"}
        else _fail("COMMON_VECTOR_INDEPENDENCE_INVALID")
    ))

    regression_pass = sum(item["result"] == "PASS" for item in results)
    return {
        "regression_total": len(results),
        "regression_pass": regression_pass,
        "regression_fail": len(results) - regression_pass,
        "results": results,
    }


def validate(path: Path) -> dict[str, Any]:
    envelope = load_manifest(path)
    manifest = envelope["manifest"]
    component_counts = validate_components(manifest)
    blocker_status = validate_blockers(manifest)
    legacy_counts = validate_legacy_matrix(manifest)
    validate_contracts(manifest)
    if manifest.get("freeze_decision") != "PARTIAL__EXACT_BLOCKERS_REMAIN":
        _fail("FREEZE_DECISION_INVALID")
    if manifest.get("reusable_p11_spce_execution_substrate") != "PARTIAL":
        _fail("SUBSTRATE_STATE_INVALID")
    regressions = run_regressions(manifest)
    if regressions["regression_fail"]:
        _fail("SUBSTRATE_REGRESSION_FAILURE")
    return {
        "schema_id": "G77_256EW_P11_SPCE_REUSABLE_SUBSTRATE_VALIDATION_RESULT_V1",
        "manifest_path": str(path),
        "manifest_inner_sha256": envelope["manifest_sha256"],
        "component_counts": component_counts,
        "legacy_22_component_counts": legacy_counts,
        "blocker_status": blocker_status,
        "freeze_decision": manifest["freeze_decision"],
        "reusable_p11_spce_execution_substrate": manifest["reusable_p11_spce_execution_substrate"],
        **regressions,
        "operational_effect": 0,
        "authority_effect": 0,
        "credit_effect": 0,
    }


def main() -> int:
    default_manifest = Path(__file__).resolve().parent.parent / MANIFEST_FILENAME
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", nargs="?", type=Path, default=default_manifest)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = validate(args.manifest.resolve())
    except (SubstrateValidationError, OSError) as exc:
        print(f"FINAL_VALIDATION=FAIL_CLOSED__{exc}")
        return 1
    if args.json:
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    else:
        print("FINAL_VALIDATION=PASS")
        print(f"FREEZE_DECISION={result['freeze_decision']}")
        print(f"REUSABLE_P11_SPCE_EXECUTION_SUBSTRATE={result['reusable_p11_spce_execution_substrate']}")
        for identity in sorted(result["blocker_status"]):
            print(f"{identity}={result['blocker_status'][identity]}")
        print(f"REGRESSION_TOTAL={result['regression_total']}")
        print(f"REGRESSION_PASS={result['regression_pass']}")
        print(f"REGRESSION_FAIL={result['regression_fail']}")
        print(f"MANIFEST_INNER_SHA256={result['manifest_inner_sha256']}")
        print("OPERATIONAL_EFFECT=0")
        print("AUTHORITY_EFFECT=0")
        print("CREDIT_EFFECT=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
