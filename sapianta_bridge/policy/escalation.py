"""Deterministic policy escalation class assignment."""

from __future__ import annotations


def escalation_class(
    *,
    admissibility: str,
    input_type: str,
    matched_rules: list[str],
    blocked_capabilities: list[str],
) -> str:
    if blocked_capabilities:
        security_markers = {
            "codex_invocation",
            "transport_invocation",
            "recursive_execution",
            "auto_merge",
            "auto_push",
            "protocol_enforcement_bypass",
        }
        if any(capability in security_markers for capability in blocked_capabilities):
            return "SECURITY_REVIEW"
        return "GOVERNANCE_REVIEW"
    if any(rule.startswith("security:") for rule in matched_rules):
        return "SECURITY_REVIEW"
    if admissibility == "ESCALATE":
        return "GOVERNANCE_REVIEW"
    if admissibility == "RESTRICTED":
        return "ARCHITECTURE_REVIEW"
    if input_type == "APPROVAL_CANDIDATE":
        return "HUMAN_REVIEW"
    return "NONE"
