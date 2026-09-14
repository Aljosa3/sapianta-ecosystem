"""Focused G77-256LI authority-free current-checkout readiness proof."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[5]
LI = ROOT / (
    ".github/governance/evidence/"
    "g77_256li_wrong_scope_current_checkout_binding_v1"
)
VERIFIER = LI / "analysis/G77_256LI_PHASE_A_STATIC_READINESS_VERIFIER_V1.py"
SPEC = importlib.util.spec_from_file_location("g77_256li_verifier", VERIFIER)
assert SPEC is not None and SPEC.loader is not None
V = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = V
SPEC.loader.exec_module(V)


def reduction() -> dict:
    envelope = V.load_canonical(V.LI_REDUCTION)
    value = envelope["reduction"]
    assert envelope["reduction_sha256"] == V.sha256_bytes(V.canonical_bytes(value))
    return value


def test_lh_failure_is_authenticated_without_rewriting_history() -> None:
    failure = V.authenticate_lh_failure()
    assert failure["failure_class"] == "IMPLEMENTATION_REGRESSION"
    assert failure["differing_argument_indexes"] == [2, 3]
    assert failure["new_capability_required"] == "NO"
    assert V.LH_REDUCTION.read_bytes() == V.committed(V.LH_REDUCTION_REL)


def test_exact_minimum_dependency_closure_and_tuple() -> None:
    closure = V.authenticate_minimum_delta()
    assert closure["source_owner"] == "FM_CURRENT_BOOTSTRAP_ASSET_BINDINGS"
    assert closure["seal_dependencies"] == []
    assert closure["bootstrap_tuple"][2:4] == [V.ENTRY_HEAD, V.ENTRY_TREE]
    assert V.STALE_HEAD not in V.LI_CLOUD.read_text(encoding="utf-8")
    assert V.STALE_TREE not in V.LI_CLOUD.read_text(encoding="utf-8")


def test_lg_lh_p11_er_are_immutable_and_no_unrelated_mutation_exists() -> None:
    V.authenticate_entry()
    assert V.sha256(V.P11) == V.P11_SHA256
    assert V.sha256(V.ER) == V.ER_SHA256
    changed = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT,
        text=True,
    ).splitlines()
    assert all(
        line[3:] == V.FM_REL.as_posix()
        or line[3:].startswith(V.LI_REL.as_posix() + "/")
        for line in changed
    )


def test_seed_is_exact_three_member_projection() -> None:
    result = V.authenticate_seed_projection()
    assert result["seed_sha256"] == V.LI_SEED_SHA256
    assert result["projection"] == "VERIFIED__EXACT_THREE_MEMBERS"


def test_complete_authority_free_phase_a_static_readiness(tmp_path: Path) -> None:
    phase = V.authenticate_phase_a(tmp_path)
    assert phase["result"] == "COMPLETE_PHASE_A_STATIC_READINESS__VERIFIED"
    assert phase["repository_head"] == V.ENTRY_HEAD
    assert phase["repository_tree"] == V.ENTRY_TREE
    assert phase["vector"] == "WRONG_SCOPE"
    counters = {key: value for key, value in phase.items() if key.endswith("_count")}
    assert counters and set(counters.values()) == {0}


def test_cross_vector_reuse_is_explicit_and_does_not_transfer_credit() -> None:
    value = reduction()
    vectors = value["cross_vector_reuse_assessment"]
    assert [item["vector"] for item in vectors] == [
        "WRONG_SCOPE", "WRONG_CALLER", "WRONG_ATTEMPT", "WRONG_INPUT",
        "WRONG_CONTRACT", "WRONG_PROVENANCE", "FUTURE", "EXPIRED",
    ]
    required = {
        "current_e05_status", "common_infrastructure_reusable",
        "static_proof_reusable", "phase_a_structure_reusable",
        "fresh_bindings_required", "authority_flow_mechanics_reusable",
        "fresh_human_authority_required_later", "fm_reusable", "gn_reusable",
        "er_reusable", "p11_reusable", "ex_reusable",
        "vector_specific_proof_required", "known_vector_specific_defect",
        "requires_new_production_capability",
    }
    assert all(required <= set(item) for item in vectors)
    assert value["e05"] == {"after": "12/18", "before": "12/18", "credit": 0}
    assert set(value["operational_counters"].values()) == {0}


def test_architecture_ex_and_terminal_are_bounded() -> None:
    value = reduction()
    architecture = value["architecture"]
    assert architecture["p11_mutation"] == 0
    assert architecture["er_mutation"] == 0
    assert architecture["ex_mutation"] == 0
    assert architecture["new_owner"] == 0
    assert architecture["new_route"] == 0
    assert architecture["production_route_count_before"] == 1
    assert architecture["production_route_count_after"] == 1
    assert value["ex"] == {
        "historical_validator_status": (
            "FAIL_CLOSED__COMPONENT_HASH_MISMATCH__ER_OPERATIONAL_HARNESS__"
            "HISTORICALLY_VERSION_BOUND"
        ),
        "reconstructed": "VERIFIED__0",
        "reused": "VERIFIED__17_OF_17",
    }
    assert value["terminal"] == V.TERMINAL


def test_g48_report_has_exact_six_h1_and_reuse_questions() -> None:
    V.authenticate_evidence()
    report = V.LI_REPORT.read_text(encoding="utf-8")
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    for index, question in enumerate(
        (
            "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
            "Katere nove zmogljivosti (če sploh) nastanejo?",
            "Ali katera obstoječa zmogljivost postane nedosegljiva?",
            "Ali implementacija ustvarja vzporedni tok?",
            "Ali zmanjšuje ali povečuje število produkcijskih poti?",
        ),
        1,
    ):
        assert report.count(f"{index}. {question}") == 1
    assert report.rstrip().endswith(V.TERMINAL)


def test_full_verifier_reaches_only_human_decision_boundary(tmp_path: Path) -> None:
    result = V.verify(tmp_path)
    assert result["terminal"] == V.TERMINAL
    assert result["phase_a"]["result"] == (
        "COMPLETE_PHASE_A_STATIC_READINESS__VERIFIED"
    )
    assert result["e05"]["after"] == "12/18"
    assert result["e05"]["credit"] == 0
