from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[5]
KP = ROOT / ".github/governance/evidence/g77_256kp_posthuman_source_authentication_v1"
REDUCER = KP / "analysis/G77_256KP_SOURCE_PROVENANCE_FAILURE_REDUCER_V1.py"
REDUCTION = KP / "G77_256KP_SPCE_TERMINAL_FAIL_CLOSED_REDUCTION_V1.json"
REPORT = KP / "G77_256KP_G48_IMPLEMENTATION_REPORT_V1.md"


def load_reducer():
    spec = importlib.util.spec_from_file_location("g77_256kp_reducer", REDUCER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


R = load_reducer()


def reduction() -> dict:
    raw = REDUCTION.read_bytes()
    envelope = json.loads(raw)
    assert raw == R.canonical_bytes(envelope)
    inner = envelope["reduction"]
    assert envelope["reduction_sha256"] == hashlib.sha256(R.canonical_bytes(inner)).hexdigest()
    return inner


def test_source_is_exact_fresh_and_unmodified() -> None:
    result = R.authenticate_inputs()
    assert result["byte_count"] == 1213
    assert result["lf_count"] == 14
    assert result["sha256"] == R.SOURCE_SHA256
    assert result["exact_byte_match"] is True
    assert R.SOURCE.read_bytes() == R.expected_source_bytes()


def test_provenance_fails_closed_before_authority_or_phase_b() -> None:
    value = reduction()
    assert value == R.build_reduction()
    assert value["terminal"] == R.TERMINAL
    assert value["human_source"]["human_authority_present"] is False
    assert value["human_source"]["human_authority_binding"].startswith("NOT_APPLICABLE__")
    assert value["phase_b_started"] is False
    assert set(value["operational_counters"].values()) == {0}
    assert len(value["operational_counters"]) == 15


def test_e05_ex_and_architecture_are_unchanged() -> None:
    value = reduction()
    assert value["e05"]["before"] == value["e05"]["after"] == "VERIFIED__11_OF_18"
    assert value["e05"]["kn_e05_credit"] == "VERIFIED__0"
    assert value["ex"] == {"ex_reconstructed": "VERIFIED__0", "ex_reused": "VERIFIED__17_OF_17"}
    architecture = value["architecture"]
    assert architecture["production_route_before"] == architecture["production_route_after"] == 1
    assert architecture["parallel_flow"] == "NO"
    assert {v for k, v in architecture.items() if k.endswith("_count")} == {0}


def test_report_has_exact_six_h1_and_five_ria_questions() -> None:
    text = REPORT.read_text(encoding="utf-8")
    assert [line for line in text.splitlines() if line.startswith("# ")] == [
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
