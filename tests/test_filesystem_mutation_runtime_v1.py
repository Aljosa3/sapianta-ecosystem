"""Tests for AIGOL_FILESYSTEM_MUTATION_RUNTIME_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect

import pytest

from aigol.runtime.filesystem_mutation_authorization_runtime import (
    AUTHORIZATION_DECISION,
    AUTHORIZATION_SCOPE,
    AUTHORIZATION_STATEMENT,
    _compute_authorization_hash,
    authorize_filesystem_mutation,
)
from aigol.runtime.filesystem_mutation_runtime import (
    FAILED_CLOSED,
    FILESYSTEM_MUTATION_ARTIFACT_V1,
    FILESYSTEM_MUTATION_COMPLETED,
    apply_filesystem_mutation,
    verify_filesystem_mutation_artifact,
)
from aigol.runtime.generated_content_acceptance_runtime import (
    ACCEPTANCE_DECISION,
    ACCEPTANCE_SCOPE,
    ACCEPTANCE_STATEMENT,
    accept_generated_content,
)
from aigol.runtime.generated_content_validation_runtime import validate_generated_content
from aigol.runtime.generated_test_validation_runtime import validate_generated_tests
from aigol.runtime.implementation_manifest_runtime import CREATE_ONLY, create_implementation_manifest
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-06-05T18:00:00Z"


def _hash(label: str) -> str:
    return replay_hash({"ref": label})


def _files() -> list[dict]:
    return [
        {
            "file_entry_id": "FILE-RUNTIME-000001",
            "target_path": "aigol/runtime/mutated_worker.py",
            "artifact_type": "PYTHON_RUNTIME_MODULE",
            "operation": CREATE_ONLY,
            "content": "def run():\n    return {'status': 'ok'}\n",
            "source_segment_reference": "PROVIDER-SEGMENT-RUNTIME",
            "validation_requirements": ["python -m pytest tests/test_mutated_worker.py"],
        },
        {
            "file_entry_id": "FILE-GOVERNANCE-000001",
            "target_path": "governance/MUTATED_WORKER_V1.md",
            "artifact_type": "GOVERNANCE_DOCUMENT_MARKDOWN",
            "operation": CREATE_ONLY,
            "content": "# MUTATED_WORKER_V1\n\nStatus: generated candidate.\n",
            "source_segment_reference": "PROVIDER-SEGMENT-GOVERNANCE",
            "validation_requirements": ["git diff --check"],
        },
    ]


def _tests() -> list[dict]:
    return [
        {
            "test_entry_id": "TEST-RUNTIME-000001",
            "target_path": "tests/test_mutated_worker.py",
            "artifact_type": "PYTEST_TEST",
            "operation": CREATE_ONLY,
            "content": (
                "from aigol.runtime.mutated_worker import run\n\n\n"
                "def test_run():\n"
                "    assert run()['status'] == 'ok'\n"
            ),
            "tests_file_entries": ["FILE-RUNTIME-000001"],
            "validation_command": "python -m pytest tests/test_mutated_worker.py",
            "expected_coverage_target": "aigol/runtime/mutated_worker.py",
            "negative_case_requirement": "rejects missing status",
            "fixture_references": [],
        }
    ]


def _manifest(tmp_path, replay_name: str = "manifest") -> dict:
    capture = create_implementation_manifest(
        manifest_id="IMPLEMENTATION-MANIFEST-FILESYSTEM-MUTATION-000001",
        canonical_chain_id="CHAIN-FILESYSTEM-MUTATION-000001",
        implementation_bundle_id="FILESYSTEM_MUTATION_BUNDLE_V1",
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
        target_worker="MUTATED_WORKER",
        generated_files=_files(),
        generated_tests=_tests(),
        validation_requirements=["python -m pytest tests/test_mutated_worker.py", "git diff --check"],
        known_gaps=["post-application verification not yet performed"],
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


def _authorized_bundle(tmp_path, suffix: str = "bundle") -> tuple[dict, dict]:
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
    return manifest, authorization


def _mutate(manifest: dict, authorization: dict, target_root) -> dict:
    return apply_filesystem_mutation(
        mutation_id="FILESYSTEM-MUTATION-000001",
        implementation_manifest_artifact=manifest,
        filesystem_mutation_authorization_artifact=authorization,
        target_root=target_root,
        created_at=CREATED_AT,
    )


def _rebind_authorization_artifact(artifact: dict) -> dict:
    artifact["filesystem_mutation_authorization_hash"] = _compute_authorization_hash(artifact)
    artifact["artifact_hash"] = replay_hash({key: value for key, value in artifact.items() if key != "artifact_hash"})
    return artifact


def test_filesystem_mutation_materializes_only_authorized_create_only_files(tmp_path) -> None:
    target_root = tmp_path / "workspace"
    manifest, authorization = _authorized_bundle(tmp_path)
    capture = _mutate(manifest, authorization, target_root)
    artifact = capture["filesystem_mutation_artifact"]

    assert capture["mutation_status"] == FILESYSTEM_MUTATION_COMPLETED
    assert artifact["artifact_type"] == FILESYSTEM_MUTATION_ARTIFACT_V1
    assert artifact["implementation_manifest_hash"] == manifest["implementation_manifest_hash"]
    assert artifact["filesystem_mutation_authorization_hash"] == authorization["filesystem_mutation_authorization_hash"]
    assert artifact["created_file_count"] == 3
    assert [result["target_path"] for result in artifact["mutation_results"]] == [
        "aigol/runtime/mutated_worker.py",
        "governance/MUTATED_WORKER_V1.md",
        "tests/test_mutated_worker.py",
    ]
    assert (target_root / "aigol/runtime/mutated_worker.py").read_text(encoding="utf-8") == _files()[0]["content"]
    assert (target_root / "governance/MUTATED_WORKER_V1.md").read_text(encoding="utf-8") == _files()[1]["content"]
    assert (target_root / "tests/test_mutated_worker.py").read_text(encoding="utf-8") == _tests()[0]["content"]
    assert all(result["operation"] == CREATE_ONLY for result in artifact["mutation_results"])
    assert all(result["content_hash"] == result["materialized_content_hash"] for result in artifact["mutation_results"])
    assert capture["filesystem_mutated"] is True
    assert capture["overwrite_performed"] is False
    assert capture["delete_performed"] is False
    assert capture["rename_performed"] is False
    assert capture["move_performed"] is False
    assert capture["implicit_file_creation_performed"] is False
    assert capture["unauthorized_files_created"] is False
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    verify_filesystem_mutation_artifact(artifact)


def test_filesystem_mutation_is_deterministic_for_identical_authorized_bundles(tmp_path) -> None:
    first_manifest, first_authorization = _authorized_bundle(tmp_path, "first")
    second_manifest, second_authorization = _authorized_bundle(tmp_path, "second")
    first = _mutate(first_manifest, first_authorization, tmp_path / "first_workspace")
    second = _mutate(second_manifest, second_authorization, tmp_path / "second_workspace")

    assert first["filesystem_mutation_hash"] == second["filesystem_mutation_hash"]
    assert first["filesystem_mutation_artifact"] == second["filesystem_mutation_artifact"]


def test_filesystem_mutation_fails_closed_on_collision_before_writing_any_authorized_files(tmp_path) -> None:
    target_root = tmp_path / "workspace"
    manifest, authorization = _authorized_bundle(tmp_path)
    collision = target_root / "aigol/runtime/mutated_worker.py"
    collision.parent.mkdir(parents=True)
    collision.write_text("existing content\n", encoding="utf-8")
    capture = _mutate(manifest, authorization, target_root)

    assert capture["mutation_status"] == FAILED_CLOSED
    assert "CREATE_ONLY collision" in capture["failure_reason"]
    assert capture["filesystem_mutated"] is False
    assert collision.read_text(encoding="utf-8") == "existing content\n"
    assert not (target_root / "governance/MUTATED_WORKER_V1.md").exists()
    assert not (target_root / "tests/test_mutated_worker.py").exists()


def test_filesystem_mutation_fails_closed_on_authorization_lineage_mismatch(tmp_path) -> None:
    manifest, authorization = _authorized_bundle(tmp_path)
    authorization = deepcopy(authorization)
    authorization["implementation_manifest_hash"] = "sha256:mismatched"
    _rebind_authorization_artifact(authorization)
    capture = _mutate(manifest, authorization, tmp_path / "workspace")

    assert capture["mutation_status"] == FAILED_CLOSED
    assert "authorization manifest hash mismatch" in capture["failure_reason"]
    assert capture["filesystem_mutated"] is False


def test_filesystem_mutation_fails_closed_on_unauthorized_path_set(tmp_path) -> None:
    manifest, authorization = _authorized_bundle(tmp_path)
    authorization = deepcopy(authorization)
    authorization["authorized_permissions"] = authorization["authorized_permissions"][:-1]
    authorization["authorized_permission_count"] = len(authorization["authorized_permissions"])
    _rebind_authorization_artifact(authorization)
    capture = _mutate(manifest, authorization, tmp_path / "workspace")

    assert capture["mutation_status"] == FAILED_CLOSED
    assert "authorized paths do not match manifest paths" in capture["failure_reason"]
    assert capture["unauthorized_files_created"] is False


def test_filesystem_mutation_fails_closed_on_non_create_only_permission(tmp_path) -> None:
    manifest, authorization = _authorized_bundle(tmp_path)
    authorization = deepcopy(authorization)
    authorization["authorized_permissions"][0]["operation"] = "UPDATE_ONLY"
    _rebind_authorization_artifact(authorization)
    capture = _mutate(manifest, authorization, tmp_path / "workspace")

    assert capture["mutation_status"] == FAILED_CLOSED
    assert "permission must be CREATE_ONLY" in capture["failure_reason"]
    assert capture["overwrite_performed"] is False


def test_filesystem_mutation_artifact_verifier_detects_tamper(tmp_path) -> None:
    artifact = _mutate(*_authorized_bundle(tmp_path), tmp_path / "workspace")["filesystem_mutation_artifact"]
    artifact["mutation_results"][0]["created"] = False

    with pytest.raises(FailClosedRuntimeError, match="filesystem mutation hash mismatch"):
        verify_filesystem_mutation_artifact(artifact)


def test_filesystem_mutation_runtime_does_not_import_forbidden_invocations() -> None:
    import aigol.runtime.filesystem_mutation_runtime as module

    source = inspect.getsource(module)

    assert "invoke_worker(" not in source
    assert "run_provider" not in source
    assert "produce_provider" not in source
    assert ".unlink(" not in source
    assert ".rename(" not in source
    assert ".replace(" not in source
