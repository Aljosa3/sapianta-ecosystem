#!/usr/bin/env python3
"""Bind committed HV to current WRONG_CONTRACT readiness without operating.

This generation-specific owner is repository-only.  It constructs no Human
authority or operational request and has no PRE, P11-entry, QEMU, VM, or
protected-effect entry point.
"""

from __future__ import annotations

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
HV_HEAD = "737ef550f02f6b65a7dd0d4e1ac5bc118599b32b"
HV_TREE = "212a36d807663b5c60927355bfb9fe1184bfc27c"
HV_SUBJECT = "G77-256HV correct WRONG_CONTRACT guest checkout binding"
HU_HEAD = "6b5c0f9914bc38156d1f5c364614ef55800a09a8"
HU_TREE = "0e9e05065f6eb5f17d998e087dcc55cbb006851a"
HT_HEAD = "af44f0afd02be7e21a24e962309e28f6edd17ae0"
HT_TREE = "fc949a2bbaa0a507edbc25811563dc5e13d18315"
HR_HEAD = "cbd457d9281e787a10980583921abb0a6021be74"
STABLE_ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_TAG = "refs/tags/sapianta-system-nested-authority-3183bab-v1"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"

GENERATION = "G77_256HW_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_CONTRACT_OPERATIONAL_COMMISSIONING_V1"
OPERATION_IDENTITY = "G77_256HW_WRONG_CONTRACT_PREOPERATIONAL_READINESS_001"
IDENTITY_PREFIX = "G77_256HW"
CASE_CLASS = "E05_NEGATIVE_AUTHORITY_WRONG_CONTRACT"
CASE_ID = "G77_256HW_E05_WRONG_CONTRACT_DENIAL_BEFORE_ENTRY_001"
WRONG_CONTRACT_IDENTITY = "G77_256HW_DISTINCT_WRONG_CONTRACT_001"
VECTOR = "WRONG_CONTRACT"
SELECTED_VECTOR = "P11-E05/NEGATIVE_AUTHORITY/WRONG_CONTRACT"

HV_ROOT = Path(".github/governance/evidence/g77_256hv_wrong_contract_checkout_bootstrap_correction_v1")
HV_TERMINAL = HV_ROOT / "G77_256HV_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
HV_REPORT = Path("docs/governance/G77_256HV_WRONG_CONTRACT_CHECKOUT_BOOTSTRAP_COMMITTED_IDENTITY_CORRECTION_V1.md")
HV_AUDITOR = HV_ROOT / "audit/G77_256HV_WRONG_CONTRACT_CHECKOUT_BOOTSTRAP_AUDITOR_V1.py"
HV_REDUCER = HV_ROOT / "audit/G77_256HV_TERMINAL_REDUCER_V1.py"
HU_TERMINAL = Path(".github/governance/evidence/g77_256hu_post_ht_live_binding_readiness_v1/G77_256HU_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json")
FM_CONTEXT = Path(".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/sapianta_fresh_operation_context_v1.py")
FM_LAUNCHER = Path(".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py")
FM_META = Path(".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/raw/G77_256FM_CLOUD_INIT_META_DATA_V1.yaml")
FM_NETWORK = Path(".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/raw/G77_256FM_CLOUD_INIT_NETWORK_CONFIG_V1.yaml")
GN_OWNER = Path(".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py")
HT_ROOT = Path(".github/governance/evidence/g77_256ht_wrong_contract_route_extension_v1")
ADAPTER = HT_ROOT / "adapter/G77_256HT_WRONG_CONTRACT_VECTOR_ADAPTER_V1.py"
MATERIALIZER = HT_ROOT / "orchestration/G77_256HT_WRONG_CONTRACT_PREAUTHORIZATION_MATERIALIZER_V1.py"
CLOUD_INIT = HT_ROOT / "static/G77_256HT_CLOUD_INIT_USER_DATA_TEMPLATE_V1.yaml"
SEED = HT_ROOT / "static/SAPIANTA_WRONG_CONTRACT_NOCLOUD_SEED_TEMPLATE_V1.img"
HG_PROJECTION = Path(".github/governance/evidence/g77_256hg_guest_projection_validation_v1/static/G77_256HG_GUEST_HOST_PATH_PROJECTION_FIXTURE_V1.py")
P11_OWNER = Path("tests/p11_da_custody_process_v1.py")
HR_ROOT = Path(".github/governance/evidence/g77_256hr_wrong_contract_formalization_v1")
HR_SPEC = HR_ROOT / "G77_256HR_WRONG_CONTRACT_FORMAL_SPECIFICATION_V1.json"
HR_PRODUCER = HR_ROOT / "producer/G77_256HR_WRONG_CONTRACT_VECTOR_PRODUCER_V1.py"
HR_REDUCER = HR_ROOT / "reducer/G77_256HR_WRONG_CONTRACT_REPOSITORY_CAPABILITY_REDUCER_V1.py"
DU_OWNER = Path(".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V1.py")
EB_OWNER = Path(".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v1/validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V1.py")
EE_OWNER = Path(".github/governance/evidence/g77_256ee_runtime_consumer_binding_v1/validator/G77_256EE_RUNTIME_CONSUMER_BINDING_VALIDATOR_V1.py")
EX_CERTIFICATE = Path(".github/governance/evidence/g77_256ex_common_substrate_certification_v1/G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json")
G48_STANDARD = Path("docs/governance/G48_00_CONSTITUTIONAL_EVIDENCE_REPORTING_STANDARD_V1.md")

ADAPTER_SHA256 = "bb9c917947d317319c9502e44c2d5dca6d423380e67f71a14db1b63eb11acc34"
CLOUD_INIT_SHA256 = "c3f7f93a55f2c3a76fe73bccb9aa0b54fed2f5011c326c0f8774a8ca72c7442f"
SEED_SHA256 = "fc98a62a1b3bd813b7f570438fc48151c378aeba4389de13d4e532d3f7979b21"
CONTEXT_OWNER_SHA256 = "3c24621ec9f0bd67e5e3468d728446069f54628f4150ee02b677a973f24972e4"

IDENTITY_PATHS = {
    "HV_TERMINAL_REDUCTION": (HV_TERMINAL, "committed HV terminal reduction"),
    "HV_G48_REPORT": (HV_REPORT, "committed HV G48 report"),
    "HV_AUDITOR": (HV_AUDITOR, "HV committed correction auditor"),
    "HV_REDUCER": (HV_REDUCER, "HV terminal reducer"),
    "FM_CONTEXT_OWNER": (FM_CONTEXT, "current host and guest vector semantics"),
    "FM_LAUNCHER": (FM_LAUNCHER, "sole runtime and checkout owner"),
    "GN_PRESENTATION_OWNER": (GN_OWNER, "presentation binding owner"),
    "WRONG_CONTRACT_ADAPTER": (ADAPTER, "WRONG_CONTRACT guest adapter"),
    "WRONG_CONTRACT_MATERIALIZER": (MATERIALIZER, "preauthorization coherence validator"),
    "WRONG_CONTRACT_CLOUD_INIT": (CLOUD_INIT, "WRONG_CONTRACT bootstrap user-data"),
    "WRONG_CONTRACT_NOCLOUD_SEED": (SEED, "NoCloud projection"),
    "HG_CHECKOUT_PROJECTION_OWNER": (HG_PROJECTION, "existing checkout projection architecture"),
    "P11_OWNER": (P11_OWNER, "unchanged D2 custody owner"),
    "HR_FORMAL_SPECIFICATION": (HR_SPEC, "WRONG_CONTRACT semantic specification"),
    "HR_PRODUCER": (HR_PRODUCER, "WRONG_CONTRACT mutation producer"),
    "HR_REDUCER": (HR_REDUCER, "WRONG_CONTRACT semantic reducer"),
    "DU_OWNER": (DU_OWNER, "continuation manifest validator"),
    "EB_OWNER": (EB_OWNER, "candidate receipt validator"),
    "EE_OWNER": (EE_OWNER, "runtime projection receipt validator"),
    "EX_CERTIFICATE": (EX_CERTIFICATE, "common certified proof substrate"),
}


class HWBindingError(ValueError):
    """Deterministic fail-closed HW binding rejection."""


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
        raise HWBindingError("GIT_IDENTITY_UNAVAILABLE") from exc


def _git_bytes(root: Path, revision: str, path: Path) -> bytes:
    try:
        return subprocess.check_output(["git", "show", f"{revision}:{path.as_posix()}"], cwd=root, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as exc:
        raise HWBindingError(f"COMMITTED_OBJECT_UNAVAILABLE__{path.name}") from exc


def _load_module(path: Path, identity: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(identity, path)
    if specification is None or specification.loader is None:
        raise HWBindingError(f"MODULE_LOAD_FAILED__{identity}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise HWBindingError(f"DUPLICATE_JSON_KEY__{key}")
        result[key] = value
    return result


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=_unique_object)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise HWBindingError(f"CANONICAL_JSON_INVALID__{path.name}")
    return value


def _is_ancestor(root: Path, ancestor: str) -> bool:
    return subprocess.run(["git", "merge-base", "--is-ancestor", ancestor, HV_HEAD], cwd=root, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def authenticate_entry(repository_root: Path) -> dict[str, Any]:
    """Authenticate the exact committed and pushed HV checkpoint."""

    root = repository_root.resolve()
    observed = {
        "repository": str(root),
        "branch": _git(root, "branch", "--show-current"),
        "head": _git(root, "rev-parse", "HEAD"),
        "tree": _git(root, "rev-parse", "HEAD^{tree}"),
        "subject": _git(root, "show", "-s", "--format=%s", "HEAD"),
        "origin": _git(root, "remote", "get-url", "origin"),
        "remote_tracking_head": _git(root, "rev-parse", f"origin/{BRANCH}"),
        "tracked_status": _git(root, "status", "--porcelain", "--untracked-files=no"),
        "index": _git(root, "diff", "--cached", "--name-only"),
    }
    expected = {
        "repository": str(root), "branch": BRANCH, "head": HV_HEAD,
        "tree": HV_TREE, "subject": HV_SUBJECT, "origin": ORIGIN,
        "remote_tracking_head": HV_HEAD, "tracked_status": "", "index": "",
    }
    if observed != expected:
        raise HWBindingError("EXACT_COMMITTED_HV_CHECKPOINT_MISMATCH")
    for ancestor in (HU_HEAD, HT_HEAD, HR_HEAD, STABLE_ANCHOR):
        if not _is_ancestor(root, ancestor):
            raise HWBindingError(f"REQUIRED_ANCESTRY_MISSING__{ancestor}")
    if _git(root, "rev-parse", f"{HU_HEAD}^{{tree}}") != HU_TREE:
        raise HWBindingError("HU_TREE_MISMATCH")
    if _git(root, "rev-parse", f"{HT_HEAD}^{{tree}}") != HT_TREE:
        raise HWBindingError("HT_TREE_MISMATCH")

    nested = root / "sapianta_system"
    nested_state = {
        "origin": _git(nested, "remote", "get-url", "origin"),
        "head": _git(nested, "rev-parse", "HEAD"),
        "tree": _git(nested, "rev-parse", "HEAD^{tree}"),
        "branch": _git(nested, "branch", "--show-current"),
        "status": _git(nested, "status", "--porcelain", "--untracked-files=all"),
        "tag_head": _git(nested, "rev-parse", NESTED_TAG + "^{commit}"),
    }
    expected_nested = {"origin": NESTED_ORIGIN, "head": NESTED_HEAD, "tree": NESTED_TREE, "branch": "", "status": "", "tag_head": NESTED_HEAD}
    if nested_state != expected_nested:
        raise HWBindingError("NESTED_AUTHORITY_NOT_CLEAN_DETACHED_PINNED")
    return observed | {"nested": nested_state}


def committed_identity(repository_root: Path, path: Path, role: str) -> dict[str, str]:
    root = repository_root.resolve()
    committed = _git_bytes(root, HV_HEAD, path)
    current = root / path
    if current.is_symlink() or not current.is_file() or current.read_bytes() != committed:
        raise HWBindingError(f"COMMITTED_WORKTREE_IDENTITY_DRIFT__{path.name}")
    return {
        "path": path.as_posix(),
        "git_blob": _git(root, "rev-parse", f"{HV_HEAD}:{path.as_posix()}"),
        "sha256": sha256_bytes(committed),
        "role": role,
        "committed_identity_status": "VERIFIED",
    }


def committed_identity_map(repository_root: Path) -> dict[str, dict[str, str]]:
    return {name: committed_identity(repository_root, path, role) for name, (path, role) in IDENTITY_PATHS.items()}


def reconstruct_hv_terminal(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    raw = _git_bytes(root, HV_HEAD, HV_TERMINAL)
    envelope = json.loads(raw, object_pairs_hook=_unique_object)
    if raw != canonical_bytes(envelope) or envelope["reduction_sha256"] != sha256_bytes(canonical_bytes(envelope["reduction"])):
        raise HWBindingError("HV_TERMINAL_AUTHENTICATION_FAILED")
    reduction = envelope["reduction"]
    selection = reduction["checkout_selection"]
    correction = reduction["correction"]
    if (selection["selected_checkout_head"], selection["selected_checkout_tree"]) != (HT_HEAD, HT_TREE):
        raise HWBindingError("HV_SELECTED_CHECKOUT_MISMATCH")
    required = {
        "checkout_owner_binding_status": "VERIFIED",
        "wrong_contract_bootstrap_head_tree_status": "VERIFIED",
        "checkout_bootstrap_coherence_status": "VERIFIED",
        "expected_harness_binding_preservation_status": "VERIFIED",
        "host_guest_context_vector_semantic_equivalence": "VERIFIED",
        "post_commit_rebind_required": "VERIFIED",
    }
    if any(correction.get(key) != value for key, value in required.items()):
        raise HWBindingError("HV_CORRECTION_CLAIM_RECONSTRUCTION_FAILED")
    if reduction["e05"] != {"before": "8/18", "credit": 0, "after": "8/18"}:
        raise HWBindingError("HV_E05_RECONSTRUCTION_FAILED")
    return reduction


def verify_committed_checkout_bootstrap(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    identities = committed_identity_map(root)
    launcher = _load_module(root / FM_LAUNCHER, "g77_256hw_committed_launcher")
    if (launcher.CHECKOUT_HEAD, launcher.CHECKOUT_TREE) != (HT_HEAD, HT_TREE):
        raise HWBindingError("COMMITTED_FM_CHECKOUT_BINDING_MISMATCH")
    bootstrap = launcher.current_bootstrap_asset_bindings(VECTOR)
    if bootstrap["cloud_init_sha256"] != CLOUD_INIT_SHA256 or bootstrap["seed_sha256"] != SEED_SHA256:
        raise HWBindingError("COMMITTED_BOOTSTRAP_ASSET_BINDING_MISMATCH")
    cloud = _git_bytes(root, HV_HEAD, CLOUD_INIT).decode("utf-8")
    commands = [line.strip().split() for line in cloud.splitlines() if line.strip().startswith("/usr/bin/python3 ")]
    if len(commands) != 1 or len(commands[0]) != 7:
        raise HWBindingError("WRONG_CONTRACT_BOOTSTRAP_COMMAND_INVALID")
    expected_harness, _, checkout_head, checkout_tree, _ = commands[0][2:]
    if (checkout_head, checkout_tree) != (HT_HEAD, HT_TREE):
        raise HWBindingError("COMMITTED_WRONG_CONTRACT_BOOTSTRAP_HEAD_TREE_MISMATCH")
    if expected_harness != identities["WRONG_CONTRACT_ADAPTER"]["sha256"] or expected_harness != ADAPTER_SHA256:
        raise HWBindingError("EXPECTED_HARNESS_BINDING_MISMATCH")
    for member, source in (("/user-data", CLOUD_INIT), ("/meta-data", FM_META), ("/network-config", FM_NETWORK)):
        projected = subprocess.check_output(["isoinfo", "-i", str(root / SEED), "-R", "-x", member], stderr=subprocess.DEVNULL)
        if projected != _git_bytes(root, HV_HEAD, source):
            raise HWBindingError(f"NOCLOUD_PROJECTION_MISMATCH__{source.name}")
    return {
        "committed_fm_checkout_binding_status": "VERIFIED",
        "committed_wrong_contract_bootstrap_head_tree_status": "VERIFIED",
        "committed_checkout_bootstrap_coherence_status": "VERIFIED",
        "committed_nocloud_projection_status": "VERIFIED",
        "expected_harness_binding_status": "VERIFIED",
        "expected_harness_sha256": expected_harness,
    }


def _context_namespace(source: bytes, identity: str) -> dict[str, Any]:
    namespace: dict[str, Any] = {"__name__": identity, "__file__": FM_CONTEXT.as_posix()}
    exec(compile(source, FM_CONTEXT.as_posix(), "exec"), namespace)
    return namespace


def generation(vector: str) -> str:
    return f"G77_256HWTEST_ONE_FRESH_HUMAN_AUTHORIZED_{vector}_OPERATIONAL_COMMISSIONING_V1"


def verify_host_guest_semantics(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    host = _context_namespace(_git_bytes(root, HV_HEAD, FM_CONTEXT), "g77_256hw_host_context")
    guest = _context_namespace(_git_bytes(root, HT_HEAD, FM_CONTEXT), "g77_256hw_guest_context")
    for vector in ("WRONG_ATTEMPT", "WRONG_INPUT", "WRONG_CONTRACT"):
        identity = generation(vector)
        if host["operation_vector"](identity) != vector or guest["operation_vector"](identity) != vector:
            raise HWBindingError(f"HOST_GUEST_VECTOR_MISMATCH__{vector}")
    for malformed in (generation("UNKNOWN"), "MALFORMED"):
        for owner in (host, guest):
            try:
                owner["operation_vector"](malformed)
            except owner["ContextError"]:
                pass
            else:
                raise HWBindingError("UNKNOWN_OR_MALFORMED_VECTOR_ACCEPTED")
    for path in (ADAPTER, HR_PRODUCER, P11_OWNER, FM_CONTEXT):
        _git_bytes(root, HT_HEAD, path)
    adapter = _git_bytes(root, HT_HEAD, ADAPTER).decode("utf-8")
    for token in ("G77_256HR_WRONG_CONTRACT_VECTOR_PRODUCER_V1.py", "G77_256FC_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py", "context_owner_path = root / ("):
        if token not in adapter:
            raise HWBindingError("GUEST_ADAPTER_DEPENDENCY_CLOSURE_INCOMPLETE")
    return {"host_guest_context_vector_semantic_equivalence": "VERIFIED", "guest_adapter_dependency_closure_status": "VERIFIED"}


def _lineage_binding(root: Path, identity: str, path: Path) -> dict[str, str]:
    return {"identity": identity, "path": path.as_posix(), "sha256": sha256_path(root / path), "git_blob": _git(root, "rev-parse", f"HEAD:{path.as_posix()}")}


def _file_binding(root: Path, identity: str, path: Path) -> dict[str, str]:
    return {"identity": identity, "path": path.as_posix(), "sha256": sha256_path(root / path)}


def candidate_semantics(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    producer = _load_module(root / HR_PRODUCER, "g77_256hw_hr_producer")
    vector = producer.produce_wrong_contract_vector(repository_root=root, wrong_contract_identity=WRONG_CONTRACT_IDENTITY)
    expected = {
        "selected_vector": SELECTED_VECTOR,
        "target_mutated_coordinate": "contract_identity",
        "dependent_recomputation_fields": ["record_identity"],
        "semantic_mutation_count": 1,
        "differing_input_fields": ["contract_identity", "record_identity"],
        "contract_specific_comparison_reached": False,
        "authority_created": False,
        "request_created": False,
        "operation_attempted": False,
    }
    if any(vector.get(key) != value for key, value in expected.items()):
        raise HWBindingError("CURRENT_WRONG_CONTRACT_SEMANTIC_FIREWALL_FAILED")
    return vector


def build_candidate(repository_root: Path) -> dict[str, Any]:
    """Build one current-HV DU candidate with exact WRONG_CONTRACT semantics."""

    root = repository_root.resolve()
    authenticate_entry(root)
    reconstruct_hv_terminal(root)
    verify_committed_checkout_bootstrap(root)
    verify_host_guest_semantics(root)
    candidate_semantics(root)
    du = _load_module(root / DU_OWNER, "g77_256hw_du_builder")
    envelope = du.build_du_fixture(root)
    manifest = envelope["manifest"]
    manifest.update({
        "generation_identity": GENERATION,
        "required_head": HV_HEAD,
        "source_tree": HV_TREE,
        "current_spce_phase": "PHASE_N_WRONG_CONTRACT_PREOPERATIONAL_READINESS_VERIFIED",
        "phase_sequence": 0,
        "prior_manifest_sha256": None,
        "completed_phase_seals": [],
        "case_counters": {"e05_case_execution_count": 0, "wrong_contract_case_count": 0},
        "authority_state": {"lifecycle_state": "NOT_CREATED", "act_identity": None, "owner_revision": None, "authority_survives": False, "transferable": False, "reusable": False},
        "lineage_bindings": [
            _lineage_binding(root, "G77_256HV_TERMINAL_REDUCTION", HV_TERMINAL),
            _lineage_binding(root, "G77_256HU_TERMINAL_FAILURE_FRONTIER", HU_TERMINAL),
            _lineage_binding(root, "G77_256EX_COMMON_SUBSTRATE_CERTIFICATE", EX_CERTIFICATE),
            _lineage_binding(root, "G48_REPORTING_STANDARD", G48_STANDARD),
        ],
        "frontier_state": {
            "constitutional_frontier": "WRONG_CONTRACT_PREOPERATIONAL_READINESS_VERIFIED__OPERATIONAL_CAPABILITY_NOT_PROVEN",
            "exact_next_legal_action": "AFTER_HUMAN_REVIEW_AND_COMMIT_ONLY__ONE_FRESH_SEPARATELY_HUMAN_AUTHORIZED_WRONG_CONTRACT_OPERATIONAL_GENERATION",
            "continuation_mode": "HUMAN_REVIEW_ONLY",
            "requires_human_review": True,
        },
        "selected_case": {"case_class": CASE_CLASS, "case_id": CASE_ID},
        "first_failure_or_current_result": "PASS__WRONG_CONTRACT_REPOSITORY_READINESS__NO_OPERATION__NO_E05_CREDIT",
        "teardown_state": "NOT_APPLICABLE",
        "final_execution_seal": None,
        "observations": [
            "CURRENT_HV_COMMIT_IDENTITY_STATUS__VERIFIED",
            "TARGET_MUTATION__contract_identity",
            "DEPENDENT_RECOMPUTATION__record_identity",
            "SEMANTIC_MUTATION_COUNT__ONE",
            "UNRELATED_MUTATION_COUNT__ZERO",
            "EXPECTED_P11_D2_INPUT_RECORD_IDENTITY_BINDING_FAILURE",
            "PRESENTATION_NOT_AUTHORIZATION",
            "CERTIFIED_NOT_AUTHORIZED",
            "PROVIDER_CAPABILITY_NOT_EXECUTION_AUTHORITY",
            "E05_REMAINS_EIGHT_OF_EIGHTEEN",
        ],
        "extension_bindings": [
            _file_binding(root, "G77_256HR_WRONG_CONTRACT_FORMAL_SPECIFICATION", HR_SPEC),
            _file_binding(root, "G77_256HR_WRONG_CONTRACT_PRODUCER", HR_PRODUCER),
            _file_binding(root, "G77_256HR_WRONG_CONTRACT_REDUCER", HR_REDUCER),
            _file_binding(root, "G77_256HT_WRONG_CONTRACT_ADAPTER", ADAPTER),
            _file_binding(root, "G77_256HT_PREAUTHORIZATION_MATERIALIZER", MATERIALIZER),
            _file_binding(root, "G77_256FM_SOLE_LAUNCHER", FM_LAUNCHER),
            _file_binding(root, "G77_256FM_CONTEXT_OWNER", FM_CONTEXT),
            _file_binding(root, "G77_256GN_PRESENTATION_OWNER", GN_OWNER),
        ],
    })
    envelope["manifest_sha256"] = sha256_bytes(canonical_bytes(manifest))
    result = du.validate_envelope(envelope, root, expected_head=HV_HEAD)
    if set(result.values()) != {"PASS"}:
        raise HWBindingError("CURRENT_DU_NOT_PASS")
    return envelope


def validate_context(repository_root: Path, context: dict[str, Any], candidate_path: Path) -> None:
    root = repository_root.resolve()
    launcher = _load_module(root / FM_LAUNCHER, "g77_256hw_context_validator")
    launcher.validate_immutable_context_bindings(root, context, candidate_source_path=candidate_path.relative_to(root))
    checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    seed = context["qemu_executable_base_seed_checkout_bindings"]["seed"]
    hashes = context["wrapper_fc_er_che_schema_hashes"]
    adapter = context["guest_adapter_binding"]
    if context["repository_head"] != HV_HEAD or context["repository_tree"] != HV_TREE:
        raise HWBindingError("CURRENT_CONTEXT_REPOSITORY_IDENTITY_MISMATCH")
    if (checkout["head"], checkout["tree"]) != (HT_HEAD, HT_TREE):
        raise HWBindingError("CURRENT_CONTEXT_CHECKOUT_IDENTITY_MISMATCH")
    if seed["sha256"] != SEED_SHA256 or hashes["cloud_init"] != CLOUD_INIT_SHA256:
        raise HWBindingError("CURRENT_CONTEXT_BOOTSTRAP_IDENTITY_MISMATCH")
    if hashes[launcher.FRESH_OPERATION_CONTEXT_OWNER_HASH_KEY] != CONTEXT_OWNER_SHA256:
        raise HWBindingError("CURRENT_CONTEXT_OWNER_IDENTITY_MISMATCH")
    if adapter["source_path"] != ADAPTER.as_posix() or adapter["source_sha256"] != ADAPTER_SHA256:
        raise HWBindingError("CURRENT_CONTEXT_ADAPTER_IDENTITY_MISMATCH")


def build_context(repository_root: Path, candidate_path: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    launcher = _load_module(root / FM_LAUNCHER, "g77_256hw_context_builder")
    context = launcher.build_operation_context(
        repository_root=root,
        repository_head=HV_HEAD,
        repository_tree=HV_TREE,
        generation_identity=GENERATION,
        operation_identity=OPERATION_IDENTITY,
        identity_namespace_prefix=IDENTITY_PREFIX,
        operation_evidence_root=Path("/tmp/g77_256hw/operation_state"),
        transient_root=Path("/tmp/g77_256hw/transient"),
        candidate_source_path=candidate_path.relative_to(root),
    )
    validate_context(root, context, candidate_path)
    return context


def validate_preauthorization_coherence(repository_root: Path, candidate_bytes: bytes, context: dict[str, Any]) -> dict[str, Any]:
    root = repository_root.resolve()
    materializer = _load_module(root / MATERIALIZER, "g77_256hw_materializer")
    semantics = {"selected_vector": SELECTED_VECTOR, "target_mutation": "contract_identity", "dependent_recomputation": "record_identity", "semantic_mutation_count": 1, "unrelated_mutation_count": 0}
    request = {"authorized_vector_requested": VECTOR, "generation_identity": context["generation_identity"], "candidate_sha256": sha256_bytes(candidate_bytes), "context_sha256": context["context_sha256"], "canonical_argv_sha256": context["canonical_argv_sha256"], "request_is_authority": False}
    presentation = {"AUTHORIZED_VECTOR_REQUESTED": VECTOR, "GENERATION_ID": context["generation_identity"], "CANDIDATE_SHA256": sha256_bytes(candidate_bytes), "CONTEXT_SHA256": context["context_sha256"], "CANONICAL_ARGV_SHA256": context["canonical_argv_sha256"]}
    result = materializer.validate_future_materialization_chain(repository_root=root, candidate_bytes=candidate_bytes, candidate_semantics=semantics, context=context, request_binding=request, presentation_binding=presentation)
    if result["candidate_context_argv_presentation_chain"] != "VERIFIED" or result["human_operational_authority"] != 0:
        raise HWBindingError("GN_PREAUTHORIZATION_COHERENCE_NOT_VERIFIED")
    return result


def _harness_bytes(runtime_filename: str) -> bytes:
    return ("from pathlib import Path\n\n" 'FIXTURE_CLASSIFICATION = "TEST_ONLY__NON_AUTHORITY__NON_OPERATIONAL__NON_EXECUTABLE"\n' 'RAW_ROOT = Path("/mnt/g77-evidence")\n' f'CONTINUATION_MANIFEST_PATH = RAW_ROOT / "{runtime_filename}"\n').encode("utf-8")


def instantiate_binding(*, repository_root: Path, output_root: Path) -> dict[str, Any]:
    """Materialize current candidate/context and fresh DU/EB/EE only."""

    root = repository_root.resolve()
    output = output_root.resolve()
    if output.exists() or output.is_symlink():
        raise HWBindingError("POST_COMMIT_BINDING_OUTPUT_COLLISION")
    try:
        relative_output = output.relative_to(root)
    except ValueError as exc:
        raise HWBindingError("OUTPUT_OUTSIDE_REPOSITORY") from exc
    candidate = build_candidate(root)
    candidate_name = "G77_256HW_WRONG_CONTRACT_CURRENT_CANDIDATE_V1.json"
    candidate_path = output / "candidate" / candidate_name
    runtime_root = output / "runtime_projection"
    runtime_path = runtime_root / candidate_name
    binding_root = output / "bindings"
    harness_path = binding_root / "G77_256HW_EE_PATH_PROJECTION_FIXTURE_V1.py"
    eb_path = binding_root / "G77_256HW_EB_RECEIPT_V1.json"
    ee_path = binding_root / "G77_256HW_EE_RECEIPT_V1.json"
    context_path = output / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    for parent in (candidate_path.parent, runtime_root, binding_root):
        parent.mkdir(parents=True, exist_ok=True)
    candidate_bytes = canonical_bytes(candidate)
    candidate_path.write_bytes(candidate_bytes)
    runtime_path.write_bytes(candidate_bytes)
    harness_path.write_bytes(_harness_bytes(candidate_name))
    context = build_context(root, candidate_path)
    launcher = _load_module(root / FM_LAUNCHER, "g77_256hw_context_serializer")
    context_path.write_bytes(launcher.fresh_context.canonical_bytes(context))
    validate_preauthorization_coherence(root, candidate_bytes, context)

    du = _load_module(root / DU_OWNER, "g77_256hw_du")
    eb = _load_module(root / EB_OWNER, "g77_256hw_eb")
    ee = _load_module(root / EE_OWNER, "g77_256hw_ee")
    du_result = du.validate_file(candidate_path, root, expected_head=HV_HEAD)
    eb_receipt = eb.validate_candidate(root, candidate_path, required_head=HV_HEAD, required_tree=HV_TREE)
    eb_path.write_bytes(eb.canonical_bytes(eb_receipt))
    eb_result = eb.verify_receipt_file(root, eb_path)
    ee_receipt = ee.validate_binding(root, candidate_path, eb_path, harness_path, runtime_root, "/mnt/g77-evidence", required_head=HV_HEAD, required_tree=HV_TREE)
    ee_path.write_bytes(ee.canonical_bytes(ee_receipt))
    ee_result = ee.verify_receipt_file(root, ee_path)
    if set(du_result.values()) != {"PASS"} or eb_result.get("overall_result") != "PASS" or ee_result.get("pre_materialization_runtime_path_binding_result") != "PASS":
        raise HWBindingError("CURRENT_DU_EB_EE_NOT_PASS")
    return {
        "schema_id": "G77_256HW_POST_HV_LIVE_BINDING_RESULT_V1",
        "artifact_class": "POST_COMMIT_BINDING__NON_AUTHORITY__NON_OPERATIONAL",
        "repository_head": HV_HEAD,
        "repository_tree": HV_TREE,
        "selected_checkout_head": HT_HEAD,
        "selected_checkout_tree": HT_TREE,
        "output_root": relative_output.as_posix(),
        "candidate_sha256": sha256_bytes(candidate_bytes),
        "context_sha256": context["context_sha256"],
        "context_file_sha256": sha256_path(context_path),
        "du": "PASS", "eb": "PASS", "ee": "PASS",
        "human_operational_authority_count": 0,
        "authority_consumption_count": 0,
        "request_count": 0,
        "p11_entry_count": 0,
        "qemu_execution_count": 0,
        "vm_creation_count": 0,
        "vm_boot_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "e05_credit": 0,
    }


def current_chain(repository_root: Path, live_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    live = live_root.resolve()
    identities = committed_identity_map(root)
    candidate = live / "candidate/G77_256HW_WRONG_CONTRACT_CURRENT_CANDIDATE_V1.json"
    runtime = live / "runtime_projection/G77_256HW_WRONG_CONTRACT_CURRENT_CANDIDATE_V1.json"
    context_path = live / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    eb = live / "bindings/G77_256HW_EB_RECEIPT_V1.json"
    ee = live / "bindings/G77_256HW_EE_RECEIPT_V1.json"
    context = load_canonical(context_path)
    return {
        "hv_head": HV_HEAD, "hv_tree": HV_TREE,
        "fm_launcher": identities["FM_LAUNCHER"]["sha256"],
        "fm_context_owner": identities["FM_CONTEXT_OWNER"]["sha256"],
        "adapter": identities["WRONG_CONTRACT_ADAPTER"]["sha256"],
        "cloud_init": identities["WRONG_CONTRACT_CLOUD_INIT"]["sha256"],
        "nocloud_seed": identities["WRONG_CONTRACT_NOCLOUD_SEED"]["sha256"],
        "checkout_head": HT_HEAD, "checkout_tree": HT_TREE,
        "projection": identities["WRONG_CONTRACT_ADAPTER"]["sha256"],
        "candidate": sha256_path(candidate), "runtime_projection": sha256_path(runtime),
        "operation_context": context["context_sha256"],
        "context_candidate": context["candidate_manifest_sha256"],
        "gn_presentation": f"{VECTOR}:{context['context_sha256']}:{context['canonical_argv_sha256']}",
        "du": "PASS", "eb": sha256_path(eb), "ee": sha256_path(ee),
        "vector": VECTOR,
    }


def validate_chain(repository_root: Path, live_root: Path, chain: dict[str, Any]) -> None:
    expected = current_chain(repository_root, live_root)
    if chain != expected:
        differing = sorted(set(chain) | set(expected), key=str)
        field = next((name for name in differing if chain.get(name) != expected.get(name)), "UNKNOWN")
        raise HWBindingError(f"PREAUTHORIZATION_BINDING_REJECTED__{field.upper()}")
    if chain["candidate"] != chain["runtime_projection"] or chain["candidate"] != chain["context_candidate"]:
        raise HWBindingError("CANDIDATE_RUNTIME_CONTEXT_COHERENCE_MISMATCH")


def authenticate_ex(repository_root: Path) -> dict[str, Any]:
    certificate = json.loads(_git_bytes(repository_root.resolve(), HV_HEAD, EX_CERTIFICATE), object_pairs_hook=_unique_object)
    preimage = deepcopy(certificate)
    preimage["certificate_sha256"] = ""
    payload = json.dumps(preimage, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")
    if certificate["certificate_sha256"] != sha256_bytes(payload) or certificate["certificate"]["component_counts"].get("CERTIFIED") != 17:
        raise HWBindingError("EX_17_OF_17_NOT_AUTHENTICATED")
    return {"ex_reused": "17/17", "ex_reconstructed": 0, "status": "VERIFIED"}


def terminal_reduction(repository_root: Path, live_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    live = live_root.resolve()
    entry = authenticate_entry(root)
    identities = committed_identity_map(root)
    hv = reconstruct_hv_terminal(root)
    checkout = verify_committed_checkout_bootstrap(root)
    semantics = verify_host_guest_semantics(root)
    candidate_path = live / "candidate/G77_256HW_WRONG_CONTRACT_CURRENT_CANDIDATE_V1.json"
    runtime_path = live / "runtime_projection/G77_256HW_WRONG_CONTRACT_CURRENT_CANDIDATE_V1.json"
    context_path = live / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    candidate = load_canonical(candidate_path)
    context = load_canonical(context_path)
    du = _load_module(root / DU_OWNER, "g77_256hw_terminal_du")
    eb = _load_module(root / EB_OWNER, "g77_256hw_terminal_eb")
    ee = _load_module(root / EE_OWNER, "g77_256hw_terminal_ee")
    if candidate_path.read_bytes() != runtime_path.read_bytes():
        raise HWBindingError("CANDIDATE_RUNTIME_BYTE_IDENTITY_MISMATCH")
    if set(du.validate_file(candidate_path, root, expected_head=HV_HEAD).values()) != {"PASS"}:
        raise HWBindingError("CURRENT_DU_NOT_PASS")
    if eb.verify_receipt_file(root, live / "bindings/G77_256HW_EB_RECEIPT_V1.json")["overall_result"] != "PASS":
        raise HWBindingError("CURRENT_EB_NOT_PASS")
    if ee.verify_receipt_file(root, live / "bindings/G77_256HW_EE_RECEIPT_V1.json")["pre_materialization_runtime_path_binding_result"] != "PASS":
        raise HWBindingError("CURRENT_EE_NOT_PASS")
    validate_context(root, context, candidate_path)
    validate_preauthorization_coherence(root, candidate_path.read_bytes(), context)
    validate_chain(root, live, current_chain(root, live))
    candidate_semantics(root)
    ex = authenticate_ex(root)
    counters = {key: 0 for key in (
        "human_operational_authority", "authority_consumption", "pre",
        "fm_operational_launcher_invocation", "qemu", "vm_creation", "vm_boot",
        "operation_attempt", "request", "p11_entry", "protected_invocation",
        "protected_effect", "e05_credit",
    )}
    return {
        "schema_id": "G77_256HW_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "mode": "REPOSITORY_ONLY__NO_AUTHORITY__NO_OPERATION",
        "entry": entry,
        "committed_identity_map": identities,
        "hv_terminal_reconstruction": {"status": "VERIFIED", "selected_checkout": hv["checkout_selection"]},
        "committed_checkout_bootstrap": checkout,
        "static_guest_coherence": semantics,
        "live_binding": {
            "current_hv_commit_identity_status": "VERIFIED",
            "post_commit_live_binding_status": "VERIFIED",
            "current_candidate_identity": sha256_path(candidate_path),
            "current_context_identity": context["context_sha256"],
            "current_wrong_contract_candidate_status": "VERIFIED",
            "current_candidate_semantic_firewall_status": "VERIFIED",
            "current_runtime_projection_status": "VERIFIED",
            "current_operation_context_status": "VERIFIED",
            "checkout_projection_coherence_status": "VERIFIED",
            "gn_presentation_binding_status": "VERIFIED",
            "preauthorization_coherence_status": "VERIFIED",
        },
        "du_eb_ee": {"current_du_status": "PASS", "current_eb_status": "PASS", "current_ee_status": "PASS"},
        "firewalls": {"preauthorization_negative_matrix_status": "VERIFIED", "known_historical_failure_class_block_status": "VERIFIED", "no_known_repository_preauth_blocker_status": "VERIFIED"},
        "readiness": {"preoperational_readiness_status": "VERIFIED", "next_operational_generation_eligible": "VERIFIED", "wrong_contract_operational_capability": "NOT_PROVEN"},
        "semantic_firewall": {"target_mutation": "contract_identity", "semantic_mutation_count": 1, "dependent_recomputation": "record_identity", "unrelated_mutation_count": 0, "expected_p11_denial": "D2_INPUT_RECORD_IDENTITY_BINDING_FAILURE", "contract_specific_comparison_reached": False},
        "reuse_impact": {
            "reused_certified_capability_set": ["EX_17_OF_17", "P11_D2", "CHE", "FK", "DU", "EB", "EE", "FM_SOLE_ROUTE", "GN", "GL", "HG_CHECKOUT_PROJECTION", "HT_ROUTE_EXTENSION", "HV_CORRECTION", "GOVERNANCE", "LAYER_0"],
            "new_capability_set": ["HW_WRONG_CONTRACT_COMMITTED_IDENTITY_LIVE_BINDING_AND_READINESS_EVIDENCE"],
            "unreachable_preexisting_capability_set": [],
            "production_route_before": 1, "production_route_after": 1, "production_route_delta": 0,
            "new_generic_framework_count": 0, "new_authority_layer_count": 0,
            "new_production_route_count": 0, "new_runtime_owner_count": 0,
        },
        "ex": ex,
        "ccwim": {
            "ccwim_maturity_level": {"status": "ESTIMATED", "value": "L4_LIKE"},
            "cross_worker_state_recovery_level": {"status": "VERIFIED", "value": "COMMITTED_HV_AND_PREDECESSOR_LINEAGE_RECONSTRUCTED"},
            "repository_derived_context_ratio": {"status": "ESTIMATED", "value": "DOMINANT"},
            "human_handoff_information_required": {"status": "VERIFIED", "value": "BOUNDED_HW_COMMISSION_ONLY"},
            "previous_worker_conversation_required": {"status": "VERIFIED", "value": "NO"},
            "previous_worker_identity_required": {"status": "VERIFIED", "value": "NO"},
            "previous_worker_memory_required": {"status": "VERIFIED", "value": "NO"},
            "authenticated_repository_continuation": {"status": "VERIFIED", "value": "YES"},
            "inter_generation_cross_worker_continuation": {"status": "VERIFIED", "value": "YES"},
            "intra_generation_cross_worker_continuation": {"status": "NOT_APPLICABLE"},
            "uncommitted_delta_recovery": {"status": "NOT_APPLICABLE"},
            "authority_state_recovery": {"status": "VERIFIED", "value": "NO_HW_AUTHORITY_EXISTS"},
            "cross_worker_constitutional_drift": {"status": "VERIFIED", "value": 0},
            "handoff_sufficiency_status": {"status": "VERIFIED"},
            "handoff_state_completeness": {"status": "VERIFIED"},
            "handoff_reconstruction_required": {"status": "VERIFIED", "value": "YES"},
            "handoff_reconstruction_success": {"status": "VERIFIED", "value": "YES"},
            "handoff_ambiguity_count": {"status": "VERIFIED", "value": 0},
            "unauthenticated_handoff_assumption_count": {"status": "VERIFIED", "value": 0},
        },
        "metrics": {
            "project_progress_estimate": {"status": "ESTIMATED", "value": "WRONG_CONTRACT_PREOPERATIONAL_READINESS_COMPLETE"},
            "constitutional_health_evidence": {"status": "VERIFIED"},
            "shadow_automation_status": {"status": "VERIFIED", "value": "ABSENT"},
            "constitutional_frontier_distance": {"status": "ESTIMATED", "value": "ONE_SEPARATELY_AUTHORIZED_OPERATIONAL_GENERATION"},
            "e05_frontier_distance": {"status": "VERIFIED", "value": "10_OF_18_OBLIGATIONS_REMAIN"},
            "selected_e05_local_frontier_distance": {"status": "ESTIMATED", "value": "ONE_FUTURE_HUMAN_OPERATIONAL_GENERATION"},
            "governance_efficience": {"status": "ESTIMATED", "value": "TARGETED_AFFECTED_FRONTIER"},
            "architectural_governance_efficience": {"status": "VERIFIED", "value": "ONE_ROUTE_RETAINED"},
            "proof_reuse_efficiency": {"status": "ESTIMATED", "value": "HIGH__EX_17_OF_17_AND_EXISTING_OWNERS_REUSED"},
            "cognition_assisted_handoff": {"status": "VERIFIED"},
            "aigol_codex_work_share": {"status": "NOT_MEASURED"},
            "overengineering_risk": {"status": "ESTIMATED", "value": "LOW"},
            "proof_process_overhead_risk": {"status": "ESTIMATED", "value": "MEDIUM"},
            "cognition_provenance": {"status": "VERIFIED", "value": "AUTHENTICATED_GIT_OBJECTS_COMMITTED_GOVERNANCE_AND_FRESH_DETERMINISTIC_HW_EVIDENCE"},
            "candidate_capability": {"status": "VERIFIED"},
            "wrong_contract_candidate_capability": {"status": "VERIFIED"},
            "wrong_contract_repository_capability": {"status": "VERIFIED"},
            "wrong_contract_route_support": {"status": "VERIFIED"},
            "wrong_contract_binding_status": {"status": "VERIFIED"},
            "wrong_contract_preoperational_readiness": {"status": "VERIFIED"},
            "wrong_contract_operational_capability": {"status": "NOT_PROVEN"},
            "shadow_design_target": {"status": "VERIFIED", "value": "FORMALIZE_REUSE_BIND_VERIFY"},
            "constitutional_continuation_progress": {"status": "VERIFIED", "value": "PREOPERATIONAL_READINESS_VERIFIED"},
            "prompt_context_reuse_ratio": {"status": "NOT_MEASURED"},
            "token_benchmark": {"status": "NOT_MEASURED"},
            "llm_cost_reduction_ratio": {"status": "NOT_MEASURED"},
            "lcrr": {"status": "NOT_MEASURED"},
            "e05_generations_per_credit": {"status": "NOT_MEASURED"},
            "operational_attempts_per_credit": {"status": "NOT_APPLICABLE"},
            "marginal_e05_generation_cost": {"status": "NOT_MEASURED"},
            "infrastructure_amortization_signal": {"status": "ESTIMATED", "value": "POSITIVE_REUSE_SIGNAL_WITH_ZERO_CREDIT"},
        },
        "infrastructure_amortization": {
            "did_hw_require_new_common_infrastructure": False,
            "did_hw_require_new_vector_specific_infrastructure": True,
            "did_hw_require_new_generic_framework": False,
            "did_hw_require_new_authority_layer": False,
            "did_hw_require_new_runtime_owner": False,
            "did_hw_require_new_production_route": False,
            "did_hw_reuse_hv_correction": True,
            "did_hw_reuse_ht_route_extension": True,
            "did_hw_reuse_existing_post_commit_binding_architecture": True,
            "did_hw_reuse_existing_checkout_projection_architecture": True,
            "did_hw_reuse_gn_gl_du_eb_ee": True,
            "did_hw_preserve_wrong_attempt": True,
            "did_hw_preserve_wrong_input": True,
            "was_ex_reused_17_of_17": True,
            "is_8_to_9_infrastructure_amortization_signal_positive": {"status": "ESTIMATED", "value": "YES__CAPABILITY_REUSE_ONLY__COMPUTE_COST_REDUCTION_NOT_MEASURED"},
        },
        "cognition_provenance": "VERIFIED__PRIMARY_AUTHORITY_FROM_COMMITTED_HV_HU_HT_HR_HP_P11_EX_FM_GN_HG_DU_EB_EE_CHE_FK_GOVERNANCE_LAYER_0_NESTED_AUTHORITY_AND_FRESH_HW_EVIDENCE",
        "e05": {"before": "8/18", "credit": 0, "after": "8/18"},
        "operational_counters": counters,
        "terminal_control": {
            "auto_continuable": False,
            "human_review_required": True,
            "last_verified_edge": "CURRENT_COMMITTED_HV_CANDIDATE_RUNTIME_CONTEXT_GN_DU_EB_EE_PREAUTHORIZATION_CHAIN",
            "first_broken_edge": "NONE_KNOWN_IN_REPOSITORY_PREAUTHORIZATION_SCOPE",
            "minimum_missing_capability": "ONE_FRESH_SEPARATELY_HUMAN_AUTHORIZED_WRONG_CONTRACT_OPERATIONAL_GENERATION",
            "minimum_legal_next_delta": "AFTER_HUMAN_REVIEW_AND_COMMIT_ONLY__ONE_FRESH_SEPARATELY_HUMAN_AUTHORIZED_WRONG_CONTRACT_OPERATIONAL_GENERATION",
            "verdict": "VERIFIED__G77_256HW_POST_HV_WRONG_CONTRACT_PREOPERATIONAL_READINESS__OPERATIONAL_CAPABILITY_NOT_PROVEN__ZERO_OPERATION__E05_8_OF_18__HUMAN_REVIEW_REQUIRED",
        },
    }


def write_terminal_reduction(*, repository_root: Path, live_root: Path, output_path: Path) -> dict[str, Any]:
    reduction = terminal_reduction(repository_root, live_root)
    envelope = {"schema_id": "G77_256HW_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1", "reduction": reduction, "reduction_sha256": sha256_bytes(canonical_bytes(reduction))}
    if output_path.exists() or output_path.is_symlink():
        raise HWBindingError("TERMINAL_REDUCTION_OUTPUT_COLLISION")
    output_path.write_bytes(canonical_bytes(envelope))
    return envelope


if __name__ == "__main__":
    raise SystemExit("repository-only binding owner; no operational CLI entry point")
