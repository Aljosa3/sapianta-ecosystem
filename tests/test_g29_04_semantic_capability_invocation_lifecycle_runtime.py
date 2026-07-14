"""Focused G29-04 semantic-selection to certified-invocation lifecycle tests."""

from __future__ import annotations

from copy import deepcopy
import inspect
import json

import pytest

import aigol.runtime.certified_capability_invocation_binding_runtime as g28_runtime
import aigol.runtime.semantic_capability_invocation_lifecycle_runtime as lifecycle_runtime
from aigol.runtime.certified_capability_invocation_binding_runtime import (
    PLATFORM_CHANGE_NORMALIZATION,
    certified_capability_invocation_adapters,
)
from aigol.runtime.implementation_manifest_runtime import CREATE_ONLY, create_implementation_manifest
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_certification_registry import (
    is_platform_capability_certified,
    lookup_platform_capability_certification,
    platform_capability_certification_registry,
    platform_capability_component_owner,
)
from aigol.runtime.platform_knowledge_runtime import query_platform_knowledge
from aigol.runtime.platform_presentation_layer import (
    CANONICAL_PLATFORM_PRESENTATION_ARTIFACT_V1,
    PRESENTATION_FAILED_CLOSED,
    PRESENTATION_READY,
    present_platform_response,
)
from aigol.runtime.platform_project_objective_inference import infer_platform_project_objective
from aigol.runtime.semantic_capability_invocation_lifecycle_runtime import (
    FAILED_CLOSED,
    LIFECYCLE_CLARIFICATION_REQUIRED,
    LIFECYCLE_COMPLETED,
    reconstruct_semantic_capability_invocation_lifecycle_replay,
    run_semantic_capability_invocation_lifecycle,
    validate_semantic_capability_invocation_lifecycle_result,
)
from aigol.runtime.semantic_capability_selection_runtime import select_semantic_capability
from aigol.runtime.semantic_capability_selection_runtime import NO_ADMISSIBLE_CAPABILITY
from aigol.runtime.transport.serialization import load_json, replay_hash


CREATED_AT = "2026-07-14T00:00:00Z"
CAPABILITY_ID = (
    "CANONICAL_SEMANTIC_SELECTION_TO_CERTIFIED_CAPABILITY_INVOCATION_LIFECYCLE_BINDING"
)


def _hash(label: str) -> str:
    return replay_hash({"label": label})


def _manifest(tmp_path) -> dict:
    capture = create_implementation_manifest(
        manifest_id="MANIFEST-G29-04",
        canonical_chain_id="CHAIN-G29-04",
        implementation_bundle_id="G29_04_LIFECYCLE",
        source_candidate_reference="CANDIDATE-G29-04",
        source_candidate_hash=_hash("candidate"),
        implementation_handoff_reference="HANDOFF-G29-04",
        implementation_handoff_hash=_hash("handoff"),
        provider_generation_authorization_reference="AUTH-G29-04",
        provider_generation_authorization_hash=_hash("authorization"),
        provider_response_reference="RESPONSE-G29-04",
        provider_response_hash=_hash("response"),
        target_domain="PLATFORM_CORE",
        target_resource="SEMANTIC_INVOCATION_LIFECYCLE",
        target_worker=None,
        generated_files=[
            {
                "file_entry_id": "FILE-G29-04",
                "target_path": "aigol/runtime/semantic_capability_invocation_lifecycle_runtime.py",
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


def _selection(tmp_path, *, available: bool = True) -> dict:
    objective = infer_platform_project_objective(
        request=(
            "Review and normalize a repository implementation change into canonical change evidence."
        ),
        development_intent={
            "requested_work_type": "ANALYSIS",
            "work_type": "ANALYSIS",
            "candidate_capability_discovery": {},
        },
        created_at=CREATED_AT,
    )
    registry = platform_capability_certification_registry()
    adapters = certified_capability_invocation_adapters()
    capture = select_semantic_capability(
        selection_id="SELECTION-G29-04",
        session_id="SESSION-G29-04",
        project_objective_artifact=objective,
        project_objective_reference="OBJECTIVE-G29-04",
        project_objective_hash=objective["artifact_hash"],
        certification_registry_state=registry,
        certification_registry_fingerprint=replay_hash(registry),
        invocation_adapter_metadata=adapters,
        invocation_adapter_metadata_fingerprint=replay_hash(adapters),
        available_input_artifact_types=(
            ["IMPLEMENTATION_MANIFEST_ARTIFACT_V1"] if available else []
        ),
        replay_dir=tmp_path / ("selection" if available else "selection-clarification"),
        created_at=CREATED_AT,
    )
    return capture["semantic_capability_selection_artifact"]


def _knowledge() -> dict:
    return query_platform_knowledge(
        query="Where is PLATFORM_CHANGE_NORMALIZATION implemented?",
        capability_identifier=PLATFORM_CHANGE_NORMALIZATION,
    )


def _inputs(manifest: dict) -> dict:
    return {
        "source_artifact": manifest,
        "source_reference": manifest["manifest_id"],
        "source_hash": manifest["artifact_hash"],
    }


def _run(tmp_path, *, selection=None, knowledge=None, inputs=None, name="lifecycle") -> dict:
    manifest = _manifest(tmp_path) if inputs is None else None
    return run_semantic_capability_invocation_lifecycle(
        invocation_id=f"INVOCATION-G29-04-{name}",
        session_id="SESSION-G29-04",
        semantic_selection_artifact=selection or _selection(tmp_path),
        platform_knowledge_response=_knowledge() if knowledge is None else knowledge,
        platform_knowledge_response_reference=f"KNOWLEDGE-G29-04-{name}",
        capability_inputs=_inputs(manifest) if inputs is None else inputs,
        invoked_by="PLATFORM_CORE",
        invoked_at=CREATED_AT,
        replay_dir=tmp_path / name,
    )


def test_valid_selection_reaches_g28_preserves_identifier_and_presents(tmp_path) -> None:
    capture = _run(tmp_path)
    result = capture["semantic_capability_invocation_lifecycle_result_artifact"]
    presentation = capture["canonical_platform_presentation"]

    assert capture["lifecycle_status"] == LIFECYCLE_COMPLETED
    assert capture["selected_capability_identifier"] == PLATFORM_CHANGE_NORMALIZATION
    assert capture["capability_invoked"] is True
    assert result["g28_invocation_result_reference"] == "INVOCATION-G29-04-lifecycle"
    assert presentation["artifact_type"] == CANONICAL_PLATFORM_PRESENTATION_ARTIFACT_V1
    assert presentation["presentation_status"] == PRESENTATION_READY
    assert presentation["answer"]["selected_capability_identifier"] == (
        PLATFORM_CHANGE_NORMALIZATION
    )
    assert validate_semantic_capability_invocation_lifecycle_result(result) == result


def test_lifecycle_replay_reconstructs_and_detects_tampering(tmp_path) -> None:
    capture = _run(tmp_path)
    replay_dir = tmp_path / "lifecycle"
    reconstructed = reconstruct_semantic_capability_invocation_lifecycle_replay(replay_dir)
    assert reconstructed["selected_capability_identifier"] == PLATFORM_CHANGE_NORMALIZATION
    assert reconstructed["replay_artifact_count"] == 5

    replay_file = replay_dir / "001_g28_invocation_request_recorded.json"
    wrapper = load_json(replay_file)
    wrapper["artifact"]["selected_capability_identifier"] = "SUBSTITUTED"
    replay_file.write_text(json.dumps(wrapper), encoding="utf-8")
    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_semantic_capability_invocation_lifecycle_replay(replay_dir)
    assert capture["repository_mutated"] is False


def test_selected_identifier_substitution_is_detected_in_reconstruction(tmp_path) -> None:
    _run(tmp_path)
    replay_dir = tmp_path / "lifecycle"
    replay_file = replay_dir / "001_g28_invocation_request_recorded.json"
    wrapper = load_json(replay_file)
    wrapper["artifact"]["selected_capability_identifier"] = "SUBSTITUTED"
    artifact = wrapper["artifact"]
    artifact.pop("artifact_hash")
    artifact["artifact_hash"] = replay_hash(artifact)
    wrapper.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper)
    replay_file.write_text(json.dumps(wrapper), encoding="utf-8")
    with pytest.raises(FailClosedRuntimeError, match="capability lineage mismatch"):
        reconstruct_semantic_capability_invocation_lifecycle_replay(replay_dir)


def test_clarification_and_no_candidate_states_never_reach_g28(tmp_path, monkeypatch) -> None:
    selection = _selection(tmp_path, available=False)
    invoked = False

    def forbidden(**kwargs):
        nonlocal invoked
        invoked = True
        raise AssertionError(kwargs)

    monkeypatch.setattr(lifecycle_runtime, "invoke_certified_capability", forbidden)
    capture = _run(
        tmp_path,
        selection=selection,
        knowledge={},
        inputs={},
        name="clarification",
    )
    assert capture["lifecycle_status"] == LIFECYCLE_CLARIFICATION_REQUIRED
    assert capture["clarification_required"] is True
    assert capture["capability_invoked"] is False
    assert invoked is False

    no_candidate = deepcopy(selection)
    no_candidate["selection_status"] = NO_ADMISSIBLE_CAPABILITY
    no_candidate.pop("artifact_hash")
    no_candidate["artifact_hash"] = replay_hash(no_candidate)
    capture = _run(
        tmp_path,
        selection=no_candidate,
        knowledge={},
        inputs={},
        name="no-candidate",
    )
    assert capture["lifecycle_status"] == LIFECYCLE_CLARIFICATION_REQUIRED
    assert capture["capability_invoked"] is False
    assert invoked is False


@pytest.mark.parametrize("mutation", ["malformed", "tampered"])
def test_malformed_or_tampered_g29_artifact_fails_closed(tmp_path, mutation: str) -> None:
    selection = _selection(tmp_path)
    if mutation == "malformed":
        selection = {"artifact_type": "WRONG"}
    else:
        selection["selected_capability_identifier"] = "SUBSTITUTED"
    capture = _run(tmp_path, selection=selection, name=mutation)
    assert capture["lifecycle_status"] == FAILED_CLOSED
    assert capture["capability_invoked"] is False


def test_missing_or_mismatched_platform_knowledge_fails_before_invocation(tmp_path) -> None:
    missing = _run(tmp_path, knowledge={}, name="missing-knowledge")
    mismatch_knowledge = query_platform_knowledge(
        query="Where is PLATFORM_CHANGE_IMPACT_ANALYSIS implemented?",
        capability_identifier="PLATFORM_CHANGE_IMPACT_ANALYSIS",
    )
    mismatch = _run(tmp_path, knowledge=mismatch_knowledge, name="mismatched-knowledge")
    assert missing["lifecycle_status"] == FAILED_CLOSED
    assert mismatch["lifecycle_status"] == FAILED_CLOSED
    assert missing["capability_invoked"] is False
    assert mismatch["capability_invoked"] is False


@pytest.mark.parametrize(
    ("name", "mutator"),
    [
        ("missing-field", lambda values: values.pop("source_hash")),
        ("extra-field", lambda values: values.update({"undeclared": True})),
        (
            "wrong-type",
            lambda values: values["source_artifact"].update({"artifact_type": "WRONG"}),
        ),
        ("reference-mismatch", lambda values: values.update({"source_reference": "WRONG"})),
        ("semantic-hash-mismatch", lambda values: values.update({"source_hash": _hash("wrong")})),
    ],
)
def test_concrete_input_failures_fail_closed(tmp_path, name, mutator) -> None:
    manifest = _manifest(tmp_path)
    values = _inputs(manifest)
    mutator(values)
    capture = _run(tmp_path, inputs=values, name=name)
    assert capture["lifecycle_status"] == FAILED_CLOSED
    assert capture["capability_invoked"] is False


@pytest.mark.parametrize("state", ["uncertified", "superseded"])
def test_current_certification_failure_remains_owned_by_g28(
    tmp_path, monkeypatch, state: str
) -> None:
    original = lookup_platform_capability_certification(PLATFORM_CHANGE_NORMALIZATION)
    changed = deepcopy(original)
    if state == "uncertified":
        changed["certification_status"] = "DRAFT"
    else:
        changed["superseded_by"] = "REPLACEMENT_CAPABILITY"
    changed.pop("certification_record_hash")
    changed["certification_record_hash"] = replay_hash(changed)
    monkeypatch.setattr(
        g28_runtime,
        "lookup_platform_capability_certification",
        lambda capability_id: deepcopy(changed),
    )
    capture = _run(tmp_path, name=state)
    assert capture["lifecycle_status"] == FAILED_CLOSED
    assert capture["canonical_platform_presentation"]["presentation_status"] == (
        PRESENTATION_FAILED_CLOSED
    )
    assert state in capture["failure_reason"]


def test_presentation_rejects_malformed_or_unsupported_invocation_result(tmp_path) -> None:
    capture = _run(tmp_path)
    result_record = load_json(
        tmp_path / "lifecycle" / "002_g28_invocation_result_recorded.json"
    )["artifact"]
    result = result_record["g28_invocation_result"]
    malformed = deepcopy(result)
    malformed["capability_identifier"] = "TAMPERED"
    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        present_platform_response(malformed)
    with pytest.raises(FailClosedRuntimeError, match="unsupported source artifact type"):
        present_platform_response({"artifact_type": "UNSUPPORTED"})
    assert capture["canonical_platform_presentation"]["presentation_status"] == PRESENTATION_READY


def test_authority_boundaries_and_static_implementation_surface(tmp_path) -> None:
    capture = _run(tmp_path)
    source = inspect.getsource(lifecycle_runtime)
    assert capture["worker_invoked"] is False
    assert capture["provider_invoked"] is False
    assert capture["repository_mutated"] is False
    assert capture["human_interface_authority"] is False
    assert capture["dynamic_import_used"] is False
    assert "importlib" not in source
    assert "__import__" not in source
    assert "implementation_owner" not in source


def test_lifecycle_capability_registration_is_governance_metadata_only() -> None:
    assert is_platform_capability_certified(CAPABILITY_ID) is True
    assert platform_capability_component_owner(CAPABILITY_ID).endswith(
        "semantic_capability_invocation_lifecycle_runtime"
    )
    record = lookup_platform_capability_certification(CAPABILITY_ID)
    assert record["certification_milestone"] == "G29-04"
    assert record["runtime_execution_authority"] is False
