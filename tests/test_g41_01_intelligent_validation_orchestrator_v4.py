"""Deterministic certification coverage for G41-01 IVE-4."""

from __future__ import annotations

from copy import deepcopy
import json

import pytest

from aigol.runtime.governed_validation_runtime import (
    create_governed_validation_approval,
    create_governed_validation_candidate,
    execute_governed_validation,
)
from aigol.runtime.implementation_manifest_runtime import (
    CREATE_ONLY,
    create_implementation_manifest,
)
from aigol.runtime.intelligent_validation_orchestrator_v4 import (
    FAILED_CLOSED,
    FAILURE_REVALIDATION_PLANNING,
    FAILURE_REVALIDATION_PLANNING_BUNDLED,
    INITIAL_VALIDATION_PLANNING,
    INITIAL_VALIDATION_PLANNING_BUNDLED,
    IVE_3_NOT_APPLICABLE,
    orchestrate_intelligent_validation_planning,
    reconstruct_intelligent_validation_orchestration_replay,
    validate_unified_validation_planning_bundle_artifact,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_certification_registry import (
    is_platform_capability_certified,
    lookup_platform_capability_certification,
)
from aigol.runtime.platform_change_normalization_runtime import (
    normalize_platform_change,
)
from aigol.runtime.transport.serialization import load_json, replay_hash


CREATED_AT = "2026-07-28T00:00:00Z"


def _hash(label: str) -> str:
    return replay_hash({"label": label})


def _normalized_change(tmp_path) -> dict:
    targets = (
        ("aigol/cli/aigol_cli.py", "PYTHON_AICLI_MODULE"),
        (
            "tests/test_g41_01_intelligent_validation_orchestrator_v4.py",
            "PYTHON_TEST_MODULE",
        ),
    )
    manifest = create_implementation_manifest(
        manifest_id="MANIFEST-G41-01",
        canonical_chain_id="CHAIN-G41-01",
        implementation_bundle_id="G41_01_INTELLIGENT_VALIDATION_ORCHESTRATOR",
        source_candidate_reference="CANDIDATE-G41-01",
        source_candidate_hash=_hash("candidate"),
        implementation_handoff_reference="HANDOFF-G41-01",
        implementation_handoff_hash=_hash("handoff"),
        provider_generation_authorization_reference="AUTH-G41-01",
        provider_generation_authorization_hash=_hash("authorization"),
        provider_response_reference="RESPONSE-G41-01",
        provider_response_hash=_hash("response"),
        target_domain="PLATFORM_CORE",
        target_resource="INTELLIGENT_VALIDATION_ORCHESTRATOR_V4",
        target_worker=None,
        generated_files=[
            {
                "file_entry_id": f"FILE-G41-01-{index:06d}",
                "target_path": target_path,
                "artifact_type": artifact_type,
                "operation": CREATE_ONLY,
                "content": f"G41-01 deterministic content {index}\n",
                "validation_requirements": [],
            }
            for index, (target_path, artifact_type) in enumerate(
                targets,
                start=1,
            )
        ],
        generated_tests=[],
        validation_requirements=[
            "python -m pytest "
            "tests/test_g41_01_intelligent_validation_orchestrator_v4.py"
        ],
        known_gaps=[],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "manifest",
    )["implementation_manifest_artifact"]
    return normalize_platform_change(
        normalization_id="NORMALIZATION-G41-01",
        source_artifact=manifest,
        source_reference=manifest["manifest_id"],
        source_hash=manifest["artifact_hash"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "normalization",
    )["normalized_change_artifact"]


def _orchestrate(
    tmp_path,
    source: dict,
    *,
    mode: str = INITIAL_VALIDATION_PLANNING,
    failure_context: dict | None = None,
    name: str = "ive-4",
) -> dict:
    return orchestrate_intelligent_validation_planning(
        orchestration_id="ORCHESTRATION-G41-01",
        session_id="SESSION-G41-01",
        planning_mode=mode,
        normalized_change_artifact=source,
        normalized_change_reference=source["normalization_id"],
        normalized_change_hash=source["normalized_change_hash"],
        failure_context=failure_context,
        created_by="PLATFORM_CORE_VALIDATION_PLANNING",
        created_at=CREATED_AT,
        replay_dir=tmp_path / name,
    )


def _failed_validation(tmp_path) -> dict:
    candidate = create_governed_validation_candidate(
        candidate_id="CANDIDATE-G41-01-FAILED",
        session_id="SESSION-G41-01",
        command_id="PYTHON_VALIDATION_FAILS_FOR_TEST",
        validation_purpose="existing failed validation evidence for IVE-4",
        created_by="PLATFORM_CORE",
        created_at=CREATED_AT,
    )
    approval = create_governed_validation_approval(
        approval_id="APPROVAL-G41-01-FAILED",
        candidate_artifact=candidate,
        confirmation_text=(
            f"confirm validation {candidate['candidate_id']} "
            f"{candidate['artifact_hash']}"
        ),
        approved_by="HUMAN_OPERATOR",
        approved_at=CREATED_AT,
    )
    return execute_governed_validation(
        execution_id="EXECUTION-G41-01-FAILED",
        candidate_artifact=candidate,
        approval_artifact=approval,
        repository_root=".",
        executed_by="PLATFORM_CORE",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "validation",
    )["validation_result_artifact"]


def _group(schedule: dict, identifier: str) -> dict:
    return next(
        group
        for group in schedule["groups"]
        if group["validation_subject_identifier"] == identifier
    )


def test_initial_mode_composes_ive_0_through_ive_2_and_reconstructs(
    tmp_path,
) -> None:
    source = _normalized_change(tmp_path)
    original = deepcopy(source)
    capture = _orchestrate(tmp_path, source)
    bundle = capture["unified_validation_planning_bundle_artifact"]
    reconstructed = reconstruct_intelligent_validation_orchestration_replay(
        tmp_path / "ive-4"
    )

    assert bundle["bundle_status"] == INITIAL_VALIDATION_PLANNING_BUNDLED
    assert bundle["planning_mode"] == INITIAL_VALIDATION_PLANNING
    assert [item["boundary"] for item in bundle["stage_lineage"]] == [
        "IVE_0",
        "IVE_1",
        "G38_ENTRY",
        "IVE_2",
        "IVE_3",
    ]
    assert bundle["stage_lineage"][-1]["invocation_status"] == (
        "NOT_APPLICABLE"
    )
    assert bundle["stage_artifacts"]["ive_3"]["state_status"] == (
        IVE_3_NOT_APPLICABLE
    )
    assert bundle["current_planning_recommendation"][
        "recommendation_type"
    ] == "IVE_2_INITIAL_VALIDATION_SCHEDULE"
    assert bundle["current_planning_recommendation"]["groups"]
    assert bundle["human_approval"]["required_before_execution"] is True
    assert bundle["human_approval_recorded"] is False
    assert bundle["validation_executed"] is False
    assert bundle["automatic_repair_performed"] is False
    assert all(value is False for value in bundle["authority_flags"].values())
    assert source == original
    assert reconstructed["bundle_hash"] == bundle["bundle_hash"]
    assert validate_unified_validation_planning_bundle_artifact(
        bundle
    ) == bundle


def test_bundle_preserves_exact_nested_certified_stage_artifacts(tmp_path) -> None:
    source = _normalized_change(tmp_path)
    bundle = _orchestrate(tmp_path, source)[
        "unified_validation_planning_bundle_artifact"
    ]
    root = tmp_path / "ive-4"

    assert bundle["stage_artifacts"]["ive_0"] == load_json(
        root / "g38/ive_0/000_intelligent_validation_plan_recorded.json"
    )["artifact"]
    assert bundle["stage_artifacts"]["ive_1"] == load_json(
        root / "g38/ive_1/001_semantic_validation_selection_recorded.json"
    )["artifact"]
    assert bundle["stage_artifacts"]["g38"] == load_json(
        root / "g38/000_intelligent_validation_planning_entry_recorded.json"
    )["artifact"]
    assert bundle["stage_artifacts"]["ive_2"] == load_json(
        root / "ive_2/002_parallel_validation_schedule_recorded.json"
    )["artifact"]


def test_failure_mode_invokes_ive_3_and_bundles_revalidation_scope(
    tmp_path,
) -> None:
    source = _normalized_change(tmp_path)
    initial = _orchestrate(tmp_path, source, name="initial")[
        "unified_validation_planning_bundle_artifact"
    ]
    schedule = initial["stage_artifacts"]["ive_2"]
    group = _group(schedule, "AICLI")
    result = _failed_validation(tmp_path)
    context = {
        "validation_result_artifact": result,
        "validation_result_reference": result["execution_id"],
        "validation_result_hash": result["artifact_hash"],
        "validation_replay_dir": tmp_path / "validation",
        "failed_group_id": group["group_id"],
        "failed_group_hash": group["group_hash"],
        "failed_requirement_hashes": group["requirement_hashes"][:1],
        "observed_by": "HUMAN_OPERATOR",
    }
    bundle = _orchestrate(
        tmp_path,
        source,
        mode=FAILURE_REVALIDATION_PLANNING,
        failure_context=context,
        name="failure",
    )["unified_validation_planning_bundle_artifact"]

    assert bundle["bundle_status"] == (
        FAILURE_REVALIDATION_PLANNING_BUNDLED
    )
    assert bundle["stage_lineage"][-1]["invocation_status"] == "INVOKED"
    assert bundle["stage_artifacts"]["ive_3"]["analysis_status"] == (
        "VALIDATION_FAILURE_ANALYZED"
    )
    recommendation = bundle["current_planning_recommendation"]
    assert recommendation["recommendation_type"] == (
        "IVE_3_FAILURE_REVALIDATION_SCOPE"
    )
    assert recommendation["earliest_known_planning_boundary"]["boundary"] == (
        "IVE_0_DIRECT_IMPACT_RECOMMENDATION"
    )
    assert recommendation["recommended_revalidation_groups"]
    assert bundle["stage_artifacts"]["ive_3"] == load_json(
        tmp_path
        / "failure/ive_3/005_validation_failure_analysis_recorded.json"
    )["artifact"]
    assert reconstruct_intelligent_validation_orchestration_replay(
        tmp_path / "failure"
    )["bundle_status"] == FAILURE_REVALIDATION_PLANNING_BUNDLED


def test_orchestration_is_deterministic_for_identical_inputs(tmp_path) -> None:
    source = _normalized_change(tmp_path)
    first = _orchestrate(tmp_path, source, name="first")[
        "unified_validation_planning_bundle_artifact"
    ]
    second = _orchestrate(tmp_path, source, name="second")[
        "unified_validation_planning_bundle_artifact"
    ]

    assert first == second


def test_missing_failure_evidence_fails_closed_before_planning(tmp_path) -> None:
    source = _normalized_change(tmp_path)
    capture = _orchestrate(
        tmp_path,
        source,
        mode=FAILURE_REVALIDATION_PLANNING,
        failure_context=None,
    )
    bundle = capture["unified_validation_planning_bundle_artifact"]

    assert bundle["bundle_status"] == FAILED_CLOSED
    assert bundle["stage_artifacts"] == {}
    assert bundle["stage_lineage"] == []
    assert bundle["full_regression"]["required"] is True
    assert bundle["validation_executed"] is False
    assert "requires failure_context" in bundle["failure_reason"]
    assert reconstruct_intelligent_validation_orchestration_replay(
        tmp_path / "ive-4"
    )["fail_closed"] is True


def test_initial_mode_rejects_unexpected_failure_context(tmp_path) -> None:
    source = _normalized_change(tmp_path)
    bundle = _orchestrate(
        tmp_path,
        source,
        failure_context={},
    )["unified_validation_planning_bundle_artifact"]

    assert bundle["bundle_status"] == FAILED_CLOSED
    assert "prohibits failure_context" in bundle["failure_reason"]


def test_bundle_replay_tamper_is_rejected(tmp_path) -> None:
    source = _normalized_change(tmp_path)
    _orchestrate(tmp_path, source)
    replay_file = (
        tmp_path
        / "ive-4/006_unified_validation_planning_bundle_recorded.json"
    )
    wrapper = json.loads(replay_file.read_text(encoding="utf-8"))
    wrapper["artifact"]["validation_executed"] = True
    replay_file.write_text(
        json.dumps(wrapper, sort_keys=True),
        encoding="utf-8",
    )

    with pytest.raises(FailClosedRuntimeError, match="replay hash mismatch"):
        reconstruct_intelligent_validation_orchestration_replay(
            tmp_path / "ive-4"
        )


def test_public_bundle_validator_rejects_rehashed_nested_stage_tamper(
    tmp_path,
) -> None:
    source = _normalized_change(tmp_path)
    bundle = _orchestrate(tmp_path, source)[
        "unified_validation_planning_bundle_artifact"
    ]
    bundle["stage_artifacts"]["g38"]["validation_executed"] = True
    bundle["bundle_hash"] = replay_hash(
        {
            key: value
            for key, value in bundle.items()
            if key not in {"bundle_hash", "artifact_hash"}
        }
    )
    bundle["artifact_hash"] = replay_hash(
        {
            key: value
            for key, value in bundle.items()
            if key != "artifact_hash"
        }
    )

    with pytest.raises(
        FailClosedRuntimeError,
        match="artifact hash mismatch",
    ):
        validate_unified_validation_planning_bundle_artifact(bundle)


def test_ive_4_has_no_execution_repair_or_transport_dependencies() -> None:
    module = __import__(
        "aigol.runtime.intelligent_validation_orchestrator_v4",
        fromlist=["unused"],
    )
    runtime_source = open(module.__file__, encoding="utf-8").read()

    assert "execute_governed_validation" not in runtime_source
    assert "import subprocess" not in runtime_source
    assert "import pytest" not in runtime_source
    assert "aigol.provider" not in runtime_source
    assert "aigol.cli" not in runtime_source
    assert "apply_patch" not in runtime_source


def test_ive_4_capability_is_certified_metadata_only() -> None:
    capability_id = "INTELLIGENT_VALIDATION_ORCHESTRATOR_V4"
    record = lookup_platform_capability_certification(capability_id)

    assert is_platform_capability_certified(capability_id) is True
    assert record["certification_milestone"] == "G41-01"
    assert record["implementation_owner"] == (
        "aigol.runtime.intelligent_validation_orchestrator_v4"
    )
    assert record["architectural_owner"] == "PLATFORM_CORE"
