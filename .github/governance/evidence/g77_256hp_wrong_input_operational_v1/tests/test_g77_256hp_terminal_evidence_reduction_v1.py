#!/usr/bin/env python3
"""Repository-only authentication of terminal G77-256HP evidence."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
HP = ROOT / ".github/governance/evidence/g77_256hp_wrong_input_operational_v1"
RUNTIME = HP / "operation_state/runtime_export"
RECEIPTS = HP / "operation_state/receipts"
SUCCESS = (
    "VERIFIED__G77_256HP_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_INPUT_OPERATIONAL_"
    "COMMISSIONING__ONE_AUTHORITY__ONE_PRE__ONE_FM__ONE_NO_NETWORK_QEMU__"
    "ONE_VM_BOOT__WRONG_INPUT_REQUEST_ACCEPTED_AS_VECTOR_AND_DENIED_BEFORE_"
    "PROTECTED_EXECUTION__ZERO_RETRY__AUTHORITATIVE_AND_INDEPENDENT_REDUCERS_"
    "AGREE__E05_8_OF_18__HUMAN_REVIEW_REQUIRED"
)


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def load_unique(path: Path) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            assert key not in result, f"duplicate JSON key: {key}"
            result[key] = value
        return result

    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique)
    assert isinstance(value, dict)
    assert raw == canonical_bytes(value)
    return value


def envelope(path: Path, key: str) -> dict[str, Any]:
    outer = load_unique(path)
    assert outer[f"{key}_sha256"] == hashlib.sha256(canonical_bytes(outer[key])).hexdigest()
    return outer[key]


def test_exact_base_grant_consumption_and_single_no_network_receipt_pair() -> None:
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() == "fc9bc52bbd708a40f884f2fc006ebe0e3f6e4df8"
    assert subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT, text=True).strip() == "9256a995bf9b90714e759dae98d2bed4c3de8f22"
    assert subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True).strip() == ""
    checkpoint = envelope(HP / "G77_256HP_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json", "checkpoint")
    assert checkpoint["authority_state_after"] == "CONSUMED"
    assert checkpoint["authority_consumed"] == 1
    assert checkpoint["operational_counters"]["authority_consumption"] == 1
    pre = load_unique(RECEIPTS / "G77_256HP_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json")
    post = load_unique(RECEIPTS / "G77_256HP_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json")
    assert pre["started_unix_ns"] == post["started_unix_ns"]
    assert pre["execution_attempt_count"] == post["execution_attempt_count"] == 1
    assert pre["automatic_retry_count"] == post["automatic_retry_count"] == 0
    assert post["process_exit_status"] == 0
    argv = pre["vector"]["argv"]
    assert argv.count("-nic") == 1
    assert argv[argv.index("-nic") + 1] == "none"
    assert pre["vector"]["canonical_argv_sha256"] == "32b1bcbc80035e5f12ff5b73c83d44baeebf68cb7e9e515ae32fb47fd05178d5"


def test_raw_guest_evidence_and_independent_reduction() -> None:
    raw_path = RUNTIME / "G77_256HP_RAW_EXECUTION_EVIDENCE_V1.jsonl"
    assert hashlib.sha256(raw_path.read_bytes()).hexdigest() == "116f694f80e95d88104df7d8b01ed0458212ae0b5d0222cd86419443c8d0f189"
    records = [json.loads(line) for line in raw_path.read_text().splitlines()]
    assert len(records) == 31
    by_type = {record["record_type"]: record for record in records}
    facts = by_type["wrong_input_denial_complete"]["facts"]
    assert facts["differing_input_fields"] == ["input_identity", "record_identity"]
    assert facts["denial_point"].startswith("D2_PRECLAIM_AUTHORITY_BINDING_VALIDATION")
    assert facts["claim_attempted"] is False
    assert by_type["b6_boundary_request_counter"]["facts"]["value"] == 1
    assert by_type["b6_p11_entry_counter"]["facts"]["value"] == 0
    assert by_type["b6_invocation_counter"]["facts"]["value"] == 0
    assert by_type["b6_protected_effect_counter"]["facts"]["value"] == 0
    independent = envelope(HP / "G77_256HP_INDEPENDENT_OPERATIONAL_REDUCTION_V1.json", "reduction")
    assert independent["authoritative_result_used_as_input"] is False
    assert independent["operational_criterion_satisfied"] is True
    assert independent["independent_reducer_status"] == "VERIFIED"


def test_authoritative_gy_reducer_replays_normalized_actual_evidence() -> None:
    normalization = envelope(HP / "G77_256HP_GY_OPERATIONAL_EVIDENCE_NORMALIZATION_V1.json", "normalization")
    assert normalization["source_raw_evidence_sha256"] == "116f694f80e95d88104df7d8b01ed0458212ae0b5d0222cd86419443c8d0f189"
    assert normalization["normalization_changes_observed_values"] is False
    reducer_path = ROOT / ".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/reducer/G77_256GY_WRONG_INPUT_TERMINAL_ACCEPTANCE_REDUCER_V1.py"
    spec = importlib.util.spec_from_file_location("g77_256hp_test_gy_reducer", reducer_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    result = module.reduce_wrong_input_terminal_evidence(normalization["normalized_packet"])
    assert result["terminal_acceptance"] == "PASS__COMPLETE_WRONG_INPUT_D2_DENIAL_EVIDENCE"
    authoritative = envelope(HP / "G77_256HP_GY_AUTHORITATIVE_OPERATIONAL_REDUCTION_V1.json", "reduction")
    assert authoritative["authoritative_gy_reducer_status"] == "VERIFIED"
    assert authoritative["result"] == result
    assert authoritative["operational_criterion_satisfied"] is True


def test_agreement_e05_teardown_and_final_seals() -> None:
    expected = {
        "human_operational_authority": 1, "authority_consumption": 1, "pre": 1,
        "fm_operational_launcher_invocation": 1, "qemu": 1, "vm_creation": 1,
        "vm_boot": 1, "operation_attempt": 1, "wrong_input_operation": 1,
        "request": 1, "p11_entry": 0, "protected_invocation": 0,
        "protected_effect": 0, "retry": 0, "repair_and_continue": 0,
        "operational_replay": 0, "e05_credit": 1,
    }
    agreement = envelope(HP / "G77_256HP_REDUCER_AGREEMENT_V1.json", "agreement")
    assert agreement["reducer_agreement_status"] == "VERIFIED"
    assert agreement["e05"] == {"before": "7/18", "credit": 1, "after": "8/18"}
    teardown = envelope(HP / "G77_256HP_SPCE_HOST_TEARDOWN_CHECKPOINT_V1.json", "checkpoint")
    assert teardown["host_teardown"]["transient_root_absent"] is True
    assert teardown["base_image"]["byte_identical"] is True
    assert not Path("/tmp/g77_256hp_wrong_input_operational_v1").exists()
    final = envelope(HP / "G77_256HP_SPCE_FINAL_EXECUTION_SEAL_V1.json", "seal")
    terminal = envelope(HP / "G77_256HP_SPCE_TERMINAL_REDUCTION_V1.json", "reduction")
    assert final["operational_counters"] == terminal["operational_counters"] == expected
    assert final["final_result"] == terminal["terminal_control"]["verdict"] == SUCCESS
    assert final["wrong_input_operational_capability"] == "VERIFIED"
    assert terminal["e05"] == {"before": "7/18", "credit": 1, "after": "8/18"}


def test_all_hp_json_canonical_serial_and_report_structure() -> None:
    for path in sorted(HP.rglob("*.json")):
        load_unique(path)
    serial = HP / "G77_256HP_SERIAL_CONSOLE_V1.log"
    assert hashlib.sha256(serial.read_bytes()).hexdigest() == "a4eaa1944f809ec6ff93ea025e6d0e7240a81e2ae32666dfd760d2c19f850ec4"
    assert b"G77_256FM_BOOT_MARKER=PASS" in serial.read_bytes()
    assert b"G77_256FM_HARNESS_EXIT_STATUS=0" in serial.read_bytes()
    report = (ROOT / "docs/governance/G77_256HP_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_INPUT_OPERATIONAL_COMMISSIONING_V1.md").read_text()
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]
    assert report.rstrip().endswith(SUCCESS)
