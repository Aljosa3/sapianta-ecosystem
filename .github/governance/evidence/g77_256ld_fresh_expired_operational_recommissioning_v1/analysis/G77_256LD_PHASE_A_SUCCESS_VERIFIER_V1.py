#!/usr/bin/env python3
"""Verify the sealed LD Phase-A Human barrier without executing it."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
LD = Path(
    ".github/governance/evidence/"
    "g77_256ld_fresh_expired_operational_recommissioning_v1"
)
ENTRY_HEAD = "98d059beaa148746d397d48bad9e898b1f9c2297"
ENTRY_TREE = "d1aadf9da3f66b2699f9b4c32647a2fe65c060cc"
ENTRY_SUBJECT = "G77-256LC reissue EXPIRED bootstrap digest projection"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
GENERATION = "G77_256LD_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256LD_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001"
TERMINAL = (
    "A__FRESH_LD_EXPIRED_MATERIALIZED_PREAUTHORIZATION_"
    "READY_FOR_HUMAN_DECISION__NO_AUTHORITY__NO_OPERATION__NO_E05_CREDIT"
)
JR = Path(
    ".github/governance/evidence/"
    "g77_256jr_expired_human_authority_materialization_and_presentation_binding_v1/"
    "adapter/G77_256JR_EXPIRED_VECTOR_ADAPTER_V1.py"
)
FM = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
CLOUD = Path(
    ".github/governance/evidence/"
    "g77_256jx_er_admission_runtime_checkout_role_separation_repair_v1/static/"
    "G77_256JX_CLOUD_INIT_USER_DATA_V1.yaml"
)
SEED = CLOUD.with_name("SAPIANTA_EXPIRED_NOCLOUD_SEED_V3.img")
META_DATA = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/raw/"
    "G77_256FM_CLOUD_INIT_META_DATA_V1.yaml"
)
NETWORK_CONFIG = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/raw/"
    "G77_256FM_CLOUD_INIT_NETWORK_CONFIG_V1.yaml"
)
P11 = Path("tests/p11_da_operational_consumer_v1.py")
HASHES = {
    JR: "df87b85f40ab9b6a286c8114c931cedc90f485c0e9992271aef92cbf1549e344",
    FM: "c5172208874cca022b638511e57f091eafa01ba3c7387b182cf65d4ee98764d0",
    CLOUD: "fdad67efe32a70784600819404222abd7a7bcee4461854fba69651513b19664e",
    SEED: "81011b08aabb7052a14dc4f81ec51536c551cad97441563f846edbe778728004",
    META_DATA: "081885fe7f51b064148db23dff5f4af40f58ae693879b5cb05fae24c8f23838a",
    NETWORK_CONFIG: "639b6f419a9ac49312b218e12395dc7e7d623d96202c3315a92dcd19d6fa02ba",
    P11: "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5",
}
REQUEST = LD / "G77_256LD_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
AUTH_PRESENTATION = LD / "G77_256LD_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
DECISION_PRESENTATION = LD / "G77_256LD_HUMAN_DECISION_PRESENTATION_V1.txt"
READINESS = LD / "G77_256LD_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json"
SAFE_STOP = LD / "G77_256LD_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
PREFLIGHT = LD / "G77_256LD_LC_MATERIALIZED_PREFLIGHT_V1.json"
REDUCTION = LD / "G77_256LD_PREHUMAN_PHASE_A_REDUCTION_V1.json"
CONTEXT = LD / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
REPORT = LD / "G77_256LD_G48_IMPLEMENTATION_REPORT_V1.md"


class LDVerificationError(RuntimeError):
    """One deterministic LD Phase-A verification failure."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes((ROOT / path).read_bytes())


def load_canonical(path: Path) -> dict[str, Any]:
    raw = (ROOT / path).read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise LDVerificationError(f"NONCANONICAL_JSON:{path}")
    return value


def sealed(path: Path, inner: str) -> tuple[dict[str, Any], dict[str, Any]]:
    envelope = load_canonical(path)
    value = envelope.get(inner)
    if (
        not isinstance(value, dict)
        or envelope.get(f"{inner}_sha256") != sha256_bytes(canonical_bytes(value))
    ):
        raise LDVerificationError(f"INNER_SEAL_MISMATCH:{path}")
    return envelope, value


def git(*args: str, nested: bool = False) -> str:
    command = ["git"]
    if nested:
        command.extend(["-C", "sapianta_system"])
    command.extend(args)
    return subprocess.run(
        command, cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def all_zero(value: dict[str, Any]) -> bool:
    return bool(value) and all(item == 0 for item in value.values())


PHASE_A_COUNTER_KEYS = {
    "authority_consumption_count",
    "expired_denial_count",
    "fm_operational_invocation_count",
    "operation_attempt_count",
    "operational_authorization_count",
    "operational_request_count",
    "p11_entry_count",
    "pre_operational_count",
    "protected_effect_count",
    "protected_invocation_count",
    "qemu_count",
    "repair_retry_count",
    "replay_count",
    "request_count",
    "retry_count",
    "vm_count",
}


RECOVERY_COUNTER_KEYS = {
    "new_authority_consumption_during_recovery",
    "new_fm_operational_invocation_during_recovery",
    "new_operation_attempt_during_recovery",
    "new_operational_request_during_recovery",
    "new_p11_entry_during_recovery",
    "new_pre_operational_during_recovery",
    "new_protected_effect_during_recovery",
    "new_protected_invocation_during_recovery",
    "new_qemu_during_recovery",
    "new_vm_during_recovery",
    "repair_retry_during_recovery",
    "replay_during_recovery",
    "retry_during_recovery",
}


def verify_repository_scope() -> None:
    if git("branch", "--show-current") != BRANCH:
        raise LDVerificationError("BRANCH_MISMATCH")
    if git("show", "-s", "--format=%T", ENTRY_HEAD) != ENTRY_TREE:
        raise LDVerificationError("ENTRY_TREE_MISMATCH")
    if git("show", "-s", "--format=%s", ENTRY_HEAD) != ENTRY_SUBJECT:
        raise LDVerificationError("ENTRY_SUBJECT_MISMATCH")
    subprocess.run(
        ["git", "merge-base", "--is-ancestor", ENTRY_HEAD, "HEAD"],
        cwd=ROOT,
        check=True,
    )
    dirty = git("status", "--porcelain=v1", "--untracked-files=all").splitlines()
    if any(LD.as_posix() not in line for line in dirty):
        raise LDVerificationError("MUTATION_OUTSIDE_LD_SCOPE")
    if (
        git("rev-parse", "HEAD", nested=True) != NESTED_HEAD
        or git("rev-parse", "HEAD^{tree}", nested=True) != NESTED_TREE
        or git("status", "--porcelain", nested=True)
        or git("branch", "--show-current", nested=True)
    ):
        raise LDVerificationError("NESTED_AUTHORITY_MISMATCH")
    for path, expected in HASHES.items():
        raw = (ROOT / path).read_bytes()
        committed = subprocess.check_output(
            ["git", "show", f"{ENTRY_HEAD}:{path.as_posix()}"], cwd=ROOT
        )
        if raw != committed or sha256_bytes(raw) != expected:
            raise LDVerificationError(f"CURRENT_LC_ASSET_MISMATCH:{path}")


def verify_phase_a() -> dict[str, Any]:
    request_envelope, request = sealed(REQUEST, "request")
    readiness_envelope, readiness = sealed(READINESS, "checkpoint")
    safe_envelope, safe = sealed(SAFE_STOP, "checkpoint")
    preflight_envelope, preflight = sealed(PREFLIGHT, "proof")
    reduction_envelope, reduction = sealed(REDUCTION, "reduction")
    context = load_canonical(CONTEXT)

    identities = reduction.get("identities", {})
    expected_identities = {
        "request_sha256": request_envelope["request_sha256"],
        "request_file_sha256": sha256_path(REQUEST),
        "presentation_sha256": sha256_path(AUTH_PRESENTATION),
        "readiness_checkpoint_sha256": readiness_envelope["checkpoint_sha256"],
        "readiness_checkpoint_file_sha256": sha256_path(READINESS),
        "checkpoint_sha256": safe_envelope["checkpoint_sha256"],
        "checkpoint_file_sha256": sha256_path(SAFE_STOP),
        "lc_materialized_preflight_sha256": preflight_envelope["proof_sha256"],
        "lc_materialized_preflight_file_sha256": sha256_path(PREFLIGHT),
    }
    if any(identities.get(key) != value for key, value in expected_identities.items()):
        raise LDVerificationError("REDUCTION_IDENTITY_BINDING_MISMATCH")

    values = (request, readiness, safe, preflight, reduction, context)
    if any(value.get("generation_identity") != GENERATION for value in values):
        raise LDVerificationError("GENERATION_IDENTITY_MISMATCH")
    if any(value.get("operation_identity") != OPERATION for value in values):
        raise LDVerificationError("OPERATION_IDENTITY_MISMATCH")
    counter_sets = [
        readiness.get("operational_counters", {}),
        safe.get("operational_counters", {}),
        preflight.get("operational_counters", {}),
        reduction.get("operational_counters", {}),
        reduction.get("recovery_operational_counters", {}),
    ]
    if (
        any(set(counters) != PHASE_A_COUNTER_KEYS for counters in counter_sets[:4])
        or set(counter_sets[4]) != RECOVERY_COUNTER_KEYS
        or not all(all_zero(counters) for counters in counter_sets)
    ):
        raise LDVerificationError("NONZERO_PHASE_A_COUNTER")
    if (
        reduction.get("terminal") != TERMINAL
        or safe.get("terminal") != TERMINAL
        or reduction.get("ready_for_human_decision") != "VERIFIED"
        or preflight.get("ready_for_human_decision") != "VERIFIED"
        or any(value.get("human_authority_present") is not False for value in values[1:5])
        or any(value.get("phase_b_started") is not False for value in values[1:5])
        or reduction.get("e05")
        != {
            "after": "VERIFIED__11_OF_18",
            "before": "VERIFIED__11_OF_18",
            "credit": "VERIFIED__0",
            "expired_status": "NOT_PROVEN_OPERATIONALLY",
            "frontier": "VERIFIED__7_UNSATISFIED_OF_18",
        }
    ):
        raise LDVerificationError("PHASE_A_TERMINAL_CONTRACT_MISMATCH")

    source_chain = preflight.get("source_to_asset_chain", {})
    if (
        source_chain.get("jr_adapter_sha256") != HASHES[JR]
        or source_chain.get("fm_launcher_sha256") != HASHES[FM]
        or source_chain.get("cloud_init_sha256") != HASHES[CLOUD]
        or source_chain.get("nocloud_user_data_sha256") != HASHES[CLOUD]
        or source_chain.get("nocloud_meta_data_sha256") != HASHES[META_DATA]
        or source_chain.get("nocloud_network_config_sha256") != HASHES[NETWORK_CONFIG]
        or source_chain.get("nocloud_seed_sha256") != HASHES[SEED]
        or source_chain.get("p11_sha256") != HASHES[P11]
    ):
        raise LDVerificationError("SOURCE_TO_ASSET_CHAIN_MISMATCH")
    argv = context.get("canonical_argv")
    if (
        not isinstance(argv, list)
        or not argv
        or argv[0] != "/usr/bin/qemu-system-x86_64"
        or "-nic" not in argv
        or argv[argv.index("-nic") + 1] != "none"
        or context.get("repository_head") != ENTRY_HEAD
        or context.get("repository_tree") != ENTRY_TREE
    ):
        raise LDVerificationError("SEALED_LAUNCH_ARGUMENT_MISMATCH")

    required_lines = {
        f"REQUEST_IDENTITY {request_envelope['request_sha256']}",
        f"REQUEST_FILE_SHA256 {sha256_path(REQUEST)}",
        f"PRESENTATION_SHA256 {sha256_path(AUTH_PRESENTATION)}",
        f"READINESS_CHECKPOINT {readiness_envelope['checkpoint_sha256']}",
        f"SAFE_STOP_CHECKPOINT {safe_envelope['checkpoint_sha256']}",
        "HUMAN_AUTHORITY NOT_SUPPLIED",
        "AUTO_CONTINUABLE NO",
        "HUMAN_REVIEW_REQUIRED YES",
        "GENERATION = G77-256LD",
        f"GENERATION_IDENTITY = {GENERATION}",
        f"OPERATION_IDENTITY = {OPERATION}",
        "VECTOR = EXPIRED",
        "TARGET_ACCEPTANCE_EDGE = EXPIRED_DENIAL_AT_GOVERNED_PRECLAIM_BEFORE_P11_ENTRY",
        "MAX_AUTHORITY_CONSUMPTION = 1",
        "MAX_OPERATION_ATTEMPT = 1",
        "SECOND_OPERATION = FORBIDDEN",
        "RETRY = FORBIDDEN",
        "REPLAY = FORBIDDEN",
        "REPAIR_RETRY = FORBIDDEN",
        "ALTERNATE_AUTHORITY_PATH = FORBIDDEN",
        "P11_BYPASS = FORBIDDEN",
        "PARALLEL_ROUTE = FORBIDDEN",
        "AUTHORITY_TRANSFER = FORBIDDEN",
        "HISTORICAL_AUTHORITY_REUSE = FORBIDDEN",
        "PRODUCTION_EXPANSION = FORBIDDEN",
        "CURRENT_E05_STATE = 11_OF_18",
        "POTENTIAL_E05_RESULT = AT_MOST_ONE_EXPIRED_ACCEPTANCE_CREDIT_IF_EXACT_AUTHENTICATED_ACCEPTANCE_IS_OBSERVED",
        "READY_FOR_HUMAN_DECISION = VERIFIED",
        "HUMAN_AUTHORITY_CREATED = 0",
        "AUTHORITY_CONSUMPTION_COUNT = 0",
        "QEMU_START_COUNT = 0",
        "VM_START_COUNT = 0",
        "OPERATION_ATTEMPT_COUNT = 0",
        "E05_CREDIT = 0",
        "STOP. DO NOT GENERATE THE HUMAN ANSWER.",
    }
    actual_lines = set((ROOT / DECISION_PRESENTATION).read_text().splitlines())
    if not required_lines.issubset(actual_lines):
        raise LDVerificationError("HUMAN_DECISION_PRESENTATION_MISMATCH")

    forbidden = [
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / LD).rglob("*")
        if path.is_file()
        and any(
            token in path.name
            for token in (
                "AUTHORIZATION_SOURCE",
                "PHASE_B_CONTROLLER",
                "CANONICAL_HUMAN_AUTHORITY",
                "EXECUTION_RESULT",
                "OPERATIONAL_RAW_EVIDENCE",
            )
        )
    ]
    if forbidden:
        raise LDVerificationError(f"FORBIDDEN_POSTHUMAN_ARTIFACT:{forbidden}")
    allowed_operation_state = {
        "operation_state/guest_harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py",
        "operation_state/guest_harness/G77_256LD_EXPIRED_VECTOR_ADAPTER_V1.py",
        "operation_state/guest_harness/sapianta_fresh_operation_context_v1.py",
        "operation_state/runtime_export/G77_256LD_CONTINUATION_MANIFEST_V1.json",
        "operation_state/runtime_export/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json",
    }
    observed_operation_state = {
        path.relative_to(ROOT / LD).as_posix()
        for path in (ROOT / LD / "operation_state").rglob("*")
        if path.is_file()
    }
    if observed_operation_state != allowed_operation_state:
        raise LDVerificationError("OPERATION_STATE_SCOPE_MISMATCH")

    report = (ROOT / REPORT).read_text(encoding="utf-8")
    if sum(line.startswith("# ") for line in report.splitlines()) != 6:
        raise LDVerificationError("G48_H1_COUNT_MISMATCH")
    questions = [line for line in report.splitlines() if line[:3] in {"1. ", "2. ", "3. ", "4. ", "5. "}]
    if len(questions) != 5:
        raise LDVerificationError("G48_REUSE_QUESTION_COUNT_MISMATCH")
    required_report_bindings = {
        f"`REQUEST_IDENTITY = {request_envelope['request_sha256']}`",
        f"`REQUEST_FILE_SHA256 = {sha256_path(REQUEST)}`",
        f"`AUTHORIZATION_PRESENTATION_SHA256 = {sha256_path(AUTH_PRESENTATION)}`",
        f"`HUMAN_DECISION_PRESENTATION_SHA256 = {sha256_path(DECISION_PRESENTATION)}`",
        f"`READINESS_CHECKPOINT_FILE_SHA256 = {sha256_path(READINESS)}`",
        f"`SAFE_STOP_CHECKPOINT_FILE_SHA256 = {sha256_path(SAFE_STOP)}`",
        f"`LC_MATERIALIZED_PREFLIGHT_FILE_SHA256 = {sha256_path(PREFLIGHT)}`",
        "`CONTINUATION_TYPE = CROSS_ACCOUNT_SAME_GENERATION`",
        "`CURRENT_COMMIT_STATE = DIRTY__UNCOMMITTED`",
        "`OPERATION_REQUEST_COUNT = 0`",
        "`CROSS_ACCOUNT_CONTINUATION = VERIFIED__SAME_G77_256LD_GENERATION`",
        "`DIRTY_WORKSPACE_REAUTHENTICATED = VERIFIED__AUTHORIZED_LD_SCOPE_ONLY`",
        "EVIDENCE_OR_REPORTING_DEFECT__HARNESS_OR_TEST_ARTIFACT",
        "DURABLE_DIRTY_LD_WORKSPACE + HUMAN_PROVIDED_CROSS_ACCOUNT_HANDOFF + CURRENT_ACCOUNT_REAUTHENTICATION",
    }
    if not all(binding in report for binding in required_report_bindings):
        raise LDVerificationError("G48_CURRENT_BINDING_OR_PROVENANCE_MISMATCH")
    return {
        "terminal": TERMINAL,
        "ready_for_human_decision": "VERIFIED",
        "human_authority_created": 0,
        "authority_consumption_count": 0,
        "qemu_start_count": 0,
        "vm_start_count": 0,
        "operation_attempt_count": 0,
        "operation_request_count": 0,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "retry_count": 0,
        "repair_retry_count": 0,
        "replay_count": 0,
        "e05_credit": 0,
        "e05_state": "VERIFIED__11_OF_18",
        "e05_frontier": "VERIFIED__7_UNSATISFIED_OF_18",
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
    }


if __name__ == "__main__":
    verify_repository_scope()
    verify_phase_a()
    print(TERMINAL)
