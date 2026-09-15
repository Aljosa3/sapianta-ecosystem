#!/usr/bin/env python3
"""Read the one MA/LZ operation and seal acceptance or non-acceptance without relaunch."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
MA = ROOT / ".github/governance/evidence/g77_256ma_operational_wrong_scope_acceptance_v1"
LZ = ROOT / ".github/governance/evidence/g77_256lz_fresh_wrong_scope_phase_a_review_object_v1"
RUNTIME = LZ / "operation_state/runtime_export"
RECEIPTS = LZ / "operation_state/receipts"
CONTEXT = RUNTIME / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
STATE = MA / "operation_state/lt_supervision/G77_256MA_WRONG_SCOPE_OPERATION_001"
PRE = RECEIPTS / "G77_256LZ_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
POST = RECEIPTS / "G77_256LZ_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
RAW = RUNTIME / "G77_256LZ_RAW_EXECUTION_EVIDENCE_V1.jsonl"
GUEST = RUNTIME / "G77_256LZ_GUEST_EXECUTION_SEAL_V1.json"
TEARDOWN = RUNTIME / "G77_256LZ_GUEST_TEARDOWN_SEAL_V1.json"
MANIFEST = RUNTIME / "G77_256LZ_CONTINUATION_MANIFEST_TERMINAL_V1.json"
SERIAL_SOURCE = Path("/tmp/g77_256lz_fresh_wrong_scope_phase_a_review_object_v1/serial.log")
SERIAL = MA / "G77_256MA_SERIAL_CONSOLE_V1.log"
REDUCTION = MA / "G77_256MA_OPERATIONAL_EVIDENCE_REDUCTION_V1.json"
DECISION = MA / "G77_256MA_TERMINAL_DECISION_V1.json"
AUTHORITY = MA / "G77_256MA_FRESH_HUMAN_OPERATIONAL_AUTHORITY_V1.json"
CONSUMPTION = MA / "G77_256MA_AUTHORITY_CONSUMPTION_CHECKPOINT_V1.json"
LY_READINESS = MA / "G77_256MA_LY_LT_PARENT_PREAUTHORITY_READINESS_V1.json"
LY_REOBSERVATION = MA / "G77_256MA_LY_PRECONSUMPTION_REOBSERVATION_V1.json"
LAUNCH_HANDOFF = MA / "G77_256MA_LT_LAUNCH_HANDOFF_V1.json"
AUTHORIZED_SCOPE = "P11_DA_ONE_BOUNDED_OPERATIONAL_ATTEMPT_V1"
PRESENTED_SCOPE = "P11_DA_DIFFERENT_OPERATIONAL_SCOPE_V1"
DENIAL_EDGE = "D2_PRECLAIM_AUTHORITY_BINDING_VALIDATION_BEFORE_PRECLAIM_LEDGER_APPEND_CLAIM_ENTRY_INVOCATION_OR_EFFECT"


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def seal(schema: str, field: str, value: dict[str, Any]) -> dict[str, Any]:
    return {"schema_id": schema, field: value, f"{field}_sha256": digest(value)}


def write_once(path: Path, value: dict[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise RuntimeError(f"TERMINAL_ARTIFACT_COLLISION:{path.name}")
    payload = canonical_bytes(value)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    with temporary.open("xb", buffering=0) as handle:
        handle.write(payload)
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def one(records: list[dict[str, Any]], kind: str) -> dict[str, Any]:
    matches = [record for record in records if record.get("record_type") == kind]
    if len(matches) != 1:
        raise RuntimeError(f"EXPECTED_EXACTLY_ONE:{kind}")
    return matches[0]


def latest_lt() -> dict[str, Any]:
    paths = sorted(STATE.glob("*.json"))
    events = [json.loads(path.read_bytes()) for path in paths]
    if not events:
        return {"event": {"state": "NOT_RESERVED__AUTHORITY_SPENT", "details": {}}}
    return events[-1]


def terminal_recorded_at(latest: dict[str, Any], post: Path) -> str:
    """Derive the reducer timestamp from durable terminal evidence."""

    wall_time_ns = latest.get("event", {}).get("wall_time_unix_ns")
    if type(wall_time_ns) is not int and post.is_file():
        wall_time_ns = json.loads(post.read_bytes()).get("completed_unix_ns")
    if type(wall_time_ns) is not int:
        raise RuntimeError("TERMINAL_WALL_TIME_MISSING")
    return datetime.fromtimestamp(wall_time_ns // 1_000_000_000, timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> int:
    latest = latest_lt()
    terminal_state = latest.get("event", {}).get("state", "UNKNOWN")
    required = (
        PRE, POST, RAW, TEARDOWN, MANIFEST, CONTEXT, SERIAL_SOURCE,
        AUTHORITY, CONSUMPTION, LY_READINESS, LY_REOBSERVATION, LAUNCH_HANDOFF,
    )
    reserved = STATE.is_dir()
    states = [json.loads(path.read_bytes()).get("event", {}).get("state") for path in sorted(STATE.glob("*.json"))] if reserved else []
    child_launched = any(state in {"RUNNING", "TERMINATED_WITH_STATUS", "INTERRUPTED_OR_LOST__UNKNOWN"} for state in states)
    complete = terminal_state == "TERMINATED_WITH_STATUS" and all(path.is_file() for path in required)
    success_complete = complete and GUEST.is_file()
    result: dict[str, Any]
    if success_complete:
        pre = json.loads(PRE.read_bytes())
        post = json.loads(POST.read_bytes())
        records = [json.loads(line) for line in RAW.read_text(encoding="utf-8").splitlines()]
        denial = one(records, "wrong_scope_denial_complete")["facts"]
        attempt = one(records, "p11_attempt_result")["facts"]
        request = one(records, "b6_boundary_request_counter")["facts"]["value"]
        denied = one(records, "b6_pre_attempt_denial_counter")["facts"]["value"]
        p11 = one(records, "b6_p11_entry_counter")["facts"]["value"]
        invocation = one(records, "b6_invocation_counter")["facts"]["value"]
        effect = one(records, "b6_protected_effect_counter")["facts"]["value"]
        agreement = one(records, "b6_producer_consumer_reduction")["facts"]["producer_consumer_agreement"]
        guest = json.loads(GUEST.read_bytes())
        teardown = json.loads(TEARDOWN.read_bytes())
        manifest = json.loads(MANIFEST.read_bytes())["manifest"]
        consumption = json.loads(CONSUMPTION.read_bytes())["checkpoint"]
        reobservation = json.loads(LY_REOBSERVATION.read_bytes())["reobservation"]
        success = all((latest["event"]["details"].get("process_exit_status") == 0, post.get("process_exit_status") == 0, pre.get("execution_attempt_count") == post.get("execution_attempt_count") == 1, pre.get("automatic_retry_count") == post.get("automatic_retry_count") == 0, consumption.get("authority_created_count") == consumption.get("authority_consumed_count") == 1, consumption.get("authority_reusable") is False, reobservation.get("result") == "VERIFIED__SAME_PREPARED_PARENT_OBJECT__SAME_INTENDED_LT_LEAF__LEAF_ABSENT", reobservation.get("authority_consumed_count") == 0, denial.get("authorized_scope") == AUTHORIZED_SCOPE, denial.get("presented_scope") == PRESENTED_SCOPE, denial.get("denial_point") == DENIAL_EDGE, denial.get("denial_error") == "operational Human act scope is invalid", denial.get("claim_attempted") is False, denial.get("wrong_scope_invariant_pass") is True, request == denied == 1, p11 == invocation == effect == 0, agreement is True, attempt.get("e05_wrong_scope_negative_authority", {}).get("semantic_mutation_field") == "authority_scope", attempt.get("e05_wrong_scope_negative_authority", {}).get("isolated_mutation_fields") == ["authority_scope"], guest.get("operational_result") == "PASS__WRONG_SCOPE_DENIED_AT_D2_BEFORE_PRECLAIM_AND_ENTRY_WITH_ZERO_EFFECT", teardown.get("teardown_state") == "COMPLETE", teardown.get("raw_evidence_sha256") == sha256(RAW), manifest.get("first_failure_or_current_result") == "PASS__E05_WRONG_SCOPE_DENIAL__GUEST_TEARDOWN_COMPLETE"))
        if not success:
            raise RuntimeError("COMPLETE_EVIDENCE_FAILS_WRONG_SCOPE_ACCEPTANCE")
        result = {"FAILURE_CLASS": "NONE__ACCEPTANCE_PROVEN", "NOVELTY": "OPERATIONAL_WRONG_SCOPE_ACCEPTANCE_PROVEN_WITH_LY_COMPOSITION", "DENIAL_CLASS": "WRONG_SCOPE", "DENIAL_ERROR": "operational Human act scope is invalid", "DENIAL_EDGE": DENIAL_EDGE, "P11_ENTRY_COUNT": 0, "PROTECTED_INVOCATION_COUNT": 0, "PROTECTED_EFFECT_COUNT": 0, "MA_E05_CREDIT": 1, "E05_AFTER": "13/18", "WRONG_SCOPE_STATUS": "SAT", "LAST_VERIFIED_EDGE": "AUTHENTICATED_WRONG_SCOPE_DENIAL_BEFORE_P11_WITH_ZERO_PROTECTED_EFFECT", "FIRST_BROKEN_EDGE": "NONE_FOR_WRONG_SCOPE_ACCEPTANCE", "FIRST_UNVERIFIED_EDGE": "INDEPENDENT_HUMAN_AUTHENTICATION_OF_MA_TERMINAL", "MINIMUM_MISSING_CAPABILITY": "NONE_FOR_WRONG_SCOPE", "MINIMUM_MISSING_PROOF": "NONE_FOR_WRONG_SCOPE", "MINIMUM_LEGAL_NEXT_DELTA": "INDEPENDENT_HUMAN_AUTHENTICATION_OF_MA_TERMINAL", "NEW_CAPABILITY_REQUIRED": "NO", "NEW_PROOF_REQUIRED": "NO__WRONG_SCOPE_ACCEPTANCE_PROVEN", "CONVERGENCE_SIGNAL": "OPERATIONAL_WRONG_SCOPE_FRONTIER_CROSSED", "REPETITION_PRESSURE": "REDUCED", "VERIFICATION_AMPLIFICATION_RISK": "BOUNDED_BY_TERMINAL_ACCEPTANCE", "terminal": "A__G77_256MA_OPERATIONAL_WRONG_SCOPE_DENIAL_PROVEN__FRESH_LZ_HUMAN_AUTHORITY_CONSUMED_EXACTLY_ONCE__LY_READINESS_AND_PRECONSUMPTION_REOBSERVATION_PROVEN__LT_ONE_SHOT_RESERVATION_PROVEN__WRONG_SCOPE_SAT__E05_13_OF_18__NO_RETRY__READY_FOR_INDEPENDENT_HUMAN_REVIEW"}
    elif complete:
        pre = json.loads(PRE.read_bytes())
        post = json.loads(POST.read_bytes())
        records = [json.loads(line) for line in RAW.read_text(encoding="utf-8").splitlines()]
        denial = one(records, "wrong_scope_denial_complete")["facts"]
        act = one(records, "human_operational_act_created")["facts"]["human_authority_act"]
        teardown = json.loads(TEARDOWN.read_bytes())
        manifest = json.loads(MANIFEST.read_bytes())["manifest"]
        context = json.loads(CONTEXT.read_bytes())
        consumption = json.loads(CONSUMPTION.read_bytes())["checkpoint"]
        reobservation = json.loads(LY_REOBSERVATION.read_bytes())["reobservation"]
        preclaim_time = context["preclaim_temporal_binding"]["coordinate_unix_ns"]
        valid_from = act["payload"]["valid_from_unix_ns"]
        valid_until = act["payload"]["valid_until_unix_ns"]
        observed = all((
            latest["event"]["details"].get("process_exit_status") == 0,
            post.get("process_exit_status") == 0,
            pre.get("execution_attempt_count") == post.get("execution_attempt_count") == 1,
            pre.get("automatic_retry_count") == post.get("automatic_retry_count") == 0,
            consumption.get("authority_created_count") == consumption.get("authority_consumed_count") == 1,
            consumption.get("authority_reusable") is False,
            reobservation.get("result") == "VERIFIED__SAME_PREPARED_PARENT_OBJECT__SAME_INTENDED_LT_LEAF__LEAF_ABSENT",
            reobservation.get("authority_consumed_count") == 0,
            denial.get("authorized_scope") == AUTHORIZED_SCOPE,
            denial.get("presented_scope") == PRESENTED_SCOPE,
            denial.get("denial_point") == DENIAL_EDGE,
            denial.get("denial_error") == "one-use Human act is future at PRECLAIM",
            denial.get("claim_attempted") is False,
            denial.get("wrong_scope_invariant_pass") is False,
            denial.get("differing_input_fields") == [],
            denial.get("p11_entry_count") == 0,
            denial.get("invocation_count") == 0,
            denial.get("protected_effect_count") == 0,
            preclaim_time == 1000,
            preclaim_time < valid_from < valid_until,
            teardown.get("execution_counters", {}).get("vm_creation_count") == 1,
            teardown.get("execution_counters", {}).get("vm_boot_count") == 1,
            teardown.get("teardown_state") == "COMPLETE",
            teardown.get("raw_evidence_sha256") == sha256(RAW),
            manifest.get("first_failure_or_current_result") == "FAIL_CLOSED__WRONG_SCOPE_REQUIRED_SUCCESS_EVIDENCE_MISSING__RuntimeError: consumed authority reuse invariant failed",
        ))
        if not observed:
            raise RuntimeError("TERMINAL_NONACCEPTANCE_EVIDENCE_CONFLICT")
        result = {
            "FAILURE_CLASS": "HARNESS_OR_TEST_ARTIFACT",
            "NOVELTY": "NEW_SEMANTIC_EDGE",
            "AFFECTED_INVARIANT": "VECTOR_LOCAL_PRECLAIM_TEMPORAL_BINDING_MUST_NOT_MASK_THE_INTENDED_WRONG_SCOPE_COMPARATOR",
            "PREVIOUS_CLOSEST_EDGE": "JH_FUTURE_D2_SUBMISSION_DENIAL_BEFORE_OWNER_STATE_AND_ENTRY",
            "SEMANTIC_DIFFERENCE": "MA_REACHED_D2_PRECLAIM_WITH_AN_EXPIRED_VECTOR_COORDINATE_BELOW_THE_FRESH_ACT_VALID_FROM_AND_THEREFORE_DENIED_FUTURE_BEFORE_SCOPE_VALIDATION",
            "PRODUCTION_BEHAVIOR_IMPACT": "NONE",
            "NEW_CAPABILITY_REQUIRED": "NO",
            "NEW_PROOF_REQUIRED": "YES__FRESHLY_AUTHORIZED_OPERATIONAL_WRONG_SCOPE_COMPARATOR_DENIAL",
            "CONVERGENCE_SIGNAL": "FAILURE_LOCALIZED_TO_EXISTING_CONTEXT_BINDING_REUSING_EXPIRED_VECTOR_COORDINATE__NO_RUNTIME_CAPABILITY_GAP",
            "REPETITION_PRESSURE": "HIGH__NO_FURTHER_OPERATION_BEFORE_INDEPENDENT_HUMAN_REVIEW",
            "VERIFICATION_AMPLIFICATION_RISK": "ELEVATED__REPEATING_WITHOUT_SEPARATE_STATIC_BINDING_PROOF_WOULD_DUPLICATE_THE_EDGE",
            "DENIAL_CLASS": "FUTURE",
            "DENIAL_ERROR": denial["denial_error"],
            "DENIAL_EDGE": DENIAL_EDGE,
            "OBSERVED_PRECLAIM_TIME_UNIX_NS": preclaim_time,
            "ACT_VALID_FROM_UNIX_NS": valid_from,
            "ACT_VALID_UNTIL_UNIX_NS": valid_until,
            "P11_ENTRY_COUNT": 0,
            "PROTECTED_INVOCATION_COUNT": 0,
            "PROTECTED_EFFECT_COUNT": 0,
            "MA_E05_CREDIT": 0,
            "E05_AFTER": "12/18",
            "WRONG_SCOPE_STATUS": "UNSAT",
            "LAST_VERIFIED_EDGE": "MA_LT_TERMINATED_STATUS_0__FM_POST_RECEIPT__GUEST_D2_PRECLAIM_DENIAL_WITH_ZERO_P11_INVOCATION_AND_EFFECT",
            "FIRST_BROKEN_EDGE": "CURRENT_ONE_USE_HUMAN_ACT_TEMPORAL_VALIDITY_TO_WRONG_SCOPE_COMPARATOR__ACT_OBSERVED_FUTURE_AT_PRECLAIM",
            "FIRST_UNVERIFIED_EDGE": "WRONG_SCOPE_COMPARATOR_DENIAL_WITH_ISOLATED_AUTHORITY_SCOPE_MISMATCH",
            "MINIMUM_MISSING_CAPABILITY": "NONE__EXISTING_TEMPORAL_AND_SCOPE_VALIDATORS_PRESENT",
            "MINIMUM_MISSING_PROOF": "AUTHENTICATED_OPERATIONAL_WRONG_SCOPE_COMPARATOR_DENIAL_WITH_ISOLATED_AUTHORITY_SCOPE_MISMATCH",
            "MINIMUM_LEGAL_NEXT_DELTA": "INDEPENDENT_HUMAN_AUTHENTICATION_OF_MA_TERMINAL",
            "terminal": "A__G77_256MA_ONE_SHOT_OPERATION_OCCURRED__WRONG_SCOPE_ACCEPTANCE_NOT_PROVEN__AUTHORITY_SPENT__NO_RETRY__EXACT_FAILURE_EDGE_RECORDED__E05_12_OF_18__STOP_FOR_INDEPENDENT_HUMAN_REVIEW",
        }
    else:
        first_broken = "AUTHORITY_CONSUMPTION_TO_EXCLUSIVE_LT_RESERVATION__STATE_PARENT_DIRECTORY_ABSENT" if not reserved else "LT_TERMINAL_TO_AUTHENTICATED_GUEST_WRONG_SCOPE_EVIDENCE"
        terminal = "A__G77_256MA_AUTHORITY_CONSUMED_BUT_OPERATION_NOT_STARTED__AUTHORITY_STATE_EXACTLY_RECORDED__ZERO_OPERATION__NO_RETRY__ZERO_E05_CREDIT__STOP_FOR_HUMAN_REVIEW" if not reserved else "A__G77_256MA_ONE_SHOT_OPERATION_OCCURRED__TERMINAL_RESULT_INCOMPLETE_OR_UNKNOWN__NO_RETRY__ZERO_E05_CREDIT__STOP_FOR_HUMAN_REVIEW"
        result = {"FAILURE_CLASS": "HARNESS_OR_TEST_ARTIFACT" if not reserved else "PROOF_GAP", "NOVELTY": "ONE_SHOT_TERMINAL_OBSERVATION", "DENIAL_CLASS": "UNKNOWN", "DENIAL_ERROR": "UNKNOWN", "DENIAL_EDGE": "UNKNOWN", "P11_ENTRY_COUNT": "UNKNOWN", "PROTECTED_INVOCATION_COUNT": "UNKNOWN", "PROTECTED_EFFECT_COUNT": "UNKNOWN", "MA_E05_CREDIT": 0, "E05_AFTER": "12/18", "WRONG_SCOPE_STATUS": "UNSAT", "LAST_VERIFIED_EDGE": "AUTHORITY_CONSUMED_EXACTLY_ONCE__NONREUSABLE" if not reserved else terminal_state, "FIRST_BROKEN_EDGE": first_broken, "FIRST_UNVERIFIED_EDGE": "AUTHENTICATED_TERMINAL_OPERATIONAL_WRONG_SCOPE_DENIAL_BEFORE_P11", "MINIMUM_MISSING_CAPABILITY": "UNKNOWN", "MINIMUM_MISSING_PROOF": "AUTHENTICATED_TERMINAL_OPERATIONAL_WRONG_SCOPE_DENIAL_BEFORE_P11", "MINIMUM_LEGAL_NEXT_DELTA": "STOP_FOR_INDEPENDENT_HUMAN_REVIEW__NO_RETRY", "NEW_CAPABILITY_REQUIRED": "UNKNOWN", "NEW_PROOF_REQUIRED": "YES__AUTHENTICATED_TERMINAL_OPERATIONAL_WRONG_SCOPE_DENIAL_BEFORE_P11", "CONVERGENCE_SIGNAL": "NONE__TERMINAL_EVIDENCE_INCOMPLETE", "REPETITION_PRESSURE": "HIGH", "VERIFICATION_AMPLIFICATION_RISK": "ELEVATED", "terminal": terminal}
    if SERIAL_SOURCE.is_file() and not SERIAL.exists():
        SERIAL.write_bytes(SERIAL_SOURCE.read_bytes())
    evidence_artifacts = (PRE, POST, RAW, GUEST, TEARDOWN, MANIFEST, SERIAL, AUTHORITY, CONSUMPTION, LY_READINESS, LY_REOBSERVATION, LAUNCH_HANDOFF)
    artifacts = {path.relative_to(ROOT).as_posix(): sha256(path) for path in evidence_artifacts if path.is_file()}
    reduction = {"schema_id": "G77_256MA_OPERATIONAL_EVIDENCE_REDUCTION_V1", "recorded_at_utc": terminal_recorded_at(latest, POST), "recovery_state_class": "STATE_C__AUTHORITY_CONSUMED__OPERATION_NOT_PROVEN_STARTED" if not reserved else "STATE_D_OR_E", "operation_completed": complete, "acceptance_satisfied": result["WRONG_SCOPE_STATUS"] == "SAT", "authority_created_count": 1, "authority_consumed_count": 1, "authority_reusable": False, "lt_terminal_state": terminal_state, "lt_reservation_count": int(reserved), "lt_child_launch_count": int(child_launched), "fm_operation_count": int(child_launched), "fm_pre_receipt_count": int(PRE.is_file()), "fm_post_receipt_count": int(POST.is_file()), "operation_attempt_count": int(child_launched), "qemu_start_count": int(PRE.is_file()), "vm_start_count": int(PRE.is_file()), "retry_count": 0, "relaunch_permitted": False, "artifacts": artifacts, **result}
    write_once(REDUCTION, seal("G77_256MA_OPERATIONAL_EVIDENCE_REDUCTION_ENVELOPE_V1", "reduction", reduction))
    decision = {"LZ_OBJECT_ID": "G77_256LZ_WRONG_SCOPE_PHASE_A_REVIEW_OBJECT_001", "LZ_OBJECT_SHA256": "e3f402fb9d8ccaa0495af55a4314e1656501f47e2814bf371d0146a87d78d3ed", "HUMAN_DECISION_SOURCE": "EXPLICIT_CURRENT_HUMAN_DECISION_OVER_INDEPENDENTLY_AUTHENTICATED_LZ_OBJECT", "HUMAN_DECISION_COUNT": 1, "MA_AUTHORITY_ID": "G77_256MA_FRESH_HUMAN_OPERATIONAL_AUTHORITY_001", "AUTHORITY_CREATED_COUNT": 1, "AUTHORITY_CONSUMED_COUNT": 1, "AUTHORITY_REUSABLE": "NO", "LY_READINESS_SHA256": sha256(LY_READINESS), "LY_PRECONSUMPTION_REOBSERVATION_SHA256": sha256(LY_REOBSERVATION), "LT_CAPABILITY_ID": "SESSION_INDEPENDENT_ONE_SHOT_FM_PROCESS_SUPERVISION_AND_DURABLE_TERMINAL_HANDOFF_V1", "LT_LIFECYCLE_ID": "G77_256MA_WRONG_SCOPE_OPERATIONAL_LIFECYCLE_001", "LT_RESERVATION_COUNT": int(reserved), "LT_CHILD_LAUNCH_COUNT": int(child_launched), "LT_TERMINAL_STATE": terminal_state, "FM_OPERATION_COUNT": int(child_launched), "FM_PRE_RECEIPT_COUNT": int(PRE.is_file()), "FM_POST_RECEIPT_COUNT": int(POST.is_file()), "QEMU_COUNT": int(PRE.is_file()), "VM_COUNT": int(PRE.is_file()), "RETRY_COUNT": 0, "AUTHORIZED_SCOPE": AUTHORIZED_SCOPE, "PRESENTED_SCOPE": PRESENTED_SCOPE, "ISOLATED_MISMATCH": "authority_scope", "E05_BEFORE": "12/18", "WRONG_SCOPE_BEFORE": "UNSAT", "PRODUCTION_BEHAVIOR_IMPACT": "NONE", "OPERATIONAL_RETRY_AUTHORIZED": "NO", "AIGOL_DEVELOPMENT_LOOP_STATUS": "SHADOW", "operational_reduction_sha256": sha256(REDUCTION), **result}
    decision["MA_AUTHORITY_SHA256"] = sha256(AUTHORITY)
    write_once(DECISION, seal("G77_256MA_TERMINAL_DECISION_ENVELOPE_V1", "decision", decision))
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
