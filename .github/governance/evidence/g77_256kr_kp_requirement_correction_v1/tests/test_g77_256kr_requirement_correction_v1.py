from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[5]
KR = ROOT / ".github/governance/evidence/g77_256kr_kp_requirement_correction_v1"
REDUCER = KR / "analysis/G77_256KR_REQUIREMENT_CORRECTION_AND_SOURCE_READINESS_V1.py"
CORRECTION = KR / "G77_256KR_SPCE_TERMINAL_CORRECTION_V1.json"
REPORT = KR / "G77_256KR_G48_IMPLEMENTATION_REPORT_V1.md"
SOURCE = ROOT / ".github/governance/evidence/g77_256kn_fresh_expired_operational_recommissioning_v1/G77_256KN_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"


def load_reducer():
    spec = importlib.util.spec_from_file_location("g77_256kr_reducer", REDUCER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_inputs_authenticate_and_class_a_is_exact() -> None:
    module = load_reducer()
    module.authenticate_inputs()
    result = module.build_correction()
    assert result["terminal"] == module.TERMINAL
    assert result["failure_novelty_and_convergence_check"]["failure_class"] == "EVIDENCE_OR_REPORTING_DEFECT"
    assert result["correction"]["correction_status"] == module.CORRECTION_STATUS
    assert result["human_source"]["source_acceptance_readiness"].startswith("VERIFIED__READY")


def test_correction_is_canonical_sealed_and_deterministic() -> None:
    module = load_reducer()
    raw = CORRECTION.read_bytes()
    envelope = json.loads(raw)
    correction = envelope["correction"]
    assert raw == module.canonical_bytes(envelope)
    assert envelope["correction_sha256"] == hashlib.sha256(module.canonical_bytes(correction)).hexdigest()
    assert correction == module.build_correction()


def test_historical_kp_is_preserved_but_forward_overconstraint_is_superseded() -> None:
    result = load_reducer().build_correction()
    assert result["historical_evidence"]["kp_historical_status"].startswith("VERIFIED__IMMUTABLE_VALID_FAIL_CLOSED")
    assert result["correction"]["correction_status"] == "SUPERSEDED_FOR_FORWARD_KN_ACCEPTANCE_BY_AUTHENTICATED_KQ_CLASSIFICATION"
    assert result["correction"]["authority_created"] == "VERIFIED__NO"


def test_anti_weakening_is_complete() -> None:
    anti = load_reducer().build_correction()["anti_weakening"]
    assert anti["anti_weakening_status"] == "VERIFIED__ALL_AUTHENTICATED_ACCEPTANCE_INVARIANTS_RETAINED"
    assert len(anti) == 19
    assert all(value.startswith("VERIFIED__") for value in anti.values())


def test_source_immutable_and_not_promoted_to_authority() -> None:
    module = load_reducer()
    raw = SOURCE.read_bytes()
    result = module.build_correction()["human_source"]
    assert len(raw) == 1213 and raw.count(b"\n") == 14
    assert hashlib.sha256(raw).hexdigest() == module.SOURCE_SHA256
    assert raw == module.exact_human_bytes()
    assert result["authority_present"] is False
    assert result["human_authority_authentication"].startswith("NOT_APPLICABLE__")
    assert result["human_authority_binding"].startswith("NOT_APPLICABLE__")


def test_zero_operation_e05_ex_and_architecture_invariants() -> None:
    result = load_reducer().build_correction()
    assert len(result["operational_counters"]) == 15
    assert set(result["operational_counters"].values()) == {0}
    assert result["phase_b_started"] is False
    assert result["e05"]["before"] == result["e05"]["after"] == "VERIFIED__11_OF_18"
    assert result["e05"]["credit"] == result["e05"]["kn_e05_credit"] == "VERIFIED__0"
    assert result["ex"] == {"ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0"}
    architecture = result["architecture"]
    assert architecture["production_route_before"] == architecture["production_route_after"] == 1
    assert architecture["parallel_flow"] == "NO"
    assert set(value for key, value in architecture.items() if key.endswith("_count")) == {0}


def test_python_ast_g48_and_exact_ria_structure() -> None:
    ast.parse(REDUCER.read_text(encoding="utf-8"))
    ast.parse(Path(__file__).read_text(encoding="utf-8"))
    report = REPORT.read_text(encoding="utf-8")
    assert re.findall(r"^# (.+)$", report, flags=re.MULTILINE) == [
        "1. Implementation Summary",
        "2. Code Evidence",
        "3. Constitutional Self-Assessment",
        "4. Validation Matrix",
        "5. Repository Mutation Summary",
        "6. Certification Verdict",
    ]
    assert re.findall(r"^[1-5]\. (.+\?)$", report, flags=re.MULTILINE) == [
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "Katere nove zmogljivosti (če sploh) nastanejo?",
        "Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "Ali implementacija ustvarja vzporedni tok?",
        "Ali zmanjšuje ali povečuje število produkcijskih poti?",
    ]
