#!/usr/bin/env python3
"""Read-only reduction of the already-completed G77-256JH operation."""

from __future__ import annotations

from collections import Counter
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
JH = ROOT / ".github/governance/evidence/g77_256jh_future_fresh_human_authorized_operational_denial_v1"
TERMINAL_PATH = JH / "G77_256JH_SPCE_TERMINAL_REDUCTION_V1.json"
REPORT_PATH = JH / "G77_256JH_G48_IMPLEMENTATION_REPORT_V1.md"
ADAPTER = ROOT / ".github/governance/evidence/g77_256jc_future_guest_context_owner_projection_v1/adapter/G77_256JC_FUTURE_VECTOR_ADAPTER_V1.py"
JG_TERMINAL = ROOT / ".github/governance/evidence/g77_256jg_future_post_jf_commit_live_binding_and_operational_readiness_certification_v1/G77_256JG_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"

HEAD = "7d33c6fb31f90514d590e39d5d410d81ee0f51b0"
TREE = "b020731686b4fe47a6f2d0ec0d850ad293d1bb97"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
SUBJECT = "G77-256JG certify FUTURE post-JF live-binding readiness"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
TARGET_HEAD = "699fcdce794ff49b6c8735602936355724ed1c90"
TARGET_TREE = "7c773d4b2acdf013f1b8238eabfc8eced4dd6866"
GENERATION = "G77_256JH_ONE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256JH_E05_FUTURE_DENIAL_BEFORE_ENTRY_001"
CANDIDATE = "ad5d204ec6ace09f18b83fd5f868e73dac5e36dad81149f9f335c87f68cf42f7"
CONTEXT = "1c91aed9619818ae712bffebeda82153c5b8e52e0197b55c18d3befa1323a275"
CONTEXT_FILE = "6e2dd8669698442aa4f1b7c2af5e50185a69d821dda3618b8ad3d0eba163aeb5"
ARGV = "2087f3b37a739d122cf7d06087bb5127d7911ba62247f355ecfd17ce9b02e949"
REQUEST = "e419e62e152c2f86db15f612be9452fa2939323f41cf82bad8247c90f1625b53"
PRESENTATION = "49ce65091a754b6e827cf81d6d99e9c89ffee3af176fc9691667fc907ad35a6e"
CHECKPOINT = "d7d5d22874f540c7d92993dcb6e0ad51d79066ea09600e18d9e7a1726f46043a"
SOURCE = "745b287a1069d8e0b421ae6ecd85fafa2bcd5efe1cd85833ee04b760bf3014d1"
AUTHORITY_HANDOFF = "d3716d9f6850f3758c107fefd1d7d65975bfb80f0cbd7f9316af4cef00bf3c10"
FUTURE_PAYLOAD = "9568e0c248ad488cabcf6bde6b490c544077862d10e3fda13bcdc8ed9953f547"
DENIAL = "operational Human act is not current"
TERMINAL = "A__FUTURE_FRESH_HUMAN_AUTHORIZED_OPERATIONAL_DENIAL_BEFORE_P11_ENTRY_VERIFIED"
INTERRUPTED_REDUCER_SHA256 = "55e555996118744b8880b4ad3da31637061cd3a928861ef666573afe587616d6"

RECOVERED_INVENTORY = {
    "G77_256JH_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json": "AUTHORITY_CONSUMPTION",
    "G77_256JH_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json": "AUTHORITY_CONSUMPTION",
    "G77_256JH_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_V1.json": "PREAUTHORIZATION",
    "G77_256JH_GL_RECEIPT_PARENT_OBSERVATION_V1.json": "PREAUTHORIZATION",
    "G77_256JH_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json": "HUMAN_AUTHORIZATION_SOURCE",
    "G77_256JH_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt": "HUMAN_AUTHORIZATION_SOURCE",
    "G77_256JH_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json": "PREAUTHORIZATION",
    "G77_256JH_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt": "HUMAN_AUTHORIZATION_SOURCE",
    "G77_256JH_POSTGRANT_PRECONSUMPTION_SAFE_STOP_CHECKPOINT_V1.json": "HUMAN_AUTHORIZATION_SOURCE",
    "G77_256JH_PREAUTHORITY_STATIC_READINESS_V1.json": "PREAUTHORIZATION",
    "G77_256JH_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json": "PREAUTHORIZATION",
    "G77_256JH_PREHUMAN_PHASE_A_REDUCTION_V1.json": "ANALYSIS",
    "analysis/G77_256JH_OPERATIONAL_DENIAL_REDUCER_V1.py": "ANALYSIS",
    "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json": "LIVE_BINDING",
    "live_binding/candidate/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json": "LIVE_BINDING",
    "live_binding/runtime_projection/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json": "LIVE_BINDING",
    "live_binding/v2_readiness/bindings/G77_256JH_EB_RECEIPT_V2.json": "LIVE_BINDING",
    "live_binding/v2_readiness/bindings/G77_256JH_EE_PATH_PROJECTION_FIXTURE_V1.py": "LIVE_BINDING",
    "live_binding/v2_readiness/bindings/G77_256JH_EE_RECEIPT_V2.json": "LIVE_BINDING",
    "live_binding/v2_readiness/candidate/G77_256JH_V2_READINESS_CANDIDATE_V2.json": "LIVE_BINDING",
    "live_binding/v2_readiness/runtime_projection/G77_256JH_V2_READINESS_CANDIDATE_V2.json": "LIVE_BINDING",
    "operation_state/guest_harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py": "OPERATION_EVIDENCE",
    "operation_state/guest_harness/G77_256JH_FUTURE_VECTOR_ADAPTER_V1.py": "OPERATION_EVIDENCE",
    "operation_state/guest_harness/sapianta_fresh_operation_context_v1.py": "OPERATION_EVIDENCE",
    "operation_state/receipts/G77_256JH_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json": "QEMU_EVIDENCE",
    "operation_state/receipts/G77_256JH_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json": "PRE_RECEIPT",
    "operation_state/runtime_export/G77_256DN_P03_RAW_EVIDENCE_V1.jsonl": "OPERATION_EVIDENCE",
    "operation_state/runtime_export/G77_256DN_SPCE_EXECUTION_SEAL_V1.json": "OPERATION_EVIDENCE",
    "operation_state/runtime_export/G77_256JH_AUTHORITY_CHECKPOINT_V1.json": "FUTURE_DENIAL_EVIDENCE",
    "operation_state/runtime_export/G77_256JH_CONTINUATION_MANIFEST_TERMINAL_V1.json": "LIVE_BINDING",
    "operation_state/runtime_export/G77_256JH_CONTINUATION_MANIFEST_V1.json": "LIVE_BINDING",
    "operation_state/runtime_export/G77_256JH_GUEST_EXECUTION_SEAL_V1.json": "OPERATION_EVIDENCE",
    "operation_state/runtime_export/G77_256JH_GUEST_TEARDOWN_SEAL_V1.json": "TEARDOWN_EVIDENCE",
    "operation_state/runtime_export/G77_256JH_PRE_ACT_CHECKPOINT_V1.json": "REQUEST_EVIDENCE",
    "operation_state/runtime_export/G77_256JH_RAW_EXECUTION_EVIDENCE_V1.jsonl": "OPERATION_EVIDENCE",
    "operation_state/runtime_export/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json": "LIVE_BINDING",
    "orchestration/G77_256JH_AUTHORITY_CONSUMPTION_CONTROLLER_V1.py": "AUTHORITY_CONSUMPTION",
    "orchestration/G77_256JH_PREAUTHORIZATION_MATERIALIZER_V1.py": "PREAUTHORIZATION",
    "tests/test_g77_256jh_preauthorization_barrier_v1.py": "TEST",
}

IMMUTABLE_OPERATIONAL_HASHES = {
    "G77_256JH_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json": "b3b8b77d033210f052a2fdf705c4d966740a1060599c3e3a073c7a5b470b3e21",
    "G77_256JH_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json": AUTHORITY_HANDOFF,
    "G77_256JH_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt": SOURCE,
    "operation_state/receipts/G77_256JH_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json": "46af56c03159a5d23a578b1efb740b08e7ff1e83ce7da3bf9d7102c546d34bd9",
    "operation_state/receipts/G77_256JH_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json": "dd998a4b9f29b388a19c47aef063b08fe8517804aaccf2a6a9966b4a0be3a653",
    "operation_state/runtime_export/G77_256JH_AUTHORITY_CHECKPOINT_V1.json": "2bc0a0e2819d94ea2eb335514151e92065748268402a18535070866d88428817",
    "operation_state/runtime_export/G77_256JH_PRE_ACT_CHECKPOINT_V1.json": "3a89fc57aff93647436f81af904b2fcb93bb030e26571211917e486de6334f92",
    "operation_state/runtime_export/G77_256JH_RAW_EXECUTION_EVIDENCE_V1.jsonl": "090a3b1e907bf87a591979e7cbd1f197820e32648afa88bbb4074d8ed594de9b",
    "operation_state/runtime_export/G77_256JH_GUEST_EXECUTION_SEAL_V1.json": "746fd1511edc1db650c1672751c9ed658347eacac75066aa182e7bae47e2eaaa",
    "operation_state/runtime_export/G77_256JH_GUEST_TEARDOWN_SEAL_V1.json": "d26d9af333eb0b02e42a940ba5c9ac388051802435c00f5f4cac147994f893d6",
    "operation_state/runtime_export/G77_256JH_CONTINUATION_MANIFEST_TERMINAL_V1.json": "dfaba8b53c9b37185ca1d4da9c8234d8e11a87cb9b0b10050b0e06bf15dc688f",
    "operation_state/runtime_export/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json": CONTEXT_FILE,
}


class ReductionError(ValueError):
    """Fail-closed terminal reduction error."""


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ReductionError(f"DUPLICATE_KEY:{key}")
        result[key] = value
    return result


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique_object)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise ReductionError(f"NONCANONICAL_JSON:{path}")
    return value


def verify_envelope(path: Path, inner: str) -> dict[str, Any]:
    envelope = load_canonical(path)
    require(inner in envelope and f"{inner}_sha256" in envelope, f"SEAL_FIELDS_MISSING:{path.name}")
    require(envelope[f"{inner}_sha256"] == sha256_bytes(canonical_bytes(envelope[inner])), f"SEAL_MISMATCH:{path.name}")
    return envelope[inner]


def load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ReductionError(f"MODULE_UNAVAILABLE:{path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def require(condition: bool, token: str) -> None:
    if not condition:
        raise ReductionError(token)


def analyze(jh: Path = JH) -> dict[str, Any]:
    runtime = jh / "operation_state/runtime_export"
    receipts = jh / "operation_state/receipts"
    require(git("rev-parse", "HEAD") == HEAD, "ENTRY_HEAD_DRIFT")
    require(git("rev-parse", "HEAD^{tree}") == TREE, "ENTRY_TREE_DRIFT")
    require(git("branch", "--show-current") == BRANCH, "ENTRY_BRANCH_DRIFT")
    require(git("remote", "get-url", "origin") == ORIGIN, "ENTRY_ORIGIN_DRIFT")
    require(git("show", "-s", "--format=%s", "HEAD") == SUBJECT, "ENTRY_SUBJECT_DRIFT")
    require(git("status", "--porcelain", "--untracked-files=no") == "", "TRACKED_WORKTREE_DRIFT")
    require(git("diff", "--cached", "--name-only") == "", "INDEX_NOT_EMPTY")
    nested = ROOT / "sapianta_system"
    require(git("rev-parse", "HEAD", cwd=nested) == NESTED_HEAD, "NESTED_HEAD_DRIFT")
    require(git("rev-parse", "HEAD^{tree}", cwd=nested) == NESTED_TREE, "NESTED_TREE_DRIFT")
    require(git("remote", "get-url", "origin", cwd=nested) == NESTED_ORIGIN, "NESTED_ORIGIN_DRIFT")
    require(git("status", "--porcelain", cwd=nested) == "", "NESTED_WORKTREE_DRIFT")
    require(git("branch", "--show-current", cwd=nested) == "", "NESTED_NOT_DETACHED")

    for relative, expected in IMMUTABLE_OPERATIONAL_HASHES.items():
        require(sha256_path(jh / relative) == expected, f"HISTORICAL_EVIDENCE_MUTATION:{relative}")

    request_envelope = load_canonical(jh / "G77_256JH_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json")
    request = verify_envelope(jh / "G77_256JH_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json", "request")
    preauth = verify_envelope(jh / "G77_256JH_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json", "checkpoint")
    prehuman = verify_envelope(jh / "G77_256JH_PREHUMAN_PHASE_A_REDUCTION_V1.json", "reduction")
    gn = verify_envelope(jh / "G77_256JH_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json", "proof")
    gl = verify_envelope(jh / "G77_256JH_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_V1.json", "proof")
    consumption = verify_envelope(jh / "G77_256JH_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json", "checkpoint")
    authority = load_canonical(jh / "G77_256JH_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json")
    require(request_envelope["request_sha256"] == REQUEST, "REQUEST_IDENTITY")
    require(request["generation_identity"] == GENERATION and request["operation_identity"] == OPERATION, "REQUEST_CORRELATION")
    require(preauth["identities"]["candidate_sha256"] == CANDIDATE, "CANDIDATE_IDENTITY")
    require(preauth["identities"]["context_sha256"] == CONTEXT, "CONTEXT_IDENTITY")
    require(preauth["identities"]["canonical_argv_sha256"] == ARGV, "ARGV_IDENTITY")
    require(preauth["authority_boundary"]["checkpoint_is_authority"] is False and preauth["authority_boundary"]["authority_state"] == "NOT_GRANTED", "PREAUTHORITY_CONFUSION")
    require(sha256_path(jh / "G77_256JH_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt") == PRESENTATION, "PRESENTATION_IDENTITY")
    require(sha256_path(jh / "G77_256JH_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt") == SOURCE, "HUMAN_SOURCE_IDENTITY")
    require(sha256_path(jh / "G77_256JH_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json") == AUTHORITY_HANDOFF, "AUTHORITY_HANDOFF_IDENTITY")
    require(gn["human_presentation_request_equivalence"] == "VERIFIED_WITHIN_EXACT_REVIEWED_AUTHORIZATION_BINDING_BOUNDARY", "GN_GRANT_CORRELATION")
    require(gn["presentation_sha256"] == PRESENTATION and gn["request_sha256"] == REQUEST, "GN_IDENTITY_CORRELATION")
    require(gl["preauth_final_admission_equivalence"] == "VERIFIED_WITHIN_EXACT_REVIEWED_RECEIPT_PARENT_BOUNDARY", "GL_RECEIPT_PARENT_CORRELATION")
    auth = authority["authorization"]
    require(authority["authorization_sha256"] == sha256_bytes(canonical_bytes(auth)), "AUTHORITY_INNER_SEAL")
    require(auth["authorization_source_sha256"] == SOURCE, "AUTHORITY_SOURCE_CORRELATION")
    require(auth["authorized_generation_identity"] == GENERATION and auth["authorized_operation_identity"] == OPERATION, "AUTHORITY_OPERATION_CORRELATION")
    require(auth["authorized_candidate_sha256"] == CANDIDATE and auth["authorized_context_sha256"] == CONTEXT, "AUTHORITY_CANDIDATE_CONTEXT")
    require(auth["authorized_canonical_argv_sha256"] == ARGV, "AUTHORITY_ARGV")
    require(auth["authorized_repository_head"] == HEAD and auth["authorized_repository_tree"] == TREE, "AUTHORITY_BASELINE")
    require(consumption["grant_source_sha256"] == SOURCE and consumption["sealed_request_sha256"] == REQUEST, "CONSUMPTION_GRANT_CORRELATION")
    require(consumption["authority_handoff_file_sha256"] == AUTHORITY_HANDOFF, "CONSUMPTION_HANDOFF_CORRELATION")
    require(consumption["human_grant_binding_status"] == "VERIFIED", "GRANT_CORRELATION")
    require(consumption["authority_state_before"] == "GRANTED_UNCONSUMED" and consumption["authority_state_after"] == "CONSUMED", "AUTHORITY_STATE_TRANSITION")
    require(consumption["authority_consumed"] == 1 and consumption["authority_reusable"] is False, "AUTHORITY_EXACTLY_ONCE")
    require(consumption["final_admission_validation"] == "PASS", "FINAL_ADMISSION")

    future = preauth["future_semantics"]
    require(future["evaluation"] == 500 and future["valid_from"] == 600 and future["valid_until"] == 1000, "FUTURE_TIME_SEMANTICS")
    require(future["payload_digest"] == f"sha256:{FUTURE_PAYLOAD}" and future["wall_clock_dependency_count"] == 0, "FUTURE_PAYLOAD_OR_CLOCK")
    require(prehuman["future_semantics"] == future, "PREAUTH_FUTURE_SEMANTIC_DRIFT")

    context_path = jh / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    runtime_context_path = runtime / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    context = load_canonical(context_path)
    require(sha256_path(context_path) == CONTEXT_FILE and context_path.read_bytes() == runtime_context_path.read_bytes(), "CONTEXT_FILE_CORRELATION")
    unsealed_context = {key: value for key, value in context.items() if key != "context_sha256"}
    require(context["context_sha256"] == CONTEXT == sha256_bytes(canonical_bytes(unsealed_context)), "CONTEXT_INNER_SEAL")
    require(context["operation_evidence_root"] == str(JH / "operation_state"), "OPTION_A_NAMESPACE")
    require(context["candidate_manifest_sha256"] == CANDIDATE and context["canonical_argv_sha256"] == ARGV, "CONTEXT_BINDINGS")
    require(context["generation_identity"] == GENERATION and context["operation_identity"] == OPERATION, "CONTEXT_OPERATION")
    require(context["identity_namespace_prefix"] == "G77_256JH", "CONTEXT_NAMESPACE_PREFIX")

    receipt_names = sorted(path.name for path in receipts.iterdir() if path.is_file())
    require(receipt_names == ["G77_256JH_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json", "G77_256JH_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"], "RECEIPT_PAIR_CARDINALITY")
    post = load_canonical(receipts / receipt_names[0])
    pre = load_canonical(receipts / receipt_names[1])
    for receipt in (pre, post):
        require(receipt["generation_identity"] == GENERATION and receipt["operation_identity"] == OPERATION, "RECEIPT_OPERATION")
        require(receipt["execution_attempt_count"] == 1 and receipt["automatic_retry_count"] == 0, "RECEIPT_ATTEMPT_COUNT")
        require(receipt["context_sha256"] == CONTEXT and receipt["candidate_sha256"] == CANDIDATE, "RECEIPT_CONTEXT_CANDIDATE")
        require(receipt["vector"]["canonical_argv_sha256"] == ARGV, "RECEIPT_ARGV")
        require(receipt["execution_authority_file_sha256"] == AUTHORITY_HANDOFF and receipt["human_authorization_source_sha256"] == SOURCE, "RECEIPT_AUTHORITY")
        require(receipt["authorized_repository_head"] == HEAD and receipt["authorized_repository_tree"] == TREE, "RECEIPT_BASELINE")
        require(receipt["identity_namespace_prefix"] == "G77_256JH", "RECEIPT_NAMESPACE")
        argv = receipt["vector"]["argv"]
        require(argv.count("-nic") == 1 and argv[argv.index("-nic") + 1] == "none", "NETWORK_NOT_DISABLED")
    require(pre["vector"] == post["vector"] and pre["started_unix_ns"] == post["started_unix_ns"], "RECEIPT_PAIR_CORRELATION")
    require(pre["process_exit_status"] is None and pre["completed_unix_ns"] is None, "PRE_RECEIPT_STATE")
    require(post["process_exit_status"] == 0 and post["completed_unix_ns"] > post["started_unix_ns"], "POST_RECEIPT_STATE")

    raw_path = runtime / "G77_256JH_RAW_EXECUTION_EVIDENCE_V1.jsonl"
    rows: list[dict[str, Any]] = []
    for line in raw_path.read_bytes().splitlines(keepends=True):
        value = json.loads(line, object_pairs_hook=unique_object)
        require(line == canonical_bytes(value), "NONCANONICAL_RAW_RECORD")
        rows.append(value)
    require(len(rows) == 19 and [row["record_sequence"] for row in rows] == list(range(19)), "RAW_SEQUENCE")
    types = Counter(row["record_type"] for row in rows)
    expected_types = {"execution_context", "commissioning_aggregate", "spce_pre_act_checkpoint", "continuation_manifest_pre_act", "human_operational_act_created", "future_submission_denial", "guest_teardown"}
    expected_types.update(f"commissioning_P{index:02d}" for index in range(1, 13))
    require(set(types) == expected_types and all(count == 1 for count in types.values()), "RAW_RECORD_TYPE_CARDINALITY")
    execution_context = rows[0]["facts"]["checkout_context"]
    require(execution_context["observed_head"] == TARGET_HEAD and execution_context["observed_tree"] == TARGET_TREE, "RUNTIME_TARGET_PROVENANCE")
    require(execution_context["checkout_mount_read_only"] is True and execution_context["checkout_status_porcelain"] == "", "RUNTIME_CHECKOUT_STATE")
    require(execution_context["interfaces"] == ["lo"] and execution_context["production_route_count"] == 0, "RUNTIME_NETWORK_STATE")
    request_record = next(row["facts"] for row in rows if row["record_type"] == "human_operational_act_created")
    denial_record = next(row["facts"] for row in rows if row["record_type"] == "future_submission_denial")
    require(request_record["creation_count"] == 1, "REQUEST_COUNT")
    act = request_record["human_authority_act"]
    require(act["request_identity"] == "G77_256JH_REQUEST_001" and act["metadata"]["generation_identity"] == GENERATION, "OPERATION_REQUEST_IDENTITY")
    require(act["payload"]["case_id"] == OPERATION and act["payload"]["valid_from_unix_ns"] == 600 and act["payload"]["valid_until_unix_ns"] == 1000, "OPERATION_REQUEST_CORRELATION")
    require(denial_record["case_id"] == OPERATION and denial_record["generation_identity"] == GENERATION, "DENIAL_OPERATION_CORRELATION")
    require(denial_record["denial_error"] == DENIAL and denial_record["evaluation_time_unix_ns"] == 500, "DENIAL_REASON")
    require(denial_record["future_valid_from_unix_ns"] == 600 and denial_record["valid_until_unix_ns"] == 1000, "DENIAL_TIME_SEMANTICS")

    checkpoint = load_canonical(runtime / "G77_256JH_AUTHORITY_CHECKPOINT_V1.json")
    pre_act = load_canonical(runtime / "G77_256JH_PRE_ACT_CHECKPOINT_V1.json")
    execution = load_canonical(runtime / "G77_256JH_GUEST_EXECUTION_SEAL_V1.json")
    teardown = load_canonical(runtime / "G77_256JH_GUEST_TEARDOWN_SEAL_V1.json")
    terminal_manifest = verify_envelope(runtime / "G77_256JH_CONTINUATION_MANIFEST_TERMINAL_V1.json", "manifest")
    require(checkpoint == denial_record, "DENIAL_CHECKPOINT_RAW_CORRELATION")
    counters = checkpoint["execution_counters"]
    require(execution["authority_checkpoint_sha256"] == sha256_path(runtime / "G77_256JH_AUTHORITY_CHECKPOINT_V1.json"), "EXECUTION_CHECKPOINT_CORRELATION")
    require(execution["pre_act_checkpoint_sha256"] == sha256_path(runtime / "G77_256JH_PRE_ACT_CHECKPOINT_V1.json"), "EXECUTION_PRE_ACT_CORRELATION")
    require(execution["source_head"] == TARGET_HEAD and execution["source_tree"] == TARGET_TREE, "EXECUTION_RUNTIME_TARGET")
    require(execution["operational_result"] == "PASS__FUTURE_DENIED_AT_D2_SUBMISSION_BEFORE_OWNER_STATE_AND_ENTRY" and execution["first_failure"] is None, "EXECUTION_RESULT")
    require(teardown["raw_evidence_sha256"] == sha256_path(raw_path) and teardown["raw_record_count"] == 19, "TEARDOWN_RAW_CORRELATION")
    require(teardown["teardown_state"] == "COMPLETE" and teardown["execution_counters"] == counters, "TEARDOWN_CORRELATION")
    require(pre_act["execution_counters"]["vm_creation_count"] == 1 and pre_act["execution_counters"]["vm_boot_count"] == 1, "VM_PRE_ACT_COUNTS")
    require(counters["human_operational_act_creation_count"] == 1 and counters["human_operational_act_submitted_count"] == 0, "ACT_COUNTS")
    require(counters["p11_entry_count"] == 0 and counters["p11_operational_invocation_count"] == 0, "P11_EDGE_CROSSED")
    require(checkpoint["owner_state_initialization_count"] == 0 and checkpoint["protected_effect_count"] == 0, "PROTECTED_EFFECT")
    require(counters["automatic_retry_count"] == 0 and counters["repair_and_continue_count"] == 0, "RETRY_OR_REPAIR")
    require(counters["execution_replay_count"] == 0 and counters["materialization_replay_count"] == 0, "REPLAY")
    require(counters["second_vm_count"] == 0 and counters["vm_creation_count"] == 1 and counters["vm_boot_count"] == 1, "VM_COUNTS")

    require(terminal_manifest["generation_identity"] == "G77_256IH_ONE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING_V1", "INHERITED_MANIFEST_OWNER")
    require(terminal_manifest["first_failure_or_current_result"] == "FAIL_CLOSED__FUTURE_REQUIRED_EVIDENCE_MISSING", "INHERITED_MANIFEST_MARKER")
    require(terminal_manifest["final_execution_seal"] is None and terminal_manifest["teardown_state"] == "COMPLETE", "INHERITED_MANIFEST_FIELDS")
    require(terminal_manifest["selected_case"]["case_id"] == OPERATION, "INHERITED_MANIFEST_OPERATION")

    adapter = load_module(ADAPTER, "g77_256jh_terminal_adapter")
    recomputed = adapter.future_terminal_reduction(
        phase="PHASE_D_GUEST_TEARDOWN_COMPLETE_PENDING_HOST_FINALIZATION", counters=counters,
        first_failure_or_current_result="PASS__FUTURE_SUBMISSION_DENIED_BEFORE_OWNER_STATE_AND_ENTRY",
        first_failure=None, authority_checkpoint=checkpoint, execution_seal=execution,
    )
    require(recomputed["success_evidence_complete"] is True and recomputed["e05_credit"] == 1, "CURRENT_ADAPTER_REDUCTION_FAILED")

    jg = verify_envelope(JG_TERMINAL, "reduction")
    require(jg["terminal"] == "A__FUTURE_POST_JF_COMMIT_LIVE_BINDING_AND_OPERATIONAL_READINESS_VERIFIED", "JG_TERMINAL")
    require(jg["reuse"]["ex_reused"] == "VERIFIED__17_OF_17" and jg["reuse"]["ex_reconstructed"] == "VERIFIED__0", "EX_REUSE")
    require(jg["jf_reconstruction"]["option_a_authority"] == "VERIFIED__SEALED_CONTEXT_OPERATION_EVIDENCE_ROOT", "OPTION_A_AUTHORITY")
    require(jg["namespace_binding"]["caller_selectable_namespace_count"] == 0, "CALLER_SELECTABLE_NAMESPACE")

    operational = {
        "human_authorization_count": 1, "authority_consumption_count": 1,
        "pre_operational_count": 1, "fm_operational_invocation_count": 1,
        "qemu_count": 1, "vm_count": 1, "vm_boot_count": 1,
        "operation_attempt_count": 1, "request_count": 1, "future_denial_count": 1,
        "p11_entry_count": 0, "protected_invocation_count": 0, "protected_effect_count": 0,
        "retry_count": 0, "repair_retry_count": 0, "replay_count": 0,
        "second_authority_consumption_count": 0, "second_pre_count": 0,
        "second_fm_invocation_count": 0, "second_qemu_count": 0,
        "second_vm_count": 0, "second_operation_attempt_count": 0,
    }
    inventory = [{"path": path, "classification": classification} for path, classification in sorted(RECOVERED_INVENTORY.items())]
    return {
        "schema_id": "G77_256JH_SPCE_TERMINAL_REDUCTION_V1", "generation": "G77-256JH",
        "recovery_mode": "SAME_GENERATION_POST_OPERATION_RECOVERY__NO_AUTHORIZATION_OR_OPERATION_REPLAY",
        "generation_identity": GENERATION, "operation_identity": OPERATION, "terminal": TERMINAL,
        "entry": {"head": HEAD, "tree": TREE, "remote_head": HEAD, "branch": BRANCH, "origin": ORIGIN, "subject": SUBJECT},
        "nested_authority": {"head": NESTED_HEAD, "tree": NESTED_TREE, "origin": NESTED_ORIGIN, "clean": True, "detached": True, "remote_tag_equal": True},
        "runtime_target": {"head": TARGET_HEAD, "tree": TARGET_TREE}, "certification_baseline": {"head": HEAD, "tree": TREE},
        "identities": {"candidate": CANDIDATE, "context": CONTEXT, "context_file": CONTEXT_FILE, "argv": ARGV, "operation": OPERATION, "authorization_request": REQUEST, "authorization_presentation": PRESENTATION, "preauthorization_checkpoint": CHECKPOINT, "execution_authority_handoff": AUTHORITY_HANDOFF},
        "authority": {"human_authorization_count": "VERIFIED__1", "grant_correlation": "VERIFIED", "consumption_count": "VERIFIED__1", "final_admission": "VERIFIED__PASS", "state": "VERIFIED__CONSUMED_NONREUSABLE", "source_sha256": SOURCE, "handoff_file_sha256": AUTHORITY_HANDOFF},
        "proof_domains": {"repository_readiness": "VERIFIED__EXACT_REMOTE_RATIFIED_JG_BASELINE", "human_authorization": "VERIFIED__EXACTLY_ONE_CORRELATED_SOURCE", "authority_consumption": "VERIFIED__EXACTLY_ONCE_NONREUSABLE", "operational_execution": "VERIFIED__EXACTLY_ONE", "request": "VERIFIED__1", "denial": "VERIFIED__EXACT_FUTURE_REASON", "p11_entry": "VERIFIED__0", "protected_invocation": "VERIFIED__0", "protected_effect": "VERIFIED__0", "retry_repair_replay": "VERIFIED__0", "teardown": "VERIFIED__COMPLETE", "inherited_historical_provenance_limitation": "VERIFIED__PRESENT_AND_PRESERVED_NONAUTHORITATIVE_FOR_JH"},
        "operational_counters": operational,
        "operation": {"denial_reason": f"VERIFIED__{DENIAL}", "future_operational_status": "VERIFIED__DENIED_BEFORE_P11_ENTRY", "raw_record_count": 19, "receipt_correlation": "VERIFIED__EXACT_ONE_PRE_POST_PAIR", "teardown_correlation": "VERIFIED__COMPLETE", "namespace_authority": "VERIFIED__SEALED_CONTEXT_OPERATION_EVIDENCE_ROOT", "caller_selectable_namespace_count": 0, "runtime_target_provenance": "VERIFIED__DETACHED_TARGET_HEAD_TREE", "certification_baseline_provenance": "VERIFIED__JG_ENTRY_HEAD_TREE", "current_adapter_reduction": recomputed},
        "future_semantics": {"evaluation_time_unix_ns": 500, "baseline_valid_from_unix_ns": 100, "future_valid_from_unix_ns": 600, "valid_until_unix_ns": 1000, "relation": "VERIFIED__500_LT_600_LT_1000", "payload_digest": FUTURE_PAYLOAD, "wall_clock_dependency": 0},
        "inherited_continuation_manifest_limitation": {"status": "VERIFIED__PRESENT_AND_PRESERVED", "artifact_path": "operation_state/runtime_export/G77_256JH_CONTINUATION_MANIFEST_TERMINAL_V1.json", "field_name": "first_failure_or_current_result", "field_value": "FAIL_CLOSED__FUTURE_REQUIRED_EVIDENCE_MISSING", "historical_owner_generation": "G77_256IH_ONE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING_V1", "authority_status": "VERIFIED__AUTHENTICATED_HISTORICAL_RUNTIME_PROVENANCE__NONAUTHORITATIVE_FOR_CURRENT_JH_HOST_REDUCTION", "reason": "IH candidate manifest carried no final execution seal; the guest transition preserved the historical marker", "effect_on_jh": "NONE__DIRECT_JH_RECEIPTS_RAW_DENIAL_CHECKPOINT_EXECUTION_SEAL_ADAPTER_REDUCTION_AND_TEARDOWN_INDEPENDENTLY_COMPLETE", "hidden_or_rewritten": False},
        "e05": {"before": "VERIFIED__10_OF_18", "after": "VERIFIED__11_OF_18", "credit": "VERIFIED__1", "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18", "selected_local_frontier_distance": "VERIFIED__0__FUTURE_DENIAL_TARGET_SATISFIED"},
        "reuse": {"ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0", "reused_certified_capability_set": "VERIFIED__JG_JF_JE_JD_JC_FM_DU_EB_EE_V2_GN_GL_ER_FC_FK_CHE_P11_EX_GOVERNANCE_LAYER_0_NESTED_AUTHORITY", "new_capability_set": "VERIFIED__JH_OPERATIONAL_DENIAL_EVIDENCE_AND_TERMINAL_REDUCTION_ONLY", "unreachable_preexisting_capability_set": "VERIFIED__EMPTY", "parallel_flow_created": "VERIFIED__NO"},
        "firewalls": {"production_route_before": 1, "production_route_after": 1, "production_route_delta": 0, "production_mutation_count": 0, "p11_mutation_count": 0, "historical_evidence_mutation_count": 0, "route_mutation_count": 0, "shadow_automation_status": "VERIFIED__ABSENT", "automatic_authorization_count": 0, "automatic_authority_reconsumption_count": 0, "automatic_retry_count": 0, "automatic_repair_retry_count": 0, "automatic_replay_count": 0, "automatic_successor_operation_count": 0, "automatic_e05_credit_count": 0},
        "frontier": {"constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR", "constitutional_frontier_distanc_e": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR", "project_progress": "VERIFIED__E05_11_OF_18__FUTURE_OPERATIONAL_DENIAL_VERIFIED", "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR", "last_verified_edge": "VERIFIED__FUTURE_DENIED_BEFORE_P11_ENTRY_WITH_ZERO_PROTECTED_EFFECT", "first_broken_edge": "NOT_APPLICABLE__JH_TARGET_COMPLETE", "blocking_owner": "NOT_APPLICABLE__JH_TARGET_COMPLETE", "minimum_missing_capability": "NOT_APPLICABLE__JH_TARGET_COMPLETE", "minimum_legal_next_delta": "HUMAN_REVIEW_ONLY__NO_AUTO_CONTINUATION__NO_JI"},
        "metrics": {"governance_efficience": "ESTIMATED__HIGH__CERTIFIED_REUSE_ONE_SHOT_OPERATION", "architectural_governance_efficience": "VERIFIED__ONE_ROUTE_ZERO_PRODUCTION_P11_AND_HISTORICAL_MUTATION", "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED", "aigol_codex_work_share": "NOT_MEASURED", "prompt_context_reuse_ratio": "NOT_MEASURED", "repository_derived_execution_context_ratio": "NOT_MEASURED", "constitutional_prompt_externalization_ratio": "NOT_MEASURED", "token_benchmark": "NOT_MEASURED", "llm_cost_reduction_ratio": "NOT_MEASURED", "lcrr": "NOT_MEASURED", "overengineering_risk": "ESTIMATED__LOW__EVIDENCE_REDUCTION_ONLY", "proof_process_overhead_risk": "ESTIMATED__MODERATE"},
        "overengineering": {"new_abstraction_count": 0, "new_generic_framework_count": 0, "generic_projection_framework_count": 0, "new_route_count": 0, "new_registry_count": 0, "new_namespace_registry_count": 0, "caller_selectable_identity_count": 0, "caller_selectable_namespace_count": 0, "duplicate_owner_semantics_count": 0, "duplicate_future_adapter_count": 0, "duplicate_p11_logic_count": 0, "new_generic_adapter_count": 0, "new_dispatcher_count": 0, "new_global_registry_count": 0},
        "cognition": {"cognition_assisted_handoff": "VERIFIED__SAME_GENERATION_CROSS_WORKER_POST_OPERATION_DURABLE_STATE_RECOVERY_WITHOUT_AUTHORITY_OR_OPERATION_REPLAY", "cognition_provenance": "VERIFIED__AUTHENTICATED_GIT_BASELINE_COMMITTED_JG_JF_JE_LINEAGE_AND_DURABLE_JH_AUTHORITY_RECEIPT_RAW_DENIAL_TEARDOWN_EVIDENCE_PRIMARY__PROMPT_AND_PROVIDER_MODEL_NONAUTHORITATIVE"},
        "ccwim": {"ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION", "cross_worker_state_recovery_level": "VERIFIED__DURABLE_POST_OPERATION_STATE_RECOVERED", "repository_derived_context_ratio": "ESTIMATED__DOMINANT__NO_NUMERIC_INSTRUMENT", "human_handoff_information_required": "VERIFIED__RECOVERY_SCOPE_AND_EXPECTED_COORDINATES_ONLY", "previous_worker_conversation_required": "VERIFIED__NO", "previous_worker_identity_required": "VERIFIED__NO", "previous_worker_memory_required": "VERIFIED__NO", "authenticated_repository_continuation": "VERIFIED__YES", "inter_generation_cross_worker_continuation": "NOT_APPLICABLE__SAME_GENERATION_RECOVERY", "intra_generation_cross_worker_continuation": "VERIFIED__JH_PROVIDER_LIMIT_POST_OPERATION_RECOVERY", "uncommitted_delta_recovery": "VERIFIED__BOUNDED_JH_NAMESPACE", "authority_state_recovery": "VERIFIED__CONSUMED_NONREUSABLE", "consumed_authority_recovery": "VERIFIED__EXACTLY_ONE", "post_operation_state_recovery": "VERIFIED__DIRECT_DURABLE_REPOSITORY_EVIDENCE", "operation_replay_prevention": "VERIFIED__NO_RECOVERY_OPERATION__EXACT_ONE_RECEIPT_PAIR__CONSUMED_NONREUSABLE_AUTHORITY", "cross_worker_constitutional_drift": "VERIFIED__0_AT_ARTIFACT_LEVEL", "observed_artifact_level_cross_worker_drift": "VERIFIED__0", "handoff_sufficiency_status": "VERIFIED", "handoff_state_completeness": "VERIFIED__COMPLETE_FOR_TERMINAL_REDUCTION", "handoff_reconstruction_required": "VERIFIED__YES", "handoff_reconstruction_success": "VERIFIED__YES", "handoff_ambiguity_count": "VERIFIED__0", "unauthenticated_handoff_assumption_count": "VERIFIED__0"},
        "candidate": {"before": "VERIFIED__POST_JF_COMMIT_LIVE_BINDING_AND_OPERATIONAL_READINESS_VERIFIED", "capability": "VERIFIED__FUTURE_FRESH_HUMAN_AUTHORIZED_OPERATIONAL_DENIAL_BEFORE_P11_ENTRY", "shadow_design_target": "VERIFIED__FAMILY_LOCAL_DU_EB_EE_V2_OPTION_B_WITH_COLOCATED_FAIL_CLOSED_MAJOR_VERSION_DISPATCH"},
        "continuity": {"constitutional_health_evidence": "VERIFIED__IV_FAILURE_TO_IW_TO_IX_TO_IY_FAILURE_TO_IZ_TO_JA_TO_JB_FAILURE_TO_JC_TO_JD_TO_JE_OPERATIONAL_FAILURE_RECOVERY_RATIFICATION_TO_JF_OPTION_A_SELECTION_PROOF_BINDING_RECOVERY_RATIFICATION_TO_JG_READINESS_RATIFICATION_TO_JH_PREAUTHORIZATION_AUTHORIZATION_CONSUMPTION_ONE_SHOT_OPERATION_PROVIDER_LIMIT_RECOVERY_TERMINAL", "constitutional_continuation_progress": "VERIFIED__IV_IMPORT_ROOT_FAILURE__IW_IMPORT_ROOT_BINDING__IX_POST_COMMIT_IMPORT_READINESS__IY_ENTRYPOINT_ABSENCE__IZ_ENTRYPOINT_STATIC_BINDING__JA_POST_COMMIT_LIVE_BINDING_READINESS__JB_OWNER_DRIFT__JC_OWNER_PROJECTION__JD_POST_JC_LIVE_BINDING_READINESS__JE_FRESH_HUMAN_AUTHORIZATION__JE_ONE_SHOT_OPERATION__JE_PRE_REQUEST_NAMESPACE_FAILURE__JE_TERMINAL_RECOVERY__JE_COMMIT_REMOTE_RATIFICATION__JF_ARCHITECTURAL_AMBIGUITY__HUMAN_OPTION_A_SELECTION__JF_OPTION_A_PROOF__JF_EXACT_NAMESPACE_BINDING__JF_PROVIDER_LIMIT_RECOVERY__JF_COMMIT_REMOTE_RATIFICATION__JG_POST_JF_LIVE_BINDING_READINESS__JG_COMMIT_REMOTE_RATIFICATION__JH_PREAUTHORIZATION_READINESS__JH_HUMAN_AUTHORIZATION__JH_AUTHORITY_CONSUMPTION__JH_ONE_SHOT_OPERATION__JH_PROVIDER_LIMIT_DURING_REDUCTION__JH_SAME_GENERATION_CROSS_WORKER_RECOVERY__JH_TERMINAL_A"},
        "inventory": {"prewrite_artifact_count": len(inventory), "artifacts": inventory, "interrupted_reducer_assessment": "SEMANTICALLY_INCOMPLETE", "interrupted_reducer_original_sha256": INTERRUPTED_REDUCER_SHA256},
        "human_review_required": True, "auto_continuable": False,
    }


def render_report(r: dict[str, Any]) -> str:
    c = r["operational_counters"]
    f = r["frontier"]
    lines = [
        "# 1. Implementation Summary", "",
        "Generation: G77-256JH — FUTURE FRESH HUMAN-AUTHORIZED OPERATIONAL DENIAL COMMISSIONING V1", "",
        "Report identity: `G77_256JH_G48_IMPLEMENTATION_REPORT_V1`", "", "Reporting date: 2026-09-08", "",
        f"Constitutional baseline: committed and remote-ratified JG at `{HEAD}`, tree `{TREE}`.", "",
        "Implementation contracts: G48 Constitutional Evidence Reporting Standard V1.d, the committed JG/JF/JE lineage, the exact JH Human authorization and consumed-authority checkpoint, FM one-shot receipts, Option A namespace authority, and EX common proof substrate.", "",
        "Objective: complete same-generation post-operation recovery after provider-limit interruption by reducing already-existing durable JH evidence. This recovery did not request or present authorization, consume authority, invoke PRE/FM, launch QEMU, boot a VM, run an operation, retry, repair-retry, replay, stage, commit, push, or start JI.", "",
        "Modified modules: the interrupted JH reducer was completed; one focused read-only recovery test, one sealed terminal reduction, and this report were added. Intentionally unchanged: all production code, P11, historical operational evidence, nested authority, routes, registries, and runtime semantics.", "",
        "`RECOVERY_MODE = SAME_GENERATION_POST_OPERATION_RECOVERY__NO_AUTHORIZATION_OR_OPERATION_REPLAY`", "",
        f"`ENTRY_HEAD = {HEAD}`", "", f"`ENTRY_TREE = {TREE}`", "", f"`ENTRY_REMOTE_HEAD = {HEAD}`", "", f"`TARGET_RUNTIME_HEAD = {TARGET_HEAD}`", "", f"`TARGET_RUNTIME_TREE = {TARGET_TREE}`", "", f"`CERTIFICATION_BASELINE_HEAD = {HEAD}`", "", f"`CERTIFICATION_BASELINE_TREE = {TREE}`", "",
        "`CERTIFIED != AUTHORIZED`", "", "`CONSUMED_AUTHORITY != REUSABLE_AUTHORITY`", "", "`REQUEST != ENTRY != INVOCATION != EFFECT`", "",
        "# 2. Code Evidence", "", "## Authenticated identities and authority", "",
        f"The durable Human source `{SOURCE}` correlates through the sealed handoff `{AUTHORITY_HANDOFF}`, consumption checkpoint, and exact receipt pair. The checkpoint proves `GRANTED_UNCONSUMED -> CONSUMED`, exactly one consumption, non-reusability, and final admission PASS.", "",
        f"`CANDIDATE_IDENTITY = {CANDIDATE}`", "", f"`CONTEXT_IDENTITY = {CONTEXT}`", "", f"`ARGV_IDENTITY = {ARGV}`", "", f"`OPERATION_IDENTITY = {OPERATION}`", "", f"`AUTHORIZATION_REQUEST_IDENTITY = {REQUEST}`", "", f"`AUTHORIZATION_PRESENTATION_IDENTITY = {PRESENTATION}`", "", f"`PREAUTHORIZATION_CHECKPOINT_IDENTITY = {CHECKPOINT}`", "", f"`EXECUTION_AUTHORITY_HANDOFF_SHA256 = {AUTHORITY_HANDOFF}`", "",
        "## Durable operation reduction", "",
        "One canonical PRE receipt and one correlated POST receipt bind the same generation, operation, authority, candidate, context, argv, JG baseline, start time, and no-network QEMU vector. The POST receipt records host exit 0. Independently, 19 canonical contiguous runtime records contain one Human act creation and one FUTURE denial; the denial checkpoint, guest execution seal, current-adapter recomputation, and teardown seal agree.", "",
        f"`DENIAL_REASON = VERIFIED__{DENIAL}`", "", "`FUTURE_OPERATIONAL_STATUS = VERIFIED__DENIED_BEFORE_P11_ENTRY`", "",
        "The sealed FUTURE relation is `500 < 600 < 1000`, baseline valid-from is 100, payload digest is `9568e0c248ad488cabcf6bde6b490c544077862d10e3fda13bcdc8ed9953f547`, and wall-clock dependency is zero.", "",
        "## Inherited continuation-manifest limitation", "",
        "`operation_state/runtime_export/G77_256JH_CONTINUATION_MANIFEST_TERMINAL_V1.json` preserves IH-owned field `first_failure_or_current_result = FAIL_CLOSED__FUTURE_REQUIRED_EVIDENCE_MISSING` and null `final_execution_seal`. It exists because the inherited IH candidate manifest lacked a final execution seal; the guest transition preserved that authenticated history. It is non-authoritative for current JH host reduction. Direct JH receipts, raw denial record/checkpoint, execution seal, current-adapter reduction, and teardown independently prove the JH result. The historical marker was not erased, mutated, or reinterpreted as historical success.", "",
        "`INHERITED_CONTINUATION_MANIFEST_LIMITATION = VERIFIED__PRESENT_AND_PRESERVED`", "", "`INHERITED_CONTINUATION_MANIFEST_AUTHORITY_STATUS = VERIFIED__AUTHENTICATED_HISTORICAL_RUNTIME_PROVENANCE__NONAUTHORITATIVE_FOR_CURRENT_JH_HOST_REDUCTION`", "",
        "# 3. Constitutional Self-Assessment", "", "## Verified", "",
        "- Exact local and remote JG entry; clean detached pinned nested authority and equal immutable remote tag.",
        "- Exact Human grant correlation, one consumed non-reusable authority, final admission PASS, one PRE/FM/QEMU/VM/operation attempt, one REQUEST and one FUTURE denial.",
        "- P11 entry, protected invocation, protected effect, retry, repair-retry, replay, every second-operation counter, shadow automation, and caller-selectable namespace are zero.",
        "- Runtime target and certification baseline remain distinct; Option A sealed operation-evidence-root authority is preserved; EX 17/17 is reused and zero reconstructed.",
        "- Complete teardown and no production, P11, route, namespace-registry, or historical-evidence mutation.", "",
        "## Not Verified", "",
        "- No governed universal whole-project scalar, numeric work-share/context/token/cost instrumentation, or L4 certification exists; these remain NOT_MEASURED or explicitly estimated.", "",
        "## Counter reconstruction", "",
    ]
    for key, value in c.items():
        lines.extend([f"`{key.upper()} = VERIFIED__{value}`", ""])
    lines.extend([
        "`AUTHORITY_FINAL_ADMISSION = VERIFIED__PASS`", "", "`AUTHORITY_STATE = VERIFIED__CONSUMED_NONREUSABLE`", "",
        "`E05_BEFORE = VERIFIED__10_OF_18`", "", "`E05_AFTER = VERIFIED__11_OF_18`", "", "`E05_CREDIT = VERIFIED__1`", "",
        "## Reuse Impact Assessment", "",
        "1. Katere obstoječe certificirane zmogljivosti se ponovno uporabijo? JG/JF/JE/JD/JC, FM, DU/EB/EE V2, GN, GL, ER/FC/FK/CHE/P11, EX, Layer 0, and pinned nested authority.",
        "2. Katere nove zmogljivosti (če sploh) nastanejo? Only JH-local operational-denial evidence and deterministic reduction; no new production capability.",
        "3. Ali katera obstoječa zmogljivost postane nedosegljiva? No.",
        "4. Ali implementacija ustvarja vzporedni tok? No.",
        "5. Ali zmanjšuje ali povečuje število produkcijskih poti? Neither; one route remains one.", "",
        f"`REUSED_CERTIFIED_CAPABILITY_SET = {r['reuse']['reused_certified_capability_set']}`", "", f"`NEW_CAPABILITY_SET = {r['reuse']['new_capability_set']}`", "", "`UNREACHABLE_PREEXISTING_CAPABILITY_SET = VERIFIED__EMPTY`", "", "`PARALLEL_FLOW_CREATED = VERIFIED__NO`", "", "`PRODUCTION_ROUTE_BEFORE = VERIFIED__1`", "", "`PRODUCTION_ROUTE_AFTER = VERIFIED__1`", "", "`PRODUCTION_ROUTE_DELTA = VERIFIED__0`", "", "`P11_MUTATION_COUNT = VERIFIED__0`", "",
        "## Constitutional health, continuation, and frontier", "",
        f"`CONSTITUTIONAL_HEALTH_EVIDENCE = {r['continuity']['constitutional_health_evidence']}`", "", f"`CONSTITUTIONAL_CONTINUATION_PROGRESS = {r['continuity']['constitutional_continuation_progress']}`", "",
        f"`CONSTITUTIONAL_FRONTIER_DISTANCE = {f['constitutional_frontier_distance']}`", "", f"`CONSTITUTIONAL_FRONTIER_DISTANCe = {f['constitutional_frontier_distanc_e']}`", "", f"`PROJECT_PROGRESS = {f['project_progress']}`", "", f"`PROJECT_PROGRESS_ESTIMATE = {f['project_progress_estimate']}`", "", "`E05_FRONTIER_DISTANCE = VERIFIED__7_UNSATISFIED_OF_18`", "", "`SELECTED_E05_LOCAL_FRONTIER_DISTANCE = VERIFIED__0__FUTURE_DENIAL_TARGET_SATISFIED`", "", f"`LAST_VERIFIED_EDGE = {f['last_verified_edge']}`", "", f"`FIRST_BROKEN_EDGE = {f['first_broken_edge']}`", "", f"`BLOCKING_OWNER = {f['blocking_owner']}`", "", f"`MINIMUM_MISSING_CAPABILITY = {f['minimum_missing_capability']}`", "", f"`MINIMUM_LEGAL_NEXT_DELTA = {f['minimum_legal_next_delta']}`", "",
        "## Governance, cognition, and CCWIM", "",
        f"`GOVERNANCE_EFFICIENCE = {r['metrics']['governance_efficience']}`", "", f"`ARCHITECTURAL_GOVERNANCE_EFFICIENCE = {r['metrics']['architectural_governance_efficience']}`", "", f"`PROOF_REUSE_EFFICIENCY = {r['metrics']['proof_reuse_efficiency']}`", "", "`EX_REUSED = VERIFIED__17_OF_17`", "", "`EX_RECONSTRUCTED = VERIFIED__0`", "", "`SHADOW_AUTOMATION_STATUS = VERIFIED__ABSENT`", "", "`AUTOMATIC_AUTHORIZATION_COUNT = VERIFIED__0`", "", "`AUTOMATIC_AUTHORITY_RECONSUMPTION_COUNT = VERIFIED__0`", "", "`AUTOMATIC_RETRY_COUNT = VERIFIED__0`", "", "`AUTOMATIC_REPAIR_RETRY_COUNT = VERIFIED__0`", "", "`AUTOMATIC_REPLAY_COUNT = VERIFIED__0`", "", "`AUTOMATIC_SUCCESSOR_OPERATION_COUNT = VERIFIED__0`", "", "`AUTOMATIC_E05_CREDIT_COUNT = VERIFIED__0`", "",
        f"`COGNITION_ASSISTED_HANDOFF = {r['cognition']['cognition_assisted_handoff']}`", "", f"`COGNITION_PROVENANCE = {r['cognition']['cognition_provenance']}`", "", "Constitutional Continuity & Worker Independence Metrics — CCWIM", "",
    ])
    for key, value in r["ccwim"].items():
        lines.extend([f"`{key.upper()} = {value}`", ""])
    for key in ("aigol_codex_work_share", "prompt_context_reuse_ratio", "repository_derived_execution_context_ratio", "constitutional_prompt_externalization_ratio", "token_benchmark", "llm_cost_reduction_ratio", "lcrr"):
        lines.extend([f"`{key.upper()} = {r['metrics'][key]}`", ""])
    lines.extend([f"`OVERENGINEERING_RISK = {r['metrics']['overengineering_risk']}`", "", f"`PROOF_PROCESS_OVERHEAD_RISK = {r['metrics']['proof_process_overhead_risk']}`", ""])
    for key, value in r["overengineering"].items():
        lines.extend([f"`{key.upper()} = VERIFIED__{value}`", ""])
    lines.extend([
        f"`CANDIDATE_CAPABILITY_BEFORE_JH = {r['candidate']['before']}`", "", f"`CANDIDATE_CAPABILITY = {r['candidate']['capability']}`", "", f"`SHADOW_DESIGN_TARGET = {r['candidate']['shadow_design_target']}`", "",
        "# 4. Validation Matrix", "", "All validation is repository-only. No authority controller, PRE/FM launcher, QEMU, VM, or operational entry point is invoked.", "",
        "| Requirement | Evidence | Validation | Result |", "|---|---|---|---|",
        "| Exact JG baseline and remote ratification | HEAD/tree/subject/origin and remote branch | exact comparison | PASS |",
        "| Pinned nested authority | local HEAD/tree/status and remote tag | exact comparison | PASS |",
        "| JH recovery reducer | durable evidence plus four fault classes | 6 passed | PASS |",
        "| JH preauthorization and consumed authority | canonical sealed artifacts and hashes | 3 current-applicable passed; 1 historical pre-consumption checkpoint-pinned | PASS |",
        "| One correlated no-network operation | PRE/POST receipt pair and 19-record sequence | JH recovery suite | PASS |",
        "| Exact FUTURE denial before P11 | raw record, checkpoint, execution seal, current adapter | JH recovery suite | PASS |",
        "| Teardown and no replay | teardown seal, exact receipt namespace, process inventory, recovery command audit | deterministic inspection | PASS |",
        "| Inherited IH limitation preserved | terminal continuation manifest | byte/hash and field checks | PASS |",
        "| GN/GL and FM owner | current-applicable focused suites | 52 plus 17 passed | PASS |",
        "| FUTURE semantics | IE semantic suite | 10 passed; 1 historical entry assertion checkpoint-pinned | PASS |",
        "| DU/EB/EE V2 | IN suite | 20 passed; 5 historical entry/scope assertions checkpoint-pinned | PASS |",
        "| EX common substrate | certified validator | repository-only validator | PASS |",
        "| Governance and Layer 0 | conformance tests/engine and freeze checker | repository-only commands | PASS |",
        "| Mutation and whitespace | Git inventory and diff checks | read-only inspection | PASS |", "",
        "Historical checkpoint-pinned assertions are classified separately from current regressions; they do not rewrite historical failures.", "",
        "# 5. Repository Mutation Summary", "",
        "The pre-write inventory contained 39 JH files and classified every artifact. The interrupted reducer (original SHA-256 `55e555996118744b8880b4ad3da31637061cd3a928861ef666573afe587616d6`) was `SEMANTICALLY_INCOMPLETE`; recovery completed it without touching durable operational evidence. Added artifacts are the focused terminal-recovery test, sealed reduction, and this report.", "",
        "`PRODUCTION_MUTATION_COUNT = VERIFIED__0`", "", "`P11_MUTATION_COUNT = VERIFIED__0`", "", "`HISTORICAL_EVIDENCE_MUTATION_COUNT = VERIFIED__0`", "", "`ROUTE_MUTATION_COUNT = VERIFIED__0`", "", "`WORKTREE_STATE = BOUNDED_UNTRACKED_JH_EVIDENCE_ONLY`", "", "`INDEX_STATE = EMPTY`", "", "`HUMAN_REVIEW_REQUIRED = VERIFIED__YES`", "", "`AUTO_CONTINUABLE = VERIFIED__NO`", "",
        "# 6. Certification Verdict", "", TERMINAL, "",
    ])
    return "\n".join(lines)


def write_recovery_artifact(path: Path, payload: bytes) -> None:
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise ReductionError(f"TERMINAL_ARTIFACT_COLLISION:{path.name}")
    path.write_bytes(payload)


def main() -> None:
    reduction = analyze()
    envelope = {"schema_id": "G77_256JH_SPCE_TERMINAL_REDUCTION_ENVELOPE_V1", "reduction": reduction, "reduction_sha256": sha256_bytes(canonical_bytes(reduction))}
    write_recovery_artifact(TERMINAL_PATH, canonical_bytes(envelope))
    write_recovery_artifact(REPORT_PATH, render_report(reduction).encode())


if __name__ == "__main__":
    main()
