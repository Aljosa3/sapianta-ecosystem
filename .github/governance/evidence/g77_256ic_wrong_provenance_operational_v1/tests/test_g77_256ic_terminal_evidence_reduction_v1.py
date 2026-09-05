#!/usr/bin/env python3
"""Repository-only authentication of terminal G77-256IC evidence."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
IC = ROOT / ".github/governance/evidence/g77_256ic_wrong_provenance_operational_v1"
RUNTIME = IC / "operation_state/runtime_export"
RECEIPTS = IC / "operation_state/receipts"
HZ_REDUCER = ROOT / (
    ".github/governance/evidence/g77_256hz_wrong_provenance_formalization_v1/"
    "reducer/G77_256HZ_WRONG_PROVENANCE_REPOSITORY_CAPABILITY_REDUCER_V1.py"
)
REPORT = ROOT / (
    "docs/governance/"
    "G77_256IC_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_PROVENANCE_OPERATIONAL_COMMISSIONING_V1.md"
)
HEAD = "ec2c4997ba62fbaa5e774fc9ba010f6319926c73"
TREE = "887f329b030582f01a49f6c0c97f54ed4f55a818"
RAW_SHA256 = "0369cf40d063a1d87c93fa2ff499eb3dd4573973485f88eb22234d4cd5062a5f"
SERIAL_SHA256 = "16b435fc2f2b6b47d2e705ba8e5f22d223c831b85d4adc63197703ed7ce05406"
HZ_REDUCER_SHA256 = "b30c082185ebe185a0be0504a44ebc97d8f20a201b143a93b8d53e2e356a6585"
EXPECTED_DENIAL = (
    "D2_PRECLAIM_AUTHORITY_BINDING_VALIDATION_BEFORE_PRECLAIM_LEDGER_APPEND_"
    "CLAIM_ENTRY_INVOCATION_OR_EFFECT"
)
EXPECTED_REASON = "operational Human act input_record_identity binding is invalid"
SUCCESS = (
    "VERIFIED__G77_256IC_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_PROVENANCE_OPERATIONAL_"
    "COMMISSIONING__ONE_AUTHORITY__ONE_PRE__ONE_FM__ONE_NO_NETWORK_QEMU__"
    "ONE_VM_CREATION__ONE_VM_BOOT__WRONG_PROVENANCE_REQUEST_DENIED_AT_D2_BEFORE_"
    "P11_ENTRY_INVOCATION_OR_EFFECT__ZERO_RETRY__AUTHORITATIVE_AND_INDEPENDENT_"
    "REDUCERS_AGREE__E05_10_OF_18__HUMAN_REVIEW_REQUIRED"
)


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_unique(path: Path) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            assert key not in result, f"duplicate JSON key: {path.name}:{key}"
            result[key] = value
        return result

    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique)
    assert isinstance(value, dict)
    assert raw == canonical_bytes(value)
    return value


def envelope(path: Path, key: str) -> dict[str, Any]:
    outer = load_unique(path)
    assert outer[f"{key}_sha256"] == hashlib.sha256(
        canonical_bytes(outer[key])
    ).hexdigest()
    return outer[key]


def one(records: list[dict[str, Any]], record_type: str) -> dict[str, Any]:
    matches = [record for record in records if record.get("record_type") == record_type]
    assert len(matches) == 1
    return matches[0]


def load_hz_reducer():
    assert sha256(HZ_REDUCER) == HZ_REDUCER_SHA256
    specification = importlib.util.spec_from_file_location(
        "g77_256ic_test_hz_reducer", HZ_REDUCER
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


def test_exact_base_consumed_authority_and_single_no_network_receipt_pair() -> None:
    assert subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip() == HEAD
    assert subprocess.check_output(
        ["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT, text=True
    ).strip() == TREE
    assert subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True
    ).strip() == ""
    checkpoint = envelope(
        IC / "G77_256IC_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json",
        "checkpoint",
    )
    assert checkpoint["authority_state_after"] == "CONSUMED"
    assert checkpoint["authority_consumed"] == 1
    assert checkpoint["operational_counters"]["authority_consumption"] == 1
    pre = load_unique(RECEIPTS / "G77_256IC_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json")
    post = load_unique(RECEIPTS / "G77_256IC_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json")
    assert pre["started_unix_ns"] == post["started_unix_ns"]
    assert pre["execution_attempt_count"] == post["execution_attempt_count"] == 1
    assert pre["automatic_retry_count"] == post["automatic_retry_count"] == 0
    assert post["process_exit_status"] == 0
    assert pre["vector"] == post["vector"]
    argv = pre["vector"]["argv"]
    assert argv.count("-nic") == 1 and argv[argv.index("-nic") + 1] == "none"
    assert pre["vector"]["canonical_argv_sha256"] == (
        "b2be4c56b989dbfde79cdfdcc86354b23c3d4d3d8c3b80b06aaead99336d4bf9"
    )


def test_raw_evidence_proves_exact_wrong_provenance_denial_and_zero_effect() -> None:
    raw = RUNTIME / "G77_256IC_RAW_EXECUTION_EVIDENCE_V1.jsonl"
    assert sha256(raw) == RAW_SHA256
    records = [json.loads(line) for line in raw.read_text().splitlines()]
    assert len(records) == 31
    assert [record["record_sequence"] for record in records] == list(range(31))
    facts = one(records, "wrong_provenance_denial_complete")["facts"]
    assert facts["differing_input_fields"] == ["provenance_identity", "record_identity"]
    assert facts["wrong_provenance_invariant_pass"] is True
    assert facts["denial_point"] == EXPECTED_DENIAL
    assert facts["denial_error"] == EXPECTED_REASON
    assert facts["claim_attempted"] is False
    assert facts["owner_state_before"] == facts["owner_state_after"]
    assert facts["owner_revision_files_unchanged"] is True
    assert facts["runtime_ledger_root_exists"] is False
    assert facts["output_present"] is False
    assert one(records, "b6_boundary_request_counter")["facts"]["value"] == 1
    assert one(records, "b6_pre_attempt_denial_counter")["facts"]["value"] == 1
    assert one(records, "b6_p11_entry_counter")["facts"]["value"] == 0
    assert one(records, "b6_invocation_counter")["facts"]["value"] == 0
    assert one(records, "b6_protected_effect_counter")["facts"]["value"] == 0
    assert one(records, "b6_producer_consumer_reduction")["facts"][
        "producer_consumer_agreement"
    ] is True


def test_hz_authoritative_and_independent_reducers_agree() -> None:
    normalization = envelope(
        IC / "G77_256IC_HZ_OPERATIONAL_EVIDENCE_NORMALIZATION_V1.json",
        "normalization",
    )
    assert normalization["source_raw_evidence_sha256"] == RAW_SHA256
    assert normalization["source_raw_record_count"] == 31
    assert normalization["normalization_changes_observed_values"] is False
    packet = normalization["normalized_packet"]
    hz = load_hz_reducer()
    hz._validate_input_record(packet["authorized_input_record"], prefix="AUTHORIZED_TEST")
    hz._validate_input_record(packet["supplied_input_record"], prefix="SUPPLIED_TEST")
    assert packet["differing_input_fields"] == hz.EXPECTED_DIFFERING_FIELDS
    assert packet["denial_boundary"] == hz.EXPECTED_DENIAL_BOUNDARY
    assert packet["denial_error_type"] == hz.EXPECTED_ERROR_TYPE
    assert packet["denial_error_reason"] == hz.EXPECTED_ERROR_REASON
    authoritative = envelope(
        IC / "G77_256IC_HZ_AUTHORITATIVE_OPERATIONAL_REDUCTION_V1.json", "reduction"
    )
    assert authoritative["reducer_sha256"] == HZ_REDUCER_SHA256
    assert authoritative["authoritative_reducer_status"] == "VERIFIED"
    assert authoritative["result"]["terminal_acceptance"] == "ACCEPT"
    assert authoritative["operational_criterion_satisfied"] is True
    independent = envelope(
        IC / "G77_256IC_INDEPENDENT_OPERATIONAL_REDUCTION_V1.json", "reduction"
    )
    assert independent["authoritative_result_used_as_input"] is False
    assert independent["independent_reducer_result"] == "ACCEPT"
    assert independent["operational_criterion_satisfied"] is True
    agreement = envelope(IC / "G77_256IC_REDUCER_AGREEMENT_V1.json", "agreement")
    assert agreement["reducer_agreement_status"] == "VERIFIED"
    assert agreement["e05"] == {"before": "9/18", "credit": 1, "after": "10/18"}


def test_terminal_counters_seals_and_host_teardown() -> None:
    expected = {
        "human_operational_authority": 1,
        "authority_consumption": 1,
        "pre": 1,
        "fm_operational_launcher_invocation": 1,
        "qemu": 1,
        "vm_creation": 1,
        "vm_boot": 1,
        "operation_attempt": 1,
        "wrong_provenance_operation": 1,
        "request": 1,
        "p11_entry": 0,
        "protected_invocation": 0,
        "protected_effect": 0,
        "retry": 0,
        "repair_retry": 0,
        "replay": 0,
        "e05_credit": 1,
    }
    teardown = envelope(
        IC / "G77_256IC_SPCE_HOST_TEARDOWN_CHECKPOINT_V1.json", "checkpoint"
    )
    assert teardown["host_teardown"]["state"] == "TEARDOWN_COMPLETE"
    assert teardown["host_teardown"]["transient_root_absent"] is True
    assert teardown["base_image"]["byte_identical"] is True
    assert not Path("/tmp/g77_256ic_wrong_provenance_operational_v1").exists()
    final = envelope(IC / "G77_256IC_SPCE_FINAL_EXECUTION_SEAL_V1.json", "seal")
    terminal = envelope(IC / "G77_256IC_SPCE_TERMINAL_REDUCTION_V1.json", "reduction")
    assert final["operational_counters"] == terminal["operational_counters"] == expected
    assert final["final_result"] == terminal["terminal_control"]["verdict"] == SUCCESS
    assert final["wrong_provenance_operational_capability"] == "VERIFIED"
    assert terminal["e05"] == {"before": "9/18", "credit": 1, "after": "10/18"}
    assert terminal["terminal_control"]["auto_continuable"] is False
    assert terminal["terminal_control"]["human_review_required"] is True
    for relative, identity in final["artifacts"].items():
        assert sha256(ROOT / relative) == identity


def test_all_ic_json_serial_and_g48_report_are_canonical() -> None:
    for path in sorted(IC.rglob("*.json")):
        load_unique(path)
    serial = IC / "G77_256IC_SERIAL_CONSOLE_V1.log"
    assert sha256(serial) == SERIAL_SHA256
    assert b"G77_256FM_BOOT_MARKER=PASS" in serial.read_bytes()
    assert b"G77_256FM_HARNESS_EXIT_STATUS=0" in serial.read_bytes()
    report = REPORT.read_text()
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    assert report.rstrip().endswith(SUCCESS)
