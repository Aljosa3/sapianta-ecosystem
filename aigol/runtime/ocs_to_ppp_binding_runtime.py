"""OCS-to-PPP proposal-only handoff binding runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.ocs_cognition_runtime import OCS_COGNITION_ARTIFACT_V1, OCS_COGNITION_COMPLETED
from aigol.runtime.ocs_context_assembly_runtime import OCS_CONTEXT_ASSEMBLED, OCS_CONTEXT_ASSEMBLY_ARTIFACT_V1
from aigol.runtime.ocs_memory_and_continuity_runtime import (
    OCS_CONTINUITY_ARTIFACT_V1,
    OCS_MEMORY_AND_CONTINUITY_RECORDED,
    OCS_MEMORY_ARTIFACT_V1,
)
from aigol.runtime.ocs_replay_derived_intent_runtime import (
    OCS_REPLAY_DERIVED_INTENT_ARTIFACT_V1,
    OCS_REPLAY_DERIVED_INTENT_CREATED,
)
from aigol.runtime.ocs_semantic_resolution_runtime import (
    OCS_SEMANTIC_RESOLUTION_ARTIFACT_V1,
    OCS_SEMANTIC_RESOLUTION_COMPLETED,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_OCS_TO_PPP_BINDING_RUNTIME_VERSION = "AIGOL_OCS_TO_PPP_BINDING_RUNTIME_V1"
OCS_TO_PPP_HANDOFF_ARTIFACT_V1 = "OCS_TO_PPP_HANDOFF_ARTIFACT_V1"
OCS_TO_PPP_HANDOFF_CANDIDATE_CREATED = "OCS_TO_PPP_HANDOFF_CANDIDATE_CREATED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "ocs_to_ppp_handoff_recorded",
    "ocs_to_ppp_handoff_returned",
)

AUTHORITY_FLAGS = {
    "authorizes_execution": False,
    "authorizes_dispatch": False,
    "authorizes_worker_invocation": False,
    "authorizes_provider_invocation": False,
    "authorizes_governance_mutation": False,
    "authorizes_replay_mutation": False,
    "authorizes_domain_creation": False,
    "authorizes_human_approval": False,
    "authorizes_automatic_implementation": False,
    "invokes_ppp": False,
}

PROHIBITED_FLAGS = (
    "authority",
    "approval_created",
    "approval_inferred",
    "execution_requested",
    "dispatch_requested",
    "worker_assignment_requested",
    "worker_dispatch_requested",
    "worker_invocation_requested",
    "worker_invoked",
    "provider_invoked",
    "domain_created",
    "governance_modified",
    "replay_modified",
    "automatic_implementation_requested",
)


def create_ocs_to_ppp_handoff(
    *,
    handoff_id: str,
    ocs_context_assembly_artifact: dict[str, Any],
    ocs_cognition_artifact: dict[str, Any],
    ocs_replay_derived_intent_artifact: dict[str, Any],
    ocs_memory_artifact: dict[str, Any],
    ocs_continuity_artifact: dict[str, Any],
    ocs_semantic_resolution_artifact: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Create a replay-visible PPP handoff candidate without invoking PPP."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        context = deepcopy(ocs_context_assembly_artifact)
        cognition = deepcopy(ocs_cognition_artifact)
        intent = deepcopy(ocs_replay_derived_intent_artifact)
        memory = deepcopy(ocs_memory_artifact)
        continuity = deepcopy(ocs_continuity_artifact)
        semantic = deepcopy(ocs_semantic_resolution_artifact)
        _validate_inputs(context, cognition, intent, memory, continuity, semantic)
        packet = _handoff_packet(context, cognition, intent, memory, continuity, semantic)
        handoff = _handoff_artifact(
            handoff_id=handoff_id,
            packet=packet,
            created_at=created_at,
            handoff_status=OCS_TO_PPP_HANDOFF_CANDIDATE_CREATED,
            failure_reason=None,
        )
        returned = _returned_artifact(handoff)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], handoff)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(handoff, returned, replay_path)
    except Exception as exc:
        failure_reason = _failure_reason(exc)
        handoff = _failed_handoff_artifact(
            handoff_id=handoff_id,
            created_at=created_at,
            failure_reason=failure_reason,
        )
        returned = _returned_artifact(handoff)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], handoff)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(handoff, returned, replay_path)


def reconstruct_ocs_to_ppp_handoff_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct OCS-to-PPP handoff evidence deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("OCS-to-PPP handoff replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("OCS-to-PPP handoff replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    recorded = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("handoff_reference") != recorded["handoff_id"]:
        raise FailClosedRuntimeError("OCS-to-PPP handoff returned reference mismatch")
    if returned.get("handoff_artifact_hash") != recorded["artifact_hash"]:
        raise FailClosedRuntimeError("OCS-to-PPP handoff returned artifact hash mismatch")
    if recorded.get("handoff_hash") != _compute_handoff_hash(recorded):
        raise FailClosedRuntimeError("OCS-to-PPP handoff hash mismatch")
    return {
        "handoff_id": recorded["handoff_id"],
        "handoff_status": recorded["handoff_status"],
        "handoff_hash": recorded["handoff_hash"],
        "handoff_candidates": deepcopy(recorded["handoff_candidates"]),
        "candidate_count": recorded["candidate_count"],
        "semantic_continuity_evidence": deepcopy(recorded["semantic_continuity_evidence"]),
        "domain_resolution_evidence": deepcopy(recorded["domain_resolution_evidence"]),
        "clarification_requirements": deepcopy(recorded["clarification_requirements"]),
        "provider_necessity_findings": deepcopy(recorded["provider_necessity_findings"]),
        "worker_candidate_findings": deepcopy(recorded["worker_candidate_findings"]),
        "authority_flags": deepcopy(recorded["authority_flags"]),
        "replay_visible": True,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "automatic_implementation_requested": False,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _validate_inputs(
    context: dict[str, Any],
    cognition: dict[str, Any],
    intent: dict[str, Any],
    memory: dict[str, Any],
    continuity: dict[str, Any],
    semantic: dict[str, Any],
) -> None:
    _validate_artifact(context, OCS_CONTEXT_ASSEMBLY_ARTIFACT_V1, "OCS context")
    _validate_artifact(cognition, OCS_COGNITION_ARTIFACT_V1, "OCS cognition")
    _validate_artifact(intent, OCS_REPLAY_DERIVED_INTENT_ARTIFACT_V1, "OCS replay-derived intent")
    _validate_artifact(memory, OCS_MEMORY_ARTIFACT_V1, "OCS memory")
    _validate_artifact(continuity, OCS_CONTINUITY_ARTIFACT_V1, "OCS continuity")
    _validate_artifact(semantic, OCS_SEMANTIC_RESOLUTION_ARTIFACT_V1, "OCS semantic resolution")
    if context.get("context_status") != OCS_CONTEXT_ASSEMBLED:
        raise FailClosedRuntimeError("OCS-to-PPP handoff failed closed: context is not assembled")
    if cognition.get("cognition_status") != OCS_COGNITION_COMPLETED:
        raise FailClosedRuntimeError("OCS-to-PPP handoff failed closed: cognition is not completed")
    if intent.get("intent_status") != OCS_REPLAY_DERIVED_INTENT_CREATED:
        raise FailClosedRuntimeError("OCS-to-PPP handoff failed closed: replay-derived intent is not created")
    if memory.get("memory_status") != OCS_MEMORY_AND_CONTINUITY_RECORDED:
        raise FailClosedRuntimeError("OCS-to-PPP handoff failed closed: memory is not recorded")
    if continuity.get("continuity_status") != OCS_MEMORY_AND_CONTINUITY_RECORDED:
        raise FailClosedRuntimeError("OCS-to-PPP handoff failed closed: continuity is not recorded")
    if semantic.get("resolution_status") != OCS_SEMANTIC_RESOLUTION_COMPLETED:
        raise FailClosedRuntimeError("OCS-to-PPP handoff failed closed: semantic resolution is not completed")
    if cognition.get("source_context_hash") != context.get("context_hash"):
        raise FailClosedRuntimeError("OCS-to-PPP handoff failed closed: cognition context hash mismatch")
    if intent.get("source_cognition_hash") != cognition.get("cognition_hash"):
        raise FailClosedRuntimeError("OCS-to-PPP handoff failed closed: intent cognition hash mismatch")
    if continuity.get("memory_hash") != memory.get("memory_hash"):
        raise FailClosedRuntimeError("OCS-to-PPP handoff failed closed: memory continuity hash mismatch")
    if semantic.get("source_memory_hash") != memory.get("memory_hash"):
        raise FailClosedRuntimeError("OCS-to-PPP handoff failed closed: semantic memory hash mismatch")
    if semantic.get("source_continuity_hash") != continuity.get("continuity_hash"):
        raise FailClosedRuntimeError("OCS-to-PPP handoff failed closed: semantic continuity hash mismatch")
    if semantic.get("source_cognition_hash") != cognition.get("cognition_hash"):
        raise FailClosedRuntimeError("OCS-to-PPP handoff failed closed: semantic cognition hash mismatch")
    if semantic.get("source_intent_hash") != intent.get("intent_hash"):
        raise FailClosedRuntimeError("OCS-to-PPP handoff failed closed: semantic intent hash mismatch")
    for artifact in (context, cognition, intent, memory, continuity, semantic):
        _reject_prohibited_flags(artifact)


def _validate_artifact(artifact: dict[str, Any], expected_type: str, label: str) -> None:
    if artifact.get("artifact_type") != expected_type:
        raise FailClosedRuntimeError(f"OCS-to-PPP handoff failed closed: invalid {label} artifact")
    if artifact.get("replay_visible") is not True:
        raise FailClosedRuntimeError(f"OCS-to-PPP handoff failed closed: {label} artifact is not replay-visible")
    _verify_artifact_hash(artifact)


def _handoff_packet(
    context: dict[str, Any],
    cognition: dict[str, Any],
    intent: dict[str, Any],
    memory: dict[str, Any],
    continuity: dict[str, Any],
    semantic: dict[str, Any],
) -> dict[str, Any]:
    domain_resolution = deepcopy(semantic.get("domain_identity_resolution", []))
    clarification = _clarification_requirements(cognition, semantic)
    provider = deepcopy(cognition.get("provider_necessity", {}))
    workers = deepcopy(semantic.get("worker_identity_resolution") or cognition.get("worker_candidates", []))
    candidates = _handoff_candidates(intent, semantic, provider, workers, clarification)
    return {
        "source_context_id": context["context_assembly_id"],
        "source_context_hash": context["context_hash"],
        "source_cognition_id": cognition["cognition_id"],
        "source_cognition_hash": cognition["cognition_hash"],
        "source_intent_generation_id": intent["intent_generation_id"],
        "source_intent_hash": intent["intent_hash"],
        "source_memory_id": memory["memory_id"],
        "source_memory_hash": memory["memory_hash"],
        "source_continuity_id": continuity["continuity_id"],
        "source_continuity_hash": continuity["continuity_hash"],
        "source_semantic_resolution_id": semantic["semantic_resolution_id"],
        "source_semantic_hash": semantic["semantic_hash"],
        "handoff_candidates": candidates,
        "semantic_continuity_evidence": {
            "semantic_hash": semantic["semantic_hash"],
            "memory_hash": memory["memory_hash"],
            "continuity_hash": continuity["continuity_hash"],
            "continuity_reference_linking": deepcopy(semantic.get("continuity_reference_linking", [])),
            "authority": False,
        },
        "domain_resolution_evidence": domain_resolution,
        "clarification_requirements": clarification,
        "provider_necessity_findings": provider,
        "worker_candidate_findings": workers,
    }


def _handoff_candidates(
    intent: dict[str, Any],
    semantic: dict[str, Any],
    provider: dict[str, Any],
    workers: list[dict[str, Any]],
    clarification: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    domains = [item["domain_id"] for item in semantic.get("domain_identity_resolution", []) if item.get("resolution_status") == "RESOLVED"]
    candidates = []
    for candidate in intent.get("improvement_candidates", []):
        payload = {
            "candidate_type": candidate.get("candidate_type"),
            "pattern_key": candidate.get("pattern_key"),
            "domains": domains,
            "provider_necessity": provider.get("necessity_classification"),
            "worker_candidates": workers,
            "clarification_required": any(item.get("required") is True for item in clarification),
        }
        candidates.append(
            {
                "candidate_id": replay_hash(payload),
                "candidate_type": candidate.get("candidate_type"),
                "pattern_key": candidate.get("pattern_key"),
                "intent_summary": candidate.get("intent_summary"),
                "target_domains": domains,
                "provider_necessity_classification": provider.get("necessity_classification"),
                "worker_candidate_count": len(workers),
                "clarification_required": payload["clarification_required"],
                "ppp_stage": "PROPOSAL_ONLY_HANDOFF_CANDIDATE",
                "proposal_created": False,
                "ppp_invoked": False,
                "authority": False,
            }
        )
    return sorted(candidates, key=lambda item: (str(item["candidate_type"]), str(item["pattern_key"]), item["candidate_id"]))


def _clarification_requirements(cognition: dict[str, Any], semantic: dict[str, Any]) -> list[dict[str, Any]]:
    items = []
    for item in cognition.get("clarification_requirements", []):
        if item.get("required") is True:
            items.append(
                {
                    "source": "OCS_COGNITION",
                    "requirement_id": item.get("requirement_id"),
                    "reason": item.get("reason"),
                    "required": True,
                    "authority": False,
                }
            )
    for item in semantic.get("clarification_candidates", []):
        items.append(
            {
                "source": "OCS_SEMANTIC_RESOLUTION",
                "requirement_id": item.get("clarification_id"),
                "reason": item.get("reason"),
                "required": item.get("required") is True,
                "authority": False,
            }
        )
    return sorted(items, key=lambda item: (item["source"], str(item["requirement_id"]), str(item["reason"])))


def _handoff_artifact(
    *,
    handoff_id: str,
    packet: dict[str, Any],
    created_at: str,
    handoff_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": OCS_TO_PPP_HANDOFF_ARTIFACT_V1,
        "runtime_version": AIGOL_OCS_TO_PPP_BINDING_RUNTIME_VERSION,
        "handoff_id": _require_string(handoff_id, "handoff_id"),
        **deepcopy(packet),
        "candidate_count": len(packet["handoff_candidates"]),
        "handoff_status": handoff_status,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "authority": False,
        "proposal_only": True,
        "ppp_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "automatic_implementation_requested": False,
        "failure_reason": failure_reason,
    }
    artifact["handoff_hash"] = _compute_handoff_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_handoff_artifact(*, handoff_id: str, created_at: str, failure_reason: str) -> dict[str, Any]:
    packet = {
        "source_context_id": None,
        "source_context_hash": None,
        "source_cognition_id": None,
        "source_cognition_hash": None,
        "source_intent_generation_id": None,
        "source_intent_hash": None,
        "source_memory_id": None,
        "source_memory_hash": None,
        "source_continuity_id": None,
        "source_continuity_hash": None,
        "source_semantic_resolution_id": None,
        "source_semantic_hash": None,
        "handoff_candidates": [],
        "semantic_continuity_evidence": {},
        "domain_resolution_evidence": [],
        "clarification_requirements": [],
        "provider_necessity_findings": {},
        "worker_candidate_findings": [],
    }
    return _handoff_artifact(
        handoff_id=handoff_id,
        packet=packet,
        created_at=created_at,
        handoff_status=FAILED_CLOSED,
        failure_reason=failure_reason,
    )


def _returned_artifact(handoff: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(handoff)
    returned = {
        "event_type": "OCS_TO_PPP_HANDOFF_RETURNED",
        "handoff_reference": handoff["handoff_id"],
        "handoff_artifact_hash": handoff["artifact_hash"],
        "handoff_hash": handoff["handoff_hash"],
        "handoff_status": handoff["handoff_status"],
        "candidate_count": handoff["candidate_count"],
        "replay_visible": True,
        "authority": False,
        "proposal_only": True,
        "ppp_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
        "automatic_implementation_requested": False,
        "failure_reason": handoff["failure_reason"],
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(handoff: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "ocs_to_ppp_handoff_artifact": deepcopy(handoff),
        "ocs_to_ppp_handoff_returned": deepcopy(returned),
        "ocs_to_ppp_handoff_replay_reference": str(replay_path),
        "handoff_status": handoff["handoff_status"],
        "handoff_hash": handoff["handoff_hash"],
        "handoff_candidates": deepcopy(handoff["handoff_candidates"]),
        "candidate_count": handoff["candidate_count"],
        "fail_closed": handoff["handoff_status"] != OCS_TO_PPP_HANDOFF_CANDIDATE_CREATED,
        "failure_reason": handoff["failure_reason"],
        "proposal_only": True,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "automatic_implementation_requested": False,
    }
    capture["ocs_to_ppp_handoff_capture_hash"] = replay_hash(capture)
    return capture


def _compute_handoff_hash(artifact: dict[str, Any]) -> str:
    return replay_hash(
        {
            "source_context_hash": artifact["source_context_hash"],
            "source_cognition_hash": artifact["source_cognition_hash"],
            "source_intent_hash": artifact["source_intent_hash"],
            "source_memory_hash": artifact["source_memory_hash"],
            "source_continuity_hash": artifact["source_continuity_hash"],
            "source_semantic_hash": artifact["source_semantic_hash"],
            "handoff_candidates": artifact["handoff_candidates"],
            "semantic_continuity_evidence": artifact["semantic_continuity_evidence"],
            "domain_resolution_evidence": artifact["domain_resolution_evidence"],
            "clarification_requirements": artifact["clarification_requirements"],
            "provider_necessity_findings": artifact["provider_necessity_findings"],
            "worker_candidate_findings": artifact["worker_candidate_findings"],
            "candidate_count": artifact["candidate_count"],
            "handoff_status": artifact["handoff_status"],
            "authority_flags": artifact["authority_flags"],
            "proposal_only": artifact["proposal_only"],
            "failure_reason": artifact["failure_reason"],
        }
    )


def _reject_prohibited_flags(artifact: dict[str, Any]) -> None:
    for flag in PROHIBITED_FLAGS:
        if artifact.get(flag) is True:
            raise FailClosedRuntimeError(f"OCS-to-PPP handoff failed closed: source carries prohibited flag {flag}")
    flags = artifact.get("authority_flags")
    if isinstance(flags, dict):
        for flag in AUTHORITY_FLAGS:
            if flags.get(flag) is True:
                raise FailClosedRuntimeError(f"OCS-to-PPP handoff failed closed: source carries prohibited authority flag {flag}")


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("OCS-to-PPP handoff replay step ordering mismatch")
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
        raise FailClosedRuntimeError("OCS-to-PPP handoff artifact hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("OCS-to-PPP handoff artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("OCS-to-PPP handoff replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("OCS-to-PPP handoff replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "OCS-to-PPP handoff failed closed"
