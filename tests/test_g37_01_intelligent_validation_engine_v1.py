"""Deterministic certification coverage for G37-01 IVE-1."""

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
    FAILED_CLOSED,
    SEMANTIC_VALIDATION_DEPENDENCY_MODEL_V1,
    SEMANTIC_VALIDATION_SCOPE_SELECTED,
    reconstruct_semantic_validation_selection_replay,
    select_semantic_validation_scope,
    semantic_validation_dependency_model,
    validate_semantic_validation_dependency_model,
    validate_semantic_validation_selection_artifact,
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


def _ive_0_plan(
    tmp_path,
    *,
    target_path: str,
    artifact_type: str,
    name: str,
) -> dict:
    manifest_capture = create_implementation_manifest(
        manifest_id=f"MANIFEST-G37-01-{name}",
        canonical_chain_id="CHAIN-G37-01",
        implementation_bundle_id="G37_01_INTELLIGENT_VALIDATION_ENGINE_V1",
        source_candidate_reference="CANDIDATE-G37-01",
        source_candidate_hash=_hash("candidate"),
        implementation_handoff_reference="HANDOFF-G37-01",
        implementation_handoff_hash=_hash("handoff"),
        provider_generation_authorization_reference="AUTH-G37-01",
        provider_generation_authorization_hash=_hash("authorization"),
        provider_response_reference="RESPONSE-G37-01",
        provider_response_hash=_hash("response"),
        target_domain="PLATFORM_CORE",
        target_resource="INTELLIGENT_VALIDATION_ENGINE_V1",
        target_worker=None,
        generated_files=[
            {
                "file_entry_id": f"FILE-G37-01-{name}",
                "target_path": target_path,
                "artifact_type": artifact_type,
                "operation": CREATE_ONLY,
                "content": f"G37-01 deterministic content for {name}\n",
                "validation_requirements": [],
            }
        ],
        generated_tests=[],
        validation_requirements=[
            "python -m pytest tests/test_g37_01_intelligent_validation_engine_v1.py"
        ],
        known_gaps=[],
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"{name}-manifest",
    )
    manifest = manifest_capture["implementation_manifest_artifact"]
    normalization = normalize_platform_change(
        normalization_id=f"NORMALIZATION-G37-01-{name}",
        source_artifact=manifest,
        source_reference=manifest["manifest_id"],
        source_hash=manifest["artifact_hash"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"{name}-normalization",
    )["normalized_change_artifact"]
    return analyze_intelligent_validation_scope(
        ive_analysis_id=f"IVE-0-G37-01-{name}",
        normalized_change_artifact=normalization,
        normalized_change_reference=normalization["normalization_id"],
        normalized_change_hash=normalization["normalized_change_hash"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"{name}-ive-0",
    )["intelligent_validation_plan_artifact"]


def _select(
    tmp_path,
    source: dict,
    *,
    name: str,
    selection_id: str | None = None,
) -> dict:
    return select_semantic_validation_scope(
        selection_id=selection_id or f"IVE-1-G37-01-{name}",
        intelligent_validation_plan_artifact=source,
        intelligent_validation_plan_reference=source["ive_analysis_id"],
        intelligent_validation_plan_hash=source[
            "intelligent_validation_plan_hash"
        ],
        created_at=CREATED_AT,
        replay_dir=tmp_path / name,
    )


def test_dependency_model_is_explicit_deterministic_and_non_authoritative() -> None:
    first = semantic_validation_dependency_model()
    second = semantic_validation_dependency_model()

    assert first == second
    assert first["artifact_type"] == SEMANTIC_VALIDATION_DEPENDENCY_MODEL_V1
    assert first["capability_dependencies"]
    assert first["component_type_dependencies"]
    assert first["mapping_policy"]["declared_edges_only"] is True
    assert first["mapping_policy"]["probabilistic_inference_allowed"] is False
    assert all(value is False for value in first["authority_flags"].values())
    assert validate_semantic_validation_dependency_model(first) == first


def test_ive_1_selects_direct_and_transitive_platform_scope_and_reconstructs(
    tmp_path,
) -> None:
    source = _ive_0_plan(
        tmp_path,
        target_path="aigol/runtime/intelligent_validation_engine_v1.py",
        artifact_type="PYTHON_RUNTIME_MODULE",
        name="platform-core",
    )
    capture = _select(tmp_path, source, name="selection")
    artifact = capture["semantic_validation_selection_artifact"]
    reconstructed = reconstruct_semantic_validation_selection_replay(
        tmp_path / "selection"
    )

    assert artifact["selection_status"] == SEMANTIC_VALIDATION_SCOPE_SELECTED
    assert artifact["direct_validation_subject_count"] == 1
    assert {
        item["dependent_identifier"]
        for item in artifact["transitive_dependencies"]
        if item["dependency_kind"] == "COMPONENT_TYPE"
    } == {
        "GOVERNANCE",
        "AUTHORIZATION",
        "PROVIDER",
        "WORKER",
        "REPLAY",
    }
    assert artifact["direct_validation_requirement_count"] > 0
    assert artifact["transitive_validation_requirement_count"] > 0
    assert {
        item["validation_scope"]
        for item in artifact["selected_validation_requirements"]
    } == {"DIRECT", "TRANSITIVE"}
    assert artifact["full_regression"] == source["validation_recommendation"][
        "full_regression"
    ]
    assert artifact["human_approval"]["required_before_execution"] is True
    assert artifact["human_approval_recorded"] is False
    assert artifact["validation_executed"] is False
    assert artifact["authorization_invoked"] is False
    assert artifact["worker_invoked"] is False
    assert artifact["provider_invoked"] is False
    assert all(value is False for value in artifact["authority_flags"].values())
    assert reconstructed["semantic_validation_selection_hash"] == artifact[
        "semantic_validation_selection_hash"
    ]
    assert validate_semantic_validation_selection_artifact(artifact) == artifact


def test_ive_1_uses_certified_capability_composition_dependencies(tmp_path) -> None:
    source = _ive_0_plan(
        tmp_path,
        target_path="aigol/runtime/platform_knowledge_runtime.py",
        artifact_type="PYTHON_RUNTIME_MODULE",
        name="knowledge",
    )
    artifact = _select(tmp_path, source, name="knowledge-selection")[
        "semantic_validation_selection_artifact"
    ]

    capability_dependencies = {
        item["dependent_identifier"]: item
        for item in artifact["transitive_dependencies"]
        if item["dependency_kind"] == "CAPABILITY"
    }
    assert set(capability_dependencies) == {
        "UNIFIED_PLATFORM_QUERY_ROUTER",
        "CANONICAL_PLATFORM_PRESENTATION_LAYER",
        "GENERATION_CERTIFICATION_COMPOSITION_SERVICE",
    }
    assert capability_dependencies["UNIFIED_PLATFORM_QUERY_ROUTER"][
        "dependency_path"
    ] == [
        "PLATFORM_KNOWLEDGE_RUNTIME",
        "UNIFIED_PLATFORM_QUERY_ROUTER",
    ]
    assert {
        item["validation_subject_identifier"]
        for item in artifact["selected_validation_requirements"]
        if item["validation_dimension"] == "CAPABILITY_REGRESSION"
    } == set(capability_dependencies)


def test_ive_1_authorization_change_propagates_without_unrelated_aicli_scope(
    tmp_path,
) -> None:
    source = _ive_0_plan(
        tmp_path,
        target_path="aigol/authorization/authorization_record.py",
        artifact_type="PYTHON_AUTHORIZATION_MODULE",
        name="authorization",
    )
    artifact = _select(tmp_path, source, name="authorization-selection")[
        "semantic_validation_selection_artifact"
    ]
    transitive_types = {
        item["dependent_identifier"]
        for item in artifact["transitive_dependencies"]
        if item["dependency_kind"] == "COMPONENT_TYPE"
    }

    assert transitive_types == {"PROVIDER", "WORKER", "REPLAY"}
    assert "AICLI" not in transitive_types
    assert any(
        item["validation_scope"] == "DIRECT"
        and item["validation_dimension"] == "AUTHORIZATION"
        for item in artifact["selected_validation_requirements"]
    )
    assert any(
        item["validation_scope"] == "TRANSITIVE"
        and item["validation_dimension"] == "PROVIDER"
        for item in artifact["selected_validation_requirements"]
    )


def test_ive_1_is_deterministic_across_selection_identity(tmp_path) -> None:
    source = _ive_0_plan(
        tmp_path,
        target_path="aigol/runtime/intelligent_validation_engine_v1.py",
        artifact_type="PYTHON_RUNTIME_MODULE",
        name="deterministic",
    )
    first = _select(
        tmp_path,
        source,
        name="first",
        selection_id="IVE-1-FIRST",
    )
    second = _select(
        tmp_path,
        source,
        name="second",
        selection_id="IVE-1-SECOND",
    )

    assert first["semantic_validation_selection_hash"] == second[
        "semantic_validation_selection_hash"
    ]
    assert first["direct_validation_subjects"] == second[
        "direct_validation_subjects"
    ]
    assert first["transitive_dependencies"] == second[
        "transitive_dependencies"
    ]
    assert first["selected_validation_requirements"] == second[
        "selected_validation_requirements"
    ]


def test_ive_1_fails_closed_on_source_hash_mismatch_and_reconstructs(
    tmp_path,
) -> None:
    source = _ive_0_plan(
        tmp_path,
        target_path="aigol/runtime/intelligent_validation_engine_v1.py",
        artifact_type="PYTHON_RUNTIME_MODULE",
        name="invalid-source",
    )
    capture = select_semantic_validation_scope(
        selection_id="IVE-1-INVALID-SOURCE",
        intelligent_validation_plan_artifact=source,
        intelligent_validation_plan_reference=source["ive_analysis_id"],
        intelligent_validation_plan_hash=_hash("wrong"),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "invalid-selection",
    )
    reconstructed = reconstruct_semantic_validation_selection_replay(
        tmp_path / "invalid-selection"
    )

    assert capture["selection_status"] == FAILED_CLOSED
    assert capture["direct_validation_subjects"] == []
    assert capture["transitive_dependencies"] == []
    assert capture["selected_validation_requirements"] == []
    assert capture["semantic_validation_selection_artifact"][
        "full_regression"
    ]["required"] is True
    assert capture["validation_executed"] is False
    assert reconstructed["fail_closed"] is True


def test_dependency_model_and_replay_tampering_fail_closed(tmp_path) -> None:
    model = semantic_validation_dependency_model()
    tampered_model = deepcopy(model)
    tampered_model["component_type_dependencies"][0][
        "dependent_component_type"
    ] = "REPLAY"

    with pytest.raises(
        FailClosedRuntimeError,
        match="dependency model hash mismatch",
    ):
        validate_semantic_validation_dependency_model(tampered_model)

    rehashed_model = deepcopy(model)
    rehashed_model["component_type_dependencies"][0][
        "reason"
    ] = "REHASHED NONCANONICAL EDGE"
    edge = rehashed_model["component_type_dependencies"][0]
    edge.pop("edge_hash")
    edge["edge_hash"] = replay_hash(edge)
    rehashed_model.pop("dependency_model_hash")
    rehashed_model["dependency_model_hash"] = replay_hash(rehashed_model)

    with pytest.raises(
        FailClosedRuntimeError,
        match="differs from canonical model",
    ):
        validate_semantic_validation_dependency_model(rehashed_model)

    source = _ive_0_plan(
        tmp_path,
        target_path="aigol/runtime/intelligent_validation_engine_v1.py",
        artifact_type="PYTHON_RUNTIME_MODULE",
        name="tamper",
    )
    _select(tmp_path, source, name="tampered-replay")
    replay_file = (
        tmp_path
        / "tampered-replay"
        / "001_semantic_validation_selection_recorded.json"
    )
    wrapper = load_json(replay_file)
    wrapper["artifact"]["transitive_dependencies"][0]["reason"] = "TAMPERED"
    replay_file.write_text(json.dumps(wrapper), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="IVE-1 replay hash mismatch"):
        reconstruct_semantic_validation_selection_replay(
            tmp_path / "tampered-replay"
        )


def test_ive_1_is_registered_as_non_authoritative_platform_capability() -> None:
    record = lookup_platform_capability_certification(
        "INTELLIGENT_VALIDATION_ENGINE_V1"
    )

    assert is_platform_capability_certified("INTELLIGENT_VALIDATION_ENGINE_V1")
    assert (
        record["implementation_owner"]
        == "aigol.runtime.intelligent_validation_engine_v1"
    )
    assert record["runtime_execution_authority"] is False
    assert record["human_interface_authority"] is False
