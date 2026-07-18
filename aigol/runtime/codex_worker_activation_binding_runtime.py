"""One-time G31 binding from governed evidence to bounded Codex activation."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from typing import Any, Callable

from aigol.runtime.approved_durable_work_repository_scope_grounding import (
    validate_approved_durable_work_repository_scope_grounding,
)
from aigol.runtime.codex_worker_platform_integration import (
    CODEX_COGNITION_PROVIDER_ID,
    CODEX_EXECUTION_WORKER_ID,
)
from aigol.runtime.confirmed_grounded_execution_authorization_binding import (
    reconstruct_confirmed_grounded_execution_ready_replay,
)
from aigol.runtime.execution_authorization_runtime import (
    EXECUTION_AUTHORIZED,
    reconstruct_execution_authorization_replay,
)
from aigol.runtime.execution_summary_runtime import create_execution_summary, verify_execution_summary
from aigol.runtime.governed_implementation_request_runtime import APPROVED, HUMAN_APPROVAL_ARTIFACT_V1
from aigol.runtime.governed_worker_execution_runtime import (
    WORKER_EXECUTION_COMPLETED,
    reconstruct_governed_worker_execution_replay,
)
from aigol.runtime.grounded_execution_authorization_human_decision_binding import (
    EXECUTION_DECISION_APPROVED,
    reconstruct_distinct_human_execution_decision,
    validate_distinct_human_execution_decision,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import (
    load_json,
    replay_hash,
    verify_replay_hash,
    write_json_immutable,
)
from aigol.runtime.unified_resource_selection_runtime import (
    RESOURCE_SELECTION_SUCCEEDED,
    WORKER_ROLE,
    reconstruct_unified_resource_selection_replay,
)
from aigol.runtime.worker_invocation_runtime import (
    WORKER_INVOKED,
    reconstruct_worker_invocation_replay,
)
from aigol.runtime.worker_invocation_to_execution_candidate_bridge_runtime import (
    WORKER_EXECUTION_CANDIDATE_CREATED,
    reconstruct_worker_invocation_to_execution_candidate_bridge_replay,
)
from sapianta_system.runtime.codex_execution_adapter import (
    create_codex_execution_request,
    execute_governed_codex,
)
from sapianta_system.runtime.codex_execution_adapter.governed_codex_execution_receipt import (
    create_codex_execution_receipt,
)
from sapianta_system.runtime.codex_execution_adapter.governed_codex_execution_replay import (
    build_codex_execution_replay_identity,
)
from sapianta_system.runtime.codex_handoff import (
    create_governed_codex_handoff,
    create_governed_codex_handoff_request,
)
from sapianta_system.runtime.codex_synthesis import (
    create_governed_codex_task_request,
    create_governed_codex_worker_execution_contract,
    synthesize_governed_codex_task,
)
from sapianta_system.runtime.execution_gate import (
    authorize_downstream_execution,
    create_execution_authorization_request,
)


RUNTIME_VERSION = "G31_21B_CODEX_WORKER_PROMPT_FIDELITY_BINDING_V1"
ACTIVATION_APPROVAL_SCOPE = "RUN_BOUNDED_CODEX_WORKER_PROCESS_ONLY"
CODEX_EXECUTABLE = "codex"
ACTIVATION_TIMEOUT_SECONDS = 60
CODEX_SYNTHESIS_PREFIX = "runtime validation: "
CODEX_SYNTHESIS_MAXIMUM_CHARACTER_COUNT = 240
LEGACY_TASK_OUTCOME_CRITERIA_VERSION = "G31_PRE_EXECUTION_TASK_OUTCOME_CRITERIA_V1"
TASK_OUTCOME_CRITERIA_VERSION = "G31_PRE_EXECUTION_TASK_OUTCOME_CRITERIA_V2"
REPLAY_STEPS = (
    "worker_activation_review_recorded",
    "worker_activation_approval_recorded",
    "worker_activation_transport_receipt_recorded",
)
SCOPE = {
    "worker_process_activation_allowed": True,
    "fixed_codex_exec_command_allowed": True,
    "bounded_transport_receipt_allowed": True,
    "provider_invocation_allowed": False,
    "worker_result_capture_allowed": False,
    "repository_mutation_allowed": False,
}
ACTIVATION_TRUTH_FIELDS = (
    "third_human_decision_recorded", "worker_process_activation_allowed",
    "worker_process_started", "subprocess_invoked", "fixed_codex_exec_command_used",
    "transport_receipt_created", "provider_invoked", "semantic_worker_result_captured",
    "result_accepted", "command_authority_broadened", "repository_mutated",
    "worker_prompt_fidelity_verified", "authorized_task_is_primary",
    "grounded_implementation_target_present", "grounded_test_target_present",
    "requested_output_type", "file_mutation_allowed",
)


def preflight_codex_worker_synthesis(
    original_request: str,
    *,
    worker_execution_contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Use the canonical synthesis owner for admission or grounded activation."""

    raw = _required(original_request, "original_request")
    final = f"{CODEX_SYNTHESIS_PREFIX}{raw}"
    contract = deepcopy(worker_execution_contract)
    synthesis_request = create_governed_codex_task_request(
        natural_language=final,
        worker_execution_contract=contract,
    )
    synthesis = synthesize_governed_codex_task(synthesis_request)
    within_bound = len(final) <= CODEX_SYNTHESIS_MAXIMUM_CHARACTER_COUNT
    handoff = (
        create_governed_codex_handoff(
            create_governed_codex_handoff_request(
                synthesis_response=synthesis,
                original_human_request=raw,
            )
        )
        if synthesis.get("status") == "SYNTHESIZED"
        else None
    )
    prompt = synthesis.get("codex_prompt_preview") if isinstance(synthesis, dict) else None
    prompt_hash = (
        sha256(prompt.encode("utf-8")).hexdigest()
        if isinstance(prompt, str) and prompt
        else None
    )
    grounded_targets = contract.get("grounded_targets", []) if isinstance(contract, dict) else []
    target_roles = {
        item.get("target_role") for item in grounded_targets if isinstance(item, dict)
    }
    faithful = bool(
        isinstance(contract, dict)
        and synthesis.get("worker_execution_contract") == contract
        and synthesis.get("bounded_prompt_sha256") == prompt_hash
        and "WORKER ROLE:" in str(prompt)
        and "PRIMARY AUTHORIZED TASK:" in str(prompt)
        and "GROUNDED TARGETS:" in str(prompt)
        and "REQUIRED OUTPUT:" in str(prompt)
        and "Prepare a bounded runtime validation task." not in str(prompt)
        and "Preview-only downstream Codex task formation" not in str(prompt)
    )
    ready = bool(
        within_bound
        and isinstance(handoff, dict)
        and handoff.get("status") == "HANDOFF_READY"
        and handoff.get("codex_prompt") == prompt
        and handoff.get("bounded_prompt_sha256") == prompt_hash
        and (contract is None or faithful)
    )
    value = {
        "runtime_version": RUNTIME_VERSION,
        "synthesis_preflight_performed": True,
        "synthesis_preflight_status": "SYNTHESIS_PREFLIGHT_READY" if ready else "SYNTHESIS_PREFLIGHT_FAILED_CLOSED",
        "synthesis_within_bound": within_bound,
        "raw_request": raw,
        "canonical_prefix": CODEX_SYNTHESIS_PREFIX,
        "final_synthesized_request": final,
        "raw_character_count": len(raw),
        "prefix_character_count": len(CODEX_SYNTHESIS_PREFIX),
        "final_character_count": len(final),
        "maximum_character_count": CODEX_SYNTHESIS_MAXIMUM_CHARACTER_COUNT,
        "character_counting_contract": "PYTHON_UNICODE_CODE_POINTS",
        "final_synthesized_request_sha256": sha256(final.encode("utf-8")).hexdigest(),
        "worker_execution_contract": contract,
        "worker_execution_contract_hash": replay_hash(contract) if contract is not None else None,
        "bounded_codex_prompt": prompt,
        "bounded_codex_prompt_sha256": prompt_hash,
        "bounded_codex_prompt_character_count": len(prompt) if isinstance(prompt, str) else 0,
        "worker_prompt_fidelity_verified": faithful,
        "authorized_task_is_primary": faithful,
        "grounded_implementation_target_present": "IMPLEMENTATION" in target_roles,
        "grounded_test_target_present": "FOCUSED_TEST" in target_roles,
        "requested_output_type": contract.get("requested_output_type") if isinstance(contract, dict) else None,
        "file_mutation_allowed": False,
        "governed_codex_task_request": deepcopy(synthesis_request),
        "governed_codex_synthesis_response": deepcopy(synthesis),
        "governed_codex_handoff": deepcopy(handoff),
        "human_decision_count": 0,
        "process_start_count": 0,
        "provider_invoked": False,
        "repository_mutated": False,
    }
    value["synthesis_preflight_hash"] = replay_hash(value)
    return value


def render_codex_worker_synthesis_preflight(capture: dict[str, Any]) -> str:
    """Render canonical preflight evidence without giving AiCLI authority."""

    return "\n".join((
        "Bounded CODEX synthesis preflight",
        f"Status: {capture.get('synthesis_preflight_status')}",
        f"Raw characters: {capture.get('raw_character_count')}",
        f"Canonical prefix characters: {capture.get('prefix_character_count')}",
        f"Final characters: {capture.get('final_character_count')}",
        f"Maximum characters: {capture.get('maximum_character_count')}",
        f"Within bound: {capture.get('synthesis_within_bound')}",
        f"Final request SHA-256: {capture.get('final_synthesized_request_sha256')}",
        "No human decision or Worker process has occurred.",
    ))


def _verified_synthesis_preflight(
    original_request: str,
    supplied: dict[str, Any] | None = None,
    *,
    worker_execution_contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    expected = preflight_codex_worker_synthesis(
        original_request,
        worker_execution_contract=worker_execution_contract,
    )
    if supplied is not None and supplied != expected:
        raise FailClosedRuntimeError("Codex synthesis preflight or request was substituted")
    if not all((
        expected["synthesis_preflight_performed"] is True,
        expected["synthesis_within_bound"] is True,
        expected["raw_character_count"] + expected["prefix_character_count"]
        == expected["final_character_count"],
        expected["final_character_count"] <= expected["maximum_character_count"]
        == CODEX_SYNTHESIS_MAXIMUM_CHARACTER_COUNT,
        expected["canonical_prefix"] == CODEX_SYNTHESIS_PREFIX,
        expected["final_synthesized_request"]
        == f"{CODEX_SYNTHESIS_PREFIX}{original_request}",
        expected["synthesis_preflight_hash"]
        == replay_hash({key: value for key, value in expected.items() if key != "synthesis_preflight_hash"}),
        isinstance(expected["governed_codex_handoff"], dict),
        expected["governed_codex_handoff"].get("status") == "HANDOFF_READY",
        expected["governed_codex_handoff"].get("codex_prompt")
        == expected["bounded_codex_prompt"],
        expected["governed_codex_handoff"].get("bounded_prompt_sha256")
        == expected["bounded_codex_prompt_sha256"],
        worker_execution_contract is None
        or all((
            expected["worker_execution_contract"] == worker_execution_contract,
            expected["worker_prompt_fidelity_verified"] is True,
            expected["authorized_task_is_primary"] is True,
            expected["grounded_implementation_target_present"] is True,
            expected["grounded_test_target_present"] is True,
            expected["file_mutation_allowed"] is False,
        )),
    )):
        raise FailClosedRuntimeError("Codex synthesis preflight failed closed")
    return expected


def prepare_codex_worker_activation_review(
    *,
    governed_execution_capture: dict[str, Any],
    execution_candidate_capture: dict[str, Any],
    session_root: str | Path,
    workspace: str | Path,
    created_at: str,
    synthesis_preflight_capture: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Reconstruct G31 evidence and form a non-authoritative third review."""

    lineage = _reconstruct_lineage(
        governed_execution_capture, execution_candidate_capture, session_root, workspace
    )
    candidate = lineage["candidate"]
    result = lineage["governed_result"]
    admission_preflight = _verified_synthesis_preflight(
        lineage["original_request"], synthesis_preflight_capture
    )
    worker_contract = _grounded_worker_execution_contract(lineage)
    preflight = _verified_synthesis_preflight(
        lineage["original_request"],
        worker_execution_contract=worker_contract,
    )
    review = create_execution_summary(
        summary_id=f"{result['worker_execution_id']}:CODEX-WORKER-ACTIVATION-REVIEW",
        original_request=lineage["original_request"],
        interpreted_intent={
            "intent_type": ACTIVATION_APPROVAL_SCOPE,
            "source_execution_candidate": candidate["execution_candidate_id"],
            "source_governed_execution": result["worker_execution_id"],
            "request_admission_preflight_hash": admission_preflight[
                "synthesis_preflight_hash"
            ],
            "synthesis_preflight_hash": preflight["synthesis_preflight_hash"],
            "synthesis_request_replay_identity": preflight["governed_codex_task_request"]["replay_identity"],
            "synthesis_response_replay_identity": preflight["governed_codex_synthesis_response"]["replay_identity"],
            "final_synthesized_request_sha256": preflight["final_synthesized_request_sha256"],
            "bounded_codex_prompt_sha256": preflight[
                "bounded_codex_prompt_sha256"
            ],
            "worker_execution_contract_hash": preflight[
                "worker_execution_contract_hash"
            ],
            "worker_role": worker_contract["worker_role"],
            "grounded_targets": deepcopy(worker_contract["grounded_targets"]),
            "requested_output_type": worker_contract["requested_output_type"],
            "worker_constraints": deepcopy(worker_contract["constraints"]),
            "task_outcome_criteria_hash": worker_contract[
                "task_outcome_criteria"
            ]["criteria_hash"],
            "final_character_count": preflight["final_character_count"],
            "maximum_character_count": preflight["maximum_character_count"],
        },
        selected_route={
            "selected_resource_id": "CODEX",
            "registered_worker_id": CODEX_EXECUTION_WORKER_ID,
            "role_type": WORKER_ROLE,
            "process_adapter": "execute_governed_codex",
        },
        planned_actions=["RUN_EXACTLY_ONE_BOUNDED_CODEX_EXEC_PROCESS"],
        expected_outputs=["BOUNDED_CODEX_TRANSPORT_RECEIPT_ONLY"],
        assumptions=["The third decision applies only to this exact reconstructed lineage."],
        constraints=[
            "Provider invocation and Provider-role substitution remain prohibited.",
            "Semantic result capture and repository mutation remain prohibited.",
            "No retry, fallback, arbitrary arguments, or hidden continuation is allowed.",
        ],
        risk_classification={
            "risk_level": "ACTUAL_WORKER_PROCESS_ACTIVATION",
            "human_decision_required": True,
        },
        execution_scope={
            "approval_scope": ACTIVATION_APPROVAL_SCOPE,
            "workspace_root": str(Path(workspace).resolve()),
            "command_vector_prefix": [CODEX_EXECUTABLE, "exec"],
            "timeout_seconds": ACTIVATION_TIMEOUT_SECONDS,
            **deepcopy(SCOPE),
        },
        replay_references=lineage["replay_references"],
        created_by="PLATFORM_CORE_G31_CODEX_WORKER_ACTIVATION_BINDING",
        created_at=_required(created_at, "created_at"),
    )
    return {
        "runtime_version": RUNTIME_VERSION,
        "request_admission_preflight_capture": deepcopy(admission_preflight),
        "synthesis_preflight_capture": deepcopy(preflight),
        "activation_review_artifact": review,
        "activation_review_required": True,
        "third_human_decision_recorded": False,
        **deepcopy(SCOPE),
        "worker_process_activation_allowed": False,
        "provider_invoked": False,
        "semantic_worker_result_captured": False,
        "repository_mutated": False,
    }


def activate_bounded_codex_worker(
    *,
    activation_review_artifact: dict[str, Any],
    governed_execution_capture: dict[str, Any],
    execution_candidate_capture: dict[str, Any],
    human_decision: str,
    decided_by: str,
    decided_at: str,
    session_root: str | Path,
    workspace: str | Path,
    replay_dir: str | Path,
    runner: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    """Consume one exact third approval and invoke the existing Codex adapter once."""

    root = Path(session_root).resolve()
    destination = Path(replay_dir).resolve()
    approved_workspace = Path(workspace).resolve()
    if not destination.is_relative_to(root):
        raise FailClosedRuntimeError("Codex activation destination is cross-session")
    _ensure_destination_available(destination)
    lineage = _reconstruct_lineage(
        governed_execution_capture, execution_candidate_capture, root, approved_workspace
    )
    expected = prepare_codex_worker_activation_review(
        governed_execution_capture=governed_execution_capture,
        execution_candidate_capture=execution_candidate_capture,
        session_root=root,
        workspace=approved_workspace,
        created_at=activation_review_artifact.get("created_at", ""),
    )["activation_review_artifact"]
    review = verify_execution_summary(activation_review_artifact)
    if review["artifact_hash"] != expected["artifact_hash"]:
        raise FailClosedRuntimeError("Codex activation review or lineage was substituted")
    if str(human_decision).strip().upper() != "APPROVE":
        raise FailClosedRuntimeError("Codex activation requires an exact third APPROVE decision")
    approval = _activation_approval(review, lineage, decided_by, decided_at)
    _validate_activation_approval(approval, review, lineage)
    _reject_reused_approval(root, approval["approval_id"])

    original = lineage["original_request"]
    worker_contract = _grounded_worker_execution_contract(lineage)
    preflight = _verified_synthesis_preflight(
        original,
        worker_execution_contract=worker_contract,
    )
    handoff = deepcopy(preflight["governed_codex_handoff"])
    authority = authorize_downstream_execution(
        create_execution_authorization_request(
            handoff_package=handoff,
            approved_by="human",
            approval_timestamp=_required(decided_at, "decided_at"),
        )
    )
    if authority.get("status") != "AUTHORIZED":
        raise FailClosedRuntimeError("bounded Codex execution authorization was rejected")
    request = create_codex_execution_request(
        handoff_package=handoff,
        authority_token=authority,
        now=decided_at,
        codex_executable=CODEX_EXECUTABLE,
        timeout_seconds=ACTIVATION_TIMEOUT_SECONDS,
    )

    _persist(destination, 0, review)
    _persist(destination, 1, approval)
    grounding = validate_approved_durable_work_repository_scope_grounding(
        lineage["grounding"], workspace=approved_workspace
    )
    if Path(grounding["workspace_root"]).resolve() != approved_workspace:
        raise FailClosedRuntimeError("approved Codex workspace was substituted")
    before = _repository_snapshot(approved_workspace, root)
    if Path.cwd().resolve() != approved_workspace:
        raise FailClosedRuntimeError("Codex activation requires the exact approved current workspace")

    response = execute_governed_codex(request, runner=runner)
    metadata = response.get("dispatch", {}).get("metadata", {})
    expected_command = [CODEX_EXECUTABLE, "exec", handoff["codex_prompt"]]
    fixed = all((
        response.get("validation", {}).get("valid") is True,
        metadata.get("args") == expected_command,
        metadata.get("shell") is False,
        metadata.get("timeout_seconds") == ACTIVATION_TIMEOUT_SECONDS,
    ))
    if not fixed:
        raise FailClosedRuntimeError("Codex adapter command, shell, or timeout was substituted")
    after = _repository_snapshot(approved_workspace, root)
    mutated = before != after
    returncode = response.get("dispatch", {}).get("returncode")
    process_started = returncode != 125 and response.get("status") in {
        "EXECUTION_ACCEPTED", "EXECUTION_FAILURE", "EXECUTION_TIMEOUT"
    }
    truth = {
        "third_human_decision_recorded": True,
        "worker_process_activation_allowed": True,
        "worker_process_started": process_started,
        "subprocess_invoked": True,
        "fixed_codex_exec_command_used": True,
        "transport_receipt_created": True,
        "provider_invoked": False,
        "semantic_worker_result_captured": False,
        "result_accepted": False,
        "command_authority_broadened": False,
        "repository_mutated": mutated,
        "worker_prompt_fidelity_verified": True,
        "authorized_task_is_primary": True,
        "grounded_implementation_target_present": True,
        "grounded_test_target_present": True,
        "requested_output_type": worker_contract["requested_output_type"],
        "file_mutation_allowed": False,
        "bounded_codex_prompt_sha256": preflight["bounded_codex_prompt_sha256"],
        "worker_execution_contract_hash": preflight[
            "worker_execution_contract_hash"
        ],
        "process_start_count": 1 if process_started else 0,
        "approved_workspace": str(approved_workspace),
        "codex_execution_request_id": request["codex_execution_request_id"],
        "codex_execution_request_replay_identity": request["replay_identity"],
        "codex_execution_response_replay_identity": response["replay_identity"],
        "repository_snapshot_before": before,
        "repository_snapshot_after": after,
    }
    _persist(destination, 2, response["receipt"], activation_truth=truth)
    if mutated:
        raise FailClosedRuntimeError("Codex activation changed approved repository content")
    return {
        "runtime_version": RUNTIME_VERSION,
        "activation_status": response["status"],
        "synthesis_preflight_capture": deepcopy(preflight),
        "activation_review_artifact": deepcopy(review),
        "activation_approval_artifact": deepcopy(approval),
        "execution_authority_token": deepcopy(authority),
        "codex_execution_request": deepcopy(request),
        "codex_transport_receipt": deepcopy(response["receipt"]),
        "bounded_dispatch": deepcopy(response["dispatch"]),
        "activation_replay_reference": str(destination),
        "approved_workspace": str(approved_workspace),
        **truth,
    }


def reconstruct_codex_worker_activation_binding(
    *,
    activation_capture: dict[str, Any],
    governed_execution_capture: dict[str, Any],
    execution_candidate_capture: dict[str, Any],
    session_root: str | Path,
    workspace: str | Path,
) -> dict[str, Any]:
    """Revalidate one supplied activation capture against its complete G31 lineage."""

    root = Path(session_root).resolve()
    approved_workspace = Path(workspace).resolve()
    replay_path = Path(activation_capture.get("activation_replay_reference", "")).resolve()
    if not replay_path.is_relative_to(root):
        raise FailClosedRuntimeError("Codex activation binding is cross-session")
    lineage = _reconstruct_lineage(
        governed_execution_capture, execution_candidate_capture, root, approved_workspace
    )
    captured_contract = (
        activation_capture.get("synthesis_preflight_capture", {})
        .get("worker_execution_contract", {})
    )
    captured_criteria_version = (
        captured_contract.get("task_outcome_criteria", {})
        .get("criteria_version")
    )
    worker_contract = _grounded_worker_execution_contract(
        lineage,
        criteria_version=captured_criteria_version,
    )
    preflight = _verified_synthesis_preflight(
        lineage["original_request"],
        worker_execution_contract=worker_contract,
    )
    if activation_capture.get("synthesis_preflight_capture") != preflight:
        raise FailClosedRuntimeError(
            "Codex activation synthesis preflight or task-outcome criteria was substituted"
        )
    reconstructed = reconstruct_codex_worker_activation_replay(replay_path)
    wrappers = [
        load_json(replay_path / f"{index:03d}_{step}.json")
        for index, step in enumerate(REPLAY_STEPS)
    ]
    review, approval, receipt = (wrapper["artifact"] for wrapper in wrappers)
    if activation_capture.get("activation_review_artifact") != review:
        raise FailClosedRuntimeError("Codex activation review capture mismatch")
    if activation_capture.get("activation_approval_artifact") != approval:
        raise FailClosedRuntimeError("Codex activation approval capture mismatch")
    if replay_hash(activation_capture.get("codex_transport_receipt")) != replay_hash(receipt):
        raise FailClosedRuntimeError("Codex activation receipt capture mismatch")
    _validate_activation_approval(approval, verify_execution_summary(review), lineage)
    request = activation_capture.get("codex_execution_request")
    authority = activation_capture.get("execution_authority_token")
    dispatch = activation_capture.get("bounded_dispatch")
    if not all(isinstance(value, dict) for value in (request, authority, dispatch)):
        raise FailClosedRuntimeError("Codex activation process binding is incomplete")
    rebuilt_request = create_codex_execution_request(
        handoff_package=request.get("handoff_package", {}),
        authority_token=authority,
        now=request.get("now", ""),
        revoked_token_ids=set(request.get("revoked_token_ids", [])),
        codex_executable=CODEX_EXECUTABLE,
        timeout_seconds=ACTIVATION_TIMEOUT_SECONDS,
    )
    if rebuilt_request != request:
        raise FailClosedRuntimeError("Codex activation process request was substituted")
    expected_receipt = create_codex_execution_receipt(
        authority_token=authority,
        execution_status=activation_capture.get("activation_status", ""),
        validation=receipt.get("validation_outcome", {}),
        dispatch=dispatch,
    )
    if expected_receipt != receipt:
        raise FailClosedRuntimeError("Codex activation receipt or output hash mismatch")
    response_identity = build_codex_execution_replay_identity(
        request=request, validation=receipt["validation_outcome"], dispatch=dispatch
    )
    truth = wrappers[2].get("activation_truth") or {}
    interpreted = review.get("interpreted_intent") or {}
    exact_prompt = preflight["bounded_codex_prompt"]
    exact_prompt_hash = preflight["bounded_codex_prompt_sha256"]
    checks = (
        reconstructed.get("replay_artifact_count") == 3,
        truth.get("codex_execution_request_id") == request["codex_execution_request_id"],
        truth.get("codex_execution_request_replay_identity") == request["replay_identity"],
        truth.get("codex_execution_response_replay_identity") == response_identity,
        truth.get("approved_workspace") == str(approved_workspace),
        review.get("execution_scope", {}).get("workspace_root") == str(approved_workspace),
        review.get("execution_scope", {}).get("timeout_seconds") == ACTIVATION_TIMEOUT_SECONDS,
        receipt.get("authority_token_id") == authority.get("token_id"),
        interpreted.get("synthesis_preflight_hash")
        == preflight["synthesis_preflight_hash"],
        interpreted.get("bounded_codex_prompt_sha256") == exact_prompt_hash,
        interpreted.get("worker_execution_contract_hash")
        == preflight["worker_execution_contract_hash"],
        interpreted.get("worker_role") == worker_contract["worker_role"],
        interpreted.get("grounded_targets") == worker_contract["grounded_targets"],
        interpreted.get("requested_output_type")
        == worker_contract["requested_output_type"],
        interpreted.get("worker_constraints") == worker_contract["constraints"],
        interpreted.get("task_outcome_criteria_hash")
        == worker_contract["task_outcome_criteria"]["criteria_hash"],
        approval.get("bounded_codex_prompt_sha256") == exact_prompt_hash,
        approval.get("worker_execution_contract_hash")
        == preflight["worker_execution_contract_hash"],
        request.get("handoff_package") == preflight["governed_codex_handoff"],
        request.get("bounded_prompt_sha256") == exact_prompt_hash,
        authority.get("bounded_prompt_sha256") == exact_prompt_hash,
        receipt.get("bounded_prompt_sha256") == exact_prompt_hash,
        dispatch.get("metadata", {}).get("args")
        == [CODEX_EXECUTABLE, "exec", exact_prompt],
        truth.get("bounded_codex_prompt_sha256") == exact_prompt_hash,
        truth.get("worker_execution_contract_hash")
        == preflight["worker_execution_contract_hash"],
        truth.get("worker_prompt_fidelity_verified") is True,
        truth.get("authorized_task_is_primary") is True,
        truth.get("grounded_implementation_target_present") is True,
        truth.get("grounded_test_target_present") is True,
        truth.get("file_mutation_allowed") is False,
        activation_capture.get("approved_workspace") == str(approved_workspace),
        activation_capture.get("provider_invoked") is False,
        activation_capture.get("repository_mutated") is False,
        truth.get("repository_snapshot_before") == truth.get("repository_snapshot_after"),
        truth.get("repository_snapshot_after") == _repository_snapshot(approved_workspace, root),
    )
    if not all(checks):
        raise FailClosedRuntimeError("Codex activation authority, workspace, or identity mismatch")
    validate_approved_durable_work_repository_scope_grounding(
        lineage["grounding"], workspace=approved_workspace
    )
    return {
        "lineage": lineage,
        "activation_review_artifact": deepcopy(review),
        "activation_approval_artifact": deepcopy(approval),
        "transport_receipt": deepcopy(receipt),
        "bounded_dispatch": deepcopy(dispatch),
        "codex_execution_request": deepcopy(request),
        "activation_replay_reference": str(replay_path),
        "activation_replay_hash": reconstructed["replay_hash"],
        "activation_truth": deepcopy(truth),
    }


def reconstruct_codex_worker_activation_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct the activation review, third approval, and transport receipt."""

    root = Path(replay_dir)
    wrappers = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(root / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("Codex activation Replay ordering mismatch")
        verify_replay_hash(wrapper)
        wrappers.append(wrapper)
    review = verify_execution_summary(wrappers[0].get("artifact"))
    approval = wrappers[1].get("artifact")
    _verify_artifact(approval)
    if approval.get("activation_review_hash") != review["artifact_hash"]:
        raise FailClosedRuntimeError("Codex activation Replay approval continuity mismatch")
    receipt = wrappers[2].get("artifact")
    if not isinstance(receipt, dict) or not receipt.get("receipt_id") or not receipt.get("replay_identity"):
        raise FailClosedRuntimeError("Codex activation Replay receipt is invalid")
    if not all((
        approval.get("bounded_codex_prompt_sha256"),
        approval.get("bounded_codex_prompt_sha256")
        == receipt.get("bounded_prompt_sha256"),
    )):
        raise FailClosedRuntimeError("Codex activation Replay prompt continuity mismatch")
    truth = wrappers[2].get("activation_truth")
    if not isinstance(truth, dict) or truth.get("transport_receipt_created") is not True:
        raise FailClosedRuntimeError("Codex activation Replay truth is incomplete")
    return {
        "activation_review_hash": review["artifact_hash"],
        "activation_approval_hash": approval["artifact_hash"],
        "transport_receipt_id": receipt["receipt_id"],
        "replay_artifact_count": 3,
        "replay_hash": replay_hash(wrappers),
        **deepcopy(truth),
    }


def render_codex_worker_activation_review(capture: dict[str, Any]) -> str:
    review = capture.get("activation_review_artifact") or {}
    preflight = capture.get("synthesis_preflight_capture") or {}
    contract = preflight.get("worker_execution_contract") or {}
    return "\n".join((
        "Bounded CODEX Worker Process Activation Review",
        f"Approval Scope: {ACTIVATION_APPROVAL_SCOPE}",
        f"Review Reference: {review.get('summary_id')}",
        f"Execution Timeout: {ACTIVATION_TIMEOUT_SECONDS} seconds (finite; no retry).",
        f"Worker Prompt SHA-256: {preflight.get('bounded_codex_prompt_sha256')}",
        f"Grounded Targets: {contract.get('grounded_targets')}",
        f"Requested Output: {contract.get('requested_output_type')}",
        "The next exact /approve permits one fixed codex exec process and one bounded transport receipt.",
        "Provider invocation, semantic result capture, and repository mutation remain prohibited.",
    ))


def render_codex_worker_activation_result(capture: dict[str, Any]) -> str:
    return "\n".join((
        "Bounded CODEX Worker Process Activation",
        f"Process Status: {capture.get('activation_status')}",
        f"Worker Process Started: {capture.get('worker_process_started')}",
        f"Transport Receipt: {(capture.get('codex_transport_receipt') or {}).get('receipt_id')}",
        "No Provider was invoked; no semantic Worker result was captured or accepted.",
        "Repository mutation remained prohibited and was not observed.",
    ))


def _reconstruct_lineage(governed: dict[str, Any], candidate_capture: dict[str, Any], session_root: str | Path, workspace: str | Path) -> dict[str, Any]:
    root, approved_workspace = Path(session_root).resolve(), Path(workspace).resolve()
    governed_path = Path(governed.get("worker_execution_replay_reference", "")).resolve()
    candidate_path = Path(candidate_capture.get("worker_execution_candidate_replay_reference", "")).resolve()
    if any(not path.is_relative_to(root) for path in (governed_path, candidate_path)):
        raise FailClosedRuntimeError("Codex activation lineage is cross-session")
    governed_reconstruction = reconstruct_governed_worker_execution_replay(governed_path)
    governed_wrapper = load_json(governed_path / "001_worker_execution_result_recorded.json")
    verify_replay_hash(governed_wrapper)
    result = governed_wrapper.get("artifact")
    _verify_artifact(result)
    supplied_result = governed.get("worker_execution_result_artifact")
    _verify_artifact(supplied_result)
    if not all((
        isinstance(supplied_result, dict),
        supplied_result.get("artifact_hash") == result["artifact_hash"],
        governed_reconstruction["execution_status"] == WORKER_EXECUTION_COMPLETED,
        result.get("worker_evidence", {}).get("subprocess_invoked") is False,
        result.get("provider_invoked") is False,
    )):
        raise FailClosedRuntimeError("incoming governed-execution evidence is not activation-eligible")
    candidate_reconstruction = reconstruct_worker_invocation_to_execution_candidate_bridge_replay(candidate_path)
    candidate_wrapper = load_json(candidate_path / "001_worker_invocation_execution_candidate_recorded.json")
    verify_replay_hash(candidate_wrapper)
    candidate = candidate_wrapper.get("artifact")
    _verify_artifact(candidate)
    supplied_candidate = candidate_capture.get("worker_execution_candidate_artifact")
    _verify_artifact(supplied_candidate)
    if not all((
        isinstance(supplied_candidate, dict),
        supplied_candidate.get("artifact_hash") == candidate["artifact_hash"],
        candidate_reconstruction["candidate_status"] == WORKER_EXECUTION_CANDIDATE_CREATED,
        result.get("source_execution_candidate") == candidate["execution_candidate_id"],
        result.get("source_execution_candidate_hash") == candidate["artifact_hash"],
    )):
        raise FailClosedRuntimeError("Codex activation candidate identity mismatch")
    references = [Path(value).resolve() for value in candidate.get("replay_references", [])]
    if not references or any(not path.is_relative_to(root) for path in references):
        raise FailClosedRuntimeError("Codex activation candidate Replay is cross-session")
    invocation_path = _one(references, "002_invocation_artifact_recorded.json")
    authorization_path = _one(references, "002_authorization_artifact_recorded.json")
    ready_path = _one(references, "000_execution_candidate_recorded.json")
    request_path = _one(references, "002_invocation_request_artifact_recorded.json")
    invocation = reconstruct_worker_invocation_replay(invocation_path)
    authorization = reconstruct_execution_authorization_replay(authorization_path)
    ready = reconstruct_confirmed_grounded_execution_ready_replay(ready_path)
    if not all((
        invocation["invocation_status"] == WORKER_INVOKED,
        invocation["worker_id"] == "CODEX",
        authorization["authorization_status"] == EXECUTION_AUTHORIZED,
    )):
        raise FailClosedRuntimeError("Codex Worker invocation or execution authorization mismatch")
    request_wrapper = load_json(request_path / "002_invocation_request_artifact_recorded.json")
    verify_replay_hash(request_wrapper)
    request_artifact = request_wrapper.get("artifact") or {}
    selection_reference = (request_artifact.get("g31_lineage") or {}).get(
        "resource_selection_replay_reference", ""
    )
    selection_path = Path(selection_reference).resolve()
    if not selection_path.is_relative_to(root):
        raise FailClosedRuntimeError("Codex Worker selection Replay is cross-session")
    selection = reconstruct_unified_resource_selection_replay(selection_path)
    identity = candidate.get("worker_identity", {})
    if not all((
        selection["selection_status"] == RESOURCE_SELECTION_SUCCEEDED,
        selection["selected_resource_id"] == "CODEX",
        selection["selected_role_type"] == WORKER_ROLE,
        identity.get("worker_id") == "CODEX",
        identity.get("worker_role") == invocation["worker_role"],
        CODEX_EXECUTION_WORKER_ID == "codex-execution",
        CODEX_COGNITION_PROVIDER_ID != CODEX_EXECUTION_WORKER_ID,
    )):
        raise FailClosedRuntimeError("CODEX selection cannot be substituted with Provider authority")
    ready_wrapper = load_json(ready_path / "000_execution_candidate_recorded.json")
    verify_replay_hash(ready_wrapper)
    decision = validate_distinct_human_execution_decision(
        ready_wrapper["artifact"]["source_human_execution_decision_artifact"],
        workspace=approved_workspace, session_root=root,
    )
    reconstructed_decision = reconstruct_distinct_human_execution_decision(
        decision["replay_reference"], workspace=approved_workspace, session_root=root
    )
    grounding = validate_approved_durable_work_repository_scope_grounding(
        decision["source_authorization_review_artifact"]["source_repository_scope_grounding_artifact"],
        workspace=approved_workspace,
    )
    if not all((
        decision["decision_status"] == EXECUTION_DECISION_APPROVED,
        reconstructed_decision["artifact_hash"] == decision["artifact_hash"],
        Path(grounding["workspace_root"]).resolve() == approved_workspace,
    )):
        raise FailClosedRuntimeError("Codex activation human decisions or grounding mismatch")
    original = decision["source_authorization_review_artifact"]["execution_summary_artifact"]["original_request"]
    return {
        "candidate": candidate, "governed_result": result, "grounding": grounding,
        "invocation": deepcopy(load_json(invocation_path / "002_invocation_artifact_recorded.json")["artifact"]),
        "invocation_replay_reference": str(invocation_path),
        "decision": decision, "original_request": _required(original, "original_request"),
        "replay_references": [str(path) for path in references] + [str(candidate_path), str(governed_path)],
    }


def _grounded_worker_execution_contract(
    lineage: dict[str, Any],
    *,
    criteria_version: str | None = None,
) -> dict[str, Any]:
    """Project the exact approved task and grounded pair into Worker instructions."""

    grounding = lineage.get("grounding") or {}
    evidence = grounding.get("target_evidence")
    if not isinstance(evidence, list) or len(evidence) != 2:
        raise FailClosedRuntimeError(
            "Codex Worker prompt requires exactly one grounded implementation/test pair"
        )
    role_map = {"SOURCE": "IMPLEMENTATION", "FOCUSED_TEST": "FOCUSED_TEST"}
    targets = []
    for item in evidence:
        if not isinstance(item, dict) or item.get("target_role") not in role_map:
            raise FailClosedRuntimeError("Codex Worker prompt target role mismatch")
        targets.append({
            "target_role": role_map[item["target_role"]],
            "target_path": _required(item.get("target_path"), "grounded target path"),
            "target_evidence_hash": _required(
                item.get("target_evidence_hash"), "grounded target evidence hash"
            ),
        })
    if {item["target_role"] for item in targets} != {"IMPLEMENTATION", "FOCUSED_TEST"}:
        raise FailClosedRuntimeError("Codex Worker prompt grounded roles are incomplete")
    if len({item["target_path"] for item in targets}) != 2:
        raise FailClosedRuntimeError("Codex Worker prompt grounded targets are duplicated")
    original = _required(lineage.get("original_request"), "original_request")
    output_type = (
        "UNIFIED_DIFF" if "unified diff" in original.casefold()
        else "AUTHORIZED_TASK_RESULT"
    )
    contract = create_governed_codex_worker_execution_contract(
        authorized_task=original,
        grounded_targets=targets,
        requested_output_type=output_type,
    )
    version = criteria_version or TASK_OUTCOME_CRITERIA_VERSION
    if version not in {
        LEGACY_TASK_OUTCOME_CRITERIA_VERSION,
        TASK_OUTCOME_CRITERIA_VERSION,
    }:
        raise FailClosedRuntimeError("Codex Worker task-outcome criteria version mismatch")
    criteria = {
        "criteria_version": version,
        "established_stage": "BEFORE_THIRD_HUMAN_ACTIVATION_DECISION",
        "established_before_worker_execution": True,
        "authorized_task": original,
        "authorized_task_sha256": sha256(original.encode("utf-8")).hexdigest(),
        "required_output_type": output_type,
        "grounded_targets": deepcopy(targets),
        "human_judgment_required": True,
        "result_acceptance_separate": True,
        "repository_mutation_authority": False,
    }
    if version == LEGACY_TASK_OUTCOME_CRITERIA_VERSION:
        criteria["requirements"] = [
            "HUMAN_MUST_REVIEW_EXACT_OUTPUT_AGAINST_EXACT_AUTHORIZED_TASK",
            "OUTPUT_TYPE_MUST_EQUAL_PREAUTHORIZED_OUTPUT_TYPE",
            "OUTPUT_TARGETS_MUST_NOT_EXCEED_GROUNDED_TARGETS",
            "PATCH_MUST_REMAIN_UNAPPLIED_DURING_TASK_OUTCOME_REVIEW",
            "TASK_SATISFACTION_MUST_NOT_IMPLY_RESULT_ACCEPTANCE",
            "TASK_SATISFACTION_MUST_NOT_AUTHORIZE_REPOSITORY_MUTATION",
        ]
    else:
        criteria.update({
            "requirements": [
                "OUTPUT_MUST_BE_SYNTACTICALLY_VALID_UNIFIED_DIFF",
                "AT_LEAST_ONE_GROUNDED_IMPLEMENTATION_TARGET_MUST_CHANGE",
                "EVERY_CHANGED_PATH_MUST_BE_WITHIN_GROUNDED_TARGET_SCOPE",
                "NO_UNGROUNDED_PATH_MAY_CHANGE",
                "REQUESTED_SEMANTIC_CHANGE_MUST_BE_REPRESENTED",
                "PATCH_MUST_REMAIN_UNAPPLIED_DURING_TASK_OUTCOME_REVIEW",
                "TASK_OUTCOME_REVIEW_MUST_NOT_CLAIM_TESTS_PASSED",
                "TECHNICAL_QUALITY_REQUIRES_LATER_APPLICATION_AND_TEST_VALIDATION",
                "TASK_SATISFACTION_MUST_NOT_IMPLY_RESULT_ACCEPTANCE",
                "TASK_SATISFACTION_MUST_NOT_AUTHORIZE_REPOSITORY_MUTATION",
            ],
            "grounded_target_semantics": {
                "inspection_targets": deepcopy(targets),
                "allowed_change_targets": deepcopy(targets),
                "every_grounded_target_must_appear_in_diff": False,
                "every_grounded_target_must_change": False,
                "unchanged_grounded_test_target_allowed": True,
            },
            "inspection_evidence_contract": {
                "unified_diff_proves_file_inspection": False,
                "affirmative_inspection_proof_required_for_task_outcome": False,
                "structured_inspection_evidence_available": False,
                "evidence_gap": (
                    "No canonical structured Worker file-inspection evidence is "
                    "currently bound to the task-outcome review."
                ),
            },
            "test_validation_contract": {
                "tests_may_be_claimed_passed_before_patch_application": False,
                "tests_run_against_applied_patch": False,
                "later_patch_application_required": True,
                "later_test_validation_required": True,
            },
        })
    criteria["criteria_hash"] = replay_hash(criteria)
    contract["task_outcome_criteria"] = criteria
    return contract


def _activation_approval(review: dict[str, Any], lineage: dict[str, Any], decided_by: str, decided_at: str) -> dict[str, Any]:
    result, candidate = lineage["governed_result"], lineage["candidate"]
    interpreted = review.get("interpreted_intent") or {}
    artifact = {
        "artifact_type": HUMAN_APPROVAL_ARTIFACT_V1,
        "approval_id": f"{result['worker_execution_id']}:CODEX-WORKER-ACTIVATION-APPROVAL",
        "approval_status": APPROVED, "approval_granted": True,
        "approval_scope": ACTIVATION_APPROVAL_SCOPE, **deepcopy(SCOPE),
        "activation_review_reference": review["summary_id"],
        "activation_review_hash": review["artifact_hash"],
        "synthesis_preflight_hash": interpreted.get("synthesis_preflight_hash"),
        "final_synthesized_request_sha256": interpreted.get(
            "final_synthesized_request_sha256"
        ),
        "bounded_codex_prompt_sha256": interpreted.get(
            "bounded_codex_prompt_sha256"
        ),
        "worker_execution_contract_hash": interpreted.get(
            "worker_execution_contract_hash"
        ),
        "worker_role": interpreted.get("worker_role"),
        "grounded_targets": deepcopy(interpreted.get("grounded_targets")),
        "requested_output_type": interpreted.get("requested_output_type"),
        "worker_constraints": deepcopy(interpreted.get("worker_constraints")),
        "task_outcome_criteria_hash": interpreted.get(
            "task_outcome_criteria_hash"
        ),
        "timeout_seconds": ACTIVATION_TIMEOUT_SECONDS,
        "source_execution_candidate": candidate["execution_candidate_id"],
        "source_execution_candidate_hash": candidate["artifact_hash"],
        "source_governed_execution": result["worker_execution_id"],
        "source_governed_execution_hash": result["artifact_hash"],
        "selected_resource_id": "CODEX", "registered_worker_id": CODEX_EXECUTION_WORKER_ID,
        "selected_role_type": WORKER_ROLE, "third_human_decision_recorded": True,
        "approved_by": _required(decided_by, "decided_by"),
        "approved_at": _required(decided_at, "decided_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _validate_activation_approval(approval: dict[str, Any], review: dict[str, Any], lineage: dict[str, Any]) -> None:
    _verify_artifact(approval)
    interpreted = review.get("interpreted_intent") or {}
    expected = {
        "artifact_type": HUMAN_APPROVAL_ARTIFACT_V1, "approval_status": APPROVED,
        "approval_granted": True, "approval_scope": ACTIVATION_APPROVAL_SCOPE,
        "activation_review_hash": review["artifact_hash"],
        "synthesis_preflight_hash": interpreted.get("synthesis_preflight_hash"),
        "final_synthesized_request_sha256": interpreted.get(
            "final_synthesized_request_sha256"
        ),
        "bounded_codex_prompt_sha256": interpreted.get(
            "bounded_codex_prompt_sha256"
        ),
        "worker_execution_contract_hash": interpreted.get(
            "worker_execution_contract_hash"
        ),
        "worker_role": interpreted.get("worker_role"),
        "grounded_targets": interpreted.get("grounded_targets"),
        "requested_output_type": interpreted.get("requested_output_type"),
        "worker_constraints": interpreted.get("worker_constraints"),
        "task_outcome_criteria_hash": interpreted.get(
            "task_outcome_criteria_hash"
        ),
        "timeout_seconds": ACTIVATION_TIMEOUT_SECONDS,
        "source_execution_candidate_hash": lineage["candidate"]["artifact_hash"],
        "source_governed_execution_hash": lineage["governed_result"]["artifact_hash"],
        "selected_resource_id": "CODEX", "registered_worker_id": CODEX_EXECUTION_WORKER_ID,
        "selected_role_type": WORKER_ROLE, "third_human_decision_recorded": True,
        **SCOPE,
    }
    if any(approval.get(field) != value for field, value in expected.items()):
        raise FailClosedRuntimeError("Codex activation approval scope or identity mismatch")


def _repository_snapshot(workspace: Path, session_root: Path) -> str:
    evidence = []
    for path in sorted(item for item in workspace.rglob("*") if item.is_file()):
        if ".git" in path.relative_to(workspace).parts or path.is_relative_to(session_root):
            continue
        evidence.append((path.relative_to(workspace).as_posix(), sha256(path.read_bytes()).hexdigest()))
    return replay_hash(evidence)


def _one(paths: list[Path], marker: str) -> Path:
    matches = [path for path in paths if (path / marker).is_file()]
    if len(matches) != 1:
        raise FailClosedRuntimeError(f"Codex activation lineage requires exactly one {marker}")
    return matches[0]


def _persist(root: Path, index: int, artifact: dict[str, Any], *, activation_truth: dict[str, Any] | None = None) -> None:
    step = REPLAY_STEPS[index]
    wrapper = {"event_type": step.upper(), "replay_index": index, "replay_step": step, "artifact": deepcopy(artifact)}
    if activation_truth is not None:
        wrapper["activation_truth"] = deepcopy(activation_truth)
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(root / f"{index:03d}_{step}.json", wrapper)


def _ensure_destination_available(root: Path) -> None:
    if any((root / f"{index:03d}_{step}.json").exists() for index, step in enumerate(REPLAY_STEPS)):
        raise FailClosedRuntimeError("Codex activation Replay destination already exists")


def _reject_reused_approval(root: Path, approval_id: str) -> None:
    for path in root.rglob("001_worker_activation_approval_recorded.json"):
        wrapper = load_json(path)
        if (wrapper.get("artifact") or {}).get("approval_id") == approval_id:
            raise FailClosedRuntimeError("Codex activation approval was already consumed")


def _verify_artifact(artifact: Any) -> None:
    if not isinstance(artifact, dict) or not isinstance(artifact.get("artifact_hash"), str):
        raise FailClosedRuntimeError("Codex activation artifact is invalid")
    value = deepcopy(artifact)
    actual = value.pop("artifact_hash")
    if actual != replay_hash(value):
        raise FailClosedRuntimeError("Codex activation artifact hash mismatch")


def _required(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"Codex activation requires {field}")
    return value.strip()
