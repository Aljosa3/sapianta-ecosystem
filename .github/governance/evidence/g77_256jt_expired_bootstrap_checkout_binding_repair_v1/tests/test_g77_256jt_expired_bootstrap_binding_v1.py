from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[5]
JT = ROOT / ".github/governance/evidence/g77_256jt_expired_bootstrap_checkout_binding_repair_v1"
FORMALIZER = JT / "analysis/G77_256JT_EXPIRED_BOOTSTRAP_BINDING_FORMALIZER_V1.py"
REPORT = JT / "G77_256JT_G48_IMPLEMENTATION_REPORT_V1.md"
REDUCTION = JT / "G77_256JT_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"

specification = importlib.util.spec_from_file_location("g77_256jt_formalizer", FORMALIZER)
assert specification is not None and specification.loader is not None
F = importlib.util.module_from_spec(specification)
sys.modules[specification.name] = F
specification.loader.exec_module(F)


def test_exact_js_entry_and_committed_blocker_reconstruct() -> None:
    entry = F.authenticate_entry()
    assert entry["head"] == F.ENTRY_HEAD
    assert entry["tree"] == F.ENTRY_TREE
    assert entry["index_empty"] is True
    assert entry["worktree"] == "DIRTY_ONLY_WITH_AUTHENTICATED_G77_256JT_DELTA"
    assert entry["recovery_existing_delta_authenticated"] == "VERIFIED__YES"
    js = F.reconstruct_js()
    assert js["terminal"] == (
        "M__EXPIRED_FRESH_PREAUTHORIZATION_BOOTSTRAP_HEAD_TREE_BINDING_MISMATCH"
    )
    assert js["operational_counters"] == "VERIFIED__ALL_FOURTEEN_ZERO"
    assert js["ex_reused"] == "VERIFIED__17_OF_17"
    assert js["ex_reconstructed"] == "VERIFIED__0"


def test_two_field_mismatch_is_independently_reproduced() -> None:
    blocker = F.reconstruct_blocker()
    assert blocker["differing_positions"] == [2, 3]
    assert blocker["all_other_positions_equal"] is True
    assert blocker["observed_tuple"][2:4] == [F.JQ_HEAD, F.JQ_TREE]
    assert blocker["required_tuple"][2:4] == [F.JR_HEAD, F.JR_TREE]


def test_stable_owner_solution_and_recurrence_firewall() -> None:
    solution = F.verify_solution()
    assert solution["authoritative_owner"] == (
        "EXISTING_FM_SEALED_RUNTIME_CHECKOUT_IDENTITY_OWNER"
    )
    assert solution["jr_checkout_head"] == F.JR_HEAD
    assert solution["jr_checkout_tree"] == F.JR_TREE
    assert solution["recurrence_hazard"].startswith("VERIFIED__ELIMINATED")
    assert solution["successor_commit_requires_bootstrap_rewrite"] == "VERIFIED__NO"
    assert solution["unchanged_vector_checkout_semantics"] == [
        "FUTURE",
        "WRONG_ATTEMPT",
        "WRONG_CONTRACT",
        "WRONG_INPUT",
        "WRONG_PROVENANCE",
    ]
    assert solution["historical_jq_authority"] == (
        "VERIFIED__REMOVED_FROM_CURRENT_SELECTOR_AND_BOOTSTRAP"
    )
    assert solution["guest_adapter_binding"] == "PREAUTHORITY_GUEST_ADAPTER_BINDING_PASS"
    assert solution["fm_fail_closed"] == (
        "VERIFIED__WRONG_ADVANCING_CHECKOUT_REJECTED"
    )
    assert solution["gn_fail_closed"] == "VERIFIED"
    assert solution["route_count"] == 1


def test_temporal_adapter_p11_and_nocloud_are_exact() -> None:
    solution = F.verify_solution()
    assert solution["expired_adapter"] == "VERIFIED__EXACT_UNCHANGED"
    assert solution["temporal_truth_table"] == {
        "999": "CURRENT",
        "1000": "EXPIRED",
        "1001": "EXPIRED",
    }
    assert solution["p11_sha256"] == F.P11_SHA256
    assert solution["nocloud_projection"] == "VERIFIED__ALL_THREE_MEMBERS_EXACT"
    assert solution["cloud_delta_line_count"] == 2


def test_terminal_reduction_is_canonical_and_matches_formalizer() -> None:
    envelope = json.loads(REDUCTION.read_bytes())
    reduction = envelope["reduction"]
    assert envelope["reduction_sha256"] == hashlib.sha256(
        F.canonical_bytes(reduction)
    ).hexdigest()
    assert reduction == F.build_reduction()
    assert reduction["terminal"] == F.TERMINAL
    assert set(reduction["operational_counters"].values()) == {"VERIFIED__0"}
    assert reduction["e05"]["after"] == "VERIFIED__11_OF_18"
    assert reduction["e05"]["credit"] == "VERIFIED__0"
    assert reduction["auto_continuable"] is False
    assert reduction["human_review_required"] is True
    assert reduction["recovery"] == {
        "recovery_type": "SAME_GENERATION_PROVIDER_LIMIT_RECOVERY",
        "recovery_source_generation": "G77-256JT",
        "new_generation_created": "VERIFIED__NO",
        "recovery_existing_delta_authenticated": "VERIFIED__YES",
        "recovery_duplicate_operation_count": "VERIFIED__0",
        "recovery_operation_replay_count": "VERIFIED__0",
    }


def test_architecture_and_proof_yield_are_narrow() -> None:
    reduction = json.loads(REDUCTION.read_bytes())["reduction"]
    architecture = reduction["architecture"]
    assert architecture["production_mutation_count"] == "VERIFIED__3"
    assert architecture["p11_implementation_mutation_count"] == "VERIFIED__0"
    assert architecture["new_owner_count"] == "VERIFIED__0"
    assert architecture["new_route_count"] == "VERIFIED__0"
    assert architecture["new_generic_abstraction_count"] == "VERIFIED__0"
    assert architecture["production_route_before"] == "VERIFIED__1"
    assert architecture["production_route_after"] == "VERIFIED__1"
    assert architecture["production_route_delta"] == "VERIFIED__0"
    assert reduction["proof_yield"]["new_verified_capability_count"].startswith(
        "VERIFIED__1__EXPIRED_BOOTSTRAP"
    )


def test_repository_only_sources_have_no_operational_or_authority_entry() -> None:
    tree = ast.parse(FORMALIZER.read_text(encoding="utf-8"))
    called_attributes = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert not {
        "main",
        "materialize_operation_state",
        "validate_final_admission",
        "write_authority_handoff",
        "claim_and_invoke_once",
    } & called_attributes
    forbidden = (
        JT / "G77_256JT_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json",
        JT / "G77_256JT_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt",
        JT / "G77_256JT_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json",
    )
    assert not any(path.exists() or path.is_symlink() for path in forbidden)


def test_g48_has_six_h1_and_five_exact_slovenian_questions() -> None:
    lines = REPORT.read_text(encoding="utf-8").splitlines()
    assert [line for line in lines if line.startswith("# ")] == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    questions = (
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "Katere nove zmogljivosti (če sploh) nastanejo?",
        "Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "Ali implementacija ustvarja vzporedni tok?",
        "Ali zmanjšuje ali povečuje število produkcijskih poti?",
    )
    assert all(REPORT.read_text(encoding="utf-8").count(question) == 1 for question in questions)
