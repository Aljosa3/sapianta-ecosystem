"""Deterministic certification coverage for G40-01 IVE-3."""

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
from aigol.runtime.intelligent_validation_engine_v2 import (
    recommend_parallel_validation_schedule,
)
from aigol.runtime.intelligent_validation_engine_v3 import (
    FAILED_CLOSED,
    VALIDATION_FAILURE_ANALYZED,
    analyze_failed_validation,
    reconstruct_validation_failure_analysis_replay,
    validate_validation_failure_analysis_artifact,
)
from aigol.runtime.intelligent_validation_entry_integration_runtime import (
    plan_development_validation,
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


def _normalized_change(tmp_path) -> dict:
    targets = (
        ("aigol/cli/aigol_cli.py", "PYTHON_AICLI_MODULE"),
        (
            "tests/test_g40_01_intelligent_validation_engine_v3.py",
            "PYTHON_TEST_MODULE",
        ),
    )
    manifest = create_implementation_manifest(
        manifest_id="MANIFEST-G40-01",
        canonical_chain_id="CHAIN-G40-01",
        implementation_bundle_id="G40_01_INTELLIGENT_VALIDATION_ENGINE_V3",
        source_candidate_reference="CANDIDATE-G40-01",
        source_candidate_hash=_hash("candidate"),
        implementation_handoff_reference="HANDOFF-G40-01",
        implementation_handoff_hash=_hash("handoff"),
        provider_generation_authorization_reference="AUTH-G40-01",
        provider_generation_authorization_hash=_hash("authorization"),
        provider_response_reference="RESPONSE-G40-01",
        provider_response_hash=_hash("response"),
        target_domain="PLATFORM_CORE",
        target_resource="INTELLIGENT_VALIDATION_ENGINE_V3",
        target_worker=None,
        generated_files=[
            {
                "file_entry_id": f"FILE-G40-01-{index:06d}",
                "target_path": target_path,
                "artifact_type": artifact_type,
                "operation": CREATE_ONLY,
                "content": f"G40-01 deterministic content {index}\n",
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
            "tests/test_g40_01_intelligent_validation_engine_v3.py"
        ],
        known_gaps=[],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "manifest",
    )["implementation_manifest_artifact"]
    return normalize_platform_change(
        normalization_id="NORMALIZATION-G40-01",
        source_artifact=manifest,
        source_reference=manifest["manifest_id"],
        source_hash=manifest["artifact_hash"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "normalization",
    )["normalized_change_artifact"]


def _planning_chain(tmp_path) -> dict:
    normalized = _normalized_change(tmp_path)
    g38 = plan_development_validation(
        entry_id="ENTRY-G40-01",
        session_id="SESSION-G40-01",
        normalized_change_artifact=normalized,
        normalized_change_reference=normalized["normalization_id"],
        normalized_change_hash=normalized["normalized_change_hash"],
        created_by="PLATFORM_CORE_VALIDATION_PLANNING",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "g38",
    )["intelligent_validation_planning_entry_artifact"]
    return recommend_parallel_validation_schedule(
        schedule_id="SCHEDULE-G40-01",
        session_id="SESSION-G40-01",
        g38_validation_plan_artifact=g38,
        g38_validation_plan_reference=g38["entry_id"],
        g38_validation_plan_hash=g38["planning_entry_hash"],
        g38_replay_dir=tmp_path / "g38",
        created_by="PLATFORM_CORE_VALIDATION_PLANNING",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "ive-2",
    )["parallel_validation_schedule_artifact"]


def _failed_validation(tmp_path, *, name: str = "validation") -> dict:
    candidate = create_governed_validation_candidate(
        candidate_id=f"CANDIDATE-G40-01-{name}",
        session_id="SESSION-G40-01",
        command_id="PYTHON_VALIDATION_FAILS_FOR_TEST",
        validation_purpose="deterministic IVE-3 failure evidence",
        created_by="PLATFORM_CORE",
        created_at=CREATED_AT,
    )
    approval = create_governed_validation_approval(
        approval_id=f"APPROVAL-G40-01-{name}",
        candidate_artifact=candidate,
        confirmation_text=(
            f"confirm validation {candidate['candidate_id']} "
            f"{candidate['artifact_hash']}"
        ),
        approved_by="HUMAN_OPERATOR",
        approved_at=CREATED_AT,
    )
    return execute_governed_validation(
        execution_id=f"EXECUTION-G40-01-{name}",
        candidate_artifact=candidate,
        approval_artifact=approval,
        repository_root=".",
        executed_by="PLATFORM_CORE",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / name,
    )["validation_result_artifact"]


def _group(schedule: dict, identifier: str) -> dict:
    return next(
        group
        for group in schedule["groups"]
        if group["validation_subject_identifier"] == identifier
    )


def _analyze(
    tmp_path,
    schedule: dict,
    result: dict,
    group: dict,
    *,
    name: str = "ive-3",
    failed_requirement_hashes: list[str] | None = None,
) -> dict:
    hashes = (
        failed_requirement_hashes
        if failed_requirement_hashes is not None
        else group["requirement_hashes"][:1]
    )
    return analyze_failed_validation(
        analysis_id="ANALYSIS-G40-01",
        session_id="SESSION-G40-01",
        ive_2_schedule_artifact=schedule,
        ive_2_schedule_reference=schedule["schedule_id"],
        ive_2_schedule_hash=schedule["schedule_hash"],
        ive_2_replay_dir=tmp_path / "ive-2",
        g38_replay_dir=tmp_path / "g38",
        validation_result_artifact=result,
        validation_result_reference=result["execution_id"],
        validation_result_hash=result["artifact_hash"],
        validation_replay_dir=tmp_path / "validation",
        failed_group_id=group["group_id"],
        failed_group_hash=group["group_hash"],
        failed_requirement_hashes=hashes,
        observed_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / name,
    )


def test_direct_failure_traces_to_ive_0_and_recommends_dependency_descendants(
    tmp_path,
) -> None:
    schedule = _planning_chain(tmp_path)
    result = _failed_validation(tmp_path)
    group = _group(schedule, "AICLI")
    original_schedule = deepcopy(schedule)
    capture = _analyze(tmp_path, schedule, result, group)
    artifact = capture["validation_failure_analysis_artifact"]
    reconstructed = reconstruct_validation_failure_analysis_replay(
        tmp_path / "ive-3"
    )

    assert artifact["analysis_status"] == VALIDATION_FAILURE_ANALYZED
    assert artifact["earliest_known_planning_boundary"]["boundary"] == (
        "IVE_0_DIRECT_IMPACT_RECOMMENDATION"
    )
    assert artifact["earliest_known_planning_boundary"]["boundary_rank"] == 0
    recommended_ids = {
        item["group_id"] for item in artifact["recommended_revalidation_groups"]
    }
    assert group["group_id"] in recommended_ids
    assert "IVE-2-FULL-REGRESSION-BARRIER" in recommended_ids
    independent = _group(schedule, "TEST_INFRASTRUCTURE")
    assert independent["group_id"] not in recommended_ids
    failed_recommendation = next(
        item
        for item in artifact["recommended_revalidation_groups"]
        if item["group_id"] == group["group_id"]
    )
    assert failed_recommendation["revalidation_requirement_hashes"] == (
        group["requirement_hashes"][:1]
    )
    assert artifact["human_approval"] == schedule["human_approval"]
    assert artifact["validation_executed"] is False
    assert artifact["automatic_repair_performed"] is False
    assert all(value is False for value in artifact["authority_flags"].values())
    assert schedule == original_schedule
    assert reconstructed["analysis_hash"] == artifact["analysis_hash"]
    assert validate_validation_failure_analysis_artifact(artifact) == artifact


def test_transitive_failure_traces_to_ive_1(tmp_path) -> None:
    schedule = _planning_chain(tmp_path)
    result = _failed_validation(tmp_path)
    group = _group(schedule, "GOVERNANCE")
    artifact = _analyze(tmp_path, schedule, result, group)[
        "validation_failure_analysis_artifact"
    ]

    assert artifact["earliest_known_planning_boundary"]["boundary"] == (
        "IVE_1_SEMANTIC_DEPENDENCY_SELECTION"
    )
    assert artifact["earliest_known_planning_boundary"]["boundary_rank"] == 1
    assert artifact["earliest_known_planning_boundary"]["evidence_hashes"]


def test_full_regression_failure_traces_to_ive_2_barrier(tmp_path) -> None:
    schedule = _planning_chain(tmp_path)
    result = _failed_validation(tmp_path)
    barrier = _group(schedule, "FULL_REPOSITORY_REGRESSION")
    artifact = _analyze(
        tmp_path,
        schedule,
        result,
        barrier,
        failed_requirement_hashes=[],
    )["validation_failure_analysis_artifact"]

    assert artifact["earliest_known_planning_boundary"]["boundary"] == (
        "IVE_2_FULL_REGRESSION_BARRIER"
    )
    assert artifact["recommended_revalidation_group_count"] == 1
    assert artifact["recommended_revalidation_groups"][0]["group_id"] == (
        barrier["group_id"]
    )


def test_analysis_is_deterministic_for_identical_evidence(tmp_path) -> None:
    schedule = _planning_chain(tmp_path)
    result = _failed_validation(tmp_path)
    group = _group(schedule, "AICLI")
    first = _analyze(tmp_path, schedule, result, group, name="first")[
        "validation_failure_analysis_artifact"
    ]
    second = _analyze(tmp_path, schedule, result, group, name="second")[
        "validation_failure_analysis_artifact"
    ]

    assert first == second


def test_unknown_group_binding_fails_closed(tmp_path) -> None:
    schedule = _planning_chain(tmp_path)
    result = _failed_validation(tmp_path)
    group = deepcopy(_group(schedule, "AICLI"))
    group["group_id"] = "UNKNOWN-GROUP"
    capture = _analyze(tmp_path, schedule, result, group)
    artifact = capture["validation_failure_analysis_artifact"]

    assert artifact["analysis_status"] == FAILED_CLOSED
    assert artifact["recommended_revalidation_groups"] == []
    assert artifact["full_regression"]["required"] is True
    assert artifact["validation_executed"] is False
    assert "group binding mismatch" in artifact["failure_reason"]
    assert reconstruct_validation_failure_analysis_replay(
        tmp_path / "ive-3"
    )["fail_closed"] is True


def test_unbound_requirement_fails_closed(tmp_path) -> None:
    schedule = _planning_chain(tmp_path)
    result = _failed_validation(tmp_path)
    group = _group(schedule, "AICLI")
    artifact = _analyze(
        tmp_path,
        schedule,
        result,
        group,
        failed_requirement_hashes=[_hash("unknown-requirement")],
    )["validation_failure_analysis_artifact"]

    assert artifact["analysis_status"] == FAILED_CLOSED
    assert "requirements are not bound" in artifact["failure_reason"]


def test_replay_tamper_is_rejected(tmp_path) -> None:
    schedule = _planning_chain(tmp_path)
    result = _failed_validation(tmp_path)
    group = _group(schedule, "AICLI")
    _analyze(tmp_path, schedule, result, group)
    replay_file = (
        tmp_path / "ive-3/005_validation_failure_analysis_recorded.json"
    )
    wrapper = json.loads(replay_file.read_text(encoding="utf-8"))
    wrapper["artifact"]["automatic_repair_performed"] = True
    replay_file.write_text(
        json.dumps(wrapper, sort_keys=True),
        encoding="utf-8",
    )

    with pytest.raises(FailClosedRuntimeError, match="replay hash mismatch"):
        reconstruct_validation_failure_analysis_replay(tmp_path / "ive-3")


def test_ive_3_has_no_execution_repair_or_transport_dependencies() -> None:
    module = __import__(
        "aigol.runtime.intelligent_validation_engine_v3",
        fromlist=["unused"],
    )
    runtime_source = open(module.__file__, encoding="utf-8").read()

    assert "execute_governed_validation" not in runtime_source
    assert "import subprocess" not in runtime_source
    assert "import pytest" not in runtime_source
    assert "aigol.provider" not in runtime_source
    assert "aigol.cli" not in runtime_source
    assert "apply_patch" not in runtime_source


def test_ive_3_capability_is_certified_metadata_only() -> None:
    capability_id = "INTELLIGENT_VALIDATION_ENGINE_V3"
    record = lookup_platform_capability_certification(capability_id)

    assert is_platform_capability_certified(capability_id) is True
    assert record["certification_milestone"] == "G40-01"
    assert record["implementation_owner"] == (
        "aigol.runtime.intelligent_validation_engine_v3"
    )
    assert record["architectural_owner"] == "PLATFORM_CORE"
