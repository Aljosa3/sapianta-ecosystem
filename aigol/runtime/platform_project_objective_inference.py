"""Canonical read-only Platform Core project-objective inference composition."""

from __future__ import annotations

import re
from copy import deepcopy
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


PLATFORM_PROJECT_OBJECTIVE_INFERENCE_VERSION = (
    "G21_02_PLATFORM_CORE_PROJECT_OBJECTIVE_INFERENCE_RUNTIME_V1"
)
PLATFORM_PROJECT_OBJECTIVE_INFERENCE_ARTIFACT_V1 = (
    "PLATFORM_CORE_PROJECT_OBJECTIVE_INFERENCE_ARTIFACT_V1"
)

OBJECTIVE_SUFFICIENT = "PROJECT_OBJECTIVE_SUFFICIENT"
OBJECTIVE_INSUFFICIENT = "PROJECT_OBJECTIVE_INSUFFICIENT"
OBJECTIVE_AMBIGUOUS = "PROJECT_OBJECTIVE_AMBIGUOUS"

OBJECTIVE_BOUNDARY_FLAGS = {
    "read_only": True,
    "advisory_only": True,
    "platform_core_authority": True,
    "composition_service_only": True,
    "new_inference_engine_created": False,
    "human_interface_authority": False,
    "clarification_authority_created": False,
    "approval_created": False,
    "execution_authorized": False,
    "provider_invoked": False,
    "worker_invoked": False,
    "repository_mutated": False,
    "governance_modified": False,
    "replay_modified": False,
}

READ_ONLY_VALIDATION_ACTIONS = ("validate", "verify", "confirm")
NON_MUTATION_CONSTRAINTS = (
    "do not implement",
    "don't implement",
    "do not modify",
    "no repository mutation",
    "no worker execution",
    "read-only result only",
    "read only result only",
    "without implementation",
    "no implementation",
)


def infer_platform_project_objective(
    *,
    request: str,
    development_intent: dict[str, Any] | None = None,
    workspace_state: dict[str, Any] | None = None,
    project_guidance: dict[str, Any] | None = None,
    created_at: str = "2026-07-11T00:00:00Z",
) -> dict[str, Any]:
    """Compose existing intent and workspace evidence into one objective artifact."""

    prompt = _require_string(request, "request")
    normalized = " ".join(prompt.split())
    lowered = normalized.lower()
    intent = development_intent if isinstance(development_intent, dict) else {}
    workspace = workspace_state if isinstance(workspace_state, dict) else {}
    guidance = project_guidance if isinstance(project_guidance, dict) else {}
    discovery = (
        intent.get("candidate_capability_discovery")
        if isinstance(intent.get("candidate_capability_discovery"), dict)
        else {}
    )
    subject = _objective_subject(normalized, discovery)
    requested_outcomes = _requested_outcomes(lowered)
    source_work_type = str(intent.get("requested_work_type") or intent.get("work_type") or "")
    requested_work_type, work_type_source = _objective_work_type(lowered, source_work_type)
    prepared_work_type = requested_work_type
    ambiguity = discovery.get("ambiguity_remaining_after_deterministic_analysis") is True
    conflicting_boundary = (
        intent.get("work_type_conflict_detected") is True
        and work_type_source != "EXPLICIT_NON_MUTATING_OBJECTIVE"
    )
    missing_information: list[str] = []
    if not subject:
        missing_information.append("project objective subject")
    if not requested_outcomes:
        missing_information.append("requested governed outcome")
    if not requested_work_type:
        missing_information.append("governed work type")
    if ambiguity:
        status = OBJECTIVE_AMBIGUOUS
    elif missing_information or conflicting_boundary:
        status = OBJECTIVE_INSUFFICIENT
    else:
        status = OBJECTIVE_SUFFICIENT
    sufficient = status == OBJECTIVE_SUFFICIENT
    satisfied_slots = _satisfied_semantic_slots(
        lowered=lowered,
        subject=subject,
        requested_outcomes=requested_outcomes,
        sufficient=sufficient,
    )
    canonical_objective = _canonical_objective(
        subject=subject,
        requested_outcomes=requested_outcomes,
        requested_work_type=requested_work_type,
    )
    artifact = {
        "artifact_type": PLATFORM_PROJECT_OBJECTIVE_INFERENCE_ARTIFACT_V1,
        "runtime_version": PLATFORM_PROJECT_OBJECTIVE_INFERENCE_VERSION,
        "created_at": _require_string(created_at, "created_at"),
        "source_request": prompt,
        "source_request_hash": replay_hash(prompt),
        "canonical_project_objective": canonical_objective,
        "objective_subject": subject,
        "requested_outcomes": requested_outcomes,
        "requested_work_type": requested_work_type,
        "prepared_work_type": prepared_work_type,
        "source_development_intent_work_type": source_work_type,
        "objective_work_type_source": work_type_source,
        "work_type_binding_required": requested_work_type != source_work_type,
        "mutation_allowed": requested_work_type == "IMPLEMENTATION" and intent.get("mutation_allowed") is True,
        "runtime_implementation": requested_work_type == "IMPLEMENTATION" and intent.get("runtime_implementation") is True,
        "objective_status": status,
        "objective_sufficient": sufficient,
        "objective_ambiguity_detected": ambiguity,
        "material_boundary_conflict_detected": conflicting_boundary,
        "missing_material_information": missing_information,
        "satisfied_semantic_slots": satisfied_slots,
        "clarification_required": not sufficient,
        "clarification_reason": (
            "multiple deterministic objective candidates remain"
            if ambiguity
            else "objective evidence is incomplete or conflicting"
            if not sufficient
            else None
        ),
        "selected_capability_target": discovery.get("selected_goal_target"),
        "candidate_capabilities": deepcopy(discovery.get("candidate_capabilities") or []),
        "active_workspace_objective": workspace.get("active_development_objective"),
        "project_guidance_objective": guidance.get("active_development_objective"),
        "development_intent_hash": intent.get("artifact_hash"),
        "workspace_state_hash": workspace.get("artifact_hash"),
        "project_guidance_hash": replay_hash(guidance),
        "coverage_composition_eligible": sufficient,
        "development_plan_composition_eligible": sufficient,
        "reused_platform_core_services": [
            "HUMAN_INTENT_RESOLUTION",
            "PLATFORM_CORE_DEVELOPMENT_INTENT_RESOLUTION",
            "PLATFORM_CORE_CANDIDATE_CAPABILITY_DISCOVERY",
            "PLATFORM_CORE_PROJECT_GUIDANCE",
            "PLATFORM_CORE_CLARIFICATION_CONTEXT_SUFFICIENCY",
            "PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_RUNTIME",
            "PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_RUNTIME",
        ],
        "replay_visible": True,
        "boundary_flags": deepcopy(OBJECTIVE_BOUNDARY_FLAGS),
        **OBJECTIVE_BOUNDARY_FLAGS,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def interpret_request_clause_roles(request: str) -> dict[str, Any]:
    """Return bounded lexical clause roles used by existing interpretation services."""

    prompt = _require_string(request, "request")
    clauses = [
        " ".join(part.split())
        for part in re.split(r"(?:\r?\n|(?<=[.!?;])\s+)", prompt)
        if part.strip()
    ]
    interpreted: list[dict[str, Any]] = []
    for clause in clauses:
        lowered = clause.lower()
        quoted = bool(re.search(r"(?:^|\s)(?:>|output:|status:|result:)|[`\"'].*[`\"']", clause))
        prohibition = any(term in lowered for term in NON_MUTATION_CONSTRAINTS)
        reference = any(
            term in lowered
            for term in (
                "mentioned", "mentions", "referenced", "references", "according to",
                "runtime output", "runtime evidence", "architectural boundary",
                "architecture boundary", "lifecycle observation", "behaved correctly",
                "does not belong", "do not belong",
            )
        )
        requested_action = bool(
            re.search(
                r"\b(?:audit|inspect|review|analyse|analyze|evaluate|validate|verify|confirm|"
                r"implement|modify|change|extend|improve|build|create|add|fix|repair|update|"
                r"make|simplify|reuse)\b",
                lowered,
            )
        ) or bool(
            re.search(r"\bshould\b.+\b(?:belong|change|enable)\b", lowered)
            or re.search(r"\b(?:require|requires)\b.+\bbindings?\b", lowered)
            or re.search(r"\bcan become\b", lowered)
            or re.search(r"\bwhere is\b.+\bimplemented\b", lowered)
        )
        requested_action = requested_action and not prohibition and not reference and not quoted
        interpreted.append(
            {
                "text": clause,
                "normalized_text": lowered,
                "requested_action": requested_action,
                "prohibition": prohibition,
                "safety_constraint": prohibition or "preserve" in lowered or "must not" in lowered,
                "quoted_runtime_evidence": quoted,
                "architectural_reference": reference or "architectural" in lowered,
                "tool_interface_reference": bool(
                    re.search(r"(?:\./aicli|\baicli\b|human interface|provider|worker)", lowered)
                ),
                "capability_target_eligible": requested_action and not quoted and not reference,
            }
        )
    lowered_prompt = " ".join(prompt.lower().split())
    return {
        "clauses": interpreted,
        "requested_action_clauses": [item["text"] for item in interpreted if item["requested_action"]],
        "prohibition_clauses": [item["text"] for item in interpreted if item["prohibition"]],
        "capability_target_clauses": [
            item["text"] for item in interpreted if item["capability_target_eligible"]
        ],
        "non_mutation_constraint_detected": any(
            term in lowered_prompt for term in NON_MUTATION_CONSTRAINTS
        ),
        "read_only_validation_action_detected": any(
            re.search(rf"\b{action}\b", item["normalized_text"])
            for action in READ_ONLY_VALIDATION_ACTIONS
            for item in interpreted
            if item["requested_action"]
        ),
        "read_only_inspection_action_detected": any(
            re.search(r"\b(?:audit|inspect|review|analyse|analyze|evaluate)\b", item["normalized_text"])
            for item in interpreted
            if item["requested_action"]
        ),
    }


def validate_platform_project_objective(artifact: dict[str, Any]) -> dict[str, Any]:
    """Fail closed unless the objective artifact is canonical and immutable."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("project objective artifact must be a dict")
    if artifact.get("artifact_type") != PLATFORM_PROJECT_OBJECTIVE_INFERENCE_ARTIFACT_V1:
        raise FailClosedRuntimeError("project objective artifact type is invalid")
    if artifact.get("runtime_version") != PLATFORM_PROJECT_OBJECTIVE_INFERENCE_VERSION:
        raise FailClosedRuntimeError("project objective runtime version is invalid")
    if artifact.get("objective_status") not in {
        OBJECTIVE_SUFFICIENT,
        OBJECTIVE_INSUFFICIENT,
        OBJECTIVE_AMBIGUOUS,
    }:
        raise FailClosedRuntimeError("project objective status is invalid")
    for field_name, expected in OBJECTIVE_BOUNDARY_FLAGS.items():
        if artifact.get(field_name) is not expected:
            raise FailClosedRuntimeError("project objective boundary flags are invalid")
        flags = artifact.get("boundary_flags")
        if not isinstance(flags, dict) or flags.get(field_name) is not expected:
            raise FailClosedRuntimeError("project objective boundary flags are invalid")
    artifact_hash = artifact.get("artifact_hash")
    body = deepcopy(artifact)
    body.pop("artifact_hash", None)
    if not isinstance(artifact_hash, str) or replay_hash(body) != artifact_hash:
        raise FailClosedRuntimeError("project objective artifact hash mismatch")
    return deepcopy(artifact)


def _objective_subject(request: str, discovery: dict[str, Any]) -> str:
    patterns = (
        r"\bfor implementing\s+(.+?)(?:\.|;|\n|$)",
        r"\b(?:audit|review|analyse|analyze|validate|verify|confirm)\s+(.+?)(?:\.|;|\n|$)",
        r"\b(?:implement|build|create|add|improve)\s+(.+?)(?:\.|;|\n|$)",
    )
    for pattern in patterns:
        match = re.search(pattern, request, flags=re.IGNORECASE)
        if match:
            subject = " ".join(match.group(1).strip(" .,:;").split())
            if subject:
                return subject
    selected = discovery.get("selected_candidate_capability")
    if isinstance(selected, dict):
        value = selected.get("display_name")
        if isinstance(value, str) and value.strip() and value != "active project objective":
            return value.strip()
    return ""


def _requested_outcomes(lowered: str) -> list[str]:
    outcomes: list[str] = []
    signals = (
        ("existing_capability_discovery", ("what already exists", "current platform core capabilities", "existing capability")),
        ("reuse_analysis", ("what can be reused", "reuse", "reusable")),
        ("certified_composition_discovery", ("certified composition", "certified capabilities")),
        ("residual_gap_analysis", ("what is missing", "residual gap", "uncovered")),
        ("governed_development_plan", ("governed development plan", "development composition plan")),
        ("implementation", ("implement ", "build ", "create ", "add ")),
        ("audit_or_analysis", ("audit", "analyse", "analyze", "review", "validate", "verify", "confirm")),
    )
    for outcome, terms in signals:
        if any(term in lowered for term in terms):
            outcomes.append(outcome)
    if any(
        phrase in lowered
        for phrase in ("do not implement", "don't implement", "no implementation", "without implementation")
    ):
        outcomes = [outcome for outcome in outcomes if outcome != "implementation"]
    return outcomes


def _satisfied_semantic_slots(
    *,
    lowered: str,
    subject: str,
    requested_outcomes: list[str],
    sufficient: bool,
) -> list[str]:
    if not sufficient:
        return []
    slots = ["capability_target", "desired_outcome"]
    if "governed_development_plan" in requested_outcomes or "audit_or_analysis" in requested_outcomes:
        slots.extend(("architecture_subject", "architecture_outcome"))
    if "reuse_analysis" in requested_outcomes and "residual_gap_analysis" in requested_outcomes:
        slots.extend(("reuse_delta", "reuse_goal"))
    if "implementation" in requested_outcomes and subject:
        slots.append("implementation_specificity")
    if any(term in lowered for term in ("do not implement", "no implementation", "preserve", "boundary")):
        slots.append("implementation_constraints")
    return list(dict.fromkeys(slots))


def _objective_work_type(lowered: str, source_work_type: str) -> tuple[str, str]:
    roles = interpret_request_clause_roles(lowered)
    non_mutation = roles["non_mutation_constraint_detected"]
    audit = any(term in lowered for term in ("audit", "analyse", "analyze", "review")) or roles[
        "read_only_validation_action_detected"
    ]
    if non_mutation and audit:
        return "AUDIT_ONLY", "EXPLICIT_NON_MUTATING_OBJECTIVE"
    return source_work_type, "DEVELOPMENT_INTENT_RESOLUTION"


def _canonical_objective(
    *, subject: str, requested_outcomes: list[str], requested_work_type: str
) -> str:
    if not subject:
        return ""
    outcomes = ", ".join(item.replace("_", " ") for item in requested_outcomes)
    suffix = f" through {outcomes}" if outcomes else ""
    work_type = f" as {requested_work_type}" if requested_work_type else ""
    return f"Resolve {subject}{suffix}{work_type}."


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


__all__ = [
    "OBJECTIVE_AMBIGUOUS",
    "OBJECTIVE_INSUFFICIENT",
    "OBJECTIVE_SUFFICIENT",
    "PLATFORM_PROJECT_OBJECTIVE_INFERENCE_ARTIFACT_V1",
    "PLATFORM_PROJECT_OBJECTIVE_INFERENCE_VERSION",
    "infer_platform_project_objective",
    "interpret_request_clause_roles",
    "validate_platform_project_objective",
]
