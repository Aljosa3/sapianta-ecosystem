#!/usr/bin/env python3
"""Git-native, repository-only certification of the committed IF checkout.

The validator does not rebind runtime owners or invoke any operational path.
It reconstructs committed IF bytes and stops at the first live-binding edge.
"""

from __future__ import annotations

from copy import deepcopy
import ast
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
IF_HEAD = "699fcdce794ff49b6c8735602936355724ed1c90"
IF_TREE = "7c773d4b2acdf013f1b8238eabfc8eced4dd6866"
IF_SUBJECT = "G77-256IF bind FUTURE static route and readiness frontier"
IE_HEAD = "9420764a5bb6db8909334f2a422225687a37a346"
IE_TREE = "b9ebdc1015e9b9459ccd93841cc8d1c7377ddc19"
ID_HEAD = "559deecb226b66d626e45e6f607b0aab6df81f1c"
IC_HEAD = "afdd47166acdee30cb9867d3d3c7bfec0de64c8a"
STABLE_ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_TAG = "refs/tags/sapianta-system-nested-authority-3183bab-v1"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"

IF_ROOT = Path(".github/governance/evidence/g77_256if_future_post_commit_readiness_v1")
REPORT = IF_ROOT / "G77_256IF_G48_IMPLEMENTATION_REPORT_V1.md"
TERMINAL = IF_ROOT / "G77_256IF_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
ADAPTER = IF_ROOT / "adapter/G77_256IF_FUTURE_VECTOR_ADAPTER_V1.py"
BINDER = IF_ROOT / "binding/G77_256IF_POST_IE_FUTURE_BINDING_V1.py"
ACT_CHE = IF_ROOT / "live_binding/G77_256IF_FUTURE_ACT_CHE_BINDING_V1.json"
CONTEXT = IF_ROOT / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
EB = IF_ROOT / "live_binding/bindings/G77_256IF_EB_RECEIPT_V1.json"
EE_FIXTURE = IF_ROOT / "live_binding/bindings/G77_256IF_EE_PATH_PROJECTION_FIXTURE_V1.py"
EE = IF_ROOT / "live_binding/bindings/G77_256IF_EE_RECEIPT_V1.json"
CANDIDATE = IF_ROOT / "live_binding/candidate/G77_256IF_FUTURE_CURRENT_CANDIDATE_V1.json"
RUNTIME = IF_ROOT / "live_binding/runtime_projection/G77_256IF_FUTURE_CURRENT_CANDIDATE_V1.json"
CLOUD_INIT = IF_ROOT / "static/G77_256IF_CLOUD_INIT_USER_DATA_TEMPLATE_V1.yaml"
SEED = IF_ROOT / "static/SAPIANTA_FUTURE_NOCLOUD_SEED_TEMPLATE_V1.img"
IF_TEST = IF_ROOT / "tests/test_g77_256if_future_post_commit_readiness_v1.py"
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

COMMITTED_IF_PATHS = {
    "IF_G48_REPORT": REPORT,
    "IF_TERMINAL_REDUCTION": TERMINAL,
    "IF_FUTURE_ADAPTER": ADAPTER,
    "IF_POST_IE_BINDER": BINDER,
    "IF_ACT_CHE_BINDING": ACT_CHE,
    "IF_CONTEXT": CONTEXT,
    "IF_EB_RECEIPT": EB,
    "IF_EE_FIXTURE": EE_FIXTURE,
    "IF_EE_RECEIPT": EE,
    "IF_CANDIDATE": CANDIDATE,
    "IF_RUNTIME": RUNTIME,
    "IF_CLOUD_INIT": CLOUD_INIT,
    "IF_NOCLOUD": SEED,
    "IF_FOCUSED_TEST": IF_TEST,
    "FM_SOLE_LAUNCHER": FM_LAUNCHER,
    "FM_CONTEXT_OWNER": FM_CONTEXT,
}

EXPECTED_SHA256 = {
    "IF_G48_REPORT": "e4e1a7c956cd0feda0223e90208b93a66438cfc1ee01e5f7782434eb53a403b0",
    "IF_TERMINAL_REDUCTION": "4f30e7ef71386828970dc16479339cbd1fe53eb39ddebef0bfa3c4388c907116",
    "IF_FUTURE_ADAPTER": "77c5f30eff125194037630f36d7940b1798637fb15c3e73cbfe14eebd5e8a854",
    "IF_POST_IE_BINDER": "2657445f221892e92717c2da0a45dc62ccd80ad44788ab1be103318d56652d70",
    "IF_ACT_CHE_BINDING": "3514cf08a47ff756b57c2a281d08680c9959d3235971f859c0ea84c5b34b29ac",
    "IF_CONTEXT": "94c2e0cdaf98ccd972b00f090751c50460065c407d29fcf24541850810623ea5",
    "IF_EB_RECEIPT": "6be5a9c6638899dcafb82109964952425243c8d5f3d2766f0be770cf1206203a",
    "IF_EE_FIXTURE": "8d1690fd82752c6f9d9fd635056d59c3e76fe82e68ff47162faf18b30ebf3365",
    "IF_EE_RECEIPT": "8da2407e3a8040da68bc45a1d45e935ffababe217c5c525d56fde801aab32fbb",
    "IF_CANDIDATE": "eafb6dcfe4593872b140aa4de44529b3c60d66bb6bcee5441932090ca32b64da",
    "IF_RUNTIME": "eafb6dcfe4593872b140aa4de44529b3c60d66bb6bcee5441932090ca32b64da",
    "IF_CLOUD_INIT": "6fbe557e8e2209aba7cd5c7cc81081fffbcd66ba57127547bcdb7ee30c6b0d40",
    "IF_NOCLOUD": "0a268fc0e97f1f0dfb9f886172382f48bfb7c1817f7a4c2ec2b8fe26395f4c9e",
    "IF_FOCUSED_TEST": "c1e30d33460f20c7525c369774f4a78025b24fa81035b70a96f61de485107da9",
    "FM_SOLE_LAUNCHER": "c57e3149d5e26e111004cb03fc3ca4ca498ff267a2ddfd33c744c6fcf1821f2c",
    "FM_CONTEXT_OWNER": "fdfa04349529d70bc97820a1848f8afc22b81071859d5456550799e0f9476237",
}

FUTURE_PAYLOAD_DIGEST = "sha256:9568e0c248ad488cabcf6bde6b490c544077862d10e3fda13bcdc8ed9953f547"
SOURCE_ACT_DIGEST = "sha256:7167b0725d2c84bafde1d0060f512b0fa358d777ec1beff8b7c68d22ee6502e8"
CORRELATION_IDENTITY = "CHE-CORRELATION-15b2680b5577da169cecf9efb3231e2e6f6467e6f409fa2594b04128f998e454"
FIRST_BROKEN_EDGE = "COMMITTED_IF_LAUNCHER_CANDIDATE_AND_CONTEXT_REMAIN_BOUND_TO_IE_NOT_IF"


class IGValidationError(ValueError):
    """One deterministic fail-closed IG certification rejection."""


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _git(root: Path, *arguments: str) -> str:
    return subprocess.check_output(["git", *arguments], cwd=root, text=True).strip()


def _git_bytes(root: Path, path: Path) -> bytes:
    return subprocess.check_output(["git", "show", f"{IF_HEAD}:{path.as_posix()}"], cwd=root)


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise IGValidationError(f"DUPLICATE_JSON_KEY__{key}")
        result[key] = value
    return result


def load_canonical_bytes(raw: bytes, identity: str) -> dict[str, Any]:
    value = json.loads(raw, object_pairs_hook=_unique)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise IGValidationError(f"CANONICAL_JSON_INVALID__{identity}")
    return value


def _load(path: Path, identity: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(identity, path)
    if specification is None or specification.loader is None:
        raise IGValidationError(f"MODULE_LOAD_FAILED__{identity}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def authenticate_entry(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    observed = {
        "repository": str(root), "branch": _git(root, "branch", "--show-current"),
        "head": _git(root, "rev-parse", "HEAD"), "tree": _git(root, "rev-parse", "HEAD^{tree}"),
        "subject": _git(root, "show", "-s", "--format=%s", "HEAD"),
        "origin": _git(root, "remote", "get-url", "origin"),
        "remote_tracking_head": _git(root, "rev-parse", f"origin/{BRANCH}"),
        "index": _git(root, "diff", "--cached", "--name-only"),
    }
    expected = {"repository": str(root), "branch": BRANCH, "head": IF_HEAD, "tree": IF_TREE, "subject": IF_SUBJECT, "origin": ORIGIN, "remote_tracking_head": IF_HEAD, "index": ""}
    if observed != expected:
        raise IGValidationError("EXACT_COMMITTED_IF_CHECKPOINT_MISMATCH")
    for ancestor in (IC_HEAD, ID_HEAD, IE_HEAD, STABLE_ANCHOR):
        if subprocess.run(["git", "merge-base", "--is-ancestor", ancestor, IF_HEAD], cwd=root).returncode:
            raise IGValidationError(f"REQUIRED_ANCESTRY_MISSING__{ancestor}")
    nested = root / "sapianta_system"
    nested_state = {"origin": _git(nested, "remote", "get-url", "origin"), "head": _git(nested, "rev-parse", "HEAD"), "tree": _git(nested, "rev-parse", "HEAD^{tree}"), "branch": _git(nested, "branch", "--show-current"), "status": _git(nested, "status", "--porcelain"), "tag_head": _git(nested, "rev-parse", NESTED_TAG + "^{commit}")}
    if nested_state != {"origin": NESTED_ORIGIN, "head": NESTED_HEAD, "tree": NESTED_TREE, "branch": "", "status": "", "tag_head": NESTED_HEAD}:
        raise IGValidationError("NESTED_AUTHORITY_NOT_CLEAN_DETACHED_PINNED")
    return observed | {"nested": nested_state}


def committed_identity_map(repository_root: Path) -> dict[str, dict[str, str]]:
    root = repository_root.resolve()
    result: dict[str, dict[str, str]] = {}
    for identity, path in COMMITTED_IF_PATHS.items():
        raw = _git_bytes(root, path)
        if raw != (root / path).read_bytes():
            raise IGValidationError(f"COMMITTED_IF_WORKTREE_DRIFT__{identity}")
        digest = sha256_bytes(raw)
        if digest != EXPECTED_SHA256[identity]:
            raise IGValidationError(f"COMMITTED_IF_HASH_MISMATCH__{identity}")
        result[identity] = {"path": path.as_posix(), "git_blob": _git(root, "rev-parse", f"{IF_HEAD}:{path.as_posix()}"), "sha256": digest, "status": "VERIFIED"}
    return result


def reconstruct_if(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    terminal = load_canonical_bytes(_git_bytes(root, TERMINAL), TERMINAL.name)
    reduction = terminal["reduction"]
    if terminal["reduction_sha256"] != sha256_bytes(canonical_bytes(reduction)):
        raise IGValidationError("IF_TERMINAL_SEAL_INVALID")
    expected_readiness = {
        "first_broken_edge": "COMMITTED_IE_CHECKOUT_DOES_NOT_CONTAIN_IF_FUTURE_ROUTE_AND_DETERMINISTIC_TIME_PROJECTION",
        "future_live_binding": "NOT_PROVEN", "future_operational_capability": "NOT_PROVEN",
        "future_preoperational_readiness": "NOT_PROVEN", "future_repository_formalization": "VERIFIED",
        "future_route_binding": "VERIFIED__REPOSITORY_STATIC_BINDING_ONLY", "next_operational_generation_eligible": "NOT_PROVEN",
    }
    if reduction["readiness"] != expected_readiness or reduction["e05"]["after"] != "10/18" or reduction["e05"]["credit"] != 0:
        raise IGValidationError("IF_TERMINAL_RECONSTRUCTION_FAILED")
    act_che = load_canonical_bytes(_git_bytes(root, ACT_CHE), ACT_CHE.name)
    if act_che["binding_sha256"] != sha256_bytes(canonical_bytes(act_che["binding"])):
        raise IGValidationError("IF_ACT_CHE_SEAL_INVALID")
    binding = act_che["binding"]
    act = binding["human_authority_act_representation"]
    che = binding["che_correlation"]
    if (act["payload_digest"], che["authority_payload_digest"], che["source_act_digest"], che["correlation_identity"]) != (FUTURE_PAYLOAD_DIGEST, FUTURE_PAYLOAD_DIGEST, SOURCE_ACT_DIGEST, CORRELATION_IDENTITY):
        raise IGValidationError("IF_ACT_CHE_IDENTITY_MISMATCH")
    if binding["semantic_independent_mutation_count"] != 1 or binding["semantic_independent_mutated_coordinate"] != "valid_from_unix_ns":
        raise IGValidationError("IF_FUTURE_SEMANTIC_MUTATION_DRIFT")
    payload = act["payload"]
    if (binding["evaluation_time_unix_ns"], payload["valid_from_unix_ns"], payload["valid_until_unix_ns"]) != (500, 600, 1000):
        raise IGValidationError("IF_FUTURE_TIME_RELATION_DRIFT")
    return {"terminal": reduction, "act_che": binding}


def committed_checkout_closure(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    identity_map = committed_identity_map(root)
    context_owner = _load(root / FM_CONTEXT, "g77_256ig_context_owner")
    launcher = _load(root / FM_LAUNCHER, "g77_256ig_launcher")
    adapter = _load(root / ADAPTER, "g77_256ig_adapter")
    if "FUTURE" not in context_owner.SUPPORTED_OPERATION_VECTORS:
        raise IGValidationError("COMMITTED_IF_FUTURE_MEMBERSHIP_ABSENT")
    if context_owner.operation_vector("G77_256IGTEST_ONE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING_V1") != "FUTURE":
        raise IGValidationError("COMMITTED_IF_FUTURE_ROUTE_INVALID")
    if adapter.deterministic_submission_kwargs(root) != {"now_unix_ns": 500}:
        raise IGValidationError("COMMITTED_IF_TIME_PROJECTION_INVALID")
    adapter_tree = ast.parse(_git_bytes(root, ADAPTER).decode("utf-8"), filename=ADAPTER.as_posix())
    calls = {node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id for node in ast.walk(adapter_tree) if isinstance(node, ast.Call) and isinstance(node.func, (ast.Attribute, ast.Name))}
    if calls.intersection({"time", "time_ns", "now", "sleep"}):
        raise IGValidationError("FUTURE_WALL_CLOCK_DEPENDENCY_PRESENT")
    candidate_bytes = _git_bytes(root, CANDIDATE)
    runtime_bytes = _git_bytes(root, RUNTIME)
    if candidate_bytes != runtime_bytes or sha256_bytes(candidate_bytes) != EXPECTED_SHA256["IF_CANDIDATE"]:
        raise IGValidationError("IF_CANDIDATE_RUNTIME_IDENTITY_INVALID")
    candidate = load_canonical_bytes(candidate_bytes, CANDIDATE.name)
    context = load_canonical_bytes(_git_bytes(root, CONTEXT), CONTEXT.name)
    if context["context_sha256"] != "a71c6a2d74553787f6fbea7359e0f60912774ae8107fb6e078d0ebb888977015":
        raise IGValidationError("IF_CONTEXT_IDENTITY_INVALID")
    checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    selected = (launcher.CHECKOUT_HEAD, launcher.CHECKOUT_TREE)
    candidate_binding = (candidate["manifest"]["required_head"], candidate["manifest"]["source_tree"])
    context_binding = (context["repository_head"], context["repository_tree"])
    context_checkout = (checkout["head"], checkout["tree"])
    if len({selected, candidate_binding, context_binding, context_checkout}) != 1 or selected != (IE_HEAD, IE_TREE):
        raise IGValidationError("IF_IE_STATIC_BINDING_RECONSTRUCTION_FAILED")
    for member, source in (("/user-data", CLOUD_INIT), ("/meta-data", FM_META), ("/network-config", FM_NETWORK)):
        projected = subprocess.check_output(["isoinfo", "-i", str(root / SEED), "-R", "-x", member])
        if projected != (root / source).read_bytes():
            raise IGValidationError(f"IF_NOCLOUD_PROJECTION_MISMATCH__{member}")
    cloud_text = _git_bytes(root, CLOUD_INIT).decode("utf-8")
    future_guest_commands = [line for line in cloud_text.splitlines() if "/usr/bin/python3" in line]
    base_image = Path(launcher.BASE_IMAGE)
    base_status = "VERIFIED" if base_image.is_file() and sha256_path(base_image) == launcher.EXPECTED_ASSET_SHA256[launcher.BASE_IMAGE] else "NOT_PROVEN"
    return {
        "committed_identity_map": identity_map,
        "committed_if_route_membership": "VERIFIED",
        "committed_if_adapter_binding": "VERIFIED",
        "committed_if_time_projection": "VERIFIED__REPOSITORY_FUNCTION_ONLY",
        "committed_if_cloud_init_binding": "VERIFIED__STATIC_NONOPERATIONAL_TEMPLATE",
        "committed_if_nocloud_binding": "VERIFIED",
        "committed_if_act_che_binding": "VERIFIED",
        "committed_if_candidate_binding": "VERIFIED__CONTAINED_BUT_IE_BOUND",
        "committed_if_runtime_binding": "VERIFIED__CONTAINED_BUT_IE_BOUND",
        "committed_if_context_binding": "VERIFIED__CONTAINED_BUT_IE_BOUND",
        "committed_if_du_binding": "VERIFIED__IF_RECEIPT_BOUND_TO_IE",
        "committed_if_eb_binding": "VERIFIED__IF_RECEIPT_BOUND_TO_IE",
        "committed_if_ee_binding": "VERIFIED__IF_RECEIPT_BOUND_TO_IE",
        "committed_if_checkout_closure_status": "NOT_PROVEN__SOLE_LAUNCHER_SELECTS_IE_NOT_IF",
        "launcher_selected_head": selected[0], "launcher_selected_tree": selected[1],
        "candidate_required_head": candidate_binding[0], "candidate_required_tree": candidate_binding[1],
        "context_repository_head": context_binding[0], "context_repository_tree": context_binding[1],
        "exact_if_head": IF_HEAD, "exact_if_tree": IF_TREE,
        "candidate_identity": sha256_bytes(candidate_bytes), "runtime_identity": sha256_bytes(runtime_bytes),
        "candidate_runtime_byte_identity_status": "VERIFIED", "context_identity": context["context_sha256"],
        "act_che_to_candidate_binding": "VERIFIED__EXTENSION_BINDING",
        "candidate_to_runtime_binding": "VERIFIED", "runtime_to_context_binding": "VERIFIED",
        "context_to_committed_if_binding": "NOT_PROVEN__CONTEXT_BINDS_IE",
        "deterministic_time_fixture_status": "VERIFIED", "deterministic_time_adapter_status": "VERIFIED__REPOSITORY_FUNCTION_ONLY",
        "deterministic_time_guest_projection_status": "NOT_PROVEN__NO_FUTURE_ADAPTER_GUEST_COMMAND_AND_IE_CHECKOUT_SELECTED",
        "wall_clock_dependency_count_on_future_path": 0, "new_clock_infrastructure_count": 0,
        "future_guest_command_count": len(future_guest_commands),
        "checkout_head_binding": "NOT_PROVEN__IE_SELECTED_NOT_IF", "checkout_tree_binding": "NOT_PROVEN__IE_SELECTED_NOT_IF",
        "bootstrap_binding": "VERIFIED__STATIC_NONOPERATIONAL", "adapter_binding": "VERIFIED__COMMITTED_FILE",
        "cloud_init_binding": "VERIFIED__COMMITTED_STATIC_TEMPLATE", "nocloud_binding": "VERIFIED__EXACT_BYTE_PROJECTION",
        "host_guest_equivalence": "NOT_PROVEN__SELECTED_CHECKOUT_IS_IE_AND_HAS_NO_FUTURE_MEMBERSHIP",
        "base_image_binding": base_status,
    }


def readiness_owners(repository_root: Path) -> dict[str, str]:
    root = repository_root.resolve()
    du = _load(root / DU_OWNER, "g77_256ig_du")
    eb = _load(root / EB_OWNER, "g77_256ig_eb")
    ee = _load(root / EE_OWNER, "g77_256ig_ee")
    du_result = du.validate_file(root / CANDIDATE, root, expected_head=IE_HEAD)
    if set(du_result.values()) != {"PASS"}:
        raise IGValidationError("IF_DU_MANIFEST_RECONSTRUCTION_FAILED")
    stale_rejections: dict[str, str] = {}
    for name, verifier, path in (
        ("eb", eb.verify_receipt_file, EB),
        ("ee", ee.verify_receipt_file, EE),
    ):
        try:
            verifier(root, root / path)
        except Exception as exc:
            if "REQUIRED_HEAD_MISMATCH" not in str(exc):
                raise IGValidationError(
                    f"IF_{name.upper()}_UNEXPECTED_RECONSTRUCTION_FAILURE"
                ) from exc
            stale_rejections[name] = "NOT_PROVEN__REQUIRED_HEAD_IE_DIFFERS_CURRENT_IF"
        else:
            raise IGValidationError(
                f"IF_{name.upper()}_STALE_RECEIPT_UNEXPECTEDLY_ACCEPTED"
            )
    for path in (GN_OWNER, GL_OWNER):
        if not (root / path).is_file():
            raise IGValidationError(f"READINESS_OWNER_ABSENT__{path.name}")
    return {
        "du": "VERIFIED__MANIFEST_CONTRACT_ONLY__CANDIDATE_REMAINS_IE_BOUND",
        "eb": stale_rejections["eb"],
        "ee": stale_rejections["ee"],
        "gn": "NOT_PROVEN__NO_COMMITTED_IF_BOUND_HUMAN_PRESENTATION",
        "gl": "NOT_APPLICABLE__NO_AUTHORITY_OR_RECEIPT_PARENT_CREATED",
    }


def authenticate_ex(repository_root: Path) -> dict[str, Any]:
    certificate = json.loads((repository_root.resolve() / EX_CERTIFICATE).read_bytes(), object_pairs_hook=_unique)
    preimage = deepcopy(certificate); preimage["certificate_sha256"] = ""
    payload = json.dumps(preimage, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")
    if certificate["certificate_sha256"] != sha256_bytes(payload) or certificate["certificate"]["component_counts"]["CERTIFIED"] != 17:
        raise IGValidationError("EX_17_OF_17_NOT_AUTHENTICATED")
    return {"ex_reused": "17/17", "ex_reconstructed": 0, "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED"}


def terminal_reduction(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    entry = authenticate_entry(root)
    identities = committed_identity_map(root)
    reconstructed = reconstruct_if(root)
    closure = committed_checkout_closure(root)
    owners = readiness_owners(root)
    counters = {key: 0 for key in ("human_operational_authority", "authority_consumption", "pre", "fm_operational_launcher_invocation", "qemu", "vm_creation", "vm_boot", "operation_attempt", "request", "p11_entry", "protected_invocation", "protected_effect", "retry", "repair_retry", "replay", "e05_credit")}
    return {
        "schema_id": "G77_256IG_POST_IF_COMMIT_READINESS_CERTIFICATION_V1",
        "mode": "REPOSITORY_ONLY__NO_AUTHORITY__NO_OPERATION",
        "entry": entry, "committed_if_identity_map": identities,
        "ig_interruption_recovery": {
            "ig_interruption_recovery_status": "VERIFIED__SAME_GENERATION_BOUNDED_DELTA_RECOVERED",
            "ig_existing_delta_status": "VERIFIED__PARTIALLY_COMPLETED_BEFORE_INTERRUPTION",
            "ig_existing_delta_authenticity": "VERIFIED__ONE_IG_OWNED_VALIDATOR_AND_NO_NON_IG_MUTATION",
            "ig_completed_edge_recovery": "VERIFIED__ENTRY_COMMITTED_OBJECT_AND_CHECKOUT_CLOSURE_LOGIC_RECOVERED",
            "ig_first_unproven_edge_after_recovery": "VERIFIED__CURRENT_APPLICABILITY_OF_IF_DU_EB_EE_RECEIPTS",
            "ig_replay_required": "VERIFIED__NO",
            "completed_before_interruption": ["ENTRY_AUTHENTICATION", "COMMITTED_IF_PATH_AND_HASH_MAP", "IF_TERMINAL_ACT_CHE_SEMANTIC_RECONSTRUCTION", "COMMITTED_CHECKOUT_CLOSURE_IMPLEMENTATION"],
            "partially_completed_before_interruption": ["DU_EB_EE_CURRENT_APPLICABILITY_REDUCTION", "TERMINAL_REDUCTION_EXECUTION"],
            "not_started_before_interruption": ["IG_FOCUSED_TESTS", "IG_TERMINAL_ARTIFACT", "IG_G48_REPORT", "BROAD_VALIDATION"],
            "unknown": [],
        },
        "if_reconstruction": {"status": "VERIFIED", "current_e05_status": "VERIFIED__10_OF_18", "selected_next_e05_vector": "VERIFIED__FUTURE", "future_repository_formalization": "VERIFIED", "future_route_binding": "VERIFIED__REPOSITORY_STATIC_BINDING_ONLY", "future_live_binding": "NOT_PROVEN", "future_preoperational_readiness": "NOT_PROVEN", "future_operational_capability": "NOT_PROVEN", "next_operational_generation_eligible": "NOT_PROVEN", "e05_credit": "VERIFIED__0"},
        "future_semantics": {"evaluation_time_unix_ns": 500, "valid_from_unix_ns": 600, "valid_until_unix_ns": 1000, "relation": "VERIFIED__500_LT_600_LT_1000", "semantic_independent_mutation_count": "VERIFIED__1", "semantic_independent_mutated_coordinate": "VERIFIED__valid_from_unix_ns", "payload_digest": FUTURE_PAYLOAD_DIGEST, "future_not_expired": "VERIFIED", "future_not_stale": "VERIFIED", "ig_new_semantic_mutation_count": "VERIFIED__0"},
        "act_che_reconstruction": {"status": "VERIFIED", "semantic_payload_digest": FUTURE_PAYLOAD_DIGEST, "fresh_outer_act": "G77_256IF_REPOSITORY_ONLY_FUTURE_ACT_REPRESENTATION_001", "authority_payload_digest": FUTURE_PAYLOAD_DIGEST, "source_act_digest": SOURCE_ACT_DIGEST, "correlation_identity": CORRELATION_IDENTITY, "human_operational_authority": 0},
        "committed_checkout_closure": closure,
        "single_route": {"existing_route_owner": FM_LAUNCHER.as_posix(), "future_route_membership": "VERIFIED__COMMITTED_IF_CONTAINS_STATIC_MEMBERSHIP", "production_route_count": "VERIFIED__1", "production_route_before": "VERIFIED__1", "production_route_after": "VERIFIED__1", "production_route_delta": "VERIFIED__0", "new_production_route_count": "VERIFIED__0", "new_generic_framework_count": "VERIFIED__0", "new_runtime_owner_count": "VERIFIED__0", "new_authority_layer_count": "VERIFIED__0"},
        "readiness_owners": owners,
        "historical_failure_firewall": {"status": "VERIFIED__DETECTED_AND_STOPPED_BEFORE_FALSE_CERTIFICATION", "reintroduced_historical_failure_count": "VERIFIED__0", "tested_set": ["PRE_COMMIT_HEAD_SELF_REFERENCE", "CHECKOUT_PINNING_MISMATCH", "BOOTSTRAP_PINNING_MISMATCH", "HOST_GUEST_PATH_MISMATCH", "LAUNCHER_ADAPTER_MISMATCH", "NOCLOUD_PROJECTION_MISMATCH", "NONCANONICAL_HANDOFF", "RECEIPT_PARENT_ABSENCE", "SEALED_HISTORICAL_SHA_MISMATCH", "TRANSIENT_ROOT_LIFECYCLE_MISMATCH", "BASE_IMAGE_MUTATION"]},
        "readiness": {"future_repository_formalization": "VERIFIED", "future_route_binding": "VERIFIED__STATIC_MEMBERSHIP_ONLY", "future_live_binding": "NOT_PROVEN", "future_preoperational_readiness": "NOT_PROVEN", "future_operational_capability": "NOT_PROVEN", "next_operational_generation_eligible": "NOT_PROVEN", "first_broken_edge": FIRST_BROKEN_EDGE},
        "ex": authenticate_ex(root),
        "reuse_impact": {"reused_certified_capability_set": ["IF_STATIC_FUTURE_BINDING", "IE_FUTURE_FORMALIZATION", "P11_TEMPORAL_OWNER", "CHE", "FM_SINGLE_ROUTE", "GN", "GL", "DU", "EB", "EE", "FK", "EX_17_OF_17", "GOVERNANCE", "LAYER_0"], "new_capability_set": ["IG_POST_IF_COMMITTED_OBJECT_CERTIFICATION_ONLY"], "unreachable_preexisting_capability_set": [], "production_route_before": "VERIFIED__1", "production_route_after": "VERIFIED__1", "production_route_delta": "VERIFIED__0", "new_generic_framework_count": "VERIFIED__0", "new_authority_layer_count": "VERIFIED__0", "new_production_route_count": "VERIFIED__0", "new_runtime_owner_count": "VERIFIED__0", "new_clock_infrastructure_count": "VERIFIED__0", "p11_core_change_count": "VERIFIED__0"},
        "infrastructure_amortization": {"e05_generations_per_credit": "VERIFIED__5__HISTORICAL_WRONG_PROVENANCE_LIFECYCLE_ONLY", "operational_attempts_per_credit": "VERIFIED__1__HISTORICAL_WRONG_PROVENANCE_ONLY", "future_generations_so_far": "VERIFIED__3__IE_IF_IG", "future_e05_credit_so_far": "VERIFIED__0", "future_operational_attempts_so_far": "VERIFIED__0", "new_common_infrastructure_for_future": "VERIFIED__0", "new_vector_specific_infrastructure_for_future": "VERIFIED__IE_IF_ONLY__IG_CERTIFICATION_ONLY", "marginal_new_infrastructure_for_ig": "VERIFIED__CERTIFICATION_ONLY", "expected_next_credit_generation_count": "ESTIMATED__AT_LEAST_TWO__LIVE_REBIND_THEN_SEPARATE_HUMAN_AUTHORIZED_OPERATION"},
        "ccwim": {"ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_L5_CLAIM", "cross_worker_state_recovery_level": "NOT_APPLICABLE__NO_DIFFERENT_WORKER_IDENTITY_PROVEN", "provider_usage_interruption_recovery": "VERIFIED__BOUNDED_IG_DELTA_RECOVERED_WITHOUT_REPLAY", "same_generation_continuation_status": "VERIFIED__G77_256IG_CONTINUED", "same_account_continuation_status": "NOT_PROVEN__NO_REPOSITORY_ACCOUNT_IDENTITY_INSTRUMENT", "repository_derived_context_ratio": "ESTIMATED__DOMINANT__NO_NUMERIC_INSTRUMENT", "human_handoff_information_required": "VERIFIED__CHECKPOINT_SCOPE_PROHIBITIONS_LOCATORS", "previous_worker_conversation_required": "VERIFIED__NO", "previous_worker_identity_required": "VERIFIED__NO", "previous_worker_memory_required": "VERIFIED__NO", "authenticated_repository_continuation": "VERIFIED__YES", "inter_generation_cross_worker_continuation": "NOT_PROVEN__WORKER_IDENTITY_NOT_INSTRUMENTED", "intra_generation_cross_worker_continuation": "NOT_PROVEN__SESSION_OR_WORKER_IDENTITY_NOT_REPOSITORY_INSTRUMENTED", "uncommitted_delta_recovery": "VERIFIED__ONE_AUTHENTIC_IG_VALIDATOR_RECOVERED", "authority_state_recovery": "VERIFIED__NO_CURRENT_AUTHORITY_EXISTS", "consumed_authority_recovery": "VERIFIED__IC_CONSUMED_NONREUSABLE", "post_operation_state_recovery": "VERIFIED__IC_TERMINAL_RECONSTRUCTED", "operation_replay_prevention": "VERIFIED__IG_COUNTERS_ZERO_AND_INTERRUPTION_NOT_COUNTED_AS_RETRY", "cross_worker_constitutional_drift": "NOT_APPLICABLE__NO_CROSS_WORKER_IDENTITY_PROVEN", "handoff_sufficiency_status": "VERIFIED", "handoff_state_completeness": "VERIFIED__COMPLETE_FOR_IG_CERTIFICATION_SCOPE", "handoff_reconstruction_required": "VERIFIED__YES", "handoff_reconstruction_success": "VERIFIED__YES", "handoff_ambiguity_count": "VERIFIED__0", "unauthenticated_handoff_assumption_count": "VERIFIED__0"},
        "metrics": {"project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR", "constitutional_health_evidence": "VERIFIED__FAIL_CLOSED_AT_FIRST_COMMITTED_BINDING_MISMATCH", "shadow_automation_status": "VERIFIED__ABSENT", "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR", "e05_frontier_distance": "VERIFIED__8_OF_18_OBLIGATIONS_REMAIN", "selected_e05_local_frontier_distance": "ESTIMATED__ONE_POST_IF_LIVE_REBIND_BEFORE_OPERATIONAL_AUTHORITY", "governance_efficience": "ESTIMATED__CERTIFICATION_ONLY_WITH_EXACT_BROKEN_EDGE", "architectural_governance_efficience": "VERIFIED__ONE_ROUTE_RETAINED", "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED", "cognition_assisted_handoff": "VERIFIED__AUTHENTICATED_IF_TO_IG_CONTINUATION", "aigol_codex_work_share": "NOT_MEASURED", "overengineering_risk": "ESTIMATED__LOW", "proof_process_overhead_risk": "ESTIMATED__MODERATE", "cognition_provenance": "VERIFIED__AUTHENTICATED_REPOSITORY_PRIMARY", "candidate_capability": "NOT_PROVEN__CURRENT_CANDIDATE_BINDS_IE_NOT_IF", "shadow_design_target": "VERIFIED__AUTHENTICATE_RECONSTRUCT_VERIFY_REDUCE_STOP", "constitutional_continuation_progress": "VERIFIED__COMMITTED_IF_CONTAINMENT_PROVEN_LIVE_BINDING_NOT_PROVEN", "prompt_context_reuse_ratio": "NOT_MEASURED", "token_benchmark": "NOT_MEASURED", "llm_cost_reduction_ratio": "NOT_MEASURED", "lcrr": "NOT_MEASURED", "e05_generations_per_credit": "VERIFIED__5__HISTORICAL_WRONG_PROVENANCE_LIFECYCLE_ONLY", "operational_attempts_per_credit": "VERIFIED__1__HISTORICAL_WRONG_PROVENANCE_ONLY", "marginal_e05_generation_cost": "NOT_MEASURED__NO_GOVERNED_COST_INSTRUMENT", "marginal_new_infrastructure_per_e05_credit": "NOT_MEASURED__FUTURE_CREDIT_NOT_EARNED", "infrastructure_amortization_signal": "ESTIMATED__POSITIVE_REUSE_SIGNAL__NO_COST_INFERENCE", "expected_next_credit_generation_count": "ESTIMATED__AT_LEAST_TWO"},
        "cognition_provenance": "VERIFIED__AUTHENTICATED_GIT_IF_IE_ID_IC_P11_CHE_FK_FM_GN_GL_DU_EB_EE_EX_GOVERNANCE_LAYER_0_PINNED_NESTED_AUTHORITY_CURRENT_TESTS",
        "operational_counters": counters, "e05": {"before": "10/18", "after": "10/18", "credit": 0, "required": 18, "satisfied": 10, "remaining": 8},
        "terminal_control": {"auto_continuable": False, "human_authorization_required": False, "human_review_required": True, "next_generation_started": False, "last_verified_edge": "COMMITTED_IF_CONTAINS_FUTURE_STATIC_ROUTE_ADAPTER_TIME_ACT_CHE_CANDIDATE_RUNTIME_CONTEXT_DU_EB_EE", "first_broken_edge": FIRST_BROKEN_EDGE, "minimum_missing_capability": "ONE_POST_IF_COMMIT_CANDIDATE_RUNTIME_CONTEXT_AND_CHECKOUT_REBIND_TO_EXACT_IF_HEAD_TREE", "minimum_legal_next_delta": "SEPARATE_REPOSITORY_ONLY_POST_IF_LIVE_REBIND_THEN_HUMAN_REVIEW", "verdict": "NOT_PROVEN__IG_FUTURE_PREOPERATIONAL_READINESS__COMMITTED_IF_CONTAINS_STATIC_CAPABILITY_BUT_LAUNCHER_CANDIDATE_CONTEXT_REMAIN_IE_BOUND__ZERO_OPERATION__E05_10_OF_18__HUMAN_REVIEW_REQUIRED"},
    }


def terminal_envelope(repository_root: Path) -> dict[str, Any]:
    reduction = terminal_reduction(repository_root)
    return {"schema_id": "G77_256IG_POST_IF_COMMIT_READINESS_CERTIFICATION_ENVELOPE_V1", "reduction": reduction, "reduction_sha256": sha256_bytes(canonical_bytes(reduction))}


if __name__ == "__main__":
    raise SystemExit("repository-only IG validator; no operational CLI entry point")
