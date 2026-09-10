from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[5]
KA = ROOT / ".github/governance/evidence/g77_256ka_fresh_expired_operational_recommissioning_v1"
TERMINAL = KA / "G77_256KA_SPCE_TERMINAL_FAILURE_REDUCTION_V2.json"
OBSERVATION = KA / "G77_256KA_PHASE_B_GUEST_FAILURE_OBSERVATION_V2.json"
SERIAL = KA / "G77_256KA_SERIAL_CONSOLE_V1.log"
REPORT = KA / "G77_256KA_G48_IMPLEMENTATION_REPORT_V1.md"
HANDOFF = KA / "G77_256KA_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
BINDING = KA / "G77_256KA_PRECONSUMPTION_INVOCATION_BINDING_V1.json"
PRE = KA / "operation_state/receipts/G77_256KA_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
POST = KA / "operation_state/receipts/G77_256KA_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def load(path: Path) -> dict:
    raw = path.read_bytes(); value = json.loads(raw)
    assert raw == canonical_bytes(value)
    return value


def inner(path: Path, key: str) -> dict:
    envelope = load(path); value = envelope[key]
    assert envelope[f"{key}_sha256"] == hashlib.sha256(canonical_bytes(value)).hexdigest()
    return value


def test_corrected_terminal_is_canonical_sealed_and_fail_closed() -> None:
    reduction = inner(TERMINAL, "reduction")
    assert reduction["terminal"] == "M__KA_AUTHORIZED_EXPIRED_OPERATION_FAILED_AT_GUEST_CONTEXT_NAMESPACE_BINDING_BEFORE_REQUEST"
    assert reduction["authority_state"] == "CONSUMED"
    assert reduction["failure"]["observed_namespace"] == "g77_256ka_fresh_expired_operational_recommissioning_v1"
    assert reduction["failure"]["required_namespace_lead"] == "g77_256ka_expired_"
    assert reduction["failure"]["exact_failure"] == "sealed operation projection is not namespace-bound"
    assert reduction["e05"] == {
        "after": "VERIFIED__11_OF_18", "before": "VERIFIED__11_OF_18",
        "credit": "VERIFIED__0", "expired": "NOT_PROVEN_OPERATIONALLY",
        "frontier": "VERIFIED__7_UNSATISFIED_OF_18", "state": "VERIFIED__11_OF_18",
    }


def test_exact_operational_counters_and_zero_effect_boundary() -> None:
    counters = inner(TERMINAL, "reduction")["operational_counters"]
    assert counters == {
        "operational_authorization_count": 1, "authority_consumption_count": 1,
        "pre_operational_count": 1, "fm_operational_invocation_count": 1,
        "qemu_count": 1, "vm_count": 1, "operation_attempt_count": 1,
        "operational_request_count": 0, "expired_denial_count": 0,
        "p11_entry_count": 0, "protected_invocation_count": 0,
        "protected_effect_count": 0, "retry_count": 0,
        "repair_retry_count": 0, "replay_count": 0,
    }


def test_jz_digest_equality_and_single_no_network_receipt_pair() -> None:
    handoff_digest = hashlib.sha256(HANDOFF.read_bytes()).hexdigest()
    binding = inner(BINDING, "invocation_binding")
    argv = binding["final_fm_argv"]
    assert {
        handoff_digest, binding["authenticated_canonical_authority_digest"],
        binding["sealed_invocation_authority_digest"], binding["final_fm_argv_authority_digest"],
        argv[argv.index("--execution-authority-sha256") + 1],
    } == {"98e514ad177a85ca358cec0f4f053abcfe49c47aaf24f108d70fd11e5ff90283"}
    pre = load(PRE); post = load(POST); qemu = pre["vector"]["argv"]
    assert pre["started_unix_ns"] == post["started_unix_ns"]
    assert pre["execution_attempt_count"] == post["execution_attempt_count"] == 1
    assert pre["automatic_retry_count"] == post["automatic_retry_count"] == 0
    assert pre["process_exit_status"] is None and post["process_exit_status"] == 0
    assert qemu[qemu.index("-nic") + 1] == "none"


def test_serial_and_correction_evidence() -> None:
    observation = inner(OBSERVATION, "observation")
    serial = SERIAL.read_bytes()
    assert hashlib.sha256(serial).hexdigest() == observation["serial_sha256"] == "45aad40d946b489f421dfb8bd87081e24ab298ec25ddde0f22949ba2ffecfa79"
    assert observation["guest_harness_exit_status"] == 1
    assert observation["expired_denial_observed"] is False
    assert b"G77_256FM_BOOT_MARKER=PASS" in serial
    assert b"sealed operation projection is not namespace-bound" in serial
    assert b"G77_256FM_HARNESS_EXIT_STATUS=1" in serial
    assert b"one-use Human act expired before PRECLAIM" not in serial
    correction = inner(TERMINAL, "reduction")["correction"]
    assert correction["classification"] == "EVIDENCE_REDUCTION_FIELD_CORRECTION__NO_OPERATIONAL_REPLAY"
    assert {correction[key] for key in ("authority_action_count", "fm_invocation_count", "qemu_count", "retry_count", "repair_retry_count", "replay_count")} == {0}


def test_g48_structure_scope_and_repository_boundary() -> None:
    report = REPORT.read_text(encoding="utf-8")
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]
    for question in (
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "Katere nove zmogljivosti (če sploh) nastanejo?",
        "Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "Ali implementacija ustvarja vzporedni tok?",
        "Ali zmanjšuje ali povečuje število produkcijskih poti?",
    ):
        assert report.count(question) == 1
    status = subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=all"], cwd=ROOT, text=True)
    assert all(line.startswith("?? " + KA.relative_to(ROOT).as_posix() + "/") for line in status.splitlines())
    assert subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True).strip() == ""
