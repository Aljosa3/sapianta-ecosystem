"""Deterministic semantic validation selection over certified IVE-0 evidence."""

from __future__ import annotations

from collections import deque
from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.generation_certification_composition import (
    canonical_generation_evidence_profile,
)
from aigol.runtime.intelligent_validation_engine_v0 import (
    COMPONENT_CLASSIFICATION_ORDER,
    FAILED_CLOSED as IVE_0_FAILED_CLOSED,
    INTELLIGENT_VALIDATION_PLAN_ARTIFACT_V1,
    RECOMMENDATION_FIELDS,
    VALIDATION_DIMENSIONS_BY_COMPONENT_TYPE,
    validate_intelligent_validation_plan_artifact,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_certification_registry import (
    lookup_platform_capability_certification,
)
from aigol.runtime.platform_capability_composition_coverage import (
    KNOWN_COMPOSITION_DEPENDENCIES,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


INTELLIGENT_VALIDATION_ENGINE_V1_RUNTIME_VERSION = (
    "G37_01_INTELLIGENT_VALIDATION_ENGINE_V1_RUNTIME_V1"
)
SEMANTIC_VALIDATION_DEPENDENCY_MODEL_V1 = (
    "SEMANTIC_VALIDATION_DEPENDENCY_MODEL_V1"
)
SEMANTIC_VALIDATION_SELECTION_ARTIFACT_V1 = (
    "SEMANTIC_VALIDATION_SELECTION_ARTIFACT_V1"
)
SEMANTIC_VALIDATION_SCOPE_SELECTED = "SEMANTIC_VALIDATION_SCOPE_SELECTED"
FAILED_CLOSED = "FAILED_CLOSED"
REPLAY_STEPS = (
    "ive_0_plan_bound",
    "semantic_validation_selection_recorded",
)

COMPONENT_TYPE_DEPENDENCIES = (
    (
        "AICLI",
        "PLATFORM_CORE",
        "Human-interface entry changes require Platform Core entry integration validation.",
    ),
    (
        "PLATFORM_CORE",
        "GOVERNANCE",
        "Platform Core behavior remains constrained by Governance evaluation.",
    ),
    (
        "PLATFORM_CORE",
        "REPLAY",
        "Platform Core behavior must preserve replay reconstruction and evidence continuity.",
    ),
    (
        "GOVERNANCE",
        "AUTHORIZATION",
        "Governance conclusions constrain downstream authorization admissibility.",
    ),
    (
        "GOVERNANCE",
        "REPLAY",
        "Governance interpretation depends on immutable replay evidence.",
    ),
    (
        "AUTHORIZATION",
        "PROVIDER",
        "Provider activation remains subordinate to authorization boundaries.",
    ),
    (
        "AUTHORIZATION",
        "WORKER",
        "Worker activation remains subordinate to authorization boundaries.",
    ),
    (
        "PROVIDER",
        "WORKER",
        "Provider handoff continuity is validated through bounded Worker-facing execution.",
    ),
    (
        "PROVIDER",
        "REPLAY",
        "Provider outcomes require replay-visible execution evidence.",
    ),
    (
        "WORKER",
        "REPLAY",
        "Worker outcomes require replay-visible execution evidence.",
    ),
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
    "parallelizes_validation": False,
    "modifies_pytest": False,
}


def semantic_validation_dependency_model() -> dict[str, Any]:
    """Return the immutable explicit dependency model used by IVE-1."""

    generation_profile = canonical_generation_evidence_profile()
    declared_capability_dependencies = dict(KNOWN_COMPOSITION_DEPENDENCIES)
    declared_capability_dependencies[
        "GENERATION_CERTIFICATION_COMPOSITION_SERVICE"
    ] = tuple(generation_profile["required_capabilities"])

    capability_edges = []
    for dependent_capability in sorted(declared_capability_dependencies):
        for required_capability in sorted(
            set(declared_capability_dependencies[dependent_capability])
        ):
            edge = {
                "edge_type": "CERTIFIED_CAPABILITY_COMPOSITION_DEPENDENCY",
                "dependent_capability": dependent_capability,
                "required_capability": required_capability,
                "validation_propagation": (
                    "REQUIRED_CAPABILITY_CHANGE_PROPAGATES_TO_DEPENDENT_CAPABILITY"
                ),
                "dependency_origin": (
                    "G20_03_KNOWN_COMPOSITION_DEPENDENCIES_AND_"
                    "CANONICAL_GENERATION_EVIDENCE_PROFILE"
                ),
                "authority_references": [
                    "docs/governance/G20_03_PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_RUNTIME_IMPLEMENTATION.md",
                    "docs/governance/G20_01_GENERATION_CERTIFICATION_COMPOSITION_SERVICE_IMPLEMENTATION.md",
                ],
            }
            edge["edge_hash"] = replay_hash(edge)
            capability_edges.append(edge)

    component_edges = []
    for source_type, dependent_type, reason in COMPONENT_TYPE_DEPENDENCIES:
        edge = {
            "edge_type": "CONSTITUTIONAL_COMPONENT_VALIDATION_DEPENDENCY",
            "source_component_type": source_type,
            "dependent_component_type": dependent_type,
            "validation_propagation": (
                "SOURCE_COMPONENT_CHANGE_REQUIRES_DEPENDENT_COMPONENT_VALIDATION"
            ),
            "reason": reason,
            "dependency_origin": "G37_01_EXPLICIT_CONSTITUTIONAL_VALIDATION_MODEL",
            "authority_references": [
                "docs/governance/CONSTITUTIONAL_ARCHITECTURE_SPEC_V1.md",
                "docs/governance/CANONICAL_LAYER_MODEL.md",
                "docs/governance/G36_01_INTELLIGENT_VALIDATION_ENGINE_V0.md",
            ],
        }
        edge["edge_hash"] = replay_hash(edge)
        component_edges.append(edge)

    model = {
        "artifact_type": SEMANTIC_VALIDATION_DEPENDENCY_MODEL_V1,
        "model_version": INTELLIGENT_VALIDATION_ENGINE_V1_RUNTIME_VERSION,
        "capability_dependencies": sorted(
            capability_edges,
            key=lambda item: (
                item["required_capability"],
                item["dependent_capability"],
            ),
        ),
        "component_type_dependencies": sorted(
            component_edges,
            key=lambda item: (
                item["source_component_type"],
                item["dependent_component_type"],
            ),
        ),
        "mapping_policy": {
            "declared_edges_only": True,
            "probabilistic_inference_allowed": False,
            "filename_semantic_inference_allowed": False,
            "natural_language_inference_allowed": False,
            "unknown_dependency_completion_allowed": False,
            "cycle_amplification_allowed": False,
            "deterministic_shortest_path_selection": True,
        },
        "read_only": True,
        "replay_visible": True,
        "non_authoritative": True,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
    }
    model["dependency_model_hash"] = replay_hash(model)
    return model


def validate_semantic_validation_dependency_model(
    model: dict[str, Any],
) -> dict[str, Any]:
    """Validate the canonical IVE-1 dependency model."""

    if not isinstance(model, dict):
        raise FailClosedRuntimeError(
            "IVE-1 dependency model must be a JSON object"
        )
    candidate = deepcopy(model)
    if candidate.get("artifact_type") != SEMANTIC_VALIDATION_DEPENDENCY_MODEL_V1:
        raise FailClosedRuntimeError("IVE-1 dependency model type mismatch")
    _verify_hash(
        candidate,
        "dependency_model_hash",
        "IVE-1 dependency model hash mismatch",
    )
    if (
        candidate.get("read_only") is not True
        or candidate.get("replay_visible") is not True
        or candidate.get("non_authoritative") is not True
    ):
        raise FailClosedRuntimeError(
            "IVE-1 dependency model boundary flags are invalid"
        )
    if any(
        value is not False for value in candidate.get("authority_flags", {}).values()
    ):
        raise FailClosedRuntimeError("IVE-1 dependency model cannot grant authority")

    capability_edges = candidate.get("capability_dependencies")
    component_edges = candidate.get("component_type_dependencies")
    if not isinstance(capability_edges, list) or not isinstance(component_edges, list):
        raise FailClosedRuntimeError("IVE-1 dependency edge lists are required")
    for edge in capability_edges:
        _verify_hash(edge, "edge_hash", "IVE-1 capability edge hash mismatch")
        lookup_platform_capability_certification(
            _require_string(edge.get("required_capability"), "required_capability")
        )
        lookup_platform_capability_certification(
            _require_string(
                edge.get("dependent_capability"),
                "dependent_capability",
            )
        )
    for edge in component_edges:
        _verify_hash(edge, "edge_hash", "IVE-1 component edge hash mismatch")
        source = _require_component_type(edge.get("source_component_type"))
        target = _require_component_type(edge.get("dependent_component_type"))
        if source == target:
            raise FailClosedRuntimeError("IVE-1 self dependency is prohibited")
    _assert_acyclic(
        [
            (
                edge["source_component_type"],
                edge["dependent_component_type"],
            )
            for edge in component_edges
        ],
        "component type",
    )
    _assert_acyclic(
        [
            (
                edge["required_capability"],
                edge["dependent_capability"],
            )
            for edge in capability_edges
        ],
        "capability",
    )
    if candidate != semantic_validation_dependency_model():
        raise FailClosedRuntimeError(
            "IVE-1 dependency model differs from canonical model"
        )
    return candidate


def select_semantic_validation_scope(
    *,
    selection_id: str,
    intelligent_validation_plan_artifact: dict[str, Any],
    intelligent_validation_plan_reference: str,
    intelligent_validation_plan_hash: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Select direct and transitive validation without executing it."""

    replay_path = Path(replay_dir)
    source: dict[str, Any] | None = None
    try:
        _ensure_replay_available(replay_path)
        selected_id = _require_string(selection_id, "selection_id")
        source_reference = _require_string(
            intelligent_validation_plan_reference,
            "intelligent_validation_plan_reference",
        )
        source_hash = _require_hash(
            intelligent_validation_plan_hash,
            "intelligent_validation_plan_hash",
        )
        timestamp = _require_string(created_at, "created_at")
        source = validate_intelligent_validation_plan_artifact(
            intelligent_validation_plan_artifact
        )
        _validate_ive_0_binding(source, source_reference, source_hash)
        model = validate_semantic_validation_dependency_model(
            semantic_validation_dependency_model()
        )
        direct_subjects = _direct_validation_subjects(source)
        transitive_dependencies = _transitive_dependencies(
            source,
            model,
        )
        requirements = _selected_validation_requirements(
            source,
            direct_subjects=direct_subjects,
            transitive_dependencies=transitive_dependencies,
        )
        selection = _selection_artifact(
            selection_id=selected_id,
            selection_status=SEMANTIC_VALIDATION_SCOPE_SELECTED,
            source=source,
            dependency_model=model,
            direct_subjects=direct_subjects,
            transitive_dependencies=transitive_dependencies,
            validation_requirements=requirements,
            created_at=timestamp,
            failure_reason=None,
        )
    except Exception as exc:
        selection = _failed_selection_artifact(
            selection_id=selection_id,
            source=source
            if source is not None
            else intelligent_validation_plan_artifact,
            source_reference=intelligent_validation_plan_reference,
            source_hash=intelligent_validation_plan_hash,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
    _persist_selection_replay(replay_path, source, selection)
    return _capture(selection, replay_path)


def validate_semantic_validation_selection_artifact(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Validate one IVE-1 semantic selection artifact."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(
            "IVE-1 semantic validation selection must be a JSON object"
        )
    candidate = deepcopy(artifact)
    _verify_selection_artifact(candidate)
    return candidate


def reconstruct_semantic_validation_selection_replay(
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Reconstruct IVE-0 source and IVE-1 selection evidence."""

    replay_path = Path(replay_dir)
    source_wrapper = load_json(
        replay_path / f"000_{REPLAY_STEPS[0]}.json"
    )
    selection_wrapper = load_json(
        replay_path / f"001_{REPLAY_STEPS[1]}.json"
    )
    _verify_wrapper(source_wrapper, 0, REPLAY_STEPS[0])
    _verify_wrapper(selection_wrapper, 1, REPLAY_STEPS[1])
    selection = validate_semantic_validation_selection_artifact(
        selection_wrapper.get("artifact")
    )
    source_artifact = source_wrapper.get("artifact")
    if (
        isinstance(source_artifact, dict)
        and source_artifact.get("artifact_type")
        == INTELLIGENT_VALIDATION_PLAN_ARTIFACT_V1
    ):
        source = validate_intelligent_validation_plan_artifact(source_artifact)
        if selection["source_ive_0_artifact_hash"] != source["artifact_hash"]:
            raise FailClosedRuntimeError("IVE-1 replay source artifact hash mismatch")
        if selection["selection_status"] != FAILED_CLOSED:
            if selection["source_ive_0_reference"] != source["ive_analysis_id"]:
                raise FailClosedRuntimeError(
                    "IVE-1 replay source reference mismatch"
                )
            if (
                selection["source_ive_0_plan_hash"]
                != source["intelligent_validation_plan_hash"]
            ):
                raise FailClosedRuntimeError(
                    "IVE-1 replay source plan hash mismatch"
                )
            model = selection["semantic_dependency_model"]
            expected_direct = _direct_validation_subjects(source)
            expected_dependencies = _transitive_dependencies(source, model)
            expected_requirements = _selected_validation_requirements(
                source,
                direct_subjects=expected_direct,
                transitive_dependencies=expected_dependencies,
            )
            if selection["direct_validation_subjects"] != expected_direct:
                raise FailClosedRuntimeError(
                    "IVE-1 replay direct selection mismatch"
                )
            if selection["transitive_dependencies"] != expected_dependencies:
                raise FailClosedRuntimeError(
                    "IVE-1 replay transitive selection mismatch"
                )
            if (
                selection["selected_validation_requirements"]
                != expected_requirements
            ):
                raise FailClosedRuntimeError(
                    "IVE-1 replay requirement selection mismatch"
                )
    else:
        if not isinstance(source_artifact, dict):
            raise FailClosedRuntimeError(
                "IVE-1 failed source snapshot must be an object"
            )
        _verify_hash(
            source_artifact,
            "artifact_hash",
            "IVE-1 failed source snapshot hash mismatch",
        )
        if (
            source_artifact.get("artifact_type")
            != "IVE_0_SOURCE_UNAVAILABLE_V1"
            or source_artifact.get("source_available") is not False
            or selection["selection_status"] != FAILED_CLOSED
        ):
            raise FailClosedRuntimeError(
                "IVE-1 failed source snapshot is invalid"
            )
        if (
            source_artifact.get("ive_analysis_id")
            != selection["source_ive_0_reference"]
            or source_artifact.get("intelligent_validation_plan_hash")
            != selection["source_ive_0_plan_hash"]
            or source_artifact.get("source_ive_0_artifact_hash")
            != selection["source_ive_0_artifact_hash"]
        ):
            raise FailClosedRuntimeError(
                "IVE-1 failed source snapshot lineage mismatch"
            )
    return {
        "selection_id": selection["selection_id"],
        "selection_status": selection["selection_status"],
        "source_ive_0_reference": selection["source_ive_0_reference"],
        "semantic_dependency_model_hash": selection[
            "semantic_dependency_model_hash"
        ],
        "direct_validation_subjects": deepcopy(
            selection["direct_validation_subjects"]
        ),
        "transitive_dependencies": deepcopy(
            selection["transitive_dependencies"]
        ),
        "selected_validation_requirements": deepcopy(
            selection["selected_validation_requirements"]
        ),
        "semantic_validation_selection_hash": selection[
            "semantic_validation_selection_hash"
        ],
        "artifact_hash": selection["artifact_hash"],
        "replay_visible": True,
        "fail_closed": selection["selection_status"] == FAILED_CLOSED,
        "human_approval_required": True,
        "validation_executed": False,
        "authority_flags": deepcopy(selection["authority_flags"]),
        "source_replay_hash": source_wrapper["replay_hash"],
        "selection_replay_hash": selection_wrapper["replay_hash"],
    }


def _validate_ive_0_binding(
    source: dict[str, Any],
    reference: str,
    source_hash: str,
) -> None:
    if source.get("artifact_type") != INTELLIGENT_VALIDATION_PLAN_ARTIFACT_V1:
        raise FailClosedRuntimeError("IVE-1 requires an IVE-0 plan artifact")
    if source.get("analysis_status") == IVE_0_FAILED_CLOSED:
        raise FailClosedRuntimeError("IVE-1 source IVE-0 plan failed closed")
    if source.get("ive_analysis_id") != reference:
        raise FailClosedRuntimeError("IVE-1 source IVE-0 reference mismatch")
    if source.get("intelligent_validation_plan_hash") != source_hash:
        raise FailClosedRuntimeError("IVE-1 source IVE-0 plan hash mismatch")


def _direct_validation_subjects(source: dict[str, Any]) -> list[dict[str, Any]]:
    subjects = []
    for component in source["affected_components"]:
        subject = {
            "validation_scope": "DIRECT",
            "subject_kind": "AFFECTED_COMPONENT",
            "subject_identifier": component["component_identifier"],
            "component_type": component["component_type"],
            "capability_identifier": component["capability_identifier"],
            "target_path": component["target_path"],
            "source_component_hash": component["component_hash"],
            "dependency_origin": component["dependency_origin"],
            "reason": component["reason_for_inclusion"],
        }
        subject["subject_hash"] = replay_hash(subject)
        subjects.append(subject)
    return sorted(subjects, key=lambda item: item["subject_identifier"])


def _transitive_dependencies(
    source: dict[str, Any],
    model: dict[str, Any],
) -> list[dict[str, Any]]:
    direct_types = sorted(
        {item["component_type"] for item in source["affected_components"]}
    )
    direct_capabilities = sorted(
        {
            item["capability_identifier"]
            for item in source["affected_components"]
            if not item["capability_identifier"].startswith("REPOSITORY_PATH:")
        }
    )

    type_adjacency = _component_type_adjacency(model)
    capability_adjacency = _capability_dependent_adjacency(model)
    type_paths = _shortest_dependency_paths(
        direct_types,
        type_adjacency,
        excluded_targets=set(direct_types),
    )
    capability_paths = _shortest_dependency_paths(
        direct_capabilities,
        capability_adjacency,
        excluded_targets=set(direct_capabilities),
    )

    dependencies = []
    for path in type_paths:
        dependency = {
            "validation_scope": "TRANSITIVE",
            "dependency_kind": "COMPONENT_TYPE",
            "direct_origin": path["origin"],
            "dependent_identifier": path["target"],
            "dependency_path": path["nodes"],
            "dependency_edge_hashes": path["edge_hashes"],
            "path_length": len(path["edge_hashes"]),
            "reason": (
                "Declared constitutional component dependencies propagate "
                f"validation from {path['origin']} to {path['target']}."
            ),
            "dependency_model_hash": model["dependency_model_hash"],
        }
        dependency["dependency_hash"] = replay_hash(dependency)
        dependencies.append(dependency)
    for path in capability_paths:
        dependency = {
            "validation_scope": "TRANSITIVE",
            "dependency_kind": "CAPABILITY",
            "direct_origin": path["origin"],
            "dependent_identifier": path["target"],
            "dependency_path": path["nodes"],
            "dependency_edge_hashes": path["edge_hashes"],
            "path_length": len(path["edge_hashes"]),
            "reason": (
                "A declared certified composition depends on the changed "
                f"capability through {path['target']}."
            ),
            "dependency_model_hash": model["dependency_model_hash"],
        }
        dependency["dependency_hash"] = replay_hash(dependency)
        dependencies.append(dependency)
    return sorted(
        dependencies,
        key=lambda item: (
            item["dependency_kind"],
            item["dependent_identifier"],
            item["direct_origin"],
            item["dependency_path"],
        ),
    )


def _component_type_adjacency(
    model: dict[str, Any],
) -> dict[str, list[dict[str, str]]]:
    adjacency: dict[str, list[dict[str, str]]] = {}
    for edge in model["component_type_dependencies"]:
        adjacency.setdefault(edge["source_component_type"], []).append(
            {
                "target": edge["dependent_component_type"],
                "edge_hash": edge["edge_hash"],
            }
        )
    return {
        key: sorted(value, key=lambda item: (item["target"], item["edge_hash"]))
        for key, value in adjacency.items()
    }


def _capability_dependent_adjacency(
    model: dict[str, Any],
) -> dict[str, list[dict[str, str]]]:
    adjacency: dict[str, list[dict[str, str]]] = {}
    for edge in model["capability_dependencies"]:
        adjacency.setdefault(edge["required_capability"], []).append(
            {
                "target": edge["dependent_capability"],
                "edge_hash": edge["edge_hash"],
            }
        )
    return {
        key: sorted(value, key=lambda item: (item["target"], item["edge_hash"]))
        for key, value in adjacency.items()
    }


def _shortest_dependency_paths(
    origins: list[str],
    adjacency: dict[str, list[dict[str, str]]],
    *,
    excluded_targets: set[str],
) -> list[dict[str, Any]]:
    selected: dict[tuple[str, str], dict[str, Any]] = {}
    for origin in sorted(origins):
        queue: deque[tuple[str, list[str], list[str]]] = deque(
            [(origin, [origin], [])]
        )
        while queue:
            current, nodes, edge_hashes = queue.popleft()
            for edge in adjacency.get(current, []):
                target = edge["target"]
                if target in nodes:
                    continue
                candidate = {
                    "origin": origin,
                    "target": target,
                    "nodes": [*nodes, target],
                    "edge_hashes": [*edge_hashes, edge["edge_hash"]],
                }
                key = (origin, target)
                existing = selected.get(key)
                if existing is None or _path_order(candidate) < _path_order(
                    existing
                ):
                    selected[key] = candidate
                    queue.append(
                        (
                            target,
                            candidate["nodes"],
                            candidate["edge_hashes"],
                        )
                    )
    return sorted(
        (
            value
            for value in selected.values()
            if value["target"] not in excluded_targets
        ),
        key=lambda item: (item["target"], item["origin"], item["nodes"]),
    )


def _path_order(path: dict[str, Any]) -> tuple[Any, ...]:
    return (
        len(path["edge_hashes"]),
        tuple(path["nodes"]),
        tuple(path["edge_hashes"]),
    )


def _selected_validation_requirements(
    source: dict[str, Any],
    *,
    direct_subjects: list[dict[str, Any]],
    transitive_dependencies: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    requirements = []
    direct_subject_hashes = [item["subject_hash"] for item in direct_subjects]
    recommendation = source["validation_recommendation"]
    for field in RECOMMENDATION_FIELDS.values():
        for item in recommendation[field]:
            requirement = {
                "validation_scope": "DIRECT",
                "validation_dimension": item["validation_dimension"],
                "validation_subject_kind": "IVE_0_AFFECTED_COMPONENT",
                "validation_subject_identifier": item["component_type"],
                "source_evidence_hashes": sorted(
                    [item["requirement_hash"], *direct_subject_hashes]
                ),
                "dependency_evidence_hashes": [],
                "reason": item["reason"],
                "required": True,
            }
            requirement["selection_requirement_hash"] = replay_hash(requirement)
            requirements.append(requirement)

    transitive_by_type: dict[str, list[dict[str, Any]]] = {}
    transitive_by_capability: dict[str, list[dict[str, Any]]] = {}
    for dependency in transitive_dependencies:
        target = dependency["dependent_identifier"]
        if dependency["dependency_kind"] == "COMPONENT_TYPE":
            transitive_by_type.setdefault(target, []).append(dependency)
        else:
            transitive_by_capability.setdefault(target, []).append(dependency)

    for component_type in COMPONENT_CLASSIFICATION_ORDER:
        dependencies = transitive_by_type.get(component_type, [])
        if not dependencies:
            continue
        dependency_hashes = sorted(item["dependency_hash"] for item in dependencies)
        for dimension in VALIDATION_DIMENSIONS_BY_COMPONENT_TYPE[component_type]:
            requirement = {
                "validation_scope": "TRANSITIVE",
                "validation_dimension": dimension,
                "validation_subject_kind": "CONSTITUTIONAL_COMPONENT_TYPE",
                "validation_subject_identifier": component_type,
                "source_evidence_hashes": [
                    source["intelligent_validation_plan_hash"]
                ],
                "dependency_evidence_hashes": dependency_hashes,
                "reason": (
                    f"Declared semantic dependencies require {dimension} "
                    f"validation for transitive {component_type} impact."
                ),
                "required": True,
            }
            requirement["selection_requirement_hash"] = replay_hash(requirement)
            requirements.append(requirement)
    for capability_id in sorted(transitive_by_capability):
        dependencies = transitive_by_capability[capability_id]
        requirement = {
            "validation_scope": "TRANSITIVE",
            "validation_dimension": "CAPABILITY_REGRESSION",
            "validation_subject_kind": "CERTIFIED_DEPENDENT_CAPABILITY",
            "validation_subject_identifier": capability_id,
            "source_evidence_hashes": [
                source["intelligent_validation_plan_hash"],
                lookup_platform_capability_certification(capability_id)[
                    "certification_record_hash"
                ],
            ],
            "dependency_evidence_hashes": sorted(
                item["dependency_hash"] for item in dependencies
            ),
            "reason": (
                "A certified composition transitively depends on an affected "
                f"capability and requires regression validation: {capability_id}."
            ),
            "required": True,
        }
        requirement["selection_requirement_hash"] = replay_hash(requirement)
        requirements.append(requirement)
    requirements.sort(
        key=lambda item: (
            0 if item["validation_scope"] == "DIRECT" else 1,
            item["validation_subject_kind"],
            item["validation_subject_identifier"],
            item["validation_dimension"],
            item["selection_requirement_hash"],
        )
    )
    for index, requirement in enumerate(requirements):
        requirement["selection_requirement_index"] = index
        requirement["selection_requirement_id"] = (
            f"IVE-1-VALIDATION-REQUIREMENT-{index:04d}"
        )
        requirement["selection_requirement_hash"] = _rehash_requirement(
            requirement
        )
    return requirements


def _selection_artifact(
    *,
    selection_id: str,
    selection_status: str,
    source: dict[str, Any],
    dependency_model: dict[str, Any],
    direct_subjects: list[dict[str, Any]],
    transitive_dependencies: list[dict[str, Any]],
    validation_requirements: list[dict[str, Any]],
    created_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    source_recommendation = source["validation_recommendation"]
    artifact = {
        "artifact_type": SEMANTIC_VALIDATION_SELECTION_ARTIFACT_V1,
        "runtime_version": INTELLIGENT_VALIDATION_ENGINE_V1_RUNTIME_VERSION,
        "selection_id": selection_id,
        "selection_status": selection_status,
        "source_artifact_type": INTELLIGENT_VALIDATION_PLAN_ARTIFACT_V1,
        "source_ive_0_reference": source["ive_analysis_id"],
        "source_ive_0_plan_hash": source["intelligent_validation_plan_hash"],
        "source_ive_0_artifact_hash": source["artifact_hash"],
        "semantic_dependency_model": deepcopy(dependency_model),
        "semantic_dependency_model_hash": dependency_model[
            "dependency_model_hash"
        ],
        "direct_validation_subjects": deepcopy(direct_subjects),
        "direct_validation_subject_count": len(direct_subjects),
        "transitive_dependencies": deepcopy(transitive_dependencies),
        "transitive_dependency_count": len(transitive_dependencies),
        "selected_validation_requirements": deepcopy(validation_requirements),
        "selected_validation_requirement_count": len(validation_requirements),
        "direct_validation_requirement_count": sum(
            item["validation_scope"] == "DIRECT"
            for item in validation_requirements
        ),
        "transitive_validation_requirement_count": sum(
            item["validation_scope"] == "TRANSITIVE"
            for item in validation_requirements
        ),
        "full_regression": deepcopy(source_recommendation["full_regression"]),
        "certification_evidence_test_targets": deepcopy(
            source_recommendation["certification_evidence_test_targets"]
        ),
        "existing_allowlisted_command_references": deepcopy(
            source_recommendation["existing_allowlisted_command_references"]
        ),
        "existing_validation_pipeline_handoff": deepcopy(
            source_recommendation["existing_validation_pipeline_handoff"]
        ),
        "human_approval": deepcopy(source_recommendation["human_approval"]),
        "selection_policy": {
            "ive_0_direct_scope_preserved": True,
            "explicit_declared_dependencies_only": True,
            "transitive_closure_cycle_safe": True,
            "shortest_dependency_path_deterministic": True,
            "validation_scope_reduction_allowed": False,
            "command_synthesis_allowed": False,
            "validation_execution_allowed": False,
        },
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
        "repository_mutated": False,
        "replay_semantics_modified": False,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "failure_reason": failure_reason,
    }
    artifact["semantic_validation_selection_hash"] = _selection_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_selection_artifact(
    *,
    selection_id: Any,
    source: Any,
    source_reference: Any,
    source_hash: Any,
    created_at: Any,
    failure_reason: str,
) -> dict[str, Any]:
    source_artifact_hash = source.get("artifact_hash") if isinstance(source, dict) else None
    failed_source = {
        "ive_analysis_id": _safe_string(source_reference),
        "intelligent_validation_plan_hash": _safe_hash(source_hash),
        "artifact_hash": _safe_hash(source_artifact_hash),
        "validation_recommendation": {
            "full_regression": {
                "required": True,
                "reason": "IVE-1 failed closed; reduced scope is prohibited.",
                "mapping_authority": "IVE_1_FAIL_CLOSED_POLICY_V1",
            },
            "certification_evidence_test_targets": [],
            "existing_allowlisted_command_references": [],
            "existing_validation_pipeline_handoff": {
                "status": "BLOCKED_BY_IVE_1_FAILURE",
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
        },
    }
    return _selection_artifact(
        selection_id=_safe_string(selection_id),
        selection_status=FAILED_CLOSED,
        source=failed_source,
        dependency_model=semantic_validation_dependency_model(),
        direct_subjects=[],
        transitive_dependencies=[],
        validation_requirements=[],
        created_at=_safe_string(created_at),
        failure_reason=failure_reason,
    )


def _verify_selection_artifact(artifact: dict[str, Any]) -> None:
    if artifact.get("artifact_type") != SEMANTIC_VALIDATION_SELECTION_ARTIFACT_V1:
        raise FailClosedRuntimeError("IVE-1 selection artifact type mismatch")
    _verify_hash(artifact, "artifact_hash", "IVE-1 artifact hash mismatch")
    if artifact.get("semantic_validation_selection_hash") != _selection_hash(
        artifact
    ):
        raise FailClosedRuntimeError("IVE-1 deterministic selection hash mismatch")
    if (
        artifact.get("replay_visible") is not True
        or artifact.get("read_only") is not True
        or artifact.get("non_authoritative") is not True
    ):
        raise FailClosedRuntimeError("IVE-1 selection boundary flags are invalid")
    if any(
        value is not False for value in artifact.get("authority_flags", {}).values()
    ):
        raise FailClosedRuntimeError("IVE-1 cannot grant authority")
    for field in (
        "human_approval_recorded",
        "validation_candidate_constructed",
        "validation_executed",
        "authorization_invoked",
        "worker_invoked",
        "provider_invoked",
        "repository_mutated",
        "replay_semantics_modified",
    ):
        if artifact.get(field) is not False:
            raise FailClosedRuntimeError(f"IVE-1 {field} must be false")
    if artifact.get("human_approval_required") is not True:
        raise FailClosedRuntimeError("IVE-1 Human Approval requirement missing")
    if (
        artifact.get("human_approval", {}).get("required_before_execution")
        is not True
    ):
        raise FailClosedRuntimeError("IVE-1 selection bypasses Human Approval")

    model = validate_semantic_validation_dependency_model(
        artifact.get("semantic_dependency_model")
    )
    if (
        artifact.get("semantic_dependency_model_hash")
        != model["dependency_model_hash"]
    ):
        raise FailClosedRuntimeError("IVE-1 dependency model binding mismatch")
    direct = artifact.get("direct_validation_subjects")
    dependencies = artifact.get("transitive_dependencies")
    requirements = artifact.get("selected_validation_requirements")
    if not isinstance(direct, list) or artifact.get(
        "direct_validation_subject_count"
    ) != len(direct):
        raise FailClosedRuntimeError("IVE-1 direct subject count mismatch")
    if not isinstance(dependencies, list) or artifact.get(
        "transitive_dependency_count"
    ) != len(dependencies):
        raise FailClosedRuntimeError("IVE-1 transitive dependency count mismatch")
    if not isinstance(requirements, list) or artifact.get(
        "selected_validation_requirement_count"
    ) != len(requirements):
        raise FailClosedRuntimeError("IVE-1 requirement count mismatch")
    for subject in direct:
        _verify_hash(subject, "subject_hash", "IVE-1 direct subject hash mismatch")
        if subject.get("validation_scope") != "DIRECT":
            raise FailClosedRuntimeError("IVE-1 direct subject scope mismatch")
    model_edge_hashes = {
        edge["edge_hash"]
        for edge in [
            *model["capability_dependencies"],
            *model["component_type_dependencies"],
        ]
    }
    component_edge_lookup = {
        (
            edge["source_component_type"],
            edge["dependent_component_type"],
        ): edge["edge_hash"]
        for edge in model["component_type_dependencies"]
    }
    capability_edge_lookup = {
        (
            edge["required_capability"],
            edge["dependent_capability"],
        ): edge["edge_hash"]
        for edge in model["capability_dependencies"]
    }
    dependency_identities: set[tuple[str, str, str]] = set()
    for dependency in dependencies:
        _verify_hash(
            dependency,
            "dependency_hash",
            "IVE-1 transitive dependency hash mismatch",
        )
        if dependency.get("validation_scope") != "TRANSITIVE":
            raise FailClosedRuntimeError("IVE-1 transitive dependency scope mismatch")
        if not set(dependency.get("dependency_edge_hashes", [])).issubset(
            model_edge_hashes
        ):
            raise FailClosedRuntimeError(
                "IVE-1 dependency cites an unknown model edge"
            )
        kind = dependency.get("dependency_kind")
        edge_lookup = (
            component_edge_lookup
            if kind == "COMPONENT_TYPE"
            else capability_edge_lookup
            if kind == "CAPABILITY"
            else None
        )
        if edge_lookup is None:
            raise FailClosedRuntimeError("IVE-1 dependency kind is invalid")
        nodes = dependency.get("dependency_path")
        edge_hashes = dependency.get("dependency_edge_hashes")
        if (
            not isinstance(nodes, list)
            or len(nodes) < 2
            or not isinstance(edge_hashes, list)
            or len(edge_hashes) != len(nodes) - 1
            or dependency.get("path_length") != len(edge_hashes)
            or dependency.get("direct_origin") != nodes[0]
            or dependency.get("dependent_identifier") != nodes[-1]
        ):
            raise FailClosedRuntimeError("IVE-1 dependency path shape mismatch")
        expected_edge_hashes = [
            edge_lookup.get((source, target))
            for source, target in zip(nodes, nodes[1:])
        ]
        if None in expected_edge_hashes or edge_hashes != expected_edge_hashes:
            raise FailClosedRuntimeError(
                "IVE-1 dependency path does not match canonical edges"
            )
        identity = (
            kind,
            dependency["direct_origin"],
            dependency["dependent_identifier"],
        )
        if identity in dependency_identities:
            raise FailClosedRuntimeError("IVE-1 dependency identity is duplicated")
        dependency_identities.add(identity)
    dependency_hashes = {
        item["dependency_hash"] for item in dependencies
    }
    for index, requirement in enumerate(requirements):
        if requirement.get("selection_requirement_index") != index:
            raise FailClosedRuntimeError("IVE-1 requirement ordering mismatch")
        if requirement.get("selection_requirement_id") != (
            f"IVE-1-VALIDATION-REQUIREMENT-{index:04d}"
        ):
            raise FailClosedRuntimeError("IVE-1 requirement identity mismatch")
        if requirement.get("selection_requirement_hash") != _rehash_requirement(
            requirement
        ):
            raise FailClosedRuntimeError("IVE-1 requirement hash mismatch")
        if requirement.get("required") is not True:
            raise FailClosedRuntimeError("IVE-1 selected requirement must be required")
        requirement_dependency_hashes = requirement.get(
            "dependency_evidence_hashes"
        )
        if not isinstance(requirement_dependency_hashes, list):
            raise FailClosedRuntimeError(
                "IVE-1 requirement dependency evidence must be a list"
            )
        if not set(requirement_dependency_hashes).issubset(dependency_hashes):
            raise FailClosedRuntimeError(
                "IVE-1 requirement cites an unknown dependency"
            )
        if (
            requirement.get("validation_scope") == "DIRECT"
            and requirement_dependency_hashes
        ):
            raise FailClosedRuntimeError(
                "IVE-1 direct requirement cannot cite transitive dependencies"
            )
        if (
            requirement.get("validation_scope") == "TRANSITIVE"
            and not requirement_dependency_hashes
        ):
            raise FailClosedRuntimeError(
                "IVE-1 transitive requirement requires dependency evidence"
            )
    if artifact.get("direct_validation_requirement_count") != sum(
        item["validation_scope"] == "DIRECT" for item in requirements
    ):
        raise FailClosedRuntimeError("IVE-1 direct requirement count mismatch")
    if artifact.get("transitive_validation_requirement_count") != sum(
        item["validation_scope"] == "TRANSITIVE" for item in requirements
    ):
        raise FailClosedRuntimeError("IVE-1 transitive requirement count mismatch")

    status = artifact.get("selection_status")
    if status == FAILED_CLOSED:
        if direct or dependencies or requirements:
            raise FailClosedRuntimeError(
                "failed IVE-1 selection cannot contain scope claims"
            )
        if artifact.get("full_regression", {}).get("required") is not True:
            raise FailClosedRuntimeError(
                "failed IVE-1 selection must require full regression"
            )
        if (
            artifact.get("existing_validation_pipeline_handoff", {}).get(
                "status"
            )
            != "BLOCKED_BY_IVE_1_FAILURE"
        ):
            raise FailClosedRuntimeError(
                "failed IVE-1 selection must block validation handoff"
            )
        if not artifact.get("failure_reason"):
            raise FailClosedRuntimeError("failed IVE-1 selection needs a reason")
    elif status == SEMANTIC_VALIDATION_SCOPE_SELECTED:
        if not direct or not requirements:
            raise FailClosedRuntimeError(
                "successful IVE-1 selection requires direct scope"
            )
        if artifact.get("failure_reason") is not None:
            raise FailClosedRuntimeError(
                "successful IVE-1 selection cannot contain failure reason"
            )
    else:
        raise FailClosedRuntimeError("IVE-1 selection status is invalid")


def _selection_hash(artifact: dict[str, Any]) -> str:
    keys = (
        "source_artifact_type",
        "source_ive_0_reference",
        "source_ive_0_plan_hash",
        "source_ive_0_artifact_hash",
        "semantic_dependency_model_hash",
        "direct_validation_subjects",
        "transitive_dependencies",
        "selected_validation_requirements",
        "full_regression",
        "certification_evidence_test_targets",
        "existing_allowlisted_command_references",
        "existing_validation_pipeline_handoff",
        "human_approval",
        "selection_policy",
        "selection_status",
        "authority_flags",
        "failure_reason",
    )
    return replay_hash({key: deepcopy(artifact[key]) for key in keys})


def _rehash_requirement(requirement: dict[str, Any]) -> str:
    candidate = deepcopy(requirement)
    candidate.pop("selection_requirement_hash", None)
    return replay_hash(candidate)


def _capture(
    artifact: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "runtime_version": INTELLIGENT_VALIDATION_ENGINE_V1_RUNTIME_VERSION,
        "semantic_validation_selection_artifact": deepcopy(artifact),
        "selection_id": artifact["selection_id"],
        "selection_status": artifact["selection_status"],
        "semantic_validation_selection_hash": artifact[
            "semantic_validation_selection_hash"
        ],
        "ive_1_replay_reference": str(replay_path),
        "direct_validation_subjects": deepcopy(
            artifact["direct_validation_subjects"]
        ),
        "transitive_dependencies": deepcopy(artifact["transitive_dependencies"]),
        "selected_validation_requirements": deepcopy(
            artifact["selected_validation_requirements"]
        ),
        "fail_closed": artifact["selection_status"] == FAILED_CLOSED,
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


def _persist_selection_replay(
    replay_path: Path,
    source: dict[str, Any] | None,
    selection: dict[str, Any],
) -> None:
    try:
        source_artifact = (
            deepcopy(source)
            if isinstance(source, dict)
            else _failed_source_snapshot(selection)
        )
        _persist_step(
            replay_path,
            0,
            REPLAY_STEPS[0],
            source_artifact,
        )
        _persist_step(
            replay_path,
            1,
            REPLAY_STEPS[1],
            selection,
        )
    except Exception:
        return


def _failed_source_snapshot(selection: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "artifact_type": "IVE_0_SOURCE_UNAVAILABLE_V1",
        "ive_analysis_id": selection["source_ive_0_reference"],
        "intelligent_validation_plan_hash": selection["source_ive_0_plan_hash"],
        "source_ive_0_artifact_hash": selection["source_ive_0_artifact_hash"],
        "source_available": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _persist_step(
    replay_path: Path,
    index: int,
    step: str,
    artifact: dict[str, Any],
) -> None:
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


def _verify_wrapper(
    wrapper: dict[str, Any],
    index: int,
    step: str,
) -> None:
    if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
        raise FailClosedRuntimeError("IVE-1 replay ordering mismatch")
    _verify_hash(wrapper, "replay_hash", "IVE-1 replay hash mismatch")


def _ensure_replay_available(replay_path: Path) -> None:
    if any(
        (
            replay_path / f"{index:03d}_{step}.json"
        ).exists()
        for index, step in enumerate(REPLAY_STEPS)
    ):
        raise FailClosedRuntimeError(
            "IVE-1 failed closed: replay artifact already exists"
        )


def _assert_acyclic(
    edges: list[tuple[str, str]],
    label: str,
) -> None:
    adjacency: dict[str, set[str]] = {}
    for source, target in edges:
        adjacency.setdefault(source, set()).add(target)
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            raise FailClosedRuntimeError(
                f"IVE-1 {label} dependency cycle detected"
            )
        if node in visited:
            return
        visiting.add(node)
        for child in sorted(adjacency.get(node, set())):
            visit(child)
        visiting.remove(node)
        visited.add(node)

    for node in sorted(adjacency):
        visit(node)


def _require_component_type(value: Any) -> str:
    text = _require_string(value, "component_type")
    if text not in COMPONENT_CLASSIFICATION_ORDER:
        raise FailClosedRuntimeError("IVE-1 component type is invalid")
    return text


def _verify_hash(value: dict[str, Any], field: str, message: str) -> None:
    actual = value.get(field)
    if not isinstance(actual, str) or not actual.startswith("sha256:"):
        raise FailClosedRuntimeError(message)
    expected = deepcopy(value)
    expected.pop(field, None)
    if replay_hash(expected) != actual:
        raise FailClosedRuntimeError(message)


def _require_hash(value: Any, field: str) -> str:
    text = _require_string(value, field)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(
            f"IVE-1 failed closed: {field} must be a sha256 hash"
        )
    return text


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"IVE-1 failed closed: {field} is required")
    return value.strip()


def _safe_hash(value: Any) -> str:
    return (
        value
        if isinstance(value, str) and value.startswith("sha256:")
        else replay_hash({"unverified": True})
    )


def _safe_string(value: Any) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else "UNKNOWN"


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return f"IVE-1 failed closed: {exc}" if str(exc) else "IVE-1 failed closed"
