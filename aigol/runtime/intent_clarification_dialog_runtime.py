"""Deterministic multi-step human intent clarification dialog runtime."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_INTENT_CLARIFICATION_DIALOG_RUNTIME_VERSION = "AIGOL_INTENT_CLARIFICATION_DIALOG_RUNTIME_V1"
HUMAN_CLARIFICATION_REQUEST_ARTIFACT_V1 = "HUMAN_CLARIFICATION_REQUEST_ARTIFACT_V1"
HUMAN_CLARIFICATION_RESPONSE_ARTIFACT_V1 = "HUMAN_CLARIFICATION_RESPONSE_ARTIFACT_V1"
HUMAN_CLARIFICATION_RESOLUTION_ARTIFACT_V1 = "HUMAN_CLARIFICATION_RESOLUTION_ARTIFACT_V1"
CLARIFICATION_RESOLVED = "CLARIFICATION_RESOLVED"
CLARIFICATION_REJECTED = "CLARIFICATION_REJECTED"
CLARIFICATION_CANCELLED = "CLARIFICATION_CANCELLED"
ADDITIONAL_CLARIFICATION_REQUIRED = "ADDITIONAL_CLARIFICATION_REQUIRED"
FAILED_CLOSED = "FAILED_CLOSED"

MAX_CLARIFICATION_STEPS = 3

REPLAY_STEPS = (
    "human_clarification_request_recorded",
    "human_clarification_response_recorded",
    "human_clarification_resolution_recorded",
    "human_clarification_dialog_returned",
)

AMBIGUITY_CATEGORIES = {
    "DOMAIN_AMBIGUITY",
    "WORKER_AMBIGUITY",
    "CAPABILITY_AMBIGUITY",
    "INTENT_AMBIGUITY",
    "RESOURCE_AMBIGUITY",
}

RESUME_STAGES = {
    "COGNITION",
    "TASK_INTAKE",
    "CONTEXT_ASSEMBLY",
    "DOMAIN_AND_WORKER_RESOLUTION",
    "RESOURCE_SELECTION",
    "PPP_ROUTING",
}

SPECIAL_RESPONSES = {"REJECT_ALL", "CANCEL", "ADDITIONAL_CLARIFICATION"}


def run_intent_clarification_dialog(
    *,
    clarification_id: str,
    canonical_chain_id: str,
    human_prompt_reference: str,
    human_prompt: str,
    ambiguity_categories: list[str],
    candidate_interpretations: list[dict[str, Any]],
    human_response: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
    source_artifact_reference: str | None = None,
    source_artifact_hash: str | None = None,
    context_reference: str | None = None,
    context_hash: str | None = None,
    provider_response_reference: str | None = None,
    provider_response_hash: str | None = None,
    clarification_history: list[dict[str, Any]] | None = None,
    max_clarification_steps: int = MAX_CLARIFICATION_STEPS,
) -> dict[str, Any]:
    """Record a bounded clarification request, response, and resolution."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        active_categories = _ambiguity_categories(ambiguity_categories)
        candidates = _candidate_interpretations(candidate_interpretations)
        history = _clarification_history(clarification_history)
        _validate_limit(history, max_clarification_steps)
        request = _request_artifact(
            clarification_id=clarification_id,
            canonical_chain_id=canonical_chain_id,
            human_prompt_reference=human_prompt_reference,
            human_prompt=human_prompt,
            ambiguity_categories=active_categories,
            candidate_interpretations=candidates,
            source_artifact_reference=source_artifact_reference,
            source_artifact_hash=source_artifact_hash,
            context_reference=context_reference,
            context_hash=context_hash,
            provider_response_reference=provider_response_reference,
            provider_response_hash=provider_response_hash,
            clarification_history=history,
            created_at=created_at,
            replay_reference=str(replay_path),
            failure_reason=None,
        )
        response = _response_artifact(
            clarification_id=clarification_id,
            request=request,
            human_response=human_response,
            created_at=created_at,
            replay_reference=str(replay_path),
            failure_reason=None,
        )
        resolution = _resolution_artifact(
            clarification_id=clarification_id,
            request=request,
            response=response,
            created_at=created_at,
            replay_reference=str(replay_path),
        )
        returned = _returned_artifact(resolution)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], request)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], response)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], resolution)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], returned)
        return _capture(request, response, resolution, returned, replay_path)
    except Exception as exc:
        request = _failed_request_artifact(
            clarification_id=clarification_id,
            canonical_chain_id=canonical_chain_id,
            human_prompt_reference=human_prompt_reference,
            human_prompt=human_prompt,
            ambiguity_categories=ambiguity_categories,
            candidate_interpretations=candidate_interpretations,
            created_at=created_at,
            replay_reference=str(replay_path),
            failure_reason=_failure_reason(exc),
        )
        response = _failed_response_artifact(
            clarification_id=clarification_id,
            request=request,
            human_response=human_response,
            created_at=created_at,
            replay_reference=str(replay_path),
        )
        resolution = _failed_resolution_artifact(
            clarification_id=clarification_id,
            request=request,
            response=response,
            created_at=created_at,
            replay_reference=str(replay_path),
            failure_reason=request["failure_reason"],
        )
        returned = _returned_artifact(resolution)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], request)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], response)
        _persist_failure_if_possible(replay_path, 2, REPLAY_STEPS[2], resolution)
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], returned)
        return _capture(request, response, resolution, returned, replay_path)


def reconstruct_intent_clarification_dialog_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct a human intent clarification dialog replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("intent clarification replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("intent clarification replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "intent clarification artifact")
        wrappers.append(wrapper)
    request = wrappers[0]["artifact"]
    response = wrappers[1]["artifact"]
    resolution = wrappers[2]["artifact"]
    returned = wrappers[3]["artifact"]
    if response.get("clarification_request_reference") != request["clarification_request_id"]:
        raise FailClosedRuntimeError("intent clarification request reference mismatch")
    if response.get("clarification_request_hash") != request["artifact_hash"]:
        raise FailClosedRuntimeError("intent clarification request hash mismatch")
    if resolution.get("clarification_request_reference") != request["clarification_request_id"]:
        raise FailClosedRuntimeError("intent clarification resolution request reference mismatch")
    if resolution.get("clarification_response_reference") != response["clarification_response_id"]:
        raise FailClosedRuntimeError("intent clarification response reference mismatch")
    if resolution.get("clarification_response_hash") != response["artifact_hash"]:
        raise FailClosedRuntimeError("intent clarification response hash mismatch")
    if returned.get("clarification_resolution_reference") != resolution["clarification_resolution_id"]:
        raise FailClosedRuntimeError("intent clarification returned reference mismatch")
    if returned.get("clarification_resolution_hash") != resolution["artifact_hash"]:
        raise FailClosedRuntimeError("intent clarification returned hash mismatch")
    return {
        "clarification_resolution_id": resolution["clarification_resolution_id"],
        "resolution_status": resolution["resolution_status"],
        "canonical_chain_id": resolution["canonical_chain_id"],
        "resolved_intent_reference": resolution["resolved_intent_reference"],
        "selected_interpretation": resolution["selected_interpretation"],
        "resume_stage": resolution["resume_stage"],
        "failure_reason": resolution["failure_reason"],
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _request_artifact(
    *,
    clarification_id: str,
    canonical_chain_id: str,
    human_prompt_reference: str,
    human_prompt: str,
    ambiguity_categories: list[str],
    candidate_interpretations: list[dict[str, Any]],
    source_artifact_reference: str | None,
    source_artifact_hash: str | None,
    context_reference: str | None,
    context_hash: str | None,
    provider_response_reference: str | None,
    provider_response_hash: str | None,
    clarification_history: list[dict[str, Any]],
    created_at: str,
    replay_reference: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": HUMAN_CLARIFICATION_REQUEST_ARTIFACT_V1,
        "runtime_version": AIGOL_INTENT_CLARIFICATION_DIALOG_RUNTIME_VERSION,
        "clarification_request_id": f"{_require_string(clarification_id, 'clarification_id')}:REQUEST",
        "clarification_reference": clarification_id,
        "canonical_chain_id": _require_string(canonical_chain_id, "canonical_chain_id"),
        "human_prompt_reference": _require_string(human_prompt_reference, "human_prompt_reference"),
        "human_prompt_hash": replay_hash(_require_string(human_prompt, "human_prompt")),
        "ambiguity_categories": deepcopy(ambiguity_categories),
        "clarification_reason": _clarification_reason(ambiguity_categories),
        "bounded_questions": _bounded_questions(ambiguity_categories),
        "source_artifact_reference": source_artifact_reference,
        "source_artifact_hash": source_artifact_hash,
        "context_reference": context_reference,
        "context_hash": context_hash,
        "provider_response_reference": provider_response_reference,
        "provider_response_hash": provider_response_hash,
        "candidate_interpretations": deepcopy(candidate_interpretations),
        "allowed_response_scope": _allowed_response_scope(candidate_interpretations),
        "resume_candidate_stages": sorted(RESUME_STAGES),
        "clarification_history": deepcopy(clarification_history),
        "clarification_history_hash": replay_hash(clarification_history),
        "request_status": "CLARIFICATION_REQUESTED" if failure_reason is None else FAILED_CLOSED,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": replay_reference,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _response_artifact(
    *,
    clarification_id: str,
    request: dict[str, Any],
    human_response: dict[str, Any],
    created_at: str,
    replay_reference: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    if not isinstance(human_response, dict):
        raise FailClosedRuntimeError("intent clarification failed closed: human response missing")
    selected = _require_string(human_response.get("selected_interpretation"), "selected_interpretation")
    resume_stage = _normalize_resume_stage(human_response.get("resume_stage"))
    artifact = {
        "artifact_type": HUMAN_CLARIFICATION_RESPONSE_ARTIFACT_V1,
        "runtime_version": AIGOL_INTENT_CLARIFICATION_DIALOG_RUNTIME_VERSION,
        "clarification_response_id": f"{_require_string(clarification_id, 'clarification_id')}:RESPONSE",
        "clarification_request_reference": request["clarification_request_id"],
        "clarification_request_hash": request["artifact_hash"],
        "canonical_chain_id": request["canonical_chain_id"],
        "selected_interpretation": selected,
        "selected_domain_id": _optional_string(human_response.get("selected_domain_id")),
        "selected_worker_family_id": _optional_string(human_response.get("selected_worker_family_id")),
        "selected_milestone_type": _optional_string(human_response.get("selected_milestone_type")),
        "selected_output_scope": _optional_string(human_response.get("selected_output_scope")),
        "human_response_text_hash": replay_hash(_optional_string(human_response.get("human_response_text")) or ""),
        "resume_stage": resume_stage,
        "response_status": "CLARIFICATION_RESPONSE_RECORDED" if failure_reason is None else FAILED_CLOSED,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": replay_reference,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _resolution_artifact(
    *,
    clarification_id: str,
    request: dict[str, Any],
    response: dict[str, Any],
    created_at: str,
    replay_reference: str,
) -> dict[str, Any]:
    status, reason, resolved = _resolve(request, response)
    artifact = {
        "artifact_type": HUMAN_CLARIFICATION_RESOLUTION_ARTIFACT_V1,
        "runtime_version": AIGOL_INTENT_CLARIFICATION_DIALOG_RUNTIME_VERSION,
        "clarification_resolution_id": f"{_require_string(clarification_id, 'clarification_id')}:RESOLUTION",
        "clarification_request_reference": request["clarification_request_id"],
        "clarification_request_hash": request["artifact_hash"],
        "clarification_response_reference": response["clarification_response_id"],
        "clarification_response_hash": response["artifact_hash"],
        "canonical_chain_id": request["canonical_chain_id"],
        "resolution_status": status,
        "resolved_intent_reference": f"{clarification_id}:RESOLVED-INTENT" if resolved else None,
        "resolved_intent": deepcopy(resolved),
        "selected_interpretation": response["selected_interpretation"],
        "resume_stage": response["resume_stage"] if status == CLARIFICATION_RESOLVED else None,
        "clarification_history": request["clarification_history"]
        + [
            {
                "clarification_request_reference": request["clarification_request_id"],
                "clarification_response_reference": response["clarification_response_id"],
                "resolution_status": status,
            }
        ],
        "clarification_history_preserved": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": replay_reference,
        "replay_visible": True,
        "failure_reason": reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_request_artifact(
    *,
    clarification_id: str,
    canonical_chain_id: str,
    human_prompt_reference: str,
    human_prompt: str,
    ambiguity_categories: list[str],
    candidate_interpretations: list[dict[str, Any]],
    created_at: str,
    replay_reference: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": HUMAN_CLARIFICATION_REQUEST_ARTIFACT_V1,
        "runtime_version": AIGOL_INTENT_CLARIFICATION_DIALOG_RUNTIME_VERSION,
        "clarification_request_id": f"{clarification_id}:REQUEST" if isinstance(clarification_id, str) else "INVALID:REQUEST",
        "clarification_reference": clarification_id if isinstance(clarification_id, str) else "INVALID",
        "canonical_chain_id": canonical_chain_id if isinstance(canonical_chain_id, str) else None,
        "human_prompt_reference": human_prompt_reference if isinstance(human_prompt_reference, str) else None,
        "human_prompt_hash": replay_hash(human_prompt) if isinstance(human_prompt, str) else None,
        "ambiguity_categories": ambiguity_categories if isinstance(ambiguity_categories, list) else [],
        "clarification_reason": "Clarification failed closed before request completion.",
        "bounded_questions": [],
        "source_artifact_reference": None,
        "source_artifact_hash": None,
        "context_reference": None,
        "context_hash": None,
        "provider_response_reference": None,
        "provider_response_hash": None,
        "candidate_interpretations": candidate_interpretations if isinstance(candidate_interpretations, list) else [],
        "allowed_response_scope": [],
        "resume_candidate_stages": [],
        "clarification_history": [],
        "clarification_history_hash": replay_hash([]),
        "request_status": FAILED_CLOSED,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "created_at": created_at,
        "replay_reference": replay_reference,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_response_artifact(
    *,
    clarification_id: str,
    request: dict[str, Any],
    human_response: dict[str, Any],
    created_at: str,
    replay_reference: str,
) -> dict[str, Any]:
    selected = human_response.get("selected_interpretation") if isinstance(human_response, dict) else None
    artifact = {
        "artifact_type": HUMAN_CLARIFICATION_RESPONSE_ARTIFACT_V1,
        "runtime_version": AIGOL_INTENT_CLARIFICATION_DIALOG_RUNTIME_VERSION,
        "clarification_response_id": f"{clarification_id}:RESPONSE" if isinstance(clarification_id, str) else "INVALID:RESPONSE",
        "clarification_request_reference": request["clarification_request_id"],
        "clarification_request_hash": request["artifact_hash"],
        "canonical_chain_id": request["canonical_chain_id"],
        "selected_interpretation": selected,
        "selected_domain_id": None,
        "selected_worker_family_id": None,
        "selected_milestone_type": None,
        "selected_output_scope": None,
        "human_response_text_hash": None,
        "resume_stage": None,
        "response_status": FAILED_CLOSED,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "created_at": created_at,
        "replay_reference": replay_reference,
        "replay_visible": True,
        "failure_reason": request["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_resolution_artifact(
    *,
    clarification_id: str,
    request: dict[str, Any],
    response: dict[str, Any],
    created_at: str,
    replay_reference: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": HUMAN_CLARIFICATION_RESOLUTION_ARTIFACT_V1,
        "runtime_version": AIGOL_INTENT_CLARIFICATION_DIALOG_RUNTIME_VERSION,
        "clarification_resolution_id": f"{clarification_id}:RESOLUTION"
        if isinstance(clarification_id, str)
        else "INVALID:RESOLUTION",
        "clarification_request_reference": request["clarification_request_id"],
        "clarification_request_hash": request["artifact_hash"],
        "clarification_response_reference": response["clarification_response_id"],
        "clarification_response_hash": response["artifact_hash"],
        "canonical_chain_id": request["canonical_chain_id"],
        "resolution_status": FAILED_CLOSED,
        "resolved_intent_reference": None,
        "resolved_intent": None,
        "selected_interpretation": response["selected_interpretation"],
        "resume_stage": None,
        "clarification_history": request["clarification_history"],
        "clarification_history_preserved": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "created_at": created_at,
        "replay_reference": replay_reference,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(resolution: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(resolution, "intent clarification resolution artifact")
    artifact = {
        "event_type": "INTENT_CLARIFICATION_DIALOG_RETURNED",
        "clarification_resolution_reference": resolution["clarification_resolution_id"],
        "clarification_resolution_hash": resolution["artifact_hash"],
        "resolution_status": resolution["resolution_status"],
        "resolved_intent_reference": resolution["resolved_intent_reference"],
        "resume_stage": resolution["resume_stage"],
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "failure_reason": resolution["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    request: dict[str, Any],
    response: dict[str, Any],
    resolution: dict[str, Any],
    returned: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "human_clarification_request_artifact": deepcopy(request),
        "human_clarification_response_artifact": deepcopy(response),
        "human_clarification_resolution_artifact": deepcopy(resolution),
        "human_clarification_dialog_replay": deepcopy(returned),
        "human_clarification_dialog_replay_reference": str(replay_path),
        "resolution_status": resolution["resolution_status"],
        "canonical_chain_id": resolution["canonical_chain_id"],
        "resolved_intent": deepcopy(resolution["resolved_intent"]),
        "resume_stage": resolution["resume_stage"],
        "clarification_history": deepcopy(resolution["clarification_history"]),
        "fail_closed": resolution["resolution_status"] == FAILED_CLOSED,
        "failure_reason": resolution["failure_reason"],
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
    }
    capture["intent_clarification_dialog_capture_hash"] = replay_hash(capture)
    return capture


def _resolve(request: dict[str, Any], response: dict[str, Any]) -> tuple[str, str | None, dict[str, Any] | None]:
    if response["canonical_chain_id"] != request["canonical_chain_id"]:
        return FAILED_CLOSED, "intent clarification failed closed: chain continuity failed", None
    selected = response["selected_interpretation"]
    if selected == "CANCEL":
        return CLARIFICATION_CANCELLED, "intent clarification cancelled by human", None
    if selected == "REJECT_ALL":
        return CLARIFICATION_REJECTED, "intent clarification rejected all candidates", None
    if selected == "ADDITIONAL_CLARIFICATION":
        return ADDITIONAL_CLARIFICATION_REQUIRED, "intent clarification requires another bounded question", None
    candidates = {candidate["interpretation_id"]: candidate for candidate in request["candidate_interpretations"]}
    if selected not in candidates:
        return FAILED_CLOSED, "intent clarification failed closed: ambiguity remains unresolved", None
    candidate = candidates[selected]
    contradiction = _contradiction(candidate, response)
    if contradiction:
        return FAILED_CLOSED, "intent clarification failed closed: contradictory answers detected", None
    resolved = {
        "intent_reference": f"{request['clarification_reference']}:RESOLVED-INTENT",
        "intent_source": "HUMAN_CLARIFICATION",
        "domain_id": candidate["domain_id"],
        "worker_family_id": candidate.get("worker_family_id"),
        "milestone_type": candidate.get("milestone_type"),
        "capability_id": candidate.get("capability_id"),
        "resource_category": candidate.get("resource_category"),
        "output_scope": candidate.get("output_scope"),
        "resume_stage": response["resume_stage"],
        "source_prompt_reference": request["human_prompt_reference"],
        "source_clarification_request": request["clarification_request_id"],
        "source_clarification_response": response["clarification_response_id"],
        "source_visible_to_cognition": False,
        "proposal_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
    }
    return CLARIFICATION_RESOLVED, None, resolved


def _contradiction(candidate: dict[str, Any], response: dict[str, Any]) -> bool:
    checks = {
        "selected_domain_id": "domain_id",
        "selected_worker_family_id": "worker_family_id",
        "selected_milestone_type": "milestone_type",
        "selected_output_scope": "output_scope",
    }
    for response_field, candidate_field in checks.items():
        value = response.get(response_field)
        if value is not None and value != candidate.get(candidate_field):
            return True
    return False


def _ambiguity_categories(values: list[str]) -> list[str]:
    if not isinstance(values, list) or not values:
        raise FailClosedRuntimeError("intent clarification failed closed: ambiguity category missing")
    categories = []
    for value in values:
        category = _require_string(value, "ambiguity_category").strip().upper().replace("-", "_").replace(" ", "_")
        if category not in AMBIGUITY_CATEGORIES:
            raise FailClosedRuntimeError("intent clarification failed closed: ambiguity category unsupported")
        categories.append(category)
    return sorted(set(categories))


def _candidate_interpretations(values: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(values, list) or not values:
        raise FailClosedRuntimeError("intent clarification failed closed: candidate interpretations missing")
    normalized = []
    seen: set[str] = set()
    for value in values:
        if not isinstance(value, dict):
            raise FailClosedRuntimeError("intent clarification failed closed: candidate interpretations missing")
        interpretation_id = _require_string(value.get("interpretation_id"), "interpretation_id")
        if interpretation_id in seen:
            raise FailClosedRuntimeError("intent clarification failed closed: contradictory answers detected")
        seen.add(interpretation_id)
        normalized.append(
            {
                "interpretation_id": interpretation_id,
                "label": _require_string(value.get("label"), "label"),
                "domain_id": _require_string(value.get("domain_id"), "domain_id"),
                "worker_family_id": _optional_string(value.get("worker_family_id")),
                "milestone_type": _optional_string(value.get("milestone_type")),
                "capability_id": _optional_string(value.get("capability_id")),
                "resource_category": _optional_string(value.get("resource_category")),
                "output_scope": _optional_string(value.get("output_scope")),
                "resume_stage": _normalize_resume_stage(value.get("resume_stage", "COGNITION")),
            }
        )
    return normalized


def _clarification_history(value: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise FailClosedRuntimeError("intent clarification failed closed: clarification history invalid")
    return deepcopy(value)


def _validate_limit(history: list[dict[str, Any]], limit: int) -> None:
    if not isinstance(limit, int) or limit < 1:
        raise FailClosedRuntimeError("intent clarification failed closed: clarification limit invalid")
    if len(history) >= limit:
        raise FailClosedRuntimeError("intent clarification failed closed: clarification exceeds limits")


def _allowed_response_scope(candidates: list[dict[str, Any]]) -> list[str]:
    return [candidate["interpretation_id"] for candidate in candidates] + sorted(SPECIAL_RESPONSES)


def _bounded_questions(categories: list[str]) -> list[str]:
    questions = {
        "DOMAIN_AMBIGUITY": "Which domain should this request target?",
        "WORKER_AMBIGUITY": "Which worker family should this request target?",
        "CAPABILITY_AMBIGUITY": "Which capability is being requested?",
        "INTENT_AMBIGUITY": "Which interpretation should AiGOL use?",
        "RESOURCE_AMBIGUITY": "Which resource category should this request use?",
    }
    return [questions[category] for category in categories]


def _clarification_reason(categories: list[str]) -> str:
    return "Ambiguous human intent requires bounded clarification: " + ", ".join(categories)


def _normalize_resume_stage(value: Any) -> str:
    stage = _require_string(value, "resume_stage").strip().upper().replace("-", "_").replace(" ", "_")
    if stage not in RESUME_STAGES:
        raise FailClosedRuntimeError("intent clarification failed closed: resume stage unsupported")
    return stage


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"intent clarification failed closed: {label} missing")
    return value


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError("intent clarification failed closed: optional field invalid")
    return value


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("intent clarification replay step ordering mismatch")
    _verify_artifact_hash(artifact, "intent clarification artifact")
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
        raise FailClosedRuntimeError("intent clarification replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("intent clarification replay hash mismatch")


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "intent clarification failed closed"
