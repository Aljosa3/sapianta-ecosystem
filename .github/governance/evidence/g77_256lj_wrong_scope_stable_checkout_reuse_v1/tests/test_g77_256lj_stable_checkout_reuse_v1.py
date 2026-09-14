"""Focused authority-free G77-256LJ stable-checkout proof."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[5]
VERIFIER = ROOT / (
    ".github/governance/evidence/"
    "g77_256lj_wrong_scope_stable_checkout_reuse_v1/analysis/"
    "G77_256LJ_POST_COMMIT_PHASE_A_VERIFIER_V1.py"
)
SPEC = importlib.util.spec_from_file_location("g77_256lj_verifier", VERIFIER)
assert SPEC is not None and SPEC.loader is not None
V = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = V
SPEC.loader.exec_module(V)


def test_li_entry_and_equivalent_edge_are_authenticated() -> None:
    entry = V.authenticate_entry()
    failure = V.authenticate_predecessor()
    assert entry["entry_head"] == V.ENTRY_HEAD
    assert failure["failure_class"] == "DUPLICATE_OR_EQUIVALENT_EDGE"
    assert failure["affected_invariant"] == (
        "EXACT_REPOSITORY_AND_RUNTIME_CHECKOUT_IDENTITY_BINDING"
    )


def test_existing_fm_owner_returns_stable_lh_for_wrong_scope_only() -> None:
    reuse = V.authenticate_stable_reuse()
    assert reuse["source_owner"] == (
        "EXISTING_FM_SEALED_RUNTIME_CHECKOUT_IDENTITY_OWNER"
    )
    assert reuse["stable_head"] == V.LH_HEAD
    assert reuse["stable_tree"] == V.LH_TREE
    assert reuse["runtime_role_separated"] is True
    assert reuse["route_count"] == 1


def test_stable_owner_fails_closed_on_tree_drift(monkeypatch: pytest.MonkeyPatch) -> None:
    fm = V.load_module(V.ROOT / V.FM_REL, "g77_256lj_drift_fm")
    monkeypatch.setattr(fm, "WRONG_SCOPE_CHECKOUT_TREE", "0" * 40)
    with pytest.raises(RuntimeError, match="WRONG_SCOPE stable checkout HEAD/TREE mismatch"):
        fm.governed_checkout_identity(
            V.ROOT,
            fm.fresh_context.WRONG_SCOPE,
            V.git("rev-parse", "HEAD"),
            V.git("rev-parse", "HEAD^{tree}"),
        )


def test_current_admission_equality_was_not_weakened() -> None:
    fm = V.load_module(V.ROOT / V.FM_REL, "g77_256lj_admission_fm")
    with pytest.raises(RuntimeError, match="sealed route target is not the current"):
        fm.authenticate_current_committed_jm_route(V.ROOT, V.LH_HEAD, V.LH_TREE)


def test_wrong_scope_er_specialization_preserves_base_and_separates_roles() -> None:
    adapter = V.load_module(V.ROOT / V.ADAPTER_REL, "g77_256lj_role_adapter")
    module = adapter.specialize_er_harness(V.ROOT)
    constants = module.load_authenticated_fresh_operation_context.__code__.co_consts
    assert "repository_head" not in constants
    assert "repository_tree" not in constants
    assert "head" in constants
    assert "tree" in constants
    assert V.sha256(V.ROOT / V.ER_REL) == V.ER_SHA256


def test_lh_contains_all_runtime_dependencies_byte_exactly() -> None:
    assert V.sha256_bytes(V.committed(V.ADAPTER_REL, V.LH_HEAD)) == V.ADAPTER_BASE_SHA256
    assert V.sha256_bytes(V.committed(V.LE_REL, V.LH_HEAD)) == V.LE_SHA256
    assert V.sha256_bytes(V.committed(V.FC_REL, V.LH_HEAD)) == V.FC_SHA256
    assert V.sha256_bytes(V.committed(V.ER_REL, V.LH_HEAD)) == V.ER_SHA256
    assert V.sha256_bytes(V.committed(V.P11_REL, V.LH_HEAD)) == V.P11_SHA256


def test_seed_is_exact_three_member_projection() -> None:
    assert V.authenticate_seed_projection() == {
        "seed_sha256": V.SEED_SHA256,
        "projection": "VERIFIED__EXACT_THREE_MEMBERS",
    }


def test_complete_phase_a_uses_current_admission_and_stable_runtime(tmp_path: Path) -> None:
    result = V.authenticate_postcommit_phase_a(tmp_path)
    assert result["result"] == "PASS__POST_COMMIT_PHASE_A_STATIC_READINESS"
    assert result["repository_head"] == V.git("rev-parse", "HEAD")
    assert result["repository_tree"] == V.git("rev-parse", "HEAD^{tree}")
    assert result["governed_runtime_checkout_head"] == V.LH_HEAD
    assert result["governed_runtime_checkout_tree"] == V.LH_TREE
    counters = {key: value for key, value in result.items() if key.endswith("_count")}
    assert counters and set(counters.values()) == {0}
