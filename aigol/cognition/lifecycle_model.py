"""Read-only cognition lifecycle model.

The lifecycle model describes bounded cognition process visibility across
governed phases. It does not execute cognition, orchestrate phases, activate
providers, infer hidden state, schedule behavior, or grant authority.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

from aigol.cognition.state_envelope import GENERATED_AT, UNKNOWN
from aigol.cognition.topology_report import build_cognition_registry_topology_report

ARTIFACT_TYPE = "COGNITION_LIFECYCLE_MODEL_V1"
VALIDATION_ARTIFACT_TYPE = "COGNITION_LIFECYCLE_MODEL_VALIDATION_V1"
SCHEMA_VERSION = "1.0"

PHASE_DEFINITIONS = (
    ("semantic_ingress_phase", "semantic_interpretation", "semantic input becomes replay-visible evidence"),
    ("normalization_phase", "semantic_interpretation", "semantic input is normalized without semantic truth certification"),
    ("semantic_contract_phase", "semantic_interpretation", "semantic meaning is bounded into non-execution contract evidence"),
    ("admissibility_phase", "semantic_interpretation", "governance admissibility is evaluated fail-closed"),
    ("authority_boundary_phase", "authority_boundary", "execution boundary visibility is established without execution"),
    ("approval_phase", "authority_boundary", "human approval evidence is recorded without dispatch authority"),
    ("dispatch_boundary_phase", "authority_boundary", "dispatch authorization evidence is recorded without execution"),
    ("execution_boundary_phase", "provider_execution_boundary", "bounded single-provider execution continuity is constrained"),
    ("governed_return_phase", "replay_and_memory", "execution result evidence becomes governed return memory"),
    ("replay_verification_phase", "replay_and_memory", "lineage and replay evidence are verified"),
    ("reflection_phase", "reflection_advisory", "advisory reflection may inspect replay evidence"),
    ("governance_memory_phase", "replay_and_memory", "institutional memory preserves governance state"),
    ("cognition_registry_phase", "replay_and_memory", "cognition primitives are indexed read-only"),
    ("cognition_topology_phase", "replay_and_memory", "subsystem relationships are reported read-only"),
    ("semantic_continuity_phase", "semantic_interpretation", "semantic continuity is checked without truth certification"),
    ("cognition_integrity_phase", "constitutional_governance", "registry, topology, and lifecycle integrity are summarized"),
)

TRANSITION_DEFINITIONS = (
    ("semantic_ingress_phase", "normalization_phase", "semantic_ingress_normalization"),
    ("normalization_phase", "semantic_contract_phase", "semantic_contract_boundary"),
    ("semantic_contract_phase", "admissibility_phase", "admissibility_evaluation"),
    ("admissibility_phase", "authority_boundary_phase", "execution_boundary_preview"),
    ("authority_boundary_phase", "approval_phase", "human_approval_boundary"),
    ("approval_phase", "dispatch_boundary_phase", "explicit_dispatch_boundary"),
    ("dispatch_boundary_phase", "execution_boundary_phase", "controlled_execution_boundary"),
    ("execution_boundary_phase", "governed_return_phase", "governed_return_capture"),
    ("governed_return_phase", "replay_verification_phase", "replay_verification"),
    ("replay_verification_phase", "reflection_phase", "advisory_reflection"),
    ("reflection_phase", "governance_memory_phase", "governance_memory_update_visibility"),
    ("governance_memory_phase", "cognition_registry_phase", "primitive_registry_visibility"),
    ("cognition_registry_phase", "cognition_topology_phase", "topology_visibility"),
    ("cognition_topology_phase", "semantic_continuity_phase", "semantic_continuity_visibility"),
    ("semantic_continuity_phase", "cognition_integrity_phase", "integrity_visibility"),
)


def _hash_input(value: dict[str, Any]) -> dict[str, Any]:
    safe = deepcopy(value)
    safe.pop("lifecycle_model_hash", None)
    return safe


def _subsystem_primitives(topology_report: dict[str, Any], subsystem: str) -> list[str]:
    data = topology_report.get("subsystems", {}).get(subsystem, {})
    values = data.get("primitive_ids", [])
    return sorted(str(value) for value in values) if isinstance(values, list) else []


def _phase(phase_id: str, subsystem: str, description: str, topology_report: dict[str, Any], order: int) -> dict[str, Any]:
    return {
        "phase_id": phase_id,
        "phase_order": order,
        "subsystem_ref": subsystem,
        "primitive_refs": _subsystem_primitives(topology_report, subsystem),
        "description": description,
        "replay_visible": True,
        "execution_capability": False,
        "authority_granted_by_phase": False,
        "runtime_activation": False,
        "unknown_handling": "UNKNOWN if evidence is absent or subsystem is uncategorized",
    }


def _transition(source: str, target: str, transition_type: str, order: int) -> dict[str, Any]:
    return {
        "transition_order": order,
        "source_phase": source,
        "target_phase": target,
        "transition_type": transition_type,
        "continuity_requirements": [
            "replay identity preserved where available",
            "lineage evidence remains replay-visible",
            "authority boundary remains explicit",
        ],
        "authority_constraints": [
            "no authority granted by lifecycle model",
            "execution capability remains false",
            "autonomous continuation remains false",
        ],
        "replay_visibility": "REPLAY_VISIBLE_DESCRIPTIVE_ONLY",
        "execution_capability": False,
        "runtime_activation": False,
        "notes": ["valid descriptive lifecycle transition only; not an executable edge"],
    }


def _continuity_paths() -> list[dict[str, Any]]:
    return [
        {
            "path_name": "semantic_continuity_propagation",
            "phases": [
                "semantic_ingress_phase",
                "normalization_phase",
                "semantic_contract_phase",
                "admissibility_phase",
                "semantic_continuity_phase",
            ],
            "continuity_checks": ["normalized intent stability", "semantic contract presence", "admissibility consistency"],
            "weakening_points": ["missing normalized intent", "missing semantic contract", "missing admissibility evidence"],
            "authority_granted": False,
        },
        {
            "path_name": "authority_continuity_propagation",
            "phases": [
                "authority_boundary_phase",
                "approval_phase",
                "dispatch_boundary_phase",
                "execution_boundary_phase",
            ],
            "continuity_checks": ["human approval evidence", "explicit dispatch evidence", "execution boundary constraints"],
            "weakening_points": ["missing approval", "missing dispatch authorization", "execution boundary mismatch"],
            "authority_granted": False,
        },
        {
            "path_name": "replay_continuity_propagation",
            "phases": [
                "semantic_ingress_phase",
                "governed_return_phase",
                "replay_verification_phase",
                "governance_memory_phase",
            ],
            "continuity_checks": ["replay identity", "lineage hashes", "governed return hash", "ledger evidence"],
            "weakening_points": ["orphaned lineage", "missing governed return", "missing replay verification"],
            "authority_granted": False,
        },
    ]


def _stabilization_stages() -> list[dict[str, Any]]:
    return [
        {
            "stage_name": "semantic_stabilization",
            "phase_refs": ["normalization_phase", "semantic_contract_phase", "semantic_continuity_phase"],
            "stabilization_type": "semantic continuity visibility",
            "operational": False,
        },
        {
            "stage_name": "replay_stabilization",
            "phase_refs": ["governed_return_phase", "replay_verification_phase"],
            "stabilization_type": "replay and lineage continuity visibility",
            "operational": False,
        },
        {
            "stage_name": "governance_stabilization",
            "phase_refs": ["admissibility_phase", "authority_boundary_phase", "approval_phase", "dispatch_boundary_phase"],
            "stabilization_type": "governance boundary visibility",
            "operational": False,
        },
        {
            "stage_name": "cognition_integrity_stabilization",
            "phase_refs": ["cognition_registry_phase", "cognition_topology_phase", "cognition_integrity_phase"],
            "stabilization_type": "registry, topology, and integrity visibility",
            "operational": False,
        },
    ]


def _epoch_boundaries(topology_report: dict[str, Any]) -> list[dict[str, Any]]:
    registry_valid = topology_report.get("source_registry_validation_status") == "VALID"
    return [
        {
            "epoch_name": "bounded_cognition_visibility_epoch",
            "epoch_type": "descriptive_cognition_lifecycle",
            "stabilization_level": "STRUCTURAL_VISIBILITY",
            "continuity_status": "VISIBLE" if registry_valid else "UNKNOWN",
            "governance_integrity": "REGISTRY_VALID" if registry_valid else "REGISTRY_NOT_VALIDATED",
            "replay_visibility": "REPLAY_VISIBLE_DESCRIPTIVE_ONLY",
            "operational": False,
            "scheduling_enabled": False,
            "notes": ["epoch is descriptive only and does not activate cognition behavior"],
        },
        {
            "epoch_name": "governed_execution_substrate_epoch",
            "epoch_type": "certified_runtime_memory_reference",
            "stabilization_level": "EVIDENCE_BACKED",
            "continuity_status": "VISIBLE",
            "governance_integrity": "BOUNDARY_CONSTRAINED",
            "replay_visibility": "REPLAY_VISIBLE_DESCRIPTIVE_ONLY",
            "operational": False,
            "scheduling_enabled": False,
            "notes": ["references existing governed runtime evidence without invoking runtime"],
        },
    ]


def _governance_constraints() -> list[dict[str, Any]]:
    constraints = (
        "no execution authority",
        "no orchestration",
        "no autonomous cognition",
        "no planning authority",
        "no runtime cognition execution",
        "no provider routing",
        "no semantic reasoning",
        "no hidden state evolution",
        "no dynamic lifecycle adaptation",
        "no cognition scheduling",
        "no self-modifying cognition",
        "no hidden transition inference",
    )
    return [
        {
            "constraint": constraint,
            "enforced_by_model": True,
            "authority_granted": False,
        }
        for constraint in constraints
    ]


def build_cognition_lifecycle_model(
    topology_report: dict[str, Any] | None = None,
    *,
    input_path: str | Path | None = None,
    generated_at: str = GENERATED_AT,
) -> dict[str, Any]:
    report = topology_report if isinstance(topology_report, dict) else build_cognition_registry_topology_report(input_path=input_path)
    phases = [
        _phase(phase_id, subsystem, description, report, index)
        for index, (phase_id, subsystem, description) in enumerate(PHASE_DEFINITIONS)
    ]
    unknowns = list(report.get("unknowns", [])) if isinstance(report.get("unknowns"), list) else []
    if unknowns:
        phases.append(
            {
                "phase_id": "UNKNOWN",
                "phase_order": len(phases),
                "subsystem_ref": "uncategorized",
                "primitive_refs": _subsystem_primitives(report, "uncategorized"),
                "description": "unknown lifecycle phase for uncategorized evidence",
                "replay_visible": True,
                "execution_capability": False,
                "authority_granted_by_phase": False,
                "runtime_activation": False,
                "unknown_handling": "explicit UNKNOWN, not inferred",
            }
        )
    transitions = [
        _transition(source, target, transition_type, index)
        for index, (source, target, transition_type) in enumerate(TRANSITION_DEFINITIONS)
    ]
    lifecycle_status = "VISIBLE" if report.get("source_registry_validation_status") == "VALID" else "UNKNOWN"
    model = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "generated_at": str(generated_at),
        "lifecycle_status": lifecycle_status,
        "source_topology_report_hash": report.get("topology_report_hash", UNKNOWN),
        "source_registry_validation_status": report.get("source_registry_validation_status", UNKNOWN),
        "phase_count": len(phases),
        "transition_count": len(transitions),
        "phases": phases,
        "transitions": transitions,
        "continuity_propagation_paths": _continuity_paths(),
        "semantic_stabilization_stages": _stabilization_stages(),
        "governance_constraints": _governance_constraints(),
        "epoch_boundaries": _epoch_boundaries(report),
        "unknowns": sorted(set(unknowns)),
        "notes": [
            "read-only cognition lifecycle visibility only",
            "lifecycle transitions are descriptive, not executable",
            "no hidden transition inference",
            "no runtime cognition behavior, scheduling, orchestration, or provider activation",
        ],
        "read_only": True,
        "execution_authority_added": False,
        "orchestration_authority_added": False,
        "autonomous_cognition_added": False,
        "autonomous_continuation_added": False,
        "planning_authority_added": False,
        "runtime_cognition_execution_added": False,
        "provider_activation_added": False,
        "provider_routing_added": False,
        "semantic_reasoning_added": False,
        "hidden_state_evolution_added": False,
        "dynamic_lifecycle_adaptation_added": False,
        "cognition_scheduling_added": False,
        "self_modifying_cognition_added": False,
        "hidden_transition_inference_added": False,
    }
    model["lifecycle_model_hash"] = canonical_hash(_hash_input(model))
    return model


def validate_cognition_lifecycle_model(model: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if model.get("artifact_type") != ARTIFACT_TYPE:
        errors.append("invalid lifecycle artifact_type")
    if model.get("phase_count") != len(model.get("phases", [])):
        errors.append("phase_count mismatch")
    if model.get("transition_count") != len(model.get("transitions", [])):
        errors.append("transition_count mismatch")
    expected_hash = canonical_hash(_hash_input(model))
    if model.get("lifecycle_model_hash") != expected_hash:
        errors.append("lifecycle_model_hash mismatch")
    for transition in model.get("transitions", []):
        if transition.get("execution_capability") is not False:
            errors.append("transition execution capability violated")
        if transition.get("runtime_activation") is not False:
            errors.append("transition runtime activation violated")
    for key in (
        "execution_authority_added",
        "orchestration_authority_added",
        "autonomous_continuation_added",
        "provider_activation_added",
        "runtime_cognition_execution_added",
        "cognition_scheduling_added",
        "hidden_transition_inference_added",
    ):
        if model.get(key) is not False:
            errors.append(f"lifecycle boundary violated: {key}")
    validation = {
        "artifact_type": VALIDATION_ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "generated_at": GENERATED_AT,
        "validation_status": "INVALID" if errors else "VALID",
        "lifecycle_model_hash": model.get("lifecycle_model_hash", UNKNOWN),
        "expected_lifecycle_model_hash": expected_hash,
        "errors": sorted(set(errors)),
        "read_only": True,
        "execution_authority_added": False,
        "orchestration_authority_added": False,
        "autonomous_continuation_added": False,
        "provider_activation_added": False,
    }
    validation["validation_hash"] = canonical_hash({key: value for key, value in validation.items() if key != "validation_hash"})
    return validation


def write_lifecycle_model(model: dict[str, Any], output_path: str | Path) -> dict[str, Any]:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(model, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return {"written": True, "output_path": str(path)}


def inspect_cognition_lifecycle(
    *,
    output_path: str | Path | None = None,
    validate: bool = False,
) -> dict[str, Any]:
    model = build_cognition_lifecycle_model()
    result = {
        "command": "aigol cognition lifecycle",
        "cognition_lifecycle_model": model,
        "read_only": True,
        "execution_authority_added": False,
        "orchestration_authority_added": False,
        "autonomous_cognition_added": False,
        "autonomous_continuation_added": False,
        "planning_authority_added": False,
        "provider_activation_added": False,
        "runtime_cognition_execution_added": False,
        "cognition_scheduling_added": False,
    }
    if validate:
        result["lifecycle_validation"] = validate_cognition_lifecycle_model(model)
    if output_path:
        result["output"] = write_lifecycle_model(model, output_path)
    return result


def render_cognition_lifecycle_summary(model: dict[str, Any]) -> str:
    phase_ids = [str(item.get("phase_id")) for item in model.get("phases", [])]
    transition_lines = [
        f"  {item.get('source_phase')} -> {item.get('target_phase')}: {item.get('transition_type')}"
        for item in model.get("transitions", [])
    ]
    continuity_lines = [
        f"  {item.get('path_name')}: {', '.join(item.get('phases', []))}"
        for item in model.get("continuity_propagation_paths", [])
    ]
    stabilization_lines = [
        f"  {item.get('stage_name')}: {item.get('stabilization_type')}"
        for item in model.get("semantic_stabilization_stages", [])
    ]
    epoch_lines = [
        f"  {item.get('epoch_name')}: {item.get('stabilization_level')}"
        for item in model.get("epoch_boundaries", [])
    ]
    return "\n".join(
        [
            "Lifecycle Phases",
            f"  {', '.join(phase_ids)}",
            "Lifecycle Transitions",
            *(transition_lines or ["  UNKNOWN"]),
            "Semantic Continuity Paths",
            *(continuity_lines or ["  UNKNOWN"]),
            "Authority Transition Phases",
            "  authority_boundary_phase, approval_phase, dispatch_boundary_phase, execution_boundary_phase",
            "Replay Continuity Propagation",
            "  semantic_ingress_phase -> governed_return_phase -> replay_verification_phase -> governance_memory_phase",
            "Stabilization Stages",
            *(stabilization_lines or ["  UNKNOWN"]),
            "Epoch Boundaries",
            *(epoch_lines or ["  UNKNOWN"]),
            "Governance Constraints",
            "  execution_authority: false",
            "  orchestration_authority: false",
            "  autonomous_continuation: false",
            "  provider_activation: false",
            "  cognition_scheduling: false",
            "Unknown / Unstable Areas",
            f"  {json.dumps(model.get('unknowns', []), sort_keys=True)}",
        ]
    )


__all__ = [
    "ARTIFACT_TYPE",
    "SCHEMA_VERSION",
    "build_cognition_lifecycle_model",
    "inspect_cognition_lifecycle",
    "render_cognition_lifecycle_summary",
    "validate_cognition_lifecycle_model",
    "write_lifecycle_model",
]
