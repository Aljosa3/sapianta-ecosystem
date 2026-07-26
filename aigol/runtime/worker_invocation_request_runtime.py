"""Replay-visible Worker invocation request preparation runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from pathlib import Path
import re
from typing import Any, Callable

from aigol.runtime.domain_approval_entry_to_execution_ready_authorization_bridge_runtime import (
    DOMAIN_EXECUTION_READY_BRIDGED,
    reconstruct_domain_execution_ready_bridge_replay,
)
from aigol.runtime.execution_authorization_runtime import (
    EXECUTION_AUTHORIZATION_ARTIFACT_V1,
    EXECUTION_AUTHORIZED,
    reconstruct_execution_authorization_replay,
)
from aigol.runtime.governed_implementation_dry_run import (
    EXECUTION_CANDIDATE_ARTIFACT_V1,
    EXECUTION_PACKET_ARTIFACT_V1,
    EXECUTION_READY,
    EXECUTION_READY_STATUS_ARTIFACT_V1,
    EXECUTION_VALIDATION_ARTIFACT_V1,
    reconstruct_governed_implementation_dry_run_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.ocs_execution_readiness_runtime import reconstruct_ocs_execution_readiness_replay
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.unified_resource_selection_runtime import (
    RESOURCE_SELECTION_SUCCEEDED,
    reconstruct_unified_resource_selection_replay,
)


AIGOL_WORKER_INVOCATION_REQUEST_RUNTIME_VERSION = "AIGOL_WORKER_INVOCATION_REQUEST_RUNTIME_V1"
WORKER_INVOCATION_REQUEST_EVIDENCE_ARTIFACT_V1 = "WORKER_INVOCATION_REQUEST_EVIDENCE_ARTIFACT_V1"
WORKER_INVOCATION_REQUEST_CLASSIFICATION_ARTIFACT_V1 = (
    "WORKER_INVOCATION_REQUEST_CLASSIFICATION_ARTIFACT_V1"
)
WORKER_INVOCATION_REQUEST_ARTIFACT_V1 = "WORKER_INVOCATION_REQUEST_ARTIFACT_V1"
WORKER_INVOCATION_REQUEST_RESULT_ARTIFACT_V1 = "WORKER_INVOCATION_REQUEST_RESULT_ARTIFACT_V1"
WORKER_INVOCATION_REQUEST_CREATED = "WORKER_INVOCATION_REQUEST_CREATED"
FAILED_CLOSED = "FAILED_CLOSED"
WORKER_SELECTION_LINEAGE_PROJECTION_V1 = "WORKER_SELECTION_LINEAGE_PROJECTION_V1"
ELIGIBLE_WORKER_RESOURCE_CATEGORIES = frozenset(
    {"WORKER", "HYBRID_PROVIDER_WORKER"}
)
CANONICAL_WORKER_ROLE = "WORKER_ROLE"
NON_AUTHORITATIVE_WORKER_PROFILE = "WORKER_AUTHORIZED_TASK_ONLY"

WorkerSelectionLineageResolver = Callable[[], dict[str, Any]]

REPLAY_STEPS = (
    "invocation_request_evidence_recorded",
    "invocation_request_classification_recorded",
    "invocation_request_artifact_recorded",
    "invocation_request_result_recorded",
)


def detect_domain_worker_request_entry_intent(human_prompt: str) -> dict[str, Any]:
    """Detect narrow operator prompts for domain worker request creation."""

    prompt = _require_string(human_prompt, "human_prompt")
    normalized = " ".join(prompt.strip().rstrip(".?!").split())
    lowered = normalized.lower()
    patterns = (
        r"^create\s+worker\s+request\s+for\s+(?P<domain>[A-Za-z][A-Za-z0-9_-]*)$",
        r"^continue\s+(?P<domain>[A-Za-z][A-Za-z0-9_-]*)\s+to\s+worker\s+request$",
        r"^create\s+authorized\s+worker\s+request\s+for\s+(?P<domain>[A-Za-z][A-Za-z0-9_-]*)$",
    )
    for pattern in patterns:
        match = re.match(pattern, normalized, flags=re.IGNORECASE)
        if match:
            if lowered.startswith("continue"):
                action = "CONTINUE_TO_WORKER_REQUEST"
            elif "authorized" in lowered:
                action = "CREATE_AUTHORIZED_WORKER_REQUEST"
            else:
                action = "CREATE_WORKER_REQUEST"
            return {
                "worker_request_entry_intent_detected": True,
                "domain_name": match.group("domain"),
                "worker_request_action": action,
                "matched_prompt": normalized,
            }
    return {
        "worker_request_entry_intent_detected": False,
        "domain_name": None,
        "worker_request_action": None,
        "matched_prompt": normalized,
    }


def find_latest_domain_execution_authorization(
    *,
    session_root: str | Path,
    domain_name: str,
) -> dict[str, Any]:
    """Find the latest unconsumed execution authorization replay for a domain."""

    root = Path(session_root)
    domain = _require_string(domain_name, "domain_name")
    if not root.exists():
        raise FailClosedRuntimeError("worker invocation request failed closed: session root missing")
    candidates: list[dict[str, Any]] = []
    bridge_index = _domain_execution_ready_bridge_index(root, domain)
    for path in sorted(root.glob("TURN-*/execution_authorization")):
        try:
            reconstructed = reconstruct_execution_authorization_replay(path)
            request_wrapper = load_json(path / "000_authorization_request_recorded.json")
            _verify_wrapper_hash(request_wrapper)
            auth_request = request_wrapper.get("artifact")
            if not isinstance(auth_request, dict):
                continue
            _verify_artifact_hash(auth_request, "execution authorization request artifact")
            authorization_wrapper = load_json(path / "002_authorization_artifact_recorded.json")
            _verify_wrapper_hash(authorization_wrapper)
            authorization = authorization_wrapper.get("artifact")
            if not isinstance(authorization, dict):
                continue
            _verify_artifact_hash(authorization, "execution authorization artifact")
        except FailClosedRuntimeError:
            continue
        if reconstructed.get("authorization_status") != EXECUTION_AUTHORIZED:
            continue
        bridge = _matching_bridge_for_authorization(auth_request, bridge_index)
        if bridge is None:
            continue
        if _execution_authorization_already_requested(
            root,
            execution_authorization_replay_reference=str(path),
            authorization_reference=str(reconstructed.get("authorization_id") or ""),
            authorization_hash=str(authorization.get("artifact_hash") or ""),
        ):
            continue
        candidates.append(
            {
                "execution_authorization_replay_reference": str(path),
                "execution_authorization_artifact": deepcopy(authorization),
                "authorization_reference": reconstructed["authorization_id"],
                "authorization_hash": authorization["artifact_hash"],
                "domain_execution_ready_bridge_replay_reference": bridge[
                    "domain_execution_ready_bridge_replay_reference"
                ],
                "execution_ready_replay_reference": auth_request["execution_ready_replay_reference"],
                "execution_ready_replay_hash": auth_request["execution_ready_hash"],
                "domain_name": bridge["approved_domain"],
                "turn_id": path.parent.name,
            }
        )
    if not candidates:
        raise FailClosedRuntimeError("worker invocation request failed closed: matching execution authorization not found")
    return candidates[-1]


def create_worker_invocation_request(
    *,
    invocation_request_id: str,
    execution_authorization_replay_reference: str,
    requested_by: str,
    requested_at: str,
    replay_dir: str | Path,
    resource_selection_replay_reference: str | None = None,
) -> dict[str, Any]:
    """Create a bounded Worker invocation request without assigning or invoking a Worker."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        lineage = _load_authorized_lineage(
            Path(execution_authorization_replay_reference), requested_at,
            resource_selection_replay_reference,
        )
        return _create_request_from_lineage(
            invocation_request_id=invocation_request_id,
            execution_authorization_replay_reference=(
                execution_authorization_replay_reference
            ),
            lineage=lineage,
            requested_by=requested_by,
            requested_at=requested_at,
            replay_path=replay_path,
        )
    except Exception as exc:
        result = _failed_result(
            invocation_request_id=invocation_request_id,
            execution_authorization_replay_reference=execution_authorization_replay_reference,
            requested_at=requested_at,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], result)
        return _capture(None, None, None, result, replay_path)


def create_worker_invocation_request_from_selection_lineage(
    *,
    invocation_request_id: str,
    worker_selection_lineage_resolver: WorkerSelectionLineageResolver,
    requested_by: str,
    requested_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Create a request from one invocation-scoped authenticated projection."""

    replay_path = Path(replay_dir)
    projection: dict[str, Any] | None = None
    try:
        _ensure_replay_available(replay_path)
        if not callable(worker_selection_lineage_resolver):
            raise FailClosedRuntimeError(
                "worker invocation request failed closed: selection lineage "
                "resolver is invalid"
            )
        projection = validate_worker_selection_lineage_projection(
            worker_selection_lineage_resolver(),
            replay_path=replay_path,
        )
        lineage = _project_worker_selection_lineage(projection)
        return _create_request_from_lineage(
            invocation_request_id=invocation_request_id,
            execution_authorization_replay_reference=projection[
                "authorization_replay_reference"
            ],
            lineage=lineage,
            requested_by=requested_by,
            requested_at=requested_at,
            replay_path=replay_path,
        )
    except Exception as exc:
        result = _failed_result(
            invocation_request_id=invocation_request_id,
            execution_authorization_replay_reference=str(
                projection.get("authorization_replay_reference")
                if isinstance(projection, dict)
                else "UNAVAILABLE"
            ),
            requested_at=requested_at,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], result)
        return _capture(None, None, None, result, replay_path)


def _create_request_from_lineage(
    *, invocation_request_id: str,
    execution_authorization_replay_reference: str,
    lineage: dict[str, Any], requested_by: str,
    requested_at: str, replay_path: Path,
) -> dict[str, Any]:
    evidence = _evidence_artifact(
        invocation_request_id=invocation_request_id,
        execution_authorization_replay_reference=(
            execution_authorization_replay_reference
        ),
        lineage=lineage,
        requested_at=requested_at,
    )
    classification = _classification_artifact(
        invocation_request_id=invocation_request_id,
        evidence=evidence,
        lineage=lineage,
        requested_at=requested_at,
    )
    request = _request_artifact(
        invocation_request_id=invocation_request_id,
        evidence=evidence,
        classification=classification,
        lineage=lineage,
        requested_by=requested_by,
        requested_at=requested_at,
    )
    result = _result_artifact(
        invocation_request_id=invocation_request_id,
        evidence=evidence,
        classification=classification,
        request=request,
        requested_at=requested_at,
        status=WORKER_INVOCATION_REQUEST_CREATED,
        failure_reason=None,
    )
    for index, artifact in enumerate((evidence, classification, request, result)):
        _persist_step(replay_path, index, REPLAY_STEPS[index], artifact)
    return _capture(evidence, classification, request, result, replay_path)


def reconstruct_worker_invocation_request_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct Worker invocation request replay deterministically."""

    replay_path = Path(replay_dir)
    expected_files = {
        f"{index:03d}_{step}.json" for index, step in enumerate(REPLAY_STEPS)
    }
    if {path.name for path in replay_path.glob("*.json")} != expected_files:
        raise FailClosedRuntimeError("worker invocation request replay file set mismatch")
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("worker invocation request replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("worker invocation request replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "worker invocation request replay artifact")
        wrappers.append(wrapper)

    evidence = wrappers[0]["artifact"]
    classification = wrappers[1]["artifact"]
    request = wrappers[2]["artifact"]
    result = wrappers[3]["artifact"]
    if classification.get("invocation_request_evidence_hash") != evidence["artifact_hash"]:
        raise FailClosedRuntimeError("worker invocation request replay evidence lineage mismatch")
    if request.get("invocation_request_classification_hash") != classification["artifact_hash"]:
        raise FailClosedRuntimeError("worker invocation request replay classification lineage mismatch")
    if result.get("worker_invocation_request_hash") != request["artifact_hash"]:
        raise FailClosedRuntimeError("worker invocation request replay request lineage mismatch")
    if len({evidence["chain_id"], classification["chain_id"], request["chain_id"], result["chain_id"]}) != 1:
        raise FailClosedRuntimeError("worker invocation request replay chain mismatch")
    if evidence["execution_packet_hash"] != request["execution_packet_hash"]:
        raise FailClosedRuntimeError("worker invocation request replay packet lineage mismatch")
    _validate_request_artifact(request)
    compatibility = request.get("compatibility_lineage")
    if compatibility:
        reconstructed_compatibility = validate_worker_selection_lineage_projection(
            compatibility,
            replay_path=replay_path,
            request_artifact=request,
        )
        if compatibility != reconstructed_compatibility:
            raise FailClosedRuntimeError(
                "worker invocation request replay compatibility lineage mismatch"
            )
    else:
        authorization_replay_path = _resolve_replay_reference(
            evidence["execution_authorization_replay_reference"],
            anchor=replay_path,
        )
        lineage = _load_authorized_lineage(
            authorization_replay_path, request["requested_at"],
            (request.get("g31_lineage") or {}).get(
                "resource_selection_replay_reference"
            ),
        )
        if request.get("g31_lineage") != lineage.get("g31_lineage"):
            raise FailClosedRuntimeError(
                "worker invocation request replay selection lineage mismatch"
            )
    return {
        "worker_invocation_request_id": request["worker_invocation_request_id"],
        "request_status": result["request_status"],
        "chain_id": request["chain_id"],
        "authorization_reference": request["authorization_reference"],
        "execution_packet_reference": request["execution_packet_reference"],
        "worker_role": request["worker_role"],
        "target_worker_family": request["target_worker_family"],
        "allowed_outputs": deepcopy(request["allowed_outputs"]),
        "forbidden_operations": deepcopy(request["forbidden_operations"]),
        "validation_requirements": deepcopy(request["validation_requirements"]),
        "request_hash": request["request_hash"],
        **({"complete_g31_lineage_reconstructed": True} if request.get("g31_lineage") else {}),
        **(
            {"complete_worker_selection_lineage_reconstructed": True}
            if compatibility else {}
        ),
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
        **_boundary_flags(),
        "failure_reason": result["failure_reason"],
    }


def validate_worker_selection_lineage_projection(
    projection: Any,
    *,
    replay_path: str | Path | None = None,
    request_artifact: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Authenticate one immutable worker-neutral selection-lineage projection."""

    if not isinstance(projection, dict):
        raise FailClosedRuntimeError(
            "worker invocation request failed closed: selection lineage "
            "projection is required"
        )
    resolved = deepcopy(projection)
    _verify_artifact_hash(resolved, "Worker selection lineage projection")
    if resolved.get("artifact_type") != WORKER_SELECTION_LINEAGE_PROJECTION_V1:
        raise FailClosedRuntimeError(
            "worker invocation request failed closed: unsupported selection lineage"
        )
    for field in (
        "projection_id",
        "source_lineage_type",
        "session_root",
        "authorization_reference",
        "authorization_hash",
        "authorization_replay_reference",
        "authorization_status",
        "execution_ready_reference",
        "execution_ready_hash",
        "approval_status",
        "approval_reference",
        "approval_hash",
        "execution_packet_reference",
        "execution_packet_hash",
        "chain_id",
        "handoff_reference",
        "handoff_hash",
        "selected_worker_id",
        "selected_worker_version",
        "selected_resource_category",
        "selected_role_type",
        "selected_authority_profile",
        "selected_domain_id",
        "required_capability",
        "selection_artifact_reference",
        "selection_artifact_hash",
        "selection_replay_reference",
        "selection_replay_hash",
        "selection_context_reference",
        "selection_context_hash",
        "selection_registry_hash",
        "worker_selection_certification_reference",
        "worker_selection_certification_hash",
        "source_lineage_hash",
    ):
        _require_string(resolved.get(field), field)
    for field in (
        "allowed_outputs",
        "forbidden_operations",
        "validation_requirements",
    ):
        if not _string_list(resolved.get(field)):
            raise FailClosedRuntimeError(
                "worker invocation request failed closed: selection lineage "
                f"{field} is invalid"
            )
    source_lineage = resolved.get("source_lineage")
    if (
        not isinstance(source_lineage, dict)
        or resolved["source_lineage_hash"] != replay_hash(source_lineage)
    ):
        raise FailClosedRuntimeError(
            "worker invocation request failed closed: selection lineage "
            "source commitment mismatch"
        )
    authority = resolved.get("authority_flags")
    if not isinstance(authority, dict) or not authority or any(
        value is not False for value in authority.values()
    ):
        raise FailClosedRuntimeError(
            "worker invocation request failed closed: selection lineage "
            "authority violation"
        )
    if not all(
        (
            resolved["chain_id"] == resolved["selection_context_hash"],
            resolved["execution_ready_hash"]
            == resolved["selection_context_hash"],
            resolved["execution_packet_reference"]
            == resolved["handoff_reference"],
            resolved["execution_packet_hash"] == resolved["handoff_hash"],
            resolved["selected_resource_category"]
            in {"WORKER", "HYBRID_PROVIDER_WORKER"},
            resolved["selected_role_type"] == "WORKER_ROLE",
            resolved["selected_authority_profile"]
            == "WORKER_AUTHORIZED_TASK_ONLY",
        )
    ):
        raise FailClosedRuntimeError(
            "worker invocation request failed closed: selection lineage mismatch"
        )

    session_root = Path(resolved["session_root"]).resolve()
    authorization_path = _resolve_replay_reference(
        resolved["authorization_replay_reference"],
        anchor=Path(replay_path) if replay_path is not None else Path("."),
    ).resolve()
    selection_path = _resolve_replay_reference(
        resolved["selection_replay_reference"],
        anchor=Path(replay_path) if replay_path is not None else Path("."),
    ).resolve()
    if not authorization_path.is_relative_to(session_root):
        raise FailClosedRuntimeError(
            "worker invocation request failed closed: Authorization lineage "
            "is cross-session"
        )
    if not selection_path.is_relative_to(session_root):
        raise FailClosedRuntimeError(
            "worker invocation request failed closed: selection lineage "
            "is cross-session"
        )
    if replay_path is not None and not Path(replay_path).resolve().is_relative_to(
        session_root
    ):
        raise FailClosedRuntimeError(
            "worker invocation request failed closed: request Replay is "
            "cross-session"
        )

    selection_reconstruction = reconstruct_unified_resource_selection_replay(
        selection_path
    )
    selection_wrapper = load_json(
        selection_path / "000_resource_selection_recorded.json"
    )
    _verify_wrapper_hash(selection_wrapper)
    selection = selection_wrapper.get("artifact")
    if not isinstance(selection, dict):
        raise FailClosedRuntimeError(
            "worker invocation request failed closed: Worker selection is missing"
        )
    _verify_artifact_hash(selection, "Worker selection artifact")
    if not all(
        (
            selection_reconstruction.get("selection_status")
            == RESOURCE_SELECTION_SUCCEEDED,
            selection_reconstruction.get("replay_hash")
            == resolved["selection_replay_hash"],
            selection.get("selection_status") == RESOURCE_SELECTION_SUCCEEDED,
            selection.get("selection_id")
            == resolved["selection_artifact_reference"],
            selection.get("artifact_hash") == resolved["selection_artifact_hash"],
            selection.get("selected_resource_id")
            == resolved["selected_worker_id"],
            selection.get("selected_resource_version")
            == resolved["selected_worker_version"],
            selection.get("selected_resource_category")
            == resolved["selected_resource_category"],
            selection.get("selected_role_type") == resolved["selected_role_type"],
            selection.get("selected_authority_profile")
            == resolved["selected_authority_profile"],
            selection.get("domain_id") == resolved["selected_domain_id"],
            selection.get("required_capability")
            == resolved["required_capability"],
            selection.get("context_reference")
            == resolved["selection_context_reference"],
            selection.get("context_hash") == resolved["selection_context_hash"],
            selection.get("registry_hash") == resolved["selection_registry_hash"],
            selection.get("worker_authorization_required") is True,
            selection.get("provider_invoked") is False,
            selection.get("worker_invoked") is False,
            selection.get("dispatch_requested") is False,
        )
    ):
        raise FailClosedRuntimeError(
            "worker invocation request failed closed: certified Worker "
            "selection mismatch"
        )
    if request_artifact is not None:
        if not isinstance(request_artifact, dict) or not all(
            (
                request_artifact.get("authorization_reference")
                == resolved["authorization_reference"],
                request_artifact.get("authorization_hash")
                == resolved["authorization_hash"],
                request_artifact.get("execution_packet_reference")
                == resolved["execution_packet_reference"],
                request_artifact.get("execution_packet_hash")
                == resolved["execution_packet_hash"],
                request_artifact.get("chain_id") == resolved["chain_id"],
                request_artifact.get("target_worker_family")
                == resolved["selected_worker_id"],
                request_artifact.get("worker_role")
                == resolved["selected_role_type"],
                request_artifact.get("target_domain")
                == resolved["selected_domain_id"],
                request_artifact.get("allowed_outputs")
                == resolved["allowed_outputs"],
                request_artifact.get("forbidden_operations")
                == resolved["forbidden_operations"],
                request_artifact.get("validation_requirements")
                == resolved["validation_requirements"],
            )
        ):
            raise FailClosedRuntimeError(
                "worker invocation request failed closed: selection lineage "
                "request mismatch"
            )
    return resolved


def _project_worker_selection_lineage(
    compatibility: dict[str, Any],
) -> dict[str, Any]:
    authorization = {
        "chain_id": compatibility["chain_id"],
        "authorization_id": compatibility["authorization_reference"],
        "artifact_hash": compatibility["authorization_hash"],
        "authorization_status": compatibility["authorization_status"],
        "execution_ready_reference": compatibility["execution_ready_reference"],
        "execution_ready_hash": compatibility["execution_ready_hash"],
        "execution_candidate_reference": compatibility[
            "selection_artifact_reference"
        ],
        "execution_candidate_hash": compatibility["selection_artifact_hash"],
        "approval_status": compatibility["approval_status"],
        "approval_reference": compatibility["approval_reference"],
        "approval_hash": compatibility["approval_hash"],
    }
    packet = {
        "packet_id": compatibility["execution_packet_reference"],
        "artifact_hash": compatibility["execution_packet_hash"],
        "worker_role_requirements": [compatibility["selected_role_type"]],
        "allowed_outputs": deepcopy(compatibility["allowed_outputs"]),
        "forbidden_operations": deepcopy(compatibility["forbidden_operations"]),
        "required_validations": deepcopy(compatibility["validation_requirements"]),
    }
    candidate = {
        "target_domain": compatibility["selected_domain_id"],
        "handoff_reference": compatibility["handoff_reference"],
        "handoff_hash": compatibility["handoff_hash"],
        "target_worker": compatibility["selected_worker_id"],
    }
    return {
        "authorization": authorization,
        "packet": packet,
        "candidate": candidate,
        "checks": {
            "authorization_lineage": True,
            "worker_specific_lineage_authenticated": True,
            "certified_selection_lineage": True,
            "replay_continuity": True,
            "authority_continuity": True,
        },
        "g31_lineage": None,
        "compatibility_lineage": compatibility,
    }


def render_worker_invocation_request_summary(capture: dict[str, Any]) -> str:
    lines = [
        "",
        "Worker Invocation Request",
        "",
        f"Request Status: {capture.get('request_status')}",
        f"Invocation Request Reference: {capture.get('worker_invocation_request_reference')}",
        f"Authorization Reference: {capture.get('authorization_reference')}",
        f"Execution Packet Reference: {capture.get('execution_packet_reference')}",
        f"Replay Reference: {capture.get('worker_invocation_request_replay_reference')}",
        "",
        "No Worker has been assigned, dispatched, invoked, or executed.",
    ]
    if capture.get("failure_reason"):
        lines.append(f"failure_reason: {capture['failure_reason']}")
    return "\n".join(lines)


def _load_authorized_lineage(
    auth_replay_path: Path, requested_at: str,
    resource_selection_replay_reference: str | None = None,
) -> dict[str, Any]:
    reconstructed = reconstruct_execution_authorization_replay(auth_replay_path)
    if reconstructed.get("authorization_status") != EXECUTION_AUTHORIZED:
        raise FailClosedRuntimeError("worker invocation request failed closed: authorization invalid")
    authorization_wrappers = []
    auth_steps = (
        "authorization_request_recorded",
        "authorization_decision_recorded",
        "authorization_artifact_recorded",
        "authorization_result_recorded",
    )
    for index, step in enumerate(auth_steps):
        wrapper = load_json(auth_replay_path / f"{index:03d}_{step}.json")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("worker invocation request failed closed: authorization replay corruption")
        _verify_artifact_hash(artifact, "execution authorization lineage artifact")
        authorization_wrappers.append(wrapper)
    auth_request = authorization_wrappers[0]["artifact"]
    decision = authorization_wrappers[1]["artifact"]
    authorization = authorization_wrappers[2]["artifact"]
    auth_result = authorization_wrappers[3]["artifact"]
    if authorization.get("artifact_type") != EXECUTION_AUTHORIZATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("worker invocation request failed closed: authorization invalid")
    if authorization.get("authorization_status") != EXECUTION_AUTHORIZED:
        raise FailClosedRuntimeError("worker invocation request failed closed: authorization invalid")
    if auth_result.get("authorization_status") != EXECUTION_AUTHORIZED:
        raise FailClosedRuntimeError("worker invocation request failed closed: authorization invalid")
    if authorization.get("authorization_revoked") is not False:
        raise FailClosedRuntimeError("worker invocation request failed closed: authorization invalid")
    _validate_not_expired(authorization.get("authorization_expires_at"), requested_at)

    ready_lineage = _load_execution_ready_lineage(
        _resolve_replay_reference(auth_request["execution_ready_replay_reference"], anchor=auth_replay_path)
    )
    candidate = ready_lineage["candidate"]
    packet = ready_lineage["packet"]
    validation = ready_lineage["validation"]
    ready = ready_lineage["ready"]
    checks = {
        "authorization_lineage": auth_result["execution_authorization_hash"] == authorization["artifact_hash"],
        "packet_lineage": authorization["execution_packet_hash"] == packet["artifact_hash"],
        "candidate_lineage": authorization["execution_candidate_hash"] == candidate["artifact_hash"],
        "handoff_lineage": bool(candidate.get("handoff_reference")) and (
            validation.get("handoff_hash") == candidate.get("handoff_hash")
            or candidate.get("execution_scope", {}).get("grounded_worker_request_hash")
            == candidate.get("handoff_hash")
        ),
        "approval_lineage": authorization["approval_hash"] == candidate["approval_hash"],
        "chain_continuity": authorization["chain_id"] == candidate["chain_id"] == packet["chain_id"],
        "replay_continuity": ready["execution_status"] == EXECUTION_READY,
        "authority_continuity": _authority_continuity(authorization, packet),
    }
    if not all(checks.values()):
        raise FailClosedRuntimeError("worker invocation request failed closed: lineage continuity invalid")
    g31_lineage = None
    if ready_lineage.get("g31_ready"):
        if not resource_selection_replay_reference:
            raise FailClosedRuntimeError("worker invocation request failed closed: G31 Worker selection is required")
        g31_lineage = _load_g31_selection_binding(
            Path(resource_selection_replay_reference),
            auth_replay_path,
        )
        g31_lineage["authorization_scope"] = deepcopy(auth_request.get("requested_scope"))
    return {
        "auth_request": auth_request,
        "authorization_decision": decision,
        "authorization": authorization,
        "authorization_result": auth_result,
        "candidate": candidate,
        "packet": packet,
        "validation": validation,
        "ready": ready,
        "checks": checks,
        "g31_lineage": g31_lineage,
    }


def _resolve_replay_reference(reference: Any, *, anchor: Path) -> Path:
    replay_path = Path(_require_string(reference, "replay_reference"))
    if replay_path.is_absolute() or replay_path.exists():
        return replay_path
    for parent in (anchor, *anchor.parents):
        candidate = parent / replay_path
        if candidate.exists():
            return candidate
    return replay_path


def _load_execution_ready_lineage(replay_path: Path) -> dict[str, dict[str, Any]]:
    g31_ready = False
    try:
        reconstructed = reconstruct_governed_implementation_dry_run_replay(replay_path)
    except FailClosedRuntimeError:
        try:
            from aigol.runtime.confirmed_grounded_execution_authorization_binding import reconstruct_confirmed_grounded_execution_ready_replay

            reconstructed = reconstruct_confirmed_grounded_execution_ready_replay(replay_path)
            g31_ready = True
        except FailClosedRuntimeError:
            reconstructed = reconstruct_ocs_execution_readiness_replay(replay_path)
    if reconstructed.get("execution_status") != EXECUTION_READY:
        raise FailClosedRuntimeError("worker invocation request failed closed: execution is not ready")
    artifacts: list[dict[str, Any]] = []
    expected = (
        (0, "execution_candidate_recorded", EXECUTION_CANDIDATE_ARTIFACT_V1),
        (1, "execution_packet_recorded", EXECUTION_PACKET_ARTIFACT_V1),
        (2, "execution_validation_recorded", EXECUTION_VALIDATION_ARTIFACT_V1),
        (3, "execution_ready_status_recorded", EXECUTION_READY_STATUS_ARTIFACT_V1),
    )
    for index, step, artifact_type in expected:
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("worker invocation request failed closed: replay corruption")
        _verify_artifact_hash(artifact, "execution-ready lineage artifact")
        if artifact.get("artifact_type") != artifact_type:
            raise FailClosedRuntimeError("worker invocation request failed closed: replay corruption")
        artifacts.append(artifact)
    candidate, packet, validation, ready = artifacts
    checks = (
        packet.get("candidate_hash") == candidate.get("artifact_hash"),
        validation.get("candidate_hash") == candidate.get("artifact_hash"),
        validation.get("packet_hash") == packet.get("artifact_hash"),
        ready.get("candidate_hash") == candidate.get("artifact_hash"),
        ready.get("packet_hash") == packet.get("artifact_hash"),
        ready.get("validation_hash") == validation.get("artifact_hash"),
        candidate.get("chain_id") == packet.get("chain_id"),
    )
    if not all(checks):
        raise FailClosedRuntimeError("worker invocation request failed closed: packet corruption")
    return {"candidate": candidate, "packet": packet, "validation": validation,
            "ready": ready, "g31_ready": g31_ready}


def _load_g31_selection_binding(
    selection_path: Path,
    auth_path: Path,
) -> dict[str, Any]:
    from aigol.runtime.confirmed_grounded_execution_authorization_binding import reconstruct_authorized_grounded_worker_selection
    from aigol.runtime.unified_resource_selection_runtime import RESOURCE_SELECTION_SUCCEEDED

    resolved_selection = selection_path.resolve()
    resolved_authorization = auth_path.resolve()
    if not resolved_selection.is_relative_to(resolved_authorization.parents[1]):
        raise FailClosedRuntimeError("worker invocation request failed closed: selection is cross-session")
    reconstructed = reconstruct_authorized_grounded_worker_selection(
        selection_replay_dir=resolved_selection, execution_authorization_replay_dir=resolved_authorization)
    wrapper = load_json(resolved_selection / "000_resource_selection_recorded.json")
    _verify_wrapper_hash(wrapper)
    selection = wrapper.get("artifact")
    if not isinstance(selection, dict):
        raise FailClosedRuntimeError("worker invocation request failed closed: Worker selection is missing")
    _verify_artifact_hash(selection, "Worker selection artifact")
    validate_historical_worker_selection_identity(
        selection,
    )
    if not all(
        (
            reconstructed.get("selection_status") == RESOURCE_SELECTION_SUCCEEDED,
            selection.get("context_hash") == reconstructed.get("execution_authorization_hash"),
            selection.get("provider_invoked") is False,
            selection.get("worker_invoked") is False,
            selection.get("dispatch_requested") is False,
        )
    ):
        raise FailClosedRuntimeError("worker invocation request failed closed: Worker selection mismatch")
    return {
        "resource_selection_artifact": deepcopy(selection),
        "resource_selection_replay_reference": str(resolved_selection),
        "worker_selection_certification_hash": reconstructed["worker_selection_certification_hash"],
        "provider_authority": False,
    }


def _evidence_artifact(
    *,
    invocation_request_id: str,
    execution_authorization_replay_reference: str,
    lineage: dict[str, dict[str, Any]],
    requested_at: str,
) -> dict[str, Any]:
    authorization = lineage["authorization"]
    packet = lineage["packet"]
    candidate = lineage["candidate"]
    artifact = {
        "artifact_type": WORKER_INVOCATION_REQUEST_EVIDENCE_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_INVOCATION_REQUEST_RUNTIME_VERSION,
        "invocation_request_evidence_id": f"{_require_string(invocation_request_id, 'invocation_request_id')}:EVIDENCE",
        "chain_id": authorization["chain_id"],
        "execution_authorization_replay_reference": _require_string(
            execution_authorization_replay_reference, "execution_authorization_replay_reference"
        ),
        "authorization_reference": authorization["authorization_id"],
        "authorization_hash": authorization["artifact_hash"],
        "authorization_status": authorization["authorization_status"],
        "execution_ready_reference": authorization["execution_ready_reference"],
        "execution_ready_hash": authorization["execution_ready_hash"],
        "execution_candidate_reference": authorization["execution_candidate_reference"],
        "execution_candidate_hash": authorization["execution_candidate_hash"],
        "execution_packet_reference": packet["packet_id"],
        "execution_packet_hash": packet["artifact_hash"],
        "target_domain": candidate.get("target_domain"),
        "handoff_reference": candidate["handoff_reference"],
        "handoff_hash": candidate["handoff_hash"],
        "approval_status": authorization["approval_status"],
        "approval_reference": authorization["approval_reference"],
        "approval_hash": authorization["approval_hash"],
        "lineage_checks": deepcopy(lineage["checks"]),
        "recorded_at": _require_string(requested_at, "requested_at"),
        "replay_visible": True,
        **_boundary_flags(),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _classification_artifact(
    *,
    invocation_request_id: str,
    evidence: dict[str, Any],
    lineage: dict[str, dict[str, Any]],
    requested_at: str,
) -> dict[str, Any]:
    packet = lineage["packet"]
    candidate = lineage["candidate"]
    worker_role = _worker_role(packet)
    artifact = {
        "artifact_type": WORKER_INVOCATION_REQUEST_CLASSIFICATION_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_INVOCATION_REQUEST_RUNTIME_VERSION,
        "invocation_request_classification_id": f"{_require_string(invocation_request_id, 'invocation_request_id')}:CLASSIFICATION",
        "invocation_request_evidence_reference": evidence["invocation_request_evidence_id"],
        "invocation_request_evidence_hash": evidence["artifact_hash"],
        "chain_id": evidence["chain_id"],
        "worker_role": worker_role,
        "target_worker_family": _target_worker_family_for_lineage(
            lineage,
            candidate,
            worker_role,
        ),
        "allowed_outputs": deepcopy(packet["allowed_outputs"]),
        "forbidden_operations": deepcopy(packet["forbidden_operations"]),
        "validation_requirements": deepcopy(packet["required_validations"]),
        "classification_status": "INVOCATION_REQUEST_SCOPE_CLASSIFIED",
        "classification_checks": {
            "one_authorization": True,
            "one_execution_packet": True,
            "one_worker_role": True,
            "authorized_outputs_preserved": True,
            "forbidden_operations_preserved": True,
            "validation_requirements_preserved": True,
            "non_authoritative_request": True,
        },
        "classified_at": _require_string(requested_at, "requested_at"),
        "replay_visible": True,
        **_boundary_flags(),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _request_artifact(
    *,
    invocation_request_id: str,
    evidence: dict[str, Any],
    classification: dict[str, Any],
    lineage: dict[str, dict[str, Any]],
    requested_by: str,
    requested_at: str,
) -> dict[str, Any]:
    packet = lineage["packet"]
    authorization = lineage["authorization"]
    artifact = {
        "artifact_type": WORKER_INVOCATION_REQUEST_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_INVOCATION_REQUEST_RUNTIME_VERSION,
        "worker_invocation_request_id": _require_string(invocation_request_id, "invocation_request_id"),
        "request_status": WORKER_INVOCATION_REQUEST_CREATED,
        "invocation_request_evidence_reference": evidence["invocation_request_evidence_id"],
        "invocation_request_evidence_hash": evidence["artifact_hash"],
        "invocation_request_classification_reference": classification["invocation_request_classification_id"],
        "invocation_request_classification_hash": classification["artifact_hash"],
        "chain_id": evidence["chain_id"],
        "authorization_reference": authorization["authorization_id"],
        "authorization_hash": authorization["artifact_hash"],
        "execution_packet_reference": packet["packet_id"],
        "execution_packet_hash": packet["artifact_hash"],
        "target_domain": evidence.get("target_domain"),
        "worker_role": classification["worker_role"],
        "target_worker_family": classification["target_worker_family"],
        "allowed_outputs": deepcopy(classification["allowed_outputs"]),
        "forbidden_operations": deepcopy(classification["forbidden_operations"]),
        "validation_requirements": deepcopy(classification["validation_requirements"]),
        "replay_references": {
            "execution_authorization_replay_reference": evidence["execution_authorization_replay_reference"],
            "execution_ready_reference": evidence["execution_ready_reference"],
            "execution_candidate_reference": evidence["execution_candidate_reference"],
            "execution_packet_reference": packet["packet_id"],
            "handoff_reference": evidence["handoff_reference"],
            "approval_reference": evidence["approval_reference"],
        },
        "requested_by": _require_string(requested_by, "requested_by"),
        "requested_at": _require_string(requested_at, "requested_at"),
        "request_authoritative": False,
        "replay_visible": True,
        **_boundary_flags(),
    }
    if lineage.get("g31_lineage"):
        artifact["g31_lineage"] = deepcopy(lineage["g31_lineage"])
    if lineage.get("compatibility_lineage"):
        artifact["compatibility_lineage"] = deepcopy(
            lineage["compatibility_lineage"]
        )
    artifact["request_hash"] = _request_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_request_artifact(artifact)
    return artifact


def _result_artifact(
    *,
    invocation_request_id: str,
    evidence: dict[str, Any],
    classification: dict[str, Any],
    request: dict[str, Any],
    requested_at: str,
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_INVOCATION_REQUEST_RESULT_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_INVOCATION_REQUEST_RUNTIME_VERSION,
        "invocation_request_result_id": f"{_require_string(invocation_request_id, 'invocation_request_id')}:RESULT",
        "request_status": status,
        "invocation_request_evidence_reference": evidence["invocation_request_evidence_id"],
        "invocation_request_evidence_hash": evidence["artifact_hash"],
        "invocation_request_classification_reference": classification["invocation_request_classification_id"],
        "invocation_request_classification_hash": classification["artifact_hash"],
        "worker_invocation_request_reference": request["worker_invocation_request_id"],
        "worker_invocation_request_hash": request["artifact_hash"],
        "request_hash": request["request_hash"],
        "chain_id": request["chain_id"],
        "authorization_reference": request["authorization_reference"],
        "execution_packet_reference": request["execution_packet_reference"],
        "completed_at": _require_string(requested_at, "requested_at"),
        "replay_visible": True,
        **_boundary_flags(),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_result(
    *,
    invocation_request_id: str,
    execution_authorization_replay_reference: str,
    requested_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_INVOCATION_REQUEST_RESULT_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_INVOCATION_REQUEST_RUNTIME_VERSION,
        "invocation_request_result_id": f"{invocation_request_id}:RESULT",
        "request_status": FAILED_CLOSED,
        "invocation_request_evidence_reference": None,
        "invocation_request_evidence_hash": None,
        "invocation_request_classification_reference": None,
        "invocation_request_classification_hash": None,
        "worker_invocation_request_reference": None,
        "worker_invocation_request_hash": None,
        "request_hash": None,
        "chain_id": None,
        "authorization_reference": None,
        "execution_packet_reference": None,
        "execution_authorization_replay_reference": execution_authorization_replay_reference,
        "completed_at": requested_at,
        "replay_visible": True,
        **_boundary_flags(),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    evidence: dict[str, Any] | None,
    classification: dict[str, Any] | None,
    request: dict[str, Any] | None,
    result: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = deepcopy(result)
    capture.update(
        {
            "invocation_request_evidence_artifact": deepcopy(evidence),
            "invocation_request_classification_artifact": deepcopy(classification),
            "worker_invocation_request_artifact": deepcopy(request),
            "invocation_request_result_artifact": deepcopy(result),
            "worker_invocation_request_reference": request.get("worker_invocation_request_id") if request else None,
            "approved_domain": request.get("target_domain") if request else None,
            "authorization_reference": request.get("authorization_reference") if request else None,
            "execution_packet_reference": request.get("execution_packet_reference") if request else None,
            "worker_role": request.get("worker_role") if request else None,
            "target_worker_family": request.get("target_worker_family") if request else None,
            "worker_invocation_request_replay_reference": str(replay_path),
            "fail_closed": result["request_status"] == FAILED_CLOSED,
        }
    )
    capture["worker_invocation_request_capture_hash"] = replay_hash(capture)
    return capture


def _validate_request_artifact(request: dict[str, Any]) -> None:
    if request.get("artifact_type") != WORKER_INVOCATION_REQUEST_ARTIFACT_V1:
        raise FailClosedRuntimeError("worker invocation request failed closed: invalid request artifact")
    if request.get("request_status") != WORKER_INVOCATION_REQUEST_CREATED:
        raise FailClosedRuntimeError("worker invocation request failed closed: request was not created")
    if request.get("request_hash") != _request_hash(request):
        raise FailClosedRuntimeError("worker invocation request failed closed: request hash mismatch")
    if request.get("request_authoritative") is not False:
        raise FailClosedRuntimeError("worker invocation request failed closed: authority violation")
    if not _string_list(request.get("allowed_outputs")):
        raise FailClosedRuntimeError("worker invocation request failed closed: allowed outputs missing")
    if not _string_list(request.get("forbidden_operations")):
        raise FailClosedRuntimeError("worker invocation request failed closed: forbidden operations missing")
    if not _string_list(request.get("validation_requirements")):
        raise FailClosedRuntimeError("worker invocation request failed closed: validation requirements missing")
    for field, expected in _boundary_flags().items():
        if request.get(field) is not expected:
            raise FailClosedRuntimeError("worker invocation request failed closed: authority violation")
    g31 = request.get("g31_lineage")
    compatibility = request.get("compatibility_lineage")
    if g31 is not None and compatibility is not None:
        raise FailClosedRuntimeError(
            "worker invocation request failed closed: lineage is ambiguous"
        )
    if g31 is not None:
        selection = g31.get("resource_selection_artifact") if isinstance(g31, dict) else None
        if not isinstance(selection, dict):
            raise FailClosedRuntimeError("worker invocation request failed closed: selection authority invalid")
        validate_historical_worker_selection_identity(
            selection,
            target_worker_family=request.get("target_worker_family"),
        )
        if not all((
            selection.get("provider_invoked") is False, g31.get("provider_authority") is False,
            isinstance(g31.get("authorization_scope"), dict),
            isinstance(g31.get("resource_selection_replay_reference"), str),
            isinstance(g31.get("worker_selection_certification_hash"), str),
        )):
            raise FailClosedRuntimeError("worker invocation request failed closed: selection authority invalid")
    if compatibility is not None:
        validate_worker_selection_lineage_projection(
            compatibility,
            request_artifact=request,
        )


def validate_historical_worker_selection_identity(
    selection: dict[str, Any],
    *,
    target_worker_family: Any | None = None,
) -> str:
    """Validate legacy G31 selection identity by immutable relationships."""

    selected_worker_identity = _require_string(
        selection.get("selected_resource_id"),
        "selected_resource_id",
    )
    request_bound_worker_identity = (
        _require_string(target_worker_family, "target_worker_family")
        if target_worker_family is not None
        else selected_worker_identity
    )
    if not all(
        (
            selection.get("selection_status") == RESOURCE_SELECTION_SUCCEEDED,
            selected_worker_identity == request_bound_worker_identity,
            selection.get("selected_resource_category")
            in ELIGIBLE_WORKER_RESOURCE_CATEGORIES,
            selection.get("selected_role_type") == CANONICAL_WORKER_ROLE,
            selection.get("selected_authority_profile")
            == NON_AUTHORITATIVE_WORKER_PROFILE,
        )
    ):
        raise FailClosedRuntimeError(
            "worker invocation request failed closed: Worker selection "
            "identity continuity invalid"
        )
    return selected_worker_identity


def _domain_execution_ready_bridge_index(root: Path, domain_name: str) -> list[dict[str, Any]]:
    bridges: list[dict[str, Any]] = []
    for path in sorted(root.glob("TURN-*/domain_execution_ready_bridge")):
        try:
            reconstructed = reconstruct_domain_execution_ready_bridge_replay(path)
        except FailClosedRuntimeError:
            continue
        if reconstructed.get("bridge_status") != DOMAIN_EXECUTION_READY_BRIDGED:
            continue
        if str(reconstructed.get("approved_domain") or "").lower() != domain_name.lower():
            continue
        bridges.append(
            {
                "domain_execution_ready_bridge_replay_reference": str(path),
                "approved_domain": reconstructed["approved_domain"],
                "execution_ready_replay_reference": reconstructed["execution_ready_replay_reference"],
                "execution_ready_replay_hash": reconstructed["execution_ready_replay_hash"],
            }
        )
    return bridges


def _matching_bridge_for_authorization(
    auth_request: dict[str, Any],
    bridge_index: list[dict[str, Any]],
) -> dict[str, Any] | None:
    ready_reference = str(auth_request.get("execution_ready_replay_reference") or "")
    ready_hash = str(auth_request.get("execution_ready_hash") or "")
    for bridge in bridge_index:
        if bridge["execution_ready_replay_reference"] == ready_reference:
            return bridge
        if bridge["execution_ready_replay_hash"] == ready_hash:
            return bridge
    return None


def _execution_authorization_already_requested(
    session_root: Path,
    *,
    execution_authorization_replay_reference: str,
    authorization_reference: str,
    authorization_hash: str,
) -> bool:
    for path in sorted(session_root.glob("TURN-*/worker_invocation_request")):
        try:
            reconstructed = reconstruct_worker_invocation_request_replay(path)
            wrapper = load_json(path / "002_invocation_request_artifact_recorded.json")
            _verify_wrapper_hash(wrapper)
            request = wrapper.get("artifact")
            if not isinstance(request, dict):
                continue
            _verify_artifact_hash(request, "worker invocation request artifact")
        except FailClosedRuntimeError:
            continue
        if reconstructed.get("request_status") != WORKER_INVOCATION_REQUEST_CREATED:
            continue
        replay_references = request.get("replay_references") or {}
        if replay_references.get("execution_authorization_replay_reference") == execution_authorization_replay_reference:
            return True
        if request.get("authorization_reference") == authorization_reference:
            return True
        if request.get("authorization_hash") == authorization_hash:
            return True
    return False


def _request_hash(request: dict[str, Any]) -> str:
    return replay_hash(
        {
            "worker_invocation_request_id": request.get("worker_invocation_request_id"),
            "chain_id": request.get("chain_id"),
            "authorization_reference": request.get("authorization_reference"),
            "authorization_hash": request.get("authorization_hash"),
            "execution_packet_reference": request.get("execution_packet_reference"),
            "execution_packet_hash": request.get("execution_packet_hash"),
            "worker_role": request.get("worker_role"),
            "target_worker_family": request.get("target_worker_family"),
            "allowed_outputs": request.get("allowed_outputs", []),
            "forbidden_operations": request.get("forbidden_operations", []),
            "validation_requirements": request.get("validation_requirements", []),
            "replay_references": request.get("replay_references", {}),
            **({"g31_lineage": request["g31_lineage"]} if request.get("g31_lineage") else {}),
            **(
                {"compatibility_lineage": request["compatibility_lineage"]}
                if request.get("compatibility_lineage") else {}
            ),
        }
    )


def _authority_continuity(authorization: dict[str, Any], packet: dict[str, Any]) -> bool:
    return (
        authorization.get("worker_assigned") is False
        and authorization.get("worker_dispatched") is False
        and authorization.get("worker_invoked") is False
        and authorization.get("execution_started") is False
        and authorization.get("result_created") is False
        and authorization.get("approval_created") is False
        and packet.get("execution_contract", {}).get("execution_state") == "NOT_STARTED"
    )


def _worker_role(packet: dict[str, Any]) -> str:
    roles = packet.get("worker_role_requirements")
    if not _string_list(roles):
        raise FailClosedRuntimeError("worker invocation request failed closed: worker role missing")
    if len(roles) != 1:
        raise FailClosedRuntimeError("worker invocation request failed closed: worker role ambiguous")
    return roles[0]


def _target_worker_family(candidate: dict[str, Any], worker_role: str) -> str:
    value = candidate.get("target_worker") or worker_role
    return _require_string(value, "target_worker_family")


def _target_worker_family_for_lineage(
    lineage: dict[str, Any],
    candidate: dict[str, Any],
    worker_role: str,
) -> str:
    g31 = lineage.get("g31_lineage")
    if isinstance(g31, dict):
        selection = g31.get("resource_selection_artifact")
        if not isinstance(selection, dict):
            raise FailClosedRuntimeError(
                "worker invocation request failed closed: Worker selection "
                "is missing"
            )
        return validate_historical_worker_selection_identity(selection)
    return _target_worker_family(candidate, worker_role)


def _validate_not_expired(expires_at: Any, requested_at: str) -> None:
    expiry = _require_string(expires_at, "authorization_expires_at")
    if expiry == "NEVER":
        return
    try:
        expires = datetime.fromisoformat(expiry.replace("Z", "+00:00"))
        requested = datetime.fromisoformat(_require_string(requested_at, "requested_at").replace("Z", "+00:00"))
    except ValueError as exc:
        raise FailClosedRuntimeError("worker invocation request failed closed: authorization expiry invalid") from exc
    if expires < requested:
        raise FailClosedRuntimeError("worker invocation request failed closed: authorization expired")


def _boundary_flags() -> dict[str, bool]:
    return {
        "approval_created": False,
        "worker_assigned": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "execution_started": False,
        "result_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("worker invocation request replay ordering mismatch")
    _verify_artifact_hash(artifact, "worker invocation request artifact")
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


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {step}")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError(f"{label} hash is required")
    candidate = deepcopy(artifact)
    actual = candidate.pop("artifact_hash")
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("worker invocation request replay hash is required")
    candidate = deepcopy(wrapper)
    actual = candidate.pop("replay_hash")
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("worker invocation request replay hash mismatch")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"worker invocation request failed closed: {field} is required")
    return value


def _string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item.strip() for item in value)


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return f"worker invocation request failed closed: {exc}"
