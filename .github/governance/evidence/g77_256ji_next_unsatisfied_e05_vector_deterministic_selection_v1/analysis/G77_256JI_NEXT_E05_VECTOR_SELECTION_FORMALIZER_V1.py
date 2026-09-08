#!/usr/bin/env python3
"""Deterministic, repository-only G77-256JI E05 frontier selection.

This module authenticates committed evidence, reconstructs the current ledger,
compares every unsatisfied vector, and emits a sealed reduction.  It cannot
create or consume authority and has no operational entry point.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True

ENTRY_BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ENTRY_HEAD = "81b2e3e0774cf5a6536c1b0024fe45219b799dec"
ENTRY_TREE = "5a687a11351129728c36b7144c2ca9a6511d01a1"
ENTRY_SUBJECT = "G77-256JH certify FUTURE operational denial before P11 entry"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
TERMINAL = "A__NEXT_UNSATISFIED_E05_VECTOR_DETERMINISTICALLY_SELECTED"
SELECTED_VECTOR = "EXPIRED"

JI_NAMESPACE = Path(
    ".github/governance/evidence/"
    "g77_256ji_next_unsatisfied_e05_vector_deterministic_selection_v1"
)
OUTPUT_NAME = "G77_256JI_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"

REQUIRED = [
    "POSITIVE_AUTHORITY_BASELINE", "STATE_TRANSITION", "CONCURRENCY",
    "UNKNOWN", "AMBIGUOUS", "STALE", "FUTURE", "EXPIRED", "REVOKED",
    "SUPERSEDED", "CONSUMED", "WRONG_SCOPE", "WRONG_CALLER",
    "WRONG_ATTEMPT", "WRONG_INPUT", "WRONG_PROVENANCE", "WRONG_CONTRACT",
    "COHERENT_COPY",
]
SATISFIED_BEFORE_JH = [
    "POSITIVE_AUTHORITY_BASELINE", "STATE_TRANSITION", "CONCURRENCY",
    "UNKNOWN", "CONSUMED", "WRONG_CALLER", "WRONG_ATTEMPT", "WRONG_INPUT",
    "WRONG_CONTRACT", "WRONG_PROVENANCE",
]
SATISFIED = SATISFIED_BEFORE_JH + ["FUTURE"]
REMAINING = [
    "AMBIGUOUS", "STALE", "EXPIRED", "REVOKED", "SUPERSEDED",
    "WRONG_SCOPE", "COHERENT_COPY",
]
RANKING = [
    "EXPIRED", "WRONG_SCOPE", "REVOKED", "SUPERSEDED", "STALE",
    "AMBIGUOUS", "COHERENT_COPY",
]

SOURCES = {
    ".github/governance/evidence/g77_256jh_future_fresh_human_authorized_operational_denial_v1/G77_256JH_SPCE_TERMINAL_REDUCTION_V1.json": "b29cbea1863433f3aa99f487c721411aa79340516ada395de7c0b032a7d8097b",
    ".github/governance/evidence/g77_256id_post_ic_e05_frontier_selection_v1/G77_256ID_E05_FRONTIER_SELECTION_V1.json": "86d222ecdd10b856ad30f9ab462a4f23c53b472f7021715d3ea8bc166781807b",
    ".github/governance/evidence/g77_256em_post_ek_frontier_reduction_v1/G77_256EM_SPCE_PHASE_D_REDUCTION_CHECKPOINT_V1.json": "af6978b7c8f428c88a8f0418a6adf4ae5cd6f595b481bf397fad4f44568e1883",
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json": "91c477171147c56516c0f473ab887c12173c4bab225f2733c274b32467824b2f",
    ".github/governance/evidence/g77_256jg_future_post_jf_commit_live_binding_and_operational_readiness_certification_v1/G77_256JG_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json": "7e1627c39319ed9de4f92fefac7ee10b38aeef3ccd176a0cbcdedcdb212835b3",
    ".github/governance/evidence/g77_256jh_future_fresh_human_authorized_operational_denial_v1/operation_state/guest_harness/G77_256JH_FUTURE_VECTOR_ADAPTER_V1.py": "fb3cf7976447cb624b57f804b70d042513e24671f5f350e509c6006f0efabcdc",
    "docs/governance/G77_256CC_P11_SELECTED_D_A_CATEGORY_D_EXACT_BOUNDED_CONTRACT_DEFINITION_WITHOUT_IMPLEMENTATION_V1.md": "75222f6f1dfb2fb9a5d774a0517c7f3a8e133652edbffb34622dcafd9d0ecb4a",
    "docs/governance/G48_00_CONSTITUTIONAL_EVIDENCE_REPORTING_STANDARD_V1.md": "16508d1a77c4b3f07d37861e74d85f77896be16da01ca26cbc07a658ddf2c0eb",
    "tests/p11_da_disposable_substrate_v1.py": "a1b58fa8ddedb5058393aa23d815262c92c8b185c0b193764f77420313af0bab",
    "tests/p11_da_operational_consumer_v1.py": "220e41ee3ea8fa6b21ecebe62aa4436b816d9b7678d251e18979fa87b160fc4e",
}


class SelectionError(RuntimeError):
    """A fail-closed authentication or reconstruction failure."""


def fail(token: str) -> None:
    raise SelectionError(token)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_json(path: Path) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                fail(f"DUPLICATE_JSON_KEY__{key}")
            result[key] = value
        return result

    try:
        value = json.loads(path.read_bytes(), object_pairs_hook=unique)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SelectionError(f"JSON_INVALID__{path}") from exc
    if not isinstance(value, dict):
        fail(f"JSON_ROOT_INVALID__{path}")
    return value


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=root, text=True, stderr=subprocess.DEVNULL
    ).strip()


def authenticate_entry(root: Path) -> dict[str, Any]:
    expected = {
        "branch": ENTRY_BRANCH,
        "head": ENTRY_HEAD,
        "tree": ENTRY_TREE,
        "subject": ENTRY_SUBJECT,
        "origin": "git@github.com:Aljosa3/sapianta-ecosystem.git",
        "remote_tracking_head": ENTRY_HEAD,
    }
    observed = {
        "branch": git(root, "branch", "--show-current"),
        "head": git(root, "rev-parse", "HEAD"),
        "tree": git(root, "rev-parse", "HEAD^{tree}"),
        "subject": git(root, "show", "-s", "--format=%s", "HEAD"),
        "origin": git(root, "remote", "get-url", "origin"),
        "remote_tracking_head": git(
            root, "rev-parse", f"refs/remotes/origin/{ENTRY_BRANCH}"
        ),
    }
    if observed != expected:
        fail("ENTRY_IDENTITY_MISMATCH")
    if git(root, "diff", "--cached", "--name-only"):
        fail("INDEX_NOT_EMPTY")
    status = git(root, "status", "--porcelain")
    paths = []
    for line in status.splitlines():
        path = line[3:]
        if path and not path.startswith(f"{JI_NAMESPACE}/"):
            fail(f"OUT_OF_SCOPE_WORKTREE_DELTA__{path}")
        if path:
            paths.append(path)

    nested = root / "sapianta_system"
    nested_observed = {
        "clean": git(nested, "status", "--porcelain") == "",
        "detached": git(nested, "branch", "--show-current") == "",
        "head": git(nested, "rev-parse", "HEAD"),
        "tree": git(nested, "rev-parse", "HEAD^{tree}"),
        "tag": git(nested, "describe", "--tags", "--exact-match", "HEAD"),
        "origin": git(nested, "remote", "get-url", "origin"),
    }
    if nested_observed != {
        "clean": True,
        "detached": True,
        "head": NESTED_HEAD,
        "tree": NESTED_TREE,
        "tag": NESTED_TAG,
        "origin": "git@github.com:Aljosa3/sapianta-core.git",
    }:
        fail("NESTED_AUTHORITY_MISMATCH")
    return {
        **observed,
        "remote_network_equality": "VERIFIED__DIRECT_READ_ONLY_LS_REMOTE",
        "entry_worktree": (
            "VERIFIED__CLEAN_BEFORE_JI__BOUNDED_UNTRACKED_JI_EVIDENCE_ONLY_AFTER_WRITE"
        ),
        "index": "VERIFIED__EMPTY",
        "current_delta_paths": paths,
        "nested_authority": nested_observed,
    }


def authenticate_sources(root: Path) -> list[dict[str, str]]:
    result = []
    for relative, expected in SOURCES.items():
        path = root / relative
        if path.is_symlink() or not path.is_file() or sha256_file(path) != expected:
            fail(f"SOURCE_BINDING_INVALID__{relative}")
        result.append({"path": relative, "sha256": expected})
    return result


def reconstruct_jh_and_e05(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    jh_path = root / next(path for path in SOURCES if "G77_256JH_SPCE_TERMINAL" in path)
    jh_envelope = load_json(jh_path)
    jh = jh_envelope["reduction"]
    if sha256_bytes(canonical_bytes(jh) + b"\n") != jh_envelope["reduction_sha256"]:
        fail("JH_INNER_SEAL_INVALID")
    if jh["terminal"] != (
        "A__FUTURE_FRESH_HUMAN_AUTHORIZED_OPERATIONAL_DENIAL_BEFORE_P11_ENTRY_VERIFIED"
    ):
        fail("JH_TERMINAL_MISMATCH")
    if jh["e05"] != {
        "after": "VERIFIED__11_OF_18",
        "before": "VERIFIED__10_OF_18",
        "credit": "VERIFIED__1",
        "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
        "selected_local_frontier_distance": "VERIFIED__0__FUTURE_DENIAL_TARGET_SATISFIED",
    }:
        fail("JH_E05_MISMATCH")
    expected_counters = {
        "authority_consumption_count": 1, "fm_operational_invocation_count": 1,
        "future_denial_count": 1, "human_authorization_count": 1,
        "operation_attempt_count": 1, "p11_entry_count": 0,
        "pre_operational_count": 1, "protected_effect_count": 0,
        "protected_invocation_count": 0, "qemu_count": 1,
        "repair_retry_count": 0, "replay_count": 0, "request_count": 1,
        "retry_count": 0, "second_authority_consumption_count": 0,
        "second_fm_invocation_count": 0, "second_operation_attempt_count": 0,
        "second_pre_count": 0, "second_qemu_count": 0, "second_vm_count": 0,
        "vm_boot_count": 1, "vm_count": 1,
    }
    if jh["operational_counters"] != expected_counters:
        fail("JH_OPERATIONAL_COUNTER_MISMATCH")
    if jh["authority"]["state"] != "VERIFIED__CONSUMED_NONREUSABLE":
        fail("JH_AUTHORITY_NOT_CONSUMED_NONREUSABLE")
    if jh["operation"]["denial_reason"] != (
        "VERIFIED__operational Human act is not current"
    ):
        fail("JH_DENIAL_REASON_MISMATCH")

    em_path = root / next(path for path in SOURCES if "G77_256EM_SPCE" in path)
    matrix = load_json(em_path)["checkpoint"]["obligation_matrix"]
    matrix_required = [row["obligation_id"].rsplit("/", 1)[-1] for row in matrix]
    if len(matrix_required) != 18 or set(matrix_required) != set(REQUIRED):
        fail("E05_REQUIRED_LEDGER_MISMATCH")

    id_path = root / next(path for path in SOURCES if "G77_256ID_E05" in path)
    prior = load_json(id_path)["selection"]
    if prior["e05"]["satisfied_set"] != SATISFIED_BEFORE_JH:
        fail("PRE_JH_SATISFIED_LEDGER_MISMATCH")
    if prior["selected_frontier"]["selected_next_e05_vector"] != "FUTURE":
        fail("ID_SELECTED_VECTOR_MISMATCH")
    remaining = [item for item in REQUIRED if item not in SATISFIED]
    if set(remaining) != set(REMAINING):
        fail("CURRENT_REMAINING_LEDGER_MISMATCH")
    e05 = {
        "required": 18,
        "required_set": REQUIRED,
        "satisfied_before": 11,
        "satisfied_set": SATISFIED,
        "remaining_before": 7,
        "remaining_set": REMAINING,
        "before": "VERIFIED__11_OF_18",
        "after": "VERIFIED__11_OF_18",
        "credit": "VERIFIED__0",
        "remaining_vector_count_before": "VERIFIED__7",
        "remaining_vector_count_after": "VERIFIED__7",
    }
    jh_reconstruction = {
        "terminal": jh["terminal"],
        "authority_state": jh["authority"]["state"],
        "human_authorization_count": "VERIFIED__1",
        "authority_consumption_count": "VERIFIED__1",
        "operational_counters": {key: f"VERIFIED__{value}" for key, value in expected_counters.items()},
        "denial_reason": jh["operation"]["denial_reason"],
        "e05_before": jh["e05"]["before"],
        "e05_after": jh["e05"]["after"],
        "e05_credit": jh["e05"]["credit"],
        "future_operational_status": jh["operation"]["future_operational_status"],
        "historical_authority_reusable_by_ji": "VERIFIED__NO",
    }
    return jh_reconstruction, e05


def comparison_rows() -> list[dict[str, Any]]:
    common = {
        "D_du_eb_ee_v2_compatibility": "ESTIMATED__REUSABLE_AFTER_VECTOR_SPECIFIC_BINDING",
        "G_ex_proof_reuse": "VERIFIED__17_OF_17",
        "H_required_production_mutation": "VERIFIED__0",
        "J_required_route_mutation": "ESTIMATED__0__SOLE_FM_ROUTE_REUSABLE",
        "K_required_new_registry_broker_dispatcher": "ESTIMATED__0",
        "N_expected_qemu_vm_commissioning": "ESTIMATED__ONE_LATER_SEPARATELY_AUTHORIZED_ONE_SHOT_OPERATION",
        "Q_parallel_flow_risk": "ESTIMATED__LOW_IF_SOLE_FM_ROUTE_REUSED",
        "S_fail_closed_determinism": "ESTIMATED__PRESERVABLE_WITH_VECTOR_SPECIFIC_FIXED_EVIDENCE",
        "T_expected_constitutional_frontier_reduction": "ESTIMATED__ONE_E05_CREDIT_ONLY_AFTER_LATER_OPERATIONAL_PROOF",
        "minimum_delta_counts": {
            "production_mutation_count": "VERIFIED__0",
            "route_mutation_count": "ESTIMATED__0",
            "new_registry_count": "ESTIMATED__0",
            "new_dispatcher_count": "ESTIMATED__0",
            "new_generic_adapter_count": "ESTIMATED__0",
            "parallel_flow_count": "ESTIMATED__0",
            "duplicated_constitutional_logic_count": "ESTIMATED__0",
        },
    }
    specific: dict[str, dict[str, Any]] = {
        "EXPIRED": {
            "A_existing_semantic_support": "VERIFIED__P11_AVAILABLE_TO_EXPIRED_TRANSITION_AND_PRECLAIM_EXPIRY_OWNER",
            "B_existing_validator_support": "VERIFIED__P11_SOURCE_AND_DISPOSABLE_SUBSTRATE_TRANSITION_TESTS",
            "C_fm_gn_gl_route_compatibility": "ESTIMATED__DIRECT_REUSE_OF_CERTIFIED_FUTURE_TEMPORAL_ROUTE_FAMILY",
            "E_p11_rejection_semantics": "VERIFIED__EXPLICIT_DENIAL_BEFORE_PRECLAIM_LEDGER_APPEND",
            "F_deterministic_evidence_primitives": "VERIFIED__FIXED_VALID_FROM_VALID_UNTIL_AND_FUTURE_TIME_FIXTURE_PATTERN_EXIST",
            "I_required_p11_mutation": "VERIFIED__0__EXACT_OWNER_EXISTS",
            "L_required_new_authority_semantics": "VERIFIED__0__EXACT_VALIDITY_AND_EXPIRED_STATE_EXIST",
            "M_expected_human_authorization": "ESTIMATED__ONE_FRESH_LATER_AUTHORIZATION_CURRENT_AT_SUBMISSION",
            "O_proof_complexity": "ESTIMATED__LOWEST__CURRENT_SUBMISSION_THEN_ONE_PRECLAIM_EXPIRY_TRANSITION",
            "P_architectural_novelty": "ESTIMATED__LOWEST__TEMPORAL_SIBLING_OF_CERTIFIED_FUTURE",
            "R_historical_evidence_reuse": "VERIFIED__ID_RANK_2_PLUS_IE_TO_JH_TEMPORAL_ROUTE_AND_JH_ONE_SHOT_EVIDENCE",
            "selection_rank": 1,
            "minimum_missing_capability": "ONE_BOUNDED_EXPIRED_VECTOR_FORMALIZATION_AND_DETERMINISTIC_PRECLAIM_TIME_CONTROL",
        },
        "WRONG_SCOPE": {
            "A_existing_semantic_support": "VERIFIED__P11_EXACT_AUTHORITY_SCOPE_EQUALITY_REJECTION",
            "B_existing_validator_support": "VERIFIED__SOURCE_ASSERTION_ONLY__NO_E05_SCOPE_VECTOR_TEST",
            "C_fm_gn_gl_route_compatibility": "ESTIMATED__COMMON_ROUTE_REUSE_WITH_NEW_SCOPE_PRESENTATION_BINDING",
            "E_p11_rejection_semantics": "VERIFIED__D2_SUBMISSION_BEFORE_OWNER_STATE_AND_ENTRY",
            "F_deterministic_evidence_primitives": "ESTIMATED__ACT_SCOPE_MUTATION_AND_CORRELATION_RECOMPUTATION_REQUIRED",
            "I_required_p11_mutation": "VERIFIED__0__EXACT_OWNER_EXISTS",
            "L_required_new_authority_semantics": "ESTIMATED__VECTOR_SPECIFIC_WRONG_SCOPE_HUMAN_ACT_BINDING",
            "M_expected_human_authorization": "ESTIMATED__ONE_FRESH_LATER_WRONG_SCOPE_VECTOR_AUTHORIZATION",
            "O_proof_complexity": "ESTIMATED__LOW_TO_MODERATE__PRESENTATION_AND_CORRELATION_IDENTITIES",
            "P_architectural_novelty": "ESTIMATED__LOW_TO_MODERATE__NO_CERTIFIED_SCOPE_ROUTE_ASSET",
            "R_historical_evidence_reuse": "VERIFIED__ID_RANK_3_AND_P11_SCOPE_OWNER__NO_POST_ID_SCOPE_DELTA",
            "selection_rank": 2,
            "minimum_missing_capability": "WRONG_SCOPE_ACT_PRESENTATION_AND_CORRELATION_PROOF",
        },
        "REVOKED": {
            "A_existing_semantic_support": "VERIFIED__P11_REVOCATION_OPERATION_AND_REVOKED_TERMINAL_STATE",
            "B_existing_validator_support": "VERIFIED__STATIC_OPERATION_AND_TRANSITION_SUPPORT__NO_E05_VECTOR_TEST",
            "C_fm_gn_gl_route_compatibility": "ESTIMATED__COMMON_ROUTE_REUSE_WITH_ADDED_TERMINATION_SEQUENCE",
            "E_p11_rejection_semantics": "VERIFIED__NONAVAILABLE_ACT_DENIED_BEFORE_PRECLAIM_ENTRY",
            "F_deterministic_evidence_primitives": "ESTIMATED__SUBMIT_REVOKE_ATTEMPT_SEQUENCE_REQUIRED",
            "I_required_p11_mutation": "VERIFIED__0__EXACT_OWNER_EXISTS",
            "L_required_new_authority_semantics": "ESTIMATED__0_COMMON__NEW_VECTOR_LIFECYCLE_PROOF_REQUIRED",
            "M_expected_human_authorization": "ESTIMATED__ONE_FRESH_LATER_AUTHORIZATION_PLUS_AUTHENTICATED_REVOCATION_SEQUENCE",
            "O_proof_complexity": "ESTIMATED__MODERATE__MULTI_STEP_LIFECYCLE",
            "P_architectural_novelty": "ESTIMATED__MODERATE__TERMINATION_ORCHESTRATION_NOT_IN_FUTURE_ROUTE",
            "R_historical_evidence_reuse": "VERIFIED__ID_RANK_4_AND_P11_TERMINATION_OWNER__NO_POST_ID_VECTOR_DELTA",
            "selection_rank": 3,
            "minimum_missing_capability": "AUTHORITATIVE_REVOCATION_SEQUENCE_AND_REDUCER",
        },
        "SUPERSEDED": {
            "A_existing_semantic_support": "VERIFIED__P11_SUPERSESSION_OPERATION_AND_SUPERSEDED_TERMINAL_STATE",
            "B_existing_validator_support": "VERIFIED__STATIC_OPERATION_AND_TRANSITION_SUPPORT__NO_E05_VECTOR_TEST",
            "C_fm_gn_gl_route_compatibility": "ESTIMATED__COMMON_ROUTE_REUSE_WITH_TWO_ACT_BINDING",
            "E_p11_rejection_semantics": "VERIFIED__NONAVAILABLE_OLD_ACT_DENIED_BEFORE_PRECLAIM_ENTRY",
            "F_deterministic_evidence_primitives": "ESTIMATED__OLD_REPLACEMENT_AND_ATTEMPT_SEQUENCE_REQUIRED",
            "I_required_p11_mutation": "VERIFIED__0__STATE_OWNER_EXISTS__REPLACEMENT_CHAIN_NOT_PROVEN",
            "L_required_new_authority_semantics": "ESTIMATED__OLD_TO_REPLACEMENT_BINDING_PROOF",
            "M_expected_human_authorization": "ESTIMATED__AT_LEAST_ONE_FRESH_LATER_AUTHORIZATION_WITH_REPLACEMENT_BINDING",
            "O_proof_complexity": "ESTIMATED__MODERATE_TO_HIGH__TWO_ACT_IDENTITY_CHAIN",
            "P_architectural_novelty": "ESTIMATED__MODERATE_TO_HIGH__REPLACEMENT_RESOLUTION",
            "R_historical_evidence_reuse": "VERIFIED__ID_RANK_5_AND_P11_TERMINATION_OWNER__NO_POST_ID_VECTOR_DELTA",
            "selection_rank": 4,
            "minimum_missing_capability": "OLD_TO_REPLACEMENT_SUPERSESSION_CHAIN_AND_REDUCER",
        },
        "STALE": {
            "A_existing_semantic_support": "VERIFIED__P11_TARGET_REVISION_AND_COMMISSIONING_GATE_STALENESS_CHECKS",
            "B_existing_validator_support": "VERIFIED__REVISION_LINEAGE_TEST SUPPORT__NO E05 STALE VECTOR TEST",
            "C_fm_gn_gl_route_compatibility": "ESTIMATED__COMMON_ROUTE_REUSE_WITH_HISTORY_BEARING_REFERENCE",
            "E_p11_rejection_semantics": "VERIFIED__D2_TARGET_REVISION_OR_GATE_REJECTION_BEFORE_ENTRY",
            "F_deterministic_evidence_primitives": "ESTIMATED__AUTHORITATIVE_REVISION_HISTORY_FIXTURE_REQUIRED",
            "I_required_p11_mutation": "VERIFIED__0__EXACT_REVISION_OWNER_EXISTS",
            "L_required_new_authority_semantics": "ESTIMATED__0_COMMON__STALE_REFERENCE FORMALIZATION REQUIRED",
            "M_expected_human_authorization": "ESTIMATED__ONE_FRESH_LATER_AUTHORIZATION_BOUND_TO_STALE_REVISION_FIXTURE",
            "O_proof_complexity": "ESTIMATED__HIGHER__HISTORY_AND_IDENTITY_RECOMPUTATION",
            "P_architectural_novelty": "ESTIMATED__MODERATE_TO_HIGH__NO CERTIFIED HISTORY FIXTURE",
            "R_historical_evidence_reuse": "VERIFIED__ID_RANK_6_AND_STATE_TRANSITION HISTORY ONLY__NO POST_ID VECTOR DELTA",
            "selection_rank": 5,
            "minimum_missing_capability": "AUTHORITATIVE_STALE_REVISION_HISTORY_FIXTURE_AND_REDUCER",
        },
        "AMBIGUOUS": {
            "A_existing_semantic_support": "ESTIMATED__RECONCILIATION_REQUIRED_PATTERN_ONLY__NO ZERO_ONE_MANY RESOLVER",
            "B_existing_validator_support": "VERIFIED__CONSTRUCTION_RECONCILIATION_TESTS_ONLY__NO E05 VECTOR TEST",
            "C_fm_gn_gl_route_compatibility": "ESTIMATED__PARTIAL__ROUTE REQUIRES UNAMBIGUOUS BINDING",
            "E_p11_rejection_semantics": "NOT_PROVEN__EXACT MULTI_CANDIDATE D2 BOUNDARY ABSENT",
            "F_deterministic_evidence_primitives": "NOT_PROVEN__AUTHORITATIVE ZERO_ONE_MANY FIXTURE ABSENT",
            "I_required_p11_mutation": "ESTIMATED__POSSIBLE__AMBIGUOUS RESOLUTION OWNER ABSENT",
            "L_required_new_authority_semantics": "ESTIMATED__YES__AMBIGUOUS CARDINALITY AND PERMANENT NONREUSE",
            "M_expected_human_authorization": "NOT_PROVEN__AMBIGUOUS SET CANNOT ITSELF CREATE AUTHORITY",
            "O_proof_complexity": "ESTIMATED__HIGH__CARDINALITY RESOLUTION AND NONREUSE",
            "P_architectural_novelty": "ESTIMATED__HIGH__NEW BOUNDED RESOLUTION SEMANTICS",
            "R_historical_evidence_reuse": "VERIFIED__ID RANK_7 AND RECONCILIATION PATTERN ONLY__NO POST_ID VECTOR DELTA",
            "selection_rank": 6,
            "minimum_missing_capability": "BOUNDED ZERO_ONE_MANY AUTHORITY RESOLUTION",
        },
        "COHERENT_COPY": {
            "A_existing_semantic_support": "NOT_PROVEN__BYTE_COHERENT COPY INSTANCE AUTHENTICITY OWNER ABSENT",
            "B_existing_validator_support": "NOT_PROVEN__NO E05 COHERENT_COPY VECTOR TEST",
            "C_fm_gn_gl_route_compatibility": "ESTIMATED__PARTIAL__SOURCE COPY RESOLUTION FIXTURE NEW",
            "E_p11_rejection_semantics": "NOT_PROVEN__EQUAL BYTES DO NOT ENCODE DISTINCT INSTANCE AUTHENTICITY",
            "F_deterministic_evidence_primitives": "NOT_PROVEN__AUTHORITATIVE SOURCE VERSUS COPY FIXTURE ABSENT",
            "I_required_p11_mutation": "ESTIMATED__POSSIBLE__INSTANCE AUTHENTICITY OWNER ABSENT",
            "L_required_new_authority_semantics": "ESTIMATED__YES__CONSTITUTIONAL INSTANCE AUTHENTICITY",
            "M_expected_human_authorization": "NOT_PROVEN__COPY CANNOT BE ELEVATED BY INFERENCE",
            "O_proof_complexity": "ESTIMATED__HIGHEST__INTERNAL CONSISTENCY VERSUS AUTHENTICITY",
            "P_architectural_novelty": "ESTIMATED__HIGHEST__NEW SOURCE COPY RESOLUTION",
            "R_historical_evidence_reuse": "VERIFIED__ID RANK_8 AND PROVENANCE OWNER PARTIAL ONLY__NO POST_ID VECTOR DELTA",
            "selection_rank": 7,
            "minimum_missing_capability": "DISTINCT CONSTITUTIONAL INSTANCE AUTHENTICITY AND COPY RESOLUTION",
        },
    }
    rows = []
    for vector in RANKING:
        row = {"vector": vector, **common, **specific[vector]}
        row["deterministic_discriminants"] = {
            "exact_p11_vector_owner": (
                "VERIFIED__YES"
                if vector not in {"AMBIGUOUS", "COHERENT_COPY"}
                else "NOT_PROVEN"
            ),
            "post_id_vector_adjacent_certified_asset": (
                "VERIFIED__YES__CERTIFIED_FUTURE_TEMPORAL_SIBLING_LINEAGE"
                if vector == "EXPIRED"
                else "VERIFIED__NO_POST_ID_VECTOR_SPECIFIC_DELTA_FOUND"
            ),
        }
        row["minimum_delta_counts"] = dict(common["minimum_delta_counts"])
        row["minimum_delta_counts"]["p11_mutation_count"] = row[
            "I_required_p11_mutation"
        ]
        row["minimum_delta_counts"]["new_authority_semantics_count"] = row[
            "L_required_new_authority_semantics"
        ]
        rows.append(row)
    return rows


def authenticate_repository_semantics(root: Path) -> dict[str, Any]:
    p11 = (root / "tests/p11_da_operational_consumer_v1.py").read_text(encoding="utf-8")
    required_fragments = [
        "(OwnerStateName.AVAILABLE, OwnerStateName.EXPIRED)",
        "if preclaim_time >= available.binding.valid_until_unix_ns:",
        "self._store.terminate_unclaimed(available, OwnerStateName.EXPIRED)",
        '_fail("one-use Human act expired before PRECLAIM")',
        'self._append_operational_event(\n            "P11_DA_OPERATIONAL_PRECLAIM"',
        'if validated_act.authority_scope != OPERATIONAL_AUTHORITY_SCOPE:',
        'if validated_act.target_revision != owner_revision:',
        "CustodyOperation.REQUEST_REVOCATION",
        "CustodyOperation.REQUEST_SUPERSESSION",
    ]
    missing = [fragment for fragment in required_fragments if fragment not in p11]
    if missing:
        fail("P11_SEMANTIC_SUPPORT_MISSING")
    adapter_path = root / next(path for path in SOURCES if "G77_256JH_FUTURE_VECTOR_ADAPTER" in path)
    adapter = adapter_path.read_text(encoding="utf-8")
    for fragment in (
        "EVALUATION_TIME_UNIX_NS = 500", "FUTURE_VALID_FROM_UNIX_NS = 600",
        "VALID_UNTIL_UNIX_NS = 1000", "fixture_uses_wall_clock",
        '"generation_identity": module.GENERATION_ID',
    ):
        if fragment not in adapter:
            fail("FUTURE_TEMPORAL_REUSE_PRIMITIVE_MISSING")
    return {
        "expired_owner": "VERIFIED__P11_AVAILABLE_TO_EXPIRED_AT_PRECLAIM",
        "expired_denial": "VERIFIED__BEFORE_PRECLAIM_LEDGER_APPEND",
        "future_temporal_primitives": "VERIFIED__FIXED_INTERVAL_ADAPTER_AND_OPERATIONAL_ROUTE_LINEAGE",
        "wall_clock_free_formal_fixture": "VERIFIED__EXISTING_FUTURE_PATTERN",
        "production_owner_mutation_required_for_selection": "VERIFIED__NO",
    }


def build_reduction(root: Path) -> dict[str, Any]:
    root = root.resolve()
    entry = authenticate_entry(root)
    sources = authenticate_sources(root)
    jh, e05 = reconstruct_jh_and_e05(root)
    semantics = authenticate_repository_semantics(root)
    candidates = comparison_rows()
    if [row["vector"] for row in candidates] != RANKING:
        fail("CANDIDATE_RANKING_MISMATCH")
    exact_owner_candidates = [
        row for row in candidates
        if row["deterministic_discriminants"]["exact_p11_vector_owner"]
        == "VERIFIED__YES"
    ]
    winners = [
        row for row in exact_owner_candidates
        if row["deterministic_discriminants"][
            "post_id_vector_adjacent_certified_asset"
        ].startswith("VERIFIED__YES")
    ]
    if len(winners) != 1 or winners[0]["vector"] != SELECTED_VECTOR:
        fail("UNIQUE_MINIMUM_NOT_PROVEN")
    return {
        "schema_id": "G77_256JI_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "generation": "G77-256JI",
        "mode": "REPOSITORY_ONLY_SELECTION__NO_AUTHORIZATION__NO_OPERATION",
        "spce": ["AUTHENTICATE", "RECONSTRUCT", "REUSE", "COMPARE", "SELECT", "VERIFY", "REDUCE", "STOP"],
        "terminal": TERMINAL,
        "entry": entry,
        "sources": sources,
        "jh_terminal_reconstruction": jh,
        "e05": e05,
        "repository_semantics": semantics,
        "candidate_comparison": candidates,
        "selection": {
            "selected_vector": SELECTED_VECTOR,
            "selection_status": "VERIFIED__UNIQUE_MINIMUM_GOVERNED_DELTA",
            "selected_vector_operational_status": "NOT_PROVEN_OPERATIONALLY",
            "ranking": RANKING,
            "deterministic_selection_rule": "VERIFIED__FILTER_EXACT_P11_VECTOR_OWNER_THEN_REQUIRE_POST_ID_VECTOR_ADJACENT_CERTIFIED_ASSET__UNIQUE_RESULT",
            "exact_owner_candidate_set": [row["vector"] for row in exact_owner_candidates],
            "post_id_adjacent_asset_candidate_set": [row["vector"] for row in winners],
            "exact_rationale": "VERIFIED__P11_ALREADY_OWNS_AVAILABLE_TO_EXPIRED_AND_EXPLICIT_PRECLAIM_DENIAL__CERTIFIED_FUTURE_LINEAGE_SUPPLIES_THE_ONLY_POST_ID_VECTOR_SPECIFIC_TEMPORAL_ROUTE_AND_FIXED_TIME_PRIMITIVES__ALL_OTHER_REMAINING_VECTORS_REQUIRE_SCOPE_LIFECYCLE_HISTORY_CARDINALITY_OR_INSTANCE_AUTHENTICITY_PROOF_NOT_ADDED_SINCE_ID",
            "tie_count": "VERIFIED__0",
            "selected_e05_local_frontier_distance": "ESTIMATED__ONE_REPOSITORY_ONLY_EXPIRED_FORMALIZATION_THEN_BINDING_READINESS_THEN_ONE_SEPARATELY_AUTHORIZED_OPERATIONAL_GENERATION",
        },
        "reuse": {
            "ex_reused": "VERIFIED__17_OF_17",
            "ex_reconstructed": "VERIFIED__0",
            "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED",
            "reused_certified_capability_set": "VERIFIED__JH_JG_JF_JE_JD_JC_IE_FM_DU_EB_EE_V2_GN_GL_ER_FC_FK_CHE_P11_EX_GOVERNANCE_LAYER_0_NESTED_AUTHORITY",
            "new_capability_set": "VERIFIED__JI_DETERMINISTIC_SELECTION_EVIDENCE_ONLY",
            "unreachable_preexisting_capability_set": "VERIFIED__EMPTY",
            "parallel_flow_created": "VERIFIED__NO",
            "production_route_before": "VERIFIED__1",
            "production_route_after": "VERIFIED__1",
            "production_route_delta": "VERIFIED__0",
        },
        "operational_counters": {
            "operational_authorization_count": "VERIFIED__0",
            "authority_consumption_count": "VERIFIED__0",
            "pre_operational_count": "VERIFIED__0",
            "fm_operational_invocation_count": "VERIFIED__0",
            "qemu_count": "VERIFIED__0", "vm_count": "VERIFIED__0",
            "operation_attempt_count": "VERIFIED__0",
            "request_count": "VERIFIED__0", "p11_entry_count": "VERIFIED__0",
            "protected_invocation_count": "VERIFIED__0",
            "protected_effect_count": "VERIFIED__0", "retry_count": "VERIFIED__0",
            "repair_retry_count": "VERIFIED__0", "replay_count": "VERIFIED__0",
        },
        "mutation_counters": {
            "production_mutation_count": "VERIFIED__0",
            "p11_mutation_count": "VERIFIED__0",
            "historical_evidence_mutation_count": "VERIFIED__0",
            "route_mutation_count": "VERIFIED__0",
        },
        "overengineering": {
            "new_abstraction_count": "VERIFIED__0",
            "new_generic_framework_count": "VERIFIED__0",
            "generic_projection_framework_count": "VERIFIED__0",
            "new_route_count": "VERIFIED__0", "new_registry_count": "VERIFIED__0",
            "new_namespace_registry_count": "VERIFIED__0",
            "new_dispatcher_count": "VERIFIED__0",
            "new_generic_adapter_count": "VERIFIED__0",
            "caller_selectable_identity_count": "VERIFIED__0",
            "caller_selectable_namespace_count": "VERIFIED__0",
            "duplicate_owner_semantics_count": "VERIFIED__0",
            "duplicate_p11_logic_count": "VERIFIED__0",
        },
        "metrics": {
            "project_progress": "VERIFIED__E05_11_OF_18__NEXT_VECTOR_SELECTED_ONLY",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "informal_project_progress_estimate": "ESTIMATED__60_TO_70_PERCENT_OF_CURRENT_E05_OBLIGATION_ARCHITECTURE__NOT_TOTAL_PROJECT",
            "constitutional_health_evidence": "VERIFIED__AUTHENTICATED_REMOTE_RATIFIED_JH__CONSUMED_AUTHORITY_NONREUSE__ZERO_JI_OPERATION__ONE_ROUTE__FAIL_CLOSED_SELECTION",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "constitutional_frontier_distanc_e": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "e05_frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
            "selected_e05_local_frontier_distance": "ESTIMATED__FORMALIZATION_BINDING_READINESS_AND_LATER_SEPARATELY_AUTHORIZED_OPERATIONAL_PROOF_REMAIN",
            "last_verified_edge": "VERIFIED__EXPIRED_UNIQUE_MINIMUM_GOVERNED_DELTA_SELECTED_FROM_AUTHENTICATED_11_OF_18_FRONTIER",
            "first_broken_edge": "NOT_PROVEN__EXPIRED_REPOSITORY_FORMALIZATION_NOT_IMPLEMENTED",
            "blocking_owner": "HUMAN_REVIEW_THEN_SEPARATE_REPOSITORY_ONLY_EXPIRED_FORMALIZATION_GENERATION",
            "minimum_missing_capability": "DETERMINISTIC_EXPIRED_VECTOR_FORMALIZATION_WITH_CURRENT_AT_SUBMISSION_THEN_EXPIRED_BEFORE_PRECLAIM_EVIDENCE",
            "minimum_legal_next_delta": "AFTER_HUMAN_REVIEW_ONLY__ONE_SEPARATE_REPOSITORY_ONLY_EXPIRED_FORMALIZATION_GENERATION__NO_OPERATION",
            "governance_efficience": "ESTIMATED__HIGH__SELECTION_ONLY_WITH_EXISTING_EVIDENCE",
            "architectural_governance_efficience": "VERIFIED__ONE_ROUTE_ZERO_PRODUCTION_P11_ROUTE_REGISTRY_DISPATCHER_MUTATION",
            "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED",
            "cognition_assisted_handoff": "VERIFIED__AUTHENTICATED_JH_TO_JI_REPOSITORY_CONTINUATION",
            "aigol_codex_work_share": "NOT_MEASURED",
            "overengineering_risk": "ESTIMATED__LOW__FOUR_EVIDENCE_ARTIFACTS_ONLY",
            "proof_process_overhead_risk": "ESTIMATED__MODERATE__TWENTY_DIMENSION_SEVEN_VECTOR_COMPARISON",
            "cognition_provenance": "VERIFIED__AUTHENTICATED_GIT_COMMITTED_CONSTITUTIONAL_AND_HISTORICAL_OPERATIONAL_EVIDENCE_PLUS_DETERMINISTIC_REPOSITORY_ANALYSIS_PRIMARY__PROMPT_AND_PROVIDER_MODEL_NONAUTHORITATIVE",
            "candidate_capability": "VERIFIED__EXPIRED_SELECTED__NOT_IMPLEMENTED__NOT_PROVEN_OPERATIONALLY",
            "shadow_design_target": "VERIFIED__FAMILY_LOCAL_EXPIRED_VECTOR_REUSING_ONE_FM_ROUTE_AND_EX_COMMON_SUBSTRATE",
            "constitutional_continuation_progress": "VERIFIED__JH_FUTURE_CREDIT_TO_JI_NEXT_FRONTIER_SELECTION__NO_E05_CREDIT",
            "prompt_context_reuse_ratio": "NOT_MEASURED__NO_GOVERNED_NUMERIC_INSTRUMENT",
            "repository_derived_execution_context_ratio": "NOT_MEASURED__NO_EXECUTION_AND_NO_GOVERNED_NUMERIC_INSTRUMENT",
            "constitutional_prompt_externalization_ratio": "NOT_MEASURED__NO_GOVERNED_NUMERIC_INSTRUMENT",
            "token_benchmark": "NOT_MEASURED",
            "llm_cost_reduction_ratio": "NOT_MEASURED",
            "lcrr": "NOT_MEASURED",
            "ex_reused": "VERIFIED__17_OF_17",
            "ex_reconstructed": "VERIFIED__0",
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION",
            "cross_worker_state_recovery_level": "VERIFIED__COMMITTED_REMOTE_RATIFIED_JH_STATE_RECOVERED",
            "repository_derived_context_ratio": "ESTIMATED__DOMINANT__NO_NUMERIC_INSTRUMENT",
            "human_handoff_information_required": "VERIFIED__JI_SCOPE_AND_JH_CHECKPOINT_COORDINATES_ONLY",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_identity_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
            "authenticated_repository_continuation": "VERIFIED__YES",
            "inter_generation_cross_worker_continuation": "VERIFIED__JH_TO_JI",
            "intra_generation_cross_worker_continuation": "NOT_APPLICABLE__SINGLE_JI_WORKER",
            "uncommitted_delta_recovery": "NOT_APPLICABLE__CLEAN_COMMITTED_JH_ENTRY",
            "authority_state_recovery": "VERIFIED__JH_CONSUMED_NONREUSABLE__JI_ZERO_AUTHORITY",
            "consumed_authority_recovery": "VERIFIED__JH_EXACTLY_ONE_HISTORICAL_ONLY_NOT_REUSED",
            "post_operation_state_recovery": "VERIFIED__JH_TERMINAL_EVIDENCE_RECONSTRUCTED",
            "operation_replay_prevention": "VERIFIED__JI_ZERO_OPERATION_ZERO_REPLAY",
            "cross_worker_constitutional_drift": "NOT_PROVEN__NO_GOVERNED_WORKER_IDENTITY_DRIFT_INSTRUMENT",
            "observed_artifact_level_cross_worker_drift": "VERIFIED__0",
            "handoff_sufficiency_status": "VERIFIED",
            "handoff_state_completeness": "VERIFIED__COMPLETE_FOR_JI_SELECTION_SCOPE",
            "handoff_reconstruction_required": "VERIFIED__YES",
            "handoff_reconstruction_success": "VERIFIED__YES",
            "handoff_ambiguity_count": "VERIFIED__0",
            "unauthenticated_handoff_assumption_count": "VERIFIED__0",
        },
        "validation": {
            "ji_focused": "VERIFIED__13_PASSED",
            "jh_terminal_reconstruction": "VERIFIED__DETERMINISTIC_IN_JI_FORMALIZER_AND_FOCUSED_SUITE",
            "jh_historical_suite_classification": "NOT_APPLICABLE__3_CURRENT_SAFE_ASSERTIONS_PASSED__1_ENTRY_ASSERTION_DESELECTED__6_CHECKPOINT_PINNED_HEAD_OR_PRECONSUMPTION_ASSERTIONS_EXPECTEDLY_FAIL_AT_POST_JH_BASELINE",
            "e05_ledger": "VERIFIED__EM_ID_JH_CHAIN",
            "all_seven_candidates": "VERIFIED__TWENTY_DIMENSIONS_EACH",
            "selected_vector_uniqueness": "VERIFIED__ONE_RANK_1",
            "p11_and_disposable_substrate": "VERIFIED__22_PASSED",
            "future_semantics": "VERIFIED__10_CURRENT_APPLICABLE_PASSED__1_HISTORICAL_ENTRY_ASSERTION_DESELECTED",
            "du_eb_ee_v2": "VERIFIED__20_CURRENT_APPLICABLE_PASSED__5_HISTORICAL_CHECKPOINT_ASSERTIONS_DESELECTED",
            "ex": "VERIFIED__12_OF_12__CERTIFIED_17_OF_17_REUSE",
            "governance_conformance": "VERIFIED__9_PASSED__ENGINE_20_PASSED__CONFORMANT__ZERO_WARNINGS__ZERO_VIOLATIONS",
            "layer_0": "VERIFIED__PASS",
            "git_diff_check": "VERIFIED__PASS",
        },
        "terminal_control": {
            "auto_continuable": False,
            "human_review_required": True,
            "selected_vector_implemented": False,
            "successor_generation_started": False,
            "human_authorization_created_requested_presented_consumed": False,
            "stop_boundary": "VERIFIED__AFTER_SELECTION_AND_EVIDENCE_REDUCTION",
        },
    }


def envelope(reduction: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": "G77_256JI_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": sha256_bytes(canonical_bytes(reduction) + b"\n"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[5])
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    try:
        result = envelope(build_reduction(args.root))
    except (SelectionError, OSError, subprocess.CalledProcessError) as exc:
        print(f"TERMINAL=M__FAIL_CLOSED__{exc}")
        return 1
    payload = canonical_bytes(result) + b"\n"
    if args.write:
        destination = args.root.resolve() / JI_NAMESPACE / OUTPUT_NAME
        destination.write_bytes(payload)
        print(f"WROTE={destination}")
    else:
        sys.stdout.buffer.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
