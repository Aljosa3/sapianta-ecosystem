#!/usr/bin/env python3
"""Durably reduce the completed KA guest namespace-binding failure.

This reducer copies already-produced serial evidence and writes sealed host
evidence.  It performs no authority action, FM invocation, QEMU start, retry,
repair, replay, request, P11 entry, or protected invocation.
"""

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
KA = ROOT / ".github/governance/evidence/g77_256ka_fresh_expired_operational_recommissioning_v1"
RUNTIME = KA / "operation_state/runtime_export"
RECEIPTS = KA / "operation_state/receipts"
TRANSIENT = Path("/tmp/g77_256ka_fresh_expired_operational_recommissioning_v1")
SERIAL_SOURCE = TRANSIENT / "serial.log"
SERIAL = KA / "G77_256KA_SERIAL_CONSOLE_V1.log"
OBSERVATION = KA / "G77_256KA_PHASE_B_GUEST_FAILURE_OBSERVATION_V1.json"
TERMINAL = KA / "G77_256KA_SPCE_TERMINAL_FAILURE_REDUCTION_V1.json"
PRE = RECEIPTS / "G77_256KA_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
POST = RECEIPTS / "G77_256KA_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
SOURCE = KA / "G77_256KA_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
HANDOFF = KA / "G77_256KA_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
BINDING = KA / "G77_256KA_PRECONSUMPTION_INVOCATION_BINDING_V1.json"
PRECONSUMPTION = KA / "G77_256KA_PHASE_B_PRECONSUMPTION_READINESS_CHECKPOINT_V1.json"
CONSUMPTION = KA / "G77_256KA_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json"
INVOCATION = KA / "G77_256KA_FM_OPERATIONAL_INVOCATION_ATTEMPT_V1.json"
RESULT = KA / "G77_256KA_FM_OPERATIONAL_INVOCATION_RESULT_V1.json"
CONTEXT = KA / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
GUEST_OWNER = KA / "operation_state/guest_harness/sapianta_fresh_operation_context_v1.py"
GUEST_ADAPTER = KA / "operation_state/guest_harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"

HEAD = "128bb145969a7b9ccebb8812b24216e00c7db04c"
TREE = "47d09bc1d2ecf0529601ba65085651d01c325a7c"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
SUBJECT = "G77-256JZ verify FM authority digest preconsumption binding"
GENERATION = "G77_256KA_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256KA_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001"
DENIAL = "one-use Human act expired before PRECLAIM"
SOURCE_SHA256 = "00e24b7c7692b140e292d5cc8cc567b0b7330d85669f62711cd11ce0eefa3fe5"
HANDOFF_SHA256 = "98e514ad177a85ca358cec0f4f053abcfe49c47aaf24f108d70fd11e5ff90283"
HANDOFF_INNER_SHA256 = "7da1eafd20b781bf40c03ea3397b92d7d1d5aa1be66c4118f97b29c3e4a952d0"
BINDING_INNER_SHA256 = "9afb51fe36f94298db5a33efc3b784f23821bb667f48476fbc3788d52f5e6c00"
PRECONSUMPTION_INNER_SHA256 = "16759a697fb95ba16f354d461a0c8b3d92415287b770347d3c612943e8f793e7"
SERIAL_SHA256 = "45aad40d946b489f421dfb8bd87081e24ab298ec25ddde0f22949ba2ffecfa79"
PRE_SHA256 = "d3f18157ff4ce5a77859c91e90ffc615b8b27d7729f553a4129882f6a32bd6ba"
POST_SHA256 = "8910c0ddc56e7d25ee1c598404519ba8dbd1523d3b190f6693de31328d1d2c12"
EXPECTED_RUNTIME_FILES = {
    "G77_256KA_CONTINUATION_MANIFEST_V1.json",
    "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json",
}
TERMINAL_VALUE = (
    "M__KA_AUTHORIZED_EXPIRED_OPERATION_FAILED_AT_GUEST_CONTEXT_"
    "NAMESPACE_BINDING_BEFORE_REQUEST"
)


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise RuntimeError(f"noncanonical evidence: {path.name}")
    return value


def inner(path: Path, key: str) -> dict[str, Any]:
    envelope = load_canonical(path)
    value = envelope.get(key)
    if not isinstance(value, dict) or envelope.get(f"{key}_sha256") != hashlib.sha256(canonical_bytes(value)).hexdigest():
        raise RuntimeError(f"evidence seal mismatch: {path.name}")
    return value


def seal(schema: str, key: str, value: dict[str, Any]) -> dict[str, Any]:
    return {"schema_id": schema, key: value, f"{key}_sha256": hashlib.sha256(canonical_bytes(value)).hexdigest()}


def write_json(path: Path, value: dict[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise RuntimeError(f"terminal artifact collision: {path.name}")
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    with temporary.open("xb", buffering=0) as handle:
        handle.write(canonical_bytes(value)); os.fsync(handle.fileno())
    os.replace(temporary, path)


def copy_serial() -> None:
    if SERIAL.exists() or SERIAL.is_symlink():
        raise RuntimeError("durable serial collision")
    with SERIAL.open("xb", buffering=0) as handle:
        handle.write(SERIAL_SOURCE.read_bytes()); os.fsync(handle.fileno())


def git(*arguments: str) -> str:
    return subprocess.check_output(["git", *arguments], cwd=ROOT, text=True).strip()


def qemu_absent() -> bool:
    return subprocess.run(
        ["pgrep", "-f", "^/usr/bin/qemu-system-x86_64.*g77_256ka"], check=False,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode != 0


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


def main() -> None:
    if any(path.exists() or path.is_symlink() for path in (SERIAL, OBSERVATION, TERMINAL)):
        raise RuntimeError("KA terminal reduction namespace is not fresh")
    if (
        git("branch", "--show-current") != BRANCH or git("rev-parse", "HEAD") != HEAD
        or git("rev-parse", "HEAD^{tree}") != TREE or git("log", "-1", "--format=%s") != SUBJECT
        or git("remote", "get-url", "origin") != ORIGIN
        or git("status", "--porcelain", "--untracked-files=no") != ""
        or git("diff", "--cached", "--name-only") != ""
    ):
        raise RuntimeError("repository drift during evidence reduction")
    if not qemu_absent():
        raise RuntimeError("KA QEMU process remains active")
    if not SERIAL_SOURCE.is_file() or sha256(SERIAL_SOURCE) != SERIAL_SHA256:
        raise RuntimeError("exact completed serial evidence unavailable")

    if sha256(SOURCE) != SOURCE_SHA256 or sha256(HANDOFF) != HANDOFF_SHA256:
        raise RuntimeError("Human source or canonical handoff identity drift")
    handoff = load_canonical(HANDOFF)
    if handoff.get("authorization_sha256") != HANDOFF_INNER_SHA256:
        raise RuntimeError("canonical handoff inner identity drift")
    binding = inner(BINDING, "invocation_binding")
    if load_canonical(BINDING)["invocation_binding_sha256"] != BINDING_INNER_SHA256:
        raise RuntimeError("sealed invocation identity drift")
    if {
        binding["authenticated_canonical_authority_digest"],
        binding["sealed_invocation_authority_digest"],
        binding["final_fm_argv_authority_digest"],
    } != {HANDOFF_SHA256}:
        raise RuntimeError("JZ digest equality drift")
    preconsumption = inner(PRECONSUMPTION, "checkpoint")
    if load_canonical(PRECONSUMPTION)["checkpoint_sha256"] != PRECONSUMPTION_INNER_SHA256:
        raise RuntimeError("preconsumption checkpoint identity drift")
    if preconsumption["negative_binding_rejection_count"] != 13 or preconsumption["operational_counters"]["authority_consumption_count"] != 0:
        raise RuntimeError("preconsumption proof incomplete")
    consumption = inner(CONSUMPTION, "checkpoint")
    invocation = inner(INVOCATION, "attempt")
    result = inner(RESULT, "result")
    if (
        consumption["authority_state_after"] != "CONSUMED"
        or consumption["operational_counters"]["authority_consumption_count"] != 1
        or invocation["invocation_count"] != 1 or result["invocation_count"] != 1
        or result["process_exit_status"] != 0
    ):
        raise RuntimeError("single consumption/invocation evidence mismatch")

    if sha256(PRE) != PRE_SHA256 or sha256(POST) != POST_SHA256:
        raise RuntimeError("FM receipt identity drift")
    pre = load_canonical(PRE); post = load_canonical(POST); argv = pre["vector"]["argv"]
    if not (
        pre["generation_identity"] == post["generation_identity"] == GENERATION
        and pre["operation_identity"] == post["operation_identity"] == OPERATION
        and pre["execution_attempt_count"] == post["execution_attempt_count"] == 1
        and pre["automatic_retry_count"] == post["automatic_retry_count"] == 0
        and pre["started_unix_ns"] == post["started_unix_ns"]
        and pre["process_exit_status"] is None and post["process_exit_status"] == 0
        and pre["vector"] == post["vector"] and argv.count("-nic") == 1
        and argv[argv.index("-nic") + 1] == "none"
    ):
        raise RuntimeError("single no-network PRE/POST receipt pair invalid")
    runtime_files = {path.name for path in RUNTIME.iterdir() if path.is_file()}
    if runtime_files != EXPECTED_RUNTIME_FILES:
        raise RuntimeError("unexpected guest operational evidence after context failure")

    serial = SERIAL_SOURCE.read_bytes()
    required = (
        b"G77_256FM_BOOT_MARKER=PASS",
        b'File "/mnt/dp-harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py", line 261, in load_guest_runtime_namespace',
        b'raise ContextError("sealed operation projection is not namespace-bound")',
        b"g77_256jr_guest_context_owner.ContextError: sealed operation projection is not namespace-bound",
        b"G77_256FM_HARNESS_EXIT_STATUS=1",
        b"Powering off.",
    )
    if any(token not in serial for token in required) or DENIAL.encode() in serial:
        raise RuntimeError("decisive guest failure evidence incomplete or denial unexpectedly present")
    locations = {
        token.decode("utf-8"): next(i for i, line in enumerate(serial.splitlines(), 1) if token in line)
        for token in required
    }
    owner = GUEST_OWNER.read_text(encoding="utf-8")
    adapter = GUEST_ADAPTER.read_text(encoding="utf-8")
    if (
        'namespace_lead = f"{prefix}_{vector}_"' not in owner
        or 'raise ContextError("sealed operation projection is not namespace-bound")' not in owner
        or "context = owner.load_context(context_path, repository_root=root)" not in adapter
        or "source = specialize_fc_runtime_source(" not in adapter
        or adapter.index("context = owner.load_context") > adapter.index("source = specialize_fc_runtime_source")
    ):
        raise RuntimeError("static failure-order evidence drift")
    context = load_canonical(CONTEXT)
    actual_namespace = Path(context["operation_evidence_root"]).name
    expected_lead = f"{context['identity_namespace_prefix'].lower()}_expired_"
    if actual_namespace.startswith(expected_lead):
        raise RuntimeError("namespace mismatch no longer reproduced")

    copy_serial()
    observation_value = {
        "schema_id": "G77_256KA_PHASE_B_GUEST_FAILURE_OBSERVATION_V1", "recorded_at_utc": now(),
        "generation_identity": GENERATION, "operation_identity": OPERATION,
        "serial_source_path": str(SERIAL_SOURCE), "durable_serial_path": SERIAL.relative_to(ROOT).as_posix(),
        "serial_sha256": sha256(SERIAL), "serial_byte_count": SERIAL.stat().st_size,
        "serial_line_count": len(serial.splitlines()), "serial_line_locations": locations,
        "boot_marker": "PASS", "guest_harness_exit_status": 1, "qemu_process_exit_status": 0,
        "exact_exception_type": "ContextError", "exact_exception": "sealed operation projection is not namespace-bound",
        "failure_boundary": "GUEST_CONTEXT_OWNER_NAMESPACE_BINDING_BEFORE_SPECIALIZATION_REQUEST_AND_P11",
        "operation_namespace_observed": actual_namespace, "operation_namespace_required_lead": expected_lead,
        "expired_denial_expected": DENIAL, "expired_denial_observed": False,
        "runtime_output_files_observed": sorted(runtime_files), "guest_operational_output_count": 0,
        "qemu_absent_after_completion": True, "retry_count": 0, "repair_retry_count": 0, "replay_count": 0,
    }
    write_json(OBSERVATION, seal("G77_256KA_PHASE_B_GUEST_FAILURE_OBSERVATION_ENVELOPE_V1", "observation", observation_value))
    observation_file_sha = sha256(OBSERVATION)
    observation_inner_sha = load_canonical(OBSERVATION)["observation_sha256"]

    reduction = {
        "schema_id": "G77_256KA_SPCE_TERMINAL_FAILURE_REDUCTION_V1", "recorded_at_utc": now(),
        "terminal": TERMINAL_VALUE, "generation_identity": GENERATION, "operation_identity": OPERATION,
        "entry": {"repository": str(ROOT), "branch": BRANCH, "head": HEAD, "tree": TREE, "subject": SUBJECT,
                  "origin": ORIGIN, "remote_head": HEAD, "index_empty": True,
                  "phase_a_worktree": "VERIFIED__EXACT_BOUNDED_KA_ROOT"},
        "nested_authority": {"origin": "git@github.com:Aljosa3/sapianta-core.git",
                             "head": "3183bab71f8f30397c0309dd2e6d846d14a11f66",
                             "tree": "7c32ec05efc2be43297849bc38ec8766514a523d",
                             "clean": True, "detached": True, "pinned": True, "remote_tag_equal": True},
        "human_authority": {"authentication": "VERIFIED__EXACT_HUMAN_SUPPLIED_ACT",
                            "source_sha256": SOURCE_SHA256, "handoff_file_sha256": HANDOFF_SHA256,
                            "handoff_inner_sha256": HANDOFF_INNER_SHA256,
                            "state": "VERIFIED__CONSUMED_EXACTLY_ONCE__NONREUSABLE__NONTRANSFERABLE"},
        "jz_preconsumption_binding": {"result": "VERIFIED__PASS_BEFORE_CONSUMPTION",
                                      "authenticated_canonical_authority_digest": HANDOFF_SHA256,
                                      "sealed_invocation_authority_digest": HANDOFF_SHA256,
                                      "final_fm_argv_authority_digest": HANDOFF_SHA256,
                                      "invocation_binding_sha256": BINDING_INNER_SHA256,
                                      "preconsumption_checkpoint_sha256": PRECONSUMPTION_INNER_SHA256,
                                      "caller_digest_input_count": 0, "provider_digest_input_count": 0,
                                      "negative_binding_rejection_count": 13},
        "operational_counters": counters(),
        "operation": {"fm_result": "VERIFIED__ONE_INVOCATION__HOST_EXIT_0", "pre_receipt_count": 1,
                      "post_receipt_count": 1, "qemu_network": "VERIFIED__NONE", "vm_boot": "VERIFIED__PASS",
                      "guest_harness_exit_status": 1, "operation_attempt": "VERIFIED__STARTED_ONCE",
                      "request": "VERIFIED__NOT_REACHED", "expired_check": "VERIFIED__NOT_REACHED",
                      "expired_denial": "NOT_OBSERVED", "p11_entry": "VERIFIED__0",
                      "protected_invocation": "VERIFIED__0", "protected_effect": "VERIFIED__0",
                      "failure_observation_path": OBSERVATION.relative_to(ROOT).as_posix(),
                      "failure_observation_file_sha256": observation_file_sha,
                      "failure_observation_inner_sha256": observation_inner_sha,
                      "pre_receipt_sha256": PRE_SHA256, "post_receipt_sha256": POST_SHA256,
                      "serial_sha256": SERIAL_SHA256},
        "failure": {"last_verified_edge": "EXACT_HUMAN_AUTHORITY_AUTHENTICATED_JZ_BOUND_CONSUMED_ONCE_AND_ONE_NO_NETWORK_VM_BOOT_REACHED_GUEST_ADAPTER",
                    "first_broken_edge": "GUEST_CONTEXT_OWNER_REJECTED_SEALED_OPERATION_EVIDENCE_ROOT_NAMESPACE_BEFORE_EXPIRED_SPECIALIZATION",
                    "exact_failure": "sealed operation projection is not namespace-bound",
                    "localized_cause": "OPERATION_ROOT_NAMESPACE_DOES_NOT_START_WITH_IDENTITY_PREFIX_PLUS_EXPIRED_VECTOR",
                    "observed_namespace": actual_namespace, "required_namespace_lead": expected_lead,
                    "minimum_missing_capability": "PREAUTHORIZATION_OPERATION_NAMESPACE_COMPATIBLE_WITH_EXISTING_GUEST_CONTEXT_OWNER_NAMESPACE_RULE",
                    "minimum_legal_next_delta": "AFTER_HUMAN_REVIEW__SEPARATE_REPOSITORY_ONLY_NAMESPACE_BINDING_GENERATION__NO_KA_RETRY_OR_REPLAY"},
        "e05": {"before": "VERIFIED__11_OF_18", "after": "VERIFIED__11_OF_18",
                "state": "VERIFIED__11_OF_18", "frontier": "VERIFIED__7_UNSATISFIED_OF_18",
                "credit": "VERIFIED__0", "expired": "NOT_PROVEN_OPERATIONALLY"},
        "reuse": {"ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0"},
        "architecture": {"production_mutation_count": 0, "p11_implementation_mutation_count": 0,
                         "new_owner_count": 0, "new_route_count": 0, "new_registry_count": 0,
                         "new_generic_abstraction_count": 0, "new_constitutional_concept_count": 0,
                         "production_route_before": 1, "production_route_after": 1},
        "proof_yield": {"new_verified_capability_count": "VERIFIED__0_OPERATIONAL_EXPIRED_VECTOR",
                        "new_blocker_localized_count": "VERIFIED__1", "e05_credit": "VERIFIED__0",
                        "proof_reuse_count": "VERIFIED__17"},
        "ccwim": {"ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION",
                  "authenticated_repository_continuation": "VERIFIED__YES",
                  "previous_worker_conversation_required": "VERIFIED__NO",
                  "previous_worker_memory_required": "VERIFIED__NO",
                  "handoff_reconstruction_success": "VERIFIED__YES", "handoff_ambiguity_count": "VERIFIED__0",
                  "observed_artifact_level_cross_worker_drift": "VERIFIED__0",
                  "cross_account_recovery": "VERIFIED__YES",
                  "cross_account_recovery_source": "AUTHENTICATED_REPOSITORY_PHASE_A_PLUS_EXACT_HUMAN_ACT"},
        "governance": {"project_progress": "VERIFIED__KA_ONE_SHOT_FAILURE_DURABLY_REDUCED",
                       "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
                       "informal_project_progress_estimate": "ESTIMATED__EXPIRED_OPERATION_BLOCKED_AT_GUEST_CONTEXT_NAMESPACE_BINDING",
                       "constitutional_health_evidence": "VERIFIED__FAIL_CLOSED_NO_RETRY_NO_P11_ENTRY_NO_PROTECTED_EFFECT",
                       "shadow_automation_status": "VERIFIED__ABSENT",
                       "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
                       "governance_efficience": "ESTIMATED__MEDIUM__ONE_SHOT_FAILURE_LOCALIZED_WITH_DURABLE_EVIDENCE",
                       "overengineering_risk": "ESTIMATED__LOW__EVIDENCE_ONLY_TERMINAL_REDUCTION",
                       "cognition_provenance": "VERIFIED__AUTHENTICATED_REPOSITORY_RECEIPT_AND_SERIAL_EVIDENCE_PRIMARY",
                       "cognition_assisted_handoff": "VERIFIED__CROSS_ACCOUNT_REPOSITORY_ONLY_PHASE_A_RECOVERY",
                       "candidate_capability": "NOT_PROVEN__FRESH_EXPIRED_OPERATIONAL_DENIAL",
                       "shadow_design_target": "VERIFIED__SOLE_FM_ER_P11_ROUTE_WITH_STABLE_JR_EXPIRED_CHECKOUT",
                       "constitutional_continuation_progress": "VERIFIED__JZ_TO_KA_PRECONSUMPTION_BINDING_TO_ONE_GUEST_FAILURE"},
        "hac_hai_hae": "NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED",
        "auto_continuable": False, "human_review_required": True, "authority_state": "CONSUMED",
    }
    write_json(TERMINAL, seal("G77_256KA_SPCE_TERMINAL_FAILURE_REDUCTION_ENVELOPE_V1", "reduction", reduction))
    print(TERMINAL_VALUE)


if __name__ == "__main__":
    main()
