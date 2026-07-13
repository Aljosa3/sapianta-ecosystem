"""Deterministic, non-executing Platform Validation Planning."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_certification_registry import (
    PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY_VERSION,
    lookup_platform_capability_certification,
)
from aigol.runtime.platform_change_impact_analysis_runtime import (
    FAILED_CLOSED as IMPACT_FAILED_CLOSED,
    PLATFORM_CHANGE_IMPACT_ARTIFACT_V1,
    validate_platform_change_impact_artifact,
)
from aigol.runtime.platform_core_validation_allowlist import (
    VALIDATION_ALLOWLIST_VERSION,
    VALIDATION_COMMAND_ALLOWLIST,
    get_validation_command_spec,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


PLATFORM_VALIDATION_PLANNING_RUNTIME_VERSION = "G27_07_PLATFORM_VALIDATION_PLANNING_RUNTIME_V1"
PLATFORM_VALIDATION_PLAN_ARTIFACT_V1 = "PLATFORM_VALIDATION_PLAN_ARTIFACT_V1"
VALIDATION_PLAN_COMPOSED = "VALIDATION_PLAN_COMPOSED"
VALIDATION_PLAN_COMPOSED_WITH_UNRESOLVED_MAPPINGS = "VALIDATION_PLAN_COMPOSED_WITH_UNRESOLVED_MAPPINGS"
FAILED_CLOSED = "FAILED_CLOSED"
REPLAY_STEP = "platform_validation_plan_recorded"

AUTHORITY_FLAGS = {
    "constructs_validation_candidates": False,
    "executes_validation": False,
    "invokes_workers": False,
    "invokes_providers": False,
    "authorizes_execution": False,
    "authorizes_dispatch": False,
    "authorizes_mutation": False,
    "certifies_results": False,
}

LAYER_REQUIREMENTS = {
    "L0": "CONSTITUTIONAL_IMMUTABILITY_VERIFICATION",
    "L1": "CANONICAL_ARTIFACT_STABILITY_VERIFICATION",
    "L2": "DECISION_SPINE_DETERMINISM_VERIFICATION",
    "L3": "GOVERNANCE_CONFORMANCE_VERIFICATION",
    "L4": "BOUNDED_DEVELOPMENT_REGRESSION_VERIFICATION",
}


def plan_platform_validation(
    *,
    validation_plan_id: str,
    platform_change_impact_artifact: dict[str, Any],
    platform_change_impact_reference: str,
    platform_change_impact_hash: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Compose one validation plan without constructing or executing candidates."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        plan_id = _require_string(validation_plan_id, "validation_plan_id")
        source_reference = _require_string(platform_change_impact_reference, "platform_change_impact_reference")
        source_hash = _require_hash(platform_change_impact_hash, "platform_change_impact_hash")
        source = validate_platform_change_impact_artifact(platform_change_impact_artifact)
        _validate_source_binding(source, source_reference, source_hash)
        requirements = _ordered_requirements(source)
        command_references = _exact_allowlisted_command_references(source)
        unresolved = _preserved_unresolved_mappings(source)
        status = (
            VALIDATION_PLAN_COMPOSED_WITH_UNRESOLVED_MAPPINGS
            if unresolved
            else VALIDATION_PLAN_COMPOSED
        )
        artifact = _plan_artifact(
            validation_plan_id=plan_id,
            impact_reference=source_reference,
            impact_hash=source_hash,
            impact_artifact_hash=source["artifact_hash"],
            requirements=requirements,
            command_references=command_references,
            unresolved_mappings=unresolved,
            planning_status=status,
            created_at=_require_string(created_at, "created_at"),
            failure_reason=None,
        )
    except Exception as exc:
        artifact = _failed_artifact(
            validation_plan_id=validation_plan_id,
            source=platform_change_impact_artifact,
            impact_reference=platform_change_impact_reference,
            impact_hash=platform_change_impact_hash,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
    _persist_if_possible(replay_path, artifact)
    return _capture(artifact, replay_path)


def validate_platform_validation_plan_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    """Validate one canonical Platform Validation Plan artifact."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("platform validation plan artifact must be a JSON object")
    candidate = deepcopy(artifact)
    _verify_plan_artifact(candidate)
    return candidate


def reconstruct_platform_validation_plan_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and verify one Platform Validation Plan replay artifact."""

    wrapper = load_json(Path(replay_dir) / f"000_{REPLAY_STEP}.json")
    if wrapper.get("replay_index") != 0 or wrapper.get("replay_step") != REPLAY_STEP:
        raise FailClosedRuntimeError("platform validation plan replay ordering mismatch")
    _verify_hash(wrapper, "replay_hash", "platform validation plan replay hash mismatch")
    artifact = validate_platform_validation_plan_artifact(wrapper.get("artifact"))
    return {
        "validation_plan_id": artifact["validation_plan_id"],
        "planning_status": artifact["planning_status"],
        "platform_change_impact_reference": artifact["platform_change_impact_reference"],
        "platform_change_impact_hash": artifact["platform_change_impact_hash"],
        "validation_requirements": deepcopy(artifact["validation_requirements"]),
        "allowlisted_command_references": deepcopy(artifact["allowlisted_command_references"]),
        "unresolved_mappings": deepcopy(artifact["unresolved_mappings"]),
        "platform_validation_plan_hash": artifact["platform_validation_plan_hash"],
        "artifact_hash": artifact["artifact_hash"],
        "replay_visible": True,
        "fail_closed": artifact["planning_status"] == FAILED_CLOSED,
        "failure_reason": artifact["failure_reason"],
        "authority_flags": deepcopy(artifact["authority_flags"]),
        "replay_hash": wrapper["replay_hash"],
    }


def _validate_source_binding(source: dict[str, Any], reference: str, source_hash: str) -> None:
    if source.get("artifact_type") != PLATFORM_CHANGE_IMPACT_ARTIFACT_V1:
        raise FailClosedRuntimeError("platform validation planning failed closed: impact artifact required")
    if source.get("impact_status") == IMPACT_FAILED_CLOSED:
        raise FailClosedRuntimeError("platform validation planning failed closed: source impact failed closed")
    if source.get("impact_analysis_id") != reference:
        raise FailClosedRuntimeError("platform validation planning failed closed: impact reference mismatch")
    if source.get("platform_change_impact_hash") != source_hash:
        raise FailClosedRuntimeError("platform validation planning failed closed: impact hash mismatch")


def _ordered_requirements(source: dict[str, Any]) -> list[dict[str, Any]]:
    requirements: list[dict[str, Any]] = []
    for capability in _require_object_list(source, "affected_capabilities"):
        capability_id = _require_string(capability.get("capability_identifier"), "capability_identifier")
        registry_record = lookup_platform_capability_certification(capability_id)
        if capability.get("certification_record_hash") != registry_record["certification_record_hash"]:
            raise FailClosedRuntimeError("platform validation planning failed closed: capability registry binding mismatch")
        requirements.append(
            _requirement(
                "CAPABILITY",
                capability_id,
                "CAPABILITY_REGRESSION_VERIFICATION",
                registry_record["capability_owner"],
                {"affected_paths": sorted(capability.get("affected_paths") or [])},
            )
        )
    for layer in _require_object_list(source, "affected_constitutional_layers"):
        layer_id = _require_string(layer.get("constitutional_layer"), "constitutional_layer")
        requirement = LAYER_REQUIREMENTS.get(layer_id)
        if requirement is None:
            raise FailClosedRuntimeError("platform validation planning failed closed: unsupported constitutional layer")
        requirements.append(
            _requirement("CONSTITUTIONAL_LAYER", layer_id, requirement, "PLATFORM_CORE_GOVERNANCE", {"affected_paths": sorted(layer.get("affected_paths") or [])})
        )
    requirements.extend(_surface_requirements(source, "affected_governance_surfaces", "GOVERNANCE", "GOVERNANCE_SURFACE_CONFORMANCE"))
    requirements.extend(_surface_requirements(source, "affected_replay_surfaces", "REPLAY", "REPLAY_SURFACE_INTEGRITY"))
    requirements.extend(_surface_requirements(source, "affected_certification_surfaces", "CERTIFICATION", "CERTIFICATION_EVIDENCE_CONTINUITY"))
    if not requirements:
        raise FailClosedRuntimeError("platform validation planning failed closed: no validation requirements resolved")
    requirements.sort(key=lambda item: (item["requirement_order"], item["source_identifier"]))
    for index, requirement in enumerate(requirements):
        requirement["requirement_index"] = index
        requirement["requirement_id"] = f"VALIDATION-REQUIREMENT-{index:03d}"
        requirement["requirement_hash"] = replay_hash(requirement)
    return requirements


def _surface_requirements(source: dict[str, Any], field: str, category: str, requirement_type: str) -> list[dict[str, Any]]:
    return [
        _requirement(
            category,
            _require_string(surface.get("surface_id"), "surface_id"),
            requirement_type,
            _require_string(surface.get("surface_owner"), "surface_owner"),
            {key: deepcopy(value) for key, value in sorted(surface.items()) if key not in {"surface_id", "surface_owner"}},
        )
        for surface in _require_object_list(source, field)
    ]


def _requirement(category: str, source_id: str, requirement_type: str, owner: str, evidence: dict[str, Any]) -> dict[str, Any]:
    order = {"CAPABILITY": 0, "CONSTITUTIONAL_LAYER": 1, "GOVERNANCE": 2, "REPLAY": 3, "CERTIFICATION": 4}[category]
    return {
        "requirement_order": order,
        "requirement_category": category,
        "source_identifier": source_id,
        "requirement_type": requirement_type,
        "requirement_owner": owner,
        "mapping_authority": "PLATFORM_CHANGE_IMPACT_ARTIFACT_V1",
        "mapping_evidence": evidence,
        "required": True,
    }


def _exact_allowlisted_command_references(source: dict[str, Any]) -> list[dict[str, Any]]:
    affected_paths = sorted(
        {_require_string(entry.get("target_path"), "target_path") for entry in _require_object_list(source, "impact_entries")}
    )
    references = []
    for command_id in sorted(VALIDATION_COMMAND_ALLOWLIST):
        spec = get_validation_command_spec(command_id)
        declared_targets = sorted(arg for arg in spec["argv"] if arg.endswith(".py") and "/" in arg)
        if declared_targets and declared_targets == affected_paths:
            references.append(
                {
                    "command_id": command_id,
                    "allowlist_version": spec["allowlist_version"],
                    "command_spec_hash": spec["spec_hash"],
                    "exact_mapping_basis": "DECLARED_COMMAND_TARGET_SET_EQUALS_AFFECTED_PATH_SET",
                    "affected_paths": affected_paths,
                }
            )
    return references


def _preserved_unresolved_mappings(source: dict[str, Any]) -> list[dict[str, Any]]:
    unresolved = []
    for item in _require_object_list(source, "unresolved_mappings", allow_empty=True):
        preserved = deepcopy(item)
        preserved["planning_disposition"] = "PRESERVED_OPTIONAL_SOURCE_MAPPING"
        unresolved.append(preserved)
    return sorted(unresolved, key=lambda item: replay_hash(item))


def _plan_artifact(*, validation_plan_id: str, impact_reference: str, impact_hash: str, impact_artifact_hash: str, requirements: list[dict[str, Any]], command_references: list[dict[str, Any]], unresolved_mappings: list[dict[str, Any]], planning_status: str, created_at: str, failure_reason: str | None) -> dict[str, Any]:
    artifact = {
        "artifact_type": PLATFORM_VALIDATION_PLAN_ARTIFACT_V1,
        "runtime_version": PLATFORM_VALIDATION_PLANNING_RUNTIME_VERSION,
        "validation_plan_id": validation_plan_id,
        "planning_status": planning_status,
        "source_artifact_type": PLATFORM_CHANGE_IMPACT_ARTIFACT_V1,
        "platform_change_impact_reference": impact_reference,
        "platform_change_impact_hash": impact_hash,
        "platform_change_impact_artifact_hash": impact_artifact_hash,
        "validation_requirements": deepcopy(requirements),
        "validation_requirement_count": len(requirements),
        "allowlisted_command_references": deepcopy(command_references),
        "allowlisted_command_reference_count": len(command_references),
        "validation_allowlist_version": VALIDATION_ALLOWLIST_VERSION,
        "capability_registry_version": PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY_VERSION,
        "unresolved_mappings": deepcopy(unresolved_mappings),
        "unresolved_mapping_count": len(unresolved_mappings),
        "mapping_policy": {
            "impact_to_requirement_mapping": "EXACT_TYPED_IMPACT_SURFACE_MAPPING",
            "command_mapping": "EXACT_DECLARED_TARGET_SET_ONLY",
            "command_synthesis_allowed": False,
            "allowlist_expansion_allowed": False,
            "deterministic_ordering": True,
        },
        "created_at": created_at,
        "replay_visible": True,
        "read_only": True,
        "non_authoritative": True,
        "validation_candidates_constructed": False,
        "validation_executed": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "certification_performed": False,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "failure_reason": failure_reason,
    }
    artifact["platform_validation_plan_hash"] = _plan_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_artifact(*, validation_plan_id: Any, source: Any, impact_reference: Any, impact_hash: Any, created_at: Any, failure_reason: str) -> dict[str, Any]:
    source_artifact_hash = source.get("artifact_hash") if isinstance(source, dict) else None
    return _plan_artifact(
        validation_plan_id=_safe_string(validation_plan_id),
        impact_reference=_safe_string(impact_reference),
        impact_hash=_safe_hash(impact_hash),
        impact_artifact_hash=_safe_hash(source_artifact_hash),
        requirements=[],
        command_references=[],
        unresolved_mappings=[],
        planning_status=FAILED_CLOSED,
        created_at=_safe_string(created_at),
        failure_reason=failure_reason,
    )


def _verify_plan_artifact(artifact: dict[str, Any]) -> None:
    if artifact.get("artifact_type") != PLATFORM_VALIDATION_PLAN_ARTIFACT_V1:
        raise FailClosedRuntimeError("platform validation plan artifact type mismatch")
    _verify_hash(artifact, "artifact_hash", "platform validation plan artifact hash mismatch")
    if artifact.get("platform_validation_plan_hash") != _plan_hash(artifact):
        raise FailClosedRuntimeError("platform validation plan hash mismatch")
    if artifact.get("replay_visible") is not True or artifact.get("read_only") is not True or artifact.get("non_authoritative") is not True:
        raise FailClosedRuntimeError("platform validation plan must be replay-visible, read-only, and non-authoritative")
    if any(value is not False for value in artifact.get("authority_flags", {}).values()):
        raise FailClosedRuntimeError("platform validation plan cannot grant authority")
    status = artifact.get("planning_status")
    if status not in {VALIDATION_PLAN_COMPOSED, VALIDATION_PLAN_COMPOSED_WITH_UNRESOLVED_MAPPINGS, FAILED_CLOSED}:
        raise FailClosedRuntimeError("platform validation plan status is invalid")
    requirements = artifact.get("validation_requirements")
    commands = artifact.get("allowlisted_command_references")
    unresolved = artifact.get("unresolved_mappings")
    if not isinstance(requirements, list) or artifact.get("validation_requirement_count") != len(requirements):
        raise FailClosedRuntimeError("platform validation plan requirement count mismatch")
    if not isinstance(commands, list) or artifact.get("allowlisted_command_reference_count") != len(commands):
        raise FailClosedRuntimeError("platform validation plan command count mismatch")
    if not isinstance(unresolved, list) or artifact.get("unresolved_mapping_count") != len(unresolved):
        raise FailClosedRuntimeError("platform validation plan unresolved count mismatch")
    for index, requirement in enumerate(requirements):
        if requirement.get("requirement_index") != index or requirement.get("requirement_id") != f"VALIDATION-REQUIREMENT-{index:03d}":
            raise FailClosedRuntimeError("platform validation plan requirement ordering mismatch")
        _verify_hash(requirement, "requirement_hash", "platform validation requirement hash mismatch")
    for command in commands:
        spec = get_validation_command_spec(command.get("command_id"))
        if command.get("command_spec_hash") != spec["spec_hash"] or command.get("allowlist_version") != spec["allowlist_version"]:
            raise FailClosedRuntimeError("platform validation plan allowlist binding mismatch")
    if status == FAILED_CLOSED and (requirements or commands):
        raise FailClosedRuntimeError("failed platform validation plan cannot contain requirements")
    if status != FAILED_CLOSED and not requirements:
        raise FailClosedRuntimeError("successful platform validation plan requires requirements")
    if status == VALIDATION_PLAN_COMPOSED and unresolved:
        raise FailClosedRuntimeError("platform validation plan status omits unresolved mappings")
    if status == VALIDATION_PLAN_COMPOSED_WITH_UNRESOLVED_MAPPINGS and not unresolved:
        raise FailClosedRuntimeError("platform validation plan unresolved status requires mappings")


def _plan_hash(artifact: dict[str, Any]) -> str:
    return replay_hash({key: deepcopy(artifact[key]) for key in (
        "source_artifact_type", "platform_change_impact_reference", "platform_change_impact_hash",
        "platform_change_impact_artifact_hash", "validation_requirements", "allowlisted_command_references",
        "validation_allowlist_version", "capability_registry_version", "unresolved_mappings", "planning_status",
        "mapping_policy", "authority_flags", "failure_reason",
    )})


def _capture(artifact: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "runtime_version": PLATFORM_VALIDATION_PLANNING_RUNTIME_VERSION,
        "platform_validation_plan_artifact": deepcopy(artifact),
        "validation_plan_id": artifact["validation_plan_id"],
        "planning_status": artifact["planning_status"],
        "platform_validation_plan_hash": artifact["platform_validation_plan_hash"],
        "platform_validation_plan_replay_reference": str(replay_path),
        "validation_requirements": deepcopy(artifact["validation_requirements"]),
        "allowlisted_command_references": deepcopy(artifact["allowlisted_command_references"]),
        "unresolved_mappings": deepcopy(artifact["unresolved_mappings"]),
        "fail_closed": artifact["planning_status"] == FAILED_CLOSED,
        "failure_reason": artifact["failure_reason"],
        "validation_candidates_constructed": False,
        "validation_executed": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "certification_performed": False,
    }
    capture["capture_hash"] = replay_hash(capture)
    return capture


def _persist_if_possible(replay_path: Path, artifact: dict[str, Any]) -> None:
    try:
        wrapper = {"replay_index": 0, "replay_step": REPLAY_STEP, "artifact": deepcopy(artifact)}
        wrapper["replay_hash"] = replay_hash(wrapper)
        write_json_immutable(replay_path / f"000_{REPLAY_STEP}.json", wrapper)
    except Exception:
        return


def _ensure_replay_available(path: Path) -> None:
    if path.exists() and any(path.iterdir()):
        raise FailClosedRuntimeError("platform validation planning replay directory must be empty")


def _require_object_list(source: dict[str, Any], field: str, *, allow_empty: bool = False) -> list[dict[str, Any]]:
    values = source.get(field)
    if not isinstance(values, list) or (not values and not allow_empty) or any(not isinstance(item, dict) for item in values):
        raise FailClosedRuntimeError(f"platform validation planning requires {field}")
    return values


def _verify_hash(value: dict[str, Any], field: str, message: str) -> None:
    actual = _require_hash(value.get(field), field)
    expected_input = deepcopy(value)
    expected_input.pop(field)
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(message)


def _require_hash(value: Any, field: str) -> str:
    text = _require_string(value, field)
    if not text.startswith("sha256:") or len(text) != 71 or any(
        character not in "0123456789abcdef" for character in text.removeprefix("sha256:")
    ):
        raise FailClosedRuntimeError(f"platform validation planning requires canonical {field}")
    return text


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"platform validation planning requires {field}")
    return value.strip()


def _safe_string(value: Any) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else "UNAVAILABLE"


def _safe_hash(value: Any) -> str:
    return value if isinstance(value, str) and value.startswith("sha256:") else replay_hash({"unavailable": True})


def _failure_reason(exc: Exception) -> str:
    return str(exc) or exc.__class__.__name__
