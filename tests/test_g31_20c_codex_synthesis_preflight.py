from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from aigol.runtime.codex_worker_activation_binding_runtime import (
    CODEX_SYNTHESIS_MAXIMUM_CHARACTER_COUNT,
    CODEX_SYNTHESIS_PREFIX,
    prepare_codex_worker_activation_review,
    preflight_codex_worker_synthesis,
)
from aigol.runtime.models import FailClosedRuntimeError
from test_g31_17b_governed_execution_to_codex_worker_activation_binding import (
    RecordingRunner,
    _activate_direct,
    _run,
    _two_decisions,
)


PREVIOUS_234_CHARACTER_REQUEST = (
    "Improve the human interface terminal summary behavior. Read KNOWN_INPUT.txt "
    "and return one short benign read-only validation result containing its exact "
    "text. Do not modify files, install packages, run tests, or start another process."
)


def _bounded_raw(length: int) -> str:
    marker = "validate runtime "
    return marker + ("x" * (length - len(marker)))


def _prepare(runtime: dict, root: Path, workspace: Path, supplied: dict) -> dict:
    return prepare_codex_worker_activation_review(
        governed_execution_capture=runtime["governed_worker_execution_capture"],
        execution_candidate_capture=runtime["worker_execution_candidate_capture"],
        session_root=root,
        workspace=workspace,
        created_at="2026-07-18T00:00:00Z",
        synthesis_preflight_capture=supplied,
    )


def test_raw_220_is_eligible_and_final_request_is_exactly_240_characters() -> None:
    capture = preflight_codex_worker_synthesis(_bounded_raw(220))

    assert CODEX_SYNTHESIS_PREFIX == "runtime validation: "
    assert len(CODEX_SYNTHESIS_PREFIX) == 20
    assert CODEX_SYNTHESIS_MAXIMUM_CHARACTER_COUNT == 240
    assert capture["synthesis_preflight_performed"] is True
    assert capture["synthesis_within_bound"] is True
    assert capture["synthesis_preflight_status"] == "SYNTHESIS_PREFLIGHT_READY"
    assert capture["raw_character_count"] == 220
    assert capture["prefix_character_count"] == 20
    assert capture["final_character_count"] == 240
    assert capture["maximum_character_count"] == 240


def test_raw_221_fails_closed_before_any_human_decision() -> None:
    capture = preflight_codex_worker_synthesis(_bounded_raw(221))

    assert capture["synthesis_preflight_status"] == "SYNTHESIS_PREFLIGHT_FAILED_CLOSED"
    assert capture["synthesis_within_bound"] is False
    assert capture["raw_character_count"] == 221
    assert capture["final_character_count"] == 241
    assert capture["human_decision_count"] == 0
    assert capture["process_start_count"] == 0


def test_previous_234_character_request_fails_in_aicli_with_zero_approvals(
    tmp_path: Path,
) -> None:
    runner = RecordingRunner()
    result, output, _, _ = _run(
        tmp_path,
        "G31-20C-PREVIOUS-234",
        [PREVIOUS_234_CHARACTER_REQUEST, "/send", "/approve", "/exit"],
        runner,
    )

    assert len(PREVIOUS_234_CHARACTER_REQUEST) == 234
    assert result["approval_count"] == 0
    assert result["synthesis_preflight_performed"] is True
    assert result["synthesis_within_bound"] is False
    assert result["raw_character_count"] == 234
    assert result["prefix_character_count"] == 20
    assert result["final_character_count"] == 254
    assert result["maximum_character_count"] == 240
    assert result["human_decision_count"] == 0
    assert result["process_start_count"] == 0
    assert runner.calls == []
    rendered = "\n".join(output)
    assert rendered.index("Final characters: 254") < rendered.index(
        "Canonical CODEX synthesis preflight failed closed before human approval."
    )
    assert "Type /approve to continue" not in rendered


@pytest.mark.parametrize(
    ("field", "substitute"),
    (
        ("canonical_prefix", "runtime validation substituted: "),
        ("maximum_character_count", 241),
        ("raw_character_count", 1),
        ("final_character_count", 1),
    ),
)
def test_preflight_prefix_limit_and_length_substitution_fail_closed(
    tmp_path: Path,
    field: str,
    substitute: object,
) -> None:
    runtime, root, workspace = _two_decisions(tmp_path, f"G31-20C-{field}")
    changed = deepcopy(runtime["codex_synthesis_preflight_capture"])
    changed[field] = substitute

    with pytest.raises(
        FailClosedRuntimeError,
        match="synthesis preflight or request was substituted",
    ):
        _prepare(runtime, root, workspace, changed)


def test_post_preflight_request_substitution_fails_closed(tmp_path: Path) -> None:
    runtime, root, workspace = _two_decisions(tmp_path, "G31-20C-POST-PREFLIGHT")
    changed = preflight_codex_worker_synthesis(
        "Validate runtime behavior for a different exact request."
    )

    with pytest.raises(
        FailClosedRuntimeError,
        match="synthesis preflight or request was substituted",
    ):
        _prepare(runtime, root, workspace, changed)


def test_exact_synthesized_request_hash_binds_review_approval_and_dispatch(
    tmp_path: Path,
) -> None:
    runtime, root, workspace = _two_decisions(tmp_path, "G31-20C-HASH-BINDING")
    preflight = runtime["codex_synthesis_preflight_capture"]
    review_capture = _prepare(runtime, root, workspace, preflight)
    review = review_capture["activation_review_artifact"]
    interpreted = review["interpreted_intent"]
    runner = RecordingRunner(stdout="Authentic bounded CODEX semantic output.")
    activation = _activate_direct(
        runtime, root, workspace, root / "activation", runner
    )
    approval = activation["activation_approval_artifact"]

    assert interpreted["synthesis_preflight_hash"] == preflight["synthesis_preflight_hash"]
    assert interpreted["final_synthesized_request_sha256"] == preflight[
        "final_synthesized_request_sha256"
    ]
    assert approval["synthesis_preflight_hash"] == preflight["synthesis_preflight_hash"]
    assert approval["final_synthesized_request_sha256"] == preflight[
        "final_synthesized_request_sha256"
    ]
    assert activation["codex_execution_request"]["handoff_package"] == preflight[
        "governed_codex_handoff"
    ]
    assert runner.calls[0][0][2] == preflight["governed_codex_handoff"]["codex_prompt"]
