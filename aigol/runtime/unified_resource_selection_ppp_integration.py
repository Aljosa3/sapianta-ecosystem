"""Replay-visible integration between unified resource selection and PPP."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.unified_resource_selection_runtime import (
    HYBRID_PROVIDER_WORKER,
    PROVIDER,
    PROVIDER_ROLE,
    RESOURCE_SELECTION_ARTIFACT_V1,
    RESOURCE_SELECTION_SUCCEEDED,
    WORKER,
    WORKER_ROLE,
)


UNIFIED_RESOURCE_SELECTION_PPP_INTEGRATION_VERSION = "UNIFIED_RESOURCE_SELECTION_PPP_INTEGRATION_V1"
RESOURCE_PPP_INTEGRATION_ARTIFACT_V1 = "RESOURCE_PPP_INTEGRATION_ARTIFACT_V1"
RESOURCE_PPP_INTEGRATED = "RESOURCE_PPP_INTEGRATED"
PPP_PROVIDER_PROPOSAL_READY = "PPP_PROVIDER_PROPOSAL_READY"
PPP_WORKER_HANDOFF_REFERENCE_READY = "PPP_WORKER_HANDOFF_REFERENCE_READY"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "resource_ppp_integration_recorded",
    "resource_ppp_integration_returned",
)


def integrate_resource_selection_with_ppp(
    *,
    integration_id: str,
    resource_selection_artifact: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
    context_assembly_artifact: dict[str, Any] | None = None,
    ppp_stage: str = "PROPOSAL_PRODUCTION",
) -> dict[str, Any]:
    """Validate a selected resource as PPP-consumable without invoking it."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        selection = deepcopy(resource_selection_artifact)
        _validate_selection_artifact(selection)
        context_reference = _context_reference(context_assembly_artifact)
        context_hash = _context_hash(context_assembly_artifact)
        integration_status = _ppp_status_for_selection(selection, ppp_stage)
        artifact = _integration_artifact(
            integration_id=integration_id,
            selection=selection,
            context_reference=context_reference,
            context_hash=context_hash,
            ppp_stage=ppp_stage,
            integration_status=RESOURCE_PPP_INTEGRATED,
            ppp_resource_status=integration_status,
            created_at=created_at,
            failure_reason=None,
        )
        returned = _returned_artifact(artifact)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, replay_path)
    except Exception as exc:
        artifact = _failed_integration_artifact(
            integration_id=integration_id,
            resource_selection_artifact=resource_selection_artifact,
            context_assembly_artifact=context_assembly_artifact,
            ppp_stage=ppp_stage,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(artifact)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, replay_path)


def reconstruct_resource_selection_ppp_integration_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct resource selection PPP integration replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("resource PPP integration replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("resource PPP integration replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    integration = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("integration_reference") != integration["integration_id"]:
        raise FailClosedRuntimeError("resource PPP integration replay reference mismatch")
    if returned.get("integration_hash") != integration["artifact_hash"]:
        raise FailClosedRuntimeError("resource PPP integration replay hash mismatch")
    return {
        "integration_id": integration["integration_id"],
        "integration_status": integration["integration_status"],
        "ppp_resource_status": integration["ppp_resource_status"],
        "selected_resource_id": integration["selected_resource_id"],
        "selected_resource_category": integration["selected_resource_category"],
        "selected_role_type": integration["selected_role_type"],
        "selection_hash": integration["selection_hash"],
        "context_hash": integration["context_hash"],
        "failure_reason": integration["failure_reason"],
        "provider_invoked": False,
        "worker_invoked": False,
        "dispatch_requested": False,
        "execution_requested": False,
        "authorization_created": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _validate_selection_artifact(selection: dict[str, Any]) -> None:
    if selection.get("artifact_type") != RESOURCE_SELECTION_ARTIFACT_V1:
        raise FailClosedRuntimeError("resource PPP integration failed closed: resource selection missing")
    _verify_artifact_hash(selection)
    if selection.get("selection_status") != RESOURCE_SELECTION_SUCCEEDED:
        raise FailClosedRuntimeError("resource PPP integration failed closed: resource selection did not succeed")
    role = _require_string(selection.get("selected_role_type"), "selected_role_type")
    category = _require_string(selection.get("selected_resource_category"), "selected_resource_category")
    if role not in {PROVIDER_ROLE, WORKER_ROLE}:
        raise FailClosedRuntimeError("resource PPP integration failed closed: resource role ambiguous")
    if category == PROVIDER and role != PROVIDER_ROLE:
        raise FailClosedRuntimeError("resource PPP integration failed closed: resource role ambiguous")
    if category == WORKER and role != WORKER_ROLE:
        raise FailClosedRuntimeError("resource PPP integration failed closed: resource role ambiguous")
    if category == HYBRID_PROVIDER_WORKER and role not in {PROVIDER_ROLE, WORKER_ROLE}:
        raise FailClosedRuntimeError("resource PPP integration failed closed: resource role ambiguous")
    if selection.get("capability_matches") is not True:
        raise FailClosedRuntimeError("resource PPP integration failed closed: capability mismatch")
    if selection.get("trust_matches") is not True:
        raise FailClosedRuntimeError("resource PPP integration failed closed: trust mismatch")
    if selection.get("authority_matches") is not True:
        raise FailClosedRuntimeError("resource PPP integration failed closed: authority mismatch")
    if selection.get("provider_invoked") is not False or selection.get("worker_invoked") is not False:
        raise FailClosedRuntimeError("resource PPP integration failed closed: replay inconsistency")
    if selection.get("execution_requested") is not False or selection.get("dispatch_requested") is not False:
        raise FailClosedRuntimeError("resource PPP integration failed closed: replay inconsistency")


def _ppp_status_for_selection(selection: dict[str, Any], ppp_stage: str) -> str:
    stage = _require_string(ppp_stage, "ppp_stage")
    role = selection["selected_role_type"]
    if role == PROVIDER_ROLE:
        if stage not in {"PROPOSAL_PRODUCTION", "PROPOSAL_REPAIR", "CLARIFICATION"}:
            raise FailClosedRuntimeError("resource PPP integration failed closed: capability mismatch")
        return PPP_PROVIDER_PROPOSAL_READY
    if role == WORKER_ROLE:
        if stage not in {"IMPLEMENTATION_HANDOFF", "WORKER_LIFECYCLE_PROPOSAL"}:
            raise FailClosedRuntimeError("resource PPP integration failed closed: capability mismatch")
        return PPP_WORKER_HANDOFF_REFERENCE_READY
    raise FailClosedRuntimeError("resource PPP integration failed closed: resource role ambiguous")


def _integration_artifact(
    *,
    integration_id: str,
    selection: dict[str, Any],
    context_reference: str | None,
    context_hash: str | None,
    ppp_stage: str,
    integration_status: str,
    ppp_resource_status: str,
    created_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": RESOURCE_PPP_INTEGRATION_ARTIFACT_V1,
        "runtime_version": UNIFIED_RESOURCE_SELECTION_PPP_INTEGRATION_VERSION,
        "integration_id": _require_string(integration_id, "integration_id"),
        "integration_status": integration_status,
        "ppp_resource_status": ppp_resource_status,
        "ppp_stage": _require_string(ppp_stage, "ppp_stage"),
        "selection_reference": selection["selection_id"],
        "selection_hash": selection["artifact_hash"],
        "selected_resource_id": selection["selected_resource_id"],
        "selected_resource_category": selection["selected_resource_category"],
        "selected_resource_version": selection["selected_resource_version"],
        "selected_role_type": selection["selected_role_type"],
        "selected_authority_profile": selection["selected_authority_profile"],
        "selection_rationale": selection["selection_rationale"],
        "capability_matches": selection["capability_matches"],
        "trust_matches": selection["trust_matches"],
        "authority_matches": selection["authority_matches"],
        "category_matches": selection["category_matches"],
        "role_matches": selection["role_matches"],
        "context_reference": context_reference,
        "context_hash": context_hash,
        "provider_invoked": False,
        "worker_invoked": False,
        "dispatch_requested": False,
        "execution_requested": False,
        "authorization_created": False,
        "provider_authority_created": False,
        "worker_authority_created": False,
        "governance_mutated": False,
        "replay_visible": True,
        "created_at": _require_string(created_at, "created_at"),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_integration_artifact(
    *,
    integration_id: str,
    resource_selection_artifact: dict[str, Any],
    context_assembly_artifact: dict[str, Any] | None,
    ppp_stage: str,
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    selection = resource_selection_artifact if isinstance(resource_selection_artifact, dict) else {}
    artifact = {
        "artifact_type": RESOURCE_PPP_INTEGRATION_ARTIFACT_V1,
        "runtime_version": UNIFIED_RESOURCE_SELECTION_PPP_INTEGRATION_VERSION,
        "integration_id": _require_string(integration_id, "integration_id"),
        "integration_status": FAILED_CLOSED,
        "ppp_resource_status": FAILED_CLOSED,
        "ppp_stage": ppp_stage,
        "selection_reference": selection.get("selection_id"),
        "selection_hash": selection.get("artifact_hash"),
        "selected_resource_id": selection.get("selected_resource_id"),
        "selected_resource_category": selection.get("selected_resource_category"),
        "selected_resource_version": selection.get("selected_resource_version"),
        "selected_role_type": selection.get("selected_role_type"),
        "selected_authority_profile": selection.get("selected_authority_profile"),
        "selection_rationale": selection.get("selection_rationale"),
        "capability_matches": selection.get("capability_matches") is True,
        "trust_matches": selection.get("trust_matches") is True,
        "authority_matches": selection.get("authority_matches") is True,
        "category_matches": selection.get("category_matches") is True,
        "role_matches": selection.get("role_matches") is True,
        "context_reference": _context_reference(context_assembly_artifact),
        "context_hash": _context_hash(context_assembly_artifact),
        "provider_invoked": False,
        "worker_invoked": False,
        "dispatch_requested": False,
        "execution_requested": False,
        "authorization_created": False,
        "provider_authority_created": False,
        "worker_authority_created": False,
        "governance_mutated": False,
        "replay_visible": True,
        "created_at": _require_string(created_at, "created_at"),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(integration: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(integration)
    returned = {
        "event_type": "RESOURCE_PPP_INTEGRATION_RETURNED",
        "integration_reference": integration["integration_id"],
        "integration_hash": integration["artifact_hash"],
        "integration_status": integration["integration_status"],
        "ppp_resource_status": integration["ppp_resource_status"],
        "selected_resource_id": integration["selected_resource_id"],
        "selected_resource_category": integration["selected_resource_category"],
        "selected_role_type": integration["selected_role_type"],
        "provider_invoked": False,
        "worker_invoked": False,
        "dispatch_requested": False,
        "execution_requested": False,
        "authorization_created": False,
        "replay_visible": True,
        "failure_reason": integration["failure_reason"],
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(integration: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "resource_ppp_integration_artifact": deepcopy(integration),
        "resource_ppp_integration_replay": deepcopy(returned),
        "resource_ppp_integration_replay_reference": str(replay_path),
        "integration_status": integration["integration_status"],
        "ppp_resource_status": integration["ppp_resource_status"],
        "selected_resource_id": integration["selected_resource_id"],
        "selected_resource_category": integration["selected_resource_category"],
        "selected_role_type": integration["selected_role_type"],
        "capability_matches": integration["capability_matches"],
        "trust_matches": integration["trust_matches"],
        "authority_matches": integration["authority_matches"],
        "fail_closed": integration["integration_status"] == FAILED_CLOSED,
        "failure_reason": integration["failure_reason"],
        "provider_invoked": False,
        "worker_invoked": False,
        "dispatch_requested": False,
        "execution_requested": False,
        "authorization_created": False,
    }
    capture["resource_ppp_integration_capture_hash"] = replay_hash(capture)
    return capture


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("resource PPP integration replay step ordering mismatch")
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
        raise FailClosedRuntimeError("resource PPP integration artifact hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("resource PPP integration artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("resource PPP integration replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("resource PPP integration replay hash mismatch")


def _context_reference(context_assembly_artifact: dict[str, Any] | None) -> str | None:
    if not isinstance(context_assembly_artifact, dict):
        return None
    value = context_assembly_artifact.get("context_reference") or context_assembly_artifact.get("context_id")
    return value if isinstance(value, str) and value.strip() else None


def _context_hash(context_assembly_artifact: dict[str, Any] | None) -> str | None:
    if not isinstance(context_assembly_artifact, dict):
        return None
    value = context_assembly_artifact.get("context_hash") or context_assembly_artifact.get("artifact_hash")
    return value if isinstance(value, str) and value.strip() else None


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "resource PPP integration failed closed"
