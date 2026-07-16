from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from aigol.cli import aicli
from aigol.runtime.confirmed_grounded_execution_authorization_binding import (
    authorize_confirmed_grounded_execution_decision,
    reconstruct_confirmed_grounded_execution_ready_replay,
)
from aigol.runtime.execution_authorization_runtime import (
    EXECUTION_AUTHORIZED,
    reconstruct_execution_authorization_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import (
    load_json,
    with_replay_hash,
)
from test_g31_09_distinct_human_execution_decision_binding import (
    CREATED_AT,
    REQUEST,
    _decision,
    _review,
    _workspace,
)


def _authorized(tmp_path: Path, session: str = "G31-10") -> tuple[dict, dict, Path, Path]:
    _, review, workspace, session_root = _review(tmp_path, session=session)
    decision = _decision(
        review,
        decision="APPROVE",
        workspace=workspace,
        session_root=session_root,
    )
    capture = authorize_confirmed_grounded_execution_decision(
        human_execution_decision_artifact=decision,
        workspace=workspace,
        session_root=session_root,
        replay_dir=session_root / "authorization-binding",
    )
    return capture, decision, workspace, session_root


def test_exact_approved_decision_creates_existing_authorization_without_third_confirmation(
    tmp_path: Path,
) -> None:
    capture, decision, _, _ = _authorized(tmp_path)
    review = decision["source_authorization_review_artifact"]

    assert capture["authorization_status"] == EXECUTION_AUTHORIZED
    assert capture["execution_summary_human_confirmation"] is True
    assert capture["execution_authorization_request_created"] is True
    assert capture["execution_authorization_decision_created"] is True
    assert capture["execution_authorization_artifact_created"] is True
    assert capture["execution_authorized"] is True
    assert capture["third_human_confirmation_requested"] is False
    assert capture["human_confirmation_hash"] == decision["human_confirmation_hash"]
    assert capture["authorization_request_artifact"]["requested_scope"] == review[
        "authorization_scope"
    ]
    assert capture["execution_authorization_artifact"]["authorized_scope"] == review[
        "authorization_scope"
    ]
    for field in (
        "worker_selected",
        "worker_assigned",
        "worker_dispatched",
        "worker_invoked",
        "provider_invoked",
        "command_executed",
        "repository_mutated",
    ):
        assert capture[field] is False


def test_existing_ready_and_authorization_replay_reconstruct(tmp_path: Path) -> None:
    capture, decision, _, _ = _authorized(tmp_path, "G31-10-REPLAY")
    ready = reconstruct_confirmed_grounded_execution_ready_replay(
        capture["execution_ready_replay_reference"]
    )
    authorization = reconstruct_execution_authorization_replay(
        capture["execution_authorization_replay_reference"]
    )

    assert ready["human_execution_decision_hash"] == decision["artifact_hash"]
    assert authorization["authorization_status"] == EXECUTION_AUTHORIZED
    assert authorization["human_confirmation_hash"] == decision["human_confirmation_hash"]
    assert authorization["worker_assigned"] is False
    assert authorization["worker_dispatched"] is False
    assert authorization["worker_invoked"] is False


def test_rejected_and_cross_session_decisions_fail_before_authorization(
    tmp_path: Path,
) -> None:
    _, review, workspace, session_root = _review(tmp_path, session="G31-10-REJECT")
    rejected = _decision(
        review,
        decision="REJECT",
        workspace=workspace,
        session_root=session_root,
    )
    with pytest.raises(FailClosedRuntimeError, match="requires approved"):
        authorize_confirmed_grounded_execution_decision(
            human_execution_decision_artifact=rejected,
            workspace=workspace,
            session_root=session_root,
            replay_dir=session_root / "rejected",
        )
    _, cross_review, cross_workspace, cross_root = _review(
        tmp_path, session="G31-10-CROSS"
    )
    approved = _decision(
        cross_review,
        decision="APPROVE",
        workspace=cross_workspace,
        session_root=cross_root,
    )
    with pytest.raises(FailClosedRuntimeError, match="session mismatch"):
        authorize_confirmed_grounded_execution_decision(
            human_execution_decision_artifact=approved,
            workspace=cross_workspace,
            session_root=tmp_path / "OTHER-SESSION",
            replay_dir=tmp_path / "OTHER-SESSION" / "authorization",
        )


@pytest.mark.parametrize(
    "mutation",
    (
        lambda value: value.update(human_confirmation_hash="sha256:" + "0" * 64),
        lambda value: value.update(authorization_scope_hash="sha256:" + "1" * 64),
        lambda value: value.update(project_objective_hash="sha256:" + "2" * 64),
        lambda value: value["source_authorization_review_artifact"][
            "authorization_scope"
        ]["source_paths"].append("broadened.py"),
    ),
)
def test_summary_scope_and_upstream_substitution_fail_closed(
    tmp_path: Path,
    mutation,
) -> None:
    _, review, workspace, session_root = _review(tmp_path, session=f"TAMPER-{id(mutation)}")
    decision = _decision(
        review,
        decision="APPROVE",
        workspace=workspace,
        session_root=session_root,
    )
    tampered = deepcopy(decision)
    mutation(tampered)
    tampered = with_replay_hash(tampered, hash_field="artifact_hash")

    with pytest.raises(FailClosedRuntimeError):
        authorize_confirmed_grounded_execution_decision(
            human_execution_decision_artifact=tampered,
            workspace=workspace,
            session_root=session_root,
            replay_dir=session_root / "tampered",
        )


def test_stale_repository_evidence_and_replayed_decision_fail_closed(tmp_path: Path) -> None:
    capture, decision, workspace, session_root = _authorized(tmp_path, "G31-10-STALE")
    with pytest.raises(FailClosedRuntimeError, match="already consumed"):
        authorize_confirmed_grounded_execution_decision(
            human_execution_decision_artifact=decision,
            workspace=workspace,
            session_root=session_root,
            replay_dir=session_root / "second-authorization",
        )
    _, stale_review, stale_workspace, stale_root = _review(
        tmp_path, session="G31-10-CHANGED-EVIDENCE"
    )
    stale_decision = _decision(
        stale_review,
        decision="APPROVE",
        workspace=stale_workspace,
        session_root=stale_root,
    )
    Path(stale_workspace, "aigol/runtime/human_interface.py").write_text(
        "def changed():\n    return True\n", encoding="utf-8"
    )
    with pytest.raises(FailClosedRuntimeError):
        authorize_confirmed_grounded_execution_decision(
            human_execution_decision_artifact=stale_decision,
            workspace=stale_workspace,
            session_root=stale_root,
            replay_dir=stale_root / "stale-authorization",
        )
    assert capture["repository_mutated"] is False


def test_reordered_and_substituted_replay_fails_closed(tmp_path: Path) -> None:
    capture, _, _, _ = _authorized(tmp_path, "G31-10-ORDER")
    root = Path(capture["execution_authorization_replay_reference"])
    path = root / "001_authorization_decision_recorded.json"
    wrapper = load_json(path)
    wrapper["replay_index"] = 2
    path.write_text(
        json.dumps(with_replay_hash(wrapper, hash_field="replay_hash")),
        encoding="utf-8",
    )
    with pytest.raises(FailClosedRuntimeError, match="ordering"):
        reconstruct_execution_authorization_replay(root)


def test_real_aicli_second_approval_authorizes_without_third_prompt(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path, "g31-10-aicli")
    output: list[str] = []
    values = iter([REQUEST, "/send", "/approve", "/approve", "/exit"])
    result = aicli.run_reference_uhi_session(
        session_id="G31-10-AICLI",
        created_at=CREATED_AT,
        runtime_root=tmp_path / "runtime",
        workspace=workspace,
        input_reader=lambda _prompt: next(values),
        output_writer=output.append,
    )
    runtime = result["runtime_result"]
    rendered = "\n".join(output)

    assert result["approval_count"] == 2
    assert runtime["execution_authorized"] is True
    assert runtime["execution_authorization_capture"][
        "third_human_confirmation_requested"
    ] is False
    assert "Execution Authorization" in rendered
    assert "No Worker has been assigned, dispatched, invoked, or executed." in rendered
    assert "third" not in rendered.lower()


def test_real_aicli_rejection_never_creates_authorization(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path, "g31-10-reject-aicli")
    values = iter([REQUEST, "/send", "/approve", "/cancel", "/exit"])
    result = aicli.run_reference_uhi_session(
        session_id="G31-10-AICLI-REJECT",
        created_at=CREATED_AT,
        runtime_root=tmp_path / "runtime",
        workspace=workspace,
        input_reader=lambda _prompt: next(values),
        output_writer=lambda _line: None,
    )

    runtime = result["runtime_result"]
    assert runtime["execution_decision_rejected"] is True
    assert runtime["execution_authorized"] is False
    assert "execution_authorization_capture" not in runtime


def test_minimality_and_no_copied_helpers() -> None:
    source = Path(
        "aigol/runtime/confirmed_grounded_execution_authorization_binding.py"
    ).read_text(encoding="utf-8")
    for helper in (
        "def _verify_hash",
        "def _relative_path",
        "def _unique_relative_paths",
        "def _persist",
        "def _verify_wrapper",
    ):
        assert helper not in source
    assert "authorize_execution_ready(" in source
    assert len(source.splitlines()) <= 300
