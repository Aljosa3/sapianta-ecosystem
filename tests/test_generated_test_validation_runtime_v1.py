"""Tests for AIGOL_GENERATED_TEST_VALIDATION_RUNTIME_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect

import pytest

from aigol.runtime.generated_test_validation_runtime import (
    FAILED_CLOSED,
    GENERATED_TEST_VALIDATED,
    GENERATED_TEST_VALIDATION_ARTIFACT_V1,
    _compute_manifest_hash,
    validate_generated_tests,
    verify_generated_test_validation_artifact,
)
from aigol.runtime.implementation_manifest_runtime import CREATE_ONLY, create_implementation_manifest
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-06-05T14:00:00Z"


def _hash(label: str) -> str:
    return replay_hash({"ref": label})


def _files() -> list[dict]:
    return [
        {
            "file_entry_id": "FILE-RUNTIME-000001",
            "target_path": "aigol/runtime/test_validated_worker.py",
            "artifact_type": "PYTHON_RUNTIME_MODULE",
            "operation": CREATE_ONLY,
            "content": "def run():\n    return {'status': 'ok'}\n",
            "source_segment_reference": "PROVIDER-SEGMENT-RUNTIME",
            "validation_requirements": ["python -m pytest tests/test_test_validated_worker.py"],
        }
    ]


def _tests() -> list[dict]:
    return [
        {
            "test_entry_id": "TEST-RUNTIME-000001",
            "target_path": "tests/test_test_validated_worker.py",
            "artifact_type": "PYTEST_TEST",
            "operation": CREATE_ONLY,
            "content": (
                "from aigol.runtime.test_validated_worker import run\n\n\n"
                "def test_run():\n"
                "    assert run()['status'] == 'ok'\n"
            ),
            "tests_file_entries": ["FILE-RUNTIME-000001"],
            "validation_command": "python -m pytest tests/test_test_validated_worker.py",
            "expected_coverage_target": "aigol/runtime/test_validated_worker.py",
            "negative_case_requirement": "rejects missing status",
            "fixture_references": [],
        }
    ]


def _manifest(tmp_path, replay_name: str = "manifest", *, generated_tests: list[dict] | None = None) -> dict:
    capture = create_implementation_manifest(
        manifest_id="IMPLEMENTATION-MANIFEST-GENERATED-TEST-000001",
        canonical_chain_id="CHAIN-GENERATED-TEST-000001",
        implementation_bundle_id="GENERATED_TEST_BUNDLE_V1",
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
        target_worker="TEST_VALIDATED_WORKER",
        generated_files=_files(),
        generated_tests=_tests() if generated_tests is None else generated_tests,
        validation_requirements=["python -m pytest tests/test_test_validated_worker.py", "git diff --check"],
        known_gaps=["manual test acceptance not yet performed"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / replay_name,
    )
    return capture["implementation_manifest_artifact"]


def _validate(manifest: dict, bundle: list[dict] | None = None) -> dict:
    return validate_generated_tests(
        validation_id="GENERATED-TEST-VALIDATION-000001",
        implementation_manifest_artifact=manifest,
        generated_test_bundle=deepcopy(manifest["test_entries"] if bundle is None else bundle),
        created_at=CREATED_AT,
    )


def _rebind_manifest_hashes(manifest: dict) -> dict:
    manifest["implementation_manifest_hash"] = _compute_manifest_hash(manifest)
    manifest["artifact_hash"] = replay_hash({key: value for key, value in manifest.items() if key != "artifact_hash"})
    return manifest


def _rebind_test_entry(test_entry: dict) -> dict:
    test_entry["test_entry_hash"] = replay_hash(
        {key: value for key, value in test_entry.items() if key != "test_entry_hash"}
    )
    return test_entry


def test_generated_test_validation_accepts_manifest_test_bundle_without_authority(tmp_path) -> None:
    capture = _validate(_manifest(tmp_path))
    artifact = capture["generated_test_validation_artifact"]

    assert capture["validation_status"] == GENERATED_TEST_VALIDATED
    assert artifact["artifact_type"] == GENERATED_TEST_VALIDATION_ARTIFACT_V1
    assert artifact["test_count"] == 1
    assert all(artifact["validation_checks"].values())
    assert artifact["test_validation_results"][0]["test_artifact_present"] is True
    assert artifact["test_validation_results"][0]["test_hash_valid"] is True
    assert artifact["test_validation_results"][0]["implementation_to_test_linkage_valid"] is True
    assert artifact["test_validation_results"][0]["linked_implementation_targets"] == [
        "aigol/runtime/test_validated_worker.py"
    ]
    assert capture["filesystem_mutated"] is False
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["approval_created"] is False
    assert capture["execution_authorized"] is False
    assert all(value is False for value in artifact["authority_flags"].values())
    verify_generated_test_validation_artifact(artifact)


def test_generated_test_validation_is_deterministic_for_identical_manifests_and_bundles(tmp_path) -> None:
    first_manifest = _manifest(tmp_path, "first")
    second_manifest = _manifest(tmp_path, "second")
    first = _validate(first_manifest)
    second = _validate(second_manifest)

    assert first["generated_test_validation_hash"] == second["generated_test_validation_hash"]
    assert first["generated_test_validation_artifact"] == second["generated_test_validation_artifact"]


def test_generated_test_validation_fails_closed_without_test_artifacts(tmp_path) -> None:
    manifest = _manifest(tmp_path, "no-tests", generated_tests=[])
    capture = _validate(manifest, [])

    assert capture["validation_status"] == FAILED_CLOSED
    assert "test artifacts are required" in capture["failure_reason"]
    assert capture["filesystem_mutated"] is False


def test_generated_test_validation_fails_closed_on_test_hash_mismatch(tmp_path) -> None:
    manifest = deepcopy(_manifest(tmp_path))
    manifest["test_entries"][0]["content_hash"] = "sha256:tampered"
    _rebind_test_entry(manifest["test_entries"][0])
    _rebind_manifest_hashes(manifest)
    capture = _validate(manifest)

    assert capture["validation_status"] == FAILED_CLOSED
    assert "test content hash mismatch" in capture["failure_reason"]


def test_generated_test_validation_fails_closed_on_test_path(tmp_path) -> None:
    manifest = deepcopy(_manifest(tmp_path))
    manifest["test_entries"][0]["target_path"] = "governance/not_a_test.py"
    _rebind_test_entry(manifest["test_entries"][0])
    _rebind_manifest_hashes(manifest)
    capture = _validate(manifest)

    assert capture["validation_status"] == FAILED_CLOSED
    assert "test path is not allowed" in capture["failure_reason"]


def test_generated_test_validation_fails_closed_on_test_artifact_type(tmp_path) -> None:
    manifest = deepcopy(_manifest(tmp_path))
    manifest["test_entries"][0]["artifact_type"] = "GOVERNANCE_DOCUMENT_MARKDOWN"
    _rebind_test_entry(manifest["test_entries"][0])
    _rebind_manifest_hashes(manifest)
    capture = _validate(manifest)

    assert capture["validation_status"] == FAILED_CLOSED
    assert "test artifact type is not allowed" in capture["failure_reason"]


def test_generated_test_validation_fails_closed_on_manifest_to_test_mismatch(tmp_path) -> None:
    manifest = _manifest(tmp_path)
    bundle = deepcopy(manifest["test_entries"])
    bundle[0]["test_entry_id"] = "TEST-RUNTIME-DIFFERENT"
    capture = _validate(manifest, bundle)

    assert capture["validation_status"] == FAILED_CLOSED
    assert "manifest-to-test consistency mismatch" in capture["failure_reason"]


def test_generated_test_validation_fails_closed_on_implementation_linkage_mismatch(tmp_path) -> None:
    manifest = deepcopy(_manifest(tmp_path))
    manifest["test_entries"][0]["expected_coverage_target"] = "aigol/runtime/unlinked_worker.py"
    _rebind_test_entry(manifest["test_entries"][0])
    _rebind_manifest_hashes(manifest)
    capture = _validate(manifest)

    assert capture["validation_status"] == FAILED_CLOSED
    assert "expected coverage target is not linked" in capture["failure_reason"]


def test_generated_test_validation_artifact_verifier_detects_tamper(tmp_path) -> None:
    artifact = _validate(_manifest(tmp_path))["generated_test_validation_artifact"]
    artifact["validation_checks"]["test_artifact_paths_valid"] = False

    with pytest.raises(FailClosedRuntimeError, match="generated test validation hash mismatch"):
        verify_generated_test_validation_artifact(artifact)


def test_generated_test_validation_runtime_has_no_mutation_or_invocation_imports() -> None:
    import aigol.runtime.generated_test_validation_runtime as module

    source = inspect.getsource(module)

    assert "open(" not in source
    assert ".write_text(" not in source
    assert "write_json_immutable" not in source
    assert "authorize_execution(" not in source
    assert "invoke_worker(" not in source
    assert "run_provider" not in source
    assert "produce_provider" not in source
    assert "create_human_implementation_approval(" not in source
