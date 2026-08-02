"""Authenticated provider-selection binding for specialized provider runtimes.

This module does not select a provider.  It binds specialized runtime entry
points to the existing Unified Resource Selection owner and preserves the
owner's replay evidence for later reconstruction.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_necessity_policy_runtime import PROVIDER_REQUIRED
from aigol.runtime.transport.serialization import replay_hash
from aigol.runtime.unified_resource_selection_runtime import (
    PROVIDER_ROLE,
    RESOURCE_SELECTION_SUCCEEDED,
    UNIFIED_RESOURCE_SELECTION_RUNTIME_VERSION,
    reconstruct_unified_resource_selection_replay,
    select_unified_resource,
)


AUTHENTICATED_PROVIDER_SELECTION_BINDING_V1 = "AUTHENTICATED_PROVIDER_SELECTION_BINDING_V1"
AUTHENTICATED_PROVIDER_SELECTION_OWNER = UNIFIED_RESOURCE_SELECTION_RUNTIME_VERSION
SELECTION_REPLAY_DIRECTORY = "provider_selection"
_CANONICAL_RESOURCE_IDS = {"openai": "OPENAI"}


def select_authenticated_provider(
    *,
    selection_id: str,
    provider_id: str,
    workflow_type: str,
    required_capability: str,
    domain_id: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Require the canonical selection owner to select one explicit provider."""

    normalized_provider_id = _normalize_provider_id(provider_id)
    expected_resource_id = _CANONICAL_RESOURCE_IDS.get(normalized_provider_id)
    if expected_resource_id is None:
        raise FailClosedRuntimeError("provider is not registered with the authenticated selection owner")

    selection_path = Path(replay_dir) / SELECTION_REPLAY_DIRECTORY
    capture = select_unified_resource(
        selection_id=_require_string(selection_id, "selection_id"),
        workflow_type=_require_string(workflow_type, "workflow_type"),
        required_capability=_require_string(required_capability, "required_capability"),
        requested_role_type=PROVIDER_ROLE,
        domain_id=_require_string(domain_id, "domain_id"),
        provider_necessity_classification=PROVIDER_REQUIRED,
        preferred_resource_id=expected_resource_id,
        created_at=_require_string(created_at, "created_at"),
        replay_dir=selection_path,
    )
    artifact = capture.get("resource_selection_artifact")
    if not isinstance(artifact, dict) or capture.get("selection_status") != RESOURCE_SELECTION_SUCCEEDED:
        raise FailClosedRuntimeError("authenticated provider selection failed closed")
    if capture.get("selected_resource_id") != expected_resource_id:
        raise FailClosedRuntimeError("authenticated provider selection identity mismatch")
    if capture.get("selected_role_type") != PROVIDER_ROLE:
        raise FailClosedRuntimeError("authenticated provider selection role mismatch")

    reconstructed = reconstruct_unified_resource_selection_replay(selection_path)
    if reconstructed["selected_resource_id"] != expected_resource_id:
        raise FailClosedRuntimeError("authenticated provider selection replay identity mismatch")
    if reconstructed["selection_status"] != RESOURCE_SELECTION_SUCCEEDED:
        raise FailClosedRuntimeError("authenticated provider selection replay did not succeed")

    binding = {
        "artifact_type": AUTHENTICATED_PROVIDER_SELECTION_BINDING_V1,
        "selection_owner": AUTHENTICATED_PROVIDER_SELECTION_OWNER,
        "selection_id": artifact["selection_id"],
        "selection_hash": artifact["artifact_hash"],
        "selection_replay_hash": reconstructed["replay_hash"],
        "selected_resource_id": expected_resource_id,
        "provider_id": normalized_provider_id,
        "required_capability": artifact["required_capability"],
        "workflow_type": artifact["workflow_type"],
        "domain_id": artifact["domain_id"],
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "authorization_created": False,
    }
    binding["artifact_hash"] = replay_hash(binding)
    return binding


def validate_authenticated_provider_selection(
    *,
    binding: dict[str, Any],
    provider_id: str,
    required_capability: str,
) -> dict[str, Any]:
    """Validate a selection binding without performing selection or invocation."""

    if not isinstance(binding, dict):
        raise FailClosedRuntimeError("authenticated provider selection binding is required")
    if binding.get("artifact_type") != AUTHENTICATED_PROVIDER_SELECTION_BINDING_V1:
        raise FailClosedRuntimeError("authenticated provider selection binding type is invalid")
    _verify_artifact_hash(binding)
    normalized_provider_id = _normalize_provider_id(provider_id)
    if binding.get("selection_owner") != AUTHENTICATED_PROVIDER_SELECTION_OWNER:
        raise FailClosedRuntimeError("provider selection owner is not authenticated")
    if binding.get("provider_id") != normalized_provider_id:
        raise FailClosedRuntimeError("authenticated provider selection provider mismatch")
    if binding.get("selected_resource_id") != _CANONICAL_RESOURCE_IDS.get(normalized_provider_id):
        raise FailClosedRuntimeError("authenticated provider selection resource mismatch")
    if binding.get("required_capability") != _require_string(required_capability, "required_capability"):
        raise FailClosedRuntimeError("authenticated provider selection capability mismatch")
    for flag in ("replay_visible",):
        if binding.get(flag) is not True:
            raise FailClosedRuntimeError("authenticated provider selection is not replay-visible")
    for flag in ("provider_invoked", "worker_invoked", "execution_requested", "authorization_created"):
        if binding.get(flag) is not False:
            raise FailClosedRuntimeError("authenticated provider selection carries prohibited authority")
    return deepcopy(binding)


def reconstruct_authenticated_provider_selection(
    *,
    replay_dir: str | Path,
    binding: dict[str, Any],
    provider_id: str,
    required_capability: str,
) -> dict[str, Any]:
    """Reconstruct and bind canonical selection replay to one provider request."""

    validated = validate_authenticated_provider_selection(
        binding=binding,
        provider_id=provider_id,
        required_capability=required_capability,
    )
    reconstructed = reconstruct_unified_resource_selection_replay(Path(replay_dir) / SELECTION_REPLAY_DIRECTORY)
    if reconstructed["selection_id"] != validated["selection_id"]:
        raise FailClosedRuntimeError("authenticated provider selection replay reference mismatch")
    if reconstructed["selected_resource_id"] != validated["selected_resource_id"]:
        raise FailClosedRuntimeError("authenticated provider selection replay resource mismatch")
    if reconstructed["required_capability"] != validated["required_capability"]:
        raise FailClosedRuntimeError("authenticated provider selection replay capability mismatch")
    if reconstructed["replay_hash"] != validated["selection_replay_hash"]:
        raise FailClosedRuntimeError("authenticated provider selection replay hash mismatch")
    return reconstructed


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("authenticated provider selection hash is required")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("authenticated provider selection hash mismatch")


def _normalize_provider_id(value: Any) -> str:
    return _require_string(value, "provider_id").strip().lower()


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
