from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess

import pytest

from aigol.runtime import human_decision_runtime as decision
from aigol.runtime import platform_core_existing_file_governance as governance
from aigol.runtime import platform_core_existing_file_mutation_candidate as candidate
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash
from aigol.workers import filesystem_replace_worker as replace_worker
import test_g31_24d_r02_aicli_task_outcome_to_disposable_review_binding as r02
import test_g31_24g_r01_existing_file_candidate_provenance as r01


ACTOR = "HUMAN_OPERATOR"


@pytest.fixture(autouse=True)
def _git_workspace(monkeypatch: pytest.MonkeyPatch):
    original = r02._workspace

    def workspace(*args, **kwargs):
        result = original(*args, **kwargs)
        for command in (
            ["git", "init"],
            ["git", "config", "user.name", "G31"],
            ["git", "config", "user.email", "g31@example.invalid"],
            ["git", "add", "aigol/runtime/human_interface.py", "tests/test_human_interface.py"],
            ["git", "commit", "-m", "baseline"],
        ):
            subprocess.run(command, cwd=result, check=True, capture_output=True, text=True)
        return result

    monkeypatch.setattr(r02, "_workspace", workspace)


def _forbid_downstream(monkeypatch: pytest.MonkeyPatch) -> dict[str, int]:
    calls: dict[str, int] = {}
    observed = (
        "authorize_g31_approved_existing_file_mutation",
        "bind_g31_mutation_authorization_actor_and_replay",
        "create_g31_authenticated_replace_request",
    )
    for name in observed:
        original = getattr(governance, name)
        calls[name] = 0

        def observe(*args, _name=name, _original=original, **kwargs):
            calls[_name] += 1
            return _original(*args, **kwargs)

        monkeypatch.setattr(governance, name, observe)
    targets = (
        (governance, "execute_g31_authenticated_replace"),
        (governance, "recover_g31_authenticated_replace"),
        (replace_worker, "execute_filesystem_replace_request"),
        (replace_worker, "_execute_authenticated_replace_v2"),
        (replace_worker, "_recover_authenticated_replace_v2"),
    )
    for module, name in targets:
        calls[name] = 0

        def forbidden(*_args, _name=name, **_kwargs):
            calls[_name] += 1
            raise AssertionError(f"forbidden downstream call: {_name}")

        monkeypatch.setattr(module, name, forbidden)
    return calls


@pytest.mark.parametrize(
    ("outcome", "approved"),
    [(decision.MUTATION_APPROVED, True), (decision.REJECTED, False)],
)
def test_exact_v3_outcome_is_transported_reconstructed_presented_and_stopped(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    outcome: str,
    approved: bool,
) -> None:
    calls = _forbid_downstream(monkeypatch)
    result, output, root, source, runner = r02._run(
        tmp_path,
        f"G31-R04-V3-{outcome}",
        ["/satisfied", "/approve", "/accept", outcome],
    )
    runtime = result["runtime_result"]
    context = runtime["human_mutation_decision_context_capture"]
    capture = runtime["human_mutation_decision_capture"]
    reconstruction = runtime["human_mutation_decision_reconstruction"]
    artifact = capture["human_mutation_decision_artifact"]

    assert result["exit_reason"] == "HUMAN_MUTATION_DECISION_RECORDED"
    assert result["pending_mutation_decision"] is False
    assert artifact["decision_type"] == decision.MUTATION_AUTHORIZATION
    assert artifact["decision_scope"] == decision.EXISTING_FILE_REPLACE_ONLY
    assert artifact["decision_outcome"] == outcome
    assert artifact["decided_by"] == ACTOR
    assert context["context_artifact"]["valid_decision_outcomes"] == [
        decision.MUTATION_APPROVED,
        decision.REJECTED,
    ]
    assert reconstruction["decision_outcome"] == outcome
    assert reconstruction["replay_artifact_count"] == 4
    assert runtime["result_accepted"] is True
    assert runtime["existing_file_mutation_candidate_created"] is True
    assert runtime["human_mutation_decision_recorded"] is True
    assert runtime["mutation_decision_approved"] is approved
    for field in (
        "mutation_authorized", "authorization_actor_bound", "authorization_replay_recorded",
    ):
        assert runtime[field] is approved
    assert runtime["worker_invoked"] is approved
    for field in (
        "provider_invoked",
        "command_executed",
        "repository_mutated",
        "main_repository_mutated",
    ):
        assert runtime[field] is False
    assert runtime["replace_request_created"] is approved
    assert runtime["authorization_consumed"] is approved
    assert runtime["human_mutation_decision_actor"] == ACTOR
    assert runtime["repository_grounding_artifact"] == (
        runtime["codex_worker_activation_binding_reconstruction"]["lineage"]["grounding"]
    )
    rendered = "\n".join(output)
    assert "Human Mutation Decision Required" in rendered
    assert "Enter exact APPROVED or REJECTED." in rendered
    assert f"Outcome: {outcome}" in rendered
    assert "Mutation Authorized: False" in rendered
    assert "Main Repository Mutated: False" in rendered
    if approved:
        assert "Canonical Existing-File Mutation Authorization" in rendered
    assert calls["authorize_g31_approved_existing_file_mutation"] == int(approved)
    assert calls["bind_g31_mutation_authorization_actor_and_replay"] == int(approved)
    assert calls["create_g31_authenticated_replace_request"] == int(approved)
    assert all(
        count == 0
        for name, count in calls.items()
        if name not in {
            "authorize_g31_approved_existing_file_mutation",
            "bind_g31_mutation_authorization_actor_and_replay",
            "create_g31_authenticated_replace_request",
        }
    )
    assert len(runner.calls) == 1
    assert (root / "G31_MUTATION_AUTHORIZATION_REPLAY_V1").exists() is approved
    assert (root / "G31_EXISTING_FILE_REPLACE_V2").exists() is approved
    assert subprocess.run(
        ["git", "status", "--short"], cwd=source, check=True, capture_output=True, text=True
    ).stdout == ""


def test_legacy_and_invalid_vocabulary_then_eof_creates_no_v3_decision(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = _forbid_downstream(monkeypatch)
    invalid = [
        "APPROVE", "/approve", "/accept", "ACCEPTED", "YES", "Y", "true",
        "/satisfied", "confirm existing-file mutation", "approved",
    ]
    result, output, root, source, runner = r02._run(
        tmp_path,
        "G31-R04-V3-INVALID",
        ["/satisfied", "/approve", "/accept", *invalid],
    )
    runtime = result["runtime_result"]
    context = runtime["human_mutation_decision_context_capture"]
    replay = Path(context["human_mutation_decision_replay_reference"])

    assert result["session_status"] == "REFERENCE_UHI_SESSION_AWAITING_MUTATION_DECISION"
    assert result["exit_reason"] == "GENERATED_CONTENT_ACCEPTANCE_RECORDED"
    assert result["pending_mutation_decision"] is True
    assert runtime["human_mutation_decision_recorded"] is False
    assert "human_mutation_decision_capture" not in runtime
    assert not replay.exists()
    assert sum(
        event["event"] == "invalid_mutation_decision_response"
        for event in result["transcript"]
    ) == len(invalid)
    rendered = "\n".join(output)
    assert rendered.count("accepts only exact APPROVED or REJECTED") == len(invalid)
    assert "awaiting exact APPROVED or REJECTED" in rendered
    assert all(count == 0 for count in calls.values())
    assert len(runner.calls) == 1
    assert not (root / "G31_MUTATION_AUTHORIZATION_REPLAY_V1").exists()
    assert subprocess.run(
        ["git", "status", "--short"], cwd=source, check=True, capture_output=True, text=True
    ).stdout == ""


def test_authentic_lineage_actor_duplicate_and_replay_fail_closed(
    tmp_path: Path,
) -> None:
    accepted, content, binding, grounding, root, _, _ = r01._accepted(
        tmp_path, "G31-R04-V3-TAMPER"
    )
    candidate_capture = candidate.create_g31_accepted_existing_file_mutation_candidate(
        candidate_id="G31-R04-V3-CANDIDATE",
        acceptance_capture=accepted,
        decision_capture=content,
        binding_capture=binding,
        repository_grounding_artifact=grounding,
        session_root=root,
        created_by=ACTOR,
        created_at=r02.CREATED_AT,
        replay_dir=root / "CANDIDATE",
    )
    common = {
        "candidate_capture": candidate_capture,
        "acceptance_capture": accepted,
        "content_decision_capture": content,
        "binding_capture": binding,
        "repository_grounding_artifact": grounding,
        "human_actor_id": ACTOR,
        "presented_at": r02.CREATED_AT,
        "session_root": root,
    }

    changed_candidate = deepcopy(candidate_capture)
    changed_candidate["existing_file_mutation_candidate_artifact"]["target_path"] = "changed.py"
    changed_replay = deepcopy(candidate_capture)
    changed_replay["candidate_replay_hash"] = "changed-replay"
    changed_provenance = deepcopy(candidate_capture)
    changed_provenance["existing_file_mutation_candidate_artifact"][
        "candidate_provenance_binding_hash"
    ] = "changed-provenance"
    changed_grounding = deepcopy(grounding)
    changed_grounding["grounding_evidence_hash"] = "changed-grounding"
    failures = (
        {"candidate_capture": changed_candidate},
        {"candidate_capture": changed_replay},
        {"candidate_capture": changed_provenance},
        {"repository_grounding_artifact": changed_grounding},
        {"session_root": tmp_path / "OTHER-SESSION"},
    )
    for index, changed in enumerate(failures):
        with pytest.raises(FailClosedRuntimeError):
            decision.prepare_existing_file_mutation_decision_context(
                context_id=f"INVALID-{index}", replay_dir=root / f"INVALID-{index}",
                **{**common, **changed},
            )

    context = decision.prepare_existing_file_mutation_decision_context(
        context_id="G31-R04-V3-CONTEXT", replay_dir=root / "DECISION", **common
    )
    with pytest.raises(FailClosedRuntimeError, match="actor"):
        decision.record_existing_file_mutation_decision(
            context_capture=context,
            decision_outcome=decision.MUTATION_APPROVED,
            decided_by="OTHER-ACTOR",
            decided_at=r02.CREATED_AT,
            **{key: common[key] for key in (
                "candidate_capture", "acceptance_capture", "content_decision_capture",
                "binding_capture", "repository_grounding_artifact", "session_root",
            )},
        )
    capture = decision.record_existing_file_mutation_decision(
        context_capture=context,
        decision_outcome=decision.MUTATION_APPROVED,
        decided_by=ACTOR,
        decided_at=r02.CREATED_AT,
        **{key: common[key] for key in (
            "candidate_capture", "acceptance_capture", "content_decision_capture",
            "binding_capture", "repository_grounding_artifact", "session_root",
        )},
    )
    with pytest.raises(FailClosedRuntimeError, match="destination already exists"):
        decision.record_existing_file_mutation_decision(
            context_capture=context,
            decision_outcome=decision.MUTATION_APPROVED,
            decided_by=ACTOR,
            decided_at=r02.CREATED_AT,
            **{key: common[key] for key in (
                "candidate_capture", "acceptance_capture", "content_decision_capture",
                "binding_capture", "repository_grounding_artifact", "session_root",
            )},
        )

    reconstruct = {
        "decision_capture": capture,
        **{key: common[key] for key in (
            "candidate_capture", "acceptance_capture", "content_decision_capture",
            "binding_capture", "repository_grounding_artifact", "session_root",
        )},
    }
    replay = Path(capture["human_mutation_decision_replay_reference"])
    first = replay / "000_mutation_decision_context_presented.json"
    second = replay / "001_mutation_decision_request_recorded.json"
    temporary = replay / "swap.json"
    first.rename(temporary); second.rename(first); temporary.rename(second)
    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        decision.reconstruct_existing_file_mutation_decision_replay(**reconstruct)
    first.rename(temporary); second.rename(first); temporary.rename(second)
    returned = replay / "003_mutation_decision_returned.json"
    wrapper = json.loads(returned.read_text(encoding="utf-8"))
    wrapper["artifact"]["decision_outcome"] = decision.REJECTED
    returned.write_text(json.dumps(wrapper), encoding="utf-8")
    with pytest.raises(FailClosedRuntimeError):
        decision.reconstruct_existing_file_mutation_decision_replay(**reconstruct)
