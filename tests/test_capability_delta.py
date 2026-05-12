from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sapianta_bridge.reflection.capability_delta import capability_delta_from_evidence


def test_capability_delta_conservative() -> None:
    delta = capability_delta_from_evidence(
        {"final_state": "FAILED"},
        {"total_executions": 1},
    )

    assert delta == {
        "detected": False,
        "summary": "capability delta not certified because latest execution failed",
    }
