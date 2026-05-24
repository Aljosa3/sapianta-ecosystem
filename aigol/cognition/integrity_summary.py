"""Unified read-only cognition integrity summary.

The integrity summary consolidates cognition observability artifacts into one
governance-safe audit view. It does not execute, orchestrate, plan, activate
runtime, route providers, infer hidden state, repair continuity, or mutate
evidence.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

from aigol.cognition.lifecycle_model import (
    build_cognition_lifecycle_model,
    validate_cognition_lifecycle_model,
)
from aigol.cognition.registry import build_cognition_registry, load_cognition_registry_index, validate_cognition_registry
from aigol.cognition.semantic_replay import build_semantic_replay_continuity_check
from aigol.cognition.state_envelope import GENERATED_AT, UNKNOWN, build_cognition_state_envelope, load_cognition_artifacts
from aigol.cognition.topology_report import build_cognition_registry_topology_report

ARTIFACT_TYPE = "COGNITION_INTEGRITY_SUMMARY_V1"
VALIDATION_ARTIFACT_TYPE = "COGNITION_INTEGRITY_SUMMARY_VALIDATION_V1"
SCHEMA_VERSION = "1.0"

HEALTHY = "HEALTHY"
HEALTHY_WITH_UNKNOWN_CONTEXT = "HEALTHY_WITH_UNKNOWN_CONTEXT"
DEGRADED = "DEGRADED"
INVALID = "INVALID"

DEGRADED_SEMANTIC_STATUSES = {
    "DRIFT_DETECTED",
    "AUTHORITY_DRIFT_DETECTED",
    "REPLAY_DISCONTINUITY",
    "INVALID_TRANSITION_CHAIN",
}


def _hash_input(value: dict[str, Any]) -> dict[str, Any]:
    safe = deepcopy(value)
    safe.pop("integrity_summary_hash", None)
    return safe


def _component(name: str, artifact: dict[str, Any], status: str, hash_field: str) -> dict[str, Any]:
    return {
        "component_name": name,
        "artifact_type": artifact.get("artifact_type", UNKNOWN),
        "status": status,
        "hash": artifact.get(hash_field, UNKNOWN),
        "read_only": True,
    }


def _semantic_status(check: dict[str, Any]) -> str:
    return str(check.get("continuity_status", UNKNOWN))


def _health_status(
    *,
    registry_validation: dict[str, Any],
    topology_report: dict[str, Any],
    lifecycle_validation: dict[str, Any],
    semantic_check: dict[str, Any],
    envelope: dict[str, Any],
) -> str:
    if registry_validation.get("validation_status") != "VALID":
        return INVALID
    if topology_report.get("source_registry_validation_status") != "VALID":
        return INVALID
    if lifecycle_validation.get("validation_status") != "VALID":
        return INVALID
    for key in (
        "execution_authority",
        "orchestration_authority",
        "autonomous_continuation",
        "mutation_authority",
    ):
        if envelope.get(key) is not False:
            return INVALID
    semantic_status = _semantic_status(semantic_check)
    if semantic_status in DEGRADED_SEMANTIC_STATUSES:
        return DEGRADED
    if semantic_status == "UNKNOWN_INSUFFICIENT_EVIDENCE" or envelope.get("replay_identity") == UNKNOWN:
        return HEALTHY_WITH_UNKNOWN_CONTEXT
    if semantic_status == "VERIFIED_WITH_WARNINGS":
        return HEALTHY_WITH_UNKNOWN_CONTEXT
    return HEALTHY


def _governance_guarantees() -> dict[str, bool]:
    return {
        "execution_authority": False,
        "orchestration_authority": False,
        "autonomous_cognition": False,
        "autonomous_continuation": False,
        "planning_authority": False,
        "runtime_cognition_execution": False,
        "provider_routing": False,
        "provider_activation": False,
        "semantic_reasoning": False,
        "hidden_inference": False,
        "runtime_activation": False,
        "cognition_scheduling": False,
        "self_modifying_cognition": False,
        "dynamic_repair_behavior": False,
        "continuity_repair": False,
    }


def _audit_findings(
    *,
    status: str,
    semantic_check: dict[str, Any],
    registry_validation: dict[str, Any],
    lifecycle_validation: dict[str, Any],
) -> list[dict[str, Any]]:
    findings = [
        {
            "finding": "registry_integrity",
            "status": registry_validation.get("validation_status", UNKNOWN),
            "details": registry_validation.get("errors", []),
        },
        {
            "finding": "semantic_continuity",
            "status": semantic_check.get("continuity_status", UNKNOWN),
            "details": semantic_check.get("forbidden_findings", []),
        },
        {
            "finding": "lifecycle_integrity",
            "status": lifecycle_validation.get("validation_status", UNKNOWN),
            "details": lifecycle_validation.get("errors", []),
        },
        {
            "finding": "overall_cognition_health",
            "status": status,
            "details": [],
        },
    ]
    return findings


def build_cognition_integrity_summary(
    artifacts: Any = None,
    *,
    input_path: str | Path | None = None,
    generated_at: str = GENERATED_AT,
) -> dict[str, Any]:
    loaded_artifacts = artifacts if artifacts is not None else load_cognition_artifacts(input_path)
    envelope = build_cognition_state_envelope(loaded_artifacts, generated_at=generated_at)
    semantic_check = build_semantic_replay_continuity_check(loaded_artifacts, generated_at=generated_at)
    registry = build_cognition_registry(load_cognition_registry_index())
    registry_validation = validate_cognition_registry(registry)
    topology_report = build_cognition_registry_topology_report(registry)
    lifecycle_model = build_cognition_lifecycle_model(topology_report)
    lifecycle_validation = validate_cognition_lifecycle_model(lifecycle_model)
    integrity_status = _health_status(
        registry_validation=registry_validation,
        topology_report=topology_report,
        lifecycle_validation=lifecycle_validation,
        semantic_check=semantic_check,
        envelope=envelope,
    )
    unknowns = sorted(
        set(
            list(envelope.get("lineage_refs", {}).keys() if envelope.get("replay_identity") == UNKNOWN else [])
            + list(semantic_check.get("unknowns", []))
            + list(topology_report.get("unknowns", []))
            + list(lifecycle_model.get("unknowns", []))
        )
    )
    summary = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "generated_at": str(generated_at),
        "integrity_status": integrity_status,
        "component_count": 5,
        "components": [
            _component("cognition_state_envelope", envelope, envelope.get("continuity_status", UNKNOWN), "envelope_hash"),
            _component("semantic_replay_continuity", semantic_check, semantic_check.get("continuity_status", UNKNOWN), "semantic_replay_check_hash"),
            _component("cognition_registry", registry, registry_validation.get("validation_status", UNKNOWN), "registry_hash"),
            _component("cognition_topology_report", topology_report, topology_report.get("source_registry_validation_status", UNKNOWN), "topology_report_hash"),
            _component("cognition_lifecycle_model", lifecycle_model, lifecycle_validation.get("validation_status", UNKNOWN), "lifecycle_model_hash"),
        ],
        "health_summary": {
            "structural_registry_health": registry_validation.get("validation_status", UNKNOWN),
            "semantic_continuity_health": semantic_check.get("continuity_status", UNKNOWN),
            "replay_lineage_health": envelope.get("continuity_status", UNKNOWN),
            "topology_health": topology_report.get("source_registry_validation_status", UNKNOWN),
            "lifecycle_health": lifecycle_validation.get("validation_status", UNKNOWN),
            "authority_boundary_health": "BOUNDED",
            "governance_guarantees_intact": True,
        },
        "governance_guarantees": _governance_guarantees(),
        "audit_findings": _audit_findings(
            status=integrity_status,
            semantic_check=semantic_check,
            registry_validation=registry_validation,
            lifecycle_validation=lifecycle_validation,
        ),
        "unknowns": unknowns,
        "source_hashes": {
            "envelope_hash": envelope.get("envelope_hash", UNKNOWN),
            "semantic_replay_check_hash": semantic_check.get("semantic_replay_check_hash", UNKNOWN),
            "registry_hash": registry.get("registry_hash", UNKNOWN),
            "topology_report_hash": topology_report.get("topology_report_hash", UNKNOWN),
            "lifecycle_model_hash": lifecycle_model.get("lifecycle_model_hash", UNKNOWN),
        },
        "notes": [
            "unified read-only cognition integrity audit only",
            "health summary is structural and replay-visible, not semantic truth certification",
            "UNKNOWN context is reported rather than guessed",
            "no execution, orchestration, planning, runtime activation, provider routing, repair, or hidden inference",
        ],
        "read_only": True,
        "execution_authority_added": False,
        "orchestration_authority_added": False,
        "autonomous_cognition_added": False,
        "autonomous_continuation_added": False,
        "planning_authority_added": False,
        "runtime_cognition_execution_added": False,
        "provider_routing_added": False,
        "provider_activation_added": False,
        "semantic_reasoning_added": False,
        "hidden_inference_added": False,
        "runtime_activation_added": False,
        "cognition_scheduling_added": False,
        "self_modifying_cognition_added": False,
        "dynamic_repair_behavior_added": False,
        "continuity_repair_added": False,
    }
    summary["integrity_summary_hash"] = canonical_hash(_hash_input(summary))
    return summary


def validate_cognition_integrity_summary(summary: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if summary.get("artifact_type") != ARTIFACT_TYPE:
        errors.append("invalid integrity summary artifact_type")
    if summary.get("component_count") != len(summary.get("components", [])):
        errors.append("component_count mismatch")
    expected_hash = canonical_hash(_hash_input(summary))
    if summary.get("integrity_summary_hash") != expected_hash:
        errors.append("integrity_summary_hash mismatch")
    for key in (
        "execution_authority_added",
        "orchestration_authority_added",
        "autonomous_continuation_added",
        "provider_activation_added",
        "runtime_activation_added",
        "dynamic_repair_behavior_added",
        "continuity_repair_added",
    ):
        if summary.get(key) is not False:
            errors.append(f"integrity boundary violated: {key}")
    validation = {
        "artifact_type": VALIDATION_ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "generated_at": GENERATED_AT,
        "validation_status": "INVALID" if errors else "VALID",
        "integrity_summary_hash": summary.get("integrity_summary_hash", UNKNOWN),
        "expected_integrity_summary_hash": expected_hash,
        "errors": sorted(set(errors)),
        "read_only": True,
        "execution_authority_added": False,
        "orchestration_authority_added": False,
        "autonomous_continuation_added": False,
        "provider_activation_added": False,
        "continuity_repair_added": False,
    }
    validation["validation_hash"] = canonical_hash({key: value for key, value in validation.items() if key != "validation_hash"})
    return validation


def write_integrity_summary(summary: dict[str, Any], output_path: str | Path) -> dict[str, Any]:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(summary, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return {"written": True, "output_path": str(path)}


def inspect_cognition_integrity(
    *,
    input_path: str | Path | None = None,
    output_path: str | Path | None = None,
    validate: bool = False,
) -> dict[str, Any]:
    summary = build_cognition_integrity_summary(input_path=input_path)
    result = {
        "command": "aigol cognition integrity",
        "input_path": str(input_path or ""),
        "cognition_integrity_summary": summary,
        "read_only": True,
        "execution_authority_added": False,
        "orchestration_authority_added": False,
        "autonomous_cognition_added": False,
        "autonomous_continuation_added": False,
        "planning_authority_added": False,
        "provider_activation_added": False,
        "runtime_activation_added": False,
        "continuity_repair_added": False,
    }
    if validate:
        result["integrity_validation"] = validate_cognition_integrity_summary(summary)
    if output_path:
        result["output"] = write_integrity_summary(summary, output_path)
    return result


def render_cognition_integrity_summary(summary: dict[str, Any]) -> str:
    component_lines = [
        f"  {item.get('component_name')}: {item.get('status')}"
        for item in summary.get("components", [])
    ]
    return "\n".join(
        [
            "Integrity Status",
            f"  {summary.get('integrity_status')}",
            "Cognition Health",
            f"  {json.dumps(summary.get('health_summary', {}), sort_keys=True)}",
            "Components",
            *(component_lines or ["  UNKNOWN"]),
            "Replay / Lineage",
            f"  {summary.get('health_summary', {}).get('replay_lineage_health')}",
            "Semantic Continuity",
            f"  {summary.get('health_summary', {}).get('semantic_continuity_health')}",
            "Authority Boundaries",
            "  execution_authority: false",
            "  orchestration_authority: false",
            "  autonomous_continuation: false",
            "  provider_activation: false",
            "  continuity_repair: false",
            "Unknowns",
            f"  {json.dumps(summary.get('unknowns', []), sort_keys=True)}",
        ]
    )


__all__ = [
    "ARTIFACT_TYPE",
    "DEGRADED",
    "HEALTHY",
    "HEALTHY_WITH_UNKNOWN_CONTEXT",
    "INVALID",
    "SCHEMA_VERSION",
    "build_cognition_integrity_summary",
    "inspect_cognition_integrity",
    "render_cognition_integrity_summary",
    "validate_cognition_integrity_summary",
    "write_integrity_summary",
]
