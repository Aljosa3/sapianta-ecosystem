"""Read-only semantic context audit bundle.

The bundle packages explicit semantic cognition artifacts for replay-visible
audit portability. It does not synthesize missing artifacts, reason, infer
hidden meaning, repair semantics, mutate sources, execute, dispatch, or activate
providers.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

from aigol.cognition.state_envelope import GENERATED_AT, UNKNOWN, load_cognition_artifacts

ARTIFACT_TYPE = "SEMANTIC_CONTEXT_AUDIT_BUNDLE_V1"
VALIDATION_ARTIFACT_TYPE = "SEMANTIC_CONTEXT_AUDIT_BUNDLE_VALIDATION_V1"
SCHEMA_VERSION = "1.0"

BUNDLE_COMPLETE = "BUNDLE_COMPLETE"
BUNDLE_PARTIAL = "BUNDLE_PARTIAL"
UNKNOWN_INSUFFICIENT_EVIDENCE = "UNKNOWN_INSUFFICIENT_EVIDENCE"

EXPECTED_ARTIFACT_TYPES = (
    "SEMANTIC_CONTEXT_STATE_V1",
    "BOUNDED_SEMANTIC_RELATIONSHIP_INDEX_V1",
    "SEMANTIC_BOUNDARY_PROPAGATION_V1",
    "SEMANTIC_CONTEXT_DIFF_V1",
    "COGNITION_AUTHORITY_PROPAGATION_VERIFIER_V1",
    "COGNITION_INTEGRITY_SUMMARY_V1",
    "COGNITION_LIFECYCLE_MODEL_V1",
    "COGNITION_REGISTRY_TOPOLOGY_REPORT_V1",
)

REF_FIELDS = {
    "semantic_context_refs": {"SEMANTIC_CONTEXT_STATE_V1"},
    "relationship_index_refs": {"BOUNDED_SEMANTIC_RELATIONSHIP_INDEX_V1"},
    "boundary_propagation_refs": {"SEMANTIC_BOUNDARY_PROPAGATION_V1"},
    "semantic_diff_refs": {"SEMANTIC_CONTEXT_DIFF_V1"},
    "authority_verification_refs": {"COGNITION_AUTHORITY_PROPAGATION_VERIFIER_V1"},
    "integrity_summary_refs": {"COGNITION_INTEGRITY_SUMMARY_V1"},
    "lifecycle_refs": {"COGNITION_LIFECYCLE_MODEL_V1"},
    "topology_refs": {"COGNITION_REGISTRY_TOPOLOGY_REPORT_V1"},
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
    safe.pop("bundle_hash", None)
    return safe


def _artifact_hash(artifact: dict[str, Any]) -> str:
    hashes = artifact.get("hashes", {}) if isinstance(artifact.get("hashes"), dict) else {}
    for key in (
        "semantic_context_hash",
        "relationship_index_hash",
        "propagation_hash",
        "diff_hash",
        "authority_propagation_hash",
        "integrity_summary_hash",
        "lifecycle_model_hash",
        "topology_report_hash",
        "artifact_hash",
    ):
        value = artifact.get(key, hashes.get(key))
        if isinstance(value, str) and value.strip():
            return value
    return canonical_hash(artifact)


def _artifact_ref(artifact: dict[str, Any], index: int) -> dict[str, Any]:
    return {
        "bundle_order": index,
        "artifact_type": _artifact_type(artifact),
        "artifact_hash": _artifact_hash(artifact),
        "replay_identity": str(artifact.get("replay_identity", UNKNOWN)),
        "included_explicitly": True,
    }


def _bundle_status(artifacts: list[dict[str, Any]], missing: list[str]) -> str:
    if not artifacts:
        return UNKNOWN_INSUFFICIENT_EVIDENCE
    if missing:
        return BUNDLE_PARTIAL
    return BUNDLE_COMPLETE


def build_semantic_context_audit_bundle(
    artifacts: Any = None,
    *,
    generated_at: str = GENERATED_AT,
) -> dict[str, Any]:
    safe_artifacts = _as_artifacts(artifacts)
    included = [_artifact_ref(artifact, index) for index, artifact in enumerate(safe_artifacts)]
    present_types = {ref["artifact_type"] for ref in included}
    missing = sorted(set(EXPECTED_ARTIFACT_TYPES) - present_types)
    artifact_hashes = {f"{ref['bundle_order']}:{ref['artifact_type']}": ref["artifact_hash"] for ref in included}
    refs = {
        field: [ref for ref in included if ref["artifact_type"] in expected]
        for field, expected in REF_FIELDS.items()
    }
    bundle_manifest = {
        "expected_artifact_types": list(EXPECTED_ARTIFACT_TYPES),
        "present_artifact_types": sorted(present_types),
        "missing_artifact_types": missing,
        "artifact_count": len(included),
        "source_mutation_performed": False,
        "missing_artifacts_synthesized": False,
    }
    bundle_seed = {
        "artifact_hashes": artifact_hashes,
        "bundle_manifest": bundle_manifest,
        "generated_at": str(generated_at),
    }
    bundle = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "generated_at": str(generated_at),
        "bundle_status": _bundle_status(safe_artifacts, missing),
        "bundle_id": canonical_hash(bundle_seed),
        "included_artifacts": included,
        "artifact_hashes": artifact_hashes,
        "bundle_manifest": bundle_manifest,
        "semantic_context_refs": refs["semantic_context_refs"],
        "relationship_index_refs": refs["relationship_index_refs"],
        "boundary_propagation_refs": refs["boundary_propagation_refs"],
        "semantic_diff_refs": refs["semantic_diff_refs"],
        "authority_verification_refs": refs["authority_verification_refs"],
        "integrity_summary_refs": refs["integrity_summary_refs"],
        "lifecycle_refs": refs["lifecycle_refs"],
        "topology_refs": refs["topology_refs"],
        "unknowns": missing + ([] if safe_artifacts else ["no explicit semantic cognition artifacts provided"]),
        "notes": [
            "read-only semantic audit bundling only",
            "only explicit input artifacts are included",
            "missing artifacts are UNKNOWN and are not synthesized",
            "no semantic reasoning, hidden inference, repair, ambiguity resolution, or executable graph semantics",
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
        "executable_semantic_graph_added": False,
    }
    bundle["bundle_hash"] = canonical_hash(_hash_input(bundle))
    return bundle


def validate_semantic_context_audit_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if bundle.get("artifact_type") != ARTIFACT_TYPE:
        errors.append("invalid semantic context audit bundle artifact_type")
    expected_hash = canonical_hash(_hash_input(bundle))
    if bundle.get("bundle_hash") != expected_hash:
        errors.append("bundle_hash mismatch")
    if bundle.get("bundle_manifest", {}).get("source_mutation_performed") is not False:
        errors.append("source mutation detected")
    if bundle.get("bundle_manifest", {}).get("missing_artifacts_synthesized") is not False:
        errors.append("missing artifact synthesis detected")
    for key in (
        "execution_authority_added",
        "orchestration_authority_added",
        "provider_activation_added",
        "semantic_reasoning_added",
        "hidden_inference_added",
        "semantic_repair_added",
        "ambiguity_resolution_added",
        "executable_semantic_graph_added",
    ):
        if bundle.get(key) is not False:
            errors.append(f"semantic audit bundle boundary violated: {key}")
    validation = {
        "artifact_type": VALIDATION_ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "generated_at": GENERATED_AT,
        "validation_status": "INVALID" if errors else "VALID",
        "bundle_hash": bundle.get("bundle_hash", UNKNOWN),
        "expected_bundle_hash": expected_hash,
        "errors": sorted(set(errors)),
        "read_only": True,
    }
    validation["validation_hash"] = canonical_hash({key: value for key, value in validation.items() if key != "validation_hash"})
    return validation


def write_semantic_context_audit_bundle(bundle: dict[str, Any], output_path: str | Path) -> dict[str, Any]:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(bundle, sort_keys=True, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return {"written": True, "output_path": str(path)}


def inspect_semantic_audit_bundle(
    *,
    input_path: str | Path | None = None,
    output_path: str | Path | None = None,
    artifacts: Any = None,
    validate: bool = False,
) -> dict[str, Any]:
    loaded = _as_artifacts(artifacts)
    if not loaded:
        loaded = load_cognition_artifacts(input_path)
    bundle = build_semantic_context_audit_bundle(loaded)
    result = {
        "command": "aigol cognition semantic-audit-bundle",
        "input_path": str(input_path or ""),
        "artifact_count": len(loaded),
        "semantic_context_audit_bundle": bundle,
        "read_only": True,
        "execution_authority_added": False,
        "orchestration_authority_added": False,
        "provider_activation_added": False,
        "semantic_reasoning_added": False,
        "hidden_inference_added": False,
        "semantic_repair_added": False,
    }
    if validate:
        result["semantic_audit_bundle_validation"] = validate_semantic_context_audit_bundle(bundle)
    if output_path:
        result["output"] = write_semantic_context_audit_bundle(bundle, output_path)
    return result


def render_semantic_audit_bundle_summary(bundle: dict[str, Any]) -> str:
    return "\n".join(
        [
            "Bundle Status",
            f"  {bundle.get('bundle_status')}",
            "Bundle ID",
            f"  {bundle.get('bundle_id')}",
            "Included Artifacts",
            f"  {len(bundle.get('included_artifacts', []))}",
            "Missing Artifacts",
            f"  {json.dumps(bundle.get('bundle_manifest', {}).get('missing_artifact_types', []), sort_keys=True)}",
            "Artifact Hashes",
            f"  {json.dumps(bundle.get('artifact_hashes', {}), sort_keys=True)}",
            "Governance Guarantees",
            "  semantic_reasoning: false",
            "  hidden_inference: false",
            "  execution_authority: false",
            "  provider_activation: false",
            "  executable_semantic_graph: false",
        ]
    )


__all__ = [
    "ARTIFACT_TYPE",
    "BUNDLE_COMPLETE",
    "BUNDLE_PARTIAL",
    "EXPECTED_ARTIFACT_TYPES",
    "UNKNOWN_INSUFFICIENT_EVIDENCE",
    "build_semantic_context_audit_bundle",
    "inspect_semantic_audit_bundle",
    "render_semantic_audit_bundle_summary",
    "validate_semantic_context_audit_bundle",
    "write_semantic_context_audit_bundle",
]
