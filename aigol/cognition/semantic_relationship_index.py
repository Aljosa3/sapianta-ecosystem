"""Read-only bounded semantic relationship index.

The index maps explicit semantic relationships present in replay-visible
cognition artifacts. It does not reason, infer hidden relationships, complete
semantics, repair relationships, execute, dispatch, or activate providers.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

from aigol.cognition.semantic_context_state import build_semantic_context_state
from aigol.cognition.semantic_replay import build_semantic_replay_continuity_check
from aigol.cognition.state_envelope import GENERATED_AT, UNKNOWN, load_cognition_artifacts

ARTIFACT_TYPE = "BOUNDED_SEMANTIC_RELATIONSHIP_INDEX_V1"
VALIDATION_ARTIFACT_TYPE = "BOUNDED_SEMANTIC_RELATIONSHIP_INDEX_VALIDATION_V1"
SCHEMA_VERSION = "1.0"

RELATIONSHIP_INDEX_COMPLETE = "RELATIONSHIP_INDEX_COMPLETE"
RELATIONSHIP_INDEX_PARTIAL = "RELATIONSHIP_INDEX_PARTIAL"
UNKNOWN_INSUFFICIENT_EVIDENCE = "UNKNOWN_INSUFFICIENT_EVIDENCE"

RELATIONSHIP_CATEGORIES = (
    "intent_to_constraint",
    "intent_to_admissibility",
    "intent_to_authority_boundary",
    "constraint_to_governance_scope",
    "semantic_anchor_to_replay_identity",
    "semantic_boundary_to_lifecycle_phase",
    "ambiguity_to_unknown_context",
    "authority_boundary_to_execution_boundary",
    "semantic_context_to_continuity_check",
    "governance_semantics_to_integrity_summary",
)


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
    safe.pop("relationship_index_hash", None)
    return safe


def _artifact_hash(artifact: dict[str, Any]) -> str:
    hashes = artifact.get("hashes", {}) if isinstance(artifact.get("hashes"), dict) else {}
    for key in (
        "artifact_hash",
        "semantic_output_hash",
        "contract_candidate_hash",
        "decision_hash",
        "preview_hash",
        "approval_hash",
        "handoff_preview_hash",
        "dispatch_authorization_hash",
        "continuity_preview_hash",
        "semantic_context_hash",
        "semantic_replay_check_hash",
        "integrity_summary_hash",
    ):
        value = artifact.get(key, hashes.get(key))
        if isinstance(value, str) and value.strip():
            return value
    return UNKNOWN


def _source_refs(artifacts: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {"artifact_type": _artifact_type(artifact), "hash": _artifact_hash(artifact)}
        for artifact in artifacts
    ]


def _first_str(artifacts: list[dict[str, Any]], *fields: str) -> str:
    for artifact in artifacts:
        for field in fields:
            value = artifact.get(field)
            if isinstance(value, str) and value.strip():
                return value
    return UNKNOWN


def _values(artifacts: list[dict[str, Any]], *fields: str) -> list[Any]:
    found: list[Any] = []
    for artifact in artifacts:
        for field in fields:
            value = artifact.get(field)
            if value not in (None, "", UNKNOWN):
                found.append(deepcopy(value))
    return found


def _ambiguities(artifacts: list[dict[str, Any]]) -> list[str]:
    found: list[str] = []
    for artifact in artifacts:
        value = artifact.get("ambiguities")
        if isinstance(value, list):
            found.extend(str(item) for item in value)
        child = artifact.get("semantic_contract_candidate")
        if isinstance(child, dict) and isinstance(child.get("ambiguities"), list):
            found.extend(str(item) for item in child["ambiguities"])
    return sorted(set(found))


def _relationship(category: str, source: str, target: str, evidence: Any, known: bool) -> dict[str, Any]:
    return {
        "relationship_category": category,
        "source": source,
        "target": target,
        "evidence": deepcopy(evidence) if known else UNKNOWN,
        "known": known,
        "inferred": False,
        "semantic_truth_certified": False,
        "executable_graph_edge": False,
    }


def _relationships(artifacts: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    unknowns: list[str] = []
    intent = _first_str(artifacts, "normalized_intent", "semantic_intent", "human_request")
    constraints = _values(artifacts, "constraints")
    governance_scope_constraints = _values(artifacts, "constraints", "forbidden_operations")
    admissibility = _first_str(artifacts, "gate_status", "governance_status", "validation_status", "status")
    authority_boundaries = _values(artifacts, "authority_boundary")
    replay_identity = _first_str(artifacts, "replay_identity")
    execution_boundary = _first_str(artifacts, "execution_boundary_state", "execution_continuity_status", "execution_status")
    ambiguities = _ambiguities(artifacts)
    context_state = build_semantic_context_state(artifacts)
    continuity_check = build_semantic_replay_continuity_check(artifacts)

    relationships = [
        _relationship("intent_to_constraint", "intent", "constraints", {"intent": intent, "constraints": constraints}, intent != UNKNOWN and bool(constraints)),
        _relationship("intent_to_admissibility", "intent", "admissibility", {"intent": intent, "admissibility": admissibility}, intent != UNKNOWN and admissibility != UNKNOWN),
        _relationship("intent_to_authority_boundary", "intent", "authority_boundary", {"intent": intent, "authority_boundaries": authority_boundaries}, intent != UNKNOWN and bool(authority_boundaries)),
        _relationship("constraint_to_governance_scope", "constraints", "governance_scope", governance_scope_constraints, bool(governance_scope_constraints)),
        _relationship("semantic_anchor_to_replay_identity", "semantic_anchor", "replay_identity", {"intent": intent, "replay_identity": replay_identity}, intent != UNKNOWN and replay_identity != UNKNOWN),
        _relationship("semantic_boundary_to_lifecycle_phase", "semantic_boundaries", "semantic_continuity_phase", context_state.get("semantic_boundaries", []), bool(artifacts) and bool(context_state.get("semantic_boundaries"))),
        _relationship("ambiguity_to_unknown_context", "ambiguity", "unknown_context", ambiguities, bool(ambiguities)),
        _relationship("authority_boundary_to_execution_boundary", "authority_boundary", "execution_boundary", {"authority_boundaries": authority_boundaries, "execution_boundary": execution_boundary}, bool(authority_boundaries) and execution_boundary != UNKNOWN),
        _relationship("semantic_context_to_continuity_check", "semantic_context_state", "semantic_replay_continuity_check", {"semantic_context_hash": context_state.get("semantic_context_hash"), "semantic_replay_check_hash": continuity_check.get("semantic_replay_check_hash")}, bool(artifacts)),
        _relationship("governance_semantics_to_integrity_summary", "governance_semantics", "integrity_summary", {"admissibility": admissibility, "constraints": governance_scope_constraints}, admissibility != UNKNOWN or bool(governance_scope_constraints)),
    ]
    for relationship in relationships:
        if not relationship["known"]:
            unknowns.append(relationship["relationship_category"])
    return relationships, sorted(set(unknowns))


def build_semantic_relationship_index(
    artifacts: Any = None,
    *,
    generated_at: str = GENERATED_AT,
) -> dict[str, Any]:
    safe_artifacts = _as_artifacts(artifacts)
    relationships, relationship_unknowns = _relationships(safe_artifacts)
    unknowns = list(relationship_unknowns)
    if not safe_artifacts:
        unknowns.append("no semantic artifacts provided")
    known_count = len([item for item in relationships if item["known"]])
    status = (
        UNKNOWN_INSUFFICIENT_EVIDENCE
        if not safe_artifacts
        else RELATIONSHIP_INDEX_COMPLETE
        if known_count == len(relationships)
        else RELATIONSHIP_INDEX_PARTIAL
    )
    index = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "generated_at": str(generated_at),
        "relationship_index_status": status,
        "semantic_relationships": relationships,
        "relationship_categories": list(RELATIONSHIP_CATEGORIES),
        "source_artifact_refs": _source_refs(safe_artifacts),
        "continuity_refs": [
            item for item in relationships if item["relationship_category"] in {
                "semantic_anchor_to_replay_identity",
                "semantic_context_to_continuity_check",
            }
        ],
        "authority_refs": [
            item for item in relationships if item["relationship_category"] in {
                "intent_to_authority_boundary",
                "authority_boundary_to_execution_boundary",
            }
        ],
        "ambiguity_refs": [
            item for item in relationships if item["relationship_category"] == "ambiguity_to_unknown_context"
        ],
        "unknowns": sorted(set(unknowns)),
        "notes": [
            "read-only explicit semantic relationship index only",
            "no semantic reasoning or hidden relationship inference",
            "no executable graph semantics",
            "missing evidence becomes UNKNOWN",
        ],
        "read_only": True,
        "execution_authority_added": False,
        "orchestration_authority_added": False,
        "autonomous_cognition_added": False,
        "planning_authority_added": False,
        "runtime_activation_added": False,
        "provider_activation_added": False,
        "semantic_reasoning_added": False,
        "hidden_inference_added": False,
        "semantic_completion_added": False,
        "semantic_repair_added": False,
        "relationship_repair_added": False,
        "executable_graph_semantics_added": False,
    }
    index["relationship_index_hash"] = canonical_hash(_hash_input(index))
    return index


def validate_semantic_relationship_index(index: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if index.get("artifact_type") != ARTIFACT_TYPE:
        errors.append("invalid relationship index artifact_type")
    expected_hash = canonical_hash(_hash_input(index))
    if index.get("relationship_index_hash") != expected_hash:
        errors.append("relationship_index_hash mismatch")
    categories = {item.get("relationship_category") for item in index.get("semantic_relationships", [])}
    missing = set(RELATIONSHIP_CATEGORIES) - categories
    if missing:
        errors.append(f"missing relationship categories: {sorted(missing)}")
    for relationship in index.get("semantic_relationships", []):
        if relationship.get("inferred") is not False:
            errors.append("hidden relationship inference detected")
        if relationship.get("executable_graph_edge") is not False:
            errors.append("executable graph semantic edge detected")
    for key in (
        "execution_authority_added",
        "orchestration_authority_added",
        "provider_activation_added",
        "semantic_reasoning_added",
        "hidden_inference_added",
        "semantic_repair_added",
        "relationship_repair_added",
        "executable_graph_semantics_added",
    ):
        if index.get(key) is not False:
            errors.append(f"relationship index boundary violated: {key}")
    validation = {
        "artifact_type": VALIDATION_ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "generated_at": GENERATED_AT,
        "validation_status": "INVALID" if errors else "VALID",
        "relationship_index_hash": index.get("relationship_index_hash", UNKNOWN),
        "expected_relationship_index_hash": expected_hash,
        "errors": sorted(set(errors)),
        "read_only": True,
    }
    validation["validation_hash"] = canonical_hash({key: value for key, value in validation.items() if key != "validation_hash"})
    return validation


def write_semantic_relationship_index(index: dict[str, Any], output_path: str | Path) -> dict[str, Any]:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(index, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return {"written": True, "output_path": str(path)}


def inspect_semantic_relationships(
    *,
    input_path: str | Path | None = None,
    output_path: str | Path | None = None,
    artifacts: Any = None,
    validate: bool = False,
) -> dict[str, Any]:
    loaded = _as_artifacts(artifacts)
    if not loaded:
        loaded = load_cognition_artifacts(input_path)
    index = build_semantic_relationship_index(loaded)
    result = {
        "command": "aigol cognition semantic-relationships",
        "input_path": str(input_path or ""),
        "artifact_count": len(loaded),
        "semantic_relationship_index": index,
        "read_only": True,
        "execution_authority_added": False,
        "orchestration_authority_added": False,
        "provider_activation_added": False,
        "semantic_reasoning_added": False,
        "hidden_inference_added": False,
        "relationship_repair_added": False,
    }
    if validate:
        result["semantic_relationship_validation"] = validate_semantic_relationship_index(index)
    if output_path:
        result["output"] = write_semantic_relationship_index(index, output_path)
    return result


def render_semantic_relationship_summary(index: dict[str, Any]) -> str:
    relationship_lines = [
        f"  {item.get('relationship_category')}: {'KNOWN' if item.get('known') else 'UNKNOWN'}"
        for item in index.get("semantic_relationships", [])
    ]
    return "\n".join(
        [
            "Relationship Index Status",
            f"  {index.get('relationship_index_status')}",
            "Semantic Relationships",
            *(relationship_lines or ["  UNKNOWN"]),
            "Continuity Refs",
            f"  {len(index.get('continuity_refs', []))}",
            "Authority Refs",
            f"  {len(index.get('authority_refs', []))}",
            "Ambiguity Refs",
            f"  {len(index.get('ambiguity_refs', []))}",
            "Unknowns",
            f"  {json.dumps(index.get('unknowns', []), sort_keys=True)}",
            "Governance Guarantees",
            "  semantic_reasoning: false",
            "  hidden_inference: false",
            "  execution_authority: false",
            "  provider_activation: false",
            "  executable_graph_semantics: false",
        ]
    )


__all__ = [
    "ARTIFACT_TYPE",
    "RELATIONSHIP_CATEGORIES",
    "RELATIONSHIP_INDEX_COMPLETE",
    "RELATIONSHIP_INDEX_PARTIAL",
    "UNKNOWN_INSUFFICIENT_EVIDENCE",
    "build_semantic_relationship_index",
    "inspect_semantic_relationships",
    "render_semantic_relationship_summary",
    "validate_semantic_relationship_index",
    "write_semantic_relationship_index",
]
