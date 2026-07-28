"""Deterministic checkpoint and resume continuity for G42/G43 workflows."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.constitutional_development_supervisor_runtime import (
    BLOCKER_DIAGNOSED,
    CONSTITUTIONAL_DEVELOPMENT_DIAGNOSIS_EVIDENCE_ARTIFACT_V1,
    WORKFLOW_HEALTHY,
    reconstruct_constitutional_development_supervisor_replay,
    validate_constitutional_development_supervisor_diagnosis_artifact,
)
from aigol.runtime.constitutional_development_workflow_integration_runtime import (
    DEVELOPMENT_VALIDATION_PLANNING_READY,
    reconstruct_constitutional_development_validation_workflow_replay,
    validate_constitutional_development_validation_workflow_artifact,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import (
    load_json,
    replay_hash,
    write_json_immutable,
)


CONSTITUTIONAL_DEVELOPMENT_CONTINUITY_MANAGER_RUNTIME_VERSION = (
    "G44_01_CONSTITUTIONAL_DEVELOPMENT_CONTINUITY_MANAGER_RUNTIME_V1"
)
CONSTITUTIONAL_DEVELOPMENT_CHECKPOINT_ARTIFACT_V1 = (
    "CONSTITUTIONAL_DEVELOPMENT_CHECKPOINT_ARTIFACT_V1"
)
CONSTITUTIONAL_DEVELOPMENT_RESUME_POINT_ARTIFACT_V1 = (
    "CONSTITUTIONAL_DEVELOPMENT_RESUME_POINT_ARTIFACT_V1"
)
EXTERNAL_REPAIR_CONTINUITY_EVIDENCE_ARTIFACT_V1 = (
    "EXTERNAL_REPAIR_CONTINUITY_EVIDENCE_ARTIFACT_V1"
)
CONSTITUTIONAL_CHECKPOINT_INVALIDATION_ARTIFACT_V1 = (
    "CONSTITUTIONAL_CHECKPOINT_INVALIDATION_ARTIFACT_V1"
)
CONSTITUTIONAL_DEVELOPMENT_CONTINUATION_DECISION_ARTIFACT_V1 = (
    "CONSTITUTIONAL_DEVELOPMENT_CONTINUATION_DECISION_ARTIFACT_V1"
)

CHECKPOINT_ACTIVE = "CHECKPOINT_ACTIVE"
RESUME_POINT_PENDING_EXTERNAL_REPAIR = (
    "RESUME_POINT_PENDING_EXTERNAL_REPAIR"
)
EXTERNAL_REPAIR_RECORDED = "EXTERNAL_REPAIR_RECORDED"
CHECKPOINT_INVALIDATED = "CHECKPOINT_INVALIDATED"
CONTINUATION_AUTHORIZED = "CONTINUATION_AUTHORIZED_FROM_RESUME_POINT"
RESUME_FAILED_CLOSED = "RESUME_FAILED_CLOSED"
FAILED_CLOSED = "FAILED_CLOSED"

CHECKPOINT_REPLAY_STEPS = (
    "g42_workflow_bound",
    "g43_supervisor_diagnosis_bound",
    "constitutional_development_checkpoint_recorded",
    "constitutional_development_resume_point_recorded",
)
RESUME_REPLAY_STEPS = (
    "constitutional_development_checkpoint_bound",
    "constitutional_development_resume_point_bound",
    "external_repair_evidence_bound",
    "post_repair_g42_workflow_bound",
    "post_repair_g43_diagnosis_bound",
    "continuation_decision_recorded",
)
INVALIDATION_REPLAY_STEP = "checkpoint_invalidation_recorded"

CANONICAL_WORKFLOW_BOUNDARIES = (
    (0, "PLATFORM_CHANGE_NORMALIZATION"),
    (1, "G42_WORKFLOW_INPUT_BINDING"),
    (2, "IVE_4_ORCHESTRATION_INPUT_BINDING"),
    (3, "IVE_0_IMPACT_ANALYSIS"),
    (4, "IVE_1_SEMANTIC_SELECTION"),
    (5, "G38_VALIDATION_ENTRY"),
    (6, "IVE_2_SCHEDULING"),
    (7, "IVE_3_FAILURE_ANALYSIS"),
    (8, "IVE_4_UNIFIED_PLANNING_BUNDLE"),
    (9, "G42_WORKFLOW_OUTPUT_BINDING"),
)
BOUNDARY_BY_RANK = dict(CANONICAL_WORKFLOW_BOUNDARIES)

INVALIDATION_REASONS = {
    "WORKFLOW_STATE_CHANGED_OUTSIDE_REPAIR_BOUNDARY",
    "REPLAY_LINEAGE_CHANGED",
    "CHECKPOINT_HASH_CHANGED",
    "REQUIRED_EVIDENCE_CHANGED",
    "AFFECTED_CAPABILITY_CHANGED",
    "SUPERSEDED_BY_EXTERNAL_MUTATION",
}

AUTHORITY_FLAGS = {
    "authorizes_execution": False,
    "authorizes_dispatch": False,
    "authorizes_worker_invocation": False,
    "authorizes_provider_invocation": False,
    "authorizes_filesystem_mutation": False,
    "authorizes_governance_mutation": False,
    "authorizes_replay_mutation": False,
    "authorizes_certification": False,
    "constructs_validation_candidate": False,
    "records_human_approval": False,
    "executes_validation": False,
    "invokes_pytest": False,
    "performs_repair": False,
    "modifies_checkpoint": False,
    "modifies_supervisor": False,
    "modifies_ive": False,
    "modifies_authorization": False,
    "modifies_worker_contracts": False,
    "modifies_provider_contracts": False,
    "modifies_aicli": False,
    "modifies_pcbv31": False,
}


def create_constitutional_development_checkpoint(
    *,
    workflow_artifact: dict[str, Any],
    workflow_reference: str,
    workflow_hash: str,
    workflow_artifact_hash: str,
    workflow_replay_dir: str | Path,
    supervisor_diagnosis_artifact: dict[str, Any],
    supervisor_diagnosis_reference: str,
    supervisor_diagnosis_hash: str,
    supervisor_diagnosis_artifact_hash: str,
    supervisor_replay_dir: str | Path,
    created_by: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Create immutable checkpoint and resume point for one diagnosed blocker."""

    replay_path = Path(replay_dir)
    workflow: dict[str, Any] | None = None
    diagnosis: dict[str, Any] | None = None
    checkpoint: dict[str, Any] | None = None
    resume_point: dict[str, Any] | None = None
    try:
        _ensure_replay_available(replay_path, CHECKPOINT_REPLAY_STEPS)
        creator = _require_string(created_by, "created_by")
        timestamp = _require_string(created_at, "created_at")
        workflow = validate_constitutional_development_validation_workflow_artifact(
            workflow_artifact
        )
        diagnosis = validate_constitutional_development_supervisor_diagnosis_artifact(
            supervisor_diagnosis_artifact
        )
        _validate_checkpoint_source_bindings(
            workflow=workflow,
            workflow_reference=workflow_reference,
            workflow_hash=workflow_hash,
            workflow_artifact_hash=workflow_artifact_hash,
            diagnosis=diagnosis,
            diagnosis_reference=supervisor_diagnosis_reference,
            diagnosis_hash=supervisor_diagnosis_hash,
            diagnosis_artifact_hash=supervisor_diagnosis_artifact_hash,
        )
        workflow_reconstruction = (
            reconstruct_constitutional_development_validation_workflow_replay(
                workflow_replay_dir
            )
        )
        supervisor_reconstruction = (
            reconstruct_constitutional_development_supervisor_replay(
                supervisor_replay_dir
            )
        )
        _validate_source_reconstruction(
            workflow,
            workflow_reconstruction,
            diagnosis,
            supervisor_reconstruction,
        )
        diagnosis_evidence = _load_supervisor_diagnosis_evidence(
            Path(supervisor_replay_dir)
        )
        checkpoint = _checkpoint_artifact(
            workflow=workflow,
            workflow_replay_reference=str(Path(workflow_replay_dir)),
            workflow_replay_hashes=workflow_reconstruction["replay_hashes"],
            diagnosis=diagnosis,
            supervisor_replay_reference=str(Path(supervisor_replay_dir)),
            supervisor_replay_hashes=supervisor_reconstruction[
                "replay_hashes"
            ],
            diagnosis_evidence=diagnosis_evidence,
            created_by=creator,
            created_at=timestamp,
        )
        resume_point = _resume_point_artifact(
            checkpoint=checkpoint,
            created_by=creator,
            created_at=timestamp,
        )
    except Exception as exc:
        checkpoint = _failed_checkpoint_artifact(
            workflow_artifact=workflow
            if workflow is not None
            else workflow_artifact,
            diagnosis_artifact=diagnosis
            if diagnosis is not None
            else supervisor_diagnosis_artifact,
            created_by=created_by,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        resume_point = _failed_resume_point_artifact(
            checkpoint=checkpoint,
            created_by=created_by,
            created_at=created_at,
            failure_reason=checkpoint["failure_reason"],
        )
    _persist_checkpoint_replay(
        replay_path,
        workflow,
        diagnosis,
        checkpoint,
        resume_point,
    )
    return _checkpoint_capture(checkpoint, resume_point, replay_path)


def validate_constitutional_development_checkpoint_artifact(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Validate one immutable constitutional checkpoint."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(
            "G44-01 checkpoint must be a JSON object"
        )
    candidate = deepcopy(artifact)
    _verify_checkpoint_artifact(candidate)
    return candidate


def validate_constitutional_development_resume_point_artifact(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Validate one immutable deterministic resume point."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(
            "G44-01 resume point must be a JSON object"
        )
    candidate = deepcopy(artifact)
    _verify_resume_point_artifact(candidate)
    return candidate


def reconstruct_constitutional_development_checkpoint_replay(
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Reconstruct checkpoint, resume point, and source lineage."""

    replay_path = Path(replay_dir)
    wrappers = [
        load_json(replay_path / f"{index:03d}_{step}.json")
        for index, step in enumerate(CHECKPOINT_REPLAY_STEPS)
    ]
    for index, (step, wrapper) in enumerate(
        zip(CHECKPOINT_REPLAY_STEPS, wrappers)
    ):
        _verify_wrapper(wrapper, index, step, "checkpoint")
    checkpoint = validate_constitutional_development_checkpoint_artifact(
        wrappers[2].get("artifact")
    )
    resume_point = validate_constitutional_development_resume_point_artifact(
        wrappers[3].get("artifact")
    )
    if checkpoint["checkpoint_status"] == CHECKPOINT_ACTIVE:
        workflow = validate_constitutional_development_validation_workflow_artifact(
            wrappers[0].get("artifact")
        )
        diagnosis = validate_constitutional_development_supervisor_diagnosis_artifact(
            wrappers[1].get("artifact")
        )
        _validate_checkpoint_replay_bindings(
            checkpoint,
            resume_point,
            workflow,
            diagnosis,
        )
    return {
        "checkpoint_id": checkpoint["checkpoint_id"],
        "checkpoint_status": checkpoint["checkpoint_status"],
        "checkpoint_hash": checkpoint["checkpoint_hash"],
        "resume_point_id": resume_point["resume_point_id"],
        "resume_point_status": resume_point["resume_point_status"],
        "resume_point_hash": resume_point["resume_point_hash"],
        "workflow_position": deepcopy(checkpoint["workflow_position"]),
        "repair_boundary": deepcopy(checkpoint["certified_repair_boundary"]),
        "required_revalidation_scope": deepcopy(
            checkpoint["required_revalidation_scope"]
        ),
        "replay_lineage_hash": checkpoint["replay_lineage_hash"],
        "replay_visible": True,
        "fail_closed": checkpoint["checkpoint_status"] == FAILED_CLOSED,
        "failure_reason": checkpoint["failure_reason"],
        "validation_executed": False,
        "repair_performed": False,
        "authority_flags": deepcopy(checkpoint["authority_flags"]),
        "replay_hashes": [wrapper["replay_hash"] for wrapper in wrappers],
    }


def record_external_repair_continuity_evidence(
    *,
    repair_evidence_id: str,
    checkpoint_artifact: dict[str, Any],
    resume_point_artifact: dict[str, Any],
    pre_repair_workflow_reference: str,
    pre_repair_workflow_hash: str,
    post_repair_workflow_reference: str,
    post_repair_workflow_hash: str,
    modified_boundaries: list[str],
    affected_capability_identifiers: list[str],
    validation_scope_hash: str,
    validation_evidence_references: list[dict[str, Any]],
    human_approval_reference: str,
    human_approval_hash: str,
    superseding_mutation_reference: str | None,
    recorded_by: str,
    recorded_at: str,
) -> dict[str, Any]:
    """Record facts asserted by an external repair process without repairing."""

    checkpoint = validate_constitutional_development_checkpoint_artifact(
        checkpoint_artifact
    )
    resume_point = validate_constitutional_development_resume_point_artifact(
        resume_point_artifact
    )
    _validate_checkpoint_resume_binding(checkpoint, resume_point)
    evidence_refs = _validation_evidence_references(
        validation_evidence_references
    )
    artifact = {
        "artifact_type": EXTERNAL_REPAIR_CONTINUITY_EVIDENCE_ARTIFACT_V1,
        "runtime_version": (
            CONSTITUTIONAL_DEVELOPMENT_CONTINUITY_MANAGER_RUNTIME_VERSION
        ),
        "repair_evidence_id": _require_string(
            repair_evidence_id,
            "repair_evidence_id",
        ),
        "repair_evidence_status": EXTERNAL_REPAIR_RECORDED,
        "checkpoint_id": checkpoint["checkpoint_id"],
        "checkpoint_hash": checkpoint["checkpoint_hash"],
        "resume_point_id": resume_point["resume_point_id"],
        "resume_point_hash": resume_point["resume_point_hash"],
        "pre_repair_workflow_reference": _require_string(
            pre_repair_workflow_reference,
            "pre_repair_workflow_reference",
        ),
        "pre_repair_workflow_hash": _require_hash(
            pre_repair_workflow_hash,
            "pre_repair_workflow_hash",
        ),
        "post_repair_workflow_reference": _require_string(
            post_repair_workflow_reference,
            "post_repair_workflow_reference",
        ),
        "post_repair_workflow_hash": _require_hash(
            post_repair_workflow_hash,
            "post_repair_workflow_hash",
        ),
        "modified_boundaries": _string_list(
            modified_boundaries,
            "modified_boundaries",
        ),
        "affected_capability_identifiers": _string_list(
            affected_capability_identifiers,
            "affected_capability_identifiers",
        ),
        "preserved_replay_lineage_hash": checkpoint[
            "replay_lineage_hash"
        ],
        "validation_scope_hash": _require_hash(
            validation_scope_hash,
            "validation_scope_hash",
        ),
        "validation_evidence_references": evidence_refs,
        "validation_evidence_count": len(evidence_refs),
        "human_approval_reference": _require_string(
            human_approval_reference,
            "human_approval_reference",
        ),
        "human_approval_hash": _require_hash(
            human_approval_hash,
            "human_approval_hash",
        ),
        "superseding_mutation_reference": (
            _require_string(
                superseding_mutation_reference,
                "superseding_mutation_reference",
            )
            if superseding_mutation_reference is not None
            else None
        ),
        "repair_performed_externally": True,
        "manager_performed_repair": False,
        "manager_executed_validation": False,
        "continuation_authorized": False,
        "recorded_by": _require_string(recorded_by, "recorded_by"),
        "recorded_at": _require_string(recorded_at, "recorded_at"),
        "replay_visible": True,
        "read_only": True,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
    }
    artifact["repair_evidence_hash"] = _repair_evidence_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def validate_external_repair_continuity_evidence_artifact(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Validate external repair facts without accepting their compliance."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(
            "G44-01 external repair evidence must be a JSON object"
        )
    candidate = deepcopy(artifact)
    _verify_repair_evidence_artifact(candidate)
    return candidate


def invalidate_constitutional_development_checkpoint(
    *,
    invalidation_id: str,
    checkpoint_artifact: dict[str, Any],
    resume_point_artifact: dict[str, Any],
    invalidation_reason: str,
    superseding_evidence_reference: str,
    superseding_evidence_hash: str,
    invalidated_by: str,
    invalidated_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Invalidate by additive record; never mutate checkpoint or resume point."""

    replay_path = Path(replay_dir)
    try:
        _ensure_single_replay_available(
            replay_path,
            INVALIDATION_REPLAY_STEP,
        )
        checkpoint = validate_constitutional_development_checkpoint_artifact(
            checkpoint_artifact
        )
        resume_point = validate_constitutional_development_resume_point_artifact(
            resume_point_artifact
        )
        _validate_checkpoint_resume_binding(checkpoint, resume_point)
        reason = _require_string(
            invalidation_reason,
            "invalidation_reason",
        )
        if reason not in INVALIDATION_REASONS:
            raise FailClosedRuntimeError(
                "G44-01 checkpoint invalidation reason invalid"
            )
        artifact = _invalidation_artifact(
            invalidation_id=_require_string(
                invalidation_id,
                "invalidation_id",
            ),
            invalidation_status=CHECKPOINT_INVALIDATED,
            checkpoint=checkpoint,
            resume_point=resume_point,
            invalidation_reason=reason,
            superseding_evidence_reference=_require_string(
                superseding_evidence_reference,
                "superseding_evidence_reference",
            ),
            superseding_evidence_hash=_require_hash(
                superseding_evidence_hash,
                "superseding_evidence_hash",
            ),
            invalidated_by=_require_string(
                invalidated_by,
                "invalidated_by",
            ),
            invalidated_at=_require_string(
                invalidated_at,
                "invalidated_at",
            ),
            failure_reason=None,
        )
    except Exception as exc:
        artifact = _failed_invalidation_artifact(
            invalidation_id=invalidation_id,
            checkpoint_artifact=checkpoint_artifact,
            resume_point_artifact=resume_point_artifact,
            invalidation_reason=invalidation_reason,
            invalidated_by=invalidated_by,
            invalidated_at=invalidated_at,
            failure_reason=_failure_reason(exc),
        )
    _persist_single_replay(
        replay_path,
        INVALIDATION_REPLAY_STEP,
        artifact,
    )
    return {
        "runtime_version": (
            CONSTITUTIONAL_DEVELOPMENT_CONTINUITY_MANAGER_RUNTIME_VERSION
        ),
        "checkpoint_invalidation_artifact": deepcopy(artifact),
        "invalidation_status": artifact["invalidation_status"],
        "checkpoint_id": artifact["checkpoint_id"],
        "checkpoint_hash": artifact["checkpoint_hash"],
        "replay_reference": str(replay_path),
        "fail_closed": artifact["invalidation_status"] == FAILED_CLOSED,
        "failure_reason": artifact["failure_reason"],
        "continuation_authorized": False,
        "checkpoint_modified": False,
    }


def validate_constitutional_checkpoint_invalidation_artifact(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Validate additive checkpoint invalidation evidence."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(
            "G44-01 checkpoint invalidation must be a JSON object"
        )
    candidate = deepcopy(artifact)
    _verify_invalidation_artifact(candidate)
    return candidate


def verify_constitutional_development_resume(
    *,
    continuation_id: str,
    checkpoint_artifact: dict[str, Any],
    resume_point_artifact: dict[str, Any],
    checkpoint_invalidation_artifact: dict[str, Any] | None,
    external_repair_evidence_artifact: dict[str, Any],
    post_repair_workflow_artifact: dict[str, Any],
    post_repair_workflow_reference: str,
    post_repair_workflow_hash: str,
    post_repair_workflow_artifact_hash: str,
    post_repair_workflow_replay_dir: str | Path,
    post_repair_supervisor_diagnosis_artifact: dict[str, Any],
    post_repair_supervisor_diagnosis_reference: str,
    post_repair_supervisor_diagnosis_hash: str,
    post_repair_supervisor_diagnosis_artifact_hash: str,
    post_repair_supervisor_replay_dir: str | Path,
    verified_by: str,
    verified_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Issue workflow-only continuation after every continuity proof passes."""

    replay_path = Path(replay_dir)
    checkpoint: dict[str, Any] | None = None
    resume_point: dict[str, Any] | None = None
    repair_evidence: dict[str, Any] | None = None
    workflow: dict[str, Any] | None = None
    diagnosis: dict[str, Any] | None = None
    try:
        _ensure_replay_available(replay_path, RESUME_REPLAY_STEPS)
        identifier = _require_string(continuation_id, "continuation_id")
        verifier = _require_string(verified_by, "verified_by")
        timestamp = _require_string(verified_at, "verified_at")
        checkpoint = validate_constitutional_development_checkpoint_artifact(
            checkpoint_artifact
        )
        resume_point = validate_constitutional_development_resume_point_artifact(
            resume_point_artifact
        )
        _validate_checkpoint_resume_binding(checkpoint, resume_point)
        if checkpoint_invalidation_artifact is not None:
            invalidation = (
                validate_constitutional_checkpoint_invalidation_artifact(
                    checkpoint_invalidation_artifact
                )
            )
            if (
                invalidation["checkpoint_id"] == checkpoint["checkpoint_id"]
                and invalidation["checkpoint_hash"]
                == checkpoint["checkpoint_hash"]
                and invalidation["invalidation_status"]
                == CHECKPOINT_INVALIDATED
            ):
                raise FailClosedRuntimeError(
                    "G44-01 stale checkpoint was invalidated"
                )
        repair_evidence = (
            validate_external_repair_continuity_evidence_artifact(
                external_repair_evidence_artifact
            )
        )
        workflow = validate_constitutional_development_validation_workflow_artifact(
            post_repair_workflow_artifact
        )
        diagnosis = validate_constitutional_development_supervisor_diagnosis_artifact(
            post_repair_supervisor_diagnosis_artifact
        )
        _validate_post_repair_bindings(
            workflow=workflow,
            workflow_reference=post_repair_workflow_reference,
            workflow_hash=post_repair_workflow_hash,
            workflow_artifact_hash=post_repair_workflow_artifact_hash,
            diagnosis=diagnosis,
            diagnosis_reference=post_repair_supervisor_diagnosis_reference,
            diagnosis_hash=post_repair_supervisor_diagnosis_hash,
            diagnosis_artifact_hash=(
                post_repair_supervisor_diagnosis_artifact_hash
            ),
        )
        workflow_reconstruction = (
            reconstruct_constitutional_development_validation_workflow_replay(
                post_repair_workflow_replay_dir
            )
        )
        supervisor_reconstruction = (
            reconstruct_constitutional_development_supervisor_replay(
                post_repair_supervisor_replay_dir
            )
        )
        _validate_source_reconstruction(
            workflow,
            workflow_reconstruction,
            diagnosis,
            supervisor_reconstruction,
        )
        diagnosis_evidence = _load_supervisor_diagnosis_evidence(
            Path(post_repair_supervisor_replay_dir)
        )
        continuity = _verify_resume_continuity(
            checkpoint=checkpoint,
            resume_point=resume_point,
            repair_evidence=repair_evidence,
            post_workflow=workflow,
            post_diagnosis=diagnosis,
            post_diagnosis_evidence=diagnosis_evidence,
        )
        decision = _continuation_decision_artifact(
            continuation_id=identifier,
            continuation_status=CONTINUATION_AUTHORIZED,
            checkpoint=checkpoint,
            resume_point=resume_point,
            repair_evidence=repair_evidence,
            workflow=workflow,
            diagnosis=diagnosis,
            continuity=continuity,
            verified_by=verifier,
            verified_at=timestamp,
            failure_reason=None,
        )
    except Exception as exc:
        decision = _failed_continuation_decision_artifact(
            continuation_id=continuation_id,
            checkpoint_artifact=checkpoint
            if checkpoint is not None
            else checkpoint_artifact,
            resume_point_artifact=resume_point
            if resume_point is not None
            else resume_point_artifact,
            external_repair_evidence_artifact=repair_evidence
            if repair_evidence is not None
            else external_repair_evidence_artifact,
            post_repair_workflow_artifact=workflow
            if workflow is not None
            else post_repair_workflow_artifact,
            post_repair_diagnosis_artifact=diagnosis
            if diagnosis is not None
            else post_repair_supervisor_diagnosis_artifact,
            verified_by=verified_by,
            verified_at=verified_at,
            failure_reason=_failure_reason(exc),
        )
    _persist_resume_replay(
        replay_path,
        checkpoint,
        resume_point,
        repair_evidence,
        workflow,
        diagnosis,
        decision,
    )
    return _continuation_capture(decision, replay_path)


def validate_constitutional_development_continuation_decision_artifact(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Validate workflow-only continuation eligibility."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(
            "G44-01 continuation decision must be a JSON object"
        )
    candidate = deepcopy(artifact)
    _verify_continuation_decision_artifact(candidate)
    return candidate


def reconstruct_constitutional_development_continuation_replay(
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Reconstruct every resume verification input and final decision."""

    replay_path = Path(replay_dir)
    wrappers = [
        load_json(replay_path / f"{index:03d}_{step}.json")
        for index, step in enumerate(RESUME_REPLAY_STEPS)
    ]
    for index, (step, wrapper) in enumerate(
        zip(RESUME_REPLAY_STEPS, wrappers)
    ):
        _verify_wrapper(wrapper, index, step, "resume")
    decision = (
        validate_constitutional_development_continuation_decision_artifact(
            wrappers[5].get("artifact")
        )
    )
    if decision["continuation_status"] == CONTINUATION_AUTHORIZED:
        checkpoint = (
            validate_constitutional_development_checkpoint_artifact(
                wrappers[0].get("artifact")
            )
        )
        resume_point = (
            validate_constitutional_development_resume_point_artifact(
                wrappers[1].get("artifact")
            )
        )
        repair_evidence = (
            validate_external_repair_continuity_evidence_artifact(
                wrappers[2].get("artifact")
            )
        )
        workflow = validate_constitutional_development_validation_workflow_artifact(
            wrappers[3].get("artifact")
        )
        diagnosis = validate_constitutional_development_supervisor_diagnosis_artifact(
            wrappers[4].get("artifact")
        )
        _validate_continuation_replay_bindings(
            decision,
            checkpoint,
            resume_point,
            repair_evidence,
            workflow,
            diagnosis,
        )
    return {
        "continuation_id": decision["continuation_id"],
        "continuation_status": decision["continuation_status"],
        "checkpoint_id": decision["checkpoint_id"],
        "resume_point_id": decision["resume_point_id"],
        "resume_from_boundary": deepcopy(
            decision["resume_from_boundary"]
        ),
        "preserved_stage_lineage": deepcopy(
            decision["preserved_stage_lineage"]
        ),
        "verified_remaining_boundaries": deepcopy(
            decision["verified_remaining_boundaries"]
        ),
        "decision_hash": decision["decision_hash"],
        "artifact_hash": decision["artifact_hash"],
        "continuation_authorized": (
            decision["continuation_status"] == CONTINUATION_AUTHORIZED
        ),
        "execution_authorized": False,
        "human_approval_required": True,
        "validation_executed": False,
        "repair_performed": False,
        "replay_visible": True,
        "fail_closed": (
            decision["continuation_status"] == RESUME_FAILED_CLOSED
        ),
        "failure_reason": decision["failure_reason"],
        "authority_flags": deepcopy(decision["authority_flags"]),
        "replay_hashes": [wrapper["replay_hash"] for wrapper in wrappers],
    }


def _checkpoint_artifact(
    *,
    workflow: dict[str, Any],
    workflow_replay_reference: str,
    workflow_replay_hashes: list[str],
    diagnosis: dict[str, Any],
    supervisor_replay_reference: str,
    supervisor_replay_hashes: list[str],
    diagnosis_evidence: dict[str, Any],
    created_by: str,
    created_at: str,
) -> dict[str, Any]:
    # Physical replay directories are transport locations, not constitutional
    # identity. Canonical artifact identifiers bind the replay lineage.
    _ = workflow_replay_reference, supervisor_replay_reference
    blocker = diagnosis["earliest_constitutional_blocker"]
    blocker_rank = blocker["boundary_rank"]
    if not isinstance(blocker_rank, int) or blocker_rank not in BOUNDARY_BY_RANK:
        raise FailClosedRuntimeError(
            "G44-01 Supervisor blocker rank is invalid"
        )
    observations = diagnosis_evidence["boundary_observations"]
    preserved = [
        deepcopy(item)
        for item in observations
        if item["boundary_rank"] < blocker_rank
    ]
    preserved.sort(key=lambda item: item["boundary_rank"])
    _validate_preserved_prefix(preserved, blocker_rank)
    replay_lineage = {
        "workflow_replay_reference": workflow["workflow_id"],
        "workflow_replay_hashes": deepcopy(workflow_replay_hashes),
        "workflow_replay_hash": replay_hash(workflow_replay_hashes),
        "supervisor_replay_reference": diagnosis["diagnosis_id"],
        "supervisor_replay_hashes": deepcopy(supervisor_replay_hashes),
        "supervisor_replay_hash": replay_hash(supervisor_replay_hashes),
        "preserved_stage_observation_hashes": [
            item["observation_hash"] for item in preserved
        ],
        "preserved_stage_lineage_hash": replay_hash(preserved),
    }
    replay_lineage["replay_lineage_hash"] = replay_hash(replay_lineage)
    repair_boundary = deepcopy(diagnosis["minimal_repair_boundary"])
    validation_scope = deepcopy(diagnosis["minimal_revalidation_scope"])
    affected = [
        diagnosis["affected_certified_capability"][
            "capability_identifier"
        ]
    ]
    ive_bundle = workflow.get("ive_4_planning_bundle_artifact") or {}
    base = {
        "workflow_position": {
            "execution_spine": "PCBV31_POST_EXECUTION_DEVELOPMENT_WORKFLOW",
            "position_status": "BLOCKED",
            "blocked_boundary_rank": blocker_rank,
            "blocked_boundary": blocker["boundary"],
            "last_certified_boundary_rank": (
                preserved[-1]["boundary_rank"] if preserved else None
            ),
            "next_required_boundary_rank": blocker_rank,
        },
        "workflow_reference": workflow["workflow_id"],
        "workflow_hash": workflow["workflow_hash"],
        "workflow_artifact_hash": workflow["artifact_hash"],
        "workflow_status": workflow["workflow_status"],
        "replay_lineage": replay_lineage,
        "replay_lineage_hash": replay_lineage["replay_lineage_hash"],
        "stage_lineage": deepcopy(
            workflow.get("planning_stage_lineage") or []
        ),
        "stage_lineage_hash": replay_hash(
            workflow.get("planning_stage_lineage") or []
        ),
        "ive_planning_bundle_reference": (
            ive_bundle.get("orchestration_id", "UNAVAILABLE")
        ),
        "ive_planning_bundle_hash": _safe_hash(
            ive_bundle.get("bundle_hash")
        ),
        "certified_repair_boundary": repair_boundary,
        "certified_repair_boundary_hash": replay_hash(repair_boundary),
        "required_revalidation_scope": validation_scope,
        "required_revalidation_scope_hash": replay_hash(validation_scope),
        "affected_capability_identifiers": affected,
        "affected_capability_identifiers_hash": replay_hash(affected),
        "supervisor_diagnosis_reference": diagnosis["diagnosis_id"],
        "supervisor_diagnosis_hash": diagnosis["diagnosis_hash"],
        "supervisor_diagnosis_artifact_hash": diagnosis["artifact_hash"],
        "supervisor_diagnosis_evidence_hash": diagnosis[
            "diagnosis_evidence_hash"
        ],
        "preserved_stage_lineage": preserved,
        "preserved_stage_lineage_hash": replay_hash(preserved),
        "created_by": created_by,
        "created_at": created_at,
    }
    state_hash = replay_hash(base)
    checkpoint_id = f"CDCM-CHECKPOINT-{state_hash[7:31].upper()}"
    artifact = {
        "artifact_type": CONSTITUTIONAL_DEVELOPMENT_CHECKPOINT_ARTIFACT_V1,
        "runtime_version": (
            CONSTITUTIONAL_DEVELOPMENT_CONTINUITY_MANAGER_RUNTIME_VERSION
        ),
        "checkpoint_id": checkpoint_id,
        "checkpoint_status": CHECKPOINT_ACTIVE,
        **base,
        "checkpoint_state_hash": state_hash,
        "checkpoint_immutable": True,
        "repair_performed": False,
        "validation_executed": False,
        "continuation_authorized": False,
        "human_approval_required": True,
        "replay_visible": True,
        "read_only": True,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "failure_reason": None,
    }
    artifact["checkpoint_hash"] = _checkpoint_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _resume_point_artifact(
    *,
    checkpoint: dict[str, Any],
    created_by: str,
    created_at: str,
) -> dict[str, Any]:
    blocker_rank = checkpoint["workflow_position"][
        "blocked_boundary_rank"
    ]
    required_boundaries = [
        {
            "boundary_rank": rank,
            "boundary": boundary,
            "required_after_repair": True,
        }
        for rank, boundary in CANONICAL_WORKFLOW_BOUNDARIES
        if rank >= blocker_rank
    ]
    resume_identity = {
        "checkpoint_id": checkpoint["checkpoint_id"],
        "checkpoint_hash": checkpoint["checkpoint_hash"],
        "workflow_hash": checkpoint["workflow_hash"],
        "replay_lineage_hash": checkpoint["replay_lineage_hash"],
        "repair_boundary_hash": checkpoint[
            "certified_repair_boundary_hash"
        ],
        "validation_scope_hash": checkpoint[
            "required_revalidation_scope_hash"
        ],
    }
    identity_hash = replay_hash(resume_identity)
    artifact = {
        "artifact_type": (
            CONSTITUTIONAL_DEVELOPMENT_RESUME_POINT_ARTIFACT_V1
        ),
        "runtime_version": (
            CONSTITUTIONAL_DEVELOPMENT_CONTINUITY_MANAGER_RUNTIME_VERSION
        ),
        "resume_point_id": (
            f"CDCM-RESUME-{identity_hash[7:31].upper()}"
        ),
        "resume_point_status": RESUME_POINT_PENDING_EXTERNAL_REPAIR,
        "checkpoint_id": checkpoint["checkpoint_id"],
        "checkpoint_hash": checkpoint["checkpoint_hash"],
        "workflow_reference": checkpoint["workflow_reference"],
        "workflow_hash": checkpoint["workflow_hash"],
        "workflow_artifact_hash": checkpoint["workflow_artifact_hash"],
        "exact_workflow_state_hash": checkpoint["checkpoint_state_hash"],
        "replay_lineage_hash": checkpoint["replay_lineage_hash"],
        "preserved_stage_lineage": deepcopy(
            checkpoint["preserved_stage_lineage"]
        ),
        "preserved_stage_lineage_hash": checkpoint[
            "preserved_stage_lineage_hash"
        ],
        "resume_boundary": deepcopy(
            checkpoint["workflow_position"]
        ),
        "certified_repair_boundary": deepcopy(
            checkpoint["certified_repair_boundary"]
        ),
        "certified_repair_boundary_hash": checkpoint[
            "certified_repair_boundary_hash"
        ],
        "required_revalidation_scope": deepcopy(
            checkpoint["required_revalidation_scope"]
        ),
        "required_revalidation_scope_hash": checkpoint[
            "required_revalidation_scope_hash"
        ],
        "required_remaining_boundaries": required_boundaries,
        "required_remaining_boundaries_hash": replay_hash(
            required_boundaries
        ),
        "must_not_repeat_boundary_ranks": [
            item["boundary_rank"]
            for item in checkpoint["preserved_stage_lineage"]
        ],
        "must_not_skip_boundary_ranks": [
            item["boundary_rank"] for item in required_boundaries
        ],
        "affected_capability_identifiers": deepcopy(
            checkpoint["affected_capability_identifiers"]
        ),
        "created_by": created_by,
        "created_at": created_at,
        "checkpoint_preserved_unchanged": True,
        "repair_performed": False,
        "validation_executed": False,
        "continuation_authorized": False,
        "human_approval_required": True,
        "replay_visible": True,
        "read_only": True,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "failure_reason": None,
    }
    artifact["resume_point_hash"] = _resume_point_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _verify_resume_continuity(
    *,
    checkpoint: dict[str, Any],
    resume_point: dict[str, Any],
    repair_evidence: dict[str, Any],
    post_workflow: dict[str, Any],
    post_diagnosis: dict[str, Any],
    post_diagnosis_evidence: dict[str, Any],
) -> dict[str, Any]:
    if (
        repair_evidence["checkpoint_id"] != checkpoint["checkpoint_id"]
        or repair_evidence["checkpoint_hash"] != checkpoint["checkpoint_hash"]
        or repair_evidence["resume_point_id"]
        != resume_point["resume_point_id"]
        or repair_evidence["resume_point_hash"]
        != resume_point["resume_point_hash"]
        or repair_evidence["pre_repair_workflow_reference"]
        != checkpoint["workflow_reference"]
        or repair_evidence["pre_repair_workflow_hash"]
        != checkpoint["workflow_hash"]
        or repair_evidence["post_repair_workflow_reference"]
        != post_workflow["workflow_id"]
        or repair_evidence["post_repair_workflow_hash"]
        != post_workflow["workflow_hash"]
    ):
        raise FailClosedRuntimeError(
            "G44-01 repair evidence checkpoint or workflow mismatch"
        )
    repair_boundary = checkpoint["certified_repair_boundary"]["boundary"]
    if repair_evidence["modified_boundaries"] != [repair_boundary]:
        raise FailClosedRuntimeError(
            "G44-01 repair exceeded the certified boundary"
        )
    if (
        repair_evidence["affected_capability_identifiers"]
        != checkpoint["affected_capability_identifiers"]
    ):
        raise FailClosedRuntimeError(
            "G44-01 affected capability changed"
        )
    if (
        repair_evidence["preserved_replay_lineage_hash"]
        != checkpoint["replay_lineage_hash"]
    ):
        raise FailClosedRuntimeError(
            "G44-01 repair replay lineage changed"
        )
    if (
        repair_evidence["validation_scope_hash"]
        != checkpoint["required_revalidation_scope_hash"]
        or not repair_evidence["validation_evidence_references"]
        or any(
            item["validated_scope_hash"]
            != checkpoint["required_revalidation_scope_hash"]
            for item in repair_evidence[
                "validation_evidence_references"
            ]
        )
    ):
        raise FailClosedRuntimeError(
            "G44-01 required validation evidence missing"
        )
    if repair_evidence["superseding_mutation_reference"] is not None:
        raise FailClosedRuntimeError(
            "G44-01 checkpoint superseded by another mutation"
        )
    if post_workflow["workflow_status"] != DEVELOPMENT_VALIDATION_PLANNING_READY:
        raise FailClosedRuntimeError(
            "G44-01 post-repair workflow is not planning-ready"
        )
    if post_diagnosis["diagnosis_status"] != WORKFLOW_HEALTHY:
        raise FailClosedRuntimeError(
            "G44-01 post-repair Supervisor diagnosis is not healthy"
        )
    if (
        post_diagnosis_evidence["evidence_status"]
        != "COMPLETE_NO_BLOCKER"
        or post_diagnosis_evidence["earliest_blocker_evidence"] is not None
    ):
        raise FailClosedRuntimeError(
            "G44-01 post-repair diagnosis evidence remains blocked"
        )

    available = _post_repair_boundary_evidence(
        post_workflow,
        post_diagnosis_evidence,
    )
    preserved = checkpoint["preserved_stage_lineage"]
    for item in preserved:
        post = available.get(item["boundary_rank"])
        if (
            post is None
            or post["boundary"] != item["boundary"]
            or post["artifact_hash"] != item["artifact_hash"]
        ):
            raise FailClosedRuntimeError(
                "G44-01 preserved certified stage lineage changed"
            )
    required_ranks = resume_point["must_not_skip_boundary_ranks"]
    missing_ranks = [rank for rank in required_ranks if rank not in available]
    if missing_ranks:
        raise FailClosedRuntimeError(
            "G44-01 required workflow stage was skipped"
        )
    if resume_point["must_not_repeat_boundary_ranks"] != [
        item["boundary_rank"] for item in preserved
    ]:
        raise FailClosedRuntimeError(
            "G44-01 preserved stage resume contract changed"
        )
    continuity = {
        "checkpoint_integrity_verified": True,
        "resume_point_integrity_verified": True,
        "original_replay_lineage_verified": True,
        "preserved_stage_lineage_verified": True,
        "repair_boundary_compliance_verified": True,
        "affected_capability_continuity_verified": True,
        "required_validation_evidence_verified": True,
        "supervisor_diagnosis_consistency_verified": True,
        "stale_checkpoint_rejected": True,
        "duplicate_resume_prohibited": True,
        "already_certified_stages_reused": True,
        "required_remaining_stages_verified": True,
        "preserved_boundary_ranks": [
            item["boundary_rank"] for item in preserved
        ],
        "verified_remaining_boundary_ranks": required_ranks,
        "post_repair_workflow_hash": post_workflow["workflow_hash"],
        "post_repair_diagnosis_hash": post_diagnosis["diagnosis_hash"],
        "validation_evidence_hashes": [
            item["evidence_hash"]
            for item in repair_evidence[
                "validation_evidence_references"
            ]
        ],
    }
    continuity["continuity_verification_hash"] = replay_hash(continuity)
    return continuity


def _post_repair_boundary_evidence(
    workflow: dict[str, Any],
    diagnosis_evidence: dict[str, Any],
) -> dict[int, dict[str, Any]]:
    available = {
        item["boundary_rank"]: {
            "boundary": item["boundary"],
            "artifact_hash": item["artifact_hash"],
        }
        for item in diagnosis_evidence["boundary_observations"]
    }
    bundle = workflow["ive_4_planning_bundle_artifact"]
    available[2] = {
        "boundary": "IVE_4_ORCHESTRATION_INPUT_BINDING",
        "artifact_hash": bundle[
            "source_normalized_change_artifact_hash"
        ],
    }
    available[9] = {
        "boundary": "G42_WORKFLOW_OUTPUT_BINDING",
        "artifact_hash": workflow["artifact_hash"],
    }
    for rank, boundary in CANONICAL_WORKFLOW_BOUNDARIES:
        item = available.get(rank)
        if item is not None and item["boundary"] != boundary:
            if rank == 3 and item["boundary"] == "IVE_0":
                item["boundary"] = boundary
            elif rank == 4 and item["boundary"] == "IVE_1":
                item["boundary"] = boundary
            elif rank == 5 and item["boundary"] == "G38_ENTRY":
                item["boundary"] = boundary
            elif rank == 6 and item["boundary"] == "IVE_2":
                item["boundary"] = boundary
            elif rank == 7 and item["boundary"] == "IVE_3":
                item["boundary"] = boundary
            else:
                raise FailClosedRuntimeError(
                    "G44-01 post-repair boundary identity mismatch"
                )
    return available


def _continuation_decision_artifact(
    *,
    continuation_id: str,
    continuation_status: str,
    checkpoint: dict[str, Any],
    resume_point: dict[str, Any],
    repair_evidence: dict[str, Any],
    workflow: dict[str, Any],
    diagnosis: dict[str, Any],
    continuity: dict[str, Any],
    verified_by: str,
    verified_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": (
            CONSTITUTIONAL_DEVELOPMENT_CONTINUATION_DECISION_ARTIFACT_V1
        ),
        "runtime_version": (
            CONSTITUTIONAL_DEVELOPMENT_CONTINUITY_MANAGER_RUNTIME_VERSION
        ),
        "continuation_id": continuation_id,
        "continuation_status": continuation_status,
        "checkpoint_id": checkpoint["checkpoint_id"],
        "checkpoint_hash": checkpoint["checkpoint_hash"],
        "resume_point_id": resume_point["resume_point_id"],
        "resume_point_hash": resume_point["resume_point_hash"],
        "repair_evidence_id": repair_evidence["repair_evidence_id"],
        "repair_evidence_hash": repair_evidence["repair_evidence_hash"],
        "post_repair_workflow_reference": workflow["workflow_id"],
        "post_repair_workflow_hash": workflow["workflow_hash"],
        "post_repair_workflow_artifact_hash": workflow["artifact_hash"],
        "post_repair_supervisor_diagnosis_reference": diagnosis[
            "diagnosis_id"
        ],
        "post_repair_supervisor_diagnosis_hash": diagnosis[
            "diagnosis_hash"
        ],
        "post_repair_supervisor_diagnosis_artifact_hash": diagnosis[
            "artifact_hash"
        ],
        "resume_from_boundary": deepcopy(
            resume_point["resume_boundary"]
        ),
        "preserved_stage_lineage": deepcopy(
            resume_point["preserved_stage_lineage"]
        ),
        "preserved_stage_lineage_hash": resume_point[
            "preserved_stage_lineage_hash"
        ],
        "verified_remaining_boundaries": deepcopy(
            resume_point["required_remaining_boundaries"]
        ),
        "verified_remaining_boundaries_hash": resume_point[
            "required_remaining_boundaries_hash"
        ],
        "required_revalidation_scope_hash": checkpoint[
            "required_revalidation_scope_hash"
        ],
        "continuity_verification": deepcopy(continuity),
        "continuity_verification_hash": continuity[
            "continuity_verification_hash"
        ],
        "next_workflow_action": (
            "CONTINUE_EXISTING_GOVERNED_WORKFLOW_FROM_CERTIFIED_RESUME_POINT"
        ),
        "continuation_authorized": True,
        "execution_authorized": False,
        "mutation_authorized": False,
        "validation_execution_authorized": False,
        "human_approval_required": True,
        "human_approval_recorded_by_manager": False,
        "verified_by": verified_by,
        "verified_at": verified_at,
        "replay_visible": True,
        "read_only": True,
        "non_authoritative_for_execution": True,
        "validation_executed": False,
        "repair_performed": False,
        "checkpoint_modified": False,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "failure_reason": failure_reason,
    }
    artifact["decision_hash"] = _decision_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_continuation_decision_artifact(
    *,
    continuation_id: Any,
    checkpoint_artifact: Any,
    resume_point_artifact: Any,
    external_repair_evidence_artifact: Any,
    post_repair_workflow_artifact: Any,
    post_repair_diagnosis_artifact: Any,
    verified_by: Any,
    verified_at: Any,
    failure_reason: str,
) -> dict[str, Any]:
    checkpoint = checkpoint_artifact if isinstance(checkpoint_artifact, dict) else {}
    resume = resume_point_artifact if isinstance(resume_point_artifact, dict) else {}
    repair = (
        external_repair_evidence_artifact
        if isinstance(external_repair_evidence_artifact, dict)
        else {}
    )
    workflow = post_repair_workflow_artifact if isinstance(post_repair_workflow_artifact, dict) else {}
    diagnosis = post_repair_diagnosis_artifact if isinstance(post_repair_diagnosis_artifact, dict) else {}
    artifact = {
        "artifact_type": (
            CONSTITUTIONAL_DEVELOPMENT_CONTINUATION_DECISION_ARTIFACT_V1
        ),
        "runtime_version": (
            CONSTITUTIONAL_DEVELOPMENT_CONTINUITY_MANAGER_RUNTIME_VERSION
        ),
        "continuation_id": _safe_string(continuation_id),
        "continuation_status": RESUME_FAILED_CLOSED,
        "checkpoint_id": _safe_string(checkpoint.get("checkpoint_id")),
        "checkpoint_hash": _safe_hash(checkpoint.get("checkpoint_hash")),
        "resume_point_id": _safe_string(resume.get("resume_point_id")),
        "resume_point_hash": _safe_hash(resume.get("resume_point_hash")),
        "repair_evidence_id": _safe_string(
            repair.get("repair_evidence_id")
        ),
        "repair_evidence_hash": _safe_hash(
            repair.get("repair_evidence_hash")
        ),
        "post_repair_workflow_reference": _safe_string(
            workflow.get("workflow_id")
        ),
        "post_repair_workflow_hash": _safe_hash(
            workflow.get("workflow_hash")
        ),
        "post_repair_workflow_artifact_hash": _safe_hash(
            workflow.get("artifact_hash")
        ),
        "post_repair_supervisor_diagnosis_reference": _safe_string(
            diagnosis.get("diagnosis_id")
        ),
        "post_repair_supervisor_diagnosis_hash": _safe_hash(
            diagnosis.get("diagnosis_hash")
        ),
        "post_repair_supervisor_diagnosis_artifact_hash": _safe_hash(
            diagnosis.get("artifact_hash")
        ),
        "resume_from_boundary": {},
        "preserved_stage_lineage": [],
        "preserved_stage_lineage_hash": replay_hash([]),
        "verified_remaining_boundaries": [],
        "verified_remaining_boundaries_hash": replay_hash([]),
        "required_revalidation_scope_hash": _safe_hash(
            checkpoint.get("required_revalidation_scope_hash")
        ),
        "continuity_verification": {
            "checkpoint_integrity_verified": False,
            "resume_point_integrity_verified": False,
            "continuation_prohibited": True,
        },
        "continuity_verification_hash": replay_hash(
            {
                "checkpoint_integrity_verified": False,
                "resume_point_integrity_verified": False,
                "continuation_prohibited": True,
            }
        ),
        "next_workflow_action": "BLOCKED_PENDING_VALID_CONTINUITY_EVIDENCE",
        "continuation_authorized": False,
        "execution_authorized": False,
        "mutation_authorized": False,
        "validation_execution_authorized": False,
        "human_approval_required": True,
        "human_approval_recorded_by_manager": False,
        "verified_by": _safe_string(verified_by),
        "verified_at": _safe_string(verified_at),
        "replay_visible": True,
        "read_only": True,
        "non_authoritative_for_execution": True,
        "validation_executed": False,
        "repair_performed": False,
        "checkpoint_modified": False,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "failure_reason": failure_reason,
    }
    artifact["decision_hash"] = _decision_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _verify_checkpoint_artifact(artifact: dict[str, Any]) -> None:
    if (
        artifact.get("artifact_type")
        != CONSTITUTIONAL_DEVELOPMENT_CHECKPOINT_ARTIFACT_V1
        or artifact.get("runtime_version")
        != CONSTITUTIONAL_DEVELOPMENT_CONTINUITY_MANAGER_RUNTIME_VERSION
    ):
        raise FailClosedRuntimeError("G44-01 checkpoint type mismatch")
    _verify_hash(
        artifact,
        "artifact_hash",
        "G44-01 checkpoint artifact hash mismatch",
    )
    if artifact.get("checkpoint_hash") != _checkpoint_hash(artifact):
        raise FailClosedRuntimeError(
            "G44-01 deterministic checkpoint hash mismatch"
        )
    if artifact.get("checkpoint_status") not in {
        CHECKPOINT_ACTIVE,
        FAILED_CLOSED,
    }:
        raise FailClosedRuntimeError("G44-01 checkpoint status invalid")
    _verify_common_boundaries(artifact, "checkpoint")
    if artifact["checkpoint_status"] == CHECKPOINT_ACTIVE:
        base = _checkpoint_state_base(artifact)
        expected_state_hash = replay_hash(base)
        if (
            artifact.get("checkpoint_state_hash") != expected_state_hash
            or artifact.get("checkpoint_id")
            != f"CDCM-CHECKPOINT-{expected_state_hash[7:31].upper()}"
            or artifact.get("checkpoint_immutable") is not True
            or artifact.get("failure_reason") is not None
        ):
            raise FailClosedRuntimeError(
                "G44-01 checkpoint identity or immutability invalid"
            )
        blocker_rank = artifact.get("workflow_position", {}).get(
            "blocked_boundary_rank"
        )
        if (
            blocker_rank not in BOUNDARY_BY_RANK
            or artifact["workflow_position"]["blocked_boundary"]
            != BOUNDARY_BY_RANK[blocker_rank]
            or artifact.get("certified_repair_boundary", {}).get(
                "boundary"
            )
            != BOUNDARY_BY_RANK[blocker_rank]
            or artifact.get("certified_repair_boundary_hash")
            != replay_hash(artifact["certified_repair_boundary"])
            or artifact.get("required_revalidation_scope_hash")
            != replay_hash(artifact["required_revalidation_scope"])
            or artifact.get("preserved_stage_lineage_hash")
            != replay_hash(artifact["preserved_stage_lineage"])
        ):
            raise FailClosedRuntimeError(
                "G44-01 checkpoint boundary lineage invalid"
            )
        _validate_preserved_prefix(
            artifact["preserved_stage_lineage"],
            blocker_rank,
        )
    elif not artifact.get("failure_reason"):
        raise FailClosedRuntimeError(
            "failed G44-01 checkpoint requires failure reason"
        )


def _verify_resume_point_artifact(artifact: dict[str, Any]) -> None:
    if (
        artifact.get("artifact_type")
        != CONSTITUTIONAL_DEVELOPMENT_RESUME_POINT_ARTIFACT_V1
        or artifact.get("runtime_version")
        != CONSTITUTIONAL_DEVELOPMENT_CONTINUITY_MANAGER_RUNTIME_VERSION
    ):
        raise FailClosedRuntimeError("G44-01 resume point type mismatch")
    _verify_hash(
        artifact,
        "artifact_hash",
        "G44-01 resume point artifact hash mismatch",
    )
    if artifact.get("resume_point_hash") != _resume_point_hash(artifact):
        raise FailClosedRuntimeError(
            "G44-01 deterministic resume point hash mismatch"
        )
    if artifact.get("resume_point_status") not in {
        RESUME_POINT_PENDING_EXTERNAL_REPAIR,
        FAILED_CLOSED,
    }:
        raise FailClosedRuntimeError("G44-01 resume point status invalid")
    _verify_common_boundaries(artifact, "resume point")
    if artifact["resume_point_status"] == RESUME_POINT_PENDING_EXTERNAL_REPAIR:
        resume_identity = {
            "checkpoint_id": artifact["checkpoint_id"],
            "checkpoint_hash": artifact["checkpoint_hash"],
            "workflow_hash": artifact["workflow_hash"],
            "replay_lineage_hash": artifact["replay_lineage_hash"],
            "repair_boundary_hash": artifact[
                "certified_repair_boundary_hash"
            ],
            "validation_scope_hash": artifact[
                "required_revalidation_scope_hash"
            ],
        }
        identity_hash = replay_hash(resume_identity)
        if (
            artifact.get("resume_point_id")
            != f"CDCM-RESUME-{identity_hash[7:31].upper()}"
            or artifact.get("checkpoint_preserved_unchanged") is not True
            or artifact.get("failure_reason") is not None
            or artifact.get("required_revalidation_scope_hash")
            != replay_hash(artifact["required_revalidation_scope"])
            or artifact.get("required_remaining_boundaries_hash")
            != replay_hash(artifact["required_remaining_boundaries"])
            or artifact.get("preserved_stage_lineage_hash")
            != replay_hash(artifact["preserved_stage_lineage"])
        ):
            raise FailClosedRuntimeError(
                "G44-01 resume point continuity fields invalid"
            )
        ranks = [
            item["boundary_rank"]
            for item in artifact["required_remaining_boundaries"]
        ]
        if ranks != artifact["must_not_skip_boundary_ranks"]:
            raise FailClosedRuntimeError(
                "G44-01 resume point skipped-stage contract invalid"
            )
    elif not artifact.get("failure_reason"):
        raise FailClosedRuntimeError(
            "failed G44-01 resume point requires failure reason"
        )


def _verify_repair_evidence_artifact(artifact: dict[str, Any]) -> None:
    if (
        artifact.get("artifact_type")
        != EXTERNAL_REPAIR_CONTINUITY_EVIDENCE_ARTIFACT_V1
        or artifact.get("runtime_version")
        != CONSTITUTIONAL_DEVELOPMENT_CONTINUITY_MANAGER_RUNTIME_VERSION
        or artifact.get("repair_evidence_status")
        != EXTERNAL_REPAIR_RECORDED
    ):
        raise FailClosedRuntimeError(
            "G44-01 external repair evidence type or status invalid"
        )
    _verify_hash(
        artifact,
        "artifact_hash",
        "G44-01 repair evidence artifact hash mismatch",
    )
    if artifact.get("repair_evidence_hash") != _repair_evidence_hash(
        artifact
    ):
        raise FailClosedRuntimeError(
            "G44-01 deterministic repair evidence hash mismatch"
        )
    if (
        artifact.get("repair_performed_externally") is not True
        or artifact.get("manager_performed_repair") is not False
        or artifact.get("manager_executed_validation") is not False
        or artifact.get("continuation_authorized") is not False
        or artifact.get("authority_flags") != AUTHORITY_FLAGS
        or artifact.get("read_only") is not True
        or artifact.get("replay_visible") is not True
    ):
        raise FailClosedRuntimeError(
            "G44-01 repair evidence boundary flags invalid"
        )
    refs = _validation_evidence_references(
        artifact.get("validation_evidence_references")
    )
    if (
        refs != artifact["validation_evidence_references"]
        or artifact.get("validation_evidence_count") != len(refs)
    ):
        raise FailClosedRuntimeError(
            "G44-01 validation evidence references invalid"
        )


def _verify_invalidation_artifact(artifact: dict[str, Any]) -> None:
    if (
        artifact.get("artifact_type")
        != CONSTITUTIONAL_CHECKPOINT_INVALIDATION_ARTIFACT_V1
        or artifact.get("runtime_version")
        != CONSTITUTIONAL_DEVELOPMENT_CONTINUITY_MANAGER_RUNTIME_VERSION
        or artifact.get("invalidation_status")
        not in {CHECKPOINT_INVALIDATED, FAILED_CLOSED}
    ):
        raise FailClosedRuntimeError(
            "G44-01 checkpoint invalidation type or status invalid"
        )
    _verify_hash(
        artifact,
        "artifact_hash",
        "G44-01 checkpoint invalidation artifact hash mismatch",
    )
    if artifact.get("invalidation_hash") != _invalidation_hash(artifact):
        raise FailClosedRuntimeError(
            "G44-01 checkpoint invalidation hash mismatch"
        )
    if (
        artifact.get("checkpoint_modified") is not False
        or artifact.get("resume_point_modified") is not False
        or artifact.get("continuation_authorized") is not False
        or artifact.get("authority_flags") != AUTHORITY_FLAGS
        or artifact.get("replay_visible") is not True
        or artifact.get("read_only") is not True
    ):
        raise FailClosedRuntimeError(
            "G44-01 invalidation boundary flags invalid"
        )
    if artifact["invalidation_status"] == CHECKPOINT_INVALIDATED:
        if (
            artifact.get("invalidation_reason")
            not in INVALIDATION_REASONS
            or artifact.get("failure_reason") is not None
        ):
            raise FailClosedRuntimeError(
                "G44-01 checkpoint invalidation reason invalid"
            )
    elif not artifact.get("failure_reason"):
        raise FailClosedRuntimeError(
            "failed G44-01 invalidation requires failure reason"
        )


def _verify_continuation_decision_artifact(
    artifact: dict[str, Any],
) -> None:
    if (
        artifact.get("artifact_type")
        != CONSTITUTIONAL_DEVELOPMENT_CONTINUATION_DECISION_ARTIFACT_V1
        or artifact.get("runtime_version")
        != CONSTITUTIONAL_DEVELOPMENT_CONTINUITY_MANAGER_RUNTIME_VERSION
        or artifact.get("continuation_status")
        not in {CONTINUATION_AUTHORIZED, RESUME_FAILED_CLOSED}
    ):
        raise FailClosedRuntimeError(
            "G44-01 continuation decision type or status invalid"
        )
    _verify_hash(
        artifact,
        "artifact_hash",
        "G44-01 continuation decision artifact hash mismatch",
    )
    if artifact.get("decision_hash") != _decision_hash(artifact):
        raise FailClosedRuntimeError(
            "G44-01 deterministic continuation decision hash mismatch"
        )
    if (
        artifact.get("execution_authorized") is not False
        or artifact.get("mutation_authorized") is not False
        or artifact.get("validation_execution_authorized") is not False
        or artifact.get("human_approval_required") is not True
        or artifact.get("human_approval_recorded_by_manager") is not False
        or artifact.get("validation_executed") is not False
        or artifact.get("repair_performed") is not False
        or artifact.get("checkpoint_modified") is not False
        or artifact.get("authority_flags") != AUTHORITY_FLAGS
        or artifact.get("replay_visible") is not True
        or artifact.get("read_only") is not True
        or artifact.get("non_authoritative_for_execution") is not True
    ):
        raise FailClosedRuntimeError(
            "G44-01 continuation authority boundary invalid"
        )
    if artifact["continuation_status"] == CONTINUATION_AUTHORIZED:
        continuity = artifact.get("continuity_verification")
        if (
            artifact.get("continuation_authorized") is not True
            or artifact.get("failure_reason") is not None
            or not isinstance(continuity, dict)
            or any(
                continuity.get(field) is not True
                for field in (
                    "checkpoint_integrity_verified",
                    "resume_point_integrity_verified",
                    "original_replay_lineage_verified",
                    "preserved_stage_lineage_verified",
                    "repair_boundary_compliance_verified",
                    "affected_capability_continuity_verified",
                    "required_validation_evidence_verified",
                    "supervisor_diagnosis_consistency_verified",
                    "required_remaining_stages_verified",
                )
            )
            or artifact.get("continuity_verification_hash")
            != replay_hash(
                {
                    key: value
                    for key, value in continuity.items()
                    if key != "continuity_verification_hash"
                }
            )
        ):
            raise FailClosedRuntimeError(
                "G44-01 continuation verification incomplete"
            )
    elif (
        artifact.get("continuation_authorized") is not False
        or not artifact.get("failure_reason")
    ):
        raise FailClosedRuntimeError(
            "failed G44-01 continuation decision invalid"
        )


def _verify_common_boundaries(
    artifact: dict[str, Any],
    label: str,
) -> None:
    if (
        artifact.get("repair_performed") is not False
        or artifact.get("validation_executed") is not False
        or artifact.get("continuation_authorized") is not False
        or artifact.get("human_approval_required") is not True
        or artifact.get("replay_visible") is not True
        or artifact.get("read_only") is not True
        or artifact.get("authority_flags") != AUTHORITY_FLAGS
    ):
        raise FailClosedRuntimeError(
            f"G44-01 {label} boundary flags invalid"
        )


def _checkpoint_state_base(artifact: dict[str, Any]) -> dict[str, Any]:
    fields = (
        "workflow_position",
        "workflow_reference",
        "workflow_hash",
        "workflow_artifact_hash",
        "workflow_status",
        "replay_lineage",
        "replay_lineage_hash",
        "stage_lineage",
        "stage_lineage_hash",
        "ive_planning_bundle_reference",
        "ive_planning_bundle_hash",
        "certified_repair_boundary",
        "certified_repair_boundary_hash",
        "required_revalidation_scope",
        "required_revalidation_scope_hash",
        "affected_capability_identifiers",
        "affected_capability_identifiers_hash",
        "supervisor_diagnosis_reference",
        "supervisor_diagnosis_hash",
        "supervisor_diagnosis_artifact_hash",
        "supervisor_diagnosis_evidence_hash",
        "preserved_stage_lineage",
        "preserved_stage_lineage_hash",
        "created_by",
        "created_at",
    )
    return {field: deepcopy(artifact[field]) for field in fields}


def _validate_checkpoint_source_bindings(
    *,
    workflow: dict[str, Any],
    workflow_reference: str,
    workflow_hash: str,
    workflow_artifact_hash: str,
    diagnosis: dict[str, Any],
    diagnosis_reference: str,
    diagnosis_hash: str,
    diagnosis_artifact_hash: str,
) -> None:
    if (
        workflow["workflow_id"]
        != _require_string(workflow_reference, "workflow_reference")
        or workflow["workflow_hash"]
        != _require_hash(workflow_hash, "workflow_hash")
        or workflow["artifact_hash"]
        != _require_hash(workflow_artifact_hash, "workflow_artifact_hash")
        or diagnosis["diagnosis_id"]
        != _require_string(diagnosis_reference, "diagnosis_reference")
        or diagnosis["diagnosis_hash"]
        != _require_hash(diagnosis_hash, "diagnosis_hash")
        or diagnosis["artifact_hash"]
        != _require_hash(
            diagnosis_artifact_hash,
            "diagnosis_artifact_hash",
        )
        or diagnosis["workflow_reference"] != workflow["workflow_id"]
        or diagnosis["workflow_hash"] != workflow["workflow_hash"]
        or diagnosis["workflow_artifact_hash"] != workflow["artifact_hash"]
        or diagnosis["diagnosis_status"] != BLOCKER_DIAGNOSED
    ):
        raise FailClosedRuntimeError(
            "G44-01 checkpoint requires one exact diagnosed workflow blocker"
        )


def _validate_post_repair_bindings(
    *,
    workflow: dict[str, Any],
    workflow_reference: str,
    workflow_hash: str,
    workflow_artifact_hash: str,
    diagnosis: dict[str, Any],
    diagnosis_reference: str,
    diagnosis_hash: str,
    diagnosis_artifact_hash: str,
) -> None:
    if (
        workflow["workflow_id"]
        != _require_string(workflow_reference, "post_workflow_reference")
        or workflow["workflow_hash"]
        != _require_hash(workflow_hash, "post_workflow_hash")
        or workflow["artifact_hash"]
        != _require_hash(
            workflow_artifact_hash,
            "post_workflow_artifact_hash",
        )
        or diagnosis["diagnosis_id"]
        != _require_string(
            diagnosis_reference,
            "post_diagnosis_reference",
        )
        or diagnosis["diagnosis_hash"]
        != _require_hash(diagnosis_hash, "post_diagnosis_hash")
        or diagnosis["artifact_hash"]
        != _require_hash(
            diagnosis_artifact_hash,
            "post_diagnosis_artifact_hash",
        )
        or diagnosis["workflow_reference"] != workflow["workflow_id"]
        or diagnosis["workflow_hash"] != workflow["workflow_hash"]
        or diagnosis["workflow_artifact_hash"] != workflow["artifact_hash"]
    ):
        raise FailClosedRuntimeError(
            "G44-01 post-repair workflow or Supervisor binding mismatch"
        )


def _validate_source_reconstruction(
    workflow: dict[str, Any],
    workflow_reconstruction: dict[str, Any],
    diagnosis: dict[str, Any],
    supervisor_reconstruction: dict[str, Any],
) -> None:
    if (
        workflow_reconstruction["workflow_id"] != workflow["workflow_id"]
        or workflow_reconstruction["workflow_hash"]
        != workflow["workflow_hash"]
        or workflow_reconstruction["artifact_hash"]
        != workflow["artifact_hash"]
        or supervisor_reconstruction["diagnosis_id"]
        != diagnosis["diagnosis_id"]
        or supervisor_reconstruction["diagnosis_hash"]
        != diagnosis["diagnosis_hash"]
        or supervisor_reconstruction["artifact_hash"]
        != diagnosis["artifact_hash"]
    ):
        raise FailClosedRuntimeError(
            "G44-01 source replay reconstruction mismatch"
        )


def _load_supervisor_diagnosis_evidence(
    supervisor_replay_dir: Path,
) -> dict[str, Any]:
    wrapper = load_json(
        supervisor_replay_dir / "001_diagnosis_evidence_recorded.json"
    )
    _verify_wrapper(
        wrapper,
        1,
        "diagnosis_evidence_recorded",
        "Supervisor",
    )
    artifact = wrapper.get("artifact")
    if (
        not isinstance(artifact, dict)
        or artifact.get("artifact_type")
        != CONSTITUTIONAL_DEVELOPMENT_DIAGNOSIS_EVIDENCE_ARTIFACT_V1
    ):
        raise FailClosedRuntimeError(
            "G44-01 Supervisor diagnosis evidence unavailable"
        )
    _verify_hash(
        artifact,
        "artifact_hash",
        "G44-01 Supervisor diagnosis evidence artifact hash mismatch",
    )
    body = deepcopy(artifact)
    body.pop("artifact_hash")
    evidence_hash = body.pop("evidence_hash", None)
    if evidence_hash != replay_hash(body):
        raise FailClosedRuntimeError(
            "G44-01 Supervisor diagnosis evidence hash mismatch"
        )
    observations = artifact.get("boundary_observations")
    if not isinstance(observations, list):
        raise FailClosedRuntimeError(
            "G44-01 Supervisor boundary observations unavailable"
        )
    for item in observations:
        _verify_hash(
            item,
            "observation_hash",
            "G44-01 Supervisor observation hash mismatch",
        )
    return deepcopy(artifact)


def _validate_preserved_prefix(
    preserved: list[dict[str, Any]],
    blocker_rank: int,
) -> None:
    if not isinstance(preserved, list):
        raise FailClosedRuntimeError(
            "G44-01 preserved stage lineage must be a list"
        )
    ranks = [item.get("boundary_rank") for item in preserved]
    if ranks != sorted(set(ranks)) or any(
        not isinstance(rank, int) or rank >= blocker_rank for rank in ranks
    ):
        raise FailClosedRuntimeError(
            "G44-01 preserved stage lineage is not a deterministic prefix"
        )
    for item in preserved:
        _verify_hash(
            item,
            "observation_hash",
            "G44-01 preserved stage observation hash mismatch",
        )


def _validate_checkpoint_resume_binding(
    checkpoint: dict[str, Any],
    resume_point: dict[str, Any],
) -> None:
    blocker_rank = checkpoint["workflow_position"]["blocked_boundary_rank"]
    expected_remaining = [
        {
            "boundary_rank": rank,
            "boundary": boundary,
            "required_after_repair": True,
        }
        for rank, boundary in CANONICAL_WORKFLOW_BOUNDARIES
        if rank >= blocker_rank
    ]
    expected_preserved_ranks = [
        item["boundary_rank"]
        for item in checkpoint["preserved_stage_lineage"]
    ]
    if (
        checkpoint["checkpoint_status"] != CHECKPOINT_ACTIVE
        or resume_point["resume_point_status"]
        != RESUME_POINT_PENDING_EXTERNAL_REPAIR
        or resume_point["checkpoint_id"] != checkpoint["checkpoint_id"]
        or resume_point["checkpoint_hash"] != checkpoint["checkpoint_hash"]
        or resume_point["workflow_hash"] != checkpoint["workflow_hash"]
        or resume_point["workflow_artifact_hash"]
        != checkpoint["workflow_artifact_hash"]
        or resume_point["exact_workflow_state_hash"]
        != checkpoint["checkpoint_state_hash"]
        or resume_point["replay_lineage_hash"]
        != checkpoint["replay_lineage_hash"]
        or resume_point["preserved_stage_lineage"]
        != checkpoint["preserved_stage_lineage"]
        or resume_point["certified_repair_boundary_hash"]
        != checkpoint["certified_repair_boundary_hash"]
        or resume_point["certified_repair_boundary"]
        != checkpoint["certified_repair_boundary"]
        or resume_point["required_revalidation_scope_hash"]
        != checkpoint["required_revalidation_scope_hash"]
        or resume_point["required_revalidation_scope"]
        != checkpoint["required_revalidation_scope"]
        or resume_point["preserved_stage_lineage_hash"]
        != checkpoint["preserved_stage_lineage_hash"]
        or resume_point["resume_boundary"] != checkpoint["workflow_position"]
        or resume_point["affected_capability_identifiers"]
        != checkpoint["affected_capability_identifiers"]
        or resume_point["required_remaining_boundaries"]
        != expected_remaining
        or resume_point["must_not_skip_boundary_ranks"]
        != [item["boundary_rank"] for item in expected_remaining]
        or resume_point["must_not_repeat_boundary_ranks"]
        != expected_preserved_ranks
    ):
        raise FailClosedRuntimeError(
            "G44-01 checkpoint and resume point binding mismatch"
        )


def _validate_checkpoint_replay_bindings(
    checkpoint: dict[str, Any],
    resume_point: dict[str, Any],
    workflow: dict[str, Any],
    diagnosis: dict[str, Any],
) -> None:
    _validate_checkpoint_resume_binding(checkpoint, resume_point)
    if (
        checkpoint["workflow_reference"] != workflow["workflow_id"]
        or checkpoint["workflow_hash"] != workflow["workflow_hash"]
        or checkpoint["workflow_artifact_hash"] != workflow["artifact_hash"]
        or checkpoint["supervisor_diagnosis_reference"]
        != diagnosis["diagnosis_id"]
        or checkpoint["supervisor_diagnosis_hash"]
        != diagnosis["diagnosis_hash"]
        or checkpoint["supervisor_diagnosis_artifact_hash"]
        != diagnosis["artifact_hash"]
    ):
        raise FailClosedRuntimeError(
            "G44-01 checkpoint replay source binding mismatch"
        )


def _validate_continuation_replay_bindings(
    decision: dict[str, Any],
    checkpoint: dict[str, Any],
    resume_point: dict[str, Any],
    repair_evidence: dict[str, Any],
    workflow: dict[str, Any],
    diagnosis: dict[str, Any],
) -> None:
    _validate_checkpoint_resume_binding(checkpoint, resume_point)
    if (
        decision["checkpoint_id"] != checkpoint["checkpoint_id"]
        or decision["checkpoint_hash"] != checkpoint["checkpoint_hash"]
        or decision["resume_point_id"] != resume_point["resume_point_id"]
        or decision["resume_point_hash"]
        != resume_point["resume_point_hash"]
        or decision["repair_evidence_id"]
        != repair_evidence["repair_evidence_id"]
        or decision["repair_evidence_hash"]
        != repair_evidence["repair_evidence_hash"]
        or decision["post_repair_workflow_hash"] != workflow["workflow_hash"]
        or decision["post_repair_supervisor_diagnosis_hash"]
        != diagnosis["diagnosis_hash"]
    ):
        raise FailClosedRuntimeError(
            "G44-01 continuation replay binding mismatch"
        )


def _failed_checkpoint_artifact(
    *,
    workflow_artifact: Any,
    diagnosis_artifact: Any,
    created_by: Any,
    created_at: Any,
    failure_reason: str,
) -> dict[str, Any]:
    workflow = workflow_artifact if isinstance(workflow_artifact, dict) else {}
    diagnosis = diagnosis_artifact if isinstance(diagnosis_artifact, dict) else {}
    artifact = {
        "artifact_type": CONSTITUTIONAL_DEVELOPMENT_CHECKPOINT_ARTIFACT_V1,
        "runtime_version": (
            CONSTITUTIONAL_DEVELOPMENT_CONTINUITY_MANAGER_RUNTIME_VERSION
        ),
        "checkpoint_id": "UNAVAILABLE",
        "checkpoint_status": FAILED_CLOSED,
        "workflow_position": {},
        "workflow_reference": _safe_string(workflow.get("workflow_id")),
        "workflow_hash": _safe_hash(workflow.get("workflow_hash")),
        "workflow_artifact_hash": _safe_hash(
            workflow.get("artifact_hash")
        ),
        "workflow_status": _safe_string(workflow.get("workflow_status")),
        "replay_lineage": {},
        "replay_lineage_hash": replay_hash({}),
        "stage_lineage": [],
        "stage_lineage_hash": replay_hash([]),
        "ive_planning_bundle_reference": "UNAVAILABLE",
        "ive_planning_bundle_hash": replay_hash({"unavailable": "IVE_4"}),
        "certified_repair_boundary": {},
        "certified_repair_boundary_hash": replay_hash({}),
        "required_revalidation_scope": {},
        "required_revalidation_scope_hash": replay_hash({}),
        "affected_capability_identifiers": [],
        "affected_capability_identifiers_hash": replay_hash([]),
        "supervisor_diagnosis_reference": _safe_string(
            diagnosis.get("diagnosis_id")
        ),
        "supervisor_diagnosis_hash": _safe_hash(
            diagnosis.get("diagnosis_hash")
        ),
        "supervisor_diagnosis_artifact_hash": _safe_hash(
            diagnosis.get("artifact_hash")
        ),
        "supervisor_diagnosis_evidence_hash": _safe_hash(
            diagnosis.get("diagnosis_evidence_hash")
        ),
        "preserved_stage_lineage": [],
        "preserved_stage_lineage_hash": replay_hash([]),
        "created_by": _safe_string(created_by),
        "created_at": _safe_string(created_at),
        "checkpoint_state_hash": replay_hash(
            {"failed_closed": failure_reason}
        ),
        "checkpoint_immutable": True,
        "repair_performed": False,
        "validation_executed": False,
        "continuation_authorized": False,
        "human_approval_required": True,
        "replay_visible": True,
        "read_only": True,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "failure_reason": failure_reason,
    }
    artifact["checkpoint_hash"] = _checkpoint_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_resume_point_artifact(
    *,
    checkpoint: dict[str, Any],
    created_by: Any,
    created_at: Any,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": (
            CONSTITUTIONAL_DEVELOPMENT_RESUME_POINT_ARTIFACT_V1
        ),
        "runtime_version": (
            CONSTITUTIONAL_DEVELOPMENT_CONTINUITY_MANAGER_RUNTIME_VERSION
        ),
        "resume_point_id": "UNAVAILABLE",
        "resume_point_status": FAILED_CLOSED,
        "checkpoint_id": checkpoint["checkpoint_id"],
        "checkpoint_hash": checkpoint["checkpoint_hash"],
        "workflow_reference": checkpoint["workflow_reference"],
        "workflow_hash": checkpoint["workflow_hash"],
        "workflow_artifact_hash": checkpoint["workflow_artifact_hash"],
        "exact_workflow_state_hash": checkpoint["checkpoint_state_hash"],
        "replay_lineage_hash": checkpoint["replay_lineage_hash"],
        "preserved_stage_lineage": [],
        "preserved_stage_lineage_hash": replay_hash([]),
        "resume_boundary": {},
        "certified_repair_boundary": {},
        "certified_repair_boundary_hash": replay_hash({}),
        "required_revalidation_scope": {},
        "required_revalidation_scope_hash": replay_hash({}),
        "required_remaining_boundaries": [],
        "required_remaining_boundaries_hash": replay_hash([]),
        "must_not_repeat_boundary_ranks": [],
        "must_not_skip_boundary_ranks": [],
        "affected_capability_identifiers": [],
        "created_by": _safe_string(created_by),
        "created_at": _safe_string(created_at),
        "checkpoint_preserved_unchanged": True,
        "repair_performed": False,
        "validation_executed": False,
        "continuation_authorized": False,
        "human_approval_required": True,
        "replay_visible": True,
        "read_only": True,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "failure_reason": failure_reason,
    }
    artifact["resume_point_hash"] = _resume_point_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _invalidation_artifact(
    *,
    invalidation_id: str,
    invalidation_status: str,
    checkpoint: dict[str, Any],
    resume_point: dict[str, Any],
    invalidation_reason: str,
    superseding_evidence_reference: str,
    superseding_evidence_hash: str,
    invalidated_by: str,
    invalidated_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": CONSTITUTIONAL_CHECKPOINT_INVALIDATION_ARTIFACT_V1,
        "runtime_version": (
            CONSTITUTIONAL_DEVELOPMENT_CONTINUITY_MANAGER_RUNTIME_VERSION
        ),
        "invalidation_id": invalidation_id,
        "invalidation_status": invalidation_status,
        "checkpoint_id": checkpoint["checkpoint_id"],
        "checkpoint_hash": checkpoint["checkpoint_hash"],
        "resume_point_id": resume_point["resume_point_id"],
        "resume_point_hash": resume_point["resume_point_hash"],
        "invalidation_reason": invalidation_reason,
        "superseding_evidence_reference": superseding_evidence_reference,
        "superseding_evidence_hash": superseding_evidence_hash,
        "invalidated_by": invalidated_by,
        "invalidated_at": invalidated_at,
        "checkpoint_modified": False,
        "resume_point_modified": False,
        "continuation_authorized": False,
        "replay_visible": True,
        "read_only": True,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "failure_reason": failure_reason,
    }
    artifact["invalidation_hash"] = _invalidation_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_invalidation_artifact(
    *,
    invalidation_id: Any,
    checkpoint_artifact: Any,
    resume_point_artifact: Any,
    invalidation_reason: Any,
    invalidated_by: Any,
    invalidated_at: Any,
    failure_reason: str,
) -> dict[str, Any]:
    checkpoint = checkpoint_artifact if isinstance(checkpoint_artifact, dict) else {}
    resume_point = (
        resume_point_artifact
        if isinstance(resume_point_artifact, dict)
        else {}
    )
    artifact = {
        "artifact_type": CONSTITUTIONAL_CHECKPOINT_INVALIDATION_ARTIFACT_V1,
        "runtime_version": (
            CONSTITUTIONAL_DEVELOPMENT_CONTINUITY_MANAGER_RUNTIME_VERSION
        ),
        "invalidation_id": _safe_string(invalidation_id),
        "invalidation_status": FAILED_CLOSED,
        "checkpoint_id": _safe_string(checkpoint.get("checkpoint_id")),
        "checkpoint_hash": _safe_hash(checkpoint.get("checkpoint_hash")),
        "resume_point_id": _safe_string(
            resume_point.get("resume_point_id")
        ),
        "resume_point_hash": _safe_hash(
            resume_point.get("resume_point_hash")
        ),
        "invalidation_reason": _safe_string(invalidation_reason),
        "superseding_evidence_reference": "UNAVAILABLE",
        "superseding_evidence_hash": replay_hash(
            {"unavailable": "superseding_evidence"}
        ),
        "invalidated_by": _safe_string(invalidated_by),
        "invalidated_at": _safe_string(invalidated_at),
        "checkpoint_modified": False,
        "resume_point_modified": False,
        "continuation_authorized": False,
        "replay_visible": True,
        "read_only": True,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "failure_reason": failure_reason,
    }
    artifact["invalidation_hash"] = _invalidation_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _validation_evidence_references(
    references: Any,
) -> list[dict[str, Any]]:
    if not isinstance(references, list):
        raise FailClosedRuntimeError(
            "G44-01 validation evidence references must be a list"
        )
    normalized: list[dict[str, Any]] = []
    for item in references:
        if not isinstance(item, dict):
            raise FailClosedRuntimeError(
                "G44-01 validation evidence reference invalid"
            )
        base = {
            "validation_evidence_id": _require_string(
                item.get("validation_evidence_id"),
                "validation_evidence_id",
            ),
            "validation_artifact_hash": _require_hash(
                item.get("validation_artifact_hash"),
                "validation_artifact_hash",
            ),
            "validation_status": _require_string(
                item.get("validation_status"),
                "validation_status",
            ),
            "validated_scope_hash": _require_hash(
                item.get("validated_scope_hash"),
                "validated_scope_hash",
            ),
        }
        if base["validation_status"] != "VALIDATION_PASSED":
            raise FailClosedRuntimeError(
                "G44-01 validation evidence is not passing"
            )
        evidence_hash = item.get("evidence_hash")
        if evidence_hash != replay_hash(base):
            raise FailClosedRuntimeError(
                "G44-01 validation evidence reference hash mismatch"
            )
        normalized.append({**base, "evidence_hash": evidence_hash})
    if len({item["validation_evidence_id"] for item in normalized}) != len(
        normalized
    ):
        raise FailClosedRuntimeError(
            "G44-01 validation evidence references contain duplicates"
        )
    return normalized


def _checkpoint_capture(
    checkpoint: dict[str, Any],
    resume_point: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "runtime_version": (
            CONSTITUTIONAL_DEVELOPMENT_CONTINUITY_MANAGER_RUNTIME_VERSION
        ),
        "constitutional_development_checkpoint_artifact": deepcopy(
            checkpoint
        ),
        "constitutional_development_resume_point_artifact": deepcopy(
            resume_point
        ),
        "checkpoint_id": checkpoint["checkpoint_id"],
        "checkpoint_status": checkpoint["checkpoint_status"],
        "checkpoint_hash": checkpoint["checkpoint_hash"],
        "resume_point_id": resume_point["resume_point_id"],
        "resume_point_status": resume_point["resume_point_status"],
        "resume_point_hash": resume_point["resume_point_hash"],
        "replay_reference": str(replay_path),
        "fail_closed": checkpoint["checkpoint_status"] == FAILED_CLOSED,
        "failure_reason": checkpoint["failure_reason"],
        "continuation_authorized": False,
        "validation_executed": False,
        "repair_performed": False,
        "checkpoint_modified": False,
    }
    capture["capture_hash"] = replay_hash(capture)
    return capture


def _continuation_capture(
    decision: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "runtime_version": (
            CONSTITUTIONAL_DEVELOPMENT_CONTINUITY_MANAGER_RUNTIME_VERSION
        ),
        "constitutional_development_continuation_decision_artifact": deepcopy(
            decision
        ),
        "continuation_id": decision["continuation_id"],
        "continuation_status": decision["continuation_status"],
        "decision_hash": decision["decision_hash"],
        "replay_reference": str(replay_path),
        "fail_closed": decision["continuation_status"] == RESUME_FAILED_CLOSED,
        "failure_reason": decision["failure_reason"],
        "continuation_authorized": decision["continuation_authorized"],
        "execution_authorized": False,
        "validation_executed": False,
        "repair_performed": False,
        "checkpoint_modified": False,
        "human_approval_required": True,
    }
    capture["capture_hash"] = replay_hash(capture)
    return capture


def _persist_checkpoint_replay(
    replay_path: Path,
    workflow: dict[str, Any] | None,
    diagnosis: dict[str, Any] | None,
    checkpoint: dict[str, Any],
    resume_point: dict[str, Any],
) -> None:
    artifacts = (
        workflow or _unavailable_snapshot("G42_WORKFLOW", checkpoint),
        diagnosis or _unavailable_snapshot("G43_DIAGNOSIS", checkpoint),
        checkpoint,
        resume_point,
    )
    _persist_wrappers(replay_path, CHECKPOINT_REPLAY_STEPS, artifacts)


def _persist_resume_replay(
    replay_path: Path,
    checkpoint: dict[str, Any] | None,
    resume_point: dict[str, Any] | None,
    repair_evidence: dict[str, Any] | None,
    workflow: dict[str, Any] | None,
    diagnosis: dict[str, Any] | None,
    decision: dict[str, Any],
) -> None:
    artifacts = (
        checkpoint or _unavailable_snapshot("CHECKPOINT", decision),
        resume_point or _unavailable_snapshot("RESUME_POINT", decision),
        repair_evidence
        or _unavailable_snapshot("EXTERNAL_REPAIR_EVIDENCE", decision),
        workflow
        or _unavailable_snapshot("POST_REPAIR_G42_WORKFLOW", decision),
        diagnosis
        or _unavailable_snapshot("POST_REPAIR_G43_DIAGNOSIS", decision),
        decision,
    )
    _persist_wrappers(replay_path, RESUME_REPLAY_STEPS, artifacts)


def _persist_single_replay(
    replay_path: Path,
    step: str,
    artifact: dict[str, Any],
) -> None:
    _persist_wrappers(replay_path, (step,), (artifact,))


def _persist_wrappers(
    replay_path: Path,
    steps: tuple[str, ...],
    artifacts: tuple[dict[str, Any], ...],
) -> None:
    try:
        for index, (step, artifact) in enumerate(zip(steps, artifacts)):
            wrapper = {
                "replay_index": index,
                "replay_step": step,
                "artifact": deepcopy(artifact),
            }
            wrapper["replay_hash"] = replay_hash(wrapper)
            write_json_immutable(
                replay_path / f"{index:03d}_{step}.json",
                wrapper,
            )
    except Exception:
        return


def _unavailable_snapshot(
    boundary: str,
    owner: dict[str, Any],
) -> dict[str, Any]:
    artifact = {
        "artifact_type": f"{boundary}_UNAVAILABLE_V1",
        "boundary": boundary,
        "owner_reference": _safe_string(
            owner.get("checkpoint_id")
            or owner.get("continuation_id")
        ),
        "source_available": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _ensure_replay_available(
    replay_path: Path,
    steps: tuple[str, ...],
) -> None:
    if any(
        (replay_path / f"{index:03d}_{step}.json").exists()
        for index, step in enumerate(steps)
    ):
        raise FailClosedRuntimeError(
            "G44-01 failed closed: replay artifact already exists"
        )


def _ensure_single_replay_available(
    replay_path: Path,
    step: str,
) -> None:
    _ensure_replay_available(replay_path, (step,))


def _verify_wrapper(
    wrapper: dict[str, Any],
    index: int,
    step: str,
    owner: str,
) -> None:
    if (
        wrapper.get("replay_index") != index
        or wrapper.get("replay_step") != step
    ):
        raise FailClosedRuntimeError(
            f"G44-01 {owner} replay ordering mismatch"
        )
    _verify_hash(
        wrapper,
        "replay_hash",
        f"G44-01 {owner} replay hash mismatch",
    )


def _verify_hash(
    value: dict[str, Any],
    field: str,
    message: str,
) -> None:
    actual = value.get(field)
    if not isinstance(actual, str) or not actual.startswith("sha256:"):
        raise FailClosedRuntimeError(message)
    expected = deepcopy(value)
    expected.pop(field, None)
    if replay_hash(expected) != actual:
        raise FailClosedRuntimeError(message)


def _checkpoint_hash(artifact: dict[str, Any]) -> str:
    return _named_artifact_hash(artifact, "checkpoint_hash")


def _resume_point_hash(artifact: dict[str, Any]) -> str:
    return _named_artifact_hash(artifact, "resume_point_hash")


def _repair_evidence_hash(artifact: dict[str, Any]) -> str:
    return _named_artifact_hash(artifact, "repair_evidence_hash")


def _invalidation_hash(artifact: dict[str, Any]) -> str:
    return _named_artifact_hash(artifact, "invalidation_hash")


def _decision_hash(artifact: dict[str, Any]) -> str:
    return _named_artifact_hash(artifact, "decision_hash")


def _named_artifact_hash(
    artifact: dict[str, Any],
    field: str,
) -> str:
    candidate = deepcopy(artifact)
    candidate.pop("artifact_hash", None)
    candidate.pop(field, None)
    return replay_hash(candidate)


def _string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise FailClosedRuntimeError(f"G44-01 requires {field}")
    normalized = [_require_string(item, field) for item in value]
    if len(set(normalized)) != len(normalized):
        raise FailClosedRuntimeError(
            f"G44-01 {field} contains duplicates"
        )
    return normalized


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"G44-01 requires {field}")
    return value


def _require_hash(value: Any, field: str) -> str:
    text = _require_string(value, field)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(
            f"G44-01 requires canonical {field}"
        )
    return text


def _safe_string(value: Any) -> str:
    return value if isinstance(value, str) and value.strip() else "UNAVAILABLE"


def _safe_hash(value: Any) -> str:
    if isinstance(value, str) and value.startswith("sha256:"):
        return value
    return replay_hash({"unavailable": str(value)})


def _failure_reason(exc: Exception) -> str:
    text = str(exc).strip()
    return text or exc.__class__.__name__
