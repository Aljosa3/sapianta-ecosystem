"""Deterministic committed-Objective handoff to certified execution owners.

The module is orchestration only.  It binds one immutable G59-07 commitment to
the existing Platform Core, governed preparation, capability, Authorization,
Worker, Completion, Replay, and Human Interface owners.  It contains no local
selection, authorization, Worker, or execution implementation.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

from aigol.cli.aigol_cli import run_interactive_conversation
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.conversation_native_development_intent_routing import (
    run_conversation_native_development_intent_routing,
)
from aigol.runtime.conversation_session_resume_runtime import resume_conversation_session
from aigol.runtime.conversation_to_ppp_handoff_execution import (
    run_conversation_to_ppp_handoff_execution,
)
from aigol.runtime.execution_authorization_runtime import (
    EXECUTION_AUTHORIZED,
    authorize_execution_ready,
    reconstruct_execution_authorization_replay,
)
from aigol.runtime.execution_runtime import reconstruct_execution_replay, start_execution
from aigol.runtime.execution_summary_runtime import (
    create_execution_summary,
    create_execution_summary_confirmation,
    verify_execution_summary,
)
from aigol.runtime.governed_termination_runtime import (
    TERMINATED,
    reconstruct_governed_termination_replay,
    terminate_reviewed_operation,
)
from aigol.runtime import (
    governed_termination_to_final_execution_certification_binding_runtime
    as final_execution_certification,
)
from aigol.runtime.governed_implementation_dry_run import (
    EXECUTION_READY,
    prepare_governed_implementation_dry_run,
    reconstruct_governed_implementation_dry_run_replay,
)
from aigol.runtime.human_interface_runtime_entry_service import (
    run_human_interface_runtime_entry,
)
from aigol.runtime.implementation_handoff_visibility import (
    create_implementation_handoff_visibility_summary,
)
from aigol.runtime.platform_change_normalization_execution_binding_runtime import (
    CAPABILITY_EXECUTION_BINDING_READY_FOR_AUTHORIZATION,
    PLATFORM_CHANGE_NORMALIZATION,
    bind_platform_change_normalization_to_execution_ready,
    reconstruct_platform_change_normalization_execution_binding_replay,
    validate_platform_change_normalization_execution_binding,
)
from aigol.runtime.platform_change_normalization_worker_completion_adapter import (
    WORKER_CAPABILITY_COMPLETED,
    complete_platform_change_normalization_worker_capability,
    create_platform_change_normalization_worker_completion_evidence,
    reconstruct_platform_change_normalization_worker_completion_replay,
)
from aigol.runtime.platform_core_objective_commitment_runtime_v2 import (
    validate_objective_commitment_record_v2,
)
from aigol.runtime.project_context_semantic_capability_route import (
    ROUTE_COMPLETED,
    reconstruct_project_context_semantic_capability_route,
)
from aigol.runtime.post_execution_replay_review_runtime import (
    REVIEW_COMPLETED,
    reconstruct_post_execution_replay_review,
    review_validated_worker_result,
)
from aigol.runtime.transport.serialization import (
    load_json,
    replay_hash,
    write_json_immutable,
)
from aigol.runtime.worker_assignment_runtime import (
    assign_worker_from_invocation_request,
    default_worker_registry_for_request,
    reconstruct_worker_assignment_runtime_replay,
)
from aigol.runtime.worker_dispatch_runtime import (
    dispatch_assigned_worker,
    reconstruct_worker_dispatch_replay,
)
from aigol.runtime.worker_invocation_request_runtime import (
    create_worker_invocation_request,
    reconstruct_worker_invocation_request_replay,
)
from aigol.runtime.worker_invocation_runtime import (
    invoke_dispatched_worker,
    reconstruct_worker_invocation_replay,
)
from aigol.runtime.worker_result_capture_runtime import (
    capture_worker_result,
    reconstruct_worker_result_capture_replay,
)
from aigol.runtime.worker_result_validation_runtime import (
    reconstruct_worker_result_validation_replay,
    validate_worker_result,
)
from aigol.runtime.human_interface_conversation_runtime_v2 import (
    OBJECTIVE_COMMITMENT_CREATED,
    run_hir_conversation_terminal_v2,
)


FIRST_COMPLETE_CONVERSATION_EXECUTION_INTEGRATION_V2 = (
    "FIRST_COMPLETE_CONVERSATION_EXECUTION_INTEGRATION_V2"
)
OBJECTIVE_COMMITMENT_BOUND_FOR_PIPELINE = "OBJECTIVE_COMMITMENT_BOUND_FOR_PIPELINE"
EXECUTION_PREPARED_AWAITING_AUTHORIZATION = (
    "EXECUTION_PREPARED_AWAITING_AUTHORIZATION"
)
COMPLETE_PIPELINE_RETURNED_TO_AICLI = "COMPLETE_PIPELINE_RETURNED_TO_AICLI"
PREPARATION_ARTIFACT_NAME = "001_execution_prepared.json"
COMMITMENT_EVIDENCE_NAME = "001_committed_objective.json"
EXECUTION_SUMMARY_EVIDENCE_NAME = "001_execution_summary.json"
PLATFORM_CONTEXT_EVIDENCE_NAME = "001_platform_core_project_context.json"


def admit_committed_objective_to_platform_core_v2(
    *,
    commitment_record: dict[str, Any],
    explicit_canonical_artifacts: list[dict[str, Any]],
    explicit_canonical_artifact_references: list[Any] | tuple[Any, ...] = (),
    runtime_root: str | Path,
    workspace: str | Path,
    session_id: str,
    human_actor: str,
    created_at: str,
) -> dict[str, Any]:
    """Admit one exact G59 Commitment through Canonical HIR and Platform Core."""

    record = validate_objective_commitment_record_v2(commitment_record)
    references = tuple(explicit_canonical_artifact_references)
    if references:
        if explicit_canonical_artifacts:
            _fail("canonical artifact objects and references cannot be mixed")
        artifacts: list[dict[str, Any]] = []
    else:
        artifacts = _one_canonical_artifact(explicit_canonical_artifacts)
    actor = _text(human_actor, "human_actor")
    session = _text(session_id, "session_id")
    timestamp = _text(created_at, "created_at")
    root = _integration_root(runtime_root, record)
    prompt = _committed_objective_prompt(record)
    handoff = _with_hash(
        {
            "artifact_type": "CONVERSATION_OBJECTIVE_COMMITMENT_HANDOFF_ARTIFACT_V1",
            "runtime_version": FIRST_COMPLETE_CONVERSATION_EXECUTION_INTEGRATION_V2,
            "handoff_status": OBJECTIVE_COMMITMENT_BOUND_FOR_PIPELINE,
            "commitment_identity": record["commitment_identity"],
            "commitment_record_digest": replay_hash(record),
            "candidate_objective_digest": record["candidate_objective_digest"],
            "source_request_id": record["source_request_id"],
            "platform_core_prompt": prompt,
            "platform_core_prompt_digest": replay_hash(prompt),
            "session_id": session,
            "workspace": str(Path(workspace).resolve()),
            "human_actor": actor,
            "created_at": timestamp,
            "objective_created": False,
            "platform_core_admitted": False,
            "authorization_granted": False,
            "worker_dispatched": False,
            "execution_started": False,
        }
    )
    _write_or_verify(root / "000_objective_commitment_handoff.json", handoff)

    hir_admission = run_human_interface_runtime_entry(
        interface_name="aicli conversation-execute-v2",
        session_id=session,
        human_requests=[prompt],
        created_at=timestamp,
        runtime_root=root / "platform_core_admission",
        workspace=workspace,
        governed_runtime_runner=run_interactive_conversation,
        explicit_canonical_artifacts=artifacts,
        explicit_canonical_artifact_references=references,
        operator_context="G60_02_COMMITTED_OBJECTIVE_HANDOFF",
        presentation={"g60_02_committed_objective_record": record},
    )
    context = hir_admission.get("platform_core_project_services_context")
    if not isinstance(context, dict):
        _fail("Platform Core project-services context is absent")
    objective = context.get("project_objective_inference")
    admission = context.get("admission_precedence")
    governed_work = context.get("governed_read_only_work_result")
    route = context.get("semantic_capability_runtime_route")
    if not isinstance(objective, dict) or objective.get("objective_sufficient") is not True:
        _fail("Platform Core Objective inference did not create a sufficient Objective")
    if objective.get("source_request") != prompt:
        _fail("Platform Core Objective source differs from committed Objective handoff")
    if not isinstance(admission, dict) or admission.get("admission_status") != (
        "EXPLICIT_CERTIFIED_CAPABILITY_REQUEST_ADMITTED"
    ):
        _fail("Platform Core admission did not admit the certified capability request")
    if not isinstance(governed_work, dict) or not isinstance(route, dict):
        _fail("certified capability route is absent")
    if route.get("route_status") != ROUTE_COMPLETED or route.get(
        "selected_capability_identifier"
    ) != PLATFORM_CHANGE_NORMALIZATION:
        _fail("committed Objective did not select the certified normalization capability")

    return {
        "integration_runtime_version": FIRST_COMPLETE_CONVERSATION_EXECUTION_INTEGRATION_V2,
        "admission_status": "COMMITTED_OBJECTIVE_ADMITTED_TO_PLATFORM_CORE",
        "commitment_record": record,
        "handoff_artifact": handoff,
        "hir_admission": hir_admission,
        "platform_core_objective": objective,
        "platform_core_admission": admission,
        "semantic_capability_route": route,
        "integration_root": str(root),
        "human_actor": actor,
        "session_id": session,
        "workspace": str(Path(workspace).resolve()),
        "created_at": timestamp,
        "authorization_granted": False,
        "worker_dispatched": False,
        "execution_started": False,
    }


def validate_committed_objective_admission_transport_v2(
    commitment_record: dict[str, Any],
    *,
    platform_core_prompt: str,
) -> dict[str, Any]:
    """Validate the exact G60 committed-Objective projection transported by HIR."""

    record = validate_objective_commitment_record_v2(commitment_record)
    if _committed_objective_prompt(record) != _text(
        platform_core_prompt, "platform_core_prompt"
    ):
        _fail("Platform Core prompt differs from committed Objective projection")
    return record


def prepare_committed_objective_execution_v2(
    *,
    commitment_record: dict[str, Any],
    explicit_canonical_artifacts: list[dict[str, Any]],
    explicit_canonical_artifact_references: list[Any] | tuple[Any, ...] = (),
    runtime_root: str | Path,
    workspace: str | Path,
    session_id: str,
    human_actor: str,
    created_at: str,
) -> dict[str, Any]:
    """Admit one committed Objective and prepare an authorization target."""

    admitted = admit_committed_objective_to_platform_core_v2(
        commitment_record=commitment_record,
        explicit_canonical_artifacts=explicit_canonical_artifacts,
        explicit_canonical_artifact_references=(
            explicit_canonical_artifact_references
        ),
        runtime_root=runtime_root,
        workspace=workspace,
        session_id=session_id,
        human_actor=human_actor,
        created_at=created_at,
    )
    record = admitted["commitment_record"]
    actor = admitted["human_actor"]
    session = admitted["session_id"]
    timestamp = admitted["created_at"]
    root = Path(admitted["integration_root"])
    prompt = admitted["handoff_artifact"]["platform_core_prompt"]
    handoff = admitted["handoff_artifact"]
    hir_admission = admitted["hir_admission"]
    objective = admitted["platform_core_objective"]
    admission = admitted["platform_core_admission"]
    route = admitted["semantic_capability_route"]

    token = record["commitment_identity"].removeprefix(
        "objective-commitment-local-sha256:"
    )[:24]
    chain = f"G60-02-{token}"
    development_prompt = (
        "Create a filesystem worker for this committed Objective: " + prompt
    )
    governance_root = root / "development_governance"
    allocation = resume_conversation_session(
        session_id=chain,
        runtime_root=governance_root / "session",
        created_at=timestamp,
    )
    prompt_id = f"{chain}:{allocation['next_turn_id']}"
    routing = run_conversation_native_development_intent_routing(
        routing_id=f"{prompt_id}:ROUTING",
        prompt_id=prompt_id,
        human_prompt=development_prompt,
        canonical_chain_id=prompt_id,
        turn_allocation_evidence=allocation,
        created_at=timestamp,
        replay_dir=governance_root / "routing",
    )
    ppp_handoff = run_conversation_to_ppp_handoff_execution(
        execution_id=f"{prompt_id}:HANDOFF",
        native_development_intent_routed_artifact=routing[
            "native_development_intent_routed_artifact"
        ],
        created_at=timestamp,
        replay_dir=governance_root / "handoff",
    )
    visibility = create_implementation_handoff_visibility_summary(
        visibility_id=f"{chain}:VISIBILITY",
        handoff_replay_reference=ppp_handoff["handoff_replay_reference"],
        approval_status=ppp_handoff["approval_status"],
        created_at=timestamp,
        replay_dir=governance_root / "visibility",
    )
    execution_ready = prepare_governed_implementation_dry_run(
        dry_run_id=f"{chain}:DRY-RUN",
        handoff_replay_reference=ppp_handoff["handoff_replay_reference"],
        handoff_visibility_artifact=visibility[
            "implementation_handoff_visibility_artifact"
        ],
        upstream_lineage_artifact=ppp_handoff[
            "conversation_to_ppp_handoff_execution_artifact"
        ],
        created_at=timestamp,
        replay_dir=governance_root / "execution_ready",
    )
    if execution_ready["execution_ready_status_artifact"].get(
        "execution_status"
    ) != EXECUTION_READY:
        _fail("Development Governance did not establish execution readiness")

    binding = bind_platform_change_normalization_to_execution_ready(
        binding_id=f"{chain}:CAPABILITY-BINDING",
        semantic_capability_route_artifact=route,
        semantic_capability_route_replay_reference=route["replay_reference"],
        execution_ready_status_artifact=execution_ready[
            "execution_ready_status_artifact"
        ],
        execution_ready_replay_reference=governance_root / "execution_ready",
        requested_by=actor,
        created_at=timestamp,
        replay_dir=root / "capability_execution_binding",
    )
    binding_artifact = binding["capability_execution_binding_artifact"]
    if binding_artifact.get("binding_status") != (
        CAPABILITY_EXECUTION_BINDING_READY_FOR_AUTHORIZATION
    ):
        _fail("capability execution binding did not become authorization-ready")

    execution_summary = create_execution_summary(
        summary_id=f"{chain}:EXECUTION-SUMMARY",
        original_request=prompt,
        interpreted_intent={
            "canonical_project_objective": deepcopy(
                objective["canonical_project_objective"]
            ),
            "platform_core_objective_hash": objective["artifact_hash"],
        },
        selected_route={
            "selected_capability_identifier": PLATFORM_CHANGE_NORMALIZATION,
            "semantic_capability_route_hash": route["artifact_hash"],
            "capability_execution_binding_hash": binding_artifact["artifact_hash"],
        },
        planned_actions=[
            "authorize execution-ready evidence",
            "dispatch the certified assigned Worker",
            "capture and validate Worker completion",
            "return authenticated completion through HIR",
        ],
        expected_outputs=["canonical normalized platform change evidence"],
        assumptions=["the explicit canonical artifact is the intended execution input"],
        constraints=["no repository mutation", "no owner redesign"],
        risk_classification={"risk_class": "BOUNDED_REPLAY_ONLY"},
        execution_scope={
            "capability_identifier": PLATFORM_CHANGE_NORMALIZATION,
            "commitment_identity": record["commitment_identity"],
        },
        replay_references=[
            route["replay_reference"],
            str(governance_root / "execution_ready"),
            binding["capability_execution_binding_replay_reference"],
        ],
        created_by="HUMAN_INTERFACE_RUNTIME",
        created_at=timestamp,
    )
    commitment_reference = root / COMMITMENT_EVIDENCE_NAME
    execution_summary_reference = root / EXECUTION_SUMMARY_EVIDENCE_NAME
    platform_context = hir_admission.get("platform_core_project_services_context")
    if not isinstance(platform_context, dict):
        _fail("Platform Core project context is absent")
    platform_context_reference = root / PLATFORM_CONTEXT_EVIDENCE_NAME
    _write_or_verify(commitment_reference, record)
    _write_or_verify(execution_summary_reference, execution_summary)
    _write_or_verify(platform_context_reference, platform_context)
    prepared_artifact = _with_hash(
        {
            "artifact_type": "COMMITTED_OBJECTIVE_EXECUTION_PREPARATION_ARTIFACT_V1",
            "runtime_version": FIRST_COMPLETE_CONVERSATION_EXECUTION_INTEGRATION_V2,
            "preparation_status": EXECUTION_PREPARED_AWAITING_AUTHORIZATION,
            "commitment_identity": record["commitment_identity"],
            "commitment_record_digest": replay_hash(record),
            "platform_core_objective_hash": objective["artifact_hash"],
            "platform_core_admission_hash": admission["artifact_hash"],
            "development_governance_execution_ready_hash": execution_ready[
                "execution_ready_status_artifact"
            ]["artifact_hash"],
            "semantic_capability_route_hash": route["artifact_hash"],
            "capability_execution_binding_hash": binding_artifact["artifact_hash"],
            "execution_summary_hash": execution_summary["artifact_hash"],
            "commitment_record_reference": str(commitment_reference),
            "execution_summary_reference": str(execution_summary_reference),
            "platform_core_project_context_reference": str(
                platform_context_reference
            ),
            "semantic_capability_route_replay_reference": route[
                "replay_reference"
            ],
            "execution_ready_replay_reference": execution_ready[
                "governed_implementation_dry_run_replay_reference"
            ],
            "capability_execution_binding_replay_reference": binding[
                "capability_execution_binding_replay_reference"
            ],
            "expected_authorization_action": (
                f"/authorize {execution_summary['artifact_hash']}"
            ),
            "development_governance_prompt": development_prompt,
            "integration_root": str(root),
            "human_actor": actor,
            "session_id": session,
            "workspace": str(Path(workspace).resolve()),
            "authorization_granted": False,
            "worker_dispatched": False,
            "execution_started": False,
            "created_at": timestamp,
        }
    )
    _write_or_verify(root / PREPARATION_ARTIFACT_NAME, prepared_artifact)
    return {
        "integration_runtime_version": FIRST_COMPLETE_CONVERSATION_EXECUTION_INTEGRATION_V2,
        "admission_status": "COMMITTED_OBJECTIVE_ADMITTED_TO_PLATFORM_CORE",
        "preparation_status": EXECUTION_PREPARED_AWAITING_AUTHORIZATION,
        "commitment_record": record,
        "handoff_artifact": handoff,
        "hir_admission": hir_admission,
        "platform_core_objective": objective,
        "platform_core_admission": admission,
        "semantic_capability_route": route,
        "development_governance_routing": routing,
        "development_governance_handoff": ppp_handoff,
        "development_governance_visibility": visibility,
        "execution_ready": execution_ready,
        "capability_execution_binding": binding,
        "execution_summary": execution_summary,
        "expected_authorization_action": prepared_artifact[
            "expected_authorization_action"
        ],
        "prepared_artifact": prepared_artifact,
        "integration_root": str(root),
        "human_actor": actor,
        "session_id": session,
        "workspace": str(Path(workspace).resolve()),
        "created_at": timestamp,
        "authorization_granted": False,
        "worker_dispatched": False,
        "execution_started": False,
    }


def reconstruct_committed_objective_execution_preparation_v2(
    preparation_reference: str | Path,
) -> dict[str, Any]:
    """Reconstruct one pending preparation from its immutable owner evidence."""

    path = Path(preparation_reference)
    prepared_artifact = _load_hashed_artifact(
        path,
        artifact_type="COMMITTED_OBJECTIVE_EXECUTION_PREPARATION_ARTIFACT_V1",
        label="committed Objective execution preparation",
    )
    if prepared_artifact.get("preparation_status") != (
        EXECUTION_PREPARED_AWAITING_AUTHORIZATION
    ):
        _fail("committed Objective execution preparation is not pending")
    root = path.parent.resolve()
    recorded_root = Path(
        _text(prepared_artifact.get("integration_root"), "integration_root")
    ).resolve()
    if recorded_root != root:
        _fail("committed Objective execution preparation root differs")

    commitment_path = _inside_root(
        prepared_artifact.get("commitment_record_reference"),
        root,
        "commitment_record_reference",
    )
    summary_path = _inside_root(
        prepared_artifact.get("execution_summary_reference"),
        root,
        "execution_summary_reference",
    )
    context_path = _inside_root(
        prepared_artifact.get("platform_core_project_context_reference"),
        root,
        "platform_core_project_context_reference",
    )
    route_path = _inside_root(
        prepared_artifact.get("semantic_capability_route_replay_reference"),
        root,
        "semantic_capability_route_replay_reference",
    )
    ready_path = _inside_root(
        prepared_artifact.get("execution_ready_replay_reference"),
        root,
        "execution_ready_replay_reference",
    )
    binding_path = _inside_root(
        prepared_artifact.get("capability_execution_binding_replay_reference"),
        root,
        "capability_execution_binding_replay_reference",
    )

    record = validate_objective_commitment_record_v2(load_json(commitment_path))
    summary = verify_execution_summary(load_json(summary_path))
    platform_context = _load_hashed_artifact(
        context_path,
        artifact_type="UNIFIED_HUMAN_INTERFACE_PROJECT_CONTEXT_ARTIFACT_V1",
        label="Platform Core project context",
    )
    route = reconstruct_project_context_semantic_capability_route(route_path)
    ready = reconstruct_governed_implementation_dry_run_replay(ready_path)
    binding_reconstruction = (
        reconstruct_platform_change_normalization_execution_binding_replay(
            binding_path
        )
    )
    binding_wrapper = load_json(
        binding_path / "001_capability_execution_binding_recorded.json"
    )
    binding_artifact = validate_platform_change_normalization_execution_binding(
        binding_wrapper.get("artifact")
    )

    checks = (
        replay_hash(record) == prepared_artifact.get("commitment_record_digest"),
        record.get("commitment_identity")
        == prepared_artifact.get("commitment_identity"),
        summary.get("artifact_hash")
        == prepared_artifact.get("execution_summary_hash"),
        prepared_artifact.get("expected_authorization_action")
        == f"/authorize {summary['artifact_hash']}",
        route.get("artifact_hash")
        == prepared_artifact.get("semantic_capability_route_hash"),
        ready.get("execution_status") == EXECUTION_READY,
        ready.get("replay_hash")
        == binding_artifact.get("execution_ready_replay_hash"),
        binding_reconstruction.get("binding_status")
        == CAPABILITY_EXECUTION_BINDING_READY_FOR_AUTHORIZATION,
        binding_artifact.get("artifact_hash")
        == prepared_artifact.get("capability_execution_binding_hash"),
        platform_context.get("project_objective_inference", {}).get(
            "artifact_hash"
        )
        == prepared_artifact.get("platform_core_objective_hash"),
        platform_context.get("admission_precedence", {}).get("artifact_hash")
        == prepared_artifact.get("platform_core_admission_hash"),
    )
    if not all(checks):
        _fail("committed Objective execution preparation lineage differs")

    return {
        "integration_runtime_version": FIRST_COMPLETE_CONVERSATION_EXECUTION_INTEGRATION_V2,
        "preparation_status": EXECUTION_PREPARED_AWAITING_AUTHORIZATION,
        "commitment_record": record,
        "platform_core_project_context": platform_context,
        "semantic_capability_route": {
            **route,
            "replay_reference": str(route_path),
        },
        "execution_ready": {
            **ready,
            "governed_implementation_dry_run_replay_reference": str(ready_path),
        },
        "capability_execution_binding": {
            "capability_execution_binding_artifact": binding_artifact,
            "capability_execution_binding_replay_reference": str(binding_path),
        },
        "execution_summary": summary,
        "expected_authorization_action": prepared_artifact[
            "expected_authorization_action"
        ],
        "prepared_artifact": prepared_artifact,
        "integration_root": str(root),
        "human_actor": prepared_artifact["human_actor"],
        "session_id": prepared_artifact["session_id"],
        "workspace": prepared_artifact["workspace"],
        "created_at": prepared_artifact["created_at"],
        "preparation_reconstructed": True,
    }


def authorize_pending_committed_objective_execution_v2(
    *,
    runtime_root: str | Path,
    session_id: str,
    explicit_authorization_action: str,
    human_actor: str,
    authorized_at: str,
) -> dict[str, Any]:
    """Continue the one exact pending G66 preparation through its owners."""

    root = Path(runtime_root)
    session = _text(session_id, "session_id")
    candidates = [
        path
        for path in sorted(
            (root / "conversation_execution_v2").glob(
                f"*/{PREPARATION_ARTIFACT_NAME}"
            )
        )
        if not (path.parent / "002_execution_completed.json").exists()
    ]
    if len(candidates) != 1:
        _fail("exactly one pending committed Objective preparation is required")
    prepared = reconstruct_committed_objective_execution_preparation_v2(
        candidates[0]
    )
    if prepared["session_id"] != session:
        _fail("pending committed Objective preparation session differs")
    actor = _text(human_actor, "human_actor")
    if prepared["human_actor"] != actor:
        _fail("pending committed Objective preparation Human actor differs")
    completed = authorize_and_execute_prepared_objective_v2(
        prepared,
        explicit_authorization_action=explicit_authorization_action,
        authorizing_actor=actor,
        authorized_at=_text(authorized_at, "authorized_at"),
    )
    completed["prepared"] = prepared
    return completed


def authorize_and_execute_prepared_objective_v2(
    prepared: dict[str, Any],
    *,
    explicit_authorization_action: str,
    authorizing_actor: str | None = None,
    authorized_at: str | None = None,
) -> dict[str, Any]:
    """Authorize one exact prepared summary and delegate the full Worker path."""

    if not isinstance(prepared, dict) or prepared.get("preparation_status") != (
        EXECUTION_PREPARED_AWAITING_AUTHORIZATION
    ):
        _fail("valid committed-Objective execution preparation is required")
    if explicit_authorization_action.strip() != prepared.get(
        "expected_authorization_action"
    ):
        _fail("exact /authorize execution-summary hash is required")
    record = validate_objective_commitment_record_v2(prepared["commitment_record"])
    root = Path(_text(prepared["integration_root"], "integration_root"))
    prepared_actor = _text(prepared["human_actor"], "human_actor")
    actor = (
        _text(authorizing_actor, "authorizing_actor")
        if authorizing_actor is not None
        else prepared_actor
    )
    if actor != prepared_actor:
        _fail("authorizing actor differs from committed Objective Human actor")
    timestamp = (
        _text(authorized_at, "authorized_at")
        if authorized_at is not None
        else _text(prepared["created_at"], "created_at")
    )
    chain = "G60-02-" + record["commitment_identity"].removeprefix(
        "objective-commitment-local-sha256:"
    )[:24]
    summary = prepared["execution_summary"]
    confirmation = create_execution_summary_confirmation(
        confirmation_id=f"{chain}:EXECUTION-SUMMARY-CONFIRMATION",
        execution_summary_artifact=summary,
        decision="APPROVE",
        confirmed_by=actor,
        confirmed_at=timestamp,
    )
    ready_reference = prepared["execution_ready"][
        "governed_implementation_dry_run_replay_reference"
    ]
    authorization = authorize_execution_ready(
        authorization_id=f"{chain}:AUTHORIZATION",
        execution_ready_replay_reference=ready_reference,
        authorizing_actor=actor,
        authorized_at=timestamp,
        replay_dir=root / "authorization",
        execution_summary_artifact=summary,
        human_confirmation_artifact=confirmation,
    )
    if authorization.get("authorization_status") != EXECUTION_AUTHORIZED:
        _fail("existing Authorization owner refused execution")
    request = create_worker_invocation_request(
        invocation_request_id=f"{chain}:WORKER-REQUEST",
        execution_authorization_replay_reference=authorization[
            "execution_authorization_replay_reference"
        ],
        requested_by=actor,
        requested_at=timestamp,
        replay_dir=root / "worker_request",
    )
    assignment = assign_worker_from_invocation_request(
        worker_assignment_id=f"{chain}:WORKER-ASSIGNMENT",
        worker_invocation_request_artifact=request["worker_invocation_request_artifact"],
        worker_invocation_request_replay_reference=request[
            "worker_invocation_request_replay_reference"
        ],
        worker_registry_artifacts=default_worker_registry_for_request(
            request["worker_invocation_request_artifact"], created_at=timestamp
        ),
        assigned_by=actor,
        assigned_at=timestamp,
        replay_dir=root / "worker_assignment",
    )
    dispatch = dispatch_assigned_worker(
        worker_dispatch_id=f"{chain}:WORKER-DISPATCH",
        worker_assignment_artifact=assignment["worker_assignment_artifact"],
        worker_assignment_replay_reference=assignment[
            "worker_assignment_replay_reference"
        ],
        dispatched_by=actor,
        dispatched_at=timestamp,
        replay_dir=root / "worker_dispatch",
    )
    invocation = invoke_dispatched_worker(
        worker_invocation_id=f"{chain}:WORKER-INVOCATION",
        worker_dispatch_artifact=dispatch["worker_dispatch_artifact"],
        worker_dispatch_replay_reference=dispatch["worker_dispatch_replay_reference"],
        invoked_by="AIGOL_GOVERNANCE",
        invoked_at=timestamp,
        replay_dir=root / "worker_invocation",
    )
    invoked = invocation["worker_invocation_artifact"]
    execution = start_execution(
        execution_id=f"{chain}:EXECUTION",
        invocation_artifact=invoked,
        invocation_replay=invocation["invocation_result_artifact"],
        dispatch_artifact=dispatch["worker_dispatch_artifact"],
        worker_assignment_artifact=assignment["worker_assignment_artifact"],
        canonical_chain_id=invoked["chain_id"],
        execution_metadata={"execution_mode": "BOUND_CAPABILITY_COMPLETION"},
        execution_context={
            "capability_id": PLATFORM_CHANGE_NORMALIZATION,
            "allowed_effects": ["RECORD_EXECUTION_START"],
            "commitment_identity": record["commitment_identity"],
        },
        started_by="AIGOL",
        started_at=timestamp,
        replay_reference=f"{chain}:EXECUTION-REPLAY",
        replay_dir=root / "execution",
    )
    binding = prepared["capability_execution_binding"]
    worker_output = create_platform_change_normalization_worker_completion_evidence(
        capability_execution_binding_artifact=binding[
            "capability_execution_binding_artifact"
        ],
        capability_execution_binding_replay_reference=binding[
            "capability_execution_binding_replay_reference"
        ],
        worker_invocation_artifact=invoked,
        worker_invocation_replay_reference=invocation[
            "worker_invocation_replay_reference"
        ],
        execution_artifact=execution["execution_artifact"],
        execution_replay_reference=root / "execution",
        completed_at=timestamp,
    )
    capture = capture_worker_result(
        worker_result_capture_id=f"{chain}:WORKER-CAPTURE",
        worker_invocation_artifact=invoked,
        worker_invocation_replay_reference=invocation[
            "worker_invocation_replay_reference"
        ],
        worker_output=worker_output,
        captured_by=actor,
        captured_at=timestamp,
        replay_dir=root / "result_capture",
        execution_artifact=execution["execution_artifact"],
        execution_replay=execution["execution_replay"],
        execution_replay_reference=str(root / "execution"),
    )
    validation = validate_worker_result(
        worker_result_validation_id=f"{chain}:WORKER-VALIDATION",
        worker_result_capture_artifact=capture["worker_result_capture_artifact"],
        worker_result_capture_replay_reference=capture[
            "worker_result_capture_replay_reference"
        ],
        validated_by=actor,
        validated_at=timestamp,
        replay_dir=root / "result_validation",
    )
    completion = complete_platform_change_normalization_worker_capability(
        completion_id=f"{chain}:COMPLETION",
        capability_execution_binding_artifact=binding[
            "capability_execution_binding_artifact"
        ],
        capability_execution_binding_replay_reference=binding[
            "capability_execution_binding_replay_reference"
        ],
        execution_authorization_replay_reference=authorization[
            "execution_authorization_replay_reference"
        ],
        worker_completion_evidence=worker_output,
        worker_result_capture_artifact=capture["worker_result_capture_artifact"],
        worker_result_capture_replay_reference=capture[
            "worker_result_capture_replay_reference"
        ],
        worker_result_validation_artifact=validation[
            "worker_result_validation_artifact"
        ],
        worker_result_validation_replay_reference=validation[
            "worker_result_validation_replay_reference"
        ],
        completed_by=actor,
        completed_at=timestamp,
        replay_dir=root / "completion",
    )
    if completion.get("completion_status") != WORKER_CAPABILITY_COMPLETED:
        _fail("existing Completion owner refused Worker completion evidence")
    replay_review = review_validated_worker_result(
        post_execution_replay_review_id=f"{chain}:POST-EXECUTION-REPLAY-REVIEW",
        worker_result_validation_artifact=validation[
            "worker_result_validation_artifact"
        ],
        worker_result_validation_replay_reference=validation[
            "worker_result_validation_replay_reference"
        ],
        reviewed_by=actor,
        reviewed_at=timestamp,
        replay_dir=root / "post_execution_replay_review",
    )
    if replay_review.get("review_status") != REVIEW_COMPLETED:
        _fail(
            replay_review.get("failure_reason")
            or "existing Replay Review owner refused validated Worker result"
        )
    termination = terminate_reviewed_operation(
        governed_termination_id=f"{chain}:GOVERNED-TERMINATION",
        post_execution_replay_review_artifact=replay_review[
            "post_execution_replay_review_artifact"
        ],
        post_execution_replay_review_replay_reference=replay_review[
            "post_execution_replay_review_replay_reference"
        ],
        terminated_by=actor,
        terminated_at=timestamp,
        replay_dir=root / "governed_termination",
    )
    if termination.get("termination_status") != TERMINATED:
        _fail(
            termination.get("failure_reason")
            or "existing Governed Termination owner refused reviewed operation"
        )
    certification = final_execution_certification.certify_governed_termination(
        binding_id=f"{chain}:FINAL-EXECUTION-CERTIFICATION",
        terminal_capture=termination,
        termination_replay_reference=termination[
            "governed_termination_replay_reference"
        ],
        termination_reconstructor=reconstruct_governed_termination_replay,
        certified_by=actor,
        certified_at=timestamp,
        replay_dir=root / "final_execution_certification",
    )
    if certification.get("binding_status") != (
        final_execution_certification.SUCCESS
    ):
        _fail(
            certification.get("failure_reason")
            or "existing final Certification owner refused terminal evidence"
        )
    hir_return = run_human_interface_runtime_entry(
        interface_name="aicli conversation-execute-v2",
        session_id=prepared["session_id"],
        human_requests=[summary["original_request"]],
        created_at=timestamp,
        runtime_root=root / "hir_completion_return",
        workspace=prepared["workspace"],
        governed_runtime_runner=run_interactive_conversation,
        worker_capability_completion_capture=completion,
    )
    replay_evidence = _reconstruct_all(
        prepared=prepared,
        authorization=authorization,
        request=request,
        assignment=assignment,
        dispatch=dispatch,
        invocation=invocation,
        execution_root=root / "execution",
        capture=capture,
        validation=validation,
        completion=completion,
        replay_review=replay_review,
        termination=termination,
        certification=certification,
    )
    completed_artifact = _with_hash(
        {
            "artifact_type": "CONVERSATION_TO_EXECUTION_COMPLETION_ARTIFACT_V1",
            "runtime_version": FIRST_COMPLETE_CONVERSATION_EXECUTION_INTEGRATION_V2,
            "completion_status": COMPLETE_PIPELINE_RETURNED_TO_AICLI,
            "commitment_identity": record["commitment_identity"],
            "execution_summary_hash": summary["artifact_hash"],
            "human_confirmation_hash": confirmation["artifact_hash"],
            "authorization_hash": authorization["execution_authorization_artifact"][
                "artifact_hash"
            ],
            "worker_invocation_hash": invoked["artifact_hash"],
            "worker_completion_hash": completion[
                "worker_capability_completion_artifact"
            ]["artifact_hash"],
            "post_execution_replay_review_hash": replay_review[
                "post_execution_replay_review_artifact"
            ]["artifact_hash"],
            "governed_termination_hash": termination[
                "governed_termination_artifact"
            ]["artifact_hash"],
            "final_execution_certification_hash": certification[
                "final_execution_certification_hash"
            ],
            "human_visible_result_hash": replay_hash(
                hir_return["human_visible_completion_result"]
            ),
            "replay_stage_count": len(replay_evidence),
            "authorization_granted": True,
            "worker_dispatched": True,
            "execution_started": True,
            "completion_recorded": True,
            "post_execution_replay_reviewed": True,
            "governed_termination_recorded": True,
            "execution_certified": True,
            "hir_returned": True,
            "aicli_presented": True,
            "completed_at": timestamp,
        }
    )
    _write_or_verify(root / "002_execution_completed.json", completed_artifact)
    return {
        "integration_runtime_version": FIRST_COMPLETE_CONVERSATION_EXECUTION_INTEGRATION_V2,
        "completion_status": COMPLETE_PIPELINE_RETURNED_TO_AICLI,
        "authorization": authorization,
        "worker_request": request,
        "worker_assignment": assignment,
        "worker_dispatch": dispatch,
        "worker_invocation": invocation,
        "execution": execution,
        "worker_result_capture": capture,
        "worker_result_validation": validation,
        "worker_completion": completion,
        "post_execution_replay_review": replay_review,
        "governed_termination": termination,
        "final_execution_certification": certification,
        "hir_return": hir_return,
        "human_visible_completion_result": hir_return[
            "human_visible_completion_result"
        ],
        "replay_evidence": replay_evidence,
        "completed_artifact": completed_artifact,
        "aicli_authorizes": False,
        "aicli_executes": False,
        "aicli_owns_replay": False,
    }


def run_complete_conversation_execution_terminal_v2(
    *,
    runtime_root: str | Path,
    workspace: str | Path,
    session_id: str,
    human_identity: str,
    created_at: str,
    explicit_canonical_artifacts: list[dict[str, Any]],
    ttl_seconds: int = 3600,
    input_reader: Callable[[str], str] = input,
    output_writer: Callable[[str], None] = print,
) -> dict[str, Any]:
    """Run Human-to-commitment then the existing complete execution path."""

    commitment = run_hir_conversation_terminal_v2(
        runtime_root=runtime_root,
        workspace_identity=workspace,
        session_identity=session_id,
        human_identity=human_identity,
        created_at=created_at,
        ttl_seconds=ttl_seconds,
        input_reader=input_reader,
        output_writer=output_writer,
    )
    if commitment.get("terminal_condition") != OBJECTIVE_COMMITMENT_CREATED:
        return commitment
    output_writer("pipeline_handoff: OBJECTIVE_COMMITMENT_BOUND_FOR_PIPELINE")
    prepared = prepare_committed_objective_execution_v2(
        commitment_record=commitment["commitment_record"],
        explicit_canonical_artifacts=explicit_canonical_artifacts,
        runtime_root=runtime_root,
        workspace=workspace,
        session_id=session_id,
        human_actor=human_identity,
        created_at=created_at,
    )
    output_writer(
        "platform_core_objective: "
        + prepared["platform_core_objective"]["objective_status"]
    )
    output_writer(
        "platform_core_admission: "
        + prepared["platform_core_admission"]["admission_status"]
    )
    output_writer("development_governance: EXECUTION_READY")
    output_writer(
        "capability_selection: "
        + prepared["semantic_capability_route"]["selected_capability_identifier"]
    )
    output_writer("execution_summary_hash: " + prepared["execution_summary"]["artifact_hash"])
    output_writer("next: " + prepared["expected_authorization_action"])
    while True:
        try:
            action = input_reader("aicli-v2-authorization> ").strip()
        except (EOFError, StopIteration):
            return {
                "preparation_status": EXECUTION_PREPARED_AWAITING_AUTHORIZATION,
                "execution_authorized": False,
                "worker_dispatched": False,
            }
        if action == prepared["expected_authorization_action"]:
            break
        output_writer(
            "authorization_refused: EXACT_EXECUTION_SUMMARY_HASH_REQUIRED"
        )
        output_writer("execution_authorized: false")
        output_writer("worker_dispatched: false")
    completed = authorize_and_execute_prepared_objective_v2(
        prepared, explicit_authorization_action=action
    )
    output_writer("authorization: EXECUTION_AUTHORIZED")
    output_writer("worker_request: WORKER_INVOCATION_REQUEST_CREATED")
    output_writer("worker_assignment: WORKER_ASSIGNED")
    output_writer("worker_dispatch: WORKER_DISPATCHED")
    output_writer("worker_invocation: WORKER_INVOKED")
    output_writer("execution: EXECUTING")
    output_writer("worker_result_capture: WORKER_RESULT_CAPTURED")
    output_writer("worker_result_validation: RESULT_VALIDATED")
    output_writer("completion: WORKER_CAPABILITY_COMPLETED")
    output_writer("post_execution_replay_review: REVIEW_COMPLETED")
    output_writer("governed_termination: TERMINATED")
    output_writer("final_certification: G31_FINAL_EXECUTION_CERTIFICATION_COMPLETED")
    visible = completed["human_visible_completion_result"]
    output_writer(
        "human_completion: "
        + str(visible.get("presentation_summary") or visible.get("message") or visible)
    )
    output_writer(
        "replay_evidence: " + str(len(completed["replay_evidence"])) + " stages reconstructed"
    )
    output_writer("aicli_authorizes: false")
    output_writer("aicli_executes: false")
    output_writer("pipeline_status: COMPLETE_PIPELINE_RETURNED_TO_AICLI")
    return completed


def _committed_objective_prompt(record: dict[str, Any]) -> str:
    objective = record["candidate_objective_snapshot"]["canonical_objective"]
    work_type = _text(objective["work_type"], "work_type").lower()
    action = _text(objective["requested_action"], "requested_action")
    subject = _text(objective["subject"], "subject")
    outcome = _text(objective["expected_outcome"], "expected_outcome")
    return f"work_type: {work_type}. {action} {subject} into {outcome}."


def _reconstruct_all(**captures: Any) -> dict[str, dict[str, Any]]:
    prepared = captures["prepared"]
    route = prepared["semantic_capability_route"]
    binding = prepared["capability_execution_binding"]
    authorization = captures["authorization"]
    request = captures["request"]
    assignment = captures["assignment"]
    dispatch = captures["dispatch"]
    invocation = captures["invocation"]
    capture = captures["capture"]
    validation = captures["validation"]
    completion = captures["completion"]
    replay_review = captures["replay_review"]
    termination = captures["termination"]
    certification = captures["certification"]
    return {
        "capability_route": reconstruct_project_context_semantic_capability_route(
            route["replay_reference"]
        ),
        "capability_binding": reconstruct_platform_change_normalization_execution_binding_replay(
            binding["capability_execution_binding_replay_reference"]
        ),
        "authorization": reconstruct_execution_authorization_replay(
            authorization["execution_authorization_replay_reference"]
        ),
        "worker_request": reconstruct_worker_invocation_request_replay(
            request["worker_invocation_request_replay_reference"]
        ),
        "worker_assignment": reconstruct_worker_assignment_runtime_replay(
            assignment["worker_assignment_replay_reference"]
        ),
        "worker_dispatch": reconstruct_worker_dispatch_replay(
            dispatch["worker_dispatch_replay_reference"]
        ),
        "worker_invocation": reconstruct_worker_invocation_replay(
            invocation["worker_invocation_replay_reference"]
        ),
        "execution": reconstruct_execution_replay(captures["execution_root"]),
        "worker_result_capture": reconstruct_worker_result_capture_replay(
            capture["worker_result_capture_replay_reference"]
        ),
        "worker_result_validation": reconstruct_worker_result_validation_replay(
            validation["worker_result_validation_replay_reference"]
        ),
        "completion": reconstruct_platform_change_normalization_worker_completion_replay(
            completion["worker_capability_completion_replay_reference"]
        ),
        "post_execution_replay_review": reconstruct_post_execution_replay_review(
            replay_review["post_execution_replay_review_replay_reference"]
        ),
        "governed_termination": reconstruct_governed_termination_replay(
            termination["governed_termination_replay_reference"]
        ),
        "final_execution_certification": (
            final_execution_certification.replay_certification
            .reconstruct_replay_certification_replay(
                certification[
                    "final_execution_certification_replay_reference"
                ]
            )
        ),
    }


def _one_canonical_artifact(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or len(value) != 1 or not isinstance(value[0], dict):
        _fail("exactly one explicit canonical artifact is required")
    return [deepcopy(value[0])]


def _integration_root(runtime_root: str | Path, record: dict[str, Any]) -> Path:
    token = record["commitment_identity"].removeprefix(
        "objective-commitment-local-sha256:"
    )
    return Path(runtime_root) / "conversation_execution_v2" / token


def _with_hash(value: dict[str, Any]) -> dict[str, Any]:
    artifact = deepcopy(value)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _write_or_verify(path: Path, value: dict[str, Any]) -> None:
    if path.exists():
        if load_json(path) != value:
            _fail("existing integration evidence conflicts with current handoff")
        return
    write_json_immutable(path, value)


def _load_hashed_artifact(
    path: Path,
    *,
    artifact_type: str,
    label: str,
) -> dict[str, Any]:
    artifact = load_json(path)
    if not isinstance(artifact, dict) or artifact.get("artifact_type") != (
        artifact_type
    ):
        _fail(f"{label} type is invalid")
    supplied_hash = artifact.get("artifact_hash")
    candidate = deepcopy(artifact)
    candidate.pop("artifact_hash", None)
    if supplied_hash != replay_hash(candidate):
        _fail(f"{label} hash differs")
    return artifact


def _inside_root(value: Any, root: Path, label: str) -> Path:
    path = Path(_text(value, label)).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError:
        _fail(f"{label} leaves the committed Objective execution root")
    return path


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _fail(f"{name} is required")
    return value.strip()


def _fail(message: str) -> None:
    raise FailClosedRuntimeError(f"G60-02 integration failed closed: {message}")


__all__ = [
    "COMPLETE_PIPELINE_RETURNED_TO_AICLI",
    "EXECUTION_PREPARED_AWAITING_AUTHORIZATION",
    "FIRST_COMPLETE_CONVERSATION_EXECUTION_INTEGRATION_V2",
    "admit_committed_objective_to_platform_core_v2",
    "authorize_pending_committed_objective_execution_v2",
    "authorize_and_execute_prepared_objective_v2",
    "prepare_committed_objective_execution_v2",
    "reconstruct_committed_objective_execution_preparation_v2",
    "run_complete_conversation_execution_terminal_v2",
    "validate_committed_objective_admission_transport_v2",
]
