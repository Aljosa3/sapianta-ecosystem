"""Conversation orchestration for clarified human intent routing."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.clarified_intent_resource_selection_ppp_integration_runtime import (
    CLARIFIED_PPP_INTENT_ROUTED,
    route_clarified_resource_selection_intent_to_ppp,
)
from aigol.runtime.clarified_intent_resource_selection_routing_runtime import (
    CLARIFIED_RESOURCE_SELECTION_INTENT_ROUTED,
    route_clarified_intent_to_resource_selection,
)
from aigol.runtime.intent_clarification_cognition_integration import (
    CLARIFIED_COGNITION_INPUT_CREATED,
    integrate_clarification_resolution_with_cognition,
)
from aigol.runtime.intent_clarification_dialog_runtime import (
    CLARIFICATION_RESOLVED,
    run_intent_clarification_dialog,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_CLARIFIED_INTENT_CONVERSATION_ROUTING_INTEGRATION_VERSION = (
    "AIGOL_CLARIFIED_INTENT_CONVERSATION_ROUTING_INTEGRATION_V1"
)
CLARIFIED_INTENT_CONVERSATION_ROUTING_ARTIFACT_V1 = (
    "CLARIFIED_INTENT_CONVERSATION_ROUTING_ARTIFACT_V1"
)
CLARIFIED_INTENT_CONVERSATION_PPP_READY = "CLARIFIED_INTENT_CONVERSATION_PPP_READY"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "clarified_intent_conversation_route_recorded",
    "clarified_intent_conversation_route_returned",
)


def run_clarified_intent_conversation_routing_integration(
    *,
    prompt_id: str,
    human_prompt: str,
    ambiguity_categories: list[str],
    candidate_interpretations: list[dict[str, Any]],
    human_response: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
    canonical_chain_id: str | None = None,
    clarification_history: list[dict[str, Any]] | None = None,
    confidence: str = "DETERMINISTIC",
    provider_necessity_classification: str = "PROVIDER_REQUIRED",
    ppp_stage: str = "PROPOSAL_PRODUCTION",
) -> dict[str, Any]:
    """Route ambiguous conversation intent through the clarified path into PPP-compatible input."""

    root = Path(replay_dir)
    route_replay = root / "clarified_intent_conversation_route"
    chain_id = canonical_chain_id or f"{prompt_id}:CLARIFIED-CHAIN"
    try:
        _ensure_replay_available(route_replay)
        _validate_ambiguity_inputs(
            ambiguity_categories=ambiguity_categories,
            candidate_interpretations=candidate_interpretations,
        )
        clarification = run_intent_clarification_dialog(
            clarification_id=f"{prompt_id}:CLARIFICATION",
            canonical_chain_id=chain_id,
            human_prompt_reference=prompt_id,
            human_prompt=human_prompt,
            ambiguity_categories=ambiguity_categories,
            candidate_interpretations=candidate_interpretations,
            human_response=human_response,
            clarification_history=clarification_history,
            created_at=created_at,
            replay_dir=root / "clarification_dialog",
        )
        if clarification.get("resolution_status") != CLARIFICATION_RESOLVED:
            clarification_reason = clarification.get("failure_reason") or ""
            if "unresolved" in str(clarification_reason):
                clarification_reason = "clarified conversation routing failed closed: clarification unresolved"
            raise FailClosedRuntimeError(
                clarification_reason
                or "clarified conversation routing failed closed: clarification unresolved"
            )
        cognition = integrate_clarification_resolution_with_cognition(
            integration_id=f"{prompt_id}:CLARIFICATION-COGNITION",
            clarification_request_artifact=clarification["human_clarification_request_artifact"],
            clarification_response_artifact=clarification["human_clarification_response_artifact"],
            clarification_resolution_artifact=clarification["human_clarification_resolution_artifact"],
            confidence=confidence,
            created_at=created_at,
            replay_dir=root / "clarification_cognition",
        )
        if cognition.get("integration_status") != CLARIFIED_COGNITION_INPUT_CREATED:
            raise FailClosedRuntimeError(
                cognition.get("failure_reason")
                or "clarified conversation routing failed closed: cognition continuity failed"
            )
        resource_selection = route_clarified_intent_to_resource_selection(
            routing_id=f"{prompt_id}:CLARIFIED-RESOURCE-SELECTION",
            clarified_cognition_input_artifact=cognition["clarified_cognition_input_artifact"],
            clarification_cognition_evidence_artifact=cognition["clarification_cognition_evidence_artifact"],
            clarification_cognition_classification_artifact=cognition[
                "clarification_cognition_classification_artifact"
            ],
            provider_necessity_classification=provider_necessity_classification,
            created_at=created_at,
            replay_dir=root / "clarified_resource_selection_routing",
        )
        if resource_selection.get("routing_status") != CLARIFIED_RESOURCE_SELECTION_INTENT_ROUTED:
            raise FailClosedRuntimeError(
                resource_selection.get("failure_reason")
                or "clarified conversation routing failed closed: resource selection continuity failed"
            )
        ppp = route_clarified_resource_selection_intent_to_ppp(
            routing_id=f"{prompt_id}:CLARIFIED-PPP",
            clarified_resource_selection_routed_intent_artifact=resource_selection[
                "clarified_resource_selection_routed_intent_artifact"
            ],
            clarified_resource_selection_routing_evidence_artifact=resource_selection[
                "clarified_resource_selection_routing_evidence_artifact"
            ],
            clarified_resource_selection_routing_classification_artifact=resource_selection[
                "clarified_resource_selection_routing_classification_artifact"
            ],
            ppp_stage=ppp_stage,
            created_at=created_at,
            replay_dir=root / "clarified_ppp_routing",
        )
        if ppp.get("routing_status") != CLARIFIED_PPP_INTENT_ROUTED:
            raise FailClosedRuntimeError(
                ppp.get("failure_reason")
                or "clarified conversation routing failed closed: PPP continuity failed"
            )
        route = _route_artifact(
            prompt_id=prompt_id,
            route_status=CLARIFIED_INTENT_CONVERSATION_PPP_READY,
            canonical_chain_id=chain_id,
            clarification=clarification,
            cognition=cognition,
            resource_selection=resource_selection,
            ppp=ppp,
            created_at=created_at,
            failure_reason=None,
        )
        returned = _returned_artifact(route)
        _persist_step(route_replay, 0, REPLAY_STEPS[0], route)
        _persist_step(route_replay, 1, REPLAY_STEPS[1], returned)
        return _capture(route, returned, route_replay, clarification, cognition, resource_selection, ppp)
    except Exception as exc:
        route = _failed_route_artifact(
            prompt_id=prompt_id,
            canonical_chain_id=chain_id,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(route)
        _persist_failure_if_possible(route_replay, 0, REPLAY_STEPS[0], route)
        _persist_failure_if_possible(route_replay, 1, REPLAY_STEPS[1], returned)
        return _capture(route, returned, route_replay, None, None, None, None)


def reconstruct_clarified_intent_conversation_routing_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct clarified intent conversation routing replay."""

    replay_path = Path(replay_dir) / "clarified_intent_conversation_route"
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("clarified conversation routing replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("clarified conversation routing replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "clarified conversation routing artifact")
        wrappers.append(wrapper)
    route = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("route_reference") != route["route_id"]:
        raise FailClosedRuntimeError("clarified conversation routing replay reference mismatch")
    if returned.get("route_hash") != route["artifact_hash"]:
        raise FailClosedRuntimeError("clarified conversation routing replay hash mismatch")
    return {
        "route_id": route["route_id"],
        "route_status": route["route_status"],
        "canonical_chain_id": route["canonical_chain_id"],
        "clarification_status": route["clarification_status"],
        "cognition_status": route["cognition_status"],
        "resource_selection_routing_status": route["resource_selection_routing_status"],
        "ppp_routing_status": route["ppp_routing_status"],
        "selected_interpretation": route["selected_interpretation"],
        "domain_reference": route["domain_reference"],
        "proposal_validation_status": route["proposal_validation_status"],
        "approval_evidence_status": route["approval_evidence_status"],
        "handoff_status": route["handoff_status"],
        "failure_reason": route["failure_reason"],
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _validate_ambiguity_inputs(
    *,
    ambiguity_categories: list[str],
    candidate_interpretations: list[dict[str, Any]],
) -> None:
    if not isinstance(ambiguity_categories, list) or not ambiguity_categories:
        raise FailClosedRuntimeError("clarified conversation routing failed closed: ambiguity not detected")
    if not isinstance(candidate_interpretations, list) or len(candidate_interpretations) < 2:
        raise FailClosedRuntimeError("clarified conversation routing failed closed: ambiguity not detected")


def _route_artifact(
    *,
    prompt_id: str,
    route_status: str,
    canonical_chain_id: str,
    clarification: dict[str, Any],
    cognition: dict[str, Any],
    resource_selection: dict[str, Any],
    ppp: dict[str, Any],
    created_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    ppp_contract = ppp["ppp_input_contract"]
    route = {
        "artifact_type": CLARIFIED_INTENT_CONVERSATION_ROUTING_ARTIFACT_V1,
        "runtime_version": AIGOL_CLARIFIED_INTENT_CONVERSATION_ROUTING_INTEGRATION_VERSION,
        "route_id": f"{_require_string(prompt_id, 'prompt_id')}:CLARIFIED-CONVERSATION-ROUTE",
        "prompt_id": prompt_id,
        "route_status": route_status,
        "canonical_chain_id": _require_string(canonical_chain_id, "canonical_chain_id"),
        "clarification_reference": clarification["human_clarification_resolution_artifact"][
            "clarification_resolution_id"
        ],
        "clarification_hash": clarification["human_clarification_resolution_artifact"]["artifact_hash"],
        "clarification_status": clarification["resolution_status"],
        "clarification_history": deepcopy(ppp["clarification_history"]),
        "clarification_history_hash": replay_hash(ppp["clarification_history"]),
        "selected_interpretation": ppp["selected_interpretation"],
        "cognition_reference": cognition["clarified_cognition_input_artifact"][
            "clarified_cognition_input_id"
        ],
        "cognition_hash": cognition["clarified_cognition_input_artifact"]["artifact_hash"],
        "cognition_status": cognition["integration_status"],
        "resource_selection_routing_reference": resource_selection[
            "clarified_resource_selection_routed_intent_artifact"
        ]["clarified_resource_selection_routed_intent_id"],
        "resource_selection_routing_hash": resource_selection[
            "clarified_resource_selection_routed_intent_artifact"
        ]["artifact_hash"],
        "resource_selection_routing_status": resource_selection["routing_status"],
        "ppp_routing_reference": ppp["clarified_ppp_routed_intent_artifact"][
            "clarified_ppp_routed_intent_id"
        ],
        "ppp_routing_hash": ppp["clarified_ppp_routed_intent_artifact"]["artifact_hash"],
        "ppp_routing_status": ppp["routing_status"],
        "ppp_input_contract_hash": replay_hash(ppp_contract),
        "domain_reference": ppp_contract["domain_id"],
        "requested_role_type": ppp_contract["requested_role_type"],
        "provider_necessity_classification": ppp_contract["provider_necessity_classification"],
        "proposal_validation_status": "AWAITING_PROVIDER_PROPOSAL",
        "approval_evidence_status": "AWAITING_VALIDATED_PROPOSAL",
        "handoff_status": "AWAITING_VALIDATED_PROPOSAL",
        "clarification_required": False,
        "approval_required": False,
        "created_at": _require_string(created_at, "created_at"),
        "conversation_orchestration_only": True,
        "proposal_only": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    route["artifact_hash"] = replay_hash(route)
    return route


def _failed_route_artifact(
    *,
    prompt_id: str,
    canonical_chain_id: str,
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    route = {
        "artifact_type": CLARIFIED_INTENT_CONVERSATION_ROUTING_ARTIFACT_V1,
        "runtime_version": AIGOL_CLARIFIED_INTENT_CONVERSATION_ROUTING_INTEGRATION_VERSION,
        "route_id": f"{prompt_id}:CLARIFIED-CONVERSATION-ROUTE"
        if isinstance(prompt_id, str)
        else "INVALID_PROMPT:CLARIFIED-CONVERSATION-ROUTE",
        "prompt_id": prompt_id if isinstance(prompt_id, str) else "INVALID_PROMPT",
        "route_status": FAILED_CLOSED,
        "canonical_chain_id": canonical_chain_id if isinstance(canonical_chain_id, str) else None,
        "clarification_reference": None,
        "clarification_hash": None,
        "clarification_status": None,
        "clarification_history": [],
        "clarification_history_hash": replay_hash([]),
        "selected_interpretation": None,
        "cognition_reference": None,
        "cognition_hash": None,
        "cognition_status": None,
        "resource_selection_routing_reference": None,
        "resource_selection_routing_hash": None,
        "resource_selection_routing_status": None,
        "ppp_routing_reference": None,
        "ppp_routing_hash": None,
        "ppp_routing_status": None,
        "ppp_input_contract_hash": None,
        "domain_reference": None,
        "requested_role_type": None,
        "provider_necessity_classification": None,
        "proposal_validation_status": None,
        "approval_evidence_status": None,
        "handoff_status": None,
        "clarification_required": "clarification unresolved" in failure_reason,
        "approval_required": False,
        "created_at": created_at,
        "conversation_orchestration_only": True,
        "proposal_only": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    route["artifact_hash"] = replay_hash(route)
    return route


def _returned_artifact(route: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(route, "clarified conversation routing artifact")
    returned = {
        "event_type": "CLARIFIED_INTENT_CONVERSATION_ROUTING_RETURNED",
        "route_reference": route["route_id"],
        "route_hash": route["artifact_hash"],
        "route_status": route["route_status"],
        "canonical_chain_id": route["canonical_chain_id"],
        "clarification_status": route["clarification_status"],
        "cognition_status": route["cognition_status"],
        "resource_selection_routing_status": route["resource_selection_routing_status"],
        "ppp_routing_status": route["ppp_routing_status"],
        "proposal_validation_status": route["proposal_validation_status"],
        "approval_evidence_status": route["approval_evidence_status"],
        "handoff_status": route["handoff_status"],
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "failure_reason": route["failure_reason"],
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(
    route: dict[str, Any],
    returned: dict[str, Any],
    replay_path: Path,
    clarification: dict[str, Any] | None,
    cognition: dict[str, Any] | None,
    resource_selection: dict[str, Any] | None,
    ppp: dict[str, Any] | None,
) -> dict[str, Any]:
    capture = {
        "clarified_intent_conversation_routing_artifact": deepcopy(route),
        "clarified_intent_conversation_routing_replay": deepcopy(returned),
        "clarified_intent_conversation_routing_replay_reference": str(replay_path),
        "clarification_dialog": deepcopy(clarification),
        "clarification_cognition_integration": deepcopy(cognition),
        "clarified_resource_selection_routing": deepcopy(resource_selection),
        "clarified_ppp_routing": deepcopy(ppp),
        "route_status": route["route_status"],
        "canonical_chain_id": route["canonical_chain_id"],
        "clarification_status": route["clarification_status"],
        "cognition_status": route["cognition_status"],
        "resource_selection_routing_status": route["resource_selection_routing_status"],
        "ppp_routing_status": route["ppp_routing_status"],
        "selected_interpretation": route["selected_interpretation"],
        "domain_reference": route["domain_reference"],
        "proposal_validation_status": route["proposal_validation_status"],
        "approval_evidence_status": route["approval_evidence_status"],
        "handoff_status": route["handoff_status"],
        "clarification_required": route["clarification_required"],
        "approval_required": route["approval_required"],
        "fail_closed": route["route_status"] == FAILED_CLOSED,
        "failure_reason": route["failure_reason"],
        "conversation_orchestration_only": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
    }
    capture["clarified_intent_conversation_routing_capture_hash"] = replay_hash(capture)
    return capture


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("clarified conversation routing replay step ordering mismatch")
    _verify_artifact_hash(artifact, "clarified conversation routing artifact")
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
        raise FailClosedRuntimeError("clarified conversation routing replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("clarified conversation routing replay hash mismatch")


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{label} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "clarified conversation routing failed closed"
