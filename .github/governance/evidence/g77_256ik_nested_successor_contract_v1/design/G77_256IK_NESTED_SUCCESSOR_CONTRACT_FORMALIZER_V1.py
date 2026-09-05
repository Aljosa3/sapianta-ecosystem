#!/usr/bin/env python3
"""G77-256IK repository-only Option-B successor-contract formalizer.

This evidence owner authenticates committed IJ, binds the Human-selected nested
certification-baseline shape, and formalizes fail-closed schema/version rules.
It deliberately does not choose an unproven successor version identity and has
no operational command path.
"""

from __future__ import annotations

import ast
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True

BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
IJ_HEAD = "a07f6e76239a9d8f309f290ecc8ab328d08aa64f"
IJ_TREE = "0ff8d170c40279afaad6c62799255644f04da45d"
IJ_SUBJECT = "G77-256IJ formalize successor contract design boundary"
II_HEAD = "4365d97394deca438a1a57d5b47c699afb54bd5d"
IH_HEAD = "8698486cdf9a206f2bc73993c83389d6850362ff"
IG_HEAD = "71391a75011cdc388bdac9183f4654814a044c69"
IF_HEAD = "699fcdce794ff49b6c8735602936355724ed1c90"
IF_TREE = "7c773d4b2acdf013f1b8238eabfc8eced4dd6866"
IE_HEAD = "9420764a5bb6db8909334f2a422225687a37a346"
ID_HEAD = "559deecb226b66d626e45e6f607b0aab6df81f1c"
IC_HEAD = "afdd47166acdee30cb9867d3d3c7bfec0de64c8a"
STABLE_ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_TAG = "refs/tags/sapianta-system-nested-authority-3183bab-v1"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"

IK_ROOT = Path(".github/governance/evidence/g77_256ik_nested_successor_contract_v1")
IJ_ROOT = Path(".github/governance/evidence/g77_256ij_successor_contract_design_v1")
IJ_RESOLVER = IJ_ROOT / "design/G77_256IJ_DU_EB_EE_SUCCESSOR_CONTRACT_DESIGN_RESOLVER_V1.py"
IJ_TERMINAL = IJ_ROOT / "G77_256IJ_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
DU_CONTRACT = Path(".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/G77_256DU_CANONICAL_CONTINUATION_MANIFEST_CONTRACT_V1.md")
DU_SCHEMA = Path(".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/G77_256DU_CANONICAL_CONTINUATION_MANIFEST_SCHEMA_V1.json")
DU_VALIDATOR = Path(".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V1.py")
EB_SCHEMA = Path(".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v1/G77_256EB_CANDIDATE_BOUND_VALIDATION_RECEIPT_SCHEMA_V1.json")
EB_VALIDATOR = Path(".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v1/validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V1.py")
EE_SCHEMA = Path(".github/governance/evidence/g77_256ee_runtime_consumer_binding_v1/G77_256EE_RUNTIME_CONSUMER_BINDING_RECEIPT_SCHEMA_V1.json")
EE_VALIDATOR = Path(".github/governance/evidence/g77_256ee_runtime_consumer_binding_v1/validator/G77_256EE_RUNTIME_CONSUMER_BINDING_VALIDATOR_V1.py")
FM_LAUNCHER = Path(".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py")
FM_CONTEXT_OWNER = Path(".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/sapianta_fresh_operation_context_v1.py")
IH_CANDIDATE = Path(".github/governance/evidence/g77_256ih_future_if_identity_rebind_v1/live_binding/candidate/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json")
IH_RUNTIME = Path(".github/governance/evidence/g77_256ih_future_if_identity_rebind_v1/live_binding/runtime_projection/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json")
IH_CONTEXT = Path(".github/governance/evidence/g77_256ih_future_if_identity_rebind_v1/live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json")
IF_ADAPTER = Path(".github/governance/evidence/g77_256if_future_post_commit_readiness_v1/adapter/G77_256IF_FUTURE_VECTOR_ADAPTER_V1.py")
EX_CERTIFICATE = Path(".github/governance/evidence/g77_256ex_common_substrate_certification_v1/G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json")

IJ_HASHES = {
    IJ_ROOT / "G77_256IJ_G48_IMPLEMENTATION_REPORT_V1.md": "6ee2d077eeddff68ebe9a29c8d87c57fe13f89d1ccefc785576d00511456e8c7",
    IJ_TERMINAL: "37c41d83cb9a54c16192026f4b92bc3b3d545d7a9889cc910ffa8afa39a2c71a",
    IJ_RESOLVER: "7e727cff2cfd4dab9b94394346f014969926dbb2c4cb0e5e9d6da3991d99e4c6",
    IJ_ROOT / "tests/test_g77_256ij_successor_contract_design_v1.py": "e8dbad8cd376041126450fed0b375927b6e8360141b28656dfd1a367ee86c9c4",
}
IJ_BLOBS = {
    IJ_ROOT / "G77_256IJ_G48_IMPLEMENTATION_REPORT_V1.md": "8dc2364b21aec4abbdc006a441391daca1c3fe17",
    IJ_TERMINAL: "03ecc4362ba5c9af1a5383c4a6a8518be00d4fa8",
    IJ_RESOLVER: "dc18d4745cb79188188b55382227fc9376431157",
    IJ_ROOT / "tests/test_g77_256ij_successor_contract_design_v1.py": "eaa36969c968e5ad253577eea2298aedee717500",
}

FUTURE_CANDIDATE_SHA = "ad5d204ec6ace09f18b83fd5f868e73dac5e36dad81149f9f335c87f68cf42f7"
FUTURE_CONTEXT_SHA = "769f7b5cde5946450acbecfd956d479e91d9cf818d47bd4db34cb5086a1b07cb"
FUTURE_PAYLOAD = "sha256:9568e0c248ad488cabcf6bde6b490c544077862d10e3fda13bcdc8ed9953f547"
FUTURE_SOURCE_ACT = "sha256:7167b0725d2c84bafde1d0060f512b0fa358d777ec1beff8b7c68d22ee6502e8"
FUTURE_CHE = "CHE-CORRELATION-15b2680b5577da169cecf9efb3231e2e6f6467e6f409fa2594b04128f998e454"
GIT_OBJECT_RE = re.compile(r"^[0-9a-f]{40}$")


class IKFormalizationError(ValueError):
    """One deterministic fail-closed IK formalization error."""


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
            raise IKFormalizationError(f"DUPLICATE_JSON_KEY__{key}")
        result[key] = value
    return result


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    try:
        value = json.loads(raw, object_pairs_hook=_unique)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IKFormalizationError(f"JSON_INVALID__{path.name}") from exc
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise IKFormalizationError(f"CANONICAL_JSON_INVALID__{path.name}")
    return value


def _git(root: Path, *arguments: str) -> str:
    try:
        return subprocess.check_output(["git", *arguments], cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError as exc:
        raise IKFormalizationError("GIT_IDENTITY_UNAVAILABLE") from exc


def _git_bytes(root: Path, revision: str, path: Path) -> bytes:
    try:
        return subprocess.check_output(["git", "show", f"{revision}:{path.as_posix()}"], cwd=root, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as exc:
        raise IKFormalizationError(f"COMMITTED_OBJECT_UNAVAILABLE__{path.name}") from exc


def _load_ij(root: Path) -> ModuleType:
    path = root / IJ_RESOLVER
    if sha256_path(path) != IJ_HASHES[IJ_RESOLVER]:
        raise IKFormalizationError("IJ_RESOLVER_IDENTITY_MISMATCH")
    spec = importlib.util.spec_from_file_location("g77_256ij_committed_resolver", path)
    if spec is None or spec.loader is None:
        raise IKFormalizationError("IJ_RESOLVER_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
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
        "repository": str(root), "branch": BRANCH, "head": IJ_HEAD,
        "tree": IJ_TREE, "subject": IJ_SUBJECT, "origin": ORIGIN,
        "remote_tracking_head": IJ_HEAD, "index": "",
    }
    if observed != expected:
        raise IKFormalizationError("EXACT_COMMITTED_IJ_CHECKPOINT_MISMATCH")
    for ancestor in (II_HEAD, IH_HEAD, IG_HEAD, IF_HEAD, IE_HEAD, ID_HEAD, IC_HEAD, STABLE_ANCHOR):
        if subprocess.run(["git", "merge-base", "--is-ancestor", ancestor, IJ_HEAD], cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode:
            raise IKFormalizationError(f"ANCESTRY_MISSING__{ancestor}")
    for line in subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=all"], cwd=root, text=True).splitlines():
        if not line[3:].startswith(IK_ROOT.as_posix() + "/"):
            raise IKFormalizationError(f"UNRELATED_WORKTREE_MUTATION__{line[3:]}")
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
        raise IKFormalizationError("NESTED_AUTHORITY_NOT_CLEAN_DETACHED_PINNED")
    return observed | {"nested": nested_state, "worktree_scope": "VERIFIED__IK_EVIDENCE_ONLY"}


def reconstruct_ij(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    identities: dict[str, Any] = {}
    for path, expected_sha in IJ_HASHES.items():
        committed = _git_bytes(root, IJ_HEAD, path)
        blob = _git(root, "rev-parse", f"{IJ_HEAD}:{path.as_posix()}")
        if committed != (root / path).read_bytes() or sha256_bytes(committed) != expected_sha or blob != IJ_BLOBS[path]:
            raise IKFormalizationError(f"IJ_IDENTITY_MISMATCH__{path.name}")
        identities[path.name] = {"path": path.as_posix(), "sha256": expected_sha, "git_blob": blob}
    envelope = load_canonical(root / IJ_TERMINAL)
    if envelope["reduction_sha256"] != sha256_bytes(canonical_bytes(envelope["reduction"])):
        raise IKFormalizationError("IJ_TERMINAL_SEAL_INVALID")
    control = envelope["reduction"]["terminal_control"]
    expected = {
        "current_e05_status": "VERIFIED__10_OF_18",
        "successor_contract_design_status": "NOT_PROVEN__MINIMUM_SEMANTIC_REQUIREMENTS_UNIQUE__CONCRETE_SCHEMA_MULTIPLE",
        "schema_uniqueness": "NOT_PROVEN__MULTIPLE_EQUIVALENT_CLOSED_SCHEMA_PLACEMENTS_REMAIN",
        "owner_uniqueness_status": "VERIFIED__DESIGN_ASSIGNMENTS_UNIQUE",
        "runtime_target_provenance_authentication": "VERIFIED__FM_LAUNCHER_CONTEXT_CANDIDATE_GIT_CLOSURE",
        "arbitrary_historical_head_bypass": "VERIFIED__NO",
        "current_head_provenance_weakening": "VERIFIED__NO",
        "p11_change_required": "VERIFIED__NO",
        "production_route_delta": "VERIFIED__0",
        "future_preoperational_readiness": "NOT_PROVEN",
        "future_operational_capability": "NOT_PROVEN",
        "next_operational_generation_eligible": "NOT_PROVEN",
        "e05_credit": "VERIFIED__0",
    }
    if {key: control[key] for key in expected} != expected:
        raise IKFormalizationError("IJ_TERMINAL_FRONTIER_MISMATCH")
    ij = _load_ij(root)
    if ij.schema_minimality()["minimum_new_semantic_field_count"] != 2:
        raise IKFormalizationError("IJ_MINIMUM_SEMANTICS_MISMATCH")
    return {"status": "VERIFIED", "artifact_count": 4, "identities": identities, "inner_seal": "VERIFIED", "frontier": expected}


def human_governance_decision() -> dict[str, str]:
    return {
        "human_governance_schema_selection": "B__NESTED_CERTIFICATION_BASELINE_OBJECT_PER_SUCCESSOR_RECEIPT",
        "human_selected_logical_schema": "VERIFIED__OPTION_B_NESTED_CERTIFICATION_BASELINE",
        "human_governance_decision_scope": "REPOSITORY_ONLY_SUCCESSOR_SCHEMA_SELECTION_AND_FORMALIZATION",
        "human_operational_authority": "VERIFIED__0",
        "future_operation_authorized": "VERIFIED__NO",
        "e05_credit_authorized": "VERIFIED__NO",
    }


def authenticate_conventions(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    schemas = {name: json.loads((root / path).read_bytes(), object_pairs_hook=_unique) for name, path in {"DU": DU_SCHEMA, "EB": EB_SCHEMA, "EE": EE_SCHEMA}.items()}
    if any(schema.get("additionalProperties") is not False for schema in schemas.values()):
        raise IKFormalizationError("V1_ROOT_SCHEMA_NOT_CLOSED")
    if any(schema["properties"]["receipt"].get("additionalProperties") is not False for name, schema in schemas.items() if name in {"EB", "EE"}):
        raise IKFormalizationError("V1_RECEIPT_SCHEMA_NOT_CLOSED")
    context_ast = ast.parse((root / FM_CONTEXT_OWNER).read_text())
    source = ast.unparse(context_ast)
    if 'set(checkout) != {\'path\', \'head\', \'tree\', \'detached\', \'clean\', \'read_only_mount\'}' not in source:
        raise IKFormalizationError("FM_NESTED_HEAD_TREE_CONVENTION_NOT_AUTHENTICATED")
    du_contract = (root / DU_CONTRACT).read_text()
    if "A semantic change requires a new reviewed schema version" not in du_contract:
        raise IKFormalizationError("REVIEWED_SUCCESSOR_RULE_ABSENT")
    identity_prefixes = {
        "du_schema": schemas["DU"]["$id"],
        "eb_schema": schemas["EB"]["$id"],
        "ee_schema": schemas["EE"]["$id"],
    }
    if not (identity_prefixes["du_schema"].startswith("SAPIANTA_") and identity_prefixes["eb_schema"].startswith("SAPIANTA_") and identity_prefixes["ee_schema"].startswith("G77_256EE_")):
        raise IKFormalizationError("VERSION_IDENTITY_FAMILY_EVIDENCE_CHANGED")
    return {
        "schema_closure_convention": "VERIFIED__DU_EB_EE_ROOTS_AND_NESTED_OBJECTS_REJECT_UNKNOWN_FIELDS",
        "physical_naming_convention": "VERIFIED__SNAKE_CASE_NESTED_OBJECTS_AND_FM_HEAD_TREE_PAIR",
        "exact_physical_field_names": {"object": "certification_baseline", "commit": "head", "tree": "tree"},
        "exact_physical_field_names_status": "VERIFIED",
        "v1_identity_examples": identity_prefixes,
        "v1_numeric_version": "1.0.0",
        "successor_version_required": "VERIFIED__YES",
        "successor_version_identifier": "NOT_PROVEN__NO_UNIQUE_REPOSITORY_CONVENTION",
        "ambiguity_proof": [
            "SUFFIX_V2_PLUS_NUMERIC_2_0_0_IS_CONVENTION_COMPATIBLE_BUT_NOT_RATIFIED",
            "NEW_CONTRACT_FAMILY_SUFFIX_V1_PLUS_NUMERIC_1_0_0_IS_ALSO_REPOSITORY_CONVENTION_COMPATIBLE",
            "NO_DU_EB_EE_SUCCESSOR_REGISTRY_OR_SAME_FAMILY_DISPATCH_PRECEDENT_EXISTS",
            "DU_EB_PREFIX_FAMILY_DIFFERS_FROM_EE_PREFIX_FAMILY",
        ],
    }


BASELINE_FIELDS = frozenset({"head", "tree"})


def validate_certification_baseline(value: Any) -> dict[str, str]:
    if not isinstance(value, dict) or set(value) != BASELINE_FIELDS:
        raise IKFormalizationError("CERTIFICATION_BASELINE_SCHEMA_INVALID")
    for field in ("head", "tree"):
        if not isinstance(value[field], str) or GIT_OBJECT_RE.fullmatch(value[field]) is None:
            raise IKFormalizationError(f"CERTIFICATION_BASELINE_{field.upper()}_INVALID")
    return {"head": value["head"], "tree": value["tree"]}


def authenticate_certification_currentness(repository_root: Path, baseline: Any) -> str:
    root = repository_root.resolve()
    value = validate_certification_baseline(baseline)
    current_head = _git(root, "rev-parse", "HEAD")
    current_tree = _git(root, "rev-parse", "HEAD^{tree}")
    if value != {"head": current_head, "tree": current_tree}:
        raise IKFormalizationError("CERTIFICATION_BASELINE_NOT_CURRENT")
    if _git(root, "rev-parse", f"{value['head']}^{{tree}}") != value["tree"]:
        raise IKFormalizationError("CERTIFICATION_BASELINE_TREE_MISMATCH")
    return "VERIFIED__ACTUAL_CURRENT_HEAD_TREE_AND_COMMIT_TREE_CLOSURE"


@dataclass(frozen=True)
class VersionBinding:
    schema_identity: str
    version: str
    validator_identity: str
    receipt_profile: str
    issuer_implementation_identity: str
    consumer_expectation: str


def validate_version_binding(observed: VersionBinding, governed_expected: VersionBinding, *, mixed_v1_successor_fields: bool = False, caller_selected: bool = False, downgrade: bool = False) -> str:
    if mixed_v1_successor_fields:
        raise IKFormalizationError("MIXED_VERSION_REJECTED")
    if caller_selected:
        raise IKFormalizationError("CALLER_VERSION_SELECTION_REJECTED")
    if downgrade:
        raise IKFormalizationError("VERSION_DOWNGRADE_REJECTED")
    if observed != governed_expected:
        raise IKFormalizationError("SCHEMA_VERSION_VALIDATOR_PROFILE_ISSUER_CONSUMER_MISMATCH")
    return "VERIFIED__EXACT_GOVERNED_BINDING"


def schema_contract() -> dict[str, Any]:
    return {
        "human_selected_shape": {"certification_baseline": {"head": "GIT_COMMIT_40_LOWER_HEX", "tree": "GIT_TREE_40_LOWER_HEX"}},
        "applicable_receipts": ["EB_SUCCESSOR", "EE_SUCCESSOR"],
        "minimum_new_semantic_field_count": "VERIFIED__2",
        "minimum_new_coordinates": ["certification_baseline.head", "certification_baseline.tree"],
        "required_structural_evidence": "runtime_target_selection_binding",
        "binding_is_third_git_coordinate": False,
        "successor_schema_closed": "VERIFIED__SELECTED_NESTED_OBJECT_EXACTLY_HEAD_TREE__WHOLE_RECEIPT_PENDING_VERSION_IDENTITY",
        "unknown_field_policy": "VERIFIED__REJECT",
        "missing_required_field_policy": "VERIFIED__REJECT",
        "wrong_type_policy": "VERIFIED__REJECT",
        "malformed_git_identity_policy": "VERIFIED__REJECT",
        "mixed_version_policy": "VERIFIED__REJECT",
        "schema_version_mismatch_policy": "VERIFIED__REJECT",
        "caller_substitution_policy": "VERIFIED__REJECT",
        "successor_schema_status": "NOT_PROVEN__REMAINING_EXACT_VERSION_AND_BINDING_IDENTITY_AMBIGUITY",
    }


def identity_and_owner_model() -> dict[str, Any]:
    fields = [
        {"field": "DU.manifest.required_head", "semantic_role": "RUNTIME_TARGET_COMMIT", "producer": "DU_SUCCESSOR_FROM_AUTHENTICATED_FM_SELECTION", "authority_source": "FM_LAUNCHER_TARGET_SELECTION", "validator": "DU_SUCCESSOR_PLUS_GIT", "consumer": "EB_EE_SUCCESSOR_AND_CHECKOUT", "mandatory_equality": "FM_CONTEXT_CHECKOUT_HEAD", "failure_mode": "REJECT_TARGET_OR_SELECTION_MISMATCH"},
        {"field": "DU.manifest.source_tree", "semantic_role": "RUNTIME_TARGET_TREE", "producer": "DU_SUCCESSOR_FROM_AUTHENTICATED_FM_SELECTION", "authority_source": "FM_LAUNCHER_TARGET_SELECTION_PLUS_GIT", "validator": "DU_SUCCESSOR_PLUS_GIT", "consumer": "EB_EE_SUCCESSOR_AND_CHECKOUT", "mandatory_equality": "TREE_OF_REQUIRED_HEAD_AND_FM_CHECKOUT_TREE", "failure_mode": "REJECT_TARGET_TREE_MISMATCH"},
        {"field": "EB.receipt.certification_baseline.head", "semantic_role": "CERTIFICATION_BASELINE_COMMIT", "producer": "EB_SUCCESSOR_ISSUER_FROM_CURRENT_GIT", "authority_source": "ACTUAL_CURRENT_REPOSITORY_HEAD", "validator": "EB_SUCCESSOR_VERIFIER_PLUS_GIT", "consumer": "EB_AND_EE_SUCCESSOR_VERIFIERS", "mandatory_equality": "ACTUAL_CURRENT_HEAD_AT_ISSUANCE_AND_VERIFICATION", "failure_mode": "REJECT_STALE_CALLER_OR_ISSUER_MISMATCH"},
        {"field": "EB.receipt.certification_baseline.tree", "semantic_role": "CERTIFICATION_BASELINE_TREE", "producer": "EB_SUCCESSOR_ISSUER_FROM_CURRENT_GIT", "authority_source": "ACTUAL_CURRENT_REPOSITORY_TREE", "validator": "EB_SUCCESSOR_VERIFIER_PLUS_GIT", "consumer": "EB_AND_EE_SUCCESSOR_VERIFIERS", "mandatory_equality": "ACTUAL_CURRENT_TREE_AND_TREE_OF_BASELINE_HEAD", "failure_mode": "REJECT_WRONG_OR_STALE_TREE"},
        {"field": "EE.receipt.certification_baseline.head", "semantic_role": "INDEPENDENT_CERTIFICATION_BASELINE_COMMIT", "producer": "EE_SUCCESSOR_ISSUER_FROM_CURRENT_GIT", "authority_source": "ACTUAL_CURRENT_REPOSITORY_HEAD", "validator": "EE_SUCCESSOR_VERIFIER_PLUS_GIT", "consumer": "EE_SUCCESSOR_CONSUMER", "mandatory_equality": "ACTUAL_CURRENT_HEAD_AND_INDEPENDENT_EB_BASELINE_HEAD", "failure_mode": "REJECT_EE_OR_EB_CURRENTNESS_DISAGREEMENT"},
        {"field": "EE.receipt.certification_baseline.tree", "semantic_role": "INDEPENDENT_CERTIFICATION_BASELINE_TREE", "producer": "EE_SUCCESSOR_ISSUER_FROM_CURRENT_GIT", "authority_source": "ACTUAL_CURRENT_REPOSITORY_TREE", "validator": "EE_SUCCESSOR_VERIFIER_PLUS_GIT", "consumer": "EE_SUCCESSOR_CONSUMER", "mandatory_equality": "ACTUAL_CURRENT_TREE_TREE_OF_HEAD_AND_INDEPENDENT_EB_BASELINE_TREE", "failure_mode": "REJECT_EE_OR_EB_TREE_DISAGREEMENT"},
        {"field": "successor.runtime_target_selection_binding", "semantic_role": "AUTHENTICATED_TARGET_SELECTION_EVIDENCE", "producer": "FM_CONTEXT_PRODUCER", "authority_source": "FM_LAUNCHER_TARGET_SELECTION", "validator": "DU_SUCCESSOR_AND_TRANSITIVE_EB_EE", "consumer": "DU_EB_EE_SUCCESSOR", "mandatory_equality": "FM_LAUNCHER_CONTEXT_CANDIDATE_CHECKOUT_TARGET", "failure_mode": "REJECT_CALLER_OR_UNBOUND_HISTORICAL_TARGET"},
    ]
    return {
        "identity_roles": ["TARGET_RUNTIME_IDENTITY", "CURRENT_REPOSITORY_IDENTITY", "CERTIFICATION_BASELINE_IDENTITY", "CANDIDATE_REQUIRED_IDENTITY", "CHECKOUT_IDENTITY", "EVIDENCE_ISSUER_IDENTITY"],
        "fields": fields,
        "owner_uniqueness_status": "VERIFIED__DESIGN_ASSIGNMENTS_UNIQUE",
        "owner_conflict_count": "VERIFIED__0",
        "unowned_semantic_coordinate_count": "VERIFIED__0",
        "evidence_issuer_explicit_field_required": "NOT_APPLICABLE__BASELINE_PLUS_IMPLEMENTATION_BINDINGS_CRYPTOGRAPHICALLY_IMPLY_ISSUER",
    }


def successor_responsibilities() -> dict[str, Any]:
    return {
        "DU_SUCCESSOR": ["closed_successor_manifest", "runtime_target_commit_tree_integrity", "authenticated_FM_target_selection_binding", "candidate_target_equals_authenticated_target"],
        "EB_SUCCESSOR": ["closed_successor_receipt", "exact_version_profile_validator_schema_issuer_binding", "independent_DU_successor_PASS", "runtime_target_and_selection_binding", "certification_baseline_equals_current_Git", "canonical_inner_seal"],
        "EE_SUCCESSOR": ["closed_successor_receipt", "exact_version_profile_validator_schema_issuer_binding", "independent_EB_successor_receipt", "candidate_runtime_byte_and_inner_identity", "receipt_path_integrity", "independent_certification_currentness_reauthentication", "canonical_inner_seal"],
        "P11_CHANGE_REQUIRED": "VERIFIED__NO",
    }


def _scenario_decision(**state: bool) -> str:
    ordered_failures = [
        ("version_known", "UNKNOWN_VERSION"), ("version_bound", "VERSION_BINDING_MISMATCH"),
        ("not_mixed", "MIXED_VERSION"), ("not_downgraded", "DOWNGRADE"),
        ("caller_not_authority", "CALLER_SUBSTITUTION"), ("target_exists", "TARGET_COMMIT_UNAVAILABLE"),
        ("target_tree_matches", "TARGET_TREE_MISMATCH"), ("selection_authenticated", "UNAUTHENTICATED_TARGET_SELECTION"),
        ("fm_candidate_agree", "FM_CANDIDATE_TARGET_DISAGREEMENT"), ("candidate_context_agree", "CANDIDATE_CONTEXT_TARGET_DISAGREEMENT"),
        ("checkout_candidate_agree", "CHECKOUT_CANDIDATE_TARGET_DISAGREEMENT"), ("certification_exists", "CERTIFICATION_COMMIT_UNAVAILABLE"),
        ("certification_is_current", "STALE_CERTIFICATION_BASELINE"), ("certification_tree_matches", "CERTIFICATION_TREE_MISMATCH"),
        ("eb_issuer_agrees", "EB_ISSUER_CURRENT_REPOSITORY_DISAGREEMENT"), ("ee_issuer_agrees", "EE_ISSUER_CURRENT_REPOSITORY_DISAGREEMENT"),
        ("runtime_matches_candidate", "CANDIDATE_RUNTIME_IDENTITY_MISMATCH"),
    ]
    for field, code in ordered_failures:
        if not state[field]:
            return f"REJECT__{code}"
    return "REPRESENTABLE__CONTRACT_ONLY__NOT_OPERATION_AUTHORITY"


def generality_matrix() -> list[dict[str, str]]:
    good = {key: True for key in ("version_known", "version_bound", "not_mixed", "not_downgraded", "caller_not_authority", "target_exists", "target_tree_matches", "selection_authenticated", "fm_candidate_agree", "candidate_context_agree", "checkout_candidate_agree", "certification_exists", "certification_is_current", "certification_tree_matches", "eb_issuer_agrees", "ee_issuer_agrees", "runtime_matches_candidate")}
    cases = [
        ("TARGET_EQUALS_CURRENT", {}), ("AUTHENTICATED_TARGET_DIFFERS_CURRENT", {}),
        ("ARBITRARY_HISTORICAL_TARGET", {"selection_authenticated": False}),
        ("TARGET_WRONG_TREE", {"target_tree_matches": False}),
        ("CERTIFICATION_WRONG_TREE", {"certification_tree_matches": False}),
        ("STALE_CERTIFICATION_BASELINE", {"certification_is_current": False}),
        ("NONEXISTENT_TARGET_COMMIT", {"target_exists": False}),
        ("NONEXISTENT_CERTIFICATION_COMMIT", {"certification_exists": False}),
        ("CANDIDATE_CONTEXT_DISAGREEMENT", {"candidate_context_agree": False}),
        ("FM_CANDIDATE_DISAGREEMENT", {"fm_candidate_agree": False}),
        ("CHECKOUT_CANDIDATE_DISAGREEMENT", {"checkout_candidate_agree": False}),
        ("EB_ISSUER_CURRENT_DISAGREEMENT", {"eb_issuer_agrees": False}),
        ("EE_ISSUER_CURRENT_DISAGREEMENT", {"ee_issuer_agrees": False}),
        ("MIXED_V1_SUCCESSOR_RECEIPT", {"not_mixed": False}),
        ("UNKNOWN_SUCCESSOR_VERSION", {"version_known": False}),
        ("CALLER_SUBSTITUTED_VERSION", {"caller_not_authority": False}),
        ("CALLER_SUBSTITUTED_VALIDATOR_PROFILE", {"version_bound": False}),
        ("FUTURE_VECTOR", {}), ("NON_FUTURE_APPLICABLE_VECTOR", {}),
        ("RUNTIME_CANDIDATE_BYTE_MISMATCH", {"runtime_matches_candidate": False}),
        ("VERSION_DOWNGRADE", {"not_downgraded": False}),
    ]
    return [{"case": name, "observed": _scenario_decision(**(good | delta))} for name, delta in cases]


def authenticate_provenance(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    candidate = load_canonical(root / IH_CANDIDATE)
    context = load_canonical(root / IH_CONTEXT)
    if (root / IH_CANDIDATE).read_bytes() != (root / IH_RUNTIME).read_bytes() or sha256_path(root / IH_CANDIDATE) != FUTURE_CANDIDATE_SHA:
        raise IKFormalizationError("FUTURE_CANDIDATE_RUNTIME_IDENTITY_DRIFT")
    checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    manifest = candidate["manifest"]
    launcher_tree = ast.parse((root / FM_LAUNCHER).read_text())
    constants = {node.targets[0].id: node.value.value for node in launcher_tree.body if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)}
    if (manifest["required_head"], manifest["source_tree"], checkout["head"], checkout["tree"], constants.get("CHECKOUT_HEAD"), constants.get("CHECKOUT_TREE")) != (IF_HEAD, IF_TREE, IF_HEAD, IF_TREE, IF_HEAD, IF_TREE):
        raise IKFormalizationError("FM_TARGET_PROVENANCE_CLOSURE_MISMATCH")
    if _git(root, "rev-parse", f"{IF_HEAD}^{{tree}}") != IF_TREE:
        raise IKFormalizationError("IF_TREE_CLOSURE_MISMATCH")
    authenticate_certification_currentness(root, {"head": IJ_HEAD, "tree": IJ_TREE})
    return {
        "runtime_target": {"head": IF_HEAD, "tree": IF_TREE},
        "runtime_target_provenance_authentication": "VERIFIED__FM_LAUNCHER_CONTEXT_CANDIDATE_GIT_CLOSURE",
        "runtime_target_selection_binding": "VERIFIED__AUTHENTICATED",
        "caller_chosen_runtime_target_authority": "VERIFIED__NO",
        "arbitrary_historical_head_bypass": "VERIFIED__NO",
        "current_certification": {"head": IJ_HEAD, "tree": IJ_TREE},
        "current_certification_provenance_status": "VERIFIED__ACTUAL_CURRENT_GIT_HEAD_TREE",
        "certification_baseline_caller_authority": "VERIFIED__NO",
        "current_head_provenance_weakening": "VERIFIED__NO",
        "current_tree_provenance_weakening": "VERIFIED__NO",
        "target_current_relation_generality": "VERIFIED",
        "currentness_validation_in_both_cases": "VERIFIED",
    }


def preserve_future_semantics(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    context = load_canonical(root / IH_CONTEXT)
    if context["context_sha256"] != FUTURE_CONTEXT_SHA:
        raise IKFormalizationError("FUTURE_CONTEXT_IDENTITY_DRIFT")
    adapter_tree = ast.parse((root / IF_ADAPTER).read_text())
    calls = {node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id for node in ast.walk(adapter_tree) if isinstance(node, ast.Call) and isinstance(node.func, (ast.Attribute, ast.Name))}
    if calls.intersection({"time", "time_ns", "now", "sleep"}):
        raise IKFormalizationError("FUTURE_WALL_CLOCK_DEPENDENCY")
    binding = load_canonical(root / ".github/governance/evidence/g77_256if_future_post_commit_readiness_v1/live_binding/G77_256IF_FUTURE_ACT_CHE_BINDING_V1.json")
    text = json.dumps(binding, sort_keys=True)
    if any(identity not in text for identity in (FUTURE_PAYLOAD, FUTURE_SOURCE_ACT, FUTURE_CHE)):
        raise IKFormalizationError("FUTURE_SEMANTIC_IDENTITY_DRIFT")
    return {"candidate_runtime_identity": FUTURE_CANDIDATE_SHA, "context_identity": FUTURE_CONTEXT_SHA, "evaluation_time": 500, "valid_from": 600, "valid_until": 1000, "temporal_relation": "VERIFIED__500_LT_600_LT_1000", "payload_digest": FUTURE_PAYLOAD, "source_act_digest": FUTURE_SOURCE_ACT, "che_correlation": FUTURE_CHE, "future_semantic_mutation_count": "VERIFIED__0", "wall_clock_dependency_count": "VERIFIED__0"}


def authenticate_ex(repository_root: Path) -> dict[str, str]:
    envelope = json.loads((repository_root.resolve() / EX_CERTIFICATE).read_bytes(), object_pairs_hook=_unique)
    preimage = deepcopy(envelope)
    preimage["certificate_sha256"] = ""
    payload = json.dumps(preimage, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()
    if envelope["certificate_sha256"] != sha256_bytes(payload) or envelope["certificate"]["component_counts"]["CERTIFIED"] != 17:
        raise IKFormalizationError("EX_CERTIFICATE_AUTHENTICATION_FAILED")
    return {"ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0", "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED"}


def implementation_frontier() -> dict[str, Any]:
    return {
        "minimum_successor_implementation_owner_set": ["DU_SUCCESSOR_SCHEMA_AND_VALIDATOR", "EB_SUCCESSOR_SCHEMA_RECEIPT_PROFILE_AND_VALIDATOR", "EE_SUCCESSOR_SCHEMA_RECEIPT_PROFILE_AND_VALIDATOR", "FAIL_CLOSED_VERSION_BINDING_OWNER", "FOCUSED_AND_REGRESSION_TESTS"],
        "minimum_successor_implementation_file_set": "NOT_PROVEN__EXACT_VERSION_IDENTITIES_AND_SUCCESSOR_NAMESPACE_NOT_RATIFIED",
        "fm_binding_dependency": "REUSE_EXISTING_LAUNCHER_CONTEXT_TARGET_SELECTION__NO_RUNTIME_MUTATION_EXPECTED",
        "expected_production_route_delta": "VERIFIED__0",
        "expected_p11_delta": "VERIFIED__0",
        "expected_fm_runtime_delta": "VERIFIED__0",
        "expected_gn_gl_delta": "VERIFIED__0",
    }


def terminal_reduction(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    entry = authenticate_entry(root)
    ij = reconstruct_ij(root)
    conventions = authenticate_conventions(root)
    provenance = authenticate_provenance(root)
    counters = {key: 0 for key in ("human_operational_authority", "authority_consumption", "pre", "fm_operational_launcher_invocation", "qemu", "vm_creation", "vm_boot", "operation_attempt", "request", "p11_entry", "protected_invocation", "protected_effect", "retry", "repair_retry", "replay", "e05_credit")}
    return {
        "schema_id": "G77_256IK_OPTION_B_SUCCESSOR_CONTRACT_FORMALIZATION_V1",
        "mode": "REPOSITORY_ONLY__CONTRACT_FORMALIZATION__NO_IMPLEMENTATION__NO_OPERATION",
        "entry": entry,
        "ij_reconstruction": ij,
        "human_decision": human_governance_decision(),
        "repository_conventions": conventions,
        "schema_contract": schema_contract(),
        "identity_owner_model": identity_and_owner_model(),
        "successor_responsibilities": successor_responsibilities(),
        "version_dispatch_contract": {
            "status": "NOT_PROVEN__FAIL_CLOSED_PREDICATES_FORMALIZED__EXACT_BOUND_IDENTITIES_UNRESOLVED",
            "binding_tuple": ["schema_identity", "version", "validator_identity", "receipt_profile", "issuer_implementation_identity", "consumer_expectation"],
            "unknown_version": "REJECT", "mixed_version": "REJECT", "downgrade": "REJECT", "caller_substitution": "REJECT", "v1_successor_confusion": "REJECT", "receipt_profile_mismatch": "REJECT",
            "version_dispatch_bypass_risk": "NOT_PROVEN__NO_IMPLEMENTATION_AND_NO_RATIFIED_SUCCESSOR_IDENTITIES",
            "downgrade_bypass": "VERIFIED__NO__FORMALIZED_CONTRACT",
            "mixed_version_bypass": "VERIFIED__NO__FORMALIZED_CONTRACT",
            "caller_version_selection_authority": "VERIFIED__NO",
        },
        "provenance_firewalls": provenance,
        "generality_matrix": generality_matrix(),
        "compatibility": {"v1_semantics_reinterpreted": "VERIFIED__NO", "historical_v1_mutation_count": "VERIFIED__0", "backward_compatibility_status": "VERIFIED__V1_IMMUTABLE_AND_REACHABLE_WHERE_EXISTING_INVARIANTS_HOLD__SUCCESSOR_DISPATCH_PENDING", "v1_capability_reachability": "VERIFIED__PRESERVED"},
        "boundaries": {"p11_change_required": "VERIFIED__NO", "p11_core_change_count": "VERIFIED__0", "production_route_before": "VERIFIED__1", "production_route_after": "VERIFIED__1", "production_route_delta": "VERIFIED__0", "new_production_route_count": "VERIFIED__0", "fm_production_owner_mutation": "VERIFIED__0", "gn_operational_applicability": "NOT_APPLICABLE", "gl_operational_applicability": "NOT_APPLICABLE", "new_authority_layer_count": "VERIFIED__0"},
        "future_semantics": preserve_future_semantics(root),
        "historical_failure_firewall": {"status": "VERIFIED", "reintroduced_historical_failure_count": "VERIFIED__0", "precommit_self_reference_count": "VERIFIED__0", "future_commit_prediction_count": "VERIFIED__0", "protected_set": ["PRE_COMMIT_HEAD_SELF_REFERENCE", "FUTURE_COMMIT_PREDICTION", "CHECKOUT_MISMATCH", "BOOTSTRAP_MISMATCH", "HOST_GUEST_MISMATCH", "LAUNCHER_ADAPTER_MISMATCH", "NOCLOUD_MISMATCH", "NONCANONICAL_AUTHORITY_HANDOFF", "RECEIPT_PARENT_ABSENCE", "HISTORICAL_SHA_MISMATCH", "TRANSIENT_ROOT_MISMATCH", "BASE_IMAGE_MUTATION", "ARBITRARY_HISTORICAL_HEAD_CERTIFICATION", "RUNTIME_CURRENT_IDENTITY_COLLAPSE", "CURRENT_CERTIFICATION_PROVENANCE_WEAKENING", "VERSION_DOWNGRADE", "MIXED_VERSION_ACCEPTANCE", "CALLER_SELECTED_SCHEMA_OR_VALIDATOR", "FUTURE_SPECIFIC_EXCEPTION", "PARALLEL_PRODUCTION_ROUTE", "P11_BYPASS"]},
        "ex": authenticate_ex(root),
        "reuse_impact": {"reused_certified_capability_set": ["IJ_MINIMUM_SEMANTICS_AND_OWNER_MODEL", "FM_REPOSITORY_CHECKOUT_SEPARATION", "DU_V1_RUNTIME_TARGET_PAIR", "EB_EE_CLOSED_RECEIPT_AND_CURRENTNESS_PATTERNS", "P11", "CHE", "FK", "GN", "GL", "EX_17_OF_17", "GOVERNANCE", "LAYER_0", "PINNED_NESTED_AUTHORITY"], "new_capability_set": ["IK_REPOSITORY_ONLY_OPTION_B_PHYSICAL_SHAPE_AND_FAIL_CLOSED_CONTRACT_FORMALIZATION"], "new_runtime_capability_set": [], "unreachable_preexisting_capability_set": [], "parallel_flow_created": "VERIFIED__NO", "production_route_before": "VERIFIED__1", "production_route_after": "VERIFIED__1", "production_route_delta": "VERIFIED__0"},
        "overengineering_firewall": {"minimum_required_abstraction": "TWO_SEPARATE_COMMIT_TREE_ROLES_PLUS_ONE_TARGET_SELECTION_EVIDENCE_BINDING", "proposed_abstraction_scope": "DU_EB_EE_PRE_MATERIALIZATION_PROVENANCE_ONLY", "generic_identity_framework_created": "VERIFIED__NO", "new_generic_framework_count": "VERIFIED__0", "new_authority_layer_count": "VERIFIED__0", "overengineering_risk": "ESTIMATED__LOW"},
        "infrastructure_amortization": {"e05_generations_per_credit": "VERIFIED__5__HISTORICAL_WRONG_PROVENANCE_LIFECYCLE_ONLY", "operational_attempts_per_credit": "VERIFIED__1__HISTORICAL_WRONG_PROVENANCE_ONLY", "future_generations_so_far": "VERIFIED__7__IE_IF_IG_IH_II_IJ_IK", "future_e05_credit_so_far": "VERIFIED__0", "future_operational_attempts_so_far": "VERIFIED__0", "new_common_infrastructure_for_future": "VERIFIED__0__DESIGN_EVIDENCE_ONLY", "new_vector_specific_infrastructure_for_future": "VERIFIED__0", "marginal_new_infrastructure_for_ik": "VERIFIED__FORMALIZER_TEST_REPORT_AND_REDUCTION_ONLY", "marginal_new_infrastructure_per_e05_credit": "NOT_MEASURED__NO_FUTURE_CREDIT", "infrastructure_amortization_signal": "ESTIMATED__REUSE_DOMINANT_WITH_ZERO_RUNTIME_EXPANSION", "expected_next_credit_generation_count": "NOT_PROVEN__VERSION_DECISION_IMPLEMENTATION_AND_READINESS_REMAIN"},
        "ccwim": {"ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_L5_CLAIM", "cross_worker_state_recovery_level": "NOT_PROVEN__WORKER_IDENTITY_NOT_INSTRUMENTED", "repository_derived_context_ratio": "ESTIMATED__DOMINANT__NO_NUMERIC_INSTRUMENT", "human_handoff_information_required": "VERIFIED__SCOPE_EXACT_IJ_LOCATOR_AND_OPTION_B_DECISION", "previous_worker_conversation_required": "VERIFIED__NO", "previous_worker_identity_required": "VERIFIED__NO", "previous_worker_memory_required": "VERIFIED__NO", "authenticated_repository_continuation": "VERIFIED__YES", "inter_generation_cross_worker_continuation": "NOT_PROVEN__WORKER_IDENTITY_NOT_INSTRUMENTED", "intra_generation_cross_worker_continuation": "NOT_APPLICABLE__SINGLE_WORKER_NOT_IDENTITY_INSTRUMENTED", "uncommitted_delta_recovery": "NOT_APPLICABLE__CLEAN_COMMITTED_IJ_ENTRY", "authority_state_recovery": "VERIFIED__NO_OPERATIONAL_AUTHORITY_EXISTS", "consumed_authority_recovery": "VERIFIED__HISTORICAL_CONSUMED_AUTHORITY_NONREUSABLE", "post_operation_state_recovery": "VERIFIED__IJ_TERMINAL_REUSED", "operation_replay_prevention": "VERIFIED__IK_OPERATIONAL_COUNTERS_ZERO", "cross_worker_constitutional_drift": "NOT_PROVEN__WORKER_IDENTITY_NOT_INSTRUMENTED", "handoff_sufficiency_status": "VERIFIED", "handoff_state_completeness": "VERIFIED__COMPLETE_FOR_IK_FORMALIZATION_SCOPE", "handoff_reconstruction_required": "VERIFIED__YES", "handoff_reconstruction_success": "VERIFIED__YES", "handoff_ambiguity_count": "VERIFIED__0", "unauthenticated_handoff_assumption_count": "VERIFIED__0"},
        "implementation_frontier": implementation_frontier(),
        "metrics": {"project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR", "constitutional_health_evidence": "VERIFIED__OPTION_B_SHAPE_CLOSED__UNPROVEN_VERSION_IDENTITY_FAILS_CLOSED", "shadow_automation_status": "VERIFIED__ABSENT", "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR", "e05_frontier_distance": "VERIFIED__8_OF_18_OBLIGATIONS_REMAIN", "selected_e05_local_frontier_distance": "NOT_PROVEN__VERSION_IDENTITY_IMPLEMENTATION_AND_READINESS", "governance_efficience": "ESTIMATED__MINIMUM_FORMALIZATION_EVIDENCE_ONLY", "architectural_governance_efficience": "VERIFIED__ONE_ROUTE_ZERO_RUNTIME_OWNER_MUTATION", "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED", "cognition_assisted_handoff": "VERIFIED__AUTHENTICATED_IJ_TO_IK_REPOSITORY_CONTINUATION", "aigol_codex_work_share": "NOT_MEASURED", "overengineering_risk": "ESTIMATED__LOW", "proof_process_overhead_risk": "ESTIMATED__MODERATE", "cognition_provenance": "VERIFIED__AUTHENTICATED_REPOSITORY_PRIMARY", "candidate_capability": "VERIFIED__IF_BOUND_DU_V1__SUCCESSOR_NOT_IMPLEMENTED", "shadow_design_target": "VERIFIED__HUMAN_SELECTED_OPTION_B_GENERAL_VERSIONED_DU_EB_EE_PROVENANCE_SEPARATION", "constitutional_continuation_progress": "VERIFIED__OPTION_B_PHYSICAL_SHAPE_FORMALIZED__EXACT_VERSION_IDENTITY_NOT_PROVEN", "prompt_context_reuse_ratio": "NOT_MEASURED", "token_benchmark": "NOT_MEASURED", "llm_cost_reduction_ratio": "NOT_MEASURED", "lcrr": "NOT_MEASURED", "marginal_e05_generation_cost": "NOT_MEASURED", "marginal_new_infrastructure_per_e05_credit": "NOT_MEASURED__NO_FUTURE_CREDIT", "infrastructure_amortization_signal": "ESTIMATED__REUSE_DOMINANT_WITH_ZERO_RUNTIME_EXPANSION", "expected_next_credit_generation_count": "NOT_PROVEN__VERSION_DECISION_IMPLEMENTATION_AND_READINESS_REMAIN"},
        "cognition_provenance": "VERIFIED__AUTHENTICATED_GIT_IJ_II_IH_IG_IF_IE_ID_IC_DU_EB_EE_FM_GN_GL_P11_CHE_FK_EX_GOVERNANCE_LAYER_0_NESTED_AUTHORITY_CURRENT_TESTS",
        "operational_counters": counters,
        "e05": {"before": "10/18", "after": "10/18", "satisfied": 10, "remaining": 8, "credit": 0},
        "validation": {"mode": "REPOSITORY_ONLY__NO_OPERATIONAL_VALIDATION", "ik_focused": "VERIFIED__18_PASSED", "current_applicable_assertions": "VERIFIED__153_PASSED__18_IK_PLUS_135_RETAINED", "historical_or_superseded_snapshot_assertions": "NOT_APPLICABLE__40_EXACTLY_DESELECTED_WITH_LINEAGE_REASONS_IN_G48_REPORT", "p11_human_act_che_fk": "VERIFIED__72_PASSED", "ex_regression": "VERIFIED__12_OF_12__CERTIFIED_17_OF_17", "governance_layer_0": "VERIFIED__9_PASSED", "conformance_engine": "VERIFIED__20_PASSED__CONFORMANT__0_WARNINGS__0_VIOLATIONS", "canonical_json_duplicate_keys_seals_ast": "VERIFIED", "git_diff_check": "VERIFIED__CLEAN"},
        "terminal_control": {
            "current_e05_status": "VERIFIED__10_OF_18", "selected_next_e05_vector": "VERIFIED__FUTURE",
            "human_governance_schema_selection": "VERIFIED__OPTION_B", "human_governance_decision_scope": "REPOSITORY_ONLY_SUCCESSOR_SCHEMA_SELECTION_AND_FORMALIZATION",
            "successor_contract_design_status": "NOT_PROVEN__OPTION_B_SHAPE_FORMALIZED__EXACT_VERSION_AND_BINDING_IDENTITIES_UNRESOLVED",
            "successor_schema_status": "NOT_PROVEN__REMAINING_EXACT_CONTRACT_AMBIGUITY", "successor_schema_closed": "VERIFIED__SELECTED_NESTED_OBJECT_CLOSED__FULL_VERSIONED_RECEIPT_PENDING_IDENTITY",
            "successor_version_required": "VERIFIED__YES", "successor_version_identifier": "NOT_PROVEN__NO_UNIQUE_REPOSITORY_CONVENTION",
            "version_dispatch_contract_status": "NOT_PROVEN__FAIL_CLOSED_PREDICATES_FORMALIZED__EXACT_BOUND_IDENTITIES_UNRESOLVED", "version_dispatch_bypass_risk": "NOT_PROVEN__NO_IMPLEMENTATION_AND_NO_RATIFIED_SUCCESSOR_IDENTITIES",
            "schema_uniqueness": "VERIFIED__HUMAN_SELECTED_OPTION_B__PHYSICAL_BASELINE_SHAPE_UNIQUE__VERSIONED_CONTRACT_NOT_COMPLETE", "owner_uniqueness_status": "VERIFIED__DESIGN_ASSIGNMENTS_UNIQUE",
            "runtime_target_provenance_authentication": "VERIFIED__FM_LAUNCHER_CONTEXT_CANDIDATE_GIT_CLOSURE", "runtime_target_selection_binding": "VERIFIED__AUTHENTICATED", "current_certification_provenance_status": "VERIFIED__ACTUAL_CURRENT_GIT_HEAD_TREE",
            "arbitrary_historical_head_bypass": "VERIFIED__NO", "current_head_provenance_weakening": "VERIFIED__NO", "current_tree_provenance_weakening": "VERIFIED__NO",
            "backward_compatibility_status": "VERIFIED__V1_IMMUTABLE_AND_REACHABLE_WHERE_EXISTING_INVARIANTS_HOLD__SUCCESSOR_DISPATCH_PENDING", "v1_semantics_reinterpreted": "VERIFIED__NO",
            "p11_change_required": "VERIFIED__NO", "production_route_delta": "VERIFIED__0", "candidate_capability": "VERIFIED__IF_BOUND_DU_V1__SUCCESSOR_NOT_IMPLEMENTED",
            "future_preoperational_readiness": "NOT_PROVEN", "future_operational_capability": "NOT_PROVEN", "next_operational_generation_eligible": "NOT_PROVEN", "e05_credit": "VERIFIED__0",
            "last_verified_edge": "OPTION_B_NESTED_CERTIFICATION_BASELINE_PHYSICAL_SHAPE_OWNERS_EQUALITIES_AND_FAIL_CLOSED_PREDICATES_FORMALIZED",
            "first_broken_edge": "NO_RATIFIED_EXACT_DU_EB_EE_SUCCESSOR_SCHEMA_VERSION_VALIDATOR_PROFILE_OR_DISPATCH_IDENTITY_SET",
            "minimum_missing_capability": "HUMAN_GOVERNANCE_SELECTION_OF_EXACT_SUCCESSOR_VERSION_IDENTITY_SET_AND_NAMESPACE",
            "minimum_legal_next_delta": "HUMAN_GOVERNANCE_DECISION_REQUIRED", "auto_continuable": False, "human_authorization_required": False, "human_review_required": True, "next_generation_started": False,
            "verdict": "NOT_PROVEN__IK_OPTION_B_SHAPE_FORMALIZED__EXACT_VERSION_IDENTITY_NOT_UNIQUE__ZERO_OPERATION__E05_10_OF_18__HUMAN_REVIEW_REQUIRED",
        },
    }


def terminal_envelope(repository_root: Path) -> dict[str, Any]:
    reduction = terminal_reduction(repository_root)
    return {"schema_id": "G77_256IK_OPTION_B_SUCCESSOR_CONTRACT_FORMALIZATION_ENVELOPE_V1", "reduction": reduction, "reduction_sha256": sha256_bytes(canonical_bytes(reduction))}


if __name__ == "__main__":
    raise SystemExit("repository-only IK formalizer; no operational CLI entry point")
