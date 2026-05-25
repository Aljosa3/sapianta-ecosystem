"""Read-only deterministic semantic context diff.

The diff compares explicit semantic context fields between two artifact sets.
It does not reason, infer hidden meaning, repair semantics, resolve ambiguity,
execute, dispatch, activate providers, or create executable semantic flows.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

from aigol.cognition.semantic_context_state import build_semantic_context_state
from aigol.cognition.state_envelope import GENERATED_AT, UNKNOWN, load_cognition_artifacts

ARTIFACT_TYPE = "SEMANTIC_CONTEXT_DIFF_V1"
VALIDATION_ARTIFACT_TYPE = "SEMANTIC_CONTEXT_DIFF_VALIDATION_V1"
SCHEMA_VERSION = "1.0"

NO_CHANGE = "NO_CHANGE"
CHANGE_DETECTED = "CHANGE_DETECTED"
UNKNOWN_STATUS = "UNKNOWN"
BOUNDARY_DRIFT_RISK = "BOUNDARY_DRIFT_RISK"
CONTINUITY_DELTA = "CONTINUITY_DELTA"
INVALID_DIFF_INPUT = "INVALID_DIFF_INPUT"

DIFF_TYPES = (
    "semantic_constraint_added",
    "semantic_constraint_removed",
    "semantic_boundary_changed",
    "ambiguity_state_changed",
    "continuity_anchor_changed",
    "authority_boundary_changed",
    "governance_scope_changed",
    "replay_continuity_changed",
    "admissibility_boundary_changed",
    "unknown_delta",
)


def _as_artifacts(artifacts: Any) -> list[dict[str, Any]]:
    if artifacts is None:
        return []
    if isinstance(artifacts, dict):
        return [artifacts]
    if isinstance(artifacts, list):
        return [item for item in artifacts if isinstance(item, dict)]
    return []


def _hash_input(value: dict[str, Any]) -> dict[str, Any]:
    safe = deepcopy(value)
    safe.pop("diff_hash", None)
    return safe


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _set_values(values: list[Any]) -> set[str]:
    return {_canonical(value) for value in values}


def _decode_values(values: set[str]) -> list[Any]:
    return [json.loads(value) for value in sorted(values)]


def _anchor_map(context: dict[str, Any]) -> dict[str, Any]:
    anchors: dict[str, Any] = {}
    for anchor in context.get("semantic_continuity_anchors", []):
        if isinstance(anchor, dict):
            anchors[str(anchor.get("anchor_name", UNKNOWN))] = deepcopy(anchor.get("value", UNKNOWN))
    return anchors


def _boundary_map(context: dict[str, Any]) -> dict[str, Any]:
    boundaries: dict[str, Any] = {}
    for boundary in context.get("semantic_boundaries", []):
        if isinstance(boundary, dict):
            boundaries[str(boundary.get("boundary_name", UNKNOWN))] = deepcopy(boundary)
    return boundaries


def _constraint_values(context: dict[str, Any]) -> list[Any]:
    values: list[Any] = []
    for constraint in context.get("semantic_constraints", []):
        if isinstance(constraint, dict):
            values.append(constraint.get("values", UNKNOWN))
    return values


def _delta(diff_type: str, source: Any, target: Any, changed: bool) -> dict[str, Any]:
    return {
        "diff_type": diff_type,
        "source": deepcopy(source),
        "target": deepcopy(target),
        "changed": changed,
        "inferred": False,
        "semantic_reasoning_performed": False,
        "semantic_repair_performed": False,
    }


def _context_ref(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_type": context.get("artifact_type", UNKNOWN),
        "semantic_context_hash": context.get("semantic_context_hash", UNKNOWN),
        "semantic_context_status": context.get("semantic_context_status", UNKNOWN),
    }


def _diff_status(
    *,
    source_context: dict[str, Any],
    target_context: dict[str, Any],
    boundary_changed: bool,
    continuity_changed: bool,
    any_changed: bool,
) -> str:
    if source_context.get("semantic_context_status") == "UNKNOWN_INSUFFICIENT_EVIDENCE" or target_context.get("semantic_context_status") == "UNKNOWN_INSUFFICIENT_EVIDENCE":
        return UNKNOWN_STATUS
    if boundary_changed:
        return BOUNDARY_DRIFT_RISK
    if continuity_changed:
        return CONTINUITY_DELTA
    if any_changed:
        return CHANGE_DETECTED
    return NO_CHANGE


def build_semantic_context_diff(
    source_artifacts: Any = None,
    target_artifacts: Any = None,
    *,
    generated_at: str = GENERATED_AT,
) -> dict[str, Any]:
    source_items = _as_artifacts(source_artifacts)
    target_items = _as_artifacts(target_artifacts)
    source_context = build_semantic_context_state(source_items)
    target_context = build_semantic_context_state(target_items)

    source_constraints = _set_values(_constraint_values(source_context))
    target_constraints = _set_values(_constraint_values(target_context))
    added_constraints = _decode_values(target_constraints - source_constraints)
    removed_constraints = _decode_values(source_constraints - target_constraints)

    source_anchors = _anchor_map(source_context)
    target_anchors = _anchor_map(target_context)
    all_anchor_names = sorted(set(source_anchors) | set(target_anchors))
    unchanged_anchors = [
        {"anchor_name": name, "value": source_anchors[name]}
        for name in all_anchor_names
        if source_anchors.get(name, UNKNOWN) == target_anchors.get(name, UNKNOWN)
    ]
    anchor_deltas = [
        _delta("continuity_anchor_changed", source_anchors.get(name, UNKNOWN), target_anchors.get(name, UNKNOWN), True)
        for name in all_anchor_names
        if source_anchors.get(name, UNKNOWN) != target_anchors.get(name, UNKNOWN)
    ]

    source_boundaries = _boundary_map(source_context)
    target_boundaries = _boundary_map(target_context)
    all_boundary_names = sorted(set(source_boundaries) | set(target_boundaries))
    boundary_deltas = [
        _delta("semantic_boundary_changed", source_boundaries.get(name, UNKNOWN), target_boundaries.get(name, UNKNOWN), True)
        for name in all_boundary_names
        if source_boundaries.get(name, UNKNOWN) != target_boundaries.get(name, UNKNOWN)
    ]

    ambiguity_delta = _delta(
        "ambiguity_state_changed",
        source_context.get("ambiguity_state", {}),
        target_context.get("ambiguity_state", {}),
        source_context.get("ambiguity_state", {}) != target_context.get("ambiguity_state", {}),
    )
    authority_delta = _delta(
        "authority_boundary_changed",
        source_context.get("governance_relevance", {}).get("has_authority_boundary", UNKNOWN),
        target_context.get("governance_relevance", {}).get("has_authority_boundary", UNKNOWN),
        source_context.get("governance_relevance", {}).get("has_authority_boundary", UNKNOWN)
        != target_context.get("governance_relevance", {}).get("has_authority_boundary", UNKNOWN),
    )
    replay_delta = _delta(
        "replay_continuity_changed",
        source_context.get("governance_relevance", {}).get("has_replay_identity", UNKNOWN),
        target_context.get("governance_relevance", {}).get("has_replay_identity", UNKNOWN),
        source_context.get("governance_relevance", {}).get("has_replay_identity", UNKNOWN)
        != target_context.get("governance_relevance", {}).get("has_replay_identity", UNKNOWN),
    )
    admissibility_delta = _delta(
        "admissibility_boundary_changed",
        source_context.get("governance_relevance", {}).get("has_admissibility_signal", UNKNOWN),
        target_context.get("governance_relevance", {}).get("has_admissibility_signal", UNKNOWN),
        source_context.get("governance_relevance", {}).get("has_admissibility_signal", UNKNOWN)
        != target_context.get("governance_relevance", {}).get("has_admissibility_signal", UNKNOWN),
    )
    governance_scope_delta = _delta(
        "governance_scope_changed",
        source_context.get("governance_relevance", {}).get("has_constraints", UNKNOWN),
        target_context.get("governance_relevance", {}).get("has_constraints", UNKNOWN),
        source_context.get("governance_relevance", {}).get("has_constraints", UNKNOWN)
        != target_context.get("governance_relevance", {}).get("has_constraints", UNKNOWN),
    )
    boundary_signal_deltas = [
        delta for delta in (authority_delta, governance_scope_delta, admissibility_delta)
        if delta["changed"]
    ]
    boundary_deltas.extend(boundary_signal_deltas)

    semantic_deltas = [
        _delta("semantic_constraint_added", [], added_constraints, bool(added_constraints)),
        _delta("semantic_constraint_removed", removed_constraints, [], bool(removed_constraints)),
        *anchor_deltas,
    ]
    continuity_deltas = [replay_delta, *anchor_deltas]
    ambiguity_deltas = [ambiguity_delta]
    authority_deltas = [authority_delta]
    all_deltas = semantic_deltas + boundary_deltas + continuity_deltas + ambiguity_deltas + authority_deltas + [governance_scope_delta, admissibility_delta]
    any_changed = any(delta["changed"] for delta in all_deltas)
    boundary_changed = bool(boundary_deltas or authority_delta["changed"] or governance_scope_delta["changed"] or admissibility_delta["changed"])
    continuity_changed = bool(replay_delta["changed"] or anchor_deltas)
    unknowns = []
    if not source_items:
        unknowns.append("source_artifacts")
    if not target_items:
        unknowns.append("target_artifacts")
    for unknown in source_context.get("unknowns", []):
        unknowns.append(f"source.{unknown}")
    for unknown in target_context.get("unknowns", []):
        unknowns.append(f"target.{unknown}")

    diff = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "generated_at": str(generated_at),
        "diff_status": _diff_status(
            source_context=source_context,
            target_context=target_context,
            boundary_changed=boundary_changed,
            continuity_changed=continuity_changed,
            any_changed=any_changed,
        ),
        "source_context_ref": _context_ref(source_context),
        "target_context_ref": _context_ref(target_context),
        "semantic_deltas": semantic_deltas,
        "boundary_deltas": boundary_deltas,
        "continuity_deltas": continuity_deltas,
        "ambiguity_deltas": ambiguity_deltas,
        "authority_deltas": authority_deltas,
        "added_constraints": added_constraints,
        "removed_constraints": removed_constraints,
        "unchanged_anchors": unchanged_anchors,
        "unknowns": sorted(set(unknowns)),
        "notes": [
            "read-only semantic context diff only",
            "explicit artifact fields only",
            "no hidden semantic inference",
            "no semantic reasoning, repair, optimization, or ambiguity resolution",
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
        "ambiguity_resolution_added": False,
        "semantic_optimization_added": False,
        "autonomous_semantic_evolution_added": False,
        "executable_semantic_graph_semantics_added": False,
    }
    diff["diff_hash"] = canonical_hash(_hash_input(diff))
    return diff


def validate_semantic_context_diff(diff: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if diff.get("artifact_type") != ARTIFACT_TYPE:
        errors.append("invalid semantic context diff artifact_type")
    expected_hash = canonical_hash(_hash_input(diff))
    if diff.get("diff_hash") != expected_hash:
        errors.append("diff_hash mismatch")
    for section in ("semantic_deltas", "boundary_deltas", "continuity_deltas", "ambiguity_deltas", "authority_deltas"):
        for delta in diff.get(section, []):
            if delta.get("inferred") is not False:
                errors.append(f"hidden inference detected in {section}")
            if delta.get("semantic_reasoning_performed") is not False:
                errors.append(f"semantic reasoning detected in {section}")
            if delta.get("semantic_repair_performed") is not False:
                errors.append(f"semantic repair detected in {section}")
    for key in (
        "execution_authority_added",
        "orchestration_authority_added",
        "provider_activation_added",
        "semantic_reasoning_added",
        "hidden_inference_added",
        "semantic_repair_added",
        "ambiguity_resolution_added",
        "executable_semantic_graph_semantics_added",
    ):
        if diff.get(key) is not False:
            errors.append(f"semantic context diff boundary violated: {key}")
    validation = {
        "artifact_type": VALIDATION_ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "generated_at": GENERATED_AT,
        "validation_status": "INVALID" if errors else "VALID",
        "diff_hash": diff.get("diff_hash", UNKNOWN),
        "expected_diff_hash": expected_hash,
        "errors": sorted(set(errors)),
        "read_only": True,
    }
    validation["validation_hash"] = canonical_hash({key: value for key, value in validation.items() if key != "validation_hash"})
    return validation


def write_semantic_context_diff(diff: dict[str, Any], output_path: str | Path) -> dict[str, Any]:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(diff, sort_keys=True, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return {"written": True, "output_path": str(path)}


def inspect_semantic_diff(
    *,
    source_path: str | Path | None = None,
    target_path: str | Path | None = None,
    output_path: str | Path | None = None,
    source_artifacts: Any = None,
    target_artifacts: Any = None,
    validate: bool = False,
) -> dict[str, Any]:
    source_loaded = _as_artifacts(source_artifacts) or load_cognition_artifacts(source_path)
    target_loaded = _as_artifacts(target_artifacts) or load_cognition_artifacts(target_path)
    diff = build_semantic_context_diff(source_loaded, target_loaded)
    result = {
        "command": "aigol cognition semantic-diff",
        "source_path": str(source_path or ""),
        "target_path": str(target_path or ""),
        "source_artifact_count": len(source_loaded),
        "target_artifact_count": len(target_loaded),
        "semantic_context_diff": diff,
        "read_only": True,
        "execution_authority_added": False,
        "orchestration_authority_added": False,
        "provider_activation_added": False,
        "semantic_reasoning_added": False,
        "hidden_inference_added": False,
        "semantic_repair_added": False,
        "ambiguity_resolution_added": False,
    }
    if validate:
        result["semantic_diff_validation"] = validate_semantic_context_diff(diff)
    if output_path:
        result["output"] = write_semantic_context_diff(diff, output_path)
    return result


def render_semantic_diff_summary(diff: dict[str, Any]) -> str:
    return "\n".join(
        [
            "Semantic Diff Status",
            f"  {diff.get('diff_status')}",
            "Semantic Deltas",
            f"  {len([item for item in diff.get('semantic_deltas', []) if item.get('changed')])} changed",
            "Boundary Deltas",
            f"  {len(diff.get('boundary_deltas', []))} changed",
            "Continuity Deltas",
            f"  {len([item for item in diff.get('continuity_deltas', []) if item.get('changed')])} changed",
            "Ambiguity Deltas",
            f"  {len([item for item in diff.get('ambiguity_deltas', []) if item.get('changed')])} changed",
            "Authority Deltas",
            f"  {len([item for item in diff.get('authority_deltas', []) if item.get('changed')])} changed",
            "Added Constraints",
            f"  {json.dumps(diff.get('added_constraints', []), sort_keys=True)}",
            "Removed Constraints",
            f"  {json.dumps(diff.get('removed_constraints', []), sort_keys=True)}",
            "Unchanged Anchors",
            f"  {len(diff.get('unchanged_anchors', []))}",
            "Unknowns",
            f"  {json.dumps(diff.get('unknowns', []), sort_keys=True)}",
            "Governance Guarantees",
            "  semantic_reasoning: false",
            "  hidden_inference: false",
            "  execution_authority: false",
            "  provider_activation: false",
            "  ambiguity_resolution: false",
        ]
    )


__all__ = [
    "ARTIFACT_TYPE",
    "BOUNDARY_DRIFT_RISK",
    "CHANGE_DETECTED",
    "CONTINUITY_DELTA",
    "INVALID_DIFF_INPUT",
    "NO_CHANGE",
    "UNKNOWN_STATUS",
    "build_semantic_context_diff",
    "inspect_semantic_diff",
    "render_semantic_diff_summary",
    "validate_semantic_context_diff",
    "write_semantic_context_diff",
]
