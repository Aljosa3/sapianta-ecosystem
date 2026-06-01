"""Provider-assisted intent classification for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.provider.provider_adapter import ProviderAdapter
from aigol.provider.provider_registry import ProviderRegistry
from aigol.provider.provider_runtime import (
    PROVIDER_PROPOSAL_RETURNED,
    reconstruct_provider_attachment_replay,
    run_provider_attachment,
)
from aigol.runtime.intent_classifier import (
    CLASSIFIED,
    FAILED_CLOSED,
    VALID_DESTINATIONS,
    classify_intent,
    reconstruct_intent_classification_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


PROVIDER_ASSISTED_CLASSIFIER_VERSION = "PROVIDER_ASSISTED_INTENT_CLASSIFICATION_V1"
MINIMAL_PROVIDER_CONTEXT_CAPSULE_VERSION = "MINIMAL_PROVIDER_CONTEXT_CAPSULE_V1"
MINIMAL_PROVIDER_CONTEXT_CAPSULE_LINES = (
    "AiGOL is a constitutional AI execution governance system.",
    "LLM providers are proposal-only sources; they do not govern, authorize, execute, mutate replay, or invoke workers.",
    "AiGOL governs; workers execute only after governed authorization; replay records evidence.",
    "Answer in the AiGOL/SAPIANTA governance domain unless the user explicitly asks for another domain.",
    "Use the human prompt as the question; provide explanatory text only.",
)
REPLAY_STEPS = (
    "provider_intent_governance_validation",
    "provider_assisted_intent_classification_artifact",
    "provider_assisted_intent_classification_replay",
)


def classify_intent_with_provider_assistance(
    *,
    artifact_id: str,
    human_request_reference: str,
    human_prompt: str,
    classification_timestamp: str,
    replay_reference: str,
    replay_dir: str | Path,
    provider_id: str,
    registry: ProviderRegistry,
    adapter: ProviderAdapter,
    normalized_request_reference: str | None = None,
) -> dict[str, Any]:
    """Classify deterministically, then request provider semantics only on failure."""

    replay_path = Path(replay_dir)
    deterministic_dir = replay_path / "deterministic_intent_classification"
    provider_dir = replay_path / "provider_semantic_assistance"
    deterministic_capture = classify_intent(
        artifact_id=f"{artifact_id}:DETERMINISTIC",
        human_request_reference=human_request_reference,
        human_prompt=human_prompt,
        classification_timestamp=classification_timestamp,
        replay_reference=str(deterministic_dir),
        replay_dir=deterministic_dir,
        normalized_request_reference=normalized_request_reference,
    )
    deterministic_artifact = deterministic_capture["intent_classification_artifact"]
    try:
        _ensure_replay_available(replay_path)
        if deterministic_artifact["classification_status"] == CLASSIFIED:
            validation = _validation_artifact(
                validation_id=f"{artifact_id}:VALIDATION",
                human_request_reference=human_request_reference,
                deterministic_artifact=deterministic_artifact,
                provider_capture=None,
                suggested_destination=deterministic_artifact["classification_destination"],
                classification_reasoning=deterministic_artifact["classification_reason"],
                confidence="DETERMINISTIC",
                validation_status=CLASSIFIED,
                provider_assistance_required=False,
                validation_reason="deterministic classification succeeded; provider assistance not requested",
                timestamp=classification_timestamp,
                failure_reason=None,
            )
            final_artifact = _final_classification_artifact(
                artifact_id=artifact_id,
                human_request_reference=human_request_reference,
                human_prompt=human_prompt,
                classification_destination=deterministic_artifact["classification_destination"],
                classification_reason=deterministic_artifact["classification_reason"],
                classifier_version=deterministic_artifact["classifier_version"],
                classification_timestamp=classification_timestamp,
                replay_reference=replay_reference,
                normalized_request_reference=normalized_request_reference,
                classification_status=CLASSIFIED,
                ambiguity_status="UNAMBIGUOUS",
                failure_reason=None,
                provider_assisted=False,
                validation_hash=validation["artifact_hash"],
            )
            assisted_replay = _assisted_replay(final_artifact, validation)
            _persist_step(replay_path, 0, REPLAY_STEPS[0], validation)
            _persist_step(replay_path, 1, REPLAY_STEPS[1], final_artifact)
            _persist_step(replay_path, 2, REPLAY_STEPS[2], assisted_replay)
            return _capture(deterministic_capture, None, validation, final_artifact, assisted_replay)

        provider_capture = run_provider_attachment(
            provider_id=provider_id,
            request=_provider_request(
                human_prompt=human_prompt,
                human_request_reference=human_request_reference,
                deterministic_artifact=deterministic_artifact,
            ),
            proposal_id=f"{artifact_id}:PROVIDER_SEMANTIC_SUGGESTION",
            timestamp=classification_timestamp,
            registry=registry,
            adapter=adapter,
            replay_dir=provider_dir,
        )
        suggestion = _extract_provider_suggestion(provider_capture)
        validation = _validation_artifact(
            validation_id=f"{artifact_id}:VALIDATION",
            human_request_reference=human_request_reference,
            deterministic_artifact=deterministic_artifact,
            provider_capture=provider_capture,
            suggested_destination=suggestion["suggested_destination"],
            classification_reasoning=suggestion["classification_reasoning"],
            confidence=suggestion["confidence"],
            validation_status=CLASSIFIED,
            provider_assistance_required=True,
            validation_reason="provider semantic suggestion validated by AiGOL",
            timestamp=classification_timestamp,
            failure_reason=None,
        )
        final_artifact = _final_classification_artifact(
            artifact_id=artifact_id,
            human_request_reference=human_request_reference,
            human_prompt=human_prompt,
            classification_destination=suggestion["suggested_destination"],
            classification_reason=f"provider-assisted semantic suggestion validated: {suggestion['classification_reasoning']}",
            classifier_version=PROVIDER_ASSISTED_CLASSIFIER_VERSION,
            classification_timestamp=classification_timestamp,
            replay_reference=replay_reference,
            normalized_request_reference=normalized_request_reference,
            classification_status=CLASSIFIED,
            ambiguity_status="UNAMBIGUOUS",
            failure_reason=None,
            provider_assisted=True,
            validation_hash=validation["artifact_hash"],
        )
        assisted_replay = _assisted_replay(final_artifact, validation)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], validation)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], final_artifact)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], assisted_replay)
        return _capture(deterministic_capture, provider_capture, validation, final_artifact, assisted_replay)
    except Exception as exc:
        provider_capture = locals().get("provider_capture")
        validation = _failed_validation_artifact(
            validation_id=f"{artifact_id}:VALIDATION",
            human_request_reference=human_request_reference,
            deterministic_artifact=deterministic_artifact,
            provider_capture=provider_capture if isinstance(provider_capture, dict) else None,
            timestamp=classification_timestamp,
            failure_reason=_failure_reason(exc),
        )
        final_artifact = _failed_classification_artifact(
            artifact_id=artifact_id,
            human_request_reference=human_request_reference,
            human_prompt=human_prompt,
            classification_timestamp=classification_timestamp,
            replay_reference=replay_reference,
            normalized_request_reference=normalized_request_reference,
            validation_hash=validation["artifact_hash"],
            failure_reason=_failure_reason(exc),
        )
        assisted_replay = _assisted_replay(final_artifact, validation)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], validation)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], final_artifact)
        _persist_failure_if_possible(replay_path, 2, REPLAY_STEPS[2], assisted_replay)
        return _capture(deterministic_capture, provider_capture if isinstance(provider_capture, dict) else None, validation, final_artifact, assisted_replay)


def reconstruct_provider_assisted_intent_classification_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct deterministic attempt, provider assistance, validation, and final classification."""

    replay_path = Path(replay_dir)
    deterministic = reconstruct_intent_classification_replay(replay_path / "deterministic_intent_classification")
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("provider-assisted intent replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("provider-assisted intent replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)

    validation = wrappers[0]["artifact"]
    final_artifact = wrappers[1]["artifact"]
    assisted_replay = wrappers[2]["artifact"]
    if final_artifact.get("governance_validation_hash") != validation["artifact_hash"]:
        raise FailClosedRuntimeError("provider-assisted intent validation hash mismatch")
    if assisted_replay.get("classification_artifact_hash") != final_artifact["artifact_hash"]:
        raise FailClosedRuntimeError("provider-assisted intent final artifact hash mismatch")
    if assisted_replay.get("governance_validation_hash") != validation["artifact_hash"]:
        raise FailClosedRuntimeError("provider-assisted intent replay validation hash mismatch")

    provider = None
    if validation["provider_assistance_required"]:
        provider = reconstruct_provider_attachment_replay(replay_path / "provider_semantic_assistance")
    return {
        "artifact_id": final_artifact["artifact_id"],
        "human_request_reference": final_artifact["human_request_reference"],
        "classification_destination": final_artifact["classification_destination"],
        "classification_status": final_artifact["classification_status"],
        "classifier_version": final_artifact["classifier_version"],
        "deterministic_classification_status": deterministic["classification_status"],
        "deterministic_destination": deterministic["classification_destination"],
        "provider_assistance_required": validation["provider_assistance_required"],
        "provider_assistance_replay": deepcopy(provider),
        "governance_validation_status": validation["validation_status"],
        "replay_visible": True,
        "non_authoritative": True,
        "provider_suggestion_authority": False,
        "routing_performed": False,
        "execution_requested": False,
        "worker_invoked": False,
        "replay_artifact_count": len(wrappers) + deterministic["replay_artifact_count"] + (provider["replay_artifact_count"] if provider else 0),
        "replay_hash": replay_hash(
            {
                "deterministic": deterministic,
                "provider": provider,
                "provider_assisted": wrappers,
            }
        ),
    }


def _provider_request(*, human_prompt: str, human_request_reference: str, deterministic_artifact: dict[str, Any]) -> dict[str, Any]:
    prompt = _require_string(human_prompt, "human_prompt")
    return {
        "semantic_task": "intent_classification_suggestion",
        "human_prompt": prompt,
        "prompt": _provider_prompt_with_context(prompt),
        "context_capsule": _minimal_provider_context_capsule(),
        "human_request_reference": _require_string(human_request_reference, "human_request_reference"),
        "allowed_destinations": sorted(VALID_DESTINATIONS),
        "deterministic_classification_status": deterministic_artifact["classification_status"],
        "deterministic_failure_reason": deterministic_artifact["failure_reason"],
        "provider_authority": False,
        "routing_authority": False,
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
    prompt = _require_string(human_prompt, "human_prompt")
    return "\n".join(
        (
            "AiGOL context:",
            *MINIMAL_PROVIDER_CONTEXT_CAPSULE_LINES,
            "",
            "Human prompt:",
            prompt,
        )
    )


def _extract_provider_suggestion(provider_capture: dict[str, Any]) -> dict[str, str]:
    returned = provider_capture.get("provider_proposal_returned")
    if not isinstance(returned, dict):
        raise FailClosedRuntimeError("provider assistance return evidence is required")
    if returned.get("event_type") != PROVIDER_PROPOSAL_RETURNED:
        reason = returned.get("failure_reason") or "provider assistance failed closed"
        raise FailClosedRuntimeError(reason)
    envelope = provider_capture.get("provider_proposal_envelope")
    if not isinstance(envelope, dict):
        raise FailClosedRuntimeError("provider assistance envelope is required")
    response = envelope.get("response")
    if not isinstance(response, dict):
        raise FailClosedRuntimeError("provider suggestion response must be a JSON object")
    suggestion = {
        "suggested_destination": _require_string(response.get("suggested_destination"), "suggested_destination"),
        "classification_reasoning": _require_string(response.get("classification_reasoning"), "classification_reasoning"),
        "confidence": _require_string(response.get("confidence"), "confidence"),
    }
    if suggestion["suggested_destination"] not in VALID_DESTINATIONS:
        raise FailClosedRuntimeError("provider suggested invalid destination")
    _reject_multiple_destinations(response)
    return suggestion


def _reject_multiple_destinations(response: dict[str, Any]) -> None:
    value = response.get("suggested_destination")
    if isinstance(value, list):
        raise FailClosedRuntimeError("provider suggested multiple destinations")
    alternates = response.get("alternate_destinations")
    if isinstance(alternates, list) and alternates:
        raise FailClosedRuntimeError("provider suggestion is ambiguous")


def _validation_artifact(
    *,
    validation_id: str,
    human_request_reference: str,
    deterministic_artifact: dict[str, Any],
    provider_capture: dict[str, Any] | None,
    suggested_destination: str,
    classification_reasoning: str,
    confidence: str,
    validation_status: str,
    provider_assistance_required: bool,
    validation_reason: str,
    timestamp: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    if suggested_destination not in VALID_DESTINATIONS:
        raise FailClosedRuntimeError("provider-assisted intent validation failed: invalid destination")
    artifact = {
        "artifact_id": _require_string(validation_id, "validation_id"),
        "artifact_type": "PROVIDER_ASSISTED_INTENT_GOVERNANCE_VALIDATION",
        "human_request_reference": _require_string(human_request_reference, "human_request_reference"),
        "deterministic_artifact_id": deterministic_artifact["artifact_id"],
        "deterministic_artifact_hash": deterministic_artifact["artifact_hash"],
        "deterministic_status": deterministic_artifact["classification_status"],
        "provider_assistance_required": provider_assistance_required,
        "provider_proposal_hash": _provider_proposal_hash(provider_capture),
        "suggested_destination": suggested_destination,
        "classification_reasoning": _require_string(classification_reasoning, "classification_reasoning"),
        "confidence": _require_string(confidence, "confidence"),
        "allowed_destinations": sorted(VALID_DESTINATIONS),
        "validation_status": validation_status,
        "validation_reason": _require_string(validation_reason, "validation_reason"),
        "validation_timestamp": _require_string(timestamp, "timestamp"),
        "provider_suggestion_authority": False,
        "routing_performed": False,
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
    human_request_reference: str,
    deterministic_artifact: dict[str, Any],
    provider_capture: dict[str, Any] | None,
    timestamp: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_id": _require_string(validation_id, "validation_id"),
        "artifact_type": "PROVIDER_ASSISTED_INTENT_GOVERNANCE_VALIDATION",
        "human_request_reference": _require_string(human_request_reference, "human_request_reference"),
        "deterministic_artifact_id": deterministic_artifact["artifact_id"],
        "deterministic_artifact_hash": deterministic_artifact["artifact_hash"],
        "deterministic_status": deterministic_artifact["classification_status"],
        "provider_assistance_required": deterministic_artifact["classification_status"] == FAILED_CLOSED,
        "provider_proposal_hash": _provider_proposal_hash(provider_capture),
        "suggested_destination": None,
        "classification_reasoning": "provider-assisted classification failed closed",
        "confidence": "FAILED_CLOSED",
        "allowed_destinations": sorted(VALID_DESTINATIONS),
        "validation_status": FAILED_CLOSED,
        "validation_reason": "provider-assisted classification failed closed",
        "validation_timestamp": _require_string(timestamp, "timestamp"),
        "provider_suggestion_authority": False,
        "routing_performed": False,
        "execution_requested": False,
        "worker_invoked": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _final_classification_artifact(
    *,
    artifact_id: str,
    human_request_reference: str,
    human_prompt: str,
    classification_destination: str,
    classification_reason: str,
    classifier_version: str,
    classification_timestamp: str,
    replay_reference: str,
    normalized_request_reference: str | None,
    classification_status: str,
    ambiguity_status: str,
    failure_reason: str | None,
    provider_assisted: bool,
    validation_hash: str,
) -> dict[str, Any]:
    if classification_destination not in VALID_DESTINATIONS:
        raise FailClosedRuntimeError("provider-assisted intent failed closed: invalid destination")
    artifact = {
        "artifact_id": _require_string(artifact_id, "artifact_id"),
        "artifact_type": "INTENT_CLASSIFICATION_ARTIFACT",
        "human_request_reference": _require_string(human_request_reference, "human_request_reference"),
        "human_prompt_hash": replay_hash({"human_prompt": " ".join(_require_string(human_prompt, "human_prompt").split())}),
        "normalized_request_reference": normalized_request_reference,
        "classification_destination": classification_destination,
        "classification_reason": _require_string(classification_reason, "classification_reason"),
        "classifier_version": _require_string(classifier_version, "classifier_version"),
        "classification_timestamp": _require_string(classification_timestamp, "classification_timestamp"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "ambiguity_status": _require_string(ambiguity_status, "ambiguity_status"),
        "classification_status": classification_status,
        "provider_assisted": provider_assisted,
        "governance_validation_hash": _require_string(validation_hash, "validation_hash"),
        "provider_suggestion_authority": False,
        "routing_performed": False,
        "execution_requested": False,
        "worker_invoked": False,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_classification_artifact(
    *,
    artifact_id: str,
    human_request_reference: str,
    human_prompt: Any,
    classification_timestamp: str,
    replay_reference: str,
    normalized_request_reference: str | None,
    validation_hash: str,
    failure_reason: str,
) -> dict[str, Any]:
    prompt = human_prompt if isinstance(human_prompt, str) and human_prompt.strip() else "INVALID_PROMPT"
    artifact = {
        "artifact_id": _require_string(artifact_id, "artifact_id"),
        "artifact_type": "INTENT_CLASSIFICATION_ARTIFACT",
        "human_request_reference": _require_string(human_request_reference, "human_request_reference"),
        "human_prompt_hash": replay_hash({"human_prompt": " ".join(str(prompt).split())}),
        "normalized_request_reference": normalized_request_reference,
        "classification_destination": None,
        "classification_reason": "provider-assisted classification failed closed",
        "classifier_version": PROVIDER_ASSISTED_CLASSIFIER_VERSION,
        "classification_timestamp": _require_string(classification_timestamp, "classification_timestamp"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "ambiguity_status": FAILED_CLOSED,
        "classification_status": FAILED_CLOSED,
        "provider_assisted": True,
        "governance_validation_hash": _require_string(validation_hash, "validation_hash"),
        "provider_suggestion_authority": False,
        "routing_performed": False,
        "execution_requested": False,
        "worker_invoked": False,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _assisted_replay(final_artifact: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "replay_id": f"{final_artifact['artifact_id']}:PROVIDER_ASSISTED_REPLAY",
        "artifact_reference": final_artifact["artifact_id"],
        "human_request_reference": final_artifact["human_request_reference"],
        "destination": final_artifact["classification_destination"],
        "classifier_version": final_artifact["classifier_version"],
        "classification_status": final_artifact["classification_status"],
        "provider_assistance_required": validation["provider_assistance_required"],
        "provider_proposal_hash": validation["provider_proposal_hash"],
        "governance_validation_hash": validation["artifact_hash"],
        "classification_artifact_hash": final_artifact["artifact_hash"],
        "replay_reference": final_artifact["replay_reference"],
        "replay_visibility": "MANDATORY",
        "non_authoritative": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    deterministic_capture: dict[str, Any],
    provider_capture: dict[str, Any] | None,
    validation: dict[str, Any],
    final_artifact: dict[str, Any],
    assisted_replay: dict[str, Any],
) -> dict[str, Any]:
    capture = {
        "deterministic_intent_classification": deepcopy(deterministic_capture),
        "provider_semantic_assistance": deepcopy(provider_capture),
        "governance_validation": deepcopy(validation),
        "intent_classification_artifact": deepcopy(final_artifact),
        "provider_assisted_intent_classification_replay": deepcopy(assisted_replay),
        "provider_assisted": final_artifact["provider_assisted"],
        "classification_destination": final_artifact["classification_destination"],
        "classification_status": final_artifact["classification_status"],
        "provider_suggestion_authority": False,
        "routing_performed": False,
        "execution_requested": False,
        "worker_invoked": False,
        "fail_closed": final_artifact["classification_status"] == FAILED_CLOSED,
        "failure_reason": final_artifact["failure_reason"],
    }
    capture["provider_assisted_intent_classifier_capture_hash"] = replay_hash(capture)
    return capture


def _provider_proposal_hash(provider_capture: dict[str, Any] | None) -> str | None:
    if not provider_capture:
        return None
    envelope = provider_capture.get("provider_proposal_envelope")
    if isinstance(envelope, dict):
        return envelope.get("proposal_hash")
    return None


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("provider-assisted intent replay step ordering mismatch")
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


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("provider-assisted intent artifact must be a JSON object")
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError("provider-assisted intent artifact hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("provider-assisted intent artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("provider-assisted intent replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("provider-assisted intent replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "provider-assisted intent classification failed closed"
