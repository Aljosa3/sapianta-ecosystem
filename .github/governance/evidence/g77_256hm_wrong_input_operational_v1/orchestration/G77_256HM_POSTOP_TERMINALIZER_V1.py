#!/usr/bin/env python3
"""Preserve and terminalize the single consumed G77-256HM operation."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
HM = ROOT / ".github/governance/evidence/g77_256hm_wrong_input_operational_v1"
RUNTIME = HM / "operation_state/runtime_export"
RECEIPTS = HM / "operation_state/receipts"
TRANSIENT = Path("/tmp/g77_256hm_wrong_input_operational_v1")
SERIAL_SOURCE = TRANSIENT / "serial.log"
SERIAL = HM / "G77_256HM_SERIAL_CONSOLE_V1.log"
PRE_RECEIPT = RECEIPTS / "G77_256HM_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
POST_RECEIPT = RECEIPTS / "G77_256HM_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
RAW = RUNTIME / "G77_256HM_RAW_EXECUTION_EVIDENCE_V1.jsonl"
GUEST_TEARDOWN = RUNTIME / "G77_256HM_GUEST_TEARDOWN_SEAL_V1.json"
AUTHORITY = HM / "G77_256HM_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
AUTHORITY_CHECKPOINT = HM / "G77_256HM_AUTHORITY_VALIDATION_CHECKPOINT_V1.json"
REQUEST = HM / "G77_256HM_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
PRESENTATION = HM / "G77_256HM_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
GRANT = HM / "G77_256HM_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
CONTEXT = HM / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
INDEPENDENT = HM / "G77_256HM_INDEPENDENT_TERMINAL_EVIDENCE_REDUCTION_V1.json"
PRE_TEARDOWN = HM / "G77_256HM_SPCE_HOST_PRE_TEARDOWN_CHECKPOINT_V1.json"
TEARDOWN = HM / "G77_256HM_SPCE_HOST_TEARDOWN_CHECKPOINT_V1.json"
FINAL_SEAL = HM / "G77_256HM_SPCE_FINAL_EXECUTION_SEAL_V1.json"
TERMINAL = HM / "G77_256HM_SPCE_TERMINAL_REDUCTION_V1.json"
BASE_IMAGE = Path("/tmp/g77_256cw.IkqZJN/noble-server-cloudimg-amd64.img")
BASE_SHA256 = "6e40c07ae715f744f84af0bec76415cc1987dd115b4b8de437818561f01a3733"
GENERATION = "G77_256HM_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_INPUT_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256HM_E05_WRONG_INPUT_DENIAL_BEFORE_ENTRY_001"
VERDICT = (
    "FAIL_CLOSED__G77_256HM_WRONG_INPUT_OPERATIONAL_PROOF_NOT_PROVEN__"
    "GUEST_BOOTSTRAP_EXPECTED_HARNESS_HASH_MISMATCH_BEFORE_REQUEST__E05_7_OF_18__"
    "ONE_OPERATION_ONLY__NO_RETRY__HUMAN_REVIEW_REQUIRED"
)
LAST_EDGE = (
    "ONE_AUTHORIZED_FM_INVOCATION__ONE_NO_NETWORK_QEMU_BOOT__"
    "WRONG_INPUT_RUNTIME_SPECIALIZATION_LOADED__ER_HARNESS_ENTERED"
)
BROKEN_EDGE = (
    "ER_HARNESS_EXPECTED_HASH_ARGUMENT_RETAINED_HISTORICAL_FM_WRAPPER_IDENTITY__"
    "MOUNTED_ACTIVE_WRONG_INPUT_ADAPTER_HAS_DISTINCT_AUTHENTICATED_IDENTITY"
)
MISSING = (
    "CURRENT_WRONG_INPUT_GUEST_BOOTSTRAP_EXPECTED_HARNESS_HASH_BINDING_"
    "TO_THE_ACTIVE_PROJECTED_ADAPTER"
)
NEXT_DELTA = (
    "ONE_SEPARATE_HUMAN_REVIEWED_REPOSITORY_ONLY_GENERATION_TO_BIND_AND_VERIFY_"
    "THE_BOOTSTRAP_EXPECTED_HARNESS_HASH_TO_THE_ACTIVE_WRONG_INPUT_ADAPTER__"
    "NO_OPERATION_IN_HM"
)


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def seal(schema: str, key: str, value: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": schema,
        key: value,
        f"{key}_sha256": hashlib.sha256(canonical_bytes(value)).hexdigest(),
    }


def write_new(path: Path, value: dict[str, Any]) -> None:
    payload = canonical_bytes(value)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    with temporary.open("xb", buffering=0) as handle:
        handle.write(payload)
        os.fsync(handle.fileno())
    os.replace(temporary, path)
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def copy_serial() -> None:
    payload = SERIAL_SOURCE.read_bytes()
    if SERIAL.exists():
        if SERIAL.read_bytes() != payload:
            raise RuntimeError("existing durable serial differs from transient source")
        return
    with SERIAL.open("xb", buffering=0) as handle:
        handle.write(payload)
        os.fsync(handle.fileno())
    if SERIAL.read_bytes() != payload:
        raise RuntimeError("durable serial copy mismatch")


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"module load failed: {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def authoritative_probe() -> str:
    producer = load_module(
        ROOT / ".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/producer/G77_256GY_WRONG_INPUT_REQUEST_AND_CANDIDATE_PRODUCER_V1.py",
        "g77_256hm_gy_producer",
    )
    reducer = load_module(
        ROOT / ".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/reducer/G77_256GY_WRONG_INPUT_TERMINAL_ACCEPTANCE_REDUCER_V1.py",
        "g77_256hm_gy_reducer",
    )
    substrate = load_module(ROOT / "tests/p11_da_disposable_substrate_v1.py", "g77_256hm_substrate")
    gv_raw = ROOT / (
        ".github/governance/evidence/g77_256gv_wrong_attempt_operational_v1/"
        "operation_state/runtime_export/G77_256GV_RAW_EXECUTION_EVIDENCE_V1.jsonl"
    )
    authorized = None
    for line in gv_raw.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        if record.get("record_type") == "wrong_attempt_denial_complete":
            authorized = substrate.bind_record_identity(record["facts"]["authorized_input_record"])
            break
    if authorized is None:
        raise RuntimeError("authenticated reducer probe baseline absent")
    request = producer.produce_wrong_input_request(
        repository_root=ROOT,
        authorized_input_canonical_bytes=authorized,
        wrong_input_identity="G77_256HM_E05_SUPPLIED_WRONG_INPUT_002",
        request_identity="G77_256HM_WRONG_INPUT_CUSTODY_REQUEST_001",
    )
    facts = {
        "case_id": producer.CASE_ID,
        "selected_vector": producer.SELECTED_VECTOR,
        "request_identity": request["request_identity"],
        "evidence_provenance": reducer.EVIDENCE_PROVENANCE,
    }
    evidence = {
        "schema_id": "G77_256GY_WRONG_INPUT_OPERATIONAL_EVIDENCE_V1",
        "case_id": producer.CASE_ID,
        "selected_vector": producer.SELECTED_VECTOR,
        "formal_specification_identity": reducer.FORMAL_SPECIFICATION_IDENTITY,
        "formal_specification_sha256": reducer.FORMAL_SPECIFICATION_SHA256,
        "candidate_identity": reducer.CANDIDATE_IDENTITY,
        "evidence_provenance": reducer.EVIDENCE_PROVENANCE,
        "request_identity": request["request_identity"],
        "authorized_input_record": request["authorized_input_record"],
        "supplied_input_record": request["supplied_input_record"],
        "differing_input_fields": request["differing_input_fields"],
        "semantic_mutation_field": request["target_mutated_coordinate"],
        "dependent_recomputation_fields": request["dependent_recomputation_fields"],
        "preserved_dimension_proof": request["preserved_dimension_proof"],
        "denial_boundary": request["expected_denial_boundary"],
        "denial_error_type": request["expected_error_type"],
        "denial_error_reason": request["expected_error_reason"],
        "request_count": 0,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "claim_attempted": False,
        "owner_state_unchanged": True,
        "runtime_ledger_exists": False,
        "output_present": False,
        "raw_evidence_records": [
            {"record_type": "wrong_input_request", "facts": dict(facts)},
            {"record_type": "wrong_input_denial_complete", "facts": dict(facts)},
            {"record_type": "request_counter", "facts": {"count": 0}},
            {"record_type": "p11_entry_counter", "facts": {"count": 0}},
            {"record_type": "protected_invocation_counter", "facts": {"count": 0}},
            {"record_type": "protected_effect_counter", "facts": {"count": 0}},
        ],
    }
    try:
        reducer.reduce_wrong_input_terminal_evidence(evidence)
    except reducer.WrongInputReductionError as exc:
        if str(exc) != "REQUEST_COUNT_INVALID":
            raise
        return "FAIL_CLOSED__REQUEST_COUNT_INVALID"
    raise RuntimeError("authoritative reducer unexpectedly accepted request_count=0")


def counters() -> dict[str, int]:
    return {
        "human_operational_authority": 1,
        "authority_consumption": 1,
        "pre": 1,
        "fm_operational_launcher_invocation": 1,
        "qemu": 1,
        "vm_creation": 1,
        "vm_boot": 1,
        "operation_attempt": 1,
        "wrong_input_operation": 0,
        "request": 0,
        "p11_entry": 0,
        "protected_invocation": 0,
        "protected_effect": 0,
        "retry": 0,
        "repair_and_continue": 0,
        "operational_replay": 0,
        "e05_credit": 0,
    }


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    targets = (INDEPENDENT, PRE_TEARDOWN, TEARDOWN, FINAL_SEAL, TERMINAL)
    if any(path.exists() for path in targets):
        raise RuntimeError("terminal HM artifact collision")
    if not TRANSIENT.is_dir() or not SERIAL_SOURCE.is_file():
        raise RuntimeError("transient operation evidence absent")
    if subprocess.run(
        ["pgrep", "-f", "^/usr/bin/qemu-system-x86_64.*g77_256hm"],
        check=False,
        stdout=subprocess.DEVNULL,
    ).returncode == 0:
        raise RuntimeError("matching QEMU process still active")
    pre = json.loads(PRE_RECEIPT.read_bytes())
    post = json.loads(POST_RECEIPT.read_bytes())
    if (
        pre["started_unix_ns"] != post["started_unix_ns"]
        or pre["execution_attempt_count"] != post["execution_attempt_count"]
        or pre["execution_attempt_count"] != 1
        or pre["automatic_retry_count"] != post["automatic_retry_count"]
        or pre["automatic_retry_count"] != 0
        or post["process_exit_status"] != 0
    ):
        raise RuntimeError("single receipt pair invalid")
    raw_records = [json.loads(line) for line in RAW.read_text(encoding="utf-8").splitlines()]
    guest = json.loads(GUEST_TEARDOWN.read_bytes())
    if (
        len(raw_records) != 2
        or raw_records[0]["facts"]["first_failure"] != "RuntimeError: EN harness hash mismatch"
        or guest["first_failure"] != "RuntimeError: EN harness hash mismatch"
        or guest["execution_counters"]["vm_boot_count"] != 1
        or guest["execution_counters"]["e05_case_execution_count"] != 0
        or guest["execution_counters"]["p11_entry_count"] != 0
    ):
        raise RuntimeError("guest terminal evidence mismatch")
    serial_bytes = SERIAL_SOURCE.read_bytes()
    if b"G77_256FM_BOOT_MARKER=PASS" not in serial_bytes or b"G77_256FM_HARNESS_EXIT_STATUS=40" not in serial_bytes:
        raise RuntimeError("serial terminal markers absent")
    if sha256(BASE_IMAGE) != BASE_SHA256:
        raise RuntimeError("base image drift before teardown")

    copy_serial()
    reducer_result = authoritative_probe()
    reduction = {
        "schema_id": "G77_256HM_INDEPENDENT_TERMINAL_EVIDENCE_REDUCTION_V1",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "observed_terminal_shape": "GUEST_EXPECTED_HARNESS_HASH_FAILURE_BEFORE_WRONG_INPUT_REQUEST",
        "failure": {
            "type": "RuntimeError",
            "reason": "EN harness hash mismatch",
            "expected_harness_sha256": "f2808a148bc9839f083ea9e59903674fe0dcd2a7587eee342fca44066ee9ad2b",
            "active_adapter_sha256": "fb83002e5567c2a109bfb977270865e6fb085e39f551d1068d03537a3b1d6230",
            "harness_exit_status": 40,
            "qemu_process_exit_status": 0,
            "serial_sha256": sha256(SERIAL),
            "serial_byte_count": SERIAL.stat().st_size,
        },
        "counter_reduction": counters(),
        "gy_authoritative_acceptance_reducer": {
            "status": "VERIFIED",
            "result": reducer_result,
            "input_request_count": 0,
            "e05_credit": 0,
        },
        "independent_reducer": {
            "status": "VERIFIED",
            "result": "FAIL_CLOSED__WRONG_INPUT_OPERATIONAL_ACCEPTANCE_NOT_PROVEN",
            "request_count": 0,
            "p11_entry_count": 0,
            "protected_invocation_count": 0,
            "protected_effect_count": 0,
            "e05_credit": 0,
        },
        "authoritative_independent_reduction_agreement_status": "VERIFIED",
        "e05": {"before": "7/18", "after": "7/18", "credit": 0},
        "last_verified_edge": LAST_EDGE,
        "first_broken_edge": BROKEN_EDGE,
        "minimum_missing_capability": MISSING,
        "minimum_legal_next_development_delta": NEXT_DELTA,
        "auto_continuable": False,
        "human_review_required": True,
        "recorded_at_utc": now(),
    }
    write_new(INDEPENDENT, seal(
        "G77_256HM_INDEPENDENT_TERMINAL_EVIDENCE_REDUCTION_ENVELOPE_V1",
        "reduction",
        reduction,
    ))

    pre_checkpoint = {
        "schema_id": "G77_256HM_SPCE_HOST_PRE_TEARDOWN_CHECKPOINT_V1",
        "checkpoint_class": "HOST_PRE_TEARDOWN",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "durable_evidence": {
            "serial_path": SERIAL.relative_to(ROOT).as_posix(),
            "serial_sha256": sha256(SERIAL),
            "serial_byte_count": SERIAL.stat().st_size,
            "pre_receipt_sha256": sha256(PRE_RECEIPT),
            "post_receipt_sha256": sha256(POST_RECEIPT),
            "raw_evidence_sha256": sha256(RAW),
            "guest_teardown_sha256": sha256(GUEST_TEARDOWN),
        },
        "failure_observation": {
            "type": "RuntimeError",
            "reason": "EN harness hash mismatch",
            "guest_boot_marker": "PASS",
            "harness_exit_status": 40,
            "qemu_process_exit_status": 0,
            "raw_record_count": 2,
        },
        "host_lifecycle": {
            "state": "PRE_TEARDOWN_OBSERVED",
            "transient_root_present": True,
            "checkout_present": (TRANSIENT / "checkout").is_dir(),
            "overlay_present": (TRANSIENT / "guest-overlay.qcow2").is_file(),
            "qemu_process_absent": True,
            "persistent_evidence_preserved": True,
        },
        "base_image": {"path": str(BASE_IMAGE), "sha256_pre_teardown": BASE_SHA256, "byte_identical": True},
        "operational_counters": counters(),
        "e05": {"before": "7/18", "after": "7/18", "credit": 0, "acceptance": "NOT_PROVEN"},
        "last_verified_edge": LAST_EDGE,
        "first_broken_edge": BROKEN_EDGE,
        "minimum_missing_capability": MISSING,
        "minimum_legal_next_development_delta": NEXT_DELTA,
        "checkpoint_is_authority": False,
        "auto_continuable": False,
        "human_review_required": True,
        "recorded_at_utc": now(),
    }
    write_new(PRE_TEARDOWN, seal(
        "G77_256HM_SPCE_HOST_PRE_TEARDOWN_CHECKPOINT_ENVELOPE_V1",
        "checkpoint",
        pre_checkpoint,
    ))

    if TRANSIENT.resolve() != Path("/tmp/g77_256hm_wrong_input_operational_v1"):
        raise RuntimeError("transient teardown target changed")
    shutil.rmtree(TRANSIENT)
    if TRANSIENT.exists() or TRANSIENT.is_symlink():
        raise RuntimeError("transient teardown incomplete")
    if sha256(BASE_IMAGE) != BASE_SHA256:
        raise RuntimeError("base image drift after teardown")

    teardown_checkpoint = {
        "schema_id": "G77_256HM_SPCE_HOST_TEARDOWN_CHECKPOINT_V1",
        "checkpoint_class": "HOST_TEARDOWN",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "host_pre_teardown_checkpoint": {
            "path": PRE_TEARDOWN.relative_to(ROOT).as_posix(),
            "file_sha256": sha256(PRE_TEARDOWN),
            "inner_sha256": json.loads(PRE_TEARDOWN.read_bytes())["checkpoint_sha256"],
        },
        "host_teardown": {
            "state": "TEARDOWN_COMPLETE",
            "transient_root": str(TRANSIENT),
            "transient_root_absent": True,
            "qemu_process_absent": True,
            "persistent_serial_preserved": True,
            "persistent_pre_receipt_preserved": True,
            "persistent_post_receipt_preserved": True,
            "persistent_guest_evidence_preserved": True,
        },
        "base_image": {"path": str(BASE_IMAGE), "sha256_before": BASE_SHA256, "sha256_after": BASE_SHA256, "byte_identical": True},
        "operational_counters": counters(),
        "e05": {"before": "7/18", "after": "7/18", "credit": 0},
        "terminal_defect": {
            "last_verified_edge": LAST_EDGE,
            "first_broken_edge": BROKEN_EDGE,
            "minimum_missing_capability": MISSING,
            "minimum_legal_next_development_delta": NEXT_DELTA,
        },
        "checkpoint_is_authority": False,
        "auto_continuable": False,
        "human_review_required": True,
        "recorded_at_utc": now(),
    }
    write_new(TEARDOWN, seal(
        "G77_256HM_SPCE_HOST_TEARDOWN_CHECKPOINT_ENVELOPE_V1",
        "checkpoint",
        teardown_checkpoint,
    ))

    artifact_paths = (
        AUTHORITY_CHECKPOINT, AUTHORITY, PRESENTATION, REQUEST, GRANT, INDEPENDENT,
        POST_RECEIPT, PRE_RECEIPT, RAW, GUEST_TEARDOWN, SERIAL, PRE_TEARDOWN, TEARDOWN, CONTEXT,
    )
    final = {
        "schema_id": "G77_256HM_SPCE_FINAL_EXECUTION_SEAL_V1",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "artifacts": {path.name: sha256(path) for path in artifact_paths},
        "authority_created_exists": 1,
        "authority_validated": 1,
        "authority_consumed": 1,
        "operation_count": 1,
        "qemu_count": 1,
        "vm_boot_count": 1,
        "wrong_input_count": 0,
        "request_count": 0,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "retry_count": 0,
        "repair_count": 0,
        "replay_count": 0,
        "e05_credit": 0,
        "teardown_state": "COMPLETE",
        "final_result": VERDICT,
        "auto_continuable": False,
        "human_review_required": True,
        "recorded_at_utc": now(),
    }
    write_new(FINAL_SEAL, seal(
        "G77_256HM_SPCE_FINAL_EXECUTION_SEAL_ENVELOPE_V1", "seal", final
    ))

    terminal = {
        "schema_id": "G77_256HM_SPCE_TERMINAL_REDUCTION_V1",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "terminal_state": "FAIL_CLOSED__OPERATION_CONSUMED__NO_RETRY",
        "operational_counters": counters(),
        "request_entry_invocation_effect_separation": {
            "request": 0, "p11_entry": 0, "protected_invocation": 0, "protected_effect": 0,
        },
        "reducers": {
            "authoritative_gy_status": "VERIFIED",
            "authoritative_gy_verdict": reducer_result,
            "authoritative_gy_input_identity": "OBSERVED_HM_REQUEST_COUNT_0_COUNTER_REDUCTION",
            "independent_status": "VERIFIED",
            "independent_verdict": "FAIL_CLOSED__WRONG_INPUT_OPERATIONAL_ACCEPTANCE_NOT_PROVEN",
            "agreement": "VERIFIED__NOT_ACCEPTED__E05_CREDIT_0",
        },
        "e05": {"before": "7/18", "after": "7/18", "credit": 0},
        "proof_reuse": {"ex_reused": "17/17", "ex_reconstructed": 0},
        "reuse_impact": {
            "existing_capabilities_reused": "HL_GY_HA_HG_HK_FM_GN_GL_DU_EB_EE_P11_CHE_FK_EX",
            "new_capabilities_created": "NONE__HM_OPERATIONAL_EVIDENCE_ONLY",
            "existing_capability_unreachable": False,
            "parallel_flow_created": False,
            "production_route_before": 1,
            "production_route_after": 1,
            "production_route_delta": 0,
        },
        "evidence": {
            "final_execution_seal_sha256": json.loads(FINAL_SEAL.read_bytes())["seal_sha256"],
            "independent_reduction_file_sha256": sha256(INDEPENDENT),
            "host_pre_teardown_checkpoint_sha256": json.loads(PRE_TEARDOWN.read_bytes())["checkpoint_sha256"],
            "host_teardown_checkpoint_sha256": json.loads(TEARDOWN.read_bytes())["checkpoint_sha256"],
            "serial_sha256": sha256(SERIAL),
            "pre_receipt_sha256": sha256(PRE_RECEIPT),
            "post_receipt_sha256": sha256(POST_RECEIPT),
            "raw_evidence_sha256": sha256(RAW),
        },
        "last_verified_edge": LAST_EDGE,
        "first_broken_edge": BROKEN_EDGE,
        "minimum_missing_capability": MISSING,
        "minimum_legal_next_development_delta": NEXT_DELTA,
        "terminal_control": {
            "verdict": VERDICT,
            "auto_continuable": False,
            "human_review_required": True,
            "next_generation_started": False,
        },
        "recorded_at_utc": now(),
    }
    write_new(TERMINAL, seal(
        "G77_256HM_SPCE_TERMINAL_REDUCTION_ENVELOPE_V1", "reduction", terminal
    ))
    print(json.dumps({
        "result": VERDICT,
        "serial_sha256": sha256(SERIAL),
        "authoritative_reducer": reducer_result,
        "transient_root_absent": not TRANSIENT.exists(),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
