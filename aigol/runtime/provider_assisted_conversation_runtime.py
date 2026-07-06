"""Provider-assisted conversation runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.provider.provider_adapter import ProviderAdapter
from aigol.provider.provider_registry import ProviderRegistry
from aigol.provider.certified_provider_attachment import run_certified_provider_attachment
from aigol.provider.provider_runtime import PROVIDER_PROPOSAL_RETURNED, reconstruct_provider_attachment_replay
from aigol.runtime.intent_classifier import CLASSIFIED, CONVERSATION
from aigol.runtime.intent_routing_attachment import (
    ROUTED,
    attach_intent_routing,
    reconstruct_intent_routing_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_assisted_intent_classification import (
    classify_intent_with_provider_assistance,
    reconstruct_provider_assisted_intent_classification_replay,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


PROVIDER_ASSISTED_CONVERSATION_RUNTIME_VERSION = "PROVIDER_ASSISTED_CONVERSATION_RUNTIME_V1"
CONVERSATION_RESPONSE_TYPE = "PROVIDER_ASSISTED_CONVERSATION_RESPONSE"
STARTED = "PROVIDER_ASSISTED_CONVERSATION_STARTED"
SELF_RESOLUTION_ATTEMPTED = "CONVERSATION_SELF_RESOLUTION_ATTEMPTED"
VALIDATED = "PROVIDER_CONVERSATION_RESPONSE_VALIDATED"
CREATED = "PROVIDER_ASSISTED_CONVERSATION_RESPONSE_CREATED"
RETURNED = "PROVIDER_ASSISTED_CONVERSATION_RESPONSE_RETURNED"
FAILED_CLOSED = "FAILED_CLOSED"
NORMALIZED_CONFIDENCE = "PROVIDER_TEXT_NORMALIZED"
VALID_CONFIDENCE_VALUES = frozenset({"LOW", "MEDIUM", "HIGH", "DETERMINISTIC", NORMALIZED_CONFIDENCE})
MINIMAL_PROVIDER_CONTEXT_CAPSULE_VERSION = "MINIMAL_PROVIDER_CONTEXT_CAPSULE_V1"
MINIMAL_PROVIDER_CONTEXT_CAPSULE_LINES = (
    "AiGOL is a constitutional AI execution governance system.",
    "LLM providers are proposal-only sources; they do not govern, authorize, execute, mutate replay, or invoke workers.",
    "AiGOL governs; workers execute only after governed authorization; replay records evidence.",
    "Answer in the AiGOL/SAPIANTA governance domain unless the user explicitly asks for another domain.",
    "Use the human prompt as the question; provide explanatory text only.",
)

REPLAY_STEPS = (
    "provider_assisted_conversation_started",
    "conversation_self_resolution_attempted",
    "provider_conversation_response_validation",
    "provider_assisted_conversation_response_created",
    "provider_assisted_conversation_response_returned",
)

FORBIDDEN_RESPONSE_FIELDS = frozenset(
    {
        "authorization_decision",
        "governance_decision",
        "execution_request",
        "dispatch_request",
        "worker_request",
        "worker_instruction",
        "provider_command",
        "worker_command",
        "memory_mutation",
        "replay_mutation",
    }
)


def run_provider_assisted_conversation(
    *,
    conversation_id: str,
    prompt_id: str,
    human_prompt: str,
    created_at: str,
    provider_id: str,
    registry: ProviderRegistry,
    adapter: ProviderAdapter,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Return a replay-visible conversation response with provider fallback only when needed."""

    replay_path = Path(replay_dir)
    started: dict[str, Any] | None = None
    try:
        _ensure_replay_available(replay_path)
        prompt = _normalize_text(human_prompt, "human_prompt")
        started = _started_artifact(
            conversation_id=conversation_id,
            prompt_id=prompt_id,
            human_prompt=prompt,
            created_at=created_at,
        )
        _persist_step(replay_path, 0, REPLAY_STEPS[0], started)

        intent_capture = classify_intent_with_provider_assistance(
            artifact_id=f"{conversation_id}:INTENT",
            human_request_reference=prompt_id,
            human_prompt=prompt,
            classification_timestamp=created_at,
            replay_reference=str(replay_path / "intent_classification"),
            replay_dir=replay_path / "intent_classification",
            provider_id=provider_id,
            registry=registry,
            adapter=adapter,
        )
        intent_artifact = intent_capture["intent_classification_artifact"]
        if intent_artifact.get("classification_status") != CLASSIFIED:
            reason = intent_artifact.get("failure_reason") or "intent classification failed"
            raise FailClosedRuntimeError(f"provider-assisted conversation failed closed: {reason}")
        if intent_artifact.get("classification_destination") != CONVERSATION:
            raise FailClosedRuntimeError("provider-assisted conversation failed closed: prompt is not conversation intent")
        routing_capture = attach_intent_routing(
            routing_record_id=f"{conversation_id}:ROUTING",
            intent_classification_artifact=intent_artifact,
            routing_timestamp=created_at,
            replay_reference=str(replay_path / "intent_routing"),
            replay_dir=replay_path / "intent_routing",
        )
        routing_record = routing_capture["intent_routing_attachment_record"]
        if routing_record.get("routing_status") != ROUTED:
            reason = routing_record.get("failure_reason") or "routing failed"
            raise FailClosedRuntimeError(f"provider-assisted conversation failed closed: {reason}")

        self_resolution = _self_resolution_artifact(
            resolution_id=f"{conversation_id}:SELF_RESOLUTION",
            prompt_id=prompt_id,
            human_prompt=prompt,
            intent_artifact=intent_artifact,
            created_at=created_at,
        )
        _persist_step(replay_path, 1, REPLAY_STEPS[1], self_resolution)

        provider_capture: dict[str, Any] | None = None
        if self_resolution["self_resolution_status"] == "RESOLVED":
            validation = _validation_artifact(
                validation_id=f"{conversation_id}:RESPONSE_VALIDATION",
                prompt_id=prompt_id,
                intent_artifact=intent_artifact,
                self_resolution=self_resolution,
                provider_capture=None,
                response_text=self_resolution["response_text"],
                response_reasoning=self_resolution["resolution_reason"],
                confidence="DETERMINISTIC",
                validation_status=VALIDATED,
                provider_assistance_required=False,
                validation_reason="deterministic self-resolution succeeded; provider response not requested",
                created_at=created_at,
                failure_reason=None,
            )
        else:
            provider_capture = run_certified_provider_attachment(
                provider_id=provider_id,
                request=_provider_response_request(
                    prompt_id=prompt_id,
                    human_prompt=prompt,
                    intent_artifact=intent_artifact,
                    self_resolution=self_resolution,
                ),
                proposal_id=f"{conversation_id}:PROVIDER_CONVERSATION_RESPONSE",
                timestamp=created_at,
                registry=registry,
                adapter=adapter,
                replay_dir=replay_path / "provider_conversation_response",
            )
            suggestion = _extract_provider_response_suggestion(provider_capture)
            validation = _validation_artifact(
                validation_id=f"{conversation_id}:RESPONSE_VALIDATION",
                prompt_id=prompt_id,
                intent_artifact=intent_artifact,
                self_resolution=self_resolution,
                provider_capture=provider_capture,
                response_text=suggestion["suggested_response_text"],
                response_reasoning=suggestion["response_reasoning"],
                confidence=suggestion["confidence"],
                validation_status=VALIDATED,
                provider_assistance_required=True,
                validation_reason="provider conversational response suggestion validated by AiGOL",
                created_at=created_at,
                failure_reason=None,
            )
        _persist_step(replay_path, 2, REPLAY_STEPS[2], validation)

        response = _response_artifact(
            response_id=f"{conversation_id}:RESPONSE",
            conversation_id=conversation_id,
            prompt_id=prompt_id,
            intent_artifact=intent_artifact,
            validation=validation,
            response_text=validation["response_text"],
            created_at=created_at,
            response_status=CREATED,
            failure_reason=None,
        )
        _persist_step(replay_path, 3, REPLAY_STEPS[3], response)
        returned = _returned_artifact(
            started=started,
            self_resolution=self_resolution,
            validation=validation,
            response=response,
            provider_capture=provider_capture,
            return_status=RETURNED,
            failure_reason=None,
        )
        _persist_step(replay_path, 4, REPLAY_STEPS[4], returned)
        return _capture(started, self_resolution, validation, response, returned, provider_capture)
    except Exception as exc:
        if started is None:
            started = _failed_started_artifact(
                conversation_id=conversation_id,
                prompt_id=prompt_id,
                human_prompt=human_prompt,
                created_at=created_at,
                failure_reason=_failure_reason(exc),
            )
            _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], started)
        self_resolution = locals().get("self_resolution")
        if not isinstance(self_resolution, dict):
            self_resolution = _failed_self_resolution_artifact(
                resolution_id=f"{conversation_id}:SELF_RESOLUTION",
                prompt_id=prompt_id,
                human_prompt=human_prompt,
                created_at=created_at,
                failure_reason=_failure_reason(exc),
            )
            _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], self_resolution)
        provider_capture = locals().get("provider_capture")
        provider_capture = provider_capture if isinstance(provider_capture, dict) else None
        validation = _failed_validation_artifact(
            validation_id=f"{conversation_id}:RESPONSE_VALIDATION",
            prompt_id=prompt_id,
            self_resolution=self_resolution,
            provider_capture=provider_capture,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, 2, REPLAY_STEPS[2], validation)
        response = _failed_response_artifact(
            response_id=f"{conversation_id}:RESPONSE",
            conversation_id=conversation_id,
            prompt_id=prompt_id,
            validation=validation,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], response)
        returned = _returned_artifact(
            started=started,
            self_resolution=self_resolution,
            validation=validation,
            response=response,
            provider_capture=provider_capture,
            return_status=FAILED_CLOSED,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, 4, REPLAY_STEPS[4], returned)
        return _capture(started, self_resolution, validation, response, returned, provider_capture)


def reconstruct_provider_assisted_conversation_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct conversation response replay without invoking provider again."""

    replay_path = Path(replay_dir)
    intent = reconstruct_provider_assisted_intent_classification_replay(replay_path / "intent_classification")
    routing = reconstruct_intent_routing_replay(replay_path / "intent_routing")
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("provider-assisted conversation replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("provider-assisted conversation replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    started = wrappers[0]["artifact"]
    self_resolution = wrappers[1]["artifact"]
    validation = wrappers[2]["artifact"]
    response = wrappers[3]["artifact"]
    returned = wrappers[4]["artifact"]
    if response.get("conversation_id") != started["conversation_id"]:
        raise FailClosedRuntimeError("provider-assisted conversation response reference mismatch")
    if response.get("validation_hash") != validation["artifact_hash"]:
        raise FailClosedRuntimeError("provider-assisted conversation validation hash mismatch")
    if returned.get("response_artifact_hash") != response["artifact_hash"]:
        raise FailClosedRuntimeError("provider-assisted conversation returned hash mismatch")
    provider = None
    if validation["provider_assistance_required"]:
        provider = reconstruct_provider_attachment_replay(replay_path / "provider_conversation_response")
    return {
        "conversation_id": started["conversation_id"],
        "prompt_id": started["prompt_id"],
        "prompt_text": started["prompt_text"],
        "intent_classification": deepcopy(intent),
        "routing_decision": deepcopy(routing),
        "self_resolution_status": self_resolution["self_resolution_status"],
        "provider_assistance_required": validation["provider_assistance_required"],
        "provider_response_replay": deepcopy(provider),
        "response_id": response["response_id"],
        "response_text": response["response_text"],
        "conversation_status": response["conversation_status"],
        "response_type": response["response_type"],
        "authority": False,
        "provider_response_authority": False,
        "worker_invoked": False,
        "execution_requested": False,
        "replay_visible": True,
        "replay_artifact_count": (
            len(wrappers)
            + intent["replay_artifact_count"]
            + routing["replay_artifact_count"]
            + (provider["replay_artifact_count"] if provider else 0)
        ),
        "replay_hash": replay_hash(
            {
                "intent": intent,
                "routing": routing,
                "provider": provider,
                "conversation": wrappers,
            }
        ),
    }


def _self_resolution_artifact(
    *,
    resolution_id: str,
    prompt_id: str,
    human_prompt: str,
    intent_artifact: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    response_text, reason = _deterministic_response(human_prompt)
    status = "RESOLVED" if response_text else "UNRESOLVED"
    artifact = {
        "artifact_id": _require_string(resolution_id, "resolution_id"),
        "artifact_type": "CONVERSATION_SELF_RESOLUTION",
        "prompt_id": _require_string(prompt_id, "prompt_id"),
        "human_prompt_hash": replay_hash({"human_prompt": _normalize_text(human_prompt, "human_prompt")}),
        "intent_artifact_id": intent_artifact["artifact_id"],
        "intent_artifact_hash": intent_artifact["artifact_hash"],
        "self_resolution_sources": [
            "replay_backed_explanations",
            "constitutional_memory",
            "governance_artifacts",
            "deterministic_runtime_knowledge",
        ],
        "self_resolution_status": status,
        "response_text": response_text,
        "resolution_reason": reason,
        "provider_assistance_required": status != "RESOLVED",
        "created_at": _require_string(created_at, "created_at"),
        "authority": False,
        "replay_visible": True,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_self_resolution_artifact(
    *,
    resolution_id: str,
    prompt_id: Any,
    human_prompt: Any,
    created_at: Any,
    failure_reason: str,
) -> dict[str, Any]:
    prompt = human_prompt if isinstance(human_prompt, str) and human_prompt.strip() else "INVALID_PROMPT"
    artifact = {
        "artifact_id": _require_string(resolution_id, "resolution_id"),
        "artifact_type": "CONVERSATION_SELF_RESOLUTION",
        "prompt_id": prompt_id if isinstance(prompt_id, str) and prompt_id.strip() else "INVALID_PROMPT_ID",
        "human_prompt_hash": replay_hash({"human_prompt": " ".join(str(prompt).split())}),
        "intent_artifact_id": None,
        "intent_artifact_hash": None,
        "self_resolution_sources": [],
        "self_resolution_status": FAILED_CLOSED,
        "response_text": "",
        "resolution_reason": "self-resolution failed closed",
        "provider_assistance_required": False,
        "created_at": created_at if isinstance(created_at, str) and created_at.strip() else "INVALID_TIMESTAMP",
        "authority": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _deterministic_response(human_prompt: str) -> tuple[str, str]:
    lowered = human_prompt.lower()
    if "what is aigol" in lowered or "what is aigol?" in lowered:
        return (
            "AiGOL is a governed AI operation path that separates proposal, governance, worker execution, and replay evidence.",
            "matched deterministic AiGOL identity knowledge",
        )
    if "purpose of aigol" in lowered:
        return (
            "The purpose of AiGOL is to make AI-assisted operations governed, replay-visible, fail-closed, and auditable before any worker execution occurs.",
            "matched deterministic AiGOL purpose knowledge",
        )
    if "explain replay" in lowered:
        return (
            "Replay is AiGOL's evidence trail: it records prompts, classifications, routing, proposals, authorization, worker results, and response artifacts so an operator can reconstruct what happened.",
            "matched deterministic replay knowledge",
        )
    if "explain governance" in lowered:
        return (
            "Governance is the AiGOL boundary that validates admissibility, preserves authority separation, fails closed on unresolved states, and prevents providers or prompts from becoming execution authority.",
            "matched deterministic governance knowledge",
        )
    if "how does aigol" in lowered:
        return (
            "AiGOL works by recording a human request, classifying intent, governing admissibility, executing only through authorized workers, and preserving replay evidence.",
            "matched deterministic AiGOL operation knowledge",
        )
    if "what can aigol" in lowered or "what can aigol do" in lowered or "kaj zna aigol" in lowered:
        return (
            "AiGOL can classify prompts, preserve replay evidence, attach proposal-only providers, authorize bounded worker requests, execute governed operations, and explain results from replay.",
            "matched deterministic AiGOL capability knowledge",
        )
    return "", "deterministic self-resolution insufficient"


def _provider_response_request(
    *,
    prompt_id: str,
    human_prompt: str,
    intent_artifact: dict[str, Any],
    self_resolution: dict[str, Any],
) -> dict[str, Any]:
    prompt = _normalize_text(human_prompt, "human_prompt")
    return {
        "semantic_task": "conversation_response_suggestion",
        "prompt_id": _require_string(prompt_id, "prompt_id"),
        "human_prompt": prompt,
        "prompt": _provider_prompt_with_context(prompt),
        "context_capsule": _minimal_provider_context_capsule(),
        "intent_destination": intent_artifact["classification_destination"],
        "self_resolution_status": self_resolution["self_resolution_status"],
        "self_resolution_reason": self_resolution["resolution_reason"],
        "provider_authority": False,
        "response_authority": False,
        "execution_authority": False,
    }


def _minimal_provider_context_capsule() -> dict[str, Any]:
    return {
        "context_capsule_version": MINIMAL_PROVIDER_CONTEXT_CAPSULE_VERSION,
        "context_type": "PROVIDER_NEUTRAL_AIGOL_IDENTITY_CAPSULE",
        "aigol_identity": "AiGOL is a constitutional AI execution governance system.",
        "governance_role": "AiGOL governs provider suggestions and downstream execution admissibility.",
        "provider_authority_boundaries": "LLM providers are proposal-only sources and do not govern, authorize, execute, mutate replay, or invoke workers.",
        "worker_authority_boundaries": "Workers execute only after governed authorization and do not receive authority from providers.",
        "replay_purpose": "Replay records prompts, provider evidence, validation, decisions, and results for reconstruction.",
        "provider_neutral": True,
        "authority_transfer": False,
    }


def _provider_prompt_with_context(human_prompt: str) -> str:
    prompt = _normalize_text(human_prompt, "human_prompt")
    return "\n".join(
        (
            "AiGOL context:",
            *MINIMAL_PROVIDER_CONTEXT_CAPSULE_LINES,
            "",
            "Human prompt:",
            prompt,
        )
    )


def _extract_provider_response_suggestion(provider_capture: dict[str, Any]) -> dict[str, str]:
    returned = provider_capture.get("provider_proposal_returned")
    if not isinstance(returned, dict):
        raise FailClosedRuntimeError("provider conversation response evidence is required")
    if returned.get("event_type") != PROVIDER_PROPOSAL_RETURNED:
        reason = returned.get("failure_reason") or "provider conversation response failed closed"
        raise FailClosedRuntimeError(reason)
    envelope = provider_capture.get("provider_proposal_envelope")
    if not isinstance(envelope, dict):
        raise FailClosedRuntimeError("provider conversation response envelope is required")
    response = envelope.get("response")
    if not isinstance(response, dict):
        raise FailClosedRuntimeError("provider conversation response must be a JSON object")
    if FORBIDDEN_RESPONSE_FIELDS.intersection(response):
        raise FailClosedRuntimeError("provider conversation response contains authority-bearing field")
    if isinstance(response.get("alternate_responses"), list) and response["alternate_responses"]:
        raise FailClosedRuntimeError("provider conversation response is ambiguous")
    suggestion = _aligned_provider_response_contract(response)
    if _looks_authority_bearing(suggestion["suggested_response_text"]):
        raise FailClosedRuntimeError("provider conversation response contains authority-bearing text")
    return suggestion


def _aligned_provider_response_contract(response: dict[str, Any]) -> dict[str, str]:
    """Normalize provider output into the existing conversation response contract.

    Real providers may return a generic proposal envelope with `response_text`.
    AiGOL treats that as provider evidence only and deterministically aligns it
    into the already-required conversation suggestion fields before validation.
    """

    has_structured_fields = any(
        key in response for key in ("suggested_response_text", "response_reasoning", "confidence")
    )
    if has_structured_fields:
        suggestion = {
            "suggested_response_text": _require_string(response.get("suggested_response_text"), "suggested_response_text"),
            "response_reasoning": _require_string(response.get("response_reasoning"), "response_reasoning"),
            "confidence": _require_confidence(response.get("confidence")),
        }
        return suggestion

    response_text = _require_string(response.get("response_text"), "response_text")
    return {
        "suggested_response_text": response_text,
        "response_reasoning": "deterministically aligned from provider response_text",
        "confidence": NORMALIZED_CONFIDENCE,
    }


def _validation_artifact(
    *,
    validation_id: str,
    prompt_id: str,
    intent_artifact: dict[str, Any],
    self_resolution: dict[str, Any],
    provider_capture: dict[str, Any] | None,
    response_text: str,
    response_reasoning: str,
    confidence: str,
    validation_status: str,
    provider_assistance_required: bool,
    validation_reason: str,
    created_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    response_text = _require_string(response_text, "response_text")
    if _looks_authority_bearing(response_text):
        raise FailClosedRuntimeError("conversation response validation failed closed: authority-bearing response")
    artifact = {
        "artifact_id": _require_string(validation_id, "validation_id"),
        "artifact_type": "PROVIDER_ASSISTED_CONVERSATION_RESPONSE_VALIDATION",
        "prompt_id": _require_string(prompt_id, "prompt_id"),
        "intent_artifact_id": intent_artifact["artifact_id"],
        "intent_artifact_hash": intent_artifact["artifact_hash"],
        "self_resolution_hash": self_resolution["artifact_hash"],
        "provider_assistance_required": provider_assistance_required,
        "provider_proposal_hash": _provider_proposal_hash(provider_capture),
        "response_text": response_text,
        "response_reasoning": _require_string(response_reasoning, "response_reasoning"),
        "confidence": _require_string(confidence, "confidence"),
        "validation_status": validation_status,
        "validation_reason": _require_string(validation_reason, "validation_reason"),
        "created_at": _require_string(created_at, "created_at"),
        "provider_response_authority": False,
        "authority": False,
        "execution_requested": False,
        "worker_invoked": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_validation_artifact(
    *,
    validation_id: str,
    prompt_id: Any,
    self_resolution: dict[str, Any],
    provider_capture: dict[str, Any] | None,
    created_at: Any,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_id": _require_string(validation_id, "validation_id"),
        "artifact_type": "PROVIDER_ASSISTED_CONVERSATION_RESPONSE_VALIDATION",
        "prompt_id": prompt_id if isinstance(prompt_id, str) and prompt_id.strip() else "INVALID_PROMPT_ID",
        "intent_artifact_id": None,
        "intent_artifact_hash": None,
        "self_resolution_hash": self_resolution["artifact_hash"],
        "provider_assistance_required": bool(provider_capture),
        "provider_proposal_hash": _provider_proposal_hash(provider_capture),
        "response_text": "",
        "response_reasoning": "provider-assisted conversation failed closed",
        "confidence": FAILED_CLOSED,
        "validation_status": FAILED_CLOSED,
        "validation_reason": "provider-assisted conversation failed closed",
        "created_at": created_at if isinstance(created_at, str) and created_at.strip() else "INVALID_TIMESTAMP",
        "provider_response_authority": False,
        "authority": False,
        "execution_requested": False,
        "worker_invoked": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _response_artifact(
    *,
    response_id: str,
    conversation_id: str,
    prompt_id: str,
    intent_artifact: dict[str, Any],
    validation: dict[str, Any],
    response_text: str,
    created_at: str,
    response_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "response_id": _require_string(response_id, "response_id"),
        "artifact_type": "PROVIDER_ASSISTED_CONVERSATION_RESPONSE_ARTIFACT",
        "conversation_id": _require_string(conversation_id, "conversation_id"),
        "prompt_id": _require_string(prompt_id, "prompt_id"),
        "intent_id": intent_artifact["artifact_id"],
        "validation_hash": validation["artifact_hash"],
        "response_text": _require_string(response_text, "response_text"),
        "response_type": CONVERSATION_RESPONSE_TYPE,
        "conversation_status": response_status,
        "created_at": _require_string(created_at, "created_at"),
        "provider_assistance_required": validation["provider_assistance_required"],
        "provider_response_authority": False,
        "authority": False,
        "execution_requested": False,
        "worker_invoked": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_response_artifact(
    *,
    response_id: str,
    conversation_id: Any,
    prompt_id: Any,
    validation: dict[str, Any],
    created_at: Any,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "response_id": _require_string(response_id, "response_id"),
        "artifact_type": "PROVIDER_ASSISTED_CONVERSATION_RESPONSE_ARTIFACT",
        "conversation_id": conversation_id if isinstance(conversation_id, str) and conversation_id.strip() else "INVALID_CONVERSATION_ID",
        "prompt_id": prompt_id if isinstance(prompt_id, str) and prompt_id.strip() else "INVALID_PROMPT_ID",
        "intent_id": "UNAVAILABLE_INTENT",
        "validation_hash": validation["artifact_hash"],
        "response_text": "",
        "response_type": CONVERSATION_RESPONSE_TYPE,
        "conversation_status": FAILED_CLOSED,
        "created_at": created_at if isinstance(created_at, str) and created_at.strip() else "INVALID_TIMESTAMP",
        "provider_assistance_required": validation["provider_assistance_required"],
        "provider_response_authority": False,
        "authority": False,
        "execution_requested": False,
        "worker_invoked": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _started_artifact(*, conversation_id: str, prompt_id: str, human_prompt: str, created_at: str) -> dict[str, Any]:
    prompt = _normalize_text(human_prompt, "human_prompt")
    artifact = {
        "event_type": STARTED,
        "conversation_id": _require_string(conversation_id, "conversation_id"),
        "prompt_id": _require_string(prompt_id, "prompt_id"),
        "prompt_text": prompt,
        "prompt_hash": replay_hash({"human_prompt": prompt}),
        "conversation_runtime_version": PROVIDER_ASSISTED_CONVERSATION_RUNTIME_VERSION,
        "created_at": _require_string(created_at, "created_at"),
        "authority": False,
        "replay_visible": True,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_started_artifact(
    *, conversation_id: Any, prompt_id: Any, human_prompt: Any, created_at: Any, failure_reason: str
) -> dict[str, Any]:
    prompt = human_prompt if isinstance(human_prompt, str) and human_prompt.strip() else "INVALID_PROMPT"
    artifact = {
        "event_type": STARTED,
        "conversation_id": conversation_id if isinstance(conversation_id, str) and conversation_id.strip() else "INVALID_CONVERSATION_ID",
        "prompt_id": prompt_id if isinstance(prompt_id, str) and prompt_id.strip() else "INVALID_PROMPT_ID",
        "prompt_text": prompt,
        "prompt_hash": replay_hash({"human_prompt": " ".join(str(prompt).split())}),
        "conversation_runtime_version": PROVIDER_ASSISTED_CONVERSATION_RUNTIME_VERSION,
        "created_at": created_at if isinstance(created_at, str) and created_at.strip() else "INVALID_TIMESTAMP",
        "authority": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(
    *,
    started: dict[str, Any],
    self_resolution: dict[str, Any],
    validation: dict[str, Any],
    response: dict[str, Any],
    provider_capture: dict[str, Any] | None,
    return_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "event_type": return_status,
        "conversation_id": started["conversation_id"],
        "prompt_id": started["prompt_id"],
        "self_resolution_hash": self_resolution["artifact_hash"],
        "validation_hash": validation["artifact_hash"],
        "response_reference": response["response_id"],
        "response_artifact_hash": response["artifact_hash"],
        "provider_assistance_required": validation["provider_assistance_required"],
        "provider_proposal_hash": _provider_proposal_hash(provider_capture),
        "provider_response_authority": False,
        "authority": False,
        "execution_requested": False,
        "worker_invoked": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    started: dict[str, Any],
    self_resolution: dict[str, Any],
    validation: dict[str, Any],
    response: dict[str, Any],
    returned: dict[str, Any],
    provider_capture: dict[str, Any] | None,
) -> dict[str, Any]:
    capture = {
        "provider_assisted_conversation_started": deepcopy(started),
        "conversation_self_resolution": deepcopy(self_resolution),
        "provider_conversation_response_validation": deepcopy(validation),
        "provider_assisted_conversation_response": deepcopy(response),
        "provider_assisted_conversation_returned": deepcopy(returned),
        "provider_conversation_response": deepcopy(provider_capture),
        "response_text": response["response_text"],
        "conversation_status": response["conversation_status"],
        "provider_assistance_required": validation["provider_assistance_required"],
        "provider_response_authority": False,
        "authority": False,
        "execution_requested": False,
        "worker_invoked": False,
        "fail_closed": response["conversation_status"] == FAILED_CLOSED,
        "failure_reason": response["failure_reason"],
    }
    capture["provider_assisted_conversation_capture_hash"] = replay_hash(capture)
    return capture


def _provider_proposal_hash(provider_capture: dict[str, Any] | None) -> str | None:
    if not provider_capture:
        return None
    envelope = provider_capture.get("provider_proposal_envelope")
    if isinstance(envelope, dict):
        return envelope.get("proposal_hash")
    return None


def _looks_authority_bearing(text: str) -> bool:
    lowered = text.lower()
    forbidden_claims = (
        "i authorize",
        "we authorize",
        "authorization granted",
        "authorized to proceed",
        "you are authorized",
        "i approve",
        "approved for execution",
        "execute the worker",
        "worker must execute",
        "dispatch the worker",
        "run the worker",
        "invoke the worker now",
    )
    return any(claim in lowered for claim in forbidden_claims)


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("provider-assisted conversation replay step ordering mismatch")
    _verify_artifact_hash(artifact)
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    path = replay_dir / f"{index:03d}_{step}.json"
    if not path.exists():
        try:
            _persist_step(replay_dir, index, step, artifact)
        except FailClosedRuntimeError:
            return


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("provider-assisted conversation artifact must be a JSON object")
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError("provider-assisted conversation artifact hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("provider-assisted conversation artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("provider-assisted conversation replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("provider-assisted conversation replay hash mismatch")


def _normalize_text(value: Any, field_name: str) -> str:
    raw = _require_string(value, field_name)
    normalized = " ".join(raw.split())
    if not normalized:
        raise FailClosedRuntimeError(f"{field_name} is required")
    return normalized


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _require_confidence(value: Any) -> str:
    confidence = _require_string(value, "confidence")
    if confidence not in VALID_CONFIDENCE_VALUES:
        raise FailClosedRuntimeError("provider conversation response confidence is invalid")
    return confidence


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "provider-assisted conversation failed closed"
