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
                domain_status="REGISTERED_CONTRACT_ONLY",
                factory_resolution_status=RESOLVABLE_NOT_EXECUTABLE,
                regulatory_constraints=["No server mutation authority.", "No deployment authority."],
                known_gaps=["Executable Server Management bundle is not certified."],
            ),
            _entry(
                domain_id="TRADING",
                display_name="Trading",
                bundle_id="TRADING_EXECUTABLE_DOMAIN_BUNDLE_V1",
                domain_status="REGISTERED_REQUIRES_HUMAN_APPROVAL",
                factory_resolution_status=RESOLVABLE_NOT_EXECUTABLE,
                regulatory_constraints=["No broker/API execution.", "Human approval required before implementation."],
                known_gaps=["Executable Trading bundle is not certified."],
            ),
            _entry(
                domain_id="HEALTHCARE",
                display_name="Healthcare",
                bundle_id="HEALTHCARE_EXECUTABLE_DOMAIN_BUNDLE_V1",
                domain_status="REGISTERED_REQUIRES_HUMAN_APPROVAL",
                factory_resolution_status=RESOLVABLE_NOT_EXECUTABLE,
                regulatory_constraints=["No compliance guarantee claims.", "Human approval required before implementation."],
                known_gaps=["Executable Healthcare bundle is not certified."],
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
    entry["entry_hash"] = replay_hash(_entry_hash_input(entry))
    return entry


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
