from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import subprocess

import pytest

from aigol.runtime import (
    codex_replacement_acceptance_prerequisite_binding_runtime as prerequisites,
    codex_satisfied_outcome_disposable_validation_binding_runtime as disposable,
    codex_worker_activation_binding_runtime as worker_activation,
    filesystem_mutation_authorization_runtime as mutation_authorization,
    filesystem_mutation_runtime as filesystem_mutation,
    generated_content_acceptance_runtime as acceptance,
    human_decision_runtime as decision,
    native_provider_execution_runtime as provider_execution,
)
from aigol.runtime.models import FailClosedRuntimeError
import test_g31_24d_r02_aicli_task_outcome_to_disposable_review_binding as r02
from test_generated_content_acceptance_runtime_v1 import _accept, _validated_bundle


@pytest.fixture(autouse=True)
def _git_source_workspace(monkeypatch: pytest.MonkeyPatch):
    original = r02._workspace

    def git_workspace(*args, **kwargs):
        workspace = original(*args, **kwargs)
        for command in (
            ["git", "init"],
            ["git", "config", "user.name", "G31 24E"],
            ["git", "config", "user.email", "g31-24e@example.invalid"],
            ["git", "add", "aigol/runtime/human_interface.py", "tests/test_human_interface.py"],
            ["git", "commit", "-m", "fixture baseline"],
        ):
            subprocess.run(command, cwd=workspace, check=True, capture_output=True, text=True)
        return workspace

    monkeypatch.setattr(r02, "_workspace", git_workspace)


def _decision_ready(tmp_path: Path, session: str, outcome: str):
    result, _, root, source, runner = r02._run(
        tmp_path, session, ["/satisfied", "/approve"]
    )
    runtime = result["runtime_result"]
    context = runtime["human_content_acceptance_context_capture"]
    binding = runtime["codex_replacement_acceptance_prerequisite_binding_capture"]
    capture = decision.record_content_acceptance_decision(
        context_capture=context, binding_capture=binding, decision_outcome=outcome,
        decided_by="HUMAN_OPERATOR", decided_at=r02.CREATED_AT, session_root=root,
    )
    return capture, binding, root, source, runner


def test_exact_v2_accepted_calls_existing_owner_once_and_reconstructs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    capture, binding, root, source, runner = _decision_ready(
        tmp_path, "G31-24E-ACCEPT", decision.ACCEPTED
    )
    source_hash = sha256((source / "aigol/runtime/human_interface.py").read_bytes()).hexdigest()
    real_accept = acceptance.accept_generated_content
    calls = {"accept": 0, "execute": 0, "command": 0, "patch": 0, "binder": 0,
             "authorization": 0, "mutation": 0, "worker": 0, "provider": 0}

    def counted_accept(**kwargs):
        calls["accept"] += 1
        return real_accept(**kwargs)

    def stopped(name: str):
        def _raise(*_args: object, **_kwargs: object) -> None:
            calls[name] += 1
            raise AssertionError(f"acceptance transition called prohibited owner {name}")
        return _raise

    monkeypatch.setattr(acceptance, "accept_generated_content", counted_accept)
    monkeypatch.setattr(disposable, "execute_disposable_patch_validation", stopped("execute"))
    monkeypatch.setattr(disposable, "execute_validation_command", stopped("command"))
    monkeypatch.setattr(disposable, "execute_governed_repository_mutation", stopped("patch"))
    monkeypatch.setattr(prerequisites, "bind_codex_replacement_acceptance_prerequisites", stopped("binder"))
    monkeypatch.setattr(mutation_authorization, "authorize_filesystem_mutation", stopped("authorization"))
    monkeypatch.setattr(filesystem_mutation, "apply_filesystem_mutation", stopped("mutation"))
    monkeypatch.setattr(worker_activation, "activate_bounded_codex_worker", stopped("worker"))
    monkeypatch.setattr(provider_execution, "invoke_provider_once", stopped("provider"))

    accepted = acceptance.accept_generated_content_from_content_acceptance_decision(
        acceptance_id="G31-24E-ACCEPTANCE", decision_capture=capture, binding_capture=binding,
        created_at=r02.CREATED_AT, session_root=root, replay_dir=root / "ACCEPTANCE",
    )
    reconstructed = acceptance.reconstruct_generated_content_acceptance_from_decision_replay(
        acceptance_capture=accepted, decision_capture=capture, binding_capture=binding,
        session_root=root,
    )
    artifact = accepted["generated_content_acceptance_artifact"]
    subject = capture["content_acceptance_context_artifact"]["subject_binding"]

    assert calls == {"accept": 1, "execute": 0, "command": 0, "patch": 0, "binder": 0,
                     "authorization": 0, "mutation": 0, "worker": 0, "provider": 0}
    assert artifact["acceptance_status"] == acceptance.GENERATED_CONTENT_ACCEPTED
    assert artifact["implementation_manifest_hash"] == subject["manifest_hash"]
    assert artifact["generated_content_validation_hash"] == subject["content_validation_hash"]
    assert artifact["generated_test_validation_hash"] == subject["test_validation_hash"]
    assert artifact["human_decision"] == decision.ACCEPTED
    assert reconstructed["result_accepted"] is True
    assert reconstructed["mutation_authorized"] is False
    assert reconstructed["main_repository_mutated"] is False
    assert reconstructed["replay_artifact_count"] == 1
    assert len(runner.calls) == 1
    assert sha256((source / "aigol/runtime/human_interface.py").read_bytes()).hexdigest() == source_hash
    assert subprocess.run(
        ["git", "status", "--short"], cwd=source, check=True, capture_output=True, text=True
    ).stdout == ""


def test_rejected_generic_and_plain_boolean_never_call_acceptance(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    rejected, binding, root, _, _ = _decision_ready(
        tmp_path, "G31-24E-REJECT", decision.REJECTED
    )
    calls = 0

    def forbidden(*_args: object, **_kwargs: object) -> None:
        nonlocal calls
        calls += 1
        raise AssertionError("rejected or generic evidence reached acceptance")

    monkeypatch.setattr(acceptance, "accept_generated_content", forbidden)
    with pytest.raises(FailClosedRuntimeError, match="exact V2 ACCEPTED"):
        acceptance.accept_generated_content_from_content_acceptance_decision(
            acceptance_id="REJECTED", decision_capture=rejected, binding_capture=binding,
            created_at=r02.CREATED_AT, session_root=root, replay_dir=root / "REJECTED",
        )
    with pytest.raises(FailClosedRuntimeError, match="exact V2 content-acceptance evidence"):
        acceptance.accept_generated_content_from_content_acceptance_decision(
            acceptance_id="BOOLEAN", decision_capture=True, binding_capture=binding,
            created_at=r02.CREATED_AT, session_root=root, replay_dir=root / "BOOLEAN",
        )
    generic = deepcopy(rejected)
    generic["human_decision_artifact"]["decision_outcome"] = "APPROVE"
    with pytest.raises(FailClosedRuntimeError):
        acceptance.accept_generated_content_from_content_acceptance_decision(
            acceptance_id="GENERIC", decision_capture=generic, binding_capture=binding,
            created_at=r02.CREATED_AT, session_root=root, replay_dir=root / "GENERIC",
        )
    assert calls == 0
    assert not list(root.rglob(f"000_{acceptance.CONTENT_ACCEPTANCE_REPLAY_STEP}.json"))


def test_tamper_cross_session_duplicate_and_replay_fail_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    capture, binding, root, source, _ = _decision_ready(
        tmp_path, "G31-24E-TAMPER", decision.ACCEPTED
    )

    def bind(changed_capture, changed_binding, name: str, session_root: Path = root):
        return acceptance.accept_generated_content_from_content_acceptance_decision(
            acceptance_id=name, decision_capture=changed_capture, binding_capture=changed_binding,
            created_at=r02.CREATED_AT, session_root=session_root, replay_dir=session_root / name,
        )

    changed = deepcopy(capture)
    changed["human_decision_artifact"]["decided_by"] = "SUBSTITUTED_ACTOR"
    with pytest.raises(FailClosedRuntimeError): bind(changed, binding, "ACTOR")
    for field in ("preimage_sha256", "postimage_sha256"):
        changed_binding = deepcopy(binding)
        changed_binding["implementation_manifest_capture"]["implementation_manifest_artifact"][
            "file_entries"
        ][0][field] = "sha256:" + "0" * 64
        with pytest.raises(FailClosedRuntimeError): bind(capture, changed_binding, field)
    changed_binding = deepcopy(binding)
    changed_binding["generated_test_validation_capture"]["generated_test_validation_artifact"][
        "validation_status"
    ] = "SUBSTITUTED"
    with pytest.raises(FailClosedRuntimeError): bind(capture, changed_binding, "VALIDATION")
    for field in ("result_accepted", "main_repository_mutated", "mutation_authorized"):
        changed_binding = deepcopy(binding); changed_binding[field] = True
        with pytest.raises(FailClosedRuntimeError): bind(capture, changed_binding, field)
    with pytest.raises(FailClosedRuntimeError, match="cross-session"):
        bind(capture, binding, "CROSS", tmp_path / "OTHER-SESSION")

    real_decision_load = decision.load_json
    with monkeypatch.context() as scoped:
        def reordered_decision(path: Path):
            artifact = real_decision_load(path)
            if Path(path).name.startswith("000_"):
                artifact["replay_step"] = "content_acceptance_request_recorded"
            return artifact
        scoped.setattr(decision, "load_json", reordered_decision)
        with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
            bind(capture, binding, "REORDERED")

    accepted = bind(capture, binding, "ACCEPTED")
    with pytest.raises(FailClosedRuntimeError, match="destination already exists"):
        bind(capture, binding, "ACCEPTED")
    with pytest.raises(FailClosedRuntimeError, match="already consumed"):
        bind(capture, binding, "SECOND")
    real_acceptance_load = acceptance.load_json
    with monkeypatch.context() as scoped:
        def reordered_acceptance(path: Path):
            artifact = real_acceptance_load(path)
            if Path(path).name.startswith("000_"):
                artifact["replay_step"] = "substituted"
            return artifact
        scoped.setattr(acceptance, "load_json", reordered_acceptance)
        with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
            acceptance.reconstruct_generated_content_acceptance_from_decision_replay(
                acceptance_capture=accepted, decision_capture=capture,
                binding_capture=binding, session_root=root,
            )
    assert subprocess.run(
        ["git", "status", "--short"], cwd=source, check=True, capture_output=True, text=True
    ).stdout == ""


def test_v1_create_only_acceptance_remains_compatible(tmp_path: Path) -> None:
    accepted = _accept(*_validated_bundle(tmp_path, "v1-compatible"))
    artifact = accepted["generated_content_acceptance_artifact"]
    assert accepted["acceptance_status"] == acceptance.GENERATED_CONTENT_ACCEPTED
    assert artifact["operation_mode"] == "CREATE_ONLY"
    acceptance.verify_generated_content_acceptance_artifact(artifact)
