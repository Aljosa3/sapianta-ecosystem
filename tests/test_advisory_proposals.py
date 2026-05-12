from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sapianta_bridge.reflection.advisory_proposals import advisory_proposals_from_risk


def test_advisory_proposals_remain_non_authoritative() -> None:
    proposals = advisory_proposals_from_risk({"level": "LOW"})

    assert proposals
    assert all(proposal["requires_human_approval"] is True for proposal in proposals)
    assert all(proposal["allowed_to_execute_automatically"] is False for proposal in proposals)
