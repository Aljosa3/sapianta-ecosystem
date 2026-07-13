"""Deterministic, non-authoritative Platform Change Impact Analysis."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_certification_registry import (
    PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY_VERSION,
    list_platform_capability_certifications,
)
from aigol.runtime.platform_change_normalization_runtime import (
    FAILED_CLOSED as NORMALIZATION_FAILED_CLOSED,
    NORMALIZED_CHANGE_ARTIFACT_V1,
    validate_normalized_change_artifact,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


PLATFORM_CHANGE_IMPACT_ANALYSIS_RUNTIME_VERSION = "G27_05_PLATFORM_CHANGE_IMPACT_ANALYSIS_RUNTIME_V1"
PLATFORM_CHANGE_IMPACT_ARTIFACT_V1 = "PLATFORM_CHANGE_IMPACT_ARTIFACT_V1"
CHANGE_IMPACT_ANALYZED = "CHANGE_IMPACT_ANALYZED"
CHANGE_IMPACT_ANALYZED_WITH_UNRESOLVED_MAPPINGS = "CHANGE_IMPACT_ANALYZED_WITH_UNRESOLVED_MAPPINGS"
FAILED_CLOSED = "FAILED_CLOSED"
REPLAY_STEP = "platform_change_impact_recorded"

L0_EXACT_PATHS = frozenset(
    {
        "docs/governance/CONSTITUTIONAL_ARCHITECTURE_SPEC_V1.md",
        "docs/governance/CANONICAL_LAYER_MODEL.md",
        "docs/governance/CONSTITUTIONAL_INVARIANTS.md",
        "docs/governance/GOVERNANCE_ENFORCEMENT_HIERARCHY.md",
        "docs/governance/GOVERNANCE_LINEAGE_MODEL.md",
        "docs/governance/STABLE_SUBSTRATE_DECLARATION_V1.md",
        "scripts/check_layer_freeze.py",
        "sapianta_system/governance/phases/LAYER_0_FREEZE.yaml",
    }
)

AUTHORITY_FLAGS = {
    "authorizes_execution": False,
    "authorizes_dispatch": False,
    "authorizes_worker_invocation": False,
    "authorizes_provider_invocation": False,
    "authorizes_filesystem_mutation": False,
    "authorizes_governance_mutation": False,
    "authorizes_replay_mutation": False,
    "authorizes_certification": False,
    "plans_validation": False,
    "selects_tests": False,
    "executes_validation": False,
}

GOVERNANCE_SURFACES_BY_LAYER = {
    "L0": ("SYSTEM_CONSTITUTION", "LAYER_0_FREEZE", "ARCHITECTURE_GUARDIAN"),
    "L1": ("CANONICAL_ARTIFACT_STABILITY", "MUTATION_VALIDATOR"),
    "L2": ("DECISION_SPINE_GOVERNANCE", "MUTATION_GUARD"),
    "L3": ("GOVERNANCE_SYSTEM", "DEV_GOVERNANCE_GATE"),
    "L4": ("BOUNDED_DEVELOPMENT_GOVERNANCE", "MUTATION_GUARD"),
}

REPLAY_SURFACES_BY_LAYER = {
    "L0": ("CONSTITUTIONAL_REPLAY_INTEGRITY",),
    "L1": ("CANONICAL_ARTIFACT_REPLAY_IDENTITY", "REPLAY_HASH_VERIFICATION"),
    "L2": ("DECISION_SPINE_REPLAY_LINEAGE", "REPLAY_RECONSTRUCTION"),
    "L3": ("GOVERNANCE_EVIDENCE_REPLAY_LINEAGE",),
    "L4": ("CHANGE_EVIDENCE_REPLAY_LINEAGE",),
}


def analyze_platform_change_impact(
    *,
    impact_analysis_id: str,
    normalized_change_artifact: dict[str, Any],
    normalized_change_reference: str,
    normalized_change_hash: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Analyze one canonical normalized change without planning validation."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        analysis_id = _require_string(impact_analysis_id, "impact_analysis_id")
        source_reference = _require_string(normalized_change_reference, "normalized_change_reference")
        source_hash = _require_hash(normalized_change_hash, "normalized_change_hash")
        source = validate_normalized_change_artifact(normalized_change_artifact)
        _validate_source_binding(source, source_reference, source_hash)
        registry = list_platform_capability_certifications()
        impact_entries = [_impact_entry(entry, registry) for entry in source["change_entries"]]
        affected_capabilities = _affected_capabilities(impact_entries, registry)
        affected_layers = _affected_layers(impact_entries)
        governance_surfaces = _governance_surfaces(impact_entries)
        replay_surfaces = _replay_surfaces(impact_entries, affected_capabilities)
        certification_surfaces = _certification_surfaces(affected_capabilities)
        unresolved = _unresolved_mappings(source, impact_entries)
        status = CHANGE_IMPACT_ANALYZED_WITH_UNRESOLVED_MAPPINGS if unresolved else CHANGE_IMPACT_ANALYZED
        artifact = _impact_artifact(
            impact_analysis_id=analysis_id,
            normalized_change_reference=source_reference,
            normalized_change_hash=source_hash,
            normalized_change_artifact_hash=source["artifact_hash"],
            impact_entries=impact_entries,
            affected_capabilities=affected_capabilities,
            affected_layers=affected_layers,
            governance_surfaces=governance_surfaces,
            replay_surfaces=replay_surfaces,
            certification_surfaces=certification_surfaces,
            unresolved_mappings=unresolved,
            impact_status=status,
            created_at=_require_string(created_at, "created_at"),
            failure_reason=None,
        )
    except Exception as exc:
        artifact = _failed_artifact(
            impact_analysis_id=impact_analysis_id,
            normalized_change_artifact=normalized_change_artifact,
            normalized_change_reference=normalized_change_reference,
            normalized_change_hash=normalized_change_hash,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
    _persist_if_possible(replay_path, artifact)
    return _capture(artifact, replay_path)


def reconstruct_platform_change_impact_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and verify one Platform Change Impact replay artifact."""

    replay_path = Path(replay_dir)
    wrapper = load_json(replay_path / f"000_{REPLAY_STEP}.json")
    if wrapper.get("replay_index") != 0 or wrapper.get("replay_step") != REPLAY_STEP:
        raise FailClosedRuntimeError("platform change impact replay ordering mismatch")
    _verify_hash(wrapper, "replay_hash", "platform change impact replay hash mismatch")
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("platform change impact replay artifact must be a JSON object")
    _verify_impact_artifact(artifact)
    return {
        "impact_analysis_id": artifact["impact_analysis_id"],
        "impact_status": artifact["impact_status"],
        "normalized_change_reference": artifact["normalized_change_reference"],
        "normalized_change_hash": artifact["normalized_change_hash"],
        "impact_entries": deepcopy(artifact["impact_entries"]),
        "affected_capabilities": deepcopy(artifact["affected_capabilities"]),
        "affected_constitutional_layers": deepcopy(artifact["affected_constitutional_layers"]),
        "affected_governance_surfaces": deepcopy(artifact["affected_governance_surfaces"]),
        "affected_replay_surfaces": deepcopy(artifact["affected_replay_surfaces"]),
        "affected_certification_surfaces": deepcopy(artifact["affected_certification_surfaces"]),
        "unresolved_mappings": deepcopy(artifact["unresolved_mappings"]),
        "platform_change_impact_hash": artifact["platform_change_impact_hash"],
        "artifact_hash": artifact["artifact_hash"],
        "replay_visible": True,
        "fail_closed": artifact["impact_status"] == FAILED_CLOSED,
        "failure_reason": artifact["failure_reason"],
        "authority_flags": deepcopy(artifact["authority_flags"]),
        "replay_hash": wrapper["replay_hash"],
    }


def validate_platform_change_impact_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    """Validate one canonical Platform Change Impact artifact."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("platform change impact artifact must be a JSON object")
    candidate = deepcopy(artifact)
    _verify_impact_artifact(candidate)
    return candidate


def _validate_source_binding(source: dict[str, Any], source_reference: str, source_hash: str) -> None:
    if source.get("artifact_type") != NORMALIZED_CHANGE_ARTIFACT_V1:
        raise FailClosedRuntimeError("platform change impact failed closed: normalized change artifact required")
    if source.get("normalization_status") == NORMALIZATION_FAILED_CLOSED:
        raise FailClosedRuntimeError("platform change impact failed closed: source normalization failed closed")
    if source.get("normalization_id") != source_reference:
        raise FailClosedRuntimeError("platform change impact failed closed: normalized change reference mismatch")
    if source.get("normalized_change_hash") != source_hash:
        raise FailClosedRuntimeError("platform change impact failed closed: normalized change hash mismatch")


def _impact_entry(change_entry: dict[str, Any], registry: list[dict[str, Any]]) -> dict[str, Any]:
    path = _require_string(change_entry.get("target_path"), "target_path")
    matches = _capability_matches(path, registry)
    if not matches:
        raise FailClosedRuntimeError(f"platform change impact failed closed: no capability mapping for {path}")
    if len(matches) != 1:
        raise FailClosedRuntimeError(f"platform change impact failed closed: ambiguous capability mapping for {path}")
    layer, rule = _constitutional_layer(path, _require_string(change_entry.get("artifact_type"), "artifact_type"))
    capability = matches[0]
    entry = {
        "change_entry_reference": change_entry["source_entry_reference"],
        "change_entry_hash": change_entry["change_entry_hash"],
        "target_path": path,
        "operation_type": change_entry["operation_type"],
        "artifact_type": change_entry["artifact_type"],
        "capability_identifier": capability["capability_identifier"],
        "capability_owner": capability["capability_owner"],
        "architectural_owner": capability["architectural_owner"],
        "implementation_owner": capability["implementation_owner"],
        "capability_mapping_source": _capability_mapping_source(path, capability),
        "constitutional_layer": layer,
        "constitutional_layer_mapping_rule": rule,
        "unresolved_mappings": deepcopy(change_entry["unresolved_mappings"]),
    }
    entry["impact_entry_hash"] = replay_hash(entry)
    return entry


def _capability_matches(path: str, registry: list[dict[str, Any]]) -> list[dict[str, Any]]:
    matches = []
    for record in registry:
        implementation_path = _implementation_owner_path(record.get("implementation_owner"))
        evidence_paths = tuple(str(item) for item in record.get("certification_evidence", ()))
        if path == implementation_path or path in evidence_paths:
            matches.append(deepcopy(record))
    return sorted(matches, key=lambda item: item["capability_identifier"])


def _implementation_owner_path(value: Any) -> str:
    owner = _require_string(value, "implementation_owner")
    return owner.replace(".", "/") + ".py"


def _capability_mapping_source(path: str, capability: dict[str, Any]) -> str:
    if path == _implementation_owner_path(capability["implementation_owner"]):
        return "PLATFORM_CAPABILITY_REGISTRY_IMPLEMENTATION_OWNER"
    return "PLATFORM_CAPABILITY_REGISTRY_CERTIFICATION_EVIDENCE"


def _constitutional_layer(path: str, artifact_type: str) -> tuple[str, str]:
    if path in L0_EXACT_PATHS or path.startswith("governance/phases/LAYER_0_"):
        return "L0", "CANONICAL_L0_PATH"
    if path.startswith(".github/governance/manifests/") or any(
        token in artifact_type for token in ("SCHEMA", "CANONICAL_ARTIFACT_DEFINITION", "LEDGER_DEFINITION")
    ):
        return "L1", "CANONICAL_ARTIFACT_DEFINITION"
    if path.startswith(("docs/governance/", ".github/governance/", "runtime/governance/")):
        return "L3", "GOVERNANCE_SYSTEM_PATH"
    if path.startswith(("aigol/runtime/", "runtime/", "aigol/cli/", "sapianta_bridge/protocol/")):
        return "L2", "DETERMINISTIC_RUNTIME_DECISION_PATH"
    if path.startswith(("tests/", "research/", "docs/product_lifecycle/", "scripts/", "web/", "mobile/")):
        return "L4", "BOUNDED_DEVELOPMENT_OR_RESEARCH_PATH"
    raise FailClosedRuntimeError(f"platform change impact failed closed: unsupported constitutional mapping for {path}")


def _affected_capabilities(
    impact_entries: list[dict[str, Any]], registry: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    by_id = {record["capability_identifier"]: record for record in registry}
    paths_by_id: dict[str, set[str]] = {}
    for entry in impact_entries:
        paths_by_id.setdefault(entry["capability_identifier"], set()).add(entry["target_path"])
    return [
        {
            "capability_identifier": capability_id,
            "capability_owner": by_id[capability_id]["capability_owner"],
            "architectural_owner": by_id[capability_id]["architectural_owner"],
            "implementation_owner": by_id[capability_id]["implementation_owner"],
            "certification_status": by_id[capability_id]["certification_status"],
            "certification_scope": by_id[capability_id]["certification_scope"],
            "certification_evidence": list(by_id[capability_id]["certification_evidence"]),
            "certification_record_hash": by_id[capability_id]["certification_record_hash"],
            "affected_paths": sorted(paths_by_id[capability_id]),
        }
        for capability_id in sorted(paths_by_id)
    ]


def _affected_layers(impact_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    paths_by_layer: dict[str, set[str]] = {}
    for entry in impact_entries:
        paths_by_layer.setdefault(entry["constitutional_layer"], set()).add(entry["target_path"])
    return [
        {
            "constitutional_layer": layer,
            "affected_paths": sorted(paths_by_layer[layer]),
            "mapping_authority": "CANONICAL_LAYER_MODEL",
        }
        for layer in sorted(paths_by_layer)
    ]


def _governance_surfaces(impact_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    surfaces: dict[str, set[str]] = {}
    for entry in impact_entries:
        for surface in GOVERNANCE_SURFACES_BY_LAYER[entry["constitutional_layer"]]:
            surfaces.setdefault(surface, set()).add(entry["target_path"])
    return [
        {"surface_id": surface, "surface_owner": "GOVERNANCE", "affected_paths": sorted(surfaces[surface])}
        for surface in sorted(surfaces)
    ]


def _replay_surfaces(
    impact_entries: list[dict[str, Any]], affected_capabilities: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    surfaces: dict[str, set[str]] = {}
    for entry in impact_entries:
        for surface in REPLAY_SURFACES_BY_LAYER[entry["constitutional_layer"]]:
            surfaces.setdefault(surface, set()).add(entry["target_path"])
    for capability in affected_capabilities:
        if "REPLAY" in capability["capability_owner"] or "REPLAY" in capability["capability_identifier"]:
            surfaces.setdefault("REPLAY_OWNED_CAPABILITY", set()).update(capability["affected_paths"])
    return [
        {"surface_id": surface, "surface_owner": "PLATFORM_CORE_REPLAY", "affected_paths": sorted(surfaces[surface])}
        for surface in sorted(surfaces)
    ]


def _certification_surfaces(affected_capabilities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    surfaces = [
        {
            "surface_id": "PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY",
            "surface_owner": "PLATFORM_CORE_CERTIFICATION",
            "affected_capabilities": sorted(item["capability_identifier"] for item in affected_capabilities),
            "certification_registry_version": PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY_VERSION,
        }
    ]
    surfaces.extend(
        {
            "surface_id": f"CAPABILITY_CERTIFICATION:{item['capability_identifier']}",
            "surface_owner": "PLATFORM_CORE_CERTIFICATION",
            "affected_capabilities": [item["capability_identifier"]],
            "certification_evidence": deepcopy(item["certification_evidence"]),
        }
        for item in affected_capabilities
    )
    return sorted(surfaces, key=lambda item: item["surface_id"])


def _unresolved_mappings(
    source: dict[str, Any], impact_entries: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    affected_paths = {entry["target_path"] for entry in impact_entries}
    unresolved = []
    for item in source["unresolved_mappings"]:
        if not isinstance(item, dict) or item.get("target_path") not in affected_paths:
            raise FailClosedRuntimeError("platform change impact failed closed: unresolved source mapping is invalid")
        unresolved.append({**deepcopy(item), "mapping_stage": "CHANGE_NORMALIZATION"})
    return sorted(
        unresolved,
        key=lambda item: (item["target_path"], item["field"], item["reason"], item["mapping_stage"]),
    )


def _impact_artifact(
    *,
    impact_analysis_id: str,
    normalized_change_reference: str,
    normalized_change_hash: str,
    normalized_change_artifact_hash: str,
    impact_entries: list[dict[str, Any]],
    affected_capabilities: list[dict[str, Any]],
    affected_layers: list[dict[str, Any]],
    governance_surfaces: list[dict[str, Any]],
    replay_surfaces: list[dict[str, Any]],
    certification_surfaces: list[dict[str, Any]],
    unresolved_mappings: list[dict[str, Any]],
    impact_status: str,
    created_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": PLATFORM_CHANGE_IMPACT_ARTIFACT_V1,
        "runtime_version": PLATFORM_CHANGE_IMPACT_ANALYSIS_RUNTIME_VERSION,
        "impact_analysis_id": impact_analysis_id,
        "impact_status": impact_status,
        "normalized_change_artifact_type": NORMALIZED_CHANGE_ARTIFACT_V1,
        "normalized_change_reference": normalized_change_reference,
        "normalized_change_hash": normalized_change_hash,
        "normalized_change_artifact_hash": normalized_change_artifact_hash,
        "impact_entries": deepcopy(impact_entries),
        "impact_entry_count": len(impact_entries),
        "affected_capabilities": deepcopy(affected_capabilities),
        "affected_capability_count": len(affected_capabilities),
        "affected_constitutional_layers": deepcopy(affected_layers),
        "affected_constitutional_layer_count": len(affected_layers),
        "affected_governance_surfaces": deepcopy(governance_surfaces),
        "affected_replay_surfaces": deepcopy(replay_surfaces),
        "affected_certification_surfaces": deepcopy(certification_surfaces),
        "unresolved_mappings": deepcopy(unresolved_mappings),
        "unresolved_mapping_count": len(unresolved_mappings),
        "mapping_policy": {
            "capability_mapping": "EXACT_CERTIFICATION_REGISTRY_OWNER_OR_EVIDENCE_PATH",
            "constitutional_mapping": "CANONICAL_L0_L4_PATH_AND_ARTIFACT_POLICY",
            "ambiguous_mapping_fails_closed": True,
            "unsupported_mapping_fails_closed": True,
            "deterministic_sorting": True,
        },
        "created_at": created_at,
        "replay_visible": True,
        "read_only": True,
        "non_authoritative": True,
        "impact_analysis_performed": impact_status != FAILED_CLOSED,
        "validation_planned": False,
        "tests_selected": False,
        "validation_executed": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_authorized": False,
        "certification_performed": False,
        "repository_mutated": False,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "failure_reason": failure_reason,
    }
    artifact["platform_change_impact_hash"] = _impact_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_artifact(
    *,
    impact_analysis_id: Any,
    normalized_change_artifact: Any,
    normalized_change_reference: Any,
    normalized_change_hash: Any,
    created_at: Any,
    failure_reason: str,
) -> dict[str, Any]:
    source_artifact_hash = (
        normalized_change_artifact.get("artifact_hash")
        if isinstance(normalized_change_artifact, dict)
        else None
    )
    return _impact_artifact(
        impact_analysis_id=_safe_string(impact_analysis_id),
        normalized_change_reference=_safe_string(normalized_change_reference),
        normalized_change_hash=_safe_hash(normalized_change_hash),
        normalized_change_artifact_hash=_safe_hash(source_artifact_hash),
        impact_entries=[],
        affected_capabilities=[],
        affected_layers=[],
        governance_surfaces=[],
        replay_surfaces=[],
        certification_surfaces=[],
        unresolved_mappings=[],
        impact_status=FAILED_CLOSED,
        created_at=_safe_string(created_at),
        failure_reason=failure_reason,
    )


def _verify_impact_artifact(artifact: dict[str, Any]) -> None:
    if artifact.get("artifact_type") != PLATFORM_CHANGE_IMPACT_ARTIFACT_V1:
        raise FailClosedRuntimeError("platform change impact artifact type mismatch")
    _verify_hash(artifact, "artifact_hash", "platform change impact artifact hash mismatch")
    if artifact.get("platform_change_impact_hash") != _impact_hash(artifact):
        raise FailClosedRuntimeError("platform change impact hash mismatch")
    if artifact.get("replay_visible") is not True or artifact.get("read_only") is not True:
        raise FailClosedRuntimeError("platform change impact artifact must be replay-visible and read-only")
    if artifact.get("non_authoritative") is not True:
        raise FailClosedRuntimeError("platform change impact artifact must be non-authoritative")
    if any(value is not False for value in artifact.get("authority_flags", {}).values()):
        raise FailClosedRuntimeError("platform change impact artifact cannot grant authority")
    status = artifact.get("impact_status")
    if status not in {CHANGE_IMPACT_ANALYZED, CHANGE_IMPACT_ANALYZED_WITH_UNRESOLVED_MAPPINGS, FAILED_CLOSED}:
        raise FailClosedRuntimeError("platform change impact status is invalid")
    entries = artifact.get("impact_entries")
    unresolved = artifact.get("unresolved_mappings")
    if not isinstance(entries, list) or artifact.get("impact_entry_count") != len(entries):
        raise FailClosedRuntimeError("platform change impact entry count mismatch")
    if not isinstance(unresolved, list) or artifact.get("unresolved_mapping_count") != len(unresolved):
        raise FailClosedRuntimeError("platform change impact unresolved count mismatch")
    for entry in entries:
        if not isinstance(entry, dict):
            raise FailClosedRuntimeError("platform change impact entry must be a JSON object")
        _verify_hash(entry, "impact_entry_hash", "platform change impact entry hash mismatch")
    if status == FAILED_CLOSED and entries:
        raise FailClosedRuntimeError("failed platform change impact cannot contain entries")
    if status != FAILED_CLOSED and not entries:
        raise FailClosedRuntimeError("successful platform change impact requires entries")
    if status == CHANGE_IMPACT_ANALYZED and unresolved:
        raise FailClosedRuntimeError("platform change impact status omits unresolved mappings")
    if status == CHANGE_IMPACT_ANALYZED_WITH_UNRESOLVED_MAPPINGS and not unresolved:
        raise FailClosedRuntimeError("platform change impact unresolved status requires mappings")


def _impact_hash(artifact: dict[str, Any]) -> str:
    return replay_hash(
        {
            "normalized_change_artifact_type": artifact["normalized_change_artifact_type"],
            "normalized_change_reference": artifact["normalized_change_reference"],
            "normalized_change_hash": artifact["normalized_change_hash"],
            "normalized_change_artifact_hash": artifact["normalized_change_artifact_hash"],
            "impact_entries": artifact["impact_entries"],
            "affected_capabilities": artifact["affected_capabilities"],
            "affected_constitutional_layers": artifact["affected_constitutional_layers"],
            "affected_governance_surfaces": artifact["affected_governance_surfaces"],
            "affected_replay_surfaces": artifact["affected_replay_surfaces"],
            "affected_certification_surfaces": artifact["affected_certification_surfaces"],
            "unresolved_mappings": artifact["unresolved_mappings"],
            "impact_status": artifact["impact_status"],
            "mapping_policy": artifact["mapping_policy"],
            "authority_flags": artifact["authority_flags"],
            "failure_reason": artifact["failure_reason"],
        }
    )


def _capture(artifact: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "runtime_version": PLATFORM_CHANGE_IMPACT_ANALYSIS_RUNTIME_VERSION,
        "platform_change_impact_artifact": deepcopy(artifact),
        "impact_analysis_id": artifact["impact_analysis_id"],
        "impact_status": artifact["impact_status"],
        "platform_change_impact_hash": artifact["platform_change_impact_hash"],
        "platform_change_impact_replay_reference": str(replay_path),
        "affected_capabilities": deepcopy(artifact["affected_capabilities"]),
        "affected_constitutional_layers": deepcopy(artifact["affected_constitutional_layers"]),
        "affected_governance_surfaces": deepcopy(artifact["affected_governance_surfaces"]),
        "affected_replay_surfaces": deepcopy(artifact["affected_replay_surfaces"]),
        "affected_certification_surfaces": deepcopy(artifact["affected_certification_surfaces"]),
        "unresolved_mappings": deepcopy(artifact["unresolved_mappings"]),
        "fail_closed": artifact["impact_status"] == FAILED_CLOSED,
        "failure_reason": artifact["failure_reason"],
        "validation_planned": False,
        "tests_selected": False,
        "validation_executed": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_authorized": False,
        "certification_performed": False,
        "repository_mutated": False,
    }
    capture["capture_hash"] = replay_hash(capture)
    return capture


def _persist_if_possible(replay_path: Path, artifact: dict[str, Any]) -> None:
    try:
        wrapper = {"replay_index": 0, "replay_step": REPLAY_STEP, "artifact": deepcopy(artifact)}
        wrapper["replay_hash"] = replay_hash(wrapper)
        write_json_immutable(replay_path / f"000_{REPLAY_STEP}.json", wrapper)
    except Exception:
        return


def _ensure_replay_available(replay_path: Path) -> None:
    if (replay_path / f"000_{REPLAY_STEP}.json").exists():
        raise FailClosedRuntimeError("platform change impact failed closed: replay artifact already exists")


def _verify_hash(value: dict[str, Any], field: str, message: str) -> None:
    actual = value.get(field)
    if not isinstance(actual, str) or not actual.startswith("sha256:"):
        raise FailClosedRuntimeError(message)
    expected = deepcopy(value)
    expected.pop(field, None)
    if replay_hash(expected) != actual:
        raise FailClosedRuntimeError(message)


def _safe_hash(value: Any) -> str:
    return value if isinstance(value, str) and value.startswith("sha256:") else replay_hash({"unverified": True})


def _safe_string(value: Any) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else "UNKNOWN"


def _require_hash(value: Any, field: str) -> str:
    text = _require_string(value, field)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(f"platform change impact failed closed: {field} must be a sha256 hash")
    return text


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"platform change impact failed closed: {field} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return f"platform change impact failed closed: {exc}" if str(exc) else "platform change impact failed closed"
