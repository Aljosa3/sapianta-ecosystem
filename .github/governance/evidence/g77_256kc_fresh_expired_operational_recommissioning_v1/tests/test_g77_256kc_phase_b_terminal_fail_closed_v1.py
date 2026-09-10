from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
KC = ROOT / ".github/governance/evidence/g77_256kc_fresh_expired_operational_recommissioning_v1"
TERMINAL = KC / "G77_256KC_SPCE_PHASE_B_TERMINAL_FAIL_CLOSED_REDUCTION_V1.json"
REPORT = KC / "G77_256KC_PHASE_B_G48_IMPLEMENTATION_REPORT_V1.md"


def canonical_bytes(value) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def reduction() -> dict:
    raw = TERMINAL.read_bytes()
    envelope = json.loads(raw)
    assert raw == canonical_bytes(envelope)
    value = envelope["reduction"]
    assert envelope["reduction_sha256"] == hashlib.sha256(canonical_bytes(value)).hexdigest()
    return value


def test_terminal_is_fail_closed_before_authority_consumption() -> None:
    value = reduction()
    assert value["terminal"] == (
        "M__KC_PHASE_B_FAIL_CLOSED_AT_PRECONSUMPTION_ENTRY_OWNER_INTERFACE_"
        "BEFORE_AUTHORITY_AUTHENTICATION_OR_CONSUMPTION"
    )
    assert value["failure"]["exact_exception"] == (
        "AttributeError: module 'g77_256kc_phase_b_materializer' has no attribute 'A'"
    )
    assert set(value["operational_counters"].values()) == {0}
    assert value["human_authority"]["canonical_authority_handoff_file_sha256"] is None
    assert value["jz_preconsumption_binding"]["invocation_binding_created"] is False
    assert value["e05"] == {
        "credit": "VERIFIED__0",
        "expired": "NOT_PROVEN_OPERATIONALLY",
        "frontier": "VERIFIED__7_UNSATISFIED_OF_18",
        "state": "VERIFIED__11_OF_18",
    }


def test_no_consumption_or_operation_artifacts_exist() -> None:
    forbidden = (
        "G77_256KC_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json",
        "G77_256KC_PRECONSUMPTION_INVOCATION_BINDING_V1.json",
        "G77_256KC_PHASE_B_PRECONSUMPTION_READINESS_CHECKPOINT_V1.json",
        "G77_256KC_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json",
        "G77_256KC_FM_OPERATIONAL_INVOCATION_ATTEMPT_V1.json",
        "G77_256KC_FM_OPERATIONAL_INVOCATION_RESULT_V1.json",
    )
    assert all(not (KC / name).exists() for name in forbidden)
    receipts = KC / "operation_state/receipts"
    assert receipts.is_dir()
    assert not any(receipts.iterdir())


def test_g48_and_reuse_impact_structures_are_exact() -> None:
    report = REPORT.read_text(encoding="utf-8")
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    questions = (
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "Katere nove zmogljivosti (če sploh) nastanejo?",
        "Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "Ali implementacija ustvarja vzporedni tok?",
        "Ali zmanjšuje ali povečuje število produkcijskih poti?",
    )
    assert all(report.count(question) == 1 for question in questions)
