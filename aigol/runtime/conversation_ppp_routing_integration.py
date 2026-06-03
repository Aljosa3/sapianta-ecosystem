"""Conversation PPP routing integration for AiGOL V1."""

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
from aigol.runtime.conversation_to_implementation_handoff_runtime import (
    IMPLEMENTATION_HANDOFF_CREATED,
    create_conversation_to_implementation_handoff,
)
from aigol.runtime.development_proposal_contract_runtime import (
    DEVELOPMENT_PROPOSAL_ARTIFACT_V1,
    DEVELOPMENT_PROPOSAL_CONTRACT_VALIDATED,
    validate_development_proposal_contract,
)
from aigol.runtime.domain_and_worker_resolution_registry import (
    RESOLUTION_SUCCEEDED,
    resolve_domain_worker_milestone,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_necessity_policy_runtime import (
    PROVIDER_REQUIRED,
    classify_provider_necessity,
)
from aigol.runtime.provider_proposal_production_runtime import (
    PROVIDER_PROPOSAL_PRODUCED,
    produce_provider_development_proposal,
)
from aigol.runtime.provider_proposal_repair_and_retry_runtime import (
    HUMAN_APPROVAL_REQUIRED,
    HUMAN_CLARIFICATION_REQUIRED,
    repair_and_retry_provider_development_proposal,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_CONVERSATION_PPP_ROUTING_INTEGRATION_VERSION = "AIGOL_CONVERSATION_PPP_ROUTING_INTEGRATION_V1"
CONVERSATION_PPP_ROUTED = "CONVERSATION_PPP_ROUTED"
CONVERSATION_PPP_HANDOFF_CREATED = "CONVERSATION_PPP_HANDOFF_CREATED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "conversation_ppp_route_recorded",
    "conversation_ppp_route_returned",
)


def run_conversation_ppp_routing_integration(
    *,
    prompt_id: str,
    human_prompt: str,
    provider_id: str,
    created_at: str,
    replay_dir: str | Path,
    registry: ProviderRegistry,
    adapter: ProviderAdapter,
    governance_root: str | Path = "governance",
    session_id: str | None = None,
    turn_id: str | None = None,
    current_chain_id: str | None = None,
    latest_chain_id: str | None = None,
) -> dict[str, Any]:
    """Route a native-development conversation prompt through the PPP lifecycle."""

    root = Path(replay_dir)
    route_replay = root / "conversation_ppp_route"
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
            raise FailClosedRuntimeError(conversation.get("failure_reason") or "conversation PPP intake failed closed")
        context = conversation["development_context_assembly"]["development_context_assembly_artifact"]
        intake = conversation["native_development_task_intake"]["native_development_task_intake_artifact"]
        canonical_chain_id = conversation["canonical_chain_id"]
        resolution = resolve_domain_worker_milestone(
            resolution_id=f"{prompt_id}:PPP-DOMAIN-WORKER-RESOLUTION",
            domain_id=context["requested_domain"],
            worker_family_id=context["requested_worker_family"],
            milestone_type=_milestone_type(intake),
            created_at=created_at,
            replay_dir=root / "domain_worker_resolution",
        )
        if resolution.get("resolution_status") != RESOLUTION_SUCCEEDED:
            raise FailClosedRuntimeError(resolution.get("failure_reason") or "conversation PPP resolution failed closed")
        resolution_artifact = resolution["domain_worker_resolution_artifact"]
        provider_policy = classify_provider_necessity(
            policy_decision_id=f"{prompt_id}:PPP-PROVIDER-NECESSITY",
            workflow_type="NATIVE_DEVELOPMENT",
            task_kind=resolution_artifact["milestone_type"],
            created_at=created_at,
            replay_dir=root / "provider_necessity",
        )
        provider_policy_artifact = provider_policy["provider_necessity_policy_artifact"]
        if provider_policy.get("necessity_classification") != PROVIDER_REQUIRED:
            raise FailClosedRuntimeError("conversation PPP failed closed: provider proposal is not required")
        seed_proposal = _seed_proposal(
            proposal_id=f"{prompt_id}:PPP-SEED-PROPOSAL",
            context=context,
            resolution=resolution_artifact,
            intake=intake,
        )
        seed_validation = validate_development_proposal_contract(
            contract_validation_id=f"{prompt_id}:PPP-SEED-PROPOSAL-VALIDATION",
            proposal_artifact=seed_proposal,
            context_assembly_artifact=context,
            registry_resolution_artifact=resolution_artifact,
            created_at=created_at,
            replay_dir=root / "seed_proposal_contract",
        )
        if seed_validation.get("validation_status") != DEVELOPMENT_PROPOSAL_CONTRACT_VALIDATED:
            raise FailClosedRuntimeError(seed_validation.get("failure_reason") or "conversation PPP seed proposal failed")
        request_handoff = create_conversation_to_implementation_handoff(
            handoff_id=f"{prompt_id}:PPP-PROVIDER-REQUEST-HANDOFF",
            proposal_artifact=seed_proposal,
            proposal_contract_validation_artifact=seed_validation["development_proposal_contract_validation_artifact"],
            context_assembly_artifact=context,
            registry_resolution_artifact=resolution_artifact,
            provider_necessity_policy_artifact=provider_policy_artifact,
            created_at=created_at,
            replay_dir=root / "provider_request_handoff",
        )
        if request_handoff.get("handoff_status") != IMPLEMENTATION_HANDOFF_CREATED:
            raise FailClosedRuntimeError(request_handoff.get("failure_reason") or "conversation PPP request handoff failed")
        production = produce_provider_development_proposal(
            production_id=f"{prompt_id}:PPP-PROVIDER-PROPOSAL-PRODUCTION",
            provider_id=provider_id,
            handoff_artifact=request_handoff["implementation_handoff_artifact"],
            context_assembly_artifact=context,
            registry_resolution_artifact=resolution_artifact,
            provider_necessity_policy_artifact=provider_policy_artifact,
            canonical_chain_id=canonical_chain_id,
            created_at=created_at,
            registry=registry,
            adapter=adapter,
            replay_dir=root / "provider_proposal_production",
        )
        repair = None
        final_validation = None
        final_handoff = None
        route_status = CONVERSATION_PPP_ROUTED
        approval_required = False
        clarification_required = False
        if production.get("production_status") == PROVIDER_PROPOSAL_PRODUCED:
            final_validation, final_handoff = _validate_and_handoff(
                prompt_id=prompt_id,
                proposal=production["development_proposal_artifact"],
                context=context,
                resolution=resolution_artifact,
                provider_policy=provider_policy_artifact,
                created_at=created_at,
                replay_root=root,
            )
            route_status = CONVERSATION_PPP_HANDOFF_CREATED
            approval_required = _is_high_risk_domain(resolution_artifact["domain_id"])
        else:
            repair = _repair_failed_production(
                prompt_id=prompt_id,
                production=production,
                context=context,
                resolution=resolution_artifact,
                provider_policy=provider_policy_artifact,
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
            request_handoff=request_handoff,
            production=production,
            repair=repair,
            final_validation=final_validation,
            final_handoff=final_handoff,
            approval_required=approval_required,
            clarification_required=clarification_required,
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


def reconstruct_conversation_ppp_routing_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct conversation PPP routing replay."""

    replay_path = Path(replay_dir) / "conversation_ppp_route"
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("conversation PPP routing replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("conversation PPP routing replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "conversation PPP routing artifact")
        wrappers.append(wrapper)
    route = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("route_reference") != route["route_id"]:
        raise FailClosedRuntimeError("conversation PPP routing replay reference mismatch")
    if returned.get("route_hash") != route["artifact_hash"]:
        raise FailClosedRuntimeError("conversation PPP routing replay hash mismatch")
    return {
        "route_id": route["route_id"],
        "route_status": route["route_status"],
        "canonical_chain_id": route["canonical_chain_id"],
        "task_intake_reference": route["task_intake_reference"],
        "context_hash": route["context_hash"],
        "domain_reference": route["domain_reference"],
        "worker_reference": route["worker_reference"],
        "provider_necessity_classification": route["provider_necessity_classification"],
        "provider_proposal_production_status": route["provider_proposal_production_status"],
        "repair_retry_status": route["repair_retry_status"],
        "implementation_handoff_reference": route["implementation_handoff_reference"],
        "clarification_required": route["clarification_required"],
        "approval_required": route["approval_required"],
        "failure_reason": route["failure_reason"],
        "provider_invoked": route["provider_invoked"],
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _validate_and_handoff(
    *,
    prompt_id: str,
    proposal: dict[str, Any],
    context: dict[str, Any],
    resolution: dict[str, Any],
    provider_policy: dict[str, Any],
    created_at: str,
    replay_root: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    validation = validate_development_proposal_contract(
        contract_validation_id=f"{prompt_id}:PPP-FINAL-PROPOSAL-VALIDATION",
        proposal_artifact=proposal,
        context_assembly_artifact=context,
        registry_resolution_artifact=resolution,
        created_at=created_at,
        replay_dir=replay_root / "final_proposal_contract",
    )
    if validation.get("validation_status") != DEVELOPMENT_PROPOSAL_CONTRACT_VALIDATED:
        raise FailClosedRuntimeError(validation.get("failure_reason") or "conversation PPP final proposal failed")
    handoff = create_conversation_to_implementation_handoff(
        handoff_id=f"{prompt_id}:PPP-FINAL-IMPLEMENTATION-HANDOFF",
        proposal_artifact=proposal,
        proposal_contract_validation_artifact=validation["development_proposal_contract_validation_artifact"],
        context_assembly_artifact=context,
        registry_resolution_artifact=resolution,
        provider_necessity_policy_artifact=provider_policy,
        created_at=created_at,
        replay_dir=replay_root / "final_implementation_handoff",
    )
    if handoff.get("handoff_status") != IMPLEMENTATION_HANDOFF_CREATED:
        raise FailClosedRuntimeError(handoff.get("failure_reason") or "conversation PPP final handoff failed")
    return validation, handoff


def _repair_failed_production(
    *,
    prompt_id: str,
    production: dict[str, Any],
    context: dict[str, Any],
    resolution: dict[str, Any],
    provider_policy: dict[str, Any],
    canonical_chain_id: str,
    provider_id: str,
    created_at: str,
    registry: ProviderRegistry,
    adapter: ProviderAdapter,
    replay_root: Path,
) -> dict[str, Any]:
    proposal = production.get("development_proposal_artifact")
    response = production.get("provider_response_artifact")
    if not isinstance(response, dict):
        raise FailClosedRuntimeError(production.get("failure_reason") or "conversation PPP provider production failed")
    if not isinstance(proposal, dict):
        proposal = _rejected_proposal_from_provider_response(
            prompt_id=prompt_id,
            response=response,
            context=context,
            resolution=resolution,
        )
    validation = validate_development_proposal_contract(
        contract_validation_id=f"{prompt_id}:PPP-REPAIR-VALIDATION-FAILURE",
        proposal_artifact=proposal,
        context_assembly_artifact=context,
        registry_resolution_artifact=resolution,
        created_at=created_at,
        replay_dir=replay_root / "repair_validation_failure",
    )
    return repair_and_retry_provider_development_proposal(
        repair_id=f"{prompt_id}:PPP-PROVIDER-REPAIR-RETRY",
        rejected_proposal_artifact=proposal,
        validation_failure_evidence=validation["development_proposal_contract_validation_artifact"],
        provider_response_artifact=response,
        context_assembly_artifact=context,
        registry_resolution_artifact=resolution,
        provider_necessity_policy_artifact=provider_policy,
        canonical_chain_id=canonical_chain_id,
        provider_id=provider_id,
        created_at=created_at,
        registry=registry,
        adapter=adapter,
        replay_dir=replay_root / "provider_proposal_repair_retry",
    )


def _rejected_proposal_from_provider_response(
    *,
    prompt_id: str,
    response: dict[str, Any],
    context: dict[str, Any],
    resolution: dict[str, Any],
) -> dict[str, Any]:
    payload = response.get("provider_response_payload")
    if not isinstance(payload, dict):
        raise FailClosedRuntimeError("conversation PPP provider production failed without repairable proposal")
    proposal = {
        "artifact_type": DEVELOPMENT_PROPOSAL_ARTIFACT_V1,
        "proposal_id": f"{prompt_id}:PPP-REJECTED-PROVIDER-PROPOSAL",
        "task_reference": context["development_task_intake_reference"],
        "context_reference": context["context_assembly_id"],
        "context_hash": context["context_hash"],
        "domain_reference": resolution["domain_id"],
        "worker_reference": resolution["worker_family_id"],
        "milestone_reference": resolution["milestone_type"],
        "proposal_summary": payload.get("proposal_summary", "Rejected provider proposal."),
        "proposed_outputs": list(payload.get("proposed_outputs", [])),
        "constraints_acknowledged": list(payload.get("constraints_acknowledged", [])),
        "assumptions": list(payload.get("assumptions", [])),
        "known_gaps": list(payload.get("known_gaps", [])),
        "proposal_only": True,
        "execution_authority": False,
        "dispatch_authority": False,
        "governance_authority": False,
        "replay_authority": False,
        "provider_authority": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "worker_created": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    proposal["artifact_hash"] = replay_hash(proposal)
    return proposal


def _seed_proposal(*, proposal_id: str, context: dict[str, Any], resolution: dict[str, Any], intake: dict[str, Any]) -> dict[str, Any]:
    outputs = intake.get("requested_output_scope")
    if not isinstance(outputs, list) or not outputs:
        outputs = [f"governance/{intake['requested_milestone_id']}.md"]
    proposal = {
        "artifact_type": DEVELOPMENT_PROPOSAL_ARTIFACT_V1,
        "proposal_id": proposal_id,
        "task_reference": context["development_task_intake_reference"],
        "context_reference": context["context_assembly_id"],
        "context_hash": context["context_hash"],
        "domain_reference": resolution["domain_id"],
        "worker_reference": resolution["worker_family_id"],
        "milestone_reference": resolution["milestone_type"],
        "proposal_summary": "Seed proposal used only to create a bounded provider request handoff.",
        "proposed_outputs": list(outputs),
        "constraints_acknowledged": list(intake.get("explicit_constraints", [])),
        "assumptions": ["Provider proposal production remains proposal-only."],
        "known_gaps": ["Seed proposal is not an implementation proposal."],
        "proposal_only": True,
        "execution_authority": False,
        "dispatch_authority": False,
        "governance_authority": False,
        "replay_authority": False,
        "provider_authority": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "worker_created": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    proposal["artifact_hash"] = replay_hash(proposal)
    return proposal


def _milestone_type(intake: dict[str, Any]) -> str:
    task_kind = intake.get("task_kind")
    if task_kind == "WORKER_FOUNDATION":
        return "WORKER_FOUNDATION"
    if isinstance(task_kind, str) and "WORKER" in task_kind and "FOUNDATION" in task_kind:
        return "WORKER_FOUNDATION"
    if isinstance(task_kind, str) and task_kind.strip():
        return task_kind
    return "WORKER_FOUNDATION"


def _route_artifact(
    *,
    prompt_id: str,
    route_status: str,
    conversation: dict[str, Any],
    resolution: dict[str, Any],
    provider_policy: dict[str, Any],
    request_handoff: dict[str, Any],
    production: dict[str, Any],
    repair: dict[str, Any] | None,
    final_validation: dict[str, Any] | None,
    final_handoff: dict[str, Any] | None,
    approval_required: bool,
    clarification_required: bool,
    created_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    resolution_artifact = resolution["domain_worker_resolution_artifact"]
    policy_artifact = provider_policy["provider_necessity_policy_artifact"]
    handoff_artifact = final_handoff.get("implementation_handoff_artifact") if final_handoff else None
    artifact = {
        "artifact_type": "CONVERSATION_PPP_ROUTING_ARTIFACT_V1",
        "runtime_version": AIGOL_CONVERSATION_PPP_ROUTING_INTEGRATION_VERSION,
        "route_id": f"{prompt_id}:PPP-ROUTE",
        "prompt_id": prompt_id,
        "route_status": route_status,
        "canonical_chain_id": conversation["canonical_chain_id"],
        "task_intake_reference": conversation["task_intake_reference"],
        "context_reference": conversation["context_assembly_reference"],
        "context_hash": conversation["context_hash"],
        "domain_reference": resolution_artifact["domain_id"],
        "worker_reference": resolution_artifact["worker_family_id"],
        "milestone_reference": resolution_artifact["milestone_type"],
        "provider_necessity_classification": provider_policy["necessity_classification"],
        "provider_necessity_hash": policy_artifact["artifact_hash"],
        "provider_request_handoff_reference": request_handoff["proposal_reference"],
        "provider_request_handoff_hash": request_handoff["handoff_hash"],
        "provider_proposal_production_status": production["production_status"],
        "provider_proposal_hash": production.get("proposal_hash"),
        "repair_retry_status": repair.get("retry_status") if repair else None,
        "repair_retry_hash": repair.get("provider_proposal_repair_retry_capture_hash") if repair else None,
        "final_validation_status": final_validation.get("validation_status") if final_validation else None,
        "implementation_handoff_reference": handoff_artifact.get("handoff_id") if handoff_artifact else None,
        "implementation_handoff_hash": handoff_artifact.get("artifact_hash") if handoff_artifact else None,
        "clarification_required": clarification_required,
        "approval_required": approval_required,
        "created_at": created_at,
        "proposal_only": True,
        "provider_invoked": production.get("provider_invocation_status") == "PROVIDER_INVOKED",
        "provider_authority": False,
        "aigol_governance_only": True,
        "human_final_authority": True,
        "worker_created": False,
        "domain_created": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_route_artifact(
    *,
    prompt_id: str,
    created_at: str,
    canonical_chain_id: Any,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": "CONVERSATION_PPP_ROUTING_ARTIFACT_V1",
        "runtime_version": AIGOL_CONVERSATION_PPP_ROUTING_INTEGRATION_VERSION,
        "route_id": f"{prompt_id}:PPP-ROUTE" if isinstance(prompt_id, str) else "INVALID_PROMPT:PPP-ROUTE",
        "prompt_id": prompt_id if isinstance(prompt_id, str) else "INVALID_PROMPT",
        "route_status": FAILED_CLOSED,
        "canonical_chain_id": canonical_chain_id if isinstance(canonical_chain_id, str) else None,
        "task_intake_reference": None,
        "context_reference": None,
        "context_hash": None,
        "domain_reference": None,
        "worker_reference": None,
        "milestone_reference": None,
        "provider_necessity_classification": None,
        "provider_proposal_production_status": None,
        "repair_retry_status": None,
        "implementation_handoff_reference": None,
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
        "governance_modified": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(route: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(route, "conversation PPP routing artifact")
    artifact = {
        "event_type": "CONVERSATION_PPP_ROUTING_RETURNED",
        "route_reference": route["route_id"],
        "route_hash": route["artifact_hash"],
        "route_status": route["route_status"],
        "canonical_chain_id": route["canonical_chain_id"],
        "implementation_handoff_reference": route["implementation_handoff_reference"],
        "clarification_required": route["clarification_required"],
        "approval_required": route["approval_required"],
        "provider_invoked": route["provider_invoked"],
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "failure_reason": route["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(route: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "conversation_ppp_routing_artifact": deepcopy(route),
        "conversation_ppp_routing_replay": deepcopy(returned),
        "conversation_ppp_routing_replay_reference": str(replay_path),
        "route_status": route["route_status"],
        "canonical_chain_id": route["canonical_chain_id"],
        "context_hash": route["context_hash"],
        "domain_reference": route["domain_reference"],
        "worker_reference": route["worker_reference"],
        "provider_proposal_production_status": route["provider_proposal_production_status"],
        "repair_retry_status": route["repair_retry_status"],
        "implementation_handoff_reference": route["implementation_handoff_reference"],
        "clarification_required": route["clarification_required"],
        "approval_required": route["approval_required"],
        "fail_closed": route["route_status"] == FAILED_CLOSED,
        "failure_reason": route["failure_reason"],
        "provider_invoked": route["provider_invoked"],
        "provider_authority": False,
        "aigol_governance_only": True,
        "human_final_authority": True,
        "worker_created": False,
        "domain_created": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
    }
    capture["conversation_ppp_routing_capture_hash"] = replay_hash(capture)
    return capture


def _is_high_risk_domain(domain_id: str) -> bool:
    return domain_id.upper() in {"TRADING", "HEALTHCARE", "LEGAL", "CRITICAL_INFRASTRUCTURE", "PUBLIC_SERVICES"}


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("conversation PPP routing replay step ordering mismatch")
    _verify_artifact_hash(artifact, "conversation PPP routing artifact")
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
        raise FailClosedRuntimeError("conversation PPP routing replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("conversation PPP routing replay hash mismatch")


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "conversation PPP routing failed closed"
