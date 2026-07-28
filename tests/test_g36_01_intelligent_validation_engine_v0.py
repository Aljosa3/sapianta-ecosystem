"""Deterministic certification coverage for G36-01 IVE-0."""

from __future__ import annotations

from copy import deepcopy
import json

import pytest

from aigol.runtime.implementation_manifest_runtime import (
    CREATE_ONLY,
    create_implementation_manifest,
)
from aigol.runtime.intelligent_validation_engine_v0 import (
    FAILED_CLOSED,
    INTELLIGENT_VALIDATION_PLAN_ARTIFACT_V1,
    IVE_ANALYSIS_COMPLETED_WITH_UNRESOLVED_MAPPINGS,
    analyze_intelligent_validation_scope,
    reconstruct_intelligent_validation_engine_v0_replay,
    validate_intelligent_validation_plan_artifact,
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


def _normalized_change(tmp_path, *, targets: list[tuple[str, str]], name: str) -> dict:
    files = [
        {
            "file_entry_id": f"FILE-G36-01-{index:06d}",
            "target_path": target_path,
            "artifact_type": artifact_type,
            "operation": CREATE_ONLY,
            "content": f"G36-01 deterministic content {index}\n",
            "validation_requirements": [],
        }
        for index, (target_path, artifact_type) in enumerate(targets, start=1)
    ]
    manifest_capture = create_implementation_manifest(
        manifest_id=f"MANIFEST-G36-01-{name}",
        canonical_chain_id="CHAIN-G36-01",
        implementation_bundle_id="G36_01_INTELLIGENT_VALIDATION_ENGINE_V0",
        source_candidate_reference="CANDIDATE-G36-01",
        source_candidate_hash=_hash("candidate"),
        implementation_handoff_reference="HANDOFF-G36-01",
        implementation_handoff_hash=_hash("handoff"),
        provider_generation_authorization_reference="AUTH-G36-01",
        provider_generation_authorization_hash=_hash("authorization"),
        provider_response_reference="RESPONSE-G36-01",
        provider_response_hash=_hash("response"),
        target_domain="PLATFORM_CORE",
        target_resource="INTELLIGENT_VALIDATION_ENGINE_V0",
        target_worker=None,
        generated_files=files,
        generated_tests=[],
        validation_requirements=[
            "python -m pytest tests/test_g36_01_intelligent_validation_engine_v0.py"
        ],
        known_gaps=[],
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"{name}-manifest",
    )
    manifest = manifest_capture["implementation_manifest_artifact"]
    return normalize_platform_change(
        normalization_id=f"NORMALIZATION-G36-01-{name}",
        source_artifact=manifest,
        source_reference=manifest["manifest_id"],
        source_hash=manifest["artifact_hash"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"{name}-normalization",
    )["normalized_change_artifact"]


def _analyze(tmp_path, source: dict, *, name: str, analysis_id: str | None = None) -> dict:
    return analyze_intelligent_validation_scope(
        ive_analysis_id=analysis_id or f"IVE-G36-01-{name}",
        normalized_change_artifact=source,
        normalized_change_reference=source["normalization_id"],
        normalized_change_hash=source["normalized_change_hash"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / name,
    )


def test_ive_0_composes_planning_only_evidence_and_reconstructs(tmp_path) -> None:
    source = _normalized_change(
        tmp_path,
        targets=[
            (
                "aigol/runtime/intelligent_validation_engine_v0.py",
                "PYTHON_RUNTIME_MODULE",
            )
        ],
        name="single",
    )
    capture = _analyze(tmp_path, source, name="ive")
    artifact = capture["intelligent_validation_plan_artifact"]
    reconstructed = reconstruct_intelligent_validation_engine_v0_replay(
        tmp_path / "ive"
    )

    assert artifact["artifact_type"] == INTELLIGENT_VALIDATION_PLAN_ARTIFACT_V1
    assert (
        artifact["analysis_status"]
        == IVE_ANALYSIS_COMPLETED_WITH_UNRESOLVED_MAPPINGS
    )
    assert artifact["affected_component_count"] == 1
    assert artifact["affected_components"][0]["component_type"] == "PLATFORM_CORE"
    assert (
        artifact["impact_classification"]["overall_classification"]
        == "PLATFORM_CORE"
    )
    recommendation = artifact["validation_recommendation"]
    assert recommendation["required_unit_tests"]
    assert recommendation["required_integration_tests"]
    assert recommendation["required_replay_validation"]
    assert recommendation["full_regression"]["required"] is True
    assert recommendation["certification_evidence_test_targets"] == []
    assert recommendation["certification_evidence_target_semantics"] == (
        "EXACT_REGISTRY_EVIDENCE_PATHS; TEST_KIND_NOT_INFERRED"
    )
    assert (
        recommendation["existing_validation_pipeline_handoff"]["status"]
        == "PLANNING_ONLY_NO_EXACT_ALLOWLIST_MAPPING"
    )
    assert recommendation["human_approval"]["required_before_execution"] is True
    assert recommendation["human_approval"]["recorded_by_ive_0"] is False
    assert artifact["validation_executed"] is False
    assert artifact["authorization_invoked"] is False
    assert artifact["worker_invoked"] is False
    assert artifact["provider_invoked"] is False
    assert all(value is False for value in artifact["authority_flags"].values())
    assert (
        reconstructed["intelligent_validation_plan_hash"]
        == artifact["intelligent_validation_plan_hash"]
    )
    assert validate_intelligent_validation_plan_artifact(artifact) == artifact


def test_ive_0_multicomponent_classification_uses_exact_rules(tmp_path) -> None:
    source = _normalized_change(
        tmp_path,
        targets=[
            (
                "aigol/runtime/intelligent_validation_engine_v0.py",
                "PYTHON_RUNTIME_MODULE",
            ),
            (
                "docs/governance/G36_01_INTELLIGENT_VALIDATION_ENGINE_V0.md",
                "MARKDOWN_GOVERNANCE_DOCUMENT",
            ),
            (
                "tests/test_g36_01_intelligent_validation_engine_v0.py",
                "PYTHON_TEST_MODULE",
            ),
        ],
        name="multi",
    )
    artifact = _analyze(tmp_path, source, name="ive-multi")[
        "intelligent_validation_plan_artifact"
    ]

    assert (
        artifact["impact_classification"]["overall_classification"]
        == "MULTI_COMPONENT"
    )
    assert {
        item["component_type"] for item in artifact["affected_components"]
    } == {"PLATFORM_CORE", "GOVERNANCE", "TEST_INFRASTRUCTURE"}
    assert (
        artifact["impact_classification"]["probabilistic_inference_used"]
        is False
    )
    assert artifact["impact_classification"]["heuristic_inference_used"] is False
    assert artifact["validation_recommendation"]["full_regression"]["required"] is True


def test_ive_0_provider_classification_and_validation_dimension(tmp_path) -> None:
    source = _normalized_change(
        tmp_path,
        targets=[("aigol/provider.py", "PYTHON_PROVIDER_MODULE")],
        name="provider",
    )
    artifact = _analyze(tmp_path, source, name="ive-provider")[
        "intelligent_validation_plan_artifact"
    ]

    assert (
        artifact["impact_classification"]["overall_classification"] == "PROVIDER"
    )
    recommendation = artifact["validation_recommendation"]
    assert recommendation["required_provider_validation"]
    assert recommendation["required_worker_validation"] == []
    assert recommendation["required_authorization_validation"] == []


def test_ive_0_direct_inventory_covers_all_constitutional_component_types(
    tmp_path,
) -> None:
    source = _normalized_change(
        tmp_path,
        targets=[
            (
                "aigol/authorization/authorization_record.py",
                "PYTHON_AUTHORIZATION_MODULE",
            ),
            ("aigol/workers/filesystem_worker.py", "PYTHON_WORKER_MODULE"),
            ("aigol/cli/aicli.py", "PYTHON_AICLI_MODULE"),
            (
                "aigol/runtime/replay_certification_runtime.py",
                "PYTHON_REPLAY_MODULE",
            ),
            (
                "docs/product_lifecycle/PRODUCT_1_EXECUTION_PHASE_V1.md",
                "MARKDOWN_DOCUMENT",
            ),
        ],
        name="direct-inventory",
    )
    artifact = _analyze(tmp_path, source, name="ive-direct-inventory")[
        "intelligent_validation_plan_artifact"
    ]

    assert artifact["analysis_strategy"] == "IVE_0_DIRECT_EXACT_PATH_DISCOVERY"
    assert {
        item["component_type"] for item in artifact["affected_components"]
    } == {
        "AUTHORIZATION",
        "WORKER",
        "AICLI",
        "REPLAY",
        "DOCUMENTATION",
    }
    recommendation = artifact["validation_recommendation"]
    assert recommendation["required_authorization_validation"]
    assert recommendation["required_worker_validation"]
    assert recommendation["required_aicli_validation"]
    assert recommendation["required_replay_validation"]
    assert recommendation["full_regression"]["required"] is True


def test_ive_0_is_deterministic_for_identical_normalized_change(tmp_path) -> None:
    source = _normalized_change(
        tmp_path,
        targets=[
            (
                "aigol/runtime/intelligent_validation_engine_v0.py",
                "PYTHON_RUNTIME_MODULE",
            )
        ],
        name="deterministic",
    )
    first = _analyze(
        tmp_path,
        source,
        name="ive-first",
        analysis_id="IVE-G36-01-FIRST",
    )
    second = _analyze(
        tmp_path,
        source,
        name="ive-second",
        analysis_id="IVE-G36-01-SECOND",
    )

    assert (
        first["intelligent_validation_plan_hash"]
        == second["intelligent_validation_plan_hash"]
    )
    assert first["affected_components"] == second["affected_components"]
    assert first["impact_classification"] == second["impact_classification"]
    assert first["validation_recommendation"] == second["validation_recommendation"]


def test_ive_0_fails_closed_on_invalid_source_binding_without_execution(tmp_path) -> None:
    source = _normalized_change(
        tmp_path,
        targets=[
            (
                "aigol/runtime/intelligent_validation_engine_v0.py",
                "PYTHON_RUNTIME_MODULE",
            )
        ],
        name="invalid",
    )
    capture = analyze_intelligent_validation_scope(
        ive_analysis_id="IVE-G36-01-INVALID",
        normalized_change_artifact=source,
        normalized_change_reference=source["normalization_id"],
        normalized_change_hash=_hash("wrong"),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "ive-invalid",
    )
    reconstructed = reconstruct_intelligent_validation_engine_v0_replay(
        tmp_path / "ive-invalid"
    )

    assert capture["analysis_status"] == FAILED_CLOSED
    assert capture["fail_closed"] is True
    assert capture["affected_components"] == []
    assert capture["validation_executed"] is False
    assert capture["authorization_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["provider_invoked"] is False
    assert (
        capture["validation_recommendation"]["full_regression"]["required"]
        is True
    )
    assert reconstructed["fail_closed"] is True


def test_ive_0_replay_tampering_fails_closed(tmp_path) -> None:
    source = _normalized_change(
        tmp_path,
        targets=[
            (
                "aigol/runtime/intelligent_validation_engine_v0.py",
                "PYTHON_RUNTIME_MODULE",
            )
        ],
        name="tamper",
    )
    _analyze(tmp_path, source, name="ive-tamper")
    replay_file = (
        tmp_path
        / "ive-tamper"
        / "000_intelligent_validation_plan_recorded.json"
    )
    wrapper = load_json(replay_file)
    wrapper["artifact"]["impact_classification"][
        "overall_classification"
    ] = "TAMPERED"
    replay_file.write_text(json.dumps(wrapper), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="IVE-0 replay hash mismatch"):
        reconstruct_intelligent_validation_engine_v0_replay(
            tmp_path / "ive-tamper"
        )


def test_ive_0_artifact_tampering_fails_closed() -> None:
    artifact = {
        "artifact_type": INTELLIGENT_VALIDATION_PLAN_ARTIFACT_V1,
        "artifact_hash": _hash("not-the-artifact"),
    }

    with pytest.raises(FailClosedRuntimeError, match="IVE-0 artifact hash mismatch"):
        validate_intelligent_validation_plan_artifact(deepcopy(artifact))


def test_ive_0_is_registered_as_non_authoritative_platform_capability() -> None:
    record = lookup_platform_capability_certification(
        "INTELLIGENT_VALIDATION_ENGINE_V0"
    )

    assert is_platform_capability_certified("INTELLIGENT_VALIDATION_ENGINE_V0")
    assert (
        record["implementation_owner"]
        == "aigol.runtime.intelligent_validation_engine_v0"
    )
    assert record["capability_owner"] == "PLATFORM_CORE_VALIDATION_PLANNING"
    assert record["runtime_execution_authority"] is False
    assert record["human_interface_authority"] is False
