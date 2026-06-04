"""Conversation-to-PPP handoff continuation for native-development routed intents."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.conversation_native_development_intent_routing import (
    NATIVE_DEVELOPMENT_INTENT_ROUTED,
    NATIVE_DEVELOPMENT_INTENT_ROUTED_ARTIFACT_V1,
)
from aigol.runtime.conversation_to_implementation_handoff_runtime import (
    IMPLEMENTATION_HANDOFF_CREATED,
    create_conversation_to_implementation_handoff,
    reconstruct_conversation_to_implementation_handoff_replay,
)
from aigol.runtime.development_context_assembly_runtime import (
    CONTEXT_ASSEMBLED,
    DEVELOPMENT_CONTEXT_ASSEMBLY_ARTIFACT_V1,
)
from aigol.runtime.development_proposal_contract_runtime import (
    DEVELOPMENT_PROPOSAL_ARTIFACT_V1,
    DEVELOPMENT_PROPOSAL_CONTRACT_VALIDATED,
    validate_development_proposal_contract,
)
from aigol.runtime.domain_and_worker_resolution_registry import (
    DOMAIN_WORKER_RESOLUTION_ARTIFACT_V1,
    RESOLUTION_SUCCEEDED,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_necessity_policy_runtime import (
    PROVIDER_NECESSITY_CLASSIFIED,
    PROVIDER_NECESSITY_POLICY_ARTIFACT_V1,
    PROVIDER_REQUIRED,
)
from aigol.runtime.provider_proposal_production_runtime import PROVIDER_PROPOSAL_PRODUCTION_ARTIFACT_V1
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.unified_resource_selection_ppp_integration import (
    RESOURCE_PPP_INTEGRATED,
    integrate_resource_selection_with_ppp,
)
from aigol.runtime.unified_resource_selection_runtime import (
    PROVIDER_ROLE,
    RESOURCE_SELECTION_SUCCEEDED,
    select_unified_resource,
)


AIGOL_CONVERSATION_TO_PPP_HANDOFF_EXECUTION_VERSION = "AIGOL_CONVERSATION_TO_PPP_HANDOFF_EXECUTION_V1"
CONVERSATION_TO_PPP_HANDOFF_EXECUTION_ARTIFACT_V1 = "CONVERSATION_TO_PPP_HANDOFF_EXECUTION_ARTIFACT_V1"
IMPLEMENTATION_HANDOFF_CREATED_STATUS = IMPLEMENTATION_HANDOFF_CREATED
HUMAN_APPROVAL_REQUIRED = "HUMAN_APPROVAL_REQUIRED"
HUMAN_CLARIFICATION_REQUIRED = "HUMAN_CLARIFICATION_REQUIRED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "conversation_to_ppp_handoff_execution_recorded",
    "conversation_to_ppp_handoff_execution_returned",
)


def run_conversation_to_ppp_handoff_execution(
    *,
    execution_id: str,
    native_development_intent_routed_artifact: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Continue a routed conversation intent to approval or implementation handoff."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        routed = deepcopy(native_development_intent_routed_artifact)
        _validate_routed_intent(routed)
        context = _context_artifact(execution_id, routed, created_at, replay_path)
        registry = _registry_resolution_artifact(execution_id, routed, created_at, replay_path)
        policy = _provider_policy_artifact(execution_id, routed, created_at)
        resource = select_unified_resource(
            selection_id=f"{execution_id}:RESOURCE-SELECTION",
            workflow_type="NATIVE_DEVELOPMENT",
            required_capability="PROPOSAL_GENERATION",
            requested_role_type=PROVIDER_ROLE,
            domain_id="NATIVE_DEVELOPMENT",
            provider_necessity_classification=PROVIDER_REQUIRED,
            created_at=created_at,
            replay_dir=replay_path / "resource_selection",
            context_assembly_output=context,
        )
        if resource.get("selection_status") != RESOURCE_SELECTION_SUCCEEDED:
            raise FailClosedRuntimeError(resource.get("failure_reason") or "conversation PPP handoff failed closed: resource selection fails")
        ppp = integrate_resource_selection_with_ppp(
            integration_id=f"{execution_id}:RESOURCE-PPP-INTEGRATION",
            resource_selection_artifact=resource["resource_selection_artifact"],
            context_assembly_artifact=context,
            created_at=created_at,
            replay_dir=replay_path / "resource_ppp_integration",
        )
        if ppp.get("integration_status") != RESOURCE_PPP_INTEGRATED:
            raise FailClosedRuntimeError(ppp.get("failure_reason") or "conversation PPP handoff failed closed: PPP integration fails")
        proposal_production = _proposal_production_artifact(execution_id, routed, context, registry, policy, resource, ppp, created_at)
        proposal = proposal_production["development_proposal_artifact"]
        validation = validate_development_proposal_contract(
            contract_validation_id=f"{execution_id}:PROPOSAL-VALIDATION",
            proposal_artifact=proposal,
            context_assembly_artifact=context,
            registry_resolution_artifact=registry,
            created_at=created_at,
            replay_dir=replay_path / "proposal_validation",
        )
        if validation.get("validation_status") != DEVELOPMENT_PROPOSAL_CONTRACT_VALIDATED:
            raise FailClosedRuntimeError(validation.get("failure_reason") or "conversation PPP handoff failed closed: PPP validation fails")
        approval = _approval_artifact(execution_id, routed, proposal, validation, created_at)
        if approval["approval_status"] == HUMAN_APPROVAL_REQUIRED:
            terminal_status = HUMAN_APPROVAL_REQUIRED
            handoff = None
        else:
            handoff = create_conversation_to_implementation_handoff(
                handoff_id=f"{execution_id}:IMPLEMENTATION-HANDOFF",
                proposal_artifact=proposal,
                proposal_contract_validation_artifact=validation["development_proposal_contract_validation_artifact"],
                context_assembly_artifact=context,
                registry_resolution_artifact=registry,
                provider_necessity_policy_artifact=policy,
                created_at=created_at,
                replay_dir=replay_path / "implementation_handoff",
            )
            if handoff.get("handoff_status") != IMPLEMENTATION_HANDOFF_CREATED:
                raise FailClosedRuntimeError(handoff.get("failure_reason") or "conversation PPP handoff failed closed: implementation handoff fails")
            terminal_status = IMPLEMENTATION_HANDOFF_CREATED_STATUS
        artifact = _execution_artifact(
            execution_id=execution_id,
            routed=routed,
            context=context,
            registry=registry,
            policy=policy,
            resource=resource,
            ppp=ppp,
            proposal_production=proposal_production,
            validation=validation,
            approval=approval,
            handoff=handoff,
            terminal_status=terminal_status,
            created_at=created_at,
            failure_reason=None,
        )
        returned = _returned_artifact(artifact)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, replay_path)
    except Exception as exc:
        artifact = _failed_execution_artifact(
            execution_id=execution_id,
            routed=native_development_intent_routed_artifact,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(artifact)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, replay_path)


def reconstruct_conversation_to_ppp_handoff_execution_replay(replay_dir: str | Path) -> dict[str, Any]:
    replay_path = Path(replay_dir)
    wrappers = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("conversation PPP handoff replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("conversation PPP handoff replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "conversation PPP handoff execution")
        wrappers.append(wrapper)
    artifact = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("execution_reference") != artifact["execution_id"]:
        raise FailClosedRuntimeError("conversation PPP handoff replay reference mismatch")
    if returned.get("execution_hash") != artifact["artifact_hash"]:
        raise FailClosedRuntimeError("conversation PPP handoff replay hash mismatch")
    if artifact.get("handoff_replay_reference"):
        handoff = reconstruct_conversation_to_implementation_handoff_replay(artifact["handoff_replay_reference"])
        if handoff["handoff_status"] != IMPLEMENTATION_HANDOFF_CREATED:
            raise FailClosedRuntimeError("conversation PPP handoff lineage mismatch")
    return {
        "execution_id": artifact["execution_id"],
        "terminal_status": artifact["terminal_status"],
        "intent_class": artifact["intent_class"],
        "resource_selection_status": artifact["resource_selection_status"],
        "ppp_integration_status": artifact["ppp_integration_status"],
        "proposal_production_status": artifact["proposal_production_status"],
        "proposal_validation_status": artifact["proposal_validation_status"],
        "approval_status": artifact["approval_status"],
        "handoff_status": artifact["handoff_status"],
        "canonical_chain_id": artifact["canonical_chain_id"],
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "authorization_created": False,
        "failure_reason": artifact["failure_reason"],
    }


def render_conversation_to_ppp_handoff_execution_summary(capture: dict[str, Any]) -> str:
    lines = [
        f"conversation_to_ppp_terminal_status: {capture.get('terminal_status')}",
        f"intent_class: {capture.get('intent_class')}",
        f"resource_selection_status: {capture.get('resource_selection_status')}",
        f"ppp_integration_status: {capture.get('ppp_integration_status')}",
        f"proposal_production_status: {capture.get('proposal_production_status')}",
        f"proposal_validation_status: {capture.get('proposal_validation_status')}",
        f"approval_status: {capture.get('approval_status')}",
        f"handoff_status: {capture.get('handoff_status')}",
        f"handoff_reference: {capture.get('handoff_reference')}",
        f"replay_reference: {capture.get('conversation_to_ppp_handoff_execution_replay_reference')}",
    ]
    if capture.get("failure_reason"):
        lines.append(f"failure_reason: {capture['failure_reason']}")
    return "\n".join(lines)


def _validate_routed_intent(routed: dict[str, Any]) -> None:
    if routed.get("artifact_type") != NATIVE_DEVELOPMENT_INTENT_ROUTED_ARTIFACT_V1:
        raise FailClosedRuntimeError("conversation PPP handoff failed closed: invalid routed intent")
    _verify_artifact_hash(routed, "native development routed intent")
    if routed.get("routing_status") != NATIVE_DEVELOPMENT_INTENT_ROUTED:
        raise FailClosedRuntimeError("conversation PPP handoff failed closed: routing lineage breaks")


def _context_artifact(execution_id: str, routed: dict[str, Any], created_at: str, replay_path: Path) -> dict[str, Any]:
    worker = _worker_family(routed)
    artifact = {
        "artifact_type": DEVELOPMENT_CONTEXT_ASSEMBLY_ARTIFACT_V1,
        "context_assembly_id": f"{execution_id}:CONTEXT",
        "development_task_intake_reference": routed["routed_intent_id"],
        "requested_domain": routed["target_domain"],
        "requested_worker_family": worker,
        "requested_milestone_id": routed["target_milestone"],
        "context_status": CONTEXT_ASSEMBLED,
        "artifact_references": [],
        "missing_context": [],
        "ambiguous_context": [],
        "known_assumptions": ["Conversation-to-PPP bridge uses deterministic context shell."],
        "known_gaps": ["Dedicated downstream context bundle is still required for full domain scaling."],
        "provider_necessity_classification": PROVIDER_REQUIRED,
        "created_at": created_at,
        "replay_reference": str(replay_path / "context"),
        "replay_visible": True,
        "worker_invoked": False,
        "execution_requested": False,
    }
    artifact["context_hash"] = replay_hash({"context_assembly_id": artifact["context_assembly_id"], "routed_intent_hash": routed["artifact_hash"]})
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _registry_resolution_artifact(execution_id: str, routed: dict[str, Any], created_at: str, replay_path: Path) -> dict[str, Any]:
    artifact = {
        "artifact_type": DOMAIN_WORKER_RESOLUTION_ARTIFACT_V1,
        "resolution_id": f"{execution_id}:DOMAIN-WORKER-RESOLUTION",
        "resolution_status": RESOLUTION_SUCCEEDED,
        "domain_id": routed["target_domain"],
        "worker_family_id": _worker_family(routed),
        "milestone_type": _milestone_type(routed),
        "registry_version": "CONVERSATION_TO_PPP_SYNTHETIC_REGISTRY_V1",
        "registry_hash": replay_hash({"registry": "conversation_to_ppp", "target_domain": routed["target_domain"]}),
        "resolution_result": {"source": "conversation_native_development_intent_routing"},
        "created_at": created_at,
        "replay_reference": str(replay_path / "domain_worker_resolution"),
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _provider_policy_artifact(execution_id: str, routed: dict[str, Any], created_at: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": PROVIDER_NECESSITY_POLICY_ARTIFACT_V1,
        "policy_decision_id": f"{execution_id}:PROVIDER-NECESSITY",
        "policy_version": "CONVERSATION_TO_PPP_PROVIDER_POLICY_V1",
        "policy_hash": replay_hash({"policy": "provider required for proposal"}),
        "workflow_type": "NATIVE_DEVELOPMENT",
        "command": None,
        "task_kind": _milestone_type(routed),
        "necessity_classification": PROVIDER_REQUIRED,
        "reason": "Conversation-to-PPP proposal drafting requires proposal-only provider resource selection.",
        "matched_rule_id": "CONVERSATION_TO_PPP_PROVIDER_REQUIRED",
        "policy_status": PROVIDER_NECESSITY_CLASSIFIED,
        "provider_invoked": False,
        "provider_authority": False,
        "proposal_generated": False,
        "worker_created": False,
        "domain_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "created_at": created_at,
        "replay_visible": True,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _proposal_production_artifact(execution_id: str, routed: dict[str, Any], context: dict[str, Any], registry: dict[str, Any], policy: dict[str, Any], resource: dict[str, Any], ppp: dict[str, Any], created_at: str) -> dict[str, Any]:
    proposal = {
        "artifact_type": DEVELOPMENT_PROPOSAL_ARTIFACT_V1,
        "proposal_id": f"{execution_id}:DEVELOPMENT-PROPOSAL",
        "task_reference": context["development_task_intake_reference"],
        "context_reference": context["context_assembly_id"],
        "context_hash": context["context_hash"],
        "domain_reference": registry["domain_id"],
        "worker_reference": registry["worker_family_id"],
        "milestone_reference": registry["milestone_type"],
        "proposal_summary": f"Proposal-only handoff for {routed['intent_class']} targeting {routed['target_domain']}.",
        "proposed_outputs": _output_targets(routed),
        "constraints_acknowledged": ["PROPOSAL_ONLY", "NO_EXECUTION", "NO_DISPATCH", "NO_GOVERNANCE_MUTATION"],
        "assumptions": ["Human authority remains final."],
        "known_gaps": ["Generated implementation artifacts are not created by conversation mode."],
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
    artifact = {
        "artifact_type": PROVIDER_PROPOSAL_PRODUCTION_ARTIFACT_V1,
        "production_id": f"{execution_id}:PROPOSAL-PRODUCTION",
        "production_status": "PROVIDER_PROPOSAL_PRODUCED",
        "provider_id": resource["selected_resource_id"],
        "provider_invocation_status": "DETERMINISTIC_PROPOSAL_EVIDENCE",
        "provider_request_hash": ppp["resource_ppp_integration_artifact"]["artifact_hash"],
        "provider_response_hash": replay_hash({"deterministic_response": proposal["proposal_id"]}),
        "proposal_hash": proposal["artifact_hash"],
        "context_hash": context["context_hash"],
        "canonical_chain_id": routed["canonical_chain_id"],
        "development_proposal_artifact": proposal,
        "provider_authority": False,
        "worker_created": False,
        "domain_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "created_at": created_at,
        "replay_visible": True,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _approval_artifact(execution_id: str, routed: dict[str, Any], proposal: dict[str, Any], validation: dict[str, Any], created_at: str) -> dict[str, Any]:
    high_risk = routed.get("target_domain") == "TRADING"
    artifact = {
        "artifact_type": "CONVERSATION_TO_PPP_APPROVAL_EVIDENCE_V1",
        "approval_id": f"{execution_id}:APPROVAL-EVIDENCE",
        "approval_status": HUMAN_APPROVAL_REQUIRED if high_risk else "APPROVAL_NOT_REQUIRED_FOR_HANDOFF",
        "approval_reason": "Trading is high-risk and requires human approval." if high_risk else "Non-executing handoff may be created without execution approval.",
        "canonical_chain_id": routed["canonical_chain_id"],
        "approval_scope": f"{routed['target_domain']}:{routed['intent_class']}:{routed.get('target_milestone')}",
        "proposal_reference": proposal["proposal_id"],
        "proposal_hash": proposal["artifact_hash"],
        "validation_reference": validation["development_proposal_contract_validation_artifact"]["contract_validation_id"],
        "validation_hash": validation["development_proposal_contract_validation_artifact"]["artifact_hash"],
        "created_at": created_at,
        "human_final_authority": True,
        "implementation_authorized": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "worker_invoked": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _execution_artifact(**kwargs: Any) -> dict[str, Any]:
    routed = kwargs["routed"]
    validation = kwargs["validation"]
    approval = kwargs["approval"]
    handoff = kwargs["handoff"]
    handoff_artifact = handoff.get("implementation_handoff_artifact", {}) if isinstance(handoff, dict) else {}
    resume_packet = None
    if kwargs["terminal_status"] == HUMAN_APPROVAL_REQUIRED:
        resume_packet = _resume_packet(
            context=kwargs["context"],
            registry=kwargs["registry"],
            policy=kwargs["policy"],
            proposal_production=kwargs["proposal_production"],
            validation=validation,
            approval=approval,
        )
    artifact = {
        "artifact_type": CONVERSATION_TO_PPP_HANDOFF_EXECUTION_ARTIFACT_V1,
        "runtime_version": AIGOL_CONVERSATION_TO_PPP_HANDOFF_EXECUTION_VERSION,
        "execution_id": kwargs["execution_id"],
        "terminal_status": kwargs["terminal_status"],
        "canonical_chain_id": routed["canonical_chain_id"],
        "routed_intent_reference": routed["routed_intent_id"],
        "routed_intent_hash": routed["artifact_hash"],
        "intent_class": routed["intent_class"],
        "resource_selection_status": kwargs["resource"]["selection_status"],
        "resource_selection_hash": kwargs["resource"]["resource_selection_artifact"]["artifact_hash"],
        "ppp_integration_status": kwargs["ppp"]["integration_status"],
        "ppp_integration_hash": kwargs["ppp"]["resource_ppp_integration_artifact"]["artifact_hash"],
        "proposal_production_status": kwargs["proposal_production"]["production_status"],
        "proposal_production_hash": kwargs["proposal_production"]["artifact_hash"],
        "proposal_validation_status": validation["validation_status"],
        "proposal_validation_hash": validation["development_proposal_contract_validation_artifact"]["artifact_hash"],
        "approval_status": approval["approval_status"],
        "approval_hash": approval["artifact_hash"],
        "approval_scope": approval["approval_scope"],
        "handoff_status": handoff.get("handoff_status") if handoff else None,
        "handoff_reference": handoff_artifact.get("handoff_id") if handoff else None,
        "handoff_hash": handoff.get("handoff_hash") if handoff else None,
        "handoff_replay_reference": handoff.get("implementation_handoff_replay_reference") if handoff else None,
        "created_at": kwargs["created_at"],
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_mutated": False,
        "approval_resume_packet": resume_packet,
        "failure_reason": kwargs["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_execution_artifact(*, execution_id: str, routed: dict[str, Any], created_at: str, failure_reason: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": CONVERSATION_TO_PPP_HANDOFF_EXECUTION_ARTIFACT_V1,
        "runtime_version": AIGOL_CONVERSATION_TO_PPP_HANDOFF_EXECUTION_VERSION,
        "execution_id": execution_id,
        "terminal_status": FAILED_CLOSED,
        "canonical_chain_id": routed.get("canonical_chain_id") if isinstance(routed, dict) else None,
        "routed_intent_reference": routed.get("routed_intent_id") if isinstance(routed, dict) else None,
        "routed_intent_hash": routed.get("artifact_hash") if isinstance(routed, dict) else None,
        "intent_class": routed.get("intent_class") if isinstance(routed, dict) else None,
        "resource_selection_status": FAILED_CLOSED,
        "resource_selection_hash": None,
        "ppp_integration_status": FAILED_CLOSED,
        "ppp_integration_hash": None,
        "proposal_production_status": FAILED_CLOSED,
        "proposal_production_hash": None,
        "proposal_validation_status": FAILED_CLOSED,
        "proposal_validation_hash": None,
        "approval_status": FAILED_CLOSED,
        "approval_hash": None,
        "approval_scope": None,
        "handoff_status": None,
        "handoff_reference": None,
        "handoff_hash": None,
        "handoff_replay_reference": None,
        "created_at": created_at,
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_mutated": False,
        "approval_resume_packet": None,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(artifact, "conversation PPP handoff execution")
    returned = {
        "event_type": "CONVERSATION_TO_PPP_HANDOFF_EXECUTION_RETURNED",
        "execution_reference": artifact["execution_id"],
        "execution_hash": artifact["artifact_hash"],
        "terminal_status": artifact["terminal_status"],
        "handoff_status": artifact["handoff_status"],
        "approval_status": artifact["approval_status"],
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "failure_reason": artifact["failure_reason"],
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(artifact: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = deepcopy(artifact)
    capture.update(
        {
            "command": "aigol conversation-to-ppp-handoff-execution",
            "conversation_to_ppp_handoff_execution_artifact": deepcopy(artifact),
            "conversation_to_ppp_handoff_execution_replay": deepcopy(returned),
            "conversation_to_ppp_handoff_execution_replay_reference": str(replay_path),
            "fail_closed": artifact["terminal_status"] == FAILED_CLOSED,
        }
    )
    capture["conversation_to_ppp_handoff_execution_capture_hash"] = replay_hash(capture)
    return capture


def _worker_family(routed: dict[str, Any]) -> str:
    return routed.get("target_worker_family") or routed.get("target_resource") or "DOMAIN_FOUNDATION"


def _milestone_type(routed: dict[str, Any]) -> str:
    if routed.get("intent_class") == "CREATE_DOMAIN":
        return "DOMAIN_FOUNDATION"
    if routed.get("intent_class") == "ADD_PROVIDER":
        return "PROVIDER_FOUNDATION"
    if routed.get("intent_class") == "IMPROVE_EXISTING_CAPABILITY":
        return "CAPABILITY_IMPROVEMENT"
    if routed.get("intent_class") == "GOVERNANCE_CHANGE":
        return "GOVERNANCE_POLICY"
    return "WORKER_FOUNDATION"


def _output_targets(routed: dict[str, Any]) -> list[str]:
    stem = str(routed.get("target_milestone") or routed["routed_intent_id"]).upper().replace(":", "_")
    return [f"governance/{stem}.md", f"governance/{stem}_CERTIFICATION.json"]


def _resume_packet(
    *,
    context: dict[str, Any],
    registry: dict[str, Any],
    policy: dict[str, Any],
    proposal_production: dict[str, Any],
    validation: dict[str, Any],
    approval: dict[str, Any],
) -> dict[str, Any]:
    packet = {
        "artifact_type": "IMPLEMENTATION_APPROVAL_RESUME_PACKET_V1",
        "context_assembly_artifact": deepcopy(context),
        "registry_resolution_artifact": deepcopy(registry),
        "provider_necessity_policy_artifact": deepcopy(policy),
        "provider_proposal_production_artifact": deepcopy(proposal_production),
        "proposal_artifact": deepcopy(proposal_production["development_proposal_artifact"]),
        "proposal_contract_validation_artifact": deepcopy(
            validation["development_proposal_contract_validation_artifact"]
        ),
        "approval_request_artifact": deepcopy(approval),
        "context_hash": context["artifact_hash"],
        "registry_hash": registry["artifact_hash"],
        "policy_hash": policy["artifact_hash"],
        "proposal_production_hash": proposal_production["artifact_hash"],
        "proposal_hash": proposal_production["development_proposal_artifact"]["artifact_hash"],
        "proposal_validation_hash": validation["development_proposal_contract_validation_artifact"]["artifact_hash"],
        "approval_request_hash": approval["artifact_hash"],
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
    }
    packet["packet_hash"] = replay_hash(packet)
    return packet


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact, "conversation PPP handoff execution")
    wrapper = {"replay_index": index, "replay_step": step, "event_type": step.upper(), "artifact": deepcopy(artifact)}
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    try:
        _persist_step(replay_dir, index, step, artifact)
    except FailClosedRuntimeError:
        pass


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {step}")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError(f"{label} hash is required")
    candidate = deepcopy(artifact)
    actual = candidate.pop("artifact_hash")
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("conversation PPP handoff replay hash is required")
    candidate = deepcopy(wrapper)
    actual = candidate.pop("replay_hash")
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("conversation PPP handoff replay hash mismatch")


def _failure_reason(exc: Exception) -> str:
    reason = str(exc).strip()
    if reason:
        return reason
    return "conversation PPP handoff failed closed"
