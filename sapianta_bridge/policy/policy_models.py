"""Policy model constants and fail-closed validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


ADMISSIBILITY = {"ALLOWED", "RESTRICTED", "BLOCKED", "ESCALATE"}
RISK_LEVELS = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
ESCALATION_CLASSES = {
    "NONE",
    "HUMAN_REVIEW",
    "GOVERNANCE_REVIEW",
    "ARCHITECTURE_REVIEW",
    "SECURITY_REVIEW",
}
INPUT_TYPES = {"REFLECTION_PROPOSAL", "APPROVAL_CANDIDATE", "GOVERNANCE_REQUEST"}


@dataclass(frozen=True)
class PolicyError(Exception):
    field: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {"field": self.field, "reason": self.reason}


def validate_policy_input(value: Any) -> None:
    if not isinstance(value, dict):
        raise PolicyError("policy_input", "policy input must be an object")
    input_type = value.get("input_type")
    if input_type not in INPUT_TYPES:
        raise PolicyError("input_type", "unknown policy input type")
    lineage = value.get("lineage")
    if not isinstance(lineage, dict) or not lineage:
        raise PolicyError("lineage", "lineage is required")
    if any(not isinstance(item, str) or not item.strip() for item in lineage.values() if item is not None):
        raise PolicyError("lineage", "lineage IDs must be non-empty")


def validate_policy_evaluation(value: Any) -> None:
    if not isinstance(value, dict):
        raise PolicyError("policy_evaluation", "policy evaluation must be an object")
    required = (
        "policy_evaluation_id",
        "timestamp",
        "input_type",
        "source_id",
        "classification",
        "policy_violations",
        "evidence",
        "lineage",
        "execution_authority_granted",
    )
    for field in required:
        if field not in value:
            raise PolicyError(field, "missing policy evaluation field")
    classification = value["classification"]
    if not isinstance(classification, dict):
        raise PolicyError("classification", "classification must be an object")
    if classification.get("admissibility") not in ADMISSIBILITY:
        raise PolicyError("classification.admissibility", "unknown admissibility")
    if classification.get("risk_level") not in RISK_LEVELS:
        raise PolicyError("classification.risk_level", "unknown risk level")
    if classification.get("escalation_class") not in ESCALATION_CLASSES:
        raise PolicyError("classification.escalation_class", "unknown escalation class")
    if classification.get("allowed_to_execute_automatically") is not False:
        raise PolicyError(
            "classification.allowed_to_execute_automatically",
            "policy cannot allow automatic execution",
        )
    if value["execution_authority_granted"] is not False:
        raise PolicyError("execution_authority_granted", "policy cannot grant execution authority")
