"""Advisory-only proposal generation from deterministic reflection evidence."""

from __future__ import annotations

from typing import Any


def advisory_proposals_from_risk(governance_risk: dict[str, Any]) -> list[dict[str, Any]]:
    level = governance_risk.get("level")
    if level == "LOW":
        proposal_type = "OBSERVABILITY_IMPROVEMENT"
        summary = "consider expanding deterministic runtime visibility"
    elif level == "MEDIUM":
        proposal_type = "VALIDATION_IMPROVEMENT"
        summary = "review failed executions before adding runtime capability"
    elif level == "HIGH":
        proposal_type = "REPLAY_CONSISTENCY_REVIEW"
        summary = "inspect replay transitions before further execution milestones"
    else:
        proposal_type = "GOVERNANCE_ESCALATION_REVIEW"
        summary = "require human governance review before further runtime changes"

    return [
        {
            "proposal_type": proposal_type,
            "summary": summary,
            "requires_human_approval": True,
            "allowed_to_execute_automatically": False,
        }
    ]
