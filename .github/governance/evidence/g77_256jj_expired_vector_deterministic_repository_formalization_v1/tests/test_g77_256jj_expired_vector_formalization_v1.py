#!/usr/bin/env python3
"""Focused deterministic repository-only validation for G77-256JJ."""

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
JJ_ROOT = ROOT / (
    ".github/governance/evidence/"
    "g77_256jj_expired_vector_deterministic_repository_formalization_v1"
)
FORMALIZER = JJ_ROOT / "analysis/G77_256JJ_EXPIRED_VECTOR_FORMALIZER_V1.py"
REDUCTION = JJ_ROOT / "G77_256JJ_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = JJ_ROOT / "G77_256JJ_G48_IMPLEMENTATION_REPORT_V1.md"
EXPECTED_FILES = {
    "G77_256JJ_G48_IMPLEMENTATION_REPORT_V1.md",
    "G77_256JJ_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json",
    "analysis/G77_256JJ_EXPIRED_VECTOR_FORMALIZER_V1.py",
    "tests/test_g77_256jj_expired_vector_formalization_v1.py",
}


def load_module(path: Path, name: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


JJ = load_module(FORMALIZER, "g77_256jj_formalizer")


def unique_json(path: Path) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            assert key not in result
            result[key] = value
        return result

    value = json.loads(path.read_bytes(), object_pairs_hook=unique)
    assert isinstance(value, dict)
    return value


def reduction() -> dict[str, Any]:
    return unique_json(REDUCTION)["reduction"]


def test_authenticated_entry_remote_tracking_and_nested_authority() -> None:
    result = JJ.authenticate_entry(ROOT)
    assert result["branch"] == JJ.ENTRY_BRANCH
    assert result["head"] == result["remote_tracking_head"] == JJ.ENTRY_HEAD
    assert result["tree"] == JJ.ENTRY_TREE
    assert result["subject"] == JJ.ENTRY_SUBJECT
    assert result["entry_worktree"] == "VERIFIED__CLEAN_BEFORE_JJ_WRITE"
    assert result["index"] == "VERIFIED__EMPTY"
    assert result["nested_authority"] == {
        "clean": True,
        "detached": True,
        "head": JJ.NESTED_HEAD,
        "tree": JJ.NESTED_TREE,
        "tag": JJ.NESTED_TAG,
        "origin": "git@github.com:Aljosa3/sapianta-core.git",
    }


def test_exact_four_file_bounded_namespace_and_empty_index() -> None:
    observed = {
        str(path.relative_to(JJ_ROOT))
        for path in JJ_ROOT.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }
    assert observed == EXPECTED_FILES
    assert subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True
    ).strip() == ""
    status = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=ROOT, text=True,
    )
    assert status
    assert all(line[3:].startswith(f"{JJ.NAMESPACE}/") for line in status.splitlines())


def test_reduction_is_canonical_unique_key_inner_sealed_and_rebuilds() -> None:
    value = unique_json(REDUCTION)
    assert REDUCTION.read_bytes() == JJ.canonical_bytes(value) + b"\n"
    assert value["schema_id"] == (
        "G77_256JJ_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1"
    )
    assert value["reduction_sha256"] == hashlib.sha256(
        JJ.canonical_bytes(value["reduction"]) + b"\n"
    ).hexdigest()
    assert JJ.envelope(JJ.build_reduction(ROOT)) == value


def test_all_sources_are_hash_bound_and_committed_at_entry() -> None:
    authenticated = JJ.authenticate_sources(ROOT)
    assert authenticated == reduction()["sources"]
    assert len(authenticated) == 18
    assert all(item["path"] not in EXPECTED_FILES for item in authenticated)


def test_committed_ji_selection_reconstructs_exactly() -> None:
    value = JJ.reconstruct_ji(ROOT)
    assert value["terminal"] == "A__NEXT_UNSATISFIED_E05_VECTOR_DETERMINISTICALLY_SELECTED"
    assert value["selected_vector"] == "EXPIRED"
    assert value["selection_status"] == "VERIFIED__UNIQUE_MINIMUM_GOVERNED_DELTA"
    assert value["selected_vector_operational_status"] == "NOT_PROVEN_OPERATIONALLY"
    assert value["e05_before"] == value["e05_after"] == "VERIFIED__11_OF_18"
    assert value["e05_credit"] == "VERIFIED__0"
    assert value["ex_reused"] == "VERIFIED__17_OF_17"
    assert value["ex_reconstructed"] == "VERIFIED__0"
    assert value["artifact_set"] == "VERIFIED__FOUR_COMMITTED_HASH_BOUND_ARTIFACTS"


def test_minimum_expired_mutation_and_dependent_recomputations() -> None:
    model = JJ.formalize_expired_vector()
    baseline = model["baseline_state"]
    mutated = model["mutated_state"]
    assert (baseline["valid_from_unix_ns"], baseline["preclaim_time_unix_ns"], baseline["valid_until_unix_ns"]) == (100, 500, 1000)
    assert baseline["current"] is True and baseline["expired"] is False
    assert (mutated["valid_from_unix_ns"], mutated["preclaim_time_unix_ns"], mutated["valid_until_unix_ns"]) == (100, 1000, 1000)
    assert mutated["current"] is False and mutated["expired"] is True
    assert model["independent_mutation_set"] == ["preclaim_time_unix_ns:500->1000"]
    assert model["independent_mutation_count"] == 1
    assert model["dependent_recomputation_count"] == 4
    assert model["baseline_formal_state_identity"] != model["mutated_formal_state_identity"]
    assert "canonical_human_authority_payload_digest" in model["unchanged_identity_set"]
    assert "CHE_correlation_identity" in model["unchanged_identity_set"]
    assert model["later_fresh_identity_status"].startswith("NOT_PROVEN")


def test_exact_p11_owner_predicate_transition_and_denial_order() -> None:
    owner = JJ.authenticate_p11_semantics(ROOT)
    assert owner["validity_interval"] == "valid_from_unix_ns <= preclaim_time < valid_until_unix_ns"
    assert owner["expired_predicate"] == "preclaim_time >= available.binding.valid_until_unix_ns"
    assert owner["transition"] == "AVAILABLE -> EXPIRED"
    assert owner["transition_revision_delta"] == 1
    assert owner["one_way_fail_closed"] == "VERIFIED__NO_TRANSITION_FROM_EXPIRED_TO_AVAILABLE"
    assert owner["denial_boundary"].endswith("before P11_DA_OPERATIONAL_PRECLAIM append")
    assert owner["denial_reason"] == "one-use Human act expired before PRECLAIM"
    assert owner["protected_invocation_after_denial"] == 0
    assert owner["protected_effect_after_denial"] == 0
    assert owner["p11_mutation_required"] is False


def test_future_and_expired_are_distinct_temporal_siblings() -> None:
    reuse = JJ.authenticate_temporal_and_route_reuse(ROOT)
    assert reuse["future_predicate"] == "evaluation_time_unix_ns < valid_from_unix_ns"
    assert reuse["expired_predicate"] == "preclaim_time_unix_ns >= valid_until_unix_ns"
    assert reuse["shared_interval"] == "valid_from_unix_ns <= current_coordinate_unix_ns < valid_until_unix_ns"
    distinctions = JJ.sibling_distinctions()
    assert set(distinctions) == {
        "FUTURE", "STALE", "REVOKED", "SUPERSEDED", "WRONG_SCOPE",
        "AMBIGUOUS", "COHERENT_COPY",
    }
    assert all("not" in text.lower() or ";" in text for text in distinctions.values())


def test_temporal_route_and_versioned_binding_reuse_without_mutation() -> None:
    reuse = reduction()["temporal_and_route_reuse"]
    for generation in ("ie", "if", "ih", "in", "io", "jf", "jg", "jh"):
        assert reuse[generation].startswith("VERIFIED")
    assert reuse["production_route_before"] == reuse["production_route_after"] == 1
    assert reuse["production_route_delta"] == 0
    assert reuse["wall_clock_dependency_added_by_jj"] == 0
    assert reuse["later_operational_preclaim_time_control"].startswith("NOT_PROVEN")


def test_ex_common_substrate_reuses_all_17_without_reconstruction() -> None:
    validator_path = ROOT / (
        ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
        "validator/G77_256EX_COMMON_SUBSTRATE_CERTIFICATION_VALIDATOR_V1.py"
    )
    validator = load_module(validator_path, "g77_256ex_validator_for_jj")
    result = validator.validate(ROOT / (
        ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
        "G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"
    ))
    assert result["regression_total"] == result["regression_pass"] == 12
    assert result["regression_fail"] == 0
    value = reduction()
    assert value["metrics"]["ex_reused"] == "VERIFIED__17_OF_17"
    assert value["metrics"]["ex_reconstructed"] == "VERIFIED__0"


def test_operational_firewall_and_overengineering_counters_are_zero() -> None:
    value = reduction()
    assert set(value["operational_counters"].values()) == {"VERIFIED__0"}
    assert all(item.startswith("VERIFIED__0") for item in value["mutation_counters"].values())
    assert set(value["overengineering"].values()) == {"VERIFIED__0"}
    assert value["reuse_impact"]["production_route_before"] == "VERIFIED__1"
    assert value["reuse_impact"]["production_route_after"] == "VERIFIED__1"
    assert value["reuse_impact"]["production_route_delta"] == "VERIFIED__0"
    assert value["reuse_impact"]["parallel_flow_created"] == "VERIFIED__NO"
    assert value["e05"]["before"] == value["e05"]["after"] == "VERIFIED__11_OF_18"
    assert value["e05"]["credit"] == "VERIFIED__0"


def test_formalizer_has_no_clock_or_operational_execution_dependency() -> None:
    tree = ast.parse(FORMALIZER.read_text(encoding="utf-8"))
    imported = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert "time" not in imported and "datetime" not in imported
    source = FORMALIZER.read_text(encoding="utf-8")
    for forbidden in ("qemu-system", "subprocess.run", "subprocess.Popen", "os.system"):
        assert forbidden not in source
    assert reduction()["mutation_counters"]["wall_clock_dependency_count"] == (
        "VERIFIED__0__JJ_FORMALIZATION_USES_ONLY_FIXED_COORDINATES"
    )


def test_required_metrics_ccwim_and_cognition_provenance_are_complete() -> None:
    value = reduction()
    required_metrics = {
        "project_progress", "project_progress_estimate", "constitutional_health_evidence",
        "shadow_automation_status", "constitutional_frontier_distance",
        "constitutional_frontier_distanc_e", "e05_frontier_distance",
        "selected_e05_local_frontier_distance", "last_verified_edge", "first_broken_edge",
        "blocking_owner", "minimum_missing_capability", "minimum_legal_next_delta",
        "governance_efficience", "architectural_governance_efficience",
        "proof_reuse_efficiency", "cognition_assisted_handoff", "aigol_codex_work_share",
        "overengineering_risk", "proof_process_overhead_risk", "cognition_provenance",
        "candidate_capability", "shadow_design_target", "constitutional_continuation_progress",
        "prompt_context_reuse_ratio", "repository_derived_execution_context_ratio",
        "constitutional_prompt_externalization_ratio", "token_benchmark",
        "llm_cost_reduction_ratio", "lcrr", "ex_reused", "ex_reconstructed",
    }
    assert required_metrics <= set(value["metrics"])
    assert value["metrics"]["project_progress_estimate"] == (
        "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR"
    )
    required_ccwim = {
        "ccwim_maturity_level", "cross_worker_state_recovery_level",
        "repository_derived_context_ratio", "human_handoff_information_required",
        "previous_worker_conversation_required", "previous_worker_identity_required",
        "previous_worker_memory_required", "authenticated_repository_continuation",
        "inter_generation_cross_worker_continuation", "intra_generation_cross_worker_continuation",
        "uncommitted_delta_recovery", "authority_state_recovery", "consumed_authority_recovery",
        "post_operation_state_recovery", "operation_replay_prevention",
        "cross_worker_constitutional_drift", "observed_artifact_level_cross_worker_drift",
        "handoff_sufficiency_status", "handoff_state_completeness",
        "handoff_reconstruction_required", "handoff_reconstruction_success",
        "handoff_ambiguity_count", "unauthenticated_handoff_assumption_count",
    }
    assert required_ccwim <= set(value["ccwim"])
    assert value["ccwim"]["ccwim_maturity_level"].startswith("ESTIMATED__L4_LIKE")
    assert value["cognition_provenance"]["prompt_assertions"].startswith("NOT_APPLICABLE")
    assert value["cognition_provenance"]["provider_model_reasoning"].startswith("NOT_APPLICABLE")


def test_g48_exact_six_h1_reuse_impact_ccwim_and_required_questions() -> None:
    report = REPORT.read_text(encoding="utf-8")
    h1 = [line for line in report.splitlines() if line.startswith("# ")]
    assert h1 == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    assert "## Reuse Impact Assessment" in report
    assert "## Constitutional Continuity & Worker Independence Metrics — CCWIM" in report
    for required in (
        "Generation:", "Report identity:", "Reporting date:",
        "Constitutional baseline:", "Implementation contracts:",
        "Objective:", "Implementation scope:", "Modified modules:",
        "Intentionally unchanged modules:", "Architectural boundaries preserved:",
    ):
        assert required in report
    for question in (
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "Katere nove zmogljivosti (če sploh) nastanejo?",
        "Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "Ali implementacija ustvarja vzporedni tok?",
        "Ali zmanjšuje ali povečuje število produkcijskih poti?",
    ):
        assert question in report
    assert "AUTO_CONTINUABLE = NO" in report
    assert "HUMAN_REVIEW_REQUIRED = YES" in report
    assert report.rstrip().endswith(JJ.TERMINAL)


def test_layer_0_and_historical_evidence_are_untouched() -> None:
    changed = subprocess.check_output(
        ["git", "diff", "--name-only"], cwd=ROOT, text=True
    ).splitlines()
    assert all(path.startswith(f"{JJ.NAMESPACE}/") for path in changed)
    status = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=ROOT, text=True,
    ).splitlines()
    assert all(line[3:].startswith(f"{JJ.NAMESPACE}/") for line in status)
    assert not any("CONSTITUTIONAL_INVARIANTS" in line for line in status)
