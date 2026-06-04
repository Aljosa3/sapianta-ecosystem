"""Registry-driven executable domain bundle resolution for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_DOMAIN_BUNDLE_REGISTRY_RUNTIME_VERSION = "AIGOL_DOMAIN_BUNDLE_REGISTRY_RUNTIME_V1"
DOMAIN_BUNDLE_REGISTRY_VERSION = "AIGOL_DOMAIN_BUNDLE_REGISTRY_V1"
DOMAIN_BUNDLE_REGISTRY_ARTIFACT_V1 = "DOMAIN_BUNDLE_REGISTRY_ARTIFACT_V1"
DOMAIN_BUNDLE_RESOLUTION_ARTIFACT_V1 = "DOMAIN_BUNDLE_RESOLUTION_ARTIFACT_V1"
DOMAIN_BUNDLE_RESOLUTION_RETURNED_V1 = "DOMAIN_BUNDLE_RESOLUTION_RETURNED_V1"
DOMAIN_BUNDLE_RESOLVED = "DOMAIN_BUNDLE_RESOLVED"
FAILED_CLOSED = "FAILED_CLOSED"
RESOLVABLE_EXECUTABLE = "RESOLVABLE_EXECUTABLE"
RESOLVABLE_NOT_EXECUTABLE = "RESOLVABLE_NOT_EXECUTABLE"
CREATE_ONLY = "CREATE_ONLY"

REPLAY_STEPS = (
    "domain_bundle_resolution_recorded",
    "domain_bundle_resolution_returned",
)


def default_domain_bundle_registry() -> dict[str, Any]:
    """Return the canonical domain bundle registry."""

    registry = {
        "artifact_type": DOMAIN_BUNDLE_REGISTRY_ARTIFACT_V1,
        "runtime_version": AIGOL_DOMAIN_BUNDLE_REGISTRY_RUNTIME_VERSION,
        "registry_version": DOMAIN_BUNDLE_REGISTRY_VERSION,
        "entries": [
            _entry(
                domain_id="MARKETING",
                display_name="Marketing",
                bundle_id="MARKETING_EXECUTABLE_DOMAIN_BUNDLE_V1",
                domain_status="EXECUTABLE_PLACEHOLDER_CERTIFIED",
                factory_resolution_status=RESOLVABLE_EXECUTABLE,
                regulatory_constraints=[],
                known_gaps=["Real Marketing implementation logic remains unimplemented."],
            ),
            _entry(
                domain_id="SERVER_MANAGEMENT",
                display_name="Server Management",
                bundle_id="SERVER_MANAGEMENT_EXECUTABLE_DOMAIN_BUNDLE_V1",
                domain_status="EXECUTABLE_PLACEHOLDER_CERTIFIED",
                factory_resolution_status=RESOLVABLE_EXECUTABLE,
                regulatory_constraints=["No server mutation authority.", "No deployment authority."],
                known_gaps=["Real Server Management implementation logic remains unimplemented."],
            ),
            _entry(
                domain_id="TRADING",
                display_name="Trading",
                bundle_id="TRADING_EXECUTABLE_DOMAIN_BUNDLE_V1",
                domain_status="EXECUTABLE_PLACEHOLDER_CERTIFIED",
                factory_resolution_status=RESOLVABLE_EXECUTABLE,
                regulatory_constraints=["No broker/API execution.", "No trading execution authority."],
                known_gaps=["Real Trading implementation logic remains unimplemented."],
            ),
            _entry(
                domain_id="HEALTHCARE",
                display_name="Healthcare",
                bundle_id="HEALTHCARE_EXECUTABLE_DOMAIN_BUNDLE_V1",
                domain_status="EXECUTABLE_PLACEHOLDER_CERTIFIED",
                factory_resolution_status=RESOLVABLE_EXECUTABLE,
                regulatory_constraints=["No compliance guarantee claims.", "No clinical or patient-data authority."],
                known_gaps=["Real Healthcare implementation logic remains unimplemented."],
            ),
        ],
        "semantic_interpretation_performed": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
    }
    _finalize_registry(registry)
    return registry


def resolve_domain_bundle(
    *,
    resolution_id: str,
    domain_id: str,
    created_at: str,
    replay_dir: str | Path,
    bundle_id: str | None = None,
    require_executable: bool = False,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve one domain bundle registry entry with replay evidence."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        active_registry = deepcopy(registry) if registry is not None else default_domain_bundle_registry()
        registry_hash = _validate_registry(active_registry)
        entry = _resolve_entry(active_registry, domain_id=domain_id, bundle_id=bundle_id)
        if require_executable and entry["factory_resolution_status"] != RESOLVABLE_EXECUTABLE:
            raise FailClosedRuntimeError("domain bundle registry failed closed: domain bundle is not executable")
        resolution = _resolution_artifact(
            resolution_id=resolution_id,
            registry=active_registry,
            registry_hash=registry_hash,
            entry=entry,
            require_executable=require_executable,
            created_at=created_at,
            resolution_status=DOMAIN_BUNDLE_RESOLVED,
            failure_reason=None,
        )
        returned = _returned_artifact(resolution)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], resolution)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(resolution, returned, replay_path)
    except Exception as exc:
        resolution = _failed_resolution_artifact(
            resolution_id=resolution_id,
            domain_id=domain_id,
            bundle_id=bundle_id,
            registry=registry,
            require_executable=require_executable,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(resolution)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], resolution)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(resolution, returned, replay_path)


def resolve_domain_bundle_entry(
    *,
    domain_id: str,
    bundle_id: str | None = None,
    require_executable: bool = False,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve one registry entry without replay persistence."""

    active_registry = deepcopy(registry) if registry is not None else default_domain_bundle_registry()
    registry_hash = _validate_registry(active_registry)
    entry = _resolve_entry(active_registry, domain_id=domain_id, bundle_id=bundle_id)
    if require_executable and entry["factory_resolution_status"] != RESOLVABLE_EXECUTABLE:
        raise FailClosedRuntimeError("domain bundle registry failed closed: domain bundle is not executable")
    resolved = deepcopy(entry)
    resolved["registry_hash"] = registry_hash
    resolved["registry_version"] = active_registry["registry_version"]
    return resolved


def resolve_domain_bundle_entry_by_bundle_id(
    *,
    bundle_id: str,
    require_executable: bool = False,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve one registry entry by bundle id without replay persistence."""

    active_registry = deepcopy(registry) if registry is not None else default_domain_bundle_registry()
    registry_hash = _validate_registry(active_registry)
    bundle_key = _normalize_key(bundle_id, "bundle_id")
    matches = [
        entry
        for entry in active_registry["entries"]
        if _normalize_key(entry["bundle_id"], "bundle_id") == bundle_key
    ]
    if not matches:
        raise FailClosedRuntimeError("domain bundle registry failed closed: unknown domain bundle")
    if len(matches) > 1:
        raise FailClosedRuntimeError("domain bundle registry failed closed: ambiguous domain bundle")
    entry = deepcopy(matches[0])
    if require_executable and entry["factory_resolution_status"] != RESOLVABLE_EXECUTABLE:
        raise FailClosedRuntimeError("domain bundle registry failed closed: domain bundle is not executable")
    entry["registry_hash"] = registry_hash
    entry["registry_version"] = active_registry["registry_version"]
    return entry


def reconstruct_domain_bundle_resolution_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct domain bundle registry resolution replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("domain bundle registry replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("domain bundle registry replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "domain bundle registry resolution")
        wrappers.append(wrapper)
    resolution = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("resolution_reference") != resolution["resolution_id"]:
        raise FailClosedRuntimeError("domain bundle registry replay reference mismatch")
    if returned.get("resolution_hash") != resolution["artifact_hash"]:
        raise FailClosedRuntimeError("domain bundle registry replay hash mismatch")
    return {
        "resolution_id": resolution["resolution_id"],
        "resolution_status": resolution["resolution_status"],
        "domain_id": resolution["domain_id"],
        "bundle_id": resolution["bundle_id"],
        "registry_version": resolution["registry_version"],
        "registry_hash": resolution["registry_hash"],
        "registry_entry_hash": resolution["registry_entry_hash"],
        "factory_resolution_status": resolution["factory_resolution_status"],
        "artifact_paths": deepcopy(resolution["artifact_paths"]),
        "failure_reason": resolution["failure_reason"],
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
    }


def domain_bundle_contents(entry: dict[str, Any]) -> dict[str, str]:
    """Return deterministic placeholder bundle content for a registry entry."""

    _validate_entry(entry)
    return domain_bundle_contents_without_validation(entry)


def _entry(
    *,
    domain_id: str,
    display_name: str,
    bundle_id: str,
    domain_status: str,
    factory_resolution_status: str,
    regulatory_constraints: list[str],
    known_gaps: list[str],
) -> dict[str, Any]:
    slug = domain_id.lower()
    artifact_prefix = domain_id
    entry = {
        "domain_id": domain_id,
        "domain_display_name": display_name,
        "domain_status": domain_status,
        "bundle_id": bundle_id,
        "bundle_status": domain_status,
        "factory_capability": "EXECUTABLE_DOMAIN_BUNDLE",
        "factory_resolution_status": factory_resolution_status,
        "artifact_templates": [
            _template("DOMAIN_FOUNDATION", f"governance/{artifact_prefix}_DOMAIN_FOUNDATION_V1.md", "GOVERNANCE_DOCUMENT_MARKDOWN"),
            _template("DOMAIN_MODEL", f"governance/{artifact_prefix}_DOMAIN_MODEL_V1.md", "GOVERNANCE_DOCUMENT_MARKDOWN"),
            _template("DOMAIN_CERTIFICATION", f"governance/{artifact_prefix}_DOMAIN_CERTIFICATION.json", "GOVERNANCE_CERTIFICATION_JSON"),
        ],
        "runtime_template": _runtime_template(domain_id, slug),
        "test_template": _test_template(domain_id, slug),
        "regulatory_constraints": list(regulatory_constraints),
        "non_goals": [
            "No provider-generated executable code.",
            "No overwrite or update semantics.",
            "No execution, dispatch, deployment, or external API authority.",
        ],
        "known_gaps": list(known_gaps),
    }
    entry["artifact_paths"] = [
        *(template["path"] for template in entry["artifact_templates"]),
        entry["runtime_template"]["path"],
        entry["test_template"]["path"],
    ]
    contents = domain_bundle_contents_without_validation(entry)
    _apply_content_hashes(entry, contents)
    entry["entry_hash"] = replay_hash(_entry_hash_input(entry))
    return entry


def domain_bundle_contents_without_validation(entry: dict[str, Any]) -> dict[str, str]:
    candidate = deepcopy(entry)
    candidate.setdefault("entry_hash", "sha256:pending")
    domain_id = candidate["domain_id"]
    display = candidate["domain_display_name"]
    slug = domain_id.lower()
    runtime_version_symbol = candidate["runtime_template"]["runtime_version_symbol"]
    describe_function = candidate["runtime_template"]["describe_function"]
    runtime_version = f"{domain_id}_DOMAIN_RUNTIME_V1"
    paths = [
        *(template["path"] for template in candidate["artifact_templates"]),
        candidate["runtime_template"]["path"],
        candidate["test_template"]["path"],
    ]
    if domain_id == "MARKETING":
        return {
            paths[0]: """# MARKETING_DOMAIN_FOUNDATION_V1

## Status

Deterministic placeholder governance document created by
`AIGOL_EXECUTABLE_DOMAIN_BUNDLE_RUNTIME_V1`.

## Scope

This artifact is the foundation member of the first governed executable Marketing domain bundle.
""",
            paths[1]: """# MARKETING_DOMAIN_MODEL_V1

## Status

Deterministic placeholder Marketing domain model.

## Model

The Marketing domain is represented as a governed, replay-visible executable domain bundle.
""",
            paths[2]: """{
  "artifact_type": "MARKETING_DOMAIN_CERTIFICATION",
  "artifact_version": "V1",
  "domain": "MARKETING",
  "status": "PLACEHOLDER_EXECUTABLE_CERTIFIED",
  "bundle_id": "MARKETING_EXECUTABLE_DOMAIN_BUNDLE_V1"
}
""",
            paths[3]: '''"""Deterministic placeholder runtime for the governed Marketing domain."""

from __future__ import annotations


MARKETING_DOMAIN_RUNTIME_VERSION = "MARKETING_DOMAIN_RUNTIME_V1"


def describe_marketing_domain() -> dict[str, str]:
    """Return the bounded placeholder Marketing domain runtime identity."""

    return {
        "domain": "MARKETING",
        "runtime_version": MARKETING_DOMAIN_RUNTIME_VERSION,
        "implementation_status": "PLACEHOLDER",
    }
''',
            paths[4]: '''"""Tests for the deterministic placeholder Marketing domain runtime."""

from aigol.runtime.marketing_domain_runtime import (
    MARKETING_DOMAIN_RUNTIME_VERSION,
    describe_marketing_domain,
)


def test_marketing_domain_runtime_identity() -> None:
    assert describe_marketing_domain() == {
        "domain": "MARKETING",
        "runtime_version": MARKETING_DOMAIN_RUNTIME_VERSION,
        "implementation_status": "PLACEHOLDER",
    }
''',
        }
    return {
        paths[0]: (
            f"# {domain_id}_DOMAIN_FOUNDATION_V1\n\n"
            "## Status\n\n"
            "Deterministic placeholder governance document created by\n"
            "`AIGOL_GENERIC_DOMAIN_FACTORY_RUNTIME_V1`.\n\n"
            "## Scope\n\n"
            f"This artifact is the foundation member of the governed executable {display} domain bundle.\n"
        ),
        paths[1]: (
            f"# {domain_id}_DOMAIN_MODEL_V1\n\n"
            "## Status\n\n"
            f"Deterministic placeholder {display} domain model.\n\n"
            "## Model\n\n"
            f"The {display} domain is represented as a governed, replay-visible executable domain bundle.\n"
        ),
        paths[2]: (
            "{\n"
            f'  "artifact_type": "{domain_id}_DOMAIN_CERTIFICATION",\n'
            '  "artifact_version": "V1",\n'
            f'  "domain": "{domain_id}",\n'
            '  "status": "PLACEHOLDER_EXECUTABLE_CERTIFIED",\n'
            f'  "bundle_id": "{candidate["bundle_id"]}"\n'
            "}\n"
        ),
        paths[3]: (
            f'"""Deterministic placeholder runtime for the governed {display} domain."""\n\n'
            "from __future__ import annotations\n\n\n"
            f'{runtime_version_symbol} = "{runtime_version}"\n\n\n'
            f"def {describe_function}() -> dict[str, str]:\n"
            f'    """Return the bounded placeholder {display} domain runtime identity."""\n\n'
            "    return {\n"
            f'        "domain": "{domain_id}",\n'
            f'        "runtime_version": {runtime_version_symbol},\n'
            '        "implementation_status": "PLACEHOLDER",\n'
            "    }\n"
        ),
        paths[4]: (
            f'"""Tests for the deterministic placeholder {display} domain runtime."""\n\n'
            f"from aigol.runtime.{slug}_domain_runtime import (\n"
            f"    {runtime_version_symbol},\n"
            f"    {describe_function},\n"
            ")\n\n\n"
            f"def test_{slug}_domain_runtime_identity() -> None:\n"
            f"    assert {describe_function}() == {{\n"
            f'        "domain": "{domain_id}",\n'
            f'        "runtime_version": {runtime_version_symbol},\n'
            '        "implementation_status": "PLACEHOLDER",\n'
            "    }\n"
        ),
    }


def _apply_content_hashes(entry: dict[str, Any], contents: dict[str, str]) -> None:
    templates = [
        *entry["artifact_templates"],
        entry["runtime_template"],
        entry["test_template"],
    ]
    for template in templates:
        template["canonical_content_hash"] = replay_hash(contents[template["path"]])


def _template(role: str, path: str, artifact_type: str) -> dict[str, Any]:
    return {
        "role": role,
        "path": path,
        "artifact_type": artifact_type,
        "template_id": f"{role}_TEMPLATE_V1",
        "template_version": "V1",
        "canonical_content_hash": replay_hash({"role": role, "path": path}),
        "permission": CREATE_ONLY,
        "overwrite_permitted": False,
    }


def _runtime_template(domain_id: str, slug: str) -> dict[str, Any]:
    return {
        "role": "DOMAIN_RUNTIME",
        "path": f"aigol/runtime/{slug}_domain_runtime.py",
        "artifact_type": "PYTHON_RUNTIME_FILE",
        "module_name": f"{slug}_domain_runtime",
        "runtime_version_symbol": f"{domain_id}_DOMAIN_RUNTIME_VERSION",
        "describe_function": f"describe_{slug}_domain",
        "implementation_status": "PLACEHOLDER",
        "canonical_content_hash": replay_hash({"role": "DOMAIN_RUNTIME", "domain_id": domain_id}),
        "permission": CREATE_ONLY,
        "overwrite_permitted": False,
    }


def _test_template(domain_id: str, slug: str) -> dict[str, Any]:
    return {
        "role": "DOMAIN_RUNTIME_TEST",
        "path": f"tests/test_{slug}_domain_runtime_v1.py",
        "artifact_type": "PYTHON_TEST_FILE",
        "test_function": f"test_{slug}_domain_runtime_identity",
        "expected_domain_id": domain_id,
        "canonical_content_hash": replay_hash({"role": "DOMAIN_RUNTIME_TEST", "domain_id": domain_id}),
        "permission": CREATE_ONLY,
        "overwrite_permitted": False,
    }


def _finalize_registry(registry: dict[str, Any]) -> None:
    _validate_registry_shape(registry)
    registry["registry_hash"] = replay_hash(_registry_hash_input(registry))
    registry["artifact_hash"] = replay_hash(registry)


def _validate_registry(registry: dict[str, Any]) -> str:
    _validate_registry_shape(registry)
    registry_hash = registry.get("registry_hash")
    expected = replay_hash(_registry_hash_input(registry))
    if registry_hash is None:
        registry["registry_hash"] = expected
        registry_hash = expected
    if registry_hash != expected:
        raise FailClosedRuntimeError("domain bundle registry failed closed: registry hash mismatch")
    return registry_hash


def _validate_registry_shape(registry: dict[str, Any]) -> None:
    if not isinstance(registry, dict) or registry.get("artifact_type") != DOMAIN_BUNDLE_REGISTRY_ARTIFACT_V1:
        raise FailClosedRuntimeError("domain bundle registry failed closed: invalid registry")
    if registry.get("registry_version") != DOMAIN_BUNDLE_REGISTRY_VERSION:
        raise FailClosedRuntimeError("domain bundle registry failed closed: invalid registry version")
    entries = registry.get("entries")
    if not isinstance(entries, list) or not entries:
        raise FailClosedRuntimeError("domain bundle registry failed closed: registry entries required")
    domain_keys: set[str] = set()
    bundle_keys: set[str] = set()
    for entry in entries:
        _validate_entry(entry)
        domain_key = _normalize_key(entry["domain_id"], "domain_id")
        bundle_key = _normalize_key(entry["bundle_id"], "bundle_id")
        if domain_key in domain_keys:
            raise FailClosedRuntimeError("domain bundle registry failed closed: duplicate domain registration")
        if bundle_key in bundle_keys:
            raise FailClosedRuntimeError("domain bundle registry failed closed: duplicate bundle registration")
        domain_keys.add(domain_key)
        bundle_keys.add(bundle_key)


def _validate_entry(entry: Any) -> None:
    if not isinstance(entry, dict):
        raise FailClosedRuntimeError("domain bundle registry failed closed: invalid registry entry")
    for field in (
        "domain_id",
        "bundle_id",
        "factory_resolution_status",
        "artifact_templates",
        "runtime_template",
        "test_template",
        "entry_hash",
    ):
        _require_string(entry.get(field), field) if field not in {"artifact_templates", "runtime_template", "test_template"} else None
    if entry["factory_resolution_status"] not in {RESOLVABLE_EXECUTABLE, RESOLVABLE_NOT_EXECUTABLE}:
        raise FailClosedRuntimeError("domain bundle registry failed closed: invalid factory resolution status")
    if entry["entry_hash"] != replay_hash(_entry_hash_input(entry)):
        raise FailClosedRuntimeError("domain bundle registry failed closed: registry entry hash mismatch")
    paths = _entry_paths(entry)
    if len(paths) != len(set(paths)):
        raise FailClosedRuntimeError("domain bundle registry failed closed: duplicate artifact path")
    for path in paths:
        _validate_path(path)


def _resolve_entry(registry: dict[str, Any], *, domain_id: str, bundle_id: str | None) -> dict[str, Any]:
    domain_key = _normalize_key(domain_id, "domain_id")
    matches = [entry for entry in registry["entries"] if _normalize_key(entry["domain_id"], "domain_id") == domain_key]
    if bundle_id is not None:
        bundle_key = _normalize_key(bundle_id, "bundle_id")
        matches = [entry for entry in matches if _normalize_key(entry["bundle_id"], "bundle_id") == bundle_key]
    if not matches:
        raise FailClosedRuntimeError("domain bundle registry failed closed: unknown domain bundle")
    if len(matches) > 1:
        raise FailClosedRuntimeError("domain bundle registry failed closed: ambiguous domain bundle")
    return deepcopy(matches[0])


def _resolution_artifact(
    *,
    resolution_id: str,
    registry: dict[str, Any],
    registry_hash: str,
    entry: dict[str, Any],
    require_executable: bool,
    created_at: str,
    resolution_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": DOMAIN_BUNDLE_RESOLUTION_ARTIFACT_V1,
        "runtime_version": AIGOL_DOMAIN_BUNDLE_REGISTRY_RUNTIME_VERSION,
        "resolution_id": _require_string(resolution_id, "resolution_id"),
        "resolution_status": resolution_status,
        "domain_id": entry["domain_id"],
        "bundle_id": entry["bundle_id"],
        "registry_version": registry["registry_version"],
        "registry_hash": _require_string(registry_hash, "registry_hash"),
        "registry_entry_hash": entry["entry_hash"],
        "factory_resolution_status": entry["factory_resolution_status"],
        "require_executable": require_executable,
        "artifact_paths": _entry_paths(entry),
        "artifact_roles": _entry_roles(entry),
        "template_hashes": _entry_template_hashes(entry),
        "registry_entry": deepcopy(entry),
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_resolution_artifact(
    *,
    resolution_id: str,
    domain_id: str,
    bundle_id: str | None,
    registry: dict[str, Any] | None,
    require_executable: bool,
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    registry_hash = None
    if isinstance(registry, dict):
        registry_hash = registry.get("registry_hash")
    artifact = {
        "artifact_type": DOMAIN_BUNDLE_RESOLUTION_ARTIFACT_V1,
        "runtime_version": AIGOL_DOMAIN_BUNDLE_REGISTRY_RUNTIME_VERSION,
        "resolution_id": resolution_id,
        "resolution_status": FAILED_CLOSED,
        "domain_id": domain_id,
        "bundle_id": bundle_id,
        "registry_version": registry.get("registry_version") if isinstance(registry, dict) else DOMAIN_BUNDLE_REGISTRY_VERSION,
        "registry_hash": registry_hash,
        "registry_entry_hash": None,
        "factory_resolution_status": FAILED_CLOSED,
        "require_executable": require_executable,
        "artifact_paths": [],
        "artifact_roles": [],
        "template_hashes": [],
        "registry_entry": None,
        "created_at": created_at,
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(resolution: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(resolution, "domain bundle registry resolution")
    artifact = {
        "artifact_type": DOMAIN_BUNDLE_RESOLUTION_RETURNED_V1,
        "event_type": "DOMAIN_BUNDLE_RESOLUTION_RETURNED",
        "resolution_reference": resolution["resolution_id"],
        "resolution_hash": resolution["artifact_hash"],
        "resolution_status": resolution["resolution_status"],
        "domain_id": resolution["domain_id"],
        "bundle_id": resolution["bundle_id"],
        "factory_resolution_status": resolution["factory_resolution_status"],
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "failure_reason": resolution["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(resolution: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = deepcopy(resolution)
    capture.update(
        {
            "domain_bundle_resolution_artifact": deepcopy(resolution),
            "domain_bundle_resolution_returned_artifact": deepcopy(returned),
            "domain_bundle_resolution_replay_reference": str(replay_path),
            "fail_closed": resolution["resolution_status"] == FAILED_CLOSED,
        }
    )
    capture["domain_bundle_resolution_capture_hash"] = replay_hash(capture)
    return capture


def _entry_paths(entry: dict[str, Any]) -> list[str]:
    return [
        *(template["path"] for template in entry["artifact_templates"]),
        entry["runtime_template"]["path"],
        entry["test_template"]["path"],
    ]


def _entry_roles(entry: dict[str, Any]) -> list[str]:
    return [
        *(template["role"] for template in entry["artifact_templates"]),
        entry["runtime_template"]["role"],
        entry["test_template"]["role"],
    ]


def _entry_template_hashes(entry: dict[str, Any]) -> list[str]:
    return [
        *(template["canonical_content_hash"] for template in entry["artifact_templates"]),
        entry["runtime_template"]["canonical_content_hash"],
        entry["test_template"]["canonical_content_hash"],
    ]


def _entry_hash_input(entry: dict[str, Any]) -> dict[str, Any]:
    candidate = deepcopy(entry)
    candidate.pop("entry_hash", None)
    candidate.pop("registry_hash", None)
    candidate.pop("registry_version", None)
    return candidate


def _registry_hash_input(registry: dict[str, Any]) -> dict[str, Any]:
    candidate = deepcopy(registry)
    candidate.pop("registry_hash", None)
    candidate.pop("artifact_hash", None)
    return candidate


def _validate_path(path: str) -> None:
    path_obj = Path(path)
    if path_obj.is_absolute() or ".." in path_obj.parts:
        raise FailClosedRuntimeError("domain bundle registry failed closed: invalid artifact path")
    if not (
        path.startswith("governance/")
        or path.startswith("aigol/runtime/")
        or path.startswith("tests/")
    ):
        raise FailClosedRuntimeError("domain bundle registry failed closed: unauthorized artifact path")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("domain bundle registry replay ordering mismatch")
    _verify_artifact_hash(artifact, "domain bundle registry resolution")
    wrapper = {"replay_index": index, "replay_step": step, "event_type": step.upper(), "artifact": deepcopy(artifact)}
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    try:
        _persist_step(replay_dir, index, step, artifact)
    except FailClosedRuntimeError:
        pass


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {step}")


def _verify_artifact_hash(artifact: Any, label: str) -> None:
    if not isinstance(artifact, dict) or "artifact_hash" not in artifact:
        raise FailClosedRuntimeError(f"{label} hash is required")
    candidate = deepcopy(artifact)
    actual = candidate.pop("artifact_hash")
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    candidate = deepcopy(wrapper)
    actual = candidate.pop("replay_hash", None)
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("domain bundle registry replay hash mismatch")


def _normalize_key(value: Any, field: str) -> str:
    text = _require_string(value, field)
    return text.strip().upper().replace("-", "_").replace(" ", "_")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"domain bundle registry failed closed: {field} is required")
    return value


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return f"domain bundle registry failed closed: {exc}"
