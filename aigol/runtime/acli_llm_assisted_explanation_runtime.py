"""Optional provider-assisted ACLI explanation runtime.

Provider-assisted explanations are advisory only. ACLI runtime state remains the
source of truth for routing, approval, execution, validation, and replay.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


ACLI_LLM_ASSISTED_EXPLANATION_RUNTIME_VERSION = "ACLI_LLM_ASSISTED_EXPLANATION_PROTOTYPE_V1"
ACLI_LLM_ASSISTED_EXPLANATION_ARTIFACT_V1 = "ACLI_LLM_ASSISTED_EXPLANATION_ARTIFACT_V1"
ACLI_LLM_EXPLANATION_REQUEST_ARTIFACT_V1 = "ACLI_LLM_EXPLANATION_REQUEST_ARTIFACT_V1"
ACLI_LLM_EXPLANATION_RESPONSE_ARTIFACT_V1 = "ACLI_LLM_EXPLANATION_RESPONSE_ARTIFACT_V1"

PROVIDER_EXPLANATION_USED = "PROVIDER_EXPLANATION_USED"
DETERMINISTIC_FALLBACK_USED = "DETERMINISTIC_FALLBACK_USED"
REPLAY_STEP = "acli_llm_assisted_explanation_recorded"

ExplanationProvider = Callable[[dict[str, Any]], dict[str, Any]]


def create_acli_llm_assisted_explanation(
    *,
    explanation_id: str,
    authoritative_state: dict[str, Any],
    deterministic_explanation: str,
    replay_dir: str | Path,
    created_at: str,
    provider: ExplanationProvider | Any | None = None,
    provider_id: str = "UNSPECIFIED_EXPLANATION_PROVIDER",
) -> dict[str, Any]:
    """Create replay-visible optional provider-assisted explanation evidence."""

    replay_path = Path(replay_dir)
    replay_path.mkdir(parents=True, exist_ok=True)
    state = _verified_authoritative_state(authoritative_state)
    deterministic_text = _require_string(deterministic_explanation, "deterministic_explanation")
    request_artifact = _explanation_request_artifact(
        explanation_id=explanation_id,
        authoritative_state=state,
        deterministic_explanation=deterministic_text,
        provider_id=provider_id,
        created_at=created_at,
    )
    provider_response, fallback_reason = _invoke_provider(
        provider=provider,
        request_artifact=request_artifact,
        authoritative_state=state,
    )
    if provider_response is None:
        response_artifact = _deterministic_fallback_response(
            explanation_id=explanation_id,
            provider_id=provider_id,
            deterministic_explanation=deterministic_text,
            fallback_reason=fallback_reason,
            authoritative_state=state,
            created_at=created_at,
        )
        explanation_status = DETERMINISTIC_FALLBACK_USED
    else:
        response_artifact = _provider_response_artifact(
            explanation_id=explanation_id,
            provider_id=provider_id,
            response=provider_response,
            authoritative_state=state,
            created_at=created_at,
        )
        explanation_status = PROVIDER_EXPLANATION_USED

    artifact = {
        "artifact_type": ACLI_LLM_ASSISTED_EXPLANATION_ARTIFACT_V1,
        "runtime_version": ACLI_LLM_ASSISTED_EXPLANATION_RUNTIME_VERSION,
        "explanation_id": _require_string(explanation_id, "explanation_id"),
        "explanation_status": explanation_status,
        "provider_id": _require_string(provider_id, "provider_id"),
        "authoritative_state": deepcopy(state),
        "authoritative_state_hash": state["artifact_hash"],
        "deterministic_explanation": deterministic_text,
        "deterministic_explanation_hash": replay_hash(deterministic_text),
        "explanation_request_artifact": request_artifact,
        "explanation_response_artifact": response_artifact,
        "rendered_explanation": response_artifact["explanation_text"],
        "rendered_explanation_hash": replay_hash(response_artifact["explanation_text"]),
        "provider_invoked": provider is not None,
        "provider_explanation_used": explanation_status == PROVIDER_EXPLANATION_USED,
        "deterministic_fallback_used": explanation_status == DETERMINISTIC_FALLBACK_USED,
        "fallback_reason": response_artifact.get("fallback_reason"),
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": str(replay_path),
        "replay_visible": True,
        "advisory_only": True,
        "visibility_only": True,
        "authority_granted": False,
        "provider_authority": False,
        "approval_authority": False,
        "execution_authority": False,
        "worker_authority": False,
        "governance_authority": False,
        "replay_authority": False,
        "approval_granted": False,
        "execution_authorized": False,
        "mutation_performed": False,
        "worker_invoked": False,
        "validation_executed": False,
        "adaptive_escalation_compatible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    wrapper = {
        "replay_index": 0,
        "replay_step": REPLAY_STEP,
        "event_type": ACLI_LLM_ASSISTED_EXPLANATION_ARTIFACT_V1,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"000_{REPLAY_STEP}.json", wrapper)
    return {
        "runtime_version": ACLI_LLM_ASSISTED_EXPLANATION_RUNTIME_VERSION,
        "explanation_status": explanation_status,
        "llm_assisted_explanation_artifact": deepcopy(artifact),
        "llm_assisted_explanation_replay_reference": str(replay_path),
        "operator_explanation": artifact["rendered_explanation"],
        "replay_visible": True,
        "advisory_only": True,
        "authority_granted": False,
    }


def authoritative_state_from_acli_proposal_capture(
    *,
    state_id: str,
    proposal_capture: dict[str, Any],
    approval_state: str = "APPROVAL_REQUIRED",
    replay_references: list[str] | None = None,
    created_at: str,
) -> dict[str, Any]:
    """Create authoritative explanation state from an ACLI proposal capture."""

    proposal = _require_mapping(proposal_capture, "proposal_capture")
    naming = proposal.get("proposal_naming_decision")
    naming = naming if isinstance(naming, dict) else {}
    proposal_artifact = proposal.get("proposal_artifact")
    proposal_artifact = proposal_artifact if isinstance(proposal_artifact, dict) else {}
    identifier = (
        naming.get("selected_artifact_identifier")
        or naming.get("requested_artifact_identifier")
        or _nested_value(proposal_artifact, "governance_artifact_proposal", "artifact_title")
    )
    target_paths = proposal.get("target_paths")
    if not isinstance(target_paths, list):
        target_paths = []
    replay = list(replay_references or [])
    proposal_replay = proposal.get("replay_reference")
    if isinstance(proposal_replay, str) and proposal_replay:
        replay.append(proposal_replay)
    state = {
        "artifact_type": "ACLI_AUTHORITATIVE_EXPLANATION_STATE_V1",
        "state_id": _require_string(state_id, "state_id"),
        "workflow_id": proposal.get("workflow_id") or "GOVERNED_DEVELOPMENT_WORKFLOW",
        "artifact_identifiers": [_require_string(identifier, "artifact_identifier")] if identifier else [],
        "target_paths": [str(path) for path in target_paths],
        "approval_state": _require_string(approval_state, "approval_state"),
        "proposal_hash": _proposal_hash(proposal),
        "replay_references": _deduplicate_strings(replay),
        "source_capture_hash": proposal.get("artifact_hash"),
        "created_at": _require_string(created_at, "created_at"),
        "authority_granted": False,
        "provider_authority": False,
        "approval_authority": False,
        "execution_authority": False,
    }
    state["artifact_hash"] = replay_hash(state)
    return state


def reconstruct_acli_llm_assisted_explanation_replay(replay_dir: str | Path) -> dict[str, Any]:
    replay_path = Path(replay_dir)
    wrapper = load_json(replay_path / f"000_{REPLAY_STEP}.json")
    if wrapper.get("replay_index") != 0 or wrapper.get("replay_step") != REPLAY_STEP:
        raise FailClosedRuntimeError("ACLI LLM-assisted explanation replay ordering mismatch")
    _verify_wrapper_hash(wrapper)
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("ACLI LLM-assisted explanation artifact missing")
    _verify_artifact_hash(artifact)
    if artifact.get("artifact_type") != ACLI_LLM_ASSISTED_EXPLANATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("ACLI LLM-assisted explanation artifact type mismatch")
    request = _require_mapping(artifact.get("explanation_request_artifact"), "explanation_request_artifact")
    response = _require_mapping(artifact.get("explanation_response_artifact"), "explanation_response_artifact")
    _verify_artifact_hash(request)
    _verify_artifact_hash(response)
    if artifact.get("rendered_explanation_hash") != replay_hash(artifact.get("rendered_explanation")):
        raise FailClosedRuntimeError("ACLI LLM-assisted explanation rendered hash mismatch")
    _validate_response_fidelity(response, artifact["authoritative_state"])
    return {
        "runtime_version": artifact["runtime_version"],
        "explanation_id": artifact["explanation_id"],
        "explanation_status": artifact["explanation_status"],
        "authoritative_state": deepcopy(artifact["authoritative_state"]),
        "explanation_request_artifact": deepcopy(request),
        "explanation_response_artifact": deepcopy(response),
        "rendered_explanation": artifact["rendered_explanation"],
        "rendered_explanation_hash": artifact["rendered_explanation_hash"],
        "provider_explanation_used": artifact["provider_explanation_used"],
        "deterministic_fallback_used": artifact["deterministic_fallback_used"],
        "advisory_only": True,
        "authority_granted": artifact["authority_granted"],
        "replay_artifact_count": 1,
        "replay_hash": replay_hash(wrapper),
    }


def render_acli_llm_assisted_explanation(capture: dict[str, Any]) -> str:
    artifact = capture.get("llm_assisted_explanation_artifact")
    if not isinstance(artifact, dict):
        artifact = capture
    rendered = artifact.get("rendered_explanation")
    if not isinstance(rendered, str) or not rendered.strip():
        raise FailClosedRuntimeError("ACLI LLM-assisted explanation rendered text missing")
    return rendered


def _explanation_request_artifact(
    *,
    explanation_id: str,
    authoritative_state: dict[str, Any],
    deterministic_explanation: str,
    provider_id: str,
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": ACLI_LLM_EXPLANATION_REQUEST_ARTIFACT_V1,
        "explanation_id": _require_string(explanation_id, "explanation_id"),
        "provider_id": _require_string(provider_id, "provider_id"),
        "authoritative_state": deepcopy(authoritative_state),
        "authoritative_state_hash": authoritative_state["artifact_hash"],
        "deterministic_explanation": deterministic_explanation,
        "deterministic_explanation_hash": replay_hash(deterministic_explanation),
        "provider_instruction": (
            "Explain the authoritative ACLI state in plain language. Preserve artifact identifiers, "
            "target paths, approval state, and replay references exactly. Do not authorize execution."
        ),
        "required_preservation": [
            "artifact_identifiers",
            "target_paths",
            "approval_state",
            "replay_references",
        ],
        "advisory_only": True,
        "authority_granted": False,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _invoke_provider(
    *,
    provider: ExplanationProvider | Any | None,
    request_artifact: dict[str, Any],
    authoritative_state: dict[str, Any],
) -> tuple[dict[str, Any] | None, str | None]:
    if provider is None:
        return None, "EXPLANATION_PROVIDER_NOT_CONFIGURED"
    try:
        if callable(provider):
            response = provider(deepcopy(request_artifact))
        elif hasattr(provider, "generate_explanation"):
            response = provider.generate_explanation(deepcopy(request_artifact))
        else:
            return None, "EXPLANATION_PROVIDER_INTERFACE_UNSUPPORTED"
    except Exception as exc:
        return None, f"EXPLANATION_PROVIDER_UNAVAILABLE: {exc}"
    if not isinstance(response, dict):
        return None, "EXPLANATION_PROVIDER_RESPONSE_MALFORMED"
    try:
        _validate_provider_response_payload(response, authoritative_state)
    except FailClosedRuntimeError as exc:
        return None, str(exc)
    return response, None


def _provider_response_artifact(
    *,
    explanation_id: str,
    provider_id: str,
    response: dict[str, Any],
    authoritative_state: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": ACLI_LLM_EXPLANATION_RESPONSE_ARTIFACT_V1,
        "explanation_id": _require_string(explanation_id, "explanation_id"),
        "provider_id": _require_string(provider_id, "provider_id"),
        "response_status": PROVIDER_EXPLANATION_USED,
        "explanation_text": _require_string(response.get("explanation_text"), "explanation_text"),
        "preserved_artifact_identifiers": _string_list(response.get("preserved_artifact_identifiers")),
        "preserved_target_paths": _string_list(response.get("preserved_target_paths")),
        "preserved_approval_state": _require_string(
            response.get("preserved_approval_state"),
            "preserved_approval_state",
        ),
        "preserved_replay_references": _string_list(response.get("preserved_replay_references")),
        "advisory_only": True,
        "authority_granted": False,
        "approval_authority": False,
        "execution_authority": False,
        "created_at": _require_string(created_at, "created_at"),
    }
    _validate_response_fidelity(artifact, authoritative_state)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _deterministic_fallback_response(
    *,
    explanation_id: str,
    provider_id: str,
    deterministic_explanation: str,
    fallback_reason: str | None,
    authoritative_state: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": ACLI_LLM_EXPLANATION_RESPONSE_ARTIFACT_V1,
        "explanation_id": _require_string(explanation_id, "explanation_id"),
        "provider_id": _require_string(provider_id, "provider_id"),
        "response_status": DETERMINISTIC_FALLBACK_USED,
        "explanation_text": deterministic_explanation,
        "fallback_reason": fallback_reason or "DETERMINISTIC_FALLBACK_SELECTED",
        "preserved_artifact_identifiers": list(authoritative_state["artifact_identifiers"]),
        "preserved_target_paths": list(authoritative_state["target_paths"]),
        "preserved_approval_state": authoritative_state["approval_state"],
        "preserved_replay_references": list(authoritative_state["replay_references"]),
        "advisory_only": True,
        "authority_granted": False,
        "approval_authority": False,
        "execution_authority": False,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _verified_authoritative_state(state: dict[str, Any]) -> dict[str, Any]:
    artifact = _require_mapping(state, "authoritative_state")
    required_lists = ("artifact_identifiers", "target_paths", "replay_references")
    for field in required_lists:
        if not isinstance(artifact.get(field), list):
            raise FailClosedRuntimeError(f"ACLI explanation authoritative state missing list: {field}")
    _require_string(artifact.get("approval_state"), "approval_state")
    _verify_artifact_hash(artifact)
    if artifact.get("authority_granted") is True or artifact.get("provider_authority") is True:
        raise FailClosedRuntimeError("ACLI explanation authoritative state cannot grant provider authority")
    return deepcopy(artifact)


def _validate_provider_response_payload(response: dict[str, Any], authoritative_state: dict[str, Any]) -> None:
    if response.get("advisory_only") is not True:
        raise FailClosedRuntimeError("EXPLANATION_PROVIDER_RESPONSE_NOT_ADVISORY")
    if response.get("authority_granted") is True:
        raise FailClosedRuntimeError("EXPLANATION_PROVIDER_RESPONSE_CLAIMS_AUTHORITY")
    _require_string(response.get("explanation_text"), "explanation_text")
    payload = {
        "preserved_artifact_identifiers": _string_list(response.get("preserved_artifact_identifiers")),
        "preserved_target_paths": _string_list(response.get("preserved_target_paths")),
        "preserved_approval_state": _require_string(
            response.get("preserved_approval_state"),
            "preserved_approval_state",
        ),
        "preserved_replay_references": _string_list(response.get("preserved_replay_references")),
    }
    _validate_response_fidelity(payload, authoritative_state)


def _validate_response_fidelity(response: dict[str, Any], authoritative_state: dict[str, Any]) -> None:
    expected = {
        "artifact_identifiers": set(authoritative_state["artifact_identifiers"]),
        "target_paths": set(authoritative_state["target_paths"]),
        "replay_references": set(authoritative_state["replay_references"]),
    }
    actual = {
        "artifact_identifiers": set(_string_list(response.get("preserved_artifact_identifiers"))),
        "target_paths": set(_string_list(response.get("preserved_target_paths"))),
        "replay_references": set(_string_list(response.get("preserved_replay_references"))),
    }
    if actual["artifact_identifiers"] != expected["artifact_identifiers"]:
        raise FailClosedRuntimeError("EXPLANATION_PROVIDER_ARTIFACT_FIDELITY_MISMATCH")
    if actual["target_paths"] != expected["target_paths"]:
        raise FailClosedRuntimeError("EXPLANATION_PROVIDER_TARGET_PATH_FIDELITY_MISMATCH")
    if actual["replay_references"] != expected["replay_references"]:
        raise FailClosedRuntimeError("EXPLANATION_PROVIDER_REPLAY_REFERENCE_FIDELITY_MISMATCH")
    if response.get("preserved_approval_state") != authoritative_state["approval_state"]:
        raise FailClosedRuntimeError("EXPLANATION_PROVIDER_APPROVAL_STATE_FIDELITY_MISMATCH")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash", None)
    if not isinstance(actual, str) or replay_hash(expected) != actual:
        raise FailClosedRuntimeError("ACLI LLM-assisted explanation replay hash mismatch")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash", None)
    if not isinstance(actual, str) or replay_hash(expected) != actual:
        raise FailClosedRuntimeError("ACLI LLM-assisted explanation artifact hash mismatch")


def _proposal_hash(proposal_capture: dict[str, Any]) -> str | None:
    proposal = proposal_capture.get("proposal_artifact")
    if isinstance(proposal, dict) and isinstance(proposal.get("artifact_hash"), str):
        return proposal["artifact_hash"]
    return proposal_capture.get("artifact_hash") if isinstance(proposal_capture.get("artifact_hash"), str) else None


def _nested_value(mapping: dict[str, Any], *keys: str) -> Any:
    value: Any = mapping
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def _deduplicate_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            continue
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _require_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"ACLI LLM-assisted explanation failed closed: {field_name} missing")
    return deepcopy(value)


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"ACLI LLM-assisted explanation failed closed: {field_name} required")
    return value.strip()
