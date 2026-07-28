"""Deterministic, planning-only Intelligent Validation Engine V0."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_certification_registry import (
    list_platform_capability_certifications,
)
from aigol.runtime.platform_change_impact_analysis_runtime import (
    FAILED_CLOSED as IMPACT_FAILED_CLOSED,
    analyze_platform_change_impact,
    reconstruct_platform_change_impact_replay,
)
from aigol.runtime.platform_change_normalization_runtime import (
    FAILED_CLOSED as NORMALIZATION_FAILED_CLOSED,
    NORMALIZED_CHANGE_ARTIFACT_V1,
    validate_normalized_change_artifact,
)
from aigol.runtime.platform_validation_planning_runtime import (
    FAILED_CLOSED as PLANNING_FAILED_CLOSED,
    plan_platform_validation,
    reconstruct_platform_validation_plan_replay,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


INTELLIGENT_VALIDATION_ENGINE_V0_RUNTIME_VERSION = (
    "G36_01_INTELLIGENT_VALIDATION_ENGINE_V0_RUNTIME_V1"
)
INTELLIGENT_VALIDATION_PLAN_ARTIFACT_V1 = "INTELLIGENT_VALIDATION_PLAN_ARTIFACT_V1"
IVE_ANALYSIS_COMPLETED = "IVE_ANALYSIS_COMPLETED"
IVE_ANALYSIS_COMPLETED_WITH_UNRESOLVED_MAPPINGS = (
    "IVE_ANALYSIS_COMPLETED_WITH_UNRESOLVED_MAPPINGS"
)
FAILED_CLOSED = "FAILED_CLOSED"
REPLAY_STEP = "intelligent_validation_plan_recorded"

COMPONENT_CLASSIFICATION_ORDER = (
    "PLATFORM_CORE",
    "REPLAY",
    "AUTHORIZATION",
    "WORKER",
    "PROVIDER",
    "AICLI",
    "GOVERNANCE",
    "TEST_INFRASTRUCTURE",
    "DOCUMENTATION",
)

VALIDATION_DIMENSIONS_BY_COMPONENT_TYPE = {
    "PLATFORM_CORE": ("UNIT", "INTEGRATION", "REPLAY"),
    "REPLAY": ("UNIT", "INTEGRATION", "REPLAY"),
    "AUTHORIZATION": ("UNIT", "INTEGRATION", "REPLAY", "AUTHORIZATION"),
    "WORKER": ("UNIT", "INTEGRATION", "REPLAY", "AUTHORIZATION", "WORKER"),
    "PROVIDER": ("UNIT", "INTEGRATION", "REPLAY", "PROVIDER"),
    "AICLI": ("UNIT", "INTEGRATION", "REPLAY", "AICLI"),
    "GOVERNANCE": ("UNIT", "INTEGRATION", "REPLAY"),
    "TEST_INFRASTRUCTURE": ("UNIT", "INTEGRATION"),
    "DOCUMENTATION": (),
}

RECOMMENDATION_FIELDS = {
    "UNIT": "required_unit_tests",
    "INTEGRATION": "required_integration_tests",
    "REPLAY": "required_replay_validation",
    "AUTHORIZATION": "required_authorization_validation",
    "WORKER": "required_worker_validation",
    "PROVIDER": "required_provider_validation",
    "AICLI": "required_aicli_validation",
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
}


def analyze_intelligent_validation_scope(
    *,
    ive_analysis_id: str,
    normalized_change_artifact: dict[str, Any],
    normalized_change_reference: str,
    normalized_change_hash: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Compose an IVE-0 recommendation without approving or executing it."""

    replay_path = Path(replay_dir)
    impact_artifact: dict[str, Any] | None = None
    plan_artifact: dict[str, Any] | None = None
    try:
        _ensure_replay_available(replay_path)
        analysis_id = _require_string(ive_analysis_id, "ive_analysis_id")
        source_reference = _require_string(
            normalized_change_reference,
            "normalized_change_reference",
        )
        source_hash = _require_hash(normalized_change_hash, "normalized_change_hash")
        timestamp = _require_string(created_at, "created_at")
        source = validate_normalized_change_artifact(normalized_change_artifact)
        _validate_normalized_source_binding(
            source,
            source_reference,
            source_hash,
        )
        lineage_digest = replay_hash(
            {
                "normalized_change_reference": source_reference,
                "normalized_change_hash": source_hash,
            }
        ).removeprefix("sha256:")

        analysis_strategy = _analysis_strategy(source)
        if analysis_strategy == "G27_CERTIFIED_IMPACT_AND_PLANNING":
            impact_capture = analyze_platform_change_impact(
                impact_analysis_id=f"IVE-0-IMPACT-{lineage_digest}",
                normalized_change_artifact=source,
                normalized_change_reference=source_reference,
                normalized_change_hash=source_hash,
                created_at=timestamp,
                replay_dir=replay_path / "impact",
            )
            impact_artifact = impact_capture["platform_change_impact_artifact"]
            if impact_capture["impact_status"] == IMPACT_FAILED_CLOSED:
                raise FailClosedRuntimeError(
                    f"IVE-0 failed closed: {impact_capture['failure_reason']}"
                )

            plan_capture = plan_platform_validation(
                validation_plan_id=f"IVE-0-VALIDATION-PLAN-{lineage_digest}",
                platform_change_impact_artifact=impact_artifact,
                platform_change_impact_reference=impact_artifact[
                    "impact_analysis_id"
                ],
                platform_change_impact_hash=impact_artifact[
                    "platform_change_impact_hash"
                ],
                created_at=timestamp,
                replay_dir=replay_path / "validation_plan",
            )
            plan_artifact = plan_capture["platform_validation_plan_artifact"]
            if plan_capture["planning_status"] == PLANNING_FAILED_CLOSED:
                raise FailClosedRuntimeError(
                    f"IVE-0 failed closed: {plan_capture['failure_reason']}"
                )
            components = _affected_components(impact_artifact)
        else:
            components = _direct_path_affected_components(source)
        classification = _impact_classification(components)
        recommendation = _validation_recommendation(
            components=components,
            normalized_change_artifact=source,
            validation_plan_artifact=plan_artifact,
        )
        reasoning = _constitutional_reasoning(
            classification=classification,
            recommendation=recommendation,
        )
        status = (
            IVE_ANALYSIS_COMPLETED_WITH_UNRESOLVED_MAPPINGS
            if source["unresolved_mappings"]
            or (
                impact_artifact is not None
                and impact_artifact["unresolved_mappings"]
            )
            or (
                plan_artifact is not None
                and plan_artifact["unresolved_mappings"]
            )
            else IVE_ANALYSIS_COMPLETED
        )
        artifact = _ive_artifact(
            ive_analysis_id=analysis_id,
            analysis_status=status,
            normalized_change_reference=source_reference,
            normalized_change_hash=source_hash,
            normalized_change_artifact_hash=_require_hash(
                source.get("artifact_hash"),
                "normalized_change_artifact.artifact_hash",
            ),
            analysis_strategy=analysis_strategy,
            impact_artifact=impact_artifact,
            plan_artifact=plan_artifact,
            affected_components=components,
            classification=classification,
            recommendation=recommendation,
            reasoning=reasoning,
            created_at=timestamp,
            failure_reason=None,
        )
    except Exception as exc:
        artifact = _failed_artifact(
            ive_analysis_id=ive_analysis_id,
            normalized_change_artifact=normalized_change_artifact,
            normalized_change_reference=normalized_change_reference,
            normalized_change_hash=normalized_change_hash,
            impact_artifact=impact_artifact,
            plan_artifact=plan_artifact,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
    _persist_if_possible(replay_path, artifact)
    return _capture(artifact, replay_path)


def validate_intelligent_validation_plan_artifact(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Validate one IVE-0 planning artifact without consulting mutable state."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(
            "IVE-0 intelligent validation plan artifact must be a JSON object"
        )
    candidate = deepcopy(artifact)
    _verify_ive_artifact(candidate)
    return candidate


def reconstruct_intelligent_validation_engine_v0_replay(
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Reconstruct IVE-0 evidence and its successful G27 lineage."""

    replay_path = Path(replay_dir)
    wrapper = load_json(replay_path / f"000_{REPLAY_STEP}.json")
    if wrapper.get("replay_index") != 0 or wrapper.get("replay_step") != REPLAY_STEP:
        raise FailClosedRuntimeError("IVE-0 replay ordering mismatch")
    _verify_hash(wrapper, "replay_hash", "IVE-0 replay hash mismatch")
    artifact = validate_intelligent_validation_plan_artifact(wrapper.get("artifact"))

    if (
        artifact["analysis_status"] != FAILED_CLOSED
        and artifact["analysis_strategy"]
        == "G27_CERTIFIED_IMPACT_AND_PLANNING"
    ):
        impact = reconstruct_platform_change_impact_replay(replay_path / "impact")
        plan = reconstruct_platform_validation_plan_replay(
            replay_path / "validation_plan"
        )
        if impact["artifact_hash"] != artifact["platform_change_impact_artifact_hash"]:
            raise FailClosedRuntimeError("IVE-0 impact replay lineage mismatch")
        if (
            impact["platform_change_impact_hash"]
            != artifact["platform_change_impact_hash"]
        ):
            raise FailClosedRuntimeError("IVE-0 impact hash lineage mismatch")
        if plan["artifact_hash"] != artifact["platform_validation_plan_artifact_hash"]:
            raise FailClosedRuntimeError("IVE-0 validation plan replay lineage mismatch")
        if (
            plan["platform_validation_plan_hash"]
            != artifact["platform_validation_plan_hash"]
        ):
            raise FailClosedRuntimeError("IVE-0 validation plan hash lineage mismatch")

    return {
        "ive_analysis_id": artifact["ive_analysis_id"],
        "analysis_status": artifact["analysis_status"],
        "normalized_change_reference": artifact["normalized_change_reference"],
        "normalized_change_hash": artifact["normalized_change_hash"],
        "analysis_strategy": artifact["analysis_strategy"],
        "affected_components": deepcopy(artifact["affected_components"]),
        "impact_classification": deepcopy(artifact["impact_classification"]),
        "validation_recommendation": deepcopy(
            artifact["validation_recommendation"]
        ),
        "supporting_constitutional_reasoning": deepcopy(
            artifact["supporting_constitutional_reasoning"]
        ),
        "intelligent_validation_plan_hash": artifact[
            "intelligent_validation_plan_hash"
        ],
        "artifact_hash": artifact["artifact_hash"],
        "replay_visible": True,
        "fail_closed": artifact["analysis_status"] == FAILED_CLOSED,
        "failure_reason": artifact["failure_reason"],
        "authority_flags": deepcopy(artifact["authority_flags"]),
        "replay_hash": wrapper["replay_hash"],
    }


def _validate_normalized_source_binding(
    source: dict[str, Any],
    source_reference: str,
    source_hash: str,
) -> None:
    if source.get("artifact_type") != NORMALIZED_CHANGE_ARTIFACT_V1:
        raise FailClosedRuntimeError(
            "IVE-0 failed closed: normalized change artifact required"
        )
    if source.get("normalization_status") == NORMALIZATION_FAILED_CLOSED:
        raise FailClosedRuntimeError(
            "IVE-0 failed closed: source normalization failed closed"
        )
    if source.get("normalization_id") != source_reference:
        raise FailClosedRuntimeError(
            "IVE-0 failed closed: normalized change reference mismatch"
        )
    if source.get("normalized_change_hash") != source_hash:
        raise FailClosedRuntimeError(
            "IVE-0 failed closed: normalized change hash mismatch"
        )


def _analysis_strategy(source: dict[str, Any]) -> str:
    registry = list_platform_capability_certifications()
    all_g27_eligible = True
    for entry in source["change_entries"]:
        path = _require_string(entry.get("target_path"), "target_path")
        matches = _registry_matches(path, registry)
        if len(matches) > 1:
            raise FailClosedRuntimeError(
                f"IVE-0 failed closed: ambiguous capability mapping for {path}"
            )
        _direct_component_type(path, matches[0] if matches else None)
        if len(matches) != 1 or not _g27_layer_path_supported(path):
            all_g27_eligible = False
    return (
        "G27_CERTIFIED_IMPACT_AND_PLANNING"
        if all_g27_eligible
        else "IVE_0_DIRECT_EXACT_PATH_DISCOVERY"
    )


def _g27_layer_path_supported(path: str) -> bool:
    return (
        path.startswith(
            (
                "governance/phases/LAYER_0_",
                ".github/governance/manifests/",
                "docs/governance/",
                ".github/governance/",
                "runtime/governance/",
                "aigol/runtime/",
                "runtime/",
                "aigol/cli/",
                "sapianta_bridge/protocol/",
                "tests/",
                "research/",
                "docs/product_lifecycle/",
                "scripts/",
                "web/",
                "mobile/",
            )
        )
        or path
        in {
            "docs/governance/CONSTITUTIONAL_ARCHITECTURE_SPEC_V1.md",
            "docs/governance/CANONICAL_LAYER_MODEL.md",
            "docs/governance/CONSTITUTIONAL_INVARIANTS.md",
            "docs/governance/GOVERNANCE_ENFORCEMENT_HIERARCHY.md",
            "docs/governance/GOVERNANCE_LINEAGE_MODEL.md",
            "docs/governance/STABLE_SUBSTRATE_DECLARATION_V1.md",
            "scripts/check_layer_freeze.py",
            "sapianta_system/governance/phases/LAYER_0_FREEZE.yaml",
        }
    )


def _registry_matches(
    path: str,
    registry: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    matches = []
    for record in registry:
        implementation_path = (
            _require_string(
                record.get("implementation_owner"),
                "implementation_owner",
            ).replace(".", "/")
            + ".py"
        )
        evidence_paths = tuple(
            str(item) for item in record.get("certification_evidence", ())
        )
        if path == implementation_path or path in evidence_paths:
            matches.append(record)
    return sorted(matches, key=lambda item: item["capability_identifier"])


def _direct_path_affected_components(
    source: dict[str, Any],
) -> list[dict[str, Any]]:
    registry = list_platform_capability_certifications()
    components = []
    for entry in source["change_entries"]:
        path = _require_string(entry.get("target_path"), "target_path")
        matches = _registry_matches(path, registry)
        if len(matches) > 1:
            raise FailClosedRuntimeError(
                f"IVE-0 failed closed: ambiguous capability mapping for {path}"
            )
        record = matches[0] if matches else None
        component_type, classification_rule = _direct_component_type(path, record)
        capability_id = (
            record["capability_identifier"]
            if record is not None
            else f"REPOSITORY_PATH:{path}"
        )
        component = {
            "component_identifier": f"{capability_id}:{path}",
            "component_type": component_type,
            "capability_identifier": capability_id,
            "target_path": path,
            "dependency_origin": (
                "PLATFORM_CAPABILITY_REGISTRY_EXACT_PATH"
                if record is not None
                else "NORMALIZED_CHANGE_DIRECT_TARGET"
            ),
            "reason_for_inclusion": (
                "The exact normalized proposed-mutation path is included by the "
                "IVE-0 direct repository component inventory."
            ),
            "classification_rule": classification_rule,
            "constitutional_layer": _direct_constitutional_layer(path),
            "impact_entry_hash": entry["change_entry_hash"],
            "certification_evidence": (
                list(record["certification_evidence"])
                if record is not None
                else []
            ),
        }
        component["component_hash"] = replay_hash(component)
        components.append(component)
    components.sort(
        key=lambda item: (
            COMPONENT_CLASSIFICATION_ORDER.index(item["component_type"]),
            item["component_identifier"],
        )
    )
    if not components:
        raise FailClosedRuntimeError("IVE-0 failed closed: no affected components")
    return components


def _direct_component_type(
    path: str,
    registry_record: dict[str, Any] | None,
) -> tuple[str, str]:
    tokens = ""
    if registry_record is not None:
        tokens = " ".join(
            (
                str(registry_record.get("capability_owner", "")),
                str(registry_record.get("capability_identifier", "")),
                str(registry_record.get("implementation_owner", "")),
            )
        ).upper()
    return _component_type_from_values(path, tokens)


def _direct_constitutional_layer(path: str) -> str:
    if path.startswith(("docs/governance/", ".github/governance/", "runtime/governance/")):
        return "L3"
    if path.startswith(
        (
            "aigol/runtime/",
            "runtime/",
            "aigol/cli/",
            "aigol/workers/",
            "aigol/providers/",
            "aigol/provider",
            "aigol/authorization/",
            "sapianta_bridge/protocol/",
        )
    ):
        return "L2"
    if path.startswith(
        (
            "tests/",
            "research/",
            "docs/",
            "scripts/",
            "web/",
            "mobile/",
        )
    ):
        return "L4"
    raise FailClosedRuntimeError(
        f"IVE-0 failed closed: unsupported constitutional layer for {path}"
    )


def _affected_components(impact: dict[str, Any]) -> list[dict[str, Any]]:
    capability_evidence = {
        item["capability_identifier"]: list(item["certification_evidence"])
        for item in impact["affected_capabilities"]
    }
    components = []
    for entry in impact["impact_entries"]:
        component_type, classification_rule = _component_type(entry)
        component = {
            "component_identifier": (
                f"{entry['capability_identifier']}:{entry['target_path']}"
            ),
            "component_type": component_type,
            "capability_identifier": entry["capability_identifier"],
            "target_path": entry["target_path"],
            "dependency_origin": entry["capability_mapping_source"],
            "reason_for_inclusion": (
                "The normalized proposed mutation targets an exact path bound to "
                f"{entry['capability_identifier']} by the Platform Capability "
                "Certification Registry."
            ),
            "classification_rule": classification_rule,
            "constitutional_layer": entry["constitutional_layer"],
            "impact_entry_hash": entry["impact_entry_hash"],
            "certification_evidence": capability_evidence[
                entry["capability_identifier"]
            ],
        }
        component["component_hash"] = replay_hash(component)
        components.append(component)
    components.sort(
        key=lambda item: (
            COMPONENT_CLASSIFICATION_ORDER.index(item["component_type"]),
            item["component_identifier"],
        )
    )
    if not components:
        raise FailClosedRuntimeError("IVE-0 failed closed: no affected components")
    return components


def _component_type(entry: dict[str, Any]) -> tuple[str, str]:
    path = _require_string(entry.get("target_path"), "target_path")
    owner = _require_string(entry.get("capability_owner"), "capability_owner")
    capability = _require_string(
        entry.get("capability_identifier"),
        "capability_identifier",
    )
    implementation_owner = _require_string(
        entry.get("implementation_owner"),
        "implementation_owner",
    )
    tokens = f"{owner} {capability} {implementation_owner}".upper()
    return _component_type_from_values(path, tokens)


def _component_type_from_values(path: str, tokens: str) -> tuple[str, str]:
    if path.startswith(("docs/governance/", ".github/governance/", "runtime/governance/")):
        return "GOVERNANCE", "EXACT_GOVERNANCE_PATH"
    if path.startswith("tests/"):
        return "TEST_INFRASTRUCTURE", "EXACT_TEST_INFRASTRUCTURE_PATH"
    if path.startswith("aigol/authorization/") or "AUTHORIZATION" in tokens:
        return "AUTHORIZATION", "EXACT_AUTHORIZATION_OWNER_OR_PATH"
    if path.startswith("aigol/workers/"):
        return "WORKER", "EXACT_WORKER_PATH"
    if path.startswith(("aigol/providers/", "aigol/provider")) or "PROVIDER_PLATFORM" in tokens:
        return "PROVIDER", "EXACT_PROVIDER_OWNER_OR_PATH"
    if path.startswith("aigol/cli/") or path == "aicli":
        return "AICLI", "EXACT_AICLI_PATH"
    if "REPLAY" in tokens or "/replay" in path or "_replay" in path:
        return "REPLAY", "EXACT_REPLAY_OWNER_OR_PATH"
    if path.startswith("docs/"):
        return "DOCUMENTATION", "EXACT_DOCUMENTATION_PATH"
    if path.startswith(
        ("aigol/runtime/", "runtime/", "sapianta_bridge/protocol/")
    ):
        return "PLATFORM_CORE", "EXACT_PLATFORM_CORE_RUNTIME_PATH"
    raise FailClosedRuntimeError(
        f"IVE-0 failed closed: unsupported component classification for {path}"
    )


def _impact_classification(
    components: list[dict[str, Any]],
) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for component in components:
        grouped.setdefault(component["component_type"], []).append(
            {
                "component_identifier": component["component_identifier"],
                "component_hash": component["component_hash"],
                "classification_rule": component["classification_rule"],
            }
        )
    classifications = [
        {
            "classification": component_type,
            "supporting_evidence": sorted(
                grouped[component_type],
                key=lambda item: item["component_identifier"],
            ),
            "evidence_count": len(grouped[component_type]),
        }
        for component_type in COMPONENT_CLASSIFICATION_ORDER
        if component_type in grouped
    ]
    overall = (
        classifications[0]["classification"]
        if len(classifications) == 1
        else "MULTI_COMPONENT"
    )
    classification = {
        "overall_classification": overall,
        "classifications": classifications,
        "classification_count": len(classifications),
        "classification_policy": (
            "IVE_0_EXACT_PATH_AND_CERTIFIED_OWNER_CLASSIFICATION_V1"
        ),
        "probabilistic_inference_used": False,
        "heuristic_inference_used": False,
    }
    classification["classification_hash"] = replay_hash(classification)
    return classification


def _validation_recommendation(
    *,
    components: list[dict[str, Any]],
    normalized_change_artifact: dict[str, Any],
    validation_plan_artifact: dict[str, Any] | None,
) -> dict[str, Any]:
    recommendation: dict[str, Any] = {
        field: [] for field in RECOMMENDATION_FIELDS.values()
    }
    by_type: dict[str, list[dict[str, Any]]] = {}
    for component in components:
        by_type.setdefault(component["component_type"], []).append(component)

    for component_type in COMPONENT_CLASSIFICATION_ORDER:
        typed_components = by_type.get(component_type, [])
        if not typed_components:
            continue
        for dimension in VALIDATION_DIMENSIONS_BY_COMPONENT_TYPE[component_type]:
            field = RECOMMENDATION_FIELDS[dimension]
            requirement = {
                "validation_dimension": dimension,
                "component_type": component_type,
                "affected_component_identifiers": sorted(
                    item["component_identifier"] for item in typed_components
                ),
                "source_component_hashes": sorted(
                    item["component_hash"] for item in typed_components
                ),
                "reason": (
                    f"IVE-0 policy requires {dimension} validation for "
                    f"{component_type} impact."
                ),
                "mapping_authority": "IVE_0_COMPONENT_TYPE_VALIDATION_POLICY_V1",
                "required": True,
            }
            requirement["requirement_hash"] = replay_hash(requirement)
            recommendation[field].append(requirement)

    affected_types = set(by_type)
    full_regression_required = any(
        component_type != "DOCUMENTATION" for component_type in affected_types
    )
    full_regression_reason = (
        "At least one affected component is executable, constitutional, "
        "governance-owned, or test-infrastructure-owned."
        if full_regression_required
        else "All affected components are non-governance documentation."
    )
    certification_evidence_tests = sorted(
        {
            evidence_path
            for component in components
            for evidence_path in component["certification_evidence"]
            if evidence_path.startswith("tests/")
        }
    )
    command_references = (
        deepcopy(validation_plan_artifact["allowlisted_command_references"])
        if validation_plan_artifact is not None
        else []
    )
    handoff_status = (
        "READY_FOR_EXISTING_G27_09_CANDIDATE_COMPOSITION"
        if command_references
        else "PLANNING_ONLY_NO_EXACT_ALLOWLIST_MAPPING"
    )
    recommendation.update(
        {
            "certification_evidence_test_targets": certification_evidence_tests,
            "certification_evidence_target_semantics": (
                "EXACT_REGISTRY_EVIDENCE_PATHS; TEST_KIND_NOT_INFERRED"
            ),
            "full_regression": {
                "required": full_regression_required,
                "reason": full_regression_reason,
                "mapping_authority": (
                    "IVE_0_NON_DOCUMENTATION_FULL_REGRESSION_POLICY_V1"
                ),
            },
            "existing_allowlisted_command_references": command_references,
            "existing_validation_pipeline_handoff": {
                "status": handoff_status,
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
                "approval_status": "PENDING_DOWNSTREAM_CANDIDATE",
                "must_bind_exact_candidate_hash": True,
                "approval_authorizes_execution_by_itself": False,
            },
            "source_validation_requirement_ids": [
                item["requirement_id"]
                for item in (
                    validation_plan_artifact["validation_requirements"]
                    if validation_plan_artifact is not None
                    else []
                )
            ],
            "unresolved_mappings": deepcopy(
                (
                    validation_plan_artifact["unresolved_mappings"]
                    if validation_plan_artifact is not None
                    else normalized_change_artifact["unresolved_mappings"]
                )
            ),
            "recommendation_is_advisory": True,
            "validation_executed": False,
        }
    )
    recommendation["recommendation_hash"] = replay_hash(recommendation)
    return recommendation


def _constitutional_reasoning(
    *,
    classification: dict[str, Any],
    recommendation: dict[str, Any],
) -> list[dict[str, Any]]:
    raw = [
        {
            "reasoning_id": "IVE-0-REASON-001",
            "constitutional_basis": "DETERMINISTIC_IMPACT_ONLY",
            "statement": (
                "Classification is derived only from exact normalized paths and "
                "certified registry ownership."
            ),
            "evidence_hashes": [classification["classification_hash"]],
        },
        {
            "reasoning_id": "IVE-0-REASON-002",
            "constitutional_basis": "HUMAN_AUTHORITY_PRESERVED",
            "statement": (
                "The recommendation remains inert until the existing validation "
                "candidate is explicitly approved and separately authorized."
            ),
            "evidence_hashes": [recommendation["recommendation_hash"]],
        },
        {
            "reasoning_id": "IVE-0-REASON-003",
            "constitutional_basis": "EXISTING_VALIDATION_PIPELINE_PRESERVED",
            "statement": (
                "IVE-0 neither synthesizes commands nor invokes validation, "
                "Workers, Providers, Authorization, or execution gates."
            ),
            "evidence_hashes": [recommendation["recommendation_hash"]],
        },
    ]
    reasoning = []
    for item in raw:
        item["reasoning_hash"] = replay_hash(item)
        reasoning.append(item)
    return reasoning


def _ive_artifact(
    *,
    ive_analysis_id: str,
    analysis_status: str,
    normalized_change_reference: str,
    normalized_change_hash: str,
    normalized_change_artifact_hash: str,
    analysis_strategy: str,
    impact_artifact: dict[str, Any] | None,
    plan_artifact: dict[str, Any] | None,
    affected_components: list[dict[str, Any]],
    classification: dict[str, Any],
    recommendation: dict[str, Any],
    reasoning: list[dict[str, Any]],
    created_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": INTELLIGENT_VALIDATION_PLAN_ARTIFACT_V1,
        "runtime_version": INTELLIGENT_VALIDATION_ENGINE_V0_RUNTIME_VERSION,
        "ive_analysis_id": ive_analysis_id,
        "analysis_status": analysis_status,
        "source_artifact_type": NORMALIZED_CHANGE_ARTIFACT_V1,
        "normalized_change_reference": normalized_change_reference,
        "normalized_change_hash": normalized_change_hash,
        "normalized_change_artifact_hash": normalized_change_artifact_hash,
        "analysis_strategy": analysis_strategy,
        "platform_change_impact_reference": _artifact_value(
            impact_artifact,
            "impact_analysis_id",
        ),
        "platform_change_impact_hash": _artifact_hash_value(
            impact_artifact,
            "platform_change_impact_hash",
        ),
        "platform_change_impact_artifact_hash": _artifact_hash_value(
            impact_artifact,
            "artifact_hash",
        ),
        "platform_change_impact_replay_reference": "impact",
        "platform_change_impact_usage": (
            "USED"
            if analysis_strategy == "G27_CERTIFIED_IMPACT_AND_PLANNING"
            else "NOT_APPLICABLE_DIRECT_PATH_DISCOVERY"
        ),
        "platform_validation_plan_reference": _artifact_value(
            plan_artifact,
            "validation_plan_id",
        ),
        "platform_validation_plan_hash": _artifact_hash_value(
            plan_artifact,
            "platform_validation_plan_hash",
        ),
        "platform_validation_plan_artifact_hash": _artifact_hash_value(
            plan_artifact,
            "artifact_hash",
        ),
        "platform_validation_plan_replay_reference": "validation_plan",
        "platform_validation_plan_usage": (
            "USED"
            if analysis_strategy == "G27_CERTIFIED_IMPACT_AND_PLANNING"
            else "NOT_APPLICABLE_DIRECT_PATH_DISCOVERY"
        ),
        "affected_components": deepcopy(affected_components),
        "affected_component_count": len(affected_components),
        "impact_classification": deepcopy(classification),
        "validation_recommendation": deepcopy(recommendation),
        "supporting_constitutional_reasoning": deepcopy(reasoning),
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
        "aicli_modified": False,
        "repository_mutated": False,
        "replay_semantics_modified": False,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "failure_reason": failure_reason,
    }
    artifact["intelligent_validation_plan_hash"] = _ive_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_artifact(
    *,
    ive_analysis_id: Any,
    normalized_change_artifact: Any,
    normalized_change_reference: Any,
    normalized_change_hash: Any,
    impact_artifact: dict[str, Any] | None,
    plan_artifact: dict[str, Any] | None,
    created_at: Any,
    failure_reason: str,
) -> dict[str, Any]:
    source_artifact_hash = (
        normalized_change_artifact.get("artifact_hash")
        if isinstance(normalized_change_artifact, dict)
        else None
    )
    classification = {
        "overall_classification": "UNDETERMINED",
        "classifications": [],
        "classification_count": 0,
        "classification_policy": (
            "IVE_0_EXACT_PATH_AND_CERTIFIED_OWNER_CLASSIFICATION_V1"
        ),
        "probabilistic_inference_used": False,
        "heuristic_inference_used": False,
    }
    classification["classification_hash"] = replay_hash(classification)
    recommendation: dict[str, Any] = {
        field: [] for field in RECOMMENDATION_FIELDS.values()
    }
    recommendation.update(
        {
            "certification_evidence_test_targets": [],
            "certification_evidence_target_semantics": (
                "EXACT_REGISTRY_EVIDENCE_PATHS; TEST_KIND_NOT_INFERRED"
            ),
            "full_regression": {
                "required": True,
                "reason": "IVE-0 failed closed; no reduced scope may be claimed.",
                "mapping_authority": "IVE_0_FAIL_CLOSED_POLICY_V1",
            },
            "existing_allowlisted_command_references": [],
            "existing_validation_pipeline_handoff": {
                "status": "BLOCKED_BY_IVE_0_FAILURE",
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
            "source_validation_requirement_ids": [],
            "unresolved_mappings": [],
            "recommendation_is_advisory": True,
            "validation_executed": False,
        }
    )
    recommendation["recommendation_hash"] = replay_hash(recommendation)
    reasoning = _constitutional_reasoning(
        classification=classification,
        recommendation=recommendation,
    )
    return _ive_artifact(
        ive_analysis_id=_safe_string(ive_analysis_id),
        analysis_status=FAILED_CLOSED,
        normalized_change_reference=_safe_string(normalized_change_reference),
        normalized_change_hash=_safe_hash(normalized_change_hash),
        normalized_change_artifact_hash=_safe_hash(source_artifact_hash),
        analysis_strategy="FAILED_CLOSED_NO_ANALYSIS_STRATEGY",
        impact_artifact=impact_artifact,
        plan_artifact=plan_artifact,
        affected_components=[],
        classification=classification,
        recommendation=recommendation,
        reasoning=reasoning,
        created_at=_safe_string(created_at),
        failure_reason=failure_reason,
    )


def _verify_ive_artifact(artifact: dict[str, Any]) -> None:
    if artifact.get("artifact_type") != INTELLIGENT_VALIDATION_PLAN_ARTIFACT_V1:
        raise FailClosedRuntimeError("IVE-0 artifact type mismatch")
    _verify_hash(artifact, "artifact_hash", "IVE-0 artifact hash mismatch")
    if artifact.get("intelligent_validation_plan_hash") != _ive_hash(artifact):
        raise FailClosedRuntimeError("IVE-0 deterministic plan hash mismatch")
    if (
        artifact.get("replay_visible") is not True
        or artifact.get("read_only") is not True
        or artifact.get("non_authoritative") is not True
    ):
        raise FailClosedRuntimeError(
            "IVE-0 artifact must be replay-visible, read-only, and non-authoritative"
        )
    if any(value is not False for value in artifact.get("authority_flags", {}).values()):
        raise FailClosedRuntimeError("IVE-0 cannot grant authority")
    for field in (
        "human_approval_recorded",
        "validation_candidate_constructed",
        "validation_executed",
        "authorization_invoked",
        "worker_invoked",
        "provider_invoked",
        "aicli_modified",
        "repository_mutated",
        "replay_semantics_modified",
    ):
        if artifact.get(field) is not False:
            raise FailClosedRuntimeError(f"IVE-0 {field} must be false")
    if artifact.get("human_approval_required") is not True:
        raise FailClosedRuntimeError("IVE-0 human approval requirement missing")

    status = artifact.get("analysis_status")
    if status not in {
        IVE_ANALYSIS_COMPLETED,
        IVE_ANALYSIS_COMPLETED_WITH_UNRESOLVED_MAPPINGS,
        FAILED_CLOSED,
    }:
        raise FailClosedRuntimeError("IVE-0 status is invalid")
    strategy = artifact.get("analysis_strategy")
    if status == FAILED_CLOSED:
        if strategy != "FAILED_CLOSED_NO_ANALYSIS_STRATEGY":
            raise FailClosedRuntimeError("failed IVE-0 strategy is invalid")
    elif strategy not in {
        "G27_CERTIFIED_IMPACT_AND_PLANNING",
        "IVE_0_DIRECT_EXACT_PATH_DISCOVERY",
    }:
        raise FailClosedRuntimeError("IVE-0 analysis strategy is invalid")
    expected_usage = (
        "USED"
        if strategy == "G27_CERTIFIED_IMPACT_AND_PLANNING"
        else "NOT_APPLICABLE_DIRECT_PATH_DISCOVERY"
    )
    if status != FAILED_CLOSED and (
        artifact.get("platform_change_impact_usage") != expected_usage
        or artifact.get("platform_validation_plan_usage") != expected_usage
    ):
        raise FailClosedRuntimeError("IVE-0 G27 lineage usage mismatch")
    components = artifact.get("affected_components")
    if not isinstance(components, list) or artifact.get(
        "affected_component_count"
    ) != len(components):
        raise FailClosedRuntimeError("IVE-0 affected component count mismatch")
    for component in components:
        _verify_hash(component, "component_hash", "IVE-0 component hash mismatch")
        if component.get("component_type") not in COMPONENT_CLASSIFICATION_ORDER:
            raise FailClosedRuntimeError("IVE-0 component type is invalid")

    classification = artifact.get("impact_classification")
    recommendation = artifact.get("validation_recommendation")
    reasoning = artifact.get("supporting_constitutional_reasoning")
    if not isinstance(classification, dict):
        raise FailClosedRuntimeError("IVE-0 classification must be an object")
    if not isinstance(recommendation, dict):
        raise FailClosedRuntimeError("IVE-0 recommendation must be an object")
    if not isinstance(reasoning, list):
        raise FailClosedRuntimeError("IVE-0 reasoning must be a list")
    _verify_hash(
        classification,
        "classification_hash",
        "IVE-0 classification hash mismatch",
    )
    _verify_hash(
        recommendation,
        "recommendation_hash",
        "IVE-0 recommendation hash mismatch",
    )
    for item in reasoning:
        _verify_hash(item, "reasoning_hash", "IVE-0 reasoning hash mismatch")
    if status != FAILED_CLOSED:
        if classification != _impact_classification(components):
            raise FailClosedRuntimeError(
                "IVE-0 classification does not match affected components"
            )
        _verify_recommendation(
            recommendation,
            components=components,
            analysis_strategy=strategy,
        )
    else:
        if classification.get("overall_classification") != "UNDETERMINED":
            raise FailClosedRuntimeError(
                "failed IVE-0 classification must be undetermined"
            )
        if (
            recommendation.get("full_regression", {}).get("required") is not True
            or recommendation.get(
                "existing_validation_pipeline_handoff",
                {},
            ).get("status")
            != "BLOCKED_BY_IVE_0_FAILURE"
        ):
            raise FailClosedRuntimeError(
                "failed IVE-0 recommendation must block reduced-scope handoff"
            )
    if reasoning != _constitutional_reasoning(
        classification=classification,
        recommendation=recommendation,
    ):
        raise FailClosedRuntimeError(
            "IVE-0 constitutional reasoning does not match evidence"
        )
    if (
        recommendation.get("human_approval", {}).get("required_before_execution")
        is not True
    ):
        raise FailClosedRuntimeError("IVE-0 recommendation bypasses human approval")
    if recommendation.get("validation_executed") is not False:
        raise FailClosedRuntimeError("IVE-0 recommendation cannot execute validation")

    if status == FAILED_CLOSED:
        if components:
            raise FailClosedRuntimeError(
                "failed IVE-0 artifact cannot claim affected components"
            )
        if not artifact.get("failure_reason"):
            raise FailClosedRuntimeError(
                "failed IVE-0 artifact requires a failure reason"
            )
    elif not components:
        raise FailClosedRuntimeError(
            "successful IVE-0 artifact requires affected components"
        )


def _verify_recommendation(
    recommendation: dict[str, Any],
    *,
    components: list[dict[str, Any]],
    analysis_strategy: str,
) -> None:
    by_type: dict[str, list[dict[str, Any]]] = {}
    for component in components:
        by_type.setdefault(component["component_type"], []).append(component)

    expected_pairs = {
        (
            RECOMMENDATION_FIELDS[dimension],
            component_type,
            dimension,
        )
        for component_type in by_type
        for dimension in VALIDATION_DIMENSIONS_BY_COMPONENT_TYPE[component_type]
    }
    observed_pairs: set[tuple[str, str, str]] = set()
    for field in RECOMMENDATION_FIELDS.values():
        requirements = recommendation.get(field)
        if not isinstance(requirements, list):
            raise FailClosedRuntimeError(
                f"IVE-0 recommendation {field} must be a list"
            )
        for requirement in requirements:
            if not isinstance(requirement, dict):
                raise FailClosedRuntimeError(
                    "IVE-0 validation requirement must be an object"
                )
            _verify_hash(
                requirement,
                "requirement_hash",
                "IVE-0 validation requirement hash mismatch",
            )
            component_type = requirement.get("component_type")
            dimension = requirement.get("validation_dimension")
            typed_components = by_type.get(component_type)
            if not typed_components:
                raise FailClosedRuntimeError(
                    "IVE-0 validation requirement component type mismatch"
                )
            if requirement.get("affected_component_identifiers") != sorted(
                item["component_identifier"] for item in typed_components
            ):
                raise FailClosedRuntimeError(
                    "IVE-0 validation requirement component identity mismatch"
                )
            if requirement.get("source_component_hashes") != sorted(
                item["component_hash"] for item in typed_components
            ):
                raise FailClosedRuntimeError(
                    "IVE-0 validation requirement component hash mismatch"
                )
            if requirement.get("required") is not True:
                raise FailClosedRuntimeError(
                    "IVE-0 validation requirement must be required"
                )
            observed_pairs.add((field, component_type, dimension))
    if observed_pairs != expected_pairs:
        raise FailClosedRuntimeError(
            "IVE-0 validation dimensions do not match affected components"
        )

    expected_evidence_tests = sorted(
        {
            path
            for component in components
            for path in component["certification_evidence"]
            if path.startswith("tests/")
        }
    )
    if (
        recommendation.get("certification_evidence_test_targets")
        != expected_evidence_tests
    ):
        raise FailClosedRuntimeError(
            "IVE-0 certification evidence test targets mismatch"
        )
    expected_full_regression = any(
        component_type != "DOCUMENTATION" for component_type in by_type
    )
    if (
        recommendation.get("full_regression", {}).get("required")
        is not expected_full_regression
    ):
        raise FailClosedRuntimeError(
            "IVE-0 full regression recommendation mismatch"
        )

    command_references = recommendation.get(
        "existing_allowlisted_command_references"
    )
    if not isinstance(command_references, list):
        raise FailClosedRuntimeError(
            "IVE-0 allowlisted command references must be a list"
        )
    if (
        analysis_strategy == "IVE_0_DIRECT_EXACT_PATH_DISCOVERY"
        and command_references
    ):
        raise FailClosedRuntimeError(
            "IVE-0 direct path discovery cannot invent command references"
        )
    expected_handoff = (
        "READY_FOR_EXISTING_G27_09_CANDIDATE_COMPOSITION"
        if command_references
        else "PLANNING_ONLY_NO_EXACT_ALLOWLIST_MAPPING"
    )
    if (
        recommendation.get("existing_validation_pipeline_handoff", {}).get(
            "status"
        )
        != expected_handoff
    ):
        raise FailClosedRuntimeError(
            "IVE-0 validation pipeline handoff status mismatch"
        )
    approval = recommendation.get("human_approval")
    if not isinstance(approval, dict) or approval != {
        "required_before_execution": True,
        "recorded_by_ive_0": False,
        "approval_status": "PENDING_DOWNSTREAM_CANDIDATE",
        "must_bind_exact_candidate_hash": True,
        "approval_authorizes_execution_by_itself": False,
    }:
        raise FailClosedRuntimeError(
            "IVE-0 recommendation Human Approval boundary mismatch"
        )
    if recommendation.get("recommendation_is_advisory") is not True:
        raise FailClosedRuntimeError("IVE-0 recommendation must remain advisory")
    if recommendation.get("validation_executed") is not False:
        raise FailClosedRuntimeError("IVE-0 recommendation cannot execute validation")


def _ive_hash(artifact: dict[str, Any]) -> str:
    keys = (
        "source_artifact_type",
        "normalized_change_reference",
        "normalized_change_hash",
        "normalized_change_artifact_hash",
        "analysis_strategy",
        "platform_change_impact_reference",
        "platform_change_impact_hash",
        "platform_change_impact_artifact_hash",
        "platform_change_impact_usage",
        "platform_validation_plan_reference",
        "platform_validation_plan_hash",
        "platform_validation_plan_artifact_hash",
        "platform_validation_plan_usage",
        "affected_components",
        "impact_classification",
        "validation_recommendation",
        "supporting_constitutional_reasoning",
        "analysis_status",
        "authority_flags",
        "failure_reason",
    )
    return replay_hash({key: deepcopy(artifact[key]) for key in keys})


def _capture(artifact: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "runtime_version": INTELLIGENT_VALIDATION_ENGINE_V0_RUNTIME_VERSION,
        "intelligent_validation_plan_artifact": deepcopy(artifact),
        "ive_analysis_id": artifact["ive_analysis_id"],
        "analysis_status": artifact["analysis_status"],
        "intelligent_validation_plan_hash": artifact[
            "intelligent_validation_plan_hash"
        ],
        "ive_replay_reference": str(replay_path),
        "affected_components": deepcopy(artifact["affected_components"]),
        "impact_classification": deepcopy(artifact["impact_classification"]),
        "validation_recommendation": deepcopy(
            artifact["validation_recommendation"]
        ),
        "fail_closed": artifact["analysis_status"] == FAILED_CLOSED,
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


def _persist_if_possible(replay_path: Path, artifact: dict[str, Any]) -> None:
    try:
        wrapper = {
            "replay_index": 0,
            "replay_step": REPLAY_STEP,
            "artifact": deepcopy(artifact),
        }
        wrapper["replay_hash"] = replay_hash(wrapper)
        write_json_immutable(
            replay_path / f"000_{REPLAY_STEP}.json",
            wrapper,
        )
    except Exception:
        return


def _ensure_replay_available(replay_path: Path) -> None:
    if (replay_path / f"000_{REPLAY_STEP}.json").exists():
        raise FailClosedRuntimeError(
            "IVE-0 failed closed: replay artifact already exists"
        )


def _artifact_value(artifact: dict[str, Any] | None, field: str) -> str:
    if isinstance(artifact, dict):
        return _safe_string(artifact.get(field))
    return "UNAVAILABLE"


def _artifact_hash_value(artifact: dict[str, Any] | None, field: str) -> str:
    if isinstance(artifact, dict):
        return _safe_hash(artifact.get(field))
    return replay_hash({"unavailable": field})


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
            f"IVE-0 failed closed: {field} must be a sha256 hash"
        )
    return text


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"IVE-0 failed closed: {field} is required")
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
    return f"IVE-0 failed closed: {exc}" if str(exc) else "IVE-0 failed closed"
