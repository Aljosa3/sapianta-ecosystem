"""Bounded semantic context state visibility.

This module preserves governance-relevant semantic context from explicit
replay-visible artifacts. It does not reason, infer hidden intent, resolve
ambiguity, repair semantics, evolve context, execute, dispatch, or grant
authority.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

from aigol.cognition.state_envelope import GENERATED_AT, UNKNOWN, load_cognition_artifacts

ARTIFACT_TYPE = "SEMANTIC_CONTEXT_STATE_V1"
VALIDATION_ARTIFACT_TYPE = "SEMANTIC_CONTEXT_STATE_VALIDATION_V1"
SCHEMA_VERSION = "1.0"

SEMANTIC_CONTEXT_STABLE = "SEMANTIC_CONTEXT_STABLE"
SEMANTIC_CONTEXT_PARTIAL = "SEMANTIC_CONTEXT_PARTIAL"
UNKNOWN_INSUFFICIENT_EVIDENCE = "UNKNOWN_INSUFFICIENT_EVIDENCE"

AMBIGUITY_LOW = "LOW"
AMBIGUITY_MODERATE = "MODERATE"
AMBIGUITY_HIGH = "HIGH"
AMBIGUITY_UNKNOWN = "UNKNOWN"


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
    safe.pop("semantic_context_hash", None)
    return safe


def _first_str(artifacts: list[dict[str, Any]], *fields: str) -> str:
    for artifact in artifacts:
        for field in fields:
            value = artifact.get(field)
            if isinstance(value, str) and value.strip():
                return value
    return UNKNOWN


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
        "execution_governance_hash",
        "governed_return_hash",
    ):
        value = artifact.get(key, hashes.get(key))
        if isinstance(value, str) and value.strip():
            return value
    return UNKNOWN


def _evidence_refs(artifacts: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {
            "artifact_type": _artifact_type(artifact),
            "hash": _artifact_hash(artifact),
            "replay_identity": str(artifact.get("replay_identity", UNKNOWN)),
        }
        for artifact in artifacts
    ]


def _collect_constraints(artifacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    constraints: list[dict[str, Any]] = []
    for artifact in artifacts:
        artifact_type = _artifact_type(artifact)
        for field in ("constraints", "forbidden_operations"):
            value = artifact.get(field)
            if isinstance(value, list):
                constraints.append({"source": artifact_type, "field": field, "values": deepcopy(value)})
            elif isinstance(value, dict):
                constraints.append({"source": artifact_type, "field": field, "values": deepcopy(value)})
        boundary = artifact.get("authority_boundary")
        if isinstance(boundary, dict):
            constraints.append({"source": artifact_type, "field": "authority_boundary", "values": deepcopy(boundary)})
    return constraints


def _collect_ambiguities(artifacts: list[dict[str, Any]]) -> list[str]:
    ambiguities: list[str] = []
    for artifact in artifacts:
        value = artifact.get("ambiguities")
        if isinstance(value, list):
            ambiguities.extend(str(item) for item in value)
        child = artifact.get("semantic_contract_candidate")
        if isinstance(child, dict) and isinstance(child.get("ambiguities"), list):
            ambiguities.extend(str(item) for item in child["ambiguities"])
    return sorted(set(ambiguities))


def _ambiguity_state(artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    ambiguities = _collect_ambiguities(artifacts)
    if not artifacts or not ambiguities:
        return {
            "status": AMBIGUITY_UNKNOWN if not artifacts else AMBIGUITY_LOW,
            "ambiguities": ambiguities,
            "resolved_by_context_state": False,
        }
    blocking = [item for item in ambiguities if item != "NO_BLOCKING_AMBIGUITY_DETECTED"]
    if not blocking:
        status = AMBIGUITY_LOW
    elif len(blocking) <= 2:
        status = AMBIGUITY_MODERATE
    else:
        status = AMBIGUITY_HIGH
    return {"status": status, "ambiguities": ambiguities, "resolved_by_context_state": False}


def _semantic_boundaries(artifacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    boundaries = [
        {
            "boundary_name": "authority semantic boundaries",
            "description": "semantic context cannot grant approval, dispatch, execution, provider, mutation, or autonomous continuation authority",
            "enforced_by_context_state": False,
            "descriptive_only": True,
        },
        {
            "boundary_name": "execution semantic boundaries",
            "description": "semantic context cannot execute cognition behavior or activate providers",
            "enforced_by_context_state": False,
            "descriptive_only": True,
        },
        {
            "boundary_name": "governance scope boundaries",
            "description": "semantic context preserves explicit governance constraints without expanding scope",
            "enforced_by_context_state": False,
            "descriptive_only": True,
        },
        {
            "boundary_name": "replay continuity boundaries",
            "description": "semantic context references replay-visible evidence only",
            "enforced_by_context_state": False,
            "descriptive_only": True,
        },
        {
            "boundary_name": "admissibility semantic boundaries",
            "description": "semantic context reports admissibility signals without approving governance",
            "enforced_by_context_state": False,
            "descriptive_only": True,
        },
    ]
    if not artifacts:
        boundaries.append(
            {
                "boundary_name": UNKNOWN,
                "description": "no semantic artifacts available",
                "enforced_by_context_state": False,
                "descriptive_only": True,
            }
        )
    return boundaries


def _continuity_anchors(artifacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    anchors: list[dict[str, Any]] = []
    human_request = _first_str(artifacts, "human_request")
    semantic_intent = _first_str(artifacts, "semantic_intent")
    normalized_intent = _first_str(artifacts, "normalized_intent")
    replay_identity = _first_str(artifacts, "replay_identity")
    admissibility = _first_str(artifacts, "gate_status", "governance_status", "validation_status", "status")
    for name, value in (
        ("original governance intent", human_request),
        ("semantic intent", semantic_intent),
        ("normalized intent", normalized_intent),
        ("replay identity reference", replay_identity),
        ("admissibility classification", admissibility),
    ):
        anchors.append({"anchor_name": name, "value": value, "replay_visible": value != UNKNOWN, "inferred": False})
    anchors.append(
        {
            "anchor_name": "explicit governance constraints",
            "value": _collect_constraints(artifacts),
            "replay_visible": bool(artifacts),
            "inferred": False,
        }
    )
    return anchors


def _normalized_semantic_context(artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "human_request": _first_str(artifacts, "human_request"),
        "semantic_intent": _first_str(artifacts, "semantic_intent"),
        "normalized_intent": _first_str(artifacts, "normalized_intent"),
        "chatgpt_semantic_output": _first_str(artifacts, "chatgpt_semantic_output"),
        "source_artifact_types": [_artifact_type(artifact) for artifact in artifacts],
        "semantic_completion_performed": False,
        "hidden_inference_performed": False,
    }


def _governance_relevance(artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "has_replay_identity": _first_str(artifacts, "replay_identity") != UNKNOWN,
        "has_normalized_intent": _first_str(artifacts, "normalized_intent") != UNKNOWN,
        "has_admissibility_signal": _first_str(artifacts, "gate_status", "governance_status", "validation_status", "status") != UNKNOWN,
        "has_authority_boundary": any(isinstance(artifact.get("authority_boundary"), dict) for artifact in artifacts),
        "has_constraints": bool(_collect_constraints(artifacts)),
        "semantic_truth_certified": False,
        "execution_authority_granted": False,
    }


def _unknowns(artifacts: list[dict[str, Any]]) -> list[str]:
    if not artifacts:
        return ["no semantic artifacts provided", "human_request", "normalized_intent", "replay_identity"]
    unknowns = []
    if _first_str(artifacts, "human_request") == UNKNOWN:
        unknowns.append("human_request")
    if _first_str(artifacts, "normalized_intent") == UNKNOWN:
        unknowns.append("normalized_intent")
    if _first_str(artifacts, "replay_identity") == UNKNOWN:
        unknowns.append("replay_identity")
    return sorted(set(unknowns))


def _status(unknowns: list[str], ambiguity_state: dict[str, Any]) -> str:
    if "no semantic artifacts provided" in unknowns:
        return UNKNOWN_INSUFFICIENT_EVIDENCE
    if unknowns or ambiguity_state.get("status") in {AMBIGUITY_MODERATE, AMBIGUITY_HIGH, AMBIGUITY_UNKNOWN}:
        return SEMANTIC_CONTEXT_PARTIAL
    return SEMANTIC_CONTEXT_STABLE


def build_semantic_context_state(
    artifacts: Any = None,
    *,
    generated_at: str = GENERATED_AT,
) -> dict[str, Any]:
    safe_artifacts = _as_artifacts(artifacts)
    ambiguity = _ambiguity_state(safe_artifacts)
    unknowns = _unknowns(safe_artifacts)
    state = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "generated_at": str(generated_at),
        "semantic_context_status": _status(unknowns, ambiguity),
        "normalized_semantic_context": _normalized_semantic_context(safe_artifacts),
        "semantic_constraints": _collect_constraints(safe_artifacts),
        "semantic_continuity_anchors": _continuity_anchors(safe_artifacts),
        "semantic_boundaries": _semantic_boundaries(safe_artifacts),
        "ambiguity_state": ambiguity,
        "governance_relevance": _governance_relevance(safe_artifacts),
        "continuity_refs": _evidence_refs(safe_artifacts),
        "unknowns": unknowns,
        "notes": [
            "bounded semantic context visibility only",
            "no semantic reasoning engine",
            "no hidden intent inference",
            "no ambiguity resolution",
            "no semantic repair or autonomous context evolution",
        ],
        "read_only": True,
        "execution_authority_added": False,
        "orchestration_authority_added": False,
        "mutation_authority_added": False,
        "provider_activation_added": False,
        "cognition_scheduling_added": False,
        "autonomous_semantic_evolution_added": False,
        "hidden_semantic_inference_added": False,
        "ambiguity_resolution_performed": False,
        "semantic_repair_performed": False,
        "semantic_reasoning_engine_added": False,
    }
    state["semantic_context_hash"] = canonical_hash(_hash_input(state))
    return state


def validate_semantic_context_state(state: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if state.get("artifact_type") != ARTIFACT_TYPE:
        errors.append("invalid semantic context artifact_type")
    expected_hash = canonical_hash(_hash_input(state))
    if state.get("semantic_context_hash") != expected_hash:
        errors.append("semantic_context_hash mismatch")
    for key in (
        "execution_authority_added",
        "orchestration_authority_added",
        "mutation_authority_added",
        "provider_activation_added",
        "autonomous_semantic_evolution_added",
        "hidden_semantic_inference_added",
        "ambiguity_resolution_performed",
        "semantic_repair_performed",
        "semantic_reasoning_engine_added",
    ):
        if state.get(key) is not False:
            errors.append(f"semantic context boundary violated: {key}")
    validation = {
        "artifact_type": VALIDATION_ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "generated_at": GENERATED_AT,
        "validation_status": "INVALID" if errors else "VALID",
        "semantic_context_hash": state.get("semantic_context_hash", UNKNOWN),
        "expected_semantic_context_hash": expected_hash,
        "errors": sorted(set(errors)),
        "read_only": True,
    }
    validation["validation_hash"] = canonical_hash({key: value for key, value in validation.items() if key != "validation_hash"})
    return validation


def write_semantic_context_state(state: dict[str, Any], output_path: str | Path) -> dict[str, Any]:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(state, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return {"written": True, "output_path": str(path)}


def inspect_semantic_context(
    *,
    input_path: str | Path | None = None,
    output_path: str | Path | None = None,
    artifacts: Any = None,
    validate: bool = False,
) -> dict[str, Any]:
    loaded = _as_artifacts(artifacts)
    if not loaded:
        loaded = load_cognition_artifacts(input_path)
    state = build_semantic_context_state(loaded)
    result = {
        "command": "aigol cognition semantic-context",
        "input_path": str(input_path or ""),
        "artifact_count": len(loaded),
        "semantic_context_state": state,
        "read_only": True,
        "execution_authority_added": False,
        "orchestration_authority_added": False,
        "provider_activation_added": False,
        "hidden_semantic_inference_added": False,
        "semantic_repair_added": False,
    }
    if validate:
        result["semantic_context_validation"] = validate_semantic_context_state(state)
    if output_path:
        result["output"] = write_semantic_context_state(state, output_path)
    return result


def render_semantic_context_summary(state: dict[str, Any]) -> str:
    anchors = [
        f"  {item.get('anchor_name')}: {item.get('value')}"
        for item in state.get("semantic_continuity_anchors", [])
        if item.get("anchor_name") != "explicit governance constraints"
    ]
    return "\n".join(
        [
            "Semantic Context Status",
            f"  {state.get('semantic_context_status')}",
            "Normalized Semantic Context",
            f"  {json.dumps(state.get('normalized_semantic_context', {}), sort_keys=True)}",
            "Semantic Continuity Anchors",
            *(anchors or ["  UNKNOWN"]),
            "Semantic Boundaries",
            f"  {', '.join(item.get('boundary_name', UNKNOWN) for item in state.get('semantic_boundaries', []))}",
            "Ambiguity State",
            f"  {json.dumps(state.get('ambiguity_state', {}), sort_keys=True)}",
            "Governance Relevance",
            f"  {json.dumps(state.get('governance_relevance', {}), sort_keys=True)}",
            "Unknowns",
            f"  {json.dumps(state.get('unknowns', []), sort_keys=True)}",
            "Governance Guarantees",
            "  execution_authority: false",
            "  orchestration_authority: false",
            "  hidden_semantic_inference: false",
            "  semantic_repair: false",
            "  autonomous_semantic_evolution: false",
        ]
    )


__all__ = [
    "ARTIFACT_TYPE",
    "AMBIGUITY_HIGH",
    "AMBIGUITY_LOW",
    "AMBIGUITY_MODERATE",
    "AMBIGUITY_UNKNOWN",
    "SEMANTIC_CONTEXT_PARTIAL",
    "SEMANTIC_CONTEXT_STABLE",
    "UNKNOWN_INSUFFICIENT_EVIDENCE",
    "build_semantic_context_state",
    "inspect_semantic_context",
    "render_semantic_context_summary",
    "validate_semantic_context_state",
    "write_semantic_context_state",
]
