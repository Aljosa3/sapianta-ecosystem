"""Deterministic certification coverage for G38-01."""

from __future__ import annotations

from copy import deepcopy
import json

import pytest

from aigol.runtime.implementation_manifest_runtime import (
    CREATE_ONLY,
    create_implementation_manifest,
)
from aigol.runtime.intelligent_validation_engine_v0 import (
    analyze_intelligent_validation_scope,
)
from aigol.runtime.intelligent_validation_engine_v1 import (
    select_semantic_validation_scope,
)
from aigol.runtime.intelligent_validation_entry_integration_runtime import (
    FAILED_CLOSED,
    INTELLIGENT_VALIDATION_PLANNING_ENTRY_ARTIFACT_V1,
    INTELLIGENT_VALIDATION_PLANNING_READY,
    plan_development_validation,
    reconstruct_intelligent_validation_entry_replay,
    validate_intelligent_validation_planning_entry_artifact,
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


def _normalized_change(tmp_path, *, name: str = "source") -> dict:
    manifest = create_implementation_manifest(
        manifest_id=f"MANIFEST-G38-01-{name}",
        canonical_chain_id="CHAIN-G38-01",
        implementation_bundle_id="G38_01_INTELLIGENT_VALIDATION_ENTRY",
        source_candidate_reference="CANDIDATE-G38-01",
        source_candidate_hash=_hash("candidate"),
        implementation_handoff_reference="HANDOFF-G38-01",
        implementation_handoff_hash=_hash("handoff"),
        provider_generation_authorization_reference="AUTH-G38-01",
        provider_generation_authorization_hash=_hash("authorization"),
        provider_response_reference="RESPONSE-G38-01",
        provider_response_hash=_hash("response"),
        target_domain="PLATFORM_CORE",
        target_resource="INTELLIGENT_VALIDATION_ENTRY_INTEGRATION",
        target_worker=None,
        generated_files=[
            {
                "file_entry_id": "FILE-G38-01-000001",
                "target_path": (
                    "aigol/runtime/"
                    "intelligent_validation_entry_integration_runtime.py"
                ),
                "artifact_type": "PYTHON_RUNTIME_MODULE",
                "operation": CREATE_ONLY,
                "content": "G38-01 deterministic content\n",
                "validation_requirements": [],
            }
        ],
        generated_tests=[],
        validation_requirements=[
            "python -m pytest "
            "tests/test_g38_01_intelligent_validation_entry_integration.py"
        ],
        known_gaps=[],
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"{name}-manifest",
    )["implementation_manifest_artifact"]
    return normalize_platform_change(
        normalization_id=f"NORMALIZATION-G38-01-{name}",
        source_artifact=manifest,
        source_reference=manifest["manifest_id"],
        source_hash=manifest["artifact_hash"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"{name}-normalization",
    )["normalized_change_artifact"]


def _plan(tmp_path, source: dict, *, name: str = "entry", entry_id: str = "ENTRY-G38-01"):
    return plan_development_validation(
        entry_id=entry_id,
        session_id="SESSION-G38-01",
        normalized_change_artifact=source,
        normalized_change_reference=source["normalization_id"],
        normalized_change_hash=source["normalized_change_hash"],
        created_by="PLATFORM_CORE_VALIDATION_PLANNING",
        created_at=CREATED_AT,
        replay_dir=tmp_path / name,
    )


def test_single_entry_runs_certified_ive_chain_and_reconstructs(tmp_path) -> None:
    source = _normalized_change(tmp_path)
    capture = _plan(tmp_path, source)
    artifact = capture["intelligent_validation_planning_entry_artifact"]
    reconstructed = reconstruct_intelligent_validation_entry_replay(
        tmp_path / "entry"
    )

    assert artifact["artifact_type"] == (
        INTELLIGENT_VALIDATION_PLANNING_ENTRY_ARTIFACT_V1
    )
    assert artifact["entry_status"] == INTELLIGENT_VALIDATION_PLANNING_READY
    assert artifact["direct_validation_subjects"]
    assert artifact["selected_validation_requirements"]
    assert artifact["full_regression"]["required"] is True
    assert artifact["human_approval"]["required_before_execution"] is True
    assert artifact["human_approval_recorded"] is False
    assert artifact["validation_candidate_constructed"] is False
    assert artifact["validation_executed"] is False
    assert artifact["authorization_invoked"] is False
    assert artifact["worker_invoked"] is False
    assert artifact["provider_invoked"] is False
    assert artifact["aicli_invoked"] is False
    assert all(value is False for value in artifact["authority_flags"].values())
    assert reconstructed["planning_entry_hash"] == artifact[
        "planning_entry_hash"
    ]
    assert reconstructed["selected_validation_requirements"] == artifact[
        "selected_validation_requirements"
    ]
    assert validate_intelligent_validation_planning_entry_artifact(
        artifact
    ) == artifact


def test_entry_consumes_ive_0_and_ive_1_outputs_unchanged(tmp_path) -> None:
    source = _normalized_change(tmp_path)
    integrated = _plan(tmp_path, source)[
        "intelligent_validation_planning_entry_artifact"
    ]
    ive_0 = analyze_intelligent_validation_scope(
        ive_analysis_id="ENTRY-G38-01:IVE-0",
        normalized_change_artifact=source,
        normalized_change_reference=source["normalization_id"],
        normalized_change_hash=source["normalized_change_hash"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "standalone-ive-0",
    )["intelligent_validation_plan_artifact"]
    ive_1 = select_semantic_validation_scope(
        selection_id="ENTRY-G38-01:IVE-1",
        intelligent_validation_plan_artifact=ive_0,
        intelligent_validation_plan_reference=ive_0["ive_analysis_id"],
        intelligent_validation_plan_hash=ive_0[
            "intelligent_validation_plan_hash"
        ],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "standalone-ive-1",
    )["semantic_validation_selection_artifact"]

    integrated_ive_0 = load_json(
        tmp_path / "entry/ive_0/000_intelligent_validation_plan_recorded.json"
    )["artifact"]
    integrated_ive_1 = load_json(
        tmp_path / "entry/ive_1/001_semantic_validation_selection_recorded.json"
    )["artifact"]
    assert integrated_ive_0 == ive_0
    assert integrated_ive_1 == ive_1
    for field in (
        "direct_validation_subjects",
        "transitive_dependencies",
        "selected_validation_requirements",
        "full_regression",
        "certification_evidence_test_targets",
        "existing_allowlisted_command_references",
        "existing_validation_pipeline_handoff",
        "human_approval",
    ):
        assert integrated[field] == ive_1[field]


def test_entry_is_deterministic_for_identical_canonical_inputs(tmp_path) -> None:
    source = _normalized_change(tmp_path)
    first = _plan(tmp_path, source, name="first")[
        "intelligent_validation_planning_entry_artifact"
    ]
    second = _plan(tmp_path, source, name="second")[
        "intelligent_validation_planning_entry_artifact"
    ]

    assert first == second


def test_invalid_source_binding_fails_closed_before_ive_handoff(tmp_path) -> None:
    source = _normalized_change(tmp_path)
    capture = plan_development_validation(
        entry_id="ENTRY-G38-01-FAILED",
        session_id="SESSION-G38-01",
        normalized_change_artifact=source,
        normalized_change_reference=source["normalization_id"],
        normalized_change_hash=_hash("wrong-source"),
        created_by="PLATFORM_CORE_VALIDATION_PLANNING",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "failed",
    )
    artifact = capture["intelligent_validation_planning_entry_artifact"]

    assert artifact["entry_status"] == FAILED_CLOSED
    assert capture["fail_closed"] is True
    assert artifact["full_regression"]["required"] is True
    assert artifact["validation_executed"] is False
    assert artifact["existing_validation_pipeline_handoff"]["status"] == (
        "BLOCKED_BY_INTELLIGENT_VALIDATION_ENTRY_FAILURE"
    )
    assert not (tmp_path / "failed/ive_0").exists()
    assert reconstruct_intelligent_validation_entry_replay(tmp_path / "failed")[
        "fail_closed"
    ] is True


def test_replay_tamper_is_rejected(tmp_path) -> None:
    source = _normalized_change(tmp_path)
    _plan(tmp_path, source)
    replay_file = (
        tmp_path
        / "entry/000_intelligent_validation_planning_entry_recorded.json"
    )
    wrapper = json.loads(replay_file.read_text(encoding="utf-8"))
    wrapper["artifact"]["validation_executed"] = True
    replay_file.write_text(
        json.dumps(wrapper, sort_keys=True),
        encoding="utf-8",
    )

    with pytest.raises(FailClosedRuntimeError, match="replay hash mismatch"):
        reconstruct_intelligent_validation_entry_replay(tmp_path / "entry")


def test_entry_does_not_change_existing_runtime_sources() -> None:
    source = __import__(
        "aigol.runtime.intelligent_validation_entry_integration_runtime",
        fromlist=["unused"],
    )
    runtime_source = open(source.__file__, encoding="utf-8").read()

    assert "execute_governed_validation" not in runtime_source
    assert "create_governed_validation_approval" not in runtime_source
    assert "subprocess" not in runtime_source
    assert "import pytest" not in runtime_source
    assert "from pytest" not in runtime_source
    assert "aigol.workers" not in runtime_source
    assert "aigol.provider" not in runtime_source
    assert "aigol.cli" not in runtime_source


def test_entry_capability_is_certified_metadata_only() -> None:
    capability_id = "INTELLIGENT_VALIDATION_ENTRY_INTEGRATION"
    record = lookup_platform_capability_certification(capability_id)

    assert is_platform_capability_certified(capability_id) is True
    assert record["certification_milestone"] == "G38-01"
    assert record["implementation_owner"] == (
        "aigol.runtime.intelligent_validation_entry_integration_runtime"
    )
    assert record["architectural_owner"] == "PLATFORM_CORE"
