#!/usr/bin/env python3
"""Reduce the completed one-shot JW operation without retry or repair."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
JW = ROOT / ".github/governance/evidence/g77_256jw_expired_operational_v1"
MATERIALIZER_PATH = JW / "orchestration/G77_256JW_PREAUTHORIZATION_MATERIALIZER_V1.py"
CONTROLLER_PATH = JW / "orchestration/G77_256JW_AUTHORITY_CONSUMPTION_CONTROLLER_V1.py"
TERMINAL_PATH = JW / "G77_256JW_SPCE_TERMINAL_FAILURE_REDUCTION_V1.json"

REQUEST = JW / "G77_256JW_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
PRESENTATION = JW / "G77_256JW_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
PHASE_A_SAFE_STOP = JW / "G77_256JW_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
SOURCE = JW / "G77_256JW_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
HANDOFF = JW / "G77_256JW_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
CONSUMPTION = JW / "G77_256JW_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json"
PRE = JW / "operation_state/receipts/G77_256JW_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
POST = JW / "operation_state/receipts/G77_256JW_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
SERIAL = JW / "operation_state/runtime_export/G77_256JW_SERIAL_CONSOLE_V1.log"
RUNTIME_CONTEXT = JW / "operation_state/runtime_export/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
RUNTIME_MANIFEST = JW / "operation_state/runtime_export/G77_256JW_CONTINUATION_MANIFEST_V1.json"
ER_HARNESS = ROOT / (
    ".github/governance/evidence/g77_256er_p11_operational_v1/harness/"
    "G77_256ER_P11_OPERATIONAL_HARNESS_V1.py"
)

HEAD = "98206cab55fb4201c3b60de48eb032cca196de7c"
TREE = "ab1a39d41553fc0296e65287782a36b1f20fb22b"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
GENERATION = "G77_256JW_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256JW_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001"
REQUEST_ID = "97388bcba3da184e1dda04814cc8041644c58739b996f3accd646438f3597562"
PHASE_A_CHECKPOINT = "28231abf2ace90db790977bddd807c4f8bb9e2fe7340b803801eaf9961bf2eef"
SOURCE_SHA256 = "1b5ce1c32791e24df2118ee195fca85d3ee780b3ae644c4213c1543bc0548195"
HANDOFF_SHA256 = "aade77297894879800fdca507186f3be4bf37d98f73276c8bc24042d0daa6ce8"
CONTEXT = "7e427b49f46d4327e35fc889141d1c0889c5f2f43a1fbc6e9810c58ef1a670fd"
ARGV = "9248e3882d3027c53f85893c42a53a749a0281703408de71b2b3ab458e83eb37"
CANDIDATE = "8af5ba1cbf9e396aa2f4f981a6f20b821c5fd1c38e091ed1cb3646c76c953b4a"
JR_HEAD = "304b342e26e92f226afa01db4b4203acfa51f532"
JR_TREE = "fc0c50e4dd79e900d85d48c5c0aeb53fe9d0c937"
FAILURE = "sealed operation context checkout binding mismatch"
TERMINAL = (
    "M__FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATION_BLOCKED_AT_ER_CONTEXT_"
    "CHECKOUT_ROLE_IDENTITY_COLLAPSE_BEFORE_EXPIRED_CHECK"
)


class ReductionError(RuntimeError):
    pass


def load_module(path: Path, name: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise ReductionError(f"MODULE_UNAVAILABLE:{name}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


M = load_module(MATERIALIZER_PATH, "g77_256jw_reducer_materializer")
C = load_module(CONTROLLER_PATH, "g77_256jw_reducer_controller")


def canonical_bytes(value: Any) -> bytes:
    return M.canonical_bytes(value)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ReductionError(f"DUPLICATE_JSON_KEY:{key}")
        result[key] = value
    return result


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique_object)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise ReductionError(f"NONCANONICAL_JSON:{path}")
    return value


def verify_envelope(path: Path, inner_name: str) -> dict[str, Any]:
    envelope = load_canonical(path)
    inner = envelope.get(inner_name)
    if not isinstance(inner, dict) or envelope.get(f"{inner_name}_sha256") != sha256_bytes(
        canonical_bytes(inner)
    ):
        raise ReductionError(f"INNER_SEAL_MISMATCH:{path.name}")
    return inner


def require(condition: bool, token: str) -> None:
    if not condition:
        raise ReductionError(token)


def traceback_failure_cardinality(serial: bytes) -> dict[str, int]:
    """Separate a traceback source echo from its terminal RuntimeError."""

    source_suffix = f'raise RuntimeError("{FAILURE}")'.encode()
    terminal_suffix = f"RuntimeError: {FAILURE}".encode()
    lines = [line.rstrip() for line in serial.splitlines()]
    return {
        "phrase_occurrence_count": serial.count(FAILURE.encode()),
        "source_echo_occurrence_count": sum(line.endswith(source_suffix) for line in lines),
        "terminal_runtime_error_occurrence_count": sum(
            line.endswith(terminal_suffix) for line in lines
        ),
    }


def analyze() -> dict[str, Any]:
    require(subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() == HEAD, "HEAD_DRIFT")
    require(subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT, text=True).strip() == TREE, "TREE_DRIFT")
    require(subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip() == M.BRANCH, "BRANCH_DRIFT")
    require(subprocess.check_output(["git", "show", "-s", "--format=%s", "HEAD"], cwd=ROOT, text=True).strip() == M.SUBJECT, "SUBJECT_DRIFT")
    require(subprocess.check_output(["git", "remote", "get-url", "origin"], cwd=ROOT, text=True).strip() == ORIGIN, "ORIGIN_DRIFT")
    require(subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True).strip() == "", "INDEX_NOT_EMPTY")

    request = verify_envelope(REQUEST, "request")
    phase_a = verify_envelope(PHASE_A_SAFE_STOP, "checkpoint")
    handoff = verify_envelope(HANDOFF, "authorization")
    consumption = verify_envelope(CONSUMPTION, "checkpoint")
    pre = load_canonical(PRE)
    post = load_canonical(POST)
    runtime_context = load_canonical(RUNTIME_CONTEXT)
    runtime_manifest = verify_envelope(RUNTIME_MANIFEST, "manifest")
    serial = SERIAL.read_bytes()

    require(sha256_path(SOURCE) == SOURCE_SHA256, "HUMAN_SOURCE_DRIFT")
    require(SOURCE.read_text().replace("\\_", "_") == C.EXPECTED_NORMALIZED_GRANT, "HUMAN_GRANT_MISMATCH")
    require(request["generation_identity"] == GENERATION and request["operation_identity"] == OPERATION, "REQUEST_CORRELATION")
    require(sha256_bytes(canonical_bytes(request)) == REQUEST_ID, "REQUEST_IDENTITY")
    require(phase_a["terminal"] == M.PHASE_A_TERMINAL and phase_a["request_identity"] == REQUEST_ID, "PHASE_A_CHECKPOINT")
    require(sha256_bytes(canonical_bytes(phase_a)) == PHASE_A_CHECKPOINT, "PHASE_A_CHECKPOINT_IDENTITY")
    require(sha256_path(HANDOFF) == HANDOFF_SHA256, "AUTHORITY_HANDOFF_IDENTITY")
    require(handoff["authorization_present"] is True and handoff["authorization_reusable"] is False, "AUTHORITY_SEMANTICS")
    require(handoff["authorization_source_sha256"] == SOURCE_SHA256 and handoff["authorized_vector"] == "EXPIRED", "AUTHORITY_CORRELATION")
    require(handoff["authorized_context_sha256"] == CONTEXT and handoff["authorized_canonical_argv_sha256"] == ARGV, "AUTHORITY_LIVE_BINDING")
    require(consumption["human_grant_binding_status"] == "VERIFIED" and consumption["final_admission_validation"] == "PASS", "FINAL_ADMISSION")
    require(consumption["authority_state_after"] == "CONSUMED" and consumption["authority_consumed"] == 1, "AUTHORITY_CONSUMPTION")

    receipt_paths = sorted((JW / "operation_state/receipts").glob("*.json"))
    require(receipt_paths == [POST, PRE], "RECEIPT_PAIR_CARDINALITY")
    common = {
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "authorized_repository_head": HEAD,
        "authorized_repository_tree": TREE,
        "candidate_sha256": CANDIDATE,
        "context_sha256": CONTEXT,
        "human_authorization_source_sha256": SOURCE_SHA256,
        "execution_authority_file_sha256": HANDOFF_SHA256,
        "adapter_sha256": M.EXPECTED_HASHES[M.JR_ADAPTER],
    }
    for key, value in common.items():
        require(pre.get(key) == value and post.get(key) == value, f"RECEIPT_CORRELATION:{key}")
    require(pre["vector"]["canonical_argv_sha256"] == ARGV and post["vector"] == pre["vector"], "ARGV_CORRELATION")
    require(pre["process_exit_status"] is None and post["process_exit_status"] == 0, "QEMU_EXIT_STATUS")
    require(pre["started_unix_ns"] == post["started_unix_ns"] and post["completed_unix_ns"] > post["started_unix_ns"], "RECEIPT_TIME_CORRELATION")
    require(pre["execution_attempt_count"] == post["execution_attempt_count"] == 1, "QEMU_ATTEMPT_COUNT")
    require(pre["automatic_retry_count"] == post["automatic_retry_count"] == 0, "AUTOMATIC_RETRY")

    failure_cardinality = traceback_failure_cardinality(serial)
    require(failure_cardinality["phrase_occurrence_count"] == 2, "EXACT_FAILURE_TRACEBACK_CARDINALITY")
    require(failure_cardinality["source_echo_occurrence_count"] == 1, "EXACT_FAILURE_SOURCE_ECHO_NOT_OBSERVED_ONCE")
    require(failure_cardinality["terminal_runtime_error_occurrence_count"] == 1, "EXACT_TERMINAL_FAILURE_NOT_OBSERVED_ONCE")
    require(b"G77_256FM_BOOT_MARKER=PASS" in serial, "VM_BOOT_NOT_OBSERVED")
    require(b"G77_256FM_HARNESS_EXIT_STATUS=1" in serial, "GUEST_HARNESS_FAILURE_NOT_OBSERVED")
    require(b"Powering off" in serial and b"Power down" in serial, "VM_TEARDOWN_NOT_OBSERVED")
    er_source = ER_HARNESS.read_text(encoding="utf-8")
    require(
        'context["repository_head"] != observed_head' in er_source
        and 'checkout_binding["head"] != observed_head' in er_source
        and f'raise RuntimeError("{FAILURE}")' in er_source,
        "ER_FAILURE_OWNER_NOT_AUTHENTICATED",
    )
    checkout = runtime_context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    require(runtime_context["repository_head"] == HEAD and runtime_context["repository_tree"] == TREE, "ADMISSION_ROLE")
    require((checkout["head"], checkout["tree"]) == (JR_HEAD, JR_TREE), "RUNTIME_ROLE")
    require((HEAD, TREE) != (JR_HEAD, JR_TREE), "EXPECTED_ROLE_SEPARATION_ABSENT")
    require(runtime_manifest["final_execution_seal"] is None, "UNEXPECTED_EXECUTION_SEAL")
    forbidden_runtime = (
        JW / "operation_state/runtime_export/G77_256JW_AUTHORITY_CHECKPOINT_V1.json",
        JW / "operation_state/runtime_export/G77_256JW_PRE_ACT_CHECKPOINT_V1.json",
        JW / "operation_state/runtime_export/G77_256JW_RAW_EXECUTION_EVIDENCE_V1.jsonl",
        JW / "operation_state/runtime_export/G77_256JW_GUEST_EXECUTION_SEAL_V1.json",
    )
    require(not any(path.exists() or path.is_symlink() for path in forbidden_runtime), "UNEXPECTED_POST_CONTEXT_GUEST_EVIDENCE")

    operational = {
        "operational_authorization_count": 1,
        "authority_consumption_count": 1,
        "pre_operational_count": 1,
        "fm_operational_invocation_count": 1,
        "qemu_count": 1,
        "vm_count": 1,
        "operation_attempt_count": 1,
        "expired_check_count": 0,
        "request_count": 0,
        "expired_denial_count": 0,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "retry_count": 0,
        "repair_retry_count": 0,
        "replay_count": 0,
    }
    return {
        "schema_id": "G77_256JW_SPCE_TERMINAL_FAILURE_REDUCTION_V1",
        "generation": "G77-256JW",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "terminal": TERMINAL,
        "result": "FAIL_CLOSED__ER_CONTEXT_CHECKOUT_ROLE_IDENTITY_COLLAPSE_MISMATCH",
        "entry": {
            "head": HEAD,
            "tree": TREE,
            "remote_head": HEAD,
            "branch": M.BRANCH,
            "subject": M.SUBJECT,
            "origin": ORIGIN,
            "worktree": "EXPECTED_DIRTY__UNTRACKED_JW_NAMESPACE_ONLY",
            "index": "VERIFIED__EMPTY",
        },
        "authority": {
            "human_authorization_count": "VERIFIED__1",
            "source_sha256": SOURCE_SHA256,
            "request_identity": REQUEST_ID,
            "phase_a_safe_stop_identity": PHASE_A_CHECKPOINT,
            "correlation": "VERIFIED__EXACT",
            "consumption_count": "VERIFIED__1",
            "state": "VERIFIED__CONSUMED_NONREUSABLE",
            "final_admission": "VERIFIED__PASS",
        },
        "operation": {
            "pre_fm_qemu_vm": "VERIFIED__EXACTLY_ONE",
            "qemu_exit_status": 0,
            "serial_console_sha256": sha256_path(SERIAL),
            "pre_receipt_sha256": sha256_path(PRE),
            "post_receipt_sha256": sha256_path(POST),
            "exact_failure": FAILURE,
            "traceback_phrase_occurrence_count": failure_cardinality["phrase_occurrence_count"],
            "traceback_source_echo_occurrence_count": failure_cardinality["source_echo_occurrence_count"],
            "terminal_failure_occurrence_count": failure_cardinality["terminal_runtime_error_occurrence_count"],
            "failure_owner": ER_HARNESS.relative_to(ROOT).as_posix(),
            "failure_boundary": "BEFORE_EXPIRED_ADAPTER_REQUEST_AND_BEFORE_P11_ENTRY",
            "expected_expired_denial_observed": False,
            "retry_performed": False,
            "repair_performed": False,
            "replay_performed": False,
        },
        "role_mismatch": {
            "admission_repository": {"head": HEAD, "tree": TREE},
            "stable_runtime_checkout": {"head": JR_HEAD, "tree": JR_TREE},
            "checkout_binding_matches_stable_runtime_checkout": True,
            "differing_sealed_fields": ["repository_head", "repository_tree"],
            "er_loader_requires_role_identity_collapse": True,
            "jt_repository_recurrence_hazard_status": "AUTHENTICATED__CLAIMED_ELIMINATED_REPOSITORY_ONLY",
            "jw_operational_recurrence_hazard_status": "VERIFIED__OBSERVED",
        },
        "operational_counters": operational,
        "e05": {
            "before": "VERIFIED__11_OF_18",
            "after": "VERIFIED__11_OF_18",
            "credit": "VERIFIED__0",
            "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
            "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
        },
        "reuse": {
            "ex_reused": "VERIFIED__17_OF_17",
            "ex_reconstructed": "VERIFIED__0",
            "existing_capability_became_unreachable": "VERIFIED__NO",
            "parallel_flow_created": "VERIFIED__NO",
            "production_path_count_effect": "VERIFIED__UNCHANGED__1_TO_1",
        },
        "architecture": {
            "p11_implementation_mutation_count": "VERIFIED__0",
            "production_mutation_count": "VERIFIED__0",
            "new_owner_count": "VERIFIED__0",
            "new_route_count": "VERIFIED__0",
            "new_registry_count": "VERIFIED__0",
            "new_generic_abstraction_count": "VERIFIED__0",
            "new_constitutional_concept_count": "VERIFIED__0",
            "production_route_before": "VERIFIED__1",
            "production_route_after": "VERIFIED__1",
            "production_route_delta": "VERIFIED__0",
        },
        "frontier": {
            "last_verified_edge": "ONE_FRESH_HUMAN_AUTHORIZED_JW_PRE_FM_QEMU_VM_OPERATION_ATTEMPT_EXECUTED_ONCE",
            "first_broken_edge": "ER_SEALED_OPERATION_CONTEXT_ADMISSION_REPOSITORY_TO_RUNTIME_CHECKOUT_IDENTITY_COLLAPSE_VALIDATION",
            "minimum_missing_capability": "ER_GUEST_CONTEXT_VALIDATION_WITH_DISTINCT_ADMISSION_REPOSITORY_AND_STABLE_RUNTIME_CHECKOUT_ROLES",
            "minimum_legal_next_delta": "SEPARATE_REPOSITORY_ONLY_ER_CONTEXT_CHECKOUT_ROLE_SEPARATION_REPAIR_GENERATION",
        },
        "proof_yield": {
            "new_verified_capability_count": "VERIFIED__0__EXPECTED_EXPIRED_DENIAL_NOT_REACHED",
            "new_blocker_localized_count": "VERIFIED__1__ER_CHECKOUT_ROLE_SEPARATION_MISMATCH",
            "e05_credit": "VERIFIED__0",
            "proof_reuse_count": "VERIFIED__17",
        },
        "recovery": {
            "recovery_type": "SAME_GENERATION_PROVIDER_LIMIT_RECOVERY",
            "recovery_source_generation": "G77-256JW",
            "new_generation_created": "VERIFIED__NO",
            "recovery_existing_delta_authenticated": "VERIFIED__YES",
            "recovery_duplicate_authority_consumption_count": "VERIFIED__0",
            "recovery_duplicate_operation_count": "VERIFIED__0",
            "recovery_operation_replay_count": "VERIFIED__0",
            "pre_recovery_jw_file_count_including_bytecode": 31,
            "pre_recovery_jw_file_count_excluding_bytecode": 30,
            "pre_recovery_path_inventory_sha256": "009e5e769501b4e3a95524cea2915dfe73df9e31fb8b9f3e5273866c44ae03df",
            "pre_recovery_file_hash_manifest_sha256": "930d3a3e5a3206686e4271dfeaa3b2df0b8904414e2aaddf96b1f038d7afbc9a",
            "pre_recovery_reducer_sha256": "55f61b59d0e43a5cddeaffa2b5b3806720ffbfaab645584a081b581368c9b625",
            "pre_recovery_reduction_sha256": "514749904b792b05dd0b7507a39d166e84eda5c818c59c3e5df9f276be2642c2",
            "pre_recovery_report_sha256": "4788eecd2009c58d3d8e15a3dea50f11a90a1b0fb62509e0fe334be3352e092f",
            "durable_and_transient_serial_byte_identity": "VERIFIED__SHA256_6de3f0ec500b19f189aac07ba1612c89e86305e8fb8c0d2e7f3195bcea580144",
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION",
            "authenticated_repository_continuation": "VERIFIED__YES",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
            "handoff_reconstruction_success": "VERIFIED__YES",
            "handoff_ambiguity_count": "VERIFIED__0",
            "observed_artifact_level_cross_worker_drift": "VERIFIED__0",
        },
        "human_review_required": True,
        "auto_continuable": False,
    }


def main() -> None:
    args = argparse.ArgumentParser()
    args.add_argument("--write", action="store_true")
    namespace = args.parse_args()
    reduction = analyze()
    envelope = {
        "schema_id": "G77_256JW_SPCE_TERMINAL_FAILURE_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": sha256_bytes(canonical_bytes(reduction)),
    }
    if namespace.write:
        if TERMINAL_PATH.exists() or TERMINAL_PATH.is_symlink():
            raise ReductionError("TERMINAL_REDUCTION_ALREADY_EXISTS")
        TERMINAL_PATH.write_bytes(canonical_bytes(envelope))
    else:
        sys.stdout.buffer.write(canonical_bytes(envelope))


if __name__ == "__main__":
    main()
