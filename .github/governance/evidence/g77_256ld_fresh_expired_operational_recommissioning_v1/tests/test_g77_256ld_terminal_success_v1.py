"""Focused verification of the terminal G77-256LD EXPIRED observation."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[5]
LD = ROOT / ".github/governance/evidence/g77_256ld_fresh_expired_operational_recommissioning_v1"
REDUCER = LD / "analysis/G77_256LD_TERMINAL_SUCCESS_REDUCER_V1.py"
SPEC = importlib.util.spec_from_file_location("g77_256ld_terminal_reducer", REDUCER)
assert SPEC is not None and SPEC.loader is not None
R = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = R
SPEC.loader.exec_module(R)


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        assert key not in result
        result[key] = value
    return result


def load(path: Path) -> dict:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique_object)
    assert isinstance(value, dict)
    assert raw == canonical_bytes(value)
    return value


def inner(path: Path, key: str) -> dict:
    envelope = load(path)
    value = envelope[key]
    assert isinstance(value, dict)
    assert envelope[f"{key}_sha256"] == hashlib.sha256(canonical_bytes(value)).hexdigest()
    return value


def test_terminal_reducer_reauthenticates_exact_success() -> None:
    R.verify()
    reduction = inner(R.OUTPUT, "reduction")
    assert reduction["terminal"] == R.TERMINAL
    assert reduction["result_class"] == "SUCCESSFUL_ACCEPTANCE_OBSERVATION"
    assert reduction["operational_observation"]["denial_error"] == "one-use Human act expired before PRECLAIM"
    assert reduction["operational_observation"]["teardown_state"] == "COMPLETE"


def test_exact_one_shot_counters_and_e05_credit() -> None:
    reduction = inner(R.OUTPUT, "reduction")
    counters = reduction["operational_counters"]
    assert counters["human_authority_source_count"] == 1
    assert counters["authority_consumption_count"] == 1
    assert counters["operation_attempt_count"] == 1
    assert counters["operation_request_count"] == 1
    assert counters["expired_denial_count"] == 1
    assert counters["p11_entry_count"] == 0
    assert counters["protected_invocation_count"] == 0
    assert counters["protected_effect_count"] == 0
    assert counters["second_operation_count"] == 0
    assert counters["retry_count"] == 0
    assert counters["repair_retry_count"] == 0
    assert counters["replay_count"] == 0
    assert reduction["e05"] == {
        "after": "VERIFIED__12_OF_18",
        "before": "VERIFIED__11_OF_18",
        "current_generation_credit": "VERIFIED__1",
        "expired": "VERIFIED__PROVEN_OPERATIONALLY",
        "frontier_after": "VERIFIED__6_UNSATISFIED_OF_18",
        "frontier_before": "VERIFIED__7_UNSATISFIED_OF_18",
    }
    assert reduction["failure_novelty_and_convergence_check"]["convergence_signal"] == (
        "LD_FRESH_EXPIRED_OPERATIONAL_ACCEPTANCE_OBSERVED__E05_FRONTIER_MOVED_11_TO_12"
    )
    assert reduction["governance"]["cognition_assisted_handoff"] == (
        "DURABLE_EVIDENCE_ONLY__NO_HIDDEN_REASONING_CONTINUITY"
    )


def test_human_source_authority_context_and_reference_bindings() -> None:
    source = LD / "G77_256LD_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
    handoff = inner(LD / "G77_256LD_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json", "authorization")
    checkpoint = load(LD / "operation_state/runtime_export/G77_256LD_AUTHORITY_CHECKPOINT_V1.json")
    assert len(source.read_bytes()) == 1381
    assert hashlib.sha256(source.read_bytes()).hexdigest() == R.SOURCE_SHA256
    assert handoff["authorization_source_sha256"] == R.SOURCE_SHA256
    assert handoff["authorized_context_sha256"] == R.CONTEXT_SHA256
    assert checkpoint["authority_act_preimage"]["metadata"]["authorized_context_sha256"] == R.CONTEXT_SHA256
    assert checkpoint["input_record_preimage"]["authorization_reference"] == checkpoint["authority_act_identity"]


def test_every_ld_json_is_unique_key_canonical_and_supported_seals_hold() -> None:
    seal_keys = ("authorization", "invocation_binding", "checkpoint", "attempt", "result", "request", "proof", "reduction", "manifest", "seal")
    for path in LD.rglob("*.json"):
        value = load(path)
        for key in seal_keys:
            if isinstance(value.get(key), dict) and f"{key}_sha256" in value:
                assert value[f"{key}_sha256"] == hashlib.sha256(canonical_bytes(value[key])).hexdigest(), path


def test_g48_exactly_six_h1_and_exactly_five_reuse_questions() -> None:
    report = (LD / "G77_256LD_G48_IMPLEMENTATION_REPORT_V1.md").read_text(encoding="utf-8")
    assert re.findall(r"^# .+$", report, re.MULTILINE) == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    assert len(re.findall(r"^\d\. (?:Katere|Ali)", report, re.MULTILINE)) == 5
    assert report.rstrip().endswith(f"`{R.TERMINAL}`")


def test_bounded_mutation_and_no_successor_generation() -> None:
    assert not any(ROOT.glob(".github/governance/evidence/g77_256le*"))
    assert not any(path.name == "G77_256LE" for path in ROOT.rglob("*"))
