"""Tests for AIGOL_IMPLEMENTATION_CERTIFICATION_RUNTIME_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect

import pytest

from aigol.runtime.filesystem_mutation_authorization_runtime import (
    AUTHORIZATION_DECISION,
    AUTHORIZATION_SCOPE,
    AUTHORIZATION_STATEMENT,
    authorize_filesystem_mutation,
)
from aigol.runtime.filesystem_mutation_runtime import (
    _compute_mutation_hash,
    apply_filesystem_mutation,
)
from aigol.runtime.generated_content_acceptance_runtime import (
    ACCEPTANCE_DECISION,
    ACCEPTANCE_SCOPE,
    ACCEPTANCE_STATEMENT,
    accept_generated_content,
)
from aigol.runtime.generated_content_validation_runtime import validate_generated_content
from aigol.runtime.generated_test_validation_runtime import validate_generated_tests
from aigol.runtime.implementation_certification_runtime import (
    FAILED_CLOSED,
    IMPLEMENTATION_CERTIFICATION_ARTIFACT_V1,
    IMPLEMENTATION_CERTIFIED,
    certify_implementation,
    verify_implementation_certification_artifact,
)
from aigol.runtime.implementation_manifest_runtime import CREATE_ONLY, create_implementation_manifest
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-06-05T19:00:00Z"


def _hash(label: str) -> str:
    return replay_hash({"ref": label})


def _files() -> list[dict]:
    return [
        {
            "file_entry_id": "FILE-RUNTIME-000001",
            "target_path": "aigol/runtime/certified_worker.py",
            "artifact_type": "PYTHON_RUNTIME_MODULE",
            "operation": CREATE_ONLY,
            "content": "def run():\n    return {'status': 'certified'}\n",
            "source_segment_reference": "PROVIDER-SEGMENT-RUNTIME",
            "validation_requirements": ["python -m pytest tests/test_certified_worker.py"],
        },
        {
            "file_entry_id": "FILE-GOVERNANCE-000001",
            "target_path": "governance/CERTIFIED_WORKER_V1.md",
            "artifact_type": "GOVERNANCE_DOCUMENT_MARKDOWN",
            "operation": CREATE_ONLY,
            "content": "# CERTIFIED_WORKER_V1\n\nStatus: generated candidate.\n",
            "source_segment_reference": "PROVIDER-SEGMENT-GOVERNANCE",
            "validation_requirements": ["git diff --check"],
        },
    ]


def _tests() -> list[dict]:
    return [
        {
            "test_entry_id": "TEST-RUNTIME-000001",
            "target_path": "tests/test_certified_worker.py",
            "artifact_type": "PYTEST_TEST",
            "operation": CREATE_ONLY,
            "content": (
                "from aigol.runtime.certified_worker import run\n\n\n"
                "def test_run():\n"
                "    assert run()['status'] == 'certified'\n"
            ),
            "tests_file_entries": ["FILE-RUNTIME-000001"],
            "validation_command": "python -m pytest tests/test_certified_worker.py",
            "expected_coverage_target": "aigol/runtime/certified_worker.py",
            "negative_case_requirement": "rejects missing status",
            "fixture_references": [],
        }
    ]


def _manifest(tmp_path, replay_name: str = "manifest") -> dict:
    capture = create_implementation_manifest(
        manifest_id="IMPLEMENTATION-MANIFEST-CERTIFICATION-000001",
        canonical_chain_id="CHAIN-CERTIFICATION-000001",
        implementation_bundle_id="IMPLEMENTATION_CERTIFICATION_BUNDLE_V1",
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
        target_worker="CERTIFIED_WORKER",
        generated_files=_files(),
        generated_tests=_tests(),
        validation_requirements=["python -m pytest tests/test_certified_worker.py", "git diff --check"],
        known_gaps=["post-certification execution is not authorized"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / replay_name,
    )
    return capture["implementation_manifest_artifact"]


def _acceptance_human() -> dict:
    return {
        "actor_id": "human.operator",
        "decision": ACCEPTANCE_DECISION,
        "accepted_at": CREATED_AT,
        "acceptance_scope": ACCEPTANCE_SCOPE,
        "acceptance_statement": ACCEPTANCE_STATEMENT,
    }


def _authorization_human() -> dict:
    return {
        "actor_id": "human.operator",
        "decision": AUTHORIZATION_DECISION,
        "authorized_at": CREATED_AT,
        "authorization_scope": AUTHORIZATION_SCOPE,
        "authorization_statement": AUTHORIZATION_STATEMENT,
    }


def _implementation_bundle(tmp_path, suffix: str = "bundle") -> tuple[dict, dict, dict, dict]:
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
    acceptance = accept_generated_content(
        acceptance_id="GENERATED-CONTENT-ACCEPTANCE-000001",
        implementation_manifest_artifact=manifest,
        generated_content_validation_artifact=content,
        generated_test_validation_artifact=tests,
        human_acceptance_evidence=_acceptance_human(),
        created_at=CREATED_AT,
    )["generated_content_acceptance_artifact"]
    authorization = authorize_filesystem_mutation(
        authorization_id="FILESYSTEM-MUTATION-AUTHORIZATION-000001",
        implementation_manifest_artifact=manifest,
        generated_content_validation_artifact=content,
        generated_test_validation_artifact=tests,
        generated_content_acceptance_artifact=acceptance,
        human_authorization_evidence=_authorization_human(),
        created_at=CREATED_AT,
    )["filesystem_mutation_authorization_artifact"]
    mutation = apply_filesystem_mutation(
        mutation_id="FILESYSTEM-MUTATION-000001",
        implementation_manifest_artifact=manifest,
        filesystem_mutation_authorization_artifact=authorization,
        target_root=tmp_path / f"{suffix}_workspace",
        created_at=CREATED_AT,
    )["filesystem_mutation_artifact"]
    return manifest, acceptance, authorization, mutation


def _certify(manifest: dict, acceptance: dict, authorization: dict, mutation: dict) -> dict:
    return certify_implementation(
        certification_id="IMPLEMENTATION-CERTIFICATION-000001",
        implementation_manifest_artifact=manifest,
        filesystem_mutation_authorization_artifact=authorization,
        generated_content_acceptance_artifact=acceptance,
        filesystem_mutation_artifact=mutation,
        created_at=CREATED_AT,
    )


def _rebind_mutation_artifact(artifact: dict) -> dict:
    artifact["filesystem_mutation_hash"] = _compute_mutation_hash(artifact)
    artifact["artifact_hash"] = replay_hash({key: value for key, value in artifact.items() if key != "artifact_hash"})
    return artifact


def test_implementation_certification_binds_manifest_acceptance_authorization_and_mutation(tmp_path) -> None:
    manifest, acceptance, authorization, mutation = _implementation_bundle(tmp_path)
    capture = _certify(manifest, acceptance, authorization, mutation)
    artifact = capture["implementation_certification_artifact"]

    assert capture["certification_status"] == IMPLEMENTATION_CERTIFIED
    assert artifact["artifact_type"] == IMPLEMENTATION_CERTIFICATION_ARTIFACT_V1
    assert artifact["implementation_manifest_hash"] == manifest["implementation_manifest_hash"]
    assert artifact["generated_content_acceptance_hash"] == acceptance["generated_content_acceptance_hash"]
    assert artifact["filesystem_mutation_authorization_hash"] == authorization[
        "filesystem_mutation_authorization_hash"
    ]
    assert artifact["filesystem_mutation_hash"] == mutation["filesystem_mutation_hash"]
    assert artifact["certified_path_count"] == 3
    assert [entry["target_path"] for entry in artifact["certified_paths"]] == [
        "aigol/runtime/certified_worker.py",
        "governance/CERTIFIED_WORKER_V1.md",
        "tests/test_certified_worker.py",
    ]
    assert all(entry["operation"] == CREATE_ONLY for entry in artifact["certified_paths"])
    assert all(entry["content_hash"] == entry["materialized_content_hash"] for entry in artifact["certified_paths"])
    assert artifact["filesystem_mutated"] is False
    assert artifact["provider_invoked"] is False
    assert artifact["worker_invoked"] is False
    assert artifact["execution_authorized"] is False
    assert artifact["governance_mutated"] is False
    verify_implementation_certification_artifact(artifact)


def test_implementation_certification_is_deterministic_for_identical_bundles(tmp_path) -> None:
    first = _certify(*_implementation_bundle(tmp_path, "first"))
    second = _certify(*_implementation_bundle(tmp_path, "second"))

    assert first["implementation_certification_hash"] == second["implementation_certification_hash"]
    assert first["implementation_certification_artifact"] == second["implementation_certification_artifact"]


def test_implementation_certification_fails_closed_on_authorization_lineage_mismatch(tmp_path) -> None:
    manifest, acceptance, authorization, mutation = _implementation_bundle(tmp_path)
    mutation = deepcopy(mutation)
    mutation["filesystem_mutation_authorization_hash"] = "sha256:mismatched"
    _rebind_mutation_artifact(mutation)
    capture = _certify(manifest, acceptance, authorization, mutation)

    assert capture["certification_status"] == FAILED_CLOSED
    assert "mutation authorization hash mismatch" in capture["failure_reason"]
    assert capture["filesystem_mutated"] is False


def test_implementation_certification_fails_closed_on_materialization_path_mismatch(tmp_path) -> None:
    manifest, acceptance, authorization, mutation = _implementation_bundle(tmp_path)
    mutation = deepcopy(mutation)
    mutation["mutation_results"][0]["target_path"] = "aigol/runtime/unexpected.py"
    _rebind_mutation_artifact(mutation)
    capture = _certify(manifest, acceptance, authorization, mutation)

    assert capture["certification_status"] == FAILED_CLOSED
    assert "materialization path continuity mismatch" in capture["failure_reason"]


def test_implementation_certification_fails_closed_on_materialized_hash_mismatch(tmp_path) -> None:
    manifest, acceptance, authorization, mutation = _implementation_bundle(tmp_path)
    mutation = deepcopy(mutation)
    mutation["mutation_results"][0]["materialized_content_hash"] = "sha256:mismatched"
    _rebind_mutation_artifact(mutation)
    capture = _certify(manifest, acceptance, authorization, mutation)

    assert capture["certification_status"] == FAILED_CLOSED
    assert "materialized content hash mismatch" in capture["failure_reason"]


def test_implementation_certification_artifact_verifier_detects_tamper(tmp_path) -> None:
    artifact = _certify(*_implementation_bundle(tmp_path))["implementation_certification_artifact"]
    artifact["certified_paths"][0]["operation"] = "UPDATE_ONLY"

    with pytest.raises(FailClosedRuntimeError, match="implementation certification hash mismatch"):
        verify_implementation_certification_artifact(artifact)


def test_implementation_certification_runtime_does_not_perform_forbidden_operations() -> None:
    import aigol.runtime.implementation_certification_runtime as module

    source = inspect.getsource(module)

    assert ".open(" not in source
    assert ".write_text(" not in source
    assert ".unlink(" not in source
    assert ".rename(" not in source
    assert ".replace(" not in source
    assert "invoke_worker(" not in source
    assert "run_provider" not in source
    assert "produce_provider" not in source
