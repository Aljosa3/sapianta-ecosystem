"""Adaptive escalation runtime for Universal Translation artifacts."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.universal_translation_artifact_schema import (
    GOVERNANCE_TO_HUMAN,
    HIGH,
    HUMAN_TO_GOVERNANCE,
    LOW,
    MATERIAL_AMBIGUITY,
    MEDIUM,
    MINOR_AMBIGUITY,
    NO_AMBIGUITY,
    UNKNOWN,
    create_universal_translation_artifact,
    validate_universal_translation_artifact,
)


RUNTIME_VERSION = "ADAPTIVE_TRANSLATION_ESCALATION_RUNTIME_V1"
REPLAY_STEP = "adaptive_translation_escalation_recorded"

STAGE_DETERMINISTIC = "STAGE_1_DETERMINISTIC_TRANSLATION"
STAGE_LOW_COST = "STAGE_2_LOW_COST_PROVIDER"
STAGE_MEDIUM_CAPABILITY = "STAGE_3_MEDIUM_CAPABILITY_PROVIDER"
STAGE_HIGH_CAPABILITY = "STAGE_4_HIGH_CAPABILITY_PROVIDER"

TIER_LOW_COST = "LOW_COST_TRANSLATION_PROVIDER"
TIER_MEDIUM_CAPABILITY = "MEDIUM_CAPABILITY_TRANSLATION_PROVIDER"
TIER_HIGH_CAPABILITY = "HIGH_CAPABILITY_TRANSLATION_PROVIDER"
ALLOWED_TIERS = (TIER_LOW_COST, TIER_MEDIUM_CAPABILITY, TIER_HIGH_CAPABILITY)

ACCEPTED = "ACCEPTED"
REJECTED = "REJECTED"
UNAVAILABLE = "UNAVAILABLE"
DETERMINISTIC_SELECTED = "DETERMINISTIC_SELECTED"
PROVIDER_SELECTED = "PROVIDER_SELECTED"
DETERMINISTIC_FALLBACK_USED = "DETERMINISTIC_FALLBACK_USED"

TranslationProvider = Callable[[dict[str, Any]], dict[str, Any]]


def run_adaptive_translation_escalation(
    *,
    translation_request_id: str,
    deterministic_translation_artifact: dict[str, Any],
    replay_dir: str | Path,
    created_at: str,
    provider_candidates: list[dict[str, Any]] | None = None,
    escalation_policy: dict[str, Any] | None = None,
    operator_requests_improved_explanation: bool = False,
    fidelity_requirements: dict[str, Any] | None = None,
    err_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run adaptive provider escalation while preserving deterministic authority."""

    replay_path = Path(replay_dir)
    deterministic = validate_universal_translation_artifact(deterministic_translation_artifact)
    policy = _normalized_policy(escalation_policy)
    fidelity = _optional_mapping(fidelity_requirements, "fidelity_requirements")
    err = _optional_mapping(err_evidence, "err_evidence")
    providers = _normalized_providers(provider_candidates)
    escalation_reasons = _escalation_reasons(
        deterministic,
        policy,
        operator_requests_improved_explanation,
        fidelity,
    )
    deterministic_decision = _deterministic_stage_decision(deterministic, escalation_reasons)
    attempts: list[dict[str, Any]] = []
    selected = deterministic
    final_status = DETERMINISTIC_SELECTED
    fallback_reason = None

    if escalation_reasons:
        for provider in _providers_in_stage_order(providers):
            attempt = _attempt_provider_translation(
                translation_request_id=translation_request_id,
                deterministic_artifact=deterministic,
                provider_candidate=provider,
                created_at=created_at,
                escalation_reasons=escalation_reasons,
                fidelity_requirements=fidelity,
            )
            attempts.append(attempt)
            if attempt["attempt_status"] == ACCEPTED:
                selected = attempt["provider_translation_artifact"]
                final_status = PROVIDER_SELECTED
                fallback_reason = None
                break
        if final_status != PROVIDER_SELECTED:
            final_status = DETERMINISTIC_FALLBACK_USED
            fallback_reason = _fallback_reason(attempts)

    artifact = _adaptive_escalation_artifact(
        translation_request_id=translation_request_id,
        deterministic_artifact=deterministic,
        selected_artifact=selected,
        deterministic_decision=deterministic_decision,
        escalation_reasons=escalation_reasons,
        provider_attempts=attempts,
        final_status=final_status,
        fallback_reason=fallback_reason,
        policy=policy,
        fidelity_requirements=fidelity,
        err_evidence=err,
        replay_reference=str(replay_path),
        created_at=created_at,
    )
    wrapper = {
        "replay_index": 0,
        "replay_step": REPLAY_STEP,
        "event_type": RUNTIME_VERSION,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"000_{REPLAY_STEP}.json", wrapper)
    return {
        "runtime_version": RUNTIME_VERSION,
        "translation_status": final_status,
        "selected_translation_artifact": deepcopy(selected),
        "deterministic_translation_artifact": deepcopy(deterministic),
        "adaptive_escalation_artifact": deepcopy(artifact),
        "adaptive_escalation_replay_reference": str(replay_path),
        "escalation_reasons": list(escalation_reasons),
        "provider_attempts": deepcopy(attempts),
        "fallback_reason": fallback_reason,
        "cost_metrics": deepcopy(artifact["cost_metrics"]),
        "provider_invoked": any(attempt["provider_invoked"] for attempt in attempts),
        "authority_granted": False,
        "workflow_executed": False,
        "approval_granted": False,
        "governance_mutated": False,
        "replay_visible": True,
    }


def reconstruct_adaptive_translation_escalation_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct adaptive translation escalation replay evidence."""

    replay_path = Path(replay_dir)
    wrapper = load_json(replay_path / f"000_{REPLAY_STEP}.json")
    if wrapper.get("replay_index") != 0 or wrapper.get("replay_step") != REPLAY_STEP:
        raise FailClosedRuntimeError("adaptive translation escalation replay ordering mismatch")
    _verify_wrapper_hash(wrapper)
    artifact = _require_mapping(wrapper.get("artifact"), "adaptive_translation_escalation_artifact")
    _verify_artifact_hash(artifact)
    if artifact.get("artifact_type") != RUNTIME_VERSION:
        raise FailClosedRuntimeError("adaptive translation escalation artifact type mismatch")
    deterministic = validate_universal_translation_artifact(artifact["deterministic_translation_artifact"])
    selected = validate_universal_translation_artifact(artifact["selected_translation_artifact"])
    if artifact["deterministic_translation_hash"] != deterministic["artifact_hash"]:
        raise FailClosedRuntimeError("adaptive translation deterministic hash mismatch")
    if artifact["selected_translation_hash"] != selected["artifact_hash"]:
        raise FailClosedRuntimeError("adaptive translation selected hash mismatch")
    _validate_authority_flags(artifact)
    for attempt in artifact["provider_attempts"]:
        _validate_attempt_replay(attempt, deterministic)
    return {
        "runtime_version": RUNTIME_VERSION,
        "translation_status": artifact["final_status"],
        "adaptive_escalation_artifact": deepcopy(artifact),
        "selected_translation_artifact": deepcopy(selected),
        "deterministic_translation_artifact": deepcopy(deterministic),
        "escalation_reasons": list(artifact["escalation_reasons"]),
        "provider_attempts": deepcopy(artifact["provider_attempts"]),
        "fallback_reason": artifact["fallback_reason"],
        "cost_metrics": deepcopy(artifact["cost_metrics"]),
        "replay_hash": wrapper["replay_hash"],
        "authority_granted": False,
        "workflow_executed": False,
        "approval_granted": False,
        "governance_mutated": False,
        "replay_visible": True,
    }


def _attempt_provider_translation(
    *,
    translation_request_id: str,
    deterministic_artifact: dict[str, Any],
    provider_candidate: dict[str, Any],
    created_at: str,
    escalation_reasons: list[str],
    fidelity_requirements: dict[str, Any],
) -> dict[str, Any]:
    request_artifact = _provider_request_artifact(
        translation_request_id=translation_request_id,
        deterministic_artifact=deterministic_artifact,
        provider_candidate=provider_candidate,
        escalation_reasons=escalation_reasons,
        fidelity_requirements=fidelity_requirements,
        created_at=created_at,
    )
    provider = provider_candidate.get("provider")
    provider_invoked = provider is not None
    response: dict[str, Any] | None = None
    rejection_reason = None
    try:
        if provider is None:
            rejection_reason = "PROVIDER_NOT_CONFIGURED"
        elif callable(provider):
            response = provider(deepcopy(request_artifact))
        elif hasattr(provider, "translate"):
            response = provider.translate(deepcopy(request_artifact))
        else:
            rejection_reason = "PROVIDER_INTERFACE_UNSUPPORTED"
    except Exception as exc:
        rejection_reason = f"PROVIDER_UNAVAILABLE: {exc}"

    if response is None:
        return _provider_attempt_artifact(
            provider_candidate=provider_candidate,
            request_artifact=request_artifact,
            response_artifact=None,
            provider_translation_artifact=None,
            attempt_status=UNAVAILABLE,
            rejection_reason=rejection_reason or "PROVIDER_RESPONSE_MISSING",
        )

    try:
        response_artifact = _provider_response_artifact(
            request_artifact=request_artifact,
            response=response,
            provider_candidate=provider_candidate,
            deterministic_artifact=deterministic_artifact,
            created_at=created_at,
        )
        provider_translation = _provider_translation_artifact(
            deterministic_artifact=deterministic_artifact,
            response_artifact=response_artifact,
            provider_candidate=provider_candidate,
            created_at=created_at,
        )
        status = ACCEPTED
        rejection = None
    except FailClosedRuntimeError as exc:
        response_artifact = _rejected_response_artifact(
            request_artifact=request_artifact,
            response=response,
            provider_candidate=provider_candidate,
            rejection_reason=str(exc),
            created_at=created_at,
        )
        provider_translation = None
        status = REJECTED
        rejection = str(exc)

    attempt = _provider_attempt_artifact(
        provider_candidate=provider_candidate,
        request_artifact=request_artifact,
        response_artifact=response_artifact,
        provider_translation_artifact=provider_translation,
        attempt_status=status,
        rejection_reason=rejection,
    )
    attempt["provider_invoked"] = provider_invoked
    return attempt


def _provider_request_artifact(
    *,
    translation_request_id: str,
    deterministic_artifact: dict[str, Any],
    provider_candidate: dict[str, Any],
    escalation_reasons: list[str],
    fidelity_requirements: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": "ADAPTIVE_TRANSLATION_PROVIDER_REQUEST_V1",
        "translation_request_id": _require_string(translation_request_id, "translation_request_id"),
        "provider_id": _require_string(provider_candidate.get("provider_id"), "provider_id"),
        "provider_tier": _require_tier(provider_candidate.get("provider_tier")),
        "provider_role": "TRANSLATION_PROVIDER",
        "deterministic_translation_hash": deterministic_artifact["artifact_hash"],
        "deterministic_translation_artifact": deepcopy(deterministic_artifact),
        "source_direction": deterministic_artifact["source_direction"],
        "bounded_translation_task": _bounded_task_for(deterministic_artifact),
        "preservation_requirements": _preservation_requirements(deterministic_artifact, fidelity_requirements),
        "escalation_reasons": list(escalation_reasons),
        "forbidden_claims": [
            "Provider output is authoritative.",
            "Execution is authorized by translation.",
            "Approval is granted by translation.",
            "Governance state was mutated by translation.",
        ],
        "advisory_only": True,
        "authority_granted": False,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _provider_response_artifact(
    *,
    request_artifact: dict[str, Any],
    response: dict[str, Any],
    provider_candidate: dict[str, Any],
    deterministic_artifact: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    payload = _require_mapping(response, "provider_response")
    if payload.get("advisory_only") is not True or payload.get("authority_granted") is True:
        raise FailClosedRuntimeError("TRANSLATION_PROVIDER_RESPONSE_CLAIMS_AUTHORITY")
    if payload.get("approval_authority") is True or payload.get("execution_authority") is True:
        raise FailClosedRuntimeError("TRANSLATION_PROVIDER_RESPONSE_CLAIMS_AUTHORITY")
    candidate = _require_mapping(payload.get("translation_candidate"), "translation_candidate")
    preserved = _require_mapping(payload.get("preserved_authoritative_references"), "preserved_authoritative_references")
    _validate_preserved_references(preserved, deterministic_artifact)
    confidence = _require_confidence(payload.get("confidence"))
    artifact = {
        "artifact_type": "ADAPTIVE_TRANSLATION_PROVIDER_RESPONSE_V1",
        "request_hash": request_artifact["artifact_hash"],
        "provider_id": _require_string(provider_candidate.get("provider_id"), "provider_id"),
        "provider_tier": _require_tier(provider_candidate.get("provider_tier")),
        "provider_role": "TRANSLATION_PROVIDER",
        "translation_candidate": deepcopy(candidate),
        "confidence": confidence,
        "limitations": _string_list(payload.get("limitations")),
        "preserved_authoritative_references": deepcopy(preserved),
        "estimated_cost": _cost_value(payload.get("estimated_cost")),
        "cost_units": _optional_string(payload.get("cost_units")) or "USD",
        "advisory_only": True,
        "authority_granted": False,
        "approval_authority": False,
        "execution_authority": False,
        "governance_authority": False,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _rejected_response_artifact(
    *,
    request_artifact: dict[str, Any],
    response: dict[str, Any],
    provider_candidate: dict[str, Any],
    rejection_reason: str,
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": "ADAPTIVE_TRANSLATION_PROVIDER_RESPONSE_REJECTED_V1",
        "request_hash": request_artifact["artifact_hash"],
        "provider_id": _require_string(provider_candidate.get("provider_id"), "provider_id"),
        "provider_tier": _require_tier(provider_candidate.get("provider_tier")),
        "provider_role": "TRANSLATION_PROVIDER",
        "raw_response_hash": replay_hash(response),
        "rejection_reason": _require_string(rejection_reason, "rejection_reason"),
        "advisory_only": True,
        "authority_granted": False,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _provider_translation_artifact(
    *,
    deterministic_artifact: dict[str, Any],
    response_artifact: dict[str, Any],
    provider_candidate: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    direction = deterministic_artifact["source_direction"]
    candidate = response_artifact["translation_candidate"]
    governance_payload: dict[str, Any] | None = None
    human_payload: dict[str, Any] | None = None
    if direction == HUMAN_TO_GOVERNANCE:
        governance_payload = _require_mapping(candidate.get("translated_governance_payload"), "translated_governance_payload")
    elif direction == GOVERNANCE_TO_HUMAN:
        human_payload = _require_mapping(candidate.get("human_readable_payload"), "human_readable_payload")
    else:
        raise FailClosedRuntimeError("adaptive translation source direction unsupported")
    artifact = create_universal_translation_artifact(
        translation_id=f"{deterministic_artifact['translation_id']}:PROVIDER:{provider_candidate['provider_id']}",
        translation_request=deepcopy(deterministic_artifact["translation_request"]),
        source_direction=direction,
        source_payload=deepcopy(deterministic_artifact["source_payload"]),
        normalized_intent=deepcopy(deterministic_artifact["normalized_intent"]),
        translated_governance_payload=governance_payload,
        human_readable_payload=human_payload,
        ambiguity_flags=deepcopy(deterministic_artifact["ambiguity_flags"]),
        confidence=response_artifact["confidence"],
        provider_metadata={
            "provider_used": True,
            "provider_count": 1,
            "providers": [
                {
                    "provider_id": provider_candidate["provider_id"],
                    "provider_tier": provider_candidate["provider_tier"],
                    "provider_role": "TRANSLATION_PROVIDER",
                    "authority_granted": False,
                    "response_hash": response_artifact["artifact_hash"],
                }
            ],
            "comparison_used": False,
        },
        deterministic_fallback_status={
            "fallback_used": False,
            "fallback_reason": None,
            "deterministic_rule_ids": ["ADAPTIVE_TRANSLATION_PROVIDER_ACCEPTED_V1"],
        },
        replay_reference=deterministic_artifact["replay_reference"],
        created_at=created_at,
    )
    _validate_no_authority(artifact)
    return artifact


def _provider_attempt_artifact(
    *,
    provider_candidate: dict[str, Any],
    request_artifact: dict[str, Any],
    response_artifact: dict[str, Any] | None,
    provider_translation_artifact: dict[str, Any] | None,
    attempt_status: str,
    rejection_reason: str | None,
) -> dict[str, Any]:
    cost = _provider_cost(provider_candidate, response_artifact)
    attempt = {
        "attempt_status": attempt_status,
        "provider_id": _require_string(provider_candidate.get("provider_id"), "provider_id"),
        "provider_tier": _require_tier(provider_candidate.get("provider_tier")),
        "stage": _stage_for_tier(provider_candidate["provider_tier"]),
        "request_artifact": deepcopy(request_artifact),
        "request_hash": request_artifact["artifact_hash"],
        "response_artifact": deepcopy(response_artifact) if response_artifact else None,
        "response_hash": response_artifact.get("artifact_hash") if response_artifact else None,
        "provider_translation_artifact": deepcopy(provider_translation_artifact) if provider_translation_artifact else None,
        "provider_translation_hash": provider_translation_artifact.get("artifact_hash") if provider_translation_artifact else None,
        "rejection_reason": rejection_reason,
        "cost_metrics": cost,
        "provider_invoked": provider_candidate.get("provider") is not None,
        "authority_granted": False,
        "approval_granted": False,
        "execution_authorized": False,
        "governance_mutated": False,
    }
    attempt["attempt_hash"] = replay_hash(attempt)
    return attempt


def _adaptive_escalation_artifact(
    *,
    translation_request_id: str,
    deterministic_artifact: dict[str, Any],
    selected_artifact: dict[str, Any],
    deterministic_decision: dict[str, Any],
    escalation_reasons: list[str],
    provider_attempts: list[dict[str, Any]],
    final_status: str,
    fallback_reason: str | None,
    policy: dict[str, Any],
    fidelity_requirements: dict[str, Any],
    err_evidence: dict[str, Any],
    replay_reference: str,
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": RUNTIME_VERSION,
        "translation_request_id": _require_string(translation_request_id, "translation_request_id"),
        "runtime_version": RUNTIME_VERSION,
        "stages": [
            STAGE_DETERMINISTIC,
            STAGE_LOW_COST,
            STAGE_MEDIUM_CAPABILITY,
            STAGE_HIGH_CAPABILITY,
        ],
        "deterministic_stage_decision": deepcopy(deterministic_decision),
        "escalation_reasons": list(escalation_reasons),
        "provider_attempts": deepcopy(provider_attempts),
        "final_status": final_status,
        "fallback_reason": fallback_reason,
        "deterministic_translation_artifact": deepcopy(deterministic_artifact),
        "deterministic_translation_hash": deterministic_artifact["artifact_hash"],
        "selected_translation_artifact": deepcopy(selected_artifact),
        "selected_translation_hash": selected_artifact["artifact_hash"],
        "policy": deepcopy(policy),
        "fidelity_requirements": deepcopy(fidelity_requirements),
        "cost_metrics": _aggregate_cost(provider_attempts),
        "err_evidence": deepcopy(err_evidence),
        "err_evidence_hash": replay_hash(err_evidence) if err_evidence else None,
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "advisory_only": True,
        "authority_granted": False,
        "provider_authority": False,
        "approval_authority": False,
        "execution_authority": False,
        "governance_authority": False,
        "mutation_authority": False,
        "worker_authority": False,
        "workflow_executed": False,
        "approval_granted": False,
        "governance_mutated": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _escalation_reasons(
    artifact: dict[str, Any],
    policy: dict[str, Any],
    operator_requests_improved_explanation: bool,
    fidelity_requirements: dict[str, Any],
) -> list[str]:
    reasons: list[str] = []
    ambiguity_status = artifact["ambiguity_flags"]["ambiguity_status"]
    if ambiguity_status not in policy["allowed_ambiguity_without_provider"]:
        reasons.append("AMBIGUITY_EXCEEDS_THRESHOLD")
    if _confidence_rank(artifact["confidence"]) < _confidence_rank(policy["minimum_confidence"]):
        reasons.append("CONFIDENCE_BELOW_THRESHOLD")
    if _translation_completeness(artifact) not in policy["acceptable_completeness"]:
        reasons.append("TRANSLATION_COMPLETENESS_INSUFFICIENT")
    missing_fidelity = _missing_fidelity_requirements(artifact, fidelity_requirements)
    if missing_fidelity:
        reasons.append("FIDELITY_REQUIREMENTS_FAIL")
    if operator_requests_improved_explanation:
        reasons.append("OPERATOR_REQUESTED_IMPROVED_EXPLANATION")
    return reasons


def _deterministic_stage_decision(artifact: dict[str, Any], reasons: list[str]) -> dict[str, Any]:
    return {
        "stage": STAGE_DETERMINISTIC,
        "deterministic_translation_hash": artifact["artifact_hash"],
        "confidence": artifact["confidence"],
        "ambiguity_status": artifact["ambiguity_flags"]["ambiguity_status"],
        "escalation_required": bool(reasons),
        "escalation_reasons": list(reasons),
        "authority_granted": False,
    }


def _normalized_policy(policy: dict[str, Any] | None) -> dict[str, Any]:
    value = _optional_mapping(policy, "escalation_policy")
    return {
        "minimum_confidence": _require_confidence(value.get("minimum_confidence", MEDIUM)),
        "allowed_ambiguity_without_provider": _string_list(
            value.get("allowed_ambiguity_without_provider", [NO_AMBIGUITY, MINOR_AMBIGUITY])
        ),
        "acceptable_completeness": _string_list(value.get("acceptable_completeness", ["COMPLETE", "GOVERNANCE_ONLY"])),
        "fallback_allowed": bool(value.get("fallback_allowed", True)),
    }


def _normalized_providers(providers: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    if providers is None:
        return []
    if not isinstance(providers, list):
        raise FailClosedRuntimeError("provider_candidates must be a list")
    normalized = []
    for provider in providers:
        item = _require_mapping(provider, "provider_candidate")
        normalized.append(
            {
                "provider_id": _require_string(item.get("provider_id"), "provider_id"),
                "provider_tier": _require_tier(item.get("provider_tier")),
                "cost_class": _optional_string(item.get("cost_class")) or "UNKNOWN_COST",
                "estimated_cost": _cost_value(item.get("estimated_cost")),
                "provider": item.get("provider"),
            }
        )
    return normalized


def _providers_in_stage_order(providers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    order = {TIER_LOW_COST: 0, TIER_MEDIUM_CAPABILITY: 1, TIER_HIGH_CAPABILITY: 2}
    return sorted(providers, key=lambda item: order[item["provider_tier"]])


def _bounded_task_for(artifact: dict[str, Any]) -> str:
    if artifact["source_direction"] == HUMAN_TO_GOVERNANCE:
        return "Improve or clarify a human-to-governance translation candidate without granting authority."
    return "Improve a governance-to-human explanation without changing authoritative governance state."


def _preservation_requirements(artifact: dict[str, Any], fidelity_requirements: dict[str, Any]) -> dict[str, Any]:
    references = _authoritative_reference_source(artifact)
    return {
        "source_direction": artifact["source_direction"],
        "translation_request_id": artifact["translation_request"]["translation_request_id"],
        "authoritative_references": references,
        "required_fields": _string_list(fidelity_requirements.get("required_fields")),
    }


def _authoritative_reference_source(artifact: dict[str, Any]) -> dict[str, Any]:
    if artifact["source_direction"] == GOVERNANCE_TO_HUMAN:
        payload = artifact["human_readable_payload"].get("authoritative_state_references", {})
        return deepcopy(payload) if isinstance(payload, dict) else {}
    if artifact["source_direction"] == HUMAN_TO_GOVERNANCE:
        payload = artifact["translated_governance_payload"].get("entities", {})
        return deepcopy(payload) if isinstance(payload, dict) else {}
    return {}


def _validate_preserved_references(preserved: dict[str, Any], deterministic_artifact: dict[str, Any]) -> None:
    expected = _authoritative_reference_source(deterministic_artifact)
    if preserved != expected:
        raise FailClosedRuntimeError("TRANSLATION_PROVIDER_AUTHORITATIVE_REFERENCE_FIDELITY_MISMATCH")


def _missing_fidelity_requirements(artifact: dict[str, Any], fidelity_requirements: dict[str, Any]) -> list[str]:
    required = _string_list(fidelity_requirements.get("required_fields"))
    if not required:
        return []
    target_payload = (
        artifact["translated_governance_payload"]
        if artifact["source_direction"] == HUMAN_TO_GOVERNANCE
        else artifact["human_readable_payload"]
    )
    return [field for field in required if field not in target_payload]


def _translation_completeness(artifact: dict[str, Any]) -> str:
    payload = artifact["human_readable_payload"] if artifact["source_direction"] == GOVERNANCE_TO_HUMAN else {}
    completeness = payload.get("translation_completeness") or payload.get("explanation_completeness")
    if isinstance(completeness, str) and completeness.strip():
        return completeness.strip()
    if artifact["confidence"] in {HIGH, MEDIUM}:
        return "COMPLETE"
    return "INCOMPLETE"


def _fallback_reason(attempts: list[dict[str, Any]]) -> str:
    if not attempts:
        return "NO_PROVIDER_CONFIGURED_FOR_REQUIRED_ESCALATION"
    reasons = [attempt.get("rejection_reason") or attempt["attempt_status"] for attempt in attempts]
    return "PROVIDER_ESCALATION_FAILED: " + "; ".join(str(reason) for reason in reasons)


def _aggregate_cost(attempts: list[dict[str, Any]]) -> dict[str, Any]:
    total = 0.0
    count = 0
    by_provider = []
    for attempt in attempts:
        metrics = attempt["cost_metrics"]
        if metrics["estimated_cost"] is not None:
            total += metrics["estimated_cost"]
        count += 1
        by_provider.append(deepcopy(metrics))
    return {
        "provider_attempt_count": count,
        "estimated_total_cost": round(total, 6),
        "cost_units": "USD",
        "by_provider": by_provider,
    }


def _provider_cost(provider_candidate: dict[str, Any], response_artifact: dict[str, Any] | None) -> dict[str, Any]:
    response_cost = response_artifact.get("estimated_cost") if response_artifact else None
    return {
        "provider_id": provider_candidate["provider_id"],
        "provider_tier": provider_candidate["provider_tier"],
        "cost_class": provider_candidate["cost_class"],
        "estimated_cost": response_cost if response_cost is not None else provider_candidate["estimated_cost"],
        "cost_units": response_artifact.get("cost_units") if response_artifact else "USD",
    }


def _validate_attempt_replay(attempt: dict[str, Any], deterministic_artifact: dict[str, Any]) -> None:
    _verify_nested_hash(attempt, "attempt_hash")
    request = _require_mapping(attempt.get("request_artifact"), "request_artifact")
    _verify_nested_hash(request, "artifact_hash")
    if request["deterministic_translation_hash"] != deterministic_artifact["artifact_hash"]:
        raise FailClosedRuntimeError("adaptive translation request deterministic hash mismatch")
    response = attempt.get("response_artifact")
    if isinstance(response, dict):
        _verify_nested_hash(response, "artifact_hash")
    provider_translation = attempt.get("provider_translation_artifact")
    if isinstance(provider_translation, dict):
        validate_universal_translation_artifact(provider_translation)
        _validate_no_authority(provider_translation)


def _validate_no_authority(artifact: dict[str, Any]) -> None:
    flags = artifact.get("authority_flags")
    if isinstance(flags, dict) and any(value is True for value in flags.values()):
        raise FailClosedRuntimeError("adaptive translation artifact cannot grant authority")


def _validate_authority_flags(artifact: dict[str, Any]) -> None:
    for field in (
        "authority_granted",
        "provider_authority",
        "approval_authority",
        "execution_authority",
        "governance_authority",
        "mutation_authority",
        "worker_authority",
        "workflow_executed",
        "approval_granted",
        "governance_mutated",
    ):
        if artifact.get(field) is True:
            raise FailClosedRuntimeError("adaptive translation escalation artifact cannot grant authority")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash", None)
    if not isinstance(actual, str) or replay_hash(expected) != actual:
        raise FailClosedRuntimeError("adaptive translation escalation replay hash mismatch")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    _verify_nested_hash(artifact, "artifact_hash")


def _verify_nested_hash(artifact: dict[str, Any], hash_field: str) -> None:
    actual = artifact.get(hash_field)
    expected = deepcopy(artifact)
    expected.pop(hash_field, None)
    if not isinstance(actual, str) or replay_hash(expected) != actual:
        raise FailClosedRuntimeError("adaptive translation artifact hash mismatch")


def _stage_for_tier(tier: str) -> str:
    if tier == TIER_LOW_COST:
        return STAGE_LOW_COST
    if tier == TIER_MEDIUM_CAPABILITY:
        return STAGE_MEDIUM_CAPABILITY
    if tier == TIER_HIGH_CAPABILITY:
        return STAGE_HIGH_CAPABILITY
    raise FailClosedRuntimeError("provider tier invalid")


def _confidence_rank(confidence: str) -> int:
    return {UNKNOWN: 0, LOW: 1, MEDIUM: 2, HIGH: 3}.get(confidence, 0)


def _require_confidence(value: Any) -> str:
    if value not in {HIGH, MEDIUM, LOW, UNKNOWN}:
        raise FailClosedRuntimeError("adaptive translation provider confidence invalid")
    return value


def _require_tier(value: Any) -> str:
    if value not in ALLOWED_TIERS:
        raise FailClosedRuntimeError("adaptive translation provider tier invalid")
    return value


def _require_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"{field_name} must be a JSON object")
    return deepcopy(value)


def _optional_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"{field_name} must be a JSON object")
    return deepcopy(value)


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _optional_string(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _string_list(values: Any) -> list[str]:
    if values is None:
        return []
    if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
        raise FailClosedRuntimeError("adaptive translation list fields must contain strings")
    return [item.strip() for item in values if item.strip()]


def _cost_value(value: Any) -> float | None:
    if value is None:
        return None
    if not isinstance(value, int | float) or value < 0:
        raise FailClosedRuntimeError("adaptive translation cost must be non-negative number")
    return round(float(value), 6)
