"""Focused tests for G27-05 Platform Change Impact Analysis."""

from __future__ import annotations

from copy import deepcopy

import pytest

from aigol.runtime.implementation_manifest_runtime import CREATE_ONLY, create_implementation_manifest
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_certification_registry import (
    is_platform_capability_certified,
    platform_capability_component_owner,
)
from aigol.runtime.platform_change_impact_analysis_runtime import (
    CHANGE_IMPACT_ANALYZED_WITH_UNRESOLVED_MAPPINGS,
    FAILED_CLOSED,
    PLATFORM_CHANGE_IMPACT_ARTIFACT_V1,
    analyze_platform_change_impact,
    reconstruct_platform_change_impact_replay,
    validate_platform_change_impact_artifact,
)
from aigol.runtime.platform_change_normalization_runtime import normalize_platform_change
from aigol.runtime.transport.serialization import load_json, replay_hash


CREATED_AT = "2026-07-13T00:00:00Z"


def _hash(label: str) -> str:
    return replay_hash({"label": label})


def _normalized_change(tmp_path, files: list[dict], name: str = "source") -> dict:
    manifest_capture = create_implementation_manifest(
        manifest_id=f"MANIFEST-G27-05-{name}",
        canonical_chain_id="CHAIN-G27-05",
        implementation_bundle_id="G27_05_CHANGE_IMPACT",
        source_candidate_reference="CANDIDATE-G27-05",
        source_candidate_hash=_hash("candidate"),
        implementation_handoff_reference="HANDOFF-G27-05",
        implementation_handoff_hash=_hash("handoff"),
        provider_generation_authorization_reference="AUTH-G27-05",
        provider_generation_authorization_hash=_hash("authorization"),
        provider_response_reference="RESPONSE-G27-05",
        provider_response_hash=_hash("response"),
        target_domain="PLATFORM_CORE",
        target_resource="CHANGE_IMPACT",
        target_worker=None,
        generated_files=files,
        generated_tests=[],
        validation_requirements=["git diff --check"],
        known_gaps=[],
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"manifest-{name}",
    )
    manifest = manifest_capture["implementation_manifest_artifact"]
    normalized_capture = normalize_platform_change(
        normalization_id=f"NORMALIZATION-G27-05-{name}",
        source_artifact=manifest,
        source_reference=manifest["manifest_id"],
        source_hash=manifest["artifact_hash"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"normalization-{name}",
    )
    assert normalized_capture["fail_closed"] is False
    return normalized_capture["normalized_change_artifact"]


def _normalization_runtime_file() -> dict:
    return {
        "file_entry_id": "FILE-G27-05-RUNTIME",
        "target_path": "aigol/runtime/platform_change_normalization_runtime.py",
        "artifact_type": "PYTHON_RUNTIME_MODULE",
        "operation": CREATE_ONLY,
        "content": "VALUE = 1\n",
        "validation_requirements": [],
    }


def _normalization_governance_document() -> dict:
    return {
        "file_entry_id": "FILE-G27-05-GOVERNANCE",
        "target_path": "docs/governance/G27_04_PLATFORM_CHANGE_NORMALIZATION_CAPABILITY.md",
        "artifact_type": "GOVERNANCE_DOCUMENT_MARKDOWN",
        "operation": CREATE_ONLY,
        "content": "# G27-04\n",
        "validation_requirements": [],
    }


def _analyze(tmp_path, source: dict, name: str = "impact") -> dict:
    return analyze_platform_change_impact(
        impact_analysis_id=f"IMPACT-G27-05-{name}",
        normalized_change_artifact=source,
        normalized_change_reference=source["normalization_id"],
        normalized_change_hash=source["normalized_change_hash"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / name,
    )


def test_analyzes_capability_layers_and_surfaces_and_reconstructs(tmp_path) -> None:
    source = _normalized_change(
        tmp_path,
        [_normalization_governance_document(), _normalization_runtime_file()],
    )
    capture = _analyze(tmp_path, source)
    artifact = capture["platform_change_impact_artifact"]
    reconstructed = reconstruct_platform_change_impact_replay(tmp_path / "impact")

    assert artifact["artifact_type"] == PLATFORM_CHANGE_IMPACT_ARTIFACT_V1
    assert artifact["impact_status"] == CHANGE_IMPACT_ANALYZED_WITH_UNRESOLVED_MAPPINGS
    assert artifact["normalized_change_hash"] == source["normalized_change_hash"]
    assert [item["capability_identifier"] for item in artifact["affected_capabilities"]] == [
        "PLATFORM_CHANGE_NORMALIZATION"
    ]
    assert [item["constitutional_layer"] for item in artifact["affected_constitutional_layers"]] == [
        "L2",
        "L3",
    ]
    governance_ids = {item["surface_id"] for item in artifact["affected_governance_surfaces"]}
    assert "DECISION_SPINE_GOVERNANCE" in governance_ids
    assert "GOVERNANCE_SYSTEM" in governance_ids
    replay_ids = {item["surface_id"] for item in artifact["affected_replay_surfaces"]}
    assert "DECISION_SPINE_REPLAY_LINEAGE" in replay_ids
    assert "GOVERNANCE_EVIDENCE_REPLAY_LINEAGE" in replay_ids
    certification_ids = {item["surface_id"] for item in artifact["affected_certification_surfaces"]}
    assert "PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY" in certification_ids
    assert "CAPABILITY_CERTIFICATION:PLATFORM_CHANGE_NORMALIZATION" in certification_ids
    assert all(item["mapping_stage"] == "CHANGE_NORMALIZATION" for item in artifact["unresolved_mappings"])
    assert reconstructed["platform_change_impact_hash"] == artifact["platform_change_impact_hash"]
    assert validate_platform_change_impact_artifact(artifact) == artifact


def test_impact_analysis_is_deterministic_for_identical_normalized_change(tmp_path) -> None:
    source = _normalized_change(tmp_path, [_normalization_runtime_file()])
    first = _analyze(tmp_path, source, "first")
    second = _analyze(tmp_path, source, "second")

    assert first["platform_change_impact_hash"] == second["platform_change_impact_hash"]
    assert first["affected_capabilities"] == second["affected_capabilities"]
    assert first["affected_governance_surfaces"] == second["affected_governance_surfaces"]


def test_unknown_capability_mapping_fails_closed(tmp_path) -> None:
    source = _normalized_change(
        tmp_path,
        [
            {
                **_normalization_runtime_file(),
                "file_entry_id": "FILE-UNKNOWN",
                "target_path": "aigol/runtime/not_registered_change.py",
            }
        ],
        "unknown",
    )
    capture = _analyze(tmp_path, source)

    assert capture["impact_status"] == FAILED_CLOSED
    assert capture["affected_capabilities"] == []
    assert "no capability mapping" in capture["failure_reason"]


def test_shared_implementation_owner_mapping_fails_closed_as_ambiguous(tmp_path) -> None:
    source = _normalized_change(
        tmp_path,
        [
            {
                **_normalization_runtime_file(),
                "file_entry_id": "FILE-AMBIGUOUS",
                "target_path": "aigol/runtime/platform_core_cognition_layer.py",
            }
        ],
        "ambiguous",
    )
    capture = _analyze(tmp_path, source)

    assert capture["impact_status"] == FAILED_CLOSED
    assert "ambiguous capability mapping" in capture["failure_reason"]


def test_only_normalized_change_artifact_is_accepted(tmp_path) -> None:
    source = _normalized_change(tmp_path, [_normalization_runtime_file()])
    invalid = deepcopy(source)
    invalid["artifact_type"] = "IMPLEMENTATION_MANIFEST_ARTIFACT_V1"
    invalid.pop("artifact_hash")
    invalid["artifact_hash"] = replay_hash(invalid)

    capture = analyze_platform_change_impact(
        impact_analysis_id="IMPACT-INVALID-SOURCE",
        normalized_change_artifact=invalid,
        normalized_change_reference=invalid["normalization_id"],
        normalized_change_hash=invalid["normalized_change_hash"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "invalid-source",
    )

    assert capture["impact_status"] == FAILED_CLOSED
    assert "change normalization artifact type mismatch" in capture["failure_reason"]


def test_source_reference_and_hash_are_bound(tmp_path) -> None:
    source = _normalized_change(tmp_path, [_normalization_runtime_file()])
    wrong_reference = analyze_platform_change_impact(
        impact_analysis_id="IMPACT-WRONG-REFERENCE",
        normalized_change_artifact=source,
        normalized_change_reference="OTHER-NORMALIZATION",
        normalized_change_hash=source["normalized_change_hash"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "wrong-reference",
    )
    wrong_hash = analyze_platform_change_impact(
        impact_analysis_id="IMPACT-WRONG-HASH",
        normalized_change_artifact=source,
        normalized_change_reference=source["normalization_id"],
        normalized_change_hash=_hash("other"),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "wrong-hash",
    )

    assert "reference mismatch" in wrong_reference["failure_reason"]
    assert "hash mismatch" in wrong_hash["failure_reason"]


def test_impact_artifact_preserves_non_authoritative_boundary(tmp_path) -> None:
    source = _normalized_change(tmp_path, [_normalization_runtime_file()])
    artifact = _analyze(tmp_path, source)["platform_change_impact_artifact"]

    assert artifact["impact_analysis_performed"] is True
    assert artifact["validation_planned"] is False
    assert artifact["tests_selected"] is False
    assert artifact["validation_executed"] is False
    assert artifact["provider_invoked"] is False
    assert artifact["worker_invoked"] is False
    assert artifact["execution_authorized"] is False
    assert artifact["certification_performed"] is False
    assert artifact["repository_mutated"] is False
    assert all(value is False for value in artifact["authority_flags"].values())


def test_reconstruction_detects_tampering(tmp_path) -> None:
    source = _normalized_change(tmp_path, [_normalization_runtime_file()])
    _analyze(tmp_path, source)
    path = tmp_path / "impact" / "000_platform_change_impact_recorded.json"
    wrapper = load_json(path)
    wrapper["artifact"]["affected_constitutional_layers"][0]["constitutional_layer"] = "L0"
    path.write_text(str(wrapper), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError):
        reconstruct_platform_change_impact_replay(tmp_path / "impact")


def test_change_impact_analysis_is_registered_as_platform_core_metadata() -> None:
    assert is_platform_capability_certified("PLATFORM_CHANGE_IMPACT_ANALYSIS") is True
    assert (
        platform_capability_component_owner("PLATFORM_CHANGE_IMPACT_ANALYSIS")
        == "aigol.runtime.platform_change_impact_analysis_runtime"
    )
