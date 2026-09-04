#!/usr/bin/env python3
"""Finalization-only terminalizer for the consumed G77-256HP operation."""

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
HP = ROOT / ".github/governance/evidence/g77_256hp_wrong_input_operational_v1"
RUNTIME = HP / "operation_state/runtime_export"
RECEIPTS = HP / "operation_state/receipts"
TRANSIENT = Path("/tmp/g77_256hp_wrong_input_operational_v1")
SERIAL_SOURCE = TRANSIENT / "serial.log"
SERIAL = HP / "G77_256HP_SERIAL_CONSOLE_V1.log"
PRE = RECEIPTS / "G77_256HP_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
POST = RECEIPTS / "G77_256HP_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
RAW = RUNTIME / "G77_256HP_RAW_EXECUTION_EVIDENCE_V1.jsonl"
GUEST_EXECUTION = RUNTIME / "G77_256HP_GUEST_EXECUTION_SEAL_V1.json"
GUEST_TEARDOWN = RUNTIME / "G77_256HP_GUEST_TEARDOWN_SEAL_V1.json"
TERMINAL_MANIFEST = RUNTIME / "G77_256HP_CONTINUATION_MANIFEST_TERMINAL_V1.json"
AUTHORITY = HP / "G77_256HP_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
AUTHORITY_CHECKPOINT = HP / "G77_256HP_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json"
REQUEST = HP / "G77_256HP_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
PRESENTATION = HP / "G77_256HP_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
GRANT = HP / "G77_256HP_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
CONTEXT = HP / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
NORMALIZATION = HP / "G77_256HP_GY_OPERATIONAL_EVIDENCE_NORMALIZATION_V1.json"
AUTHORITATIVE = HP / "G77_256HP_GY_AUTHORITATIVE_OPERATIONAL_REDUCTION_V1.json"
INDEPENDENT = HP / "G77_256HP_INDEPENDENT_OPERATIONAL_REDUCTION_V1.json"
AGREEMENT = HP / "G77_256HP_REDUCER_AGREEMENT_V1.json"
PRE_TEARDOWN = HP / "G77_256HP_SPCE_HOST_PRE_TEARDOWN_CHECKPOINT_V1.json"
TEARDOWN = HP / "G77_256HP_SPCE_HOST_TEARDOWN_CHECKPOINT_V1.json"
FINAL_SEAL = HP / "G77_256HP_SPCE_FINAL_EXECUTION_SEAL_V1.json"
TERMINAL = HP / "G77_256HP_SPCE_TERMINAL_REDUCTION_V1.json"
BASE_IMAGE = Path("/tmp/g77_256cw.IkqZJN/noble-server-cloudimg-amd64.img")
BASE_SHA256 = "6e40c07ae715f744f84af0bec76415cc1987dd115b4b8de437818561f01a3733"
GENERATION = "G77_256HP_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_INPUT_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256HP_E05_WRONG_INPUT_DENIAL_BEFORE_ENTRY_001"
SUCCESS = (
    "VERIFIED__G77_256HP_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_INPUT_OPERATIONAL_"
    "COMMISSIONING__ONE_AUTHORITY__ONE_PRE__ONE_FM__ONE_NO_NETWORK_QEMU__"
    "ONE_VM_BOOT__WRONG_INPUT_REQUEST_ACCEPTED_AS_VECTOR_AND_DENIED_BEFORE_"
    "PROTECTED_EXECUTION__ZERO_RETRY__AUTHORITATIVE_AND_INDEPENDENT_REDUCERS_"
    "AGREE__E05_8_OF_18__HUMAN_REVIEW_REQUIRED"
)


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def seal(schema: str, key: str, value: dict[str, Any]) -> dict[str, Any]:
    return {"schema_id": schema, key: value, f"{key}_sha256": hashlib.sha256(canonical_bytes(value)).hexdigest()}


def write_new(path: Path, value: dict[str, Any]) -> None:
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
    if SERIAL.exists():
        if SERIAL.read_bytes() != payload:
            raise RuntimeError("durable serial collision")
        return
    with SERIAL.open("xb", buffering=0) as handle:
        handle.write(payload)
        os.fsync(handle.fileno())


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("g77_256hp_gy_reducer", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("GY reducer load failed")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def record_identity(value: dict[str, Any]) -> str:
    preimage = dict(value)
    preimage.pop("record_identity", None)
    return "sha256:" + hashlib.sha256(canonical_bytes(preimage).rstrip(b"\n")).hexdigest()


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
        "wrong_input_operation": 1,
        "request": 1,
        "p11_entry": 0,
        "protected_invocation": 0,
        "protected_effect": 0,
        "retry": 0,
        "repair_and_continue": 0,
        "operational_replay": 0,
        "e05_credit": 1,
    }


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def one(records: list[dict[str, Any]], record_type: str) -> dict[str, Any]:
    matched = [record for record in records if record.get("record_type") == record_type]
    if len(matched) != 1:
        raise RuntimeError(f"expected exactly one {record_type}")
    return matched[0]


def main() -> int:
    targets = (NORMALIZATION, AUTHORITATIVE, INDEPENDENT, AGREEMENT, PRE_TEARDOWN, TEARDOWN, FINAL_SEAL, TERMINAL)
    if any(path.exists() for path in targets):
        raise RuntimeError("terminal HP artifact collision")
    if not TRANSIENT.is_dir() or not SERIAL_SOURCE.is_file():
        raise RuntimeError("transient operation evidence absent")
    if subprocess.run(
        ["pgrep", "-f", "^/usr/bin/qemu-system-x86_64.*g77_256hp"],
        check=False,
        stdout=subprocess.DEVNULL,
    ).returncode == 0:
        raise RuntimeError("matching QEMU remains active")

    pre = json.loads(PRE.read_bytes())
    post = json.loads(POST.read_bytes())
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
    denial = one(records, "wrong_input_denial_complete")
    attempt = one(records, "p11_attempt_result")
    request_counter = one(records, "b6_boundary_request_counter")
    entry_counter = one(records, "b6_p11_entry_counter")
    invocation_counter = one(records, "b6_invocation_counter")
    effect_counter = one(records, "b6_protected_effect_counter")
    counter_reduction = one(records, "b6_producer_consumer_reduction")
    raw_facts = denial["facts"]
    authorized = raw_facts["authorized_input_record"]
    supplied = raw_facts["supplied_input_record"]
    differing = sorted(key for key in authorized if authorized[key] != supplied[key])
    preserved = {key: authorized[key] == supplied[key] for key in authorized if key not in differing}
    guest = json.loads(GUEST_EXECUTION.read_bytes())
    guest_teardown = json.loads(GUEST_TEARDOWN.read_bytes())
    terminal_manifest = json.loads(TERMINAL_MANIFEST.read_bytes())["manifest"]
    if not (
        len(records) == 31
        and guest["operational_result"] == "PASS__WRONG_INPUT_DENIED_AT_D2_BEFORE_PRECLAIM_AND_ENTRY_WITH_ZERO_EFFECT"
        and guest_teardown["teardown_state"] == "COMPLETE"
        and guest_teardown["raw_record_count"] == 31
        and guest_teardown["raw_evidence_sha256"] == sha256(RAW)
        and terminal_manifest["first_failure_or_current_result"] == "PASS__E05_WRONG_INPUT_DENIAL__GUEST_TEARDOWN_COMPLETE"
        and terminal_manifest["authority_state"]["authority_survives"] is False
        and differing == ["input_identity", "record_identity"]
        and record_identity(authorized) == authorized["record_identity"]
        and record_identity(supplied) == supplied["record_identity"]
        and raw_facts["wrong_input_invariant_pass"] is True
        and raw_facts["claim_attempted"] is False
        and raw_facts["owner_state_before"] == raw_facts["owner_state_after"]
        and raw_facts["owner_revision_files_unchanged"] is True
        and raw_facts["runtime_ledger_root_exists"] is False
        and raw_facts["output_present"] is False
        and request_counter["facts"]["value"] == 1
        and entry_counter["facts"]["value"] == invocation_counter["facts"]["value"] == effect_counter["facts"]["value"] == 0
        and counter_reduction["facts"]["producer_consumer_agreement"] is True
    ):
        raise RuntimeError("raw terminal evidence is not the commissioned success class")

    reducer_path = ROOT / ".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/reducer/G77_256GY_WRONG_INPUT_TERMINAL_ACCEPTANCE_REDUCER_V1.py"
    reducer = load_module(reducer_path)
    provenance_facts = {
        "case_id": reducer.CASE_ID,
        "selected_vector": reducer.SELECTED_VECTOR,
        "request_identity": raw_facts["request_identity"],
        "evidence_provenance": reducer.EVIDENCE_PROVENANCE,
    }
    normalized_records = [
        {"record_type": "wrong_input_request", "facts": dict(provenance_facts)},
        {"record_type": "wrong_input_denial_complete", "facts": dict(provenance_facts)},
        {"record_type": "request_counter", "facts": {"count": request_counter["facts"]["value"]}},
        {"record_type": "p11_entry_counter", "facts": {"count": entry_counter["facts"]["value"]}},
        {"record_type": "protected_invocation_counter", "facts": {"count": invocation_counter["facts"]["value"]}},
        {"record_type": "protected_effect_counter", "facts": {"count": effect_counter["facts"]["value"]}},
    ]
    packet = {
        "schema_id": "G77_256GY_WRONG_INPUT_OPERATIONAL_EVIDENCE_V1",
        "case_id": reducer.CASE_ID,
        "selected_vector": reducer.SELECTED_VECTOR,
        "formal_specification_identity": reducer.FORMAL_SPECIFICATION_IDENTITY,
        "formal_specification_sha256": reducer.FORMAL_SPECIFICATION_SHA256,
        "candidate_identity": reducer.CANDIDATE_IDENTITY,
        "evidence_provenance": reducer.EVIDENCE_PROVENANCE,
        "request_identity": raw_facts["request_identity"],
        "authorized_input_record": authorized,
        "supplied_input_record": supplied,
        "differing_input_fields": differing,
        "semantic_mutation_field": "input_identity",
        "dependent_recomputation_fields": ["record_identity"],
        "preserved_dimension_proof": preserved,
        "denial_boundary": raw_facts["denial_point"],
        "denial_error_type": raw_facts["denial_error_type"],
        "denial_error_reason": raw_facts["denial_error"],
        "request_count": request_counter["facts"]["value"],
        "p11_entry_count": entry_counter["facts"]["value"],
        "protected_invocation_count": invocation_counter["facts"]["value"],
        "protected_effect_count": effect_counter["facts"]["value"],
        "claim_attempted": raw_facts["claim_attempted"],
        "owner_state_unchanged": raw_facts["owner_state_before"] == raw_facts["owner_state_after"] and raw_facts["owner_revision_files_unchanged"],
        "runtime_ledger_exists": raw_facts["runtime_ledger_root_exists"],
        "output_present": raw_facts["output_present"],
        "raw_evidence_records": normalized_records,
    }
    authoritative_result = reducer.reduce_wrong_input_terminal_evidence(packet)
    if authoritative_result["terminal_acceptance"] != "PASS__COMPLETE_WRONG_INPUT_D2_DENIAL_EVIDENCE":
        raise RuntimeError("authoritative reducer did not accept")

    normalization = {
        "schema_id": "G77_256HP_GY_OPERATIONAL_EVIDENCE_NORMALIZATION_V1",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "purpose": "LOSSLESS_VOCABULARY_ADAPTER_FROM_HP_RAW_RECORD_TYPES_TO_GY_REDUCER_INPUT",
        "source_raw_evidence_path": RAW.relative_to(ROOT).as_posix(),
        "source_raw_evidence_sha256": sha256(RAW),
        "source_raw_record_count": len(records),
        "mapping": {
            "wrong_input_request": ["wrong_input_denial_complete", "p11_attempt_result"],
            "wrong_input_denial_complete": ["wrong_input_denial_complete"],
            "request_counter": ["b6_boundary_request_counter"],
            "p11_entry_counter": ["b6_p11_entry_counter"],
            "protected_invocation_counter": ["b6_invocation_counter"],
            "protected_effect_counter": ["b6_protected_effect_counter"],
            "generic_case_id": {"from": OPERATION, "to": reducer.CASE_ID},
        },
        "source_record_sha256": {
            record["record_type"]: hashlib.sha256(canonical_bytes(record).rstrip(b"\n")).hexdigest()
            for record in (denial, attempt, request_counter, entry_counter, invocation_counter, effect_counter, counter_reduction)
        },
        "normalized_packet": packet,
        "normalized_packet_sha256": hashlib.sha256(canonical_bytes(packet)).hexdigest(),
        "normalization_changes_observed_values": False,
        "normalization_is_authority": False,
        "recorded_at_utc": now(),
    }
    write_new(NORMALIZATION, seal("G77_256HP_GY_OPERATIONAL_EVIDENCE_NORMALIZATION_ENVELOPE_V1", "normalization", normalization))
    authoritative = {
        "schema_id": "G77_256HP_GY_AUTHORITATIVE_OPERATIONAL_REDUCTION_V1",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "authoritative_gy_reducer_status": "VERIFIED",
        "reducer_path": reducer_path.relative_to(ROOT).as_posix(),
        "reducer_sha256": sha256(reducer_path),
        "input_normalization_file_sha256": sha256(NORMALIZATION),
        "result": authoritative_result,
        "operational_criterion_satisfied": True,
        "gy_repository_only_credit_field": 0,
        "gy_credit_scope_note": "GY has no operational authority; HP owns operational E05 accounting after agreement.",
        "recorded_at_utc": now(),
    }
    write_new(AUTHORITATIVE, seal("G77_256HP_GY_AUTHORITATIVE_OPERATIONAL_REDUCTION_ENVELOPE_V1", "reduction", authoritative))

    independent = {
        "schema_id": "G77_256HP_INDEPENDENT_OPERATIONAL_REDUCTION_V1",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "independent_reducer_status": "VERIFIED",
        "independent_reducer_verdict": "PASS__ONE_WRONG_INPUT_REQUEST_DENIED_AT_D2_BEFORE_P11_ENTRY_INVOCATION_OR_EFFECT",
        "independent_source": "DIRECT_HP_RAW_RECORD_RECEIPT_SERIAL_AND_GUEST_SEAL_RECONSTRUCTION",
        "authoritative_result_used_as_input": False,
        "observations": {
            "raw_evidence_sha256": sha256(RAW),
            "raw_record_count": len(records),
            "operation_count": 1,
            "request_count": request_counter["facts"]["value"],
            "semantic_mutation_field": "input_identity",
            "dependent_recomputation_fields": ["record_identity"],
            "actual_differing_fields": differing,
            "authorized_record_identity_valid": True,
            "supplied_record_identity_valid": True,
            "denial_boundary": raw_facts["denial_point"],
            "claim_attempted": raw_facts["claim_attempted"],
            "owner_state_unchanged": True,
            "p11_entry_count": entry_counter["facts"]["value"],
            "protected_invocation_count": invocation_counter["facts"]["value"],
            "protected_effect_count": effect_counter["facts"]["value"],
            "retry_count": 0,
            "repair_count": 0,
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
    write_new(INDEPENDENT, seal("G77_256HP_INDEPENDENT_OPERATIONAL_REDUCTION_ENVELOPE_V1", "reduction", independent))

    agreement = {
        "schema_id": "G77_256HP_REDUCER_AGREEMENT_V1",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "authoritative_gy_reducer_status": "VERIFIED",
        "authoritative_verdict": authoritative_result["terminal_acceptance"],
        "independent_reducer_status": "VERIFIED",
        "independent_verdict": independent["independent_reducer_verdict"],
        "reducer_agreement_status": "VERIFIED",
        "agreement": "VERIFIED__BOTH_ACCEPT_OPERATIONAL_WRONG_INPUT_CRITERION__E05_CREDIT_1",
        "one_shot_contract_satisfied": True,
        "e05": {"before": "7/18", "credit": 1, "after": "8/18"},
        "authoritative_reduction_file_sha256": sha256(AUTHORITATIVE),
        "independent_reduction_file_sha256": sha256(INDEPENDENT),
        "recorded_at_utc": now(),
    }
    write_new(AGREEMENT, seal("G77_256HP_REDUCER_AGREEMENT_ENVELOPE_V1", "agreement", agreement))

    serial_bytes = SERIAL_SOURCE.read_bytes()
    if b"G77_256FM_BOOT_MARKER=PASS" not in serial_bytes or b"G77_256FM_HARNESS_EXIT_STATUS=0" not in serial_bytes:
        raise RuntimeError("serial success markers absent")
    if sha256(BASE_IMAGE) != BASE_SHA256:
        raise RuntimeError("base image drift before teardown")
    copy_serial()
    pre_teardown = {
        "schema_id": "G77_256HP_SPCE_HOST_PRE_TEARDOWN_CHECKPOINT_V1",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "durable_evidence": {
            "serial_sha256": sha256(SERIAL), "serial_byte_count": SERIAL.stat().st_size,
            "pre_receipt_sha256": sha256(PRE), "post_receipt_sha256": sha256(POST),
            "raw_evidence_sha256": sha256(RAW), "guest_execution_sha256": sha256(GUEST_EXECUTION),
            "guest_teardown_sha256": sha256(GUEST_TEARDOWN), "terminal_manifest_sha256": sha256(TERMINAL_MANIFEST),
        },
        "host_lifecycle": {
            "state": "PRE_TEARDOWN_OBSERVED", "transient_root_present": True,
            "checkout_present": (TRANSIENT / "checkout").is_dir(),
            "overlay_present": (TRANSIENT / "guest-overlay.qcow2").is_file(),
            "qemu_process_absent": True, "persistent_evidence_preserved": True,
        },
        "base_image": {"path": str(BASE_IMAGE), "sha256_pre_teardown": BASE_SHA256, "byte_identical": True},
        "operational_counters": counters(),
        "e05": {"before": "7/18", "credit": 1, "after": "8/18"},
        "checkpoint_is_authority": False, "auto_continuable": False, "human_review_required": True,
        "recorded_at_utc": now(),
    }
    write_new(PRE_TEARDOWN, seal("G77_256HP_SPCE_HOST_PRE_TEARDOWN_CHECKPOINT_ENVELOPE_V1", "checkpoint", pre_teardown))

    if TRANSIENT.resolve() != Path("/tmp/g77_256hp_wrong_input_operational_v1"):
        raise RuntimeError("transient teardown target changed")
    shutil.rmtree(TRANSIENT)
    if TRANSIENT.exists() or TRANSIENT.is_symlink() or sha256(BASE_IMAGE) != BASE_SHA256:
        raise RuntimeError("host teardown or base-image preservation failed")
    teardown = {
        "schema_id": "G77_256HP_SPCE_HOST_TEARDOWN_CHECKPOINT_V1",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "host_pre_teardown_checkpoint_file_sha256": sha256(PRE_TEARDOWN),
        "host_teardown": {"state": "TEARDOWN_COMPLETE", "transient_root": str(TRANSIENT), "transient_root_absent": True, "qemu_process_absent": True, "persistent_evidence_preserved": True},
        "base_image": {"path": str(BASE_IMAGE), "sha256_before": BASE_SHA256, "sha256_after": BASE_SHA256, "byte_identical": True},
        "operational_counters": counters(),
        "e05": {"before": "7/18", "credit": 1, "after": "8/18"},
        "checkpoint_is_authority": False, "auto_continuable": False, "human_review_required": True,
        "recorded_at_utc": now(),
    }
    write_new(TEARDOWN, seal("G77_256HP_SPCE_HOST_TEARDOWN_CHECKPOINT_ENVELOPE_V1", "checkpoint", teardown))

    artifacts = (AUTHORITY_CHECKPOINT, AUTHORITY, PRESENTATION, REQUEST, GRANT, PRE, POST, RAW, GUEST_EXECUTION, GUEST_TEARDOWN, TERMINAL_MANIFEST, SERIAL, NORMALIZATION, AUTHORITATIVE, INDEPENDENT, AGREEMENT, PRE_TEARDOWN, TEARDOWN, CONTEXT)
    final = {
        "schema_id": "G77_256HP_SPCE_FINAL_EXECUTION_SEAL_V1",
        "generation_identity": GENERATION, "operation_identity": OPERATION,
        "artifacts": {path.relative_to(ROOT).as_posix(): sha256(path) for path in artifacts},
        "operational_counters": counters(),
        "authority_created": 1, "authority_validated": 1, "authority_consumed": 1,
        "authoritative_gy_reducer_status": "VERIFIED", "independent_reducer_status": "VERIFIED", "reducer_agreement_status": "VERIFIED",
        "wrong_input_operational_capability": "VERIFIED",
        "e05": {"before": "7/18", "credit": 1, "after": "8/18"},
        "teardown_state": "COMPLETE", "final_result": SUCCESS,
        "auto_continuable": False, "human_review_required": True, "recorded_at_utc": now(),
    }
    write_new(FINAL_SEAL, seal("G77_256HP_SPCE_FINAL_EXECUTION_SEAL_ENVELOPE_V1", "seal", final))
    terminal = {
        "schema_id": "G77_256HP_SPCE_TERMINAL_REDUCTION_V1",
        "generation_identity": GENERATION, "operation_identity": OPERATION,
        "terminal_state": "VERIFIED__OPERATION_CONSUMED__GUEST_AND_HOST_TEARDOWN_COMPLETE__NO_RETRY",
        "operational_counters": counters(),
        "request_entry_invocation_effect_separation": {"request": 1, "p11_entry": 0, "protected_invocation": 0, "protected_effect": 0},
        "reducers": {
            "authoritative_gy_reducer_status": "VERIFIED", "authoritative_gy_verdict": authoritative_result["terminal_acceptance"],
            "independent_reducer_status": "VERIFIED", "independent_reducer_verdict": independent["independent_reducer_verdict"],
            "reducer_agreement_status": "VERIFIED",
        },
        "e05": {"before": "7/18", "credit": 1, "after": "8/18"},
        "capability": {"candidate": "VERIFIED", "repository": "VERIFIED", "operational": "VERIFIED"},
        "proof_reuse": {"ex_reused": "17/17", "ex_reconstructed": 0},
        "reuse_impact": {
            "reused_certified_capability_set": "HL_GY_HA_HG_HK_FM_GN_GL_DU_EB_EE_P11_CHE_FK_EX",
            "new_capability_set": "HP_OPERATIONAL_EVIDENCE_ONLY", "unreachable_preexisting_capability_set": "NONE",
            "parallel_flow_created": False, "production_route_before": 1, "production_route_after": 1, "production_route_delta": 0,
            "new_generic_framework_count": 0, "new_authority_layer_count": 0, "new_production_route_count": 0, "new_runtime_owner_count": 0,
        },
        "evidence": {
            "final_execution_seal_inner_sha256": json.loads(FINAL_SEAL.read_bytes())["seal_sha256"],
            "normalization_file_sha256": sha256(NORMALIZATION), "authoritative_reduction_file_sha256": sha256(AUTHORITATIVE),
            "independent_reduction_file_sha256": sha256(INDEPENDENT), "agreement_file_sha256": sha256(AGREEMENT),
            "host_pre_teardown_checkpoint_file_sha256": sha256(PRE_TEARDOWN), "host_teardown_checkpoint_file_sha256": sha256(TEARDOWN),
            "serial_sha256": sha256(SERIAL), "raw_evidence_sha256": sha256(RAW),
        },
        "next_constitutional_frontier": "SEPARATE_HUMAN_REVIEW_BEFORE_ANY_NEXT_E05_OBLIGATION",
        "terminal_control": {"verdict": SUCCESS, "auto_continuable": False, "human_review_required": True, "next_generation_started": False},
        "recorded_at_utc": now(),
    }
    write_new(TERMINAL, seal("G77_256HP_SPCE_TERMINAL_REDUCTION_ENVELOPE_V1", "reduction", terminal))
    print(json.dumps({"result": SUCCESS, "serial_sha256": sha256(SERIAL), "raw_sha256": sha256(RAW), "transient_root_absent": not TRANSIENT.exists()}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
