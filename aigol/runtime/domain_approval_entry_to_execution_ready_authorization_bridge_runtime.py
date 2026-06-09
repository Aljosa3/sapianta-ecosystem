"""Bridge domain approval-entry artifacts into canonical execution-ready replay."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
from typing import Any

from aigol.runtime.conversation_to_implementation_handoff_runtime import (
    IMPLEMENTATION_HANDOFF_ARTIFACT_V1,
    IMPLEMENTATION_HANDOFF_CREATED,
)
from aigol.runtime.domain_handoff_review_approval_binding_runtime import (
    AUTHORIZATION_ENTRY_CREATED,
    DOMAIN_APPROVAL_BINDING_ARTIFACT_V1,
    DOMAIN_APPROVAL_BOUND,
    DOMAIN_AUTHORIZATION_ENTRY_ARTIFACT_V1,
    DOMAIN_EXECUTION_READY_CONTINUATION_ARTIFACT_V1,
    EXECUTION_READY_CONTINUATION_CREATED,
    reconstruct_domain_handoff_review_approval_binding_replay,
)
from aigol.runtime.governed_implementation_dry_run import (
    EXECUTION_CANDIDATE_ARTIFACT_V1,
    EXECUTION_PACKET_ARTIFACT_V1,
    EXECUTION_READY,
    EXECUTION_READY_STATUS_ARTIFACT_V1,
    EXECUTION_VALIDATION_ARTIFACT_V1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_DOMAIN_APPROVAL_ENTRY_TO_EXECUTION_READY_AUTHORIZATION_BRIDGE_RUNTIME_VERSION = (
    "AIGOL_DOMAIN_APPROVAL_ENTRY_TO_EXECUTION_READY_AUTHORIZATION_BRIDGE_RUNTIME_V1"
)
DOMAIN_EXECUTION_READY_BRIDGE_ARTIFACT_V1 = "DOMAIN_EXECUTION_READY_BRIDGE_ARTIFACT_V1"
DOMAIN_EXECUTION_READY_BRIDGE_RETURNED_ARTIFACT_V1 = "DOMAIN_EXECUTION_READY_BRIDGE_RETURNED_ARTIFACT_V1"
DOMAIN_EXECUTION_READY_BRIDGED = "DOMAIN_EXECUTION_READY_BRIDGED"
FAILED_CLOSED = "FAILED_CLOSED"

HANDOFF_REPLAY_STEPS = (
    "implementation_handoff_created",
    "implementation_handoff_returned",
)
EXECUTION_READY_REPLAY_STEPS = (
    "execution_candidate_recorded",
    "execution_packet_recorded",
    "execution_validation_recorded",
    "execution_ready_status_recorded",
)
BRIDGE_REPLAY_STEPS = (
    "domain_execution_ready_bridge_recorded",
    "domain_execution_ready_bridge_returned",
)

FORBIDDEN_OPERATIONS = (
    "AUTHORIZE_EXECUTION",
    "CREATE_DOMAIN_WITHOUT_AUTHORIZATION",
    "MUTATE_LIVE_DOMAIN_REGISTRY",
    "INVOKE_WORKER",
    "DISPATCH_WORKER",
    "REPAIR",
    "RETRY",
)
REQUIRED_VALIDATIONS = (
    "DOMAIN_APPROVAL_LINEAGE",
    "HANDOFF_REVIEW_LINEAGE",
    "AUTHORIZATION_ENTRY_LINEAGE",
    "EXECUTION_READY_CONTINUATION_LINEAGE",
    "WORKER_BINDING_LINEAGE",
    "AUTHORITY_BOUNDARIES",
    "HASH_INTEGRITY",
)
BOUNDARY_FLAGS = {
    "authorization_created": False,
    "worker_request_created": False,
    "worker_assigned": False,
    "worker_dispatched": False,
    "worker_invoked": False,
    "execution_started": False,
    "domain_created": False,
    "repair_started": False,
    "retry_started": False,
    "governance_mutated": False,
    "replay_mutated": False,
}


def detect_domain_execution_ready_entry_intent(human_prompt: str) -> dict[str, Any]:
    """Detect narrow operator prompts for domain execution-ready bridge entry."""

    prompt = _require_string(human_prompt, "human_prompt")
    normalized = " ".join(prompt.strip().rstrip(".?!").split())
    lowered = normalized.lower()
    patterns = (
        r"^continue\s+(?P<domain>[A-Za-z][A-Za-z0-9_-]*)\s+to\s+execution\s+authorization$",
        r"^create\s+execution[-\s]ready\s+authorization\s+packet\s+for\s+(?P<domain>[A-Za-z][A-Za-z0-9_-]*)$",
        r"^continue\s+(?P<domain>[A-Za-z][A-Za-z0-9_-]*)\s+authorization\s+workflow$",
    )
    for pattern in patterns:
        match = re.match(pattern, normalized, flags=re.IGNORECASE)
        if match:
            if lowered.startswith("create"):
                action = "CREATE_EXECUTION_READY_AUTHORIZATION_PACKET"
            elif "authorization workflow" in lowered:
                action = "CONTINUE_AUTHORIZATION_WORKFLOW"
            else:
                action = "CONTINUE_TO_EXECUTION_AUTHORIZATION"
            return {
                "execution_ready_entry_intent_detected": True,
                "domain_name": match.group("domain"),
                "execution_ready_action": action,
                "matched_prompt": normalized,
            }
    return {
        "execution_ready_entry_intent_detected": False,
        "domain_name": None,
        "execution_ready_action": None,
        "matched_prompt": normalized,
    }


def find_latest_domain_approval_binding(
    *,
    session_root: str | Path,
    domain_name: str,
) -> dict[str, Any]:
    """Find the latest unbridged domain approval binding for a domain in a session."""

    root = Path(session_root)
    domain = _require_string(domain_name, "domain_name")
    if not root.exists():
        raise FailClosedRuntimeError("domain execution-ready bridge failed closed: session root missing")
    candidates: list[dict[str, Any]] = []
    for path in sorted(root.glob("TURN-*/domain_approval_binding")):
        try:
            reconstructed = reconstruct_domain_handoff_review_approval_binding_replay(path)
            wrapper = load_json(path / "000_domain_approval_binding_recorded.json")
            _verify_wrapper_hash(wrapper, "domain approval binding replay")
            artifact = wrapper.get("artifact")
            if not isinstance(artifact, dict):
                continue
            _verify_artifact_hash(artifact, "domain approval binding artifact")
        except FailClosedRuntimeError:
            continue
        if reconstructed.get("approval_status") != DOMAIN_APPROVAL_BOUND:
            continue
        if reconstructed.get("authorization_entry_status") != AUTHORIZATION_ENTRY_CREATED:
            continue
        if reconstructed.get("execution_ready_continuation_status") != EXECUTION_READY_CONTINUATION_CREATED:
            continue
        if str(reconstructed.get("approved_domain") or "").lower() != domain.lower():
            continue
        if _approval_binding_already_bridged(root, artifact["artifact_hash"]):
            continue
        candidates.append(
            {
                "domain_approval_binding_replay_reference": str(path),
                "domain_approval_binding_artifact": deepcopy(artifact),
                "turn_id": path.parent.name,
                "created_at": artifact.get("approved_at"),
            }
        )
    if not candidates:
        raise FailClosedRuntimeError("domain execution-ready bridge failed closed: matching approval binding not found")
    return candidates[-1]


def bridge_domain_approval_entry_to_execution_ready(
    *,
    bridge_id: str,
    domain_approval_binding_replay_reference: str,
    approved_domain: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Convert a domain approval-entry replay into an authorization-compatible execution-ready replay."""

    replay_path = Path(replay_dir)
    handoff_replay_path = replay_path / "compatibility_implementation_handoff"
    execution_ready_replay_path = replay_path / "execution_ready"
    bridge_replay_path = replay_path / "bridge"
    try:
        _ensure_replay_available(handoff_replay_path, HANDOFF_REPLAY_STEPS)
        _ensure_replay_available(execution_ready_replay_path, EXECUTION_READY_REPLAY_STEPS)
        _ensure_replay_available(bridge_replay_path, BRIDGE_REPLAY_STEPS)
        lineage = _load_domain_approval_entry_lineage(
            Path(_require_string(domain_approval_binding_replay_reference, "domain_approval_binding_replay_reference")),
            approved_domain=approved_domain,
        )
        handoff = _compatibility_handoff_artifact(
            bridge_id=bridge_id,
            lineage=lineage,
            created_at=created_at,
            handoff_replay_path=handoff_replay_path,
        )
        handoff_returned = _compatibility_handoff_returned_artifact(handoff)
        _persist_step(handoff_replay_path, 0, HANDOFF_REPLAY_STEPS[0], handoff, HANDOFF_REPLAY_STEPS)
        _persist_step(handoff_replay_path, 1, HANDOFF_REPLAY_STEPS[1], handoff_returned, HANDOFF_REPLAY_STEPS)

        candidate = _candidate_artifact(
            bridge_id=bridge_id,
            lineage=lineage,
            handoff=handoff,
            handoff_replay_path=handoff_replay_path,
            created_at=created_at,
        )
        packet = _packet_artifact(bridge_id=bridge_id, candidate=candidate, lineage=lineage, created_at=created_at)
        validation = _validation_artifact(
            bridge_id=bridge_id,
            lineage=lineage,
            handoff=handoff,
            candidate=candidate,
            packet=packet,
            created_at=created_at,
        )
        ready = _ready_artifact(
            bridge_id=bridge_id,
            candidate=candidate,
            packet=packet,
            validation=validation,
            created_at=created_at,
            status=EXECUTION_READY,
            failure_reason=None,
        )
        _persist_step(execution_ready_replay_path, 0, EXECUTION_READY_REPLAY_STEPS[0], candidate, EXECUTION_READY_REPLAY_STEPS)
        _persist_step(execution_ready_replay_path, 1, EXECUTION_READY_REPLAY_STEPS[1], packet, EXECUTION_READY_REPLAY_STEPS)
        _persist_step(execution_ready_replay_path, 2, EXECUTION_READY_REPLAY_STEPS[2], validation, EXECUTION_READY_REPLAY_STEPS)
        _persist_step(execution_ready_replay_path, 3, EXECUTION_READY_REPLAY_STEPS[3], ready, EXECUTION_READY_REPLAY_STEPS)

        bridge = _bridge_artifact(
            bridge_id=bridge_id,
            lineage=lineage,
            handoff=handoff,
            ready=ready,
            execution_ready_replay_path=execution_ready_replay_path,
            created_at=created_at,
            status=DOMAIN_EXECUTION_READY_BRIDGED,
            failure_reason=None,
        )
        returned = _bridge_returned_artifact(bridge, created_at=created_at)
        _persist_step(bridge_replay_path, 0, BRIDGE_REPLAY_STEPS[0], bridge, BRIDGE_REPLAY_STEPS)
        _persist_step(bridge_replay_path, 1, BRIDGE_REPLAY_STEPS[1], returned, BRIDGE_REPLAY_STEPS)
        return _capture(
            bridge=bridge,
            returned=returned,
            handoff=handoff,
            candidate=candidate,
            packet=packet,
            validation=validation,
            ready=ready,
            replay_path=replay_path,
            handoff_replay_path=handoff_replay_path,
            execution_ready_replay_path=execution_ready_replay_path,
            bridge_replay_path=bridge_replay_path,
        )
    except Exception as exc:
        ready = _failed_ready_artifact(
            bridge_id=bridge_id,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        bridge = _failed_bridge_artifact(
            bridge_id=bridge_id,
            domain_approval_binding_replay_reference=domain_approval_binding_replay_reference,
            approved_domain=approved_domain,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _bridge_returned_artifact(bridge, created_at=created_at)
        _persist_failure_if_possible(execution_ready_replay_path, 3, EXECUTION_READY_REPLAY_STEPS[3], ready, EXECUTION_READY_REPLAY_STEPS)
        _persist_failure_if_possible(bridge_replay_path, 0, BRIDGE_REPLAY_STEPS[0], bridge, BRIDGE_REPLAY_STEPS)
        _persist_failure_if_possible(bridge_replay_path, 1, BRIDGE_REPLAY_STEPS[1], returned, BRIDGE_REPLAY_STEPS)
        return _capture(
            bridge=bridge,
            returned=returned,
            handoff=None,
            candidate=None,
            packet=None,
            validation=None,
            ready=ready,
            replay_path=replay_path,
            handoff_replay_path=handoff_replay_path,
            execution_ready_replay_path=execution_ready_replay_path,
            bridge_replay_path=bridge_replay_path,
        )


def reconstruct_domain_execution_ready_bridge_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct bridge replay and its generated execution-ready replay."""

    replay_path = Path(replay_dir)
    bridge_replay_path = replay_path / "bridge"
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(BRIDGE_REPLAY_STEPS):
        wrapper = load_json(bridge_replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("domain execution-ready bridge replay ordering mismatch")
        _verify_wrapper_hash(wrapper, "domain execution-ready bridge replay")
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("domain execution-ready bridge replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "domain execution-ready bridge artifact")
        wrappers.append(wrapper)
    bridge = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("bridge_hash") != bridge["artifact_hash"]:
        raise FailClosedRuntimeError("domain execution-ready bridge returned lineage mismatch")
    if bridge["bridge_status"] != FAILED_CLOSED:
        execution_ready_replay_path = Path(bridge["execution_ready_replay_reference"])
        _load_domain_approval_entry_lineage(
            Path(bridge["domain_approval_binding_replay_reference"]),
            approved_domain=bridge["approved_domain"],
        )
        _load_execution_ready_artifacts(execution_ready_replay_path)
        if replay_hash(_load_wrappers(execution_ready_replay_path, EXECUTION_READY_REPLAY_STEPS)) != bridge["execution_ready_replay_hash"]:
            raise FailClosedRuntimeError("domain execution-ready bridge execution-ready replay hash mismatch")
    return {
        "bridge_id": bridge["bridge_id"],
        "bridge_status": bridge["bridge_status"],
        "approved_domain": bridge["approved_domain"],
        "execution_status": bridge["execution_status"],
        "execution_ready_replay_reference": bridge["execution_ready_replay_reference"],
        "execution_ready_replay_hash": bridge["execution_ready_replay_hash"],
        "authorization_runtime_compatible": bridge["authorization_runtime_compatible"],
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
        **deepcopy(BOUNDARY_FLAGS),
        "failure_reason": bridge["failure_reason"],
    }


def render_domain_execution_ready_bridge_summary(capture: dict[str, Any]) -> str:
    """Render a compact operator summary."""

    if capture.get("fail_closed") is True:
        return f"FAILED_CLOSED: {capture.get('failure_reason')}"
    return "\n".join(
        [
            "Domain Execution-Ready Bridge",
            "",
            f"Bridge Status: {capture.get('bridge_status')}",
            f"Approved Domain: {capture.get('approved_domain')}",
            f"Execution Status: {capture.get('execution_status')}",
            f"Execution Ready Replay: {capture.get('execution_ready_replay_reference')}",
            "",
            "No authorization, worker request, dispatch, invocation, execution, repair, or retry was created.",
        ]
    )


def _load_domain_approval_entry_lineage(replay_path: Path, *, approved_domain: str) -> dict[str, Any]:
    reconstructed = reconstruct_domain_handoff_review_approval_binding_replay(replay_path)
    if reconstructed.get("approval_status") != DOMAIN_APPROVAL_BOUND:
        raise FailClosedRuntimeError("domain execution-ready bridge failed closed: approval not bound")
    if reconstructed.get("authorization_entry_status") != AUTHORIZATION_ENTRY_CREATED:
        raise FailClosedRuntimeError("domain execution-ready bridge failed closed: authorization entry missing")
    if reconstructed.get("execution_ready_continuation_status") != EXECUTION_READY_CONTINUATION_CREATED:
        raise FailClosedRuntimeError("domain execution-ready bridge failed closed: execution-ready continuation missing")
    domain = _require_string(approved_domain, "approved_domain")
    if reconstructed.get("approved_domain", "").lower() != domain.lower():
        raise FailClosedRuntimeError("domain execution-ready bridge failed closed: approved-domain mismatch")
    wrappers = _load_wrappers(
        replay_path,
        (
            "domain_approval_binding_recorded",
            "domain_authorization_entry_recorded",
            "domain_execution_ready_continuation_recorded",
            "domain_approval_entry_returned",
        ),
    )
    binding, authorization_entry, continuation, returned = [wrapper["artifact"] for wrapper in wrappers]
    _require_artifact_type(binding, DOMAIN_APPROVAL_BINDING_ARTIFACT_V1)
    _require_artifact_type(authorization_entry, DOMAIN_AUTHORIZATION_ENTRY_ARTIFACT_V1)
    _require_artifact_type(continuation, DOMAIN_EXECUTION_READY_CONTINUATION_ARTIFACT_V1)
    if authorization_entry.get("approval_binding_hash") != binding["artifact_hash"]:
        raise FailClosedRuntimeError("domain execution-ready bridge failed closed: authorization lineage mismatch")
    if continuation.get("approval_binding_hash") != binding["artifact_hash"]:
        raise FailClosedRuntimeError("domain execution-ready bridge failed closed: continuation lineage mismatch")
    if continuation.get("authorization_entry_hash") != authorization_entry["artifact_hash"]:
        raise FailClosedRuntimeError("domain execution-ready bridge failed closed: continuation authorization mismatch")
    if returned.get("approval_binding_hash") != binding["artifact_hash"]:
        raise FailClosedRuntimeError("domain execution-ready bridge failed closed: returned lineage mismatch")
    if not isinstance(binding.get("approval_hash"), str) or not binding["approval_hash"].strip():
        raise FailClosedRuntimeError("domain execution-ready bridge failed closed: approval hash missing")
    if binding.get("approval_reference") != binding.get("approval_entry_id"):
        raise FailClosedRuntimeError("domain execution-ready bridge failed closed: approval reference mismatch")
    _validate_authority(binding)
    _validate_authority(authorization_entry)
    _validate_authority(continuation)
    return {
        "replay_reference": str(replay_path),
        "replay_hash": replay_hash(wrappers),
        "reconstructed": reconstructed,
        "binding": deepcopy(binding),
        "authorization_entry": deepcopy(authorization_entry),
        "continuation": deepcopy(continuation),
        "returned": deepcopy(returned),
    }


def _compatibility_handoff_artifact(
    *,
    bridge_id: str,
    lineage: dict[str, Any],
    created_at: str,
    handoff_replay_path: Path,
) -> dict[str, Any]:
    binding = lineage["binding"]
    scope = binding["approved_scope"]
    handoff_id = f"{_require_string(bridge_id, 'bridge_id')}:COMPATIBILITY-HANDOFF"
    artifact = {
        "artifact_type": IMPLEMENTATION_HANDOFF_ARTIFACT_V1,
        "runtime_version": AIGOL_DOMAIN_APPROVAL_ENTRY_TO_EXECUTION_READY_AUTHORIZATION_BRIDGE_RUNTIME_VERSION,
        "handoff_id": handoff_id,
        "handoff_status": IMPLEMENTATION_HANDOFF_CREATED,
        "task_reference": binding["approval_entry_id"],
        "proposal_reference": binding["handoff_review_reference"],
        "proposal_hash": binding["handoff_review_hash"],
        "context_reference": binding["handoff_review_replay_reference"],
        "context_hash": binding["handoff_review_hash"],
        "domain_reference": binding["approved_domain"],
        "worker_reference": scope["target_worker_id"],
        "milestone_reference": "DOMAIN_ARTIFACT_CREATION",
        "output_targets": deepcopy(scope["allowed_outputs"]),
        "validation_references": {
            "domain_approval_binding_reference": binding["approval_entry_id"],
            "domain_approval_binding_hash": binding["artifact_hash"],
            "domain_authorization_entry_reference": lineage["authorization_entry"]["authorization_entry_id"],
            "domain_authorization_entry_hash": lineage["authorization_entry"]["artifact_hash"],
            "domain_execution_ready_continuation_reference": lineage["continuation"]["execution_ready_continuation_id"],
            "domain_execution_ready_continuation_hash": lineage["continuation"]["artifact_hash"],
        },
        "replay_references": {
            "domain_approval_binding_replay_reference": lineage["replay_reference"],
            "handoff_review_replay_reference": binding["handoff_review_replay_reference"],
            "compatibility_handoff_replay_reference": str(handoff_replay_path),
        },
        "constraints": deepcopy(scope["forbidden_operations"]),
        "assumptions": ["Domain approval-entry replay is the governing source for this compatibility handoff."],
        "known_gaps": ["Execution authorization, worker request, and worker invocation remain downstream."],
        "provider_necessity_classification": "PROVIDER_NOT_REQUIRED",
        "implementation_authorized": False,
        "proposal_only": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "worker_created": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "failure_reason": None,
    }
    artifact["handoff_hash"] = replay_hash(
        {
            "task_reference": artifact["task_reference"],
            "proposal_hash": artifact["proposal_hash"],
            "context_hash": artifact["context_hash"],
            "registry_resolution_hash": artifact["validation_references"]["domain_approval_binding_hash"],
            "output_targets": artifact["output_targets"],
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _compatibility_handoff_returned_artifact(handoff: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "event_type": "IMPLEMENTATION_HANDOFF_RETURNED",
        "handoff_reference": handoff["handoff_id"],
        "handoff_hash": handoff["artifact_hash"],
        "handoff_status": handoff["handoff_status"],
        "proposal_hash": handoff["proposal_hash"],
        "context_hash": handoff["context_hash"],
        "domain_reference": handoff["domain_reference"],
        "worker_reference": handoff["worker_reference"],
        "milestone_reference": handoff["milestone_reference"],
        "implementation_authorized": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "failure_reason": handoff["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _candidate_artifact(
    *,
    bridge_id: str,
    lineage: dict[str, Any],
    handoff: dict[str, Any],
    handoff_replay_path: Path,
    created_at: str,
) -> dict[str, Any]:
    binding = lineage["binding"]
    scope = binding["approved_scope"]
    artifact = {
        "artifact_type": EXECUTION_CANDIDATE_ARTIFACT_V1,
        "runtime_version": AIGOL_DOMAIN_APPROVAL_ENTRY_TO_EXECUTION_READY_AUTHORIZATION_BRIDGE_RUNTIME_VERSION,
        "candidate_id": f"{_require_string(bridge_id, 'bridge_id')}:CANDIDATE",
        "handoff_reference": handoff["handoff_id"],
        "handoff_hash": handoff["artifact_hash"],
        "handoff_replay_reference": str(handoff_replay_path),
        "chain_id": binding["canonical_chain_id"],
        "target_domain": binding["approved_domain"],
        "target_resource": "DOMAIN_ARTIFACTS",
        "target_worker": scope["target_worker_id"],
        "planned_artifacts": deepcopy(scope["allowed_outputs"]),
        "required_resource_roles": ["governed domain artifact worker"],
        "approval_status": "APPROVED",
        "approval_reference": binding["approval_reference"],
        "approval_hash": binding["approval_hash"],
        "upstream_lineage_reference": binding["approval_entry_id"],
        "upstream_lineage_hash": binding["artifact_hash"],
        "execution_scope": {
            "mode": "DOMAIN_ARTIFACT_AUTHORIZATION_READY",
            "domain_name": binding["approved_domain"],
            "operation": scope["operation"],
            "allowed_outputs": deepcopy(scope["allowed_outputs"]),
            "forbidden_operations": deepcopy(scope["forbidden_operations"]),
            "execution_authorized": False,
        },
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "worker_invoked": False,
        "code_generated": False,
        "files_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "authorization_created": False,
        "governance_mutated": False,
    }
    artifact["candidate_hash"] = _candidate_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _packet_artifact(
    *,
    bridge_id: str,
    candidate: dict[str, Any],
    lineage: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    scope = lineage["binding"]["approved_scope"]
    artifact = {
        "artifact_type": EXECUTION_PACKET_ARTIFACT_V1,
        "runtime_version": AIGOL_DOMAIN_APPROVAL_ENTRY_TO_EXECUTION_READY_AUTHORIZATION_BRIDGE_RUNTIME_VERSION,
        "packet_id": f"{_require_string(bridge_id, 'bridge_id')}:PACKET",
        "candidate_reference": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "chain_id": candidate["chain_id"],
        "execution_contract": {
            "contract_type": "DOMAIN_ARTIFACT_CREATION_AUTHORIZATION_READY",
            "execution_state": "NOT_STARTED",
            "execution_authorized": False,
            "preparation_only": True,
        },
        "allowed_outputs": deepcopy(scope["allowed_outputs"]),
        "forbidden_operations": list(dict.fromkeys([*scope["forbidden_operations"], *FORBIDDEN_OPERATIONS])),
        "required_validations": list(REQUIRED_VALIDATIONS),
        "worker_role_requirements": deepcopy(candidate["required_resource_roles"]),
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "worker_invoked": False,
        "code_generated": False,
        "files_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "authorization_created": False,
        "governance_mutated": False,
    }
    artifact["packet_hash"] = _packet_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _validation_artifact(
    *,
    bridge_id: str,
    lineage: dict[str, Any],
    handoff: dict[str, Any],
    candidate: dict[str, Any],
    packet: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    binding = lineage["binding"]
    checks = {
        "domain_approval_lineage": candidate["approval_hash"] == binding["approval_hash"],
        "handoff_lineage": candidate["handoff_reference"] == handoff["handoff_id"],
        "authorization_entry_lineage": lineage["authorization_entry"]["approval_binding_hash"] == binding["artifact_hash"],
        "execution_ready_continuation_lineage": lineage["continuation"]["approval_binding_hash"] == binding["artifact_hash"],
        "candidate_lineage": packet["candidate_hash"] == candidate["artifact_hash"],
        "packet_lineage": packet["packet_hash"] == _packet_hash(packet),
        "authority_boundaries": (
            candidate["worker_invoked"] is False
            and candidate["execution_requested"] is False
            and candidate["authorization_created"] is False
            and packet["worker_invoked"] is False
            and packet["execution_requested"] is False
            and packet["authorization_created"] is False
        ),
        "hash_integrity": candidate["candidate_hash"] == _candidate_hash(candidate),
    }
    if not all(checks.values()):
        raise FailClosedRuntimeError("domain execution-ready bridge failed closed: validation failed")
    artifact = {
        "artifact_type": EXECUTION_VALIDATION_ARTIFACT_V1,
        "runtime_version": AIGOL_DOMAIN_APPROVAL_ENTRY_TO_EXECUTION_READY_AUTHORIZATION_BRIDGE_RUNTIME_VERSION,
        "validation_id": f"{_require_string(bridge_id, 'bridge_id')}:VALIDATION",
        "candidate_reference": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "packet_reference": packet["packet_id"],
        "packet_hash": packet["artifact_hash"],
        "handoff_reference": handoff["handoff_id"],
        "handoff_hash": handoff["artifact_hash"],
        "approval_reference": binding["approval_reference"],
        "approval_hash": binding["approval_hash"],
        "validation_checks": checks,
        "validation_status": "DOMAIN_EXECUTION_READY_BRIDGE_VALIDATED",
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "authorization_created": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _ready_artifact(
    *,
    bridge_id: str,
    candidate: dict[str, Any],
    packet: dict[str, Any],
    validation: dict[str, Any],
    created_at: str,
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": EXECUTION_READY_STATUS_ARTIFACT_V1,
        "runtime_version": AIGOL_DOMAIN_APPROVAL_ENTRY_TO_EXECUTION_READY_AUTHORIZATION_BRIDGE_RUNTIME_VERSION,
        "dry_run_id": _require_string(bridge_id, "bridge_id"),
        "execution_status": status,
        "candidate_reference": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "packet_reference": packet["packet_id"],
        "packet_hash": packet["artifact_hash"],
        "validation_reference": validation["validation_id"],
        "validation_hash": validation["artifact_hash"],
        "execution_started": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "worker_invoked": False,
        "code_generated": False,
        "files_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "authorization_created": False,
        "governance_mutated": False,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_ready_artifact(*, bridge_id: Any, created_at: Any, failure_reason: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": EXECUTION_READY_STATUS_ARTIFACT_V1,
        "runtime_version": AIGOL_DOMAIN_APPROVAL_ENTRY_TO_EXECUTION_READY_AUTHORIZATION_BRIDGE_RUNTIME_VERSION,
        "dry_run_id": bridge_id if isinstance(bridge_id, str) and bridge_id.strip() else "INVALID-DOMAIN-READY-BRIDGE",
        "execution_status": FAILED_CLOSED,
        "candidate_reference": None,
        "candidate_hash": None,
        "packet_reference": None,
        "packet_hash": None,
        "validation_reference": None,
        "validation_hash": None,
        "execution_started": False,
        "created_at": created_at if isinstance(created_at, str) and created_at.strip() else "1970-01-01T00:00:00Z",
        "replay_visible": True,
        "worker_invoked": False,
        "code_generated": False,
        "files_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "authorization_created": False,
        "governance_mutated": False,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _bridge_artifact(
    *,
    bridge_id: str,
    lineage: dict[str, Any],
    handoff: dict[str, Any],
    ready: dict[str, Any],
    execution_ready_replay_path: Path,
    created_at: str,
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    binding = lineage["binding"]
    artifact = {
        "artifact_type": DOMAIN_EXECUTION_READY_BRIDGE_ARTIFACT_V1,
        "runtime_version": AIGOL_DOMAIN_APPROVAL_ENTRY_TO_EXECUTION_READY_AUTHORIZATION_BRIDGE_RUNTIME_VERSION,
        "bridge_id": _require_string(bridge_id, "bridge_id"),
        "bridge_status": status,
        "approved_domain": binding["approved_domain"],
        "domain_approval_binding_replay_reference": lineage["replay_reference"],
        "domain_approval_binding_replay_hash": lineage["replay_hash"],
        "domain_approval_binding_reference": binding["approval_entry_id"],
        "domain_approval_binding_hash": binding["artifact_hash"],
        "domain_authorization_entry_reference": lineage["authorization_entry"]["authorization_entry_id"],
        "domain_authorization_entry_hash": lineage["authorization_entry"]["artifact_hash"],
        "domain_execution_ready_continuation_reference": lineage["continuation"]["execution_ready_continuation_id"],
        "domain_execution_ready_continuation_hash": lineage["continuation"]["artifact_hash"],
        "compatibility_handoff_reference": handoff["handoff_id"],
        "compatibility_handoff_hash": handoff["artifact_hash"],
        "execution_ready_reference": ready["dry_run_id"],
        "execution_ready_hash": ready["artifact_hash"],
        "execution_ready_replay_reference": str(execution_ready_replay_path),
        "execution_ready_replay_hash": replay_hash(_load_wrappers(execution_ready_replay_path, EXECUTION_READY_REPLAY_STEPS)),
        "execution_status": ready["execution_status"],
        "authorization_runtime_compatible": ready["execution_status"] == EXECUTION_READY,
        "created_at": _require_string(created_at, "created_at"),
        **deepcopy(BOUNDARY_FLAGS),
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_bridge_artifact(
    *,
    bridge_id: Any,
    domain_approval_binding_replay_reference: Any,
    approved_domain: Any,
    created_at: Any,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": DOMAIN_EXECUTION_READY_BRIDGE_ARTIFACT_V1,
        "runtime_version": AIGOL_DOMAIN_APPROVAL_ENTRY_TO_EXECUTION_READY_AUTHORIZATION_BRIDGE_RUNTIME_VERSION,
        "bridge_id": bridge_id if isinstance(bridge_id, str) and bridge_id.strip() else "INVALID-DOMAIN-READY-BRIDGE",
        "bridge_status": FAILED_CLOSED,
        "approved_domain": approved_domain if isinstance(approved_domain, str) else None,
        "domain_approval_binding_replay_reference": domain_approval_binding_replay_reference
        if isinstance(domain_approval_binding_replay_reference, str)
        else None,
        "domain_approval_binding_replay_hash": None,
        "domain_approval_binding_reference": None,
        "domain_approval_binding_hash": None,
        "domain_authorization_entry_reference": None,
        "domain_authorization_entry_hash": None,
        "domain_execution_ready_continuation_reference": None,
        "domain_execution_ready_continuation_hash": None,
        "compatibility_handoff_reference": None,
        "compatibility_handoff_hash": None,
        "execution_ready_reference": None,
        "execution_ready_hash": None,
        "execution_ready_replay_reference": None,
        "execution_ready_replay_hash": None,
        "execution_status": FAILED_CLOSED,
        "authorization_runtime_compatible": False,
        "created_at": created_at if isinstance(created_at, str) and created_at.strip() else "1970-01-01T00:00:00Z",
        **deepcopy(BOUNDARY_FLAGS),
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _bridge_returned_artifact(bridge: dict[str, Any], *, created_at: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": DOMAIN_EXECUTION_READY_BRIDGE_RETURNED_ARTIFACT_V1,
        "runtime_version": AIGOL_DOMAIN_APPROVAL_ENTRY_TO_EXECUTION_READY_AUTHORIZATION_BRIDGE_RUNTIME_VERSION,
        "bridge_reference": bridge["bridge_id"],
        "bridge_hash": bridge["artifact_hash"],
        "bridge_status": bridge["bridge_status"],
        "approved_domain": bridge["approved_domain"],
        "execution_ready_replay_reference": bridge["execution_ready_replay_reference"],
        "execution_ready_replay_hash": bridge["execution_ready_replay_hash"],
        "authorization_runtime_compatible": bridge["authorization_runtime_compatible"],
        "created_at": _require_string(created_at, "created_at"),
        **deepcopy(BOUNDARY_FLAGS),
        "replay_visible": True,
        "failure_reason": bridge["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    *,
    bridge: dict[str, Any],
    returned: dict[str, Any],
    handoff: dict[str, Any] | None,
    candidate: dict[str, Any] | None,
    packet: dict[str, Any] | None,
    validation: dict[str, Any] | None,
    ready: dict[str, Any],
    replay_path: Path,
    handoff_replay_path: Path,
    execution_ready_replay_path: Path,
    bridge_replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "milestone_id": AIGOL_DOMAIN_APPROVAL_ENTRY_TO_EXECUTION_READY_AUTHORIZATION_BRIDGE_RUNTIME_VERSION,
        "bridge_status": bridge["bridge_status"],
        "approved_domain": bridge["approved_domain"],
        "execution_status": bridge["execution_status"],
        "execution_ready_replay_reference": bridge["execution_ready_replay_reference"],
        "execution_ready_replay_hash": bridge["execution_ready_replay_hash"],
        "execution_ready_reference": bridge["execution_ready_reference"],
        "execution_ready_hash": bridge["execution_ready_hash"],
        "authorization_runtime_compatible": bridge["authorization_runtime_compatible"],
        "compatibility_handoff_replay_reference": str(handoff_replay_path),
        "domain_execution_ready_bridge_replay_reference": str(replay_path),
        "bridge_event_replay_reference": str(bridge_replay_path),
        "domain_execution_ready_bridge_artifact": deepcopy(bridge),
        "domain_execution_ready_bridge_returned_artifact": deepcopy(returned),
        "compatibility_handoff_artifact": deepcopy(handoff),
        "execution_candidate_artifact": deepcopy(candidate),
        "execution_packet_artifact": deepcopy(packet),
        "execution_validation_artifact": deepcopy(validation),
        "execution_ready_status_artifact": deepcopy(ready),
        "fail_closed": bridge["bridge_status"] == FAILED_CLOSED,
        **deepcopy(BOUNDARY_FLAGS),
        "failure_reason": bridge["failure_reason"],
    }
    capture["domain_execution_ready_bridge_capture_hash"] = replay_hash(capture)
    return capture


def _approval_binding_already_bridged(session_root: Path, binding_hash: str) -> bool:
    for path in sorted(session_root.glob("TURN-*/domain_execution_ready_bridge/bridge/000_domain_execution_ready_bridge_recorded.json")):
        try:
            wrapper = load_json(path)
            _verify_wrapper_hash(wrapper, "domain execution-ready bridge replay")
            artifact = wrapper.get("artifact")
            if isinstance(artifact, dict):
                _verify_artifact_hash(artifact, "domain execution-ready bridge artifact")
                if artifact.get("domain_approval_binding_hash") == binding_hash and artifact.get("bridge_status") != FAILED_CLOSED:
                    return True
        except FailClosedRuntimeError:
            continue
    return False


def _load_execution_ready_artifacts(replay_path: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    wrappers = _load_wrappers(replay_path, EXECUTION_READY_REPLAY_STEPS)
    candidate, packet, validation, ready = [wrapper["artifact"] for wrapper in wrappers]
    _require_artifact_type(candidate, EXECUTION_CANDIDATE_ARTIFACT_V1)
    _require_artifact_type(packet, EXECUTION_PACKET_ARTIFACT_V1)
    _require_artifact_type(validation, EXECUTION_VALIDATION_ARTIFACT_V1)
    _require_artifact_type(ready, EXECUTION_READY_STATUS_ARTIFACT_V1)
    if packet.get("candidate_hash") != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("domain execution-ready bridge candidate lineage mismatch")
    if validation.get("candidate_hash") != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("domain execution-ready bridge validation candidate mismatch")
    if validation.get("packet_hash") != packet["artifact_hash"]:
        raise FailClosedRuntimeError("domain execution-ready bridge validation packet mismatch")
    if ready.get("validation_hash") != validation["artifact_hash"]:
        raise FailClosedRuntimeError("domain execution-ready bridge ready validation mismatch")
    if candidate.get("candidate_hash") != _candidate_hash(candidate):
        raise FailClosedRuntimeError("domain execution-ready bridge candidate hash mismatch")
    if packet.get("packet_hash") != _packet_hash(packet):
        raise FailClosedRuntimeError("domain execution-ready bridge packet hash mismatch")
    if ready.get("execution_status") != EXECUTION_READY:
        raise FailClosedRuntimeError("domain execution-ready bridge execution status mismatch")
    return candidate, packet, validation, ready


def _load_wrappers(replay_path: Path, steps: tuple[str, ...]) -> list[dict[str, Any]]:
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(steps):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("domain execution-ready bridge replay ordering mismatch")
        _verify_wrapper_hash(wrapper, "domain execution-ready bridge replay")
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("domain execution-ready bridge replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "domain execution-ready bridge replay artifact")
        wrappers.append(wrapper)
    return wrappers


def _candidate_hash(candidate: dict[str, Any]) -> str:
    return replay_hash(
        {
            "handoff_reference": candidate.get("handoff_reference"),
            "handoff_hash": candidate.get("handoff_hash"),
            "chain_id": candidate.get("chain_id"),
            "planned_artifacts": candidate.get("planned_artifacts", []),
            "required_resource_roles": candidate.get("required_resource_roles", []),
            "approval_hash": candidate.get("approval_hash"),
            "execution_scope": candidate.get("execution_scope", {}),
        }
    )


def _packet_hash(packet: dict[str, Any]) -> str:
    return replay_hash(
        {
            "candidate_reference": packet.get("candidate_reference"),
            "candidate_hash": packet.get("candidate_hash"),
            "execution_contract": packet.get("execution_contract", {}),
            "allowed_outputs": packet.get("allowed_outputs", []),
            "forbidden_operations": packet.get("forbidden_operations", []),
            "required_validations": packet.get("required_validations", []),
            "worker_role_requirements": packet.get("worker_role_requirements", []),
        }
    )


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any], steps: tuple[str, ...]) -> None:
    if steps[index] != step:
        raise FailClosedRuntimeError("domain execution-ready bridge replay ordering mismatch")
    _verify_artifact_hash(artifact, "domain execution-ready bridge artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "event_type": step.upper(),
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(
    replay_dir: Path,
    index: int,
    step: str,
    artifact: dict[str, Any],
    steps: tuple[str, ...],
) -> None:
    try:
        _persist_step(replay_dir, index, step, artifact, steps)
    except FailClosedRuntimeError:
        return


def _ensure_replay_available(replay_path: Path, steps: tuple[str, ...]) -> None:
    for index, step in enumerate(steps):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError(f"append-only domain execution-ready bridge artifact already exists: {step}")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    actual = _require_string(artifact.get("artifact_hash"), "artifact_hash")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any], label: str) -> None:
    actual = _require_string(wrapper.get("replay_hash"), "replay_hash")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _require_artifact_type(artifact: dict[str, Any], artifact_type: str) -> None:
    if artifact.get("artifact_type") != artifact_type:
        raise FailClosedRuntimeError("domain execution-ready bridge failed closed: artifact type mismatch")


def _validate_authority(artifact: dict[str, Any]) -> None:
    for field, expected in BOUNDARY_FLAGS.items():
        if field in artifact and artifact.get(field) is not expected:
            raise FailClosedRuntimeError("domain execution-ready bridge failed closed: authority boundary violation")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"domain execution-ready bridge failed closed: {field_name} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return f"domain execution-ready bridge failed closed: {exc}"
