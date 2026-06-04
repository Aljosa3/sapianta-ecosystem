"""Conversation entry routing for native-development intents."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_CONVERSATION_NATIVE_DEVELOPMENT_INTENT_ROUTING_VERSION = (
    "AIGOL_CONVERSATION_NATIVE_DEVELOPMENT_INTENT_ROUTING_V1"
)
NATIVE_DEVELOPMENT_INTENT_ROUTING_EVIDENCE_V1 = "NATIVE_DEVELOPMENT_INTENT_ROUTING_EVIDENCE_V1"
NATIVE_DEVELOPMENT_INTENT_ROUTING_CLASSIFICATION_V1 = "NATIVE_DEVELOPMENT_INTENT_ROUTING_CLASSIFICATION_V1"
NATIVE_DEVELOPMENT_INTENT_ROUTED_ARTIFACT_V1 = "NATIVE_DEVELOPMENT_INTENT_ROUTED_ARTIFACT_V1"
NATIVE_DEVELOPMENT_INTENT_ROUTED = "NATIVE_DEVELOPMENT_INTENT_ROUTED"
CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"
FAILED_CLOSED = "FAILED_CLOSED"

CREATE_DOMAIN = "CREATE_DOMAIN"
CREATE_WORKER = "CREATE_WORKER"
MODIFY_WORKER = "MODIFY_WORKER"
ADD_PROVIDER = "ADD_PROVIDER"
MODIFY_PROVIDER = "MODIFY_PROVIDER"
IMPROVE_EXISTING_CAPABILITY = "IMPROVE_EXISTING_CAPABILITY"
GOVERNANCE_CHANGE = "GOVERNANCE_CHANGE"
REPLAY_DERIVED_IMPROVEMENT = "REPLAY_DERIVED_IMPROVEMENT"

REPLAY_STEPS = (
    "native_development_intent_routing_evidence_recorded",
    "native_development_intent_routing_classification_recorded",
    "native_development_intent_routed_recorded",
    "native_development_intent_routing_returned",
)


def is_conversation_native_development_intent(human_prompt: str) -> bool:
    """Return whether a prompt can be deterministically classified as native development intent."""

    try:
        return _classify_intent(human_prompt)["routing_decision"] == NATIVE_DEVELOPMENT_INTENT_ROUTED
    except FailClosedRuntimeError:
        return False


def run_conversation_native_development_intent_routing(
    *,
    routing_id: str,
    prompt_id: str,
    human_prompt: str,
    canonical_chain_id: str,
    turn_allocation_evidence: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Classify and route conversation prompts into native-development intent without execution authority."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        analysis = _classify_intent(human_prompt)
        if analysis["routing_decision"] != NATIVE_DEVELOPMENT_INTENT_ROUTED:
            raise FailClosedRuntimeError(
                "conversation native development intent routing failed closed: intent requires clarification"
            )
        evidence = _evidence_artifact(
            routing_id=routing_id,
            prompt_id=prompt_id,
            human_prompt=human_prompt,
            canonical_chain_id=canonical_chain_id,
            turn_allocation_evidence=turn_allocation_evidence,
            created_at=created_at,
            replay_reference=str(replay_path),
            failure_reason=None,
        )
        classification = _classification_artifact(
            routing_id=routing_id,
            evidence=evidence,
            analysis=analysis,
            created_at=created_at,
            failure_reason=None,
        )
        routed = _routed_artifact(
            routing_id=routing_id,
            evidence=evidence,
            classification=classification,
            analysis=analysis,
            created_at=created_at,
            replay_reference=str(replay_path),
            routing_status=NATIVE_DEVELOPMENT_INTENT_ROUTED,
            failure_reason=None,
        )
        returned = _returned_artifact(routed)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], evidence)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], classification)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], routed)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], returned)
        return _capture(evidence, classification, routed, returned, replay_path)
    except Exception as exc:
        failure_reason = _failure_reason(exc)
        evidence = _failed_evidence_artifact(
            routing_id=routing_id,
            prompt_id=prompt_id,
            human_prompt=human_prompt,
            canonical_chain_id=canonical_chain_id,
            turn_allocation_evidence=turn_allocation_evidence,
            created_at=created_at,
            replay_reference=str(replay_path),
            failure_reason=failure_reason,
        )
        classification = _failed_classification_artifact(
            routing_id=routing_id,
            evidence=evidence,
            created_at=created_at,
            failure_reason=failure_reason,
        )
        routed = _failed_routed_artifact(
            routing_id=routing_id,
            evidence=evidence,
            classification=classification,
            created_at=created_at,
            replay_reference=str(replay_path),
            failure_reason=failure_reason,
        )
        returned = _returned_artifact(routed)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], evidence)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], classification)
        _persist_failure_if_possible(replay_path, 2, REPLAY_STEPS[2], routed)
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], returned)
        return _capture(evidence, classification, routed, returned, replay_path)


def reconstruct_conversation_native_development_intent_routing_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct native-development intent routing replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("conversation native development intent routing replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("conversation native development intent routing artifact must be an object")
        _verify_artifact_hash(artifact, "conversation native development intent routing artifact")
        wrappers.append(wrapper)
    evidence = wrappers[0]["artifact"]
    classification = wrappers[1]["artifact"]
    routed = wrappers[2]["artifact"]
    returned = wrappers[3]["artifact"]
    if classification.get("routing_evidence_reference") != evidence["routing_evidence_id"]:
        raise FailClosedRuntimeError("conversation native development intent routing evidence reference mismatch")
    if classification.get("routing_evidence_hash") != evidence["artifact_hash"]:
        raise FailClosedRuntimeError("conversation native development intent routing evidence hash mismatch")
    if routed.get("routing_classification_reference") != classification["routing_classification_id"]:
        raise FailClosedRuntimeError("conversation native development intent routing classification reference mismatch")
    if routed.get("routing_classification_hash") != classification["artifact_hash"]:
        raise FailClosedRuntimeError("conversation native development intent routing classification hash mismatch")
    if returned.get("routed_intent_reference") != routed["routed_intent_id"]:
        raise FailClosedRuntimeError("conversation native development intent routing returned reference mismatch")
    return {
        "routed_intent_id": routed["routed_intent_id"],
        "routing_status": routed["routing_status"],
        "intent_class": routed["intent_class"],
        "target_domain": routed["target_domain"],
        "target_resource": routed["target_resource"],
        "canonical_chain_id": routed["canonical_chain_id"],
        "turn_id": evidence["turn_id"],
        "turn_allocation_hash": evidence["turn_allocation_hash"],
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "authorization_created": False,
        "failure_reason": routed["failure_reason"],
    }


def render_native_development_intent_routing_summary(capture: dict[str, Any]) -> str:
    lines = [
        f"native_development_intent_routing_status: {capture.get('routing_status')}",
        f"intent_class: {capture.get('intent_class')}",
        f"target_domain: {capture.get('target_domain')}",
        f"target_resource: {capture.get('target_resource')}",
        f"target_provider: {capture.get('target_provider')}",
        f"target_worker_family: {capture.get('target_worker_family')}",
        f"canonical_chain_id: {capture.get('canonical_chain_id')}",
        f"next_pipeline_stage: {capture.get('next_pipeline_stage')}",
        f"replay_reference: {capture.get('native_development_intent_routing_replay_reference')}",
    ]
    if capture.get("failure_reason"):
        lines.append(f"failure_reason: {capture['failure_reason']}")
    return "\n".join(lines)


def _classify_intent(human_prompt: str) -> dict[str, Any]:
    prompt = _require_string(human_prompt, "human_prompt")
    normalized = prompt.lower().strip().rstrip(".")
    rules = (
        (
            CREATE_DOMAIN,
            ("create", "marketing", "domain"),
            {
                "target_domain": "MARKETING",
                "target_resource": "DOMAIN",
                "target_provider": None,
                "target_worker_family": None,
                "target_milestone": "MARKETING_DOMAIN_FOUNDATION_V1",
                "target_capability": "DOMAIN_FOUNDATION",
            },
        ),
        (
            CREATE_WORKER,
            ("create", "sentiment", "analysis", "worker"),
            {
                "target_domain": "MARKETING",
                "target_resource": "WORKER",
                "target_provider": None,
                "target_worker_family": "SENTIMENT_ANALYSIS",
                "target_milestone": "MARKETING_SENTIMENT_ANALYSIS_WORKER_FOUNDATION_V1",
                "target_capability": "SENTIMENT_ANALYSIS",
            },
        ),
        (
            CREATE_WORKER,
            ("create", "trading", "worker"),
            {
                "target_domain": "TRADING",
                "target_resource": "WORKER",
                "target_provider": None,
                "target_worker_family": "TRADING_WORKER",
                "target_milestone": "TRADING_WORKER_FOUNDATION_V1",
                "target_capability": "TRADING_DOMAIN_WORK",
            },
        ),
        (
            ADD_PROVIDER,
            ("add", "provider", "anthropic"),
            {
                "target_domain": "AIGOL_CORE",
                "target_resource": "PROVIDER",
                "target_provider": "ANTHROPIC",
                "target_worker_family": None,
                "target_milestone": "AIGOL_PROVIDER_ANTHROPIC_ATTACHMENT_V1",
                "target_capability": "PROVIDER_ECOSYSTEM",
            },
        ),
        (
            IMPROVE_EXISTING_CAPABILITY,
            ("improve", "trading", "strategy"),
            {
                "target_domain": "TRADING",
                "target_resource": "CAPABILITY",
                "target_provider": None,
                "target_worker_family": "STRATEGY_ANALYSIS",
                "target_milestone": "TRADING_STRATEGY_IMPROVEMENT_CAPABILITY_V1",
                "target_capability": "STRATEGY_IMPROVEMENT",
            },
        ),
        (
            MODIFY_WORKER,
            ("upgrade", "replay", "subsystem"),
            {
                "target_domain": "AIGOL_CORE",
                "target_resource": "REPLAY_SUBSYSTEM",
                "target_provider": None,
                "target_worker_family": "REPLAY",
                "target_milestone": "AIGOL_REPLAY_SUBSYSTEM_UPGRADE_V1",
                "target_capability": "REPLAY_CONTINUITY",
            },
        ),
        (
            GOVERNANCE_CHANGE,
            ("add", "governance", "policy"),
            {
                "target_domain": "GOVERNANCE",
                "target_resource": "GOVERNANCE_POLICY",
                "target_provider": None,
                "target_worker_family": None,
                "target_milestone": "AIGOL_GOVERNANCE_POLICY_ADDITION_V1",
                "target_capability": "GOVERNANCE_POLICY",
            },
        ),
    )
    matches = []
    for intent_class, required_terms, details in rules:
        if all(term in normalized for term in required_terms):
            matches.append((intent_class, details))
    if len(matches) != 1:
        if "workstation" in normalized:
            return {"routing_decision": CLARIFICATION_REQUIRED}
        raise FailClosedRuntimeError("conversation native development intent routing failed closed: intent cannot be classified")
    intent_class, details = matches[0]
    return {
        "routing_decision": NATIVE_DEVELOPMENT_INTENT_ROUTED,
        "intent_class": intent_class,
        "confidence": "HIGH",
        "next_pipeline_stage": "NATIVE_DEVELOPMENT_INTAKE",
        **details,
    }


def _evidence_artifact(
    *,
    routing_id: str,
    prompt_id: str,
    human_prompt: str,
    canonical_chain_id: str,
    turn_allocation_evidence: dict[str, Any],
    created_at: str,
    replay_reference: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    _validate_turn_allocation(prompt_id, turn_allocation_evidence)
    artifact = {
        "artifact_type": NATIVE_DEVELOPMENT_INTENT_ROUTING_EVIDENCE_V1,
        "runtime_version": AIGOL_CONVERSATION_NATIVE_DEVELOPMENT_INTENT_ROUTING_VERSION,
        "routing_evidence_id": f"{_require_string(routing_id, 'routing_id')}:EVIDENCE",
        "prompt_id": _require_string(prompt_id, "prompt_id"),
        "human_prompt_hash": replay_hash(_require_string(human_prompt, "human_prompt")),
        "canonical_chain_id": _require_string(canonical_chain_id, "canonical_chain_id"),
        "turn_id": turn_allocation_evidence["next_turn_id"],
        "turn_allocation_hash": turn_allocation_evidence["artifact_hash"],
        "turn_allocation_status": turn_allocation_evidence["resume_status"],
        "turn_allocation_valid": True,
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_mutated": False,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _classification_artifact(
    *,
    routing_id: str,
    evidence: dict[str, Any],
    analysis: dict[str, Any],
    created_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": NATIVE_DEVELOPMENT_INTENT_ROUTING_CLASSIFICATION_V1,
        "runtime_version": AIGOL_CONVERSATION_NATIVE_DEVELOPMENT_INTENT_ROUTING_VERSION,
        "routing_classification_id": f"{_require_string(routing_id, 'routing_id')}:CLASSIFICATION",
        "routing_evidence_reference": evidence["routing_evidence_id"],
        "routing_evidence_hash": evidence["artifact_hash"],
        "canonical_chain_id": evidence["canonical_chain_id"],
        "routing_decision": analysis["routing_decision"],
        "intent_class": analysis.get("intent_class"),
        "confidence": analysis.get("confidence"),
        "target_domain": analysis.get("target_domain"),
        "target_resource": analysis.get("target_resource"),
        "target_provider": analysis.get("target_provider"),
        "target_worker_family": analysis.get("target_worker_family"),
        "target_milestone": analysis.get("target_milestone"),
        "target_capability": analysis.get("target_capability"),
        "next_pipeline_stage": analysis.get("next_pipeline_stage"),
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_mutated": False,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _routed_artifact(
    *,
    routing_id: str,
    evidence: dict[str, Any],
    classification: dict[str, Any],
    analysis: dict[str, Any],
    created_at: str,
    replay_reference: str,
    routing_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": NATIVE_DEVELOPMENT_INTENT_ROUTED_ARTIFACT_V1,
        "runtime_version": AIGOL_CONVERSATION_NATIVE_DEVELOPMENT_INTENT_ROUTING_VERSION,
        "routed_intent_id": f"{_require_string(routing_id, 'routing_id')}:ROUTED",
        "routing_evidence_reference": evidence["routing_evidence_id"],
        "routing_evidence_hash": evidence["artifact_hash"],
        "routing_classification_reference": classification["routing_classification_id"],
        "routing_classification_hash": classification["artifact_hash"],
        "canonical_chain_id": evidence["canonical_chain_id"],
        "routing_status": routing_status,
        "intent_class": analysis.get("intent_class"),
        "confidence": analysis.get("confidence"),
        "target_domain": analysis.get("target_domain"),
        "target_resource": analysis.get("target_resource"),
        "target_provider": analysis.get("target_provider"),
        "target_worker_family": analysis.get("target_worker_family"),
        "target_milestone": analysis.get("target_milestone"),
        "target_capability": analysis.get("target_capability"),
        "next_pipeline_stage": analysis.get("next_pipeline_stage"),
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_mutated": False,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(routed: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(routed, "conversation native development intent routed artifact")
    artifact = {
        "event_type": "CONVERSATION_NATIVE_DEVELOPMENT_INTENT_ROUTING_RETURNED",
        "routed_intent_reference": routed["routed_intent_id"],
        "routed_intent_hash": routed["artifact_hash"],
        "routing_status": routed["routing_status"],
        "intent_class": routed["intent_class"],
        "target_domain": routed["target_domain"],
        "target_resource": routed["target_resource"],
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "failure_reason": routed["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_evidence_artifact(**kwargs: Any) -> dict[str, Any]:
    artifact = {
        "artifact_type": NATIVE_DEVELOPMENT_INTENT_ROUTING_EVIDENCE_V1,
        "runtime_version": AIGOL_CONVERSATION_NATIVE_DEVELOPMENT_INTENT_ROUTING_VERSION,
        "routing_evidence_id": f"{kwargs.get('routing_id')}:EVIDENCE",
        "prompt_id": kwargs.get("prompt_id") if isinstance(kwargs.get("prompt_id"), str) else None,
        "human_prompt_hash": replay_hash(kwargs.get("human_prompt")) if isinstance(kwargs.get("human_prompt"), str) else None,
        "canonical_chain_id": kwargs.get("canonical_chain_id") if isinstance(kwargs.get("canonical_chain_id"), str) else None,
        "turn_id": kwargs.get("turn_allocation_evidence", {}).get("next_turn_id")
        if isinstance(kwargs.get("turn_allocation_evidence"), dict)
        else None,
        "turn_allocation_hash": kwargs.get("turn_allocation_evidence", {}).get("artifact_hash")
        if isinstance(kwargs.get("turn_allocation_evidence"), dict)
        else None,
        "turn_allocation_status": kwargs.get("turn_allocation_evidence", {}).get("resume_status")
        if isinstance(kwargs.get("turn_allocation_evidence"), dict)
        else None,
        "turn_allocation_valid": False,
        "created_at": kwargs.get("created_at") if isinstance(kwargs.get("created_at"), str) else "",
        "replay_reference": kwargs.get("replay_reference") if isinstance(kwargs.get("replay_reference"), str) else "",
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_mutated": False,
        "failure_reason": kwargs["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_classification_artifact(*, routing_id: str, evidence: dict[str, Any], created_at: str, failure_reason: str) -> dict[str, Any]:
    return _classification_artifact(
        routing_id=routing_id,
        evidence=evidence,
        analysis={"routing_decision": FAILED_CLOSED},
        created_at=created_at,
        failure_reason=failure_reason,
    )


def _failed_routed_artifact(
    *,
    routing_id: str,
    evidence: dict[str, Any],
    classification: dict[str, Any],
    created_at: str,
    replay_reference: str,
    failure_reason: str,
) -> dict[str, Any]:
    return _routed_artifact(
        routing_id=routing_id,
        evidence=evidence,
        classification=classification,
        analysis={"routing_decision": FAILED_CLOSED},
        created_at=created_at,
        replay_reference=replay_reference,
        routing_status=FAILED_CLOSED,
        failure_reason=failure_reason,
    )


def _capture(
    evidence: dict[str, Any],
    classification: dict[str, Any],
    routed: dict[str, Any],
    returned: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "native_development_intent_routing_evidence_artifact": deepcopy(evidence),
        "native_development_intent_routing_classification_artifact": deepcopy(classification),
        "native_development_intent_routed_artifact": deepcopy(routed),
        "native_development_intent_routing_replay": deepcopy(returned),
        "native_development_intent_routing_replay_reference": str(replay_path),
        "response_status": routed["routing_status"],
        "response_source": "NATIVE_DEVELOPMENT_INTENT_ROUTING",
        "routing_status": routed["routing_status"],
        "intent_class": routed["intent_class"],
        "target_domain": routed["target_domain"],
        "target_resource": routed["target_resource"],
        "target_provider": routed["target_provider"],
        "target_worker_family": routed["target_worker_family"],
        "target_milestone": routed["target_milestone"],
        "target_capability": routed["target_capability"],
        "next_pipeline_stage": routed["next_pipeline_stage"],
        "canonical_chain_id": routed["canonical_chain_id"],
        "current_chain_id": routed["canonical_chain_id"],
        "latest_chain_id": routed["canonical_chain_id"],
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "fail_closed": routed["routing_status"] == FAILED_CLOSED,
        "failure_reason": routed["failure_reason"],
    }
    capture["conversation_native_development_intent_routing_capture_hash"] = replay_hash(capture)
    return capture


def _validate_turn_allocation(prompt_id: str, turn_allocation: dict[str, Any]) -> None:
    if not isinstance(turn_allocation, dict):
        raise FailClosedRuntimeError("conversation native development intent routing failed closed: turn allocation invalid")
    _verify_artifact_hash(turn_allocation, "conversation turn allocation artifact")
    turn_id = _require_string(turn_allocation.get("next_turn_id"), "turn_id")
    if not _require_string(prompt_id, "prompt_id").endswith(turn_id):
        raise FailClosedRuntimeError("conversation native development intent routing failed closed: turn allocation invalid")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("conversation native development intent routing replay step ordering mismatch")
    _verify_artifact_hash(artifact, "conversation native development intent routing artifact")
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


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {step}")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError(f"{label} hash is required")
    expected = deepcopy(artifact)
    actual = expected.pop("artifact_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("conversation native development intent routing replay hash is required")
    expected = deepcopy(wrapper)
    actual = expected.pop("replay_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("conversation native development intent routing replay hash mismatch")


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"conversation native development intent routing failed closed: {label} missing")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "conversation native development intent routing failed closed"
