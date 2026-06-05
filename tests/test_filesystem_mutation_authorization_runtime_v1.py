"""Tests for AIGOL_FILESYSTEM_MUTATION_AUTHORIZATION_RUNTIME_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect

import pytest

from aigol.runtime.filesystem_mutation_authorization_runtime import (
    AUTHORIZATION_DECISION,
    AUTHORIZATION_SCOPE,
    AUTHORIZATION_STATEMENT,
    FAILED_CLOSED,
    FILESYSTEM_MUTATION_AUTHORIZATION_ARTIFACT_V1,
    FILESYSTEM_MUTATION_AUTHORIZED,
    authorize_filesystem_mutation,
    verify_filesystem_mutation_authorization_artifact,
)
from aigol.runtime.generated_content_acceptance_runtime import (
    ACCEPTANCE_DECISION,
    ACCEPTANCE_SCOPE,
    ACCEPTANCE_STATEMENT,
    _compute_acceptance_hash,
    accept_generated_content,
)
from aigol.runtime.generated_content_validation_runtime import (
    _compute_validation_hash as _compute_content_validation_hash,
    validate_generated_content,
)
from aigol.runtime.generated_test_validation_runtime import (
    _compute_validation_hash as _compute_test_validation_hash,
    validate_generated_tests,
)
from aigol.runtime.implementation_manifest_runtime import CREATE_ONLY, create_implementation_manifest
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-06-05T17:00:00Z"


def _hash(label: str) -> str:
    return replay_hash({"ref": label})


def _files() -> list[dict]:
    return [
        {
            "file_entry_id": "FILE-RUNTIME-000001",
            "target_path": "aigol/runtime/authorized_worker.py",
            "artifact_type": "PYTHON_RUNTIME_MODULE",
            "operation": CREATE_ONLY,
            "content": "def run():\n    return {'status': 'ok'}\n",
            "source_segment_reference": "PROVIDER-SEGMENT-RUNTIME",
            "validation_requirements": ["python -m pytest tests/test_authorized_worker.py"],
        },
        {
            "file_entry_id": "FILE-GOVERNANCE-000001",
            "target_path": "governance/AUTHORIZED_WORKER_V1.md",
            "artifact_type": "GOVERNANCE_DOCUMENT_MARKDOWN",
            "operation": CREATE_ONLY,
            "content": "# AUTHORIZED_WORKER_V1\n\nStatus: generated candidate.\n",
            "source_segment_reference": "PROVIDER-SEGMENT-GOVERNANCE",
            "validation_requirements": ["git diff --check"],
        },
    ]


def _tests() -> list[dict]:
    return [
        {
            "test_entry_id": "TEST-RUNTIME-000001",
            "target_path": "tests/test_authorized_worker.py",
            "artifact_type": "PYTEST_TEST",
            "operation": CREATE_ONLY,
            "content": (
                "from aigol.runtime.authorized_worker import run\n\n\n"
                "def test_run():\n"
                "    assert run()['status'] == 'ok'\n"
            ),
            "tests_file_entries": ["FILE-RUNTIME-000001"],
            "validation_command": "python -m pytest tests/test_authorized_worker.py",
            "expected_coverage_target": "aigol/runtime/authorized_worker.py",
            "negative_case_requirement": "rejects missing status",
            "fixture_references": [],
        }
    ]


def _manifest(tmp_path, replay_name: str = "manifest") -> dict:
    capture = create_implementation_manifest(
        manifest_id="IMPLEMENTATION-MANIFEST-FILESYSTEM-AUTH-000001",
        canonical_chain_id="CHAIN-FILESYSTEM-AUTH-000001",
        implementation_bundle_id="FILESYSTEM_AUTHORIZATION_BUNDLE_V1",
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
        target_worker="AUTHORIZED_WORKER",
        generated_files=_files(),
        generated_tests=_tests(),
        validation_requirements=["python -m pytest tests/test_authorized_worker.py", "git diff --check"],
        known_gaps=["filesystem mutation has not been performed"],
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


def _validated_and_accepted_bundle(tmp_path, suffix: str = "bundle") -> tuple[dict, dict, dict, dict]:
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
    return manifest, content, tests, acceptance


def _authorize(
    manifest: dict,
    content: dict,
    tests: dict,
    acceptance: dict,
    *,
    human: dict | None = None,
    prior: list[str] | None = None,
) -> dict:
    return authorize_filesystem_mutation(
        authorization_id="FILESYSTEM-MUTATION-AUTHORIZATION-000001",
        implementation_manifest_artifact=manifest,
        generated_content_validation_artifact=content,
        generated_test_validation_artifact=tests,
        generated_content_acceptance_artifact=acceptance,
        human_authorization_evidence=_authorization_human() if human is None else human,
        created_at=CREATED_AT,
        prior_authorization_lineage_keys=prior,
    )


def _rebind_content_validation_artifact(artifact: dict) -> dict:
    artifact["generated_content_validation_hash"] = _compute_content_validation_hash(artifact)
    artifact["artifact_hash"] = replay_hash({key: value for key, value in artifact.items() if key != "artifact_hash"})
    return artifact


def _rebind_test_validation_artifact(artifact: dict) -> dict:
    artifact["generated_test_validation_hash"] = _compute_test_validation_hash(artifact)
    artifact["artifact_hash"] = replay_hash({key: value for key, value in artifact.items() if key != "artifact_hash"})
    return artifact


def _rebind_acceptance_artifact(artifact: dict) -> dict:
    artifact["generated_content_acceptance_hash"] = _compute_acceptance_hash(artifact)
    artifact["artifact_hash"] = replay_hash({key: value for key, value in artifact.items() if key != "artifact_hash"})
    return artifact


def test_filesystem_mutation_authorization_binds_exact_create_only_permissions(tmp_path) -> None:
    manifest, content, tests, acceptance = _validated_and_accepted_bundle(tmp_path)
    capture = _authorize(manifest, content, tests, acceptance)
    artifact = capture["filesystem_mutation_authorization_artifact"]

    assert capture["authorization_status"] == FILESYSTEM_MUTATION_AUTHORIZED
    assert artifact["artifact_type"] == FILESYSTEM_MUTATION_AUTHORIZATION_ARTIFACT_V1
    assert artifact["implementation_manifest_hash"] == manifest["implementation_manifest_hash"]
    assert artifact["generated_content_validation_hash"] == content["generated_content_validation_hash"]
    assert artifact["generated_test_validation_hash"] == tests["generated_test_validation_hash"]
    assert artifact["generated_content_acceptance_hash"] == acceptance["generated_content_acceptance_hash"]
    assert artifact["authorized_permission_count"] == 3
    assert [entry["target_path"] for entry in artifact["authorized_permissions"]] == [
        "aigol/runtime/authorized_worker.py",
        "governance/AUTHORIZED_WORKER_V1.md",
        "tests/test_authorized_worker.py",
    ]
    assert all(entry["operation"] == CREATE_ONLY for entry in artifact["authorized_permissions"])
    assert all(entry["content_hash"].startswith("sha256:") for entry in artifact["authorized_permissions"])
    assert all(entry["required_preflight_target_state"] == "MUST_NOT_EXIST" for entry in artifact["authorized_permissions"])
    assert capture["filesystem_mutation_authorized"] is True
    assert capture["filesystem_mutated"] is False
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_authorized"] is False
    assert capture["automatic_authorization_inferred"] is False
    assert artifact["authority_flags"]["authorizes_filesystem_mutation"] is True
    assert artifact["authority_flags"]["performs_filesystem_mutation"] is False
    verify_filesystem_mutation_authorization_artifact(artifact)


def test_filesystem_mutation_authorization_is_deterministic_for_identical_lineage(tmp_path) -> None:
    first = _authorize(*_validated_and_accepted_bundle(tmp_path, "first"))
    second = _authorize(*_validated_and_accepted_bundle(tmp_path, "second"))

    assert first["filesystem_mutation_authorization_hash"] == second["filesystem_mutation_authorization_hash"]
    assert first["filesystem_mutation_authorization_artifact"] == second["filesystem_mutation_authorization_artifact"]


def test_filesystem_mutation_authorization_prevents_reuse_of_lineage_key(tmp_path) -> None:
    manifest, content, tests, acceptance = _validated_and_accepted_bundle(tmp_path)
    first = _authorize(manifest, content, tests, acceptance)
    second = _authorize(manifest, content, tests, acceptance, prior=[first["authorization_lineage_key"]])

    assert second["authorization_status"] == FAILED_CLOSED
    assert "authorization lineage already used" in second["failure_reason"]
    assert second["filesystem_mutation_authorized"] is False


def test_filesystem_mutation_authorization_fails_closed_without_explicit_authorization(tmp_path) -> None:
    manifest, content, tests, acceptance = _validated_and_accepted_bundle(tmp_path)
    human = _authorization_human()
    human["authorization_statement"] = "Please apply this."
    capture = _authorize(manifest, content, tests, acceptance, human=human)

    assert capture["authorization_status"] == FAILED_CLOSED
    assert "explicit authorization statement required" in capture["failure_reason"]
    assert capture["automatic_authorization_inferred"] is False


def test_filesystem_mutation_authorization_fails_closed_on_content_validation_mismatch(tmp_path) -> None:
    manifest, content, tests, acceptance = _validated_and_accepted_bundle(tmp_path)
    content = deepcopy(content)
    content["implementation_bundle_id"] = "OTHER_BUNDLE"
    _rebind_content_validation_artifact(content)
    capture = _authorize(manifest, content, tests, acceptance)

    assert capture["authorization_status"] == FAILED_CLOSED
    assert "content validation bundle mismatch" in capture["failure_reason"]


def test_filesystem_mutation_authorization_fails_closed_on_test_validation_mismatch(tmp_path) -> None:
    manifest, content, tests, acceptance = _validated_and_accepted_bundle(tmp_path)
    tests = deepcopy(tests)
    tests["implementation_manifest_reference"] = "OTHER-MANIFEST"
    _rebind_test_validation_artifact(tests)
    capture = _authorize(manifest, content, tests, acceptance)

    assert capture["authorization_status"] == FAILED_CLOSED
    assert "test validation manifest reference mismatch" in capture["failure_reason"]


def test_filesystem_mutation_authorization_fails_closed_on_acceptance_mismatch(tmp_path) -> None:
    manifest, content, tests, acceptance = _validated_and_accepted_bundle(tmp_path)
    acceptance = deepcopy(acceptance)
    acceptance["generated_content_validation_hash"] = "sha256:mismatched"
    _rebind_acceptance_artifact(acceptance)
    capture = _authorize(manifest, content, tests, acceptance)

    assert capture["authorization_status"] == FAILED_CLOSED
    assert "acceptance content validation mismatch" in capture["failure_reason"]


def test_filesystem_mutation_authorization_fails_closed_on_non_create_only_permission(tmp_path) -> None:
    manifest, content, tests, acceptance = _validated_and_accepted_bundle(tmp_path)
    manifest = deepcopy(manifest)
    manifest["file_entries"][0]["operation"] = "UPDATE_ONLY"
    manifest["implementation_manifest_hash"] = replay_hash({"invalid": "operation"})
    manifest["artifact_hash"] = replay_hash({key: value for key, value in manifest.items() if key != "artifact_hash"})
    capture = _authorize(manifest, content, tests, acceptance)

    assert capture["authorization_status"] == FAILED_CLOSED
    assert "manifest hash mismatch" in capture["failure_reason"]


def test_filesystem_mutation_authorization_artifact_verifier_detects_tamper(tmp_path) -> None:
    artifact = _authorize(*_validated_and_accepted_bundle(tmp_path))["filesystem_mutation_authorization_artifact"]
    artifact["authorized_permissions"][0]["target_path"] = "aigol/runtime/other.py"

    with pytest.raises(FailClosedRuntimeError, match="filesystem mutation authorization hash mismatch"):
        verify_filesystem_mutation_authorization_artifact(artifact)


def test_filesystem_mutation_authorization_runtime_has_no_mutation_or_invocation_imports() -> None:
    import aigol.runtime.filesystem_mutation_authorization_runtime as module

    source = inspect.getsource(module)

    assert "open(" not in source
    assert ".write_text(" not in source
    assert "write_json_immutable" not in source
    assert "invoke_worker(" not in source
    assert "run_provider" not in source
    assert "produce_provider" not in source
    assert "execute(" not in source
