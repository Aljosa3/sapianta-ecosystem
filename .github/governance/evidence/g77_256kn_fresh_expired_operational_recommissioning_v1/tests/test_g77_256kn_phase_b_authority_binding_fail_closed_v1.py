from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[5]
KN = ROOT / ".github/governance/evidence/g77_256kn_fresh_expired_operational_recommissioning_v1"
REDUCER = KN / "analysis/G77_256KN_PHASE_B_AUTHORITY_BINDING_FAILURE_REDUCER_V1.py"
REDUCTION = KN / "G77_256KN_PHASE_B_AUTHORITY_BINDING_FAIL_CLOSED_REDUCTION_V1.json"
REPORT = KN / "G77_256KN_PHASE_B_G48_IMPLEMENTATION_REPORT_V1.md"


def load_reducer():
    spec = importlib.util.spec_from_file_location("g77_256kn_authority_failure", REDUCER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


R = load_reducer()


def load_reduction() -> dict:
    raw = REDUCTION.read_bytes()
    envelope = json.loads(raw)
    assert raw == R.canonical_bytes(envelope)
    reduction = envelope["reduction"]
    assert envelope["reduction_sha256"] == hashlib.sha256(R.canonical_bytes(reduction)).hexdigest()
    return reduction


def test_exact_input_state_and_missing_authoritative_source() -> None:
    R.authenticate_input_state()
    assert not R.SOURCE.exists()
    assert all(not (KN / name).exists() for name in R.FORBIDDEN_PHASE_B_ARTIFACTS)


def test_fail_closed_reduction_is_exact_and_all_counters_are_zero() -> None:
    reduction = load_reduction()
    assert reduction == R.build_reduction()
    assert reduction["terminal"] == R.TERMINAL
    assert reduction["phase_b_started"] is False
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["human_authority"]["human_authority_present"] is False
    assert reduction["human_authority"]["authority_consumption_count"] == 0


def test_e05_ex_and_architecture_are_unchanged() -> None:
    reduction = load_reduction()
    assert reduction["e05"]["before"] == "VERIFIED__11_OF_18"
    assert reduction["e05"]["after"] == "VERIFIED__11_OF_18"
    assert reduction["e05"]["kn_e05_credit"] == "VERIFIED__0"
    assert reduction["e05"]["expired"] == "NOT_PROVEN_OPERATIONALLY"
    assert reduction["ex"] == {
        "ex_reconstructed": "VERIFIED__0",
        "ex_reused": "VERIFIED__17_OF_17",
    }
    architecture = reduction["architecture"]
    assert architecture["production_route_before"] == architecture["production_route_after"] == 1
    assert architecture["parallel_flow"] == "NO"
    assert {value for key, value in architecture.items() if key.endswith("_count")} == {0}


def test_g48_has_exact_six_h1_and_five_ria_questions() -> None:
    text = REPORT.read_text(encoding="utf-8")
    headings = [line for line in text.splitlines() if line.startswith("# ")]
    assert headings == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    questions = [
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "Katere nove zmogljivosti (če sploh) nastanejo?",
        "Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "Ali implementacija ustvarja vzporedni tok?",
        "Ali zmanjšuje ali povečuje število produkcijskih poti?",
    ]
    assert all(text.count(question) == 1 for question in questions)
