"""Policy admissibility classification."""

from __future__ import annotations

from .policy_rules import matched_boundary_rules


def classify_admissibility(
    policy_input: dict,
    blocked_capabilities: list[str],
) -> str:
    if blocked_capabilities:
        return "BLOCKED"
    input_type = policy_input["input_type"]
    rules = matched_boundary_rules(policy_input)
    if any(rule.startswith("governance:") for rule in rules):
        return "ESCALATE"
    if any(rule in {"boundary:policy", "boundary:approval", "boundary:enforcement"} for rule in rules):
        return "ESCALATE"
    if any(rule.startswith("boundary:") for rule in rules):
        return "RESTRICTED"
    if input_type == "APPROVAL_CANDIDATE":
        return "ALLOWED"
    if policy_input.get("requires_human_approval") is True:
        return "ALLOWED"
    return "ESCALATE"


def risk_for_admissibility(admissibility: str) -> str:
    if admissibility == "ALLOWED":
        return "LOW"
    if admissibility == "RESTRICTED":
        return "MEDIUM"
    if admissibility == "ESCALATE":
        return "HIGH"
    return "CRITICAL"
