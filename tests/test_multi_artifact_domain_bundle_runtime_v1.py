"""Tests for AIGOL_MULTI_ARTIFACT_DOMAIN_BUNDLE_RUNTIME_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect
import json

import pytest

from aigol.cli.aigol_cli import run_interactive_conversation
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.executable_domain_bundle_runtime import (
    EXECUTABLE_BUNDLE_CONTENTS,
    EXECUTABLE_BUNDLE_PATHS,
)
from aigol.runtime.multi_artifact_domain_bundle_runtime import (
    ARTIFACTS_CREATED,
    BUNDLE_ARTIFACT_TYPES,
    BUNDLE_AUTHORIZED,
    BUNDLE_CONTENTS,
    BUNDLE_MUTATION_AUTHORIZATION,
    BUNDLE_PATHS,
    BUNDLE_VERIFIED,
    MARKETING_DOMAIN_BUNDLE_ID,
    MULTI_ARTIFACT_DOMAIN_BUNDLE_ARTIFACT_V1,
    create_bundle_mutation_authorization,
    create_marketing_domain_bundle,
    reconstruct_multi_artifact_domain_bundle_replay,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash
from test_worker_result_validation_runtime_v1 import CREATED_AT, _args, _input_sequence, _validate


def _workspace(tmp_path):
    workspace = tmp_path / "workspace"
    (workspace / "governance").mkdir(parents=True)
    return workspace


def _authorization(validation: dict, *, suffix: str) -> dict:
    return create_bundle_mutation_authorization(
        bundle_authorization_id=f"BUNDLE-AUTHORIZATION-{suffix}",
        bundle_id=MARKETING_DOMAIN_BUNDLE_ID,
        worker_result_validation_artifact=validation["worker_result_validation_artifact"],
        authorized_by="AIGOL_GOVERNANCE",
        authorized_at=CREATED_AT,
    )


def _create(tmp_path, *, suffix: str, validation: dict | None = None, authorization: dict | None = None) -> dict:
    if validation is None:
        validation = _validate(tmp_path, prompt="Create a marketing domain.", suffix=suffix)
    if authorization is None:
        authorization = _authorization(validation, suffix=suffix)
    return create_marketing_domain_bundle(
        domain_bundle_runtime_id=f"DOMAIN-BUNDLE-{suffix}",
        worker_result_validation_artifact=validation["worker_result_validation_artifact"],
        worker_result_validation_replay_reference=validation["worker_result_validation_replay_reference"],
        bundle_mutation_authorization_artifact=authorization,
        workspace_root=_workspace(tmp_path),
        created_by="AIGOL_GOVERNANCE",
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"domain_bundle_{suffix}",
    )


def _rehash(artifact: dict) -> dict:
    artifact = deepcopy(artifact)
    artifact.pop("artifact_hash", None)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def test_result_validated_becomes_verified_marketing_domain_bundle(tmp_path) -> None:
    result = _create(tmp_path, suffix="success")
    artifact = result["multi_artifact_domain_bundle_artifact"]
    reconstructed = reconstruct_multi_artifact_domain_bundle_replay(tmp_path / "domain_bundle_success")

    assert result["bundle_authorization_status"] == BUNDLE_AUTHORIZED
    assert result["artifact_creation_status"] == ARTIFACTS_CREATED
    assert result["bundle_verification_status"] == BUNDLE_VERIFIED
    assert artifact["artifact_type"] == MULTI_ARTIFACT_DOMAIN_BUNDLE_ARTIFACT_V1
    assert artifact["artifact_paths"] == list(BUNDLE_PATHS)
    assert artifact["partial_completion"] is False
    assert reconstructed["bundle_verification_status"] == BUNDLE_VERIFIED
    for path in BUNDLE_PATHS:
        assert (tmp_path / "workspace" / path).read_text(encoding="utf-8") == BUNDLE_CONTENTS[path]


def test_bundle_mutation_authorization_contains_exact_manifests(tmp_path) -> None:
    validation = _validate(tmp_path, prompt="Create a marketing domain.", suffix="authorization")
    authorization = _authorization(validation, suffix="authorization")

    assert authorization["artifact_type"] == BUNDLE_MUTATION_AUTHORIZATION
    assert authorization["bundle_id"] == MARKETING_DOMAIN_BUNDLE_ID
    assert [item["path"] for item in authorization["artifacts"]] == list(BUNDLE_PATHS)
    assert [item["artifact_type"] for item in authorization["artifacts"]] == [
        BUNDLE_ARTIFACT_TYPES[path] for path in BUNDLE_PATHS
    ]
    assert all(item["permission"] == "CREATE_ONLY" for item in authorization["artifacts"])
    assert all(item["overwrite_permitted"] is False for item in authorization["artifacts"])


def test_bundle_replay_records_required_artifacts(tmp_path) -> None:
    _create(tmp_path, suffix="events")
    replay_dir = tmp_path / "domain_bundle_events"

    assert (replay_dir / "000_bundle_authorization_recorded.json").exists()
    assert (replay_dir / "001_bundle_creation_evidence_recorded.json").exists()
    assert (replay_dir / "002_per_artifact_verification_recorded.json").exists()
    assert (replay_dir / "003_bundle_verification_result_recorded.json").exists()


def test_existing_artifact_fails_before_any_bundle_member_is_created(tmp_path) -> None:
    validation = _validate(tmp_path, prompt="Create a marketing domain.", suffix="existing")
    authorization = _authorization(validation, suffix="existing")
    workspace = _workspace(tmp_path)
    existing = workspace / BUNDLE_PATHS[0]
    existing.write_text("existing\n", encoding="utf-8")

    result = create_marketing_domain_bundle(
        domain_bundle_runtime_id="DOMAIN-BUNDLE-existing",
        worker_result_validation_artifact=validation["worker_result_validation_artifact"],
        worker_result_validation_replay_reference=validation["worker_result_validation_replay_reference"],
        bundle_mutation_authorization_artifact=authorization,
        workspace_root=workspace,
        created_by="AIGOL_GOVERNANCE",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "domain_bundle_existing",
    )

    assert result["bundle_verification_status"] == "FAILED_CLOSED"
    assert result["partial_completion"] is False
    assert existing.read_text(encoding="utf-8") == "existing\n"
    assert not (workspace / BUNDLE_PATHS[1]).exists()
    assert not (workspace / BUNDLE_PATHS[2]).exists()


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"bundle_id": "OTHER-BUNDLE"}, "bundle id"),
        ({"permission": "OVERWRITE"}, "create-only"),
        ({"overwrite_permitted": True}, "overwrite_permitted"),
        ({"chain_id": "OTHER-CHAIN"}, "chain"),
        ({"artifacts": []}, "artifact list"),
    ],
)
def test_bundle_fails_closed_on_authorization_drift(tmp_path, changes: dict, reason: str) -> None:
    suffix = reason.replace(" ", "-")
    validation = _validate(tmp_path, prompt="Create a marketing domain.", suffix=suffix)
    authorization = _rehash({**_authorization(validation, suffix=suffix), **changes})

    result = _create(tmp_path, suffix=suffix, validation=validation, authorization=authorization)

    assert result["bundle_verification_status"] == "FAILED_CLOSED"
    assert reason in result["failure_reason"]
    assert all(not (tmp_path / "workspace" / path).exists() for path in BUNDLE_PATHS)


def test_bundle_reconstruction_detects_artifact_content_mismatch(tmp_path) -> None:
    _create(tmp_path, suffix="content-mismatch")
    (tmp_path / "workspace" / BUNDLE_PATHS[1]).write_text("corrupted\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="artifact mismatch"):
        reconstruct_multi_artifact_domain_bundle_replay(tmp_path / "domain_bundle_content-mismatch")


def test_bundle_reconstruction_detects_replay_hash_mismatch(tmp_path) -> None:
    _create(tmp_path, suffix="replay-mismatch")
    path = tmp_path / "domain_bundle_replay-mismatch" / "003_bundle_verification_result_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["bundle_id"] = "CORRUPTED"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_multi_artifact_domain_bundle_replay(tmp_path / "domain_bundle_replay-mismatch")


def test_bundle_runtime_has_no_delete_rename_move_or_directory_creation() -> None:
    source = inspect.getsource(create_marketing_domain_bundle)

    assert ".unlink(" not in source
    assert ".rename(" not in source
    assert ".replace(" not in source
    assert ".mkdir(" not in source
    assert "open(\"x\"" in source


def test_interactive_cli_routes_marketing_domain_to_executable_bundle(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _args(tmp_path, session_id="SESSION-CLI-MULTI-ARTIFACT-DOMAIN-BUNDLE-000001"),
        input_func=_input_sequence(["Create a marketing domain.", "exit"]),
        output_func=output.append,
    )

    assert result["executable_bundle_authorized"] is True
    assert result["artifacts_created"] is True
    assert result["executable_bundle_verified"] is True
    assert result["post_execution_replay_reviewed"] is True
    assert result["terminated"] is True
    assert all(
        (tmp_path / path).read_text(encoding="utf-8") == EXECUTABLE_BUNDLE_CONTENTS[path]
        for path in EXECUTABLE_BUNDLE_PATHS
    )
    assert any("Executable Bundle Authorization Status: EXECUTABLE_BUNDLE_AUTHORIZED" in chunk for chunk in output)
    assert any("Artifact Creation Status: ARTIFACTS_CREATED" in chunk for chunk in output)
    assert any("Executable Bundle Verification Status: EXECUTABLE_BUNDLE_VERIFIED" in chunk for chunk in output)
