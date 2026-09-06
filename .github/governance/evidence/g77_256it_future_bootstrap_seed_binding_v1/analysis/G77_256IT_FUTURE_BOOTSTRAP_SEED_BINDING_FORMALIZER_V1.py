#!/usr/bin/env python3
"""Repository-only formalizer for the G77-256IT FUTURE bootstrap binding."""

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
IS_HEAD = "032bd82276a2a4fb2543ca90d3533b5e1b050bdf"
IS_TREE = "77e1560c20ad677e0a9c468be29682a4628c24ab"
IS_SUBJECT = "G77-256IS record FUTURE preauthorization bootstrap blocker"
IF_HEAD = "699fcdce794ff49b6c8735602936355724ed1c90"
IF_TREE = "7c773d4b2acdf013f1b8238eabfc8eced4dd6866"
IR_HEAD = "8f68fb2e94db3c8bac56fc96315b312e6217dea6"
IR_TREE = "b43a481b505c83b12ae006eccf1f35aa0e191eff"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
LINEAGE = {
    "IS": IS_HEAD,
    "IR": IR_HEAD,
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
CLOUD_INIT = IT_ROOT / "static/G77_256IT_CLOUD_INIT_USER_DATA_V1.yaml"
SEED = IT_ROOT / "static/SAPIANTA_FUTURE_NOCLOUD_SEED_V1.img"
FM_ROOT = Path(".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1")
FM_LAUNCHER = FM_ROOT / "launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
FM_CONTEXT = FM_ROOT / "launcher/sapianta_fresh_operation_context_v1.py"
FM_META = FM_ROOT / "raw/G77_256FM_CLOUD_INIT_META_DATA_V1.yaml"
FM_NETWORK = FM_ROOT / "raw/G77_256FM_CLOUD_INIT_NETWORK_CONFIG_V1.yaml"
IF_ROOT = Path(".github/governance/evidence/g77_256if_future_post_commit_readiness_v1")
IF_CLOUD_INIT = IF_ROOT / "static/G77_256IF_CLOUD_INIT_USER_DATA_TEMPLATE_V1.yaml"
IF_SEED = IF_ROOT / "static/SAPIANTA_FUTURE_NOCLOUD_SEED_TEMPLATE_V1.img"
IF_ADAPTER = IF_ROOT / "adapter/G77_256IF_FUTURE_VECTOR_ADAPTER_V1.py"
IS_ROOT = Path(".github/governance/evidence/g77_256is_future_operational_v1")
IS_TERMINAL = IS_ROOT / "G77_256IS_SPCE_TERMINAL_PREAUTHORIZATION_BLOCKER_V1.json"
IS_CANDIDATE = IS_ROOT / "live_binding/candidate/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json"
EX_CERTIFICATE = Path(
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
    "G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"
)
BOOTSTRAP_GUEST_PATH = "/mnt/dp-harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
PROHIBITION = "G77_256IF_FUTURE_BOOTSTRAP_PROHIBITED_UNTIL_POST_COMMIT_REBIND"
OLD_CLOUD_SHA256 = "6fbe557e8e2209aba7cd5c7cc81081fffbcd66ba57127547bcdb7ee30c6b0d40"
NEW_CLOUD_SHA256 = "85fff3ed0a764c2e0a26acc5d08778b21bec9fe925c2eb69e931b410f906eaff"
OLD_SEED_SHA256 = "0a268fc0e97f1f0dfb9f886172382f48bfb7c1817f7a4c2ec2b8fe26395f4c9e"
NEW_SEED_SHA256 = "58b880d7011a9a781968139f212eef8f6b913f0efadf86df1ee98ac05b0f3369"
OLD_LAUNCHER_SHA256 = "f8310a6c8aba85f170ef9f30c3459bf615ec73014ec00f91aace5e8e5b44b769"
NEW_LAUNCHER_SHA256 = "669985cc31ea7bde26a3187e0f212d6ab2dd6643f73fc34589a7fb7e633ad6c0"
ADAPTER_SHA256 = "77c5f30eff125194037630f36d7940b1798637fb15c3e73cbfe14eebd5e8a854"
RAW_SCHEMA_SHA256 = "95ca9b753b2e4256b6530652d5a6e2a8220fed68c52f774928e1e39721f4ca67"
DN_HARNESS_SHA256 = "4e5d01699796d4bb451818408f7cd6a080b6d55fde518df8a9dd2acd3f1a73bb"
FUTURE_PAYLOAD = "sha256:9568e0c248ad488cabcf6bde6b490c544077862d10e3fda13bcdc8ed9953f547"
FUTURE_SOURCE_ACT = "sha256:7167b0725d2c84bafde1d0060f512b0fa358d777ec1beff8b7c68d22ee6502e8"
FUTURE_CHE = "CHE-CORRELATION-15b2680b5577da169cecf9efb3231e2e6f6467e6f409fa2594b04128f998e454"


class ITBindingError(ValueError):
    """One deterministic fail-closed IT validation error."""


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *arguments], cwd=cwd, text=True).strip()


def load_module(path: Path, identity: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(identity, path)
    if specification is None or specification.loader is None:
        raise ITBindingError(f"MODULE_LOAD_FAILED__{identity}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ITBindingError(f"DUPLICATE_JSON_KEY__{key}")
        value[key] = item
    return value


def load_canonical_bytes(raw: bytes) -> dict[str, Any]:
    value = json.loads(raw, object_pairs_hook=unique_object)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise ITBindingError("CANONICAL_JSON_INVALID")
    return value


def authenticate_entry() -> dict[str, Any]:
    observed = {
        "repository": str(ROOT),
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "subject": git("show", "-s", "--format=%s", "HEAD"),
        "origin": git("remote", "get-url", "origin"),
        "remote_tracking_head": git("rev-parse", f"origin/{BRANCH}"),
        "index": git("diff", "--cached", "--name-only"),
    }
    expected = {
        "repository": str(ROOT), "branch": BRANCH, "head": IS_HEAD,
        "tree": IS_TREE, "subject": IS_SUBJECT, "origin": ORIGIN,
        "remote_tracking_head": IS_HEAD, "index": "",
    }
    if observed != expected:
        raise ITBindingError("EXACT_COMMITTED_IS_CHECKPOINT_MISMATCH")
    for label, revision in LINEAGE.items():
        if subprocess.run(
            ["git", "merge-base", "--is-ancestor", revision, IS_HEAD],
            cwd=ROOT, check=False, stdout=subprocess.DEVNULL,
        ).returncode:
            raise ITBindingError(f"LINEAGE_MISSING__{label}")
    nested = ROOT / "sapianta_system"
    nested_state = {
        "origin": git("remote", "get-url", "origin", cwd=nested),
        "head": git("rev-parse", "HEAD", cwd=nested),
        "tree": git("rev-parse", "HEAD^{tree}", cwd=nested),
        "branch": git("branch", "--show-current", cwd=nested),
        "status": git("status", "--porcelain", cwd=nested),
        "tag": git("describe", "--tags", "--exact-match", "HEAD", cwd=nested),
    }
    if nested_state != {
        "origin": NESTED_ORIGIN, "head": NESTED_HEAD, "tree": NESTED_TREE,
        "branch": "", "status": "", "tag": NESTED_TAG,
    }:
        raise ITBindingError("NESTED_AUTHORITY_NOT_CLEAN_DETACHED_PINNED")
    return observed | {"lineage": {key: "VERIFIED" for key in LINEAGE}, "nested": nested_state}


def reconstruct_is() -> dict[str, Any]:
    raw = subprocess.check_output(["git", "show", f"{IS_HEAD}:{IS_TERMINAL}"], cwd=ROOT)
    envelope = load_canonical_bytes(raw)
    reduction = envelope["reduction"]
    if envelope["reduction_sha256"] != sha256_bytes(canonical_bytes(reduction)):
        raise ITBindingError("IS_TERMINAL_INNER_SEAL_INVALID")
    blocker = reduction["blocker"]
    expected = {
        "terminal": "E__CONSTITUTIONAL_REGRESSION",
        "last_verified_edge": "IF_CANDIDATE_AND_IR_BASELINE_V2_ROLE_SEPARATION__FM_OPERATION_STATE_MATERIALIZED_WITHOUT_QEMU",
        "first_broken_edge": "FM_AUTHORITY_FREE_STATIC_READINESS__FUTURE_CLOUD_INIT_ADAPTER_BOOTSTRAP_CONSUMER",
        "blocking_owner": IF_CLOUD_INIT.as_posix(),
        "exact_failure": "RuntimeError: cloud-init adapter bootstrap consumer mismatch",
    }
    observed = {"terminal": reduction["terminal"]} | {
        key: blocker[key] for key in expected if key != "terminal"
    }
    if observed != expected:
        raise ITBindingError("IS_TERMINAL_RECONSTRUCTION_MISMATCH")
    old_cloud = subprocess.check_output(["git", "show", f"{IS_HEAD}:{IF_CLOUD_INIT}"], cwd=ROOT)
    if sha256_bytes(old_cloud) != OLD_CLOUD_SHA256:
        raise ITBindingError("IF_HISTORICAL_CLOUD_IDENTITY_MISMATCH")
    old_text = old_cloud.decode()
    if old_text.count(BOOTSTRAP_GUEST_PATH) != 0 or old_text.count(PROHIBITION) != 1:
        raise ITBindingError("IS_HISTORICAL_BLOCKER_BYTES_MISMATCH")
    if sha256_path(ROOT / IF_SEED) != OLD_SEED_SHA256:
        raise ITBindingError("IF_HISTORICAL_SEED_IDENTITY_MISMATCH")
    return expected | {
        "minimum_missing_capability": blocker["minimum_missing_capability"],
        "minimum_legal_next_delta": blocker["minimum_legal_next_delta"],
        "old_cloud_sha256": OLD_CLOUD_SHA256,
        "old_seed_sha256": OLD_SEED_SHA256,
    }


def seed_projection() -> dict[str, Any]:
    sources = {"/user-data": CLOUD_INIT, "/meta-data": FM_META, "/network-config": FM_NETWORK}
    for member, source in sources.items():
        projected = subprocess.check_output(
            ["isoinfo", "-i", str(ROOT / SEED), "-R", "-x", member],
            stderr=subprocess.DEVNULL,
        )
        if projected != (ROOT / source).read_bytes():
            raise ITBindingError(f"NOCLOUD_PROJECTION_MISMATCH__{member}")
    return {
        "builder_mechanism": "GENISOIMAGE_CIDATA_JOLIET_ROCK__STATIC_CONTENT_HASH_IDENTITY",
        "source_projection": "VERIFIED",
        "bootstrap_bytes_identity": "VERIFIED",
        "nocloud_seed_bootstrap_binding": "VERIFIED",
        "wall_clock_freshness_dependency": "VERIFIED__0",
    }


def audit_binding() -> dict[str, Any]:
    launcher = load_module(ROOT / FM_LAUNCHER, "g77_256it_fm_launcher")
    if sha256_path(ROOT / CLOUD_INIT) != NEW_CLOUD_SHA256:
        raise ITBindingError("IT_CLOUD_INIT_IDENTITY_MISMATCH")
    if sha256_path(ROOT / SEED) != NEW_SEED_SHA256:
        raise ITBindingError("IT_SEED_IDENTITY_MISMATCH")
    if sha256_path(ROOT / IF_ADAPTER) != ADAPTER_SHA256:
        raise ITBindingError("FUTURE_ADAPTER_IDENTITY_MISMATCH")
    if sha256_path(ROOT / FM_LAUNCHER) != NEW_LAUNCHER_SHA256:
        raise ITBindingError("FM_LAUNCHER_IDENTITY_MISMATCH")
    selected = launcher.current_bootstrap_asset_bindings("FUTURE")
    expected = {
        "cloud_init_path": CLOUD_INIT.as_posix(),
        "cloud_init_sha256": NEW_CLOUD_SHA256,
        "seed_path": str(ROOT / SEED),
        "seed_sha256": NEW_SEED_SHA256,
    }
    if selected != expected:
        raise ITBindingError("FM_FUTURE_SUCCESSOR_SELECTION_MISMATCH")
    cloud_text = (ROOT / CLOUD_INIT).read_text(encoding="utf-8")
    if cloud_text.count(BOOTSTRAP_GUEST_PATH) != 1 or PROHIBITION in cloud_text:
        raise ITBindingError("IT_BOOTSTRAP_CONSUMER_BINDING_MISMATCH")
    arguments = launcher.bootstrap_guest_command_arguments(cloud_text, BOOTSTRAP_GUEST_PATH)
    if arguments != (ADAPTER_SHA256, RAW_SCHEMA_SHA256, IF_HEAD, IF_TREE, DN_HARNESS_SHA256):
        raise ITBindingError("IT_BOOTSTRAP_ARGUMENT_BINDING_MISMATCH")
    if (launcher.CHECKOUT_HEAD, launcher.CHECKOUT_TREE) != (IF_HEAD, IF_TREE):
        raise ITBindingError("IF_RUNTIME_TARGET_ROLE_DRIFT")
    tree = ast.parse((ROOT / FM_LAUNCHER).read_text(encoding="utf-8"))
    if sum(isinstance(node, ast.FunctionDef) and node.name == "main" for node in tree.body) != 1:
        raise ITBindingError("PRODUCTION_ROUTE_COUNT_INVALID")
    seed = seed_projection()
    with tempfile.TemporaryDirectory(prefix="g77_256it_static_") as temporary:
        temporary_root = Path(temporary)
        context = launcher.build_operation_context(
            repository_root=ROOT,
            repository_head=IS_HEAD,
            repository_tree=IS_TREE,
            generation_identity="G77_256IT_ONE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING_V1",
            operation_identity="G77_256IT_STATIC_BINDING_FIXTURE_001",
            identity_namespace_prefix="G77_256IT",
            operation_evidence_root=temporary_root / "operation_state",
            transient_root=temporary_root / "transient",
            candidate_source_path=IS_CANDIDATE,
        )
        binding = context["guest_adapter_binding"]
        projection_root = Path(binding["projection_root"])
        projection_root.mkdir(parents=True)
        adapter_bytes = (ROOT / IF_ADAPTER).read_bytes()
        Path(binding["projected_path"]).write_bytes(adapter_bytes)
        Path(binding["bootstrap_projected_path"]).write_bytes(adapter_bytes)
        proof = launcher.prove_guest_adapter_binding(ROOT, context)
    if proof["result"] != "PREAUTHORITY_GUEST_ADAPTER_BINDING_PASS":
        raise ITBindingError("FM_STATIC_BOOTSTRAP_PROOF_FAILED")
    return {
        "authoritative_historical_owner": IF_CLOUD_INIT.as_posix(),
        "authoritative_successor_owner": CLOUD_INIT.as_posix(),
        "authoritative_seed_owner": SEED.as_posix(),
        "authoritative_selector_owner": FM_LAUNCHER.as_posix(),
        "existing_fm_bootstrap_consumer": BOOTSTRAP_GUEST_PATH,
        "existing_fm_bootstrap_consumer_bound": "VERIFIED",
        "is_bootstrap_consumer_blocker": "VERIFIED__REMOVED_BY_IT_REPOSITORY_DELTA",
        "bootstrap_prohibition_remains_in_current_projection": "VERIFIED__NO",
        "stale_bootstrap_projection": "VERIFIED__NO",
        "static_fm_binding_proof": proof["result"],
        "seed": seed,
    }


def ex_reuse() -> dict[str, Any]:
    envelope = json.loads(
        (ROOT / EX_CERTIFICATE).read_bytes(), object_pairs_hook=unique_object
    )
    certificate = envelope["certificate"]
    preimage = dict(envelope)
    preimage["certificate_sha256"] = ""
    if (
        envelope["certificate_sha256"]
        != sha256_bytes(canonical_bytes(preimage).removesuffix(b"\n"))
        or certificate["component_counts"]["CERTIFIED"] != 17
    ):
        raise ITBindingError("EX_CERTIFICATE_RECONSTRUCTION_FAILED")
    return {"ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0"}


def build_reduction() -> dict[str, Any]:
    entry = authenticate_entry()
    blocker = reconstruct_is()
    binding = audit_binding()
    return {
        "schema_id": "G77_256IT_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "terminal": "A__FUTURE_BOOTSTRAP_AND_NOCLOUD_SEED_BINDING_REPOSITORY_IMPLEMENTED",
        "entry": entry,
        "is_reconstruction": blocker,
        "owner_graph": binding,
        "dependent_identity_recomputation": [
            {"owner": CLOUD_INIT.as_posix(), "old_identity": OLD_CLOUD_SHA256, "new_identity": NEW_CLOUD_SHA256, "dependency_reason": "FUTURE_BOOTSTRAP_CONSUMER_BYTES"},
            {"owner": SEED.as_posix(), "old_identity": OLD_SEED_SHA256, "new_identity": NEW_SEED_SHA256, "dependency_reason": "NOCLOUD_USER_DATA_PROJECTION"},
            {"owner": FM_LAUNCHER.as_posix(), "old_identity": OLD_LAUNCHER_SHA256, "new_identity": NEW_LAUNCHER_SHA256, "dependency_reason": "EXISTING_FUTURE_ASSET_SELECTOR_BINDING"},
        ],
        "independent_identities": {
            "future_payload": FUTURE_PAYLOAD, "source_act": FUTURE_SOURCE_ACT,
            "che_correlation": FUTURE_CHE, "if_runtime_candidate_sha256": "ad5d204ec6ace09f18b83fd5f868e73dac5e36dad81149f9f335c87f68cf42f7",
        },
        "future_semantics": {"evaluation": 500, "valid_from": 600, "valid_until": 1000, "relation": "500 < 600 < 1000", "future_semantic_mutation_count": "VERIFIED__0", "wall_clock_dependency_count": "VERIFIED__0"},
        "v2_role_separation": {"runtime_target": {"head": IF_HEAD, "tree": IF_TREE}, "certification_baseline": {"head": IR_HEAD, "tree": IR_TREE}, "runtime_certification_role_collapse": "VERIFIED__NO"},
        "route_firewall": {"parallel_flow_created": "VERIFIED__NO", "production_route_before": "VERIFIED__1", "production_route_after": "VERIFIED__1", "production_route_delta": "VERIFIED__0", "new_launcher_count": "VERIFIED__0", "new_generic_adapter_count": "VERIFIED__0", "new_dispatcher_count": "VERIFIED__0"},
        "authority_firewall": {"p11_mutation_count": "VERIFIED__0", "human_operational_authority": "VERIFIED__0", "authority_consumption": "VERIFIED__0", "pre_operational_invocation": "VERIFIED__0", "fm_operational_invocation": "VERIFIED__0", "qemu": "VERIFIED__0", "vm_creation": "VERIFIED__0", "vm_boot": "VERIFIED__0", "operation_attempt": "VERIFIED__0", "request": "VERIFIED__0", "p11_entry": "VERIFIED__0", "protected_invocation": "VERIFIED__0", "protected_effect": "VERIFIED__0", "retry": "VERIFIED__0", "repair_retry": "VERIFIED__0", "replay": "VERIFIED__0", "e05_credit": "VERIFIED__0", "e05": "VERIFIED__10_OF_18"},
        "historical_failure_firewall": {"reintroduced_historical_failure_count": "VERIFIED__0"},
        "ex": ex_reuse(),
        "terminal_frontier": {"last_verified_edge": "FUTURE_BOOTSTRAP_AND_NOCLOUD_SEED_BINDING_REPOSITORY_STATIC_CLOSURE", "first_broken_edge": "POST_COMMIT_FUTURE_BOOTSTRAP_AND_FULL_FM_STATIC_READINESS_AUTHENTICATION_NOT_YET_PROVEN", "minimum_missing_capability": "POST_COMMIT_AUTHENTICATION_OF_IT_BOOTSTRAP_SEED_AND_FULL_FM_STATIC_READINESS", "minimum_legal_next_delta": "HUMAN_REVIEW_COMMIT_AND_PUSH_IT_THEN_SEPARATE_POST_COMMIT_READINESS_CERTIFICATION", "auto_continuable": "NO", "human_review_required": "YES", "next_generation_started": "NO"},
    }


def build_envelope() -> dict[str, Any]:
    reduction = build_reduction()
    return {
        "schema_id": "G77_256IT_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": sha256_bytes(canonical_bytes(reduction)),
    }


def main() -> None:
    print(canonical_bytes(build_envelope()).decode(), end="")


if __name__ == "__main__":
    main()
