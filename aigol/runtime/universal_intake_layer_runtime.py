"""Replay-visible Universal Intake Layer for ACLI workflow routing."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_UNIVERSAL_INTAKE_LAYER_RUNTIME_VERSION = "AIGOL_UNIVERSAL_INTAKE_LAYER_V1"
UNIVERSAL_INTAKE_ARTIFACT_V1 = "UNIVERSAL_INTAKE_ARTIFACT_V1"
UNIVERSAL_INTAKE_RECORDED = "UNIVERSAL_INTAKE_RECORDED"
FAILED_CLOSED = "FAILED_CLOSED"

DOMAIN_INTAKE = "DOMAIN_INTAKE"
NATIVE_DEVELOPMENT_INTAKE = "NATIVE_DEVELOPMENT_INTAKE"
OCS_COGNITION_INTAKE = "OCS_COGNITION_INTAKE"
INTAKE_NOT_APPLICABLE = "INTAKE_NOT_APPLICABLE"

REPLAY_STEP = "universal_intake_recorded"

DOMAIN_WORKFLOWS = frozenset(
    {
        "CREATE_DOMAIN_COMPLIANCE_CLARIFICATION",
        "AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW",
        "DOMAIN_EXECUTION_READY_AUTHORIZATION_BRIDGE",
        "DOMAIN_EXECUTION_AUTHORIZATION",
        "DOMAIN_WORKER_REQUEST",
        "DOMAIN_WORKER_ASSIGNMENT",
        "DOMAIN_WORKER_DISPATCH",
        "DOMAIN_WORKER_INVOCATION",
        "DOMAIN_WORKER_EXECUTION",
        "DOMAIN_WORKER_RESULT_CAPTURE",
        "DOMAIN_WORKER_RESULT_VALIDATION",
        "DOMAIN_POST_EXECUTION_REPLAY_REVIEW",
        "DOMAIN_GOVERNED_TERMINATION",
    }
)
NATIVE_DEVELOPMENT_WORKFLOWS = frozenset(
    {
        "NATIVE_DEVELOPMENT_INTENT_ROUTING",
        "NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION",
        "CREATE_DOMAIN_TRADING",
        "CREATE_DOMAIN_MARKETING",
    }
)
OCS_WORKFLOWS = frozenset({"OCS_LLM_COGNITION"})


def record_universal_intake(
    *,
    intake_id: str,
    turn_id: str,
    prompt_id: str,
    human_prompt: str,
    chain_id: str,
    workflow_id: str,
    routing_visibility_artifact: dict[str, Any],
    routing_visibility_replay_reference: str,
    source_router_replay_reference: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Record a passive universal intake artifact without invoking downstream authority."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        routing = deepcopy(routing_visibility_artifact)
        _validate_routing_visibility(routing)
        classification = _classify_workflow(workflow_id)
        artifact = _artifact(
            intake_id=intake_id,
            turn_id=turn_id,
            prompt_id=prompt_id,
            human_prompt=human_prompt,
            chain_id=chain_id,
            workflow_id=workflow_id,
            classification=classification,
            routing_visibility_artifact=routing,
            routing_visibility_replay_reference=routing_visibility_replay_reference,
            source_router_replay_reference=source_router_replay_reference,
            created_at=created_at,
            replay_reference=str(replay_path),
            intake_status=UNIVERSAL_INTAKE_RECORDED,
            failure_reason=None,
        )
        _persist_step(replay_path, artifact)
        return _capture(artifact, replay_path)
    except Exception as exc:
        artifact = _failed_artifact(
            intake_id=intake_id,
            turn_id=turn_id,
            prompt_id=prompt_id,
            human_prompt=human_prompt,
            chain_id=chain_id,
            workflow_id=workflow_id,
            created_at=created_at,
            replay_reference=str(replay_path),
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, artifact)
        return _capture(artifact, replay_path)


def reconstruct_universal_intake_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct universal intake replay evidence."""

    replay_path = Path(replay_dir)
    wrapper = load_json(replay_path / f"000_{REPLAY_STEP}.json")
    if wrapper.get("replay_index") != 0 or wrapper.get("replay_step") != REPLAY_STEP:
        raise FailClosedRuntimeError("universal intake replay ordering mismatch")
    _verify_wrapper_hash(wrapper)
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("universal intake artifact must be a JSON object")
    _verify_artifact_hash(artifact)
    if artifact.get("artifact_type") != UNIVERSAL_INTAKE_ARTIFACT_V1:
        raise FailClosedRuntimeError("universal intake artifact type mismatch")
    return {
        "universal_intake_id": artifact["universal_intake_id"],
        "intake_status": artifact["intake_status"],
        "chain_id": artifact["chain_id"],
        "prompt_reference": artifact["prompt_reference"],
        "human_prompt_hash": artifact["human_prompt_hash"],
        "intake_classification": artifact["intake_classification"],
        "cognition_required": artifact["cognition_required"],
        "provider_necessity": artifact["provider_necessity"],
        "domain_reference": artifact["domain_reference"],
        "worker_family_reference": artifact["worker_family_reference"],
        "approval_status": artifact["approval_status"],
        "next_backbone_target": artifact["next_backbone_target"],
        "source_workflow_id": artifact["source_workflow_id"],
        "source_router_replay_reference": artifact["source_router_replay_reference"],
        "routing_visibility_replay_reference": artifact["routing_visibility_replay_reference"],
        "source_intake_replay_reference": artifact["source_intake_replay_reference"],
        "provider_invoked": artifact["provider_invoked"],
        "worker_invoked": artifact["worker_invoked"],
        "approval_created": artifact["approval_created"],
        "ppp_artifact_mutated": artifact["ppp_artifact_mutated"],
        "governance_mutated": artifact["governance_mutated"],
        "replay_visible": True,
        "fail_closed": artifact["fail_closed"],
        "failure_reason": artifact["failure_reason"],
        "replay_hash": replay_hash(wrapper),
    }


def _classify_workflow(workflow_id: str) -> dict[str, Any]:
    workflow = _require_string(workflow_id, "workflow_id")
    if workflow in DOMAIN_WORKFLOWS:
        return {
            "intake_classification": DOMAIN_INTAKE,
            "cognition_required": False,
            "provider_necessity": "PROVIDER_NOT_REQUIRED",
            "domain_reference": "PENDING_DOMAIN_INTAKE",
            "worker_family_reference": "PENDING_DOMAIN_WORKER_BINDING",
            "approval_status": "PENDING_OR_NOT_REQUIRED",
            "next_backbone_target": "CLARIFICATION"
            if workflow == "CREATE_DOMAIN_COMPLIANCE_CLARIFICATION"
            else "WORKER_LIFECYCLE",
        }
    if workflow in NATIVE_DEVELOPMENT_WORKFLOWS:
        return {
            "intake_classification": NATIVE_DEVELOPMENT_INTAKE,
            "cognition_required": False,
            "provider_necessity": "UNKNOWN_PENDING_INTAKE",
            "domain_reference": "PENDING_DEVELOPMENT_CONTEXT",
            "worker_family_reference": "PENDING_DEVELOPMENT_CONTEXT",
            "approval_status": "PENDING_OR_NOT_REQUIRED",
            "next_backbone_target": "PPP_ROUTING",
        }
    if workflow in OCS_WORKFLOWS:
        return {
            "intake_classification": OCS_COGNITION_INTAKE,
            "cognition_required": True,
            "provider_necessity": "PROVIDER_REQUIRED_FOR_COGNITION",
            "domain_reference": "PENDING_OCS_SEMANTIC_RESOLUTION",
            "worker_family_reference": "PENDING_OCS_SEMANTIC_RESOLUTION",
            "approval_status": "NOT_REQUIRED_FOR_COGNITION",
            "next_backbone_target": "OCS_COGNITION",
        }
    return {
        "intake_classification": INTAKE_NOT_APPLICABLE,
        "cognition_required": False,
        "provider_necessity": "NOT_EVALUATED",
        "domain_reference": None,
        "worker_family_reference": None,
        "approval_status": "NOT_EVALUATED",
        "next_backbone_target": "REPLAY_ONLY",
    }


def _artifact(
    *,
    intake_id: str,
    turn_id: str,
    prompt_id: str,
    human_prompt: str,
    chain_id: str,
    workflow_id: str,
    classification: dict[str, Any],
    routing_visibility_artifact: dict[str, Any],
    routing_visibility_replay_reference: str,
    source_router_replay_reference: str,
    created_at: str,
    replay_reference: str,
    intake_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": UNIVERSAL_INTAKE_ARTIFACT_V1,
        "runtime_version": AIGOL_UNIVERSAL_INTAKE_LAYER_RUNTIME_VERSION,
        "universal_intake_id": _require_string(intake_id, "intake_id"),
        "turn_id": _require_string(turn_id, "turn_id"),
        "chain_id": _require_string(chain_id, "chain_id"),
        "prompt_reference": _require_string(prompt_id, "prompt_id"),
        "human_prompt_hash": replay_hash(_require_string(human_prompt, "human_prompt")),
        "intake_classification": classification["intake_classification"],
        "cognition_required": classification["cognition_required"],
        "provider_necessity": classification["provider_necessity"],
        "domain_reference": classification["domain_reference"],
        "worker_family_reference": classification["worker_family_reference"],
        "approval_status": classification["approval_status"],
        "next_backbone_target": classification["next_backbone_target"],
        "source_workflow_id": _require_string(workflow_id, "workflow_id"),
        "source_workflow_hash": replay_hash(workflow_id),
        "routing_visibility_reference": routing_visibility_artifact["routing_visibility_id"],
        "routing_visibility_hash": routing_visibility_artifact["artifact_hash"],
        "routing_visibility_replay_reference": _require_string(
            routing_visibility_replay_reference,
            "routing_visibility_replay_reference",
        ),
        "source_router_replay_reference": _require_string(
            source_router_replay_reference,
            "source_router_replay_reference",
        ),
        "source_intake_replay_reference": None,
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "intake_status": intake_status,
        "replay_visible": True,
        "visibility_only": True,
        "authority_granted": False,
        "provider_authority": False,
        "worker_authority": False,
        "approval_authority": False,
        "execution_authority": False,
        "ppp_authority": False,
        "governance_authority": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "ppp_artifact_mutated": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "fail_closed": intake_status == FAILED_CLOSED,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_artifact(
    *,
    intake_id: str,
    turn_id: str,
    prompt_id: str,
    human_prompt: str,
    chain_id: str,
    workflow_id: str,
    created_at: str,
    replay_reference: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": UNIVERSAL_INTAKE_ARTIFACT_V1,
        "runtime_version": AIGOL_UNIVERSAL_INTAKE_LAYER_RUNTIME_VERSION,
        "universal_intake_id": str(intake_id or "UNIVERSAL_INTAKE_FAILED_CLOSED"),
        "turn_id": str(turn_id or "TURN_UNKNOWN"),
        "chain_id": str(chain_id or "CHAIN_UNKNOWN"),
        "prompt_reference": str(prompt_id or "PROMPT_UNKNOWN"),
        "human_prompt_hash": replay_hash(str(human_prompt or "")),
        "intake_classification": INTAKE_NOT_APPLICABLE,
        "cognition_required": False,
        "provider_necessity": "NOT_EVALUATED",
        "domain_reference": None,
        "worker_family_reference": None,
        "approval_status": "FAILED_CLOSED",
        "next_backbone_target": "REPLAY_ONLY",
        "source_workflow_id": str(workflow_id or "UNKNOWN_WORKFLOW"),
        "source_workflow_hash": replay_hash(str(workflow_id or "UNKNOWN_WORKFLOW")),
        "routing_visibility_reference": None,
        "routing_visibility_hash": None,
        "routing_visibility_replay_reference": None,
        "source_router_replay_reference": None,
        "source_intake_replay_reference": None,
        "created_at": str(created_at or "UNKNOWN_CREATED_AT"),
        "replay_reference": str(replay_reference or ""),
        "intake_status": FAILED_CLOSED,
        "replay_visible": True,
        "visibility_only": True,
        "authority_granted": False,
        "provider_authority": False,
        "worker_authority": False,
        "approval_authority": False,
        "execution_authority": False,
        "ppp_authority": False,
        "governance_authority": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "ppp_artifact_mutated": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "fail_closed": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(artifact: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    return {
        "universal_intake_artifact": deepcopy(artifact),
        "universal_intake_replay_reference": str(replay_path),
        "intake_status": artifact["intake_status"],
        "intake_classification": artifact["intake_classification"],
        "cognition_required": artifact["cognition_required"],
        "provider_necessity": artifact["provider_necessity"],
        "domain_reference": artifact["domain_reference"],
        "worker_family_reference": artifact["worker_family_reference"],
        "approval_status": artifact["approval_status"],
        "next_backbone_target": artifact["next_backbone_target"],
        "source_workflow_id": artifact["source_workflow_id"],
        "fail_closed": artifact["fail_closed"],
        "failure_reason": artifact["failure_reason"],
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "ppp_artifact_mutated": False,
        "governance_mutated": False,
        "replay_visible": True,
    }


def _validate_routing_visibility(artifact: dict[str, Any]) -> None:
    if artifact.get("artifact_type") != "CONVERSATIONAL_ROUTING_VISIBILITY_ARTIFACT_V1":
        raise FailClosedRuntimeError("universal intake failed closed: invalid routing visibility artifact")
    if artifact.get("replay_visible") is not True:
        raise FailClosedRuntimeError("universal intake failed closed: routing visibility is not replay-visible")
    _verify_artifact_hash(artifact)


def _ensure_replay_available(replay_path: Path) -> None:
    path = replay_path / f"000_{REPLAY_STEP}.json"
    if path.exists():
        raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_path: Path, artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact)
    wrapper = {
        "replay_index": 0,
        "replay_step": REPLAY_STEP,
        "event_type": UNIVERSAL_INTAKE_ARTIFACT_V1,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"000_{REPLAY_STEP}.json", wrapper)


def _persist_failure_if_possible(replay_path: Path, artifact: dict[str, Any]) -> None:
    try:
        _persist_step(replay_path, artifact)
    except Exception:
        return


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"universal intake {field_name} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "universal intake failed closed"


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    candidate = deepcopy(artifact)
    actual = candidate.pop("artifact_hash", None)
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("universal intake artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    candidate = deepcopy(wrapper)
    actual = candidate.pop("replay_hash", None)
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("universal intake replay hash mismatch")
