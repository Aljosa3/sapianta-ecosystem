"""Tests for AIGOL_IMPLEMENTATION_SUMMARY_RUNTIME_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect

import pytest

from aigol.runtime.generated_content_validation_runtime import (
    _compute_validation_hash as _compute_content_validation_hash,
    validate_generated_content,
)
from aigol.runtime.generated_test_validation_runtime import (
    _compute_validation_hash as _compute_test_validation_hash,
    validate_generated_tests,
)
from aigol.runtime.implementation_manifest_runtime import CREATE_ONLY, create_implementation_manifest
from aigol.runtime.implementation_summary_runtime import (
    FAILED_CLOSED,
    IMPLEMENTATION_SUMMARY_ARTIFACT_V1,
    IMPLEMENTATION_SUMMARY_CREATED,
    create_implementation_summary,
    render_implementation_summary,
    verify_implementation_summary_artifact,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-06-05T16:00:00Z"


def _hash(label: str) -> str:
    return replay_hash({"ref": label})


def _files() -> list[dict]:
    return [
        {
            "file_entry_id": "FILE-RUNTIME-000001",
            "target_path": "aigol/runtime/summary_worker.py",
            "artifact_type": "PYTHON_RUNTIME_MODULE",
            "operation": CREATE_ONLY,
            "content": "def run():\n    return {'status': 'ok'}\n",
            "source_segment_reference": "PROVIDER-SEGMENT-RUNTIME",
            "validation_requirements": ["python -m pytest tests/test_summary_worker.py"],
        },
        {
            "file_entry_id": "FILE-GOVERNANCE-000001",
            "target_path": "governance/SUMMARY_WORKER_V1.md",
            "artifact_type": "GOVERNANCE_DOCUMENT_MARKDOWN",
            "operation": CREATE_ONLY,
            "content": "# SUMMARY_WORKER_V1\n\nStatus: generated candidate.\n",
            "source_segment_reference": "PROVIDER-SEGMENT-GOVERNANCE",
            "validation_requirements": ["git diff --check"],
        },
    ]


def _tests() -> list[dict]:
    return [
        {
            "test_entry_id": "TEST-RUNTIME-000001",
            "target_path": "tests/test_summary_worker.py",
            "artifact_type": "PYTEST_TEST",
            "operation": CREATE_ONLY,
            "content": (
                "from aigol.runtime.summary_worker import run\n\n\n"
                "def test_run():\n"
                "    assert run()['status'] == 'ok'\n"
            ),
            "tests_file_entries": ["FILE-RUNTIME-000001"],
            "validation_command": "python -m pytest tests/test_summary_worker.py",
            "expected_coverage_target": "aigol/runtime/summary_worker.py",
            "negative_case_requirement": "rejects missing status",
            "fixture_references": [],
        }
    ]


def _manifest(tmp_path, replay_name: str = "manifest") -> dict:
    capture = create_implementation_manifest(
        manifest_id="IMPLEMENTATION-MANIFEST-SUMMARY-000001",
        canonical_chain_id="CHAIN-IMPLEMENTATION-SUMMARY-000001",
        implementation_bundle_id="IMPLEMENTATION_SUMMARY_BUNDLE_V1",
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
        target_worker="SUMMARY_WORKER",
        generated_files=_files(),
        generated_tests=_tests(),
        validation_requirements=["python -m pytest tests/test_summary_worker.py", "git diff --check"],
        known_gaps=["human content acceptance not yet performed"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / replay_name,
    )
    return capture["implementation_manifest_artifact"]


def _validated_bundle(tmp_path, suffix: str = "bundle") -> tuple[dict, dict, dict]:
    manifest = _manifest(tmp_path, suffix)
    content = validate_generated_content(
        validation_id="GENERATED-CONTENT-VALIDATION-000001",
        implementation_manifest_artifact=manifest,
        created_at=CREATED_AT,
    )["generated_content_validation_artifact"]
    tests = validate_generated_tests(
        validation_id="GENERATED-TEST-VALIDATION-000001",
        implementation_manifest_artifact=manifest,
        generated_test_bundle=manifest["test_entries"],
        created_at=CREATED_AT,
    )["generated_test_validation_artifact"]
    return manifest, content, tests


def _summary(manifest: dict, content: dict, tests: dict) -> dict:
    return create_implementation_summary(
        summary_id="IMPLEMENTATION-SUMMARY-000001",
        implementation_manifest_artifact=manifest,
        generated_content_validation_artifact=content,
        generated_test_validation_artifact=tests,
        created_at=CREATED_AT,
    )


def _rebind_content_validation_artifact(artifact: dict) -> dict:
    artifact["generated_content_validation_hash"] = _compute_content_validation_hash(artifact)
    artifact["artifact_hash"] = replay_hash({key: value for key, value in artifact.items() if key != "artifact_hash"})
    return artifact


def _rebind_test_validation_artifact(artifact: dict) -> dict:
    artifact["generated_test_validation_hash"] = _compute_test_validation_hash(artifact)
    artifact["artifact_hash"] = replay_hash({key: value for key, value in artifact.items() if key != "artifact_hash"})
    return artifact


def test_implementation_summary_summarizes_candidate_without_authority(tmp_path) -> None:
    manifest, content, tests = _validated_bundle(tmp_path)
    capture = _summary(manifest, content, tests)
    artifact = capture["implementation_summary_artifact"]

    assert capture["summary_status"] == IMPLEMENTATION_SUMMARY_CREATED
    assert artifact["artifact_type"] == IMPLEMENTATION_SUMMARY_ARTIFACT_V1
    assert artifact["implementation_manifest_hash"] == manifest["implementation_manifest_hash"]
    assert artifact["generated_content_validation_hash"] == content["generated_content_validation_hash"]
    assert artifact["generated_test_validation_hash"] == tests["generated_test_validation_hash"]
    assert "IMPLEMENTATION_SUMMARY_BUNDLE_V1" in artifact["implementation_purpose"]
    assert len(artifact["implementation_files"]) == 2
    assert artifact["implementation_files"][0]["target_path"] == "aigol/runtime/summary_worker.py"
    assert artifact["generated_tests"][0]["target_path"] == "tests/test_summary_worker.py"
    assert artifact["validation_outcomes"][0] == "Generated content validation status: GENERATED_CONTENT_VALIDATED."
    assert artifact["known_gaps"] == ["human content acceptance not yet performed"]
    assert all(artifact["validation_checks"].values())
    assert capture["filesystem_mutated"] is False
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["approval_created"] is False
    assert capture["execution_authorized"] is False
    assert capture["automatic_acceptance_created"] is False
    assert all(value is False for value in artifact["authority_flags"].values())
    verify_implementation_summary_artifact(artifact)


def test_implementation_summary_renders_human_readable_review(tmp_path) -> None:
    rendered = render_implementation_summary(_summary(*_validated_bundle(tmp_path)))

    assert "Implementation Summary" in rendered
    assert "Planned Functionality" in rendered
    assert "aigol/runtime/summary_worker.py" in rendered
    assert "tests/test_summary_worker.py covers aigol/runtime/summary_worker.py" in rendered
    assert "Generated content validation status: GENERATED_CONTENT_VALIDATED." in rendered


def test_implementation_summary_is_deterministic_for_identical_lineage(tmp_path) -> None:
    first = _summary(*_validated_bundle(tmp_path, "first"))
    second = _summary(*_validated_bundle(tmp_path, "second"))

    assert first["implementation_summary_hash"] == second["implementation_summary_hash"]
    assert first["implementation_summary_artifact"] == second["implementation_summary_artifact"]


def test_implementation_summary_fails_closed_on_content_validation_mismatch(tmp_path) -> None:
    manifest, content, tests = _validated_bundle(tmp_path)
    content = deepcopy(content)
    content["canonical_chain_id"] = "OTHER-CHAIN"
    _rebind_content_validation_artifact(content)
    capture = _summary(manifest, content, tests)

    assert capture["summary_status"] == FAILED_CLOSED
    assert "content validation chain mismatch" in capture["failure_reason"]
    assert capture["approval_created"] is False


def test_implementation_summary_fails_closed_on_test_validation_mismatch(tmp_path) -> None:
    manifest, content, tests = _validated_bundle(tmp_path)
    tests = deepcopy(tests)
    tests["implementation_manifest_reference"] = "OTHER-MANIFEST"
    _rebind_test_validation_artifact(tests)
    capture = _summary(manifest, content, tests)

    assert capture["summary_status"] == FAILED_CLOSED
    assert "test validation manifest reference mismatch" in capture["failure_reason"]
    assert capture["automatic_acceptance_created"] is False


def test_implementation_summary_artifact_verifier_detects_tamper(tmp_path) -> None:
    artifact = _summary(*_validated_bundle(tmp_path))["implementation_summary_artifact"]
    artifact["planned_functionality"].append("Unauthorized extra line.")

    with pytest.raises(FailClosedRuntimeError, match="implementation summary hash mismatch"):
        verify_implementation_summary_artifact(artifact)


def test_implementation_summary_runtime_has_no_mutation_or_invocation_imports() -> None:
    import aigol.runtime.implementation_summary_runtime as module

    source = inspect.getsource(module)

    assert "open(" not in source
    assert ".write_text(" not in source
    assert "write_json_immutable" not in source
    assert "authorize_execution(" not in source
    assert "invoke_worker(" not in source
    assert "run_provider" not in source
    assert "produce_provider" not in source
    assert "accept_generated_content(" not in source
    assert "create_human_implementation_approval(" not in source
