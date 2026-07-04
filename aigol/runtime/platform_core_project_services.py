"""Platform Core project workspace, guidance, and knowledge reuse services."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.native_development_task_intake_runtime import is_native_development_prompt
from aigol.runtime.transport.serialization import replay_hash


PLATFORM_CORE_PROJECT_SERVICES_VERSION = "G14_08A_PLATFORM_CORE_PROJECT_SERVICES_EXTRACTION_V1"
PLATFORM_CORE_PERSISTENT_WORKSPACE_VERSION = "G14_05_PERSISTENT_DEVELOPMENT_WORKSPACE_AND_PROJECT_CONTINUITY_V1"
PLATFORM_CORE_PROJECT_GUIDANCE_VERSION = "G14_06_PROJECT_GUIDANCE_AND_DEVELOPMENT_ASSISTANT_V1"
PLATFORM_CORE_PROJECT_KNOWLEDGE_REUSE_VERSION = (
    "G14_08_PROJECT_KNOWLEDGE_REUSE_AND_CONTEXTUAL_TASK_MAPPING_V1"
)
PLATFORM_CORE_DEVELOPMENT_INTENT_RESOLUTION_VERSION = (
    "G14_19_CANONICAL_DEVELOPMENT_INTENT_RESOLUTION_UNIFICATION_V1"
)


def build_persistent_workspace_state_artifact(
    *,
    conversation_id: str,
    command_name: str,
    prior_state: dict[str, Any] | None,
    completion: dict[str, Any],
    turn_results: list[dict[str, Any]],
    pending_clarification: dict[str, Any] | None,
    pending_summary: dict[str, Any] | None,
    session_root: Path,
    created_at: str,
    workspace: str | Path,
) -> dict[str, Any]:
    """Build the authoritative Platform Core project workspace snapshot."""

    prior_history = prior_state.get("implementation_history", []) if isinstance(prior_state, dict) else []
    if not isinstance(prior_history, list):
        prior_history = []
    new_history = [
        {
            "runtime_binding_status": result.get("runtime_binding_status"),
            "runtime_replay_reference": result.get("runtime_replay_reference") or result.get("replay_reference"),
            "latest_prompt_hash": replay_hash(result.get("latest_prompt", "")),
            "replay_certification_reached": result.get("replay_certification_reached") is True,
        }
        for result in turn_results
    ]
    implementation_history = [*deepcopy(prior_history), *new_history]
    active_objective = active_development_objective(
        pending_clarification=pending_clarification,
        pending_summary=pending_summary,
        implementation_history=implementation_history,
    )
    pending_approval = pending_summary is not None
    pending_clarification_present = pending_clarification is not None
    guidance = project_guidance_model(
        active_objective=active_objective,
        pending_clarification=pending_clarification_present,
        pending_approval=pending_approval,
        implementation_history_count=len(implementation_history),
        runtime_bound_count=sum(
            1 for result in turn_results if result.get("runtime_binding_status") == "AIGOL_NEXT_RUNTIME_BOUND"
        ),
    )
    knowledge_index = project_knowledge_index_model(
        prior_state=prior_state,
        pending_summary=pending_summary,
        guidance=guidance,
        implementation_history=implementation_history,
    )
    artifact = {
        "artifact_type": "ACLI_NEXT_PERSISTENT_WORKSPACE_STATE_ARTIFACT_V1",
        "runtime_version": PLATFORM_CORE_PERSISTENT_WORKSPACE_VERSION,
        "platform_core_project_services_version": PLATFORM_CORE_PROJECT_SERVICES_VERSION,
        "command": command_name,
        "session_id": conversation_id,
        "workspace": str(Path(workspace)),
        "created_at": require_string(created_at, "created_at"),
        "session_root": str(session_root),
        "completion_reference": completion.get("replay_reference"),
        "completion_hash": completion.get("artifact_hash"),
        "prior_workspace_state_reference": prior_state.get("replay_reference") if isinstance(prior_state, dict) else None,
        "active_development_objective": active_objective,
        "pending_clarification_request": deepcopy(pending_clarification),
        "pending_implementation_summary": deepcopy(pending_summary),
        "pending_approval": pending_approval,
        "pending_approval_kind": "IMPLEMENTATION_SUMMARY_APPROVAL" if pending_approval else None,
        "implementation_history": implementation_history,
        "implementation_history_count": len(implementation_history),
        "project_guidance": guidance,
        "project_knowledge_index": knowledge_index,
        "recent_governed_decisions": [
            {
                "decision": "HUMAN_CONFIRMATION_RECORDED",
                "runtime_binding_status": result.get("runtime_binding_status"),
                "replay_certification_reached": result.get("replay_certification_reached") is True,
            }
            for result in turn_results
            if result.get("runtime_binding_status")
        ],
        "resumable_conversational_context": True,
        "replay_visible": True,
        "acli_next_authorizes": False,
        "acli_next_executes": False,
        "platform_core_runtime_delegated": True,
        "project_workspace_authority": "PLATFORM_CORE",
        "project_guidance_authority": "PLATFORM_CORE",
        "project_knowledge_reuse_authority": "PLATFORM_CORE",
        "contextual_task_mapping_authority": "PLATFORM_CORE",
        "replay_reference": str(session_root / "workspace_state"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def active_development_objective(
    *,
    pending_clarification: dict[str, Any] | None,
    pending_summary: dict[str, Any] | None,
    implementation_history: list[dict[str, Any]],
) -> str | None:
    if isinstance(pending_summary, dict):
        return str(pending_summary.get("original_message") or pending_summary.get("refined_message") or "")
    if isinstance(pending_clarification, dict):
        return str(pending_clarification.get("original_message") or "")
    if implementation_history:
        return "recent governed development runtime completed"
    return None


def project_guidance_from_workspace_state(workspace_state: dict[str, Any]) -> dict[str, Any]:
    existing = workspace_state.get("project_guidance")
    if isinstance(existing, dict):
        return deepcopy(existing)
    return project_guidance_model(
        active_objective=workspace_state.get("active_development_objective"),
        pending_clarification=workspace_state.get("pending_clarification_request") is not None,
        pending_approval=workspace_state.get("pending_approval") is True,
        implementation_history_count=int(workspace_state.get("implementation_history_count") or 0),
        runtime_bound_count=sum(
            1
            for item in workspace_state.get("implementation_history", [])
            if isinstance(item, dict) and item.get("runtime_binding_status") == "AIGOL_NEXT_RUNTIME_BOUND"
        ),
    )


def project_guidance_model(
    *,
    active_objective: Any,
    pending_clarification: bool,
    pending_approval: bool,
    implementation_history_count: int,
    runtime_bound_count: int,
) -> dict[str, Any]:
    objective = str(active_objective or "No active development objective")
    pending_work = guidance_pending_work(
        active_objective=objective,
        pending_clarification=pending_clarification,
        pending_approval=pending_approval,
    )
    return {
        "guidance_version": PLATFORM_CORE_PROJECT_GUIDANCE_VERSION,
        "platform_core_project_services_version": PLATFORM_CORE_PROJECT_SERVICES_VERSION,
        "guidance_source": "deterministic_workspace_state",
        "guidance_authority": "PLATFORM_CORE",
        "advisory_only": True,
        "active_generation": guidance_generation(objective),
        "active_milestone": guidance_milestone(objective),
        "active_development_objective": objective,
        "pending_implementation_work": pending_work,
        "pending_approvals": ["IMPLEMENTATION_SUMMARY_APPROVAL"] if pending_approval else [],
        "unresolved_clarification": pending_clarification,
        "implementation_history_count": int(implementation_history_count),
        "runtime_bound_count": int(runtime_bound_count),
        "recommended_next_governed_action": guidance_next_action(
            pending_clarification=pending_clarification,
            pending_approval=pending_approval,
            implementation_history_count=implementation_history_count,
        ),
        "requires_explicit_human_approval": pending_approval,
        "acli_next_executes_recommendation": False,
    }


def guidance_generation(objective: str) -> str:
    marker = find_generation_marker(objective)
    return f"Generation {marker}" if marker else "Generation 14"


def guidance_milestone(objective: str) -> str:
    for part in objective.replace("-", "_").split():
        normalized = part.strip(".,:;()[]{}")
        if "_V" in normalized and normalized.rsplit("_V", 1)[-1].isdigit():
            return normalized
    return "AIGOL_GENERIC_DEVELOPMENT_TASK_V1"


def find_generation_marker(value: str) -> str | None:
    for token in value.replace("-", "_").split("_"):
        if token.startswith("G") and token[1:].isdigit():
            return token[1:]
    for token in value.split():
        cleaned = token.strip(".,:;()[]{}")
        if cleaned.startswith("G") and cleaned[1:].isdigit():
            return cleaned[1:]
    return None


def guidance_pending_work(
    *,
    active_objective: str,
    pending_clarification: bool,
    pending_approval: bool,
) -> list[str]:
    if pending_clarification:
        return [f"Answer clarification for: {active_objective}"]
    if pending_approval:
        return [f"Approve or cancel implementation summary for: {active_objective}"]
    if active_objective != "No active development objective":
        return [f"Continue next governed development task after: {active_objective}"]
    return ["Define the next governed development objective"]


def guidance_next_action(
    *,
    pending_clarification: bool,
    pending_approval: bool,
    implementation_history_count: int,
) -> str:
    if pending_clarification:
        return "Answer the pending clarification, then type /send."
    if pending_approval:
        return "Review the pending implementation summary, then type /approve or /cancel."
    if implementation_history_count > 0:
        return "Choose the next governed development objective."
    return "Compose the first governed development request."


def project_knowledge_index_model(
    *,
    prior_state: dict[str, Any] | None,
    pending_summary: dict[str, Any] | None,
    guidance: dict[str, Any],
    implementation_history: list[dict[str, Any]],
) -> dict[str, Any]:
    prior_index = (
        prior_state.get("project_knowledge_index")
        if isinstance(prior_state, dict) and isinstance(prior_state.get("project_knowledge_index"), dict)
        else {}
    )
    known_targets = unique_strings(prior_index.get("known_goal_targets"))
    certified_artifacts = copy_string_map(prior_index.get("certified_artifacts_by_target"))
    related_milestones = copy_string_map(prior_index.get("related_milestones_by_target"))
    implementation_matches = copy_string_map(prior_index.get("implementation_history_by_target"))
    target = None
    if isinstance(pending_summary, dict) and isinstance(pending_summary.get("goal_mapping"), dict):
        mapping = pending_summary["goal_mapping"]
        target = str(mapping.get("goal_target") or "").strip() or None
        if target:
            known_targets = unique_strings([*known_targets, target])
            certified_artifacts[target] = unique_strings(
                [
                    *certified_artifacts.get(target, []),
                    *certified_artifacts_for_goal_target(target),
                ]
            )
            related_milestones[target] = unique_strings(
                [
                    *related_milestones.get(target, []),
                    str(guidance.get("active_milestone") or "AIGOL_GENERIC_DEVELOPMENT_TASK_V1"),
                ]
            )
            implementation_matches[target] = unique_strings(
                [
                    *implementation_matches.get(target, []),
                    str(mapping.get("governed_request") or mapping.get("source_goal") or ""),
                ]
            )
    return {
        "knowledge_reuse_version": PLATFORM_CORE_PROJECT_KNOWLEDGE_REUSE_VERSION,
        "platform_core_project_services_version": PLATFORM_CORE_PROJECT_SERVICES_VERSION,
        "knowledge_source": "deterministic_workspace_state",
        "knowledge_reuse_authority": "PLATFORM_CORE",
        "known_goal_targets": known_targets,
        "certified_artifacts_by_target": certified_artifacts,
        "related_milestones_by_target": related_milestones,
        "implementation_history_by_target": implementation_matches,
        "implementation_history_count": len(implementation_history),
        "latest_pending_goal_target": target,
        "conversation_history_is_authority": False,
        "requires_human_approval_before_execution": True,
        "acli_next_executes_recommendation": False,
    }


def project_knowledge_context_from_workspace(
    *,
    message: str,
    workspace_state: dict[str, Any] | None,
    goal_target: str,
    governed_request: str,
) -> dict[str, Any]:
    knowledge_index = (
        workspace_state.get("project_knowledge_index")
        if isinstance(workspace_state, dict) and isinstance(workspace_state.get("project_knowledge_index"), dict)
        else {}
    )
    known_targets = set(unique_strings(knowledge_index.get("known_goal_targets")))
    known = goal_target in known_targets
    lowered = message.lower()
    already_requested = any(term in lowered for term in ("already", "done", "implemented", "satisfied"))
    modify_requested = any(term in lowered for term in ("improve", "change", "modify", "refine", "update"))
    continue_requested = any(term in lowered for term in ("continue", "extend", "add to", "build on"))
    if known and already_requested:
        classification = "ALREADY_SATISFIED"
        new_work_required = False
        reuse_recommended = True
        reason = "The deterministic workspace already records this goal target."
    elif known and modify_requested:
        classification = "MODIFIES_EXISTING_CAPABILITY"
        new_work_required = True
        reuse_recommended = True
        reason = "The goal modifies a capability already present in the deterministic workspace."
    elif known and continue_requested:
        classification = "EXTENDS_EXISTING_MILESTONE"
        new_work_required = True
        reuse_recommended = True
        reason = "The goal extends an existing workspace milestone instead of creating unrelated work."
    elif goal_target != "general_project_goal" and certified_artifacts_for_goal_target(goal_target):
        classification = "RELATES_TO_CERTIFIED_CAPABILITY"
        new_work_required = True
        reuse_recommended = True
        reason = "Certified artifacts already describe the related capability family."
    else:
        classification = "NEW_GOVERNED_WORK"
        new_work_required = True
        reuse_recommended = False
        reason = "No deterministic workspace match was found for this goal target."
    artifacts_by_target = (
        knowledge_index.get("certified_artifacts_by_target")
        if isinstance(knowledge_index.get("certified_artifacts_by_target"), dict)
        else {}
    )
    artifacts = unique_strings(
        [
            *artifacts_by_target.get(goal_target, []),
            *certified_artifacts_for_goal_target(goal_target),
        ]
    )
    milestones = unique_strings(
        knowledge_index.get("related_milestones_by_target", {}).get(goal_target, [])
        if isinstance(knowledge_index.get("related_milestones_by_target"), dict)
        else []
    )
    history_matches = unique_strings(
        knowledge_index.get("implementation_history_by_target", {}).get(goal_target, [])
        if isinstance(knowledge_index.get("implementation_history_by_target"), dict)
        else []
    )
    return {
        "knowledge_reuse_version": PLATFORM_CORE_PROJECT_KNOWLEDGE_REUSE_VERSION,
        "platform_core_project_services_version": PLATFORM_CORE_PROJECT_SERVICES_VERSION,
        "workspace_inspected": True,
        "mapping_source": "deterministic_workspace_state",
        "contextual_task_mapping_authority": "PLATFORM_CORE",
        "classification": classification,
        "goal_target": goal_target,
        "governed_request": governed_request,
        "related_milestones": milestones,
        "relevant_certified_artifacts": artifacts,
        "implementation_history_matches": history_matches,
        "reuse_recommended": reuse_recommended,
        "reuse_reason": reason,
        "new_work_required": new_work_required,
        "duplicate_work_avoided": classification == "ALREADY_SATISFIED",
        "requires_human_approval": True,
        "acli_next_executes_recommendation": False,
    }


def certified_artifacts_for_goal_target(goal_target: str) -> list[str]:
    artifacts = {
        "github_actions": [
            "docs/governance/G14_07_GOAL_ORIENTED_DEVELOPMENT_EXPERIENCE_V1.md",
        ],
        "deployment": [
            "docs/governance/G11_00_OPERATIONAL_EXPANSION_PRIORITIZATION_REVIEW_V1.md",
        ],
        "mobile_interface": [
            "docs/governance/G14_01_UNIFIED_HUMAN_INTERFACE_ARCHITECTURE_CERTIFICATION_V1.md",
        ],
        "active_objective": [
            "docs/governance/G14_05_PERSISTENT_DEVELOPMENT_WORKSPACE_AND_PROJECT_CONTINUITY_V1.md",
        ],
    }
    return artifacts.get(goal_target, [])


def goal_oriented_request_detected(message: str) -> bool:
    lowered = message.lower().strip()
    return lowered.startswith(("i want ", "i want aigol", "let's ", "lets ", "continue "))


def resolve_development_intent(
    *,
    message: str,
    workspace_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve deterministic development intent once for summary and runtime binding."""

    raw_message = require_string(message, "message")
    goal_detected = goal_oriented_request_detected(raw_message)
    guided_detected = guided_development_request_detected(raw_message)
    goal_mapping = (
        goal_mapping_from_workspace(message=raw_message, workspace_state=workspace_state)
        if goal_detected
        else None
    )
    governed_request = (
        str(goal_mapping.get("governed_request") or raw_message)
        if isinstance(goal_mapping, dict)
        else raw_message
    )
    clarification_required = False
    clarification_reason = None
    if guided_detected and guided_development_clarification_required(raw_message):
        clarification_required = True
        clarification_reason = "guided development request lacks deterministic implementation specificity"
    if not goal_detected and not guided_detected:
        clarification_reason = "request is not a deterministic development request"

    canonical_runtime_prompt = canonical_development_runtime_prompt(governed_request)
    native_runtime_admissible = is_native_development_prompt(canonical_runtime_prompt)
    summary_admissible = (
        (goal_detected or guided_detected)
        and not clarification_required
        and native_runtime_admissible
    )
    runtime_binding_admissible = summary_admissible
    resolution = {
        "artifact_type": "PLATFORM_CORE_DEVELOPMENT_INTENT_RESOLUTION_ARTIFACT_V1",
        "runtime_version": PLATFORM_CORE_DEVELOPMENT_INTENT_RESOLUTION_VERSION,
        "platform_core_project_services_version": PLATFORM_CORE_PROJECT_SERVICES_VERSION,
        "development_intent_resolution_authority": "PLATFORM_CORE",
        "raw_prompt": raw_message,
        "goal_oriented_request_detected": goal_detected,
        "guided_development_request_detected": guided_detected,
        "clarification_required": clarification_required,
        "clarification_reason": clarification_reason,
        "goal_mapping": deepcopy(goal_mapping),
        "governed_request": governed_request,
        "refined_message": canonical_runtime_prompt,
        "canonical_runtime_prompt": canonical_runtime_prompt,
        "native_development_prompt_detected": native_runtime_admissible,
        "summary_admissible": summary_admissible,
        "runtime_binding_admissible": runtime_binding_admissible,
        "same_decision_for_send_and_approve": True,
        "acli_next_executes_resolution": False,
        "requires_human_approval": summary_admissible,
        "replay_visible": True,
    }
    resolution["artifact_hash"] = replay_hash(resolution)
    return resolution


def canonical_development_runtime_prompt(message: str) -> str:
    """Return a deterministic runtime prompt for governed development continuation."""

    prompt = require_string(message, "message")
    if is_native_development_prompt(prompt):
        return prompt
    lowered = prompt.lower()
    if guided_development_request_detected(prompt) and not guided_development_clarification_required(prompt):
        if "governed" in lowered or "governance" in lowered:
            return f"{prompt} Implement as a native development governance workflow."
    return prompt


def goal_mapping_from_workspace(
    *,
    message: str,
    workspace_state: dict[str, Any] | None,
) -> dict[str, Any]:
    lowered = message.lower()
    active_objective = (
        workspace_state.get("active_development_objective")
        if isinstance(workspace_state, dict)
        else None
    )
    if "github actions" in lowered:
        governed_request = "Add GitHub Actions support."
        goal_type = "EXTENDS_PROJECT"
        target = "github_actions"
    elif "deployment" in lowered:
        governed_request = "Add governed deployment workflow support."
        goal_type = "EXTENDS_PROJECT"
        target = "deployment"
    elif "mobile" in lowered:
        governed_request = "Continue the governed mobile interface."
        goal_type = "CONTINUES_PROJECT"
        target = "mobile_interface"
    elif lowered.startswith(("continue ", "let's continue", "lets continue")):
        governed_request = str(active_objective or "Continue the active governed development objective.")
        goal_type = "CONTINUES_PROJECT"
        target = "active_objective"
    else:
        governed_request = message
        goal_type = "MODIFIES_PROJECT" if active_objective else "EXTENDS_PROJECT"
        target = "general_project_goal"
    mapping = {
        "goal_mapping_status": "GOAL_MAPPED_TO_GOVERNED_REQUEST",
        "platform_core_project_services_version": PLATFORM_CORE_PROJECT_SERVICES_VERSION,
        "goal_mapping_authority": "PLATFORM_CORE",
        "goal_type": goal_type,
        "goal_target": target,
        "source_goal": message,
        "active_workspace_objective": active_objective,
        "governed_request": governed_request,
        "mapping_source": "deterministic_workspace_state",
        "requires_human_approval": True,
        "acli_next_executes_mapping": False,
    }
    mapping["contextual_task_mapping"] = project_knowledge_context_from_workspace(
        message=message,
        workspace_state=workspace_state,
        goal_target=target,
        governed_request=governed_request,
    )
    return mapping


def guided_development_request_detected(message: str) -> bool:
    lowered = message.lower().strip()
    return lowered.startswith(
        (
            "add ",
            "build ",
            "create ",
            "enhance ",
            "extend ",
            "fix ",
            "implement ",
            "improve ",
            "introduce ",
            "optimize ",
            "refactor ",
            "repair ",
            "update ",
        )
    )


def guided_development_clarification_required(message: str) -> bool:
    lowered = message.lower()
    if not guided_development_request_detected(message):
        return False
    specificity_terms = (
        "support",
        "workflow",
        "runtime",
        "test",
        "validation",
        "validator",
        "parser",
        "feature",
        "helper",
        "utility",
        "github actions",
        "governed",
        "governance",
        "replay",
        "routing",
        "intent classification",
        "message composer",
        "provider handling",
        "provider availability",
        "provider resilience",
        "runtime",
        "availability handling",
        "workspace",
    )
    return not any(term in lowered for term in specificity_terms)


def guided_development_clarification(message: str) -> dict[str, Any]:
    return {
        "original_message": message,
        "clarification_required": True,
        "clarification_authority": "PLATFORM_CORE",
        "platform_core_project_services_version": PLATFORM_CORE_PROJECT_SERVICES_VERSION,
        "clarification_questions": [
            "What specific capability should AiGOL implement?",
            "What constraints or boundaries should the implementation preserve?",
        ],
    }


def unique_strings(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return sorted({str(value) for value in values if str(value).strip()})


def copy_string_map(value: Any) -> dict[str, list[str]]:
    if not isinstance(value, dict):
        return {}
    result: dict[str, list[str]] = {}
    for key, values in value.items():
        result[str(key)] = unique_strings(values)
    return result


def require_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} must be a non-empty string")
    return value
