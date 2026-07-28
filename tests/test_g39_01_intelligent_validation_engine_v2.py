"""Deterministic certification coverage for G39-01 IVE-2."""

from __future__ import annotations

from copy import deepcopy
import json

import pytest

from aigol.runtime.implementation_manifest_runtime import (
    CREATE_ONLY,
    create_implementation_manifest,
)
from aigol.runtime.intelligent_validation_engine_v2 import (
    FAILED_CLOSED,
    PARALLEL_VALIDATION_SCHEDULE_ARTIFACT_V1,
    PARALLEL_VALIDATION_SCHEDULE_RECOMMENDED,
    recommend_parallel_validation_schedule,
    reconstruct_parallel_validation_schedule_replay,
    validate_parallel_validation_schedule_artifact,
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


def _normalized_change(tmp_path, *, name: str = "source") -> dict:
    targets = (
        ("aigol/cli/aigol_cli.py", "PYTHON_AICLI_MODULE"),
        (
            "tests/test_g39_01_intelligent_validation_engine_v2.py",
            "PYTHON_TEST_MODULE",
        ),
    )
    manifest = create_implementation_manifest(
        manifest_id=f"MANIFEST-G39-01-{name}",
        canonical_chain_id="CHAIN-G39-01",
        implementation_bundle_id="G39_01_INTELLIGENT_VALIDATION_ENGINE_V2",
        source_candidate_reference="CANDIDATE-G39-01",
        source_candidate_hash=_hash("candidate"),
        implementation_handoff_reference="HANDOFF-G39-01",
        implementation_handoff_hash=_hash("handoff"),
        provider_generation_authorization_reference="AUTH-G39-01",
        provider_generation_authorization_hash=_hash("authorization"),
        provider_response_reference="RESPONSE-G39-01",
        provider_response_hash=_hash("response"),
        target_domain="PLATFORM_CORE",
        target_resource="INTELLIGENT_VALIDATION_ENGINE_V2",
        target_worker=None,
        generated_files=[
            {
                "file_entry_id": f"FILE-G39-01-{index:06d}",
                "target_path": target_path,
                "artifact_type": artifact_type,
                "operation": CREATE_ONLY,
                "content": f"G39-01 deterministic content {index}\n",
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
            "tests/test_g39_01_intelligent_validation_engine_v2.py"
        ],
        known_gaps=[],
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"{name}-manifest",
    )["implementation_manifest_artifact"]
    return normalize_platform_change(
        normalization_id=f"NORMALIZATION-G39-01-{name}",
        source_artifact=manifest,
        source_reference=manifest["manifest_id"],
        source_hash=manifest["artifact_hash"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"{name}-normalization",
    )["normalized_change_artifact"]


def _g38_plan(tmp_path, source: dict, *, name: str = "g38") -> dict:
    return plan_development_validation(
        entry_id="ENTRY-G39-01",
        session_id="SESSION-G39-01",
        normalized_change_artifact=source,
        normalized_change_reference=source["normalization_id"],
        normalized_change_hash=source["normalized_change_hash"],
        created_by="PLATFORM_CORE_VALIDATION_PLANNING",
        created_at=CREATED_AT,
        replay_dir=tmp_path / name,
    )["intelligent_validation_planning_entry_artifact"]


def _schedule(
    tmp_path,
    source: dict,
    *,
    g38_name: str = "g38",
    name: str = "ive-2",
    schedule_id: str = "SCHEDULE-G39-01",
) -> dict:
    return recommend_parallel_validation_schedule(
        schedule_id=schedule_id,
        session_id="SESSION-G39-01",
        g38_validation_plan_artifact=source,
        g38_validation_plan_reference=source["entry_id"],
        g38_validation_plan_hash=source["planning_entry_hash"],
        g38_replay_dir=tmp_path / g38_name,
        created_by="PLATFORM_CORE_VALIDATION_PLANNING",
        created_at=CREATED_AT,
        replay_dir=tmp_path / name,
    )


def test_ive_2_recommends_only_proven_independent_groups_and_reconstructs(
    tmp_path,
) -> None:
    normalized = _normalized_change(tmp_path)
    source = _g38_plan(tmp_path, normalized)
    original_source = deepcopy(source)
    capture = _schedule(tmp_path, source)
    artifact = capture["parallel_validation_schedule_artifact"]
    reconstructed = reconstruct_parallel_validation_schedule_replay(
        tmp_path / "ive-2"
    )

    assert artifact["artifact_type"] == (
        PARALLEL_VALIDATION_SCHEDULE_ARTIFACT_V1
    )
    assert artifact["schedule_status"] == (
        PARALLEL_VALIDATION_SCHEDULE_RECOMMENDED
    )
    parallel_waves = [
        wave
        for wave in artifact["waves"]
        if wave["execution_mode_recommendation"].startswith(
            "PARALLEL_ELIGIBLE"
        )
    ]
    assert parallel_waves
    assert artifact["maximum_recommended_concurrency"] >= 2
    assert artifact["independence_evidence"]
    assert all(
        item["path_left_to_right"] is False
        and item["path_right_to_left"] is False
        and item["unknown_dependency_inference_used"] is False
        for item in artifact["independence_evidence"]
    )
    assert artifact["human_approval"] == source["human_approval"]
    assert artifact["full_regression"] == source["full_regression"]
    assert artifact["existing_allowlisted_command_references"] == source[
        "existing_allowlisted_command_references"
    ]
    assert artifact["existing_validation_pipeline_handoff"] == source[
        "existing_validation_pipeline_handoff"
    ]
    assert source == original_source
    assert artifact["human_approval_recorded"] is False
    assert artifact["validation_executed"] is False
    assert artifact["authorization_invoked"] is False
    assert artifact["worker_invoked"] is False
    assert artifact["provider_invoked"] is False
    assert artifact["aicli_invoked"] is False
    assert all(value is False for value in artifact["authority_flags"].values())
    assert reconstructed["schedule_hash"] == artifact["schedule_hash"]
    assert validate_parallel_validation_schedule_artifact(artifact) == artifact


def test_full_regression_remains_a_terminal_sequential_barrier(tmp_path) -> None:
    normalized = _normalized_change(tmp_path)
    source = _g38_plan(tmp_path, normalized)
    artifact = _schedule(tmp_path, source)[
        "parallel_validation_schedule_artifact"
    ]
    barrier = artifact["groups"][-1]
    final_wave = artifact["waves"][-1]

    assert source["full_regression"]["required"] is True
    assert barrier["group_kind"] == "FULL_REGRESSION_BARRIER"
    assert barrier["depends_on_group_ids"] == sorted(
        group["group_id"] for group in artifact["groups"][:-1]
    )
    assert final_wave["group_ids"] == [barrier["group_id"]]
    assert final_wave["execution_mode_recommendation"] == (
        "SEQUENTIAL_SINGLE_GROUP"
    )


def test_ive_2_is_deterministic_for_identical_g38_plan(tmp_path) -> None:
    normalized = _normalized_change(tmp_path)
    source = _g38_plan(tmp_path, normalized)
    first = _schedule(tmp_path, source, name="first")[
        "parallel_validation_schedule_artifact"
    ]
    second = _schedule(tmp_path, source, name="second")[
        "parallel_validation_schedule_artifact"
    ]

    assert first == second


def test_unknown_dependency_evidence_fails_closed(tmp_path) -> None:
    normalized = _normalized_change(tmp_path)
    source = _g38_plan(tmp_path, normalized)
    selection_path = (
        tmp_path
        / "g38/ive_1/001_semantic_validation_selection_recorded.json"
    )
    wrapper = json.loads(selection_path.read_text(encoding="utf-8"))
    selection = wrapper["artifact"]
    dependency = selection["transitive_dependencies"][0]
    dependency["dependency_kind"] = "UNKNOWN_DEPENDENCY_KIND"
    dependency_body = deepcopy(dependency)
    dependency_body.pop("dependency_hash")
    dependency["dependency_hash"] = replay_hash(dependency_body)
    selection_keys = (
        "source_artifact_type",
        "source_ive_0_reference",
        "source_ive_0_plan_hash",
        "source_ive_0_artifact_hash",
        "semantic_dependency_model_hash",
        "direct_validation_subjects",
        "transitive_dependencies",
        "selected_validation_requirements",
        "full_regression",
        "certification_evidence_test_targets",
        "existing_allowlisted_command_references",
        "existing_validation_pipeline_handoff",
        "human_approval",
        "selection_policy",
        "selection_status",
        "authority_flags",
        "failure_reason",
    )
    selection["semantic_validation_selection_hash"] = replay_hash(
        {key: deepcopy(selection[key]) for key in selection_keys}
    )
    artifact_body = deepcopy(selection)
    artifact_body.pop("artifact_hash")
    selection["artifact_hash"] = replay_hash(artifact_body)
    wrapper_body = deepcopy(wrapper)
    wrapper_body.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper_body)
    selection_path.write_text(
        json.dumps(wrapper, sort_keys=True),
        encoding="utf-8",
    )

    capture = _schedule(tmp_path, source, name="unknown")
    artifact = capture["parallel_validation_schedule_artifact"]

    assert artifact["schedule_status"] == FAILED_CLOSED
    assert artifact["groups"] == []
    assert artifact["waves"] == []
    assert artifact["maximum_recommended_concurrency"] == 0
    assert artifact["full_regression"]["required"] is True
    assert "dependency kind is invalid" in artifact["failure_reason"]
    assert reconstruct_parallel_validation_schedule_replay(
        tmp_path / "unknown"
    )["fail_closed"] is True


def test_invalid_g38_binding_fails_closed_before_scheduling(tmp_path) -> None:
    normalized = _normalized_change(tmp_path)
    source = _g38_plan(tmp_path, normalized)
    capture = recommend_parallel_validation_schedule(
        schedule_id="SCHEDULE-G39-01-FAILED",
        session_id="SESSION-G39-01",
        g38_validation_plan_artifact=source,
        g38_validation_plan_reference=source["entry_id"],
        g38_validation_plan_hash=_hash("wrong-g38-plan"),
        g38_replay_dir=tmp_path / "g38",
        created_by="PLATFORM_CORE_VALIDATION_PLANNING",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "failed",
    )
    artifact = capture["parallel_validation_schedule_artifact"]

    assert artifact["schedule_status"] == FAILED_CLOSED
    assert artifact["groups"] == []
    assert artifact["waves"] == []
    assert artifact["validation_executed"] is False
    assert artifact["existing_validation_pipeline_handoff"]["status"] == (
        "BLOCKED_BY_IVE_2_FAILURE"
    )


def test_schedule_replay_tamper_is_rejected(tmp_path) -> None:
    normalized = _normalized_change(tmp_path)
    source = _g38_plan(tmp_path, normalized)
    _schedule(tmp_path, source)
    replay_file = (
        tmp_path / "ive-2/002_parallel_validation_schedule_recorded.json"
    )
    wrapper = json.loads(replay_file.read_text(encoding="utf-8"))
    wrapper["artifact"]["validation_executed"] = True
    replay_file.write_text(
        json.dumps(wrapper, sort_keys=True),
        encoding="utf-8",
    )

    with pytest.raises(FailClosedRuntimeError, match="replay hash mismatch"):
        reconstruct_parallel_validation_schedule_replay(tmp_path / "ive-2")


def test_ive_2_has_no_execution_or_transport_dependencies() -> None:
    module = __import__(
        "aigol.runtime.intelligent_validation_engine_v2",
        fromlist=["unused"],
    )
    runtime_source = open(module.__file__, encoding="utf-8").read()

    assert "execute_governed_validation" not in runtime_source
    assert "create_governed_validation_approval" not in runtime_source
    assert "import subprocess" not in runtime_source
    assert "import pytest" not in runtime_source
    assert "aigol.workers" not in runtime_source
    assert "aigol.provider" not in runtime_source
    assert "aigol.cli" not in runtime_source


def test_ive_2_capability_is_certified_metadata_only() -> None:
    capability_id = "INTELLIGENT_VALIDATION_ENGINE_V2"
    record = lookup_platform_capability_certification(capability_id)

    assert is_platform_capability_certified(capability_id) is True
    assert record["certification_milestone"] == "G39-01"
    assert record["implementation_owner"] == (
        "aigol.runtime.intelligent_validation_engine_v2"
    )
    assert record["architectural_owner"] == "PLATFORM_CORE"
