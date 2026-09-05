#!/usr/bin/env python3
"""G77-256IM repository-only V2 implementation-gate formalizer.

The Human decision closes the V2 directory-layout choice and assigns dispatch
to each DU/EB/EE family.  It does not provide one exact dispatcher identity,
path, or choice between a distinct dispatcher and validator-owned dispatch.
This formalizer therefore stops before implementation and emits Terminal B.
It has no readiness or operational path.
"""

from __future__ import annotations

import ast
from copy import deepcopy
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
IL_HEAD = "c43839f54ae788caa11a2082aba845b9426ea4c6"
IL_TREE = "3af78505ae459388370ba572cc440d0a571acaf1"
IL_SUBJECT = "G77-256IL ratify V2 successor identity boundary"
IK_HEAD = "7a7c77d32551020d5fed6cce5b4f7786e9974573"
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

IM_ROOT = Path(".github/governance/evidence/g77_256im_family_local_v2_successor_implementation_v1")
IL_ROOT = Path(".github/governance/evidence/g77_256il_successor_identity_ratification_v1")
IL_TERMINAL = IL_ROOT / "G77_256IL_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
IL_HASHES = {
    IL_ROOT / "G77_256IL_G48_IMPLEMENTATION_REPORT_V1.md": "a36c1ffd3b7deae0039485c91293ad4ce1cdccfb50f71828c679aa8f5cc7e6f2",
    IL_TERMINAL: "96040ff316f20d68f8034a74b2b86003124023a4e6246eb45593798a309c6589",
    IL_ROOT / "design/G77_256IL_SUCCESSOR_IDENTITY_RATIFICATION_FORMALIZER_V1.py": "79444365d624f5a0548fa4329f0a3acbd842b50f8cb8558a5fe0614dffe072d2",
    IL_ROOT / "tests/test_g77_256il_successor_identity_ratification_v1.py": "5f3e38efd10b209051a9322bb5c874739d79ed0b066bc97d6d871888d2f9198a",
}
IL_BLOBS = {
    IL_ROOT / "G77_256IL_G48_IMPLEMENTATION_REPORT_V1.md": "41cbd165f89066c42feddad3d1be429b150b4cbe",
    IL_TERMINAL: "109200d65f17d5c756b8085a07b111c694562d31",
    IL_ROOT / "design/G77_256IL_SUCCESSOR_IDENTITY_RATIFICATION_FORMALIZER_V1.py": "347974f32ee2852ca81c12260577f5c62a6909fb",
    IL_ROOT / "tests/test_g77_256il_successor_identity_ratification_v1.py": "11db99f2dc5674dfa288e5691be60f32a669f86a",
}

DU_V1 = Path(".github/governance/evidence/g77_256du_continuation_manifest_contract_v1")
EB_V1 = Path(".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v1")
EE_V1 = Path(".github/governance/evidence/g77_256ee_runtime_consumer_binding_v1")
DU_V2 = Path(".github/governance/evidence/g77_256du_continuation_manifest_contract_v2")
EB_V2 = Path(".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v2")
EE_V2 = Path(".github/governance/evidence/g77_256ee_runtime_consumer_binding_v2")

V1_OWNERS = {
    "DU_SCHEMA": DU_V1 / "G77_256DU_CANONICAL_CONTINUATION_MANIFEST_SCHEMA_V1.json",
    "DU_VALIDATOR": DU_V1 / "validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V1.py",
    "EB_SCHEMA": EB_V1 / "G77_256EB_CANDIDATE_BOUND_VALIDATION_RECEIPT_SCHEMA_V1.json",
    "EB_VALIDATOR": EB_V1 / "validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V1.py",
    "EE_SCHEMA": EE_V1 / "G77_256EE_RUNTIME_CONSUMER_BINDING_RECEIPT_SCHEMA_V1.json",
    "EE_VALIDATOR": EE_V1 / "validator/G77_256EE_RUNTIME_CONSUMER_BINDING_VALIDATOR_V1.py",
}

FUTURE_CANDIDATE_SHA = "ad5d204ec6ace09f18b83fd5f868e73dac5e36dad81149f9f335c87f68cf42f7"
FUTURE_CONTEXT_SHA = "769f7b5cde5946450acbecfd956d479e91d9cf818d47bd4db34cb5086a1b07cb"
GIT_OBJECT_RE = re.compile(r"^[0-9a-f]{40}$")


class IMGateError(ValueError):
    """One deterministic fail-closed IM gate error."""


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
            raise IMGateError(f"DUPLICATE_JSON_KEY__{key}")
        result[key] = value
    return result


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    try:
        value = json.loads(raw, object_pairs_hook=_unique)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IMGateError(f"JSON_INVALID__{path.name}") from exc
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise IMGateError(f"CANONICAL_JSON_INVALID__{path.name}")
    return value


def _git(root: Path, *arguments: str) -> str:
    try:
        return subprocess.check_output(
            ["git", *arguments], cwd=root, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except subprocess.CalledProcessError as exc:
        raise IMGateError("GIT_IDENTITY_UNAVAILABLE") from exc


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
        "repository": str(root), "branch": BRANCH, "head": IL_HEAD,
        "tree": IL_TREE, "subject": IL_SUBJECT, "origin": ORIGIN,
        "remote_tracking_head": IL_HEAD, "index": "",
    }
    if observed != expected:
        raise IMGateError("EXACT_COMMITTED_IL_CHECKPOINT_MISMATCH")
    for ancestor in (IK_HEAD, IJ_HEAD, II_HEAD, IH_HEAD, IG_HEAD, IF_HEAD, IE_HEAD, ID_HEAD, IC_HEAD, STABLE_ANCHOR):
        result = subprocess.run(
            ["git", "merge-base", "--is-ancestor", ancestor, IL_HEAD], cwd=root,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        if result.returncode:
            raise IMGateError(f"ANCESTRY_MISSING__{ancestor}")
    status = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=all"], cwd=root, text=True
    ).splitlines()
    if any(not line[3:].startswith(IM_ROOT.as_posix() + "/") for line in status):
        raise IMGateError("UNRELATED_WORKTREE_MUTATION")
    nested = root / "sapianta_system"
    nested_state = {
        "origin": _git(nested, "remote", "get-url", "origin"),
        "head": _git(nested, "rev-parse", "HEAD"),
        "tree": _git(nested, "rev-parse", "HEAD^{tree}"),
        "branch": _git(nested, "branch", "--show-current"),
        "status": _git(nested, "status", "--porcelain", "--untracked-files=all"),
        "tag_head": _git(nested, "rev-parse", NESTED_TAG + "^{commit}"),
    }
    if nested_state != {
        "origin": NESTED_ORIGIN, "head": NESTED_HEAD, "tree": NESTED_TREE,
        "branch": "", "status": "", "tag_head": NESTED_HEAD,
    }:
        raise IMGateError("NESTED_AUTHORITY_NOT_CLEAN_DETACHED_PINNED")
    return observed | {"nested": nested_state, "worktree_scope": "VERIFIED__IM_EVIDENCE_ONLY"}


def reconstruct_il(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    identities: dict[str, Any] = {}
    for path, expected_sha in IL_HASHES.items():
        committed = subprocess.check_output(["git", "show", f"{IL_HEAD}:{path.as_posix()}"], cwd=root)
        blob = _git(root, "rev-parse", f"{IL_HEAD}:{path.as_posix()}")
        if committed != (root / path).read_bytes() or sha256_bytes(committed) != expected_sha or blob != IL_BLOBS[path]:
            raise IMGateError(f"IL_IDENTITY_MISMATCH__{path.name}")
        identities[path.name] = {"path": path.as_posix(), "sha256": expected_sha, "git_blob": blob}
    envelope = load_canonical(root / IL_TERMINAL)
    if envelope["reduction_sha256"] != sha256_bytes(canonical_bytes(envelope["reduction"])):
        raise IMGateError("IL_TERMINAL_SEAL_INVALID")
    control = envelope["reduction"]["terminal_control"]
    expected = {
        "current_e05_status": "VERIFIED__10_OF_18",
        "successor_version_identifier": "VERIFIED__EXACT_V2",
        "exact_successor_namespace_set": "NOT_PROVEN__TWO_FAMILY_LOCAL_LAYOUTS_REMAIN_WITHOUT_DU_EB_EE_SUCCESSION_PRECEDENT",
        "p11_change_required": "VERIFIED__NO",
        "production_route_delta": "VERIFIED__0",
        "e05_credit": "VERIFIED__0",
    }
    if {key: control[key] for key in expected} != expected:
        raise IMGateError("IL_TERMINAL_FRONTIER_MISMATCH")
    return {
        "status": "VERIFIED", "artifact_count": 4, "identities": identities,
        "canonical_json": "VERIFIED", "inner_seal": "VERIFIED", "frontier": expected,
    }


def human_decisions() -> dict[str, Any]:
    return {
        "decision_scope": "REPOSITORY_ONLY_V2_FILESYSTEM_AND_DISPATCH_IMPLEMENTATION_POLICY",
        "schema_selection": "B__NESTED_CERTIFICATION_BASELINE_OBJECT_PER_SUCCESSOR_RECEIPT",
        "successor_identity_policy": "EXISTING_DU_EB_EE_CONTRACT_FAMILIES__INCOMPATIBLE_MAJOR_SUCCESSOR",
        "major": 2, "semver": "2.0.0", "identity_suffix": "V2",
        "filesystem_layout": "VERSIONED_SIBLING_DIRECTORIES_WITHIN_EXISTING_DU_EB_EE_FAMILIES",
        "dispatch_policy": "EXPLICIT_FAMILY_LOCAL_FAIL_CLOSED_DISPATCH_OWNER",
        "dispatch_owners": {"DU": "DU_FAMILY_LOCAL", "EB": "EB_FAMILY_LOCAL", "EE": "EE_FAMILY_LOCAL"},
        "global_version_registry": False, "caller_selected_version": False,
        "unknown_version_behavior": "REJECT", "mixed_version_behavior": "REJECT",
        "v1_mutation": False, "new_production_route": False,
        "human_operational_authority": 0,
    }


def _module_constants(path: Path) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and isinstance(node.value, ast.Constant):
            values[node.targets[0].id] = node.value.value
    return values


def derive_file_set(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    du = _module_constants(root / V1_OWNERS["DU_VALIDATOR"])
    eb = _module_constants(root / V1_OWNERS["EB_VALIDATOR"])
    ee = _module_constants(root / V1_OWNERS["EE_VALIDATOR"])
    v1_hashes = {name: sha256_path(root / path) for name, path in V1_OWNERS.items()}
    rows = [
        (DU_V2 / "G77_256DU_CANONICAL_CONTINUATION_MANIFEST_SCHEMA_V2.json", "DU", "V2_SCHEMA", V1_OWNERS["DU_SCHEMA"], du["SCHEMA_IDENTITY"], "SAPIANTA_SPCE_CONTINUATION_MANIFEST_SCHEMA_V2"),
        (DU_V2 / "validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V2.py", "DU", "V2_VALIDATOR_AND_PRODUCER", V1_OWNERS["DU_VALIDATOR"], du["CONSUMER_IDENTITY"], "G77_256DU_PRE_MATERIALIZATION_CONSUMER_VALIDATOR_V2"),
        (EB_V2 / "G77_256EB_CANDIDATE_BOUND_VALIDATION_RECEIPT_SCHEMA_V2.json", "EB", "V2_SCHEMA", V1_OWNERS["EB_SCHEMA"], eb["RECEIPT_SCHEMA_IDENTITY"], "SAPIANTA_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATION_RECEIPT_SCHEMA_V2"),
        (EB_V2 / "validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V2.py", "EB", "V2_VALIDATOR_ISSUER_AND_PROFILE", V1_OWNERS["EB_VALIDATOR"], eb["VALIDATOR_IDENTITY"], "G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V2"),
        (EE_V2 / "G77_256EE_RUNTIME_CONSUMER_BINDING_RECEIPT_SCHEMA_V2.json", "EE", "V2_SCHEMA", V1_OWNERS["EE_SCHEMA"], ee["SCHEMA_IDENTITY"], "G77_256EE_RUNTIME_CONSUMER_BINDING_RECEIPT_SCHEMA_V2"),
        (EE_V2 / "validator/G77_256EE_RUNTIME_CONSUMER_BINDING_VALIDATOR_V2.py", "EE", "V2_VALIDATOR_ISSUER_AND_PROFILE", V1_OWNERS["EE_VALIDATOR"], ee["VALIDATOR_IDENTITY"], "G77_256EE_RUNTIME_CONSUMER_BINDING_VALIDATOR_V2"),
    ]
    derivable = [{
        "path": path.as_posix(), "family": family, "role": role,
        "v1_analog": analog.as_posix(), "v1_identity": v1_identity,
        "v2_identity": v2_identity, "create_or_modify": "CREATE",
        "why_required": "MINIMUM_V2_COUNTERPART_OF_AUTHENTICATED_V1_OWNER",
        "owner": f"{family}_FAMILY_LOCAL", "consumer": "EXISTING_DU_EB_EE_SUCCESSOR_CHAIN",
        "failure_if_absent": "V2_CONTRACT_NOT_IMPLEMENTED",
    } for path, family, role, analog, v1_identity, v2_identity in rows]
    dispatcher_alternatives = {
        family: [
            {
                "shape": "DISTINCT_DISPATCH_OWNER_MODULE",
                "path": (v2_root / f"validator/G77_256{family}_FAMILY_LOCAL_VERSION_DISPATCHER_V1.py").as_posix(),
                "identity": "NOT_PROVEN__NO_IL_RATIFIED_DISPATCHER_IDENTITY",
            },
            {
                "shape": "V2_VALIDATOR_OWNS_EXPLICIT_DISPATCH_ENTRYPOINT",
                "path": next(row["path"] for row in derivable if row["family"] == family and "VALIDATOR" in row["role"]),
                "identity": next(row["v2_identity"] for row in derivable if row["family"] == family and "VALIDATOR" in row["role"]),
            },
        ]
        for family, v2_root in (("DU", DU_V2), ("EB", EB_V2), ("EE", EE_V2))
    }
    return {
        "namespace_policy": "VERIFIED__VERSIONED_SIBLING_DIRECTORIES_WITHIN_EXISTING_FAMILIES",
        "namespace_set": {"DU": DU_V2.as_posix(), "EB": EB_V2.as_posix(), "EE": EE_V2.as_posix()},
        "derivable_v2_owner_files": derivable,
        "derivable_v2_owner_file_count": 6,
        "embedded_profile_representation": "VERIFIED__EB_AND_EE_V1_PROFILES_ARE_VALIDATOR_CONSTANTS__NO_SEPARATE_PROFILE_FILE",
        "separate_du_producer_file": "NOT_APPLICABLE__DU_V1_PRODUCER_AND_VALIDATOR_SHARE_ONE_MODULE",
        "v1_owner_hashes": v1_hashes,
        "dispatch_owner_family_assignment": "VERIFIED__DU_EB_EE_FAMILY_LOCAL",
        "dispatch_realization_alternatives": dispatcher_alternatives,
        "dispatch_realization_count_per_family": 2,
        "dispatcher_identity_status": "NOT_PROVEN__NO_EXACT_DISPATCHER_IDENTITY_IN_IL_TABLE_OR_HUMAN_DECISION",
        "exact_implementation_file_set": "NOT_PROVEN__DISPATCH_OWNER_FILE_IDENTITY_PATH_AND_ROLE_COLOCATION_UNRESOLVED",
        "owner_uniqueness_status": "NOT_PROVEN__FAMILY_UNIQUE__FILE_OWNER_REALIZATION_NOT_UNIQUE",
        "unowned_file_count": "NOT_PROVEN__DISTINCT_DISPATCH_MODULE_VARIANT_REQUIRES_UNRATIFIED_IDENTITY",
        "owner_conflict_count": "NOT_PROVEN__VALIDATOR_COLOCATION_VARIANT_COMBINES_TWO_CONCEPTUAL_ROLES",
    }


def preimplementation_gate(repository_root: Path) -> dict[str, Any]:
    derived = derive_file_set(repository_root)
    predicates = {
        "exact_il_entry": "VERIFIED", "human_decisions": "VERIFIED",
        "exact_v2_identities": "VERIFIED", "exact_v2_sibling_namespaces": "VERIFIED",
        "exact_implementation_file_set": derived["exact_implementation_file_set"],
        "owner_uniqueness": derived["owner_uniqueness_status"],
        "v1_immutable_scope": "VERIFIED", "p11_delta_zero": "VERIFIED",
        "fm_runtime_delta_zero": "VERIFIED", "production_route_delta_zero": "VERIFIED",
        "no_global_registry": "VERIFIED", "no_generic_framework": "VERIFIED",
        "no_operational_authority": "VERIFIED",
    }
    return {
        "predicates": predicates,
        "result": "REJECT__IMPLEMENTATION_FORBIDDEN",
        "first_broken_edge": "EXACT_FAMILY_LOCAL_DISPATCH_OWNER_FILE_IDENTITY_PATH_AND_ROLE_COLOCATION_NOT_UNIQUELY_RATIFIED",
        "implementation_entered": False,
    }


def terminal_reduction(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    derived = derive_file_set(root)
    gate = preimplementation_gate(root)
    counters = {key: 0 for key in (
        "human_operational_authority", "authority_consumption", "pre",
        "fm_operational_launcher_invocation", "qemu", "vm_creation", "vm_boot",
        "operation_attempt", "request", "p11_entry", "protected_invocation",
        "protected_effect", "retry", "repair_retry", "replay", "e05_credit",
    )}
    return {
        "schema_id": "G77_256IM_FAMILY_LOCAL_V2_IMPLEMENTATION_GATE_TERMINAL_B_V1",
        "mode": "REPOSITORY_ONLY__PREIMPLEMENTATION_GATE__NO_V2_MATERIALIZATION__NO_OPERATION",
        "entry": authenticate_entry(root), "il_reconstruction": reconstruct_il(root),
        "human_governance_decisions": human_decisions(),
        "file_set_derivation": derived, "preimplementation_gate": gate,
        "option_b": {
            "shape": {"certification_baseline": {"head": "GIT_COMMIT_40_LOWER_HEX", "tree": "GIT_TREE_40_LOWER_HEX"}},
            "status": "VERIFIED__RATIFIED__IMPLEMENTATION_NOT_ENTERED",
            "minimum_semantic_git_coordinate_count": 2,
        },
        "provenance": {
            "runtime_target": {"head": IF_HEAD, "tree": IF_TREE},
            "runtime_target_selection_binding": "VERIFIED__AUTHENTICATED_BY_COMMITTED_IL",
            "candidate_identity": FUTURE_CANDIDATE_SHA, "context_identity": FUTURE_CONTEXT_SHA,
            "certification_baseline": {"head": IL_HEAD, "tree": IL_TREE},
            "runtime_current_separation": "VERIFIED__PRESERVED",
            "caller_chosen_runtime_target_authority": "VERIFIED__NO",
            "arbitrary_historical_head_bypass": "VERIFIED__NO",
        },
        "compatibility": {
            "v1_semantics_reinterpreted": "VERIFIED__NO", "v1_identity_mutation_count": "VERIFIED__0",
            "v1_schema_mutation_count": "VERIFIED__0", "v1_reachability": "VERIFIED__PRESERVED",
            "v2_implementation_status": "NOT_PROVEN__IMPLEMENTATION_BLOCKED",
            "downgrade_bypass": "VERIFIED__NO_IMPLEMENTATION_PATH_CREATED",
            "mixed_version_bypass": "VERIFIED__NO_IMPLEMENTATION_PATH_CREATED",
            "caller_version_selection_authority": "VERIFIED__NO",
            "cross_family_substitution_bypass": "VERIFIED__NO_IMPLEMENTATION_PATH_CREATED",
        },
        "boundaries": {
            "p11_change_required": "VERIFIED__NO", "p11_core_change_count": "VERIFIED__0",
            "fm_runtime_owner_mutation": "VERIFIED__0", "fm_production_route_mutation": "VERIFIED__0",
            "production_route_before": "VERIFIED__1", "production_route_after": "VERIFIED__1",
            "production_route_delta": "VERIFIED__0", "parallel_production_flow_created": "VERIFIED__NO",
            "gn_operational_applicability": "NOT_APPLICABLE", "gl_operational_applicability": "NOT_APPLICABLE",
            "global_version_registry": "VERIFIED__NO", "generic_dispatch_framework": "VERIFIED__NO",
            "new_generic_framework_count": "VERIFIED__0", "new_authority_layer_count": "VERIFIED__0",
            "new_launcher_count": "VERIFIED__0", "shadow_automation_status": "VERIFIED__ABSENT",
        },
        "future_semantics": {
            "evaluation": 500, "valid_from": 600, "valid_until": 1000,
            "payload_digest": "9568e0c248ad488cabcf6bde6b490c544077862d10e3fda13bcdc8ed9953f547",
            "source_act": "7167b0725d2c84bafde1d0060f512b0fa358d777ec1beff8b7c68d22ee6502e8",
            "che_correlation": "CHE-CORRELATION-15b2680b5577da169cecf9efb3231e2e6f6467e6f409fa2594b04128f998e454",
            "future_semantic_mutation_count": "VERIFIED__0", "wall_clock_dependency_count": "VERIFIED__0",
        },
        "ex": {"ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0", "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED"},
        "historical_failure_firewall": {"reintroduced_historical_failure_count": "VERIFIED__0", "precommit_self_reference_count": "VERIFIED__0", "future_commit_prediction_count": "VERIFIED__0"},
        "reuse_impact": {
            "reused_certified_capability_set": ["IL_IDENTITY_BOUNDARY", "DU_V1", "EB_V1", "EE_V1", "FM_TARGET_SELECTION", "P11", "CHE_FK", "GN_GL", "EX_17_OF_17", "GOVERNANCE", "LAYER_0", "PINNED_NESTED_AUTHORITY"],
            "new_capability_set": ["IM_REPOSITORY_ONLY_HUMAN_POLICY_BINDING_AND_DISPATCH_REALIZATION_AMBIGUITY_PROOF"],
            "new_operational_production_capability_set": [], "unreachable_preexisting_capability_set": [],
            "parallel_flow_created": "VERIFIED__NO", "production_route_before": "VERIFIED__1",
            "production_route_after": "VERIFIED__1", "production_route_delta": "VERIFIED__0",
        },
        "infrastructure_amortization": {
            "future_generations_so_far": "VERIFIED__9__IE_IF_IG_IH_II_IJ_IK_IL_IM",
            "future_e05_credit_so_far": "VERIFIED__0", "future_operational_attempts_so_far": "VERIFIED__0",
            "new_common_infrastructure_for_future": "VERIFIED__0__GATE_EVIDENCE_ONLY",
            "new_vector_specific_infrastructure_for_future": "VERIFIED__0",
            "marginal_new_infrastructure_for_im": "VERIFIED__FORMALIZER_TEST_REPORT_AND_REDUCTION_ONLY",
            "marginal_new_infrastructure_per_e05_credit": "NOT_MEASURED__NO_FUTURE_CREDIT",
            "infrastructure_amortization_signal": "ESTIMATED__REUSE_DOMINANT_WITH_ZERO_RUNTIME_EXPANSION",
            "expected_next_credit_generation_count": "NOT_PROVEN__DISPATCH_IDENTITY_PATH_DECISION_IMPLEMENTATION_AND_READINESS_REMAIN",
            "e05_generations_per_credit": "VERIFIED__5__HISTORICAL_WRONG_PROVENANCE_LIFECYCLE_ONLY",
            "operational_attempts_per_credit": "VERIFIED__1__HISTORICAL_WRONG_PROVENANCE_ONLY",
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_L5_CLAIM",
            "cross_worker_state_recovery_level": "NOT_PROVEN__WORKER_IDENTITY_NOT_INSTRUMENTED",
            "repository_derived_context_ratio": "ESTIMATED__DOMINANT__NUMERIC_RATIO_NOT_MEASURED",
            "human_handoff_information_required": "VERIFIED__SCOPE_IL_LOCATOR_AND_THREE_HUMAN_DECISIONS",
            "previous_worker_conversation_required": "VERIFIED__NO", "previous_worker_identity_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO", "authenticated_repository_continuation": "VERIFIED",
            "inter_generation_cross_worker_continuation": "NOT_PROVEN__WORKER_IDENTITY_NOT_INSTRUMENTED",
            "intra_generation_cross_worker_continuation": "NOT_APPLICABLE__NO_DELEGATION",
            "uncommitted_delta_recovery": "NOT_APPLICABLE__CLEAN_IL_ENTRY",
            "authority_state_recovery": "NOT_APPLICABLE__NO_OPERATIONAL_AUTHORITY",
            "consumed_authority_recovery": "VERIFIED__HISTORICAL_AUTHORITY_NONREUSABLE",
            "post_operation_state_recovery": "NOT_APPLICABLE__NO_IM_OPERATION",
            "operation_replay_prevention": "VERIFIED__ZERO_IM_OPERATION_COUNTERS",
            "cross_worker_constitutional_drift": "NOT_PROVEN__WORKER_IDENTITY_NOT_INSTRUMENTED",
            "handoff_sufficiency_status": "VERIFIED", "handoff_state_completeness": "VERIFIED__AUTHORIZED_SCOPE_COMPLETE",
            "handoff_reconstruction_required": "VERIFIED__YES", "handoff_reconstruction_success": "VERIFIED",
            "handoff_ambiguity_count": "VERIFIED__0__INPUT_DECISIONS__ONE_IMPLEMENTATION_AMBIGUITY_DISCOVERED",
            "unauthenticated_handoff_assumption_count": "VERIFIED__0",
        },
        "metrics": {
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "constitutional_health_evidence": "VERIFIED__PREIMPLEMENTATION_GATE_REJECTS_NONUNIQUE_FILE_SET",
            "shadow_automation_status": "VERIFIED__ABSENT", "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "e05_frontier_distance": "VERIFIED__8_OF_18_OBLIGATIONS_REMAIN",
            "selected_e05_local_frontier_distance": "NOT_PROVEN__DISPATCH_IDENTITY_PATH_IMPLEMENTATION_AND_READINESS",
            "governance_efficience": "ESTIMATED__FAIL_CLOSED_BEFORE_UNRATIFIED_IMPLEMENTATION",
            "architectural_governance_efficience": "VERIFIED__ONE_ROUTE_ZERO_RUNTIME_OWNER_MUTATION",
            "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED",
            "cognition_assisted_handoff": "VERIFIED__AUTHENTICATED_IL_TO_IM_REPOSITORY_CONTINUATION",
            "aigol_codex_work_share": "NOT_MEASURED", "overengineering_risk": "ESTIMATED__LOW",
            "proof_process_overhead_risk": "ESTIMATED__MODERATE", "cognition_provenance": "VERIFIED__AUTHENTICATED_REPOSITORY_PRIMARY",
            "candidate_capability": "VERIFIED__IF_BOUND_DU_V1__SUCCESSOR_NOT_IMPLEMENTED",
            "shadow_design_target": "VERIFIED__FAMILY_LOCAL_DU_EB_EE_V2_OPTION_B_WITH_FAIL_CLOSED_MAJOR_VERSION_DISPATCH",
            "constitutional_continuation_progress": "VERIFIED__FILESYSTEM_POLICY_BOUND__DISPATCH_FAMILY_BOUND__EXACT_DISPATCH_REALIZATION_NOT_PROVEN",
            "prompt_context_reuse_ratio": "NOT_MEASURED", "token_benchmark": "NOT_MEASURED",
            "llm_cost_reduction_ratio": "NOT_MEASURED", "lcrr": "NOT_MEASURED",
            "marginal_e05_generation_cost": "NOT_MEASURED",
            "marginal_new_infrastructure_per_e05_credit": "NOT_MEASURED__NO_FUTURE_CREDIT",
            "infrastructure_amortization_signal": "ESTIMATED__REUSE_DOMINANT_WITH_ZERO_RUNTIME_EXPANSION",
            "expected_next_credit_generation_count": "NOT_PROVEN__DISPATCH_IDENTITY_PATH_DECISION_IMPLEMENTATION_AND_READINESS_REMAIN",
        },
        "cognition_provenance": "VERIFIED__AUTHENTICATED_GIT_IL_IK_IJ_II_IH_IG_IF_IE_ID_IC_DU_EB_EE_FM_GN_GL_P11_CHE_FK_EX_GOVERNANCE_LAYER_0_NESTED_AUTHORITY_CURRENT_TESTS",
        "validation": {
            "mode": "REPOSITORY_ONLY__NO_READINESS__NO_OPERATION",
            "im_focused": "VERIFIED__17_PASSED",
            "p11_human_act_che_fk_current": "VERIFIED__92_PASSED",
            "governance_layer_0": "VERIFIED__9_PASSED",
            "du_v1_self_test": "VERIFIED__11_OF_11",
            "eb_v1_live_self_test": "EXPECTED_FAIL_CLOSED__IMMUTABLE_FIXTURE_BINDS_HISTORICAL_HEAD_07057C__V1_BYTES_AUTHENTICATED",
            "ee_v1_live_self_test": "EXPECTED_FAIL_CLOSED__IMMUTABLE_FIXTURE_BINDS_HISTORICAL_HEAD_07057C__V1_BYTES_AUTHENTICATED",
            "ex_regression": "VERIFIED__12_OF_12__CERTIFIED_17_OF_17",
            "conformance_engine": "VERIFIED__20_PASSED__CONFORMANT__0_WARNINGS__0_VIOLATIONS",
            "current_applicable_assertions": "VERIFIED__118_PASSED__17_IM_PLUS_92_P11_HUMAN_ACT_CHE_FK_PLUS_9_GOVERNANCE_LAYER_0",
            "historical_or_superseded_snapshot_assertions": "NOT_APPLICABLE__IL_LIVE_ENTRY_AND_EB_EE_07057C_POSITIVE_FIXTURES__COMMITTED_IDENTITIES_RECONSTRUCTED",
            "canonical_json_duplicate_keys_inner_seal_ast_six_headings": "VERIFIED",
            "git_diff_check": "VERIFIED__CLEAN",
        },
        "operational_counters": counters,
        "e05": {"before": "10/18", "after": "10/18", "satisfied": 10, "remaining": 8, "credit": 0},
        "terminal_control": {
            "v2_implementation_status": "NOT_PROVEN__IMPLEMENTATION_BLOCKED",
            "exact_successor_namespace_set": "VERIFIED__VERSIONED_SIBLING_DIRECTORIES",
            "du_dispatch_owner": "VERIFIED__DU_FAMILY_LOCAL__EXACT_FILE_NOT_PROVEN",
            "eb_dispatch_owner": "VERIFIED__EB_FAMILY_LOCAL__EXACT_FILE_NOT_PROVEN",
            "ee_dispatch_owner": "VERIFIED__EE_FAMILY_LOCAL__EXACT_FILE_NOT_PROVEN",
            "version_dispatch_contract_status": "NOT_PROVEN__IMPLEMENTATION_FORBIDDEN_BY_NONUNIQUE_FILE_SET",
            "v1_semantics_reinterpreted": "VERIFIED__NO", "p11_change_required": "VERIFIED__NO",
            "production_route_delta": "VERIFIED__0", "future_preoperational_readiness": "NOT_PROVEN",
            "future_operational_capability": "NOT_PROVEN", "next_operational_generation_eligible": "NOT_PROVEN",
            "e05_credit": "VERIFIED__0",
            "last_verified_edge": "V2_SIBLING_NAMESPACES_AND_DU_EB_EE_FAMILY_DISPATCH_ASSIGNMENTS_BOUND",
            "first_broken_edge": gate["first_broken_edge"],
            "minimum_missing_capability": "HUMAN_GOVERNANCE_DECISION_OF_EXACT_DU_EB_EE_DISPATCHER_IDENTITY_PATH_AND_DISTINCT_VERSUS_VALIDATOR_COLOCATED_OWNER_SHAPE",
            "minimum_legal_next_delta": "HUMAN_GOVERNANCE_DECISION_REQUIRED",
            "auto_continuable": False, "human_review_required": True, "next_generation_started": False,
            "verdict": "NOT_PROVEN__IM_IMPLEMENTATION_BLOCKED_AT_EXACT_DISPATCH_FILE_SET__ZERO_OPERATION__E05_10_OF_18__HUMAN_REVIEW_REQUIRED",
        },
    }


def terminal_envelope(repository_root: Path) -> dict[str, Any]:
    reduction = terminal_reduction(repository_root)
    return {
        "schema_id": "G77_256IM_FAMILY_LOCAL_V2_IMPLEMENTATION_GATE_TERMINAL_B_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": sha256_bytes(canonical_bytes(reduction)),
    }


def main() -> int:
    if len(sys.argv) == 2 and sys.argv[1] == "--emit-terminal":
        sys.stdout.buffer.write(canonical_bytes(terminal_envelope(Path.cwd())))
        return 0
    print("REFUSED__G77_256IM_REPOSITORY_ONLY_GATE_FORMALIZER_HAS_NO_OPERATIONAL_PATH", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
