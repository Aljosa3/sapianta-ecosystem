"""Deterministic unified resource selection runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_necessity_policy_runtime import (
    PROVIDER_OPTIONAL,
    PROVIDER_PROHIBITED,
    PROVIDER_REQUIRED,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


UNIFIED_RESOURCE_SELECTION_RUNTIME_VERSION = "UNIFIED_RESOURCE_SELECTION_RUNTIME_V1"
RESOURCE_SELECTION_ARTIFACT_V1 = "RESOURCE_SELECTION_ARTIFACT_V1"
RESOURCE_SELECTION_STATUS_V1 = "RESOURCE_SELECTION_STATUS_V1"
RESOURCE_SELECTION_DIAGNOSTICS_V1 = "RESOURCE_SELECTION_DIAGNOSTICS_V1"
RESOURCE_SELECTION_SUCCEEDED = "RESOURCE_SELECTION_SUCCEEDED"
FAILED_CLOSED = "FAILED_CLOSED"

PROVIDER = "PROVIDER"
WORKER = "WORKER"
HYBRID_PROVIDER_WORKER = "HYBRID_PROVIDER_WORKER"
OPERATOR_TOOL = "OPERATOR_TOOL"
GOVERNANCE_RUNTIME = "GOVERNANCE_RUNTIME"
DOMAIN_RUNTIME = "DOMAIN_RUNTIME"

PROVIDER_ROLE = "PROVIDER_ROLE"
WORKER_ROLE = "WORKER_ROLE"
OPERATOR_TOOL_ROLE = "OPERATOR_TOOL_ROLE"
GOVERNANCE_RUNTIME_ROLE = "GOVERNANCE_RUNTIME_ROLE"
DOMAIN_RUNTIME_ROLE = "DOMAIN_RUNTIME_ROLE"

REPLAY_STEPS = (
    "resource_selection_recorded",
    "resource_selection_returned",
)

TRUST_RANK = {
    "UNASSESSED": 0,
    "LOW": 1,
    "STANDARD": 2,
    "HIGH": 3,
    "RESTRICTED": 1,
    "SUSPENDED": -1,
}

SELECTABLE_STATUSES = {"APPROVED", "ATTACHED", "AVAILABLE"}

DEFAULT_RESOURCES = (
    {
        "resource_id": "OPENAI",
        "resource_category": PROVIDER,
        "display_name": "OpenAI",
        "resource_version": "openai-responses-v1",
        "trust_level": "HIGH",
        "lifecycle_status": "AVAILABLE",
        "selection_priority": 10,
        "role_bindings": (
            {
                "role_type": PROVIDER_ROLE,
                "role_status": "AVAILABLE",
                "capability_ids": ("PROPOSAL_GENERATION", "PROPOSAL_REPAIR", "CLARIFICATION_ASSISTANCE"),
                "authority_profile": "PROVIDER_PROPOSAL_ONLY",
                "domain_scope": ("NATIVE_DEVELOPMENT", "GOVERNANCE", "TRADING"),
            },
        ),
    },
    {
        "resource_id": "ANTHROPIC",
        "resource_category": PROVIDER,
        "display_name": "Anthropic",
        "resource_version": "anthropic-provider-candidate-v1",
        "trust_level": "STANDARD",
        "lifecycle_status": "APPROVED",
        "selection_priority": 20,
        "role_bindings": (
            {
                "role_type": PROVIDER_ROLE,
                "role_status": "APPROVED",
                "capability_ids": ("PROPOSAL_GENERATION", "PROPOSAL_REPAIR", "CLARIFICATION_ASSISTANCE"),
                "authority_profile": "PROVIDER_PROPOSAL_ONLY",
                "domain_scope": ("NATIVE_DEVELOPMENT", "GOVERNANCE", "TRADING"),
            },
        ),
    },
    {
        "resource_id": "CODEX",
        "resource_category": HYBRID_PROVIDER_WORKER,
        "display_name": "Codex",
        "resource_version": "codex-hybrid-candidate-v1",
        "trust_level": "STANDARD",
        "lifecycle_status": "AVAILABLE",
        "selection_priority": 30,
        "role_bindings": (
            {
                "role_type": PROVIDER_ROLE,
                "role_status": "AVAILABLE",
                "capability_ids": ("PROPOSAL_GENERATION", "IMPLEMENTATION_ASSISTANCE"),
                "authority_profile": "PROVIDER_PROPOSAL_ONLY",
                "domain_scope": ("NATIVE_DEVELOPMENT", "GOVERNANCE", "TRADING"),
            },
            {
                "role_type": WORKER_ROLE,
                "role_status": "AVAILABLE",
                "capability_ids": ("IMPLEMENTATION_ASSISTANCE", "FILESYSTEM_INSPECTION"),
                "authority_profile": "WORKER_AUTHORIZED_TASK_ONLY",
                "domain_scope": ("NATIVE_DEVELOPMENT", "GOVERNANCE"),
            },
        ),
    },
    {
        "resource_id": "CLAUDE_CODE",
        "resource_category": HYBRID_PROVIDER_WORKER,
        "display_name": "Claude Code",
        "resource_version": "claude-code-hybrid-candidate-v1",
        "trust_level": "STANDARD",
        "lifecycle_status": "APPROVED",
        "selection_priority": 40,
        "role_bindings": (
            {
                "role_type": PROVIDER_ROLE,
                "role_status": "APPROVED",
                "capability_ids": ("PROPOSAL_GENERATION", "IMPLEMENTATION_ASSISTANCE"),
                "authority_profile": "PROVIDER_PROPOSAL_ONLY",
                "domain_scope": ("NATIVE_DEVELOPMENT", "GOVERNANCE", "TRADING"),
            },
            {
                "role_type": WORKER_ROLE,
                "role_status": "APPROVED",
                "capability_ids": ("IMPLEMENTATION_ASSISTANCE", "FILESYSTEM_INSPECTION"),
                "authority_profile": "WORKER_AUTHORIZED_TASK_ONLY",
                "domain_scope": ("NATIVE_DEVELOPMENT", "GOVERNANCE"),
            },
        ),
    },
    {
        "resource_id": "REPLAY_INSPECTOR_WORKER",
        "resource_category": WORKER,
        "display_name": "Replay Inspector Worker",
        "resource_version": "replay-inspector-worker-v1",
        "trust_level": "HIGH",
        "lifecycle_status": "AVAILABLE",
        "selection_priority": 50,
        "role_bindings": (
            {
                "role_type": WORKER_ROLE,
                "role_status": "AVAILABLE",
                "capability_ids": ("REPLAY_INSPECTION",),
                "authority_profile": "WORKER_AUTHORIZED_TASK_ONLY",
                "domain_scope": ("REPLAY", "GOVERNANCE"),
            },
        ),
    },
    {
        "resource_id": "UNIFIED_REPLAY_RECONSTRUCTION_RUNTIME",
        "resource_category": GOVERNANCE_RUNTIME,
        "display_name": "Unified Replay Reconstruction Runtime",
        "resource_version": "unified-replay-reconstruction-runtime-v1",
        "trust_level": "HIGH",
        "lifecycle_status": "AVAILABLE",
        "selection_priority": 60,
        "role_bindings": (
            {
                "role_type": GOVERNANCE_RUNTIME_ROLE,
                "role_status": "AVAILABLE",
                "capability_ids": ("GOVERNANCE_VALIDATION", "REPLAY_INSPECTION"),
                "authority_profile": "GOVERNANCE_RUNTIME_VALIDATION_ONLY",
                "domain_scope": ("REPLAY", "GOVERNANCE"),
            },
        ),
    },
)

AUTHORITY_PROFILES = {
    "PROVIDER_PROPOSAL_ONLY": {
        "can_propose": True,
        "can_execute_authorized_task": False,
        "can_dispatch": False,
        "can_authorize": False,
        "can_govern": False,
        "can_mutate_replay": False,
        "can_mutate_governance": False,
        "can_invoke_provider": False,
        "can_invoke_worker": False,
    },
    "WORKER_AUTHORIZED_TASK_ONLY": {
        "can_propose": False,
        "can_execute_authorized_task": True,
        "can_dispatch": False,
        "can_authorize": False,
        "can_govern": False,
        "can_mutate_replay": False,
        "can_mutate_governance": False,
        "can_invoke_provider": False,
        "can_invoke_worker": False,
    },
    "GOVERNANCE_RUNTIME_VALIDATION_ONLY": {
        "can_propose": False,
        "can_execute_authorized_task": False,
        "can_dispatch": False,
        "can_authorize": False,
        "can_govern": True,
        "can_mutate_replay": False,
        "can_mutate_governance": False,
        "can_invoke_provider": False,
        "can_invoke_worker": False,
    },
}


def default_resource_registry() -> dict[str, Any]:
    """Return the canonical resource registry with deterministic hash."""

    registry = {
        "registry_version": UNIFIED_RESOURCE_SELECTION_RUNTIME_VERSION,
        "resources": deepcopy(list(DEFAULT_RESOURCES)),
        "authority_profiles": deepcopy(AUTHORITY_PROFILES),
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "authorization_created": False,
    }
    _validate_registry(registry)
    registry["registry_hash"] = replay_hash(_registry_hash_input(registry))
    return registry


def select_unified_resource(
    *,
    selection_id: str,
    workflow_type: str,
    required_capability: str,
    requested_role_type: str,
    domain_id: str,
    created_at: str,
    replay_dir: str | Path,
    provider_necessity_classification: str | None = None,
    worker_authorization_required: bool = False,
    min_trust_level: str = "STANDARD",
    preferred_resource_id: str | None = None,
    context_assembly_output: dict[str, Any] | None = None,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Select an eligible resource and active role without invoking it."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        active_registry = deepcopy(registry) if registry is not None else default_resource_registry()
        _validate_registry(active_registry)
        registry_hash = active_registry.get("registry_hash") or replay_hash(_registry_hash_input(active_registry))
        diagnostics = _evaluate_resources(
            registry=active_registry,
            workflow_type=workflow_type,
            required_capability=required_capability,
            requested_role_type=requested_role_type,
            domain_id=domain_id,
            provider_necessity_classification=provider_necessity_classification,
            worker_authorization_required=worker_authorization_required,
            min_trust_level=min_trust_level,
            preferred_resource_id=preferred_resource_id,
        )
        selected = _select_candidate(diagnostics)
        artifact = _selection_artifact(
            selection_id=selection_id,
            registry=active_registry,
            registry_hash=registry_hash,
            workflow_type=workflow_type,
            required_capability=required_capability,
            requested_role_type=requested_role_type,
            domain_id=domain_id,
            provider_necessity_classification=provider_necessity_classification,
            worker_authorization_required=worker_authorization_required,
            min_trust_level=min_trust_level,
            preferred_resource_id=preferred_resource_id,
            context_assembly_output=context_assembly_output,
            selected=selected,
            diagnostics=diagnostics,
            created_at=created_at,
            selection_status=RESOURCE_SELECTION_SUCCEEDED,
            failure_reason=None,
        )
        returned = _returned_artifact(artifact)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, replay_path)
    except Exception as exc:
        artifact = _failed_selection_artifact(
            selection_id=selection_id,
            workflow_type=workflow_type,
            required_capability=required_capability,
            requested_role_type=requested_role_type,
            domain_id=domain_id,
            created_at=created_at,
            registry=registry,
            provider_necessity_classification=provider_necessity_classification,
            worker_authorization_required=worker_authorization_required,
            min_trust_level=min_trust_level,
            preferred_resource_id=preferred_resource_id,
            context_assembly_output=context_assembly_output,
            diagnostics=locals().get("diagnostics"),
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(artifact)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, replay_path)


def reconstruct_unified_resource_selection_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct unified resource selection replay evidence."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("resource selection replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("resource selection replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    selection = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("selection_reference") != selection["selection_id"]:
        raise FailClosedRuntimeError("resource selection replay reference mismatch")
    if returned.get("selection_hash") != selection["artifact_hash"]:
        raise FailClosedRuntimeError("resource selection replay hash mismatch")
    return {
        "selection_id": selection["selection_id"],
        "selection_status": selection["selection_status"],
        "selected_resource_id": selection["selected_resource_id"],
        "selected_resource_category": selection["selected_resource_category"],
        "selected_role_type": selection["selected_role_type"],
        "required_capability": selection["required_capability"],
        "domain_id": selection["domain_id"],
        "selection_rationale": selection["selection_rationale"],
        "registry_hash": selection["registry_hash"],
        "diagnostics_hash": selection["diagnostics"]["diagnostics_hash"],
        "failure_reason": selection["failure_reason"],
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "authorization_created": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _evaluate_resources(
    *,
    registry: dict[str, Any],
    workflow_type: str,
    required_capability: str,
    requested_role_type: str,
    domain_id: str,
    provider_necessity_classification: str | None,
    worker_authorization_required: bool,
    min_trust_level: str,
    preferred_resource_id: str | None,
) -> dict[str, Any]:
    workflow = _normalize_key(workflow_type, "workflow_type")
    capability = _normalize_key(required_capability, "required_capability")
    role = _normalize_key(requested_role_type, "requested_role_type")
    domain = _normalize_key(domain_id, "domain_id")
    minimum_trust = _normalize_key(min_trust_level, "min_trust_level")
    _validate_selection_constraints(role, provider_necessity_classification, worker_authorization_required)
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for resource in registry["resources"]:
        reason = _resource_rejection_reason(
            registry=registry,
            resource=resource,
            role=role,
            capability=capability,
            domain=domain,
            minimum_trust=minimum_trust,
            preferred_resource_id=preferred_resource_id,
        )
        if reason is None:
            binding = _matching_role_binding(resource, role)
            accepted.append(
                {
                    "resource_id": resource["resource_id"],
                    "resource_category": resource["resource_category"],
                    "resource_version": resource["resource_version"],
                    "selected_role_type": binding["role_type"],
                    "capability_matches": True,
                    "trust_matches": True,
                    "authority_matches": True,
                    "category_matches": True,
                    "role_matches": True,
                    "selection_priority": int(resource["selection_priority"]),
                    "trust_level": resource["trust_level"],
                    "authority_profile": binding["authority_profile"],
                    "selection_reason": _selection_reason(resource, binding, workflow, capability),
                }
            )
        else:
            rejected.append({"resource_id": resource["resource_id"], "reason": reason})
    diagnostics = {
        "artifact_type": RESOURCE_SELECTION_DIAGNOSTICS_V1,
        "workflow_type": workflow,
        "required_capability": capability,
        "requested_role_type": role,
        "domain_id": domain,
        "provider_necessity_classification": provider_necessity_classification,
        "worker_authorization_required": worker_authorization_required,
        "min_trust_level": minimum_trust,
        "eligible_resources": accepted,
        "rejected_resources": rejected,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
    }
    diagnostics["diagnostics_hash"] = replay_hash(diagnostics)
    return diagnostics


def _select_candidate(diagnostics: dict[str, Any]) -> dict[str, Any]:
    candidates = diagnostics["eligible_resources"]
    if not candidates:
        raise FailClosedRuntimeError("resource selection failed closed: no eligible resource exists")
    ordered = sorted(candidates, key=lambda item: (item["selection_priority"], item["resource_id"], item["selected_role_type"]))
    if len(ordered) > 1 and ordered[0]["selection_priority"] == ordered[1]["selection_priority"]:
        raise FailClosedRuntimeError("resource selection failed closed: ambiguous resource resolution")
    return deepcopy(ordered[0])


def _resource_rejection_reason(
    *,
    registry: dict[str, Any],
    resource: dict[str, Any],
    role: str,
    capability: str,
    domain: str,
    minimum_trust: str,
    preferred_resource_id: str | None,
) -> str | None:
    if preferred_resource_id is not None and _normalize_key(resource["resource_id"], "resource_id") != _normalize_key(
        preferred_resource_id, "preferred_resource_id"
    ):
        return "preferred resource mismatch"
    if resource["lifecycle_status"] not in SELECTABLE_STATUSES:
        return "resource lifecycle status is not selectable"
    if TRUST_RANK[_normalize_key(resource["trust_level"], "trust_level")] < TRUST_RANK[minimum_trust]:
        return "trust mismatch"
    binding = _find_role_binding(resource, role)
    if binding is None:
        return "role mismatch"
    if binding["role_status"] not in SELECTABLE_STATUSES:
        return "role status is not selectable"
    if capability not in {_normalize_key(value, "capability_id") for value in binding["capability_ids"]}:
        return "capability mismatch"
    if domain not in {_normalize_key(value, "domain_scope") for value in binding["domain_scope"]}:
        return "domain mismatch"
    profile = registry["authority_profiles"].get(binding["authority_profile"])
    if not isinstance(profile, dict):
        return "authority profile missing"
    if not _authority_profile_compatible(role, profile):
        return "authority mismatch"
    return None


def _validate_selection_constraints(
    role: str,
    provider_necessity_classification: str | None,
    worker_authorization_required: bool,
) -> None:
    if role == PROVIDER_ROLE:
        classification = _normalize_key(provider_necessity_classification, "provider_necessity_classification")
        if classification == PROVIDER_PROHIBITED:
            raise FailClosedRuntimeError("resource selection failed closed: provider is prohibited")
        if classification not in {PROVIDER_REQUIRED, PROVIDER_OPTIONAL}:
            raise FailClosedRuntimeError("resource selection failed closed: provider necessity mismatch")
    elif provider_necessity_classification == PROVIDER_REQUIRED:
        raise FailClosedRuntimeError("resource selection failed closed: provider necessity conflicts with selected role")
    if role == WORKER_ROLE and not worker_authorization_required:
        raise FailClosedRuntimeError("resource selection failed closed: worker authorization requirement is missing")
    if role != WORKER_ROLE and worker_authorization_required:
        raise FailClosedRuntimeError("resource selection failed closed: worker authorization conflicts with selected role")


def _authority_profile_compatible(role: str, profile: dict[str, Any]) -> bool:
    forbidden = (
        "can_dispatch",
        "can_authorize",
        "can_mutate_replay",
        "can_mutate_governance",
        "can_invoke_provider",
        "can_invoke_worker",
    )
    if any(profile.get(field) is not False for field in forbidden):
        return False
    if role == PROVIDER_ROLE:
        return profile.get("can_propose") is True and profile.get("can_execute_authorized_task") is False
    if role == WORKER_ROLE:
        return profile.get("can_execute_authorized_task") is True and profile.get("can_propose") is False
    if role == GOVERNANCE_RUNTIME_ROLE:
        return profile.get("can_govern") is True and profile.get("can_propose") is False
    return False


def _selection_artifact(
    *,
    selection_id: str,
    registry: dict[str, Any],
    registry_hash: str,
    workflow_type: str,
    required_capability: str,
    requested_role_type: str,
    domain_id: str,
    provider_necessity_classification: str | None,
    worker_authorization_required: bool,
    min_trust_level: str,
    preferred_resource_id: str | None,
    context_assembly_output: dict[str, Any] | None,
    selected: dict[str, Any],
    diagnostics: dict[str, Any],
    created_at: str,
    selection_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": RESOURCE_SELECTION_ARTIFACT_V1,
        "status_artifact_type": RESOURCE_SELECTION_STATUS_V1,
        "runtime_version": UNIFIED_RESOURCE_SELECTION_RUNTIME_VERSION,
        "registry_version": registry.get("registry_version", UNIFIED_RESOURCE_SELECTION_RUNTIME_VERSION),
        "registry_hash": _require_string(registry_hash, "registry_hash"),
        "selection_id": _require_string(selection_id, "selection_id"),
        "workflow_type": _require_string(workflow_type, "workflow_type"),
        "required_capability": _require_string(required_capability, "required_capability"),
        "requested_role_type": _require_string(requested_role_type, "requested_role_type"),
        "domain_id": _require_string(domain_id, "domain_id"),
        "provider_necessity_classification": provider_necessity_classification,
        "worker_authorization_required": worker_authorization_required,
        "min_trust_level": _require_string(min_trust_level, "min_trust_level"),
        "preferred_resource_id": preferred_resource_id,
        "context_reference": _context_reference(context_assembly_output),
        "context_hash": _context_hash(context_assembly_output),
        "selection_status": selection_status,
        "selected_resource_id": selected["resource_id"],
        "selected_resource_category": selected["resource_category"],
        "selected_resource_version": selected["resource_version"],
        "selected_role_type": selected["selected_role_type"],
        "selected_authority_profile": selected["authority_profile"],
        "selection_rationale": selected["selection_reason"],
        "capability_matches": selected["capability_matches"],
        "trust_matches": selected["trust_matches"],
        "authority_matches": selected["authority_matches"],
        "category_matches": selected["category_matches"],
        "role_matches": selected["role_matches"],
        "diagnostics": deepcopy(diagnostics),
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "authorization_created": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_selection_artifact(
    *,
    selection_id: str,
    workflow_type: str,
    required_capability: str,
    requested_role_type: str,
    domain_id: str,
    created_at: str,
    registry: dict[str, Any] | None,
    provider_necessity_classification: str | None,
    worker_authorization_required: bool,
    min_trust_level: str,
    preferred_resource_id: str | None,
    context_assembly_output: dict[str, Any] | None,
    diagnostics: dict[str, Any] | None,
    failure_reason: str,
) -> dict[str, Any]:
    active_registry = deepcopy(registry) if isinstance(registry, dict) else default_resource_registry()
    registry_hash = active_registry.get("registry_hash") or replay_hash(_registry_hash_input(active_registry))
    if not isinstance(diagnostics, dict):
        diagnostics = {
            "artifact_type": RESOURCE_SELECTION_DIAGNOSTICS_V1,
            "eligible_resources": [],
            "rejected_resources": [],
            "failure_reason": failure_reason,
        }
    else:
        diagnostics = deepcopy(diagnostics)
        diagnostics["failure_reason"] = failure_reason
        diagnostics.pop("diagnostics_hash", None)
    diagnostics["diagnostics_hash"] = replay_hash(diagnostics)
    artifact = {
        "artifact_type": RESOURCE_SELECTION_ARTIFACT_V1,
        "status_artifact_type": RESOURCE_SELECTION_STATUS_V1,
        "runtime_version": UNIFIED_RESOURCE_SELECTION_RUNTIME_VERSION,
        "registry_version": active_registry.get("registry_version", UNIFIED_RESOURCE_SELECTION_RUNTIME_VERSION),
        "registry_hash": registry_hash,
        "selection_id": _require_string(selection_id, "selection_id"),
        "workflow_type": workflow_type,
        "required_capability": required_capability,
        "requested_role_type": requested_role_type,
        "domain_id": domain_id,
        "provider_necessity_classification": provider_necessity_classification,
        "worker_authorization_required": worker_authorization_required,
        "min_trust_level": min_trust_level,
        "preferred_resource_id": preferred_resource_id,
        "context_reference": _context_reference(context_assembly_output),
        "context_hash": _context_hash(context_assembly_output),
        "selection_status": FAILED_CLOSED,
        "selected_resource_id": None,
        "selected_resource_category": None,
        "selected_resource_version": None,
        "selected_role_type": None,
        "selected_authority_profile": None,
        "selection_rationale": None,
        "capability_matches": False,
        "trust_matches": False,
        "authority_matches": False,
        "category_matches": False,
        "role_matches": False,
        "diagnostics": diagnostics,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "authorization_created": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(selection: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(selection)
    returned = {
        "event_type": "RESOURCE_SELECTION_RETURNED",
        "selection_reference": selection["selection_id"],
        "selection_hash": selection["artifact_hash"],
        "selection_status": selection["selection_status"],
        "selected_resource_id": selection["selected_resource_id"],
        "selected_resource_category": selection["selected_resource_category"],
        "selected_role_type": selection["selected_role_type"],
        "registry_hash": selection["registry_hash"],
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "failure_reason": selection["failure_reason"],
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(selection: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "resource_selection_artifact": deepcopy(selection),
        "resource_selection_status": {
            "artifact_type": RESOURCE_SELECTION_STATUS_V1,
            "selection_status": selection["selection_status"],
            "selected_resource_id": selection["selected_resource_id"],
            "selected_resource_category": selection["selected_resource_category"],
            "selected_role_type": selection["selected_role_type"],
            "failure_reason": selection["failure_reason"],
        },
        "resource_selection_diagnostics": deepcopy(selection["diagnostics"]),
        "resource_selection_replay": deepcopy(returned),
        "resource_selection_replay_reference": str(replay_path),
        "selection_status": selection["selection_status"],
        "selected_resource_id": selection["selected_resource_id"],
        "selected_resource_category": selection["selected_resource_category"],
        "selected_role_type": selection["selected_role_type"],
        "selection_rationale": selection["selection_rationale"],
        "registry_hash": selection["registry_hash"],
        "fail_closed": selection["selection_status"] == FAILED_CLOSED,
        "failure_reason": selection["failure_reason"],
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "authorization_created": False,
    }
    capture["resource_selection_capture_hash"] = replay_hash(capture)
    return capture


def _validate_registry(registry: dict[str, Any]) -> None:
    if registry.get("registry_version") != UNIFIED_RESOURCE_SELECTION_RUNTIME_VERSION:
        raise FailClosedRuntimeError("resource selection failed closed: invalid registry version")
    resources = _require_list(registry.get("resources"), "resources")
    profiles = registry.get("authority_profiles")
    if not isinstance(profiles, dict) or not profiles:
        raise FailClosedRuntimeError("resource selection failed closed: authority profiles are required")
    ids = [_normalize_key(resource.get("resource_id"), "resource_id") for resource in resources if isinstance(resource, dict)]
    if len(ids) != len(resources) or len(set(ids)) != len(ids):
        raise FailClosedRuntimeError("resource selection failed closed: duplicate resource registration")
    for resource in resources:
        _validate_resource(resource, profiles)


def _validate_resource(resource: dict[str, Any], profiles: dict[str, Any]) -> None:
    category = _normalize_key(resource.get("resource_category"), "resource_category")
    if category not in {PROVIDER, WORKER, HYBRID_PROVIDER_WORKER, OPERATOR_TOOL, GOVERNANCE_RUNTIME, DOMAIN_RUNTIME}:
        raise FailClosedRuntimeError("resource selection failed closed: invalid resource category")
    _require_string(resource.get("resource_id"), "resource_id")
    _require_string(resource.get("resource_version"), "resource_version")
    _normalize_key(resource.get("trust_level"), "trust_level")
    if _normalize_key(resource["trust_level"], "trust_level") not in TRUST_RANK:
        raise FailClosedRuntimeError("resource selection failed closed: invalid trust level")
    int(resource.get("selection_priority"))
    bindings = _require_list(resource.get("role_bindings"), "role_bindings")
    role_keys = []
    for binding in bindings:
        role = _normalize_key(binding.get("role_type"), "role_type")
        role_keys.append(role)
        _require_list(binding.get("capability_ids"), "capability_ids")
        _require_list(binding.get("domain_scope"), "domain_scope")
        profile_id = _require_string(binding.get("authority_profile"), "authority_profile")
        if profile_id not in profiles:
            raise FailClosedRuntimeError("resource selection failed closed: authority profile missing")
        if not _authority_profile_compatible(role, profiles[profile_id]):
            raise FailClosedRuntimeError("resource selection failed closed: authority mismatch")
    if len(set(role_keys)) != len(role_keys):
        raise FailClosedRuntimeError("resource selection failed closed: duplicate role binding")


def _find_role_binding(resource: dict[str, Any], role: str) -> dict[str, Any] | None:
    matches = [binding for binding in resource["role_bindings"] if _normalize_key(binding["role_type"], "role_type") == role]
    if len(matches) > 1:
        raise FailClosedRuntimeError("resource selection failed closed: ambiguous resource resolution")
    return deepcopy(matches[0]) if matches else None


def _matching_role_binding(resource: dict[str, Any], role: str) -> dict[str, Any]:
    binding = _find_role_binding(resource, role)
    if binding is None:
        raise FailClosedRuntimeError("resource selection failed closed: role mismatch")
    return binding


def _selection_reason(resource: dict[str, Any], binding: dict[str, Any], workflow: str, capability: str) -> str:
    return (
        f"{resource['resource_id']} selected for {workflow} as {binding['role_type']} "
        f"because capability {capability}, authority, trust, category, and role matched."
    )


def _registry_hash_input(registry: dict[str, Any]) -> dict[str, Any]:
    return {
        "registry_version": registry.get("registry_version"),
        "resources": registry.get("resources"),
        "authority_profiles": registry.get("authority_profiles"),
    }


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("resource selection replay step ordering mismatch")
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
        raise FailClosedRuntimeError("resource selection artifact hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("resource selection artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("resource selection replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("resource selection replay hash mismatch")


def _context_reference(context_assembly_output: dict[str, Any] | None) -> str | None:
    if not isinstance(context_assembly_output, dict):
        return None
    value = context_assembly_output.get("context_reference") or context_assembly_output.get("context_id")
    return value if isinstance(value, str) and value.strip() else None


def _context_hash(context_assembly_output: dict[str, Any] | None) -> str | None:
    if not isinstance(context_assembly_output, dict):
        return None
    value = context_assembly_output.get("context_hash") or context_assembly_output.get("artifact_hash")
    return value if isinstance(value, str) and value.strip() else None


def _normalize_key(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).upper().replace("-", "_").replace(" ", "_")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _require_list(value: Any, field_name: str) -> list[Any]:
    if isinstance(value, tuple):
        return list(value)
    if not isinstance(value, list) or not value:
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "resource selection failed closed"
