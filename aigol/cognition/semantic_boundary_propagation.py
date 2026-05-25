"""Read-only semantic boundary propagation visibility.

The propagation model tracks explicit semantic boundary continuity across
replay-visible cognition artifacts. It does not reason, infer hidden meaning,
repair semantics, enforce runtime behavior, execute, dispatch, or activate
providers.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

from aigol.cognition.semantic_context_state import build_semantic_context_state
from aigol.cognition.semantic_relationship_index import build_semantic_relationship_index
from aigol.cognition.state_envelope import GENERATED_AT, UNKNOWN, load_cognition_artifacts

ARTIFACT_TYPE = "SEMANTIC_BOUNDARY_PROPAGATION_V1"
VALIDATION_ARTIFACT_TYPE = "SEMANTIC_BOUNDARY_PROPAGATION_VALIDATION_V1"
SCHEMA_VERSION = "1.0"

STABLE = "STABLE"
STABLE_WITH_WARNINGS = "STABLE_WITH_WARNINGS"
UNKNOWN_STATUS = "UNKNOWN"
PROPAGATION_DRIFT_RISK = "PROPAGATION_DRIFT_RISK"
BOUNDARY_DISCONTINUITY = "BOUNDARY_DISCONTINUITY"
INVALID_PROPAGATION_CHAIN = "INVALID_PROPAGATION_CHAIN"

BOUNDARY_TYPES = (
    "authority_semantic_boundary",
    "execution_semantic_boundary",
    "governance_scope_boundary",
    "admissibility_boundary",
    "replay_continuity_boundary",
    "lifecycle_transition_boundary",
    "integrity_boundary",
    "ambiguity_boundary",
)

BOUNDARY_TO_CONTEXT_NAME = {
    "authority_semantic_boundary": "authority semantic boundaries",
    "execution_semantic_boundary": "execution semantic boundaries",
    "governance_scope_boundary": "governance scope boundaries",
    "admissibility_boundary": "admissibility semantic boundaries",
    "replay_continuity_boundary": "replay continuity boundaries",
}

BOUNDARY_TO_RELATIONSHIP = {
    "authority_semantic_boundary": "intent_to_authority_boundary",
    "execution_semantic_boundary": "authority_boundary_to_execution_boundary",
    "governance_scope_boundary": "constraint_to_governance_scope",
    "admissibility_boundary": "intent_to_admissibility",
    "replay_continuity_boundary": "semantic_anchor_to_replay_identity",
    "lifecycle_transition_boundary": "semantic_boundary_to_lifecycle_phase",
    "integrity_boundary": "governance_semantics_to_integrity_summary",
    "ambiguity_boundary": "ambiguity_to_unknown_context",
}


def _as_artifacts(artifacts: Any) -> list[dict[str, Any]]:
    if artifacts is None:
        return []
    if isinstance(artifacts, dict):
        return [artifacts]
    if isinstance(artifacts, list):
        return [item for item in artifacts if isinstance(item, dict)]
    return []


def _artifact_type(artifact: dict[str, Any]) -> str:
    return str(artifact.get("artifact_type") or artifact.get("gate_type") or UNKNOWN)


def _hash_input(value: dict[str, Any]) -> dict[str, Any]:
    safe = deepcopy(value)
    safe.pop("propagation_hash", None)
    return safe


def _artifact_hash(artifact: dict[str, Any]) -> str:
    hashes = artifact.get("hashes", {}) if isinstance(artifact.get("hashes"), dict) else {}
    for key in (
        "artifact_hash",
        "preview_hash",
        "approval_hash",
        "handoff_preview_hash",
        "dispatch_authorization_hash",
        "continuity_preview_hash",
        "semantic_context_hash",
        "relationship_index_hash",
    ):
        value = artifact.get(key, hashes.get(key))
        if isinstance(value, str) and value.strip():
            return value
    return UNKNOWN


def _refs(artifacts: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [{"artifact_type": _artifact_type(artifact), "hash": _artifact_hash(artifact)} for artifact in artifacts]


def _relationship_by_category(index: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("relationship_category")): item
        for item in index.get("semantic_relationships", [])
        if isinstance(item, dict)
    }


def _explicit_drift_findings(artifacts: list[dict[str, Any]]) -> list[str]:
    findings: list[str] = []
    for artifact in artifacts:
        artifact_type = _artifact_type(artifact)
        if artifact.get("execution_authority") is True or artifact.get("execution_authorized") is True:
            findings.append(f"{artifact_type} crosses execution semantic boundary")
        if artifact.get("provider_invoked") is True and artifact_type != "CONTROLLED_EXECUTION_HANDOFF_V1":
            findings.append(f"{artifact_type} crosses provider semantic boundary")
        if artifact.get("mutation_authority") is True:
            findings.append(f"{artifact_type} crosses mutation semantic boundary")
        if artifact.get("semantic_reasoning_added") is True or artifact.get("hidden_semantic_inference_added") is True:
            findings.append(f"{artifact_type} expands semantic interpretation boundary")
    return sorted(set(findings))


def _semantic_boundaries(
    context_state: dict[str, Any],
    relationship_index: dict[str, Any],
    *,
    has_artifacts: bool,
) -> tuple[list[dict[str, Any]], list[str]]:
    relationships = _relationship_by_category(relationship_index)
    context_names = {
        str(item.get("boundary_name"))
        for item in context_state.get("semantic_boundaries", [])
        if isinstance(item, dict)
    }
    unknowns: list[str] = []
    boundaries: list[dict[str, Any]] = []
    for boundary_type in BOUNDARY_TYPES:
        relationship = relationships.get(BOUNDARY_TO_RELATIONSHIP[boundary_type], {})
        context_name = BOUNDARY_TO_CONTEXT_NAME.get(boundary_type)
        explicit_context = has_artifacts and (context_name in context_names if context_name else bool(relationship.get("known")))
        explicit_relationship = relationship.get("known") is True
        known = explicit_context or explicit_relationship
        if not known:
            unknowns.append(boundary_type)
        boundaries.append(
            {
                "boundary_type": boundary_type,
                "explicit_context_boundary": explicit_context,
                "explicit_relationship_boundary": explicit_relationship,
                "known": known,
                "inferred": False,
                "runtime_enforcement_added": False,
                "semantic_expansion_performed": False,
            }
        )
    return boundaries, unknowns


def _propagation_paths(boundaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "path_name": "semantic_context_to_relationship_index",
            "source": "SEMANTIC_CONTEXT_STATE_V1",
            "target": "BOUNDED_SEMANTIC_RELATIONSHIP_INDEX_V1",
            "boundary_types": [item["boundary_type"] for item in boundaries if item["known"]],
            "propagation_explicit": any(item["known"] for item in boundaries),
            "inferred": False,
            "executable_semantic_flow": False,
        },
        {
            "path_name": "relationship_index_to_lifecycle_visibility",
            "source": "BOUNDED_SEMANTIC_RELATIONSHIP_INDEX_V1",
            "target": "COGNITION_LIFECYCLE_MODEL_V1",
            "boundary_types": ["lifecycle_transition_boundary"],
            "propagation_explicit": any(item["boundary_type"] == "lifecycle_transition_boundary" and item["known"] for item in boundaries),
            "inferred": False,
            "executable_semantic_flow": False,
        },
        {
            "path_name": "authority_boundary_to_execution_boundary",
            "source": "authority_semantic_boundary",
            "target": "execution_semantic_boundary",
            "boundary_types": ["authority_semantic_boundary", "execution_semantic_boundary"],
            "propagation_explicit": all(
                any(item["boundary_type"] == boundary_type and item["known"] for item in boundaries)
                for boundary_type in ("authority_semantic_boundary", "execution_semantic_boundary")
            ),
            "inferred": False,
            "executable_semantic_flow": False,
        },
    ]


def _status(artifacts: list[dict[str, Any]], unknowns: list[str], drift_findings: list[str]) -> str:
    if drift_findings:
        return PROPAGATION_DRIFT_RISK
    if not artifacts:
        return UNKNOWN_STATUS
    if len(unknowns) == len(BOUNDARY_TYPES):
        return BOUNDARY_DISCONTINUITY
    if unknowns:
        return STABLE_WITH_WARNINGS
    return STABLE


def build_semantic_boundary_propagation(
    artifacts: Any = None,
    *,
    generated_at: str = GENERATED_AT,
) -> dict[str, Any]:
    safe_artifacts = _as_artifacts(artifacts)
    context_state = build_semantic_context_state(safe_artifacts)
    relationship_index = build_semantic_relationship_index(safe_artifacts)
    boundaries, boundary_unknowns = _semantic_boundaries(
        context_state,
        relationship_index,
        has_artifacts=bool(safe_artifacts),
    )
    drift_findings = _explicit_drift_findings(safe_artifacts)
    unknowns = list(boundary_unknowns)
    if not safe_artifacts:
        unknowns.append("no semantic boundary artifacts provided")
    status = _status(safe_artifacts, sorted(set(unknowns)), drift_findings)
    propagation = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "generated_at": str(generated_at),
        "propagation_status": status,
        "semantic_boundaries": boundaries,
        "propagation_paths": _propagation_paths(boundaries),
        "propagation_constraints": [
            "explicit boundary fields only",
            "UNKNOWN for missing propagation evidence",
            "no hidden semantic inference",
            "no semantic expansion",
            "no semantic optimization",
            "no runtime enforcement semantics",
        ],
        "continuity_refs": relationship_index.get("continuity_refs", []),
        "lifecycle_refs": [
            item for item in relationship_index.get("semantic_relationships", [])
            if item.get("relationship_category") == "semantic_boundary_to_lifecycle_phase"
        ],
        "authority_refs": relationship_index.get("authority_refs", []),
        "ambiguity_refs": relationship_index.get("ambiguity_refs", []),
        "stability_assessment": {
            "status": status,
            "drift_findings": drift_findings,
            "known_boundary_count": len([item for item in boundaries if item["known"]]),
            "unknown_boundary_count": len([item for item in boundaries if not item["known"]]),
            "hidden_semantic_expansion_detected": bool(drift_findings),
        },
        "source_artifact_refs": _refs(safe_artifacts),
        "unknowns": sorted(set(unknowns)),
        "notes": [
            "read-only semantic boundary propagation visibility only",
            "no semantic reasoning or hidden inference",
            "no executable semantic propagation",
            "no runtime enforcement semantics",
        ],
        "read_only": True,
        "execution_authority_added": False,
        "orchestration_authority_added": False,
        "planning_authority_added": False,
        "runtime_activation_added": False,
        "provider_routing_added": False,
        "provider_activation_added": False,
        "semantic_reasoning_added": False,
        "hidden_inference_added": False,
        "semantic_repair_added": False,
        "autonomous_semantic_propagation_added": False,
        "executable_semantic_graphs_added": False,
        "dynamic_semantic_evolution_added": False,
    }
    propagation["propagation_hash"] = canonical_hash(_hash_input(propagation))
    return propagation


def validate_semantic_boundary_propagation(propagation: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if propagation.get("artifact_type") != ARTIFACT_TYPE:
        errors.append("invalid semantic boundary propagation artifact_type")
    expected_hash = canonical_hash(_hash_input(propagation))
    if propagation.get("propagation_hash") != expected_hash:
        errors.append("propagation_hash mismatch")
    boundary_types = {item.get("boundary_type") for item in propagation.get("semantic_boundaries", [])}
    missing = set(BOUNDARY_TYPES) - boundary_types
    if missing:
        errors.append(f"missing semantic boundary types: {sorted(missing)}")
    for path in propagation.get("propagation_paths", []):
        if path.get("inferred") is not False:
            errors.append("hidden propagation inference detected")
        if path.get("executable_semantic_flow") is not False:
            errors.append("executable semantic flow detected")
    for key in (
        "execution_authority_added",
        "orchestration_authority_added",
        "runtime_activation_added",
        "provider_activation_added",
        "semantic_reasoning_added",
        "hidden_inference_added",
        "semantic_repair_added",
        "executable_semantic_graphs_added",
    ):
        if propagation.get(key) is not False:
            errors.append(f"semantic boundary propagation boundary violated: {key}")
    validation = {
        "artifact_type": VALIDATION_ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "generated_at": GENERATED_AT,
        "validation_status": "INVALID" if errors else "VALID",
        "propagation_hash": propagation.get("propagation_hash", UNKNOWN),
        "expected_propagation_hash": expected_hash,
        "errors": sorted(set(errors)),
        "read_only": True,
    }
    validation["validation_hash"] = canonical_hash({key: value for key, value in validation.items() if key != "validation_hash"})
    return validation


def write_semantic_boundary_propagation(propagation: dict[str, Any], output_path: str | Path) -> dict[str, Any]:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(propagation, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return {"written": True, "output_path": str(path)}


def inspect_semantic_boundaries(
    *,
    input_path: str | Path | None = None,
    output_path: str | Path | None = None,
    artifacts: Any = None,
    validate: bool = False,
) -> dict[str, Any]:
    loaded = _as_artifacts(artifacts)
    if not loaded:
        loaded = load_cognition_artifacts(input_path)
    propagation = build_semantic_boundary_propagation(loaded)
    result = {
        "command": "aigol cognition semantic-boundaries",
        "input_path": str(input_path or ""),
        "artifact_count": len(loaded),
        "semantic_boundary_propagation": propagation,
        "read_only": True,
        "execution_authority_added": False,
        "orchestration_authority_added": False,
        "provider_activation_added": False,
        "semantic_reasoning_added": False,
        "hidden_inference_added": False,
        "semantic_repair_added": False,
        "executable_semantic_graphs_added": False,
    }
    if validate:
        result["semantic_boundary_validation"] = validate_semantic_boundary_propagation(propagation)
    if output_path:
        result["output"] = write_semantic_boundary_propagation(propagation, output_path)
    return result


def render_semantic_boundary_summary(propagation: dict[str, Any]) -> str:
    boundary_lines = [
        f"  {item.get('boundary_type')}: {'KNOWN' if item.get('known') else 'UNKNOWN'}"
        for item in propagation.get("semantic_boundaries", [])
    ]
    path_lines = [
        f"  {item.get('path_name')}: explicit={item.get('propagation_explicit')}"
        for item in propagation.get("propagation_paths", [])
    ]
    return "\n".join(
        [
            "Propagation Status",
            f"  {propagation.get('propagation_status')}",
            "Semantic Boundaries",
            *(boundary_lines or ["  UNKNOWN"]),
            "Propagation Paths",
            *(path_lines or ["  UNKNOWN"]),
            "Stability Assessment",
            f"  {json.dumps(propagation.get('stability_assessment', {}), sort_keys=True)}",
            "Unknowns",
            f"  {json.dumps(propagation.get('unknowns', []), sort_keys=True)}",
            "Governance Guarantees",
            "  semantic_reasoning: false",
            "  hidden_inference: false",
            "  execution_authority: false",
            "  provider_activation: false",
            "  executable_semantic_graphs: false",
        ]
    )


__all__ = [
    "ARTIFACT_TYPE",
    "BOUNDARY_TYPES",
    "BOUNDARY_DISCONTINUITY",
    "INVALID_PROPAGATION_CHAIN",
    "PROPAGATION_DRIFT_RISK",
    "STABLE",
    "STABLE_WITH_WARNINGS",
    "UNKNOWN_STATUS",
    "build_semantic_boundary_propagation",
    "inspect_semantic_boundaries",
    "render_semantic_boundary_summary",
    "validate_semantic_boundary_propagation",
    "write_semantic_boundary_propagation",
]
