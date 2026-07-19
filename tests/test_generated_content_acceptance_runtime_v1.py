"""Tests for AIGOL_GENERATED_CONTENT_ACCEPTANCE_RUNTIME_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect

import pytest

from aigol.runtime.generated_content_acceptance_runtime import (
    ACCEPTANCE_DECISION,
    ACCEPTANCE_SCOPE,
    ACCEPTANCE_STATEMENT,
    FAILED_CLOSED,
    GENERATED_CONTENT_ACCEPTANCE_ARTIFACT_V1,
    GENERATED_CONTENT_ACCEPTED,
    accept_generated_content,
    verify_generated_content_acceptance_artifact,
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


CREATED_AT = "2026-06-05T15:00:00Z"


def _hash(label: str) -> str:
    return replay_hash({"ref": label})


def _files() -> list[dict]:
    return [
        {
            "file_entry_id": "FILE-RUNTIME-000001",
            "target_path": "aigol/runtime/accepted_worker.py",
            "artifact_type": "PYTHON_RUNTIME_MODULE",
            "operation": CREATE_ONLY,
            "content": "def run():\n    return {'status': 'ok'}\n",
            "source_segment_reference": "PROVIDER-SEGMENT-RUNTIME",
            "validation_requirements": ["python -m pytest tests/test_accepted_worker.py"],
        }
    ]


def _tests() -> list[dict]:
    return [
        {
            "test_entry_id": "TEST-RUNTIME-000001",
            "target_path": "tests/test_accepted_worker.py",
            "artifact_type": "PYTEST_TEST",
            "operation": CREATE_ONLY,
            "content": (
                "from aigol.runtime.accepted_worker import run\n\n\n"
                "def test_run():\n"
                "    assert run()['status'] == 'ok'\n"
            ),
            "tests_file_entries": ["FILE-RUNTIME-000001"],
            "validation_command": "python -m pytest tests/test_accepted_worker.py",
            "expected_coverage_target": "aigol/runtime/accepted_worker.py",
            "negative_case_requirement": "rejects missing status",
            "fixture_references": [],
        }
    ]


def _manifest(tmp_path, replay_name: str = "manifest") -> dict:
    capture = create_implementation_manifest(
        manifest_id="IMPLEMENTATION-MANIFEST-GENERATED-ACCEPTANCE-000001",
        canonical_chain_id="CHAIN-GENERATED-ACCEPTANCE-000001",
        implementation_bundle_id="GENERATED_ACCEPTANCE_BUNDLE_V1",
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
        target_worker="ACCEPTED_WORKER",
        generated_files=_files(),
        generated_tests=_tests(),
        validation_requirements=["python -m pytest tests/test_accepted_worker.py", "git diff --check"],
        known_gaps=["filesystem mutation authorization not yet performed"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / replay_name,
    )
    return capture["implementation_manifest_artifact"]


def _human_evidence() -> dict:
    return {
        "actor_id": "human.operator",
        "decision": ACCEPTANCE_DECISION,
        "accepted_at": CREATED_AT,
        "acceptance_scope": ACCEPTANCE_SCOPE,
        "acceptance_statement": ACCEPTANCE_STATEMENT,
    }


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


def _accept(manifest: dict, content: dict, tests: dict, *, human: dict | None = None, prior: list[str] | None = None) -> dict:
    return accept_generated_content(
        acceptance_id="GENERATED-CONTENT-ACCEPTANCE-000001",
        implementation_manifest_artifact=manifest,
        generated_content_validation_artifact=content,
        generated_test_validation_artifact=tests,
        human_acceptance_evidence=_human_evidence() if human is None else human,
        created_at=CREATED_AT,
        prior_acceptance_lineage_keys=prior,
    )


def _rebind_content_validation_artifact(artifact: dict) -> dict:
    artifact["generated_content_validation_hash"] = _compute_content_validation_hash(artifact)
    artifact["artifact_hash"] = replay_hash({key: value for key, value in artifact.items() if key != "artifact_hash"})
    return artifact


def _rebind_test_validation_artifact(artifact: dict) -> dict:
    artifact["generated_test_validation_hash"] = _compute_test_validation_hash(artifact)
    artifact["artifact_hash"] = replay_hash({key: value for key, value in artifact.items() if key != "artifact_hash"})
    return artifact


def test_generated_content_acceptance_binds_manifest_and_validation_lineage(tmp_path) -> None:
    manifest, content, tests = _validated_bundle(tmp_path)
    capture = _accept(manifest, content, tests)
    artifact = capture["generated_content_acceptance_artifact"]

    assert capture["acceptance_status"] == GENERATED_CONTENT_ACCEPTED
    assert artifact["artifact_type"] == GENERATED_CONTENT_ACCEPTANCE_ARTIFACT_V1
    assert artifact["implementation_manifest_hash"] == manifest["implementation_manifest_hash"]
    assert artifact["generated_content_validation_hash"] == content["generated_content_validation_hash"]
    assert artifact["generated_test_validation_hash"] == tests["generated_test_validation_hash"]
    assert artifact["human_decision"] == ACCEPTANCE_DECISION
    assert artifact["acceptance_reuse_prohibited"] is True
    assert all(artifact["validation_checks"].values())
    assert capture["filesystem_mutated"] is False
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_authorized"] is False
    assert capture["automatic_approval_inferred"] is False
    assert all(value is False for value in artifact["authority_flags"].values())
    verify_generated_content_acceptance_artifact(artifact)


def test_generated_content_acceptance_is_deterministic_for_identical_lineage(tmp_path) -> None:
    first = _accept(*_validated_bundle(tmp_path, "first"))
    second = _accept(*_validated_bundle(tmp_path, "second"))

    assert first["generated_content_acceptance_hash"] == second["generated_content_acceptance_hash"]
    assert first["generated_content_acceptance_artifact"] == second["generated_content_acceptance_artifact"]


def test_generated_content_acceptance_prevents_reuse_of_lineage_key(tmp_path) -> None:
    manifest, content, tests = _validated_bundle(tmp_path)
    first = _accept(manifest, content, tests)
    second = _accept(manifest, content, tests, prior=[first["acceptance_lineage_key"]])

    assert second["acceptance_status"] == FAILED_CLOSED
    assert "acceptance lineage already used" in second["failure_reason"]


def test_generated_content_acceptance_fails_closed_without_explicit_human_statement(tmp_path) -> None:
    manifest, content, tests = _validated_bundle(tmp_path)
    human = _human_evidence()
    human["acceptance_statement"] = "Looks fine."
    capture = _accept(manifest, content, tests, human=human)

    assert capture["acceptance_status"] == FAILED_CLOSED
    assert "explicit acceptance statement required" in capture["failure_reason"]
    assert capture["automatic_approval_inferred"] is False


def test_generated_content_acceptance_fails_closed_on_content_validation_mismatch(tmp_path) -> None:
    manifest, content, tests = _validated_bundle(tmp_path)
    content = deepcopy(content)
    content["implementation_manifest_hash"] = "sha256:mismatched"
    _rebind_content_validation_artifact(content)
    capture = _accept(manifest, content, tests)

    assert capture["acceptance_status"] == FAILED_CLOSED
    assert "content validation manifest hash mismatch" in capture["failure_reason"]


def test_generated_content_acceptance_fails_closed_on_test_validation_mismatch(tmp_path) -> None:
    manifest, content, tests = _validated_bundle(tmp_path)
    tests = deepcopy(tests)
    tests["implementation_bundle_id"] = "OTHER_BUNDLE"
    _rebind_test_validation_artifact(tests)
    capture = _accept(manifest, content, tests)

    assert capture["acceptance_status"] == FAILED_CLOSED
    assert "test validation bundle mismatch" in capture["failure_reason"]


def test_generated_content_acceptance_artifact_verifier_detects_tamper(tmp_path) -> None:
    artifact = _accept(*_validated_bundle(tmp_path))["generated_content_acceptance_artifact"]
    artifact["validation_checks"]["human_acceptance_explicit"] = False

    with pytest.raises(FailClosedRuntimeError, match="generated content acceptance hash mismatch"):
        verify_generated_content_acceptance_artifact(artifact)


def test_generated_content_acceptance_runtime_has_no_mutation_or_invocation_imports() -> None:
    import aigol.runtime.generated_content_acceptance_runtime as module

    source = inspect.getsource(module.accept_generated_content)

    assert "open(" not in source
    assert ".write_text(" not in source
    assert "write_json_immutable" not in source
    assert "authorize_execution(" not in source
    assert "invoke_worker(" not in source
    assert "run_provider" not in source
    assert "produce_provider" not in source
    assert "create_human_implementation_approval(" not in source
