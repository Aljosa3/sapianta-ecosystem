"""Deterministic, recommendation-only parallel validation scheduling."""

from __future__ import annotations

from copy import deepcopy
from itertools import combinations
from pathlib import Path
from typing import Any

from aigol.runtime.intelligent_validation_engine_v0 import (
    COMPONENT_CLASSIFICATION_ORDER,
)
from aigol.runtime.intelligent_validation_engine_v1 import (
    REPLAY_STEPS as IVE_1_REPLAY_STEPS,
    validate_semantic_validation_dependency_model,
    validate_semantic_validation_selection_artifact,
)
from aigol.runtime.intelligent_validation_entry_integration_runtime import (
    FAILED_CLOSED as G38_FAILED_CLOSED,
    REPLAY_STEP as G38_REPLAY_STEP,
    reconstruct_intelligent_validation_entry_replay,
    validate_intelligent_validation_planning_entry_artifact,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import (
    load_json,
    replay_hash,
    write_json_immutable,
)


INTELLIGENT_VALIDATION_ENGINE_V2_RUNTIME_VERSION = (
    "G39_01_INTELLIGENT_VALIDATION_ENGINE_V2_RUNTIME_V1"
)
PARALLEL_VALIDATION_SCHEDULE_ARTIFACT_V1 = (
    "PARALLEL_VALIDATION_SCHEDULE_ARTIFACT_V1"
)
PARALLEL_VALIDATION_SCHEDULE_RECOMMENDED = (
    "PARALLEL_VALIDATION_SCHEDULE_RECOMMENDED"
)
FAILED_CLOSED = "FAILED_CLOSED"
REPLAY_STEPS = (
    "g38_validation_plan_bound",
    "ive_1_semantic_selection_bound",
    "parallel_validation_schedule_recorded",
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
}


def recommend_parallel_validation_schedule(
    *,
    schedule_id: str,
    session_id: str,
    g38_validation_plan_artifact: dict[str, Any],
    g38_validation_plan_reference: str,
    g38_validation_plan_hash: str,
    g38_replay_dir: str | Path,
    created_by: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Recommend deterministic waves without creating or executing work."""

    replay_path = Path(replay_dir)
    source: dict[str, Any] | None = None
    selection: dict[str, Any] | None = None
    try:
        _ensure_replay_available(replay_path)
        identifier = _require_string(schedule_id, "schedule_id")
        session = _require_string(session_id, "session_id")
        source_reference = _require_string(
            g38_validation_plan_reference,
            "g38_validation_plan_reference",
        )
        source_hash = _require_hash(
            g38_validation_plan_hash,
            "g38_validation_plan_hash",
        )
        creator = _require_string(created_by, "created_by")
        timestamp = _require_string(created_at, "created_at")
        source = validate_intelligent_validation_planning_entry_artifact(
            g38_validation_plan_artifact
        )
        _validate_g38_binding(source, source_reference, source_hash)

        g38_replay_path = Path(g38_replay_dir)
        reconstructed = reconstruct_intelligent_validation_entry_replay(
            g38_replay_path
        )
        _validate_g38_replay_binding(source, reconstructed)
        selection_wrapper = load_json(
            g38_replay_path
            / "ive_1/001_semantic_validation_selection_recorded.json"
        )
        selection = validate_semantic_validation_selection_artifact(
            selection_wrapper.get("artifact")
        )
        _validate_ive_1_binding(source, selection)
        model = validate_semantic_validation_dependency_model(
            selection["semantic_dependency_model"]
        )
        schedule = _deterministic_schedule(source, selection, model)
        artifact = _schedule_artifact(
            schedule_id=identifier,
            session_id=session,
            schedule_status=PARALLEL_VALIDATION_SCHEDULE_RECOMMENDED,
            source=source,
            source_replay_hash=reconstructed["replay_hash"],
            selection=selection,
            selection_replay_hash=selection_wrapper["replay_hash"],
            groups=schedule["groups"],
            waves=schedule["waves"],
            independence_evidence=schedule["independence_evidence"],
            maximum_recommended_concurrency=schedule[
                "maximum_recommended_concurrency"
            ],
            created_by=creator,
            created_at=timestamp,
            failure_reason=None,
        )
    except Exception as exc:
        artifact = _failed_schedule_artifact(
            schedule_id=schedule_id,
            session_id=session_id,
            source=g38_validation_plan_artifact,
            source_reference=g38_validation_plan_reference,
            source_hash=g38_validation_plan_hash,
            selection=selection,
            created_by=created_by,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
    _persist_replay(replay_path, source, selection, artifact)
    return _capture(artifact, replay_path)


def validate_parallel_validation_schedule_artifact(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Validate one immutable IVE-2 scheduling recommendation."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(
            "IVE-2 schedule artifact must be a JSON object"
        )
    candidate = deepcopy(artifact)
    _verify_schedule_artifact(candidate)
    return candidate


def reconstruct_parallel_validation_schedule_replay(
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Reconstruct source bindings and deterministic scheduling evidence."""

    replay_path = Path(replay_dir)
    wrappers = [
        load_json(replay_path / f"{index:03d}_{step}.json")
        for index, step in enumerate(REPLAY_STEPS)
    ]
    for index, (step, wrapper) in enumerate(zip(REPLAY_STEPS, wrappers)):
        _verify_wrapper(wrapper, index, step)
    artifact = validate_parallel_validation_schedule_artifact(
        wrappers[2].get("artifact")
    )

    if artifact["schedule_status"] != FAILED_CLOSED:
        source = validate_intelligent_validation_planning_entry_artifact(
            wrappers[0].get("artifact")
        )
        selection = validate_semantic_validation_selection_artifact(
            wrappers[1].get("artifact")
        )
        _validate_replay_lineage(artifact, source, selection)
        model = validate_semantic_validation_dependency_model(
            selection["semantic_dependency_model"]
        )
        expected = _deterministic_schedule(source, selection, model)
        for field in (
            "groups",
            "waves",
            "independence_evidence",
            "maximum_recommended_concurrency",
        ):
            if artifact[field] != expected[field]:
                raise FailClosedRuntimeError(
                    f"IVE-2 replay scheduling mismatch: {field}"
                )

    return {
        "schedule_id": artifact["schedule_id"],
        "schedule_status": artifact["schedule_status"],
        "source_g38_reference": artifact["source_g38_reference"],
        "groups": deepcopy(artifact["groups"]),
        "waves": deepcopy(artifact["waves"]),
        "independence_evidence": deepcopy(
            artifact["independence_evidence"]
        ),
        "maximum_recommended_concurrency": artifact[
            "maximum_recommended_concurrency"
        ],
        "schedule_hash": artifact["schedule_hash"],
        "artifact_hash": artifact["artifact_hash"],
        "replay_visible": True,
        "fail_closed": artifact["schedule_status"] == FAILED_CLOSED,
        "failure_reason": artifact["failure_reason"],
        "human_approval_required": True,
        "validation_executed": False,
        "authority_flags": deepcopy(artifact["authority_flags"]),
        "source_replay_hash": wrappers[0]["replay_hash"],
        "selection_replay_hash": wrappers[1]["replay_hash"],
        "schedule_replay_hash": wrappers[2]["replay_hash"],
    }


def _deterministic_schedule(
    source: dict[str, Any],
    selection: dict[str, Any],
    model: dict[str, Any],
) -> dict[str, Any]:
    if source["selected_validation_requirements"] != selection[
        "selected_validation_requirements"
    ]:
        raise FailClosedRuntimeError(
            "IVE-2 source requirements differ from IVE-1 selection"
        )
    if source["transitive_dependencies"] != selection[
        "transitive_dependencies"
    ]:
        raise FailClosedRuntimeError(
            "IVE-2 source dependencies differ from IVE-1 selection"
        )
    groups = _requirement_groups(source, selection, model)
    edges = _group_dependency_edges(groups, model)
    groups = _bind_group_dependencies(groups, edges)
    if source["full_regression"]["required"] is True:
        groups, edges = _append_full_regression_barrier(
            groups,
            edges,
            source["full_regression"],
        )
    waves = _topological_waves(groups, edges)
    independence = _independence_evidence(waves, groups, edges, model)
    maximum = max((len(wave["group_ids"]) for wave in waves), default=0)
    return {
        "groups": groups,
        "waves": waves,
        "independence_evidence": independence,
        "maximum_recommended_concurrency": maximum,
    }


def _requirement_groups(
    source: dict[str, Any],
    selection: dict[str, Any],
    model: dict[str, Any],
) -> list[dict[str, Any]]:
    requirements = source["selected_validation_requirements"]
    if not isinstance(requirements, list) or not requirements:
        raise FailClosedRuntimeError(
            "IVE-2 requires selected validation requirements"
        )
    direct_types = {
        item["component_type"] for item in source["direct_validation_subjects"]
    }
    known_component_types = set(COMPONENT_CLASSIFICATION_ORDER)
    capability_nodes = {
        node
        for edge in model["capability_dependencies"]
        for node in (
            edge["required_capability"],
            edge["dependent_capability"],
        )
    }
    dependency_by_hash = {
        item["dependency_hash"]: item
        for item in selection["transitive_dependencies"]
    }
    buckets: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for requirement in requirements:
        kind = requirement["validation_subject_kind"]
        identifier = requirement["validation_subject_identifier"]
        namespace = _requirement_namespace(kind)
        if namespace == "COMPONENT_TYPE":
            if identifier not in known_component_types:
                raise FailClosedRuntimeError(
                    "IVE-2 encountered unknown component dependency subject"
                )
            if kind == "IVE_0_AFFECTED_COMPONENT" and identifier not in direct_types:
                raise FailClosedRuntimeError(
                    "IVE-2 direct component subject is not bound to G38"
                )
        elif identifier not in capability_nodes:
            raise FailClosedRuntimeError(
                "IVE-2 encountered unknown capability dependency subject"
            )
        _validate_requirement_dependency_evidence(
            requirement,
            namespace,
            identifier,
            dependency_by_hash,
        )
        buckets.setdefault((namespace, identifier), []).append(
            deepcopy(requirement)
        )

    groups = []
    for index, ((namespace, identifier), members) in enumerate(
        sorted(buckets.items())
    ):
        members.sort(
            key=lambda item: (
                item["selection_requirement_index"],
                item["selection_requirement_hash"],
            )
        )
        group = {
            "group_id": f"IVE-2-VALIDATION-GROUP-{index:04d}",
            "group_kind": "VALIDATION_SUBJECT",
            "dependency_namespace": namespace,
            "validation_subject_identifier": identifier,
            "requirement_ids": [
                item["selection_requirement_id"] for item in members
            ],
            "requirement_hashes": [
                item["selection_requirement_hash"] for item in members
            ],
            "requirements": members,
            "depends_on_group_ids": [],
            "intra_group_parallelism_allowed": False,
            "recommendation_only": True,
        }
        group["group_hash"] = replay_hash(group)
        groups.append(group)
    return groups


def _requirement_namespace(kind: str) -> str:
    if kind in {
        "IVE_0_AFFECTED_COMPONENT",
        "CONSTITUTIONAL_COMPONENT_TYPE",
    }:
        return "COMPONENT_TYPE"
    if kind == "CERTIFIED_DEPENDENT_CAPABILITY":
        return "CAPABILITY"
    raise FailClosedRuntimeError(
        "IVE-2 encountered unknown validation subject kind"
    )


def _validate_requirement_dependency_evidence(
    requirement: dict[str, Any],
    namespace: str,
    identifier: str,
    dependency_by_hash: dict[str, dict[str, Any]],
) -> None:
    evidence_hashes = requirement.get("dependency_evidence_hashes")
    if not isinstance(evidence_hashes, list):
        raise FailClosedRuntimeError(
            "IVE-2 requirement dependency evidence is invalid"
        )
    if requirement["validation_scope"] == "DIRECT":
        if evidence_hashes:
            raise FailClosedRuntimeError(
                "IVE-2 direct requirement has transitive dependency evidence"
            )
        return
    if not evidence_hashes:
        raise FailClosedRuntimeError(
            "IVE-2 transitive requirement lacks dependency evidence"
        )
    expected_kind = (
        "COMPONENT_TYPE" if namespace == "COMPONENT_TYPE" else "CAPABILITY"
    )
    for evidence_hash in evidence_hashes:
        dependency = dependency_by_hash.get(evidence_hash)
        if (
            dependency is None
            or dependency.get("dependency_kind") != expected_kind
            or dependency.get("dependent_identifier") != identifier
        ):
            raise FailClosedRuntimeError(
                "IVE-2 encountered unknown or mismatched dependency evidence"
            )


def _group_dependency_edges(
    groups: list[dict[str, Any]],
    model: dict[str, Any],
) -> set[tuple[str, str]]:
    by_subject = {
        (
            group["dependency_namespace"],
            group["validation_subject_identifier"],
        ): group["group_id"]
        for group in groups
    }
    edges: set[tuple[str, str]] = set()
    for edge in model["component_type_dependencies"]:
        source_id = by_subject.get(
            ("COMPONENT_TYPE", edge["source_component_type"])
        )
        target_id = by_subject.get(
            ("COMPONENT_TYPE", edge["dependent_component_type"])
        )
        if source_id and target_id:
            edges.add((source_id, target_id))
    for edge in model["capability_dependencies"]:
        source_id = by_subject.get(("CAPABILITY", edge["required_capability"]))
        target_id = by_subject.get(("CAPABILITY", edge["dependent_capability"]))
        if source_id and target_id:
            edges.add((source_id, target_id))

    component_ids = [
        group["group_id"]
        for group in groups
        if group["dependency_namespace"] == "COMPONENT_TYPE"
    ]
    capability_ids = [
        group["group_id"]
        for group in groups
        if group["dependency_namespace"] == "CAPABILITY"
    ]
    for component_id in component_ids:
        for capability_id in capability_ids:
            edges.add((component_id, capability_id))
    return edges


def _bind_group_dependencies(
    groups: list[dict[str, Any]],
    edges: set[tuple[str, str]],
) -> list[dict[str, Any]]:
    bound = []
    for group in groups:
        candidate = deepcopy(group)
        candidate["depends_on_group_ids"] = sorted(
            source for source, target in edges if target == group["group_id"]
        )
        candidate["group_hash"] = _group_hash(candidate)
        bound.append(candidate)
    return bound


def _append_full_regression_barrier(
    groups: list[dict[str, Any]],
    edges: set[tuple[str, str]],
    full_regression: dict[str, Any],
) -> tuple[list[dict[str, Any]], set[tuple[str, str]]]:
    barrier_id = "IVE-2-FULL-REGRESSION-BARRIER"
    dependencies = sorted(group["group_id"] for group in groups)
    barrier = {
        "group_id": barrier_id,
        "group_kind": "FULL_REGRESSION_BARRIER",
        "dependency_namespace": "FULL_REGRESSION",
        "validation_subject_identifier": "FULL_REPOSITORY_REGRESSION",
        "requirement_ids": [],
        "requirement_hashes": [replay_hash(full_regression)],
        "requirements": [],
        "depends_on_group_ids": dependencies,
        "intra_group_parallelism_allowed": False,
        "recommendation_only": True,
    }
    barrier["group_hash"] = replay_hash(barrier)
    updated_edges = set(edges)
    updated_edges.update((group_id, barrier_id) for group_id in dependencies)
    return [*groups, barrier], updated_edges


def _topological_waves(
    groups: list[dict[str, Any]],
    edges: set[tuple[str, str]],
) -> list[dict[str, Any]]:
    group_ids = {group["group_id"] for group in groups}
    if any(source not in group_ids or target not in group_ids for source, target in edges):
        raise FailClosedRuntimeError("IVE-2 scheduling edge references unknown group")
    predecessors = {
        group_id: {source for source, target in edges if target == group_id}
        for group_id in group_ids
    }
    unscheduled = set(group_ids)
    completed: set[str] = set()
    waves = []
    while unscheduled:
        ready = sorted(
            group_id
            for group_id in unscheduled
            if predecessors[group_id].issubset(completed)
        )
        if not ready:
            raise FailClosedRuntimeError(
                "IVE-2 dependency graph is cyclic or unresolved"
            )
        namespaces = {
            next(
                group["dependency_namespace"]
                for group in groups
                if group["group_id"] == group_id
            )
            for group_id in ready
        }
        if len(namespaces) != 1:
            raise FailClosedRuntimeError(
                "IVE-2 cannot prove cross-namespace independence"
            )
        wave = {
            "wave_index": len(waves),
            "wave_id": f"IVE-2-SCHEDULE-WAVE-{len(waves):04d}",
            "dependency_namespace": next(iter(namespaces)),
            "group_ids": ready,
            "group_hashes": [
                next(
                    group["group_hash"]
                    for group in groups
                    if group["group_id"] == group_id
                )
                for group_id in ready
            ],
            "execution_mode_recommendation": (
                "PARALLEL_ELIGIBLE_AFTER_EXISTING_APPROVAL_AND_AUTHORIZATION"
                if len(ready) > 1
                else "SEQUENTIAL_SINGLE_GROUP"
            ),
            "recommendation_only": True,
        }
        wave["wave_hash"] = replay_hash(wave)
        waves.append(wave)
        unscheduled.difference_update(ready)
        completed.update(ready)
    return waves


def _independence_evidence(
    waves: list[dict[str, Any]],
    groups: list[dict[str, Any]],
    edges: set[tuple[str, str]],
    model: dict[str, Any],
) -> list[dict[str, Any]]:
    adjacency: dict[str, set[str]] = {}
    for source, target in edges:
        adjacency.setdefault(source, set()).add(target)
    evidence = []
    group_by_id = {group["group_id"]: group for group in groups}
    for wave in waves:
        for left, right in combinations(wave["group_ids"], 2):
            if _reachable(left, right, adjacency) or _reachable(
                right,
                left,
                adjacency,
            ):
                raise FailClosedRuntimeError(
                    "IVE-2 parallel wave contains dependent groups"
                )
            left_group = group_by_id[left]
            right_group = group_by_id[right]
            if (
                left_group["dependency_namespace"]
                != right_group["dependency_namespace"]
                or left_group["dependency_namespace"] == "FULL_REGRESSION"
            ):
                raise FailClosedRuntimeError(
                    "IVE-2 cannot prove group independence"
                )
            item = {
                "wave_id": wave["wave_id"],
                "left_group_id": left,
                "left_group_hash": left_group["group_hash"],
                "right_group_id": right,
                "right_group_hash": right_group["group_hash"],
                "dependency_namespace": left_group["dependency_namespace"],
                "dependency_model_hash": model["dependency_model_hash"],
                "path_left_to_right": False,
                "path_right_to_left": False,
                "independence_scope": (
                    "CANONICAL_DECLARED_DEPENDENCY_MODEL_ONLY"
                ),
                "unknown_dependency_inference_used": False,
            }
            item["independence_hash"] = replay_hash(item)
            evidence.append(item)
    return evidence


def _reachable(
    origin: str,
    target: str,
    adjacency: dict[str, set[str]],
) -> bool:
    pending = list(sorted(adjacency.get(origin, set()), reverse=True))
    visited: set[str] = set()
    while pending:
        current = pending.pop()
        if current == target:
            return True
        if current in visited:
            continue
        visited.add(current)
        pending.extend(
            sorted(adjacency.get(current, set()) - visited, reverse=True)
        )
    return False


def _schedule_artifact(
    *,
    schedule_id: str,
    session_id: str,
    schedule_status: str,
    source: dict[str, Any],
    source_replay_hash: str,
    selection: dict[str, Any],
    selection_replay_hash: str,
    groups: list[dict[str, Any]],
    waves: list[dict[str, Any]],
    independence_evidence: list[dict[str, Any]],
    maximum_recommended_concurrency: int,
    created_by: str,
    created_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": PARALLEL_VALIDATION_SCHEDULE_ARTIFACT_V1,
        "runtime_version": INTELLIGENT_VALIDATION_ENGINE_V2_RUNTIME_VERSION,
        "schedule_id": schedule_id,
        "session_id": session_id,
        "schedule_status": schedule_status,
        "source_artifact_type": source["artifact_type"],
        "source_g38_reference": source["entry_id"],
        "source_g38_planning_entry_hash": source["planning_entry_hash"],
        "source_g38_artifact_hash": source["artifact_hash"],
        "source_g38_replay_hash": source_replay_hash,
        "source_ive_1_reference": selection["selection_id"],
        "source_ive_1_selection_hash": selection[
            "semantic_validation_selection_hash"
        ],
        "source_ive_1_artifact_hash": selection["artifact_hash"],
        "source_ive_1_replay_hash": selection_replay_hash,
        "semantic_dependency_model_hash": selection[
            "semantic_dependency_model_hash"
        ],
        "groups": deepcopy(groups),
        "group_count": len(groups),
        "waves": deepcopy(waves),
        "wave_count": len(waves),
        "independence_evidence": deepcopy(independence_evidence),
        "independence_evidence_count": len(independence_evidence),
        "maximum_recommended_concurrency": maximum_recommended_concurrency,
        "full_regression": deepcopy(source["full_regression"]),
        "existing_allowlisted_command_references": deepcopy(
            source["existing_allowlisted_command_references"]
        ),
        "existing_validation_pipeline_handoff": deepcopy(
            source["existing_validation_pipeline_handoff"]
        ),
        "human_approval": deepcopy(source["human_approval"]),
        "scheduling_policy": {
            "recommendation_only": True,
            "canonical_declared_dependencies_only": True,
            "unknown_dependencies_fail_closed": True,
            "cross_namespace_parallelism_allowed": False,
            "requirements_within_group_remain_sequential": True,
            "full_regression_is_terminal_barrier": True,
            "validation_scope_reduction_allowed": False,
            "command_synthesis_allowed": False,
            "validation_execution_allowed": False,
            "pytest_modification_allowed": False,
        },
        "created_by": created_by,
        "created_at": created_at,
        "replay_visible": True,
        "read_only": True,
        "non_authoritative": True,
        "human_approval_required": True,
        "human_approval_recorded": False,
        "validation_candidate_constructed": False,
        "validation_executed": False,
        "authorization_invoked": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "aicli_invoked": False,
        "repository_mutated": False,
        "replay_semantics_modified": False,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "failure_reason": failure_reason,
    }
    artifact["schedule_hash"] = _schedule_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_schedule_artifact(
    *,
    schedule_id: Any,
    session_id: Any,
    source: Any,
    source_reference: Any,
    source_hash: Any,
    selection: dict[str, Any] | None,
    created_by: Any,
    created_at: Any,
    failure_reason: str,
) -> dict[str, Any]:
    unavailable = replay_hash({"unavailable": "G39-01"})
    failed_source = {
        "artifact_type": (
            source.get("artifact_type")
            if isinstance(source, dict)
            else "G38_VALIDATION_PLAN_UNAVAILABLE_V1"
        ),
        "entry_id": _safe_string(source_reference),
        "planning_entry_hash": _safe_hash(source_hash),
        "artifact_hash": _safe_hash(
            source.get("artifact_hash")
            if isinstance(source, dict)
            else unavailable
        ),
        "full_regression": {
            "required": True,
            "reason": "IVE-2 failure prohibits parallel or reduced-scope claims.",
            "mapping_authority": "IVE_2_FAIL_CLOSED_POLICY_V1",
        },
        "existing_allowlisted_command_references": [],
        "existing_validation_pipeline_handoff": {
            "status": "BLOCKED_BY_IVE_2_FAILURE",
            "candidate_composition_owner": (
                "PLATFORM_VALIDATION_PLAN_TO_CANDIDATE_COMPOSITION"
            ),
            "human_approval_owner": "PLATFORM_CORE_VALIDATION_GOVERNANCE",
            "execution_owner": "EXISTING_GOVERNED_VALIDATION_RUNTIME",
            "new_command_synthesis_allowed": False,
            "allowlist_expansion_allowed": False,
        },
        "human_approval": {
            "required_before_execution": True,
            "recorded_by_ive_0": False,
            "approval_status": "BLOCKED",
            "must_bind_exact_candidate_hash": True,
            "approval_authorizes_execution_by_itself": False,
        },
    }
    failed_selection = {
        "selection_id": _safe_string((selection or {}).get("selection_id")),
        "semantic_validation_selection_hash": _safe_hash(
            (selection or {}).get("semantic_validation_selection_hash")
        ),
        "artifact_hash": _safe_hash((selection or {}).get("artifact_hash")),
        "semantic_dependency_model_hash": _safe_hash(
            (selection or {}).get("semantic_dependency_model_hash")
        ),
    }
    return _schedule_artifact(
        schedule_id=_safe_string(schedule_id),
        session_id=_safe_string(session_id),
        schedule_status=FAILED_CLOSED,
        source=failed_source,
        source_replay_hash=unavailable,
        selection=failed_selection,
        selection_replay_hash=unavailable,
        groups=[],
        waves=[],
        independence_evidence=[],
        maximum_recommended_concurrency=0,
        created_by=_safe_string(created_by),
        created_at=_safe_string(created_at),
        failure_reason=failure_reason,
    )


def _verify_schedule_artifact(artifact: dict[str, Any]) -> None:
    if artifact.get("artifact_type") != PARALLEL_VALIDATION_SCHEDULE_ARTIFACT_V1:
        raise FailClosedRuntimeError("IVE-2 schedule artifact type mismatch")
    _verify_hash(artifact, "artifact_hash", "IVE-2 artifact hash mismatch")
    if artifact.get("schedule_hash") != _schedule_hash(artifact):
        raise FailClosedRuntimeError("IVE-2 deterministic schedule hash mismatch")
    if artifact.get("schedule_status") not in {
        PARALLEL_VALIDATION_SCHEDULE_RECOMMENDED,
        FAILED_CLOSED,
    }:
        raise FailClosedRuntimeError("IVE-2 schedule status invalid")
    if (
        artifact.get("replay_visible") is not True
        or artifact.get("read_only") is not True
        or artifact.get("non_authoritative") is not True
    ):
        raise FailClosedRuntimeError("IVE-2 boundary flags invalid")
    if artifact.get("authority_flags") != AUTHORITY_FLAGS:
        raise FailClosedRuntimeError("IVE-2 authority flags invalid")
    for field in (
        "human_approval_recorded",
        "validation_candidate_constructed",
        "validation_executed",
        "authorization_invoked",
        "worker_invoked",
        "provider_invoked",
        "aicli_invoked",
        "repository_mutated",
        "replay_semantics_modified",
    ):
        if artifact.get(field) is not False:
            raise FailClosedRuntimeError(f"IVE-2 {field} must be false")
    if artifact.get("human_approval_required") is not True:
        raise FailClosedRuntimeError("IVE-2 Human Approval requirement missing")
    approval = artifact.get("human_approval")
    if (
        not isinstance(approval, dict)
        or approval.get("required_before_execution") is not True
        or approval.get("must_bind_exact_candidate_hash") is not True
        or approval.get("approval_authorizes_execution_by_itself") is not False
    ):
        raise FailClosedRuntimeError("IVE-2 Human Approval boundary invalid")
    policy = artifact.get("scheduling_policy")
    if not isinstance(policy, dict) or policy != {
        "recommendation_only": True,
        "canonical_declared_dependencies_only": True,
        "unknown_dependencies_fail_closed": True,
        "cross_namespace_parallelism_allowed": False,
        "requirements_within_group_remain_sequential": True,
        "full_regression_is_terminal_barrier": True,
        "validation_scope_reduction_allowed": False,
        "command_synthesis_allowed": False,
        "validation_execution_allowed": False,
        "pytest_modification_allowed": False,
    }:
        raise FailClosedRuntimeError("IVE-2 scheduling policy invalid")
    groups = artifact.get("groups")
    waves = artifact.get("waves")
    evidence = artifact.get("independence_evidence")
    if (
        not isinstance(groups, list)
        or artifact.get("group_count") != len(groups)
        or not isinstance(waves, list)
        or artifact.get("wave_count") != len(waves)
        or not isinstance(evidence, list)
        or artifact.get("independence_evidence_count") != len(evidence)
    ):
        raise FailClosedRuntimeError("IVE-2 schedule evidence counts mismatch")
    for group in groups:
        if group.get("group_hash") != _group_hash(group):
            raise FailClosedRuntimeError("IVE-2 group hash mismatch")
        if group.get("intra_group_parallelism_allowed") is not False:
            raise FailClosedRuntimeError(
                "IVE-2 cannot parallelize within a validation subject"
            )
    for wave in waves:
        _verify_hash(wave, "wave_hash", "IVE-2 wave hash mismatch")
    for item in evidence:
        _verify_hash(
            item,
            "independence_hash",
            "IVE-2 independence evidence hash mismatch",
        )
        if (
            item.get("path_left_to_right") is not False
            or item.get("path_right_to_left") is not False
            or item.get("unknown_dependency_inference_used") is not False
        ):
            raise FailClosedRuntimeError(
                "IVE-2 independence evidence is not fail-closed"
            )
    if artifact["schedule_status"] == FAILED_CLOSED:
        if groups or waves or evidence:
            raise FailClosedRuntimeError(
                "failed IVE-2 schedule cannot contain scheduling claims"
            )
        if artifact.get("maximum_recommended_concurrency") != 0:
            raise FailClosedRuntimeError(
                "failed IVE-2 schedule cannot recommend concurrency"
            )
        if artifact.get("full_regression", {}).get("required") is not True:
            raise FailClosedRuntimeError(
                "failed IVE-2 schedule must require full regression"
            )
        if (
            artifact.get("existing_validation_pipeline_handoff", {}).get(
                "status"
            )
            != "BLOCKED_BY_IVE_2_FAILURE"
        ):
            raise FailClosedRuntimeError(
                "failed IVE-2 schedule must block handoff"
            )
        if not artifact.get("failure_reason"):
            raise FailClosedRuntimeError(
                "failed IVE-2 schedule requires failure reason"
            )
    else:
        if not groups or not waves:
            raise FailClosedRuntimeError(
                "successful IVE-2 schedule requires recommendation groups"
            )
        if artifact.get("maximum_recommended_concurrency", 0) < 1:
            raise FailClosedRuntimeError(
                "successful IVE-2 concurrency evidence invalid"
            )
        if artifact.get("failure_reason") is not None:
            raise FailClosedRuntimeError(
                "successful IVE-2 schedule cannot contain failure reason"
            )


def _validate_g38_binding(
    source: dict[str, Any],
    reference: str,
    source_hash: str,
) -> None:
    if source.get("entry_status") == G38_FAILED_CLOSED:
        raise FailClosedRuntimeError("IVE-2 source G38 plan failed closed")
    if source.get("entry_id") != reference:
        raise FailClosedRuntimeError("IVE-2 source G38 reference mismatch")
    if source.get("planning_entry_hash") != source_hash:
        raise FailClosedRuntimeError("IVE-2 source G38 plan hash mismatch")


def _validate_g38_replay_binding(
    source: dict[str, Any],
    reconstructed: dict[str, Any],
) -> None:
    if reconstructed["fail_closed"] is True:
        raise FailClosedRuntimeError("IVE-2 source G38 replay failed closed")
    if (
        reconstructed["entry_id"] != source["entry_id"]
        or reconstructed["planning_entry_hash"] != source["planning_entry_hash"]
        or reconstructed["artifact_hash"] != source["artifact_hash"]
    ):
        raise FailClosedRuntimeError("IVE-2 source G38 replay lineage mismatch")


def _validate_ive_1_binding(
    source: dict[str, Any],
    selection: dict[str, Any],
) -> None:
    if (
        selection["selection_id"] != source["ive_1_reference"]
        or selection["semantic_validation_selection_hash"]
        != source["ive_1_selection_hash"]
        or selection["artifact_hash"] != source["ive_1_artifact_hash"]
    ):
        raise FailClosedRuntimeError("IVE-2 IVE-1 source lineage mismatch")


def _validate_replay_lineage(
    artifact: dict[str, Any],
    source: dict[str, Any],
    selection: dict[str, Any],
) -> None:
    if (
        artifact["source_g38_reference"] != source["entry_id"]
        or artifact["source_g38_planning_entry_hash"]
        != source["planning_entry_hash"]
        or artifact["source_g38_artifact_hash"] != source["artifact_hash"]
    ):
        raise FailClosedRuntimeError("IVE-2 replay G38 lineage mismatch")
    expected_g38_wrapper = {
        "replay_index": 0,
        "replay_step": G38_REPLAY_STEP,
        "artifact": deepcopy(source),
    }
    if artifact["source_g38_replay_hash"] != replay_hash(
        expected_g38_wrapper
    ):
        raise FailClosedRuntimeError("IVE-2 source G38 replay hash mismatch")
    if (
        artifact["source_ive_1_reference"] != selection["selection_id"]
        or artifact["source_ive_1_selection_hash"]
        != selection["semantic_validation_selection_hash"]
        or artifact["source_ive_1_artifact_hash"] != selection["artifact_hash"]
        or artifact["semantic_dependency_model_hash"]
        != selection["semantic_dependency_model_hash"]
    ):
        raise FailClosedRuntimeError("IVE-2 replay IVE-1 lineage mismatch")
    expected_selection_wrapper = {
        "replay_index": 1,
        "replay_step": IVE_1_REPLAY_STEPS[1],
        "artifact": deepcopy(selection),
    }
    if artifact["source_ive_1_replay_hash"] != replay_hash(
        expected_selection_wrapper
    ):
        raise FailClosedRuntimeError(
            "IVE-2 source IVE-1 replay hash mismatch"
        )
    for field in (
        "full_regression",
        "existing_allowlisted_command_references",
        "existing_validation_pipeline_handoff",
        "human_approval",
    ):
        if artifact[field] != source[field]:
            raise FailClosedRuntimeError(
                f"IVE-2 altered G38 source field: {field}"
            )


def _schedule_hash(artifact: dict[str, Any]) -> str:
    candidate = deepcopy(artifact)
    candidate.pop("artifact_hash", None)
    candidate.pop("schedule_hash", None)
    return replay_hash(candidate)


def _group_hash(group: dict[str, Any]) -> str:
    candidate = deepcopy(group)
    candidate.pop("group_hash", None)
    return replay_hash(candidate)


def _capture(artifact: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "runtime_version": INTELLIGENT_VALIDATION_ENGINE_V2_RUNTIME_VERSION,
        "parallel_validation_schedule_artifact": deepcopy(artifact),
        "schedule_id": artifact["schedule_id"],
        "schedule_status": artifact["schedule_status"],
        "schedule_hash": artifact["schedule_hash"],
        "replay_reference": str(replay_path),
        "groups": deepcopy(artifact["groups"]),
        "waves": deepcopy(artifact["waves"]),
        "maximum_recommended_concurrency": artifact[
            "maximum_recommended_concurrency"
        ],
        "fail_closed": artifact["schedule_status"] == FAILED_CLOSED,
        "failure_reason": artifact["failure_reason"],
        "human_approval_required": True,
        "validation_executed": False,
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
    selection: dict[str, Any] | None,
    artifact: dict[str, Any],
) -> None:
    try:
        source_artifact = (
            deepcopy(source)
            if isinstance(source, dict)
            else _unavailable_source_snapshot(artifact)
        )
        selection_artifact = (
            deepcopy(selection)
            if isinstance(selection, dict)
            else _unavailable_selection_snapshot(artifact)
        )
        for index, (step, replay_artifact) in enumerate(
            zip(
                REPLAY_STEPS,
                (source_artifact, selection_artifact, artifact),
            )
        ):
            wrapper = {
                "replay_index": index,
                "replay_step": step,
                "artifact": replay_artifact,
            }
            wrapper["replay_hash"] = replay_hash(wrapper)
            write_json_immutable(
                replay_path / f"{index:03d}_{step}.json",
                wrapper,
            )
    except Exception:
        return


def _unavailable_source_snapshot(artifact: dict[str, Any]) -> dict[str, Any]:
    snapshot = {
        "artifact_type": "G38_VALIDATION_PLAN_UNAVAILABLE_V1",
        "entry_id": artifact["source_g38_reference"],
        "planning_entry_hash": artifact["source_g38_planning_entry_hash"],
        "source_available": False,
    }
    snapshot["artifact_hash"] = replay_hash(snapshot)
    return snapshot


def _unavailable_selection_snapshot(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    snapshot = {
        "artifact_type": "IVE_1_SELECTION_UNAVAILABLE_V1",
        "selection_id": artifact["source_ive_1_reference"],
        "semantic_validation_selection_hash": artifact[
            "source_ive_1_selection_hash"
        ],
        "source_available": False,
    }
    snapshot["artifact_hash"] = replay_hash(snapshot)
    return snapshot


def _verify_wrapper(
    wrapper: dict[str, Any],
    index: int,
    step: str,
) -> None:
    if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
        raise FailClosedRuntimeError("IVE-2 replay ordering mismatch")
    _verify_hash(wrapper, "replay_hash", "IVE-2 replay hash mismatch")


def _ensure_replay_available(replay_path: Path) -> None:
    if any(
        (replay_path / f"{index:03d}_{step}.json").exists()
        for index, step in enumerate(REPLAY_STEPS)
    ):
        raise FailClosedRuntimeError(
            "IVE-2 failed closed: replay artifact already exists"
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
        raise FailClosedRuntimeError(f"IVE-2 requires {field}")
    return value


def _require_hash(value: Any, field: str) -> str:
    text = _require_string(value, field)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(f"IVE-2 requires canonical {field}")
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
