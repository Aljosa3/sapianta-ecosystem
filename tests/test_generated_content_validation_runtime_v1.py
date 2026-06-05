"""Tests for AIGOL_GENERATED_CONTENT_VALIDATION_RUNTIME_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect

import pytest

from aigol.runtime.generated_content_validation_runtime import (
    FAILED_CLOSED,
    GENERATED_CONTENT_VALIDATED,
    GENERATED_CONTENT_VALIDATION_ARTIFACT_V1,
    _compute_manifest_hash,
    validate_generated_content,
    verify_generated_content_validation_artifact,
)
from aigol.runtime.implementation_manifest_runtime import CREATE_ONLY, create_implementation_manifest
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-06-05T13:00:00Z"


def _hash(label: str) -> str:
    return replay_hash({"ref": label})


def _files() -> list[dict]:
    return [
        {
            "file_entry_id": "FILE-RUNTIME-000001",
            "target_path": "aigol/runtime/generated_worker.py",
            "artifact_type": "PYTHON_RUNTIME_MODULE",
            "operation": CREATE_ONLY,
            "content": "def run():\n    return {'status': 'ok'}\n",
            "source_segment_reference": "PROVIDER-SEGMENT-RUNTIME",
            "validation_requirements": ["python -m pytest tests/test_generated_worker.py"],
        },
        {
            "file_entry_id": "FILE-GOVERNANCE-000001",
            "target_path": "governance/GENERATED_WORKER_V1.md",
            "artifact_type": "GOVERNANCE_DOCUMENT_MARKDOWN",
            "operation": CREATE_ONLY,
            "content": "# GENERATED_WORKER_V1\n\nStatus: generated candidate.\n",
            "source_segment_reference": "PROVIDER-SEGMENT-GOVERNANCE",
            "validation_requirements": ["git diff --check"],
        },
    ]


def _tests() -> list[dict]:
    return [
        {
            "test_entry_id": "TEST-RUNTIME-000001",
            "target_path": "tests/test_generated_worker.py",
            "artifact_type": "PYTEST_TEST",
            "operation": CREATE_ONLY,
            "content": "from aigol.runtime.generated_worker import run\n\n\ndef test_run():\n    assert run()['status'] == 'ok'\n",
            "tests_file_entries": ["FILE-RUNTIME-000001"],
            "validation_command": "python -m pytest tests/test_generated_worker.py",
            "expected_coverage_target": "aigol/runtime/generated_worker.py",
            "negative_case_requirement": "rejects missing status",
            "fixture_references": [],
        }
    ]


def _manifest(tmp_path, replay_name: str = "manifest") -> dict:
    capture = create_implementation_manifest(
        manifest_id="IMPLEMENTATION-MANIFEST-GENERATED-CONTENT-000001",
        canonical_chain_id="CHAIN-GENERATED-CONTENT-000001",
        implementation_bundle_id="GENERATED_CONTENT_BUNDLE_V1",
        source_candidate_reference="OCS-PPP-CANDIDATE-000001",
        source_candidate_hash=_hash("candidate"),
        implementation_handoff_reference="IMPLEMENTATION-HANDOFF-000001",
        implementation_handoff_hash=_hash("handoff"),
        provider_generation_authorization_reference="PROVIDER-GENERATION-AUTH-000001",
        provider_generation_authorization_hash=_hash("provider-auth"),
        provider_response_reference="PROVIDER-IMPLEMENTATION-RESPONSE-000001",
        provider_response_hash=_hash("provider-response"),
        target_domain="TRADING",
        target_resource="WORKER",
        target_worker="GENERATED_WORKER",
        generated_files=_files(),
        generated_tests=_tests(),
        validation_requirements=["python -m pytest tests/test_generated_worker.py", "git diff --check"],
        known_gaps=["manual content acceptance not yet performed"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / replay_name,
    )
    return capture["implementation_manifest_artifact"]


def _validate(manifest: dict) -> dict:
    return validate_generated_content(
        validation_id="GENERATED-CONTENT-VALIDATION-000001",
        implementation_manifest_artifact=manifest,
        created_at=CREATED_AT,
    )


def _rebind_manifest_hashes(manifest: dict) -> dict:
    manifest["implementation_manifest_hash"] = _compute_manifest_hash(manifest)
    manifest["artifact_hash"] = replay_hash({key: value for key, value in manifest.items() if key != "artifact_hash"})
    return manifest


def test_generated_content_validation_accepts_manifest_without_authority(tmp_path) -> None:
    capture = _validate(_manifest(tmp_path))
    artifact = capture["generated_content_validation_artifact"]

    assert capture["validation_status"] == GENERATED_CONTENT_VALIDATED
    assert artifact["artifact_type"] == GENERATED_CONTENT_VALIDATION_ARTIFACT_V1
    assert artifact["file_count"] == 2
    assert artifact["test_count"] == 1
    assert all(artifact["validation_checks"].values())
    assert artifact["file_validation_results"][0]["content_hash_valid"] is True
    assert artifact["test_validation_results"][0]["bundle_reference_valid"] is True
    assert capture["filesystem_mutated"] is False
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["approval_created"] is False
    assert capture["execution_authorized"] is False
    assert all(value is False for value in artifact["authority_flags"].values())
    verify_generated_content_validation_artifact(artifact)


def test_generated_content_validation_is_deterministic_for_identical_manifests(tmp_path) -> None:
    first = _validate(_manifest(tmp_path, "first"))
    second = _validate(_manifest(tmp_path, "second"))

    assert first["generated_content_validation_hash"] == second["generated_content_validation_hash"]
    assert first["generated_content_validation_artifact"] == second["generated_content_validation_artifact"]


def test_generated_content_validation_fails_closed_on_content_hash_mismatch(tmp_path) -> None:
    manifest = deepcopy(_manifest(tmp_path))
    manifest["file_entries"][0]["content_hash"] = "sha256:tampered"
    manifest["file_entries"][0]["file_entry_hash"] = replay_hash(
        {key: value for key, value in manifest["file_entries"][0].items() if key != "file_entry_hash"}
    )
    _rebind_manifest_hashes(manifest)
    capture = _validate(manifest)

    assert capture["validation_status"] == FAILED_CLOSED
    assert "file content hash mismatch" in capture["failure_reason"]
    assert capture["filesystem_mutated"] is False


def test_generated_content_validation_fails_closed_on_disallowed_path(tmp_path) -> None:
    manifest = deepcopy(_manifest(tmp_path))
    manifest["file_entries"][0]["target_path"] = "unknown/generated_worker.py"
    manifest["file_entries"][0]["file_entry_hash"] = replay_hash(
        {key: value for key, value in manifest["file_entries"][0].items() if key != "file_entry_hash"}
    )
    _rebind_manifest_hashes(manifest)
    capture = _validate(manifest)

    assert capture["validation_status"] == FAILED_CLOSED
    assert "target path is not allowed" in capture["failure_reason"]


def test_generated_content_validation_fails_closed_on_disallowed_artifact_type(tmp_path) -> None:
    manifest = deepcopy(_manifest(tmp_path))
    manifest["file_entries"][0]["artifact_type"] = "UNBOUNDED_SCRIPT"
    manifest["file_entries"][0]["file_entry_hash"] = replay_hash(
        {key: value for key, value in manifest["file_entries"][0].items() if key != "file_entry_hash"}
    )
    _rebind_manifest_hashes(manifest)
    capture = _validate(manifest)

    assert capture["validation_status"] == FAILED_CLOSED
    assert "artifact type is not allowed" in capture["failure_reason"]


def test_generated_content_validation_fails_closed_on_non_create_only(tmp_path) -> None:
    manifest = deepcopy(_manifest(tmp_path))
    manifest["operation_mode"] = "UPDATE_ONLY"
    manifest["artifact_hash"] = replay_hash({key: value for key, value in manifest.items() if key != "artifact_hash"})
    capture = _validate(manifest)

    assert capture["validation_status"] == FAILED_CLOSED
    assert "manifest must be CREATE_ONLY" in capture["failure_reason"]


def test_generated_content_validation_fails_closed_on_unknown_test_reference(tmp_path) -> None:
    manifest = deepcopy(_manifest(tmp_path))
    manifest["test_entries"][0]["tests_file_entries"] = ["UNKNOWN-FILE"]
    manifest["test_entries"][0]["test_entry_hash"] = replay_hash(
        {key: value for key, value in manifest["test_entries"][0].items() if key != "test_entry_hash"}
    )
    _rebind_manifest_hashes(manifest)
    capture = _validate(manifest)

    assert capture["validation_status"] == FAILED_CLOSED
    assert "test references unknown file entry" in capture["failure_reason"]


def test_generated_content_validation_artifact_verifier_detects_tamper(tmp_path) -> None:
    artifact = _validate(_manifest(tmp_path))["generated_content_validation_artifact"]
    artifact["validation_checks"]["allowed_paths_valid"] = False

    with pytest.raises(FailClosedRuntimeError, match="generated content validation hash mismatch"):
        verify_generated_content_validation_artifact(artifact)


def test_generated_content_validation_runtime_has_no_mutation_or_invocation_imports() -> None:
    import aigol.runtime.generated_content_validation_runtime as module

    source = inspect.getsource(module)

    assert "open(" not in source
    assert ".write_text(" not in source
    assert "write_json_immutable" not in source
    assert "authorize_execution(" not in source
    assert "invoke_worker(" not in source
    assert "run_provider" not in source
    assert "produce_provider" not in source
    assert "create_human_implementation_approval(" not in source
