from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path
import re
import sys


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
KW = Path(
    ".github/governance/evidence/"
    "g77_256kw_fresh_expired_operational_recommissioning_v1"
)
VERIFIER = KW / "analysis/G77_256KW_PHASE_A_SUCCESS_VERIFIER_V1.py"
REPORT = KW / "G77_256KW_G48_IMPLEMENTATION_REPORT_V1.md"
REDUCTION = KW / "G77_256KW_PREHUMAN_PHASE_A_REDUCTION_V1.json"


def load_verifier():
    specification = importlib.util.spec_from_file_location(
        "g77_256kw_phase_a_success_verifier", ROOT / VERIFIER
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


V = load_verifier()


def result() -> dict:
    return V.verify(V.HEAD, V.NESTED_HEAD)


def reduction() -> dict:
    return V.verify_seal(V.load_canonical(REDUCTION), "reduction")


def test_exact_kv_entry_nested_authority_and_historical_kn_source() -> None:
    entry = result()["entry"]
    assert entry["head"] == V.HEAD
    assert entry["tree"] == V.TREE
    assert entry["subject"] == V.SUBJECT
    assert entry["remote_equality"] == "VERIFIED__DIRECT_BRANCH_LS_REMOTE"
    assert entry["index_empty"] is True
    assert entry["historical_kn_source"] == "VERIFIED__UNCHANGED__NOT_KW_AUTHORITY"
    assert entry["nested_authority"]["clean"] is True
    assert entry["nested_authority"]["detached"] is True


def test_fresh_kw_candidate_context_request_and_presentations_are_distinct() -> None:
    phase_a = result()["phase_a"]
    assert phase_a["generation"] == V.GENERATION
    assert phase_a["operation"] == V.OPERATION
    assert phase_a["freshness_against_kn"] == "VERIFIED__ALL_REQUIRED_DIGESTS_DISTINCT"
    assert phase_a["candidate_sha256"] != "8af5ba1cbf9e396aa2f4f981a6f20b821c5fd1c38e091ed1cb3646c76c953b4a"
    assert phase_a["authorization_presentation_sha256"] != phase_a["human_decision_presentation_sha256"]


def test_current_head_coordinates_are_exact_everywhere() -> None:
    phase_a = result()["phase_a"]
    assert {
        phase_a["authorization_base_head"],
        phase_a["operation_context_head"],
        phase_a["presentation_head"],
    } == {V.HEAD}
    assert {
        phase_a["authorization_base_tree"],
        phase_a["operation_context_tree"],
        phase_a["presentation_tree"],
    } == {V.TREE}


def test_hp_hx_ic_jh_successful_lifecycle_precedents_are_reauthenticated() -> None:
    precedents = result()["successful_precedents"]
    assert precedents == {
        "hp_hx_ic": "VERIFIED__AUTHORITY_PRECONSUMPTION_EXECUTION_HEAD_EQUALITY",
        "jh": "VERIFIED__CONTEXT_REQUEST_AUTHORITY_AND_ADMISSION_HEAD_TREE_EQUALITY",
        "authority_rebinding": "VERIFIED__ABSENT",
    }


def test_gn_schema_is_exact_and_candidate_is_du_valid() -> None:
    phase_a = result()["phase_a"]
    assert phase_a["gn_exact_preauthorization_field_count"] == 10
    candidate = V.load_canonical(V.CANDIDATE_SOURCE)
    assert candidate["manifest"]["required_head"] == V.HEAD
    assert candidate["manifest"]["source_tree"] == V.TREE
    assert candidate["manifest_sha256"] == V.sha256_bytes(
        V.canonical_bytes(candidate["manifest"])
    )


def test_human_barrier_and_all_operational_counters_are_exact() -> None:
    phase_a = result()["phase_a"]
    assert phase_a["terminal"] == V.TERMINAL
    assert phase_a["human_decision_presentation_status"] == (
        "VERIFIED__READY_FOR_HUMAN_DECISION"
    )
    assert phase_a["human_authority_status"] == (
        "NOT_PROVEN__NO_FRESH_KW_HUMAN_ACT_YET"
    )
    assert phase_a["human_authority_handoff_status"].startswith("NOT_APPLICABLE__")
    assert phase_a["preconsumption_binding_status"].startswith("NOT_APPLICABLE__")
    assert not any(phase_a["operational_counters"].values())


def test_e05_ex_classification_and_architecture_remain_bounded() -> None:
    phase_a = result()["phase_a"]
    value = reduction()
    assert phase_a["e05"] == {
        "before": "VERIFIED__11_OF_18",
        "credit": "VERIFIED__0",
        "current": "VERIFIED__11_OF_18",
        "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
        "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
    }
    assert phase_a["ex"] == {
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
    }
    assert value["failure_novelty_and_convergence_check"]["failure_class"] == (
        "EVIDENCE_OR_REPORTING_DEFECT"
    )
    assert value["failure_novelty_and_convergence_check"]["new_capability_required"] == (
        "VERIFIED__NO"
    )
    assert value["architecture"] == {
        "production_mutation_count": 0,
        "p11_implementation_mutation_count": 0,
        "new_owner_count": 0,
        "new_route_count": 0,
        "new_registry_count": 0,
        "new_generic_abstraction_count": 0,
        "new_constitutional_concept_count": 0,
        "production_route_before": 1,
        "production_route_after": 1,
        "parallel_flow": "NO",
    }


def test_materializer_has_no_phase_b_or_operational_entrypoint() -> None:
    source = (ROOT / V.MATERIALIZER).read_text(encoding="utf-8")
    ast.parse(source)
    assert "fresh=True" in source
    assert "PHASE_B_CONTROLLER" not in source
    assert "run_phase_b" not in source
    assert "subprocess.Popen" not in source
    assert "qemu-system" not in source


def test_all_kw_json_is_canonical_and_sealed() -> None:
    observed = result()["canonical_artifacts"]
    assert observed["canonical_json_count"] == 20
    assert observed["verified_inner_seal_count"] >= 14


def test_g48_has_exact_six_h1_and_five_required_ria_questions() -> None:
    report = (ROOT / REPORT).read_text(encoding="utf-8")
    assert re.findall(r"^# .+$", report, flags=re.MULTILINE) == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    assert re.findall(r"^\d+\. .+\?$", report, flags=re.MULTILINE) == [
        "1. Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "2. Katere nove zmogljivosti (če sploh) nastanejo?",
        "3. Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "4. Ali implementacija ustvarja vzporedni tok?",
        "5. Ali zmanjšuje ali povečuje število produkcijskih poti?",
    ]
