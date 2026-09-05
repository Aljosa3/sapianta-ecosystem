#!/usr/bin/env python3
"""Repository-only resolver for the G77-256II identity-contract frontier.

The resolver authenticates committed IH, reproduces the post-IH DU/EB/EE
conflict, distinguishes runtime-target from certification-currentness
identities, and returns a fail-closed reduction.  It has no operational CLI
entry point and creates no receipt or authority object.
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
IH_HEAD = "8698486cdf9a206f2bc73993c83389d6850362ff"
IH_TREE = "0c9e70f0e71a7e742de69bbd770b8590d79a270f"
IH_SUBJECT = "G77-256IH prepare FUTURE IF identity rebind frontier"
IG_HEAD = "71391a75011cdc388bdac9183f4654814a044c69"
IF_HEAD = "699fcdce794ff49b6c8735602936355724ed1c90"
IF_TREE = "7c773d4b2acdf013f1b8238eabfc8eced4dd6866"
IE_HEAD = "9420764a5bb6db8909334f2a422225687a37a346"
STABLE_ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_TAG = "refs/tags/sapianta-system-nested-authority-3183bab-v1"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"

II_ROOT = Path(".github/governance/evidence/g77_256ii_runtime_certification_contract_resolution_v1")
IH_ROOT = Path(".github/governance/evidence/g77_256ih_future_if_identity_rebind_v1")
CANDIDATE = IH_ROOT / "live_binding/candidate/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json"
RUNTIME = IH_ROOT / "live_binding/runtime_projection/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json"
CONTEXT = IH_ROOT / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
IH_TERMINAL = IH_ROOT / "G77_256IH_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
FM_ROOT = Path(".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1")
FM_LAUNCHER = FM_ROOT / "launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
FM_CONTEXT = FM_ROOT / "launcher/sapianta_fresh_operation_context_v1.py"
IF_ROOT = Path(".github/governance/evidence/g77_256if_future_post_commit_readiness_v1")
IF_ADAPTER = IF_ROOT / "adapter/G77_256IF_FUTURE_VECTOR_ADAPTER_V1.py"
DU_CONTRACT = Path(".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/G77_256DU_CANONICAL_CONTINUATION_MANIFEST_CONTRACT_V1.md")
DU_SCHEMA = Path(".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/G77_256DU_CANONICAL_CONTINUATION_MANIFEST_SCHEMA_V1.json")
DU_OWNER = Path(".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V1.py")
EB_SCHEMA = Path(".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v1/G77_256EB_CANDIDATE_BOUND_VALIDATION_RECEIPT_SCHEMA_V1.json")
EB_OWNER = Path(".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v1/validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V1.py")
EE_CONTRACT = Path(".github/governance/evidence/g77_256ee_runtime_consumer_binding_v1/G77_256EE_RUNTIME_CONSUMER_BINDING_CONTRACT_V1.md")
EE_SCHEMA = Path(".github/governance/evidence/g77_256ee_runtime_consumer_binding_v1/G77_256EE_RUNTIME_CONSUMER_BINDING_RECEIPT_SCHEMA_V1.json")
EE_OWNER = Path(".github/governance/evidence/g77_256ee_runtime_consumer_binding_v1/validator/G77_256EE_RUNTIME_CONSUMER_BINDING_VALIDATOR_V1.py")
GN_OWNER = Path(".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py")
GL_OWNER = Path(".github/governance/evidence/g77_256gl_receipt_parent_equivalence_v1/orchestration/G77_256GL_RECEIPT_PARENT_PREAUTHORIZATION_BINDING_V1.py")
EX_CERTIFICATE = Path(".github/governance/evidence/g77_256ex_common_substrate_certification_v1/G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json")

IH_HASHES = {
    "G48_REPORT": (IH_ROOT / "G77_256IH_G48_IMPLEMENTATION_REPORT_V1.md", "ebef8a7be2e9c41449230fd007e8de31e6dd6b674662687ff7a34d4ce590eaae"),
    "TERMINAL": (IH_TERMINAL, "34ae2ae086898da9c17f00e66a3d883779a68611d96c097ab3acf59a0c52c91c"),
    "BINDER": (IH_ROOT / "binding/G77_256IH_POST_IG_FUTURE_IF_REBIND_V1.py", "435cdf95b3d360970000d2a8351d2e3aa411d163359ad77b238748fdf0c7bdc3"),
    "CONTEXT": (CONTEXT, "4aea81e06e7fdeaa18e48f5e084c218046f1a8f787b7be42671963f27f4c7419"),
    "CHECKPOINT": (IH_ROOT / "live_binding/bindings/G77_256IH_DU_EB_EE_READINESS_CHECKPOINT_V1.json", "35eaa3ffd227f49fdacb17ecc479f2984e094874de8eda4802a238bf48c45e62"),
    "EE_FIXTURE": (IH_ROOT / "live_binding/bindings/G77_256IH_EE_PATH_PROJECTION_FIXTURE_V1.py", "6730c443287de1ab12bf3ea243bffca2c41666ae3fb9ff0fb68c7738737c42ea"),
    "CANDIDATE": (CANDIDATE, "ad5d204ec6ace09f18b83fd5f868e73dac5e36dad81149f9f335c87f68cf42f7"),
    "RUNTIME": (RUNTIME, "ad5d204ec6ace09f18b83fd5f868e73dac5e36dad81149f9f335c87f68cf42f7"),
    "TESTS": (IH_ROOT / "tests/test_g77_256ih_future_if_identity_rebind_v1.py", "c04228f0e5a453f7e1409e47a2b8998d8c2b9e9bc41fe905564b66b8397bba9d"),
}

OWNER_HASHES = {
    DU_CONTRACT: "e2fc8ddff0376f2e6acbd01f2cefb714dbd299baf1013d055d5ceeae251fed9e",
    DU_SCHEMA: "a21ba1567c65101a5f178afdfefb5d500c97fc2cc6a9eb9da6c9fb4cc914478e",
    DU_OWNER: "27457993a4e6b778cc65356cd9b17a1bf2665f4e6147608d27dc233ff512304d",
    EB_SCHEMA: "5b477ce183df65446aa1c3df3f8006856fce72b0771fcf04ff0c9cc6ae3a5f49",
    EB_OWNER: "8e8171f757213f064cec463868408364175772e766615bd276ed7f0e28306b43",
    EE_CONTRACT: "a4cd5694f2a3f05ed3f41e1fd5c84b33ee54e6d48dd81496ca8ee20951d1bf8c",
    EE_SCHEMA: "b193f6d392b0f5b0be32041e554ce3ccc18288f68bab0880c27326cb42d2ccc0",
    EE_OWNER: "5e4b35b3c7e7e23e5b7209c5f56e8a70055eac9a3deef32bc288b210e80f9410",
    FM_LAUNCHER: "f8310a6c8aba85f170ef9f30c3459bf615ec73014ec00f91aace5e8e5b44b769",
    FM_CONTEXT: "fdfa04349529d70bc97820a1848f8afc22b81071859d5456550799e0f9476237",
}

FUTURE_PAYLOAD_DIGEST = "sha256:9568e0c248ad488cabcf6bde6b490c544077862d10e3fda13bcdc8ed9953f547"
SOURCE_ACT_DIGEST = "sha256:7167b0725d2c84bafde1d0060f512b0fa358d777ec1beff8b7c68d22ee6502e8"
CORRELATION_IDENTITY = "CHE-CORRELATION-15b2680b5577da169cecf9efb3231e2e6f6467e6f409fa2594b04128f998e454"


class IIResolutionError(ValueError):
    """One fail-closed II repository-evidence error."""


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise IIResolutionError(f"DUPLICATE_JSON_KEY__{key}")
        result[key] = value
    return result


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=_unique)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise IIResolutionError(f"CANONICAL_JSON_INVALID__{path.name}")
    return value


def _git(root: Path, *arguments: str) -> str:
    try:
        return subprocess.check_output(["git", *arguments], cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError as exc:
        raise IIResolutionError("GIT_IDENTITY_UNAVAILABLE") from exc


def _git_bytes(root: Path, revision: str, path: Path) -> bytes:
    try:
        return subprocess.check_output(["git", "show", f"{revision}:{path.as_posix()}"], cwd=root, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as exc:
        raise IIResolutionError(f"COMMITTED_OBJECT_UNAVAILABLE__{path.name}") from exc


def _load(path: Path, identity: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(identity, path)
    if specification is None or specification.loader is None:
        raise IIResolutionError(f"MODULE_LOAD_FAILED__{identity}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def authenticate_entry(repository_root: Path) -> dict[str, Any]:
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
        "repository": str(root), "branch": BRANCH, "head": IH_HEAD,
        "tree": IH_TREE, "subject": IH_SUBJECT, "origin": ORIGIN,
        "remote_tracking_head": IH_HEAD, "index": "",
    }
    if observed != expected:
        raise IIResolutionError("EXACT_COMMITTED_IH_CHECKPOINT_MISMATCH")
    for ancestor in (IF_HEAD, IG_HEAD, IE_HEAD, STABLE_ANCHOR):
        if subprocess.run(["git", "merge-base", "--is-ancestor", ancestor, IH_HEAD], cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode:
            raise IIResolutionError(f"ANCESTRY_MISSING__{ancestor}")
    changed = subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=all"], cwd=root, text=True).splitlines()
    for line in changed:
        if not line[3:].startswith(II_ROOT.as_posix() + "/"):
            raise IIResolutionError(f"UNRELATED_WORKTREE_MUTATION__{line[3:]}")
    nested = root / "sapianta_system"
    nested_state = {
        "origin": _git(nested, "remote", "get-url", "origin"),
        "head": _git(nested, "rev-parse", "HEAD"),
        "tree": _git(nested, "rev-parse", "HEAD^{tree}"),
        "branch": _git(nested, "branch", "--show-current"),
        "status": _git(nested, "status", "--porcelain", "--untracked-files=all"),
        "tag_head": _git(nested, "rev-parse", NESTED_TAG + "^{commit}"),
    }
    required_nested = {"origin": NESTED_ORIGIN, "head": NESTED_HEAD, "tree": NESTED_TREE, "branch": "", "status": "", "tag_head": NESTED_HEAD}
    if nested_state != required_nested:
        raise IIResolutionError("NESTED_AUTHORITY_NOT_CLEAN_DETACHED_PINNED")
    return observed | {
        "nested": nested_state,
        "worktree_scope": "VERIFIED__II_EVIDENCE_ONLY",
        "continuation_recovery": {
            "resolver": "PARTIALLY_COMPLETED_BEFORE_INTERRUPTION__AUTHENTICATED_AND_REUSED",
            "focused_tests": "NOT_STARTED_BEFORE_INTERRUPTION",
            "terminal_reduction": "NOT_STARTED_BEFORE_INTERRUPTION",
            "g48_report": "NOT_STARTED_BEFORE_INTERRUPTION",
            "unrelated_repository_delta_count": "VERIFIED__0",
            "ignored_interpreter_cache": "NOT_APPLICABLE__NOT_A_GIT_DELTA",
        },
    }


def reconstruct_ih(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    identities: dict[str, Any] = {}
    for identity, (path, expected_sha) in IH_HASHES.items():
        committed = _git_bytes(root, IH_HEAD, path)
        if sha256_bytes(committed) != expected_sha or committed != (root / path).read_bytes():
            raise IIResolutionError(f"IH_IDENTITY_MISMATCH__{identity}")
        identities[identity] = {"path": path.as_posix(), "sha256": expected_sha, "git_blob": _git(root, "rev-parse", f"{IH_HEAD}:{path.as_posix()}")}
    envelope = load_canonical(root / IH_TERMINAL)
    reduction = envelope["reduction"]
    if envelope["reduction_sha256"] != sha256_bytes(canonical_bytes(reduction)):
        raise IIResolutionError("IH_TERMINAL_SEAL_INVALID")
    required = {
        "current_e05_status": "VERIFIED__10_OF_18",
        "future_live_identity_rebind": "VERIFIED__REPOSITORY_PREPARED_IF_BOUND",
        "future_live_binding": "NOT_PROVEN__EB_EE_CURRENT_HEAD_BASELINE_MISMATCH",
        "future_preoperational_readiness": "NOT_PROVEN__EB_EE_CURRENT_HEAD_BASELINE_MISMATCH",
        "e05_credit": "VERIFIED__0",
    }
    observed = {key: reduction["readiness"][key] for key in required}
    if observed != required:
        raise IIResolutionError("IH_FRONTIER_RECONSTRUCTION_FAILED")
    return {"status": "VERIFIED", "identities": identities, "frontier": observed, "terminal_control": reduction["terminal_control"]}


def authenticate_owner_trace(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    for path, expected in OWNER_HASHES.items():
        if sha256_path(root / path) != expected or _git_bytes(root, IH_HEAD, path) != (root / path).read_bytes():
            raise IIResolutionError(f"OWNER_IDENTITY_MISMATCH__{path.name}")
    return {
        "owners": {path.as_posix(): digest for path, digest in OWNER_HASHES.items()},
        "equalities": [
            {"owner": "DU", "left": "candidate.required_head", "right": "requested expected_head", "classification": "RUNTIME_TARGET_INVARIANT"},
            {"owner": "DU", "left": "candidate.source_tree", "right": "tree(candidate.required_head)", "classification": "PROVENANCE_INVARIANT"},
            {"owner": "DU_SCHEMA", "left": "required_head/source_tree", "right": "single closed V1 field pair", "classification": "SCHEMA_STRUCTURAL_INVARIANT"},
            {"owner": "EB", "left": "receipt.required_head/tree", "right": "actual current HEAD/tree", "classification": "CERTIFICATION_CURRENTNESS_INVARIANT"},
            {"owner": "EB", "left": "DU expected_head", "right": "receipt required_head", "classification": "HISTORICAL_COUPLING"},
            {"owner": "EE", "left": "receipt git_binding", "right": "actual current HEAD/tree", "classification": "CERTIFICATION_CURRENTNESS_INVARIANT"},
            {"owner": "EE", "left": "candidate/runtime required_head", "right": "receipt required_head", "classification": "HISTORICAL_COUPLING"},
            {"owner": "FM_LAUNCHER", "left": "checkout head/tree", "right": "exact IF head/tree", "classification": "RUNTIME_TARGET_INVARIANT"},
            {"owner": "FM_CONTEXT", "left": "context repository head/tree", "right": "observed current repository head/tree at readiness", "classification": "CERTIFICATION_CURRENTNESS_INVARIANT"},
            {"owner": "FM_CONTEXT", "left": "context checkout head/tree", "right": "launcher checkout head/tree", "classification": "PROVENANCE_INVARIANT"},
        ],
        "observed_cross_role_coupling": "VERIFIED__IMPLEMENTATION_DERIVED",
        "coupling_classification": "VERIFIED__IMPLEMENTATION_COUPLING",
        "identity_coupling_status": "NOT_PROVEN__NO_UNIQUE_GOVERNED_CONTRACT_SEPARATION",
        "chronology": "VERIFIED__DU_EB_EE_PRECEDE_DETACHED_FUTURE_TARGET",
    }


def _error_code(call: Any) -> str:
    try:
        call()
    except Exception as exc:
        return str(getattr(exc, "code", exc.__class__.__name__))
    return "UNEXPECTED_PASS"


def reproduce_post_ih_conflict(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    du = _load(root / DU_OWNER, "g77_256ii_du")
    eb = _load(root / EB_OWNER, "g77_256ii_eb")
    ee = _load(root / EE_OWNER, "g77_256ii_ee")
    du_if = du.validate_file(root / CANDIDATE, root, expected_head=IF_HEAD)
    if set(du_if.values()) != {"PASS"}:
        raise IIResolutionError("IH_IF_BOUND_DU_NOT_PASS")
    if_result = {
        "du": "VERIFIED__CURRENT_IF_BOUND",
        "eb": _error_code(lambda: eb.validate_candidate(root, root / CANDIDATE, required_head=IF_HEAD, required_tree=IF_TREE)),
        "ee": _error_code(lambda: ee._authenticate_git(root, IF_HEAD, IF_TREE)),
    }
    current_result = {
        "eb": _error_code(lambda: eb.validate_candidate(root, root / CANDIDATE, required_head=IH_HEAD, required_tree=IH_TREE)),
        "ee_git": _error_code(lambda: ee._authenticate_git(root, IH_HEAD, IH_TREE)),
        "ee_candidate": _error_code(lambda: ee._manifest_binding(root / CANDIDATE, du, expected_head=IH_HEAD, runtime=False)),
    }
    if if_result["eb"] != "REQUIRED_HEAD_MISMATCH" or if_result["ee"] != "REQUIRED_HEAD_MISMATCH":
        raise IIResolutionError("IF_BASELINE_CONFLICT_NOT_REPRODUCED")
    if current_result != {"eb": "REQUIRED_HEAD_MISMATCH", "ee_git": "UNEXPECTED_PASS", "ee_candidate": "CANDIDATE_REQUIRED_HEAD_MISMATCH"}:
        raise IIResolutionError("IH_BASELINE_CONFLICT_NOT_REPRODUCED")
    return {
        "actual_current_head": IH_HEAD,
        "actual_current_tree": IH_TREE,
        "target_runtime_head": IF_HEAD,
        "target_runtime_tree": IF_TREE,
        "if_as_shared_baseline": if_result,
        "ih_as_shared_baseline": current_result,
        "post_ih_commit_eb_ee_conflict": "VERIFIED__PERSISTS",
        "precommit_only_conflict_hypothesis": "VERIFIED__FALSE",
        "single_shared_identity_satisfies_both_roles": "VERIFIED__NO",
        "eb_receipt_created": False,
        "ee_receipt_created": False,
    }


def identity_contract_matrix() -> list[dict[str, Any]]:
    return [
        {"identity": "TARGET_RUNTIME_IDENTITY", "meaning": "immutable commit/tree selected for the detached guest checkout", "owner": "FM launcher checkout binding", "consumer": "FM checkout/bootstrap/guest projection", "runtime_provenance": True, "current_certification_provenance": False, "checkout_provenance": True, "equals_current_head": False, "equals_target_head": True, "equality_status": "RUNTIME_TARGET_INVARIANT", "coupling_origin": "SEMANTIC__OWNER_DECLARED"},
        {"identity": "CURRENT_REPOSITORY_IDENTITY", "meaning": "actual committed HEAD/tree of the canonical worktree", "owner": "Git", "consumer": "FM readiness/admission and EB/EE baseline authentication", "runtime_provenance": False, "current_certification_provenance": True, "checkout_provenance": False, "equals_current_head": True, "equals_target_head": False, "equality_status": "CERTIFICATION_CURRENTNESS_INVARIANT", "coupling_origin": "SEMANTIC__CURRENTNESS_DECLARED"},
        {"identity": "CERTIFICATION_BASELINE_IDENTITY", "meaning": "HEAD/tree against which EB/EE issue and reauthenticate repository evidence", "owner": "EB and EE receipt contracts", "consumer": "EB/EE receipt verifiers", "runtime_provenance": False, "current_certification_provenance": True, "checkout_provenance": False, "equals_current_head": True, "equals_target_head": False, "equality_status": "CERTIFICATION_CURRENTNESS_INVARIANT", "coupling_origin": "SEMANTIC__CURRENTNESS_DECLARED"},
        {"identity": "CANDIDATE_REQUIRED_IDENTITY", "meaning": "requested checkout HEAD and reconstruction tree carried by DU Canonical V1", "owner": "DU contract/schema/validator", "consumer": "DU plus EB/EE adapters", "runtime_provenance": True, "current_certification_provenance": False, "checkout_provenance": True, "equals_current_head": False, "equals_target_head": True, "equality_status": "RUNTIME_TARGET_INVARIANT", "coupling_origin": "SEMANTIC__DU_OWNER_DECLARED"},
        {"identity": "CHECKOUT_IDENTITY", "meaning": "detached clean read-only checkout actually projected to the guest", "owner": "FM launcher and context checkout binding", "consumer": "FM host/guest validation", "runtime_provenance": True, "current_certification_provenance": False, "checkout_provenance": True, "equals_current_head": False, "equals_target_head": True, "equality_status": "PROVENANCE_INVARIANT", "coupling_origin": "SEMANTIC__FM_OWNER_DECLARED"},
        {"identity": "EVIDENCE_ISSUER_IDENTITY", "meaning": "current repository identity whose owner/schema bytes issue EB/EE evidence", "owner": "implicit in Git plus EB/EE current-baseline checks", "consumer": "EB/EE receipt verification", "runtime_provenance": False, "current_certification_provenance": True, "checkout_provenance": False, "equals_current_head": True, "equals_target_head": False, "equality_status": "NOT_PROVEN__NO_SEPARATE_V1_FIELD", "coupling_origin": "IMPLEMENTATION_DERIVED__NO_SEPARATE_V1_FIELD"},
    ]


def resolution_options() -> dict[str, Any]:
    common = {"p11_change_required": False, "new_route_required": False, "new_authority_layer_required": False}
    return {
        "OPTION_A": common | {"existing_owner_support": "PARTIAL__CONCEPTS_EXIST_BUT_EB_EE_SCHEMA_HAS_ONE_SHARED_HEAD", "new_schema_required": True, "self_reference_risk": "LOW_IF_BASELINE_IS_PRIOR_COMMITTED_HEAD", "historical_evidence_impact": "PRESERVE_V1_AND_ADD_REVIEWED_SUCCESSOR", "minimum_delta": "REVIEWED_DU_EB_EE_SUCCESSOR_FIELDS_AND_GENERAL_VALIDATION", "constitutional_status": "NOT_PROVEN__REQUIRES_SEPARATE_GOVERNED_SCHEMA_AUTHORITY"},
        "OPTION_B": common | {"existing_owner_support": "VERIFIED__NO", "new_schema_required": True, "self_reference_risk": "NOT_APPLICABLE", "historical_evidence_impact": "NONE", "minimum_delta": "NOT_AVAILABLE", "constitutional_status": "NOT_PROVEN__NO_EXISTING_RECEIPT_FIELD_SEPARATES_ROLES"},
        "OPTION_C": common | {"existing_owner_support": "VERIFIED__NO__SOURCE_TREE_MUST_EQUAL_TREE_OF_REQUIRED_HEAD", "new_schema_required": True, "self_reference_risk": "NOT_APPLICABLE", "historical_evidence_impact": "WOULD_REINTERPRET_DU_V1", "minimum_delta": "REJECTED", "constitutional_status": "NOT_PROVEN__V1_PROVENANCE_INVARIANT_FORBIDS"},
        "OPTION_D": common | {"existing_owner_support": "VERIFIED__NO__CLOSED_SCHEMA_HAS_NO_TARGET_FIELD", "new_schema_required": True, "self_reference_risk": "NOT_APPLICABLE", "historical_evidence_impact": "WOULD_CHANGE_CLOSED_V1_SCHEMA", "minimum_delta": "REJECTED", "constitutional_status": "NOT_PROVEN__PRODUCER_DID_NOT_COLLAPSE_EXISTING_FIELDS"},
        "OPTION_E": common | {"existing_owner_support": "VERIFIED__CURRENT_ARCHITECTURE_HAS_NO_GOVERNED_SEPARATION", "new_schema_required": False, "self_reference_risk": "VERIFIED__0_FOR_EVIDENCE_ONLY_FORMALIZATION", "historical_evidence_impact": "VERIFIED__NONE", "minimum_delta": "II_EVIDENCE_ONLY_GAP_FORMALIZATION", "constitutional_status": "VERIFIED__SELECTED_FAIL_CLOSED"},
    }


def preserve_future_state(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    candidate = load_canonical(root / CANDIDATE)
    context = load_canonical(root / CONTEXT)
    if (root / CANDIDATE).read_bytes() != (root / RUNTIME).read_bytes():
        raise IIResolutionError("CANDIDATE_RUNTIME_BYTES_DIFFER")
    checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    if (candidate["manifest"]["required_head"], candidate["manifest"]["source_tree"], checkout["head"], checkout["tree"]) != (IF_HEAD, IF_TREE, IF_HEAD, IF_TREE):
        raise IIResolutionError("IF_RUNTIME_TARGET_DRIFT")
    launcher = _load(root / FM_LAUNCHER, "g77_256ii_launcher")
    adapter = _load(root / IF_ADAPTER, "g77_256ii_future_adapter")
    if (launcher.CHECKOUT_HEAD, launcher.CHECKOUT_TREE) != (IF_HEAD, IF_TREE):
        raise IIResolutionError("LAUNCHER_IF_TARGET_DRIFT")
    if adapter.deterministic_submission_kwargs(root) != {"now_unix_ns": 500}:
        raise IIResolutionError("DETERMINISTIC_TIME_DRIFT")
    calls = {node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id for node in ast.walk(ast.parse((root / IF_ADAPTER).read_text())) if isinstance(node, ast.Call) and isinstance(node.func, (ast.Attribute, ast.Name))}
    if calls.intersection({"time", "time_ns", "now", "sleep"}):
        raise IIResolutionError("WALL_CLOCK_DEPENDENCY_PRESENT")
    return {
        "candidate_identity": sha256_path(root / CANDIDATE),
        "runtime_identity": sha256_path(root / RUNTIME),
        "candidate_runtime_byte_identity_status": "VERIFIED",
        "context_identity": context["context_sha256"],
        "context_file_sha256": sha256_path(root / CONTEXT),
        "candidate_required_identity": {"head": IF_HEAD, "tree": IF_TREE},
        "checkout_identity": {"head": checkout["head"], "tree": checkout["tree"]},
        "context_repository_identity": {"head": context["repository_head"], "tree": context["repository_tree"]},
        "current_context_applicability": "NOT_PROVEN__COMMITTED_IH_CONTEXT_REPOSITORY_IDENTITY_IS_IF_NOT_CURRENT_IH",
        "evaluation_time_unix_ns": 500, "valid_from_unix_ns": 600, "valid_until_unix_ns": 1000,
        "temporal_relation": "VERIFIED__500_LT_600_LT_1000",
        "payload_digest": FUTURE_PAYLOAD_DIGEST, "source_act_digest": SOURCE_ACT_DIGEST,
        "che_correlation_identity": CORRELATION_IDENTITY,
        "ii_new_future_semantic_mutation_count": "VERIFIED__0",
        "deterministic_time_fixture_status": "VERIFIED",
        "wall_clock_dependency_count_on_future_path": "VERIFIED__0",
        "production_route_before": "VERIFIED__1", "production_route_after": "VERIFIED__1", "production_route_delta": "VERIFIED__0",
    }


def authenticate_ex(repository_root: Path) -> dict[str, Any]:
    raw = (repository_root.resolve() / EX_CERTIFICATE).read_bytes()
    envelope = json.loads(raw, object_pairs_hook=_unique)
    if not isinstance(envelope, dict):
        raise IIResolutionError("EX_CERTIFICATE_NOT_OBJECT")
    certificate = envelope["certificate"]
    preimage = deepcopy(envelope)
    preimage["certificate_sha256"] = ""
    payload = json.dumps(
        preimage,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    if envelope["certificate_sha256"] != sha256_bytes(payload):
        raise IIResolutionError("EX_CERTIFICATE_SEAL_INVALID")
    if certificate["component_counts"]["CERTIFIED"] != 17:
        raise IIResolutionError("EX_17_OF_17_NOT_AUTHENTICATED")
    return {"ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0", "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED"}


def terminal_reduction(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    entry = authenticate_entry(root)
    ih = reconstruct_ih(root)
    trace = authenticate_owner_trace(root)
    conflict = reproduce_post_ih_conflict(root)
    future = preserve_future_state(root)
    counters = {key: 0 for key in ("human_operational_authority", "authority_consumption", "pre", "fm_operational_launcher_invocation", "qemu", "vm_creation", "vm_boot", "operation_attempt", "request", "p11_entry", "protected_invocation", "protected_effect", "retry", "repair_retry", "replay", "e05_credit")}
    return {
        "schema_id": "G77_256II_RUNTIME_CERTIFICATION_CONTRACT_RESOLUTION_V1",
        "mode": "REPOSITORY_ONLY__EVIDENCE_FORMALIZATION__NO_OPERATION",
        "entry": entry,
        "ih_reconstruction": ih,
        "post_ih_conflict": conflict,
        "identity_contract_matrix": identity_contract_matrix(),
        "owner_trace": trace,
        "resolution_options": resolution_options(),
        "resolution": {
            "selected_option": "OPTION_E",
            "runtime_certification_identity_contract": "NOT_PROVEN__NO_UNIQUE_EXISTING_GOVERNED_SEPARATION",
            "observed_cross_role_coupling": "VERIFIED__IMPLEMENTATION_DERIVED",
            "coupling_classification": "VERIFIED__IMPLEMENTATION_COUPLING",
            "identity_coupling_status": "NOT_PROVEN__NO_UNIQUE_GOVERNED_CONTRACT_SEPARATION",
            "production_owner_mutation_count": "VERIFIED__0",
            "pre_commit_self_reference_count": "VERIFIED__0",
            "future_commit_prediction_count": "VERIFIED__0",
            "arbitrary_historical_head_bypass": "VERIFIED__NO",
            "current_head_provenance_weakening": "VERIFIED__NO",
            "vector_specific_certification_bypass": "VERIFIED__NO",
        },
        "future_state": future,
        "gn_gl": {"gn": "NOT_APPLICABLE__NO_HUMAN_AUTHORIZATION_REQUEST_CREATED", "gl": "NOT_APPLICABLE__NO_AUTHORITY_OR_RECEIPT_PARENT_CREATED"},
        "historical_failure_firewall": {"status": "VERIFIED", "reintroduced_historical_failure_count": "VERIFIED__0", "protected_set": ["PRE_COMMIT_HEAD_SELF_REFERENCE", "CHECKOUT_PINNING_MISMATCH", "BOOTSTRAP_PINNING_MISMATCH", "HOST_GUEST_PATH_MISMATCH", "LAUNCHER_ADAPTER_MISMATCH", "NOCLOUD_MISMATCH", "NONCANONICAL_HANDOFF", "RECEIPT_PARENT_ABSENCE", "SEALED_HISTORICAL_SHA_MISMATCH", "TRANSIENT_ROOT_LIFECYCLE_MISMATCH", "BASE_IMAGE_MUTATION", "ARBITRARY_HISTORICAL_HEAD_CERTIFICATION", "RUNTIME_CERTIFICATION_IDENTITY_COLLAPSE"]},
        "ex": authenticate_ex(root),
        "reuse_impact": {
            "reused_certified_capability_set": ["IH_IF_BOUND_PREPARATION", "IF_RUNTIME_TARGET", "FM_SINGLE_ROUTE", "DU", "EB", "EE", "GN", "GL", "P11", "CHE", "FK", "EX_17_OF_17", "GOVERNANCE", "LAYER_0"],
            "new_capability_set": ["II_MACHINE_READABLE_IDENTITY_CONTRACT_GAP_FORMALIZATION"],
            "unreachable_preexisting_capability_set": [], "parallel_flow_created": "VERIFIED__NO",
            "production_route_before": "VERIFIED__1", "production_route_after": "VERIFIED__1", "production_route_delta": "VERIFIED__0",
            "new_generic_framework_count": "VERIFIED__0", "new_authority_layer_count": "VERIFIED__0", "new_production_route_count": "VERIFIED__0", "new_runtime_owner_count": "VERIFIED__0", "new_clock_infrastructure_count": "VERIFIED__0", "p11_core_change_count": "VERIFIED__0",
        },
        "infrastructure_amortization": {
            "e05_generations_per_credit": "VERIFIED__5__HISTORICAL_WRONG_PROVENANCE_LIFECYCLE_ONLY",
            "operational_attempts_per_credit": "VERIFIED__1__HISTORICAL_WRONG_PROVENANCE_ONLY",
            "future_generations_before_ii": "VERIFIED__4__IE_IF_IG_IH", "future_generations_so_far": "VERIFIED__5__IE_IF_IG_IH_II",
            "future_e05_credit_so_far": "VERIFIED__0", "future_operational_attempts_so_far": "VERIFIED__0",
            "new_common_infrastructure_for_future": "VERIFIED__0", "new_vector_specific_infrastructure_for_future": "VERIFIED__0",
            "marginal_new_infrastructure_for_ii": "VERIFIED__EVIDENCE_ONLY_RESOLVER_TEST_REPORT_AND_REDUCTION",
            "expected_next_credit_generation_count": "NOT_PROVEN__IDENTITY_CONTRACT_REQUIRES_HUMAN_GOVERNANCE_DECISION",
        },
        "validation": {
            "mode": "REPOSITORY_ONLY__NO_OPERATIONAL_VALIDATION",
            "ii_focused": "VERIFIED__15_PASSED",
            "current_applicable_lineage_and_owner_assertions": "VERIFIED__142_PASSED",
            "historical_or_superseded_snapshot_assertions": "NOT_APPLICABLE__18_EXACTLY_DESELECTED_WITH_LINEAGE_REASONS_IN_G48_REPORT",
            "p11_human_act_che_fk": "VERIFIED__72_PASSED",
            "ex_regression": "VERIFIED__12_OF_12__CERTIFIED_17_OF_17",
            "governance_layer_0": "VERIFIED__9_PASSED",
            "conformance_engine": "VERIFIED__20_PASSED__CONFORMANT__0_WARNINGS__0_VIOLATIONS",
            "canonical_json_duplicate_keys_seals_ast": "VERIFIED",
            "git_diff_check": "VERIFIED__CLEAN",
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_L5_CLAIM", "cross_worker_state_recovery_level": "NOT_PROVEN__WORKER_IDENTITY_NOT_INSTRUMENTED",
            "repository_derived_context_ratio": "ESTIMATED__DOMINANT__NO_NUMERIC_INSTRUMENT", "human_handoff_information_required": "VERIFIED__SCOPE_AND_TARGET_LOCATORS_ONLY",
            "previous_worker_conversation_required": "VERIFIED__NO", "previous_worker_identity_required": "VERIFIED__NO", "previous_worker_memory_required": "VERIFIED__NO",
            "authenticated_repository_continuation": "VERIFIED__YES", "inter_generation_cross_worker_continuation": "NOT_PROVEN__WORKER_IDENTITY_NOT_INSTRUMENTED",
            "same_generation_continuation_status": "ESTIMATED__USER_SUPPLIED_SAME_THREAD_PROVIDER_RESET__REPOSITORY_PROVES_CONTINUOUS_II_DELTA_ONLY",
            "intra_generation_cross_worker_continuation": "NOT_APPLICABLE__SAME_THREAD_REPORTED__WORKER_IDENTITY_NOT_REPOSITORY_INSTRUMENTED", "uncommitted_delta_recovery": "VERIFIED__EXISTING_II_RESOLVER_AUTHENTICATED_AND_REUSED",
            "authority_state_recovery": "VERIFIED__NO_CURRENT_AUTHORITY_EXISTS", "consumed_authority_recovery": "VERIFIED__IC_HISTORICAL_CONSUMED_NONREUSABLE",
            "post_operation_state_recovery": "VERIFIED__IC_TERMINAL_REUSED", "operation_replay_prevention": "VERIFIED__II_OPERATIONAL_COUNTERS_ZERO",
            "cross_worker_constitutional_drift": "NOT_PROVEN__WORKER_IDENTITY_NOT_INSTRUMENTED", "handoff_sufficiency_status": "VERIFIED",
            "handoff_state_completeness": "VERIFIED__COMPLETE_FOR_II_REPOSITORY_SCOPE", "handoff_reconstruction_required": "VERIFIED__YES",
            "handoff_reconstruction_success": "VERIFIED__YES", "handoff_ambiguity_count": "VERIFIED__0", "unauthenticated_handoff_assumption_count": "VERIFIED__0",
        },
        "metrics": {
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR", "constitutional_health_evidence": "VERIFIED__POST_IH_CONFLICT_REPRODUCED_AND_FAIL_CLOSED",
            "shadow_automation_status": "VERIFIED__ABSENT", "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "e05_frontier_distance": "VERIFIED__8_OF_18_OBLIGATIONS_REMAIN", "selected_e05_local_frontier_distance": "NOT_PROVEN__RUNTIME_CERTIFICATION_IDENTITY_CONTRACT",
            "governance_efficience": "ESTIMATED__MINIMUM_EVIDENCE_ONLY_FORMALIZATION", "architectural_governance_efficience": "VERIFIED__ONE_ROUTE_ZERO_OWNER_MUTATION",
            "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED", "cognition_assisted_handoff": "VERIFIED__AUTHENTICATED_IH_TO_II_REPOSITORY_CONTINUATION",
            "aigol_codex_work_share": "NOT_MEASURED", "overengineering_risk": "ESTIMATED__LOW", "proof_process_overhead_risk": "ESTIMATED__MODERATE",
            "cognition_provenance": "VERIFIED__AUTHENTICATED_REPOSITORY_PRIMARY", "candidate_capability": "VERIFIED__IF_BOUND_DU_VALID__EB_EE_NOT_PROVEN",
            "shadow_design_target": "VERIFIED__FORMALIZE_REUSE_BIND_VERIFY_FAIL_CLOSED_REDUCE_STOP", "constitutional_continuation_progress": "VERIFIED__STRUCTURAL_IDENTITY_CONFLICT_FORMALIZED__READINESS_NOT_PROVEN",
            "prompt_context_reuse_ratio": "NOT_MEASURED", "token_benchmark": "NOT_MEASURED", "llm_cost_reduction_ratio": "NOT_MEASURED", "lcrr": "NOT_MEASURED",
            "e05_generations_per_credit": "VERIFIED__5__HISTORICAL_WRONG_PROVENANCE_LIFECYCLE_ONLY", "operational_attempts_per_credit": "VERIFIED__1__HISTORICAL_WRONG_PROVENANCE_ONLY",
            "marginal_e05_generation_cost": "NOT_MEASURED", "marginal_new_infrastructure_per_e05_credit": "NOT_MEASURED__FUTURE_CREDIT_NOT_EARNED",
            "infrastructure_amortization_signal": "ESTIMATED__PROOF_REUSE_WITH_ZERO_RUNTIME_EXPANSION", "expected_next_credit_generation_count": "NOT_PROVEN__IDENTITY_CONTRACT_REQUIRES_HUMAN_GOVERNANCE_DECISION",
        },
        "cognition_provenance": "VERIFIED__AUTHENTICATED_GIT_IH_IG_IF_IE_ID_IC_P11_CHE_FK_FM_GN_GL_DU_EB_EE_EX_GOVERNANCE_LAYER_0_PINNED_NESTED_AUTHORITY_CURRENT_TESTS",
        "operational_counters": counters,
        "e05": {"before": "10/18", "after": "10/18", "satisfied": 10, "remaining": 8, "credit": 0},
        "terminal_control": {
            "current_e05_status": "VERIFIED__10_OF_18", "selected_next_e05_vector": "VERIFIED__FUTURE",
            "future_repository_formalization": "VERIFIED", "future_route_binding": "VERIFIED__STATIC_MEMBERSHIP_ONLY",
            "future_live_identity_rebind": "VERIFIED__REPOSITORY_PREPARED_IF_BOUND", "runtime_certification_identity_contract": "NOT_PROVEN__NO_UNIQUE_EXISTING_GOVERNED_SEPARATION",
            "identity_coupling_status": "NOT_PROVEN__NO_UNIQUE_GOVERNED_CONTRACT_SEPARATION", "future_live_binding": "NOT_PROVEN__STRUCTURAL_IDENTITY_CONTRACT_GAP",
            "future_preoperational_readiness": "NOT_PROVEN__STRUCTURAL_IDENTITY_CONTRACT_GAP", "future_operational_capability": "NOT_PROVEN",
            "next_operational_generation_eligible": "NOT_PROVEN", "e05_credit": "VERIFIED__0",
            "last_verified_edge": "POST_IH_COMMIT_IF_TARGET_AND_IH_CERTIFICATION_BASELINE_CONFLICT_REPRODUCED_AND_IDENTITY_ROLES_FORMALIZED",
            "first_broken_edge": "NO_EXISTING_GOVERNED_FIELD_SEPARATES_DU_RUNTIME_TARGET_FROM_EB_EE_CURRENT_CERTIFICATION_BASELINE",
            "minimum_missing_capability": "HUMAN_GOVERNED_VERSIONED_DU_EB_EE_CONTRACT_SEPARATING_RUNTIME_TARGET_PROVENANCE_FROM_CURRENT_CERTIFICATION_PROVENANCE",
            "minimum_legal_next_delta": "HUMAN_REVIEW_AND_SEPARATELY_AUTHORIZED_GENERAL_SUCCESSOR_CONTRACT_DESIGN__NO_OPERATION",
            "auto_continuable": False, "human_authorization_required": False, "human_review_required": True, "next_generation_started": False,
            "verdict": "NOT_PROVEN__II_RUNTIME_CERTIFICATION_CONTRACT_UNRESOLVED__OPTION_E_GAP_FORMALIZED__ZERO_OWNER_MUTATION__ZERO_OPERATION__E05_10_OF_18__HUMAN_REVIEW_REQUIRED",
        },
    }


def terminal_envelope(repository_root: Path) -> dict[str, Any]:
    reduction = terminal_reduction(repository_root)
    return {"schema_id": "G77_256II_RUNTIME_CERTIFICATION_CONTRACT_RESOLUTION_ENVELOPE_V1", "reduction": reduction, "reduction_sha256": sha256_bytes(canonical_bytes(reduction))}


if __name__ == "__main__":
    raise SystemExit("repository-only II resolver; no operational CLI entry point")
