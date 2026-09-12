from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
import re
import sys


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
KY = Path(
    ".github/governance/evidence/"
    "g77_256ky_fresh_expired_operational_recommissioning_v1"
)
VERIFIER = KY / "analysis/G77_256KY_PHASE_A_SUCCESS_VERIFIER_V1.py"
REPORT = KY / "G77_256KY_G48_IMPLEMENTATION_REPORT_V1.md"
REDUCTION = KY / "G77_256KY_PREHUMAN_PHASE_A_REDUCTION_V1.json"


def load_verifier():
    specification = importlib.util.spec_from_file_location(
        "g77_256ky_phase_a_success_verifier", ROOT / VERIFIER
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
    return V.A.verify_seal(V.A.load_canonical(REDUCTION), "reduction")


def test_exact_kx_entry_and_nested_authority() -> None:
    entry = result()["entry"]
    assert entry["head"] == V.HEAD
    assert entry["tree"] == V.TREE
    assert entry["subject"] == V.SUBJECT
    assert entry["remote_equality"] == "VERIFIED__DIRECT_BRANCH_LS_REMOTE"
    assert entry["index_empty"] is True
    assert entry["nested_authority"]["clean"] is True
    assert entry["nested_authority"]["detached"] is True


def test_fresh_ky_identity_and_current_head_bindings() -> None:
    phase = result()["phase_a"]
    assert phase["commission"] == V.COMMISSION
    assert phase["generation"] == V.GENERATION
    assert phase["operation"] == V.OPERATION
    assert phase["vector"] == "EXPIRED"
    assert phase["freshness_against_kw"].startswith("VERIFIED__")
    assert {
        phase["authorization_base_head"],
        phase["operation_context_head"],
        phase["presentation_head"],
    } == {V.HEAD}
    assert {
        phase["authorization_base_tree"],
        phase["operation_context_tree"],
        phase["presentation_tree"],
    } == {V.TREE}


def test_kx_and_kw_are_authenticated_without_authority_reuse() -> None:
    value = reduction()
    kx = value["kx_repair_authentication"]
    assert kx["terminal"].startswith("A__KX_EXISTING_FM_RUNTIME_EXPORT")
    assert kx["kw_terminal"].startswith("I__KW_PROVIDER_RECOVERY")
    assert kx["kw_authority"].endswith("NONREUSABLE__NONTRANSFERABLE")
    assert kx["kw_authority_consumption_count"] == 1
    assert kx["kw_operation_attempt_count"] == 1
    assert kx["kw_retry_count"] == kx["kw_repair_retry_count"] == kx["kw_replay_count"] == 0


def test_frontier_is_proof_gap_and_not_a_new_capability() -> None:
    check = reduction()["failure_novelty_and_convergence_check"]
    assert check["failure_class"] == "PROOF_GAP"
    assert check["new_capability_required"] == "VERIFIED__NO"
    assert "POST_KX_OPERATIONAL_OBSERVATION" in check["new_proof_required"]


def test_human_barrier_and_all_fifteen_counters_are_zero() -> None:
    phase = result()["phase_a"]
    assert phase["terminal"] == V.TERMINAL
    assert phase["human_decision_presentation_status"] == "VERIFIED__READY_FOR_HUMAN_DECISION"
    assert phase["human_authority_status"] == "NOT_PROVEN__NO_FRESH_KY_HUMAN_ACT_YET"
    assert len(phase["operational_counters"]) == 15
    assert not any(phase["operational_counters"].values())


def test_e05_ex_and_architecture_remain_bounded() -> None:
    phase = result()["phase_a"]
    value = reduction()
    assert phase["e05"] == {
        "before": "VERIFIED__11_OF_18",
        "credit": "VERIFIED__0",
        "current": "VERIFIED__11_OF_18",
        "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
        "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
    }
    assert phase["ex"] == {
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
    }
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


def test_exact_human_decision_presentation_and_digests() -> None:
    phase = result()["phase_a"]
    text = (ROOT / V.HUMAN_PRESENTATION).read_text(encoding="utf-8")
    assert f"PURPOSE {V.PURPOSE}\n" in text
    assert f"CANDIDATE_SHA256 {phase['candidate_sha256']}\n" in text
    assert f"REQUEST_IDENTITY_SHA256 {phase['request_sha256']}\n" in text
    assert "REPAIR_RETRY_LIMIT 0\n" in text
    assert "STOP AT THE HUMAN DECISION BARRIER.\n" in text


def test_no_phase_b_or_operational_entrypoint_or_artifact() -> None:
    source = (ROOT / V.MATERIALIZER).read_text(encoding="utf-8")
    tree = ast.parse(source)
    names = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
    assert "Popen" not in names
    assert "run_phase_b" not in source
    assert "PHASE_B_CONTROLLER" not in source


def test_all_ky_json_is_canonical_and_sealed() -> None:
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
