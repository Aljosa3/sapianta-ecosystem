from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import subprocess

import pytest

from aigol.runtime import (
    codex_replacement_acceptance_prerequisite_binding_runtime as prerequisites,
    codex_satisfied_outcome_disposable_validation_binding_runtime as disposable,
    filesystem_mutation_authorization_runtime as mutation_authorization,
    generated_content_acceptance_runtime as acceptance,
    human_decision_runtime as decision,
)
from aigol.runtime.models import FailClosedRuntimeError
import test_g31_24d_r02_aicli_task_outcome_to_disposable_review_binding as r02
from test_human_decision_runtime_v1 import _approval_required, CREATED_AT


@pytest.fixture(autouse=True)
def _git_source_workspace(monkeypatch: pytest.MonkeyPatch):
    original = r02._workspace

    def git_workspace(*args, **kwargs):
        workspace = original(*args, **kwargs)
        for command in (
            ["git", "init"],
            ["git", "config", "user.name", "G31 24D"],
            ["git", "config", "user.email", "g31-24d@example.invalid"],
            ["git", "add", "aigol/runtime/human_interface.py", "tests/test_human_interface.py"],
            ["git", "commit", "-m", "fixture baseline"],
        ):
            subprocess.run(command, cwd=workspace, check=True, capture_output=True, text=True)
        return workspace

    monkeypatch.setattr(r02, "_workspace", git_workspace)


def _forbid_downstream(monkeypatch: pytest.MonkeyPatch) -> dict[str, int]:
    calls = {"accept": 0, "authorization": 0}

    def forbidden(name: str):
        def _raise(*_args: object, **_kwargs: object) -> None:
            calls[name] += 1
            raise AssertionError(f"G31-24D must not call {name}")
        return _raise

    monkeypatch.setattr(acceptance, "accept_generated_content", forbidden("accept"))
    monkeypatch.setattr(mutation_authorization, "authorize_filesystem_mutation", forbidden("authorization"))
    return calls


def test_aicli_accept_records_exact_v2_decision_without_downstream(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    downstream = {"accept": 0, "authorization": 0}
    real_accept = acceptance.accept_generated_content

    def accept_once(**kwargs):
        downstream["accept"] += 1
        return real_accept(**kwargs)

    def forbid_authorization(*_args: object, **_kwargs: object) -> None:
        downstream["authorization"] += 1
        raise AssertionError("G31-24E must stop before mutation authorization")

    monkeypatch.setattr(acceptance, "accept_generated_content", accept_once)
    monkeypatch.setattr(mutation_authorization, "authorize_filesystem_mutation", forbid_authorization)
    real_execute = disposable.execute_disposable_patch_validation
    real_command = disposable.execute_validation_command
    real_mutation = disposable.execute_governed_repository_mutation
    real_bind = prerequisites.bind_codex_replacement_acceptance_prerequisites
    calls = {"execute": 0, "command": 0, "patch": 0, "binder": 0}

    def counted(name: str, owner):
        def _call(**kwargs):
            calls[name] += 1
            return owner(**kwargs)
        return _call

    monkeypatch.setattr(disposable, "execute_disposable_patch_validation", counted("execute", real_execute))
    monkeypatch.setattr(disposable, "execute_validation_command", counted("command", real_command))
    monkeypatch.setattr(disposable, "execute_governed_repository_mutation", counted("patch", real_mutation))
    monkeypatch.setattr(prerequisites, "bind_codex_replacement_acceptance_prerequisites", counted("binder", real_bind))
    result, output, _, source, runner = r02._run(
        tmp_path, "G31-24D-ACCEPT", ["/satisfied", "/approve", "/accept"]
    )
    runtime = result["runtime_result"]
    capture = runtime["human_content_acceptance_decision_capture"]
    artifact = capture["human_decision_artifact"]
    reconstructed = runtime["human_content_acceptance_decision_reconstruction"]
    context = capture["content_acceptance_context_artifact"]
    subject = context["subject_binding"]

    assert result["exit_reason"] == "GENERATED_CONTENT_ACCEPTANCE_RECORDED"
    assert artifact["artifact_type"] == decision.HUMAN_DECISION_ARTIFACT_V2
    assert artifact["decision_type"] == decision.CONTENT_ACCEPTANCE
    assert artifact["decision_scope"] == decision.CONTENT_ACCEPTANCE_ONLY
    assert artifact["decision_outcome"] == decision.ACCEPTED
    assert reconstructed["decision_outcome"] == decision.ACCEPTED
    assert reconstructed["replay_artifact_count"] == 4
    assert subject["binding_hash"] == runtime[
        "codex_replacement_acceptance_prerequisite_binding_capture"
    ]["binding_artifact"]["artifact_hash"]
    assert subject["operation_mode"] == "REPLACE_CONTENT"
    assert subject["replacement_files"][0]["preimage_sha256"].startswith("sha256:")
    assert subject["replacement_files"][0]["postimage_sha256"].startswith("sha256:")
    assert runtime["result_accepted"] is True
    assert runtime["mutation_authorized"] is False
    assert runtime["main_repository_mutated"] is False
    assert calls == {"execute": 1, "command": 1, "patch": 1, "binder": 1}
    assert downstream == {"accept": 1, "authorization": 0}
    assert runtime["generated_content_acceptance_reconstruction"]["result_accepted"] is True
    assert len(runner.calls) == 1
    assert subprocess.run(
        ["git", "status", "--short"], cwd=source, check=True, capture_output=True, text=True
    ).stdout == ""
    rendered = "\n".join(output)
    assert "Human Content-Acceptance Decision Required" in rendered
    assert "Decision Outcome: ACCEPTED" in rendered
    assert "Generated Content Accepted" in rendered
    assert "Result Accepted: True" in rendered


def test_aicli_reject_records_v2_rejected_and_never_accepts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    downstream = _forbid_downstream(monkeypatch)
    result, output, _, source, _ = r02._run(
        tmp_path, "G31-24D-REJECT", ["/satisfied", "/approve", "/reject"]
    )
    runtime = result["runtime_result"]
    capture = runtime["human_content_acceptance_decision_capture"]
    reconstructed = decision.reconstruct_content_acceptance_decision_replay(
        decision_capture=capture,
        binding_capture=runtime["codex_replacement_acceptance_prerequisite_binding_capture"],
        session_root=Path(capture["human_decision_replay_reference"]).parent,
    )
    assert capture["decision_outcome"] == decision.REJECTED
    assert reconstructed["decision_outcome"] == decision.REJECTED
    assert reconstructed["result_accepted"] is False
    assert downstream == {"accept": 0, "authorization": 0}
    assert "Decision Outcome: REJECTED" in "\n".join(output)
    assert subprocess.run(
        ["git", "status", "--short"], cwd=source, check=True, capture_output=True, text=True
    ).stdout == ""


def test_generic_response_is_not_content_acceptance(
    tmp_path: Path,
) -> None:
    result, output, _, _, _ = r02._run(
        tmp_path, "G31-24D-GENERIC", ["/satisfied", "/approve", "/approve"]
    )
    runtime = result["runtime_result"]
    context = runtime["human_content_acceptance_context_capture"]
    assert result["exit_reason"] == "EOF_AWAITING_CONTENT_ACCEPTANCE_DECISION"
    assert "human_content_acceptance_decision_capture" not in runtime
    assert not Path(context["human_decision_replay_reference"]).exists()
    assert "accepts only /accept or /reject" in "\n".join(output)


def test_tamper_alias_actor_session_duplicate_and_replay_fail_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    result, _, root, _, _ = r02._run(
        tmp_path, "G31-24D-TAMPER", ["/satisfied", "/approve"]
    )
    runtime = result["runtime_result"]
    context = runtime["human_content_acceptance_context_capture"]
    binding = runtime["codex_replacement_acceptance_prerequisite_binding_capture"]
    replay_path = Path(context["human_decision_replay_reference"])

    for outcome in ("APPROVE", "YES", "SATISFIED"):
        with pytest.raises(FailClosedRuntimeError, match="actor or outcome"):
            decision.record_content_acceptance_decision(
                context_capture=context, binding_capture=binding, decision_outcome=outcome,
                decided_by="HUMAN_OPERATOR_VIA_AICLI", decided_at=CREATED_AT, session_root=root,
            )
    with pytest.raises(FailClosedRuntimeError, match="actor or outcome"):
        decision.record_content_acceptance_decision(
            context_capture=context, binding_capture=binding, decision_outcome=decision.ACCEPTED,
            decided_by="SUBSTITUTED_ACTOR", decided_at=CREATED_AT, session_root=root,
        )
    changed = deepcopy(binding)
    changed["ready_for_acceptance"] = False
    with pytest.raises(FailClosedRuntimeError, match="readiness"):
        decision.record_content_acceptance_decision(
            context_capture=context, binding_capture=changed, decision_outcome=decision.ACCEPTED,
            decided_by="HUMAN_OPERATOR_VIA_AICLI", decided_at=CREATED_AT, session_root=root,
        )
    changed = deepcopy(binding)
    changed["generated_content_validation_capture"]["generated_content_validation_artifact"][
        "validation_status"
    ] = "SUBSTITUTED"
    with pytest.raises(FailClosedRuntimeError):
        decision.record_content_acceptance_decision(
            context_capture=context, binding_capture=changed, decision_outcome=decision.ACCEPTED,
            decided_by="HUMAN_OPERATOR_VIA_AICLI", decided_at=CREATED_AT, session_root=root,
        )
    changed = deepcopy(binding)
    changed["implementation_manifest_capture"]["implementation_manifest_artifact"][
        "file_entries"
    ][0]["postimage_sha256"] = "sha256:" + "0" * 64
    with pytest.raises(FailClosedRuntimeError):
        decision.record_content_acceptance_decision(
            context_capture=context, binding_capture=changed, decision_outcome=decision.ACCEPTED,
            decided_by="HUMAN_OPERATOR_VIA_AICLI", decided_at=CREATED_AT, session_root=root,
        )
    with pytest.raises(FailClosedRuntimeError, match="cross-session"):
        decision.record_content_acceptance_decision(
            context_capture=context, binding_capture=binding, decision_outcome=decision.ACCEPTED,
            decided_by="HUMAN_OPERATOR_VIA_AICLI", decided_at=CREATED_AT,
            session_root=tmp_path / "OTHER-SESSION",
        )
    assert not replay_path.exists()

    stop_calls = {"execute": 0, "command": 0, "patch": 0, "binder": 0, "accept": 0, "authorization": 0}

    def stopped(name: str):
        def _raise(*_args: object, **_kwargs: object) -> None:
            stop_calls[name] += 1
            raise AssertionError(f"V2 decision transition called prohibited owner {name}")
        return _raise

    monkeypatch.setattr(disposable, "execute_disposable_patch_validation", stopped("execute"))
    monkeypatch.setattr(disposable, "execute_validation_command", stopped("command"))
    monkeypatch.setattr(disposable, "execute_governed_repository_mutation", stopped("patch"))
    monkeypatch.setattr(prerequisites, "bind_codex_replacement_acceptance_prerequisites", stopped("binder"))
    monkeypatch.setattr(acceptance, "accept_generated_content", stopped("accept"))
    monkeypatch.setattr(mutation_authorization, "authorize_filesystem_mutation", stopped("authorization"))
    capture = decision.record_content_acceptance_decision(
        context_capture=context, binding_capture=binding, decision_outcome=decision.ACCEPTED,
        decided_by="HUMAN_OPERATOR_VIA_AICLI", decided_at=CREATED_AT, session_root=root,
    )
    assert stop_calls == {"execute": 0, "command": 0, "patch": 0, "binder": 0, "accept": 0, "authorization": 0}
    with pytest.raises(FailClosedRuntimeError, match="destination already exists"):
        decision.record_content_acceptance_decision(
            context_capture=context, binding_capture=binding, decision_outcome=decision.ACCEPTED,
            decided_by="HUMAN_OPERATOR_VIA_AICLI", decided_at=CREATED_AT, session_root=root,
        )
    second_context = decision.prepare_content_acceptance_decision_context(
        context_id="DUPLICATE-SUBJECT", binding_capture=binding,
        human_actor_id="HUMAN_OPERATOR_VIA_AICLI", presented_at=CREATED_AT,
        session_root=root, replay_dir=root / "SECOND-CONTENT-DECISION",
    )
    with pytest.raises(FailClosedRuntimeError, match="subject already decided"):
        decision.record_content_acceptance_decision(
            context_capture=second_context, binding_capture=binding,
            decision_outcome=decision.ACCEPTED, decided_by="HUMAN_OPERATOR_VIA_AICLI",
            decided_at=CREATED_AT, session_root=root,
        )
    substituted = deepcopy(capture)
    substituted["human_decision_replay_reference"] = str(tmp_path / "OTHER-REPLAY")
    with pytest.raises(FailClosedRuntimeError, match="cross-session|No such file"):
        decision.reconstruct_content_acceptance_decision_replay(
            decision_capture=substituted, binding_capture=binding, session_root=root,
        )
    real_load = decision.load_json

    def reordered(path: Path):
        artifact = real_load(path)
        if Path(path).name.startswith("000_"):
            artifact["replay_step"] = "content_acceptance_request_recorded"
        return artifact

    monkeypatch.setattr(decision, "load_json", reordered)
    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        decision.reconstruct_content_acceptance_decision_replay(
            decision_capture=capture, binding_capture=binding, session_root=root,
        )


def test_v1_constructor_and_two_step_replay_remain_unchanged(tmp_path: Path) -> None:
    approval = _approval_required(tmp_path)
    capture = decision.record_human_decision(
        human_decision_id="V1-COMPATIBILITY",
        approval_required_artifact=approval["conversation_to_ppp_handoff_execution_artifact"],
        decision=decision.APPROVE, decision_reason="Preserve V1.",
        decided_by="human.operator", decided_at=CREATED_AT, replay_dir=tmp_path / "v1",
    )
    reconstructed = decision.reconstruct_human_decision_replay(tmp_path / "v1")
    assert capture["artifact_type"] == decision.HUMAN_DECISION_ARTIFACT_V1
    assert capture["decision"] == decision.APPROVE
    assert reconstructed["decision"] == decision.APPROVE
    assert reconstructed["replay_artifact_count"] == 2
    assert decision.normalize_human_decision("YES") == decision.APPROVE
