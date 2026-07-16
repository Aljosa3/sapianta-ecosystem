from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from aigol.cli import aicli
from aigol.runtime.approved_durable_work_repository_scope_grounding import (
    ground_approved_durable_work_repository_scope,
)
from aigol.runtime.approved_durable_work_worker_payload_binding import (
    bind_approved_durable_work_to_worker_payload,
)
from aigol.runtime.execution_summary_runtime import (
    EXECUTION_SUMMARY_HUMAN_CONFIRMATION_ARTIFACT_V1,
    verify_execution_summary_confirmation,
)
from aigol.runtime.grounded_execution_authorization_human_decision_binding import (
    EXECUTION_DECISION_APPROVED,
    EXECUTION_DECISION_FAILED_CLOSED,
    EXECUTION_DECISION_REJECTED,
    HUMAN_EXECUTION_DECISION_RESULT_ARTIFACT_V1,
    bind_distinct_human_execution_decision,
    reconstruct_distinct_human_execution_decision,
    render_distinct_human_execution_decision,
    validate_distinct_human_execution_decision,
)
from aigol.runtime.grounded_worker_request_execution_authorization_binding import (
    bind_grounded_worker_request_to_execution_authorization_review,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_project_services import (
    prepare_unified_human_interface_project_context,
)
from aigol.runtime.platform_implementation_turn_durable_work_binding import (
    consume_approved_implementation_turn_binding,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-07-16T00:00:00Z"
REQUEST = (
    "Improve the human interface terminal summary behavior. "
    "Include focused tests and validation."
)


def _rehash(artifact: dict) -> dict:
    artifact["artifact_hash"] = replay_hash(
        {key: value for key, value in artifact.items() if key != "artifact_hash"}
    )
    return artifact


def _workspace(tmp_path: Path, name: str) -> Path:
    workspace = tmp_path / name
    (workspace / ".git").mkdir(parents=True)
    (workspace / "aigol" / "runtime").mkdir(parents=True)
    (workspace / "tests").mkdir()
    (workspace / "aigol" / "runtime" / "human_interface.py").write_text(
        "def render_summary(value):\n    return f'Summary: {value}'\n",
        encoding="utf-8",
    )
    (workspace / "tests" / "test_human_interface.py").write_text(
        "from aigol.runtime.human_interface import render_summary\n\n"
        "def test_render_summary():\n"
        "    assert render_summary('ready') == 'Summary: ready'\n",
        encoding="utf-8",
    )
    return workspace


def _review(
    tmp_path: Path,
    *,
    session: str,
) -> tuple[dict, dict, Path, Path]:
    workspace = _workspace(tmp_path, f"workspace-{session}")
    runtime_root = tmp_path / "runtime"
    session_root = runtime_root / session
    binding = prepare_unified_human_interface_project_context(
        interface_name="aicli",
        session_id=session,
        message=REQUEST,
        runtime_root=runtime_root,
        workspace=workspace,
        created_at=CREATED_AT,
    )["canonical_implementation_turn_binding"]
    consumption = consume_approved_implementation_turn_binding(
        binding_artifact=binding,
        development_composition_plan_hash=binding[
            "development_composition_plan_hash"
        ],
        durable_governed_work_hash=binding["durable_governed_work_hash"],
        proposal_preview_hash=binding["proposal_preview_hash"],
        approval_request_hash=binding["approval_request_hash"],
        created_at=CREATED_AT,
        replay_dir=binding["replay_reference"],
    )
    payload = bind_approved_durable_work_to_worker_payload(
        implementation_turn_binding=binding,
        approval_consumption_artifact=consumption,
        requested_by="CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY",
        created_at=CREATED_AT,
        replay_dir=session_root / "payload",
    )
    grounding = ground_approved_durable_work_repository_scope(
        worker_payload_binding_artifact=payload,
        workspace=workspace,
        created_at=CREATED_AT,
        replay_dir=session_root / "grounding",
    )
    review = bind_grounded_worker_request_to_execution_authorization_review(
        repository_scope_grounding_artifact=grounding,
        workspace=workspace,
        created_at=CREATED_AT,
        replay_dir=session_root / "review",
    )
    return binding, review, workspace, session_root


def _decision(
    review: dict,
    *,
    decision: str,
    workspace: Path,
    session_root: Path,
    replay_name: str = "decision",
    session: str | None = None,
) -> dict:
    return bind_distinct_human_execution_decision(
        authorization_review_artifact=review,
        human_decision=decision,
        session_id=session or session_root.name,
        decided_by="HUMAN_OPERATOR_VIA_AICLI",
        decided_at=CREATED_AT,
        workspace=workspace,
        session_root=session_root,
        replay_dir=session_root / replay_name,
    )


def test_exact_second_human_approval_creates_existing_confirmation(
    tmp_path: Path,
) -> None:
    _, review, workspace, session_root = _review(tmp_path, session="G31-09-APPROVE")
    result = _decision(
        review,
        decision="APPROVE",
        workspace=workspace,
        session_root=session_root,
    )

    assert result["artifact_type"] == HUMAN_EXECUTION_DECISION_RESULT_ARTIFACT_V1
    assert result["decision_status"] == EXECUTION_DECISION_APPROVED
    assert result["execution_summary_human_confirmation"] is True
    confirmation = result["human_confirmation_artifact"]
    assert confirmation["artifact_type"] == (
        EXECUTION_SUMMARY_HUMAN_CONFIRMATION_ARTIFACT_V1
    )
    verify_execution_summary_confirmation(
        review["execution_summary_artifact"], confirmation
    )


def test_explicit_rejection_is_replay_visible_and_non_confirming(tmp_path: Path) -> None:
    _, review, workspace, session_root = _review(tmp_path, session="G31-09-REJECT")
    result = _decision(
        review,
        decision="REJECT",
        workspace=workspace,
        session_root=session_root,
    )

    assert result["decision_status"] == EXECUTION_DECISION_REJECTED
    assert result["execution_decision_rejected"] is True
    assert result["execution_summary_human_confirmation"] is False
    assert result["human_confirmation_artifact"] is None
    assert result["replay_visible"] is True


@pytest.mark.parametrize("decision", ["", "yes", "approve execution", "maybe"])
def test_missing_or_ambiguous_decision_fails_closed(
    tmp_path: Path,
    decision: str,
) -> None:
    _, review, workspace, session_root = _review(
        tmp_path, session=f"G31-09-AMBIGUOUS-{len(decision)}"
    )
    result = _decision(
        review,
        decision=decision,
        workspace=workspace,
        session_root=session_root,
    )

    assert result["decision_status"] == EXECUTION_DECISION_FAILED_CLOSED
    assert result["execution_summary_human_confirmation"] is False
    assert result["execution_authorized"] is False


def test_proposal_approval_cannot_substitute_for_execution_review(tmp_path: Path) -> None:
    binding, review, workspace, session_root = _review(
        tmp_path, session="G31-09-PROPOSAL-SUBSTITUTION"
    )
    result = _decision(
        binding,
        decision="APPROVE",
        workspace=workspace,
        session_root=session_root,
    )

    assert result["decision_status"] == EXECUTION_DECISION_FAILED_CLOSED
    assert result["human_confirmation_artifact"] is None
    assert result["source_review_observation_hash"] == replay_hash(binding)
    assert review["proposal_approval_is_execution_authorization"] is False


def test_mismatched_review_or_execution_summary_fails_closed(tmp_path: Path) -> None:
    _, review, workspace, session_root = _review(
        tmp_path, session="G31-09-REVIEW-MISMATCH"
    )
    tampered = deepcopy(review)
    summary = tampered["execution_summary_artifact"]
    summary["original_request"] = "substituted"
    _rehash(summary)
    tampered["execution_summary_hash"] = summary["artifact_hash"]
    _rehash(tampered)
    result = _decision(
        tampered,
        decision="APPROVE",
        workspace=workspace,
        session_root=session_root,
    )

    assert result["decision_status"] == EXECUTION_DECISION_FAILED_CLOSED
    assert "Replay" in result["failure_reason"]


def test_changed_repository_evidence_fails_closed(tmp_path: Path) -> None:
    _, review, workspace, session_root = _review(tmp_path, session="G31-09-STALE")
    (workspace / "aigol" / "runtime" / "human_interface.py").write_text(
        "def render_summary(value):\n    return value.upper()\n",
        encoding="utf-8",
    )
    result = _decision(
        review,
        decision="APPROVE",
        workspace=workspace,
        session_root=session_root,
    )

    assert result["decision_status"] == EXECUTION_DECISION_FAILED_CLOSED
    assert "stale or substituted" in result["failure_reason"]


def test_changed_grounded_worker_request_fails_closed(tmp_path: Path) -> None:
    _, review, workspace, session_root = _review(
        tmp_path, session="G31-09-WORKER-TAMPER"
    )
    tampered = deepcopy(review)
    worker = tampered["source_repository_scope_grounding_artifact"][
        "grounded_worker_request_artifact"
    ]
    worker["worker_objective"] = "substituted objective"
    _rehash(worker)
    _rehash(tampered["source_repository_scope_grounding_artifact"])
    _rehash(tampered)
    result = _decision(
        tampered,
        decision="APPROVE",
        workspace=workspace,
        session_root=session_root,
    )

    assert result["decision_status"] == EXECUTION_DECISION_FAILED_CLOSED


def test_replayed_decision_fails_closed_without_second_confirmation(tmp_path: Path) -> None:
    _, review, workspace, session_root = _review(tmp_path, session="G31-09-REPLAYED")
    first = _decision(
        review,
        decision="APPROVE",
        workspace=workspace,
        session_root=session_root,
        replay_name="decision-1",
    )
    second = _decision(
        review,
        decision="APPROVE",
        workspace=workspace,
        session_root=session_root,
        replay_name="decision-2",
    )

    assert first["decision_status"] == EXECUTION_DECISION_APPROVED
    assert second["decision_status"] == EXECUTION_DECISION_FAILED_CLOSED
    assert "already recorded" in second["failure_reason"]
    assert second["human_confirmation_artifact"] is None


def test_cross_session_review_fails_closed(tmp_path: Path) -> None:
    _, review, workspace, _ = _review(tmp_path, session="G31-09-SOURCE-SESSION")
    other_root = tmp_path / "runtime" / "G31-09-OTHER-SESSION"
    result = _decision(
        review,
        decision="APPROVE",
        workspace=workspace,
        session_root=other_root,
    )

    assert result["decision_status"] == EXECUTION_DECISION_FAILED_CLOSED
    assert "cross-session" in result["failure_reason"]


def test_complete_nested_replay_reconstructs(tmp_path: Path) -> None:
    _, review, workspace, session_root = _review(tmp_path, session="G31-09-RECONSTRUCT")
    result = _decision(
        review,
        decision="APPROVE",
        workspace=workspace,
        session_root=session_root,
    )
    reconstructed = reconstruct_distinct_human_execution_decision(
        result["replay_reference"],
        workspace=workspace,
        session_root=session_root,
    )

    assert reconstructed["artifact_hash"] == result["artifact_hash"]
    assert reconstructed["source_authorization_review_hash"] == review[
        "artifact_hash"
    ]


def test_confirmation_and_replay_substitution_fail_closed(tmp_path: Path) -> None:
    _, review, workspace, session_root = _review(
        tmp_path, session="G31-09-CONFIRMATION-TAMPER"
    )
    result = _decision(
        review,
        decision="APPROVE",
        workspace=workspace,
        session_root=session_root,
    )
    tampered = deepcopy(result)
    tampered["human_confirmation_hash"] = replay_hash("substituted")
    _rehash(tampered)
    with pytest.raises(FailClosedRuntimeError, match="confirmation mismatch"):
        validate_distinct_human_execution_decision(tampered, workspace=workspace)

    path = Path(result["replay_reference"]) / "001_execution_human_decision_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["replay_step"] = "substituted"
    wrapper["replay_hash"] = replay_hash(
        {key: value for key, value in wrapper.items() if key != "replay_hash"}
    )
    path.write_text(json.dumps(wrapper), encoding="utf-8")
    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_distinct_human_execution_decision(
            result["replay_reference"],
            workspace=workspace,
            session_root=session_root,
        )


@pytest.mark.parametrize("decision", ["APPROVE", "REJECT"])
def test_stop_boundary_remains_false_after_either_decision(
    tmp_path: Path,
    decision: str,
) -> None:
    _, review, workspace, session_root = _review(
        tmp_path, session=f"G31-09-BOUNDARY-{decision}"
    )
    result = _decision(
        review,
        decision=decision,
        workspace=workspace,
        session_root=session_root,
    )

    for field in (
        "authorization_request_created",
        "authorization_decision_created",
        "execution_authorization_artifact_created",
        "execution_authorized",
        "worker_selected",
        "worker_assigned",
        "worker_dispatched",
        "worker_invoked",
        "provider_invoked",
        "command_executed",
        "repository_mutated",
        "deployment_reached",
        "human_interface_authority",
        "human_interface_decision_authority",
        "human_interface_authorization_authority",
    ):
        assert result[field] is False
    assert result["dispatch_blocked"] is True


def test_presentation_distinguishes_both_approvals_and_actual_authority(
    tmp_path: Path,
) -> None:
    _, review, workspace, session_root = _review(
        tmp_path, session="G31-09-PRESENTATION"
    )
    result = _decision(
        review,
        decision="APPROVE",
        workspace=workspace,
        session_root=session_root,
    )
    rendered = render_distinct_human_execution_decision(result)

    assert "proposal_approval_consumed: True" in rendered
    assert "proposal_approval_is_execution_authorization: False" in rendered
    assert "execution_summary_human_confirmation: True" in rendered
    assert "execution_authorized: False" in rendered
    assert "worker_dispatched: False" in rendered


def test_real_aicli_contextual_second_approval_preserves_g31_09_stop_evidence(
    tmp_path: Path,
) -> None:
    workspace = _workspace(tmp_path, "aicli-approve-workspace")
    output: list[str] = []
    inputs = iter([REQUEST, "/send", "/approve", "/approve", "/exit"])
    result = aicli.run_reference_uhi_session(
        session_id="G31-09-AICLI-APPROVE",
        created_at=CREATED_AT,
        runtime_root=tmp_path / "aicli-runtime",
        workspace=workspace,
        input_reader=lambda _prompt: next(inputs),
        output_writer=output.append,
    )
    runtime = result["runtime_result"]
    rendered = "\n".join(output)

    assert result["approval_count"] == 2
    assert runtime["execution_human_decision_status"] == EXECUTION_DECISION_APPROVED
    assert runtime["execution_summary_human_confirmation"] is True
    assert runtime["execution_human_decision_result"]["execution_authorized"] is False
    assert runtime["execution_authorized"] is True
    assert runtime["execution_human_decision_result"]["worker_selected"] is False
    assert runtime["worker_selected"] is True
    assert runtime["worker_assigned"] is False
    assert "A distinct execution decision is now pending" in rendered
    assert "No execution is authorized yet" in rendered


def test_real_aicli_contextual_cancel_is_explicit_rejection(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path, "aicli-reject-workspace")
    output: list[str] = []
    inputs = iter([REQUEST, "/send", "/approve", "/cancel", "/exit"])
    result = aicli.run_reference_uhi_session(
        session_id="G31-09-AICLI-REJECT",
        created_at=CREATED_AT,
        runtime_root=tmp_path / "aicli-runtime",
        workspace=workspace,
        input_reader=lambda _prompt: next(inputs),
        output_writer=output.append,
    )
    runtime = result["runtime_result"]

    assert result["approval_count"] == 1
    assert runtime["execution_human_decision_status"] == EXECUTION_DECISION_REJECTED
    assert runtime["execution_decision_rejected"] is True
    assert runtime["execution_summary_human_confirmation"] is False
    assert runtime["execution_authorized"] is False


def test_real_aicli_ambiguous_text_does_not_consume_pending_decision(
    tmp_path: Path,
) -> None:
    workspace = _workspace(tmp_path, "aicli-ambiguous-workspace")
    output: list[str] = []
    inputs = iter([REQUEST, "/send", "/approve", "yes", "/approve", "/exit"])
    result = aicli.run_reference_uhi_session(
        session_id="G31-09-AICLI-AMBIGUOUS",
        created_at=CREATED_AT,
        runtime_root=tmp_path / "aicli-runtime",
        workspace=workspace,
        input_reader=lambda _prompt: next(inputs),
        output_writer=output.append,
    )

    assert result["runtime_result"]["execution_human_decision_status"] == (
        EXECUTION_DECISION_APPROVED
    )
    assert {item["event"] for item in result["transcript"]} >= {
        "ambiguous_execution_decision_rejected",
        "execution_decision_approved",
    }


def test_no_observed_g31_07_helpers_or_authorization_runtime_call_are_copied() -> None:
    runtime_source = Path(
        "aigol/runtime/grounded_execution_authorization_human_decision_binding.py"
    ).read_text(encoding="utf-8")
    aicli_source = Path(aicli.__file__).read_text(encoding="utf-8")

    for helper in ("def _verify_hash", "def _relative_path", "def _unique_relative_paths"):
        assert helper not in runtime_source
    assert "verify_replay_hash" in runtime_source
    assert "authorize_execution_ready" not in runtime_source
    assert "authorize_execution_ready" not in aicli_source
