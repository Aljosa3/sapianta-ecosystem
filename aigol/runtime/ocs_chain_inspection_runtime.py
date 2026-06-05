"""Read-only OCS chain inspection runtime for AiGOL V1."""

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
from aigol.runtime.ocs_to_ppp_binding_runtime import (
    OCS_TO_PPP_HANDOFF_ARTIFACT_V1,
    OCS_TO_PPP_HANDOFF_CANDIDATE_CREATED,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_OCS_CHAIN_INSPECTION_RUNTIME_VERSION = "AIGOL_OCS_CHAIN_INSPECTION_RUNTIME_V1"
OCS_CHAIN_INSPECTION_ARTIFACT_V1 = "OCS_CHAIN_INSPECTION_ARTIFACT_V1"
OCS_CHAIN_INSPECTION_COMPLETED = "OCS_CHAIN_INSPECTION_COMPLETED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "ocs_chain_inspection_recorded",
    "ocs_chain_inspection_returned",
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
    "ppp_invoked",
)


def inspect_ocs_chain(
    *,
    inspection_id: str,
    ocs_context_assembly_artifact: dict[str, Any],
    ocs_cognition_artifact: dict[str, Any],
    ocs_replay_derived_intent_artifact: dict[str, Any],
    ocs_memory_artifact: dict[str, Any],
    ocs_continuity_artifact: dict[str, Any],
    ocs_semantic_resolution_artifact: dict[str, Any],
    ocs_to_ppp_handoff_artifact: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Inspect a complete OCS chain without invoking downstream authority."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        context = deepcopy(ocs_context_assembly_artifact)
        cognition = deepcopy(ocs_cognition_artifact)
        intent = deepcopy(ocs_replay_derived_intent_artifact)
        memory = deepcopy(ocs_memory_artifact)
        continuity = deepcopy(ocs_continuity_artifact)
        semantic = deepcopy(ocs_semantic_resolution_artifact)
        handoff = deepcopy(ocs_to_ppp_handoff_artifact)
        _validate_chain(context, cognition, intent, memory, continuity, semantic, handoff)
        summary = _inspection_summary(context, cognition, intent, memory, continuity, semantic, handoff)
        inspection = _inspection_artifact(
            inspection_id=inspection_id,
            summary=summary,
            created_at=created_at,
            inspection_status=OCS_CHAIN_INSPECTION_COMPLETED,
            failure_reason=None,
        )
        returned = _returned_artifact(inspection)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], inspection)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(inspection, returned, replay_path)
    except Exception as exc:
        failure_reason = _failure_reason(exc)
        inspection = _failed_inspection_artifact(
            inspection_id=inspection_id,
            created_at=created_at,
            failure_reason=failure_reason,
        )
        returned = _returned_artifact(inspection)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], inspection)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(inspection, returned, replay_path)


def reconstruct_ocs_chain_inspection_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct OCS chain inspection evidence deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("OCS chain inspection replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("OCS chain inspection replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    recorded = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("inspection_reference") != recorded["inspection_id"]:
        raise FailClosedRuntimeError("OCS chain inspection returned reference mismatch")
    if returned.get("inspection_artifact_hash") != recorded["artifact_hash"]:
        raise FailClosedRuntimeError("OCS chain inspection returned artifact hash mismatch")
    if returned.get("inspection_hash") != recorded["inspection_hash"]:
        raise FailClosedRuntimeError("OCS chain inspection returned inspection hash mismatch")
    if recorded.get("inspection_hash") != _compute_inspection_hash(recorded):
        raise FailClosedRuntimeError("OCS chain inspection hash mismatch")
    return {
        "inspection_id": recorded["inspection_id"],
        "inspection_status": recorded["inspection_status"],
        "inspection_hash": recorded["inspection_hash"],
        "chain_stages": deepcopy(recorded["chain_stages"]),
        "continuity_links": deepcopy(recorded["continuity_links"]),
        "semantic_resolution_results": deepcopy(recorded["semantic_resolution_results"]),
        "replay_derived_intent_candidates": deepcopy(recorded["replay_derived_intent_candidates"]),
        "ppp_handoff_candidates": deepcopy(recorded["ppp_handoff_candidates"]),
        "operator_summary": deepcopy(recorded["operator_summary"]),
        "authority_flags": deepcopy(recorded["authority_flags"]),
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "approval_created": False,
        "ppp_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
        "automatic_implementation_requested": False,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _validate_chain(
    context: dict[str, Any],
    cognition: dict[str, Any],
    intent: dict[str, Any],
    memory: dict[str, Any],
    continuity: dict[str, Any],
    semantic: dict[str, Any],
    handoff: dict[str, Any],
) -> None:
    _validate_artifact(context, OCS_CONTEXT_ASSEMBLY_ARTIFACT_V1, "OCS context")
    _validate_artifact(cognition, OCS_COGNITION_ARTIFACT_V1, "OCS cognition")
    _validate_artifact(intent, OCS_REPLAY_DERIVED_INTENT_ARTIFACT_V1, "OCS replay-derived intent")
    _validate_artifact(memory, OCS_MEMORY_ARTIFACT_V1, "OCS memory")
    _validate_artifact(continuity, OCS_CONTINUITY_ARTIFACT_V1, "OCS continuity")
    _validate_artifact(semantic, OCS_SEMANTIC_RESOLUTION_ARTIFACT_V1, "OCS semantic resolution")
    _validate_artifact(handoff, OCS_TO_PPP_HANDOFF_ARTIFACT_V1, "OCS to PPP handoff")
    if context.get("context_status") != OCS_CONTEXT_ASSEMBLED:
        raise FailClosedRuntimeError("OCS chain inspection failed closed: context is not assembled")
    if cognition.get("cognition_status") != OCS_COGNITION_COMPLETED:
        raise FailClosedRuntimeError("OCS chain inspection failed closed: cognition is not completed")
    if intent.get("intent_status") != OCS_REPLAY_DERIVED_INTENT_CREATED:
        raise FailClosedRuntimeError("OCS chain inspection failed closed: replay-derived intent is not created")
    if memory.get("memory_status") != OCS_MEMORY_AND_CONTINUITY_RECORDED:
        raise FailClosedRuntimeError("OCS chain inspection failed closed: memory is not recorded")
    if continuity.get("continuity_status") != OCS_MEMORY_AND_CONTINUITY_RECORDED:
        raise FailClosedRuntimeError("OCS chain inspection failed closed: continuity is not recorded")
    if semantic.get("resolution_status") != OCS_SEMANTIC_RESOLUTION_COMPLETED:
        raise FailClosedRuntimeError("OCS chain inspection failed closed: semantic resolution is not completed")
    if handoff.get("handoff_status") != OCS_TO_PPP_HANDOFF_CANDIDATE_CREATED:
        raise FailClosedRuntimeError("OCS chain inspection failed closed: OCS to PPP handoff is not created")
    if cognition.get("source_context_hash") != context.get("context_hash"):
        raise FailClosedRuntimeError("OCS chain inspection failed closed: cognition context hash mismatch")
    if intent.get("source_cognition_hash") != cognition.get("cognition_hash"):
        raise FailClosedRuntimeError("OCS chain inspection failed closed: intent cognition hash mismatch")
    if continuity.get("memory_hash") != memory.get("memory_hash"):
        raise FailClosedRuntimeError("OCS chain inspection failed closed: memory continuity hash mismatch")
    if semantic.get("source_memory_hash") != memory.get("memory_hash"):
        raise FailClosedRuntimeError("OCS chain inspection failed closed: semantic memory hash mismatch")
    if semantic.get("source_continuity_hash") != continuity.get("continuity_hash"):
        raise FailClosedRuntimeError("OCS chain inspection failed closed: semantic continuity hash mismatch")
    if semantic.get("source_cognition_hash") != cognition.get("cognition_hash"):
        raise FailClosedRuntimeError("OCS chain inspection failed closed: semantic cognition hash mismatch")
    if semantic.get("source_intent_hash") != intent.get("intent_hash"):
        raise FailClosedRuntimeError("OCS chain inspection failed closed: semantic intent hash mismatch")
    if handoff.get("source_context_hash") != context.get("context_hash"):
        raise FailClosedRuntimeError("OCS chain inspection failed closed: handoff context hash mismatch")
    if handoff.get("source_cognition_hash") != cognition.get("cognition_hash"):
        raise FailClosedRuntimeError("OCS chain inspection failed closed: handoff cognition hash mismatch")
    if handoff.get("source_intent_hash") != intent.get("intent_hash"):
        raise FailClosedRuntimeError("OCS chain inspection failed closed: handoff intent hash mismatch")
    if handoff.get("source_memory_hash") != memory.get("memory_hash"):
        raise FailClosedRuntimeError("OCS chain inspection failed closed: handoff memory hash mismatch")
    if handoff.get("source_continuity_hash") != continuity.get("continuity_hash"):
        raise FailClosedRuntimeError("OCS chain inspection failed closed: handoff continuity hash mismatch")
    if handoff.get("source_semantic_hash") != semantic.get("semantic_hash"):
        raise FailClosedRuntimeError("OCS chain inspection failed closed: handoff semantic hash mismatch")
    for artifact in (context, cognition, intent, memory, continuity, semantic, handoff):
        _reject_prohibited_flags(artifact)


def _validate_artifact(artifact: dict[str, Any], expected_type: str, label: str) -> None:
    if artifact.get("artifact_type") != expected_type:
        raise FailClosedRuntimeError(f"OCS chain inspection failed closed: invalid {label} artifact")
    if artifact.get("replay_visible") is not True:
        raise FailClosedRuntimeError(f"OCS chain inspection failed closed: {label} artifact is not replay-visible")
    _verify_artifact_hash(artifact)


def _inspection_summary(
    context: dict[str, Any],
    cognition: dict[str, Any],
    intent: dict[str, Any],
    memory: dict[str, Any],
    continuity: dict[str, Any],
    semantic: dict[str, Any],
    handoff: dict[str, Any],
) -> dict[str, Any]:
    stages = _chain_stages(context, cognition, intent, memory, continuity, semantic, handoff)
    semantic_results = {
        "domain_identity_resolution": deepcopy(semantic.get("domain_identity_resolution", [])),
        "capability_identity_resolution": deepcopy(semantic.get("capability_identity_resolution", [])),
        "worker_identity_resolution": deepcopy(semantic.get("worker_identity_resolution", [])),
        "ambiguity_detection": deepcopy(semantic.get("ambiguity_detection", {})),
        "clarification_candidates": deepcopy(semantic.get("clarification_candidates", [])),
    }
    intent_candidates = _intent_candidates(intent)
    handoff_candidates = _handoff_candidates(handoff)
    return {
        "source_chain_hashes": {
            "context_hash": context["context_hash"],
            "cognition_hash": cognition["cognition_hash"],
            "intent_hash": intent["intent_hash"],
            "memory_hash": memory["memory_hash"],
            "continuity_hash": continuity["continuity_hash"],
            "semantic_hash": semantic["semantic_hash"],
            "handoff_hash": handoff["handoff_hash"],
        },
        "chain_stages": stages,
        "continuity_links": {
            "operation_groups": deepcopy(continuity.get("operation_groups", [])),
            "domain_continuity": deepcopy(continuity.get("domain_continuity", [])),
            "intent_continuity": deepcopy(continuity.get("intent_continuity", [])),
            "context_linkage": deepcopy(continuity.get("context_linkage", [])),
            "semantic_reference_linking": deepcopy(semantic.get("continuity_reference_linking", [])),
        },
        "semantic_resolution_results": semantic_results,
        "replay_derived_intent_candidates": intent_candidates,
        "ppp_handoff_candidates": handoff_candidates,
        "operator_summary": _operator_summary(stages, semantic_results, intent_candidates, handoff_candidates),
    }


def _chain_stages(
    context: dict[str, Any],
    cognition: dict[str, Any],
    intent: dict[str, Any],
    memory: dict[str, Any],
    continuity: dict[str, Any],
    semantic: dict[str, Any],
    handoff: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        _stage(1, "CONTEXT_ASSEMBLY", context, "context_assembly_id", "context_status", "context_hash"),
        _stage(2, "COGNITION", cognition, "cognition_id", "cognition_status", "cognition_hash"),
        _stage(3, "REPLAY_DERIVED_INTENT", intent, "intent_generation_id", "intent_status", "intent_hash"),
        _stage(4, "MEMORY", memory, "memory_id", "memory_status", "memory_hash"),
        _stage(5, "CONTINUITY", continuity, "continuity_id", "continuity_status", "continuity_hash"),
        _stage(6, "SEMANTIC_RESOLUTION", semantic, "semantic_resolution_id", "resolution_status", "semantic_hash"),
        _stage(7, "OCS_TO_PPP_BINDING", handoff, "handoff_id", "handoff_status", "handoff_hash"),
    ]


def _stage(
    order: int,
    stage_name: str,
    artifact: dict[str, Any],
    id_field: str,
    status_field: str,
    hash_field: str,
) -> dict[str, Any]:
    return {
        "stage_order": order,
        "stage_name": stage_name,
        "artifact_id": artifact[id_field],
        "artifact_type": artifact["artifact_type"],
        "status": artifact[status_field],
        "stage_hash": artifact[hash_field],
        "artifact_hash": artifact["artifact_hash"],
        "replay_visible": True,
        "authority": False,
    }


def _intent_candidates(intent: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = []
    for candidate in intent.get("improvement_candidates", []):
        candidates.append(
            {
                "candidate_id": candidate.get("candidate_id"),
                "candidate_type": candidate.get("candidate_type"),
                "pattern_key": candidate.get("pattern_key"),
                "intent_summary": candidate.get("intent_summary"),
                "confidence": candidate.get("confidence"),
                "human_review_required": candidate.get("human_review_required") is True,
                "ppp_eligible": candidate.get("ppp_eligible") is True,
                "proposal_created": False,
                "authority": False,
            }
        )
    return sorted(candidates, key=lambda item: (str(item["candidate_type"]), str(item["pattern_key"]), str(item["candidate_id"])))


def _handoff_candidates(handoff: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = []
    for candidate in handoff.get("handoff_candidates", []):
        item = deepcopy(candidate)
        item["proposal_created"] = False
        item["ppp_invoked"] = False
        item["authority"] = False
        candidates.append(item)
    return sorted(candidates, key=lambda item: (str(item.get("candidate_type")), str(item.get("pattern_key")), str(item.get("candidate_id"))))


def _operator_summary(
    stages: list[dict[str, Any]],
    semantic_results: dict[str, Any],
    intent_candidates: list[dict[str, Any]],
    handoff_candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    ambiguity = semantic_results.get("ambiguity_detection", {})
    return {
        "stage_count": len(stages),
        "all_stages_completed": all(stage["status"] != FAILED_CLOSED for stage in stages),
        "resolved_domain_count": len(semantic_results.get("domain_identity_resolution", [])),
        "resolved_worker_count": len(semantic_results.get("worker_identity_resolution", [])),
        "semantic_ambiguity_detected": ambiguity.get("is_ambiguous") is True,
        "clarification_candidate_count": len(semantic_results.get("clarification_candidates", [])),
        "replay_derived_intent_candidate_count": len(intent_candidates),
        "ppp_handoff_candidate_count": len(handoff_candidates),
        "proposal_only": True,
        "operator_action_available": bool(handoff_candidates),
        "operator_action_required_before_ppp": True,
        "authority": False,
    }


def _inspection_artifact(
    *,
    inspection_id: str,
    summary: dict[str, Any],
    created_at: str,
    inspection_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": OCS_CHAIN_INSPECTION_ARTIFACT_V1,
        "runtime_version": AIGOL_OCS_CHAIN_INSPECTION_RUNTIME_VERSION,
        "inspection_id": _require_string(inspection_id, "inspection_id"),
        **deepcopy(summary),
        "inspection_status": inspection_status,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "authority": False,
        "read_only_inspection": True,
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
    artifact["inspection_hash"] = _compute_inspection_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_inspection_artifact(*, inspection_id: str, created_at: str, failure_reason: str) -> dict[str, Any]:
    summary = {
        "source_chain_hashes": {},
        "chain_stages": [],
        "continuity_links": {},
        "semantic_resolution_results": {},
        "replay_derived_intent_candidates": [],
        "ppp_handoff_candidates": [],
        "operator_summary": {
            "stage_count": 0,
            "all_stages_completed": False,
            "resolved_domain_count": 0,
            "resolved_worker_count": 0,
            "semantic_ambiguity_detected": True,
            "clarification_candidate_count": 1,
            "replay_derived_intent_candidate_count": 0,
            "ppp_handoff_candidate_count": 0,
            "proposal_only": True,
            "operator_action_available": False,
            "operator_action_required_before_ppp": True,
            "authority": False,
        },
    }
    return _inspection_artifact(
        inspection_id=inspection_id,
        summary=summary,
        created_at=created_at,
        inspection_status=FAILED_CLOSED,
        failure_reason=failure_reason,
    )


def _returned_artifact(inspection: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(inspection)
    returned = {
        "event_type": "OCS_CHAIN_INSPECTION_RETURNED",
        "inspection_reference": inspection["inspection_id"],
        "inspection_artifact_hash": inspection["artifact_hash"],
        "inspection_hash": inspection["inspection_hash"],
        "inspection_status": inspection["inspection_status"],
        "stage_count": inspection["operator_summary"]["stage_count"],
        "ppp_handoff_candidate_count": inspection["operator_summary"]["ppp_handoff_candidate_count"],
        "replay_visible": True,
        "authority": False,
        "read_only_inspection": True,
        "proposal_only": True,
        "ppp_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
        "automatic_implementation_requested": False,
        "failure_reason": inspection["failure_reason"],
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(inspection: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "ocs_chain_inspection_artifact": deepcopy(inspection),
        "ocs_chain_inspection_returned": deepcopy(returned),
        "ocs_chain_inspection_replay_reference": str(replay_path),
        "inspection_status": inspection["inspection_status"],
        "inspection_hash": inspection["inspection_hash"],
        "chain_stages": deepcopy(inspection["chain_stages"]),
        "continuity_links": deepcopy(inspection["continuity_links"]),
        "semantic_resolution_results": deepcopy(inspection["semantic_resolution_results"]),
        "replay_derived_intent_candidates": deepcopy(inspection["replay_derived_intent_candidates"]),
        "ppp_handoff_candidates": deepcopy(inspection["ppp_handoff_candidates"]),
        "operator_summary": deepcopy(inspection["operator_summary"]),
        "fail_closed": inspection["inspection_status"] != OCS_CHAIN_INSPECTION_COMPLETED,
        "failure_reason": inspection["failure_reason"],
        "read_only_inspection": True,
        "proposal_only": True,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "approval_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "automatic_implementation_requested": False,
    }
    capture["ocs_chain_inspection_capture_hash"] = replay_hash(capture)
    return capture


def _compute_inspection_hash(artifact: dict[str, Any]) -> str:
    return replay_hash(
        {
            "source_chain_hashes": artifact["source_chain_hashes"],
            "chain_stages": artifact["chain_stages"],
            "continuity_links": artifact["continuity_links"],
            "semantic_resolution_results": artifact["semantic_resolution_results"],
            "replay_derived_intent_candidates": artifact["replay_derived_intent_candidates"],
            "ppp_handoff_candidates": artifact["ppp_handoff_candidates"],
            "operator_summary": artifact["operator_summary"],
            "inspection_status": artifact["inspection_status"],
            "authority_flags": artifact["authority_flags"],
            "read_only_inspection": artifact["read_only_inspection"],
            "proposal_only": artifact["proposal_only"],
            "failure_reason": artifact["failure_reason"],
        }
    )


def _reject_prohibited_flags(artifact: dict[str, Any]) -> None:
    for flag in PROHIBITED_FLAGS:
        if artifact.get(flag) is True:
            raise FailClosedRuntimeError(f"OCS chain inspection failed closed: source carries prohibited flag {flag}")
    flags = artifact.get("authority_flags")
    if isinstance(flags, dict):
        for flag in AUTHORITY_FLAGS:
            if flags.get(flag) is True:
                raise FailClosedRuntimeError(f"OCS chain inspection failed closed: source carries prohibited authority flag {flag}")


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("OCS chain inspection replay step ordering mismatch")
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
        raise FailClosedRuntimeError("OCS chain inspection artifact hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("OCS chain inspection artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("OCS chain inspection replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("OCS chain inspection replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "OCS chain inspection failed closed"
