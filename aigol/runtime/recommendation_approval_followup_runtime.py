"""Recommendation approval continuity and follow-up candidates for AiGOL."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.operator_decision_support_runtime import (
    OPERATOR_DECISION_SUPPORT_ARTIFACT_V1,
    RECOMMENDATION_GENERATED,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_RECOMMENDATION_APPROVAL_AND_FOLLOWUP_RUNTIME_V1"
FINAL_CLASSIFICATION = "AIGOL_RECOMMENDATION_APPROVAL_AND_FOLLOWUP_RUNTIME_STATUS"

RECOMMENDATION_CONTINUITY_ARTIFACT_V1 = "RECOMMENDATION_CONTINUITY_ARTIFACT_V1"
RECOMMENDATION_APPROVAL_ARTIFACT_V1 = "RECOMMENDATION_APPROVAL_ARTIFACT_V1"
RECOMMENDATION_FOLLOWUP_ARTIFACT_V1 = "RECOMMENDATION_FOLLOWUP_ARTIFACT_V1"
COMMAND_BOUNDARY_COMPARISON_ARTIFACT_V1 = "COMMAND_BOUNDARY_COMPARISON_ARTIFACT_V1"
PLATFORM_SEMANTIC_GAP_CLOSURE_G2_10_COMMAND_BOUNDARY_AND_RECOMMENDATION_PROSE_CERTIFICATION_V1 = (
    "PLATFORM_SEMANTIC_GAP_CLOSURE_G2_10_COMMAND_BOUNDARY_AND_RECOMMENDATION_PROSE_CERTIFICATION_V1"
)

CONTINUITY_RECORDED = "RECOMMENDATION_CONTINUITY_RECORDED"
APPROVAL_RECORDED = "RECOMMENDATION_APPROVAL_RECORDED"
FOLLOWUP_CANDIDATE_GENERATED = "RECOMMENDATION_FOLLOWUP_CANDIDATE_GENERATED"
APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
FAILED_CLOSED = "FAILED_CLOSED"

APPROVE = "APPROVE"
REJECT = "REJECT"
IGNORE = "IGNORE"

PREPARE_PROPOSAL = "PREPARE_PROPOSAL"
PREPARE_IMPLEMENTATION_CANDIDATE = "PREPARE_IMPLEMENTATION_CANDIDATE"
PREPARE_DOMAIN_PLAN = "PREPARE_DOMAIN_PLAN"
PREPARE_ROADMAP = "PREPARE_ROADMAP"

CONTINUITY_REPLAY_STEPS = (
    "recommendation_continuity_recorded",
    "recommendation_continuity_returned",
)
APPROVAL_REPLAY_STEPS = (
    "recommendation_approval_recorded",
    "recommendation_approval_returned",
)
FOLLOWUP_REPLAY_STEPS = (
    "recommendation_followup_recorded",
    "recommendation_followup_returned",
)


def is_recommendation_approval_prompt(human_prompt: str) -> bool:
    normalized = str(human_prompt or "").lower().strip().rstrip(".?!")
    return normalized in {"i approve", "approve", "i approve the recommendation", "approve the recommendation"} or (
        "approve" in normalized and "recommendation" in normalized
    )


def is_recommendation_rejection_prompt(human_prompt: str) -> bool:
    normalized = str(human_prompt or "").lower().strip().rstrip(".?!")
    return normalized in {"i reject", "reject", "i reject the recommendation", "reject the recommendation"} or (
        "reject" in normalized and "recommendation" in normalized
    )


def is_recommendation_ignore_prompt(human_prompt: str) -> bool:
    normalized = str(human_prompt or "").lower().strip().rstrip(".?!")
    return normalized in {"ignore", "ignore the recommendation", "i ignore the recommendation"} or (
        "ignore" in normalized and "recommendation" in normalized
    )


def is_recommendation_followup_prompt(human_prompt: str) -> bool:
    return _followup_action(human_prompt) is not None


def create_recommendation_continuity(
    *,
    continuity_id: str,
    recommendation_artifact: dict[str, Any],
    conversation_reference: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path, CONTINUITY_REPLAY_STEPS, "recommendation continuity")
        recommendation = deepcopy(recommendation_artifact)
        _validate_recommendation(recommendation)
        artifact = _continuity_artifact(
            continuity_id=continuity_id,
            recommendation=recommendation,
            conversation_reference=conversation_reference,
            created_at=created_at,
            replay_reference=str(replay_path),
            failure_reason=None,
        )
        returned = _returned_artifact(
            event_type="RECOMMENDATION_CONTINUITY_RETURNED",
            reference_field="continuity_reference",
            hash_field="continuity_hash",
            artifact=artifact,
            status_field="continuity_status",
        )
        _persist_step(replay_path, 0, CONTINUITY_REPLAY_STEPS, artifact)
        _persist_step(replay_path, 1, CONTINUITY_REPLAY_STEPS, returned)
        return _continuity_capture(artifact, returned, replay_path)
    except Exception as exc:
        failure_reason = _failure_reason(exc, "recommendation continuity failed closed")
        artifact = _failed_continuity_artifact(
            continuity_id=continuity_id,
            recommendation_artifact=recommendation_artifact,
            conversation_reference=conversation_reference,
            created_at=created_at,
            replay_reference=str(replay_path),
            failure_reason=failure_reason,
        )
        returned = _returned_artifact(
            event_type="RECOMMENDATION_CONTINUITY_RETURNED",
            reference_field="continuity_reference",
            hash_field="continuity_hash",
            artifact=artifact,
            status_field="continuity_status",
        )
        _persist_failure_if_possible(replay_path, 0, CONTINUITY_REPLAY_STEPS, artifact)
        _persist_failure_if_possible(replay_path, 1, CONTINUITY_REPLAY_STEPS, returned)
        return _continuity_capture(artifact, returned, replay_path)


def record_recommendation_approval(
    *,
    approval_id: str,
    recommendation_continuity_artifact: dict[str, Any],
    operator_decision: str,
    approval_timestamp: str,
    replay_dir: str | Path,
    canonical_semantic_lineage: dict[str, Any] | None = None,
) -> dict[str, Any]:
    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path, APPROVAL_REPLAY_STEPS, "recommendation approval")
        continuity = deepcopy(recommendation_continuity_artifact)
        _validate_continuity(continuity)
        decision = _normalize_operator_decision(operator_decision)
        command_boundary = _command_boundary_artifact(
            boundary_id=f"{approval_id}:G2-10-COMMAND-BOUNDARY",
            boundary_scope="RECOMMENDATION_APPROVAL_COMMAND",
            parser_name="RECOMMENDATION_APPROVAL_COMMAND_PARSER",
            parser_matched=True,
            parser_decision=decision,
            human_prompt=operator_decision,
            canonical_semantic_lineage=canonical_semantic_lineage,
            created_at=approval_timestamp,
            replay_reference=str(replay_path),
            fallback_reason=None,
        )
        artifact = _approval_artifact(
            approval_id=approval_id,
            continuity=continuity,
            operator_decision=decision,
            command_boundary=command_boundary,
            approval_timestamp=approval_timestamp,
            replay_reference=str(replay_path),
            failure_reason=None,
        )
        returned = _returned_artifact(
            event_type="RECOMMENDATION_APPROVAL_RETURNED",
            reference_field="approval_reference",
            hash_field="approval_hash",
            artifact=artifact,
            status_field="approval_status",
        )
        _persist_step(replay_path, 0, APPROVAL_REPLAY_STEPS, artifact)
        _persist_step(replay_path, 1, APPROVAL_REPLAY_STEPS, returned)
        return _approval_capture(artifact, returned, replay_path)
    except Exception as exc:
        failure_reason = _failure_reason(exc, "recommendation approval failed closed")
        artifact = _failed_approval_artifact(
            approval_id=approval_id,
            recommendation_continuity_artifact=recommendation_continuity_artifact,
            operator_decision=operator_decision,
            command_boundary=_command_boundary_artifact(
                boundary_id=f"{approval_id}:G2-10-COMMAND-BOUNDARY"
                if isinstance(approval_id, str)
                else "INVALID-APPROVAL:G2-10-COMMAND-BOUNDARY",
                boundary_scope="RECOMMENDATION_APPROVAL_COMMAND",
                parser_name="RECOMMENDATION_APPROVAL_COMMAND_PARSER",
                parser_matched=False,
                parser_decision=None,
                human_prompt=operator_decision if isinstance(operator_decision, str) else "",
                canonical_semantic_lineage=canonical_semantic_lineage,
                created_at=approval_timestamp,
                replay_reference=str(replay_path),
                fallback_reason="COMMAND_PARSER_NON_MATCH",
            ),
            approval_timestamp=approval_timestamp,
            replay_reference=str(replay_path),
            failure_reason=failure_reason,
        )
        returned = _returned_artifact(
            event_type="RECOMMENDATION_APPROVAL_RETURNED",
            reference_field="approval_reference",
            hash_field="approval_hash",
            artifact=artifact,
            status_field="approval_status",
        )
        _persist_failure_if_possible(replay_path, 0, APPROVAL_REPLAY_STEPS, artifact)
        _persist_failure_if_possible(replay_path, 1, APPROVAL_REPLAY_STEPS, returned)
        return _approval_capture(artifact, returned, replay_path)


def create_recommendation_followup(
    *,
    followup_id: str,
    recommendation_continuity_artifact: dict[str, Any],
    recommendation_approval_artifact: dict[str, Any],
    human_prompt: str,
    created_at: str,
    replay_dir: str | Path,
    canonical_semantic_lineage: dict[str, Any] | None = None,
) -> dict[str, Any]:
    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path, FOLLOWUP_REPLAY_STEPS, "recommendation followup")
        continuity = deepcopy(recommendation_continuity_artifact)
        approval = deepcopy(recommendation_approval_artifact)
        _validate_continuity(continuity)
        _validate_approval(approval, continuity)
        if approval.get("operator_decision") != APPROVE:
            raise FailClosedRuntimeError("recommendation followup failed closed: explicit approval is required")
        action = _followup_action(human_prompt)
        command_boundary = _command_boundary_artifact(
            boundary_id=f"{followup_id}:G2-10-COMMAND-BOUNDARY",
            boundary_scope="RECOMMENDATION_FOLLOWUP_COMMAND",
            parser_name="RECOMMENDATION_FOLLOWUP_COMMAND_PARSER",
            parser_matched=action is not None,
            parser_decision=action,
            human_prompt=human_prompt,
            canonical_semantic_lineage=canonical_semantic_lineage,
            created_at=created_at,
            replay_reference=str(replay_path),
            fallback_reason=None if action is not None else "COMMAND_PARSER_NON_MATCH",
        )
        if action is None:
            raise FailClosedRuntimeError("recommendation followup failed closed: unsupported follow-up action")
        artifact = _followup_artifact(
            followup_id=followup_id,
            continuity=continuity,
            approval=approval,
            human_prompt=human_prompt,
            followup_action=action,
            command_boundary=command_boundary,
            created_at=created_at,
            replay_reference=str(replay_path),
            failure_reason=None,
        )
        returned = _returned_artifact(
            event_type="RECOMMENDATION_FOLLOWUP_RETURNED",
            reference_field="followup_reference",
            hash_field="followup_hash",
            artifact=artifact,
            status_field="followup_status",
        )
        _persist_step(replay_path, 0, FOLLOWUP_REPLAY_STEPS, artifact)
        _persist_step(replay_path, 1, FOLLOWUP_REPLAY_STEPS, returned)
        return _followup_capture(artifact, returned, replay_path)
    except Exception as exc:
        failure_reason = _failure_reason(exc, "recommendation followup failed closed")
        artifact = _failed_followup_artifact(
            followup_id=followup_id,
            recommendation_continuity_artifact=recommendation_continuity_artifact,
            recommendation_approval_artifact=recommendation_approval_artifact,
            human_prompt=human_prompt,
            command_boundary=_command_boundary_artifact(
                boundary_id=f"{followup_id}:G2-10-COMMAND-BOUNDARY"
                if isinstance(followup_id, str)
                else "INVALID-FOLLOWUP:G2-10-COMMAND-BOUNDARY",
                boundary_scope="RECOMMENDATION_FOLLOWUP_COMMAND",
                parser_name="RECOMMENDATION_FOLLOWUP_COMMAND_PARSER",
                parser_matched=_followup_action(human_prompt) is not None if isinstance(human_prompt, str) else False,
                parser_decision=_followup_action(human_prompt) if isinstance(human_prompt, str) else None,
                human_prompt=human_prompt if isinstance(human_prompt, str) else "",
                canonical_semantic_lineage=canonical_semantic_lineage,
                created_at=created_at,
                replay_reference=str(replay_path),
                fallback_reason=None
                if isinstance(human_prompt, str) and _followup_action(human_prompt) is not None
                else "COMMAND_PARSER_NON_MATCH",
            ),
            created_at=created_at,
            replay_reference=str(replay_path),
            failure_reason=failure_reason,
        )
        returned = _returned_artifact(
            event_type="RECOMMENDATION_FOLLOWUP_RETURNED",
            reference_field="followup_reference",
            hash_field="followup_hash",
            artifact=artifact,
            status_field="followup_status",
        )
        _persist_failure_if_possible(replay_path, 0, FOLLOWUP_REPLAY_STEPS, artifact)
        _persist_failure_if_possible(replay_path, 1, FOLLOWUP_REPLAY_STEPS, returned)
        return _followup_capture(artifact, returned, replay_path)


def reconstruct_recommendation_continuity_replay(replay_dir: str | Path) -> dict[str, Any]:
    artifact, returned, wrappers = _reconstruct(replay_dir, CONTINUITY_REPLAY_STEPS, "continuity")
    if returned.get("continuity_reference") != artifact["continuity_id"]:
        raise FailClosedRuntimeError("recommendation continuity replay reference mismatch")
    if returned.get("continuity_hash") != artifact["artifact_hash"]:
        raise FailClosedRuntimeError("recommendation continuity replay hash mismatch")
    return _reconstruction_common(artifact, wrappers, "continuity_status")


def reconstruct_recommendation_approval_replay(replay_dir: str | Path) -> dict[str, Any]:
    artifact, returned, wrappers = _reconstruct(replay_dir, APPROVAL_REPLAY_STEPS, "approval")
    if returned.get("approval_reference") != artifact["approval_id"]:
        raise FailClosedRuntimeError("recommendation approval replay reference mismatch")
    if returned.get("approval_hash") != artifact["artifact_hash"]:
        raise FailClosedRuntimeError("recommendation approval replay hash mismatch")
    return _reconstruction_common(artifact, wrappers, "approval_status")


def reconstruct_recommendation_followup_replay(replay_dir: str | Path) -> dict[str, Any]:
    artifact, returned, wrappers = _reconstruct(replay_dir, FOLLOWUP_REPLAY_STEPS, "followup")
    if returned.get("followup_reference") != artifact["followup_id"]:
        raise FailClosedRuntimeError("recommendation followup replay reference mismatch")
    if returned.get("followup_hash") != artifact["artifact_hash"]:
        raise FailClosedRuntimeError("recommendation followup replay hash mismatch")
    return _reconstruction_common(artifact, wrappers, "followup_status")


def render_recommendation_continuity_summary(capture: dict[str, Any]) -> str:
    artifact = capture.get("recommendation_continuity_artifact") or {}
    lines = [
        "Recommendation Continuity Recorded",
        f"recommendation_reference: {artifact.get('recommendation_reference')}",
        f"recommended: {artifact.get('recommended')}",
        f"approval_required: {artifact.get('approval_required')}",
        f"approval_status: {artifact.get('approval_status')}",
        "Available Next Actions:",
    ]
    lines.extend(f"* {item}" for item in artifact.get("followup_candidates", []))
    lines.append("Operator Selection Required")
    return "\n".join(lines)


def render_recommendation_approval_summary(capture: dict[str, Any]) -> str:
    artifact = capture.get("recommendation_approval_artifact") or {}
    lines = [
        "Recommendation Approval Recorded",
        f"operator_decision: {artifact.get('operator_decision')}",
        f"recommended: {artifact.get('recommended')}",
        "Available Next Actions:",
    ]
    lines.extend(f"* {item}" for item in artifact.get("available_next_actions", []))
    lines.extend(
        [
            "Operator Selection Required",
            f"replay_reference: {capture.get('recommendation_approval_replay_reference')}",
            f"provider_invoked: {capture.get('provider_invoked')}",
            f"worker_invoked: {capture.get('worker_invoked')}",
            f"execution_requested: {capture.get('execution_requested')}",
        ]
    )
    return "\n".join(lines)


def render_recommendation_followup_summary(capture: dict[str, Any]) -> str:
    artifact = capture.get("recommendation_followup_artifact") or {}
    lines = [
        "Recommendation Follow-Up Candidate Generated",
        f"followup_action: {artifact.get('followup_action')}",
        f"candidate_title: {artifact.get('candidate', {}).get('title')}",
        f"target_recommendation: {artifact.get('recommended')}",
        f"candidate_status: {artifact.get('candidate_status')}",
        f"replay_reference: {capture.get('recommendation_followup_replay_reference')}",
        f"provider_invoked: {capture.get('provider_invoked')}",
        f"worker_invoked: {capture.get('worker_invoked')}",
        f"execution_requested: {capture.get('execution_requested')}",
        f"implementation_authorized: {capture.get('implementation_authorized')}",
    ]
    if artifact.get("failure_reason"):
        lines.append(f"failure_reason: {artifact['failure_reason']}")
    return "\n".join(lines)


def _continuity_artifact(
    *,
    continuity_id: str,
    recommendation: dict[str, Any],
    conversation_reference: str,
    created_at: str,
    replay_reference: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": RECOMMENDATION_CONTINUITY_ARTIFACT_V1,
        "milestone_id": MILESTONE_ID,
        "continuity_id": _require_string(continuity_id, "continuity_id"),
        "recommendation_reference": recommendation["recommendation_id"],
        "recommendation_hash": recommendation["artifact_hash"],
        "recommendation_business_hash": recommendation.get("recommendation_hash"),
        "conversation_reference": _require_string(conversation_reference, "conversation_reference"),
        "recommended": recommendation.get("recommendation"),
        "recommendation_category": recommendation.get("category"),
        "continuity_status": CONTINUITY_RECORDED,
        "approval_required": True,
        "approval_status": APPROVAL_REQUIRED,
        "followup_candidates": _followup_candidates(recommendation),
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "lineage_bound": True,
        **_authority_flags(),
        "failure_reason": failure_reason,
    }
    artifact["continuity_hash"] = replay_hash(_continuity_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _approval_artifact(
    *,
    approval_id: str,
    continuity: dict[str, Any],
    operator_decision: str,
    command_boundary: dict[str, Any],
    approval_timestamp: str,
    replay_reference: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": RECOMMENDATION_APPROVAL_ARTIFACT_V1,
        "milestone_id": MILESTONE_ID,
        "approval_id": _require_string(approval_id, "approval_id"),
        "recommendation_reference": continuity["recommendation_reference"],
        "recommendation_hash": continuity["recommendation_hash"],
        "continuity_reference": continuity["continuity_id"],
        "continuity_hash": continuity["artifact_hash"],
        "operator_decision": operator_decision,
        "approval_status": _approval_status(operator_decision),
        **_command_boundary_fields(command_boundary),
        "approval_timestamp": _require_string(approval_timestamp, "approval_timestamp"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "recommended": continuity.get("recommended"),
        "available_next_actions": _available_next_actions(operator_decision),
        "replay_visible": True,
        "lineage_bound": True,
        **_authority_flags(),
        "failure_reason": failure_reason,
    }
    artifact["approval_hash"] = replay_hash(_approval_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _followup_artifact(
    *,
    followup_id: str,
    continuity: dict[str, Any],
    approval: dict[str, Any],
    human_prompt: str,
    followup_action: str,
    command_boundary: dict[str, Any],
    created_at: str,
    replay_reference: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    candidate = _candidate_for_action(followup_action, continuity)
    artifact = {
        "artifact_type": RECOMMENDATION_FOLLOWUP_ARTIFACT_V1,
        "milestone_id": MILESTONE_ID,
        "followup_id": _require_string(followup_id, "followup_id"),
        "recommendation_reference": continuity["recommendation_reference"],
        "recommendation_hash": continuity["recommendation_hash"],
        "continuity_reference": continuity["continuity_id"],
        "continuity_hash": continuity["artifact_hash"],
        "approval_reference": approval["approval_id"],
        "approval_hash": approval["artifact_hash"],
        "operator_prompt_hash": replay_hash(_require_string(human_prompt, "human_prompt")),
        "followup_action": followup_action,
        **_command_boundary_fields(command_boundary),
        "followup_status": FOLLOWUP_CANDIDATE_GENERATED,
        "candidate_status": FOLLOWUP_CANDIDATE_GENERATED,
        "candidate": candidate,
        "recommended": continuity.get("recommended"),
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "lineage_bound": True,
        **_authority_flags(),
        "implementation_authorized": False,
        "failure_reason": failure_reason,
    }
    artifact["followup_hash"] = replay_hash(_followup_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_continuity_artifact(
    *,
    continuity_id: str,
    recommendation_artifact: Any,
    conversation_reference: str,
    created_at: str,
    replay_reference: str,
    failure_reason: str,
) -> dict[str, Any]:
    recommendation = recommendation_artifact if isinstance(recommendation_artifact, dict) else {}
    artifact = {
        "artifact_type": RECOMMENDATION_CONTINUITY_ARTIFACT_V1,
        "milestone_id": MILESTONE_ID,
        "continuity_id": continuity_id if isinstance(continuity_id, str) else None,
        "recommendation_reference": recommendation.get("recommendation_id"),
        "recommendation_hash": recommendation.get("artifact_hash"),
        "conversation_reference": conversation_reference if isinstance(conversation_reference, str) else None,
        "recommended": recommendation.get("recommendation"),
        "recommendation_category": recommendation.get("category"),
        "continuity_status": FAILED_CLOSED,
        "approval_required": True,
        "approval_status": FAILED_CLOSED,
        "followup_candidates": [],
        "created_at": created_at if isinstance(created_at, str) else "",
        "replay_reference": replay_reference,
        "replay_visible": True,
        "lineage_bound": True,
        **_authority_flags(),
        "failure_reason": failure_reason,
    }
    artifact["continuity_hash"] = replay_hash(_continuity_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_approval_artifact(
    *,
    approval_id: str,
    recommendation_continuity_artifact: Any,
    operator_decision: Any,
    command_boundary: dict[str, Any],
    approval_timestamp: str,
    replay_reference: str,
    failure_reason: str,
) -> dict[str, Any]:
    continuity = recommendation_continuity_artifact if isinstance(recommendation_continuity_artifact, dict) else {}
    artifact = {
        "artifact_type": RECOMMENDATION_APPROVAL_ARTIFACT_V1,
        "milestone_id": MILESTONE_ID,
        "approval_id": approval_id if isinstance(approval_id, str) else None,
        "recommendation_reference": continuity.get("recommendation_reference"),
        "recommendation_hash": continuity.get("recommendation_hash"),
        "continuity_reference": continuity.get("continuity_id"),
        "continuity_hash": continuity.get("artifact_hash"),
        "operator_decision": operator_decision if isinstance(operator_decision, str) else None,
        "approval_status": FAILED_CLOSED,
        **_command_boundary_fields(command_boundary),
        "approval_timestamp": approval_timestamp if isinstance(approval_timestamp, str) else "",
        "replay_reference": replay_reference,
        "recommended": continuity.get("recommended"),
        "available_next_actions": [],
        "replay_visible": True,
        "lineage_bound": True,
        **_authority_flags(),
        "failure_reason": failure_reason,
    }
    artifact["approval_hash"] = replay_hash(_approval_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_followup_artifact(
    *,
    followup_id: str,
    recommendation_continuity_artifact: Any,
    recommendation_approval_artifact: Any,
    human_prompt: Any,
    command_boundary: dict[str, Any],
    created_at: str,
    replay_reference: str,
    failure_reason: str,
) -> dict[str, Any]:
    continuity = recommendation_continuity_artifact if isinstance(recommendation_continuity_artifact, dict) else {}
    approval = recommendation_approval_artifact if isinstance(recommendation_approval_artifact, dict) else {}
    artifact = {
        "artifact_type": RECOMMENDATION_FOLLOWUP_ARTIFACT_V1,
        "milestone_id": MILESTONE_ID,
        "followup_id": followup_id if isinstance(followup_id, str) else None,
        "recommendation_reference": continuity.get("recommendation_reference"),
        "recommendation_hash": continuity.get("recommendation_hash"),
        "continuity_reference": continuity.get("continuity_id"),
        "continuity_hash": continuity.get("artifact_hash"),
        "approval_reference": approval.get("approval_id"),
        "approval_hash": approval.get("artifact_hash"),
        "operator_prompt_hash": replay_hash(human_prompt) if isinstance(human_prompt, str) else None,
        "followup_action": _followup_action(human_prompt) if isinstance(human_prompt, str) else None,
        **_command_boundary_fields(command_boundary),
        "followup_status": FAILED_CLOSED,
        "candidate_status": FAILED_CLOSED,
        "candidate": {},
        "recommended": continuity.get("recommended"),
        "created_at": created_at if isinstance(created_at, str) else "",
        "replay_reference": replay_reference,
        "replay_visible": True,
        "lineage_bound": True,
        **_authority_flags(),
        "implementation_authorized": False,
        "failure_reason": failure_reason,
    }
    artifact["followup_hash"] = replay_hash(_followup_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _continuity_capture(artifact: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    return _capture(
        command="aigol recommendation continuity",
        response_source="RECOMMENDATION_CONTINUITY_RUNTIME",
        status_key="continuity_status",
        artifact_key="recommendation_continuity_artifact",
        returned_key="recommendation_continuity_returned",
        replay_key="recommendation_continuity_replay_reference",
        artifact=artifact,
        returned=returned,
        replay_path=replay_path,
    )


def _approval_capture(artifact: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    return _capture(
        command="aigol recommendation approve",
        response_source="RECOMMENDATION_APPROVAL_RUNTIME",
        status_key="approval_status",
        artifact_key="recommendation_approval_artifact",
        returned_key="recommendation_approval_returned",
        replay_key="recommendation_approval_replay_reference",
        artifact=artifact,
        returned=returned,
        replay_path=replay_path,
    )


def _followup_capture(artifact: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    return _capture(
        command="aigol recommendation followup",
        response_source="RECOMMENDATION_FOLLOWUP_RUNTIME",
        status_key="followup_status",
        artifact_key="recommendation_followup_artifact",
        returned_key="recommendation_followup_returned",
        replay_key="recommendation_followup_replay_reference",
        artifact=artifact,
        returned=returned,
        replay_path=replay_path,
    )


def _capture(
    *,
    command: str,
    response_source: str,
    status_key: str,
    artifact_key: str,
    returned_key: str,
    replay_key: str,
    artifact: dict[str, Any],
    returned: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    status = returned.get(status_key)
    capture = {
        "command": command,
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "response_status": status,
        "response_source": response_source,
        status_key: status,
        artifact_key: deepcopy(artifact),
        returned_key: deepcopy(returned),
        replay_key: str(replay_path),
        "conversation_replay_reference": str(replay_path),
        "recommendation_reference": artifact.get("recommendation_reference"),
        "recommendation_hash": artifact.get("recommendation_hash"),
        "continuity_reference": artifact.get("continuity_reference") or artifact.get("continuity_id"),
        "approval_reference": artifact.get("approval_reference") or artifact.get("approval_id"),
        "followup_action": artifact.get("followup_action"),
        "command_boundary_source": artifact.get("command_boundary_source"),
        "command_parser_decision": deepcopy(artifact.get("command_parser_decision")),
        "command_boundary_comparison_artifact": deepcopy(artifact.get("command_boundary_comparison_artifact")),
        "command_boundary_comparison_hash": artifact.get("command_boundary_comparison_hash"),
        "command_boundary_parity_status": artifact.get("command_boundary_parity_status"),
        "command_boundary_migration_batch_id": artifact.get("command_boundary_migration_batch_id"),
        "canonical_semantic_artifact_reference": artifact.get("canonical_semantic_artifact_reference"),
        "canonical_semantic_artifact_hash": artifact.get("canonical_semantic_artifact_hash"),
        "command_boundary_fallback_reason": artifact.get("command_boundary_fallback_reason"),
        "fail_closed": status == FAILED_CLOSED,
        "failure_reason": returned.get("failure_reason"),
        **_authority_flags(),
        "implementation_authorized": False,
    }
    capture["response_text"] = ""
    capture["capture_hash"] = replay_hash(capture)
    return capture


def _returned_artifact(
    *,
    event_type: str,
    reference_field: str,
    hash_field: str,
    artifact: dict[str, Any],
    status_field: str,
) -> dict[str, Any]:
    _verify_artifact_hash(artifact)
    reference_key = {
        "continuity_reference": "continuity_id",
        "approval_reference": "approval_id",
        "followup_reference": "followup_id",
    }[reference_field]
    artifact_status = artifact.get(status_field)
    returned = {
        "event_type": event_type,
        "milestone_id": MILESTONE_ID,
        reference_field: artifact[reference_key],
        hash_field: artifact["artifact_hash"],
        status_field: artifact_status,
        "recommendation_reference": artifact.get("recommendation_reference"),
        "recommendation_hash": artifact.get("recommendation_hash"),
        "command_boundary_source": artifact.get("command_boundary_source"),
        "command_boundary_comparison_hash": artifact.get("command_boundary_comparison_hash"),
        "command_boundary_parity_status": artifact.get("command_boundary_parity_status"),
        "command_boundary_migration_batch_id": artifact.get("command_boundary_migration_batch_id"),
        "canonical_semantic_artifact_hash": artifact.get("canonical_semantic_artifact_hash"),
        "replay_visible": True,
        **_authority_flags(),
        "implementation_authorized": False,
        "failure_reason": artifact.get("failure_reason"),
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _reconstruct(replay_dir: str | Path, steps: tuple[str, ...], label: str) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(steps):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError(f"recommendation {label} replay ordering mismatch")
        _verify_wrapper_hash(wrapper, label)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError(f"recommendation {label} replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    return wrappers[0]["artifact"], wrappers[1]["artifact"], wrappers


def _reconstruction_common(artifact: dict[str, Any], wrappers: list[dict[str, Any]], status_key: str) -> dict[str, Any]:
    return {
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        status_key: artifact.get(status_key),
        "recommendation_reference": artifact.get("recommendation_reference"),
        "recommendation_hash": artifact.get("recommendation_hash"),
        "recommended": artifact.get("recommended"),
        "followup_action": artifact.get("followup_action"),
        "candidate_status": artifact.get("candidate_status"),
        "command_boundary_source": artifact.get("command_boundary_source"),
        "command_parser_decision": deepcopy(artifact.get("command_parser_decision")),
        "command_boundary_comparison_artifact": deepcopy(artifact.get("command_boundary_comparison_artifact")),
        "command_boundary_comparison_hash": artifact.get("command_boundary_comparison_hash"),
        "command_boundary_parity_status": artifact.get("command_boundary_parity_status"),
        "command_boundary_migration_batch_id": artifact.get("command_boundary_migration_batch_id"),
        "canonical_semantic_artifact_reference": artifact.get("canonical_semantic_artifact_reference"),
        "canonical_semantic_artifact_hash": artifact.get("canonical_semantic_artifact_hash"),
        "command_boundary_fallback_reason": artifact.get("command_boundary_fallback_reason"),
        "replay_visible": True,
        "lineage_bound": True,
        "replay_artifact_count": len(wrappers),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "implementation_authorized": False,
        "approval_bypassed": False,
        "domain_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "replay_hash": replay_hash(wrappers),
    }


def _validate_recommendation(recommendation: dict[str, Any]) -> None:
    if recommendation.get("artifact_type") != OPERATOR_DECISION_SUPPORT_ARTIFACT_V1:
        raise FailClosedRuntimeError("recommendation continuity failed closed: invalid recommendation artifact")
    _verify_artifact_hash(recommendation)
    if recommendation.get("recommendation_status") != RECOMMENDATION_GENERATED:
        raise FailClosedRuntimeError("recommendation continuity failed closed: recommendation is not generated")


def _validate_continuity(continuity: dict[str, Any]) -> None:
    if continuity.get("artifact_type") != RECOMMENDATION_CONTINUITY_ARTIFACT_V1:
        raise FailClosedRuntimeError("recommendation approval failed closed: invalid continuity artifact")
    _verify_artifact_hash(continuity)
    if continuity.get("approval_required") is not True:
        raise FailClosedRuntimeError("recommendation approval failed closed: approval is not required")


def _validate_approval(approval: dict[str, Any], continuity: dict[str, Any]) -> None:
    if approval.get("artifact_type") != RECOMMENDATION_APPROVAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("recommendation followup failed closed: invalid approval artifact")
    _verify_artifact_hash(approval)
    if approval.get("continuity_hash") != continuity["artifact_hash"]:
        raise FailClosedRuntimeError("recommendation followup failed closed: approval continuity mismatch")


def _command_boundary_artifact(
    *,
    boundary_id: str,
    boundary_scope: str,
    parser_name: str,
    parser_matched: bool,
    parser_decision: str | None,
    human_prompt: str,
    canonical_semantic_lineage: dict[str, Any] | None,
    created_at: str,
    replay_reference: str,
    fallback_reason: str | None,
) -> dict[str, Any]:
    lineage = _normalize_canonical_semantic_lineage(canonical_semantic_lineage)
    csa_available = lineage["canonical_semantic_artifact_hash"] is not None
    csa_used = not parser_matched and csa_available
    parser = {
        "parser_name": _require_string(parser_name, "parser_name"),
        "parser_matched": parser_matched,
        "parser_decision": parser_decision,
        "parser_authoritative": parser_matched,
        "exact_command_authority_preserved": True,
    }
    csa = {
        "source": "CANONICAL_SEMANTIC_ARTIFACT_COMMAND_PROSE_OBSERVATION",
        "available": csa_available,
        "used": csa_used,
        "canonical_semantic_artifact_reference": lineage["canonical_semantic_artifact_reference"],
        "canonical_semantic_artifact_hash": lineage["canonical_semantic_artifact_hash"],
        "semantic_routing_source": lineage["semantic_routing_source"],
        "source_migration_batch_id": lineage["migration_batch_id"],
        "parser_non_match_required": True,
    }
    if parser_matched:
        source = "DETERMINISTIC_COMMAND_PARSER"
        parity_status = "COMMAND_PARSER_AUTHORITATIVE"
        equivalence = "NOT_APPLIED"
        differences = []
    elif csa_used:
        source = "CANONICAL_SEMANTIC_ARTIFACT_AFTER_COMMAND_NON_MATCH"
        parity_status = "CSA_OBSERVATIONAL_AFTER_COMMAND_NON_MATCH"
        equivalence = "OBSERVED_ONLY"
        differences = ["Compatibility command parser produced no exact match."]
    else:
        source = "COMPATIBILITY_FALLBACK"
        parity_status = "COMPATIBILITY_FALLBACK_AUTHORITATIVE"
        equivalence = "NOT_EVALUATED"
        differences = ["No deterministic command match and no CSA lineage available."]
    artifact = {
        "artifact_type": COMMAND_BOUNDARY_COMPARISON_ARTIFACT_V1,
        "boundary_id": _require_string(boundary_id, "boundary_id"),
        "boundary_scope": _require_string(boundary_scope, "boundary_scope"),
        "migration_batch_id": PLATFORM_SEMANTIC_GAP_CLOSURE_G2_10_COMMAND_BOUNDARY_AND_RECOMMENDATION_PROSE_CERTIFICATION_V1,
        "command_boundary_source": source,
        "command_parser_decision": parser,
        "csa_command_prose_interpretation": csa,
        "canonical_semantic_artifact_reference": lineage["canonical_semantic_artifact_reference"],
        "canonical_semantic_artifact_hash": lineage["canonical_semantic_artifact_hash"],
        "fallback_reason": fallback_reason,
        "semantic_equivalence_result": equivalence,
        "semantic_differences": differences,
        "parity_status": parity_status,
        "semantic_parity_evidence": {
            "parity_status": parity_status,
            "parity_scope": boundary_scope,
            "exact_command_authority_preserved": True,
            "csa_requires_parser_non_match": True,
            "compatibility_fallback_available": True,
            "approval_authority_transferred": False,
            "execution_authority_granted": False,
            "provider_invoked": False,
            "worker_invoked": False,
        },
        "replay_lineage": {
            "replay_reference": _require_string(replay_reference, "replay_reference"),
            "operator_prompt_hash": replay_hash(_require_string(human_prompt, "human_prompt")),
        },
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        **_authority_flags(),
    }
    artifact["semantic_comparison_hash"] = replay_hash(
        {
            "parser": parser,
            "csa": csa,
            "parity_status": parity_status,
            "fallback_reason": fallback_reason,
        }
    )
    artifact["semantic_parity_evidence"]["semantic_comparison_hash"] = artifact["semantic_comparison_hash"]
    artifact["semantic_parity_evidence"]["parity_hash"] = replay_hash(artifact["semantic_parity_evidence"])
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _command_boundary_fields(command_boundary: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(command_boundary)
    return {
        "command_boundary_source": command_boundary["command_boundary_source"],
        "command_parser_decision": deepcopy(command_boundary["command_parser_decision"]),
        "command_boundary_comparison_artifact": deepcopy(command_boundary),
        "command_boundary_comparison_hash": command_boundary["artifact_hash"],
        "command_boundary_parity_status": command_boundary["parity_status"],
        "command_boundary_migration_batch_id": command_boundary["migration_batch_id"],
        "canonical_semantic_artifact_reference": command_boundary.get("canonical_semantic_artifact_reference"),
        "canonical_semantic_artifact_hash": command_boundary.get("canonical_semantic_artifact_hash"),
        "command_boundary_fallback_reason": command_boundary.get("fallback_reason"),
    }


def _normalize_canonical_semantic_lineage(source: dict[str, Any] | None) -> dict[str, Any]:
    source = source if isinstance(source, dict) else {}
    reference = source.get("canonical_semantic_artifact_reference")
    artifact_hash = source.get("canonical_semantic_artifact_hash")
    return {
        "canonical_semantic_artifact_reference": reference if isinstance(reference, str) else None,
        "canonical_semantic_artifact_hash": artifact_hash if isinstance(artifact_hash, str) else None,
        "semantic_routing_source": source.get("semantic_routing_source"),
        "migration_batch_id": source.get("migration_batch_id"),
    }


def _followup_action(human_prompt: str) -> str | None:
    normalized = str(human_prompt or "").lower().strip().rstrip(".?!")
    if "proposal" in normalized:
        return PREPARE_PROPOSAL
    if "implementation candidate" in normalized or ("implementation" in normalized and "candidate" in normalized):
        return PREPARE_IMPLEMENTATION_CANDIDATE
    if "domain plan" in normalized or ("plan" in normalized and "domain" in normalized):
        return PREPARE_DOMAIN_PLAN
    if "roadmap" in normalized:
        return PREPARE_ROADMAP
    return None


def _candidate_for_action(action: str, continuity: dict[str, Any]) -> dict[str, Any]:
    recommended = continuity.get("recommended") or "RECOMMENDATION"
    if action == PREPARE_PROPOSAL:
        title = f"Product Domain Proposal Candidate: {recommended}"
        sections = ["purpose", "target users", "decision validation scope", "non-goals", "human review gates"]
    elif action == PREPARE_IMPLEMENTATION_CANDIDATE:
        title = f"Implementation Candidate: {recommended}"
        sections = ["candidate scope", "required approvals", "validation evidence", "blocked execution steps"]
    elif action == PREPARE_DOMAIN_PLAN:
        title = f"Domain Plan Candidate: {recommended}"
        sections = ["domain boundaries", "capabilities", "lineage model", "acceptance checks"]
    else:
        title = f"Roadmap Candidate: {recommended}"
        sections = ["milestones", "dependencies", "risks", "review checkpoints"]
    return {
        "title": title,
        "target": recommended,
        "sections": sections,
        "candidate_only": True,
        "requires_human_review": True,
        "creates_domain": False,
        "authorizes_implementation": False,
        "authorizes_execution": False,
    }


def _followup_candidates(recommendation: dict[str, Any]) -> list[str]:
    if recommendation.get("category") == "DOMAIN_SELECTION":
        return [
            "Prepare Product Domain Proposal",
            "Prepare Domain Plan",
            "Prepare Implementation Candidate",
            "Prepare Roadmap",
        ]
    return [
        "Prepare Proposal",
        "Prepare Implementation Candidate",
        "Prepare Roadmap",
    ]


def _available_next_actions(operator_decision: str) -> list[str]:
    if operator_decision != APPROVE:
        return []
    return [
        "Prepare Product Domain Proposal",
        "Prepare Domain Plan",
        "Prepare Implementation Candidate",
        "Prepare Roadmap",
    ]


def _normalize_operator_decision(value: str) -> str:
    normalized = _require_string(value, "operator_decision").upper().strip()
    if normalized not in {APPROVE, REJECT, IGNORE}:
        raise FailClosedRuntimeError("recommendation approval failed closed: unsupported operator decision")
    return normalized


def _approval_status(operator_decision: str) -> str:
    if operator_decision == APPROVE:
        return APPROVAL_RECORDED
    if operator_decision == REJECT:
        return "RECOMMENDATION_REJECTED"
    return "RECOMMENDATION_IGNORED"


def _continuity_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "continuity_id": artifact.get("continuity_id"),
        "recommendation_reference": artifact.get("recommendation_reference"),
        "recommendation_hash": artifact.get("recommendation_hash"),
        "conversation_reference": artifact.get("conversation_reference"),
        "approval_required": artifact.get("approval_required"),
        "approval_status": artifact.get("approval_status"),
        "followup_candidates": artifact.get("followup_candidates", []),
    }


def _approval_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "approval_id": artifact.get("approval_id"),
        "recommendation_hash": artifact.get("recommendation_hash"),
        "continuity_hash": artifact.get("continuity_hash"),
        "operator_decision": artifact.get("operator_decision"),
        "approval_timestamp": artifact.get("approval_timestamp"),
    }


def _followup_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "followup_id": artifact.get("followup_id"),
        "recommendation_hash": artifact.get("recommendation_hash"),
        "continuity_hash": artifact.get("continuity_hash"),
        "approval_hash": artifact.get("approval_hash"),
        "followup_action": artifact.get("followup_action"),
        "candidate": artifact.get("candidate", {}),
    }


def _authority_flags() -> dict[str, bool]:
    return {
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_bypassed": False,
        "domain_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _persist_step(replay_dir: Path, index: int, steps: tuple[str, ...], artifact: dict[str, Any]) -> None:
    step = steps[index]
    _verify_artifact_hash(artifact)
    wrapper = {"replay_index": index, "replay_step": step, "artifact": deepcopy(artifact)}
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, index: int, steps: tuple[str, ...], artifact: dict[str, Any]) -> None:
    try:
        path = replay_dir / f"{index:03d}_{steps[index]}.json"
        if not path.exists():
            _persist_step(replay_dir, index, steps, artifact)
    except FailClosedRuntimeError:
        return


def _ensure_replay_available(replay_dir: Path, steps: tuple[str, ...], label: str) -> None:
    for index, step in enumerate(steps):
        if (replay_dir / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError(f"{label} failed closed: replay already exists")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("recommendation continuity artifact hash is required")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("recommendation continuity artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any], label: str) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError(f"recommendation {label} replay hash is required")
    expected_input = deepcopy(wrapper)
    expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"recommendation {label} replay hash mismatch")


def _failure_reason(exc: Exception, fallback: str) -> str:
    return str(exc) if isinstance(exc, FailClosedRuntimeError) else fallback


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()
