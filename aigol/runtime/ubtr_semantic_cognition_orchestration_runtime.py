"""UBTR semantic cognition orchestration decision runtime."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.canonical_semantic_artifact_runtime import CANONICAL_SEMANTIC_ARTIFACT_TYPE
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


RUNTIME_VERSION = "UBTR_SEMANTIC_COGNITION_ORCHESTRATION_RUNTIME_V1"
REPLAY_STEP = "ubtr_semantic_cognition_orchestration_recorded"

DETERMINISTIC_SEMANTIC_ARTIFACT_VALID = "DETERMINISTIC_SEMANTIC_ARTIFACT_VALID"
OCS_COGNITION_REQUESTED = "OCS_COGNITION_REQUESTED"
FAILED_CLOSED = "FAILED_CLOSED"


def orchestrate_ubtr_semantic_cognition(
    *,
    orchestration_id: str,
    canonical_semantic_artifact: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Decide whether UBTR can continue deterministically or must request OCS cognition."""

    replay_path = Path(replay_dir)
    try:
        semantic = _validate_canonical_semantic_artifact(canonical_semantic_artifact)
        decision_reasons = _cognition_required_reasons(semantic)
        ocs_request = (
            _ocs_cognition_request(
                orchestration_id=orchestration_id,
                semantic_artifact=semantic,
                decision_reasons=decision_reasons,
                created_at=created_at,
            )
            if decision_reasons
            else None
        )
        decision = OCS_COGNITION_REQUESTED if ocs_request is not None else DETERMINISTIC_SEMANTIC_ARTIFACT_VALID
        failure_reason = None
    except Exception as exc:
        semantic = canonical_semantic_artifact if isinstance(canonical_semantic_artifact, dict) else {}
        decision_reasons = ["CANONICAL_SEMANTIC_ARTIFACT_INVALID"]
        ocs_request = None
        decision = FAILED_CLOSED
        failure_reason = str(exc) if isinstance(exc, FailClosedRuntimeError) else "UBTR semantic cognition orchestration failed closed"

    artifact = _orchestration_artifact(
        orchestration_id=orchestration_id,
        semantic_artifact=semantic,
        decision=decision,
        decision_reasons=decision_reasons,
        ocs_request=ocs_request,
        failure_reason=failure_reason,
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
    return _capture(artifact, replay_path)


def reconstruct_ubtr_semantic_cognition_orchestration_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct UBTR semantic cognition orchestration replay."""

    replay_path = Path(replay_dir)
    wrapper = load_json(replay_path / f"000_{REPLAY_STEP}.json")
    if wrapper.get("replay_index") != 0 or wrapper.get("replay_step") != REPLAY_STEP:
        raise FailClosedRuntimeError("UBTR semantic cognition orchestration replay ordering mismatch")
    _verify_wrapper_hash(wrapper)
    artifact = _require_mapping(wrapper.get("artifact"), "orchestration_artifact")
    _verify_artifact_hash(artifact)
    if artifact.get("artifact_type") != RUNTIME_VERSION:
        raise FailClosedRuntimeError("UBTR semantic cognition orchestration artifact type mismatch")
    _validate_no_authority(artifact)
    semantic = artifact.get("canonical_semantic_artifact")
    if isinstance(semantic, dict) and semantic:
        _validate_canonical_semantic_artifact(semantic)
    return {
        **_capture(artifact, replay_path),
        "replay_hash": wrapper["replay_hash"],
    }


def _orchestration_artifact(
    *,
    orchestration_id: str,
    semantic_artifact: dict[str, Any],
    decision: str,
    decision_reasons: list[str],
    ocs_request: dict[str, Any] | None,
    failure_reason: str | None,
    replay_reference: str,
    created_at: str,
) -> dict[str, Any]:
    semantic_hash = semantic_artifact.get("artifact_hash") if isinstance(semantic_artifact, dict) else None
    artifact = {
        "artifact_type": RUNTIME_VERSION,
        "orchestration_id": _require_string(orchestration_id, "orchestration_id"),
        "semantic_decision": _require_decision(decision),
        "decision_reasons": list(decision_reasons),
        "canonical_semantic_artifact_hash": semantic_hash,
        "canonical_semantic_artifact": deepcopy(semantic_artifact) if isinstance(semantic_artifact, dict) else {},
        "ocs_cognition_request": deepcopy(ocs_request),
        "ocs_cognition_request_hash": ocs_request.get("artifact_hash") if isinstance(ocs_request, dict) else None,
        "ocs_provider_selection_owner": "OCS" if isinstance(ocs_request, dict) else None,
        "ubtr_semantic_orchestration_owner": "UBTR",
        "failure_reason": failure_reason,
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "provider_invoked": False,
        "provider_selected": False,
        "provider_selection_authority": False,
        "worker_invoked": False,
        "approval_granted": False,
        "execution_authorized": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "authority_granted": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(artifact: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    return {
        "runtime_version": RUNTIME_VERSION,
        "semantic_decision": artifact["semantic_decision"],
        "decision_reasons": list(artifact["decision_reasons"]),
        "orchestration_artifact": deepcopy(artifact),
        "orchestration_replay_reference": str(replay_path),
        "canonical_semantic_artifact_hash": artifact["canonical_semantic_artifact_hash"],
        "ocs_cognition_request": deepcopy(artifact["ocs_cognition_request"]),
        "ocs_cognition_request_hash": artifact["ocs_cognition_request_hash"],
        "provider_invoked": False,
        "provider_selected": False,
        "worker_invoked": False,
        "approval_granted": False,
        "execution_authorized": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "authority_granted": False,
        "replay_visible": True,
    }


def _cognition_required_reasons(semantic: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    ambiguity = _require_mapping(semantic.get("ambiguity"), "ambiguity")
    confidence = _require_mapping(semantic.get("confidence"), "confidence")
    workflow_identity = _require_mapping(semantic.get("workflow_identity"), "workflow_identity")
    semantic_identity = _require_mapping(semantic.get("semantic_identity"), "semantic_identity")
    if ambiguity.get("clarification_required") is True:
        reasons.append("SEMANTIC_AMBIGUITY_REQUIRES_COGNITION")
    if ambiguity.get("ambiguity_status") not in {"NO_AMBIGUITY", "MINOR_AMBIGUITY"}:
        reasons.append("AMBIGUITY_STATUS_EXCEEDS_DETERMINISTIC_THRESHOLD")
    if confidence.get("semantic_confidence") not in {"HIGH", "GOVERNANCE_ONLY"}:
        reasons.append("SEMANTIC_CONFIDENCE_BELOW_THRESHOLD")
    if not _optional_string(workflow_identity.get("workflow_id")):
        reasons.append("WORKFLOW_CANDIDATE_MISSING")
    entities = semantic_identity.get("entities")
    entity_missing = False
    if isinstance(entities, dict):
        artifact_ids = entities.get("artifact_identifiers")
        target_paths = entities.get("target_paths")
        entity_missing = not bool(artifact_ids or target_paths)
    if entity_missing and semantic_identity.get("domain") == "GOVERNANCE":
        reasons.append("GOVERNANCE_TARGET_ENTITY_MISSING")
    return sorted(set(reasons))


def _ocs_cognition_request(
    *,
    orchestration_id: str,
    semantic_artifact: dict[str, Any],
    decision_reasons: list[str],
    created_at: str,
) -> dict[str, Any]:
    ambiguity = _require_mapping(semantic_artifact.get("ambiguity"), "ambiguity")
    confidence = _require_mapping(semantic_artifact.get("confidence"), "confidence")
    clarification_state = _require_mapping(semantic_artifact.get("clarification_state"), "clarification_state")
    request = {
        "artifact_type": "UBTR_GOVERNED_OCS_COGNITION_REQUEST_V1",
        "request_id": f"{_require_string(orchestration_id, 'orchestration_id')}:OCS-COGNITION-REQUEST",
        "request_owner": "UBTR",
        "governance_owner": "OCS",
        "canonical_semantic_artifact_hash": semantic_artifact["artifact_hash"],
        "semantic_ambiguity": deepcopy(ambiguity),
        "semantic_confidence": deepcopy(confidence),
        "missing_information": list(clarification_state.get("clarification_questions") or []),
        "cognition_objective": _cognition_objective(decision_reasons),
        "escalation_reasons": list(decision_reasons),
        "provider_selection_required": True,
        "provider_selection_owner": "OCS",
        "capability_escalation_owner": "OCS",
        "multi_provider_comparison_owner": "OCS",
        "ubtr_semantic_authority_preserved": True,
        "advisory_provider_output_only": True,
        "created_at": _require_string(created_at, "created_at"),
        "provider_invoked": False,
        "provider_selected": False,
        "worker_invoked": False,
        "approval_granted": False,
        "execution_authorized": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "authority_granted": False,
    }
    request["artifact_hash"] = replay_hash(request)
    return request


def _cognition_objective(decision_reasons: list[str]) -> str:
    if "GOVERNANCE_TARGET_ENTITY_MISSING" in decision_reasons:
        return "Resolve the missing governance artifact or target path without authorizing execution."
    if "WORKFLOW_CANDIDATE_MISSING" in decision_reasons:
        return "Resolve the intended workflow candidate without selecting providers inside UBTR."
    if "SEMANTIC_CONFIDENCE_BELOW_THRESHOLD" in decision_reasons:
        return "Improve semantic confidence while preserving provider non-authority."
    return "Resolve semantic ambiguity while preserving governance and approval boundaries."


def _validate_canonical_semantic_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    candidate = _require_mapping(artifact, "canonical_semantic_artifact")
    if candidate.get("artifact_type") != CANONICAL_SEMANTIC_ARTIFACT_TYPE:
        raise FailClosedRuntimeError("UBTR orchestration canonical semantic artifact type mismatch")
    flags = _require_mapping(candidate.get("authority_flags"), "authority_flags")
    if flags.get("semantic_authority") is not True:
        raise FailClosedRuntimeError("UBTR orchestration semantic authority missing")
    for key, value in flags.items():
        if key != "semantic_authority" and value is not False:
            raise FailClosedRuntimeError("UBTR orchestration canonical artifact grants non-semantic authority")
    _verify_artifact_hash(candidate)
    return deepcopy(candidate)


def _validate_no_authority(artifact: dict[str, Any]) -> None:
    for field in (
        "provider_invoked",
        "provider_selected",
        "provider_selection_authority",
        "worker_invoked",
        "approval_granted",
        "execution_authorized",
        "governance_mutated",
        "replay_mutated",
        "authority_granted",
    ):
        if artifact.get(field) is not False:
            raise FailClosedRuntimeError("UBTR semantic cognition orchestration authority drift")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    candidate = deepcopy(artifact)
    actual = candidate.pop("artifact_hash", None)
    if not isinstance(actual, str) or replay_hash(candidate) != actual:
        raise FailClosedRuntimeError("UBTR semantic cognition orchestration artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    candidate = deepcopy(wrapper)
    actual = candidate.pop("replay_hash", None)
    if not isinstance(actual, str) or replay_hash(candidate) != actual:
        raise FailClosedRuntimeError("UBTR semantic cognition orchestration replay hash mismatch")


def _require_decision(value: Any) -> str:
    if value not in {DETERMINISTIC_SEMANTIC_ARTIFACT_VALID, OCS_COGNITION_REQUESTED, FAILED_CLOSED}:
        raise FailClosedRuntimeError("UBTR semantic cognition decision invalid")
    return str(value)


def _require_mapping(value: Any, field_name: str) -> dict[str, Any]:
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
