"""Bind approved durable governed work to existing non-executing Worker payloads."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.governed_implementation_request_runtime import (
    APPROVED,
    HUMAN_APPROVAL_ARTIFACT_V1,
    IMPLEMENTATION_REQUEST_CREATED,
    create_governed_implementation_request,
    reconstruct_governed_implementation_request_replay,
)
from aigol.runtime.implementation_request_to_worker_request_bridge_runtime import (
    WORKER_REQUEST_CREATED,
    bridge_implementation_request_to_worker_request,
    reconstruct_implementation_request_to_worker_request_bridge_replay,
)
from aigol.runtime.improvement_intent_to_ppp_bridge_runtime import (
    PPP_CANDIDATE_ARTIFACT_V1,
    PPP_CANDIDATE_CREATED,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_implementation_turn_durable_work_binding import (
    IMPLEMENTATION_TURN_APPROVED_IDENTITIES_CONSUMED,
    reconstruct_implementation_turn_approval_consumption,
    reconstruct_implementation_turn_durable_work_binding,
    validate_implementation_turn_approval_consumption,
    validate_implementation_turn_durable_work_binding,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


APPROVED_DURABLE_WORK_WORKER_PAYLOAD_BINDING_VERSION = (
    "G31_05_APPROVED_DURABLE_WORK_WORKER_PAYLOAD_BINDING_V1"
)
APPROVED_DURABLE_WORK_WORKER_PAYLOAD_BINDING_ARTIFACT_V1 = (
    "APPROVED_DURABLE_WORK_WORKER_PAYLOAD_BINDING_ARTIFACT_V1"
)
APPROVED_DURABLE_WORK_PPP_TASK_PACKAGE_SOURCE = "APPROVED_DURABLE_GOVERNED_WORK"
APPROVED_DURABLE_WORK_PPP_CERTIFICATION_STATUS = (
    "CERTIFIED_APPROVED_DURABLE_GOVERNED_WORK_ACCEPTED"
)
WORKER_PAYLOAD_BOUND = "APPROVED_DURABLE_WORK_WORKER_PAYLOAD_BOUND"
WORKER_PAYLOAD_SCOPE_UNRESOLVED_FAILED_CLOSED = (
    "APPROVED_DURABLE_WORK_WORKER_PAYLOAD_SCOPE_UNRESOLVED_FAILED_CLOSED"
)

REPLAY_STEPS = (
    "approved_durable_work_ppp_task_package_recorded",
    "approved_durable_work_worker_payload_binding_recorded",
)

FALSE_BOUNDARIES = {
    "execution_authorized": False,
    "provider_invoked": False,
    "worker_invoked": False,
    "worker_assigned": False,
    "worker_dispatched": False,
    "repository_mutated": False,
    "validation_executed": False,
    "certification_reached": False,
    "human_interface_authority": False,
    "human_interface_semantic_authority": False,
    "human_interface_planning_authority": False,
    "human_interface_provider_authority": False,
    "human_interface_worker_authority": False,
    "human_interface_mutation_authority": False,
    "human_interface_approval_authority": False,
    "human_interface_authorization_authority": False,
    "human_interface_replay_authority": False,
}


def bind_approved_durable_work_to_worker_payload(
    *,
    implementation_turn_binding: dict[str, Any],
    approval_consumption_artifact: dict[str, Any],
    requested_by: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Project approved work through the existing PPP/request payload contracts."""

    binding = validate_implementation_turn_durable_work_binding(
        implementation_turn_binding,
        require_ready=True,
    )
    consumption = validate_implementation_turn_approval_consumption(
        approval_consumption_artifact
    )
    _validate_approval_continuity(binding=binding, consumption=consumption)
    root = Path(replay_dir)
    _ensure_replay_available(root)
    payload_scope = _implementation_scope(binding=binding, consumption=consumption)
    ppp_candidate = _ppp_task_package(
        binding=binding,
        consumption=consumption,
        payload_scope=payload_scope,
        created_at=created_at,
    )
    _persist_step(root, 0, REPLAY_STEPS[0], ppp_candidate)
    approval = _implementation_request_approval(
        ppp_candidate=ppp_candidate,
        binding=binding,
        consumption=consumption,
        created_at=created_at,
    )
    implementation_capture = create_governed_implementation_request(
        request_id=f"{binding['durable_governed_work_id']}:IMPLEMENTATION-REQUEST",
        ppp_candidate_artifact=ppp_candidate,
        human_approval_artifact=approval,
        requested_by=_require_string(requested_by, "requested_by"),
        created_at=_require_string(created_at, "created_at"),
        replay_dir=root / "governed_implementation_request",
        implementation_scope=payload_scope,
    )
    if implementation_capture.get("request_status") != IMPLEMENTATION_REQUEST_CREATED:
        raise FailClosedRuntimeError(
            implementation_capture.get("failure_reason")
            or "approved durable work implementation request failed closed"
        )
    implementation_request = implementation_capture["implementation_request_artifact"]
    worker_capture = bridge_implementation_request_to_worker_request(
        bridge_id=f"{binding['durable_governed_work_id']}:WORKER-PAYLOAD",
        implementation_request_artifact=implementation_request,
        requested_by=_require_string(requested_by, "requested_by"),
        created_at=_require_string(created_at, "created_at"),
        replay_dir=root / "worker_request_payload",
    )
    if worker_capture.get("request_status") != WORKER_REQUEST_CREATED:
        raise FailClosedRuntimeError(
            worker_capture.get("failure_reason")
            or "approved durable work Worker payload failed closed"
        )
    worker_payload = worker_capture["worker_request_artifact"]
    unresolved = _repository_scope_unresolved(payload_scope)
    status = (
        WORKER_PAYLOAD_SCOPE_UNRESOLVED_FAILED_CLOSED
        if unresolved
        else WORKER_PAYLOAD_BOUND
    )
    failure_reason = (
        "repository scope remains unresolved; Worker dispatch is prohibited"
        if unresolved
        else None
    )
    artifact = {
        "artifact_type": APPROVED_DURABLE_WORK_WORKER_PAYLOAD_BINDING_ARTIFACT_V1,
        "runtime_version": APPROVED_DURABLE_WORK_WORKER_PAYLOAD_BINDING_VERSION,
        "binding_status": status,
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": str(root),
        "source_implementation_turn_binding": binding["artifact_type"],
        "source_implementation_turn_binding_hash": binding["artifact_hash"],
        "source_approval_consumption": consumption["artifact_type"],
        "source_approval_consumption_hash": consumption["artifact_hash"],
        "source_development_composition_plan_hash": binding[
            "development_composition_plan_hash"
        ],
        "source_durable_governed_work_id": binding["durable_governed_work_id"],
        "source_durable_governed_work_hash": binding["durable_governed_work_hash"],
        "source_proposal_preview_hash": binding["proposal_preview_hash"],
        "source_approval_request_hash": binding["approval_request_hash"],
        "ppp_task_package_artifact": deepcopy(ppp_candidate),
        "ppp_task_package_hash": ppp_candidate["artifact_hash"],
        "implementation_request_artifact": deepcopy(implementation_request),
        "implementation_request_hash": implementation_request["artifact_hash"],
        "worker_implementation_payload_artifact": deepcopy(worker_payload),
        "worker_implementation_payload_hash": worker_payload["artifact_hash"],
        "payload_field_lineage": deepcopy(payload_scope["field_lineage"]),
        "repository_scope_status": payload_scope["repository_scope_status"],
        "repository_targets": deepcopy(payload_scope["repository_targets"]),
        "repository_scope_unresolved": unresolved,
        "generic_marker_fallback_used": False,
        "generic_worker_foundation_payload_used": False,
        "approved_work_reclassified": False,
        "replacement_project_objective_created": False,
        "replacement_plan_created": False,
        "replacement_proposal_created": False,
        "payload_composed": True,
        "task_package_accepted": True,
        "ready_for_separate_dispatch_governance": (
            worker_payload.get("ready_for_worker_dispatch_governance") is True
            and not unresolved
        ),
        "dispatch_blocked": unresolved,
        "approval_is_execution_authorization": False,
        "fail_closed": unresolved,
        "failure_reason": failure_reason,
        "replay_visible": True,
        **FALSE_BOUNDARIES,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    validate_approved_durable_work_worker_payload_binding(artifact)
    _persist_step(root, 1, REPLAY_STEPS[1], artifact)
    return deepcopy(artifact)


def validate_approved_durable_work_worker_payload_binding(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("approved durable work Worker payload binding must be a dict")
    candidate = deepcopy(artifact)
    if candidate.get("artifact_type") != (
        APPROVED_DURABLE_WORK_WORKER_PAYLOAD_BINDING_ARTIFACT_V1
    ):
        raise FailClosedRuntimeError("approved durable work Worker payload binding type is invalid")
    if candidate.get("runtime_version") != APPROVED_DURABLE_WORK_WORKER_PAYLOAD_BINDING_VERSION:
        raise FailClosedRuntimeError("approved durable work Worker payload binding version is invalid")
    if candidate.get("binding_status") not in {
        WORKER_PAYLOAD_BOUND,
        WORKER_PAYLOAD_SCOPE_UNRESOLVED_FAILED_CLOSED,
    }:
        raise FailClosedRuntimeError("approved durable work Worker payload status is invalid")
    ppp_candidate = _validate_ppp_task_package(candidate.get("ppp_task_package_artifact"))
    implementation_request = _validate_hash(candidate.get("implementation_request_artifact"), "implementation request")
    worker_payload = _validate_hash(candidate.get("worker_implementation_payload_artifact"), "Worker payload")
    expected = {
        "ppp_task_package_hash": ppp_candidate["artifact_hash"],
        "implementation_request_hash": implementation_request["artifact_hash"],
        "worker_implementation_payload_hash": worker_payload["artifact_hash"],
        "source_implementation_turn_binding_hash": ppp_candidate[
            "source_approved_work_lineage"
        ]["implementation_turn_binding_hash"],
        "source_approval_consumption_hash": ppp_candidate[
            "source_approved_work_lineage"
        ]["approval_consumption_hash"],
        "source_development_composition_plan_hash": ppp_candidate[
            "source_approved_work_lineage"
        ]["development_composition_plan_hash"],
        "source_durable_governed_work_id": ppp_candidate[
            "source_approved_work_lineage"
        ]["durable_governed_work_id"],
        "source_durable_governed_work_hash": ppp_candidate[
            "source_approved_work_lineage"
        ]["durable_governed_work_hash"],
        "source_proposal_preview_hash": ppp_candidate[
            "source_approved_work_lineage"
        ]["proposal_preview_hash"],
        "source_approval_request_hash": ppp_candidate[
            "source_approved_work_lineage"
        ]["approval_request_hash"],
    }
    for field, value in expected.items():
        if candidate.get(field) != value:
            raise FailClosedRuntimeError(
                f"approved durable work Worker payload identity mismatch: {field}"
            )
    lineage = ppp_candidate["source_approved_work_lineage"]
    if implementation_request.get("canonical_approved_work_lineage") != lineage:
        raise FailClosedRuntimeError("implementation request approved-work lineage mismatch")
    if worker_payload.get("canonical_approved_work_lineage") != lineage:
        raise FailClosedRuntimeError("Worker payload approved-work lineage mismatch")
    if (
        implementation_request.get("source_ppp_candidate")
        != ppp_candidate.get("ppp_candidate_id")
        or implementation_request.get("source_ppp_candidate_hash")
        != ppp_candidate.get("artifact_hash")
    ):
        raise FailClosedRuntimeError("implementation request PPP task-package mismatch")
    if (
        worker_payload.get("source_implementation_request")
        != implementation_request.get("implementation_request_id")
        or worker_payload.get("source_implementation_request_hash")
        != implementation_request.get("artifact_hash")
    ):
        raise FailClosedRuntimeError("Worker payload implementation-request mismatch")
    if (
        worker_payload.get("source_ppp_candidate")
        != ppp_candidate.get("ppp_candidate_id")
        or worker_payload.get("source_ppp_candidate_hash")
        != ppp_candidate.get("artifact_hash")
    ):
        raise FailClosedRuntimeError("Worker payload PPP task-package mismatch")
    scope = implementation_request.get("implementation_scope")
    if not isinstance(scope, dict) or worker_payload.get("implementation_scope") != scope:
        raise FailClosedRuntimeError("Worker payload implementation scope mismatch")
    if ppp_candidate.get("approved_implementation_scope") != scope:
        raise FailClosedRuntimeError("PPP task package implementation scope mismatch")
    if ppp_candidate.get("approved_implementation_scope_hash") != replay_hash(scope):
        raise FailClosedRuntimeError("PPP task package implementation scope hash mismatch")
    if implementation_request.get("implementation_objective") != ppp_candidate.get(
        "proposal_summary"
    ):
        raise FailClosedRuntimeError("implementation request objective mismatch")
    if worker_payload.get("worker_objective") != implementation_request.get(
        "implementation_objective"
    ):
        raise FailClosedRuntimeError("Worker payload objective mismatch")
    if worker_payload.get("worker_payload_field_lineage") != scope.get(
        "field_lineage"
    ):
        raise FailClosedRuntimeError("Worker payload projected lineage mismatch")
    if candidate.get("payload_field_lineage") != scope.get("field_lineage"):
        raise FailClosedRuntimeError("Worker payload field lineage mismatch")
    if candidate.get("repository_scope_status") != scope.get("repository_scope_status"):
        raise FailClosedRuntimeError("Worker payload repository scope mismatch")
    if candidate.get("repository_targets") != scope.get("repository_targets"):
        raise FailClosedRuntimeError("Worker payload repository targets mismatch")
    unresolved = _repository_scope_unresolved(scope)
    if candidate.get("repository_scope_unresolved") is not unresolved:
        raise FailClosedRuntimeError("Worker payload repository scope state mismatch")
    if candidate.get("dispatch_blocked") is not unresolved:
        raise FailClosedRuntimeError("Worker payload dispatch boundary mismatch")
    if candidate.get("fail_closed") is not unresolved:
        raise FailClosedRuntimeError("Worker payload fail-closed state mismatch")
    if unresolved and candidate.get("binding_status") != WORKER_PAYLOAD_SCOPE_UNRESOLVED_FAILED_CLOSED:
        raise FailClosedRuntimeError("unresolved Worker payload must fail closed")
    if unresolved and worker_payload.get("ready_for_worker_dispatch_governance") is not False:
        raise FailClosedRuntimeError("unresolved Worker payload cannot be dispatch ready")
    if (
        not unresolved
        and worker_payload.get("ready_for_worker_dispatch_governance") is not True
    ):
        raise FailClosedRuntimeError("grounded Worker payload readiness mismatch")
    for field, expected_value in FALSE_BOUNDARIES.items():
        if candidate.get(field) is not expected_value:
            raise FailClosedRuntimeError(
                f"approved durable work Worker payload boundary invalid: {field}"
            )
    for field in (
        "generic_marker_fallback_used",
        "generic_worker_foundation_payload_used",
        "approved_work_reclassified",
        "replacement_project_objective_created",
        "replacement_plan_created",
        "replacement_proposal_created",
    ):
        if candidate.get(field) is not False:
            raise FailClosedRuntimeError(f"approved durable work substitution detected: {field}")
    body = deepcopy(candidate)
    actual_hash = body.pop("artifact_hash", None)
    if replay_hash(body) != actual_hash:
        raise FailClosedRuntimeError("approved durable work Worker payload binding hash mismatch")
    return candidate


def reconstruct_approved_durable_work_worker_payload_binding(
    replay_dir: str | Path,
) -> dict[str, Any]:
    root = Path(replay_dir)
    wrappers = [
        load_json(root / f"{index:03d}_{step}.json")
        for index, step in enumerate(REPLAY_STEPS)
    ]
    for index, (step, wrapper) in enumerate(zip(REPLAY_STEPS, wrappers)):
        _validate_wrapper(wrapper, index=index, step=step)
    ppp_candidate = _validate_ppp_task_package(wrappers[0]["artifact"])
    binding = validate_approved_durable_work_worker_payload_binding(
        wrappers[1]["artifact"]
    )
    if binding["ppp_task_package_hash"] != ppp_candidate["artifact_hash"]:
        raise FailClosedRuntimeError("approved durable work PPP Replay lineage mismatch")
    reconstruct_governed_implementation_request_replay(
        root / "governed_implementation_request"
    )
    reconstruct_implementation_request_to_worker_request_bridge_replay(
        root / "worker_request_payload"
    )
    implementation_wrapper = load_json(
        root / "governed_implementation_request" / "000_implementation_request_recorded.json"
    )
    worker_wrapper = load_json(
        root / "worker_request_payload" / "000_worker_request_recorded.json"
    )
    if implementation_wrapper["artifact"]["artifact_hash"] != binding[
        "implementation_request_hash"
    ]:
        raise FailClosedRuntimeError("approved durable work implementation request Replay mismatch")
    if worker_wrapper["artifact"]["artifact_hash"] != binding[
        "worker_implementation_payload_hash"
    ]:
        raise FailClosedRuntimeError("approved durable work Worker payload Replay mismatch")
    source_binding = reconstruct_implementation_turn_durable_work_binding(
        ppp_candidate["source_replay_references"][0]
    )
    source_consumption = reconstruct_implementation_turn_approval_consumption(
        ppp_candidate["source_replay_references"][0]
    )
    if source_binding["artifact_hash"] != binding[
        "source_implementation_turn_binding_hash"
    ]:
        raise FailClosedRuntimeError("approved durable work source binding Replay mismatch")
    if source_consumption["artifact_hash"] != binding[
        "source_approval_consumption_hash"
    ]:
        raise FailClosedRuntimeError("approved durable work approval Replay mismatch")
    return binding


def render_approved_durable_work_worker_payload_binding(
    artifact: dict[str, Any],
) -> str:
    binding = validate_approved_durable_work_worker_payload_binding(artifact)
    return "\n".join(
        [
            "Approved durable governed work Worker payload",
            f"binding_status: {binding['binding_status']}",
            f"durable_governed_work_id: {binding['source_durable_governed_work_id']}",
            f"development_composition_plan_hash: {binding['source_development_composition_plan_hash']}",
            f"durable_governed_work_hash: {binding['source_durable_governed_work_hash']}",
            f"proposal_preview_hash: {binding['source_proposal_preview_hash']}",
            f"approval_request_hash: {binding['source_approval_request_hash']}",
            f"approval_consumption_hash: {binding['source_approval_consumption_hash']}",
            f"ppp_task_package_hash: {binding['ppp_task_package_hash']}",
            f"implementation_request_hash: {binding['implementation_request_hash']}",
            f"worker_implementation_payload_hash: {binding['worker_implementation_payload_hash']}",
            f"repository_scope_status: {binding['repository_scope_status']}",
            f"repository_targets: {binding['repository_targets']}",
            f"dispatch_blocked: {binding['dispatch_blocked']}",
            f"approval_is_execution_authorization: {binding['approval_is_execution_authorization']}",
            f"provider_invoked: {binding['provider_invoked']}",
            f"worker_invoked: {binding['worker_invoked']}",
            f"repository_mutated: {binding['repository_mutated']}",
            f"failure_reason: {binding['failure_reason']}",
            f"replay_reference: {binding['replay_reference']}",
        ]
    )


def _implementation_scope(
    *, binding: dict[str, Any], consumption: dict[str, Any]
) -> dict[str, Any]:
    objective = binding["project_objective_artifact"]
    coverage = binding["capability_composition_coverage_artifact"]
    plan = binding["development_composition_plan_artifact"]
    durable = binding["durable_governed_work_artifact"]
    preview = binding["proposal_preview_artifact"]
    repository_targets = deepcopy(preview.get("proposed_repository_paths") or [])
    scope = {
        "objective": objective["canonical_project_objective"],
        "original_human_goal": binding["original_request"],
        "original_human_goal_hash": binding["original_request_hash"],
        "canonical_project_objective": objective["canonical_project_objective"],
        "project_objective_hash": binding["project_objective_hash"],
        "platform_knowledge_identity": binding["platform_knowledge_artifact"]["artifact_type"],
        "platform_knowledge_hash": binding["platform_knowledge_hash"],
        "knowledge_reuse_identity": "KNOWLEDGE_REUSE_EVIDENCE_SNAPSHOT",
        "knowledge_reuse_hash": binding["knowledge_reuse_hash"],
        "capability_composition_coverage_identity": coverage["artifact_type"],
        "capability_composition_coverage_hash": binding[
            "capability_composition_coverage_hash"
        ],
        "development_composition_plan_identity": plan["artifact_type"],
        "development_composition_plan_hash": binding[
            "development_composition_plan_hash"
        ],
        "durable_governed_work_id": binding["durable_governed_work_id"],
        "durable_governed_work_hash": binding["durable_governed_work_hash"],
        "proposal_preview_identity": preview["artifact_type"],
        "proposal_preview_hash": binding["proposal_preview_hash"],
        "approval_request_identity": binding["approval_request_id"],
        "approval_request_hash": binding["approval_request_hash"],
        "approval_consumption_identity": consumption["artifact_type"],
        "approval_consumption_hash": consumption["artifact_hash"],
        "bounded_work_scope": deepcopy(plan.get("minimal_required_platform_extension") or {}),
        "residual_implementation_gaps": deepcopy(plan.get("residual_capability_gaps") or []),
        "ordered_implementation_sequence": deepcopy(plan.get("ordered_implementation_sequence") or []),
        "repository_scope_status": preview["repository_scope_status"],
        "repository_targets": repository_targets,
        "focused_test_requirements": deepcopy(preview.get("focused_tests") or []),
        "validation_requirements": deepcopy(durable.get("validation_requirements") or []),
        "governance_requirements": deepcopy(durable.get("governance_dependencies") or []),
        "replay_requirements": deepcopy(durable.get("replay_dependencies") or []),
        "certification_requirements": deepcopy(durable.get("certification_dependencies") or []),
        "acceptance_requirements": [],
        "allowed_next_step": "WORKER_REQUEST_GENERATION",
        "execution_out_of_scope": True,
    }
    scope["field_lineage"] = _field_lineage(
        binding=binding,
        consumption=consumption,
    )
    return scope


def _field_lineage(
    *, binding: dict[str, Any], consumption: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    plan = binding["development_composition_plan_artifact"]
    durable = binding["durable_governed_work_artifact"]
    preview = binding["proposal_preview_artifact"]
    return {
        "original_human_goal": _source(binding["artifact_type"], binding["original_request_hash"], binding["artifact_hash"]),
        "project_objective": _source(binding["project_objective_artifact"]["artifact_type"], binding["project_objective_hash"], binding["project_objective_hash"]),
        "platform_knowledge": _source(binding["platform_knowledge_artifact"]["artifact_type"], binding["platform_knowledge_hash"], binding["platform_knowledge_hash"]),
        "knowledge_reuse": _source("KNOWLEDGE_REUSE_EVIDENCE_SNAPSHOT", binding["knowledge_reuse_hash"], binding["knowledge_reuse_hash"]),
        "capability_coverage": _source(binding["capability_composition_coverage_artifact"]["artifact_type"], binding["capability_composition_coverage_hash"], binding["capability_composition_coverage_hash"]),
        "development_plan": _source(plan["artifact_type"], binding["development_composition_plan_hash"], binding["development_composition_plan_hash"]),
        "durable_governed_work": _source(durable["artifact_type"], binding["durable_governed_work_id"], binding["durable_governed_work_hash"]),
        "proposal_preview": _source(preview["artifact_type"], binding["proposal_preview_hash"], binding["proposal_preview_hash"]),
        "approval_request": _source("APPROVAL_REQUEST", binding["approval_request_id"], binding["approval_request_hash"]),
        "approval_consumption": _source(consumption["artifact_type"], consumption["artifact_hash"], consumption["artifact_hash"]),
        "work_scope_and_sequence": _source(plan["artifact_type"], binding["development_composition_plan_hash"], binding["development_composition_plan_hash"]),
        "repository_scope": _source(preview["artifact_type"], binding["proposal_preview_hash"], binding["proposal_preview_hash"]),
        "test_validation_governance_replay_certification": _source(durable["artifact_type"], binding["durable_governed_work_id"], binding["durable_governed_work_hash"]),
    }


def _source(artifact_type: str, identity: str, artifact_hash: str) -> dict[str, Any]:
    return {
        "source_artifact_type": artifact_type,
        "source_identity": identity,
        "source_hash": artifact_hash,
    }


def _ppp_task_package(
    *,
    binding: dict[str, Any],
    consumption: dict[str, Any],
    payload_scope: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    objective = binding["project_objective_artifact"]
    durable = binding["durable_governed_work_artifact"]
    lineage = {
        "implementation_turn_binding_identity": binding["artifact_type"],
        "implementation_turn_binding_hash": binding["artifact_hash"],
        "approval_consumption_identity": consumption["artifact_type"],
        "approval_consumption_hash": consumption["artifact_hash"],
        "development_composition_plan_identity": binding[
            "development_composition_plan_artifact"
        ]["artifact_type"],
        "development_composition_plan_hash": binding[
            "development_composition_plan_hash"
        ],
        "durable_governed_work_id": binding["durable_governed_work_id"],
        "durable_governed_work_hash": binding["durable_governed_work_hash"],
        "proposal_preview_identity": binding["proposal_preview_artifact"]["artifact_type"],
        "proposal_preview_hash": binding["proposal_preview_hash"],
        "approval_request_identity": binding["approval_request_id"],
        "approval_request_hash": binding["approval_request_hash"],
    }
    candidate = {
        "artifact_type": PPP_CANDIDATE_ARTIFACT_V1,
        "runtime_version": APPROVED_DURABLE_WORK_WORKER_PAYLOAD_BINDING_VERSION,
        "ppp_candidate_id": f"{binding['durable_governed_work_id']}:PPP-CANDIDATE",
        "bridge_id": f"{binding['durable_governed_work_id']}:APPROVED-WORK-PPP-BINDING",
        "candidate_status": PPP_CANDIDATE_CREATED,
        "candidate_source_type": APPROVED_DURABLE_WORK_PPP_TASK_PACKAGE_SOURCE,
        "source_improvement_intent": binding["artifact_type"],
        "source_improvement_intent_hash": binding["artifact_hash"],
        "source_gap_reference": binding["capability_composition_coverage_artifact"]["artifact_type"],
        "source_gap_hash": binding["capability_composition_coverage_hash"],
        "source_replay_references": [
            binding["replay_reference"],
            durable["replay_reference"],
        ],
        "source_replay_hashes": [
            binding["artifact_hash"],
            consumption["artifact_hash"],
            binding["capability_composition_coverage_hash"],
            binding["development_composition_plan_hash"],
            binding["durable_governed_work_hash"],
            binding["proposal_preview_hash"],
            binding["approval_request_hash"],
        ],
        "proposal_summary": objective["canonical_project_objective"],
        "affected_runtime": durable.get("downstream_contract_target") or "UNRESOLVED",
        "affected_domain": objective.get("selected_capability_target") or "UNRESOLVED",
        "affected_worker_family": "UNRESOLVED",
        "affected_lifecycle_stage": "APPROVED_DURABLE_GOVERNED_WORK",
        "governance_classification": {
            "work_type": "IMPLEMENTATION",
            "source": APPROVED_DURABLE_WORK_PPP_TASK_PACKAGE_SOURCE,
            "human_review_required": True,
            "approval_is_execution_authorization": False,
        },
        "source_approved_work_lineage": lineage,
        "approved_implementation_scope": deepcopy(payload_scope),
        "approved_implementation_scope_hash": replay_hash(payload_scope),
        "human_approval_requirement": "MANDATORY",
        "human_approval_required": True,
        "approval_granted": False,
        "replay_lineage_preserved": True,
        "certification_status": APPROVED_DURABLE_WORK_PPP_CERTIFICATION_STATUS,
        "ppp_intake_ready": True,
        "proposal_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "implementation_authorized": False,
        "implementation_applied": False,
        "code_modified": False,
        "governance_modified": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "failure_reason": None,
    }
    candidate["artifact_hash"] = replay_hash(candidate)
    return _validate_ppp_task_package(candidate)


def _implementation_request_approval(
    *,
    ppp_candidate: dict[str, Any],
    binding: dict[str, Any],
    consumption: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    approval = {
        "artifact_type": HUMAN_APPROVAL_ARTIFACT_V1,
        "approval_id": f"{binding['durable_governed_work_id']}:IMPLEMENTATION-REQUEST-APPROVAL",
        "approval_status": APPROVED,
        "approval_granted": True,
        "source_ppp_candidate": ppp_candidate["ppp_candidate_id"],
        "source_ppp_candidate_hash": ppp_candidate["artifact_hash"],
        "approval_scope": "CREATE_IMPLEMENTATION_REQUEST_ONLY",
        "implementation_execution_allowed": False,
        "approved_by": "CANONICAL_HUMAN_APPROVAL_CONSUMPTION",
        "approved_at": _require_string(created_at, "created_at"),
        "source_approval_request": binding["approval_request_id"],
        "source_approval_request_hash": binding["approval_request_hash"],
        "source_approval_consumption": consumption["artifact_type"],
        "source_approval_consumption_hash": consumption["artifact_hash"],
        "approval_is_execution_authorization": False,
        "replay_visible": True,
    }
    approval["artifact_hash"] = replay_hash(approval)
    return approval


def _validate_ppp_task_package(value: Any) -> dict[str, Any]:
    candidate = _validate_hash(value, "approved durable work PPP task package")
    if candidate.get("artifact_type") != PPP_CANDIDATE_ARTIFACT_V1:
        raise FailClosedRuntimeError("approved durable work PPP task package type is invalid")
    if candidate.get("candidate_status") != PPP_CANDIDATE_CREATED:
        raise FailClosedRuntimeError("approved durable work PPP task package is not ready")
    if candidate.get("candidate_source_type") != APPROVED_DURABLE_WORK_PPP_TASK_PACKAGE_SOURCE:
        raise FailClosedRuntimeError("approved durable work PPP task package source is invalid")
    if candidate.get("certification_status") != APPROVED_DURABLE_WORK_PPP_CERTIFICATION_STATUS:
        raise FailClosedRuntimeError("approved durable work PPP certification is invalid")
    lineage = candidate.get("source_approved_work_lineage")
    if not isinstance(lineage, dict):
        raise FailClosedRuntimeError("approved durable work PPP lineage is missing")
    for field in (
        "implementation_turn_binding_hash",
        "approval_consumption_hash",
        "development_composition_plan_hash",
        "durable_governed_work_id",
        "durable_governed_work_hash",
        "proposal_preview_hash",
        "approval_request_hash",
    ):
        _require_string(lineage.get(field), field)
    return candidate


def _validate_approval_continuity(
    *, binding: dict[str, Any], consumption: dict[str, Any]
) -> None:
    expected = {
        "binding_hash": binding["artifact_hash"],
        "project_objective_hash": binding["project_objective_hash"],
        "knowledge_reuse_hash": binding["knowledge_reuse_hash"],
        "platform_knowledge_hash": binding["platform_knowledge_hash"],
        "capability_composition_coverage_hash": binding[
            "capability_composition_coverage_hash"
        ],
        "development_composition_plan_hash": binding[
            "development_composition_plan_hash"
        ],
        "durable_governed_work_hash": binding["durable_governed_work_hash"],
        "proposal_preview_hash": binding["proposal_preview_hash"],
        "approval_request_hash": binding["approval_request_hash"],
        "approval_request_id": binding["approval_request_id"],
        "durable_governed_work_id": binding["durable_governed_work_id"],
    }
    for field, value in expected.items():
        if consumption.get(field) != value:
            raise FailClosedRuntimeError(
                f"approved durable work approval continuity mismatch: {field}"
            )
    if consumption.get("consumption_status") != IMPLEMENTATION_TURN_APPROVED_IDENTITIES_CONSUMED:
        raise FailClosedRuntimeError("approved durable work approval was not consumed")


def _repository_scope_unresolved(scope: dict[str, Any]) -> bool:
    status = str(scope.get("repository_scope_status") or "")
    return status.startswith("UNRESOLVED") or not scope.get("repository_targets")


def _validate_hash(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"{label} must be a dict")
    candidate = deepcopy(value)
    body = deepcopy(candidate)
    actual_hash = body.pop("artifact_hash", None)
    if replay_hash(body) != actual_hash:
        raise FailClosedRuntimeError(f"{label} hash mismatch")
    return candidate


def _ensure_replay_available(root: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (root / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("approved durable work Worker payload Replay already exists")


def _persist_step(root: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(root / f"{index:03d}_{step}.json", wrapper)


def _validate_wrapper(wrapper: dict[str, Any], *, index: int, step: str) -> None:
    if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
        raise FailClosedRuntimeError("approved durable work Worker payload Replay ordering mismatch")
    body = deepcopy(wrapper)
    actual_hash = body.pop("replay_hash", None)
    if replay_hash(body) != actual_hash:
        raise FailClosedRuntimeError("approved durable work Worker payload Replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()
