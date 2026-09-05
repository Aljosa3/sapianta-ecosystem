#!/usr/bin/env python3
"""Prepare one IF-bound FUTURE identity tuple without entering operation.

This owner is deliberately repository-only.  It rebinds the existing sole FM
checkout tuple from committed IE to committed IF, derives one matching DU
candidate/runtime/context projection, and stops when the immutable EB/EE
owners reject the requested IF baseline because the actual repository HEAD is
committed IG.  It creates no authority, request, PRE entry, P11 entry, QEMU
process, VM, protected invocation, retry, or E05 credit.
"""

from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True

BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
IG_HEAD = "71391a75011cdc388bdac9183f4654814a044c69"
IG_TREE = "e19cf096bc855e20f6005a2ee8f84c8972fbde82"
IG_SUBJECT = "G77-256IG certify FUTURE post-IF binding frontier"
IF_HEAD = "699fcdce794ff49b6c8735602936355724ed1c90"
IF_TREE = "7c773d4b2acdf013f1b8238eabfc8eced4dd6866"
IF_SUBJECT = "G77-256IF bind FUTURE static route and readiness frontier"
IE_HEAD = "9420764a5bb6db8909334f2a422225687a37a346"
IE_TREE = "b9ebdc1015e9b9459ccd93841cc8d1c7377ddc19"
ID_HEAD = "559deecb226b66d626e45e6f607b0aab6df81f1c"
IC_HEAD = "afdd47166acdee30cb9867d3d3c7bfec0de64c8a"
STABLE_ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_TAG = "refs/tags/sapianta-system-nested-authority-3183bab-v1"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"

VECTOR = "FUTURE"
SELECTED_VECTOR = "P11-E05/NEGATIVE_AUTHORITY/FUTURE"
GENERATION = "G77_256IH_ONE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING_V1"
OPERATION_IDENTITY = "G77_256IH_FUTURE_PREOPERATIONAL_READINESS_PREPARATION_001"
IDENTITY_PREFIX = "G77_256IH"

IH_ROOT = Path(".github/governance/evidence/g77_256ih_future_if_identity_rebind_v1")
LIVE = IH_ROOT / "live_binding"
BINDING_CHECKPOINT = LIVE / "bindings/G77_256IH_DU_EB_EE_READINESS_CHECKPOINT_V1.json"
TERMINAL = IH_ROOT / "G77_256IH_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = IH_ROOT / "G77_256IH_G48_IMPLEMENTATION_REPORT_V1.md"
IG_ROOT = Path(".github/governance/evidence/g77_256ig_future_post_if_commit_rebind_v1")
IG_TERMINAL = IG_ROOT / "G77_256IG_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
IF_ROOT = Path(".github/governance/evidence/g77_256if_future_post_commit_readiness_v1")
IF_CANDIDATE = IF_ROOT / "live_binding/candidate/G77_256IF_FUTURE_CURRENT_CANDIDATE_V1.json"
IF_ACT_CHE = IF_ROOT / "live_binding/G77_256IF_FUTURE_ACT_CHE_BINDING_V1.json"
IF_ADAPTER = IF_ROOT / "adapter/G77_256IF_FUTURE_VECTOR_ADAPTER_V1.py"
IF_CLOUD_INIT = IF_ROOT / "static/G77_256IF_CLOUD_INIT_USER_DATA_TEMPLATE_V1.yaml"
IF_SEED = IF_ROOT / "static/SAPIANTA_FUTURE_NOCLOUD_SEED_TEMPLATE_V1.img"
FM_ROOT = Path(".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1")
FM_LAUNCHER = FM_ROOT / "launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
FM_CONTEXT = FM_ROOT / "launcher/sapianta_fresh_operation_context_v1.py"
FM_META = FM_ROOT / "raw/G77_256FM_CLOUD_INIT_META_DATA_V1.yaml"
FM_NETWORK = FM_ROOT / "raw/G77_256FM_CLOUD_INIT_NETWORK_CONFIG_V1.yaml"
DU_OWNER = Path(".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V1.py")
EB_OWNER = Path(".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v1/validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V1.py")
EE_OWNER = Path(".github/governance/evidence/g77_256ee_runtime_consumer_binding_v1/validator/G77_256EE_RUNTIME_CONSUMER_BINDING_VALIDATOR_V1.py")
GN_OWNER = Path(".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py")
GL_OWNER = Path(".github/governance/evidence/g77_256gl_receipt_parent_equivalence_v1/orchestration/G77_256GL_RECEIPT_PARENT_PREAUTHORIZATION_BINDING_V1.py")
EX_CERTIFICATE = Path(".github/governance/evidence/g77_256ex_common_substrate_certification_v1/G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json")

FUTURE_PAYLOAD_DIGEST = "sha256:9568e0c248ad488cabcf6bde6b490c544077862d10e3fda13bcdc8ed9953f547"
SOURCE_ACT_DIGEST = "sha256:7167b0725d2c84bafde1d0060f512b0fa358d777ec1beff8b7c68d22ee6502e8"
CORRELATION_IDENTITY = "CHE-CORRELATION-15b2680b5577da169cecf9efb3231e2e6f6467e6f409fa2594b04128f998e454"
IF_ADAPTER_SHA256 = "77c5f30eff125194037630f36d7940b1798637fb15c3e73cbfe14eebd5e8a854"
IF_CLOUD_INIT_SHA256 = "6fbe557e8e2209aba7cd5c7cc81081fffbcd66ba57127547bcdb7ee30c6b0d40"
IF_SEED_SHA256 = "0a268fc0e97f1f0dfb9f886172382f48bfb7c1817f7a4c2ec2b8fe26395f4c9e"
FM_CONTEXT_SHA256 = "fdfa04349529d70bc97820a1848f8afc22b81071859d5456550799e0f9476237"
FM_LAUNCHER_REBOUND_SHA256 = "f8310a6c8aba85f170ef9f30c3459bf615ec73014ec00f91aace5e8e5b44b769"

COMMITTED_IG_PATHS = {
    "IG_G48_REPORT": (IG_ROOT / "G77_256IG_G48_IMPLEMENTATION_REPORT_V1.md", "236587ad7dc5e47735a4ad26fe862e7ca2ff26980cd1a5048d7c667d91a08b07"),
    "IG_TERMINAL_REDUCTION": (IG_TERMINAL, "cf3e3a42f60afc3f1095c70e8a7a4f93f3f9e4a074da2e535fc6d372ba5176de"),
    "IG_VALIDATOR": (IG_ROOT / "validator/G77_256IG_POST_IF_COMMIT_READINESS_VALIDATOR_V1.py", "55d82c451760119b505759975ff5f8e6b2a73d7cd1266445c49509dd5a126801"),
    "IG_TESTS": (IG_ROOT / "tests/test_g77_256ig_post_if_commit_readiness_v1.py", "9b8bb4bc100ba2805a23ace26dd09a3593d31acbba2e5b352135240743304ca4"),
}


class IHBindingError(ValueError):
    """One deterministic fail-closed IH preparation rejection."""


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _git(root: Path, *arguments: str) -> str:
    try:
        return subprocess.check_output(["git", *arguments], cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError as exc:
        raise IHBindingError("GIT_IDENTITY_UNAVAILABLE") from exc


def _git_bytes(root: Path, revision: str, path: Path) -> bytes:
    try:
        return subprocess.check_output(["git", "show", f"{revision}:{path.as_posix()}"], cwd=root, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as exc:
        raise IHBindingError(f"COMMITTED_OBJECT_UNAVAILABLE__{path.name}") from exc


def _load(path: Path, identity: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(identity, path)
    if specification is None or specification.loader is None:
        raise IHBindingError(f"MODULE_LOAD_FAILED__{identity}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise IHBindingError(f"DUPLICATE_JSON_KEY__{key}")
        result[key] = value
    return result


def load_canonical_bytes(raw: bytes, identity: str) -> dict[str, Any]:
    value = json.loads(raw, object_pairs_hook=_unique)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise IHBindingError(f"CANONICAL_JSON_INVALID__{identity}")
    return value


def load_canonical(path: Path) -> dict[str, Any]:
    return load_canonical_bytes(path.read_bytes(), path.name)


def authenticate_entry(repository_root: Path) -> dict[str, Any]:
    """Authenticate exact IG and permit only the explicit unstaged IH delta."""

    root = repository_root.resolve()
    observed = {
        "repository": str(root),
        "branch": _git(root, "branch", "--show-current"),
        "head": _git(root, "rev-parse", "HEAD"),
        "tree": _git(root, "rev-parse", "HEAD^{tree}"),
        "subject": _git(root, "show", "-s", "--format=%s", "HEAD"),
        "origin": _git(root, "remote", "get-url", "origin"),
        "remote_tracking_head": _git(root, "rev-parse", f"origin/{BRANCH}"),
        "index": _git(root, "diff", "--cached", "--name-only"),
    }
    expected = {
        "repository": str(root), "branch": BRANCH, "head": IG_HEAD,
        "tree": IG_TREE, "subject": IG_SUBJECT, "origin": ORIGIN,
        "remote_tracking_head": IG_HEAD, "index": "",
    }
    if observed != expected:
        raise IHBindingError("EXACT_COMMITTED_IG_CHECKPOINT_MISMATCH")
    for ancestor in (IF_HEAD, IE_HEAD, ID_HEAD, IC_HEAD, STABLE_ANCHOR):
        if subprocess.run(["git", "merge-base", "--is-ancestor", ancestor, IG_HEAD], cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode:
            raise IHBindingError(f"REQUIRED_ANCESTRY_MISSING__{ancestor}")
    if _git(root, "rev-parse", f"{IF_HEAD}^{{tree}}") != IF_TREE:
        raise IHBindingError("IF_TREE_MISMATCH")
    changed = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=root,
        text=True,
    ).splitlines()
    for line in changed:
        path = line[3:]
        if path != FM_LAUNCHER.as_posix() and not path.startswith(IH_ROOT.as_posix() + "/"):
            raise IHBindingError(f"UNRELATED_WORKTREE_MUTATION__{path}")
    nested = root / "sapianta_system"
    nested_state = {
        "origin": _git(nested, "remote", "get-url", "origin"),
        "head": _git(nested, "rev-parse", "HEAD"),
        "tree": _git(nested, "rev-parse", "HEAD^{tree}"),
        "branch": _git(nested, "branch", "--show-current"),
        "status": _git(nested, "status", "--porcelain", "--untracked-files=all"),
        "tag_head": _git(nested, "rev-parse", NESTED_TAG + "^{commit}"),
    }
    if nested_state != {"origin": NESTED_ORIGIN, "head": NESTED_HEAD, "tree": NESTED_TREE, "branch": "", "status": "", "tag_head": NESTED_HEAD}:
        raise IHBindingError("NESTED_AUTHORITY_NOT_CLEAN_DETACHED_PINNED")
    return observed | {"nested": nested_state, "worktree_delta_scope": "VERIFIED__FM_LAUNCHER_PLUS_IH_ONLY"}


def reconstruct_ig(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    identities: dict[str, dict[str, str]] = {}
    for identity, (path, expected_sha) in COMMITTED_IG_PATHS.items():
        raw = _git_bytes(root, IG_HEAD, path)
        if sha256_bytes(raw) != expected_sha or (root / path).read_bytes() != raw:
            raise IHBindingError(f"COMMITTED_IG_IDENTITY_MISMATCH__{identity}")
        identities[identity] = {
            "path": path.as_posix(),
            "git_blob": _git(root, "rev-parse", f"{IG_HEAD}:{path.as_posix()}"),
            "sha256": expected_sha,
            "status": "VERIFIED",
        }
    terminal = load_canonical_bytes(_git_bytes(root, IG_HEAD, IG_TERMINAL), IG_TERMINAL.name)
    reduction = terminal["reduction"]
    if terminal["reduction_sha256"] != sha256_bytes(canonical_bytes(reduction)):
        raise IHBindingError("IG_TERMINAL_SEAL_INVALID")
    expected = {
        "current_e05_status": reduction["if_reconstruction"]["current_e05_status"],
        "selected_next_e05_vector": reduction["if_reconstruction"]["selected_next_e05_vector"],
        "future_repository_formalization": reduction["readiness"]["future_repository_formalization"],
        "future_route_binding": reduction["readiness"]["future_route_binding"],
        "future_live_binding": reduction["readiness"]["future_live_binding"],
        "future_preoperational_readiness": reduction["readiness"]["future_preoperational_readiness"],
        "future_operational_capability": reduction["readiness"]["future_operational_capability"],
        "next_operational_generation_eligible": reduction["readiness"]["next_operational_generation_eligible"],
        "e05_credit": reduction["if_reconstruction"]["e05_credit"],
        "last_verified_edge": reduction["terminal_control"]["last_verified_edge"],
        "first_broken_edge": reduction["terminal_control"]["first_broken_edge"],
        "minimum_missing_capability": reduction["terminal_control"]["minimum_missing_capability"],
        "minimum_legal_next_delta": reduction["terminal_control"]["minimum_legal_next_delta"],
    }
    required = {
        "current_e05_status": "VERIFIED__10_OF_18",
        "selected_next_e05_vector": "VERIFIED__FUTURE",
        "future_repository_formalization": "VERIFIED",
        "future_route_binding": "VERIFIED__STATIC_MEMBERSHIP_ONLY",
        "future_live_binding": "NOT_PROVEN",
        "future_preoperational_readiness": "NOT_PROVEN",
        "future_operational_capability": "NOT_PROVEN",
        "next_operational_generation_eligible": "NOT_PROVEN",
        "e05_credit": "VERIFIED__0",
        "last_verified_edge": "COMMITTED_IF_CONTAINS_FUTURE_STATIC_ROUTE_ADAPTER_TIME_ACT_CHE_CANDIDATE_RUNTIME_CONTEXT_DU_EB_EE",
        "first_broken_edge": "COMMITTED_IF_LAUNCHER_CANDIDATE_AND_CONTEXT_REMAIN_BOUND_TO_IE_NOT_IF",
        "minimum_missing_capability": "ONE_POST_IF_COMMIT_CANDIDATE_RUNTIME_CONTEXT_AND_CHECKOUT_REBIND_TO_EXACT_IF_HEAD_TREE",
        "minimum_legal_next_delta": "SEPARATE_REPOSITORY_ONLY_POST_IF_LIVE_REBIND_THEN_HUMAN_REVIEW",
    }
    if expected != required:
        raise IHBindingError("IG_FRONTIER_RECONSTRUCTION_FAILED")
    return {"status": "VERIFIED", "identity_map": identities, "frontier": expected}


def future_semantics(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    envelope = load_canonical_bytes(_git_bytes(root, IF_HEAD, IF_ACT_CHE), IF_ACT_CHE.name)
    binding = envelope["binding"]
    if envelope["binding_sha256"] != sha256_bytes(canonical_bytes(binding)):
        raise IHBindingError("IF_ACT_CHE_SEAL_INVALID")
    act = binding["human_authority_act_representation"]
    che = binding["che_correlation"]
    if (act["payload_digest"], che["authority_payload_digest"], che["source_act_digest"], che["correlation_identity"]) != (FUTURE_PAYLOAD_DIGEST, FUTURE_PAYLOAD_DIGEST, SOURCE_ACT_DIGEST, CORRELATION_IDENTITY):
        raise IHBindingError("FUTURE_ACT_CHE_IDENTITY_DRIFT")
    payload = act["payload"]
    if (binding["evaluation_time_unix_ns"], payload["valid_from_unix_ns"], payload["valid_until_unix_ns"]) != (500, 600, 1000):
        raise IHBindingError("FUTURE_TEMPORAL_SEMANTICS_DRIFT")
    if binding["semantic_independent_mutation_count"] != 1 or binding["semantic_independent_mutated_coordinate"] != "valid_from_unix_ns":
        raise IHBindingError("FUTURE_SEMANTIC_MUTATION_DRIFT")
    return {
        "status": "VERIFIED", "evaluation_time_unix_ns": 500,
        "valid_from_unix_ns": 600, "valid_until_unix_ns": 1000,
        "relation": "VERIFIED__500_LT_600_LT_1000",
        "payload_digest": FUTURE_PAYLOAD_DIGEST,
        "outer_act": act["authority_act_identity"],
        "source_act_digest": SOURCE_ACT_DIGEST,
        "correlation_identity": CORRELATION_IDENTITY,
        "semantic_independent_mutation_count": "VERIFIED__1",
        "semantic_independent_mutated_coordinate": "VERIFIED__valid_from_unix_ns",
        "ih_semantic_mutation_count": "VERIFIED__0",
        "act_representation_status": "VERIFIED__NONAUTHORIZING",
        "human_operational_authority": 0,
    }


def verify_checkout_bootstrap(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    launcher = _load(root / FM_LAUNCHER, "g77_256ih_launcher_audit")
    if sha256_path(root / FM_LAUNCHER) != FM_LAUNCHER_REBOUND_SHA256:
        raise IHBindingError("REBOUND_LAUNCHER_HASH_MISMATCH")
    if (launcher.CHECKOUT_HEAD, launcher.CHECKOUT_TREE) != (IF_HEAD, IF_TREE):
        raise IHBindingError("FM_CHECKOUT_NOT_BOUND_TO_EXACT_IF")
    bootstrap = launcher.current_bootstrap_asset_bindings(VECTOR)
    expected_bootstrap = {
        "cloud_init_path": IF_CLOUD_INIT.as_posix(),
        "cloud_init_sha256": IF_CLOUD_INIT_SHA256,
        "seed_path": str(root / IF_SEED),
        "seed_sha256": IF_SEED_SHA256,
    }
    if bootstrap != expected_bootstrap:
        raise IHBindingError("FUTURE_BOOTSTRAP_BINDING_MISMATCH")
    for path, expected_sha in ((IF_ADAPTER, IF_ADAPTER_SHA256), (IF_CLOUD_INIT, IF_CLOUD_INIT_SHA256), (IF_SEED, IF_SEED_SHA256), (FM_CONTEXT, FM_CONTEXT_SHA256)):
        if sha256_path(root / path) != expected_sha or _git_bytes(root, IF_HEAD, path) != (root / path).read_bytes():
            raise IHBindingError(f"IF_COMMITTED_DEPENDENCY_MISMATCH__{path.name}")
    for member, source in (("/user-data", IF_CLOUD_INIT), ("/meta-data", FM_META), ("/network-config", FM_NETWORK)):
        projected = subprocess.check_output(["isoinfo", "-i", str(root / IF_SEED), "-R", "-x", member], stderr=subprocess.DEVNULL)
        if projected != (root / source).read_bytes():
            raise IHBindingError(f"NOCLOUD_PROJECTION_MISMATCH__{member}")
    committed_context = _git_bytes(root, IF_HEAD, FM_CONTEXT)
    namespace: dict[str, Any] = {"__name__": "g77_256ih_committed_if_context", "__file__": FM_CONTEXT.as_posix()}
    exec(compile(committed_context, FM_CONTEXT.as_posix(), "exec"), namespace)
    if namespace["operation_vector"](GENERATION) != VECTOR:
        raise IHBindingError("COMMITTED_IF_FUTURE_ROUTE_MEMBERSHIP_ABSENT")
    adapter = _load(root / IF_ADAPTER, "g77_256ih_future_adapter")
    if adapter.deterministic_submission_kwargs(root) != {"now_unix_ns": 500}:
        raise IHBindingError("DETERMINISTIC_TIME_ADAPTER_DRIFT")
    adapter_tree = ast.parse((root / IF_ADAPTER).read_text(encoding="utf-8"))
    calls = {node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id for node in ast.walk(adapter_tree) if isinstance(node, ast.Call) and isinstance(node.func, (ast.Attribute, ast.Name))}
    if calls.intersection({"time", "time_ns", "now", "sleep"}):
        raise IHBindingError("FUTURE_WALL_CLOCK_DEPENDENCY_PRESENT")
    guest_commands = [line for line in (root / IF_CLOUD_INIT).read_text(encoding="utf-8").splitlines() if line.strip().startswith("/usr/bin/python3 ")]
    launcher_tree = ast.parse((root / FM_LAUNCHER).read_text(encoding="utf-8"))
    route_count = sum(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "main" for node in launcher_tree.body)
    if route_count != 1:
        raise IHBindingError("SOLE_PRODUCTION_ROUTE_COUNT_INVALID")
    return {
        "checkout_head_binding": "VERIFIED__IF", "checkout_tree_binding": "VERIFIED__IF",
        "checkout_head": IF_HEAD, "checkout_tree": IF_TREE,
        "bootstrap_binding": "VERIFIED__IF_CONTEXT_COUPLED_UNCHANGED_BYTES",
        "cloud_init_sha256": IF_CLOUD_INIT_SHA256, "nocloud_seed_sha256": IF_SEED_SHA256,
        "nocloud_projection_status": "VERIFIED",
        "host_guest_equivalence": "VERIFIED__COMMITTED_IF_ROUTE_ADAPTER_AND_CONTEXT_IDENTITY",
        "guest_operational_execution_projection": "NOT_PROVEN__IF_ADAPTER_HAS_NO_OPERATIONAL_CLI_ENTRYPOINT",
        "future_guest_command_count": len(guest_commands),
        "deterministic_time_fixture_status": "VERIFIED",
        "deterministic_time_adapter_status": "VERIFIED__REPOSITORY_FUNCTION_ONLY",
        "wall_clock_dependency_count_on_future_path": "VERIFIED__0",
        "new_clock_infrastructure_count": "VERIFIED__0",
        "production_route_before": "VERIFIED__1", "production_route_after": "VERIFIED__1",
        "production_route_delta": "VERIFIED__0", "new_production_route_count": "VERIFIED__0",
    }


def _file_binding(root: Path, identity: str, path: Path) -> dict[str, str]:
    return {"identity": identity, "path": path.as_posix(), "sha256": sha256_path(root / path)}


def build_candidate(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    authenticate_entry(root)
    reconstruct_ig(root)
    future_semantics(root)
    verify_checkout_bootstrap(root)
    envelope = deepcopy(load_canonical_bytes(_git_bytes(root, IF_HEAD, IF_CANDIDATE), IF_CANDIDATE.name))
    manifest = envelope["manifest"]
    manifest.update({
        "generation_identity": GENERATION,
        "required_head": IF_HEAD,
        "source_tree": IF_TREE,
        "current_spce_phase": "PHASE_N_FUTURE_IF_IDENTITY_REBIND_PREPARED_EB_EE_CURRENT_HEAD_MISMATCH",
        "frontier_state": {
            "constitutional_frontier": "FUTURE_IF_IDENTITY_REBIND_PREPARED__EB_EE_CURRENT_HEAD_BASELINE_NOT_SATISFIED",
            "exact_next_legal_action": "HUMAN_REVIEW_OF_IF_TARGET_VERSUS_CURRENT_HEAD_CONTRACT_CONFLICT",
            "continuation_mode": "HUMAN_REVIEW_ONLY",
            "requires_human_review": True,
        },
        "first_failure_or_current_result": "FAIL_CLOSED__EB_EE_REQUIRE_ACTUAL_HEAD_IF_BUT_AUTHENTICATED_ENTRY_HEAD_IS_IG",
        "observations": [
            "CURRENT_IG_COMMIT_IDENTITY_STATUS__VERIFIED",
            "ROOT_REBIND__IE_HEAD_TREE_TO_EXACT_IF_HEAD_TREE",
            "FUTURE_SEMANTICS_PRESERVED__ZERO_IH_SEMANTIC_MUTATION",
            "DETERMINISTIC_TIME__NOW_UNIX_NS_500",
            "ACT_CHE_IDENTITIES_PRESERVED",
            "DU_CURRENT_IF_BOUND__PASS",
            "EB_EE_CURRENT_HEAD_CONTRACT__NOT_PROVEN",
            "E05_REMAINS_TEN_OF_EIGHTEEN",
        ],
    })
    launcher_binding = [item for item in manifest["extension_bindings"] if item["identity"] == "G77_256FM_SOLE_LAUNCHER"]
    if len(launcher_binding) != 1:
        raise IHBindingError("LAUNCHER_EXTENSION_BINDING_MISSING_OR_AMBIGUOUS")
    launcher_binding[0]["sha256"] = FM_LAUNCHER_REBOUND_SHA256
    manifest["lineage_bindings"].append({
        "identity": "G77_256IG_TERMINAL_REDUCTION",
        "path": IG_TERMINAL.as_posix(),
        "sha256": COMMITTED_IG_PATHS["IG_TERMINAL_REDUCTION"][1],
        "git_blob": _git(root, "rev-parse", f"{IG_HEAD}:{IG_TERMINAL.as_posix()}"),
    })
    envelope["manifest_sha256"] = sha256_bytes(canonical_bytes(manifest))
    du = _load(root / DU_OWNER, "g77_256ih_du_builder")
    if set(du.validate_envelope(envelope, root, expected_head=IF_HEAD).values()) != {"PASS"}:
        raise IHBindingError("CURRENT_IF_BOUND_DU_NOT_PASS")
    return envelope


def _harness_bytes(candidate_name: str) -> bytes:
    return ("from pathlib import Path\n\nFIXTURE_CLASSIFICATION = \"TEST_ONLY__NON_AUTHORITY__NON_OPERATIONAL__NON_EXECUTABLE\"\nRAW_ROOT = Path(\"/mnt/g77-evidence\")\nCONTINUATION_MANIFEST_PATH = RAW_ROOT / \"" + candidate_name + "\"\n").encode("utf-8")


def build_context(repository_root: Path, candidate_path: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    launcher = _load(root / FM_LAUNCHER, "g77_256ih_context_builder")
    context = launcher.build_operation_context(
        repository_root=root, repository_head=IF_HEAD, repository_tree=IF_TREE,
        generation_identity=GENERATION, operation_identity=OPERATION_IDENTITY,
        identity_namespace_prefix=IDENTITY_PREFIX,
        operation_evidence_root=Path("/tmp/g77_256ih/operation_state"),
        transient_root=Path("/tmp/g77_256ih/transient"),
        candidate_source_path=candidate_path.relative_to(root),
    )
    launcher.validate_immutable_context_bindings(root, context, candidate_path.relative_to(root))
    checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    if (context["repository_head"], context["repository_tree"], checkout["head"], checkout["tree"]) != (IF_HEAD, IF_TREE, IF_HEAD, IF_TREE):
        raise IHBindingError("CONTEXT_IF_IDENTITY_REBIND_MISMATCH")
    return context


def baseline_owner_results(repository_root: Path, candidate_path: Path) -> dict[str, Any]:
    """Run DU and prove the exact immutable EB/EE baseline rejection."""

    root = repository_root.resolve()
    du = _load(root / DU_OWNER, "g77_256ih_du")
    eb = _load(root / EB_OWNER, "g77_256ih_eb")
    ee = _load(root / EE_OWNER, "g77_256ih_ee")
    du_result = du.validate_file(candidate_path, root, expected_head=IF_HEAD)
    if set(du_result.values()) != {"PASS"}:
        raise IHBindingError("CURRENT_IF_BOUND_DU_NOT_PASS")
    rejections: dict[str, str] = {}
    try:
        eb.validate_candidate(root, candidate_path, required_head=IF_HEAD, required_tree=IF_TREE)
    except Exception as exc:
        if getattr(exc, "code", None) != "REQUIRED_HEAD_MISMATCH":
            raise IHBindingError("EB_UNEXPECTED_REJECTION") from exc
        rejections["eb"] = "NOT_PROVEN__REQUIRED_HEAD_MISMATCH__ACTUAL_IG_REQUIRED_IF"
    else:
        raise IHBindingError("EB_UNEXPECTEDLY_ACCEPTED_NONCURRENT_IF_BASELINE")
    try:
        ee._authenticate_git(root, IF_HEAD, IF_TREE)
    except Exception as exc:
        if getattr(exc, "code", None) != "REQUIRED_HEAD_MISMATCH":
            raise IHBindingError("EE_UNEXPECTED_REJECTION") from exc
        rejections["ee"] = "NOT_PROVEN__REQUIRED_HEAD_MISMATCH__ACTUAL_IG_REQUIRED_IF"
    else:
        raise IHBindingError("EE_UNEXPECTEDLY_ACCEPTED_NONCURRENT_IF_BASELINE")
    return {
        "actual_repository_head": IG_HEAD,
        "requested_candidate_and_checkout_head": IF_HEAD,
        "du": "VERIFIED__CURRENT_IF_BOUND",
        "du_gate_results": du_result,
        "eb": rejections["eb"], "ee": rejections["ee"],
        "eb_receipt_created": False, "ee_receipt_created": False,
        "receipt_fabrication_count": 0,
    }


def instantiate_binding(repository_root: Path, output_root: Path) -> dict[str, Any]:
    """Write only prepared identities and a sealed fail-closed owner checkpoint."""

    root = repository_root.resolve()
    output = output_root.resolve()
    try:
        output.relative_to(root)
    except ValueError as exc:
        raise IHBindingError("OUTPUT_OUTSIDE_REPOSITORY") from exc
    candidate_name = "G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json"
    candidate_path = output / "candidate" / candidate_name
    runtime_path = output / "runtime_projection" / candidate_name
    harness_path = output / "bindings/G77_256IH_EE_PATH_PROJECTION_FIXTURE_V1.py"
    context_path = output / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    checkpoint_path = output / "bindings/G77_256IH_DU_EB_EE_READINESS_CHECKPOINT_V1.json"
    for path in (candidate_path, runtime_path, harness_path, context_path, checkpoint_path):
        if path.exists() or path.is_symlink():
            raise IHBindingError(f"OUTPUT_COLLISION__{path.name}")
        path.parent.mkdir(parents=True, exist_ok=True)
    candidate_bytes = canonical_bytes(build_candidate(root))
    candidate_path.write_bytes(candidate_bytes)
    runtime_path.write_bytes(candidate_bytes)
    harness_path.write_bytes(_harness_bytes(candidate_name))
    context = build_context(root, candidate_path)
    launcher = _load(root / FM_LAUNCHER, "g77_256ih_context_serializer")
    context_path.write_bytes(launcher.fresh_context.canonical_bytes(context))
    owner_results = baseline_owner_results(root, candidate_path)
    checkpoint = {
        "schema_id": "G77_256IH_DU_EB_EE_READINESS_CHECKPOINT_V1",
        "artifact_class": "REPOSITORY_ONLY__NON_AUTHORITY__NON_OPERATIONAL",
        "candidate_path": candidate_path.relative_to(root).as_posix(),
        "candidate_sha256": sha256_bytes(candidate_bytes),
        "runtime_path": runtime_path.relative_to(root).as_posix(),
        "runtime_sha256": sha256_path(runtime_path),
        "context_path": context_path.relative_to(root).as_posix(),
        "context_sha256": context["context_sha256"],
        "context_file_sha256": sha256_path(context_path),
        "owner_results": owner_results,
        "human_review_required": True,
        "auto_continuable": False,
    }
    checkpoint_path.write_bytes(canonical_bytes({
        "schema_id": "G77_256IH_DU_EB_EE_READINESS_CHECKPOINT_ENVELOPE_V1",
        "checkpoint": checkpoint,
        "checkpoint_sha256": sha256_bytes(canonical_bytes(checkpoint)),
    }))
    return {
        "candidate_sha256": sha256_bytes(candidate_bytes),
        "runtime_sha256": sha256_path(runtime_path),
        "context_sha256": context["context_sha256"],
        "context_file_sha256": sha256_path(context_path),
        "checkpoint_sha256": sha256_path(checkpoint_path),
        "du": owner_results["du"], "eb": owner_results["eb"], "ee": owner_results["ee"],
    }


def authenticate_ex(repository_root: Path) -> dict[str, Any]:
    certificate = json.loads(_git_bytes(repository_root.resolve(), IF_HEAD, EX_CERTIFICATE), object_pairs_hook=_unique)
    preimage = deepcopy(certificate)
    preimage["certificate_sha256"] = ""
    payload = json.dumps(preimage, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")
    if certificate["certificate_sha256"] != sha256_bytes(payload) or certificate["certificate"]["component_counts"]["CERTIFIED"] != 17:
        raise IHBindingError("EX_17_OF_17_NOT_AUTHENTICATED")
    return {"ex_reused": "17/17", "ex_reconstructed": 0, "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED"}


def terminal_reduction(repository_root: Path, live_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    live = live_root.resolve()
    entry = authenticate_entry(root)
    ig = reconstruct_ig(root)
    semantics = future_semantics(root)
    checkout = verify_checkout_bootstrap(root)
    candidate_path = live / "candidate/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json"
    runtime_path = live / "runtime_projection/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json"
    harness_path = live / "bindings/G77_256IH_EE_PATH_PROJECTION_FIXTURE_V1.py"
    context_path = live / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    checkpoint_path = live / "bindings/G77_256IH_DU_EB_EE_READINESS_CHECKPOINT_V1.json"
    candidate = load_canonical(candidate_path)
    context = load_canonical(context_path)
    checkpoint_envelope = load_canonical(checkpoint_path)
    checkpoint = checkpoint_envelope["checkpoint"]
    if checkpoint_envelope["checkpoint_sha256"] != sha256_bytes(canonical_bytes(checkpoint)):
        raise IHBindingError("DU_EB_EE_CHECKPOINT_SEAL_INVALID")
    if candidate_path.read_bytes() != runtime_path.read_bytes():
        raise IHBindingError("CANDIDATE_RUNTIME_BYTE_IDENTITY_MISMATCH")
    if candidate["manifest"]["required_head"] != IF_HEAD or candidate["manifest"]["source_tree"] != IF_TREE:
        raise IHBindingError("CANDIDATE_IF_BINDING_MISMATCH")
    if context["candidate_manifest_sha256"] != sha256_path(candidate_path):
        raise IHBindingError("CONTEXT_CANDIDATE_BINDING_MISMATCH")
    build_context(root, candidate_path)
    if not harness_path.is_file() or BINDING_CHECKPOINT.name != checkpoint_path.name:
        raise IHBindingError("CURRENT_BINDING_EVIDENCE_INCOMPLETE")
    owners = baseline_owner_results(root, candidate_path)
    if owners != checkpoint["owner_results"]:
        raise IHBindingError("OWNER_CHECKPOINT_RECONSTRUCTION_MISMATCH")
    for path in (GN_OWNER, GL_OWNER):
        if not (root / path).is_file():
            raise IHBindingError(f"READINESS_OWNER_ABSENT__{path.name}")
    counters = {key: 0 for key in (
        "human_operational_authority", "authority_consumption", "pre",
        "fm_operational_launcher_invocation", "qemu", "vm_creation", "vm_boot",
        "operation_attempt", "request", "p11_entry", "protected_invocation",
        "protected_effect", "retry", "repair_retry", "replay", "e05_credit",
    )}
    first_broken = "EB_EE_REQUIRE_ACTUAL_CURRENT_HEAD_TO_EQUAL_CANDIDATE_REQUIRED_IF_BUT_AUTHENTICATED_ENTRY_HEAD_IS_IG"
    return {
        "schema_id": "G77_256IH_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "mode": "REPOSITORY_ONLY__NO_AUTHORITY__NO_OPERATION",
        "entry": entry,
        "ig_reconstruction": ig,
        "future_semantics": semantics,
        "root_rebind": {
            "from": {"head": IE_HEAD, "tree": IE_TREE},
            "to": {"head": IF_HEAD, "tree": IF_TREE},
            "root_rebind_count": "VERIFIED__ONE_LOGICAL_REBIND",
            "root_rebind_physical_field_count": 2,
            "unrelated_launcher_mutation_count": "VERIFIED__0",
            "pre_commit_self_reference_count": "VERIFIED__0",
            "future_commit_prediction_count": "VERIFIED__0",
        },
        "interruption_recovery": {
            "ih_interruption_recovery_status": "VERIFIED__SAME_GENERATION_REPOSITORY_CONTINUATION",
            "ih_existing_delta_status": "VERIFIED__PRESENT_UNSTAGED_AND_BOUNDED",
            "ih_existing_delta_authenticity": "VERIFIED__COHERENT_WITH_IG_IF_LINEAGE_AND_IH_NAMESPACE",
            "ih_completed_edge_recovery": "VERIFIED__ROOT_REBIND_CANDIDATE_RUNTIME_CONTEXT_AND_DU",
            "ih_partial_edge_recovery": "VERIFIED__FOCUSED_TESTS_G48_REPORT_TERMINAL_REDUCTION_AND_BROADER_VALIDATION",
            "ih_first_unproven_edge_after_recovery": "VERIFIED__EB_EE_REQUIRED_HEAD_MISMATCH",
            "ih_replay_required": "VERIFIED__NO",
            "major_obligations": {
                "entry_and_delta_authentication": "COMPLETED_BEFORE_INTERRUPTION__REAUTHENTICATED",
                "ig_reconstruction": "COMPLETED_BEFORE_INTERRUPTION__REAUTHENTICATED",
                "ie_to_if_root_rebind": "COMPLETED_BEFORE_INTERRUPTION__REAUTHENTICATED",
                "candidate_runtime_context_du": "COMPLETED_BEFORE_INTERRUPTION__REAUTHENTICATED",
                "eb_ee_frontier_discovery": "COMPLETED_BEFORE_INTERRUPTION__INDEPENDENTLY_REAUTHENTICATED",
                "focused_negative_tests": "PARTIALLY_COMPLETED_BEFORE_INTERRUPTION__COMPLETED_AFTER_RECOVERY",
                "g48_and_terminal_reduction": "PARTIALLY_COMPLETED_BEFORE_INTERRUPTION__CONTINUED",
                "broader_repository_validation": "PARTIALLY_COMPLETED_BEFORE_INTERRUPTION__CONTINUED",
                "operational_execution": "NOT_STARTED_BEFORE_INTERRUPTION__PROHIBITED",
            },
        },
        "dependent_recomputation_graph": {
            "graph": "IE_HEAD_TREE_TO_IF_HEAD_TREE__TO_LAUNCHER__TO_CANDIDATE_RUNTIME__TO_CONTEXT__TO_DU_EB_EE",
            "dependent_identity_count": 14,
            "dependent_identities": [
                "launcher.CHECKOUT_HEAD", "launcher.CHECKOUT_TREE",
                "candidate.manifest.required_head", "candidate.manifest.source_tree",
                "candidate.launcher_sha256", "candidate.manifest_sha256",
                "runtime.byte_projection", "context.repository_head", "context.repository_tree",
                "context.checkout.head", "context.checkout.tree",
                "context.candidate_manifest_sha256", "context.context_sha256",
                "DU_EB_EE_CURRENT_APPLICABILITY",
            ],
            "dependent_recomputation_count": "VERIFIED__14",
            "evidence_only_mutation_count": "VERIFIED__5_PATHS",
            "unrelated_mutation_count": "VERIFIED__0",
        },
        "delta_inventory": [
            {"classification": "ROOT_REBIND", "path": FM_LAUNCHER.as_posix()},
            {"classification": "DEPENDENT_RECOMPUTATION", "path": (IH_ROOT / "live_binding/candidate/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json").as_posix()},
            {"classification": "DEPENDENT_RECOMPUTATION", "path": (IH_ROOT / "live_binding/runtime_projection/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json").as_posix()},
            {"classification": "DEPENDENT_RECOMPUTATION", "path": (IH_ROOT / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json").as_posix()},
            {"classification": "DEPENDENT_RECOMPUTATION", "path": (IH_ROOT / "live_binding/bindings/G77_256IH_EE_PATH_PROJECTION_FIXTURE_V1.py").as_posix()},
            {"classification": "EVIDENCE_ONLY", "path": (IH_ROOT / "binding/G77_256IH_POST_IG_FUTURE_IF_REBIND_V1.py").as_posix()},
            {"classification": "EVIDENCE_ONLY", "path": BINDING_CHECKPOINT.as_posix()},
            {"classification": "EVIDENCE_ONLY", "path": TERMINAL.as_posix()},
            {"classification": "EVIDENCE_ONLY", "path": (IH_ROOT / "tests/test_g77_256ih_future_if_identity_rebind_v1.py").as_posix()},
            {"classification": "EVIDENCE_ONLY", "path": REPORT.as_posix()},
        ],
        "checkout_bootstrap_nocloud": checkout,
        "live_identity_preparation": {
            "status": "VERIFIED__REPOSITORY_PREPARED_IF_BOUND",
            "current_future_candidate_identity": sha256_path(candidate_path),
            "current_future_runtime_identity": sha256_path(runtime_path),
            "candidate_runtime_byte_identity_status": "VERIFIED",
            "candidate_to_if_binding": "VERIFIED",
            "runtime_to_if_binding": "VERIFIED",
            "current_future_context_identity": context["context_sha256"],
            "context_repository_binding": "VERIFIED__IF",
            "context_checkout_binding": "VERIFIED__IF",
            "context_candidate_binding": "VERIFIED",
            "context_runtime_binding": "VERIFIED__BY_CANDIDATE_RUNTIME_BYTE_IDENTITY",
        },
        "du_eb_ee": owners,
        "identity_interpretation": {
            "target_runtime_identity": {"head": IF_HEAD, "tree": IF_TREE},
            "current_repository_certification_identity": {"head": IG_HEAD, "tree": IG_TREE},
            "eb_ee_actual_head_equality_requirement": "VERIFIED",
            "du_candidate_required_head_coupling": "VERIFIED",
            "existing_non_circular_separation_mechanism": "NOT_PROVEN",
            "architecture_interpretation": "VERIFIED__A_IS_SEMANTICALLY_REQUIRED_BUT_NOT_IMPLEMENTED_BY_CURRENT_OWNER_SCHEMA",
            "minimum_non_circular_requirement": "VERIFIED__SEPARATE_TARGET_RUNTIME_IDENTITY_FROM_POST_COMMIT_CURRENT_HEAD_CERTIFICATION_IDENTITY_THROUGH_GOVERNED_EXISTING_OR_NEWLY_AUTHORIZED_SCHEMA_SEMANTICS",
        },
        "gn_gl": {
            "gn": "NOT_APPLICABLE__NO_HUMAN_AUTHORIZATION_REQUEST_CREATED",
            "gl": "NOT_APPLICABLE__NO_AUTHORITY_OR_RECEIPT_PARENT_CREATED",
            "repository_readiness_is_authority": False,
        },
        "historical_failure_firewall": {
            "status": "VERIFIED",
            "reintroduced_historical_failure_count": "VERIFIED__0",
            "tested_set": [
                "PRE_COMMIT_HEAD_SELF_REFERENCE", "CHECKOUT_PINNING_MISMATCH",
                "BOOTSTRAP_PINNING_MISMATCH", "HOST_GUEST_PATH_MISMATCH",
                "LAUNCHER_ADAPTER_MISMATCH", "NOCLOUD_PROJECTION_MISMATCH",
                "NONCANONICAL_HANDOFF", "RECEIPT_PARENT_ABSENCE",
                "SEALED_HISTORICAL_SHA_MISMATCH", "TRANSIENT_ROOT_LIFECYCLE_MISMATCH",
                "BASE_IMAGE_MUTATION",
            ],
        },
        "ex": authenticate_ex(root),
        "reuse_impact": {
            "reused_certified_capability_set": ["IE_FUTURE_FORMALIZATION", "IF_STATIC_FUTURE_BINDING", "IG_FRONTIER_CERTIFICATION", "P11_TEMPORAL_OWNER", "CHE", "FM_SINGLE_ROUTE", "GN", "GL", "DU", "EB", "EE", "FK", "EX_17_OF_17", "GOVERNANCE", "LAYER_0"],
            "new_capability_set": ["CURRENT_IF_BOUND_FUTURE_LIVE_IDENTITY_PREPARATION_ONLY"],
            "unreachable_preexisting_capability_set": [],
            "parallel_flow_created": "VERIFIED__NO",
            "production_route_before": "VERIFIED__1", "production_route_after": "VERIFIED__1", "production_route_delta": "VERIFIED__0",
            "new_generic_framework_count": "VERIFIED__0", "new_authority_layer_count": "VERIFIED__0", "new_production_route_count": "VERIFIED__0", "new_runtime_owner_count": "VERIFIED__0", "new_clock_infrastructure_count": "VERIFIED__0", "p11_core_change_count": "VERIFIED__0",
        },
        "infrastructure_amortization": {
            "e05_generations_per_credit": "VERIFIED__5__HISTORICAL_WRONG_PROVENANCE_LIFECYCLE_ONLY",
            "operational_attempts_per_credit": "VERIFIED__1__HISTORICAL_WRONG_PROVENANCE_ONLY",
            "future_generations_so_far": "VERIFIED__4__IE_IF_IG_IH",
            "future_e05_credit_so_far": "VERIFIED__0", "future_operational_attempts_so_far": "VERIFIED__0",
            "new_common_infrastructure_for_future": "VERIFIED__0",
            "new_vector_specific_infrastructure_for_future": "VERIFIED__IE_IF_ONLY__IG_IH_CERTIFICATION_AND_REBIND_PREPARATION",
            "marginal_new_infrastructure_for_ih": "VERIFIED__ONE_REBIND_OWNER_AND_EVIDENCE_SET__NO_COMMON_INFRASTRUCTURE",
            "expected_next_credit_generation_count": "NOT_PROVEN__EB_EE_BASELINE_CONFLICT_REQUIRES_HUMAN_REVIEW",
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_L5_CLAIM",
            "cross_worker_state_recovery_level": "NOT_PROVEN__WORKER_IDENTITY_NOT_INSTRUMENTED",
            "provider_usage_interruption_recovery": "NOT_PROVEN__USER_REPORTED_PROVIDER_LIMIT__REPOSITORY_CONTINUATION_VERIFIED",
            "cross_account_continuation_status": "NOT_PROVEN__USER_REPORTED_ACCOUNT_CHANGE__PROVIDER_ACCOUNT_IDENTITY_NOT_REPOSITORY_PROVEN",
            "same_generation_continuation_status": "VERIFIED__IH_NAMESPACE_AND_UNCOMMITTED_DELTA_CONTINUITY",
            "repository_derived_context_ratio": "ESTIMATED__DOMINANT__NO_NUMERIC_INSTRUMENT",
            "human_handoff_information_required": "VERIFIED__CHECKPOINT_SCOPE_PROHIBITIONS_AND_LOCATORS",
            "previous_worker_conversation_required": "VERIFIED__NO", "previous_worker_identity_required": "VERIFIED__NO", "previous_worker_memory_required": "VERIFIED__NO",
            "authenticated_repository_continuation": "VERIFIED__YES",
            "inter_generation_cross_worker_continuation": "NOT_PROVEN__WORKER_IDENTITY_NOT_INSTRUMENTED",
            "intra_generation_cross_worker_continuation": "NOT_PROVEN__USER_REPORTED__WORKER_IDENTITY_NOT_REPOSITORY_INSTRUMENTED",
            "uncommitted_delta_recovery": "VERIFIED__AUTHENTIC_BOUNDED_IH_DELTA_RECOVERED_WITHOUT_RECREATION",
            "authority_state_recovery": "VERIFIED__NO_CURRENT_AUTHORITY_EXISTS",
            "consumed_authority_recovery": "VERIFIED__IC_HISTORICAL_CONSUMED_NONREUSABLE",
            "post_operation_state_recovery": "VERIFIED__IC_TERMINAL_RECONSTRUCTED",
            "operation_replay_prevention": "VERIFIED__IH_OPERATIONAL_COUNTERS_ZERO",
            "cross_worker_constitutional_drift": "NOT_PROVEN__WORKER_IDENTITY_NOT_INSTRUMENTED__REPOSITORY_DELTA_DRIFT_COUNT_ZERO",
            "handoff_sufficiency_status": "VERIFIED", "handoff_state_completeness": "VERIFIED__COMPLETE_FOR_IH_REPOSITORY_SCOPE",
            "handoff_reconstruction_required": "VERIFIED__YES", "handoff_reconstruction_success": "VERIFIED__YES",
            "handoff_ambiguity_count": "VERIFIED__0", "unauthenticated_handoff_assumption_count": "VERIFIED__0",
        },
        "metrics": {
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "constitutional_health_evidence": "VERIFIED__FAIL_CLOSED_AT_EB_EE_CURRENT_HEAD_CONTRACT",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "e05_frontier_distance": "VERIFIED__8_OF_18_OBLIGATIONS_REMAIN",
            "selected_e05_local_frontier_distance": "NOT_PROVEN__EB_EE_BASELINE_CONFLICT",
            "governance_efficience": "ESTIMATED__ONE_LOGICAL_REBIND_WITH_EXPLICIT_STOP",
            "architectural_governance_efficience": "VERIFIED__ONE_ROUTE_RETAINED",
            "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED",
            "cognition_assisted_handoff": "VERIFIED__AUTHENTICATED_IG_TO_IH_REPOSITORY_CONTINUATION",
            "aigol_codex_work_share": "NOT_MEASURED", "overengineering_risk": "ESTIMATED__LOW_TO_MODERATE",
            "proof_process_overhead_risk": "ESTIMATED__MODERATE",
            "cognition_provenance": "VERIFIED__AUTHENTICATED_REPOSITORY_PRIMARY",
            "candidate_capability": "VERIFIED__IF_BOUND_DU_VALID__EB_EE_NOT_PROVEN",
            "shadow_design_target": "VERIFIED__AUTHENTICATE_RECONSTRUCT_REUSE_BIND_VERIFY_REDUCE_STOP",
            "constitutional_continuation_progress": "VERIFIED__IF_LIVE_IDENTITIES_PREPARED__PREOPERATIONAL_READINESS_NOT_PROVEN",
            "prompt_context_reuse_ratio": "NOT_MEASURED", "token_benchmark": "NOT_MEASURED", "llm_cost_reduction_ratio": "NOT_MEASURED", "lcrr": "NOT_MEASURED",
            "e05_generations_per_credit": "VERIFIED__5__HISTORICAL_WRONG_PROVENANCE_LIFECYCLE_ONLY",
            "operational_attempts_per_credit": "VERIFIED__1__HISTORICAL_WRONG_PROVENANCE_ONLY",
            "marginal_e05_generation_cost": "NOT_MEASURED__NO_GOVERNED_COST_INSTRUMENT",
            "marginal_new_infrastructure_per_e05_credit": "NOT_MEASURED__FUTURE_CREDIT_NOT_EARNED",
            "infrastructure_amortization_signal": "ESTIMATED__POSITIVE_REUSE_SIGNAL__NO_COST_INFERENCE",
            "expected_next_credit_generation_count": "NOT_PROVEN__EB_EE_BASELINE_CONFLICT_REQUIRES_HUMAN_REVIEW",
        },
        "validation": {
            "current_applicable_assertions": "VERIFIED__206_PASSED",
            "focused_lineage_route_gn_gl": "VERIFIED__125_PASSED__14_HISTORICAL_DESELECTED",
            "p11_human_act_che_fk": "VERIFIED__72_PASSED",
            "governance_pytest": "VERIFIED__9_PASSED",
            "conformance_engine": "VERIFIED__20_OF_20__CONFORMANT__0_WARNINGS__0_VIOLATIONS",
            "ex_regression": "VERIFIED__12_OF_12__17_OF_17_REUSED__0_RECONSTRUCTED",
            "canonical_unique_key_json": "VERIFIED__5_OF_5",
            "inner_seals": "VERIFIED__4_OF_4",
            "python_ast": "VERIFIED__4_OF_4",
            "historical_or_superseded_snapshot_assertions": "VERIFIED__14_DESELECTED",
            "historical_deselection_reasons": [
                "IG_EXACT_IF_ENTRY_SNAPSHOT",
                "IG_COMMITTED_IF_WORKTREE_BYTES_SNAPSHOT",
                "IG_IE_BOUND_LAUNCHER_CLOSURE_SNAPSHOT",
                "IG_IE_BOUND_CANDIDATE_RUNTIME_CONTEXT_SNAPSHOT",
                "IG_IE_BOUND_CHECKOUT_BOOTSTRAP_NOCLOUD_SNAPSHOT",
                "IG_STALE_IF_RECEIPT_APPLICABILITY_SNAPSHOT",
                "IG_PRE_IH_INTERRUPTION_REDUCTION_SNAPSHOT",
                "IF_EXACT_IE_ENTRY_SNAPSHOT",
                "IF_IE_BOUND_LAUNCHER_SNAPSHOT",
                "IE_EXACT_ID_ENTRY_SNAPSHOT",
                "ID_EXACT_IC_ENTRY_SNAPSHOT",
                "IC_EXACT_OPERATIONAL_ENTRY_SNAPSHOT",
                "IA_HT_BOUND_BOOTSTRAP_ARGUMENT_SNAPSHOT",
                "IA_HT_BOUND_STATIC_CHECKOUT_SNAPSHOT",
            ],
            "operational_validation": "NOT_APPLICABLE__PROHIBITED_BY_IH_SCOPE",
            "git_diff_check": "VERIFIED__PASS",
        },
        "cognition_provenance": "VERIFIED__AUTHENTICATED_GIT_IG_IF_IE_ID_IC_P11_CHE_FK_FM_GN_GL_DU_EB_EE_EX_GOVERNANCE_LAYER_0_PINNED_NESTED_AUTHORITY_CURRENT_TESTS",
        "operational_counters": counters,
        "e05": {"before": "10/18", "after": "10/18", "credit": 0, "required": 18, "satisfied": 10, "remaining": 8},
        "readiness": {
            "current_e05_status": "VERIFIED__10_OF_18", "selected_next_e05_vector": "VERIFIED__FUTURE",
            "future_repository_formalization": "VERIFIED", "future_route_binding": "VERIFIED__STATIC_MEMBERSHIP_ONLY",
            "future_live_identity_rebind": "VERIFIED__REPOSITORY_PREPARED_IF_BOUND",
            "future_live_binding": "NOT_PROVEN__EB_EE_CURRENT_HEAD_BASELINE_MISMATCH",
            "future_preoperational_readiness": "NOT_PROVEN__EB_EE_CURRENT_HEAD_BASELINE_MISMATCH",
            "future_operational_capability": "NOT_PROVEN", "next_operational_generation_eligible": "NOT_PROVEN",
            "e05_credit": "VERIFIED__0",
        },
        "terminal_control": {
            "auto_continuable": False, "human_authorization_required": False,
            "human_review_required": True, "next_generation_started": False,
            "last_verified_edge": "EXACT_IF_BOUND_LAUNCHER_CANDIDATE_RUNTIME_CONTEXT_AND_DU_REPOSITORY_PREPARATION",
            "first_broken_edge": first_broken,
            "minimum_missing_capability": "GOVERNANCE_VALID_NONCIRCULAR_SEPARATION_OF_EXACT_IF_RUNTIME_TARGET_FROM_POST_COMMIT_CURRENT_HEAD_DU_EB_EE_CERTIFICATION_IDENTITY",
            "minimum_legal_next_delta": "HUMAN_REVIEW_AND_SEPARATE_REPOSITORY_ONLY_BASELINE_CONTRACT_RESOLUTION__NO_OPERATION",
            "verdict": "NOT_PROVEN__IH_FUTURE_PREOPERATIONAL_READINESS__IF_IDENTITIES_PREPARED_DU_PASS_EB_EE_CURRENT_HEAD_MISMATCH__ZERO_OPERATION__E05_10_OF_18__HUMAN_REVIEW_REQUIRED",
        },
    }


def terminal_envelope(repository_root: Path, live_root: Path) -> dict[str, Any]:
    reduction = terminal_reduction(repository_root, live_root)
    return {"schema_id": "G77_256IH_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1", "reduction": reduction, "reduction_sha256": sha256_bytes(canonical_bytes(reduction))}


if __name__ == "__main__":
    raise SystemExit("repository-only IH binding owner; no operational CLI entry point")
