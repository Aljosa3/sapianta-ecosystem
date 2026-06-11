"""Deterministic lifecycle gap detection runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.replay_gap_detection_runtime import (
    FAILED_CLOSED,
    GAP_CLASSIFICATION_ARTIFACT_V1,
    GAP_DETECTION_ARTIFACT_V1,
    GAP_EVIDENCE_ARTIFACT_V1,
    GAPS_DETECTED,
    NO_GAPS_DETECTED,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_LIFECYCLE_GAP_DETECTION_RUNTIME_VERSION = "AIGOL_LIFECYCLE_GAP_DETECTION_RUNTIME_V1"

REPLAY_STEPS = (
    "lifecycle_gap_evidence_recorded",
    "lifecycle_gap_classification_recorded",
    "lifecycle_gap_detection_recorded",
    "lifecycle_gap_detection_returned",
)

EXPECTED_LIFECYCLE = (
    "CLARIFICATION",
    "APPROVAL",
    "EXECUTION_READY",
    "EXECUTION_AUTHORIZED",
    "WORKER_REQUESTED",
    "WORKER_ASSIGNED",
    "WORKER_DISPATCHED",
    "WORKER_INVOKED",
    "EXECUTING",
    "RESULT_CREATED",
    "RESULT_VALIDATED",
    "REPLAY_REVIEWED",
    "TERMINATED",
)

EXPECTED_WORKFLOW_BY_STAGE = {
    "APPROVAL": "CREATE_DOMAIN_COMPLIANCE_CLARIFICATION",
    "EXECUTION_READY": "DOMAIN_HANDOFF_REVIEW_APPROVAL_AND_BINDING_ENTRY",
    "EXECUTION_AUTHORIZED": "DOMAIN_EXECUTION_AUTHORIZATION",
    "WORKER_REQUESTED": "DOMAIN_WORKER_REQUEST",
    "WORKER_ASSIGNED": "DOMAIN_WORKER_ASSIGNMENT",
    "WORKER_DISPATCHED": "DOMAIN_WORKER_DISPATCH",
    "WORKER_INVOKED": "DOMAIN_WORKER_INVOCATION",
    "EXECUTING": "DOMAIN_WORKER_EXECUTION",
    "RESULT_CREATED": "DOMAIN_WORKER_RESULT_CAPTURE",
    "RESULT_VALIDATED": "DOMAIN_WORKER_RESULT_VALIDATION",
    "REPLAY_REVIEWED": "DOMAIN_POST_EXECUTION_REPLAY_REVIEW",
    "TERMINATED": "DOMAIN_GOVERNED_TERMINATION",
}


def detect_lifecycle_gaps(
    *,
    detection_id: str,
    observed_turns: list[dict[str, Any]],
    created_at: str,
    replay_dir: str | Path,
    expected_lifecycle: tuple[str, ...] = EXPECTED_LIFECYCLE,
    canonical_chain_id: str = "LIFECYCLE-GAP-CHAIN-000001",
) -> dict[str, Any]:
    """Detect lifecycle deviations from replay-visible ACLI turn summaries only."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        turns = _normalize_turns(observed_turns)
        expected = _normalize_expected_lifecycle(expected_lifecycle)
        gap_items = _detect_gap_items(turns=turns, expected_lifecycle=expected)
        evidence = _evidence_artifact(
            detection_id=detection_id,
            turns=turns,
            gap_items=gap_items,
            expected_lifecycle=expected,
            canonical_chain_id=canonical_chain_id,
            created_at=created_at,
            evidence_status="LIFECYCLE_GAP_EVIDENCE_CAPTURED",
            failure_reason=None,
        )
        classification = _classification_artifact(
            detection_id=detection_id,
            evidence=evidence,
            gap_items=gap_items,
            created_at=created_at,
            classification_status="LIFECYCLE_GAP_CLASSIFICATION_COMPLETED",
            failure_reason=None,
        )
        detection = _detection_artifact(
            detection_id=detection_id,
            evidence=evidence,
            classification=classification,
            created_at=created_at,
            detection_status=GAPS_DETECTED if gap_items else NO_GAPS_DETECTED,
            failure_reason=None,
        )
        returned = _returned_artifact(detection)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], evidence)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], classification)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], detection)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], returned)
        return _capture(evidence, classification, detection, returned, replay_path)
    except Exception as exc:
        evidence = _failed_evidence_artifact(
            detection_id=detection_id,
            observed_turns=observed_turns,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        classification = _classification_artifact(
            detection_id=detection_id if isinstance(detection_id, str) else "INVALID_DETECTION",
            evidence=evidence,
            gap_items=[],
            created_at=created_at,
            classification_status=FAILED_CLOSED,
            failure_reason=evidence["failure_reason"],
        )
        detection = _detection_artifact(
            detection_id=detection_id if isinstance(detection_id, str) else "INVALID_DETECTION",
            evidence=evidence,
            classification=classification,
            created_at=created_at,
            detection_status=FAILED_CLOSED,
            failure_reason=evidence["failure_reason"],
        )
        returned = _returned_artifact(detection)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], evidence)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], classification)
        _persist_failure_if_possible(replay_path, 2, REPLAY_STEPS[2], detection)
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], returned)
        return _capture(evidence, classification, detection, returned, replay_path)


def reconstruct_lifecycle_gap_detection_replay(replay_dir: str | Path) -> dict[str, Any]:
    replay_path = Path(replay_dir)
    wrappers = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("lifecycle gap detection replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("lifecycle gap detection replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "lifecycle gap detection artifact")
        wrappers.append(wrapper)
    evidence = wrappers[0]["artifact"]
    classification = wrappers[1]["artifact"]
    detection = wrappers[2]["artifact"]
    returned = wrappers[3]["artifact"]
    if classification.get("evidence_reference") != evidence["evidence_id"]:
        raise FailClosedRuntimeError("lifecycle gap detection evidence reference mismatch")
    if classification.get("evidence_hash") != evidence["artifact_hash"]:
        raise FailClosedRuntimeError("lifecycle gap detection evidence hash mismatch")
    if detection.get("classification_reference") != classification["classification_id"]:
        raise FailClosedRuntimeError("lifecycle gap detection classification reference mismatch")
    if detection.get("classification_hash") != classification["artifact_hash"]:
        raise FailClosedRuntimeError("lifecycle gap detection classification hash mismatch")
    if returned.get("detection_reference") != detection["detection_id"]:
        raise FailClosedRuntimeError("lifecycle gap detection returned reference mismatch")
    if returned.get("detection_hash") != detection["artifact_hash"]:
        raise FailClosedRuntimeError("lifecycle gap detection returned hash mismatch")
    return {
        "detection_id": detection["detection_id"],
        "detection_status": detection["detection_status"],
        "gap_count": detection["gap_count"],
        "gap_categories": deepcopy(detection["gap_categories"]),
        "expected_state": deepcopy(detection["expected_state"]),
        "observed_state": deepcopy(detection["observed_state"]),
        "human_review_required": detection["human_review_required"],
        "improvement_intent_allowed": detection["improvement_intent_allowed"],
        "failure_reason": detection["failure_reason"],
        "proposal_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _detect_gap_items(*, turns: list[dict[str, Any]], expected_lifecycle: tuple[str, ...]) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    observed_stages = [turn["current_lifecycle_stage"] for turn in turns]
    stage_positions = {stage: index for index, stage in enumerate(expected_lifecycle)}
    previous_position: int | None = None
    previous_turn: dict[str, Any] | None = None
    for turn in turns:
        status = turn["workflow_status"]
        stage = turn["current_lifecycle_stage"]
        source_ref = turn["source_replay_reference"]
        if status["workflow_state"] == FAILED_CLOSED or turn.get("fail_closed") is True:
            gaps.append(_gap(turn, "FAIL_CLOSED_INTERRUPTION", "non-failed lifecycle state", "FAILED_CLOSED", source_ref))
        if stage not in stage_positions and stage != FAILED_CLOSED:
            gaps.append(_gap(turn, "LIFECYCLE_STAGE_DEVIATION", "certified lifecycle stage", stage, source_ref))
        if stage in stage_positions:
            current_position = stage_positions[stage]
            if previous_position is not None and current_position < previous_position:
                gaps.append(
                    _gap(
                        turn,
                        "LIFECYCLE_STAGE_DEVIATION",
                        f"stage at or after {expected_lifecycle[previous_position]}",
                        stage,
                        source_ref,
                    )
                )
            previous_position = current_position
        action = str(status.get("next_expected_action") or "")
        if "the active domain" in action:
            gaps.append(_gap(turn, "PROJECTION_INCONSISTENCY", "domain-specific continuation", action, source_ref))
        if status["workflow_state"] == "CONTINUATION_AVAILABLE":
            if not action.strip() or action.startswith("Informational only:"):
                gaps.append(_gap(turn, "MISSING_CONTINUATION", "certified actionable continuation", action, source_ref))
        expected_workflow = EXPECTED_WORKFLOW_BY_STAGE.get(stage)
        workflow_name = str(status.get("workflow_name") or turn.get("response_source") or "")
        if expected_workflow is not None and workflow_name != expected_workflow:
            if not (stage == "EXECUTION_READY" and workflow_name == "DOMAIN_EXECUTION_READY_AUTHORIZATION_BRIDGE"):
                gaps.append(_gap(turn, "ROUTING_MISMATCH", expected_workflow, workflow_name, source_ref))
        if previous_turn is not None:
            previous_action = previous_turn["workflow_status"].get("next_expected_action")
            auto_action = turn.get("auto_continued_from_next_expected_action")
            input_mode = turn.get("multiline_input_mode")
            if auto_action is not None and auto_action != previous_action:
                gaps.append(_gap(turn, "REPLAY_CONTINUITY_BREAK", previous_action, auto_action, source_ref))
            if input_mode == "AUTO_CONTINUE" and auto_action is None:
                gaps.append(_gap(turn, "REPLAY_CONTINUITY_BREAK", "recorded auto continuation evidence", None, source_ref))
        previous_turn = turn
    missing = [stage for stage in expected_lifecycle if stage not in observed_stages]
    if missing and turns:
        gaps.append(
            _gap(
                turns[-1],
                "MISSING_CONTINUATION",
                f"observed lifecycle includes {missing[0]}",
                f"observed stages: {', '.join(observed_stages)}",
                turns[-1]["source_replay_reference"],
            )
        )
    return gaps


def _gap(turn: dict[str, Any], category: str, expected: Any, observed: Any, source_ref: str) -> dict[str, Any]:
    return {
        "gap_id": f"{turn['turn_id']}:{category}",
        "turn_id": turn["turn_id"],
        "gap_category": category,
        "expected_state": expected,
        "observed_state": observed,
        "source_replay_reference": source_ref,
        "source_replay_hash": turn["source_replay_hash"],
        "severity": "CRITICAL" if category == "REPLAY_CONTINUITY_BREAK" else "HIGH",
        "confidence": "DETERMINISTIC",
        "human_review_required": True,
        "improvement_intent_allowed": True,
    }


def _normalize_turns(observed_turns: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(observed_turns, list) or not observed_turns:
        raise FailClosedRuntimeError("lifecycle gap detection failed closed: replay evidence missing")
    turns = []
    for index, item in enumerate(observed_turns):
        if not isinstance(item, dict):
            raise FailClosedRuntimeError("lifecycle gap detection failed closed: replay evidence invalid")
        status = item.get("workflow_status")
        if not isinstance(status, dict):
            raise FailClosedRuntimeError("lifecycle gap detection failed closed: workflow status missing")
        source_ref = _source_reference(item, index)
        source_payload = {
            "turn_id": item.get("turn_id"),
            "response_source": item.get("response_source"),
            "workflow_status": status,
            "fail_closed": item.get("fail_closed") is True,
            "auto_continued_from_next_expected_action": item.get("auto_continued_from_next_expected_action"),
        }
        turns.append(
            {
                "turn_id": _require_string(item.get("turn_id") or f"TURN-{index + 1:06d}", "turn_id"),
                "response_source": item.get("response_source"),
                "workflow_status": deepcopy(status),
                "current_lifecycle_stage": _require_string(status.get("current_lifecycle_stage"), "current_lifecycle_stage"),
                "fail_closed": item.get("fail_closed") is True,
                "auto_continued_from_next_expected_action": item.get("auto_continued_from_next_expected_action"),
                "multiline_input_mode": item.get("multiline_input_mode"),
                "source_replay_reference": source_ref,
                "source_replay_payload": source_payload,
                "source_replay_hash": replay_hash(source_payload),
            }
        )
    return turns


def _source_reference(item: dict[str, Any], index: int) -> str:
    for key in ("replay_reference", "source_router_replay_reference", "multiline_prompt_capture_replay_reference"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return f"observed_turns[{index}]"


def _evidence_artifact(
    *,
    detection_id: str,
    turns: list[dict[str, Any]],
    gap_items: list[dict[str, Any]],
    expected_lifecycle: tuple[str, ...],
    canonical_chain_id: str,
    created_at: str,
    evidence_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": GAP_EVIDENCE_ARTIFACT_V1,
        "runtime_version": AIGOL_LIFECYCLE_GAP_DETECTION_RUNTIME_VERSION,
        "evidence_id": f"{_require_string(detection_id, 'detection_id')}:LIFECYCLE-GAP-EVIDENCE",
        "detection_reference": detection_id,
        "domain_id": "AIGOL_CORE",
        "expected_lifecycle": list(expected_lifecycle),
        "observed_lifecycle": [turn["current_lifecycle_stage"] for turn in turns],
        "observed_turns": deepcopy(turns),
        "evidence_items": [
            {
                **deepcopy(item),
                "canonical_chain_id": _require_string(canonical_chain_id, "canonical_chain_id"),
            }
            for item in gap_items
        ],
        "gap_evidence_items": deepcopy(gap_items),
        "evidence_count": len(turns),
        "gap_count": len(gap_items),
        "evidence_status": evidence_status,
        "detection_only": True,
        "proposal_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _classification_artifact(
    *,
    detection_id: str,
    evidence: dict[str, Any],
    gap_items: list[dict[str, Any]],
    created_at: str,
    classification_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": GAP_CLASSIFICATION_ARTIFACT_V1,
        "runtime_version": AIGOL_LIFECYCLE_GAP_DETECTION_RUNTIME_VERSION,
        "classification_id": f"{_require_string(detection_id, 'detection_id')}:LIFECYCLE-GAP-CLASSIFICATION",
        "detection_reference": detection_id,
        "evidence_reference": evidence["evidence_id"],
        "evidence_hash": evidence["artifact_hash"],
        "domain_id": evidence["domain_id"],
        "gap_classifications": deepcopy(gap_items),
        "gap_count": len(gap_items),
        "gap_categories": sorted({item["gap_category"] for item in gap_items}),
        "confidence": "DETERMINISTIC" if gap_items else "NONE",
        "human_review_required": bool(gap_items),
        "improvement_intent_allowed": bool(gap_items),
        "proposal_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "failure_reason": failure_reason,
        "classification_status": classification_status,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _detection_artifact(
    *,
    detection_id: str,
    evidence: dict[str, Any],
    classification: dict[str, Any],
    created_at: str,
    detection_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": GAP_DETECTION_ARTIFACT_V1,
        "runtime_version": AIGOL_LIFECYCLE_GAP_DETECTION_RUNTIME_VERSION,
        "detection_id": _require_string(detection_id, "detection_id"),
        "detection_status": detection_status,
        "domain_id": evidence["domain_id"],
        "evidence_reference": evidence["evidence_id"],
        "evidence_hash": evidence["artifact_hash"],
        "classification_reference": classification["classification_id"],
        "classification_hash": classification["artifact_hash"],
        "expected_state": {"lifecycle": deepcopy(evidence["expected_lifecycle"])},
        "observed_state": {"lifecycle": deepcopy(evidence["observed_lifecycle"])},
        "gap_count": classification["gap_count"],
        "gap_categories": deepcopy(classification["gap_categories"]),
        "confidence": classification["confidence"],
        "human_review_required": classification["human_review_required"],
        "improvement_intent_allowed": classification["improvement_intent_allowed"],
        "proposal_created": False,
        "improvement_proposal_created": False,
        "improvement_intent_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "authorization_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_evidence_artifact(*, detection_id: Any, observed_turns: Any, created_at: Any, failure_reason: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": GAP_EVIDENCE_ARTIFACT_V1,
        "runtime_version": AIGOL_LIFECYCLE_GAP_DETECTION_RUNTIME_VERSION,
        "evidence_id": f"{detection_id}:LIFECYCLE-GAP-EVIDENCE" if isinstance(detection_id, str) else "INVALID_DETECTION:LIFECYCLE-GAP-EVIDENCE",
        "detection_reference": detection_id if isinstance(detection_id, str) else "INVALID_DETECTION",
        "domain_id": "AIGOL_CORE",
        "expected_lifecycle": list(EXPECTED_LIFECYCLE),
        "observed_lifecycle": [],
        "observed_turns": observed_turns if isinstance(observed_turns, list) else [],
        "evidence_items": [],
        "gap_evidence_items": [],
        "evidence_count": len(observed_turns) if isinstance(observed_turns, list) else 0,
        "gap_count": 0,
        "evidence_status": FAILED_CLOSED,
        "detection_only": True,
        "proposal_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "created_at": created_at if isinstance(created_at, str) else None,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(detection: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(detection, "lifecycle gap detection artifact")
    artifact = {
        "event_type": "LIFECYCLE_GAP_DETECTION_RETURNED",
        "detection_reference": detection["detection_id"],
        "detection_hash": detection["artifact_hash"],
        "detection_status": detection["detection_status"],
        "gap_count": detection["gap_count"],
        "gap_categories": deepcopy(detection["gap_categories"]),
        "expected_state": deepcopy(detection["expected_state"]),
        "observed_state": deepcopy(detection["observed_state"]),
        "human_review_required": detection["human_review_required"],
        "improvement_intent_allowed": detection["improvement_intent_allowed"],
        "proposal_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "failure_reason": detection["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    evidence: dict[str, Any],
    classification: dict[str, Any],
    detection: dict[str, Any],
    returned: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "gap_evidence_artifact": deepcopy(evidence),
        "gap_classification_artifact": deepcopy(classification),
        "gap_detection_artifact": deepcopy(detection),
        "gap_detection_replay": deepcopy(returned),
        "gap_detection_replay_reference": str(replay_path),
        "detection_status": detection["detection_status"],
        "gap_count": detection["gap_count"],
        "gap_categories": deepcopy(detection["gap_categories"]),
        "expected_state": deepcopy(detection["expected_state"]),
        "observed_state": deepcopy(detection["observed_state"]),
        "confidence": detection["confidence"],
        "human_review_required": detection["human_review_required"],
        "improvement_intent_allowed": detection["improvement_intent_allowed"],
        "fail_closed": detection["detection_status"] == FAILED_CLOSED,
        "failure_reason": detection["failure_reason"],
        "proposal_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
    }
    capture["lifecycle_gap_detection_capture_hash"] = replay_hash(capture)
    return capture


def _normalize_expected_lifecycle(expected_lifecycle: tuple[str, ...]) -> tuple[str, ...]:
    if not isinstance(expected_lifecycle, tuple) or not expected_lifecycle:
        raise FailClosedRuntimeError("lifecycle gap detection failed closed: expected lifecycle missing")
    return tuple(_require_string(stage, "expected_lifecycle_stage") for stage in expected_lifecycle)


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {step}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("lifecycle gap detection replay step ordering mismatch")
    _verify_artifact_hash(artifact, "lifecycle gap detection artifact")
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
        raise FailClosedRuntimeError("lifecycle gap detection replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("lifecycle gap detection replay hash mismatch")


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"lifecycle gap detection failed closed: {label} missing")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "lifecycle gap detection failed closed"
