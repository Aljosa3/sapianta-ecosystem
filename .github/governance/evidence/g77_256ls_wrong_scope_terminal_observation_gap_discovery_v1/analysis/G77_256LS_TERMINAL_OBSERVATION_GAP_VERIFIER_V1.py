#!/usr/bin/env python3
"""Read-only verifier for the G77-256LS terminal observation gap discovery."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
LS_REL = Path(
    ".github/governance/evidence/"
    "g77_256ls_wrong_scope_terminal_observation_gap_discovery_v1"
)
LS = ROOT / LS_REL
LR = ROOT / ".github/governance/evidence/g77_256lr_operational_wrong_scope_denial_v1"
LQ = ROOT / ".github/governance/evidence/g77_256lq_wrong_scope_fresh_phase_a_review_object_v1"
DECISION = LS / "G77_256LS_TERMINAL_OBSERVATION_GAP_DISCOVERY_V1.json"
REPORT = LS / "G77_256LS_G48_IMPLEMENTATION_REPORT_V1.md"
SERIAL = LR / "G77_256LR_INTERRUPTED_SERIAL_LOG_V1.log"
RECONSTRUCTION = LR / "G77_256LR_INTERRUPTED_STATE_RECONSTRUCTION_V1.json"
PRE = LQ / "operation_state/receipts/G77_256LQ_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
POST = LQ / "operation_state/receipts/G77_256LQ_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
RESULT = LR / "G77_256LR_FM_OPERATIONAL_INVOCATION_RESULT_V1.json"
RUNTIME = LQ / "operation_state/runtime_export"
CONTROLLER = LR / "orchestration/G77_256LR_ONE_SHOT_CONTROLLER_V1.py"
FM = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
CLOUD = ROOT / (
    ".github/governance/evidence/g77_256lj_wrong_scope_stable_checkout_reuse_v1/"
    "static/G77_256LJ_CLOUD_INIT_USER_DATA_V1.yaml"
)
P11 = ROOT / "tests/p11_da_operational_consumer_v1.py"
NESTED = ROOT / "sapianta_system"

LR_HEAD = "b738b0795b9d50b60819bbbf31e49fab6b47ed5d"
LR_TREE = "ee02f204235da4ea28bca05bfedabe645fe1cdfa"
LR_SUBJECT = "G77-256LR record interrupted one-shot operational terminal"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "refs/tags/sapianta-system-nested-authority-3183bab-v1"
SERIAL_SHA256 = "72c46b41a40d6b00ffd4a1fccdfc67ae5b4584dfe0bf2bc924aec0f2251c5998"
RECONSTRUCTION_SHA256 = "429123ec1ddef737060de182e712cb1a6091318a69345ca720764f91977b126b"
PRE_SHA256 = "b8da75b9ad19fce7f355fc07f18fc45a1fec10f9941bd52cf2539284e28d41ac"
CONTROLLER_SHA256 = "89a7ebf2f6d7972e6899956b947c20a1614db2c9d53e5d3ac97816929a31b1b0"
FM_SHA256 = "5a0a597434bd89752828afd85ecb5a98669f41ae66fa0480ea27be6d611597e8"
CLOUD_SHA256 = "17957eee3b80526632c0384c552f1e11979b0411995a131950c207a9086feaea"
P11_SHA256 = "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5"
TERMINAL = (
    "A__G77_256LS_WRONG_SCOPE_TERMINAL_OBSERVATION_GAP_CLASSIFIED__"
    "ZERO_AUTHORITY__ZERO_OPERATION__MINIMUM_LEGAL_NEXT_DELTA_IDENTIFIED__"
    "READY_FOR_HUMAN_REVIEW"
)


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(repository: Path, *arguments: str) -> str:
    return subprocess.check_output(
        ["git", *arguments], cwd=repository, text=True
    ).strip()


def active_related_processes() -> list[str]:
    output = subprocess.check_output(
        ["ps", "-eo", "comm=,args="], text=True
    )
    return [
        line for line in output.splitlines()
        if line.split(None, 1)[0].startswith("qemu")
        or (
            line.split(None, 1)[0] in {"python", "python3"}
            and "G77_256LR_ONE_SHOT_CONTROLLER_V1.py" in line
        )
    ]


def authenticate_git_and_nested() -> None:
    if (
        git(ROOT, "rev-parse", f"{LR_HEAD}^{{tree}}") != LR_TREE
        or git(ROOT, "show", "-s", "--format=%s", LR_HEAD) != LR_SUBJECT
        or git(ROOT, "branch", "--show-current")
        != "g77-256fl-wrong-attempt-preboot-blocker"
        or subprocess.run(
            ["git", "merge-base", "--is-ancestor", LR_HEAD, "HEAD"],
            cwd=ROOT,
            check=False,
        ).returncode != 0
        or int(git(ROOT, "rev-list", "--count", f"{LR_HEAD}..HEAD")) > 1
    ):
        raise RuntimeError("LR_ENTRY_OR_LS_SUCCESSOR_CONFLICT")
    dirty = git(ROOT, "status", "--porcelain=v1", "--untracked-files=all")
    if any(
        line and not line[3:].startswith(LS_REL.as_posix() + "/")
        for line in dirty.splitlines()
    ):
        raise RuntimeError("UNRELATED_MUTATION")
    if (
        git(NESTED, "rev-parse", "HEAD") != NESTED_HEAD
        or git(NESTED, "rev-parse", "HEAD^{tree}") != NESTED_TREE
        or git(NESTED, "branch", "--show-current") != ""
        or git(NESTED, "status", "--porcelain=v1", "--untracked-files=all") != ""
        or git(NESTED, "rev-parse", f"{NESTED_TAG}^{{}}") != NESTED_HEAD
    ):
        raise RuntimeError("NESTED_AUTHORITY_CONFLICT")


def authenticate_lr_artifacts() -> dict[str, Any]:
    expected = {
        RECONSTRUCTION: RECONSTRUCTION_SHA256,
        PRE: PRE_SHA256,
        CONTROLLER: CONTROLLER_SHA256,
        FM: FM_SHA256,
        CLOUD: CLOUD_SHA256,
        P11: P11_SHA256,
    }
    if any(path.is_symlink() or not path.is_file() or sha256(path) != digest
           for path, digest in expected.items()):
        raise RuntimeError("AUTHENTICATED_INPUT_HASH_CONFLICT")
    if SERIAL.stat().st_size != 43692 or sha256(SERIAL) != SERIAL_SHA256:
        raise RuntimeError("SERIAL_IDENTITY_CONFLICT")
    absent = [
        POST,
        RESULT,
        RUNTIME / "G77_256LQ_RAW_EXECUTION_EVIDENCE_V1.jsonl",
        RUNTIME / "G77_256LQ_GUEST_EXECUTION_SEAL_V1.json",
        RUNTIME / "G77_256LQ_GUEST_TEARDOWN_SEAL_V1.json",
        RUNTIME / "G77_256LQ_CONTINUATION_MANIFEST_TERMINAL_V1.json",
    ]
    if any(path.exists() or path.is_symlink() for path in absent):
        raise RuntimeError("LR_ABSENCE_SET_CHANGED")
    if active_related_processes():
        raise RuntimeError("RELATED_OPERATIONAL_PROCESS_ACTIVE")
    envelope = json.loads(RECONSTRUCTION.read_bytes())
    reconstruction = envelope["reconstruction"]
    if envelope["reconstruction_sha256"] != hashlib.sha256(
        canonical_bytes(reconstruction)
    ).hexdigest():
        raise RuntimeError("LR_RECONSTRUCTION_SEAL_CONFLICT")
    if (
        not reconstruction["recovery_state_class"].startswith("STATE_B__")
        or reconstruction["cardinality"]["authority_created_count"] != 1
        or reconstruction["cardinality"]["authority_consumed_count"] != 1
        or reconstruction["cardinality"]["operation_attempt_count"] != 1
        or reconstruction["cardinality"]["retry_count"] != 0
        or reconstruction["operation"]["operation_terminal_evidence_present"] is not False
    ):
        raise RuntimeError("LR_TERMINAL_FACT_CONFLICT")
    return reconstruction


def authenticate_static_analysis() -> None:
    controller = CONTROLLER.read_text(encoding="utf-8")
    fm = FM.read_text(encoding="utf-8")
    cloud = CLOUD.read_text(encoding="utf-8")
    p11 = P11.read_text(encoding="utf-8")
    serial = SERIAL.read_bytes()
    required_controller = (
        "status = subprocess.run(final_argv, cwd=ROOT, check=False).returncode",
        "except BaseException as exc:",
        '"G77_256LR_FM_OPERATIONAL_INVOCATION_RESULT_V1"',
    )
    required_fm = (
        "result = subprocess.run(argv, check=False)",
        "finally:",
        'context=context, phase="POST"',
    )
    if not all(token in controller for token in required_controller):
        raise RuntimeError("LR_CONTROLLER_TERMINALIZATION_ANALYSIS_CONFLICT")
    if not all(token in fm for token in required_fm):
        raise RuntimeError("FM_POST_TERMINALIZATION_ANALYSIS_CONFLICT")
    if any(token in controller + fm for token in ("start_new_session=True", "setsid(", "signal.signal(")):
        raise RuntimeError("UNEXPECTED_SESSION_INDEPENDENCE_CAPABILITY")
    if (
        "G77_256FM_BOOT_MARKER=PASS" not in cloud
        or b"G77_256FM_BOOT_MARKER=PASS" in serial
        or b"G77_256FM_HARNESS_EXIT_STATUS=" in serial
        or b"reboot: Power down" in serial
    ):
        raise RuntimeError("SERIAL_BOUNDARY_CLASSIFICATION_CONFLICT")
    scope_check = "if validated_act.authority_scope != OPERATIONAL_AUTHORITY_SCOPE:"
    denial = '_fail("operational Human act scope is invalid")'
    claim = p11[p11.index("    def claim_and_invoke_once("):]
    authority_validation = "binding = self._validate_authority_sources("
    preclaim_append = 'self._append_operational_event(\n            "P11_DA_OPERATIONAL_PRECLAIM"'
    if (
        p11.count(scope_check) != 1
        or p11.count(denial) != 1
        or claim.count(authority_validation) != 1
        or claim.count(preclaim_append) != 1
        or claim.index(authority_validation) > claim.index(preclaim_append)
    ):
        raise RuntimeError("STATIC_WRONG_SCOPE_PATH_CONFLICT")


def authenticate_decision_and_report() -> dict[str, Any]:
    envelope = json.loads(DECISION.read_bytes())
    decision = envelope.get("decision")
    discovery = envelope.get("discovery")
    if (
        not isinstance(decision, dict)
        or envelope.get("decision_sha256")
        != hashlib.sha256(canonical_bytes(decision)).hexdigest()
        or not isinstance(discovery, dict)
        or discovery.get("terminal") != TERMINAL
        or decision.get("failure_class") != "HARNESS_OR_TEST_ARTIFACT"
        or decision.get("production_capability_gap")
        != "NO__STATIC_WRONG_SCOPE_DENIAL_AND_EXISTING_ER_TO_P11_ROUTE_REMAIN_PRESENT"
        or decision.get("operational_retry_authorized") != "NO"
        or set(discovery["execution_counters_ls"].values()) != {0}
        or discovery["architecture"]["route_count_before"] != 1
        or discovery["architecture"]["route_count_after"] != 1
    ):
        raise RuntimeError("LS_DECISION_SEAL_OR_SEMANTICS_CONFLICT")
    report = REPORT.read_text(encoding="utf-8")
    headings = [line for line in report.splitlines() if line.startswith("# ")]
    if headings != [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]:
        raise RuntimeError("G48_H1_STRUCTURE_CONFLICT")
    questions = (
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "Katere nove zmogljivosti (če sploh) nastanejo?",
        "Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "Ali implementacija ustvarja vzporedni tok?",
        "Ali zmanjšuje ali povečuje število produkcijskih poti?",
    )
    if any(report.count(question) != 1 for question in questions):
        raise RuntimeError("G48_REUSE_QUESTION_CARDINALITY_CONFLICT")
    return discovery


def verify() -> str:
    authenticate_git_and_nested()
    authenticate_lr_artifacts()
    authenticate_static_analysis()
    authenticate_decision_and_report()
    print(TERMINAL)
    return TERMINAL


if __name__ == "__main__":
    verify()
