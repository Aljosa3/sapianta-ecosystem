"""Read-only constitutional supervision of the certified G42 workflow."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

from aigol.runtime.constitutional_development_workflow_integration_runtime import (
    CONSTITUTIONAL_DEVELOPMENT_VALIDATION_WORKFLOW_ARTIFACT_V1,
    DEVELOPMENT_VALIDATION_PLANNING_READY,
    FAILED_CLOSED as G42_FAILED_CLOSED,
    reconstruct_constitutional_development_validation_workflow_replay,
    validate_constitutional_development_validation_workflow_artifact,
)
from aigol.runtime.intelligent_validation_engine_v0 import (
    FAILED_CLOSED as IVE_0_FAILED_CLOSED,
    INTELLIGENT_VALIDATION_PLAN_ARTIFACT_V1,
    validate_intelligent_validation_plan_artifact,
)
from aigol.runtime.intelligent_validation_engine_v1 import (
    FAILED_CLOSED as IVE_1_FAILED_CLOSED,
    SEMANTIC_VALIDATION_SELECTION_ARTIFACT_V1,
    validate_semantic_validation_selection_artifact,
)
from aigol.runtime.intelligent_validation_engine_v2 import (
    FAILED_CLOSED as IVE_2_FAILED_CLOSED,
    PARALLEL_VALIDATION_SCHEDULE_ARTIFACT_V1,
    validate_parallel_validation_schedule_artifact,
)
from aigol.runtime.intelligent_validation_engine_v3 import (
    FAILED_CLOSED as IVE_3_FAILED_CLOSED,
    VALIDATION_FAILURE_ANALYSIS_ARTIFACT_V1,
    validate_validation_failure_analysis_artifact,
)
from aigol.runtime.intelligent_validation_entry_integration_runtime import (
    FAILED_CLOSED as G38_FAILED_CLOSED,
    INTELLIGENT_VALIDATION_PLANNING_ENTRY_ARTIFACT_V1,
    validate_intelligent_validation_planning_entry_artifact,
)
from aigol.runtime.intelligent_validation_orchestrator_v4 import (
    FAILED_CLOSED as IVE_4_FAILED_CLOSED,
    REPLAY_STEPS as IVE_4_REPLAY_STEPS,
    UNIFIED_VALIDATION_PLANNING_BUNDLE_ARTIFACT_V1,
    reconstruct_intelligent_validation_orchestration_replay,
    validate_unified_validation_planning_bundle_artifact,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_certification_registry import (
    lookup_platform_capability_certification,
)
from aigol.runtime.platform_change_normalization_runtime import (
    NORMALIZED_CHANGE_ARTIFACT_V1,
    validate_normalized_change_artifact,
)
from aigol.runtime.transport.serialization import (
    load_json,
    replay_hash,
    write_json_immutable,
)


CONSTITUTIONAL_DEVELOPMENT_SUPERVISOR_RUNTIME_VERSION = (
    "G43_01_CONSTITUTIONAL_DEVELOPMENT_SUPERVISOR_RUNTIME_V1"
)
CONSTITUTIONAL_DEVELOPMENT_DIAGNOSIS_EVIDENCE_ARTIFACT_V1 = (
    "CONSTITUTIONAL_DEVELOPMENT_DIAGNOSIS_EVIDENCE_ARTIFACT_V1"
)
CONSTITUTIONAL_DEVELOPMENT_SUPERVISOR_DIAGNOSIS_ARTIFACT_V1 = (
    "CONSTITUTIONAL_DEVELOPMENT_SUPERVISOR_DIAGNOSIS_ARTIFACT_V1"
)
WORKFLOW_HEALTHY = "WORKFLOW_HEALTHY"
BLOCKER_DIAGNOSED = "BLOCKER_DIAGNOSED"
FAILED_CLOSED = "FAILED_CLOSED"
NO_CONSTITUTIONAL_BLOCKER = "NO_CONSTITUTIONAL_BLOCKER_IDENTIFIED"
REPLAY_STEPS = (
    "constitutional_development_workflow_bound",
    "diagnosis_evidence_recorded",
    "constitutional_development_supervisor_diagnosis_recorded",
)

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
    "performs_automatic_repair": False,
    "modifies_certified_workflow": False,
    "modifies_ive": False,
    "modifies_authorization": False,
    "modifies_worker_contracts": False,
    "modifies_provider_contracts": False,
    "modifies_aicli": False,
    "modifies_pcbv31": False,
}

WORKFLOW_POLICY = {
    "observes_g42_read_only": True,
    "certified_ive_reconstruction_only": True,
    "earliest_blocker_only": True,
    "missing_evidence_explicit": True,
    "minimal_repair_boundary_only": True,
    "certified_revalidation_scope_only": True,
    "unknown_evidence_fails_closed": True,
    "human_approval_preserved": True,
    "validation_execution_allowed": False,
    "automatic_repair_allowed": False,
}

STAGE_SPECS: tuple[
    tuple[
        str,
        str,
        str,
        str,
        str,
        Callable[[dict[str, Any]], dict[str, Any]],
    ],
    ...,
] = (
    (
        "IVE_0_IMPACT_ANALYSIS",
        "INTELLIGENT_VALIDATION_ENGINE_V0",
        INTELLIGENT_VALIDATION_PLAN_ARTIFACT_V1,
        "analysis_status",
        IVE_0_FAILED_CLOSED,
        validate_intelligent_validation_plan_artifact,
    ),
    (
        "IVE_1_SEMANTIC_SELECTION",
        "INTELLIGENT_VALIDATION_ENGINE_V1",
        SEMANTIC_VALIDATION_SELECTION_ARTIFACT_V1,
        "selection_status",
        IVE_1_FAILED_CLOSED,
        validate_semantic_validation_selection_artifact,
    ),
    (
        "G38_VALIDATION_ENTRY",
        "INTELLIGENT_VALIDATION_ENTRY_INTEGRATION",
        INTELLIGENT_VALIDATION_PLANNING_ENTRY_ARTIFACT_V1,
        "entry_status",
        G38_FAILED_CLOSED,
        validate_intelligent_validation_planning_entry_artifact,
    ),
    (
        "IVE_2_SCHEDULING",
        "INTELLIGENT_VALIDATION_ENGINE_V2",
        PARALLEL_VALIDATION_SCHEDULE_ARTIFACT_V1,
        "schedule_status",
        IVE_2_FAILED_CLOSED,
        validate_parallel_validation_schedule_artifact,
    ),
    (
        "IVE_3_FAILURE_ANALYSIS",
        "INTELLIGENT_VALIDATION_ENGINE_V3",
        VALIDATION_FAILURE_ANALYSIS_ARTIFACT_V1,
        "analysis_status",
        IVE_3_FAILED_CLOSED,
        validate_validation_failure_analysis_artifact,
    ),
)


def supervise_constitutional_development_workflow(
    *,
    diagnosis_id: str,
    workflow_artifact: dict[str, Any],
    workflow_reference: str,
    workflow_hash: str,
    workflow_artifact_hash: str,
    workflow_replay_dir: str | Path,
    observed_by: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Diagnose one certified workflow without execution or repair."""

    replay_path = Path(replay_dir)
    workflow: dict[str, Any] | None = None
    evidence: dict[str, Any] | None = None
    try:
        _ensure_replay_available(replay_path)
        identifier = _require_string(diagnosis_id, "diagnosis_id")
        reference = _require_string(
            workflow_reference,
            "workflow_reference",
        )
        semantic_hash = _require_hash(workflow_hash, "workflow_hash")
        artifact_hash = _require_hash(
            workflow_artifact_hash,
            "workflow_artifact_hash",
        )
        observer = _require_string(observed_by, "observed_by")
        timestamp = _require_string(created_at, "created_at")
        workflow = (
            validate_constitutional_development_validation_workflow_artifact(
                workflow_artifact
            )
        )
        _validate_workflow_binding(
            workflow,
            reference,
            semantic_hash,
            artifact_hash,
        )
        workflow_reconstruction = (
            reconstruct_constitutional_development_validation_workflow_replay(
                workflow_replay_dir
            )
        )
        _validate_workflow_reconstruction(
            workflow,
            workflow_reconstruction,
        )
        evidence = _diagnose_workflow_evidence(
            diagnosis_id=identifier,
            workflow=workflow,
            workflow_replay_dir=Path(workflow_replay_dir),
        )
        diagnosis = _diagnosis_artifact(
            diagnosis_id=identifier,
            workflow=workflow,
            diagnosis_evidence=evidence,
            observed_by=observer,
            created_at=timestamp,
        )
    except Exception as exc:
        diagnosis = _failed_diagnosis_artifact(
            diagnosis_id=diagnosis_id,
            workflow_artifact=workflow
            if workflow is not None
            else workflow_artifact,
            workflow_reference=workflow_reference,
            workflow_hash=workflow_hash,
            workflow_artifact_hash=workflow_artifact_hash,
            observed_by=observed_by,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
    _persist_replay(replay_path, workflow, evidence, diagnosis)
    return _capture(diagnosis, replay_path)


def validate_constitutional_development_supervisor_diagnosis_artifact(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Validate a deterministic supervisor diagnosis."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(
            "G43-01 supervisor diagnosis must be a JSON object"
        )
    candidate = deepcopy(artifact)
    _verify_diagnosis_artifact(candidate)
    return candidate


def reconstruct_constitutional_development_supervisor_replay(
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Reconstruct workflow observation and diagnosis evidence."""

    replay_path = Path(replay_dir)
    wrappers = [
        load_json(replay_path / f"{index:03d}_{step}.json")
        for index, step in enumerate(REPLAY_STEPS)
    ]
    for index, (step, wrapper) in enumerate(zip(REPLAY_STEPS, wrappers)):
        _verify_wrapper(wrapper, index, step)
    diagnosis = (
        validate_constitutional_development_supervisor_diagnosis_artifact(
            wrappers[2].get("artifact")
        )
    )
    if diagnosis["diagnosis_status"] != FAILED_CLOSED:
        workflow = (
            validate_constitutional_development_validation_workflow_artifact(
                wrappers[0].get("artifact")
            )
        )
        evidence = _validate_diagnosis_evidence(
            wrappers[1].get("artifact")
        )
        _validate_diagnosis_bindings(diagnosis, workflow, evidence)
    return {
        "diagnosis_id": diagnosis["diagnosis_id"],
        "diagnosis_status": diagnosis["diagnosis_status"],
        "workflow_reference": diagnosis["workflow_reference"],
        "earliest_constitutional_blocker": deepcopy(
            diagnosis["earliest_constitutional_blocker"]
        ),
        "missing_evidence": deepcopy(diagnosis["missing_evidence"]),
        "affected_certified_capability": deepcopy(
            diagnosis["affected_certified_capability"]
        ),
        "minimal_repair_boundary": deepcopy(
            diagnosis["minimal_repair_boundary"]
        ),
        "minimal_revalidation_scope": deepcopy(
            diagnosis["minimal_revalidation_scope"]
        ),
        "diagnosis_hash": diagnosis["diagnosis_hash"],
        "artifact_hash": diagnosis["artifact_hash"],
        "replay_visible": True,
        "fail_closed": diagnosis["diagnosis_status"] == FAILED_CLOSED,
        "failure_reason": diagnosis["failure_reason"],
        "human_approval_required": True,
        "validation_executed": False,
        "automatic_repair_performed": False,
        "authority_flags": deepcopy(diagnosis["authority_flags"]),
        "replay_hashes": [wrapper["replay_hash"] for wrapper in wrappers],
    }


def _diagnose_workflow_evidence(
    *,
    diagnosis_id: str,
    workflow: dict[str, Any],
    workflow_replay_dir: Path,
) -> dict[str, Any]:
    observations: list[dict[str, Any]] = []
    if workflow["workflow_status"] == DEVELOPMENT_VALIDATION_PLANNING_READY:
        bundle = validate_unified_validation_planning_bundle_artifact(
            workflow["ive_4_planning_bundle_artifact"]
        )
        reconstructed = reconstruct_intelligent_validation_orchestration_replay(
            workflow_replay_dir / "ive_4"
        )
        _validate_ive_4_reconstruction(bundle, reconstructed)
        observations.extend(_healthy_stage_observations(bundle))
        return _diagnosis_evidence_artifact(
            diagnosis_id=diagnosis_id,
            workflow=workflow,
            evidence_status="COMPLETE_NO_BLOCKER",
            observations=observations,
            blocker=None,
        )

    source_wrapper = load_json(
        workflow_replay_dir / "000_normalized_change_bound.json"
    )
    ive_4_wrapper = load_json(
        workflow_replay_dir / "001_ive_4_planning_bundle_bound.json"
    )
    _verify_external_wrapper(
        source_wrapper,
        0,
        "normalized_change_bound",
        "G42",
    )
    _verify_external_wrapper(
        ive_4_wrapper,
        1,
        "ive_4_planning_bundle_bound",
        "G42",
    )
    source_artifact = source_wrapper.get("artifact")
    if _is_unavailable(source_artifact):
        blocker = _blocker(
            rank=0,
            boundary="PLATFORM_CHANGE_NORMALIZATION",
            capability_id="PLATFORM_CHANGE_NORMALIZATION",
            evidence_status="UNAVAILABLE",
            source_artifact=source_artifact,
            requirement=(
                "Valid normalized-change artifact and immutable replay."
            ),
        )
        observations.append(_observation_from_blocker(blocker))
        return _diagnosis_evidence_artifact(
            diagnosis_id=diagnosis_id,
            workflow=workflow,
            evidence_status="BLOCKER_IDENTIFIED",
            observations=observations,
            blocker=blocker,
        )
    source = validate_normalized_change_artifact(source_artifact)
    observations.append(
        _observation(
            rank=0,
            boundary="PLATFORM_CHANGE_NORMALIZATION",
            capability_id="PLATFORM_CHANGE_NORMALIZATION",
            evidence_status="VALID",
            artifact_hash=source["artifact_hash"],
        )
    )
    if (
        workflow["source_normalized_change_reference"]
        != source["normalization_id"]
        or workflow["source_normalized_change_hash"]
        != source["normalized_change_hash"]
        or workflow["source_normalized_change_artifact_hash"]
        != source["artifact_hash"]
    ):
        blocker = _blocker(
            rank=1,
            boundary="G42_WORKFLOW_INPUT_BINDING",
            capability_id=(
                "CONSTITUTIONAL_DEVELOPMENT_WORKFLOW_INTEGRATION"
            ),
            evidence_status="BINDING_MISMATCH",
            source_artifact=workflow,
            requirement=(
                "Exact normalized-change reference, semantic hash, and "
                "artifact hash binding."
            ),
        )
        observations.append(_observation_from_blocker(blocker))
        return _diagnosis_evidence_artifact(
            diagnosis_id=diagnosis_id,
            workflow=workflow,
            evidence_status="BLOCKER_IDENTIFIED",
            observations=observations,
            blocker=blocker,
        )

    ive_4_artifact = ive_4_wrapper.get("artifact")
    if _is_unavailable(ive_4_artifact):
        blocker = _blocker(
            rank=1,
            boundary="G42_WORKFLOW_INPUT_BINDING",
            capability_id=(
                "CONSTITUTIONAL_DEVELOPMENT_WORKFLOW_INTEGRATION"
            ),
            evidence_status="IVE_4_NOT_INVOKED",
            source_artifact=ive_4_artifact,
            requirement=(
                "Valid workflow input binding before default IVE-4 "
                "planning invocation."
            ),
        )
        observations.append(_observation_from_blocker(blocker))
        return _diagnosis_evidence_artifact(
            diagnosis_id=diagnosis_id,
            workflow=workflow,
            evidence_status="BLOCKER_IDENTIFIED",
            observations=observations,
            blocker=blocker,
        )

    bundle = validate_unified_validation_planning_bundle_artifact(
        ive_4_artifact
    )
    reconstructed = reconstruct_intelligent_validation_orchestration_replay(
        workflow_replay_dir / "ive_4"
    )
    if bundle["bundle_status"] == IVE_4_FAILED_CLOSED:
        blocker, stage_observations = _diagnose_failed_ive_4(
            bundle=bundle,
            ive_4_replay_dir=workflow_replay_dir / "ive_4",
        )
        observations.extend(stage_observations)
        return _diagnosis_evidence_artifact(
            diagnosis_id=diagnosis_id,
            workflow=workflow,
            evidence_status="BLOCKER_IDENTIFIED",
            observations=observations,
            blocker=blocker,
        )

    _validate_ive_4_reconstruction(bundle, reconstructed)
    observations.extend(_healthy_stage_observations(bundle))
    blocker = _blocker(
        rank=9,
        boundary="G42_WORKFLOW_OUTPUT_BINDING",
        capability_id="CONSTITUTIONAL_DEVELOPMENT_WORKFLOW_INTEGRATION",
        evidence_status="FAILED_CLOSED_WITH_VALID_IVE_4",
        source_artifact=workflow,
        requirement=(
            "Valid G42 binding of the reconstructed IVE-4 planning bundle."
        ),
    )
    observations.append(_observation_from_blocker(blocker))
    return _diagnosis_evidence_artifact(
        diagnosis_id=diagnosis_id,
        workflow=workflow,
        evidence_status="BLOCKER_IDENTIFIED",
        observations=observations,
        blocker=blocker,
    )


def _diagnose_failed_ive_4(
    *,
    bundle: dict[str, Any],
    ive_4_replay_dir: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    observations: list[dict[str, Any]] = []
    wrappers = [
        load_json(ive_4_replay_dir / f"{index:03d}_{step}.json")
        for index, step in enumerate(IVE_4_REPLAY_STEPS)
    ]
    for index, (step, wrapper) in enumerate(
        zip(IVE_4_REPLAY_STEPS, wrappers)
    ):
        _verify_external_wrapper(wrapper, index, step, "IVE-4")

    source_artifact = wrappers[0].get("artifact")
    if _is_unavailable(source_artifact):
        blocker = _blocker(
            rank=0,
            boundary="PLATFORM_CHANGE_NORMALIZATION",
            capability_id="PLATFORM_CHANGE_NORMALIZATION",
            evidence_status="UNAVAILABLE",
            source_artifact=source_artifact,
            requirement="Valid normalized-change evidence for IVE-4.",
        )
        return blocker, [_observation_from_blocker(blocker)]
    source = validate_normalized_change_artifact(source_artifact)
    observations.append(
        _observation(
            rank=0,
            boundary="PLATFORM_CHANGE_NORMALIZATION",
            capability_id="PLATFORM_CHANGE_NORMALIZATION",
            evidence_status="VALID",
            artifact_hash=source["artifact_hash"],
        )
    )

    for offset, (spec, wrapper) in enumerate(
        zip(STAGE_SPECS, wrappers[1:6]),
        start=3,
    ):
        (
            boundary,
            capability_id,
            artifact_type,
            status_field,
            failed_status,
            validator,
        ) = spec
        stage_artifact = wrapper.get("artifact")
        if _is_unavailable(stage_artifact):
            blocker = _blocker(
                rank=2 if not observations[1:] else offset,
                boundary=(
                    "IVE_4_ORCHESTRATION_INPUT_BINDING"
                    if not observations[1:]
                    else boundary
                ),
                capability_id=(
                    "INTELLIGENT_VALIDATION_ORCHESTRATOR_V4"
                    if not observations[1:]
                    else capability_id
                ),
                evidence_status="UNAVAILABLE",
                source_artifact=stage_artifact,
                requirement=(
                    "Complete mode-specific IVE-4 input evidence."
                    if not observations[1:]
                    else f"Successful certified {boundary} evidence."
                ),
            )
            observations.append(_observation_from_blocker(blocker))
            return blocker, observations
        if stage_artifact.get("artifact_type") != artifact_type:
            raise FailClosedRuntimeError(
                f"G43-01 unexpected {boundary} evidence type"
            )
        validated = validator(stage_artifact)
        stage_status = validated.get(status_field)
        observation = _observation(
            rank=offset,
            boundary=boundary,
            capability_id=capability_id,
            evidence_status=(
                "FAILED_CLOSED"
                if stage_status == failed_status
                else "VALID"
            ),
            artifact_hash=validated["artifact_hash"],
        )
        observations.append(observation)
        if stage_status == failed_status:
            blocker = _blocker(
                rank=offset,
                boundary=boundary,
                capability_id=capability_id,
                evidence_status="FAILED_CLOSED",
                source_artifact=validated,
                requirement=f"Successful certified {boundary} evidence.",
            )
            return blocker, observations

    blocker = _blocker(
        rank=8,
        boundary="IVE_4_UNIFIED_PLANNING_BUNDLE",
        capability_id="INTELLIGENT_VALIDATION_ORCHESTRATOR_V4",
        evidence_status="FAILED_CLOSED",
        source_artifact=bundle,
        requirement="Successful deterministic IVE-4 planning bundle.",
    )
    observations.append(_observation_from_blocker(blocker))
    return blocker, observations


def _diagnosis_evidence_artifact(
    *,
    diagnosis_id: str,
    workflow: dict[str, Any],
    evidence_status: str,
    observations: list[dict[str, Any]],
    blocker: dict[str, Any] | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": (
            CONSTITUTIONAL_DEVELOPMENT_DIAGNOSIS_EVIDENCE_ARTIFACT_V1
        ),
        "diagnosis_id": diagnosis_id,
        "workflow_reference": workflow["workflow_id"],
        "workflow_hash": workflow["workflow_hash"],
        "workflow_artifact_hash": workflow["artifact_hash"],
        "workflow_status": workflow["workflow_status"],
        "evidence_status": evidence_status,
        "boundary_observations": deepcopy(observations),
        "boundary_observation_hashes": [
            item["observation_hash"] for item in observations
        ],
        "earliest_blocker_evidence": deepcopy(blocker),
        "certified_ive_reconstruction_invoked": True,
        "workflow_modified": False,
        "validation_executed": False,
        "automatic_repair_performed": False,
        "replay_visible": True,
        "read_only": True,
    }
    artifact["evidence_hash"] = replay_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _validate_diagnosis_evidence(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(
            "G43-01 diagnosis evidence must be a JSON object"
        )
    candidate = deepcopy(artifact)
    if (
        candidate.get("artifact_type")
        != CONSTITUTIONAL_DEVELOPMENT_DIAGNOSIS_EVIDENCE_ARTIFACT_V1
        or candidate.get("evidence_status")
        not in {"COMPLETE_NO_BLOCKER", "BLOCKER_IDENTIFIED"}
    ):
        raise FailClosedRuntimeError(
            "G43-01 diagnosis evidence type or status invalid"
        )
    _verify_hash(
        candidate,
        "artifact_hash",
        "G43-01 diagnosis evidence artifact hash mismatch",
    )
    body = deepcopy(candidate)
    body.pop("artifact_hash")
    evidence_hash = body.pop("evidence_hash", None)
    if evidence_hash != replay_hash(body):
        raise FailClosedRuntimeError(
            "G43-01 deterministic diagnosis evidence hash mismatch"
        )
    observations = candidate.get("boundary_observations")
    if not isinstance(observations, list):
        raise FailClosedRuntimeError(
            "G43-01 boundary observations required"
        )
    for observation in observations:
        _verify_hash(
            observation,
            "observation_hash",
            "G43-01 boundary observation hash mismatch",
        )
    if candidate.get("boundary_observation_hashes") != [
        item["observation_hash"] for item in observations
    ]:
        raise FailClosedRuntimeError(
            "G43-01 boundary observation lineage mismatch"
        )
    if (
        candidate.get("certified_ive_reconstruction_invoked") is not True
        or candidate.get("workflow_modified") is not False
        or candidate.get("validation_executed") is not False
        or candidate.get("automatic_repair_performed") is not False
        or candidate.get("replay_visible") is not True
        or candidate.get("read_only") is not True
    ):
        raise FailClosedRuntimeError(
            "G43-01 diagnosis evidence boundary flags invalid"
        )
    return candidate


def _diagnosis_artifact(
    *,
    diagnosis_id: str,
    workflow: dict[str, Any],
    diagnosis_evidence: dict[str, Any],
    observed_by: str,
    created_at: str,
) -> dict[str, Any]:
    blocker = diagnosis_evidence["earliest_blocker_evidence"]
    if blocker is None:
        status = WORKFLOW_HEALTHY
        earliest = {
            "boundary_rank": None,
            "boundary": NO_CONSTITUTIONAL_BLOCKER,
            "evidence_status": "COMPLETE_NO_BLOCKER",
            "blocker_hash": replay_hash(
                {"boundary": NO_CONSTITUTIONAL_BLOCKER}
            ),
        }
        missing_evidence: list[dict[str, Any]] = []
        affected_capability: dict[str, Any] | None = None
        repair = {
            "repair_status": "NO_REPAIR_REQUIRED",
            "boundary": NO_CONSTITUTIONAL_BLOCKER,
            "permitted_repair_targets": [],
            "prohibited_repair_targets": [
                "CERTIFIED_WORKFLOW",
                "CERTIFIED_IVE",
                "AUTHORIZATION",
                "WORKER",
                "PROVIDER",
                "PCBV31",
            ],
            "automatic_repair_allowed": False,
            "human_approval_required": True,
        }
        bundle = workflow["ive_4_planning_bundle_artifact"]
        revalidation = {
            "scope_status": "CERTIFIED_IVE_4_SCOPE_AVAILABLE",
            "source_reference": bundle["orchestration_id"],
            "source_hash": bundle["bundle_hash"],
            "recommendation": deepcopy(
                bundle["current_planning_recommendation"]
            ),
            "full_regression": deepcopy(bundle["full_regression"]),
            "certified_scope_claim_allowed": True,
            "reduced_scope_claim_allowed": False,
            "validation_execution_allowed": False,
            "human_approval_required": True,
        }
    else:
        status = BLOCKER_DIAGNOSED
        earliest = deepcopy(blocker)
        missing_evidence = [
            {
                "boundary": blocker["boundary"],
                "capability_identifier": blocker[
                    "capability_identifier"
                ],
                "required_evidence": blocker["required_evidence"],
                "observed_evidence_status": blocker["evidence_status"],
                "source_artifact_hash": blocker[
                    "source_artifact_hash"
                ],
            }
        ]
        affected_capability = _certified_capability_evidence(
            blocker["capability_identifier"]
        )
        repair = {
            "repair_status": "EVIDENCE_BOUNDARY_REPAIR_RECOMMENDED",
            "boundary": blocker["boundary"],
            "capability_identifier": blocker[
                "capability_identifier"
            ],
            "permitted_repair_targets": [
                "MISSING_OR_INVALID_INPUT_EVIDENCE",
                "EXACT_REFERENCE_AND_HASH_BINDING",
            ],
            "prohibited_repair_targets": [
                "UPSTREAM_VALID_CERTIFIED_EVIDENCE",
                "CERTIFIED_IVE_SEMANTICS",
                "HUMAN_APPROVAL",
                "AUTHORIZATION",
                "WORKER",
                "PROVIDER",
                "AICLI",
                "PCBV31",
            ],
            "automatic_repair_allowed": False,
            "implementation_change_authorized": False,
            "human_approval_required": True,
        }
        revalidation = {
            "scope_status": "FULL_REGRESSION_REQUIRED",
            "source_reference": "UNAVAILABLE",
            "source_hash": blocker["source_artifact_hash"],
            "recommendation": {
                "recommendation_type": (
                    "NO_REDUCED_SCOPE_WITH_INCOMPLETE_DIAGNOSIS_LINEAGE"
                ),
                "groups": [],
                "recommendation_only": True,
            },
            "full_regression": {
                "required": True,
                "reason": (
                    "Earliest constitutional blocker prevents a certified "
                    "minimal-scope claim."
                ),
                "mapping_authority": "G43_01_FAIL_CLOSED_SCOPE_POLICY_V1",
            },
            "reduced_scope_claim_allowed": False,
            "validation_execution_allowed": False,
            "human_approval_required": True,
        }

    artifact = {
        "artifact_type": (
            CONSTITUTIONAL_DEVELOPMENT_SUPERVISOR_DIAGNOSIS_ARTIFACT_V1
        ),
        "runtime_version": (
            CONSTITUTIONAL_DEVELOPMENT_SUPERVISOR_RUNTIME_VERSION
        ),
        "diagnosis_id": diagnosis_id,
        "diagnosis_status": status,
        "workflow_reference": workflow["workflow_id"],
        "workflow_hash": workflow["workflow_hash"],
        "workflow_artifact_hash": workflow["artifact_hash"],
        "workflow_status": workflow["workflow_status"],
        "diagnosis_evidence_hash": diagnosis_evidence["evidence_hash"],
        "diagnosis_evidence_artifact_hash": diagnosis_evidence[
            "artifact_hash"
        ],
        "earliest_constitutional_blocker": earliest,
        "missing_evidence": missing_evidence,
        "affected_certified_capability": affected_capability,
        "minimal_repair_boundary": repair,
        "minimal_revalidation_scope": revalidation,
        "supervision_policy": deepcopy(WORKFLOW_POLICY),
        "observed_by": observed_by,
        "created_at": created_at,
        "replay_visible": True,
        "read_only": True,
        "non_authoritative": True,
        "human_approval_required": True,
        "human_approval_recorded": False,
        "validation_executed": False,
        "automatic_repair_performed": False,
        "authorization_invoked": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "aicli_invoked": False,
        "workflow_modified": False,
        "pcbv31_modified": False,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "failure_reason": None,
    }
    artifact["diagnosis_hash"] = _diagnosis_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_diagnosis_artifact(
    *,
    diagnosis_id: Any,
    workflow_artifact: Any,
    workflow_reference: Any,
    workflow_hash: Any,
    workflow_artifact_hash: Any,
    observed_by: Any,
    created_at: Any,
    failure_reason: str,
) -> dict[str, Any]:
    source = workflow_artifact if isinstance(workflow_artifact, dict) else {}
    fallback_hash = _safe_hash(source.get("artifact_hash"))
    artifact = {
        "artifact_type": (
            CONSTITUTIONAL_DEVELOPMENT_SUPERVISOR_DIAGNOSIS_ARTIFACT_V1
        ),
        "runtime_version": (
            CONSTITUTIONAL_DEVELOPMENT_SUPERVISOR_RUNTIME_VERSION
        ),
        "diagnosis_id": _safe_string(diagnosis_id),
        "diagnosis_status": FAILED_CLOSED,
        "workflow_reference": _safe_string(workflow_reference),
        "workflow_hash": _safe_hash(workflow_hash),
        "workflow_artifact_hash": _safe_hash(
            workflow_artifact_hash or fallback_hash
        ),
        "workflow_status": _safe_string(
            source.get("workflow_status")
        ),
        "diagnosis_evidence_hash": fallback_hash,
        "diagnosis_evidence_artifact_hash": fallback_hash,
        "earliest_constitutional_blocker": {
            "boundary_rank": None,
            "boundary": "UNKNOWN_INCOMPLETE_DIAGNOSIS_EVIDENCE",
            "evidence_status": "INCOMPLETE",
            "blocker_hash": replay_hash(
                {"boundary": "UNKNOWN_INCOMPLETE_DIAGNOSIS_EVIDENCE"}
            ),
        },
        "missing_evidence": [],
        "affected_certified_capability": None,
        "minimal_repair_boundary": {
            "repair_status": "BLOCKED_PENDING_COMPLETE_DIAGNOSIS_EVIDENCE",
            "boundary": "UNKNOWN",
            "permitted_repair_targets": [],
            "prohibited_repair_targets": ["ALL_UNDIAGNOSED_BOUNDARIES"],
            "automatic_repair_allowed": False,
            "human_approval_required": True,
        },
        "minimal_revalidation_scope": {
            "scope_status": "FULL_REGRESSION_REQUIRED",
            "source_reference": "UNAVAILABLE",
            "source_hash": fallback_hash,
            "recommendation": {
                "recommendation_type": (
                    "NO_SCOPE_RECOMMENDATION_WITH_INCOMPLETE_EVIDENCE"
                ),
                "groups": [],
                "recommendation_only": True,
            },
            "full_regression": {
                "required": True,
                "reason": (
                    "Incomplete diagnosis evidence prohibits reduced scope."
                ),
                "mapping_authority": "G43_01_FAIL_CLOSED_SCOPE_POLICY_V1",
            },
            "reduced_scope_claim_allowed": False,
            "validation_execution_allowed": False,
            "human_approval_required": True,
        },
        "supervision_policy": deepcopy(WORKFLOW_POLICY),
        "observed_by": _safe_string(observed_by),
        "created_at": _safe_string(created_at),
        "replay_visible": True,
        "read_only": True,
        "non_authoritative": True,
        "human_approval_required": True,
        "human_approval_recorded": False,
        "validation_executed": False,
        "automatic_repair_performed": False,
        "authorization_invoked": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "aicli_invoked": False,
        "workflow_modified": False,
        "pcbv31_modified": False,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "failure_reason": failure_reason,
    }
    artifact["diagnosis_hash"] = _diagnosis_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _verify_diagnosis_artifact(artifact: dict[str, Any]) -> None:
    if (
        artifact.get("artifact_type")
        != CONSTITUTIONAL_DEVELOPMENT_SUPERVISOR_DIAGNOSIS_ARTIFACT_V1
        or artifact.get("runtime_version")
        != CONSTITUTIONAL_DEVELOPMENT_SUPERVISOR_RUNTIME_VERSION
    ):
        raise FailClosedRuntimeError("G43-01 diagnosis artifact type mismatch")
    _verify_hash(
        artifact,
        "artifact_hash",
        "G43-01 diagnosis artifact hash mismatch",
    )
    if artifact.get("diagnosis_hash") != _diagnosis_hash(artifact):
        raise FailClosedRuntimeError(
            "G43-01 deterministic diagnosis hash mismatch"
        )
    if artifact.get("diagnosis_status") not in {
        WORKFLOW_HEALTHY,
        BLOCKER_DIAGNOSED,
        FAILED_CLOSED,
    }:
        raise FailClosedRuntimeError("G43-01 diagnosis status invalid")
    if (
        artifact.get("supervision_policy") != WORKFLOW_POLICY
        or artifact.get("authority_flags") != AUTHORITY_FLAGS
        or artifact.get("replay_visible") is not True
        or artifact.get("read_only") is not True
        or artifact.get("non_authoritative") is not True
        or artifact.get("human_approval_required") is not True
    ):
        raise FailClosedRuntimeError("G43-01 supervision policy invalid")
    for field in (
        "human_approval_recorded",
        "validation_executed",
        "automatic_repair_performed",
        "authorization_invoked",
        "worker_invoked",
        "provider_invoked",
        "aicli_invoked",
        "workflow_modified",
        "pcbv31_modified",
    ):
        if artifact.get(field) is not False:
            raise FailClosedRuntimeError(f"G43-01 {field} must be false")
    if artifact["diagnosis_status"] == FAILED_CLOSED:
        if (
            artifact.get("affected_certified_capability") is not None
            or artifact.get("missing_evidence")
            or not artifact.get("failure_reason")
        ):
            raise FailClosedRuntimeError(
                "failed G43-01 diagnosis cannot make blocker claims"
            )
        if (
            artifact.get("minimal_revalidation_scope", {})
            .get("full_regression", {})
            .get("required")
            is not True
        ):
            raise FailClosedRuntimeError(
                "failed G43-01 diagnosis must require full regression"
            )
    elif artifact.get("failure_reason") is not None:
        raise FailClosedRuntimeError(
            "successful G43-01 diagnosis cannot contain failure reason"
        )
    elif artifact["diagnosis_status"] == WORKFLOW_HEALTHY:
        if (
            artifact.get("earliest_constitutional_blocker", {}).get(
                "boundary"
            )
            != NO_CONSTITUTIONAL_BLOCKER
            or artifact.get("missing_evidence")
            or artifact.get("affected_certified_capability") is not None
            or artifact.get("minimal_repair_boundary", {}).get(
                "repair_status"
            )
            != "NO_REPAIR_REQUIRED"
            or artifact.get("minimal_revalidation_scope", {}).get(
                "validation_execution_allowed"
            )
            is not False
        ):
            raise FailClosedRuntimeError(
                "healthy G43-01 diagnosis boundary claims invalid"
            )
    else:
        blocker = artifact.get("earliest_constitutional_blocker", {})
        missing = artifact.get("missing_evidence")
        affected = artifact.get("affected_certified_capability")
        if (
            not isinstance(missing, list)
            or len(missing) != 1
            or not isinstance(affected, dict)
            or affected.get("capability_identifier")
            != blocker.get("capability_identifier")
            or missing[0].get("capability_identifier")
            != blocker.get("capability_identifier")
            or artifact.get("minimal_repair_boundary", {}).get(
                "boundary"
            )
            != blocker.get("boundary")
            or artifact.get("minimal_revalidation_scope", {})
            .get("full_regression", {})
            .get("required")
            is not True
        ):
            raise FailClosedRuntimeError(
                "G43-01 blocker diagnosis claims invalid"
            )


def _validate_diagnosis_bindings(
    diagnosis: dict[str, Any],
    workflow: dict[str, Any],
    evidence: dict[str, Any],
) -> None:
    if (
        diagnosis["workflow_reference"] != workflow["workflow_id"]
        or diagnosis["workflow_hash"] != workflow["workflow_hash"]
        or diagnosis["workflow_artifact_hash"] != workflow["artifact_hash"]
        or diagnosis["diagnosis_evidence_hash"]
        != evidence["evidence_hash"]
        or diagnosis["diagnosis_evidence_artifact_hash"]
        != evidence["artifact_hash"]
        or evidence["workflow_reference"] != workflow["workflow_id"]
        or evidence["workflow_hash"] != workflow["workflow_hash"]
        or evidence["workflow_artifact_hash"] != workflow["artifact_hash"]
        or diagnosis["earliest_constitutional_blocker"]
        != (
            evidence["earliest_blocker_evidence"]
            if evidence["earliest_blocker_evidence"] is not None
            else diagnosis["earliest_constitutional_blocker"]
        )
    ):
        raise FailClosedRuntimeError(
            "G43-01 supervisor replay lineage mismatch"
        )
    expected = _diagnosis_artifact(
        diagnosis_id=diagnosis["diagnosis_id"],
        workflow=workflow,
        diagnosis_evidence=evidence,
        observed_by=diagnosis["observed_by"],
        created_at=diagnosis["created_at"],
    )
    if diagnosis != expected:
        raise FailClosedRuntimeError(
            "G43-01 deterministic supervisor diagnosis mismatch"
        )


def _validate_workflow_binding(
    workflow: dict[str, Any],
    reference: str,
    semantic_hash: str,
    artifact_hash: str,
) -> None:
    if (
        workflow.get("artifact_type")
        != CONSTITUTIONAL_DEVELOPMENT_VALIDATION_WORKFLOW_ARTIFACT_V1
        or workflow.get("workflow_id") != reference
        or workflow.get("workflow_hash") != semantic_hash
        or workflow.get("artifact_hash") != artifact_hash
    ):
        raise FailClosedRuntimeError(
            "G43-01 workflow binding mismatch"
        )


def _validate_workflow_reconstruction(
    workflow: dict[str, Any],
    reconstructed: dict[str, Any],
) -> None:
    if (
        reconstructed.get("workflow_id") != workflow["workflow_id"]
        or reconstructed.get("workflow_hash") != workflow["workflow_hash"]
        or reconstructed.get("artifact_hash") != workflow["artifact_hash"]
        or reconstructed.get("workflow_status")
        != workflow["workflow_status"]
    ):
        raise FailClosedRuntimeError(
            "G43-01 workflow replay reconstruction mismatch"
        )


def _validate_ive_4_reconstruction(
    bundle: dict[str, Any],
    reconstructed: dict[str, Any],
) -> None:
    if (
        reconstructed.get("bundle_hash") != bundle["bundle_hash"]
        or reconstructed.get("artifact_hash") != bundle["artifact_hash"]
        or reconstructed.get("planning_mode") != bundle["planning_mode"]
        or reconstructed.get("stage_lineage") != bundle["stage_lineage"]
    ):
        raise FailClosedRuntimeError(
            "G43-01 IVE-4 replay reconstruction mismatch"
        )


def _healthy_stage_observations(
    bundle: dict[str, Any],
) -> list[dict[str, Any]]:
    observations = [
        _observation(
            rank=0,
            boundary="PLATFORM_CHANGE_NORMALIZATION",
            capability_id="PLATFORM_CHANGE_NORMALIZATION",
            evidence_status="VALID",
            artifact_hash=bundle[
                "source_normalized_change_artifact_hash"
            ],
        ),
        _observation(
            rank=1,
            boundary="G42_WORKFLOW_INPUT_BINDING",
            capability_id=(
                "CONSTITUTIONAL_DEVELOPMENT_WORKFLOW_INTEGRATION"
            ),
            evidence_status="VALID",
            artifact_hash=bundle[
                "source_normalized_change_artifact_hash"
            ],
        ),
    ]
    capability_by_boundary = {
        "IVE_0": "INTELLIGENT_VALIDATION_ENGINE_V0",
        "IVE_1": "INTELLIGENT_VALIDATION_ENGINE_V1",
        "G38_ENTRY": "INTELLIGENT_VALIDATION_ENTRY_INTEGRATION",
        "IVE_2": "INTELLIGENT_VALIDATION_ENGINE_V2",
        "IVE_3": "INTELLIGENT_VALIDATION_ENGINE_V3",
    }
    for offset, stage in enumerate(bundle["stage_lineage"], start=3):
        observations.append(
            _observation(
                rank=offset,
                boundary=stage["boundary"],
                capability_id=capability_by_boundary[stage["boundary"]],
                evidence_status=stage["invocation_status"],
                artifact_hash=stage["artifact_hash"],
            )
        )
    observations.append(
        _observation(
            rank=8,
            boundary="IVE_4_UNIFIED_PLANNING_BUNDLE",
            capability_id="INTELLIGENT_VALIDATION_ORCHESTRATOR_V4",
            evidence_status="VALID",
            artifact_hash=bundle["artifact_hash"],
        )
    )
    return observations


def _observation(
    *,
    rank: int,
    boundary: str,
    capability_id: str,
    evidence_status: str,
    artifact_hash: str,
) -> dict[str, Any]:
    item = {
        "boundary_rank": rank,
        "boundary": boundary,
        "capability_identifier": capability_id,
        "evidence_status": evidence_status,
        "artifact_hash": artifact_hash,
    }
    item["observation_hash"] = replay_hash(item)
    return item


def _blocker(
    *,
    rank: int,
    boundary: str,
    capability_id: str,
    evidence_status: str,
    source_artifact: Any,
    requirement: str,
) -> dict[str, Any]:
    source_hash = _safe_hash(
        source_artifact.get("artifact_hash")
        if isinstance(source_artifact, dict)
        else None
    )
    blocker = {
        "boundary_rank": rank,
        "boundary": boundary,
        "capability_identifier": capability_id,
        "evidence_status": evidence_status,
        "source_artifact_hash": source_hash,
        "required_evidence": requirement,
        "earliest_known_boundary_only": True,
    }
    blocker["blocker_hash"] = replay_hash(blocker)
    return blocker


def _observation_from_blocker(
    blocker: dict[str, Any],
) -> dict[str, Any]:
    return _observation(
        rank=blocker["boundary_rank"],
        boundary=blocker["boundary"],
        capability_id=blocker["capability_identifier"],
        evidence_status=blocker["evidence_status"],
        artifact_hash=blocker["source_artifact_hash"],
    )


def _certified_capability_evidence(
    capability_id: str,
) -> dict[str, Any]:
    record = lookup_platform_capability_certification(capability_id)
    return {
        "capability_identifier": record["capability_identifier"],
        "certification_status": record["certification_status"],
        "certification_milestone": record["certification_milestone"],
        "certification_version": record["certification_version"],
        "implementation_owner": record["implementation_owner"],
        "certification_record_hash": replay_hash(record),
    }


def _is_unavailable(artifact: Any) -> bool:
    return (
        isinstance(artifact, dict)
        and isinstance(artifact.get("artifact_type"), str)
        and artifact["artifact_type"].endswith("_UNAVAILABLE_V1")
        and artifact.get("source_available") is False
    )


def _capture(
    artifact: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "runtime_version": (
            CONSTITUTIONAL_DEVELOPMENT_SUPERVISOR_RUNTIME_VERSION
        ),
        "constitutional_development_supervisor_diagnosis_artifact": deepcopy(
            artifact
        ),
        "diagnosis_id": artifact["diagnosis_id"],
        "diagnosis_status": artifact["diagnosis_status"],
        "workflow_reference": artifact["workflow_reference"],
        "earliest_constitutional_blocker": deepcopy(
            artifact["earliest_constitutional_blocker"]
        ),
        "minimal_repair_boundary": deepcopy(
            artifact["minimal_repair_boundary"]
        ),
        "minimal_revalidation_scope": deepcopy(
            artifact["minimal_revalidation_scope"]
        ),
        "diagnosis_hash": artifact["diagnosis_hash"],
        "replay_reference": str(replay_path),
        "fail_closed": artifact["diagnosis_status"] == FAILED_CLOSED,
        "failure_reason": artifact["failure_reason"],
        "human_approval_required": True,
        "validation_executed": False,
        "automatic_repair_performed": False,
        "authorization_invoked": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "repository_mutated": False,
    }
    capture["capture_hash"] = replay_hash(capture)
    return capture


def _persist_replay(
    replay_path: Path,
    workflow: dict[str, Any] | None,
    evidence: dict[str, Any] | None,
    diagnosis: dict[str, Any],
) -> None:
    try:
        artifacts = (
            workflow or _unavailable_snapshot("G42_WORKFLOW", diagnosis),
            evidence or _unavailable_snapshot(
                "DIAGNOSIS_EVIDENCE",
                diagnosis,
            ),
            diagnosis,
        )
        for index, (step, artifact) in enumerate(zip(REPLAY_STEPS, artifacts)):
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
    diagnosis: dict[str, Any],
) -> dict[str, Any]:
    artifact = {
        "artifact_type": f"{boundary}_UNAVAILABLE_V1",
        "boundary": boundary,
        "diagnosis_id": diagnosis["diagnosis_id"],
        "source_available": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _verify_wrapper(
    wrapper: dict[str, Any],
    index: int,
    step: str,
) -> None:
    if (
        wrapper.get("replay_index") != index
        or wrapper.get("replay_step") != step
    ):
        raise FailClosedRuntimeError("G43-01 replay ordering mismatch")
    _verify_hash(wrapper, "replay_hash", "G43-01 replay hash mismatch")


def _verify_external_wrapper(
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
            f"G43-01 {owner} replay ordering mismatch"
        )
    _verify_hash(
        wrapper,
        "replay_hash",
        f"G43-01 {owner} replay hash mismatch",
    )


def _ensure_replay_available(replay_path: Path) -> None:
    if any(
        (replay_path / f"{index:03d}_{step}.json").exists()
        for index, step in enumerate(REPLAY_STEPS)
    ):
        raise FailClosedRuntimeError(
            "G43-01 failed closed: replay artifact already exists"
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


def _diagnosis_hash(artifact: dict[str, Any]) -> str:
    candidate = deepcopy(artifact)
    candidate.pop("artifact_hash", None)
    candidate.pop("diagnosis_hash", None)
    return replay_hash(candidate)


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"G43-01 requires {field}")
    return value


def _require_hash(value: Any, field: str) -> str:
    text = _require_string(value, field)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(
            f"G43-01 requires canonical {field}"
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
