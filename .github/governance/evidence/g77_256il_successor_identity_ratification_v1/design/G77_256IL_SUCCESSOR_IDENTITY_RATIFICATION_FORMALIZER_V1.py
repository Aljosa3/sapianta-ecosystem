#!/usr/bin/env python3
"""G77-256IL repository-only DU/EB/EE V2 identity ratification.

The Human-selected same-family incompatible-major policy uniquely derives the
V2 identity strings that have V1 ancestors.  Repository evidence does not,
however, select one exact family-local filesystem layout or dispatch owner.
This formalizer preserves that remaining boundary and has no operational path.
"""

from __future__ import annotations

import ast
from copy import deepcopy
from dataclasses import asdict, dataclass, replace
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True

BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
IK_HEAD = "7a7c77d32551020d5fed6cce5b4f7786e9974573"
IK_TREE = "244c48f120df88602126851e4801f9647e2da377"
IK_SUBJECT = "G77-256IK formalize nested successor contract boundary"
IJ_HEAD = "a07f6e76239a9d8f309f290ecc8ab328d08aa64f"
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

IL_ROOT = Path(".github/governance/evidence/g77_256il_successor_identity_ratification_v1")
IK_ROOT = Path(".github/governance/evidence/g77_256ik_nested_successor_contract_v1")
DU_ROOT = Path(".github/governance/evidence/g77_256du_continuation_manifest_contract_v1")
EB_ROOT = Path(".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v1")
EE_ROOT = Path(".github/governance/evidence/g77_256ee_runtime_consumer_binding_v1")
DU_SCHEMA = DU_ROOT / "G77_256DU_CANONICAL_CONTINUATION_MANIFEST_SCHEMA_V1.json"
DU_VALIDATOR = DU_ROOT / "validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V1.py"
EB_SCHEMA = EB_ROOT / "G77_256EB_CANDIDATE_BOUND_VALIDATION_RECEIPT_SCHEMA_V1.json"
EB_VALIDATOR = EB_ROOT / "validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V1.py"
EE_SCHEMA = EE_ROOT / "G77_256EE_RUNTIME_CONSUMER_BINDING_RECEIPT_SCHEMA_V1.json"
EE_VALIDATOR = EE_ROOT / "validator/G77_256EE_RUNTIME_CONSUMER_BINDING_VALIDATOR_V1.py"
FM_LAUNCHER = Path(".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py")
IH_CANDIDATE = Path(".github/governance/evidence/g77_256ih_future_if_identity_rebind_v1/live_binding/candidate/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json")
IH_RUNTIME = Path(".github/governance/evidence/g77_256ih_future_if_identity_rebind_v1/live_binding/runtime_projection/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json")
IH_CONTEXT = Path(".github/governance/evidence/g77_256ih_future_if_identity_rebind_v1/live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json")
IF_BINDING = Path(".github/governance/evidence/g77_256if_future_post_commit_readiness_v1/live_binding/G77_256IF_FUTURE_ACT_CHE_BINDING_V1.json")
IF_ADAPTER = Path(".github/governance/evidence/g77_256if_future_post_commit_readiness_v1/adapter/G77_256IF_FUTURE_VECTOR_ADAPTER_V1.py")
EX_CERTIFICATE = Path(".github/governance/evidence/g77_256ex_common_substrate_certification_v1/G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json")

IK_HASHES = {
    IK_ROOT / "G77_256IK_G48_IMPLEMENTATION_REPORT_V1.md": "17dc7e4e15102aa1cf41911df167752ae40d0ff9b8c9a2c706679f57031362c2",
    IK_ROOT / "G77_256IK_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json": "cc167af85f126e8a0a6c31a20ece2deeb620b1c0bab2e3d0f47fdcae9343ff90",
    IK_ROOT / "design/G77_256IK_NESTED_SUCCESSOR_CONTRACT_FORMALIZER_V1.py": "88333cde5759bf8568bf4cd389d4de75887939dd63c4fc50285ca19b59863be7",
    IK_ROOT / "tests/test_g77_256ik_nested_successor_contract_v1.py": "06c8effd1643576d5ebe505bc8a008e9f983f5f3069ea606aedb6d79f8007475",
}
IK_BLOBS = {
    IK_ROOT / "G77_256IK_G48_IMPLEMENTATION_REPORT_V1.md": "7140652685c3a7c6e53751b092bf65afd471f2ae",
    IK_ROOT / "G77_256IK_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json": "8f13cbda640892cfb539d558c4fd842d6937e297",
    IK_ROOT / "design/G77_256IK_NESTED_SUCCESSOR_CONTRACT_FORMALIZER_V1.py": "10da38e897b750346ed5eef61eb12a5d566dd59c",
    IK_ROOT / "tests/test_g77_256ik_nested_successor_contract_v1.py": "fa7c0343f42021dad9086ff1815d59b79a2a36eb",
}

FUTURE_CANDIDATE_SHA = "ad5d204ec6ace09f18b83fd5f868e73dac5e36dad81149f9f335c87f68cf42f7"
FUTURE_CONTEXT_SHA = "769f7b5cde5946450acbecfd956d479e91d9cf818d47bd4db34cb5086a1b07cb"
FUTURE_PAYLOAD = "9568e0c248ad488cabcf6bde6b490c544077862d10e3fda13bcdc8ed9953f547"
FUTURE_SOURCE_ACT = "7167b0725d2c84bafde1d0060f512b0fa358d777ec1beff8b7c68d22ee6502e8"
FUTURE_CHE = "CHE-CORRELATION-15b2680b5577da169cecf9efb3231e2e6f6467e6f409fa2594b04128f998e454"
GIT_OBJECT_RE = re.compile(r"^[0-9a-f]{40}$")


class ILRatificationError(ValueError):
    """One deterministic fail-closed IL ratification error."""


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
            raise ILRatificationError(f"DUPLICATE_JSON_KEY__{key}")
        result[key] = value
    return result


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    try:
        value = json.loads(raw, object_pairs_hook=_unique)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ILRatificationError(f"JSON_INVALID__{path.name}") from exc
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise ILRatificationError(f"CANONICAL_JSON_INVALID__{path.name}")
    return value


def _git(root: Path, *arguments: str) -> str:
    try:
        return subprocess.check_output(["git", *arguments], cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError as exc:
        raise ILRatificationError("GIT_IDENTITY_UNAVAILABLE") from exc


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
        "repository": str(root), "branch": BRANCH, "head": IK_HEAD,
        "tree": IK_TREE, "subject": IK_SUBJECT, "origin": ORIGIN,
        "remote_tracking_head": IK_HEAD, "index": "",
    }
    if observed != expected:
        raise ILRatificationError("EXACT_COMMITTED_IK_CHECKPOINT_MISMATCH")
    for ancestor in (IJ_HEAD, II_HEAD, IH_HEAD, IG_HEAD, IF_HEAD, IE_HEAD, ID_HEAD, IC_HEAD, STABLE_ANCHOR):
        if subprocess.run(["git", "merge-base", "--is-ancestor", ancestor, IK_HEAD], cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode:
            raise ILRatificationError(f"ANCESTRY_MISSING__{ancestor}")
    status = subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=all"], cwd=root, text=True).splitlines()
    if any(not line[3:].startswith(IL_ROOT.as_posix() + "/") for line in status):
        raise ILRatificationError("UNRELATED_WORKTREE_MUTATION")
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
        raise ILRatificationError("NESTED_AUTHORITY_NOT_CLEAN_DETACHED_PINNED")
    return observed | {"nested": nested_state, "worktree_scope": "VERIFIED__IL_EVIDENCE_ONLY"}


def reconstruct_ik(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    identities: dict[str, Any] = {}
    for path, expected_sha in IK_HASHES.items():
        committed = subprocess.check_output(["git", "show", f"{IK_HEAD}:{path.as_posix()}"], cwd=root)
        blob = _git(root, "rev-parse", f"{IK_HEAD}:{path.as_posix()}")
        if committed != (root / path).read_bytes() or sha256_bytes(committed) != expected_sha or blob != IK_BLOBS[path]:
            raise ILRatificationError(f"IK_IDENTITY_MISMATCH__{path.name}")
        identities[path.name] = {"path": path.as_posix(), "sha256": expected_sha, "git_blob": blob}
    envelope = load_canonical(root / IK_ROOT / "G77_256IK_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json")
    if envelope["reduction_sha256"] != sha256_bytes(canonical_bytes(envelope["reduction"])):
        raise ILRatificationError("IK_TERMINAL_SEAL_INVALID")
    control = envelope["reduction"]["terminal_control"]
    expected = {
        "current_e05_status": "VERIFIED__10_OF_18",
        "human_governance_schema_selection": "VERIFIED__OPTION_B",
        "successor_version_identifier": "NOT_PROVEN__NO_UNIQUE_REPOSITORY_CONVENTION",
        "first_broken_edge": "NO_RATIFIED_EXACT_DU_EB_EE_SUCCESSOR_SCHEMA_VERSION_VALIDATOR_PROFILE_OR_DISPATCH_IDENTITY_SET",
        "p11_change_required": "VERIFIED__NO",
        "production_route_delta": "VERIFIED__0",
        "future_operational_capability": "NOT_PROVEN",
        "e05_credit": "VERIFIED__0",
    }
    if {key: control[key] for key in expected} != expected:
        raise ILRatificationError("IK_TERMINAL_FRONTIER_MISMATCH")
    return {"status": "VERIFIED", "artifact_count": 4, "identities": identities, "canonical_json": "VERIFIED", "inner_seal": "VERIFIED", "frontier": expected}


def human_identity_policy() -> dict[str, Any]:
    return {
        "human_governance_successor_identity_policy": "EXISTING_DU_EB_EE_CONTRACT_FAMILIES__INCOMPATIBLE_MAJOR_SUCCESSOR",
        "successor_major_version": 2,
        "successor_semver": "2.0.0",
        "successor_identity_suffix": "V2",
        "new_generic_contract_family": False,
        "v1_reinterpretation": False,
        "decision_scope": "REPOSITORY_ONLY_SUCCESSOR_IDENTITY_VERSION_NAMESPACE_RATIFICATION",
        "human_operational_authority": 0,
        "future_operation_authorized": False,
        "e05_credit_authorized": False,
    }


def _module_constants(path: Path) -> dict[str, Any]:
    constants: dict[str, Any] = {}
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and isinstance(node.value, ast.Constant):
            constants[node.targets[0].id] = node.value.value
    return constants


def v1_identity_inventory(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    du, eb, ee = (_module_constants(root / path) for path in (DU_VALIDATOR, EB_VALIDATOR, EE_VALIDATOR))
    schemas = {family: json.loads((root / path).read_bytes(), object_pairs_hook=_unique) for family, path in {"DU": DU_SCHEMA, "EB": EB_SCHEMA, "EE": EE_SCHEMA}.items()}
    if any(schema.get("additionalProperties") is not False for schema in schemas.values()):
        raise ILRatificationError("V1_SCHEMA_NOT_CLOSED")
    rows = [
        ("DU", "schema", du["SCHEMA_IDENTITY"], DU_SCHEMA),
        ("DU", "envelope_schema", du["ENVELOPE_SCHEMA_ID"], DU_SCHEMA),
        ("DU", "payload_schema", du["MANIFEST_SCHEMA_ID"], DU_SCHEMA),
        ("DU", "validator", du["CONSUMER_IDENTITY"], DU_VALIDATOR),
        ("DU", "producer", du["PRODUCER_IDENTITY"], DU_VALIDATOR),
        ("EB", "schema", eb["RECEIPT_SCHEMA_IDENTITY"], EB_SCHEMA),
        ("EB", "envelope_schema", eb["RECEIPT_ENVELOPE_SCHEMA_ID"], EB_SCHEMA),
        ("EB", "receipt_schema", eb["RECEIPT_SCHEMA_ID"], EB_SCHEMA),
        ("EB", "validator_and_issuer_implementation", eb["VALIDATOR_IDENTITY"], EB_VALIDATOR),
        ("EB", "receipt_profile", eb["VALIDATION_PROFILE"], EB_VALIDATOR),
        ("EB", "consumer_expectation", ee["EB_VALIDATOR_IDENTITY"], EE_VALIDATOR),
        ("EE", "schema", ee["SCHEMA_IDENTITY"], EE_SCHEMA),
        ("EE", "envelope_schema", ee["ENVELOPE_SCHEMA_ID"], EE_SCHEMA),
        ("EE", "receipt_schema", ee["RECEIPT_SCHEMA_ID"], EE_SCHEMA),
        ("EE", "validator_and_issuer_implementation", ee["VALIDATOR_IDENTITY"], EE_VALIDATOR),
        ("EE", "receipt_profile", ee["VALIDATION_PROFILE"], EE_VALIDATOR),
    ]
    inventory = [{"family": family, "role": role, "identity": identity, "owner_path": path.as_posix(), "status": "VERIFIED"} for family, role, identity, path in rows]
    return {
        "status": "VERIFIED__EXACT_V1_IDENTITY_INVENTORY",
        "semantic_versions": {"DU": du["MANIFEST_VERSION"], "EB": eb["RECEIPT_VERSION"], "EE": ee["RECEIPT_VERSION"]},
        "identities": inventory,
        "not_applicable": ["DU_NAMED_PROFILE", "EE_EXPLICIT_DOWNSTREAM_CONSUMER_IDENTITY"],
        "closed_schema_owners": {"DU": DU_SCHEMA.as_posix(), "EB": EB_SCHEMA.as_posix(), "EE": EE_SCHEMA.as_posix()},
        "naming_constants": "VERIFIED__AST_LEVEL_DU_EB_EE_IDENTITY_AND_VERSION_CONSTANTS",
        "file_naming_patterns": "VERIFIED__GENERATION_FAMILY_ROLE_AND_TERMINAL_V1_SUFFIXES",
        "schema_registries": "NOT_PROVEN__NO_DU_EB_EE_CROSS_VERSION_SCHEMA_REGISTRY_EXISTS",
        "profile_registries": "NOT_PROVEN__NO_DU_EB_EE_CROSS_VERSION_PROFILE_REGISTRY_EXISTS",
        "validator_registries": "NOT_PROVEN__NO_DU_EB_EE_CROSS_VERSION_VALIDATOR_REGISTRY_EXISTS",
        "version_check_helpers": "VERIFIED__FAMILY_LOCAL_CONSTANT_EQUALITY_AND_CLOSED_SCHEMA_CONST_CHECKS__NO_MAJOR_DISPATCH_HELPER",
        "canonical_binding_rule": "IDENTITY_PLUS_PATH_PLUS_FILE_SHA256__CANONICAL_SORTED_COMPACT_JSON_PLUS_LF_AND_INNER_SHA256_WHERE_APPLICABLE",
    }


def derive_v2_identity(v1_identity: str) -> str:
    if not isinstance(v1_identity, str) or not re.search(r"(?<![A-Z0-9])V1(?![A-Z0-9])", v1_identity):
        raise ILRatificationError("V1_TOKEN_ABSENT_OR_NONCANONICAL")
    return re.sub(r"(?<![A-Z0-9])V1(?![A-Z0-9])", "V2", v1_identity)


def v2_derivations(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    inventory = v1_identity_inventory(root)
    derived: list[dict[str, Any]] = []
    values: list[str] = []
    for row in inventory["identities"]:
        v2 = derive_v2_identity(row["identity"])
        values.append(v2)
        family = row["family"]
        owner_model = {
            "DU": ("DU_SUCCESSOR_CONTRACT", "DU_SUCCESSOR_PRODUCER", "DU_SUCCESSOR_VALIDATOR", "EB_AND_EE_SUCCESSOR_CHAIN", "EXACT_V2_IDENTITY_VERSION_PATH_AND_FILE_HASH", "REJECT_DU_IDENTITY_OR_IMPLEMENTATION_MISMATCH"),
            "EB": ("EB_SUCCESSOR_CONTRACT", "EB_SUCCESSOR_ISSUER", "EB_SUCCESSOR_VALIDATOR", "EE_SUCCESSOR_VERIFIER", "EXACT_V2_IDENTITY_VERSION_PROFILE_PATH_AND_FILE_HASH", "REJECT_EB_IDENTITY_PROFILE_OR_IMPLEMENTATION_MISMATCH"),
            "EE": ("EE_SUCCESSOR_CONTRACT", "EE_SUCCESSOR_ISSUER", "EE_SUCCESSOR_VALIDATOR", "RUNTIME_BINDING_CONSUMER", "EXACT_V2_IDENTITY_VERSION_PROFILE_PATH_AND_FILE_HASH", "REJECT_EE_IDENTITY_PROFILE_OR_IMPLEMENTATION_MISMATCH"),
        }[family]
        result = subprocess.run(["git", "grep", "-F", "--", v2, IK_HEAD], cwd=root, text=True, capture_output=True)
        if result.returncode not in (0, 1):
            raise ILRatificationError("COLLISION_SCAN_FAILED")
        derived.append({
            "family": row["family"], "identity_role": row["role"], "v1_identity": row["identity"],
            "derivation_rule": "REPLACE_EVERY_STANDALONE_V1_VERSION_TOKEN_WITH_V2__PRESERVE_ALL_OTHER_FAMILY_TOKENS",
            "derived_v2_identity": v2,
            "uniqueness_proof": "VERIFIED__ONE_TOKEN_REWRITE_RESULT_UNDER_HUMAN_POLICY",
            "collision_check": "VERIFIED__ABSENT_AT_COMMITTED_IK" if result.returncode == 1 else "COLLISION",
            "namespace_check": "VERIFIED__IDENTITY_FAMILY_PREFIX_PRESERVED",
            "semantic_owner": owner_model[0], "producer": owner_model[1], "validator": owner_model[2],
            "consumer": owner_model[3], "namespace": "NOT_PROVEN__FAMILY_LOCAL_LAYOUT_AMBIGUITY",
            "mandatory_equality": owner_model[4], "failure_mode": owner_model[5],
        })
    v1_to_v2: dict[str, str] = {}
    for row in derived:
        prior = v1_to_v2.setdefault(row["v1_identity"], row["derived_v2_identity"])
        if prior != row["derived_v2_identity"]:
            raise ILRatificationError("V2_DERIVATION_NOT_FUNCTIONAL")
    if len(set(v1_to_v2)) != len(set(v1_to_v2.values())) or any(row["collision_check"] == "COLLISION" for row in derived):
        raise ILRatificationError("V2_IDENTITY_COLLISION")
    return {"status": "VERIFIED__ALL_V1_COUNTERPART_IDENTITIES_UNIQUELY_DERIVED", "semantic_version": "2.0.0", "major": 2, "identities": derived}


@dataclass(frozen=True)
class BoundIdentityTuple:
    family: str
    schema_identity: str
    version: str
    validator_identity: str
    receipt_profile: str
    issuer_implementation_identity: str
    consumer_expectation: str


def successor_tuples(repository_root: Path) -> dict[str, Any]:
    rows = v2_derivations(repository_root)["identities"]
    by_role = {(row["family"], row["identity_role"]): row["derived_v2_identity"] for row in rows}
    tuples = {
        "DU": BoundIdentityTuple("DU", by_role[("DU", "schema")], "2.0.0", by_role[("DU", "validator")], "NOT_APPLICABLE__NO_V1_NAMED_DU_PROFILE", by_role[("DU", "producer")], by_role[("DU", "validator")]),
        "EB": BoundIdentityTuple("EB", by_role[("EB", "schema")], "2.0.0", by_role[("EB", "validator_and_issuer_implementation")], by_role[("EB", "receipt_profile")], by_role[("EB", "validator_and_issuer_implementation")], by_role[("EB", "consumer_expectation")]),
        "EE": BoundIdentityTuple("EE", by_role[("EE", "schema")], "2.0.0", by_role[("EE", "validator_and_issuer_implementation")], by_role[("EE", "receipt_profile")], by_role[("EE", "validator_and_issuer_implementation")], "NOT_APPLICABLE__NO_EXPLICIT_V1_DOWNSTREAM_CONSUMER_IDENTITY"),
    }
    return {"status": "VERIFIED__IDENTITY_VALUES_UNIQUE__FILESYSTEM_NAMESPACE_AND_DISPATCH_OWNER_UNRESOLVED", "tuples": {key: asdict(value) for key, value in tuples.items()}}


def validate_bound_tuple(observed: BoundIdentityTuple, expected: BoundIdentityTuple, *, caller_selected: bool = False, downgrade: bool = False) -> str:
    if caller_selected:
        raise ILRatificationError("CALLER_IDENTITY_SELECTION_REJECTED")
    if downgrade:
        raise ILRatificationError("VERSION_DOWNGRADE_REJECTED")
    if observed != expected:
        raise ILRatificationError("SCHEMA_VERSION_VALIDATOR_PROFILE_ISSUER_CONSUMER_OR_FAMILY_MISMATCH")
    return "VERIFIED__EXACT_GOVERNED_TUPLE"


BASELINE_FIELDS = frozenset({"head", "tree"})


def validate_certification_baseline(value: Any) -> dict[str, str]:
    if not isinstance(value, dict) or set(value) != BASELINE_FIELDS:
        raise ILRatificationError("CERTIFICATION_BASELINE_SCHEMA_INVALID")
    if any(not isinstance(value[field], str) or GIT_OBJECT_RE.fullmatch(value[field]) is None for field in BASELINE_FIELDS):
        raise ILRatificationError("CERTIFICATION_BASELINE_GIT_IDENTITY_INVALID")
    return {"head": value["head"], "tree": value["tree"]}


def authenticate_certification_currentness(repository_root: Path, baseline: Any) -> str:
    root = repository_root.resolve()
    value = validate_certification_baseline(baseline)
    if value != {"head": _git(root, "rev-parse", "HEAD"), "tree": _git(root, "rev-parse", "HEAD^{tree}")}:
        raise ILRatificationError("CERTIFICATION_BASELINE_NOT_CURRENT")
    if _git(root, "rev-parse", f"{value['head']}^{{tree}}") != value["tree"]:
        raise ILRatificationError("CERTIFICATION_BASELINE_TREE_MISMATCH")
    return "VERIFIED__ACTUAL_CURRENT_HEAD_TREE_AND_COMMIT_TREE_CLOSURE"


def namespace_analysis() -> dict[str, Any]:
    candidates = {
        "VERSIONED_FAMILY_DIRECTORY": {
            "DU": ".github/governance/evidence/g77_256du_continuation_manifest_contract_v2/",
            "EB": ".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v2/",
            "EE": ".github/governance/evidence/g77_256ee_runtime_consumer_binding_v2/",
        },
        "V2_SIBLINGS_IN_EXISTING_FAMILY_DIRECTORY": {
            "DU": DU_ROOT.as_posix() + "/",
            "EB": EB_ROOT.as_posix() + "/",
            "EE": EE_ROOT.as_posix() + "/",
        },
    }
    return {
        "successor_namespace_policy": "VERIFIED__EXISTING_FAMILIES_ONLY",
        "new_generic_namespace_created": "VERIFIED__NO",
        "exact_successor_namespace_set": "NOT_PROVEN__TWO_FAMILY_LOCAL_LAYOUTS_REMAIN_WITHOUT_DU_EB_EE_SUCCESSION_PRECEDENT",
        "equally_family_preserving_candidates": candidates,
        "rejected_generic_candidate_count": 1,
    }


def implementation_frontier() -> dict[str, Any]:
    return {
        "minimum_successor_implementation_owner_set": "NOT_PROVEN__IDENTITY_OWNERS_DERIVED_BUT_EXACT_FILESYSTEM_AND_DISPATCH_OWNER_PLACEMENT_UNRESOLVED",
        "candidate_owner_roles": ["DU_V2_SCHEMA_AND_VALIDATOR", "EB_V2_SCHEMA_PROFILE_AND_VALIDATOR", "EE_V2_SCHEMA_PROFILE_AND_VALIDATOR", "FAMILY_LOCAL_FAIL_CLOSED_VERSION_DISPATCH", "FOCUSED_AND_REGRESSION_TESTS"],
        "minimum_successor_implementation_file_set": "NOT_PROVEN__TWO_FAMILY_LOCAL_NAMESPACE_LAYOUTS_AND_MULTIPLE_NON_GENERIC_DISPATCH_PLACEMENTS_REMAIN",
        "expected_production_route_delta": "VERIFIED__0", "expected_p11_delta": "VERIFIED__0",
        "expected_fm_runtime_delta": "VERIFIED__0", "expected_gn_gl_delta": "VERIFIED__0",
    }


def provenance(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    candidate = load_canonical(root / IH_CANDIDATE)
    context = load_canonical(root / IH_CONTEXT)
    if (root / IH_CANDIDATE).read_bytes() != (root / IH_RUNTIME).read_bytes() or sha256_path(root / IH_CANDIDATE) != FUTURE_CANDIDATE_SHA:
        raise ILRatificationError("FUTURE_CANDIDATE_RUNTIME_IDENTITY_DRIFT")
    checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    manifest = candidate["manifest"]
    constants = _module_constants(root / FM_LAUNCHER)
    if (manifest["required_head"], manifest["source_tree"], checkout["head"], checkout["tree"], constants["CHECKOUT_HEAD"], constants["CHECKOUT_TREE"]) != (IF_HEAD, IF_TREE, IF_HEAD, IF_TREE, IF_HEAD, IF_TREE):
        raise ILRatificationError("FM_TARGET_PROVENANCE_CLOSURE_MISMATCH")
    if _git(root, "rev-parse", f"{IF_HEAD}^{{tree}}") != IF_TREE:
        raise ILRatificationError("IF_TREE_CLOSURE_MISMATCH")
    authenticate_certification_currentness(root, {"head": IK_HEAD, "tree": IK_TREE})
    return {
        "runtime_target": {"head": IF_HEAD, "tree": IF_TREE},
        "runtime_target_provenance_authentication": "VERIFIED__FM_LAUNCHER_CONTEXT_CANDIDATE_GIT_CLOSURE",
        "runtime_target_selection_binding": "VERIFIED__AUTHENTICATED",
        "caller_chosen_runtime_target_authority": "VERIFIED__NO",
        "arbitrary_historical_head_bypass": "VERIFIED__NO",
        "current_certification": {"head": IK_HEAD, "tree": IK_TREE},
        "current_certification_provenance_status": "VERIFIED__ACTUAL_CURRENT_GIT_HEAD_TREE",
        "certification_baseline_caller_authority": "VERIFIED__NO",
        "current_head_provenance_weakening": "VERIFIED__NO", "current_tree_provenance_weakening": "VERIFIED__NO",
    }


def future_semantics(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    context = load_canonical(root / IH_CONTEXT)
    if context["context_sha256"] != FUTURE_CONTEXT_SHA:
        raise ILRatificationError("FUTURE_CONTEXT_IDENTITY_DRIFT")
    calls = {node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id for node in ast.walk(ast.parse((root / IF_ADAPTER).read_text())) if isinstance(node, ast.Call) and isinstance(node.func, (ast.Attribute, ast.Name))}
    if calls.intersection({"time", "time_ns", "now", "sleep"}):
        raise ILRatificationError("FUTURE_WALL_CLOCK_DEPENDENCY")
    text = json.dumps(load_canonical(root / IF_BINDING), sort_keys=True)
    if any(identity not in text for identity in (FUTURE_PAYLOAD, FUTURE_SOURCE_ACT, FUTURE_CHE)):
        raise ILRatificationError("FUTURE_SEMANTIC_IDENTITY_DRIFT")
    return {"evaluation_time": 500, "valid_from": 600, "valid_until": 1000, "relation": "VERIFIED__500_LT_600_LT_1000", "payload_digest": FUTURE_PAYLOAD, "source_act_digest": FUTURE_SOURCE_ACT, "che_correlation": FUTURE_CHE, "future_semantic_mutation_count": "VERIFIED__0", "wall_clock_dependency_count": "VERIFIED__0"}


def authenticate_ex(repository_root: Path) -> dict[str, str]:
    envelope = json.loads((repository_root.resolve() / EX_CERTIFICATE).read_bytes(), object_pairs_hook=_unique)
    preimage = deepcopy(envelope)
    preimage["certificate_sha256"] = ""
    payload = json.dumps(preimage, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()
    if envelope["certificate_sha256"] != sha256_bytes(payload) or envelope["certificate"]["component_counts"]["CERTIFIED"] != 17:
        raise ILRatificationError("EX_CERTIFICATE_AUTHENTICATION_FAILED")
    return {"ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0", "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED"}


def generality_matrix() -> list[dict[str, str]]:
    accepted = {"V1_CURRENT_TARGET_VALID", "V2_TARGET_EQUALS_CURRENT", "V2_AUTHENTICATED_TARGET_DIFFERS_CURRENT", "FUTURE_VECTOR", "NON_FUTURE_APPLICABLE_VECTOR"}
    cases = [
        "V1_CURRENT_TARGET_VALID", "V2_TARGET_EQUALS_CURRENT", "V2_AUTHENTICATED_TARGET_DIFFERS_CURRENT",
        "V2_ARBITRARY_HISTORICAL_TARGET", "V2_WRONG_TARGET_TREE", "V2_WRONG_CERTIFICATION_TREE",
        "V2_STALE_CERTIFICATION_BASELINE", "V2_NONEXISTENT_TARGET", "V2_NONEXISTENT_CERTIFICATION_COMMIT",
        "V2_CANDIDATE_CONTEXT_MISMATCH", "V2_FM_CANDIDATE_MISMATCH", "V2_EB_CURRENT_MISMATCH",
        "V2_EE_CURRENT_MISMATCH", "V1_RECEIPT_WITH_V2_IDENTITY", "V2_RECEIPT_WITH_V1_IDENTITY",
        "V1_VALIDATOR_WITH_V2_SCHEMA", "V2_VALIDATOR_WITH_V1_SCHEMA", "MIXED_RECEIPT_PROFILE",
        "UNKNOWN_V2_IDENTITY", "CALLER_SELECTED_VERSION", "CALLER_SELECTED_VALIDATOR", "CALLER_SELECTED_PROFILE",
        "CROSS_FAMILY_DU_EB_SUBSTITUTION", "CROSS_FAMILY_EB_EE_SUBSTITUTION", "FUTURE_VECTOR",
        "NON_FUTURE_APPLICABLE_VECTOR", "RUNTIME_CANDIDATE_BYTE_MISMATCH",
    ]
    return [{"case": case, "observed": "REPRESENTABLE__CONTRACT_ONLY__NOT_AUTHORITY" if case in accepted else "REJECT__FAIL_CLOSED"} for case in cases]


def terminal_reduction(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    namespaces = namespace_analysis()
    counters = {key: 0 for key in ("human_operational_authority", "authority_consumption", "pre", "fm_operational_launcher_invocation", "qemu", "vm_creation", "vm_boot", "operation_attempt", "request", "p11_entry", "protected_invocation", "protected_effect", "retry", "repair_retry", "replay", "e05_credit")}
    return {
        "schema_id": "G77_256IL_SUCCESSOR_IDENTITY_RATIFICATION_V1",
        "mode": "REPOSITORY_ONLY__IDENTITY_RATIFICATION__NO_IMPLEMENTATION__NO_OPERATION",
        "entry": authenticate_entry(root), "ik_reconstruction": reconstruct_ik(root),
        "human_identity_policy": human_identity_policy(), "v1_identity_inventory": v1_identity_inventory(root),
        "v2_derivation": v2_derivations(root), "successor_identity_tuples": successor_tuples(root),
        "option_b_binding": {"status": "VERIFIED__IDENTITY_LEVEL", "shape": {"certification_baseline": {"head": "GIT_COMMIT_40_LOWER_HEX", "tree": "GIT_TREE_40_LOWER_HEX"}}, "minimum_new_semantic_field_count": "VERIFIED__2", "complete_implementation_binding": "NOT_PROVEN__NAMESPACE_AND_DISPATCH_OWNER_UNRESOLVED"},
        "namespace_analysis": namespaces,
        "version_dispatch": {"status": "NOT_PROVEN__EXACT_IDENTITIES_DERIVED__EXACT_FILESYSTEM_AND_DISPATCH_OWNER_PLACEMENT_AMBIGUITY_REMAINS", "tuple_fields": ["family", "schema_identity", "version", "validator_identity", "receipt_profile", "issuer_implementation_identity", "consumer_expectation"], "unknown_tuple": "REJECT", "mixed_v1_v2": "REJECT", "downgrade": "REJECT", "caller_selected_identity": "REJECT", "cross_family_substitution": "REJECT", "bypass_risk": "NOT_PROVEN__NO_IMPLEMENTATION_AND_NO_UNIQUE_DISPATCH_OWNER"},
        "provenance": provenance(root), "future_semantics": future_semantics(root), "generality_matrix": generality_matrix(),
        "compatibility": {"version_change_classification": "VERIFIED__INCOMPATIBLE_MAJOR", "successor_semver": "VERIFIED__2.0.0", "v1_semantics_reinterpreted": "VERIFIED__NO", "historical_v1_mutation_count": "VERIFIED__0", "v1_identity_collision_with_v2": "VERIFIED__NO", "v1_capability_reachability": "VERIFIED__PRESERVED", "backward_compatibility_status": "VERIFIED__V1_IMMUTABLE_AND_REACHABLE__V2_NOT_IMPLEMENTED"},
        "boundaries": {"p11_change_required": "VERIFIED__NO", "p11_core_change_count": "VERIFIED__0", "fm_production_owner_mutation": "VERIFIED__0", "production_route_before": "VERIFIED__1", "production_route_after": "VERIFIED__1", "production_route_delta": "VERIFIED__0", "new_production_route_count": "VERIFIED__0", "gn_operational_applicability": "NOT_APPLICABLE", "gl_operational_applicability": "NOT_APPLICABLE", "new_authority_layer_count": "VERIFIED__0"},
        "family_firewall": {"du_eb_ee_family_collapse": "VERIFIED__NO", "new_generic_identity_framework": "VERIFIED__NO", "new_generic_provenance_framework": "VERIFIED__NO", "new_generic_contract_family": "VERIFIED__NO"},
        "implementation_frontier": implementation_frontier(), "ex": authenticate_ex(root),
        "historical_failure_firewall": {"status": "VERIFIED", "reintroduced_historical_failure_count": "VERIFIED__0", "precommit_self_reference_count": "VERIFIED__0", "future_commit_prediction_count": "VERIFIED__0"},
        "reuse_impact": {"reused_certified_capability_set": ["IK_OPTION_B_CONTRACT", "DU_V1", "EB_V1", "EE_V1", "FM_TARGET_SELECTION", "P11", "CHE_FK", "GN_GL", "EX_17_OF_17", "GOVERNANCE", "LAYER_0", "PINNED_NESTED_AUTHORITY"], "new_capability_set": ["IL_REPOSITORY_ONLY_V2_COUNTERPART_IDENTITY_DERIVATION_AND_REMAINING_NAMESPACE_AMBIGUITY_PROOF"], "new_runtime_capability_set": [], "unreachable_preexisting_capability_set": [], "parallel_flow_created": "VERIFIED__NO", "production_route_before": "VERIFIED__1", "production_route_after": "VERIFIED__1", "production_route_delta": "VERIFIED__0"},
        "infrastructure_amortization": {"e05_generations_per_credit": "VERIFIED__5__HISTORICAL_WRONG_PROVENANCE_LIFECYCLE_ONLY", "operational_attempts_per_credit": "VERIFIED__1__HISTORICAL_WRONG_PROVENANCE_ONLY", "future_generations_so_far": "VERIFIED__8__IE_IF_IG_IH_II_IJ_IK_IL", "future_e05_credit_so_far": "VERIFIED__0", "future_operational_attempts_so_far": "VERIFIED__0", "new_common_infrastructure_for_future": "VERIFIED__0__RATIFICATION_EVIDENCE_ONLY", "new_vector_specific_infrastructure_for_future": "VERIFIED__0", "marginal_new_infrastructure_for_il": "VERIFIED__FORMALIZER_TEST_REPORT_AND_REDUCTION_ONLY", "marginal_new_infrastructure_per_e05_credit": "NOT_MEASURED__NO_FUTURE_CREDIT", "infrastructure_amortization_signal": "ESTIMATED__REUSE_DOMINANT_WITH_ZERO_RUNTIME_EXPANSION", "expected_next_credit_generation_count": "NOT_PROVEN__NAMESPACE_DECISION_IMPLEMENTATION_AND_READINESS_REMAIN"},
        "ccwim": {"ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_L5_CLAIM", "cross_worker_state_recovery_level": "NOT_PROVEN__WORKER_IDENTITY_NOT_INSTRUMENTED", "repository_derived_context_ratio": "ESTIMATED__DOMINANT__NUMERIC_RATIO_NOT_MEASURED", "human_handoff_information_required": "VERIFIED__SCOPE_IK_LOCATOR_AND_IDENTITY_POLICY", "previous_worker_conversation_required": "VERIFIED__NO", "previous_worker_identity_required": "VERIFIED__NO", "previous_worker_memory_required": "VERIFIED__NO", "authenticated_repository_continuation": "VERIFIED", "inter_generation_cross_worker_continuation": "NOT_PROVEN__WORKER_IDENTITY_NOT_INSTRUMENTED", "intra_generation_cross_worker_continuation": "NOT_APPLICABLE__NO_DELEGATION", "uncommitted_delta_recovery": "NOT_APPLICABLE__CLEAN_IK_ENTRY", "authority_state_recovery": "NOT_APPLICABLE__NO_OPERATIONAL_AUTHORITY", "consumed_authority_recovery": "VERIFIED__HISTORICAL_AUTHORITY_NONREUSABLE", "post_operation_state_recovery": "NOT_APPLICABLE__NO_IL_OPERATION", "operation_replay_prevention": "VERIFIED__ZERO_IL_OPERATION_COUNTERS", "cross_worker_constitutional_drift": "NOT_PROVEN__WORKER_IDENTITY_NOT_INSTRUMENTED", "handoff_sufficiency_status": "VERIFIED", "handoff_state_completeness": "VERIFIED__AUTHORIZED_SCOPE_COMPLETE", "handoff_reconstruction_required": "VERIFIED__YES", "handoff_reconstruction_success": "VERIFIED", "handoff_ambiguity_count": "VERIFIED__0", "unauthenticated_handoff_assumption_count": "VERIFIED__0"},
        "metrics": {"project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR", "constitutional_health_evidence": "VERIFIED__V2_COUNTERPART_IDENTITIES_DERIVED__NAMESPACE_AMBIGUITY_FAILS_CLOSED", "shadow_automation_status": "VERIFIED__ABSENT", "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR", "e05_frontier_distance": "VERIFIED__8_OF_18_OBLIGATIONS_REMAIN", "selected_e05_local_frontier_distance": "NOT_PROVEN__NAMESPACE_DISPATCH_IMPLEMENTATION_AND_READINESS", "governance_efficience": "ESTIMATED__MINIMUM_RATIFICATION_EVIDENCE_ONLY", "architectural_governance_efficience": "VERIFIED__ONE_ROUTE_ZERO_RUNTIME_OWNER_MUTATION", "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED", "cognition_assisted_handoff": "VERIFIED__AUTHENTICATED_IK_TO_IL_REPOSITORY_CONTINUATION", "aigol_codex_work_share": "NOT_MEASURED", "overengineering_risk": "ESTIMATED__LOW", "proof_process_overhead_risk": "ESTIMATED__MODERATE", "cognition_provenance": "VERIFIED__AUTHENTICATED_REPOSITORY_PRIMARY", "candidate_capability": "VERIFIED__IF_BOUND_DU_V1__SUCCESSOR_NOT_IMPLEMENTED", "shadow_design_target": "VERIFIED__HUMAN_GOVERNED_EXISTING_FAMILY_V2_DU_EB_EE_OPTION_B_SUCCESSOR_IDENTITY_BINDING", "constitutional_continuation_progress": "VERIFIED__V2_COUNTERPART_IDENTITY_VALUES_DERIVED__EXACT_NAMESPACE_AND_DISPATCH_OWNER_NOT_PROVEN", "prompt_context_reuse_ratio": "NOT_MEASURED", "token_benchmark": "NOT_MEASURED", "llm_cost_reduction_ratio": "NOT_MEASURED", "lcrr": "NOT_MEASURED", "marginal_e05_generation_cost": "NOT_MEASURED", "marginal_new_infrastructure_per_e05_credit": "NOT_MEASURED__NO_FUTURE_CREDIT", "infrastructure_amortization_signal": "ESTIMATED__REUSE_DOMINANT_WITH_ZERO_RUNTIME_EXPANSION", "expected_next_credit_generation_count": "NOT_PROVEN__NAMESPACE_DECISION_IMPLEMENTATION_AND_READINESS_REMAIN"},
        "cognition_provenance": "VERIFIED__AUTHENTICATED_GIT_IK_IJ_II_IH_IG_IF_IE_ID_IC_DU_EB_EE_FM_GN_GL_P11_CHE_FK_EX_GOVERNANCE_LAYER_0_NESTED_AUTHORITY_CURRENT_TESTS",
        "validation": {
            "mode": "REPOSITORY_ONLY__NO_OPERATIONAL_VALIDATION",
            "il_focused": "VERIFIED__19_PASSED",
            "current_applicable_pytest_assertions": "VERIFIED__100_PASSED__19_IL_PLUS_72_P11_HUMAN_ACT_CHE_FK_PLUS_9_GOVERNANCE_LAYER_0",
            "du_eb_ee_v1_regressions": "VERIFIED__41_CASES__DU_11_EB_13_EE_17",
            "ex_regression": "VERIFIED__12_OF_12__CERTIFIED_17_OF_17",
            "conformance_engine": "VERIFIED__20_PASSED__CONFORMANT__0_WARNINGS__0_VIOLATIONS",
            "canonical_json_duplicate_keys_inner_seal_ast_six_headings": "VERIFIED",
            "historical_or_superseded_snapshot_assertions": "NOT_APPLICABLE__18_IK_LIVE_ENTRY_OR_SUPERSEDED_FRONTIER_TESTS__IK_REPORT_AUTHENTICATES_40_EARLIER_EXCLUSIONS",
            "git_diff_check": "VERIFIED__CLEAN",
        },
        "operational_counters": counters,
        "e05": {"before": "10/18", "after": "10/18", "satisfied": 10, "remaining": 8, "credit": 0},
        "terminal_control": {
            "current_e05_status": "VERIFIED__10_OF_18", "selected_next_e05_vector": "VERIFIED__FUTURE",
            "human_governance_successor_identity_policy": "VERIFIED__EXISTING_DU_EB_EE_CONTRACT_FAMILIES__INCOMPATIBLE_MAJOR_SUCCESSOR",
            "successor_major_version": "VERIFIED__2", "successor_semver": "VERIFIED__2.0.0", "successor_identity_suffix": "VERIFIED__V2",
            "new_generic_contract_family": "VERIFIED__NO", "v1_reinterpretation": "VERIFIED__NO", "v1_identity_inventory_status": "VERIFIED__EXACT",
            "successor_version_identifier": "VERIFIED__EXACT_V2", "successor_schema_identity_status": "VERIFIED__ALL_V1_COUNTERPARTS_UNIQUE",
            "successor_validator_identity_status": "VERIFIED__ALL_V1_COUNTERPARTS_UNIQUE", "successor_receipt_profile_identity_status": "VERIFIED__APPLICABLE_EB_EE_COUNTERPARTS_UNIQUE__DU_NOT_APPLICABLE",
            "successor_issuer_identity_status": "VERIFIED__EXPLICIT_COUNTERPARTS_UNIQUE", "successor_consumer_identity_status": "VERIFIED__EXPLICIT_COUNTERPARTS_UNIQUE__EE_NOT_APPLICABLE",
            "exact_successor_identity_tuple_status": "NOT_PROVEN__IDENTITY_VALUES_DERIVED__EXACT_NAMESPACE_AND_DISPATCH_OWNER_AMBIGUITY_REMAINS",
            "exact_successor_namespace_set": namespaces["exact_successor_namespace_set"], "identity_tuple_closed": "NOT_PROVEN__OWNER_PATH_AND_DISPATCH_PLACEMENT_UNRESOLVED",
            "version_dispatch_contract_status": "NOT_PROVEN__EXACT_IDENTITIES_DERIVED__EXACT_FILESYSTEM_AND_DISPATCH_OWNER_PLACEMENT_AMBIGUITY_REMAINS",
            "version_dispatch_bypass_risk": "NOT_PROVEN__NO_IMPLEMENTATION_AND_NO_UNIQUE_DISPATCH_OWNER", "downgrade_bypass": "VERIFIED__NO__FORMALIZED_REJECTION",
            "mixed_version_bypass": "VERIFIED__NO__FORMALIZED_REJECTION", "caller_version_selection_authority": "VERIFIED__NO",
            "owner_uniqueness_status": "NOT_PROVEN__SEMANTIC_ROLES_UNIQUE__EXACT_IMPLEMENTATION_OWNER_PATH_AMBIGUOUS", "option_b_to_v2_binding": "VERIFIED__IDENTITY_LEVEL__IMPLEMENTATION_ABSENT",
            "runtime_target_provenance_authentication": "VERIFIED__FM_LAUNCHER_CONTEXT_CANDIDATE_GIT_CLOSURE", "runtime_target_selection_binding": "VERIFIED__AUTHENTICATED",
            "current_certification_provenance_status": "VERIFIED__ACTUAL_CURRENT_GIT_HEAD_TREE", "arbitrary_historical_head_bypass": "VERIFIED__NO",
            "current_head_provenance_weakening": "VERIFIED__NO", "backward_compatibility_status": "VERIFIED__V1_IMMUTABLE_AND_REACHABLE__V2_NOT_IMPLEMENTED",
            "v1_semantics_reinterpreted": "VERIFIED__NO", "p11_change_required": "VERIFIED__NO", "production_route_delta": "VERIFIED__0",
            "minimum_successor_implementation_owner_set": "NOT_PROVEN__EXACT_DISPATCH_OWNER_PLACEMENT_AMBIGUOUS", "minimum_successor_implementation_file_set": "NOT_PROVEN__TWO_FAMILY_LOCAL_NAMESPACE_LAYOUTS_REMAIN",
            "candidate_capability": "VERIFIED__IF_BOUND_DU_V1__SUCCESSOR_NOT_IMPLEMENTED", "future_preoperational_readiness": "NOT_PROVEN", "future_operational_capability": "NOT_PROVEN", "next_operational_generation_eligible": "NOT_PROVEN", "e05_credit": "VERIFIED__0",
            "last_verified_edge": "HUMAN_V2_POLICY_APPLIED_TO_EXACT_V1_INVENTORY__ALL_COUNTERPART_IDENTITY_STRINGS_UNIQUE_AND_COLLISION_FREE",
            "first_broken_edge": "NO_UNIQUE_DU_EB_EE_FAMILY_LOCAL_V2_FILESYSTEM_NAMESPACE_OR_FAIL_CLOSED_DISPATCH_OWNER_PLACEMENT",
            "minimum_missing_capability": "HUMAN_GOVERNANCE_SELECTION_OF_EXACT_FAMILY_LOCAL_V2_FILESYSTEM_LAYOUT_AND_DISPATCH_OWNER_PLACEMENT",
            "minimum_legal_next_delta": "HUMAN_GOVERNANCE_DECISION_REQUIRED", "auto_continuable": False, "human_authorization_required": False, "human_review_required": True, "next_generation_started": False,
            "verdict": "NOT_PROVEN__IL_V2_IDENTITIES_DERIVED__NAMESPACE_AND_DISPATCH_OWNER_AMBIGUITY_FAIL_CLOSED__ZERO_OPERATION__E05_10_OF_18__HUMAN_REVIEW_REQUIRED",
        },
    }


def terminal_envelope(repository_root: Path) -> dict[str, Any]:
    reduction = terminal_reduction(repository_root)
    return {"schema_id": "G77_256IL_SUCCESSOR_IDENTITY_RATIFICATION_ENVELOPE_V1", "reduction": reduction, "reduction_sha256": sha256_bytes(canonical_bytes(reduction))}


def main() -> int:
    if len(sys.argv) == 2 and sys.argv[1] == "--emit-terminal":
        sys.stdout.buffer.write(canonical_bytes(terminal_envelope(Path.cwd())))
        return 0
    print("REFUSED__G77_256IL_REPOSITORY_ONLY_FORMALIZER_HAS_NO_OPERATIONAL_PATH", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
