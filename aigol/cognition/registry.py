"""Read-only cognition primitive registry and validator.

The registry indexes existing bounded cognition primitives for governance-safe
discoverability. It does not execute, orchestrate, dynamically load, activate,
self-register, mutate governance state, or grant authority.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

from aigol.cognition.state_envelope import GENERATED_AT, UNKNOWN

ARTIFACT_TYPE = "COGNITION_REGISTRY_V1"
VALIDATION_ARTIFACT_TYPE = "COGNITION_REGISTRY_VALIDATION_V1"
SCHEMA_VERSION = "1.0"
DEFAULT_INDEX_PATH = Path("COGNITION_PRIMITIVES_INDEX.json")

VALID = "VALID"
VALID_WITH_WARNINGS = "VALID_WITH_WARNINGS"
INVALID = "INVALID"

REQUIRED_PRIMITIVE_FIELDS = (
    "id",
    "source_files",
    "governance_role",
    "cognition_category",
    "maturity_level",
    "replay_relevance",
    "authority_classification",
    "execution_relevance",
)

FORBIDDEN_AUTHORITY_TERMS = (
    "unrestricted",
    "autonomous_execution",
    "self_modifying",
    "self-modifying",
    "orchestration_authority",
    "hidden_execution",
    "provider_routing",
    "grants_mutation_authority",
)

REQUIRED_SUMMARY_FIELDS = (
    "primitive_count",
    "strongest_existing_categories",
    "primary_missing_categories",
    "final_assessment",
)


def _canonical_copy(value: Any) -> Any:
    return deepcopy(value)


def _safe_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _load_json(path: str | Path | None) -> dict[str, Any]:
    registry_path = Path(path) if path else DEFAULT_INDEX_PATH
    try:
        parsed = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _topology(primitives: list[dict[str, Any]]) -> dict[str, Any]:
    categories: dict[str, list[str]] = {}
    authority_classes: dict[str, list[str]] = {}
    replay_roles: dict[str, list[str]] = {}
    lifecycle_roles: dict[str, list[str]] = {}
    for primitive in primitives:
        primitive_id = str(primitive.get("id", UNKNOWN))
        categories.setdefault(str(primitive.get("cognition_category", UNKNOWN)), []).append(primitive_id)
        authority_classes.setdefault(str(primitive.get("authority_classification", UNKNOWN)), []).append(primitive_id)
        replay_roles.setdefault(str(primitive.get("replay_relevance", UNKNOWN)), []).append(primitive_id)
        lifecycle_roles.setdefault(str(primitive.get("execution_relevance", UNKNOWN)), []).append(primitive_id)
    return {
        "categories": {key: sorted(values) for key, values in sorted(categories.items())},
        "authority_classes": {key: sorted(values) for key, values in sorted(authority_classes.items())},
        "replay_roles": {key: sorted(values) for key, values in sorted(replay_roles.items())},
        "lifecycle_roles": {key: sorted(values) for key, values in sorted(lifecycle_roles.items())},
    }


def _source_file_status(primitives: list[dict[str, Any]]) -> dict[str, Any]:
    missing: list[str] = []
    present: list[str] = []
    for primitive in primitives:
        for source_file in _safe_list(primitive.get("source_files")):
            if Path(str(source_file)).exists():
                present.append(str(source_file))
            else:
                missing.append(str(source_file))
    return {
        "present_count": len(sorted(set(present))),
        "missing_count": len(sorted(set(missing))),
        "missing_source_files": sorted(set(missing)),
    }


def _validation_findings(
    index: dict[str, Any],
    primitives: list[dict[str, Any]],
    *,
    require_summary: bool = True,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if index.get("artifact_type") not in {"COGNITION_PRIMITIVES_INDEX", ARTIFACT_TYPE}:
        errors.append("invalid registry source artifact_type")
    if not primitives:
        errors.append("registry contains no primitives")
    seen: set[str] = set()
    for position, primitive in enumerate(primitives):
        primitive_id = primitive.get("id")
        if not isinstance(primitive_id, str) or not primitive_id.strip():
            errors.append(f"primitive[{position}] missing id")
            primitive_id = f"primitive[{position}]"
        if primitive_id in seen:
            errors.append(f"duplicate primitive id: {primitive_id}")
        seen.add(str(primitive_id))
        for field in REQUIRED_PRIMITIVE_FIELDS:
            value = primitive.get(field)
            if field == "source_files":
                if not isinstance(value, list) or not value:
                    errors.append(f"{primitive_id} missing source_files")
            elif not isinstance(value, str) or not value.strip():
                errors.append(f"{primitive_id} missing {field}")
        authority_text = str(primitive.get("authority_classification", "")).lower()
        for forbidden in FORBIDDEN_AUTHORITY_TERMS:
            if forbidden in authority_text:
                errors.append(f"{primitive_id} forbidden authority term: {forbidden}")
    summary = index.get("summary", {})
    if require_summary:
        if not isinstance(summary, dict):
            warnings.append("summary missing")
        else:
            for field in REQUIRED_SUMMARY_FIELDS:
                if field not in summary:
                    warnings.append(f"summary missing {field}")
            if isinstance(summary.get("primitive_count"), int) and summary["primitive_count"] != len(primitives):
                warnings.append("summary primitive_count does not match primitives length")
    source_status = _source_file_status(primitives)
    if source_status["missing_source_files"]:
        warnings.append("one or more source files are missing")
    return sorted(set(errors)), sorted(set(warnings))


def _validation_status(errors: list[str], warnings: list[str]) -> str:
    if errors:
        return INVALID
    if warnings:
        return VALID_WITH_WARNINGS
    return VALID


def _hash_input(value: dict[str, Any], *hash_fields: str) -> dict[str, Any]:
    safe = _canonical_copy(value)
    for field in hash_fields:
        safe.pop(field, None)
    return safe


def build_cognition_registry(
    index: dict[str, Any] | None = None,
    *,
    generated_at: str = GENERATED_AT,
) -> dict[str, Any]:
    source = _canonical_copy(index or {})
    primitives = [item for item in _safe_list(source.get("primitives")) if isinstance(item, dict)]
    errors, warnings = _validation_findings(source, primitives)
    registry = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "generated_at": str(generated_at),
        "source_artifact_type": source.get("artifact_type", UNKNOWN),
        "source_schema_version": source.get("schema_version", UNKNOWN),
        "cognition_definition": source.get("cognition_definition", "bounded institutional reasoning inside deterministic governance"),
        "authority_statement": "This registry is read-only and grants no execution, orchestration, autonomous cognition, continuation, mutation, provider routing, runtime activation, self-registration, or hidden ingestion authority.",
        "primitive_count": len(primitives),
        "primitives": sorted(primitives, key=lambda item: str(item.get("id", ""))),
        "topology": _topology(primitives),
        "source_file_status": _source_file_status(primitives),
        "governance_boundaries": {
            "execution_authority": False,
            "orchestration_authority": False,
            "autonomous_cognition": False,
            "autonomous_continuation": False,
            "semantic_reasoning_authority": False,
            "provider_routing_authority": False,
            "dynamic_plugin_loading": False,
            "mutation_authority": False,
            "runtime_activation": False,
            "self_registration": False,
            "hidden_ingestion": False,
        },
        "validation_summary": {
            "validation_status": _validation_status(errors, warnings),
            "errors": errors,
            "warnings": warnings,
        },
        "read_only": True,
        "fail_closed": bool(errors),
    }
    registry["registry_hash"] = canonical_hash(_hash_input(registry, "registry_hash"))
    return registry


def validate_cognition_registry(registry: dict[str, Any]) -> dict[str, Any]:
    primitives = [item for item in _safe_list(registry.get("primitives")) if isinstance(item, dict)]
    errors, warnings = _validation_findings(
        {
            "artifact_type": registry.get("source_artifact_type") or registry.get("artifact_type"),
            "summary": {"primitive_count": registry.get("primitive_count")},
            "primitives": primitives,
        },
        primitives,
        require_summary=False,
    )
    expected_hash = canonical_hash(_hash_input(registry, "registry_hash"))
    actual_hash = registry.get("registry_hash")
    if actual_hash != expected_hash:
        errors.append("registry_hash mismatch")
    for key, expected in {
        "execution_authority": False,
        "orchestration_authority": False,
        "autonomous_cognition": False,
        "autonomous_continuation": False,
        "mutation_authority": False,
        "runtime_activation": False,
    }.items():
        if registry.get("governance_boundaries", {}).get(key) is not expected:
            errors.append(f"governance boundary violated: {key}")
    validation = {
        "artifact_type": VALIDATION_ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "generated_at": GENERATED_AT,
        "validation_status": _validation_status(errors, warnings),
        "registry_hash": actual_hash or UNKNOWN,
        "expected_registry_hash": expected_hash,
        "primitive_count": len(primitives),
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
        "read_only": True,
        "execution_authority_added": False,
        "orchestration_authority_added": False,
        "autonomous_continuation_added": False,
        "mutation_authority_added": False,
        "provider_routing_added": False,
        "runtime_activation_added": False,
    }
    validation["validation_hash"] = canonical_hash(_hash_input(validation, "validation_hash"))
    return validation


def load_cognition_registry_index(input_path: str | Path | None = None) -> dict[str, Any]:
    return _load_json(input_path)


def write_cognition_registry(registry: dict[str, Any], output_path: str | Path) -> dict[str, Any]:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(registry, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return {"written": True, "output_path": str(path)}


def inspect_cognition_registry(
    *,
    input_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    index = load_cognition_registry_index(input_path)
    registry = build_cognition_registry(index)
    validation = validate_cognition_registry(registry)
    result = {
        "command": "aigol cognition registry",
        "input_path": str(input_path or DEFAULT_INDEX_PATH),
        "cognition_registry": registry,
        "registry_validation": validation,
        "read_only": True,
        "execution_authority_added": False,
        "orchestration_authority_added": False,
        "autonomous_cognition_added": False,
        "autonomous_continuation_added": False,
        "mutation_authority_added": False,
        "provider_routing_added": False,
        "runtime_activation_added": False,
        "self_registration_added": False,
        "hidden_ingestion_added": False,
    }
    if output_path:
        result["output"] = write_cognition_registry(registry, output_path)
    return result


def render_cognition_registry_summary(registry: dict[str, Any], validation: dict[str, Any] | None = None) -> str:
    validation = validation or {}
    topology = registry.get("topology", {})
    categories = sorted((topology.get("categories") or {}).keys())
    lines = [
        "Registry Status",
        f"  {validation.get('validation_status', registry.get('validation_summary', {}).get('validation_status', UNKNOWN))}",
        "Primitive Index",
        f"  primitive_count: {registry.get('primitive_count')}",
        f"  registry_hash: {registry.get('registry_hash')}",
        "Cognition Categories",
        f"  {', '.join(categories)}",
        "Governance Boundaries",
        "  execution_authority: false",
        "  orchestration_authority: false",
        "  autonomous_cognition: false",
        "  autonomous_continuation: false",
        "  mutation_authority: false",
        "  provider_routing_authority: false",
        "  runtime_activation: false",
        "Registry Integrity",
        f"  errors: {json.dumps(validation.get('errors', []), sort_keys=True)}",
        f"  warnings: {json.dumps(validation.get('warnings', []), sort_keys=True)}",
    ]
    return "\n".join(lines)


__all__ = [
    "ARTIFACT_TYPE",
    "INVALID",
    "SCHEMA_VERSION",
    "VALID",
    "VALIDATION_ARTIFACT_TYPE",
    "VALID_WITH_WARNINGS",
    "build_cognition_registry",
    "inspect_cognition_registry",
    "load_cognition_registry_index",
    "render_cognition_registry_summary",
    "validate_cognition_registry",
    "write_cognition_registry",
]
