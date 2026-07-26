"""Filesystem-specific authentication for the neutral Worker selection boundary."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import (
    load_json,
    replay_hash,
    verify_replay_hash,
)
from aigol.runtime.unified_resource_selection_runtime import (
    RESOURCE_SELECTION_SUCCEEDED,
    default_resource_registry,
    reconstruct_unified_resource_selection_replay,
)
from aigol.runtime.worker_invocation_request_runtime import (
    WORKER_SELECTION_LINEAGE_PROJECTION_V1,
)
from aigol.runtime.worker_selection_certification_v1 import (
    validate_worker_selection_certification_v1,
)
from aigol.workers.filesystem_replace_worker import (
    reconstruct_authenticated_replace_replay_v2,
    validate_authenticated_replace_request_v2,
)


RUNTIME_VERSION = (
    "G31_FILESYSTEM_REPLACE_WORKER_SELECTION_LINEAGE_RESOLVER_V1"
)
AUTHENTICATED_REPLACEMENT_SELECTION_LINEAGE_V1 = (
    "AUTHENTICATED_REPLACEMENT_SELECTION_LINEAGE_V1"
)

AUTHORITY_FLAGS = {
    "authorizes_execution": False,
    "selects_workers": False,
    "assigns_workers": False,
    "dispatches_workers": False,
    "invokes_workers": False,
    "invokes_providers": False,
    "executes_commands": False,
    "mutates_repository": False,
    "mutates_governance": False,
    "mutates_replay": False,
}


def resolve_authenticated_replacement_worker_selection_lineage(
    *,
    authenticated_request: dict[str, Any],
    consumption_reconstruction: dict[str, Any],
    resource_selection_capture: dict[str, Any],
    worker_selection_certification_reference: str | Path,
    anchor: str | Path,
) -> dict[str, Any]:
    """Authenticate Filesystem lineage and return one neutral immutable projection."""

    request = validate_authenticated_replace_request_v2(authenticated_request)
    if not isinstance(consumption_reconstruction, dict) or not isinstance(
        resource_selection_capture, dict
    ):
        raise FailClosedRuntimeError(
            "Filesystem selection lineage resolver failed closed: lineage is incomplete"
        )
    session_root = Path(request["session_root"]).resolve()
    request_replay = _reconstruct_consumption_prefix(request)
    selection_reference = _resolve_reference(
        resource_selection_capture.get("resource_selection_replay_reference"),
        anchor=Path(anchor),
    ).resolve()
    if not selection_reference.is_relative_to(session_root):
        raise FailClosedRuntimeError(
            "Filesystem selection lineage resolver failed closed: selection "
            "is cross-session"
        )
    selection_reconstruction = reconstruct_unified_resource_selection_replay(
        selection_reference
    )
    selection_wrapper = load_json(
        selection_reference / "000_resource_selection_recorded.json"
    )
    _verify_wrapper(selection_wrapper)
    selection = selection_wrapper.get("artifact")
    if not isinstance(selection, dict):
        raise FailClosedRuntimeError(
            "Filesystem selection lineage resolver failed closed: selection missing"
        )
    _verify_artifact(selection, "Worker selection artifact")

    certification_reference = _resolve_reference(
        worker_selection_certification_reference,
        anchor=Path(anchor),
    ).resolve()
    try:
        certification = validate_worker_selection_certification_v1(
            load_json(certification_reference),
            default_resource_registry(),
        )
    except (OSError, ValueError, TypeError) as exc:
        raise FailClosedRuntimeError(
            "Filesystem selection lineage resolver failed closed: selection "
            "certification unavailable"
        ) from exc
    context = resource_selection_capture.get(
        "consumed_replacement_selection_context"
    )
    context_hash = resource_selection_capture.get(
        "consumed_replacement_selection_context_hash"
    )
    parent = resource_selection_capture.get(
        "parent_request_consumption_reconstruction"
    )
    captured_reconstruction = resource_selection_capture.get(
        "certified_selection_reconstruction"
    )
    if not isinstance(context, dict) or context_hash != replay_hash(context):
        raise FailClosedRuntimeError(
            "Filesystem selection lineage resolver failed closed: selection "
            "context invalid"
        )
    if not isinstance(parent, dict) or not all(
        (
            request_replay.get("event_keys") == ["request", "consumption"],
            request_replay.get("latest_event")
            == "AUTHORIZATION_CONSUMPTION_CLAIMED",
            request_replay.get("replay_artifact_count") == 2,
            parent == request_replay,
            consumption_reconstruction.get("request_id") == request["request_id"],
            consumption_reconstruction.get("request_hash")
            == request["request_hash"],
            consumption_reconstruction.get("authorization_id")
            == request["authorization_id"],
            consumption_reconstruction.get("authorization_hash")
            == request["authorization_hash"],
            consumption_reconstruction.get("consumption_identity")
            == request["authorization_hash"],
            consumption_reconstruction.get("request_replay_reference")
            == request_replay["request_replay_reference"],
            consumption_reconstruction.get("replay_hash")
            == request_replay["replay_hash"],
            consumption_reconstruction.get("authorization_consumed") is True,
            consumption_reconstruction.get("worker_selected") is False,
            consumption_reconstruction.get("worker_dispatched") is False,
            consumption_reconstruction.get("worker_invoked") is False,
            consumption_reconstruction.get("provider_invoked") is False,
            consumption_reconstruction.get("command_executed") is False,
            consumption_reconstruction.get("repository_mutated") is False,
        )
    ):
        raise FailClosedRuntimeError(
            "Filesystem selection lineage resolver failed closed: consumption "
            "lineage mismatch"
        )
    if not all(
        (
            resource_selection_capture.get("selection_status")
            == RESOURCE_SELECTION_SUCCEEDED,
            resource_selection_capture.get("resource_selection_artifact")
            == selection,
            captured_reconstruction == selection_reconstruction,
            selection_reconstruction.get("selection_status")
            == RESOURCE_SELECTION_SUCCEEDED,
            selection.get("selected_resource_id") == request["worker_id"],
            selection.get("required_capability") == request["worker_operation"],
            selection.get("selected_role_type") == context.get("role_type"),
            selection.get("selected_authority_profile")
            == context.get("authority_profile"),
            selection.get("selected_resource_version")
            == context.get("worker_version"),
            selection.get("context_reference") == context.get("context_identity"),
            selection.get("context_hash") == context_hash,
            context.get("authenticated_request_identity") == request["request_id"],
            context.get("authenticated_request_hash") == request["request_hash"],
            context.get("authorization_identity") == request["authorization_id"],
            context.get("authorization_hash") == request["authorization_hash"],
            context.get("consumption_identity")
            == consumption_reconstruction.get("consumption_identity"),
            context.get("consumption_replay_hash") == request_replay["replay_hash"],
            context.get("certified_registry_hash") == selection.get("registry_hash"),
            context.get("certification_report_hash")
            == certification["artifact_hash"],
            selection.get("provider_invoked") is False,
            selection.get("worker_invoked") is False,
            selection.get("dispatch_requested") is False,
            resource_selection_capture.get("worker_assigned") is False,
            resource_selection_capture.get("worker_dispatched") is False,
            resource_selection_capture.get("execution_requested") is False,
            resource_selection_capture.get("command_executed") is False,
            resource_selection_capture.get("repository_mutated") is False,
        )
    ):
        raise FailClosedRuntimeError(
            "Filesystem selection lineage resolver failed closed: selection "
            "lineage mismatch"
        )

    source_lineage = {
        "lineage_type": AUTHENTICATED_REPLACEMENT_SELECTION_LINEAGE_V1,
        "authenticated_request": deepcopy(request),
        "consumption_reconstruction": deepcopy(consumption_reconstruction),
        "resource_selection_capture": {
            "resource_selection_artifact": deepcopy(selection),
            "resource_selection_replay_reference": str(selection_reference),
            "consumed_replacement_selection_context": deepcopy(context),
            "consumed_replacement_selection_context_hash": context_hash,
            "parent_request_consumption_reconstruction": deepcopy(parent),
            "certified_selection_reconstruction": deepcopy(
                selection_reconstruction
            ),
            "selection_status": resource_selection_capture["selection_status"],
            "worker_assigned": False,
            "worker_dispatched": False,
            "provider_invoked": False,
            "worker_invoked": False,
            "execution_requested": False,
            "command_executed": False,
            "repository_mutated": False,
        },
        "worker_selection_certification_reference": str(certification_reference),
        "worker_selection_certification_hash": certification["artifact_hash"],
    }
    projection = {
        **deepcopy(source_lineage),
        "artifact_type": WORKER_SELECTION_LINEAGE_PROJECTION_V1,
        "runtime_version": RUNTIME_VERSION,
        "projection_id": f"{request['request_id']}:WORKER-SELECTION-LINEAGE",
        "source_lineage_type": AUTHENTICATED_REPLACEMENT_SELECTION_LINEAGE_V1,
        "source_lineage": deepcopy(source_lineage),
        "source_lineage_hash": replay_hash(source_lineage),
        "session_root": str(session_root),
        "authorization_reference": request["authorization_id"],
        "authorization_hash": request["authorization_hash"],
        "authorization_replay_reference": request[
            "authorization_replay_reference"
        ],
        "authorization_status": request["authorization_status"],
        "execution_ready_reference": context["context_identity"],
        "execution_ready_hash": context_hash,
        "approval_status": request["mutation_decision_outcome"],
        "approval_reference": request["mutation_decision_id"],
        "approval_hash": request["mutation_decision_hash"],
        "execution_packet_reference": request["request_id"],
        "execution_packet_hash": request["request_hash"],
        "chain_id": context_hash,
        "handoff_reference": request["request_id"],
        "handoff_hash": request["request_hash"],
        "selected_worker_id": selection["selected_resource_id"],
        "selected_worker_version": selection["selected_resource_version"],
        "selected_resource_category": selection["selected_resource_category"],
        "selected_role_type": selection["selected_role_type"],
        "selected_authority_profile": selection[
            "selected_authority_profile"
        ],
        "selected_domain_id": selection["domain_id"],
        "required_capability": selection["required_capability"],
        "selection_artifact_reference": selection["selection_id"],
        "selection_artifact_hash": selection["artifact_hash"],
        "selection_replay_reference": str(selection_reference),
        "selection_replay_hash": selection_reconstruction["replay_hash"],
        "selection_context_reference": selection["context_reference"],
        "selection_context_hash": selection["context_hash"],
        "selection_registry_hash": selection["registry_hash"],
        "worker_selection_certification_reference": str(certification_reference),
        "worker_selection_certification_hash": certification["artifact_hash"],
        "allowed_outputs": [request["target_path"]],
        "forbidden_operations": [
            "PROVIDER_INVOCATION",
            "SHELL_COMMAND_EXECUTION",
            "MUTATION_OUTSIDE_AUTHENTICATED_TARGET",
        ],
        "validation_requirements": [
            "AUTHENTICATED_REQUEST_REPLAY",
            "SINGLE_USE_CONSUMPTION_REPLAY",
            "CERTIFIED_SELECTION_REPLAY",
            "PREIMAGE_SHA256",
            "REPLACEMENT_CONTENT_HASH",
        ],
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
    }
    projection["artifact_hash"] = replay_hash(projection)
    return projection


def _reconstruct_consumption_prefix(
    request: dict[str, Any],
) -> dict[str, Any]:
    current = reconstruct_authenticated_replace_replay_v2(request)
    if (
        current.get("event_keys", [])[:2] != ["request", "consumption"]
        or current.get("replay_artifact_count", 0) < 2
    ):
        raise FailClosedRuntimeError(
            "Filesystem selection lineage resolver failed closed: consumption "
            "prefix missing"
        )
    request_wrapper = load_json(Path(request["destinations"]["request"]))
    consumption_wrapper = load_json(Path(request["destinations"]["consumption"]))
    for wrapper, key in (
        (request_wrapper, "request"),
        (consumption_wrapper, "consumption"),
    ):
        _verify_wrapper(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError(
                "Filesystem selection lineage resolver failed closed: "
                "consumption prefix invalid"
            )
        _verify_artifact(artifact, "authenticated replacement Replay artifact")
        if (
            wrapper.get("event_key") != key
            or artifact.get("request_hash") != request["request_hash"]
            or artifact.get("authorization_id") != request["authorization_id"]
            or artifact.get("authorization_hash") != request["authorization_hash"]
        ):
            raise FailClosedRuntimeError(
                "Filesystem selection lineage resolver failed closed: "
                "consumption prefix invalid"
            )
    if not all(
        (
            request_wrapper.get("previous_replay_hash") is None,
            request_wrapper["artifact"].get("event_type") == "REQUEST_VALIDATED",
            request_wrapper["artifact"].get("payload") == {},
            consumption_wrapper.get("previous_replay_hash")
            == request_wrapper.get("replay_hash"),
            consumption_wrapper["artifact"].get("event_type")
            == "AUTHORIZATION_CONSUMPTION_CLAIMED",
            consumption_wrapper["artifact"].get("payload")
            == {"consumption_identity": request["authorization_hash"]},
        )
    ):
        raise FailClosedRuntimeError(
            "Filesystem selection lineage resolver failed closed: consumption "
            "prefix invalid"
        )
    wrappers = [request_wrapper, consumption_wrapper]
    return {
        "request_id": request["request_id"],
        "request_hash": request["request_hash"],
        "request_replay_reference": str(
            Path(request["destinations"]["request"]).parent
        ),
        "authorization_id": request["authorization_id"],
        "event_keys": ["request", "consumption"],
        "latest_event": "AUTHORIZATION_CONSUMPTION_CLAIMED",
        "latest_artifact": deepcopy(consumption_wrapper["artifact"]),
        "replay_artifact_count": 2,
        "replay_hash": replay_hash(wrappers),
        "last_wrapper_hash": consumption_wrapper["replay_hash"],
    }


def _resolve_reference(value: Any, *, anchor: Path) -> Path:
    if not isinstance(value, (str, Path)) or not str(value).strip():
        raise FailClosedRuntimeError(
            "Filesystem selection lineage resolver failed closed: Replay "
            "reference missing"
        )
    path = Path(value)
    if path.is_absolute() or path.exists():
        return path
    for parent in (anchor, *anchor.parents):
        candidate = parent / path
        if candidate.exists():
            return candidate
    return path


def _verify_artifact(artifact: dict[str, Any], label: str) -> None:
    try:
        verify_replay_hash(artifact, hash_field="artifact_hash")
    except (TypeError, ValueError) as exc:
        raise FailClosedRuntimeError(
            f"Filesystem selection lineage resolver failed closed: {label} "
            "hash mismatch"
        ) from exc


def _verify_wrapper(wrapper: dict[str, Any]) -> None:
    try:
        verify_replay_hash(wrapper, hash_field="replay_hash")
    except (TypeError, ValueError) as exc:
        raise FailClosedRuntimeError(
            "Filesystem selection lineage resolver failed closed: Replay "
            "wrapper hash mismatch"
        ) from exc


__all__ = [
    "AUTHENTICATED_REPLACEMENT_SELECTION_LINEAGE_V1",
    "RUNTIME_VERSION",
    "resolve_authenticated_replacement_worker_selection_lineage",
]
