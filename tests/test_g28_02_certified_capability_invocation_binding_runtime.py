"""Focused G28-02 certified capability invocation binding tests."""

from __future__ import annotations

from copy import deepcopy
import inspect
import json

import pytest

import aigol.runtime.certified_capability_invocation_binding_runtime as binding
from aigol.runtime.certified_capability_invocation_binding_runtime import (
    CERTIFIED_CAPABILITY_INVOCATION_COMPLETED,
    CERTIFIED_CAPABILITY_INVOCATION_RESULT_ARTIFACT_V1,
    FAILED_CLOSED,
    PLATFORM_CAPABILITY_COMPOSITION_COVERAGE,
    PLATFORM_CHANGE_IMPACT_ANALYSIS,
    PLATFORM_CHANGE_NORMALIZATION,
    PLATFORM_VALIDATION_PLANNING,
    certified_capability_invocation_adapters,
    invoke_certified_capability,
    reconstruct_certified_capability_invocation_replay,
    validate_certified_capability_invocation_result_artifact,
)
from aigol.runtime.implementation_manifest_runtime import CREATE_ONLY, create_implementation_manifest
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_certification_registry import (
    is_platform_capability_certified,
    lookup_platform_capability_certification,
    platform_capability_component_owner,
)
from aigol.runtime.platform_knowledge_runtime import query_platform_knowledge
from aigol.runtime.transport.serialization import load_json, replay_hash


CREATED_AT = "2026-07-13T00:00:00Z"


def _hash(label: str) -> str:
    return replay_hash({"label": label})


def _manifest(tmp_path) -> dict:
    capture = create_implementation_manifest(
        manifest_id="MANIFEST-G28-02",
        canonical_chain_id="CHAIN-G28-02",
        implementation_bundle_id="G28_02_CAPABILITY_INVOCATION",
        source_candidate_reference="CANDIDATE-G28-02",
        source_candidate_hash=_hash("candidate"),
        implementation_handoff_reference="HANDOFF-G28-02",
        implementation_handoff_hash=_hash("handoff"),
        provider_generation_authorization_reference="AUTH-G28-02",
        provider_generation_authorization_hash=_hash("authorization"),
        provider_response_reference="RESPONSE-G28-02",
        provider_response_hash=_hash("response"),
        target_domain="PLATFORM_CORE",
        target_resource="CAPABILITY_INVOCATION",
        target_worker=None,
        generated_files=[
            {
                "file_entry_id": "FILE-G28-02-RUNTIME",
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
    return capture["implementation_manifest_artifact"]


def _knowledge(capability_id: str) -> dict:
    return query_platform_knowledge(
        query=f"Where is {capability_id} implemented?",
        capability_identifier=capability_id,
    )


def _invoke(
    tmp_path,
    *,
    capability_id: str,
    inputs: dict,
    name: str,
    discovery: dict | None = None,
) -> dict:
    return invoke_certified_capability(
        invocation_id=f"INVOCATION-G28-02-{name}",
        session_id="SESSION-G28-02",
        platform_knowledge_response=discovery or _knowledge(capability_id),
        platform_knowledge_response_reference=f"KNOWLEDGE-G28-02-{name}",
        discovered_capability_identifier=capability_id,
        capability_inputs=inputs,
        invoked_by="PLATFORM_CORE",
        invoked_at=CREATED_AT,
        replay_dir=tmp_path / name,
    )


def _normalization(tmp_path, name: str = "normalization") -> dict:
    manifest = _manifest(tmp_path)
    capture = _invoke(
        tmp_path,
        capability_id=PLATFORM_CHANGE_NORMALIZATION,
        inputs={
            "source_artifact": manifest,
            "source_reference": manifest["manifest_id"],
            "source_hash": manifest["artifact_hash"],
        },
        name=name,
    )
    assert capture["fail_closed"] is False
    return capture["capability_output_artifact"]


def _impact(tmp_path, name: str = "impact") -> dict:
    normalized = _normalization(tmp_path, f"{name}-normalization")
    capture = _invoke(
        tmp_path,
        capability_id=PLATFORM_CHANGE_IMPACT_ANALYSIS,
        inputs={
            "normalized_change_artifact": normalized,
            "normalized_change_reference": normalized["normalization_id"],
            "normalized_change_hash": normalized["normalized_change_hash"],
        },
        name=name,
    )
    assert capture["fail_closed"] is False
    return capture["capability_output_artifact"]


def test_valid_discovery_invokes_allowlisted_impact_analysis_and_reconstructs(tmp_path) -> None:
    normalized = _normalization(tmp_path)
    capture = _invoke(
        tmp_path,
        capability_id=PLATFORM_CHANGE_IMPACT_ANALYSIS,
        inputs={
            "normalized_change_artifact": normalized,
            "normalized_change_reference": normalized["normalization_id"],
            "normalized_change_hash": normalized["normalized_change_hash"],
        },
        name="impact",
    )
    result = capture["certified_capability_invocation_result_artifact"]
    reconstructed = reconstruct_certified_capability_invocation_replay(tmp_path / "impact")

    assert result["artifact_type"] == CERTIFIED_CAPABILITY_INVOCATION_RESULT_ARTIFACT_V1
    assert result["invocation_status"] == CERTIFIED_CAPABILITY_INVOCATION_COMPLETED
    assert result["capability_identifier"] == PLATFORM_CHANGE_IMPACT_ANALYSIS
    assert result["output_artifact_type"] == "PLATFORM_CHANGE_IMPACT_ARTIFACT_V1"
    assert result["output_artifact_hash"] == capture["capability_output_artifact"]["artifact_hash"]
    assert reconstructed["capability_identifier"] == PLATFORM_CHANGE_IMPACT_ANALYSIS
    assert reconstructed["replay_artifact_count"] == 6
    assert validate_certified_capability_invocation_result_artifact(result) == result


def test_all_allowlisted_read_only_adapters_reuse_canonical_entry_points(tmp_path) -> None:
    impact = _impact(tmp_path)
    planning = _invoke(
        tmp_path,
        capability_id=PLATFORM_VALIDATION_PLANNING,
        inputs={
            "platform_change_impact_artifact": impact,
            "platform_change_impact_reference": impact["impact_analysis_id"],
            "platform_change_impact_hash": impact["platform_change_impact_hash"],
        },
        name="planning",
    )

    assert planning["invocation_status"] == CERTIFIED_CAPABILITY_INVOCATION_COMPLETED
    assert planning["capability_output_artifact"]["artifact_type"] == (
        "PLATFORM_VALIDATION_PLAN_ARTIFACT_V1"
    )
    assert set(certified_capability_invocation_adapters()) == {
        PLATFORM_CAPABILITY_COMPOSITION_COVERAGE,
        PLATFORM_CHANGE_NORMALIZATION,
        PLATFORM_CHANGE_IMPACT_ANALYSIS,
        PLATFORM_VALIDATION_PLANNING,
    }


def test_invalid_platform_knowledge_response_hash_fails_closed(tmp_path) -> None:
    discovery = _knowledge(PLATFORM_CHANGE_NORMALIZATION)
    discovery["query"] = "tampered"
    manifest = _manifest(tmp_path)

    capture = _invoke(
        tmp_path,
        capability_id=PLATFORM_CHANGE_NORMALIZATION,
        inputs={
            "source_artifact": manifest,
            "source_reference": manifest["manifest_id"],
            "source_hash": manifest["artifact_hash"],
        },
        name="invalid-discovery",
        discovery=discovery,
    )

    assert capture["invocation_status"] == FAILED_CLOSED
    assert "response hash mismatch" in capture["failure_reason"]


def test_discovered_capability_mismatch_fails_closed(tmp_path) -> None:
    capture = _invoke(
        tmp_path,
        capability_id=PLATFORM_CHANGE_NORMALIZATION,
        inputs={},
        name="mismatch",
        discovery=_knowledge(PLATFORM_CHANGE_IMPACT_ANALYSIS),
    )

    assert capture["fail_closed"] is True
    assert "discovered capability mismatch" in capture["failure_reason"]


def test_uncertified_discovery_fails_closed(tmp_path) -> None:
    discovery = _knowledge(PLATFORM_CHANGE_NORMALIZATION)
    discovery["is_certified"] = False
    discovery.pop("artifact_hash")
    discovery["artifact_hash"] = replay_hash(discovery)

    capture = _invoke(
        tmp_path,
        capability_id=PLATFORM_CHANGE_NORMALIZATION,
        inputs={},
        name="uncertified",
        discovery=discovery,
    )

    assert capture["fail_closed"] is True
    assert "uncertified" in capture["failure_reason"]


def test_superseded_capability_fails_closed(tmp_path, monkeypatch) -> None:
    original = lookup_platform_capability_certification(PLATFORM_CHANGE_NORMALIZATION)

    def superseded(_capability_id: str) -> dict:
        return {**original, "superseded_by": "REPLACEMENT_CAPABILITY"}

    monkeypatch.setattr(binding, "lookup_platform_capability_certification", superseded)
    capture = _invoke(
        tmp_path,
        capability_id=PLATFORM_CHANGE_NORMALIZATION,
        inputs={},
        name="superseded",
    )

    assert capture["fail_closed"] is True
    assert "superseded" in capture["failure_reason"]


def test_certified_capability_without_adapter_fails_closed(tmp_path) -> None:
    capability_id = "REPLAY_CERTIFICATION_RUNTIME"
    capture = _invoke(
        tmp_path,
        capability_id=capability_id,
        inputs={},
        name="missing-adapter",
    )

    assert capture["fail_closed"] is True
    assert "no allowlisted invocation adapter" in capture["failure_reason"]


def test_wrong_input_artifact_type_fails_closed(tmp_path) -> None:
    manifest = _manifest(tmp_path)
    capture = _invoke(
        tmp_path,
        capability_id=PLATFORM_CHANGE_IMPACT_ANALYSIS,
        inputs={
            "normalized_change_artifact": manifest,
            "normalized_change_reference": manifest["manifest_id"],
            "normalized_change_hash": manifest["artifact_hash"],
        },
        name="wrong-input-type",
    )

    assert capture["fail_closed"] is True
    assert "artifact type mismatch" in capture["failure_reason"]


def test_invalid_input_hash_fails_closed(tmp_path) -> None:
    normalized = _normalization(tmp_path)
    capture = _invoke(
        tmp_path,
        capability_id=PLATFORM_CHANGE_IMPACT_ANALYSIS,
        inputs={
            "normalized_change_artifact": normalized,
            "normalized_change_reference": normalized["normalization_id"],
            "normalized_change_hash": _hash("wrong"),
        },
        name="wrong-input-hash",
    )

    assert capture["fail_closed"] is True
    assert "input hash mismatch" in capture["failure_reason"]


def test_missing_required_input_fails_closed(tmp_path) -> None:
    capture = _invoke(
        tmp_path,
        capability_id=PLATFORM_CHANGE_IMPACT_ANALYSIS,
        inputs={},
        name="missing-input",
    )

    assert capture["fail_closed"] is True
    assert "missing required input" in capture["failure_reason"]


def test_unexpected_output_artifact_fails_closed(tmp_path, monkeypatch) -> None:
    normalized = _normalization(tmp_path)

    def wrong_output(**_kwargs):
        artifact = {"artifact_type": "UNEXPECTED_ARTIFACT_V1"}
        artifact["artifact_hash"] = replay_hash(artifact)
        return {"platform_change_impact_artifact": artifact}

    monkeypatch.setattr(binding, "analyze_platform_change_impact", wrong_output)
    capture = _invoke(
        tmp_path,
        capability_id=PLATFORM_CHANGE_IMPACT_ANALYSIS,
        inputs={
            "normalized_change_artifact": normalized,
            "normalized_change_reference": normalized["normalization_id"],
            "normalized_change_hash": normalized["normalized_change_hash"],
        },
        name="unexpected-output",
    )

    assert capture["fail_closed"] is True
    assert "unexpected output artifact" in capture["failure_reason"]


def test_replay_tamper_is_detected(tmp_path) -> None:
    normalized = _normalization(tmp_path)
    capture = _invoke(
        tmp_path,
        capability_id=PLATFORM_CHANGE_IMPACT_ANALYSIS,
        inputs={
            "normalized_change_artifact": normalized,
            "normalized_change_reference": normalized["normalization_id"],
            "normalized_change_hash": normalized["normalized_change_hash"],
        },
        name="tamper",
    )
    assert capture["fail_closed"] is False
    path = tmp_path / "tamper" / "002_invocation_adapter_selection_recorded.json"
    wrapper = load_json(path)
    wrapper["artifact"]["adapter_selection_status"] = "TAMPERED"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_certified_capability_invocation_replay(tmp_path / "tamper")


def test_no_worker_provider_mutation_or_dynamic_import_surface(tmp_path) -> None:
    normalized = _normalization(tmp_path)
    capture = _invoke(
        tmp_path,
        capability_id=PLATFORM_CHANGE_IMPACT_ANALYSIS,
        inputs={
            "normalized_change_artifact": normalized,
            "normalized_change_reference": normalized["normalization_id"],
            "normalized_change_hash": normalized["normalized_change_hash"],
        },
        name="boundaries",
    )
    source = inspect.getsource(binding)

    assert capture["worker_invoked"] is False
    assert capture["provider_invoked"] is False
    assert capture["repository_mutated"] is False
    assert capture["human_interface_authority"] is False
    assert capture["dynamic_import_used"] is False
    assert "importlib" not in source
    assert "__import__" not in source
    assert "import_module" not in source
    assert "implementation_owner)." not in source


def test_capability_registration_is_certified() -> None:
    capability_id = "CERTIFIED_CAPABILITY_INVOCATION_BINDING"
    assert is_platform_capability_certified(capability_id) is True
    assert platform_capability_component_owner(capability_id).endswith(
        "certified_capability_invocation_binding_runtime"
    )
