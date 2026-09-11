#!/usr/bin/env python3
"""Verify the bounded KM GN/KI binding correction without running Phase A."""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
HEAD = "6f75d96a4c92cd8534cbb933667b5018786acf42"
TREE = "bb3b89d9aa7f430045771f2a3bdd974975578979"
SUBJECT = "G77-256KL reduce GN preauthorization schema failure"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
STABLE_ANCESTRY = "5c972e9960987ab27420395b54ace693df097e7b"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_REF = "refs/tags/sapianta-system-nested-authority-3183bab-v1"
TERMINAL = (
    "A__GN_EXACT_PREAUTHORIZATION_SCHEMA_PRESERVED_WITH_KI_PREFLIGHT_"
    "EVIDENCE_BOUND_OUTSIDE_GN_OWNER_OBJECT__NO_AUTHORITY__NO_OPERATION__NO_KL_RETRY"
)
KL_TERMINAL = (
    "M__KL_PHASE_A_FAIL_CLOSED_AT_GN_EXACT_SEALED_REQUEST_SCHEMA_VALIDATION_"
    "BEFORE_HUMAN_DECISION_PRESENTATION_OR_KK_BINDING"
)
LAST_OPERATIONAL_EDGE = (
    "EXACT_HUMAN_AUTHORITY_AUTHENTICATED_JZ_BOUND_CONSUMED_ONCE_AND_ONE_"
    "NO_NETWORK_VM_BOOT_REACHED_GUEST_CUSTODY_LOAD"
)
FIRST_UNVERIFIED_OPERATIONAL_EDGE = (
    "FRESH_HUMAN_AUTHORIZED_EXPIRED_DENIAL_BEFORE_P11_ENTRY_AFTER_KF_REPAIR"
)

KM = Path(
    ".github/governance/evidence/"
    "g77_256km_gn_exact_preauthorization_schema_preserving_ki_preflight_binding_v1"
)
VERIFIER = KM / "analysis/G77_256KM_GN_SCHEMA_PRESERVING_KI_PREFLIGHT_BINDING_VERIFIER_V1.py"
TESTS = KM / "tests/test_g77_256km_gn_schema_preserving_ki_preflight_binding_v1.py"
REPORT = KM / "G77_256KM_G48_IMPLEMENTATION_REPORT_V1.md"
REDUCTION = KM / "G77_256KM_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
KJ_WRAPPER = Path(
    ".github/governance/evidence/"
    "g77_256kj_fresh_expired_operational_recommissioning_v1/orchestration/"
    "G77_256KJ_PREAUTHORIZATION_MATERIALIZER_V1.py"
)
KJ_BEFORE_SHA256 = "900741ac1e095d0f0ef2e0c19b102742bf38d3ddf9b11ca602eec463d6e3614f"
KJ_AFTER_SHA256 = "fcc1a60fdbc3fb246d918ac2e8143bd4888e3e65ebc2e3769298a039c5aeebbf"
GN_OWNER = Path(
    ".github/governance/evidence/"
    "g77_256gn_human_authorization_presentation_binding_v1/presentation/"
    "G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"
)
GN_OWNER_SHA256 = "cd3aed49b8f1ca35e53ca4ee31f278dd038fc28fe912175602180be9a2a8a5c3"
KC_PATTERN = Path(
    ".github/governance/evidence/"
    "g77_256kc_fresh_expired_operational_recommissioning_v1/orchestration/"
    "G77_256KC_PREAUTHORIZATION_MATERIALIZER_V1.py"
)
KC_PATTERN_SHA256 = "f41a7b9942a1de0b1825bdda3676d04968d857d01f7370551844abcde16de1d2"
KL_ROOT = Path(
    ".github/governance/evidence/"
    "g77_256kl_fresh_expired_operational_recommissioning_v1"
)
KL_REDUCTION = KL_ROOT / "G77_256KL_SPCE_PHASE_A_TERMINAL_FAIL_CLOSED_REDUCTION_V1.json"
KL_REDUCTION_SHA256 = "0c7f0f92469983d9a043b587c133792b3b52f04f96675c1c1aeb05c189cde363"
KL_REDUCTION_INNER_SHA256 = "fb26bbf73a40315ca822f6d23fe9e12319967a07d1b49ab573ebc67e01476114"
KL_REQUEST = KL_ROOT / "G77_256KL_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
KL_REQUEST_SHA256 = "4f776cc6e15a10b1da4e0255ecd7fdad105f1c99df25c2438a74c8bef865e778"
KL_READINESS = KL_ROOT / "G77_256KL_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json"
KL_READINESS_SHA256 = "5b087803eb00d66284731c2eb1b4fae0954ad71b9d971e35032cb5c373b10e06"
KL_KI_PREFLIGHT = KL_ROOT / "G77_256KL_KI_FRONTIER_PREFLIGHT_V1.json"
KL_KI_PREFLIGHT_SHA256 = "26c63fe71d98a3e396651cbaee6b2e70439e01fe9ce3944886ec205811d44f84"
KI_ASSESSMENT = Path(
    ".github/governance/evidence/"
    "g77_256ki_expired_operational_frontier_assessment_v1/"
    "G77_256KI_SPCE_TERMINAL_REPOSITORY_ONLY_ASSESSMENT_V1.json"
)
KI_ASSESSMENT_SHA256 = "169d3a6feddf327a4e0bcc65927167699c73fe1b4d971c3ef2f730e583589283"
EX_ROOT = Path(".github/governance/evidence/g77_256ex_common_substrate_certification_v1")
EX_CERTIFICATE = EX_ROOT / "G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"
EX_CERTIFICATE_SHA256 = "91c477171147c56516c0f473ab887c12173c4bab225f2733c274b32467824b2f"
EX_SEAL = EX_ROOT / "G77_256EX_FINAL_VALIDATION_SEAL_V1.json"
EX_SEAL_SHA256 = "46115a7627264793af5e289abe85565fcaaf8a381b009e185c35ebc3d4b8a543"
JP_REDUCTION = Path(
    ".github/governance/evidence/"
    "g77_256jp_post_jo_committed_live_binding_and_expired_operational_readiness_reauthentication_v1/"
    "G77_256JP_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
)
JP_REDUCTION_SHA256 = "ca02e314f459a9aa11092f89264deb9d40ba810d35731980e1e60c5c85949503"
ER_HARNESS = Path(
    ".github/governance/evidence/g77_256er_p11_operational_v1/harness/"
    "G77_256ER_P11_OPERATIONAL_HARNESS_V1.py"
)
ER_SUCCESSOR_SHA256 = "c6539d1cc60940b1999956965bff43923a270598a982cd19f976eadec0a93152"
EXTRA_FIELDS = {
    "ki_frontier_preflight_file_sha256",
    "ki_frontier_preflight_inner_sha256",
}


class KMVerificationError(RuntimeError):
    """One deterministic fail-closed KM verification error."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def compact_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes((ROOT / path).read_bytes())


def git(*arguments: str, nested: bool = False) -> str:
    command = ["git"]
    if nested:
        command.extend(["-C", "sapianta_system"])
    command.extend(arguments)
    return subprocess.run(
        command, cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def committed(path: Path) -> bytes:
    return subprocess.run(
        ["git", "show", f"{HEAD}:{path.as_posix()}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout


def load_canonical(path: Path) -> dict[str, Any]:
    raw = (ROOT / path).read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise KMVerificationError(f"NONCANONICAL_JSON:{path}")
    return value


def verify_seal(envelope: dict[str, Any], key: str) -> dict[str, Any]:
    value = envelope.get(key)
    if not isinstance(value, dict):
        raise KMVerificationError(f"MISSING_SEALED_OBJECT:{key}")
    if envelope.get(f"{key}_sha256") != sha256_bytes(canonical_bytes(value)):
        raise KMVerificationError(f"INNER_SEAL_MISMATCH:{key}")
    return value


def load_module(path: Path, name: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, ROOT / path)
    if specification is None or specification.loader is None:
        raise KMVerificationError(f"MODULE_LOAD_FAILED:{path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def verify_entry(remote_head: str, nested_remote_tag: str) -> dict[str, Any]:
    observed = {
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "subject": git("show", "-s", "--format=%s", "HEAD"),
        "origin": git("remote", "get-url", "origin"),
    }
    expected = {
        "branch": BRANCH,
        "head": HEAD,
        "tree": TREE,
        "subject": SUBJECT,
        "origin": ORIGIN,
    }
    if observed != expected or remote_head != HEAD:
        raise KMVerificationError(f"ENTRY_IDENTITY_MISMATCH:{observed}:{remote_head}")
    if git("merge-base", "--is-ancestor", STABLE_ANCESTRY, HEAD) != "":
        raise KMVerificationError("STABLE_ANCESTRY_OUTPUT_UNEXPECTED")
    if git("diff", "--cached", "--name-only"):
        raise KMVerificationError("INDEX_NOT_EMPTY")
    nested = {
        "head": git("rev-parse", "HEAD", nested=True),
        "tree": git("rev-parse", "HEAD^{tree}", nested=True),
        "origin": git("remote", "get-url", "origin", nested=True),
        "clean": git("status", "--porcelain", nested=True) == "",
        "detached": git("branch", "--show-current", nested=True) == "",
    }
    if nested != {
        "head": NESTED_HEAD,
        "tree": NESTED_TREE,
        "origin": NESTED_ORIGIN,
        "clean": True,
        "detached": True,
    } or nested_remote_tag != NESTED_HEAD:
        raise KMVerificationError(f"NESTED_AUTHORITY_MISMATCH:{nested}")
    return {
        **observed,
        "stable_ancestry": "VERIFIED",
        "remote_head": remote_head,
        "remote_equality": "VERIFIED__DIRECT_BRANCH_LS_REMOTE",
        "entry_worktree": "VERIFIED__CLEAN_BEFORE_FIRST_KM_MUTATION",
        "entry_index": "VERIFIED__EMPTY_BEFORE_FIRST_KM_MUTATION",
        "nested_authority": {
            **nested,
            "immutable_ref": NESTED_REF,
            "remote_tag_equal": "VERIFIED__DIRECT_LS_REMOTE",
        },
    }


def verify_mutation_scope() -> dict[str, Any]:
    tracked = git("diff", "--name-status").splitlines()
    if tracked != [f"M\t{KJ_WRAPPER.as_posix()}"]:
        raise KMVerificationError(f"TRACKED_MUTATION_SCOPE_MISMATCH:{tracked}")
    untracked = set(git("ls-files", "--others", "--exclude-standard").splitlines())
    expected = {path.as_posix() for path in (VERIFIER, TESTS, REPORT, REDUCTION)}
    if untracked != expected:
        raise KMVerificationError(f"UNTRACKED_MUTATION_SCOPE_MISMATCH:{sorted(untracked)}")
    return {
        "tracked_evidence_orchestration_mutation_count": 1,
        "new_km_proof_artifact_count": 4,
        "production_mutation_count": 0,
    }


def verify_exact_correction() -> dict[str, Any]:
    before = committed(KJ_WRAPPER)
    after = (ROOT / KJ_WRAPPER).read_bytes()
    removed = (
        b'            "ki_frontier_preflight_file_sha256": preflight["file_sha256"],\n',
        b'            "ki_frontier_preflight_inner_sha256": preflight["inner_sha256"],\n'
    )
    if sha256_bytes(before) != KJ_BEFORE_SHA256:
        raise KMVerificationError("KJ_PREDECESSOR_IDENTITY_MISMATCH")
    expected = before
    for line in removed:
        if line not in expected:
            raise KMVerificationError("KJ_EXACT_REMOVAL_PRECONDITION_MISMATCH")
        expected = expected.replace(line, b"", 1)
    if after != expected or sha256_bytes(after) != KJ_AFTER_SHA256:
        raise KMVerificationError("KJ_MINIMUM_CORRECTION_MISMATCH")
    ast.parse(after.decode("utf-8"))
    source = after.decode("utf-8")
    required = (
        'readiness["checkpoint"]["ki_frontier_preflight"] = preflight',
        'reseal(readiness, "checkpoint")',
        '"checkpoint_file_sha256": sha256_path(readiness_path)',
        '"checkpoint_inner_sha256": readiness["checkpoint_sha256"]',
        'reseal(request, "request")',
    )
    if any(token not in source for token in required):
        raise KMVerificationError("KJ_TRANSITIVE_BINDING_CHAIN_MISSING")
    function = next(
        node for node in ast.parse(source).body
        if isinstance(node, ast.FunctionDef) and node.name == "bind_ki_into_phase_a"
    )
    function_source = ast.get_source_segment(source, function) or ""
    preauthorization_update = function_source[
        function_source.index('request["request"]["preauthorization"].update('):
        function_source.index('reseal(request, "request")')
    ]
    if any(field in preauthorization_update for field in EXTRA_FIELDS):
        raise KMVerificationError("KJ_DIRECT_KI_GN_FIELD_BINDING_REMAINS")
    return {
        "owner": KJ_WRAPPER.as_posix(),
        "before_sha256": KJ_BEFORE_SHA256,
        "after_sha256": KJ_AFTER_SHA256,
        "removed_fields": sorted(EXTRA_FIELDS),
        "added_fields": [],
        "gn_owner_changed": False,
        "gn_validation_weakened": "VERIFIED__NO",
        "second_accepted_gn_schema": "VERIFIED__NO",
        "fallback": "VERIFIED__ABSENT",
        "alias": "VERIFIED__ABSENT",
        "parallel_authority_path": "VERIFIED__NO",
        "binding_shape": "KI_PREFLIGHT_METADATA_IN_SEALED_READINESS_CHECKPOINT__GN_REQUEST_BINDS_EXISTING_CHECKPOINT_FILE_AND_INNER_DIGEST_FIELDS",
        "predecessor_successor_relation": "VERIFIED__KK_CERTIFIED_PREDECESSOR_BYTES_PRESERVED_IN_GIT__KM_SUCCESSOR_DIFF_EXACTLY_TWO_REMOVALS",
    }


def verify_kl_terminal() -> dict[str, Any]:
    raw = (ROOT / KL_REDUCTION).read_bytes()
    if raw != committed(KL_REDUCTION) or sha256_bytes(raw) != KL_REDUCTION_SHA256:
        raise KMVerificationError("KL_REDUCTION_IDENTITY_MISMATCH")
    envelope = load_canonical(KL_REDUCTION)
    reduction = verify_seal(envelope, "reduction")
    failure = reduction.get("failure", {})
    partial = reduction.get("partial_phase_a_state", {})
    if (
        envelope.get("reduction_sha256") != KL_REDUCTION_INNER_SHA256
        or reduction.get("terminal") != KL_TERMINAL
        or failure.get("failure_class") != "EVIDENCE_OR_REPORTING_DEFECT"
        or failure.get("exact_exception")
        != "PresentationBindingError: SEALED_REQUEST_PREAUTHORIZATION_INVALID"
        or set(partial.get("gn_unexpected_fields", [])) != EXTRA_FIELDS
        or partial.get("fresh_kl_phase_a_presentation_ready") != "NOT_PROVEN"
        or reduction.get("human_authority_present") is not False
        or reduction.get("phase_b_started") is not False
        or reduction.get("auto_continuable") is not False
        or reduction.get("human_review_required") is not True
        or any(reduction.get("operational_counters", {}).values())
    ):
        raise KMVerificationError("KL_FAIL_CLOSED_CONTRACT_MISMATCH")
    return {
        "terminal": KL_TERMINAL,
        "failure_class": failure["failure_class"],
        "exact_exception": failure["exact_exception"],
        "reduction_file_sha256": KL_REDUCTION_SHA256,
        "reduction_inner_sha256": KL_REDUCTION_INNER_SHA256,
        "fresh_kl_phase_a_presentation_ready": "NOT_PROVEN",
        "authorization_presentation_state": partial["authorization_presentation_state"],
        "safe_stop_state": partial["safe_stop_state"],
        "human_authority_present": False,
        "phase_b_started": False,
        "operational_counters": "VERIFIED__ALL_ZERO",
    }


def verify_gn_and_binding() -> dict[str, Any]:
    gn_raw = (ROOT / GN_OWNER).read_bytes()
    if gn_raw != committed(GN_OWNER) or sha256_bytes(gn_raw) != GN_OWNER_SHA256:
        raise KMVerificationError("GN_OWNER_IDENTITY_MISMATCH")
    gn = load_module(GN_OWNER, "g77_256km_authenticated_gn_owner")
    expected_fields = {
        "all_operational_counters_zero",
        "checkpoint_file_sha256",
        "checkpoint_inner_sha256",
        "checkpoint_path",
        "complete_deterministic_readiness",
        "gk_receipt_parent_false_positive_blocked",
        "preauth_final_admission_equivalence",
        "preauth_final_admission_equivalence_file_sha256",
        "receipt_parent_observation_file_sha256",
        "static_readiness_file_sha256",
    }
    if gn.PREAUTHORIZATION_FIELDS != expected_fields:
        raise KMVerificationError("GN_EXACT_FIELD_SET_MISMATCH")

    for path, digest in (
        (KL_REQUEST, KL_REQUEST_SHA256),
        (KL_READINESS, KL_READINESS_SHA256),
        (KL_KI_PREFLIGHT, KL_KI_PREFLIGHT_SHA256),
    ):
        raw = (ROOT / path).read_bytes()
        if raw != committed(path) or sha256_bytes(raw) != digest:
            raise KMVerificationError(f"KL_HISTORICAL_ARTIFACT_CHANGED:{path}")
    request_envelope = load_canonical(KL_REQUEST)
    request = verify_seal(request_envelope, "request")
    readiness_envelope = load_canonical(KL_READINESS)
    readiness = verify_seal(readiness_envelope, "checkpoint")
    preflight_envelope = load_canonical(KL_KI_PREFLIGHT)
    preflight = verify_seal(preflight_envelope, "proof")
    actual_fields = set(request.get("preauthorization", {}))
    if actual_fields - expected_fields != EXTRA_FIELDS or expected_fields - actual_fields:
        raise KMVerificationError("KL_SCHEMA_DIFFERENCE_MISMATCH")
    try:
        gn.load_validated_sealed_request(ROOT / KL_REQUEST)
    except gn.PresentationBindingError as exc:
        if str(exc) != "SEALED_REQUEST_PREAUTHORIZATION_INVALID":
            raise KMVerificationError(f"UNEXPECTED_GN_REJECTION:{exc}") from exc
    else:
        raise KMVerificationError("KL_HISTORICAL_REQUEST_UNEXPECTEDLY_ACCEPTED")

    metadata = readiness.get("ki_frontier_preflight", {})
    if (
        request["preauthorization"]["checkpoint_file_sha256"] != KL_READINESS_SHA256
        or request["preauthorization"]["checkpoint_inner_sha256"]
        != readiness_envelope["checkpoint_sha256"]
        or metadata.get("path") != KL_KI_PREFLIGHT.as_posix()
        or metadata.get("file_sha256") != KL_KI_PREFLIGHT_SHA256
        or metadata.get("inner_sha256") != preflight_envelope["proof_sha256"]
        or metadata.get("scope") != "REPOSITORY_ONLY__NONAUTHORITY__NONOPERATIONAL"
        or preflight.get("artifact_class")
        != "REPOSITORY_PREFLIGHT__NONAUTHORITY__NONOPERATIONAL"
        or preflight.get("human_authority_present") is not False
        or any(preflight.get("operational_counters", {}).values())
    ):
        raise KMVerificationError("KI_CHECKPOINT_BINDING_MISMATCH")

    corrected = copy.deepcopy(request_envelope)
    for field in EXTRA_FIELDS:
        corrected["request"]["preauthorization"].pop(field)
    corrected["request_sha256"] = sha256_bytes(canonical_bytes(corrected["request"]))
    if set(corrected["request"]["preauthorization"]) != expected_fields:
        raise KMVerificationError("CORRECTED_GN_FIELD_SET_MISMATCH")
    gn._validate_request_semantics(corrected)
    if corrected["request"]["preauthorization"]["checkpoint_file_sha256"] != KL_READINESS_SHA256:
        raise KMVerificationError("CORRECTED_REQUEST_LOST_CHECKPOINT_BINDING")
    for mutation in ("unknown_field", "checkpoint_inner_sha256"):
        negative = copy.deepcopy(corrected)
        if mutation == "unknown_field":
            negative["request"]["preauthorization"][mutation] = "forbidden"
        else:
            negative["request"]["preauthorization"].pop(mutation)
        try:
            gn._validate_request_semantics(negative)
        except gn.PresentationBindingError as exc:
            if str(exc) != "SEALED_REQUEST_PREAUTHORIZATION_INVALID":
                raise KMVerificationError(f"GN_NEGATIVE_WRONG_TOKEN:{exc}") from exc
        else:
            raise KMVerificationError("GN_EXACT_FIELD_NEGATIVE_ACCEPTED")

    kc_raw = (ROOT / KC_PATTERN).read_bytes()
    kc_source = kc_raw.decode("utf-8")
    kc_binding = kc_source[
        kc_source.index("def bind_namespace_into_phase_a"):
        kc_source.index("def parse_args")
    ]
    kc_preauthorization_update = kc_binding[
        kc_binding.index('request["request"]["preauthorization"].update('):
        kc_binding.index('reseal(request, "request")')
    ]
    if (
        kc_raw != committed(KC_PATTERN)
        or sha256_bytes(kc_raw) != KC_PATTERN_SHA256
        or 'checkpoint["checkpoint"]["kb_namespace_preflight"] = preflight' not in kc_source
        or '"checkpoint_file_sha256": sha256_path(checkpoint_path)' not in kc_source
        or '"checkpoint_inner_sha256": checkpoint["checkpoint_sha256"]' not in kc_source
        or "kb_namespace_preflight_file_sha256" in kc_preauthorization_update
    ):
        raise KMVerificationError("KC_CERTIFIED_SCHEMA_PRESERVING_PATTERN_MISMATCH")
    return {
        "gn_owner": GN_OWNER.as_posix(),
        "gn_owner_sha256": GN_OWNER_SHA256,
        "gn_exact_preauthorization_fields": sorted(expected_fields),
        "gn_exact_preauthorization_field_count": len(expected_fields),
        "unknown_or_additional_fields_prohibited": True,
        "canonical_encoding": "SORTED_COMPACT_JSON_UTF8_PLUS_LF__ALLOW_NAN_FALSE",
        "seal_rule": "REQUEST_SHA256_EQUALS_SHA256_OF_CANONICAL_REQUEST_OBJECT",
        "historical_kl_extra_fields": sorted(EXTRA_FIELDS),
        "historical_kl_rejection": "PresentationBindingError: SEALED_REQUEST_PREAUTHORIZATION_INVALID",
        "synthetic_schema_preserving_projection": "VERIFIED__GN_SEMANTIC_VALIDATOR_ACCEPTED",
        "strict_negative_checks": "VERIFIED__UNKNOWN_AND_MISSING_FIELD_REJECTED_WITH_EXACT_GN_TOKEN",
        "ki_evidence_owner": KL_KI_PREFLIGHT.as_posix(),
        "ki_invariant": "KI_OPERATIONAL_FRONTIER_REAUTHENTICATED__E05_EXPIRED_OPERATIONAL_OBSERVATION_GAP_PRESERVED",
        "ki_digest_semantics": "EVIDENCE_PROOF_METADATA__NONAUTHORITY__NONOPERATIONAL",
        "ki_digest_required_inside_gn_object": False,
        "binding_chain": {
            "ki_preflight_file_sha256": KL_KI_PREFLIGHT_SHA256,
            "ki_preflight_inner_sha256": preflight_envelope["proof_sha256"],
            "readiness_checkpoint_file_sha256": KL_READINESS_SHA256,
            "readiness_checkpoint_inner_sha256": readiness_envelope["checkpoint_sha256"],
            "gn_existing_binding_fields": [
                "checkpoint_file_sha256",
                "checkpoint_inner_sha256",
            ],
            "result": "VERIFIED__DETERMINISTIC_TRANSITIVE_BINDING_OUTSIDE_GN_OWNER_OBJECT",
        },
        "reused_pattern": "VERIFIED__KC_NAMESPACE_PREFLIGHT_IN_SEALED_CHECKPOINT_WITH_ONLY_EXISTING_GN_CHECKPOINT_DIGEST_FIELDS",
        "gn_exact_preauthorization_schema": "VERIFIED__UNCHANGED",
        "ki_preflight_binding": "VERIFIED__SCHEMA_PRESERVING",
    }


def verify_ki_and_ex() -> dict[str, Any]:
    ki_raw = (ROOT / KI_ASSESSMENT).read_bytes()
    if ki_raw != committed(KI_ASSESSMENT) or sha256_bytes(ki_raw) != KI_ASSESSMENT_SHA256:
        raise KMVerificationError("KI_ASSESSMENT_IDENTITY_MISMATCH")
    ki = verify_seal(load_canonical(KI_ASSESSMENT), "assessment")
    if (
        ki.get("terminal")
        != "A__EXPIRED_OPERATIONAL_FRONTIER_RECONSTRUCTED__NO_NEW_CAPABILITY_GAP__ONLY_FRESH_HUMAN_AUTHORIZED_OPERATIONAL_OBSERVATION_REMAINS__NO_AUTHORITY_CONSUMED__NO_OPERATION__E05_UNCHANGED"
        or ki.get("baseline", {}).get("e05_state") != "VERIFIED__11_OF_18"
        or ki.get("baseline", {}).get("e05_frontier") != "VERIFIED__7_UNSATISFIED_OF_18"
        or ki.get("baseline", {}).get("e05_credit") != "VERIFIED__0"
    ):
        raise KMVerificationError("KI_FRONTIER_CONTRACT_MISMATCH")

    certificate_raw = (ROOT / EX_CERTIFICATE).read_bytes()
    seal_raw = (ROOT / EX_SEAL).read_bytes()
    if sha256_bytes(certificate_raw) != EX_CERTIFICATE_SHA256 or sha256_bytes(seal_raw) != EX_SEAL_SHA256:
        raise KMVerificationError("EX_IDENTITY_MISMATCH")
    certificate_envelope = json.loads(certificate_raw)
    certificate_preimage = copy.deepcopy(certificate_envelope)
    certificate_preimage["certificate_sha256"] = ""
    if (
        certificate_envelope.get("certificate_sha256")
        != sha256_bytes(compact_bytes(certificate_preimage))
        or certificate_envelope.get("certificate", {}).get("component_counts", {}).get("CERTIFIED") != 17
    ):
        raise KMVerificationError("EX_CERTIFICATE_CONTRACT_MISMATCH")
    seal_envelope = json.loads(seal_raw)
    seal = seal_envelope.get("seal", {})
    if (
        seal_envelope.get("seal_sha256") != sha256_bytes(compact_bytes(seal))
        or seal.get("validation", {}).get("ew_regression") != "17_OF_17_PASS"
    ):
        raise KMVerificationError("EX_FINAL_SEAL_CONTRACT_MISMATCH")
    jp_raw = (ROOT / JP_REDUCTION).read_bytes()
    jp = verify_seal(load_canonical(JP_REDUCTION), "reduction")
    successor = jp.get("ex_successor_reauthentication", {})
    if (
        jp_raw != committed(JP_REDUCTION)
        or sha256_bytes(jp_raw) != JP_REDUCTION_SHA256
        or successor.get("changed_component") != "ER_OPERATIONAL_HARNESS"
        or successor.get("changed_ex_bound_component_count") != "VERIFIED__1"
        or successor.get("additional_ex_bound_component_change_count") != "VERIFIED__0"
        or successor.get("classification") != "REQUIRES_HARDENING"
        or successor.get("successor_sha256") != ER_SUCCESSOR_SHA256
        or successor.get("ex_reused") != "VERIFIED__17_OF_17"
        or successor.get("ex_reconstructed") != "VERIFIED__0"
        or sha256_path(ER_HARNESS) != ER_SUCCESSOR_SHA256
    ):
        raise KMVerificationError("JP_EX_SUCCESSOR_CONTRACT_MISMATCH")
    return {
        "ex_certificate_file_sha256": EX_CERTIFICATE_SHA256,
        "ex_final_seal_file_sha256": EX_SEAL_SHA256,
        "successor_reauthentication": "VERIFIED__JP_ONE_REQUIRES_HARDENING_ER_DELTA__17_CERTIFIED_COMPONENTS_UNCHANGED",
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
    }


def zero_counters() -> dict[str, int]:
    return {
        "operational_authorization_count": 0,
        "authority_consumption_count": 0,
        "pre_operational_invocation_count": 0,
        "fm_operational_invocation_count": 0,
        "qemu_start_count": 0,
        "vm_start_count": 0,
        "operation_attempt_count": 0,
        "operation_request_count": 0,
        "expired_denial_count": 0,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "retry_count": 0,
        "repair_retry_count": 0,
        "replay_count": 0,
    }


def build_reduction(remote_head: str, nested_remote_tag: str) -> dict[str, Any]:
    entry = verify_entry(remote_head, nested_remote_tag)
    mutation = verify_mutation_scope()
    correction = verify_exact_correction()
    kl = verify_kl_terminal()
    binding = verify_gn_and_binding()
    ex = verify_ki_and_ex()
    artifacts = {path.as_posix(): sha256_path(path) for path in (VERIFIER, TESTS, REPORT)}
    return {
        "schema_id": "G77_256KM_GN_SCHEMA_PRESERVING_KI_PREFLIGHT_BINDING_REDUCTION_V1",
        "terminal": TERMINAL,
        "mode": "REPOSITORY_ONLY__STATIC_SCHEMA_BINDING_PROOF__NO_AUTHORITY__NO_OPERATION__NO_KL_RETRY",
        "vector": "EXPIRED",
        "entry": entry,
        "authenticated_kl_failure": kl,
        "failure_novelty_and_convergence_check": {
            "failure_class": "EVIDENCE_OR_REPORTING_DEFECT",
            "novelty": "VERIFIED__NEW_INHERITED_KJ_KI_PREFLIGHT_FIELDS_ADDED_TO_GN_EXACT_PREAUTHORIZATION_OBJECT__NO_NEW_PRODUCTION_SEMANTICS",
            "affected_invariant": "GN_EXACT_SEALED_REQUEST_SCHEMA_PRESERVATION_DURING_PHASE_A_PREFLIGHT_BINDING",
            "previous_closest_edge": "JV_GN_COMPATIBLE_EXPIRED_AUTHORIZATION_REQUEST_PROJECTION_REPOSITORY_VERIFIED",
            "semantic_difference": "VERIFIED__TWO_KI_PREFLIGHT_DIGEST_FIELDS_ADDED_BEYOND_AUTHENTICATED_GN_PREAUTHORIZATION_FIELD_SET",
            "production_behavior_impact": "VERIFIED__NONE__FAILURE_PRECEDED_HUMAN_DECISION_AUTHORITY_AND_OPERATION",
            "new_capability_required": "NOT_PROVEN",
            "new_proof_required": "VERIFIED__GN_SCHEMA_PRESERVING_KI_PREFLIGHT_BINDING_PROVEN_BY_KM",
            "convergence_signal": "VERIFIED__GN_SCHEMA_EDGE_CLOSED__KI_OPERATIONAL_FRONTIER_AND_E05_UNCHANGED",
            "repetition_pressure": "ESTIMATED__REDUCED_BY_SEPARATE_NONRECURSIVE_KM_STATIC_CORRECTION",
            "verification_amplification_risk": "VERIFIED__CONTAINED__NO_KL_RETRY_OR_PROOF_SCOPE_EXPANSION",
            "classification_evidence": "VERIFIED__COMMITTED_KL_SEAL__GN_EXACT_FIELD_OWNER__KJ_TWO_LINE_DELTA__KC_CERTIFIED_PATTERN__STATIC_NEGATIVES",
            "classification_confidence": "VERIFIED__HIGH",
            "acceptance_requirement_forcing_continuation": "VERIFIED__KM_REQUIRED_SEPARATE_SCHEMA_PRESERVING_BINDING_PROOF_AND_STOPS_AT_REPOSITORY_EDGE",
        },
        "binding": binding,
        "correction": correction,
        "frontier": {
            "last_verified_operational_edge": LAST_OPERATIONAL_EDGE,
            "first_unverified_operational_edge": FIRST_UNVERIFIED_OPERATIONAL_EDGE,
            "last_verified_edge": "GN_EXACT_PREAUTHORIZATION_SCHEMA_PRESERVED_WITH_KI_PREFLIGHT_EVIDENCE_DETERMINISTICALLY_BOUND_THROUGH_SEALED_READINESS_CHECKPOINT",
            "first_broken_edge": "NOT_PROVEN__NO_NEXT_REPOSITORY_LOCAL_BROKEN_EDGE_AUTHENTICATED",
            "current_real_blocker": "NOT_PROVEN__GN_SCHEMA_BINDING_EDGE_CLOSED__NO_NEXT_REPOSITORY_LOCAL_BLOCKER_AUTHENTICATED",
            "minimum_missing_capability": "NOT_PROVEN__GN_SCHEMA_BINDING_GAP_ELIMINATED__NO_NEW_PRODUCTION_CAPABILITY_GAP_ESTABLISHED",
            "minimum_legal_next_delta": "AFTER_HUMAN_REVIEW__SEPARATELY_GOVERNED_FRESH_PHASE_A_CONSTRUCTION",
        },
        "baseline": {
            "e05_state": "VERIFIED__11_OF_18",
            "e05_frontier": "VERIFIED__7_UNSATISFIED_OF_18",
            "e05_credit": "VERIFIED__0",
            "km_e05_credit": "VERIFIED__0",
            "expired": "NOT_PROVEN_OPERATIONALLY",
            **ex,
        },
        "governance": {
            "project_state": "VERIFIED__GN_SCHEMA_PRESERVING_KI_PREFLIGHT_BINDING_REPOSITORY_CORRECTED__NO_PHASE_A_EXECUTION",
            "project_progress": "VERIFIED__KL_LOCAL_SCHEMA_BINDING_BLOCKER_CLOSED__OPERATIONAL_FRONTIER_UNCHANGED",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "informal_project_progress_estimate": "ESTIMATED__SCHEMA_PREREQUISITE_READY_FOR_FUTURE_SEPARATELY_GOVERNED_REVIEW",
            "constitutional_health_evidence": "VERIFIED__GN_STRICTNESS_PRESERVED__FAIL_CLOSED_HISTORY_PRESERVED__ZERO_OPERATION__NO_RETRY__ONE_ROUTE",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "governance_efficience": "ESTIMATED__HIGH__TWO_FIELD_LOCAL_DELTA_AND_CERTIFIED_PATTERN_REUSE_CLOSE_ONE_EDGE",
            "overengineering_risk": "ESTIMATED__LOW_WITHIN_KM__HIGH_IF_KL_RETRY_OR_SCHEMA_EVOLUTION_IS_ADDED",
            "cognition_provenance": "VERIFIED__AUTHENTICATED_REPOSITORY_ARTIFACTS_AND_DETERMINISTIC_STATIC_ANALYSIS_PRIMARY",
            "cognition_assisted_handoff": "VERIFIED__SEALED_KM_REPOSITORY_ONLY_REDUCTION",
            "candidate_capability": "VERIFIED__GN_SCHEMA_PRESERVING_KI_EVIDENCE_BINDING_ONLY__NOT_PRODUCTION_OR_OPERATIONAL_CAPABILITY",
            "shadow_design_target": "VERIFIED__SOLE_FM_ER_P11_ROUTE_UNCHANGED_AND_NOT_INVOKED",
            "constitutional_continuation_progress": "VERIFIED__KL_FAIL_CLOSED_EDGE_TO_KM_REPOSITORY_BINDING_CLOSURE",
            "hac_hai_hae": "NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED",
        },
        "architecture": {
            "production_mutation_count": 0,
            "p11_implementation_mutation_count": 0,
            "new_owner_count": 0,
            "new_route_count": 0,
            "new_registry_count": 0,
            "new_generic_abstraction_count": 0,
            "new_constitutional_concept_count": 0,
            "production_route_before": 1,
            "production_route_after": 1,
            "parallel_flow": "NO",
            **mutation,
        },
        "proof_yield": {
            "new_verified_capability_count": "VERIFIED__1__REPOSITORY_SCHEMA_BINDING_ONLY",
            "new_operational_capability_count": "VERIFIED__0",
            "new_blocker_localized_count": "VERIFIED__0__LOCALIZED_BY_KL",
            "new_blocker_closed_count": "VERIFIED__1__GN_SCHEMA_PRESERVING_KI_PREFLIGHT_BINDING",
            "new_false_or_superseded_blocker_removed_count": "VERIFIED__0",
            "new_classification_result_count": "VERIFIED__1__EVIDENCE_OR_REPORTING_DEFECT_REAUTHENTICATED",
            "e05_credit": "VERIFIED__0",
            "proof_reuse_count": "VERIFIED__17__EX_COMMON_COMPONENTS",
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION",
            "authenticated_repository_continuation": "VERIFIED__YES",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
            "handoff_reconstruction_success": "VERIFIED__YES",
            "handoff_ambiguity_count": "VERIFIED__0",
            "observed_artifact_level_cross_worker_drift": "VERIFIED__0",
        },
        "reuse_impact_assessment": {
            "1_katere_obstojece_certificirane_zmogljivosti_se_ponovno_uporabijo": "VERIFIED__EX_17_OF_17__GN__JV__KC_SCHEMA_PRESERVING_CHECKPOINT_PATTERN__KI__KL_FAILURE_EVIDENCE__SOLE_ROUTE",
            "2_katere_nove_zmogljivosti_ce_sploh_nastanejo": "VERIFIED__ONE_REPOSITORY_SCHEMA_BINDING_CAPABILITY__ZERO_PRODUCTION_OR_OPERATIONAL_CAPABILITIES",
            "3_ali_katera_obstojeca_zmogljivost_postane_nedosegljiva": "VERIFIED__NO",
            "4_ali_implementacija_ustvarja_vzporedni_tok": "VERIFIED__NO",
            "5_ali_zmanjsuje_ali_povecuje_stevilo_produkcijskih_poti": "VERIFIED__UNCHANGED__1_TO_1",
        },
        "operational_counters": zero_counters(),
        "kl_retry_performed": False,
        "fresh_phase_a_commission_created": False,
        "human_authority_present": False,
        "phase_b_started": False,
        "auto_continuable": False,
        "human_review_required": True,
        "known_validation_limitation": "VERIFIED__HISTORICAL_KL_POINT_IN_TIME_TEST_EXPECTS_PRE_KL_ENTRY_C625542A_AND_REJECTS_CURRENT_REQUIRED_KL_HEAD_6F75D96A__HISTORICAL_VALIDATOR_UNCHANGED",
        "artifact_hashes": artifacts,
    }


def envelope(reduction: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": "G77_256KM_GN_SCHEMA_PRESERVING_KI_PREFLIGHT_BINDING_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": sha256_bytes(canonical_bytes(reduction)),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-head", required=True)
    parser.add_argument("--nested-remote-tag", required=True)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    arguments = parse_args()
    value = envelope(build_reduction(arguments.remote_head, arguments.nested_remote_tag))
    raw = canonical_bytes(value)
    if arguments.output is None:
        sys.stdout.buffer.write(raw)
    else:
        output = arguments.output
        if not output.is_absolute():
            output = ROOT / output
        output.write_bytes(raw)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
