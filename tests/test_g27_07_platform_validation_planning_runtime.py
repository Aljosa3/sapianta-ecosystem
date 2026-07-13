from __future__ import annotations

from copy import deepcopy

import pytest

from aigol.runtime.implementation_manifest_runtime import CREATE_ONLY, create_implementation_manifest
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_certification_registry import (
    is_platform_capability_certified,
    lookup_platform_capability_certification,
)
from aigol.runtime.platform_change_impact_analysis_runtime import analyze_platform_change_impact
from aigol.runtime.platform_change_normalization_runtime import normalize_platform_change
from aigol.runtime.platform_validation_planning_runtime import (
    FAILED_CLOSED,
    PLATFORM_VALIDATION_PLAN_ARTIFACT_V1,
    VALIDATION_PLAN_COMPOSED_WITH_UNRESOLVED_MAPPINGS,
    plan_platform_validation,
    reconstruct_platform_validation_plan_replay,
    validate_platform_validation_plan_artifact,
)
from aigol.runtime.transport.serialization import load_json, replay_hash


CREATED_AT = "2026-07-13T00:00:00Z"


def _hash(label: str) -> str:
    return replay_hash({"label": label})


def _impact(tmp_path) -> dict:
    manifest_capture = create_implementation_manifest(
        manifest_id="MANIFEST-G27-07",
        canonical_chain_id="CHAIN-G27-07",
        implementation_bundle_id="G27_07_VALIDATION_PLANNING",
        source_candidate_reference="CANDIDATE-G27-07",
        source_candidate_hash=_hash("candidate"),
        implementation_handoff_reference="HANDOFF-G27-07",
        implementation_handoff_hash=_hash("handoff"),
        provider_generation_authorization_reference="AUTH-G27-07",
        provider_generation_authorization_hash=_hash("authorization"),
        provider_response_reference="RESPONSE-G27-07",
        provider_response_hash=_hash("response"),
        target_domain="PLATFORM_CORE",
        target_resource="VALIDATION_PLANNING",
        target_worker=None,
        generated_files=[
            {
                "file_entry_id": "FILE-G27-07-RUNTIME",
                "target_path": "aigol/runtime/platform_change_normalization_runtime.py",
                "artifact_type": "PYTHON_RUNTIME_MODULE",
                "operation": CREATE_ONLY,
                "content": "VALUE = 1\n",
                "validation_requirements": [],
            }
        ],
        generated_tests=[],
        validation_requirements=["git diff --check"],
        known_gaps=[],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "manifest",
    )
    manifest = manifest_capture["implementation_manifest_artifact"]
    normalization = normalize_platform_change(
        normalization_id="NORMALIZATION-G27-07",
        source_artifact=manifest,
        source_reference=manifest["manifest_id"],
        source_hash=manifest["artifact_hash"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "normalization",
    )["normalized_change_artifact"]
    return analyze_platform_change_impact(
        impact_analysis_id="IMPACT-G27-07",
        normalized_change_artifact=normalization,
        normalized_change_reference=normalization["normalization_id"],
        normalized_change_hash=normalization["normalized_change_hash"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "impact",
    )["platform_change_impact_artifact"]


def _plan(tmp_path, impact: dict, name: str = "plan") -> dict:
    return plan_platform_validation(
        validation_plan_id=f"PLAN-G27-07-{name}",
        platform_change_impact_artifact=impact,
        platform_change_impact_reference=impact["impact_analysis_id"],
        platform_change_impact_hash=impact["platform_change_impact_hash"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / name,
    )


def test_composes_ordered_requirements_and_reconstructs_replay(tmp_path) -> None:
    impact = _impact(tmp_path)
    capture = _plan(tmp_path, impact)
    artifact = capture["platform_validation_plan_artifact"]
    reconstructed = reconstruct_platform_validation_plan_replay(tmp_path / "plan")

    assert artifact["artifact_type"] == PLATFORM_VALIDATION_PLAN_ARTIFACT_V1
    assert artifact["planning_status"] == VALIDATION_PLAN_COMPOSED_WITH_UNRESOLVED_MAPPINGS
    assert artifact["platform_change_impact_artifact_hash"] == impact["artifact_hash"]
    assert [item["requirement_index"] for item in artifact["validation_requirements"]] == list(
        range(artifact["validation_requirement_count"])
    )
    categories = {item["requirement_category"] for item in artifact["validation_requirements"]}
    assert categories == {"CAPABILITY", "CONSTITUTIONAL_LAYER", "GOVERNANCE", "REPLAY", "CERTIFICATION"}
    assert artifact["allowlisted_command_references"] == []
    assert reconstructed["platform_validation_plan_hash"] == artifact["platform_validation_plan_hash"]
    assert validate_platform_validation_plan_artifact(artifact) == artifact


def test_planning_is_deterministic_for_identical_impact(tmp_path) -> None:
    impact = _impact(tmp_path)
    first = _plan(tmp_path, impact, "first")
    second = _plan(tmp_path, impact, "second")

    assert first["platform_validation_plan_hash"] == second["platform_validation_plan_hash"]
    assert first["validation_requirements"] == second["validation_requirements"]


def test_only_valid_non_failed_impact_is_accepted(tmp_path) -> None:
    impact = _impact(tmp_path)
    invalid = deepcopy(impact)
    invalid["artifact_type"] = "NORMALIZED_CHANGE_ARTIFACT_V1"
    invalid.pop("artifact_hash")
    invalid["artifact_hash"] = replay_hash(invalid)

    capture = _plan(tmp_path, invalid)

    assert capture["planning_status"] == FAILED_CLOSED
    assert "impact artifact type mismatch" in capture["failure_reason"]


def test_source_reference_and_hash_are_bound(tmp_path) -> None:
    impact = _impact(tmp_path)
    wrong_reference = plan_platform_validation(
        validation_plan_id="PLAN-WRONG-REFERENCE",
        platform_change_impact_artifact=impact,
        platform_change_impact_reference="OTHER-IMPACT",
        platform_change_impact_hash=impact["platform_change_impact_hash"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "wrong-reference",
    )
    wrong_hash = plan_platform_validation(
        validation_plan_id="PLAN-WRONG-HASH",
        platform_change_impact_artifact=impact,
        platform_change_impact_reference=impact["impact_analysis_id"],
        platform_change_impact_hash=_hash("wrong"),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "wrong-hash",
    )

    assert "reference mismatch" in wrong_reference["failure_reason"]
    assert "hash mismatch" in wrong_hash["failure_reason"]


def test_registry_binding_mismatch_fails_closed(tmp_path) -> None:
    impact = _impact(tmp_path)
    invalid = deepcopy(impact)
    invalid["affected_capabilities"][0]["certification_record_hash"] = _hash("wrong-registry-record")
    invalid["platform_change_impact_hash"] = _rehash_impact(invalid)
    invalid.pop("artifact_hash")
    invalid["artifact_hash"] = replay_hash(invalid)

    capture = _plan(tmp_path, invalid)

    assert capture["planning_status"] == FAILED_CLOSED
    assert "capability registry binding mismatch" in capture["failure_reason"]


def test_plan_never_constructs_candidates_or_grants_authority(tmp_path) -> None:
    artifact = _plan(tmp_path, _impact(tmp_path))["platform_validation_plan_artifact"]

    assert artifact["validation_candidates_constructed"] is False
    assert artifact["validation_executed"] is False
    assert artifact["provider_invoked"] is False
    assert artifact["worker_invoked"] is False
    assert artifact["execution_authorized"] is False
    assert artifact["repository_mutated"] is False
    assert artifact["certification_performed"] is False
    assert all(value is False for value in artifact["authority_flags"].values())


def test_replay_tampering_fails_closed(tmp_path) -> None:
    _plan(tmp_path, _impact(tmp_path))
    replay_file = tmp_path / "plan" / "000_platform_validation_plan_recorded.json"
    wrapper = load_json(replay_file)
    wrapper["artifact"]["validation_requirements"][0]["requirement_type"] = "TAMPERED"
    replay_file.write_text(__import__("json").dumps(wrapper), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="replay hash mismatch"):
        reconstruct_platform_validation_plan_replay(tmp_path / "plan")


def test_capability_is_registered() -> None:
    record = lookup_platform_capability_certification("PLATFORM_VALIDATION_PLANNING")

    assert is_platform_capability_certified("PLATFORM_VALIDATION_PLANNING") is True
    assert record["implementation_owner"] == "aigol.runtime.platform_validation_planning_runtime"
    assert record["runtime_execution_authority"] is False


def _rehash_impact(artifact: dict) -> str:
    return replay_hash(
        {
            "normalized_change_artifact_type": artifact["normalized_change_artifact_type"],
            "normalized_change_reference": artifact["normalized_change_reference"],
            "normalized_change_hash": artifact["normalized_change_hash"],
            "normalized_change_artifact_hash": artifact["normalized_change_artifact_hash"],
            "impact_entries": artifact["impact_entries"],
            "affected_capabilities": artifact["affected_capabilities"],
            "affected_constitutional_layers": artifact["affected_constitutional_layers"],
            "affected_governance_surfaces": artifact["affected_governance_surfaces"],
            "affected_replay_surfaces": artifact["affected_replay_surfaces"],
            "affected_certification_surfaces": artifact["affected_certification_surfaces"],
            "unresolved_mappings": artifact["unresolved_mappings"],
            "impact_status": artifact["impact_status"],
            "mapping_policy": artifact["mapping_policy"],
            "authority_flags": artifact["authority_flags"],
            "failure_reason": artifact["failure_reason"],
        }
    )
