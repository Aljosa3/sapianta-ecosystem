from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
II_ROOT = ROOT / ".github/governance/evidence/g77_256ii_runtime_certification_contract_resolution_v1"
RESOLVER = II_ROOT / "analysis/G77_256II_RUNTIME_CERTIFICATION_CONTRACT_RESOLVER_V1.py"
TERMINAL = II_ROOT / "G77_256II_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = II_ROOT / "G77_256II_G48_IMPLEMENTATION_REPORT_V1.md"


def _load_resolver():
    specification = importlib.util.spec_from_file_location("g77_256ii_resolver", RESOLVER)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


II = _load_resolver()


def test_exact_ih_entry_nested_authority_and_continuation_recovery() -> None:
    entry = II.authenticate_entry(ROOT)
    assert (entry["head"], entry["tree"], entry["remote_tracking_head"]) == (II.IH_HEAD, II.IH_TREE, II.IH_HEAD)
    assert entry["index"] == ""
    assert entry["nested"]["head"] == II.NESTED_HEAD
    assert entry["nested"]["branch"] == entry["nested"]["status"] == ""
    assert entry["continuation_recovery"]["resolver"].startswith("PARTIALLY_COMPLETED_BEFORE_INTERRUPTION")
    assert entry["continuation_recovery"]["unrelated_repository_delta_count"] == "VERIFIED__0"


def test_committed_ih_is_reconstructed_by_exact_hash_and_terminal_seal() -> None:
    reconstructed = II.reconstruct_ih(ROOT)
    assert reconstructed["status"] == "VERIFIED"
    assert len(reconstructed["identities"]) == 9
    assert reconstructed["frontier"]["current_e05_status"] == "VERIFIED__10_OF_18"
    assert reconstructed["frontier"]["e05_credit"] == "VERIFIED__0"


def test_post_ih_structural_conflict_is_reproduced_without_receipts() -> None:
    conflict = II.reproduce_post_ih_conflict(ROOT)
    assert conflict["if_as_shared_baseline"] == {
        "du": "VERIFIED__CURRENT_IF_BOUND",
        "eb": "REQUIRED_HEAD_MISMATCH",
        "ee": "REQUIRED_HEAD_MISMATCH",
    }
    assert conflict["ih_as_shared_baseline"] == {
        "eb": "REQUIRED_HEAD_MISMATCH",
        "ee_git": "UNEXPECTED_PASS",
        "ee_candidate": "CANDIDATE_REQUIRED_HEAD_MISMATCH",
    }
    assert conflict["post_ih_commit_eb_ee_conflict"] == "VERIFIED__PERSISTS"
    assert conflict["precommit_only_conflict_hypothesis"] == "VERIFIED__FALSE"
    assert conflict["eb_receipt_created"] is conflict["ee_receipt_created"] is False


def test_identity_contract_matrix_has_six_distinct_roles_and_equalities() -> None:
    matrix = II.identity_contract_matrix()
    assert [row["identity"] for row in matrix] == [
        "TARGET_RUNTIME_IDENTITY",
        "CURRENT_REPOSITORY_IDENTITY",
        "CERTIFICATION_BASELINE_IDENTITY",
        "CANDIDATE_REQUIRED_IDENTITY",
        "CHECKOUT_IDENTITY",
        "EVIDENCE_ISSUER_IDENTITY",
    ]
    assert all("coupling_origin" in row for row in matrix)
    target_roles = {row["identity"] for row in matrix if row["equals_target_head"]}
    current_roles = {row["identity"] for row in matrix if row["equals_current_head"]}
    assert target_roles == {"TARGET_RUNTIME_IDENTITY", "CANDIDATE_REQUIRED_IDENTITY", "CHECKOUT_IDENTITY"}
    assert current_roles == {"CURRENT_REPOSITORY_IDENTITY", "CERTIFICATION_BASELINE_IDENTITY", "EVIDENCE_ISSUER_IDENTITY"}


def test_authoritative_owner_trace_proves_implementation_coupling_only() -> None:
    trace = II.authenticate_owner_trace(ROOT)
    assert len(trace["owners"]) == 10
    assert trace["observed_cross_role_coupling"] == "VERIFIED__IMPLEMENTATION_DERIVED"
    assert trace["coupling_classification"] == "VERIFIED__IMPLEMENTATION_COUPLING"
    assert trace["identity_coupling_status"] == "NOT_PROVEN__NO_UNIQUE_GOVERNED_CONTRACT_SEPARATION"
    assert trace["chronology"] == "VERIFIED__DU_EB_EE_PRECEDE_DETACHED_FUTURE_TARGET"
    assert {item["classification"] for item in trace["equalities"]} >= {
        "RUNTIME_TARGET_INVARIANT", "CERTIFICATION_CURRENTNESS_INVARIANT", "HISTORICAL_COUPLING"
    }


def test_option_e_is_only_selected_fail_closed_resolution() -> None:
    options = II.resolution_options()
    selected = [key for key, value in options.items() if value["constitutional_status"] == "VERIFIED__SELECTED_FAIL_CLOSED"]
    assert selected == ["OPTION_E"]
    assert options["OPTION_A"]["new_schema_required"] is True
    assert all(options[key]["constitutional_status"].startswith("NOT_PROVEN") for key in ("OPTION_A", "OPTION_B", "OPTION_C", "OPTION_D"))
    assert all(options[key]["p11_change_required"] is False for key in options)


def test_future_candidate_runtime_context_and_time_are_preserved() -> None:
    future = II.preserve_future_state(ROOT)
    assert future["candidate_identity"] == future["runtime_identity"] == "ad5d204ec6ace09f18b83fd5f868e73dac5e36dad81149f9f335c87f68cf42f7"
    assert future["context_identity"] == "769f7b5cde5946450acbecfd956d479e91d9cf818d47bd4db34cb5086a1b07cb"
    assert future["candidate_required_identity"] == future["checkout_identity"] == {"head": II.IF_HEAD, "tree": II.IF_TREE}
    assert (future["evaluation_time_unix_ns"], future["valid_from_unix_ns"], future["valid_until_unix_ns"]) == (500, 600, 1000)
    assert future["wall_clock_dependency_count_on_future_path"] == "VERIFIED__0"
    assert future["production_route_delta"] == "VERIFIED__0"


def test_ex_common_substrate_is_reused_not_reconstructed() -> None:
    assert II.authenticate_ex(ROOT) == {
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
        "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED",
    }


def test_terminal_reduction_is_fail_closed_and_operationally_zero() -> None:
    reduction = II.terminal_reduction(ROOT)
    control = reduction["terminal_control"]
    assert reduction["resolution"]["selected_option"] == "OPTION_E"
    assert control["runtime_certification_identity_contract"].startswith("NOT_PROVEN")
    assert control["future_preoperational_readiness"].startswith("NOT_PROVEN")
    assert control["next_operational_generation_eligible"] == "NOT_PROVEN"
    assert control["auto_continuable"] is control["human_authorization_required"] is control["next_generation_started"] is False
    assert control["human_review_required"] is True
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["e05"] == {"before": "10/18", "after": "10/18", "satisfied": 10, "remaining": 8, "credit": 0}


def test_generality_bypass_route_and_owner_firewalls_remain_closed() -> None:
    reduction = II.terminal_reduction(ROOT)
    resolution = reduction["resolution"]
    reuse = reduction["reuse_impact"]
    assert resolution["arbitrary_historical_head_bypass"] == "VERIFIED__NO"
    assert resolution["current_head_provenance_weakening"] == "VERIFIED__NO"
    assert resolution["vector_specific_certification_bypass"] == "VERIFIED__NO"
    assert resolution["pre_commit_self_reference_count"] == resolution["future_commit_prediction_count"] == "VERIFIED__0"
    for key in ("new_generic_framework_count", "new_authority_layer_count", "new_production_route_count", "new_runtime_owner_count", "new_clock_infrastructure_count", "p11_core_change_count"):
        assert reuse[key] == "VERIFIED__0"
    assert reuse["production_route_before"] == reuse["production_route_after"] == "VERIFIED__1"
    assert reuse["production_route_delta"] == "VERIFIED__0"


def test_gn_gl_historical_firewall_and_ccwim_are_explicit() -> None:
    reduction = II.terminal_reduction(ROOT)
    assert all(value.startswith("NOT_APPLICABLE") for value in reduction["gn_gl"].values())
    assert reduction["historical_failure_firewall"]["reintroduced_historical_failure_count"] == "VERIFIED__0"
    assert reduction["ccwim"]["ccwim_maturity_level"] == "ESTIMATED__L4_LIKE__NO_L5_CLAIM"
    assert reduction["ccwim"]["uncommitted_delta_recovery"] == "VERIFIED__EXISTING_II_RESOLVER_AUTHENTICATED_AND_REUSED"
    assert reduction["ccwim"]["same_generation_continuation_status"].startswith("ESTIMATED__USER_SUPPLIED")
    assert reduction["ccwim"]["handoff_ambiguity_count"] == "VERIFIED__0"


def test_terminal_artifact_is_canonical_duplicate_safe_and_sealed() -> None:
    raw = TERMINAL.read_bytes()
    envelope = II.load_canonical(TERMINAL)
    assert raw == II.canonical_bytes(envelope)
    assert envelope["reduction_sha256"] == II.sha256_bytes(II.canonical_bytes(envelope["reduction"]))
    assert envelope == II.terminal_envelope(ROOT)


def test_duplicate_json_keys_fail_closed(tmp_path: Path) -> None:
    invalid = tmp_path / "duplicate.json"
    invalid.write_text('{"a":1,"a":2}\n')
    with pytest.raises(II.IIResolutionError, match="DUPLICATE_JSON_KEY"):
        II.load_canonical(invalid)


def test_python_ast_and_repository_mutation_scope() -> None:
    tree = ast.parse(RESOLVER.read_text())
    assert any(isinstance(node, ast.FunctionDef) and node.name == "terminal_reduction" for node in ast.walk(tree))
    status = subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=all"], cwd=ROOT, text=True).splitlines()
    assert status
    assert all(line[3:].startswith(II_ROOT.relative_to(ROOT).as_posix() + "/") for line in status)
    assert subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True) == ""


def test_g48_report_has_exactly_six_required_top_level_headings() -> None:
    headings = [line for line in REPORT.read_text().splitlines() if line.startswith("# ")]
    assert headings == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
