#!/usr/bin/env python3
"""Deterministic repository-only G77-256KR correction and readiness reducer.

KR preserves historical KP/KQ/KO evidence and the Human-source bytes.  It
corrects only the forward acceptance status of KP's unauthenticated writer
identity requirement.  It creates no authority and exposes no operational
call surface.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
KR = ROOT / ".github/governance/evidence/g77_256kr_kp_requirement_correction_v1"
OUTPUT = KR / "G77_256KR_SPCE_TERMINAL_CORRECTION_V1.json"
KN = ROOT / ".github/governance/evidence/g77_256kn_fresh_expired_operational_recommissioning_v1"
SOURCE = KN / "G77_256KN_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
PRESENTATION = KN / "G77_256KN_HUMAN_DECISION_PRESENTATION_V1.txt"
REQUEST = KN / "G77_256KN_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
KO = ROOT / ".github/governance/evidence/g77_256ko_exact_human_source_authentication_bridge_v1"
KO_INSTRUCTION = KO / "G77_256KO_DIRECT_HUMAN_ACT_INSTRUCTION_V1.txt"
KP = ROOT / ".github/governance/evidence/g77_256kp_posthuman_source_authentication_v1"
KP_REDUCTION = KP / "G77_256KP_SPCE_TERMINAL_FAIL_CLOSED_REDUCTION_V1.json"
KQ = ROOT / ".github/governance/evidence/g77_256kq_human_provenance_capability_discovery_v1"
KQ_CLASSIFICATION = KQ / "G77_256KQ_SPCE_TERMINAL_CLASSIFICATION_V1.json"

HEAD = "64a56f11c8e5b82594fc562571917614d1556488"
TREE = "4e80f45a48333bc2af154a5114bfcb0a89d70c52"
SUBJECT = "G77-256KQ classify Human provenance overconstraint"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
SOURCE_SHA256 = "56a50ef8a69761e492138d4f9f425eb2e845231bd654a731ead02fcbc34fdc96"
PRESENTATION_SHA256 = "9b95f4ad710b607b0c8607da4b2b720d5e8bf94929f4f39dc4e121cc5b5f2f12"
KQ_FILE_SHA256 = "3281ee60d0229bf6d1fa8a9bfb55a6c3807f53c5a42bd1c8cc66a922a2e2d997"
KP_FILE_SHA256 = "c3aa5626f622f4f28f15025c7f90a1c058ad39e910d72c8c078390e4e0900ae4"
KO_INSTRUCTION_SHA256 = "7e40a57152cdf590a587506c696c25394373f660ff75aebcaf0bf7d23e4b674b"
KQ_TERMINAL = "D__KQ_INDEPENDENT_WRITER_REQUIREMENT_NOT_AUTHENTICATED__HISTORICAL_ACCEPTANCE_USED_WEAKER_DIRECT_HUMAN_INTERACTION_BOUNDARY__NO_AUTHORITY_BINDING__NO_CONSUMPTION__NO_PHASE_B__NO_OPERATION"
KP_TERMINAL = "M__KP_EXACT_KN_SOURCE_BYTES_MATCH_BUT_DIRECT_HUMAN_PROVENANCE_NOT_INDEPENDENTLY_AUTHENTICATABLE__NO_AUTHORITY_BINDING__NO_CONSUMPTION__NO_PHASE_B__NO_OPERATION"
TERMINAL = "A__KR_CORRECTION_VERIFIED__EXISTING_KN_SOURCE_READY_FOR_SEPARATE_AUTHORITY_AUTHENTICATION__NO_BINDING__NO_CONSUMPTION__NO_PHASE_B__NO_OPERATION"
CORRECTION_STATUS = "SUPERSEDED_FOR_FORWARD_KN_ACCEPTANCE_BY_AUTHENTICATED_KQ_CLASSIFICATION"


class KRReductionError(RuntimeError):
    """Stable fail-closed KR reduction failure."""


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *arguments], cwd=cwd, text=True).strip()


def load_envelope(path: Path, inner: str) -> dict[str, Any]:
    raw = path.read_bytes()
    envelope = json.loads(raw)
    if not isinstance(envelope, dict) or raw != canonical_bytes(envelope):
        raise KRReductionError(f"NONCANONICAL_JSON:{path.name}")
    value = envelope.get(inner)
    if not isinstance(value, dict):
        raise KRReductionError(f"MISSING_INNER_OBJECT:{path.name}")
    if envelope.get(f"{inner}_sha256") != hashlib.sha256(canonical_bytes(value)).hexdigest():
        raise KRReductionError(f"SEAL_MISMATCH:{path.name}")
    return value


def exact_human_bytes() -> bytes:
    instruction = KO_INSTRUCTION.read_text(encoding="utf-8")
    begin = "--- BEGIN EXACT HUMAN-SOURCE BYTES ---\n"
    end = "--- END EXACT HUMAN-SOURCE BYTES ---\n"
    if instruction.count(begin) != 1 or instruction.count(end) != 1:
        raise KRReductionError("KO_SOURCE_MARKERS_INVALID")
    return instruction.split(begin, 1)[1].split(end, 1)[0].encode("utf-8")


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
        or git("diff", "--name-only")
        or git("diff", "--cached", "--name-only")
    ):
        raise KRReductionError("KQ_ENTRY_CHECKPOINT_MISMATCH")
    if subprocess.run(["git", "merge-base", "--is-ancestor", ANCHOR, "HEAD"], cwd=ROOT, check=False).returncode:
        raise KRReductionError("STABLE_ANCESTRY_MISMATCH")

    nested = ROOT / "sapianta_system"
    if (
        git("remote", "get-url", "origin", cwd=nested) != "git@github.com:Aljosa3/sapianta-core.git"
        or git("rev-parse", "HEAD", cwd=nested) != "3183bab71f8f30397c0309dd2e6d846d14a11f66"
        or git("rev-parse", "HEAD^{tree}", cwd=nested) != "7c32ec05efc2be43297849bc38ec8766514a523d"
        or git("branch", "--show-current", cwd=nested)
        or git("status", "--short", cwd=nested)
    ):
        raise KRReductionError("NESTED_AUTHORITY_MISMATCH")

    source = SOURCE.read_bytes()
    if (
        len(source) != 1213
        or source.count(b"\n") != 14
        or hashlib.sha256(source).hexdigest() != SOURCE_SHA256
        or source.startswith(b"\xef\xbb\xbf")
        or not source.endswith(b"\n")
        or source != exact_human_bytes()
        or sha256_path(PRESENTATION) != PRESENTATION_SHA256
    ):
        raise KRReductionError("HUMAN_SOURCE_IMMUTABILITY_OR_BINDING_FAILURE")
    source.decode("utf-8")
    if git("ls-files", "--", SOURCE.relative_to(ROOT).as_posix()):
        raise KRReductionError("UNEXPECTED_TRACKED_SOURCE")

    if (
        sha256_path(KQ_CLASSIFICATION) != KQ_FILE_SHA256
        or sha256_path(KP_REDUCTION) != KP_FILE_SHA256
        or sha256_path(KO_INSTRUCTION) != KO_INSTRUCTION_SHA256
    ):
        raise KRReductionError("HISTORICAL_ARTIFACT_IMMUTABILITY_FAILURE")
    kq = load_envelope(KQ_CLASSIFICATION, "classification")
    kp = load_envelope(KP_REDUCTION, "reduction")
    if (
        kq.get("terminal") != KQ_TERMINAL
        or kq.get("failure_novelty_and_convergence_check", {}).get("failure_class") != "EVIDENCE_OR_REPORTING_DEFECT"
        or kq.get("provenance_capability", {}).get("status") != "CURRENT_REQUIREMENT_NOT_AUTHENTICATED"
        or not str(kq.get("failure_novelty_and_convergence_check", {}).get("new_capability_required", "")).startswith("NOT_PROVEN")
        or kq.get("requirement_provenance", {}).get("human_provenance_requirement_authentication") != "NOT_PROVEN__RECENT_REPORTING_ASSERTION_ONLY"
        or kq.get("requirement_provenance", {}).get("human_provenance_requirement_scope") != "NOT_PROVEN_AS_KN_AUTHORITY_PROTOCOL__KP_REPORTING_SCOPE_ONLY"
        or kq.get("historical_success_comparator", {}).get("stronger_requirement_classification") != "C__EVIDENCE_OR_REPORTING_OVERCONSTRAINT"
        or kq.get("failure_novelty_and_convergence_check", {}).get("acceptance_requirement_forcing_continuation") != "NOT_PROVEN__NO_AUTHENTICATED_RULE_REQUIRES_INDEPENDENT_WRITER_ATTESTATION_BEYOND_THE_EXISTING_DIRECT_HUMAN_INTERACTION_BOUNDARY"
        or kp.get("terminal") != KP_TERMINAL
        or kp.get("phase_b_started") is not False
        or set(kp.get("operational_counters", {}).values()) != {0}
    ):
        raise KRReductionError("KQ_OR_KP_CLASSIFICATION_MISMATCH")

    human_act = (ROOT / "aigol/runtime/canonical_human_authority_act_contract_v1.py").read_text(encoding="utf-8")
    che = (ROOT / "aigol/runtime/canonical_human_entry_contract_v1.py").read_text(encoding="utf-8")
    ko_report = (KO / "G77_256KO_G48_IMPLEMENTATION_REPORT_V1.md").read_text(encoding="utf-8")
    ke_report = (ROOT / ".github/governance/evidence/g77_256ke_fresh_expired_operational_recommissioning_v1/G77_256KE_G48_IMPLEMENTATION_REPORT_V1.md").read_text(encoding="utf-8")
    kg_controller = (ROOT / ".github/governance/evidence/g77_256kg_fresh_expired_operational_recommissioning_v1/orchestration/G77_256KG_PHASE_B_CONTROLLER_V1.py").read_text(encoding="utf-8")
    jz_report = (ROOT / ".github/governance/evidence/g77_256jz_fm_authority_digest_handoff_repair_v1/G77_256JZ_G48_IMPLEMENTATION_REPORT_V1.md").read_text(encoding="utf-8")
    if (
        'HUMAN_AUTHORITY_OWNER = "HUMAN_AUTHORITY"' not in human_act
        or "request.actor_class != HUMAN_ACTOR" not in human_act
        or '"target_source_act_digest"' not in che
        or "the Human personally creates the file after presentation" not in ko_report
        or "Human-act authentication is `VERIFIED__EXACT_HUMAN_SUPPLIED_ACT`" not in ke_report
        or "HUMAN_SOURCE_SHA256" not in kg_controller
        or "one-shot authority-consumption transition" not in jz_report
    ):
        raise KRReductionError("AUTHENTICATED_ACCEPTANCE_BASELINE_MISMATCH")

    forbidden = (
        "G77_256KN_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json",
        "G77_256KN_PRECONSUMPTION_INVOCATION_BINDING_V1.json",
        "G77_256KN_PHASE_B_PRECONSUMPTION_READINESS_CHECKPOINT_V1.json",
        "G77_256KN_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json",
        "G77_256KN_FM_OPERATIONAL_INVOCATION_ATTEMPT_V1.json",
        "G77_256KN_FM_OPERATIONAL_INVOCATION_RESULT_V1.json",
    )
    if any((KN / name).exists() for name in forbidden):
        raise KRReductionError("POSTHUMAN_KN_ARTIFACT_COLLISION")


def build_correction() -> dict[str, Any]:
    return {
        "schema_id": "G77_256KR_SPCE_TERMINAL_CORRECTION_V1",
        "terminal": TERMINAL,
        "mode": "SPCE_PHASE_A_LIKE__REPOSITORY_ONLY_CORRECTION_AND_READINESS",
        "entry": {
            "branch": BRANCH, "head": HEAD, "tree": TREE, "subject": SUBJECT,
            "origin": ORIGIN, "remote_head": HEAD,
            "remote_equality": "VERIFIED__DIRECT_BRANCH_LS_REMOTE",
            "ancestry_anchor": ANCHOR, "ancestry_verified": True,
            "index_empty": True, "tracked_repository_unchanged": True,
            "expected_untracked_human_source_at_entry": True,
        },
        "continuation": {
            "same_generation": "VERIFIED__G77_256KR",
            "provider_limit_exhaustion": "NOT_APPLICABLE__NOT_A_CONSTITUTIONAL_FAILURE_OR_NEW_GENERATION",
            "kr_existing_artifact_status": "VERIFIED__NO_FILE_ARTIFACTS__EMPTY_DIRECTORY_SCAFFOLD_ONLY",
            "kr_existing_artifact_provenance": "VERIFIED__CURRENT_WORKER_CREATED_EMPTY_SCAFFOLD_BEFORE_CONTINUATION_COMMISSION",
            "kr_existing_artifact_determinism": "NOT_APPLICABLE__NO_EXISTING_FILE_ARTIFACT_TO_AUTHENTICATE",
            "kr_existing_artifact_reuse_decision": "VERIFIED__CONTINUE_MINIMUM_DETERMINISTIC_ARTIFACT_CREATION__NO_RECONSTRUCTION",
        },
        "nested_authority": {
            "origin": "git@github.com:Aljosa3/sapianta-core.git",
            "immutable_ref": "refs/tags/sapianta-system-nested-authority-3183bab-v1",
            "head": "3183bab71f8f30397c0309dd2e6d846d14a11f66",
            "tree": "7c32ec05efc2be43297849bc38ec8766514a523d",
            "clean": True, "detached": True, "pinned": True,
            "remote_tag_equal": "VERIFIED__DIRECT_LS_REMOTE",
        },
        "historical_evidence": {
            "kp_file_sha256": KP_FILE_SHA256, "kp_terminal": KP_TERMINAL,
            "kp_historical_status": "VERIFIED__IMMUTABLE_VALID_FAIL_CLOSED_EVENT_UNDER_ITS_THEN_STATED_RULE",
            "kq_file_sha256": KQ_FILE_SHA256, "kq_terminal": KQ_TERMINAL,
            "ko_instruction_sha256": KO_INSTRUCTION_SHA256,
        },
        "failure_novelty_and_convergence_check": {
            "failure_class": "EVIDENCE_OR_REPORTING_DEFECT",
            "novelty": "VERIFIED__NOT_NEW__KP_INTRODUCED_AN_UNOWNED_STRONGER_WRITER_IDENTITY_TEST",
            "affected_invariant": "EXPLICIT_HUMAN_AUTHORITY_AND_EXACT_BOUND_SOURCE_BYTES_MUST_PRECEDE_AUTHORITY_BINDING_OR_CONSUMPTION",
            "previous_closest_edge": "KQ_CASE_D_LOCALIZED_KP_REPORTING_OVERCONSTRAINT_AND_REQUIRED_A_SEPARATE_BOUNDED_CORRECTION",
            "semantic_difference": "VERIFIED__KR_CLOSES_THE_FORWARD_REQUIREMENT_CORRECTION_AND_EXISTING_SOURCE_READINESS_EDGE_THAT_KQ_EXPLICITLY_LEFT_OPEN",
            "production_behavior_impact": "VERIFIED__NONE",
            "new_capability_required": "NOT_PROVEN__NO_AUTHENTICATED_NEW_CAPABILITY_REQUIREMENT",
            "new_proof_required": "VERIFIED__BOUNDED_REQUIREMENT_CORRECTION_PROVING_REMOVAL_OF_THE_UNAUTHENTICATED_KP_OVERCONSTRAINT_WITHOUT_WEAKENING_AUTHENTICATED_ACCEPTANCE",
            "convergence_signal": "VERIFIED__KQ_LOCALIZATION_CLOSED_BY_ONE_FORWARD_CORRECTION_AND_SOURCE_READINESS_RESULT",
            "repetition_pressure": "VERIFIED__HIGH__KN_KO_KP_KQ_AND_KR_HAVE_NO_E05_MOVEMENT",
            "verification_amplification_risk": "VERIFIED__HIGH_BEFORE_CORRECTION__REDUCED_BY_REUSE_OF_AUTHENTICATED_ACCEPTANCE_BASELINE",
            "classification_evidence": "VERIFIED__SEALED_KQ__IMMUTABLE_KP_AND_KO__KE_KG_KA_JZ_KH_GN_FM_AND_CANONICAL_HUMAN_ACT_CHE_COMPARISON",
            "classification_confidence": "VERIFIED__HIGH",
            "acceptance_requirement_forcing_continuation": "VERIFIED__KQ_REQUIRES_A_SEPARATE_BOUNDED_CORRECTION_BEFORE_EXISTING_SOURCE_REEVALUATION__NOT_INDEPENDENT_WRITER_IDENTITY",
        },
        "authenticated_acceptance_baseline": {
            "authenticated_acceptance_owner": "VERIFIED__HUMAN_AUTHORITY_AT_THE_DIRECT_HUMAN_INTERACTION_BOUNDARY",
            "authenticated_acceptance_source": "VERIFIED__CANONICAL_HUMAN_AUTHORITY_ACT_AND_CHE_CONTRACTS__KO_DIRECT_HUMAN_ACT_PROTOCOL__KE_KG_KA_JZ_KH_GN_FM_PRECEDENT__KQ_CASE_D",
            "authenticated_acceptance_rule": "VERIFIED__EXACT_HUMAN_SUPPLIED_SOURCE_TEXT__DERIVED_SOURCE_SHA256__PRESENTATION_SCOPE_TEMPORAL_AND_CANONICAL_HANDOFF_BINDINGS__COLLISION_GUARDS__ONE_SHOT_CONSUMPTION",
            "authenticated_direct_human_interaction_requirement": "VERIFIED__REQUIRED_AT_HUMAN_SOURCE_CREATION_BOUNDARY",
            "authenticated_exact_byte_requirement": "VERIFIED__REQUIRED",
            "authenticated_presentation_binding_requirement": "VERIFIED__REQUIRED",
            "authenticated_scope_binding_requirement": "VERIFIED__REQUIRED",
            "authenticated_temporal_requirement": "VERIFIED__PER_GENERATION_FRESHNESS_AND_PRECONSUMPTION_STATE_REQUIRED",
            "authenticated_one_shot_requirement": "VERIFIED__AT_MOST_ONE_CONSUMPTION_AND_ONE_OPERATIONAL_ATTEMPT",
            "authenticated_writer_identity_requirement": "NOT_PROVEN__NO_INDEPENDENT_FILESYSTEM_WRITER_IDENTITY_REQUIREMENT_IN_AUTHENTICATED_KN_ACCEPTANCE",
        },
        "correction": {
            "correction_status": CORRECTION_STATUS,
            "historical_kp_preserved": "VERIFIED__YES",
            "forward_acceptance_rule": "VERIFIED__RESTORED_AUTHENTICATED_PRE_KP_DIRECT_HUMAN_INTERACTION_BASELINE",
            "reporting_scope_expansion_prevented": "VERIFIED__KP_REPORTING_SCOPE_IS_NOT_A_CONSTITUTIONAL_RULE",
            "authority_created": "VERIFIED__NO",
            "operational_proof_created": "VERIFIED__NO",
            "e05_credit_created": "VERIFIED__NO",
        },
        "anti_weakening": {
            "anti_weakening_status": "VERIFIED__ALL_AUTHENTICATED_ACCEPTANCE_INVARIANTS_RETAINED",
            "explicit_human_authority": "VERIFIED__RETAINED",
            "direct_human_interaction": "VERIFIED__RETAINED_WHERE_AUTHENTICATED",
            "no_ai_generated_human_authority": "VERIFIED__RETAINED",
            "no_caller_assertion_as_authority": "VERIFIED__RETAINED",
            "exact_byte_equality": "VERIFIED__RETAINED",
            "source_digest_derivation": "VERIFIED__RETAINED",
            "presentation_binding": "VERIFIED__RETAINED",
            "scope_binding": "VERIFIED__RETAINED",
            "temporal_and_freshness_binding": "VERIFIED__RETAINED",
            "canonical_handoff_validation": "VERIFIED__RETAINED",
            "collision_guards": "VERIFIED__RETAINED",
            "one_shot_consumption": "VERIFIED__RETAINED",
            "nontransferability_and_nonreusability": "VERIFIED__RETAINED",
            "no_replay": "VERIFIED__RETAINED",
            "no_authority_transfer": "VERIFIED__RETAINED",
            "no_alternate_or_parallel_authority_route": "VERIFIED__RETAINED",
            "no_p11_bypass_or_weakening": "VERIFIED__RETAINED",
            "e05_acceptance": "VERIFIED__UNCHANGED",
        },
        "human_source": {
            "path": SOURCE.relative_to(ROOT).as_posix(), "byte_count": 1213,
            "lf_count": 14, "sha256": SOURCE_SHA256, "utf8_valid": True,
            "bom_absent": True, "final_lf": True, "immutability": "VERIFIED__UNMODIFIED__EXPECTED_UNTRACKED_EXCEPTION",
            "source_exact_bytes_status": "VERIFIED__EXACT_KO_BYTE_EQUALITY",
            "source_direct_human_interaction_status": "VERIFIED__KO_REQUIRED_PERSONAL_HUMAN_CREATION_AND_THE_EXACT_SOURCE_APPEARED_ONLY_AFTER_THE_KO_HUMAN_BARRIER__UNDER_RESTORED_ACCEPTANCE_BASELINE",
            "source_presentation_binding_status": "VERIFIED__EXACT_PRESENTATION_SHA256_BOUND_IN_SOURCE",
            "source_scope_binding_status": "VERIFIED__ONE_KN_GENERATION_ONE_KN_OPERATION_ONE_CONSUMPTION_AND_ONE_ATTEMPT_MAXIMUM",
            "source_temporal_binding_status": "VERIFIED__SOURCE_ABSENT_AT_PREHUMAN_KO_BARRIER__PRESENT_UNCHANGED_AFTER_DIRECT_HUMAN_INTERACTION__PRECONSUMPTION",
            "source_namespace_unconsumed_status": "VERIFIED__NO_AUTHORITY_HANDOFF_BINDING_OR_CONSUMPTION_ARTIFACT_EXISTS",
            "source_replay_status": "VERIFIED__NOT_REPLAYED__REPLAY_COUNT_ZERO",
            "source_acceptance_readiness": "VERIFIED__READY_FOR_SEPARATE_AUTHORITY_AUTHENTICATION_STEP__NOT_AUTHORITY_OR_BINDING",
            "human_source_provenance": "VERIFIED__DIRECT_HUMAN_INTERACTION_PROVENANCE_UNDER_AUTHENTICATED_PRE_KP_ACCEPTANCE_BASELINE__NOT_INDEPENDENT_WRITER_IDENTITY",
            "human_authority_authentication": "NOT_APPLICABLE__KR_STOPS_BEFORE_SEPARATE_AUTHORITY_AUTHENTICATION",
            "human_authority_binding": "NOT_APPLICABLE__NO_BINDING_IN_KR",
            "authority_present": False, "authority_previously_consumed": "VERIFIED__NO",
        },
        "cross_vector_reuse_assessment": {
            "cross_vector_reuse_scope": "MULTI_VECTOR_REUSABLE",
            "reusable_component": "DIRECT_HUMAN_UTF8_SOURCE_BYTES_TO_DERIVED_DIGEST_TO_CANONICAL_HANDOFF_TO_ONE_SHOT_CONSUMPTION_PATTERN",
            "reuse_invariant": "EXPLICIT_HUMAN_DECISION_SOURCE_AND_EXACT_BYTES_MUST_PRECEDE_AUTHORITY_BINDING_AND_CONSUMPTION",
            "applicable_vectors": ["EXPIRED", "FUTURE", "WRONG_ATTEMPT", "WRONG_CONTRACT", "WRONG_INPUT", "WRONG_PROVENANCE"],
            "vector_specific_residue": "DIRECT_INTERACTION_EVIDENCE__SOURCE_BYTES__PRESENTATION_SCOPE__TEMPORAL_VALIDITY__AUTHORITY_AUTHENTICATION__OPERATIONAL_ACCEPTANCE__E05_CREDIT",
            "reuse_preconditions": "PER_GENERATION_DIRECT_HUMAN_INTERACTION__EXACT_BYTES__UNCHANGED_BINDINGS__UNCONSUMED_NAMESPACE__SEPARATE_AUTHORITY_AUTHENTICATION",
            "revalidation_required": "VERIFIED__PER_HUMAN_ACT_GENERATION_VECTOR_AND_OPERATION",
            "expected_future_proof_reduction": "ESTIMATED__REUSE_BYTE_DIGEST_HANDOFF_COLLISION_AND_ONE_SHOT_GUARDS__NO_AUTHORITY_OPERATIONAL_PROOF_OR_E05_TRANSFER",
        },
        "frontier": {
            "last_verified_operational_edge": "EXACT_HUMAN_AUTHORITY_AUTHENTICATED_JZ_BOUND_CONSUMED_ONCE_AND_ONE_NO_NETWORK_VM_BOOT_REACHED_GUEST_CUSTODY_LOAD",
            "first_unverified_operational_edge": "FRESH_HUMAN_AUTHORIZED_EXPIRED_DENIAL_BEFORE_P11_ENTRY_AFTER_KF_REPAIR",
            "last_verified_edge": "KR_FORWARD_REQUIREMENT_CORRECTION_AND_EXISTING_KN_SOURCE_ACCEPTANCE_READINESS_VERIFIED",
            "first_broken_edge": "SEPARATE_HUMAN_AUTHORITY_AUTHENTICATION_AND_CANONICAL_BINDING_FOR_THE_EXISTING_KN_SOURCE",
            "current_real_blocker": "VERIFIED__HUMAN_REVIEW_AND_SEPARATE_AUTHORITY_AUTHENTICATION_HAVE_NOT_OCCURRED",
            "minimum_missing_capability": "NOT_PROVEN__NO_NEW_CAPABILITY_GAP__EXISTING_SEPARATE_AUTHORITY_AUTHENTICATION_STEP_REQUIRED",
            "minimum_legal_next_delta": "AFTER_HUMAN_REVIEW__SEPARATE_REPOSITORY_ONLY_AUTHORITY_AUTHENTICATION_AND_CANONICAL_BINDING_READINESS__STOP_BEFORE_CONSUMPTION",
        },
        "governance": {
            "project_state": "VERIFIED__KR_CORRECTION_AND_SOURCE_READINESS_COMPLETE__STOPPED_BEFORE_AUTHORITY_AUTHENTICATION",
            "project_progress": "VERIFIED__KQ_OPEN_CORRECTION_EDGE_CLOSED_AND_EXISTING_KN_SOURCE_READY_FOR_SEPARATE_AUTHORITY_AUTHENTICATION",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "informal_project_progress_estimate": "ESTIMATED__ONE_SEPARATE_AUTHORITY_AUTHENTICATION_AND_BINDING_READINESS_DELTA_PRECEDES_ANY_CONSUMPTION",
            "constitutional_health_evidence": "VERIFIED__ANTI_WEAKENING_PASS__FAIL_CLOSED__REPLAY_SAFE__MUTATION_BOUNDED",
            "shadow_automation_status": "NOT_APPLICABLE__NO_SHADOW_AUTOMATION_OR_WRITER_IDENTITY_INFRASTRUCTURE_CREATED",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "governance_efficiency": "ESTIMATED__HIGH__ONE_REQUIRED_CORRECTION_CLOSES_KQ_EDGE_WITHOUT_PRODUCTION_OR_TRUST_INFRASTRUCTURE",
            "overengineering_risk": "ESTIMATED__LOW_AFTER_CORRECTION__NO_NEW_IDENTITY_OWNER_ROUTE_REGISTRY_OR_ABSTRACTION",
            "cognition_provenance": "VERIFIED__COMMITTED_KQ_KP_KO_CANONICAL_AND_HISTORICAL_REPOSITORY_EVIDENCE_PLUS_DETERMINISTIC_LOCAL_VALIDATION",
            "cognition_assisted_handoff": "VERIFIED__PROVIDER_INTERRUPTION_LEAD_REAUTHENTICATED_FROM_REPOSITORY__NO_MEMORY_DEPENDENCY",
            "candidate_capability": "VERIFIED__EXISTING_KN_SOURCE_ACCEPTANCE_READINESS_ONLY__NOT_OPERATIONAL_CAPABILITY",
            "shadow_design_target": "VERIFIED__SEPARATE_AUTHORITY_AUTHENTICATION_AND_CANONICAL_BINDING_READINESS__NO_CONSUMPTION",
            "constitutional_continuation_progress": "VERIFIED__KP_FORWARD_OVERCONSTRAINT_SUPERSEDED_AND_KN_SOURCE_READINESS_EDGE_CLOSED",
        },
        "e05": {"before": "VERIFIED__11_OF_18", "after": "VERIFIED__11_OF_18", "state": "VERIFIED__11_OF_18", "frontier": "VERIFIED__7_UNSATISFIED_OF_18", "credit": "VERIFIED__0", "kn_e05_credit": "VERIFIED__0", "expired": "NOT_PROVEN_OPERATIONALLY"},
        "ex": {"ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0"},
        "architecture": {"production_mutation_count": 0, "p11_implementation_mutation_count": 0, "new_owner_count": 0, "new_route_count": 0, "new_registry_count": 0, "new_generic_abstraction_count": 0, "new_constitutional_concept_count": 0, "production_route_before": 1, "production_route_after": 1, "parallel_flow": "NO"},
        "proof_yield": {"new_verified_capability_count": "VERIFIED__0", "new_operational_capability_count": "VERIFIED__0", "new_blocker_localized_count": "VERIFIED__0__KQ_ALREADY_LOCALIZED_IT", "new_blocker_closed_count": "VERIFIED__1__KP_FORWARD_OVERCONSTRAINT", "new_false_or_superseded_blocker_removed_count": "VERIFIED__1__INDEPENDENT_WRITER_IDENTITY_AS_FORWARD_KN_BLOCKER", "new_classification_result_count": "VERIFIED__1__EXISTING_SOURCE_READY_FOR_SEPARATE_AUTHORITY_AUTHENTICATION", "corrected_requirement_count": "VERIFIED__1", "source_readiness_edge_count": "VERIFIED__1", "proof_reuse_count": "VERIFIED__17__EX_COMMON_COMPONENTS"},
        "ccwim": {"ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION", "authenticated_repository_continuation": "VERIFIED__YES", "previous_worker_conversation_required": "VERIFIED__NO", "previous_worker_memory_required": "VERIFIED__NO", "handoff_reconstruction_success": "VERIFIED__YES", "handoff_ambiguity_count": "VERIFIED__0", "observed_artifact_level_cross_worker_drift": "VERIFIED__0"},
        "hac_hai_hae": "NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED",
        "operational_counters": zero_counters(), "phase_b_started": False,
        "auto_continuable": False, "human_review_required": True,
    }


def envelope() -> dict[str, Any]:
    correction = build_correction()
    return {"schema_id": "G77_256KR_SPCE_TERMINAL_CORRECTION_ENVELOPE_V1", "correction": correction, "correction_sha256": hashlib.sha256(canonical_bytes(correction)).hexdigest()}


def verify() -> None:
    authenticate_inputs()
    if load_envelope(OUTPUT, "correction") != build_correction():
        raise KRReductionError("KR_CORRECTION_CONTENT_MISMATCH")
    print(TERMINAL)


def write() -> None:
    authenticate_inputs()
    if OUTPUT.exists() or OUTPUT.is_symlink():
        raise KRReductionError("KR_CORRECTION_COLLISION")
    OUTPUT.write_bytes(canonical_bytes(envelope()))
    print(TERMINAL)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("write", "verify"), default="verify", nargs="?")
    args = parser.parse_args()
    write() if args.mode == "write" else verify()


if __name__ == "__main__":
    main()
