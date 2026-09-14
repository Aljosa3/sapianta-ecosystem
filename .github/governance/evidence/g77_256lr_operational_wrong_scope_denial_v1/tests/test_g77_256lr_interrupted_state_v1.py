from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[5]
LR = ROOT / ".github/governance/evidence/g77_256lr_operational_wrong_scope_denial_v1"
REDUCER_PATH = LR / "analysis/G77_256LR_INTERRUPTED_STATE_REDUCER_V1.py"


def load_reducer():
    spec = importlib.util.spec_from_file_location("g77_256lr_reducer_test", REDUCER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_reconstructed_state_is_exactly_state_b_and_one_shot() -> None:
    reducer = load_reducer()
    reducer.verify()
    reconstruction = reducer.inner(reducer.RECONSTRUCTION, "reconstruction")
    assert reconstruction["recovery_state_class"].startswith("STATE_B__")
    assert reconstruction["cardinality"] == {
        "human_decision_count": 1,
        "authority_created_count": 1,
        "authority_consumed_count": 1,
        "operation_attempt_count": 1,
        "retry_count": 0,
        "constitutional_cardinality_conflict": False,
    }


def test_incomplete_observation_cannot_receive_e05_credit() -> None:
    reducer = load_reducer()
    reconstruction = reducer.inner(reducer.RECONSTRUCTION, "reconstruction")
    operation = reconstruction["operation"]
    assert operation["operation_terminal_evidence_present"] is False
    assert operation["wrong_scope_denial_evidence_present"] is False
    assert operation["denial_class"] == "UNKNOWN"
    assert reconstruction["e05"] == {
        "before": "12/18",
        "lr_credit": 0,
        "after": "12/18",
        "wrong_scope": "UNSAT__OPERATIONAL_PROOF_INCOMPLETE",
    }


def test_authority_is_consumed_terminal_and_nonreusable() -> None:
    reducer = load_reducer()
    reconstruction = reducer.inner(reducer.RECONSTRUCTION, "reconstruction")
    assert reconstruction["authority"]["current_state"] == "CONSUMED__TERMINAL_NONREUSABLE"
    assert reconstruction["authority"]["reusable"] is False
    assert reconstruction["authority"]["terminated"] is True
    assert reducer.POST_RECEIPT.exists() is False


def test_report_has_exact_g48_structure_and_five_questions() -> None:
    report = (LR / "G77_256LR_G48_IMPLEMENTATION_REPORT_V1.md").read_text(encoding="utf-8")
    assert sum(line.startswith("# ") for line in report.splitlines()) == 6
    questions = (
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "Katere nove zmogljivosti (če sploh) nastanejo?",
        "Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "Ali implementacija ustvarja vzporedni tok?",
        "Ali zmanjšuje ali povečuje število produkcijskih poti?",
    )
    assert all(report.count(question) == 1 for question in questions)
    assert report.count("## Reuse Impact Assessment") == 1


def test_preserved_serial_bytes_are_exact() -> None:
    copied = LR / "G77_256LR_INTERRUPTED_SERIAL_LOG_V1.log"
    assert copied.stat().st_size == 43692
    assert hashlib.sha256(copied.read_bytes()).hexdigest() == (
        "72c46b41a40d6b00ffd4a1fccdfc67ae5b4584dfe0bf2bc924aec0f2251c5998"
    )
    value = json.loads((LR / "G77_256LR_INTERRUPTED_STATE_RECONSTRUCTION_V1.json").read_bytes())
    assert value["reconstruction"]["runtime_observation"]["serial_copy_sha256"] == (
        "72c46b41a40d6b00ffd4a1fccdfc67ae5b4584dfe0bf2bc924aec0f2251c5998"
    )
