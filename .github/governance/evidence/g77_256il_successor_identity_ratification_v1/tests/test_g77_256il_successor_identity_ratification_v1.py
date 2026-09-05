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
IL_ROOT = ROOT / ".github/governance/evidence/g77_256il_successor_identity_ratification_v1"
FORMALIZER = IL_ROOT / "design/G77_256IL_SUCCESSOR_IDENTITY_RATIFICATION_FORMALIZER_V1.py"
TERMINAL = IL_ROOT / "G77_256IL_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = IL_ROOT / "G77_256IL_G48_IMPLEMENTATION_REPORT_V1.md"


def _load():
    spec = importlib.util.spec_from_file_location("g77_256il_formalizer", FORMALIZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


IL = _load()


def test_exact_ik_entry_ancestry_and_nested_authority() -> None:
    entry = IL.authenticate_entry(ROOT)
    assert (entry["head"], entry["tree"], entry["remote_tracking_head"]) == (IL.IK_HEAD, IL.IK_TREE, IL.IK_HEAD)
    assert entry["index"] == ""
    assert entry["nested"]["head"] == IL.NESTED_HEAD
    assert entry["nested"]["branch"] == entry["nested"]["status"] == ""


def test_committed_ik_bytes_blobs_canonical_seal_and_frontier_reconstruct() -> None:
    result = IL.reconstruct_ik(ROOT)
    assert result["status"] == "VERIFIED"
    assert result["artifact_count"] == 4
    assert result["canonical_json"] == result["inner_seal"] == "VERIFIED"
    assert result["frontier"]["current_e05_status"] == "VERIFIED__10_OF_18"
    assert result["frontier"]["successor_version_identifier"].startswith("NOT_PROVEN")


def test_human_policy_is_exact_v2_repository_only_and_non_operational() -> None:
    policy = IL.human_identity_policy()
    assert policy["human_governance_successor_identity_policy"].startswith("EXISTING_DU_EB_EE")
    assert (policy["successor_major_version"], policy["successor_semver"], policy["successor_identity_suffix"]) == (2, "2.0.0", "V2")
    assert policy["new_generic_contract_family"] is policy["v1_reinterpretation"] is False
    assert policy["human_operational_authority"] == 0


def test_exact_v1_inventory_authenticates_closed_family_owners() -> None:
    inventory = IL.v1_identity_inventory(ROOT)
    assert inventory["status"] == "VERIFIED__EXACT_V1_IDENTITY_INVENTORY"
    assert inventory["semantic_versions"] == {"DU": "1.0.0", "EB": "1.0.0", "EE": "1.0.0"}
    assert len(inventory["identities"]) == 16
    assert set(inventory["closed_schema_owners"]) == {"DU", "EB", "EE"}
    assert inventory["not_applicable"] == ["DU_NAMED_PROFILE", "EE_EXPLICIT_DOWNSTREAM_CONSUMER_IDENTITY"]
    assert inventory["schema_registries"].startswith("NOT_PROVEN__NO_DU_EB_EE")
    assert inventory["version_check_helpers"].startswith("VERIFIED__FAMILY_LOCAL")


def test_v2_token_rule_is_deterministic_and_rejects_unversioned_input() -> None:
    assert IL.derive_v2_identity("SAPIANTA_X_V1") == "SAPIANTA_X_V2"
    assert IL.derive_v2_identity("DU_EB_CANONICAL_V1_RUNTIME_V1") == "DU_EB_CANONICAL_V2_RUNTIME_V2"
    with pytest.raises(IL.ILRatificationError, match="V1_TOKEN_ABSENT"):
        IL.derive_v2_identity("SAPIANTA_X")


def test_all_counterpart_v2_identities_are_unique_collision_free_and_family_preserving() -> None:
    result = IL.v2_derivations(ROOT)
    assert result["status"].startswith("VERIFIED")
    assert (result["major"], result["semantic_version"]) == (2, "2.0.0")
    assert all(row["collision_check"].startswith("VERIFIED") for row in result["identities"])
    assert all(row["namespace_check"].startswith("VERIFIED") for row in result["identities"])
    assert all(set(("semantic_owner", "producer", "validator", "consumer", "namespace", "mandatory_equality", "failure_mode")).issubset(row) for row in result["identities"])
    mapping = {(row["family"], row["identity_role"]): row["derived_v2_identity"] for row in result["identities"]}
    assert mapping[("DU", "schema")] == "SAPIANTA_SPCE_CONTINUATION_MANIFEST_SCHEMA_V2"
    assert mapping[("EB", "validator_and_issuer_implementation")] == "G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V2"
    assert mapping[("EE", "receipt_profile")] == "DU_EB_CANONICAL_V2_RUNTIME_CONSUMER_BINDING_V2"


def test_successor_tuple_values_are_exact_with_only_repository_supported_coordinates() -> None:
    result = IL.successor_tuples(ROOT)
    assert result["status"].startswith("VERIFIED__IDENTITY_VALUES_UNIQUE")
    assert result["tuples"]["DU"]["receipt_profile"].startswith("NOT_APPLICABLE")
    assert result["tuples"]["EB"]["version"] == "2.0.0"
    assert result["tuples"]["EB"]["consumer_expectation"] == "G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V2"
    assert result["tuples"]["EE"]["consumer_expectation"].startswith("NOT_APPLICABLE")


def test_exact_tuple_guard_rejects_unknown_mixed_downgrade_caller_and_cross_family() -> None:
    values = IL.successor_tuples(ROOT)["tuples"]
    expected = IL.BoundIdentityTuple(**values["EB"])
    assert IL.validate_bound_tuple(expected, expected).startswith("VERIFIED")
    mutations = (
        replace(expected, schema_identity="UNKNOWN_V2"),
        replace(expected, version="1.0.0"),
        replace(expected, validator_identity=values["DU"]["validator_identity"]),
        replace(expected, receipt_profile=values["EE"]["receipt_profile"]),
        replace(expected, family="EE"),
    )
    for observed in mutations:
        with pytest.raises(IL.ILRatificationError, match="MISMATCH"):
            IL.validate_bound_tuple(observed, expected)
    with pytest.raises(IL.ILRatificationError, match="CALLER"):
        IL.validate_bound_tuple(expected, expected, caller_selected=True)
    with pytest.raises(IL.ILRatificationError, match="DOWNGRADE"):
        IL.validate_bound_tuple(expected, expected, downgrade=True)


def test_option_b_baseline_is_closed_typed_exactly_two_and_current_git_owned() -> None:
    baseline = {"head": IL.IK_HEAD, "tree": IL.IK_TREE}
    assert IL.validate_certification_baseline(baseline) == baseline
    assert IL.authenticate_certification_currentness(ROOT, baseline).startswith("VERIFIED")
    for invalid in ({"head": IL.IK_HEAD}, {"head": IL.IK_HEAD, "tree": IL.IK_TREE, "extra": "x"}, {"head": "A" * 40, "tree": IL.IK_TREE}):
        with pytest.raises(IL.ILRatificationError):
            IL.validate_certification_baseline(invalid)
    with pytest.raises(IL.ILRatificationError, match="NOT_CURRENT"):
        IL.authenticate_certification_currentness(ROOT, {"head": IL.IJ_HEAD, "tree": IL.IK_TREE})


def test_namespace_and_dispatch_owner_ambiguity_fails_closed_without_generic_family() -> None:
    result = IL.namespace_analysis()
    assert result["successor_namespace_policy"] == "VERIFIED__EXISTING_FAMILIES_ONLY"
    assert result["new_generic_namespace_created"] == "VERIFIED__NO"
    assert result["exact_successor_namespace_set"].startswith("NOT_PROVEN__TWO_FAMILY_LOCAL_LAYOUTS")
    assert len(result["equally_family_preserving_candidates"]) == 2
    frontier = IL.implementation_frontier()
    assert frontier["minimum_successor_implementation_owner_set"].startswith("NOT_PROVEN")
    assert frontier["minimum_successor_implementation_file_set"].startswith("NOT_PROVEN")


def test_runtime_target_and_current_certification_provenance_remain_separate() -> None:
    result = IL.provenance(ROOT)
    assert result["runtime_target"] == {"head": IL.IF_HEAD, "tree": IL.IF_TREE}
    assert result["current_certification"] == {"head": IL.IK_HEAD, "tree": IL.IK_TREE}
    assert result["runtime_target_selection_binding"] == "VERIFIED__AUTHENTICATED"
    assert result["arbitrary_historical_head_bypass"] == "VERIFIED__NO"
    assert result["certification_baseline_caller_authority"] == "VERIFIED__NO"


def test_generality_matrix_covers_v1_v2_cross_family_and_rejects_every_fault() -> None:
    matrix = IL.generality_matrix()
    assert len(matrix) == 27
    results = {row["case"]: row["observed"] for row in matrix}
    accepted = {"V1_CURRENT_TARGET_VALID", "V2_TARGET_EQUALS_CURRENT", "V2_AUTHENTICATED_TARGET_DIFFERS_CURRENT", "FUTURE_VECTOR", "NON_FUTURE_APPLICABLE_VECTOR"}
    assert all(results[case].startswith("REPRESENTABLE__CONTRACT_ONLY") for case in accepted)
    assert all(result.startswith("REJECT__") for case, result in results.items() if case not in accepted)
    assert results["CROSS_FAMILY_DU_EB_SUBSTITUTION"].startswith("REJECT")
    assert results["V2_RECEIPT_WITH_V1_IDENTITY"].startswith("REJECT")


def test_future_vector_semantics_are_unchanged_and_vector_neutral() -> None:
    result = IL.future_semantics(ROOT)
    assert (result["evaluation_time"], result["valid_from"], result["valid_until"]) == (500, 600, 1000)
    assert result["payload_digest"] == IL.FUTURE_PAYLOAD
    assert result["source_act_digest"] == IL.FUTURE_SOURCE_ACT
    assert result["che_correlation"] == IL.FUTURE_CHE
    assert result["future_semantic_mutation_count"] == result["wall_clock_dependency_count"] == "VERIFIED__0"


def test_ex_is_reused_without_reconstruction() -> None:
    assert IL.authenticate_ex(ROOT) == {"ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0", "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED"}


def test_boundaries_v1_immutability_family_separation_and_routes_are_preserved() -> None:
    reduction = IL.terminal_reduction(ROOT)
    assert reduction["compatibility"]["v1_semantics_reinterpreted"] == "VERIFIED__NO"
    assert reduction["compatibility"]["historical_v1_mutation_count"] == "VERIFIED__0"
    assert reduction["family_firewall"]["new_generic_contract_family"] == "VERIFIED__NO"
    assert reduction["boundaries"]["p11_change_required"] == "VERIFIED__NO"
    assert reduction["boundaries"]["production_route_delta"] == "VERIFIED__0"


def test_terminal_b_is_operationally_zero_e05_unchanged_and_stops_for_human() -> None:
    reduction = IL.terminal_reduction(ROOT)
    control = reduction["terminal_control"]
    assert control["successor_version_identifier"] == "VERIFIED__EXACT_V2"
    assert control["exact_successor_identity_tuple_status"].startswith("NOT_PROVEN")
    assert control["minimum_legal_next_delta"] == "HUMAN_GOVERNANCE_DECISION_REQUIRED"
    assert control["future_preoperational_readiness"] == control["future_operational_capability"] == control["next_operational_generation_eligible"] == "NOT_PROVEN"
    assert control["auto_continuable"] is control["human_authorization_required"] is control["next_generation_started"] is False
    assert control["human_review_required"] is True
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["e05"] == {"before": "10/18", "after": "10/18", "satisfied": 10, "remaining": 8, "credit": 0}


def test_terminal_is_canonical_duplicate_safe_and_inner_sealed(tmp_path: Path) -> None:
    envelope = IL.load_canonical(TERMINAL)
    assert TERMINAL.read_bytes() == IL.canonical_bytes(envelope)
    assert envelope["reduction_sha256"] == IL.sha256_bytes(IL.canonical_bytes(envelope["reduction"]))
    assert envelope == IL.terminal_envelope(ROOT)
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text('{"x":1,"x":2}\n')
    with pytest.raises(IL.ILRatificationError, match="DUPLICATE_JSON_KEY"):
        IL.load_canonical(duplicate)


def test_ast_report_exact_headings_and_repository_mutation_scope() -> None:
    tree = ast.parse(FORMALIZER.read_text())
    assert any(isinstance(node, ast.FunctionDef) and node.name == "terminal_reduction" for node in ast.walk(tree))
    headings = [line for line in REPORT.read_text().splitlines() if line.startswith("# ")]
    assert headings == ["# 1. Implementation Summary", "# 2. Code Evidence", "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix", "# 5. Repository Mutation Summary", "# 6. Certification Verdict"]
    status = subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=all"], cwd=ROOT, text=True).splitlines()
    assert status and all(line[3:].startswith(IL_ROOT.relative_to(ROOT).as_posix() + "/") for line in status)
    assert subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True) == ""


def test_direct_execution_has_no_operational_path() -> None:
    result = subprocess.run([sys.executable, str(FORMALIZER)], cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 2
    assert result.stdout == ""
    assert "NO_OPERATIONAL_PATH" in result.stderr
