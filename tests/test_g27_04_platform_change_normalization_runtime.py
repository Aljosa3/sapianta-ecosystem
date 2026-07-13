"""Tests for the bounded G27-04 Platform Change Normalization capability."""

from __future__ import annotations

from copy import deepcopy

import pytest

from aigol.runtime.governed_repository_mutation_runtime import create_governed_repository_mutation_proposal
from aigol.runtime.implementation_manifest_runtime import CREATE_ONLY, create_implementation_manifest
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_certification_registry import (
    is_platform_capability_certified,
    platform_capability_component_owner,
)
from aigol.runtime.platform_change_normalization_runtime import (
    CHANGE_NORMALIZED_WITH_UNRESOLVED_MAPPINGS,
    FAILED_CLOSED,
    NORMALIZED_CHANGE_ARTIFACT_V1,
    normalize_platform_change,
    reconstruct_platform_change_normalization_replay,
)
from aigol.runtime.transport.serialization import load_json, replay_hash


CREATED_AT = "2026-07-13T00:00:00Z"


def _hash(label: str) -> str:
    return replay_hash({"label": label})


def _manifest(tmp_path, name: str = "manifest") -> dict:
    capture = create_implementation_manifest(
        manifest_id="MANIFEST-G27-04-000001",
        canonical_chain_id="CHAIN-G27-04-000001",
        implementation_bundle_id="G27_04_CHANGE_NORMALIZATION",
        source_candidate_reference="CANDIDATE-G27-04",
        source_candidate_hash=_hash("candidate"),
        implementation_handoff_reference="HANDOFF-G27-04",
        implementation_handoff_hash=_hash("handoff"),
        provider_generation_authorization_reference="AUTH-G27-04",
        provider_generation_authorization_hash=_hash("authorization"),
        provider_response_reference="RESPONSE-G27-04",
        provider_response_hash=_hash("response"),
        target_domain="PLATFORM_CORE",
        target_resource="CHANGE_NORMALIZATION",
        target_worker=None,
        generated_files=[
            {
                "file_entry_id": "FILE-G27-04-000001",
                "target_path": "aigol/runtime/platform_change_normalization_runtime.py",
                "artifact_type": "python-runtime-module",
                "operation": CREATE_ONLY,
                "content": "VALUE = 1\n",
                "validation_requirements": [],
            }
        ],
        generated_tests=[],
        validation_requirements=["python -m pytest tests/test_g27_04_platform_change_normalization_runtime.py"],
        known_gaps=[],
        created_at=CREATED_AT,
        replay_dir=tmp_path / name,
    )
    return capture["implementation_manifest_artifact"]


def _proposal() -> dict:
    return create_governed_repository_mutation_proposal(
        proposal_id="PROPOSAL-G27-04-000001",
        original_request_reference="REQUEST-G27-04",
        resolved_intent_reference="INTENT-G27-04",
        file_mutations=[
            {
                "target_path": "aigol/runtime/existing_runtime.py",
                "operation": "REPLACE_CONTENT",
                "new_content": "VALUE = 2\n",
                "new_content_hash": replay_hash("VALUE = 2\n"),
                "approved": True,
            }
        ],
        validation_command=["git", "diff", "--check"],
        replay_references=["replay/request.json"],
        replay_hashes=[_hash("request")],
        created_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
    )


def _normalize(tmp_path, source: dict, reference: str, name: str = "normalized") -> dict:
    return normalize_platform_change(
        normalization_id="NORMALIZATION-G27-04-000001",
        source_artifact=source,
        source_reference=reference,
        source_hash=source["artifact_hash"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / name,
    )


def test_normalizes_implementation_manifest_and_reconstructs_replay(tmp_path) -> None:
    source = _manifest(tmp_path)
    capture = _normalize(tmp_path, source, source["manifest_id"])
    artifact = capture["normalized_change_artifact"]
    reconstructed = reconstruct_platform_change_normalization_replay(tmp_path / "normalized")

    assert artifact["artifact_type"] == NORMALIZED_CHANGE_ARTIFACT_V1
    assert artifact["normalization_status"] == CHANGE_NORMALIZED_WITH_UNRESOLVED_MAPPINGS
    assert artifact["source_hash"] == source["artifact_hash"]
    assert artifact["change_entry_count"] == 1
    assert artifact["change_entries"][0]["target_path"] == "aigol/runtime/platform_change_normalization_runtime.py"
    assert artifact["change_entries"][0]["operation_type"] == "CREATE"
    assert artifact["change_entries"][0]["artifact_type"] == "PYTHON_RUNTIME_MODULE"
    assert artifact["change_entries"][0]["before_hash"] is None
    assert artifact["change_entries"][0]["after_hash"] == replay_hash("VALUE = 1\n")
    assert artifact["unresolved_mappings"][0]["field"] == "before_hash"
    assert reconstructed["normalized_change_hash"] == artifact["normalized_change_hash"]
    assert reconstructed["replay_visible"] is True
    assert all(value is False for value in artifact["authority_flags"].values())


def test_normalizes_governed_mutation_proposal_without_inventing_artifact_detail(tmp_path) -> None:
    source = _proposal()
    capture = _normalize(tmp_path, source, source["proposal_id"])
    artifact = capture["normalized_change_artifact"]
    entry = artifact["change_entries"][0]

    assert capture["fail_closed"] is False
    assert entry["operation_type"] == "UPDATE"
    assert entry["artifact_type"] == "REPOSITORY_FILE"
    assert entry["after_hash"] == replay_hash("VALUE = 2\n")
    assert [item["field"] for item in entry["unresolved_mappings"]] == [
        "before_hash",
        "artifact_type_detail",
    ]
    assert artifact["impact_analysis_performed"] is False
    assert artifact["validation_planned"] is False
    assert artifact["validation_executed"] is False
    assert artifact["certification_performed"] is False
    assert artifact["provider_invoked"] is False
    assert artifact["worker_invoked"] is False


def test_normalization_is_deterministic_for_identical_source(tmp_path) -> None:
    source = _manifest(tmp_path)
    first = _normalize(tmp_path, source, source["manifest_id"], "first")
    second = _normalize(tmp_path, source, source["manifest_id"], "second")

    assert first["normalized_change_hash"] == second["normalized_change_hash"]
    assert first["change_entries"] == second["change_entries"]
    assert first["unresolved_mappings"] == second["unresolved_mappings"]


def test_unsupported_artifact_family_fails_closed_and_records_replay(tmp_path) -> None:
    source = {"artifact_type": "UNKNOWN_CHANGE_ARTIFACT_V1", "artifact_id": "UNKNOWN", "replay_visible": True}
    source["artifact_hash"] = replay_hash(source)

    capture = _normalize(tmp_path, source, "UNKNOWN")
    reconstructed = reconstruct_platform_change_normalization_replay(tmp_path / "normalized")

    assert capture["normalization_status"] == FAILED_CLOSED
    assert capture["change_entries"] == []
    assert "unsupported source artifact type" in capture["failure_reason"]
    assert reconstructed["fail_closed"] is True


def test_source_reference_and_hash_must_match(tmp_path) -> None:
    source = _manifest(tmp_path)
    mismatched_reference = normalize_platform_change(
        normalization_id="NORMALIZATION-BAD-REFERENCE",
        source_artifact=source,
        source_reference="OTHER-MANIFEST",
        source_hash=source["artifact_hash"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "bad-reference",
    )
    mismatched_hash = normalize_platform_change(
        normalization_id="NORMALIZATION-BAD-HASH",
        source_artifact=source,
        source_reference=source["manifest_id"],
        source_hash=_hash("other"),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "bad-hash",
    )

    assert mismatched_reference["fail_closed"] is True
    assert "source reference mismatch" in mismatched_reference["failure_reason"]
    assert mismatched_hash["fail_closed"] is True
    assert "source hash does not match" in mismatched_hash["failure_reason"]


def test_ambiguous_operation_and_invalid_path_fail_closed(tmp_path) -> None:
    source = _proposal()
    ambiguous = deepcopy(source)
    ambiguous["file_mutations"][0]["operation"] = "MAGIC_CHANGE"
    ambiguous.pop("artifact_hash")
    ambiguous["artifact_hash"] = replay_hash(ambiguous)
    invalid_path = deepcopy(source)
    invalid_path["file_mutations"][0]["target_path"] = "../escape.py"
    invalid_path["target_paths"] = ["../escape.py"]
    invalid_path.pop("artifact_hash")
    invalid_path["artifact_hash"] = replay_hash(invalid_path)

    ambiguous_capture = _normalize(tmp_path, ambiguous, ambiguous["proposal_id"], "ambiguous")
    invalid_path_capture = _normalize(tmp_path, invalid_path, invalid_path["proposal_id"], "invalid-path")

    assert ambiguous_capture["fail_closed"] is True
    assert "unsupported operation type" in ambiguous_capture["failure_reason"]
    assert invalid_path_capture["fail_closed"] is True
    assert "invalid repository-relative path" in invalid_path_capture["failure_reason"]


def test_reconstruction_detects_tampered_normalized_artifact(tmp_path) -> None:
    source = _manifest(tmp_path)
    _normalize(tmp_path, source, source["manifest_id"])
    path = tmp_path / "normalized" / "000_normalized_change_recorded.json"
    wrapper = load_json(path)
    wrapper["artifact"]["change_entries"][0]["operation_type"] = "DELETE"
    path.write_text(str(wrapper), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError):
        reconstruct_platform_change_normalization_replay(tmp_path / "normalized")


def test_change_normalization_is_registered_as_platform_core_metadata() -> None:
    assert is_platform_capability_certified("PLATFORM_CHANGE_NORMALIZATION") is True
    assert (
        platform_capability_component_owner("PLATFORM_CHANGE_NORMALIZATION")
        == "aigol.runtime.platform_change_normalization_runtime"
    )
