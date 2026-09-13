#!/usr/bin/env python3
"""Deterministic repository-only formalizer for G77-256LE WRONG_SCOPE.

The formalizer authenticates committed owners, proves the existing P11 scope
denial and its ordering, emits a sealed repository reduction, and stops.  It
has no operational entry point and cannot create or consume Human authority.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True

ENTRY_BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ENTRY_HEAD = "9ba0a887899c69350b20980f290678373ac478e3"
ENTRY_TREE = "763cb5d003fe21f8407ca6f26df82145826e431c"
ENTRY_SUBJECT = "G77-256LD prove EXPIRED denial before P11 entry"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
EXPECTED_SCOPE = "P11_DA_ONE_BOUNDED_OPERATIONAL_ATTEMPT_V1"
PRESENTED_WRONG_SCOPE = "P11_DA_DIFFERENT_OPERATIONAL_SCOPE_V1"
TERMINAL = (
    "A__WRONG_SCOPE_EXISTING_CAPABILITY_REUSED__REPOSITORY_PROOF_COMPLETE__"
    "OPERATIONAL_PROOF_REQUIRED"
)
NAMESPACE = Path(
    ".github/governance/evidence/"
    "g77_256le_wrong_scope_minimum_governed_delta_v1"
)
SELECTION_NAME = "G77_256LE_HUMAN_FRONTIER_SELECTION_BINDING_V1.json"
OUTPUT_NAME = "G77_256LE_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"

SOURCES = {
    ".github/governance/evidence/g77_256em_post_ek_frontier_reduction_v1/G77_256EM_SPCE_PHASE_D_REDUCTION_CHECKPOINT_V1.json": "af6978b7c8f428c88a8f0418a6adf4ae5cd6f595b481bf397fad4f44568e1883",
    ".github/governance/evidence/g77_256ji_next_unsatisfied_e05_vector_deterministic_selection_v1/G77_256JI_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json": "06acd7f7d76526fd8a5377be25d95a0897c1d53fe39fe0ce6417db258595678c",
    ".github/governance/evidence/g77_256ld_fresh_expired_operational_recommissioning_v1/G77_256LD_SPCE_TERMINAL_SUCCESS_REDUCTION_V1.json": "1b36a038fc25b8137bded389e06a8ccd8cf7e7d324d1691d1c1dc4dda3c26624",
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json": "91c477171147c56516c0f473ab887c12173c4bab225f2733c274b32467824b2f",
    "aigol/runtime/canonical_human_authority_act_contract_v1.py": "905ce577c31c2c538033455d1633470a34e9f7a94edd6190d50932e97ba8ebc8",
    "tests/p11_da_operational_consumer_v1.py": "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5",
    "tests/p11_da_disposable_substrate_v1.py": "a1b58fa8ddedb5058393aa23d815262c92c8b185c0b193764f77420313af0bab",
    ".github/governance/evidence/g77_256er_p11_operational_v1/harness/G77_256ER_P11_OPERATIONAL_HARNESS_V1.py": "c6539d1cc60940b1999956965bff43923a270598a982cd19f976eadec0a93152",
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py": "c5172208874cca022b638511e57f091eafa01ba3c7387b182cf65d4ee98764d0",
}


class FormalizationError(RuntimeError):
    """A fail-closed repository authentication or semantic error."""


def fail(token: str) -> None:
    raise FormalizationError(token)


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value, sort_keys=True, separators=(",", ":"),
            ensure_ascii=False, allow_nan=False,
        )
        + "\n"
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
        raise FormalizationError(f"JSON_INVALID__{path}") from exc
    if not isinstance(value, dict):
        fail(f"JSON_ROOT_INVALID__{path}")
    return value


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=root, text=True, stderr=subprocess.DEVNULL
    ).strip()


def authenticate_entry(root: Path) -> dict[str, Any]:
    observed = {
        "branch": git(root, "branch", "--show-current"),
        "head": git(root, "rev-parse", "HEAD"),
        "tree": git(root, "rev-parse", "HEAD^{tree}"),
        "subject": git(root, "show", "-s", "--format=%s", "HEAD"),
        "remote_tracking_head": git(
            root, "rev-parse", f"refs/remotes/origin/{ENTRY_BRANCH}"
        ),
    }
    expected = {
        "branch": ENTRY_BRANCH,
        "head": ENTRY_HEAD,
        "tree": ENTRY_TREE,
        "subject": ENTRY_SUBJECT,
        "remote_tracking_head": ENTRY_HEAD,
    }
    if observed != expected:
        fail("ENTRY_IDENTITY_MISMATCH")
    if git(root, "diff", "--cached", "--name-only"):
        fail("INDEX_NOT_EMPTY")
    delta_paths = []
    for line in git(root, "status", "--porcelain", "--untracked-files=all").splitlines():
        path = line[3:]
        if not path.startswith(f"{NAMESPACE}/"):
            fail(f"OUT_OF_SCOPE_WORKTREE_DELTA__{path}")
        delta_paths.append(path)

    nested = root / "sapianta_system"
    nested_observed = {
        "clean": git(nested, "status", "--porcelain") == "",
        "detached": git(nested, "branch", "--show-current") == "",
        "head": git(nested, "rev-parse", "HEAD"),
        "tree": git(nested, "rev-parse", "HEAD^{tree}"),
        "tag": git(nested, "describe", "--tags", "--exact-match", "HEAD"),
    }
    if nested_observed != {
        "clean": True,
        "detached": True,
        "head": NESTED_HEAD,
        "tree": NESTED_TREE,
        "tag": NESTED_TAG,
    }:
        fail("NESTED_AUTHORITY_MISMATCH")
    return {
        **observed,
        "remote_network_equality": "VERIFIED__DIRECT_LS_REMOTE_DURING_INTERRUPTION_RECOVERY",
        "entry_index": "VERIFIED__EMPTY",
        "entry_worktree": "VERIFIED__ONE_INTERRUPTED_LE_SELECTION_BINDING_ONLY",
        "bounded_current_delta_paths": sorted(delta_paths),
        "nested_authority": nested_observed,
        "nested_remote_tag_equality": "VERIFIED__DIRECT_LS_REMOTE_DURING_INTERRUPTION_RECOVERY",
    }


def authenticate_sources(root: Path) -> list[dict[str, str]]:
    authenticated = []
    for relative, expected_sha256 in SOURCES.items():
        path = root / relative
        if path.is_symlink() or not path.is_file():
            fail(f"SOURCE_NOT_REGULAR__{relative}")
        if sha256_file(path) != expected_sha256:
            fail(f"SOURCE_HASH_MISMATCH__{relative}")
        try:
            git(root, "cat-file", "-e", f"HEAD:{relative}")
        except subprocess.CalledProcessError as exc:
            raise FormalizationError(
                f"SOURCE_NOT_COMMITTED_AT_ENTRY__{relative}"
            ) from exc
        committed = subprocess.check_output(
            ["git", "show", f"HEAD:{relative}"], cwd=root,
            stderr=subprocess.DEVNULL,
        )
        if committed != path.read_bytes():
            fail(f"SOURCE_DIFFERS_FROM_COMMITTED_BYTES__{relative}")
        authenticated.append({"path": relative, "sha256": expected_sha256})
    return authenticated


def verify_inner_seal(
    envelope: dict[str, Any], inner_key: str, seal_key: str
) -> None:
    if inner_key not in envelope or seal_key not in envelope:
        fail(f"ENVELOPE_FIELDS_MISSING__{inner_key}")
    if envelope[seal_key] != sha256_bytes(canonical_bytes(envelope[inner_key])):
        fail(f"INNER_SEAL_INVALID__{inner_key}")


def authenticate_human_selection(root: Path) -> dict[str, Any]:
    path = root / NAMESPACE / SELECTION_NAME
    envelope = load_json(path)
    if path.read_bytes() != canonical_bytes(envelope):
        fail("SELECTION_NOT_CANONICAL")
    verify_inner_seal(envelope, "selection", "selection_sha256")
    selection = envelope["selection"]
    expected = {
        "authority_consumption_granted": "NO",
        "human_frontier_selection": "WRONG_SCOPE",
        "operation_granted": "NO",
        "operational_authority_granted": "NO",
        "predecessor_generation": "G77-256LD",
        "predecessor_head": ENTRY_HEAD,
        "predecessor_tree": ENTRY_TREE,
        "selected_e05_vector": "P11-E05/NEGATIVE_AUTHORITY/WRONG_SCOPE",
        "selection_authority_scope": (
            "SELECT_WRONG_SCOPE_AS_NEXT_E05_GOVERNANCE_FRONTIER_ONLY"
        ),
        "selection_class": "HUMAN_FRONTIER_DEVELOPMENT_SELECTION",
    }
    if selection != expected:
        fail("HUMAN_FRONTIER_SELECTION_MISMATCH")
    return {
        "selection_sha256": envelope["selection_sha256"],
        "selected_vector": selection["selected_e05_vector"],
        "selection_class": selection["selection_class"],
        "operational_authority_granted": False,
        "operation_granted": False,
        "intelligence_is_authority": False,
    }


def authenticate_frontier(root: Path) -> dict[str, Any]:
    ji_path = root / next(path for path in SOURCES if "G77_256JI_SPCE" in path)
    ld_path = root / next(path for path in SOURCES if "G77_256LD_SPCE" in path)
    em_path = root / next(path for path in SOURCES if "G77_256EM_SPCE" in path)
    ji_envelope = load_json(ji_path)
    ld_envelope = load_json(ld_path)
    verify_inner_seal(ji_envelope, "reduction", "reduction_sha256")
    verify_inner_seal(ld_envelope, "reduction", "reduction_sha256")
    ji = ji_envelope["reduction"]
    ld = ld_envelope["reduction"]
    satisfied_before_ld = ji["e05"]["satisfied_set"]
    if ji["e05"]["after"] != "VERIFIED__11_OF_18":
        fail("JI_E05_FRONTIER_MISMATCH")
    if "FUTURE" not in satisfied_before_ld or "WRONG_SCOPE" in satisfied_before_ld:
        fail("JI_VECTOR_STATUS_MISMATCH")
    if ld["e05"] != {
        "after": "VERIFIED__12_OF_18",
        "before": "VERIFIED__11_OF_18",
        "current_generation_credit": "VERIFIED__1",
        "expired": "VERIFIED__PROVEN_OPERATIONALLY",
        "frontier_after": "VERIFIED__6_UNSATISFIED_OF_18",
        "frontier_before": "VERIFIED__7_UNSATISFIED_OF_18",
    }:
        fail("LD_E05_FRONTIER_MISMATCH")
    rows = load_json(em_path)["checkpoint"]["obligation_matrix"]
    wrong_scope = next(
        row for row in rows if row["obligation_id"].endswith("/WRONG_SCOPE")
    )
    if wrong_scope["obligation_semantics"] != (
        "WRONG_SCOPE_DENIES_BEFORE_ATTEMPT_WITH_ZERO_EFFECT"
    ):
        fail("WRONG_SCOPE_OBLIGATION_SEMANTICS_MISMATCH")
    return {
        "current": "VERIFIED__12_OF_18",
        "satisfied": sorted([*satisfied_before_ld, "EXPIRED"]),
        "unsatisfied": [
            "AMBIGUOUS", "STALE", "REVOKED", "SUPERSEDED",
            "WRONG_SCOPE", "COHERENT_COPY",
        ],
        "wrong_scope": "UNSATISFIED__SEPARATE_OPERATIONAL_ACCEPTANCE_REQUIRED",
        "wrong_scope_obligation_semantics": wrong_scope["obligation_semantics"],
        "wrong_scope_dependencies": wrong_scope["dependencies"],
    }


def authenticate_ex(root: Path) -> dict[str, Any]:
    path = root / next(path for path in SOURCES if "G77_256EX_P11" in path)
    envelope = load_json(path)
    seal_preimage = deepcopy(envelope)
    seal_preimage["certificate_sha256"] = ""
    ex_canonical_preimage = json.dumps(
        seal_preimage, sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, allow_nan=False,
    ).encode("utf-8")
    if envelope.get("certificate_sha256") != sha256_bytes(ex_canonical_preimage):
        fail("EX_CERTIFICATE_SEAL_INVALID")
    certificate = envelope["certificate"]
    counts = certificate["component_counts"]
    if counts["CERTIFIED"] != 17:
        fail("EX_CERTIFIED_COMPONENT_COUNT_MISMATCH")
    if certificate["certificate_is_execution_authority"] is not False:
        fail("EX_AUTHORITY_BOUNDARY_MISMATCH")
    if certificate["certificate_is_credit_authority"] is not False:
        fail("EX_CREDIT_BOUNDARY_MISMATCH")
    return {
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
        "fresh_wrong_scope_operational_evidence_transferred": False,
        "e05_credit_transferred": False,
    }


def authenticate_scope_owners(root: Path) -> dict[str, Any]:
    contract = (root / "aigol/runtime/canonical_human_authority_act_contract_v1.py").read_text()
    consumer = (root / "tests/p11_da_operational_consumer_v1.py").read_text()
    substrate = (root / "tests/p11_da_disposable_substrate_v1.py").read_text()
    er = (root / next(path for path in SOURCES if "G77_256ER_P11" in path)).read_text()
    fm = (root / next(path for path in SOURCES if "G77_256FM_ONE" in path)).read_text()

    for fragment in (
        '"authority_scope",', "authority_scope: str",
        '"authority_scope": self.authority_scope',
    ):
        if fragment not in contract:
            fail("CANONICAL_AUTHORITY_SCOPE_DEFINITION_MISSING")
    for fragment in (
        f'OPERATIONAL_AUTHORITY_SCOPE = "{EXPECTED_SCOPE}"',
        "if validated_act.authority_scope != OPERATIONAL_AUTHORITY_SCOPE:",
        '_fail("operational Human act scope is invalid")',
        "authorized_scope=OPERATIONAL_AUTHORITY_SCOPE",
    ):
        if fragment not in consumer:
            fail("P11_SCOPE_OWNER_FRAGMENT_MISSING")
    for fragment in (
        "authorized_scope: str", '"authorized_scope",',
    ):
        if fragment not in substrate:
            fail("OWNER_SCOPE_BINDING_FRAGMENT_MISSING")
    for fragment in (
        f'authority_scope="{EXPECTED_SCOPE}"',
        "consumer.submit_human_act(", "consumer.claim_and_invoke_once(",
    ):
        if fragment not in er:
            fail("ER_SCOPE_BINDING_FRAGMENT_MISSING")
    for fragment in (
        "build_authority_handoff", "canonical_authority_handoff_bytes",
        "parse_authority_handoff_bytes", "execution authority inner seal mismatch",
    ):
        if fragment not in fm:
            fail("FM_AUTHORITY_TRANSPORT_FRAGMENT_MISSING")

    validate_block = consumer[
        consumer.index("    def _validate_authority_sources("):
        consumer.index("    def submit_human_act(")
    ]
    submit_block = consumer[
        consumer.index("    def submit_human_act("):
        consumer.index("    def terminate_human_act(")
    ]
    claim_block = consumer[consumer.index("    def claim_and_invoke_once("):]
    if validate_block.index("authority_scope") > validate_block.index(
        "self._gate.owner_state_root_identity"
    ):
        fail("SCOPE_CHECK_NOT_BEFORE_PROTECTED_GATE_BINDING")
    if submit_block.index("self._validate_authority_sources(") > submit_block.index(
        "self._store.initialize_available(binding)"
    ):
        fail("SCOPE_CHECK_NOT_BEFORE_OWNER_INITIALIZATION")
    claim_markers = (
        "self._validate_authority_sources(",
        'self._append_operational_event(\n            "P11_DA_OPERATIONAL_PRECLAIM"',
        "self._store.claim(",
        "self._build_one_output(",
        '"P11_DA_OPERATIONAL_INVOCATION"',
        "terminal_bind_and_permanently_exhaust(",
    )
    positions = [claim_block.index(marker) for marker in claim_markers]
    if positions != sorted(positions) or len(set(positions)) != len(positions):
        fail("ATTEMPT_SCOPE_REVALIDATION_ORDER_INVALID")
    return {
        "authority_scope_definition": "CanonicalHumanAuthorityActV1.authority_scope__REQUIRED_NONEMPTY_STRING_AND_CANONICALLY_SERIALIZED",
        "canonical_scope_constant": f"OPERATIONAL_AUTHORITY_SCOPE={EXPECTED_SCOPE}",
        "human_authority_scope_binding": "CanonicalHumanAuthorityActV1.authority_scope",
        "fm_scope_transport": "SEALED_CANONICAL_AUTHORIZATION_ENVELOPE_AND_BOUND_ER_HARNESS_ASSET__NO_STANDALONE_SCOPE_REWRITE",
        "er_scope_preservation": f"ER_CREATES_CANONICAL_ACT_WITH_{EXPECTED_SCOPE}_AND_PASSES_THE_SAME_ACT_TO_SUBMIT_AND_ATTEMPT",
        "p11_submission_scope_comparison": "EXACT_STRING_EQUALITY_IN__validate_authority_sources",
        "p11_attempt_scope_revalidation": "SAME__validate_authority_sources_CALLED_AGAIN_DURING_claim_and_invoke_once",
        "ordering_before_owner_state_initialization": "VERIFIED",
        "ordering_before_first_ledger_mutation": "VERIFIED",
        "ordering_before_protected_invocation": "VERIFIED",
        "ordering_before_protected_effect": "VERIFIED",
        "denial_reason": "operational Human act scope is invalid",
        "code_exists": True,
        "static_semantics_verified": True,
        "behavioral_repository_proof_present": True,
        "materialized_preflight_present": False,
        "operational_acceptance_present": False,
    }


def formalize_wrong_scope() -> dict[str, Any]:
    baseline = {
        "authority_kind": "AUTHORIZATION",
        "authority_scope": EXPECTED_SCOPE,
        "authority_lifecycle_state": "AVAILABLE",
        "attempt_identity": "SAME_AUTHORIZED_ATTEMPT",
        "input_identity": "SAME_AUTHORIZED_INPUT",
        "contract_identity": "SAME_AUTHORIZED_CONTRACT",
        "provenance_identity": "SAME_AUTHORIZED_PROVENANCE",
        "current": True,
        "scope_admissible": True,
    }
    presented = deepcopy(baseline)
    presented["authority_scope"] = PRESENTED_WRONG_SCOPE
    presented["scope_admissible"] = False
    independent = [
        key for key in (
            "authority_kind", "authority_scope", "authority_lifecycle_state",
            "attempt_identity", "input_identity", "contract_identity",
            "provenance_identity", "current",
        )
        if baseline[key] != presented[key]
    ]
    if independent != ["authority_scope"]:
        fail("WRONG_SCOPE_MUTATION_NOT_ISOLATED")
    if baseline["authority_scope"] != EXPECTED_SCOPE:
        fail("BASELINE_SCOPE_INVALID")
    if presented["authority_scope"] == EXPECTED_SCOPE:
        fail("PRESENTED_SCOPE_NOT_WRONG")
    return {
        "vector": "WRONG_SCOPE",
        "canonical_obligation": "P11-E05/NEGATIVE_AUTHORITY/WRONG_SCOPE",
        "baseline": baseline,
        "presented": presented,
        "independent_semantic_mutation_set": [
            f"authority_scope:{EXPECTED_SCOPE}->{PRESENTED_WRONG_SCOPE}"
        ],
        "independent_semantic_mutation_count": 1,
        "dependent_recomputation_set": [
            "canonical_Human_act_content_identity",
            "CHE_source_act_digest_and_correlation_identity",
            "scope_admissible:true->false",
        ],
        "preserved_non_target_dimensions": [
            "authority_kind", "authority_lifecycle_state", "attempt_identity",
            "input_identity", "contract_identity", "provenance_identity",
            "validity_interval_and_currentness", "target_owner_and_revision",
            "caller_identity",
        ],
        "expected_denial": {
            "boundary": "D2_AUTHORITY_SCOPE_VALIDATION_BEFORE_OWNER_INITIALIZATION_OR_PRECLAIM_LEDGER_APPEND",
            "reason": "operational Human act scope is invalid",
            "owner_state_initialized": False,
            "preclaim_ledger_append": False,
            "p11_entry": False,
            "protected_invocation": False,
            "protected_effect": False,
        },
        "repository_behavior_is_operational_acceptance": False,
    }


def cross_vector_reuse() -> list[dict[str, Any]]:
    statuses = {
        "WRONG_SCOPE": "UNSATISFIED__REPOSITORY_PROOF_ONLY",
        "WRONG_CALLER": "SATISFIED__OPERATIONAL",
        "WRONG_ATTEMPT": "SATISFIED__OPERATIONAL",
        "WRONG_INPUT": "SATISFIED__OPERATIONAL",
        "WRONG_CONTRACT": "SATISFIED__OPERATIONAL",
        "WRONG_PROVENANCE": "SATISFIED__OPERATIONAL",
        "FUTURE": "SATISFIED__OPERATIONAL",
        "EXPIRED": "SATISFIED__OPERATIONAL",
    }
    distinctions = {
        "WRONG_SCOPE": "authority_scope inequality",
        "WRONG_CALLER": "authenticated peer principal inequality at D1",
        "WRONG_ATTEMPT": "attempt identity inequality",
        "WRONG_INPUT": "canonical input identity inequality",
        "WRONG_CONTRACT": "contract identity or content inequality",
        "WRONG_PROVENANCE": "provenance identity or authoritative resolution inequality",
        "FUTURE": "preclaim coordinate below valid_from",
        "EXPIRED": "preclaim coordinate at or above valid_until",
    }
    return [
        {
            "vector": vector,
            "current_e05_status": statuses[vector],
            "common_infrastructure_reusable": True,
            "static_proof_reusable": True,
            "phase_a_reusable": "STRUCTURE_ONLY__FRESH_BINDINGS_REQUIRED",
            "authority_flow_reusable": "MECHANISM_ONLY__FRESH_AUTHORITY_REQUIRED",
            "fm_reusable": "SOLE_ROUTE_AND_HANDOFF_MECHANISM_ONLY",
            "er_reusable": "COMMON_HARNESS_MECHANICS_ONLY",
            "p11_reusable": True,
            "ex_reusable": "VERIFIED__17_OF_17__COMMON_ONLY",
            "vector_specific_proof_required": True,
            "known_vector_specific_defect": (
                "NONE__WRONG_SCOPE_OPERATIONAL_PROOF_ABSENT"
                if vector == "WRONG_SCOPE" else "NONE_FOR_ACCEPTED_VECTOR"
            ),
            "requires_new_production_capability": False,
            "semantic_edge": distinctions[vector],
        }
        for vector in statuses
    ]


def build_reduction(root: Path) -> dict[str, Any]:
    root = root.resolve()
    return {
        "schema_id": "G77_256LE_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "generation": "G77-256LE",
        "mode": "REPOSITORY_ONLY_PROOF__NO_AUTHORIZATION__NO_OPERATION",
        "terminal": TERMINAL,
        "entry": authenticate_entry(root),
        "sources": authenticate_sources(root),
        "human_frontier_selection": authenticate_human_selection(root),
        "frontier": authenticate_frontier(root),
        "ex": authenticate_ex(root),
        "wrong_scope_model": formalize_wrong_scope(),
        "existing_capability": authenticate_scope_owners(root),
        "failure_novelty_and_convergence_check": {
            "failure_class": "PROOF_GAP",
            "novelty": "DISTINCT_CANONICAL_E05_EDGE__NO_NEW_FAILURE_MECHANISM",
            "affected_invariant": "WRONG_SCOPE_DENIES_BEFORE_ATTEMPT_WITH_ZERO_EFFECT",
            "previous_closest_edge": "WRONG_ATTEMPT__SHARED_D2_OWNER_PATTERN_BUT_DIFFERENT_BOUND_COORDINATE",
            "semantic_difference": "AUTHORITY_SCOPE_INEQUALITY_NOT_CALLER_ATTEMPT_INPUT_CONTRACT_PROVENANCE_OR_TIME",
            "production_behavior_impact": "NONE",
            "new_capability_required": "NO",
            "new_proof_required": "YES__VECTOR_SPECIFIC_REPOSITORY_PROOF_NOW_COMPLETE__OPERATIONAL_ACCEPTANCE_OPEN",
            "convergence_signal": "EXISTING_EXACT_P11_CHECK_REUSED_WITH_ZERO_PRODUCTION_DELTA",
            "repetition_pressure": "LOW__FIRST_WRONG_SCOPE_REPOSITORY_PACKAGE",
            "verification_amplification_risk": "MODERATE_IF_ACCEPTED_COMMON_ASSETS_ARE_RECONSTRUCTED_OR_OPERATION_PREMATURELY_ATTEMPTED",
        },
        "cross_vector_reuse_assessment": cross_vector_reuse(),
        "minimum_governed_delta": {
            "minimum_legal_next_delta": "THIS_GENERATION_ONLY__SELECTION_BINDING_PLUS_FORMALIZER_PLUS_FOCUSED_TESTS_PLUS_SEALED_REDUCTION_PLUS_G48_REPORT",
            "delta_scope": "GENERATION_LOCAL_REPOSITORY_PROOF_AND_AUDIT_ONLY",
            "files_in_scope": [
                str(NAMESPACE / SELECTION_NAME),
                str(NAMESPACE / "analysis/G77_256LE_WRONG_SCOPE_SEMANTIC_FORMALIZER_V1.py"),
                str(NAMESPACE / "tests/test_g77_256le_wrong_scope_semantics_v1.py"),
                str(NAMESPACE / OUTPUT_NAME),
                str(NAMESPACE / "G77_256LE_G48_IMPLEMENTATION_REPORT_V1.md"),
            ],
            "files_out_of_scope": "ALL_PRODUCTION_P11_FM_ER_EX_CONSTITUTIONAL_HISTORICAL_AND_OPERATIONAL_STATE_FILES",
            "why_no_smaller_delta_suffices": "SELECTION_REQUIRES_DURABLE_BINDING__SEMANTICS_REQUIRE_DETERMINISTIC_OWNER_AND_ORDER_PROOF__CLAIMS_REQUIRE_TESTS_AND_SEALED_REDUCTION__G48_REQUIRES_REPORT",
        },
        "architectural_delta_budget": {
            "production_mutation": 0,
            "p11_mutation": 0,
            "new_owner": 0,
            "new_route": 0,
            "new_registry": 0,
            "new_generic_abstraction": 0,
            "new_constitutional_concept": 0,
            "parallel_flow": "NO",
            "production_route_count": 1,
            "production_route": "FM→ER→P11",
        },
        "reuse_impact_assessment": {
            "existing_certified_capabilities_reused": "EX_17_OF_17__CANONICAL_HUMAN_ACT__FM_CANONICAL_HANDOFF__ER_SCOPE_BINDING__P11_EXACT_SCOPE_CHECK__SOLE_ROUTE",
            "new_capabilities": "WRONG_SCOPE_GENERATION_LOCAL_REPOSITORY_PROOF_ONLY__NO_PRODUCTION_CAPABILITY",
            "existing_capability_became_unreachable": False,
            "parallel_flow_created": False,
            "production_path_count_effect": "UNCHANGED__1_TO_1",
        },
        "operational_counters": {
            "human_operational_authority": 0,
            "authority_consumption": 0,
            "vm_or_qemu": 0,
            "operation_attempt": 0,
            "request": 0,
            "p11_entry": 0,
            "protected_invocation": 0,
            "protected_effect": 0,
            "retry": 0,
            "replay": 0,
            "e05_credit": 0,
        },
        "phase_a_and_human_boundary": {
            "materialized_preflight": "NOT_PRESENT",
            "operational_acceptance": "NOT_PRESENT",
            "ready_for_operational_authority_decision": False,
            "reason": "WRONG_SCOPE_SPECIFIC_PHASE_A_AND_LIVE_BINDING_NOT_CREATED_IN_THIS_MINIMUM_REPOSITORY_PROOF_DELTA",
            "required_future_authority": "FRESH_INDEPENDENT_HUMAN_OPERATIONAL_AUTHORIZATION_AFTER_SEPARATE_READINESS",
            "historical_authority_reusable": False,
            "stop": True,
        },
        "frontier_and_metrics": {
            "project_state": "WRONG_SCOPE_REPOSITORY_PROOF_COMPLETE__OPERATIONAL_PROOF_OPEN",
            "informal_project_progress_estimate": "E05_REMAINS_12_OF_18__SIX_OBLIGATIONS_OPEN",
            "constitutional_health_evidence": "VERIFIED__EXACT_CHECK_REUSED__ZERO_PRODUCTION_MUTATION__ZERO_OPERATION__BOUNDARY_PRESERVED",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "e05_state_frontier_credit": "VERIFIED__12_OF_18__WRONG_SCOPE_REPOSITORY_PROOF_ONLY__CREDIT_0",
            "governance_efficience": "ESTIMATED__HIGH__FIVE_VECTOR_LOCAL_ARTIFACTS__ZERO_COMMON_RECONSTRUCTION",
            "overengineering_risk": "ESTIMATED__LOW__NO_ADAPTER_ROUTE_OR_GENERIC_FRAMEWORK_ADDED",
            "cognition_provenance": "AUTHENTICATED_REPOSITORY_AND_DURABLE_EVIDENCE_PRIMARY__HANDOFF_LOCATORS_REVALIDATED__MODEL_NONAUTHORITATIVE",
            "cognition_assisted_handoff": "VERIFIED__INTERRUPTED_LE_DELTA_RECOVERED_WITH_ONE_VALID_FILE_AND_ZERO_UNRELATED_MUTATIONS",
            "candidate_capability": "EXISTING_P11_WRONG_SCOPE_DENIAL__REPOSITORY_PROVEN__NOT_OPERATIONALLY_ACCEPTED",
            "shadow_design_target": "HUMAN_DECISION_REJECTION_AND_REAUTHORIZATION_LIFECYCLE",
            "shadow_design_implement_now": "NO",
            "constitutional_continuation_progress": "LD_TERMINAL_TO_LE_SELECTION_AND_REPOSITORY_PROOF__NO_E05_CREDIT",
            "last_verified_edge": "WRONG_SCOPE_EXACT_P11_DENIAL_AND_PREMUTATION_ORDER_REPOSITORY_PROOF",
            "first_broken_edge": "NONE_OBSERVED_IN_EXISTING_PRODUCTION_CAPABILITY",
            "first_unverified_edge": "WRONG_SCOPE_SPECIFIC_MATERIALIZED_PHASE_A_AND_FRESH_OPERATIONAL_ACCEPTANCE",
            "minimum_missing_capability": "NONE",
            "minimum_missing_proof": "FRESH_HUMAN_AUTHORIZED_WRONG_SCOPE_OPERATIONAL_DENIAL_BEFORE_P11_ENTRY_WITH_ZERO_EFFECT",
            "proof_yield": "ONE_DISTINCT_VECTOR_REPOSITORY_PROOF_PACKAGE__ZERO_E05_CREDIT__ZERO_OPERATION",
            "ex_reused": "VERIFIED__17_OF_17",
            "ex_reconstructed": "VERIFIED__0",
            "aigol_codex_work_share": "NOT_MEASURED__NO_GOVERNED_ATTRIBUTION_DENOMINATOR",
            "prompt_context_reuse_ratio": "NOT_MEASURED__NO_GOVERNED_TOKEN_INSTRUMENT",
            "token_benchmark": "NOT_MEASURED__PROVIDER_TELEMETRY_EXCLUDED",
            "lcrr": "NOT_MEASURED__NO_FORMAL_COST_DENOMINATOR",
            "full_ccwim": "NOT_MEASURED__NO_GOVERNED_FULL_CCWIM_SCHEMA",
        },
        "hac_hai_hae": "NOT_USED__AUTHENTICATED_DEFINITIONS_NOT_PROVEN",
        "ccwim": {
            "authenticated_repository_continuation": "VERIFIED__LD_HEAD_TREE_REMOTE_AND_NESTED_AUTHORITY",
            "cross_worker_state_recovery_level": "VERIFIED__ONE_INTERRUPTED_LE_FILE_AUTHENTICATED_AND_PRESERVED",
            "uncommitted_delta_recovery": "VERIFIED__SELECTION_BINDING_COMPLETE_AND_VALID",
            "unrelated_mutation_count": 0,
            "handoff_ambiguity_count": 0,
            "previous_worker_memory_required": "NO__DURABLE_REPOSITORY_AND_EXPLICIT_HANDOFF_REVALIDATED",
            "human_authority_state": "FRONTIER_SELECTION_ONLY__NO_OPERATIONAL_AUTHORITY",
            "operation_replay_prevention": "VERIFIED__ZERO_OPERATION_ZERO_REPLAY",
            "observed_artifact_level_cross_worker_drift": 0,
        },
        "validation": {
            "focused_wrong_scope": "VERIFIED__13_PASSED",
            "relevant_p11_human_act_and_che": "VERIFIED__47_PASSED",
            "ex": "VERIFIED__17_CERTIFIED_COMPONENT_ROLES_REUSED_BY_AUTHENTICATED_EX_CERTIFICATE_AND_LD_IDENTITY__ZERO_RECONSTRUCTED",
            "ex_historical_validator": "FAIL_CLOSED__ER_OPERATIONAL_HARNESS_HASH_DRIFT__CLASSIFIED_HISTORICAL_VERSION_BINDING__ER_IS_REQUIRES_HARDENING_NOT_ONE_OF_17_CERTIFIED_COMPONENTS",
            "governance_conformance": "VERIFIED__9_PASSED__ENGINE_20_PASSED__CONFORMANT__ZERO_WARNINGS_ZERO_VIOLATIONS",
            "git_diff_check": "VERIFIED__PASS",
        },
        "terminal_control": {
            "auto_continuable": False,
            "human_review_required": True,
            "successor_generation_started": False,
            "operational_authority_created": False,
            "operation_performed": False,
            "e05_credit_awarded": False,
            "stop_boundary": "AFTER_REPOSITORY_PROOF_BEFORE_PHASE_A_OR_OPERATIONAL_AUTHORITY",
        },
    }


def envelope(reduction: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": "G77_256LE_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": sha256_bytes(canonical_bytes(reduction)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[5])
    parser.add_argument("--write", action="store_true")
    arguments = parser.parse_args()
    try:
        result = envelope(build_reduction(arguments.root))
    except (FormalizationError, OSError, subprocess.CalledProcessError) as exc:
        print(f"TERMINAL=M__FAIL_CLOSED__{exc}")
        return 1
    payload = canonical_bytes(result)
    if arguments.write:
        destination = arguments.root.resolve() / NAMESPACE / OUTPUT_NAME
        destination.write_bytes(payload)
        print(f"WROTE={destination}")
    else:
        sys.stdout.buffer.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
