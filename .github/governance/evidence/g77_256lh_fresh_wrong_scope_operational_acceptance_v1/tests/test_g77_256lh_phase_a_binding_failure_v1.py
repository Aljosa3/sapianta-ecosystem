"""Focused validation for the G77-256LH Phase-A binding-failure terminal."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[5]
VERIFIER = ROOT / (
    ".github/governance/evidence/"
    "g77_256lh_fresh_wrong_scope_operational_acceptance_v1/analysis/"
    "G77_256LH_PHASE_A_BINDING_FAILURE_VERIFIER_V1.py"
)
SPEC = importlib.util.spec_from_file_location("g77_256lh_failure", VERIFIER)
assert SPEC is not None and SPEC.loader is not None
V = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = V
SPEC.loader.exec_module(V)


def test_phase_a_fails_closed_before_human_barrier() -> None:
    result = V.verify()
    assert result["terminal"] == V.TERMINAL
    assert result["failure_class"] == "IMPLEMENTATION_REGRESSION"
    assert result["differing_argument_indexes"] == [2, 3]
    assert result["ready_for_human_decision"] is False


def test_all_operational_counters_and_e05_credit_remain_zero() -> None:
    result = V.verify()
    assert result["operational_counters"]
    assert set(result["operational_counters"].values()) == {0}
    assert result["e05"]["after"] == "12/18"
    assert result["e05"]["credit"] == 0


def test_ex_is_reused_without_reconstruction() -> None:
    result = V.verify()
    assert result["ex"]["reused"] == "VERIFIED__17_OF_17"
    assert result["ex"]["reconstructed"] == "VERIFIED__0"
