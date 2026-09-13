"""Focused tests for the G77-256LD authority-free Phase-A terminal."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[5]
VERIFIER = ROOT / (
    ".github/governance/evidence/"
    "g77_256ld_fresh_expired_operational_recommissioning_v1/analysis/"
    "G77_256LD_PHASE_A_SUCCESS_VERIFIER_V1.py"
)
SPEC = importlib.util.spec_from_file_location("g77_256ld_phase_a_verifier", VERIFIER)
assert SPEC is not None and SPEC.loader is not None
V = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = V
SPEC.loader.exec_module(V)


def test_repository_continuation_and_mutation_scope() -> None:
    V.verify_repository_scope()


def test_phase_a_terminal_and_zero_counters() -> None:
    result = V.verify_phase_a()
    assert result["terminal"] == V.TERMINAL
    assert result["ready_for_human_decision"] == "VERIFIED"
    for key in (
        "human_authority_created",
        "authority_consumption_count",
        "qemu_start_count",
        "vm_start_count",
        "operation_attempt_count",
        "e05_credit",
    ):
        assert result[key] == 0


def test_e05_and_ex_accounting_remain_unchanged() -> None:
    result = V.verify_phase_a()
    assert result["e05_state"] == "VERIFIED__11_OF_18"
    assert result["e05_frontier"] == "VERIFIED__7_UNSATISFIED_OF_18"
    assert result["ex_reused"] == "VERIFIED__17_OF_17"
    assert result["ex_reconstructed"] == "VERIFIED__0"
