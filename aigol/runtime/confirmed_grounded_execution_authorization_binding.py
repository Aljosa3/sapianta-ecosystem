"""Project one confirmed grounded decision into existing execution authorization."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.governed_implementation_dry_run import (
    EXECUTION_CANDIDATE_ARTIFACT_V1,
    EXECUTION_PACKET_ARTIFACT_V1,
    EXECUTION_READY,
    EXECUTION_READY_STATUS_ARTIFACT_V1,
    EXECUTION_VALIDATION_ARTIFACT_V1,
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
    with_replay_hash,
    write_json_immutable,
)


RUNTIME_VERSION = "G31_10_CONFIRMED_GROUNDED_EXECUTION_AUTHORIZATION_BINDING_V1"
REPLAY_STEPS = (
    "execution_candidate_recorded",
    "execution_packet_recorded",
    "execution_validation_recorded",
    "execution_ready_status_recorded",
)
FORBIDDEN_OPERATIONS = (
    "SELECT_WORKER",
    "ASSIGN_WORKER",
    "DISPATCH_WORKER",
    "INVOKE_PROVIDER",
    "INVOKE_WORKER",
    "EXECUTE_COMMAND",
    "MUTATE_REPOSITORY",
)
STOP_BOUNDARIES = {
    "worker_selected": False,
    "worker_dispatched": False,
    "worker_invoked": False,
    "provider_invoked": False,
    "command_executed": False,
    "repository_mutated": False,
}


def authorize_confirmed_grounded_execution_decision(
    *,
    human_execution_decision_artifact: dict[str, Any],
    workspace: str | Path,
    session_root: str | Path,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Authorize the exact confirmed scope without crossing Worker selection."""

    root = Path(session_root).resolve()
    destination = Path(replay_dir).resolve()
    if not destination.is_relative_to(root):
        raise FailClosedRuntimeError("confirmed authorization Replay is cross-session")
    decision = validate_distinct_human_execution_decision(
        human_execution_decision_artifact,
        workspace=workspace,
        session_root=root,
    )
    if decision["decision_status"] != EXECUTION_DECISION_APPROVED:
        raise FailClosedRuntimeError("confirmed authorization requires approved human decision")
    reconstructed = reconstruct_distinct_human_execution_decision(
        decision["replay_reference"],
        workspace=workspace,
        session_root=root,
    )
    if reconstructed["artifact_hash"] != decision["artifact_hash"]:
        raise FailClosedRuntimeError("confirmed authorization decision Replay mismatch")
    for path in root.rglob("001_execution_packet_recorded.json"):
        wrapper = load_json(path)
        verify_replay_hash(wrapper, hash_field="replay_hash")
        packet = wrapper.get("artifact")
        if isinstance(packet, dict) and packet.get(
            "source_human_execution_decision_hash"
        ) == decision["artifact_hash"]:
            raise FailClosedRuntimeError("confirmed authorization decision already consumed")

    review = decision["source_authorization_review_artifact"]
    scope = deepcopy(review["authorization_scope"])
    summary = deepcopy(review["execution_summary_artifact"])
    confirmation = deepcopy(decision["human_confirmation_artifact"])
    ready_root = destination / "execution_ready"
    authorization_root = destination / "authorization"
    chain_id = scope["scope_hash"]
    candidate = {
        "artifact_type": EXECUTION_CANDIDATE_ARTIFACT_V1,
        "runtime_version": RUNTIME_VERSION,
        "candidate_id": f"{decision['artifact_hash']}:CANDIDATE",
        "handoff_reference": scope["grounded_worker_request_reference"],
        "handoff_hash": scope["grounded_worker_request_hash"],
        "chain_id": chain_id,
        "target_domain": "GROUNDED_GOVERNED_DEVELOPMENT",
        "approval_status": "APPROVED",
        "approval_reference": decision["replay_reference"],
        "approval_hash": decision["artifact_hash"],
        "execution_scope": deepcopy(scope),
        "source_human_execution_decision_artifact": deepcopy(decision),
        "source_human_execution_decision_hash": decision["artifact_hash"],
        "created_at": decision["decided_at"],
        "replay_visible": True,
        "execution_started": False,
        **STOP_BOUNDARIES,
    }
    candidate["candidate_hash"] = replay_hash(candidate["execution_scope"])
    candidate = with_replay_hash(candidate, hash_field="artifact_hash")
    packet = {
        "artifact_type": EXECUTION_PACKET_ARTIFACT_V1,
        "runtime_version": RUNTIME_VERSION,
        "packet_id": f"{decision['artifact_hash']}:PACKET",
        "candidate_reference": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "chain_id": chain_id,
        "execution_contract": {
            "contract_type": "EXACT_GROUNDED_SCOPE_AUTHORIZATION",
            "execution_state": "NOT_STARTED",
            "execution_authorized": False,
            "preparation_only": True,
        },
        "authorization_scope": deepcopy(scope),
        "allowed_outputs": deepcopy(scope["repository_targets"]),
        "forbidden_operations": list(FORBIDDEN_OPERATIONS),
        "required_validations": deepcopy(scope["validation_requirements"]),
        "worker_role_requirements": ["GOAL_FAITHFUL_IMPLEMENTATION_WORKER"],
        "source_human_execution_decision_hash": decision["artifact_hash"],
        "created_at": decision["decided_at"],
        "replay_visible": True,
        **STOP_BOUNDARIES,
    }
    packet["packet_hash"] = replay_hash(
        {"candidate_hash": packet["candidate_hash"], "authorization_scope": scope}
    )
    packet = with_replay_hash(packet, hash_field="artifact_hash")
    validation = with_replay_hash(
        {
            "artifact_type": EXECUTION_VALIDATION_ARTIFACT_V1,
            "runtime_version": RUNTIME_VERSION,
            "validation_id": f"{decision['artifact_hash']}:VALIDATION",
            "candidate_hash": candidate["artifact_hash"],
            "packet_hash": packet["artifact_hash"],
            "chain_id": chain_id,
            "approval_hash": decision["artifact_hash"],
            "authorization_scope_hash": scope["scope_hash"],
            "validation_checks": {
                "human_decision_reconstructed": True,
                "summary_confirmation_exact": True,
                "grounded_scope_exact": True,
                "authority_boundary_preserved": True,
            },
            "validation_status": "EXECUTION_READY",
            "created_at": decision["decided_at"],
            "replay_visible": True,
        },
        hash_field="artifact_hash",
    )
    ready = with_replay_hash(
        {
            "artifact_type": EXECUTION_READY_STATUS_ARTIFACT_V1,
            "runtime_version": RUNTIME_VERSION,
            "dry_run_id": f"{decision['artifact_hash']}:READY",
            "execution_status": EXECUTION_READY,
            "candidate_hash": candidate["artifact_hash"],
            "packet_hash": packet["artifact_hash"],
            "validation_hash": validation["artifact_hash"],
            "execution_started": False,
            "created_at": decision["decided_at"],
            "replay_visible": True,
            "failure_reason": None,
        },
        hash_field="artifact_hash",
    )
    for index, (step, artifact) in enumerate(
        zip(REPLAY_STEPS, (candidate, packet, validation, ready))
    ):
        wrapper = with_replay_hash(
            {
                "replay_index": index,
                "replay_step": step,
                "event_type": step.upper(),
                "artifact": artifact,
            },
            hash_field="replay_hash",
        )
        write_json_immutable(ready_root / f"{index:03d}_{step}.json", wrapper)
    reconstruct_confirmed_grounded_execution_ready_replay(ready_root)

    from aigol.runtime.execution_authorization_runtime import (
        EXECUTION_AUTHORIZED,
        authorize_execution_ready,
    )

    capture = authorize_execution_ready(
        authorization_id=f"{decision['artifact_hash']}:AUTHORIZATION",
        execution_ready_replay_reference=str(ready_root),
        authorizing_actor=confirmation["confirmed_by"],
        authorized_at=confirmation["confirmed_at"],
        replay_dir=authorization_root,
        execution_summary_artifact=summary,
        human_confirmation_artifact=confirmation,
    )
    if capture.get("authorization_status") != EXECUTION_AUTHORIZED:
        return capture
    request = capture["authorization_request_artifact"]
    authorization = capture["execution_authorization_artifact"]
    if request["requested_scope"] != scope or authorization["authorized_scope"] != scope:
        raise FailClosedRuntimeError("execution authorization broadened grounded scope")
    capture.update(
        {
            "execution_summary_human_confirmation": True,
            "execution_authorization_request_created": True,
            "execution_authorization_decision_created": True,
            "execution_authorization_artifact_created": True,
            "execution_authorized": True,
            "third_human_confirmation_requested": False,
            **STOP_BOUNDARIES,
            "execution_ready_replay_reference": str(ready_root),
        }
    )
    return capture


def reconstruct_confirmed_grounded_execution_ready_replay(
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Validate the existing execution-ready families and their G31 lineage."""

    root = Path(replay_dir)
    wrappers = [
        load_json(root / f"{index:03d}_{step}.json")
        for index, step in enumerate(REPLAY_STEPS)
    ]
    artifacts = []
    expected_types = (
        EXECUTION_CANDIDATE_ARTIFACT_V1,
        EXECUTION_PACKET_ARTIFACT_V1,
        EXECUTION_VALIDATION_ARTIFACT_V1,
        EXECUTION_READY_STATUS_ARTIFACT_V1,
    )
    for index, (step, wrapper, artifact_type) in enumerate(
        zip(REPLAY_STEPS, wrappers, expected_types)
    ):
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("confirmed execution-ready Replay ordering mismatch")
        verify_replay_hash(wrapper, hash_field="replay_hash")
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict) or artifact.get("artifact_type") != artifact_type:
            raise FailClosedRuntimeError("confirmed execution-ready artifact type mismatch")
        verify_replay_hash(artifact, hash_field="artifact_hash")
        artifacts.append(artifact)
    candidate, packet, validation, ready = artifacts
    decision = validate_distinct_human_execution_decision(
        candidate.get("source_human_execution_decision_artifact"),
        workspace=packet.get("authorization_scope", {}).get("workspace_root"),
    )
    checks = (
        decision["decision_status"] == EXECUTION_DECISION_APPROVED,
        candidate.get("source_human_execution_decision_hash") == decision["artifact_hash"],
        packet.get("source_human_execution_decision_hash") == decision["artifact_hash"],
        candidate.get("artifact_hash") == packet.get("candidate_hash"),
        candidate.get("artifact_hash") == validation.get("candidate_hash"),
        packet.get("artifact_hash") == validation.get("packet_hash"),
        candidate.get("artifact_hash") == ready.get("candidate_hash"),
        packet.get("artifact_hash") == ready.get("packet_hash"),
        validation.get("artifact_hash") == ready.get("validation_hash"),
        candidate.get("execution_scope") == packet.get("authorization_scope"),
        packet.get("authorization_scope", {}).get("scope_hash")
        == validation.get("authorization_scope_hash"),
        ready.get("execution_status") == EXECUTION_READY,
        ready.get("execution_started") is False,
    )
    if not all(checks):
        raise FailClosedRuntimeError("confirmed execution-ready lineage mismatch")
    reconstructed = reconstruct_distinct_human_execution_decision(
        decision["replay_reference"],
        workspace=packet["authorization_scope"]["workspace_root"],
    )
    if reconstructed["artifact_hash"] != decision["artifact_hash"]:
        raise FailClosedRuntimeError("confirmed execution-ready decision Replay mismatch")
    return {
        "execution_status": ready["execution_status"],
        "chain_id": candidate["chain_id"],
        "authorization_scope": deepcopy(packet["authorization_scope"]),
        "human_execution_decision_hash": decision["artifact_hash"],
        "replay_hash": replay_hash(wrappers),
        **STOP_BOUNDARIES,
    }
