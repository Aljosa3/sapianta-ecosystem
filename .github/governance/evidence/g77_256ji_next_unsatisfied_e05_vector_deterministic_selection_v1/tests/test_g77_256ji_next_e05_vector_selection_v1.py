#!/usr/bin/env python3
"""Focused repository-only validation for G77-256JI."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[5]
JI_ROOT = ROOT / (
    ".github/governance/evidence/"
    "g77_256ji_next_unsatisfied_e05_vector_deterministic_selection_v1"
)
FORMALIZER = JI_ROOT / "analysis/G77_256JI_NEXT_E05_VECTOR_SELECTION_FORMALIZER_V1.py"
REDUCTION = JI_ROOT / "G77_256JI_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = JI_ROOT / "G77_256JI_G48_IMPLEMENTATION_REPORT_V1.md"
EXPECTED_FILES = {
    "G77_256JI_G48_IMPLEMENTATION_REPORT_V1.md",
    "G77_256JI_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json",
    "analysis/G77_256JI_NEXT_E05_VECTOR_SELECTION_FORMALIZER_V1.py",
    "tests/test_g77_256ji_next_e05_vector_selection_v1.py",
}
REMAINING = {
    "AMBIGUOUS", "STALE", "EXPIRED", "REVOKED", "SUPERSEDED",
    "WRONG_SCOPE", "COHERENT_COPY",
}
TWENTY_DIMENSIONS = {
    "A_existing_semantic_support", "B_existing_validator_support",
    "C_fm_gn_gl_route_compatibility", "D_du_eb_ee_v2_compatibility",
    "E_p11_rejection_semantics", "F_deterministic_evidence_primitives",
    "G_ex_proof_reuse", "H_required_production_mutation",
    "I_required_p11_mutation", "J_required_route_mutation",
    "K_required_new_registry_broker_dispatcher",
    "L_required_new_authority_semantics", "M_expected_human_authorization",
    "N_expected_qemu_vm_commissioning", "O_proof_complexity",
    "P_architectural_novelty", "Q_parallel_flow_risk",
    "R_historical_evidence_reuse", "S_fail_closed_determinism",
    "T_expected_constitutional_frontier_reduction",
}


def load_module(path: Path, name: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


JI = load_module(FORMALIZER, "g77_256ji_formalizer")


def unique_json(path: Path) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            assert key not in result
            result[key] = value
        return result

    result = json.loads(path.read_bytes(), object_pairs_hook=unique)
    assert isinstance(result, dict)
    return result


def reduction() -> dict[str, Any]:
    return unique_json(REDUCTION)["reduction"]


def test_authenticated_entry_and_pinned_nested_authority() -> None:
    result = JI.authenticate_entry(ROOT)
    assert result["branch"] == JI.ENTRY_BRANCH
    assert result["head"] == JI.ENTRY_HEAD
    assert result["tree"] == JI.ENTRY_TREE
    assert result["subject"] == JI.ENTRY_SUBJECT
    assert result["remote_tracking_head"] == JI.ENTRY_HEAD
    assert result["index"] == "VERIFIED__EMPTY"
    assert result["nested_authority"] == {
        "clean": True,
        "detached": True,
        "head": JI.NESTED_HEAD,
        "tree": JI.NESTED_TREE,
        "tag": JI.NESTED_TAG,
        "origin": "git@github.com:Aljosa3/sapianta-core.git",
    }


def test_exact_four_file_bounded_namespace() -> None:
    observed = {
        str(path.relative_to(JI_ROOT))
        for path in JI_ROOT.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }
    assert observed == EXPECTED_FILES
    assert subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True
    ).strip() == ""


def test_reduction_is_canonical_unique_key_and_inner_sealed() -> None:
    envelope = unique_json(REDUCTION)
    assert REDUCTION.read_bytes() == JI.canonical_bytes(envelope) + b"\n"
    assert envelope["schema_id"] == (
        "G77_256JI_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1"
    )
    assert envelope["reduction_sha256"] == hashlib.sha256(
        JI.canonical_bytes(envelope["reduction"]) + b"\n"
    ).hexdigest()
    rebuilt = JI.envelope(JI.build_reduction(ROOT))
    assert rebuilt == envelope


def test_all_committed_sources_are_hash_bound() -> None:
    assert JI.authenticate_sources(ROOT) == reduction()["sources"]
    assert len(reduction()["sources"]) == 10


def test_jh_terminal_and_consumed_authority_reconstruct_exactly() -> None:
    jh = reduction()["jh_terminal_reconstruction"]
    assert jh["terminal"] == (
        "A__FUTURE_FRESH_HUMAN_AUTHORIZED_OPERATIONAL_DENIAL_BEFORE_P11_ENTRY_VERIFIED"
    )
    assert jh["authority_state"] == "VERIFIED__CONSUMED_NONREUSABLE"
    assert jh["human_authorization_count"] == "VERIFIED__1"
    assert jh["authority_consumption_count"] == "VERIFIED__1"
    assert jh["historical_authority_reusable_by_ji"] == "VERIFIED__NO"
    assert jh["denial_reason"] == "VERIFIED__operational Human act is not current"
    assert jh["e05_before"] == "VERIFIED__10_OF_18"
    assert jh["e05_after"] == "VERIFIED__11_OF_18"
    assert jh["e05_credit"] == "VERIFIED__1"
    assert jh["future_operational_status"] == "VERIFIED__DENIED_BEFORE_P11_ENTRY"
    counters = jh["operational_counters"]
    for name in (
        "human_authorization_count", "authority_consumption_count",
        "pre_operational_count", "fm_operational_invocation_count", "qemu_count",
        "vm_count", "operation_attempt_count", "request_count", "future_denial_count",
    ):
        assert counters[name] == "VERIFIED__1"
    for name in (
        "p11_entry_count", "protected_invocation_count", "protected_effect_count",
        "retry_count", "repair_retry_count", "replay_count",
    ):
        assert counters[name] == "VERIFIED__0"


def test_e05_ledger_reconstructs_exactly_seven_unsatisfied_vectors() -> None:
    e05 = reduction()["e05"]
    assert e05["before"] == e05["after"] == "VERIFIED__11_OF_18"
    assert e05["credit"] == "VERIFIED__0"
    assert e05["required"] == 18
    assert e05["satisfied_before"] == 11
    assert e05["remaining_before"] == 7
    assert set(e05["remaining_set"]) == REMAINING
    assert set(e05["required_set"]) - set(e05["satisfied_set"]) == REMAINING
    assert "FUTURE" in e05["satisfied_set"] and "FUTURE" not in REMAINING


def test_all_seven_candidates_have_twenty_dimensions_and_unique_winner() -> None:
    candidates = reduction()["candidate_comparison"]
    assert len(candidates) == 7
    assert {row["vector"] for row in candidates} == REMAINING
    for row in candidates:
        assert TWENTY_DIMENSIONS <= set(row)
        assert row["G_ex_proof_reuse"] == "VERIFIED__17_OF_17"
        assert row["H_required_production_mutation"] == "VERIFIED__0"
        assert set(row["minimum_delta_counts"]) == {
            "production_mutation_count", "p11_mutation_count",
            "route_mutation_count", "new_registry_count", "new_dispatcher_count",
            "new_generic_adapter_count", "new_authority_semantics_count",
            "parallel_flow_count", "duplicated_constitutional_logic_count",
        }
    ranks = [row["selection_rank"] for row in candidates]
    assert sorted(ranks) == list(range(1, 8))
    winner = next(row for row in candidates if row["selection_rank"] == 1)
    assert winner["vector"] == "EXPIRED"
    selection = reduction()["selection"]
    assert selection["selected_vector"] == "EXPIRED"
    assert selection["selection_status"] == "VERIFIED__UNIQUE_MINIMUM_GOVERNED_DELTA"
    assert selection["selected_vector_operational_status"] == "NOT_PROVEN_OPERATIONALLY"
    assert selection["tie_count"] == "VERIFIED__0"
    assert selection["exact_owner_candidate_set"] == [
        "EXPIRED", "WRONG_SCOPE", "REVOKED", "SUPERSEDED", "STALE"
    ]
    assert selection["post_id_adjacent_asset_candidate_set"] == ["EXPIRED"]
    assert selection["deterministic_selection_rule"].startswith(
        "VERIFIED__FILTER_EXACT_P11_VECTOR_OWNER"
    )


def test_expired_reuses_exact_existing_p11_and_future_temporal_primitives() -> None:
    result = JI.authenticate_repository_semantics(ROOT)
    assert result["expired_owner"] == "VERIFIED__P11_AVAILABLE_TO_EXPIRED_AT_PRECLAIM"
    assert result["expired_denial"] == "VERIFIED__BEFORE_PRECLAIM_LEDGER_APPEND"
    assert result["future_temporal_primitives"].startswith("VERIFIED__FIXED_INTERVAL")
    candidates = reduction()["candidate_comparison"]
    expired = next(row for row in candidates if row["vector"] == "EXPIRED")
    assert expired["I_required_p11_mutation"] == "VERIFIED__0__EXACT_OWNER_EXISTS"
    assert expired["L_required_new_authority_semantics"].startswith("VERIFIED__0")
    assert all(row["selection_rank"] > 1 for row in candidates if row is not expired)


def test_ex_is_reused_without_reconstruction() -> None:
    ex_path = ROOT / (
        ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
        "validator/G77_256EX_COMMON_SUBSTRATE_CERTIFICATION_VALIDATOR_V1.py"
    )
    ex = load_module(ex_path, "g77_256ex_validator_for_ji")
    result = ex.validate(
        ROOT / (
            ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
            "G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"
        )
    )
    assert result["regression_total"] == result["regression_pass"] == 12
    assert result["regression_fail"] == 0
    assert reduction()["reuse"]["ex_reused"] == "VERIFIED__17_OF_17"
    assert reduction()["reuse"]["ex_reconstructed"] == "VERIFIED__0"


def test_ji_firewall_reuse_and_overengineering_counters() -> None:
    value = reduction()
    assert set(value["operational_counters"].values()) == {"VERIFIED__0"}
    assert set(value["mutation_counters"].values()) == {"VERIFIED__0"}
    assert set(value["overengineering"].values()) == {"VERIFIED__0"}
    reuse = value["reuse"]
    assert reuse["production_route_before"] == reuse["production_route_after"] == "VERIFIED__1"
    assert reuse["production_route_delta"] == "VERIFIED__0"
    assert reuse["parallel_flow_created"] == "VERIFIED__NO"
    assert reuse["unreachable_preexisting_capability_set"] == "VERIFIED__EMPTY"
    assert value["terminal_control"]["auto_continuable"] is False
    assert value["terminal_control"]["human_review_required"] is True
    assert value["terminal_control"]["selected_vector_implemented"] is False


def test_ccwim_and_required_metrics_are_complete_and_truthfully_classified() -> None:
    value = reduction()
    required_metrics = {
        "project_progress", "project_progress_estimate",
        "informal_project_progress_estimate", "constitutional_health_evidence",
        "shadow_automation_status", "constitutional_frontier_distance",
        "constitutional_frontier_distanc_e", "e05_frontier_distance",
        "selected_e05_local_frontier_distance", "last_verified_edge",
        "first_broken_edge", "blocking_owner", "minimum_missing_capability",
        "minimum_legal_next_delta", "governance_efficience",
        "architectural_governance_efficience", "proof_reuse_efficiency",
        "cognition_assisted_handoff", "aigol_codex_work_share",
        "overengineering_risk", "proof_process_overhead_risk",
        "cognition_provenance", "candidate_capability", "shadow_design_target",
        "constitutional_continuation_progress", "prompt_context_reuse_ratio",
        "repository_derived_execution_context_ratio",
        "constitutional_prompt_externalization_ratio", "token_benchmark",
        "llm_cost_reduction_ratio", "lcrr", "ex_reused", "ex_reconstructed",
    }
    assert required_metrics <= set(value["metrics"])
    assert value["metrics"]["project_progress_estimate"] == (
        "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR"
    )
    for metric in (
        "aigol_codex_work_share", "token_benchmark", "llm_cost_reduction_ratio", "lcrr"
    ):
        assert value["metrics"][metric] == "NOT_MEASURED"
    required_ccwim = {
        "ccwim_maturity_level", "cross_worker_state_recovery_level",
        "repository_derived_context_ratio", "human_handoff_information_required",
        "previous_worker_conversation_required", "previous_worker_identity_required",
        "previous_worker_memory_required", "authenticated_repository_continuation",
        "inter_generation_cross_worker_continuation",
        "intra_generation_cross_worker_continuation", "uncommitted_delta_recovery",
        "authority_state_recovery", "consumed_authority_recovery",
        "post_operation_state_recovery", "operation_replay_prevention",
        "cross_worker_constitutional_drift",
        "observed_artifact_level_cross_worker_drift", "handoff_sufficiency_status",
        "handoff_state_completeness", "handoff_reconstruction_required",
        "handoff_reconstruction_success", "handoff_ambiguity_count",
        "unauthenticated_handoff_assumption_count",
    }
    assert required_ccwim == set(value["ccwim"])
    assert value["ccwim"]["inter_generation_cross_worker_continuation"] == "VERIFIED__JH_TO_JI"
    assert value["ccwim"]["intra_generation_cross_worker_continuation"].startswith("NOT_APPLICABLE")


def test_formalizer_has_no_operational_entrypoint() -> None:
    source = FORMALIZER.read_text(encoding="utf-8")
    tree = ast.parse(source)
    called_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert not ({"submit_human_act", "claim_and_invoke_once", "execv", "Popen"} & called_names)
    assert "qemu-system" not in source
    assert "HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST" not in source


def test_g48_report_has_exactly_six_h1_sections_and_terminal_last() -> None:
    report = REPORT.read_text(encoding="utf-8")
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]
    assert "Constitutional Continuity & Worker Independence Metrics — CCWIM" in report
    for question in (
        "1. Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "2. Katere nove zmogljivosti (če sploh) nastanejo?",
        "3. Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "4. Ali implementacija ustvarja vzporedni tok?",
        "5. Ali zmanjšuje ali povečuje število produkcijskih poti?",
    ):
        assert question in report
    assert report.rstrip().endswith(JI.TERMINAL)
