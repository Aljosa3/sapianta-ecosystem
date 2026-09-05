#!/usr/bin/env python3
"""Repository-only validation for the G77-256ID E05 frontier selection."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[5]
ID_ROOT = ROOT / ".github/governance/evidence/g77_256id_post_ic_e05_frontier_selection_v1"
SELECTION = ID_ROOT / "G77_256ID_E05_FRONTIER_SELECTION_V1.json"
REPORT = ROOT / "docs/governance/G77_256ID_POST_IC_REPOSITORY_ONLY_E05_FRONTIER_SELECTION_V1.md"
EM = ROOT / ".github/governance/evidence/g77_256em_post_ek_frontier_reduction_v1/G77_256EM_SPCE_PHASE_D_REDUCTION_CHECKPOINT_V1.json"
HY = ROOT / "docs/governance/G77_256HY_AUTHENTICATED_E05_9_OF_18_FRONTIER_SELECTION_MINIMUM_DELTA_REUSE_ANALYSIS_AND_NEXT_OBLIGATION_DESIGN_V1.md"
IC_SEAL = ROOT / ".github/governance/evidence/g77_256ic_wrong_provenance_operational_v1/G77_256IC_SPCE_FINAL_EXECUTION_SEAL_V1.json"
IC_REDUCTION = ROOT / ".github/governance/evidence/g77_256ic_wrong_provenance_operational_v1/G77_256IC_SPCE_TERMINAL_REDUCTION_V1.json"
P11 = ROOT / "tests/p11_da_operational_consumer_v1.py"
HEAD = "afdd47166acdee30cb9867d3d3c7bfec0de64c8a"
TREE = "58ef5f2ce3d4e5b09632dd0eb212defc5a62b474"
SELECTION_SHA256 = "4cc520613eedb0c866b99acd75aa273f3a7bd4108aa6e280013a6d75fa6fb20f"
REQUIRED = [
    "POSITIVE_AUTHORITY_BASELINE", "STATE_TRANSITION", "CONCURRENCY", "UNKNOWN",
    "AMBIGUOUS", "STALE", "FUTURE", "EXPIRED", "REVOKED", "SUPERSEDED",
    "CONSUMED", "WRONG_SCOPE", "WRONG_CALLER", "WRONG_ATTEMPT", "WRONG_INPUT",
    "WRONG_PROVENANCE", "WRONG_CONTRACT", "COHERENT_COPY",
]
SATISFIED = [
    "POSITIVE_AUTHORITY_BASELINE", "STATE_TRANSITION", "CONCURRENCY", "UNKNOWN",
    "CONSUMED", "WRONG_CALLER", "WRONG_ATTEMPT", "WRONG_INPUT", "WRONG_CONTRACT",
    "WRONG_PROVENANCE",
]
REMAINING = [
    "AMBIGUOUS", "STALE", "FUTURE", "EXPIRED", "REVOKED", "SUPERSEDED",
    "WRONG_SCOPE", "COHERENT_COPY",
]
RANKING = [
    "FUTURE", "EXPIRED", "WRONG_SCOPE", "REVOKED", "SUPERSEDED", "STALE",
    "AMBIGUOUS", "COHERENT_COPY",
]
VERDICT = (
    "VERIFIED__G77_256ID_POST_IC_REPOSITORY_ONLY_E05_FRONTIER_SELECTION__"
    "IC_10_OF_18_RECONSTRUCTED__ALL_EIGHT_COMPARED__FUTURE_UNIQUELY_SELECTED__"
    "EX_17_OF_17_REUSED__ZERO_OPERATION__HUMAN_REVIEW_REQUIRED"
)


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_unique(path: Path) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    value = json.loads(path.read_bytes(), object_pairs_hook=unique)
    assert isinstance(value, dict)
    return value


def test_exact_clean_committed_ic_entry_and_nested_authority() -> None:
    git = lambda *args: subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    assert git("branch", "--show-current") == "g77-256fl-wrong-attempt-preboot-blocker"
    assert git("rev-parse", "HEAD") == HEAD
    assert git("rev-parse", "HEAD^{tree}") == TREE
    assert git("show", "-s", "--format=%s", "HEAD") == "G77-256IC certify WRONG_PROVENANCE operational denial"
    assert git("status", "--porcelain", "--untracked-files=no") == ""
    assert git("diff", "--cached", "--name-only") == ""
    nested = ROOT / "sapianta_system"
    nested_git = lambda *args: subprocess.check_output(["git", *args], cwd=nested, text=True).strip()
    assert nested_git("rev-parse", "HEAD") == "3183bab71f8f30397c0309dd2e6d846d14a11f66"
    assert nested_git("rev-parse", "HEAD^{tree}") == "7c32ec05efc2be43297849bc38ec8766514a523d"
    assert nested_git("branch", "--show-current") == ""
    assert nested_git("status", "--porcelain") == ""
    assert nested_git("describe", "--tags", "--exact-match", "HEAD") == "sapianta-system-nested-authority-3183bab-v1"


def test_selection_json_is_unique_key_canonical_and_inner_sealed() -> None:
    envelope = load_unique(SELECTION)
    assert SELECTION.read_bytes() == canonical_bytes(envelope)
    assert envelope["schema_id"] == "G77_256ID_E05_FRONTIER_SELECTION_ENVELOPE_V1"
    assert envelope["selection_sha256"] == SELECTION_SHA256
    assert hashlib.sha256(canonical_bytes(envelope["selection"])).hexdigest() == SELECTION_SHA256
    with pytest.raises(ValueError):
        json.loads('{"x":1,"x":2}', object_pairs_hook=lambda pairs: (_ for _ in ()).throw(ValueError()) if len({k for k, _ in pairs}) != len(pairs) else dict(pairs))


def test_authoritative_sources_are_hash_bound() -> None:
    selection = load_unique(SELECTION)["selection"]
    assert len(selection["sources"]) == 8
    for source in selection["sources"]:
        assert sha256(ROOT / source["path"]) == source["sha256"]


def test_ic_terminal_state_and_e05_matrix_reconstruct_exactly() -> None:
    selection = load_unique(SELECTION)["selection"]
    em = load_unique(EM)["checkpoint"]["obligation_matrix"]
    observed_required = [row["obligation_id"].rsplit("/", 1)[-1] for row in em]
    assert len(observed_required) == len(set(observed_required)) == 18
    assert set(observed_required) == set(REQUIRED)
    assert selection["e05"] == {
        "remaining": 8, "remaining_set": REMAINING, "required": 18,
        "required_set": REQUIRED, "satisfied": 10, "satisfied_set": SATISFIED,
        "status": "VERIFIED__10_OF_18",
    }
    assert set(REQUIRED) - set(SATISFIED) == set(REMAINING)
    hy_text = HY.read_text(encoding="utf-8")
    assert "Verified satisfied set:" in hy_text and "WRONG_CONTRACT" in hy_text
    ic = load_unique(IC_SEAL)["seal"]
    terminal = load_unique(IC_REDUCTION)["reduction"]
    assert ic["e05"] == terminal["e05"] == {"after": "10/18", "before": "9/18", "credit": 1}
    assert ic["wrong_provenance_operational_capability"] == "VERIFIED"
    assert ic["authoritative_reducer_result"] == ic["independent_reducer_result"] == "ACCEPT"
    assert ic["reducer_agreement_status"] == "VERIFIED"
    assert ic["teardown_state"] == "COMPLETE"
    assert selection["ic_terminal_reconstruction"]["operational_counters"] == ic["operational_counters"]


def test_all_eight_candidates_have_complete_analysis_and_unique_future_rank() -> None:
    selection = load_unique(SELECTION)["selection"]
    candidates = selection["candidates"]
    required_fields = {
        "current_repository_support", "ex_reuse", "existing_authority_reuse",
        "existing_reducer_reuse", "existing_route_reuse", "existing_runtime_reuse",
        "existing_semantic_owner_reuse", "expected_denial_boundary_clarity",
        "expected_operational_complexity", "expected_proof_complexity",
        "frontier_selection_score_or_order", "minimum_legal_delta",
        "new_custody_or_authenticity_mechanism_required",
        "new_lifecycle_mechanism_required", "new_resolution_mechanism_required",
        "new_scope_mechanism_required", "new_semantic_mechanism_required",
        "new_temporal_mechanism_required", "overengineering_risk", "vector",
    }
    assert len(candidates) == 8
    assert all(set(candidate) == required_fields for candidate in candidates)
    assert {candidate["vector"] for candidate in candidates} == set(REMAINING)
    assert selection["ranking"] == RANKING
    assert selection["selected_frontier"]["selected_next_e05_vector"] == "FUTURE"
    assert selection["selected_frontier"]["selection_status"].startswith("VERIFIED__UNIQUE")


def test_future_reuses_currentness_owner_without_claiming_other_mechanisms() -> None:
    source = P11.read_text(encoding="utf-8")
    tree = ast.parse(source)
    assert "valid_from_unix_ns" in source and "valid_until_unix_ns" in source
    assert "if not valid_from <= current < valid_until:" in source
    assert '_fail("operational Human act is not current")' in source
    assert "now_unix_ns: int" in source
    assert any(isinstance(node, ast.ClassDef) and node.name == "P11BoundedConsumerV1" for node in ast.walk(tree))
    coherent = next(item for item in load_unique(SELECTION)["selection"]["candidates"] if item["vector"] == "COHERENT_COPY")
    assert coherent["expected_denial_boundary_clarity"].startswith("NOT_PROVEN__")


def test_id_has_zero_operational_effect_and_preserves_one_route() -> None:
    selection = load_unique(SELECTION)["selection"]
    assert set(selection["operational_counters"].values()) == {0}
    reuse = selection["reuse_impact"]
    assert reuse["production_route_before"] == reuse["production_route_after"] == "VERIFIED__1"
    assert reuse["production_route_delta"] == "VERIFIED__0"
    for key in ("new_generic_framework_count", "new_authority_layer_count", "new_production_route_count", "new_runtime_owner_count"):
        assert reuse[key] == "VERIFIED__0"
    assert selection["ex"] == {
        "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED",
        "reconstructed": 0,
        "reused": "17/17",
    }


def test_same_generation_cross_worker_recovery_is_exactly_accounted() -> None:
    selection = load_unique(SELECTION)["selection"]
    ccwim = selection["ccwim"]
    assert ccwim["intra_generation_cross_worker_continuation"].startswith(
        "VERIFIED__YES__G77_256ID"
    )
    assert ccwim["uncommitted_delta_recovery"].startswith("VERIFIED__YES")
    assert ccwim["uncommitted_selection_delta_recovery"] == "VERIFIED__YES"
    assert (
        ccwim["repository_only_analytical_cross_worker_continuation"]
        == "VERIFIED__YES"
    )
    inherited = selection["inherited_delta"]
    assert inherited["complete_enumeration_status"] == "VERIFIED"
    assert inherited["entry_file_count"] == len(inherited["files"]) == 4
    assert inherited["unrelated_mutation_count"] == 0
    assert sum("GENERATED_BYTECODE_REMOVED" in item["classification"] for item in inherited["files"]) == 1


def test_g48_report_has_exactly_six_headings_and_terminal_verdict() -> None:
    report = REPORT.read_text(encoding="utf-8")
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]
    assert report.rstrip().endswith(VERDICT)
