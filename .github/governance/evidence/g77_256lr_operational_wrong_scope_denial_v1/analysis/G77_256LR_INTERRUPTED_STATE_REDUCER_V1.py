#!/usr/bin/env python3
"""Seal the read-only reconstruction of LR's already-started one-shot attempt."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
LR = ROOT / (
    ".github/governance/evidence/g77_256lr_operational_wrong_scope_denial_v1"
)
LQ = ROOT / (
    ".github/governance/evidence/"
    "g77_256lq_wrong_scope_fresh_phase_a_review_object_v1"
)
RECONSTRUCTION = LR / "G77_256LR_INTERRUPTED_STATE_RECONSTRUCTION_V1.json"
REDUCTION = LR / "G77_256LR_SPCE_TERMINAL_INCOMPLETE_OPERATION_V1.json"
SERIAL_COPY = LR / "G77_256LR_INTERRUPTED_SERIAL_LOG_V1.log"
SERIAL_SOURCE = Path(
    "/tmp/g77_256lq_wrong_scope_fresh_phase_a_review_object_v1/serial.log"
)
PRE_RECEIPT = LQ / (
    "operation_state/receipts/"
    "G77_256LQ_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
)
POST_RECEIPT = LQ / (
    "operation_state/receipts/"
    "G77_256LQ_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
)
RUNTIME = LQ / "operation_state/runtime_export"

R_HEAD = "010aaf1b4f8ae14141d8f65ea9109dfcf5ffac83"
R_TREE = "892f0c35419dc6fd90f1fbd9d753b0aa0778730e"
C_HEAD = "ef944daef992055583c2b18c6d7696e472efd09d"
C_TREE = "f14a9312f89ea7accdf24fa8a35a87754802fb17"
OBJECT_ID = "G77_256LQ_WRONG_SCOPE_PHASE_A_REVIEW_OBJECT_001"
OBJECT_SHA256 = "035e406848463173bd68b6cf1ec810cdfa7ab846ce02b26cf376c7d81a77eecb"
AUTHORIZED_SCOPE = "P11_DA_ONE_BOUNDED_OPERATIONAL_ATTEMPT_V1"
PRESENTED_SCOPE = "P11_DA_DIFFERENT_OPERATIONAL_SCOPE_V1"
AUTHORITY_ID = "G77_256LR_FRESH_HUMAN_OPERATIONAL_AUTHORITY_001"
AUTHORITY_SHA256 = "7b5cdc5aa1bcf253bb19d6e5ec732a490f60cd72e37409938d081ebcf03c901f"
TRANSITION_SHA256 = "3ad7d1edcb568693d6510804f03686221d1ce2a1c04be9cc722184a6c7e69911"
SERIAL_SHA256 = "72c46b41a40d6b00ffd4a1fccdfc67ae5b4584dfe0bf2bc924aec0f2251c5998"
SERIAL_SIZE = 43692
TERMINAL = (
    "A__G77_256LR_EXISTING_OPERATION_ALREADY_OCCURRED__"
    "OUTCOME_RECONSTRUCTED_INCOMPLETE__NO_RETRY__STOP"
)

INPUT_HASHES = {
    "G77_256LR_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt": "8f1b01dbdfbe4826951b5e41ab57a2a55cb041abe38d5aff870072ce0c460206",
    "G77_256LR_LP_COMMITTED_REVIEW_TRANSITION_V1.json": "0d2417607fa6988e8be53c094bf816374aedfa8c8f6c6ce71c3d3bfc7b58a495",
    "G77_256LR_PREAUTHORITY_ENTRY_AND_DECISION_BINDING_V1.json": "c72c9b8b5e3730b094a30743caace2decea99ddede51a7f77a640ad96cbd43a1",
    "G77_256LR_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json": AUTHORITY_SHA256,
    "G77_256LR_PRECONSUMPTION_INVOCATION_BINDING_V1.json": "80a54e4dc39936ebea042cfbc8a1c354c26c94c39a96e3184b2a19216c16742d",
    "G77_256LR_PRECONSUMPTION_READINESS_CHECKPOINT_V1.json": "17f69c518f1e8fa5670f7dd0f08fbc0e34a3e638223c46c9a3ae828ce6dbede1",
    "G77_256LR_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json": "0b66e13296c283685bbc08e2234af439a6992de4495b013ec3631c99ed545f6b",
    "G77_256LR_FM_OPERATIONAL_INVOCATION_ATTEMPT_V1.json": "ce639b9146204ea89da4c767eb25c8fc330dc01a14168278b250cc8159d4b258",
    "orchestration/G77_256LR_ONE_SHOT_CONTROLLER_V1.py": "89a7ebf2f6d7972e6899956b947c20a1614db2c9d53e5d3ac97816929a31b1b0",
}
PRE_RECEIPT_SHA256 = "b8da75b9ad19fce7f355fc07f18fc45a1fec10f9941bd52cf2539284e28d41ac"


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise RuntimeError(f"NONCANONICAL_JSON:{path.name}")
    return value


def inner(path: Path, field: str) -> dict[str, Any]:
    envelope = load_canonical(path)
    value = envelope.get(field)
    if (
        not isinstance(value, dict)
        or envelope.get(f"{field}_sha256")
        != hashlib.sha256(canonical_bytes(value)).hexdigest()
    ):
        raise RuntimeError(f"SEAL_MISMATCH:{path.name}")
    return value


def envelope(schema: str, field: str, value: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": schema,
        field: value,
        f"{field}_sha256": hashlib.sha256(canonical_bytes(value)).hexdigest(),
    }


def now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def active_related_processes() -> list[dict[str, str]]:
    output = subprocess.check_output(
        ["ps", "-eo", "pid=,ppid=,stat=,comm=,args="], text=True
    )
    matches: list[dict[str, str]] = []
    for line in output.splitlines():
        fields = line.strip().split(None, 4)
        if len(fields) != 5:
            continue
        pid, ppid, state, command, arguments = fields
        if command.startswith("qemu") or (
            command in {"python", "python3"}
            and "G77_256LR_ONE_SHOT_CONTROLLER_V1.py" in arguments
        ):
            matches.append(
                {
                    "pid": pid,
                    "ppid": ppid,
                    "state": state,
                    "command": command,
                    "arguments": arguments,
                }
            )
    return matches


def authenticate_inputs() -> dict[str, Any]:
    for relative, expected in INPUT_HASHES.items():
        path = LR / relative
        if path.is_symlink() or not path.is_file() or sha256_path(path) != expected:
            raise RuntimeError(f"LR_DURABLE_INPUT_MISMATCH:{relative}")
    if sha256_path(PRE_RECEIPT) != PRE_RECEIPT_SHA256:
        raise RuntimeError("FM_PRE_RECEIPT_MISMATCH")
    if (
        POST_RECEIPT.exists()
        or (LR / "G77_256LR_FM_OPERATIONAL_INVOCATION_RESULT_V1.json").exists()
        or (RUNTIME / "G77_256LQ_RAW_EXECUTION_EVIDENCE_V1.jsonl").exists()
        or (RUNTIME / "G77_256LQ_GUEST_EXECUTION_SEAL_V1.json").exists()
        or (RUNTIME / "G77_256LQ_GUEST_TEARDOWN_SEAL_V1.json").exists()
        or (RUNTIME / "G77_256LQ_CONTINUATION_MANIFEST_TERMINAL_V1.json").exists()
    ):
        raise RuntimeError("RECOVERY_ABSENCE_SET_CHANGED")
    if (
        SERIAL_SOURCE.is_symlink()
        or not SERIAL_SOURCE.is_file()
        or SERIAL_SOURCE.stat().st_size != SERIAL_SIZE
        or sha256_path(SERIAL_SOURCE) != SERIAL_SHA256
    ):
        raise RuntimeError("INTERRUPTED_SERIAL_OBSERVATION_MISMATCH")
    if active_related_processes():
        raise RuntimeError("RELATED_OPERATIONAL_PROCESS_STILL_ACTIVE")

    handoff = inner(
        LR / "G77_256LR_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json",
        "authorization",
    )
    preauth = inner(
        LR / "G77_256LR_PREAUTHORITY_ENTRY_AND_DECISION_BINDING_V1.json",
        "checkpoint",
    )
    preconsumption = inner(
        LR / "G77_256LR_PRECONSUMPTION_READINESS_CHECKPOINT_V1.json",
        "checkpoint",
    )
    consumption = inner(
        LR / "G77_256LR_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json",
        "checkpoint",
    )
    attempt = inner(
        LR / "G77_256LR_FM_OPERATIONAL_INVOCATION_ATTEMPT_V1.json",
        "attempt",
    )
    receipt = load_canonical(PRE_RECEIPT)
    if (
        handoff.get("authorization_source_sha256") != INPUT_HASHES[
            "G77_256LR_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
        ]
        or handoff.get("authorized_repository_head") != C_HEAD
        or handoff.get("authorized_repository_tree") != C_TREE
        or handoff.get("authorized_vector") != "WRONG_SCOPE"
        or handoff.get("wrong_scope_operational_attempt_limit") != 1
        or handoff.get("retry_limit") != 0
        or handoff.get("repair_limit") != 0
        or handoff.get("replay_limit") != 0
        or handoff.get("authorization_reusable") is not False
        or preauth.get("authority_created_count") != 0
        or preauth.get("operation_attempt_count") != 0
        or preconsumption.get("authority_id") != AUTHORITY_ID
        or preconsumption.get("authority_state") != "GRANTED_UNCONSUMED"
        or preconsumption.get("operational_counters", {}).get("authority_creation_count") != 1
        or preconsumption.get("operational_counters", {}).get("authority_consumption_count") != 0
        or preconsumption.get("operational_counters", {}).get("operation_attempt_count") != 0
        or consumption.get("authority_state_before") != "GRANTED_UNCONSUMED"
        or consumption.get("authority_state_after") != "CONSUMED"
        or consumption.get("authority_reusable") is not False
        or consumption.get("authority_survives") is not False
        or consumption.get("operational_counters", {}).get("authority_consumption_count") != 1
        or attempt.get("authority_state") != "CONSUMED"
        or attempt.get("invocation_count") != 1
        or attempt.get("operational_counters", {}).get("operation_attempt_count") != 1
        or attempt.get("operational_counters", {}).get("qemu_start_count") != 1
        or attempt.get("operational_counters", {}).get("vm_start_count") != 1
        or attempt.get("retry_count") != 0
        or attempt.get("repair_retry_count") != 0
        or attempt.get("replay_count") != 0
        or receipt.get("execution_attempt_count") != 1
        or receipt.get("execution_authority_file_sha256") != AUTHORITY_SHA256
        or receipt.get("committed_review_transition_sha256") != TRANSITION_SHA256
        or receipt.get("completed_unix_ns") is not None
        or receipt.get("process_exit_status") is not None
        or receipt.get("automatic_retry_count") != 0
    ):
        raise RuntimeError("LR_CARDINALITY_OR_BINDING_RECONSTRUCTION_CONFLICT")
    return {
        "handoff": handoff,
        "preauth": preauth,
        "preconsumption": preconsumption,
        "consumption": consumption,
        "attempt": attempt,
        "receipt": receipt,
    }


def build_reconstruction(serial_copy_sha256: str) -> dict[str, Any]:
    values = authenticate_inputs()
    return {
        "schema_id": "G77_256LR_INTERRUPTED_STATE_RECONSTRUCTION_V1",
        "terminal": TERMINAL,
        "reconstruction_observed_at_utc": now(),
        "recovery_state_class": "STATE_B__AUTHORITY_ALREADY_CONSUMED__EXACTLY_ONE_OPERATION_ALREADY_STARTED__OUTCOME_INCOMPLETE",
        "last_reported_state": "AUTHORITY_CREATED_1__AUTHORITY_CONSUMED_0__OPERATION_ATTEMPT_0",
        "durably_reconstructed_state": "AUTHORITY_CREATED_1__AUTHORITY_CONSUMED_1__OPERATION_ATTEMPT_1__PRE_RECEIPT_1__POST_RECEIPT_0__NO_ACTIVE_PROCESS__NO_TERMINAL_OPERATION_EVIDENCE",
        "repository": {
            "head": C_HEAD,
            "tree": C_TREE,
            "branch": "g77-256fl-wrong-attempt-preboot-blocker",
            "lr_commit_count": 0,
            "worktree_scope": "ONLY_AUTHORIZED_LR_AND_ONE_LQ_FM_PRE_RECEIPT_UNTRACKED",
        },
        "human_decision": {
            "object_id": OBJECT_ID,
            "object_sha256": OBJECT_SHA256,
            "authorized_scope": AUTHORIZED_SCOPE,
            "presented_scope": PRESENTED_SCOPE,
            "source_present": True,
            "source_sha256": INPUT_HASHES[
                "G77_256LR_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
            ],
        },
        "authority": {
            "id": AUTHORITY_ID,
            "sha256": AUTHORITY_SHA256,
            "created_count": 1,
            "consumed_count": 1,
            "current_state": "CONSUMED__TERMINAL_NONREUSABLE",
            "reusable": False,
            "terminated": True,
        },
        "receipts": {
            "consumption_receipt_present": True,
            "consumption_receipt_id": "G77_256LR_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1",
            "consumption_receipt_sha256": INPUT_HASHES[
                "G77_256LR_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json"
            ],
            "operational_pre_receipt_present": True,
            "operational_pre_receipt_id": "SAPIANTA_CONTEXT_BOUND_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1",
            "operational_pre_receipt_sha256": PRE_RECEIPT_SHA256,
            "operational_post_receipt_present": False,
            "operational_post_receipt_sha256": "ABSENT",
        },
        "operation": {
            "attempt_count": 1,
            "retry_count": 0,
            "qemu_start_count": 1,
            "vm_start_count": 1,
            "qemu_process_state": "ABSENT_AT_RECONSTRUCTION",
            "vm_process_state": "ABSENT_AT_RECONSTRUCTION",
            "controller_process_state": "ABSENT_AT_RECONSTRUCTION",
            "result": "INCOMPLETE__NO_POST_RECEIPT_NO_CONTROLLER_RESULT_NO_GUEST_TERMINAL",
            "wrong_scope_denial_evidence_present": False,
            "denial_class": "UNKNOWN",
            "denial_edge": "UNKNOWN",
            "p11_entry_count": "UNKNOWN__NO_GUEST_TERMINAL_EVIDENCE",
            "protected_invocation_count": "UNKNOWN__NO_GUEST_TERMINAL_EVIDENCE",
            "protected_effect_count": "UNKNOWN__NO_GUEST_TERMINAL_EVIDENCE",
            "operation_terminal_evidence_present": False,
        },
        "runtime_observation": {
            "serial_source_sha256": SERIAL_SHA256,
            "serial_copy_sha256": serial_copy_sha256,
            "serial_byte_count": SERIAL_SIZE,
            "serial_state": "VM_BOOT_OUTPUT_PRESENT__NO_GUEST_GOVERNANCE_OUTPUT_PRESENT",
            "pre_receipt_started_unix_ns": values["receipt"]["started_unix_ns"],
        },
        "transition": {
            "review_identity_r": f"{R_HEAD}/{R_TREE}",
            "current_admission_identity_c": f"{C_HEAD}/{C_TREE}",
            "transition_sha256": TRANSITION_SHA256,
            "is_authority": False,
            "consumable": False,
        },
        "cardinality": {
            "human_decision_count": 1,
            "authority_created_count": 1,
            "authority_consumed_count": 1,
            "operation_attempt_count": 1,
            "retry_count": 0,
            "constitutional_cardinality_conflict": False,
        },
        "e05": {
            "before": "12/18",
            "lr_credit": 0,
            "after": "12/18",
            "wrong_scope": "UNSAT__OPERATIONAL_PROOF_INCOMPLETE",
        },
    }


def build_reduction(reconstruction_sha256: str) -> dict[str, Any]:
    return {
        "schema_id": "G77_256LR_SPCE_TERMINAL_INCOMPLETE_OPERATION_V1",
        "terminal": TERMINAL,
        "result_class": "ONE_SHOT_OPERATIONAL_OBSERVATION_INCOMPLETE__NO_RETRY",
        "recovery_state_class": "STATE_B",
        "reconstruction_file_sha256": reconstruction_sha256,
        "spce": {
            "state": "ONE_AUTHORITY_CONSUMED__ONE_OPERATION_STARTED__TERMINAL_RESULT_MISSING",
            "problem": "POST_RECEIPT_CONTROLLER_RESULT_AND_GUEST_TERMINAL_EVIDENCE_ABSENT",
            "constraints": "NO_SECOND_AUTHORITY__NO_SECOND_CONSUMPTION__NO_SECOND_ATTEMPT__NO_RETRY",
            "execution": "READ_ONLY_RECONSTRUCTION__FAILURE_SEAL__COMMIT_PUSH__STOP",
        },
        "failure_novelty_and_convergence_check": {
            "failure_class": "PROOF_GAP",
            "novelty": "NO_NEW_SEMANTIC_EDGE__ONE_SHOT_OPERATIONAL_TERMINAL_OBSERVATION_INCOMPLETE",
            "affected_invariant": "ONE_HUMAN_DECISION__ONE_AUTHORITY__AT_MOST_ONE_OPERATIONAL_ATTEMPT__NO_RETRY",
            "previous_closest_edge": "LR_AUTHORITY_CREATED_UNCONSUMED__FINAL_FM_ADMISSION_PASS__OPERATION_COUNT_ZERO",
            "semantic_difference": "AUTHORITY_NOW_CONSUMED_AND_ONE_OPERATION_STARTED_WITHOUT_TERMINAL_OBSERVATION",
            "production_behavior_impact": "NONE_PROVEN__NO_PRODUCTION_MUTATION",
            "new_capability_required": "NO",
            "new_proof_required": "YES__FUTURE_SEPARATELY_AUTHORIZED_COMPLETE_OPERATIONAL_WRONG_SCOPE_OBSERVATION",
            "convergence_signal": "LR_CROSSED_LN_AND_LQ_STATIC_BLOCKERS_BUT_DID_NOT_PRODUCE_TERMINAL_OPERATIONAL_PROOF",
            "repetition_pressure": "INCREASED__CURRENT_ONE_SHOT_LIFECYCLE_EXHAUSTED_WITHOUT_E05_CREDIT",
            "verification_amplification_risk": "HIGH__ANY_LR_REINVOCATION_WOULD_BE_FORBIDDEN_RETRY",
        },
        "cross_vector_reuse_assessment": {
            "reused": "FM_AUTHORITY_ADMISSION_ONE_SHOT_RECEIPTS__LP_R_C_TRANSITION__LJ_STABLE_CHECKOUT__GN_PRESENTATION__ER_P11_ROUTE__LG_AUTHORITY_SCOPE__EX_17_OF_17",
            "vectors": "WRONG_ATTEMPT__WRONG_INPUT__WRONG_CONTRACT__WRONG_PROVENANCE__WRONG_CALLER__FUTURE__EXPIRED",
            "lineage": "LI__LJ__LK__LL__LM__LN__LO__LP__LQ",
            "authority_transfer": False,
            "proof_transfer": False,
            "e05_credit_transfer": False,
        },
        "frontier": {
            "last_verified_edge": "EXACT_AUTHORITY_CONSUMED_ONCE__EXACT_FM_PRE_RECEIPT_FOR_R_TO_C_BOUND_ATTEMPT",
            "first_broken_edge": "TERMINAL_OPERATION_RESULT_OBSERVATION_AFTER_FM_PRE_RECEIPT",
            "first_unverified_edge": "WRONG_SCOPE_DENIAL_BEFORE_P11_WITH_ZERO_PROTECTED_EFFECT",
            "minimum_missing_capability": "NONE_PROVEN",
            "minimum_missing_proof": "COMPLETE_OPERATIONAL_WRONG_SCOPE_DENIAL_OBSERVATION",
            "minimum_legal_next_delta": "STOP_FOR_INDEPENDENT_HUMAN_AUTHENTICATION__NO_LR_RETRY",
        },
        "governance": {
            "project_state": "LR_STATE_B_ONE_SHOT_OPERATION_STARTED__OUTCOME_INCOMPLETE__NO_RETRY",
            "informal_project_progress": "STATIC_AND_AUTHORITY_BINDING_GAPS_CLOSED__WRONG_SCOPE_OPERATIONAL_PROOF_REMAINS_UNSAT",
            "constitutional_health_evidence": "CARDINALITY_PRESERVED__ONE_AUTHORITY__ONE_ATTEMPT__ZERO_RETRY__UNKNOWN_OUTCOME_FAILS_CLOSED",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "ONE_FUTURE_SEPARATELY_HUMAN_AUTHORIZED_COMPLETE_WRONG_SCOPE_OPERATIONAL_PROOF",
            "governance_efficiency": "HIGH__DURABLE_EVIDENCE_REUSED__NO_REPLAY_OR_PRODUCTION_MUTATION",
            "overengineering_risk": "HIGH_IF_LR_IS_RETRIED_OR_RECOVERY_FRAMEWORK_IS_GENERALIZED",
            "cognition_provenance": "EXACT_REPOSITORY_STATE__SEALED_DURABLE_LR_ARTIFACTS__FM_PRE_RECEIPT__PRESERVED_SERIAL_BYTES__READ_ONLY_PROCESS_OBSERVATION__MODEL_CLASSIFICATION",
            "cognition_assisted_handoff": "DURABLE_RECONSTRUCTION_ONLY__NO_AUTHORITY_PROOF_OR_E05_TRANSFER",
            "candidate_capability": "NONE_NEW__EXISTING_WRONG_SCOPE_ROUTE_ATTEMPTED_ONCE",
            "shadow_design_target": "HUMAN_DECISION_REJECTION_AND_REAUTHORIZATION_LIFECYCLE__HUMAN_REJECTION_FINALITY__IMPLEMENT_NOW_NO",
            "constitutional_continuation_progress": "LQ_HUMAN_BOUNDARY_TO_LR_AUTHORITY_CONSUMPTION_AND_FM_PRE_RECEIPT",
            "hac_hai_hae": "NOT_USED__AUTHENTICATED_DEFINITIONS_NOT_PROVEN",
        },
        "forward_compatibility": {
            "AMBIGUOUS": "UNCHANGED",
            "STALE": "UNCHANGED",
            "REVOKED": "UNCHANGED",
            "SUPERSEDED": "UNCHANGED",
            "COHERENT_COPY": "UNCHANGED",
            "WRONG_SCOPE": "UNCHANGED__OPERATIONAL_UNSAT",
        },
        "architecture": {
            "production_semantic_mutation": 0,
            "fm_mutation": 0,
            "gn_mutation": 0,
            "er_mutation": 0,
            "p11_mutation": 0,
            "ex_semantic_mutation": 0,
            "owner_delta": 0,
            "route_delta": 0,
            "registry_delta": 0,
            "constitutional_concept_delta": 0,
            "route_count_before": 1,
            "route_count_after": 1,
            "authority_created_additional_during_recovery": 0,
            "operation_attempt_additional_during_recovery": 0,
        },
        "proof_yield": {
            "authority_spent": 1,
            "operation_attempt_spent": 1,
            "terminal_operational_observation": 0,
            "e05_credit": 0,
            "ex_reused": "VERIFIED__17_OF_17",
            "ex_reconstructed": "VERIFIED__0",
        },
        "reuse_impact_assessment": {
            "existing_certified_capabilities_reused": "FM__LP__LJ__GN__GL__ER__P11__LG__EX",
            "new_capabilities": "NONE",
            "existing_capability_became_unreachable": False,
            "parallel_flow_created": False,
            "production_path_count_effect": "UNCHANGED__1_TO_1",
        },
        "ccwim": {
            "recovery_state_authenticated": "STATE_B",
            "last_reported_state_distinguished": True,
            "durable_state_reconstructed": True,
            "operational_state_complete": False,
            "authority_created_count": 1,
            "authority_consumed_count": 1,
            "operation_attempt_count": 1,
            "retry_count": 0,
            "second_authority_count": 0,
            "second_operation_count": 0,
            "unrelated_mutation_count": 0,
        },
        "ex": {
            "ex_reused": "VERIFIED__17_OF_17",
            "ex_reconstructed": "VERIFIED__0",
        },
        "terminality": {
            "authority_reusable": False,
            "lr_retry_allowed": False,
            "successor_generation_created": False,
            "auto_continuable": False,
            "human_review_required": True,
        },
    }


def materialize() -> None:
    if any(path.exists() or path.is_symlink() for path in (SERIAL_COPY, RECONSTRUCTION, REDUCTION)):
        raise RuntimeError("RECOVERY_TERMINAL_ARTIFACT_COLLISION")
    authenticate_inputs()
    SERIAL_COPY.write_bytes(SERIAL_SOURCE.read_bytes())
    serial_copy_sha256 = sha256_path(SERIAL_COPY)
    reconstruction = envelope(
        "G77_256LR_INTERRUPTED_STATE_RECONSTRUCTION_ENVELOPE_V1",
        "reconstruction",
        build_reconstruction(serial_copy_sha256),
    )
    RECONSTRUCTION.write_bytes(canonical_bytes(reconstruction))
    reduction = envelope(
        "G77_256LR_SPCE_TERMINAL_INCOMPLETE_OPERATION_ENVELOPE_V1",
        "reduction",
        build_reduction(sha256_path(RECONSTRUCTION)),
    )
    REDUCTION.write_bytes(canonical_bytes(reduction))
    print(TERMINAL)


def verify() -> None:
    authenticate_inputs()
    if (
        sha256_path(SERIAL_COPY) != SERIAL_SHA256
        or SERIAL_COPY.read_bytes() != SERIAL_SOURCE.read_bytes()
    ):
        raise RuntimeError("PRESERVED_SERIAL_LOG_MISMATCH")
    reconstruction = inner(RECONSTRUCTION, "reconstruction")
    reduction = inner(REDUCTION, "reduction")
    if (
        reconstruction.get("terminal") != TERMINAL
        or reconstruction.get("recovery_state_class", "").split("__", 1)[0]
        != "STATE_B"
        or reconstruction.get("authority", {}).get("created_count") != 1
        or reconstruction.get("authority", {}).get("consumed_count") != 1
        or reconstruction.get("operation", {}).get("attempt_count") != 1
        or reconstruction.get("operation", {}).get("retry_count") != 0
        or reconstruction.get("operation", {}).get("operation_terminal_evidence_present")
        is not False
        or reduction != build_reduction(sha256_path(RECONSTRUCTION))
    ):
        raise RuntimeError("RECOVERY_TERMINAL_REDUCTION_MISMATCH")
    print(TERMINAL)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("materialize", "verify"))
    arguments = parser.parse_args()
    materialize() if arguments.mode == "materialize" else verify()


if __name__ == "__main__":
    main()
