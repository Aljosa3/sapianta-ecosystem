"""Governed unknown-domain clarification workflow for AiGOL conversations."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_UNKNOWN_DOMAIN_AND_CLARIFICATION_UX_V1"
FINAL_CLASSIFICATION = "AIGOL_UNKNOWN_DOMAIN_AND_CLARIFICATION_UX_STATUS"

UNKNOWN_DOMAIN_ARTIFACT_V1 = "UNKNOWN_DOMAIN_ARTIFACT_V1"
CLARIFICATION_REQUEST_ARTIFACT_V1 = "CLARIFICATION_REQUEST_ARTIFACT_V1"

UNKNOWN_DOMAIN = "UNKNOWN_DOMAIN"
INTENT_RESOLVED = "INTENT_RESOLVED"
PROPOSED_DOMAIN = "PROPOSED_DOMAIN"
CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"
NOT_CLARIFICATION_ELIGIBLE = "NOT_CLARIFICATION_ELIGIBLE"
FAILED_CLOSED = "FAILED_CLOSED"

CREATE_DOMAIN = "CREATE_DOMAIN"

KNOWN_DOMAINS = frozenset(
    {
        "AIGOL_CORE",
        "COGNITION",
        "GOVERNANCE",
        "HEALTHCARE",
        "MARKETING",
        "SERVER_MANAGEMENT",
        "TRADING",
    }
)

REPLAY_STEPS = (
    "unknown_domain_recorded",
    "clarification_request_recorded",
    "clarification_workflow_returned",
)


def is_unknown_domain_clarification_eligible(human_prompt: str) -> bool:
    """Return whether a prompt can enter governed unknown-domain clarification."""

    try:
        return _analyze_prompt(human_prompt)["eligible"] is True
    except FailClosedRuntimeError:
        return False


def run_unknown_domain_clarification_workflow(
    *,
    clarification_id: str,
    prompt_id: str,
    human_prompt: str,
    canonical_chain_id: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Persist replay-visible unknown-domain clarification artifacts."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        analysis = _analyze_prompt(human_prompt)
        if analysis["eligible"] is not True:
            raise FailClosedRuntimeError("unknown domain clarification failed closed: prompt is not clarification-eligible")
        unknown_domain = _unknown_domain_artifact(
            clarification_id=clarification_id,
            prompt_id=prompt_id,
            human_prompt=human_prompt,
            canonical_chain_id=canonical_chain_id,
            created_at=created_at,
            replay_reference=str(replay_path),
            analysis=analysis,
        )
        clarification_request = _clarification_request_artifact(
            clarification_id=clarification_id,
            prompt_id=prompt_id,
            canonical_chain_id=canonical_chain_id,
            created_at=created_at,
            replay_reference=str(replay_path),
            unknown_domain=unknown_domain,
            analysis=analysis,
        )
        returned = _returned_artifact(unknown_domain, clarification_request)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], unknown_domain)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], clarification_request)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], returned)
        return _capture(unknown_domain, clarification_request, returned, replay_path)
    except Exception as exc:
        failure_reason = str(exc) if isinstance(exc, FailClosedRuntimeError) else "unknown domain clarification failed closed"
        unknown_domain = _failed_unknown_domain_artifact(
            clarification_id=clarification_id,
            prompt_id=prompt_id,
            human_prompt=human_prompt,
            canonical_chain_id=canonical_chain_id,
            created_at=created_at,
            replay_reference=str(replay_path),
            failure_reason=failure_reason,
        )
        clarification_request = _failed_clarification_request_artifact(
            clarification_id=clarification_id,
            prompt_id=prompt_id,
            canonical_chain_id=canonical_chain_id,
            created_at=created_at,
            replay_reference=str(replay_path),
            unknown_domain=unknown_domain,
            failure_reason=failure_reason,
        )
        returned = _returned_artifact(unknown_domain, clarification_request)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], unknown_domain)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], clarification_request)
        _persist_failure_if_possible(replay_path, 2, REPLAY_STEPS[2], returned)
        return _capture(unknown_domain, clarification_request, returned, replay_path)


def reconstruct_unknown_domain_clarification_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct unknown-domain clarification replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("unknown domain clarification replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("unknown domain clarification replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    unknown_domain = wrappers[0]["artifact"]
    clarification_request = wrappers[1]["artifact"]
    returned = wrappers[2]["artifact"]
    if clarification_request.get("unknown_domain_reference") != unknown_domain["unknown_domain_id"]:
        raise FailClosedRuntimeError("unknown domain clarification reference mismatch")
    if clarification_request.get("unknown_domain_hash") != unknown_domain["artifact_hash"]:
        raise FailClosedRuntimeError("unknown domain clarification hash mismatch")
    if returned.get("clarification_request_reference") != clarification_request["clarification_id"]:
        raise FailClosedRuntimeError("unknown domain clarification returned reference mismatch")
    return {
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "workflow_status": returned["workflow_status"],
        "originating_intent": clarification_request["originating_intent"],
        "proposed_domain": clarification_request["proposed_domain"],
        "missing_information": deepcopy(clarification_request["missing_information"]),
        "unknown_domain_reference": unknown_domain["unknown_domain_id"],
        "clarification_request_reference": clarification_request["clarification_id"],
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "lineage_bound": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_created": False,
        "domain_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "replay_hash": replay_hash(wrappers),
    }


def render_unknown_domain_clarification_workflow(capture: dict[str, Any]) -> str:
    """Render operator-facing clarification workflow text."""

    request = capture.get("clarification_request_artifact") or {}
    unknown = capture.get("unknown_domain_artifact") or {}
    if capture.get("response_status") == FAILED_CLOSED:
        return f"FAILED_CLOSED: {capture.get('failure_reason')}"
    if request.get("clarification_mode") == "DOMAIN_OPTIONS":
        lines = [
            "Unknown Domain Detected",
            "",
            f"Requested Domain: {request.get('proposed_domain')}",
            "",
            "Options:",
        ]
        for index, option in enumerate(request.get("operator_options", []), start=1):
            lines.append(f"{index}. {option['label']}")
        lines.extend(["", "Operator Selection Required"])
        return "\n".join(lines)
    lines = [
        "Clarification Required",
        "",
        f"Detected Intent: {request.get('originating_intent')}",
        f"Proposed Domain: {request.get('proposed_domain') or unknown.get('requested_domain')}",
        "",
        "Please provide:",
    ]
    for item in request.get("missing_information", []):
        lines.append(f"* {item}")
    lines.extend(["", "Operator Response Required"])
    return "\n".join(lines)


def _analyze_prompt(human_prompt: str) -> dict[str, Any]:
    prompt = _require_string(human_prompt, "human_prompt")
    normalized = prompt.lower().strip().rstrip(".")
    if "domain" not in normalized or not any(term in normalized for term in ("create", "new", "add")):
        return {"eligible": False}
    if "trading" in normalized:
        return {"eligible": False}
    if "compliance" in normalized or "regulatory" in normalized:
        if "purpose" in normalized and "capabilit" in normalized and "user" in normalized:
            return {"eligible": False}
        return {
            "eligible": True,
            "originating_intent": CREATE_DOMAIN,
            "requested_domain": "COMPLIANCE",
            "proposed_domain": "COMPLIANCE",
            "domain_known": False,
            "domain_mapping_missing": True,
            "capability_mapping_missing": True,
            "missing_information": ["primary purpose", "expected capabilities", "target users"],
            "clarification_mode": "DOMAIN_DETAILS" if "new domain" in normalized or "regulatory" in normalized else "DOMAIN_OPTIONS",
            "detection_reasons": ["unknown domain", "missing domain mapping", "missing capability mapping"],
        }
    return {"eligible": False}


def _unknown_domain_artifact(
    *,
    clarification_id: str,
    prompt_id: str,
    human_prompt: str,
    canonical_chain_id: str,
    created_at: str,
    replay_reference: str,
    analysis: dict[str, Any],
) -> dict[str, Any]:
    artifact = {
        "artifact_type": UNKNOWN_DOMAIN_ARTIFACT_V1,
        "milestone_id": MILESTONE_ID,
        "unknown_domain_id": f"{_require_string(clarification_id, 'clarification_id')}:UNKNOWN-DOMAIN",
        "prompt_id": _require_string(prompt_id, "prompt_id"),
        "human_prompt_hash": replay_hash(_require_string(human_prompt, "human_prompt")),
        "canonical_chain_id": _require_string(canonical_chain_id, "canonical_chain_id"),
        "unknown_domain_status": UNKNOWN_DOMAIN,
        "originating_intent": analysis["originating_intent"],
        "requested_domain": analysis["requested_domain"],
        "proposed_domain": analysis["proposed_domain"],
        "known_domains": sorted(KNOWN_DOMAINS),
        "domain_known": False,
        "domain_mapping_missing": analysis["domain_mapping_missing"],
        "capability_mapping_missing": analysis["capability_mapping_missing"],
        "detection_reasons": list(analysis["detection_reasons"]),
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_created": False,
        "domain_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _clarification_request_artifact(
    *,
    clarification_id: str,
    prompt_id: str,
    canonical_chain_id: str,
    created_at: str,
    replay_reference: str,
    unknown_domain: dict[str, Any],
    analysis: dict[str, Any],
) -> dict[str, Any]:
    _verify_artifact_hash(unknown_domain)
    artifact = {
        "artifact_type": CLARIFICATION_REQUEST_ARTIFACT_V1,
        "milestone_id": MILESTONE_ID,
        "clarification_id": f"{_require_string(clarification_id, 'clarification_id')}:CLARIFICATION",
        "prompt_id": _require_string(prompt_id, "prompt_id"),
        "canonical_chain_id": _require_string(canonical_chain_id, "canonical_chain_id"),
        "unknown_domain_reference": unknown_domain["unknown_domain_id"],
        "unknown_domain_hash": unknown_domain["artifact_hash"],
        "clarification_status": CLARIFICATION_REQUIRED,
        "originating_intent": analysis["originating_intent"],
        "proposed_domain": analysis["proposed_domain"],
        "missing_information": list(analysis["missing_information"]),
        "clarification_mode": analysis["clarification_mode"],
        "operator_options": _operator_options(analysis["proposed_domain"]),
        "replay_references": {
            "unknown_domain_replay_reference": replay_reference,
            "prompt_id": prompt_id,
            "canonical_chain_id": canonical_chain_id,
        },
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "lineage_bound": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_created": False,
        "domain_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _operator_options(domain: str) -> list[dict[str, Any]]:
    return [
        {
            "option_id": "CREATE_NEW_DOMAIN",
            "label": f"Create new domain {domain}",
            "creates_domain": False,
            "requires_followup_artifact": True,
        },
        {
            "option_id": "MAP_TO_EXISTING_DOMAIN",
            "label": "Map to existing domain",
            "creates_domain": False,
            "requires_followup_artifact": True,
        },
        {
            "option_id": "CANCEL",
            "label": "Cancel",
            "creates_domain": False,
            "requires_followup_artifact": False,
        },
    ]


def _returned_artifact(unknown_domain: dict[str, Any], clarification_request: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(unknown_domain)
    _verify_artifact_hash(clarification_request)
    artifact = {
        "event_type": "UNKNOWN_DOMAIN_CLARIFICATION_WORKFLOW_RETURNED",
        "milestone_id": MILESTONE_ID,
        "workflow_status": clarification_request["clarification_status"],
        "unknown_domain_reference": unknown_domain["unknown_domain_id"],
        "unknown_domain_hash": unknown_domain["artifact_hash"],
        "clarification_request_reference": clarification_request["clarification_id"],
        "clarification_request_hash": clarification_request["artifact_hash"],
        "originating_intent": clarification_request["originating_intent"],
        "proposed_domain": clarification_request["proposed_domain"],
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_created": False,
        "domain_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "failure_reason": clarification_request["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_unknown_domain_artifact(
    *,
    clarification_id: str,
    prompt_id: str,
    human_prompt: Any,
    canonical_chain_id: str,
    created_at: str,
    replay_reference: str,
    failure_reason: str,
) -> dict[str, Any]:
    prompt_hash = replay_hash(human_prompt) if isinstance(human_prompt, str) else None
    artifact = {
        "artifact_type": UNKNOWN_DOMAIN_ARTIFACT_V1,
        "milestone_id": MILESTONE_ID,
        "unknown_domain_id": f"{clarification_id}:UNKNOWN-DOMAIN",
        "prompt_id": prompt_id if isinstance(prompt_id, str) else None,
        "human_prompt_hash": prompt_hash,
        "canonical_chain_id": canonical_chain_id if isinstance(canonical_chain_id, str) else None,
        "unknown_domain_status": FAILED_CLOSED,
        "originating_intent": None,
        "requested_domain": None,
        "proposed_domain": None,
        "known_domains": sorted(KNOWN_DOMAINS),
        "domain_known": None,
        "domain_mapping_missing": None,
        "capability_mapping_missing": None,
        "detection_reasons": [],
        "created_at": created_at if isinstance(created_at, str) else "",
        "replay_reference": replay_reference,
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_created": False,
        "domain_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_clarification_request_artifact(
    *,
    clarification_id: str,
    prompt_id: str,
    canonical_chain_id: str,
    created_at: str,
    replay_reference: str,
    unknown_domain: dict[str, Any],
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": CLARIFICATION_REQUEST_ARTIFACT_V1,
        "milestone_id": MILESTONE_ID,
        "clarification_id": f"{clarification_id}:CLARIFICATION",
        "prompt_id": prompt_id if isinstance(prompt_id, str) else None,
        "canonical_chain_id": canonical_chain_id if isinstance(canonical_chain_id, str) else None,
        "unknown_domain_reference": unknown_domain["unknown_domain_id"],
        "unknown_domain_hash": unknown_domain["artifact_hash"],
        "originating_intent": None,
        "proposed_domain": None,
        "missing_information": [],
        "clarification_mode": None,
        "operator_options": [],
        "replay_references": {},
        "created_at": created_at if isinstance(created_at, str) else "",
        "replay_reference": replay_reference,
        "replay_visible": True,
        "lineage_bound": True,
        "clarification_status": FAILED_CLOSED,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_created": False,
        "domain_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    unknown_domain: dict[str, Any],
    clarification_request: dict[str, Any],
    returned: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "command": "aigol conversation",
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "response_status": returned["workflow_status"],
        "response_source": "UNKNOWN_DOMAIN_CLARIFICATION_WORKFLOW",
        "response_text": "",
        "unknown_domain_artifact": deepcopy(unknown_domain),
        "clarification_request_artifact": deepcopy(clarification_request),
        "clarification_workflow_returned": deepcopy(returned),
        "unknown_domain_replay_reference": str(replay_path),
        "conversation_replay_reference": str(replay_path),
        "canonical_chain_id": clarification_request.get("canonical_chain_id"),
        "current_chain_id": clarification_request.get("canonical_chain_id"),
        "latest_chain_id": clarification_request.get("canonical_chain_id"),
        "fail_closed": returned["workflow_status"] == FAILED_CLOSED,
        "failure_reason": returned.get("failure_reason"),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_created": False,
        "domain_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }
    capture["response_text"] = render_unknown_domain_clarification_workflow(capture)
    capture["unknown_domain_clarification_hash"] = replay_hash(capture)
    return capture


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("unknown domain clarification replay step ordering mismatch")
    _verify_artifact_hash(artifact)
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    try:
        path = replay_dir / f"{index:03d}_{step}.json"
        if not path.exists():
            _persist_step(replay_dir, index, step, artifact)
    except FailClosedRuntimeError:
        return


def _ensure_replay_available(replay_dir: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_dir / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("unknown domain clarification failed closed: replay already exists")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("unknown domain clarification artifact hash is required")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("unknown domain clarification artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("unknown domain clarification replay hash is required")
    expected_input = deepcopy(wrapper)
    expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("unknown domain clarification replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()
