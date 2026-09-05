from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
import subprocess
import sys

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
IJ_ROOT = ROOT / ".github/governance/evidence/g77_256ij_successor_contract_design_v1"
RESOLVER = IJ_ROOT / "design/G77_256IJ_DU_EB_EE_SUCCESSOR_CONTRACT_DESIGN_RESOLVER_V1.py"
TERMINAL = IJ_ROOT / "G77_256IJ_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = IJ_ROOT / "G77_256IJ_G48_IMPLEMENTATION_REPORT_V1.md"


def _load():
    specification = importlib.util.spec_from_file_location("g77_256ij_design", RESOLVER)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


IJ = _load()


def test_exact_ii_entry_ancestry_and_nested_authority() -> None:
    entry = IJ.authenticate_entry(ROOT)
    assert (entry["head"], entry["tree"], entry["remote_tracking_head"]) == (IJ.II_HEAD, IJ.II_TREE, IJ.II_HEAD)
    assert entry["index"] == ""
    assert entry["nested"]["head"] == IJ.NESTED_HEAD
    assert entry["nested"]["branch"] == entry["nested"]["status"] == ""


def test_committed_ii_artifacts_terminal_and_option_e_reconstruct() -> None:
    result = IJ.reconstruct_ii(ROOT)
    assert result["status"] == "VERIFIED"
    assert len(result["identities"]) == 4
    assert result["frontier"]["current_e05_status"] == "VERIFIED__10_OF_18"
    assert result["frontier"]["runtime_certification_identity_contract"].startswith("NOT_PROVEN")
    assert result["option_e"] == "VERIFIED__SELECTED_FAIL_CLOSED"


def test_v1_owners_closed_schemas_and_reviewed_successor_rule_authenticate() -> None:
    evidence = IJ.authenticate_owners(ROOT)
    assert len(evidence["owner_hashes"]) == 10
    assert evidence["v1_closed_schema_status"] == "VERIFIED"
    assert evidence["reviewed_successor_rule"].startswith("VERIFIED__DU_REQUIRES")


def test_six_identity_roles_and_current_target_noncollapse_are_preserved() -> None:
    model = IJ.identity_model()
    assert [row["identity"] for row in model] == [
        "TARGET_RUNTIME_IDENTITY", "CURRENT_REPOSITORY_IDENTITY",
        "CERTIFICATION_BASELINE_IDENTITY", "CANDIDATE_REQUIRED_IDENTITY",
        "CHECKOUT_IDENTITY", "EVIDENCE_ISSUER_IDENTITY",
    ]
    assert {row["identity"] for row in model if row["target_head_required"]} == {
        "TARGET_RUNTIME_IDENTITY", "CANDIDATE_REQUIRED_IDENTITY", "CHECKOUT_IDENTITY"
    }
    assert {row["identity"] for row in model if row["current_head_required"]} == {
        "CURRENT_REPOSITORY_IDENTITY", "CERTIFICATION_BASELINE_IDENTITY", "EVIDENCE_ISSUER_IDENTITY"
    }


def test_semantic_minimum_is_two_fields_but_concrete_schema_is_not_unique() -> None:
    minimum = IJ.schema_minimality()
    assert minimum["minimum_new_semantic_field_count"] == 2
    assert minimum["minimum_new_schema_coordinate_set"] == ["certification_baseline_head", "certification_baseline_tree"]
    assert minimum["required_nonidentity_structural_binding"] == "runtime_target_selection_binding"
    assert minimum["deprecated_v1_coordinate_set"] == []
    assert len(minimum["alternatives"]) == 3
    assert minimum["schema_uniqueness"].startswith("NOT_PROVEN")
    assert minimum["generic_identity_framework_created"] == "VERIFIED__NO"


def test_successor_requirements_separate_only_historical_cross_role_equality() -> None:
    design = IJ.successor_contract_design()
    assert design["logical_fields"]["runtime_target_commit"] == "DU.manifest.required_head"
    assert design["logical_fields"]["certification_current_commit"] == "successor.certification_baseline_head"
    assert len(design["mandatory_equalities"]) == 9
    assert "NO_LONGER_REQUIRED_TO_EQUAL" in design["intentionally_separated_v1_equality"]
    assert design["equal_and_unequal_targets_supported"] == "VERIFIED__DESIGN_SUPPORTS_BOTH"
    assert design["successor_contract_design_status"].startswith("NOT_PROVEN")


def test_owner_assignments_are_unique_and_complete_at_design_level() -> None:
    owners = IJ.owner_model()
    assert len(owners["coordinates"]) == 6
    assert owners["owner_uniqueness_status"] == "VERIFIED__DESIGN_ASSIGNMENTS_UNIQUE"
    assert owners["owner_conflict_count"] == owners["unowned_semantic_coordinate_count"] == "VERIFIED__0"


def test_runtime_target_selection_and_currentness_firewalls_authenticate() -> None:
    result = IJ.target_and_currentness_firewalls(ROOT)
    assert result["runtime_target"] == {"head": IJ.IF_HEAD, "tree": IJ.IF_TREE}
    assert result["current_certification"] == {"head": IJ.II_HEAD, "tree": IJ.II_TREE}
    assert result["runtime_target_provenance_authentication"].startswith("VERIFIED__FM_LAUNCHER")
    assert result["caller_chosen_runtime_target_authority"] == "VERIFIED__NO"
    assert result["arbitrary_historical_head_bypass"] == "VERIFIED__NO"
    assert result["current_head_provenance_weakening"] == result["current_tree_provenance_weakening"] == "VERIFIED__NO"


def test_generality_matrix_accepts_both_identity_relations_and_rejects_all_faults() -> None:
    matrix = IJ.generality_matrix()
    assert len(matrix) == 12
    decisions = {row["case"]: row["observed"] for row in matrix}
    assert decisions["TARGET_EQUALS_CURRENT"].startswith("ACCEPT__DESIGN_CONTRACT_ONLY")
    assert decisions["TARGET_DIFFERS_CURRENT_AUTHENTICATED"].startswith("ACCEPT__DESIGN_CONTRACT_ONLY")
    assert decisions["FUTURE_VECTOR_AUTHENTICATED_IF"].startswith("ACCEPT__DESIGN_CONTRACT_ONLY")
    assert decisions["NON_FUTURE_CURRENT_TARGET"].startswith("ACCEPT__DESIGN_CONTRACT_ONLY")
    assert all(value.startswith("REJECT__") for key, value in decisions.items() if key not in {"TARGET_EQUALS_CURRENT", "TARGET_DIFFERS_CURRENT_AUTHENTICATED", "FUTURE_VECTOR_AUTHENTICATED_IF", "NON_FUTURE_CURRENT_TARGET"})


def test_versioning_preserves_v1_and_leaves_dispatch_unimplemented() -> None:
    result = IJ.versioning_and_compatibility()
    assert result["successor_contract_versioning"].startswith("VERIFIED__NEW_REVIEWED_INCOMPATIBLE_VERSION_REQUIRED")
    assert result["v1_semantics_reinterpreted"] == "VERIFIED__NO"
    assert result["historical_v1_mutation_count"] == "VERIFIED__0"
    assert result["runtime_version_dispatch_implemented"] is False
    assert result["version_dispatch_bypass_risk"].startswith("NOT_PROVEN")
    assert result["parallel_production_flow_risk"].startswith("VERIFIED__NO")


def test_successor_responsibilities_do_not_expand_p11_or_issuer_coordinates() -> None:
    responsibilities = IJ.successor_responsibilities()
    assert set(responsibilities) == {"DU_SUCCESSOR", "EB_SUCCESSOR", "EE_SUCCESSOR", "EVIDENCE_ISSUER_EXPLICIT_FIELD_REQUIRED", "P11_CHANGE_REQUIRED"}
    assert responsibilities["P11_CHANGE_REQUIRED"] == "VERIFIED__NO"
    assert responsibilities["EVIDENCE_ISSUER_EXPLICIT_FIELD_REQUIRED"].startswith("NOT_APPLICABLE")


def test_future_semantics_and_ex_reuse_are_unchanged() -> None:
    future = IJ.preserve_future_semantics(ROOT)
    assert future["candidate_runtime_identity"] == IJ.FUTURE_CANDIDATE_SHA
    assert future["context_identity"] == IJ.FUTURE_CONTEXT_INNER
    assert (future["evaluation_time_unix_ns"], future["valid_from_unix_ns"], future["valid_until_unix_ns"]) == (500, 600, 1000)
    assert future["future_semantic_mutation_count"] == future["wall_clock_dependency_count_on_future_path"] == "VERIFIED__0"
    assert IJ.authenticate_ex(ROOT)["ex_reused"] == "VERIFIED__17_OF_17"


def test_terminal_is_fail_closed_operationally_zero_and_e05_unchanged() -> None:
    reduction = IJ.terminal_reduction(ROOT)
    control = reduction["terminal_control"]
    assert control["successor_contract_design_status"].startswith("NOT_PROVEN")
    assert control["schema_uniqueness"].startswith("NOT_PROVEN")
    assert control["minimum_legal_next_delta"] == "HUMAN_GOVERNANCE_DECISION_REQUIRED"
    assert control["future_preoperational_readiness"] == control["future_operational_capability"] == control["next_operational_generation_eligible"] == "NOT_PROVEN"
    assert control["auto_continuable"] is control["human_authorization_required"] is control["next_generation_started"] is False
    assert control["human_review_required"] is True
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["e05"] == {"before": "10/18", "after": "10/18", "satisfied": 10, "remaining": 8, "credit": 0}


def test_terminal_artifact_is_canonical_duplicate_safe_and_sealed() -> None:
    envelope = IJ.load_canonical(TERMINAL)
    assert TERMINAL.read_bytes() == IJ.canonical_bytes(envelope)
    assert envelope["reduction_sha256"] == IJ.sha256_bytes(IJ.canonical_bytes(envelope["reduction"]))
    assert envelope == IJ.terminal_envelope(ROOT)


def test_duplicate_keys_ast_report_and_mutation_scope(tmp_path: Path) -> None:
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text('{"x":1,"x":2}\n')
    with pytest.raises(IJ.IJDesignError, match="DUPLICATE_JSON_KEY"):
        IJ.load_canonical(duplicate)
    tree = ast.parse(RESOLVER.read_text())
    assert any(isinstance(node, ast.FunctionDef) and node.name == "terminal_reduction" for node in ast.walk(tree))
    headings = [line for line in REPORT.read_text().splitlines() if line.startswith("# ")]
    assert headings == ["# 1. Implementation Summary", "# 2. Code Evidence", "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix", "# 5. Repository Mutation Summary", "# 6. Certification Verdict"]
    status = subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=all"], cwd=ROOT, text=True).splitlines()
    assert status and all(line[3:].startswith(IJ_ROOT.relative_to(ROOT).as_posix() + "/") for line in status)
    assert subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True) == ""
