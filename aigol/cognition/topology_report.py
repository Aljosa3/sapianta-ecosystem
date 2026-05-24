"""Read-only cognition registry topology report.

The topology report derives fixed subsystem relationships from
COGNITION_REGISTRY_V1. It does not execute, orchestrate, plan, activate runtime,
route providers, infer hidden topology, schedule cognition, load plugins, or
grant authority.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

from aigol.cognition.registry import (
    ARTIFACT_TYPE as REGISTRY_ARTIFACT_TYPE,
    build_cognition_registry,
    load_cognition_registry_index,
    validate_cognition_registry,
)
from aigol.cognition.state_envelope import GENERATED_AT, UNKNOWN

ARTIFACT_TYPE = "COGNITION_REGISTRY_TOPOLOGY_REPORT_V1"
SCHEMA_VERSION = "1.0"

SUBSYSTEM_CATEGORY_MAP = {
    "constitutional_governance": {
        "authority_taxonomy",
        "constitutional_constraints",
        "constitutional_reasoning",
        "lineage_memory",
        "precedence_reasoning",
    },
    "semantic_interpretation": {
        "admissibility_gate",
        "admissibility_validation",
        "artifact_validation",
        "risk_escalation",
        "semantic_classification",
        "semantic_contract",
        "semantic_evidence",
        "semantic_ingress",
    },
    "authority_boundary": {
        "boundary_state",
        "cognition_action_boundary",
        "dispatch_authority",
        "execution_path_visibility",
        "handoff_boundary",
        "human_authority",
        "human_oversight",
    },
    "provider_execution_boundary": {
        "bounded_provider",
        "operational_cognition_substrate",
    },
    "replay_and_memory": {
        "execution_memory",
        "institutional_memory",
        "operational_epoch_memory",
        "primitive_topology",
        "replay_identity",
    },
    "reflection_advisory": {
        "advisory_guidance",
        "bounded_recommendation",
        "capability_reasoning",
        "intent_awareness",
        "meta_cognition",
        "meta_refinement_reasoning",
        "risk_reasoning",
    },
    "capability_and_learning_memory": {
        "bounded_learning_scaffold",
        "bounded_memory",
        "capability_memory",
        "self_assessment",
    },
}

SUBSYSTEM_RELATIONSHIPS = [
    {
        "from": "constitutional_governance",
        "to": "semantic_interpretation",
        "relationship": "constrains admissibility and semantic interpretation",
        "boundary": "constitutional precedence",
    },
    {
        "from": "semantic_interpretation",
        "to": "authority_boundary",
        "relationship": "produces governed meaning before authority transitions",
        "boundary": "admissibility and approval",
    },
    {
        "from": "authority_boundary",
        "to": "provider_execution_boundary",
        "relationship": "limits provider visibility and execution continuity",
        "boundary": "human approval and explicit dispatch authorization",
    },
    {
        "from": "provider_execution_boundary",
        "to": "replay_and_memory",
        "relationship": "emits governed execution evidence and return continuity",
        "boundary": "single provider and governed return evidence",
    },
    {
        "from": "replay_and_memory",
        "to": "reflection_advisory",
        "relationship": "feeds advisory reflection from replay-visible evidence",
        "boundary": "advisory only",
    },
    {
        "from": "reflection_advisory",
        "to": "authority_boundary",
        "relationship": "returns bounded recommendations requiring human authority",
        "boundary": "no automatic execution",
    },
    {
        "from": "capability_and_learning_memory",
        "to": "constitutional_governance",
        "relationship": "records bounded capability memory under governance constraints",
        "boundary": "no self-promotion",
    },
]

AUTHORITY_TRANSITION_ORDER = (
    "semantic_input_no_authority",
    "validator_no_execution_authority",
    "gate_no_execution_authority",
    "preview_no_execution_authority",
    "human_approval_evidence_not_execution",
    "handoff_preview_no_dispatch_authority",
    "dispatch_authorization_not_execution",
    "bounded_execution_authority_when_gated",
    "single_provider_bounded_execution",
    "evidence_persistence_no_replay_mutation",
)


def _canonical_copy(value: Any) -> Any:
    return deepcopy(value)


def _hash_input(value: dict[str, Any]) -> dict[str, Any]:
    safe = _canonical_copy(value)
    safe.pop("topology_report_hash", None)
    return safe


def _registry_from_input(input_path: str | Path | None = None, registry: dict[str, Any] | None = None) -> dict[str, Any]:
    if isinstance(registry, dict) and registry.get("artifact_type") == REGISTRY_ARTIFACT_TYPE:
        return _canonical_copy(registry)
    loaded = load_cognition_registry_index(input_path)
    if loaded.get("artifact_type") == REGISTRY_ARTIFACT_TYPE:
        return loaded
    return build_cognition_registry(loaded)


def _subsystem_for_category(category: str) -> str:
    for subsystem, categories in SUBSYSTEM_CATEGORY_MAP.items():
        if category in categories:
            return subsystem
    return "uncategorized"


def _subsystems(primitives: list[dict[str, Any]]) -> dict[str, Any]:
    subsystems: dict[str, dict[str, Any]] = {
        name: {
            "subsystem_name": name,
            "categories": sorted(categories),
            "primitive_ids": [],
            "boundary_role": _boundary_role(name),
        }
        for name, categories in sorted(SUBSYSTEM_CATEGORY_MAP.items())
    }
    subsystems["uncategorized"] = {
        "subsystem_name": "uncategorized",
        "categories": [],
        "primitive_ids": [],
        "boundary_role": "UNKNOWN",
    }
    for primitive in primitives:
        category = str(primitive.get("cognition_category", UNKNOWN))
        subsystem = _subsystem_for_category(category)
        subsystems[subsystem]["primitive_ids"].append(str(primitive.get("id", UNKNOWN)))
        if subsystem == "uncategorized" and category not in subsystems[subsystem]["categories"]:
            subsystems[subsystem]["categories"].append(category)
    return {
        key: {**value, "primitive_ids": sorted(value["primitive_ids"]), "categories": sorted(value["categories"])}
        for key, value in sorted(subsystems.items())
        if value["primitive_ids"] or key != "uncategorized"
    }


def _boundary_role(subsystem: str) -> str:
    roles = {
        "constitutional_governance": "defines governing constraints",
        "semantic_interpretation": "normalizes and validates semantic evidence",
        "authority_boundary": "mediates approval and dispatch boundaries",
        "provider_execution_boundary": "contains single-provider execution continuity",
        "replay_and_memory": "preserves replay-visible evidence and memory",
        "reflection_advisory": "produces advisory-only reflection",
        "capability_and_learning_memory": "tracks bounded capability and learning memory",
    }
    return roles.get(subsystem, UNKNOWN)


def _boundary_analysis(registry: dict[str, Any], subsystems: dict[str, Any]) -> dict[str, Any]:
    boundaries = registry.get("governance_boundaries", {})
    enforced = {
        key: value is False
        for key, value in boundaries.items()
        if key in {
            "execution_authority",
            "orchestration_authority",
            "autonomous_cognition",
            "autonomous_continuation",
            "provider_routing_authority",
            "mutation_authority",
            "runtime_activation",
            "self_registration",
            "hidden_ingestion",
        }
    }
    return {
        "governance_boundaries_present": bool(boundaries),
        "no_authority_boundaries_enforced": enforced,
        "boundary_subsystems": sorted(
            subsystem
            for subsystem in ("constitutional_governance", "semantic_interpretation", "authority_boundary", "provider_execution_boundary", "replay_and_memory")
            if subsystem in subsystems
        ),
    }


def _replay_continuity_map(primitives: list[dict[str, Any]], subsystems: dict[str, Any]) -> dict[str, Any]:
    high_replay = {
        str(primitive.get("id", UNKNOWN))
        for primitive in primitives
        if primitive.get("replay_relevance") == "high"
    }
    subsystem_replay: dict[str, dict[str, Any]] = {}
    for subsystem, data in subsystems.items():
        primitive_ids = set(data.get("primitive_ids", []))
        high = sorted(primitive_ids & high_replay)
        subsystem_replay[subsystem] = {
            "high_replay_primitive_count": len(high),
            "high_replay_primitives": high,
            "replay_visible": bool(high),
        }
    return subsystem_replay


def _authority_transition_map(primitives: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_authority: dict[str, list[str]] = {}
    for primitive in primitives:
        authority = str(primitive.get("authority_classification", UNKNOWN))
        by_authority.setdefault(authority, []).append(str(primitive.get("id", UNKNOWN)))
    transitions: list[dict[str, Any]] = []
    for order, authority in enumerate(AUTHORITY_TRANSITION_ORDER):
        transitions.append(
            {
                "order": order,
                "authority_classification": authority,
                "primitive_ids": sorted(by_authority.get(authority, [])),
                "authority_granted_by_report": False,
            }
        )
    extra_authorities = sorted(set(by_authority) - set(AUTHORITY_TRANSITION_ORDER))
    for authority in extra_authorities:
        transitions.append(
            {
                "order": len(transitions),
                "authority_classification": authority,
                "primitive_ids": sorted(by_authority[authority]),
                "authority_granted_by_report": False,
            }
        )
    return transitions


def _integrity_guarantees(registry: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
    return {
        "registry_valid": validation.get("validation_status") == "VALID",
        "registry_hash": registry.get("registry_hash", UNKNOWN),
        "validation_hash": validation.get("validation_hash", UNKNOWN),
        "source_files_missing": registry.get("source_file_status", {}).get("missing_count", UNKNOWN),
        "read_only": True,
        "execution_authority": False,
        "orchestration_authority": False,
        "autonomous_cognition": False,
        "planning_authority": False,
        "runtime_activation": False,
        "provider_routing": False,
        "semantic_reasoning": False,
        "hidden_topology_inference": False,
        "dynamic_graph_execution": False,
        "self_modifying_cognition": False,
        "cognition_scheduling": False,
        "plugin_loading": False,
    }


def build_cognition_registry_topology_report(
    registry: dict[str, Any] | None = None,
    *,
    input_path: str | Path | None = None,
    generated_at: str = GENERATED_AT,
) -> dict[str, Any]:
    resolved_registry = _registry_from_input(input_path=input_path, registry=registry)
    validation = validate_cognition_registry(resolved_registry)
    primitives = [item for item in resolved_registry.get("primitives", []) if isinstance(item, dict)]
    subsystems = _subsystems(primitives)
    report = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "generated_at": str(generated_at),
        "source_registry_hash": resolved_registry.get("registry_hash", UNKNOWN),
        "source_registry_validation_status": validation.get("validation_status", UNKNOWN),
        "primitive_count": len(primitives),
        "subsystems": subsystems,
        "relationships": SUBSYSTEM_RELATIONSHIPS,
        "boundary_analysis": _boundary_analysis(resolved_registry, subsystems),
        "replay_continuity_map": _replay_continuity_map(primitives, subsystems),
        "authority_transition_map": _authority_transition_map(primitives),
        "integrity_guarantees": _integrity_guarantees(resolved_registry, validation),
        "unknowns": ["uncategorized primitives present"] if "uncategorized" in subsystems else [],
        "notes": [
            "read-only topology visibility only",
            "relationships are derived from explicit registry categories and fixed subsystem mapping",
            "no hidden topology inference",
            "no execution, orchestration, planning, runtime activation, provider routing, scheduling, or plugin loading",
        ],
        "read_only": True,
        "execution_authority_added": False,
        "orchestration_authority_added": False,
        "autonomous_cognition_added": False,
        "planning_authority_added": False,
        "runtime_activation_added": False,
        "provider_routing_added": False,
        "semantic_reasoning_added": False,
        "hidden_topology_inference_added": False,
        "dynamic_graph_execution_added": False,
        "self_modifying_cognition_added": False,
        "cognition_scheduling_added": False,
        "plugin_loading_added": False,
    }
    report["topology_report_hash"] = canonical_hash(_hash_input(report))
    return report


def write_topology_report(report: dict[str, Any], output_path: str | Path) -> dict[str, Any]:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return {"written": True, "output_path": str(path)}


def inspect_cognition_topology(
    *,
    input_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    report = build_cognition_registry_topology_report(input_path=input_path)
    result = {
        "command": "aigol cognition topology",
        "input_path": str(input_path or "COGNITION_PRIMITIVES_INDEX.json"),
        "cognition_topology_report": report,
        "read_only": True,
        "execution_authority_added": False,
        "orchestration_authority_added": False,
        "autonomous_cognition_added": False,
        "planning_authority_added": False,
        "runtime_activation_added": False,
        "provider_routing_added": False,
        "semantic_reasoning_added": False,
        "hidden_topology_inference_added": False,
        "dynamic_graph_execution_added": False,
        "self_modifying_cognition_added": False,
        "cognition_scheduling_added": False,
        "plugin_loading_added": False,
    }
    if output_path:
        result["output"] = write_topology_report(report, output_path)
    return result


def render_cognition_topology_summary(report: dict[str, Any]) -> str:
    subsystem_names = sorted(report.get("subsystems", {}).keys())
    relationship_lines = [
        f"  {item.get('from')} -> {item.get('to')}: {item.get('boundary')}"
        for item in report.get("relationships", [])
    ]
    lines = [
        "Topology Status",
        f"  source_registry_validation_status: {report.get('source_registry_validation_status')}",
        f"  topology_report_hash: {report.get('topology_report_hash')}",
        "Subsystems",
        f"  {', '.join(subsystem_names)}",
        "Relationships",
        *(relationship_lines or ["  UNKNOWN"]),
        "Boundary Analysis",
        f"  {json.dumps(report.get('boundary_analysis', {}), sort_keys=True)}",
        "Replay Continuity",
        f"  {json.dumps(report.get('replay_continuity_map', {}), sort_keys=True)}",
        "Authority Transitions",
        f"  {len(report.get('authority_transition_map', []))} classifications",
        "Integrity Guarantees",
        "  execution_authority: false",
        "  orchestration_authority: false",
        "  autonomous_cognition: false",
        "  planning_authority: false",
        "  runtime_activation: false",
        "  provider_routing: false",
        "  semantic_reasoning: false",
        "  hidden_topology_inference: false",
    ]
    return "\n".join(lines)


__all__ = [
    "ARTIFACT_TYPE",
    "SCHEMA_VERSION",
    "build_cognition_registry_topology_report",
    "inspect_cognition_topology",
    "render_cognition_topology_summary",
    "write_topology_report",
]
