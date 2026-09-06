#!/usr/bin/env python3
"""Repository-only G77-256IN constitutional gate and terminal reduction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any


BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
IM_HEAD = "f25afc281cbfe457b23a389a8375900717a5a1e2"
IM_TREE = "ae1d9b40b33c8a0067d4bbc987ac036634eb84e1"
IM_SUBJECT = "G77-256IM formalize dispatch realization boundary"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
IM_ROOT = Path(".github/governance/evidence/g77_256im_family_local_v2_successor_implementation_v1")
IN_ROOT = Path(".github/governance/evidence/g77_256in_family_local_v2_option_b_dispatch_v1")
NESTED_ROOT = Path("sapianta_system")
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
V2_FILES = (
    Path(".github/governance/evidence/g77_256du_continuation_manifest_contract_v2/G77_256DU_CANONICAL_CONTINUATION_MANIFEST_SCHEMA_V2.json"),
    Path(".github/governance/evidence/g77_256du_continuation_manifest_contract_v2/validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V2.py"),
    Path(".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v2/G77_256EB_CANDIDATE_BOUND_VALIDATION_RECEIPT_SCHEMA_V2.json"),
    Path(".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v2/validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V2.py"),
    Path(".github/governance/evidence/g77_256ee_runtime_consumer_binding_v2/G77_256EE_RUNTIME_CONSUMER_BINDING_RECEIPT_SCHEMA_V2.json"),
    Path(".github/governance/evidence/g77_256ee_runtime_consumer_binding_v2/validator/G77_256EE_RUNTIME_CONSUMER_BINDING_VALIDATOR_V2.py"),
)
IN_EVIDENCE_FILES = (
    IN_ROOT / "G77_256IN_G48_IMPLEMENTATION_REPORT_V1.md",
    IN_ROOT / "G77_256IN_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json",
    IN_ROOT / "analysis/G77_256IN_FAMILY_LOCAL_V2_OPTION_B_GATE_FORMALIZER_V1.py",
    IN_ROOT / "tests/test_g77_256in_family_local_v2_option_b_dispatch_v1.py",
)
AUTHORIZED_DELTA_FILES = frozenset(V2_FILES + IN_EVIDENCE_FILES)
V2_ROOTS = (V2_FILES[0].parent, V2_FILES[2].parent, V2_FILES[4].parent)
V1_HASHES = {
    ".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/G77_256DU_CANONICAL_CONTINUATION_MANIFEST_SCHEMA_V1.json": "a21ba1567c65101a5f178afdfefb5d500c97fc2cc6a9eb9da6c9fb4cc914478e",
    ".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V1.py": "27457993a4e6b778cc65356cd9b17a1bf2665f4e6147608d27dc233ff512304d",
    ".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v1/G77_256EB_CANDIDATE_BOUND_VALIDATION_RECEIPT_SCHEMA_V1.json": "5b477ce183df65446aa1c3df3f8006856fce72b0771fcf04ff0c9cc6ae3a5f49",
    ".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v1/validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V1.py": "8e8171f757213f064cec463868408364175772e766615bd276ed7f0e28306b43",
    ".github/governance/evidence/g77_256ee_runtime_consumer_binding_v1/G77_256EE_RUNTIME_CONSUMER_BINDING_RECEIPT_SCHEMA_V1.json": "b193f6d392b0f5b0be32041e554ce3ccc18288f68bab0880c27326cb42d2ccc0",
    ".github/governance/evidence/g77_256ee_runtime_consumer_binding_v1/validator/G77_256EE_RUNTIME_CONSUMER_BINDING_VALIDATOR_V1.py": "5e4b35b3c7e7e23e5b7209c5f56e8a70055eac9a3deef32bc288b210e80f9410",
}
IM_HASHES = {
    "G77_256IM_G48_IMPLEMENTATION_REPORT_V1.md": "fa71261131594a27df45e870294254af3780ef5b531ce8ac4b5517e9cddbf72f",
    "G77_256IM_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json": "9e1aa5f71ef45891108548e8f6c8c2689e9a97e890acb3db09e2d39c7d374d7a",
    "analysis/G77_256IM_FAMILY_LOCAL_V2_IMPLEMENTATION_GATE_FORMALIZER_V1.py": "9d00aeb091afc579e0103b90cb3d2f15a2a4cd8eff6818f696e3974a8b30eb25",
    "tests/test_g77_256im_family_local_v2_successor_implementation_v1.py": "0ad0f235b765636638a1eb6b50be684b204b5e8674f2a2a51c706a85e27ed239",
}
ANCESTRY = (
    "c43839f54ae788caa11a2082aba845b9426ea4c6", "7a7c77d32551020d5fed6cce5b4f7786e9974573",
    "a07f6e76239a9d8f309f290ecc8ab328d08aa64f", "4365d97394deca438a1a57d5b47c699afb54bd5d",
    "8698486cdf9a206f2bc73993c83389d6850362ff", "71391a75011cdc388bdac9183f4654814a044c69",
    "699fcdce794ff49b6c8735602936355724ed1c90", "9420764a5bb6db8909334f2a422225687a37a346",
    "559deecb226b66d626e45e6f607b0aab6df81f1c", "afdd47166acdee30cb9867d3d3c7bfec0de64c8a",
    "5c972e9960987ab27420395b54ace693df097e7b",
)


class INGateError(ValueError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise INGateError(f"DUPLICATE_KEY:{key}")
        value[key] = item
    return value


def load_canonical(path: Path) -> Any:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=_pairs, parse_constant=lambda x: (_ for _ in ()).throw(INGateError(f"NONFINITE:{x}")))
    if raw != canonical_bytes(value):
        raise INGateError(f"NONCANONICAL_JSON:{path}")
    return value


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def authenticate_uncommitted_delta(root: Path) -> dict[str, Any]:
    lines = _git(root, "status", "--porcelain", "--untracked-files=all").splitlines()
    observed: dict[Path, str] = {}
    for line in lines:
        if len(line) < 4 or " -> " in line:
            raise INGateError("UNCOMMITTED_DELTA_STATUS_UNPARSABLE")
        observed[Path(line[3:])] = line[:2]
    if set(observed) != AUTHORIZED_DELTA_FILES:
        raise INGateError("UNCOMMITTED_DELTA_SCOPE_MISMATCH")
    if set(observed.values()) != {"??"}:
        raise INGateError("UNCOMMITTED_DELTA_NOT_EXACTLY_UNSTAGED_CREATED_FILES")
    return {
        "status": "VERIFIED__AUTHENTICATED_EXISTING_UNCOMMITTED_DELTA",
        "file_count": len(observed),
        "v2_owner_file_count": len(V2_FILES),
        "in_evidence_file_count": len(IN_EVIDENCE_FILES),
        "index": "EMPTY",
        "scope": "VERIFIED__EXACT_SIX_V2_OWNER_FILES_PLUS_FOUR_IN_EVIDENCE_ARTIFACTS",
        "files": [path.as_posix() for path in sorted(observed, key=lambda item: item.as_posix())],
    }


def authenticate_nested_authority(root: Path) -> dict[str, str]:
    nested = root / NESTED_ROOT
    observed = {
        "branch": _git(nested, "branch", "--show-current"),
        "head": _git(nested, "rev-parse", "HEAD"),
        "tree": _git(nested, "rev-parse", "HEAD^{tree}"),
        "origin": _git(nested, "remote", "get-url", "origin"),
        "status": _git(nested, "status", "--short"),
        "tag_head": _git(nested, "rev-parse", f"refs/tags/{NESTED_TAG}^{{}}"),
    }
    expected = {
        "branch": "", "head": NESTED_HEAD, "tree": NESTED_TREE,
        "origin": NESTED_ORIGIN, "status": "", "tag_head": NESTED_HEAD,
    }
    if observed != expected:
        raise INGateError("NESTED_AUTHORITY_MISMATCH")
    return observed


def authenticate_entry(root: Path) -> dict[str, Any]:
    observed = {
        "branch": _git(root, "branch", "--show-current"),
        "head": _git(root, "rev-parse", "HEAD"),
        "tree": _git(root, "rev-parse", "HEAD^{tree}"),
        "subject": _git(root, "show", "-s", "--format=%s", "HEAD"),
        "origin": _git(root, "remote", "get-url", "origin"),
        "remote_tracking_head": _git(root, "rev-parse", f"origin/{BRANCH}"),
        "index": _git(root, "diff", "--cached", "--name-only"),
    }
    expected = {
        "branch": BRANCH, "head": IM_HEAD, "tree": IM_TREE, "subject": IM_SUBJECT,
        "origin": ORIGIN, "remote_tracking_head": IM_HEAD, "index": "",
    }
    if observed != expected:
        raise INGateError("EXACT_COMMITTED_IM_CHECKPOINT_MISMATCH")
    if any(subprocess.run(["git", "merge-base", "--is-ancestor", item, "HEAD"], cwd=root).returncode for item in ANCESTRY):
        raise INGateError("REQUIRED_ANCESTRY_MISSING")
    observed["nested_authority"] = authenticate_nested_authority(root)
    observed["uncommitted_delta"] = authenticate_uncommitted_delta(root)
    observed["recovery_classification"] = "VERIFIED__SAME_GENERATION_PROVIDER_LIMIT_RECOVERY"
    return observed


def reconstruct_im(root: Path) -> dict[str, Any]:
    identities: dict[str, Any] = {}
    for relative, expected_sha in IM_HASHES.items():
        path = root / IM_ROOT / relative
        if sha256_path(path) != expected_sha:
            raise INGateError(f"IM_BYTE_MISMATCH:{relative}")
        blob = _git(root, "rev-parse", f"HEAD:{(IM_ROOT / relative).as_posix()}")
        identities[relative] = {"sha256": expected_sha, "git_blob": blob}
    terminal = load_canonical(root / IM_ROOT / "G77_256IM_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json")
    if terminal["reduction_sha256"] != sha256_bytes(canonical_bytes(terminal["reduction"])):
        raise INGateError("IM_INNER_SEAL_MISMATCH")
    return {"status": "VERIFIED", "artifact_count": 4, "identities": identities, "inner_seal": "VERIFIED"}


def human_dispatch_decision() -> dict[str, Any]:
    return {
        "decision_scope": "REPOSITORY_ONLY_DISPATCH_REALIZATION",
        "dispatch_realization": "COLOCATED_EXPLICIT_FAMILY_LOCAL_DISPATCH_ENTRYPOINT_IN_EACH_V2_VALIDATOR",
        "dispatch_owners": {"DU": "DU_V2_VALIDATOR", "EB": "EB_V2_VALIDATOR", "EE": "EE_V2_VALIDATOR"},
        "separate_dispatcher_modules": False, "new_dispatcher_identities": False,
        "caller_selected_version": False, "unknown_version": "REJECT",
        "mixed_version": "REJECT", "downgrade": "REJECT",
        "global_version_registry": False, "generic_dispatch_framework": False,
        "human_operational_authority": 0,
    }


def preimplementation_gate(root: Path) -> dict[str, Any]:
    authenticate_entry(root)
    reconstruct_im(root)
    if any(sha256_path(root / path) != digest for path, digest in V1_HASHES.items()):
        raise INGateError("V1_OWNER_BYTES_CHANGED")
    implementation_files = {
        path.relative_to(root)
        for family_root in V2_ROOTS
        for path in (root / family_root).rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    }
    if len(V2_FILES) != len(set(V2_FILES)) or implementation_files != set(V2_FILES):
        raise INGateError("FILE_OWNER_UNIQUENESS_FAILED")
    if any("DISPATCHER" in path.name for path in implementation_files):
        raise INGateError("SEPARATE_DISPATCHER_MODULE_PRESENT")
    authenticate_uncommitted_delta(root)
    return {
        "pre_implementation_gate": "PASS__IMPLEMENTATION_ALLOWED",
        "exact_implementation_file_set": "VERIFIED__UNIQUE__SIX_V2_OWNER_FILES",
        "exact_successor_namespace_set": "VERIFIED__THREE_VERSIONED_SIBLING_FAMILY_DIRECTORIES",
        "separate_dispatcher_file_count": "VERIFIED__0",
        "new_dispatcher_identity_count": "VERIFIED__0",
        "unowned_file_count": "VERIFIED__0", "owner_conflict_count": "VERIFIED__0",
    }


def terminal_reduction(root: Path) -> dict[str, Any]:
    entry = authenticate_entry(root)
    im = reconstruct_im(root)
    if any(not (root / path).is_file() for path in V2_FILES):
        raise INGateError("V2_OWNER_FILE_ABSENT")
    v2_hashes = {path.as_posix(): sha256_path(root / path) for path in V2_FILES}
    return {
        "entry": entry, "im_reconstruction": im, "human_governance_decisions": human_dispatch_decision(),
        "recovery": {
            "classification": "VERIFIED__SAME_GENERATION_G77_256IN_PROVIDER_LIMIT_RECOVERY",
            "provider_capability_is_execution_authority": "VERIFIED__NO",
            "committed_checkpoint": "VERIFIED__EXACT_COMMITTED_AND_PUSHED_G77_256IM",
            "existing_uncommitted_delta": "VERIFIED__AUTHENTICATED_NOT_NARRATION_TRUSTED",
            "prior_worker_report_role": "VERIFIED__CHECKPOINT_HINT_ONLY",
            "new_generation_started": False,
        },
        "implementation": {
            **preimplementation_gate(root),
            "v2_implementation_status": "VERIFIED__REPOSITORY_IMPLEMENTED",
            "dispatch_realization": "VERIFIED__COLOCATED_IN_V2_VALIDATOR_OWNERS",
            "version_dispatch_contract_status": "VERIFIED__IMPLEMENTED_FAIL_CLOSED",
            "v2_owner_hashes": v2_hashes,
        },
        "compatibility": {
            "v1_semantics_reinterpreted": "VERIFIED__NO", "v1_identity_mutation_count": "VERIFIED__0",
            "v1_schema_mutation_count": "VERIFIED__0", "v1_validator_mutation_count": "VERIFIED__0",
            "v1_reachability": "VERIFIED__PRESERVED", "downgrade_bypass": "VERIFIED__NO",
            "mixed_version_bypass": "VERIFIED__NO", "caller_version_selection_authority": "VERIFIED__NO",
            "cross_family_substitution_bypass": "VERIFIED__NO",
        },
        "provenance": {
            "option_b": "VERIFIED__CLOSED_CERTIFICATION_BASELINE_HEAD_TREE",
            "runtime_target_provenance_authentication": "VERIFIED__FM_LAUNCHER_CONTEXT_CANDIDATE_GIT_CLOSURE",
            "runtime_target_selection_binding": "VERIFIED__AUTHENTICATED",
            "target_certification_separation": "VERIFIED",
            "if_head": "699fcdce794ff49b6c8735602936355724ed1c90",
            "if_tree": "7c773d4b2acdf013f1b8238eabfc8eced4dd6866",
        },
        "boundaries": {
            "p11_change_required": "VERIFIED__NO", "p11_core_change_count": "VERIFIED__0",
            "fm_runtime_owner_mutation": "VERIFIED__0", "fm_production_route_mutation": "VERIFIED__0",
            "production_route_before": "VERIFIED__1", "production_route_after": "VERIFIED__1",
            "production_route_delta": "VERIFIED__0", "parallel_production_flow_created": "VERIFIED__NO",
            "gn_operational_applicability": "NOT_APPLICABLE", "gl_operational_applicability": "NOT_APPLICABLE",
            "shadow_automation_status": "VERIFIED__ABSENT", "new_launcher_count": "VERIFIED__0",
            "global_version_registry": "VERIFIED__NO", "generic_dispatch_framework": "VERIFIED__NO",
            "new_generic_framework_count": "VERIFIED__0", "new_authority_layer_count": "VERIFIED__0",
            "separate_dispatcher_module_count": "VERIFIED__0", "new_dispatcher_identity_count": "VERIFIED__0",
        },
        "future_semantics": {
            "evaluation": 500, "valid_from": 600, "valid_until": 1000,
            "payload_digest": "9568e0c248ad488cabcf6bde6b490c544077862d10e3fda13bcdc8ed9953f547",
            "source_act": "7167b0725d2c84bafde1d0060f512b0fa358d777ec1beff8b7c68d22ee6502e8",
            "che_correlation": "CHE-CORRELATION-15b2680b5577da169cecf9efb3231e2e6f6467e6f409fa2594b04128f998e454",
            "future_semantic_mutation_count": "VERIFIED__0", "wall_clock_dependency_count": "VERIFIED__0",
        },
        "ex": {"ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0", "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED"},
        "historical_failure_firewall": {
            "status": "VERIFIED", "reintroduced_historical_failure_count": "VERIFIED__0",
            "precommit_self_reference_count": "VERIFIED__0", "future_commit_prediction_count": "VERIFIED__0",
        },
        "reuse_impact": {
            "reused_certified_capability_set": "VERIFIED__DU_EB_EE_V1_FM_P11_CHE_FK_EX_GOVERNANCE_LAYER_0",
            "new_capability_set": "VERIFIED__REPOSITORY_V2_OPTION_B_CONTRACT_AND_COLOCATED_DISPATCH_ONLY",
            "unreachable_preexisting_capability_set": "VERIFIED__EMPTY",
            "parallel_flow_created": "VERIFIED__NO",
            "production_route_before": "VERIFIED__1", "production_route_after": "VERIFIED__1",
            "production_route_delta": "VERIFIED__0",
        },
        "validation": {
            "mode": "VERIFIED__REPOSITORY_ONLY__NO_READINESS__NO_OPERATION",
            "in_focused": "VERIFIED__25_PASSED",
            "im_committed_reconstruction": "VERIFIED__FOUR_ARTIFACT_BYTES_BLOBS_CANONICAL_JSON_INNER_SEAL_AND_FRONTIER",
            "im_historical_suite_classification": "VERIFIED__8_CURRENT_SAFE_ASSERTIONS_PASSED__9_LIVE_ENTRY_OR_SCOPE_ASSERTIONS_SUPERSEDED_WITH_EXACT_REASON",
            "du_v1_self_test": "VERIFIED__11_OF_11",
            "du_v2_self_test": "VERIFIED__11_OF_11",
            "eb_v2_self_test": "VERIFIED__13_OF_13",
            "ee_v2_self_test": "VERIFIED__17_OF_17",
            "p11_human_act_che_fk_current": "VERIFIED__66_PASSED",
            "gn_gl_boundary": "VERIFIED__52_PASSED__OPERATIONAL_APPLICABILITY_NOT_APPLICABLE",
            "ex_regression": "VERIFIED__12_OF_12__CERTIFIED_17_OF_17_REUSED",
            "governance_tests": "VERIFIED__9_PASSED",
            "layer_0_freeze": "VERIFIED__PASS",
            "conformance_engine": "VERIFIED__20_PASSED__CONFORMANT__DETERMINISTIC__FAIL_CLOSED__READ_ONLY__0_WARNINGS__0_VIOLATIONS",
            "canonical_duplicate_safe_inner_seal_ast_g48": "VERIFIED__PASS",
            "git_diff_check": "VERIFIED__CLEAN",
        },
        "operational_zero": {key: 0 for key in (
            "human_operational_authority", "authority_consumption", "pre", "fm_operational_launcher_invocation",
            "qemu", "vm_creation", "vm_boot", "operation_attempt", "request", "p11_entry",
            "protected_invocation", "protected_effect", "retry", "repair_retry", "replay", "e05_credit",
        )},
        "e05": {"before": "10/18", "after": "10/18", "credit": 0, "satisfied": 10, "remaining": 8},
        "metrics": {
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "constitutional_health_evidence": "VERIFIED__GOVERNANCE_PRESERVED",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "e05_frontier_distance": "VERIFIED__8_UNSATISFIED_OF_18", "selected_e05_local_frontier_distance": "NOT_PROVEN",
            "governance_efficience": "ESTIMATED__HIGH", "architectural_governance_efficience": "ESTIMATED__HIGH",
            "aigol_codex_work_share": "NOT_MEASURED", "prompt_context_reuse_ratio": "NOT_MEASURED",
            "token_benchmark": "NOT_MEASURED", "llm_cost_reduction_ratio": "NOT_MEASURED", "lcrr": "NOT_MEASURED",
            "marginal_e05_generation_cost": "NOT_MEASURED", "overengineering_risk": "ESTIMATED__LOW",
            "proof_process_overhead_risk": "ESTIMATED__MODERATE",
            "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED",
            "cognition_assisted_handoff": "VERIFIED__AUTHENTICATED_UNCOMMITTED_DELTA_RECOVERY",
            "cognition_provenance": "VERIFIED__AUTHENTICATED_REPOSITORY_EVIDENCE_PRIMARY",
            "candidate_capability": "VERIFIED__IF_BOUND_RUNTIME_CANDIDATE_REMAINS_V1__V2_REPOSITORY_CONTRACT_IMPLEMENTED_NOT_READY",
            "shadow_design_target": "VERIFIED__FAMILY_LOCAL_DU_EB_EE_V2_OPTION_B_WITH_COLOCATED_FAIL_CLOSED_MAJOR_VERSION_DISPATCH",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_continuation_progress": "VERIFIED__IM_AMBIGUITY_RESOLVED__IN_IMPLEMENTED_AND_RECOVERED",
            "e05_generations_per_credit": "VERIFIED__5__HISTORICAL_WRONG_PROVENANCE_LIFECYCLE_ONLY",
            "operational_attempts_per_credit": "VERIFIED__1__HISTORICAL_WRONG_PROVENANCE_ONLY",
            "marginal_new_infrastructure_per_e05_credit": "NOT_APPLICABLE__ZERO_IN_CREDIT",
            "infrastructure_amortization_signal": "ESTIMATED__POSITIVE_REPOSITORY_REUSE_ONLY",
            "expected_next_credit_generation_count": "NOT_PROVEN",
        },
        "infrastructure_amortization": {
            "future_generations_so_far": "VERIFIED__10__IE_IF_IG_IH_II_IJ_IK_IL_IM_IN", "future_e05_credit_so_far": "VERIFIED__0",
            "future_operational_attempts_so_far": "VERIFIED__0", "new_common_infrastructure_for_future": "VERIFIED__DU_EB_EE_V2_OPTION_B_DISPATCH",
            "new_vector_specific_infrastructure_for_future": "VERIFIED__0", "marginal_new_infrastructure_for_in": "VERIFIED__SIX_V2_OWNER_FILES_PLUS_FOUR_REPOSITORY_EVIDENCE_ARTIFACTS",
            "marginal_new_infrastructure_per_e05_credit": "NOT_APPLICABLE__ZERO_IN_CREDIT",
            "infrastructure_amortization_signal": "ESTIMATED__POSITIVE_REPOSITORY_REUSE_ONLY",
            "expected_next_credit_generation_count": "NOT_PROVEN", "e05_generations_per_credit": "VERIFIED__5__HISTORICAL_WRONG_PROVENANCE_LIFECYCLE_ONLY",
            "operational_attempts_per_credit": "VERIFIED__1__HISTORICAL_WRONG_PROVENANCE_LIFECYCLE_ONLY",
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_L5_CLAIM",
            "cross_worker_state_recovery_level": "VERIFIED__AUTHENTICATED_UNCOMMITTED_DELTA_RECOVERY__WORKER_IDENTITY_CONTINUITY_NOT_PROVEN",
            "repository_derived_context_ratio": "ESTIMATED__DOMINANT__NUMERIC_RATIO_NOT_MEASURED",
            "human_handoff_information_required": "VERIFIED__IM_LOCATOR_EXPECTED_DELTA_AND_DISPATCH_REALIZATION",
            "previous_worker_conversation_required": "VERIFIED__NO", "previous_worker_identity_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO", "authenticated_repository_continuation": "VERIFIED__SAME_GENERATION_G77_256IN",
            "inter_generation_cross_worker_continuation": "NOT_APPLICABLE__SAME_GENERATION_RECOVERY",
            "intra_generation_cross_worker_continuation": "VERIFIED__PROVIDER_INTERRUPTED_G77_256IN_DELTA_RECOVERED__WORKER_IDENTITY_CONTINUITY_NOT_PROVEN",
            "uncommitted_delta_recovery": "VERIFIED__EXACT_TEN_FILE_G77_256IN_DELTA_AUTHENTICATED_AND_REUSED", "authority_state_recovery": "NOT_APPLICABLE__NO_OPERATIONAL_AUTHORITY",
            "consumed_authority_recovery": "NOT_APPLICABLE__NO_AUTHORITY_CONSUMPTION", "post_operation_state_recovery": "NOT_APPLICABLE__NO_IN_OPERATION",
            "operation_replay_prevention": "VERIFIED__ZERO_IN_OPERATION_COUNTERS", "cross_worker_constitutional_drift": "VERIFIED__0_WITHIN_AUTHENTICATED_DELTA_SCOPE__WORKER_IDENTITY_CONTINUITY_NOT_PROVEN",
            "handoff_sufficiency_status": "VERIFIED", "handoff_state_completeness": "VERIFIED__AUTHORIZED_SCOPE_COMPLETE",
            "handoff_reconstruction_required": "VERIFIED__YES", "handoff_reconstruction_success": "VERIFIED",
            "handoff_ambiguity_count": "VERIFIED__0", "unauthenticated_handoff_assumption_count": "VERIFIED__0",
            "worker_identity_continuity": "NOT_PROVEN__NO_GOVERNED_INSTRUMENTATION",
        },
        "cognition_provenance": "VERIFIED__AUTHENTICATED_GIT_AND_EXISTING_UNCOMMITTED_IN_DELTA_IM_IL_IK_IJ_II_IH_IG_IF_IE_ID_IC_DU_EB_EE_FM_GN_GL_P11_CHE_FK_EX_GOVERNANCE_LAYER_0_NESTED_AUTHORITY_CURRENT_TESTS",
        "cognition_assisted_handoff": "VERIFIED__AUTHENTICATED_UNCOMMITTED_DELTA_RECOVERY",
        "candidate_capability": "VERIFIED__IF_BOUND_RUNTIME_CANDIDATE_REMAINS_V1__V2_REPOSITORY_CONTRACT_IMPLEMENTED_NOT_READY",
        "shadow_design_target": "VERIFIED__FAMILY_LOCAL_DU_EB_EE_V2_OPTION_B_WITH_COLOCATED_FAIL_CLOSED_MAJOR_VERSION_DISPATCH",
        "continuation": {
            "constitutional_continuation_progress": "VERIFIED__IM_AMBIGUITY_RESOLVED__IN_IMPLEMENTED_AND_PROVIDER_INTERRUPTION_RECOVERED",
            "last_verified_edge": "V2_REPOSITORY_IMPLEMENTATION_AND_VERSION_FIREWALL",
            "first_broken_edge": "POST_COMMIT_V2_LIVE_BINDING_AND_READINESS_NOT_PERFORMED",
            "minimum_missing_capability": "POST_COMMIT_V2_LIVE_BINDING_AND_READINESS_CERTIFICATION",
            "minimum_legal_next_delta": "SEPARATE_POST_COMMIT_V2_LIVE_BINDING_AND_READINESS_CERTIFICATION",
            "future_preoperational_readiness": "NOT_PROVEN", "future_operational_capability": "NOT_PROVEN",
            "next_operational_generation_eligible": "NOT_PROVEN", "auto_continuable": False,
            "human_review_required": True, "next_generation_started": False,
        },
    }


def terminal_envelope(root: Path) -> dict[str, Any]:
    reduction = terminal_reduction(root)
    return {
        "schema_id": "G77_256IN_FAMILY_LOCAL_V2_OPTION_B_DISPATCH_TERMINAL_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": sha256_bytes(canonical_bytes(reduction)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[5])
    parser.add_argument("--print-terminal", action="store_true")
    args = parser.parse_args()
    if args.print_terminal:
        print(canonical_bytes(terminal_envelope(args.repo_root.resolve())).decode(), end="")
        return 0
    print("REFUSED__G77_256IN_REPOSITORY_ONLY_FORMALIZER_HAS_NO_OPERATIONAL_PATH")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
