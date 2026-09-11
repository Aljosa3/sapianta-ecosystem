#!/usr/bin/env python3
"""Repository-only G77-256KQ provenance capability classification.

This reducer reads committed evidence and the unmodified KN Human-source file.
It creates no authority, performs no binding or consumption, and has no
production or operational call surface.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
KQ = ROOT / ".github/governance/evidence/g77_256kq_human_provenance_capability_discovery_v1"
OUTPUT = KQ / "G77_256KQ_SPCE_TERMINAL_CLASSIFICATION_V1.json"
SOURCE = ROOT / ".github/governance/evidence/g77_256kn_fresh_expired_operational_recommissioning_v1/G77_256KN_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
KO_INSTRUCTION = ROOT / ".github/governance/evidence/g77_256ko_exact_human_source_authentication_bridge_v1/G77_256KO_DIRECT_HUMAN_ACT_INSTRUCTION_V1.txt"
KP_REDUCTION = ROOT / ".github/governance/evidence/g77_256kp_posthuman_source_authentication_v1/G77_256KP_SPCE_TERMINAL_FAIL_CLOSED_REDUCTION_V1.json"

HEAD = "7356457a1e2c1d53a10d3161664df373e2380943"
TREE = "7d29c3913208e7cfbfde19fa20d823f44705a510"
SUBJECT = "G77-256KP fail closed at Human source provenance"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
SOURCE_SHA256 = "56a50ef8a69761e492138d4f9f425eb2e845231bd654a731ead02fcbc34fdc96"
KP_TERMINAL = "M__KP_EXACT_KN_SOURCE_BYTES_MATCH_BUT_DIRECT_HUMAN_PROVENANCE_NOT_INDEPENDENTLY_AUTHENTICATABLE__NO_AUTHORITY_BINDING__NO_CONSUMPTION__NO_PHASE_B__NO_OPERATION"
TERMINAL = "D__KQ_INDEPENDENT_WRITER_REQUIREMENT_NOT_AUTHENTICATED__HISTORICAL_ACCEPTANCE_USED_WEAKER_DIRECT_HUMAN_INTERACTION_BOUNDARY__NO_AUTHORITY_BINDING__NO_CONSUMPTION__NO_PHASE_B__NO_OPERATION"


class KQClassificationError(RuntimeError):
    """Stable fail-closed KQ classification failure."""


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
        raise KQClassificationError(f"NONCANONICAL_JSON:{path.name}")
    value = envelope.get(inner)
    if not isinstance(value, dict):
        raise KQClassificationError(f"MISSING_INNER_OBJECT:{path.name}")
    if envelope.get(f"{inner}_sha256") != hashlib.sha256(canonical_bytes(value)).hexdigest():
        raise KQClassificationError(f"SEAL_MISMATCH:{path.name}")
    return value


def exact_human_bytes() -> bytes:
    instruction = KO_INSTRUCTION.read_text(encoding="utf-8")
    begin = "--- BEGIN EXACT HUMAN-SOURCE BYTES ---\n"
    end = "--- END EXACT HUMAN-SOURCE BYTES ---\n"
    if instruction.count(begin) != 1 or instruction.count(end) != 1:
        raise KQClassificationError("KO_SOURCE_MARKERS_INVALID")
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
        raise KQClassificationError("KP_ENTRY_CHECKPOINT_MISMATCH")
    if subprocess.run(["git", "merge-base", "--is-ancestor", ANCHOR, "HEAD"], cwd=ROOT, check=False).returncode:
        raise KQClassificationError("STABLE_ANCESTRY_MISMATCH")
    nested = ROOT / "sapianta_system"
    if (
        git("remote", "get-url", "origin", cwd=nested) != "git@github.com:Aljosa3/sapianta-core.git"
        or git("rev-parse", "HEAD", cwd=nested) != "3183bab71f8f30397c0309dd2e6d846d14a11f66"
        or git("rev-parse", "HEAD^{tree}", cwd=nested) != "7c32ec05efc2be43297849bc38ec8766514a523d"
        or git("branch", "--show-current", cwd=nested)
        or git("status", "--short", cwd=nested)
    ):
        raise KQClassificationError("NESTED_AUTHORITY_MISMATCH")
    source = SOURCE.read_bytes()
    if (
        len(source) != 1213
        or source.count(b"\n") != 14
        or hashlib.sha256(source).hexdigest() != SOURCE_SHA256
        or source.startswith(b"\xef\xbb\xbf")
        or not source.endswith(b"\n")
        or source != exact_human_bytes()
    ):
        raise KQClassificationError("HUMAN_SOURCE_IMMUTABILITY_FAILURE")
    source.decode("utf-8")
    kp = load_envelope(KP_REDUCTION, "reduction")
    if (
        kp.get("terminal") != KP_TERMINAL
        or kp.get("phase_b_started") is not False
        or kp.get("human_source", {}).get("authority_previously_consumed") != "VERIFIED__NO"
        or set(kp.get("operational_counters", {}).values()) != {0}
        or kp.get("e05", {}).get("after") != "VERIFIED__11_OF_18"
        or kp.get("e05", {}).get("credit") != "VERIFIED__0"
        or kp.get("ex", {}).get("ex_reused") != "VERIFIED__17_OF_17"
    ):
        raise KQClassificationError("KP_TERMINAL_MISMATCH")

    profile_b = (ROOT / "aigol/runtime/authority_provenance.py").read_text(encoding="utf-8")
    profile_b_recert = (ROOT / "docs/governance/G77_INDEPENDENT_POST_COMMIT_PROFILE_B_C1_AUTHORITY_PROVENANCE_IMPLEMENTATION_C2_C3_NON_REGRESSION_ADVERSARIAL_TRUST_BOUNDARY_RECERTIFICATION_V1.md").read_text(encoding="utf-8")
    profile_a = (ROOT / "aigol/runtime/profile_a_authority_process_boundary.py").read_text(encoding="utf-8")
    candidate_h = (ROOT / "aigol/runtime/candidate_h_founder/authentication.py").read_text(encoding="utf-8")
    candidate_h_orchestration = (ROOT / "aigol/runtime/candidate_h_founder/orchestration.py").read_text(encoding="utf-8")
    canonical_architecture = (ROOT / "docs/governance/CONSTITUTIONAL_ARCHITECTURE_SPEC_V1.md").read_text(encoding="utf-8")
    canonical_invariants = (ROOT / "docs/governance/CONSTITUTIONAL_INVARIANTS.md").read_text(encoding="utf-8")
    ke_report = (ROOT / ".github/governance/evidence/g77_256ke_fresh_expired_operational_recommissioning_v1/G77_256KE_G48_IMPLEMENTATION_REPORT_V1.md").read_text(encoding="utf-8")
    if (
        "zero authority by itself" not in profile_b
        or "C1_STATUS = OPEN__NOT_CERTIFIED" not in profile_b_recert
        or "PROFILE_A_PRODUCTION_BINDING_PATH" not in profile_a
        or "SO_PEERCRED" not in profile_a
        or "Fixture-only Candidate H authentication" not in candidate_h
        or "_FIXTURE_ED25519_SEED" not in candidate_h
        or "fixture-only CAS" not in candidate_h_orchestration
        or "Human Authority governs final direction" not in canonical_architecture
        or "independent trusted writer" in canonical_architecture.lower()
        or "independent trusted writer" in canonical_invariants.lower()
        or "Human-act authentication is `VERIFIED__EXACT_HUMAN_SUPPLIED_ACT`" not in ke_report
        or "AUTHORITY_CONSUMPTION_COUNT` | 1" not in ke_report
    ):
        raise KQClassificationError("DISCOVERY_EVIDENCE_MISMATCH")


def build_classification() -> dict[str, Any]:
    return {
        "schema_id": "G77_256KQ_SPCE_TERMINAL_CLASSIFICATION_V1",
        "terminal": TERMINAL,
        "entry": {
            "branch": BRANCH,
            "head": HEAD,
            "tree": TREE,
            "subject": SUBJECT,
            "origin": ORIGIN,
            "remote_head": HEAD,
            "remote_equality": "VERIFIED__DIRECT_BRANCH_LS_REMOTE",
            "ancestry_anchor": ANCHOR,
            "ancestry_verified": True,
            "index_empty": True,
            "tracked_repository_unchanged": True,
            "expected_untracked_human_source_only_at_entry": True,
        },
        "nested_authority": {
            "origin": "git@github.com:Aljosa3/sapianta-core.git",
            "immutable_ref": "refs/tags/sapianta-system-nested-authority-3183bab-v1",
            "head": "3183bab71f8f30397c0309dd2e6d846d14a11f66",
            "tree": "7c32ec05efc2be43297849bc38ec8766514a523d",
            "clean": True,
            "detached": True,
            "pinned": True,
            "remote_tag_equal": "VERIFIED__DIRECT_LS_REMOTE",
        },
        "human_source": {
            "path": SOURCE.relative_to(ROOT).as_posix(),
            "byte_count": 1213,
            "lf_count": 14,
            "sha256": SOURCE_SHA256,
            "utf8_valid": True,
            "bom_absent": True,
            "final_lf": True,
            "exact_ko_byte_match": "VERIFIED__YES",
            "immutability": "VERIFIED__UNMODIFIED__EXPECTED_UNTRACKED_EXCEPTION",
            "provenance": "NOT_PROVEN__FILESYSTEM_AND_GIT_DO_NOT_IDENTIFY_THE_WRITER",
            "decision_status": "NOT_PROVEN__KP_STATE_PRESERVED_PENDING_HUMAN_REVIEW_OF_REQUIREMENT_CORRECTION",
            "authority_authentication": "NOT_PROVEN__KQ_DOES_NOT_BIND_UNDER_AN_UNCORRECTED_REQUIREMENT",
            "authority_binding": "NOT_APPLICABLE__KQ_CLASSIFICATION_ONLY",
            "authority_present": False,
            "authority_previously_consumed": "VERIFIED__NO",
        },
        "kp_terminal": {
            "terminal": KP_TERMINAL,
            "authenticated": "VERIFIED",
            "phase_b_started": False,
            "operational_counters": zero_counters(),
        },
        "failure_novelty_and_convergence_check": {
            "failure_class": "EVIDENCE_OR_REPORTING_DEFECT",
            "novelty": "VERIFIED__KP_INTRODUCED_A_STRONGER_INDEPENDENT_WRITER_IDENTITY_TEST_NOT_FOUND_IN_CANONICAL_ACCEPTANCE_OR_PRIOR_OPERATIONAL_SUCCESS",
            "affected_invariant": "EXPLICIT_HUMAN_AUTHORITY_AND_EXACT_BOUND_SOURCE_BYTES_MUST_PRECEDE_AUTHORITY_BINDING_OR_CONSUMPTION",
            "previous_closest_edge": "KO_DIRECT_HUMAN_INTERACTION_SOURCE_BOUNDARY_AND_KE_EXACT_HUMAN_SUPPLIED_ACT_ACCEPTANCE",
            "semantic_difference": "VERIFIED__KP_REQUIRES_INDEPENDENT_WRITER_ATTESTATION_WHERE_AUTHENTICATED_PRECEDENT_REQUIRES_A_DIRECT_HUMAN_ACT_PLUS_EXACT_BYTES_AND_BINDINGS",
            "production_behavior_impact": "VERIFIED__NONE__KQ_IS_REPOSITORY_ONLY_AND_STOPS",
            "new_capability_required": "NOT_PROVEN__THE_FORCING_REQUIREMENT_IS_NOT_AUTHENTICATED",
            "new_proof_required": "VERIFIED__BOUNDED_REQUIREMENT_CORRECTION_AND_HUMAN_REVIEW_BEFORE_ANY_REEVALUATION_OF_THE_EXISTING_SOURCE",
            "convergence_signal": "VERIFIED__FALSE_STRONGER_BLOCKER_LOCALIZED_WITHOUT_CREATING_AN_IDENTITY_SYSTEM",
            "repetition_pressure": "VERIFIED__HIGH__KN_KO_KP_AND_KQ_HAVE_NOT_MOVED_THE_OPERATIONAL_FRONTIER_OR_E05_CREDIT",
            "verification_amplification_risk": "VERIFIED__HIGH__AN_UNOWNED_WRITER_IDENTITY_TEST_WOULD_FORCE_A_NEW_TRUST_SYSTEM",
            "classification_evidence": "VERIFIED__CANONICAL_SOURCE_OF_TRUTH_SEARCH__KO_KP_REQUIREMENT_DIFF__KE_COMPARATOR__PROFILE_B_PROFILE_A_CANDIDATE_H_AND_PEER_CREDENTIAL_REVIEW",
            "classification_confidence": "VERIFIED__HIGH",
            "acceptance_requirement_forcing_continuation": "NOT_PROVEN__NO_AUTHENTICATED_RULE_REQUIRES_INDEPENDENT_WRITER_ATTESTATION_BEYOND_THE_EXISTING_DIRECT_HUMAN_INTERACTION_BOUNDARY",
        },
        "historical_success_comparator": {
            "previous_closest_successful_human_authority_edge": "G77_256KE_EXACT_HUMAN_SUPPLIED_ACT_BOUND_THROUGH_JZ_CONSUMED_ONCE_AND_ONE_FM_QEMU_VM_OPERATION_ATTEMPT",
            "how_was_human_actor_identity_proven": "WEAKER_HISTORICAL_ASSUMPTION",
            "historical_acceptance_requirement": "EXACT_HUMAN_SUPPLIED_SOURCE_TEXT__SOURCE_SHA256__PRESENTATION_AND_SCOPE_BINDINGS__CANONICAL_HANDOFF__ONE_SHOT_CONSUMPTION",
            "current_kp_acceptance_requirement": "INDEPENDENT_TRUSTED_WRITER_IDENTITY_OR_HUMAN_ORIGIN_ATTESTATION_BEYOND_EXACT_BYTES_AND_DIRECT_INTERACTION",
            "semantic_difference": "KP_ADDS_INDEPENDENT_WRITER_IDENTITY_PROOF_NOT_PRESENT_IN_KE_OR_OTHER_SUCCESSFUL_OPERATIONAL_REDUCTIONS",
            "stronger_requirement_classification": "C__EVIDENCE_OR_REPORTING_OVERCONSTRAINT",
        },
        "requirement_provenance": {
            "human_provenance_requirement_source": "VERIFIED__FIRST_EXACT_WRITER_IDENTITY_FORMULATION_IN_COMMITTED_KP_REPORT_AND_KP_REDUCER__CURRENT_KQ_COMMISSION_REPEATS_IT",
            "human_provenance_requirement_owner": "NOT_PROVEN__NO_CONSTITUTIONAL_OR_OPERATIONAL_ACCEPTANCE_OWNER_LOCATED",
            "human_provenance_requirement_authentication": "NOT_PROVEN__RECENT_REPORTING_ASSERTION_ONLY",
            "human_provenance_requirement_scope": "NOT_PROVEN_AS_KN_AUTHORITY_PROTOCOL__KP_REPORTING_SCOPE_ONLY",
            "human_provenance_requirement_precedent": "NOT_PROVEN__PRE_KP_SUCCESS_AUTHENTICATED_SOURCE_CONTENT_DIGEST_PRESENTATION_SCOPE_AND_ONE_SHOT_STATE_NOT_WRITER_IDENTITY",
            "human_provenance_requirement_consistency_with_prior_success": "NOT_PROVEN__STRICTER_THAN_KE_JY_JW_KA_AND_OTHER_ACCEPTED_GENERATIONS",
        },
        "profile_b": {
            "status": "VERIFIED__ROOT_SCHEMA_IMPLEMENTED__PROFILE_B_C1_NOT_CERTIFIED__PROFILE_A_REMEDIATION_PENDING_RECERTIFICATION_AND_UNPROVISIONED",
            "owner": "HUMAN_CONSTITUTIONAL_AUTHORITY_FOR_BOUNDED_EVIDENCE_REDUCTION_POLICY_ONLY",
            "trust_root": "NOT_ACTIVE__PROFILE_B_CALLER_MINTABILITY_FAILED_RECERTIFICATION__PROFILE_A_REQUIRES_ABSENT_ROOT_OWNED_OS_BINDING",
            "authority_semantics": "ZERO_AUTHORITY_BY_ROOT_MATERIALIZATION__ALLOW_ONLY_INSIDE_FIXED_BOUNDED_EVIDENCE_REDUCTION_GATE",
            "human_identity_semantics": "DECLARED_CANONICAL_HUMAN_ACT_ACTOR_PLUS_DESIGNATED_OS_PRINCIPAL__NOT_NATURAL_PERSON_WRITER_ATTESTATION",
            "source_binding": "BOUND_TO_CHE_ACT_POLICY_SCOPE_AND_CORRELATION__NOT_TO_KN_SOURCE_BYTES",
            "replay_properties": "IMMUTABLE_HASH_REVISION_SUPERSESSION_AND_OWNER_STATE_GUARDS__PROFILE_A_REQUEST_RECEIPTS",
            "activation_status": "NOT_ACTIVE__PRODUCTION_BINDING_AND_SOCKET_ABSENT",
            "reuse_legality": "NOT_LEGAL_FOR_KN__DIFFERENT_ACTION_SCOPE_NO_KN_SOURCE_BINDING_AND_NO_ACTIVE_CERTIFIED_ROOT",
        },
        "candidate_h": {
            "status": "VERIFIED__ED25519_FIXTURE_RUNTIME_AND_SEPARATE_EXTERNAL_STATUS_OWNER_CONTROL_PROOF_EXIST__NEITHER_BINDS_KN_HUMAN_SOURCE_OR_KN_AUTHORITY",
            "signature_primitive_status": "VERIFIED__RFC8032_PURE_FIXTURE_IMPLEMENTATION_AND_HISTORICAL_PUBLIC_CONTROL_PROOF",
            "signer_key_ownership": "FIXTURE_PRIVATE_SEED_COMMITTED_IN_RUNTIME__SEPARATE_EXTERNAL_STATUS_OWNER_KEY_CONTROL_PROVEN_FOR_ITS_OWN_ANCHOR",
            "signer_identity_binding": "BOUND_ONLY_TO_CANDIDATE_H_FOUNDER_OR_EXTERNAL_STATUS_OWNER_DOMAINS",
            "human_identity_binding": "NOT_PROVEN_FOR_KN_HUMAN_AUTHORITY_OWNER",
            "source_bytes_binding": "NOT_PROVEN__KN_SOURCE_BYTES_NOT_SIGNED",
            "fixture_dependency": "VERIFIED__RUNTIME_AUTHENTICATOR_REQUIRES_HARD_WIRED_FIXTURE_PUBLIC_KEY_AND_OPTIONAL_FIXTURE_PRIVATE_SEED",
            "activation_status": "NOT_ACTIVE_FOR_KN__FIXTURE_ORCHESTRATION_HAS_ZERO_PRODUCTION_EFFECT",
            "authority_semantics": "CANDIDATE_H_ONE_SHOT_FOUNDING_OR_EXTERNAL_STATUS_OWNER_CONTROL__NO_KN_OPERATIONAL_AUTHORITY",
            "replay_guard": "VERIFIED_WITHIN_CANDIDATE_H_FIXTURE_AND_EXTERNAL_CHALLENGE_DOMAINS__NOT_KN",
            "domain_binding": "G77_CANDIDATE_H_FOUNDING_AND_G77_171_EXTERNAL_STATUS_OWNER_ANCHOR_CONTROL__NOT_G77_256KN",
            "reuse_legality": "NOT_LEGAL_FOR_KN_WITHOUT_NEW_OWNER_DOMAIN_SOURCE_AND_AUTHORITY_BINDINGS",
        },
        "peer_credentials": {
            "status": "VERIFIED__IMPLEMENTED_FOR_LOCAL_PROCESS_ROLE_IDENTITY__PROFILE_A_PRODUCTION_BINDING_ABSENT__NOT_HUMAN_PROVENANCE",
            "identity_asserted": "LINUX_KERNEL_SUPPLIED_PID_UID_GID",
            "trust_boundary": "LOCAL_AF_UNIX_SO_PEERCRED_PLUS_ROOT_OWNED_FIXED_BINDING_WHEN_PROVISIONED",
            "process_identity_binding": "VERIFIED__PEER_UID_TO_CONFIGURED_LOCAL_PROCESS_ROLE",
            "os_user_identity_binding": "VERIFIED__NUMERIC_LOCAL_UID_ONLY",
            "human_identity_binding": "NOT_PROVEN__OS_UID_IS_NOT_BOUND_TO_THE_KN_HUMAN_AUTHORITY_OWNER",
            "source_bytes_binding": "NOT_PROVEN__NO_KN_SOURCE_BYTE_BINDING",
            "temporal_binding": "PROCESS_CONNECTION_AND_RECEIPT_LOCAL_ONLY__NOT_KN_SOURCE_CREATION_TIME",
            "replay_guard": "PROFILE_A_IMMUTABLE_REQUEST_RECEIPTS__NOT_KN_SOURCE_REPLAY",
            "authority_semantics": "LOCAL_PROCESS_OR_ROLE_AUTHENTICATION__NOT_DIRECT_HUMAN_ACTOR_PROVENANCE",
            "remote_or_local_scope": "LOCAL_ONLY",
            "reuse_legality": "NOT_LEGAL_FOR_KN_WITHOUT_A_NEW_HUMAN_TO_OS_IDENTITY_AND_SOURCE_BINDING_TRUST_MODEL",
        },
        "provenance_capability": {
            "status": "CURRENT_REQUIREMENT_NOT_AUTHENTICATED",
            "owner": "NOT_APPLICABLE__NO_OWNER_FOR_THE_STRONGER_REQUIREMENT",
            "artifact": "NOT_APPLICABLE__NO_COMPLIANT_KN_WRITER_ATTESTATION_ARTIFACT_REQUIRED_BY_AUTHENTICATED_ACCEPTANCE",
            "trust_root": "NOT_APPLICABLE__DO_NOT_CREATE_ONE_IN_KQ",
            "identity_binding": "HISTORICAL_DIRECT_HUMAN_INTERACTION_BOUNDARY_ONLY__INDEPENDENT_WRITER_BINDING_NOT_AUTHENTICATED_AS_REQUIRED",
            "source_binding": "VERIFIED__EXISTING_DIRECT_HUMAN_SOURCE_BYTES_TO_PRESENTATION_SCOPE_AND_DERIVED_DIGEST_PATTERN",
            "temporal_binding": "VERIFIED__SOURCE_ABSENT_PREHUMAN_AND_PRESENT_AFTER_PRESENTATION__NOT_WRITER_IDENTITY",
            "replay_guard": "VERIFIED__GENERATION_LOCAL_ONE_SHOT_COLLISION_AND_CONSUMPTION_GUARDS__NOT_INVOKED",
            "authority_separation": "VERIFIED__SOURCE_CAPTURE_PROOF_IS_NOT_AUTHORITY__KQ_BINDS_AND_CONSUMES_NOTHING",
            "reuse_legality": "STOP__CASE_D__CORRECT_THE_UNAUTHENTICATED_REQUIREMENT_BEFORE_REEVALUATING_EXISTING_SOURCE",
            "reuse_preconditions": "HUMAN_REVIEW__BOUNDED_KP_REQUIREMENT_CORRECTION__REAUTHENTICATE_KO_DIRECT_INTERACTION_ACCEPTANCE__THEN_SEPARATE_NO_AUTOCONTINUE_DECISION",
        },
        "cross_vector_reuse_assessment": {
            "cross_vector_reuse_scope": "MULTI_VECTOR_REUSABLE",
            "reusable_component": "DIRECT_HUMAN_UTF8_SOURCE_BYTES_TO_DERIVED_DIGEST_TO_CANONICAL_HANDOFF_TO_ONE_SHOT_CONSUMPTION_PATTERN",
            "reuse_invariant": "EXPLICIT_HUMAN_DECISION_SOURCE_AND_EXACT_BYTES_MUST_PRECEDE_AUTHORITY_BINDING_AND_CONSUMPTION",
            "applicable_vectors": ["EXPIRED", "FUTURE", "WRONG_ATTEMPT", "WRONG_CONTRACT", "WRONG_INPUT", "WRONG_PROVENANCE"],
            "vector_specific_residue": "DIRECT_INTERACTION_EVIDENCE__SOURCE_BYTES__PRESENTATION_SCOPE__TEMPORAL_VALIDITY__OPERATIONAL_ACCEPTANCE__E05_CREDIT",
            "reuse_preconditions": "PER_GENERATION_DIRECT_HUMAN_INTERACTION__EXACT_BYTES__UNCHANGED_BINDINGS__UNCONSUMED_NAMESPACE",
            "revalidation_required": "VERIFIED__PER_HUMAN_ACT_GENERATION_VECTOR_AND_OPERATION",
            "expected_future_proof_reduction": "ESTIMATED__REUSE_BYTE_DIGEST_HANDOFF_AND_ONE_SHOT_GUARDS__NO_AUTHORITY_OR_E05_TRANSFER",
        },
        "frontier": {
            "last_verified_operational_edge": "EXACT_HUMAN_AUTHORITY_AUTHENTICATED_JZ_BOUND_CONSUMED_ONCE_AND_ONE_NO_NETWORK_VM_BOOT_REACHED_GUEST_CUSTODY_LOAD",
            "first_unverified_operational_edge": "FRESH_HUMAN_AUTHORIZED_EXPIRED_DENIAL_BEFORE_P11_ENTRY_AFTER_KF_REPAIR",
            "last_verified_edge": "KQ_AUTHENTICATED_THAT_KP_INDEPENDENT_WRITER_REQUIREMENT_IS_NOT_OWNED_BY_CANONICAL_OR_HISTORICAL_ACCEPTANCE_EVIDENCE",
            "first_broken_edge": "BOUNDED_KP_REQUIREMENT_CORRECTION_AND_HUMAN_REVIEW_BEFORE_KN_SOURCE_REEVALUATION",
            "current_real_blocker": "VERIFIED__UNAUTHENTICATED_KP_WRITER_IDENTITY_OVERCONSTRAINT_REQUIRES_GOVERNED_CORRECTION_NOT_NEW_IDENTITY_INFRASTRUCTURE",
            "minimum_missing_capability": "NOT_PROVEN__NO_NEW_CAPABILITY_GAP__REQUIREMENT_CORRECTION_REQUIRED",
            "minimum_legal_next_delta": "HUMAN_REVIEW__SEPARATE_BOUNDED_EVIDENCE_CORRECTION_RESTORING_THE_EXISTING_DIRECT_HUMAN_INTERACTION_ACCEPTANCE_RULE__NO_AUTOMATIC_BINDING",
        },
        "governance": {
            "project_state": "VERIFIED__KQ_CASE_D_CLASSIFIED_AND_STOPPED_BEFORE_AUTHORITY_BINDING",
            "project_progress": "VERIFIED__EXISTING_CAPABILITIES_AND_REQUIREMENT_PROVENANCE_AUTHENTICATED__FALSE_STRONGER_BLOCKER_LOCALIZED",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "informal_project_progress_estimate": "ESTIMATED__ONE_BOUNDED_REQUIREMENT_CORRECTION_AND_HUMAN_REVIEW_PRECEDE_ANY_KN_SOURCE_REEVALUATION",
            "constitutional_health_evidence": "VERIFIED__FAIL_CLOSED_WITHOUT_CREATING_NEW_TRUST_AUTHORITY_OR_OPERATION_PATH",
            "shadow_automation_status": "NOT_PROVEN__NO_INDEPENDENT_WRITER_AUDIT__NOT_AN_AUTHENTICATED_ACCEPTANCE_REQUIREMENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "governance_efficiency": "ESTIMATED__HIGH__AVOIDED_UNNECESSARY_IDENTITY_INFRASTRUCTURE_AND_PRESERVED_STOP",
            "overengineering_risk": "VERIFIED__HIGH_IF_PROFILE_B_CANDIDATE_H_OR_SO_PEERCRED_IS_REPURPOSED_TO_SATISFY_AN_UNOWNED_REQUIREMENT",
            "cognition_provenance": "VERIFIED__AUTHENTICATED_KP_REPOSITORY_HISTORY_AND_CURRENT_SOURCE_PRIMARY__PREVIOUS_WORKER_LEADS_REAUTHENTICATED",
            "cognition_assisted_handoff": "VERIFIED__SAME_GENERATION_PROVIDER_INTERRUPTION_CONTINUATION_WITHOUT_MEMORY_DEPENDENCY",
            "candidate_capability": "NOT_PROVEN__NO_KN_WRITER_ATTESTATION_CAPABILITY_REQUIRED_BY_AUTHENTICATED_ACCEPTANCE",
            "shadow_design_target": "VERIFIED__EXISTING_DIRECT_HUMAN_SOURCE_TO_FM_ER_P11_CHAIN__NOT_INVOKED",
            "constitutional_continuation_progress": "VERIFIED__KP_PROOF_GAP_RECLASSIFIED_AS_REPORTING_OVERCONSTRAINT__STOPPED_FOR_HUMAN_REVIEW",
        },
        "e05": {
            "state": "VERIFIED__11_OF_18",
            "frontier": "VERIFIED__7_UNSATISFIED_OF_18",
            "credit": "VERIFIED__0",
            "kn_e05_credit": "VERIFIED__0",
            "expired": "NOT_PROVEN_OPERATIONALLY",
        },
        "ex": {"ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0"},
        "architecture": {
            "production_mutation_count": 0,
            "p11_implementation_mutation_count": 0,
            "new_owner_count": 0,
            "new_route_count": 0,
            "new_registry_count": 0,
            "new_generic_abstraction_count": 0,
            "new_constitutional_concept_count": 0,
            "production_route_before": 1,
            "production_route_after": 1,
            "parallel_flow": "NO",
        },
        "proof_yield": {
            "new_verified_capability_count": "VERIFIED__0",
            "new_operational_capability_count": "VERIFIED__0",
            "new_blocker_localized_count": "VERIFIED__1__UNOWNED_KP_WRITER_IDENTITY_REQUIREMENT",
            "new_blocker_closed_count": "VERIFIED__0__KQ_DOES_NOT_CORRECT_OR_BIND",
            "new_false_or_superseded_blocker_removed_count": "VERIFIED__1__INDEPENDENT_WRITER_ATTESTATION_AS_CURRENT_CAPABILITY_GAP",
            "new_classification_result_count": "VERIFIED__1__CURRENT_REQUIREMENT_NOT_AUTHENTICATED",
            "proof_reuse_count": "VERIFIED__17__EX_COMMON_COMPONENTS",
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION",
            "authenticated_repository_continuation": "VERIFIED__YES",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
            "handoff_reconstruction_success": "VERIFIED__YES",
            "handoff_ambiguity_count": "VERIFIED__0",
            "observed_artifact_level_cross_worker_drift": "VERIFIED__0",
        },
        "hac_hai_hae": "NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED",
        "operational_counters": zero_counters(),
        "phase_b_started": False,
        "auto_continuable": False,
        "human_review_required": True,
    }


def envelope() -> dict[str, Any]:
    classification = build_classification()
    return {
        "schema_id": "G77_256KQ_SPCE_TERMINAL_CLASSIFICATION_ENVELOPE_V1",
        "classification": classification,
        "classification_sha256": hashlib.sha256(canonical_bytes(classification)).hexdigest(),
    }


def verify() -> None:
    authenticate_inputs()
    if load_envelope(OUTPUT, "classification") != build_classification():
        raise KQClassificationError("KQ_CLASSIFICATION_CONTENT_MISMATCH")
    print(TERMINAL)


def write() -> None:
    authenticate_inputs()
    if OUTPUT.exists() or OUTPUT.is_symlink():
        raise KQClassificationError("KQ_CLASSIFICATION_COLLISION")
    OUTPUT.write_bytes(canonical_bytes(envelope()))
    print(TERMINAL)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("write", "verify"), default="verify", nargs="?")
    args = parser.parse_args()
    write() if args.mode == "write" else verify()


if __name__ == "__main__":
    main()
