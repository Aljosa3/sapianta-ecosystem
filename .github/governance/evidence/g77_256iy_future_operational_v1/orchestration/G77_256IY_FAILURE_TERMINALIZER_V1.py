#!/usr/bin/env python3
"""Seal the consumed G77-256IY pre-request missing-entrypoint failure.

This finalizer performs no authority creation, launcher invocation, QEMU
execution, retry, repair, replay, request, or P11 entry.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
IY = ROOT / ".github/governance/evidence/g77_256iy_future_operational_v1"
RUNTIME = IY / "operation_state/runtime_export"
RECEIPTS = IY / "operation_state/receipts"
TRANSIENT = Path("/tmp/g77_256iy_future_operational_v1")
SERIAL_SOURCE = TRANSIENT / "serial.log"
SERIAL = IY / "G77_256IY_SERIAL_CONSOLE_V1.log"
PRE = RECEIPTS / "G77_256IY_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
POST = RECEIPTS / "G77_256IY_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
RAW = RUNTIME / "G77_256IY_RAW_EXECUTION_EVIDENCE_V1.jsonl"
GUEST_EXECUTION = RUNTIME / "G77_256IY_GUEST_EXECUTION_SEAL_V1.json"
GUEST_TEARDOWN = RUNTIME / "G77_256IY_GUEST_TEARDOWN_SEAL_V1.json"
AUTHORITY = IY / "G77_256IY_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
CONSUMPTION = IY / "G77_256IY_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json"
CONTEXT = IY / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
INDEPENDENT = IY / "G77_256IY_INDEPENDENT_TERMINAL_EVIDENCE_REDUCTION_V1.json"
PRE_TEARDOWN = IY / "G77_256IY_SPCE_HOST_PRE_TEARDOWN_CHECKPOINT_V1.json"
TEARDOWN = IY / "G77_256IY_SPCE_HOST_TEARDOWN_CHECKPOINT_V1.json"
FINAL_SEAL = IY / "G77_256IY_SPCE_FINAL_EXECUTION_SEAL_V1.json"
TERMINAL = IY / "G77_256IY_SPCE_TERMINAL_REDUCTION_V1.json"
BASE_IMAGE = Path("/tmp/g77_256cw.IkqZJN/noble-server-cloudimg-amd64.img")
BASE_SHA256 = "6e40c07ae715f744f84af0bec76415cc1987dd115b4b8de437818561f01a3733"
GENERATION = "G77_256IY_ONE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256IY_E05_FUTURE_DENIAL_BEFORE_ENTRY_001"
TERMINAL_CLASS = "E__AUTHORIZED_OPERATION_FAILED_BEFORE_REQUEST"
VERDICT = (
    "FAIL_CLOSED__G77_256IY_FUTURE_OPERATIONAL_PROOF_NOT_PROVEN__"
    "FUTURE_OPERATIONAL_CLI_ENTRYPOINT_ABSENT_BEFORE_REQUEST__E05_10_OF_18__"
    "ONE_OPERATION_ONLY__NO_RETRY__HUMAN_REVIEW_REQUIRED"
)
LAST_VERIFIED = (
    "ONE_AUTHORIZED_FM_INVOCATION__ONE_NO_NETWORK_QEMU_BOOT__"
    "FUTURE_GUEST_ADAPTER_TOP_LEVEL_AIGOL_IMPORTS_SUCCEEDED"
)
FIRST_BROKEN = "FUTURE_GUEST_ADAPTER_OPERATIONAL_CLI_ENTRYPOINT_ABSENT"
BLOCKING_OWNER = "G77_256IF_FUTURE_VECTOR_ADAPTER_OPERATIONAL_ENTRYPOINT"
EXACT_FAILURE = "repository-only FUTURE adapter; no operational CLI entry point"
MINIMUM_MISSING = (
    "GOVERNED_OPERATIONAL_FUTURE_ADAPTER_ENTRYPOINT_THAT_REUSES_THE_EXISTING_"
    "P11_ROUTE"
)
MINIMUM_NEXT = (
    "SEPARATE_HUMAN_REVIEWED_REPOSITORY_ONLY_SUCCESSOR_GENERATION_TO_FORMALIZE_"
    "AND_STATICALLY_VERIFY_THE_FUTURE_OPERATIONAL_ADAPTER_ENTRYPOINT__NO_RETRY_IN_IY"
)


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise RuntimeError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique_object)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise RuntimeError(f"noncanonical JSON: {path.name}")
    return value


def seal(schema: str, key: str, value: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": schema,
        key: value,
        f"{key}_sha256": hashlib.sha256(canonical_bytes(value)).hexdigest(),
    }


def write_json(path: Path, value: dict[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise RuntimeError(f"terminal artifact collision: {path.name}")
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    with temporary.open("xb", buffering=0) as handle:
        handle.write(canonical_bytes(value))
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def copy_serial() -> None:
    if SERIAL.exists() or SERIAL.is_symlink():
        raise RuntimeError("durable serial collision")
    with SERIAL.open("xb", buffering=0) as handle:
        handle.write(SERIAL_SOURCE.read_bytes())
        os.fsync(handle.fileno())


def qemu_absent() -> bool:
    return subprocess.run(
        ["pgrep", "-f", "^/usr/bin/qemu-system-x86_64.*g77_256iy"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode != 0


def counters() -> dict[str, int]:
    return {
        "human_authorization_presentation": 1,
        "human_operational_authority": 1,
        "authority_consumption": 1,
        "pre": 1,
        "fm_operational_launcher_invocation": 1,
        "qemu": 1,
        "vm_creation": 1,
        "vm_boot": 1,
        "operation_attempt": 1,
        "future_operation": 0,
        "request": 0,
        "future_denial": 0,
        "p11_entry": 0,
        "protected_invocation": 0,
        "protected_effect": 0,
        "retry": 0,
        "repair_retry": 0,
        "replay": 0,
        "second_consumption": 0,
        "e05_credit": 0,
    }


def main() -> int:
    targets = (SERIAL, INDEPENDENT, PRE_TEARDOWN, TEARDOWN, FINAL_SEAL, TERMINAL)
    if any(path.exists() or path.is_symlink() for path in targets):
        raise RuntimeError("IY failure terminal namespace is not fresh")
    if TRANSIENT.is_symlink() or not TRANSIENT.is_dir() or not SERIAL_SOURCE.is_file():
        raise RuntimeError("exact transient serial evidence unavailable")
    if not qemu_absent():
        raise RuntimeError("IY QEMU process still present")

    pre = load_canonical(PRE)
    post = load_canonical(POST)
    argv = pre["vector"]["argv"]
    if not (
        pre["generation_identity"] == post["generation_identity"] == GENERATION
        and pre["operation_identity"] == post["operation_identity"] == OPERATION
        and pre["started_unix_ns"] == post["started_unix_ns"]
        and pre["execution_attempt_count"] == post["execution_attempt_count"] == 1
        and pre["automatic_retry_count"] == post["automatic_retry_count"] == 0
        and post["process_exit_status"] == 0
        and pre["vector"] == post["vector"]
        and argv.count("-nic") == 1
        and argv[argv.index("-nic") + 1] == "none"
    ):
        raise RuntimeError("single no-network receipt pair invalid")

    consumption = load_canonical(CONSUMPTION)["checkpoint"]
    if not (
        consumption["authority_state_after"] == "CONSUMED"
        and consumption["authority_consumed"] == 1
        and consumption["operational_counters"]["authority_consumption"] == 1
    ):
        raise RuntimeError("single authority consumption not proven")
    load_canonical(AUTHORITY)
    load_canonical(CONTEXT)
    if any(path.exists() or path.is_symlink() for path in (RAW, GUEST_EXECUTION, GUEST_TEARDOWN)):
        raise RuntimeError("unexpected guest operational evidence after entrypoint failure")

    serial = SERIAL_SOURCE.read_bytes()
    required = (
        b"G77_256FM_BOOT_MARKER=PASS",
        b"repository-only FUTURE adapter; no operational CLI entry point",
        b"G77_256FM_HARNESS_EXIT_STATUS=1",
    )
    if any(token not in serial for token in required):
        raise RuntimeError("decisive guest entrypoint failure evidence incomplete")
    locations = {
        token.decode("utf-8"): next(
            index for index, line in enumerate(serial.splitlines(), start=1) if token in line
        )
        for token in required
    }
    if sha256(BASE_IMAGE) != BASE_SHA256:
        raise RuntimeError("base image changed before teardown")

    copy_serial()
    pre_checkpoint = {
        "schema_id": "G77_256IY_SPCE_HOST_PRE_TEARDOWN_CHECKPOINT_V1",
        "checkpoint_class": "HOST_PRE_TEARDOWN",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "terminal": TERMINAL_CLASS,
        "host_lifecycle": {
            "state": "PRE_TEARDOWN_OBSERVED",
            "qemu_process_absent": True,
            "transient_root_present": True,
            "checkout_present": (TRANSIENT / "checkout").is_dir(),
            "overlay_present": (TRANSIENT / "guest-overlay.qcow2").is_file(),
            "persistent_evidence_preserved": True,
        },
        "failure_observation": {
            "exception_type": "SystemExit",
            "exception_reason": EXACT_FAILURE,
            "exact_failure": EXACT_FAILURE,
            "harness_exit_status": 1,
            "qemu_process_exit_status": 0,
            "raw_evidence_absent": True,
            "guest_execution_seal_absent": True,
            "guest_teardown_seal_absent": True,
            "serial_line_locations": locations,
        },
        "durable_evidence": {
            "pre_receipt_sha256": sha256(PRE),
            "post_receipt_sha256": sha256(POST),
            "serial_sha256": sha256(SERIAL),
            "serial_byte_count": SERIAL.stat().st_size,
        },
        "base_image": {
            "path": str(BASE_IMAGE),
            "sha256_before": BASE_SHA256,
            "sha256_pre_teardown": sha256(BASE_IMAGE),
            "byte_identical": True,
        },
        "operational_counters": counters(),
        "e05": {"before": "10/18", "credit": 0, "after": "10/18"},
        "last_verified_edge": LAST_VERIFIED,
        "first_broken_edge": FIRST_BROKEN,
        "blocking_owner": BLOCKING_OWNER,
        "exact_failure": EXACT_FAILURE,
        "minimum_missing_capability": MINIMUM_MISSING,
        "minimum_legal_next_delta": MINIMUM_NEXT,
        "auto_continuable": False,
        "human_review_required": True,
        "recorded_at_utc": now(),
    }
    write_json(
        PRE_TEARDOWN,
        seal("G77_256IY_SPCE_HOST_PRE_TEARDOWN_CHECKPOINT_ENVELOPE_V1", "checkpoint", pre_checkpoint),
    )

    if TRANSIENT.resolve() != Path("/tmp/g77_256iy_future_operational_v1"):
        raise RuntimeError("transient teardown target mismatch")
    shutil.rmtree(TRANSIENT)
    if TRANSIENT.exists() or not qemu_absent() or sha256(BASE_IMAGE) != BASE_SHA256:
        raise RuntimeError("host teardown did not close")

    teardown = {
        "schema_id": "G77_256IY_SPCE_HOST_TEARDOWN_CHECKPOINT_V1",
        "checkpoint_class": "HOST_TEARDOWN",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "terminal": TERMINAL_CLASS,
        "host_pre_teardown_checkpoint": {
            "path": PRE_TEARDOWN.relative_to(ROOT).as_posix(),
            "file_sha256": sha256(PRE_TEARDOWN),
            "inner_sha256": load_canonical(PRE_TEARDOWN)["checkpoint_sha256"],
        },
        "host_teardown": {
            "state": "TEARDOWN_COMPLETE",
            "transient_root": str(TRANSIENT),
            "transient_root_absent": True,
            "transient_mount_absent": True,
            "qemu_process_absent": True,
            "persistent_serial_preserved": SERIAL.is_file(),
            "persistent_pre_receipt_preserved": PRE.is_file(),
            "persistent_post_receipt_preserved": POST.is_file(),
            "persistent_decisive_evidence_preserved": True,
        },
        "base_image": {
            "path": str(BASE_IMAGE),
            "sha256_before": BASE_SHA256,
            "sha256_after": sha256(BASE_IMAGE),
            "byte_identical": True,
        },
        "operational_counters": counters(),
        "e05": {"before": "10/18", "credit": 0, "after": "10/18"},
        "terminal_defect": {
            "last_verified_edge": LAST_VERIFIED,
            "first_broken_edge": FIRST_BROKEN,
            "blocking_owner": BLOCKING_OWNER,
            "exact_failure": EXACT_FAILURE,
            "minimum_missing_capability": MINIMUM_MISSING,
            "minimum_legal_next_delta": MINIMUM_NEXT,
        },
        "auto_continuable": False,
        "human_review_required": True,
        "recorded_at_utc": now(),
    }
    write_json(
        TEARDOWN,
        seal("G77_256IY_SPCE_HOST_TEARDOWN_CHECKPOINT_ENVELOPE_V1", "checkpoint", teardown),
    )

    reduction = {
        "schema_id": "G77_256IY_INDEPENDENT_TERMINAL_EVIDENCE_REDUCTION_V1",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "terminal": TERMINAL_CLASS,
        "observed_terminal_shape": "GUEST_AIGOL_IMPORTS_SUCCEEDED__OPERATIONAL_CLI_ENTRYPOINT_ABSENT_BEFORE_FUTURE_REQUEST",
        "failure": {
            "exception_type": "SystemExit",
            "exception_reason": EXACT_FAILURE,
            "exact_failure": EXACT_FAILURE,
            "harness_exit_status": 1,
            "qemu_process_exit_status": 0,
            "serial_sha256": sha256(SERIAL),
            "serial_byte_count": SERIAL.stat().st_size,
        },
        "counter_reduction": counters(),
        "future_semantics": {
            "evaluation": 500,
            "valid_from": 600,
            "valid_until": 1000,
            "relation": "500 < 600 < 1000",
            "semantic_result": "NOT_REACHED_OPERATIONALLY__ENTRYPOINT_ABSENT_BEFORE_REQUEST",
        },
        "request_entry_invocation_effect_separation": {
            "request": 0,
            "future_denial": 0,
            "p11_entry": 0,
            "protected_invocation": 0,
            "protected_effect": 0,
        },
        "e05": {"before": "10/18", "credit": 0, "after": "10/18"},
        "last_verified_edge": LAST_VERIFIED,
        "first_broken_edge": FIRST_BROKEN,
        "blocking_owner": BLOCKING_OWNER,
        "exact_failure": EXACT_FAILURE,
        "minimum_missing_capability": MINIMUM_MISSING,
        "minimum_legal_next_delta": MINIMUM_NEXT,
        "teardown": {
            "state": "COMPLETE",
            "transient_root_absent": True,
            "qemu_process_absent": True,
            "base_image_unchanged": True,
            "persistent_evidence_preserved": True,
        },
        "auto_continuable": False,
        "human_review_required": True,
        "recorded_at_utc": now(),
    }
    write_json(
        INDEPENDENT,
        seal("G77_256IY_INDEPENDENT_TERMINAL_EVIDENCE_REDUCTION_ENVELOPE_V1", "reduction", reduction),
    )

    artifacts = {
        path.relative_to(IY).as_posix(): sha256(path)
        for path in (
            AUTHORITY, CONSUMPTION, CONTEXT, PRE, POST, SERIAL,
            PRE_TEARDOWN, TEARDOWN, INDEPENDENT,
        )
    }
    final = {
        "schema_id": "G77_256IY_SPCE_FINAL_EXECUTION_SEAL_V1",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "terminal": TERMINAL_CLASS,
        "final_result": VERDICT,
        "authority_created_exists": 1,
        "authority_validated": 1,
        "authority_consumed": 1,
        "operation_count": 1,
        "qemu_count": 1,
        "vm_boot_count": 1,
        "future_operation_count": 0,
        "request_count": 0,
        "future_denial_count": 0,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "retry_count": 0,
        "repair_count": 0,
        "replay_count": 0,
        "e05_credit": 0,
        "teardown_state": "COMPLETE",
        "artifacts": artifacts,
        "auto_continuable": False,
        "human_review_required": True,
        "next_generation_started": False,
        "recorded_at_utc": now(),
    }
    write_json(
        FINAL_SEAL,
        seal("G77_256IY_SPCE_FINAL_EXECUTION_SEAL_ENVELOPE_V1", "seal", final),
    )

    terminal = {
        "schema_id": "G77_256IY_SPCE_TERMINAL_REDUCTION_V1",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "terminal": TERMINAL_CLASS,
        "terminal_state": "FAIL_CLOSED__OPERATION_CONSUMED__NO_RETRY",
        "operational_counters": counters(),
        "request_entry_invocation_effect_separation": {
            "request": 0,
            "future_denial": 0,
            "p11_entry": 0,
            "protected_invocation": 0,
            "protected_effect": 0,
        },
        "e05": {"before": "10/18", "credit": 0, "after": "10/18"},
        "evidence": {
            "authority_handoff_sha256": sha256(AUTHORITY),
            "authority_consumption_checkpoint_sha256": sha256(CONSUMPTION),
            "pre_receipt_sha256": sha256(PRE),
            "post_receipt_sha256": sha256(POST),
            "serial_sha256": sha256(SERIAL),
            "raw_evidence_status": "ABSENT__GUEST_FAILED_BEFORE_RUNTIME_EVIDENCE_PRODUCTION",
            "host_pre_teardown_checkpoint_sha256": load_canonical(PRE_TEARDOWN)["checkpoint_sha256"],
            "host_teardown_checkpoint_sha256": load_canonical(TEARDOWN)["checkpoint_sha256"],
            "independent_reduction_file_sha256": sha256(INDEPENDENT),
            "final_execution_seal_sha256": load_canonical(FINAL_SEAL)["seal_sha256"],
        },
        "proof_reuse": {"ex_reused": "17/17", "ex_reconstructed": 0},
        "route_firewall": {
            "production_route_before": 1,
            "production_route_after": 1,
            "production_route_delta": 0,
            "parallel_flow_created": False,
            "p11_mutation_count": 0,
        },
        "last_verified_edge": LAST_VERIFIED,
        "first_broken_edge": FIRST_BROKEN,
        "blocking_owner": BLOCKING_OWNER,
        "exact_failure": EXACT_FAILURE,
        "minimum_missing_capability": MINIMUM_MISSING,
        "minimum_legal_next_delta": MINIMUM_NEXT,
        "teardown": reduction["teardown"],
        "terminal_control": {
            "verdict": VERDICT,
            "auto_continuable": False,
            "human_review_required": True,
            "next_generation_started": False,
        },
        "recorded_at_utc": now(),
    }
    write_json(
        TERMINAL,
        seal("G77_256IY_SPCE_TERMINAL_REDUCTION_ENVELOPE_V1", "reduction", terminal),
    )
    print(json.dumps({
        "terminal": TERMINAL_CLASS,
        "verdict": VERDICT,
        "serial_sha256": sha256(SERIAL),
        "transient_root_absent": not TRANSIENT.exists(),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
