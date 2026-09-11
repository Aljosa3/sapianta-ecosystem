#!/usr/bin/env python3
"""Seal or verify the KP post-Human source-provenance stop."""

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
KP = ROOT / ".github/governance/evidence/g77_256kp_posthuman_source_authentication_v1"
KO = ROOT / ".github/governance/evidence/g77_256ko_exact_human_source_authentication_bridge_v1"
KN = ROOT / ".github/governance/evidence/g77_256kn_fresh_expired_operational_recommissioning_v1"
SOURCE = KN / "G77_256KN_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
INSTRUCTION = KO / "G77_256KO_DIRECT_HUMAN_ACT_INSTRUCTION_V1.txt"
OUTPUT = KP / "G77_256KP_SPCE_TERMINAL_FAIL_CLOSED_REDUCTION_V1.json"

HEAD = "825f9e2795b2310f027ae5c5d777466d8c9f79ea"
TREE = "9033c5e9714c6305164224bc7015f0a1e5a95664"
SUBJECT = "G77-256KO expose authenticated Human source boundary"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
GENERATION = "G77_256KN_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256KN_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001"
CANDIDATE = "8af5ba1cbf9e396aa2f4f981a6f20b821c5fd1c38e091ed1cb3646c76c953b4a"
DECISION_PRESENTATION = "9b95f4ad710b607b0c8607da4b2b720d5e8bf94929f4f39dc4e121cc5b5f2f12"
SOURCE_SHA256 = "56a50ef8a69761e492138d4f9f425eb2e845231bd654a731ead02fcbc34fdc96"
KO_REDUCTION_SHA256 = "053e97690d55e7f27e139399f4b8e57f6ad3fd72d4fd0fc523bd46c468e0b622"
KO_INSTRUCTION_SHA256 = "7e40a57152cdf590a587506c696c25394373f660ff75aebcaf0bf7d23e4b674b"
KO_TERMINAL = (
    "A__KO_EXISTING_KN_DECISION_OBJECT_READY_FOR_DIRECT_AUTHENTICATED_HUMAN_SOURCE_ACT"
    "__NO_AUTHORITY_CONSUMPTION__NO_PHASE_B"
)
TERMINAL = (
    "M__KP_EXACT_KN_SOURCE_BYTES_MATCH_BUT_DIRECT_HUMAN_PROVENANCE_NOT_INDEPENDENTLY_AUTHENTICATABLE"
    "__NO_AUTHORITY_BINDING__NO_CONSUMPTION__NO_PHASE_B__NO_OPERATION"
)

FORBIDDEN_POSTHUMAN = (
    "G77_256KN_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json",
    "G77_256KN_PRECONSUMPTION_INVOCATION_BINDING_V1.json",
    "G77_256KN_PHASE_B_PRECONSUMPTION_READINESS_CHECKPOINT_V1.json",
    "G77_256KN_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json",
    "G77_256KN_FM_OPERATIONAL_INVOCATION_ATTEMPT_V1.json",
    "G77_256KN_FM_OPERATIONAL_INVOCATION_RESULT_V1.json",
)


class KPProvenanceError(RuntimeError):
    """Deterministic KP source-provenance evidence error."""


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
        raise KPProvenanceError(f"NONCANONICAL_JSON:{path.name}")
    value = envelope.get(inner)
    if not isinstance(value, dict):
        raise KPProvenanceError(f"MISSING_INNER_OBJECT:{path.name}")
    if envelope.get(f"{inner}_sha256") != hashlib.sha256(canonical_bytes(value)).hexdigest():
        raise KPProvenanceError(f"SEAL_MISMATCH:{path.name}")
    return value


def expected_source_bytes() -> bytes:
    instruction = INSTRUCTION.read_bytes()
    begin = b"--- BEGIN EXACT HUMAN-SOURCE BYTES ---\n"
    end = b"--- END EXACT HUMAN-SOURCE BYTES ---\n"
    if instruction.count(begin) != 1 or instruction.count(end) != 1:
        raise KPProvenanceError("KO_SOURCE_MARKER_MISMATCH")
    return instruction.split(begin, 1)[1].split(end, 1)[0]


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


def authenticate_inputs() -> dict[str, Any]:
    if (
        git("branch", "--show-current") != BRANCH
        or git("remote", "get-url", "origin") != ORIGIN
        or git("rev-parse", "HEAD") != HEAD
        or git("rev-parse", "HEAD^{tree}") != TREE
        or git("log", "-1", "--format=%s") != SUBJECT
        or git("diff", "--name-only") != ""
        or git("diff", "--cached", "--name-only") != ""
    ):
        raise KPProvenanceError("ENTRY_CHECKPOINT_MISMATCH")
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", ANCHOR, "HEAD"], cwd=ROOT, check=False
    ).returncode != 0:
        raise KPProvenanceError("STABLE_ANCESTRY_MISMATCH")
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
        raise KPProvenanceError("NESTED_AUTHORITY_MISMATCH")
    allowed_prefix = KP.relative_to(ROOT).as_posix() + "/"
    source_relative = SOURCE.relative_to(ROOT).as_posix()
    untracked = git("ls-files", "--others", "--exclude-standard").splitlines()
    if source_relative not in untracked or any(
        path != source_relative and not path.startswith(allowed_prefix) for path in untracked
    ):
        raise KPProvenanceError("UNEXPLAINED_WORKTREE_MUTATION")
    if SOURCE.is_symlink() or not SOURCE.is_file():
        raise KPProvenanceError("KN_SOURCE_NOT_REGULAR_FILE")
    source = SOURCE.read_bytes()
    expected = expected_source_bytes()
    if (
        len(source) != 1213
        or source.count(b"\n") != 14
        or hashlib.sha256(source).hexdigest() != SOURCE_SHA256
        or source != expected
        or source.startswith(b"\xef\xbb\xbf")
        or not source.endswith(b"\n")
    ):
        raise KPProvenanceError("KN_SOURCE_EXACT_BYTE_MISMATCH")
    try:
        source.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise KPProvenanceError("KN_SOURCE_NOT_UTF8") from exc
    if subprocess.run(
        ["git", "cat-file", "-e", f"{HEAD}:{source_relative}"], cwd=ROOT,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
    ).returncode == 0:
        raise KPProvenanceError("KN_SOURCE_WAS_PRESENT_AT_KO_COMMIT")
    commit_epoch = int(git("show", "-s", "--format=%ct", HEAD))
    if SOURCE.stat().st_mtime_ns // 1_000_000_000 <= commit_epoch:
        raise KPProvenanceError("KN_SOURCE_FRESHNESS_NOT_AFTER_KO_COMMIT")
    if sha256_path(KO / "G77_256KO_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json") != KO_REDUCTION_SHA256:
        raise KPProvenanceError("KO_REDUCTION_FILE_MISMATCH")
    if sha256_path(INSTRUCTION) != KO_INSTRUCTION_SHA256:
        raise KPProvenanceError("KO_INSTRUCTION_FILE_MISMATCH")
    ko = load_envelope(KO / "G77_256KO_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json", "reduction")
    if (
        ko.get("terminal") != KO_TERMINAL
        or ko.get("human_interaction", {}).get("human_authority_present") is not False
        or ko.get("phase_b_started") is not False
        or set(ko.get("operational_counters", {}).values()) != {0}
    ):
        raise KPProvenanceError("KO_TERMINAL_STATE_MISMATCH")
    for name in FORBIDDEN_POSTHUMAN:
        path = KN / name
        if path.exists() or path.is_symlink():
            raise KPProvenanceError(f"POSTHUMAN_COLLISION:{name}")
    return {
        "byte_count": len(source),
        "exact_byte_match": True,
        "final_lf": True,
        "lf_count": source.count(b"\n"),
        "no_bom": True,
        "sha256": hashlib.sha256(source).hexdigest(),
        "source_mtime_epoch": SOURCE.stat().st_mtime_ns // 1_000_000_000,
        "utf8_valid": True,
    }


def build_reduction() -> dict[str, Any]:
    source = authenticate_inputs()
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
            "expected_future_proof_reduction": "ESTIMATED__REUSE_BYTE_VALIDATION_DIGEST_HANDOFF_AND_ONE_SHOT_GUARDS__REAUTHENTICATE_SOURCE_PROVENANCE_PER_ACT__NO_VECTOR_CREDIT",
            "multi_vector_reuse_is_authority_transfer": False,
            "reusable_component": "DIRECT_HUMAN_UTF8_SOURCE_BYTES_TO_DERIVED_DIGEST_TO_CANONICAL_HANDOFF_TO_ONE_SHOT_CONSUMPTION_PATTERN",
            "reuse_invariant": "HUMAN_SOURCE_PROVENANCE_AND_EXACT_BYTES_MUST_PRECEDE_AUTHORITY_BINDING_AND_CONSUMPTION",
            "reuse_preconditions": "INDEPENDENT_SOURCE_ACTOR_PROVENANCE__EXACT_BYTES__PRESENTATION_SCOPE_TEMPORAL_BINDING__UNCONSUMED_NAMESPACE",
            "revalidation_required": "VERIFIED__PER_HUMAN_ACT_GENERATION_VECTOR_AND_OPERATION",
            "vector_specific_residue": "SOURCE_PROVENANCE__PRESENTATION_COORDINATES__TEMPORAL_VALIDITY__OPERATIONAL_ACCEPTANCE__E05_CREDIT",
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
            "tracked_artifacts_unchanged": True,
            "tree": TREE,
        },
        "ex": {"ex_reconstructed": "VERIFIED__0", "ex_reused": "VERIFIED__17_OF_17"},
        "failure_novelty_and_convergence_check": {
            "acceptance_requirement_forcing_continuation": "NOT_APPLICABLE__HUMAN_PROVENANCE_GATE_FAILED_BEFORE_AUTHORITY_BINDING",
            "affected_invariant": "HUMAN_SOURCE_PROVENANCE_AND_EXACT_BYTES_MUST_BE_INDEPENDENTLY_AUTHENTICATED_BEFORE_AUTHORITY_BINDING_OR_CONSUMPTION",
            "classification_confidence": "VERIFIED__HIGH",
            "classification_evidence": "VERIFIED__EXACT_BYTES_AND_FRESHNESS__NOT_PROVEN_WRITER_IDENTITY_OR_AUTOMATION_EXCLUSION__PROMPT_FORBIDS_INFERENCE",
            "convergence_signal": "VERIFIED__BYTE_INTEGRITY_SUBEDGE_CLOSED__PRECISE_SOURCE_ACTOR_PROVENANCE_EDGE_REMAINS",
            "failure_class": "PROOF_GAP",
            "new_capability_required": "NOT_PROVEN",
            "new_proof_required": "VERIFIED__INDEPENDENT_TRUSTED_ATTESTATION_THAT_THE_EXISTING_UNMODIFIED_SOURCE_BYTES_ORIGINATED_FROM_THE_HUMAN",
            "novelty": "VERIFIED__NOT_NEW__EXACT_BYTE_INTEGRITY_CLOSED__SOURCE_ACTOR_PROVENANCE_REMAINS_WITHIN_EXISTING_KN_GAP",
            "previous_closest_edge": "KO_EXISTING_KN_DECISION_OBJECT_READY_FOR_DIRECT_AUTHENTICATED_HUMAN_SOURCE_ACT",
            "production_behavior_impact": "VERIFIED__NONE__STOPPED_BEFORE_HANDOFF_AND_PHASE_B",
            "repetition_pressure": "ESTIMATED__HIGH",
            "semantic_difference": "VERIFIED__SOURCE_BYTES_NOW_PRESENT_EXACT_AND_FRESH__WRITER_IDENTITY_IS_NOT_INDEPENDENTLY_ATTESTED",
            "verification_amplification_risk": "ESTIMATED__HIGH_IF_CORRECT_CONTENT_UNTRACKED_STATUS_OR_CALLER_STATEMENT_IS_RELABELED_AS_PROVENANCE",
        },
        "frontier": {
            "current_real_blocker": "VERIFIED__NO_INDEPENDENT_TRUSTED_WRITER_IDENTITY_OR_HUMAN_ORIGIN_ATTESTATION",
            "first_broken_edge": "INDEPENDENT_HUMAN_SOURCE_ACTOR_PROVENANCE_AUTHENTICATION",
            "first_unverified_operational_edge": "FRESH_HUMAN_AUTHORIZED_EXPIRED_DENIAL_BEFORE_P11_ENTRY_AFTER_KF_REPAIR",
            "last_verified_edge": "EXACT_KN_SOURCE_BYTES_PRESENT_FRESH_PRESENTATION_BOUND_SCOPE_BOUND_AND_UNCONSUMED",
            "last_verified_operational_edge": "EXACT_HUMAN_AUTHORITY_AUTHENTICATED_JZ_BOUND_CONSUMED_ONCE_AND_ONE_NO_NETWORK_VM_BOOT_REACHED_GUEST_CUSTODY_LOAD",
            "minimum_legal_next_delta": "HUMAN_REVIEW__PROVIDE_INDEPENDENT_TRUSTED_PROVENANCE_EVIDENCE_FOR_THE_EXISTING_UNMODIFIED_SOURCE_BYTES__NO_BINDING_UNTIL_VERIFIED",
            "minimum_missing_capability": "NOT_PROVEN__NO_NEW_CAPABILITY_ESTABLISHED__INDEPENDENT_HUMAN_ORIGIN_ATTESTATION_EVIDENCE_REQUIRED",
        },
        "governance": {
            "candidate_capability": "NOT_PROVEN__NO_OPERATIONAL_CAPABILITY__SOURCE_BYTES_ONLY",
            "cognition_assisted_handoff": "VERIFIED__REPOSITORY_ONLY_REPLAY_SAFE_KP_FAIL_CLOSED_REDUCTION",
            "cognition_provenance": "VERIFIED__COMMITTED_KO__UNMODIFIED_SOURCE_BYTES__REPOSITORY_AND_FILESYSTEM_MEASUREMENTS_PRIMARY",
            "constitutional_continuation_progress": "VERIFIED__SOURCE_BYTE_INTEGRITY_CLOSED__SOURCE_ACTOR_PROVENANCE_LOCALIZED",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "constitutional_health_evidence": "VERIFIED__FAIL_CLOSED_AT_PROVENANCE__NO_HANDOFF__NO_CONSUMPTION__ALL_COUNTERS_ZERO",
            "governance_efficiency": "ESTIMATED__HIGH__IRREVERSIBLE_CONSUMPTION_PREVENTED_AT_FIRST_UNPROVEN_EDGE",
            "informal_project_progress_estimate": "ESTIMATED__EXACT_SOURCE_CONTENT_READY__INDEPENDENT_HUMAN_ORIGIN_PROOF_REMAINS",
            "overengineering_risk": "ESTIMATED__HIGH_IF_PROVENANCE_IS_INFERRED_OR_A_NEW_AUTHORITY_PATH_IS_ADDED",
            "project_progress": "VERIFIED__EXACT_SOURCE_BYTES_AND_BINDINGS_AUTHENTICATED__PROVENANCE_FAIL_CLOSED",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "project_state": "VERIFIED__KP_STOPPED_AT_HUMAN_SOURCE_PROVENANCE_BEFORE_AUTHORITY_BINDING",
            "shadow_automation_status": "NOT_PROVEN__NO_INDEPENDENT_WRITER_AUDIT",
            "shadow_design_target": "VERIFIED__SOLE_EXISTING_SOURCE_TO_FM_ER_P11_CHAIN__NOT_INVOKED",
        },
        "hac_hai_hae": "NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED",
        "human_source": {
            "authority_previously_consumed": "VERIFIED__NO",
            "exact_byte_match": "VERIFIED__YES",
            "human_authority_authentication": "NOT_PROVEN__DIRECT_HUMAN_ORIGIN_NOT_INDEPENDENTLY_ATTESTED",
            "human_authority_binding": "NOT_APPLICABLE__PROVENANCE_FAILED_BEFORE_HANDOFF_CONSTRUCTION",
            "human_authority_present": False,
            "human_source_decision_status": "NOT_PROVEN__EXACT_DECISION_BYTES_PRESENT_BUT_HUMAN_ACTOR_PROVENANCE_UNATTESTED",
            "human_source_provenance": "NOT_PROVEN__FILESYSTEM_AND_GIT_DO_NOT_IDENTIFY_THE_WRITER",
            "source_absent_at_ko_prehuman_barrier": "VERIFIED__COMMITTED_TREE_ABSENCE",
            "source_freshness": "VERIFIED__PRESENT_UNTRACKED_AFTER_KO_COMMIT_WITH_EXACT_UNCHANGED_BYTES",
            "source_measurements": source,
            "source_not_written_by_automation": "NOT_PROVEN__NO_INDEPENDENT_WRITER_AUDIT",
            "source_not_written_by_codex": "NOT_PROVEN__NO_REPLAY_SAFE_WRITER_IDENTITY_ATTESTATION",
            "source_not_written_by_ko_assessor": "VERIFIED__ASSESSOR_HAS_NO_SOURCE_WRITE_SURFACE",
            "source_present_after_ko_human_barrier": "VERIFIED__YES",
        },
        "human_review_required": True,
        "operational_counters": zero_counters(),
        "operational_observation": "NOT_APPLICABLE__STOPPED_BEFORE_AUTHORITY_BINDING_AND_PHASE_B",
        "phase_b_started": False,
        "proof_yield": {
            "new_blocker_closed_count": "VERIFIED__1__SOURCE_BYTE_INTEGRITY_AND_FRESHNESS_SUBEDGE",
            "new_blocker_localized_count": "VERIFIED__1__INDEPENDENT_SOURCE_ACTOR_PROVENANCE",
            "new_classification_result_count": "VERIFIED__1__PROOF_GAP_REDUCED_TO_PROVENANCE",
            "new_false_or_superseded_blocker_removed_count": "VERIFIED__0",
            "new_operational_capability_count": "VERIFIED__0",
            "new_verified_capability_count": "VERIFIED__0__BYTE_AUTHENTICATION_IS_NOT_A_PRODUCTION_CAPABILITY",
            "proof_reuse_count": "VERIFIED__17__EX_COMMON_COMPONENTS",
        },
        "schema_id": "G77_256KP_SPCE_TERMINAL_FAIL_CLOSED_REDUCTION_V1",
        "terminal": TERMINAL,
    }


def envelope() -> dict[str, Any]:
    reduction = build_reduction()
    return {
        "schema_id": "G77_256KP_SPCE_TERMINAL_FAIL_CLOSED_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": hashlib.sha256(canonical_bytes(reduction)).hexdigest(),
    }


def materialize() -> None:
    value = envelope()
    if OUTPUT.exists() or OUTPUT.is_symlink():
        raise KPProvenanceError("KP_REDUCTION_COLLISION")
    OUTPUT.write_bytes(canonical_bytes(value))
    print(TERMINAL)


def verify() -> None:
    observed = load_envelope(OUTPUT, "reduction")
    if observed != build_reduction():
        raise KPProvenanceError("KP_REDUCTION_CONTENT_MISMATCH")
    print(TERMINAL)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("materialize", "verify"))
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    materialize() if args.mode == "materialize" else verify()
