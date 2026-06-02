"""Deterministic domain and worker resolution registry for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_DOMAIN_AND_WORKER_RESOLUTION_REGISTRY_VERSION = "AIGOL_DOMAIN_AND_WORKER_RESOLUTION_REGISTRY_V1"
DOMAIN_WORKER_RESOLUTION_ARTIFACT_V1 = "DOMAIN_WORKER_RESOLUTION_ARTIFACT_V1"
RESOLUTION_SUCCEEDED = "RESOLUTION_SUCCEEDED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "domain_worker_resolution_recorded",
    "domain_worker_resolution_returned",
)

DEFAULT_DOMAINS = (
    {
        "domain_id": "TRADING",
        "display_name": "Trading",
        "status": "CERTIFIED",
        "foundation_artifact": "TRADING_DOMAIN_FOUNDATION_V1",
        "certification_artifact": "TRADING_DOMAIN_CERTIFICATION",
        "aliases": ("TRADING",),
    },
    {
        "domain_id": "MARKETING",
        "display_name": "Marketing",
        "status": "REGISTERED_FUTURE_DOMAIN",
        "foundation_artifact": None,
        "certification_artifact": None,
        "aliases": ("MARKETING",),
    },
    {
        "domain_id": "HEALTHCARE",
        "display_name": "Healthcare",
        "status": "REGISTERED_FUTURE_DOMAIN",
        "foundation_artifact": None,
        "certification_artifact": None,
        "aliases": ("HEALTHCARE",),
    },
    {
        "domain_id": "PUBLIC_SERVICES",
        "display_name": "Public Services",
        "status": "REGISTERED_FUTURE_DOMAIN",
        "foundation_artifact": None,
        "certification_artifact": None,
        "aliases": ("PUBLIC_SERVICES", "PUBLIC SERVICES"),
    },
)

DEFAULT_WORKER_FAMILIES = (
    {
        "domain_id": "TRADING",
        "worker_family_id": "MARKET_EVIDENCE_NORMALIZATION",
        "display_name": "Market Evidence Normalization",
        "worker_class": "EVIDENCE_NORMALIZATION",
        "status": "FOUNDATION_CANDIDATE",
        "aliases": ("MARKET EVIDENCE NORMALIZATION", "MARKET_EVIDENCE_NORMALIZATION"),
        "authority": "READ_ONLY_EVIDENCE_TRANSFORMATION",
    },
    {
        "domain_id": "TRADING",
        "worker_family_id": "RISK_ANALYSIS",
        "display_name": "Risk Analysis",
        "worker_class": "RISK_ANALYSIS",
        "status": "FOUNDATION_CANDIDATE",
        "aliases": ("RISK ANALYSIS", "TRADING RISK ANALYSIS"),
        "authority": "ANALYSIS_ONLY",
    },
    {
        "domain_id": "TRADING",
        "worker_family_id": "PORTFOLIO_ANALYSIS",
        "display_name": "Portfolio Analysis",
        "worker_class": "PORTFOLIO_CONTEXT",
        "status": "FOUNDATION_CANDIDATE",
        "aliases": ("PORTFOLIO ANALYSIS", "PORTFOLIO WORKER"),
        "authority": "CONTEXT_EVIDENCE_ONLY",
    },
    {
        "domain_id": "TRADING",
        "worker_family_id": "STRATEGY_EVALUATION",
        "display_name": "Strategy Evaluation",
        "worker_class": "STRATEGY_EVALUATION",
        "status": "FOUNDATION_CANDIDATE",
        "aliases": ("STRATEGY EVALUATION",),
        "authority": "EVALUATION_ONLY",
    },
    {
        "domain_id": "TRADING",
        "worker_family_id": "DECISION_EXPLANATION",
        "display_name": "Decision Explanation",
        "worker_class": "DECISION_EXPLANATION",
        "status": "FOUNDATION_CANDIDATE",
        "aliases": ("DECISION EXPLANATION",),
        "authority": "EXPLANATION_ONLY",
    },
)

DEFAULT_MILESTONE_TYPES = (
    {
        "milestone_type": "WORKER_FOUNDATION",
        "display_name": "Worker Foundation",
        "suffix": "WORKER_FOUNDATION_V1",
        "implementation_allowed": False,
    },
    {
        "milestone_type": "WORKER_RUNTIME",
        "display_name": "Worker Runtime",
        "suffix": "WORKER_RUNTIME_V1",
        "implementation_allowed": True,
    },
    {
        "milestone_type": "WORKER_CERTIFICATION",
        "display_name": "Worker Certification",
        "suffix": "WORKER_CERTIFICATION_V1",
        "implementation_allowed": False,
    },
    {
        "milestone_type": "WORKER_ACCEPTANCE",
        "display_name": "Worker Acceptance",
        "suffix": "WORKER_ACCEPTANCE_V1",
        "implementation_allowed": False,
    },
)


def default_domain_worker_registry() -> dict[str, Any]:
    """Return the canonical registry with a deterministic hash."""

    registry = {
        "registry_version": AIGOL_DOMAIN_AND_WORKER_RESOLUTION_REGISTRY_VERSION,
        "domains": deepcopy(list(DEFAULT_DOMAINS)),
        "worker_families": deepcopy(list(DEFAULT_WORKER_FAMILIES)),
        "milestone_types": deepcopy(list(DEFAULT_MILESTONE_TYPES)),
        "semantic_interpretation_performed": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
    }
    _validate_registry_entries(registry)
    registry["registry_hash"] = replay_hash(_registry_hash_input(registry))
    return registry


def resolve_domain_worker_milestone(
    *,
    resolution_id: str,
    domain_id: str,
    worker_family_id: str,
    milestone_type: str,
    created_at: str,
    replay_dir: str | Path,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve explicit domain, worker family, and milestone type ids without semantic interpretation."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        active_registry = deepcopy(registry) if registry is not None else default_domain_worker_registry()
        _validate_registry_entries(active_registry)
        registry_hash = active_registry.get("registry_hash") or replay_hash(_registry_hash_input(active_registry))
        domain = _resolve_domain(active_registry, domain_id)
        worker = _resolve_worker(active_registry, domain["domain_id"], worker_family_id)
        milestone = _resolve_milestone(active_registry, milestone_type)
        artifact = _resolution_artifact(
            resolution_id=resolution_id,
            registry=active_registry,
            registry_hash=registry_hash,
            domain=domain,
            worker=worker,
            milestone=milestone,
            created_at=created_at,
            resolution_status=RESOLUTION_SUCCEEDED,
            failure_reason=None,
        )
        returned = _returned_artifact(artifact)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, replay_path)
    except Exception as exc:
        artifact = _failed_resolution_artifact(
            resolution_id=resolution_id,
            domain_id=domain_id,
            worker_family_id=worker_family_id,
            milestone_type=milestone_type,
            created_at=created_at,
            registry=registry,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(artifact)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, replay_path)


def reconstruct_domain_worker_resolution_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct domain and worker resolution replay evidence."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("domain worker resolution replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("domain worker resolution replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    resolution = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("resolution_reference") != resolution["resolution_id"]:
        raise FailClosedRuntimeError("domain worker resolution replay reference mismatch")
    if returned.get("resolution_hash") != resolution["artifact_hash"]:
        raise FailClosedRuntimeError("domain worker resolution replay hash mismatch")
    return {
        "resolution_id": resolution["resolution_id"],
        "resolution_status": resolution["resolution_status"],
        "domain_id": resolution["domain_id"],
        "worker_family_id": resolution["worker_family_id"],
        "milestone_type": resolution["milestone_type"],
        "registry_version": resolution["registry_version"],
        "registry_hash": resolution["registry_hash"],
        "resolution_result": deepcopy(resolution["resolution_result"]),
        "failure_reason": resolution["failure_reason"],
        "semantic_interpretation_performed": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _resolve_domain(registry: dict[str, Any], value: str) -> dict[str, Any]:
    key = _normalize_key(value, "domain_id")
    matches = [
        domain
        for domain in registry["domains"]
        if key == _normalize_key(domain["domain_id"], "domain_id")
        or key in {_normalize_key(alias, "domain_alias") for alias in domain.get("aliases", [])}
    ]
    if not matches:
        raise FailClosedRuntimeError("domain worker resolution failed closed: unknown domain")
    if len(matches) > 1:
        raise FailClosedRuntimeError("domain worker resolution failed closed: ambiguous domain")
    return deepcopy(matches[0])


def _resolve_worker(registry: dict[str, Any], domain_id: str, value: str) -> dict[str, Any]:
    key = _normalize_key(value, "worker_family_id")
    domain = _normalize_key(domain_id, "domain_id")
    matches = [
        worker
        for worker in registry["worker_families"]
        if _normalize_key(worker["domain_id"], "worker_domain_id") == domain
        and (
            key == _normalize_key(worker["worker_family_id"], "worker_family_id")
            or key in {_normalize_key(alias, "worker_alias") for alias in worker.get("aliases", [])}
            or key == _normalize_key(worker.get("display_name"), "worker_display_name")
        )
    ]
    if not matches:
        raise FailClosedRuntimeError("domain worker resolution failed closed: unknown worker family")
    if len(matches) > 1:
        raise FailClosedRuntimeError("domain worker resolution failed closed: ambiguous worker family")
    return deepcopy(matches[0])


def _resolve_milestone(registry: dict[str, Any], value: str) -> dict[str, Any]:
    key = _normalize_key(value, "milestone_type")
    matches = [
        milestone
        for milestone in registry["milestone_types"]
        if key == _normalize_key(milestone["milestone_type"], "milestone_type")
        or key == _normalize_key(milestone["display_name"], "milestone_display_name")
    ]
    if not matches:
        raise FailClosedRuntimeError("domain worker resolution failed closed: invalid milestone type")
    if len(matches) > 1:
        raise FailClosedRuntimeError("domain worker resolution failed closed: ambiguous milestone type")
    return deepcopy(matches[0])


def _resolution_artifact(
    *,
    resolution_id: str,
    registry: dict[str, Any],
    registry_hash: str,
    domain: dict[str, Any],
    worker: dict[str, Any],
    milestone: dict[str, Any],
    created_at: str,
    resolution_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    result = {
        "domain": deepcopy(domain),
        "worker_family": deepcopy(worker),
        "milestone": deepcopy(milestone),
        "canonical_milestone_prefix": f"{domain['domain_id']}_{worker['worker_family_id']}_{milestone['milestone_type']}",
    }
    artifact = {
        "artifact_type": DOMAIN_WORKER_RESOLUTION_ARTIFACT_V1,
        "registry_version": registry.get("registry_version", AIGOL_DOMAIN_AND_WORKER_RESOLUTION_REGISTRY_VERSION),
        "registry_hash": _require_string(registry_hash, "registry_hash"),
        "resolution_id": _require_string(resolution_id, "resolution_id"),
        "domain_id": domain["domain_id"],
        "worker_family_id": worker["worker_family_id"],
        "milestone_type": milestone["milestone_type"],
        "resolution_status": resolution_status,
        "resolution_result": result,
        "semantic_interpretation_performed": False,
        "provider_invoked": False,
        "provider_authority": False,
        "domain_created": False,
        "worker_created": False,
        "proposal_generated": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "worker_invoked": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_resolution_artifact(
    *,
    resolution_id: str,
    domain_id: str,
    worker_family_id: str,
    milestone_type: str,
    created_at: str,
    registry: dict[str, Any] | None,
    failure_reason: str,
) -> dict[str, Any]:
    active_registry = deepcopy(registry) if isinstance(registry, dict) else default_domain_worker_registry()
    registry_hash = active_registry.get("registry_hash") or replay_hash(_registry_hash_input(active_registry))
    artifact = {
        "artifact_type": DOMAIN_WORKER_RESOLUTION_ARTIFACT_V1,
        "registry_version": active_registry.get("registry_version", AIGOL_DOMAIN_AND_WORKER_RESOLUTION_REGISTRY_VERSION),
        "registry_hash": registry_hash,
        "resolution_id": _require_string(resolution_id, "resolution_id"),
        "domain_id": domain_id,
        "worker_family_id": worker_family_id,
        "milestone_type": milestone_type,
        "resolution_status": FAILED_CLOSED,
        "resolution_result": None,
        "semantic_interpretation_performed": False,
        "provider_invoked": False,
        "provider_authority": False,
        "domain_created": False,
        "worker_created": False,
        "proposal_generated": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "worker_invoked": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(resolution: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(resolution)
    returned = {
        "event_type": "DOMAIN_WORKER_RESOLUTION_RETURNED",
        "resolution_reference": resolution["resolution_id"],
        "resolution_hash": resolution["artifact_hash"],
        "resolution_status": resolution["resolution_status"],
        "domain_id": resolution["domain_id"],
        "worker_family_id": resolution["worker_family_id"],
        "milestone_type": resolution["milestone_type"],
        "registry_version": resolution["registry_version"],
        "registry_hash": resolution["registry_hash"],
        "replay_visible": True,
        "semantic_interpretation_performed": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "failure_reason": resolution["failure_reason"],
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(resolution: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "domain_worker_resolution_artifact": deepcopy(resolution),
        "domain_worker_resolution_replay": deepcopy(returned),
        "domain_worker_resolution_replay_reference": str(replay_path),
        "resolution_status": resolution["resolution_status"],
        "domain_id": resolution["domain_id"],
        "worker_family_id": resolution["worker_family_id"],
        "milestone_type": resolution["milestone_type"],
        "registry_version": resolution["registry_version"],
        "registry_hash": resolution["registry_hash"],
        "resolution_result": deepcopy(resolution["resolution_result"]),
        "fail_closed": resolution["resolution_status"] == FAILED_CLOSED,
        "failure_reason": resolution["failure_reason"],
        "semantic_interpretation_performed": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
    }
    capture["domain_worker_resolution_capture_hash"] = replay_hash(capture)
    return capture


def _validate_registry_entries(registry: dict[str, Any]) -> None:
    if registry.get("registry_version") != AIGOL_DOMAIN_AND_WORKER_RESOLUTION_REGISTRY_VERSION:
        raise FailClosedRuntimeError("domain worker resolution failed closed: invalid registry version")
    _validate_unique(registry.get("domains"), "domain_id", "duplicate domain registration")
    _validate_unique(registry.get("milestone_types"), "milestone_type", "duplicate milestone registration")
    worker_keys = []
    for worker in _require_list(registry.get("worker_families"), "worker_families"):
        domain = _normalize_key(worker.get("domain_id"), "worker_domain_id")
        worker_id = _normalize_key(worker.get("worker_family_id"), "worker_family_id")
        worker_keys.append(f"{domain}:{worker_id}")
    if len(set(worker_keys)) != len(worker_keys):
        raise FailClosedRuntimeError("domain worker resolution failed closed: duplicate worker registration")


def _validate_unique(value: Any, key: str, message: str) -> None:
    entries = _require_list(value, key)
    keys = [_normalize_key(entry.get(key), key) for entry in entries if isinstance(entry, dict)]
    if len(keys) != len(entries) or len(set(keys)) != len(keys):
        raise FailClosedRuntimeError(f"domain worker resolution failed closed: {message}")


def _registry_hash_input(registry: dict[str, Any]) -> dict[str, Any]:
    return {
        "registry_version": registry.get("registry_version"),
        "domains": registry.get("domains"),
        "worker_families": registry.get("worker_families"),
        "milestone_types": registry.get("milestone_types"),
    }


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("domain worker resolution replay step ordering mismatch")
    _verify_artifact_hash(artifact)
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "event_type": step.upper(),
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    try:
        _persist_step(replay_dir, index, step, artifact)
    except FailClosedRuntimeError:
        pass


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError("domain worker resolution artifact hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("domain worker resolution artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("domain worker resolution replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("domain worker resolution replay hash mismatch")


def _normalize_key(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).upper().replace("-", "_").replace(" ", "_")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _require_list(value: Any, field_name: str) -> list[Any]:
    if not isinstance(value, list) or not value:
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "domain worker resolution failed closed"

