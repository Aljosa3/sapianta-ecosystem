"""Tests for AIGOL_IMPLEMENTATION_MANIFEST_RUNTIME_V1."""

from __future__ import annotations

import inspect

import pytest

from aigol.runtime.implementation_manifest_runtime import (
    CREATE_ONLY,
    IMPLEMENTATION_MANIFEST_ARTIFACT_V1,
    IMPLEMENTATION_MANIFEST_CREATED,
    create_implementation_manifest,
    reconstruct_implementation_manifest_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


CREATED_AT = "2026-06-05T12:30:00Z"


def _hash(label: str) -> str:
    return replay_hash({"ref": label})


def _files() -> list[dict]:
    return [
        {
            "file_entry_id": "FILE-RUNTIME-000001",
            "target_path": "aigol/runtime/example_worker.py",
            "artifact_type": "PYTHON_RUNTIME_MODULE",
            "operation": CREATE_ONLY,
            "content": "def run():\n    return {'status': 'ok'}\n",
            "source_segment_reference": "PROVIDER-SEGMENT-RUNTIME",
            "validation_requirements": ["python -m pytest tests/test_example_worker.py"],
        },
        {
            "file_entry_id": "FILE-GOVERNANCE-000001",
            "target_path": "governance/EXAMPLE_WORKER_V1.md",
            "artifact_type": "GOVERNANCE_DOCUMENT_MARKDOWN",
            "operation": CREATE_ONLY,
            "content": "# EXAMPLE_WORKER_V1\n\nStatus: generated candidate.\n",
            "source_segment_reference": "PROVIDER-SEGMENT-GOVERNANCE",
            "validation_requirements": ["git diff --check"],
        },
    ]


def _tests() -> list[dict]:
    return [
        {
            "test_entry_id": "TEST-RUNTIME-000001",
            "target_path": "tests/test_example_worker.py",
            "artifact_type": "PYTEST_TEST",
            "operation": CREATE_ONLY,
            "content": "from aigol.runtime.example_worker import run\n\n\ndef test_run():\n    assert run()['status'] == 'ok'\n",
            "tests_file_entries": ["FILE-RUNTIME-000001"],
            "validation_command": "python -m pytest tests/test_example_worker.py",
            "expected_coverage_target": "aigol/runtime/example_worker.py",
            "negative_case_requirement": "rejects missing status",
            "fixture_references": [],
        }
    ]


def _manifest(tmp_path, replay_name: str = "manifest"):
    return create_implementation_manifest(
        manifest_id="IMPLEMENTATION-MANIFEST-000001",
        canonical_chain_id="CHAIN-IMPLEMENTATION-MANIFEST-000001",
        implementation_bundle_id="EXAMPLE_IMPLEMENTATION_BUNDLE_V1",
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
        target_worker="EXAMPLE_WORKER",
        generated_files=_files(),
        generated_tests=_tests(),
        validation_requirements=["python -m pytest tests/test_example_worker.py", "git diff --check"],
        known_gaps=["manual content acceptance not yet performed"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / replay_name,
    )


def test_implementation_manifest_creates_exact_reconstructable_manifest(tmp_path) -> None:
    capture = _manifest(tmp_path)
    reconstructed = reconstruct_implementation_manifest_replay(tmp_path / "manifest")
    artifact = capture["implementation_manifest_artifact"]

    assert artifact["artifact_type"] == IMPLEMENTATION_MANIFEST_ARTIFACT_V1
    assert capture["manifest_status"] == IMPLEMENTATION_MANIFEST_CREATED
    assert artifact["operation_mode"] == CREATE_ONLY
    assert artifact["implementation_bundle_id"] == "EXAMPLE_IMPLEMENTATION_BUNDLE_V1"
    assert artifact["file_count"] == 2
    assert artifact["test_count"] == 1
    assert [entry["target_path"] for entry in artifact["file_entries"]] == [
        "aigol/runtime/example_worker.py",
        "governance/EXAMPLE_WORKER_V1.md",
    ]
    assert artifact["file_entries"][0]["content_hash"] == replay_hash("def run():\n    return {'status': 'ok'}\n")
    assert artifact["test_entries"][0]["tests_file_entries"] == ["FILE-RUNTIME-000001"]
    assert artifact["filesystem_mutated"] is False
    assert artifact["provider_invoked"] is False
    assert artifact["worker_invoked"] is False
    assert artifact["approval_created"] is False
    assert all(value is False for value in artifact["authority_flags"].values())
    assert reconstructed["implementation_manifest_hash"] == capture["implementation_manifest_hash"]
    assert reconstructed["replay_artifact_count"] == 2


def test_implementation_manifest_is_deterministic_for_identical_bundles(tmp_path) -> None:
    first = _manifest(tmp_path, "first")
    second = _manifest(tmp_path, "second")

    assert first["implementation_manifest_hash"] == second["implementation_manifest_hash"]
    assert first["file_entries"] == second["file_entries"]
    assert first["test_entries"] == second["test_entries"]


def test_implementation_manifest_fails_closed_on_invalid_path(tmp_path) -> None:
    files = _files()
    files[0]["target_path"] = "../escape.py"
    capture = create_implementation_manifest(
        manifest_id="IMPLEMENTATION-MANIFEST-INVALID-PATH",
        canonical_chain_id="CHAIN-INVALID-PATH",
        implementation_bundle_id="BAD_BUNDLE",
        source_candidate_reference="CANDIDATE",
        source_candidate_hash=_hash("candidate"),
        implementation_handoff_reference="HANDOFF",
        implementation_handoff_hash=_hash("handoff"),
        provider_generation_authorization_reference="AUTH",
        provider_generation_authorization_hash=_hash("auth"),
        provider_response_reference="RESPONSE",
        provider_response_hash=_hash("response"),
        target_domain="TRADING",
        target_resource="WORKER",
        target_worker="BAD",
        generated_files=files,
        generated_tests=[],
        validation_requirements=["git diff --check"],
        known_gaps=[],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "invalid-path",
    )

    assert capture["fail_closed"] is True
    assert "invalid target path" in capture["failure_reason"]


def test_implementation_manifest_fails_closed_on_unknown_test_target(tmp_path) -> None:
    tests = _tests()
    tests[0]["tests_file_entries"] = ["UNKNOWN-FILE"]
    capture = create_implementation_manifest(
        manifest_id="IMPLEMENTATION-MANIFEST-BAD-TEST",
        canonical_chain_id="CHAIN-BAD-TEST",
        implementation_bundle_id="BAD_TEST_BUNDLE",
        source_candidate_reference="CANDIDATE",
        source_candidate_hash=_hash("candidate"),
        implementation_handoff_reference="HANDOFF",
        implementation_handoff_hash=_hash("handoff"),
        provider_generation_authorization_reference="AUTH",
        provider_generation_authorization_hash=_hash("auth"),
        provider_response_reference="RESPONSE",
        provider_response_hash=_hash("response"),
        target_domain="TRADING",
        target_resource="WORKER",
        target_worker="BAD",
        generated_files=_files(),
        generated_tests=tests,
        validation_requirements=["git diff --check"],
        known_gaps=[],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "bad-test",
    )

    assert capture["fail_closed"] is True
    assert "test references unknown file entry" in capture["failure_reason"]


def test_implementation_manifest_fails_closed_on_non_create_only_operation(tmp_path) -> None:
    files = _files()
    files[0]["operation"] = "UPDATE_ONLY"
    capture = create_implementation_manifest(
        manifest_id="IMPLEMENTATION-MANIFEST-BAD-OPERATION",
        canonical_chain_id="CHAIN-BAD-OPERATION",
        implementation_bundle_id="BAD_OPERATION_BUNDLE",
        source_candidate_reference="CANDIDATE",
        source_candidate_hash=_hash("candidate"),
        implementation_handoff_reference="HANDOFF",
        implementation_handoff_hash=_hash("handoff"),
        provider_generation_authorization_reference="AUTH",
        provider_generation_authorization_hash=_hash("auth"),
        provider_response_reference="RESPONSE",
        provider_response_hash=_hash("response"),
        target_domain="TRADING",
        target_resource="WORKER",
        target_worker="BAD",
        generated_files=files,
        generated_tests=[],
        validation_requirements=["git diff --check"],
        known_gaps=[],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "bad-operation",
    )

    assert capture["fail_closed"] is True
    assert "file operation must be CREATE_ONLY" in capture["failure_reason"]


def test_implementation_manifest_replay_fails_closed_on_tamper(tmp_path) -> None:
    _manifest(tmp_path, "tamper")
    wrapper_path = tmp_path / "tamper" / "000_implementation_manifest_recorded.json"
    wrapper = load_json(wrapper_path)
    wrapper["artifact"]["file_entries"][0]["content_hash"] = "sha256:tampered"
    wrapper_path.unlink()
    write_json_immutable(wrapper_path, wrapper)

    with pytest.raises(FailClosedRuntimeError, match="implementation manifest replay hash mismatch"):
        reconstruct_implementation_manifest_replay(tmp_path / "tamper")


def test_implementation_manifest_runtime_does_not_import_mutating_runtimes() -> None:
    import aigol.runtime.implementation_manifest_runtime as module

    source = inspect.getsource(module)

    assert "open(" not in source
    assert ".write_text(" not in source
    assert "authorize_execution(" not in source
    assert "invoke_worker(" not in source
    assert "run_provider" not in source
    assert "produce_provider" not in source
    assert "create_human_implementation_approval(" not in source
