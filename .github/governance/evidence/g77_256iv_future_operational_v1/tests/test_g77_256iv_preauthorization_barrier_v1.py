#!/usr/bin/env python3
"""Focused Phase A Human-barrier validation for G77-256IV."""

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
IV = ROOT / ".github/governance/evidence/g77_256iv_future_operational_v1"
MATERIALIZER_PATH = IV / "orchestration/G77_256IV_PREAUTHORIZATION_MATERIALIZER_V1.py"
CONTROLLER_PATH = IV / "orchestration/G77_256IV_AUTHORITY_CONSUMPTION_CONTROLLER_V1.py"
REPORT_PATH = IV / "G77_256IV_G48_PHASE_A_HUMAN_AUTHORIZATION_BARRIER_REPORT_V1.md"


def load_module(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


M = load_module(MATERIALIZER_PATH, "g77_256iv_test_materializer")
C = load_module(CONTROLLER_PATH, "g77_256iv_test_controller")


def load_unique(path: Path) -> dict:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=M.unique_object)
    assert isinstance(value, dict)
    assert raw == M.canonical_bytes(value)
    return value


def test_exact_iu_entry_reconstruction_lineage_and_nested_authority() -> None:
    entry = M.authenticate_entry(M.HEAD, M.NESTED_HEAD)
    assert (entry["head"], entry["tree"], entry["subject"]) == (M.HEAD, M.TREE, M.SUBJECT)
    assert entry["local_remote_equality"] == "VERIFIED"
    assert set(entry["lineage"].values()) == {"VERIFIED"}
    assert entry["nested_authority"]["clean"] is True
    assert entry["nested_authority"]["detached"] is True
    iu = M.reconstruct_iu()
    assert iu["status"] == "VERIFIED__COMMITTED_OBJECT_RECONSTRUCTION"
    assert iu["terminal"] == "A__FUTURE_POST_COMMIT_FULL_STATIC_READINESS_VERIFIED"
    assert iu["ex_reused"] == "VERIFIED__17_OF_17"


def test_fresh_iv_identity_future_semantics_and_if_runtime_target() -> None:
    identity = M.derive_identity()
    assert identity["operation_generation"] == M.GENERATION
    assert identity["operation_identity"] == M.OPERATION
    assert identity["committed_history_collision"] == "VERIFIED__NO"
    assert identity["previous_authority_reuse"] == "VERIFIED__NO"
    future = M.authenticate_future_semantics()
    assert (future["evaluation"], future["valid_from"], future["valid_until"]) == (500, 600, 1000)
    assert future["future_semantic_mutation_count"] == 0
    assert future["wall_clock_dependency_count"] == 0


def test_operation_context_candidate_runtime_and_v2_role_separation() -> None:
    context = M.FM.fresh_context.load_context(
        IV / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json",
        repository_root=ROOT,
    )
    assert context["generation_identity"] == M.GENERATION
    assert context["operation_identity"] == M.OPERATION
    assert context["repository_head"] == M.HEAD and context["repository_tree"] == M.TREE
    candidate = IV / "live_binding/candidate/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json"
    runtime = IV / "live_binding/runtime_projection/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json"
    assert candidate.read_bytes() == runtime.read_bytes()
    assert M.sha256_path(candidate) == M.FUTURE_CANDIDATE_SHA
    eb = load_unique(IV / "live_binding/v2_readiness/bindings/G77_256IV_EB_RECEIPT_V2.json")["receipt"]
    ee = load_unique(IV / "live_binding/v2_readiness/bindings/G77_256IV_EE_RECEIPT_V2.json")["receipt"]
    assert eb["certification_baseline"] == {"head": M.HEAD, "tree": M.TREE}
    assert (eb["runtime_target_selection_binding"]["head"], eb["runtime_target_selection_binding"]["tree"]) == (M.IF_HEAD, M.IF_TREE)
    assert ee["certification_baseline"] == eb["certification_baseline"]
    assert ee["runtime_target_selection_binding"] == eb["runtime_target_selection_binding"]


def test_full_static_readiness_gl_and_exact_gn_presentation() -> None:
    static = load_unique(IV / "G77_256IV_PREAUTHORITY_STATIC_READINESS_V1.json")["proof"]
    assert static["readiness"]["result"] == "STATIC_READINESS_PASS"
    assert static["readiness"]["guest_adapter_binding"]["result"] == "PREAUTHORITY_GUEST_ADAPTER_BINDING_PASS"
    assert static["human_operational_authority"] == 0
    assert static["operational_execution_count"] == 0
    equivalence = load_unique(IV / "G77_256IV_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_V1.json")["proof"]
    assert equivalence["preauth_final_admission_equivalence"] == "VERIFIED_WITHIN_EXACT_REVIEWED_RECEIPT_PARENT_BOUNDARY"
    result = M.GN.validate_human_authorization_presentation(
        IV / "G77_256IV_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json",
        (IV / "G77_256IV_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt").read_bytes(),
    )
    assert result["human_presentation_request_equivalence"] == "VERIFIED_WITHIN_EXACT_REVIEWED_AUTHORIZATION_BINDING_BOUNDARY"
    assert result["operational_execution_count"] == 0


def test_phase_a_terminal_and_all_operational_counters_zero() -> None:
    envelope = load_unique(IV / "G77_256IV_PREHUMAN_PHASE_A_REDUCTION_V1.json")
    reduction = envelope["reduction"]
    assert envelope["reduction_sha256"] == hashlib.sha256(M.canonical_bytes(reduction)).hexdigest()
    assert reduction["terminal"] == "HUMAN_AUTHORIZATION_REQUIRED"
    assert reduction["authority_boundary"]["human_operational_authority"] == "VERIFIED__0"
    assert reduction["authority_boundary"]["authority_consumption"] == "VERIFIED__0"
    assert reduction["authority_boundary"]["auto_continuable"] is False
    assert reduction["authority_boundary"]["human_review_required"] is True
    counters = reduction["operational_counters"]
    assert counters["authorization_presentation"] == 1
    assert all(value == 0 for key, value in counters.items() if key != "authorization_presentation")
    assert reduction["e05"] == {"before": "10/18", "current": "10/18", "credit": 0, "remaining": 8}


def test_exact_human_action_is_bound_and_phase_a_snapshot_remains_zero() -> None:
    expected = (
        "I explicitly authorize G77-256IV request 21ea2f7ecf8a781c7033745f79a073bdfdd7c85da5f91997586815e0cd3972ff "
        "for operation G77_256IV_E05_FUTURE_DENIAL_BEFORE_ENTRY_001, candidate "
        "ad5d204ec6ace09f18b83fd5f868e73dac5e36dad81149f9f335c87f68cf42f7, context "
        "ef37bd1a77dbc87870e176f4542b0a5e358839b96dd1d8b6fd3d655ea188b6e9, and canonical argv "
        "141b1eb43c88dba58d51dde7baf8fa6a4bbb477784a6fed94c46e5b8d810fd95, starting from E05 10/18, "
        "subject to exactly one authority consumption, PRE, FM invocation, no-network QEMU, VM boot, and operation attempt, "
        "with zero retry, repair, replay, or protected effect.\n"
    )
    assert C.EXPECTED_NORMALIZED_GRANT == expected
    phase_a = load_unique(IV / "G77_256IV_PREHUMAN_PHASE_A_REDUCTION_V1.json")["reduction"]
    assert phase_a["authority_boundary"]["human_operational_authority"] == "VERIFIED__0"
    terminal = IV / "G77_256IV_SPCE_TERMINAL_REDUCTION_V1.json"
    if terminal.exists():
        assert C.GRANT_PATH.read_text(encoding="utf-8").replace("\\_", "_") == expected
        assert C.HANDOFF_PATH.exists() and C.SAFE_STOP_PATH.exists() and C.CONSUMPTION_PATH.exists()
    else:
        assert not C.GRANT_PATH.exists()
        assert not C.HANDOFF_PATH.exists()
        assert not C.SAFE_STOP_PATH.exists()
        assert not C.CONSUMPTION_PATH.exists()


def test_controller_fails_closed_before_duplicate_authority_or_operation() -> None:
    expected_error = RuntimeError if C.HANDOFF_PATH.exists() else FileNotFoundError
    with pytest.raises(expected_error):
        C.main(type("Args", (), {
            "capacity_read_at_utc": "NOT_USED",
            "primary_used_percent": 0,
            "secondary_used_percent": 0,
        })())
    context = load_unique(IV / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json")
    forbidden = [
        Path(context["pre_receipt_path"]), Path(context["post_receipt_path"]),
        Path(context["serial_path"]),
        *(Path(context["runtime_export_root"]) / relative for relative in context["guest_output_relative_paths"]),
    ]
    terminal = IV / "G77_256IV_SPCE_TERMINAL_REDUCTION_V1.json"
    if not terminal.exists():
        assert all(not path.exists() and not path.is_symlink() for path in forbidden)


def test_all_iv_json_is_canonical_unique_and_inner_sealed() -> None:
    for path in sorted(IV.rglob("*.json")):
        value = load_unique(path)
        for key, inner in (("reduction", "reduction_sha256"), ("proof", "proof_sha256"), ("checkpoint", "checkpoint_sha256"), ("request", "request_sha256"), ("observation", "observation_sha256")):
            if key in value and inner in value:
                assert value[inner] == hashlib.sha256(M.canonical_bytes(value[key])).hexdigest()


def test_ast_single_route_p11_and_historical_authority_firewalls() -> None:
    for path in IV.rglob("*.py"):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    assert "subprocess.run(argv" not in CONTROLLER_PATH.read_text(encoding="utf-8")
    assert subprocess.check_output(
        ["git", "diff", "--name-only", M.HEAD, "--", "aigol/runtime", "sapianta_system", ".github/governance/evidence/g77_256ec_p11_operational_v1"],
        cwd=ROOT, text=True,
    ).strip() == ""
    assert subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True).strip() == ""


def test_recovered_phase_a_inventory_remains_and_delta_is_iv_bounded() -> None:
    expected = {
        "G77_256IV_G48_PHASE_A_HUMAN_AUTHORIZATION_BARRIER_REPORT_V1.md",
        "G77_256IV_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_V1.json",
        "G77_256IV_GL_RECEIPT_PARENT_OBSERVATION_V1.json",
        "G77_256IV_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json",
        "G77_256IV_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt",
        "G77_256IV_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json",
        "G77_256IV_PREAUTHORITY_STATIC_READINESS_V1.json",
        "G77_256IV_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json",
        "G77_256IV_PREHUMAN_PHASE_A_REDUCTION_V1.json",
        "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json",
        "live_binding/candidate/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json",
        "live_binding/runtime_projection/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json",
        "live_binding/v2_readiness/bindings/G77_256IV_EB_RECEIPT_V2.json",
        "live_binding/v2_readiness/bindings/G77_256IV_EE_PATH_PROJECTION_FIXTURE_V1.py",
        "live_binding/v2_readiness/bindings/G77_256IV_EE_RECEIPT_V2.json",
        "live_binding/v2_readiness/candidate/G77_256IV_V2_READINESS_CANDIDATE_V2.json",
        "live_binding/v2_readiness/runtime_projection/G77_256IV_V2_READINESS_CANDIDATE_V2.json",
        "operation_state/guest_harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py",
        "operation_state/guest_harness/G77_256IV_FUTURE_VECTOR_ADAPTER_V1.py",
        "operation_state/runtime_export/G77_256IV_CONTINUATION_MANIFEST_V1.json",
        "operation_state/runtime_export/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json",
        "orchestration/G77_256IV_AUTHORITY_CONSUMPTION_CONTROLLER_V1.py",
        "orchestration/G77_256IV_PREAUTHORIZATION_MATERIALIZER_V1.py",
        "tests/test_g77_256iv_preauthorization_barrier_v1.py",
    }
    observed = {
        path.relative_to(IV).as_posix()
        for path in IV.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }
    assert expected <= observed
    status = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT,
        text=True,
    ).splitlines()
    assert len(status) == len(observed)
    assert all(line.startswith("?? ") and str(IV.relative_to(ROOT)) in line for line in status)


def test_g48_exact_six_headings_and_required_metrics() -> None:
    text = REPORT_PATH.read_text(encoding="utf-8")
    assert [line for line in text.splitlines() if line.startswith("# ")] == [
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
        "REPOSITORY_DERIVED_EXECUTION_CONTEXT_RATIO", "CONSTITUTIONAL_PROMPT_EXTERNALIZATION_RATIO",
        "TOKEN_BENCHMARK", "LLM_COST_REDUCTION_RATIO", "LCRR",
        "E05_GENERATIONS_PER_CREDIT", "OPERATIONAL_ATTEMPTS_PER_CREDIT",
        "MARGINAL_E05_GENERATION_COST", "MARGINAL_NEW_INFRASTRUCTURE_PER_E05_CREDIT",
        "INFRASTRUCTURE_AMORTIZATION_SIGNAL", "EXPECTED_NEXT_CREDIT_GENERATION_COUNT",
        "SAME_GENERATION_RECOVERY", "PROVIDER_LIMIT_INTERRUPTION_RECOVERED",
        "UNCOMMITTED_DELTA_RECOVERY", "AUTHORITY_STATE_RECOVERY",
        "RECOVERED_IV_FILE_COUNT", "RECOVERED_AUTHORING_FILE_LINE_TOTAL",
    }
    assert all(token in text for token in required)
