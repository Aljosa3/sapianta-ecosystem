"""Tests for AIGOL_REPOSITORY_MUTATION_WORKER_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from aigol.runtime.repository_mutation_worker_runtime import (
    FAILED_CLOSED,
    PATCH_PROPOSAL_ARTIFACT_V1,
    REPOSITORY_MUTATION_ARTIFACT_V1,
    REPOSITORY_MUTATION_COMPLETED,
    apply_repository_mutation,
    create_patch_proposal_artifact,
    reconstruct_repository_mutation_replay,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash
from aigol.runtime.validation_command_runner_runtime import (
    VALIDATION_COMMAND_COMPLETED,
    create_validation_command_request,
    execute_validation_command,
)


CREATED_AT = "2026-06-12T00:00:00Z"


def _mutation(target_path: str, new_content: str) -> dict:
    return {
        "target_path": target_path,
        "operation": "CREATE_OR_REPLACE",
        "new_content": new_content,
        "new_content_hash": replay_hash(new_content),
        "approved": True,
    }


def _proposal(file_mutations: list[dict]) -> dict:
    return create_patch_proposal_artifact(
        proposal_id="PATCH-PROPOSAL-REPOSITORY-MUTATION-000001",
        file_mutations=file_mutations,
        replay_references=["replay/repository-mutation-proposal.json"],
        replay_hashes=[replay_hash({"proposal": "repository-mutation"})],
        authorization_references=["HUMAN-AUTHORIZATION-REPOSITORY-MUTATION-000001"],
        created_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
    )


def test_repository_mutation_worker_applies_approved_patch_and_generates_artifact(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    target = repo / "aigol/runtime/generated_validation_worker.py"
    new_content = "def status():\n    return 'ok'\n"
    proposal = _proposal([_mutation("aigol/runtime/generated_validation_worker.py", new_content)])
    capture = apply_repository_mutation(
        mutation_id="REPOSITORY-MUTATION-000001",
        source_artifact=proposal,
        target_root=repo,
        mutated_by="AIGOL_REPOSITORY_MUTATION_WORKER",
        mutated_at=CREATED_AT,
        replay_dir=tmp_path / "mutation_replay",
    )
    artifact = capture["repository_mutation_artifact"]
    reconstructed = reconstruct_repository_mutation_replay(tmp_path / "mutation_replay")

    assert proposal["artifact_type"] == PATCH_PROPOSAL_ARTIFACT_V1
    assert capture["mutation_status"] == REPOSITORY_MUTATION_COMPLETED
    assert capture["repository_mutation_worker_implemented"] is True
    assert capture["repository_mutation_artifact_generated"] is True
    assert capture["replay_lineage_preserved"] is True
    assert capture["unauthorized_mutation_prevented"] is True
    assert capture["fail_closed_preserved"] is True
    assert artifact["artifact_type"] == REPOSITORY_MUTATION_ARTIFACT_V1
    assert artifact["source_artifact_id"] == proposal["proposal_id"]
    assert artifact["mutated_files"] == ["aigol/runtime/generated_validation_worker.py"]
    assert artifact["before_hashes"]["aigol/runtime/generated_validation_worker.py"] is None
    assert artifact["after_hashes"]["aigol/runtime/generated_validation_worker.py"] == replay_hash(new_content)
    assert artifact["mutation_results"][0]["before_content_snapshot"] is None
    assert artifact["mutation_results"][0]["after_content_snapshot"] == new_content
    assert artifact["governance_artifacts_modified"] is False
    assert artifact["replay_artifacts_modified"] is False
    assert artifact["provider_invoked"] is False
    assert artifact["arbitrary_shell_executed"] is False
    assert target.read_text(encoding="utf-8") == new_content
    assert reconstructed["mutation_status"] == REPOSITORY_MUTATION_COMPLETED
    assert reconstructed["replay_lineage_preserved"] is True
    assert reconstructed["ready_for_governed_repository_changes"] is True


def test_repository_mutation_worker_preserves_before_snapshot_on_update(tmp_path) -> None:
    repo = tmp_path / "repo"
    target = repo / "aigol/runtime/existing_worker.py"
    target.parent.mkdir(parents=True)
    before = "def status():\n    return 'old'\n"
    after = "def status():\n    return 'new'\n"
    target.write_text(before, encoding="utf-8")
    proposal = _proposal([_mutation("aigol/runtime/existing_worker.py", after)])
    capture = apply_repository_mutation(
        mutation_id="REPOSITORY-MUTATION-UPDATE-000001",
        source_artifact=proposal,
        target_root=repo,
        mutated_by="AIGOL_REPOSITORY_MUTATION_WORKER",
        mutated_at=CREATED_AT,
        replay_dir=tmp_path / "update_replay",
    )
    result = capture["repository_mutation_artifact"]["mutation_results"][0]

    assert result["before_hash"] == replay_hash(before)
    assert result["after_hash"] == replay_hash(after)
    assert result["before_content_snapshot"] == before
    assert target.read_text(encoding="utf-8") == after


def test_repository_mutation_worker_prevents_governance_artifact_mutation(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    with pytest.raises(Exception, match="target path is not authorized"):
        _proposal([_mutation(".github/governance/review/unsafe.json", "{}\n")])


def test_repository_mutation_worker_fails_closed_for_unapproved_mutation(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    mutation = _mutation("aigol/runtime/not_approved.py", "VALUE = 1\n")
    mutation["approved"] = False
    with pytest.raises(Exception, match="file mutation not approved"):
        _proposal([mutation])


def test_repository_mutation_worker_fails_closed_without_mutating_outside_scope(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    artifact = {
        "artifact_type": PATCH_PROPOSAL_ARTIFACT_V1,
        "runtime_version": "AIGOL_REPOSITORY_MUTATION_WORKER_RUNTIME_V1",
        "proposal_id": "PATCH-PROPOSAL-UNAUTHORIZED-PATH",
        "certification_status": "CERTIFIED_PATCH_PROPOSAL",
        "authorization_scope": "APPLY_APPROVED_FILE_MUTATIONS_ONLY",
        "human_approval_required": True,
        "human_approval_granted": True,
        "repository_mutation_scope": {
            "allowed_operations": ["CREATE_OR_REPLACE", "REPLACE_CONTENT"],
            "allowed_target_paths": ["../escape.py"],
            "forbidden_target_prefixes": [".github/governance/"],
            "governance_artifact_mutation_allowed": False,
            "replay_artifact_mutation_allowed": False,
        },
        "file_mutations": [
            {
                "target_path": "../escape.py",
                "operation": "CREATE_OR_REPLACE",
                "new_content": "VALUE = 1\n",
                "new_content_hash": replay_hash("VALUE = 1\n"),
                "approved": True,
            }
        ],
        "file_mutation_count": 1,
        "replay_references": ["replay/bad.json"],
        "replay_hashes": [replay_hash({"bad": True})],
        "authorization_references": ["HUMAN-AUTH"],
        "created_by": "HUMAN_OPERATOR",
        "created_at": CREATED_AT,
        "replay_lineage_preserved": True,
        "fail_closed_preserved": True,
        "provider_invocation_allowed": False,
        "command_execution_allowed": False,
        "replay_visible": True,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    capture = apply_repository_mutation(
        mutation_id="REPOSITORY-MUTATION-BLOCKED-000001",
        source_artifact=artifact,
        target_root=repo,
        mutated_by="AIGOL_REPOSITORY_MUTATION_WORKER",
        mutated_at=CREATED_AT,
        replay_dir=tmp_path / "blocked_replay",
    )

    assert capture["mutation_status"] == FAILED_CLOSED
    assert capture["repository_mutation_artifact"]["mutated_files"] == []
    assert capture["unauthorized_mutation_prevented"] is True
    assert capture["fail_closed_preserved"] is True
    assert not (tmp_path / "escape.py").exists()


def test_repository_mutation_to_validation_command_path(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    target_path = "aigol/runtime/generated_validation_worker.py"
    new_content = "def status():\n    return 'ok'\n"
    proposal = _proposal([_mutation(target_path, new_content)])
    mutation = apply_repository_mutation(
        mutation_id="REPOSITORY-MUTATION-VALIDATION-000001",
        source_artifact=proposal,
        target_root=repo,
        mutated_by="AIGOL_REPOSITORY_MUTATION_WORKER",
        mutated_at=CREATED_AT,
        replay_dir=tmp_path / "validation_mutation_replay",
    )["repository_mutation_artifact"]
    request = create_validation_command_request(
        request_id="VALIDATION-COMMAND-REQUEST-REPOSITORY-MUTATION-000001",
        command=["python", "-m", "py_compile", str(repo / target_path)],
        cwd=str(repo),
        requested_by="HUMAN_OPERATOR",
        requested_at=CREATED_AT,
        replay_references=[str(tmp_path / "validation_mutation_replay")],
        replay_hashes=[mutation["artifact_hash"]],
        timeout_seconds=30,
    )
    validation = execute_validation_command(
        request_artifact=request,
        executed_by="AIGOL_VALIDATION_COMMAND_RUNNER",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "validation_command_replay",
    )

    assert validation["command_status"] == VALIDATION_COMMAND_COMPLETED
    assert validation["validation_command_result_artifact"]["exit_code"] == 0
    assert validation["replay_preserved"] is True


def test_repository_mutation_replay_detects_corruption(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    proposal = _proposal([_mutation("aigol/runtime/corrupt_worker.py", "VALUE = 1\n")])
    apply_repository_mutation(
        mutation_id="REPOSITORY-MUTATION-CORRUPT-000001",
        source_artifact=proposal,
        target_root=repo,
        mutated_by="AIGOL_REPOSITORY_MUTATION_WORKER",
        mutated_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt_replay",
    )
    path = tmp_path / "corrupt_replay" / "001_repository_mutation_artifact_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["provider_invoked"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(Exception, match="hash mismatch"):
        reconstruct_repository_mutation_replay(tmp_path / "corrupt_replay")


def test_repository_mutation_worker_has_no_provider_or_shell_execution_surface() -> None:
    import aigol.runtime.repository_mutation_worker_runtime as runtime

    source = inspect.getsource(runtime)

    assert "subprocess." not in source
    assert "os.system" not in source
    assert "invoke_live_external_llm_provider(" not in source
    assert "invoke_worker(" not in source
    assert "execute_worker(" not in source
