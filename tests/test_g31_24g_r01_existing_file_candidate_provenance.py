from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import subprocess

import pytest

from aigol.runtime import generated_content_acceptance_runtime as acceptance
from aigol.runtime import human_decision_runtime as decision
from aigol.runtime import platform_core_existing_file_mutation_candidate as candidate
from aigol.runtime import codex_worker_activation_binding_runtime as worker_activation
from aigol.runtime.models import FailClosedRuntimeError
import test_g31_24d_r02_aicli_task_outcome_to_disposable_review_binding as r02


@pytest.fixture(autouse=True)
def _git_workspace(monkeypatch: pytest.MonkeyPatch):
    original = r02._workspace

    def workspace(*args, **kwargs):
        result = original(*args, **kwargs)
        for command in (["git", "init"], ["git", "config", "user.name", "G31"],
                        ["git", "config", "user.email", "g31@example.invalid"],
                        ["git", "add", "aigol/runtime/human_interface.py", "tests/test_human_interface.py"],
                        ["git", "commit", "-m", "baseline"]):
            subprocess.run(command, cwd=result, check=True, capture_output=True, text=True)
        return result

    monkeypatch.setattr(r02, "_workspace", workspace)


def _accepted(tmp_path: Path, name: str = "G31-24G"):
    result, _, root, source, runner = r02._run(tmp_path, name, ["/satisfied", "/approve"])
    runtime = result["runtime_result"]
    binding = runtime["codex_replacement_acceptance_prerequisite_binding_capture"]
    content = decision.record_content_acceptance_decision(
        context_capture=runtime["human_content_acceptance_context_capture"], binding_capture=binding,
        decision_outcome=decision.ACCEPTED, decided_by="HUMAN_OPERATOR_VIA_AICLI",
        decided_at=r02.CREATED_AT, session_root=root)
    accepted = acceptance.accept_generated_content_from_content_acceptance_decision(
        acceptance_id=f"{name}-ACCEPTANCE", decision_capture=content, binding_capture=binding,
        created_at=r02.CREATED_AT, session_root=root, replay_dir=root / "ACCEPTANCE")
    activation = worker_activation.reconstruct_codex_worker_activation_binding(
        activation_capture=runtime["codex_worker_activation_capture"],
        governed_execution_capture=runtime["governed_worker_execution_capture"],
        execution_candidate_capture=runtime["worker_execution_candidate_capture"],
        session_root=root, workspace=source)
    grounding = activation["lineage"]["grounding"]
    return accepted, content, binding, grounding, root, source, runner


def test_exact_accepted_result_creates_and_reconstructs_v2_candidate(tmp_path: Path) -> None:
    accepted, content, binding, grounding, root, source, runner = _accepted(tmp_path)
    before = sha256((source / "aigol/runtime/human_interface.py").read_bytes()).hexdigest()
    capture = candidate.create_g31_accepted_existing_file_mutation_candidate(
        candidate_id="G31-24G-CANDIDATE", acceptance_capture=accepted, decision_capture=content,
        binding_capture=binding, repository_grounding_artifact=grounding, session_root=root,
        created_by="HUMAN_OPERATOR_VIA_AICLI", created_at=r02.CREATED_AT, replay_dir=root / "CANDIDATE")
    reconstructed = candidate.reconstruct_g31_accepted_existing_file_mutation_candidate_replay(
        candidate_capture=capture, acceptance_capture=accepted, decision_capture=content,
        binding_capture=binding, repository_grounding_artifact=grounding, session_root=root)
    artifact = capture["existing_file_mutation_candidate_artifact"]
    assert artifact["artifact_type"] == candidate.EXISTING_FILE_MUTATION_CANDIDATE_ARTIFACT_V2
    assert reconstructed["replay_artifact_count"] == 3
    assert capture["result_accepted"] is True
    assert capture["human_mutation_decision_recorded"] is False
    assert capture["mutation_authorized"] is False
    assert capture["main_repository_mutated"] is False
    assert "No human mutation decision" in candidate.render_g31_accepted_existing_file_mutation_candidate(capture)
    assert len(runner.calls) == 1
    assert sha256((source / "aigol/runtime/human_interface.py").read_bytes()).hexdigest() == before
    assert subprocess.run(["git", "status", "--short"], cwd=source, check=True, capture_output=True, text=True).stdout == ""


def test_candidate_fails_closed_on_lineage_tamper_and_reuse(tmp_path: Path) -> None:
    accepted, content, binding, grounding, root, _, _ = _accepted(tmp_path, "G31-24G-TAMPER")
    args = dict(candidate_id="G31-24G-CANDIDATE", acceptance_capture=accepted, decision_capture=content,
                binding_capture=binding, repository_grounding_artifact=grounding, session_root=root,
                created_by="HUMAN_OPERATOR", created_at=r02.CREATED_AT)
    changed = deepcopy(binding)
    changed["implementation_manifest_capture"]["implementation_manifest_artifact"]["file_entries"][0]["postimage_sha256"] = "sha256:" + "0" * 64
    with pytest.raises(FailClosedRuntimeError):
        candidate.create_g31_accepted_existing_file_mutation_candidate(replay_dir=root / "TAMPER", binding_capture=changed, **{k: v for k, v in args.items() if k != "binding_capture"})
    capture = candidate.create_g31_accepted_existing_file_mutation_candidate(replay_dir=root / "CANDIDATE", **args)
    with pytest.raises(FailClosedRuntimeError, match="destination already exists"):
        candidate.create_g31_accepted_existing_file_mutation_candidate(replay_dir=root / "CANDIDATE", **args)
    with pytest.raises(FailClosedRuntimeError, match="already consumed"):
        candidate.create_g31_accepted_existing_file_mutation_candidate(replay_dir=root / "SECOND", **args)
    changed_capture = deepcopy(capture)
    changed_capture["existing_file_mutation_candidate_artifact"]["target_path"] = "substituted.py"
    with pytest.raises(FailClosedRuntimeError):
        candidate.reconstruct_g31_accepted_existing_file_mutation_candidate_replay(
            candidate_capture=changed_capture, acceptance_capture=accepted, decision_capture=content,
            binding_capture=binding, repository_grounding_artifact=grounding, session_root=root)


def test_aicli_transports_candidate_after_acceptance_without_authorization(tmp_path: Path) -> None:
    result, output, root, source, runner = r02._run(tmp_path, "G31-24G-AICLI", ["/satisfied", "/approve", "/accept"])
    runtime = result["runtime_result"]
    capture = runtime["existing_file_mutation_candidate_capture"]
    assert "lineage" not in runtime["codex_worker_activation_capture"]
    assert result["exit_reason"] == "GENERATED_CONTENT_ACCEPTANCE_RECORDED"
    assert runtime["result_accepted"] is True
    assert runtime["existing_file_mutation_candidate_created"] is True
    assert runtime["human_mutation_decision_recorded"] is False
    assert runtime["mutation_authorized"] is False
    assert runtime["main_repository_mutated"] is False
    assert candidate.reconstruct_g31_accepted_existing_file_mutation_candidate_replay(
        candidate_capture=capture, acceptance_capture=runtime["generated_content_acceptance_capture"],
        decision_capture=runtime["human_content_acceptance_decision_capture"],
        binding_capture=runtime["codex_replacement_acceptance_prerequisite_binding_capture"],
        repository_grounding_artifact=worker_activation.reconstruct_codex_worker_activation_binding(
            activation_capture=runtime["codex_worker_activation_capture"],
            governed_execution_capture=runtime["governed_worker_execution_capture"],
            execution_candidate_capture=runtime["worker_execution_candidate_capture"],
            session_root=root, workspace=source)["lineage"]["grounding"],
        session_root=root)["replay_artifact_count"] == 3
    assert "Existing-File Mutation Candidate" in "\n".join(output)
    assert len(runner.calls) == 1
    assert subprocess.run(["git", "status", "--short"], cwd=source, check=True, capture_output=True, text=True).stdout == ""


def test_aicli_fails_closed_before_candidate_if_activation_reconstruction_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    def failed_reconstruction(**_kwargs):
        raise FailClosedRuntimeError("activation reconstruction failed closed")

    monkeypatch.setattr(r02.aicli.worker_activation, "reconstruct_codex_worker_activation_binding", failed_reconstruction)
    with pytest.raises(FailClosedRuntimeError, match="activation reconstruction failed closed"):
        r02._run(tmp_path, "G31-24G-AICLI-FAIL-CLOSED", ["/satisfied", "/approve", "/accept"])
