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
from aigol.runtime.platform_project_objective_inference import (
    infer_platform_project_objective,
    interpret_request_clause_roles,
    validate_platform_project_objective,
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
PLATFORM_CORE_CLARIFICATION_COMPLETION_VERSION = (
    "G19_HI_04_CLARIFICATION_COMPLETION_LIFECYCLE_V1"
)
PLATFORM_CORE_CLARIFICATION_CONTEXT_SUFFICIENCY_VERSION = (
    "G19_HI_06_FIRST_PASS_CONTEXT_SUFFICIENCY_TRANSITION_V1"
)
PLATFORM_CORE_WORK_TYPE_PRESERVATION_VERSION = (
    "G19_HI_02_GOVERNED_WORK_TYPE_PRESERVATION_V1"
)
PLATFORM_CORE_PREPARED_WORK_TYPE_RESOLUTION_VERSION = (
    "G19_HI_08_PREPARED_WORK_TYPE_RESOLUTION_REFACTORING_V1"
)
PLATFORM_CORE_READ_ONLY_WORK_BINDING_VERSION = (
    "G19_HI_10_GOVERNED_READ_ONLY_RUNTIME_BINDING_V1"
)
PLATFORM_CORE_OPERATIONAL_TURN_BINDING_VERSION = (
    "G30_04_OPERATIONAL_PLATFORM_CORE_TURN_BINDING_INTEGRATION_V1"
)
PLATFORM_CORE_OPERATIONAL_TURN_BINDING_ARTIFACT_V1 = (
    "PLATFORM_CORE_OPERATIONAL_TURN_BINDING_ARTIFACT_V1"
)
PLATFORM_CORE_CLARIFICATION_ENVELOPE_V1 = (
    "PLATFORM_CORE_OPERATIONAL_CLARIFICATION_ENVELOPE_V1"
)
PLATFORM_CORE_ARTIFACT_ATTACHMENT_RETRY_VERSION = (
    "G30_07_FAIL_CLOSED_IN_SESSION_ARTIFACT_ATTACHMENT_RETRY_CONTINUITY_V1"
)
PLATFORM_CORE_ARTIFACT_ATTACHMENT_RETRY_STATE_V1 = (
    "PLATFORM_CORE_ARTIFACT_ATTACHMENT_RETRY_STATE_V1"
)
ATTACHMENT_RETRY_ELIGIBLE = "ATTACHMENT_RETRY_ELIGIBLE"
ATTACHMENT_RETRY_COMPLETED = "ATTACHMENT_RETRY_COMPLETED"
ATTACHMENT_RETRY_TERMINAL = "ATTACHMENT_RETRY_TERMINAL"

OPERATIONAL_PLATFORM_QUERY = "OPERATIONAL_PLATFORM_QUERY"
OPERATIONAL_GOVERNED_WORK = "OPERATIONAL_GOVERNED_WORK"
OPERATIONAL_CLARIFICATION_REPLY = "OPERATIONAL_CLARIFICATION_REPLY"
PLATFORM_QUERY_ROUTER_BINDING = "PLATFORM_QUERY_ROUTER"
PLATFORM_PROJECT_SERVICES_BINDING = "PLATFORM_CORE_PROJECT_SERVICES"
G29_SEMANTIC_SELECTION_CLARIFICATION_OWNER = "G29_SEMANTIC_CAPABILITY_SELECTION"

GOVERNED_READ_ONLY_WORK_BOUND = "GOVERNED_READ_ONLY_WORK_BOUND"
GOVERNED_READ_ONLY_WORK_NOT_REQUIRED = "GOVERNED_READ_ONLY_WORK_NOT_REQUIRED"
GOVERNED_READ_ONLY_WORK_FAILED_CLOSED = "GOVERNED_READ_ONLY_WORK_FAILED_CLOSED"

CANONICAL_GOVERNED_WORK_TYPES = (
    "AUDIT_ONLY",
    "IMPLEMENTATION",
    "REVIEW",
    "CERTIFICATION",
    "ANALYSIS",
    "DOCUMENTATION",
)
NON_MUTATING_GOVERNED_WORK_TYPES = (
    "AUDIT_ONLY",
    "REVIEW",
    "CERTIFICATION",
    "ANALYSIS",
    "DOCUMENTATION",
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
    explicit_canonical_artifacts: list[dict[str, Any]] | tuple[dict[str, Any], ...] = (),
    explicit_canonical_artifact_references: list[Any] | tuple[Any, ...] = (),
) -> dict[str, Any]:
    """Prepare the canonical Platform Core project-services context for any UHI."""

    session_root = Path(runtime_root) / require_string(session_id, "session_id")
    prior_state = latest_platform_core_workspace_state(session_root)
    ingress_capture: dict[str, Any] | None = None
    validated_explicit_artifacts = explicit_canonical_artifacts
    if explicit_canonical_artifact_references:
        from aigol.runtime.explicit_canonical_artifact_ingress_runtime import (
            run_explicit_canonical_artifact_ingress,
        )

        if explicit_canonical_artifacts:
            raise FailClosedRuntimeError(
                "explicit canonical artifact objects and references cannot be mixed"
            )
        attachment_transport_hash = replay_hash(
            list(explicit_canonical_artifact_references)
        )
        _reject_duplicate_attachment_attempt(
            workspace_state=prior_state,
            attachment_transport_hash=attachment_transport_hash,
        )
        ingress_index = next_index(
            session_root / "explicit_artifact_ingress", "*_ingress"
        )
        ingress_root = (
            session_root
            / "explicit_artifact_ingress"
            / f"{ingress_index:03d}_ingress"
        )
        ingress_capture = run_explicit_canonical_artifact_ingress(
            ingress_id=f"G29-08-INGRESS-{session_id}-{ingress_index:03d}",
            session_id=session_id,
            opaque_artifact_references=explicit_canonical_artifact_references,
            runtime_root=runtime_root,
            workspace=workspace,
            created_at=created_at,
            replay_dir=ingress_root,
        )
        validated_explicit_artifacts = tuple(
            ingress_capture["validated_canonical_artifacts"]
        )
    else:
        attachment_transport_hash = None
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
    turn_index = next_index(
        session_root / "operational_turn_binding",
        "*_operational_turn_binding_recorded.json",
    )
    turn_reference = str(
        session_root
        / "operational_turn_binding"
        / f"{turn_index:03d}_operational_turn_binding_recorded.json"
    )
    clarification_continuity = None
    owner_specific_continuation: dict[str, Any] | None = None
    informational_router_response: dict[str, Any] | None = None
    operational_classification: dict[str, Any] | None = None
    active_clarification_state = replay_backed_uhi_clarification_state(prior_state)
    active_envelope = (
        active_clarification_state.get("operational_clarification_envelope")
        if isinstance(active_clarification_state, dict)
        and isinstance(
            active_clarification_state.get("operational_clarification_envelope"), dict
        )
        else None
    )
    if active_envelope is not None:
        owner_specific_continuation = _bind_owner_specific_clarification_reply(
            reply=message,
            session_id=session_id,
            active_envelope=active_envelope,
            prior_workspace_state=prior_state,
            created_at=created_at,
            turn_reference=turn_reference,
        )
        development_intent = owner_specific_continuation["development_intent_resolution"]
        clarification_continuity = owner_specific_continuation["clarification_continuity"]
        effective_message = owner_specific_continuation["original_message"]
    elif active_clarification_state is not None:
        development_intent, clarification_continuity = resolve_uhi_clarification_continuity(
            message=message,
            workspace_state=prior_state,
            active_clarification_state=active_clarification_state,
            session_root=session_root,
            created_at=created_at,
        )
        effective_message = str(
            development_intent.get("clarification_resolved_query")
            if development_intent.get("query_class_continuity_applicable") is True
            else message
        )
    else:
        operational_classification = _classify_new_operational_turn(
            message=message,
            workspace_state=prior_state,
            created_at=created_at,
            explicit_artifact_transport_present=bool(
                explicit_canonical_artifacts
                or explicit_canonical_artifact_references
            ),
            turn_reference=turn_reference,
            session_id=session_id,
        )
        if (
            operational_classification["binding_destination"]
            == PLATFORM_QUERY_ROUTER_BINDING
        ):
            informational_router_response = operational_classification[
                "platform_query_router_response"
            ]
        development_intent = resolve_development_intent(message=message, workspace_state=prior_state)
        effective_message = message
    goal_mapping = (
        development_intent.get("goal_mapping")
        if isinstance(development_intent.get("goal_mapping"), dict)
        else goal_mapping_from_workspace(message=effective_message, workspace_state=prior_state)
    )
    knowledge_reuse = (
        goal_mapping.get("contextual_task_mapping")
        if isinstance(goal_mapping, dict) and isinstance(goal_mapping.get("contextual_task_mapping"), dict)
        else project_knowledge_context_from_workspace(
            message=effective_message,
            workspace_state=prior_state,
            goal_target="general_project_goal",
            governed_request=effective_message,
        )
    )
    if owner_specific_continuation is not None:
        project_objective = validate_platform_project_objective(
            owner_specific_continuation["originating_project_objective_artifact"]
        )
    elif informational_router_response is not None:
        project_objective = None
    else:
        project_objective = infer_platform_project_objective(
            request=effective_message,
            development_intent=development_intent,
            workspace_state=prior_state,
            project_guidance=guidance,
            created_at=created_at,
        )
        validate_platform_project_objective(project_objective)
    development_intent = deepcopy(development_intent)
    if project_objective is not None:
        development_intent["project_objective_inference"] = deepcopy(project_objective)
        development_intent["project_objective_inference_hash"] = project_objective["artifact_hash"]
        development_intent["project_objective_sufficient"] = project_objective["objective_sufficient"]
    if (
        project_objective is not None
        and project_objective.get("work_type_binding_required") is True
    ):
        objective_work_type = str(project_objective["requested_work_type"])
        development_intent["requested_work_type"] = objective_work_type
        development_intent["work_type"] = objective_work_type
        development_intent["prepared_work_type"] = objective_work_type
        development_intent["work_type_source"] = "PROJECT_OBJECTIVE_INFERENCE"
        development_intent["work_type_source_text"] = (
            project_objective.get("objective_work_type_source")
        )
        development_intent["mutation_allowed"] = False
        development_intent["runtime_implementation"] = False
        development_intent["work_type_conflict_detected"] = False
        development_intent["work_type_conflict_reason"] = None
        development_intent["summary_admissible"] = False
        development_intent["runtime_binding_admissible"] = False
        development_intent["read_only_work_binding_admissible"] = True
        development_intent["read_only_work_binding_status"] = GOVERNED_READ_ONLY_WORK_BOUND
        development_intent["requires_human_approval"] = False
        development_intent["project_objective_work_type_bound"] = True
    if informational_router_response is not None:
        development_intent.update(
            {
                "clarification_required": False,
                "clarification_reason": None,
                "requested_work_type": "INFORMATIONAL_QUERY",
                "work_type": "INFORMATIONAL_QUERY",
                "prepared_work_type": "INFORMATIONAL_QUERY",
                "work_type_source": "PLATFORM_QUERY_ROUTER_CLASSIFICATION",
                "work_type_source_text": informational_router_response.get(
                    "selected_query_class"
                ),
                "mutation_allowed": False,
                "runtime_implementation": False,
                "summary_admissible": False,
                "runtime_binding_admissible": False,
                "read_only_work_binding_admissible": True,
                "read_only_work_binding_status": GOVERNED_READ_ONLY_WORK_BOUND,
                "requires_human_approval": False,
                "operational_turn_classification": OPERATIONAL_PLATFORM_QUERY,
            }
        )
    development_intent["artifact_hash"] = replay_hash(development_intent)
    conversation_experience = human_conversation_experience_from_resolution(
        message=effective_message,
        guidance=guidance,
        knowledge_reuse=knowledge_reuse,
        development_intent=development_intent,
        workspace_state=prior_state,
    )
    development_intent = development_intent_with_context_sufficiency(
        development_intent=development_intent,
        conversation_experience=conversation_experience,
    )
    read_only_work_result = None
    if informational_router_response is not None:
        read_only_work_result = _read_only_result_from_platform_query_router(
            message=message,
            development_intent=development_intent,
            created_at=created_at,
            router_response=informational_router_response,
        )
    elif development_intent.get("read_only_work_binding_admissible") is True:
        if (
            isinstance(ingress_capture, dict)
            and ingress_capture.get("ingress_status")
            == "EXPLICIT_CANONICAL_ARTIFACT_INGRESS_FAILED_CLOSED"
        ):
            read_only_work_result = _failed_read_only_work_result(
                message=effective_message,
                development_intent=development_intent,
                created_at=created_at,
                failure_reason=str(ingress_capture.get("failure_reason")),
            )
            read_only_work_result["explicit_canonical_artifact_ingress_status"] = (
                ingress_capture["ingress_status"]
            )
            read_only_work_result["explicit_canonical_artifact_ingress_reference"] = (
                ingress_capture["replay_reference"]
            )
            read_only_work_result["artifact_hash"] = replay_hash(read_only_work_result)
        else:
            read_only_work_result = run_governed_read_only_work_binding(
                message=effective_message,
                workspace_state=prior_state,
                development_intent=development_intent,
                created_at=created_at,
                durable_work_root=session_root / "durable_governed_work",
                session_id=session_id,
                project_objective_artifact=project_objective,
                candidate_discovery_evidence=(
                    development_intent.get("candidate_capability_discovery")
                    if isinstance(
                        development_intent.get("candidate_capability_discovery"), dict
                    )
                    else None
                ),
                explicit_canonical_artifacts=validated_explicit_artifacts,
                semantic_route_root=(
                    session_root
                    / "semantic_capability_route"
                    / f"{next_index(session_root / 'semantic_capability_route', '*'):03d}_route"
                ),
            )
    if isinstance(read_only_work_result, dict):
        development_intent = development_intent_with_read_only_work_result(
            development_intent=development_intent,
            read_only_work_result=read_only_work_result,
        )
        conversation_experience = human_conversation_experience_with_read_only_result(
            conversation_experience=conversation_experience,
            read_only_work_result=read_only_work_result,
        )
    semantic_route = (
        read_only_work_result.get("semantic_capability_runtime_route")
        if isinstance(read_only_work_result, dict)
        and isinstance(read_only_work_result.get("semantic_capability_runtime_route"), dict)
        else None
    )
    operational_clarification_envelope = _operational_clarification_envelope(
        session_id=session_id,
        created_at=created_at,
        turn_reference=turn_reference,
        original_message=(
            owner_specific_continuation["original_message"]
            if owner_specific_continuation is not None
            else message
        ),
        project_objective=project_objective,
        semantic_route=semantic_route,
        development_intent=development_intent,
        parent_envelope=(
            owner_specific_continuation.get("active_envelope")
            if owner_specific_continuation is not None
            else None
        ),
    )
    attachment_retry_state = _record_artifact_attachment_retry_state(
        session_id=session_id,
        created_at=created_at,
        turn_reference=turn_reference,
        active_clarification_state=active_clarification_state,
        active_envelope=active_envelope,
        ingress_capture=ingress_capture,
        semantic_route=semantic_route,
        attachment_transport_hash=attachment_transport_hash,
    )
    if (
        isinstance(attachment_retry_state, dict)
        and attachment_retry_state.get("retry_eligible") is True
        and isinstance(active_envelope, dict)
    ):
        operational_clarification_envelope = deepcopy(active_envelope)
        conversation_experience = deepcopy(conversation_experience)
        conversation_experience.update(
            {
                "artifact_attachment_retry_eligible": True,
                "artifact_attachment_retry_state": deepcopy(
                    attachment_retry_state
                ),
                "artifact_attachment_retry_original_message": active_envelope.get(
                    "original_message"
                ),
                "clarification_questions": deepcopy(
                    active_clarification_state.get("clarification_questions")
                    if isinstance(active_clarification_state, dict)
                    else []
                ),
                "operational_clarification_envelope": deepcopy(active_envelope),
                "user_headline": (
                    "The artifact attachment failed closed; the original "
                    "clarification remains active."
                ),
                "user_explanation": (
                    "Platform Core rejected the attachment before semantic "
                    "continuation or capability invocation."
                ),
                "recommended_next_user_action": (
                    "Attach a different opaque canonical artifact reference."
                ),
            }
        )
        conversation_experience["artifact_hash"] = replay_hash(
            conversation_experience
        )
    elif isinstance(attachment_retry_state, dict):
        conversation_experience = deepcopy(conversation_experience)
        conversation_experience["artifact_attachment_retry_eligible"] = False
        conversation_experience["artifact_attachment_retry_state"] = deepcopy(
            attachment_retry_state
        )
        conversation_experience["artifact_hash"] = replay_hash(
            conversation_experience
        )
    if operational_clarification_envelope is not None:
        conversation_experience = deepcopy(conversation_experience)
        conversation_experience["operational_clarification_envelope"] = deepcopy(
            operational_clarification_envelope
        )
        conversation_experience["artifact_hash"] = replay_hash(conversation_experience)
    operational_turn_binding = _finalize_operational_turn_binding(
        session_id=session_id,
        created_at=created_at,
        message=message,
        turn_reference=turn_reference,
        operational_classification=operational_classification,
        active_clarification_state=active_clarification_state,
        owner_specific_continuation=owner_specific_continuation,
        semantic_route=semantic_route,
        operational_clarification_envelope=operational_clarification_envelope,
        ingress_capture=ingress_capture,
        attachment_retry_state=attachment_retry_state,
    )
    write_json_immutable(Path(turn_reference), operational_turn_binding)
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
        "project_objective_inference": project_objective,
        "clarification_continuity": clarification_continuity,
        "operational_turn_binding": deepcopy(operational_turn_binding),
        "operational_turn_binding_reference": turn_reference,
        "operational_turn_binding_hash": operational_turn_binding["artifact_hash"],
        "operational_clarification_envelope": deepcopy(
            operational_clarification_envelope
        ),
        "artifact_attachment_retry_state": deepcopy(attachment_retry_state),
        "development_intent_resolution": development_intent,
        "human_conversation_experience": conversation_experience,
        "governed_read_only_work_result": read_only_work_result,
        "explicit_canonical_artifact_ingress": (
            deepcopy(
                ingress_capture.get("explicit_canonical_artifact_ingress_artifact")
            )
            if isinstance(ingress_capture, dict)
            else None
        ),
        "explicit_canonical_artifact_ingress_reference": (
            ingress_capture.get("replay_reference")
            if isinstance(ingress_capture, dict)
            else None
        ),
        "semantic_capability_runtime_route": (
            deepcopy(read_only_work_result.get("semantic_capability_runtime_route"))
            if isinstance(read_only_work_result, dict)
            and isinstance(
                read_only_work_result.get("semantic_capability_runtime_route"), dict
            )
            else None
        ),
        "durable_governed_work_artifact": (
            deepcopy(read_only_work_result.get("durable_governed_work_artifact"))
            if isinstance(read_only_work_result, dict)
            and isinstance(read_only_work_result.get("durable_governed_work_artifact"), dict)
            else None
        ),
        "project_workspace_authority": "PLATFORM_CORE",
        "project_guidance_authority": "PLATFORM_CORE",
        "project_knowledge_reuse_authority": "PLATFORM_CORE",
        "development_intent_resolution_authority": "PLATFORM_CORE",
        "project_objective_inference_authority": "PLATFORM_CORE",
        "human_conversation_experience_authority": "PLATFORM_CORE",
        "durable_governed_work_authority": "PLATFORM_CORE",
        "interface_authority": False,
        "interface_executes_project_services": False,
        "replay_visible": True,
        "replay_reference": str(session_root / "uhi_project_services"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    project_context_path = (
        session_root
        / "uhi_project_services"
        / f"{next_uhi_project_context_index(session_root):03d}_uhi_project_context_recorded.json"
    )
    write_json_immutable(
        project_context_path,
        artifact,
    )
    if isinstance(ingress_capture, dict):
        from aigol.runtime.explicit_canonical_artifact_ingress_runtime import (
            link_explicit_canonical_artifact_ingress,
        )

        route = artifact.get("semantic_capability_runtime_route")
        link_explicit_canonical_artifact_ingress(
            replay_dir=ingress_capture["replay_reference"],
            project_context_reference=str(project_context_path),
            project_context_hash=artifact["artifact_hash"],
            downstream_route_reference=(
                route.get("replay_reference") if isinstance(route, dict) else None
            ),
            downstream_route_hash=(
                route.get("artifact_hash") if isinstance(route, dict) else None
            ),
            downstream_route_status=(
                route.get("route_status") if isinstance(route, dict) else None
            ),
        )
    return artifact


def _classify_new_operational_turn(
    *,
    message: str,
    workspace_state: dict[str, Any] | None,
    created_at: str,
    explicit_artifact_transport_present: bool,
    turn_reference: str,
    session_id: str,
) -> dict[str, Any]:
    """Bind one new UHI turn using the existing Platform Query Router."""

    from aigol.runtime.platform_query_router import (
        GOVERNED_DEVELOPMENT_ROUTE,
        route_platform_query,
        validate_platform_query_router_response,
    )

    router = validate_platform_query_router_response(
        route_platform_query(
            query=require_string(message, "message"),
            workspace_state=workspace_state,
            created_at=created_at,
        )
    )
    roles = interpret_request_clause_roles(message)
    governed_action = bool(roles.get("requested_action_clauses"))
    governed_work_type_declared = (
        explicit_governed_work_type(message).get("work_type") is not None
    )
    classification_evidence = (
        router.get("classification_evidence")
        if isinstance(router.get("classification_evidence"), dict)
        else {}
    )
    platform_knowledge_classification = classification_evidence.get(
        "platform_knowledge_query_classification"
    )
    informational_query_addressed = (
        platform_knowledge_classification not in {None, "UNKNOWN_PLATFORM_KNOWLEDGE"}
        or require_string(message, "message").rstrip().endswith("?")
    )
    existing_development_clarification_signal = (
        _vague_improvement_or_ideation_detected(message.lower())
        or _reuse_request_detected(message.lower())
    )
    project_services_required = (
        governed_action
        or governed_work_type_declared
        or explicit_artifact_transport_present
        or router.get("selected_service") == GOVERNED_DEVELOPMENT_ROUTE
        or existing_development_clarification_signal
        or not informational_query_addressed
    )
    return {
        "turn_kind": (
            OPERATIONAL_GOVERNED_WORK
            if project_services_required
            else OPERATIONAL_PLATFORM_QUERY
        ),
        "binding_destination": (
            PLATFORM_PROJECT_SERVICES_BINDING
            if project_services_required
            else PLATFORM_QUERY_ROUTER_BINDING
        ),
        "binding_reason": (
            "EXISTING_GOVERNED_ACTION_EVIDENCE"
            if governed_action or governed_work_type_declared
            else (
                "EXPLICIT_CANONICAL_ARTIFACT_TRANSPORT"
                if explicit_artifact_transport_present
                else (
                    "EXISTING_QUERY_ROUTER_GOVERNED_DEVELOPMENT_ROUTE"
                    if router.get("selected_service") == GOVERNED_DEVELOPMENT_ROUTE
                    else (
                        "EXISTING_PROJECT_SERVICES_CLARIFICATION_SIGNAL"
                        if existing_development_clarification_signal
                        or not informational_query_addressed
                        else "EXISTING_QUERY_ROUTER_INFORMATIONAL_ROUTE"
                    )
                )
            )
        ),
        "session_id": require_string(session_id, "session_id"),
        "turn_reference": require_string(turn_reference, "turn_reference"),
        "platform_query_router_response": deepcopy(router),
        "platform_query_router_response_hash": router["artifact_hash"],
        "selected_service": router.get("selected_service"),
        "selected_query_class": router.get("selected_query_class"),
        "selected_route_score": router.get("selected_route_score"),
        "governed_action_evidence": deepcopy(roles.get("requested_action_clauses") or []),
        "classification_authority": "PLATFORM_CORE_QUERY_ROUTER",
        "human_interface_classified": False,
    }


def _read_only_result_from_platform_query_router(
    *,
    message: str,
    development_intent: dict[str, Any],
    created_at: str,
    router_response: dict[str, Any],
) -> dict[str, Any]:
    """Project an already-classified informational query into the read-only contract."""

    from aigol.runtime.platform_presentation_layer import (
        present_platform_response,
        validate_platform_presentation,
    )
    from aigol.runtime.platform_query_router import validate_platform_query_router_response

    router = validate_platform_query_router_response(router_response)
    presentation = validate_platform_presentation(
        present_platform_response(router, created_at=created_at)
    )
    result = {
        "artifact_type": "PLATFORM_CORE_GOVERNED_READ_ONLY_WORK_RESULT_V1",
        "runtime_version": PLATFORM_CORE_READ_ONLY_WORK_BINDING_VERSION,
        "binding_status": GOVERNED_READ_ONLY_WORK_BOUND,
        "created_at": require_string(created_at, "created_at"),
        "original_message": require_string(message, "message"),
        "original_message_hash": replay_hash(message),
        "requested_work_type": "INFORMATIONAL_QUERY",
        "work_type": "INFORMATIONAL_QUERY",
        "prepared_work_type": "INFORMATIONAL_QUERY",
        "read_only_work_binding_admissible": True,
        "read_only_work_result_status": "GOVERNED_READ_ONLY_RESULT_READY",
        "selected_read_only_service": router.get("selected_service"),
        "selected_query_class": router.get("selected_query_class"),
        "platform_query_router_response": deepcopy(router),
        "platform_query_router_response_hash": router.get("artifact_hash"),
        "canonical_presentation": deepcopy(presentation),
        "canonical_presentation_hash": presentation.get("presentation_hash"),
        "presentation_artifact_type": presentation.get("artifact_type"),
        "presentation_status": presentation.get("presentation_status"),
        "presentation_summary": presentation.get("summary"),
        "presentation_answer": deepcopy(presentation.get("answer")),
        "presentation_recommended_next_step": presentation.get("recommended_next_step"),
        "durable_governed_work_artifact": None,
        "semantic_capability_runtime_route": None,
        "reusable_platform_core_components": [
            "UNIFIED_PLATFORM_QUERY_ROUTER",
            "CANONICAL_PLATFORM_PRESENTATION_LAYER",
        ],
        "human_approval_required": False,
        "human_interface_authority": False,
        "platform_core_authority": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "repository_mutated": False,
        "governance_modified": False,
        "replay_modified": False,
        "runtime_implementation_invoked": False,
        "implementation_summary_created": False,
        "read_only": True,
        "replay_visible": True,
    }
    result["artifact_hash"] = replay_hash(result)
    return result


def _operational_clarification_envelope(
    *,
    session_id: str,
    created_at: str,
    turn_reference: str,
    original_message: str,
    project_objective: dict[str, Any] | None,
    semantic_route: dict[str, Any] | None,
    development_intent: dict[str, Any],
    parent_envelope: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Preserve canonical owner and slot metadata for a G29 clarification."""

    if not isinstance(semantic_route, dict) or semantic_route.get("clarification_required") is not True:
        return None
    clarification = semantic_route.get("clarification_artifact")
    if not isinstance(clarification, dict) or not isinstance(project_objective, dict):
        raise FailClosedRuntimeError("operational clarification origin is incomplete")
    selected_slot = clarification.get("selected_missing_slot")
    if not isinstance(selected_slot, str) or not selected_slot.strip():
        selected_slot = (
            "canonical_artifact_reference"
            if clarification.get("artifact_type")
            == "SEMANTIC_CAPABILITY_ARTIFACT_BINDING_CLARIFICATION_ARTIFACT_V1"
            else "capability_clarification"
        )
    envelope = {
        "artifact_type": PLATFORM_CORE_CLARIFICATION_ENVELOPE_V1,
        "runtime_version": PLATFORM_CORE_OPERATIONAL_TURN_BINDING_VERSION,
        "session_id": require_string(session_id, "session_id"),
        "created_at": require_string(created_at, "created_at"),
        "clarification_status": "ACTIVE",
        "clarification_owner": G29_SEMANTIC_SELECTION_CLARIFICATION_OWNER,
        "clarification_runtime_identity": semantic_route.get("runtime_version"),
        "semantic_slot": selected_slot,
        "originating_turn_reference": require_string(turn_reference, "turn_reference"),
        "originating_route_reference": semantic_route.get("replay_reference"),
        "originating_route_hash": semantic_route.get("artifact_hash"),
        "originating_selection_reference": semantic_route.get("selection_reference"),
        "originating_selection_hash": semantic_route.get("selection_hash"),
        "originating_project_objective_reference": semantic_route.get(
            "project_objective_reference"
        ),
        "originating_project_objective_hash": project_objective.get("artifact_hash"),
        "originating_project_objective_artifact": deepcopy(project_objective),
        "originating_clarification_artifact": deepcopy(clarification),
        "originating_clarification_hash": clarification.get("artifact_hash"),
        "original_message": require_string(original_message, "original_message"),
        "original_message_hash": replay_hash(original_message),
        "requested_work_type": development_intent.get("requested_work_type"),
        "work_type": development_intent.get("work_type"),
        "prepared_work_type": development_intent.get("prepared_work_type"),
        "work_type_source": development_intent.get("work_type_source"),
        "work_type_source_text": development_intent.get("work_type_source_text"),
        "mutation_allowed": development_intent.get("mutation_allowed"),
        "runtime_implementation": development_intent.get("runtime_implementation"),
        "clarification_questions": deepcopy(
            clarification.get("clarification_questions") or []
        ),
        "parent_clarification_envelope_hash": (
            parent_envelope.get("artifact_hash")
            if isinstance(parent_envelope, dict)
            else None
        ),
        "reply_interpretation_authority": "PLATFORM_CORE",
        "human_interface_authority": False,
        "replay_visible": True,
    }
    envelope["artifact_hash"] = replay_hash(envelope)
    return validate_operational_clarification_envelope(envelope)


def validate_operational_clarification_envelope(
    envelope: dict[str, Any],
    *,
    expected_session_id: str | None = None,
) -> dict[str, Any]:
    """Fail closed on owner, slot, session, route, or artifact substitution."""

    if not isinstance(envelope, dict):
        raise FailClosedRuntimeError("operational clarification envelope must be an object")
    candidate = deepcopy(envelope)
    if candidate.get("artifact_type") != PLATFORM_CORE_CLARIFICATION_ENVELOPE_V1:
        raise FailClosedRuntimeError("operational clarification envelope type mismatch")
    supplied_hash = candidate.pop("artifact_hash", None)
    if supplied_hash != replay_hash(candidate):
        raise FailClosedRuntimeError("operational clarification envelope hash mismatch")
    candidate["artifact_hash"] = supplied_hash
    if expected_session_id is not None and candidate.get("session_id") != expected_session_id:
        raise FailClosedRuntimeError("operational clarification cross-session reply rejected")
    if candidate.get("clarification_owner") != G29_SEMANTIC_SELECTION_CLARIFICATION_OWNER:
        raise FailClosedRuntimeError("operational clarification owner substitution detected")
    if not isinstance(candidate.get("semantic_slot"), str) or not candidate["semantic_slot"]:
        raise FailClosedRuntimeError("operational clarification semantic slot missing")
    from aigol.runtime.project_context_semantic_capability_route import (
        reconstruct_project_context_semantic_capability_route,
    )

    route = reconstruct_project_context_semantic_capability_route(
        candidate.get("originating_route_reference")
    )
    if route.get("artifact_hash") != candidate.get("originating_route_hash"):
        raise FailClosedRuntimeError("operational clarification route tampering detected")
    if route.get("session_id") != candidate.get("session_id"):
        raise FailClosedRuntimeError("operational clarification route session mismatch")
    clarification = route.get("clarification_artifact")
    if not isinstance(clarification, dict) or clarification.get("artifact_hash") != candidate.get(
        "originating_clarification_hash"
    ):
        raise FailClosedRuntimeError("operational clarification artifact substitution detected")
    route_slot = clarification.get("selected_missing_slot")
    if isinstance(route_slot, str) and route_slot != candidate.get("semantic_slot"):
        raise FailClosedRuntimeError("operational clarification slot substitution detected")
    objective = validate_platform_project_objective(
        candidate.get("originating_project_objective_artifact")
    )
    if objective.get("artifact_hash") != candidate.get("originating_project_objective_hash"):
        raise FailClosedRuntimeError("operational clarification objective substitution detected")
    return candidate


def _bind_owner_specific_clarification_reply(
    *,
    reply: str,
    session_id: str,
    active_envelope: dict[str, Any],
    prior_workspace_state: dict[str, Any] | None,
    created_at: str,
    turn_reference: str,
) -> dict[str, Any]:
    """Return a reply to the Platform Core runtime that created the clarification."""

    envelope = validate_operational_clarification_envelope(
        active_envelope,
        expected_session_id=session_id,
    )
    pending = (
        prior_workspace_state.get("pending_clarification_request")
        if isinstance(prior_workspace_state, dict)
        else None
    )
    pending_envelope = (
        pending.get("operational_clarification_envelope")
        if isinstance(pending, dict)
        else None
    )
    if not isinstance(pending_envelope, dict) or pending_envelope.get(
        "artifact_hash"
    ) != envelope.get("artifact_hash"):
        raise FailClosedRuntimeError("operational clarification stale reply rejected")
    original = require_string(envelope.get("original_message"), "original_message")
    resolution = resolve_development_intent(
        message=original,
        workspace_state=prior_workspace_state,
    )
    resolution.update(
        {
            "clarification_required": False,
            "clarification_reply_bound": True,
            "clarification_owner": envelope["clarification_owner"],
            "clarification_runtime_identity": envelope["clarification_runtime_identity"],
            "active_clarification_open_slot": envelope["semantic_slot"],
            "clarification_reply_hash": replay_hash(require_string(reply, "reply")),
            "clarification_originating_route_reference": envelope[
                "originating_route_reference"
            ],
            "clarification_originating_route_hash": envelope["originating_route_hash"],
            "requested_work_type": envelope.get("requested_work_type"),
            "work_type": envelope.get("work_type"),
            "prepared_work_type": envelope.get("prepared_work_type"),
            "work_type_source": envelope.get("work_type_source"),
            "work_type_source_text": envelope.get("work_type_source_text"),
            "mutation_allowed": envelope.get("mutation_allowed"),
            "runtime_implementation": envelope.get("runtime_implementation"),
            "summary_admissible": False,
            "runtime_binding_admissible": False,
            "read_only_work_binding_admissible": True,
            "read_only_work_binding_status": GOVERNED_READ_ONLY_WORK_BOUND,
            "requires_human_approval": False,
            "project_objective_restarted": False,
        }
    )
    resolution["artifact_hash"] = replay_hash(resolution)
    continuity = {
        "artifact_type": "PLATFORM_CORE_OWNER_SPECIFIC_CLARIFICATION_CONTINUITY_V1",
        "runtime_version": PLATFORM_CORE_OPERATIONAL_TURN_BINDING_VERSION,
        "session_id": session_id,
        "created_at": require_string(created_at, "created_at"),
        "reply_hash": replay_hash(reply),
        "reply_bound_to_active_clarification": True,
        "clarification_owner": envelope["clarification_owner"],
        "clarification_runtime_identity": envelope["clarification_runtime_identity"],
        "semantic_slot": envelope["semantic_slot"],
        "originating_turn_reference": envelope["originating_turn_reference"],
        "originating_route_reference": envelope["originating_route_reference"],
        "originating_route_hash": envelope["originating_route_hash"],
        "active_clarification_envelope_hash": envelope["artifact_hash"],
        "continuation_turn_reference": turn_reference,
        "owner_specific_continuation": True,
        "project_objective_restarted": False,
        "human_interface_authority": False,
        "platform_core_authority": True,
        "replay_visible": True,
    }
    continuity["artifact_hash"] = replay_hash(continuity)
    return {
        "original_message": original,
        "active_envelope": envelope,
        "originating_project_objective_artifact": deepcopy(
            envelope["originating_project_objective_artifact"]
        ),
        "development_intent_resolution": resolution,
        "clarification_continuity": continuity,
    }


def _record_artifact_attachment_retry_state(
    *,
    session_id: str,
    created_at: str,
    turn_reference: str,
    active_clarification_state: dict[str, Any] | None,
    active_envelope: dict[str, Any] | None,
    ingress_capture: dict[str, Any] | None,
    semantic_route: dict[str, Any] | None,
    attachment_transport_hash: str | None,
) -> dict[str, Any] | None:
    """Record one deterministic attachment attempt owned by Platform Core."""

    if not (
        isinstance(active_envelope, dict)
        and isinstance(ingress_capture, dict)
        and isinstance(attachment_transport_hash, str)
    ):
        return None
    envelope = validate_operational_clarification_envelope(
        active_envelope,
        expected_session_id=session_id,
    )
    pending = (
        active_clarification_state.get("pending_clarification_request")
        if isinstance(active_clarification_state, dict)
        else None
    )
    prior_state = (
        pending.get("artifact_attachment_retry_state")
        if isinstance(pending, dict)
        and isinstance(pending.get("artifact_attachment_retry_state"), dict)
        else None
    )
    if isinstance(prior_state, dict):
        prior_state = validate_artifact_attachment_retry_state(prior_state)
        if prior_state.get("retry_eligible") is not True:
            raise FailClosedRuntimeError(
                "artifact attachment retry rejected after terminal state"
            )
        if prior_state.get("session_id") != session_id:
            raise FailClosedRuntimeError("artifact attachment retry session mismatch")
        if prior_state.get("clarification_envelope_hash") != envelope.get(
            "artifact_hash"
        ):
            raise FailClosedRuntimeError(
                "artifact attachment retry stale clarification"
            )
    ingress = ingress_capture.get("explicit_canonical_artifact_ingress_artifact")
    if not isinstance(ingress, dict):
        raise FailClosedRuntimeError(
            "artifact attachment retry ingress resolution missing"
        )
    attempt_number = (
        int(prior_state["attempt_number"]) + 1
        if isinstance(prior_state, dict)
        else 1
    )
    route_status = (
        semantic_route.get("route_status")
        if isinstance(semantic_route, dict)
        else None
    )
    lifecycle_status = (
        semantic_route.get("lifecycle_status")
        if isinstance(semantic_route, dict)
        else None
    )
    capability_invocation_started = lifecycle_status is not None
    capability_invocation_completed = route_status == (
        "SEMANTIC_CAPABILITY_ROUTE_COMPLETED"
    )
    retry_eligible = (
        ingress.get("ingress_status")
        == "EXPLICIT_CANONICAL_ARTIFACT_INGRESS_FAILED_CLOSED"
        and semantic_route is None
        and not capability_invocation_started
    )
    retry_status = (
        ATTACHMENT_RETRY_ELIGIBLE
        if retry_eligible
        else (
            ATTACHMENT_RETRY_COMPLETED
            if capability_invocation_completed
            else ATTACHMENT_RETRY_TERMINAL
        )
    )
    attempt_identity = replay_hash(
        {
            "session_id": session_id,
            "clarification_envelope_hash": envelope["artifact_hash"],
            "attempt_number": attempt_number,
            "attachment_transport_hash": attachment_transport_hash,
        }
    )
    turn_path = Path(turn_reference)
    index = turn_path.name.split("_", 1)[0]
    attempt_reference = str(
        turn_path.parent.parent
        / "artifact_attachment_retry"
        / f"{index}_artifact_attachment_attempt_recorded.json"
    )
    state = {
        "artifact_type": PLATFORM_CORE_ARTIFACT_ATTACHMENT_RETRY_STATE_V1,
        "runtime_version": PLATFORM_CORE_ARTIFACT_ATTACHMENT_RETRY_VERSION,
        "session_id": require_string(session_id, "session_id"),
        "created_at": require_string(created_at, "created_at"),
        "attempt_number": attempt_number,
        "attempt_identity": attempt_identity,
        "attempt_reference": attempt_reference,
        "attachment_transport_hash": attachment_transport_hash,
        "clarification_owner": envelope["clarification_owner"],
        "semantic_slot": envelope["semantic_slot"],
        "clarification_envelope_hash": envelope["artifact_hash"],
        "originating_turn_reference": envelope["originating_turn_reference"],
        "originating_route_reference": envelope["originating_route_reference"],
        "originating_route_hash": envelope["originating_route_hash"],
        "originating_project_objective_hash": envelope[
            "originating_project_objective_hash"
        ],
        "prior_attempt_reference": (
            prior_state.get("attempt_reference")
            if isinstance(prior_state, dict)
            else None
        ),
        "prior_attempt_hash": (
            prior_state.get("artifact_hash")
            if isinstance(prior_state, dict)
            else None
        ),
        "ingress_reference": ingress_capture["replay_reference"],
        "ingress_request_hash": ingress.get("ingress_request_hash"),
        "ingress_resolution_hash": ingress.get("artifact_hash"),
        "ingress_status": ingress.get("ingress_status"),
        "ingress_failure_reason": ingress.get("failure_reason"),
        "continuation_route_reference": (
            semantic_route.get("replay_reference")
            if isinstance(semantic_route, dict)
            else None
        ),
        "continuation_route_hash": (
            semantic_route.get("artifact_hash")
            if isinstance(semantic_route, dict)
            else None
        ),
        "continuation_route_status": route_status,
        "capability_invocation_started": capability_invocation_started,
        "capability_invocation_completed": capability_invocation_completed,
        "retry_status": retry_status,
        "retry_eligible": retry_eligible,
        "clarification_remains_active": retry_eligible,
        "invalid_artifact_satisfied_slot": False,
        "platform_core_retry_authority": True,
        "human_interface_retry_authority": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "repository_mutated": False,
        "replay_visible": True,
    }
    state["artifact_hash"] = replay_hash(state)
    state = validate_artifact_attachment_retry_state(state)
    write_json_immutable(Path(attempt_reference), state)
    return state


def validate_artifact_attachment_retry_state(
    state: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(state, dict):
        raise FailClosedRuntimeError("artifact attachment retry state required")
    candidate = deepcopy(state)
    if candidate.get("artifact_type") != (
        PLATFORM_CORE_ARTIFACT_ATTACHMENT_RETRY_STATE_V1
    ):
        raise FailClosedRuntimeError("artifact attachment retry state type mismatch")
    if candidate.get("runtime_version") != (
        PLATFORM_CORE_ARTIFACT_ATTACHMENT_RETRY_VERSION
    ):
        raise FailClosedRuntimeError("artifact attachment retry state version mismatch")
    supplied_hash = candidate.pop("artifact_hash", None)
    if supplied_hash != replay_hash(candidate):
        raise FailClosedRuntimeError("artifact attachment retry state hash mismatch")
    candidate["artifact_hash"] = supplied_hash
    if candidate.get("clarification_owner") != (
        G29_SEMANTIC_SELECTION_CLARIFICATION_OWNER
    ):
        raise FailClosedRuntimeError("artifact attachment retry owner substitution")
    if candidate.get("semantic_slot") != "input_artifact_family":
        raise FailClosedRuntimeError("artifact attachment retry slot substitution")
    attempt_number = candidate.get("attempt_number")
    if not isinstance(attempt_number, int) or attempt_number < 1:
        raise FailClosedRuntimeError("artifact attachment retry attempt number invalid")
    expected_identity = replay_hash(
        {
            "session_id": candidate.get("session_id"),
            "clarification_envelope_hash": candidate.get(
                "clarification_envelope_hash"
            ),
            "attempt_number": attempt_number,
            "attachment_transport_hash": candidate.get(
                "attachment_transport_hash"
            ),
        }
    )
    if candidate.get("attempt_identity") != expected_identity:
        raise FailClosedRuntimeError("artifact attachment retry attempt substitution")
    if attempt_number == 1:
        if candidate.get("prior_attempt_reference") is not None or candidate.get(
            "prior_attempt_hash"
        ) is not None:
            raise FailClosedRuntimeError("artifact attachment retry ordering mismatch")
    elif not (
        isinstance(candidate.get("prior_attempt_reference"), str)
        and isinstance(candidate.get("prior_attempt_hash"), str)
    ):
        raise FailClosedRuntimeError("artifact attachment retry prior attempt missing")
    if candidate.get("retry_status") not in {
        ATTACHMENT_RETRY_ELIGIBLE,
        ATTACHMENT_RETRY_COMPLETED,
        ATTACHMENT_RETRY_TERMINAL,
    }:
        raise FailClosedRuntimeError("artifact attachment retry status invalid")
    if candidate.get("retry_eligible") is True:
        if candidate.get("retry_status") != ATTACHMENT_RETRY_ELIGIBLE:
            raise FailClosedRuntimeError("artifact attachment retry eligibility mismatch")
        if candidate.get("ingress_status") != (
            "EXPLICIT_CANONICAL_ARTIFACT_INGRESS_FAILED_CLOSED"
        ):
            raise FailClosedRuntimeError("artifact attachment retry ingress mismatch")
        if candidate.get("continuation_route_reference") is not None:
            raise FailClosedRuntimeError(
                "artifact attachment retry reached semantic continuation"
            )
        if candidate.get("capability_invocation_started") is not False:
            raise FailClosedRuntimeError(
                "artifact attachment retry reached capability invocation"
            )
        if candidate.get("clarification_remains_active") is not True:
            raise FailClosedRuntimeError(
                "artifact attachment retry clarification continuity mismatch"
            )
    elif candidate.get("clarification_remains_active") is not False:
        raise FailClosedRuntimeError(
            "artifact attachment retry terminal clarification mismatch"
        )
    if candidate.get("retry_status") == ATTACHMENT_RETRY_COMPLETED:
        if candidate.get("ingress_status") != (
            "EXPLICIT_CANONICAL_ARTIFACT_INGRESS_COMPLETED"
        ) or candidate.get("capability_invocation_completed") is not True:
            raise FailClosedRuntimeError(
                "artifact attachment retry completion state mismatch"
            )
    if candidate.get("retry_status") == ATTACHMENT_RETRY_TERMINAL and candidate.get(
        "retry_eligible"
    ) is not False:
        raise FailClosedRuntimeError("artifact attachment retry terminal state mismatch")
    if candidate.get("invalid_artifact_satisfied_slot") is not False:
        raise FailClosedRuntimeError("invalid artifact satisfied clarification slot")
    for field, expected in {
        "platform_core_retry_authority": True,
        "human_interface_retry_authority": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "repository_mutated": False,
        "replay_visible": True,
    }.items():
        if candidate.get(field) is not expected:
            raise FailClosedRuntimeError("artifact attachment retry boundary mismatch")
    return candidate


def reconstruct_artifact_attachment_retry(
    attempt_reference: str | Path,
) -> dict[str, Any]:
    current = validate_artifact_attachment_retry_state(
        load_json(Path(attempt_reference))
    )
    history: list[dict[str, Any]] = []
    cursor = current
    seen_references: set[str] = set()
    seen_transport_hashes: set[str] = set()
    while True:
        reference = str(cursor["attempt_reference"])
        if reference in seen_references:
            raise FailClosedRuntimeError("artifact attachment retry replay cycle")
        seen_references.add(reference)
        transport_hash = str(cursor["attachment_transport_hash"])
        if transport_hash in seen_transport_hashes:
            raise FailClosedRuntimeError("duplicate attachment attempt rejected")
        seen_transport_hashes.add(transport_hash)
        history.append(cursor)
        prior_reference = cursor.get("prior_attempt_reference")
        if prior_reference is None:
            break
        prior = validate_artifact_attachment_retry_state(
            load_json(Path(prior_reference))
        )
        if prior.get("artifact_hash") != cursor.get("prior_attempt_hash"):
            raise FailClosedRuntimeError("artifact attachment retry attempt substitution")
        if prior.get("attempt_number") != cursor.get("attempt_number") - 1:
            raise FailClosedRuntimeError("artifact attachment retry ordering mismatch")
        for field in (
            "session_id",
            "clarification_owner",
            "semantic_slot",
            "clarification_envelope_hash",
        ):
            if prior.get(field) != cursor.get(field):
                raise FailClosedRuntimeError(
                    "artifact attachment retry continuity mismatch"
                )
        if cursor.get("attempt_number", 1) > 1 and prior.get("retry_eligible") is not True:
            raise FailClosedRuntimeError(
                "artifact attachment retry continued after terminal state"
            )
        cursor = prior
    history.reverse()
    if [item["attempt_number"] for item in history] != list(
        range(1, len(history) + 1)
    ):
        raise FailClosedRuntimeError("artifact attachment retry ordering mismatch")
    from aigol.runtime.explicit_canonical_artifact_ingress_runtime import (
        reconstruct_explicit_canonical_artifact_ingress,
    )

    for attempt in history:
        ingress = reconstruct_explicit_canonical_artifact_ingress(
            attempt["ingress_reference"]
        )
        if ingress.get("session_id") != attempt.get("session_id"):
            raise FailClosedRuntimeError("artifact attachment retry cross-session replay")
        if ingress.get("ingress_request_hash") != attempt.get("ingress_request_hash"):
            raise FailClosedRuntimeError("artifact attachment retry ingress substitution")
        if ingress.get("ingress_resolution_hash") != attempt.get(
            "ingress_resolution_hash"
        ):
            raise FailClosedRuntimeError("artifact attachment retry ingress substitution")
        if ingress.get("ingress_status") != attempt.get("ingress_status"):
            raise FailClosedRuntimeError("artifact attachment retry ingress status mismatch")
        if ingress.get("downstream_route_hash") != attempt.get(
            "continuation_route_hash"
        ):
            raise FailClosedRuntimeError("artifact attachment retry route mismatch")
    return {
        "attempt_count": len(history),
        "attempt_history": deepcopy(history),
        "current_retry_status": current["retry_status"],
        "current_attempt_hash": current["artifact_hash"],
        "clarification_envelope_hash": current["clarification_envelope_hash"],
        "replay_hash": replay_hash(history),
    }


def _reject_duplicate_attachment_attempt(
    *,
    workspace_state: dict[str, Any] | None,
    attachment_transport_hash: str,
) -> None:
    pending = (
        workspace_state.get("pending_clarification_request")
        if isinstance(workspace_state, dict)
        else None
    )
    state = (
        pending.get("artifact_attachment_retry_state")
        if isinstance(pending, dict)
        and isinstance(pending.get("artifact_attachment_retry_state"), dict)
        else None
    )
    if not isinstance(state, dict):
        return
    reconstructed = reconstruct_artifact_attachment_retry(
        state["attempt_reference"]
    )
    if any(
        attempt.get("attachment_transport_hash") == attachment_transport_hash
        for attempt in reconstructed["attempt_history"]
    ):
        raise FailClosedRuntimeError("duplicate attachment attempt rejected")


def _finalize_operational_turn_binding(
    *,
    session_id: str,
    created_at: str,
    message: str,
    turn_reference: str,
    operational_classification: dict[str, Any] | None,
    active_clarification_state: dict[str, Any] | None,
    owner_specific_continuation: dict[str, Any] | None,
    semantic_route: dict[str, Any] | None,
    operational_clarification_envelope: dict[str, Any] | None,
    ingress_capture: dict[str, Any] | None,
    attachment_retry_state: dict[str, Any] | None,
) -> dict[str, Any]:
    if operational_classification is not None:
        turn_kind = operational_classification["turn_kind"]
        destination = operational_classification["binding_destination"]
        router = operational_classification["platform_query_router_response"]
        origin_envelope = None
    else:
        turn_kind = OPERATIONAL_CLARIFICATION_REPLY
        destination = (
            G29_SEMANTIC_SELECTION_CLARIFICATION_OWNER
            if owner_specific_continuation is not None
            else PLATFORM_PROJECT_SERVICES_BINDING
        )
        router = None
        origin_envelope = (
            owner_specific_continuation.get("active_envelope")
            if owner_specific_continuation is not None
            else None
        )
    ingress_resolution = (
        ingress_capture.get("explicit_canonical_artifact_ingress_artifact")
        if isinstance(ingress_capture, dict)
        and isinstance(
            ingress_capture.get("explicit_canonical_artifact_ingress_artifact"),
            dict,
        )
        else None
    )
    attachment_bound = (
        isinstance(origin_envelope, dict) and isinstance(ingress_resolution, dict)
    )
    artifact = {
        "artifact_type": PLATFORM_CORE_OPERATIONAL_TURN_BINDING_ARTIFACT_V1,
        "runtime_version": PLATFORM_CORE_OPERATIONAL_TURN_BINDING_VERSION,
        "session_id": require_string(session_id, "session_id"),
        "created_at": require_string(created_at, "created_at"),
        "turn_reference": require_string(turn_reference, "turn_reference"),
        "turn_kind": turn_kind,
        "user_turn_hash": replay_hash(require_string(message, "message")),
        "binding_destination": destination,
        "binding_reason": (
            operational_classification.get("binding_reason")
            if operational_classification is not None
            else "ACTIVE_CLARIFICATION_OWNER_BINDING"
        ),
        "platform_query_router_response": deepcopy(router),
        "platform_query_router_response_hash": (
            router.get("artifact_hash") if isinstance(router, dict) else None
        ),
        "selected_service": (
            router.get("selected_service") if isinstance(router, dict) else None
        ),
        "selected_query_class": (
            router.get("selected_query_class") if isinstance(router, dict) else None
        ),
        "originating_clarification_owner": (
            origin_envelope.get("clarification_owner")
            if isinstance(origin_envelope, dict)
            else None
        ),
        "originating_semantic_slot": (
            origin_envelope.get("semantic_slot")
            if isinstance(origin_envelope, dict)
            else None
        ),
        "originating_clarification_envelope_hash": (
            origin_envelope.get("artifact_hash")
            if isinstance(origin_envelope, dict)
            else None
        ),
        "originating_turn_reference": (
            origin_envelope.get("originating_turn_reference")
            if isinstance(origin_envelope, dict)
            else None
        ),
        "continuation_route_reference": (
            semantic_route.get("replay_reference")
            if isinstance(semantic_route, dict)
            else None
        ),
        "continuation_route_hash": (
            semantic_route.get("artifact_hash")
            if isinstance(semantic_route, dict)
            else None
        ),
        "continuation_semantic_slot": (
            operational_clarification_envelope.get("semantic_slot")
            if isinstance(operational_clarification_envelope, dict)
            else (
                origin_envelope.get("semantic_slot")
                if isinstance(origin_envelope, dict)
                else None
            )
        ),
        "operational_clarification_envelope": deepcopy(
            operational_clarification_envelope
        ),
        "operational_clarification_envelope_hash": (
            operational_clarification_envelope.get("artifact_hash")
            if isinstance(operational_clarification_envelope, dict)
            else None
        ),
        "in_session_opaque_artifact_attachment": attachment_bound,
        "explicit_canonical_artifact_ingress_reference": (
            ingress_capture.get("replay_reference")
            if attachment_bound and isinstance(ingress_capture, dict)
            else None
        ),
        "explicit_canonical_artifact_ingress_hash": (
            ingress_resolution.get("artifact_hash")
            if attachment_bound and isinstance(ingress_resolution, dict)
            else None
        ),
        "explicit_canonical_artifact_ingress_status": (
            ingress_resolution.get("ingress_status")
            if attachment_bound and isinstance(ingress_resolution, dict)
            else None
        ),
        "artifact_attachment_retry_state": deepcopy(attachment_retry_state),
        "artifact_attachment_retry_reference": (
            attachment_retry_state.get("attempt_reference")
            if isinstance(attachment_retry_state, dict)
            else None
        ),
        "artifact_attachment_retry_hash": (
            attachment_retry_state.get("artifact_hash")
            if isinstance(attachment_retry_state, dict)
            else None
        ),
        "classification_authority": "PLATFORM_CORE",
        "clarification_binding_authority": "PLATFORM_CORE",
        "human_interface_classified": False,
        "human_interface_interpreted_reply": False,
        "human_interface_authority": False,
        "platform_core_authority": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "repository_mutated": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return validate_operational_turn_binding(artifact)


def validate_operational_turn_binding(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("operational turn binding must be an object")
    candidate = deepcopy(artifact)
    if candidate.get("artifact_type") != PLATFORM_CORE_OPERATIONAL_TURN_BINDING_ARTIFACT_V1:
        raise FailClosedRuntimeError("operational turn binding type mismatch")
    if candidate.get("runtime_version") != PLATFORM_CORE_OPERATIONAL_TURN_BINDING_VERSION:
        raise FailClosedRuntimeError("operational turn binding version mismatch")
    supplied_hash = candidate.pop("artifact_hash", None)
    if supplied_hash != replay_hash(candidate):
        raise FailClosedRuntimeError("operational turn binding hash mismatch")
    candidate["artifact_hash"] = supplied_hash
    if candidate.get("human_interface_authority") is not False:
        raise FailClosedRuntimeError("operational turn binding interface authority invalid")
    if candidate.get("turn_kind") in {OPERATIONAL_PLATFORM_QUERY, OPERATIONAL_GOVERNED_WORK}:
        from aigol.runtime.platform_query_router import validate_platform_query_router_response

        router = validate_platform_query_router_response(
            candidate.get("platform_query_router_response")
        )
        if router.get("artifact_hash") != candidate.get("platform_query_router_response_hash"):
            raise FailClosedRuntimeError("operational turn classification lineage mismatch")
        if router.get("selected_service") != candidate.get("selected_service"):
            raise FailClosedRuntimeError("operational turn selected route substitution detected")
    elif candidate.get("turn_kind") == OPERATIONAL_CLARIFICATION_REPLY:
        if candidate.get("binding_destination") == G29_SEMANTIC_SELECTION_CLARIFICATION_OWNER:
            if candidate.get("originating_clarification_owner") != (
                G29_SEMANTIC_SELECTION_CLARIFICATION_OWNER
            ):
                raise FailClosedRuntimeError("operational turn owner substitution detected")
            if candidate.get("originating_semantic_slot") != candidate.get(
                "continuation_semantic_slot"
            ):
                raise FailClosedRuntimeError("operational turn slot substitution detected")
    else:
        raise FailClosedRuntimeError("operational turn kind invalid")
    envelope = candidate.get("operational_clarification_envelope")
    if isinstance(envelope, dict):
        validated = validate_operational_clarification_envelope(
            envelope,
            expected_session_id=str(candidate.get("session_id")),
        )
        if validated.get("artifact_hash") != candidate.get(
            "operational_clarification_envelope_hash"
        ):
            raise FailClosedRuntimeError("operational turn clarification lineage mismatch")
    attachment_bound = candidate.get("in_session_opaque_artifact_attachment") is True
    attachment_fields = (
        candidate.get("explicit_canonical_artifact_ingress_reference"),
        candidate.get("explicit_canonical_artifact_ingress_hash"),
        candidate.get("explicit_canonical_artifact_ingress_status"),
    )
    if attachment_bound:
        if candidate.get("turn_kind") != OPERATIONAL_CLARIFICATION_REPLY:
            raise FailClosedRuntimeError(
                "operational artifact attachment requires active clarification"
            )
        if not all(isinstance(value, str) and value for value in attachment_fields):
            raise FailClosedRuntimeError(
                "operational artifact attachment ingress lineage missing"
            )
        if candidate.get("originating_clarification_envelope_hash") is None:
            raise FailClosedRuntimeError(
                "operational artifact attachment clarification lineage missing"
            )
    elif any(value is not None for value in attachment_fields):
        raise FailClosedRuntimeError(
            "operational artifact attachment boundary mismatch"
        )
    retry_state = candidate.get("artifact_attachment_retry_state")
    if isinstance(retry_state, dict):
        retry_state = validate_artifact_attachment_retry_state(retry_state)
        if retry_state.get("attempt_reference") != candidate.get(
            "artifact_attachment_retry_reference"
        ) or retry_state.get("artifact_hash") != candidate.get(
            "artifact_attachment_retry_hash"
        ):
            raise FailClosedRuntimeError(
                "artifact attachment retry turn lineage mismatch"
            )
        if retry_state.get("clarification_envelope_hash") != candidate.get(
            "originating_clarification_envelope_hash"
        ):
            raise FailClosedRuntimeError(
                "operational turn stale clarification lineage: artifact attachment "
                "retry clarification substitution"
            )
        if retry_state.get("session_id") != candidate.get("session_id"):
            raise FailClosedRuntimeError(
                "artifact attachment retry session substitution"
            )
        if retry_state.get("clarification_owner") != candidate.get(
            "originating_clarification_owner"
        ):
            raise FailClosedRuntimeError(
                "artifact attachment retry owner substitution"
            )
        if retry_state.get("semantic_slot") != candidate.get(
            "originating_semantic_slot"
        ):
            raise FailClosedRuntimeError(
                "artifact attachment retry slot substitution"
            )
        if retry_state.get("ingress_resolution_hash") != candidate.get(
            "explicit_canonical_artifact_ingress_hash"
        ):
            raise FailClosedRuntimeError(
                "artifact attachment substitution: retry ingress lineage mismatch"
            )
    elif candidate.get("artifact_attachment_retry_reference") is not None or candidate.get(
        "artifact_attachment_retry_hash"
    ) is not None:
        raise FailClosedRuntimeError("artifact attachment retry boundary mismatch")
    return candidate


def reconstruct_operational_turn_binding(
    turn_reference: str | Path,
) -> dict[str, Any]:
    """Reconstruct classification and owner-specific continuation Replay."""

    turn = validate_operational_turn_binding(load_json(Path(turn_reference)))
    if turn.get("turn_kind") == OPERATIONAL_CLARIFICATION_REPLY:
        origin_reference = turn.get("originating_turn_reference")
        if not origin_reference:
            if turn.get("binding_destination") == G29_SEMANTIC_SELECTION_CLARIFICATION_OWNER:
                raise FailClosedRuntimeError("operational turn clarification origin missing")
            return turn
        origin = validate_operational_turn_binding(load_json(Path(origin_reference)))
        if origin.get("operational_clarification_envelope_hash") != turn.get(
            "originating_clarification_envelope_hash"
        ):
            raise FailClosedRuntimeError("operational turn stale clarification lineage")
        if origin.get("session_id") != turn.get("session_id"):
            raise FailClosedRuntimeError("operational turn cross-session lineage")
        if turn.get("continuation_route_reference"):
            from aigol.runtime.project_context_semantic_capability_route import (
                reconstruct_project_context_semantic_capability_route,
            )

            route = reconstruct_project_context_semantic_capability_route(
                turn["continuation_route_reference"]
            )
            if route.get("artifact_hash") != turn.get("continuation_route_hash"):
                raise FailClosedRuntimeError("operational turn continuation route tampering")
        if turn.get("in_session_opaque_artifact_attachment") is True:
            from aigol.runtime.explicit_canonical_artifact_ingress_runtime import (
                reconstruct_explicit_canonical_artifact_ingress,
            )

            ingress = reconstruct_explicit_canonical_artifact_ingress(
                turn["explicit_canonical_artifact_ingress_reference"]
            )
            if ingress.get("session_id") != turn.get("session_id"):
                raise FailClosedRuntimeError(
                    "operational artifact attachment session mismatch"
                )
            if ingress.get("ingress_resolution_hash") != turn.get(
                "explicit_canonical_artifact_ingress_hash"
            ):
                raise FailClosedRuntimeError(
                    "operational artifact attachment substitution detected"
                )
            if ingress.get("ingress_status") != turn.get(
                "explicit_canonical_artifact_ingress_status"
            ):
                raise FailClosedRuntimeError(
                    "operational artifact attachment status mismatch"
                )
            if ingress.get("downstream_route_hash") != turn.get(
                "continuation_route_hash"
            ):
                raise FailClosedRuntimeError(
                    "operational artifact attachment route lineage mismatch"
                )
            retry = reconstruct_artifact_attachment_retry(
                turn["artifact_attachment_retry_reference"]
            )
            if retry.get("current_attempt_hash") != turn.get(
                "artifact_attachment_retry_hash"
            ):
                raise FailClosedRuntimeError(
                    "operational artifact attachment retry lineage mismatch"
                )
    return turn


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
        "requested_work_type": pending.get("requested_work_type"),
        "work_type": pending.get("work_type"),
        "prepared_work_type": pending.get("prepared_work_type"),
        "work_type_source": pending.get("work_type_source"),
        "work_type_source_text": pending.get("work_type_source_text"),
        "mutation_allowed": pending.get("mutation_allowed"),
        "runtime_implementation": pending.get("runtime_implementation"),
        "work_type_change_allowed": pending.get("work_type_change_allowed"),
        "work_type_conflict_detected": pending.get("work_type_conflict_detected"),
        "work_type_conflict_reason": pending.get("work_type_conflict_reason"),
        "clarification_questions": unique_strings(pending.get("clarification_questions")),
        "clarification_question_bindings": deterministic_clarification_question_bindings(
            pending.get("clarification_questions")
        ),
        "operational_clarification_envelope": deepcopy(
            pending.get("operational_clarification_envelope")
        )
        if isinstance(pending.get("operational_clarification_envelope"), dict)
        else None,
        "pending_clarification_request": deepcopy(pending),
        "replay_backed": True,
        "platform_core_authority": True,
        "human_interface_authority": False,
    }


def clarification_explicitly_changes_query_intent(reply: str) -> bool:
    """Return whether a clarification explicitly replaces the original intent."""

    lowered = " ".join(require_string(reply, "reply").lower().split())
    return any(
        marker in lowered
        for marker in (
            "instead,",
            "instead ",
            "change the request to",
            "change my request to",
            "replace the original request",
            "replace my original request",
            "new request:",
            "ignore the original request",
        )
    )


def canonical_query_identity(
    *,
    query: str,
    workspace_state: dict[str, Any] | None,
    created_at: str,
) -> dict[str, str]:
    """Resolve replay-visible query identity through the existing router."""

    from aigol.runtime.platform_query_router import route_platform_query

    response = route_platform_query(
        query=require_string(query, "query"),
        workspace_state=workspace_state,
        created_at=created_at,
    )
    return {
        "query_class": require_string(response.get("selected_query_class"), "selected_query_class"),
        "selected_service": require_string(response.get("selected_service"), "selected_service"),
        "route_score": str(int(response.get("selected_route_score") or 0)),
        "router_response_hash": require_string(response.get("artifact_hash"), "artifact_hash"),
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
    satisfaction = clarification_satisfaction_verification(
        reply=reply,
        active_clarification_state=active_clarification_state,
    )
    question_bindings = deterministic_clarification_question_bindings(
        active_clarification_state.get("clarification_questions")
    )
    completion = clarification_completion_transition(
        satisfaction=satisfaction,
        question_bindings=question_bindings,
    )
    original_query = require_string(
        active_clarification_state.get("original_message"),
        "active_clarification_state.original_message",
    )
    explicit_intent_change = clarification_explicitly_changes_query_intent(reply)
    resolved_query = (
        reply
        if explicit_intent_change
        else clarification_resolved_development_request(
            reply=reply,
            active_clarification_state=active_clarification_state,
        )
    )
    original_query_identity = canonical_query_identity(
        query=original_query,
        workspace_state=workspace_state,
        created_at=created_at,
    )
    clarification_query_identity = canonical_query_identity(
        query=reply,
        workspace_state=workspace_state,
        created_at=created_at,
    )
    final_query_identity = canonical_query_identity(
        query=resolved_query,
        workspace_state=workspace_state,
        created_at=created_at,
    )
    original_query_class = original_query_identity["query_class"]
    final_query_class = final_query_identity["query_class"]
    query_class_continuity_applicable = (
        int(original_query_identity["route_score"]) == 100
        and original_query_class
        in {
            "ARCHITECTURAL_META_AUDIT",
            "CAPABILITY_COMPOSITION_DISCOVERY",
            "DEVELOPMENT_COMPOSITION_PLAN",
            "DURABLE_GOVERNED_WORK",
            "GENERATION_CERTIFICATION",
            "PROJECT_OBJECTIVE_INFERENCE",
        }
    )
    query_class_continuity_preserved = (
        query_class_continuity_applicable
        and not explicit_intent_change
        and final_query_class == original_query_class
    )
    query_class_continuity_decision = (
        "QUERY_CLASS_RECLASSIFIED_EXPLICIT_INTENT_CHANGE"
        if query_class_continuity_applicable and explicit_intent_change
        else (
            "ORIGINAL_QUERY_CLASS_PRESERVED"
            if query_class_continuity_preserved
            else (
                "QUERY_CLASS_CONTINUITY_FAILED_CLOSED"
                if query_class_continuity_applicable
                else "QUERY_CLASS_CONTINUITY_NOT_APPLICABLE"
            )
        )
    )
    if (
        reply_resolution.get("summary_admissible") is not True
        and satisfaction["clarification_satisfied"] is True
    ):
        resolution_source = "ORIGINAL_REQUEST_WITH_BOUND_CLARIFICATION_REPLY"
        reply_resolution = resolve_development_intent(
            message=resolved_query,
            workspace_state=workspace_state,
        )
    reply_resolution = preserve_active_clarification_work_type(
        resolution=reply_resolution,
        active_clarification_state=active_clarification_state,
    )
    completed = completion["clarification_completed"] is True
    resolved = completed
    status = (
        "CLARIFICATION_RESOLVED"
        if completed
        else "CLARIFICATION_STILL_REQUIRED"
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
        "original_query_hash": replay_hash(original_query),
        "clarification_query_hash": replay_hash(reply),
        "final_query_hash": replay_hash(resolved_query),
        "original_query_class": original_query_class,
        "clarification_query_class": clarification_query_identity["query_class"],
        "final_query_class": final_query_class,
        "original_selected_composition_capability": original_query_identity[
            "selected_service"
        ],
        "clarification_selected_composition_capability": clarification_query_identity[
            "selected_service"
        ],
        "final_selected_composition_capability": final_query_identity[
            "selected_service"
        ],
        "query_class_continuity_preserved": query_class_continuity_preserved,
        "query_class_continuity_applicable": query_class_continuity_applicable,
        "clarification_explicit_intent_change": explicit_intent_change,
        "query_class_continuity_decision": query_class_continuity_decision,
        "query_class_continuity_failed_closed": (
            query_class_continuity_decision == "QUERY_CLASS_CONTINUITY_FAILED_CLOSED"
        ),
        "clarification_question_bindings": question_bindings,
        "clarification_satisfaction_verification": deepcopy(satisfaction),
        "clarification_completion_transition": deepcopy(completion),
        "clarification_completion_status": completion["clarification_completion_status"],
        "clarification_completed": completed,
        "completed_clarification_question_ids": completion["completed_clarification_question_ids"],
        "completed_semantic_slots": completion["completed_semantic_slots"],
        "remaining_clarification_questions": completion["remaining_clarification_questions"],
        "remaining_clarification_question_bindings": completion[
            "remaining_clarification_question_bindings"
        ],
        "answered_clarification_question_ids": completion["completed_clarification_question_ids"],
        "satisfied_semantic_slots": completion["completed_semantic_slots"],
        "pending_semantic_slots": completion["pending_semantic_slots"],
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
        "requested_work_type": reply_resolution.get("requested_work_type")
        or active_clarification_state.get("requested_work_type"),
        "work_type": reply_resolution.get("work_type") or active_clarification_state.get("work_type"),
        "prepared_work_type": reply_resolution.get("prepared_work_type"),
        "mutation_allowed": reply_resolution.get("mutation_allowed"),
        "runtime_implementation": reply_resolution.get("runtime_implementation"),
        "work_type_conflict_detected": reply_resolution.get("work_type_conflict_detected"),
        "work_type_conflict_reason": reply_resolution.get("work_type_conflict_reason"),
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
    if not completed:
        enriched_resolution["clarification_required"] = True
        enriched_resolution["clarification_reason"] = (
            "clarification answer did not satisfy active semantic slot"
        )
        enriched_resolution["clarification_decision_explainability"] = satisfaction[
            "clarification_decision_explainability"
        ]
        enriched_resolution["active_clarification_open_slot"] = satisfaction["open_semantic_slot"]
        enriched_resolution["active_clarification_missing_information"] = satisfaction[
            "missing_information"
        ]
        enriched_resolution["active_clarification_original_question"] = satisfaction[
            "open_question_text"
        ]
        enriched_resolution["summary_admissible"] = False
        enriched_resolution["runtime_binding_admissible"] = False
        enriched_resolution["read_only_work_binding_admissible"] = False
        enriched_resolution["read_only_work_binding_status"] = GOVERNED_READ_ONLY_WORK_NOT_REQUIRED
        enriched_resolution["read_only_work_result_required"] = False
        enriched_resolution["requires_human_approval"] = False
    else:
        enriched_resolution["clarification_required"] = False
        enriched_resolution["clarification_completion_authority"] = "PLATFORM_CORE"
    enriched_resolution.update(
        {
            "clarification_reply_bound": True,
            "clarification_reply_resolution_source": resolution_source,
            "clarification_resolved_query": resolved_query,
            "clarification_resolved_query_hash": replay_hash(resolved_query),
            "original_query_class": original_query_class,
            "clarification_query_class": clarification_query_identity["query_class"],
            "final_query_class": final_query_class,
            "query_class_continuity_preserved": query_class_continuity_preserved,
            "query_class_continuity_applicable": query_class_continuity_applicable,
            "clarification_explicit_intent_change": explicit_intent_change,
            "query_class_continuity_decision": query_class_continuity_decision,
            "clarification_question_bindings": question_bindings,
            "clarification_satisfaction_verification": deepcopy(satisfaction),
            "clarification_completion_transition": deepcopy(completion),
            "clarification_completion_status": completion["clarification_completion_status"],
            "clarification_completed": completed,
            "completed_clarification_question_ids": completion[
                "completed_clarification_question_ids"
            ],
            "completed_semantic_slots": completion["completed_semantic_slots"],
            "remaining_clarification_questions": completion["remaining_clarification_questions"],
            "remaining_clarification_question_bindings": completion[
                "remaining_clarification_question_bindings"
            ],
            "clarification_decision_explainability": satisfaction[
                "clarification_decision_explainability"
            ],
            "answered_clarification_question_ids": completion["completed_clarification_question_ids"],
            "satisfied_semantic_slots": completion["completed_semantic_slots"],
            "pending_semantic_slots": completion["pending_semantic_slots"],
            "clarification_continuity_status": status,
            "clarification_resolved": resolved,
            "requested_work_type": reply_resolution.get("requested_work_type")
            or active_clarification_state.get("requested_work_type"),
            "work_type": reply_resolution.get("work_type") or active_clarification_state.get("work_type"),
            "prepared_work_type": reply_resolution.get("prepared_work_type"),
            "mutation_allowed": reply_resolution.get("mutation_allowed"),
            "runtime_implementation": reply_resolution.get("runtime_implementation"),
            "work_type_conflict_detected": reply_resolution.get("work_type_conflict_detected"),
            "work_type_conflict_reason": reply_resolution.get("work_type_conflict_reason"),
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
    if query_class_continuity_decision == "QUERY_CLASS_CONTINUITY_FAILED_CLOSED":
        enriched_resolution.update(
            {
                "clarification_required": True,
                "clarification_reason": (
                    "clarification changed canonical query class without an explicit "
                    "intent-change declaration"
                ),
                "summary_admissible": False,
                "runtime_binding_admissible": False,
                "read_only_work_binding_admissible": False,
                "read_only_work_binding_status": GOVERNED_READ_ONLY_WORK_NOT_REQUIRED,
                "read_only_work_result_required": False,
                "requires_human_approval": False,
                "query_class_continuity_failed_closed": True,
            }
        )
    enriched_resolution["artifact_hash"] = replay_hash(enriched_resolution)
    return enriched_resolution, continuity_artifact


def read_only_work_binding_admissible_for_intent(
    *,
    requested_work_type: str,
    prepared_work_type: str,
    clarification_required: bool,
    work_type_conflict_detected: bool,
) -> bool:
    """Return whether a non-mutating work type may bind to read-only services."""

    return (
        requested_work_type in NON_MUTATING_GOVERNED_WORK_TYPES
        and prepared_work_type == requested_work_type
        and work_type_conflict_detected is not True
    )


def run_governed_read_only_work_binding(
    *,
    message: str,
    workspace_state: dict[str, Any] | None,
    development_intent: dict[str, Any],
    created_at: str,
    durable_work_root: str | Path | None = None,
    session_id: str = "PLATFORM-CORE-READ-ONLY-SESSION",
    project_objective_artifact: dict[str, Any] | None = None,
    candidate_discovery_evidence: dict[str, Any] | None = None,
    explicit_canonical_artifacts: list[dict[str, Any]] | tuple[dict[str, Any], ...] = (),
    semantic_route_root: str | Path | None = None,
) -> dict[str, Any]:
    """Execute non-mutating work through existing read-only Platform Core services."""

    prompt = require_string(message, "message")
    intent = development_intent if isinstance(development_intent, dict) else {}
    work_type = str(intent.get("work_type") or intent.get("requested_work_type") or "")
    prepared_work_type = str(intent.get("prepared_work_type") or "")
    if intent.get("read_only_work_binding_admissible") is not True:
        result = _failed_read_only_work_result(
            message=prompt,
            development_intent=intent,
            created_at=created_at,
            failure_reason="read-only work binding is not admissible",
        )
        result["artifact_hash"] = replay_hash(result)
        return result
    try:
        semantic_route = None
        if isinstance(project_objective_artifact, dict):
            from aigol.runtime.project_context_semantic_capability_route import (
                ROUTE_NOT_ELIGIBLE,
                run_project_context_semantic_capability_route,
            )

            semantic_root = (
                Path(semantic_route_root)
                if semantic_route_root is not None
                else Path(durable_work_root or ".runtime/platform_core")
                / "semantic_capability_route"
            )
            semantic_route = run_project_context_semantic_capability_route(
                session_id=session_id,
                message=prompt,
                project_objective_artifact=project_objective_artifact,
                project_objective_reference=str(
                    project_objective_artifact.get("artifact_hash")
                ),
                explicit_canonical_artifacts=explicit_canonical_artifacts,
                created_at=created_at,
                replay_dir=semantic_root,
                workspace_state=workspace_state,
                candidate_discovery_evidence=candidate_discovery_evidence,
            )
            if semantic_route.get("route_status") != ROUTE_NOT_ELIGIBLE:
                return _read_only_result_from_semantic_capability_route(
                    message=prompt,
                    development_intent=intent,
                    created_at=created_at,
                    semantic_route=semantic_route,
                )

        from aigol.runtime.platform_presentation_layer import (
            present_platform_response,
            validate_platform_presentation,
        )
        from aigol.runtime.platform_query_router import (
            route_platform_query,
            validate_platform_query_router_response,
        )
        from aigol.runtime.platform_durable_governed_work import (
            compose_durable_governed_work,
        )

        router_response = route_platform_query(
            query=prompt,
            workspace_state=workspace_state,
            created_at=created_at,
        )
        validate_platform_query_router_response(router_response)
        presentation = present_platform_response(
            router_response,
            created_at=created_at,
        )
        validate_platform_presentation(presentation)
        service_response = router_response.get("service_response")
        durable_work = None
        if (
            router_response.get("selected_service")
            == "PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_RUNTIME"
            and isinstance(service_response, dict)
            and service_response.get("artifact_type")
            == "PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_ARTIFACT_V1"
        ):
            plan_hash = str(service_response.get("artifact_hash") or "").split(":", 1)[-1]
            replay_dir = (
                Path(durable_work_root) / plan_hash[:24]
                if durable_work_root is not None
                else None
            )
            durable_work = compose_durable_governed_work(
                development_plan_artifact=service_response,
                project_objective_artifact=(
                    intent.get("project_objective_inference")
                    if isinstance(intent.get("project_objective_inference"), dict)
                    else None
                ),
                source_work_type=work_type,
                created_at=created_at,
                replay_dir=replay_dir,
            )
        result = {
            "artifact_type": "PLATFORM_CORE_GOVERNED_READ_ONLY_WORK_RESULT_V1",
            "runtime_version": PLATFORM_CORE_READ_ONLY_WORK_BINDING_VERSION,
            "binding_status": GOVERNED_READ_ONLY_WORK_BOUND,
            "created_at": require_string(created_at, "created_at"),
            "original_message": prompt,
            "original_message_hash": replay_hash(prompt),
            "requested_work_type": work_type,
            "work_type": work_type,
            "prepared_work_type": prepared_work_type,
            "read_only_work_binding_admissible": True,
            "read_only_work_result_status": "GOVERNED_READ_ONLY_RESULT_READY",
            "selected_read_only_service": router_response.get("selected_service"),
            "selected_query_class": router_response.get("selected_query_class"),
            "platform_query_router_response": deepcopy(router_response),
            "platform_query_router_response_hash": router_response.get("artifact_hash"),
            "canonical_presentation": deepcopy(presentation),
            "canonical_presentation_hash": presentation.get("presentation_hash"),
            "presentation_artifact_type": presentation.get("artifact_type"),
            "presentation_status": presentation.get("presentation_status"),
            "presentation_summary": presentation.get("summary"),
            "presentation_answer": deepcopy(presentation.get("answer")),
            "presentation_recommended_next_step": presentation.get("recommended_next_step"),
            "durable_governed_work_artifact": deepcopy(durable_work),
            "semantic_capability_runtime_route": deepcopy(semantic_route),
            "durable_governed_work_artifact_hash": (
                durable_work.get("artifact_hash") if isinstance(durable_work, dict) else None
            ),
            "durable_governed_work_id": (
                durable_work.get("governed_work_id") if isinstance(durable_work, dict) else None
            ),
            "durable_governed_work_status": (
                durable_work.get("work_status") if isinstance(durable_work, dict) else None
            ),
            "durable_governed_work_ready_for_review": (
                isinstance(durable_work, dict)
                and durable_work.get("work_status") == "DURABLE_GOVERNED_WORK_READY_FOR_REVIEW"
            ),
            "manual_copy_paste_required": False if isinstance(durable_work, dict) else None,
            "reusable_platform_core_components": unique_strings(
                [
                    "UNIFIED_PLATFORM_QUERY_ROUTER",
                    "CANONICAL_PLATFORM_PRESENTATION_LAYER",
                    *(presentation.get("reusable_components") or []),
                ]
            ),
            "human_approval_required": False,
            "human_interface_authority": False,
            "platform_core_authority": True,
            "provider_invoked": False,
            "worker_invoked": False,
            "repository_mutated": False,
            "governance_modified": False,
            "replay_modified": False,
            "runtime_implementation_invoked": False,
            "implementation_summary_created": False,
            "read_only": True,
            "replay_visible": True,
        }
        result["artifact_hash"] = replay_hash(result)
        return result
    except Exception as exc:
        result = _failed_read_only_work_result(
            message=prompt,
            development_intent=intent,
            created_at=created_at,
            failure_reason=str(exc) or "read-only work binding failed closed",
        )
        result["artifact_hash"] = replay_hash(result)
        return result


def _read_only_result_from_semantic_capability_route(
    *,
    message: str,
    development_intent: dict[str, Any],
    created_at: str,
    semantic_route: dict[str, Any],
) -> dict[str, Any]:
    """Project the bounded G29-06 route into the existing read-only contract."""

    route = deepcopy(semantic_route)
    route_status = str(route.get("route_status") or "")
    clarification = (
        route.get("clarification_artifact")
        if isinstance(route.get("clarification_artifact"), dict)
        else None
    )
    presentation = (
        route.get("canonical_platform_presentation")
        if isinstance(route.get("canonical_platform_presentation"), dict)
        else None
    )
    clarification_required = route_status == (
        "SEMANTIC_CAPABILITY_ROUTE_CLARIFICATION_REQUIRED"
    )
    completed = route_status == "SEMANTIC_CAPABILITY_ROUTE_COMPLETED"
    failed_closed = route_status == "SEMANTIC_CAPABILITY_ROUTE_FAILED_CLOSED"
    work_type = str(
        development_intent.get("work_type")
        or development_intent.get("requested_work_type")
        or ""
    )
    if clarification_required:
        result_status = "GOVERNED_READ_ONLY_CLARIFICATION_REQUIRED"
        presentation_status = "CLARIFICATION_REQUIRED"
        summary = "Platform Core requires one clarification before capability invocation."
        next_step = "Answer the Platform Core clarification question."
    elif completed:
        result_status = "GOVERNED_READ_ONLY_RESULT_READY"
        presentation_status = presentation.get("presentation_status") if presentation else None
        summary = presentation.get("summary") if presentation else None
        next_step = presentation.get("recommended_next_step") if presentation else None
    else:
        result_status = "GOVERNED_READ_ONLY_WORK_FAILED_CLOSED"
        presentation_status = "FAILED_CLOSED"
        summary = "Semantic capability invocation failed closed."
        next_step = "Review the replay-visible failure evidence before retrying."
    result = {
        "artifact_type": "PLATFORM_CORE_GOVERNED_READ_ONLY_WORK_RESULT_V1",
        "runtime_version": PLATFORM_CORE_READ_ONLY_WORK_BINDING_VERSION,
        "binding_status": (
            GOVERNED_READ_ONLY_WORK_FAILED_CLOSED if failed_closed else GOVERNED_READ_ONLY_WORK_BOUND
        ),
        "created_at": require_string(created_at, "created_at"),
        "original_message": require_string(message, "message"),
        "original_message_hash": replay_hash(message),
        "requested_work_type": work_type,
        "work_type": work_type,
        "prepared_work_type": str(development_intent.get("prepared_work_type") or ""),
        "read_only_work_binding_admissible": True,
        "read_only_work_result_status": result_status,
        "selected_read_only_service": (
            "CANONICAL_PROJECT_CONTEXT_TO_SEMANTIC_CAPABILITY_RUNTIME_ROUTE_BINDING"
        ),
        "selected_query_class": "SEMANTIC_CAPABILITY_INVOCATION",
        "platform_query_router_response": None,
        "platform_query_router_response_hash": None,
        "semantic_capability_runtime_route": route,
        "semantic_capability_runtime_route_hash": route.get("artifact_hash"),
        "selected_capability_identifier": route.get("selected_capability_identifier"),
        "canonical_presentation": deepcopy(presentation),
        "canonical_presentation_hash": (
            presentation.get("presentation_hash") if presentation else None
        ),
        "presentation_artifact_type": presentation.get("artifact_type") if presentation else None,
        "presentation_status": presentation_status,
        "presentation_summary": summary,
        "presentation_answer": deepcopy(presentation.get("answer")) if presentation else None,
        "presentation_recommended_next_step": next_step,
        "clarification_required": clarification_required,
        "clarification_artifact": deepcopy(clarification),
        "clarification_questions": (
            deepcopy(clarification.get("clarification_questions", []))
            if clarification
            else []
        ),
        "failure_reason": route.get("failure_reason"),
        "durable_governed_work_artifact": None,
        "durable_governed_work_artifact_hash": None,
        "durable_governed_work_id": None,
        "durable_governed_work_status": None,
        "durable_governed_work_ready_for_review": False,
        "manual_copy_paste_required": False,
        "reusable_platform_core_components": [
            "CANONICAL_SEMANTIC_CAPABILITY_SELECTION_BINDING",
            "PLATFORM_KNOWLEDGE_RUNTIME",
            "CANONICAL_SEMANTIC_SELECTION_TO_CERTIFIED_CAPABILITY_INVOCATION_LIFECYCLE_BINDING",
            "CERTIFIED_CAPABILITY_INVOCATION_BINDING",
            "CANONICAL_PLATFORM_PRESENTATION_LAYER",
        ],
        "human_approval_required": False,
        "human_interface_authority": False,
        "platform_core_authority": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "repository_mutated": False,
        "governance_modified": False,
        "replay_modified": False,
        "runtime_implementation_invoked": False,
        "implementation_summary_created": False,
        "read_only": True,
        "replay_visible": True,
    }
    result["artifact_hash"] = replay_hash(result)
    return result


def development_intent_with_read_only_work_result(
    *,
    development_intent: dict[str, Any],
    read_only_work_result: dict[str, Any],
) -> dict[str, Any]:
    """Attach replay-visible read-only work result evidence to intent metadata."""

    intent = deepcopy(development_intent)
    result = read_only_work_result if isinstance(read_only_work_result, dict) else {}
    intent["read_only_work_result"] = deepcopy(result)
    intent["read_only_work_result_hash"] = result.get("artifact_hash")
    intent["read_only_work_result_status"] = result.get("read_only_work_result_status")
    intent["read_only_work_binding_status"] = result.get("binding_status")
    intent["read_only_work_selected_service"] = result.get("selected_read_only_service")
    intent["read_only_work_presentation_status"] = result.get("presentation_status")
    intent["read_only_work_provider_invoked"] = result.get("provider_invoked") is True
    intent["read_only_work_worker_invoked"] = result.get("worker_invoked") is True
    intent["read_only_work_repository_mutated"] = result.get("repository_mutated") is True
    intent["artifact_hash"] = replay_hash(intent)
    return intent


def human_conversation_experience_with_read_only_result(
    *,
    conversation_experience: dict[str, Any],
    read_only_work_result: dict[str, Any],
) -> dict[str, Any]:
    """Project a governed read-only result into the Platform Core conversation artifact."""

    conversation = deepcopy(conversation_experience)
    result = read_only_work_result if isinstance(read_only_work_result, dict) else {}
    clarification_required = result.get("clarification_required") is True
    clarification = (
        result.get("clarification_artifact")
        if isinstance(result.get("clarification_artifact"), dict)
        else {}
    )
    canonical_input_required = (
        clarification.get("selected_missing_slot") == "input_artifact_family"
    )
    if canonical_input_required:
        user_explanation = (
            "Platform Core did not invoke a capability. The "
            "input_artifact_family slot requires one compatible existing "
            "canonical artifact; descriptive text is bound to the "
            "clarification owner but is not canonical input evidence."
        )
        recommended_next_user_action = (
            "Use /attach <reference> to transport one compatible immutable "
            "Replay wrapper."
        )
    elif clarification_required:
        user_explanation = (
            "Platform Core did not invoke a capability because exact semantic "
            "or canonical input evidence remains unresolved."
        )
        recommended_next_user_action = (
            "Answer the deterministic Platform Core clarification question."
        )
    else:
        user_explanation = (
            "Platform Core routed the non-mutating request through read-only "
            "services and produced a canonical presentation artifact."
        )
        recommended_next_user_action = "Review the governed read-only result."
    conversation.update(
        {
            "response_mode": "CLARIFICATION" if clarification_required else "READ_ONLY_RESULT",
            "user_headline": (
                "Platform Core requires clarification before certified capability invocation."
                if clarification_required
                else f"I completed governed {result.get('work_type')} read-only work."
            ),
            "user_explanation": user_explanation,
            "recommended_next_user_action": recommended_next_user_action,
            "governed_read_only_work_result": deepcopy(result),
            "governed_read_only_work_result_hash": result.get("artifact_hash"),
            "read_only_work_binding_status": result.get("binding_status"),
            "read_only_work_result_status": result.get("read_only_work_result_status"),
            "read_only_work_selected_service": result.get("selected_read_only_service"),
            "read_only_work_presentation_status": result.get("presentation_status"),
            "read_only_work_provider_invoked": result.get("provider_invoked") is True,
            "read_only_work_worker_invoked": result.get("worker_invoked") is True,
            "read_only_work_repository_mutated": result.get("repository_mutated") is True,
        }
    )
    if clarification_required:
        conversation["clarification_required"] = True
        conversation["clarification_questions"] = deepcopy(
            result.get("clarification_questions") or []
        )
        conversation["clarification_reply_satisfied_semantic_slot"] = False
        conversation["canonical_artifact_transport_required"] = (
            canonical_input_required
        )
    conversation["artifact_hash"] = replay_hash(conversation)
    return conversation


def _failed_read_only_work_result(
    *,
    message: str,
    development_intent: dict[str, Any],
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    work_type = str(
        development_intent.get("work_type")
        or development_intent.get("requested_work_type")
        or ""
    )
    return {
        "artifact_type": "PLATFORM_CORE_GOVERNED_READ_ONLY_WORK_RESULT_V1",
        "runtime_version": PLATFORM_CORE_READ_ONLY_WORK_BINDING_VERSION,
        "binding_status": GOVERNED_READ_ONLY_WORK_FAILED_CLOSED,
        "created_at": require_string(created_at, "created_at"),
        "original_message": message,
        "original_message_hash": replay_hash(message),
        "requested_work_type": work_type,
        "work_type": work_type,
        "prepared_work_type": development_intent.get("prepared_work_type"),
        "read_only_work_binding_admissible": (
            development_intent.get("read_only_work_binding_admissible") is True
        ),
        "read_only_work_result_status": "GOVERNED_READ_ONLY_RESULT_FAILED_CLOSED",
        "failure_reason": failure_reason,
        "selected_read_only_service": None,
        "presentation_status": "FAILED_CLOSED",
        "presentation_summary": (
            "Platform Core rejected the read-only input before capability invocation."
        ),
        "human_approval_required": False,
        "human_interface_authority": False,
        "platform_core_authority": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "repository_mutated": False,
        "governance_modified": False,
        "replay_modified": False,
        "runtime_implementation_invoked": False,
        "implementation_summary_created": False,
        "read_only": True,
        "replay_visible": True,
    }


def clarification_completion_transition(
    *,
    satisfaction: dict[str, Any],
    question_bindings: list[dict[str, Any]],
) -> dict[str, Any]:
    """Complete satisfied clarification questions independently of downstream intent."""

    satisfied_question_ids = unique_strings(satisfaction.get("satisfied_question_ids"))
    satisfied_slots = unique_strings(satisfaction.get("satisfied_semantic_slots"))
    pending_slots = unique_strings(satisfaction.get("pending_semantic_slots"))
    remaining_bindings = [
        deepcopy(binding)
        for binding in question_bindings
        if str(binding.get("question_id") or "") not in set(satisfied_question_ids)
    ]
    remaining_questions = unique_strings(
        [binding.get("question_text") for binding in remaining_bindings]
    )
    clarification_satisfied = satisfaction.get("clarification_satisfied") is True
    completed = (
        clarification_satisfied
        and not pending_slots
        and not remaining_bindings
        and bool(satisfied_question_ids or satisfied_slots)
    )
    partially_completed = (
        clarification_satisfied
        and not pending_slots
        and bool(remaining_bindings)
    )
    status = (
        "CLARIFICATION_COMPLETED"
        if completed
        else (
            "CLARIFICATION_PARTIALLY_COMPLETED"
            if partially_completed
            else "CLARIFICATION_COMPLETION_STILL_REQUIRED"
        )
    )
    artifact = {
        "artifact_type": "PLATFORM_CORE_CLARIFICATION_COMPLETION_TRANSITION_V1",
        "runtime_version": PLATFORM_CORE_CLARIFICATION_COMPLETION_VERSION,
        "completion_authority": "PLATFORM_CORE",
        "completion_evaluation_source": "CLARIFICATION_SATISFACTION_VERIFICATION",
        "clarification_completion_status": status,
        "clarification_completed": completed,
        "clarification_partially_completed": partially_completed,
        "clarification_still_required": not completed,
        "completed_clarification_question_ids": satisfied_question_ids,
        "completed_semantic_slots": satisfied_slots,
        "remaining_clarification_questions": remaining_questions,
        "remaining_clarification_question_bindings": remaining_bindings,
        "pending_semantic_slots": pending_slots,
        "pending_clarification_should_be_removed": completed,
        "downstream_intent_admissibility_required": False,
        "approval_preparation_required_for_completion": False,
        "runtime_binding_required_for_completion": False,
        "completion_blocks_remaining": [] if completed else (
            ["remaining clarification questions"] if remaining_bindings else ["active slot not satisfied"]
        ),
        "human_interface_authority": False,
        "platform_core_owns_completion": True,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def deterministic_clarification_question_bindings(questions: Any) -> list[dict[str, Any]]:
    """Create stable identifiers for replay-backed clarification questions."""

    return [
        {
            "question_id": f"CLARIFICATION_QUESTION_{replay_hash(question)[:16]}",
            "question_text": question,
            "semantic_slot": semantic_slot_for_clarification_question(question),
            "binding_authority": "PLATFORM_CORE",
        }
        for question in unique_strings(questions)
    ]


def semantic_slot_for_clarification_question(question: Any) -> str:
    """Infer the deterministic semantic slot bound to a clarification question."""

    lowered = " ".join(str(question).lower().split())
    if "extending the current governed development objective" in lowered:
        return "continuation_reference"
    if "which inferred governed capability" in lowered:
        return "capability_target_choice"
    if "improve runtime, clarification quality, replay behavior" in lowered:
        return "capability_target"
    if "architecture decision enable" in lowered:
        return "architecture_outcome"
    if "placed architecturally" in lowered:
        return "architecture_subject"
    if "new outcome should be added" in lowered or "outcome should change in the existing" in lowered:
        return "reuse_delta"
    if "check against existing governed work" in lowered:
        return "reuse_goal"
    if "name the capability or runtime behavior" in lowered:
        return "implementation_specificity"
    if "what should change next" in lowered:
        return "active_objective_delta"
    if "what outcome should the" in lowered and "improvement produce" in lowered:
        return "desired_outcome"
    if "user-visible outcome should this development work produce" in lowered:
        return "desired_outcome"
    if "constraints or boundaries should the implementation preserve" in lowered:
        return "implementation_constraints"
    return "desired_outcome"


def clarification_satisfaction_verification(
    *,
    reply: str,
    active_clarification_state: dict[str, Any],
) -> dict[str, Any]:
    """Verify whether a reply satisfies the currently open clarification slot."""

    text = " ".join(require_string(reply, "reply").split())
    bindings = deterministic_clarification_question_bindings(
        active_clarification_state.get("clarification_questions")
    )
    satisfied_bindings = [
        binding
        for binding in bindings
        if _clarification_reply_satisfies_slot(
            reply=text,
            slot_id=str(binding.get("semantic_slot") or ""),
        )
    ]
    open_binding = (
        satisfied_bindings[0]
        if satisfied_bindings
        else (bindings[0] if bindings else None)
    )
    open_slot = (
        str(open_binding.get("semantic_slot"))
        if isinstance(open_binding, dict)
        else None
    )
    open_question = (
        str(open_binding.get("question_text"))
        if isinstance(open_binding, dict)
        else None
    )
    satisfied = bool(satisfied_bindings)
    missing_information = (
        None
        if satisfied
        else _clarification_slot_missing_information(open_slot)
    )
    explainability = clarification_decision_explainability(
        reply=text,
        slot_id=open_slot,
        question_text=open_question,
        clarification_satisfied=satisfied,
    )
    return {
        "artifact_type": "PLATFORM_CORE_CLARIFICATION_SATISFACTION_VERIFICATION_V1",
        "runtime_version": "G15_HIR_10_CLARIFICATION_SATISFACTION_VERIFICATION_V1",
        "verification_authority": "PLATFORM_CORE",
        "reply_hash": replay_hash(text),
        "open_question_id": open_binding.get("question_id") if isinstance(open_binding, dict) else None,
        "open_question_text": open_question,
        "open_semantic_slot": open_slot,
        "clarification_satisfied": satisfied,
        "satisfied_question_ids": unique_strings(
            [binding.get("question_id") for binding in satisfied_bindings]
        ),
        "satisfied_semantic_slots": unique_strings(
            [binding.get("semantic_slot") for binding in satisfied_bindings]
        ),
        "pending_semantic_slots": [] if satisfied or open_slot is None else [open_slot],
        "missing_information": missing_information,
        "clarification_decision_explainability": deepcopy(explainability),
        "identical_question_repeated": False,
        "llm_reasoning_used": False,
        "probabilistic_scoring_used": False,
        "human_interface_authority": False,
        "platform_core_owns_satisfaction": True,
        "replay_visible": True,
    }


def clarification_decision_explainability(
    *,
    reply: str,
    slot_id: str | None,
    question_text: str | None,
    clarification_satisfied: bool,
) -> dict[str, Any]:
    """Explain the deterministic clarification decision in semantic terms."""

    expected = _clarification_expected_semantic_outcome(slot_id)
    accepted = _accepted_semantic_requirements(reply=reply, slot_id=slot_id)
    required = _required_semantic_requirements(slot_id)
    remaining = [] if clarification_satisfied else [
        requirement for requirement in required if requirement not in accepted
    ]
    if not clarification_satisfied and not remaining:
        remaining = [_clarification_slot_missing_information(slot_id)]
    blocker = (
        "No semantic blocker remains for the active clarification slot."
        if clarification_satisfied
        else (
            "Deterministic continuation is blocked until the remaining semantic "
            "requirement is satisfied."
        )
    )
    return {
        "artifact_type": "PLATFORM_CORE_CLARIFICATION_DECISION_EXPLAINABILITY_V1",
        "runtime_version": "G15_HIR_11_CLARIFICATION_DECISION_EXPLAINABILITY_V1",
        "explanation_authority": "PLATFORM_CORE",
        "active_semantic_slot": slot_id,
        "active_question_text": question_text,
        "expected_semantic_outcome": expected,
        "accepted_semantic_requirements": accepted,
        "unresolved_semantic_requirements": remaining,
        "deterministic_continuation_status": (
            "READY" if clarification_satisfied else "BLOCKED"
        ),
        "deterministic_continuation_reason": blocker,
        "user_explanation": _clarification_user_explanation(
            slot_id=slot_id,
            accepted=accepted,
            remaining=remaining,
            clarification_satisfied=clarification_satisfied,
        ),
        "implementation_internals_exposed": False,
        "semantic_reasoning_only": True,
        "human_interface_authority": False,
        "replay_visible": True,
    }


def _clarification_expected_semantic_outcome(slot_id: str | None) -> str:
    if slot_id == "architecture_outcome":
        return "a reusable architecture outcome with an observable user-facing effect"
    if slot_id == "architecture_subject":
        return "the behavior or artifact being placed and the outcome that placement enables"
    if slot_id == "continuation_reference":
        return "whether the request extends the active objective or starts a new one"
    if slot_id == "capability_target_choice":
        return "the specific governed capability target to continue"
    if slot_id == "capability_target":
        return "the governed capability or outcome to improve"
    if slot_id == "desired_outcome":
        return "the observable outcome the improvement should produce"
    if slot_id == "reuse_delta":
        return "the new outcome or delta against existing governed evidence"
    if slot_id == "reuse_goal":
        return "the user-visible outcome to compare with existing governed work"
    if slot_id == "implementation_specificity":
        return "the capability or runtime behavior the implementation should change"
    if slot_id == "active_objective_delta":
        return "the next concrete change to the active objective"
    if slot_id == "implementation_constraints":
        return "the constraints or boundaries the implementation should preserve"
    return "the remaining semantic detail needed for governed continuation"


def _required_semantic_requirements(slot_id: str | None) -> list[str]:
    if slot_id == "architecture_outcome":
        return [
            "reusable Platform Core behavior",
            "Human Interface neutrality",
            "observable user-visible outcome",
        ]
    if slot_id == "architecture_subject":
        return ["behavior or artifact", "enabled outcome"]
    if slot_id == "continuation_reference":
        return ["continuation choice"]
    if slot_id == "capability_target_choice":
        return ["governed capability target"]
    if slot_id == "capability_target":
        return ["governed capability target", "desired outcome"]
    if slot_id == "desired_outcome":
        return ["observable user-visible outcome"]
    if slot_id == "reuse_delta":
        return ["existing evidence delta", "new outcome"]
    if slot_id == "reuse_goal":
        return ["user-visible reuse goal"]
    if slot_id == "implementation_specificity":
        return ["capability or runtime behavior"]
    if slot_id == "active_objective_delta":
        return ["next concrete change"]
    if slot_id == "implementation_constraints":
        return ["constraints or boundaries"]
    return ["remaining semantic detail"]


def _accepted_semantic_requirements(*, reply: str, slot_id: str | None) -> list[str]:
    lowered = reply.lower()
    accepted: list[str] = []
    if slot_id == "architecture_outcome":
        if "platform core" in lowered or "reusable" in lowered or "shared" in lowered:
            accepted.append("reusable Platform Core behavior")
        if "human interface" in lowered or "interfaces" in lowered or "shared" in lowered:
            accepted.append("Human Interface neutrality")
        if any(
            term in lowered
            for term in (
                "outcome",
                "user-visible",
                "observable",
                "enable",
                "enables",
                "become",
                "presentation adapter",
                "presentation adapters",
                "thin adapter",
                "stateless",
            )
        ):
            accepted.append("observable user-visible outcome")
    elif slot_id == "architecture_subject":
        if any(term in lowered for term in ("behavior", "artifact", "interface", "runtime", "workflow")):
            accepted.append("behavior or artifact")
        if any(term in lowered for term in ("outcome", "enable", "enables", "produce")):
            accepted.append("enabled outcome")
    elif slot_id == "continuation_reference":
        if any(term in lowered for term in ("current", "existing", "continue", "extend", "new one", "start a new")):
            accepted.append("continuation choice")
    elif slot_id == "capability_target_choice":
        if any(term in lowered for term in ("automation", "runtime", "replay", "governance", "governed", "github actions", "interface", "clarification", "validation", "worker")):
            accepted.append("governed capability target")
    elif slot_id in {"capability_target", "desired_outcome"}:
        if any(term in lowered for term in ("automation", "runtime", "replay", "governance", "governed", "github actions", "interface", "clarification", "validation", "worker")):
            accepted.append("governed capability target")
        if any(term in lowered for term in ("outcome", "produce", "improve", "enable", "behavior")):
            accepted.append("desired outcome" if slot_id == "capability_target" else "observable user-visible outcome")
    elif slot_id == "reuse_delta":
        if any(term in lowered for term in ("existing", "reuse", "evidence")):
            accepted.append("existing evidence delta")
        if any(term in lowered for term in ("outcome", "new", "change", "delta")):
            accepted.append("new outcome")
    elif slot_id == "reuse_goal":
        if any(term in lowered for term in ("outcome", "goal", "user-visible")):
            accepted.append("user-visible reuse goal")
    elif slot_id == "implementation_specificity":
        if any(term in lowered for term in ("capability", "runtime", "behavior", "workflow", "interface")):
            accepted.append("capability or runtime behavior")
    elif slot_id == "active_objective_delta":
        if any(term in lowered for term in ("change", "next", "add", "remove", "update", "improve")):
            accepted.append("next concrete change")
    elif slot_id == "implementation_constraints":
        if any(term in lowered for term in ("preserve", "boundary", "constraint", "replay", "governance")):
            accepted.append("constraints or boundaries")
    return unique_strings(accepted)


def _clarification_user_explanation(
    *,
    slot_id: str | None,
    accepted: list[str],
    remaining: list[str],
    clarification_satisfied: bool,
) -> str:
    slot_label = str(slot_id or "semantic detail").replace("_", " ")
    if clarification_satisfied:
        accepted_text = ", ".join(accepted) if accepted else "the requested semantic detail"
        return f"Accepted for {slot_label}: {accepted_text}. Deterministic continuation can proceed."
    accepted_text = ", ".join(accepted) if accepted else "no required semantic requirement yet"
    remaining_text = ", ".join(remaining) if remaining else "remaining semantic detail"
    return (
        f"Current semantic slot: {slot_label}. Accepted: {accepted_text}. "
        f"Still required: {remaining_text}. Deterministic continuation is blocked until that is provided."
    )


def _clarification_reply_satisfies_slot(*, reply: str, slot_id: str | None) -> bool:
    lowered = reply.lower()
    if len(lowered) < 20:
        return False
    outcome_terms = (
        "outcome",
        "enable",
        "enables",
        "produce",
        "create",
        "build",
        "change",
        "improve",
        "implement",
        "support",
        "behavior",
        "capability",
        "workflow",
        "runtime",
        "reusable",
        "shared",
    )
    scope_terms = (
        "aicli",
        "automation",
        "governance",
        "governed",
        "github actions",
        "human interface",
        "interfaces",
        "platform core",
        "replay",
        "runtime",
        "validation",
        "workflow",
        "worker",
        "certification",
    )
    if slot_id == "architecture_outcome":
        return (
            any(term in lowered for term in ("outcome", "enable", "enables", "behavior", "capability"))
            and any(term in lowered for term in ("platform core", "human interface", "interfaces", "reusable", "shared"))
        )
    if slot_id == "architecture_subject":
        return (
            any(term in lowered for term in ("behavior", "artifact", "interface", "platform core", "runtime", "workflow"))
            and any(term in lowered for term in outcome_terms)
        )
    if slot_id == "continuation_reference":
        return any(term in lowered for term in ("current", "existing", "continue", "extend", "new one", "start a new"))
    if slot_id == "capability_target_choice":
        return any(term in lowered for term in scope_terms)
    if slot_id == "implementation_constraints":
        return any(term in lowered for term in ("preserve", "boundary", "replay", "governance", "thin", "fail closed"))
    if slot_id in {
        "capability_target",
        "desired_outcome",
        "reuse_delta",
        "reuse_goal",
        "implementation_specificity",
        "active_objective_delta",
    }:
        return any(term in lowered for term in outcome_terms) and any(term in lowered for term in scope_terms)
    return any(term in lowered for term in outcome_terms) and any(term in lowered for term in scope_terms)


def _clarification_slot_missing_information(slot_id: str | None) -> str:
    if slot_id == "architecture_outcome":
        return "architecture outcome"
    if slot_id == "architecture_subject":
        return "user-visible behavior or artifact and the outcome it enables"
    if slot_id == "continuation_reference":
        return "whether to extend the active objective or start a new one"
    if slot_id == "capability_target_choice":
        return "which inferred governed capability should continue"
    if slot_id == "capability_target":
        return "target governed capability or outcome"
    if slot_id == "desired_outcome":
        return "desired outcome"
    if slot_id == "reuse_delta":
        return "new outcome or delta against existing evidence"
    if slot_id == "reuse_goal":
        return "user-visible reuse goal"
    if slot_id == "implementation_specificity":
        return "capability or runtime behavior to change"
    if slot_id == "active_objective_delta":
        return "next change to the active objective"
    if slot_id == "implementation_constraints":
        return "constraints or boundaries to preserve"
    return "remaining semantic detail"


def clarification_reply_substantively_answers_active_questions(
    *,
    reply: str,
    active_clarification_state: dict[str, Any],
) -> bool:
    """Return whether a free-form reply is enough to consume active clarification slots."""

    return clarification_satisfaction_verification(
        reply=reply,
        active_clarification_state=active_clarification_state,
    )["clarification_satisfied"] is True


def clarification_resolved_development_request(
    *,
    reply: str,
    active_clarification_state: dict[str, Any],
) -> str:
    """Build the Platform Core-owned request resolved from a clarification answer."""

    original = str(active_clarification_state.get("original_message") or "").strip()
    work_type = str(active_clarification_state.get("requested_work_type") or "IMPLEMENTATION")
    if work_type not in CANONICAL_GOVERNED_WORK_TYPES:
        work_type = "IMPLEMENTATION"
    questions = [
        binding["question_text"]
        for binding in deterministic_clarification_question_bindings(
            active_clarification_state.get("clarification_questions")
        )
    ]
    question_text = "\n".join(f"- {question}" for question in questions)
    if work_type == "IMPLEMENTATION":
        opening = "Implement the clarification-resolved governed development request."
        closing = "Implement as a governed development workflow."
    else:
        opening = f"Prepare the clarification-resolved governed {work_type} request."
        closing = f"Preserve governed work type {work_type}; do not convert it into implementation work."
    return "\n".join(
        [
            opening,
            f"Requested work type: {work_type}",
            f"Original request: {original}",
            "Clarification questions:",
            question_text,
            f"Clarification answer: {require_string(reply, 'reply')}",
            closing,
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
    prior_completed_clarifications = (
        prior_state.get("completed_clarifications", [])
        if isinstance(prior_state, dict) and isinstance(prior_state.get("completed_clarifications"), list)
        else []
    )
    latest_completion = (
        completion.get("development_intent_resolution", {})
        if isinstance(completion.get("development_intent_resolution"), dict)
        else {}
    )
    completed_clarifications = [*deepcopy(prior_completed_clarifications)]
    if latest_completion.get("clarification_completed") is True:
        completed_clarifications.append(
            {
                "clarification_completion_status": latest_completion.get(
                    "clarification_completion_status"
                ),
                "completed_clarification_question_ids": unique_strings(
                    latest_completion.get("completed_clarification_question_ids")
                ),
                "completed_semantic_slots": unique_strings(
                    latest_completion.get("completed_semantic_slots")
                ),
                "clarification_continuity_replay_reference": latest_completion.get(
                    "clarification_continuity_replay_reference"
                ),
                "clarification_continuity_artifact_hash": latest_completion.get(
                    "clarification_continuity_artifact_hash"
                ),
                "completion_authority": "PLATFORM_CORE",
            }
        )
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
        "completed_clarifications": completed_clarifications,
        "completed_clarification_count": len(completed_clarifications),
        "latest_clarification_completion_transition": deepcopy(
            latest_completion.get("clarification_completion_transition")
        )
        if latest_completion.get("clarification_completed") is True
        else None,
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
    clause_roles = interpret_request_clause_roles(raw_message)
    target_text = " ".join(clause_roles["capability_target_clauses"]).lower()
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
        evidence = [term for term in capability["keywords"] if term in target_text]
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
        "clause_role_interpretation": deepcopy(clause_roles),
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

    work_type_resolution = resolve_governed_work_type(raw_message)
    requested_work_type = str(work_type_resolution["requested_work_type"])
    canonical_runtime_prompt = canonical_development_runtime_prompt(governed_request)
    native_runtime_admissible = is_native_development_prompt(canonical_runtime_prompt)
    prepared_work_type_resolution = resolve_prepared_work_type(
        requested_work_type=requested_work_type,
        canonical_runtime_prompt=canonical_runtime_prompt,
        governed_work_type_metadata=work_type_resolution,
    )
    prepared_work_type = str(prepared_work_type_resolution["prepared_work_type"])
    work_type_conflict = (
        prepared_work_type != requested_work_type
        and work_type_resolution["explicit_work_type_change_declared"] is not True
    )
    mutation_allowed = work_type_resolution["mutation_allowed"] is True
    runtime_implementation = work_type_resolution["runtime_implementation"] is True
    summary_admissible = (
        (goal_detected or guided_detected)
        and not clarification_required
        and native_runtime_admissible
        and requested_work_type == "IMPLEMENTATION"
        and mutation_allowed
        and runtime_implementation
        and not work_type_conflict
    )
    runtime_binding_admissible = summary_admissible
    read_only_work_binding_admissible = read_only_work_binding_admissible_for_intent(
        requested_work_type=requested_work_type,
        prepared_work_type=prepared_work_type,
        clarification_required=clarification_required,
        work_type_conflict_detected=work_type_conflict,
    )
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
        "work_type_preservation_version": PLATFORM_CORE_WORK_TYPE_PRESERVATION_VERSION,
        "prepared_work_type_resolution_version": PLATFORM_CORE_PREPARED_WORK_TYPE_RESOLUTION_VERSION,
        "governed_work_type_metadata": deepcopy(work_type_resolution),
        "prepared_work_type_resolution": deepcopy(prepared_work_type_resolution),
        "requested_work_type": requested_work_type,
        "work_type": requested_work_type,
        "prepared_work_type": prepared_work_type,
        "runtime_prompt_work_type_signal": prepared_work_type_resolution[
            "runtime_prompt_work_type_signal"
        ],
        "work_type_source": work_type_resolution["work_type_source"],
        "work_type_source_text": work_type_resolution["work_type_source_text"],
        "mutation_allowed": mutation_allowed,
        "runtime_implementation": runtime_implementation,
        "work_type_change_allowed": work_type_resolution["work_type_change_allowed"],
        "work_type_conflict_detected": work_type_conflict,
        "work_type_conflict_reason": work_type_conflict_reason(
            requested_work_type=requested_work_type,
            prepared_work_type=prepared_work_type,
            mutation_allowed=mutation_allowed,
            runtime_implementation=runtime_implementation,
        )
        if work_type_conflict or not mutation_allowed or not runtime_implementation
        else None,
        "knowledge_reuse_classification_is_work_type": False,
        "summary_admissible": summary_admissible,
        "runtime_binding_admissible": runtime_binding_admissible,
        "read_only_work_binding_version": PLATFORM_CORE_READ_ONLY_WORK_BINDING_VERSION,
        "read_only_work_binding_admissible": read_only_work_binding_admissible,
        "read_only_work_binding_status": (
            GOVERNED_READ_ONLY_WORK_BOUND
            if read_only_work_binding_admissible
            else GOVERNED_READ_ONLY_WORK_NOT_REQUIRED
        ),
        "read_only_work_supported_types": list(NON_MUTATING_GOVERNED_WORK_TYPES),
        "read_only_work_result_required": read_only_work_binding_admissible,
        "read_only_work_human_approval_required": False,
        "read_only_work_provider_invocation_allowed": False,
        "read_only_work_worker_invocation_allowed": False,
        "read_only_work_mutation_allowed": False,
        "same_decision_for_send_and_approve": True,
        "acli_next_executes_resolution": False,
        "requires_human_approval": summary_admissible,
        "replay_visible": True,
    }
    resolution["artifact_hash"] = replay_hash(resolution)
    return resolution


def resolve_governed_work_type(message: str) -> dict[str, Any]:
    """Resolve explicit governed work-type metadata for Platform Core artifacts."""

    prompt = require_string(message, "message")
    explicit = explicit_governed_work_type(prompt)
    clause_roles = interpret_request_clause_roles(prompt)
    inferred_read_only_validation = (
        explicit["work_type"] is None
        and clause_roles["non_mutation_constraint_detected"] is True
        and (
            clause_roles["read_only_validation_action_detected"] is True
            or clause_roles["read_only_inspection_action_detected"] is True
        )
    )
    requested = explicit["work_type"] or ("AUDIT_ONLY" if inferred_read_only_validation else "IMPLEMENTATION")
    work_type_source = (
        "EXPLICIT_NON_MUTATING_VALIDATION_OBJECTIVE"
        if inferred_read_only_validation
        else explicit["source"]
    )
    work_type_source_text = (
        "validation action with explicit non-mutation constraint"
        if inferred_read_only_validation
        else explicit["source_text"]
    )
    mutation_allowed = requested == "IMPLEMENTATION"
    artifact = {
        "artifact_type": "PLATFORM_CORE_GOVERNED_WORK_TYPE_METADATA_V1",
        "runtime_version": PLATFORM_CORE_WORK_TYPE_PRESERVATION_VERSION,
        "work_type_authority": "PLATFORM_CORE",
        "requested_work_type": requested,
        "work_type": requested,
        "work_type_source": work_type_source,
        "work_type_source_text": work_type_source_text,
        "clause_role_interpretation": deepcopy(clause_roles),
        "supported_work_types": list(CANONICAL_GOVERNED_WORK_TYPES),
        "mutation_allowed": mutation_allowed,
        "runtime_implementation": requested == "IMPLEMENTATION",
        "work_type_change_allowed": False,
        "explicit_work_type_change_declared": False,
        "work_type_conflict_detected": False,
        "work_type_conflict_reason": None,
        "knowledge_reuse_classification_is_work_type": False,
        "human_interface_authority": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def preserve_active_clarification_work_type(
    *,
    resolution: dict[str, Any],
    active_clarification_state: dict[str, Any],
) -> dict[str, Any]:
    """Carry immutable work type from the active clarification into the resolved intent."""

    requested = str(active_clarification_state.get("requested_work_type") or "").strip()
    if requested not in CANONICAL_GOVERNED_WORK_TYPES:
        return resolution
    enriched = deepcopy(resolution)
    prompt = str(enriched.get("canonical_runtime_prompt") or enriched.get("raw_prompt") or "")
    prepared_resolution = resolve_prepared_work_type(
        requested_work_type=requested,
        canonical_runtime_prompt=prompt,
        governed_work_type_metadata=enriched.get("governed_work_type_metadata"),
    )
    prepared = str(prepared_resolution["prepared_work_type"])
    mutation_allowed = requested == "IMPLEMENTATION"
    runtime_implementation = requested == "IMPLEMENTATION"
    conflict = prepared != requested
    metadata = deepcopy(enriched.get("governed_work_type_metadata"))
    if not isinstance(metadata, dict):
        metadata = {}
    metadata.update(
        {
            "requested_work_type": requested,
            "work_type": requested,
            "work_type_source": active_clarification_state.get("work_type_source"),
            "work_type_source_text": active_clarification_state.get("work_type_source_text"),
            "mutation_allowed": mutation_allowed,
            "runtime_implementation": runtime_implementation,
            "work_type_change_allowed": False,
            "prepared_work_type_resolution_version": (
                PLATFORM_CORE_PREPARED_WORK_TYPE_RESOLUTION_VERSION
            ),
            "prepared_work_type_resolution": deepcopy(prepared_resolution),
            "prepared_work_type": prepared,
            "runtime_prompt_work_type_signal": prepared_resolution[
                "runtime_prompt_work_type_signal"
            ],
            "work_type_conflict_detected": conflict,
            "work_type_conflict_reason": work_type_conflict_reason(
                requested_work_type=requested,
                prepared_work_type=prepared,
                mutation_allowed=mutation_allowed,
                runtime_implementation=runtime_implementation,
            )
            if conflict or not mutation_allowed or not runtime_implementation
            else None,
            "active_clarification_work_type_preserved": True,
        }
    )
    metadata["artifact_hash"] = replay_hash(metadata)
    runtime_admissible = (
        enriched.get("runtime_binding_admissible") is True
        and requested == "IMPLEMENTATION"
        and mutation_allowed
        and runtime_implementation
        and not conflict
    )
    read_only_work_binding_admissible = read_only_work_binding_admissible_for_intent(
        requested_work_type=requested,
        prepared_work_type=prepared,
        clarification_required=enriched.get("clarification_required") is True,
        work_type_conflict_detected=conflict,
    )
    enriched.update(
        {
            "governed_work_type_metadata": metadata,
            "requested_work_type": requested,
            "work_type": requested,
            "prepared_work_type": prepared,
            "prepared_work_type_resolution_version": (
                PLATFORM_CORE_PREPARED_WORK_TYPE_RESOLUTION_VERSION
            ),
            "prepared_work_type_resolution": deepcopy(prepared_resolution),
            "runtime_prompt_work_type_signal": prepared_resolution[
                "runtime_prompt_work_type_signal"
            ],
            "work_type_source": active_clarification_state.get("work_type_source"),
            "work_type_source_text": active_clarification_state.get("work_type_source_text"),
            "mutation_allowed": mutation_allowed,
            "runtime_implementation": runtime_implementation,
            "work_type_change_allowed": False,
            "work_type_conflict_detected": conflict,
            "work_type_conflict_reason": metadata["work_type_conflict_reason"],
            "active_clarification_work_type_preserved": True,
            "summary_admissible": runtime_admissible,
            "runtime_binding_admissible": runtime_admissible,
            "read_only_work_binding_version": PLATFORM_CORE_READ_ONLY_WORK_BINDING_VERSION,
            "read_only_work_binding_admissible": read_only_work_binding_admissible,
            "read_only_work_binding_status": (
                GOVERNED_READ_ONLY_WORK_BOUND
                if read_only_work_binding_admissible
                else GOVERNED_READ_ONLY_WORK_NOT_REQUIRED
            ),
            "read_only_work_supported_types": list(NON_MUTATING_GOVERNED_WORK_TYPES),
            "read_only_work_result_required": read_only_work_binding_admissible,
            "read_only_work_human_approval_required": False,
            "read_only_work_provider_invocation_allowed": False,
            "read_only_work_worker_invocation_allowed": False,
            "read_only_work_mutation_allowed": False,
            "requires_human_approval": runtime_admissible,
        }
    )
    enriched["artifact_hash"] = replay_hash(enriched)
    return enriched


def explicit_governed_work_type(message: str) -> dict[str, str | None]:
    """Return explicit work-type declarations without treating reuse class as work type."""

    lowered = " ".join(require_string(message, "message").lower().replace("-", "_").split())
    declarations = {
        "AUDIT_ONLY": (
            "work_type: audit_only",
            "work type: audit_only",
            "work_type=audit_only",
            "audit_only",
            "audit only",
        ),
        "IMPLEMENTATION": (
            "work_type: implementation",
            "work type: implementation",
            "work_type=implementation",
            "implementation_only",
        ),
        "REVIEW": (
            "work_type: review",
            "work type: review",
            "work_type=review",
            "review_only",
        ),
        "CERTIFICATION": (
            "work_type: certification",
            "work type: certification",
            "work_type=certification",
            "certification_only",
        ),
        "ANALYSIS": (
            "work_type: analysis",
            "work type: analysis",
            "work_type=analysis",
            "analysis_only",
        ),
        "DOCUMENTATION": (
            "work_type: documentation",
            "work type: documentation",
            "work_type=documentation",
            "documentation_only",
        ),
    }
    matches: list[tuple[str, str]] = []
    for work_type, markers in declarations.items():
        for marker in markers:
            if marker in lowered:
                matches.append((work_type, marker))
                break
    if len(matches) == 1:
        return {
            "work_type": matches[0][0],
            "source": "EXPLICIT_HUMAN_WORK_TYPE_DECLARATION",
            "source_text": matches[0][1],
        }
    if len(matches) > 1:
        return {
            "work_type": matches[0][0],
            "source": "CONFLICTING_EXPLICIT_HUMAN_WORK_TYPE_DECLARATIONS",
            "source_text": ", ".join(match[1] for match in matches),
        }
    return {
        "work_type": None,
        "source": "DEFAULT_GOVERNED_DEVELOPMENT_WORK_TYPE",
        "source_text": None,
    }


def runtime_prompt_work_type_signal(prompt: str) -> dict[str, Any]:
    """Record runtime-prompt work-type wording as evidence, not authority."""

    lowered = " ".join(require_string(prompt, "prompt").lower().split())
    implementation_markers = (
        "implement ",
        "implement as a governed development workflow",
        "implement as a native development governance workflow",
    )
    starts_with_implementation = lowered.startswith(
        ("implement ", "add ", "build ", "create ", "fix ", "repair ", "update ")
    )
    contains_implementation_marker = any(marker in lowered for marker in implementation_markers)
    signal = (
        "IMPLEMENTATION"
        if starts_with_implementation or contains_implementation_marker
        else "NO_RUNTIME_IMPLEMENTATION_SIGNAL"
    )
    artifact = {
        "artifact_type": "PLATFORM_CORE_RUNTIME_PROMPT_WORK_TYPE_SIGNAL_V1",
        "runtime_version": PLATFORM_CORE_PREPARED_WORK_TYPE_RESOLUTION_VERSION,
        "signal_authority": "PLATFORM_CORE_EVIDENCE_ONLY",
        "prompt_hash": replay_hash(prompt),
        "runtime_prompt_work_type_signal": signal,
        "implementation_marker_detected": signal == "IMPLEMENTATION",
        "starts_with_implementation_command": starts_with_implementation,
        "contains_implementation_marker": contains_implementation_marker,
        "signal_changes_prepared_work_type": False,
        "human_interface_authority": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def resolve_prepared_work_type(
    *,
    requested_work_type: str,
    canonical_runtime_prompt: str,
    governed_work_type_metadata: dict[str, Any] | None = None,
    governed_work_type_transition: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve prepared work type from authoritative governance metadata."""

    requested = require_string(requested_work_type, "requested_work_type")
    if requested not in CANONICAL_GOVERNED_WORK_TYPES:
        requested = "IMPLEMENTATION"
    metadata = governed_work_type_metadata if isinstance(governed_work_type_metadata, dict) else {}
    transition = governed_work_type_transition if isinstance(governed_work_type_transition, dict) else {}
    prompt_signal = runtime_prompt_work_type_signal(canonical_runtime_prompt)
    transition_authorized = (
        transition.get("work_type_change_authorized") is True
        and transition.get("transition_authority") == "PLATFORM_CORE"
        and transition.get("human_authorization_recorded") is True
        and transition.get("replay_visible") is True
    )
    transition_work_type = str(transition.get("prepared_work_type") or "")
    prepared = (
        transition_work_type
        if transition_authorized and transition_work_type in CANONICAL_GOVERNED_WORK_TYPES
        else requested
    )
    artifact = {
        "artifact_type": "PLATFORM_CORE_PREPARED_WORK_TYPE_RESOLUTION_V1",
        "runtime_version": PLATFORM_CORE_PREPARED_WORK_TYPE_RESOLUTION_VERSION,
        "resolution_authority": "PLATFORM_CORE",
        "prepared_work_type_source": (
            "AUTHORIZED_GOVERNED_WORK_TYPE_TRANSITION"
            if prepared != requested
            else "REQUESTED_WORK_TYPE_METADATA"
        ),
        "requested_work_type": requested,
        "prepared_work_type": prepared,
        "requested_work_type_source": metadata.get("work_type_source"),
        "requested_work_type_source_text": metadata.get("work_type_source_text"),
        "runtime_prompt_work_type_signal": deepcopy(prompt_signal),
        "runtime_prompt_wording_changes_prepared_work_type": False,
        "governed_work_type_transition_authorized": transition_authorized,
        "governed_work_type_transition": deepcopy(transition) if transition else None,
        "work_type_change_allowed": transition_authorized,
        "human_authorization_required_for_work_type_change": prepared != requested,
        "human_interface_authority": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def prepared_work_type_for_runtime_prompt(prompt: str, *, requested_work_type: str) -> str:
    """Compatibility projection for callers that need the prepared work type."""

    return str(
        resolve_prepared_work_type(
            requested_work_type=requested_work_type,
            canonical_runtime_prompt=prompt,
        )["prepared_work_type"]
    )


def inferred_work_type_from_runtime_prompt(prompt: str) -> str:
    """Return evidence-only runtime prompt signal for diagnostic callers."""

    signal = runtime_prompt_work_type_signal(prompt)["runtime_prompt_work_type_signal"]
    return "IMPLEMENTATION" if signal == "IMPLEMENTATION" else "UNSPECIFIED"


def _legacy_prepared_work_type_for_runtime_prompt(prompt: str, *, requested_work_type: str) -> str:
    """Legacy prompt-text classifier retained only for source trace comparison."""

    lowered = " ".join(require_string(prompt, "prompt").lower().split())
    implementation_markers = (
        "implement ",
        "implement as a governed development workflow",
        "implement as a native development governance workflow",
    )
    if lowered.startswith(("implement ", "add ", "build ", "create ", "fix ", "repair ", "update ")):
        return "IMPLEMENTATION"
    if any(marker in lowered for marker in implementation_markers):
        return "IMPLEMENTATION"
    if requested_work_type in CANONICAL_GOVERNED_WORK_TYPES:
        return requested_work_type
    return "IMPLEMENTATION"


def work_type_conflict_reason(
    *,
    requested_work_type: str,
    prepared_work_type: str,
    mutation_allowed: bool,
    runtime_implementation: bool,
) -> str:
    if prepared_work_type != requested_work_type:
        return (
            f"Prepared work type {prepared_work_type} does not match requested work type "
            f"{requested_work_type}."
        )
    if not mutation_allowed:
        return f"Requested work type {requested_work_type} does not allow mutation."
    if not runtime_implementation:
        return f"Requested work type {requested_work_type} does not allow runtime implementation."
    return "Work-type preservation guard blocked runtime continuation."


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
    clarification_required_after_sufficiency = (
        clarification_plan.get("clarification_required_after_sufficiency") is True
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
    elif intent.get("clarification_required") is True and clarification_required_after_sufficiency:
        response_mode = "CLARIFICATION"
        headline = "I need one clarification before governed execution."
        explanation = _conversation_explanation_for_clarification(prompt, intent)
        if _reuse_request_detected(lowered):
            headline = "I checked for reusable project capability evidence."
        elif _architecture_question_detected(lowered):
            headline = "I can help place this architecturally."
        questions = _clarification_questions_from_plan(clarification_plan)
        next_step = "Answer the question with the smallest useful detail."
    elif intent.get("work_type_conflict_detected") is True or (
        intent.get("work_type") in NON_MUTATING_GOVERNED_WORK_TYPES
        and not clarification_required_after_sufficiency
    ):
        response_mode = "INFORMATIONAL"
        headline = f"I preserved this as {intent.get('work_type')} work."
        explanation = (
            "Platform Core preserved the requested work type and blocked certified runtime "
            "implementation because this work type is non-mutating."
        )
        next_step = "Submit an explicit implementation work type only if you want runtime implementation."
    elif _reuse_request_detected(lowered) and clarification_required_after_sufficiency:
        response_mode = "CLARIFICATION"
        headline = "I checked for reusable project capability evidence."
        explanation = (
            "Reuse decisions come from deterministic workspace and governance evidence. "
            "I inferred candidate targets first and will only ask if the goal still has more than one safe reading."
        )
        questions = _clarification_questions_from_plan(clarification_plan)
        next_step = "Choose the goal outcome or confirm the inferred target."
    elif _architecture_question_detected(lowered) and clarification_required_after_sufficiency:
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


def development_intent_with_context_sufficiency(
    *,
    development_intent: dict[str, Any],
    conversation_experience: dict[str, Any],
) -> dict[str, Any]:
    """Project first-pass sufficiency into the returned intent artifact."""

    intent = deepcopy(development_intent)
    conversation = conversation_experience if isinstance(conversation_experience, dict) else {}
    plan = conversation.get("deterministic_clarification_plan")
    if not isinstance(plan, dict):
        return intent
    sufficiency = plan.get("clarification_context_sufficiency_evaluation")
    if not isinstance(sufficiency, dict):
        return intent
    clarification_required_before = intent.get("clarification_required") is True
    slot_sufficiency_requires_clarification = (
        sufficiency.get("clarification_required_after_sufficiency") is True
    )
    active_clarification_still_required = (
        intent.get("clarification_completed") is False
        and intent.get("clarification_continuity_status") == "CLARIFICATION_STILL_REQUIRED"
    )
    clarification_required_after = (
        slot_sufficiency_requires_clarification or active_clarification_still_required
    )
    intent["clarification_context_sufficiency_version"] = (
        PLATFORM_CORE_CLARIFICATION_CONTEXT_SUFFICIENCY_VERSION
    )
    intent["clarification_required_before_context_sufficiency"] = clarification_required_before
    intent["clarification_required_after_context_sufficiency"] = clarification_required_after
    intent["clarification_required_after_slot_sufficiency"] = (
        slot_sufficiency_requires_clarification
    )
    intent["active_clarification_still_required_after_context_sufficiency"] = (
        active_clarification_still_required
    )
    intent["clarification_context_sufficiency_evaluation"] = deepcopy(sufficiency)
    intent["candidate_missing_semantic_slots"] = deepcopy(
        plan.get("candidate_missing_semantic_slots") or []
    )
    intent["remaining_missing_semantic_slots"] = deepcopy(
        sufficiency.get("remaining_missing_slots") or []
    )
    intent["satisfied_semantic_slots_from_context"] = unique_strings(
        sufficiency.get("satisfied_semantic_slots")
    )
    intent["clarification_suppressed_by_context_sufficiency"] = (
        clarification_required_before and not clarification_required_after
    )
    if clarification_required_before and not clarification_required_after:
        intent["clarification_required"] = False
        intent["clarification_reason_before_context_sufficiency"] = intent.get(
            "clarification_reason"
        )
        intent["clarification_reason"] = None
    read_only_work_binding_admissible = read_only_work_binding_admissible_for_intent(
        requested_work_type=str(intent.get("requested_work_type") or ""),
        prepared_work_type=str(intent.get("prepared_work_type") or ""),
        clarification_required=intent.get("clarification_required") is True,
        work_type_conflict_detected=intent.get("work_type_conflict_detected") is True,
    )
    intent["read_only_work_binding_version"] = PLATFORM_CORE_READ_ONLY_WORK_BINDING_VERSION
    intent["read_only_work_binding_admissible"] = read_only_work_binding_admissible
    intent["read_only_work_binding_status"] = (
        GOVERNED_READ_ONLY_WORK_BOUND
        if read_only_work_binding_admissible
        else GOVERNED_READ_ONLY_WORK_NOT_REQUIRED
    )
    intent["read_only_work_result_required"] = read_only_work_binding_admissible
    intent["artifact_hash"] = replay_hash(intent)
    return intent


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
        "clarification_context_sufficiency_version": (
            PLATFORM_CORE_CLARIFICATION_CONTEXT_SUFFICIENCY_VERSION
        ),
        "clarification_context_sufficiency_evaluation": deepcopy(
            clarification_plan.get("clarification_context_sufficiency_evaluation")
        ),
        "clarification_required_after_sufficiency": clarification_plan.get(
            "clarification_required_after_sufficiency"
        ) is True,
        "satisfied_semantic_slots_from_context": unique_strings(
            clarification_plan.get("satisfied_semantic_slots_from_context")
        ),
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
        "work_type_preservation_version": development_intent.get("work_type_preservation_version"),
        "prepared_work_type_resolution_version": development_intent.get(
            "prepared_work_type_resolution_version"
        ),
        "governed_work_type_metadata": deepcopy(development_intent.get("governed_work_type_metadata")),
        "prepared_work_type_resolution": deepcopy(
            development_intent.get("prepared_work_type_resolution")
        ),
        "runtime_prompt_work_type_signal": deepcopy(
            development_intent.get("runtime_prompt_work_type_signal")
        ),
        "requested_work_type": development_intent.get("requested_work_type"),
        "work_type": development_intent.get("work_type"),
        "prepared_work_type": development_intent.get("prepared_work_type"),
        "work_type_source": development_intent.get("work_type_source"),
        "work_type_source_text": development_intent.get("work_type_source_text"),
        "mutation_allowed": development_intent.get("mutation_allowed"),
        "runtime_implementation": development_intent.get("runtime_implementation"),
        "work_type_change_allowed": development_intent.get("work_type_change_allowed"),
        "work_type_conflict_detected": development_intent.get("work_type_conflict_detected"),
        "work_type_conflict_reason": development_intent.get("work_type_conflict_reason"),
        "knowledge_reuse_classification_is_work_type": False,
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
    work_type = str(development_intent.get("work_type") or "IMPLEMENTATION")
    prepared_work_type = str(development_intent.get("prepared_work_type") or work_type)
    return {
        "summary_type": (
            "GOVERNED_IMPLEMENTATION_SUMMARY"
            if work_type == "IMPLEMENTATION"
            else "GOVERNED_WORK_TYPE_PRESERVATION_SUMMARY"
        ),
        "summary_authority": "PLATFORM_CORE",
        "summary_title": (
            "Governed implementation summary"
            if work_type == "IMPLEMENTATION"
            else f"Governed {work_type} preservation summary"
        ),
        "original_request": development_intent.get("raw_prompt") or message,
        "original_message": development_intent.get("raw_prompt") or message,
        "canonical_runtime_prompt": development_intent.get("canonical_runtime_prompt") or message,
        "refined_message": development_intent.get("canonical_runtime_prompt") or message,
        "goal_mapping": deepcopy(development_intent.get("goal_mapping")),
        "work_type_preservation_version": development_intent.get("work_type_preservation_version"),
        "prepared_work_type_resolution_version": development_intent.get(
            "prepared_work_type_resolution_version"
        ),
        "prepared_work_type_resolution": deepcopy(
            development_intent.get("prepared_work_type_resolution")
        ),
        "runtime_prompt_work_type_signal": deepcopy(
            development_intent.get("runtime_prompt_work_type_signal")
        ),
        "requested_work_type": work_type,
        "work_type": work_type,
        "prepared_work_type": prepared_work_type,
        "work_type_source": development_intent.get("work_type_source"),
        "work_type_source_text": development_intent.get("work_type_source_text"),
        "mutation_allowed": development_intent.get("mutation_allowed") is True,
        "runtime_implementation": development_intent.get("runtime_implementation") is True,
        "work_type_change_allowed": development_intent.get("work_type_change_allowed") is True,
        "work_type_conflict_detected": development_intent.get("work_type_conflict_detected") is True,
        "work_type_conflict_reason": development_intent.get("work_type_conflict_reason"),
        "knowledge_reuse_classification_is_work_type": False,
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
    work_type_reason = development_intent.get("work_type_conflict_reason")
    return {
        "response_type": "FAIL_CLOSED_EXPLANATION",
        "response_authority": "PLATFORM_CORE",
        "response_title": "No governed implementation summary was produced.",
        "reason": work_type_reason or development_intent.get("clarification_reason"),
        "fail_closed_explanation": explanation,
        "recommended_next_user_action": next_step,
        "requested_work_type": development_intent.get("requested_work_type"),
        "work_type": development_intent.get("work_type"),
        "prepared_work_type": development_intent.get("prepared_work_type"),
        "prepared_work_type_resolution_version": development_intent.get(
            "prepared_work_type_resolution_version"
        ),
        "prepared_work_type_resolution": deepcopy(
            development_intent.get("prepared_work_type_resolution")
        ),
        "runtime_prompt_work_type_signal": deepcopy(
            development_intent.get("runtime_prompt_work_type_signal")
        ),
        "mutation_allowed": development_intent.get("mutation_allowed") is True,
        "runtime_implementation": development_intent.get("runtime_implementation") is True,
        "work_type_conflict_detected": development_intent.get("work_type_conflict_detected") is True,
        "work_type_conflict_reason": work_type_reason,
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
    if reason == "clarification answer did not satisfy active semantic slot":
        explainability = intent.get("clarification_decision_explainability")
        if isinstance(explainability, dict) and explainability.get("user_explanation"):
            return str(explainability["user_explanation"])
        return "The answer did not yet satisfy the active semantic slot, so deterministic continuation remains blocked."
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
    candidate_missing_slots = (
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
    sufficiency_evaluation = clarification_context_sufficiency_evaluation(
        message=prompt,
        candidate_missing_slots=candidate_missing_slots,
        workspace_state=workspace_state,
        guidance=guidance,
        knowledge_reuse=knowledge_reuse,
        development_intent=development_intent,
    )
    missing_slots = sufficiency_evaluation["remaining_missing_slots"]
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
            "CONTEXT_SUFFICIENCY_EVALUATION",
            "DETERMINISTIC_SLOT_SATISFACTION",
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
            "canonical_semantic_artifact_available": isinstance(
                development_intent.get("project_objective_inference"), dict
            ),
            "project_objective_inference_hash": (
                development_intent.get("project_objective_inference_hash")
            ),
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
        "candidate_missing_semantic_slots": deepcopy(candidate_missing_slots),
        "clarification_context_sufficiency_evaluation": deepcopy(sufficiency_evaluation),
        "clarification_required_after_sufficiency": sufficiency_evaluation[
            "clarification_required_after_sufficiency"
        ],
        "satisfied_semantic_slots_from_context": sufficiency_evaluation[
            "satisfied_semantic_slots"
        ],
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


def clarification_context_sufficiency_evaluation(
    *,
    message: str,
    candidate_missing_slots: list[dict[str, Any]],
    workspace_state: dict[str, Any] | None,
    guidance: dict[str, Any],
    knowledge_reuse: dict[str, Any],
    development_intent: dict[str, Any],
) -> dict[str, Any]:
    """Remove clarification slots already satisfied by deterministic context."""

    prompt = " ".join(require_string(message, "message").split())
    lowered_prompt = prompt.lower()
    clarification_first_requested = any(
        term in lowered_prompt
        for term in (
            "need clarification",
            "needs clarification",
            "ask me for clarification",
            "ask for clarification",
            "clarify before",
        )
    )
    remaining_slots: list[dict[str, Any]] = []
    satisfied_slots: list[str] = []
    satisfied_from_original_request: list[dict[str, Any]] = []
    objective_inference = (
        development_intent.get("project_objective_inference")
        if isinstance(development_intent.get("project_objective_inference"), dict)
        else {}
    )
    objective_satisfied_slots = set(
        unique_strings(objective_inference.get("satisfied_semantic_slots"))
        if objective_inference.get("objective_sufficient") is True
        else []
    )
    unresolved_slots: list[dict[str, Any]] = []
    for slot in _dedupe_missing_slots(candidate_missing_slots):
        slot_id = str(slot.get("slot_id") or "")
        accepted = _accepted_semantic_requirements(reply=prompt, slot_id=slot_id)
        required = _required_semantic_requirements(slot_id)
        satisfied_by_objective = (
            not clarification_first_requested and slot_id in objective_satisfied_slots
        )
        satisfied = satisfied_by_objective or (
            not clarification_first_requested
            and bool(required)
            and all(requirement in accepted for requirement in required)
        )
        unresolved = [] if satisfied else [
            requirement for requirement in required if requirement not in accepted
        ]
        if satisfied:
            satisfied_slots.append(slot_id)
            satisfied_from_original_request.append(
                {
                    "slot_id": slot_id,
                    "source": "ORIGINAL_REQUEST",
                    "accepted_semantic_requirements": accepted,
                    "required_semantic_requirements": required,
                    "project_objective_inference_satisfied": satisfied_by_objective,
                    "project_objective_inference_hash": objective_inference.get("artifact_hash"),
                    "source_hash": replay_hash(prompt),
                }
            )
        else:
            unresolved_slots.append(
                {
                    "slot_id": slot_id,
                    "unresolved_semantic_requirements": unresolved
                    or [_clarification_slot_missing_information(slot_id)],
                    "accepted_semantic_requirements": accepted,
                    "required_semantic_requirements": required,
                }
            )
            remaining_slots.append(slot)
    artifact = {
        "artifact_type": "PLATFORM_CORE_CLARIFICATION_CONTEXT_SUFFICIENCY_EVALUATION_V1",
        "runtime_version": PLATFORM_CORE_CLARIFICATION_CONTEXT_SUFFICIENCY_VERSION,
        "platform_core_project_services_version": PLATFORM_CORE_PROJECT_SERVICES_VERSION,
        "sufficiency_authority": "PLATFORM_CORE",
        "evaluation_mode": "DETERMINISTIC_FIRST_PASS_CONTEXT_SUFFICIENCY",
        "input_sequence": [
            "ORIGINAL_REQUEST",
            "WORKSPACE_CONTEXT",
            "PROJECT_GUIDANCE",
            "PLATFORM_KNOWLEDGE_REUSE",
            "DEVELOPMENT_INTENT_RESOLUTION",
            "CANDIDATE_MISSING_SLOTS",
            "DETERMINISTIC_SLOT_SATISFACTION",
            "REMAINING_MISSING_SLOTS",
        ],
        "original_request_hash": replay_hash(prompt),
        "clarification_first_requested": clarification_first_requested,
        "workspace_context_available": isinstance(workspace_state, dict),
        "workspace_state_hash": workspace_state.get("artifact_hash") if isinstance(workspace_state, dict) else None,
        "project_guidance_hash": replay_hash(guidance),
        "knowledge_reuse_hash": replay_hash(knowledge_reuse),
        "development_intent_hash": development_intent.get("artifact_hash"),
        "project_objective_inference_available": bool(objective_inference),
        "project_objective_inference_hash": objective_inference.get("artifact_hash"),
        "project_objective_sufficient": objective_inference.get("objective_sufficient") is True,
        "candidate_missing_slots": deepcopy(_dedupe_missing_slots(candidate_missing_slots)),
        "satisfied_from_original_request": satisfied_from_original_request,
        "satisfied_from_workspace_context": [],
        "satisfied_from_previous_clarification": [],
        "satisfied_semantic_slots": unique_strings(satisfied_slots),
        "unresolved_slot_requirements": unresolved_slots,
        "remaining_missing_slots": _dedupe_missing_slots(remaining_slots),
        "clarification_required_after_sufficiency": bool(remaining_slots),
        "human_interface_authority": False,
        "platform_core_owns_sufficiency": True,
        "llm_reasoning_used": False,
        "probabilistic_matching_used": False,
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
    objective_inference = (
        development_intent.get("project_objective_inference")
        if isinstance(development_intent.get("project_objective_inference"), dict)
        else {}
    )
    reason = str(development_intent.get("clarification_reason") or "")
    if reason == "continuation request requires deterministic workspace state":
        slots.append(_missing_slot("continuation_reference", 100, "No replay-backed active objective was available."))
    if reason == "clarification answer did not satisfy active semantic slot":
        active_slot = str(development_intent.get("active_clarification_open_slot") or "")
        missing = str(
            development_intent.get("active_clarification_missing_information")
            or "remaining semantic detail"
        )
        if active_slot:
            slots.append(
                {
                    **_missing_slot(active_slot, 101, f"Clarification answer still lacks {missing}."),
                    "followup_after_insufficient_answer": True,
                    "missing_information": missing,
                    "original_question": development_intent.get(
                        "active_clarification_original_question"
                    ),
                }
            )
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
        non_mutating_objective = str(development_intent.get("requested_work_type") or "") in (
            NON_MUTATING_GOVERNED_WORK_TYPES
        )
        objective_outcomes = set(
            objective_inference.get("requested_outcomes")
            if isinstance(objective_inference.get("requested_outcomes"), list)
            else []
        )
        inspection_objective = bool(
            objective_outcomes.intersection({"audit_or_analysis", "existing_capability_discovery"})
        )
        if not (non_mutating_objective and inspection_objective):
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
        if slot.get("followup_after_insufficient_answer") is True:
            return "I still need whether this extends the active objective or starts a new one. State one of those choices."
        return "Are you extending the current governed development objective or starting a new one?"
    if slot_id == "capability_target_choice":
        if slot.get("followup_after_insufficient_answer") is True:
            return "I still need the governed capability to continue. Name the capability target."
        return "Which inferred governed capability should this continue?"
    if slot_id == "capability_target":
        if slot.get("followup_after_insufficient_answer") is True:
            return "I still need the target governed capability or outcome. Name the runtime, replay, clarification, governance, or interface behavior to improve."
        return "What outcome should improve runtime, clarification quality, replay behavior, or another governed capability?"
    if slot_id == "desired_outcome":
        if slot.get("followup_after_insufficient_answer") is True:
            return f"I still need the outcome the {display} improvement should produce. State the outcome in one sentence."
        return f"What outcome should the {display} improvement produce?"
    if slot_id == "architecture_outcome":
        if slot.get("followup_after_insufficient_answer") is True:
            return f"I still need the architecture outcome for {display}. State the reusable behavior or interface outcome it should enable."
        return f"What outcome should the {display} architecture decision enable?"
    if slot_id == "architecture_subject":
        if slot.get("followup_after_insufficient_answer") is True:
            return "I still need the behavior or artifact to place architecturally and the outcome it should enable."
        return "What user-visible behavior or artifact should be placed architecturally? Include the outcome it should enable."
    if slot_id == "reuse_delta":
        if slot.get("followup_after_insufficient_answer") is True:
            return f"I still need the new outcome or delta for the existing {display} evidence."
        artifacts = knowledge_reuse.get("relevant_certified_artifacts")
        if isinstance(artifacts, list) and artifacts:
            return f"What new outcome should be added to the existing {display} evidence?"
        return f"What outcome should change in the existing {display} capability?"
    if slot_id == "reuse_goal":
        if slot.get("followup_after_insufficient_answer") is True:
            return "I still need the user-visible outcome to check against existing governed work."
        return "What user-visible outcome should I check against existing governed work?"
    if slot_id == "implementation_specificity":
        if slot.get("followup_after_insufficient_answer") is True:
            return "I still need the capability or runtime behavior this implementation should change."
        return "What should be improved or built? Name the capability or runtime behavior this implementation should change."
    if slot_id == "active_objective_delta":
        objective = str(active_objective or "active objective")
        if slot.get("followup_after_insufficient_answer") is True:
            return f"I still need the next change to {objective}. State the concrete change."
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
    completed = workspace_state.get("completed_clarifications")
    if isinstance(completed, list):
        answer_ids: list[str] = []
        for item in completed:
            if isinstance(item, dict):
                answer_ids.extend(unique_strings(item.get("completed_clarification_question_ids")))
        return unique_strings(answer_ids)
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
