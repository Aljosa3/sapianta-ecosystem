#!/usr/bin/env python3
"""Focused authority-free validation for G77-256IU."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
IU = ROOT / ".github/governance/evidence/g77_256iu_post_commit_future_static_readiness_v1"
FORMALIZER = IU / "analysis/G77_256IU_POST_COMMIT_FUTURE_STATIC_READINESS_FORMALIZER_V1.py"
TERMINAL = IU / "G77_256IU_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = IU / "G77_256IU_G48_POST_COMMIT_STATIC_READINESS_REPORT_V1.md"


def load_module():
    specification = importlib.util.spec_from_file_location("g77_256iu_test_formalizer", FORMALIZER)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


IUF = load_module()
RUN = IUF.build_envelope()


def load_unique(path: Path) -> dict:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique)
    assert raw == IUF.canonical_bytes(value)
    return value


def test_exact_ratified_it_entry_lineage_and_nested_authority() -> None:
    entry = RUN["reduction"]["entry"]
    assert (entry["head"], entry["tree"], entry["subject"]) == (
        IUF.IT_HEAD, IUF.IT_TREE, IUF.IT_SUBJECT,
    )
    assert entry["remote_head"] == IUF.IT_HEAD
    assert entry["index"] == "" and entry["tracked_delta"] == ""
    assert set(entry["lineage"]) == set(IUF.LINEAGE)
    assert set(entry["lineage"].values()) == {"VERIFIED"}
    assert entry["nested_authority"]["clean"] is True
    assert entry["nested_authority"]["detached"] is True
    assert entry["nested_authority"]["remote_tag"] == IUF.NESTED_HEAD


def test_it_is_reconstructed_from_exact_committed_objects() -> None:
    result = RUN["reduction"]["it_reconstruction"]
    assert result["status"] == "VERIFIED__COMMITTED_OBJECT_RECONSTRUCTION"
    assert result["artifact_count"] == 4
    assert result["inner_seal"] == "VERIFIED"
    assert result["terminal"] == (
        "A__FUTURE_BOOTSTRAP_AND_NOCLOUD_SEED_BINDING_REPOSITORY_IMPLEMENTED"
    )


def test_bootstrap_seed_extraction_selector_and_guest_consumer() -> None:
    result = RUN["reduction"]["bootstrap_seed_selector"]
    assert result["committed_it_bootstrap_hash"] == "VERIFIED__EXACT"
    assert result["committed_it_nocloud_seed_hash"] == "VERIFIED__EXACT"
    assert set(result["seed_member_equality"].values()) == {"VERIFIED__EXACT_BYTES"}
    assert result["future_selector_target"] == "VERIFIED__IT_SUCCESSOR_PAIR"
    assert result["existing_fm_guest_consumer_occurrence"] == "VERIFIED__EXACTLY_ONE"
    assert result["existing_fm_guest_path"] == IUF.GUEST_PATH
    assert result["stale_bootstrap_projection"] == "VERIFIED__NO"


def test_future_semantics_are_immutable_and_wall_clock_free() -> None:
    future = RUN["reduction"]["future_semantics"]
    assert (future["evaluation"], future["valid_from"], future["valid_until"]) == (500, 600, 1000)
    assert future["relation"] == "500 < 600 < 1000"
    assert future["payload_digest"] == "9568e0c248ad488cabcf6bde6b490c544077862d10e3fda13bcdc8ed9953f547"
    assert future["future_semantic_mutation_count"] == "VERIFIED__0"
    assert future["wall_clock_dependency_count"] == "VERIFIED__0"


def test_du_eb_ee_v2_post_commit_role_separation() -> None:
    readiness = RUN["reduction"]["readiness"]
    assert readiness["du_v2_post_commit_readiness"] == "VERIFIED"
    assert readiness["eb_v2_post_commit_readiness"] == "VERIFIED"
    assert readiness["ee_v2_post_commit_readiness"] == "VERIFIED"
    assert readiness["du_eb_ee_v2_chain"] == "VERIFIED"
    assert readiness["runtime_target"] == {"head": IUF.IF_HEAD, "tree": IUF.IF_TREE}
    assert readiness["certification_baseline"] == {"head": IUF.IT_HEAD, "tree": IUF.IT_TREE}
    assert readiness["runtime_target_equals_certification_baseline"] == "VERIFIED__NO"
    assert readiness["role_collapse"] == "VERIFIED__NO"
    assert readiness["family_local_dispatch"] == "VERIFIED"
    assert readiness["global_registry"] == "VERIFIED__NO"


def test_full_fm_authority_free_static_readiness_closes() -> None:
    readiness = RUN["reduction"]["readiness"]
    assert readiness["materialization"] == "FRESH_OPERATION_STATE_MATERIALIZED_WITHOUT_QEMU"
    assert readiness["static_readiness_result"] == "STATIC_READINESS_PASS"
    assert readiness["fm_authority_free_static_readiness"] == "VERIFIED"
    assert readiness["future_post_commit_preoperational_readiness"] == "VERIFIED"
    assert readiness["existing_fm_guest_consumer_bound"] == "VERIFIED"
    assert readiness["guest_consumer_route_count"] == "VERIFIED__1"
    assert readiness["guest_consumer_bypass"] == "VERIFIED__NO"


def test_gn_gl_p11_ex_and_route_firewalls() -> None:
    boundary = RUN["reduction"]["boundary_firewalls"]
    assert boundary == {
        "gn_future_compatibility": "VERIFIED",
        "gl_boundary": "VERIFIED",
        "human_authorization_presentation_issued": "VERIFIED__0",
        "p11_mutation_count": "VERIFIED__0",
        "p11_bypass": "VERIFIED__NO",
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
    }
    route = RUN["reduction"]["route_firewall"]
    assert route["parallel_flow_created"] == "VERIFIED__NO"
    assert route["production_route_before"] == route["production_route_after"] == "VERIFIED__1"
    assert route["production_route_delta"] == "VERIFIED__0"


def test_all_operational_counters_are_zero_and_e05_unchanged() -> None:
    counters = RUN["reduction"]["operational_counters"]
    assert counters["e05"] == "VERIFIED__10_OF_18"
    assert all(value == "VERIFIED__0" for key, value in counters.items() if key != "e05")


def test_terminal_frontier_stops_for_separate_human_governed_generation() -> None:
    reduction = RUN["reduction"]
    assert reduction["terminal"] == "A__FUTURE_POST_COMMIT_FULL_STATIC_READINESS_VERIFIED"
    frontier = reduction["terminal_frontier"]
    assert frontier["last_verified_edge"] == "FUTURE_POST_COMMIT_FULL_STATIC_PREOPERATIONAL_READINESS"
    assert frontier["first_broken_edge"] == "FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_NOT_YET_ISSUED"
    assert frontier["auto_continuable"] == "NO"
    assert frontier["human_review_required"] == "YES"
    assert frontier["next_generation_started"] == "NO"


def test_terminal_is_canonical_unique_inner_sealed_and_reproducible() -> None:
    terminal = load_unique(TERMINAL)
    assert terminal == RUN
    assert terminal["reduction_sha256"] == hashlib.sha256(
        IUF.canonical_bytes(terminal["reduction"])
    ).hexdigest()
    with pytest.raises(ValueError, match="duplicate JSON key"):
        json.loads('{"a":1,"a":2}', object_pairs_hook=lambda pairs: (_ for _ in ()).throw(ValueError("duplicate JSON key")))


def test_formalizer_ast_and_prohibited_operational_calls_absent() -> None:
    source = FORMALIZER.read_text(encoding="utf-8")
    ast.parse(source, filename=str(FORMALIZER))
    prohibited = (
        "render_human_authorization_presentation(",
        "validate_execution_admission(",
        "validate_final_admission(",
        "subprocess.Popen(",
        "subprocess.call(",
        "os.exec",
    )
    assert all(token not in source for token in prohibited)


def test_exact_six_g48_headings_and_all_required_metrics() -> None:
    text = REPORT.read_text(encoding="utf-8")
    headings = [line for line in text.splitlines() if line.startswith("# ")]
    assert headings == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]
    required = {
        "Reuse Impact Assessment", "Infrastructure Amortization", "CCWIM",
        "Cognition Provenance", "Prompt Externalization Metrics",
        "PROJECT_PROGRESS_ESTIMATE", "CONSTITUTIONAL_HEALTH_EVIDENCE",
        "SHADOW_AUTOMATION_STATUS", "CONSTITUTIONAL_FRONTIER_DISTANCE",
        "E05_FRONTIER_DISTANCE", "SELECTED_E05_LOCAL_FRONTIER_DISTANCE",
        "GOVERNANCE_EFFICIENCE", "ARCHITECTURAL_GOVERNANCE_EFFICIENCE",
        "PROOF_REUSE_EFFICIENCY", "COGNITION_ASSISTED_HANDOFF",
        "AIGOL_CODEX_WORK_SHARE", "OVERENGINEERING_RISK",
        "PROOF_PROCESS_OVERHEAD_RISK", "COGNITION_PROVENANCE",
        "CANDIDATE_CAPABILITY", "SHADOW_DESIGN_TARGET",
        "CONSTITUTIONAL_CONTINUATION_PROGRESS", "PROMPT_CONTEXT_REUSE_RATIO",
        "REPOSITORY_DERIVED_EXECUTION_CONTEXT_RATIO",
        "CONSTITUTIONAL_PROMPT_EXTERNALIZATION_RATIO", "TOKEN_BENCHMARK",
        "LLM_COST_REDUCTION_RATIO", "LCRR", "E05_GENERATIONS_PER_CREDIT",
        "OPERATIONAL_ATTEMPTS_PER_CREDIT", "MARGINAL_E05_GENERATION_COST",
        "MARGINAL_NEW_INFRASTRUCTURE_PER_E05_CREDIT",
        "INFRASTRUCTURE_AMORTIZATION_SIGNAL", "EXPECTED_NEXT_CREDIT_GENERATION_COUNT",
    }
    assert all(token in text for token in required)


def test_only_iu_evidence_is_uncommitted_and_index_is_empty() -> None:
    assert subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True
    ).strip() == ""
    assert subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT, text=True
    ).strip() == ""
    assert subprocess.check_output(
        ["git", "diff", "--name-only", IUF.IT_HEAD, "--", *IUF.P11_PATHS],
        cwd=ROOT, text=True,
    ).strip() == ""
