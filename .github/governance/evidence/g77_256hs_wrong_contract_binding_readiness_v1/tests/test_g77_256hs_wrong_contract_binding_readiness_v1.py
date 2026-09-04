#!/usr/bin/env python3
"""Focused repository-only tests for the G77-256HS fail-closed reduction."""

from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
HS = ROOT / ".github/governance/evidence/g77_256hs_wrong_contract_binding_readiness_v1"
REDUCER_PATH = HS / "analysis/G77_256HS_WRONG_CONTRACT_BINDING_READINESS_REDUCER_V1.py"
TERMINAL_PATH = HS / "G77_256HS_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = ROOT / (
    "docs/governance/G77_256HS_POST_HR_WRONG_CONTRACT_COMMITTED_IDENTITY_"
    "BINDING_AND_PREOPERATIONAL_READINESS_V1.md"
)


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


HS_REDUCER = load_module(REDUCER_PATH, "g77_256hs_reducer_tests")


def load_unique(path: Path) -> dict[str, Any]:
    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            assert key not in value, f"duplicate JSON key: {key}"
            value[key] = item
        return value

    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique_object)
    assert isinstance(value, dict)
    return value


def test_exact_committed_hr_and_nested_authority_authenticate() -> None:
    observed = HS_REDUCER.authenticate_entry(ROOT)
    assert observed["head"] == HS_REDUCER.HR_HEAD
    assert observed["tree"] == HS_REDUCER.HR_TREE
    assert observed["subject"] == HS_REDUCER.HR_SUBJECT
    assert observed["remote_tracking_head"] == HS_REDUCER.HR_HEAD
    assert observed["tracked_status"] == observed["index"] == ""
    assert set(observed["ancestry"].values()) == {True}
    assert observed["nested"]["branch"] == observed["nested"]["status"] == ""
    assert observed["nested"]["head"] == observed["nested"]["tag_head"]


def test_hr_repository_capability_is_independently_reconstructed() -> None:
    result = HS_REDUCER.reconstruct_hr(ROOT)
    assert result["status"] == "VERIFIED"
    assert result["target_mutation"] == "contract_identity"
    assert result["dependent_recomputation"] == "record_identity"
    assert result["semantic_mutation_count"] == 1
    assert result["unrelated_mutation_count"] == 0
    assert result["contract_specific_comparison_reached"] is False
    assert result["expected_error_reason"] == (
        "operational Human act input_record_identity binding is invalid"
    )


def test_ex_is_reused_17_of_17_without_reconstruction() -> None:
    assert HS_REDUCER.authenticate_ex(ROOT) == {
        "status": "VERIFIED", "ex_reused": "17/17", "ex_reconstructed": 0,
    }


def test_current_route_rejects_wrong_contract_at_every_closed_vector_edge() -> None:
    route = HS_REDUCER.diagnose_route(ROOT)
    assert route["status"] == "FAIL_CLOSED"
    assert route["production_route_count"] == 1
    assert route["wrong_contract_route_count"] == 0
    assert route["supported_vectors"] == ["WRONG_ATTEMPT", "WRONG_INPUT"]
    assert set(route["rejections"]) == {
        "fm_context_vector", "fm_bootstrap_vector", "fm_authorization_vector",
        "gn_presentation_vector", "bootstrap_expected_harness", "adapter",
        "hp_materializer",
    }
    assert route["first_broken_edge"] == (
        "FM_CONTEXT_OPERATION_VECTOR_CLOSED_SET_REJECTS_WRONG_CONTRACT"
    )


def test_wrong_contract_cannot_be_misrepresented_as_wrong_input() -> None:
    owner = load_module(ROOT / HS_REDUCER.FM_CONTEXT_OWNER, "g77_256hs_context_test")
    with pytest.raises(owner.ContextError, match="no exact supported operation vector"):
        owner.operation_vector(HS_REDUCER.WRONG_CONTRACT_OPERATION_GENERATION)
    assert owner.operation_vector(
        "G77_256HS_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_INPUT_OPERATIONAL_COMMISSIONING_V1"
    ) == "WRONG_INPUT"


def test_negative_matrix_covers_all_required_binding_dimensions() -> None:
    matrix = HS_REDUCER.negative_matrix()
    assert matrix["status"] == "VERIFIED"
    assert matrix["case_count"] == 18
    assert {row["result"] for row in matrix["results"]} == {
        "FAIL_CLOSED_BEFORE_OPERATION"
    }
    names = " ".join(row["case"] for row in matrix["results"])
    for token in (
        "HR_HEAD", "HR_TREE", "FORMAL_SPECIFICATION", "PRODUCER", "REDUCER",
        "CANDIDATE", "RUNTIME", "CONTEXT", "ADAPTER", "EXPECTED_HARNESS",
        "CHECKOUT", "PROJECTION", "BOOTSTRAP", "SEED", "PRESENTATION",
        "DU_RECEIPT", "EB_RECEIPT", "EE_RECEIPT",
    ):
        assert token in names


def test_terminal_reduction_fails_closed_with_zero_operation_and_credit() -> None:
    reduction = HS_REDUCER.terminal_reduction(ROOT)
    readiness = reduction["readiness_reduction"]
    assert readiness["current_hr_commit_identity_status"] == "VERIFIED"
    assert readiness["wrong_contract_repository_capability"] == "VERIFIED"
    for field in (
        "post_commit_live_binding_status", "wrong_contract_context_status",
        "wrong_contract_adapter_status", "checkout_projection_coherence_status",
        "bootstrap_coherence_status", "expected_harness_binding_status",
        "gn_presentation_binding_status", "current_du_status", "current_eb_status",
        "current_ee_status", "no_known_repository_preauth_blocker_status",
        "preoperational_readiness_status", "next_operational_generation_eligible",
        "wrong_contract_operational_capability",
    ):
        assert readiness[field] == "NOT_PROVEN"
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["e05"] == {
        "before": "8/18", "credit": 0, "after": "8/18", "remaining": 10,
    }
    assert reduction["terminal_control"]["auto_continuable"] is False
    assert reduction["terminal_control"]["human_review_required"] is True
    assert reduction["terminal_control"]["verdict"].startswith("FAIL_CLOSED__")


def test_no_parallel_route_authority_layer_or_runtime_owner_is_created() -> None:
    reduction = HS_REDUCER.terminal_reduction(ROOT)
    impact = reduction["reuse_impact"]
    assert (impact["production_route_before"], impact["production_route_after"]) == (1, 1)
    for field in (
        "production_route_delta", "new_generic_framework_count",
        "new_authority_layer_count", "new_production_route_count",
        "new_runtime_owner_count",
    ):
        assert impact[field] == 0
    assert reduction["infrastructure_amortization"]["did_hs_require_new_common_infrastructure"] is True
    assert reduction["required_metrics"]["INFRASTRUCTURE_AMORTIZATION_SIGNAL"]["status"] == "NOT_PROVEN"


def test_terminal_artifact_is_canonical_uniquely_keyed_and_sealed() -> None:
    envelope = load_unique(TERMINAL_PATH)
    assert TERMINAL_PATH.read_bytes() == HS_REDUCER.canonical_bytes(envelope)
    assert envelope["reduction_sha256"] == HS_REDUCER.sha256_bytes(
        HS_REDUCER.canonical_bytes(envelope["reduction"])
    )
    assert envelope["reduction"] == HS_REDUCER.terminal_reduction(ROOT)


def test_only_allowed_metric_status_vocabulary_is_used() -> None:
    allowed = {"VERIFIED", "ESTIMATED", "NOT_MEASURED", "NOT_PROVEN", "NOT_APPLICABLE"}
    reduction = load_unique(TERMINAL_PATH)["reduction"]
    for section in (reduction["required_metrics"], reduction["ccwim"]):
        for value in section.values():
            assert value["status"] in allowed


def test_reducer_has_no_operational_subprocess_or_authority_path() -> None:
    tree = ast.parse(REDUCER_PATH.read_text(encoding="utf-8"))
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
    forbidden_names = {"claim_and_invoke_once", "build_operation_context", "materialize_preboot_inputs"}
    assert not any(isinstance(node.func, ast.Name) and node.func.id in forbidden_names for node in calls)
    source = REDUCER_PATH.read_text(encoding="utf-8")
    assert "qemu-system" not in source
    assert "request_plugin_install" not in source


def test_g48_report_has_exactly_six_top_level_headings_and_failure_verdict() -> None:
    text = REPORT.read_text(encoding="utf-8")
    headings = [line for line in text.splitlines() if line.startswith("# ")]
    assert headings == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    for token in (
        "LAST_VERIFIED_EDGE", "FIRST_BROKEN_EDGE", "MINIMUM_MISSING_CAPABILITY",
        "MINIMUM_LEGAL_NEXT_DELTA", "EX_REUSED = 17/17", "EX_RECONSTRUCTED = 0",
        "E05_AFTER_HS = 8/18", "AUTO_CONTINUABLE = NO", "HUMAN_REVIEW_REQUIRED = YES",
    ):
        assert token in text


def test_index_remains_empty() -> None:
    assert subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True
    ).strip() == ""
