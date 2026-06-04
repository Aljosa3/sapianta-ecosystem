"""Tests for AIGOL_EXECUTABLE_DOMAIN_BUNDLE_RUNTIME_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect

import pytest

from aigol.cli.aigol_cli import run_interactive_conversation
from aigol.runtime.executable_domain_bundle_runtime import (
    ARTIFACTS_CREATED,
    EXECUTABLE_BUNDLE_ARTIFACT_TYPES,
    EXECUTABLE_BUNDLE_AUTHORIZED,
    EXECUTABLE_BUNDLE_CONTENTS,
    EXECUTABLE_BUNDLE_MUTATION_AUTHORIZATION,
    EXECUTABLE_BUNDLE_PATHS,
    EXECUTABLE_BUNDLE_VERIFIED,
    EXECUTABLE_DOMAIN_BUNDLE_ARTIFACT_V1,
    MARKETING_EXECUTABLE_DOMAIN_BUNDLE_ID,
    create_executable_bundle_mutation_authorization,
    create_marketing_executable_domain_bundle,
    reconstruct_executable_domain_bundle_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash
from test_worker_result_validation_runtime_v1 import CREATED_AT, _args, _input_sequence, _validate


def _workspace(tmp_path):
    workspace = tmp_path / "workspace"
    (workspace / "governance").mkdir(parents=True)
    (workspace / "aigol" / "runtime").mkdir(parents=True)
    (workspace / "tests").mkdir()
    return workspace


def _authorization(validation: dict, *, suffix: str) -> dict:
    return create_executable_bundle_mutation_authorization(
        executable_bundle_authorization_id=f"EXECUTABLE-BUNDLE-AUTHORIZATION-{suffix}",
        bundle_id=MARKETING_EXECUTABLE_DOMAIN_BUNDLE_ID,
        worker_result_validation_artifact=validation["worker_result_validation_artifact"],
        authorized_by="AIGOL_GOVERNANCE",
        authorized_at=CREATED_AT,
    )


def _create(tmp_path, *, suffix: str, validation: dict | None = None, authorization: dict | None = None) -> dict:
    if validation is None:
        validation = _validate(tmp_path, prompt="Create a marketing domain.", suffix=suffix)
    if authorization is None:
        authorization = _authorization(validation, suffix=suffix)
    return create_marketing_executable_domain_bundle(
        executable_bundle_runtime_id=f"EXECUTABLE-DOMAIN-BUNDLE-{suffix}",
        worker_result_validation_artifact=validation["worker_result_validation_artifact"],
        worker_result_validation_replay_reference=validation["worker_result_validation_replay_reference"],
        executable_bundle_mutation_authorization_artifact=authorization,
        workspace_root=_workspace(tmp_path),
        created_by="AIGOL_GOVERNANCE",
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"executable_bundle_{suffix}",
    )


def _rehash(artifact: dict) -> dict:
    artifact = deepcopy(artifact)
    artifact.pop("artifact_hash", None)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def test_result_validated_becomes_verified_executable_domain_bundle(tmp_path) -> None:
    result = _create(tmp_path, suffix="success")
    artifact = result["executable_domain_bundle_artifact"]
    reconstructed = reconstruct_executable_domain_bundle_replay(tmp_path / "executable_bundle_success")

    assert result["executable_bundle_authorization_status"] == EXECUTABLE_BUNDLE_AUTHORIZED
    assert result["artifact_creation_status"] == ARTIFACTS_CREATED
    assert result["executable_bundle_verification_status"] == EXECUTABLE_BUNDLE_VERIFIED
    assert artifact["artifact_type"] == EXECUTABLE_DOMAIN_BUNDLE_ARTIFACT_V1
    assert artifact["artifact_paths"] == list(EXECUTABLE_BUNDLE_PATHS)
    assert artifact["partial_completion"] is False
    assert reconstructed["executable_bundle_verification_status"] == EXECUTABLE_BUNDLE_VERIFIED
    for path in EXECUTABLE_BUNDLE_PATHS:
        assert (tmp_path / "workspace" / path).read_text(encoding="utf-8") == EXECUTABLE_BUNDLE_CONTENTS[path]


def test_executable_bundle_authorization_binds_exact_ordered_artifacts(tmp_path) -> None:
    validation = _validate(tmp_path, prompt="Create a marketing domain.", suffix="authorization")
    authorization = _authorization(validation, suffix="authorization")

    assert authorization["artifact_type"] == EXECUTABLE_BUNDLE_MUTATION_AUTHORIZATION
    assert authorization["bundle_id"] == MARKETING_EXECUTABLE_DOMAIN_BUNDLE_ID
    assert [item["path"] for item in authorization["artifacts"]] == list(EXECUTABLE_BUNDLE_PATHS)
    assert [item["artifact_type"] for item in authorization["artifacts"]] == [
        EXECUTABLE_BUNDLE_ARTIFACT_TYPES[path] for path in EXECUTABLE_BUNDLE_PATHS
    ]
    assert all(item["permission"] == "CREATE_ONLY" for item in authorization["artifacts"])
    assert authorization["implicit_creation_permitted"] is False


def test_executable_bundle_replay_records_required_artifacts(tmp_path) -> None:
    _create(tmp_path, suffix="events")
    replay_dir = tmp_path / "executable_bundle_events"

    assert (replay_dir / "000_executable_bundle_authorization_recorded.json").exists()
    assert (replay_dir / "001_executable_bundle_creation_evidence_recorded.json").exists()
    assert (replay_dir / "002_executable_bundle_per_artifact_verification_recorded.json").exists()
    assert (replay_dir / "003_executable_bundle_verification_result_recorded.json").exists()


def test_existing_artifact_fails_before_any_executable_bundle_member_is_created(tmp_path) -> None:
    validation = _validate(tmp_path, prompt="Create a marketing domain.", suffix="existing")
    authorization = _authorization(validation, suffix="existing")
    workspace = _workspace(tmp_path)
    existing = workspace / EXECUTABLE_BUNDLE_PATHS[0]
    existing.write_text("existing\n", encoding="utf-8")

    result = create_marketing_executable_domain_bundle(
        executable_bundle_runtime_id="EXECUTABLE-DOMAIN-BUNDLE-existing",
        worker_result_validation_artifact=validation["worker_result_validation_artifact"],
        worker_result_validation_replay_reference=validation["worker_result_validation_replay_reference"],
        executable_bundle_mutation_authorization_artifact=authorization,
        workspace_root=workspace,
        created_by="AIGOL_GOVERNANCE",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "executable_bundle_existing",
    )

    assert result["executable_bundle_verification_status"] == "FAILED_CLOSED"
    assert result["partial_completion"] is False
    assert existing.read_text(encoding="utf-8") == "existing\n"
    assert all(not (workspace / path).exists() for path in EXECUTABLE_BUNDLE_PATHS[1:])


def test_existing_artifact_failure_replay_reconstructs_without_missing_authorization_cascade(tmp_path) -> None:
    validation = _validate(tmp_path, prompt="Create a marketing domain.", suffix="existing-replay")
    authorization = _authorization(validation, suffix="existing-replay")
    workspace = _workspace(tmp_path)
    existing = workspace / EXECUTABLE_BUNDLE_PATHS[0]
    existing.write_text("existing\n", encoding="utf-8")
    replay_dir = tmp_path / "executable_bundle_existing_replay"

    result = create_marketing_executable_domain_bundle(
        executable_bundle_runtime_id="EXECUTABLE-DOMAIN-BUNDLE-existing-replay",
        worker_result_validation_artifact=validation["worker_result_validation_artifact"],
        worker_result_validation_replay_reference=validation["worker_result_validation_replay_reference"],
        executable_bundle_mutation_authorization_artifact=authorization,
        workspace_root=workspace,
        created_by="AIGOL_GOVERNANCE",
        created_at=CREATED_AT,
        replay_dir=replay_dir,
    )
    reconstructed = reconstruct_executable_domain_bundle_replay(replay_dir)

    assert result["executable_bundle_verification_status"] == "FAILED_CLOSED"
    assert reconstructed["executable_bundle_verification_status"] == "FAILED_CLOSED"
    assert "target already exists" in reconstructed["failure_reason"]
    assert reconstructed["replay_artifact_count"] == 1
    assert not (replay_dir / "000_executable_bundle_authorization_recorded.json").exists()


def test_interactive_marketing_domain_collision_fails_closed_once_without_replay_review_cascade(tmp_path) -> None:
    args = _args(tmp_path, session_id="SESSION-CLI-EXECUTABLE-BUNDLE-COLLISION-000001")
    existing = tmp_path / EXECUTABLE_BUNDLE_PATHS[0]
    existing.write_text("existing\n", encoding="utf-8")
    output: list[str] = []

    result = run_interactive_conversation(
        args,
        input_func=_input_sequence(["Create a marketing domain.", "exit"]),
        output_func=output.append,
    )

    failed_closed_lines = [chunk for chunk in output if chunk.startswith("FAILED_CLOSED:")]
    assert len(failed_closed_lines) == 1
    assert "target already exists" in failed_closed_lines[0]
    assert "runtime artifact missing" not in "\n".join(output)
    assert result["executable_bundle_verified"] is False
    assert result["post_execution_replay_reviewed"] is False
    assert result["terminated"] is False


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"bundle_id": "OTHER-BUNDLE"}, "bundle id"),
        ({"permission": "OVERWRITE"}, "create-only"),
        ({"overwrite_permitted": True}, "overwrite_permitted"),
        ({"implicit_creation_permitted": True}, "implicit_creation_permitted"),
        ({"chain_id": "OTHER-CHAIN"}, "chain"),
        ({"artifacts": []}, "artifact list"),
    ],
)
def test_executable_bundle_fails_closed_on_authorization_drift(tmp_path, changes: dict, reason: str) -> None:
    suffix = reason.replace(" ", "-")
    validation = _validate(tmp_path, prompt="Create a marketing domain.", suffix=suffix)
    authorization = _rehash({**_authorization(validation, suffix=suffix), **changes})

    result = _create(tmp_path, suffix=suffix, validation=validation, authorization=authorization)

    assert result["executable_bundle_verification_status"] == "FAILED_CLOSED"
    assert reason in result["failure_reason"]
    assert all(not (tmp_path / "workspace" / path).exists() for path in EXECUTABLE_BUNDLE_PATHS)


def test_executable_bundle_reconstruction_detects_artifact_content_mismatch(tmp_path) -> None:
    _create(tmp_path, suffix="content-mismatch")
    (tmp_path / "workspace" / EXECUTABLE_BUNDLE_PATHS[-1]).write_text("corrupted\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="artifact mismatch"):
        reconstruct_executable_domain_bundle_replay(tmp_path / "executable_bundle_content-mismatch")


def test_executable_bundle_runtime_has_no_delete_rename_move_or_directory_creation() -> None:
    source = inspect.getsource(create_marketing_executable_domain_bundle)

    assert ".unlink(" not in source
    assert ".rename(" not in source
    assert ".replace(" not in source
    assert ".mkdir(" not in source
    assert "open(\"x\"" in source


def test_interactive_cli_creates_and_verifies_executable_marketing_domain_bundle(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _args(tmp_path, session_id="SESSION-CLI-EXECUTABLE-DOMAIN-BUNDLE-000001"),
        input_func=_input_sequence(["Create a marketing domain.", "exit"]),
        output_func=output.append,
    )

    assert result["executable_bundle_authorized"] is True
    assert result["artifacts_created"] is True
    assert result["executable_bundle_verified"] is True
    assert result["post_execution_replay_reviewed"] is True
    assert result["terminated"] is True
    assert all((tmp_path / path).read_text(encoding="utf-8") == EXECUTABLE_BUNDLE_CONTENTS[path] for path in EXECUTABLE_BUNDLE_PATHS)
    assert any("Executable Bundle Authorization Status: EXECUTABLE_BUNDLE_AUTHORIZED" in chunk for chunk in output)
    assert any("Artifact Creation Status: ARTIFACTS_CREATED" in chunk for chunk in output)
    assert any("Executable Bundle Verification Status: EXECUTABLE_BUNDLE_VERIFIED" in chunk for chunk in output)
