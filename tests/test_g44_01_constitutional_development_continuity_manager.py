"""Deterministic certification coverage for G44-01."""

from __future__ import annotations

from copy import deepcopy
import json

import pytest

from aigol.runtime.constitutional_development_continuity_manager_runtime import (
    CHECKPOINT_ACTIVE,
    CHECKPOINT_INVALIDATED,
    CONTINUATION_AUTHORIZED,
    RESUME_FAILED_CLOSED,
    create_constitutional_development_checkpoint,
    invalidate_constitutional_development_checkpoint,
    reconstruct_constitutional_development_checkpoint_replay,
    reconstruct_constitutional_development_continuation_replay,
    record_external_repair_continuity_evidence,
    validate_constitutional_development_checkpoint_artifact,
    verify_constitutional_development_resume,
)
from aigol.runtime.constitutional_development_supervisor_runtime import (
    supervise_constitutional_development_workflow,
)
from aigol.runtime.constitutional_development_workflow_integration_runtime import (
    plan_constitutional_development_validation,
)
from aigol.runtime.implementation_manifest_runtime import (
    CREATE_ONLY,
    create_implementation_manifest,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_certification_registry import (
    is_platform_capability_certified,
    lookup_platform_capability_certification,
)
from aigol.runtime.platform_change_normalization_runtime import (
    normalize_platform_change,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-07-28T00:00:00Z"


def _hash(label: str) -> str:
    return replay_hash({"label": label})


def _normalized_change(tmp_path, name: str = "base") -> dict:
    target = "aigol/runtime/constitutional_development_continuity_manager_runtime.py"
    manifest = create_implementation_manifest(
        manifest_id=f"MANIFEST-G44-01-{name}",
        canonical_chain_id=f"CHAIN-G44-01-{name}",
        implementation_bundle_id=f"G44_01_CONTINUITY_{name}",
        source_candidate_reference=f"CANDIDATE-G44-01-{name}",
        source_candidate_hash=_hash(f"candidate-{name}"),
        implementation_handoff_reference=f"HANDOFF-G44-01-{name}",
        implementation_handoff_hash=_hash(f"handoff-{name}"),
        provider_generation_authorization_reference=f"AUTH-G44-01-{name}",
        provider_generation_authorization_hash=_hash(f"authorization-{name}"),
        provider_response_reference=f"RESPONSE-G44-01-{name}",
        provider_response_hash=_hash(f"response-{name}"),
        target_domain="PLATFORM_CORE",
        target_resource="CONSTITUTIONAL_DEVELOPMENT_CONTINUITY_MANAGER",
        target_worker=None,
        generated_files=[
            {
                "file_entry_id": "FILE-G44-01-000001",
                "target_path": target,
                "artifact_type": "PYTHON_RUNTIME_MODULE",
                "operation": CREATE_ONLY,
                "content": f"G44-01 deterministic content {name}\n",
                "validation_requirements": [],
            }
        ],
        generated_tests=[],
        validation_requirements=[
            "python -m pytest "
            "tests/test_g44_01_constitutional_development_continuity_manager.py"
        ],
        known_gaps=[],
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"manifest_{name}",
    )["implementation_manifest_artifact"]
    return normalize_platform_change(
        normalization_id=f"NORMALIZATION-G44-01-{name}",
        source_artifact=manifest,
        source_reference=manifest["manifest_id"],
        source_hash=manifest["artifact_hash"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"normalization_{name}",
    )["normalized_change_artifact"]


def _workflow(
    tmp_path,
    source: dict,
    name: str,
    *,
    blocked: bool,
) -> tuple[dict, object]:
    capture = plan_constitutional_development_validation(
        workflow_id=f"WORKFLOW-G44-01-{name}",
        session_id=f"SESSION-G44-01-{name}",
        normalized_change_artifact=source,
        normalized_change_reference=source["normalization_id"],
        normalized_change_hash=(
            _hash("incorrect-binding")
            if blocked
            else source["normalized_change_hash"]
        ),
        created_by="PLATFORM_CORE_VALIDATION_PLANNING",
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"workflow_{name}",
        failure_context=None,
    )
    return (
        capture[
            "constitutional_development_validation_workflow_artifact"
        ],
        tmp_path / f"workflow_{name}",
    )


def _supervise(
    tmp_path,
    workflow: dict,
    workflow_replay,
    name: str,
) -> tuple[dict, object]:
    capture = supervise_constitutional_development_workflow(
        diagnosis_id=f"DIAGNOSIS-G44-01-{name}",
        workflow_artifact=workflow,
        workflow_reference=workflow["workflow_id"],
        workflow_hash=workflow["workflow_hash"],
        workflow_artifact_hash=workflow["artifact_hash"],
        workflow_replay_dir=workflow_replay,
        observed_by="PLATFORM_CORE_DEVELOPMENT_SUPERVISION",
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"supervisor_{name}",
    )
    return (
        capture[
            "constitutional_development_supervisor_diagnosis_artifact"
        ],
        tmp_path / f"supervisor_{name}",
    )


def _checkpoint(tmp_path, name: str = "base") -> dict:
    source = _normalized_change(tmp_path, name)
    workflow, workflow_replay = _workflow(
        tmp_path, source, f"{name}_blocked", blocked=True
    )
    diagnosis, supervisor_replay = _supervise(
        tmp_path, workflow, workflow_replay, f"{name}_blocked"
    )
    return create_constitutional_development_checkpoint(
        workflow_artifact=workflow,
        workflow_reference=workflow["workflow_id"],
        workflow_hash=workflow["workflow_hash"],
        workflow_artifact_hash=workflow["artifact_hash"],
        workflow_replay_dir=workflow_replay,
        supervisor_diagnosis_artifact=diagnosis,
        supervisor_diagnosis_reference=diagnosis["diagnosis_id"],
        supervisor_diagnosis_hash=diagnosis["diagnosis_hash"],
        supervisor_diagnosis_artifact_hash=diagnosis["artifact_hash"],
        supervisor_replay_dir=supervisor_replay,
        created_by="PLATFORM_CORE_DEVELOPMENT_CONTINUITY",
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"checkpoint_{name}",
    )


def _validation_reference(scope_hash: str) -> dict:
    base = {
        "validation_evidence_id": "VALIDATION-EVIDENCE-G44-01",
        "validation_artifact_hash": _hash("validation-artifact"),
        "validation_status": "VALIDATION_PASSED",
        "validated_scope_hash": scope_hash,
    }
    return {**base, "evidence_hash": replay_hash(base)}


def _healthy_post_repair(
    tmp_path,
    name: str = "post",
    source_name: str = "base",
):
    with (tmp_path / f"normalization_{source_name}" /
          "000_normalized_change_recorded.json").open(
        "r",
        encoding="utf-8",
    ) as handle:
        source = json.load(handle)["artifact"]
    workflow, workflow_replay = _workflow(
        tmp_path, source, name, blocked=False
    )
    diagnosis, supervisor_replay = _supervise(
        tmp_path, workflow, workflow_replay, name
    )
    return workflow, workflow_replay, diagnosis, supervisor_replay


def _repair_evidence(
    checkpoint: dict,
    resume_point: dict,
    post_workflow: dict,
    *,
    boundaries: list[str] | None = None,
    superseding: str | None = None,
) -> dict:
    scope_hash = checkpoint["required_revalidation_scope_hash"]
    return record_external_repair_continuity_evidence(
        repair_evidence_id="REPAIR-EVIDENCE-G44-01",
        checkpoint_artifact=checkpoint,
        resume_point_artifact=resume_point,
        pre_repair_workflow_reference=checkpoint["workflow_reference"],
        pre_repair_workflow_hash=checkpoint["workflow_hash"],
        post_repair_workflow_reference=post_workflow["workflow_id"],
        post_repair_workflow_hash=post_workflow["workflow_hash"],
        modified_boundaries=boundaries
        or [checkpoint["certified_repair_boundary"]["boundary"]],
        affected_capability_identifiers=checkpoint[
            "affected_capability_identifiers"
        ],
        validation_scope_hash=scope_hash,
        validation_evidence_references=[
            _validation_reference(scope_hash)
        ],
        human_approval_reference="HUMAN-APPROVAL-G44-01",
        human_approval_hash=_hash("human-approval"),
        superseding_mutation_reference=superseding,
        recorded_by="EXTERNAL_REPAIR_PROCESS",
        recorded_at=CREATED_AT,
    )


def _resume(
    tmp_path,
    capture: dict,
    post_workflow: dict,
    post_workflow_replay,
    post_diagnosis: dict,
    post_supervisor_replay,
    repair_evidence: dict,
    *,
    name: str = "resume",
    invalidation: dict | None = None,
) -> dict:
    checkpoint = capture["constitutional_development_checkpoint_artifact"]
    resume_point = capture[
        "constitutional_development_resume_point_artifact"
    ]
    return verify_constitutional_development_resume(
        continuation_id=f"CONTINUATION-G44-01-{name}",
        checkpoint_artifact=checkpoint,
        resume_point_artifact=resume_point,
        checkpoint_invalidation_artifact=invalidation,
        external_repair_evidence_artifact=repair_evidence,
        post_repair_workflow_artifact=post_workflow,
        post_repair_workflow_reference=post_workflow["workflow_id"],
        post_repair_workflow_hash=post_workflow["workflow_hash"],
        post_repair_workflow_artifact_hash=post_workflow["artifact_hash"],
        post_repair_workflow_replay_dir=post_workflow_replay,
        post_repair_supervisor_diagnosis_artifact=post_diagnosis,
        post_repair_supervisor_diagnosis_reference=post_diagnosis[
            "diagnosis_id"
        ],
        post_repair_supervisor_diagnosis_hash=post_diagnosis[
            "diagnosis_hash"
        ],
        post_repair_supervisor_diagnosis_artifact_hash=post_diagnosis[
            "artifact_hash"
        ],
        post_repair_supervisor_replay_dir=post_supervisor_replay,
        verified_by="PLATFORM_CORE_DEVELOPMENT_CONTINUITY",
        verified_at=CREATED_AT,
        replay_dir=tmp_path / name,
    )


def test_checkpoint_and_resume_point_are_immutable_and_reconstructable(
    tmp_path,
) -> None:
    capture = _checkpoint(tmp_path)
    checkpoint = capture["constitutional_development_checkpoint_artifact"]
    resume_point = capture[
        "constitutional_development_resume_point_artifact"
    ]

    assert checkpoint["checkpoint_status"] == CHECKPOINT_ACTIVE
    assert checkpoint["workflow_position"]["blocked_boundary_rank"] == 1
    assert resume_point["must_not_repeat_boundary_ranks"] == [0]
    assert resume_point["must_not_skip_boundary_ranks"] == list(range(1, 10))
    assert checkpoint["authority_flags"]["performs_repair"] is False
    reconstructed = reconstruct_constitutional_development_checkpoint_replay(
        capture["replay_reference"]
    )
    assert reconstructed["checkpoint_hash"] == checkpoint["checkpoint_hash"]
    assert reconstructed["resume_point_hash"] == resume_point["resume_point_hash"]


def test_checkpoint_is_deterministic_for_identical_evidence(tmp_path) -> None:
    first = _checkpoint(tmp_path / "first", "same")
    second = _checkpoint(tmp_path / "second", "same")
    assert first["checkpoint_hash"] == second["checkpoint_hash"]
    assert first["resume_point_hash"] == second["resume_point_hash"]


def test_compliant_external_repair_authorizes_only_workflow_continuation(
    tmp_path,
) -> None:
    capture = _checkpoint(tmp_path)
    checkpoint = deepcopy(
        capture["constitutional_development_checkpoint_artifact"]
    )
    resume_point = capture[
        "constitutional_development_resume_point_artifact"
    ]
    post = _healthy_post_repair(tmp_path)
    evidence = _repair_evidence(checkpoint, resume_point, post[0])
    result = _resume(tmp_path, capture, *post, evidence)

    assert result["continuation_status"] == CONTINUATION_AUTHORIZED
    assert result["continuation_authorized"] is True
    assert result["execution_authorized"] is False
    assert result["validation_executed"] is False
    assert result["repair_performed"] is False
    assert capture["constitutional_development_checkpoint_artifact"] == checkpoint
    reconstruction = reconstruct_constitutional_development_continuation_replay(
        result["replay_reference"]
    )
    assert reconstruction["continuation_authorized"] is True
    assert reconstruction["execution_authorized"] is False


def test_out_of_boundary_repair_fails_closed(tmp_path) -> None:
    capture = _checkpoint(tmp_path)
    checkpoint = capture["constitutional_development_checkpoint_artifact"]
    resume_point = capture[
        "constitutional_development_resume_point_artifact"
    ]
    post = _healthy_post_repair(tmp_path)
    evidence = _repair_evidence(
        checkpoint,
        resume_point,
        post[0],
        boundaries=["IVE_0_IMPACT_ANALYSIS"],
    )
    result = _resume(tmp_path, capture, *post, evidence)
    assert result["continuation_status"] == RESUME_FAILED_CLOSED
    assert "exceeded the certified boundary" in result["failure_reason"]


def test_invalidated_and_superseded_checkpoints_cannot_resume(tmp_path) -> None:
    capture = _checkpoint(tmp_path)
    checkpoint = capture["constitutional_development_checkpoint_artifact"]
    resume_point = capture[
        "constitutional_development_resume_point_artifact"
    ]
    invalidation_capture = invalidate_constitutional_development_checkpoint(
        invalidation_id="INVALIDATION-G44-01",
        checkpoint_artifact=checkpoint,
        resume_point_artifact=resume_point,
        invalidation_reason="SUPERSEDED_BY_EXTERNAL_MUTATION",
        superseding_evidence_reference="MUTATION-G44-01",
        superseding_evidence_hash=_hash("superseding-mutation"),
        invalidated_by="HUMAN_AUTHORITY",
        invalidated_at=CREATED_AT,
        replay_dir=tmp_path / "invalidation",
    )
    assert invalidation_capture["invalidation_status"] == CHECKPOINT_INVALIDATED
    post = _healthy_post_repair(tmp_path)
    evidence = _repair_evidence(checkpoint, resume_point, post[0])
    result = _resume(
        tmp_path,
        capture,
        *post,
        evidence,
        invalidation=invalidation_capture[
            "checkpoint_invalidation_artifact"
        ],
    )
    assert result["continuation_status"] == RESUME_FAILED_CLOSED
    assert "stale checkpoint" in result["failure_reason"]


def test_tamper_replay_mismatch_and_duplicate_resume_fail_closed(
    tmp_path,
) -> None:
    capture = _checkpoint(tmp_path)
    checkpoint = deepcopy(
        capture["constitutional_development_checkpoint_artifact"]
    )
    checkpoint["workflow_hash"] = _hash("tampered")
    with pytest.raises(FailClosedRuntimeError):
        validate_constitutional_development_checkpoint_artifact(checkpoint)

    resume_point = capture[
        "constitutional_development_resume_point_artifact"
    ]
    post = _healthy_post_repair(tmp_path)
    evidence = _repair_evidence(
        capture["constitutional_development_checkpoint_artifact"],
        resume_point,
        post[0],
    )
    first = _resume(tmp_path, capture, *post, evidence, name="duplicate")
    second = _resume(tmp_path, capture, *post, evidence, name="duplicate")
    assert first["continuation_status"] == CONTINUATION_AUTHORIZED
    assert second["continuation_status"] == RESUME_FAILED_CLOSED
    assert "replay artifact already exists" in second["failure_reason"]


def test_missing_validation_evidence_and_source_lineage_fail_closed(
    tmp_path,
) -> None:
    capture = _checkpoint(tmp_path)
    checkpoint = capture["constitutional_development_checkpoint_artifact"]
    resume_point = capture[
        "constitutional_development_resume_point_artifact"
    ]
    post = _healthy_post_repair(tmp_path)
    evidence = _repair_evidence(checkpoint, resume_point, post[0])
    evidence["validation_evidence_references"] = []
    evidence["validation_evidence_count"] = 0
    evidence.pop("artifact_hash")
    evidence.pop("repair_evidence_hash")
    evidence["repair_evidence_hash"] = replay_hash(evidence)
    evidence["artifact_hash"] = replay_hash(evidence)
    result = _resume(tmp_path, capture, *post, evidence, name="missing")
    assert result["continuation_status"] == RESUME_FAILED_CLOSED

    _normalized_change(tmp_path / "different", "different")
    different_post = _healthy_post_repair(
        tmp_path / "different",
        "different",
        "different",
    )
    valid_evidence = _repair_evidence(
        checkpoint, resume_point, different_post[0]
    )
    lineage_result = _resume(
        tmp_path,
        capture,
        *different_post,
        valid_evidence,
        name="lineage",
    )
    assert lineage_result["continuation_status"] == RESUME_FAILED_CLOSED
    assert "preserved certified stage lineage changed" in (
        lineage_result["failure_reason"]
    )


def test_replay_mismatch_and_skipped_stage_evidence_are_rejected(
    tmp_path,
) -> None:
    capture = _checkpoint(tmp_path)
    checkpoint_replay = tmp_path / "checkpoint_base"
    with (checkpoint_replay / "000_g42_workflow_bound.json").open(
        "r",
        encoding="utf-8",
    ) as handle:
        workflow = json.load(handle)["artifact"]
    with (checkpoint_replay / "001_g43_supervisor_diagnosis_bound.json").open(
        "r",
        encoding="utf-8",
    ) as handle:
        diagnosis = json.load(handle)["artifact"]
    workflow_replay = tmp_path / "workflow_base_blocked"
    workflow_wrapper_path = (
        workflow_replay / "000_normalized_change_bound.json"
    )
    with workflow_wrapper_path.open("r", encoding="utf-8") as handle:
        wrapper = json.load(handle)
    wrapper["replay_hash"] = _hash("tampered-replay")
    with workflow_wrapper_path.open("w", encoding="utf-8") as handle:
        json.dump(wrapper, handle)
    mismatched = create_constitutional_development_checkpoint(
        workflow_artifact=workflow,
        workflow_reference=workflow["workflow_id"],
        workflow_hash=workflow["workflow_hash"],
        workflow_artifact_hash=workflow["artifact_hash"],
        workflow_replay_dir=workflow_replay,
        supervisor_diagnosis_artifact=diagnosis,
        supervisor_diagnosis_reference=diagnosis["diagnosis_id"],
        supervisor_diagnosis_hash=diagnosis["diagnosis_hash"],
        supervisor_diagnosis_artifact_hash=diagnosis["artifact_hash"],
        supervisor_replay_dir=tmp_path / "supervisor_base_blocked",
        created_by="PLATFORM_CORE_DEVELOPMENT_CONTINUITY",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "checkpoint_replay_mismatch",
    )
    assert mismatched["fail_closed"] is True
    assert "replay hash mismatch" in mismatched["failure_reason"]

    post = _healthy_post_repair(tmp_path)
    checkpoint = capture["constitutional_development_checkpoint_artifact"]
    resume_point = capture[
        "constitutional_development_resume_point_artifact"
    ]
    evidence = _repair_evidence(checkpoint, resume_point, post[0])
    supervisor_evidence_path = (
        post[3] / "001_diagnosis_evidence_recorded.json"
    )
    with supervisor_evidence_path.open("r", encoding="utf-8") as handle:
        skipped_wrapper = json.load(handle)
    skipped_wrapper["artifact"]["boundary_observations"] = [
        item
        for item in skipped_wrapper["artifact"]["boundary_observations"]
        if item["boundary_rank"] != 6
    ]
    with supervisor_evidence_path.open("w", encoding="utf-8") as handle:
        json.dump(skipped_wrapper, handle)
    skipped = _resume(
        tmp_path,
        capture,
        *post,
        evidence,
        name="skipped_stage",
    )
    assert skipped["continuation_status"] == RESUME_FAILED_CLOSED
    assert skipped["continuation_authorized"] is False


def test_g44_registry_and_authority_boundaries() -> None:
    record = lookup_platform_capability_certification(
        "CONSTITUTIONAL_DEVELOPMENT_CONTINUITY_MANAGER"
    )
    assert is_platform_capability_certified(
        "CONSTITUTIONAL_DEVELOPMENT_CONTINUITY_MANAGER"
    )
    assert record["certification_milestone"] == "G44-01"
    assert record["runtime_execution_authority"] is False
    assert record["worker_invoked"] is False
    assert record["provider_invoked"] is False
