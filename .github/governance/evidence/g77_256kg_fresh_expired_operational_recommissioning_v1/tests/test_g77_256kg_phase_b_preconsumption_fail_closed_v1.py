from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[5]
KG = ROOT / ".github/governance/evidence/g77_256kg_fresh_expired_operational_recommissioning_v1"
REDUCTION = KG / "G77_256KG_PHASE_B_PRECONSUMPTION_FAIL_CLOSED_REDUCTION_V1.json"
REPORT = KG / "G77_256KG_G48_IMPLEMENTATION_REPORT_V1.md"
TERMINAL = (
    "M__KG_PHASE_B_HUMAN_SOURCE_TO_CANONICAL_HANDOFF_DIGEST_MISMATCH_"
    "BEFORE_AUTHORITY_CONSUMPTION"
)


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode()


def load_reduction() -> dict:
    raw = REDUCTION.read_bytes()
    envelope = json.loads(raw)
    assert raw == canonical_bytes(envelope)
    reduction = envelope["reduction"]
    assert envelope["reduction_sha256"] == hashlib.sha256(
        canonical_bytes(reduction)
    ).hexdigest()
    return reduction


def test_exact_human_source_authenticated_but_unconsumed() -> None:
    value = load_reduction()
    authority = value["human_authority"]
    assert value["terminal"] == TERMINAL
    assert authority["authentication"] == (
        "VERIFIED__EXACT_HUMAN_SUPPLIED_ACT__UNCONSUMED"
    )
    assert authority["human_source_sha256"] == (
        "d11850611c8c1273dbd1484af40d1d38533f95d8f0665da418885947b32a9484"
    )
    assert authority["authorization_state"] == "AUTHENTICATED__UNCONSUMED"


def test_required_source_to_handoff_equality_fails_closed() -> None:
    binding = load_reduction()["jz_digest_binding"]
    assert binding["derived_human_source_sha256"] != (
        binding["canonical_handoff_authority_digest"]
    )
    assert {
        binding["canonical_handoff_authority_digest"],
        binding["authenticated_canonical_authority_digest"],
        binding["sealed_invocation_authority_digest"],
        binding["final_fm_argv_authority_digest"],
    } == {"1e6c6fec12e064dffa2bd69873664e5a236dde812eb47853c1b7f1c056e8020c"}
    assert binding["commission_required_human_source_equality"] == (
        "NOT_PROVEN__MISMATCH"
    )
    assert binding["negative_binding_rejection_count"] == 13


def test_no_consumption_or_operation_artifact_exists() -> None:
    for name in (
        "G77_256KG_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json",
        "G77_256KG_FM_OPERATIONAL_INVOCATION_ATTEMPT_V1.json",
        "G77_256KG_FM_OPERATIONAL_INVOCATION_RESULT_V1.json",
    ):
        assert not (KG / name).exists()
    counters = load_reduction()["operational_counters"]
    assert counters["operational_authorization_count"] == 1
    assert set(value for key, value in counters.items() if key != "operational_authorization_count") == {0}


def test_e05_architecture_and_terminal_governance_are_preserved() -> None:
    value = load_reduction()
    assert value["e05"] == {
        "state": "VERIFIED__11_OF_18",
        "frontier": "VERIFIED__7_UNSATISFIED_OF_18",
        "credit": "VERIFIED__0",
    }
    assert value["expired"] == "NOT_PROVEN_OPERATIONALLY"
    assert value["ex_reuse"]["ex_reused"] == "VERIFIED__17_OF_17"
    assert value["ex_reuse"]["ex_reconstructed"] == "VERIFIED__0"
    assert value["architecture"]["production_route_before"] == 1
    assert value["architecture"]["production_route_after"] == 1
    assert value["auto_continuable"] is False
    assert value["human_review_required"] is True


def test_g48_and_ria_structure_remain_exact() -> None:
    text = REPORT.read_text(encoding="utf-8")
    assert re.findall(r"^# .+$", text, flags=re.MULTILINE) == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]
    assert len(re.findall(r"^\d+\. .+\?$", text, flags=re.MULTILINE)) == 5
