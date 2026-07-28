"""Deterministic validation failure analysis over certified IVE lineage."""

from __future__ import annotations

from collections import deque
from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.intelligent_validation_engine_v0 import (
    FAILED_CLOSED as IVE_0_FAILED_CLOSED,
    reconstruct_intelligent_validation_engine_v0_replay,
    validate_intelligent_validation_plan_artifact,
)
from aigol.runtime.intelligent_validation_engine_v1 import (
    FAILED_CLOSED as IVE_1_FAILED_CLOSED,
    validate_semantic_validation_selection_artifact,
)
from aigol.runtime.intelligent_validation_engine_v2 import (
    FAILED_CLOSED as IVE_2_FAILED_CLOSED,
    reconstruct_parallel_validation_schedule_replay,
    validate_parallel_validation_schedule_artifact,
)
from aigol.runtime.intelligent_validation_entry_integration_runtime import (
    FAILED_CLOSED as G38_FAILED_CLOSED,
    reconstruct_intelligent_validation_entry_replay,
    validate_intelligent_validation_planning_entry_artifact,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_validation_candidate import (
    validate_governed_validation_candidate,
)
from aigol.runtime.platform_core_validation_governance import (
    validate_governed_validation_approval,
)
from aigol.runtime.platform_core_validation_replay import (
    VALIDATION_REPLAY_STEPS,
    reconstruct_governed_validation_replay,
    verify_validation_artifact_hash,
)
from aigol.runtime.platform_core_validation_result import (
    VALIDATION_RESULT_ARTIFACT_V1,
)
from aigol.runtime.transport.serialization import (
    load_json,
    replay_hash,
    write_json_immutable,
)
from aigol.workers.validation_command_worker import (
    VALIDATION_FAILED,
    VALIDATION_TIMED_OUT,
)


INTELLIGENT_VALIDATION_ENGINE_V3_RUNTIME_VERSION = (
    "G40_01_INTELLIGENT_VALIDATION_ENGINE_V3_RUNTIME_V1"
)
FAILED_VALIDATION_EXECUTION_EVIDENCE_ARTIFACT_V1 = (
    "FAILED_VALIDATION_EXECUTION_EVIDENCE_ARTIFACT_V1"
)
VALIDATION_FAILURE_ANALYSIS_ARTIFACT_V1 = (
    "VALIDATION_FAILURE_ANALYSIS_ARTIFACT_V1"
)
VALIDATION_FAILURE_ANALYZED = "VALIDATION_FAILURE_ANALYZED"
FAILED_CLOSED = "FAILED_CLOSED"
FAILED_VALIDATION_STATUSES = {VALIDATION_FAILED, VALIDATION_TIMED_OUT}
REPLAY_STEPS = (
    "ive_0_plan_bound",
    "ive_1_semantic_selection_bound",
    "g38_validation_plan_bound",
    "ive_2_schedule_bound",
    "failed_validation_execution_evidence_bound",
    "validation_failure_analysis_recorded",
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
    "schedules_runtime_execution": False,
    "invokes_parallel_workers": False,
    "modifies_pytest": False,
    "modifies_validation_runtime": False,
    "modifies_authorization": False,
    "performs_automatic_repair": False,
}


def analyze_failed_validation(
    *,
    analysis_id: str,
    session_id: str,
    ive_2_schedule_artifact: dict[str, Any],
    ive_2_schedule_reference: str,
    ive_2_schedule_hash: str,
    ive_2_replay_dir: str | Path,
    g38_replay_dir: str | Path,
    validation_result_artifact: dict[str, Any],
    validation_result_reference: str,
    validation_result_hash: str,
    validation_replay_dir: str | Path,
    failed_group_id: str,
    failed_group_hash: str,
    failed_requirement_hashes: list[str],
    observed_by: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Analyze one replay-backed failure without executing or repairing."""

    replay_path = Path(replay_dir)
    ive_0: dict[str, Any] | None = None
    ive_1: dict[str, Any] | None = None
    g38: dict[str, Any] | None = None
    ive_2: dict[str, Any] | None = None
    execution_evidence: dict[str, Any] | None = None
    try:
        _ensure_replay_available(replay_path)
        identifier = _require_string(analysis_id, "analysis_id")
        session = _require_string(session_id, "session_id")
        schedule_reference = _require_string(
            ive_2_schedule_reference,
            "ive_2_schedule_reference",
        )
        schedule_hash = _require_hash(
            ive_2_schedule_hash,
            "ive_2_schedule_hash",
        )
        observer = _require_string(observed_by, "observed_by")
        timestamp = _require_string(created_at, "created_at")

        ive_2 = validate_parallel_validation_schedule_artifact(
            ive_2_schedule_artifact
        )
        _validate_ive_2_binding(ive_2, schedule_reference, schedule_hash)
        source_replay = reconstruct_parallel_validation_schedule_replay(
            ive_2_replay_dir
        )
        _validate_ive_2_replay_binding(ive_2, source_replay)
        ive_1, g38 = _load_ive_2_sources(ive_2_replay_dir, ive_2)
        ive_0 = _load_and_validate_earlier_lineage(
            g38_replay_dir,
            g38,
            ive_1,
        )

        execution_evidence = _failed_execution_evidence(
            result_artifact=validation_result_artifact,
            result_reference=validation_result_reference,
            result_hash=validation_result_hash,
            validation_replay_dir=validation_replay_dir,
            schedule=ive_2,
            failed_group_id=failed_group_id,
            failed_group_hash=failed_group_hash,
            failed_requirement_hashes=failed_requirement_hashes,
            observed_by=observer,
            observed_at=timestamp,
        )
        analysis = _derive_failure_analysis(
            analysis_id=identifier,
            session_id=session,
            ive_0=ive_0,
            ive_1=ive_1,
            g38=g38,
            ive_2=ive_2,
            execution_evidence=execution_evidence,
            created_at=timestamp,
        )
    except Exception as exc:
        analysis = _failed_analysis_artifact(
            analysis_id=analysis_id,
            session_id=session_id,
            ive_2_schedule_artifact=ive_2_schedule_artifact,
            validation_result_artifact=validation_result_artifact,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
    _persist_replay(
        replay_path,
        ive_0,
        ive_1,
        g38,
        ive_2,
        execution_evidence,
        analysis,
    )
    return _capture(analysis, replay_path)


def validate_validation_failure_analysis_artifact(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Validate one immutable IVE-3 analysis artifact."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(
            "IVE-3 failure analysis artifact must be a JSON object"
        )
    candidate = deepcopy(artifact)
    _verify_analysis_artifact(candidate)
    return candidate


def reconstruct_validation_failure_analysis_replay(
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Reconstruct IVE-0 through IVE-3 and the failed execution binding."""

    replay_path = Path(replay_dir)
    wrappers = [
        load_json(replay_path / f"{index:03d}_{step}.json")
        for index, step in enumerate(REPLAY_STEPS)
    ]
    for index, (step, wrapper) in enumerate(zip(REPLAY_STEPS, wrappers)):
        _verify_wrapper(wrapper, index, step)
    analysis = validate_validation_failure_analysis_artifact(
        wrappers[5].get("artifact")
    )

    if analysis["analysis_status"] != FAILED_CLOSED:
        ive_0 = validate_intelligent_validation_plan_artifact(
            wrappers[0].get("artifact")
        )
        ive_1 = validate_semantic_validation_selection_artifact(
            wrappers[1].get("artifact")
        )
        g38 = validate_intelligent_validation_planning_entry_artifact(
            wrappers[2].get("artifact")
        )
        ive_2 = validate_parallel_validation_schedule_artifact(
            wrappers[3].get("artifact")
        )
        execution = _validate_execution_evidence(wrappers[4].get("artifact"))
        _validate_complete_lineage(
            analysis,
            ive_0,
            ive_1,
            g38,
            ive_2,
            execution,
        )
        expected = _derive_failure_analysis(
            analysis_id=analysis["analysis_id"],
            session_id=analysis["session_id"],
            ive_0=ive_0,
            ive_1=ive_1,
            g38=g38,
            ive_2=ive_2,
            execution_evidence=execution,
            created_at=analysis["created_at"],
        )
        if analysis != expected:
            raise FailClosedRuntimeError(
                "IVE-3 replay deterministic analysis mismatch"
            )

    return {
        "analysis_id": analysis["analysis_id"],
        "analysis_status": analysis["analysis_status"],
        "earliest_known_planning_boundary": deepcopy(
            analysis["earliest_known_planning_boundary"]
        ),
        "recommended_revalidation_groups": deepcopy(
            analysis["recommended_revalidation_groups"]
        ),
        "recommended_revalidation_group_count": analysis[
            "recommended_revalidation_group_count"
        ],
        "full_regression": deepcopy(analysis["full_regression"]),
        "analysis_hash": analysis["analysis_hash"],
        "artifact_hash": analysis["artifact_hash"],
        "replay_visible": True,
        "fail_closed": analysis["analysis_status"] == FAILED_CLOSED,
        "failure_reason": analysis["failure_reason"],
        "human_approval_required": True,
        "validation_executed": False,
        "automatic_repair_performed": False,
        "authority_flags": deepcopy(analysis["authority_flags"]),
        "replay_hashes": [wrapper["replay_hash"] for wrapper in wrappers],
    }


def _load_ive_2_sources(
    ive_2_replay_dir: str | Path,
    ive_2: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    source_path = Path(ive_2_replay_dir)
    g38 = validate_intelligent_validation_planning_entry_artifact(
        load_json(source_path / "000_g38_validation_plan_bound.json").get(
            "artifact"
        )
    )
    ive_1 = validate_semantic_validation_selection_artifact(
        load_json(
            source_path / "001_ive_1_semantic_selection_bound.json"
        ).get("artifact")
    )
    if (
        ive_2["source_g38_reference"] != g38["entry_id"]
        or ive_2["source_g38_planning_entry_hash"]
        != g38["planning_entry_hash"]
        or ive_2["source_g38_artifact_hash"] != g38["artifact_hash"]
    ):
        raise FailClosedRuntimeError("IVE-3 G39-to-G38 lineage mismatch")
    if (
        ive_2["source_ive_1_reference"] != ive_1["selection_id"]
        or ive_2["source_ive_1_selection_hash"]
        != ive_1["semantic_validation_selection_hash"]
        or ive_2["source_ive_1_artifact_hash"] != ive_1["artifact_hash"]
    ):
        raise FailClosedRuntimeError("IVE-3 G39-to-IVE-1 lineage mismatch")
    return ive_1, g38


def _load_and_validate_earlier_lineage(
    g38_replay_dir: str | Path,
    g38: dict[str, Any],
    ive_1: dict[str, Any],
) -> dict[str, Any]:
    source_path = Path(g38_replay_dir)
    reconstructed = reconstruct_intelligent_validation_entry_replay(
        source_path
    )
    if (
        reconstructed["entry_id"] != g38["entry_id"]
        or reconstructed["planning_entry_hash"] != g38["planning_entry_hash"]
        or reconstructed["artifact_hash"] != g38["artifact_hash"]
    ):
        raise FailClosedRuntimeError("IVE-3 G38 replay lineage mismatch")
    ive_0 = validate_intelligent_validation_plan_artifact(
        load_json(
            source_path / "ive_0/000_intelligent_validation_plan_recorded.json"
        ).get("artifact")
    )
    reconstruct_intelligent_validation_engine_v0_replay(
        source_path / "ive_0"
    )
    if (
        ive_0["analysis_status"] == IVE_0_FAILED_CLOSED
        or ive_1["selection_status"] == IVE_1_FAILED_CLOSED
        or g38["entry_status"] == G38_FAILED_CLOSED
    ):
        raise FailClosedRuntimeError(
            "IVE-3 planning lineage contains failed source"
        )
    if (
        ive_1["source_ive_0_reference"] != ive_0["ive_analysis_id"]
        or ive_1["source_ive_0_plan_hash"]
        != ive_0["intelligent_validation_plan_hash"]
        or ive_1["source_ive_0_artifact_hash"] != ive_0["artifact_hash"]
    ):
        raise FailClosedRuntimeError("IVE-3 IVE-0-to-IVE-1 lineage mismatch")
    return ive_0


def _failed_execution_evidence(
    *,
    result_artifact: dict[str, Any],
    result_reference: str,
    result_hash: str,
    validation_replay_dir: str | Path,
    schedule: dict[str, Any],
    failed_group_id: str,
    failed_group_hash: str,
    failed_requirement_hashes: list[str],
    observed_by: str,
    observed_at: str,
) -> dict[str, Any]:
    replay_path = Path(validation_replay_dir)
    reconstructed = reconstruct_governed_validation_replay(replay_path)
    candidate = load_json(
        replay_path / f"000_{VALIDATION_REPLAY_STEPS[0]}.json"
    )["artifact"]
    approval = load_json(
        replay_path / f"001_{VALIDATION_REPLAY_STEPS[1]}.json"
    )["artifact"]
    replay_result = load_json(
        replay_path / f"006_{VALIDATION_REPLAY_STEPS[6]}.json"
    )["artifact"]
    validated_candidate = validate_governed_validation_candidate(candidate)
    validated_approval = validate_governed_validation_approval(
        approval,
        validated_candidate,
    )
    verify_validation_artifact_hash(replay_result)
    verify_validation_artifact_hash(result_artifact)
    if replay_result != result_artifact:
        raise FailClosedRuntimeError(
            "IVE-3 validation result differs from execution replay"
        )
    if (
        replay_result.get("artifact_type") != VALIDATION_RESULT_ARTIFACT_V1
        or replay_result.get("execution_id")
        != _require_string(result_reference, "validation_result_reference")
        or replay_result.get("artifact_hash")
        != _require_hash(result_hash, "validation_result_hash")
    ):
        raise FailClosedRuntimeError("IVE-3 validation result binding mismatch")
    if replay_result.get("validation_status") not in FAILED_VALIDATION_STATUSES:
        raise FailClosedRuntimeError(
            "IVE-3 requires a failed or timed-out validation result"
        )
    if (
        reconstructed["validation_status"]
        != replay_result["validation_status"]
        or replay_result["candidate_id"] != validated_candidate["candidate_id"]
        or replay_result["candidate_hash"] != validated_candidate["artifact_hash"]
    ):
        raise FailClosedRuntimeError(
            "IVE-3 failed validation replay lineage mismatch"
        )
    group = _bound_failed_group(
        schedule,
        failed_group_id,
        failed_group_hash,
        failed_requirement_hashes,
    )
    artifact = {
        "artifact_type": FAILED_VALIDATION_EXECUTION_EVIDENCE_ARTIFACT_V1,
        "schedule_id": schedule["schedule_id"],
        "schedule_hash": schedule["schedule_hash"],
        "failed_group_id": group["group_id"],
        "failed_group_hash": group["group_hash"],
        "failed_requirement_hashes": sorted(failed_requirement_hashes),
        "candidate_artifact": deepcopy(validated_candidate),
        "candidate_hash": validated_candidate["artifact_hash"],
        "human_approval_artifact": deepcopy(validated_approval),
        "human_approval_hash": validated_approval["artifact_hash"],
        "validation_result_artifact": deepcopy(replay_result),
        "validation_result_hash": replay_result["artifact_hash"],
        "validation_replay_hash": reconstructed["replay_hash"],
        "validation_status": replay_result["validation_status"],
        "human_approval_observed": True,
        "observed_by": observed_by,
        "observed_at": observed_at,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _bound_failed_group(
    schedule: dict[str, Any],
    group_id: Any,
    group_hash: Any,
    requirement_hashes: Any,
) -> dict[str, Any]:
    identifier = _require_string(group_id, "failed_group_id")
    expected_hash = _require_hash(group_hash, "failed_group_hash")
    group = next(
        (item for item in schedule["groups"] if item["group_id"] == identifier),
        None,
    )
    if group is None or group["group_hash"] != expected_hash:
        raise FailClosedRuntimeError("IVE-3 failed group binding mismatch")
    if not isinstance(requirement_hashes, list):
        raise FailClosedRuntimeError(
            "IVE-3 failed requirement hashes must be a list"
        )
    normalized = [_require_hash(item, "failed_requirement_hash") for item in requirement_hashes]
    if len(normalized) != len(set(normalized)):
        raise FailClosedRuntimeError(
            "IVE-3 duplicate failed requirement binding"
        )
    available = set(group["requirement_hashes"])
    if group["group_kind"] == "FULL_REGRESSION_BARRIER":
        if normalized:
            raise FailClosedRuntimeError(
                "IVE-3 full-regression barrier cannot bind requirement hashes"
            )
    elif not normalized or not set(normalized).issubset(available):
        raise FailClosedRuntimeError(
            "IVE-3 failed requirements are not bound to failed group"
        )
    return group


def _validate_execution_evidence(artifact: Any) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(
            "IVE-3 failed execution evidence must be an object"
        )
    candidate = deepcopy(artifact)
    _verify_hash(candidate, "artifact_hash", "IVE-3 execution evidence hash mismatch")
    if (
        candidate.get("artifact_type")
        != FAILED_VALIDATION_EXECUTION_EVIDENCE_ARTIFACT_V1
    ):
        raise FailClosedRuntimeError("IVE-3 execution evidence type mismatch")
    validated_candidate = validate_governed_validation_candidate(
        candidate.get("candidate_artifact")
    )
    approval = validate_governed_validation_approval(
        candidate.get("human_approval_artifact"),
        validated_candidate,
    )
    result = candidate.get("validation_result_artifact")
    verify_validation_artifact_hash(result)
    if (
        candidate.get("candidate_hash") != validated_candidate["artifact_hash"]
        or candidate.get("human_approval_hash") != approval["artifact_hash"]
        or candidate.get("validation_result_hash") != result["artifact_hash"]
        or result.get("candidate_hash") != validated_candidate["artifact_hash"]
        or result.get("validation_status") not in FAILED_VALIDATION_STATUSES
        or candidate.get("validation_status") != result["validation_status"]
        or candidate.get("human_approval_observed") is not True
    ):
        raise FailClosedRuntimeError(
            "IVE-3 execution evidence lineage mismatch"
        )
    return candidate


def _derive_failure_analysis(
    *,
    analysis_id: str,
    session_id: str,
    ive_0: dict[str, Any],
    ive_1: dict[str, Any],
    g38: dict[str, Any],
    ive_2: dict[str, Any],
    execution_evidence: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    group = _bound_failed_group(
        ive_2,
        execution_evidence["failed_group_id"],
        execution_evidence["failed_group_hash"],
        execution_evidence["failed_requirement_hashes"],
    )
    earliest = _earliest_boundary(
        group,
        execution_evidence["failed_requirement_hashes"],
        ive_0,
        ive_1,
        ive_2,
    )
    revalidation = _minimal_revalidation_scope(
        ive_2,
        group,
        execution_evidence["failed_requirement_hashes"],
    )
    lineage = [
        {
            "lineage_index": 0,
            "boundary": "IVE_0",
            "reference": ive_0["ive_analysis_id"],
            "semantic_hash": ive_0["intelligent_validation_plan_hash"],
            "artifact_hash": ive_0["artifact_hash"],
        },
        {
            "lineage_index": 1,
            "boundary": "IVE_1",
            "reference": ive_1["selection_id"],
            "semantic_hash": ive_1["semantic_validation_selection_hash"],
            "artifact_hash": ive_1["artifact_hash"],
        },
        {
            "lineage_index": 2,
            "boundary": "G38_ENTRY",
            "reference": g38["entry_id"],
            "semantic_hash": g38["planning_entry_hash"],
            "artifact_hash": g38["artifact_hash"],
        },
        {
            "lineage_index": 3,
            "boundary": "IVE_2",
            "reference": ive_2["schedule_id"],
            "semantic_hash": ive_2["schedule_hash"],
            "artifact_hash": ive_2["artifact_hash"],
        },
    ]
    for item in lineage:
        item["lineage_hash"] = replay_hash(item)
    artifact = {
        "artifact_type": VALIDATION_FAILURE_ANALYSIS_ARTIFACT_V1,
        "runtime_version": INTELLIGENT_VALIDATION_ENGINE_V3_RUNTIME_VERSION,
        "analysis_id": analysis_id,
        "session_id": session_id,
        "analysis_status": VALIDATION_FAILURE_ANALYZED,
        "planning_lineage": lineage,
        "planning_lineage_hash": replay_hash(lineage),
        "failed_execution_evidence_hash": execution_evidence["artifact_hash"],
        "failed_validation_status": execution_evidence["validation_status"],
        "failed_group_id": group["group_id"],
        "failed_group_hash": group["group_hash"],
        "failed_requirement_hashes": deepcopy(
            execution_evidence["failed_requirement_hashes"]
        ),
        "earliest_known_planning_boundary": earliest,
        "recommended_revalidation_groups": revalidation,
        "recommended_revalidation_group_count": len(revalidation),
        "full_regression": deepcopy(ive_2["full_regression"]),
        "human_approval": deepcopy(ive_2["human_approval"]),
        "analysis_policy": {
            "earliest_known_boundary_only": True,
            "certified_dependency_descendants_only": True,
            "failed_group_requirements_exact": True,
            "downstream_group_requirements_preserved": True,
            "full_regression_not_reduced": True,
            "unknown_dependencies_fail_closed": True,
            "recommendation_only": True,
            "validation_execution_allowed": False,
            "automatic_repair_allowed": False,
        },
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
        "repository_mutated": False,
        "replay_semantics_modified": False,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "failure_reason": None,
    }
    artifact["analysis_hash"] = _analysis_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _earliest_boundary(
    group: dict[str, Any],
    failed_hashes: list[str],
    ive_0: dict[str, Any],
    ive_1: dict[str, Any],
    ive_2: dict[str, Any],
) -> dict[str, Any]:
    if group["group_kind"] == "FULL_REGRESSION_BARRIER":
        boundary = {
            "boundary_rank": 2,
            "boundary": "IVE_2_FULL_REGRESSION_BARRIER",
            "reference": ive_2["schedule_id"],
            "semantic_hash": ive_2["schedule_hash"],
            "evidence_hashes": [group["group_hash"]],
            "reason": (
                "The failed validation is bound to the IVE-2 terminal "
                "full-regression barrier."
            ),
        }
    else:
        failed = [
            item
            for item in group["requirements"]
            if item["selection_requirement_hash"] in failed_hashes
        ]
        scopes = {item["validation_scope"] for item in failed}
        if not failed or not scopes.issubset({"DIRECT", "TRANSITIVE"}):
            raise FailClosedRuntimeError(
                "IVE-3 cannot resolve failed requirement planning scope"
            )
        if "DIRECT" in scopes:
            evidence = sorted(
                {
                    evidence_hash
                    for item in failed
                    if item["validation_scope"] == "DIRECT"
                    for evidence_hash in item["source_evidence_hashes"]
                }
            )
            boundary = {
                "boundary_rank": 0,
                "boundary": "IVE_0_DIRECT_IMPACT_RECOMMENDATION",
                "reference": ive_0["ive_analysis_id"],
                "semantic_hash": ive_0["intelligent_validation_plan_hash"],
                "evidence_hashes": evidence,
                "reason": (
                    "At least one exact failed requirement originates in "
                    "IVE-0 direct impact recommendation evidence."
                ),
            }
        else:
            evidence = sorted(
                {
                    evidence_hash
                    for item in failed
                    for evidence_hash in item["dependency_evidence_hashes"]
                }
            )
            boundary = {
                "boundary_rank": 1,
                "boundary": "IVE_1_SEMANTIC_DEPENDENCY_SELECTION",
                "reference": ive_1["selection_id"],
                "semantic_hash": ive_1["semantic_validation_selection_hash"],
                "evidence_hashes": evidence,
                "reason": (
                    "The exact failed requirements originate in IVE-1 "
                    "transitive dependency selection."
                ),
            }
    boundary["boundary_hash"] = replay_hash(boundary)
    return boundary


def _minimal_revalidation_scope(
    schedule: dict[str, Any],
    failed_group: dict[str, Any],
    failed_requirement_hashes: list[str],
) -> list[dict[str, Any]]:
    groups = {item["group_id"]: item for item in schedule["groups"]}
    adjacency: dict[str, set[str]] = {}
    for group in schedule["groups"]:
        for predecessor in group["depends_on_group_ids"]:
            if predecessor not in groups:
                raise FailClosedRuntimeError(
                    "IVE-3 schedule contains unknown dependency group"
                )
            adjacency.setdefault(predecessor, set()).add(group["group_id"])
    paths = _shortest_group_paths(failed_group["group_id"], adjacency)
    selected_ids = {
        failed_group["group_id"],
        *paths,
    }
    schedule_order = {
        group_id: (wave["wave_index"], index)
        for wave in schedule["waves"]
        for index, group_id in enumerate(wave["group_ids"])
    }
    if not selected_ids.issubset(schedule_order):
        raise FailClosedRuntimeError(
            "IVE-3 revalidation group is absent from schedule waves"
        )
    recommendations = []
    for group_id in sorted(selected_ids, key=lambda item: schedule_order[item]):
        group = groups[group_id]
        if group_id == failed_group["group_id"]:
            requirement_hashes = sorted(failed_requirement_hashes)
            reason = "Exact failed requirements must be re-validated."
            path = [group_id]
        else:
            requirement_hashes = deepcopy(group["requirement_hashes"])
            reason = (
                "A certified scheduling dependency descends from the failed "
                "group and must be re-validated."
            )
            path = paths[group_id]
        recommendation = {
            "group_id": group_id,
            "group_hash": group["group_hash"],
            "group_kind": group["group_kind"],
            "revalidation_requirement_hashes": requirement_hashes,
            "dependency_path_from_failed_group": path,
            "dependency_path_hash": replay_hash(path),
            "reason": reason,
            "required": True,
        }
        recommendation["recommendation_hash"] = replay_hash(recommendation)
        recommendations.append(recommendation)
    return recommendations


def _shortest_group_paths(
    origin: str,
    adjacency: dict[str, set[str]],
) -> dict[str, list[str]]:
    paths: dict[str, list[str]] = {}
    queue: deque[list[str]] = deque([[origin]])
    while queue:
        path = queue.popleft()
        for target in sorted(adjacency.get(path[-1], set())):
            candidate = [*path, target]
            existing = paths.get(target)
            if existing is None or (len(candidate), candidate) < (
                len(existing),
                existing,
            ):
                paths[target] = candidate
                queue.append(candidate)
    return paths


def _failed_analysis_artifact(
    *,
    analysis_id: Any,
    session_id: Any,
    ive_2_schedule_artifact: Any,
    validation_result_artifact: Any,
    created_at: Any,
    failure_reason: str,
) -> dict[str, Any]:
    schedule_hash = _safe_hash(
        ive_2_schedule_artifact.get("schedule_hash")
        if isinstance(ive_2_schedule_artifact, dict)
        else None
    )
    result_hash = _safe_hash(
        validation_result_artifact.get("artifact_hash")
        if isinstance(validation_result_artifact, dict)
        else None
    )
    boundary = {
        "boundary_rank": None,
        "boundary": "UNKNOWN_FAILED_CLOSED",
        "reference": "UNAVAILABLE",
        "semantic_hash": schedule_hash,
        "evidence_hashes": [result_hash],
        "reason": "Planning lineage could not be reconstructed deterministically.",
    }
    boundary["boundary_hash"] = replay_hash(boundary)
    artifact = {
        "artifact_type": VALIDATION_FAILURE_ANALYSIS_ARTIFACT_V1,
        "runtime_version": INTELLIGENT_VALIDATION_ENGINE_V3_RUNTIME_VERSION,
        "analysis_id": _safe_string(analysis_id),
        "session_id": _safe_string(session_id),
        "analysis_status": FAILED_CLOSED,
        "planning_lineage": [],
        "planning_lineage_hash": replay_hash([]),
        "failed_execution_evidence_hash": result_hash,
        "failed_validation_status": "UNKNOWN",
        "failed_group_id": "UNAVAILABLE",
        "failed_group_hash": schedule_hash,
        "failed_requirement_hashes": [],
        "earliest_known_planning_boundary": boundary,
        "recommended_revalidation_groups": [],
        "recommended_revalidation_group_count": 0,
        "full_regression": {
            "required": True,
            "reason": "IVE-3 failure prohibits minimal-scope claims.",
            "mapping_authority": "IVE_3_FAIL_CLOSED_POLICY_V1",
        },
        "human_approval": {
            "required_before_execution": True,
            "approval_status": "BLOCKED",
            "must_bind_exact_candidate_hash": True,
            "approval_authorizes_execution_by_itself": False,
        },
        "analysis_policy": {
            "earliest_known_boundary_only": True,
            "certified_dependency_descendants_only": True,
            "failed_group_requirements_exact": True,
            "downstream_group_requirements_preserved": True,
            "full_regression_not_reduced": True,
            "unknown_dependencies_fail_closed": True,
            "recommendation_only": True,
            "validation_execution_allowed": False,
            "automatic_repair_allowed": False,
        },
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
        "repository_mutated": False,
        "replay_semantics_modified": False,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "failure_reason": failure_reason,
    }
    artifact["analysis_hash"] = _analysis_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _verify_analysis_artifact(artifact: dict[str, Any]) -> None:
    if artifact.get("artifact_type") != VALIDATION_FAILURE_ANALYSIS_ARTIFACT_V1:
        raise FailClosedRuntimeError("IVE-3 analysis artifact type mismatch")
    _verify_hash(artifact, "artifact_hash", "IVE-3 artifact hash mismatch")
    if artifact.get("analysis_hash") != _analysis_hash(artifact):
        raise FailClosedRuntimeError("IVE-3 deterministic analysis hash mismatch")
    if artifact.get("analysis_status") not in {
        VALIDATION_FAILURE_ANALYZED,
        FAILED_CLOSED,
    }:
        raise FailClosedRuntimeError("IVE-3 analysis status invalid")
    if (
        artifact.get("replay_visible") is not True
        or artifact.get("read_only") is not True
        or artifact.get("non_authoritative") is not True
    ):
        raise FailClosedRuntimeError("IVE-3 boundary flags invalid")
    if artifact.get("authority_flags") != AUTHORITY_FLAGS:
        raise FailClosedRuntimeError("IVE-3 authority flags invalid")
    for field in (
        "human_approval_recorded",
        "validation_executed",
        "automatic_repair_performed",
        "authorization_invoked",
        "worker_invoked",
        "provider_invoked",
        "aicli_invoked",
        "repository_mutated",
        "replay_semantics_modified",
    ):
        if artifact.get(field) is not False:
            raise FailClosedRuntimeError(f"IVE-3 {field} must be false")
    if artifact.get("human_approval_required") is not True:
        raise FailClosedRuntimeError("IVE-3 Human Approval requirement missing")
    policy = artifact.get("analysis_policy")
    if not isinstance(policy, dict) or policy != {
        "earliest_known_boundary_only": True,
        "certified_dependency_descendants_only": True,
        "failed_group_requirements_exact": True,
        "downstream_group_requirements_preserved": True,
        "full_regression_not_reduced": True,
        "unknown_dependencies_fail_closed": True,
        "recommendation_only": True,
        "validation_execution_allowed": False,
        "automatic_repair_allowed": False,
    }:
        raise FailClosedRuntimeError("IVE-3 analysis policy invalid")
    groups = artifact.get("recommended_revalidation_groups")
    if (
        not isinstance(groups, list)
        or artifact.get("recommended_revalidation_group_count") != len(groups)
    ):
        raise FailClosedRuntimeError("IVE-3 revalidation count mismatch")
    if artifact["analysis_status"] == FAILED_CLOSED:
        if groups or artifact.get("planning_lineage"):
            raise FailClosedRuntimeError(
                "failed IVE-3 analysis cannot contain scope claims"
            )
        if artifact.get("full_regression", {}).get("required") is not True:
            raise FailClosedRuntimeError(
                "failed IVE-3 analysis must require full regression"
            )
        if not artifact.get("failure_reason"):
            raise FailClosedRuntimeError(
                "failed IVE-3 analysis requires failure reason"
            )
    else:
        if not groups or len(artifact.get("planning_lineage", [])) != 4:
            raise FailClosedRuntimeError(
                "successful IVE-3 analysis requires complete lineage and scope"
            )
        if artifact.get("failure_reason") is not None:
            raise FailClosedRuntimeError(
                "successful IVE-3 analysis cannot contain failure reason"
            )
        if artifact.get("failed_validation_status") not in FAILED_VALIDATION_STATUSES:
            raise FailClosedRuntimeError(
                "successful IVE-3 analysis requires failed validation status"
            )
        for item in groups:
            _verify_hash(
                item,
                "recommendation_hash",
                "IVE-3 revalidation recommendation hash mismatch",
            )
        _verify_hash(
            artifact["earliest_known_planning_boundary"],
            "boundary_hash",
            "IVE-3 earliest boundary hash mismatch",
        )


def _validate_complete_lineage(
    analysis: dict[str, Any],
    ive_0: dict[str, Any],
    ive_1: dict[str, Any],
    g38: dict[str, Any],
    ive_2: dict[str, Any],
    execution: dict[str, Any],
) -> None:
    if (
        ive_0["analysis_status"] == IVE_0_FAILED_CLOSED
        or ive_1["selection_status"] == IVE_1_FAILED_CLOSED
        or g38["entry_status"] == G38_FAILED_CLOSED
        or ive_2["schedule_status"] == IVE_2_FAILED_CLOSED
    ):
        raise FailClosedRuntimeError("IVE-3 replay contains failed planning source")
    if (
        ive_1["source_ive_0_artifact_hash"] != ive_0["artifact_hash"]
        or g38["ive_0_artifact_hash"] != ive_0["artifact_hash"]
        or g38["ive_1_artifact_hash"] != ive_1["artifact_hash"]
        or ive_2["source_g38_artifact_hash"] != g38["artifact_hash"]
        or ive_2["source_ive_1_artifact_hash"] != ive_1["artifact_hash"]
        or execution["schedule_id"] != ive_2["schedule_id"]
        or execution["schedule_hash"] != ive_2["schedule_hash"]
        or analysis["failed_execution_evidence_hash"]
        != execution["artifact_hash"]
    ):
        raise FailClosedRuntimeError("IVE-3 replay planning lineage mismatch")


def _validate_ive_2_binding(
    schedule: dict[str, Any],
    reference: str,
    schedule_hash: str,
) -> None:
    if schedule.get("schedule_status") == IVE_2_FAILED_CLOSED:
        raise FailClosedRuntimeError("IVE-3 source IVE-2 schedule failed closed")
    if schedule.get("schedule_id") != reference:
        raise FailClosedRuntimeError("IVE-3 source schedule reference mismatch")
    if schedule.get("schedule_hash") != schedule_hash:
        raise FailClosedRuntimeError("IVE-3 source schedule hash mismatch")


def _validate_ive_2_replay_binding(
    schedule: dict[str, Any],
    reconstructed: dict[str, Any],
) -> None:
    if (
        reconstructed["fail_closed"] is True
        or reconstructed["schedule_id"] != schedule["schedule_id"]
        or reconstructed["schedule_hash"] != schedule["schedule_hash"]
        or reconstructed["artifact_hash"] != schedule["artifact_hash"]
    ):
        raise FailClosedRuntimeError("IVE-3 source IVE-2 replay mismatch")


def _analysis_hash(artifact: dict[str, Any]) -> str:
    candidate = deepcopy(artifact)
    candidate.pop("artifact_hash", None)
    candidate.pop("analysis_hash", None)
    return replay_hash(candidate)


def _capture(artifact: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "runtime_version": INTELLIGENT_VALIDATION_ENGINE_V3_RUNTIME_VERSION,
        "validation_failure_analysis_artifact": deepcopy(artifact),
        "analysis_id": artifact["analysis_id"],
        "analysis_status": artifact["analysis_status"],
        "analysis_hash": artifact["analysis_hash"],
        "replay_reference": str(replay_path),
        "earliest_known_planning_boundary": deepcopy(
            artifact["earliest_known_planning_boundary"]
        ),
        "recommended_revalidation_groups": deepcopy(
            artifact["recommended_revalidation_groups"]
        ),
        "fail_closed": artifact["analysis_status"] == FAILED_CLOSED,
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
    ive_0: dict[str, Any] | None,
    ive_1: dict[str, Any] | None,
    g38: dict[str, Any] | None,
    ive_2: dict[str, Any] | None,
    execution: dict[str, Any] | None,
    analysis: dict[str, Any],
) -> None:
    try:
        artifacts = (
            ive_0 or _unavailable_snapshot("IVE_0", analysis),
            ive_1 or _unavailable_snapshot("IVE_1", analysis),
            g38 or _unavailable_snapshot("G38", analysis),
            ive_2 or _unavailable_snapshot("IVE_2", analysis),
            execution or _unavailable_snapshot("FAILED_EXECUTION", analysis),
            analysis,
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
    analysis: dict[str, Any],
) -> dict[str, Any]:
    artifact = {
        "artifact_type": f"{boundary}_UNAVAILABLE_V1",
        "boundary": boundary,
        "analysis_id": analysis["analysis_id"],
        "source_available": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _verify_wrapper(
    wrapper: dict[str, Any],
    index: int,
    step: str,
) -> None:
    if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
        raise FailClosedRuntimeError("IVE-3 replay ordering mismatch")
    _verify_hash(wrapper, "replay_hash", "IVE-3 replay hash mismatch")


def _ensure_replay_available(replay_path: Path) -> None:
    if any(
        (replay_path / f"{index:03d}_{step}.json").exists()
        for index, step in enumerate(REPLAY_STEPS)
    ):
        raise FailClosedRuntimeError(
            "IVE-3 failed closed: replay artifact already exists"
        )


def _verify_hash(value: dict[str, Any], field: str, message: str) -> None:
    actual = value.get(field)
    if not isinstance(actual, str) or not actual.startswith("sha256:"):
        raise FailClosedRuntimeError(message)
    expected = deepcopy(value)
    expected.pop(field, None)
    if replay_hash(expected) != actual:
        raise FailClosedRuntimeError(message)


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"IVE-3 requires {field}")
    return value


def _require_hash(value: Any, field: str) -> str:
    text = _require_string(value, field)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(f"IVE-3 requires canonical {field}")
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
