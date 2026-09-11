from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[5]
KS = ROOT / ".github/governance/evidence/g77_256ks_existing_kn_authority_authentication_binding_readiness_v1"
REDUCER = KS / "analysis/G77_256KS_AUTHORITY_AUTHENTICATION_AND_BINDING_READINESS_V1.py"
READINESS = KS / "G77_256KS_CANONICAL_BINDING_READINESS_V1.json"
REPORT = KS / "G77_256KS_G48_IMPLEMENTATION_REPORT_V1.md"
SOURCE = ROOT / ".github/governance/evidence/g77_256kn_fresh_expired_operational_recommissioning_v1/G77_256KN_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"


def load_reducer():
    spec = importlib.util.spec_from_file_location("g77_256ks_reducer", REDUCER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_inputs_authenticate_and_terminal_is_exact() -> None:
    module = load_reducer()
    authenticated = module.authenticate_inputs()
    result = module.build_readiness()
    assert authenticated["handoff_byte_count"] == 1715
    assert result["terminal"] == module.TERMINAL
    assert result["failure_novelty_and_convergence_check"]["failure_class"] == "PROOF_GAP"
    assert result["human_authority"]["human_authority_authentication"].startswith("VERIFIED__")
    assert result["human_authority"]["human_authority_binding_readiness"].startswith("VERIFIED__")


def test_readiness_is_canonical_sealed_and_deterministic() -> None:
    module = load_reducer()
    raw = READINESS.read_bytes()
    envelope = json.loads(raw)
    readiness = envelope["readiness"]
    assert raw == module.canonical_bytes(envelope)
    assert envelope["readiness_sha256"] == hashlib.sha256(module.canonical_bytes(readiness)).hexdigest()
    assert readiness == module.build_readiness()


def test_existing_fm_serializer_projects_exact_nonpersisted_handoff() -> None:
    module = load_reducer()
    authenticated = module.authenticate_inputs()
    fm = module.load_fm()
    authorization = authenticated["authorization"]
    raw = fm.canonical_authority_handoff_bytes(authorization)
    envelope = fm.parse_authority_handoff_bytes(raw)
    assert set(authorization) == fm.authorization_fields(authorization)
    assert hashlib.sha256(raw).hexdigest() == module.PROJECTED_HANDOFF_SHA256
    assert envelope["authorization_sha256"] == module.PROJECTED_AUTHORIZATION_SHA256
    assert not (module.KN / "G77_256KN_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json").exists()


def test_human_source_exact_decision_and_binding_coordinates() -> None:
    module = load_reducer()
    raw = SOURCE.read_bytes()
    result = module.build_readiness()
    binding = result["binding_readiness"]
    assert len(raw) == 1213 and raw.count(b"\n") == 14
    assert hashlib.sha256(raw).hexdigest() == module.SOURCE_SHA256
    assert raw == module.exact_human_bytes()
    assert binding["authority_binding_generation"] == module.GENERATION
    assert binding["authority_binding_operation"] == module.OPERATION
    assert binding["authority_binding_source_sha256"] == module.SOURCE_SHA256
    assert binding["authority_binding_route"] == "FM_TO_ER_TO_P11"


def test_authentication_binding_and_consumption_are_separate() -> None:
    result = load_reducer().build_readiness()
    authority = result["human_authority"]
    assert authority["human_authority_authentication"].startswith("VERIFIED__")
    assert authority["human_authority_binding_readiness"].startswith("VERIFIED__")
    assert authority["human_authority_binding"].startswith("NOT_APPLICABLE__")
    assert authority["authority_present_in_repository"] is False
    assert authority["authority_consumption_count"] == 0


def test_zero_operation_e05_ex_and_architecture() -> None:
    result = load_reducer().build_readiness()
    assert len(result["operational_counters"]) == 15
    assert set(result["operational_counters"].values()) == {0}
    assert result["phase_b_started"] is False
    assert result["e05"]["state"] == result["e05"]["after"] == "VERIFIED__11_OF_18"
    assert result["e05"]["credit"] == result["e05"]["kn_e05_credit"] == "VERIFIED__0"
    assert result["ex"] == {"ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0"}
    architecture = result["architecture"]
    assert architecture["production_route_before"] == architecture["production_route_after"] == 1
    assert architecture["parallel_flow"] == "NO"
    assert set(value for key, value in architecture.items() if key.endswith("_count")) == {0}


def test_gn_exact_ten_fields_and_cross_vector_reuse() -> None:
    result = load_reducer().build_readiness()
    assert result["kn_coordinates"]["gn_exact_preauthorization_field_count"] == 10
    assert result["kn_coordinates"]["gn_exact_preauthorization_schema"] == "VERIFIED__UNCHANGED"
    reuse = result["cross_vector_reuse_assessment"]
    assert reuse["cross_vector_reuse_scope"] == "MULTI_VECTOR_REUSABLE"
    assert reuse["applicable_vectors"] == ["EXPIRED", "FUTURE", "WRONG_ATTEMPT", "WRONG_CONTRACT", "WRONG_INPUT", "WRONG_PROVENANCE"]


def test_python_ast_g48_and_exact_ria_structure() -> None:
    ast.parse(REDUCER.read_text(encoding="utf-8"))
    ast.parse(Path(__file__).read_text(encoding="utf-8"))
    report = REPORT.read_text(encoding="utf-8")
    assert re.findall(r"^# (.+)$", report, flags=re.MULTILINE) == [
        "1. Implementation Summary", "2. Code Evidence",
        "3. Constitutional Self-Assessment", "4. Validation Matrix",
        "5. Repository Mutation Summary", "6. Certification Verdict",
    ]
    assert re.findall(r"^[1-5]\. (.+\?)$", report, flags=re.MULTILINE) == [
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "Katere nove zmogljivosti (če sploh) nastanejo?",
        "Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "Ali implementacija ustvarja vzporedni tok?",
        "Ali zmanjšuje ali povečuje število produkcijskih poti?",
    ]
