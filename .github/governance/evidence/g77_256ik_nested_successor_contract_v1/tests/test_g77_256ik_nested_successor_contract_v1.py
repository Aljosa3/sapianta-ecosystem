from __future__ import annotations

import ast
from dataclasses import replace
import importlib.util
from pathlib import Path
import subprocess
import sys

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
IK_ROOT = ROOT / ".github/governance/evidence/g77_256ik_nested_successor_contract_v1"
FORMALIZER = IK_ROOT / "design/G77_256IK_NESTED_SUCCESSOR_CONTRACT_FORMALIZER_V1.py"
TERMINAL = IK_ROOT / "G77_256IK_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = IK_ROOT / "G77_256IK_G48_IMPLEMENTATION_REPORT_V1.md"


def _load():
    spec = importlib.util.spec_from_file_location("g77_256ik_formalizer", FORMALIZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


IK = _load()


def test_exact_ij_entry_ancestry_and_nested_authority() -> None:
    entry = IK.authenticate_entry(ROOT)
    assert (entry["head"], entry["tree"], entry["remote_tracking_head"]) == (IK.IJ_HEAD, IK.IJ_TREE, IK.IJ_HEAD)
    assert entry["index"] == ""
    assert entry["nested"]["head"] == IK.NESTED_HEAD
    assert entry["nested"]["branch"] == entry["nested"]["status"] == ""


def test_committed_ij_bytes_blobs_canonical_seal_and_frontier_reconstruct() -> None:
    result = IK.reconstruct_ij(ROOT)
    assert result["status"] == "VERIFIED"
    assert result["artifact_count"] == 4
    assert result["inner_seal"] == "VERIFIED"
    assert result["frontier"]["current_e05_status"] == "VERIFIED__10_OF_18"
    assert result["frontier"]["schema_uniqueness"].startswith("NOT_PROVEN")


def test_human_decision_is_option_b_and_not_operational_authority() -> None:
    decision = IK.human_governance_decision()
    assert decision["human_governance_schema_selection"].startswith("B__NESTED")
    assert decision["human_selected_logical_schema"] == "VERIFIED__OPTION_B_NESTED_CERTIFICATION_BASELINE"
    assert decision["human_operational_authority"] == "VERIFIED__0"
    assert decision["future_operation_authorized"] == decision["e05_credit_authorized"] == "VERIFIED__NO"


def test_repository_conventions_uniquely_bind_physical_shape_but_not_version() -> None:
    result = IK.authenticate_conventions(ROOT)
    assert result["exact_physical_field_names"] == {"object": "certification_baseline", "commit": "head", "tree": "tree"}
    assert result["exact_physical_field_names_status"] == "VERIFIED"
    assert result["successor_version_required"] == "VERIFIED__YES"
    assert result["successor_version_identifier"] == "NOT_PROVEN__NO_UNIQUE_REPOSITORY_CONVENTION"
    assert len(result["ambiguity_proof"]) == 4


def test_nested_certification_baseline_is_closed_typed_and_exactly_two_coordinates() -> None:
    baseline = {"head": IK.IJ_HEAD, "tree": IK.IJ_TREE}
    assert IK.validate_certification_baseline(baseline) == baseline
    schema = IK.schema_contract()
    assert schema["minimum_new_semantic_field_count"] == "VERIFIED__2"
    assert schema["minimum_new_coordinates"] == ["certification_baseline.head", "certification_baseline.tree"]
    assert schema["binding_is_third_git_coordinate"] is False
    for invalid in (
        None,
        {"head": IK.IJ_HEAD},
        {"head": IK.IJ_HEAD, "tree": IK.IJ_TREE, "extra": "x"},
        {"head": 1, "tree": IK.IJ_TREE},
        {"head": "A" * 40, "tree": IK.IJ_TREE},
        {"head": IK.IJ_HEAD, "tree": "0" * 39},
    ):
        with pytest.raises(IK.IKFormalizationError):
            IK.validate_certification_baseline(invalid)


def test_current_certification_is_git_owned_and_stale_or_wrong_tree_rejects() -> None:
    assert IK.authenticate_certification_currentness(ROOT, {"head": IK.IJ_HEAD, "tree": IK.IJ_TREE}).startswith("VERIFIED")
    with pytest.raises(IK.IKFormalizationError, match="NOT_CURRENT"):
        IK.authenticate_certification_currentness(ROOT, {"head": IK.II_HEAD, "tree": IK.IJ_TREE})
    with pytest.raises(IK.IKFormalizationError, match="NOT_CURRENT"):
        IK.authenticate_certification_currentness(ROOT, {"head": IK.IJ_HEAD, "tree": IK.IF_TREE})


def test_version_schema_validator_profile_issuer_consumer_binding_is_exact() -> None:
    bound = IK.VersionBinding("SCHEMA_SUCCESSOR", "SUCCESSOR_VERSION", "VALIDATOR_SUCCESSOR", "PROFILE_SUCCESSOR", "ISSUER_SUCCESSOR", "CONSUMER_SUCCESSOR")
    assert IK.validate_version_binding(bound, bound).startswith("VERIFIED")
    fields = ("schema_identity", "version", "validator_identity", "receipt_profile", "issuer_implementation_identity", "consumer_expectation")
    for field in fields:
        with pytest.raises(IK.IKFormalizationError, match="MISMATCH"):
            IK.validate_version_binding(replace(bound, **{field: getattr(bound, field) + "_SUBSTITUTED"}), bound)


def test_unknown_mixed_downgrade_and_caller_selected_versions_fail_closed() -> None:
    bound = IK.VersionBinding("S", "V", "X", "P", "I", "C")
    for kwargs, code in (
        ({"mixed_v1_successor_fields": True}, "MIXED_VERSION"),
        ({"caller_selected": True}, "CALLER_VERSION_SELECTION"),
        ({"downgrade": True}, "VERSION_DOWNGRADE"),
    ):
        with pytest.raises(IK.IKFormalizationError, match=code):
            IK.validate_version_binding(bound, bound, **kwargs)


def test_owner_model_is_unique_complete_and_issuer_field_remains_unneeded() -> None:
    model = IK.identity_and_owner_model()
    assert len(model["identity_roles"]) == 6
    assert len(model["fields"]) == 7
    assert model["owner_uniqueness_status"] == "VERIFIED__DESIGN_ASSIGNMENTS_UNIQUE"
    assert model["owner_conflict_count"] == model["unowned_semantic_coordinate_count"] == "VERIFIED__0"
    assert model["evidence_issuer_explicit_field_required"].startswith("NOT_APPLICABLE")
    assert all(set(row) == {"field", "semantic_role", "producer", "authority_source", "validator", "consumer", "mandatory_equality", "failure_mode"} for row in model["fields"])


def test_du_eb_ee_responsibilities_preserve_ee_independence_and_p11_boundary() -> None:
    result = IK.successor_responsibilities()
    assert "independent_DU_successor_PASS" in result["EB_SUCCESSOR"]
    assert "independent_EB_successor_receipt" in result["EE_SUCCESSOR"]
    assert "independent_certification_currentness_reauthentication" in result["EE_SUCCESSOR"]
    assert result["P11_CHANGE_REQUIRED"] == "VERIFIED__NO"


def test_runtime_target_and_current_certification_provenance_both_authenticate() -> None:
    result = IK.authenticate_provenance(ROOT)
    assert result["runtime_target"] == {"head": IK.IF_HEAD, "tree": IK.IF_TREE}
    assert result["current_certification"] == {"head": IK.IJ_HEAD, "tree": IK.IJ_TREE}
    assert result["runtime_target_provenance_authentication"].startswith("VERIFIED__FM_LAUNCHER")
    assert result["runtime_target_selection_binding"] == "VERIFIED__AUTHENTICATED"
    assert result["arbitrary_historical_head_bypass"] == "VERIFIED__NO"
    assert result["certification_baseline_caller_authority"] == "VERIFIED__NO"
    assert result["currentness_validation_in_both_cases"] == "VERIFIED"


def test_generality_matrix_covers_required_cases_and_rejects_every_fault() -> None:
    matrix = IK.generality_matrix()
    assert len(matrix) == 21
    results = {row["case"]: row["observed"] for row in matrix}
    accepted = {"TARGET_EQUALS_CURRENT", "AUTHENTICATED_TARGET_DIFFERS_CURRENT", "FUTURE_VECTOR", "NON_FUTURE_APPLICABLE_VECTOR"}
    assert all(results[name].startswith("REPRESENTABLE__CONTRACT_ONLY") for name in accepted)
    assert all(result.startswith("REJECT__") for name, result in results.items() if name not in accepted)
    assert results["ARBITRARY_HISTORICAL_TARGET"] == "REJECT__UNAUTHENTICATED_TARGET_SELECTION"
    assert results["MIXED_V1_SUCCESSOR_RECEIPT"] == "REJECT__MIXED_VERSION"
    assert results["VERSION_DOWNGRADE"] == "REJECT__DOWNGRADE"


def test_future_vector_semantics_are_unchanged_and_vector_neutral() -> None:
    result = IK.preserve_future_semantics(ROOT)
    assert result["candidate_runtime_identity"] == IK.FUTURE_CANDIDATE_SHA
    assert result["context_identity"] == IK.FUTURE_CONTEXT_SHA
    assert (result["evaluation_time"], result["valid_from"], result["valid_until"]) == (500, 600, 1000)
    assert result["future_semantic_mutation_count"] == result["wall_clock_dependency_count"] == "VERIFIED__0"


def test_ex_is_reused_without_reconstruction() -> None:
    assert IK.authenticate_ex(ROOT) == {"ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0", "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED"}


def test_implementation_frontier_fails_closed_at_unratified_version_namespace() -> None:
    frontier = IK.implementation_frontier()
    assert len(frontier["minimum_successor_implementation_owner_set"]) == 5
    assert frontier["minimum_successor_implementation_file_set"].startswith("NOT_PROVEN")
    assert frontier["expected_production_route_delta"] == frontier["expected_p11_delta"] == frontier["expected_fm_runtime_delta"] == frontier["expected_gn_gl_delta"] == "VERIFIED__0"


def test_terminal_b_is_operationally_zero_and_e05_unchanged() -> None:
    reduction = IK.terminal_reduction(ROOT)
    control = reduction["terminal_control"]
    assert control["human_governance_schema_selection"] == "VERIFIED__OPTION_B"
    assert control["successor_version_identifier"].startswith("NOT_PROVEN")
    assert control["minimum_legal_next_delta"] == "HUMAN_GOVERNANCE_DECISION_REQUIRED"
    assert control["future_preoperational_readiness"] == control["future_operational_capability"] == control["next_operational_generation_eligible"] == "NOT_PROVEN"
    assert control["auto_continuable"] is control["human_authorization_required"] is control["next_generation_started"] is False
    assert control["human_review_required"] is True
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["e05"] == {"before": "10/18", "after": "10/18", "satisfied": 10, "remaining": 8, "credit": 0}


def test_terminal_is_canonical_duplicate_safe_and_inner_sealed(tmp_path: Path) -> None:
    envelope = IK.load_canonical(TERMINAL)
    assert TERMINAL.read_bytes() == IK.canonical_bytes(envelope)
    assert envelope["reduction_sha256"] == IK.sha256_bytes(IK.canonical_bytes(envelope["reduction"]))
    assert envelope == IK.terminal_envelope(ROOT)
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text('{"x":1,"x":2}\n')
    with pytest.raises(IK.IKFormalizationError, match="DUPLICATE_JSON_KEY"):
        IK.load_canonical(duplicate)


def test_ast_report_exact_headings_and_mutation_scope() -> None:
    tree = ast.parse(FORMALIZER.read_text())
    assert any(isinstance(node, ast.FunctionDef) and node.name == "terminal_reduction" for node in ast.walk(tree))
    headings = [line for line in REPORT.read_text().splitlines() if line.startswith("# ")]
    assert headings == ["# 1. Implementation Summary", "# 2. Code Evidence", "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix", "# 5. Repository Mutation Summary", "# 6. Certification Verdict"]
    status = subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=all"], cwd=ROOT, text=True).splitlines()
    assert status and all(line[3:].startswith(IK_ROOT.relative_to(ROOT).as_posix() + "/") for line in status)
    assert subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True) == ""
