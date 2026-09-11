from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path
import re
import sys


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
KN = Path(
    ".github/governance/evidence/"
    "g77_256kn_fresh_expired_operational_recommissioning_v1"
)
VERIFIER = KN / "analysis/G77_256KN_PHASE_A_SUCCESS_VERIFIER_V1.py"
REPORT = KN / "G77_256KN_G48_IMPLEMENTATION_REPORT_V1.md"
REDUCTION = KN / "G77_256KN_PREHUMAN_PHASE_A_REDUCTION_V1.json"


def load_verifier():
    specification = importlib.util.spec_from_file_location(
        "g77_256kn_phase_a_success_verifier", ROOT / VERIFIER
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
    envelope = V.load_canonical(V.REDUCTION)
    return V.verify_seal(envelope, "reduction")


def test_complete_phase_a_verifier_passes_without_reexecution() -> None:
    observed = result()
    assert observed["entry"]["head"] == V.HEAD
    assert observed["entry"]["tree"] == V.TREE
    assert observed["entry"]["remote_equality"] == "VERIFIED__DIRECT_BRANCH_LS_REMOTE"
    assert observed["phase_a"]["terminal"] == V.TERMINAL
    assert observed["ex"]["ex_reused"] == "VERIFIED__17_OF_17"
    assert observed["ex"]["ex_reconstructed"] == "VERIFIED__0"


def test_fresh_kn_coordinates_and_human_barrier_are_exact() -> None:
    phase_a = result()["phase_a"]
    assert phase_a["generation"] == V.GENERATION
    assert phase_a["operation"] == V.OPERATION
    assert phase_a["freshness_against_kl"].startswith("VERIFIED__ALL_")
    assert phase_a["phase_a_construction_attempt_count"].startswith("VERIFIED__1__")
    assert phase_a["human_authority_present"] is False
    assert phase_a["phase_b_started"] is False
    assert phase_a["operational_execution"] is False
    assert phase_a["human_decision_presentation_sha256"] == V.sha256_path(
        V.HUMAN_PRESENTATION
    )


def test_gn_exact_schema_and_km_binding_are_preserved() -> None:
    phase_a = result()["phase_a"]
    assert phase_a["gn_exact_preauthorization_field_count"] == 10
    assert set(phase_a["gn_exact_preauthorization_fields"]) == V.GN_FIELDS
    assert phase_a["gn_unknown_and_missing_field_rejection"] == (
        "VERIFIED__SEALED_REQUEST_PREAUTHORIZATION_INVALID"
    )
    assert phase_a["ki_preflight_binding"] == (
        "VERIFIED__KM_SCHEMA_PRESERVING_PATH_USED"
    )
    assert phase_a["km_authentication"]["gn_validation_weakened"] == "VERIFIED__NO"
    assert phase_a["km_authentication"]["second_accepted_gn_schema"] == "VERIFIED__NO"
    assert phase_a["km_authentication"]["fallback"] == "VERIFIED__ABSENT"
    assert phase_a["km_authentication"]["alias"] == "VERIFIED__ABSENT"


def test_cross_vector_reuse_is_bounded_and_not_operational_proof() -> None:
    cross_vector = result()["phase_a"]["cross_vector_reuse_assessment"]
    assert cross_vector["cross_vector_reuse_scope"] == "VERIFIED__MULTI_VECTOR_REUSABLE"
    assert cross_vector["applicable_vectors"] == [
        "EXPIRED",
        "FUTURE",
        "WRONG_ATTEMPT",
        "WRONG_CONTRACT",
        "WRONG_INPUT",
        "WRONG_PROVENANCE",
    ]
    assert cross_vector["common_proof_reuse_is_vector_operational_proof"] is False
    assert cross_vector["multi_vector_reuse_is_authority_transfer"] is False


def test_reduction_preserves_e05_frontier_architecture_and_zero_counters() -> None:
    value = reduction()
    assert value["terminal"] == V.TERMINAL
    assert value["e05"] == {
        "before": "VERIFIED__11_OF_18",
        "credit": "VERIFIED__0",
        "current": "VERIFIED__11_OF_18",
        "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
        "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
    }
    assert not any(value["operational_counters"].values())
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
    assert value["fresh_kn_phase_a_presentation_ready"] == "VERIFIED"
    assert value["safe_stop_checkpoint"] == "VERIFIED"
    assert value["human_authority_present"] is False
    assert value["phase_b_started"] is False
    assert value["auto_continuable"] is False
    assert value["human_review_required"] is True


def test_materializer_is_phase_a_only_and_fresh_collision_guarded() -> None:
    source = (ROOT / V.MATERIALIZER).read_text(encoding="utf-8")
    ast.parse(source)
    assert "fresh=True" in source
    assert "P.E.materialize_human_decision_presentation()" in source
    assert "PHASE_B_CONTROLLER" not in source
    assert "run_phase_b" not in source
    assert "subprocess.Popen" not in source
    assert "qemu-system" not in source


def test_all_kn_json_is_canonical_and_top_level_inner_seals_match() -> None:
    checked = 0
    sealed = 0
    for path in (ROOT / KN).rglob("*.json"):
        raw = path.read_bytes()
        value = json.loads(raw)
        assert raw == V.canonical_bytes(value), path
        checked += 1
        for inner in ("request", "checkpoint", "proof", "reduction", "observation"):
            seal_name = f"{inner}_sha256"
            if isinstance(value.get(inner), dict) and seal_name in value:
                assert value[seal_name] == V.sha256_bytes(
                    V.canonical_bytes(value[inner])
                ), path
                sealed += 1
    assert checked == 19
    assert sealed >= 10


def test_g48_has_exactly_six_h1_and_exactly_five_ria_questions() -> None:
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
