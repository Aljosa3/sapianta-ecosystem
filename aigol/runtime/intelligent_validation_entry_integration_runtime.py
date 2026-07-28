"""Single planning entry over certified IVE-0 and IVE-1 runtimes."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.intelligent_validation_engine_v0 import (
    FAILED_CLOSED as IVE_0_FAILED_CLOSED,
    analyze_intelligent_validation_scope,
    reconstruct_intelligent_validation_engine_v0_replay,
    validate_intelligent_validation_plan_artifact,
)
from aigol.runtime.intelligent_validation_engine_v1 import (
    FAILED_CLOSED as IVE_1_FAILED_CLOSED,
    reconstruct_semantic_validation_selection_replay,
    select_semantic_validation_scope,
    validate_semantic_validation_selection_artifact,
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


INTELLIGENT_VALIDATION_ENTRY_INTEGRATION_RUNTIME_VERSION = (
    "G38_01_INTELLIGENT_VALIDATION_ENTRY_INTEGRATION_RUNTIME_V1"
)
INTELLIGENT_VALIDATION_PLANNING_ENTRY_ARTIFACT_V1 = (
    "INTELLIGENT_VALIDATION_PLANNING_ENTRY_ARTIFACT_V1"
)
INTELLIGENT_VALIDATION_PLANNING_READY = "INTELLIGENT_VALIDATION_PLANNING_READY"
FAILED_CLOSED = "FAILED_CLOSED"
REPLAY_STEP = "intelligent_validation_planning_entry_recorded"

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
    "parallelizes_validation": False,
    "modifies_pytest": False,
    "modifies_validation_runtime": False,
    "modifies_authorization": False,
}


def plan_development_validation(
    *,
    entry_id: str,
    session_id: str,
    normalized_change_artifact: dict[str, Any],
    normalized_change_reference: str,
    normalized_change_hash: str,
    created_by: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Run certified IVE-0 then IVE-1 and record one inert planning entry."""

    replay_path = Path(replay_dir)
    ive_0_artifact: dict[str, Any] | None = None
    ive_1_artifact: dict[str, Any] | None = None
    try:
        _ensure_replay_available(replay_path)
        identifier = _require_string(entry_id, "entry_id")
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
        source = validate_normalized_change_artifact(normalized_change_artifact)
        _validate_source_binding(source, source_reference, source_hash)

        ive_0_capture = analyze_intelligent_validation_scope(
            ive_analysis_id=f"{identifier}:IVE-0",
            normalized_change_artifact=source,
            normalized_change_reference=source_reference,
            normalized_change_hash=source_hash,
            created_at=timestamp,
            replay_dir=replay_path / "ive_0",
        )
        ive_0_artifact = validate_intelligent_validation_plan_artifact(
            ive_0_capture["intelligent_validation_plan_artifact"]
        )
        if ive_0_artifact["analysis_status"] == IVE_0_FAILED_CLOSED:
            raise FailClosedRuntimeError(
                f"G38-01 failed closed: {ive_0_artifact['failure_reason']}"
            )

        ive_1_capture = select_semantic_validation_scope(
            selection_id=f"{identifier}:IVE-1",
            intelligent_validation_plan_artifact=ive_0_artifact,
            intelligent_validation_plan_reference=ive_0_artifact[
                "ive_analysis_id"
            ],
            intelligent_validation_plan_hash=ive_0_artifact[
                "intelligent_validation_plan_hash"
            ],
            created_at=timestamp,
            replay_dir=replay_path / "ive_1",
        )
        ive_1_artifact = validate_semantic_validation_selection_artifact(
            ive_1_capture["semantic_validation_selection_artifact"]
        )
        if ive_1_artifact["selection_status"] == IVE_1_FAILED_CLOSED:
            raise FailClosedRuntimeError(
                f"G38-01 failed closed: {ive_1_artifact['failure_reason']}"
            )

        artifact = _entry_artifact(
            entry_id=identifier,
            session_id=session,
            status=INTELLIGENT_VALIDATION_PLANNING_READY,
            source_reference=source_reference,
            source_hash=source_hash,
            source_artifact_hash=source["artifact_hash"],
            ive_0_artifact=ive_0_artifact,
            ive_1_artifact=ive_1_artifact,
            created_by=creator,
            created_at=timestamp,
            failure_reason=None,
        )
    except Exception as exc:
        artifact = _failed_entry_artifact(
            entry_id=entry_id,
            session_id=session_id,
            normalized_change_artifact=normalized_change_artifact,
            normalized_change_reference=normalized_change_reference,
            normalized_change_hash=normalized_change_hash,
            ive_0_artifact=ive_0_artifact,
            ive_1_artifact=ive_1_artifact,
            created_by=created_by,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
    _persist_if_possible(replay_path, artifact)
    return _capture(artifact, replay_path)


def validate_intelligent_validation_planning_entry_artifact(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Validate one G38 planning entry without invoking mutable state."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(
            "G38-01 planning entry artifact must be a JSON object"
        )
    candidate = deepcopy(artifact)
    _verify_entry_artifact(candidate)
    return candidate


def reconstruct_intelligent_validation_entry_replay(
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Reconstruct the entry and both certified nested IVE replay families."""

    replay_path = Path(replay_dir)
    wrapper = load_json(replay_path / f"000_{REPLAY_STEP}.json")
    if wrapper.get("replay_index") != 0 or wrapper.get("replay_step") != REPLAY_STEP:
        raise FailClosedRuntimeError("G38-01 replay ordering mismatch")
    _verify_hash(wrapper, "replay_hash", "G38-01 replay hash mismatch")
    artifact = validate_intelligent_validation_planning_entry_artifact(
        wrapper.get("artifact")
    )

    if artifact["entry_status"] != FAILED_CLOSED:
        ive_0 = reconstruct_intelligent_validation_engine_v0_replay(
            replay_path / "ive_0"
        )
        reconstruct_semantic_validation_selection_replay(
            replay_path / "ive_1"
        )
        ive_1_wrapper = load_json(
            replay_path / "ive_1/001_semantic_validation_selection_recorded.json"
        )
        ive_1 = validate_semantic_validation_selection_artifact(
            ive_1_wrapper.get("artifact")
        )
        _verify_reconstructed_lineage(artifact, ive_0, ive_1)

    return {
        "entry_id": artifact["entry_id"],
        "entry_status": artifact["entry_status"],
        "normalized_change_reference": artifact[
            "normalized_change_reference"
        ],
        "ive_0_plan_hash": artifact["ive_0_plan_hash"],
        "ive_1_selection_hash": artifact["ive_1_selection_hash"],
        "selected_validation_requirements": deepcopy(
            artifact["selected_validation_requirements"]
        ),
        "full_regression": deepcopy(artifact["full_regression"]),
        "existing_validation_pipeline_handoff": deepcopy(
            artifact["existing_validation_pipeline_handoff"]
        ),
        "human_approval": deepcopy(artifact["human_approval"]),
        "planning_entry_hash": artifact["planning_entry_hash"],
        "artifact_hash": artifact["artifact_hash"],
        "replay_visible": True,
        "fail_closed": artifact["entry_status"] == FAILED_CLOSED,
        "failure_reason": artifact["failure_reason"],
        "human_approval_required": True,
        "validation_executed": False,
        "authority_flags": deepcopy(artifact["authority_flags"]),
        "replay_hash": wrapper["replay_hash"],
    }


def _entry_artifact(
    *,
    entry_id: str,
    session_id: str,
    status: str,
    source_reference: str,
    source_hash: str,
    source_artifact_hash: str,
    ive_0_artifact: dict[str, Any],
    ive_1_artifact: dict[str, Any],
    created_by: str,
    created_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": INTELLIGENT_VALIDATION_PLANNING_ENTRY_ARTIFACT_V1,
        "runtime_version": INTELLIGENT_VALIDATION_ENTRY_INTEGRATION_RUNTIME_VERSION,
        "entry_id": entry_id,
        "session_id": session_id,
        "entry_status": status,
        "normalized_change_reference": source_reference,
        "normalized_change_hash": source_hash,
        "normalized_change_artifact_hash": source_artifact_hash,
        "ive_0_reference": ive_0_artifact["ive_analysis_id"],
        "ive_0_plan_hash": ive_0_artifact["intelligent_validation_plan_hash"],
        "ive_0_artifact_hash": ive_0_artifact["artifact_hash"],
        "ive_0_replay_reference": "ive_0",
        "ive_1_reference": ive_1_artifact["selection_id"],
        "ive_1_selection_hash": ive_1_artifact[
            "semantic_validation_selection_hash"
        ],
        "ive_1_artifact_hash": ive_1_artifact["artifact_hash"],
        "ive_1_replay_reference": "ive_1",
        "direct_validation_subjects": deepcopy(
            ive_1_artifact["direct_validation_subjects"]
        ),
        "transitive_dependencies": deepcopy(
            ive_1_artifact["transitive_dependencies"]
        ),
        "selected_validation_requirements": deepcopy(
            ive_1_artifact["selected_validation_requirements"]
        ),
        "full_regression": deepcopy(ive_1_artifact["full_regression"]),
        "certification_evidence_test_targets": deepcopy(
            ive_1_artifact["certification_evidence_test_targets"]
        ),
        "existing_allowlisted_command_references": deepcopy(
            ive_1_artifact["existing_allowlisted_command_references"]
        ),
        "existing_validation_pipeline_handoff": deepcopy(
            ive_1_artifact["existing_validation_pipeline_handoff"]
        ),
        "human_approval": deepcopy(ive_1_artifact["human_approval"]),
        "integration_policy": {
            "ive_0_output_consumed_unchanged": True,
            "ive_1_output_consumed_unchanged": True,
            "candidate_composition_owner_unchanged": True,
            "validation_governance_owner_unchanged": True,
            "validation_execution_owner_unchanged": True,
            "pytest_execution_unchanged": True,
            "scope_reduction_allowed": False,
            "command_synthesis_allowed": False,
            "parallel_scheduling_allowed": False,
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
    artifact["planning_entry_hash"] = _planning_entry_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_entry_artifact(
    *,
    entry_id: Any,
    session_id: Any,
    normalized_change_artifact: Any,
    normalized_change_reference: Any,
    normalized_change_hash: Any,
    ive_0_artifact: dict[str, Any] | None,
    ive_1_artifact: dict[str, Any] | None,
    created_by: Any,
    created_at: Any,
    failure_reason: str,
) -> dict[str, Any]:
    unavailable = replay_hash({"unavailable": "G38-01"})
    failed_ive_0 = {
        "ive_analysis_id": _safe_string(
            (ive_0_artifact or {}).get("ive_analysis_id")
        ),
        "intelligent_validation_plan_hash": _safe_hash(
            (ive_0_artifact or {}).get("intelligent_validation_plan_hash")
        ),
        "artifact_hash": _safe_hash((ive_0_artifact or {}).get("artifact_hash")),
    }
    failed_ive_1 = {
        "selection_id": _safe_string((ive_1_artifact or {}).get("selection_id")),
        "semantic_validation_selection_hash": _safe_hash(
            (ive_1_artifact or {}).get("semantic_validation_selection_hash")
        ),
        "artifact_hash": _safe_hash((ive_1_artifact or {}).get("artifact_hash")),
        "direct_validation_subjects": [],
        "transitive_dependencies": [],
        "selected_validation_requirements": [],
        "full_regression": {
            "required": True,
            "reason": "G38-01 failure prohibits reduced validation scope.",
            "mapping_authority": "G38_01_FAIL_CLOSED_POLICY_V1",
        },
        "certification_evidence_test_targets": [],
        "existing_allowlisted_command_references": [],
        "existing_validation_pipeline_handoff": {
            "status": "BLOCKED_BY_INTELLIGENT_VALIDATION_ENTRY_FAILURE",
            "candidate_composition_owner": (
                "PLATFORM_VALIDATION_PLAN_TO_CANDIDATE_COMPOSITION"
            ),
            "human_approval_owner": "PLATFORM_CORE_VALIDATION_GOVERNANCE",
            "execution_owner": "EXISTING_GOVERNED_VALIDATION_RUNTIME",
            "new_command_synthesis_allowed": False,
            "allowlist_expansion_allowed": False,
        },
        "human_approval": {
            "required_before_execution": True,
            "recorded_by_ive_0": False,
            "approval_status": "BLOCKED",
            "must_bind_exact_candidate_hash": True,
            "approval_authorizes_execution_by_itself": False,
        },
    }
    return _entry_artifact(
        entry_id=_safe_string(entry_id),
        session_id=_safe_string(session_id),
        status=FAILED_CLOSED,
        source_reference=_safe_string(normalized_change_reference),
        source_hash=_safe_hash(normalized_change_hash),
        source_artifact_hash=_safe_hash(
            normalized_change_artifact.get("artifact_hash")
            if isinstance(normalized_change_artifact, dict)
            else unavailable
        ),
        ive_0_artifact=failed_ive_0,
        ive_1_artifact=failed_ive_1,
        created_by=_safe_string(created_by),
        created_at=_safe_string(created_at),
        failure_reason=failure_reason,
    )


def _verify_entry_artifact(artifact: dict[str, Any]) -> None:
    if artifact.get("artifact_type") != INTELLIGENT_VALIDATION_PLANNING_ENTRY_ARTIFACT_V1:
        raise FailClosedRuntimeError("G38-01 planning entry artifact type mismatch")
    _verify_hash(artifact, "artifact_hash", "G38-01 artifact hash mismatch")
    if artifact.get("planning_entry_hash") != _planning_entry_hash(artifact):
        raise FailClosedRuntimeError("G38-01 deterministic planning entry hash mismatch")
    if artifact.get("entry_status") not in {
        INTELLIGENT_VALIDATION_PLANNING_READY,
        FAILED_CLOSED,
    }:
        raise FailClosedRuntimeError("G38-01 planning entry status invalid")
    if (
        artifact.get("replay_visible") is not True
        or artifact.get("read_only") is not True
        or artifact.get("non_authoritative") is not True
    ):
        raise FailClosedRuntimeError("G38-01 planning boundary flags invalid")
    if artifact.get("authority_flags") != AUTHORITY_FLAGS:
        raise FailClosedRuntimeError("G38-01 authority flags invalid")
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
            raise FailClosedRuntimeError(f"G38-01 {field} must be false")
    if artifact.get("human_approval_required") is not True:
        raise FailClosedRuntimeError("G38-01 Human Approval requirement missing")
    approval = artifact.get("human_approval")
    if (
        not isinstance(approval, dict)
        or approval.get("required_before_execution") is not True
        or approval.get("must_bind_exact_candidate_hash") is not True
        or approval.get("approval_authorizes_execution_by_itself") is not False
    ):
        raise FailClosedRuntimeError("G38-01 Human Approval boundary invalid")
    policy = artifact.get("integration_policy")
    if not isinstance(policy, dict) or policy != {
        "ive_0_output_consumed_unchanged": True,
        "ive_1_output_consumed_unchanged": True,
        "candidate_composition_owner_unchanged": True,
        "validation_governance_owner_unchanged": True,
        "validation_execution_owner_unchanged": True,
        "pytest_execution_unchanged": True,
        "scope_reduction_allowed": False,
        "command_synthesis_allowed": False,
        "parallel_scheduling_allowed": False,
    }:
        raise FailClosedRuntimeError("G38-01 integration policy invalid")
    if artifact["entry_status"] == FAILED_CLOSED:
        if not artifact.get("failure_reason") or artifact.get(
            "existing_validation_pipeline_handoff", {}
        ).get("status") != "BLOCKED_BY_INTELLIGENT_VALIDATION_ENTRY_FAILURE":
            raise FailClosedRuntimeError("G38-01 failed entry is not terminal")
    elif artifact.get("failure_reason") is not None:
        raise FailClosedRuntimeError("G38-01 successful entry has failure reason")


def _verify_reconstructed_lineage(
    artifact: dict[str, Any],
    ive_0: dict[str, Any],
    ive_1: dict[str, Any],
) -> None:
    if (
        artifact["ive_0_reference"] != ive_0["ive_analysis_id"]
        or artifact["ive_0_plan_hash"] != ive_0["intelligent_validation_plan_hash"]
        or artifact["ive_0_artifact_hash"] != ive_0["artifact_hash"]
    ):
        raise FailClosedRuntimeError("G38-01 IVE-0 replay lineage mismatch")
    if (
        artifact["ive_1_reference"] != ive_1["selection_id"]
        or artifact["ive_1_selection_hash"]
        != ive_1["semantic_validation_selection_hash"]
        or artifact["ive_1_artifact_hash"] != ive_1["artifact_hash"]
    ):
        raise FailClosedRuntimeError("G38-01 IVE-1 replay lineage mismatch")
    if ive_1["source_ive_0_reference"] != ive_0["ive_analysis_id"]:
        raise FailClosedRuntimeError("G38-01 IVE-0 to IVE-1 binding mismatch")
    for field in (
        "selected_validation_requirements",
        "full_regression",
        "existing_validation_pipeline_handoff",
        "human_approval",
    ):
        if artifact[field] != ive_1[field]:
            raise FailClosedRuntimeError(
                f"G38-01 altered IVE-1 output field: {field}"
            )


def _validate_source_binding(
    source: dict[str, Any],
    reference: str,
    source_hash: str,
) -> None:
    if source.get("normalization_id") != reference:
        raise FailClosedRuntimeError("G38-01 normalized change reference mismatch")
    if source.get("normalized_change_hash") != source_hash:
        raise FailClosedRuntimeError("G38-01 normalized change hash mismatch")


def _planning_entry_hash(artifact: dict[str, Any]) -> str:
    candidate = deepcopy(artifact)
    candidate.pop("artifact_hash", None)
    candidate.pop("planning_entry_hash", None)
    return replay_hash(candidate)


def _capture(artifact: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "runtime_version": INTELLIGENT_VALIDATION_ENTRY_INTEGRATION_RUNTIME_VERSION,
        "intelligent_validation_planning_entry_artifact": deepcopy(artifact),
        "entry_id": artifact["entry_id"],
        "entry_status": artifact["entry_status"],
        "planning_entry_hash": artifact["planning_entry_hash"],
        "replay_reference": str(replay_path),
        "fail_closed": artifact["entry_status"] == FAILED_CLOSED,
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


def _persist_if_possible(replay_path: Path, artifact: dict[str, Any]) -> None:
    try:
        wrapper = {
            "replay_index": 0,
            "replay_step": REPLAY_STEP,
            "artifact": deepcopy(artifact),
        }
        wrapper["replay_hash"] = replay_hash(wrapper)
        write_json_immutable(
            replay_path / f"000_{REPLAY_STEP}.json",
            wrapper,
        )
    except Exception:
        return


def _ensure_replay_available(replay_path: Path) -> None:
    if (replay_path / f"000_{REPLAY_STEP}.json").exists():
        raise FailClosedRuntimeError(
            "G38-01 failed closed: replay artifact already exists"
        )


def _verify_hash(value: dict[str, Any], field: str, message: str) -> None:
    actual = value.get(field)
    if not isinstance(actual, str) or not actual.startswith("sha256:"):
        raise FailClosedRuntimeError(message)
    expected = deepcopy(value)
    expected.pop(field, None)
    if replay_hash(expected) != actual:
        raise FailClosedRuntimeError(message)


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"G38-01 requires {field}")
    return value


def _require_hash(value: Any, field: str) -> str:
    text = _require_string(value, field)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(f"G38-01 requires canonical {field}")
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
