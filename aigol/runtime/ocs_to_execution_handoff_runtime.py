"""Replay-visible OCS-to-execution handoff runtime."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.ocs_llm_cognition_end_to_end_runtime import (
    OCS_LLM_COGNITION_END_TO_END_ARTIFACT_V1,
    STATUS_COMPLETED as OCS_STATUS_COMPLETED,
    reconstruct_ocs_llm_cognition_end_to_end_replay,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_OCS_TO_EXECUTION_HANDOFF_RUNTIME_V1"
OCS_EXECUTION_HANDOFF_ARTIFACT_V1 = "OCS_EXECUTION_HANDOFF_ARTIFACT_V1"
OCS_EXECUTION_HANDOFF_RETURNED_V1 = "OCS_EXECUTION_HANDOFF_RETURNED_V1"
EXECUTION_HANDOFF_CANDIDATE = "EXECUTION_HANDOFF_CANDIDATE"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "ocs_execution_handoff_recorded",
    "ocs_execution_handoff_returned",
)

AUTHORITY_FLAGS = {
    "provider_authority": False,
    "ocs_authority": False,
    "approval_authority": False,
    "execution_authority": False,
    "worker_authority": False,
    "governance_authority": False,
    "replay_authority": False,
}

DOWNSTREAM_EXPECTED_ARTIFACT_REFS = (
    "EXECUTION_READY_STATUS_ARTIFACT_V1",
    "EXECUTION_AUTHORIZATION_ARTIFACT_V1",
    "WORKER_INVOCATION_REQUEST_ARTIFACT_V1",
    "WORKER_ASSIGNMENT_ARTIFACT_V1",
    "WORKER_DISPATCH_ARTIFACT_V1",
    "WORKER_INVOCATION_ARTIFACT_V1",
    "WORKER_RESULT_CAPTURE_ARTIFACT_V1",
    "WORKER_RESULT_VALIDATION_ARTIFACT_V1",
    "POST_EXECUTION_REPLAY_REVIEW_ARTIFACT_V1",
    "GOVERNED_TERMINATION_ARTIFACT_V1",
)

DEFAULT_REQUIRED_VALIDATION = (
    "OCS_COGNITION_LINEAGE",
    "NORMALIZED_COGNITION_PRESENT",
    "BOUNDED_EXECUTION_INTENT",
    "ALLOWED_OUTPUTS_EXPLICIT",
    "FORBIDDEN_OPERATIONS_EXPLICIT",
    "HUMAN_APPROVAL_BINDING",
    "WORKER_ROLE_CONSTRAINTS",
    "REPLAY_LINEAGE_CONTINUITY",
    "AUTHORITY_BOUNDARIES",
    "HASH_INTEGRITY",
)


def create_ocs_execution_handoff(
    *,
    handoff_id: str,
    ocs_cognition_replay_reference: str,
    execution_intake_id: str,
    execution_intent_summary: str,
    execution_candidate_scope: dict[str, Any],
    requested_outcomes: list[str],
    non_goals: list[str],
    allowed_outputs: list[str],
    forbidden_operations: list[str],
    worker_role_requirements: list[str],
    target_worker_family: str,
    candidate_worker_constraints: dict[str, Any],
    worker_capability_requirements: list[str],
    worker_exclusion_rules: list[str],
    worker_registry_requirements: list[str],
    created_at: str,
    replay_dir: str | Path,
    required_validation: list[str] | None = None,
    source_chain_id: str | None = None,
) -> dict[str, Any]:
    """Create a non-authoritative OCS execution handoff candidate."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        ocs_lineage = _load_ocs_cognition_lineage(Path(_require_string(ocs_cognition_replay_reference, "ocs_cognition_replay_reference")))
        artifact = _handoff_artifact(
            handoff_id=handoff_id,
            ocs_cognition_replay_reference=ocs_cognition_replay_reference,
            ocs_lineage=ocs_lineage,
            execution_intake_id=execution_intake_id,
            execution_intent_summary=execution_intent_summary,
            execution_candidate_scope=execution_candidate_scope,
            requested_outcomes=requested_outcomes,
            non_goals=non_goals,
            allowed_outputs=allowed_outputs,
            forbidden_operations=forbidden_operations,
            required_validation=required_validation or list(DEFAULT_REQUIRED_VALIDATION),
            worker_role_requirements=worker_role_requirements,
            target_worker_family=target_worker_family,
            candidate_worker_constraints=candidate_worker_constraints,
            worker_capability_requirements=worker_capability_requirements,
            worker_exclusion_rules=worker_exclusion_rules,
            worker_registry_requirements=worker_registry_requirements,
            created_at=created_at,
            source_chain_id=source_chain_id,
            status=EXECUTION_HANDOFF_CANDIDATE,
            failure_reason="",
        )
        returned = _returned_artifact(artifact, created_at=created_at)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, replay_path)
    except Exception as exc:
        artifact = _failed_handoff_artifact(
            handoff_id=handoff_id,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(artifact, created_at=created_at)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, replay_path)


def reconstruct_ocs_execution_handoff_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct OCS execution handoff replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("OCS execution handoff replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("OCS execution handoff replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "OCS execution handoff replay artifact")
        wrappers.append(wrapper)
    handoff = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("handoff_artifact_hash") != handoff["artifact_hash"]:
        raise FailClosedRuntimeError("OCS execution handoff returned lineage mismatch")
    if handoff.get("handoff_hash") != _handoff_hash(handoff):
        raise FailClosedRuntimeError("OCS execution handoff hash mismatch")
    if handoff.get("handoff_status") == EXECUTION_HANDOFF_CANDIDATE:
        _load_ocs_cognition_lineage(Path(handoff["ocs_cognition_replay_reference"]))
        _validate_handoff_authority(handoff)
    return {
        "handoff_id": handoff.get("handoff_id"),
        "handoff_status": handoff.get("handoff_status"),
        "chain_id": handoff.get("chain_id"),
        "execution_intake_id": handoff.get("execution_intake_id"),
        "ocs_cognition_reference": handoff.get("ocs_cognition_reference"),
        "approval_status": handoff.get("approval_status"),
        "worker_selection_status": handoff.get("worker_selection_status"),
        "execution_readiness_status": handoff.get("execution_readiness_status"),
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
        "provider_authority": False,
        "ocs_authority": False,
        "approval_authority": False,
        "execution_authority": False,
        "worker_authority": False,
        "governance_authority": False,
        "replay_authority": False,
        "authorization_created": False,
        "worker_request_created": False,
        "worker_assigned": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "execution_started": False,
        "repair_started": False,
        "retry_started": False,
        "failure_reason": handoff.get("failure_reason", ""),
    }


def render_ocs_execution_handoff_summary(capture: dict[str, Any]) -> str:
    """Render a compact operator summary."""

    lines = [
        "OCS Execution Handoff",
        f"Handoff Status: {capture.get('handoff_status')}",
        f"Handoff Reference: {capture.get('handoff_reference')}",
        f"Execution Intake: {capture.get('execution_intake_id')}",
        f"Replay Reference: {capture.get('ocs_execution_handoff_replay_reference')}",
        "No approval, authorization, Worker request, dispatch, invocation, execution, repair, or retry was created.",
    ]
    if capture.get("failure_reason"):
        lines.append(f"failure_reason: {capture['failure_reason']}")
    return "\n".join(lines)


def _load_ocs_cognition_lineage(replay_path: Path) -> dict[str, Any]:
    reconstructed = reconstruct_ocs_llm_cognition_end_to_end_replay(replay_path)
    if reconstructed.get("final_status") != OCS_STATUS_COMPLETED:
        raise FailClosedRuntimeError("OCS execution handoff failed closed: OCS cognition is not completed")
    wrapper = load_json(replay_path / "000_ocs_llm_cognition_end_to_end_artifact.json")
    _verify_wrapper_hash(wrapper)
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("OCS execution handoff failed closed: OCS artifact missing")
    _verify_artifact_hash(artifact, "OCS cognition end-to-end artifact")
    if artifact.get("artifact_type") != OCS_LLM_COGNITION_END_TO_END_ARTIFACT_V1:
        raise FailClosedRuntimeError("OCS execution handoff failed closed: invalid OCS artifact")
    if artifact.get("workflow_status") != OCS_STATUS_COMPLETED:
        raise FailClosedRuntimeError("OCS execution handoff failed closed: OCS cognition is not completed")
    _validate_ocs_authority(artifact)
    human_result = artifact.get("human_facing_cognition_result")
    if not isinstance(human_result, dict):
        raise FailClosedRuntimeError("OCS execution handoff failed closed: normalized cognition missing")
    if not _string_list(human_result.get("findings")):
        raise FailClosedRuntimeError("OCS execution handoff failed closed: normalized cognition missing")
    return {
        "artifact": deepcopy(artifact),
        "reconstructed": deepcopy(reconstructed),
        "human_result": deepcopy(human_result),
    }


def _handoff_artifact(
    *,
    handoff_id: str,
    ocs_cognition_replay_reference: str,
    ocs_lineage: dict[str, Any],
    execution_intake_id: str,
    execution_intent_summary: str,
    execution_candidate_scope: dict[str, Any],
    requested_outcomes: list[str],
    non_goals: list[str],
    allowed_outputs: list[str],
    forbidden_operations: list[str],
    required_validation: list[str],
    worker_role_requirements: list[str],
    target_worker_family: str,
    candidate_worker_constraints: dict[str, Any],
    worker_capability_requirements: list[str],
    worker_exclusion_rules: list[str],
    worker_registry_requirements: list[str],
    created_at: str,
    source_chain_id: str | None,
    status: str,
    failure_reason: str,
) -> dict[str, Any]:
    ocs_artifact = ocs_lineage["artifact"]
    human_result = ocs_lineage["human_result"]
    _validate_execution_intake(
        execution_candidate_scope=execution_candidate_scope,
        requested_outcomes=requested_outcomes,
        non_goals=non_goals,
        allowed_outputs=allowed_outputs,
        forbidden_operations=forbidden_operations,
        required_validation=required_validation,
        worker_role_requirements=worker_role_requirements,
        target_worker_family=target_worker_family,
        candidate_worker_constraints=candidate_worker_constraints,
        worker_capability_requirements=worker_capability_requirements,
        worker_exclusion_rules=worker_exclusion_rules,
        worker_registry_requirements=worker_registry_requirements,
    )
    chain_id = source_chain_id or ocs_artifact.get("end_to_end_id")
    artifact = {
        "artifact_type": OCS_EXECUTION_HANDOFF_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "contract_reference": "AIGOL_OCS_TO_EXECUTION_HANDOFF_CONTRACT_V1",
        "artifact_version": 1,
        "handoff_id": _require_string(handoff_id, "handoff_id"),
        "chain_id": _require_string(chain_id, "chain_id"),
        "created_at": _require_string(created_at, "created_at"),
        "handoff_status": status,
        "ocs_cognition_reference": ocs_artifact["end_to_end_id"],
        "ocs_cognition_hash": ocs_artifact["artifact_hash"],
        "ocs_cognition_replay_reference": _require_string(
            ocs_cognition_replay_reference, "ocs_cognition_replay_reference"
        ),
        "human_prompt_hash": ocs_artifact["human_question_hash"],
        "human_facing_cognition_hash": replay_hash(human_result),
        "findings_hash": replay_hash(human_result.get("findings", [])),
        "assumptions_hash": replay_hash(human_result.get("assumptions", [])),
        "risks_hash": replay_hash(human_result.get("risks", [])),
        "uncertainties_hash": replay_hash(human_result.get("uncertainties", [])),
        "clarification_questions_hash": replay_hash(human_result.get("clarification_questions", [])),
        "recommended_next_milestone_hash": replay_hash(human_result.get("recommended_next_milestone", "")),
        "execution_intake_id": _require_string(execution_intake_id, "execution_intake_id"),
        "execution_intent_summary": _require_string(execution_intent_summary, "execution_intent_summary"),
        "execution_candidate_scope": deepcopy(execution_candidate_scope),
        "requested_outcomes": _string_list_required(requested_outcomes, "requested_outcomes"),
        "non_goals": _string_list_required(non_goals, "non_goals"),
        "allowed_outputs": _string_list_required(allowed_outputs, "allowed_outputs"),
        "forbidden_operations": _string_list_required(forbidden_operations, "forbidden_operations"),
        "required_validation": _string_list_required(required_validation, "required_validation"),
        "execution_readiness_requirements": list(DEFAULT_REQUIRED_VALIDATION),
        "human_review_required": True,
        **deepcopy(AUTHORITY_FLAGS),
        "authorization_created": False,
        "worker_request_created": False,
        "worker_assigned": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "execution_started": False,
        "repair_started": False,
        "retry_started": False,
        "approval_required": True,
        "approval_status": "PENDING_HUMAN_REVIEW",
        "approval_reference": None,
        "approval_hash": None,
        "approval_scope_requirements": {
            "must_bind_handoff_id": _require_string(handoff_id, "handoff_id"),
            "may_not_broaden_allowed_outputs": True,
            "may_not_weaken_forbidden_operations": True,
            "must_preserve_required_validation": True,
        },
        "approval_expiry_requirements": {
            "expiry_required_for_runtime_authorization": True,
            "expired_approval_fails_closed": True,
        },
        "approval_revocation_requirements": {
            "revoked_approval_fails_closed": True,
            "revocation_must_be_replay_visible": True,
        },
        "approval_actor_requirements": {
            "human_actor_required": True,
            "provider_actor_forbidden": True,
            "ocs_actor_forbidden": True,
        },
        "worker_selection_required": True,
        "worker_role_requirements": _string_list_required(worker_role_requirements, "worker_role_requirements"),
        "target_worker_family": _require_string(target_worker_family, "target_worker_family"),
        "candidate_worker_constraints": deepcopy(candidate_worker_constraints),
        "worker_capability_requirements": _string_list_required(
            worker_capability_requirements, "worker_capability_requirements"
        ),
        "worker_exclusion_rules": _string_list_required(worker_exclusion_rules, "worker_exclusion_rules"),
        "worker_registry_requirements": _string_list_required(worker_registry_requirements, "worker_registry_requirements"),
        "worker_selection_status": "NOT_SELECTED",
        "worker_reference": None,
        "worker_hash": None,
        "replay_root_reference": str(Path(ocs_cognition_replay_reference).parent),
        "ocs_stage_replay_references": deepcopy(ocs_artifact.get("stage_replay_references", {})),
        "handoff_replay_reference": None,
        "lineage_refs": {
            "ocs_cognition_hash": ocs_artifact["artifact_hash"],
            "human_prompt_hash": ocs_artifact["human_question_hash"],
            "human_facing_cognition_hash": replay_hash(human_result),
            "provider_response_artifact_hashes": deepcopy(ocs_artifact.get("provider_response_artifact_hashes", [])),
            "cognition_artifact_hashes": deepcopy(ocs_artifact.get("cognition_artifact_hashes", [])),
        },
        "upstream_artifact_refs": {
            "ocs_cognition_artifact_type": ocs_artifact["artifact_type"],
            "ocs_cognition_reference": ocs_artifact["end_to_end_id"],
            "ocs_cognition_hash": ocs_artifact["artifact_hash"],
        },
        "downstream_expected_artifact_refs": list(DOWNSTREAM_EXPECTED_ARTIFACT_REFS),
        "hash_bindings": {
            "ocs_cognition_hash": ocs_artifact["artifact_hash"],
            "human_facing_cognition_hash": replay_hash(human_result),
            "execution_intake_hash": replay_hash(
                {
                    "execution_candidate_scope": execution_candidate_scope,
                    "requested_outcomes": requested_outcomes,
                    "allowed_outputs": allowed_outputs,
                    "forbidden_operations": forbidden_operations,
                    "required_validation": required_validation,
                }
            ),
        },
        "replay_integrity_requirements": {
            "ocs_replay_reconstructs_before_handoff": True,
            "handoff_replay_append_only": True,
            "downstream_must_reference_handoff_hash": True,
        },
        "execution_readiness_status": "NOT_EXECUTION_READY",
        "readiness_preconditions": list(DEFAULT_REQUIRED_VALIDATION),
        "readiness_validation_requirements": _string_list_required(required_validation, "required_validation"),
        "readiness_failure_conditions": [
            "approval missing",
            "scope ambiguous",
            "authority escalation",
            "replay lineage mismatch",
            "worker role constraints missing",
        ],
        "execution_packet_requirements": {
            "must_preserve_allowed_outputs": True,
            "must_preserve_forbidden_operations": True,
            "must_preserve_worker_role_requirements": True,
            "execution_state": "NOT_STARTED",
        },
        "authorization_compatibility_requirements": {
            "authorization_must_be_downstream": True,
            "authorization_must_consume_execution_ready": True,
            "authorization_may_not_consume_raw_ocs_cognition": True,
        },
        "failure_reason": failure_reason,
        "replay_visible": True,
    }
    _validate_handoff_authority(artifact)
    artifact["handoff_hash"] = _handoff_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_handoff_artifact(*, handoff_id: str, created_at: str, failure_reason: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": OCS_EXECUTION_HANDOFF_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "contract_reference": "AIGOL_OCS_TO_EXECUTION_HANDOFF_CONTRACT_V1",
        "artifact_version": 1,
        "handoff_id": handoff_id if isinstance(handoff_id, str) and handoff_id.strip() else "OCS-HANDOFF-INVALID",
        "chain_id": "FAILED_CLOSED",
        "created_at": created_at if isinstance(created_at, str) and created_at.strip() else "1970-01-01T00:00:00Z",
        "handoff_status": FAILED_CLOSED,
        "failure_reason": failure_reason,
        **deepcopy(AUTHORITY_FLAGS),
        "authorization_created": False,
        "worker_request_created": False,
        "worker_assigned": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "execution_started": False,
        "repair_started": False,
        "retry_started": False,
        "approval_required": True,
        "approval_status": "FAILED_CLOSED",
        "worker_selection_status": "FAILED_CLOSED",
        "execution_readiness_status": FAILED_CLOSED,
        "replay_visible": True,
    }
    artifact["handoff_hash"] = _handoff_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(handoff: dict[str, Any], *, created_at: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": OCS_EXECUTION_HANDOFF_RETURNED_V1,
        "runtime_version": MILESTONE_ID,
        "handoff_id": handoff["handoff_id"],
        "handoff_status": handoff["handoff_status"],
        "handoff_reference": handoff["handoff_id"],
        "handoff_hash": handoff["handoff_hash"],
        "handoff_artifact_hash": handoff["artifact_hash"],
        "created_at": _require_string(created_at, "created_at"),
        "approval_created": False,
        "authorization_created": False,
        "worker_request_created": False,
        "worker_assigned": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "execution_started": False,
        "repair_started": False,
        "retry_started": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(handoff: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "milestone_id": MILESTONE_ID,
        "final_classification": "AIGOL_OCS_TO_EXECUTION_HANDOFF_RUNTIME_STATUS",
        "classification": "CERTIFIED_OCS_TO_EXECUTION_HANDOFF_RUNTIME",
        "handoff_status": handoff["handoff_status"],
        "handoff_reference": handoff["handoff_id"],
        "handoff_hash": handoff["handoff_hash"],
        "artifact_hash": handoff["artifact_hash"],
        "execution_intake_id": handoff.get("execution_intake_id"),
        "ocs_execution_handoff_artifact": deepcopy(handoff),
        "ocs_execution_handoff_returned_artifact": deepcopy(returned),
        "ocs_execution_handoff_replay_reference": str(replay_path),
        "provider_authority": False,
        "ocs_authority": False,
        "approval_authority": False,
        "execution_authority": False,
        "worker_authority": False,
        "governance_authority": False,
        "replay_authority": False,
        "approval_created": False,
        "authorization_created": False,
        "worker_request_created": False,
        "worker_assigned": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "execution_started": False,
        "repair_started": False,
        "retry_started": False,
        "fail_closed": handoff["handoff_status"] == FAILED_CLOSED,
        "failure_reason": handoff.get("failure_reason", ""),
    }
    capture["ocs_execution_handoff_capture_hash"] = replay_hash(capture)
    return capture


def _validate_ocs_authority(artifact: dict[str, Any]) -> None:
    flags = artifact.get("authority_flags")
    if not isinstance(flags, dict):
        raise FailClosedRuntimeError("OCS execution handoff failed closed: OCS authority flags missing")
    for key, expected in AUTHORITY_FLAGS.items():
        if key == "ocs_authority" and key not in flags:
            continue
        if flags.get(key) is not expected:
            raise FailClosedRuntimeError("OCS execution handoff failed closed: OCS authority violation")
    for key in ("approval_created", "worker_invoked", "execution_requested", "dispatch_requested", "governance_modified", "replay_modified"):
        if artifact.get(key) is not False:
            raise FailClosedRuntimeError("OCS execution handoff failed closed: OCS authority violation")


def _validate_execution_intake(
    *,
    execution_candidate_scope: dict[str, Any],
    requested_outcomes: list[str],
    non_goals: list[str],
    allowed_outputs: list[str],
    forbidden_operations: list[str],
    required_validation: list[str],
    worker_role_requirements: list[str],
    target_worker_family: str,
    candidate_worker_constraints: dict[str, Any],
    worker_capability_requirements: list[str],
    worker_exclusion_rules: list[str],
    worker_registry_requirements: list[str],
) -> None:
    if not isinstance(execution_candidate_scope, dict) or not execution_candidate_scope:
        raise FailClosedRuntimeError("OCS execution handoff failed closed: execution scope ambiguous")
    if not isinstance(candidate_worker_constraints, dict):
        raise FailClosedRuntimeError("OCS execution handoff failed closed: worker constraints invalid")
    for value, name in (
        (requested_outcomes, "requested_outcomes"),
        (non_goals, "non_goals"),
        (allowed_outputs, "allowed_outputs"),
        (forbidden_operations, "forbidden_operations"),
        (required_validation, "required_validation"),
        (worker_role_requirements, "worker_role_requirements"),
        (worker_capability_requirements, "worker_capability_requirements"),
        (worker_exclusion_rules, "worker_exclusion_rules"),
        (worker_registry_requirements, "worker_registry_requirements"),
    ):
        _string_list_required(value, name)
    _require_string(target_worker_family, "target_worker_family")
    if set(allowed_outputs).intersection(forbidden_operations):
        raise FailClosedRuntimeError("OCS execution handoff failed closed: allowed and forbidden operations overlap")


def _validate_handoff_authority(artifact: dict[str, Any]) -> None:
    for key, expected in AUTHORITY_FLAGS.items():
        if artifact.get(key) is not expected:
            raise FailClosedRuntimeError("OCS execution handoff failed closed: authority violation")
    for key in (
        "authorization_created",
        "worker_request_created",
        "worker_assigned",
        "worker_dispatched",
        "worker_invoked",
        "execution_started",
        "repair_started",
        "retry_started",
    ):
        if artifact.get(key) is not False:
            raise FailClosedRuntimeError("OCS execution handoff failed closed: authority violation")
    if artifact.get("approval_status") != "PENDING_HUMAN_REVIEW":
        raise FailClosedRuntimeError("OCS execution handoff failed closed: approval boundary violation")
    if artifact.get("approval_reference") is not None or artifact.get("approval_hash") is not None:
        raise FailClosedRuntimeError("OCS execution handoff failed closed: approval boundary violation")
    if artifact.get("worker_selection_status") != "NOT_SELECTED":
        raise FailClosedRuntimeError("OCS execution handoff failed closed: worker boundary violation")
    if artifact.get("worker_reference") is not None or artifact.get("worker_hash") is not None:
        raise FailClosedRuntimeError("OCS execution handoff failed closed: worker boundary violation")


def _handoff_hash(artifact: dict[str, Any]) -> str:
    payload = deepcopy(artifact)
    payload.pop("handoff_hash", None)
    payload.pop("artifact_hash", None)
    return replay_hash(payload)


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": artifact,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    try:
        _persist_step(replay_path, index, step, artifact)
    except Exception:
        return


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    expected = deepcopy(wrapper)
    actual = expected.pop("replay_hash", None)
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("OCS execution handoff replay hash mismatch")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    expected = deepcopy(artifact)
    actual = expected.pop("artifact_hash", None)
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _ensure_replay_available(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    for index, step in enumerate(REPLAY_STEPS):
        if (path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("OCS execution handoff replay already exists")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"OCS execution handoff failed closed: {field_name} is required")
    return value.strip()


def _string_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) and item.strip() for item in value) and bool(value)


def _string_list_required(value: Any, field_name: str) -> list[str]:
    if not _string_list(value):
        raise FailClosedRuntimeError(f"OCS execution handoff failed closed: {field_name} is required")
    return [item.strip() for item in value]


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "OCS execution handoff failed closed"
