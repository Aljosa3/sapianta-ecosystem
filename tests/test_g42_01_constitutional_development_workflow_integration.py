"""Certification coverage for G42-01 workflow integration."""

from __future__ import annotations

from copy import deepcopy
import json

import pytest

from aigol.runtime.constitutional_development_workflow_integration_runtime import (
    DEVELOPMENT_VALIDATION_PLANNING_READY,
    FAILED_CLOSED,
    plan_constitutional_development_validation,
    reconstruct_constitutional_development_validation_workflow_replay,
    validate_constitutional_development_validation_workflow_artifact,
)
from aigol.runtime.implementation_manifest_runtime import (
    CREATE_ONLY,
    create_implementation_manifest,
)
from aigol.runtime.intelligent_validation_orchestrator_v4 import (
    FAILURE_REVALIDATION_PLANNING,
    INITIAL_VALIDATION_PLANNING,
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
        (
            "aigol/runtime/"
            "constitutional_development_workflow_integration_runtime.py",
            "PYTHON_RUNTIME_MODULE",
        ),
        (
            "tests/"
            "test_g42_01_constitutional_development_workflow_integration.py",
            "PYTHON_TEST_MODULE",
        ),
    )
    manifest = create_implementation_manifest(
        manifest_id="MANIFEST-G42-01",
        canonical_chain_id="CHAIN-G42-01",
        implementation_bundle_id=(
            "G42_01_CONSTITUTIONAL_DEVELOPMENT_WORKFLOW_INTEGRATION"
        ),
        source_candidate_reference="CANDIDATE-G42-01",
        source_candidate_hash=_hash("candidate"),
        implementation_handoff_reference="HANDOFF-G42-01",
        implementation_handoff_hash=_hash("handoff"),
        provider_generation_authorization_reference="AUTH-G42-01",
        provider_generation_authorization_hash=_hash("authorization"),
        provider_response_reference="RESPONSE-G42-01",
        provider_response_hash=_hash("response"),
        target_domain="PLATFORM_CORE",
        target_resource="DEVELOPMENT_VALIDATION_WORKFLOW",
        target_worker=None,
        generated_files=[
            {
                "file_entry_id": f"FILE-G42-01-{index:06d}",
                "target_path": target_path,
                "artifact_type": artifact_type,
                "operation": CREATE_ONLY,
                "content": f"G42-01 deterministic content {index}\n",
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
            "tests/"
            "test_g42_01_constitutional_development_workflow_integration.py"
        ],
        known_gaps=[],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "manifest",
    )["implementation_manifest_artifact"]
    return normalize_platform_change(
        normalization_id="NORMALIZATION-G42-01",
        source_artifact=manifest,
        source_reference=manifest["manifest_id"],
        source_hash=manifest["artifact_hash"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "normalization",
    )["normalized_change_artifact"]


def _plan(
    tmp_path,
    source: dict,
    *,
    name: str = "workflow",
    planning_mode: str | None = None,
    failure_context: dict | None = None,
    source_hash: str | None = None,
) -> dict:
    arguments = {
        "workflow_id": "WORKFLOW-G42-01",
        "session_id": "SESSION-G42-01",
        "normalized_change_artifact": source,
        "normalized_change_reference": source["normalization_id"],
        "normalized_change_hash": (
            source["normalized_change_hash"]
            if source_hash is None
            else source_hash
        ),
        "failure_context": failure_context,
        "created_by": "PLATFORM_CORE_VALIDATION_PLANNING",
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / name,
    }
    if planning_mode is not None:
        arguments["planning_mode"] = planning_mode
    return plan_constitutional_development_validation(
        **arguments,
    )


def test_default_workflow_entry_uses_exact_ive_4_bundle(tmp_path) -> None:
    source = _normalized_change(tmp_path)
    original = deepcopy(source)
    capture = _plan(tmp_path, source)
    artifact = capture[
        "constitutional_development_validation_workflow_artifact"
    ]
    source_bundle = load_json(
        tmp_path
        / "workflow/ive_4/"
        "006_unified_validation_planning_bundle_recorded.json"
    )["artifact"]

    assert artifact["workflow_status"] == (
        DEVELOPMENT_VALIDATION_PLANNING_READY
    )
    assert artifact["planning_mode"] == INITIAL_VALIDATION_PLANNING
    assert artifact["default_planning_entry"][
        "capability_identifier"
    ] == "INTELLIGENT_VALIDATION_ORCHESTRATOR_V4"
    assert artifact["default_planning_entry"]["adoption_status"] == (
        "DEFAULT_PLATFORM_CORE_DEVELOPMENT_VALIDATION_PLANNER"
    )
    assert artifact["ive_4_planning_bundle_artifact"] == source_bundle
    assert artifact["ive_4_bundle_hash"] == source_bundle["bundle_hash"]
    assert validate_unified_validation_planning_bundle_artifact(
        source_bundle
    ) == source_bundle
    assert source == original


def test_workflow_preserves_approval_and_existing_execution_handoff(
    tmp_path,
) -> None:
    source = _normalized_change(tmp_path)
    artifact = _plan(tmp_path, source)[
        "constitutional_development_validation_workflow_artifact"
    ]
    bundle = artifact["ive_4_planning_bundle_artifact"]
    g38 = bundle["stage_artifacts"]["g38"]

    assert artifact["human_approval"] == bundle["human_approval"]
    assert artifact["human_approval"]["required_before_execution"] is True
    assert artifact["existing_validation_pipeline_handoff"] == (
        g38["existing_validation_pipeline_handoff"]
    )
    assert artifact["human_approval_recorded"] is False
    assert artifact["validation_candidate_constructed"] is False
    assert artifact["validation_executed"] is False
    assert artifact["authorization_invoked"] is False
    assert artifact["worker_invoked"] is False
    assert artifact["provider_invoked"] is False
    assert artifact["aicli_invoked"] is False
    assert all(
        value is False for value in artifact["authority_flags"].values()
    )


def test_workflow_replay_reconstructs_complete_ive_4_lineage(
    tmp_path,
) -> None:
    source = _normalized_change(tmp_path)
    artifact = _plan(tmp_path, source)[
        "constitutional_development_validation_workflow_artifact"
    ]
    reconstructed = (
        reconstruct_constitutional_development_validation_workflow_replay(
            tmp_path / "workflow"
        )
    )

    assert reconstructed["workflow_hash"] == artifact["workflow_hash"]
    assert reconstructed["ive_4_bundle_hash"] == (
        artifact["ive_4_bundle_hash"]
    )
    assert reconstructed["default_planning_entry"] == (
        artifact["default_planning_entry"]
    )
    assert reconstructed["human_approval_required"] is True
    assert reconstructed["validation_executed"] is False


def test_workflow_is_deterministic_for_identical_inputs(tmp_path) -> None:
    source = _normalized_change(tmp_path)
    first = _plan(tmp_path, source, name="first")[
        "constitutional_development_validation_workflow_artifact"
    ]
    second = _plan(tmp_path, source, name="second")[
        "constitutional_development_validation_workflow_artifact"
    ]

    assert first == second


def test_missing_source_planning_evidence_fails_closed(tmp_path) -> None:
    source = _normalized_change(tmp_path)
    capture = _plan(
        tmp_path,
        source,
        source_hash=_hash("wrong-normalized-change"),
    )
    artifact = capture[
        "constitutional_development_validation_workflow_artifact"
    ]

    assert artifact["workflow_status"] == FAILED_CLOSED
    assert artifact["ive_4_planning_bundle_artifact"] == {}
    assert artifact["planning_stage_lineage"] == []
    assert artifact["full_regression"]["required"] is True
    assert artifact["human_approval"]["approval_status"] == "BLOCKED"
    assert artifact["validation_executed"] is False
    assert "binding mismatch" in artifact["failure_reason"]


def test_missing_ive_4_failure_context_fails_closed(tmp_path) -> None:
    source = _normalized_change(tmp_path)
    artifact = _plan(
        tmp_path,
        source,
        planning_mode=FAILURE_REVALIDATION_PLANNING,
    )["constitutional_development_validation_workflow_artifact"]

    assert artifact["workflow_status"] == FAILED_CLOSED
    assert artifact["ive_4_planning_bundle_artifact"] == {}
    assert artifact["full_regression"]["required"] is True
    assert "failure_context" in artifact["failure_reason"]


def test_workflow_replay_tamper_is_rejected(tmp_path) -> None:
    source = _normalized_change(tmp_path)
    _plan(tmp_path, source)
    replay_file = (
        tmp_path
        / "workflow/"
        "002_constitutional_development_validation_workflow_recorded.json"
    )
    wrapper = json.loads(replay_file.read_text(encoding="utf-8"))
    wrapper["artifact"]["validation_executed"] = True
    replay_file.write_text(
        json.dumps(wrapper, sort_keys=True),
        encoding="utf-8",
    )

    with pytest.raises(FailClosedRuntimeError, match="replay hash mismatch"):
        reconstruct_constitutional_development_validation_workflow_replay(
            tmp_path / "workflow"
        )


def test_public_validator_rejects_rehashed_ive_4_tamper(tmp_path) -> None:
    source = _normalized_change(tmp_path)
    artifact = _plan(tmp_path, source)[
        "constitutional_development_validation_workflow_artifact"
    ]
    artifact["ive_4_planning_bundle_artifact"][
        "validation_executed"
    ] = True
    artifact["workflow_hash"] = replay_hash(
        {
            key: value
            for key, value in artifact.items()
            if key not in {"workflow_hash", "artifact_hash"}
        }
    )
    artifact["artifact_hash"] = replay_hash(
        {
            key: value
            for key, value in artifact.items()
            if key != "artifact_hash"
        }
    )

    with pytest.raises(
        FailClosedRuntimeError,
        match="artifact hash mismatch",
    ):
        validate_constitutional_development_validation_workflow_artifact(
            artifact
        )


def test_workflow_has_no_execution_or_transport_dependencies() -> None:
    module = __import__(
        "aigol.runtime."
        "constitutional_development_workflow_integration_runtime",
        fromlist=["unused"],
    )
    runtime_source = open(module.__file__, encoding="utf-8").read()

    assert "orchestrate_intelligent_validation_planning" in runtime_source
    assert "intelligent_validation_engine_v0" not in runtime_source
    assert "intelligent_validation_engine_v1" not in runtime_source
    assert "intelligent_validation_engine_v2" not in runtime_source
    assert "intelligent_validation_engine_v3" not in runtime_source
    assert "intelligent_validation_entry_integration" not in runtime_source
    assert "platform_validation_planning_runtime" not in runtime_source
    assert "execute_governed_validation" not in runtime_source
    assert "compose_platform_validation_candidate" not in runtime_source
    assert "import subprocess" not in runtime_source
    assert "import pytest" not in runtime_source
    assert "aigol.provider" not in runtime_source
    assert "aigol.cli" not in runtime_source
    assert "human_interface_runtime_entry" not in runtime_source


def test_g42_capability_is_certified_metadata_only() -> None:
    capability_id = "CONSTITUTIONAL_DEVELOPMENT_WORKFLOW_INTEGRATION"
    record = lookup_platform_capability_certification(capability_id)

    assert is_platform_capability_certified(capability_id) is True
    assert record["certification_milestone"] == "G42-01"
    assert record["implementation_owner"] == (
        "aigol.runtime."
        "constitutional_development_workflow_integration_runtime"
    )
    assert record["architectural_owner"] == "PLATFORM_CORE"
