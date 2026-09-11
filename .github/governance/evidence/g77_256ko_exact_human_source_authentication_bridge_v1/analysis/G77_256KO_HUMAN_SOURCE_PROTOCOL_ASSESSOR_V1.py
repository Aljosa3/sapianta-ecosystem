#!/usr/bin/env python3
"""Authenticate and seal the pre-Human KO source-capture bridge."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
KO = ROOT / ".github/governance/evidence/g77_256ko_exact_human_source_authentication_bridge_v1"
KN = ROOT / ".github/governance/evidence/g77_256kn_fresh_expired_operational_recommissioning_v1"
INSTRUCTION = KO / "G77_256KO_DIRECT_HUMAN_ACT_INSTRUCTION_V1.txt"
OUTPUT = KO / "G77_256KO_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
KN_SOURCE = KN / "G77_256KN_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"

HEAD = "64cf75ddc215009273713c08165b1058fef8b424"
TREE = "87773ea9260b80a03dc2c2555606ecc2db9a8a6e"
SUBJECT = "G77-256KN fail closed at exact Human source authentication"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
GENERATION = "G77_256KN_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256KN_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001"
CANDIDATE = "8af5ba1cbf9e396aa2f4f981a6f20b821c5fd1c38e091ed1cb3646c76c953b4a"
DECISION_PRESENTATION = "9b95f4ad710b607b0c8607da4b2b720d5e8bf94929f4f39dc4e121cc5b5f2f12"
KN_TERMINAL = (
    "M__KN_HUMAN_SOURCE_EXACT_BYTES_NOT_INDEPENDENTLY_AUTHENTICATABLE"
    "__NO_AUTHORITY_CONSUMPTION__NO_PHASE_B__NO_OPERATION"
)
TERMINAL = (
    "A__KO_EXISTING_KN_DECISION_OBJECT_READY_FOR_DIRECT_AUTHENTICATED_HUMAN_SOURCE_ACT"
    "__NO_AUTHORITY_CONSUMPTION__NO_PHASE_B"
)

EXPECTED_HUMAN_ACT = """I authorize exactly one bounded G77_256KN SPCE Phase-B attempt for:

GENERATION G77_256KN_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1
OPERATION G77_256KN_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001
CANDIDATE_SHA256 8af5ba1cbf9e396aa2f4f981a6f20b821c5fd1c38e091ed1cb3646c76c953b4a
HUMAN_DECISION_PRESENTATION_SHA256 9b95f4ad710b607b0c8607da4b2b720d5e8bf94929f4f39dc4e121cc5b5f2f12
PURPOSE Perform exactly one fresh Human-authorized EXPIRED operational attempt in the same G77-256KN generation to observe whether EXPIRED is denied before P11 entry after the KF repair.
AUTHORITY_SCOPE ONE_KN_GENERATION__ONE_KN_OPERATION__ONE_AUTHORITY_CONSUMPTION_MAXIMUM__ONE_OPERATIONAL_ATTEMPT_MAXIMUM
NOT_AUTHORIZED NO_REPLAY__NO_REPAIR_RETRY__NO_SECOND_OPERATION__NO_ALTERNATE_AUTHORITY_PATH__NO_P11_BYPASS__NO_PARALLEL_ROUTE__NO_AUTHORITY_TRANSFER__NO_HISTORICAL_AUTHORITY_REUSE__NO_EXPANSION_OF_PRODUCTION_BEHAVIOR
EXPECTED_ROUTE FM_TO_ER_TO_P11
E05_BEFORE_OPERATION VERIFIED__11_OF_18
EXPIRED_BEFORE_OPERATION NOT_PROVEN_OPERATIONALLY

I understand that this file is my direct Human act, authority may be consumed at most once, and EXPIRED denial before P11 entry remains unproven until operationally observed.
"""

AUTHENTICATED_FILES = {
    KN / "G77_256KN_PHASE_B_AUTHORITY_BINDING_FAIL_CLOSED_REDUCTION_V1.json":
        "d859d8d2706238503a1caa023bec6a2a963ac3d19db8caca3f0fe2a38fdee6a8",
    KN / "G77_256KN_HUMAN_DECISION_PRESENTATION_V1.txt": DECISION_PRESENTATION,
    ROOT / ".github/governance/evidence/g77_256kg_fresh_expired_operational_recommissioning_v1/orchestration/G77_256KG_PHASE_B_CONTROLLER_V1.py":
        "ba0cb126e0548b6dccf9b2ad353e9cf8b251493085a81079d7e823285cb5297e",
    ROOT / ".github/governance/evidence/g77_256kg_fresh_expired_operational_recommissioning_v1/G77_256KG_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt":
        "d11850611c8c1273dbd1484af40d1d38533f95d8f0665da418885947b32a9484",
    ROOT / ".github/governance/evidence/g77_256ka_fresh_expired_operational_recommissioning_v1/orchestration/G77_256KA_PHASE_B_CONTROLLER_V1.py":
        "44cde7913d6fef0a3c48cb7b96b82e7b79605c94a963f2acd0f36b0b0f80e34e",
    ROOT / ".github/governance/evidence/g77_256jz_fm_authority_digest_handoff_repair_v1/analysis/G77_256JZ_PRECONSUMPTION_INVOCATION_BINDING_FORMALIZER_V1.py":
        "3832d64c3e071bfe66926cd545c8fd13d133284fcfe7d40c568b1dfebb9340c5",
    ROOT / ".github/governance/evidence/g77_256kh_jz_digest_semantics_assessment_v1/G77_256KH_SPCE_TERMINAL_REPOSITORY_ONLY_ASSESSMENT_V1.json":
        "1d862eadfe196663396f5e13a1d6bc7883a80b5415443c971c2bb0349d4fcad1",
    ROOT / ".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py":
        "cd3aed49b8f1ca35e53ca4ee31f278dd038fc28fe912175602180be9a2a8a5c3",
    ROOT / ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py":
        "e1db7e6d59d81a85ee025b27c3145abe697c1097822694498a4ad686d2406c51",
}

FORBIDDEN_KN_POSTHUMAN = (
    "G77_256KN_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json",
    "G77_256KN_PRECONSUMPTION_INVOCATION_BINDING_V1.json",
    "G77_256KN_PHASE_B_PRECONSUMPTION_READINESS_CHECKPOINT_V1.json",
    "G77_256KN_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json",
    "G77_256KN_FM_OPERATIONAL_INVOCATION_ATTEMPT_V1.json",
    "G77_256KN_FM_OPERATIONAL_INVOCATION_RESULT_V1.json",
)


class KOAssessmentError(RuntimeError):
    """Deterministic KO bridge assessment failure."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*arguments: str) -> str:
    return subprocess.check_output(["git", *arguments], cwd=ROOT, text=True).strip()


def load_envelope(path: Path, inner: str) -> dict[str, Any]:
    raw = path.read_bytes()
    envelope = json.loads(raw)
    if not isinstance(envelope, dict) or raw != canonical_bytes(envelope):
        raise KOAssessmentError(f"NONCANONICAL_JSON:{path.name}")
    value = envelope.get(inner)
    if not isinstance(value, dict):
        raise KOAssessmentError(f"MISSING_INNER_OBJECT:{path.name}")
    if envelope.get(f"{inner}_sha256") != hashlib.sha256(canonical_bytes(value)).hexdigest():
        raise KOAssessmentError(f"SEAL_MISMATCH:{path.name}")
    return value


def instruction_human_bytes() -> bytes:
    text = INSTRUCTION.read_text(encoding="utf-8")
    begin = "--- BEGIN EXACT HUMAN-SOURCE BYTES ---\n"
    end = "--- END EXACT HUMAN-SOURCE BYTES ---\n"
    if text.count(begin) != 1 or text.count(end) != 1:
        raise KOAssessmentError("HUMAN_INSTRUCTION_MARKER_MISMATCH")
    body = text.split(begin, 1)[1].split(end, 1)[0]
    return body.encode("utf-8")


def zero_counters() -> dict[str, int]:
    return {
        "operational_authorization_count": 0,
        "authority_consumption_count": 0,
        "pre_operational_invocation_count": 0,
        "fm_operational_invocation_count": 0,
        "qemu_start_count": 0,
        "vm_start_count": 0,
        "operation_attempt_count": 0,
        "operation_request_count": 0,
        "expired_denial_count": 0,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "retry_count": 0,
        "repair_retry_count": 0,
        "replay_count": 0,
    }


def authenticate_inputs() -> None:
    if (
        git("branch", "--show-current") != BRANCH
        or git("remote", "get-url", "origin") != ORIGIN
        or git("rev-parse", "HEAD") != HEAD
        or git("rev-parse", "HEAD^{tree}") != TREE
        or git("log", "-1", "--format=%s") != SUBJECT
        or git("diff", "--name-only") != ""
        or git("diff", "--cached", "--name-only") != ""
    ):
        raise KOAssessmentError("ENTRY_CHECKPOINT_MISMATCH")
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ANCHOR, "HEAD"], cwd=ROOT, check=False
    )
    if ancestor.returncode != 0:
        raise KOAssessmentError("STABLE_ANCESTRY_MISMATCH")
    if (
        git("-C", "sapianta_system", "remote", "get-url", "origin")
        != "git@github.com:Aljosa3/sapianta-core.git"
        or git("-C", "sapianta_system", "rev-parse", "HEAD")
        != "3183bab71f8f30397c0309dd2e6d846d14a11f66"
        or git("-C", "sapianta_system", "rev-parse", "HEAD^{tree}")
        != "7c32ec05efc2be43297849bc38ec8766514a523d"
        or git("-C", "sapianta_system", "branch", "--show-current") != ""
        or git("-C", "sapianta_system", "status", "--short") != ""
    ):
        raise KOAssessmentError("NESTED_AUTHORITY_MISMATCH")
    for path, expected in AUTHENTICATED_FILES.items():
        if sha256_path(path) != expected:
            raise KOAssessmentError(f"AUTHENTICATED_FILE_MISMATCH:{path.name}")
    kn = load_envelope(
        KN / "G77_256KN_PHASE_B_AUTHORITY_BINDING_FAIL_CLOSED_REDUCTION_V1.json",
        "reduction",
    )
    if (
        kn.get("terminal") != KN_TERMINAL
        or kn.get("human_authority", {}).get("authority_consumption_count") != 0
        or kn.get("phase_b_started") is not False
        or set(kn.get("operational_counters", {}).values()) != {0}
        or kn.get("e05", {}).get("after") != "VERIFIED__11_OF_18"
        or kn.get("e05", {}).get("kn_e05_credit") != "VERIFIED__0"
    ):
        raise KOAssessmentError("KN_TERMINAL_STATE_MISMATCH")
    if KN_SOURCE.exists() or KN_SOURCE.is_symlink():
        raise KOAssessmentError("DIRECT_HUMAN_ACT_ALREADY_PRESENT")
    for name in FORBIDDEN_KN_POSTHUMAN:
        path = KN / name
        if path.exists() or path.is_symlink():
            raise KOAssessmentError(f"UNEXPECTED_POSTHUMAN_ARTIFACT:{name}")
    if instruction_human_bytes() != EXPECTED_HUMAN_ACT.encode("utf-8"):
        raise KOAssessmentError("DIRECT_HUMAN_ACT_INSTRUCTION_BYTES_MISMATCH")
    kg_controller = next(
        path for path in AUTHENTICATED_FILES if path.name == "G77_256KG_PHASE_B_CONTROLLER_V1.py"
    ).read_text(encoding="utf-8")
    if (
        "source.read_bytes() != EXPECTED_HUMAN_ACT.encode()" not in kg_controller
        or "hashlib.sha256(source.read_bytes()).hexdigest()" not in kg_controller
        or "SOURCE.write" in kg_controller
        or "SOURCE.write_text" in kg_controller
        or "SOURCE.write_bytes" in kg_controller
    ):
        raise KOAssessmentError("HISTORICAL_HUMAN_SOURCE_PROTOCOL_MISMATCH")


def build_reduction() -> dict[str, Any]:
    return {
        "architecture": {
            "new_constitutional_concept_count": 0,
            "new_generic_abstraction_count": 0,
            "new_owner_count": 0,
            "new_registry_count": 0,
            "new_route_count": 0,
            "p11_implementation_mutation_count": 0,
            "parallel_flow": "NO",
            "production_mutation_count": 0,
            "production_route_after": 1,
            "production_route_before": 1,
        },
        "auto_continuable": False,
        "ccwim": {
            "authenticated_repository_continuation": "VERIFIED__YES",
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION",
            "handoff_ambiguity_count": "VERIFIED__0",
            "handoff_reconstruction_success": "VERIFIED__YES",
            "observed_artifact_level_cross_worker_drift": "VERIFIED__0",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
        },
        "cross_vector_reuse_assessment": {
            "applicable_vectors": ["EXPIRED", "FUTURE", "WRONG_ATTEMPT", "WRONG_CONTRACT", "WRONG_INPUT", "WRONG_PROVENANCE"],
            "common_proof_reuse_is_vector_operational_proof": False,
            "cross_vector_reuse_scope": "VERIFIED__MULTI_VECTOR_REUSABLE",
            "expected_future_proof_reduction": "ESTIMATED__REUSE_EXACT_SOURCE_BYTE_VALIDATION_DERIVED_DIGEST_HANDOFF_AND_ONE_SHOT_GUARDS__NO_VECTOR_OPERATIONAL_CREDIT",
            "multi_vector_reuse_is_authority_transfer": False,
            "reusable_component": "DIRECT_HUMAN_UTF8_SOURCE_BYTES_TO_DERIVED_DIGEST_TO_CANONICAL_HANDOFF_TO_ONE_SHOT_CONSUMPTION_PATTERN",
            "reuse_invariant": "HUMAN_SOURCE_PROVENANCE_AND_EXACT_BYTES_MUST_PRECEDE_AUTHORITY_BINDING_AND_CONSUMPTION",
            "reuse_preconditions": "DIRECT_HUMAN_ACT_AFTER_PRESENTATION__EXACT_GENERATION_BINDING__UNCONSUMED_NAMESPACE__CURRENT_TEMPORAL_AND_VECTOR_REVALIDATION",
            "revalidation_required": "VERIFIED__PER_GENERATION_PRESENTATION_SOURCE_PROVENANCE_TEMPORAL_SCOPE_AND_VECTOR_OPERATION",
            "vector_specific_residue": "PRESENTATION_COORDINATES__TEMPORAL_VALIDITY__AUTHORITY_SCOPE__OPERATIONAL_ACCEPTANCE__E05_CREDIT",
        },
        "e05": {
            "after": "VERIFIED__11_OF_18",
            "before": "VERIFIED__11_OF_18",
            "credit": "VERIFIED__0",
            "expired": "NOT_PROVEN_OPERATIONALLY",
            "frontier": "VERIFIED__7_UNSATISFIED_OF_18",
            "kn_e05_credit": "VERIFIED__0",
        },
        "entry": {
            "ancestry_anchor": ANCHOR,
            "ancestry_verified": True,
            "branch": BRANCH,
            "head": HEAD,
            "index_empty": True,
            "origin": ORIGIN,
            "remote_equality": "VERIFIED__DIRECT_BRANCH_LS_REMOTE",
            "remote_head": HEAD,
            "subject": SUBJECT,
            "tree": TREE,
            "worktree_entry_clean": True,
        },
        "ex": {"ex_reconstructed": "VERIFIED__0", "ex_reused": "VERIFIED__17_OF_17"},
        "failure_novelty_and_convergence_check": {
            "acceptance_requirement_forcing_continuation": "VERIFIED__EXACT_DIRECT_HUMAN_ACT_IS_REQUIRED_BEFORE_SAME_GENERATION_KN_PHASE_B",
            "affected_invariant": "EXACT_HUMAN_SOURCE_BYTES_MUST_BE_AUTHENTICATED_BEFORE_AUTHORITY_BINDING_OR_CONSUMPTION",
            "classification_confidence": "VERIFIED__HIGH",
            "classification_evidence": "VERIFIED__COMMITTED_KN_TERMINAL__KG_KA_JZ_KH_GN_FM_PROTOCOL_BYTES__KN_SOURCE_ABSENT",
            "convergence_signal": "VERIFIED__EXISTING_PROTOCOL_REUSED__NO_NEW_AUTHORITY_OWNER_OR_ROUTE_REQUIRED__DIRECT_HUMAN_ACT_REMAINS",
            "failure_class": "PROOF_GAP",
            "new_capability_required": "NOT_PROVEN",
            "new_proof_required": "VERIFIED__DIRECT_HUMAN_ORIGINATED_EXACT_SOURCE_BYTES_BOUND_TO_EXISTING_KN_PRESENTATION",
            "novelty": "VERIFIED__NOT_NEW__SAME_KN_AUTHORITY_SOURCE_GAP_WITH_EXISTING_CAPTURE_PROTOCOL_NOW_EXPOSED",
            "previous_closest_edge": "KG_EXACT_HUMAN_ACT_AUTHENTICATED_BEFORE_PRECONSUMPTION_DIGEST_CHECK",
            "production_behavior_impact": "VERIFIED__NONE__KO_IS_REPOSITORY_ONLY_NONAUTHORITY",
            "repetition_pressure": "ESTIMATED__HIGH",
            "semantic_difference": "VERIFIED__NO_NEW_AUTHORITY_SEMANTIC__KO_EXPOSES_THE_EXISTING_DIRECT_SOURCE_CAPTURE_BOUNDARY_FOR_KN",
            "verification_amplification_risk": "ESTIMATED__HIGH_IF_SOURCE_BYTES_ARE_AI_WRITTEN_OR_PHASE_A_IS_REPEATED",
        },
        "frontier": {
            "current_real_blocker": "VERIFIED__DIRECT_HUMAN_ACT_HAS_NOT_YET_CREATED_THE_KN_SOURCE_BYTES",
            "first_broken_edge": "DIRECT_HUMAN_ORIGINATION_OF_EXACT_KN_SOURCE_BYTES_THROUGH_THE_AUTHENTICATED_CAPTURE_BOUNDARY",
            "first_unverified_operational_edge": "FRESH_HUMAN_AUTHORIZED_EXPIRED_DENIAL_BEFORE_P11_ENTRY_AFTER_KF_REPAIR",
            "last_verified_edge": "EXISTING_HUMAN_SOURCE_PROTOCOL_AUTHENTICATED_AND_EXACT_KN_DIRECT_ACT_INSTRUCTION_SEALED",
            "last_verified_operational_edge": "EXACT_HUMAN_AUTHORITY_AUTHENTICATED_JZ_BOUND_CONSUMED_ONCE_AND_ONE_NO_NETWORK_VM_BOOT_REACHED_GUEST_CUSTODY_LOAD",
            "minimum_legal_next_delta": "HUMAN_PERSONALLY_CREATES_THE_EXACT_KN_SOURCE_FILE__THEN_SEPARATE_POSTHUMAN_AUTHENTICATION",
            "minimum_missing_capability": "NOT_PROVEN__NO_NEW_CAPABILITY__DIRECT_HUMAN_ACT_REQUIRED",
        },
        "governance": {
            "candidate_capability": "VERIFIED__EXISTING_KN_DECISION_OBJECT_READY_FOR_DIRECT_HUMAN_SOURCE_ACT_ONLY",
            "cognition_assisted_handoff": "VERIFIED__REPOSITORY_ONLY_REPLAY_SAFE_KO_PREHUMAN_BRIDGE",
            "cognition_provenance": "VERIFIED__COMMITTED_KN__KG_KA_JZ_KH_GN_FM_PROTOCOL__SEALED_KO_EVIDENCE_PRIMARY",
            "constitutional_continuation_progress": "VERIFIED__KNOWN_KN_SOURCE_GAP_TO_EXACT_DIRECT_HUMAN_INTERACTION_BOUNDARY",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "constitutional_health_evidence": "VERIFIED__FAIL_CLOSED__NO_AI_WRITTEN_SOURCE__NO_AUTHORITY__ALL_COUNTERS_ZERO__ONE_ROUTE",
            "governance_efficiency": "ESTIMATED__HIGH__EXISTING_PROTOCOL_REUSED_WITH_ZERO_PRODUCTION_MUTATION",
            "informal_project_progress_estimate": "ESTIMATED__AUTHORITY_PROTOCOL_READY__ONE_DIRECT_HUMAN_ACT_REMAINS_BEFORE_POSTHUMAN_AUTHENTICATION",
            "overengineering_risk": "ESTIMATED__HIGH_IF_A_SECOND_CAPTURE_PROTOCOL_OR_AUTOMATED_SOURCE_WRITER_IS_CREATED",
            "project_progress": "VERIFIED__EXISTING_HUMAN_SOURCE_CAPTURE_PROTOCOL_AUTHENTICATED_AND_EXPOSED_FOR_KN",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "project_state": "VERIFIED__KO_PREHUMAN_BRIDGE_READY_AT_DIRECT_HUMAN_ACT_BARRIER",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "shadow_design_target": "VERIFIED__SOLE_EXISTING_SOURCE_TO_FM_ER_P11_CHAIN__NOT_INVOKED",
        },
        "hac_hai_hae": "NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED",
        "human_interaction": {
            "exact_human_act_sha256_expected_after_direct_creation": hashlib.sha256(EXPECTED_HUMAN_ACT.encode("utf-8")).hexdigest(),
            "human_authority_authentication": "NOT_APPLICABLE__DIRECT_HUMAN_ACT_NOT_YET_PERFORMED",
            "human_authority_binding": "NOT_APPLICABLE__NO_SOURCE_BYTES",
            "human_authority_present": False,
            "human_source_decision_status": "NOT_APPLICABLE__AWAITING_DIRECT_HUMAN_ACT",
            "human_source_provenance": "NOT_PROVEN__DIRECT_HUMAN_ACT_NOT_YET_PERFORMED",
            "instruction_path": INSTRUCTION.relative_to(ROOT).as_posix(),
            "kn_source_path": KN_SOURCE.relative_to(ROOT).as_posix(),
        },
        "human_review_required": True,
        "operational_counters": zero_counters(),
        "operational_observation": "NOT_APPLICABLE__PREHUMAN_REPOSITORY_ONLY_BRIDGE",
        "phase_b_started": False,
        "proof_yield": {
            "new_blocker_closed_count": "VERIFIED__0",
            "new_blocker_localized_count": "VERIFIED__0__SAME_KN_SOURCE_GAP",
            "new_classification_result_count": "VERIFIED__1__KNOWN_PROOF_GAP_REAUTHENTICATED",
            "new_false_or_superseded_blocker_removed_count": "VERIFIED__0",
            "new_operational_capability_count": "VERIFIED__0",
            "new_verified_capability_count": "VERIFIED__0__EXISTING_PROTOCOL_EXPOSED_NOT_NEW_AUTHORITY_CAPABILITY",
            "proof_reuse_count": "VERIFIED__17__EX_COMMON_COMPONENTS",
        },
        "protocol_discovery": {
            "authenticated_consumption_rule": "VERIFIED__COLLISION_GUARDED_EXACTLY_ONCE__NONREUSABLE__NONTRANSFERABLE__NO_RETRY_REPLAY",
            "authenticated_handoff_rule": "VERIFIED__DERIVED_SOURCE_DIGEST_BOUND_IN_CANONICAL_FM_AUTHORITY_HANDOFF_AND_JZ_PRECONSUMPTION_BINDING",
            "authenticated_human_act_capture_mechanism": "VERIFIED__HUMAN_PERSONALLY_CREATES_GENERATION_LOCAL_UTF8_SOURCE_FILE_AFTER_PRESENTATION__NO_REPOSITORY_WRITER",
            "authenticated_human_source_artifact_type": "VERIFIED__GENERATION_LOCAL_UTF8_TEXT_FILE__LF_TERMINATED__GIT_MODE_100644_WHEN_COMMITTED",
            "authenticated_human_source_owner": "VERIFIED__DIRECT_HUMAN_ACT_AT_GENERATION_LOCAL_SOURCE_BOUNDARY__VALIDATED_BY_EXISTING_PHASE_B_CONTROLLER_CHAIN",
            "authenticated_presentation_binding_rule": "VERIFIED__EXACT_SOURCE_TEXT_ENUMERATES_KN_PRESENTATION_HASH_GENERATION_OPERATION_CANDIDATE_SCOPE_AND_LIMITS",
            "authenticated_source_byte_rule": "VERIFIED__RAW_FILE_BYTES_EXACTLY_EQUAL_PRESENTED_ACT__SHA256_DERIVED_FROM_BYTES__NO_CALLER_DIGEST",
            "authenticated_source_provenance_rule": "VERIFIED__SOURCE_FILE_MUST_BE_ABSENT_PREHUMAN_AND_ORIGINATE_FROM_DIRECT_HUMAN_ACT__AI_WRITING_FORBIDDEN",
            "authenticated_temporal_rule": "VERIFIED__SOURCE_ABSENT_AT_KO_ENTRY__DIRECT_ACT_AFTER_PRESENTATION__SAME_UNCHANGED_KN_COORDINATES__REVALIDATE_BEFORE_BINDING",
            "authority_source_mechanism": "VERIFIED__EXISTING_KG_KA_JZ_GN_FM_CHAIN_REUSABLE_FOR_KN_WITH_GENERATION_LOCAL_BINDINGS",
            "source_capture_is_authority": False,
        },
        "schema_id": "G77_256KO_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "terminal": TERMINAL,
    }


def envelope() -> dict[str, Any]:
    reduction = build_reduction()
    return {
        "schema_id": "G77_256KO_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": hashlib.sha256(canonical_bytes(reduction)).hexdigest(),
    }


def materialize() -> None:
    authenticate_inputs()
    if OUTPUT.exists() or OUTPUT.is_symlink():
        raise KOAssessmentError("KO_REDUCTION_COLLISION")
    OUTPUT.write_bytes(canonical_bytes(envelope()))
    print(TERMINAL)


def verify() -> None:
    authenticate_inputs()
    if load_envelope(OUTPUT, "reduction") != build_reduction():
        raise KOAssessmentError("KO_REDUCTION_CONTENT_MISMATCH")
    print(TERMINAL)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("materialize", "verify"))
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    materialize() if args.mode == "materialize" else verify()
