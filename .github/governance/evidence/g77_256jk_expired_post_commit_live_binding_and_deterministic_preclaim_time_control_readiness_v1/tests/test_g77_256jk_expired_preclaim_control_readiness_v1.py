#!/usr/bin/env python3
"""Focused repository-only validation for G77-256JK."""

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

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
JK_ROOT = ROOT / (
    ".github/governance/evidence/"
    "g77_256jk_expired_post_commit_live_binding_and_deterministic_"
    "preclaim_time_control_readiness_v1"
)
FORMALIZER = JK_ROOT / "analysis/G77_256JK_EXPIRED_PRECLAIM_CONTROL_READINESS_FORMALIZER_V1.py"
REDUCTION = JK_ROOT / "G77_256JK_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = JK_ROOT / "G77_256JK_G48_IMPLEMENTATION_REPORT_V1.md"
EXPECTED_FILES = {
    "G77_256JK_G48_IMPLEMENTATION_REPORT_V1.md",
    "G77_256JK_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json",
    "analysis/G77_256JK_EXPIRED_PRECLAIM_CONTROL_READINESS_FORMALIZER_V1.py",
    "tests/test_g77_256jk_expired_preclaim_control_readiness_v1.py",
}


def load_module(path: Path, name: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


JK = load_module(FORMALIZER, "g77_256jk_formalizer")


def unique_json(path: Path) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            assert key not in value
            value[key] = item
        return value

    result = json.loads(path.read_bytes(), object_pairs_hook=unique)
    assert isinstance(result, dict)
    return result


def reduction() -> dict[str, Any]:
    return unique_json(REDUCTION)["reduction"]


def test_authenticated_entry_remote_tracking_and_nested_authority() -> None:
    value = JK.authenticate_entry(ROOT)
    assert value["branch"] == JK.ENTRY_BRANCH
    assert value["head"] == value["remote_tracking_head"] == value["entry_remote_head"] == JK.ENTRY_HEAD
    assert value["tree"] == JK.ENTRY_TREE
    assert value["subject"] == JK.ENTRY_SUBJECT
    assert value["entry_worktree"] == "VERIFIED__CLEAN_BEFORE_JK_WRITE"
    assert value["index"] == "VERIFIED__EMPTY"
    assert value["nested_authority"] == {
        "clean": True, "detached": True, "head": JK.NESTED_HEAD,
        "tree": JK.NESTED_TREE, "tag": JK.NESTED_TAG,
        "origin": JK.NESTED_ORIGIN,
    }


def test_exact_four_file_bounded_namespace_and_empty_index() -> None:
    observed = {
        str(path.relative_to(JK_ROOT)) for path in JK_ROOT.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }
    assert observed == EXPECTED_FILES
    assert subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True
    ).strip() == ""
    status = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=ROOT, text=True,
    ).splitlines()
    assert status
    assert all(line[3:].startswith(f"{JK.NAMESPACE}/") for line in status)


def test_all_25_sources_are_hash_bound_committed_regular_files() -> None:
    sources = JK.authenticate_sources(ROOT)
    assert len(sources) == 25
    assert sources == reduction()["sources"]
    assert all((ROOT / item["path"]).is_file() for item in sources)


def test_committed_jj_terminal_selection_semantics_e05_and_ex_reconstruct() -> None:
    value = JK.reconstruct_jj(ROOT)
    assert value["terminal"] == "A__EXPIRED_VECTOR_DETERMINISTIC_REPOSITORY_FORMALIZATION_VERIFIED"
    assert value["expired_selection"] == "VERIFIED__INHERITED_FROM_COMMITTED_JI"
    assert value["expired_formalization"] == "VERIFIED__DETERMINISTIC_REPOSITORY_ONLY"
    assert value["expired_operational_status"] == "NOT_PROVEN_OPERATIONALLY"
    assert value["e05_before"] == value["e05_after"] == "VERIFIED__11_OF_18"
    assert value["e05_credit"] == "VERIFIED__0"
    assert value["ex_reused"] == "VERIFIED__17_OF_17"
    assert value["ex_reconstructed"] == "VERIFIED__0"
    assert value["fixture"] == {
        "valid_from_unix_ns": 100, "baseline_preclaim_time_unix_ns": 500,
        "expired_preclaim_time_unix_ns": 1000, "valid_until_unix_ns": 1000,
    }


def test_exact_preclaim_owner_source_binding_and_trust_boundary() -> None:
    value = JK.trace_preclaim_time(ROOT)
    assert value["preclaim_time_owner"].endswith("P11BoundedConsumerV1.claim_and_invoke_once")
    assert value["preclaim_time_source"].startswith("Python time.time_ns()")
    assert value["preclaim_source_call_count"] == 3
    assert value["p11_module_time_time_ns_call_count"] == 4
    assert value["preclaim_time_caller_selectability"].startswith("VERIFIED__NO")
    assert value["preclaim_time_provider_selectability"].startswith("VERIFIED__NO")
    assert value["preclaim_time_replay_semantics"].startswith("NOT_PROVEN")
    assert value["preclaim_time_authentication_status"].startswith("NOT_PROVEN")
    assert not any("time" in item for item in value["preclaim_api_arguments"])
    assert not any("time" in item for item in value["custody_request_fields"])


def test_equality_boundary_and_malformed_coordinates_fail_closed() -> None:
    value = JK.verify_boundaries()
    assert value["valid_until_minus_1"] == "NOT_EXPIRED"
    assert value["valid_until"] == "EXPIRED"
    assert value["valid_until_plus_1"] == "EXPIRED"
    assert JK.boundary_classification(500, 1000) == "NOT_EXPIRED"
    for coordinate in (-1, True, 1.0, "1000", None):
        with pytest.raises(JK.ReadinessError, match="TEMPORAL_COORDINATE_MALFORMED"):
            JK.boundary_classification(coordinate, 1000)


def test_future_temporal_reuse_is_submission_only_and_gap_is_exact() -> None:
    value = JK.verify_temporal_reuse_and_gap(ROOT)
    assert value["decision_order"] == "C__EXACT_MINIMUM_MISSING_CAPABILITY__STOP"
    for generation in ("ie", "if", "ih", "in", "io", "jf", "jg", "jh", "ji", "jj"):
        assert value[generation].startswith("VERIFIED")
    assert value["existing_deterministic_submission_control"].startswith("VERIFIED")
    assert value["existing_deterministic_preclaim_control"].startswith("NOT_PROVEN")
    assert value["family_local_binding_without_p11_semantic_change"].startswith("NOT_PROVEN")
    assert "time.time_ns()" in value["first_broken_edge"]


def test_wall_clock_firewall_and_control_assessment_fail_closed() -> None:
    wall = JK.wall_clock_audit()
    control = JK.control_assessment()
    assert wall["runtime_clock_capability_is_execution_authority"] == "VERIFIED__NO"
    assert wall["wall_clock_constitutional_authority_absent"].startswith("NOT_PROVEN")
    assert wall["hidden_wall_clock_fallback_absent"].startswith("NOT_PROVEN")
    assert control["preclaim_time_control_status"].startswith("NOT_PROVEN")
    assert control["deterministic"].startswith("NOT_PROVEN")
    assert control["authenticated_or_structurally_sealed"] == "NOT_PROVEN"
    assert control["caller_selectable"] == control["provider_selectable"] == "VERIFIED__NO"
    assert control["p11_bypass"] == "VERIFIED__NOT_INTRODUCED_BY_JK"
    assert control["protected_effect_before_expiry_evaluation"] == "VERIFIED__0"


def test_live_binding_option_b_roles_preserved_but_coordinate_e_blocks() -> None:
    value = JK.live_binding_model()
    assert value["A_detached_runtime_target_provenance"].startswith("VERIFIED")
    assert value["B_current_certification_baseline"].startswith("VERIFIED")
    assert value["runtime_target_provenance_collapsed_into_certification_provenance"] == "VERIFIED__NO"
    assert value["E_deterministic_preclaim_time_control"] == "NOT_PROVEN__MISSING_BINDING_POINT"
    assert value["precommit_readiness"] == "NOT_PROVEN__BLOCKED_AT_COORDINATE_E"
    assert value["post_jk_commit_live_binding"].startswith("NOT_PROVEN")


def test_p11_owner_semantics_immutable_and_no_duplicate_owner() -> None:
    value = reduction()
    assert value["p11"]["owner"] == "P11 D.A ProtectedOwnerStateStoreV1 via P11BoundedConsumerV1"
    assert value["p11"]["transition"] == "AVAILABLE -> EXPIRED"
    assert value["p11"]["denial_boundary"] == "before P11_DA_OPERATIONAL_PRECLAIM append"
    assert value["p11"]["p11_mutation_count"] == "VERIFIED__0"
    assert value["p11"]["duplicate_p11_logic_count"] == "VERIFIED__0"
    assert value["p11"]["required_change_classification"].startswith("STOP__")


def test_ex_common_substrate_reuses_17_of_17_without_reconstruction() -> None:
    validator_path = ROOT / (
        ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
        "validator/G77_256EX_COMMON_SUBSTRATE_CERTIFICATION_VALIDATOR_V1.py"
    )
    validator = load_module(validator_path, "g77_256ex_validator_for_jk")
    result = validator.validate(ROOT / (
        ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
        "G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"
    ))
    assert result["regression_total"] == result["regression_pass"] == 12
    assert result["regression_fail"] == 0
    assert reduction()["reuse_impact"]["ex_reused"] == "VERIFIED__17_OF_17"
    assert reduction()["reuse_impact"]["ex_reconstructed"] == "VERIFIED__0"


def test_operational_e05_route_and_overengineering_firewalls() -> None:
    value = reduction()
    assert set(value["operational_counters"].values()) == {"VERIFIED__0"}
    assert set(value["mutation_counters"].values()) == {"VERIFIED__0"}
    assert set(value["overengineering"].values()) == {"VERIFIED__0"}
    assert value["e05"]["before"] == value["e05"]["after"] == "VERIFIED__11_OF_18"
    assert value["e05"]["credit"] == "VERIFIED__0"
    assert value["reuse_impact"]["production_route_before"] == "VERIFIED__1"
    assert value["reuse_impact"]["production_route_after"] == "VERIFIED__1"
    assert value["reuse_impact"]["production_route_delta"] == "VERIFIED__0"
    assert value["reuse_impact"]["parallel_flow_created"] == "VERIFIED__NO"


def test_reduction_is_unique_key_canonical_inner_sealed_and_rebuilds() -> None:
    value = unique_json(REDUCTION)
    assert REDUCTION.read_bytes() == JK.canonical_bytes(value) + b"\n"
    assert value["reduction_sha256"] == hashlib.sha256(
        JK.canonical_bytes(value["reduction"]) + b"\n"
    ).hexdigest()
    assert value == JK.envelope(JK.build_reduction(ROOT))
    assert value["reduction"]["terminal"] == JK.TERMINAL


def test_required_metrics_ccwim_and_cognition_provenance_complete() -> None:
    value = reduction()
    metrics = {
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
    assert metrics <= set(value["metrics"])
    assert value["metrics"]["project_progress_estimate"] == "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR"
    ccwim = {
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
    assert ccwim <= set(value["ccwim"])
    assert value["ccwim"]["ccwim_maturity_level"].startswith("ESTIMATED__L4_LIKE")
    assert value["cognition_provenance"]["prompt_assertions"].startswith("NOT_APPLICABLE")
    assert value["cognition_provenance"]["provider_model_reasoning"].startswith("NOT_APPLICABLE")


def test_g48_exact_six_h1_reuse_impact_ccwim_and_required_questions() -> None:
    report = REPORT.read_text(encoding="utf-8")
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]
    assert "## Reuse Impact Assessment" in report
    assert "## Constitutional Continuity & Worker Independence Metrics — CCWIM" in report
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
    assert report.rstrip().endswith(JK.TERMINAL)


def test_formalizer_is_static_and_layer_0_historical_evidence_untouched() -> None:
    tree = ast.parse(FORMALIZER.read_text(encoding="utf-8"))
    imported = {
        alias.name for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom)) for alias in node.names
    }
    assert "time" not in imported and "datetime" not in imported
    source = FORMALIZER.read_text(encoding="utf-8")
    for forbidden in ("subprocess.run", "subprocess.Popen", "os.system", "qemu-system"):
        assert forbidden not in source
    status = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=ROOT, text=True,
    ).splitlines()
    assert all(line[3:].startswith(f"{JK.NAMESPACE}/") for line in status)
    assert not any("CONSTITUTIONAL_INVARIANTS" in line for line in status)
