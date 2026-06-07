"""End-to-end OCS LLM cognition orchestration runtime."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

from aigol.runtime.cognition_comparison_runtime import (
    COGNITION_COMPARISON_ARTIFACT_V1,
    COGNITION_COMPARISON_RETURNED_V1,
    CERTIFIED_CLASSIFICATION as COGNITION_COMPARISON_CERTIFIED_CLASSIFICATION,
    MILESTONE_ID as COGNITION_COMPARISON_RUNTIME_VERSION,
    reconstruct_cognition_comparison_replay,
    run_cognition_comparison_runtime,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.multi_provider_cognition_runtime import (
    MULTI_PROVIDER_COGNITION_RESULT_BUNDLE_V1,
    reconstruct_multi_provider_cognition_replay,
    run_multi_provider_cognition_runtime,
)
from aigol.runtime.ocs_context_assembly_runtime import (
    OCS_CONTEXT_ASSEMBLED,
    OCS_CONTEXT_ASSEMBLY_ARTIFACT_V1,
    assemble_ocs_context,
    reconstruct_ocs_context_assembly_replay,
)
from aigol.runtime.ocs_llm_cognition_continuity_and_clarification_runtime import (
    COGNITION_CLARIFICATION_ARTIFACT_V1,
    COGNITION_CONTINUITY_ARTIFACT_V1,
    COGNITION_HISTORY_REFERENCE_V1,
    reconstruct_ocs_llm_cognition_continuity_and_clarification_replay,
    run_ocs_llm_cognition_continuity_and_clarification,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_OCS_LLM_COGNITION_END_TO_END_V1"
FINAL_CLASSIFICATION = "AIGOL_OCS_LLM_COGNITION_END_TO_END_STATUS"
CERTIFIED_CLASSIFICATION = "CERTIFIED_OCS_LLM_COGNITION_END_TO_END"

OCS_LLM_COGNITION_END_TO_END_ARTIFACT_V1 = "OCS_LLM_COGNITION_END_TO_END_ARTIFACT_V1"
OCS_LLM_COGNITION_END_TO_END_RETURNED_V1 = "OCS_LLM_COGNITION_END_TO_END_RETURNED_V1"

STATUS_COMPLETED = "COMPLETED"
STATUS_FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "ocs_llm_cognition_end_to_end_artifact",
    "ocs_llm_cognition_end_to_end_returned",
)

AUTHORITY_FLAGS = {
    "provider_authority": False,
    "approval_authority": False,
    "execution_authority": False,
    "worker_authority": False,
    "governance_authority": False,
    "replay_authority": False,
}

ProviderTransport = Callable[[dict[str, Any], dict[str, Any]], Any]


def run_ocs_llm_cognition_end_to_end(
    *,
    end_to_end_id: str,
    human_question: str,
    source_context: dict[str, Any],
    provider_contracts: list[dict[str, Any]],
    transport_registry: dict[str, ProviderTransport],
    created_at: str,
    replay_dir: str | Path,
    source_chain_id: str | None = None,
    source_request_reference: str | None = None,
    prior_cognition_artifacts: list[dict[str, Any]] | None = None,
    prior_comparison_artifacts: list[dict[str, Any]] | None = None,
    prior_clarification_artifacts: list[dict[str, Any]] | None = None,
    single_provider_primary_mode: bool = False,
    disagreement_threshold: int = 1,
    uncertainty_threshold: int = 1,
    minimum_confidence: str = "HIGH",
) -> dict[str, Any]:
    """Run the complete governed OCS LLM cognition workflow."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        end_to_end = _require_string(end_to_end_id, "end_to_end_id")
        question = _require_string(human_question, "human_question")
        timestamp = _require_string(created_at, "created_at")
        stage_paths = _stage_replay_paths(replay_path)

        context_capture = assemble_ocs_context(
            context_assembly_id=f"{end_to_end}:OCS_CONTEXT",
            created_at=timestamp,
            replay_dir=stage_paths["context"],
            source_context=source_context,
            source_chain_id=source_chain_id,
            source_request_reference=source_request_reference,
        )
        _require_stage_success(context_capture, "OCS context assembly")
        context_artifact = _validate_context_artifact(context_capture["ocs_context_assembly_artifact"])

        multi_capture = run_multi_provider_cognition_runtime(
            multi_provider_cognition_bundle_id=f"{end_to_end}:MULTI_PROVIDER_COGNITION",
            human_request=question,
            ocs_context_artifact=context_artifact,
            provider_contracts=provider_contracts,
            created_at=timestamp,
            replay_dir=stage_paths["multi_provider_cognition"],
            transport_registry=transport_registry,
        )
        _require_stage_success(multi_capture, "multi-provider cognition")
        result_bundle = _validate_result_bundle(multi_capture["result_bundle"])

        comparison_id = f"{end_to_end}:COGNITION_COMPARISON"
        if single_provider_primary_mode and len(result_bundle.get("provider_results", [])) == 1:
            comparison_capture = _single_provider_primary_comparison_capture(
                cognition_comparison_id=comparison_id,
                result_bundle=result_bundle,
                created_at=timestamp,
                replay_dir=stage_paths["cognition_comparison"],
            )
        else:
            comparison_capture = run_cognition_comparison_runtime(
                cognition_comparison_id=comparison_id,
                multi_provider_result_bundle=result_bundle,
                created_at=timestamp,
                replay_dir=stage_paths["cognition_comparison"],
            )
        _require_stage_success(comparison_capture, "cognition comparison")
        comparison_artifact = _validate_comparison_artifact(comparison_capture["cognition_comparison_artifact"])

        continuity_capture = run_ocs_llm_cognition_continuity_and_clarification(
            continuity_id=f"{end_to_end}:COGNITION_CONTINUITY",
            clarification_id=f"{end_to_end}:COGNITION_CLARIFICATION",
            current_comparison_artifact=comparison_artifact,
            prior_cognition_artifacts=prior_cognition_artifacts,
            prior_comparison_artifacts=prior_comparison_artifacts,
            prior_clarification_artifacts=prior_clarification_artifacts,
            created_at=timestamp,
            replay_dir=stage_paths["continuity_and_clarification"],
            disagreement_threshold=disagreement_threshold,
            uncertainty_threshold=uncertainty_threshold,
            minimum_confidence=minimum_confidence,
        )
        _require_stage_success(continuity_capture, "cognition continuity and clarification")

        artifact = _end_to_end_artifact(
            end_to_end_id=end_to_end,
            human_question=question,
            created_at=timestamp,
            context_artifact=context_artifact,
            result_bundle=result_bundle,
            comparison_artifact=comparison_artifact,
            continuity_artifact=continuity_capture["cognition_continuity_artifact"],
            clarification_artifact=continuity_capture["cognition_clarification_artifact"],
            history_reference=continuity_capture["history_reference"],
            stage_replay_references={key: str(value) for key, value in stage_paths.items()},
            failure_reason="",
            workflow_status=STATUS_COMPLETED,
            single_provider_primary_mode=single_provider_primary_mode,
        )
        returned = _returned_artifact(artifact)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(
            final_status=STATUS_COMPLETED,
            artifact=artifact,
            returned=returned,
            replay_path=replay_path,
            failure_reason="",
            stage_captures={
                "context": context_capture,
                "multi_provider_cognition": multi_capture,
                "cognition_comparison": comparison_capture,
                "continuity_and_clarification": continuity_capture,
            },
        )
    except Exception as exc:
        failure_reason = str(exc) if isinstance(exc, FailClosedRuntimeError) else "OCS LLM cognition end-to-end failed closed"
        timestamp = created_at if _is_nonempty_string(created_at) else "1970-01-01T00:00:00Z"
        artifact = _failed_end_to_end_artifact(
            end_to_end_id=end_to_end_id if _is_nonempty_string(end_to_end_id) else "OCS-LLM-COGNITION-E2E-INVALID",
            human_question=human_question if _is_nonempty_string(human_question) else "",
            created_at=timestamp,
            replay_path=replay_path,
            failure_reason=failure_reason,
        )
        returned = _returned_artifact(artifact)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(
            final_status=STATUS_FAILED_CLOSED,
            artifact=artifact,
            returned=returned,
            replay_path=replay_path,
            failure_reason=failure_reason,
            stage_captures={},
        )


def reconstruct_ocs_llm_cognition_end_to_end_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct the complete end-to-end cognition replay chain."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("OCS LLM cognition end-to-end replay ordering mismatch")
        _verify_replay_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("OCS LLM cognition end-to-end replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "OCS LLM cognition end-to-end replay artifact")
        wrappers.append(wrapper)

    artifact = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("end_to_end_artifact_hash") != artifact["artifact_hash"]:
        raise FailClosedRuntimeError("OCS LLM cognition end-to-end returned hash mismatch")
    if artifact.get("end_to_end_hash") != _compute_end_to_end_hash(artifact):
        raise FailClosedRuntimeError("OCS LLM cognition end-to-end hash mismatch")

    stage_refs = artifact.get("stage_replay_references") or {}
    if artifact.get("workflow_status") == STATUS_COMPLETED:
        context_replay = reconstruct_ocs_context_assembly_replay(stage_refs["context"])
        multi_replay = reconstruct_multi_provider_cognition_replay(stage_refs["multi_provider_cognition"])
        comparison_replay = reconstruct_cognition_comparison_replay(stage_refs["cognition_comparison"])
        continuity_replay = reconstruct_ocs_llm_cognition_continuity_and_clarification_replay(
            stage_refs["continuity_and_clarification"]
        )
        _verify_stage_hashes(artifact, context_replay, multi_replay, comparison_replay, continuity_replay)
    else:
        context_replay = {}
        multi_replay = {}
        comparison_replay = {}
        continuity_replay = {}

    return {
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "classification": artifact.get("classification"),
        "final_status": artifact.get("workflow_status"),
        "end_to_end_id": artifact.get("end_to_end_id"),
        "artifact_type": artifact.get("artifact_type"),
        "context_hash": artifact.get("context_hash"),
        "provider_count": artifact.get("provider_count"),
        "successful_provider_count": artifact.get("successful_provider_count"),
        "failed_provider_count": artifact.get("failed_provider_count"),
        "cognition_artifact_count": len(artifact.get("cognition_artifact_hashes", [])),
        "comparison_confidence": artifact.get("human_facing_cognition_result", {}).get("comparison_confidence"),
        "clarification_required": artifact.get("human_facing_cognition_result", {}).get("clarification_required"),
        "clarification_candidate_count": artifact.get("human_facing_cognition_result", {}).get(
            "clarification_candidate_count"
        ),
        "stage_replay_references": deepcopy(stage_refs),
        "stage_replay": {
            "context": context_replay,
            "multi_provider_cognition": multi_replay,
            "cognition_comparison": comparison_replay,
            "continuity_and_clarification": continuity_replay,
        },
        "authority_flags": deepcopy(artifact.get("authority_flags", {})),
        "replay_visible": True,
        "worker_invoked": False,
        "execution_requested": False,
        "approval_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def render_ocs_llm_cognition_end_to_end_summary(result: dict[str, Any]) -> str:
    artifact = result.get("ocs_llm_cognition_end_to_end_artifact") or {}
    human_result = artifact.get("human_facing_cognition_result", {})
    return "\n".join(
        [
            "AIGOL OCS LLM COGNITION END-TO-END",
            f"status: {result.get('final_status')}",
            f"classification: {result.get('classification')}",
            f"end_to_end_id: {result.get('end_to_end_id')}",
            f"provider_count: {artifact.get('provider_count')}",
            f"successful_provider_count: {artifact.get('successful_provider_count')}",
            f"comparison_confidence: {human_result.get('comparison_confidence')}",
            f"clarification_required: {human_result.get('clarification_required')}",
            f"replay_reference: {result.get('replay_reference')}",
            f"fail_closed: {result.get('fail_closed')}",
            f"failure_reason: {result.get('failure_reason') or ''}",
        ]
    )


def render_operator_visible_ocs_llm_cognition(result: dict[str, Any]) -> str:
    artifact = result.get("ocs_llm_cognition_end_to_end_artifact") or {}
    human_result = artifact.get("human_facing_cognition_result")
    if not isinstance(human_result, dict):
        human_result = {}
    return "\n".join(
        [
            "AIGOL OCS COGNITION",
            "Findings:",
            *_render_bullets(human_result.get("findings")),
            "Assumptions:",
            *_render_bullets(human_result.get("assumptions")),
            "Risks:",
            *_render_bullets(human_result.get("risks")),
            "Uncertainties:",
            *_render_bullets(human_result.get("uncertainties")),
            "Clarification Questions:",
            *_render_bullets(human_result.get("clarification_questions")),
            "Recommended Next Milestone:",
            *_render_bullets([human_result.get("recommended_next_milestone")]),
        ]
    )


def _render_bullets(items: Any) -> list[str]:
    if not isinstance(items, list):
        items = []
    rendered = [_render_item(item) for item in items]
    rendered = [item for item in rendered if item]
    if not rendered:
        return ["- (none recorded)"]
    return [f"- {item}" for item in rendered]


def _render_item(item: Any) -> str:
    if isinstance(item, str):
        return _clean_operator_text(item)
    if not isinstance(item, dict):
        return ""
    if isinstance(item.get("question"), str):
        return _clean_operator_text(item["question"])
    if isinstance(item.get("text"), str):
        return _clean_operator_text(item["text"])
    if isinstance(item.get("summary"), str):
        return _clean_operator_text(item["summary"])
    if isinstance(item.get("reason"), str):
        return _clean_operator_text(item["reason"])
    if isinstance(item.get("missing"), str):
        return _clean_operator_text(f"Missing {item['missing']}")
    return ""


def _clean_operator_text(value: str) -> str:
    text = " ".join(str(value).split())
    if not text:
        return ""
    if _looks_like_json(text):
        return ""
    return text


def _looks_like_json(value: str) -> bool:
    stripped = value.strip()
    if not ((stripped.startswith("{") and stripped.endswith("}")) or (stripped.startswith("[") and stripped.endswith("]"))):
        return False
    try:
        parsed = json.loads(stripped)
    except (TypeError, json.JSONDecodeError):
        return False
    return isinstance(parsed, (dict, list))


def _end_to_end_artifact(
    *,
    end_to_end_id: str,
    human_question: str,
    created_at: str,
    context_artifact: dict[str, Any],
    result_bundle: dict[str, Any],
    comparison_artifact: dict[str, Any],
    continuity_artifact: dict[str, Any],
    clarification_artifact: dict[str, Any],
    history_reference: dict[str, Any],
    stage_replay_references: dict[str, str],
    failure_reason: str,
    workflow_status: str,
    single_provider_primary_mode: bool,
) -> dict[str, Any]:
    provider_results = result_bundle.get("provider_results", [])
    human_result = _human_facing_result(result_bundle, comparison_artifact, clarification_artifact)
    artifact = {
        "artifact_type": OCS_LLM_COGNITION_END_TO_END_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "classification": CERTIFIED_CLASSIFICATION,
        "end_to_end_id": end_to_end_id,
        "workflow_status": workflow_status,
        "human_question": human_question,
        "human_question_hash": replay_hash(human_question),
        "context_artifact_type": context_artifact["artifact_type"],
        "context_assembly_id": context_artifact["context_assembly_id"],
        "context_hash": context_artifact["context_hash"],
        "context_artifact_hash": context_artifact["artifact_hash"],
        "multi_provider_result_bundle_hash": result_bundle["artifact_hash"],
        "multi_provider_result_bundle_result_hash": result_bundle["result_bundle_hash"],
        "provider_count": result_bundle["provider_count"],
        "successful_provider_count": result_bundle["successful_provider_count"],
        "failed_provider_count": result_bundle["failed_provider_count"],
        "provider_request_artifact_hashes": [item["provider_request_artifact_hash"] for item in provider_results],
        "provider_response_artifact_hashes": [item["provider_response_artifact_hash"] for item in provider_results],
        "cognition_artifact_hashes": result_bundle["cognition_artifact_hashes"],
        "provider_failure_hashes": result_bundle["provider_failure_hashes"],
        "single_provider_primary_mode": bool(single_provider_primary_mode),
        "comparison_required": not bool(single_provider_primary_mode),
        "comparison_performed": comparison_artifact.get("single_provider_primary_mode") is not True,
        "comparison_artifact_hash": comparison_artifact["artifact_hash"],
        "comparison_hash": comparison_artifact["comparison_hash"],
        "history_reference_hash": history_reference["artifact_hash"],
        "history_hash": history_reference["history_hash"],
        "continuity_artifact_hash": continuity_artifact["artifact_hash"],
        "continuity_hash": continuity_artifact["continuity_hash"],
        "clarification_artifact_hash": clarification_artifact["artifact_hash"],
        "clarification_hash": clarification_artifact["clarification_hash"],
        "human_facing_cognition_result": human_result,
        "stage_replay_references": deepcopy(stage_replay_references),
        "lineage_refs": {
            "human_question_hash": replay_hash(human_question),
            "context_hash": context_artifact["context_hash"],
            "context_artifact_hash": context_artifact["artifact_hash"],
            "multi_provider_result_bundle_hash": result_bundle["artifact_hash"],
            "source_cognition_artifact_hashes": result_bundle["cognition_artifact_hashes"],
            "comparison_artifact_hash": comparison_artifact["artifact_hash"],
            "history_reference_hash": history_reference["artifact_hash"],
            "continuity_artifact_hash": continuity_artifact["artifact_hash"],
            "clarification_artifact_hash": clarification_artifact["artifact_hash"],
        },
        "governance_preservation": {
            "llm_proposes": True,
            "aigol_governs": True,
            "worker_executes": True,
            "replay_records": True,
            "human_review_required": True,
            "provider_output_authoritative": False,
            "comparison_output_authoritative": False,
            "clarification_output_authoritative": False,
        },
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "non_authoritative": True,
        "human_review_required": True,
        "replay_visible": True,
        "provider_invoked": True,
        "approval_created": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "failure_reason": failure_reason,
        "created_at": created_at,
    }
    artifact["end_to_end_hash"] = _compute_end_to_end_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _human_facing_result(
    result_bundle: dict[str, Any],
    comparison_artifact: dict[str, Any],
    clarification_artifact: dict[str, Any],
) -> dict[str, Any]:
    clarification_candidates = deepcopy(clarification_artifact.get("clarification_candidates", []))
    cognition_artifacts = _source_cognition_artifacts(result_bundle)
    return {
        "result_type": "HUMAN_FACING_COGNITION_RESULT",
        "summary": "Provider-assisted cognition completed. Human review remains required before any downstream action.",
        "comparison_confidence": comparison_artifact.get("comparison_confidence"),
        "comparison_findings": deepcopy(comparison_artifact.get("comparison_findings", [])),
        "findings": _operator_cognition_items(cognition_artifacts, "findings"),
        "assumptions": _operator_cognition_items(cognition_artifacts, "assumptions"),
        "risks": _operator_cognition_items(cognition_artifacts, "risks"),
        "uncertainties": _operator_cognition_items(cognition_artifacts, "uncertainties"),
        "comparison_performed": comparison_artifact.get("single_provider_primary_mode") is not True,
        "single_provider_primary_mode": comparison_artifact.get("single_provider_primary_mode") is True,
        "clarification_required": clarification_artifact.get("clarification_required") is True,
        "clarification_status": clarification_artifact.get("clarification_status"),
        "clarification_candidate_count": len(clarification_candidates),
        "clarification_candidates": clarification_candidates,
        "clarification_questions": [
            item["question"] for item in clarification_candidates if isinstance(item, dict) and item.get("question")
        ],
        "recommended_next_milestone": "Human review of normalized cognition output.",
        "allowed_next_step": "HUMAN_REVIEW",
        "approval_created": False,
        "execution_requested": False,
        "worker_invoked": False,
        "non_authoritative": True,
    }


def _source_cognition_artifacts(result_bundle: dict[str, Any]) -> list[dict[str, Any]]:
    provider_results = result_bundle.get("provider_results", [])
    if not isinstance(provider_results, list):
        return []
    artifacts = []
    for item in provider_results:
        if not isinstance(item, dict):
            continue
        artifact = item.get("llm_cognition_artifact")
        if isinstance(artifact, dict):
            artifacts.append(artifact)
    return artifacts


def _operator_cognition_items(cognition_artifacts: list[dict[str, Any]], field_name: str) -> list[str]:
    items: list[str] = []
    for artifact in cognition_artifacts:
        items.extend(_operator_items_from_value(artifact.get(field_name), field_name))
    return _dedupe_operator_items(items)


def _operator_items_from_value(value: Any, field_name: str) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        items: list[str] = []
        for item in value:
            items.extend(_operator_items_from_value(item, field_name))
        return items
    if isinstance(value, str):
        parsed = _parse_operator_json(value)
        if parsed is not None:
            return _operator_items_from_value(parsed.get(field_name), field_name) if isinstance(parsed, dict) else []
        cleaned = _clean_operator_text(value)
        return [cleaned] if cleaned else []
    if isinstance(value, dict):
        if field_name in value:
            return _operator_items_from_value(value.get(field_name), field_name)
        for key in ("text", "question", "summary", "reason"):
            if isinstance(value.get(key), str):
                cleaned = _clean_operator_text(value[key])
                return [cleaned] if cleaned else []
    return []


def _parse_operator_json(value: str) -> Any | None:
    stripped = value.strip()
    if not ((stripped.startswith("{") and stripped.endswith("}")) or (stripped.startswith("[") and stripped.endswith("]"))):
        return None
    try:
        return json.loads(stripped)
    except (TypeError, json.JSONDecodeError):
        return None


def _dedupe_operator_items(items: list[str]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()
    for item in items:
        normalized = " ".join(item.split())
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(normalized)
    return deduped


def _failed_end_to_end_artifact(
    *,
    end_to_end_id: str,
    human_question: str,
    created_at: str,
    replay_path: Path,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": OCS_LLM_COGNITION_END_TO_END_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "classification": CERTIFIED_CLASSIFICATION,
        "end_to_end_id": end_to_end_id,
        "workflow_status": STATUS_FAILED_CLOSED,
        "human_question": human_question,
        "human_question_hash": replay_hash(human_question),
        "context_artifact_type": None,
        "context_assembly_id": None,
        "context_hash": None,
        "context_artifact_hash": None,
        "multi_provider_result_bundle_hash": None,
        "multi_provider_result_bundle_result_hash": None,
        "provider_count": 0,
        "successful_provider_count": 0,
        "failed_provider_count": 0,
        "provider_request_artifact_hashes": [],
        "provider_response_artifact_hashes": [],
        "cognition_artifact_hashes": [],
        "provider_failure_hashes": [],
        "single_provider_primary_mode": False,
        "comparison_required": True,
        "comparison_performed": False,
        "comparison_artifact_hash": None,
        "comparison_hash": None,
        "history_reference_hash": None,
        "history_hash": None,
        "continuity_artifact_hash": None,
        "continuity_hash": None,
        "clarification_artifact_hash": None,
        "clarification_hash": None,
        "human_facing_cognition_result": {
            "result_type": "HUMAN_FACING_COGNITION_RESULT",
            "summary": "Provider-assisted cognition failed closed before a human-facing result could be completed.",
            "clarification_required": False,
            "clarification_candidate_count": 0,
            "clarification_candidates": [],
            "allowed_next_step": "HUMAN_REVIEW_OF_FAILURE",
            "approval_created": False,
            "execution_requested": False,
            "worker_invoked": False,
            "non_authoritative": True,
        },
        "stage_replay_references": {key: str(value) for key, value in _stage_replay_paths(replay_path).items()},
        "lineage_refs": {
            "human_question_hash": replay_hash(human_question),
            "context_hash": None,
            "context_artifact_hash": None,
            "multi_provider_result_bundle_hash": None,
            "source_cognition_artifact_hashes": [],
            "comparison_artifact_hash": None,
            "history_reference_hash": None,
            "continuity_artifact_hash": None,
            "clarification_artifact_hash": None,
        },
        "governance_preservation": {
            "llm_proposes": True,
            "aigol_governs": True,
            "worker_executes": True,
            "replay_records": True,
            "human_review_required": True,
            "provider_output_authoritative": False,
            "comparison_output_authoritative": False,
            "clarification_output_authoritative": False,
        },
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "non_authoritative": True,
        "human_review_required": True,
        "replay_visible": True,
        "provider_invoked": False,
        "approval_created": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "failure_reason": failure_reason,
        "created_at": created_at,
    }
    artifact["end_to_end_hash"] = _compute_end_to_end_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    returned = {
        "artifact_type": OCS_LLM_COGNITION_END_TO_END_RETURNED_V1,
        "runtime_version": MILESTONE_ID,
        "end_to_end_id": artifact["end_to_end_id"],
        "end_to_end_artifact_hash": artifact["artifact_hash"],
        "workflow_status": artifact["workflow_status"],
        "clarification_required": artifact["human_facing_cognition_result"]["clarification_required"],
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "replay_visible": True,
        "approval_created": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _single_provider_primary_comparison_capture(
    *,
    cognition_comparison_id: str,
    result_bundle: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    replay_path = Path(replay_dir)
    _ensure_comparison_replay_available(replay_path)
    provider_results = result_bundle.get("provider_results", [])
    if len(provider_results) != 1:
        raise FailClosedRuntimeError("single-provider primary mode requires exactly one successful cognition artifact")
    cognition_artifact = provider_results[0].get("llm_cognition_artifact")
    if not isinstance(cognition_artifact, dict):
        raise FailClosedRuntimeError("single-provider primary cognition artifact is required")
    artifact = _single_provider_primary_comparison_artifact(
        cognition_comparison_id=cognition_comparison_id,
        result_bundle=result_bundle,
        cognition_artifact=cognition_artifact,
        created_at=created_at,
    )
    returned = _comparison_returned_artifact(artifact)
    _persist_comparison_step(replay_path, 0, "cognition_comparison_artifact", artifact)
    _persist_comparison_step(replay_path, 1, "cognition_comparison_returned", returned)
    return {
        "command": "aigol cognition comparison run",
        "milestone_id": COGNITION_COMPARISON_RUNTIME_VERSION,
        "final_classification": "AIGOL_COGNITION_COMPARISON_RUNTIME_STATUS",
        "classification": COGNITION_COMPARISON_CERTIFIED_CLASSIFICATION,
        "final_status": STATUS_COMPLETED,
        "cognition_comparison_id": artifact["cognition_comparison_id"],
        "cognition_comparison_artifact": deepcopy(artifact),
        "cognition_comparison_returned": deepcopy(returned),
        "comparison_confidence": artifact["comparison_confidence"],
        "single_provider_primary_mode": True,
        "comparison_performed": False,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "replay_reference": str(replay_path),
        "approval_created": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "fail_closed": False,
        "failure_reason": "",
    }


def _single_provider_primary_comparison_artifact(
    *,
    cognition_comparison_id: str,
    result_bundle: dict[str, Any],
    cognition_artifact: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    source = _single_provider_source_summary(cognition_artifact)
    provider_id = source["provider_id"]
    uncertainty = [
        {
            "text": item,
            "provider_id": provider_id,
            "source": "single_provider_uncertainty",
        }
        for item in cognition_artifact.get("uncertainties", [])
    ]
    missing_information = []
    for field in ("findings", "assumptions", "alternatives", "risks", "uncertainties"):
        if not cognition_artifact.get(field):
            missing_information.append(
                {
                    "provider_id": provider_id,
                    "missing": field,
                    "reason": "source cognition artifact field empty",
                }
            )
    artifact = {
        "artifact_type": COGNITION_COMPARISON_ARTIFACT_V1,
        "runtime_version": COGNITION_COMPARISON_RUNTIME_VERSION,
        "classification": COGNITION_COMPARISON_CERTIFIED_CLASSIFICATION,
        "cognition_comparison_id": _require_string(cognition_comparison_id, "cognition_comparison_id"),
        "comparison_status": STATUS_COMPLETED,
        "multi_provider_cognition_bundle_id": result_bundle["multi_provider_cognition_bundle_id"],
        "source_result_bundle_hash": result_bundle["artifact_hash"],
        "source_result_bundle_result_hash": result_bundle["result_bundle_hash"],
        "context_hash": result_bundle["context_hash"],
        "source_cognition_artifacts": [source],
        "provider_identities": [deepcopy(cognition_artifact["provider_identity"])],
        "comparison_findings": [
            "Single-provider primary cognition completed.",
            "Comparison was not performed in default conversational OCS mode.",
            f"Provider cognition confidence: {cognition_artifact.get('confidence')}.",
        ],
        "agreement": [],
        "disagreement": [
            {"text": item, "providers": [provider_id], "provider_count": 1}
            for item in cognition_artifact.get("findings", [])
        ],
        "conflicting_assumptions": [],
        "conflicting_risks": [],
        "conflicting_alternatives": [],
        "uncertainty": uncertainty,
        "missing_information": missing_information,
        "comparison_confidence": cognition_artifact.get("confidence") or "UNKNOWN",
        "comparison_policy": {
            "comparison_method": "single_provider_primary_mode_no_comparison",
            "confidence_model": "single provider normalized cognition confidence",
            "non_authoritative": True,
            "human_review_required": True,
        },
        "lineage_refs": {
            "multi_provider_result_bundle_hash": result_bundle["artifact_hash"],
            "multi_provider_result_bundle_result_hash": result_bundle["result_bundle_hash"],
            "context_hash": result_bundle["context_hash"],
            "source_cognition_artifact_hashes": [cognition_artifact["artifact_hash"]],
            "source_cognition_hashes": [cognition_artifact["cognition_hash"]],
            "provider_identity_hashes": [replay_hash(cognition_artifact["provider_identity"])],
        },
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "non_authoritative": True,
        "human_review_required": True,
        "comparison_created": False,
        "single_provider_primary_mode": True,
        "comparison_performed": False,
        "approval_created": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "replay_visible": True,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["comparison_hash"] = _compute_comparison_compatible_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _single_provider_source_summary(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "cognition_artifact_id": artifact["cognition_artifact_id"],
        "artifact_hash": artifact["artifact_hash"],
        "cognition_hash": artifact["cognition_hash"],
        "provider_id": artifact["provider_identity"]["provider_id"],
        "provider_identity": deepcopy(artifact["provider_identity"]),
        "context_hash": artifact["context_hash"],
        "request_hash": artifact["request_hash"],
        "response_hash": artifact["response_hash"],
        "confidence": artifact["confidence"],
    }


def _comparison_returned_artifact(comparison_artifact: dict[str, Any]) -> dict[str, Any]:
    returned = {
        "artifact_type": COGNITION_COMPARISON_RETURNED_V1,
        "runtime_version": COGNITION_COMPARISON_RUNTIME_VERSION,
        "cognition_comparison_reference": comparison_artifact["cognition_comparison_id"],
        "cognition_comparison_hash": comparison_artifact["artifact_hash"],
        "comparison_hash": comparison_artifact["comparison_hash"],
        "comparison_status": comparison_artifact["comparison_status"],
        "comparison_confidence": comparison_artifact["comparison_confidence"],
        "replay_visible": True,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "approval_created": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _persist_comparison_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "event_type": step.upper(),
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", wrapper)


def _ensure_comparison_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(("cognition_comparison_artifact", "cognition_comparison_returned")):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _compute_comparison_compatible_hash(artifact: dict[str, Any]) -> str:
    return replay_hash(
        {
            "cognition_comparison_id": artifact["cognition_comparison_id"],
            "comparison_status": artifact["comparison_status"],
            "multi_provider_cognition_bundle_id": artifact["multi_provider_cognition_bundle_id"],
            "source_result_bundle_hash": artifact["source_result_bundle_hash"],
            "context_hash": artifact["context_hash"],
            "source_cognition_artifacts": artifact["source_cognition_artifacts"],
            "provider_identities": artifact["provider_identities"],
            "comparison_findings": artifact["comparison_findings"],
            "agreement": artifact["agreement"],
            "disagreement": artifact["disagreement"],
            "conflicting_assumptions": artifact["conflicting_assumptions"],
            "conflicting_risks": artifact["conflicting_risks"],
            "conflicting_alternatives": artifact["conflicting_alternatives"],
            "uncertainty": artifact["uncertainty"],
            "missing_information": artifact["missing_information"],
            "comparison_confidence": artifact["comparison_confidence"],
            "lineage_refs": artifact["lineage_refs"],
            "authority_flags": artifact["authority_flags"],
            "failure_reason": artifact.get("failure_reason"),
        }
    )


def _capture(
    *,
    final_status: str,
    artifact: dict[str, Any],
    returned: dict[str, Any],
    replay_path: Path,
    failure_reason: str,
    stage_captures: dict[str, Any],
) -> dict[str, Any]:
    result = {
        "command": "aigol ocs llm-cognition end-to-end",
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "classification": CERTIFIED_CLASSIFICATION,
        "final_status": final_status,
        "end_to_end_id": artifact.get("end_to_end_id"),
        "ocs_llm_cognition_end_to_end_artifact": deepcopy(artifact),
        "returned_artifact": deepcopy(returned),
        "human_facing_cognition_result": deepcopy(artifact.get("human_facing_cognition_result")),
        "stage_captures": deepcopy(stage_captures),
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "replay_reference": str(replay_path),
        "approval_created": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "fail_closed": final_status != STATUS_COMPLETED,
        "failure_reason": failure_reason,
    }
    result["ocs_llm_cognition_end_to_end_hash"] = replay_hash(result)
    return result


def _compute_end_to_end_hash(artifact: dict[str, Any]) -> str:
    return replay_hash(
        {
            "end_to_end_id": artifact["end_to_end_id"],
            "workflow_status": artifact["workflow_status"],
            "human_question_hash": artifact["human_question_hash"],
            "context_hash": artifact["context_hash"],
            "context_artifact_hash": artifact["context_artifact_hash"],
            "multi_provider_result_bundle_hash": artifact["multi_provider_result_bundle_hash"],
            "provider_request_artifact_hashes": artifact["provider_request_artifact_hashes"],
            "provider_response_artifact_hashes": artifact["provider_response_artifact_hashes"],
            "cognition_artifact_hashes": artifact["cognition_artifact_hashes"],
            "provider_failure_hashes": artifact["provider_failure_hashes"],
            "single_provider_primary_mode": artifact["single_provider_primary_mode"],
            "comparison_required": artifact["comparison_required"],
            "comparison_performed": artifact["comparison_performed"],
            "comparison_artifact_hash": artifact["comparison_artifact_hash"],
            "comparison_hash": artifact["comparison_hash"],
            "history_reference_hash": artifact["history_reference_hash"],
            "history_hash": artifact["history_hash"],
            "continuity_artifact_hash": artifact["continuity_artifact_hash"],
            "continuity_hash": artifact["continuity_hash"],
            "clarification_artifact_hash": artifact["clarification_artifact_hash"],
            "clarification_hash": artifact["clarification_hash"],
            "human_facing_cognition_result": artifact["human_facing_cognition_result"],
            "stage_replay_references": artifact["stage_replay_references"],
            "lineage_refs": artifact["lineage_refs"],
            "authority_flags": artifact["authority_flags"],
            "failure_reason": artifact["failure_reason"],
        }
    )


def _stage_replay_paths(replay_path: Path) -> dict[str, Path]:
    return {
        "context": replay_path / "stages" / "context",
        "multi_provider_cognition": replay_path / "stages" / "multi_provider_cognition",
        "cognition_comparison": replay_path / "stages" / "cognition_comparison",
        "continuity_and_clarification": replay_path / "stages" / "continuity_and_clarification",
    }


def _require_stage_success(capture: dict[str, Any], stage_name: str) -> None:
    if not isinstance(capture, dict) or capture.get("fail_closed") is True:
        reason = capture.get("failure_reason") if isinstance(capture, dict) else ""
        raise FailClosedRuntimeError(f"{stage_name} failed closed: {reason}")


def _validate_context_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("OCS context artifact must be a JSON object")
    if artifact.get("artifact_type") != OCS_CONTEXT_ASSEMBLY_ARTIFACT_V1:
        raise FailClosedRuntimeError("invalid OCS context artifact")
    if artifact.get("context_status") != OCS_CONTEXT_ASSEMBLED:
        raise FailClosedRuntimeError("OCS context must be assembled")
    _verify_artifact_hash(artifact, "OCS context artifact")
    _reject_boundary_flags(artifact, "OCS context artifact")
    return deepcopy(artifact)


def _validate_result_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(bundle, dict):
        raise FailClosedRuntimeError("multi-provider cognition result bundle must be a JSON object")
    if bundle.get("artifact_type") != MULTI_PROVIDER_COGNITION_RESULT_BUNDLE_V1:
        raise FailClosedRuntimeError("invalid multi-provider cognition result bundle")
    if bundle.get("bundle_status") != STATUS_COMPLETED:
        raise FailClosedRuntimeError("multi-provider cognition result bundle must be completed")
    _verify_artifact_hash(bundle, "multi-provider cognition result bundle")
    _reject_boundary_flags(bundle, "multi-provider cognition result bundle")
    return deepcopy(bundle)


def _validate_comparison_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("cognition comparison artifact must be a JSON object")
    if artifact.get("artifact_type") != COGNITION_COMPARISON_ARTIFACT_V1:
        raise FailClosedRuntimeError("invalid cognition comparison artifact")
    if artifact.get("comparison_status") != STATUS_COMPLETED:
        raise FailClosedRuntimeError("cognition comparison artifact must be completed")
    _verify_artifact_hash(artifact, "cognition comparison artifact")
    _reject_boundary_flags(artifact, "cognition comparison artifact")
    return deepcopy(artifact)


def _verify_stage_hashes(
    artifact: dict[str, Any],
    context_replay: dict[str, Any],
    multi_replay: dict[str, Any],
    comparison_replay: dict[str, Any],
    continuity_replay: dict[str, Any],
) -> None:
    if context_replay.get("context_hash") != artifact["context_hash"]:
        raise FailClosedRuntimeError("end-to-end context replay hash mismatch")
    if multi_replay.get("context_hash") != artifact["context_hash"]:
        raise FailClosedRuntimeError("end-to-end multi-provider context hash mismatch")
    if multi_replay.get("cognition_artifact_hashes") != artifact["cognition_artifact_hashes"]:
        raise FailClosedRuntimeError("end-to-end cognition artifact hash mismatch")
    if comparison_replay.get("context_hash") != artifact["context_hash"]:
        raise FailClosedRuntimeError("end-to-end comparison context hash mismatch")
    if comparison_replay.get("comparison_confidence") != artifact["human_facing_cognition_result"]["comparison_confidence"]:
        raise FailClosedRuntimeError("end-to-end comparison confidence mismatch")
    if continuity_replay.get("clarification_required") != artifact["human_facing_cognition_result"]["clarification_required"]:
        raise FailClosedRuntimeError("end-to-end clarification requirement mismatch")
    if (
        continuity_replay.get("clarification_candidate_count")
        != artifact["human_facing_cognition_result"]["clarification_candidate_count"]
    ):
        raise FailClosedRuntimeError("end-to-end clarification candidate count mismatch")


def _reject_boundary_flags(artifact: dict[str, Any], label: str) -> None:
    if artifact.get("approval_created") is True:
        raise FailClosedRuntimeError(f"{label} created approval")
    if artifact.get("worker_invoked") is True:
        raise FailClosedRuntimeError(f"{label} invoked worker")
    if artifact.get("execution_requested") is True:
        raise FailClosedRuntimeError(f"{label} requested execution")
    if artifact.get("governance_modified") is True:
        raise FailClosedRuntimeError(f"{label} modified governance")
    if artifact.get("replay_modified") is True:
        raise FailClosedRuntimeError(f"{label} modified replay")
    flags = artifact.get("authority_flags")
    if isinstance(flags, dict) and any(value is not False for value in flags.values()):
        raise FailClosedRuntimeError(f"{label} contains authority")


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("OCS LLM cognition end-to-end replay artifact already exists")


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(
        {
            "replay_index": wrapper["replay_index"],
            "replay_step": wrapper["replay_step"],
            "artifact": wrapper["artifact"],
        }
    )
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    try:
        _persist_step(replay_path, index, step, artifact)
    except Exception:
        return


def _verify_replay_wrapper_hash(wrapper: dict[str, Any]) -> None:
    expected = replay_hash(
        {
            "replay_index": wrapper.get("replay_index"),
            "replay_step": wrapper.get("replay_step"),
            "artifact": wrapper.get("artifact"),
        }
    )
    if wrapper.get("replay_hash") != expected:
        raise FailClosedRuntimeError("OCS LLM cognition end-to-end replay hash mismatch")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    provided = artifact.get("artifact_hash")
    if not isinstance(provided, str) or not provided:
        raise FailClosedRuntimeError(f"{label} artifact hash missing")
    comparable = deepcopy(artifact)
    comparable.pop("artifact_hash", None)
    if replay_hash(comparable) != provided:
        raise FailClosedRuntimeError(f"{label} artifact hash mismatch")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field} is required")
    return value.strip()


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
