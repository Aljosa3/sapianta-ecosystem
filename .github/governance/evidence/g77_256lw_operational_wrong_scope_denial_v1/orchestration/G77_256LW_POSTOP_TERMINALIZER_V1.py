#!/usr/bin/env python3
"""Read the one LW/LV operation and seal success or UNKNOWN without relaunch."""

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
LW = ROOT / ".github/governance/evidence/g77_256lw_operational_wrong_scope_denial_v1"
LV = ROOT / ".github/governance/evidence/g77_256lv_fresh_wrong_scope_phase_a_review_object_v1"
RUNTIME = LV / "operation_state/runtime_export"
RECEIPTS = LV / "operation_state/receipts"
STATE = LW / "operation_state/lt_supervision/G77_256LW_WRONG_SCOPE_OPERATION_001"
PRE = RECEIPTS / "G77_256LV_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
POST = RECEIPTS / "G77_256LV_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
RAW = RUNTIME / "G77_256LV_RAW_EXECUTION_EVIDENCE_V1.jsonl"
GUEST = RUNTIME / "G77_256LV_GUEST_EXECUTION_SEAL_V1.json"
TEARDOWN = RUNTIME / "G77_256LV_GUEST_TEARDOWN_SEAL_V1.json"
MANIFEST = RUNTIME / "G77_256LV_CONTINUATION_MANIFEST_TERMINAL_V1.json"
SERIAL_SOURCE = Path("/tmp/g77_256lv_fresh_wrong_scope_phase_a_review_object_v1/serial.log")
SERIAL = LW / "G77_256LW_SERIAL_CONSOLE_V1.log"
REDUCTION = LW / "G77_256LW_OPERATIONAL_EVIDENCE_REDUCTION_V1.json"
DECISION = LW / "G77_256LW_TERMINAL_DECISION_V1.json"
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


def main() -> int:
    latest = latest_lt()
    terminal_state = latest.get("event", {}).get("state", "UNKNOWN")
    required = (PRE, POST, RAW, GUEST, TEARDOWN, MANIFEST, SERIAL_SOURCE)
    reserved = STATE.is_dir()
    states = [json.loads(path.read_bytes()).get("event", {}).get("state") for path in sorted(STATE.glob("*.json"))] if reserved else []
    child_launched = any(state in {"RUNNING", "TERMINATED_WITH_STATUS", "INTERRUPTED_OR_LOST__UNKNOWN"} for state in states)
    complete = terminal_state == "TERMINATED_WITH_STATUS" and all(path.is_file() for path in required)
    result: dict[str, Any]
    if complete:
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
        success = all((latest["event"]["details"].get("process_exit_status") == 0, post.get("process_exit_status") == 0, pre.get("execution_attempt_count") == post.get("execution_attempt_count") == 1, pre.get("automatic_retry_count") == post.get("automatic_retry_count") == 0, denial.get("authorized_scope") == AUTHORIZED_SCOPE, denial.get("presented_scope") == PRESENTED_SCOPE, denial.get("denial_point") == DENIAL_EDGE, denial.get("denial_error") == "operational Human act scope is invalid", denial.get("claim_attempted") is False, denial.get("wrong_scope_invariant_pass") is True, request == denied == 1, p11 == invocation == effect == 0, agreement is True, attempt.get("e05_wrong_scope_negative_authority", {}).get("semantic_mutation_field") == "authority_scope", attempt.get("e05_wrong_scope_negative_authority", {}).get("isolated_mutation_fields") == ["authority_scope"], guest.get("operational_result") == "PASS__WRONG_SCOPE_DENIED_AT_D2_BEFORE_PRECLAIM_AND_ENTRY_WITH_ZERO_EFFECT", teardown.get("teardown_state") == "COMPLETE", teardown.get("raw_evidence_sha256") == sha256(RAW), manifest.get("first_failure_or_current_result") == "PASS__E05_WRONG_SCOPE_DENIAL__GUEST_TEARDOWN_COMPLETE"))
        if not success:
            raise RuntimeError("COMPLETE_EVIDENCE_FAILS_WRONG_SCOPE_ACCEPTANCE")
        result = {"DENIAL_CLASS": "WRONG_SCOPE", "DENIAL_EDGE": DENIAL_EDGE, "P11_ENTRY_COUNT": 0, "PROTECTED_INVOCATION_COUNT": 0, "PROTECTED_EFFECT_COUNT": 0, "LW_E05_CREDIT": 1, "E05_AFTER": "13/18", "WRONG_SCOPE_STATUS": "SAT", "LAST_VERIFIED_EDGE": "AUTHENTICATED_WRONG_SCOPE_DENIAL_BEFORE_P11_WITH_ZERO_PROTECTED_EFFECT", "FIRST_BROKEN_EDGE": "NONE_FOR_WRONG_SCOPE_ACCEPTANCE", "MINIMUM_MISSING_CAPABILITY": "NONE_FOR_WRONG_SCOPE", "MINIMUM_MISSING_PROOF": "NONE_FOR_WRONG_SCOPE", "MINIMUM_LEGAL_NEXT_DELTA": "STOP_FOR_INDEPENDENT_HUMAN_AUTHENTICATION_AND_REVIEW_OF_LW_TERMINAL", "terminal": "A__G77_256LW_WRONG_SCOPE_OPERATIONALLY_DENIED_BEFORE_P11__ONE_HUMAN_DECISION__ONE_AUTHORITY__ONE_CONSUMPTION__ONE_OPERATION__ZERO_RETRY__ZERO_P11_ENTRY__ZERO_PROTECTED_EFFECT__E05_13_OF_18__STOP_FOR_HUMAN_REVIEW"}
    else:
        first_broken = "AUTHORITY_CONSUMPTION_TO_EXCLUSIVE_LT_RESERVATION__STATE_PARENT_DIRECTORY_ABSENT" if not reserved else "LT_TERMINAL_TO_AUTHENTICATED_GUEST_WRONG_SCOPE_EVIDENCE"
        terminal = "A__G77_256LW_AUTHORITY_CONSUMED_BUT_OPERATION_NOT_STARTED__AUTHORITY_STATE_EXACTLY_RECORDED__ZERO_OPERATION__NO_RETRY__ZERO_E05_CREDIT__STOP_FOR_HUMAN_REVIEW" if not reserved else "A__G77_256LW_ONE_SHOT_OPERATION_OCCURRED__TERMINAL_RESULT_INCOMPLETE_OR_UNKNOWN__NO_RETRY__ZERO_E05_CREDIT__STOP_FOR_HUMAN_REVIEW"
        result = {"DENIAL_CLASS": "UNKNOWN", "DENIAL_EDGE": "UNKNOWN", "P11_ENTRY_COUNT": "UNKNOWN", "PROTECTED_INVOCATION_COUNT": "UNKNOWN", "PROTECTED_EFFECT_COUNT": "UNKNOWN", "LW_E05_CREDIT": 0, "E05_AFTER": "12/18", "WRONG_SCOPE_STATUS": "UNSAT", "LAST_VERIFIED_EDGE": "AUTHORITY_CONSUMED_EXACTLY_ONCE__NONREUSABLE" if not reserved else terminal_state, "FIRST_BROKEN_EDGE": first_broken, "MINIMUM_MISSING_CAPABILITY": "NONE__GENERATION_LOCAL_READINESS_DEFECT_NOT_PRODUCTION_CAPABILITY_GAP" if not reserved else "UNKNOWN", "MINIMUM_MISSING_PROOF": "AUTHENTICATED_TERMINAL_OPERATIONAL_WRONG_SCOPE_DENIAL_BEFORE_P11", "MINIMUM_LEGAL_NEXT_DELTA": "STOP_FOR_INDEPENDENT_HUMAN_REVIEW__NO_RETRY", "terminal": terminal}
    if SERIAL_SOURCE.is_file() and not SERIAL.exists():
        SERIAL.write_bytes(SERIAL_SOURCE.read_bytes())
    artifacts = {path.relative_to(ROOT).as_posix(): sha256(path) for path in required if path.is_file()}
    reduction = {"schema_id": "G77_256LW_OPERATIONAL_EVIDENCE_REDUCTION_V1", "recorded_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"), "recovery_state_class": "STATE_C__AUTHORITY_CONSUMED__OPERATION_NOT_PROVEN_STARTED" if not reserved else "STATE_D_OR_E", "failure_class_post_operation": "HARNESS_OR_TEST_ARTIFACT" if not reserved else "PROOF_GAP", "novelty_post_operation": "LW_GENERATION_LOCAL_LT_STATE_PARENT_READINESS_OMITTED_BEFORE_AUTHORITY_CONSUMPTION" if not reserved else "ONE_SHOT_TERMINAL_OBSERVATION", "lt_terminal_state": terminal_state, "lt_reservation_count": int(reserved), "lt_child_launch_count": int(child_launched), "fm_pre_receipt_count": int(PRE.is_file()), "fm_post_receipt_count": int(POST.is_file()), "operation_attempt_count": int(child_launched), "qemu_start_count": int(PRE.is_file()), "vm_start_count": int(PRE.is_file()), "retry_count": 0, "artifacts": artifacts, **result}
    write_once(REDUCTION, seal("G77_256LW_OPERATIONAL_EVIDENCE_REDUCTION_ENVELOPE_V1", "reduction", reduction))
    decision = {"FAILURE_CLASS": "HARNESS_OR_TEST_ARTIFACT" if not reserved else "PROOF_GAP", "NOVELTY": "LW_GENERATION_LOCAL_LT_STATE_PARENT_READINESS_OMITTED_BEFORE_AUTHORITY_CONSUMPTION" if not reserved else "ONE_SHOT_TERMINAL_OBSERVATION", "LV_OBJECT_ID": "G77_256LV_WRONG_SCOPE_PHASE_A_REVIEW_OBJECT_001", "LV_OBJECT_SHA256": "333c95c19351f237e5e8bd000894e6bbabadc7c5851b33e624d2c256378c4f5e", "HUMAN_DECISION_SOURCE": "EXPLICIT_CURRENT_HUMAN_DECISION_OVER_INDEPENDENTLY_AUTHENTICATED_LV_OBJECT", "HUMAN_DECISION_COUNT": 1, "LW_AUTHORITY_ID": "G77_256LW_FRESH_HUMAN_OPERATIONAL_AUTHORITY_001", "AUTHORITY_CREATED_COUNT": 1, "AUTHORITY_CONSUMED_COUNT": 1, "AUTHORITY_REUSABLE": "NO", "LT_CAPABILITY_ID": "SESSION_INDEPENDENT_ONE_SHOT_FM_PROCESS_SUPERVISION_AND_DURABLE_TERMINAL_HANDOFF_V1", "LT_LIFECYCLE_ID": "G77_256LW_WRONG_SCOPE_OPERATIONAL_LIFECYCLE_001", "LT_RESERVATION_COUNT": int(reserved), "LT_CHILD_LAUNCH_COUNT": int(child_launched), "LT_TERMINAL_STATE": terminal_state, "FM_OPERATION_ATTEMPT_COUNT": int(child_launched), "FM_PRE_RECEIPT_COUNT": int(PRE.is_file()), "FM_POST_RECEIPT_COUNT": int(POST.is_file()), "QEMU_START_COUNT": int(PRE.is_file()), "VM_START_COUNT": int(PRE.is_file()), "RETRY_COUNT": 0, "AUTHORIZED_SCOPE": AUTHORIZED_SCOPE, "PRESENTED_SCOPE": PRESENTED_SCOPE, "ISOLATED_MISMATCH": "authority_scope", "E05_BEFORE": "12/18", "PRODUCTION_BEHAVIOR_IMPACT": "NONE", "NEW_CAPABILITY_REQUIRED": "NO", "OPERATIONAL_RETRY_AUTHORIZED": "NO", "AIGOL_DEVELOPMENT_LOOP_STATUS": "SHADOW", "AIGOL_DEVELOPMENT_FIRST_BROKEN_EDGE": "PREAUTHORITY_STATIC_PREREQUISITE_ENUMERATION_DID_NOT_ENFORCE_LT_STATE_PARENT_EXISTENCE", "operational_reduction_sha256": sha256(REDUCTION), **result}
    decision["LW_AUTHORITY_SHA256"] = sha256(LW / "G77_256LW_FRESH_HUMAN_OPERATIONAL_AUTHORITY_V1.json")
    write_once(DECISION, seal("G77_256LW_TERMINAL_DECISION_ENVELOPE_V1", "decision", decision))
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
