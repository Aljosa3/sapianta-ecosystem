"""Read-only cognition authority propagation verifier.

The verifier checks authority continuity across replay-visible cognition
artifacts. It does not issue authority, execute, dispatch, activate providers,
repair authority, infer hidden context, or mutate evidence.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

from aigol.cognition.state_envelope import GENERATED_AT, UNKNOWN, load_cognition_artifacts

ARTIFACT_TYPE = "COGNITION_AUTHORITY_PROPAGATION_VERIFIER_V1"
VALIDATION_ARTIFACT_TYPE = "COGNITION_AUTHORITY_PROPAGATION_VALIDATION_V1"
SCHEMA_VERSION = "1.0"

AUTHORITY_STABLE = "AUTHORITY_STABLE"
AUTHORITY_STABLE_WITH_WARNINGS = "AUTHORITY_STABLE_WITH_WARNINGS"
UNKNOWN_INSUFFICIENT_EVIDENCE = "UNKNOWN_INSUFFICIENT_EVIDENCE"
AUTHORITY_PROPAGATION_RISK = "AUTHORITY_PROPAGATION_RISK"
HIDDEN_AUTHORITY_ESCALATION = "HIDDEN_AUTHORITY_ESCALATION"
INVALID_AUTHORITY_CHAIN = "INVALID_AUTHORITY_CHAIN"

AUTHORITY_FIELDS = (
    "execution_authority",
    "execution_authorized",
    "governance_authority",
    "dispatch_authorized",
    "provider_invoked",
    "provider_dispatch_authorized",
    "runtime_activation",
    "mutation_authority",
    "autonomous_continuation",
    "autonomous_continuation_authorized",
    "orchestration_authority",
)

RUNTIME_REPORT_TYPES = {
    "BOUNDED_COGNITION_STATE_ENVELOPE_V1",
    "SEMANTIC_REPLAY_CONTINUITY_CHECK_V1",
    "COGNITION_REGISTRY_V1",
    "COGNITION_REGISTRY_TOPOLOGY_REPORT_V1",
    "COGNITION_LIFECYCLE_MODEL_V1",
    "COGNITION_INTEGRITY_SUMMARY_V1",
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
    safe.pop("authority_propagation_hash", None)
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
        "execution_governance_hash",
        "governed_return_hash",
        "registry_hash",
        "topology_report_hash",
        "lifecycle_model_hash",
        "integrity_summary_hash",
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


def _authority_snapshot(artifact: dict[str, Any]) -> dict[str, Any]:
    snapshot = {"artifact_type": _artifact_type(artifact)}
    for field in AUTHORITY_FIELDS:
        if field in artifact:
            snapshot[field] = artifact[field]
    return snapshot


def _nested_true(value: Any, field_names: set[str], path: str = "") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            if key in field_names and child is True:
                findings.append(child_path)
            findings.extend(_nested_true(child, field_names, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(_nested_true(child, field_names, f"{path}[{index}]"))
    return findings


def _check_artifact(artifact: dict[str, Any]) -> tuple[list[str], list[str], list[str]]:
    artifact_type = _artifact_type(artifact)
    violations: list[str] = []
    warnings: list[str] = []
    unknowns: list[str] = []

    if artifact_type == UNKNOWN:
        unknowns.append("artifact_type")

    if artifact_type == "CHATGPT_INGRESS_ARTIFACT_V1":
        forbidden = _nested_true(
            artifact,
            {
                "execution_authority",
                "execution_authorized",
                "governance_authority",
                "dispatch_authorized",
                "provider_invoked",
                "mutation_authority",
                "autonomous_continuation",
            },
        )
        violations.extend(f"ChatGPT semantic input gained authority: {field}" for field in forbidden)

    if artifact_type == "HUMAN_APPROVAL_GATE_V1":
        if artifact.get("execution_authorized") is True or artifact.get("execution_performed") is True:
            warnings.append("human approval treated as execution authority")
        if artifact.get("dispatch_authorized") is True:
            warnings.append("human approval treated as dispatch authorization")

    if artifact_type == "EXPLICIT_DISPATCH_AUTHORIZATION_V1":
        if artifact.get("execution_authorized") is True or artifact.get("execution_performed") is True:
            warnings.append("dispatch authorization treated as execution")
        if artifact.get("provider_invoked") is True or artifact.get("provider_dispatch_performed") is True:
            warnings.append("dispatch authorization treated as provider invocation")

    if artifact_type.startswith("REFLECTION") or "reflection_id" in artifact:
        forbidden = _nested_true(
            artifact,
            {"execution_authority", "execution_authorized", "execution_performed", "provider_invoked"},
        )
        violations.extend(f"reflection gained execution authority: {field}" for field in forbidden)

    if artifact_type in RUNTIME_REPORT_TYPES:
        forbidden = _nested_true(
            artifact,
            {
                "execution_authority",
                "execution_authorized",
                "runtime_activation",
                "provider_invoked",
                "provider_activation",
                "provider_routing",
                "mutation_authority",
                "autonomous_continuation",
            },
        )
        violations.extend(f"observability report gained runtime authority: {field}" for field in forbidden)

    if artifact.get("provider_invoked") is True and artifact_type not in {"CONTROLLED_EXECUTION_HANDOFF_V1"}:
        warnings.append(f"provider authority outside bounded execution boundary: {artifact_type}")

    for field in ("mutation_authority", "autonomous_continuation", "autonomous_continuation_authorized"):
        if artifact.get(field) is True:
            violations.append(f"{field} became true")

    return sorted(set(violations)), sorted(set(warnings)), sorted(set(unknowns))


def _authority_chain(artifacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "order": index,
            "artifact_type": _artifact_type(artifact),
            "authority_snapshot": _authority_snapshot(artifact),
            "authority_issued_by_verifier": False,
        }
        for index, artifact in enumerate(artifacts)
    ]


def _authority_transitions(artifacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    transitions: list[dict[str, Any]] = []
    for index, artifact in enumerate(artifacts):
        artifact_type = _artifact_type(artifact)
        if artifact_type == "HUMAN_APPROVAL_GATE_V1":
            transitions.append(
                {
                    "order": index,
                    "transition": "human approval evidence",
                    "dispatch_authorization_created": False,
                    "execution_authority_created": False,
                }
            )
        if artifact_type == "EXPLICIT_DISPATCH_AUTHORIZATION_V1":
            transitions.append(
                {
                    "order": index,
                    "transition": "explicit dispatch authorization evidence",
                    "dispatch_authorization_created": artifact.get("dispatch_authorized") is True,
                    "execution_authority_created": False,
                }
            )
        if artifact_type == "CONTROLLED_EXECUTION_HANDOFF_V1":
            transitions.append(
                {
                    "order": index,
                    "transition": "bounded execution boundary evidence",
                    "dispatch_authorization_required": True,
                    "provider_authority_boundary": artifact.get("provider_invoked") is True,
                    "autonomous_continuation_created": False,
                }
            )
    return transitions


def _status(artifacts: list[dict[str, Any]], violations: list[str], warnings: list[str], unknowns: list[str]) -> str:
    if not artifacts:
        return UNKNOWN_INSUFFICIENT_EVIDENCE
    if any("ChatGPT semantic input gained authority" in item or "reflection gained execution authority" in item or "observability report gained runtime authority" in item for item in violations):
        return HIDDEN_AUTHORITY_ESCALATION
    if violations:
        return INVALID_AUTHORITY_CHAIN
    if warnings:
        return AUTHORITY_PROPAGATION_RISK
    if unknowns:
        return AUTHORITY_STABLE_WITH_WARNINGS
    return AUTHORITY_STABLE


def build_authority_propagation_verifier(
    artifacts: Any = None,
    *,
    generated_at: str = GENERATED_AT,
) -> dict[str, Any]:
    safe_artifacts = _as_artifacts(artifacts)
    violations: list[str] = []
    warnings: list[str] = []
    unknowns: list[str] = []
    for artifact in safe_artifacts:
        artifact_violations, artifact_warnings, artifact_unknowns = _check_artifact(artifact)
        violations.extend(artifact_violations)
        warnings.extend(artifact_warnings)
        unknowns.extend(artifact_unknowns)
    if not safe_artifacts:
        unknowns.append("no replay-visible authority evidence provided")
    result = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "generated_at": str(generated_at),
        "authority_propagation_status": _status(safe_artifacts, violations, warnings, unknowns),
        "authority_chain": _authority_chain(safe_artifacts),
        "authority_transitions": _authority_transitions(safe_artifacts),
        "violations": sorted(set(violations)),
        "warnings": sorted(set(warnings)),
        "unknowns": sorted(set(unknowns)),
        "evidence_refs": _evidence_refs(safe_artifacts),
        "governance_guarantees": {
            "execution_authority_issued": False,
            "orchestration_authority_issued": False,
            "autonomous_cognition_issued": False,
            "planning_authority_issued": False,
            "semantic_reasoning_issued": False,
            "runtime_activation_issued": False,
            "provider_routing_issued": False,
            "hidden_inference_performed": False,
            "authority_repair_performed": False,
            "mutation_authority_issued": False,
        },
        "read_only": True,
        "execution_authority_added": False,
        "orchestration_authority_added": False,
        "autonomous_cognition_added": False,
        "planning_authority_added": False,
        "semantic_reasoning_added": False,
        "runtime_activation_added": False,
        "provider_routing_added": False,
        "hidden_inference_added": False,
        "authority_issuance_added": False,
        "authority_repair_added": False,
        "mutation_authority_added": False,
    }
    result["authority_propagation_hash"] = canonical_hash(_hash_input(result))
    return result


def validate_authority_propagation_verifier(artifact: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if artifact.get("artifact_type") != ARTIFACT_TYPE:
        errors.append("invalid authority propagation artifact_type")
    expected_hash = canonical_hash(_hash_input(artifact))
    if artifact.get("authority_propagation_hash") != expected_hash:
        errors.append("authority_propagation_hash mismatch")
    for key in (
        "execution_authority_added",
        "orchestration_authority_added",
        "autonomous_cognition_added",
        "provider_routing_added",
        "runtime_activation_added",
        "authority_issuance_added",
        "authority_repair_added",
        "mutation_authority_added",
    ):
        if artifact.get(key) is not False:
            errors.append(f"authority verifier boundary violated: {key}")
    validation = {
        "artifact_type": VALIDATION_ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "generated_at": GENERATED_AT,
        "validation_status": "INVALID" if errors else "VALID",
        "authority_propagation_hash": artifact.get("authority_propagation_hash", UNKNOWN),
        "expected_authority_propagation_hash": expected_hash,
        "errors": sorted(set(errors)),
        "read_only": True,
    }
    validation["validation_hash"] = canonical_hash({key: value for key, value in validation.items() if key != "validation_hash"})
    return validation


def write_authority_propagation_verifier(artifact: dict[str, Any], output_path: str | Path) -> dict[str, Any]:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(artifact, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return {"written": True, "output_path": str(path)}


def inspect_authority_propagation(
    *,
    input_path: str | Path | None = None,
    output_path: str | Path | None = None,
    artifacts: Any = None,
    validate: bool = False,
) -> dict[str, Any]:
    loaded = _as_artifacts(artifacts)
    if not loaded:
        loaded = load_cognition_artifacts(input_path)
    verifier = build_authority_propagation_verifier(loaded)
    result = {
        "command": "aigol cognition authority",
        "input_path": str(input_path or ""),
        "artifact_count": len(loaded),
        "authority_propagation_verifier": verifier,
        "read_only": True,
        "execution_authority_added": False,
        "orchestration_authority_added": False,
        "autonomous_cognition_added": False,
        "provider_activation_added": False,
        "authority_issuance_added": False,
        "authority_repair_added": False,
        "mutation_authority_added": False,
    }
    if validate:
        result["authority_validation"] = validate_authority_propagation_verifier(verifier)
    if output_path:
        result["output"] = write_authority_propagation_verifier(verifier, output_path)
    return result


def render_authority_propagation_summary(artifact: dict[str, Any]) -> str:
    transition_lines = [
        f"  {item.get('transition')}: execution_authority_created={item.get('execution_authority_created', False)}"
        for item in artifact.get("authority_transitions", [])
    ]
    return "\n".join(
        [
            "Authority Propagation Status",
            f"  {artifact.get('authority_propagation_status')}",
            "Authority Chain",
            f"  {len(artifact.get('authority_chain', []))} artifacts",
            "Authority Transitions",
            *(transition_lines or ["  UNKNOWN"]),
            "Violations",
            f"  {json.dumps(artifact.get('violations', []), sort_keys=True)}",
            "Warnings",
            f"  {json.dumps(artifact.get('warnings', []), sort_keys=True)}",
            "Unknowns",
            f"  {json.dumps(artifact.get('unknowns', []), sort_keys=True)}",
            "Governance Guarantees",
            "  execution_authority_issued: false",
            "  orchestration_authority_issued: false",
            "  provider_routing_issued: false",
            "  authority_repair_performed: false",
        ]
    )


__all__ = [
    "ARTIFACT_TYPE",
    "AUTHORITY_PROPAGATION_RISK",
    "AUTHORITY_STABLE",
    "AUTHORITY_STABLE_WITH_WARNINGS",
    "HIDDEN_AUTHORITY_ESCALATION",
    "INVALID_AUTHORITY_CHAIN",
    "UNKNOWN_INSUFFICIENT_EVIDENCE",
    "build_authority_propagation_verifier",
    "inspect_authority_propagation",
    "render_authority_propagation_summary",
    "validate_authority_propagation_verifier",
    "write_authority_propagation_verifier",
]
