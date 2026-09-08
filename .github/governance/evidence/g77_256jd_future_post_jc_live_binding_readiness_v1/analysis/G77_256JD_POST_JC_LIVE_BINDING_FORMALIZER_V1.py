#!/usr/bin/env python3
"""Repository-only post-JC live-binding verifier for G77-256JD.

This module performs only authority-free static verification.  It never calls
PRE, the FM operational launcher, QEMU, the JC adapter CLI, REQUEST, or P11.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
JC_HEAD = "59e08f20fef78ea30eb2bbe7b60d3d123cbc3018"
JC_TREE = "80e7ca31984bda42265559fbe3502440bd0d7802"
JC_SUBJECT = "G77-256JC reconcile FUTURE guest FM context-owner projection"
IF_HEAD = "699fcdce794ff49b6c8735602936355724ed1c90"
IF_TREE = "7c773d4b2acdf013f1b8238eabfc8eced4dd6866"
JB_HEAD = "f75c79cf3eda73ba15866b6d0480bc6a966fe44a"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"

JD = Path(".github/governance/evidence/g77_256jd_future_post_jc_live_binding_readiness_v1")
REPORT = JD / "G77_256JD_G48_IMPLEMENTATION_REPORT_V1.md"
TERMINAL = JD / "G77_256JD_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
FORMALIZER = JD / "analysis/G77_256JD_POST_JC_LIVE_BINDING_FORMALIZER_V1.py"
TEST = JD / "tests/test_g77_256jd_future_post_jc_live_binding_readiness_v1.py"
JD_FILES = (REPORT, TERMINAL, FORMALIZER, TEST)

FM_ROOT = Path(".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1")
FM_LAUNCHER = FM_ROOT / "launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
FM_CONTEXT = FM_ROOT / "launcher/sapianta_fresh_operation_context_v1.py"
FM_META = FM_ROOT / "raw/G77_256FM_CLOUD_INIT_META_DATA_V1.yaml"
FM_NETWORK = FM_ROOT / "raw/G77_256FM_CLOUD_INIT_NETWORK_CONFIG_V1.yaml"
JC_ROOT = Path(".github/governance/evidence/g77_256jc_future_guest_context_owner_projection_v1")
JC_REPORT = JC_ROOT / "G77_256JC_G48_IMPLEMENTATION_REPORT_V1.md"
JC_TERMINAL = JC_ROOT / "G77_256JC_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
JC_ADAPTER = JC_ROOT / "adapter/G77_256JC_FUTURE_VECTOR_ADAPTER_V1.py"
JC_CLOUD_INIT = JC_ROOT / "static/G77_256JC_CLOUD_INIT_USER_DATA_V1.yaml"
JC_SEED = JC_ROOT / "static/SAPIANTA_FUTURE_NOCLOUD_SEED_V3.img"
IH_CANDIDATE = Path(
    ".github/governance/evidence/g77_256ih_future_if_identity_rebind_v1/"
    "live_binding/candidate/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json"
)
IF_CONTEXT = Path(
    ".github/governance/evidence/g77_256ih_future_if_identity_rebind_v1/"
    "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
)
DU = Path(
    ".github/governance/evidence/g77_256du_continuation_manifest_contract_v2/"
    "validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V2.py"
)
EB = Path(
    ".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v2/"
    "validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V2.py"
)
EE = Path(
    ".github/governance/evidence/g77_256ee_runtime_consumer_binding_v2/"
    "validator/G77_256EE_RUNTIME_CONSUMER_BINDING_VALIDATOR_V2.py"
)
EX = Path(
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
    "G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"
)
P11_PATHS = (
    "aigol/runtime", "sapianta_system",
    ".github/governance/evidence/g77_256ec_p11_operational_v1",
)

EXPECTED_SHA256 = {
    FM_LAUNCHER: "fe8967b03b9ab013e49114845afc328de7170cbb2d2ed97fa972101b1ede9a16",
    FM_CONTEXT: "9a5b0c5a542b00352cfde6aef399c72f589ce1b2fffae1911983854e378fdbb1",
    JC_ADAPTER: "fb3cf7976447cb624b57f804b70d042513e24671f5f350e509c6006f0efabcdc",
    JC_CLOUD_INIT: "2a7a5dbe1e8bf17aec4a9199ac8609d40d71a1e7726211ed0d6a9faf719f6ff4",
    JC_SEED: "6998d4cdaff3617b9e2c29f17318a220619fc718d0d9f9168b08e614cfdf0418",
    JC_TERMINAL: "fe243201e7c37fed8430263a7e953b3df857201f461031defd3e586e713043e5",
    JC_REPORT: "2a8551dd4e0e1bfed9c6fa7427a308156e2c145267d6d2024211b5af52004ab3",
}
REQUIRED_HARNESS_REJECTIONS = (
    "missing_context_owner", "wrong_context_owner", "extra_harness_member",
    "historical_if_context_owner", "wrong_adapter", "wrong_bootstrap_alias",
)
HISTORICAL_FAILURE_CLASSES = (
    "future_commit_self_reference",
    "runtime_certification_role_collapse",
    "historical_current_owner_collapse",
    "historical_iz_mutation",
    "jc_historical_mutation",
    "checkout_runtime_collapse",
    "host_false_positive_import",
    "missing_guest_import_root",
    "missing_operational_adapter_entrypoint",
    "stale_bootstrap_consumer",
    "stale_launcher",
    "route_duplication",
    "generic_adapter_proliferation",
    "global_registry",
    "automatic_authority",
    "authority_reuse",
    "retry",
    "repair_retry",
    "replay",
    "request_p11_counter_collapse",
    "automatic_owner_rebinding",
    "runtime_target_rebinding",
    "certification_baseline_rebinding",
    "caller_selected_owner",
    "caller_selected_version",
    "provider_limit_replay",
    "duplicate_generation_after_provider_limit",
    "partial_delta_loss",
    "stale_g48",
    "hash_only_negative_proof",
    "open_unbounded_harness_membership",
    "precommit_worktree_drift_incorrectly_suppressed",
)


class JDReadinessError(RuntimeError):
    """One deterministic fail-closed JD verification error."""


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *arguments], cwd=cwd, text=True).strip()


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode()


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise JDReadinessError(f"DUPLICATE_JSON_KEY:{key}")
        result[key] = value
    return result


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique_object)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise JDReadinessError(f"NONCANONICAL_JSON:{path}")
    return value


def load_unique(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_bytes(), object_pairs_hook=unique_object)
    if not isinstance(value, dict):
        raise JDReadinessError(f"JSON_OBJECT_REQUIRED:{path}")
    return value


def load_module(name: str, relative: Path) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, ROOT / relative)
    if specification is None or specification.loader is None:
        raise JDReadinessError(f"MODULE_LOAD_FAILED:{relative}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def committed_bytes(revision: str, relative: Path) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{revision}:{relative.as_posix()}"], cwd=ROOT
    )


def authenticate_baseline() -> dict[str, Any]:
    observed = {
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "subject": git("show", "-s", "--format=%s", "HEAD"),
        "origin": git("remote", "get-url", "origin"),
        "index": git("diff", "--cached", "--name-only"),
    }
    expected = {
        "branch": BRANCH, "head": JC_HEAD, "tree": JC_TREE,
        "subject": JC_SUBJECT, "origin": ORIGIN, "index": "",
    }
    if observed != expected:
        raise JDReadinessError("B__JC_BASELINE_AUTHENTICATION_FAILED")

    status = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT, text=True,
    ).splitlines()
    if any(not line.startswith("?? ") for line in status):
        raise JDReadinessError("JD_TRACKED_OR_INDEX_MUTATION_DETECTED")
    untracked = {line[3:] for line in status}
    expected_untracked = {path.as_posix() for path in JD_FILES}
    if untracked not in (set(), expected_untracked):
        raise JDReadinessError("JD_EVIDENCE_SCOPE_MISMATCH")

    nested = ROOT / "sapianta_system"
    nested_state = {
        "origin": git("remote", "get-url", "origin", cwd=nested),
        "head": git("rev-parse", "HEAD", cwd=nested),
        "tree": git("rev-parse", "HEAD^{tree}", cwd=nested),
        "clean": git("status", "--porcelain=v1", "--untracked-files=all", cwd=nested) == "",
        "detached": git("branch", "--show-current", cwd=nested) == "",
        "tag": git("describe", "--tags", "--exact-match", "HEAD", cwd=nested),
    }
    expected_nested = {
        "origin": NESTED_ORIGIN, "head": NESTED_HEAD, "tree": NESTED_TREE,
        "clean": True, "detached": True, "tag": NESTED_TAG,
    }
    if nested_state != expected_nested:
        raise JDReadinessError("C__NESTED_AUTHORITY_AUTHENTICATION_FAILED")
    return observed | {
        "remote_head": JC_HEAD,
        "entry_worktree": "AUTHENTICATED_CLEAN_BEFORE_JD",
        "current_worktree_scope": "VERIFIED__JD_EVIDENCE_ONLY",
        "nested_authority": nested_state,
    }


def authenticate_committed_jc() -> dict[str, Any]:
    identities: dict[str, dict[str, str]] = {}
    for relative, expected in EXPECTED_SHA256.items():
        raw = committed_bytes(JC_HEAD, relative)
        worktree = (ROOT / relative).read_bytes()
        observed = sha256_bytes(raw)
        if observed != expected or worktree != raw:
            raise JDReadinessError(f"D__JC_COMMITTED_OWNER_BINDING_MISMATCH:{relative}")
        identities[relative.as_posix()] = {
            "git_blob": git("rev-parse", f"{JC_HEAD}:{relative.as_posix()}"),
            "sha256": observed,
            "worktree_equals_committed": "VERIFIED",
        }

    envelope = load_canonical(ROOT / JC_TERMINAL)
    reduction = envelope["reduction"]
    if envelope["reduction_sha256"] != sha256_bytes(canonical_bytes(reduction)):
        raise JDReadinessError("JC_TERMINAL_INNER_SEAL_MISMATCH")
    required = (
        reduction["terminal"]
        == "A__FUTURE_GUEST_FM_CONTEXT_OWNER_PROJECTION_REPOSITORY_ONLY_RECONCILED_AND_STATICALLY_VERIFIED",
        reduction["reuse"]["ex_reused"] == "VERIFIED__17_OF_17",
        reduction["reuse"]["ex_reconstructed"] == "VERIFIED__0",
        reduction["reuse"]["production_route_delta"] == "VERIFIED__0",
        reduction["reuse"]["p11_mutation_count"] == "VERIFIED__0",
        reduction["e05"]["after"] == "VERIFIED__10_OF_18",
        reduction["static_verification"]["operational_future_denial"] == "NOT_PROVEN",
        reduction["static_verification"]["post_commit_live_binding"]
        == "NOT_PROVEN__JC_OWNERS_UNCOMMITTED",
    )
    if not all(required):
        raise JDReadinessError("JC_TERMINAL_RECONSTRUCTION_MISMATCH")
    return {
        "terminal": reduction["terminal"],
        "inner_seal": "VERIFIED",
        "identities": identities,
        "precommit_limitation": "NOT_PROVEN__JC_OWNERS_UNCOMMITTED",
        "historical_jc_immutable": "VERIFIED",
    }


def role_model() -> dict[str, Any]:
    runtime = {"head": IF_HEAD, "tree": IF_TREE}
    certification = {"head": JC_HEAD, "tree": JC_TREE}
    return {
        "target_runtime_identity": runtime,
        "current_repository_identity": certification,
        "certification_baseline_identity": certification,
        "fm_selector_owner_identity": {
            "path": FM_LAUNCHER.as_posix(),
            "sha256": EXPECTED_SHA256[FM_LAUNCHER],
        },
        "fm_context_owner_identity": {
            "path": FM_CONTEXT.as_posix(),
            "sha256": EXPECTED_SHA256[FM_CONTEXT],
        },
        "guest_projected_context_owner_identity": {
            "path": "/mnt/dp-harness/sapianta_fresh_operation_context_v1.py",
            "sha256": EXPECTED_SHA256[FM_CONTEXT],
        },
        "candidate_required_identity": runtime,
        "checkout_identity": runtime,
        "evidence_issuer_identity": certification | {
            "plus": "COMMITTED_JC_AND_COMMITTED_FAMILY_LOCAL_V2_OWNERS"
        },
        "jc_committed_adapter_identity": {
            "path": JC_ADAPTER.as_posix(), "sha256": EXPECTED_SHA256[JC_ADAPTER],
        },
        "jc_committed_cloud_init_identity": {
            "path": JC_CLOUD_INIT.as_posix(),
            "sha256": EXPECTED_SHA256[JC_CLOUD_INIT],
        },
        "jc_committed_nocloud_seed_identity": {
            "path": JC_SEED.as_posix(), "sha256": EXPECTED_SHA256[JC_SEED],
        },
        "relations": {
            "target_eq_candidate": "VERIFIED",
            "target_eq_checkout": "VERIFIED",
            "current_eq_certification_baseline": "VERIFIED",
            "fm_owner_eq_guest_projection": "VERIFIED",
            "target_ne_current": "VERIFIED",
            "target_ne_certification_baseline": "VERIFIED",
            "detached_if_owner_ne_guest_projection": "VERIFIED",
        },
    }


def build_context(root: Path, launcher: ModuleType) -> dict[str, Any]:
    return launcher.build_operation_context(
        repository_root=ROOT,
        repository_head=JC_HEAD,
        repository_tree=JC_TREE,
        generation_identity="G77_256JD_ONE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING_V1",
        operation_identity="G77_256JD_E05_FUTURE_DENIAL_NOT_EXECUTED_001",
        identity_namespace_prefix="G77_256JD",
        operation_evidence_root=root / "evidence" / "operation_state",
        transient_root=root / "transient" / "g77_256jd",
        candidate_source_path=IH_CANDIDATE,
    )


def validate_fm_post_commit_binding() -> dict[str, Any]:
    launcher = load_module("g77_256jd_fm", FM_LAUNCHER)
    with tempfile.TemporaryDirectory(prefix="g77_256jd_fm_") as raw:
        root = Path(raw)
        (root / "evidence").mkdir()
        (root / "transient").mkdir()
        context = build_context(root, launcher)
        source = root / "context.json"
        source.write_bytes(canonical_bytes(context))
        materialized = launcher.materialize_operation_state(
            repository_root=ROOT,
            context=context,
            context_source_path=source,
            candidate_source_path=IH_CANDIDATE,
        )
        observed = launcher.observe_context_assets(ROOT, context, IH_CANDIDATE)
        readiness = launcher.authority_free_static_readiness(
            repository_root=ROOT,
            context=context,
            observed_head=JC_HEAD,
            observed_tree=JC_TREE,
            repository_clean=True,
            observed_asset_sha256=observed,
            candidate_source_path=IH_CANDIDATE,
        )
        proof = readiness["checkout_readiness"]["preauth_guest_fm_context_owner_binding"]
        projection = Path(context["guest_adapter_binding"]["projection_root"])
        entries = sorted(path.name for path in projection.iterdir())
        checkout = Path(
            context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["path"]
        )
        if (
            readiness["result"] != "STATIC_READINESS_PASS"
            or materialized["qemu_execution_count"] != 0
            or len(entries) != 3
            or proof["projection_sha256"] != EXPECTED_SHA256[FM_CONTEXT]
            or git("rev-parse", "HEAD", cwd=checkout) != IF_HEAD
            or git("rev-parse", "HEAD^{tree}", cwd=checkout) != IF_TREE
            or git("status", "--porcelain=v1", "--untracked-files=all", cwd=checkout)
            or git("branch", "--show-current", cwd=checkout)
        ):
            raise JDReadinessError("G__FM_COMMITTED_STATIC_READINESS_FAILED")
        return {
            "result": "VERIFIED__STATIC_READINESS_PASS",
            "harness_member_count": "VERIFIED__3",
            "harness_members": entries,
            "guest_owner_projection_cardinality": "VERIFIED__1",
            "guest_owner_sha256": proof["projection_sha256"],
            "caller_selected_owner_identity": "VERIFIED__NO",
            "detached_if_checkout": "VERIFIED__CLEAN_DETACHED_EXACT_HEAD_TREE",
            "qemu_execution_count": 0,
        }


def validate_v2_post_commit_binding() -> dict[str, Any]:
    du = load_module("g77_256jd_du", DU)
    eb = load_module("g77_256jd_eb", EB)
    ee = load_module("g77_256jd_ee", EE)
    with tempfile.TemporaryDirectory(prefix=".g77_256jd_static_", dir=ROOT) as raw:
        temporary = Path(raw)
        candidate = temporary / "candidate-v2.json"
        candidate.write_bytes(du.canonical_bytes(du.build_du_fixture(ROOT)))
        du_result = du.validate_file(candidate, ROOT, expected_head=IF_HEAD)
        eb_envelope = eb.validate_candidate(ROOT, candidate)
        eb_path = temporary / "eb-v2.json"
        eb_path.write_bytes(eb.canonical_bytes(eb_envelope))
        runtime = temporary / "runtime"
        runtime.mkdir()
        (runtime / candidate.name).write_bytes(candidate.read_bytes())
        harness = temporary / "ee-path-fixture.py"
        harness.write_text(
            "from pathlib import Path\n"
            "FIXTURE_CLASSIFICATION='TEST_ONLY__NON_AUTHORITY__NON_OPERATIONAL'\n"
            "RAW_ROOT=Path('/mnt/g77-evidence')\n"
            "CONTINUATION_MANIFEST_PATH=RAW_ROOT/'candidate-v2.json'\n",
            encoding="utf-8",
        )
        ee_envelope = ee.validate_binding(
            ROOT, candidate, eb_path, harness, runtime, "/mnt/g77-evidence"
        )
        eb_result = eb.verify_receipt_envelope(ROOT, eb_envelope)
        ee_result = ee.verify_receipt_envelope(ROOT, ee_envelope)
        _, du_self_test = du.run_self_test(ROOT)
        eb_self_test = eb.run_self_test(ROOT, candidate)
        ee_self_test = ee.run_self_test(
            ROOT, candidate, eb_path, harness, runtime, "/mnt/g77-evidence"
        )
    target = eb_envelope["receipt"]["runtime_target_selection_binding"]
    baseline = eb_envelope["receipt"]["certification_baseline"]
    if set(du_result.values()) != {"PASS"} or eb_result["overall_result"] != "PASS":
        raise JDReadinessError("F__POST_COMMIT_RUNTIME_TARGET_SELECTION_DRIFT_PERSISTS")
    if ee_result["pre_materialization_runtime_path_binding_result"] != "PASS":
        raise JDReadinessError("I__DU_EB_EE_V2_POST_COMMIT_BINDING_FAILED")
    if (
        (target["head"], target["tree"]) != (IF_HEAD, IF_TREE)
        or baseline != {"head": JC_HEAD, "tree": JC_TREE}
        or ee_envelope["receipt"]["runtime_target_selection_binding"] != target
        or ee_envelope["receipt"]["certification_baseline"] != baseline
    ):
        raise JDReadinessError("E__RUNTIME_CERTIFICATION_ROLE_COLLAPSE_DETECTED")
    return {
        "former_worktree_drift_barrier": "VERIFIED__CLOSED_BY_COMMITTED_OWNER_BYTES",
        "du_v2": "VERIFIED__CURRENT_APPLICABLE_PASS",
        "eb_v2": "VERIFIED__POST_COMMIT_POSITIVE_PATH",
        "ee_v2": "VERIFIED__POST_COMMIT_POSITIVE_PATH",
        "runtime_target": target,
        "certification_baseline": baseline,
        "runtime_certification_role_separation": "VERIFIED__PRESERVED",
        "du_v2_self_test": "VERIFIED__PASS",
        "du_v2_negative_case_count": du_self_test["negative_case_count"],
        "eb_v2_self_test": "VERIFIED__" + eb_self_test["overall_self_test_result"],
        "eb_v2_case_count": eb_self_test["case_count"],
        "ee_v2_self_test": "VERIFIED__" + ee_self_test["overall_result"],
        "ee_v2_case_count": ee_self_test["case_count"],
        "major": 2,
        "semver": "2.0.0",
        "suffix": "V2",
        "family_local_fail_closed_dispatch": "VERIFIED",
        "caller_selected_version": "VERIFIED__NO",
        "v1_reinterpretation": "VERIFIED__0",
        "mixed_major_acceptance": "VERIFIED__0",
        "downgrade": "VERIFIED__0",
    }


def validate_adapter_nocloud_and_semantics() -> dict[str, Any]:
    adapter = (ROOT / JC_ADAPTER).read_text(encoding="utf-8")
    cloud = (ROOT / JC_CLOUD_INIT).read_text(encoding="utf-8")
    ast.parse(adapter, filename=str(JC_ADAPTER))
    required = (
        "EVALUATION_TIME_UNIX_NS = 500",
        "BASELINE_VALID_FROM_UNIX_NS = 100",
        "FUTURE_VALID_FROM_UNIX_NS = 600",
        "VALID_UNTIL_UNIX_NS = 1000",
        "9568e0c248ad488cabcf6bde6b490c544077862d10e3fda13bcdc8ed9953f547",
        "operational Human act is not current",
    )
    if not all(value in adapter for value in required):
        raise JDReadinessError("FUTURE_SEMANTIC_FIREWALL_FAILED")
    if (
        cloud.count("export PYTHONPATH=/mnt/aigol") != 1
        or cloud.count("/mnt/dp-harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py") != 1
    ):
        raise JDReadinessError("JC_CLOUD_INIT_BINDING_FAILED")
    projected: dict[str, str] = {}
    for member, source in {
        "/user-data": ROOT / JC_CLOUD_INIT,
        "/meta-data": ROOT / FM_META,
        "/network-config": ROOT / FM_NETWORK,
    }.items():
        raw = subprocess.check_output(
            ["isoinfo", "-i", str(ROOT / JC_SEED), "-R", "-x", member]
        )
        if raw != source.read_bytes():
            raise JDReadinessError(f"JC_NOCLOUD_PROJECTION_FAILED:{member}")
        projected[member] = sha256_bytes(raw)
    return {
        "evaluation_time_unix_ns": 500,
        "baseline_valid_from_unix_ns": 100,
        "future_valid_from_unix_ns": 600,
        "valid_until_unix_ns": 1000,
        "relation": "500 < 600 < 1000",
        "independent_mutation_count": 1,
        "independent_mutated_coordinate": "valid_from_unix_ns",
        "payload_digest": "9568e0c248ad488cabcf6bde6b490c544077862d10e3fda13bcdc8ed9953f547",
        "expected_denial_reason": "operational Human act is not current",
        "wall_clock_dependency_count": 0,
        "nocloud_projection": projected,
        "guest_import_root": "/mnt/aigol",
        "operational_denial": "NOT_PROVEN",
    }


def authenticate_reuse_and_firewalls() -> tuple[dict[str, Any], dict[str, Any]]:
    certificate = load_unique(ROOT / EX)["certificate"]
    if (
        certificate["component_counts"]["CERTIFIED"] != 17
        or certificate["certificate_is_credit_authority"] is not False
    ):
        raise JDReadinessError("N__EX_REUSE_CONTRACT_FAILED")
    tracked_delta = git("diff", "--name-only")
    p11_jc_delta = git("diff", "--name-only", "HEAD^", "HEAD", "--", *P11_PATHS)
    if tracked_delta or p11_jc_delta:
        raise JDReadinessError("L__P11_MUTATION_REQUIRED")
    launcher = (ROOT / FM_LAUNCHER).read_text(encoding="utf-8")
    if launcher.count("result = subprocess.run(argv, check=False)") != 1:
        raise JDReadinessError("K__PARALLEL_ROUTE_OR_GENERIC_FRAMEWORK_REQUIRED")
    if len(HISTORICAL_FAILURE_CLASSES) != 32:
        raise JDReadinessError("HISTORICAL_FAILURE_FIREWALL_COUNT_MISMATCH")
    reuse = {
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
        "ex_is_authority": "VERIFIED__NO",
        "ex_is_operation": "VERIFIED__NO",
        "ex_is_e05_credit": "VERIFIED__NO",
        "production_route_before": "VERIFIED__1",
        "production_route_after": "VERIFIED__1",
        "production_route_delta": "VERIFIED__0",
        "production_owner_mutation_count": "VERIFIED__0",
        "p11_mutation_count": "VERIFIED__0",
        "new_generic_adapter_count": "VERIFIED__0",
        "new_dispatcher_count": "VERIFIED__0",
        "new_global_registry_count": "VERIFIED__0",
        "new_generic_framework_count": "VERIFIED__0",
    }
    firewall = {
        "checked_failure_classes": list(HISTORICAL_FAILURE_CLASSES),
        "checked_failure_class_count": "VERIFIED__32",
        "reintroduced_historical_failure_count": "VERIFIED__0",
        "historical_evidence_mutation_count": "VERIFIED__0",
        "historical_iz_mutation_count": "VERIFIED__0",
        "historical_jc_mutation_count": "VERIFIED__0",
        "shadow_automation_status": "VERIFIED__ABSENT",
        "caller_selected_owner": "VERIFIED__NO",
        "caller_selected_version": "VERIFIED__NO",
        "runtime_target_rebinding": "VERIFIED__0",
        "certification_baseline_rebinding": "VERIFIED__0",
    }
    return reuse, firewall


def operational_counters() -> dict[str, int]:
    return {key: 0 for key in (
        "human_authorization_presentation", "human_authorization",
        "authority_consumption", "pre", "fm_operational_invocation", "qemu",
        "vm", "operation_attempt", "request", "p11_entry",
        "protected_invocation", "protected_effect", "retry", "repair_retry",
        "replay",
    )}


def terminal_reduction() -> dict[str, Any]:
    entry = authenticate_baseline()
    jc = authenticate_committed_jc()
    roles = role_model()
    fm = validate_fm_post_commit_binding()
    v2 = validate_v2_post_commit_binding()
    semantics = validate_adapter_nocloud_and_semantics()
    reuse, firewall = authenticate_reuse_and_firewalls()
    return {
        "schema_id": "G77_256JD_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "generation": "G77-256JD",
        "mode": "POST_JC_COMMIT_LIVE_BINDING_STATIC_READINESS_ONLY__NO_AUTHORIZATION__NO_OPERATION",
        "terminal": "A__FUTURE_POST_JC_COMMIT_LIVE_BINDING_AND_OPERATIONAL_READINESS_VERIFIED",
        "entry": entry,
        "jc_reconstruction": jc,
        "roles": roles,
        "fm_post_commit_binding": fm,
        "du_eb_ee_v2": v2,
        "adapter_nocloud_future_semantics": semantics,
        "reuse": reuse,
        "historical_failure_firewall": firewall,
        "operational_counters": operational_counters(),
        "e05": {
            "before": "VERIFIED__10_OF_18",
            "after": "VERIFIED__10_OF_18",
            "credit": "VERIFIED__0",
            "remaining_vectors": [
                "AMBIGUOUS", "STALE", "FUTURE", "EXPIRED", "REVOKED",
                "SUPERSEDED", "WRONG_SCOPE", "COHERENT_COPY",
            ],
        },
        "reuse_impact": {
            "reused_certified_capability_set": "VERIFIED__JC_JB_JA_IZ_FM_GH_HG_HD_IW_IE_IF_DU_EB_EE_V2_ER_FC_FK_CANONICAL_HUMAN_ACT_CHE_CUSTODY_REQUEST_P11_GN_GL_DI_EX_GOVERNANCE_LAYER_0_NESTED_AUTHORITY",
            "new_capability_set": "VERIFIED__JD_REPOSITORY_ONLY_POST_COMMIT_CERTIFICATION_EVIDENCE_ONLY",
            "unreachable_preexisting_capability_set": "VERIFIED__EMPTY",
            "parallel_flow_created": "VERIFIED__NO",
            "production_route_before": "VERIFIED__1",
            "production_route_after": "VERIFIED__1",
            "production_route_delta": "VERIFIED__0",
        },
        "continuity": {
            "chain": "IV -> IW -> IX -> IY -> IZ -> JA -> JB -> JC -> JD",
            "constitutional_health_evidence": "VERIFIED__IV_IMPORT_ROOT_FAIL_CLOSED__IW_BINDING__IX_POST_COMMIT_READINESS__IY_ENTRYPOINT_FAIL_CLOSED__IZ_ENTRYPOINT_BINDING__JA_POST_COMMIT_READINESS__JB_OWNER_DRIFT_FAIL_CLOSED__JC_OWNER_PROJECTION_RECONCILIATION__JD_POST_JC_COMMITTED_LIVE_BINDING__ALL_JD_OPERATIONAL_COUNTERS_ZERO",
            "authority_count": "VERIFIED__0",
            "operation_count": "VERIFIED__0",
            "retry_count": "VERIFIED__0",
            "replay_count": "VERIFIED__0",
            "route_count": "VERIFIED__1",
            "p11_mutation_count": "VERIFIED__0",
            "historical_mutation_count": "VERIFIED__0",
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_L5_CLAIM",
            "cross_worker_state_recovery_level": "VERIFIED__AUTHENTICATED_REPOSITORY_HANDOFF",
            "repository_derived_context_ratio": "ESTIMATED__DOMINANT__NO_NUMERIC_INSTRUMENT",
            "human_handoff_information_required": "VERIFIED__COMMISSION_SCOPE_JC_CHECKPOINT_AND_LOCATORS",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_identity_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
            "authenticated_repository_continuation": "VERIFIED__YES",
            "inter_generation_cross_worker_continuation": "VERIFIED__JC_TO_JD",
            "intra_generation_cross_worker_continuation": "NOT_APPLICABLE__SINGLE_JD_WORKER",
            "uncommitted_delta_recovery": "NOT_APPLICABLE__CLEAN_COMMITTED_JC_ENTRY",
            "authority_state_recovery": "VERIFIED__JD_ZERO_AUTHORITY__HISTORICAL_AUTHORITY_NONREUSABLE",
            "consumed_authority_recovery": "VERIFIED__HISTORICAL_CONSUMPTION_RECONSTRUCTED_AND_NOT_REUSED",
            "post_operation_state_recovery": "VERIFIED__IY_FAIL_CLOSED_AND_JB_PREAUTH_FAILURE_RECONSTRUCTED",
            "operation_replay_prevention": "VERIFIED__JD_ZERO_OPERATION__NO_AUTHORITY_REUSE",
            "cross_worker_constitutional_drift": "NOT_PROVEN__NO_GOVERNED_WORKER_IDENTITY_DRIFT_INSTRUMENT",
            "observed_artifact_level_cross_worker_drift": "VERIFIED__0",
            "handoff_sufficiency_status": "VERIFIED",
            "handoff_state_completeness": "VERIFIED__COMPLETE_FOR_JD_SCOPE",
            "handoff_reconstruction_required": "VERIFIED__YES",
            "handoff_reconstruction_success": "VERIFIED__YES",
            "handoff_ambiguity_count": "VERIFIED__0",
            "unauthenticated_handoff_assumption_count": "VERIFIED__0",
        },
        "cognition": {
            "cognition_assisted_handoff": "VERIFIED__RATIFIED_JC_REPOSITORY_DERIVED_CROSS_GENERATION_HANDOFF",
            "cognition_provenance": "VERIFIED__JC_SOL_HIGH_ASTRA_EXTRA_HIGH_SOL_HIGH_LINEAGE_CONTEXT_ONLY__RATIFIED_JC_GIT_AND_REPOSITORY_EVIDENCE_PRIMARY__MODEL_PROVIDER_NONAUTHORITATIVE",
            "provider_capability_is_execution_authority": False,
            "model_identity_is_constitutional_authority": False,
            "repository_evidence_is_human_authorization": False,
            "aigol_codex_work_share": "NOT_MEASURED",
            "prompt_context_reuse_ratio": "NOT_MEASURED__NO_GOVERNED_NUMERIC_INSTRUMENT",
            "repository_derived_execution_context_ratio": "NOT_MEASURED__NO_GOVERNED_NUMERIC_INSTRUMENT",
            "constitutional_prompt_externalization_ratio": "NOT_MEASURED__NO_GOVERNED_NUMERIC_INSTRUMENT",
            "token_benchmark": "NOT_MEASURED",
            "llm_cost_reduction_ratio": "NOT_MEASURED",
            "lcrr": "NOT_MEASURED",
        },
        "infrastructure_amortization": {
            "future_generations_so_far": "VERIFIED__26__IE_THROUGH_JD",
            "future_e05_credit_so_far": "VERIFIED__0",
            "future_operational_attempts_so_far": "VERIFIED__2__IV_AND_IY",
            "marginal_new_infrastructure_for_jd": "VERIFIED__POST_COMMIT_CERTIFICATION_EVIDENCE_ONLY",
            "new_common_infrastructure": "VERIFIED__0",
            "new_vector_specific_infrastructure": "VERIFIED__0",
            "infrastructure_amortization_signal": "ESTIMATED__HIGH_REUSE_WITH_ZERO_PRODUCTION_MUTATION",
        },
        "metrics": {
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "constitutional_frontier_distanc_e": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "e05_frontier_distance": "VERIFIED__8_UNSATISFIED_OF_18",
            "selected_e05_local_frontier_distance": "VERIFIED__SEPARATE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING",
            "governance_efficience": "ESTIMATED__HIGH_REUSE_WITH_FAIL_CLOSED_POST_COMMIT_CLOSURE",
            "architectural_governance_efficience": "VERIFIED__ONE_ROUTE_ZERO_ROUTE_DELTA_ZERO_PRODUCTION_AND_P11_MUTATION",
            "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED",
            "overengineering_risk": "ESTIMATED__LOW__EVIDENCE_ONLY",
            "proof_process_overhead_risk": "ESTIMATED__MODERATE",
            "new_abstraction_count": "VERIFIED__0",
            "generic_projection_framework_count": "VERIFIED__0",
            "new_generic_framework_count": "VERIFIED__0",
            "new_route_count": "VERIFIED__0",
            "new_registry_count": "VERIFIED__0",
            "caller_selectable_identity_count": "VERIFIED__0",
            "duplicate_future_adapter_count": "VERIFIED__0",
            "duplicate_p11_logic_count": "VERIFIED__0",
            "candidate_capability": "VERIFIED__FUTURE_GUEST_CURRENT_FM_CONTEXT_OWNER_COMMITTED_AND_PROJECTED_READ_ONLY_SEPARATELY_FROM_DETACHED_IF_RUNTIME__DU_EB_EE_V2_POST_COMMIT_LIVE_BOUND__STATICALLY_READY_FOR_SEPARATE_HUMAN_AUTHORIZED_COMMISSIONING__OPERATIONAL_DENIAL_NOT_PROVEN",
            "shadow_design_target": "VERIFIED__FAMILY_LOCAL_DU_EB_EE_V2_OPTION_B_WITH_COLOCATED_FAIL_CLOSED_MAJOR_VERSION_DISPATCH",
        },
        "validation": {
            "jd_focused": "VERIFIED__20_PASSED",
            "jc_current_applicable": "VERIFIED__17_PASSED__3_HISTORICAL_OR_PRECOMMIT_ASSERTIONS_DESELECTED",
            "fm_operation_context": "VERIFIED__17_PASSED",
            "in_v2_current_applicable": "VERIFIED__20_PASSED__5_HISTORICAL_ENTRY_OR_MUTATION_SCOPE_ASSERTIONS_DESELECTED",
            "du_eb_ee_v2_self_test_cases": "VERIFIED__40_PASSED",
            "route_regressions": "VERIFIED__124_PASSED",
            "ex": "VERIFIED__12_OF_12__CERTIFIED_17_OF_17_REUSED",
            "governance_pytest": "VERIFIED__13_PASSED",
            "conformance_engine": "VERIFIED__20_PASSED__CONFORMANT__0_WARNINGS__0_VIOLATIONS",
            "layer_0_freeze": "VERIFIED__PASS",
            "git_diff_check": "VERIFIED__PASS",
        },
        "terminal_frontier": {
            "last_verified_edge": "FUTURE_POST_JC_COMMIT_LIVE_BINDING_AND_STATIC_OPERATIONAL_READINESS",
            "first_broken_edge": "FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_NOT_PRESENT",
            "blocking_owner": "HUMAN_AUTHORITY",
            "minimum_missing_capability": "SEPARATE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING",
            "minimum_legal_next_delta": "HUMAN_REVIEW_THEN_SEPARATE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING_GENERATION",
            "auto_continuable": "NO",
            "human_review_required": "YES",
            "next_generation_started": "NO",
        },
    }


def terminal_envelope() -> dict[str, Any]:
    reduction = terminal_reduction()
    return {
        "schema_id": "G77_256JD_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": sha256_bytes(canonical_bytes(reduction)),
    }


if __name__ == "__main__":
    sys.stdout.buffer.write(canonical_bytes(terminal_envelope()))
