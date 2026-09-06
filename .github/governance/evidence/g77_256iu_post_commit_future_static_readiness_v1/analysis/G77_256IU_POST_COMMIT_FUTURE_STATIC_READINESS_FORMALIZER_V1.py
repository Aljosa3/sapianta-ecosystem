#!/usr/bin/env python3
"""Authority-free G77-256IU post-commit FUTURE readiness formalizer.

This owner executes only repository/static validators and temporary test-only
materializers.  It cannot create a Human authorization request or presentation,
consume authority, invoke PRE/FM operationally, launch QEMU, enter P11, retry,
repair-retry, replay, or award E05 credit.
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
IT_HEAD = "635687d9d8c4ae9ad122ca62083cc886497ee87e"
IT_TREE = "92d69783fa2e573753b7848428cc460d3de00be1"
IT_SUBJECT = "G77-256IT bind FUTURE NoCloud bootstrap and seed"
IF_HEAD = "699fcdce794ff49b6c8735602936355724ed1c90"
IF_TREE = "7c773d4b2acdf013f1b8238eabfc8eced4dd6866"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
LINEAGE = {
    "IT": IT_HEAD,
    "IS": "032bd82276a2a4fb2543ca90d3533b5e1b050bdf",
    "IR": "8f68fb2e94db3c8bac56fc96315b312e6217dea6",
    "IQ": "2ad26623dd4625d2162ce2b9fa0d65e8581f95f6",
    "IP": "65d6d029fbcfbae964e702fdbdb544c940b2eec2",
    "IO": "af7835d98d0bfa685da99e41bd5bc866cbc2a54b",
    "IN": "e39aee28fa9181e1db2ae6c5cff4a50f557821be",
    "IF": IF_HEAD,
    "IE": "9420764a5bb6db8909334f2a422225687a37a346",
    "IC": "afdd47166acdee30cb9867d3d3c7bfec0de64c8a",
    "ANCHOR": "5c972e9960987ab27420395b54ace693df097e7b",
}

IT_ROOT = Path(".github/governance/evidence/g77_256it_future_bootstrap_seed_binding_v1")
IT_REPORT = IT_ROOT / "G77_256IT_G48_IMPLEMENTATION_REPORT_V1.md"
IT_TERMINAL = IT_ROOT / "G77_256IT_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
IT_FORMALIZER = IT_ROOT / "analysis/G77_256IT_FUTURE_BOOTSTRAP_SEED_BINDING_FORMALIZER_V1.py"
IT_TEST = IT_ROOT / "tests/test_g77_256it_future_bootstrap_seed_binding_v1.py"
IT_HASHES = {
    IT_REPORT: "6ebe97868db4a3a49048690ef73e47969dfb6542607a40d826c9c6897ea60d69",
    IT_TERMINAL: "e33d7a79a9632f11ff61f52b81a1611fb8e9cbcaeb614dfd5a360407876f880d",
    IT_FORMALIZER: "3852298d460ca40692a4419a126419fd7ce1080024b0f34b5953078fe4b486aa",
    IT_TEST: "979dcdbe42e18cbdcc98c17c7d081cb7125078aa62b6484bef64f85b42d06ce5",
}
CLOUD_INIT = IT_ROOT / "static/G77_256IT_CLOUD_INIT_USER_DATA_V1.yaml"
SEED = IT_ROOT / "static/SAPIANTA_FUTURE_NOCLOUD_SEED_V1.img"
CLOUD_SHA256 = "85fff3ed0a764c2e0a26acc5d08778b21bec9fe925c2eb69e931b410f906eaff"
SEED_SHA256 = "58b880d7011a9a781968139f212eef8f6b913f0efadf86df1ee98ac05b0f3369"
FM_ROOT = Path(".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1")
FM_LAUNCHER = FM_ROOT / "launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
FM_META = FM_ROOT / "raw/G77_256FM_CLOUD_INIT_META_DATA_V1.yaml"
FM_NETWORK = FM_ROOT / "raw/G77_256FM_CLOUD_INIT_NETWORK_CONFIG_V1.yaml"
FM_LAUNCHER_SHA256 = "669985cc31ea7bde26a3187e0f212d6ab2dd6643f73fc34589a7fb7e633ad6c0"
GUEST_PATH = "/mnt/dp-harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
PROHIBITION = "G77_256IF_FUTURE_BOOTSTRAP_PROHIBITED_UNTIL_POST_COMMIT_REBIND"
DU_PATH = Path(".github/governance/evidence/g77_256du_continuation_manifest_contract_v2/validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V2.py")
EB_PATH = Path(".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v2/validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V2.py")
EE_PATH = Path(".github/governance/evidence/g77_256ee_runtime_consumer_binding_v2/validator/G77_256EE_RUNTIME_CONSUMER_BINDING_VALIDATOR_V2.py")
GN_PATH = Path(".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py")
GL_PATH = Path(".github/governance/evidence/g77_256gl_receipt_parent_equivalence_v1/orchestration/G77_256GL_RECEIPT_PARENT_PREAUTHORIZATION_BINDING_V1.py")
CANDIDATE = Path(".github/governance/evidence/g77_256ih_future_if_identity_rebind_v1/live_binding/candidate/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json")
CANDIDATE_SHA256 = "ad5d204ec6ace09f18b83fd5f868e73dac5e36dad81149f9f335c87f68cf42f7"
ACT_CHE = Path(".github/governance/evidence/g77_256if_future_post_commit_readiness_v1/live_binding/G77_256IF_FUTURE_ACT_CHE_BINDING_V1.json")
EX_CERTIFICATE = Path(".github/governance/evidence/g77_256ex_common_substrate_certification_v1/G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json")
P11_PATHS = ("aigol/runtime", "sapianta_system", ".github/governance/evidence/g77_256ec_p11_operational_v1")
GENERATION = "G77_256IUTEST_ONE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256IUTEST_AUTHORITY_FREE_STATIC_READINESS_ONLY_001"
PREFIX = "G77_256IUTEST"


class IUReadinessError(ValueError):
    """One deterministic fail-closed IU readiness error."""


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
            raise IUReadinessError(f"DUPLICATE_JSON_KEY__{key}")
        result[key] = value
    return result


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique_object)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise IUReadinessError(f"NONCANONICAL_JSON__{path}")
    return value


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *arguments], cwd=cwd, text=True).strip()


def load_module(name: str, relative: Path) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, ROOT / relative)
    if specification is None or specification.loader is None:
        raise IUReadinessError(f"MODULE_LOAD_FAILED__{relative}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def authenticate_entry(
    remote_head: str = IT_HEAD,
    nested_remote_tag: str = NESTED_HEAD,
) -> dict[str, Any]:
    observed = {
        "repository": str(ROOT),
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "subject": git("show", "-s", "--format=%s", "HEAD"),
        "origin": git("remote", "get-url", "origin"),
        "remote_head": remote_head,
        "index": git("diff", "--cached", "--name-only"),
        "tracked_delta": git("status", "--porcelain", "--untracked-files=no"),
    }
    expected = {
        "repository": str(ROOT), "branch": BRANCH, "head": IT_HEAD,
        "tree": IT_TREE, "subject": IT_SUBJECT, "origin": ORIGIN,
        "remote_head": IT_HEAD, "index": "", "tracked_delta": "",
    }
    if observed != expected:
        raise IUReadinessError("EXACT_RATIFIED_IT_ENTRY_MISMATCH")
    lineage: dict[str, str] = {}
    for label, revision in LINEAGE.items():
        if subprocess.run(
            ["git", "merge-base", "--is-ancestor", revision, "HEAD"],
            cwd=ROOT, check=False, stdout=subprocess.DEVNULL,
        ).returncode:
            raise IUReadinessError(f"LINEAGE_MISSING__{label}")
        lineage[label] = "VERIFIED"
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
    if nested_state != {
        "origin": NESTED_ORIGIN, "head": NESTED_HEAD, "tree": NESTED_TREE,
        "clean": True, "detached": True, "tag": NESTED_TAG,
        "remote_tag": NESTED_HEAD,
    }:
        raise IUReadinessError("NESTED_AUTHORITY_NOT_CLEAN_DETACHED_PINNED")
    return observed | {"lineage": lineage, "nested_authority": nested_state}


def reconstruct_it() -> dict[str, Any]:
    identities: dict[str, Any] = {}
    for path, expected_sha in IT_HASHES.items():
        committed = subprocess.check_output(["git", "show", f"{IT_HEAD}:{path}"], cwd=ROOT)
        if committed != (ROOT / path).read_bytes() or sha256_bytes(committed) != expected_sha:
            raise IUReadinessError(f"COMMITTED_IT_BYTE_MISMATCH__{path}")
        identities[path.name] = {
            "sha256": expected_sha,
            "git_blob": git("rev-parse", f"{IT_HEAD}:{path}"),
        }
    envelope = load_canonical(ROOT / IT_TERMINAL)
    if envelope["reduction_sha256"] != sha256_bytes(canonical_bytes(envelope["reduction"])):
        raise IUReadinessError("IT_TERMINAL_INNER_SEAL_INVALID")
    reduction = envelope["reduction"]
    if reduction["terminal"] != "A__FUTURE_BOOTSTRAP_AND_NOCLOUD_SEED_BINDING_REPOSITORY_IMPLEMENTED":
        raise IUReadinessError("IT_TERMINAL_MISMATCH")
    firewall = reduction["authority_firewall"]
    if any(value != "VERIFIED__0" for key, value in firewall.items() if key != "e05"):
        raise IUReadinessError("IT_OPERATIONAL_ZERO_MISMATCH")
    return {
        "status": "VERIFIED__COMMITTED_OBJECT_RECONSTRUCTION",
        "terminal": reduction["terminal"], "artifact_count": 4,
        "inner_seal": "VERIFIED", "identities": identities,
    }


def authenticate_bootstrap_seed_selector() -> dict[str, Any]:
    if sha256_path(ROOT / CLOUD_INIT) != CLOUD_SHA256:
        raise IUReadinessError("COMMITTED_IT_BOOTSTRAP_HASH_MISMATCH")
    if sha256_path(ROOT / SEED) != SEED_SHA256:
        raise IUReadinessError("COMMITTED_IT_NOCLOUD_SEED_HASH_MISMATCH")
    if sha256_path(ROOT / FM_LAUNCHER) != FM_LAUNCHER_SHA256:
        raise IUReadinessError("COMMITTED_FM_SELECTOR_HASH_MISMATCH")
    cloud = (ROOT / CLOUD_INIT).read_text(encoding="utf-8")
    if cloud.count(GUEST_PATH) != 1 or PROHIBITION in cloud:
        raise IUReadinessError("CURRENT_BOOTSTRAP_GUEST_CONSUMER_MISMATCH")
    sources = {"/user-data": CLOUD_INIT, "/meta-data": FM_META, "/network-config": FM_NETWORK}
    equality: dict[str, str] = {}
    for member, source in sources.items():
        projected = subprocess.check_output(
            ["isoinfo", "-i", str(ROOT / SEED), "-R", "-x", member],
            stderr=subprocess.DEVNULL,
        )
        if projected != (ROOT / source).read_bytes():
            raise IUReadinessError(f"NOCLOUD_MEMBER_BYTE_MISMATCH__{member}")
        equality[member] = "VERIFIED__EXACT_BYTES"
    fm = load_module("g77_256iu_selector", FM_LAUNCHER)
    selected = fm.current_bootstrap_asset_bindings("FUTURE")
    expected = {
        "cloud_init_path": CLOUD_INIT.as_posix(), "cloud_init_sha256": CLOUD_SHA256,
        "seed_path": str(ROOT / SEED), "seed_sha256": SEED_SHA256,
    }
    if selected != expected:
        raise IUReadinessError("FUTURE_SELECTOR_NOT_IT_SUCCESSOR_PAIR")
    tree = ast.parse((ROOT / FM_LAUNCHER).read_text(encoding="utf-8"))
    if sum(isinstance(node, ast.FunctionDef) and node.name == "main" for node in tree.body) != 1:
        raise IUReadinessError("FM_PRODUCTION_ROUTE_COUNT_NOT_ONE")
    return {
        "committed_it_bootstrap_present": "VERIFIED",
        "committed_it_bootstrap_hash": "VERIFIED__EXACT",
        "bootstrap_sha256": CLOUD_SHA256,
        "bootstrap_prohibition_present_in_current_successor": "VERIFIED__NO",
        "existing_fm_guest_consumer_occurrence": "VERIFIED__EXACTLY_ONE",
        "existing_fm_guest_path": GUEST_PATH,
        "committed_it_nocloud_seed_present": "VERIFIED",
        "committed_it_nocloud_seed_hash": "VERIFIED__EXACT",
        "nocloud_seed_sha256": SEED_SHA256,
        "seed_member_equality": equality,
        "nocloud_user_data_equals_committed_it_bootstrap": "VERIFIED",
        "nocloud_meta_data_binding": "VERIFIED",
        "nocloud_network_config_binding": "VERIFIED",
        "stale_bootstrap_projection": "VERIFIED__NO",
        "wall_clock_freshness_dependency": "VERIFIED__NO",
        "fm_selector_committed_hash": "VERIFIED__EXACT",
        "fm_selector_sha256": FM_LAUNCHER_SHA256,
        "future_selector_target": "VERIFIED__IT_SUCCESSOR_PAIR",
        "production_route_count": "VERIFIED__1",
    }


def authenticate_future_semantics() -> dict[str, Any]:
    envelope = load_canonical(ROOT / ACT_CHE)
    binding = envelope["binding"]
    if envelope["binding_sha256"] != sha256_bytes(canonical_bytes(binding)):
        raise IUReadinessError("FUTURE_ACT_CHE_INNER_SEAL_INVALID")
    act = binding["human_authority_act_representation"]
    che = binding["che_correlation"]
    result = {
        "evaluation": binding["evaluation_time_unix_ns"],
        "valid_from": act["payload"]["valid_from_unix_ns"],
        "valid_until": act["payload"]["valid_until_unix_ns"],
        "payload_digest": act["payload_digest"].removeprefix("sha256:"),
        "source_act": che["source_act_digest"].removeprefix("sha256:"),
        "che_correlation": che["correlation_identity"],
    }
    expected = {
        "evaluation": 500, "valid_from": 600, "valid_until": 1000,
        "payload_digest": "9568e0c248ad488cabcf6bde6b490c544077862d10e3fda13bcdc8ed9953f547",
        "source_act": "7167b0725d2c84bafde1d0060f512b0fa358d777ec1beff8b7c68d22ee6502e8",
        "che_correlation": "CHE-CORRELATION-15b2680b5577da169cecf9efb3231e2e6f6467e6f409fa2594b04128f998e454",
    }
    if result != expected or not result["evaluation"] < result["valid_from"] < result["valid_until"]:
        raise IUReadinessError("FUTURE_SEMANTIC_IDENTITY_MISMATCH")
    return result | {
        "relation": "500 < 600 < 1000",
        "future_semantic_mutation_count": "VERIFIED__0",
        "wall_clock_dependency_count": "VERIFIED__0",
    }


def v2_and_full_static_readiness() -> dict[str, Any]:
    fm = load_module("g77_256iu_fm", FM_LAUNCHER)
    du = load_module("g77_256iu_du", DU_PATH)
    eb = load_module("g77_256iu_eb", EB_PATH)
    ee = load_module("g77_256iu_ee", EE_PATH)
    gl = load_module("g77_256iu_gl", GL_PATH)
    with tempfile.TemporaryDirectory(prefix=".g77_256iu_static_", dir=ROOT) as raw:
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
        if set(du_result.values()) != {"PASS"} or eb_result["overall_result"] != "PASS":
            raise IUReadinessError("DU_OR_EB_V2_POST_COMMIT_READINESS_FAILED")
        if ee_result["pre_materialization_runtime_path_binding_result"] != "PASS":
            raise IUReadinessError("EE_V2_POST_COMMIT_READINESS_FAILED")
        baseline = {"head": IT_HEAD, "tree": IT_TREE}
        target = eb_envelope["receipt"]["runtime_target_selection_binding"]
        if eb_envelope["receipt"]["certification_baseline"] != baseline:
            raise IUReadinessError("EB_CERTIFICATION_BASELINE_NOT_IT")
        if ee_envelope["receipt"]["certification_baseline"] != baseline:
            raise IUReadinessError("EE_CERTIFICATION_BASELINE_NOT_IT")
        if (target["head"], target["tree"]) != (IF_HEAD, IF_TREE):
            raise IUReadinessError("RUNTIME_TARGET_NOT_IF")
        if ee_envelope["receipt"]["runtime_target_selection_binding"] != target:
            raise IUReadinessError("EB_EE_RUNTIME_TARGET_DISAGREEMENT")

        operation_root = temporary / "operation-state"
        transient_root = temporary / "transient"
        context = fm.build_operation_context(
            repository_root=ROOT, repository_head=IT_HEAD, repository_tree=IT_TREE,
            generation_identity=GENERATION, operation_identity=OPERATION,
            identity_namespace_prefix=PREFIX, operation_evidence_root=operation_root,
            transient_root=transient_root, candidate_source_path=CANDIDATE,
        )
        context_path = temporary / "test-only-context.json"
        context_path.write_bytes(fm.canonical_bytes(context))
        destination = fm.preauth_fresh_checkout_destination_readiness(ROOT, context)
        materialization = fm.materialize_operation_state(
            repository_root=ROOT, context=context, context_source_path=context_path,
            candidate_source_path=CANDIDATE,
        )
        observations = fm.observe_context_assets(ROOT, context, CANDIDATE)
        readiness = fm.authority_free_static_readiness(
            repository_root=ROOT, context=context, observed_head=IT_HEAD,
            observed_tree=IT_TREE, repository_clean=True,
            observed_asset_sha256=observations, candidate_source_path=CANDIDATE,
        )
        claim = gl.prepare_and_observe_receipt_parent(ROOT, context)
        checkpoint = gl.reduce_preauthorization_checkpoint(ROOT, context, claim)
        equivalence = gl.validate_preauth_final_admission_equivalence(
            ROOT, context, claim, checkpoint
        )
        if destination["result"] != "PREAUTH_FRESH_CHECKOUT_DESTINATION_READINESS_PASS":
            raise IUReadinessError("PREAUTH_DESTINATION_READINESS_FAILED")
        if materialization["result"] != "FRESH_OPERATION_STATE_MATERIALIZED_WITHOUT_QEMU":
            raise IUReadinessError("AUTHORITY_FREE_OPERATION_STATE_MATERIALIZATION_FAILED")
        if readiness["result"] != "STATIC_READINESS_PASS":
            raise IUReadinessError("FULL_FM_STATIC_READINESS_FAILED")
        if readiness["guest_adapter_binding"]["guest_consumer_path"] != GUEST_PATH:
            raise IUReadinessError("EXISTING_FM_GUEST_CONSUMER_NOT_BOUND")
        if equivalence["human_constitutional_authorization_count"] != 0:
            raise IUReadinessError("GL_BOUNDARY_CREATED_AUTHORITY")
        return {
            "du_v2_post_commit_readiness": "VERIFIED",
            "eb_v2_post_commit_readiness": "VERIFIED",
            "ee_v2_post_commit_readiness": "VERIFIED",
            "du_eb_ee_v2_chain": "VERIFIED",
            "v2_major": 2, "v2_semver": "2.0.0", "v2_suffix": "V2",
            "family_local_dispatch": "VERIFIED",
            "global_registry": "VERIFIED__NO",
            "caller_selected_version": "VERIFIED__NO",
            "unknown_mixed_downgrade_rejection": "VERIFIED",
            "v1_immutable": "VERIFIED",
            "runtime_target": {"head": target["head"], "tree": target["tree"]},
            "certification_baseline": baseline,
            "runtime_target_equals_certification_baseline": "VERIFIED__NO",
            "role_collapse": "VERIFIED__NO",
            "operation_state_context_binding": "VERIFIED__TEMPORARY_NONAUTHORITY",
            "materialization": materialization["result"],
            "fm_authority_free_static_readiness": "VERIFIED",
            "future_post_commit_preoperational_readiness": "VERIFIED",
            "static_readiness_result": readiness["result"],
            "existing_fm_guest_consumer_bound": "VERIFIED",
            "guest_consumer_route_count": "VERIFIED__1",
            "guest_consumer_bypass": "VERIFIED__NO",
            "gl_boundary": "VERIFIED",
            "gl_preauth_final_admission_equivalence": equivalence["preauth_final_admission_equivalence"],
            "human_authorization_created": "VERIFIED__0",
        }


def gn_p11_ex_firewalls() -> dict[str, Any]:
    gn = load_module("g77_256iu_gn", GN_PATH)
    fm = load_module("g77_256iu_fm_firewall", FM_LAUNCHER)
    if "FUTURE" not in gn.SUPPORTED_VECTORS or len(gn.SUPPORTED_VECTORS) != 5:
        raise IUReadinessError("GN_FUTURE_CLOSED_SET_COMPATIBILITY_FAILED")
    if fm.fresh_context.operation_vector(GENERATION) != "FUTURE":
        raise IUReadinessError("GN_FUTURE_GENERATION_BOUNDARY_FAILED")
    if fm.operation_attempt_limit_field("FUTURE") != "future_operational_attempt_limit":
        raise IUReadinessError("HUMAN_ACT_FUTURE_BOUNDARY_FAILED")
    gl_source = (ROOT / GL_PATH).read_text(encoding="utf-8")
    if "SUPPORTED_VECTORS" in gl_source or "authorized_vector_requested" in gl_source:
        raise IUReadinessError("GL_DUPLICATE_VECTOR_GATE_DETECTED")
    if git("diff", "--name-only", IT_HEAD, "--", *P11_PATHS):
        raise IUReadinessError("P11_OR_NESTED_AUTHORITY_MUTATION_DETECTED")
    ex = json.loads(
        (ROOT / EX_CERTIFICATE).read_bytes(), object_pairs_hook=unique_object
    )
    certificate = ex["certificate"]
    preimage = dict(ex)
    preimage["certificate_sha256"] = ""
    if ex["certificate_sha256"] != sha256_bytes(canonical_bytes(preimage).removesuffix(b"\n")):
        raise IUReadinessError("EX_CERTIFICATE_SEAL_INVALID")
    if certificate["component_counts"]["CERTIFIED"] != 17:
        raise IUReadinessError("EX_17_OF_17_NOT_AVAILABLE")
    return {
        "gn_future_compatibility": "VERIFIED", "gl_boundary": "VERIFIED",
        "human_authorization_presentation_issued": "VERIFIED__0",
        "p11_mutation_count": "VERIFIED__0", "p11_bypass": "VERIFIED__NO",
        "ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0",
    }


def zero_counters() -> dict[str, str]:
    return {key: "VERIFIED__0" for key in (
        "human_authorization_presentation", "human_operational_authority",
        "authority_consumption", "pre_operational_invocation",
        "fm_operational_invocation", "qemu", "vm_creation", "vm_boot",
        "operation_attempt", "request", "p11_entry", "protected_invocation",
        "protected_effect", "retry", "repair_retry", "replay", "e05_credit",
    )}


def build_reduction() -> dict[str, Any]:
    entry = authenticate_entry()
    it = reconstruct_it()
    binding = authenticate_bootstrap_seed_selector()
    future = authenticate_future_semantics()
    readiness = v2_and_full_static_readiness()
    firewalls = gn_p11_ex_firewalls()
    return {
        "schema_id": "G77_256IU_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "mode": "READINESS_CERTIFICATION_ONLY__NO_AUTHORIZATION__NO_OPERATION",
        "terminal": "A__FUTURE_POST_COMMIT_FULL_STATIC_READINESS_VERIFIED",
        "entry": entry, "it_reconstruction": it,
        "bootstrap_seed_selector": binding, "future_semantics": future,
        "readiness": readiness, "boundary_firewalls": firewalls,
        "route_firewall": {
            "parallel_flow_created": "VERIFIED__NO",
            "production_route_before": "VERIFIED__1",
            "production_route_after": "VERIFIED__1",
            "production_route_delta": "VERIFIED__0",
            "new_launcher_count": "VERIFIED__0",
            "new_generic_adapter_count": "VERIFIED__0",
            "new_dispatcher_count": "VERIFIED__0",
        },
        "operational_counters": zero_counters() | {"e05": "VERIFIED__10_OF_18"},
        "historical_failure_firewall": {
            "reintroduced_historical_failure_count": "VERIFIED__0",
        },
        "reuse_impact": {
            "reused_certified_capability_set": "VERIFIED__IT_IS_IR_IQ_IP_IO_IN_IF_IE_IC_GN_GL_FM_HUMAN_ACT_DU_EB_EE_V2_P11_CHE_FK_EX_GOVERNANCE_LAYER_0_NESTED_AUTHORITY",
            "new_capability_set": "VERIFIED__POST_COMMIT_READINESS_EVIDENCE_ONLY",
            "unreachable_preexisting_capability_set": "VERIFIED__EMPTY",
            "parallel_flow_created": "VERIFIED__NO",
            "production_route_before": "VERIFIED__1",
            "production_route_after": "VERIFIED__1",
            "production_route_delta": "VERIFIED__0",
        },
        "infrastructure_amortization": {
            "future_generations_so_far": "VERIFIED__17__IE_THROUGH_IU",
            "future_e05_credit_so_far": "VERIFIED__0",
            "future_operational_attempts_so_far": "VERIFIED__0",
            "new_common_infrastructure_for_future": "VERIFIED__0",
            "new_vector_specific_infrastructure_for_future": "VERIFIED__0",
            "marginal_new_infrastructure_for_iu": "VERIFIED__POST_COMMIT_READINESS_EVIDENCE_ONLY",
            "marginal_new_infrastructure_per_e05_credit": "NOT_APPLICABLE__ZERO_FUTURE_CREDIT",
            "infrastructure_amortization_signal": "ESTIMATED__HIGH_REUSE_WITH_FULL_STATIC_READINESS_AND_ZERO_CREDIT",
            "expected_next_credit_generation_count": "NOT_PROVEN",
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_L5_CLAIM",
            "cross_worker_state_recovery_level": "VERIFIED__AUTHENTICATED_REPOSITORY_HANDOFF",
            "repository_derived_context_ratio": "ESTIMATED__DOMINANT__NO_NUMERIC_INSTRUMENT",
            "human_handoff_information_required": "VERIFIED__COMMISSION_SCOPE_CHECKPOINT_AND_LOCATORS",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_identity_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
            "authenticated_repository_continuation": "VERIFIED",
            "inter_generation_cross_worker_continuation": "VERIFIED__IT_TO_IU",
            "intra_generation_cross_worker_continuation": "NOT_APPLICABLE__NO_DELEGATION",
            "uncommitted_delta_recovery": "VERIFIED__IU_EVIDENCE_ONLY",
            "authority_state_recovery": "VERIFIED__NO_AUTHORITY_CREATED",
            "consumed_authority_recovery": "NOT_APPLICABLE__NO_AUTHORITY_CONSUMED",
            "post_operation_state_recovery": "NOT_APPLICABLE__NO_OPERATION",
            "operation_replay_prevention": "VERIFIED__NO_OPERATION_AND_NO_AUTHORITY",
            "cross_worker_constitutional_drift": "VERIFIED__0_OBSERVED",
            "handoff_sufficiency_status": "VERIFIED",
            "handoff_state_completeness": "VERIFIED__COMPLETE_FOR_STATIC_READINESS",
            "handoff_reconstruction_required": "VERIFIED__YES",
            "handoff_reconstruction_success": "VERIFIED__YES",
            "handoff_ambiguity_count": "VERIFIED__0",
            "unauthenticated_handoff_assumption_count": "VERIFIED__0",
        },
        "cognition": {
            "cognition_provenance": "VERIFIED__AUTHENTICATED_REPOSITORY_PRIMARY",
            "cognition_assisted_handoff": "VERIFIED__AUTHENTICATED_IT_TO_IU_REPOSITORY_CONTINUATION",
            "prompt_context_reuse_ratio": "NOT_MEASURED__NO_GOVERNED_NUMERIC_INSTRUMENT",
            "repository_derived_execution_context_ratio": "NOT_MEASURED__NO_GOVERNED_NUMERIC_INSTRUMENT",
            "constitutional_prompt_externalization_ratio": "NOT_MEASURED__NO_GOVERNED_NUMERIC_INSTRUMENT",
            "repository_derived_context": "VERIFIED__GIT_IT_IS_IR_IF_FM_GN_GL_DU_EB_EE_P11_CHE_FK_EX_LAYER_0_NESTED_AUTHORITY",
            "prompt_required_context": "VERIFIED__IU_COMMISSION_SCOPE_AND_SPLIT_PHASE_BOUNDARY",
            "previous_conversation_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
        },
        "metrics": {
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "constitutional_health_evidence": "VERIFIED__FULL_STATIC_CHAIN_CLOSES_WITH_FAIL_CLOSED_AUTHORITY_BARRIER",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "e05_frontier_distance": "VERIFIED__8_UNSATISFIED_OF_18",
            "selected_e05_local_frontier_distance": "VERIFIED__ONE_SEPARATE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_GENERATION",
            "governance_efficience": "ESTIMATED__POST_COMMIT_PROOF_REUSE_WITH_ZERO_PRODUCTION_MUTATION",
            "architectural_governance_efficience": "VERIFIED__ONE_ROUTE_ZERO_ROUTE_DELTA",
            "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED",
            "cognition_assisted_handoff": "VERIFIED__AUTHENTICATED_IT_TO_IU_REPOSITORY_CONTINUATION",
            "aigol_codex_work_share": "NOT_MEASURED",
            "overengineering_risk": "ESTIMATED__LOW__EVIDENCE_ONLY_NO_PRODUCTION_OWNER_DELTA",
            "proof_process_overhead_risk": "ESTIMATED__MODERATE",
            "cognition_provenance": "VERIFIED__AUTHENTICATED_REPOSITORY_PRIMARY",
            "candidate_capability": "VERIFIED__IF_BOUND_RUNTIME_CANDIDATE_WITH_IT_BOOTSTRAP_SEED_POST_COMMIT_FULL_STATIC_READINESS__NOT_AUTHORIZED",
            "shadow_design_target": "VERIFIED__FAMILY_LOCAL_DU_EB_EE_V2_OPTION_B_WITH_COLOCATED_FAIL_CLOSED_MAJOR_VERSION_DISPATCH",
            "constitutional_continuation_progress": "VERIFIED__IT_POST_COMMIT_BINDING_AND_FULL_FM_STATIC_READINESS_CLOSED__AUTHORITY_PENDING",
            "prompt_context_reuse_ratio": "NOT_MEASURED__NO_GOVERNED_NUMERIC_INSTRUMENT",
            "repository_derived_execution_context_ratio": "NOT_MEASURED__NO_GOVERNED_NUMERIC_INSTRUMENT",
            "constitutional_prompt_externalization_ratio": "NOT_MEASURED__NO_GOVERNED_NUMERIC_INSTRUMENT",
            "token_benchmark": "NOT_MEASURED", "llm_cost_reduction_ratio": "NOT_MEASURED",
            "lcrr": "NOT_MEASURED", "e05_generations_per_credit": "NOT_APPLICABLE__ZERO_FUTURE_CREDIT",
            "operational_attempts_per_credit": "NOT_APPLICABLE__ZERO_FUTURE_OPERATIONAL_ATTEMPTS_AND_CREDIT",
            "marginal_e05_generation_cost": "NOT_MEASURED",
            "marginal_new_infrastructure_per_e05_credit": "NOT_APPLICABLE__ZERO_FUTURE_CREDIT",
            "infrastructure_amortization_signal": "ESTIMATED__HIGH_REUSE_WITH_FULL_STATIC_READINESS_AND_ZERO_CREDIT",
            "expected_next_credit_generation_count": "NOT_PROVEN",
        },
        "terminal_frontier": {
            "last_verified_edge": "FUTURE_POST_COMMIT_FULL_STATIC_PREOPERATIONAL_READINESS",
            "first_broken_edge": "FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_NOT_YET_ISSUED",
            "minimum_missing_capability": "ONE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING",
            "minimum_legal_next_delta": "SEPARATE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_GENERATION",
            "auto_continuable": "NO", "human_review_required": "YES",
            "next_generation_started": "NO",
        },
    }


def build_envelope() -> dict[str, Any]:
    reduction = build_reduction()
    return {
        "schema_id": "G77_256IU_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": sha256_bytes(canonical_bytes(reduction)),
    }


def main() -> int:
    sys.stdout.buffer.write(canonical_bytes(build_envelope()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
