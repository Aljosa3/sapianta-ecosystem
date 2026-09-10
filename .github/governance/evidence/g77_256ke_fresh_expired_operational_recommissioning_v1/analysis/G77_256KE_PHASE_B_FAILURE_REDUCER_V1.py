#!/usr/bin/env python3
"""Reduce the consumed KE one-shot guest-custody failure without retry."""

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
KE = ROOT / ".github/governance/evidence/g77_256ke_fresh_expired_operational_recommissioning_v1"
RUNTIME = KE / "operation_state/runtime_export"
RECEIPTS = KE / "operation_state/receipts"
TRANSIENT = Path("/tmp/g77_256ke_fresh_expired_operational_recommissioning_v1")
SERIAL_SOURCE = TRANSIENT / "serial.log"
SERIAL = KE / "G77_256KE_SERIAL_CONSOLE_V1.log"
OBSERVATION = KE / "G77_256KE_PHASE_B_GUEST_CUSTODY_FAILURE_OBSERVATION_V1.json"
TERMINAL = KE / "G77_256KE_SPCE_TERMINAL_FAILURE_REDUCTION_V1.json"
SOURCE = KE / "G77_256KE_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
HANDOFF = KE / "G77_256KE_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
BINDING = KE / "G77_256KE_PRECONSUMPTION_INVOCATION_BINDING_V1.json"
PRECONSUMPTION = KE / "G77_256KE_PHASE_B_PRECONSUMPTION_READINESS_CHECKPOINT_V1.json"
CONSUMPTION = KE / "G77_256KE_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json"
INVOCATION = KE / "G77_256KE_FM_OPERATIONAL_INVOCATION_ATTEMPT_V1.json"
RESULT = KE / "G77_256KE_FM_OPERATIONAL_INVOCATION_RESULT_V1.json"
PRE = RECEIPTS / "G77_256KE_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
POST = RECEIPTS / "G77_256KE_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
RAW = RUNTIME / "G77_256KE_RAW_EXECUTION_EVIDENCE_V1.jsonl"
TEARDOWN = RUNTIME / "G77_256KE_GUEST_TEARDOWN_SEAL_V1.json"
TERMINAL_MANIFEST = RUNTIME / "G77_256KE_CONTINUATION_MANIFEST_TERMINAL_V1.json"
PROJECTION_ROOT = KE / "operation_state/guest_harness"
FM_LAUNCHER = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)

HEAD = "ed4acdc4c132754d857d623e54783e54e4c96d52"
TREE = "be8967cad28c9149fb5e17b895e5c58ac119ef13"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
SUBJECT = "G77-256KD verify KC Phase-B entry owner interface binding"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
GENERATION = "G77_256KE_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256KE_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001"
TERMINAL_VALUE = "M__KE_AUTHORIZED_EXPIRED_OPERATION_FAILED_AT_GUEST_CUSTODY_IMPORT_BEFORE_OPERATION_REQUEST"
FIRST_FAILURE = (
    "RuntimeError: custody failed before gate: {'error': \"[Errno 13] Permission denied: "
    "'/mnt/dp-harness/sapianta_fresh_operation_context_v1.py'\", 'error_type': "
    "'PermissionError', 'message_type': 'CUSTODY_FAILURE'}"
)

EXPECTED_HASHES = {
    SOURCE: "2a5b0f25fb9e9b0cca9a6bf1d6ee803f4c73f3b3415039fbaab9eae53ac25724",
    HANDOFF: "55b1578d5896b19c08b38047de8e64d32142d5f13e7b66def6e87a51f0443632",
    BINDING: "48f335cdf2a81df2f5440f21b15011f1cc65b1fe13e8e90a170b11fa62617a8b",
    PRECONSUMPTION: "28b3dae69a0e75514fb9b858befdf4490a0326b71716b7f416c4c7f6dfd87e1c",
    CONSUMPTION: "b40f3c6da9ca1d2f3ca302ec8da38f2e9551f9d39c5854c54ff5955201cddfb0",
    INVOCATION: "e81fc88a26f1f5739824c38fe23706fce04f941d22ab703eaa64d9f95c7fa248",
    RESULT: "c89463cca95da47b5c11f89001ea8269525094891db71234e40e1a83831877c2",
    PRE: "137daac3246325ddef266959ac4265f939032a2c774b87327df23190238c81ec",
    POST: "2bf46a2f7fcdbc522221242d64e71f16b90709797b4c1f56025c693e3fcc9e4b",
    RAW: "7602388667ff722ea40851189f895e827227e8aecfc8269ec65f008dbfbfe9fb",
    TEARDOWN: "e6e068ea5b69fd36e3c5370dab37bba38a56a3235f895b52276afcf7813a5553",
    TERMINAL_MANIFEST: "2f895379e8dbb63221bc89fe444af3cee6090b4d7e1b8ba7cd867937807213ac",
    SERIAL_SOURCE: "b1c772f8431ea8432d470e895458497f142f29c3fea360f5e22bada407d9762e",
    FM_LAUNCHER: "662cce2458300c12cb6dfb18d8c836db7867c4400430a8081acbb4e285a60a36",
}
HANDOFF_INNER = "65aa7b99aecc8f7957af65e1cfcdb100b5813103f70306c635ff0364566fe93e"
BINDING_INNER = "f429b473c36bba4944e4c68941018f5b670010f1ad1a609cfd217ccec1605e61"
PRECONSUMPTION_INNER = "01f90d7a1b6a1ac3732666295fb955cd773559f7286deddcdf91954e651cab25"


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes(); value = json.loads(raw)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise RuntimeError(f"noncanonical evidence: {path.name}")
    return value


def inner(path: Path, key: str) -> dict[str, Any]:
    envelope = load_canonical(path); value = envelope.get(key)
    if not isinstance(value, dict) or envelope.get(f"{key}_sha256") != hashlib.sha256(canonical_bytes(value)).hexdigest():
        raise RuntimeError(f"seal mismatch: {path.name}")
    return value


def seal(schema: str, key: str, value: dict[str, Any]) -> dict[str, Any]:
    return {"schema_id": schema, key: value, f"{key}_sha256": hashlib.sha256(canonical_bytes(value)).hexdigest()}


def persist(path: Path, data: bytes) -> None:
    if path.exists() or path.is_symlink():
        raise RuntimeError(f"terminal collision: {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    with temporary.open("xb", buffering=0) as handle:
        handle.write(data); os.fsync(handle.fileno())
    os.replace(temporary, path)


def persist_json(path: Path, value: dict[str, Any]) -> None:
    persist(path, canonical_bytes(value))


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def counters() -> dict[str, int]:
    return {
        "operational_authorization_count": 1, "authority_consumption_count": 1,
        "pre_operational_count": 1, "fm_operational_invocation_count": 1,
        "qemu_count": 1, "vm_count": 1, "operation_attempt_count": 1,
        "operational_request_count": 0, "expired_denial_count": 0,
        "p11_entry_count": 0, "protected_invocation_count": 0,
        "protected_effect_count": 0, "retry_count": 0,
        "repair_retry_count": 0, "replay_count": 0,
    }


def recovery_counters() -> dict[str, int]:
    return {
        "new_authority_consumption_during_recovery": 0,
        "new_operation_attempt_during_recovery": 0,
        "new_pre_during_recovery": 0,
        "new_fm_operational_invocation_during_recovery": 0,
        "new_qemu_during_recovery": 0,
        "new_vm_during_recovery": 0,
        "retry_during_recovery": 0,
        "repair_retry_during_recovery": 0,
        "replay_during_recovery": 0,
    }


def main() -> None:
    if SERIAL.exists() or OBSERVATION.exists() or TERMINAL.exists():
        raise RuntimeError("KE reduction namespace is not fresh")
    if (
        git("branch", "--show-current") != BRANCH or git("rev-parse", "HEAD") != HEAD
        or git("rev-parse", "HEAD^{tree}") != TREE or git("log", "-1", "--format=%s") != SUBJECT
        or git("remote", "get-url", "origin") != ORIGIN
        or git("status", "--porcelain", "--untracked-files=no") != ""
        or git("diff", "--cached", "--name-only") != ""
    ):
        raise RuntimeError("repository drift during reduction")
    if subprocess.run(["pgrep", "-f", "^/usr/bin/qemu-system-x86_64.*g77_256ke"], check=False, stdout=subprocess.DEVNULL).returncode == 0:
        raise RuntimeError("KE QEMU remains active")
    for path, expected in EXPECTED_HASHES.items():
        if sha256(path) != expected:
            raise RuntimeError(f"identity mismatch: {path.name}")

    handoff = load_canonical(HANDOFF)
    binding = inner(BINDING, "invocation_binding")
    preconsumption = inner(PRECONSUMPTION, "checkpoint")
    consumption = inner(CONSUMPTION, "checkpoint")
    invocation = inner(INVOCATION, "attempt")
    result = inner(RESULT, "result")
    digest = EXPECTED_HASHES[HANDOFF]
    if (
        handoff.get("authorization_sha256") != HANDOFF_INNER
        or load_canonical(BINDING).get("invocation_binding_sha256") != BINDING_INNER
        or load_canonical(PRECONSUMPTION).get("checkpoint_sha256") != PRECONSUMPTION_INNER
        or {binding["authenticated_canonical_authority_digest"], binding["sealed_invocation_authority_digest"], binding["final_fm_argv_authority_digest"]} != {digest}
        or preconsumption.get("negative_binding_rejection_count") != 13
        or consumption.get("authority_state_after") != "CONSUMED"
        or consumption["operational_counters"]["authority_consumption_count"] != 1
        or invocation.get("invocation_count") != 1 or result.get("invocation_count") != 1
        or result.get("process_exit_status") != 0
    ):
        raise RuntimeError("authority, JZ, consumption, or invocation mismatch")

    pre = load_canonical(PRE); post = load_canonical(POST)
    if not (
        pre["generation_identity"] == post["generation_identity"] == GENERATION
        and pre["operation_identity"] == post["operation_identity"] == OPERATION
        and pre["execution_attempt_count"] == post["execution_attempt_count"] == 1
        and pre["automatic_retry_count"] == post["automatic_retry_count"] == 0
        and pre["started_unix_ns"] == post["started_unix_ns"]
        and pre["process_exit_status"] is None and post["process_exit_status"] == 0
        and pre["vector"] == post["vector"]
        and pre["vector"]["argv"].count("-nic") == 1
        and pre["vector"]["argv"][pre["vector"]["argv"].index("-nic") + 1] == "none"
    ):
        raise RuntimeError("single no-network receipt pair mismatch")

    teardown = load_canonical(TEARDOWN)
    guest_counts = teardown.get("execution_counters", {})
    if (
        teardown.get("first_failure") != FIRST_FAILURE
        or teardown.get("teardown_state") != "COMPLETE"
        or guest_counts.get("vm_boot_count") != 1
        or guest_counts.get("e05_case_execution_count") != 0
        or guest_counts.get("p11_entry_count") != 0
        or guest_counts.get("p11_operational_invocation_count") != 0
        or guest_counts.get("automatic_retry_count") != 0
        or guest_counts.get("execution_replay_count") != 0
    ):
        raise RuntimeError("guest teardown evidence mismatch")
    raw_lines = RAW.read_text(encoding="utf-8").splitlines()
    raw_records = [json.loads(line) for line in raw_lines]
    failures = [r for r in raw_records if r.get("record_type") == "first_failure"]
    if len(raw_records) != 15 or len(failures) != 1 or failures[0]["facts"].get("first_failure") != FIRST_FAILURE:
        raise RuntimeError("raw first-failure evidence mismatch")
    execution_contexts = [r for r in raw_records if r.get("record_type") == "execution_context"]
    p01_records = [r for r in raw_records if r.get("record_type") == "commissioning_P01"]
    if len(execution_contexts) != 1 or len(p01_records) != 1:
        raise RuntimeError("guest projection provenance evidence mismatch")
    guest_mounts = execution_contexts[0]["facts"]["checkout_context"]["guest_mount_table"]
    custody_roles = [r for r in p01_records[0]["facts"]["live_roles"] if r.get("role") == "custody"]
    projection_stat = PROJECTION_ROOT.stat()
    launcher_source = FM_LAUNCHER.read_text(encoding="utf-8")
    if (
        len(custody_roles) != 1
        or custody_roles[0].get("uid") != 3
        or custody_roles[0].get("gid") != 3
        or not any(line.startswith("fm_harness /mnt/dp-harness 9p ro,") for line in guest_mounts)
        or projection_stat.st_mode & 0o777 != 0o700
        or "adapter_projection_root.mkdir(mode=0o700, parents=False, exist_ok=False)" not in launcher_source
    ):
        raise RuntimeError("guest projection permission provenance mismatch")
    serial = SERIAL_SOURCE.read_bytes()
    if not all(token in serial for token in (
        b"G77_256FM_BOOT_MARKER=PASS", b"G77_256FM_HARNESS_EXIT_STATUS=40", b"Powering off."
    )) or b"one-use Human act expired before PRECLAIM" in serial:
        raise RuntimeError("serial terminal evidence mismatch")

    persist(SERIAL, serial)
    observation_value = {
        "schema_id": "G77_256KE_PHASE_B_GUEST_CUSTODY_FAILURE_OBSERVATION_V1",
        "recorded_at_utc": now(), "generation_identity": GENERATION,
        "operation_identity": OPERATION, "serial_sha256": sha256(SERIAL),
        "serial_byte_count": SERIAL.stat().st_size, "serial_line_count": len(serial.splitlines()),
        "boot_marker": "PASS", "guest_harness_exit_status": 40,
        "qemu_process_exit_status": 0, "qemu_absent_after_completion": True,
        "exact_exception_type": "PermissionError", "exact_exception_errno": 13,
        "exact_exception_path": "/mnt/dp-harness/sapianta_fresh_operation_context_v1.py",
        "first_failure": FIRST_FAILURE,
        "failure_boundary": "GUEST_CUSTODY_CONTEXT_OWNER_IMPORT_BEFORE_EXPIRED_OPERATION_REQUEST_AND_P11",
        "blocker_classification": "VERIFIED__GUEST_CUSTODY_PROJECTION_PERMISSION_DENIAL_AT_CONTEXT_OWNER_LOAD",
        "root_cause": "VERIFIED__HOST_GUEST_HARNESS_PROJECTION_ROOT_MODE_0700_EXCLUDES_CUSTODY_UID_3_TRAVERSAL",
        "host_projection_root": PROJECTION_ROOT.relative_to(ROOT).as_posix(),
        "host_projection_root_mode": "0700",
        "host_projection_root_uid": projection_stat.st_uid,
        "host_projection_root_gid": projection_stat.st_gid,
        "guest_custody_uid": custody_roles[0]["uid"], "guest_custody_gid": custody_roles[0]["gid"],
        "guest_projection_mount": next(line for line in guest_mounts if line.startswith("fm_harness ")),
        "projection_root_mode_owner": "FM_LAUNCHER_ADAPTER_PROJECTION_ROOT_MKDIR_MODE_0700",
        "fm_launcher_sha256": EXPECTED_HASHES[FM_LAUNCHER],
        "expired_denial_expected": "one-use Human act expired before PRECLAIM",
        "expired_denial_observed": False, "raw_evidence_sha256": EXPECTED_HASHES[RAW],
        "raw_record_count": len(raw_records), "guest_execution_counters": guest_counts,
        "retry_count": 0, "repair_retry_count": 0, "replay_count": 0,
    }
    persist_json(OBSERVATION, seal(
        "G77_256KE_PHASE_B_GUEST_CUSTODY_FAILURE_OBSERVATION_ENVELOPE_V1",
        "observation", observation_value,
    ))

    reduction = {
        "schema_id": "G77_256KE_SPCE_TERMINAL_FAILURE_REDUCTION_V1",
        "recorded_at_utc": now(), "terminal": TERMINAL_VALUE,
        "generation_identity": GENERATION, "operation_identity": OPERATION,
        "entry": {"repository": str(ROOT), "branch": BRANCH, "head": HEAD, "tree": TREE,
                  "subject": SUBJECT, "origin": ORIGIN, "remote_head": HEAD,
                  "remote_equality": "VERIFIED", "index_empty": True,
                  "phase_a_worktree": "VERIFIED__EXACT_BOUNDED_KE_ROOT"},
        "nested_authority": {"origin": "git@github.com:Aljosa3/sapianta-core.git",
            "head": "3183bab71f8f30397c0309dd2e6d846d14a11f66",
            "tree": "7c32ec05efc2be43297849bc38ec8766514a523d",
            "clean": True, "detached": True, "pinned": True, "remote_tag_equal": True},
        "provider_interruption": {
            "provider_limit_interruption": "OBSERVED",
            "operation_interrupted_by_provider_limit": "NO__OPERATION_ALREADY_TERMINATED",
            "same_generation_recovery": "PERMITTED__TERMINAL_REDUCTION_ONLY",
            "provider_capability_is_execution_authority": False,
        },
        "human_authority": {"authentication": "VERIFIED__EXACT_HUMAN_SUPPLIED_ACT",
            "source_sha256": EXPECTED_HASHES[SOURCE], "handoff_file_sha256": digest,
            "handoff_inner_sha256": HANDOFF_INNER,
            "state": "VERIFIED__CONSUMED_EXACTLY_ONCE__NONREUSABLE__NONTRANSFERABLE"},
        "jz_preconsumption_binding": {"result": "VERIFIED__PASS_BEFORE_CONSUMPTION",
            "authenticated_canonical_authority_digest": digest,
            "sealed_invocation_authority_digest": digest,
            "final_fm_argv_authority_digest": digest,
            "invocation_binding_sha256": BINDING_INNER,
            "preconsumption_checkpoint_sha256": PRECONSUMPTION_INNER,
            "caller_digest_input_count": 0, "provider_digest_input_count": 0,
            "negative_binding_rejection_count": 13},
        "operational_counters": counters(),
        "recovery_delta_operational_counters": recovery_counters(),
        "operation": {"fm_result": "VERIFIED__ONE_INVOCATION__HOST_EXIT_0",
            "pre_receipt_count": 1, "post_receipt_count": 1,
            "qemu_network": "VERIFIED__NONE", "vm_boot": "VERIFIED__PASS",
            "guest_harness_exit_status": 40, "operation_attempt": "VERIFIED__STARTED_ONCE",
            "operational_request": "VERIFIED__NOT_REACHED",
            "expired_check": "VERIFIED__NOT_REACHED", "expired_denial": "NOT_OBSERVED",
            "p11_entry": "VERIFIED__0", "protected_invocation": "VERIFIED__0",
            "protected_effect": "VERIFIED__0",
            "failure_observation_path": OBSERVATION.relative_to(ROOT).as_posix(),
            "failure_observation_file_sha256": sha256(OBSERVATION),
            "failure_observation_inner_sha256": load_canonical(OBSERVATION)["observation_sha256"],
            "pre_receipt_sha256": EXPECTED_HASHES[PRE], "post_receipt_sha256": EXPECTED_HASHES[POST],
            "serial_sha256": EXPECTED_HASHES[SERIAL_SOURCE], "raw_evidence_sha256": EXPECTED_HASHES[RAW],
            "teardown_sha256": EXPECTED_HASHES[TEARDOWN],
            "terminal_manifest_sha256": EXPECTED_HASHES[TERMINAL_MANIFEST]},
        "failure": {"last_verified_edge": "EXACT_HUMAN_AUTHORITY_AUTHENTICATED_JZ_BOUND_CONSUMED_ONCE_AND_ONE_NO_NETWORK_VM_BOOT_REACHED_GUEST_CUSTODY_LOAD",
            "first_broken_edge": "GUEST_CUSTODY_PROCESS_COULD_NOT_LOAD_PROJECTED_CONTEXT_OWNER_BEFORE_EXPIRED_OPERATION_REQUEST",
            "exact_failure": "PermissionError: [Errno 13] Permission denied: /mnt/dp-harness/sapianta_fresh_operation_context_v1.py",
            "blocker_classification": "VERIFIED__GUEST_CUSTODY_PROJECTION_PERMISSION_DENIAL_AT_CONTEXT_OWNER_LOAD",
            "root_cause": "VERIFIED__HOST_GUEST_HARNESS_PROJECTION_ROOT_MODE_0700_EXCLUDES_CUSTODY_UID_3_TRAVERSAL",
            "minimum_missing_capability": "GUEST_CUSTODY_TRAVERSAL_AND_READABILITY_OF_EXISTING_CONTEXT_OWNER_THROUGH_CURRENT_READ_ONLY_PROJECTION",
            "minimum_legal_next_delta": "AFTER_HUMAN_REVIEW__SEPARATE_REPOSITORY_ONLY_GUEST_HARNESS_PERMISSION_BINDING_GENERATION__NO_KE_RETRY_OR_REPLAY"},
        "e05": {"before": "VERIFIED__11_OF_18", "after": "VERIFIED__11_OF_18",
            "state": "VERIFIED__11_OF_18", "frontier": "VERIFIED__7_UNSATISFIED_OF_18",
            "credit": "VERIFIED__0", "expired": "NOT_PROVEN_OPERATIONALLY"},
        "reuse": {"ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0"},
        "terminality": {"ke_retry_allowed": False, "ke_repair_retry_allowed": False,
            "ke_replay_allowed": False, "ke_replacement_authority_allowed": False,
            "ke_second_attempt_allowed": False, "ke_authority_successor_transfer_allowed": False},
        "architecture": {"production_mutation_count": 0, "p11_implementation_mutation_count": 0,
            "new_owner_count": 0, "new_route_count": 0, "new_registry_count": 0,
            "new_generic_abstraction_count": 0, "new_constitutional_concept_count": 0,
            "production_route_before": 1, "production_route_after": 1},
        "proof_yield": {"new_verified_capability_count": "VERIFIED__0_OPERATIONAL_EXPIRED_VECTOR",
            "new_blocker_localized_count": "VERIFIED__1", "e05_credit": "VERIFIED__0",
            "proof_reuse_count": "VERIFIED__17"},
        "governance": {"project_progress": "VERIFIED__KE_SINGLE_AUTHORIZED_ATTEMPT_COMPLETED_AND_POSTCONSUMPTION_GUEST_BLOCKER_LOCALIZED",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "informal_project_progress_estimate": "ESTIMATED__EXPIRED_PATH_REACHED_SINGLE_VM_ATTEMPT_BUT_FAILED_BEFORE_EXPIRED_GATE",
            "constitutional_health_evidence": "VERIFIED__ONE_AUTHORITY_CONSUMPTION_ONE_OPERATION_ATTEMPT_ZERO_RETRY_ZERO_PROTECTED_EFFECT",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "governance_efficience": "ESTIMATED__MEDIUM__ONE_SHOT_FAILURE_LOCALIZED_WITH_DURABLE_EVIDENCE",
            "overengineering_risk": "ESTIMATED__LOW__EVIDENCE_ONLY_TERMINAL_REDUCTION",
            "cognition_provenance": "VERIFIED__AUTHENTICATED_RECEIPT_RAW_GUEST_TEARDOWN_AND_SERIAL_EVIDENCE_PRIMARY",
            "cognition_assisted_handoff": "VERIFIED__CROSS_ACCOUNT_SAME_GENERATION_RECOVERY_FROM_DURABLE_ARTIFACTS",
            "candidate_capability": "NOT_PROVEN__FRESH_EXPIRED_OPERATIONAL_DENIAL",
            "shadow_design_target": "VERIFIED__SOLE_FM_ER_P11_ROUTE_WITH_STABLE_JR_EXPIRED_CHECKOUT",
            "constitutional_continuation_progress": "VERIFIED__KE_PHASE_B_SINGLE_ATTEMPT_TO_POSTCONSUMPTION_GUEST_BLOCKER_REDUCTION"},
        "ccwim": {"ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION",
            "authenticated_repository_continuation": "VERIFIED__YES",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
            "handoff_reconstruction_success": "VERIFIED__YES", "handoff_ambiguity_count": "VERIFIED__0",
            "observed_artifact_level_cross_worker_drift": "VERIFIED__0",
            "cross_account_recovery": "VERIFIED",
            "provider_interruption_recovery": "VERIFIED"},
        "reuse_impact_assessment": {"existing_certified_capabilities_reused": "EX_17_OF_17__KD__KB__JZ__JX__JR__GN__FM__ER__P11",
            "new_capabilities": "VERIFIED__0_OPERATIONAL_EXPIRED_VECTOR__1_BLOCKER_LOCALIZED",
            "existing_capability_became_unreachable": False, "parallel_flow_created": False,
            "production_path_count_effect": "UNCHANGED__1_TO_1"},
        "hac_hai_hae": "NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED",
        "auto_continuable": False, "human_review_required": True,
    }
    persist_json(TERMINAL, seal(
        "G77_256KE_SPCE_TERMINAL_FAILURE_REDUCTION_ENVELOPE_V1", "reduction", reduction
    ))
    print(TERMINAL_VALUE)


if __name__ == "__main__":
    main()
