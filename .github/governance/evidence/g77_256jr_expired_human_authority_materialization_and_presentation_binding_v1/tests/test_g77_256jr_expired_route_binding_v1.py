#!/usr/bin/env python3
"""Focused repository-only tests for the G77-256JR EXPIRED route binding."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
JR = ROOT / (
    ".github/governance/evidence/"
    "g77_256jr_expired_human_authority_materialization_and_presentation_binding_v1"
)
FORMALIZER = JR / "analysis/G77_256JR_EXPIRED_ROUTE_BINDING_FORMALIZER_V1.py"
REDUCTION = JR / "G77_256JR_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = JR / "G77_256JR_G48_IMPLEMENTATION_REPORT_V1.md"


def load(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


F = load(FORMALIZER, "g77_256jr_formalizer")


def test_exact_jq_recovery_entry_nested_authority_and_initial_delta() -> None:
    entry = F.authenticate_entry()
    assert entry["head"] == entry["remote_tracking_head"] == F.ENTRY_HEAD
    assert entry["tree"] == F.ENTRY_TREE
    assert entry["subject"] == F.ENTRY_SUBJECT
    assert entry["index_empty"] is True
    assert entry["recovery_entry_worktree"] == "EXPECTED__JR_GENERATION_ONLY_DIRTY"
    assert entry["nested_authority"] == {
        "origin": F.NESTED_ORIGIN,
        "head": F.NESTED_HEAD,
        "tree": F.NESTED_TREE,
        "clean": True,
        "detached": True,
        "tag": F.NESTED_TAG,
    }
    recovered = F.RECOVERED_JR_FILES[F.ADAPTER.as_posix()]
    assert recovered == {
        "line_count": 269,
        "size_bytes": 10705,
        "sha256": "96b5a90269cf871f722babbdcf49b0aa067d712c9d07142d0a2acb15510c68c2",
    }


def test_jq_blocker_ex_and_operational_firewall_reconstruct_exactly() -> None:
    jq = F.authenticate_jq()
    assert jq["terminal"] == F.JQ_TERMINAL
    assert jq["ex_reused"] == "VERIFIED__17_OF_17"
    assert jq["ex_reconstructed"] == "VERIFIED__0"
    assert jq["operational_counters"] == "VERIFIED__ALL_FOURTEEN_ZERO"
    assert jq["e05"] == {
        "after": "VERIFIED__11_OF_18",
        "before": "VERIFIED__11_OF_18",
        "credit": "VERIFIED__0",
        "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
        "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
    }


def test_existing_context_owner_and_sole_launcher_bind_exact_expired() -> None:
    route = F.verify_route_binding()
    assert route["derived_vector"] == "EXPIRED"
    assert route["adapter_source_path"] == F.ADAPTER.as_posix()
    assert route["adapter_source_sha256"] == F.RECOVERED_JR_FILES[
        F.ADAPTER.as_posix()
    ]["sha256"]
    assert route["preclaim_coordinate_unix_ns"] == 1000
    assert route["guest_consumer_path"] == (
        "/mnt/dp-harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
    )
    assert route["production_route_before"] == "VERIFIED__1"
    assert route["production_route_after"] == "VERIFIED__1"
    assert route["production_route_delta"] == "VERIFIED__0"
    assert route["parallel_route_created"] == "VERIFIED__NO"


def test_recovered_adapter_is_fixed_family_local_and_non_operational() -> None:
    result = F.verify_adapter()
    assert result["fixed_submission_time_unix_ns"] == 500
    assert result["fixed_valid_from_unix_ns"] == 100
    assert result["fixed_valid_until_unix_ns"] == 1000
    assert result["fixed_preclaim_time_unix_ns"] == 1000
    assert result["caller_selectable_temporal_coordinate_count"] == "VERIFIED__0"
    assert result["provider_selectable_temporal_coordinate_count"] == "VERIFIED__0"
    assert result["human_selectable_temporal_coordinate_count"] == "VERIFIED__0"
    assert result["generic_er_mutation_count"] == "VERIFIED__0"
    assert result["p11_mutation_count"] == "VERIFIED__0"
    assert result["adapter_main_invoked"] == "VERIFIED__NO"


def test_gn_accepts_only_exact_expired_generation_binding() -> None:
    result = F.verify_presentation()
    assert result["expired_exact_generation_binding"] == "VERIFIED__ACCEPTED"
    assert result["expired_future_mismatch"] == "VERIFIED__REJECTED"
    assert result["unknown_vector"] == "VERIFIED__REJECTED"
    assert result["human_request_created"] == "VERIFIED__0"
    assert result["human_presentation_created"] == "VERIFIED__0"
    assert result["human_authority_created"] == "VERIFIED__0"


def test_family_local_bootstrap_seed_is_exact_source_projection() -> None:
    assets = F.verify_static_assets()
    assert assets["family_local"] == "VERIFIED__YES"
    assert assets["authority"] == "VERIFIED__NO"
    assert assets["execution_authority"] == "VERIFIED__NO"
    assert assets["nocloud_source_projection"] == "VERIFIED__EXACT"


def test_sole_launcher_pre_authority_guest_binding_integration(tmp_path: Path) -> None:
    owner = F.load_module(F.CONTEXT_OWNER, "g77_256jr_integration_owner")
    launcher_dir = str((ROOT / F.LAUNCHER).parent)
    if launcher_dir not in sys.path:
        sys.path.insert(0, launcher_dir)
    sys.modules["sapianta_fresh_operation_context_v1"] = owner
    launcher = F.load_module(F.LAUNCHER, "g77_256jr_integration_launcher")
    operation_root = tmp_path / "operation_state"
    context = launcher.build_operation_context(
        repository_root=ROOT,
        repository_head=F.ENTRY_HEAD,
        repository_tree=F.ENTRY_TREE,
        generation_identity=("G77_256JR" + F.GENERATION_SUFFIXES["EXPIRED"]),
        operation_identity="G77_256JR_EXPIRED_OPERATION_001",
        identity_namespace_prefix="G77_256JR",
        operation_evidence_root=operation_root,
        transient_root=tmp_path / "transient",
    )
    binding = context["guest_adapter_binding"]
    projection_root = Path(binding["projection_root"])
    projection_root.mkdir(parents=True)
    adapter_bytes = (ROOT / F.ADAPTER).read_bytes()
    Path(binding["projected_path"]).write_bytes(adapter_bytes)
    Path(binding["bootstrap_projected_path"]).write_bytes(adapter_bytes)
    (projection_root / launcher.FRESH_OPERATION_CONTEXT_OWNER_PROJECTION_FILENAME).write_bytes(
        (ROOT / F.CONTEXT_OWNER).read_bytes()
    )
    result = launcher.prove_guest_adapter_binding(ROOT, context)
    assert result["result"] == "PREAUTHORITY_GUEST_ADAPTER_BINDING_PASS"
    assert result["source_sha256"] == F.RECOVERED_JR_FILES[F.ADAPTER.as_posix()][
        "sha256"
    ]
    assert result["guest_path"] == binding["guest_path"]
    assert result["nocloud_source_projection_identity"] == "PASS"
    assert result["source_projected_byte_identity"] == "PASS"


def test_temporal_truth_table_and_all_five_vector_regressions() -> None:
    result = F.verify_temporal_and_regressions()
    assert result["truth_table"] == {
        "999": "CURRENT", "1000": "EXPIRED", "1001": "EXPIRED"
    }
    assert result["future_semantics"] == "VERIFIED__DISTINCT_AND_UNCHANGED"
    for vector in (
        "WRONG_ATTEMPT", "WRONG_CONTRACT", "WRONG_INPUT", "WRONG_PROVENANCE"
    ):
        assert result[vector.lower()] == "VERIFIED__UNCHANGED"
    assert result["p11_expired_boundary"] == (
        "BEFORE_P11_DA_OPERATIONAL_PRECLAIM_APPEND"
    )
    assert result["vector_paths"] == F.EXPECTED_VECTOR_PATHS


def test_no_second_launcher_owner_registry_generic_framework_or_p11_delta() -> None:
    adapter_tree = ast.parse((ROOT / F.ADAPTER).read_text(encoding="utf-8"))
    names = {
        node.name for node in ast.walk(adapter_tree)
        if isinstance(node, (ast.FunctionDef, ast.ClassDef))
    }
    assert "main" in names
    assert not {
        "launch", "run_once", "submit_human_act", "claim_and_invoke_once",
        "create_human_authority", "register_vector",
    } & names
    assert subprocess.check_output(
        ["git", "diff", "--name-only", "--", "tests/p11_da_operational_consumer_v1.py"],
        cwd=ROOT, text=True,
    ).strip() == ""
    reduction = F.build_reduction()
    architecture = reduction["architecture"]
    for key in (
        "p11_implementation_mutation_count", "new_owner_count", "new_route_count",
        "new_registry_count", "new_generic_abstraction_count",
        "new_constitutional_concept_count", "production_route_delta",
    ):
        assert architecture[key] == "VERIFIED__0"


def test_terminal_reduction_is_exact_inner_sealed_and_zero_operation() -> None:
    envelope = json.loads(REDUCTION.read_bytes())
    reduction = envelope["reduction"]
    assert envelope["reduction_sha256"] == hashlib.sha256(
        F.canonical_bytes(reduction)
    ).hexdigest()
    assert reduction == F.build_reduction()
    assert reduction["terminal"] == F.TERMINAL
    assert set(reduction["operational_counters"].values()) == {"VERIFIED__0"}
    assert reduction["e05"] == {
        "before": "VERIFIED__11_OF_18",
        "after": "VERIFIED__11_OF_18",
        "credit": "VERIFIED__0",
        "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
        "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
    }
    assert reduction["reuse"]["ex_reused"] == "VERIFIED__17_OF_17"
    assert reduction["reuse"]["ex_reconstructed"] == "VERIFIED__0"
    assert reduction["auto_continuable"] is False
    assert reduction["human_review_required"] is True


def test_g48_has_exactly_six_h1_five_questions_and_recovery_ccwim() -> None:
    report = REPORT.read_text(encoding="utf-8")
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    for token in (
        "## Reuse Impact Assessment",
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "Katere nove zmogljivosti (če sploh) nastanejo?",
        "Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "Ali implementacija ustvarja vzporedni tok?",
        "Ali zmanjšuje ali povečuje število produkcijskih poti?",
        "## Minimal Governance Dashboard", "## Compact Recovery CCWIM",
        "AUTO_CONTINUABLE = NO", "HUMAN_REVIEW_REQUIRED = YES", F.TERMINAL,
    ):
        assert token in report


def test_final_mutation_scope_and_index_are_exact() -> None:
    assert set(subprocess.check_output(
        ["git", "diff", "--name-only"], cwd=ROOT, text=True
    ).splitlines()) == {path.as_posix() for path in F.TRACKED_PRODUCTION}
    status = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT, text=True,
    ).splitlines()
    assert {line[3:] for line in status if line.startswith("?? ")} == {
        path.as_posix() for path in F.FINAL_UNTRACKED
    }
    assert subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True
    ).strip() == ""
