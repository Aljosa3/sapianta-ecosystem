#!/usr/bin/env python3
"""Authenticate the consumed IY one-shot pre-request terminal without replay."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
IY = ROOT / ".github/governance/evidence/g77_256iy_future_operational_v1"
REPORT = IY / "G77_256IY_G48_IMPLEMENTATION_REPORT_V1.md"
TERMINAL = IY / "G77_256IY_SPCE_TERMINAL_REDUCTION_V1.json"
SERIAL = IY / "G77_256IY_SERIAL_CONSOLE_V1.log"
PRE = IY / "operation_state/receipts/G77_256IY_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
POST = IY / "operation_state/receipts/G77_256IY_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
CONTROLLER = IY / "orchestration/G77_256IY_AUTHORITY_CONSUMPTION_CONTROLLER_V1.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


C = load_module(CONTROLLER, "g77_256iy_phase_b_controller")


def unique(pairs):
    result = {}
    for key, value in pairs:
        assert key not in result
        result[key] = value
    return result


def load(path: Path) -> dict:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique)
    assert raw == C.FM.canonical_bytes(value)
    return value


def test_exact_human_authority_and_single_consumption() -> None:
    assert C.GRANT_PATH.read_text(encoding="utf-8").replace("\\_", "_") == C.EXPECTED_NORMALIZED_GRANT
    authority = load(C.HANDOFF_PATH)
    checkpoint = load(C.CONSUMPTION_PATH)["checkpoint"]
    assert authority["authorization"]["authorization_present"] is True
    assert authority["authorization"]["authorization_reusable"] is False
    assert checkpoint["human_grant_binding_status"] == "VERIFIED"
    assert checkpoint["authority_state_before"] == "GRANTED_UNCONSUMED"
    assert checkpoint["authority_state_after"] == "CONSUMED"
    assert checkpoint["authority_consumed"] == 1
    assert checkpoint["operational_counters"]["authority_consumption"] == 1


def test_one_pre_fm_no_network_qemu_vm_attempt_and_no_retry() -> None:
    pre = load(PRE)
    post = load(POST)
    assert pre["generation_identity"] == post["generation_identity"] == C.GENERATION
    assert pre["operation_identity"] == post["operation_identity"] == C.OPERATION
    assert pre["started_unix_ns"] == post["started_unix_ns"]
    assert pre["execution_attempt_count"] == post["execution_attempt_count"] == 1
    assert pre["automatic_retry_count"] == post["automatic_retry_count"] == 0
    assert pre["vector"] == post["vector"]
    assert post["process_exit_status"] == 0
    argv = pre["vector"]["argv"]
    assert argv.count("-nic") == 1 and argv[argv.index("-nic") + 1] == "none"
    assert sum("qemu-system-x86_64" in item for item in argv) == 1


def test_import_root_succeeded_then_exact_entrypoint_failure() -> None:
    raw = SERIAL.read_bytes()
    boot = raw.index(b"G77_256FM_BOOT_MARKER=PASS")
    failure = raw.index(b"repository-only FUTURE adapter; no operational CLI entry point")
    exit_status = raw.index(b"G77_256FM_HARNESS_EXIT_STATUS=1")
    assert boot < failure < exit_status
    assert b"ModuleNotFoundError" not in raw
    assert hashlib.sha256(raw).hexdigest() == "9ecb8f66d6e6f9f786621682bcf6b46929bbeea951875dfcaca583f93f61d343"


def test_terminal_reduces_actual_zero_request_denial_p11_and_effect() -> None:
    envelope = load(TERMINAL)
    reduction = envelope["reduction"]
    assert envelope["reduction_sha256"] == hashlib.sha256(C.FM.canonical_bytes(reduction)).hexdigest()
    assert reduction["terminal"] == "E__AUTHORIZED_OPERATION_FAILED_BEFORE_REQUEST"
    assert reduction["last_verified_edge"].endswith("FUTURE_GUEST_ADAPTER_TOP_LEVEL_AIGOL_IMPORTS_SUCCEEDED")
    assert reduction["first_broken_edge"] == "FUTURE_GUEST_ADAPTER_OPERATIONAL_CLI_ENTRYPOINT_ABSENT"
    assert reduction["exact_failure"] == "repository-only FUTURE adapter; no operational CLI entry point"
    counters = reduction["operational_counters"]
    assert counters["human_authorization_presentation"] == 1
    assert counters["human_operational_authority"] == 1
    assert counters["authority_consumption"] == counters["pre"] == 1
    assert counters["fm_operational_launcher_invocation"] == counters["qemu"] == 1
    assert counters["vm_boot"] == counters["operation_attempt"] == 1
    for key in ("future_operation", "request", "future_denial", "p11_entry",
                "protected_invocation", "protected_effect", "retry", "repair_retry",
                "replay", "second_consumption", "e05_credit"):
        assert counters[key] == 0
    assert reduction["e05"] == {"before": "10/18", "credit": 0, "after": "10/18"}
    assert reduction["terminal_control"]["auto_continuable"] is False
    assert reduction["terminal_control"]["next_generation_started"] is False


def test_no_guest_effect_evidence_qemu_or_transient_state_remains() -> None:
    runtime = IY / "operation_state/runtime_export"
    absent = (
        runtime / "G77_256IY_RAW_EXECUTION_EVIDENCE_V1.jsonl",
        runtime / "G77_256IY_GUEST_EXECUTION_SEAL_V1.json",
        runtime / "G77_256IY_GUEST_TEARDOWN_SEAL_V1.json",
    )
    assert all(not path.exists() for path in absent)
    assert not Path("/tmp/g77_256iy_future_operational_v1").exists()
    assert subprocess.run(
        ["pgrep", "-f", "^/usr/bin/qemu-system-x86_64.*g77_256iy"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
    ).returncode != 0


def test_all_json_seals_ast_and_exact_six_report_headings() -> None:
    for path in IY.rglob("*.json"):
        value = load(path)
        for inner, seal in (("reduction", "reduction_sha256"), ("proof", "proof_sha256"),
                            ("checkpoint", "checkpoint_sha256"), ("request", "request_sha256"),
                            ("observation", "observation_sha256"), ("seal", "seal_sha256")):
            if inner in value and seal in value:
                assert value[seal] == hashlib.sha256(C.FM.canonical_bytes(value[inner])).hexdigest()
    for path in IY.rglob("*.py"):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    headings = [line for line in REPORT.read_text(encoding="utf-8").splitlines() if line.startswith("# ")]
    assert headings == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]


def test_index_empty_and_production_route_unchanged() -> None:
    assert subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True).strip() == ""
    assert subprocess.check_output(
        ["git", "diff", "--name-only", C.HEAD, "--", "aigol/runtime", "sapianta_system",
         ".github/governance/evidence/g77_256ec_p11_operational_v1",
         ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1"],
        cwd=ROOT, text=True,
    ).strip() == ""
