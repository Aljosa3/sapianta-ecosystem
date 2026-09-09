"""Focused repository-only verification for G77-256JL."""

from __future__ import annotations

import ast
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[5]
NAMESPACE = Path(__file__).resolve().parents[1]
FORMALIZER = NAMESPACE / "analysis/G77_256JL_P11_TEMPORAL_OWNER_CONTRACT_FORMALIZER_V1.py"
REPORT = NAMESPACE / "G77_256JL_G48_IMPLEMENTATION_REPORT_V1.md"
REDUCTION = NAMESPACE / "G77_256JL_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"

SPEC = importlib.util.spec_from_file_location("g77_256jl_formalizer", FORMALIZER)
assert SPEC is not None and SPEC.loader is not None
JL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(JL)


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def load_reduction() -> dict:
    envelope = json.loads(REDUCTION.read_bytes(), object_pairs_hook=JL.unique_object)
    return JL.verify_inner_seal(envelope)


def test_authenticated_entry_and_nested_authority_are_exact() -> None:
    entry = JL.authenticate_entry(ROOT)
    assert entry["branch"] == JL.ENTRY_BRANCH
    assert entry["entry_head"] == JL.ENTRY_HEAD
    assert entry["entry_tree"] == JL.ENTRY_TREE
    assert entry["entry_remote_head"] == JL.ENTRY_HEAD
    assert entry["subject"] == JL.ENTRY_SUBJECT
    assert entry["entry_index"] == "VERIFIED__EMPTY"
    assert entry["nested_authority"] == {
        "origin": JL.NESTED_ORIGIN,
        "head": JL.NESTED_HEAD,
        "tree": JL.NESTED_TREE,
        "clean": True,
        "detached": True,
        "tag": JL.NESTED_TAG,
    }


def test_authenticated_sources_and_jk_reconstruction() -> None:
    assert len(JL.authenticate_sources(ROOT)) == 20
    jk = JL.reconstruct_jk(ROOT)
    assert jk["jk_terminal"] == JL.JK_TERMINAL
    assert jk["preclaim_time_owner"].endswith("P11BoundedConsumerV1.claim_and_invoke_once")
    assert "time.time_ns()" in jk["preclaim_time_source"]
    assert jk["caller_selectable_time_authority_count"] == "VERIFIED__0"
    assert jk["provider_selectable_time_authority_count"] == "VERIFIED__0"
    assert jk["boundary"] == {
        "valid_until_minus_1": "NOT_EXPIRED",
        "valid_until": "EXPIRED",
        "valid_until_plus_1": "EXPIRED",
    }
    assert jk["owner_transition"] == "AVAILABLE -> EXPIRED"
    assert jk["denial_boundary"] == "before P11_DA_OPERATIONAL_PRECLAIM append"
    assert jk["ex_reused"] == "VERIFIED__17_OF_17"
    assert jk["ex_reconstructed"] == "VERIFIED__0"
    assert jk["e05"] == "VERIFIED__11_OF_18"


def test_repository_owner_trace_reuses_existing_context_and_gate() -> None:
    trace = JL.trace_repository_owners(ROOT)
    assert trace["current_preclaim_source"] == "unconditional internal time.time_ns()"
    assert trace["current_request_fields"] == [
        "protocol_identity", "operation", "request_identity", "canonical_payload"
    ]
    assert trace["current_request_temporal_field_count"] == 0
    assert trace["existing_namespace_owner"] == "SEALED_CONTEXT_OPERATION_EVIDENCE_ROOT"
    assert trace["p11_commissioning_gate"].startswith("VERIFIED__HASH_IDENTIFIED")
    assert "context_sha256" in trace["existing_context_seal"]
    assert trace["existing_future_temporal_reuse"].endswith(
        "binding boundary not reused as preclaim"
    )


def test_all_options_cover_a_through_x_and_only_a_passes() -> None:
    candidates = JL.candidate_comparison()
    assert set(candidates) == {"OPTION_A", "OPTION_B", "OPTION_C", "OPTION_D"}
    required = {f"{letter}_" for letter in "ABCDEFGHIJKLMNOPQRSTUVWX"}
    for candidate in candidates.values():
        prefixes = {key[:2] for key in candidate if len(key) > 2 and key[1] == "_"}
        assert required <= prefixes
    assert [name for name, value in candidates.items()
            if value["constitutional_admissibility"] == "PASS"] == ["OPTION_A"]
    assert candidates["OPTION_A"]["dominance"] == "UNIQUE_NONDOMINATED_SAFE_CANDIDATE"
    assert candidates["OPTION_B"]["rejection"] == "CALLER_OR_HUMAN_SELECTABLE_TEMPORAL_AUTHORITY"
    assert "PROVIDER_TRUST_SURFACE" in candidates["OPTION_C"]["rejection"]
    assert candidates["OPTION_D"]["rejection"].startswith("UNSAFE_OR_REDUCES_TO_OPTION_A")


def test_unique_minimum_and_exact_ownership_chain() -> None:
    selection = JL.select_unique_minimum()
    contract = JL.temporal_owner_contract()
    assert selection["passing_candidate_set"] == ["OPTION_A"]
    assert selection["temporal_owner_selection_status"] == "VERIFIED__UNIQUE_MINIMUM_GOVERNED_DELTA"
    assert contract["temporal_coordinate_owner"] == JL.TEMPORAL_OWNER
    assert contract["temporal_coordinate_producer"].startswith(
        "EXISTING_FAMILY_LOCAL_PREAUTHORIZATION_MATERIALIZER"
    )
    assert contract["temporal_coordinate_authenticator"].startswith(
        "P11_DA_AUTHORITY_CUSTODY_PROCESS_PRINCIPAL"
    )
    assert contract["temporal_coordinate_seal_owner"] == (
        "EXISTING_FM_SAPIANTA_FRESH_OPERATION_CONTEXT_V1.context_sha256"
    )
    assert contract["temporal_coordinate_consumer"].endswith(
        "P11BoundedConsumerV1.claim_and_invoke_once"
    )
    assert contract["human_may_select_coordinate"].startswith("VERIFIED__NO")
    assert contract["caller_may_select_coordinate"] == "VERIFIED__NO"
    assert contract["provider_model_may_select_coordinate"] == "VERIFIED__NO"


def test_temporal_authority_separation_and_mutation_rules() -> None:
    contract = JL.temporal_owner_contract()
    for key in (
        "temporal_coordinate_is_execution_authority",
        "temporal_coordinate_is_human_authority",
        "temporal_coordinate_is_p11_authority",
        "temporal_coordinate_is_protected_effect_authority",
        "runtime_clock_capability_is_execution_authority",
    ):
        assert contract[key] == "VERIFIED__NO"
    assert contract["deterministic_input_without_valid_p11_authority"] == (
        "VERIFIED__NO_PROTECTED_EFFECT"
    )
    assert contract["change_after_authority_correlation"].startswith("PROHIBITED")
    assert contract["change_after_authority_consumption"].startswith("PROHIBITED")
    assert contract["reuse_by_replay"] == "PROHIBITED_OPERATIONALLY"
    assert "NONAUTHORITATIVE_OBSERVATION" in contract["wall_clock_disagreement"]


def test_synthetic_context_is_sealed_operation_local_and_expired() -> None:
    context = JL.make_synthetic_context()
    correlation = JL.synthetic_authority_correlation(context)
    coordinate = JL.authenticate_synthetic_coordinate(context, correlation)
    assert coordinate == 1000
    assert JL.temporal_decision(coordinate) == "EXPIRED"
    assert correlation["authorized_context_sha256"] == context["context_sha256"]
    assert context["generation_identity"] == JL.SYNTHETIC_GENERATION
    assert context["operation_identity"] == JL.SYNTHETIC_OPERATION


def test_fail_closed_temporal_input_matrix_is_complete() -> None:
    failures = JL.verify_contract_failures()
    assert set(failures) == {
        "absent", "wrong_type", "negative", "bool", "policy_output_mismatch",
        "coordinate_seal_mismatch", "operation_context_mismatch",
        "mutation_after_sealing", "mutation_after_authority_correlation",
        "caller_replacement", "provider_replacement",
        "authority_correlation_mismatch", "replay_with_different_coordinate",
        "malformed_json", "duplicate_conflicting_coordinates",
        "wall_clock_disagreement", "conflicting_temporal_source",
    }
    assert len(failures) == 17
    assert failures["absent"].startswith("VERIFIED__FAIL_CLOSED")
    assert failures["authority_correlation_mismatch"].endswith(
        "TEMPORAL_AUTHORITY_OR_PREFLIGHT_CORRELATION_MISMATCH"
    )
    assert failures["operation_context_mismatch"].endswith(
        "TEMPORAL_OPERATION_CONTEXT_MISMATCH"
    )
    assert failures["mutation_after_authority_correlation"].endswith(
        "TEMPORAL_AUTHORITY_OR_PREFLIGHT_CORRELATION_MISMATCH"
    )
    assert failures["wall_clock_disagreement"].endswith("NO_OVERRIDE_OR_REPAIR")


def test_exact_fields_duplicate_keys_seal_and_correlation_fail_closed() -> None:
    with pytest.raises(JL.ContractError, match="DUPLICATE_JSON_KEY__coordinate_unix_ns"):
        json.loads(
            '{"coordinate_unix_ns":1000,"coordinate_unix_ns":1001}',
            object_pairs_hook=JL.unique_object,
        )
    baseline = JL.make_synthetic_context()
    correlation = JL.synthetic_authority_correlation(baseline)
    extra = deepcopy(baseline)
    extra["second_time_source"] = 1001
    with pytest.raises(JL.ContractError, match="TEMPORAL_CONTEXT_FIELDS_INVALID"):
        JL.authenticate_synthetic_coordinate(extra, correlation)
    changed = deepcopy(baseline)
    changed["candidate_manifest_sha256"] = "c" * 64
    with pytest.raises(JL.ContractError, match="TEMPORAL_CONTEXT_SEAL_INVALID"):
        JL.authenticate_synthetic_coordinate(changed, correlation)


def test_replay_and_disjoint_boundary_semantics() -> None:
    assert JL.replay_semantics() == {
        "same_authenticated_inputs_same_coordinate_same_decision": "VERIFIED__EXPIRED_EQUALS_EXPIRED",
        "operational_replay_authorized": "VERIFIED__NO",
        "read_only_reduction": "VERIFIED__DETERMINISTIC",
        "independent_authenticated_state_transition_exception": (
            "VERIFIED__REVOCATION_OR_SUPERSESSION_MAY_INVALIDATE__NOT_IMPLEMENTED_BY_JL"
        ),
        "different_coordinate_same_authority": "VERIFIED__FAIL_CLOSED_CORRELATION_OR_POLICY_MISMATCH",
    }
    assert JL.boundary_semantics() == {
        "future": "FUTURE", "current_lower": "CURRENT", "current_upper": "CURRENT",
        "expired_equal": "EXPIRED", "expired_after": "EXPIRED",
    }


def test_reduction_is_sealed_complete_and_contract_only() -> None:
    reduction = load_reduction()
    rebuilt = JL.build_reduction(ROOT)
    assert reduction == rebuilt
    assert reduction["terminal"] == JL.TERMINAL
    assert reduction["mode"] == "CONTRACT_FORMALIZATION_ONLY__NO_AUTHORITY__NO_OPERATION"
    assert reduction["entry_head"] == JL.ENTRY_HEAD
    assert reduction["entry_tree"] == JL.ENTRY_TREE
    assert reduction["entry_remote_head"] == JL.ENTRY_HEAD
    assert reduction["jk_terminal"] == JL.JK_TERMINAL
    assert reduction["selected_temporal_owner_contract"] == JL.SELECTED_CONTRACT
    assert reduction["auto_continuable"] is False
    assert reduction["human_review_required"] is True


def test_firewalls_routes_ex_and_e05_are_preserved() -> None:
    reduction = load_reduction()
    assert reduction["p11_implementation_mutation_count"] == "VERIFIED__0"
    assert reduction["production_mutation_count"] == "VERIFIED__0"
    assert (
        reduction["production_route_before"], reduction["production_route_after"],
        reduction["production_route_delta"],
    ) == ("VERIFIED__1", "VERIFIED__1", "VERIFIED__0")
    assert reduction["ex_reused"] == "VERIFIED__17_OF_17"
    assert reduction["ex_reconstructed"] == "VERIFIED__0"
    assert (
        reduction["e05_before"], reduction["e05_after"], reduction["e05_credit"],
    ) == ("VERIFIED__11_OF_18", "VERIFIED__11_OF_18", "VERIFIED__0")
    assert reduction["expired_operational_status"] == "NOT_PROVEN_OPERATIONALLY"
    assert set(reduction["operational_counters"].values()) == {"VERIFIED__0"}


def test_ex_common_substrate_remains_hash_bound_17_of_17() -> None:
    ex_path = ROOT / next(path for path in JL.SOURCES if "g77_256ex_common" in path)
    ex = json.loads(ex_path.read_bytes(), object_pairs_hook=JL.unique_object)
    certificate = ex["certificate"]
    preimage = deepcopy(ex)
    preimage["certificate_sha256"] = ""
    assert ex["certificate_sha256"] == JL.sha256_bytes(
        JL.canonical_bytes(preimage)
    )
    assert certificate["component_counts"]["CERTIFIED"] == 17
    assert sum(
        component["proposed_ex_classification"] == "CERTIFIED"
        for component in certificate["component_certification_matrix"]
    ) == 17


def test_report_has_exact_g48_structure_reuse_ccwim_and_answers() -> None:
    text = REPORT.read_text(encoding="utf-8")
    assert [line for line in text.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]
    assert "## Reuse Impact Assessment" in text
    assert "## Constitutional Continuity & Worker Independence Metrics — CCWIM" in text
    for question in (
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "Katere nove zmogljivosti (če sploh) nastanejo?",
        "Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "Ali implementacija ustvarja vzporedni tok?",
        "Ali zmanjšuje ali povečuje število produkcijskih poti?",
    ):
        assert question in text
    assert text.rstrip().endswith(JL.TERMINAL)


def test_namespace_is_exactly_four_unstaged_files_and_layer_zero_is_untouched() -> None:
    files = sorted(
        str(path.relative_to(ROOT)) for path in NAMESPACE.rglob("*") if path.is_file()
    )
    assert files == sorted(JL.EXPECTED_DELTA_PATHS)
    assert git("diff", "--cached", "--name-only") == ""
    status_paths = [line[3:] for line in git("status", "--porcelain", "--untracked-files=all").splitlines()]
    assert sorted(status_paths) == sorted(JL.EXPECTED_DELTA_PATHS)
    assert all(path.startswith(str(JL.NAMESPACE) + "/") for path in status_paths)
    assert not any(path.startswith(("docs/governance/", "runtime/", "tests/p11_")) for path in status_paths)


def test_formalizer_contains_no_clock_or_operational_capability() -> None:
    tree = ast.parse(FORMALIZER.read_text(encoding="utf-8"))
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert "time" not in imports
    assert "datetime" not in imports
    calls = {
        node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, (ast.Attribute, ast.Name))
    }
    assert not ({"sleep", "invoke", "claim_and_invoke_once", "operate", "retry"} & calls)
