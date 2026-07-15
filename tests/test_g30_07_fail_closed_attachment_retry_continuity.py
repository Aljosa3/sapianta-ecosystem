"""Focused G30-07 fail-closed attachment retry continuity tests."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from aigol.cli.aicli import run_reference_uhi_session
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_composition_coverage import (
    create_platform_capability_composition_coverage_request,
)
from aigol.runtime.platform_core_project_services import (
    ATTACHMENT_RETRY_COMPLETED,
    ATTACHMENT_RETRY_ELIGIBLE,
    G29_SEMANTIC_SELECTION_CLARIFICATION_OWNER,
    reconstruct_artifact_attachment_retry,
    reconstruct_operational_turn_binding,
    validate_artifact_attachment_retry_state,
    validate_operational_clarification_envelope,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-07-15T00:00:00Z"
REQUEST = ["Analyze Platform Capability Composition Coverage.", "Audit only."]


def _reader(values: list[str]):
    iterator = iter(values)
    return lambda _prompt: next(iterator)


def _reference(tmp_path: Path, name: str, *, invalid: bool = False) -> Path:
    artifact = create_platform_capability_composition_coverage_request(
        request_id=f"G30-07-{name.upper()}",
        query="Assess reusable Platform capability coverage and residual gaps.",
        created_at=CREATED_AT,
    )
    wrapper = {
        "replay_index": 0,
        "replay_step": "composition_coverage_request_recorded",
        "artifact": deepcopy(artifact),
    }
    wrapper["wrapper_hash"] = replay_hash(wrapper)
    if invalid:
        wrapper["artifact"]["request_id"] = "TAMPERED-AFTER-RECORDING"
    path = tmp_path / "canonical-input" / f"{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(wrapper, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def _run(
    tmp_path: Path,
    commands: list[str],
    *,
    session_id: str = "SESSION-G30-07",
) -> tuple[dict, list[str]]:
    output: list[str] = []
    result = run_reference_uhi_session(
        session_id=session_id,
        runtime_root=tmp_path / "runtime",
        workspace=tmp_path,
        created_at=CREATED_AT,
        input_reader=_reader(commands),
        output_writer=output.append,
    )
    return result, output


def _invalid_only(tmp_path: Path) -> tuple[dict, list[str]]:
    invalid = _reference(tmp_path, "invalid", invalid=True)
    return _run(tmp_path, [*REQUEST, "/send", f"/attach {invalid}"])


def _invalid_then_valid(tmp_path: Path) -> tuple[dict, list[str]]:
    invalid = _reference(tmp_path, "invalid", invalid=True)
    valid = _reference(tmp_path, "valid")
    return _run(
        tmp_path,
        [
            *REQUEST,
            "/send",
            f"/attach {invalid}",
            f"/attach {valid}",
            "/exit",
        ],
    )


def test_invalid_attachment_fails_closed_and_original_clarification_survives(
    tmp_path: Path,
) -> None:
    result, output = _invalid_only(tmp_path)
    context = result["platform_core_project_services_context"]
    state = context["artifact_attachment_retry_state"]
    envelope = context["operational_clarification_envelope"]
    work = context["governed_read_only_work_result"]
    rendered = "\n".join(output)

    assert work["binding_status"] == "GOVERNED_READ_ONLY_WORK_FAILED_CLOSED"
    assert work["presentation_status"] == "FAILED_CLOSED"
    assert state["retry_status"] == ATTACHMENT_RETRY_ELIGIBLE
    assert state["retry_eligible"] is True
    assert state["attempt_number"] == 1
    assert state["semantic_slot"] == "input_artifact_family"
    assert state["clarification_owner"] == G29_SEMANTIC_SELECTION_CLARIFICATION_OWNER
    assert state["invalid_artifact_satisfied_slot"] is False
    assert state["continuation_route_reference"] is None
    assert state["capability_invocation_started"] is False
    assert state["capability_invocation_completed"] is False
    assert context["semantic_capability_runtime_route"] is None
    assert envelope["artifact_hash"] == state["clarification_envelope_hash"]
    assert "clarification remains active" in rendered
    assert "attachment_attempt: 1" in rendered
    assert result["session_status"] == "REFERENCE_UHI_SESSION_AWAITING_HUMAN_CLARIFICATION"
    assert work["provider_invoked"] is False
    assert work["worker_invoked"] is False
    assert work["repository_mutated"] is False


def test_second_valid_attachment_completes_unchanged_runtime(tmp_path: Path) -> None:
    result, output = _invalid_then_valid(tmp_path)
    context = result["platform_core_project_services_context"]
    state = context["artifact_attachment_retry_state"]
    route = context["semantic_capability_runtime_route"]

    assert state["attempt_number"] == 2
    assert state["retry_status"] == ATTACHMENT_RETRY_COMPLETED
    assert state["retry_eligible"] is False
    assert state["semantic_slot"] == "input_artifact_family"
    assert state["clarification_owner"] == G29_SEMANTIC_SELECTION_CLARIFICATION_OWNER
    assert state["capability_invocation_completed"] is True
    assert route["route_status"] == "SEMANTIC_CAPABILITY_ROUTE_COMPLETED"
    assert route["lifecycle_status"] == (
        "SEMANTIC_CAPABILITY_INVOCATION_LIFECYCLE_COMPLETED"
    )
    assert context["development_intent_resolution"]["project_objective_restarted"] is False
    assert "presentation_status: PRESENTATION_READY" in "\n".join(output)
    assert route["provider_invoked"] is False
    assert route["worker_invoked"] is False
    assert route["repository_mutated"] is False


def test_replay_reconstructs_invalid_then_valid_attempt_sequence(
    tmp_path: Path,
) -> None:
    result, _output = _invalid_then_valid(tmp_path)
    context = result["platform_core_project_services_context"]
    state = context["artifact_attachment_retry_state"]
    replay = reconstruct_artifact_attachment_retry(state["attempt_reference"])
    turn = reconstruct_operational_turn_binding(
        context["operational_turn_binding_reference"]
    )

    assert replay["attempt_count"] == 2
    assert [item["retry_status"] for item in replay["attempt_history"]] == [
        ATTACHMENT_RETRY_ELIGIBLE,
        ATTACHMENT_RETRY_COMPLETED,
    ]
    assert replay["attempt_history"][0]["continuation_route_reference"] is None
    assert replay["attempt_history"][1]["continuation_route_hash"] == (
        context["semantic_capability_runtime_route"]["artifact_hash"]
    )
    assert turn["artifact_attachment_retry_hash"] == state["artifact_hash"]


def test_duplicate_attachment_attempt_is_rejected_without_new_attempt(
    tmp_path: Path,
) -> None:
    invalid = _reference(tmp_path, "invalid", invalid=True)
    result, output = _run(
        tmp_path,
        [*REQUEST, "/send", f"/attach {invalid}", f"/attach {invalid}", "/exit"],
        session_id="G30-07-DUPLICATE",
    )
    state = result["platform_core_project_services_context"][
        "artifact_attachment_retry_state"
    ]

    assert "duplicate attachment attempt rejected" in "\n".join(output)
    assert state["attempt_number"] == 1
    assert reconstruct_artifact_attachment_retry(state["attempt_reference"])[
        "attempt_count"
    ] == 1


def test_cancelled_and_completed_clarifications_reject_retry(tmp_path: Path) -> None:
    cancelled_root = tmp_path / "cancelled"
    cancelled_invalid = _reference(cancelled_root, "invalid", invalid=True)
    cancelled_valid = _reference(cancelled_root, "valid")
    cancelled, cancelled_output = _run(
        cancelled_root,
        [
            *REQUEST,
            "/send",
            f"/attach {cancelled_invalid}",
            "/cancel",
            f"/attach {cancelled_valid}",
            "/exit",
        ],
        session_id="G30-07-CANCELLED",
    )
    completed_root = tmp_path / "completed"
    completed_invalid = _reference(completed_root, "invalid", invalid=True)
    completed_valid = _reference(completed_root, "valid")
    completed, completed_output = _run(
        completed_root,
        [
            *REQUEST,
            "/send",
            f"/attach {completed_invalid}",
            f"/attach {completed_valid}",
            f"/attach {completed_valid}",
            "/exit",
        ],
        session_id="G30-07-COMPLETED",
    )

    assert "No active Platform Core clarification" in "\n".join(cancelled_output)
    assert "No active Platform Core clarification" in "\n".join(completed_output)
    assert cancelled["submitted_message_count"] == 2
    assert completed["submitted_message_count"] == 3


def test_wrong_session_owner_and_slot_retry_state_fail_closed(tmp_path: Path) -> None:
    result, _output = _invalid_only(tmp_path)
    context = result["platform_core_project_services_context"]
    envelope = context["operational_clarification_envelope"]
    state = context["artifact_attachment_retry_state"]

    with pytest.raises(FailClosedRuntimeError, match="cross-session"):
        validate_operational_clarification_envelope(
            envelope,
            expected_session_id="WRONG-SESSION",
        )

    owner = deepcopy(state)
    owner["clarification_owner"] = "SUBSTITUTED_OWNER"
    owner["artifact_hash"] = replay_hash(
        {key: value for key, value in owner.items() if key != "artifact_hash"}
    )
    with pytest.raises(FailClosedRuntimeError, match="owner substitution"):
        validate_artifact_attachment_retry_state(owner)

    slot = deepcopy(state)
    slot["semantic_slot"] = "desired_outcome"
    slot["artifact_hash"] = replay_hash(
        {key: value for key, value in slot.items() if key != "artifact_hash"}
    )
    with pytest.raises(FailClosedRuntimeError, match="slot substitution"):
        validate_artifact_attachment_retry_state(slot)


def test_stale_clarification_retry_fails_closed(tmp_path: Path) -> None:
    result, _output = _invalid_only(tmp_path)
    context = result["platform_core_project_services_context"]
    turn = deepcopy(context["operational_turn_binding"])
    turn["originating_clarification_envelope_hash"] = replay_hash("stale")
    turn["artifact_hash"] = replay_hash(
        {key: value for key, value in turn.items() if key != "artifact_hash"}
    )

    with pytest.raises(FailClosedRuntimeError, match="clarification substitution"):
        from aigol.runtime.platform_core_project_services import (
            validate_operational_turn_binding,
        )

        validate_operational_turn_binding(turn)


@pytest.mark.parametrize(
    "tamper",
    ["removed", "reordered", "substituted"],
)
def test_retry_replay_rejects_removed_reordered_or_substituted_attempts(
    tmp_path: Path,
    tamper: str,
) -> None:
    result, _output = _invalid_then_valid(tmp_path)
    state = result["platform_core_project_services_context"][
        "artifact_attachment_retry_state"
    ]
    attempt_path = Path(state["attempt_reference"])
    candidate = json.loads(attempt_path.read_text(encoding="utf-8"))
    if tamper == "removed":
        candidate["prior_attempt_reference"] = None
    elif tamper == "reordered":
        candidate["attempt_number"] = 1
    else:
        candidate["ingress_resolution_hash"] = replay_hash("substituted")
    attempt_path.write_text(json.dumps(candidate), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError):
        reconstruct_artifact_attachment_retry(attempt_path)


def test_ai_cli_retains_no_retry_validation_or_semantic_authority(
    tmp_path: Path,
) -> None:
    result, _output = _invalid_then_valid(tmp_path)
    context = result["platform_core_project_services_context"]
    state = context["artifact_attachment_retry_state"]

    assert state["platform_core_retry_authority"] is True
    assert state["human_interface_retry_authority"] is False
    assert result["aicli_authorizes"] is False
    assert result["aicli_executes"] is False
    assert result["aicli_owns_artifact_resolution"] is False
    assert result["aicli_owns_artifact_validation"] is False
    assert result["aicli_owns_artifact_selection"] is False
