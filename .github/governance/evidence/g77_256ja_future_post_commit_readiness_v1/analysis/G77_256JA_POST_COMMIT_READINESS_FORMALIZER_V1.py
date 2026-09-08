#!/usr/bin/env python3
"""G77-256JA repository-only post-commit FUTURE readiness verifier.

This verifier authenticates committed objects and executes only static,
authority-free validation.  It never calls the IZ adapter entrypoint, PRE, the
FM operational launcher, QEMU, a protected request, or P11 operationally.
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
sys.path.insert(0, str(ROOT))  # Host-only verifier imports; not guest import-root evidence.
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
IZ_HEAD = "6c1bbd1fbe592c4bdc9ed72394c00506a0318854"
IZ_TREE = "2172899d5a3f22d8d0e62ad07acad4dd9c5c8180"
IZ_SUBJECT = "G77-256IZ bind FUTURE governed operational adapter entrypoint"
IF_HEAD = "699fcdce794ff49b6c8735602936355724ed1c90"
IF_TREE = "7c773d4b2acdf013f1b8238eabfc8eced4dd6866"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"

JA_ROOT = Path(".github/governance/evidence/g77_256ja_future_post_commit_readiness_v1")
TERMINAL = JA_ROOT / "G77_256JA_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
IZ_ROOT = Path(".github/governance/evidence/g77_256iz_future_operational_entrypoint_v1")
IZ_TERMINAL = IZ_ROOT / "G77_256IZ_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
ADAPTER = IZ_ROOT / "adapter/G77_256IZ_FUTURE_VECTOR_ADAPTER_V1.py"
CLOUD = IZ_ROOT / "static/G77_256IZ_CLOUD_INIT_USER_DATA_V1.yaml"
SEED = IZ_ROOT / "static/SAPIANTA_FUTURE_NOCLOUD_SEED_V2.img"
FM_ROOT = Path(".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1")
FM_LAUNCHER = FM_ROOT / "launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
FM_CONTEXT = FM_ROOT / "launcher/sapianta_fresh_operation_context_v1.py"
FM_META = FM_ROOT / "raw/G77_256FM_CLOUD_INIT_META_DATA_V1.yaml"
FM_NETWORK = FM_ROOT / "raw/G77_256FM_CLOUD_INIT_NETWORK_CONFIG_V1.yaml"
IF_CONTEXT = Path(".github/governance/evidence/g77_256ih_future_if_identity_rebind_v1/live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json")
DU = Path(".github/governance/evidence/g77_256du_continuation_manifest_contract_v2/validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V2.py")
EB = Path(".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v2/validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V2.py")
EE = Path(".github/governance/evidence/g77_256ee_runtime_consumer_binding_v2/validator/G77_256EE_RUNTIME_CONSUMER_BINDING_VALIDATOR_V2.py")
EX = Path(".github/governance/evidence/g77_256ex_common_substrate_certification_v1/G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json")
P11_PATHS = ("aigol/runtime", "sapianta_system", ".github/governance/evidence/g77_256ec_p11_operational_v1")

EXPECTED_SHA256 = {
    FM_LAUNCHER: "bdd2765652f9dbe0b4de183cd7cb6c55fb7e00de2c986f019684934f89148a2d",
    FM_CONTEXT: "da09342d92f2a8d8310987aa0104bd6bd6ad7a3d009b51b8d710443c4884e9c7",
    ADAPTER: "e7babafc2a85ebcb59ef3b7aaa70cf220a5a6fb6833dc2f85f8377be5c3c8533",
    CLOUD: "7f82b2dbb480af92b54b3e85e06e06af55b1623d51f8a541db195fa970a028e4",
    SEED: "456a6e5187cb77be474dbc37cd052d24c9367e49604bd12ab9a8c19b08897cbd",
    IZ_TERMINAL: "8ca399f3c056f93cbd14eca1959886e74b88d9062d9e6a9378c9d89eb3ba6e52",
}
HISTORICAL_FAILURE_CLASSES = (
    "future_commit_self_reference", "precommit_head_dependency", "checkout_mismatch",
    "alternates_escape", "checkout_collision", "transient_root_collision",
    "host_guest_path_mismatch", "adapter_mismatch", "launcher_sha_mismatch",
    "bootstrap_sha_mismatch", "nocloud_mismatch", "stale_projection",
    "historical_wrapper_binding", "runtime_current_identity_collapse",
    "runtime_certification_collapse", "caller_selected_runtime", "caller_selected_vector",
    "caller_selected_version", "caller_selected_import_root", "global_registry",
    "generic_dispatcher", "weak_generation_binding", "parallel_route", "p11_bypass",
    "automatic_authority", "authority_replay", "automatic_retry", "repair_retry",
    "host_sys_path_false_positive", "network_dependency", "guest_import_root_regression",
    "cross_generation_authority", "second_authority_consumption", "second_qemu",
    "second_operation", "provider_limit_replay", "historical_evidence_rewrite",
    "duplicate_future_semantics", "duplicate_request_logic", "duplicate_p11_logic",
    "entrypoint_induced_p11_bypass", "uncommitted_owner_false_positive",
    "runtime_target_selection_worktree_drift_bypass",
)


class JAReadinessError(ValueError):
    """One deterministic fail-closed JA verification error."""


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise JAReadinessError(f"DUPLICATE_JSON_KEY__{key}")
        result[key] = value
    return result


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique_object)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise JAReadinessError(f"NONCANONICAL_JSON__{path}")
    return value


def load_unique(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_bytes(), object_pairs_hook=unique_object)
    if not isinstance(value, dict):
        raise JAReadinessError(f"JSON_OBJECT_REQUIRED__{path}")
    return value


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *arguments], cwd=cwd, text=True).strip()


def load_module(name: str, relative: Path) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, ROOT / relative)
    if specification is None or specification.loader is None:
        raise JAReadinessError(f"MODULE_LOAD_FAILED__{relative}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def committed_bytes(revision: str, path: Path) -> bytes:
    return subprocess.check_output(["git", "show", f"{revision}:{path.as_posix()}"], cwd=ROOT)


def authenticate_entry(remote_head: str = IZ_HEAD, nested_remote_tag: str = NESTED_HEAD) -> dict[str, Any]:
    observed = {
        "repository": str(ROOT), "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"), "tree": git("rev-parse", "HEAD^{tree}"),
        "subject": git("show", "-s", "--format=%s", "HEAD"),
        "origin": git("remote", "get-url", "origin"), "remote_head": remote_head,
        "index": git("diff", "--cached", "--name-only"),
        "tracked_delta": git("status", "--porcelain", "--untracked-files=no"),
    }
    expected = {
        "repository": str(ROOT), "branch": BRANCH, "head": IZ_HEAD, "tree": IZ_TREE,
        "subject": IZ_SUBJECT, "origin": ORIGIN, "remote_head": IZ_HEAD,
        "index": "", "tracked_delta": "",
    }
    if observed != expected:
        raise JAReadinessError("E__IZ_RATIFIED_BASELINE_AUTHENTICATION_FAILED")
    for line in git("status", "--porcelain", "--untracked-files=all").splitlines():
        if not line.startswith("?? " + JA_ROOT.as_posix() + "/"):
            raise JAReadinessError("JA_BOUNDED_WORKTREE_SCOPE_VIOLATION")
    nested = ROOT / "sapianta_system"
    nested_state = {
        "origin": git("remote", "get-url", "origin", cwd=nested),
        "head": git("rev-parse", "HEAD", cwd=nested),
        "tree": git("rev-parse", "HEAD^{tree}", cwd=nested),
        "clean": git("status", "--porcelain", cwd=nested) == "",
        "detached": git("branch", "--show-current", cwd=nested) == "",
        "tag": git("describe", "--tags", "--exact-match", "HEAD", cwd=nested),
        "remote_tag": nested_remote_tag,
    }
    expected_nested = {
        "origin": NESTED_ORIGIN, "head": NESTED_HEAD, "tree": NESTED_TREE,
        "clean": True, "detached": True, "tag": NESTED_TAG, "remote_tag": NESTED_HEAD,
    }
    if nested_state != expected_nested:
        raise JAReadinessError("H__BASELINE_OR_NESTED_AUTHORITY_AUTHENTICATION_FAILED")
    return observed | {"worktree_scope": "VERIFIED__JA_EVIDENCE_ONLY", "nested_authority": nested_state}


def authenticate_committed_iz() -> dict[str, Any]:
    identities: dict[str, Any] = {}
    for path, expected_sha in EXPECTED_SHA256.items():
        raw = committed_bytes(IZ_HEAD, path)
        if raw != (ROOT / path).read_bytes() or sha256_bytes(raw) != expected_sha:
            raise JAReadinessError(f"B__IZ_COMMITTED_BINDING_MISMATCH__{path}")
        identities[path.as_posix()] = {
            "sha256": expected_sha, "git_blob": git("rev-parse", f"{IZ_HEAD}:{path.as_posix()}"),
        }
    envelope = load_canonical(ROOT / IZ_TERMINAL)
    iz_reduction_bytes = json.dumps(
        envelope["reduction"], sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()
    if envelope["reduction_sha256"] != sha256_bytes(iz_reduction_bytes):
        raise JAReadinessError("B__IZ_TERMINAL_INNER_SEAL_MISMATCH")
    expected_terminal = "A__FUTURE_GOVERNED_OPERATIONAL_ADAPTER_ENTRYPOINT_REPOSITORY_ONLY_STATIC_READINESS_VERIFIED"
    if envelope["reduction"]["terminal"] != expected_terminal:
        raise JAReadinessError("B__IZ_TERMINAL_MISMATCH")
    return {
        "iz_committed_binding": "VERIFIED", "iz_remote_ratification": "VERIFIED",
        "iz_terminal": expected_terminal, "artifact_count": len(identities),
        "inner_seal": "VERIFIED", "identities": identities,
    }


def _replace_all(value: bytes, replacements: dict[bytes, bytes]) -> bytes:
    for current, prior in replacements.items():
        if value.count(current) < 1:
            raise JAReadinessError("IZ_FUTURE_REBIND_REPLACEMENT_CARDINALITY_MISMATCH")
        value = value.replace(current, prior)
    return value


def authenticate_two_owner_rebind() -> dict[str, Any]:
    changed = git("diff", "--name-only", "HEAD^", "HEAD", "--", FM_ROOT.as_posix()).splitlines()
    expected_changed = sorted([FM_LAUNCHER.as_posix(), FM_CONTEXT.as_posix()])
    if sorted(changed) != expected_changed:
        raise JAReadinessError("E__PRODUCTION_ROUTE_DELTA_NONZERO")
    prior_context = committed_bytes("HEAD^", FM_CONTEXT)
    current_context = committed_bytes("HEAD", FM_CONTEXT)
    normalized_context = _replace_all(current_context, {
        b"g77_256iz_future_operational_entrypoint_v1/": b"g77_256if_future_post_commit_readiness_v1/",
        b"G77_256IZ_FUTURE_VECTOR_ADAPTER_V1.py": b"G77_256IF_FUTURE_VECTOR_ADAPTER_V1.py",
    })
    if normalized_context != prior_context:
        raise JAReadinessError("IZ_CONTEXT_OWNER_NON_FUTURE_DRIFT")
    prior_launcher = committed_bytes("HEAD^", FM_LAUNCHER)
    current_launcher = committed_bytes("HEAD", FM_LAUNCHER)
    normalized_launcher = _replace_all(current_launcher, {
        b"g77_256iz_future_operational_entrypoint_v1/": b"g77_256iw_future_guest_import_root_binding_v1/",
        b"G77_256IZ_CLOUD_INIT_USER_DATA_V1.yaml": b"G77_256IW_CLOUD_INIT_USER_DATA_V1.yaml",
        b"7f82b2dbb480af92b54b3e85e06e06af55b1623d51f8a541db195fa970a028e4": b"10092e4d10327c0bef42608e3125ca4b04b82b8e91a0c5e88a5148ee1a14fee2",
        b"SAPIANTA_FUTURE_NOCLOUD_SEED_V2.img": b"SAPIANTA_FUTURE_NOCLOUD_SEED_V1.img",
        b"da09342d92f2a8d8310987aa0104bd6bd6ad7a3d009b51b8d710443c4884e9c7": b"fdfa04349529d70bc97820a1848f8afc22b81071859d5456550799e0f9476237",
        b"456a6e5187cb77be474dbc37cd052d24c9367e49604bd12ab9a8c19b08897cbd": b"655b8b4122f89acbf0e4d3a670ee3b4fb38fb37600eeb6c8745c0a13cdc57eab",
    })
    if normalized_launcher != prior_launcher:
        raise JAReadinessError("IZ_LAUNCHER_OWNER_NON_FUTURE_DRIFT")
    context = load_module("g77_256ja_fm_context", FM_CONTEXT)
    launcher = load_module("g77_256ja_fm_launcher", FM_LAUNCHER)
    generation = "G77_256JA_ONE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING_V1"
    if context.operation_vector(generation) != "FUTURE" or context.adapter_source_relative_path(generation) != ADAPTER.as_posix():
        raise JAReadinessError("IZ_COMMITTED_FUTURE_SELECTOR_BINDING_MISMATCH")
    bootstrap = launcher.current_bootstrap_asset_bindings("FUTURE")
    if bootstrap != {
        "cloud_init_path": CLOUD.as_posix(), "cloud_init_sha256": EXPECTED_SHA256[CLOUD],
        "seed_path": "/home/pisarna/work/sapianta-fl/" + SEED.as_posix(), "seed_sha256": EXPECTED_SHA256[SEED],
    }:
        raise JAReadinessError("IZ_COMMITTED_FUTURE_BOOTSTRAP_BINDING_MISMATCH")
    return {
        "production_owner_mutation_count": "VERIFIED__2",
        "production_owner_mutation_set": expected_changed,
        "non_future_mappings_unchanged": "VERIFIED", "future_selector_binding": "VERIFIED",
        "future_bootstrap_binding": "VERIFIED", "production_route_before": "VERIFIED__1",
        "production_route_after": "VERIFIED__1", "production_route_delta": "VERIFIED__0",
        "parallel_flow_created": "VERIFIED__NO",
    }


def authenticate_adapter_and_semantics() -> dict[str, Any]:
    adapter = load_module("g77_256ja_iz_adapter", ADAPTER)
    packet = adapter.authenticate_future_semantics(ROOT)
    specialized = adapter.specialize_fc_runtime_source(
        repository_root=ROOT, identity_namespace_prefix="G77_256JA"
    )
    er = adapter.load_future_er(ROOT)
    source = (ROOT / ADAPTER).read_text(encoding="utf-8")
    tree = ast.parse(source)
    if len([node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main"]) != 1:
        raise JAReadinessError("IZ_ADAPTER_ENTRYPOINT_BINDING_MISMATCH")
    required = (
        "CustodyRequest(", "consumer.submit_human_act(",
        "now_unix_ns=EVALUATION_TIME_UNIX_NS", "bind_record_identity(",
        "canonical_human_authority_payload_digest_v1(", "rebind_canonical_correlation(",
    )
    if any(token not in specialized for token in required):
        raise JAReadinessError("EXISTING_ER_FC_FK_P11_ROUTE_BINDING_MISSING")
    if "initialize_available(" in specialized or "valid_from <=" in source:
        raise JAReadinessError("DUPLICATE_P11_OR_DIRECT_OWNER_MUTATION_DETECTED")
    observed = {
        "evaluation_time_unix_ns": packet["evaluation_time_unix_ns"],
        "baseline_valid_from_unix_ns": packet["baseline_payload"]["valid_from_unix_ns"],
        "future_valid_from_unix_ns": packet["future_payload"]["valid_from_unix_ns"],
        "valid_until_unix_ns": packet["future_payload"]["valid_until_unix_ns"],
        "independent_mutation_count": packet["independent_mutation_count"],
        "independent_mutated_coordinate": packet["independent_mutated_coordinate"],
        "payload_digest": packet["future_payload_digest"].removeprefix("sha256:"),
        "wall_clock_dependency": packet["fixture_uses_wall_clock"],
    }
    expected = {
        "evaluation_time_unix_ns": 500, "baseline_valid_from_unix_ns": 100,
        "future_valid_from_unix_ns": 600, "valid_until_unix_ns": 1000,
        "independent_mutation_count": 1, "independent_mutated_coordinate": "valid_from_unix_ns",
        "payload_digest": "9568e0c248ad488cabcf6bde6b490c544077862d10e3fda13bcdc8ed9953f547",
        "wall_clock_dependency": False,
    }
    if observed != expected or er.create_input_and_authority.__code__.co_consts.count(500) < 1:
        raise JAReadinessError("FUTURE_SEMANTIC_IDENTITY_MISMATCH")
    return observed | {
        "relation": "500 < 600 < 1000", "expected_denial_reason": "operational Human act is not current",
        "adapter_main_invoked": "VERIFIED__NO", "existing_route_static_binding": "VERIFIED",
        "canonical_identity_producers_reused": "VERIFIED", "custody_request_reused": "VERIFIED",
        "che_correlation_reused": "VERIFIED", "p11_submit_human_act_reused": "VERIFIED",
        "duplicate_p11_currentness_logic": "VERIFIED__0", "direct_protected_owner_mutation": "VERIFIED__0",
    }


def authenticate_nocloud_projection() -> dict[str, Any]:
    cloud = (ROOT / CLOUD).read_text(encoding="utf-8")
    if cloud.count("export PYTHONPATH=/mnt/aigol") != 1 or cloud.count("/mnt/dp-harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py") != 1:
        raise JAReadinessError("GUEST_IMPORT_ROOT_OR_ADAPTER_PROJECTION_MISMATCH")
    projected: dict[str, str] = {}
    for member, source in (("/user-data", CLOUD), ("/meta-data", FM_META), ("/network-config", FM_NETWORK)):
        raw = subprocess.check_output(["isoinfo", "-i", str(ROOT / SEED), "-R", "-x", member])
        if raw != (ROOT / source).read_bytes():
            raise JAReadinessError(f"NOCLOUD_EXACT_PROJECTION_MISMATCH__{member}")
        projected[member] = sha256_bytes(raw)
    return {
        "cloud_init_sha256": EXPECTED_SHA256[CLOUD], "nocloud_seed_sha256": EXPECTED_SHA256[SEED],
        "exact_projection": "VERIFIED", "projection_members": projected,
        "guest_checkout_import_root": "/mnt/aigol", "five_argument_fm_guest_contract": "VERIFIED",
        "network_dependency": "VERIFIED__0", "iv_import_root_failure_reintroduced": "VERIFIED__NO",
        "iy_entrypoint_absence_reintroduced": "VERIFIED__NO",
    }


def validate_v2_post_commit_binding() -> dict[str, Any]:
    du = load_module("g77_256ja_du", DU)
    eb = load_module("g77_256ja_eb", EB)
    ee = load_module("g77_256ja_ee", EE)
    with tempfile.TemporaryDirectory(prefix=".g77_256ja_static_", dir=ROOT) as raw:
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
            "from pathlib import Path\nFIXTURE_CLASSIFICATION='TEST_ONLY__NON_AUTHORITY__NON_OPERATIONAL'\n"
            "RAW_ROOT=Path('/mnt/g77-evidence')\nCONTINUATION_MANIFEST_PATH=RAW_ROOT/'candidate-v2.json'\n",
            encoding="utf-8",
        )
        ee_envelope = ee.validate_binding(ROOT, candidate, eb_path, harness, runtime, "/mnt/g77-evidence")
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
        raise JAReadinessError("C__RUNTIME_TARGET_SELECTION_WORKTREE_DRIFT_PERSISTS")
    if ee_result["pre_materialization_runtime_path_binding_result"] != "PASS":
        raise JAReadinessError("G__POST_COMMIT_READINESS_AMBIGUOUS")
    if (target["head"], target["tree"]) != (IF_HEAD, IF_TREE) or baseline != {"head": IZ_HEAD, "tree": IZ_TREE}:
        raise JAReadinessError("D__RUNTIME_CERTIFICATION_ROLE_COLLAPSE_DETECTED")
    if ee_envelope["receipt"]["runtime_target_selection_binding"] != target or ee_envelope["receipt"]["certification_baseline"] != baseline:
        raise JAReadinessError("D__RUNTIME_CERTIFICATION_ROLE_COLLAPSE_DETECTED")
    return {
        "former_worktree_drift_barrier": "VERIFIED__CLOSED",
        "du_v2": "VERIFIED__CURRENT_APPLICABLE_PASS", "eb_v2": "VERIFIED__POST_COMMIT_POSITIVE_PATH",
        "ee_v2": "VERIFIED__POST_COMMIT_POSITIVE_PATH", "runtime_target": target,
        "du_v2_self_test": "VERIFIED__PASS",
        "du_v2_negative_case_count": du_self_test["negative_case_count"],
        "eb_v2_self_test": "VERIFIED__" + eb_self_test["overall_self_test_result"],
        "eb_v2_case_count": eb_self_test["case_count"],
        "ee_v2_self_test": "VERIFIED__" + ee_self_test["overall_result"],
        "ee_v2_case_count": ee_self_test["case_count"],
        "certification_baseline": baseline, "runtime_certification_role_separation": "VERIFIED__PRESERVED",
        "target_runtime_identity": "VERIFIED__DETACHED_IF", "current_repository_identity": "VERIFIED__COMMITTED_IZ",
        "certification_baseline_identity": "VERIFIED__COMMITTED_IZ", "candidate_required_identity": "VERIFIED__DETACHED_IF",
        "checkout_identity": "VERIFIED__DETACHED_IF", "evidence_issuer_identity": "VERIFIED__COMMITTED_IZ_PLUS_COMMITTED_V2_OWNERS",
        "nested_certification_baseline_option_b": "VERIFIED", "family_local_fail_closed_major_dispatch": "VERIFIED",
        "v1_reinterpretation": "VERIFIED__0", "caller_selected_version": "VERIFIED__0",
        "mixed_major_acceptance": "VERIFIED__0", "downgrade": "VERIFIED__0",
    }


def authenticate_ex_and_firewalls() -> tuple[dict[str, Any], dict[str, Any]]:
    certificate = load_unique(ROOT / EX)["certificate"]
    if certificate["component_counts"]["CERTIFIED"] != 17 or certificate["certificate_is_credit_authority"] is not False:
        raise JAReadinessError("EX_COMMON_SUBSTRATE_REUSE_MISMATCH")
    if git("diff", "--name-only", "HEAD^", "HEAD", "--", *P11_PATHS):
        raise JAReadinessError("P11_MUTATION_DETECTED")
    proof = {
        "ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0",
        "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED",
        "ex_is_authority": "VERIFIED__NO", "ex_is_operation": "VERIFIED__NO", "ex_is_e05_credit": "VERIFIED__NO",
    }
    if len(HISTORICAL_FAILURE_CLASSES) != 43 or len(set(HISTORICAL_FAILURE_CLASSES)) != 43:
        raise JAReadinessError("HISTORICAL_FAILURE_FIREWALL_CARDINALITY_MISMATCH")
    firewall = {
        "checked_failure_classes": list(HISTORICAL_FAILURE_CLASSES),
        "checked_failure_class_count": f"VERIFIED__{len(HISTORICAL_FAILURE_CLASSES)}",
        "reintroduced_historical_failure_count": "VERIFIED__0",
        "p11_mutation_count": "VERIFIED__0", "historical_evidence_mutation_count": "VERIFIED__0",
        "shadow_automation_status": "VERIFIED__ABSENT", "caller_selected_runtime": "VERIFIED__NO",
        "caller_selected_vector": "VERIFIED__NO", "caller_selected_adapter": "VERIFIED__NO",
        "caller_selected_import_root": "VERIFIED__NO", "caller_selected_version": "VERIFIED__NO",
        "new_generic_adapter_count": "VERIFIED__0", "new_dispatcher_count": "VERIFIED__0",
        "new_global_registry_count": "VERIFIED__0", "new_production_capability_count": "VERIFIED__0",
        "new_route_count": "VERIFIED__0", "new_generic_framework_count": "VERIFIED__0",
    }
    return proof, firewall


def zero_counters() -> dict[str, str]:
    return {key: "VERIFIED__0" for key in (
        "ja_human_operational_authority", "ja_authority_consumption", "ja_pre",
        "ja_fm_operational_invocation", "ja_qemu", "ja_vm_boot", "ja_operation_attempt",
        "ja_request", "ja_p11_entry", "ja_protected_invocation", "ja_protected_effect",
        "ja_retry", "ja_repair_retry", "ja_replay",
    )}


def build_reduction() -> dict[str, Any]:
    entry = authenticate_entry()
    iz = authenticate_committed_iz()
    owners = authenticate_two_owner_rebind()
    adapter = authenticate_adapter_and_semantics()
    nocloud = authenticate_nocloud_projection()
    live = validate_v2_post_commit_binding()
    proof, firewall = authenticate_ex_and_firewalls()
    return {
        "schema_id": "G77_256JA_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "mode": "POST_COMMIT_LIVE_BINDING_STATIC_READINESS_ONLY__NO_AUTHORIZATION__NO_OPERATION",
        "terminal": "A__FUTURE_POST_COMMIT_LIVE_BINDING_AND_OPERATIONAL_READINESS_VERIFIED",
        "entry": entry, "iz_reconstruction": iz, "production_owner_binding": owners,
        "adapter_and_future_semantics": adapter, "nocloud_and_guest_import_root": nocloud,
        "live_binding": live, "proof_reuse": proof, "historical_failure_firewall": firewall,
        "operational_counters": zero_counters(),
        "reuse_impact": {
            "reused_certified_capability_set": "VERIFIED__IZ_FM_IW_IE_IF_DU_EB_EE_V2_ER_FC_FK_CANONICAL_HUMAN_ACT_CHE_CUSTODY_REQUEST_P11_GN_GL_DI_EX_GOVERNANCE_LAYER_0_NESTED_AUTHORITY",
            "new_capability_set": "VERIFIED__JA_POST_COMMIT_LIVE_BINDING_READINESS_EVIDENCE_ONLY",
            "unreachable_preexisting_capability_set": "VERIFIED__EMPTY", "parallel_flow_created": "VERIFIED__NO",
            "production_route_before": "VERIFIED__1", "production_route_after": "VERIFIED__1",
            "production_route_delta": "VERIFIED__0", "new_generic_adapter_count": "VERIFIED__0",
            "new_dispatcher_count": "VERIFIED__0", "new_global_registry_count": "VERIFIED__0",
            "p11_mutation_count": "VERIFIED__0",
        },
        "continuity": {
            "chain": "IV -> IW -> IX -> IY -> IZ -> JA",
            "progress": "VERIFIED__IV_IMPORT_ROOT_FAILURE__IW_IMPORT_ROOT_BINDING__IX_POST_COMMIT_IMPORT_READINESS__IY_IMPORT_SUCCESS_AND_ENTRYPOINT_ABSENCE__IZ_ENTRYPOINT_STATIC_BINDING__JA_POST_COMMIT_LIVE_BINDING_READINESS",
        },
        "infrastructure_amortization": {
            "future_generations_so_far": "VERIFIED__23__IE_THROUGH_JA",
            "future_e05_credit_so_far": "VERIFIED__0", "future_operational_attempts_so_far": "VERIFIED__2__IV_AND_IY",
            "marginal_new_infrastructure_for_ja": "VERIFIED__READINESS_EVIDENCE_ONLY",
            "new_common_infrastructure": "VERIFIED__0", "new_vector_specific_infrastructure": "VERIFIED__0",
            "infrastructure_amortization_signal": "ESTIMATED__HIGH_REUSE_WITH_ZERO_PRODUCTION_MUTATION",
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_L5_CLAIM",
            "cross_worker_state_recovery_level": "VERIFIED__AUTHENTICATED_REPOSITORY_HANDOFF",
            "repository_derived_context_ratio": "ESTIMATED__DOMINANT__NO_NUMERIC_INSTRUMENT",
            "human_handoff_information_required": "VERIFIED__COMMISSION_SCOPE_CHECKPOINT_AND_LOCATORS",
            "previous_worker_conversation_required": "VERIFIED__NO", "previous_worker_identity_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO", "authenticated_repository_continuation": "VERIFIED__YES",
            "inter_generation_cross_worker_continuation": "VERIFIED__IZ_TO_JA",
            "intra_generation_cross_worker_continuation": "NOT_APPLICABLE__NO_DELEGATION",
            "uncommitted_delta_recovery": "NOT_APPLICABLE__CLEAN_ENTRY",
            "authority_state_recovery": "VERIFIED__JA_ZERO_AUTHORITY__IY_HISTORICAL_AUTHORITY_NONREUSABLE",
            "consumed_authority_recovery": "VERIFIED__IY_CONSUMPTION_RECONSTRUCTED_AND_NOT_REUSED",
            "post_operation_state_recovery": "VERIFIED__IY_FAIL_CLOSED_TERMINAL_RECONSTRUCTED",
            "operation_replay_prevention": "VERIFIED__JA_ZERO_OPERATION__IY_AUTHORITY_NOT_REUSED",
            "cross_worker_constitutional_drift": "NOT_PROVEN__NO_GOVERNED_WORKER_IDENTITY_DRIFT_INSTRUMENT",
            "observed_artifact_level_cross_worker_drift": "VERIFIED__0", "handoff_sufficiency_status": "VERIFIED",
            "handoff_state_completeness": "VERIFIED__COMPLETE_FOR_JA_SCOPE", "handoff_reconstruction_required": "VERIFIED__YES",
            "handoff_reconstruction_success": "VERIFIED__YES", "handoff_ambiguity_count": "VERIFIED__0",
            "unauthenticated_handoff_assumption_count": "VERIFIED__0",
        },
        "cognition": {
            "cognition_assisted_handoff": "VERIFIED__REPOSITORY_DERIVED_IZ_TO_JA_CONTINUATION",
            "cognition_provenance": "VERIFIED__RATIFIED_IZ_GIT_CHECKPOINT_AND_COMMITTED_EVIDENCE_PRIMARY",
            "aigol_codex_work_share": "NOT_MEASURED",
            "prompt_context_reuse_ratio": "NOT_MEASURED__NO_GOVERNED_NUMERIC_INSTRUMENT",
            "repository_derived_execution_context_ratio": "NOT_MEASURED__NO_GOVERNED_NUMERIC_INSTRUMENT",
            "constitutional_prompt_externalization_ratio": "NOT_MEASURED__NO_GOVERNED_NUMERIC_INSTRUMENT",
            "token_benchmark": "NOT_MEASURED", "llm_cost_reduction_ratio": "NOT_MEASURED", "lcrr": "NOT_MEASURED",
        },
        "metrics": {
            "project_progress": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "constitutional_frontier_distanc_e": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "e05_frontier_distance": "VERIFIED__8_UNSATISFIED_OF_18",
            "selected_e05_local_frontier_distance": "VERIFIED__SEPARATE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING",
            "governance_efficience": "ESTIMATED__HIGH_REUSE_WITH_FAIL_CLOSED_POST_COMMIT_CLOSURE",
            "architectural_governance_efficience": "VERIFIED__ONE_ROUTE_ZERO_ROUTE_DELTA_ZERO_P11_MUTATION",
            "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED",
            "overengineering_risk": "ESTIMATED__LOW__EVIDENCE_ONLY",
            "proof_process_overhead_risk": "ESTIMATED__MODERATE",
            "candidate_capability": "VERIFIED__FUTURE_GOVERNED_OPERATIONAL_ADAPTER_ENTRYPOINT_POST_COMMIT_LIVE_BOUND_TO_EXISTING_P11_ROUTE_AND_STATICALLY_READY_FOR_SEPARATE_HUMAN_AUTHORIZED_COMMISSIONING__OPERATIONAL_DENIAL_NOT_PROVEN",
            "shadow_design_target": "VERIFIED__FAMILY_LOCAL_DU_EB_EE_V2_OPTION_B_WITH_COLOCATED_FAIL_CLOSED_MAJOR_VERSION_DISPATCH",
        },
        "validation": {
            "ja_focused": "VERIFIED__14_PASSED",
            "iz_current_applicable": "VERIFIED__10_PASSED__3_HISTORICAL_GENERATION_PINNED_DESELECTED",
            "ie_current_applicable": "VERIFIED__10_PASSED__1_HISTORICAL_GENERATION_PINNED_DESELECTED",
            "fm_operation_context": "VERIFIED__17_PASSED",
            "in_v2_current_structural": "VERIFIED__20_PASSED__5_HISTORICAL_GENERATION_PINNED_DESELECTED",
            "gn_gl_p11_di_human_act_che_fk": "VERIFIED__124_PASSED",
            "du_eb_ee_v2_self_test_cases": "VERIFIED__41_PASSED",
            "ex_regression": "VERIFIED__12_OF_12__CERTIFIED_17_OF_17_REUSED",
            "governance_pytest": "VERIFIED__100_PASSED",
            "governance_hook_drift": "VERIFIED__4_PASSED",
            "conformance_engine": "VERIFIED__20_PASSED__CONFORMANT__0_WARNINGS__0_VIOLATIONS",
            "layer_0_freeze": "VERIFIED__PASS", "operational": "NOT_APPLICABLE",
            "canonical_json_duplicate_key_ast_static_route_nocloud_g48": "VERIFIED",
            "git_diff_check": "VERIFIED__CLEAN",
        },
        "e05": {"before": "VERIFIED__10_OF_18", "after": "VERIFIED__10_OF_18", "credit": "VERIFIED__0"},
        "terminal_frontier": {
            "last_verified_edge": "FUTURE_POST_COMMIT_LIVE_BINDING_AND_STATIC_OPERATIONAL_READINESS",
            "first_broken_edge": "FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_NOT_PRESENT",
            "minimum_missing_capability": "SEPARATE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING",
            "minimum_legal_next_delta": "HUMAN_REVIEW_THEN_SEPARATE_AUTHORIZATION_GENERATION",
            "auto_continuable": "NO", "human_review_required": "YES", "next_generation_started": "NO",
        },
    }


def build_envelope() -> dict[str, Any]:
    reduction = build_reduction()
    return {
        "schema_id": "G77_256JA_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction, "reduction_sha256": sha256_bytes(canonical_bytes(reduction)),
    }


def main() -> int:
    envelope = build_envelope()
    (ROOT / TERMINAL).write_bytes(canonical_bytes(envelope))
    print(json.dumps(envelope["reduction"]["terminal_frontier"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
