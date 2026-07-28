"""Default constitutional development-validation planning through IVE-4."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.intelligent_validation_orchestrator_v4 import (
    FAILED_CLOSED as IVE_4_FAILED_CLOSED,
    INITIAL_VALIDATION_PLANNING,
    orchestrate_intelligent_validation_planning,
    reconstruct_intelligent_validation_orchestration_replay,
    validate_unified_validation_planning_bundle_artifact,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_change_normalization_runtime import (
    validate_normalized_change_artifact,
)
from aigol.runtime.transport.serialization import (
    load_json,
    replay_hash,
    write_json_immutable,
)


CONSTITUTIONAL_DEVELOPMENT_WORKFLOW_INTEGRATION_RUNTIME_VERSION = (
    "G42_01_CONSTITUTIONAL_DEVELOPMENT_WORKFLOW_INTEGRATION_RUNTIME_V1"
)
CONSTITUTIONAL_DEVELOPMENT_VALIDATION_WORKFLOW_ARTIFACT_V1 = (
    "CONSTITUTIONAL_DEVELOPMENT_VALIDATION_WORKFLOW_ARTIFACT_V1"
)
DEVELOPMENT_VALIDATION_PLANNING_READY = (
    "DEVELOPMENT_VALIDATION_PLANNING_READY"
)
FAILED_CLOSED = "FAILED_CLOSED"
REPLAY_STEPS = (
    "normalized_change_bound",
    "ive_4_planning_bundle_bound",
    "constitutional_development_validation_workflow_recorded",
)

DEFAULT_PLANNING_ENTRY = {
    "capability_identifier": "INTELLIGENT_VALIDATION_ORCHESTRATOR_V4",
    "runtime_owner": (
        "aigol.runtime.intelligent_validation_orchestrator_v4"
    ),
    "entry_point": "orchestrate_intelligent_validation_planning",
    "adoption_status": "DEFAULT_PLATFORM_CORE_DEVELOPMENT_VALIDATION_PLANNER",
}

AUTHORITY_FLAGS = {
    "authorizes_execution": False,
    "authorizes_dispatch": False,
    "authorizes_worker_invocation": False,
    "authorizes_provider_invocation": False,
    "authorizes_filesystem_mutation": False,
    "authorizes_governance_mutation": False,
    "authorizes_replay_mutation": False,
    "authorizes_certification": False,
    "constructs_validation_candidate": False,
    "records_human_approval": False,
    "executes_validation": False,
    "invokes_pytest": False,
    "modifies_validation_runtime": False,
    "modifies_authorization": False,
    "modifies_worker_contracts": False,
    "modifies_provider_contracts": False,
    "modifies_aicli": False,
    "modifies_pcbv31": False,
}


def plan_constitutional_development_validation(
    *,
    workflow_id: str,
    session_id: str,
    normalized_change_artifact: dict[str, Any],
    normalized_change_reference: str,
    normalized_change_hash: str,
    created_by: str,
    created_at: str,
    replay_dir: str | Path,
    planning_mode: str = INITIAL_VALIDATION_PLANNING,
    failure_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Use certified IVE-4 as the default development planning entry."""

    replay_path = Path(replay_dir)
    source: dict[str, Any] | None = None
    ive_4_bundle: dict[str, Any] | None = None
    try:
        _ensure_replay_available(replay_path)
        identifier = _require_string(workflow_id, "workflow_id")
        session = _require_string(session_id, "session_id")
        source_reference = _require_string(
            normalized_change_reference,
            "normalized_change_reference",
        )
        source_hash = _require_hash(
            normalized_change_hash,
            "normalized_change_hash",
        )
        creator = _require_string(created_by, "created_by")
        timestamp = _require_string(created_at, "created_at")
        source = validate_normalized_change_artifact(
            normalized_change_artifact
        )
        _validate_source_binding(source, source_reference, source_hash)

        ive_4_capture = orchestrate_intelligent_validation_planning(
            orchestration_id=f"{identifier}:IVE-4",
            session_id=session,
            planning_mode=planning_mode,
            normalized_change_artifact=source,
            normalized_change_reference=source_reference,
            normalized_change_hash=source_hash,
            failure_context=failure_context,
            created_by=creator,
            created_at=timestamp,
            replay_dir=replay_path / "ive_4",
        )
        ive_4_bundle = validate_unified_validation_planning_bundle_artifact(
            ive_4_capture[
                "unified_validation_planning_bundle_artifact"
            ]
        )
        if ive_4_bundle["bundle_status"] == IVE_4_FAILED_CLOSED:
            raise FailClosedRuntimeError(
                "G42-01 failed closed at IVE-4: "
                f"{ive_4_bundle['failure_reason']}"
            )
        reconstructed = (
            reconstruct_intelligent_validation_orchestration_replay(
                replay_path / "ive_4"
            )
        )
        _validate_ive_4_reconstruction(ive_4_bundle, reconstructed)
        artifact = _workflow_artifact(
            workflow_id=identifier,
            session_id=session,
            workflow_status=DEVELOPMENT_VALIDATION_PLANNING_READY,
            source=source,
            ive_4_bundle=ive_4_bundle,
            created_by=creator,
            created_at=timestamp,
            failure_reason=None,
        )
    except Exception as exc:
        artifact = _failed_workflow_artifact(
            workflow_id=workflow_id,
            session_id=session_id,
            normalized_change_artifact=normalized_change_artifact,
            normalized_change_reference=normalized_change_reference,
            normalized_change_hash=normalized_change_hash,
            planning_mode=planning_mode,
            created_by=created_by,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
    _persist_replay(
        replay_path,
        source,
        ive_4_bundle,
        artifact,
    )
    return _capture(artifact, replay_path)


def validate_constitutional_development_validation_workflow_artifact(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Validate one G42 constitutional development workflow artifact."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(
            "G42-01 workflow artifact must be a JSON object"
        )
    candidate = deepcopy(artifact)
    _verify_workflow_artifact(candidate)
    return candidate


def reconstruct_constitutional_development_validation_workflow_replay(
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Reconstruct the default IVE-4 workflow and its immutable lineage."""

    replay_path = Path(replay_dir)
    wrappers = [
        load_json(replay_path / f"{index:03d}_{step}.json")
        for index, step in enumerate(REPLAY_STEPS)
    ]
    for index, (step, wrapper) in enumerate(zip(REPLAY_STEPS, wrappers)):
        _verify_wrapper(wrapper, index, step)
    artifact = (
        validate_constitutional_development_validation_workflow_artifact(
            wrappers[2].get("artifact")
        )
    )
    if artifact["workflow_status"] != FAILED_CLOSED:
        source = validate_normalized_change_artifact(
            wrappers[0].get("artifact")
        )
        bundle = validate_unified_validation_planning_bundle_artifact(
            wrappers[1].get("artifact")
        )
        reconstructed = (
            reconstruct_intelligent_validation_orchestration_replay(
                replay_path / "ive_4"
            )
        )
        _validate_ive_4_reconstruction(bundle, reconstructed)
        _validate_success_bindings(artifact, source, bundle)
        expected = _workflow_artifact(
            workflow_id=artifact["workflow_id"],
            session_id=artifact["session_id"],
            workflow_status=artifact["workflow_status"],
            source=source,
            ive_4_bundle=bundle,
            created_by=artifact["created_by"],
            created_at=artifact["created_at"],
            failure_reason=None,
        )
        if artifact != expected:
            raise FailClosedRuntimeError(
                "G42-01 deterministic workflow replay mismatch"
            )
    return {
        "workflow_id": artifact["workflow_id"],
        "workflow_status": artifact["workflow_status"],
        "planning_mode": artifact["planning_mode"],
        "default_planning_entry": deepcopy(
            artifact["default_planning_entry"]
        ),
        "ive_4_bundle_hash": artifact["ive_4_bundle_hash"],
        "workflow_hash": artifact["workflow_hash"],
        "artifact_hash": artifact["artifact_hash"],
        "replay_visible": True,
        "fail_closed": artifact["workflow_status"] == FAILED_CLOSED,
        "failure_reason": artifact["failure_reason"],
        "human_approval_required": True,
        "validation_candidate_constructed": False,
        "validation_executed": False,
        "authority_flags": deepcopy(artifact["authority_flags"]),
        "replay_hashes": [wrapper["replay_hash"] for wrapper in wrappers],
    }


def _workflow_artifact(
    *,
    workflow_id: str,
    session_id: str,
    workflow_status: str,
    source: dict[str, Any],
    ive_4_bundle: dict[str, Any],
    created_by: str,
    created_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    g38 = ive_4_bundle["stage_artifacts"]["g38"]
    artifact = {
        "artifact_type": (
            CONSTITUTIONAL_DEVELOPMENT_VALIDATION_WORKFLOW_ARTIFACT_V1
        ),
        "runtime_version": (
            CONSTITUTIONAL_DEVELOPMENT_WORKFLOW_INTEGRATION_RUNTIME_VERSION
        ),
        "workflow_id": workflow_id,
        "session_id": session_id,
        "workflow_status": workflow_status,
        "planning_mode": ive_4_bundle["planning_mode"],
        "source_normalized_change_reference": source["normalization_id"],
        "source_normalized_change_hash": source["normalized_change_hash"],
        "source_normalized_change_artifact_hash": source["artifact_hash"],
        "default_planning_entry": deepcopy(DEFAULT_PLANNING_ENTRY),
        "ive_4_orchestration_reference": ive_4_bundle[
            "orchestration_id"
        ],
        "ive_4_bundle_hash": ive_4_bundle["bundle_hash"],
        "ive_4_artifact_hash": ive_4_bundle["artifact_hash"],
        "ive_4_replay_reference": "ive_4",
        "ive_4_planning_bundle_artifact": deepcopy(ive_4_bundle),
        "planning_stage_lineage": deepcopy(
            ive_4_bundle["stage_lineage"]
        ),
        "current_planning_recommendation": deepcopy(
            ive_4_bundle["current_planning_recommendation"]
        ),
        "full_regression": deepcopy(ive_4_bundle["full_regression"]),
        "existing_validation_pipeline_handoff": deepcopy(
            g38["existing_validation_pipeline_handoff"]
        ),
        "human_approval": deepcopy(ive_4_bundle["human_approval"]),
        "workflow_policy": {
            "ive_4_is_default_planning_entry": True,
            "ive_4_output_consumed_unchanged": True,
            "existing_candidate_composition_owner_unchanged": True,
            "existing_human_approval_owner_unchanged": True,
            "existing_authorization_owner_unchanged": True,
            "existing_validation_execution_owner_unchanged": True,
            "pytest_execution_unchanged": True,
            "replay_protocols_unchanged": True,
            "planning_evidence_required": True,
            "command_synthesis_allowed": False,
            "validation_execution_allowed": False,
        },
        "created_by": created_by,
        "created_at": created_at,
        "replay_visible": True,
        "read_only": True,
        "non_authoritative": True,
        "human_approval_required": True,
        "human_approval_recorded": False,
        "validation_candidate_constructed": False,
        "validation_executed": False,
        "authorization_invoked": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "aicli_invoked": False,
        "repository_mutated": False,
        "replay_semantics_modified": False,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "failure_reason": failure_reason,
    }
    artifact["workflow_hash"] = _workflow_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_workflow_artifact(
    *,
    workflow_id: Any,
    session_id: Any,
    normalized_change_artifact: Any,
    normalized_change_reference: Any,
    normalized_change_hash: Any,
    planning_mode: Any,
    created_by: Any,
    created_at: Any,
    failure_reason: str,
) -> dict[str, Any]:
    source = (
        normalized_change_artifact
        if isinstance(normalized_change_artifact, dict)
        else {}
    )
    unavailable_hash = _safe_hash(source.get("artifact_hash"))
    recommendation = {
        "recommendation_type": "FAILED_CLOSED_NO_PLANNING_EVIDENCE",
        "recommendation_only": True,
    }
    recommendation["recommendation_hash"] = replay_hash(recommendation)
    artifact = {
        "artifact_type": (
            CONSTITUTIONAL_DEVELOPMENT_VALIDATION_WORKFLOW_ARTIFACT_V1
        ),
        "runtime_version": (
            CONSTITUTIONAL_DEVELOPMENT_WORKFLOW_INTEGRATION_RUNTIME_VERSION
        ),
        "workflow_id": _safe_string(workflow_id),
        "session_id": _safe_string(session_id),
        "workflow_status": FAILED_CLOSED,
        "planning_mode": _safe_string(planning_mode),
        "source_normalized_change_reference": _safe_string(
            normalized_change_reference
        ),
        "source_normalized_change_hash": _safe_hash(
            normalized_change_hash
        ),
        "source_normalized_change_artifact_hash": unavailable_hash,
        "default_planning_entry": deepcopy(DEFAULT_PLANNING_ENTRY),
        "ive_4_orchestration_reference": "UNAVAILABLE",
        "ive_4_bundle_hash": unavailable_hash,
        "ive_4_artifact_hash": unavailable_hash,
        "ive_4_replay_reference": "ive_4",
        "ive_4_planning_bundle_artifact": {},
        "planning_stage_lineage": [],
        "current_planning_recommendation": recommendation,
        "full_regression": {
            "required": True,
            "reason": (
                "G42-01 missing or invalid planning evidence prohibits "
                "reduced-scope validation."
            ),
            "mapping_authority": "G42_01_FAIL_CLOSED_POLICY_V1",
        },
        "existing_validation_pipeline_handoff": {
            "status": "BLOCKED_BY_MISSING_PLANNING_EVIDENCE",
            "candidate_composition_owner": (
                "PLATFORM_VALIDATION_PLAN_TO_CANDIDATE_COMPOSITION"
            ),
            "human_approval_owner": (
                "PLATFORM_CORE_VALIDATION_GOVERNANCE"
            ),
            "execution_owner": "EXISTING_GOVERNED_VALIDATION_RUNTIME",
            "new_command_synthesis_allowed": False,
            "allowlist_expansion_allowed": False,
        },
        "human_approval": {
            "required_before_execution": True,
            "approval_status": "BLOCKED",
            "must_bind_exact_candidate_hash": True,
            "approval_authorizes_execution_by_itself": False,
        },
        "workflow_policy": {
            "ive_4_is_default_planning_entry": True,
            "ive_4_output_consumed_unchanged": True,
            "existing_candidate_composition_owner_unchanged": True,
            "existing_human_approval_owner_unchanged": True,
            "existing_authorization_owner_unchanged": True,
            "existing_validation_execution_owner_unchanged": True,
            "pytest_execution_unchanged": True,
            "replay_protocols_unchanged": True,
            "planning_evidence_required": True,
            "command_synthesis_allowed": False,
            "validation_execution_allowed": False,
        },
        "created_by": _safe_string(created_by),
        "created_at": _safe_string(created_at),
        "replay_visible": True,
        "read_only": True,
        "non_authoritative": True,
        "human_approval_required": True,
        "human_approval_recorded": False,
        "validation_candidate_constructed": False,
        "validation_executed": False,
        "authorization_invoked": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "aicli_invoked": False,
        "repository_mutated": False,
        "replay_semantics_modified": False,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "failure_reason": failure_reason,
    }
    artifact["workflow_hash"] = _workflow_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _verify_workflow_artifact(artifact: dict[str, Any]) -> None:
    if (
        artifact.get("artifact_type")
        != CONSTITUTIONAL_DEVELOPMENT_VALIDATION_WORKFLOW_ARTIFACT_V1
        or artifact.get("runtime_version")
        != CONSTITUTIONAL_DEVELOPMENT_WORKFLOW_INTEGRATION_RUNTIME_VERSION
    ):
        raise FailClosedRuntimeError("G42-01 workflow artifact type mismatch")
    _verify_hash(
        artifact,
        "artifact_hash",
        "G42-01 workflow artifact hash mismatch",
    )
    if artifact.get("workflow_hash") != _workflow_hash(artifact):
        raise FailClosedRuntimeError(
            "G42-01 deterministic workflow hash mismatch"
        )
    if artifact.get("workflow_status") not in {
        DEVELOPMENT_VALIDATION_PLANNING_READY,
        FAILED_CLOSED,
    }:
        raise FailClosedRuntimeError("G42-01 workflow status invalid")
    if artifact.get("default_planning_entry") != DEFAULT_PLANNING_ENTRY:
        raise FailClosedRuntimeError(
            "G42-01 default planning entry mismatch"
        )
    if (
        artifact.get("replay_visible") is not True
        or artifact.get("read_only") is not True
        or artifact.get("non_authoritative") is not True
        or artifact.get("authority_flags") != AUTHORITY_FLAGS
    ):
        raise FailClosedRuntimeError("G42-01 boundary flags invalid")
    for field in (
        "human_approval_recorded",
        "validation_candidate_constructed",
        "validation_executed",
        "authorization_invoked",
        "worker_invoked",
        "provider_invoked",
        "aicli_invoked",
        "repository_mutated",
        "replay_semantics_modified",
    ):
        if artifact.get(field) is not False:
            raise FailClosedRuntimeError(f"G42-01 {field} must be false")
    if artifact.get("human_approval_required") is not True:
        raise FailClosedRuntimeError(
            "G42-01 Human Approval requirement missing"
        )
    if artifact.get("workflow_policy") != {
        "ive_4_is_default_planning_entry": True,
        "ive_4_output_consumed_unchanged": True,
        "existing_candidate_composition_owner_unchanged": True,
        "existing_human_approval_owner_unchanged": True,
        "existing_authorization_owner_unchanged": True,
        "existing_validation_execution_owner_unchanged": True,
        "pytest_execution_unchanged": True,
        "replay_protocols_unchanged": True,
        "planning_evidence_required": True,
        "command_synthesis_allowed": False,
        "validation_execution_allowed": False,
    }:
        raise FailClosedRuntimeError("G42-01 workflow policy invalid")
    if artifact["workflow_status"] == FAILED_CLOSED:
        if (
            artifact.get("ive_4_planning_bundle_artifact")
            or artifact.get("planning_stage_lineage")
        ):
            raise FailClosedRuntimeError(
                "failed G42-01 workflow cannot claim planning evidence"
            )
        if artifact.get("full_regression", {}).get("required") is not True:
            raise FailClosedRuntimeError(
                "failed G42-01 workflow must require full regression"
            )
        if not artifact.get("failure_reason"):
            raise FailClosedRuntimeError(
                "failed G42-01 workflow requires failure reason"
            )
        if (
            artifact.get("current_planning_recommendation", {}).get(
                "recommendation_type"
            )
            != "FAILED_CLOSED_NO_PLANNING_EVIDENCE"
            or artifact.get(
                "existing_validation_pipeline_handoff",
                {},
            ).get("status")
            != "BLOCKED_BY_MISSING_PLANNING_EVIDENCE"
            or artifact.get("human_approval", {}).get("approval_status")
            != "BLOCKED"
        ):
            raise FailClosedRuntimeError(
                "failed G42-01 workflow boundary policy invalid"
            )
        return
    bundle = validate_unified_validation_planning_bundle_artifact(
        artifact.get("ive_4_planning_bundle_artifact")
    )
    if bundle["bundle_status"] == IVE_4_FAILED_CLOSED:
        raise FailClosedRuntimeError(
            "successful G42-01 workflow cannot bind failed IVE-4"
        )
    _validate_success_bundle_fields(artifact, bundle)


def _validate_success_bindings(
    artifact: dict[str, Any],
    source: dict[str, Any],
    bundle: dict[str, Any],
) -> None:
    if (
        artifact["source_normalized_change_reference"]
        != source["normalization_id"]
        or artifact["source_normalized_change_hash"]
        != source["normalized_change_hash"]
        or artifact["source_normalized_change_artifact_hash"]
        != source["artifact_hash"]
        or bundle["source_normalized_change_reference"]
        != source["normalization_id"]
        or bundle["source_normalized_change_hash"]
        != source["normalized_change_hash"]
        or bundle["source_normalized_change_artifact_hash"]
        != source["artifact_hash"]
    ):
        raise FailClosedRuntimeError(
            "G42-01 normalized change lineage mismatch"
        )
    _validate_success_bundle_fields(artifact, bundle)


def _validate_success_bundle_fields(
    artifact: dict[str, Any],
    bundle: dict[str, Any],
) -> None:
    g38 = bundle["stage_artifacts"]["g38"]
    if (
        artifact.get("source_normalized_change_reference")
        != bundle["source_normalized_change_reference"]
        or artifact.get("source_normalized_change_hash")
        != bundle["source_normalized_change_hash"]
        or artifact.get("source_normalized_change_artifact_hash")
        != bundle["source_normalized_change_artifact_hash"]
        or artifact.get("ive_4_orchestration_reference")
        != bundle["orchestration_id"]
        or artifact.get("ive_4_bundle_hash") != bundle["bundle_hash"]
        or artifact.get("ive_4_artifact_hash") != bundle["artifact_hash"]
        or artifact.get("ive_4_replay_reference") != "ive_4"
        or artifact.get("planning_mode") != bundle["planning_mode"]
        or artifact.get("planning_stage_lineage")
        != bundle["stage_lineage"]
        or artifact.get("current_planning_recommendation")
        != bundle["current_planning_recommendation"]
        or artifact.get("full_regression") != bundle["full_regression"]
        or artifact.get("human_approval") != bundle["human_approval"]
        or artifact.get("existing_validation_pipeline_handoff")
        != g38["existing_validation_pipeline_handoff"]
        or artifact.get("failure_reason") is not None
    ):
        raise FailClosedRuntimeError(
            "G42-01 IVE-4 workflow binding mismatch"
        )
    if (
        artifact["human_approval"].get("required_before_execution")
        is not True
    ):
        raise FailClosedRuntimeError(
            "G42-01 workflow bypasses Human Approval"
        )


def _validate_ive_4_reconstruction(
    bundle: dict[str, Any],
    reconstructed: dict[str, Any],
) -> None:
    if (
        reconstructed.get("fail_closed") is not False
        or reconstructed.get("bundle_hash") != bundle["bundle_hash"]
        or reconstructed.get("artifact_hash") != bundle["artifact_hash"]
        or reconstructed.get("planning_mode") != bundle["planning_mode"]
        or reconstructed.get("stage_lineage") != bundle["stage_lineage"]
    ):
        raise FailClosedRuntimeError(
            "G42-01 IVE-4 replay reconstruction mismatch"
        )


def _validate_source_binding(
    source: dict[str, Any],
    reference: str,
    source_hash: str,
) -> None:
    if (
        source.get("normalization_id") != reference
        or source.get("normalized_change_hash") != source_hash
    ):
        raise FailClosedRuntimeError(
            "G42-01 normalized change binding mismatch"
        )


def _capture(
    artifact: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "runtime_version": (
            CONSTITUTIONAL_DEVELOPMENT_WORKFLOW_INTEGRATION_RUNTIME_VERSION
        ),
        "constitutional_development_validation_workflow_artifact": deepcopy(
            artifact
        ),
        "workflow_id": artifact["workflow_id"],
        "workflow_status": artifact["workflow_status"],
        "planning_mode": artifact["planning_mode"],
        "default_planning_entry": deepcopy(
            artifact["default_planning_entry"]
        ),
        "ive_4_bundle_hash": artifact["ive_4_bundle_hash"],
        "workflow_hash": artifact["workflow_hash"],
        "replay_reference": str(replay_path),
        "fail_closed": artifact["workflow_status"] == FAILED_CLOSED,
        "failure_reason": artifact["failure_reason"],
        "human_approval_required": True,
        "validation_candidate_constructed": False,
        "validation_executed": False,
        "authorization_invoked": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "repository_mutated": False,
    }
    capture["capture_hash"] = replay_hash(capture)
    return capture


def _persist_replay(
    replay_path: Path,
    source: dict[str, Any] | None,
    ive_4_bundle: dict[str, Any] | None,
    artifact: dict[str, Any],
) -> None:
    try:
        artifacts = (
            source or _unavailable_snapshot("NORMALIZED_CHANGE", artifact),
            ive_4_bundle or _unavailable_snapshot("IVE_4", artifact),
            artifact,
        )
        for index, (step, item) in enumerate(zip(REPLAY_STEPS, artifacts)):
            wrapper = {
                "replay_index": index,
                "replay_step": step,
                "artifact": deepcopy(item),
            }
            wrapper["replay_hash"] = replay_hash(wrapper)
            write_json_immutable(
                replay_path / f"{index:03d}_{step}.json",
                wrapper,
            )
    except Exception:
        return


def _unavailable_snapshot(
    boundary: str,
    artifact: dict[str, Any],
) -> dict[str, Any]:
    snapshot = {
        "artifact_type": f"{boundary}_UNAVAILABLE_V1",
        "boundary": boundary,
        "workflow_id": artifact["workflow_id"],
        "source_available": False,
    }
    snapshot["artifact_hash"] = replay_hash(snapshot)
    return snapshot


def _verify_wrapper(
    wrapper: dict[str, Any],
    index: int,
    step: str,
) -> None:
    if (
        wrapper.get("replay_index") != index
        or wrapper.get("replay_step") != step
    ):
        raise FailClosedRuntimeError("G42-01 replay ordering mismatch")
    _verify_hash(wrapper, "replay_hash", "G42-01 replay hash mismatch")


def _ensure_replay_available(replay_path: Path) -> None:
    if any(
        (replay_path / f"{index:03d}_{step}.json").exists()
        for index, step in enumerate(REPLAY_STEPS)
    ):
        raise FailClosedRuntimeError(
            "G42-01 failed closed: replay artifact already exists"
        )


def _verify_hash(
    value: dict[str, Any],
    field: str,
    message: str,
) -> None:
    actual = value.get(field)
    if not isinstance(actual, str) or not actual.startswith("sha256:"):
        raise FailClosedRuntimeError(message)
    expected = deepcopy(value)
    expected.pop(field, None)
    if replay_hash(expected) != actual:
        raise FailClosedRuntimeError(message)


def _workflow_hash(artifact: dict[str, Any]) -> str:
    candidate = deepcopy(artifact)
    candidate.pop("artifact_hash", None)
    candidate.pop("workflow_hash", None)
    return replay_hash(candidate)


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"G42-01 requires {field}")
    return value


def _require_hash(value: Any, field: str) -> str:
    text = _require_string(value, field)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(
            f"G42-01 requires canonical {field}"
        )
    return text


def _safe_string(value: Any) -> str:
    return value if isinstance(value, str) and value.strip() else "UNAVAILABLE"


def _safe_hash(value: Any) -> str:
    if isinstance(value, str) and value.startswith("sha256:"):
        return value
    return replay_hash({"unavailable": str(value)})


def _failure_reason(exc: Exception) -> str:
    text = str(exc).strip()
    return text or exc.__class__.__name__
