"""Clarification fallback for provider-unavailable conversation prompts."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.intent_clarification_dialog_runtime import (
    ADDITIONAL_CLARIFICATION_REQUIRED,
    HUMAN_CLARIFICATION_REQUEST_ARTIFACT_V1,
    run_intent_clarification_dialog,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_CONVERSATION_PROVIDER_UNAVAILABLE_CLARIFICATION_FALLBACK_VERSION = (
    "AIGOL_CONVERSATION_PROVIDER_UNAVAILABLE_CLARIFICATION_FALLBACK_V1"
)
CONVERSATION_PROVIDER_UNAVAILABLE_CLARIFICATION_FALLBACK_ARTIFACT_V1 = (
    "CONVERSATION_PROVIDER_UNAVAILABLE_CLARIFICATION_FALLBACK_ARTIFACT_V1"
)
CLARIFICATION_FALLBACK_ELIGIBLE = "CLARIFICATION_FALLBACK_ELIGIBLE"
HUMAN_CLARIFICATION_REQUIRED = "HUMAN_CLARIFICATION_REQUIRED"
FAILED_CLOSED = "FAILED_CLOSED"

PROVIDER_UNAVAILABLE_MARKERS = (
    "OpenAI provider unavailable",
    "provider unavailable",
    "provider-assisted conversation failed closed",
)

REPLAY_STEP = "conversation_provider_unavailable_clarification_fallback_recorded"


def run_conversation_provider_unavailable_clarification_fallback(
    *,
    fallback_id: str,
    prompt_id: str,
    human_prompt: str,
    provider_failure_capture: dict[str, Any],
    canonical_chain_id: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Create clarification request evidence when provider conversation is unavailable."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        prompt = _require_string(human_prompt, "human_prompt")
        failure_reason = _provider_failure_reason(provider_failure_capture)
        if not _provider_unavailable(failure_reason):
            raise FailClosedRuntimeError(
                "conversation provider clarification fallback failed closed: provider unavailable not detected"
            )
        ambiguity = _classify_ambiguity(prompt)
        clarification = run_intent_clarification_dialog(
            clarification_id=f"{_require_string(fallback_id, 'fallback_id')}:CLARIFICATION",
            canonical_chain_id=_require_string(canonical_chain_id, "canonical_chain_id"),
            human_prompt_reference=_require_string(prompt_id, "prompt_id"),
            human_prompt=prompt,
            ambiguity_categories=ambiguity["ambiguity_categories"],
            candidate_interpretations=ambiguity["candidate_interpretations"],
            human_response={
                "selected_interpretation": "ADDITIONAL_CLARIFICATION",
                "human_response_text": "Provider unavailable; awaiting bounded human clarification.",
                "resume_stage": "COGNITION",
            },
            created_at=created_at,
            replay_dir=replay_path / "clarification_dialog",
            provider_response_reference=provider_failure_capture.get("conversation_replay_reference"),
            provider_response_hash=provider_failure_capture.get("prompt_to_conversation_capture_hash"),
        )
        request = clarification["human_clarification_request_artifact"]
        if request.get("artifact_type") != HUMAN_CLARIFICATION_REQUEST_ARTIFACT_V1:
            raise FailClosedRuntimeError(
                "conversation provider clarification fallback failed closed: clarification artifact cannot be created"
            )
        artifact = _fallback_artifact(
            fallback_id=fallback_id,
            prompt_id=prompt_id,
            human_prompt=prompt,
            provider_failure_capture=provider_failure_capture,
            provider_failure_reason=failure_reason,
            canonical_chain_id=canonical_chain_id,
            created_at=created_at,
            clarification_capture=clarification,
            fallback_status=HUMAN_CLARIFICATION_REQUIRED,
            eligibility_status=CLARIFICATION_FALLBACK_ELIGIBLE,
            failure_reason=None,
            replay_reference=str(replay_path),
        )
        _persist(replay_path, artifact)
        return _capture(artifact, clarification, provider_failure_capture, replay_path)
    except Exception as exc:
        artifact = _failed_artifact(
            fallback_id=fallback_id,
            prompt_id=prompt_id,
            human_prompt=human_prompt,
            provider_failure_capture=provider_failure_capture,
            canonical_chain_id=canonical_chain_id,
            created_at=created_at,
            replay_reference=str(replay_path),
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, artifact)
        return _capture(artifact, None, provider_failure_capture, replay_path)


def reconstruct_conversation_provider_unavailable_clarification_fallback_replay(
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Reconstruct fallback replay evidence."""

    replay_path = Path(replay_dir)
    wrapper = load_json(replay_path / f"000_{REPLAY_STEP}.json")
    if wrapper.get("replay_index") != 0 or wrapper.get("replay_step") != REPLAY_STEP:
        raise FailClosedRuntimeError("conversation provider clarification fallback replay ordering mismatch")
    _verify_wrapper_hash(wrapper)
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("conversation provider clarification fallback artifact must be a JSON object")
    _verify_artifact_hash(artifact, "conversation provider clarification fallback artifact")
    return {
        "fallback_id": artifact["fallback_id"],
        "fallback_status": artifact["fallback_status"],
        "eligibility_status": artifact["eligibility_status"],
        "canonical_chain_id": artifact["canonical_chain_id"],
        "human_clarification_request_reference": artifact["human_clarification_request_reference"],
        "provider_failure_preserved": artifact["provider_failure_preserved"],
        "fallback_allowed": artifact["fallback_allowed"],
        "failure_reason": artifact["failure_reason"],
        "provider_invoked_by_fallback": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "replay_hash": replay_hash(wrapper),
    }


def render_provider_unavailable_clarification_fallback(capture: dict[str, Any]) -> str:
    request = capture.get("human_clarification_request_artifact") or {}
    if capture.get("fallback_status") == FAILED_CLOSED:
        return f"FAILED_CLOSED: {capture.get('failure_reason')}"
    lines = [
        "HUMAN_CLARIFICATION_REQUIRED",
        "",
        "Provider unavailable before safe conversation resolution.",
        "AiGOL will not guess. Choose one interpretation and resubmit with that clarification.",
        "",
        "Questions:",
    ]
    for question in request.get("bounded_questions", []):
        lines.append(f"- {question}")
    lines.extend(["", "Options:"])
    for candidate in request.get("candidate_interpretations", []):
        lines.append(f"- {candidate['interpretation_id']}: {candidate['label']}")
    return "\n".join(lines)


def _classify_ambiguity(prompt: str) -> dict[str, Any]:
    lowered = prompt.lower().strip()
    if "workstation" in lowered and any(marker in lowered for marker in ("create", "open", "build", "add")):
        return {
            "ambiguity_categories": [
                "DOMAIN_AMBIGUITY",
                "WORKER_AMBIGUITY",
                "CAPABILITY_AMBIGUITY",
                "INTENT_AMBIGUITY",
                "RESOURCE_AMBIGUITY",
            ],
            "candidate_interpretations": [
                {
                    "interpretation_id": "EMPLOYEE_MANAGEMENT_DOMAIN",
                    "label": "Create a new employee-management domain.",
                    "domain_id": "HR",
                    "worker_family_id": "EMPLOYEE_MANAGEMENT",
                    "milestone_type": "DOMAIN_FOUNDATION",
                    "capability_id": "DOMAIN_ARCHITECTURE",
                    "resource_category": "DOMAIN_RUNTIME",
                    "output_scope": "DOMAIN_FOUNDATION",
                    "resume_stage": "COGNITION",
                },
                {
                    "interpretation_id": "OPERATOR_WORKSTATION_TOOL",
                    "label": "Create an operator workstation infrastructure artifact.",
                    "domain_id": "AIGOL_CORE",
                    "worker_family_id": "INFRASTRUCTURE",
                    "milestone_type": "OPERATOR_TOOL_FOUNDATION",
                    "capability_id": "INFRASTRUCTURE",
                    "resource_category": "OPERATOR_TOOL",
                    "output_scope": "INFRASTRUCTURE_FOUNDATION",
                    "resume_stage": "TASK_INTAKE",
                },
                {
                    "interpretation_id": "WORKER_FOUNDATION",
                    "label": "Create a new governed worker foundation.",
                    "domain_id": "AIGOL_CORE",
                    "worker_family_id": "UNRESOLVED_WORKER",
                    "milestone_type": "WORKER_FOUNDATION",
                    "capability_id": "DOMAIN_WORK",
                    "resource_category": "WORKER",
                    "output_scope": "GOVERNANCE_FOUNDATION",
                    "resume_stage": "COGNITION",
                },
            ],
        }
    if lowered in {"improve trading.", "improve trading", "add analysis.", "add analysis", "create reporting.", "create reporting"}:
        return {
            "ambiguity_categories": ["CAPABILITY_AMBIGUITY", "INTENT_AMBIGUITY", "WORKER_AMBIGUITY"],
            "candidate_interpretations": [
                {
                    "interpretation_id": "DOMAIN_CAPABILITY_REQUEST",
                    "label": "Clarify the domain capability to create or improve.",
                    "domain_id": "AIGOL_CORE",
                    "worker_family_id": "UNRESOLVED_WORKER",
                    "milestone_type": "CAPABILITY_FOUNDATION",
                    "capability_id": "UNRESOLVED_CAPABILITY",
                    "resource_category": "WORKER",
                    "output_scope": "GOVERNANCE_FOUNDATION",
                    "resume_stage": "COGNITION",
                }
            ],
        }
    raise FailClosedRuntimeError(
        "conversation provider clarification fallback failed closed: prompt is not clarification-eligible"
    )


def _fallback_artifact(
    *,
    fallback_id: str,
    prompt_id: str,
    human_prompt: str,
    provider_failure_capture: dict[str, Any],
    provider_failure_reason: str,
    canonical_chain_id: str,
    created_at: str,
    clarification_capture: dict[str, Any],
    fallback_status: str,
    eligibility_status: str,
    failure_reason: str | None,
    replay_reference: str,
) -> dict[str, Any]:
    request = clarification_capture["human_clarification_request_artifact"]
    artifact = {
        "artifact_type": CONVERSATION_PROVIDER_UNAVAILABLE_CLARIFICATION_FALLBACK_ARTIFACT_V1,
        "runtime_version": AIGOL_CONVERSATION_PROVIDER_UNAVAILABLE_CLARIFICATION_FALLBACK_VERSION,
        "fallback_id": _require_string(fallback_id, "fallback_id"),
        "prompt_id": _require_string(prompt_id, "prompt_id"),
        "human_prompt_hash": replay_hash(_require_string(human_prompt, "human_prompt")),
        "canonical_chain_id": _require_string(canonical_chain_id, "canonical_chain_id"),
        "provider_failure_reason": provider_failure_reason,
        "provider_failure_hash": replay_hash(provider_failure_capture),
        "provider_failure_preserved": True,
        "eligibility_status": eligibility_status,
        "fallback_allowed": True,
        "fallback_status": fallback_status,
        "clarification_resolution_status": clarification_capture["resolution_status"],
        "human_clarification_request_reference": request["clarification_request_id"],
        "human_clarification_request_hash": request["artifact_hash"],
        "human_clarification_dialog_replay_reference": clarification_capture[
            "human_clarification_dialog_replay_reference"
        ],
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": replay_reference,
        "replay_visible": True,
        "provider_invoked_by_fallback": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_mutated": False,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_artifact(
    *,
    fallback_id: Any,
    prompt_id: Any,
    human_prompt: Any,
    provider_failure_capture: dict[str, Any],
    canonical_chain_id: Any,
    created_at: Any,
    replay_reference: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": CONVERSATION_PROVIDER_UNAVAILABLE_CLARIFICATION_FALLBACK_ARTIFACT_V1,
        "runtime_version": AIGOL_CONVERSATION_PROVIDER_UNAVAILABLE_CLARIFICATION_FALLBACK_VERSION,
        "fallback_id": fallback_id if isinstance(fallback_id, str) else "INVALID_FALLBACK_ID",
        "prompt_id": prompt_id if isinstance(prompt_id, str) else "INVALID_PROMPT_ID",
        "human_prompt_hash": replay_hash(human_prompt) if isinstance(human_prompt, str) else None,
        "canonical_chain_id": canonical_chain_id if isinstance(canonical_chain_id, str) else None,
        "provider_failure_reason": _provider_failure_reason(provider_failure_capture)
        if isinstance(provider_failure_capture, dict)
        else "",
        "provider_failure_hash": replay_hash(provider_failure_capture)
        if isinstance(provider_failure_capture, dict)
        else None,
        "provider_failure_preserved": isinstance(provider_failure_capture, dict),
        "eligibility_status": FAILED_CLOSED,
        "fallback_allowed": False,
        "fallback_status": FAILED_CLOSED,
        "clarification_resolution_status": FAILED_CLOSED,
        "human_clarification_request_reference": None,
        "human_clarification_request_hash": None,
        "human_clarification_dialog_replay_reference": None,
        "created_at": created_at if isinstance(created_at, str) else "",
        "replay_reference": replay_reference,
        "replay_visible": True,
        "provider_invoked_by_fallback": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_mutated": False,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    artifact: dict[str, Any],
    clarification: dict[str, Any] | None,
    provider_failure_capture: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    request = clarification["human_clarification_request_artifact"] if clarification else None
    capture = deepcopy(provider_failure_capture)
    capture.update(
        {
            "conversation_provider_unavailable_clarification_fallback_artifact": deepcopy(artifact),
            "human_clarification_request_artifact": deepcopy(request),
            "clarification_fallback_replay_reference": str(replay_path),
            "conversation_replay_reference": str(replay_path),
            "response_status": artifact["fallback_status"],
            "response_source": "DETERMINISTIC_CLARIFICATION_FALLBACK",
            "response_text": render_provider_unavailable_clarification_fallback(
                {
                    "fallback_status": artifact["fallback_status"],
                    "failure_reason": artifact["failure_reason"],
                    "human_clarification_request_artifact": request,
                }
            ),
            "provider_used": False,
            "provider_invoked": False,
            "worker_invoked": False,
            "authorization_created": False,
            "execution_requested": False,
            "dispatch_requested": False,
            "fail_closed": artifact["fallback_status"] == FAILED_CLOSED,
            "failure_reason": artifact["failure_reason"],
            "fallback_status": artifact["fallback_status"],
            "fallback_allowed": artifact["fallback_allowed"],
            "provider_failure_preserved": artifact["provider_failure_preserved"],
        }
    )
    capture["conversation_provider_unavailable_clarification_fallback_capture_hash"] = replay_hash(capture)
    return capture


def _provider_failure_reason(provider_failure_capture: dict[str, Any]) -> str:
    if not isinstance(provider_failure_capture, dict):
        raise FailClosedRuntimeError(
            "conversation provider clarification fallback failed closed: provider failure evidence missing"
        )
    return str(provider_failure_capture.get("failure_reason") or "")


def _provider_unavailable(reason: str) -> bool:
    lowered = reason.lower()
    return any(marker.lower() in lowered for marker in PROVIDER_UNAVAILABLE_MARKERS)


def _persist(replay_path: Path, artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact, "conversation provider clarification fallback artifact")
    wrapper = {
        "replay_index": 0,
        "replay_step": REPLAY_STEP,
        "event_type": REPLAY_STEP.upper(),
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"000_{REPLAY_STEP}.json", wrapper)


def _persist_failure_if_possible(replay_path: Path, artifact: dict[str, Any]) -> None:
    try:
        _persist(replay_path, artifact)
    except FailClosedRuntimeError:
        pass


def _ensure_replay_available(replay_path: Path) -> None:
    if (replay_path / f"000_{REPLAY_STEP}.json").exists():
        raise FailClosedRuntimeError("append-only runtime artifact already exists: 000_" + REPLAY_STEP + ".json")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError(f"{label} hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("conversation provider clarification fallback replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("conversation provider clarification fallback replay hash mismatch")


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"conversation provider clarification fallback failed closed: {label} missing")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "conversation provider clarification fallback failed closed"
