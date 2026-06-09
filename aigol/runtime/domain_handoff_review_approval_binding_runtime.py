"""Approval entry binding for reviewed governed domain workflows."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
from typing import Any

from aigol.runtime.clarified_domain_intent_handoff_review_runtime import (
    FAIL_CLOSED,
    HANDOFF_REVIEW_DECISION_ARTIFACT_V1,
    WORKER_BINDING_APPROVED,
    reconstruct_clarified_domain_intent_handoff_review_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_DOMAIN_HANDOFF_REVIEW_APPROVAL_AND_BINDING_ENTRY_RUNTIME_VERSION = (
    "AIGOL_DOMAIN_HANDOFF_REVIEW_APPROVAL_AND_BINDING_ENTRY_RUNTIME_V1"
)
DOMAIN_APPROVAL_BINDING_ARTIFACT_V1 = "DOMAIN_APPROVAL_BINDING_ARTIFACT_V1"
DOMAIN_AUTHORIZATION_ENTRY_ARTIFACT_V1 = "DOMAIN_AUTHORIZATION_ENTRY_ARTIFACT_V1"
DOMAIN_EXECUTION_READY_CONTINUATION_ARTIFACT_V1 = "DOMAIN_EXECUTION_READY_CONTINUATION_ARTIFACT_V1"
DOMAIN_APPROVAL_ENTRY_RETURNED_ARTIFACT_V1 = "DOMAIN_APPROVAL_ENTRY_RETURNED_ARTIFACT_V1"

DOMAIN_APPROVAL_BOUND = "DOMAIN_APPROVAL_BOUND"
AUTHORIZATION_ENTRY_CREATED = "AUTHORIZATION_ENTRY_CREATED"
EXECUTION_READY_CONTINUATION_CREATED = "EXECUTION_READY_CONTINUATION_CREATED"

REPLAY_STEPS = (
    "domain_approval_binding_recorded",
    "domain_authorization_entry_recorded",
    "domain_execution_ready_continuation_recorded",
    "domain_approval_entry_returned",
)

AUTHORITY_FLAGS = {
    "provider_invoked": False,
    "ocs_authority": False,
    "approval_authority": False,
    "execution_authority": False,
    "worker_authority": False,
    "authorization_created": False,
    "worker_request_created": False,
    "worker_assigned": False,
    "worker_dispatched": False,
    "worker_invoked": False,
    "execution_started": False,
    "domain_created": False,
    "domain_activated": False,
    "live_registry_mutated": False,
    "repair_started": False,
    "retry_started": False,
    "replay_mutated": False,
}


def detect_domain_approval_entry_intent(human_prompt: str) -> dict[str, Any]:
    """Detect narrow operator approval prompts for reviewed domain workflows."""

    prompt = _require_string(human_prompt, "human_prompt")
    normalized = " ".join(prompt.strip().rstrip(".?!").split())
    lowered = normalized.lower()
    patterns = (
        r"^approve\s+(?P<domain>[A-Za-z][A-Za-z0-9_-]*)\s+for\s+domain\s+artifact\s+creation$",
        r"^approve\s+reviewed\s+(?P<domain>[A-Za-z][A-Za-z0-9_-]*)\s+workflow$",
        r"^continue\s+(?P<domain>[A-Za-z][A-Za-z0-9_-]*)\s+to\s+authorization$",
        r"^authorize\s+(?P<domain>[A-Za-z][A-Za-z0-9_-]*)\s+domain\s+artifact\s+request$",
    )
    for pattern in patterns:
        match = re.match(pattern, normalized, flags=re.IGNORECASE)
        if match:
            domain = match.group("domain")
            if lowered.startswith("authorize"):
                approval_action = "AUTHORIZE_DOMAIN_ARTIFACT_REQUEST"
            elif lowered.startswith("approve"):
                approval_action = "APPROVE_DOMAIN_ARTIFACT_CREATION"
            else:
                approval_action = "CONTINUE_TO_AUTHORIZATION"
            return {
                "approval_entry_intent_detected": True,
                "domain_name": domain,
                "approval_action": approval_action,
                "matched_prompt": normalized,
            }
    return {
        "approval_entry_intent_detected": False,
        "domain_name": None,
        "approval_action": None,
        "matched_prompt": normalized,
    }


def find_latest_domain_handoff_review(
    *,
    session_root: str | Path,
    domain_name: str,
) -> dict[str, Any]:
    """Find the latest unbound handoff review replay for a domain in a session."""

    root = Path(session_root)
    domain = _require_string(domain_name, "domain_name")
    if not root.exists():
        raise FailClosedRuntimeError("domain approval entry failed closed: session root missing")
    candidates: list[dict[str, Any]] = []
    for path in sorted(root.glob("TURN-*/clarified_domain_handoff_review")):
        try:
            reconstructed = reconstruct_clarified_domain_intent_handoff_review_replay(path)
            wrapper = load_json(path / "000_handoff_review_decision_recorded.json")
            _verify_wrapper_hash(wrapper)
            artifact = wrapper.get("artifact")
            if not isinstance(artifact, dict):
                continue
            _verify_artifact_hash(artifact, "handoff review decision artifact")
        except FailClosedRuntimeError:
            continue
        if reconstructed.get("review_decision") != WORKER_BINDING_APPROVED:
            continue
        if str(reconstructed.get("proposed_domain") or "").lower() != domain.lower():
            continue
        if _review_already_bound(root, artifact["artifact_hash"]):
            continue
        candidates.append(
            {
                "handoff_review_replay_reference": str(path),
                "handoff_review_decision_artifact": deepcopy(artifact),
                "turn_id": path.parent.name,
                "created_at": artifact.get("created_at"),
            }
        )
    if not candidates:
        raise FailClosedRuntimeError("domain approval entry failed closed: matching reviewed domain not found")
    return candidates[-1]


def bind_domain_handoff_review_approval(
    *,
    approval_entry_id: str,
    handoff_review_replay_reference: str,
    operator_prompt: str,
    approved_domain: str,
    approving_actor: str,
    approved_at: str,
    replay_dir: str | Path,
    latest_handoff_review_replay_reference: str | None = None,
) -> dict[str, Any]:
    """Bind an operator approval prompt to one reviewed domain handoff decision."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        intent = detect_domain_approval_entry_intent(operator_prompt)
        if intent["approval_entry_intent_detected"] is not True:
            raise FailClosedRuntimeError("domain approval entry failed closed: approval intent missing")
        if intent["domain_name"].lower() != _require_string(approved_domain, "approved_domain").lower():
            raise FailClosedRuntimeError("domain approval entry failed closed: approval-domain mismatch")
        if latest_handoff_review_replay_reference is not None and (
            str(Path(latest_handoff_review_replay_reference))
            != str(Path(_require_string(handoff_review_replay_reference, "handoff_review_replay_reference")))
        ):
            raise FailClosedRuntimeError("domain approval entry failed closed: stale handoff review")
        review = _load_handoff_review(Path(handoff_review_replay_reference), approved_domain)
        binding = _approval_binding_artifact(
            approval_entry_id=approval_entry_id,
            operator_prompt=operator_prompt,
            intent=intent,
            review=review,
            handoff_review_replay_reference=handoff_review_replay_reference,
            approving_actor=approving_actor,
            approved_at=approved_at,
        )
        authorization_entry = _authorization_entry_artifact(binding=binding, approved_at=approved_at)
        continuation = _execution_ready_continuation_artifact(
            binding=binding,
            authorization_entry=authorization_entry,
            approved_at=approved_at,
        )
        returned = _returned_artifact(
            binding=binding,
            authorization_entry=authorization_entry,
            continuation=continuation,
            approved_at=approved_at,
        )
        _persist_step(replay_path, 0, REPLAY_STEPS[0], binding)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], authorization_entry)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], continuation)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], returned)
        return _capture(binding, authorization_entry, continuation, returned, replay_path)
    except Exception as exc:
        binding = _failed_binding_artifact(
            approval_entry_id=approval_entry_id,
            handoff_review_replay_reference=handoff_review_replay_reference,
            operator_prompt=operator_prompt,
            approved_domain=approved_domain,
            approving_actor=approving_actor,
            approved_at=approved_at,
            failure_reason=_failure_reason(exc),
        )
        authorization_entry = _failed_authorization_entry_artifact(binding, approved_at=approved_at)
        continuation = _failed_continuation_artifact(binding, authorization_entry, approved_at=approved_at)
        returned = _returned_artifact(
            binding=binding,
            authorization_entry=authorization_entry,
            continuation=continuation,
            approved_at=approved_at if isinstance(approved_at, str) and approved_at.strip() else "1970-01-01T00:00:00Z",
        )
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], binding)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], authorization_entry)
        _persist_failure_if_possible(replay_path, 2, REPLAY_STEPS[2], continuation)
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], returned)
        return _capture(binding, authorization_entry, continuation, returned, replay_path)


def reconstruct_domain_handoff_review_approval_binding_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct domain handoff review approval binding replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("domain approval entry replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("domain approval entry replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "domain approval entry artifact")
        _validate_authority_flags(artifact)
        wrappers.append(wrapper)
    binding = wrappers[0]["artifact"]
    authorization_entry = wrappers[1]["artifact"]
    continuation = wrappers[2]["artifact"]
    returned = wrappers[3]["artifact"]
    if authorization_entry.get("approval_binding_hash") != binding["artifact_hash"]:
        raise FailClosedRuntimeError("domain approval entry authorization lineage mismatch")
    if continuation.get("approval_binding_hash") != binding["artifact_hash"]:
        raise FailClosedRuntimeError("domain approval entry continuation lineage mismatch")
    if continuation.get("authorization_entry_hash") != authorization_entry["artifact_hash"]:
        raise FailClosedRuntimeError("domain approval entry continuation authorization mismatch")
    if returned.get("approval_binding_hash") != binding["artifact_hash"]:
        raise FailClosedRuntimeError("domain approval entry returned binding mismatch")
    if binding["approval_status"] != FAIL_CLOSED:
        review = _load_handoff_review(
            _resolve_replay_reference(binding["handoff_review_replay_reference"], anchor=replay_path),
            binding["approved_domain"],
        )
        if review["artifact_hash"] != binding["handoff_review_hash"]:
            raise FailClosedRuntimeError("domain approval entry handoff review hash mismatch")
    return {
        "approval_entry_id": binding["approval_entry_id"],
        "approval_status": binding["approval_status"],
        "approved_domain": binding["approved_domain"],
        "handoff_review_reference": binding["handoff_review_reference"],
        "canonical_chain_id": binding["canonical_chain_id"],
        "authorization_entry_status": authorization_entry["authorization_entry_status"],
        "execution_ready_continuation_status": continuation["execution_ready_continuation_status"],
        "next_runtime": continuation["next_runtime"],
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        **deepcopy(AUTHORITY_FLAGS),
        "failure_reason": binding["failure_reason"],
        "replay_hash": replay_hash(wrappers),
    }


def render_domain_handoff_review_approval_binding_summary(capture: dict[str, Any]) -> str:
    """Render a compact operator summary for domain approval entry."""

    if capture.get("fail_closed") is True:
        return f"FAILED_CLOSED: {capture.get('failure_reason')}"
    return "\n".join(
        [
            "Domain Approval Binding",
            "",
            f"Approval Status: {capture.get('approval_status')}",
            f"Approved Domain: {capture.get('approved_domain')}",
            f"Authorization Entry Status: {capture.get('authorization_entry_status')}",
            f"Execution Ready Continuation: {capture.get('execution_ready_continuation_status')}",
            f"Next Runtime: {capture.get('next_runtime')}",
            "",
            "No authorization, worker request, dispatch, invocation, execution, repair, or retry was created.",
        ]
    )


def _resolve_replay_reference(reference: Any, *, anchor: Path) -> Path:
    replay_path = Path(_require_string(reference, "replay_reference"))
    if replay_path.is_absolute() or replay_path.exists():
        return replay_path
    for parent in (anchor, *anchor.parents):
        candidate = parent / replay_path
        if candidate.exists():
            return candidate
    return replay_path


def _load_handoff_review(replay_path: Path, approved_domain: str) -> dict[str, Any]:
    reconstructed = reconstruct_clarified_domain_intent_handoff_review_replay(replay_path)
    if reconstructed.get("review_decision") != WORKER_BINDING_APPROVED:
        raise FailClosedRuntimeError("domain approval entry failed closed: review is not worker-binding approved")
    wrapper = load_json(replay_path / "000_handoff_review_decision_recorded.json")
    _verify_wrapper_hash(wrapper)
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("domain approval entry failed closed: handoff review missing")
    _verify_artifact_hash(artifact, "handoff review decision artifact")
    if artifact.get("artifact_type") != HANDOFF_REVIEW_DECISION_ARTIFACT_V1:
        raise FailClosedRuntimeError("domain approval entry failed closed: invalid handoff review")
    if artifact.get("review_decision") != WORKER_BINDING_APPROVED:
        raise FailClosedRuntimeError("domain approval entry failed closed: review is not approved")
    if str(artifact.get("proposed_domain") or "").lower() != _require_string(approved_domain, "approved_domain").lower():
        raise FailClosedRuntimeError("domain approval entry failed closed: approval-domain mismatch")
    if artifact.get("next_certified_stage") != "AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW":
        raise FailClosedRuntimeError("domain approval entry failed closed: review stage mismatch")
    worker_binding = artifact.get("worker_binding")
    if not isinstance(worker_binding, dict) or not worker_binding:
        raise FailClosedRuntimeError("domain approval entry failed closed: worker binding missing")
    if worker_binding.get("domain_name") != artifact.get("proposed_domain"):
        raise FailClosedRuntimeError("domain approval entry failed closed: worker binding domain mismatch")
    if artifact.get("failure_reason") not in {None, ""}:
        raise FailClosedRuntimeError("domain approval entry failed closed: handoff review failed closed")
    return deepcopy(artifact)


def _approval_binding_artifact(
    *,
    approval_entry_id: str,
    operator_prompt: str,
    intent: dict[str, Any],
    review: dict[str, Any],
    handoff_review_replay_reference: str,
    approving_actor: str,
    approved_at: str,
) -> dict[str, Any]:
    actor = _require_string(approving_actor, "approving_actor")
    if actor.lower() in {"openai", "provider", "ocs", "llm"}:
        raise FailClosedRuntimeError("domain approval entry failed closed: approval actor invalid")
    worker_binding = review["worker_binding"]
    artifact = {
        "artifact_type": DOMAIN_APPROVAL_BINDING_ARTIFACT_V1,
        "runtime_version": AIGOL_DOMAIN_HANDOFF_REVIEW_APPROVAL_AND_BINDING_ENTRY_RUNTIME_VERSION,
        "approval_entry_id": _require_string(approval_entry_id, "approval_entry_id"),
        "approval_status": DOMAIN_APPROVAL_BOUND,
        "operator_prompt": _require_string(operator_prompt, "operator_prompt"),
        "operator_prompt_hash": replay_hash(operator_prompt),
        "approval_action": intent["approval_action"],
        "approved_domain": intent["domain_name"],
        "approving_actor": actor,
        "approved_at": _require_string(approved_at, "approved_at"),
        "handoff_review_replay_reference": _require_string(
            handoff_review_replay_reference,
            "handoff_review_replay_reference",
        ),
        "handoff_review_reference": review["review_id"],
        "handoff_review_hash": review["artifact_hash"],
        "canonical_chain_id": review["canonical_chain_id"],
        "approved_scope": {
            "domain_name": review["proposed_domain"],
            "target_worker_id": worker_binding["target_worker_id"],
            "target_worker_family": worker_binding["target_worker_family"],
            "authorized_scope": worker_binding["authorized_scope"],
            "operation": worker_binding["operation"],
            "allowed_outputs": deepcopy(worker_binding["allowed_outputs"]),
            "forbidden_operations": deepcopy(worker_binding["forbidden_operations"]),
        },
        "scope_preservation": {
            "domain_identity_preserved": intent["domain_name"].lower() == review["proposed_domain"].lower(),
            "allowed_outputs_preserved": True,
            "forbidden_operations_preserved": True,
            "worker_binding_preserved": True,
            "no_scope_broadening": True,
        },
        "approval_reference": _require_string(approval_entry_id, "approval_entry_id"),
        "approval_hash": None,
        "execution_ready_continuation_created": False,
        **deepcopy(AUTHORITY_FLAGS),
        "replay_visible": True,
        "failure_reason": None,
    }
    artifact["binding_hash"] = _binding_hash(artifact)
    artifact["approval_hash"] = artifact["binding_hash"]
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _authorization_entry_artifact(*, binding: dict[str, Any], approved_at: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": DOMAIN_AUTHORIZATION_ENTRY_ARTIFACT_V1,
        "runtime_version": AIGOL_DOMAIN_HANDOFF_REVIEW_APPROVAL_AND_BINDING_ENTRY_RUNTIME_VERSION,
        "authorization_entry_id": f"{binding['approval_entry_id']}:AUTHORIZATION-ENTRY",
        "authorization_entry_status": AUTHORIZATION_ENTRY_CREATED if binding["approval_status"] != FAIL_CLOSED else FAIL_CLOSED,
        "approval_binding_reference": binding["approval_entry_id"],
        "approval_binding_hash": binding["artifact_hash"],
        "approval_reference": binding["approval_reference"],
        "approval_hash": binding["approval_hash"],
        "approved_domain": binding["approved_domain"],
        "canonical_chain_id": binding["canonical_chain_id"],
        "target_worker_id": binding.get("approved_scope", {}).get("target_worker_id"),
        "next_required_runtime": "AIGOL_EXECUTION_AUTHORIZATION_RUNTIME_V1",
        "authorization_replay_reference": None,
        "authorization_created": False,
        "created_at": _require_string(approved_at, "approved_at"),
        **deepcopy(AUTHORITY_FLAGS),
        "replay_visible": True,
        "failure_reason": binding["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _execution_ready_continuation_artifact(
    *,
    binding: dict[str, Any],
    authorization_entry: dict[str, Any],
    approved_at: str,
) -> dict[str, Any]:
    status = EXECUTION_READY_CONTINUATION_CREATED if binding["approval_status"] != FAIL_CLOSED else FAIL_CLOSED
    artifact = {
        "artifact_type": DOMAIN_EXECUTION_READY_CONTINUATION_ARTIFACT_V1,
        "runtime_version": AIGOL_DOMAIN_HANDOFF_REVIEW_APPROVAL_AND_BINDING_ENTRY_RUNTIME_VERSION,
        "execution_ready_continuation_id": f"{binding['approval_entry_id']}:EXECUTION-READY-CONTINUATION",
        "execution_ready_continuation_status": status,
        "approval_binding_reference": binding["approval_entry_id"],
        "approval_binding_hash": binding["artifact_hash"],
        "authorization_entry_reference": authorization_entry["authorization_entry_id"],
        "authorization_entry_hash": authorization_entry["artifact_hash"],
        "approved_domain": binding["approved_domain"],
        "canonical_chain_id": binding["canonical_chain_id"],
        "approval_reference": binding["approval_reference"],
        "approval_hash": binding["approval_hash"],
        "next_runtime": "AIGOL_HANDOFF_REVIEW_TO_AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_RUNTIME_V1",
        "next_required_inputs": [
            "DOMAIN_APPROVAL_BINDING_ARTIFACT_V1",
            "HANDOFF_REVIEW_DECISION_ARTIFACT_V1",
            "OCS_EXECUTION_HANDOFF_OR_EQUIVALENT_EXECUTION_READY_PACKET",
        ],
        "execution_ready_replay_reference": None,
        "execution_ready_created": False,
        "created_at": _require_string(approved_at, "approved_at"),
        **deepcopy(AUTHORITY_FLAGS),
        "replay_visible": True,
        "failure_reason": binding["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(
    *,
    binding: dict[str, Any],
    authorization_entry: dict[str, Any],
    continuation: dict[str, Any],
    approved_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": DOMAIN_APPROVAL_ENTRY_RETURNED_ARTIFACT_V1,
        "runtime_version": AIGOL_DOMAIN_HANDOFF_REVIEW_APPROVAL_AND_BINDING_ENTRY_RUNTIME_VERSION,
        "approval_binding_reference": binding["approval_entry_id"],
        "approval_binding_hash": binding["artifact_hash"],
        "authorization_entry_reference": authorization_entry["authorization_entry_id"],
        "authorization_entry_hash": authorization_entry["artifact_hash"],
        "execution_ready_continuation_reference": continuation["execution_ready_continuation_id"],
        "execution_ready_continuation_hash": continuation["artifact_hash"],
        "approval_status": binding["approval_status"],
        "authorization_entry_status": authorization_entry["authorization_entry_status"],
        "execution_ready_continuation_status": continuation["execution_ready_continuation_status"],
        "approved_domain": binding["approved_domain"],
        "next_runtime": continuation["next_runtime"],
        "created_at": _require_string(approved_at, "approved_at"),
        **deepcopy(AUTHORITY_FLAGS),
        "replay_visible": True,
        "failure_reason": binding["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_binding_artifact(
    *,
    approval_entry_id: Any,
    handoff_review_replay_reference: Any,
    operator_prompt: Any,
    approved_domain: Any,
    approving_actor: Any,
    approved_at: Any,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": DOMAIN_APPROVAL_BINDING_ARTIFACT_V1,
        "runtime_version": AIGOL_DOMAIN_HANDOFF_REVIEW_APPROVAL_AND_BINDING_ENTRY_RUNTIME_VERSION,
        "approval_entry_id": approval_entry_id if isinstance(approval_entry_id, str) and approval_entry_id.strip() else "INVALID-APPROVAL-ENTRY",
        "approval_status": FAIL_CLOSED,
        "operator_prompt": operator_prompt if isinstance(operator_prompt, str) else "",
        "operator_prompt_hash": replay_hash(operator_prompt) if isinstance(operator_prompt, str) else None,
        "approval_action": None,
        "approved_domain": approved_domain if isinstance(approved_domain, str) else None,
        "approving_actor": approving_actor if isinstance(approving_actor, str) else None,
        "approved_at": approved_at if isinstance(approved_at, str) and approved_at.strip() else "1970-01-01T00:00:00Z",
        "handoff_review_replay_reference": handoff_review_replay_reference if isinstance(handoff_review_replay_reference, str) else None,
        "handoff_review_reference": None,
        "handoff_review_hash": None,
        "canonical_chain_id": None,
        "approved_scope": {},
        "scope_preservation": {},
        "approval_reference": None,
        "approval_hash": None,
        "execution_ready_continuation_created": False,
        **deepcopy(AUTHORITY_FLAGS),
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["binding_hash"] = _binding_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_authorization_entry_artifact(binding: dict[str, Any], *, approved_at: str) -> dict[str, Any]:
    return _authorization_entry_artifact(binding=binding, approved_at=approved_at if isinstance(approved_at, str) and approved_at.strip() else "1970-01-01T00:00:00Z")


def _failed_continuation_artifact(
    binding: dict[str, Any],
    authorization_entry: dict[str, Any],
    *,
    approved_at: str,
) -> dict[str, Any]:
    return _execution_ready_continuation_artifact(
        binding=binding,
        authorization_entry=authorization_entry,
        approved_at=approved_at if isinstance(approved_at, str) and approved_at.strip() else "1970-01-01T00:00:00Z",
    )


def _capture(
    binding: dict[str, Any],
    authorization_entry: dict[str, Any],
    continuation: dict[str, Any],
    returned: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "milestone_id": AIGOL_DOMAIN_HANDOFF_REVIEW_APPROVAL_AND_BINDING_ENTRY_RUNTIME_VERSION,
        "final_classification": "DOMAIN_HANDOFF_REVIEW_APPROVAL_AND_BINDING_ENTRY_STATUS",
        "approval_status": binding["approval_status"],
        "approval_reference": binding["approval_reference"],
        "approval_hash": binding["approval_hash"],
        "approved_domain": binding["approved_domain"],
        "canonical_chain_id": binding["canonical_chain_id"],
        "authorization_entry_status": authorization_entry["authorization_entry_status"],
        "authorization_entry_reference": authorization_entry["authorization_entry_id"],
        "execution_ready_continuation_status": continuation["execution_ready_continuation_status"],
        "execution_ready_continuation_reference": continuation["execution_ready_continuation_id"],
        "next_runtime": continuation["next_runtime"],
        "domain_approval_binding_artifact": deepcopy(binding),
        "domain_authorization_entry_artifact": deepcopy(authorization_entry),
        "domain_execution_ready_continuation_artifact": deepcopy(continuation),
        "domain_approval_entry_returned_artifact": deepcopy(returned),
        "domain_approval_binding_replay_reference": str(replay_path),
        "fail_closed": binding["approval_status"] == FAIL_CLOSED,
        **deepcopy(AUTHORITY_FLAGS),
        "failure_reason": binding["failure_reason"],
    }
    capture["domain_approval_binding_capture_hash"] = replay_hash(capture)
    return capture


def _review_already_bound(session_root: Path, review_hash: str) -> bool:
    for path in sorted(session_root.glob("TURN-*/domain_approval_binding/000_domain_approval_binding_recorded.json")):
        try:
            wrapper = load_json(path)
            _verify_wrapper_hash(wrapper)
            artifact = wrapper.get("artifact")
            if isinstance(artifact, dict):
                _verify_artifact_hash(artifact, "domain approval binding artifact")
                if artifact.get("handoff_review_hash") == review_hash and artifact.get("approval_status") != FAIL_CLOSED:
                    return True
        except FailClosedRuntimeError:
            continue
    return False


def _binding_hash(artifact: dict[str, Any]) -> str:
    payload = deepcopy(artifact)
    payload.pop("binding_hash", None)
    payload.pop("artifact_hash", None)
    payload.pop("approval_hash", None)
    return replay_hash(payload)


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("domain approval entry replay step ordering mismatch")
    _verify_artifact_hash(artifact, "domain approval entry artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    path = replay_dir / f"{index:03d}_{step}.json"
    if not path.exists():
        try:
            _persist_step(replay_dir, index, step, artifact)
        except FailClosedRuntimeError:
            return


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError(f"append-only domain approval entry artifact already exists: {step}")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    actual = _require_string(artifact.get("artifact_hash"), "artifact_hash")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} hash mismatch")
    if "binding_hash" in artifact and artifact["binding_hash"] != _binding_hash(artifact):
        raise FailClosedRuntimeError(f"{label} binding hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = _require_string(wrapper.get("replay_hash"), "replay_hash")
    expected_input = deepcopy(wrapper)
    expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("domain approval entry replay hash mismatch")


def _validate_authority_flags(artifact: dict[str, Any]) -> None:
    for key, expected in AUTHORITY_FLAGS.items():
        if artifact.get(key) is not expected:
            raise FailClosedRuntimeError("domain approval entry authority violation")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"domain approval entry failed closed: {field_name} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "domain approval entry failed closed"
