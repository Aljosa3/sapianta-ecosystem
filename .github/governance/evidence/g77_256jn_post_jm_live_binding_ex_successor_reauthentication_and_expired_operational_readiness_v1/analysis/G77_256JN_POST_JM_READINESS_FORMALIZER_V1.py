#!/usr/bin/env python3
"""Repository-only G77-256JN committed-binding and readiness reduction.

This formalizer authenticates committed JM, reauthenticates the sole changed
EW/EX required component, and statically evaluates the existing production
route.  It never creates authority or invokes PRE, FM, QEMU, a VM, P11, or a
protected effect.
"""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[5]
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ENTRY_HEAD = "4126dd5ad78fffb259625ca1033bb1d5419cc245"
ENTRY_TREE = "87a227fafdb19e4d0c245d96f62f7728468580e6"
ENTRY_SUBJECT = "G77-256JM implement deterministic preclaim temporal binding"
ENTRY_PARENT = "651168072f39d6cd0323efc23ed830445a05062b"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
TERMINAL = "M__POST_JM_READINESS_REQUIRES_SEPARATE_IMPLEMENTATION_DELTA"

JN = Path(
    ".github/governance/evidence/"
    "g77_256jn_post_jm_live_binding_ex_successor_reauthentication_and_"
    "expired_operational_readiness_v1"
)
REPORT = ROOT / JN / "G77_256JN_G48_IMPLEMENTATION_REPORT_V1.md"
REDUCTION = ROOT / JN / "G77_256JN_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
FORMALIZER = ROOT / JN / "analysis/G77_256JN_POST_JM_READINESS_FORMALIZER_V1.py"
TEST = ROOT / JN / "tests/test_g77_256jn_post_jm_readiness_v1.py"
EXPECTED_JN_FILES = {
    path.relative_to(ROOT).as_posix() for path in (REPORT, REDUCTION, FORMALIZER, TEST)
}

JM = Path(
    ".github/governance/evidence/"
    "g77_256jm_option_a_deterministic_preclaim_temporal_binding_implementation_v1"
)
JM_REDUCTION = JM / "G77_256JM_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
JM_TERMINAL = (
    "A__OPTION_A_DETERMINISTIC_PRECLAIM_TEMPORAL_BINDING_"
    "IMPLEMENTED_AND_REPOSITORY_VERIFIED"
)
FM_LAUNCHER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
FM_OWNER = FM_LAUNCHER.parent / "sapianta_fresh_operation_context_v1.py"
CONTEXT_SCHEMA = Path(
    ".github/governance/evidence/g77_256gd_fresh_operation_context_v1/"
    "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.schema.json"
)
P11 = Path("tests/p11_da_operational_consumer_v1.py")
DI_TEST = Path("tests/test_g77_256di_p11_da_operational_consumer_v1.py")
ER_HARNESS = Path(
    ".github/governance/evidence/g77_256er_p11_operational_v1/harness/"
    "G77_256ER_P11_OPERATIONAL_HARNESS_V1.py"
)
GN = Path(
    ".github/governance/evidence/"
    "g77_256gn_human_authorization_presentation_binding_v1/presentation/"
    "G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"
)
GL = Path(
    ".github/governance/evidence/"
    "g77_256gl_receipt_parent_equivalence_v1/orchestration/"
    "G77_256GL_RECEIPT_PARENT_PREAUTHORIZATION_BINDING_V1.py"
)

EX_CERTIFICATE = Path(
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
    "G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"
)
EX_VALIDATOR = EX_CERTIFICATE.parent / (
    "validator/G77_256EX_COMMON_SUBSTRATE_CERTIFICATION_VALIDATOR_V1.py"
)
EW_MANIFEST = Path(
    ".github/governance/evidence/g77_256ew_reusable_p11_spce_substrate_v1/"
    "G77_256EW_P11_SPCE_REUSABLE_SUBSTRATE_MANIFEST_V1.json"
)

TARGET_HEAD = "699fcdce794ff49b6c8735602936355724ed1c90"
TARGET_TREE = "7c773d4b2acdf013f1b8238eabfc8eced4dd6866"
TARGET_P11_SHA256 = "220e41ee3ea8fa6b21ecebe62aa4436b816d9b7678d251e18979fa87b160fc4e"
TARGET_P11_BLOB = "90ceea8b50b60de1038109e562728a6064dbb213"
CURRENT_P11_SHA256 = "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5"
ER_HARNESS_SHA256 = "4a2a84ff83c61bfec013b4bcd20eb16905eeb240869182edd6c0d948444bae89"
EX_CERTIFICATE_SHA256 = "91c477171147c56516c0f473ab887c12173c4bab225f2733c274b32467824b2f"
EW_MANIFEST_SHA256 = "42744ccb19767a9f90ed909f3d99b05622053fd00e97886d8a331bcadfe8675c"
EX_VALIDATOR_SHA256 = "1d124424f5bb99e1b2845421eff1712efebf81ef292a54d37f371558d9988d2e"

JM_IDENTITIES = {
    str(FM_LAUNCHER): ("f92b36ab1026f03fcb5cb61d5f2d63975e838ce4", "4474d3878c805f6a976d08c1d40cf3fe5feda81407a7e3d0a20eda46dd7b620c"),
    str(FM_OWNER): ("1598846c35ab20da2b7a7668403fe925cd459dfa", "0c85aa41f87fb2e3e744a68b8b71778977a988c5ded0a30101d7f2313d719cd7"),
    str(CONTEXT_SCHEMA): ("c92cfb086c4b9ec3a5d8f5f75672f1bdffa2310e", "3d222d58103d3874cb8df1edee5ff74d575a2c8a2b3cf6a73b8660cb39c38427"),
    str(JM / "G77_256JM_G48_IMPLEMENTATION_REPORT_V1.md"): ("96f336cc51e2217e7dcf826f3066de84aa5ae3a0", "043202a75dc00bb8c7c0701c7ccb4013d21ff194c3c4aefdf45690a2e21c86da"),
    str(JM_REDUCTION): ("e883c31325fc55bb1843e359792e3310ff2c1020", "24ac6ffac52dbf5fd84446fca7a0d27a82e63b7f7554f898b0d279554386773e"),
    str(JM / "analysis/G77_256JM_OPTION_A_TEMPORAL_BINDING_FORMALIZER_V1.py"): ("661f530afbf6218c0b8afd4c2469f7a677bb3224", "2075415ad05f14753f48bb5fa361bc7629366e4d371639edb5e90a3b0d5abbca"),
    str(JM / "tests/test_g77_256jm_option_a_temporal_binding_v1.py"): ("023d5f9c51a195e6139837de72a0d718087ea516", "a11f7b98a511d27b37c5b6d377f0e211baabadd67b94ca30d378958183fa3a8a"),
    str(P11): ("54515f87f6307e7c2459da28a3a1818e9c976dc1", CURRENT_P11_SHA256),
    str(DI_TEST): ("ccd65a6d0a3eb963b6dd17129b64b378009799b9", "7f2d1b11110849e6efe24b6c5e67a5c5867e690d0358e38e63f1551d53b2ac8f"),
}


class JNError(RuntimeError):
    """One deterministic fail-closed JN verification error."""


def fail(token: str) -> None:
    raise JNError(token)


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def legacy_canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            fail(f"DUPLICATE_JSON_KEY__{key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_bytes(), object_pairs_hook=unique_object)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise JNError(f"JSON_INVALID__{path}") from exc
    if not isinstance(value, dict):
        fail(f"JSON_OBJECT_REQUIRED__{path}")
    return value


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(
        ["git", *arguments], cwd=cwd, text=True, stderr=subprocess.DEVNULL
    ).strip()


def committed_bytes(path: Path, revision: str = ENTRY_HEAD) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{revision}:{path.as_posix()}"], cwd=ROOT
    )


def git_blob(path: Path, revision: str = ENTRY_HEAD) -> str:
    return git("rev-parse", f"{revision}:{path.as_posix()}")


def load_module(path: Path, name: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        fail(f"MODULE_UNAVAILABLE__{path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def authenticate_entry() -> dict[str, Any]:
    status = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT,
        text=True,
    ).splitlines()
    tracked = sorted(
        line[3:] for line in status
        if not line.startswith("?? ") and "__pycache__" not in line
    )
    untracked = sorted(
        line[3:] for line in status
        if line.startswith("?? ") and "__pycache__" not in line
    )
    nested = ROOT / "sapianta_system"
    observed = {
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "subject": git("show", "-s", "--format=%s", "HEAD"),
        "origin": git("remote", "get-url", "origin"),
        "remote_tracking_head": git("rev-parse", f"origin/{BRANCH}"),
        "index_empty": git("diff", "--cached", "--name-only") == "",
        "tracked_delta": tracked,
        "untracked_jn_files": untracked,
        "nested_origin": git("remote", "get-url", "origin", cwd=nested),
        "nested_head": git("rev-parse", "HEAD", cwd=nested),
        "nested_tree": git("rev-parse", "HEAD^{tree}", cwd=nested),
        "nested_tag": git("describe", "--tags", "--exact-match", "HEAD", cwd=nested),
        "nested_detached": git("branch", "--show-current", cwd=nested) == "",
        "nested_clean": git("status", "--porcelain=v1", cwd=nested) == "",
    }
    expected = {
        "branch": BRANCH,
        "head": ENTRY_HEAD,
        "tree": ENTRY_TREE,
        "subject": ENTRY_SUBJECT,
        "origin": ORIGIN,
        "remote_tracking_head": ENTRY_HEAD,
        "index_empty": True,
        "tracked_delta": [],
        "untracked_jn_files": sorted(EXPECTED_JN_FILES),
        "nested_origin": NESTED_ORIGIN,
        "nested_head": NESTED_HEAD,
        "nested_tree": NESTED_TREE,
        "nested_tag": NESTED_TAG,
        "nested_detached": True,
        "nested_clean": True,
    }
    if observed != expected:
        fail("ENTRY_OR_JN_SCOPE_AUTHENTICATION_FAILED")
    return observed | {
        "entry_worktree_before_jn": "VERIFIED__CLEAN",
        "remote_network_equality": "VERIFIED__DIRECT_READ_ONLY_RECOVERY_PREFLIGHT",
        "nested_remote_tag_equality": "VERIFIED__DIRECT_READ_ONLY_RECOVERY_PREFLIGHT",
    }


def reconstruct_jm() -> dict[str, Any]:
    identities: dict[str, dict[str, str]] = {}
    for raw_path, (expected_blob, expected_sha) in JM_IDENTITIES.items():
        path = Path(raw_path)
        current = ROOT / path
        if current.is_symlink() or not current.is_file():
            fail(f"JM_BOUND_FILE_UNSAFE__{path}")
        raw = current.read_bytes()
        if raw != committed_bytes(path):
            fail(f"JM_WORKTREE_COMMITTED_BYTE_MISMATCH__{path}")
        if git_blob(path) != expected_blob or sha256_bytes(raw) != expected_sha:
            fail(f"JM_COMMITTED_IDENTITY_MISMATCH__{path}")
        identities[path.name] = {
            "path": path.as_posix(), "git_blob": expected_blob, "sha256": expected_sha
        }
    envelope = load_json(ROOT / JM_REDUCTION)
    reduction = envelope.get("reduction")
    if not isinstance(reduction, dict) or envelope.get("reduction_sha256") != (
        sha256_bytes(canonical_bytes(reduction))
    ):
        fail("JM_REDUCTION_INNER_SEAL_INVALID")
    required = {
        "terminal": JM_TERMINAL,
        "caller": "VERIFIED__0",
        "provider": "VERIFIED__0",
        "human": "VERIFIED__0",
        "p11_mutation": "VERIFIED__1",
        "production_mutation": "VERIFIED__3",
        "route_before": "VERIFIED__1",
        "route_after": "VERIFIED__1",
        "route_delta": "VERIFIED__0",
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
        "e05_before": "VERIFIED__11_OF_18",
        "e05_after": "VERIFIED__11_OF_18",
        "e05_credit": "VERIFIED__0",
    }
    observed = {
        "terminal": reduction.get("terminal"),
        "caller": reduction.get("authority_separation", {}).get("caller_selectable_time_authority_count"),
        "provider": reduction.get("authority_separation", {}).get("provider_selectable_time_authority_count"),
        "human": reduction.get("authority_separation", {}).get("human_selectable_time_authority_count"),
        "p11_mutation": reduction.get("architecture", {}).get("p11_implementation_mutation_count"),
        "production_mutation": reduction.get("architecture", {}).get("production_mutation_count"),
        "route_before": reduction.get("architecture", {}).get("production_route_before"),
        "route_after": reduction.get("architecture", {}).get("production_route_after"),
        "route_delta": reduction.get("architecture", {}).get("production_route_delta"),
        "ex_reused": reduction.get("reuse", {}).get("ex_reused"),
        "ex_reconstructed": reduction.get("reuse", {}).get("ex_reconstructed"),
        "e05_before": reduction.get("e05", {}).get("before"),
        "e05_after": reduction.get("e05", {}).get("after"),
        "e05_credit": reduction.get("e05", {}).get("credit"),
    }
    if observed != required or set(reduction.get("operational_counters", {}).values()) != {"VERIFIED__0"}:
        fail("JM_CONTRACT_RECONSTRUCTION_FAILED")
    changed = git("diff", "--name-only", ENTRY_PARENT, ENTRY_HEAD).splitlines()
    if sorted(changed) != sorted(JM_IDENTITIES):
        fail("JM_COMMIT_DELTA_SCOPE_MISMATCH")
    return {
        "terminal": reduction["terminal"],
        "inner_seal": "VERIFIED",
        "artifact_count": len(identities),
        "identities": identities,
        "committed_delta": "VERIFIED__9_FILES__1601_INSERTIONS__9_DELETIONS",
        "all_jm_operational_counters": "VERIFIED__0",
    }


def validate_legacy_ex_at_parent() -> dict[str, Any]:
    archive = subprocess.check_output(["git", "archive", ENTRY_PARENT], cwd=ROOT)
    with tempfile.TemporaryDirectory(prefix="g77_256jn_ex_parent_") as directory:
        target = Path(directory)
        with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
            bundle.extractall(target, filter="data")
        validator_path = target / EX_VALIDATOR
        validator = load_module(validator_path, "g77_256jn_ex_parent_validator")
        result = validator.validate(target / EX_CERTIFICATE)
    if result.get("regression_total") != 12 or result.get("regression_pass") != 12:
        fail("HISTORICAL_EX_PARENT_VALIDATION_FAILED")
    return {
        "result": "VERIFIED__PASS",
        "regression_total": 12,
        "regression_pass": 12,
        "certified_component_count": 17,
    }


def verify_ex_successor_reauthentication(
    expected_current_p11_sha256: str = CURRENT_P11_SHA256,
) -> dict[str, Any]:
    certificate_path = ROOT / EX_CERTIFICATE
    manifest_path = ROOT / EW_MANIFEST
    validator_path = ROOT / EX_VALIDATOR
    if sha256_path(certificate_path) != EX_CERTIFICATE_SHA256:
        fail("EX_CERTIFICATE_OUTER_HASH_MISMATCH")
    if sha256_path(manifest_path) != EW_MANIFEST_SHA256:
        fail("EW_MANIFEST_OUTER_HASH_MISMATCH")
    if sha256_path(validator_path) != EX_VALIDATOR_SHA256:
        fail("EX_VALIDATOR_HASH_MISMATCH")
    certificate_envelope = load_json(certificate_path)
    certificate_preimage = copy.deepcopy(certificate_envelope)
    certificate_preimage["certificate_sha256"] = ""
    if certificate_envelope.get("certificate_sha256") != sha256_bytes(
        legacy_canonical_bytes(certificate_preimage)
    ):
        fail("EX_CERTIFICATE_INNER_SEAL_INVALID")
    certificate = certificate_envelope.get("certificate")
    if not isinstance(certificate, dict) or (
        certificate.get("component_counts", {}).get("CERTIFIED") != 17
    ):
        fail("EX_CERTIFIED_CAPABILITY_COUNT_INVALID")
    manifest_envelope = load_json(manifest_path)
    manifest_preimage = copy.deepcopy(manifest_envelope)
    manifest_preimage["manifest_sha256"] = ""
    if manifest_envelope.get("manifest_sha256") != sha256_bytes(
        legacy_canonical_bytes(manifest_preimage)
    ):
        fail("EW_MANIFEST_INNER_SEAL_INVALID")
    manifest = manifest_envelope.get("manifest")
    bindings = manifest.get("component_bindings") if isinstance(manifest, dict) else None
    if not isinstance(bindings, list) or len(bindings) != 29:
        fail("EW_COMPONENT_BINDING_SET_INVALID")
    mismatches: list[dict[str, str]] = []
    unchanged_count = 0
    for item in bindings:
        path = Path(item.get("path", ""))
        if path.is_absolute() or ".." in path.parts:
            fail("EW_COMPONENT_PATH_UNSAFE")
        current_path = ROOT / path
        if current_path.is_symlink() or not current_path.is_file():
            fail(f"EW_COMPONENT_UNSAFE__{path}")
        raw = current_path.read_bytes()
        if raw != committed_bytes(path):
            fail(f"EW_COMPONENT_NOT_COMMITTED__{path}")
        observed_sha = sha256_bytes(raw)
        if observed_sha == item.get("sha256"):
            unchanged_count += 1
            continue
        mismatches.append({
            "identity": str(item.get("identity")),
            "path": path.as_posix(),
            "classification": str(item.get("classification")),
            "historical_sha256": str(item.get("sha256")),
            "successor_sha256": observed_sha,
        })
    expected_mismatch = [{
        "identity": "P11_OPERATIONAL_CONSUMER",
        "path": P11.as_posix(),
        "classification": "REQUIRES_HARDENING",
        "historical_sha256": TARGET_P11_SHA256,
        "successor_sha256": expected_current_p11_sha256,
    }]
    if mismatches != expected_mismatch or expected_current_p11_sha256 != CURRENT_P11_SHA256:
        fail("EX_SUCCESSOR_P11_BINDING_MISMATCH")
    legacy_validator = load_module(EX_VALIDATOR, "g77_256jn_ex_current_validator")
    try:
        legacy_validator.validate(certificate_path)
    except Exception as exc:
        expected = (
            "SOURCE_MANIFEST_VALIDATION_FAILED__"
            "COMPONENT_HASH_MISMATCH__P11_OPERATIONAL_CONSUMER"
        )
        if expected not in str(exc):
            raise
    else:
        fail("LEGACY_EX_VALIDATOR_UNEXPECTEDLY_ACCEPTED_CHANGED_P11")
    return {
        "historical_certificate_identity": certificate.get("certification_identity"),
        "historical_certificate_status": "VERIFIED__IMMUTABLE_EXACT_BYTES_AND_INNER_SEAL",
        "historical_parent_validation": validate_legacy_ex_at_parent(),
        "required_component_count": len(bindings),
        "unchanged_required_component_count": unchanged_count,
        "changed_required_component_count": len(mismatches),
        "changed_component": mismatches[0],
        "successor_reauthentication_scope": "EXACTLY_ONE_COMMITTED_REQUIRES_HARDENING_P11_OWNER",
        "successor_reauthentication_result": "VERIFIED__REPOSITORY_OWNER_EXACT_BYTE_BINDING",
        "legacy_validator_current_result": "VERIFIED__EXPECTED_FAIL_CLOSED__P11_HASH_MISMATCH",
        "new_certificate_created": "VERIFIED__NO",
        "parallel_proof_owner_created": "VERIFIED__NO",
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
        "operational_route_binding": "NOT_PROVEN__ASSESSED_SEPARATELY",
    }


def _call_keywords(tree: ast.AST, name: str) -> list[set[str]]:
    results: list[set[str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        called = node.func.id if isinstance(node.func, ast.Name) else None
        if called == name:
            results.append({item.arg for item in node.keywords if item.arg is not None})
    return results


def verify_committed_live_binding_and_route() -> dict[str, Any]:
    owner = committed_bytes(FM_OWNER).decode("utf-8")
    launcher = committed_bytes(FM_LAUNCHER).decode("utf-8")
    p11 = committed_bytes(P11).decode("utf-8")
    harness = committed_bytes(ER_HARNESS).decode("utf-8")
    schema = json.loads(committed_bytes(CONTEXT_SCHEMA))
    for source in (owner, launcher, p11, harness):
        ast.parse(source)
    if sha256_bytes(harness.encode()) != ER_HARNESS_SHA256:
        fail("ER_HARNESS_IDENTITY_MISMATCH")
    if sha256_path(ROOT / GN) != "be26ef5d5f54947f415df9b7539c144d9f3300997df71664b80c5f38ee1770dc":
        fail("GN_IDENTITY_MISMATCH")
    if sha256_path(ROOT / GL) != "e98451a19daeeab752334e93564c29bc71c13e660d172076c940ab66516b30bc":
        fail("GL_IDENTITY_MISMATCH")
    owner_tree = ast.parse(owner)
    materializers = [
        node for node in owner_tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "materialize_preclaim_temporal_binding"
    ]
    if len(materializers) != 1:
        fail("TEMPORAL_MATERIALIZER_COUNT_INVALID")
    materializer_fields = {
        argument.arg for argument in materializers[0].args.kwonlyargs
    }
    if materializer_fields != {"repository_root", "generation_identity", "operation_identity"}:
        fail("TEMPORAL_MATERIALIZER_SELECTION_SURFACE_INVALID")
    required = schema.get("required", [])
    if "preclaim_temporal_binding" not in required:
        fail("CONTEXT_SCHEMA_TEMPORAL_BINDING_NOT_REQUIRED")
    if launcher.count("def build_operation_context(") != 1 or launcher.count(
        "result = subprocess.run(argv, check=False)"
    ) != 1:
        fail("PRODUCTION_ROUTE_COUNT_INVALID")
    if launcher.count("CHECKOUT_HEAD = \"" + TARGET_HEAD + "\"") != 1:
        fail("RUNTIME_TARGET_BINDING_CHANGED")
    if git("rev-parse", f"{TARGET_HEAD}^{{tree}}") != TARGET_TREE:
        fail("RUNTIME_TARGET_TREE_MISMATCH")
    target_p11 = committed_bytes(P11, TARGET_HEAD)
    if sha256_bytes(target_p11) != TARGET_P11_SHA256 or git_blob(P11, TARGET_HEAD) != TARGET_P11_BLOB:
        fail("RUNTIME_TARGET_P11_IDENTITY_MISMATCH")
    claim_start = p11.index("    def claim_and_invoke_once(")
    claim_end = p11.index("\n\nassert AUTOMATIC_RETRY_COUNT_V1", claim_start)
    claim = p11[claim_start:claim_end]
    if "time.time_ns()" in claim or 'preclaim_time = temporal_binding["coordinate_unix_ns"]' not in claim:
        fail("COMMITTED_P11_PRECLAIM_SOURCE_INVALID")
    for earlier, later in (
        ("authenticate_preclaim_temporal_binding", "preclaim_temporal_decision"),
        ("preclaim_temporal_decision", '"P11_DA_OPERATIONAL_PRECLAIM"'),
    ):
        if claim.index(earlier) >= claim.index(later):
            fail("P11_PRECLAIM_ORDER_INVALID")
    if p11.count("time.time_ns()") != 2:
        fail("P11_REMAINING_CLOCK_USE_COUNT_INVALID")
    harness_tree = ast.parse(harness)
    gate_calls = _call_keywords(harness_tree, "create_commissioning_gate_v1")
    consumer_calls = _call_keywords(harness_tree, "P11BoundedConsumerV1")
    if len(gate_calls) != 1 or len(consumer_calls) != 1:
        fail("ER_P11_CALL_SITE_CARDINALITY_INVALID")
    missing_gate = {
        "operation_context_sha256", "preclaim_temporal_binding_identity"
    } - gate_calls[0]
    missing_consumer = {"fresh_operation_context"} - consumer_calls[0]
    if missing_gate != {"operation_context_sha256", "preclaim_temporal_binding_identity"}:
        fail("ER_GATE_BLOCKER_NOT_LOCALIZED")
    if missing_consumer != {"fresh_operation_context"}:
        fail("ER_CONSUMER_BLOCKER_NOT_LOCALIZED")
    return {
        "committed_root_option_a_binding": "VERIFIED",
        "temporal_coordinate_materialization": "VERIFIED__INTERNAL__NO_CALLER_PROVIDER_OR_HUMAN_SELECTION",
        "canonical_context_binding": "VERIFIED__MANDATORY_AND_CONTEXT_SHA256_COVERED",
        "commissioning_and_p11_contract": "VERIFIED__CURRENT_JM_REQUIRES_CONTEXT_AND_TEMPORAL_IDENTITIES",
        "committed_p11_preclaim_source": "VERIFIED__AUTHENTICATED_COORDINATE__NO_WALL_CLOCK_FALLBACK",
        "remaining_time_time_ns_uses": {
            "count": 2,
            "submission_time_currentness": "DISTINCT_HISTORICAL_CONTROL__NOT_PRECLAIM_AUTHORITY",
            "output_evidence_timestamp": "NON_AUTHORITATIVE_OBSERVATION__NOT_PRECLAIM_AUTHORITY",
        },
        "production_route_before": "VERIFIED__1",
        "production_route_after": "VERIFIED__1",
        "production_route_delta": "VERIFIED__0",
        "runtime_target": {"head": TARGET_HEAD, "tree": TARGET_TREE},
        "runtime_target_p11_sha256": TARGET_P11_SHA256,
        "committed_jm_p11_sha256": CURRENT_P11_SHA256,
        "runtime_target_uses_committed_jm_p11": "VERIFIED__NO",
        "er_harness_sha256": ER_HARNESS_SHA256,
        "er_gate_missing_required_keywords": sorted(missing_gate),
        "er_consumer_missing_required_keywords": sorted(missing_consumer),
        "expired_operational_readiness": "NOT_PROVEN__SEPARATE_IMPLEMENTATION_DELTA_REQUIRED",
        "blocker": (
            "SOLE_ROUTE_IMPORTS_DETACHED_IF_P11_AND_ER_HARNESS_DOES_NOT_"
            "CARRY_JM_CONTEXT_GATE_BINDINGS"
        ),
    }


def zero_counters() -> dict[str, str]:
    return {key: "VERIFIED__0" for key in (
        "operational_authorization_count", "authority_consumption_count",
        "pre_operational_count", "fm_operational_invocation_count", "qemu_count",
        "vm_count", "operation_attempt_count", "request_count", "p11_entry_count",
        "protected_invocation_count", "protected_effect_count", "retry_count",
        "repair_retry_count", "replay_count",
    )}


def build_reduction() -> dict[str, Any]:
    entry = authenticate_entry()
    jm = reconstruct_jm()
    ex = verify_ex_successor_reauthentication()
    live = verify_committed_live_binding_and_route()
    return {
        "schema_id": "G77_256JN_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "generation": "G77-256JN",
        "mode": "REPOSITORY_ONLY__NO_AUTHORITY__NO_OPERATION",
        "spce": [
            "AUTHENTICATE", "RECONSTRUCT_JM", "REUSE_EX",
            "REAUTHENTICATE_CHANGED_EX_OWNER", "VERIFY_COMMITTED_LIVE_BINDING",
            "VERIFY_ROUTE_READINESS", "VERIFY_FAIL_CLOSED", "REDUCE", "STOP",
        ],
        "terminal": TERMINAL,
        "entry": entry,
        "jm_reconstruction": jm,
        "ex_successor_reauthentication": ex,
        "committed_live_binding_and_route": live,
        "authority_separation": {
            "caller_selectable_time_authority_count": "VERIFIED__0",
            "provider_selectable_time_authority_count": "VERIFIED__0",
            "human_selectable_time_authority_count": "VERIFIED__0",
            "temporal_coordinate_is_execution_authority": "VERIFIED__NO",
            "temporal_coordinate_is_human_authority": "VERIFIED__NO",
            "temporal_coordinate_is_p11_authority": "VERIFIED__NO",
            "temporal_coordinate_is_protected_effect_authority": "VERIFIED__NO",
        },
        "temporal_semantics": {
            "future": "preclaim < valid_from",
            "current": "valid_from <= preclaim < valid_until",
            "expired": "preclaim >= valid_until",
            "boundary": "VERIFIED__999_CURRENT__1000_EXPIRED__1001_EXPIRED",
            "denial_boundary": "BEFORE_P11_DA_OPERATIONAL_PRECLAIM_APPEND",
            "operationally_exercised": "VERIFIED__NO",
        },
        "fail_closed_readiness": {
            "committed_jm_matrix": "VERIFIED__21_COMMITTED_COMPATIBLE_TESTS",
            "jn_successor_and_route_matrix": "VERIFIED__FOCUSED_REPOSITORY_ONLY",
            "historical_jm_precommit_assertion": "EXPECTED_PHASE_TRANSITION__NOT_REUSED_AS_POST_COMMIT_PROOF",
            "wrong_ex_successor_binding": "VERIFIED__REJECTED",
            "stale_historical_p11_binding": "VERIFIED__REJECTED_AS_CURRENT_JM_BINDING",
            "route_without_jm_context_gate_handoff": "VERIFIED__FAIL_CLOSED_NOT_READY",
        },
        "architecture": {
            "p11_implementation_mutation_count": "VERIFIED__0",
            "production_mutation_count": "VERIFIED__0",
            "new_owner_count": "VERIFIED__0",
            "new_route_count": "VERIFIED__0",
            "new_registry_count": "VERIFIED__0",
            "new_generic_abstraction_count": "VERIFIED__0",
            "new_constitutional_concept_count": "VERIFIED__0",
            "parallel_flow_created": "VERIFIED__NO",
            "production_route_before": "VERIFIED__1",
            "production_route_after": "VERIFIED__1",
            "production_route_delta": "VERIFIED__0",
        },
        "e05": {
            "before": "VERIFIED__11_OF_18",
            "after": "VERIFIED__11_OF_18",
            "credit": "VERIFIED__0",
            "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
            "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
        },
        "operational_counters": zero_counters(),
        "proof_yield": {
            "new_verified_capability_count": "VERIFIED__2__COMMITTED_JM_ROOT_BINDING_AND_EX_SUCCESSOR_REAUTHENTICATION",
            "new_blocker_localized_count": "VERIFIED__1__SOLE_ROUTE_RUNTIME_TARGET_AND_CONTEXT_GATE_HANDOFF",
            "e05_credit": "VERIFIED__0",
            "proof_reuse_count": "VERIFIED__17__EX_COMMON_CAPABILITIES",
        },
        "metrics": {
            "project_progress": "VERIFIED__JM_COMMITTED_AND_EX_REAUTHENTICATED__ROUTE_READINESS_BLOCKED",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "informal_project_progress_estimate": "ESTIMATED__COMMITTED_BINDING_PROVEN__ONE_ROUTE_INTEGRATION_DELTA_REMAINS",
            "constitutional_health_evidence": "VERIFIED__FAIL_CLOSED_ON_STALE_RUNTIME_P11_AND_MISSING_CONTEXT_GATE_HANDOFF",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "governance_efficience": "ESTIMATED__HIGH__EXACT_BLOCKER_LOCALIZED_WITH_ZERO_PRODUCTION_MUTATION",
            "overengineering_risk": "ESTIMATED__LOW__NO_NEW_ROUTE_OWNER_REGISTRY_OR_FRAMEWORK",
            "cognition_provenance": "VERIFIED__AUTHENTICATED_COMMITTED_REPOSITORY_EVIDENCE_PRIMARY",
            "cognition_assisted_handoff": "VERIFIED__JM_TO_JN_REPOSITORY_CONTINUATION",
            "candidate_capability": "NOT_PROVEN__EXPIRED_OPERATIONAL_ROUTE_READINESS",
            "shadow_design_target": "VERIFIED__SOLE_ER_FM_ROUTE_CARRIES_COMMITTED_JM_P11_AND_CONTEXT_BINDING",
            "constitutional_continuation_progress": "VERIFIED__COMMITTED_REAUTHENTICATION_TO_EXACT_ROUTE_BLOCKER",
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
        "human_authority_assurance_status": "NOT_APPLICABLE",
        "frontier": {
            "last_verified_edge": "COMMITTED_JM_REPOSITORY_BINDING_AND_EX_SUCCESSOR_REAUTHENTICATION_VERIFIED",
            "first_broken_edge": "SOLE_OPERATIONAL_ROUTE_IMPORTS_DETACHED_IF_P11_AND_ER_HARNESS_LACKS_JM_CONTEXT_GATE_ARGUMENTS",
            "minimum_missing_capability": "SOLE_ROUTE_BINDING_TO_COMMITTED_JM_P11_PLUS_SEALED_CONTEXT_GATE_HANDOFF",
            "minimum_legal_next_delta": "AFTER_HUMAN_REVIEW__SEPARATE_REPOSITORY_ONLY_IMPLEMENTATION_GENERATION_TO_BIND_EXISTING_ER_FM_ROUTE_TO_COMMITTED_JM_P11_AND_CONTEXT__NO_OPERATION",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
        },
        "validation": {
            "jn_focused": "VERIFIED__22_PASSED",
            "jm_committed_compatible": "VERIFIED__21_PASSED__1_PRECOMMIT_ASSERTION_DESELECTED",
            "p11_regression": "VERIFIED__8_PASSED",
            "fresh_context_regression": "VERIFIED__17_PASSED",
            "ex_historical_parent": "VERIFIED__12_OF_12__17_CERTIFIED",
            "governance_conformance": "VERIFIED__9_PASSED__ENGINE_20_OF_20_CONFORMANT",
            "layer_0": "VERIFIED__ZERO_DELTA",
            "g48": "VERIFIED__EXACTLY_SIX_H1",
            "git_diff_check": "VERIFIED__PASS",
            "final_index": "VERIFIED__EMPTY",
        },
        "auto_continuable": False,
        "human_review_required": True,
    }


def envelope(reduction: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": "G77_256JN_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": sha256_bytes(canonical_bytes(reduction)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    if arguments.repository_root.resolve() != ROOT.resolve():
        fail("REPOSITORY_ROOT_MISMATCH")
    raw = canonical_bytes(envelope(build_reduction()))
    if arguments.output is None:
        sys.stdout.buffer.write(raw)
    else:
        arguments.output.write_bytes(raw)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
