"""End-to-end bounded OCS orchestration runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.ocs_chain_inspection_runtime import (
    OCS_CHAIN_INSPECTION_COMPLETED,
    inspect_ocs_chain,
)
from aigol.runtime.ocs_clarification_runtime import (
    FAILED_CLOSED as CLARIFICATION_FAILED_CLOSED,
    generate_ocs_clarification,
)
from aigol.runtime.ocs_cognition_runtime import OCS_COGNITION_COMPLETED, run_ocs_cognition
from aigol.runtime.ocs_context_assembly_runtime import OCS_CONTEXT_ASSEMBLED, assemble_ocs_context
from aigol.runtime.ocs_memory_and_continuity_runtime import (
    OCS_MEMORY_AND_CONTINUITY_RECORDED,
    build_ocs_memory_and_continuity,
)
from aigol.runtime.ocs_replay_derived_intent_runtime import (
    OCS_REPLAY_DERIVED_INTENT_CREATED,
    generate_ocs_replay_derived_intent,
)
from aigol.runtime.ocs_semantic_resolution_runtime import OCS_SEMANTIC_RESOLUTION_COMPLETED, resolve_ocs_semantics
from aigol.runtime.ocs_to_ppp_binding_runtime import (
    OCS_TO_PPP_HANDOFF_CANDIDATE_CREATED,
    create_ocs_to_ppp_handoff,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_OCS_END_TO_END_RUNTIME_VERSION = "AIGOL_OCS_END_TO_END_RUNTIME_V1"
OCS_END_TO_END_ARTIFACT_V1 = "OCS_END_TO_END_ARTIFACT_V1"
OCS_END_TO_END_COMPLETED = "OCS_END_TO_END_COMPLETED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "ocs_end_to_end_recorded",
    "ocs_end_to_end_returned",
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


def run_ocs_end_to_end(
    *,
    ocs_run_id: str,
    created_at: str,
    replay_dir: str | Path,
    source_context: dict[str, Any],
    source_chain_id: str | None = None,
    source_request_reference: str | None = None,
    execution_history: list[dict[str, Any]] | None = None,
    validation_history: list[dict[str, Any]] | None = None,
    failure_history: list[dict[str, Any]] | None = None,
    operator_decision_history: list[dict[str, Any]] | None = None,
    domain_registry_context: list[dict[str, Any]] | None = None,
    replay_visible_operation_history: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Run the complete certified OCS chain without downstream activation."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        source = deepcopy(source_context)
        registry = deepcopy(domain_registry_context if domain_registry_context is not None else source.get("registry_context", []))
        operation_history = deepcopy(
            replay_visible_operation_history
            if replay_visible_operation_history is not None
            else source.get("replay_visible_operation_context", [])
        )
        source_hash = _source_input_hash(
            source,
            registry,
            operation_history,
            execution_history or [],
            validation_history or [],
            failure_history or [],
            operator_decision_history or [],
        )
        captures = _execute_stages(
            stage_key=f"OCS-E2E-STAGE-{source_hash[7:19]}",
            created_at=created_at,
            replay_path=replay_path,
            source_context=source,
            source_chain_id=source_chain_id,
            source_request_reference=source_request_reference,
            execution_history=deepcopy(execution_history or []),
            validation_history=deepcopy(validation_history or []),
            failure_history=deepcopy(failure_history or []),
            operator_decision_history=deepcopy(operator_decision_history or []),
            domain_registry_context=registry,
            replay_visible_operation_history=operation_history,
        )
        summary = _end_to_end_summary(
            captures,
            source,
            registry,
            operation_history,
            execution_history or [],
            validation_history or [],
            failure_history or [],
            operator_decision_history or [],
        )
        artifact = _end_to_end_artifact(
            ocs_run_id=ocs_run_id,
            summary=summary,
            created_at=created_at,
            end_to_end_status=OCS_END_TO_END_COMPLETED,
            failure_reason=None,
        )
        returned = _returned_artifact(artifact)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, replay_path)
    except Exception as exc:
        failure_reason = _failure_reason(exc)
        artifact = _failed_end_to_end_artifact(
            ocs_run_id=ocs_run_id,
            created_at=created_at,
            failure_reason=failure_reason,
        )
        returned = _returned_artifact(artifact)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, replay_path)


def reconstruct_ocs_end_to_end_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct OCS end-to-end evidence deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("OCS end-to-end replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("OCS end-to-end replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    recorded = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("ocs_run_reference") != recorded["ocs_run_id"]:
        raise FailClosedRuntimeError("OCS end-to-end returned reference mismatch")
    if returned.get("end_to_end_artifact_hash") != recorded["artifact_hash"]:
        raise FailClosedRuntimeError("OCS end-to-end returned artifact hash mismatch")
    if returned.get("end_to_end_hash") != recorded["end_to_end_hash"]:
        raise FailClosedRuntimeError("OCS end-to-end returned hash mismatch")
    if recorded.get("end_to_end_hash") != _compute_end_to_end_hash(recorded):
        raise FailClosedRuntimeError("OCS end-to-end hash mismatch")
    return {
        "ocs_run_id": recorded["ocs_run_id"],
        "end_to_end_status": recorded["end_to_end_status"],
        "end_to_end_hash": recorded["end_to_end_hash"],
        "stage_references": deepcopy(recorded["stage_references"]),
        "stage_hashes": deepcopy(recorded["stage_hashes"]),
        "clarification_summary": deepcopy(recorded["clarification_summary"]),
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


def _execute_stages(
    *,
    stage_key: str,
    created_at: str,
    replay_path: Path,
    source_context: dict[str, Any],
    source_chain_id: str | None,
    source_request_reference: str | None,
    execution_history: list[dict[str, Any]],
    validation_history: list[dict[str, Any]],
    failure_history: list[dict[str, Any]],
    operator_decision_history: list[dict[str, Any]],
    domain_registry_context: list[dict[str, Any]],
    replay_visible_operation_history: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    context = assemble_ocs_context(
        context_assembly_id=f"{stage_key}-CONTEXT",
        created_at=created_at,
        replay_dir=replay_path / "001_context_assembly",
        source_context=source_context,
        source_chain_id=source_chain_id,
        source_request_reference=source_request_reference,
    )
    _require_status(context, "context_status", OCS_CONTEXT_ASSEMBLED, "context assembly")

    cognition = run_ocs_cognition(
        cognition_id=f"{stage_key}-COGNITION",
        ocs_context_assembly_artifact=context["ocs_context_assembly_artifact"],
        created_at=created_at,
        replay_dir=replay_path / "002_cognition",
    )
    _require_status(cognition, "cognition_status", OCS_COGNITION_COMPLETED, "cognition")

    intent = generate_ocs_replay_derived_intent(
        intent_generation_id=f"{stage_key}-INTENT",
        ocs_cognition_artifact=cognition["ocs_cognition_artifact"],
        created_at=created_at,
        replay_dir=replay_path / "003_replay_derived_intent",
        execution_history=execution_history,
        validation_history=validation_history,
        failure_history=failure_history,
        operator_decision_history=operator_decision_history,
    )
    _require_status(intent, "intent_status", OCS_REPLAY_DERIVED_INTENT_CREATED, "replay-derived intent")

    memory = build_ocs_memory_and_continuity(
        memory_continuity_id=f"{stage_key}-MEMORY",
        created_at=created_at,
        replay_dir=replay_path / "004_memory_continuity",
        ocs_context_artifacts=[context["ocs_context_assembly_artifact"]],
        ocs_cognition_artifacts=[cognition["ocs_cognition_artifact"]],
        replay_derived_intent_artifacts=[intent["ocs_replay_derived_intent_artifact"]],
        domain_registry_context=domain_registry_context,
        replay_visible_operation_history=replay_visible_operation_history,
    )
    _require_status(memory, "memory_status", OCS_MEMORY_AND_CONTINUITY_RECORDED, "memory")
    _require_status(memory, "continuity_status", OCS_MEMORY_AND_CONTINUITY_RECORDED, "continuity")

    semantic = resolve_ocs_semantics(
        semantic_resolution_id=f"{stage_key}-SEMANTIC",
        ocs_memory_artifact=memory["ocs_memory_artifact"],
        ocs_continuity_artifact=memory["ocs_continuity_artifact"],
        ocs_cognition_artifact=cognition["ocs_cognition_artifact"],
        replay_derived_intent_artifact=intent["ocs_replay_derived_intent_artifact"],
        domain_registry_context=domain_registry_context,
        created_at=created_at,
        replay_dir=replay_path / "005_semantic_resolution",
    )
    _require_status(semantic, "resolution_status", OCS_SEMANTIC_RESOLUTION_COMPLETED, "semantic resolution")

    clarification = generate_ocs_clarification(
        clarification_id=f"{stage_key}-CLARIFICATION",
        ocs_cognition_artifact=cognition["ocs_cognition_artifact"],
        ocs_semantic_resolution_artifact=semantic["ocs_semantic_resolution_artifact"],
        created_at=created_at,
        replay_dir=replay_path / "006_clarification",
    )
    if clarification.get("clarification_status") == CLARIFICATION_FAILED_CLOSED:
        raise FailClosedRuntimeError("OCS end-to-end failed closed: clarification failed closed")

    handoff = create_ocs_to_ppp_handoff(
        handoff_id=f"{stage_key}-PPP-HANDOFF",
        ocs_context_assembly_artifact=context["ocs_context_assembly_artifact"],
        ocs_cognition_artifact=cognition["ocs_cognition_artifact"],
        ocs_replay_derived_intent_artifact=intent["ocs_replay_derived_intent_artifact"],
        ocs_memory_artifact=memory["ocs_memory_artifact"],
        ocs_continuity_artifact=memory["ocs_continuity_artifact"],
        ocs_semantic_resolution_artifact=semantic["ocs_semantic_resolution_artifact"],
        created_at=created_at,
        replay_dir=replay_path / "007_ocs_to_ppp_handoff",
    )
    _require_status(handoff, "handoff_status", OCS_TO_PPP_HANDOFF_CANDIDATE_CREATED, "OCS to PPP binding")

    inspection = inspect_ocs_chain(
        inspection_id=f"{stage_key}-INSPECTION",
        ocs_context_assembly_artifact=context["ocs_context_assembly_artifact"],
        ocs_cognition_artifact=cognition["ocs_cognition_artifact"],
        ocs_replay_derived_intent_artifact=intent["ocs_replay_derived_intent_artifact"],
        ocs_memory_artifact=memory["ocs_memory_artifact"],
        ocs_continuity_artifact=memory["ocs_continuity_artifact"],
        ocs_semantic_resolution_artifact=semantic["ocs_semantic_resolution_artifact"],
        ocs_to_ppp_handoff_artifact=handoff["ocs_to_ppp_handoff_artifact"],
        created_at=created_at,
        replay_dir=replay_path / "008_chain_inspection",
    )
    _require_status(inspection, "inspection_status", OCS_CHAIN_INSPECTION_COMPLETED, "chain inspection")

    return {
        "context": context,
        "cognition": cognition,
        "intent": intent,
        "memory": memory,
        "semantic": semantic,
        "clarification": clarification,
        "handoff": handoff,
        "inspection": inspection,
    }


def _end_to_end_summary(
    captures: dict[str, dict[str, Any]],
    source_context: dict[str, Any],
    domain_registry_context: list[dict[str, Any]],
    replay_visible_operation_history: list[dict[str, Any]],
    execution_history: list[dict[str, Any]],
    validation_history: list[dict[str, Any]],
    failure_history: list[dict[str, Any]],
    operator_decision_history: list[dict[str, Any]],
) -> dict[str, Any]:
    context_artifact = captures["context"]["ocs_context_assembly_artifact"]
    cognition_artifact = captures["cognition"]["ocs_cognition_artifact"]
    intent_artifact = captures["intent"]["ocs_replay_derived_intent_artifact"]
    memory_artifact = captures["memory"]["ocs_memory_artifact"]
    continuity_artifact = captures["memory"]["ocs_continuity_artifact"]
    semantic_artifact = captures["semantic"]["ocs_semantic_resolution_artifact"]
    clarification_artifact = captures["clarification"]["ocs_clarification_artifact"]
    handoff_artifact = captures["handoff"]["ocs_to_ppp_handoff_artifact"]
    inspection_artifact = captures["inspection"]["ocs_chain_inspection_artifact"]
    stage_hashes = {
        "context_hash": context_artifact["context_hash"],
        "cognition_hash": cognition_artifact["cognition_hash"],
        "intent_hash": intent_artifact["intent_hash"],
        "memory_hash": memory_artifact["memory_hash"],
        "continuity_hash": continuity_artifact["continuity_hash"],
        "semantic_hash": semantic_artifact["semantic_hash"],
        "clarification_hash": clarification_artifact["clarification_hash"],
        "handoff_hash": handoff_artifact["handoff_hash"],
        "inspection_hash": inspection_artifact["inspection_hash"],
    }
    return {
        "source_input_hash": _source_input_hash(
            source_context,
            domain_registry_context,
            replay_visible_operation_history,
            execution_history,
            validation_history,
            failure_history,
            operator_decision_history,
        ),
        "stage_references": [
            _stage_reference(1, "CONTEXT_ASSEMBLY", context_artifact, "context_assembly_id", "context_status", "context_hash"),
            _stage_reference(2, "COGNITION", cognition_artifact, "cognition_id", "cognition_status", "cognition_hash"),
            _stage_reference(3, "REPLAY_DERIVED_INTENT", intent_artifact, "intent_generation_id", "intent_status", "intent_hash"),
            _stage_reference(4, "MEMORY", memory_artifact, "memory_id", "memory_status", "memory_hash"),
            _stage_reference(5, "CONTINUITY", continuity_artifact, "continuity_id", "continuity_status", "continuity_hash"),
            _stage_reference(6, "SEMANTIC_RESOLUTION", semantic_artifact, "semantic_resolution_id", "resolution_status", "semantic_hash"),
            _stage_reference(7, "CLARIFICATION", clarification_artifact, "clarification_id", "clarification_status", "clarification_hash"),
            _stage_reference(8, "OCS_TO_PPP_BINDING", handoff_artifact, "handoff_id", "handoff_status", "handoff_hash"),
            _stage_reference(9, "CHAIN_INSPECTION", inspection_artifact, "inspection_id", "inspection_status", "inspection_hash"),
        ],
        "stage_hashes": stage_hashes,
        "clarification_summary": {
            "clarification_status": clarification_artifact["clarification_status"],
            "clarification_required": clarification_artifact["clarification_required"],
            "clarification_request_count": len(clarification_artifact["clarification_requests"]),
            "clarification_hash": clarification_artifact["clarification_hash"],
            "authority": False,
        },
        "operator_summary": {
            **deepcopy(inspection_artifact["operator_summary"]),
            "clarification_status": clarification_artifact["clarification_status"],
            "clarification_required": clarification_artifact["clarification_required"],
            "end_to_end_stage_count": 9,
            "authority": False,
        },
    }


def _stage_reference(
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


def _source_input_hash(
    source_context: dict[str, Any],
    domain_registry_context: list[dict[str, Any]],
    replay_visible_operation_history: list[dict[str, Any]],
    execution_history: list[dict[str, Any]],
    validation_history: list[dict[str, Any]],
    failure_history: list[dict[str, Any]],
    operator_decision_history: list[dict[str, Any]],
) -> str:
    return replay_hash(
        {
            "source_context": source_context,
            "domain_registry_context": domain_registry_context,
            "replay_visible_operation_history": replay_visible_operation_history,
            "execution_history": execution_history,
            "validation_history": validation_history,
            "failure_history": failure_history,
            "operator_decision_history": operator_decision_history,
        }
    )


def _end_to_end_artifact(
    *,
    ocs_run_id: str,
    summary: dict[str, Any],
    created_at: str,
    end_to_end_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": OCS_END_TO_END_ARTIFACT_V1,
        "runtime_version": AIGOL_OCS_END_TO_END_RUNTIME_VERSION,
        "ocs_run_id": _require_string(ocs_run_id, "ocs_run_id"),
        **deepcopy(summary),
        "end_to_end_status": end_to_end_status,
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
    artifact["end_to_end_hash"] = _compute_end_to_end_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_end_to_end_artifact(*, ocs_run_id: str, created_at: str, failure_reason: str) -> dict[str, Any]:
    return _end_to_end_artifact(
        ocs_run_id=ocs_run_id,
        summary={
            "source_input_hash": None,
            "stage_references": [],
            "stage_hashes": {},
            "clarification_summary": {
                "clarification_status": FAILED_CLOSED,
                "clarification_required": True,
                "clarification_request_count": 0,
                "clarification_hash": None,
                "authority": False,
            },
            "operator_summary": {
                "all_stages_completed": False,
                "end_to_end_stage_count": 0,
                "operator_action_available": False,
                "operator_action_required_before_ppp": True,
                "proposal_only": True,
                "authority": False,
            },
        },
        created_at=created_at,
        end_to_end_status=FAILED_CLOSED,
        failure_reason=failure_reason,
    )


def _returned_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(artifact)
    returned = {
        "event_type": "OCS_END_TO_END_RETURNED",
        "ocs_run_reference": artifact["ocs_run_id"],
        "end_to_end_artifact_hash": artifact["artifact_hash"],
        "end_to_end_hash": artifact["end_to_end_hash"],
        "end_to_end_status": artifact["end_to_end_status"],
        "stage_count": len(artifact["stage_references"]),
        "replay_visible": True,
        "authority": False,
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
        "failure_reason": artifact["failure_reason"],
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(artifact: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "ocs_end_to_end_artifact": deepcopy(artifact),
        "ocs_end_to_end_returned": deepcopy(returned),
        "ocs_end_to_end_replay_reference": str(replay_path),
        "end_to_end_status": artifact["end_to_end_status"],
        "end_to_end_hash": artifact["end_to_end_hash"],
        "stage_references": deepcopy(artifact["stage_references"]),
        "stage_hashes": deepcopy(artifact["stage_hashes"]),
        "clarification_summary": deepcopy(artifact["clarification_summary"]),
        "operator_summary": deepcopy(artifact["operator_summary"]),
        "fail_closed": artifact["end_to_end_status"] != OCS_END_TO_END_COMPLETED,
        "failure_reason": artifact["failure_reason"],
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
    capture["ocs_end_to_end_capture_hash"] = replay_hash(capture)
    return capture


def _compute_end_to_end_hash(artifact: dict[str, Any]) -> str:
    return replay_hash(
        {
            "source_input_hash": artifact["source_input_hash"],
            "stage_references": _stable_stage_references(artifact["stage_references"]),
            "stage_hash_keys": sorted(artifact["stage_hashes"]),
            "clarification_summary": _stable_clarification_summary(artifact["clarification_summary"]),
            "operator_summary": artifact["operator_summary"],
            "end_to_end_status": artifact["end_to_end_status"],
            "authority_flags": artifact["authority_flags"],
            "proposal_only": artifact["proposal_only"],
            "failure_reason": artifact["failure_reason"],
        }
    )


def _stable_stage_references(stage_references: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "stage_order": item["stage_order"],
            "stage_name": item["stage_name"],
            "artifact_type": item["artifact_type"],
            "status": item["status"],
            "replay_visible": item["replay_visible"],
            "authority": item["authority"],
        }
        for item in stage_references
    ]


def _stable_clarification_summary(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "clarification_status": summary["clarification_status"],
        "clarification_required": summary["clarification_required"],
        "clarification_request_count": summary["clarification_request_count"],
        "authority": summary["authority"],
    }


def _require_status(capture: dict[str, Any], status_field: str, expected: str, label: str) -> None:
    if capture.get(status_field) != expected:
        reason = capture.get("failure_reason") or f"{label} did not complete"
        raise FailClosedRuntimeError(f"OCS end-to-end failed closed: {reason}")


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("OCS end-to-end replay step ordering mismatch")
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
        raise FailClosedRuntimeError("OCS end-to-end artifact hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("OCS end-to-end artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("OCS end-to-end replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("OCS end-to-end replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "OCS end-to-end failed closed"
