"""Tests for AIGOL_REAL_OUTPUT_BINDING_RUNTIME_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect
import json

import pytest

from aigol.cli.aigol_cli import run_interactive_conversation
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.multi_artifact_domain_bundle_runtime import (
    BUNDLE_CONTENTS,
    BUNDLE_PATHS,
)
from aigol.runtime.real_output_binding_runtime import (
    ARTIFACT_CREATED,
    ARTIFACT_VERIFIED,
    EXACT_OUTPUT_MUTATION_AUTHORIZATION,
    GOVERNANCE_DOCUMENT_MARKDOWN,
    OUTPUT_BOUND,
    REAL_OUTPUT_BINDING_ARTIFACT_V1,
    TARGET_CONTENT,
    TARGET_PATH,
    bind_validated_output,
    create_exact_output_mutation_authorization,
    reconstruct_real_output_binding_replay,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash
from test_worker_result_validation_runtime_v1 import CREATED_AT, _args, _input_sequence, _validate


def _workspace(tmp_path):
    workspace = tmp_path / "workspace"
    (workspace / "governance").mkdir(parents=True)
    return workspace


def _authorization(validation: dict, *, suffix: str) -> dict:
    return create_exact_output_mutation_authorization(
        mutation_authorization_id=f"EXACT-OUTPUT-MUTATION-AUTHORIZATION-{suffix}",
        worker_result_validation_artifact=validation["worker_result_validation_artifact"],
        target_path=TARGET_PATH,
        artifact_type=GOVERNANCE_DOCUMENT_MARKDOWN,
        authorized_by="AIGOL_GOVERNANCE",
        authorized_at=CREATED_AT,
    )


def _bind(tmp_path, *, suffix: str, validation: dict | None = None, authorization: dict | None = None) -> dict:
    if validation is None:
        validation = _validate(tmp_path, prompt="Create a marketing domain.", suffix=suffix)
    if authorization is None:
        authorization = _authorization(validation, suffix=suffix)
    return bind_validated_output(
        real_output_binding_id=f"REAL-OUTPUT-BINDING-{suffix}",
        worker_result_validation_artifact=validation["worker_result_validation_artifact"],
        worker_result_validation_replay_reference=validation["worker_result_validation_replay_reference"],
        mutation_authorization_artifact=authorization,
        workspace_root=_workspace(tmp_path),
        bound_by="AIGOL_GOVERNANCE",
        bound_at=CREATED_AT,
        replay_dir=tmp_path / f"real_output_binding_{suffix}",
    )


def _rehash(artifact: dict) -> dict:
    artifact = deepcopy(artifact)
    artifact.pop("artifact_hash", None)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def test_result_validated_becomes_real_artifact_created_and_verified(tmp_path) -> None:
    result = _bind(tmp_path, suffix="success")
    artifact = result["real_output_binding_artifact"]
    target = tmp_path / "workspace" / TARGET_PATH
    reconstructed = reconstruct_real_output_binding_replay(tmp_path / "real_output_binding_success")

    assert result["output_binding_status"] == OUTPUT_BOUND
    assert result["artifact_creation_status"] == ARTIFACT_CREATED
    assert result["verification_status"] == ARTIFACT_VERIFIED
    assert artifact["artifact_type"] == REAL_OUTPUT_BINDING_ARTIFACT_V1
    assert artifact["target_path"] == TARGET_PATH
    assert artifact["target_artifact_type"] == GOVERNANCE_DOCUMENT_MARKDOWN
    assert artifact["overwrite_permitted"] is False
    assert target.read_text(encoding="utf-8") == TARGET_CONTENT
    assert reconstructed["verification_status"] == ARTIFACT_VERIFIED
    assert reconstructed["content_hash"] == replay_hash(TARGET_CONTENT)


def test_exact_output_mutation_authorization_is_narrow(tmp_path) -> None:
    validation = _validate(tmp_path, prompt="Create a marketing domain.", suffix="authorization")
    authorization = _authorization(validation, suffix="authorization")

    assert authorization["artifact_type"] == EXACT_OUTPUT_MUTATION_AUTHORIZATION
    assert authorization["target_path"] == TARGET_PATH
    assert authorization["target_artifact_type"] == GOVERNANCE_DOCUMENT_MARKDOWN
    assert authorization["permission"] == "CREATE_ONLY"
    assert authorization["overwrite_permitted"] is False
    assert authorization["directory_creation_permitted"] is False
    assert authorization["recursive_creation_permitted"] is False
    assert authorization["authority_transferable"] is False


def test_real_output_binding_persists_required_replay_events(tmp_path) -> None:
    _bind(tmp_path, suffix="events")
    replay_dir = tmp_path / "real_output_binding_events"

    assert (replay_dir / "000_mutation_authorization_recorded.json").exists()
    assert (replay_dir / "001_output_binding_evidence_recorded.json").exists()
    assert (replay_dir / "002_output_binding_artifact_recorded.json").exists()
    assert (replay_dir / "003_artifact_verification_result_recorded.json").exists()


def test_real_output_binding_fails_closed_without_authorization(tmp_path) -> None:
    validation = _validate(tmp_path, prompt="Create a marketing domain.", suffix="missing-auth")

    result = _bind(tmp_path, suffix="missing-auth", validation=validation, authorization={})

    assert result["verification_status"] == "FAILED_CLOSED"
    assert result["real_output_binding_artifact"] is None
    assert "exact output mutation authorization required" in result["failure_reason"]


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"target_path": "governance/OTHER.md"}, "unauthorized path"),
        ({"target_artifact_type": "RUNTIME_FILE"}, "artifact type"),
        ({"permission": "OVERWRITE"}, "create-only"),
        ({"overwrite_permitted": True}, "overwrite_permitted"),
        ({"content_hash": "sha256:invalid"}, "content hash"),
        ({"chain_id": "OTHER-CHAIN"}, "chain"),
    ],
)
def test_real_output_binding_fails_closed_on_authorization_drift(tmp_path, changes: dict, reason: str) -> None:
    suffix = reason.replace(" ", "-")
    validation = _validate(tmp_path, prompt="Create a marketing domain.", suffix=suffix)
    authorization = _rehash({**_authorization(validation, suffix=suffix), **changes})

    result = _bind(tmp_path, suffix=suffix, validation=validation, authorization=authorization)

    assert result["verification_status"] == "FAILED_CLOSED"
    assert result["real_output_binding_artifact"] is None
    assert reason in result["failure_reason"]


def test_real_output_binding_fails_closed_when_target_exists(tmp_path) -> None:
    validation = _validate(tmp_path, prompt="Create a marketing domain.", suffix="exists")
    authorization = _authorization(validation, suffix="exists")
    workspace = _workspace(tmp_path)
    target = workspace / TARGET_PATH
    target.write_text("existing\n", encoding="utf-8")

    result = bind_validated_output(
        real_output_binding_id="REAL-OUTPUT-BINDING-exists",
        worker_result_validation_artifact=validation["worker_result_validation_artifact"],
        worker_result_validation_replay_reference=validation["worker_result_validation_replay_reference"],
        mutation_authorization_artifact=authorization,
        workspace_root=workspace,
        bound_by="AIGOL_GOVERNANCE",
        bound_at=CREATED_AT,
        replay_dir=tmp_path / "real_output_binding_exists",
    )

    assert result["verification_status"] == "FAILED_CLOSED"
    assert target.read_text(encoding="utf-8") == "existing\n"
    assert "target already exists" in result["failure_reason"]


def test_real_output_binding_fails_closed_without_governance_directory(tmp_path) -> None:
    validation = _validate(tmp_path, prompt="Create a marketing domain.", suffix="no-directory")
    authorization = _authorization(validation, suffix="no-directory")
    workspace = tmp_path / "empty-workspace"
    workspace.mkdir()

    result = bind_validated_output(
        real_output_binding_id="REAL-OUTPUT-BINDING-no-directory",
        worker_result_validation_artifact=validation["worker_result_validation_artifact"],
        worker_result_validation_replay_reference=validation["worker_result_validation_replay_reference"],
        mutation_authorization_artifact=authorization,
        workspace_root=workspace,
        bound_by="AIGOL_GOVERNANCE",
        bound_at=CREATED_AT,
        replay_dir=tmp_path / "real_output_binding_no_directory",
    )

    assert result["verification_status"] == "FAILED_CLOSED"
    assert "governance directory missing" in result["failure_reason"]


def test_real_output_binding_reconstruction_detects_verification_mismatch(tmp_path) -> None:
    _bind(tmp_path, suffix="reconstruct")
    path = tmp_path / "real_output_binding_reconstruct" / "003_artifact_verification_result_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["content_hash"] = "sha256:corrupted"
    wrapper["artifact"] = _rehash(wrapper["artifact"])
    wrapper.pop("replay_hash", None)
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="content hash mismatch"):
        reconstruct_real_output_binding_replay(tmp_path / "real_output_binding_reconstruct")


def test_real_output_binding_reconstruction_detects_missing_created_artifact(tmp_path) -> None:
    _bind(tmp_path, suffix="missing-created-artifact")
    (tmp_path / "workspace" / TARGET_PATH).unlink()

    with pytest.raises(FailClosedRuntimeError, match="artifact missing"):
        reconstruct_real_output_binding_replay(tmp_path / "real_output_binding_missing-created-artifact")


def test_real_output_binding_runtime_has_no_delete_rename_move_or_directory_creation() -> None:
    source = inspect.getsource(bind_validated_output)

    assert ".unlink(" not in source
    assert ".rename(" not in source
    assert ".replace(" not in source
    assert ".mkdir(" not in source
    assert "open(\"x\"" in source


def test_interactive_cli_routes_marketing_domain_to_bundle_runtime(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _args(tmp_path, session_id="SESSION-CLI-REAL-OUTPUT-BINDING-000001"),
        input_func=_input_sequence(["Create a marketing domain.", "exit"]),
        output_func=output.append,
    )

    assert result["bundle_authorized"] is True
    assert result["artifacts_created"] is True
    assert result["bundle_verified"] is True
    assert result["post_execution_replay_reviewed"] is True
    assert result["terminated"] is True
    assert all((tmp_path / path).read_text(encoding="utf-8") == BUNDLE_CONTENTS[path] for path in BUNDLE_PATHS)
    assert any("Bundle Authorization Status: BUNDLE_AUTHORIZED" in chunk for chunk in output)
    assert any("Artifact Creation Status: ARTIFACTS_CREATED" in chunk for chunk in output)
    assert any("Bundle Verification Status: BUNDLE_VERIFIED" in chunk for chunk in output)
