"""Conversation PPP routing with unified resource selection for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.provider.provider_adapter import ProviderAdapter
from aigol.provider.provider_registry import ProviderRegistry
from aigol.runtime.conversation_native_development_context_integration import (
    CONVERSATION_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATED,
    run_conversation_native_development_context_integration,
)
from aigol.runtime.conversation_ppp_routing_integration import (
    _is_high_risk_domain,
    _milestone_type,
    _normalize_canonical_semantic_lineage,
    _ppp_semantic_annotation_artifact,
    _repair_failed_production,
    _seed_proposal,
    _validate_and_handoff,
)
from aigol.runtime.conversation_to_implementation_handoff_runtime import (
    IMPLEMENTATION_HANDOFF_CREATED,
    create_conversation_to_implementation_handoff,
)
from aigol.runtime.development_proposal_contract_runtime import DEVELOPMENT_PROPOSAL_CONTRACT_VALIDATED
from aigol.runtime.domain_and_worker_resolution_registry import (
    RESOLUTION_SUCCEEDED,
    resolve_domain_worker_milestone,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_necessity_policy_runtime import PROVIDER_REQUIRED, classify_provider_necessity
from aigol.runtime.provider_proposal_production_runtime import (
    PROVIDER_PROPOSAL_PRODUCED,
    produce_provider_development_proposal,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.unified_resource_selection_ppp_integration import (
    PPP_PROVIDER_PROPOSAL_READY,
    PPP_WORKER_HANDOFF_REFERENCE_READY,
    RESOURCE_PPP_INTEGRATED,
    integrate_resource_selection_with_ppp,
)
from aigol.runtime.unified_resource_selection_runtime import (
    PROVIDER_ROLE,
    WORKER_ROLE,
    select_unified_resource,
)


CONVERSATION_PPP_RESOURCE_SELECTION_ROUTING_VERSION = "CONVERSATION_PPP_RESOURCE_SELECTION_ROUTING_V1"
CONVERSATION_RESOURCE_PPP_HANDOFF_CREATED = "CONVERSATION_RESOURCE_PPP_HANDOFF_CREATED"
CONVERSATION_RESOURCE_PPP_WORKER_HANDOFF_REFERENCE_READY = "CONVERSATION_RESOURCE_PPP_WORKER_HANDOFF_REFERENCE_READY"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "conversation_resource_ppp_route_recorded",
    "conversation_resource_ppp_route_returned",
)

EXPLICIT_RESOURCE_ROLES = {
    "OPENAI_PROVIDER_ROLE": ("OPENAI", PROVIDER_ROLE, "PROPOSAL_GENERATION", "TRADING", False),
    "ANTHROPIC_PROVIDER_ROLE": ("ANTHROPIC", PROVIDER_ROLE, "PROPOSAL_GENERATION", "TRADING", False),
    "CODEX_PROVIDER_ROLE": ("CODEX", PROVIDER_ROLE, "IMPLEMENTATION_ASSISTANCE", "NATIVE_DEVELOPMENT", False),
    "CODEX_WORKER_ROLE": ("CODEX", WORKER_ROLE, "IMPLEMENTATION_ASSISTANCE", "NATIVE_DEVELOPMENT", True),
    "CLAUDE_CODE_PROVIDER_ROLE": ("CLAUDE_CODE", PROVIDER_ROLE, "IMPLEMENTATION_ASSISTANCE", "NATIVE_DEVELOPMENT", False),
    "CLAUDE_CODE_WORKER_ROLE": ("CLAUDE_CODE", WORKER_ROLE, "IMPLEMENTATION_ASSISTANCE", "NATIVE_DEVELOPMENT", True),
}


def run_conversation_ppp_resource_selection_routing(
    *,
    prompt_id: str,
    human_prompt: str,
    provider_id: str,
    created_at: str,
    replay_dir: str | Path,
    registry: ProviderRegistry,
    adapter: ProviderAdapter,
    governance_root: str | Path = "governance",
    explicit_resource_role: str | None = None,
    resource_registry: dict[str, Any] | None = None,
    session_id: str | None = None,
    turn_id: str | None = None,
    current_chain_id: str | None = None,
    latest_chain_id: str | None = None,
    canonical_semantic_lineage: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Route a conversation native-development prompt through Resource Selection and PPP."""

    root = Path(replay_dir)
    route_replay = root / "conversation_resource_ppp_route"
    try:
        _ensure_replay_available(route_replay)
        conversation = run_conversation_native_development_context_integration(
            prompt_id=prompt_id,
            human_prompt=human_prompt,
            created_at=created_at,
            replay_dir=root / "conversation_native_development",
            governance_root=governance_root,
            session_id=session_id,
            turn_id=turn_id,
            current_chain_id=current_chain_id,
            latest_chain_id=latest_chain_id,
        )
        if conversation.get("response_status") != CONVERSATION_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATED:
            raise FailClosedRuntimeError(conversation.get("failure_reason") or "conversation resource PPP cognition failed closed")
        context = conversation["development_context_assembly"]["development_context_assembly_artifact"]
        intake = conversation["native_development_task_intake"]["native_development_task_intake_artifact"]
        canonical_chain_id = conversation["canonical_chain_id"]
        resolution = resolve_domain_worker_milestone(
            resolution_id=f"{prompt_id}:RESOURCE-PPP-DOMAIN-WORKER-RESOLUTION",
            domain_id=context["requested_domain"],
            worker_family_id=context["requested_worker_family"],
            milestone_type=_milestone_type(intake),
            created_at=created_at,
            replay_dir=root / "domain_worker_resolution",
        )
        if resolution.get("resolution_status") != RESOLUTION_SUCCEEDED:
            raise FailClosedRuntimeError(resolution.get("failure_reason") or "conversation resource PPP resolution failed closed")
        resolution_artifact = resolution["domain_worker_resolution_artifact"]
        provider_policy = classify_provider_necessity(
            policy_decision_id=f"{prompt_id}:RESOURCE-PPP-PROVIDER-NECESSITY",
            workflow_type="NATIVE_DEVELOPMENT",
            task_kind=resolution_artifact["milestone_type"],
            created_at=created_at,
            replay_dir=root / "provider_necessity",
        )
        if provider_policy.get("necessity_classification") != PROVIDER_REQUIRED:
            raise FailClosedRuntimeError("conversation resource PPP failed closed: provider proposal is not required")
        selection_options = _resource_selection_options(explicit_resource_role)
        resource_selection = select_unified_resource(
            selection_id=f"{prompt_id}:RESOURCE-SELECTION",
            workflow_type="NATIVE_DEVELOPMENT",
            required_capability=selection_options["required_capability"],
            requested_role_type=selection_options["requested_role_type"],
            domain_id=selection_options["domain_id"],
            provider_necessity_classification=provider_policy["necessity_classification"]
            if selection_options["requested_role_type"] == PROVIDER_ROLE
            else None,
            worker_authorization_required=selection_options["worker_authorization_required"],
            preferred_resource_id=selection_options["preferred_resource_id"],
            context_assembly_output=context,
            registry=resource_registry,
            created_at=created_at,
            replay_dir=root / "resource_selection",
        )
        if resource_selection.get("selection_status") != "RESOURCE_SELECTION_SUCCEEDED":
            raise FailClosedRuntimeError(resource_selection.get("failure_reason") or "conversation resource selection failed closed")
        selected = resource_selection["resource_selection_artifact"]
        resource_ppp = integrate_resource_selection_with_ppp(
            integration_id=f"{prompt_id}:RESOURCE-PPP-INTEGRATION",
            resource_selection_artifact=selected,
            context_assembly_artifact=context,
            ppp_stage="PROPOSAL_PRODUCTION"
            if selected["selected_role_type"] == PROVIDER_ROLE
            else "IMPLEMENTATION_HANDOFF",
            created_at=created_at,
            replay_dir=root / "resource_ppp_integration",
        )
        if resource_ppp.get("integration_status") != RESOURCE_PPP_INTEGRATED:
            raise FailClosedRuntimeError(resource_ppp.get("failure_reason") or "conversation resource PPP integration failed closed")
        ppp_semantic_annotation = _resource_ppp_semantic_annotation_artifact(
            annotation_id=f"{prompt_id}:G2-09-RESOURCE-PPP-SEMANTIC-ANNOTATION",
            canonical_semantic_lineage=canonical_semantic_lineage,
            context=context,
            resolution_artifact=resolution_artifact,
            provider_policy_artifact=provider_policy["provider_necessity_policy_artifact"],
            resource_selection_artifact=selected,
            resource_ppp_artifact=resource_ppp["resource_ppp_integration_artifact"],
            created_at=created_at,
        )
        if resource_ppp["ppp_resource_status"] == PPP_WORKER_HANDOFF_REFERENCE_READY:
            route = _route_artifact(
                prompt_id=prompt_id,
                route_status=CONVERSATION_RESOURCE_PPP_WORKER_HANDOFF_REFERENCE_READY,
                conversation=conversation,
                resolution=resolution,
                provider_policy=provider_policy,
                resource_selection=resource_selection,
                resource_ppp=resource_ppp,
                production=None,
                repair=None,
                final_validation=None,
                final_handoff=None,
                approval_required=_is_high_risk_domain(resolution_artifact["domain_id"]),
                clarification_required=False,
                ppp_semantic_annotation=ppp_semantic_annotation,
                created_at=created_at,
                failure_reason=None,
            )
        else:
            if resource_ppp["ppp_resource_status"] != PPP_PROVIDER_PROPOSAL_READY:
                raise FailClosedRuntimeError("conversation resource PPP failed closed: resource is not PPP-ready")
            if provider_id != selected["selected_resource_id"]:
                raise FailClosedRuntimeError("conversation resource PPP failed closed: selected provider resource mismatch")
            request_handoff = _create_request_handoff(
                prompt_id=prompt_id,
                context=context,
                intake=intake,
                resolution_artifact=resolution_artifact,
                provider_policy_artifact=provider_policy["provider_necessity_policy_artifact"],
                created_at=created_at,
                replay_root=root,
            )
            production = produce_provider_development_proposal(
                production_id=f"{prompt_id}:RESOURCE-PPP-PROVIDER-PROPOSAL-PRODUCTION",
                provider_id=provider_id,
                handoff_artifact=request_handoff["implementation_handoff_artifact"],
                context_assembly_artifact=context,
                registry_resolution_artifact=resolution_artifact,
                provider_necessity_policy_artifact=provider_policy["provider_necessity_policy_artifact"],
                canonical_chain_id=canonical_chain_id,
                created_at=created_at,
                registry=registry,
                adapter=adapter,
                replay_dir=root / "provider_proposal_production",
            )
            repair = None
            final_validation = None
            final_handoff = None
            route_status = FAILED_CLOSED
            approval_required = False
            clarification_required = False
            if production.get("production_status") == PROVIDER_PROPOSAL_PRODUCED:
                final_validation, final_handoff = _validate_and_handoff(
                    prompt_id=prompt_id,
                    proposal=production["development_proposal_artifact"],
                    context=context,
                    resolution=resolution_artifact,
                    provider_policy=provider_policy["provider_necessity_policy_artifact"],
                    created_at=created_at,
                    replay_root=root,
                )
                route_status = CONVERSATION_RESOURCE_PPP_HANDOFF_CREATED
                approval_required = _is_high_risk_domain(resolution_artifact["domain_id"])
            else:
                repair = _repair_failed_production(
                    prompt_id=prompt_id,
                    production=production,
                    context=context,
                    resolution=resolution_artifact,
                    provider_policy=provider_policy["provider_necessity_policy_artifact"],
                    canonical_chain_id=canonical_chain_id,
                    provider_id=provider_id,
                    created_at=created_at,
                    registry=registry,
                    adapter=adapter,
                    replay_root=root,
                )
                route_status = repair["retry_status"]
                approval_required = repair.get("approval_required", False)
                clarification_required = repair.get("clarification_required", False)
            route = _route_artifact(
                prompt_id=prompt_id,
                route_status=route_status,
                conversation=conversation,
                resolution=resolution,
                provider_policy=provider_policy,
                resource_selection=resource_selection,
                resource_ppp=resource_ppp,
                production=production,
                repair=repair,
                final_validation=final_validation,
                final_handoff=final_handoff,
                approval_required=approval_required,
                clarification_required=clarification_required,
                ppp_semantic_annotation=ppp_semantic_annotation,
                created_at=created_at,
                failure_reason=None,
            )
        returned = _returned_artifact(route)
        _persist_step(route_replay, 0, REPLAY_STEPS[0], route)
        _persist_step(route_replay, 1, REPLAY_STEPS[1], returned)
        return _capture(route, returned, route_replay)
    except Exception as exc:
        route = _failed_route_artifact(
            prompt_id=prompt_id,
            created_at=created_at,
            canonical_chain_id=locals().get("canonical_chain_id"),
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(route)
        _persist_failure_if_possible(route_replay, 0, REPLAY_STEPS[0], route)
        _persist_failure_if_possible(route_replay, 1, REPLAY_STEPS[1], returned)
        return _capture(route, returned, route_replay)


def reconstruct_conversation_ppp_resource_selection_routing_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct conversation resource-selection PPP routing replay."""

    replay_path = Path(replay_dir) / "conversation_resource_ppp_route"
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("conversation resource PPP routing replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("conversation resource PPP routing replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "conversation resource PPP routing artifact")
        wrappers.append(wrapper)
    route = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("route_reference") != route["route_id"]:
        raise FailClosedRuntimeError("conversation resource PPP routing replay reference mismatch")
    if returned.get("route_hash") != route["artifact_hash"]:
        raise FailClosedRuntimeError("conversation resource PPP routing replay hash mismatch")
    return {
        "route_id": route["route_id"],
        "route_status": route["route_status"],
        "canonical_chain_id": route["canonical_chain_id"],
        "ppp_semantic_annotation_source": route.get("ppp_semantic_annotation_source"),
        "ppp_semantic_annotation_hash": route.get("ppp_semantic_annotation_hash"),
        "ppp_semantic_annotation_parity_status": route.get("ppp_semantic_annotation_parity_status"),
        "ppp_semantic_annotation_migration_batch_id": route.get("ppp_semantic_annotation_migration_batch_id"),
        "canonical_semantic_artifact_reference": route.get("canonical_semantic_artifact_reference"),
        "canonical_semantic_artifact_hash": route.get("canonical_semantic_artifact_hash"),
        "selected_resource_id": route["selected_resource_id"],
        "selected_resource_category": route["selected_resource_category"],
        "selected_role_type": route["selected_role_type"],
        "resource_ppp_status": route["resource_ppp_status"],
        "provider_proposal_production_status": route["provider_proposal_production_status"],
        "implementation_handoff_reference": route["implementation_handoff_reference"],
        "clarification_required": route["clarification_required"],
        "approval_required": route["approval_required"],
        "failure_reason": route["failure_reason"],
        "provider_invoked": route["provider_invoked"],
        "worker_invoked": False,
        "dispatch_requested": False,
        "execution_requested": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _resource_selection_options(explicit_resource_role: str | None) -> dict[str, Any]:
    if explicit_resource_role is None:
        return {
            "preferred_resource_id": None,
            "requested_role_type": PROVIDER_ROLE,
            "required_capability": "PROPOSAL_GENERATION",
            "domain_id": "TRADING",
            "worker_authorization_required": False,
        }
    key = explicit_resource_role.strip().upper().replace("-", "_").replace(" ", "_")
    if key not in EXPLICIT_RESOURCE_ROLES:
        raise FailClosedRuntimeError("conversation resource PPP failed closed: resource role ambiguous")
    resource_id, role, capability, domain, worker_auth = EXPLICIT_RESOURCE_ROLES[key]
    return {
        "preferred_resource_id": resource_id,
        "requested_role_type": role,
        "required_capability": capability,
        "domain_id": domain,
        "worker_authorization_required": worker_auth,
    }


def _create_request_handoff(
    *,
    prompt_id: str,
    context: dict[str, Any],
    intake: dict[str, Any],
    resolution_artifact: dict[str, Any],
    provider_policy_artifact: dict[str, Any],
    created_at: str,
    replay_root: Path,
) -> dict[str, Any]:
    seed_proposal = _seed_proposal(
        proposal_id=f"{prompt_id}:RESOURCE-PPP-SEED-PROPOSAL",
        context=context,
        resolution=resolution_artifact,
        intake=intake,
    )
    from aigol.runtime.development_proposal_contract_runtime import validate_development_proposal_contract

    seed_validation = validate_development_proposal_contract(
        contract_validation_id=f"{prompt_id}:RESOURCE-PPP-SEED-PROPOSAL-VALIDATION",
        proposal_artifact=seed_proposal,
        context_assembly_artifact=context,
        registry_resolution_artifact=resolution_artifact,
        created_at=created_at,
        replay_dir=replay_root / "seed_proposal_contract",
    )
    if seed_validation.get("validation_status") != DEVELOPMENT_PROPOSAL_CONTRACT_VALIDATED:
        raise FailClosedRuntimeError(seed_validation.get("failure_reason") or "conversation resource PPP seed proposal failed")
    handoff = create_conversation_to_implementation_handoff(
        handoff_id=f"{prompt_id}:RESOURCE-PPP-PROVIDER-REQUEST-HANDOFF",
        proposal_artifact=seed_proposal,
        proposal_contract_validation_artifact=seed_validation["development_proposal_contract_validation_artifact"],
        context_assembly_artifact=context,
        registry_resolution_artifact=resolution_artifact,
        provider_necessity_policy_artifact=provider_policy_artifact,
        created_at=created_at,
        replay_dir=replay_root / "provider_request_handoff",
    )
    if handoff.get("handoff_status") != IMPLEMENTATION_HANDOFF_CREATED:
        raise FailClosedRuntimeError(handoff.get("failure_reason") or "conversation resource PPP request handoff failed")
    return handoff


def _resource_ppp_semantic_annotation_artifact(
    *,
    annotation_id: str,
    canonical_semantic_lineage: dict[str, Any] | None,
    context: dict[str, Any],
    resolution_artifact: dict[str, Any],
    provider_policy_artifact: dict[str, Any],
    resource_selection_artifact: dict[str, Any],
    resource_ppp_artifact: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    annotation = _ppp_semantic_annotation_artifact(
        annotation_id=annotation_id,
        canonical_semantic_lineage=_normalize_canonical_semantic_lineage(canonical_semantic_lineage),
        context=context,
        resolution_artifact=resolution_artifact,
        provider_policy_artifact=provider_policy_artifact,
        created_at=created_at,
    )
    annotation["resource_selection_lineage"] = {
        "resource_selection_hash": resource_selection_artifact["artifact_hash"],
        "selected_resource_id": resource_selection_artifact["selected_resource_id"],
        "selected_role_type": resource_selection_artifact["selected_role_type"],
        "resource_ppp_integration_hash": resource_ppp_artifact["artifact_hash"],
    }
    annotation["semantic_parity_evidence"]["resource_selection_hash"] = resource_selection_artifact["artifact_hash"]
    annotation["semantic_parity_evidence"]["resource_ppp_integration_hash"] = resource_ppp_artifact["artifact_hash"]
    annotation["semantic_parity_evidence"]["parity_hash"] = replay_hash(annotation["semantic_parity_evidence"])
    annotation.pop("artifact_hash", None)
    annotation["artifact_hash"] = replay_hash(annotation)
    return annotation


def _route_artifact(
    *,
    prompt_id: str,
    route_status: str,
    conversation: dict[str, Any],
    resolution: dict[str, Any],
    provider_policy: dict[str, Any],
    resource_selection: dict[str, Any],
    resource_ppp: dict[str, Any],
    production: dict[str, Any] | None,
    repair: dict[str, Any] | None,
    final_validation: dict[str, Any] | None,
    final_handoff: dict[str, Any] | None,
    approval_required: bool,
    clarification_required: bool,
    ppp_semantic_annotation: dict[str, Any],
    created_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    resolution_artifact = resolution["domain_worker_resolution_artifact"]
    selection_artifact = resource_selection["resource_selection_artifact"]
    resource_ppp_artifact = resource_ppp["resource_ppp_integration_artifact"]
    handoff_artifact = final_handoff.get("implementation_handoff_artifact") if final_handoff else None
    artifact = {
        "artifact_type": "CONVERSATION_PPP_RESOURCE_SELECTION_ROUTING_ARTIFACT_V1",
        "runtime_version": CONVERSATION_PPP_RESOURCE_SELECTION_ROUTING_VERSION,
        "route_id": f"{prompt_id}:CONVERSATION-RESOURCE-PPP-ROUTE",
        "prompt_id": prompt_id,
        "route_status": route_status,
        "canonical_chain_id": conversation["canonical_chain_id"],
        "task_intake_reference": conversation["task_intake_reference"],
        "context_reference": conversation["context_assembly_reference"],
        "context_hash": conversation["context_hash"],
        "ppp_semantic_annotation_source": ppp_semantic_annotation["semantic_annotation_source"],
        "ppp_semantic_annotation_artifact": deepcopy(ppp_semantic_annotation),
        "ppp_semantic_annotation_hash": ppp_semantic_annotation["artifact_hash"],
        "ppp_semantic_annotation_parity_status": ppp_semantic_annotation["parity_status"],
        "ppp_semantic_annotation_migration_batch_id": ppp_semantic_annotation["migration_batch_id"],
        "canonical_semantic_artifact_reference": ppp_semantic_annotation.get("canonical_semantic_artifact_reference"),
        "canonical_semantic_artifact_hash": ppp_semantic_annotation.get("canonical_semantic_artifact_hash"),
        "domain_reference": resolution_artifact["domain_id"],
        "worker_reference": resolution_artifact["worker_family_id"],
        "milestone_reference": resolution_artifact["milestone_type"],
        "provider_necessity_classification": provider_policy["necessity_classification"],
        "resource_selection_reference": selection_artifact["selection_id"],
        "resource_selection_hash": selection_artifact["artifact_hash"],
        "selected_resource_id": selection_artifact["selected_resource_id"],
        "selected_resource_category": selection_artifact["selected_resource_category"],
        "selected_role_type": selection_artifact["selected_role_type"],
        "resource_ppp_integration_reference": resource_ppp_artifact["integration_id"],
        "resource_ppp_integration_hash": resource_ppp_artifact["artifact_hash"],
        "resource_ppp_status": resource_ppp["ppp_resource_status"],
        "capability_matches": resource_ppp["capability_matches"],
        "trust_matches": resource_ppp["trust_matches"],
        "authority_matches": resource_ppp["authority_matches"],
        "provider_proposal_production_status": production.get("production_status") if production else None,
        "provider_proposal_hash": production.get("proposal_hash") if production else None,
        "repair_retry_status": repair.get("retry_status") if repair else None,
        "repair_retry_hash": repair.get("provider_proposal_repair_retry_capture_hash") if repair else None,
        "final_validation_status": final_validation.get("validation_status") if final_validation else None,
        "implementation_handoff_reference": handoff_artifact.get("handoff_id") if handoff_artifact else None,
        "implementation_handoff_hash": handoff_artifact.get("artifact_hash") if handoff_artifact else None,
        "clarification_required": clarification_required,
        "approval_required": approval_required,
        "created_at": created_at,
        "proposal_only": True,
        "provider_invoked": bool(production and production.get("provider_invocation_status") == "PROVIDER_INVOKED"),
        "provider_authority": False,
        "aigol_governance_only": True,
        "human_final_authority": True,
        "worker_created": False,
        "domain_created": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "authorization_created": False,
        "governance_modified": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_route_artifact(*, prompt_id: str, created_at: str, canonical_chain_id: Any, failure_reason: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": "CONVERSATION_PPP_RESOURCE_SELECTION_ROUTING_ARTIFACT_V1",
        "runtime_version": CONVERSATION_PPP_RESOURCE_SELECTION_ROUTING_VERSION,
        "route_id": f"{prompt_id}:CONVERSATION-RESOURCE-PPP-ROUTE" if isinstance(prompt_id, str) else "INVALID_PROMPT:CONVERSATION-RESOURCE-PPP-ROUTE",
        "prompt_id": prompt_id if isinstance(prompt_id, str) else "INVALID_PROMPT",
        "route_status": FAILED_CLOSED,
        "canonical_chain_id": canonical_chain_id if isinstance(canonical_chain_id, str) else None,
        "task_intake_reference": None,
        "context_reference": None,
        "context_hash": None,
        "ppp_semantic_annotation_source": None,
        "ppp_semantic_annotation_artifact": None,
        "ppp_semantic_annotation_hash": None,
        "ppp_semantic_annotation_parity_status": None,
        "ppp_semantic_annotation_migration_batch_id": None,
        "canonical_semantic_artifact_reference": None,
        "canonical_semantic_artifact_hash": None,
        "domain_reference": None,
        "worker_reference": None,
        "milestone_reference": None,
        "provider_necessity_classification": None,
        "resource_selection_reference": None,
        "resource_selection_hash": None,
        "selected_resource_id": None,
        "selected_resource_category": None,
        "selected_role_type": None,
        "resource_ppp_integration_reference": None,
        "resource_ppp_integration_hash": None,
        "resource_ppp_status": None,
        "capability_matches": False,
        "trust_matches": False,
        "authority_matches": False,
        "provider_proposal_production_status": None,
        "provider_proposal_hash": None,
        "repair_retry_status": None,
        "repair_retry_hash": None,
        "final_validation_status": None,
        "implementation_handoff_reference": None,
        "implementation_handoff_hash": None,
        "clarification_required": False,
        "approval_required": False,
        "created_at": created_at,
        "proposal_only": True,
        "provider_invoked": False,
        "provider_authority": False,
        "aigol_governance_only": True,
        "human_final_authority": True,
        "worker_created": False,
        "domain_created": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "authorization_created": False,
        "governance_modified": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(route: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(route, "conversation resource PPP routing artifact")
    artifact = {
        "event_type": "CONVERSATION_PPP_RESOURCE_SELECTION_ROUTING_RETURNED",
        "route_reference": route["route_id"],
        "route_hash": route["artifact_hash"],
        "route_status": route["route_status"],
        "canonical_chain_id": route["canonical_chain_id"],
        "ppp_semantic_annotation_hash": route.get("ppp_semantic_annotation_hash"),
        "ppp_semantic_annotation_parity_status": route.get("ppp_semantic_annotation_parity_status"),
        "canonical_semantic_artifact_hash": route.get("canonical_semantic_artifact_hash"),
        "selected_resource_id": route["selected_resource_id"],
        "selected_role_type": route["selected_role_type"],
        "implementation_handoff_reference": route["implementation_handoff_reference"],
        "clarification_required": route["clarification_required"],
        "approval_required": route["approval_required"],
        "provider_invoked": route["provider_invoked"],
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "authorization_created": False,
        "replay_visible": True,
        "failure_reason": route["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(route: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "conversation_ppp_resource_selection_routing_artifact": deepcopy(route),
        "conversation_ppp_resource_selection_routing_replay": deepcopy(returned),
        "conversation_ppp_resource_selection_routing_replay_reference": str(replay_path),
        "route_status": route["route_status"],
        "canonical_chain_id": route["canonical_chain_id"],
        "ppp_semantic_annotation_source": route.get("ppp_semantic_annotation_source"),
        "ppp_semantic_annotation_artifact": deepcopy(route.get("ppp_semantic_annotation_artifact")),
        "ppp_semantic_annotation_hash": route.get("ppp_semantic_annotation_hash"),
        "ppp_semantic_annotation_parity_status": route.get("ppp_semantic_annotation_parity_status"),
        "ppp_semantic_annotation_migration_batch_id": route.get("ppp_semantic_annotation_migration_batch_id"),
        "canonical_semantic_artifact_reference": route.get("canonical_semantic_artifact_reference"),
        "canonical_semantic_artifact_hash": route.get("canonical_semantic_artifact_hash"),
        "selected_resource_id": route["selected_resource_id"],
        "selected_resource_category": route["selected_resource_category"],
        "selected_role_type": route["selected_role_type"],
        "resource_ppp_status": route["resource_ppp_status"],
        "provider_proposal_production_status": route["provider_proposal_production_status"],
        "repair_retry_status": route["repair_retry_status"],
        "implementation_handoff_reference": route["implementation_handoff_reference"],
        "clarification_required": route["clarification_required"],
        "approval_required": route["approval_required"],
        "fail_closed": route["route_status"] == FAILED_CLOSED,
        "failure_reason": route["failure_reason"],
        "provider_invoked": route["provider_invoked"],
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "authorization_created": False,
        "worker_created": False,
        "domain_created": False,
    }
    capture["conversation_ppp_resource_selection_routing_capture_hash"] = replay_hash(capture)
    return capture


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("conversation resource PPP routing replay step ordering mismatch")
    _verify_artifact_hash(artifact, "conversation resource PPP routing artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "event_type": step.upper(),
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    try:
        _persist_step(replay_dir, index, step, artifact)
    except FailClosedRuntimeError:
        pass


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError(f"{label} hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("conversation resource PPP routing replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("conversation resource PPP routing replay hash mismatch")


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "conversation resource PPP routing failed closed"
