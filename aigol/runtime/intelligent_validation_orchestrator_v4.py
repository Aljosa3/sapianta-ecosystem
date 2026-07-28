"""Deterministic orchestration of certified Intelligent Validation planning."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.intelligent_validation_engine_v0 import (
    FAILED_CLOSED as IVE_0_FAILED_CLOSED,
    validate_intelligent_validation_plan_artifact,
)
from aigol.runtime.intelligent_validation_engine_v1 import (
    FAILED_CLOSED as IVE_1_FAILED_CLOSED,
    validate_semantic_validation_selection_artifact,
)
from aigol.runtime.intelligent_validation_engine_v2 import (
    FAILED_CLOSED as IVE_2_FAILED_CLOSED,
    recommend_parallel_validation_schedule,
    validate_parallel_validation_schedule_artifact,
)
from aigol.runtime.intelligent_validation_engine_v3 import (
    FAILED_CLOSED as IVE_3_FAILED_CLOSED,
    analyze_failed_validation,
    validate_validation_failure_analysis_artifact,
)
from aigol.runtime.intelligent_validation_entry_integration_runtime import (
    FAILED_CLOSED as G38_FAILED_CLOSED,
    plan_development_validation,
    validate_intelligent_validation_planning_entry_artifact,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_change_normalization_runtime import (
    validate_normalized_change_artifact,
)
from aigol.runtime.transport.serialization import (
    load_json,
    replay_hash,
    write_json_immutable,
)


INTELLIGENT_VALIDATION_ORCHESTRATOR_V4_RUNTIME_VERSION = (
    "G41_01_INTELLIGENT_VALIDATION_ORCHESTRATOR_V4_RUNTIME_V1"
)
UNIFIED_VALIDATION_PLANNING_BUNDLE_ARTIFACT_V1 = (
    "UNIFIED_VALIDATION_PLANNING_BUNDLE_ARTIFACT_V1"
)
INITIAL_VALIDATION_PLANNING = "INITIAL_VALIDATION_PLANNING"
FAILURE_REVALIDATION_PLANNING = "FAILURE_REVALIDATION_PLANNING"
INITIAL_VALIDATION_PLANNING_BUNDLED = "INITIAL_VALIDATION_PLANNING_BUNDLED"
FAILURE_REVALIDATION_PLANNING_BUNDLED = (
    "FAILURE_REVALIDATION_PLANNING_BUNDLED"
)
IVE_3_NOT_APPLICABLE = "IVE_3_NOT_APPLICABLE_NO_FAILED_VALIDATION_EVIDENCE"
FAILED_CLOSED = "FAILED_CLOSED"
REPLAY_STEPS = (
    "normalized_change_bound",
    "ive_0_plan_bound",
    "ive_1_semantic_selection_bound",
    "g38_validation_plan_bound",
    "ive_2_schedule_bound",
    "ive_3_analysis_state_bound",
    "unified_validation_planning_bundle_recorded",
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


def orchestrate_intelligent_validation_planning(
    *,
    orchestration_id: str,
    session_id: str,
    planning_mode: str,
    normalized_change_artifact: dict[str, Any],
    normalized_change_reference: str,
    normalized_change_hash: str,
    failure_context: dict[str, Any] | None,
    created_by: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Compose certified IVE stages into one immutable planning bundle."""

    replay_path = Path(replay_dir)
    source: dict[str, Any] | None = None
    ive_0: dict[str, Any] | None = None
    ive_1: dict[str, Any] | None = None
    g38: dict[str, Any] | None = None
    ive_2: dict[str, Any] | None = None
    ive_3_state: dict[str, Any] | None = None
    try:
        _ensure_replay_available(replay_path)
        identifier = _require_string(orchestration_id, "orchestration_id")
        session = _require_string(session_id, "session_id")
        mode = _require_mode(planning_mode)
        source_reference = _require_string(
            normalized_change_reference,
            "normalized_change_reference",
        )
        source_hash = _require_hash(
            normalized_change_hash,
            "normalized_change_hash",
        )
        creator = _require_string(created_by, "created_by")
        timestamp = _require_string(created_at, "created_at")
        source = validate_normalized_change_artifact(
            normalized_change_artifact
        )
        _validate_source_binding(source, source_reference, source_hash)
        _validate_failure_context_mode(mode, failure_context)

        g38_capture = plan_development_validation(
            entry_id=f"{identifier}:G38",
            session_id=session,
            normalized_change_artifact=source,
            normalized_change_reference=source_reference,
            normalized_change_hash=source_hash,
            created_by=creator,
            created_at=timestamp,
            replay_dir=replay_path / "g38",
        )
        g38 = validate_intelligent_validation_planning_entry_artifact(
            g38_capture["intelligent_validation_planning_entry_artifact"]
        )
        if g38["entry_status"] == G38_FAILED_CLOSED:
            raise FailClosedRuntimeError(
                f"IVE-4 failed closed at G38: {g38['failure_reason']}"
            )
        ive_0, ive_1 = _load_g38_stage_artifacts(replay_path / "g38", g38)

        ive_2_capture = recommend_parallel_validation_schedule(
            schedule_id=f"{identifier}:IVE-2",
            session_id=session,
            g38_validation_plan_artifact=g38,
            g38_validation_plan_reference=g38["entry_id"],
            g38_validation_plan_hash=g38["planning_entry_hash"],
            g38_replay_dir=replay_path / "g38",
            created_by=creator,
            created_at=timestamp,
            replay_dir=replay_path / "ive_2",
        )
        ive_2 = validate_parallel_validation_schedule_artifact(
            ive_2_capture["parallel_validation_schedule_artifact"]
        )
        if ive_2["schedule_status"] == IVE_2_FAILED_CLOSED:
            raise FailClosedRuntimeError(
                f"IVE-4 failed closed at IVE-2: {ive_2['failure_reason']}"
            )

        if mode == FAILURE_REVALIDATION_PLANNING:
            context = _validated_failure_context(failure_context)
            ive_3_capture = analyze_failed_validation(
                analysis_id=f"{identifier}:IVE-3",
                session_id=session,
                ive_2_schedule_artifact=ive_2,
                ive_2_schedule_reference=ive_2["schedule_id"],
                ive_2_schedule_hash=ive_2["schedule_hash"],
                ive_2_replay_dir=replay_path / "ive_2",
                g38_replay_dir=replay_path / "g38",
                validation_result_artifact=context[
                    "validation_result_artifact"
                ],
                validation_result_reference=context[
                    "validation_result_reference"
                ],
                validation_result_hash=context["validation_result_hash"],
                validation_replay_dir=context["validation_replay_dir"],
                failed_group_id=context["failed_group_id"],
                failed_group_hash=context["failed_group_hash"],
                failed_requirement_hashes=context[
                    "failed_requirement_hashes"
                ],
                observed_by=context["observed_by"],
                created_at=timestamp,
                replay_dir=replay_path / "ive_3",
            )
            ive_3_state = validate_validation_failure_analysis_artifact(
                ive_3_capture["validation_failure_analysis_artifact"]
            )
            if ive_3_state["analysis_status"] == IVE_3_FAILED_CLOSED:
                raise FailClosedRuntimeError(
                    f"IVE-4 failed closed at IVE-3: "
                    f"{ive_3_state['failure_reason']}"
                )
        else:
            ive_3_state = _ive_3_not_applicable_artifact(identifier)

        bundle = _bundle_artifact(
            orchestration_id=identifier,
            session_id=session,
            planning_mode=mode,
            bundle_status=(
                INITIAL_VALIDATION_PLANNING_BUNDLED
                if mode == INITIAL_VALIDATION_PLANNING
                else FAILURE_REVALIDATION_PLANNING_BUNDLED
            ),
            source=source,
            ive_0=ive_0,
            ive_1=ive_1,
            g38=g38,
            ive_2=ive_2,
            ive_3_state=ive_3_state,
            created_by=creator,
            created_at=timestamp,
            failure_reason=None,
        )
    except Exception as exc:
        bundle = _failed_bundle_artifact(
            orchestration_id=orchestration_id,
            session_id=session_id,
            planning_mode=planning_mode,
            normalized_change_artifact=normalized_change_artifact,
            created_by=created_by,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
    _persist_replay(
        replay_path,
        source,
        ive_0,
        ive_1,
        g38,
        ive_2,
        ive_3_state,
        bundle,
    )
    return _capture(bundle, replay_path)


def validate_unified_validation_planning_bundle_artifact(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Validate one immutable IVE-4 unified planning bundle."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(
            "IVE-4 planning bundle must be a JSON object"
        )
    candidate = deepcopy(artifact)
    _verify_bundle_artifact(candidate)
    return candidate


def reconstruct_intelligent_validation_orchestration_replay(
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Reconstruct every bundled IVE planning stage deterministically."""

    replay_path = Path(replay_dir)
    wrappers = [
        load_json(replay_path / f"{index:03d}_{step}.json")
        for index, step in enumerate(REPLAY_STEPS)
    ]
    for index, (step, wrapper) in enumerate(zip(REPLAY_STEPS, wrappers)):
        _verify_wrapper(wrapper, index, step)
    bundle = validate_unified_validation_planning_bundle_artifact(
        wrappers[6].get("artifact")
    )

    if bundle["bundle_status"] != FAILED_CLOSED:
        source = validate_normalized_change_artifact(
            wrappers[0].get("artifact")
        )
        ive_0 = validate_intelligent_validation_plan_artifact(
            wrappers[1].get("artifact")
        )
        ive_1 = validate_semantic_validation_selection_artifact(
            wrappers[2].get("artifact")
        )
        g38 = validate_intelligent_validation_planning_entry_artifact(
            wrappers[3].get("artifact")
        )
        ive_2 = validate_parallel_validation_schedule_artifact(
            wrappers[4].get("artifact")
        )
        if bundle["planning_mode"] == INITIAL_VALIDATION_PLANNING:
            ive_3_state = _validate_ive_3_not_applicable(
                wrappers[5].get("artifact")
            )
        else:
            ive_3_state = validate_validation_failure_analysis_artifact(
                wrappers[5].get("artifact")
            )
        _validate_stage_lineage(
            source,
            ive_0,
            ive_1,
            g38,
            ive_2,
            ive_3_state,
            bundle["planning_mode"],
        )
        expected = _bundle_artifact(
            orchestration_id=bundle["orchestration_id"],
            session_id=bundle["session_id"],
            planning_mode=bundle["planning_mode"],
            bundle_status=bundle["bundle_status"],
            source=source,
            ive_0=ive_0,
            ive_1=ive_1,
            g38=g38,
            ive_2=ive_2,
            ive_3_state=ive_3_state,
            created_by=bundle["created_by"],
            created_at=bundle["created_at"],
            failure_reason=None,
        )
        if bundle != expected:
            raise FailClosedRuntimeError(
                "IVE-4 replay deterministic bundle mismatch"
            )

    return {
        "orchestration_id": bundle["orchestration_id"],
        "planning_mode": bundle["planning_mode"],
        "bundle_status": bundle["bundle_status"],
        "stage_lineage": deepcopy(bundle["stage_lineage"]),
        "current_planning_recommendation": deepcopy(
            bundle["current_planning_recommendation"]
        ),
        "bundle_hash": bundle["bundle_hash"],
        "artifact_hash": bundle["artifact_hash"],
        "replay_visible": True,
        "fail_closed": bundle["bundle_status"] == FAILED_CLOSED,
        "failure_reason": bundle["failure_reason"],
        "human_approval_required": True,
        "validation_executed": False,
        "automatic_repair_performed": False,
        "authority_flags": deepcopy(bundle["authority_flags"]),
        "replay_hashes": [wrapper["replay_hash"] for wrapper in wrappers],
    }


def _load_g38_stage_artifacts(
    g38_replay_dir: Path,
    g38: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    ive_0 = validate_intelligent_validation_plan_artifact(
        load_json(
            g38_replay_dir
            / "ive_0/000_intelligent_validation_plan_recorded.json"
        ).get("artifact")
    )
    ive_1 = validate_semantic_validation_selection_artifact(
        load_json(
            g38_replay_dir
            / "ive_1/001_semantic_validation_selection_recorded.json"
        ).get("artifact")
    )
    if (
        ive_0["analysis_status"] == IVE_0_FAILED_CLOSED
        or ive_1["selection_status"] == IVE_1_FAILED_CLOSED
        or g38["ive_0_artifact_hash"] != ive_0["artifact_hash"]
        or g38["ive_1_artifact_hash"] != ive_1["artifact_hash"]
    ):
        raise FailClosedRuntimeError(
            "IVE-4 G38 nested IVE lineage mismatch"
        )
    return ive_0, ive_1


def _bundle_artifact(
    *,
    orchestration_id: str,
    session_id: str,
    planning_mode: str,
    bundle_status: str,
    source: dict[str, Any],
    ive_0: dict[str, Any],
    ive_1: dict[str, Any],
    g38: dict[str, Any],
    ive_2: dict[str, Any],
    ive_3_state: dict[str, Any],
    created_by: str,
    created_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    stage_artifacts = {
        "ive_0": deepcopy(ive_0),
        "ive_1": deepcopy(ive_1),
        "g38": deepcopy(g38),
        "ive_2": deepcopy(ive_2),
        "ive_3": deepcopy(ive_3_state),
    }
    stage_lineage = _stage_lineage(
        ive_0,
        ive_1,
        g38,
        ive_2,
        ive_3_state,
    )
    current_recommendation = _current_recommendation(
        planning_mode,
        ive_2,
        ive_3_state,
    )
    artifact = {
        "artifact_type": UNIFIED_VALIDATION_PLANNING_BUNDLE_ARTIFACT_V1,
        "runtime_version": INTELLIGENT_VALIDATION_ORCHESTRATOR_V4_RUNTIME_VERSION,
        "orchestration_id": orchestration_id,
        "session_id": session_id,
        "planning_mode": planning_mode,
        "bundle_status": bundle_status,
        "source_normalized_change_reference": source["normalization_id"],
        "source_normalized_change_hash": source["normalized_change_hash"],
        "source_normalized_change_artifact_hash": source["artifact_hash"],
        "stage_artifacts": stage_artifacts,
        "stage_artifact_hashes": {
            key: value["artifact_hash"]
            for key, value in stage_artifacts.items()
        },
        "stage_lineage": stage_lineage,
        "stage_lineage_hash": replay_hash(stage_lineage),
        "current_planning_recommendation": current_recommendation,
        "full_regression": deepcopy(ive_2["full_regression"]),
        "human_approval": deepcopy(ive_2["human_approval"]),
        "orchestration_policy": {
            "certified_stages_invoked_unchanged": True,
            "ive_3_requires_failed_validation_evidence": True,
            "missing_required_evidence_fails_closed": True,
            "recommendation_only": True,
            "validation_execution_allowed": False,
            "automatic_repair_allowed": False,
            "parallel_runtime_dispatch_allowed": False,
            "scope_reduction_allowed": False,
        },
        "created_by": created_by,
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
        "failure_reason": failure_reason,
    }
    artifact["bundle_hash"] = _bundle_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _stage_lineage(
    ive_0: dict[str, Any],
    ive_1: dict[str, Any],
    g38: dict[str, Any],
    ive_2: dict[str, Any],
    ive_3_state: dict[str, Any],
) -> list[dict[str, Any]]:
    ive_3_invoked = "analysis_status" in ive_3_state
    ive_3_reference = (
        ive_3_state["analysis_id"]
        if ive_3_invoked
        else ive_3_state["state_id"]
    )
    ive_3_semantic_hash = (
        ive_3_state["analysis_hash"]
        if ive_3_invoked
        else ive_3_state["state_hash"]
    )
    raw = [
        (
            "IVE_0",
            ive_0["ive_analysis_id"],
            ive_0["intelligent_validation_plan_hash"],
            ive_0["artifact_hash"],
            "INVOKED",
        ),
        (
            "IVE_1",
            ive_1["selection_id"],
            ive_1["semantic_validation_selection_hash"],
            ive_1["artifact_hash"],
            "INVOKED",
        ),
        (
            "G38_ENTRY",
            g38["entry_id"],
            g38["planning_entry_hash"],
            g38["artifact_hash"],
            "INVOKED",
        ),
        (
            "IVE_2",
            ive_2["schedule_id"],
            ive_2["schedule_hash"],
            ive_2["artifact_hash"],
            "INVOKED",
        ),
        (
            "IVE_3",
            ive_3_reference,
            ive_3_semantic_hash,
            ive_3_state["artifact_hash"],
            "INVOKED" if ive_3_invoked else "NOT_APPLICABLE",
        ),
    ]
    lineage = []
    for index, (
        boundary,
        reference,
        semantic_hash,
        artifact_hash,
        status,
    ) in enumerate(raw):
        item = {
            "stage_index": index,
            "boundary": boundary,
            "reference": reference,
            "semantic_hash": semantic_hash,
            "artifact_hash": artifact_hash,
            "invocation_status": status,
        }
        item["lineage_hash"] = replay_hash(item)
        lineage.append(item)
    return lineage


def _current_recommendation(
    planning_mode: str,
    ive_2: dict[str, Any],
    ive_3_state: dict[str, Any],
) -> dict[str, Any]:
    if planning_mode == INITIAL_VALIDATION_PLANNING:
        recommendation = {
            "recommendation_type": "IVE_2_INITIAL_VALIDATION_SCHEDULE",
            "source_reference": ive_2["schedule_id"],
            "source_hash": ive_2["schedule_hash"],
            "groups": deepcopy(ive_2["groups"]),
            "waves": deepcopy(ive_2["waves"]),
            "maximum_recommended_concurrency": ive_2[
                "maximum_recommended_concurrency"
            ],
            "recommendation_only": True,
        }
    else:
        recommendation = {
            "recommendation_type": "IVE_3_FAILURE_REVALIDATION_SCOPE",
            "source_reference": ive_3_state["analysis_id"],
            "source_hash": ive_3_state["analysis_hash"],
            "earliest_known_planning_boundary": deepcopy(
                ive_3_state["earliest_known_planning_boundary"]
            ),
            "recommended_revalidation_groups": deepcopy(
                ive_3_state["recommended_revalidation_groups"]
            ),
            "recommendation_only": True,
        }
    recommendation["recommendation_hash"] = replay_hash(recommendation)
    return recommendation


def _ive_3_not_applicable_artifact(orchestration_id: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": "IVE_3_NOT_APPLICABLE_ARTIFACT_V1",
        "state_id": f"{orchestration_id}:IVE-3",
        "state_status": IVE_3_NOT_APPLICABLE,
        "state_reason": "No failed validation evidence exists in initial planning mode.",
        "analysis_invoked": False,
        "failure_evidence_fabricated": False,
        "replay_visible": True,
    }
    artifact["state_hash"] = replay_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _validate_ive_3_not_applicable(artifact: Any) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(
            "IVE-4 IVE-3 not-applicable state must be an object"
        )
    candidate = deepcopy(artifact)
    _verify_hash(
        candidate,
        "artifact_hash",
        "IVE-4 IVE-3 state artifact hash mismatch",
    )
    body = deepcopy(candidate)
    body.pop("artifact_hash")
    actual_state_hash = body.pop("state_hash", None)
    if (
        candidate.get("artifact_type") != "IVE_3_NOT_APPLICABLE_ARTIFACT_V1"
        or candidate.get("state_status") != IVE_3_NOT_APPLICABLE
        or candidate.get("analysis_invoked") is not False
        or candidate.get("failure_evidence_fabricated") is not False
        or actual_state_hash != replay_hash(body)
    ):
        raise FailClosedRuntimeError(
            "IVE-4 IVE-3 not-applicable state invalid"
        )
    return candidate


def _validate_stage_lineage(
    source: dict[str, Any],
    ive_0: dict[str, Any],
    ive_1: dict[str, Any],
    g38: dict[str, Any],
    ive_2: dict[str, Any],
    ive_3_state: dict[str, Any],
    planning_mode: str,
) -> None:
    if source["artifact_hash"] != g38["normalized_change_artifact_hash"]:
        raise FailClosedRuntimeError("IVE-4 source lineage mismatch")
    _validate_stage_lineage_without_source(
        ive_0,
        ive_1,
        g38,
        ive_2,
        ive_3_state,
        planning_mode,
    )


def _validate_stage_lineage_without_source(
    ive_0: dict[str, Any],
    ive_1: dict[str, Any],
    g38: dict[str, Any],
    ive_2: dict[str, Any],
    ive_3_state: dict[str, Any],
    planning_mode: str,
) -> None:
    if (
        ive_0["analysis_status"] == IVE_0_FAILED_CLOSED
        or ive_1["selection_status"] == IVE_1_FAILED_CLOSED
        or g38["entry_status"] == G38_FAILED_CLOSED
        or ive_2["schedule_status"] == IVE_2_FAILED_CLOSED
        or ive_1["source_ive_0_artifact_hash"] != ive_0["artifact_hash"]
        or g38["ive_0_artifact_hash"] != ive_0["artifact_hash"]
        or g38["ive_1_artifact_hash"] != ive_1["artifact_hash"]
        or ive_2["source_g38_artifact_hash"] != g38["artifact_hash"]
        or ive_2["source_ive_1_artifact_hash"] != ive_1["artifact_hash"]
    ):
        raise FailClosedRuntimeError("IVE-4 stage lineage mismatch")
    if planning_mode == FAILURE_REVALIDATION_PLANNING:
        if (
            ive_3_state["analysis_status"] == IVE_3_FAILED_CLOSED
            or ive_3_state["planning_lineage"][0]["artifact_hash"]
            != ive_0["artifact_hash"]
            or ive_3_state["planning_lineage"][1]["artifact_hash"]
            != ive_1["artifact_hash"]
            or ive_3_state["planning_lineage"][2]["artifact_hash"]
            != g38["artifact_hash"]
            or ive_3_state["planning_lineage"][3]["artifact_hash"]
            != ive_2["artifact_hash"]
        ):
            raise FailClosedRuntimeError("IVE-4 IVE-3 lineage mismatch")


def _validated_failure_context(
    value: dict[str, Any] | None,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(
            "IVE-4 failure re-planning requires failure_context"
        )
    required = (
        "validation_result_artifact",
        "validation_result_reference",
        "validation_result_hash",
        "validation_replay_dir",
        "failed_group_id",
        "failed_group_hash",
        "failed_requirement_hashes",
        "observed_by",
    )
    missing = [field for field in required if field not in value]
    if missing:
        raise FailClosedRuntimeError(
            f"IVE-4 failure_context missing fields: {', '.join(missing)}"
        )
    if set(value) != set(required):
        raise FailClosedRuntimeError(
            "IVE-4 failure_context contains unknown fields"
        )
    if not isinstance(value["validation_result_artifact"], dict):
        raise FailClosedRuntimeError(
            "IVE-4 failure_context result artifact invalid"
        )
    if not isinstance(value["failed_requirement_hashes"], list):
        raise FailClosedRuntimeError(
            "IVE-4 failure_context requirement hashes invalid"
        )
    for field in (
        "validation_result_reference",
        "validation_result_hash",
        "failed_group_id",
        "failed_group_hash",
        "observed_by",
    ):
        _require_string(value[field], f"failure_context.{field}")
    return deepcopy(value)


def _validate_failure_context_mode(
    mode: str,
    context: dict[str, Any] | None,
) -> None:
    if mode == INITIAL_VALIDATION_PLANNING and context is not None:
        raise FailClosedRuntimeError(
            "IVE-4 initial planning prohibits failure_context"
        )
    if mode == FAILURE_REVALIDATION_PLANNING and context is None:
        raise FailClosedRuntimeError(
            "IVE-4 failure re-planning requires failure_context"
        )


def _failed_bundle_artifact(
    *,
    orchestration_id: Any,
    session_id: Any,
    planning_mode: Any,
    normalized_change_artifact: Any,
    created_by: Any,
    created_at: Any,
    failure_reason: str,
) -> dict[str, Any]:
    source_hash = _safe_hash(
        normalized_change_artifact.get("artifact_hash")
        if isinstance(normalized_change_artifact, dict)
        else None
    )
    recommendation = {
        "recommendation_type": "FAILED_CLOSED_NO_PLANNING_RECOMMENDATION",
        "source_reference": "UNAVAILABLE",
        "source_hash": source_hash,
        "recommendation_only": True,
    }
    recommendation["recommendation_hash"] = replay_hash(recommendation)
    artifact = {
        "artifact_type": UNIFIED_VALIDATION_PLANNING_BUNDLE_ARTIFACT_V1,
        "runtime_version": INTELLIGENT_VALIDATION_ORCHESTRATOR_V4_RUNTIME_VERSION,
        "orchestration_id": _safe_string(orchestration_id),
        "session_id": _safe_string(session_id),
        "planning_mode": (
            planning_mode
            if planning_mode in {
                INITIAL_VALIDATION_PLANNING,
                FAILURE_REVALIDATION_PLANNING,
            }
            else "UNKNOWN"
        ),
        "bundle_status": FAILED_CLOSED,
        "source_normalized_change_reference": "UNAVAILABLE",
        "source_normalized_change_hash": source_hash,
        "source_normalized_change_artifact_hash": source_hash,
        "stage_artifacts": {},
        "stage_artifact_hashes": {},
        "stage_lineage": [],
        "stage_lineage_hash": replay_hash([]),
        "current_planning_recommendation": recommendation,
        "full_regression": {
            "required": True,
            "reason": "IVE-4 failure prohibits reduced-scope planning claims.",
            "mapping_authority": "IVE_4_FAIL_CLOSED_POLICY_V1",
        },
        "human_approval": {
            "required_before_execution": True,
            "approval_status": "BLOCKED",
            "must_bind_exact_candidate_hash": True,
            "approval_authorizes_execution_by_itself": False,
        },
        "orchestration_policy": {
            "certified_stages_invoked_unchanged": True,
            "ive_3_requires_failed_validation_evidence": True,
            "missing_required_evidence_fails_closed": True,
            "recommendation_only": True,
            "validation_execution_allowed": False,
            "automatic_repair_allowed": False,
            "parallel_runtime_dispatch_allowed": False,
            "scope_reduction_allowed": False,
        },
        "created_by": _safe_string(created_by),
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
    artifact["bundle_hash"] = _bundle_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _verify_bundle_artifact(artifact: dict[str, Any]) -> None:
    if (
        artifact.get("artifact_type")
        != UNIFIED_VALIDATION_PLANNING_BUNDLE_ARTIFACT_V1
        or artifact.get("runtime_version")
        != INTELLIGENT_VALIDATION_ORCHESTRATOR_V4_RUNTIME_VERSION
    ):
        raise FailClosedRuntimeError("IVE-4 bundle artifact type mismatch")
    _verify_hash(artifact, "artifact_hash", "IVE-4 artifact hash mismatch")
    if artifact.get("bundle_hash") != _bundle_hash(artifact):
        raise FailClosedRuntimeError("IVE-4 deterministic bundle hash mismatch")
    if artifact.get("bundle_status") not in {
        INITIAL_VALIDATION_PLANNING_BUNDLED,
        FAILURE_REVALIDATION_PLANNING_BUNDLED,
        FAILED_CLOSED,
    }:
        raise FailClosedRuntimeError("IVE-4 bundle status invalid")
    if (
        artifact.get("replay_visible") is not True
        or artifact.get("read_only") is not True
        or artifact.get("non_authoritative") is not True
        or artifact.get("authority_flags") != AUTHORITY_FLAGS
    ):
        raise FailClosedRuntimeError("IVE-4 boundary flags invalid")
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
            raise FailClosedRuntimeError(f"IVE-4 {field} must be false")
    if artifact.get("human_approval_required") is not True:
        raise FailClosedRuntimeError("IVE-4 Human Approval requirement missing")
    if artifact.get("orchestration_policy") != {
        "certified_stages_invoked_unchanged": True,
        "ive_3_requires_failed_validation_evidence": True,
        "missing_required_evidence_fails_closed": True,
        "recommendation_only": True,
        "validation_execution_allowed": False,
        "automatic_repair_allowed": False,
        "parallel_runtime_dispatch_allowed": False,
        "scope_reduction_allowed": False,
    }:
        raise FailClosedRuntimeError("IVE-4 orchestration policy invalid")
    _verify_embedded_hash(
        artifact.get("stage_lineage"),
        artifact.get("stage_lineage_hash"),
        "IVE-4 stage lineage hash mismatch",
    )
    recommendation = artifact.get("current_planning_recommendation")
    if not isinstance(recommendation, dict):
        raise FailClosedRuntimeError(
            "IVE-4 current planning recommendation invalid"
        )
    recommendation_body = deepcopy(recommendation)
    recommendation_hash = recommendation_body.pop(
        "recommendation_hash",
        None,
    )
    _verify_embedded_hash(
        recommendation_body,
        recommendation_hash,
        "IVE-4 recommendation hash mismatch",
    )
    if artifact["bundle_status"] == FAILED_CLOSED:
        if artifact.get("stage_artifacts") or artifact.get("stage_lineage"):
            raise FailClosedRuntimeError(
                "failed IVE-4 bundle cannot contain planning claims"
            )
        if artifact.get("full_regression", {}).get("required") is not True:
            raise FailClosedRuntimeError(
                "failed IVE-4 bundle must require full regression"
            )
        if not artifact.get("failure_reason"):
            raise FailClosedRuntimeError(
                "failed IVE-4 bundle requires failure reason"
            )
        if artifact.get("stage_artifact_hashes"):
            raise FailClosedRuntimeError(
                "failed IVE-4 bundle cannot claim stage hashes"
            )
    else:
        mode = artifact.get("planning_mode")
        expected_status = (
            INITIAL_VALIDATION_PLANNING_BUNDLED
            if mode == INITIAL_VALIDATION_PLANNING
            else FAILURE_REVALIDATION_PLANNING_BUNDLED
        )
        if (
            mode
            not in {
                INITIAL_VALIDATION_PLANNING,
                FAILURE_REVALIDATION_PLANNING,
            }
            or artifact["bundle_status"] != expected_status
        ):
            raise FailClosedRuntimeError(
                "IVE-4 planning mode and bundle status mismatch"
            )
        stages = artifact.get("stage_artifacts", {})
        if set(stages) != {
            "ive_0",
            "ive_1",
            "g38",
            "ive_2",
            "ive_3",
        } or len(artifact.get("stage_lineage", [])) != 5:
            raise FailClosedRuntimeError(
                "successful IVE-4 bundle requires all stage evidence"
            )
        if artifact.get("failure_reason") is not None:
            raise FailClosedRuntimeError(
                "successful IVE-4 bundle cannot contain failure reason"
            )
        if (
            artifact.get("human_approval", {}).get(
                "required_before_execution"
            )
            is not True
        ):
            raise FailClosedRuntimeError(
                "successful IVE-4 bundle bypasses Human Approval"
            )
        ive_0 = validate_intelligent_validation_plan_artifact(
            stages["ive_0"]
        )
        ive_1 = validate_semantic_validation_selection_artifact(
            stages["ive_1"]
        )
        g38 = validate_intelligent_validation_planning_entry_artifact(
            stages["g38"]
        )
        ive_2 = validate_parallel_validation_schedule_artifact(
            stages["ive_2"]
        )
        ive_3_state = (
            _validate_ive_3_not_applicable(stages["ive_3"])
            if mode == INITIAL_VALIDATION_PLANNING
            else validate_validation_failure_analysis_artifact(
                stages["ive_3"]
            )
        )
        expected_hashes = {
            key: value["artifact_hash"]
            for key, value in stages.items()
        }
        if artifact.get("stage_artifact_hashes") != expected_hashes:
            raise FailClosedRuntimeError(
                "IVE-4 stage artifact hashes mismatch"
            )
        if artifact.get("stage_lineage") != _stage_lineage(
            ive_0,
            ive_1,
            g38,
            ive_2,
            ive_3_state,
        ):
            raise FailClosedRuntimeError(
                "IVE-4 stage lineage artifact mismatch"
            )
        if (
            artifact.get("source_normalized_change_reference")
            != g38["normalized_change_reference"]
            or artifact.get("source_normalized_change_hash")
            != g38["normalized_change_hash"]
            or artifact.get("source_normalized_change_artifact_hash")
            != g38["normalized_change_artifact_hash"]
            or artifact.get("full_regression") != ive_2["full_regression"]
            or artifact.get("human_approval") != ive_2["human_approval"]
        ):
            raise FailClosedRuntimeError(
                "IVE-4 source or policy lineage mismatch"
            )
        if artifact["current_planning_recommendation"] != (
            _current_recommendation(mode, ive_2, ive_3_state)
        ):
            raise FailClosedRuntimeError(
                "IVE-4 current recommendation lineage mismatch"
            )
        _validate_stage_lineage_without_source(
            ive_0,
            ive_1,
            g38,
            ive_2,
            ive_3_state,
            mode,
        )


def _validate_source_binding(
    source: dict[str, Any],
    reference: str,
    source_hash: str,
) -> None:
    if (
        source.get("normalization_id") != reference
        or source.get("normalized_change_hash") != source_hash
    ):
        raise FailClosedRuntimeError(
            "IVE-4 normalized change binding mismatch"
        )


def _require_mode(value: Any) -> str:
    mode = _require_string(value, "planning_mode")
    if mode not in {
        INITIAL_VALIDATION_PLANNING,
        FAILURE_REVALIDATION_PLANNING,
    }:
        raise FailClosedRuntimeError("IVE-4 planning mode invalid")
    return mode


def _bundle_hash(artifact: dict[str, Any]) -> str:
    candidate = deepcopy(artifact)
    candidate.pop("artifact_hash", None)
    candidate.pop("bundle_hash", None)
    return replay_hash(candidate)


def _capture(artifact: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "runtime_version": INTELLIGENT_VALIDATION_ORCHESTRATOR_V4_RUNTIME_VERSION,
        "unified_validation_planning_bundle_artifact": deepcopy(artifact),
        "orchestration_id": artifact["orchestration_id"],
        "planning_mode": artifact["planning_mode"],
        "bundle_status": artifact["bundle_status"],
        "bundle_hash": artifact["bundle_hash"],
        "replay_reference": str(replay_path),
        "current_planning_recommendation": deepcopy(
            artifact["current_planning_recommendation"]
        ),
        "fail_closed": artifact["bundle_status"] == FAILED_CLOSED,
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
    source: dict[str, Any] | None,
    ive_0: dict[str, Any] | None,
    ive_1: dict[str, Any] | None,
    g38: dict[str, Any] | None,
    ive_2: dict[str, Any] | None,
    ive_3_state: dict[str, Any] | None,
    bundle: dict[str, Any],
) -> None:
    try:
        artifacts = (
            source or _unavailable_snapshot("NORMALIZED_CHANGE", bundle),
            ive_0 or _unavailable_snapshot("IVE_0", bundle),
            ive_1 or _unavailable_snapshot("IVE_1", bundle),
            g38 or _unavailable_snapshot("G38", bundle),
            ive_2 or _unavailable_snapshot("IVE_2", bundle),
            ive_3_state or _unavailable_snapshot("IVE_3", bundle),
            bundle,
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
    bundle: dict[str, Any],
) -> dict[str, Any]:
    artifact = {
        "artifact_type": f"{boundary}_UNAVAILABLE_V1",
        "boundary": boundary,
        "orchestration_id": bundle["orchestration_id"],
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
        raise FailClosedRuntimeError("IVE-4 replay ordering mismatch")
    _verify_hash(wrapper, "replay_hash", "IVE-4 replay hash mismatch")


def _ensure_replay_available(replay_path: Path) -> None:
    if any(
        (replay_path / f"{index:03d}_{step}.json").exists()
        for index, step in enumerate(REPLAY_STEPS)
    ):
        raise FailClosedRuntimeError(
            "IVE-4 failed closed: replay artifact already exists"
        )


def _verify_hash(value: dict[str, Any], field: str, message: str) -> None:
    actual = value.get(field)
    if not isinstance(actual, str) or not actual.startswith("sha256:"):
        raise FailClosedRuntimeError(message)
    expected = deepcopy(value)
    expected.pop(field, None)
    if replay_hash(expected) != actual:
        raise FailClosedRuntimeError(message)


def _verify_embedded_hash(value: Any, actual: Any, message: str) -> None:
    if (
        not isinstance(actual, str)
        or not actual.startswith("sha256:")
        or replay_hash(value) != actual
    ):
        raise FailClosedRuntimeError(message)


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"IVE-4 requires {field}")
    return value


def _require_hash(value: Any, field: str) -> str:
    text = _require_string(value, field)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(f"IVE-4 requires canonical {field}")
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
