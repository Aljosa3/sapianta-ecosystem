"""OCS replay-derived improvement intent candidate runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.ocs_cognition_runtime import (
    OCS_COGNITION_ARTIFACT_V1,
    OCS_COGNITION_COMPLETED,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_OCS_REPLAY_DERIVED_INTENT_RUNTIME_VERSION = "AIGOL_OCS_REPLAY_DERIVED_INTENT_RUNTIME_V1"
OCS_REPLAY_DERIVED_INTENT_ARTIFACT_V1 = "OCS_REPLAY_DERIVED_INTENT_ARTIFACT_V1"
OCS_REPLAY_DERIVED_INTENT_CREATED = "OCS_REPLAY_DERIVED_INTENT_CREATED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "ocs_replay_derived_intent_recorded",
    "ocs_replay_derived_intent_returned",
)

HISTORY_CATEGORIES = (
    "execution_history",
    "validation_history",
    "failure_history",
    "operator_decision_history",
)

AUTHORITY_FLAGS = {
    "authorizes_execution": False,
    "authorizes_dispatch": False,
    "authorizes_worker_invocation": False,
    "authorizes_provider_invocation": False,
    "authorizes_governance_mutation": False,
    "authorizes_replay_mutation": False,
    "authorizes_domain_creation": False,
    "authorizes_human_approval": False,
    "authorizes_self_modification": False,
    "authorizes_automatic_implementation": False,
}

PROHIBITED_FLAGS = (
    "authority",
    "self_modification_requested",
    "automatic_implementation_requested",
    "approval_created",
    "execution_requested",
    "dispatch_requested",
    "worker_assignment_requested",
    "worker_dispatch_requested",
    "worker_invocation_requested",
    "worker_invoked",
    "provider_invoked",
    "domain_created",
    "governance_modified",
    "replay_modified",
)


def generate_ocs_replay_derived_intent(
    *,
    intent_generation_id: str,
    ocs_cognition_artifact: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
    execution_history: list[dict[str, Any]] | None = None,
    validation_history: list[dict[str, Any]] | None = None,
    failure_history: list[dict[str, Any]] | None = None,
    operator_decision_history: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Generate replay-derived improvement intent candidates without authority."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        cognition = deepcopy(ocs_cognition_artifact)
        _validate_cognition_artifact(cognition)
        history = _normalize_history(
            execution_history=execution_history or [],
            validation_history=validation_history or [],
            failure_history=failure_history or [],
            operator_decision_history=operator_decision_history or [],
        )
        candidates = _improvement_candidates(cognition, history)
        artifact = _intent_artifact(
            intent_generation_id=intent_generation_id,
            cognition=cognition,
            history=history,
            candidates=candidates,
            created_at=created_at,
            intent_status=OCS_REPLAY_DERIVED_INTENT_CREATED,
            failure_reason=None,
        )
        returned = _returned_artifact(artifact)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, replay_path)
    except Exception as exc:
        failure_reason = _failure_reason(exc)
        artifact = _failed_intent_artifact(
            intent_generation_id=intent_generation_id,
            cognition=ocs_cognition_artifact if isinstance(ocs_cognition_artifact, dict) else {},
            created_at=created_at,
            failure_reason=failure_reason,
        )
        returned = _returned_artifact(artifact)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, replay_path)


def reconstruct_ocs_replay_derived_intent_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct OCS replay-derived intent evidence deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("OCS replay-derived intent replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("OCS replay-derived intent replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    recorded = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("intent_generation_reference") != recorded["intent_generation_id"]:
        raise FailClosedRuntimeError("OCS replay-derived intent returned reference mismatch")
    if returned.get("intent_generation_hash") != recorded["artifact_hash"]:
        raise FailClosedRuntimeError("OCS replay-derived intent returned hash mismatch")
    if recorded.get("intent_hash") != _compute_intent_hash(recorded):
        raise FailClosedRuntimeError("OCS replay-derived intent hash mismatch")
    return {
        "intent_generation_id": recorded["intent_generation_id"],
        "intent_status": recorded["intent_status"],
        "source_cognition_id": recorded["source_cognition_id"],
        "source_cognition_hash": recorded["source_cognition_hash"],
        "improvement_candidates": deepcopy(recorded["improvement_candidates"]),
        "candidate_count": recorded["candidate_count"],
        "recurring_failure_count": recorded["recurring_failure_count"],
        "recurring_clarification_count": recorded["recurring_clarification_count"],
        "recurring_operator_intervention_count": recorded["recurring_operator_intervention_count"],
        "capability_gap_count": recorded["capability_gap_count"],
        "intent_hash": recorded["intent_hash"],
        "authority_flags": deepcopy(recorded["authority_flags"]),
        "replay_visible": True,
        "self_modification_requested": False,
        "automatic_implementation_requested": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _validate_cognition_artifact(cognition: dict[str, Any]) -> None:
    if cognition.get("artifact_type") != OCS_COGNITION_ARTIFACT_V1:
        raise FailClosedRuntimeError("OCS replay-derived intent failed closed: invalid OCS cognition artifact")
    _verify_artifact_hash(cognition)
    if cognition.get("cognition_status") != OCS_COGNITION_COMPLETED:
        raise FailClosedRuntimeError("OCS replay-derived intent failed closed: OCS cognition is not completed")
    if cognition.get("replay_visible") is not True:
        raise FailClosedRuntimeError("OCS replay-derived intent failed closed: OCS cognition is not replay-visible")
    if cognition.get("cognition_hash") != _compute_cognition_hash_for_validation(cognition):
        raise FailClosedRuntimeError("OCS replay-derived intent failed closed: OCS cognition hash mismatch")
    authority_flags = cognition.get("authority_flags")
    if not isinstance(authority_flags, dict):
        raise FailClosedRuntimeError("OCS replay-derived intent failed closed: cognition authority flags are required")
    for flag in AUTHORITY_FLAGS:
        if flag in authority_flags and authority_flags.get(flag) is not False:
            raise FailClosedRuntimeError(f"OCS replay-derived intent failed closed: cognition authority flag must be false: {flag}")
    for flag in PROHIBITED_FLAGS:
        if cognition.get(flag) is True:
            raise FailClosedRuntimeError(f"OCS replay-derived intent failed closed: cognition carries prohibited flag {flag}")


def _normalize_history(
    *,
    execution_history: list[dict[str, Any]],
    validation_history: list[dict[str, Any]],
    failure_history: list[dict[str, Any]],
    operator_decision_history: list[dict[str, Any]],
) -> dict[str, Any]:
    raw = {
        "execution_history": execution_history,
        "validation_history": validation_history,
        "failure_history": failure_history,
        "operator_decision_history": operator_decision_history,
    }
    normalized: dict[str, Any] = {}
    for category in HISTORY_CATEGORIES:
        entries = raw[category]
        if not isinstance(entries, list):
            raise FailClosedRuntimeError("OCS replay-derived intent failed closed: history category must be a list")
        normalized[category] = sorted(
            [_normalize_history_item(category, index, entry) for index, entry in enumerate(entries)],
            key=lambda item: (item["pattern_key"], item["source_id"], item["source_hash"]),
        )
    return normalized


def _normalize_history_item(category: str, index: int, entry: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(entry, dict):
        raise FailClosedRuntimeError("OCS replay-derived intent failed closed: history item must be a JSON object")
    artifact = deepcopy(entry)
    if artifact.get("replay_visible") is not True:
        raise FailClosedRuntimeError("OCS replay-derived intent failed closed: history item is not replay-visible")
    _reject_prohibited_flags(artifact)
    if "artifact_hash" in artifact:
        _verify_artifact_hash(artifact)
    artifact_type = _optional_string(artifact.get("artifact_type")) or _optional_string(artifact.get("event_type")) or "UNKNOWN"
    source_id = (
        _optional_string(artifact.get("artifact_id"))
        or _optional_string(artifact.get("execution_id"))
        or _optional_string(artifact.get("validation_id"))
        or _optional_string(artifact.get("failure_id"))
        or _optional_string(artifact.get("decision_id"))
        or _optional_string(artifact.get("source_id"))
        or f"{category}:ITEM-{index:06d}"
    )
    source_hash = _optional_string(artifact.get("artifact_hash")) or _optional_string(artifact.get("replay_hash")) or replay_hash(artifact)
    summary = _summary(artifact)
    pattern_key = _pattern_key(category, artifact_type, summary)
    return {
        "category": category,
        "source_id": source_id,
        "artifact_type": artifact_type,
        "source_hash": source_hash,
        "pattern_key": pattern_key,
        "summary": summary,
        "replay_visible": True,
        "authority": False,
    }


def _improvement_candidates(cognition: dict[str, Any], history: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    candidates.extend(_recurring_candidates(history["failure_history"], "RECURRING_FAILURE", "Stabilize recurring failure pattern."))
    candidates.extend(
        _recurring_candidates(
            _clarification_sources(cognition, history),
            "RECURRING_CLARIFICATION_REQUEST",
            "Reduce recurring clarification need.",
        )
    )
    candidates.extend(
        _recurring_candidates(
            history["operator_decision_history"],
            "RECURRING_OPERATOR_INTERVENTION",
            "Reduce repeated operator intervention.",
        )
    )
    candidates.extend(_capability_gap_candidates(cognition, history))
    return sorted(candidates, key=lambda item: (item["candidate_type"], item["pattern_key"], item["candidate_id"]))


def _recurring_candidates(entries: list[dict[str, Any]], candidate_type: str, summary: str) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for entry in entries:
        groups.setdefault(entry["pattern_key"], []).append(entry)
    candidates = []
    for pattern_key, members in groups.items():
        if len(members) < 2:
            continue
        candidates.append(
            _candidate(
                candidate_type=candidate_type,
                pattern_key=pattern_key,
                summary=summary,
                evidence=members,
                confidence="HIGH",
            )
        )
    return candidates


def _capability_gap_candidates(cognition: dict[str, Any], history: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    if cognition.get("ambiguity", {}).get("is_ambiguous") is True:
        candidates.append(
            _candidate(
                candidate_type="CAPABILITY_GAP",
                pattern_key="COGNITION_AMBIGUITY",
                summary="Improve OCS ambiguity resolution inputs.",
                evidence=_synthetic_cognition_evidence(cognition, "ambiguity"),
                confidence="MEDIUM",
            )
        )
    if cognition.get("provider_necessity", {}).get("necessity_classification") == "PROVIDER_UNDETERMINED":
        candidates.append(
            _candidate(
                candidate_type="CAPABILITY_GAP",
                pattern_key="PROVIDER_NECESSITY_UNDETERMINED",
                summary="Define provider necessity policy coverage for this OCS path.",
                evidence=_synthetic_cognition_evidence(cognition, "provider_necessity"),
                confidence="MEDIUM",
            )
        )
    validation_gap_entries = [
        entry
        for entry in history["validation_history"]
        if any(token in entry["pattern_key"] for token in ("FAILED", "MISSING", "INVALID"))
    ]
    if len(validation_gap_entries) >= 2:
        candidates.append(
            _candidate(
                candidate_type="CAPABILITY_GAP",
                pattern_key="VALIDATION_HISTORY_GAP",
                summary="Improve validation coverage for recurring validation gaps.",
                evidence=validation_gap_entries,
                confidence="HIGH",
            )
        )
    return candidates


def _clarification_sources(cognition: dict[str, Any], history: dict[str, Any]) -> list[dict[str, Any]]:
    entries = list(history["operator_decision_history"])
    for requirement in cognition.get("clarification_requirements", []):
        if requirement.get("required") is True:
            entries.append(
                {
                    "category": "cognition_clarification_requirement",
                    "source_id": str(requirement.get("requirement_id")),
                    "artifact_type": "OCS_CLARIFICATION_REQUIREMENT",
                    "source_hash": replay_hash(requirement),
                    "pattern_key": f"CLARIFICATION:{requirement.get('requirement_id')}",
                    "summary": deepcopy(requirement),
                    "replay_visible": True,
                    "authority": False,
                }
            )
    return entries


def _candidate(
    *,
    candidate_type: str,
    pattern_key: str,
    summary: str,
    evidence: list[dict[str, Any]],
    confidence: str,
) -> dict[str, Any]:
    evidence_refs = [
        {
            "category": entry["category"],
            "source_id": entry["source_id"],
            "source_hash": entry["source_hash"],
            "pattern_key": entry["pattern_key"],
        }
        for entry in evidence
    ]
    candidate_id = replay_hash(
        {
            "candidate_type": candidate_type,
            "pattern_key": pattern_key,
            "evidence_refs": evidence_refs,
            "summary": summary,
        }
    )
    return {
        "candidate_id": candidate_id,
        "candidate_type": candidate_type,
        "pattern_key": pattern_key,
        "intent_summary": summary,
        "evidence_count": len(evidence_refs),
        "evidence_references": evidence_refs,
        "confidence": confidence,
        "human_review_required": True,
        "ppp_eligible": True,
        "proposal_created": False,
        "automatic_implementation_requested": False,
        "authority": False,
    }


def _intent_artifact(
    *,
    intent_generation_id: str,
    cognition: dict[str, Any],
    history: dict[str, Any],
    candidates: list[dict[str, Any]],
    created_at: str,
    intent_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    recurring_failures = [candidate for candidate in candidates if candidate["candidate_type"] == "RECURRING_FAILURE"]
    recurring_clarifications = [
        candidate for candidate in candidates if candidate["candidate_type"] == "RECURRING_CLARIFICATION_REQUEST"
    ]
    recurring_interventions = [
        candidate for candidate in candidates if candidate["candidate_type"] == "RECURRING_OPERATOR_INTERVENTION"
    ]
    capability_gaps = [candidate for candidate in candidates if candidate["candidate_type"] == "CAPABILITY_GAP"]
    artifact = {
        "artifact_type": OCS_REPLAY_DERIVED_INTENT_ARTIFACT_V1,
        "runtime_version": AIGOL_OCS_REPLAY_DERIVED_INTENT_RUNTIME_VERSION,
        "intent_generation_id": _require_string(intent_generation_id, "intent_generation_id"),
        "source_cognition_id": cognition["cognition_id"],
        "source_cognition_artifact_hash": cognition["artifact_hash"],
        "source_cognition_hash": cognition["cognition_hash"],
        "history_categories": list(HISTORY_CATEGORIES),
        "normalized_history": deepcopy(history),
        "improvement_candidates": deepcopy(candidates),
        "candidate_count": len(candidates),
        "recurring_failure_count": len(recurring_failures),
        "recurring_clarification_count": len(recurring_clarifications),
        "recurring_operator_intervention_count": len(recurring_interventions),
        "capability_gap_count": len(capability_gaps),
        "intent_status": intent_status,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "authority": False,
        "self_modification_requested": False,
        "automatic_implementation_requested": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "worker_invocation_requested": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "failure_reason": failure_reason,
    }
    artifact["intent_hash"] = _compute_intent_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_intent_artifact(
    *,
    intent_generation_id: str,
    cognition: dict[str, Any],
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    safe_cognition = {
        "cognition_id": cognition.get("cognition_id", "INVALID_COGNITION_ID"),
        "artifact_hash": cognition.get("artifact_hash", "INVALID_COGNITION_ARTIFACT_HASH"),
        "cognition_hash": cognition.get("cognition_hash", "INVALID_COGNITION_HASH"),
    }
    return _intent_artifact(
        intent_generation_id=intent_generation_id,
        cognition=safe_cognition,
        history={category: [] for category in HISTORY_CATEGORIES},
        candidates=[],
        created_at=created_at,
        intent_status=FAILED_CLOSED,
        failure_reason=failure_reason,
    )


def _returned_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(artifact)
    returned = {
        "event_type": "OCS_REPLAY_DERIVED_INTENT_RETURNED",
        "intent_generation_reference": artifact["intent_generation_id"],
        "intent_generation_hash": artifact["artifact_hash"],
        "intent_status": artifact["intent_status"],
        "intent_hash": artifact["intent_hash"],
        "candidate_count": artifact["candidate_count"],
        "replay_visible": True,
        "authority": False,
        "self_modification_requested": False,
        "automatic_implementation_requested": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
        "failure_reason": artifact["failure_reason"],
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(artifact: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "ocs_replay_derived_intent_artifact": deepcopy(artifact),
        "ocs_replay_derived_intent_returned": deepcopy(returned),
        "ocs_replay_derived_intent_replay_reference": str(replay_path),
        "intent_status": artifact["intent_status"],
        "intent_hash": artifact["intent_hash"],
        "improvement_candidates": deepcopy(artifact["improvement_candidates"]),
        "candidate_count": artifact["candidate_count"],
        "recurring_failure_count": artifact["recurring_failure_count"],
        "recurring_clarification_count": artifact["recurring_clarification_count"],
        "recurring_operator_intervention_count": artifact["recurring_operator_intervention_count"],
        "capability_gap_count": artifact["capability_gap_count"],
        "fail_closed": artifact["intent_status"] != OCS_REPLAY_DERIVED_INTENT_CREATED,
        "failure_reason": artifact["failure_reason"],
        "self_modification_requested": False,
        "automatic_implementation_requested": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    capture["ocs_replay_derived_intent_capture_hash"] = replay_hash(capture)
    return capture


def _compute_intent_hash(artifact: dict[str, Any]) -> str:
    return replay_hash(
        {
            "source_cognition_id": artifact["source_cognition_id"],
            "source_cognition_artifact_hash": artifact["source_cognition_artifact_hash"],
            "source_cognition_hash": artifact["source_cognition_hash"],
            "history_categories": artifact["history_categories"],
            "normalized_history": artifact["normalized_history"],
            "improvement_candidates": artifact["improvement_candidates"],
            "candidate_count": artifact["candidate_count"],
            "recurring_failure_count": artifact["recurring_failure_count"],
            "recurring_clarification_count": artifact["recurring_clarification_count"],
            "recurring_operator_intervention_count": artifact["recurring_operator_intervention_count"],
            "capability_gap_count": artifact["capability_gap_count"],
            "intent_status": artifact["intent_status"],
            "authority_flags": artifact["authority_flags"],
            "failure_reason": artifact["failure_reason"],
        }
    )


def _compute_cognition_hash_for_validation(cognition: dict[str, Any]) -> str:
    return replay_hash(
        {
            "contract_reference": cognition["contract_reference"],
            "source_context_assembly_id": cognition["source_context_assembly_id"],
            "source_context_artifact_hash": cognition["source_context_artifact_hash"],
            "source_context_hash": cognition["source_context_hash"],
            "task_intent": cognition["task_intent"],
            "ambiguity": cognition["ambiguity"],
            "clarification_requirements": cognition["clarification_requirements"],
            "domain_candidates": cognition["domain_candidates"],
            "worker_candidates": cognition["worker_candidates"],
            "provider_necessity": cognition["provider_necessity"],
            "cognition_status": cognition["cognition_status"],
            "authority_flags": cognition["authority_flags"],
            "failure_reason": cognition["failure_reason"],
        }
    )


def _pattern_key(category: str, artifact_type: str, summary: dict[str, Any]) -> str:
    parts = [category.upper(), artifact_type.upper()]
    for field in ("failure_reason", "status", "validation_status", "decision_status", "terminal_status", "error_code"):
        value = summary.get(field)
        if isinstance(value, str) and value.strip():
            parts.append(value.strip().upper().replace(" ", "_"))
            break
    return ":".join(parts)


def _summary(artifact: dict[str, Any]) -> dict[str, Any]:
    fields = (
        "artifact_type",
        "event_type",
        "status",
        "validation_status",
        "failure_reason",
        "decision_status",
        "terminal_status",
        "error_code",
        "domain_id",
        "worker_family_id",
    )
    return {field: deepcopy(artifact[field]) for field in fields if field in artifact}


def _synthetic_cognition_evidence(cognition: dict[str, Any], field: str) -> list[dict[str, Any]]:
    payload = deepcopy(cognition.get(field))
    return [
        {
            "category": "ocs_cognition",
            "source_id": cognition["cognition_id"],
            "source_hash": replay_hash(payload),
            "pattern_key": field.upper(),
            "summary": payload,
            "replay_visible": True,
            "authority": False,
        }
    ]


def _reject_prohibited_flags(artifact: dict[str, Any]) -> None:
    for flag in PROHIBITED_FLAGS:
        if artifact.get(flag) is True:
            raise FailClosedRuntimeError(f"OCS replay-derived intent failed closed: history item carries prohibited flag {flag}")


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("OCS replay-derived intent replay step ordering mismatch")
    _verify_artifact_hash(artifact)
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


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError("OCS replay-derived intent artifact hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("OCS replay-derived intent artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("OCS replay-derived intent replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("OCS replay-derived intent replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _optional_string(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "OCS replay-derived intent failed closed"
