from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sapianta_bridge.protocol.lifecycle import validate_transition


def test_invalid_lifecycle_transition_rejected() -> None:
    result = validate_transition("CREATED", "EXECUTING")
    assert not result.valid
    assert result.errors[0]["reason"] == "invalid lifecycle transition"


def test_closed_state_is_terminal() -> None:
    result = validate_transition("CLOSED", "VALIDATED")
    assert not result.valid
    assert result.errors[0]["reason"] == "CLOSED is terminal"


def test_quarantined_state_is_terminal() -> None:
    result = validate_transition("QUARANTINED", "VALIDATED")
    assert not result.valid
    assert result.errors[0]["reason"] == "QUARANTINED is terminal"


def test_fail_states_require_evidence() -> None:
    missing_evidence = validate_transition("EXECUTING", "EXECUTION_FAILED")
    assert not missing_evidence.valid
    assert missing_evidence.errors[0]["field"] == "evidence"

    with_evidence = validate_transition(
        "EXECUTING",
        "EXECUTION_FAILED",
        evidence={"reason": "transport unavailable"},
    )
    assert with_evidence.valid
