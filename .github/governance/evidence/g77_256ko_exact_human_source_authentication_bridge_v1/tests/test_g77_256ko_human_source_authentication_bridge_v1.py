from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[5]
KO = ROOT / ".github/governance/evidence/g77_256ko_exact_human_source_authentication_bridge_v1"
ASSESSOR = KO / "analysis/G77_256KO_HUMAN_SOURCE_PROTOCOL_ASSESSOR_V1.py"
REDUCTION = KO / "G77_256KO_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = KO / "G77_256KO_G48_IMPLEMENTATION_REPORT_V1.md"


def load_assessor():
    spec = importlib.util.spec_from_file_location("g77_256ko_assessor", ASSESSOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


A = load_assessor()


def reduction() -> dict:
    raw = REDUCTION.read_bytes()
    envelope = json.loads(raw)
    assert raw == A.canonical_bytes(envelope)
    inner = envelope["reduction"]
    assert envelope["reduction_sha256"] == hashlib.sha256(A.canonical_bytes(inner)).hexdigest()
    return inner


def test_authenticated_inputs_and_direct_human_barrier() -> None:
    A.authenticate_inputs()
    assert not A.KN_SOURCE.exists()
    assert A.instruction_human_bytes() == A.EXPECTED_HUMAN_ACT.encode("utf-8")


def test_terminal_authority_and_all_counters_are_exact() -> None:
    value = reduction()
    assert value == A.build_reduction()
    assert value["terminal"] == A.TERMINAL
    assert value["human_interaction"]["human_authority_present"] is False
    assert value["phase_b_started"] is False
    assert set(value["operational_counters"].values()) == {0}
    assert len(value["operational_counters"]) == 15


def test_protocol_reuse_e05_ex_and_architecture_are_bounded() -> None:
    value = reduction()
    assert value["protocol_discovery"]["authority_source_mechanism"].startswith("VERIFIED__EXISTING")
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
