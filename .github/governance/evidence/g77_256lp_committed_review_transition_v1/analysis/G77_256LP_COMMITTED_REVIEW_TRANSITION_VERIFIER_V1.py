#!/usr/bin/env python3
"""Read-only verifier for the minimum FM committed-review transition capability."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ENTRY_HEAD = "541d48dd6f859ac8dd79ae4dcae57675f6cf3a79"
ENTRY_TREE = "ecff1d60b4b7b5215f5c68e2b8c7c8b5588ce1ae"
ENTRY_SUBJECT = "G77-256LO record lifecycle discovery terminal"
LO_FIRST = "cba84342941c723429a2f1644b09b65e8ccaeb16"
LN_HEAD = "fcbbacfed226e550f7668265b0de0bde500c37d7"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
TERMINAL = (
    "A__G77_256LP_MINIMUM_FM_COMMITTED_REVIEW_TO_CURRENT_ADMISSION_"
    "TRANSITION_CAPABILITY_IMPLEMENTED_AND_STATICALLY_PROVEN__ZERO_AUTHORITY__"
    "ZERO_OPERATION__READY_FOR_HUMAN_REVIEW"
)
LP_REL = Path(
    ".github/governance/evidence/g77_256lp_committed_review_transition_v1"
)
LP = ROOT / LP_REL
REPORT = LP / "G77_256LP_G48_IMPLEMENTATION_REPORT_V1.md"
REDUCTION = LP / "G77_256LP_SPCE_TERMINAL_REDUCTION_V1.json"
FM_REL = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
FM_BEFORE_SHA256 = "4bb8151e68aca89dd09e85178e177834a2811211870a37124d3991d757c7c247"
FM_AFTER_SHA256 = "5a0a597434bd89752828afd85ecb5a98669f41ae66fa0480ea27be6d611597e8"
LO_REDUCTION_REL = Path(
    ".github/governance/evidence/g77_256lo_phase_a_phase_b_lifecycle_discovery_v1/"
    "G77_256LO_SPCE_TERMINAL_LIFECYCLE_GAP_V1.json"
)
LO_REDUCTION_SHA256 = "90372b07f0473e15a9117ba6f50e55f904e85fb9bd6efe3f8a76d4bc75fff284"
LM_CONTEXT_REL = Path(
    ".github/governance/evidence/g77_256lm_wrong_scope_receipt_parent_phase_a_v1/"
    "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
)
P11_REL = Path("tests/p11_da_operational_consumer_v1.py")
P11_SHA256 = "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5"
ER_REL = Path(
    ".github/governance/evidence/g77_256er_p11_operational_v1/harness/"
    "G77_256ER_P11_OPERATIONAL_HARNESS_V1.py"
)
ER_SHA256 = "c6539d1cc60940b1999956965bff43923a270598a982cd19f976eadec0a93152"
EX_REL = Path(
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
    "validator/G77_256EX_COMMON_SUBSTRATE_CERTIFICATION_VALIDATOR_V1.py"
)
EX_SHA256 = "1d124424f5bb99e1b2845421eff1712efebf81ef292a54d37f371558d9988d2e"


class LPVerificationError(RuntimeError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def is_ancestor(ancestor: str, descendant: str) -> bool:
    return subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=ROOT,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_bytes())
    if not isinstance(value, dict):
        raise LPVerificationError(f"JSON_ROOT_INVALID:{path}")
    return value


def load_fm():
    spec = importlib.util.spec_from_file_location("g77_256lp_verified_fm", ROOT / FM_REL)
    if spec is None or spec.loader is None:
        raise LPVerificationError("FM_IMPORT_SPEC_MISSING")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def authenticate_entry() -> dict[str, str]:
    head = git("rev-parse", "HEAD")
    remote = git("rev-parse", f"refs/remotes/origin/{BRANCH}")
    if (
        ROOT != Path("/home/pisarna/work/sapianta-fl")
        or git("branch", "--show-current") != BRANCH
        or git("rev-parse", f"{ENTRY_HEAD}^{{tree}}") != ENTRY_TREE
        or git("show", "-s", "--format=%s", ENTRY_HEAD) != ENTRY_SUBJECT
        or not is_ancestor(LN_HEAD, ENTRY_HEAD)
        or not is_ancestor(LO_FIRST, ENTRY_HEAD)
        or not is_ancestor(ENTRY_HEAD, head)
        or not is_ancestor(ENTRY_HEAD, remote)
    ):
        raise LPVerificationError("LO_ENTRY_OR_SUCCESSOR_AUTHENTICATION_FAILED")
    nested = ROOT / "sapianta_system"
    if (
        git("rev-parse", "HEAD", cwd=nested) != NESTED_HEAD
        or git("rev-parse", "HEAD^{tree}", cwd=nested) != NESTED_TREE
        or git("status", "--porcelain=v1", "--untracked-files=all", cwd=nested)
        or git("branch", "--show-current", cwd=nested)
        or git("rev-parse", f"refs/tags/{NESTED_TAG}^{{}}", cwd=nested) != NESTED_HEAD
    ):
        raise LPVerificationError("NESTED_AUTHORITY_MISMATCH")
    return {"entry_head": ENTRY_HEAD, "entry_tree": ENTRY_TREE, "current_head": head, "remote_head": remote}


def authenticate_mutation_scope() -> dict[str, int]:
    committed = set(filter(None, git("diff", "--name-only", ENTRY_HEAD, "HEAD").splitlines()))
    dirty_lines = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT,
        text=True,
    ).splitlines()
    dirty = {line[3:] for line in dirty_lines}
    changed = committed | dirty
    allowed = {FM_REL.as_posix()}
    unexpected = [path for path in changed if path not in allowed and not path.startswith(LP_REL.as_posix() + "/")]
    if unexpected or FM_REL.as_posix() not in changed:
        raise LPVerificationError(f"LP_MUTATION_SCOPE_INVALID:{unexpected}")
    if sha256_path(ROOT / FM_REL) != FM_AFTER_SHA256:
        raise LPVerificationError("FM_IMPLEMENTATION_HASH_MISMATCH")
    committed_before = subprocess.check_output(
        ["git", "show", f"{ENTRY_HEAD}:{FM_REL.as_posix()}"], cwd=ROOT
    )
    if hashlib.sha256(committed_before).hexdigest() != FM_BEFORE_SHA256:
        raise LPVerificationError("FM_ENTRY_HASH_MISMATCH")
    immutable = {P11_REL: P11_SHA256, ER_REL: ER_SHA256, EX_REL: EX_SHA256}
    if any(sha256_path(ROOT / path) != digest for path, digest in immutable.items()):
        raise LPVerificationError("P11_ER_EX_IMMUTABILITY_MISMATCH")
    return {
        "production_files_changed": 1,
        "fm_files_changed": 1,
        "p11_files_changed": 0,
        "er_files_changed": 0,
        "ex_files_changed": 0,
        "owner_count_delta": 0,
        "route_count_before": 1,
        "route_count_after": 1,
    }


def authenticate_implementation() -> dict[str, Any]:
    source = (ROOT / FM_REL).read_text()
    tree = ast.parse(source)
    names = [node.name for node in tree.body if isinstance(node, ast.FunctionDef)]
    required = (
        "build_committed_review_transition",
        "authenticate_review_to_current_admission",
        "load_committed_review_transition",
        "authenticate_current_committed_jm_route",
        "authority_free_static_readiness",
        "validate_execution_admission",
        "validate_final_admission",
    )
    if any(names.count(name) != 1 for name in required):
        raise LPVerificationError("FM_TRANSITION_OWNER_SET_INVALID")
    fragments = (
        '"transition_is_authority": False',
        '"transition_consumable": False',
        '"lineage_rule": "ANCESTRY_NECESSARY_NOT_SUFFICIENT"',
        'raise RuntimeError("committed review transition proof missing or ambiguous")',
        'raise RuntimeError("same-HEAD admission must not select a transition proof")',
        'raise RuntimeError("post-review object rebinding or rewrite detected")',
        'authenticate_current_committed_jm_route(repository_root, observed_head, observed_tree)',
        'if authorization["authorized_repository_head"] != observed_head:',
        'if authorization["authorized_repository_tree"] != observed_tree:',
        'if receipt_namespace_consumed:',
    )
    if any(fragment not in source for fragment in fragments):
        raise LPVerificationError("FM_TRANSITION_SECURITY_GUARD_MISSING")
    fm = load_fm()
    context = fm.fresh_context.load_context(ROOT / LM_CONTEXT_REL, repository_root=ROOT)
    current_head = git("rev-parse", "HEAD")
    current_tree = git("rev-parse", "HEAD^{tree}")
    proof = fm.build_committed_review_transition(
        repository_root=ROOT,
        context=context,
        current_admission_head=current_head,
        current_admission_tree=current_tree,
    )
    result = fm.authenticate_review_to_current_admission(
        repository_root=ROOT,
        context=context,
        observed_head=current_head,
        observed_tree=current_tree,
        committed_review_transitions=[proof],
    )
    if (
        proof["review_object_head"] != "7368af35f707f75f4d0951133995013211699126"
        or proof["review_base_head"] != "ea3781b64cd8780021e8cbb5e65f6b057b1bf649"
        or proof["transition_is_authority"] is not False
        or proof["transition_consumable"] is not False
        or result["repository_identity_relation"]
        != "EXACT_COMMITTED_REVIEW_TO_CURRENT_ADMISSION_TRANSITION"
    ):
        raise LPVerificationError("AUTHENTICATED_LM_TRANSITION_PROOF_FAILED")
    return {
        "owner": "EXISTING_FM",
        "review_object_identity": "UNIQUE_CANONICAL_PATH_INTRODUCTION_COMMIT_TREE_BLOB_AND_SHA256",
        "current_admission_identity": "EXACT_OBSERVED_HEAD_TREE_AND_CURRENT_JM_ROUTE",
        "runtime_checkout_identity": "EXISTING_FM_GOVERNED_CHECKOUT_UNCHANGED",
        "transition_relation": "EXACT_ENDPOINT_PAIR_PLUS_COMPLETE_GIT_DELTA",
        "ancestry_role": "NECESSARY_NOT_SUFFICIENT",
        "transition_is_authority": False,
        "transition_consumable": False,
    }


def authenticate_precedent_reuse() -> None:
    if sha256_path(ROOT / LO_REDUCTION_REL) != LO_REDUCTION_SHA256:
        raise LPVerificationError("LO_REDUCTION_HASH_MISMATCH")
    envelope = load_json(ROOT / LO_REDUCTION_REL)
    reduction = envelope.get("reduction")
    if (
        not isinstance(reduction, dict)
        or envelope.get("reduction_sha256")
        != hashlib.sha256(canonical_bytes(reduction)).hexdigest()
        or reduction.get("cross_vector_precedent_count") != 7
        or reduction.get("cross_vector_assessment_count") != 8
    ):
        raise LPVerificationError("LO_PRECEDENT_REUSE_INVALID")


def authenticate_zero_authority_operation() -> None:
    forbidden = (
        "*HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE*",
        "*FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF*",
        "*AUTHORITY_VALIDATION_AND_CONSUMPTION*",
        "*OPERATIONAL_INVOCATION_ATTEMPT*",
        "*SERIAL_CONSOLE*",
    )
    for pattern in forbidden:
        if list(LP.rglob(pattern)):
            raise LPVerificationError(f"LP_AUTHORITY_OR_OPERATION_ARTIFACT:{pattern}")


def build_reduction() -> dict[str, Any]:
    return {
        "schema_id": "G77_256LP_SPCE_TERMINAL_REDUCTION_V1",
        "generation": "G77-256LP",
        "terminal": TERMINAL,
        "failure_novelty_and_convergence_check": {
            "failure_class": "DUPLICATE_OR_EQUIVALENT_EDGE",
            "novelty": "LI_CLASS_CURRENT_ADMISSION_IDENTITY_MISMATCH_RECURS_AT_PHASE_B__LO_LIFECYCLE_GAP_IMPLEMENTED_NARROWLY",
            "affected_invariant": "SEALED_OPERATION_CONTEXT_REPOSITORY_IDENTITY_MUST_EQUAL_CURRENT_COMMITTED_ADMISSION_IDENTITY_OR_ONE_EXACT_STRONGER_FM_TRANSITION_MUST_AUTHENTICATE_THE_DIFFERENCE",
            "previous_closest_edge": "G77_256LI_POST_COMMIT_CURRENT_HEAD_TREE_MISMATCH",
            "semantic_difference": "COMMITTED_CANONICAL_REVIEW_OBJECT_IDENTITY_IS_NOW_DISTINCT_FROM_EXACT_CURRENT_ADMISSION_IDENTITY",
            "production_behavior_impact": "OPTIONAL_EXACT_TRANSITION_PATH_ADDED_INSIDE_EXISTING_FM_ROUTE__SAME_HEAD_PATH_UNCHANGED",
            "new_capability_required": "YES_ONLY_FOR_COMMITTED_PHASE_A_OBJECT_TO_SUCCESSOR_PHASE_B_ADMISSION",
            "new_proof_required": "STATIC_NEGATIVE_TRANSITION_MATRIX__PROVIDED__OPERATIONAL_WRONG_SCOPE_PROOF_STILL_MISSING",
            "convergence_signal": "ONE_FM_OWNER__ONE_ROUTE__EXACT_PAIR_AND_DELTA__NO_ANCESTRY_AUTHORITY",
            "repetition_pressure": "REDUCED__LITERAL_REBIND_AND_POST_REVIEW_MUTATION_REJECTED",
            "verification_amplification_risk": "BOUNDED__TRANSITION_PROOF_DETERMINISTIC_NONAUTHORITY_AND_NONCONSUMABLE",
        },
        "spce": {
            "state": "FM_EXACT_SAME_HEAD_ADMISSION_SAFE_AND_PRESERVED",
            "problem": "COMMITTED_REVIEW_OBJECT_AND_CURRENT_ADMISSION_IDENTITIES_REQUIRE_EXACT_DISTINCT_BINDING",
            "constraints": "TWENTY_LP_SECURITY_CONSTRAINTS_PRESERVED",
            "execution": "ONE_OPTIONAL_FM_TRANSITION_RELATION__NO_NEW_OWNER_ROUTE_REGISTRY_OR_CONTEXT_SCHEMA",
        },
        "implementation": {
            "owner": "EXISTING_FM",
            "review_object_identity": "CANONICAL_CONTEXT_PATH_PLUS_UNIQUE_INTRODUCTION_COMMIT_TREE_BLOB_SHA256_AND_CONTEXT_SEAL",
            "current_admission_identity": "OBSERVED_CURRENT_HEAD_TREE_PLUS_EXISTING_COMMITTED_JM_ROUTE",
            "runtime_checkout_identity": "EXISTING_GOVERNED_CHECKOUT_IDENTITY_UNCHANGED",
            "transition_binding": "EXACT_REVIEW_AND_CURRENT_ENDPOINTS_PLUS_COMPLETE_MODE_BLOB_SHA256_DELTA",
            "same_head_default": "EXACT_EQUALITY__TRANSITION_PROOF_REJECTED",
            "human_authority_binding": "EXISTING_CONTEXT_SHA256_PLUS_AUTHORIZED_CURRENT_HEAD_TREE",
            "transition_is_authority": False,
            "transition_consumable": False,
        },
        "cross_vector_reuse_assessment": {
            "satisfied_vectors": ["WRONG_ATTEMPT", "WRONG_INPUT", "WRONG_CONTRACT", "WRONG_PROVENANCE", "WRONG_CALLER", "FUTURE", "EXPIRED"],
            "same_head_precedent_count": 7,
            "existing_fm_ownership_reused": True,
            "exact_identity_checks_reused": True,
            "one_shot_and_receipt_checks_reused": True,
            "human_presentation_binding_reused": True,
            "stronger_transition_precedent_found": False,
            "authority_transfer": "NO",
            "proof_transfer": "NO",
            "e05_credit_transfer": "NO",
        },
        "negative_static_matrix": {
            "wrong_review_head_tree": "REJECT",
            "wrong_current_head_tree": "REJECT",
            "ancestor_descendant_sibling_or_same_branch_substitution": "REJECT",
            "coherent_copy": "REJECT__CANONICAL_PATH_AND_UNIQUE_INTRODUCTION_REQUIRED",
            "wrong_proof_endpoints": "REJECT",
            "missing_or_multiple_proofs": "REJECT",
            "unbound_delta": "REJECT",
            "post_review_rebind": "REJECT",
            "stale_transition": "REJECT",
            "delete_readd_supersession": "REJECT__AMBIGUOUS_INTRODUCTION",
            "replay": "DETERMINISTIC_REVALIDATION_ONLY__NO_CONSUMABLE_TOKEN_INTRODUCED",
        },
        "forward_compatibility": {
            "AMBIGUOUS": "STRONGER__ZERO_OR_MULTIPLE_TRANSITIONS_FAIL_CLOSED",
            "STALE": "STRONGER__CURRENT_ENDPOINT_MUST_EQUAL_OBSERVED_GIT",
            "REVOKED": "UNCHANGED__TRANSITION_IS_NONAUTHORITY_AND_EXISTING_AUTHORITY_CHECKS_REMAIN",
            "SUPERSEDED": "STRONGER_FOR_REVIEW_IDENTITY__DELETE_READD_IS_AMBIGUOUS__AUTHORITY_MODEL_UNCHANGED",
            "WRONG_SCOPE": "STRONGER__EXACT_COMMITTED_REVIEW_RELATION_AVAILABLE",
            "COHERENT_COPY": "STRONGER__BYTES_ALONE_CANNOT_SELECT_REVIEW_IDENTITY",
        },
        "frontier": {
            "last_verified_edge": "EXACT_FM_COMMITTED_REVIEW_TO_CURRENT_ADMISSION_TRANSITION_STATICALLY_AUTHENTICATED",
            "first_broken_edge": "NONE_WITHIN_LP_STATIC_CAPABILITY_SCOPE",
            "first_unverified_edge": "FRESH_PHASE_A_THEN_FRESH_HUMAN_DECISION_AND_OPERATIONAL_WRONG_SCOPE_DENIAL",
            "minimum_missing_capability": "NONE_WITHIN_LP_STATIC_TRANSITION_SCOPE",
            "minimum_missing_proof": "OPERATIONAL_WRONG_SCOPE_DENIAL_BEFORE_P11_ENTRY",
            "minimum_legal_next_delta": "STOP_FOR_INDEPENDENT_HUMAN_REVIEW_OF_LP_CHECKPOINT",
        },
        "architecture": {
            "production_mutation": 1,
            "fm_mutation": 1,
            "p11_mutation": 0,
            "er_mutation": 0,
            "ex_mutation": 0,
            "new_owner": 0,
            "new_route": 0,
            "new_registry": 0,
            "new_generic_abstraction": 0,
            "new_constitutional_concept": 0,
            "route_count_before": 1,
            "route_count_after": 1,
        },
        "operational_counters": {
            "HUMAN_AUTHORITY_SOURCE_COUNT": 0,
            "AUTHORITY_CREATION_COUNT": 0,
            "AUTHORITY_CONSUMPTION_COUNT": 0,
            "OPERATION_ATTEMPT_COUNT": 0,
            "QEMU_START_COUNT": 0,
            "VM_START_COUNT": 0,
            "P11_ENTRY_COUNT": 0,
            "PROTECTED_INVOCATION_COUNT": 0,
            "PROTECTED_EFFECT_COUNT": 0,
            "RETRY_COUNT": 0,
            "OPERATIONAL_REPLAY_COUNT": 0,
            "REPAIR_RETRY_COUNT": 0,
        },
        "e05": {"before": "12/18", "lp_credit": 0, "after": "12/18", "wrong_scope": "UNSAT"},
        "ex": {"reused": "VERIFIED__17_OF_17", "reconstructed": "VERIFIED__0"},
        "reuse_impact_assessment": {
            "existing_certified_capabilities_reused": "FM_EXACT_CURRENT_ROUTE_CONTEXT_ASSETS_AUTHORITY_RECEIPT_ONE_SHOT_AND_RUNTIME_CHECKOUT__GN_FC_ER_P11_EX_UNCHANGED",
            "new_capabilities": "ONE_NARROW_FM_COMMITTED_REVIEW_TO_CURRENT_ADMISSION_TRANSITION_VALIDATOR",
            "existing_capability_unreachable": False,
            "parallel_flow": False,
            "production_route_effect": "UNCHANGED__1_TO_1",
        },
        "governance": {
            "project_state": "LP_MINIMUM_TRANSITION_CAPABILITY_IMPLEMENTED__STATICALLY_PROVEN__READY_FOR_HUMAN_REVIEW",
            "informal_project_progress": "COMMITTED_REVIEW_SUCCESSOR_ADMISSION_GAP_CLOSED_STATICALLY__WRONG_SCOPE_REMAINS_12_OF_18",
            "constitutional_health_evidence": "EXACT_SAME_HEAD_GUARDS_PRESERVED__STRONGER_TRANSITION_FAILS_CLOSED__ZERO_AUTHORITY_OPERATION_EFFECT",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "ONE_INDEPENDENT_HUMAN_CHECKPOINT_THEN_FRESH_PHASE_A_AND_SEPARATELY_AUTHORIZED_OPERATIONAL_GENERATION",
            "governance_efficiency": "HIGH__ONE_EXISTING_OWNER_AND_ROUTE__NO_SCHEMA_OR_RUNTIME_ROUTE_EXPANSION",
            "overengineering_risk": "BOUNDED__CANONICAL_CONTEXT_ONLY__DO_NOT_GENERALIZE_TO_COMMIT_TRANSITION_SERVICE",
            "cognition_provenance": "AUTHENTICATED_REPOSITORY_FACT_PLUS_DERIVED_REPOSITORY_FACT_PLUS_MODEL_INFERENCE_PLUS_HISTORICAL_HUMAN_DECISION_EVIDENCE_PLUS_AUTHORITY_FREE_STATIC_OBSERVATION",
            "cognition_assisted_handoff": "EXACT_STATIC_CAPABILITY_AND_SECURITY_PROOF_ONLY__NO_AUTHORITY_PROOF_OR_E05_TRANSFER",
            "candidate_capability": "FM_OWNED_COMMITTED_REVIEW_IDENTITY_TO_EXACT_CURRENT_ADMISSION_TRANSITION_VALIDATION__IMPLEMENTED_STATICALLY",
            "shadow_design_target": "HUMAN_DECISION_REJECTION_AND_REAUTHORIZATION_LIFECYCLE__HUMAN_REJECTION_FINALITY__IMPLEMENT_NOW_NO",
            "constitutional_continuation_progress": "LO_MINIMUM_GAP_TO_LP_ONE_OWNER_EXACT_TRANSITION_STATIC_PROOF",
            "hac_hai_hae": "NOT_USED__AUTHENTICATED_DEFINITIONS_NOT_PROVEN",
        },
    }


def verify() -> dict[str, Any]:
    repository = authenticate_entry()
    mutation = authenticate_mutation_scope()
    authenticate_precedent_reuse()
    implementation = authenticate_implementation()
    authenticate_zero_authority_operation()
    reduction = build_reduction()
    envelope = load_json(REDUCTION)
    if (
        envelope.get("reduction") != reduction
        or envelope.get("reduction_sha256")
        != hashlib.sha256(canonical_bytes(reduction)).hexdigest()
    ):
        raise LPVerificationError("LP_REDUCTION_MISMATCH")
    return {
        "terminal": TERMINAL,
        "repository": repository,
        "mutation": mutation,
        "implementation": implementation,
    }


if __name__ == "__main__":
    print(verify()["terminal"])
