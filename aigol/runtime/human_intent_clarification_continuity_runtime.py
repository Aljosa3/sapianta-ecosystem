"""Replay-visible continuity for human-intent clarification intake."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.clarification_lifecycle_resolution_runtime import active_clarification_state
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_HUMAN_INTENT_CLARIFICATION_CONTINUITY_RUNTIME_V1 = (
    "AIGOL_HUMAN_INTENT_CLARIFICATION_CONTINUITY_RUNTIME_V1"
)
HUMAN_INTENT_CLARIFICATION_CONTINUITY_STATUS = "HUMAN_INTENT_CLARIFICATION_CONTINUITY_STATUS"

HUMAN_INTENT_CLARIFICATION_REPLY_BINDING_ARTIFACT_V1 = (
    "HUMAN_INTENT_CLARIFICATION_REPLY_BINDING_ARTIFACT_V1"
)
HUMAN_INTENT_CLARIFICATION_RESPONSE_ARTIFACT_V1 = "HUMAN_INTENT_CLARIFICATION_RESPONSE_ARTIFACT_V1"
HUMAN_INTENT_WORKFLOW_TARGET_REFINEMENT_ARTIFACT_V1 = (
    "HUMAN_INTENT_WORKFLOW_TARGET_REFINEMENT_ARTIFACT_V1"
)
HUMAN_INTENT_CLARIFICATION_RESOLUTION_ARTIFACT_V1 = "HUMAN_INTENT_CLARIFICATION_RESOLUTION_ARTIFACT_V1"
HUMAN_INTENT_WORKFLOW_SELECTION_AFTER_CLARIFICATION_ARTIFACT_V1 = (
    "HUMAN_INTENT_WORKFLOW_SELECTION_AFTER_CLARIFICATION_ARTIFACT_V1"
)

HUMAN_INTENT_CLARIFICATION_INTAKE = "HUMAN_INTENT_CLARIFICATION_INTAKE"
AMBIGUOUS_INTENT = "AMBIGUOUS_INTENT"
GENERAL_IMPROVEMENT_INTENT = "GENERAL_IMPROVEMENT_INTENT"
CONTINUATION_INTENT = "CONTINUATION_INTENT"
CREATE_DOMAIN_COMPLIANCE_CLARIFICATION = "CREATE_DOMAIN_COMPLIANCE_CLARIFICATION"
OCS_LLM_COGNITION = "OCS_LLM_COGNITION"
BOUNDED_FILE_WRITE_WORKER_USER_SESSION = "BOUNDED_FILE_WRITE_WORKER_USER_SESSION"
SUPPORTED_TARGET_WORKFLOWS = frozenset(
    {CREATE_DOMAIN_COMPLIANCE_CLARIFICATION, OCS_LLM_COGNITION, BOUNDED_FILE_WRITE_WORKER_USER_SESSION}
)
WORKFLOW_SELECTED = "WORKFLOW_SELECTED"
WORKFLOW_SELECTION_AFTER_CLARIFICATION = "WORKFLOW_SELECTION_AFTER_CLARIFICATION"
WORKFLOW_TARGET_REFINED_AFTER_CLARIFICATION = "WORKFLOW_TARGET_REFINED_AFTER_CLARIFICATION"
TARGET_PRESERVED_LOW_CONFIDENCE = "TARGET_PRESERVED_LOW_CONFIDENCE"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "human_intent_clarification_reply_binding_recorded",
    "human_intent_clarification_response_recorded",
    "human_intent_workflow_target_refinement_recorded",
    "human_intent_clarification_resolution_recorded",
    "human_intent_workflow_selection_after_clarification_recorded",
)


def continue_human_intent_clarification_to_workflow(
    *,
    continuity_id: str,
    session_root: str | Path,
    turn_id: str,
    prompt_id: str,
    clarification_response: str,
    current_chain_id: str | None,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Bind a human-intent clarification response and select the expected workflow."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        state = _require_human_intent_state(Path(session_root))
        _validate_state(state=state, current_chain_id=current_chain_id)
        binding = _binding_artifact(
            continuity_id=continuity_id,
            state=state,
            turn_id=turn_id,
            prompt_id=prompt_id,
            clarification_response=clarification_response,
            created_at=created_at,
            replay_reference=str(replay_path),
        )
        response = _response_artifact(
            continuity_id=continuity_id,
            state=state,
            binding=binding,
            clarification_response=clarification_response,
            created_at=created_at,
        )
        refinement = _target_refinement_artifact(
            continuity_id=continuity_id,
            state=state,
            response=response,
            clarification_response=clarification_response,
            created_at=created_at,
        )
        resolution = _resolution_artifact(
            continuity_id=continuity_id,
            state=state,
            response=response,
            refinement=refinement,
            clarification_response=clarification_response,
            created_at=created_at,
        )
        selection = _selection_artifact(
            continuity_id=continuity_id,
            state=state,
            refinement=refinement,
            resolution=resolution,
            created_at=created_at,
        )
        _persist_step(replay_path, 0, REPLAY_STEPS[0], binding)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], response)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], refinement)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], resolution)
        _persist_step(replay_path, 4, REPLAY_STEPS[4], selection)
        return _capture(binding, response, refinement, resolution, selection, state, replay_path)
    except Exception as exc:
        failure_reason = str(exc) if isinstance(exc, FailClosedRuntimeError) else "human intent clarification continuity failed closed"
        return _failed_capture(
            continuity_id=continuity_id,
            turn_id=turn_id,
            prompt_id=prompt_id,
            current_chain_id=current_chain_id,
            created_at=created_at,
            replay_reference=str(replay_path),
            failure_reason=failure_reason,
        )


def reconstruct_human_intent_clarification_continuity_replay(replay_dir: str | Path) -> dict[str, Any]:
    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("human intent clarification continuity replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("human intent clarification continuity artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    refinement = wrappers[2]["artifact"]
    selection = wrappers[4]["artifact"]
    return {
        "runtime_version": AIGOL_HUMAN_INTENT_CLARIFICATION_CONTINUITY_RUNTIME_V1,
        "final_classification": HUMAN_INTENT_CLARIFICATION_CONTINUITY_STATUS,
        "workflow_id": selection["workflow_id"],
        "routing_status": selection["routing_status"],
        "workflow_target_refinement_status": refinement["refinement_status"],
        "workflow_target_refinement_reason": refinement["refinement_reason"],
        "ambiguity_escalation_reason": refinement["ambiguity_escalation_reason"],
        "unresolved_ambiguity_classification": refinement["unresolved_ambiguity_classification"],
        "proposal_only_cognition_routing": refinement["proposal_only_cognition_routing"],
        "human_confirmation_required": refinement["human_confirmation_required"],
        "future_deterministic_rule_candidate_status": refinement["future_deterministic_rule_candidate_status"],
        "original_workflow_targets": deepcopy(refinement["original_expected_workflow_targets"]),
        "refined_workflow_targets": deepcopy(refinement["refined_workflow_targets"]),
        "clarification_response_bound": True,
        "intent_resolution_after_clarification": True,
        "workflow_selection_after_clarification": True,
        "canonical_chain_id": selection["canonical_chain_id"],
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "replay_hash": replay_hash(wrappers),
    }


def render_human_intent_clarification_continuity_summary(capture: dict[str, Any]) -> str:
    if capture.get("fail_closed") is True:
        return f"FAILED_CLOSED: {capture.get('failure_reason')}"
    return "\n".join(
        [
            "Human Intent Clarification Bound",
            f"Intent Family: {capture.get('intent_family')}",
            f"Selected Workflow: {capture.get('workflow_id')}",
            f"Workflow Target Refinement: {capture.get('workflow_target_refinement_status')}",
            f"Refinement Reason: {capture.get('workflow_target_refinement_reason')}",
            f"Ambiguity Escalation: {capture.get('ambiguity_escalation_reason') or 'NO'}",
            "Proposal-Only Cognition Routing: "
            + ("YES" if capture.get("proposal_only_cognition_routing") is True else "NO"),
            "Human Confirmation Required: "
            + ("YES" if capture.get("human_confirmation_required") is True else "NO"),
            "Workflow Selection After Clarification: YES",
            "No provider invoked.",
            "No worker invoked.",
            "No execution requested.",
        ]
    )


def _require_human_intent_state(session_root: Path) -> dict[str, Any]:
    state = active_clarification_state(session_root=session_root)
    if not isinstance(state, dict):
        raise FailClosedRuntimeError("human intent clarification continuity failed closed: missing active clarification")
    if state.get("originating_workflow_id") != HUMAN_INTENT_CLARIFICATION_INTAKE:
        raise FailClosedRuntimeError("human intent clarification continuity failed closed: workflow mismatch")
    return state


def _validate_state(*, state: dict[str, Any], current_chain_id: str | None) -> None:
    request = state["clarification_request_artifact"]
    chain_id = request.get("canonical_chain_id")
    if current_chain_id is not None and current_chain_id != chain_id:
        raise FailClosedRuntimeError("human intent clarification continuity failed closed: chain mismatch")
    _initial_workflow_target(request)


def _initial_workflow_target(request: dict[str, Any]) -> str:
    targets = request.get("expected_workflow_targets")
    if not isinstance(targets, list) or not targets:
        raise FailClosedRuntimeError("human intent clarification continuity failed closed: target workflow missing")
    selected = targets[0]
    if selected not in SUPPORTED_TARGET_WORKFLOWS:
        raise FailClosedRuntimeError("human intent clarification continuity failed closed: unsupported target workflow")
    return selected


def _selected_workflow_id(refinement: dict[str, Any]) -> str:
    selected = refinement.get("selected_workflow_id")
    if selected not in SUPPORTED_TARGET_WORKFLOWS:
        raise FailClosedRuntimeError("human intent clarification continuity failed closed: unsupported refined target workflow")
    return selected


def _binding_artifact(
    *,
    continuity_id: str,
    state: dict[str, Any],
    turn_id: str,
    prompt_id: str,
    clarification_response: str,
    created_at: str,
    replay_reference: str,
) -> dict[str, Any]:
    request = state["clarification_request_artifact"]
    artifact = {
        "artifact_type": HUMAN_INTENT_CLARIFICATION_REPLY_BINDING_ARTIFACT_V1,
        "runtime_version": AIGOL_HUMAN_INTENT_CLARIFICATION_CONTINUITY_RUNTIME_V1,
        "binding_id": f"{_require_string(continuity_id, 'continuity_id')}:BINDING",
        "turn_id": _require_string(turn_id, "turn_id"),
        "prompt_id": _require_string(prompt_id, "prompt_id"),
        "clarification_request_reference": request["workflow_selection_id"],
        "clarification_request_hash": request["artifact_hash"],
        "clarification_response_hash": replay_hash(_require_string(clarification_response, "clarification_response")),
        "canonical_chain_id": request["canonical_chain_id"],
        "binding_status": "CLARIFICATION_RESPONSE_BOUND",
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _response_artifact(
    *,
    continuity_id: str,
    state: dict[str, Any],
    binding: dict[str, Any],
    clarification_response: str,
    created_at: str,
) -> dict[str, Any]:
    request = state["clarification_request_artifact"]
    artifact = {
        "artifact_type": HUMAN_INTENT_CLARIFICATION_RESPONSE_ARTIFACT_V1,
        "runtime_version": AIGOL_HUMAN_INTENT_CLARIFICATION_CONTINUITY_RUNTIME_V1,
        "response_id": f"{_require_string(continuity_id, 'continuity_id')}:RESPONSE",
        "binding_reference": binding["binding_id"],
        "binding_hash": binding["artifact_hash"],
        "clarification_request_reference": request["workflow_selection_id"],
        "clarification_request_hash": request["artifact_hash"],
        "original_prompt_hash": request.get("routing_decision_hash"),
        "clarification_response_hash": binding["clarification_response_hash"],
        "combined_intent_hash": replay_hash(
            {
                "original_prompt_reference": request.get("routing_decision_reference"),
                "clarification_response": clarification_response,
            }
        ),
        "created_at": _require_string(created_at, "created_at"),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _target_refinement_artifact(
    *,
    continuity_id: str,
    state: dict[str, Any],
    response: dict[str, Any],
    clarification_response: str,
    created_at: str,
) -> dict[str, Any]:
    request = state["clarification_request_artifact"]
    original_target = _initial_workflow_target(request)
    response_text = _require_string(clarification_response, "clarification_response")
    decision = _refined_workflow_target(
        original_intent_family=request.get("intent_family"),
        original_target=original_target,
        clarification_response=response_text,
    )
    artifact = {
        "artifact_type": HUMAN_INTENT_WORKFLOW_TARGET_REFINEMENT_ARTIFACT_V1,
        "runtime_version": AIGOL_HUMAN_INTENT_CLARIFICATION_CONTINUITY_RUNTIME_V1,
        "refinement_id": f"{_require_string(continuity_id, 'continuity_id')}:TARGET-REFINEMENT",
        "clarification_request_reference": request["workflow_selection_id"],
        "clarification_request_hash": request["artifact_hash"],
        "clarification_response_reference": response["response_id"],
        "clarification_response_hash": response["artifact_hash"],
        "original_intent_family": request.get("intent_family"),
        "original_expected_workflow_targets": deepcopy(request.get("expected_workflow_targets", [])),
        "clarification_response_signals": decision["signals"],
        "refined_intent_family": decision["refined_intent_family"],
        "refined_workflow_targets": [decision["selected_workflow_id"]],
        "selected_workflow_id": decision["selected_workflow_id"],
        "refinement_status": decision["refinement_status"],
        "refinement_reason": decision["refinement_reason"],
        "ambiguity_escalation_reason": decision["ambiguity_escalation_reason"],
        "unresolved_ambiguity_classification": decision["unresolved_ambiguity_classification"],
        "proposal_only_cognition_routing": decision["proposal_only_cognition_routing"],
        "human_confirmation_required": decision["human_confirmation_required"],
        "future_deterministic_rule_candidate_status": decision["future_deterministic_rule_candidate_status"],
        "canonical_chain_id": request["canonical_chain_id"],
        "created_at": _require_string(created_at, "created_at"),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_bypassed": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "failure_reason": None,
    }
    if artifact["selected_workflow_id"] not in SUPPORTED_TARGET_WORKFLOWS:
        raise FailClosedRuntimeError("human intent clarification continuity failed closed: unsupported refined target workflow")
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _refined_workflow_target(
    *,
    original_intent_family: Any,
    original_target: str,
    clarification_response: str,
) -> dict[str, Any]:
    normalized = clarification_response.lower().strip()
    unsafe_escalation_signals = _matched_terms(
        normalized,
        (
            "without approval",
            "bypass approval",
            "skip approval",
            "unrestricted autonomous agent",
            "store my api key",
            "save my api key",
            "shrani ta kljuc",
            "shrani ta ključ",
            "kljuc",
            "ključ",
            "sk-",
            "secret",
            "credential",
            "invoke worker",
            "execute worker",
        ),
    )
    if unsafe_escalation_signals:
        raise FailClosedRuntimeError(
            "human intent clarification continuity failed closed: unsafe ambiguity escalation request"
        )
    confirmation_signals = _matched_terms(
        normalized,
        (
            "yes",
            "yes.",
            "da",
            "da.",
            "odobreno",
            "odobrim",
            "potrjujem",
            "approved",
            "approve",
            "go ahead",
            "confirm",
            "confirmed",
            "that is correct",
        ),
    )
    if original_target == BOUNDED_FILE_WRITE_WORKER_USER_SESSION and confirmation_signals:
        return {
            "selected_workflow_id": BOUNDED_FILE_WRITE_WORKER_USER_SESSION,
            "refined_intent_family": original_intent_family or AMBIGUOUS_INTENT,
            "refinement_status": WORKFLOW_TARGET_REFINED_AFTER_CLARIFICATION,
            "refinement_reason": "clarification response confirmed bounded file-write proof action",
            "signals": confirmation_signals,
            **_no_ambiguity_escalation(),
        }
    unresolved_ambiguity_signals = _matched_terms(
        normalized,
        (
            "not sure",
            "not certain",
            "unclear",
            "i do not know",
            "i don't know",
            "help me decide",
            "help me figure out",
            "safest interpretation",
            "safe next step",
            "what this means",
            "what should this become",
        ),
    )
    advisory_signals = _matched_terms(
        normalized,
        (
            "advisory",
            "guidance",
            "plan",
            "plan only",
            "planning",
            "recommend",
            "recommendation",
            "analyze",
            "how should we",
            "reduce risk",
            "safer",
            "understand",
            "explain",
            "wording",
            "before implementation",
            "do not start implementation",
            "no implementation",
            "without execution",
            "first step",
            "next safest",
            "best next step",
            "za uvedbo",
            "uvedbo orodja",
            "podporo strankam",
            "support tool",
            "customer support tool",
            "tool rollout",
            "samo predlog",
            "nic ne spreminjaj",
            "nič ne spreminjaj",
            "pomagaj mi izbrati",
            "pomagaj mi ugotoviti",
            "pomagaj mi razmisljati",
            "pomagaj mi razmišljati",
            "dobra ideja",
            "povej samo",
            "najverjetneje problem",
            "just advice",
            "don't change anything",
            "dont change anything",
            "whether writing it is a good idea",
            "najbolje",
            "narediti naprej",
            "naslednji korak",
            "before any runtime changes",
        ),
    )
    governed_signals = _matched_terms(
        normalized,
        (
            "governed workflow",
            "workflow proposal",
            "implementation proposal",
            "evidence model",
            "collect evidence",
            "audit evidence",
            "approval criteria",
            "review before use",
            "review ai recommendations",
            "automatically check",
            "missing justification",
            "before staff use",
            "before they affect",
            "controlled workflow",
            "create a governed",
            "start with a governed",
            "odgovor stranki",
            "manjka utemeljitev",
        ),
    )
    bounded_file_signals = _matched_terms(
        normalized,
        (
            "majhno datoteko",
            "majhna datoteka",
            "malo datoteko",
            "tekstovno datoteko",
            "dokazni zapis",
            "dokaz",
            "small text file",
            "tiny proof",
            "proof file",
            "proof note",
            "i approve",
            "approved",
            "odobreno",
            "odobrim",
        ),
    )
    no_execution_signals = _matched_terms(
        normalized,
        (
            "do not start implementation",
            "no implementation",
            "without execution",
            "before any runtime changes",
        ),
    )
    if (
        original_target == BOUNDED_FILE_WRITE_WORKER_USER_SESSION
        and (confirmation_signals or bounded_file_signals)
    ) or (
        bounded_file_signals
        and any(signal in bounded_file_signals for signal in ("majhno datoteko", "tekstovno datoteko", "small text file", "tiny proof", "proof file", "proof note"))
    ):
        return {
            "selected_workflow_id": BOUNDED_FILE_WRITE_WORKER_USER_SESSION,
            "refined_intent_family": original_intent_family or AMBIGUOUS_INTENT,
            "refinement_status": WORKFLOW_TARGET_REFINED_AFTER_CLARIFICATION,
            "refinement_reason": "clarification response requested bounded proof file worker path",
            "signals": confirmation_signals + bounded_file_signals,
            **_no_ambiguity_escalation(),
        }
    if governed_signals and not no_execution_signals and not advisory_signals:
        return {
            "selected_workflow_id": CREATE_DOMAIN_COMPLIANCE_CLARIFICATION,
            "refined_intent_family": original_intent_family or AMBIGUOUS_INTENT,
            "refinement_status": WORKFLOW_TARGET_REFINED_AFTER_CLARIFICATION,
            "refinement_reason": "clarification response requested governed workflow or evidence handling",
            "signals": governed_signals,
            **_no_ambiguity_escalation(),
        }
    if (
        original_intent_family in {AMBIGUOUS_INTENT, CONTINUATION_INTENT}
        and unresolved_ambiguity_signals
        and not governed_signals
    ):
        return {
            "selected_workflow_id": OCS_LLM_COGNITION,
            "refined_intent_family": original_intent_family or AMBIGUOUS_INTENT,
            "refinement_status": WORKFLOW_TARGET_REFINED_AFTER_CLARIFICATION,
            "refinement_reason": (
                "clarification response left deterministic target unresolved and requested proposal-only cognition"
            ),
            "signals": unresolved_ambiguity_signals + no_execution_signals,
            "ambiguity_escalation_reason": "UNRESOLVED_AMBIGUITY_AFTER_CLARIFICATION",
            "unresolved_ambiguity_classification": "UNKNOWN_INTENT_REQUIRES_OCS_PROPOSAL",
            "proposal_only_cognition_routing": True,
            "human_confirmation_required": True,
            "future_deterministic_rule_candidate_status": "HUMAN_CONFIRMATION_REQUIRED_BEFORE_RULE_CANDIDATE",
        }
    if advisory_signals:
        return {
            "selected_workflow_id": OCS_LLM_COGNITION,
            "refined_intent_family": GENERAL_IMPROVEMENT_INTENT,
            "refinement_status": WORKFLOW_TARGET_REFINED_AFTER_CLARIFICATION,
            "refinement_reason": "clarification response requested advisory planning without execution",
            "signals": advisory_signals + no_execution_signals,
            **_no_ambiguity_escalation(),
        }
    return {
        "selected_workflow_id": original_target,
        "refined_intent_family": original_intent_family or AMBIGUOUS_INTENT,
        "refinement_status": TARGET_PRESERVED_LOW_CONFIDENCE,
        "refinement_reason": "clarification response did not contain deterministic target refinement signals",
        "signals": [],
        **_no_ambiguity_escalation(),
    }


def _resolution_artifact(
    *,
    continuity_id: str,
    state: dict[str, Any],
    response: dict[str, Any],
    refinement: dict[str, Any],
    clarification_response: str,
    created_at: str,
) -> dict[str, Any]:
    request = state["clarification_request_artifact"]
    selected_workflow_id = _selected_workflow_id(refinement)
    artifact = {
        "artifact_type": HUMAN_INTENT_CLARIFICATION_RESOLUTION_ARTIFACT_V1,
        "runtime_version": AIGOL_HUMAN_INTENT_CLARIFICATION_CONTINUITY_RUNTIME_V1,
        "resolution_id": f"{_require_string(continuity_id, 'continuity_id')}:RESOLUTION",
        "response_reference": response["response_id"],
        "response_hash": response["artifact_hash"],
        "target_refinement_reference": refinement["refinement_id"],
        "target_refinement_hash": refinement["artifact_hash"],
        "clarification_request_reference": request["workflow_selection_id"],
        "clarification_request_hash": request["artifact_hash"],
        "intent_family": refinement["refined_intent_family"],
        "original_intent_family": refinement["original_intent_family"],
        "ambiguity_escalation_reason": refinement["ambiguity_escalation_reason"],
        "unresolved_ambiguity_classification": refinement["unresolved_ambiguity_classification"],
        "proposal_only_cognition_routing": refinement["proposal_only_cognition_routing"],
        "human_confirmation_required": refinement["human_confirmation_required"],
        "future_deterministic_rule_candidate_status": refinement["future_deterministic_rule_candidate_status"],
        "original_workflow_id": request.get("workflow_id"),
        "clarification_response_hash": replay_hash(_require_string(clarification_response, "clarification_response")),
        "resolution_status": "INTENT_RESOLVED_AFTER_CLARIFICATION",
        "selected_workflow_id": selected_workflow_id,
        "created_at": _require_string(created_at, "created_at"),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _selection_artifact(
    *,
    continuity_id: str,
    state: dict[str, Any],
    refinement: dict[str, Any],
    resolution: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    request = state["clarification_request_artifact"]
    selected_workflow_id = _selected_workflow_id(refinement)
    artifact = {
        "artifact_type": HUMAN_INTENT_WORKFLOW_SELECTION_AFTER_CLARIFICATION_ARTIFACT_V1,
        "runtime_version": AIGOL_HUMAN_INTENT_CLARIFICATION_CONTINUITY_RUNTIME_V1,
        "selection_id": f"{_require_string(continuity_id, 'continuity_id')}:WORKFLOW-SELECTION",
        "resolution_reference": resolution["resolution_id"],
        "resolution_hash": resolution["artifact_hash"],
        "target_refinement_reference": refinement["refinement_id"],
        "target_refinement_hash": refinement["artifact_hash"],
        "canonical_chain_id": request["canonical_chain_id"],
        "workflow_id": selected_workflow_id,
        "routing_status": WORKFLOW_SELECTED,
        "selection_status": WORKFLOW_SELECTION_AFTER_CLARIFICATION,
        "ambiguity_escalation_reason": refinement["ambiguity_escalation_reason"],
        "unresolved_ambiguity_classification": refinement["unresolved_ambiguity_classification"],
        "proposal_only_cognition_routing": refinement["proposal_only_cognition_routing"],
        "human_confirmation_required": refinement["human_confirmation_required"],
        "future_deterministic_rule_candidate_status": refinement["future_deterministic_rule_candidate_status"],
        "created_at": _require_string(created_at, "created_at"),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_bypassed": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    binding: dict[str, Any],
    response: dict[str, Any],
    refinement: dict[str, Any],
    resolution: dict[str, Any],
    selection: dict[str, Any],
    state: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    request = state["clarification_request_artifact"]
    capture = {
        "command": "aigol conversation",
        "runtime_version": AIGOL_HUMAN_INTENT_CLARIFICATION_CONTINUITY_RUNTIME_V1,
        "final_classification": HUMAN_INTENT_CLARIFICATION_CONTINUITY_STATUS,
        "response_status": WORKFLOW_SELECTED,
        "response_source": "HUMAN_INTENT_CLARIFICATION_CONTINUITY_RUNTIME",
        "response_text": "",
        "human_intent_clarification_reply_binding_artifact": deepcopy(binding),
        "human_intent_clarification_response_artifact": deepcopy(response),
        "human_intent_workflow_target_refinement_artifact": deepcopy(refinement),
        "human_intent_clarification_resolution_artifact": deepcopy(resolution),
        "human_intent_workflow_selection_after_clarification_artifact": deepcopy(selection),
        "human_intent_clarification_continuity_replay_reference": str(replay_path),
        "conversation_replay_reference": str(replay_path),
        "canonical_chain_id": request["canonical_chain_id"],
        "current_chain_id": request["canonical_chain_id"],
        "latest_chain_id": request["canonical_chain_id"],
        "originating_workflow_id": HUMAN_INTENT_CLARIFICATION_INTAKE,
        "intent_family": refinement["refined_intent_family"],
        "original_intent_family": refinement["original_intent_family"],
        "workflow_target_refinement_status": refinement["refinement_status"],
        "workflow_target_refinement_reason": refinement["refinement_reason"],
        "ambiguity_escalation_reason": refinement["ambiguity_escalation_reason"],
        "unresolved_ambiguity_classification": refinement["unresolved_ambiguity_classification"],
        "proposal_only_cognition_routing": refinement["proposal_only_cognition_routing"],
        "human_confirmation_required": refinement["human_confirmation_required"],
        "future_deterministic_rule_candidate_status": refinement["future_deterministic_rule_candidate_status"],
        "original_workflow_targets": deepcopy(refinement["original_expected_workflow_targets"]),
        "refined_workflow_targets": deepcopy(refinement["refined_workflow_targets"]),
        "clarification_response_bound": True,
        "intent_resolution_after_clarification": True,
        "workflow_selection_after_clarification": True,
        "workflow_id": selection["workflow_id"],
        "routing_status": selection["routing_status"],
        "fail_closed": False,
        "failure_reason": None,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_bypassed": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }
    capture["response_text"] = render_human_intent_clarification_continuity_summary(capture)
    capture["human_intent_clarification_continuity_hash"] = replay_hash(capture)
    return capture


def _failed_capture(
    *,
    continuity_id: str,
    turn_id: str,
    prompt_id: str,
    current_chain_id: str | None,
    created_at: str,
    replay_reference: str,
    failure_reason: str,
) -> dict[str, Any]:
    return {
        "command": "aigol conversation",
        "runtime_version": AIGOL_HUMAN_INTENT_CLARIFICATION_CONTINUITY_RUNTIME_V1,
        "final_classification": HUMAN_INTENT_CLARIFICATION_CONTINUITY_STATUS,
        "response_status": FAILED_CLOSED,
        "response_source": "HUMAN_INTENT_CLARIFICATION_CONTINUITY_RUNTIME",
        "continuity_id": continuity_id,
        "turn_id": turn_id,
        "prompt_id": prompt_id,
        "canonical_chain_id": current_chain_id,
        "created_at": created_at,
        "replay_reference": replay_reference,
        "fail_closed": True,
        "failure_reason": failure_reason,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
    }


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("human intent clarification continuity replay step ordering mismatch")
    _verify_artifact_hash(artifact)
    wrapper = {"replay_index": index, "replay_step": step, "artifact": deepcopy(artifact)}
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _ensure_replay_available(replay_dir: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_dir / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("human intent clarification continuity failed closed: replay already exists")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("human intent clarification continuity artifact hash is required")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("human intent clarification continuity replay mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("human intent clarification continuity wrapper hash is required")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("human intent clarification continuity replay mismatch")


def _matched_terms(normalized: str, terms: tuple[str, ...]) -> list[str]:
    return [term for term in terms if term in normalized]


def _no_ambiguity_escalation() -> dict[str, Any]:
    return {
        "ambiguity_escalation_reason": None,
        "unresolved_ambiguity_classification": None,
        "proposal_only_cognition_routing": False,
        "human_confirmation_required": False,
        "future_deterministic_rule_candidate_status": None,
    }


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()
