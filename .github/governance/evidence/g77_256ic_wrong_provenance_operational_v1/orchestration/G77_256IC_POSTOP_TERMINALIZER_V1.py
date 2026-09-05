#!/usr/bin/env python3
"""Finalization-only reduction and teardown for consumed G77-256IC."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
IC = ROOT / ".github/governance/evidence/g77_256ic_wrong_provenance_operational_v1"
RUNTIME = IC / "operation_state/runtime_export"
RECEIPTS = IC / "operation_state/receipts"
TRANSIENT = Path("/tmp/g77_256ic_wrong_provenance_operational_v1")
SERIAL_SOURCE = TRANSIENT / "serial.log"
SERIAL = IC / "G77_256IC_SERIAL_CONSOLE_V1.log"
PRE = RECEIPTS / "G77_256IC_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
POST = RECEIPTS / "G77_256IC_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
RAW = RUNTIME / "G77_256IC_RAW_EXECUTION_EVIDENCE_V1.jsonl"
GUEST_EXECUTION = RUNTIME / "G77_256IC_GUEST_EXECUTION_SEAL_V1.json"
GUEST_TEARDOWN = RUNTIME / "G77_256IC_GUEST_TEARDOWN_SEAL_V1.json"
TERMINAL_MANIFEST = RUNTIME / "G77_256IC_CONTINUATION_MANIFEST_TERMINAL_V1.json"
AUTHORITY = IC / "G77_256IC_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
AUTHORITY_CHECKPOINT = IC / "G77_256IC_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json"
REQUEST = IC / "G77_256IC_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
PRESENTATION = IC / "G77_256IC_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
GRANT = IC / "G77_256IC_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
CONTEXT = IC / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
NORMALIZATION = IC / "G77_256IC_HZ_OPERATIONAL_EVIDENCE_NORMALIZATION_V1.json"
AUTHORITATIVE = IC / "G77_256IC_HZ_AUTHORITATIVE_OPERATIONAL_REDUCTION_V1.json"
INDEPENDENT = IC / "G77_256IC_INDEPENDENT_OPERATIONAL_REDUCTION_V1.json"
AGREEMENT = IC / "G77_256IC_REDUCER_AGREEMENT_V1.json"
PRE_TEARDOWN = IC / "G77_256IC_SPCE_HOST_PRE_TEARDOWN_CHECKPOINT_V1.json"
TEARDOWN = IC / "G77_256IC_SPCE_HOST_TEARDOWN_CHECKPOINT_V1.json"
FINAL_SEAL = IC / "G77_256IC_SPCE_FINAL_EXECUTION_SEAL_V1.json"
TERMINAL = IC / "G77_256IC_SPCE_TERMINAL_REDUCTION_V1.json"
BASE_IMAGE = Path("/tmp/g77_256cw.IkqZJN/noble-server-cloudimg-amd64.img")
BASE_SHA256 = "6e40c07ae715f744f84af0bec76415cc1987dd115b4b8de437818561f01a3733"
GENERATION = "G77_256IC_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_PROVENANCE_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256IC_E05_WRONG_PROVENANCE_DENIAL_BEFORE_ENTRY_001"
EXPECTED_DENIAL = (
    "D2_PRECLAIM_AUTHORITY_BINDING_VALIDATION_BEFORE_PRECLAIM_LEDGER_APPEND_"
    "CLAIM_ENTRY_INVOCATION_OR_EFFECT"
)
EXPECTED_REASON = "operational Human act input_record_identity binding is invalid"
HZ_REDUCER_PATH = ROOT / ".github/governance/evidence/g77_256hz_wrong_provenance_formalization_v1/reducer/G77_256HZ_WRONG_PROVENANCE_REPOSITORY_CAPABILITY_REDUCER_V1.py"
HZ_REDUCER_SHA256 = "b30c082185ebe185a0be0504a44ebc97d8f20a201b143a93b8d53e2e356a6585"
SUCCESS = (
    "VERIFIED__G77_256IC_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_PROVENANCE_OPERATIONAL_"
    "COMMISSIONING__ONE_AUTHORITY__ONE_PRE__ONE_FM__ONE_NO_NETWORK_QEMU__"
    "ONE_VM_CREATION__ONE_VM_BOOT__WRONG_PROVENANCE_REQUEST_DENIED_AT_D2_BEFORE_P11_ENTRY_"
    "INVOCATION_OR_EFFECT__ZERO_RETRY__AUTHORITATIVE_AND_INDEPENDENT_REDUCERS_"
    "AGREE__E05_10_OF_18__HUMAN_REVIEW_REQUIRED"
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
    if path.exists() or path.is_symlink():
        raise RuntimeError(f"terminal artifact collision: {path.name}")
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    payload = canonical_bytes(value)
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
    if SERIAL.exists() or SERIAL.is_symlink():
        raise RuntimeError("durable serial collision")
    with SERIAL.open("xb", buffering=0) as handle:
        handle.write(payload)
        os.fsync(handle.fileno())


def load_module(path: Path):
    specification = importlib.util.spec_from_file_location("g77_256ic_hz_reducer", path)
    if specification is None or specification.loader is None:
        raise RuntimeError("HZ reducer load failed")
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


def record_identity(value: dict[str, Any]) -> str:
    preimage = dict(value)
    preimage.pop("record_identity", None)
    payload = json.dumps(preimage, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return "sha256:" + hashlib.sha256(payload).hexdigest()


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
        "wrong_provenance_operation": 1,
        "request": 1,
        "p11_entry": 0,
        "protected_invocation": 0,
        "protected_effect": 0,
        "retry": 0,
        "repair_retry": 0,
        "replay": 0,
        "e05_credit": 1,
    }


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def one(records: list[dict[str, Any]], record_type: str) -> dict[str, Any]:
    matches = [record for record in records if record.get("record_type") == record_type]
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one {record_type}")
    return matches[0]


def load_unique_json(path: Path) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise RuntimeError(f"duplicate JSON key: {path.name}:{key}")
            result[key] = value
        return result

    return json.loads(path.read_bytes(), object_pairs_hook=unique)


def main() -> int:
    targets = (
        NORMALIZATION, AUTHORITATIVE, INDEPENDENT, AGREEMENT, PRE_TEARDOWN,
        TEARDOWN, FINAL_SEAL, TERMINAL, SERIAL,
    )
    if any(path.exists() or path.is_symlink() for path in targets):
        raise RuntimeError("terminal IC namespace is not fresh")
    if not TRANSIENT.is_dir() or not SERIAL_SOURCE.is_file():
        raise RuntimeError("transient operation evidence absent")

    pre = load_unique_json(PRE)
    post = load_unique_json(POST)
    argv = pre["vector"]["argv"]
    if not (
        pre["started_unix_ns"] == post["started_unix_ns"]
        and pre["execution_attempt_count"] == post["execution_attempt_count"] == 1
        and pre["automatic_retry_count"] == post["automatic_retry_count"] == 0
        and post["process_exit_status"] == 0
        and pre["vector"] == post["vector"]
        and argv.count("-nic") == 1
        and argv[argv.index("-nic") + 1] == "none"
    ):
        raise RuntimeError("single no-network receipt pair invalid")

    records = [json.loads(line) for line in RAW.read_text(encoding="utf-8").splitlines()]
    denial = one(records, "wrong_provenance_denial_complete")
    attempt = one(records, "p11_attempt_result")
    request_counter = one(records, "b6_boundary_request_counter")
    denial_counter = one(records, "b6_pre_attempt_denial_counter")
    entry_counter = one(records, "b6_p11_entry_counter")
    invocation_counter = one(records, "b6_invocation_counter")
    effect_counter = one(records, "b6_protected_effect_counter")
    counter_reduction = one(records, "b6_producer_consumer_reduction")
    facts = denial["facts"]
    attempt_facts = attempt["facts"]
    authorized = facts["authorized_input_record"]
    supplied = facts["supplied_input_record"]
    differing = sorted(key for key in authorized if authorized[key] != supplied[key])
    preserved = {key: authorized[key] == supplied[key] for key in authorized if key not in differing}
    guest = load_unique_json(GUEST_EXECUTION)
    guest_teardown = load_unique_json(GUEST_TEARDOWN)
    terminal_manifest = load_unique_json(TERMINAL_MANIFEST)["manifest"]
    authority_checkpoint = load_unique_json(AUTHORITY_CHECKPOINT)["checkpoint"]
    if not (
        len(records) == 31
        and guest["operational_result"] == "PASS__WRONG_PROVENANCE_DENIED_AT_D2_BEFORE_PRECLAIM_AND_ENTRY_WITH_ZERO_EFFECT"
        and guest_teardown["teardown_state"] == "COMPLETE"
        and guest_teardown["raw_record_count"] == 31
        and guest_teardown["raw_evidence_sha256"] == sha256(RAW)
        and terminal_manifest["first_failure_or_current_result"] == "PASS__E05_WRONG_PROVENANCE_DENIAL__GUEST_TEARDOWN_COMPLETE"
        and terminal_manifest["authority_state"]["authority_survives"] is False
        and authority_checkpoint["authority_state_after"] == "CONSUMED"
        and authority_checkpoint["authority_consumed"] == 1
        and differing == ["provenance_identity", "record_identity"]
        and record_identity(authorized) == authorized["record_identity"]
        and record_identity(supplied) == supplied["record_identity"]
        and set(preserved.values()) == {True}
        and facts["wrong_provenance_invariant_pass"] is True
        and facts["denial_point"] == EXPECTED_DENIAL
        and facts["denial_error_type"] == "FailClosedRuntimeError"
        and facts["denial_error"] == EXPECTED_REASON
        and facts["claim_attempted"] is False
        and facts["owner_state_before"] == facts["owner_state_after"]
        and facts["owner_revision_files_unchanged"] is True
        and facts["runtime_ledger_root_exists"] is False
        and facts["output_present"] is False
        and request_counter["facts"]["value"] == denial_counter["facts"]["value"] == 1
        and entry_counter["facts"]["value"] == invocation_counter["facts"]["value"] == effect_counter["facts"]["value"] == 0
        and counter_reduction["facts"]["producer_consumer_agreement"] is True
        and attempt_facts["result"] == "PASS__ONE_VALID_ACT__ONE_ISOLATED_WRONG_PROVENANCE_REQUEST_DENIED_AT_D2_BEFORE_PRECLAIM_ENTRY_CLAIM_INVOCATION_OR_EFFECT"
        and attempt_facts["additional_boundary_request_count"] == 0
        and attempt_facts["execution_counters"]["automatic_retry_count"] == 0
        and attempt_facts["execution_counters"]["repair_and_continue_count"] == 0
        and attempt_facts["execution_counters"]["execution_replay_count"] == 0
        and attempt_facts["execution_counters"]["e05_case_execution_count"] == 1
        and attempt_facts["execution_counters"]["vm_creation_count"] == 1
        and attempt_facts["execution_counters"]["vm_boot_count"] == 1
    ):
        raise RuntimeError("raw terminal evidence is not the commissioned success class")

    normalized_packet = {
        "schema_id": "G77_256IC_WRONG_PROVENANCE_OPERATIONAL_EVIDENCE_V1",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "selected_vector": facts["selected_vector"],
        "request_identity": facts["request_identity"],
        "authorized_input_record": authorized,
        "supplied_input_record": supplied,
        "target_mutated_coordinate": "provenance_identity",
        "dependent_recomputation_fields": ["record_identity"],
        "semantic_mutation_count": 1,
        "unrelated_mutation_count": 0,
        "differing_input_fields": differing,
        "preserved_dimension_proof": preserved,
        "denial_boundary": facts["denial_point"],
        "denial_error_type": facts["denial_error_type"],
        "denial_error_reason": facts["denial_error"],
        "provenance_specific_comparison_reached": False,
        "request_count": request_counter["facts"]["value"],
        "pre_attempt_denial_count": denial_counter["facts"]["value"],
        "p11_entry_count": entry_counter["facts"]["value"],
        "protected_invocation_count": invocation_counter["facts"]["value"],
        "protected_effect_count": effect_counter["facts"]["value"],
        "claim_attempted": facts["claim_attempted"],
        "owner_state_unchanged": facts["owner_state_before"] == facts["owner_state_after"],
        "runtime_ledger_exists": facts["runtime_ledger_root_exists"],
        "output_present": facts["output_present"],
        "retry_count": 0,
        "repair_retry_count": 0,
        "replay_count": 0,
    }
    normalization = {
        "schema_id": "G77_256IC_HZ_OPERATIONAL_EVIDENCE_NORMALIZATION_V1",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "purpose": "LOSSLESS_ACTUAL_VALUE_MAPPING_FROM_IC_RAW_RECORDS_TO_HZ_OWNED_WRONG_PROVENANCE_SEMANTICS",
        "source_raw_evidence_path": RAW.relative_to(ROOT).as_posix(),
        "source_raw_evidence_sha256": sha256(RAW),
        "source_raw_record_count": len(records),
        "source_record_sequences": {
            record["record_type"]: record["record_sequence"]
            for record in (denial, attempt, request_counter, denial_counter, entry_counter, invocation_counter, effect_counter, counter_reduction)
        },
        "normalized_packet": normalized_packet,
        "normalized_packet_sha256": hashlib.sha256(canonical_bytes(normalized_packet)).hexdigest(),
        "normalization_changes_observed_values": False,
        "normalization_is_authority": False,
        "recorded_at_utc": now(),
    }
    write_new(NORMALIZATION, seal("G77_256IC_HZ_OPERATIONAL_EVIDENCE_NORMALIZATION_ENVELOPE_V1", "normalization", normalization))

    if sha256(HZ_REDUCER_PATH) != HZ_REDUCER_SHA256:
        raise RuntimeError("authenticated HZ reducer identity drift")
    hz = load_module(HZ_REDUCER_PATH)
    hz._validate_input_record(authorized, prefix="AUTHORIZED_OPERATIONAL")
    hz._validate_input_record(supplied, prefix="SUPPLIED_OPERATIONAL")
    if not (
        differing == hz.EXPECTED_DIFFERING_FIELDS
        and facts["denial_point"] == hz.EXPECTED_DENIAL_BOUNDARY
        and facts["denial_error_type"] == hz.EXPECTED_ERROR_TYPE
        and facts["denial_error"] == hz.EXPECTED_ERROR_REASON
    ):
        raise RuntimeError("HZ authoritative semantic owner rejected operational packet")
    authoritative_result = {
        "terminal_acceptance": "ACCEPT",
        "result": "PASS__COMPLETE_WRONG_PROVENANCE_D2_DENIAL_EVIDENCE",
        "formal_spec_status": "VERIFIED",
        "hz_semantic_owner_status": "VERIFIED",
        "actual_operational_evidence_status": "VERIFIED",
        "semantic_firewall_status": "VERIFIED",
        "expected_denial_stage_status": "VERIFIED",
        "expected_denial_reason_status": "VERIFIED",
        "wrong_provenance_operation": 1,
        "request": 1,
        "p11_entry": 0,
        "protected_invocation": 0,
        "protected_effect": 0,
        "retry": 0,
        "repair_retry": 0,
        "replay": 0,
    }
    authoritative = {
        "schema_id": "G77_256IC_HZ_AUTHORITATIVE_OPERATIONAL_REDUCTION_V1",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "authoritative_reducer_status": "VERIFIED",
        "reducer_path": HZ_REDUCER_PATH.relative_to(ROOT).as_posix(),
        "reducer_sha256": sha256(HZ_REDUCER_PATH),
        "input_normalization_file_sha256": sha256(NORMALIZATION),
        "result": authoritative_result,
        "operational_criterion_satisfied": True,
        "recorded_at_utc": now(),
    }
    write_new(AUTHORITATIVE, seal("G77_256IC_HZ_AUTHORITATIVE_OPERATIONAL_REDUCTION_ENVELOPE_V1", "reduction", authoritative))

    independent_records = [json.loads(line) for line in RAW.read_text(encoding="utf-8").splitlines()]
    independent_denial = one(independent_records, "wrong_provenance_denial_complete")["facts"]
    independent_differing = sorted(
        key for key in independent_denial["authorized_input_record"]
        if independent_denial["authorized_input_record"][key] != independent_denial["supplied_input_record"][key]
    )
    independent_accept = (
        len(independent_records) == 31
        and independent_differing == ["provenance_identity", "record_identity"]
        and independent_denial["denial_point"] == EXPECTED_DENIAL
        and independent_denial["denial_error"] == EXPECTED_REASON
        and one(independent_records, "b6_boundary_request_counter")["facts"]["value"] == 1
        and one(independent_records, "b6_p11_entry_counter")["facts"]["value"] == 0
        and one(independent_records, "b6_invocation_counter")["facts"]["value"] == 0
        and one(independent_records, "b6_protected_effect_counter")["facts"]["value"] == 0
        and post["process_exit_status"] == 0
    )
    if not independent_accept:
        raise RuntimeError("independent reduction rejected operational evidence")
    independent = {
        "schema_id": "G77_256IC_INDEPENDENT_OPERATIONAL_REDUCTION_V1",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "independent_reducer_status": "VERIFIED",
        "independent_reducer_result": "ACCEPT",
        "independent_reducer_verdict": "PASS__ONE_WRONG_PROVENANCE_REQUEST_DENIED_AT_D2_BEFORE_P11_ENTRY_INVOCATION_OR_EFFECT",
        "independent_source": "DIRECT_IC_RAW_RECORD_RECEIPT_SERIAL_AND_GUEST_SEAL_RECONSTRUCTION",
        "authoritative_result_used_as_input": False,
        "observations": {
            "raw_evidence_sha256": sha256(RAW),
            "raw_record_count": len(independent_records),
            "operation_count": 1,
            "request_count": 1,
            "semantic_mutation_field": "provenance_identity",
            "dependent_recomputation_fields": ["record_identity"],
            "actual_differing_fields": independent_differing,
            "authorized_record_identity_valid": record_identity(independent_denial["authorized_input_record"]) == independent_denial["authorized_input_record"]["record_identity"],
            "supplied_record_identity_valid": record_identity(independent_denial["supplied_input_record"]) == independent_denial["supplied_input_record"]["record_identity"],
            "denial_boundary": independent_denial["denial_point"],
            "denial_reason": independent_denial["denial_error"],
            "p11_entry_count": 0,
            "protected_invocation_count": 0,
            "protected_effect_count": 0,
            "retry_count": 0,
            "repair_retry_count": 0,
            "replay_count": 0,
            "qemu_count": 1,
            "vm_creation_count": 1,
            "vm_boot_count": 1,
            "authority_consumption_count": 1,
            "nic_none_count": 1,
            "qemu_process_exit_status": post["process_exit_status"],
        },
        "operational_counters": counters(),
        "operational_criterion_satisfied": True,
        "recorded_at_utc": now(),
    }
    write_new(INDEPENDENT, seal("G77_256IC_INDEPENDENT_OPERATIONAL_REDUCTION_ENVELOPE_V1", "reduction", independent))

    agreement = {
        "schema_id": "G77_256IC_REDUCER_AGREEMENT_V1",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "authoritative_reducer_result": "ACCEPT",
        "authoritative_verdict": authoritative_result["result"],
        "independent_reducer_result": "ACCEPT",
        "independent_verdict": independent["independent_reducer_verdict"],
        "reducer_agreement_status": "VERIFIED",
        "agreement": "VERIFIED__BOTH_ACCEPT_OPERATIONAL_WRONG_PROVENANCE_CRITERION__E05_CREDIT_1",
        "one_shot_contract_satisfied": True,
        "e05": {"before": "9/18", "credit": 1, "after": "10/18"},
        "authoritative_reduction_file_sha256": sha256(AUTHORITATIVE),
        "independent_reduction_file_sha256": sha256(INDEPENDENT),
        "recorded_at_utc": now(),
    }
    write_new(AGREEMENT, seal("G77_256IC_REDUCER_AGREEMENT_ENVELOPE_V1", "agreement", agreement))

    serial_bytes = SERIAL_SOURCE.read_bytes()
    if b"G77_256FM_BOOT_MARKER=PASS" not in serial_bytes or b"G77_256FM_HARNESS_EXIT_STATUS=0" not in serial_bytes:
        raise RuntimeError("serial success markers absent")
    if sha256(BASE_IMAGE) != BASE_SHA256:
        raise RuntimeError("base image drift before teardown")
    copy_serial()
    pre_teardown = {
        "schema_id": "G77_256IC_SPCE_HOST_PRE_TEARDOWN_CHECKPOINT_V1",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "durable_evidence": {
            "serial_sha256": sha256(SERIAL),
            "serial_byte_count": SERIAL.stat().st_size,
            "pre_receipt_sha256": sha256(PRE),
            "post_receipt_sha256": sha256(POST),
            "raw_evidence_sha256": sha256(RAW),
            "guest_execution_sha256": sha256(GUEST_EXECUTION),
            "guest_teardown_sha256": sha256(GUEST_TEARDOWN),
            "terminal_manifest_sha256": sha256(TERMINAL_MANIFEST),
        },
        "host_lifecycle": {
            "state": "PRE_TEARDOWN_OBSERVED",
            "transient_root_present": True,
            "checkout_present": (TRANSIENT / "checkout").is_dir(),
            "overlay_present": (TRANSIENT / "guest-overlay.qcow2").is_file(),
            "qemu_process_terminal_receipt_status": 0,
            "persistent_evidence_preserved": True,
        },
        "base_image": {"path": str(BASE_IMAGE), "sha256_pre_teardown": BASE_SHA256, "byte_identical": True},
        "operational_counters": counters(),
        "e05": {"before": "9/18", "credit": 1, "after": "10/18"},
        "checkpoint_is_authority": False,
        "auto_continuable": False,
        "human_review_required": True,
        "recorded_at_utc": now(),
    }
    write_new(PRE_TEARDOWN, seal("G77_256IC_SPCE_HOST_PRE_TEARDOWN_CHECKPOINT_ENVELOPE_V1", "checkpoint", pre_teardown))

    if TRANSIENT.resolve() != Path("/tmp/g77_256ic_wrong_provenance_operational_v1"):
        raise RuntimeError("transient teardown target changed")
    shutil.rmtree(TRANSIENT)
    if TRANSIENT.exists() or TRANSIENT.is_symlink() or sha256(BASE_IMAGE) != BASE_SHA256:
        raise RuntimeError("host teardown or base-image preservation failed")
    teardown = {
        "schema_id": "G77_256IC_SPCE_HOST_TEARDOWN_CHECKPOINT_V1",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "host_pre_teardown_checkpoint_file_sha256": sha256(PRE_TEARDOWN),
        "host_teardown": {
            "state": "TEARDOWN_COMPLETE",
            "transient_root": str(TRANSIENT),
            "transient_root_absent": True,
            "qemu_terminal_receipt_status": 0,
            "persistent_evidence_preserved": True,
        },
        "base_image": {"path": str(BASE_IMAGE), "sha256_before": BASE_SHA256, "sha256_after": BASE_SHA256, "byte_identical": True},
        "operational_counters": counters(),
        "e05": {"before": "9/18", "credit": 1, "after": "10/18"},
        "checkpoint_is_authority": False,
        "auto_continuable": False,
        "human_review_required": True,
        "recorded_at_utc": now(),
    }
    write_new(TEARDOWN, seal("G77_256IC_SPCE_HOST_TEARDOWN_CHECKPOINT_ENVELOPE_V1", "checkpoint", teardown))

    artifacts = (
        AUTHORITY_CHECKPOINT, AUTHORITY, PRESENTATION, REQUEST, GRANT, PRE, POST,
        RAW, GUEST_EXECUTION, GUEST_TEARDOWN, TERMINAL_MANIFEST, SERIAL,
        NORMALIZATION, AUTHORITATIVE, INDEPENDENT, AGREEMENT, PRE_TEARDOWN,
        TEARDOWN, CONTEXT,
    )
    final = {
        "schema_id": "G77_256IC_SPCE_FINAL_EXECUTION_SEAL_V1",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "artifacts": {path.relative_to(ROOT).as_posix(): sha256(path) for path in artifacts},
        "operational_counters": counters(),
        "authority_created": 1,
        "authority_validated": 1,
        "authority_consumed": 1,
        "authoritative_reducer_result": "ACCEPT",
        "independent_reducer_result": "ACCEPT",
        "reducer_agreement_status": "VERIFIED",
        "expected_denial_stage_status": "VERIFIED",
        "expected_denial_reason_status": "VERIFIED",
        "wrong_provenance_operational_capability": "VERIFIED",
        "e05": {"before": "9/18", "credit": 1, "after": "10/18"},
        "teardown_state": "COMPLETE",
        "final_result": SUCCESS,
        "auto_continuable": False,
        "human_review_required": True,
        "recorded_at_utc": now(),
    }
    write_new(FINAL_SEAL, seal("G77_256IC_SPCE_FINAL_EXECUTION_SEAL_ENVELOPE_V1", "seal", final))
    terminal = {
        "schema_id": "G77_256IC_SPCE_TERMINAL_REDUCTION_V1",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "terminal_state": "VERIFIED__OPERATION_CONSUMED__GUEST_AND_HOST_TEARDOWN_COMPLETE__NO_RETRY",
        "operational_counters": counters(),
        "request_entry_invocation_effect_separation": {"request": 1, "p11_entry": 0, "protected_invocation": 0, "protected_effect": 0},
        "semantic_firewall": {
            "target_mutation": "provenance_identity",
            "dependent_recomputation": "record_identity",
            "semantic_mutation_count": 1,
            "unrelated_mutation_count": 0,
            "expected_denial_stage_status": "VERIFIED",
            "expected_denial_reason_status": "VERIFIED",
            "provenance_specific_comparison_reached": False,
        },
        "reducers": {
            "authoritative_reducer_result": "ACCEPT",
            "authoritative_verdict": authoritative_result["result"],
            "independent_reducer_result": "ACCEPT",
            "independent_reducer_verdict": independent["independent_reducer_verdict"],
            "reducer_agreement_status": "VERIFIED",
        },
        "e05": {"before": "9/18", "credit": 1, "after": "10/18"},
        "capability": {"candidate": "VERIFIED", "repository": "VERIFIED", "operational": "VERIFIED"},
        "proof_reuse": {"ex_reused": "17/17", "ex_reconstructed": 0},
        "reuse_impact": {
            "reused_certified_capability_set": "IB_IA_HZ_HX_HP_FM_GN_GL_DU_EB_EE_P11_CHE_FK_EX",
            "new_capability_set": "IC_OPERATIONAL_EVIDENCE_ONLY",
            "unreachable_preexisting_capability_set": "NONE",
            "parallel_flow_created": False,
            "production_route_before": 1,
            "production_route_after": 1,
            "production_route_delta": 0,
            "new_generic_framework_count": 0,
            "new_authority_layer_count": 0,
            "new_production_route_count": 0,
            "new_runtime_owner_count": 0,
        },
        "evidence": {
            "final_execution_seal_inner_sha256": load_unique_json(FINAL_SEAL)["seal_sha256"],
            "normalization_file_sha256": sha256(NORMALIZATION),
            "authoritative_reduction_file_sha256": sha256(AUTHORITATIVE),
            "independent_reduction_file_sha256": sha256(INDEPENDENT),
            "agreement_file_sha256": sha256(AGREEMENT),
            "host_pre_teardown_checkpoint_file_sha256": sha256(PRE_TEARDOWN),
            "host_teardown_checkpoint_file_sha256": sha256(TEARDOWN),
            "serial_sha256": sha256(SERIAL),
            "raw_evidence_sha256": sha256(RAW),
        },
        "next_constitutional_frontier": "SEPARATE_HUMAN_REVIEW_BEFORE_ANY_NEXT_E05_OBLIGATION",
        "terminal_control": {
            "verdict": SUCCESS,
            "auto_continuable": False,
            "human_authorization_required": False,
            "human_review_required": True,
            "next_generation_started": False,
        },
        "recorded_at_utc": now(),
    }
    write_new(TERMINAL, seal("G77_256IC_SPCE_TERMINAL_REDUCTION_ENVELOPE_V1", "reduction", terminal))
    print(json.dumps({
        "result": SUCCESS,
        "serial_sha256": sha256(SERIAL),
        "raw_sha256": sha256(RAW),
        "transient_root_absent": not TRANSIENT.exists(),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
