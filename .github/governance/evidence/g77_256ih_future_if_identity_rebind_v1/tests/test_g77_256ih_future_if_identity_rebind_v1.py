#!/usr/bin/env python3
"""Focused repository-only validation for G77-256IH."""

from __future__ import annotations

import ast
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
IH = ROOT / ".github/governance/evidence/g77_256ih_future_if_identity_rebind_v1"
BINDER_PATH = IH / "binding/G77_256IH_POST_IG_FUTURE_IF_REBIND_V1.py"
LIVE = IH / "live_binding"
CANDIDATE = LIVE / "candidate/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json"
RUNTIME = LIVE / "runtime_projection/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json"
CONTEXT = LIVE / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
HARNESS = LIVE / "bindings/G77_256IH_EE_PATH_PROJECTION_FIXTURE_V1.py"
CHECKPOINT = LIVE / "bindings/G77_256IH_DU_EB_EE_READINESS_CHECKPOINT_V1.json"
TERMINAL = IH / "G77_256IH_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = IH / "G77_256IH_G48_IMPLEMENTATION_REPORT_V1.md"


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


BINDER = load_module(BINDER_PATH, "g77_256ih_test_binder")


def rejects(call) -> bool:
    try:
        call()
    except Exception:
        return True
    return False


def test_exact_ig_entry_if_ancestry_remote_tracking_and_nested_authority() -> None:
    entry = BINDER.authenticate_entry(ROOT)
    assert entry["head"] == BINDER.IG_HEAD
    assert entry["tree"] == BINDER.IG_TREE
    assert entry["subject"] == BINDER.IG_SUBJECT
    assert entry["remote_tracking_head"] == BINDER.IG_HEAD
    assert entry["index"] == ""
    assert entry["nested"]["head"] == BINDER.NESTED_HEAD
    assert entry["nested"]["tree"] == BINDER.NESTED_TREE
    assert entry["nested"]["branch"] == entry["nested"]["status"] == ""


def test_committed_ig_frontier_reconstructs_exactly() -> None:
    result = BINDER.reconstruct_ig(ROOT)
    assert result["status"] == "VERIFIED"
    assert set(result["identity_map"]) == set(BINDER.COMMITTED_IG_PATHS)
    assert result["frontier"]["current_e05_status"] == "VERIFIED__10_OF_18"
    assert result["frontier"]["first_broken_edge"] == (
        "COMMITTED_IF_LAUNCHER_CANDIDATE_AND_CONTEXT_REMAIN_BOUND_TO_IE_NOT_IF"
    )


def test_future_semantics_act_che_and_deterministic_time_are_unchanged() -> None:
    semantics = BINDER.future_semantics(ROOT)
    assert semantics["evaluation_time_unix_ns"] == 500
    assert semantics["valid_from_unix_ns"] == 600
    assert semantics["valid_until_unix_ns"] == 1000
    assert semantics["payload_digest"] == BINDER.FUTURE_PAYLOAD_DIGEST
    assert semantics["source_act_digest"] == BINDER.SOURCE_ACT_DIGEST
    assert semantics["correlation_identity"] == BINDER.CORRELATION_IDENTITY
    assert semantics["ih_semantic_mutation_count"] == "VERIFIED__0"
    assert semantics["human_operational_authority"] == 0


def test_one_logical_launcher_rebind_bootstrap_nocloud_and_route() -> None:
    result = BINDER.verify_checkout_bootstrap(ROOT)
    assert result["checkout_head"] == BINDER.IF_HEAD
    assert result["checkout_tree"] == BINDER.IF_TREE
    assert result["bootstrap_binding"] == "VERIFIED__IF_CONTEXT_COUPLED_UNCHANGED_BYTES"
    assert result["nocloud_projection_status"] == "VERIFIED"
    assert result["host_guest_equivalence"].startswith("VERIFIED__")
    assert result["wall_clock_dependency_count_on_future_path"] == "VERIFIED__0"
    assert result["production_route_before"] == result["production_route_after"] == "VERIFIED__1"
    assert result["production_route_delta"] == "VERIFIED__0"


def test_candidate_runtime_and_context_are_exact_if_bound_and_reproducible() -> None:
    candidate = BINDER.load_canonical(CANDIDATE)
    context = BINDER.load_canonical(CONTEXT)
    assert BINDER.canonical_bytes(BINDER.build_candidate(ROOT)) == CANDIDATE.read_bytes()
    assert CANDIDATE.read_bytes() == RUNTIME.read_bytes()
    assert candidate["manifest"]["required_head"] == BINDER.IF_HEAD
    assert candidate["manifest"]["source_tree"] == BINDER.IF_TREE
    assert context["repository_head"] == BINDER.IF_HEAD
    assert context["repository_tree"] == BINDER.IF_TREE
    checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    assert checkout["head"] == BINDER.IF_HEAD and checkout["tree"] == BINDER.IF_TREE
    assert context["candidate_manifest_sha256"] == BINDER.sha256_path(CANDIDATE)
    assert BINDER.build_context(ROOT, CANDIDATE) == context


def test_du_passes_and_eb_ee_fail_closed_on_actual_ig_vs_required_if() -> None:
    result = BINDER.baseline_owner_results(ROOT, CANDIDATE)
    assert result["du"] == "VERIFIED__CURRENT_IF_BOUND"
    assert set(result["du_gate_results"].values()) == {"PASS"}
    assert result["eb"] == "NOT_PROVEN__REQUIRED_HEAD_MISMATCH__ACTUAL_IG_REQUIRED_IF"
    assert result["ee"] == "NOT_PROVEN__REQUIRED_HEAD_MISMATCH__ACTUAL_IG_REQUIRED_IF"
    assert result["eb_receipt_created"] is result["ee_receipt_created"] is False
    assert result["receipt_fabrication_count"] == 0
    assert not (LIVE / "bindings/G77_256IH_EB_RECEIPT_V1.json").exists()
    assert not (LIVE / "bindings/G77_256IH_EE_RECEIPT_V1.json").exists()


def test_binding_checkpoint_is_canonical_sealed_and_matches_current_files() -> None:
    envelope = BINDER.load_canonical(CHECKPOINT)
    checkpoint = envelope["checkpoint"]
    assert envelope["checkpoint_sha256"] == BINDER.sha256_bytes(
        BINDER.canonical_bytes(checkpoint)
    )
    assert checkpoint["candidate_sha256"] == BINDER.sha256_path(CANDIDATE)
    assert checkpoint["runtime_sha256"] == BINDER.sha256_path(RUNTIME)
    assert checkpoint["context_file_sha256"] == BINDER.sha256_path(CONTEXT)
    assert HARNESS.is_file()


@pytest.mark.parametrize("field,value", (
    ("required_head", "71391a75011cdc388bdac9183f4654814a044c69"),
    ("required_head", "f" * 40),
    ("source_tree", "0" * 40),
))
def test_wrong_stale_future_or_conflicting_candidate_baseline_rejects(
    field: str, value: str
) -> None:
    du = load_module(ROOT / BINDER.DU_OWNER, f"g77_256ih_du_negative_{field}_{value[0]}")
    candidate = deepcopy(BINDER.load_canonical(CANDIDATE))
    candidate["manifest"][field] = value
    candidate["manifest_sha256"] = BINDER.sha256_bytes(
        BINDER.canonical_bytes(candidate["manifest"])
    )
    assert rejects(lambda: du.validate_envelope(candidate, ROOT, expected_head=BINDER.IF_HEAD))


def test_historical_failure_firewall_no_second_launcher_or_operational_owner() -> None:
    source = BINDER_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    assert not any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "main"
        for node in ast.walk(tree)
    )
    assert list(IH.rglob("*LAUNCHER*.py")) == []
    launcher_tree = ast.parse((ROOT / BINDER.FM_LAUNCHER).read_text(encoding="utf-8"))
    assert sum(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "main"
        for node in launcher_tree.body
    ) == 1
    assert "FUTURE_IH_COMMIT" not in source
    assert BINDER.IF_HEAD != BINDER.IG_HEAD


def test_terminal_is_canonical_sealed_zero_operation_and_fail_closed() -> None:
    envelope = BINDER.load_canonical(TERMINAL)
    reduction = envelope["reduction"]
    assert envelope["reduction_sha256"] == BINDER.sha256_bytes(
        BINDER.canonical_bytes(reduction)
    )
    assert BINDER.terminal_reduction(ROOT, LIVE) == reduction
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["e05"] == {
        "before": "10/18", "after": "10/18", "credit": 0,
        "required": 18, "satisfied": 10, "remaining": 8,
    }
    assert reduction["readiness"]["future_live_identity_rebind"] == (
        "VERIFIED__REPOSITORY_PREPARED_IF_BOUND"
    )
    assert reduction["readiness"]["future_preoperational_readiness"].startswith("NOT_PROVEN__")
    assert reduction["readiness"]["next_operational_generation_eligible"] == "NOT_PROVEN"
    assert reduction["terminal_control"]["auto_continuable"] is False
    assert reduction["terminal_control"]["human_review_required"] is True
    assert reduction["terminal_control"]["next_generation_started"] is False
    assert reduction["root_rebind"]["future_commit_prediction_count"] == "VERIFIED__0"
    recovery = reduction["interruption_recovery"]
    assert recovery["ih_replay_required"] == "VERIFIED__NO"
    assert recovery["ih_existing_delta_status"] == "VERIFIED__PRESENT_UNSTAGED_AND_BOUNDED"
    assert recovery["ih_first_unproven_edge_after_recovery"] == (
        "VERIFIED__EB_EE_REQUIRED_HEAD_MISMATCH"
    )
    interpretation = reduction["identity_interpretation"]
    assert interpretation["target_runtime_identity"]["head"] == BINDER.IF_HEAD
    assert interpretation["current_repository_certification_identity"]["head"] == BINDER.IG_HEAD
    assert interpretation["existing_non_circular_separation_mechanism"] == "NOT_PROVEN"
    ccwim = reduction["ccwim"]
    assert ccwim["same_generation_continuation_status"].startswith("VERIFIED__")
    assert ccwim["cross_account_continuation_status"].startswith("NOT_PROVEN__")
    assert ccwim["uncommitted_delta_recovery"].startswith("VERIFIED__")
    validation = reduction["validation"]
    assert validation["current_applicable_assertions"] == "VERIFIED__206_PASSED"
    assert len(validation["historical_deselection_reasons"]) == 14


def test_g48_report_has_exactly_six_top_level_headings() -> None:
    headings = [
        line for line in REPORT.read_text(encoding="utf-8").splitlines()
        if line.startswith("# ")
    ]
    assert headings == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]


def test_all_ih_json_rejects_duplicate_keys_and_all_python_parses() -> None:
    json_paths = sorted(IH.rglob("*.json"))
    assert len(json_paths) == 5
    for path in json_paths:
        BINDER.load_canonical(path)
    with pytest.raises(BINDER.IHBindingError, match="DUPLICATE_JSON_KEY__a"):
        BINDER.load_canonical_bytes(b'{"a":1,"a":2}\n', "duplicate-fixture")
    python_paths = sorted(IH.rglob("*.py")) + [ROOT / BINDER.FM_LAUNCHER]
    assert len(python_paths) == 4
    for path in python_paths:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
