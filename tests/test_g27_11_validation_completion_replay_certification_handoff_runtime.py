"""Focused tests for G27-11 validation completion certification handoff."""

from __future__ import annotations

import inspect

from aigol.runtime.architectural_health_advisory import (
    create_platform_digital_twin_evidence_bundle,
    generate_architectural_health_advisory,
)
from aigol.runtime.governed_validation_runtime import (
    GOVERNED_VALIDATION_COMPLETED,
    GOVERNED_VALIDATION_COMPLETION_ARTIFACT_V1,
)
from aigol.runtime.governed_validation_suite_runtime import (
    GOVERNED_VALIDATION_SUITE_COMPLETED,
    GOVERNED_VALIDATION_SUITE_COMPLETION_ARTIFACT_V1,
    VALIDATION_SUITE_FAILED,
    VALIDATION_SUITE_SUMMARY_ARTIFACT_V1,
)
from aigol.runtime.platform_capability_certification_registry import (
    lookup_platform_capability_certification,
)
from aigol.runtime.platform_core_validation_replay import (
    VALIDATION_REPLAY_STEPS,
    persist_validation_replay_step,
)
from aigol.runtime.platform_core_validation_result import VALIDATION_RESULT_ARTIFACT_V1
from aigol.runtime.platform_core_validation_suite_replay import (
    VALIDATION_SUITE_REPLAY_STEPS,
    persist_validation_suite_replay_step,
)
from aigol.runtime.replay_certification_runtime import (
    REPLAY_CERTIFICATION_COMPLETED,
    certify_validated_replay,
)
from aigol.runtime.result_validation_runtime import (
    RESULT_VALIDATION_ARTIFACT_V1,
    RESULT_VALIDATION_COMPLETED,
)
from aigol.runtime.transport.serialization import replay_hash
from aigol.runtime.validation_completion_replay_certification_handoff_runtime import (
    FAILED_CLOSED,
    VALIDATION_COMPLETION_HANDOFF_READY,
    VALIDATION_COMPLETION_REPLAY_CERTIFICATION_HANDOFF_ARTIFACT_V1,
    compose_validation_completion_replay_certification_handoff,
    reconstruct_validation_completion_replay_certification_handoff,
    validate_validation_completion_replay_certification_handoff_artifact,
)
from aigol.workers.validation_command_worker import VALIDATION_FAILED, VALIDATION_PASSED


CREATED_AT = "2026-07-13T00:00:00Z"
PLAN_LINEAGE = {
    "source_artifact_type": "PLATFORM_VALIDATION_PLAN_ARTIFACT_V1",
    "validation_plan_id": "PLAN-000001",
    "validation_plan_artifact_hash": "sha256:" + "1" * 64,
    "validation_plan_hash": "sha256:" + "2" * 64,
    "platform_change_impact_reference": "IMPACT-000001",
    "platform_change_impact_hash": "sha256:" + "3" * 64,
    "replay_visible": True,
}


def _hashed(artifact: dict, field: str = "artifact_hash") -> dict:
    result = dict(artifact)
    result[field] = replay_hash(result)
    return result


def _single_replay(tmp_path, *, completed: bool = True):
    replay_dir = tmp_path / "single_validation"
    candidate = _hashed(
        {
            "artifact_type": "VALIDATION_CANDIDATE_ARTIFACT_V1",
            "candidate_id": "SINGLE-CANDIDATE",
            "command_id": "PY_COMPILE_AIGOL",
            "command_spec_hash": "sha256:" + "4" * 64,
            "argv_hash": "sha256:" + "5" * 64,
            "associated_reference": PLAN_LINEAGE,
        }
    )
    approval = _hashed({"candidate_hash": candidate["artifact_hash"], "approval_id": "APPROVAL"})
    authorization = _hashed(
        {"proposal_id": candidate["candidate_id"], "authorization_id": "AUTHORIZATION"},
        "authorization_hash",
    )
    request = _hashed(
        {"authorization_hash": authorization["authorization_hash"], "request_id": "REQUEST"},
        "request_hash",
    )
    pre_execution = _hashed({"command_spec_hash": candidate["command_spec_hash"]})
    worker_result = _hashed(
        {
            "argv_hash": candidate["argv_hash"],
            "validation_status": VALIDATION_PASSED,
            "worker_invoked": True,
        }
    )
    validation_result = _hashed(
        {
            "artifact_type": VALIDATION_RESULT_ARTIFACT_V1,
            "execution_id": "SINGLE-EXECUTION",
            "candidate_id": candidate["candidate_id"],
            "candidate_hash": candidate["artifact_hash"],
            "validation_status": VALIDATION_PASSED,
            "exit_code": 0,
            "timed_out": False,
        }
    )
    completion = _hashed(
        {
            "artifact_type": GOVERNED_VALIDATION_COMPLETION_ARTIFACT_V1,
            "execution_id": "SINGLE-EXECUTION",
            "execution_status": GOVERNED_VALIDATION_COMPLETED if completed else FAILED_CLOSED,
            "candidate_id": candidate["candidate_id"],
            "candidate_hash": candidate["artifact_hash"],
            "validation_result_hash": validation_result["artifact_hash"],
            "git_performed": False,
            "deployment_performed": False,
            "provider_invoked": False,
            "fail_closed": not completed,
        }
    )
    artifacts = [
        candidate,
        approval,
        authorization,
        request,
        pre_execution,
        worker_result,
        validation_result,
        completion,
    ]
    for index, artifact in enumerate(artifacts):
        persist_validation_replay_step(replay_dir, index, VALIDATION_REPLAY_STEPS[index], artifact)
    return replay_dir, validation_result


def _suite_replay(tmp_path):
    replay_dir = tmp_path / "suite_validation"
    candidate = _hashed(
        {
            "artifact_type": "VALIDATION_SUITE_CANDIDATE_ARTIFACT_V1",
            "candidate_id": "SUITE-CANDIDATE",
            "command_count": 2,
            "associated_reference": PLAN_LINEAGE,
        }
    )
    approval = _hashed({"candidate_hash": candidate["artifact_hash"], "approval_id": "SUITE-APPROVAL"})
    authorization = _hashed(
        {
            "candidate_hash": candidate["artifact_hash"],
            "approval_hash": approval["artifact_hash"],
            "authorization_id": "SUITE-AUTHORIZATION",
        }
    )
    pre_suite = _hashed({"candidate_hash": candidate["artifact_hash"]})
    command_execution = _hashed(
        {
            "candidate_hash": candidate["artifact_hash"],
            "worker_invoked_count": 1,
            "command_results": [],
        }
    )
    summary = _hashed(
        {
            "artifact_type": VALIDATION_SUITE_SUMMARY_ARTIFACT_V1,
            "execution_id": "SUITE-EXECUTION",
            "candidate_id": candidate["candidate_id"],
            "candidate_hash": candidate["artifact_hash"],
            "command_execution_hash": command_execution["artifact_hash"],
            "executed_command_count": 1,
            "validation_suite_status": VALIDATION_SUITE_FAILED,
            "validation_suite_passed": False,
        }
    )
    bundle = create_platform_digital_twin_evidence_bundle(
        bundle_id="SUITE-EVIDENCE",
        component_scope="Governed Validation Suite",
        evidence_records=[
            {
                "evidence_id": "SUITE-SUMMARY",
                "source_path": "runtime:governed_validation_suite",
                "source_title": "Governed Validation Suite",
                "milestone_id": "G9-13",
                "source_class": "runtime_evidence",
                "status": VALIDATION_SUITE_FAILED,
                "final_verdict": "VALIDATION_SUITE_FAILED",
                "component_scope": "Governed Validation Suite",
                "expected_owner": "Platform Core",
                "observed_owner": "Platform Core",
                "evidence_type": "validation_suite_summary",
                "boundary": "Platform Core coordinates validation",
                "replay_reference": str(replay_dir),
                "governance_reference": candidate["candidate_id"],
                "validation_evidence": summary,
            }
        ],
        created_at=CREATED_AT,
    )
    advisory = generate_architectural_health_advisory(
        projection_id="SUITE-ADVISORY",
        digital_twin_evidence=bundle,
        generated_at=CREATED_AT,
    )
    completion = _hashed(
        {
            "artifact_type": GOVERNED_VALIDATION_SUITE_COMPLETION_ARTIFACT_V1,
            "execution_id": "SUITE-EXECUTION",
            "execution_status": GOVERNED_VALIDATION_SUITE_COMPLETED,
            "candidate_id": candidate["candidate_id"],
            "candidate_hash": candidate["artifact_hash"],
            "suite_summary_hash": summary["artifact_hash"],
            "architectural_health_advisory_hash": advisory["artifact_hash"],
            "worker_invoked_count": 1,
            "fail_closed": False,
        }
    )
    artifacts = [candidate, approval, authorization, pre_suite, command_execution, summary, advisory, completion]
    for index, artifact in enumerate(artifacts):
        persist_validation_suite_replay_step(
            replay_dir,
            index,
            VALIDATION_SUITE_REPLAY_STEPS[index],
            artifact,
        )
    return replay_dir, summary


def _compose(tmp_path, source, source_replay, name="handoff"):
    return compose_validation_completion_replay_certification_handoff(
        handoff_id="HANDOFF-000001",
        validation_artifact=source,
        validation_replay_reference=source_replay,
        composed_by="PLATFORM_CORE",
        composed_at=CREATED_AT,
        replay_dir=tmp_path / name,
    )


def test_single_validation_completion_composes_existing_certification_input(tmp_path) -> None:
    source_replay, source = _single_replay(tmp_path)
    capture = _compose(tmp_path, source, source_replay)
    result = capture["result_validation_artifact"]

    assert capture["handoff_status"] == VALIDATION_COMPLETION_HANDOFF_READY
    assert result["artifact_type"] == RESULT_VALIDATION_ARTIFACT_V1
    assert result["validation_status"] == RESULT_VALIDATION_COMPLETED
    assert result["source_validation_artifact_type"] == VALIDATION_RESULT_ARTIFACT_V1
    assert result["source_validation_artifact_hash"] == source["artifact_hash"]
    assert result["replay_lineage_preserved"] is True
    assert result["deterministic_validation_preserved"] is True
    assert result["ready_for_replay_certification"] is True
    assert result["certification_readiness"]["requires_replay_certification"] is True
    assert result["plan_lineage"] == PLAN_LINEAGE
    assert capture["certification_performed"] is False


def test_suite_failure_is_completed_evidence_and_becomes_certification_input(tmp_path) -> None:
    source_replay, source = _suite_replay(tmp_path)
    capture = _compose(tmp_path, source, source_replay, "suite_handoff")
    result = capture["result_validation_artifact"]

    assert capture["handoff_status"] == VALIDATION_COMPLETION_HANDOFF_READY
    assert result["source_validation_artifact_type"] == VALIDATION_SUITE_SUMMARY_ARTIFACT_V1
    assert result["source_validation_status"] == VALIDATION_SUITE_FAILED
    assert result["plan_lineage_preserved"] is True
    assert result["ready_for_replay_certification"] is True


def test_composed_contract_is_accepted_by_existing_replay_certification(tmp_path) -> None:
    source_replay, source = _single_replay(tmp_path)
    handoff = _compose(tmp_path, source, source_replay)
    certification = certify_validated_replay(
        certification_id="REPLAY-CERTIFICATION-000001",
        result_validation_artifact=handoff["result_validation_artifact"],
        certified_by="PLATFORM_CORE_CERTIFICATION",
        certified_at=CREATED_AT,
        replay_dir=tmp_path / "certification",
    )

    assert certification["certification_status"] == REPLAY_CERTIFICATION_COMPLETED
    assert certification["replay_certification_completed"] is True


def test_handoff_replay_reconstructs_embedded_contract(tmp_path) -> None:
    source_replay, source = _single_replay(tmp_path)
    capture = _compose(tmp_path, source, source_replay)
    reconstructed = reconstruct_validation_completion_replay_certification_handoff(tmp_path / "handoff")

    assert reconstructed["handoff_status"] == VALIDATION_COMPLETION_HANDOFF_READY
    assert reconstructed["result_validation_artifact_hash"] == capture["result_validation_artifact"]["artifact_hash"]
    assert reconstructed["plan_lineage_preserved"] is True
    assert reconstructed["ready_for_replay_certification"] is True


def test_incomplete_validation_lifecycle_fails_closed(tmp_path) -> None:
    source_replay, source = _single_replay(tmp_path, completed=False)
    capture = _compose(tmp_path, source, source_replay)

    assert capture["handoff_status"] == FAILED_CLOSED
    assert capture["result_validation_artifact"] is None
    assert capture["ready_for_replay_certification"] is False
    assert "completed validation lifecycle required" in capture["failure_reason"]


def test_source_not_identical_to_replay_artifact_fails_closed(tmp_path) -> None:
    source_replay, source = _single_replay(tmp_path)
    changed = dict(source)
    changed["execution_id"] = "DIFFERENT"
    changed.pop("artifact_hash")
    changed["artifact_hash"] = replay_hash(changed)
    capture = _compose(tmp_path, changed, source_replay)

    assert capture["handoff_status"] == FAILED_CLOSED
    assert "replay source artifact mismatch" in capture["failure_reason"]


def test_unsupported_artifact_type_fails_closed(tmp_path) -> None:
    source = _hashed({"artifact_type": "GOVERNED_VALIDATION_COMPLETION_ARTIFACT_V1"})
    capture = _compose(tmp_path, source, tmp_path / "missing")

    assert capture["handoff_status"] == FAILED_CLOSED
    assert "unsupported validation artifact type" in capture["failure_reason"]


def test_handoff_validator_rejects_tampering(tmp_path) -> None:
    source_replay, source = _single_replay(tmp_path)
    artifact = _compose(tmp_path, source, source_replay)["handoff_artifact"]
    artifact["certification_performed"] = True

    try:
        validate_validation_completion_replay_certification_handoff_artifact(artifact)
    except Exception as exc:
        assert "hash mismatch" in str(exc)
    else:
        raise AssertionError("tampered handoff must fail closed")


def test_capability_is_registered() -> None:
    record = lookup_platform_capability_certification(
        "VALIDATION_COMPLETION_REPLAY_CERTIFICATION_HANDOFF"
    )

    assert record["certification_milestone"] == "G27-11"
    assert record["architectural_owner"] == "PLATFORM_CORE"
    assert record["human_interface_authority"] is False


def test_runtime_has_no_execution_or_certification_invocation_surfaces() -> None:
    import aigol.runtime.validation_completion_replay_certification_handoff_runtime as runtime

    source = inspect.getsource(runtime)
    assert "execute_governed_validation(" not in source
    assert "execute_governed_validation_suite(" not in source
    assert "execute_validation_command_request(" not in source
    assert "certify_validated_replay(" not in source
    assert "subprocess." not in source
    assert "aigol.cli" not in source
