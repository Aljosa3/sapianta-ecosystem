"""Classification-only governance policy engine."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sapianta_bridge.protocol.hashing import compute_hash
from sapianta_bridge.transport.transport_config import TransportConfig

from .admissibility import classify_admissibility, risk_for_admissibility
from .escalation import escalation_class
from .policy_evidence import write_policy_evaluation
from .policy_models import PolicyError, validate_policy_input, validate_policy_evaluation
from .policy_rules import detect_forbidden_capabilities, matched_boundary_rules


def _source_id(policy_input: dict[str, Any]) -> str:
    for field in ("approval_id", "proposal_id", "reflection_id", "request_id"):
        value = policy_input.get(field)
        if isinstance(value, str) and value.strip():
            return value
    lineage = policy_input.get("lineage", {})
    for field in ("source_reflection_id", "source_task_id"):
        value = lineage.get(field)
        if isinstance(value, str) and value.strip():
            return value
    return "UNKNOWN"


def build_policy_evaluation(
    policy_input: dict[str, Any],
    *,
    timestamp: str | None = None,
) -> dict[str, Any]:
    validate_policy_input(policy_input)
    blocked = detect_forbidden_capabilities(policy_input)
    matched = matched_boundary_rules(policy_input)
    admissibility = classify_admissibility(policy_input, blocked)
    escalation = escalation_class(
        admissibility=admissibility,
        input_type=policy_input["input_type"],
        matched_rules=matched,
        blocked_capabilities=blocked,
    )
    risk = risk_for_admissibility(admissibility)
    effective_timestamp = timestamp or datetime.now(timezone.utc).isoformat()
    seed = {
        "timestamp": effective_timestamp,
        "input": policy_input,
        "admissibility": admissibility,
    }
    violations = [{"capability": capability, "reason": "forbidden capability requested"} for capability in blocked]
    evaluation = {
        "policy_evaluation_id": f"POLICY-{compute_hash(seed)[:16].upper()}",
        "timestamp": effective_timestamp,
        "input_type": policy_input["input_type"],
        "source_id": _source_id(policy_input),
        "classification": {
            "admissibility": admissibility,
            "risk_level": risk,
            "escalation_class": escalation,
            "requires_human_approval": True,
            "allowed_to_execute_automatically": False,
        },
        "policy_violations": violations,
        "evidence": {
            "matched_rules": matched,
            "blocked_capabilities": blocked,
            "reason": _reason(admissibility, blocked, matched),
        },
        "lineage": policy_input["lineage"],
        "execution_authority_granted": False,
    }
    validate_policy_evaluation(evaluation)
    return evaluation


def evaluate_policy_input(
    policy_input: dict[str, Any],
    config: TransportConfig | None = None,
    *,
    timestamp: str | None = None,
) -> dict[str, Any]:
    try:
        evaluation = build_policy_evaluation(policy_input, timestamp=timestamp)
    except PolicyError:
        raise
    path = write_policy_evaluation(evaluation, config)
    return {"evaluated": True, "policy_evaluation_path": str(path), "evaluation": evaluation}


def fail_closed_evaluation(
    *,
    field: str,
    reason: str,
    timestamp: str | None = None,
) -> dict[str, Any]:
    effective_timestamp = timestamp or datetime.now(timezone.utc).isoformat()
    return {
        "policy_evaluation_id": f"POLICY-{compute_hash({'field': field, 'reason': reason, 'timestamp': effective_timestamp})[:16].upper()}",
        "timestamp": effective_timestamp,
        "input_type": "UNKNOWN",
        "source_id": "UNKNOWN",
        "classification": {
            "admissibility": "BLOCKED",
            "risk_level": "CRITICAL",
            "escalation_class": "GOVERNANCE_REVIEW",
            "requires_human_approval": True,
            "allowed_to_execute_automatically": False,
        },
        "policy_violations": [{"field": field, "reason": reason}],
        "evidence": {
            "matched_rules": [],
            "blocked_capabilities": ["policy_uncertainty"],
            "reason": reason,
        },
        "lineage": {},
        "execution_authority_granted": False,
    }


def _reason(admissibility: str, blocked: list[str], matched: list[str]) -> str:
    if blocked:
        return "forbidden capability request detected"
    if admissibility == "ESCALATE":
        return "governance or authority boundary requires escalation"
    if admissibility == "RESTRICTED":
        return "runtime or architecture boundary requires restricted handling"
    if matched:
        return "policy matched advisory evidence without forbidden capability"
    return "advisory-only input with human approval boundary preserved"
