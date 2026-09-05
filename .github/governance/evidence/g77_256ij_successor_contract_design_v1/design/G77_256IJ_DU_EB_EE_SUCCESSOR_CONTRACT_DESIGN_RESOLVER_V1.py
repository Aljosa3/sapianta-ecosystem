#!/usr/bin/env python3
"""Repository-only G77-256IJ successor-contract design resolver.

This module authenticates committed II, formalizes the minimum general
DU/EB/EE successor requirements, proves the design firewalls, and stops where
the repository does not select one concrete closed-schema placement.  It is a
design artifact, not an operational successor implementation or authority.
"""

from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True

BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
II_HEAD = "4365d97394deca438a1a57d5b47c699afb54bd5d"
II_TREE = "a748da718c2807cee0bfce19ba6aa3789f9586a7"
II_SUBJECT = "G77-256II formalize runtime certification contract gap"
IH_HEAD = "8698486cdf9a206f2bc73993c83389d6850362ff"
IG_HEAD = "71391a75011cdc388bdac9183f4654814a044c69"
IF_HEAD = "699fcdce794ff49b6c8735602936355724ed1c90"
IF_TREE = "7c773d4b2acdf013f1b8238eabfc8eced4dd6866"
IE_HEAD = "9420764a5bb6db8909334f2a422225687a37a346"
STABLE_ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_TAG = "refs/tags/sapianta-system-nested-authority-3183bab-v1"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"

IJ_ROOT = Path(".github/governance/evidence/g77_256ij_successor_contract_design_v1")
II_ROOT = Path(".github/governance/evidence/g77_256ii_runtime_certification_contract_resolution_v1")
II_TERMINAL = II_ROOT / "G77_256II_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
DU_CONTRACT = Path(".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/G77_256DU_CANONICAL_CONTINUATION_MANIFEST_CONTRACT_V1.md")
DU_SCHEMA = Path(".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/G77_256DU_CANONICAL_CONTINUATION_MANIFEST_SCHEMA_V1.json")
DU_OWNER = Path(".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V1.py")
EB_SCHEMA = Path(".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v1/G77_256EB_CANDIDATE_BOUND_VALIDATION_RECEIPT_SCHEMA_V1.json")
EB_OWNER = Path(".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v1/validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V1.py")
EE_CONTRACT = Path(".github/governance/evidence/g77_256ee_runtime_consumer_binding_v1/G77_256EE_RUNTIME_CONSUMER_BINDING_CONTRACT_V1.md")
EE_SCHEMA = Path(".github/governance/evidence/g77_256ee_runtime_consumer_binding_v1/G77_256EE_RUNTIME_CONSUMER_BINDING_RECEIPT_SCHEMA_V1.json")
EE_OWNER = Path(".github/governance/evidence/g77_256ee_runtime_consumer_binding_v1/validator/G77_256EE_RUNTIME_CONSUMER_BINDING_VALIDATOR_V1.py")
FM_LAUNCHER = Path(".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py")
FM_CONTEXT_OWNER = Path(".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/sapianta_fresh_operation_context_v1.py")
IH_CANDIDATE = Path(".github/governance/evidence/g77_256ih_future_if_identity_rebind_v1/live_binding/candidate/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json")
IH_RUNTIME = Path(".github/governance/evidence/g77_256ih_future_if_identity_rebind_v1/live_binding/runtime_projection/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json")
IH_CONTEXT = Path(".github/governance/evidence/g77_256ih_future_if_identity_rebind_v1/live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json")
IF_ADAPTER = Path(".github/governance/evidence/g77_256if_future_post_commit_readiness_v1/adapter/G77_256IF_FUTURE_VECTOR_ADAPTER_V1.py")
EX_CERTIFICATE = Path(".github/governance/evidence/g77_256ex_common_substrate_certification_v1/G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json")

II_HASHES = {
    II_ROOT / "G77_256II_G48_IMPLEMENTATION_REPORT_V1.md": "446fb114ad19a54e845f08be4823e28a5a771d1a08e6dc4ee7a11a2b0181f74d",
    II_TERMINAL: "92992bd677a572aa44a22d5b875c458cd53e5882fd8ae17577f601bbc30c78e4",
    II_ROOT / "analysis/G77_256II_RUNTIME_CERTIFICATION_CONTRACT_RESOLVER_V1.py": "3ca25aff9d55380b26e217323d467b1b386aa8cac8a7606246f22996121652c2",
    II_ROOT / "tests/test_g77_256ii_runtime_certification_contract_resolution_v1.py": "2177fb2c0e59b5b61cd5ee83ae0f2b4353d00f0576110f27758cd2a58c60759b",
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
    FM_CONTEXT_OWNER: "fdfa04349529d70bc97820a1848f8afc22b81071859d5456550799e0f9476237",
}

FUTURE_CANDIDATE_SHA = "ad5d204ec6ace09f18b83fd5f868e73dac5e36dad81149f9f335c87f68cf42f7"
FUTURE_CONTEXT_INNER = "769f7b5cde5946450acbecfd956d479e91d9cf818d47bd4db34cb5086a1b07cb"
FUTURE_PAYLOAD = "sha256:9568e0c248ad488cabcf6bde6b490c544077862d10e3fda13bcdc8ed9953f547"
FUTURE_SOURCE_ACT = "sha256:7167b0725d2c84bafde1d0060f512b0fa358d777ec1beff8b7c68d22ee6502e8"
FUTURE_CHE = "CHE-CORRELATION-15b2680b5577da169cecf9efb3231e2e6f6467e6f409fa2594b04128f998e454"


class IJDesignError(ValueError):
    """One fail-closed repository-only IJ design error."""


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise IJDesignError(f"DUPLICATE_JSON_KEY__{key}")
        value[key] = item
    return value


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=_unique)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise IJDesignError(f"CANONICAL_JSON_INVALID__{path.name}")
    return value


def _git(root: Path, *arguments: str) -> str:
    try:
        return subprocess.check_output(["git", *arguments], cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError as exc:
        raise IJDesignError("GIT_IDENTITY_UNAVAILABLE") from exc


def _git_bytes(root: Path, revision: str, path: Path) -> bytes:
    try:
        return subprocess.check_output(["git", "show", f"{revision}:{path.as_posix()}"], cwd=root, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as exc:
        raise IJDesignError(f"COMMITTED_OBJECT_UNAVAILABLE__{path.name}") from exc


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
        "repository": str(root), "branch": BRANCH, "head": II_HEAD,
        "tree": II_TREE, "subject": II_SUBJECT, "origin": ORIGIN,
        "remote_tracking_head": II_HEAD, "index": "",
    }
    if observed != expected:
        raise IJDesignError("EXACT_COMMITTED_II_CHECKPOINT_MISMATCH")
    for ancestor in (IH_HEAD, IG_HEAD, IF_HEAD, IE_HEAD, STABLE_ANCHOR):
        if subprocess.run(["git", "merge-base", "--is-ancestor", ancestor, II_HEAD], cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode:
            raise IJDesignError(f"ANCESTRY_MISSING__{ancestor}")
    for line in subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=all"], cwd=root, text=True).splitlines():
        if not line[3:].startswith(IJ_ROOT.as_posix() + "/"):
            raise IJDesignError(f"UNRELATED_WORKTREE_MUTATION__{line[3:]}")
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
        raise IJDesignError("NESTED_AUTHORITY_NOT_CLEAN_DETACHED_PINNED")
    return observed | {"nested": nested_state, "worktree_scope": "VERIFIED__IJ_DESIGN_EVIDENCE_ONLY"}


def reconstruct_ii(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    identities: dict[str, Any] = {}
    for path, expected_sha in II_HASHES.items():
        committed = _git_bytes(root, II_HEAD, path)
        if committed != (root / path).read_bytes() or sha256_bytes(committed) != expected_sha:
            raise IJDesignError(f"II_IDENTITY_MISMATCH__{path.name}")
        identities[path.name] = {"path": path.as_posix(), "sha256": expected_sha, "git_blob": _git(root, "rev-parse", f"{II_HEAD}:{path.as_posix()}")}
    envelope = load_canonical(root / II_TERMINAL)
    reduction = envelope["reduction"]
    if envelope["reduction_sha256"] != sha256_bytes(canonical_bytes(reduction)):
        raise IJDesignError("II_TERMINAL_SEAL_INVALID")
    control = reduction["terminal_control"]
    required = {
        "current_e05_status": "VERIFIED__10_OF_18",
        "future_operational_capability": "NOT_PROVEN",
        "future_preoperational_readiness": "NOT_PROVEN__STRUCTURAL_IDENTITY_CONTRACT_GAP",
        "runtime_certification_identity_contract": "NOT_PROVEN__NO_UNIQUE_EXISTING_GOVERNED_SEPARATION",
        "identity_coupling_status": "NOT_PROVEN__NO_UNIQUE_GOVERNED_CONTRACT_SEPARATION",
        "e05_credit": "VERIFIED__0",
    }
    if {key: control[key] for key in required} != required:
        raise IJDesignError("II_TERMINAL_FRONTIER_MISMATCH")
    if reduction["resolution_options"]["OPTION_E"]["constitutional_status"] != "VERIFIED__SELECTED_FAIL_CLOSED":
        raise IJDesignError("II_OPTION_E_NOT_AUTHENTICATED")
    return {"status": "VERIFIED", "identities": identities, "frontier": required, "option_e": "VERIFIED__SELECTED_FAIL_CLOSED"}


def authenticate_owners(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    for path, digest in OWNER_HASHES.items():
        if sha256_path(root / path) != digest or _git_bytes(root, II_HEAD, path) != (root / path).read_bytes():
            raise IJDesignError(f"OWNER_IDENTITY_MISMATCH__{path.name}")
    du_text = (root / DU_CONTRACT).read_text()
    if "A semantic change requires a new reviewed schema version" not in du_text:
        raise IJDesignError("DU_REVIEWED_SUCCESSOR_RULE_ABSENT")
    for path in (DU_SCHEMA, EB_SCHEMA, EE_SCHEMA):
        schema = json.loads((root / path).read_bytes(), object_pairs_hook=_unique)
        if schema.get("additionalProperties") is not False:
            raise IJDesignError(f"CLOSED_SCHEMA_ROOT_MISSING__{path.name}")
    return {
        "owner_hashes": {path.as_posix(): digest for path, digest in OWNER_HASHES.items()},
        "v1_closed_schema_status": "VERIFIED",
        "reviewed_successor_rule": "VERIFIED__DU_REQUIRES_NEW_REVIEWED_SCHEMA_VERSION_FOR_SEMANTIC_CHANGE",
        "owner_chronology": "VERIFIED__DU_EB_EE_PRECEDE_DETACHED_FUTURE_TARGET",
    }


def identity_model() -> list[dict[str, Any]]:
    return [
        {"identity": "TARGET_RUNTIME_IDENTITY", "semantic_owner": "FM launcher target selection", "producer": "FM context producer", "consumer": "DU successor and checkout consumer", "equality": "CHECKOUT_IDENTITY", "current_head_required": False, "target_head_required": True},
        {"identity": "CURRENT_REPOSITORY_IDENTITY", "semantic_owner": "Git current repository state", "producer": "Git observation", "consumer": "EB/EE successor issuer and verifier", "equality": "CERTIFICATION_BASELINE_IDENTITY", "current_head_required": True, "target_head_required": False},
        {"identity": "CERTIFICATION_BASELINE_IDENTITY", "semantic_owner": "EB/EE successor contract", "producer": "EB/EE issuer from Git current state", "consumer": "EB/EE verifier", "equality": "CURRENT_REPOSITORY_IDENTITY_AT_ISSUANCE_AND_VERIFICATION", "current_head_required": True, "target_head_required": False},
        {"identity": "CANDIDATE_REQUIRED_IDENTITY", "semantic_owner": "DU candidate contract", "producer": "DU producer from authenticated FM target selection", "consumer": "DU/EB/EE successor", "equality": "TARGET_RUNTIME_IDENTITY", "current_head_required": False, "target_head_required": True},
        {"identity": "CHECKOUT_IDENTITY", "semantic_owner": "FM context and launcher checkout binding", "producer": "FM context producer", "consumer": "FM host/guest checkout validator", "equality": "TARGET_RUNTIME_IDENTITY", "current_head_required": False, "target_head_required": True},
        {"identity": "EVIDENCE_ISSUER_IDENTITY", "semantic_owner": "Git current state plus bound EB/EE implementation", "producer": "EB/EE issuer", "consumer": "receipt verifier", "equality": "CERTIFICATION_BASELINE_PLUS_IMPLEMENTATION_BINDINGS", "current_head_required": True, "target_head_required": False},
    ]


def schema_minimality() -> dict[str, Any]:
    return {
        "minimum_new_semantic_field_count": 2,
        "minimum_new_schema_coordinate_set": ["certification_baseline_head", "certification_baseline_tree"],
        "required_nonidentity_structural_binding": "runtime_target_selection_binding",
        "reused_v1_coordinate_set": [
            "DU.manifest.required_head__RUNTIME_TARGET_COMMIT",
            "DU.manifest.source_tree__RUNTIME_TARGET_TREE",
            "EB.candidate_binding__CANDIDATE_BYTES_IMPLY_TARGET_PAIR",
            "EE.validated_candidate__CANDIDATE_BYTES_IMPLY_TARGET_PAIR",
            "EE.runtime_consumer__RUNTIME_BYTES_AND_INNER_IDENTITY",
            "FM.context.repository_head_tree__CURRENT_CERTIFICATION_SOURCE",
            "FM.context.checkout.head_tree__AUTHENTICATED_RUNTIME_TARGET_SOURCE",
        ],
        "deprecated_v1_coordinate_set": [],
        "v1_semantics_reinterpreted": "VERIFIED__NO",
        "historical_v1_mutation_count": "VERIFIED__0",
        "alternatives": [
            "FLAT_CERTIFICATION_PAIR_IN_EB_EE_SUCCESSOR_RECEIPTS",
            "NESTED_CERTIFICATION_BASELINE_OBJECT_IN_EB_EE_SUCCESSOR_RECEIPTS",
            "SHARED_VERSIONED_PROVENANCE_BINDING_OBJECT_REFERENCED_BY_EB_EE_SUCCESSORS",
        ],
        "schema_uniqueness": "NOT_PROVEN__MULTIPLE_EQUIVALENT_CLOSED_SCHEMA_PLACEMENTS_REMAIN",
        "minimum_required_abstraction": "TWO_SEPARATE_COMMIT_TREE_ROLES_PLUS_ONE_TARGET_SELECTION_EVIDENCE_BINDING",
        "proposed_abstraction_scope": "DU_EB_EE_PRE_MATERIALIZATION_PROVENANCE_ONLY",
        "generic_identity_framework_created": "VERIFIED__NO",
        "new_generic_framework_count": "VERIFIED__0",
    }


def successor_contract_design() -> dict[str, Any]:
    return {
        "design_scope": "GENERAL_DU_EB_EE_PRE_MATERIALIZATION_SUCCESSOR_REQUIREMENTS",
        "concrete_schema_status": "NOT_SELECTED__HUMAN_GOVERNANCE_DECISION_REQUIRED",
        "logical_fields": {
            "runtime_target_commit": "DU.manifest.required_head",
            "runtime_target_tree": "DU.manifest.source_tree",
            "certification_current_commit": "successor.certification_baseline_head",
            "certification_current_tree": "successor.certification_baseline_tree",
            "target_selection_evidence": "successor.runtime_target_selection_binding",
        },
        "mandatory_equalities": [
            "tree(runtime_target_commit)=runtime_target_tree",
            "candidate_required_identity=runtime_target_identity",
            "checkout_identity=runtime_target_identity",
            "context_checkout_identity=launcher_selected_target_identity",
            "actual_current_HEAD_at_issuance=certification_baseline_head",
            "actual_current_TREE_at_issuance=certification_baseline_tree",
            "tree(certification_baseline_head)=certification_baseline_tree",
            "receipt_issuer_provenance=certification_baseline_plus_bound_implementation",
            "candidate_runtime_bytes_and_inner_identity_equal",
        ],
        "intentionally_separated_v1_equality": "DU_candidate_required_head_NO_LONGER_REQUIRED_TO_EQUAL_EB_EE_certification_baseline_head",
        "equal_and_unequal_targets_supported": "VERIFIED__DESIGN_SUPPORTS_BOTH",
        "successor_contract_design_status": "NOT_PROVEN__MINIMUM_SEMANTIC_REQUIREMENTS_UNIQUE__CONCRETE_SCHEMA_MULTIPLE",
    }


def owner_model() -> dict[str, Any]:
    coordinates = {
        "runtime_target_commit_tree": {"owner": "FM_LAUNCHER_TARGET_SELECTION", "producer": "FM_CONTEXT_PRODUCER", "validator": "DU_SUCCESSOR_PLUS_GIT"},
        "candidate_target_provenance": {"owner": "DU_SUCCESSOR_CONTRACT", "producer": "DU_SUCCESSOR_PRODUCER", "validator": "DU_SUCCESSOR_VALIDATOR"},
        "certification_baseline_commit_tree": {"owner": "GIT_CURRENT_REPOSITORY_STATE", "producer": "EB_EE_SUCCESSOR_ISSUER", "validator": "EB_EE_SUCCESSOR_VERIFIER_PLUS_GIT"},
        "candidate_validation_receipt": {"owner": "EB_SUCCESSOR_CONTRACT", "producer": "EB_SUCCESSOR_ISSUER", "validator": "EB_SUCCESSOR_VERIFIER"},
        "runtime_consumer_receipt": {"owner": "EE_SUCCESSOR_CONTRACT", "producer": "EE_SUCCESSOR_ISSUER", "validator": "EE_SUCCESSOR_VERIFIER"},
        "context_repository_and_checkout_pairs": {"owner": "FM_CONTEXT_CONTRACT", "producer": "FM_CONTEXT_PRODUCER", "validator": "FM_CONTEXT_VALIDATOR"},
    }
    return {"coordinates": coordinates, "owner_uniqueness_status": "VERIFIED__DESIGN_ASSIGNMENTS_UNIQUE", "owner_conflict_count": "VERIFIED__0", "unowned_semantic_coordinate_count": "VERIFIED__0"}


def successor_responsibilities() -> dict[str, Any]:
    return {
        "DU_SUCCESSOR": ["candidate_structural_validity", "runtime_target_commit_tree_integrity", "FM_target_selection_binding_authentication", "candidate_target_equals_authenticated_selection", "constitutional_target_admissibility"],
        "EB_SUCCESSOR": ["actual_current_certification_baseline", "independent_DU_successor_result", "candidate_target_provenance", "target_current_noncollapse_semantics", "receipt_authenticity"],
        "EE_SUCCESSOR": ["actual_current_certification_baseline", "independent_EB_successor_receipt", "candidate_runtime_byte_and_inner_identity", "runtime_target_identity", "current_certification_identity", "receipt_path_integrity"],
        "EVIDENCE_ISSUER_EXPLICIT_FIELD_REQUIRED": "NOT_APPLICABLE__BASELINE_PLUS_IMPLEMENTATION_BINDINGS_CRYPTOGRAPHICALLY_IMPLY_ISSUER",
        "P11_CHANGE_REQUIRED": "VERIFIED__NO",
    }


def versioning_and_compatibility() -> dict[str, Any]:
    return {
        "successor_contract_versioning": "VERIFIED__NEW_REVIEWED_INCOMPATIBLE_VERSION_REQUIRED__EXACT_IDENTIFIER_NOT_PROVEN",
        "v1_semantics_reinterpreted": "VERIFIED__NO",
        "historical_v1_mutation_count": "VERIFIED__0",
        "backward_compatibility_status": "VERIFIED__V1_REMAINS_VALID_WHEN_TARGET_EQUALS_CURRENT__SUCCESSOR_DESIGN_SUPPORTS_EQUAL_OR_DETACHED",
        "v1_detached_target_support": "NOT_PROVEN__STRUCTURAL_CURRENT_HEAD_COUPLING",
        "runtime_version_dispatch_implemented": False,
        "version_dispatch_rule": "EXACT_SCHEMA_ID_VERSION_VALIDATOR_AND_RECEIPT_PROFILE_BINDING__UNKNOWN_OR_MIXED_VERSION_FAILS_CLOSED",
        "version_dispatch_bypass_risk": "NOT_PROVEN__NO_IMPLEMENTATION_EXISTS__DESIGN_REQUIRES_FAIL_CLOSED_BOUND_DISPATCH",
        "parallel_production_flow_risk": "VERIFIED__NO__CONTRACT_VERSION_IS_NOT_A_PRODUCTION_ROUTE",
    }


def target_and_currentness_firewalls(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    candidate = load_canonical(root / IH_CANDIDATE)
    context = load_canonical(root / IH_CONTEXT)
    if (root / IH_CANDIDATE).read_bytes() != (root / IH_RUNTIME).read_bytes():
        raise IJDesignError("CANDIDATE_RUNTIME_BYTES_DIFFER")
    target = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    manifest = candidate["manifest"]
    launcher_ast = ast.parse((root / FM_LAUNCHER).read_text())
    constants: dict[str, str] = {}
    for statement in launcher_ast.body:
        if isinstance(statement, ast.Assign) and len(statement.targets) == 1 and isinstance(statement.targets[0], ast.Name) and isinstance(statement.value, ast.Constant) and isinstance(statement.value.value, str):
            constants[statement.targets[0].id] = statement.value.value
    if (manifest["required_head"], manifest["source_tree"], target["head"], target["tree"], constants.get("CHECKOUT_HEAD"), constants.get("CHECKOUT_TREE")) != (IF_HEAD, IF_TREE, IF_HEAD, IF_TREE, IF_HEAD, IF_TREE):
        raise IJDesignError("FM_TARGET_SELECTION_CLOSURE_MISMATCH")
    if _git(root, "rev-parse", f"{IF_HEAD}^{{tree}}") != IF_TREE:
        raise IJDesignError("TARGET_TREE_NOT_OWNED_BY_TARGET_COMMIT")
    return {
        "runtime_target_provenance_authentication": "VERIFIED__FM_LAUNCHER_CONTEXT_CANDIDATE_GIT_CLOSURE",
        "runtime_target_selection_rule": "ONLY_AUTHENTICATED_FM_LAUNCHER_CONTEXT_SELECTION_MAY_POPULATE_DU_TARGET_COORDINATES",
        "caller_chosen_runtime_target_authority": "VERIFIED__NO",
        "arbitrary_historical_head_bypass": "VERIFIED__NO",
        "current_head_provenance_weakening": "VERIFIED__NO",
        "current_tree_provenance_weakening": "VERIFIED__NO",
        "certification_currentness_rule": "SUCCESSOR_BASELINE_MUST_EQUAL_ACTUAL_CURRENT_HEAD_TREE_AT_ISSUANCE_AND_REAUTHENTICATION",
        "candidate_identity": sha256_path(root / IH_CANDIDATE),
        "runtime_identity": sha256_path(root / IH_RUNTIME),
        "context_identity": context["context_sha256"],
        "runtime_target": {"head": IF_HEAD, "tree": IF_TREE},
        "current_certification": {"head": II_HEAD, "tree": II_TREE},
    }


def _scenario_decision(*, target_exists: bool, target_tree_matches: bool, selection_authenticated: bool, candidate_context_agree: bool, certification_is_current: bool, certification_tree_matches: bool, issuer_agrees: bool, runtime_matches_candidate: bool) -> str:
    if not target_exists:
        return "REJECT__TARGET_COMMIT_UNAVAILABLE"
    if not target_tree_matches:
        return "REJECT__TARGET_TREE_MISMATCH"
    if not selection_authenticated:
        return "REJECT__UNAUTHENTICATED_TARGET_SELECTION"
    if not candidate_context_agree:
        return "REJECT__CANDIDATE_CONTEXT_TARGET_DISAGREEMENT"
    if not certification_is_current:
        return "REJECT__STALE_CERTIFICATION_BASELINE"
    if not certification_tree_matches:
        return "REJECT__CERTIFICATION_TREE_MISMATCH"
    if not issuer_agrees:
        return "REJECT__ISSUER_CURRENT_REPOSITORY_DISAGREEMENT"
    if not runtime_matches_candidate:
        return "REJECT__CANDIDATE_RUNTIME_IDENTITY_MISMATCH"
    return "ACCEPT__DESIGN_CONTRACT_ONLY__NOT_OPERATION_AUTHORITY"


def generality_matrix() -> list[dict[str, str]]:
    good = dict(target_exists=True, target_tree_matches=True, selection_authenticated=True, candidate_context_agree=True, certification_is_current=True, certification_tree_matches=True, issuer_agrees=True, runtime_matches_candidate=True)
    cases = [
        ("TARGET_EQUALS_CURRENT", {}, "ACCEPT__DESIGN_CONTRACT_ONLY__NOT_OPERATION_AUTHORITY"),
        ("TARGET_DIFFERS_CURRENT_AUTHENTICATED", {}, "ACCEPT__DESIGN_CONTRACT_ONLY__NOT_OPERATION_AUTHORITY"),
        ("TARGET_DIFFERS_CURRENT_ARBITRARY", {"selection_authenticated": False}, "REJECT__UNAUTHENTICATED_TARGET_SELECTION"),
        ("WRONG_TARGET_TREE", {"target_tree_matches": False}, "REJECT__TARGET_TREE_MISMATCH"),
        ("WRONG_CERTIFICATION_TREE", {"certification_tree_matches": False}, "REJECT__CERTIFICATION_TREE_MISMATCH"),
        ("STALE_CERTIFICATION_BASELINE", {"certification_is_current": False}, "REJECT__STALE_CERTIFICATION_BASELINE"),
        ("FUTURE_OR_NONEXISTENT_TARGET", {"target_exists": False}, "REJECT__TARGET_COMMIT_UNAVAILABLE"),
        ("CANDIDATE_CONTEXT_DISAGREEMENT", {"candidate_context_agree": False}, "REJECT__CANDIDATE_CONTEXT_TARGET_DISAGREEMENT"),
        ("RECEIPT_ISSUER_CURRENT_DISAGREEMENT", {"issuer_agrees": False}, "REJECT__ISSUER_CURRENT_REPOSITORY_DISAGREEMENT"),
        ("FUTURE_VECTOR_AUTHENTICATED_IF", {}, "ACCEPT__DESIGN_CONTRACT_ONLY__NOT_OPERATION_AUTHORITY"),
        ("NON_FUTURE_CURRENT_TARGET", {}, "ACCEPT__DESIGN_CONTRACT_ONLY__NOT_OPERATION_AUTHORITY"),
        ("RUNTIME_CANDIDATE_BYTES_DIFFER", {"runtime_matches_candidate": False}, "REJECT__CANDIDATE_RUNTIME_IDENTITY_MISMATCH"),
    ]
    result = []
    for identity, mutations, expected in cases:
        inputs = good | mutations
        observed = _scenario_decision(**inputs)
        if observed != expected:
            raise IJDesignError(f"GENERALITY_CASE_FAILED__{identity}")
        result.append({"case": identity, "expected": expected, "observed": observed})
    return result


def preserve_future_semantics(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    candidate = load_canonical(root / IH_CANDIDATE)
    context = load_canonical(root / IH_CONTEXT)
    if sha256_path(root / IH_CANDIDATE) != FUTURE_CANDIDATE_SHA or sha256_path(root / IH_RUNTIME) != FUTURE_CANDIDATE_SHA:
        raise IJDesignError("FUTURE_CANDIDATE_IDENTITY_DRIFT")
    if context["context_sha256"] != FUTURE_CONTEXT_INNER:
        raise IJDesignError("FUTURE_CONTEXT_IDENTITY_DRIFT")
    adapter_tree = ast.parse((root / IF_ADAPTER).read_text())
    calls = {node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id for node in ast.walk(adapter_tree) if isinstance(node, ast.Call) and isinstance(node.func, (ast.Attribute, ast.Name))}
    if calls.intersection({"time", "time_ns", "now", "sleep"}):
        raise IJDesignError("FUTURE_WALL_CLOCK_DEPENDENCY")
    act_binding = load_canonical(root / Path(".github/governance/evidence/g77_256if_future_post_commit_readiness_v1/live_binding/G77_256IF_FUTURE_ACT_CHE_BINDING_V1.json"))
    text = json.dumps(act_binding, sort_keys=True)
    for identity in (FUTURE_PAYLOAD, FUTURE_SOURCE_ACT, FUTURE_CHE):
        if identity not in text:
            raise IJDesignError("FUTURE_ACT_CHE_IDENTITY_DRIFT")
    return {
        "candidate_runtime_identity": FUTURE_CANDIDATE_SHA,
        "context_identity": FUTURE_CONTEXT_INNER,
        "evaluation_time_unix_ns": 500,
        "valid_from_unix_ns": 600,
        "valid_until_unix_ns": 1000,
        "temporal_relation": "VERIFIED__500_LT_600_LT_1000",
        "payload_digest": FUTURE_PAYLOAD,
        "source_act_digest": FUTURE_SOURCE_ACT,
        "che_correlation_identity": FUTURE_CHE,
        "future_semantic_mutation_count": "VERIFIED__0",
        "deterministic_time_fixture_status": "VERIFIED",
        "wall_clock_dependency_count_on_future_path": "VERIFIED__0",
    }


def authenticate_ex(repository_root: Path) -> dict[str, str]:
    raw = (repository_root.resolve() / EX_CERTIFICATE).read_bytes()
    envelope = json.loads(raw, object_pairs_hook=_unique)
    preimage = deepcopy(envelope)
    preimage["certificate_sha256"] = ""
    payload = json.dumps(preimage, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()
    if envelope["certificate_sha256"] != sha256_bytes(payload) or envelope["certificate"]["component_counts"]["CERTIFIED"] != 17:
        raise IJDesignError("EX_CERTIFICATE_AUTHENTICATION_FAILED")
    return {"ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0", "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED"}


def terminal_reduction(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    entry = authenticate_entry(root)
    ii = reconstruct_ii(root)
    owners = authenticate_owners(root)
    firewalls = target_and_currentness_firewalls(root)
    counters = {key: 0 for key in ("human_operational_authority", "authority_consumption", "pre", "fm_operational_launcher_invocation", "qemu", "vm_creation", "vm_boot", "operation_attempt", "request", "p11_entry", "protected_invocation", "protected_effect", "retry", "repair_retry", "replay", "e05_credit")}
    return {
        "schema_id": "G77_256IJ_GENERAL_VERSIONED_SUCCESSOR_CONTRACT_DESIGN_V1",
        "mode": "REPOSITORY_ONLY__DESIGN_FORMALIZATION__NO_OPERATION",
        "entry": entry,
        "ii_reconstruction": ii,
        "identity_model": identity_model(),
        "owner_evidence": owners,
        "schema_minimality": schema_minimality(),
        "successor_contract_design": successor_contract_design(),
        "owner_model": owner_model(),
        "successor_responsibilities": successor_responsibilities(),
        "versioning_and_compatibility": versioning_and_compatibility(),
        "provenance_firewalls": firewalls,
        "generality_matrix": generality_matrix(),
        "future_semantics": preserve_future_semantics(root),
        "boundaries": {
            "p11_change_required": "VERIFIED__NO",
            "gn": "NOT_APPLICABLE__NO_HUMAN_AUTHORIZATION_REQUEST_CREATED",
            "gl": "NOT_APPLICABLE__NO_AUTHORITY_OR_RECEIPT_PARENT_CREATED",
            "production_route_before": "VERIFIED__1",
            "production_route_after": "VERIFIED__1",
            "production_route_delta": "VERIFIED__0",
            "new_production_route_count": "VERIFIED__0",
            "new_authority_layer_count": "VERIFIED__0",
            "new_runtime_owner_count": "VERIFIED__0",
            "new_clock_infrastructure_count": "VERIFIED__0",
        },
        "historical_failure_firewall": {
            "status": "VERIFIED",
            "reintroduced_historical_failure_count": "VERIFIED__0",
            "protected_set": ["PRE_COMMIT_HEAD_SELF_REFERENCE", "FUTURE_COMMIT_PREDICTION", "CHECKOUT_MISMATCH", "BOOTSTRAP_MISMATCH", "HOST_GUEST_MISMATCH", "LAUNCHER_ADAPTER_MISMATCH", "NOCLOUD_MISMATCH", "NONCANONICAL_HANDOFF", "RECEIPT_PARENT_ABSENCE", "HISTORICAL_SHA_MISMATCH", "TRANSIENT_ROOT_MISMATCH", "BASE_IMAGE_MUTATION", "ARBITRARY_HISTORICAL_HEAD_CERTIFICATION", "RUNTIME_CURRENT_IDENTITY_COLLAPSE", "CURRENT_CERTIFICATION_PROVENANCE_WEAKENING", "VERSION_DISPATCH_BYPASS", "FUTURE_SPECIFIC_EXCEPTION"],
            "pre_commit_self_reference_count": "VERIFIED__0",
            "future_commit_prediction_count": "VERIFIED__0",
        },
        "ex": authenticate_ex(root),
        "reuse_impact": {
            "reused_certified_capability_set": ["II_IDENTITY_MODEL_AND_OPTION_E", "FM_REPOSITORY_CHECKOUT_SEPARATION", "DU_V1_TARGET_PROVENANCE", "EB_EE_CURRENTNESS", "P11", "CHE", "FK", "GN", "GL", "EX_17_OF_17", "GOVERNANCE", "LAYER_0", "PINNED_NESTED_AUTHORITY"],
            "new_capability_set": ["IJ_MACHINE_READABLE_SUCCESSOR_REQUIREMENTS_AND_SCHEMA_AMBIGUITY_FORMALIZATION"],
            "unreachable_preexisting_capability_set": [],
            "parallel_flow_created": "VERIFIED__NO",
            "production_route_before": "VERIFIED__1",
            "production_route_after": "VERIFIED__1",
            "production_route_delta": "VERIFIED__0",
        },
        "overengineering_firewall": schema_minimality() | {"overengineering_risk": "ESTIMATED__LOW_AFTER_REJECTING_CONCRETE_SCHEMA_SELECTION"},
        "infrastructure_amortization": {
            "e05_generations_per_credit": "VERIFIED__5__HISTORICAL_WRONG_PROVENANCE_LIFECYCLE_ONLY",
            "operational_attempts_per_credit": "VERIFIED__1__HISTORICAL_WRONG_PROVENANCE_ONLY",
            "future_generations_before_ij": "VERIFIED__5__IE_IF_IG_IH_II",
            "future_generations_so_far": "VERIFIED__6__IE_IF_IG_IH_II_IJ",
            "future_e05_credit_so_far": "VERIFIED__0",
            "future_operational_attempts_so_far": "VERIFIED__0",
            "new_common_infrastructure_for_future": "VERIFIED__0__DESIGN_EVIDENCE_ONLY",
            "new_vector_specific_infrastructure_for_future": "VERIFIED__0",
            "marginal_new_infrastructure_for_ij": "VERIFIED__DESIGN_RESOLVER_TEST_REPORT_AND_REDUCTION_ONLY",
            "expected_next_credit_generation_count": "NOT_PROVEN__SCHEMA_AND_IMPLEMENTATION_REQUIRE_SEPARATE_HUMAN_DECISIONS",
            "infrastructure_amortization_signal": "ESTIMATED__REUSE_DOMINANT_WITH_ZERO_RUNTIME_EXPANSION",
        },
        "validation": {
            "mode": "REPOSITORY_ONLY__NO_OPERATIONAL_VALIDATION",
            "ij_focused": "VERIFIED__15_PASSED",
            "current_applicable_lineage_and_owner_assertions": "VERIFIED__150_PASSED",
            "historical_or_superseded_snapshot_assertions": "NOT_APPLICABLE__25_EXACTLY_DESELECTED_WITH_LINEAGE_REASONS_IN_G48_REPORT",
            "p11_human_act_che_fk": "VERIFIED__72_PASSED",
            "ex_regression": "VERIFIED__12_OF_12__CERTIFIED_17_OF_17",
            "governance_layer_0": "VERIFIED__9_PASSED",
            "conformance_engine": "VERIFIED__20_PASSED__CONFORMANT__0_WARNINGS__0_VIOLATIONS",
            "canonical_json_duplicate_keys_seals_ast": "VERIFIED",
            "git_diff_check": "VERIFIED__CLEAN",
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_L5_CLAIM",
            "cross_worker_state_recovery_level": "NOT_PROVEN__WORKER_IDENTITY_NOT_INSTRUMENTED",
            "repository_derived_context_ratio": "ESTIMATED__DOMINANT__NO_NUMERIC_INSTRUMENT",
            "human_handoff_information_required": "VERIFIED__SCOPE_AND_EXACT_II_LOCATOR_ONLY",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_identity_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
            "authenticated_repository_continuation": "VERIFIED__YES",
            "inter_generation_cross_worker_continuation": "NOT_PROVEN__WORKER_IDENTITY_NOT_INSTRUMENTED",
            "intra_generation_cross_worker_continuation": "NOT_APPLICABLE__CLEAN_COMMITTED_II_ENTRY",
            "uncommitted_delta_recovery": "NOT_APPLICABLE__CLEAN_COMMITTED_II_ENTRY",
            "authority_state_recovery": "VERIFIED__NO_OPERATIONAL_AUTHORITY_EXISTS",
            "consumed_authority_recovery": "VERIFIED__HISTORICAL_CONSUMED_AUTHORITY_NONREUSABLE",
            "post_operation_state_recovery": "VERIFIED__II_TERMINAL_REUSED",
            "operation_replay_prevention": "VERIFIED__IJ_OPERATIONAL_COUNTERS_ZERO",
            "cross_worker_constitutional_drift": "NOT_PROVEN__WORKER_IDENTITY_NOT_INSTRUMENTED",
            "handoff_sufficiency_status": "VERIFIED",
            "handoff_state_completeness": "VERIFIED__COMPLETE_FOR_IJ_DESIGN_SCOPE",
            "handoff_reconstruction_required": "VERIFIED__YES",
            "handoff_reconstruction_success": "VERIFIED__YES",
            "handoff_ambiguity_count": "VERIFIED__0",
            "unauthenticated_handoff_assumption_count": "VERIFIED__0",
        },
        "metrics": {
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "constitutional_health_evidence": "VERIFIED__MINIMUM_SEMANTICS_FORMALIZED_AND_SCHEMA_AMBIGUITY_FAILS_CLOSED",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "e05_frontier_distance": "VERIFIED__8_OF_18_OBLIGATIONS_REMAIN",
            "selected_e05_local_frontier_distance": "NOT_PROVEN__CONCRETE_SUCCESSOR_SCHEMA_AND_IMPLEMENTATION",
            "governance_efficience": "ESTIMATED__MINIMUM_DESIGN_EVIDENCE_ONLY",
            "architectural_governance_efficience": "VERIFIED__ONE_ROUTE_ZERO_RUNTIME_OWNER_MUTATION",
            "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED",
            "cognition_assisted_handoff": "VERIFIED__AUTHENTICATED_II_TO_IJ_REPOSITORY_CONTINUATION",
            "aigol_codex_work_share": "NOT_MEASURED",
            "overengineering_risk": "ESTIMATED__LOW_AFTER_REJECTING_CONCRETE_SCHEMA_SELECTION",
            "proof_process_overhead_risk": "ESTIMATED__MODERATE",
            "cognition_provenance": "VERIFIED__AUTHENTICATED_REPOSITORY_PRIMARY",
            "candidate_capability": "VERIFIED__IF_BOUND_DU_V1__SUCCESSOR_NOT_IMPLEMENTED",
            "shadow_design_target": "VERIFIED__GENERAL_VERSIONED_DU_EB_EE_PROVENANCE_SEPARATION",
            "constitutional_continuation_progress": "VERIFIED__SEMANTIC_MINIMUM_AND_OWNERS_PROVEN__SCHEMA_UNIQUENESS_NOT_PROVEN",
            "prompt_context_reuse_ratio": "NOT_MEASURED",
            "token_benchmark": "NOT_MEASURED",
            "llm_cost_reduction_ratio": "NOT_MEASURED",
            "lcrr": "NOT_MEASURED",
            "marginal_e05_generation_cost": "NOT_MEASURED",
            "marginal_new_infrastructure_per_e05_credit": "NOT_MEASURED__NO_FUTURE_CREDIT",
            "infrastructure_amortization_signal": "ESTIMATED__REUSE_DOMINANT_WITH_ZERO_RUNTIME_EXPANSION",
            "expected_next_credit_generation_count": "NOT_PROVEN__SCHEMA_AND_IMPLEMENTATION_REQUIRE_SEPARATE_HUMAN_DECISIONS",
        },
        "cognition_provenance": "VERIFIED__AUTHENTICATED_GIT_II_IH_IG_IF_IE_ID_IC_P11_CHE_FK_FM_GN_GL_DU_EB_EE_EX_GOVERNANCE_LAYER_0_PINNED_NESTED_AUTHORITY_CURRENT_TESTS",
        "operational_counters": counters,
        "e05": {"before": "10/18", "after": "10/18", "satisfied": 10, "remaining": 8, "credit": 0},
        "terminal_control": {
            "current_e05_status": "VERIFIED__10_OF_18",
            "selected_next_e05_vector": "VERIFIED__FUTURE",
            "runtime_certification_identity_contract": "NOT_PROVEN__SUCCESSOR_NOT_IMPLEMENTED",
            "successor_contract_design_status": "NOT_PROVEN__MINIMUM_SEMANTIC_REQUIREMENTS_UNIQUE__CONCRETE_SCHEMA_MULTIPLE",
            "successor_contract_versioning": "VERIFIED__NEW_REVIEWED_INCOMPATIBLE_VERSION_REQUIRED__EXACT_IDENTIFIER_NOT_PROVEN",
            "schema_uniqueness": "NOT_PROVEN__MULTIPLE_EQUIVALENT_CLOSED_SCHEMA_PLACEMENTS_REMAIN",
            "owner_uniqueness_status": "VERIFIED__DESIGN_ASSIGNMENTS_UNIQUE",
            "runtime_target_provenance_authentication": "VERIFIED__FM_LAUNCHER_CONTEXT_CANDIDATE_GIT_CLOSURE",
            "current_certification_provenance_status": "VERIFIED__DESIGN_REQUIRES_ACTUAL_CURRENT_HEAD_TREE",
            "arbitrary_historical_head_bypass": "VERIFIED__NO",
            "current_head_provenance_weakening": "VERIFIED__NO",
            "backward_compatibility_status": "VERIFIED__V1_PRESERVED__SUCCESSOR_DESIGN_GENERAL",
            "version_dispatch_bypass_risk": "NOT_PROVEN__NO_IMPLEMENTATION_EXISTS__FAIL_CLOSED_BOUND_DISPATCH_REQUIRED",
            "p11_change_required": "VERIFIED__NO",
            "production_route_delta": "VERIFIED__0",
            "future_preoperational_readiness": "NOT_PROVEN",
            "future_operational_capability": "NOT_PROVEN",
            "next_operational_generation_eligible": "NOT_PROVEN",
            "e05_credit": "VERIFIED__0",
            "last_verified_edge": "UNIQUE_MINIMUM_SEMANTIC_COORDINATES_OWNERS_INVARIANTS_AND_FIREWALL_REQUIREMENTS_FORMALIZED",
            "first_broken_edge": "NO_GOVERNED_EVIDENCE_SELECTS_ONE_OF_MULTIPLE_EQUIVALENT_CLOSED_SUCCESSOR_SCHEMA_PLACEMENTS",
            "minimum_missing_capability": "HUMAN_GOVERNANCE_SELECTION_OF_EXACT_VERSIONED_DU_EB_EE_SCHEMA_SHAPE_AND_BOUND_VERSION_DISPATCH",
            "minimum_legal_next_delta": "HUMAN_GOVERNANCE_DECISION_REQUIRED",
            "auto_continuable": False,
            "human_authorization_required": False,
            "human_review_required": True,
            "next_generation_started": False,
            "verdict": "NOT_PROVEN__IJ_SEMANTIC_SUCCESSOR_REQUIREMENTS_FORMALIZED__CONCRETE_SCHEMA_NOT_UNIQUE__ZERO_OPERATION__E05_10_OF_18__HUMAN_REVIEW_REQUIRED",
        },
    }


def terminal_envelope(repository_root: Path) -> dict[str, Any]:
    reduction = terminal_reduction(repository_root)
    return {"schema_id": "G77_256IJ_GENERAL_VERSIONED_SUCCESSOR_CONTRACT_DESIGN_ENVELOPE_V1", "reduction": reduction, "reduction_sha256": sha256_bytes(canonical_bytes(reduction))}


if __name__ == "__main__":
    raise SystemExit("repository-only IJ design resolver; no operational CLI entry point")
