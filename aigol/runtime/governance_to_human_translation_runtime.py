"""Deterministic Governance -> Human translation runtime."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_communication_wrapper_wiring import wire_transparency_wrapper_to_uhcl
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.universal_translation_artifact_schema import (
    GOVERNANCE_ONLY,
    GOVERNANCE_TO_HUMAN,
    MATERIAL_AMBIGUITY,
    NO_AMBIGUITY,
    create_universal_translation_artifact,
    validate_universal_translation_artifact,
)


RUNTIME_VERSION = "GOVERNANCE_TO_HUMAN_TRANSLATION_RUNTIME_V1"
REPLAY_STEP = "governance_to_human_translation_recorded"

STATUS_NOT_PROVIDED = "NOT_PROVIDED"
STATUS_PENDING_APPROVAL = "PENDING_APPROVAL"
STATUS_APPROVED = "APPROVED"
STATUS_REJECTED = "REJECTED"
STATUS_MODIFICATION_REQUESTED = "MODIFICATION_REQUESTED"
STATUS_EXECUTED = "EXECUTED"
STATUS_NOT_EXECUTED = "NOT_EXECUTED"
STATUS_PASSED = "PASSED"
STATUS_FAILED = "FAILED"
STATUS_UNKNOWN = "UNKNOWN"


def translate_governance_to_human(
    *,
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
    operator_context: str = "HUMAN_OPERATOR",
) -> dict[str, Any]:
    """Translate authoritative governance state into a human-readable artifact."""

    replay_path = Path(replay_dir)
    governance = _require_nonempty_mapping(governance_state, "governance_state")
    replay = _require_nonempty_mapping(replay_evidence, "replay_evidence")
    proposal = _optional_mapping(proposal_state, "proposal_state")
    approval = _optional_mapping(approval_state, "approval_state")
    worker = _optional_mapping(worker_results, "worker_results")
    validation = _optional_mapping(validation_results, "validation_results")
    err = _optional_mapping(err_evidence, "err_evidence")

    references = _authoritative_references(
        governance_state=governance,
        replay_evidence=replay,
        proposal_state=proposal,
        approval_state=approval,
        worker_results=worker,
        validation_results=validation,
        err_evidence=err,
    )
    ambiguity = _detect_ambiguity(governance, replay, approval)
    human_payload = _human_readable_payload(
        governance_state=governance,
        replay_evidence=replay,
        proposal_state=proposal,
        approval_state=approval,
        worker_results=worker,
        validation_results=validation,
        err_evidence=err,
        authoritative_references=references,
        ambiguity_flags=ambiguity,
    )
    normalized_intent = {
        "translation_runtime": RUNTIME_VERSION,
        "intent_family": _string_or_unknown(governance.get("intent_family")),
        "workflow": _string_or_unknown(governance.get("workflow") or governance.get("workflow_id")),
        "workflow_state": _string_or_unknown(governance.get("workflow_state") or governance.get("state")),
        "approval_required": bool(governance.get("approval_required", False)),
        "operator_action_required": human_payload["operator_action_required"],
    }
    artifact = create_universal_translation_artifact(
        translation_id=f"{translation_request_id}:GOVERNANCE-TO-HUMAN",
        translation_request={
            "translation_request_id": _require_string(translation_request_id, "translation_request_id"),
            "operator_context": _require_string(operator_context, "operator_context"),
            "created_at": _require_string(created_at, "created_at"),
        },
        source_direction=GOVERNANCE_TO_HUMAN,
        source_payload={
            "governance_state": deepcopy(governance),
            "replay_evidence": deepcopy(replay),
            "proposal_state": deepcopy(proposal),
            "approval_state": deepcopy(approval),
            "worker_results": deepcopy(worker),
            "validation_results": deepcopy(validation),
            "err_evidence": deepcopy(err),
            "authoritative_references": deepcopy(references),
        },
        normalized_intent=normalized_intent,
        human_readable_payload=human_payload,
        ambiguity_flags=ambiguity,
        confidence=GOVERNANCE_ONLY,
        provider_metadata={
            "provider_used": False,
            "provider_count": 0,
            "providers": [],
            "comparison_used": False,
        },
        deterministic_fallback_status={
            "fallback_used": True,
            "fallback_reason": "DETERMINISTIC_GOVERNANCE_TO_HUMAN_TRANSLATION_RUNTIME",
            "deterministic_rule_ids": _rule_ids_for(governance, approval, worker, validation, err),
        },
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
    uhcl_wrapper_wiring = wire_transparency_wrapper_to_uhcl(
        wrapper_surface="GOVERNANCE_TO_HUMAN_TRANSLATION_RUNTIME",
        wrapper_id=translation_request_id,
        transparency_content={
            "translation_id": artifact["translation_id"],
            "rendered_explanation_hash": replay_hash(human_payload["rendered_explanation"]),
            "operator_action_required": human_payload["operator_action_required"],
            "ambiguity_flags": deepcopy(ambiguity),
        },
        evidence_references=[
            {
                "evidence_reference": "governance_state",
                "evidence_hash": references["governance_state_hash"],
            },
            {
                "evidence_reference": "replay_evidence",
                "evidence_hash": references["replay_evidence_hash"],
            },
            {
                "evidence_reference": artifact["translation_id"],
                "evidence_hash": artifact["artifact_hash"],
            },
        ],
        created_at=created_at,
        replay_dir=replay_path / "uhcl_wrapper_wiring",
        rollback_reference=f"rollback:{translation_request_id}:uhcl-wrapper-wiring",
    )
    return {
        "runtime_version": RUNTIME_VERSION,
        "translation_status": "TRANSLATED",
        "translation_artifact": deepcopy(artifact),
        "translation_replay_reference": str(replay_path),
        "human_readable_payload": deepcopy(human_payload),
        "rendered_explanation": human_payload["rendered_explanation"],
        "ambiguity_flags": deepcopy(ambiguity),
        "confidence": GOVERNANCE_ONLY,
        "provider_invoked": False,
        "workflow_executed": False,
        "governance_mutated": False,
        "approval_granted": False,
        "uhcl_wrapper_wiring": uhcl_wrapper_wiring,
        "replay_visible": True,
    }


def reconstruct_governance_to_human_translation_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct deterministic Governance -> Human translation replay evidence."""

    replay_path = Path(replay_dir)
    wrapper = load_json(replay_path / f"000_{REPLAY_STEP}.json")
    if wrapper.get("replay_index") != 0 or wrapper.get("replay_step") != REPLAY_STEP:
        raise FailClosedRuntimeError("governance-to-human translation replay ordering mismatch")
    _verify_wrapper_hash(wrapper)
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("governance-to-human translation artifact must be a JSON object")
    validated = validate_universal_translation_artifact(artifact)
    if validated["source_direction"] != GOVERNANCE_TO_HUMAN:
        raise FailClosedRuntimeError("governance-to-human translation replay direction mismatch")
    human_payload = validated["human_readable_payload"]
    uhcl_wrapper_wiring = _load_optional_uhcl_wrapper_wiring(replay_path)
    return {
        "runtime_version": RUNTIME_VERSION,
        "translation_id": validated["translation_id"],
        "translation_artifact": deepcopy(validated),
        "human_readable_payload": deepcopy(human_payload),
        "rendered_explanation": human_payload["rendered_explanation"],
        "normalized_intent": deepcopy(validated["normalized_intent"]),
        "ambiguity_flags": deepcopy(validated["ambiguity_flags"]),
        "confidence": validated["confidence"],
        "artifact_hash": validated["artifact_hash"],
        "replay_hash": wrapper["replay_hash"],
        "provider_invoked": False,
        "workflow_executed": False,
        "governance_mutated": False,
        "approval_granted": False,
        "uhcl_wrapper_wiring": deepcopy(uhcl_wrapper_wiring),
        "replay_visible": True,
    }


def _load_optional_uhcl_wrapper_wiring(replay_path: Path) -> dict[str, Any] | None:
    wrapper_path = (
        replay_path
        / "uhcl_wrapper_wiring"
        / "000_uhcl_typed_communication_section_recorded.json"
    )
    if not wrapper_path.exists():
        return None
    wrapper = load_json(wrapper_path)
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("governance-to-human UHCL wrapper wiring artifact must be a JSON object")
    return {
        "wiring_version": "G3_04_PHASE_8B_PLATFORM_COMMUNICATION_WRAPPER_WIRING_V1",
        "wrapper_surface": "GOVERNANCE_TO_HUMAN_TRANSLATION_RUNTIME",
        "uhcl_consumed": True,
        "uhcl_artifact_type": artifact.get("artifact_type"),
        "uhcl_artifact_hash": artifact.get("artifact_hash"),
        "uhcl_replay_reference": str(wrapper_path.parent),
        "legacy_contract_preserved": True,
        "new_communication_semantics_introduced": False,
    }


def _human_readable_payload(
    *,
    governance_state: dict[str, Any],
    replay_evidence: dict[str, Any],
    proposal_state: dict[str, Any],
    approval_state: dict[str, Any],
    worker_results: dict[str, Any],
    validation_results: dict[str, Any],
    err_evidence: dict[str, Any],
    authoritative_references: dict[str, Any],
    ambiguity_flags: dict[str, Any],
) -> dict[str, Any]:
    proposal_summary = _proposal_summary(proposal_state)
    approval_summary = _approval_summary(governance_state, approval_state)
    worker_summary = _worker_summary(worker_results)
    validation_summary = _validation_summary(validation_results)
    replay_summary = _replay_summary(replay_evidence)
    err_summary = _err_summary(err_evidence)
    sections = {
        "SUMMARY": [
            _governance_summary(governance_state),
            proposal_summary,
        ],
        "APPROVAL": [approval_summary],
        "EXECUTION": [worker_summary],
        "VALIDATION": [validation_summary],
        "REPLAY": [replay_summary],
        "ERR": [err_summary],
        "WHAT TO DO NEXT": [_next_action(governance_state, approval_state, ambiguity_flags)],
    }
    return {
        "summary": _governance_summary(governance_state),
        "governance_decision_summary": _decision_summary(governance_state),
        "proposal_summary": proposal_summary,
        "approval_explanation": approval_summary,
        "worker_execution_status": worker_summary,
        "validation_summary": validation_summary,
        "replay_summary": replay_summary,
        "err_summary": err_summary,
        "operator_action_required": _next_action(governance_state, approval_state, ambiguity_flags),
        "authoritative_state_references": deepcopy(authoritative_references),
        "ambiguity_explanation": _ambiguity_explanation(ambiguity_flags),
        "sections": sections,
        "rendered_explanation": _render_sections(sections),
        "non_authoritative_notice": "This translation explains governance state. It does not approve or execute anything.",
    }


def _authoritative_references(
    *,
    governance_state: dict[str, Any],
    replay_evidence: dict[str, Any],
    proposal_state: dict[str, Any],
    approval_state: dict[str, Any],
    worker_results: dict[str, Any],
    validation_results: dict[str, Any],
    err_evidence: dict[str, Any],
) -> dict[str, Any]:
    return {
        "governance_state_hash": replay_hash(governance_state),
        "replay_evidence_hash": replay_hash(replay_evidence),
        "proposal_state_hash": replay_hash(proposal_state) if proposal_state else None,
        "approval_state_hash": replay_hash(approval_state) if approval_state else None,
        "worker_results_hash": replay_hash(worker_results) if worker_results else None,
        "validation_results_hash": replay_hash(validation_results) if validation_results else None,
        "err_evidence_hash": replay_hash(err_evidence) if err_evidence else None,
        "replay_reference": _first_string(
            replay_evidence.get("replay_reference"),
            replay_evidence.get("path"),
            replay_evidence.get("replay_path"),
        ),
        "proposal_reference": _first_string(
            proposal_state.get("proposal_id"),
            proposal_state.get("artifact_identifier"),
            proposal_state.get("proposal_hash"),
        ),
        "approval_reference": _first_string(
            approval_state.get("approval_id"),
            approval_state.get("approval_hash"),
            approval_state.get("state"),
        ),
        "err_reference": _first_string(
            err_evidence.get("err_id"),
            err_evidence.get("evidence_id"),
            err_evidence.get("artifact_hash"),
        ),
    }


def _detect_ambiguity(
    governance_state: dict[str, Any],
    replay_evidence: dict[str, Any],
    approval_state: dict[str, Any],
) -> dict[str, Any]:
    questions: list[str] = []
    status = NO_AMBIGUITY
    if bool(governance_state.get("approval_required", False)) and not approval_state:
        status = MATERIAL_AMBIGUITY
        questions.append("Approval is required, but no approval state was provided.")
    if not _first_string(replay_evidence.get("replay_reference"), replay_evidence.get("path"), replay_evidence.get("replay_path")):
        status = MATERIAL_AMBIGUITY
        questions.append("Replay evidence exists, but no replay reference was provided.")
    return {
        "ambiguity_status": status,
        "clarification_required": status != NO_AMBIGUITY,
        "clarification_questions": questions,
    }


def _governance_summary(governance_state: dict[str, Any]) -> str:
    workflow = _string_or_unknown(governance_state.get("workflow") or governance_state.get("workflow_id"))
    state = _string_or_unknown(governance_state.get("workflow_state") or governance_state.get("state"))
    return f"ACLI is in workflow {workflow} with state {state}."


def _decision_summary(governance_state: dict[str, Any]) -> str:
    decision = _string_or_unknown(governance_state.get("decision") or governance_state.get("governance_decision"))
    return f"Governance decision: {decision}."


def _proposal_summary(proposal_state: dict[str, Any]) -> str:
    if not proposal_state:
        return "No proposal state was provided."
    identifier = _first_string(
        proposal_state.get("artifact_identifier"),
        proposal_state.get("proposal_id"),
        proposal_state.get("name"),
    )
    targets = proposal_state.get("target_paths") or proposal_state.get("targets") or []
    if not isinstance(targets, list):
        targets = []
    target_text = ", ".join(str(item) for item in targets) if targets else "no target paths listed"
    return f"Proposal {identifier or STATUS_UNKNOWN} affects {target_text}."


def _approval_summary(governance_state: dict[str, Any], approval_state: dict[str, Any]) -> str:
    if not bool(governance_state.get("approval_required", False)):
        return "Approval is not required by the current governance state."
    if not approval_state:
        return "Approval is required, but no approval decision has been recorded."
    status = _string_or_unknown(approval_state.get("approval_status") or approval_state.get("state"))
    if status in {STATUS_APPROVED, "APPROVE", "APPROVED_BY_HUMAN"}:
        return "A human approval decision is recorded."
    if status in {STATUS_REJECTED, "REJECT"}:
        return "The proposal was rejected. No execution should occur."
    if status in {STATUS_MODIFICATION_REQUESTED, "REQUEST_MODIFICATION"}:
        return "A modification was requested. The current proposal should not execute."
    return f"Approval state is {status}."


def _worker_summary(worker_results: dict[str, Any]) -> str:
    if not worker_results:
        return "No worker execution result was provided."
    status = _string_or_unknown(worker_results.get("execution_status") or worker_results.get("status"))
    if status in {STATUS_EXECUTED, "SUCCESS", "COMPLETED"}:
        return "Worker execution is recorded as completed."
    if status in {STATUS_NOT_EXECUTED, "SKIPPED"}:
        return "No worker execution occurred."
    return f"Worker execution status is {status}."


def _validation_summary(validation_results: dict[str, Any]) -> str:
    if not validation_results:
        return "No validation result was provided."
    status = _string_or_unknown(validation_results.get("validation_status") or validation_results.get("status"))
    if status in {STATUS_PASSED, "PASS", "SUCCESS"}:
        return "Validation passed."
    if status in {STATUS_FAILED, "FAIL", "FAILED"}:
        return "Validation failed."
    return f"Validation status is {status}."


def _replay_summary(replay_evidence: dict[str, Any]) -> str:
    reference = _first_string(
        replay_evidence.get("replay_reference"),
        replay_evidence.get("path"),
        replay_evidence.get("replay_path"),
    )
    status = _string_or_unknown(replay_evidence.get("replay_status") or replay_evidence.get("status"))
    if reference:
        return f"Replay evidence is recorded at {reference} with status {status}."
    return f"Replay evidence was provided with status {status}, but no replay path was supplied."


def _err_summary(err_evidence: dict[str, Any]) -> str:
    if not err_evidence:
        return "No ERR evidence was provided."
    status = _string_or_unknown(err_evidence.get("err_status") or err_evidence.get("status"))
    reference = _first_string(err_evidence.get("err_id"), err_evidence.get("evidence_id"))
    if reference:
        return f"ERR evidence {reference} has status {status}."
    return f"ERR evidence status is {status}."


def _next_action(
    governance_state: dict[str, Any],
    approval_state: dict[str, Any],
    ambiguity_flags: dict[str, Any],
) -> str:
    if ambiguity_flags["clarification_required"]:
        return "Review the missing or unclear governance evidence before continuing."
    if bool(governance_state.get("approval_required", False)) and not approval_state:
        return "Review the proposal and provide an approval decision."
    status = _string_or_unknown(approval_state.get("approval_status") or approval_state.get("state")) if approval_state else ""
    if status in {STATUS_REJECTED, "REJECT", STATUS_MODIFICATION_REQUESTED, "REQUEST_MODIFICATION"}:
        return "No execution should occur for the current proposal."
    return "Review the replay evidence for audit continuity."


def _ambiguity_explanation(ambiguity_flags: dict[str, Any]) -> str:
    if not ambiguity_flags["clarification_required"]:
        return "No material ambiguity was detected in the provided governance state."
    return " ".join(ambiguity_flags["clarification_questions"])


def _render_sections(sections: dict[str, list[str]]) -> str:
    lines = ["GOVERNANCE STATE EXPLANATION"]
    for heading in ("SUMMARY", "APPROVAL", "EXECUTION", "VALIDATION", "REPLAY", "ERR", "WHAT TO DO NEXT"):
        body = sections.get(heading)
        if not isinstance(body, list) or not body:
            raise FailClosedRuntimeError(f"governance-to-human translation section missing: {heading}")
        lines.extend(["", heading])
        lines.extend(f"- {item}" for item in body)
    return "\n".join(lines)


def _rule_ids_for(
    governance_state: dict[str, Any],
    approval_state: dict[str, Any],
    worker_results: dict[str, Any],
    validation_results: dict[str, Any],
    err_evidence: dict[str, Any],
) -> list[str]:
    rule_ids = [
        "GOVERNANCE_STATE_SUMMARY_V1",
        "REPLAY_EVIDENCE_SUMMARY_V1",
        "AUTHORITY_REFERENCE_HASHING_V1",
    ]
    if governance_state.get("approval_required") is not None:
        rule_ids.append("APPROVAL_REQUIREMENT_EXPLANATION_V1")
    if approval_state:
        rule_ids.append("APPROVAL_STATE_EXPLANATION_V1")
    if worker_results:
        rule_ids.append("WORKER_RESULT_EXPLANATION_V1")
    if validation_results:
        rule_ids.append("VALIDATION_RESULT_EXPLANATION_V1")
    if err_evidence:
        rule_ids.append("ERR_EVIDENCE_EXPLANATION_V1")
    return rule_ids


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash", None)
    if not isinstance(actual, str) or replay_hash(expected) != actual:
        raise FailClosedRuntimeError("governance-to-human translation replay hash mismatch")


def _require_nonempty_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict) or not value:
        raise FailClosedRuntimeError(f"{field_name} must be a non-empty JSON object")
    return deepcopy(value)


def _optional_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"{field_name} must be a JSON object")
    return deepcopy(value)


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _string_or_unknown(value: Any) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return STATUS_UNKNOWN


def _first_string(*values: Any) -> str | None:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None
