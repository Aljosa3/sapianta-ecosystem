"""Platform Core project workspace, guidance, and knowledge reuse services."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.native_development_task_intake_runtime import is_native_development_prompt
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_certification_registry import (
    list_platform_capability_certifications,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


PLATFORM_CORE_PROJECT_SERVICES_VERSION = "G14_08A_PLATFORM_CORE_PROJECT_SERVICES_EXTRACTION_V1"
PLATFORM_CORE_PERSISTENT_WORKSPACE_VERSION = "G14_05_PERSISTENT_DEVELOPMENT_WORKSPACE_AND_PROJECT_CONTINUITY_V1"
PLATFORM_CORE_PROJECT_GUIDANCE_VERSION = "G14_06_PROJECT_GUIDANCE_AND_DEVELOPMENT_ASSISTANT_V1"
PLATFORM_CORE_PROJECT_KNOWLEDGE_REUSE_VERSION = (
    "G14_08_PROJECT_KNOWLEDGE_REUSE_AND_CONTEXTUAL_TASK_MAPPING_V1"
)
PLATFORM_CORE_DEVELOPMENT_INTENT_RESOLUTION_VERSION = (
    "G14_19_CANONICAL_DEVELOPMENT_INTENT_RESOLUTION_UNIFICATION_V1"
)
PLATFORM_CORE_UHI_PROJECT_SERVICES_INTEGRATION_VERSION = (
    "G14_27_UNIFIED_HUMAN_INTERFACE_RUNTIME_PROJECT_SERVICES_INTEGRATION_V1"
)
PLATFORM_CORE_HUMAN_CONVERSATION_EXPERIENCE_VERSION = (
    "G14_38_PLATFORM_CORE_HUMAN_CONVERSATION_EXPERIENCE_V1"
)
PLATFORM_CORE_HUMAN_INTENT_CAPABILITY_RESOLUTION_VERSION = (
    "G14_47_HUMAN_INTENT_TO_CAPABILITY_RESOLUTION_V1"
)
PLATFORM_CORE_UHI_CLARIFICATION_CONTINUITY_VERSION = (
    "G15_HIR_02_REPLAY_BACKED_CLARIFICATION_CONTINUITY_V1"
)
PLATFORM_CORE_DETERMINISTIC_CLARIFICATION_PLANNER_VERSION = (
    "G15_HIR_08_DETERMINISTIC_CLARIFICATION_PLANNER_V1"
)


CAPABILITY_CATALOG: tuple[dict[str, Any], ...] = (
    {
        "capability_id": "governance_documentation",
        "display_name": "governance documentation",
        "keywords": (
            "governance documentation",
            "governance docs",
            "governance document",
            "constitutional documentation",
            "governance report",
            "governance artifact",
        ),
        "default_goal_type": "EXTENDS_PROJECT",
        "canonical_request": "Improve governance documentation.",
    },
    {
        "capability_id": "governance_validation",
        "display_name": "governance validator",
        "keywords": (
            "governance validator",
            "governance validation",
            "validator",
            "validation",
            "validate governance",
        ),
        "default_goal_type": "EXTENDS_PROJECT",
        "canonical_request": "Improve governance validation.",
    },
    {
        "capability_id": "replay",
        "display_name": "replay evidence",
        "keywords": (
            "replay",
            "replay evidence",
            "replay certification",
            "replay generation",
            "replay-safe",
            "replay safe",
        ),
        "default_goal_type": "EXTENDS_PROJECT",
        "canonical_request": "Improve replay evidence handling.",
    },
    {
        "capability_id": "certification",
        "display_name": "certification workflow",
        "keywords": (
            "certification",
            "certify",
            "final certification",
            "certification simpler",
            "certification easier",
        ),
        "default_goal_type": "EXTENDS_PROJECT",
        "canonical_request": "Simplify certification workflow.",
    },
    {
        "capability_id": "development_experience",
        "display_name": "development experience",
        "keywords": (
            "development easier",
            "make development easier",
            "developer experience",
            "development experience",
            "ordinary users",
            "user experience",
        ),
        "default_goal_type": "EXTENDS_PROJECT",
        "canonical_request": "Improve governed development experience.",
    },
    {
        "capability_id": "human_intent_resolution",
        "display_name": "human intent resolution",
        "keywords": (
            "human intent",
            "intent resolution",
            "natural language",
            "capability resolution",
            "derive capability",
        ),
        "default_goal_type": "EXTENDS_PROJECT",
        "canonical_request": "Improve human intent to capability resolution.",
    },
    {
        "capability_id": "provider_attachment",
        "display_name": "provider attachment",
        "keywords": (
            "provider attachment",
            "provider platform",
            "external provider",
            "provider boundary",
            "provider",
        ),
        "default_goal_type": "EXTENDS_PROJECT",
        "canonical_request": "Improve provider attachment boundary handling.",
    },
    {
        "capability_id": "human_interface",
        "display_name": "human interface",
        "keywords": (
            "human interface",
            "interface",
            "aicli",
            "aigol next",
            "web interface",
            "mobile interface",
            "voice interface",
        ),
        "default_goal_type": "EXTENDS_PROJECT",
        "canonical_request": "Improve the human interface experience.",
    },
)


def prepare_unified_human_interface_project_context(
    *,
    interface_name: str,
    session_id: str,
    message: str,
    runtime_root: str | Path,
    workspace: str | Path,
    created_at: str,
) -> dict[str, Any]:
    """Prepare the canonical Platform Core project-services context for any UHI."""

    session_root = Path(runtime_root) / require_string(session_id, "session_id")
    prior_state = latest_platform_core_workspace_state(session_root)
    guidance = (
        project_guidance_from_workspace_state(prior_state)
        if isinstance(prior_state, dict)
        else project_guidance_model(
            active_objective=None,
            pending_clarification=False,
            pending_approval=False,
            implementation_history_count=0,
            runtime_bound_count=0,
        )
    )
    clarification_continuity = None
    active_clarification_state = replay_backed_uhi_clarification_state(prior_state)
    if active_clarification_state is not None:
        development_intent, clarification_continuity = resolve_uhi_clarification_continuity(
            message=message,
            workspace_state=prior_state,
            active_clarification_state=active_clarification_state,
            session_root=session_root,
            created_at=created_at,
        )
    else:
        development_intent = resolve_development_intent(message=message, workspace_state=prior_state)
    goal_mapping = (
        development_intent.get("goal_mapping")
        if isinstance(development_intent.get("goal_mapping"), dict)
        else goal_mapping_from_workspace(message=message, workspace_state=prior_state)
    )
    knowledge_reuse = (
        goal_mapping.get("contextual_task_mapping")
        if isinstance(goal_mapping, dict) and isinstance(goal_mapping.get("contextual_task_mapping"), dict)
        else project_knowledge_context_from_workspace(
            message=message,
            workspace_state=prior_state,
            goal_target="general_project_goal",
            governed_request=message,
        )
    )
    conversation_experience = human_conversation_experience_from_resolution(
        message=message,
        guidance=guidance,
        knowledge_reuse=knowledge_reuse,
        development_intent=development_intent,
        workspace_state=prior_state,
    )
    artifact = {
        "artifact_type": "UNIFIED_HUMAN_INTERFACE_PROJECT_CONTEXT_ARTIFACT_V1",
        "runtime_version": PLATFORM_CORE_UHI_PROJECT_SERVICES_INTEGRATION_VERSION,
        "platform_core_project_services_version": PLATFORM_CORE_PROJECT_SERVICES_VERSION,
        "platform_core_human_conversation_experience_version": (
            PLATFORM_CORE_HUMAN_CONVERSATION_EXPERIENCE_VERSION
        ),
        "interface_name": require_string(interface_name, "interface_name"),
        "session_id": require_string(session_id, "session_id"),
        "workspace": str(Path(workspace)),
        "created_at": require_string(created_at, "created_at"),
        "message_hash": replay_hash(message),
        "project_workspace_restored": prior_state is not None,
        "project_workspace_replay_reference": prior_state.get("replay_reference") if isinstance(prior_state, dict) else None,
        "project_guidance": guidance,
        "knowledge_reuse": knowledge_reuse,
        "clarification_continuity": clarification_continuity,
        "development_intent_resolution": development_intent,
        "human_conversation_experience": conversation_experience,
        "project_workspace_authority": "PLATFORM_CORE",
        "project_guidance_authority": "PLATFORM_CORE",
        "project_knowledge_reuse_authority": "PLATFORM_CORE",
        "development_intent_resolution_authority": "PLATFORM_CORE",
        "human_conversation_experience_authority": "PLATFORM_CORE",
        "interface_authority": False,
        "interface_executes_project_services": False,
        "replay_visible": True,
        "replay_reference": str(session_root / "uhi_project_services"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    write_json_immutable(
        session_root
        / "uhi_project_services"
        / f"{next_uhi_project_context_index(session_root):03d}_uhi_project_context_recorded.json",
        artifact,
    )
    return artifact


def record_unified_human_interface_workspace_state(
    *,
    interface_name: str,
    session_id: str,
    runtime_root: str | Path,
    workspace: str | Path,
    created_at: str,
    completion: dict[str, Any],
    turn_results: list[dict[str, Any]],
    pending_clarification: dict[str, Any] | None,
    pending_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    """Record the canonical Platform Core project workspace state for any UHI."""

    session_root = Path(runtime_root) / require_string(session_id, "session_id")
    prior_state = latest_platform_core_workspace_state(session_root)
    artifact = build_persistent_workspace_state_artifact(
        conversation_id=session_id,
        command_name=interface_name,
        prior_state=prior_state,
        completion=completion,
        turn_results=turn_results,
        pending_clarification=pending_clarification,
        pending_summary=pending_summary,
        session_root=session_root,
        created_at=created_at,
        workspace=workspace,
    )
    write_json_immutable(
        session_root
        / "workspace_state"
        / f"{next_workspace_state_index(session_root):03d}_platform_core_workspace_state_recorded.json",
        artifact,
    )
    return artifact


def latest_platform_core_workspace_state(session_root: Path) -> dict[str, Any] | None:
    state_root = session_root / "workspace_state"
    if not state_root.exists():
        return None
    candidates = sorted(state_root.glob("*_workspace_state_recorded.json"))
    for path in reversed(candidates):
        try:
            artifact = load_json(path)
        except FailClosedRuntimeError:
            continue
        if artifact.get("artifact_type") == "ACLI_NEXT_PERSISTENT_WORKSPACE_STATE_ARTIFACT_V1":
            return artifact
    return None


def replay_backed_uhi_clarification_state(workspace_state: dict[str, Any] | None) -> dict[str, Any] | None:
    """Recover the active UHI clarification state from Platform Core workspace replay."""

    if not isinstance(workspace_state, dict):
        return None
    pending = workspace_state.get("pending_clarification_request")
    if not isinstance(pending, dict):
        return None
    return {
        "artifact_type": "PLATFORM_CORE_UHI_ACTIVE_CLARIFICATION_STATE_V1",
        "runtime_version": PLATFORM_CORE_UHI_CLARIFICATION_CONTINUITY_VERSION,
        "state_source": "PLATFORM_CORE_WORKSPACE_REPLAY",
        "workspace_state_reference": workspace_state.get("replay_reference"),
        "workspace_state_hash": workspace_state.get("artifact_hash"),
        "session_id": workspace_state.get("session_id"),
        "original_message": pending.get("original_message"),
        "clarification_questions": unique_strings(pending.get("clarification_questions")),
        "clarification_question_bindings": deterministic_clarification_question_bindings(
            pending.get("clarification_questions")
        ),
        "pending_clarification_request": deepcopy(pending),
        "replay_backed": True,
        "platform_core_authority": True,
        "human_interface_authority": False,
    }


def resolve_uhi_clarification_continuity(
    *,
    message: str,
    workspace_state: dict[str, Any] | None,
    active_clarification_state: dict[str, Any],
    session_root: Path,
    created_at: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Bind a UHI clarification reply to the replay-backed active clarification."""

    reply = require_string(message, "message")
    reply_resolution = resolve_development_intent(
        message=reply,
        workspace_state=workspace_state,
    )
    resolution_source = "CLARIFICATION_REPLY_STANDALONE"
    if (
        reply_resolution.get("summary_admissible") is not True
        and clarification_reply_substantively_answers_active_questions(
            reply=reply,
            active_clarification_state=active_clarification_state,
        )
    ):
        resolution_source = "ORIGINAL_REQUEST_WITH_BOUND_CLARIFICATION_REPLY"
        reply_resolution = resolve_development_intent(
            message=clarification_resolved_development_request(
                reply=reply,
                active_clarification_state=active_clarification_state,
            ),
            workspace_state=workspace_state,
        )
    resolved = reply_resolution.get("summary_admissible") is True
    status = "CLARIFICATION_RESOLVED" if resolved else "CLARIFICATION_STILL_REQUIRED"
    question_bindings = deterministic_clarification_question_bindings(
        active_clarification_state.get("clarification_questions")
    )
    continuity_artifact = {
        "artifact_type": "PLATFORM_CORE_UHI_CLARIFICATION_CONTINUITY_ARTIFACT_V1",
        "runtime_version": PLATFORM_CORE_UHI_CLARIFICATION_CONTINUITY_VERSION,
        "platform_core_project_services_version": PLATFORM_CORE_PROJECT_SERVICES_VERSION,
        "created_at": require_string(created_at, "created_at"),
        "session_id": active_clarification_state.get("session_id"),
        "reply_hash": replay_hash(reply),
        "reply_bound_to_active_clarification": True,
        "reply_resolution_source": resolution_source,
        "clarification_question_bindings": question_bindings,
        "answered_clarification_question_ids": [
            binding["question_id"] for binding in question_bindings
        ] if resolved else [],
        "clarification_continuity_status": status,
        "clarification_resolved": resolved,
        "new_governed_request_created": False,
        "active_clarification_state": deepcopy(active_clarification_state),
        "active_clarification_workspace_state_reference": active_clarification_state.get(
            "workspace_state_reference"
        ),
        "active_clarification_workspace_state_hash": active_clarification_state.get(
            "workspace_state_hash"
        ),
        "development_intent_resolution_hash": reply_resolution.get("artifact_hash"),
        "canonical_semantic_artifact_hash": None,
        "canonical_semantic_artifact_status": (
            "NOT_CREATED_BY_UHI_PROJECT_SERVICES_CONTINUITY"
        ),
        "semantic_lineage_preserved": True,
        "replay_lineage_preserved": True,
        "governance_authority_preserved": True,
        "human_interface_authority": False,
        "provider_platform_preserved": True,
        "worker_platform_preserved": True,
        "replay_reference": str(session_root / "uhi_clarification_continuity"),
    }
    continuity_artifact["artifact_hash"] = replay_hash(continuity_artifact)
    write_json_immutable(
        session_root
        / "uhi_clarification_continuity"
        / f"{next_uhi_clarification_continuity_index(session_root):03d}_uhi_clarification_continuity_recorded.json",
        continuity_artifact,
    )
    enriched_resolution = deepcopy(reply_resolution)
    if not resolved:
        enriched_resolution["clarification_required"] = True
        enriched_resolution["clarification_reason"] = (
            "clarification reply did not resolve active clarification deterministically"
        )
        enriched_resolution["summary_admissible"] = False
        enriched_resolution["runtime_binding_admissible"] = False
        enriched_resolution["requires_human_approval"] = False
    enriched_resolution.update(
        {
            "clarification_reply_bound": True,
            "clarification_reply_resolution_source": resolution_source,
            "clarification_question_bindings": question_bindings,
            "answered_clarification_question_ids": [
                binding["question_id"] for binding in question_bindings
            ] if resolved else [],
            "clarification_continuity_status": status,
            "clarification_resolved": resolved,
            "clarification_continuity_replay_reference": continuity_artifact["replay_reference"],
            "clarification_continuity_artifact_hash": continuity_artifact["artifact_hash"],
            "active_clarification_workspace_state_reference": active_clarification_state.get(
                "workspace_state_reference"
            ),
            "new_governed_request_created": False,
            "human_interface_resolves_clarification": False,
            "platform_core_resolves_clarification": True,
        }
    )
    enriched_resolution["artifact_hash"] = replay_hash(enriched_resolution)
    return enriched_resolution, continuity_artifact


def deterministic_clarification_question_bindings(questions: Any) -> list[dict[str, Any]]:
    """Create stable identifiers for replay-backed clarification questions."""

    return [
        {
            "question_id": f"CLARIFICATION_QUESTION_{replay_hash(question)[:16]}",
            "question_text": question,
            "binding_authority": "PLATFORM_CORE",
        }
        for question in unique_strings(questions)
    ]


def clarification_reply_substantively_answers_active_questions(
    *,
    reply: str,
    active_clarification_state: dict[str, Any],
) -> bool:
    """Return whether a free-form reply is enough to consume active clarification slots."""

    text = " ".join(require_string(reply, "reply").split())
    if len(text) < 20:
        return False
    lowered = text.lower()
    action_terms = (
        "add",
        "build",
        "change",
        "create",
        "fix",
        "implement",
        "improve",
        "record",
        "remove",
        "reuse",
        "support",
        "update",
    )
    scope_terms = (
        "aicli",
        "governance",
        "human interface",
        "interface",
        "platform core",
        "replay",
        "runtime",
        "workflow",
    )
    if not any(term in lowered for term in action_terms):
        return False
    if not any(term in lowered for term in scope_terms):
        return False
    return bool(deterministic_clarification_question_bindings(
        active_clarification_state.get("clarification_questions")
    ))


def clarification_resolved_development_request(
    *,
    reply: str,
    active_clarification_state: dict[str, Any],
) -> str:
    """Build the Platform Core-owned request resolved from a clarification answer."""

    original = str(active_clarification_state.get("original_message") or "").strip()
    questions = [
        binding["question_text"]
        for binding in deterministic_clarification_question_bindings(
            active_clarification_state.get("clarification_questions")
        )
    ]
    question_text = "\n".join(f"- {question}" for question in questions)
    return "\n".join(
        [
            "Implement the clarification-resolved governed development request.",
            f"Original request: {original}",
            "Clarification questions:",
            question_text,
            f"Clarification answer: {require_string(reply, 'reply')}",
            "Implement as a governed development workflow.",
        ]
    )


def next_workspace_state_index(session_root: Path) -> int:
    return next_index(session_root / "workspace_state", "*_workspace_state_recorded.json")


def next_uhi_project_context_index(session_root: Path) -> int:
    return next_index(session_root / "uhi_project_services", "*_uhi_project_context_recorded.json")


def next_uhi_clarification_continuity_index(session_root: Path) -> int:
    return next_index(
        session_root / "uhi_clarification_continuity",
        "*_uhi_clarification_continuity_recorded.json",
    )


def next_index(root: Path, pattern: str) -> int:
    existing: list[int] = []
    if root.exists():
        for path in root.glob(pattern):
            prefix = path.name.split("_", 1)[0]
            if prefix.isdigit():
                existing.append(int(prefix))
    return max(existing, default=0) + 1


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
    candidate_capability_discovery: dict[str, Any] | None = None,
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
    discovery = candidate_capability_discovery if isinstance(candidate_capability_discovery, dict) else {}
    discovery_target = str(discovery.get("selected_goal_target") or "")
    capability_decision = (
        str(discovery.get("capability_resolution_decision") or "")
        if discovery_target == goal_target
        else ""
    )
    candidate_capabilities = (
        discovery.get("candidate_capabilities")
        if isinstance(discovery.get("candidate_capabilities"), list)
        else []
    )
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
    elif capability_decision == "EXTENDS_EXISTING_CAPABILITY":
        classification = "RELATES_TO_CERTIFIED_CAPABILITY"
        new_work_required = True
        reuse_recommended = True
        reason = "Candidate capability discovery found a related certified capability family."
    elif capability_decision == "EXISTING_CAPABILITY":
        classification = "ALREADY_SATISFIED"
        new_work_required = False
        reuse_recommended = True
        reason = "Candidate capability discovery found an existing workspace capability."
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
    evidence_selection = _knowledge_reuse_evidence_selection(
        artifacts=artifacts,
        history_matches=history_matches,
        milestones=milestones,
    )
    return {
        "knowledge_reuse_version": PLATFORM_CORE_PROJECT_KNOWLEDGE_REUSE_VERSION,
        "platform_core_project_services_version": PLATFORM_CORE_PROJECT_SERVICES_VERSION,
        "workspace_inspected": True,
        "certified_artifacts_inspected": True,
        "knowledge_reuse_evidence_selection": evidence_selection,
        "evidence_selection_authority": "PLATFORM_CORE",
        "human_selects_evidence_sources": False,
        "mapping_source": "deterministic_workspace_state",
        "contextual_task_mapping_authority": "PLATFORM_CORE",
        "classification": classification,
        "goal_target": goal_target,
        "governed_request": governed_request,
        "candidate_capability_discovery": deepcopy(discovery),
        "candidate_capabilities_received": deepcopy(candidate_capabilities),
        "capability_resolution_decision": capability_decision or "NEW_CAPABILITY",
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
        "governance_documentation": [
            "docs/governance/CONSTITUTIONAL_ARCHITECTURE_SPEC_V1.md",
            "docs/governance/GOVERNANCE_CONFORMANCE_SYSTEM_V1.md",
        ],
        "governance_validation": [
            "runtime/governance/governance_conformance_engine.py",
            "runtime/governance/conformance_rules.py",
        ],
        "replay": [
            "docs/governance/GOVERNANCE_LINEAGE_MODEL.md",
            "governance/UNIFIED_REPLAY_RECONSTRUCTION_MODEL_V1.md",
        ],
        "certification": [
            "docs/governance/G14_31_FINAL_GENERATION_14_OPERATIONAL_ACCEPTANCE_V1.md",
        ],
        "development_experience": [
            "docs/governance/G14_38_PLATFORM_CORE_HUMAN_CONVERSATION_EXPERIENCE_V1.md",
        ],
        "human_intent_resolution": [
            "docs/governance/G14_19_DEVELOPMENT_INTENT_RESOLUTION_UNIFICATION_V1.md",
        ],
        "provider_attachment": [
            "aigol/provider/certified_provider_attachment.py",
        ],
        "human_interface": [
            "docs/governance/G14_30_CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_SERVICE_V1.md",
        ],
    }
    return artifacts.get(goal_target, [])


def _knowledge_reuse_evidence_selection(
    *,
    artifacts: list[str],
    history_matches: list[str],
    milestones: list[str],
) -> dict[str, Any]:
    sources: list[str] = []
    if history_matches or milestones:
        sources.append("PROJECT_WORKSPACE")
    if artifacts:
        sources.append("CERTIFIED_ARTIFACTS")
    if not sources:
        sources.append("DETERMINISTIC_CAPABILITY_DISCOVERY")
    return {
        "selection_authority": "PLATFORM_CORE",
        "selected_sources": sources,
        "workspace_selected": "PROJECT_WORKSPACE" in sources,
        "certified_artifacts_selected": "CERTIFIED_ARTIFACTS" in sources,
        "additional_deterministic_evidence_selected": "DETERMINISTIC_CAPABILITY_DISCOVERY" in sources,
        "human_selects_sources": False,
    }


def goal_oriented_request_detected(message: str) -> bool:
    lowered = message.lower().strip()
    return lowered.startswith(("i want ", "i want aigol", "let's ", "lets ")) or (
        continuation_development_request_detected(message)
        or collaborative_development_request_detected(message)
    )


def discover_candidate_capabilities(
    *,
    message: str,
    workspace_state: dict[str, Any] | None,
) -> dict[str, Any]:
    """Infer candidate Platform Core capabilities from ordinary human language."""

    raw_message = require_string(message, "message")
    lowered = " ".join(raw_message.lower().split())
    if _invalid_continuation_reference(lowered):
        return _empty_candidate_capability_discovery(raw_message)
    knowledge_index = (
        workspace_state.get("project_knowledge_index")
        if isinstance(workspace_state, dict) and isinstance(workspace_state.get("project_knowledge_index"), dict)
        else {}
    )
    active_objective = (
        workspace_state.get("active_development_objective")
        if isinstance(workspace_state, dict)
        else None
    )
    candidates: list[dict[str, Any]] = []
    for capability in CAPABILITY_CATALOG:
        evidence = [term for term in capability["keywords"] if term in lowered]
        if not evidence:
            continue
        candidate = _candidate_capability(
            capability=capability,
            evidence=evidence,
            message=raw_message,
            workspace_state=workspace_state,
            knowledge_index=knowledge_index,
        )
        candidates.append(candidate)
    if not candidates and active_objective and _workspace_reference_detected(lowered):
        candidates.append(
            _active_objective_candidate(
                active_objective=active_objective,
                message=raw_message,
                knowledge_index=knowledge_index,
            )
        )
    candidates = sorted(candidates, key=lambda item: (-int(item.get("confidence_score") or 0), item["capability_id"]))
    selected = candidates[0] if candidates else None
    ambiguity_remaining = len(candidates) > 1 and int(candidates[0]["confidence_score"]) == int(candidates[1]["confidence_score"])
    if selected is None:
        decision = "NEW_CAPABILITY"
    elif selected.get("workspace_match") is True and _already_satisfied_request_detected(lowered):
        decision = "EXISTING_CAPABILITY"
    elif selected.get("workspace_match") is True or selected.get("certified_artifacts"):
        decision = "EXTENDS_EXISTING_CAPABILITY"
    else:
        decision = "NEW_CAPABILITY"
    artifact = {
        "artifact_type": "PLATFORM_CORE_CANDIDATE_CAPABILITY_DISCOVERY_ARTIFACT_V1",
        "runtime_version": PLATFORM_CORE_HUMAN_INTENT_CAPABILITY_RESOLUTION_VERSION,
        "platform_core_project_services_version": PLATFORM_CORE_PROJECT_SERVICES_VERSION,
        "capability_discovery_authority": "PLATFORM_CORE",
        "raw_prompt": raw_message,
        "human_objective": extract_human_objective(raw_message),
        "candidate_capabilities": candidates,
        "candidate_capability_count": len(candidates),
        "selected_candidate_capability": deepcopy(selected),
        "selected_goal_target": selected.get("goal_target") if isinstance(selected, dict) else "general_project_goal",
        "capability_resolution_decision": decision,
        "workspace_inspected": True,
        "knowledge_reuse_prepared": True,
        "certified_governance_artifacts_inspected": True,
        "ambiguity_remaining_after_deterministic_analysis": ambiguity_remaining,
        "requires_human_capability_name": False,
        "clarification_allowed_only_for_remaining_ambiguity": True,
        "human_interface_authority": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _empty_candidate_capability_discovery(message: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": "PLATFORM_CORE_CANDIDATE_CAPABILITY_DISCOVERY_ARTIFACT_V1",
        "runtime_version": PLATFORM_CORE_HUMAN_INTENT_CAPABILITY_RESOLUTION_VERSION,
        "platform_core_project_services_version": PLATFORM_CORE_PROJECT_SERVICES_VERSION,
        "capability_discovery_authority": "PLATFORM_CORE",
        "raw_prompt": message,
        "human_objective": extract_human_objective(message),
        "candidate_capabilities": [],
        "candidate_capability_count": 0,
        "selected_candidate_capability": None,
        "selected_goal_target": "general_project_goal",
        "capability_resolution_decision": "NEW_CAPABILITY",
        "workspace_inspected": True,
        "knowledge_reuse_prepared": True,
        "certified_governance_artifacts_inspected": True,
        "ambiguity_remaining_after_deterministic_analysis": False,
        "requires_human_capability_name": False,
        "clarification_allowed_only_for_remaining_ambiguity": True,
        "human_interface_authority": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _invalid_continuation_reference(lowered: str) -> bool:
    starts_like_continuation = lowered.startswith(
        (
            "continue",
            "resume",
            "pick up",
        )
    )
    return starts_like_continuation and not continuation_development_request_detected(lowered)


def _candidate_capability(
    *,
    capability: dict[str, Any],
    evidence: list[str],
    message: str,
    workspace_state: dict[str, Any] | None,
    knowledge_index: dict[str, Any],
) -> dict[str, Any]:
    capability_id = str(capability["capability_id"])
    known_targets = set(unique_strings(knowledge_index.get("known_goal_targets")))
    workspace_match = capability_id in known_targets
    artifacts = certified_artifacts_for_goal_target(capability_id)
    active_objective = (
        workspace_state.get("active_development_objective")
        if isinstance(workspace_state, dict)
        else None
    )
    confidence = 60 + min(len(evidence), 3) * 10
    if workspace_match:
        confidence += 15
    if artifacts:
        confidence += 10
    if active_objective and capability_id in str(active_objective).lower().replace(" ", "_"):
        confidence += 5
    return {
        "capability_id": capability_id,
        "goal_target": capability_id,
        "display_name": capability["display_name"],
        "default_goal_type": capability.get("default_goal_type", "EXTENDS_PROJECT"),
        "matched_terms": unique_strings(evidence),
        "human_objective": extract_human_objective(message),
        "workspace_match": workspace_match,
        "certified_artifacts": artifacts,
        "reuse_decision_basis": "keyword_workspace_certified_artifact_match",
        "confidence_score": confidence,
        "requires_human_capability_name": False,
    }


def _active_objective_candidate(
    *,
    active_objective: Any,
    message: str,
    knowledge_index: dict[str, Any],
) -> dict[str, Any]:
    artifacts_by_target = (
        knowledge_index.get("certified_artifacts_by_target")
        if isinstance(knowledge_index.get("certified_artifacts_by_target"), dict)
        else {}
    )
    return {
        "capability_id": "active_objective",
        "goal_target": "active_objective",
        "display_name": "active project objective",
        "matched_terms": ["this", "current", "previous"],
        "human_objective": extract_human_objective(message),
        "workspace_match": True,
        "active_workspace_objective": str(active_objective),
        "certified_artifacts": unique_strings(artifacts_by_target.get("active_objective", [])),
        "reuse_decision_basis": "workspace_active_objective_reference",
        "confidence_score": 70,
        "requires_human_capability_name": False,
    }


def extract_human_objective(message: str) -> str:
    text = " ".join(require_string(message, "message").strip().split())
    lowered = text.lower()
    prefixes = (
        "i have an idea to ",
        "i have an idea about ",
        "i have an idea ",
        "we should ",
        "we should probably ",
        "i think ",
        "i think we should ",
        "can we ",
        "could we ",
        "let's ",
        "lets ",
        "i want to ",
        "i'd like to ",
        "id like to ",
    )
    for prefix in prefixes:
        if lowered.startswith(prefix):
            return text[len(prefix) :].strip(" .") or text
    return text.strip(" .")


def _already_satisfied_request_detected(lowered: str) -> bool:
    return any(term in lowered for term in ("already implemented", "already exists", "done", "satisfied"))


def _clarification_first_request_detected(message: str) -> bool:
    lowered = " ".join(require_string(message, "message").lower().split())
    if _reuse_request_detected(lowered) or _architecture_question_detected(lowered):
        return True
    if lowered.startswith(
        (
            "i have another idea",
            "i have an idea but",
            "i think something",
            "something should be improved",
            "help me decide",
            "i'm not sure",
            "im not sure",
            "what do you recommend",
            "is there already",
            "we probably implemented",
            "check whether",
            "search previous work",
        )
    ):
        return True
    return False


def _workspace_reference_detected(lowered: str) -> bool:
    return any(
        term in lowered
        for term in (
            "this",
            "current",
            "previous",
            "what we started",
            "where we stopped",
            "where we left off",
            "existing",
        )
    )


def resolve_development_intent(
    *,
    message: str,
    workspace_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve deterministic development intent once for summary and runtime binding."""

    raw_message = require_string(message, "message")
    candidate_capability_discovery = discover_candidate_capabilities(
        message=raw_message,
        workspace_state=workspace_state,
    )
    candidate_goal_target = str(candidate_capability_discovery.get("selected_goal_target") or "")
    base_goal_detected = goal_oriented_request_detected(raw_message)
    actionable_candidate_detected = (
        candidate_goal_target not in {"", "general_project_goal"}
        and not _clarification_first_request_detected(raw_message)
    )
    goal_detected = base_goal_detected or actionable_candidate_detected
    guided_detected = guided_development_request_detected(raw_message)
    continuation_detected = continuation_development_request_detected(raw_message)
    collaborative_detected = collaborative_development_request_detected(raw_message)
    goal_mapping = (
        goal_mapping_from_workspace(
            message=raw_message,
            workspace_state=workspace_state,
            candidate_capability_discovery=candidate_capability_discovery,
        )
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
    if continuation_detected and not isinstance(workspace_state, dict):
        mapped_target = (
            str(goal_mapping.get("goal_target") or "")
            if isinstance(goal_mapping, dict)
            else ""
        )
        if mapped_target in {"", "active_objective", "general_project_goal"}:
            clarification_required = True
            clarification_reason = "continuation request requires deterministic workspace state"
    if collaborative_detected and collaborative_development_request_requires_workspace(raw_message, workspace_state):
        clarification_required = True
        clarification_reason = "collaborative development request requires deterministic workspace state"
    if _clarification_first_request_detected(raw_message) and not guided_detected and not base_goal_detected:
        clarification_required = True
        clarification_reason = "deterministic capability inference requires goal confirmation"
    if (
        candidate_capability_discovery.get("ambiguity_remaining_after_deterministic_analysis") is True
        and not isinstance(workspace_state, dict)
        and not guided_detected
    ):
        clarification_required = True
        clarification_reason = "multiple inferred capability targets remain plausible"
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
        "continuation_development_request_detected": continuation_detected,
        "collaborative_development_request_detected": collaborative_detected,
        "candidate_capability_discovery": deepcopy(candidate_capability_discovery),
        "candidate_capabilities": deepcopy(candidate_capability_discovery.get("candidate_capabilities")),
        "capability_resolution_decision": candidate_capability_discovery.get(
            "capability_resolution_decision"
        ),
        "human_capability_name_required": False,
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


def human_conversation_experience_from_resolution(
    *,
    message: str,
    guidance: dict[str, Any] | None,
    knowledge_reuse: dict[str, Any] | None,
    development_intent: dict[str, Any],
    workspace_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the canonical Platform Core human conversation response model."""

    prompt = require_string(message, "message")
    lowered = " ".join(prompt.lower().split())
    guidance_model = guidance if isinstance(guidance, dict) else {}
    reuse_model = knowledge_reuse if isinstance(knowledge_reuse, dict) else {}
    intent = development_intent if isinstance(development_intent, dict) else {}
    clarification_plan = deterministic_clarification_plan(
        message=prompt,
        workspace_state=workspace_state,
        guidance=guidance_model,
        knowledge_reuse=reuse_model,
        development_intent=intent,
    )
    response_mode = "INFORMATIONAL"
    headline = "I inspected the project state."
    explanation = "I did not find enough deterministic development intent to prepare governed execution."
    questions: list[str] = []
    next_step = "Describe the capability, improvement, or decision you want AiGOL to help with."
    if intent.get("summary_admissible") is True:
        response_mode = "APPROVAL_PREPARATION"
        headline = "I can prepare this as governed development work."
        explanation = (
            "I checked the workspace, considered reuse, and prepared a governed implementation summary. "
            "Approval will delegate to the certified runtime; the interface will not execute or authorize work."
        )
        next_step = "Review the summary and approve only if it matches your intent."
    elif intent.get("clarification_required") is True:
        response_mode = "CLARIFICATION"
        headline = "I need one clarification before governed execution."
        explanation = _conversation_explanation_for_clarification(prompt, intent)
        if _reuse_request_detected(lowered):
            headline = "I checked for reusable project capability evidence."
        elif _architecture_question_detected(lowered):
            headline = "I can help place this architecturally."
        questions = _clarification_questions_from_plan(clarification_plan)
        next_step = "Answer the question with the smallest useful detail."
    elif _reuse_request_detected(lowered):
        response_mode = "CLARIFICATION"
        headline = "I checked for reusable project capability evidence."
        explanation = (
            "Reuse decisions come from deterministic workspace and governance evidence. "
            "I inferred candidate targets first and will only ask if the goal still has more than one safe reading."
        )
        questions = _clarification_questions_from_plan(clarification_plan)
        next_step = "Choose the goal outcome or confirm the inferred target."
    elif _architecture_question_detected(lowered):
        response_mode = "CLARIFICATION"
        headline = "I can help place this architecturally."
        explanation = (
            "Architecture placement is a Platform Core decision based on the capability being discussed. "
            "I inferred candidate ownership targets before asking for clarification."
        )
        questions = _clarification_questions_from_plan(clarification_plan)
        next_step = "Confirm the desired outcome for the inferred ownership decision."
    elif _vague_improvement_or_ideation_detected(lowered):
        response_mode = "CLARIFICATION"
        headline = "I can help turn this into governed development work."
        explanation = (
            "Your request sounds like a development direction, but it does not yet identify the target "
            "capability or desired outcome."
        )
        questions = _clarification_questions_from_plan(clarification_plan)
        next_step = "Name the target capability or desired outcome."
    return _conversation_experience_artifact(
        message=prompt,
        response_mode=response_mode,
        headline=headline,
        explanation=explanation,
        questions=questions,
        next_step=next_step,
        guidance=guidance_model,
        knowledge_reuse=reuse_model,
        development_intent=intent,
        clarification_plan=clarification_plan,
    )


def _conversation_experience_artifact(
    *,
    message: str,
    response_mode: str,
    headline: str,
    explanation: str,
    questions: list[str],
    next_step: str,
    guidance: dict[str, Any],
    knowledge_reuse: dict[str, Any],
    development_intent: dict[str, Any],
    clarification_plan: dict[str, Any],
) -> dict[str, Any]:
    approval_summary = _conversation_approval_summary(
        message=message,
        development_intent=development_intent,
        approval_explanation=(
            "Approval delegates to the certified runtime; the Human Interface does not authorize or execute."
        ),
    )
    fail_closed_response = _conversation_fail_closed_response(
        message=message,
        development_intent=development_intent,
        explanation="When intent is incomplete, AiGOL asks for clarification instead of guessing or executing.",
        next_step=next_step,
    )
    artifact = {
        "artifact_type": "PLATFORM_CORE_HUMAN_CONVERSATION_EXPERIENCE_ARTIFACT_V1",
        "runtime_version": PLATFORM_CORE_HUMAN_CONVERSATION_EXPERIENCE_VERSION,
        "platform_core_project_services_version": PLATFORM_CORE_PROJECT_SERVICES_VERSION,
        "conversation_authority": "PLATFORM_CORE",
        "interface_executes_conversation": False,
        "raw_prompt": message,
        "response_mode": response_mode,
        "user_headline": headline,
        "user_explanation": explanation,
        "clarification_questions": questions,
        "deterministic_clarification_plan": deepcopy(clarification_plan),
        "clarification_planner_version": clarification_plan.get("runtime_version"),
        "clarification_planner_authority": clarification_plan.get("planner_authority"),
        "clarification_planner_selected_slot": clarification_plan.get("selected_missing_slot"),
        "clarification_question_count": len(questions),
        "recommended_next_user_action": next_step,
        "progress_messages": [
            "Workspace state inspected.",
            "Candidate capability discovery completed.",
            "Project guidance checked.",
            "Knowledge reuse checked.",
            "Development intent evaluated.",
        ],
        "approval_summary": approval_summary,
        "approval_explanation": approval_summary["approval_explanation"],
        "fail_closed_response": fail_closed_response,
        "fail_closed_explanation": fail_closed_response["fail_closed_explanation"],
        "project_guidance_summary": guidance.get("recommended_next_governed_action"),
        "knowledge_reuse_classification": knowledge_reuse.get("classification"),
        "candidate_capability_discovery": deepcopy(development_intent.get("candidate_capability_discovery")),
        "candidate_capabilities": deepcopy(development_intent.get("candidate_capabilities")),
        "capability_resolution_decision": development_intent.get("capability_resolution_decision"),
        "human_capability_name_required": False,
        "reuse_recommended": knowledge_reuse.get("reuse_recommended") is True,
        "summary_admissible": development_intent.get("summary_admissible") is True,
        "runtime_binding_admissible": development_intent.get("runtime_binding_admissible") is True,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _conversation_approval_summary(
    *,
    message: str,
    development_intent: dict[str, Any],
    approval_explanation: str,
) -> dict[str, Any]:
    summary_admissible = development_intent.get("summary_admissible") is True
    return {
        "summary_type": "GOVERNED_IMPLEMENTATION_SUMMARY",
        "summary_authority": "PLATFORM_CORE",
        "summary_title": "Governed implementation summary",
        "original_request": development_intent.get("raw_prompt") or message,
        "original_message": development_intent.get("raw_prompt") or message,
        "canonical_runtime_prompt": development_intent.get("canonical_runtime_prompt") or message,
        "refined_message": development_intent.get("canonical_runtime_prompt") or message,
        "goal_mapping": deepcopy(development_intent.get("goal_mapping")),
        "requires_human_approval": development_intent.get("requires_human_approval") is True,
        "runtime_after_approval": "CERTIFIED_PLATFORM_CORE_RUNTIME" if summary_admissible else None,
        "approval_state": "PENDING_HUMAN_APPROVAL" if summary_admissible else "NOT_APPLICABLE",
        "approval_explanation": approval_explanation,
        "human_interface_authorizes": False,
        "human_interface_executes": False,
        "acli_next_authorizes": False,
        "acli_next_executes": False,
    }


def _conversation_fail_closed_response(
    *,
    message: str,
    development_intent: dict[str, Any],
    explanation: str,
    next_step: str,
) -> dict[str, Any]:
    lowered = " ".join(message.lower().split())
    return {
        "response_type": "FAIL_CLOSED_EXPLANATION",
        "response_authority": "PLATFORM_CORE",
        "response_title": "No governed implementation summary was produced.",
        "reason": development_intent.get("clarification_reason"),
        "fail_closed_explanation": explanation,
        "recommended_next_user_action": next_step,
        "conversation_state": (
            "FAIL_CLOSED"
            if development_intent.get("summary_admissible") is not True
            and development_intent.get("clarification_required") is not True
            else "NOT_APPLICABLE"
        ),
        "interface_render_recommended": "could be better" in lowered,
        "human_interface_generates_explanation": False,
    }


def _conversation_explanation_for_clarification(prompt: str, intent: dict[str, Any]) -> str:
    reason = str(intent.get("clarification_reason") or "").strip()
    if reason == "continuation request requires deterministic workspace state":
        return "I need to know which project work should continue before I can safely resume it."
    if reason == "guided development request lacks deterministic implementation specificity":
        return "The request sounds like development work, but the target capability is not specific enough yet."
    return "I need one more detail before converting this into governed development work."


def deterministic_clarification_plan(
    *,
    message: str,
    workspace_state: dict[str, Any] | None,
    guidance: dict[str, Any],
    knowledge_reuse: dict[str, Any],
    development_intent: dict[str, Any],
) -> dict[str, Any]:
    """Plan the smallest deterministic clarification needed from existing evidence."""

    prompt = require_string(message, "message")
    lowered = " ".join(prompt.lower().split())
    candidate = _selected_candidate_from_intent(development_intent)
    discovery = development_intent.get("candidate_capability_discovery")
    if not isinstance(discovery, dict):
        discovery = {}
    active_objective = (
        workspace_state.get("active_development_objective")
        if isinstance(workspace_state, dict)
        else None
    )
    previous_answers = _previous_clarification_answer_ids(workspace_state)
    goal_mapping = development_intent.get("goal_mapping")
    if not isinstance(goal_mapping, dict):
        goal_mapping = {}
    candidate_goal_target = str(goal_mapping.get("goal_target") or "")
    if not candidate_goal_target and isinstance(discovery, dict):
        candidate_goal_target = str(discovery.get("selected_goal_target") or "")
    missing_slots = (
        []
        if development_intent.get("summary_admissible") is True
        else _clarification_missing_slots(
            lowered=lowered,
            workspace_state=workspace_state,
            active_objective=active_objective,
            development_intent=development_intent,
            knowledge_reuse=knowledge_reuse,
            candidate=candidate,
            candidate_goal_target=candidate_goal_target,
        )
    )
    ranked_slots = sorted(
        missing_slots,
        key=lambda item: (-int(item["uncertainty_rank"]), str(item["slot_id"])),
    )
    selected_slot = ranked_slots[0] if ranked_slots else None
    question = (
        _clarification_question_for_slot(
            slot=selected_slot,
            candidate=candidate,
            knowledge_reuse=knowledge_reuse,
            active_objective=active_objective,
        )
        if isinstance(selected_slot, dict)
        else None
    )
    certification_records = list_platform_capability_certifications()
    certification_capabilities = [
        str(record.get("capability_id"))
        for record in certification_records
        if isinstance(record, dict) and record.get("capability_id")
    ]
    artifact = {
        "artifact_type": "PLATFORM_CORE_DETERMINISTIC_CLARIFICATION_PLAN_ARTIFACT_V1",
        "runtime_version": PLATFORM_CORE_DETERMINISTIC_CLARIFICATION_PLANNER_VERSION,
        "platform_core_project_services_version": PLATFORM_CORE_PROJECT_SERVICES_VERSION,
        "planner_authority": "PLATFORM_CORE",
        "planning_mode": "DETERMINISTIC_SEMANTIC_PLANNING",
        "raw_prompt": prompt,
        "input_sequence": [
            "HUMAN_REQUEST",
            "WORKSPACE_CONTEXT",
            "REPLAY_CONTEXT",
            "GOVERNANCE_CONTEXT",
            "CERTIFICATION_CONTEXT",
            "CONVERSATION_CONTEXT",
            "CANDIDATE_GOVERNED_GOALS",
            "MISSING_SEMANTIC_SLOTS",
            "RANK_REMAINING_UNCERTAINTY",
            "CHOOSE_HIGHEST_VALUE_CLARIFICATION",
        ],
        "deterministic_inputs": {
            "human_request_hash": replay_hash(prompt),
            "workspace_context_available": isinstance(workspace_state, dict),
            "workspace_state_hash": workspace_state.get("artifact_hash") if isinstance(workspace_state, dict) else None,
            "replay_continuity_available": isinstance(workspace_state, dict),
            "clarification_continuity_available": bool(previous_answers),
            "canonical_semantic_artifact_available": False,
            "certification_registry_available": True,
            "certified_capability_count": len(certification_capabilities),
            "governance_evidence_available": bool(knowledge_reuse.get("relevant_certified_artifacts")),
            "previous_clarification_answers": previous_answers,
            "active_governed_workflow": active_objective,
            "project_objective": guidance.get("active_development_objective"),
            "runtime_state_available": bool(
                isinstance(workspace_state, dict) and workspace_state.get("implementation_history")
            ),
        },
        "candidate_governed_goals": deepcopy(development_intent.get("candidate_capabilities") or []),
        "selected_candidate_capability": deepcopy(candidate),
        "missing_semantic_slots": ranked_slots,
        "selected_missing_slot": selected_slot.get("slot_id") if isinstance(selected_slot, dict) else None,
        "selected_clarification_question": question,
        "clarification_questions": [question] if question else [],
        "clarification_question_count": 1 if question else 0,
        "asks_exactly_one_question": question is not None,
        "already_known_information_reused": True,
        "resolved_clarifications_suppressed": bool(previous_answers),
        "generic_template_used": False,
        "human_interface_authority": False,
        "platform_core_owns_clarification_semantics": True,
        "llm_reasoning_used": False,
        "probabilistic_routing_used": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _clarification_missing_slots(
    *,
    lowered: str,
    workspace_state: dict[str, Any] | None,
    active_objective: Any,
    development_intent: dict[str, Any],
    knowledge_reuse: dict[str, Any],
    candidate: dict[str, Any],
    candidate_goal_target: str,
) -> list[dict[str, Any]]:
    slots: list[dict[str, Any]] = []
    reason = str(development_intent.get("clarification_reason") or "")
    if reason == "continuation request requires deterministic workspace state":
        slots.append(_missing_slot("continuation_reference", 100, "No replay-backed active objective was available."))
    discovery = development_intent.get("candidate_capability_discovery")
    if not isinstance(discovery, dict):
        discovery = {}
    if discovery.get("ambiguity_remaining_after_deterministic_analysis") is True:
        slots.append(_missing_slot("capability_target_choice", 95, "Multiple deterministic capability targets tied."))
    if not candidate and candidate_goal_target in {"", "general_project_goal"}:
        slots.append(_missing_slot("capability_target", 90, "No deterministic capability target was selected."))
    if _vague_improvement_or_ideation_detected(lowered):
        if "implementation" in lowered:
            slots.append(_missing_slot("implementation_specificity", 91, "Implementation request lacks target behavior."))
        elif candidate or candidate_goal_target not in {"", "general_project_goal"}:
            slots.append(_missing_slot("desired_outcome", 85, "The capability target is inferred but outcome is missing."))
        else:
            slots.append(_missing_slot("capability_target", 90, "The request is ideation without a target capability."))
    if _architecture_question_detected(lowered):
        if candidate:
            slots.append(
                _missing_slot(
                    "architecture_outcome",
                    88,
                    "Architecture placement needs the outcome before ownership can be determined.",
                )
            )
        else:
            slots.append(_missing_slot("architecture_subject", 92, "Architecture placement subject is missing."))
    if _reuse_request_detected(lowered):
        if knowledge_reuse.get("reuse_recommended") is True or candidate:
            slots.append(_missing_slot("reuse_delta", 86, "Reuse evidence exists but the requested delta is missing."))
        else:
            slots.append(_missing_slot("reuse_goal", 84, "Reuse request lacks the user-visible goal."))
    if reason == "guided development request lacks deterministic implementation specificity":
        slots.append(_missing_slot("implementation_specificity", 89, "Guided request lacks target capability detail."))
    if active_objective and _workspace_reference_detected(lowered):
        slots = [slot for slot in slots if slot["slot_id"] not in {"continuation_reference", "capability_target"}]
        if not slots and development_intent.get("summary_admissible") is not True:
            slots.append(_missing_slot("active_objective_delta", 83, "Active objective is known but requested delta is missing."))
    if not slots and development_intent.get("clarification_required") is True:
        slots.append(_missing_slot("desired_outcome", 80, "Summary admissibility still requires one outcome detail."))
    return _dedupe_missing_slots(slots)


def _missing_slot(slot_id: str, uncertainty_rank: int, evidence_reason: str) -> dict[str, Any]:
    return {
        "slot_id": slot_id,
        "uncertainty_rank": uncertainty_rank,
        "evidence_reason": evidence_reason,
        "slot_authority": "PLATFORM_CORE",
    }


def _dedupe_missing_slots(slots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    for slot in slots:
        slot_id = str(slot.get("slot_id") or "")
        existing = by_id.get(slot_id)
        if existing is None or int(slot["uncertainty_rank"]) > int(existing["uncertainty_rank"]):
            by_id[slot_id] = slot
    return list(by_id.values())


def _clarification_question_for_slot(
    *,
    slot: dict[str, Any] | None,
    candidate: dict[str, Any],
    knowledge_reuse: dict[str, Any],
    active_objective: Any,
) -> str | None:
    if not isinstance(slot, dict):
        return None
    slot_id = str(slot.get("slot_id") or "")
    display = str(candidate.get("display_name") or "governed capability")
    if slot_id == "continuation_reference":
        return "Are you extending the current governed development objective or starting a new one?"
    if slot_id == "capability_target_choice":
        return "Which inferred governed capability should this continue?"
    if slot_id == "capability_target":
        return "What outcome should improve runtime, clarification quality, replay behavior, or another governed capability?"
    if slot_id == "desired_outcome":
        return f"What outcome should the {display} improvement produce?"
    if slot_id == "architecture_outcome":
        return f"What outcome should the {display} architecture decision enable?"
    if slot_id == "architecture_subject":
        return "What user-visible behavior or artifact should be placed architecturally? Include the outcome it should enable."
    if slot_id == "reuse_delta":
        artifacts = knowledge_reuse.get("relevant_certified_artifacts")
        if isinstance(artifacts, list) and artifacts:
            return f"What new outcome should be added to the existing {display} evidence?"
        return f"What outcome should change in the existing {display} capability?"
    if slot_id == "reuse_goal":
        return "What user-visible outcome should I check against existing governed work?"
    if slot_id == "implementation_specificity":
        return "What should be improved or built? Name the capability or runtime behavior this implementation should change."
    if slot_id == "active_objective_delta":
        objective = str(active_objective or "active objective")
        return f"What should change next in {objective}?"
    return "What remaining outcome should this governed development work produce?"


def _clarification_questions_from_plan(plan: dict[str, Any]) -> list[str]:
    questions = unique_strings(plan.get("clarification_questions"))
    return questions[:1]


def _previous_clarification_answer_ids(workspace_state: dict[str, Any] | None) -> list[str]:
    if not isinstance(workspace_state, dict):
        return []
    pending = workspace_state.get("pending_clarification_request")
    if isinstance(pending, dict):
        return unique_strings(pending.get("answered_clarification_question_ids"))
    continuity = workspace_state.get("clarification_continuity")
    if isinstance(continuity, dict):
        return unique_strings(continuity.get("answered_clarification_question_ids"))
    return []


def _conversation_questions_for_prompt(
    prompt: str,
    knowledge_reuse: dict[str, Any],
    intent: dict[str, Any],
) -> list[str]:
    lowered = " ".join(prompt.lower().split())
    candidate = _selected_candidate_from_intent(intent)
    if _reuse_request_detected(lowered):
        if candidate:
            return [
                _goal_oriented_candidate_question(candidate, knowledge_reuse),
                "What problem should the reused or extended work solve for the user?",
            ]
        return [
            "What user-visible outcome should I check for prior implementation?",
            "What problem are you trying to avoid solving twice?",
        ]
    if _architecture_question_detected(lowered):
        if candidate:
            return [
                _goal_oriented_candidate_question(candidate, knowledge_reuse),
                "Should the outcome be reusable Platform Core behavior or interface-only presentation?",
            ]
        return [
            "What user-visible behavior or artifact should be placed architecturally?",
            "What outcome should the architecture decision enable for users?",
        ]
    if continuation_development_request_detected(prompt):
        return [
            "Which previous user goal should continue?",
            "What constraint should remain preserved while continuing?",
        ]
    if knowledge_reuse.get("reuse_recommended") is True:
        return [
            "Should AiGOL extend the existing related capability or create new governed work?",
            "What change should be made to the existing capability?",
        ]
    if _vague_improvement_or_ideation_detected(lowered):
        if candidate:
            return [
                _goal_oriented_candidate_question(candidate, knowledge_reuse),
                "What outcome would make the improvement successful?",
            ]
        return [
            "What should be improved or built?",
            "What outcome would make the improvement successful?",
        ]
    return guided_development_clarification(prompt)["clarification_questions"]


def _reuse_request_detected(lowered: str) -> bool:
    return any(
        term in lowered
        for term in (
            "already implemented",
            "already exists",
            "reuse",
            "reuse something",
            "something similar",
            "check whether",
            "search previous work",
        )
    )


def _selected_candidate_from_intent(intent: dict[str, Any]) -> dict[str, Any]:
    discovery = intent.get("candidate_capability_discovery")
    if not isinstance(discovery, dict):
        return {}
    selected = discovery.get("selected_candidate_capability")
    return selected if isinstance(selected, dict) else {}


def _goal_oriented_candidate_question(
    candidate: dict[str, Any],
    knowledge_reuse: dict[str, Any],
) -> str:
    display = str(candidate.get("display_name") or "the inferred target")
    artifacts = knowledge_reuse.get("relevant_certified_artifacts")
    if isinstance(artifacts, list) and artifacts:
        return f"I found existing {display} evidence. What outcome should this improvement add?"
    if candidate.get("workspace_match") is True:
        return f"I found an active {display} thread in the workspace. What should change next?"
    return f"I inferred {display} as the target. What outcome should this produce?"


def _architecture_question_detected(lowered: str) -> bool:
    return any(
        term in lowered
        for term in (
            "platform core",
            "belong in",
            "inside the interface",
            "make this reusable",
            "architecture",
            "architectural",
        )
    )


def _vague_improvement_or_ideation_detected(lowered: str) -> bool:
    return any(
        term in lowered
        for term in (
            "i have an idea",
            "not sure how",
            "help me decide",
            "what do you recommend",
            "should be improved",
            "can be better",
            "something should be improved",
            "build something",
            "improve this",
        )
    )


def canonical_development_runtime_prompt(message: str) -> str:
    """Return a deterministic runtime prompt for governed development continuation."""

    prompt = require_string(message, "message")
    if is_native_development_prompt(prompt):
        return prompt
    lowered = prompt.lower()
    if guided_development_request_detected(prompt) and not guided_development_clarification_required(prompt):
        if "governed" in lowered or "governance" in lowered:
            return f"{prompt} Implement as a native development governance workflow."
        contextual_development_terms = (
            "capability",
            "current functionality",
            "implementation",
            "previous implementation",
            "solution",
        )
        if any(term in lowered for term in contextual_development_terms):
            return f"{prompt} Implement as a governed development workflow."
    if continuation_development_request_detected(prompt) and (
        "governed" in lowered
        or "interface" in lowered
        or "support" in lowered
        or "workflow" in lowered
    ):
        return f"{prompt} Implement as a governed development workflow."
    return prompt


def goal_mapping_from_workspace(
    *,
    message: str,
    workspace_state: dict[str, Any] | None,
    candidate_capability_discovery: dict[str, Any] | None = None,
) -> dict[str, Any]:
    lowered = message.lower()
    discovery = candidate_capability_discovery if isinstance(candidate_capability_discovery, dict) else {}
    discovered_target = str(discovery.get("selected_goal_target") or "")
    selected_candidate = (
        discovery.get("selected_candidate_capability")
        if isinstance(discovery.get("selected_candidate_capability"), dict)
        else {}
    )
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
    elif "release notes" in lowered:
        governed_request = "Add governed release notes support."
        goal_type = "EXTENDS_PROJECT"
        target = "release_notes"
    elif continuation_development_request_detected(message):
        governed_request = continuation_development_governed_request(
            message=message,
            active_objective=active_objective,
        )
        goal_type = "CONTINUES_PROJECT"
        target = "active_objective"
    elif collaborative_development_request_detected(message):
        governed_request = collaborative_development_governed_request(
            message=message,
            active_objective=active_objective,
        )
        goal_type = "MODIFIES_PROJECT" if active_objective else "EXTENDS_PROJECT"
        target = "active_objective" if active_objective else "general_project_goal"
    elif guided_development_request_detected(message):
        governed_request = message
        goal_type = "MODIFIES_PROJECT" if active_objective else "EXTENDS_PROJECT"
        target = discovered_target if discovered_target else "general_project_goal"
    elif discovered_target and discovered_target != "general_project_goal":
        governed_request = _governed_request_for_discovered_capability(
            message=message,
            selected_candidate=selected_candidate,
        )
        goal_type = (
            "CONTINUES_PROJECT"
            if discovered_target == "active_objective"
            else str(selected_candidate.get("default_goal_type") or "EXTENDS_PROJECT")
        )
        target = discovered_target
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
        candidate_capability_discovery=discovery,
    )
    return mapping


def _governed_request_for_discovered_capability(
    *,
    message: str,
    selected_candidate: dict[str, Any],
) -> str:
    source = require_string(message, "message")
    display_name = str(selected_candidate.get("display_name") or "inferred capability").strip()
    objective = extract_human_objective(source)
    if source.lower().strip().startswith(("implement ", "add ", "create ", "build ")):
        return source
    return (
        f"Implement governed development work to improve {display_name}. "
        f"Human objective: {objective}."
    )


def continuation_development_request_detected(message: str) -> bool:
    lowered = " ".join(require_string(message, "message").lower().split())
    if not lowered.startswith(
        (
            "continue ",
            "continue developing",
            "continue implementing",
            "continue improving",
            "keep developing",
            "keep improving",
            "let's finish",
            "lets finish",
            "let's keep going",
            "lets keep going",
            "pick up ",
            "resume ",
            "let's continue",
            "lets continue",
        )
    ):
        return False
    negative_subjects = (
        "conversation",
        "talking",
        "writing documentation",
        "chat",
    )
    if any(subject in lowered for subject in negative_subjects):
        return False
    if lowered in {"continue", "continue.", "resume", "resume.", "pick up", "pick up."}:
        return False
    continuation_subjects = (
        "aigol",
        "capability",
        "development",
        "developing",
        "implementation",
        "implementing",
        "improving",
        "github actions",
        "going",
        "interface",
        "mobile",
        "project",
        "platform",
        "previous",
        "previous task",
        "support",
        "what we started",
        "where we stopped",
        "where we left off",
        "work",
    )
    return any(subject in lowered for subject in continuation_subjects)


def continuation_development_governed_request(
    *,
    message: str,
    active_objective: Any,
) -> str:
    objective = str(active_objective or "").strip()
    source = require_string(message, "message")
    if objective and objective != "No active development objective":
        return (
            "Implement the next governed development workflow for the active "
            f"project objective: {objective}. Source continuation request: {source}"
        )
    return (
        "Implement the next governed development workflow for the active "
        f"project. Source continuation request: {source}"
    )


def collaborative_development_request_detected(message: str) -> bool:
    lowered = " ".join(require_string(message, "message").lower().split())
    if lowered.startswith(("i have another idea", "i'm not sure", "im not sure", "what do you recommend")):
        return False
    collaborative_prefixes = (
        "can we ",
        "could we ",
        "i think we should ",
        "i'd like to ",
        "id like to ",
        "let's ",
        "lets ",
        "we should ",
        "we should probably ",
    )
    if not lowered.startswith(collaborative_prefixes):
        return False
    development_actions = (
        "add",
        "expand",
        "extend",
        "improve",
        "refactor",
    )
    if not any(action in lowered for action in development_actions):
        return False
    development_references = (
        "capability",
        "current functionality",
        "existing capability",
        "implementation",
        "platform",
        "previous implementation",
        "project",
        "this",
        "work",
    )
    return any(reference in lowered for reference in development_references)


def collaborative_development_request_requires_workspace(
    message: str,
    workspace_state: dict[str, Any] | None,
) -> bool:
    if isinstance(workspace_state, dict):
        return False
    lowered = " ".join(require_string(message, "message").lower().split())
    workspace_bound_references = (
        "current functionality",
        "previous implementation",
        "this",
        "work",
    )
    return any(reference in lowered for reference in workspace_bound_references)


def collaborative_development_governed_request(
    *,
    message: str,
    active_objective: Any,
) -> str:
    objective = str(active_objective or "").strip()
    source = require_string(message, "message")
    if objective and objective != "No active development objective":
        return (
            "Implement the requested governed development improvement for the active "
            f"project objective: {objective}. Source request: {source}"
        )
    return (
        "Implement the requested governed development improvement for the active "
        f"project. Source request: {source}"
    )


def guided_development_request_detected(message: str) -> bool:
    lowered = message.lower().strip()
    return lowered.startswith(
        (
            "add ",
            "build ",
            "create ",
            "enhance ",
            "expand ",
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
        "capability",
        "current functionality",
        "implementation",
        "previous implementation",
        "solution",
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
            "What user-visible outcome should this development work produce?",
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
