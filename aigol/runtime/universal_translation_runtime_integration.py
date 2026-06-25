"""Integration layer for Universal Translation Runtime adoption."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.acli_llm_assisted_explanation_runtime import create_acli_llm_assisted_explanation
from aigol.runtime.conversational_cli_runtime import route_conversational_cli_intent
from aigol.runtime.governance_to_human_translation_runtime import translate_governance_to_human
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.universal_translation_artifact_schema import (
    GOVERNANCE_TO_HUMAN,
    HUMAN_TO_GOVERNANCE,
    validate_universal_translation_artifact,
)


RUNTIME_VERSION = "UNIVERSAL_TRANSLATION_RUNTIME_INTEGRATION_V1"
HUMAN_ROUTE_STEP = "universal_human_to_governance_integration_recorded"
GOVERNANCE_EXPLANATION_STEP = "universal_governance_to_human_integration_recorded"

FULLY_INTEGRATED = "UNIVERSAL_TRANSLATION_RUNTIME_FULLY_INTEGRATED"


def route_human_request_through_universal_translation(
    *,
    integration_id: str,
    prompt_id: str,
    human_prompt: str,
    canonical_chain_id: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Route Human -> Universal Translation -> HIRR-compatible ACLI workflow resolution."""

    replay_path = Path(replay_dir)
    route_capture = route_conversational_cli_intent(
        routing_id=f"{integration_id}:CONVERSATIONAL-ROUTING",
        prompt_id=prompt_id,
        human_prompt=human_prompt,
        canonical_chain_id=canonical_chain_id,
        created_at=created_at,
        replay_dir=replay_path / "acli_hirr_workflow_resolution",
    )
    decision = route_capture["routing_decision_artifact"]
    translation_reference = _require_string(
        decision.get("universal_translation_reference"),
        "universal_translation_reference",
    )
    translation_hash = _require_string(decision.get("universal_translation_hash"), "universal_translation_hash")
    integration = {
        "artifact_type": RUNTIME_VERSION,
        "integration_id": _require_string(integration_id, "integration_id"),
        "integration_direction": HUMAN_TO_GOVERNANCE,
        "integration_status": FULLY_INTEGRATED,
        "source_prompt_id": _require_string(prompt_id, "prompt_id"),
        "source_prompt_hash": replay_hash(_require_string(human_prompt, "human_prompt")),
        "universal_translation_reference": translation_reference,
        "universal_translation_hash": translation_hash,
        "hirr_compatibility_runtime": "conversational_cli_runtime.route_conversational_cli_intent",
        "hirr_compatible_routing_reference": route_capture["conversational_cli_routing_replay_reference"],
        "routing_decision_hash": decision["artifact_hash"],
        "workflow_selection_hash": route_capture["workflow_selection_artifact"]["artifact_hash"],
        "selected_workflow_id": route_capture["workflow_id"],
        "routing_status": route_capture["routing_status"],
        "migration_mode": "CANONICAL_TRANSLATION_BEFORE_HIRR_COMPATIBILITY",
        "deprecated_direct_path": "Human -> HIRR without Universal Translation evidence",
        "compatibility_layer_active": True,
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": str(replay_path),
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_granted": False,
        "execution_requested": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "authority_granted": False,
    }
    integration["artifact_hash"] = replay_hash(integration)
    _persist(replay_path, HUMAN_ROUTE_STEP, integration)
    return {
        "runtime_version": RUNTIME_VERSION,
        "integration_status": FULLY_INTEGRATED,
        "integration_artifact": deepcopy(integration),
        "conversational_routing_capture": deepcopy(route_capture),
        "workflow_id": route_capture["workflow_id"],
        "routing_status": route_capture["routing_status"],
        "universal_translation_reference": translation_reference,
        "universal_translation_hash": translation_hash,
        "replay_reference": str(replay_path),
        "authority_granted": False,
        "provider_invoked": False,
        "execution_requested": False,
        "governance_mutated": False,
        "replay_visible": True,
    }


def create_operator_explanation_through_universal_translation(
    *,
    integration_id: str,
    translation_request_id: str,
    governance_state: dict[str, Any],
    replay_evidence: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
    proposal_state: dict[str, Any] | None = None,
    approval_state: dict[str, Any] | None = None,
    worker_results: dict[str, Any] | None = None,
    validation_results: dict[str, Any] | None = None,
    err_evidence: dict[str, Any] | None = None,
    llm_explanation_provider: Any | None = None,
    llm_explanation_provider_id: str = "UNSPECIFIED_EXPLANATION_PROVIDER",
) -> dict[str, Any]:
    """Translate Governance -> Universal Translation -> operator explanation compatibility."""

    replay_path = Path(replay_dir)
    translation_capture = translate_governance_to_human(
        translation_request_id=translation_request_id,
        governance_state=governance_state,
        replay_evidence=replay_evidence,
        proposal_state=proposal_state,
        approval_state=approval_state,
        worker_results=worker_results,
        validation_results=validation_results,
        err_evidence=err_evidence,
        created_at=created_at,
        replay_dir=replay_path / "governance_to_human_translation",
    )
    translation_artifact = validate_universal_translation_artifact(translation_capture["translation_artifact"])
    authoritative_state = _authoritative_state_from_translation(
        state_id=f"{integration_id}:AUTHORITATIVE-EXPLANATION-STATE",
        translation_artifact=translation_artifact,
        created_at=created_at,
    )
    llm_capture = None
    if llm_explanation_provider is not None:
        llm_capture = create_acli_llm_assisted_explanation(
            explanation_id=f"{integration_id}:LLM-ASSISTED-EXPLANATION",
            authoritative_state=authoritative_state,
            deterministic_explanation=translation_capture["rendered_explanation"],
            replay_dir=replay_path / "llm_assisted_explanation",
            created_at=created_at,
            provider=llm_explanation_provider,
            provider_id=llm_explanation_provider_id,
        )
    operator_explanation = (
        llm_capture.get("operator_explanation_with_transparency")
        if isinstance(llm_capture, dict)
        else translation_capture["rendered_explanation"]
    )
    integration = {
        "artifact_type": RUNTIME_VERSION,
        "integration_id": _require_string(integration_id, "integration_id"),
        "integration_direction": GOVERNANCE_TO_HUMAN,
        "integration_status": FULLY_INTEGRATED,
        "universal_translation_reference": translation_capture["translation_replay_reference"],
        "universal_translation_hash": translation_artifact["artifact_hash"],
        "operator_explanation_hash": replay_hash(operator_explanation),
        "llm_assisted_explanation_reference": (
            llm_capture.get("llm_assisted_explanation_replay_reference")
            if isinstance(llm_capture, dict)
            else None
        ),
        "llm_assisted_explanation_hash": (
            llm_capture["llm_assisted_explanation_artifact"]["artifact_hash"]
            if isinstance(llm_capture, dict)
            else None
        ),
        "migration_mode": "CANONICAL_TRANSLATION_BEFORE_OPERATOR_EXPLANATION",
        "deprecated_direct_path": "Governance -> ACLI explanation without Universal Translation evidence",
        "compatibility_layer_active": True,
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": str(replay_path),
        "replay_visible": True,
        "provider_invoked": llm_explanation_provider is not None,
        "worker_invoked": False,
        "approval_granted": False,
        "execution_requested": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "authority_granted": False,
    }
    integration["artifact_hash"] = replay_hash(integration)
    _persist(replay_path, GOVERNANCE_EXPLANATION_STEP, integration)
    return {
        "runtime_version": RUNTIME_VERSION,
        "integration_status": FULLY_INTEGRATED,
        "integration_artifact": deepcopy(integration),
        "governance_to_human_translation_capture": deepcopy(translation_capture),
        "llm_assisted_explanation_capture": deepcopy(llm_capture),
        "operator_explanation": operator_explanation,
        "universal_translation_reference": translation_capture["translation_replay_reference"],
        "universal_translation_hash": translation_artifact["artifact_hash"],
        "replay_reference": str(replay_path),
        "authority_granted": False,
        "execution_requested": False,
        "governance_mutated": False,
        "replay_visible": True,
    }


def reconstruct_universal_translation_runtime_integration_replay(
    replay_dir: str | Path,
    *,
    direction: str,
) -> dict[str, Any]:
    """Reconstruct Universal Translation Runtime integration replay evidence."""

    replay_path = Path(replay_dir)
    step = HUMAN_ROUTE_STEP if direction == HUMAN_TO_GOVERNANCE else GOVERNANCE_EXPLANATION_STEP
    wrapper = load_json(replay_path / f"000_{step}.json")
    if wrapper.get("replay_index") != 0 or wrapper.get("replay_step") != step:
        raise FailClosedRuntimeError("universal translation integration replay ordering mismatch")
    _verify_wrapper_hash(wrapper)
    artifact = _require_mapping(wrapper.get("artifact"), "integration_artifact")
    _verify_artifact_hash(artifact)
    if artifact.get("artifact_type") != RUNTIME_VERSION:
        raise FailClosedRuntimeError("universal translation integration artifact type mismatch")
    if artifact.get("integration_direction") != direction:
        raise FailClosedRuntimeError("universal translation integration direction mismatch")
    _validate_no_authority(artifact)
    return {
        "runtime_version": RUNTIME_VERSION,
        "integration_status": artifact["integration_status"],
        "integration_artifact": deepcopy(artifact),
        "integration_direction": artifact["integration_direction"],
        "universal_translation_reference": artifact["universal_translation_reference"],
        "universal_translation_hash": artifact["universal_translation_hash"],
        "replay_hash": wrapper["replay_hash"],
        "authority_granted": False,
        "execution_requested": False,
        "governance_mutated": False,
        "replay_visible": True,
    }


def _authoritative_state_from_translation(
    *,
    state_id: str,
    translation_artifact: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    human_payload = translation_artifact["human_readable_payload"]
    references = human_payload.get("authoritative_state_references")
    references = references if isinstance(references, dict) else {}
    replay_reference = references.get("replay_reference") or translation_artifact["replay_reference"]
    state = {
        "artifact_type": "UNIVERSAL_TRANSLATION_OPERATOR_EXPLANATION_STATE_V1",
        "state_id": _require_string(state_id, "state_id"),
        "workflow_id": translation_artifact["normalized_intent"].get("workflow", "UNKNOWN"),
        "artifact_identifiers": [],
        "target_paths": [],
        "approval_state": translation_artifact["normalized_intent"].get("workflow_state", "UNKNOWN"),
        "proposal_hash": references.get("proposal_state_hash"),
        "replay_references": [str(replay_reference)] if replay_reference else [],
        "source_capture_hash": translation_artifact["artifact_hash"],
        "created_at": _require_string(created_at, "created_at"),
        "authority_granted": False,
        "provider_authority": False,
        "approval_authority": False,
        "execution_authority": False,
    }
    state["artifact_hash"] = replay_hash(state)
    return state


def _persist(replay_path: Path, step: str, artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact)
    wrapper = {"replay_index": 0, "replay_step": step, "artifact": deepcopy(artifact)}
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"000_{step}.json", wrapper)


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash", None)
    if not isinstance(actual, str) or replay_hash(expected) != actual:
        raise FailClosedRuntimeError("universal translation integration replay hash mismatch")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash", None)
    if not isinstance(actual, str) or replay_hash(expected) != actual:
        raise FailClosedRuntimeError("universal translation integration artifact hash mismatch")


def _validate_no_authority(artifact: dict[str, Any]) -> None:
    for field in (
        "authority_granted",
        "approval_granted",
        "execution_requested",
        "governance_mutated",
        "replay_mutated",
    ):
        if artifact.get(field) is True:
            raise FailClosedRuntimeError("universal translation integration cannot grant authority")


def _require_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"{field_name} must be a JSON object")
    return deepcopy(value)


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()
