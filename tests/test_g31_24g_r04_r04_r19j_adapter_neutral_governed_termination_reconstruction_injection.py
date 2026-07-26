from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from aigol.runtime import governed_termination_runtime as termination
from aigol.runtime import human_decision_runtime as decision
from aigol.runtime import (
    filesystem_replace_worker_schema_aware_authorization_lineage_resolver_runtime
    as resolver,
)
from aigol.runtime.models import FailClosedRuntimeError
from test_g31_24g_r04_r04_r04_r01_common_entry_adapter_repair import (
    InMemoryAdapter,
    _pending_state,
)


def _review(result: dict) -> tuple[dict, str]:
    capture = result[
        "filesystem_replace_worker_post_execution_replay_review"
    ]
    return (
        capture["post_execution_replay_review_artifact"],
        result[
            "filesystem_replace_worker_post_execution_replay_review_replay_reference"
        ],
    )


def test_filesystem_reconstructor_is_supplied_per_termination_invocation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, "R19J-INJECTION")
    result = InMemoryAdapter(root).transport(
        state,
        decision.MUTATION_APPROVED,
    )
    review, review_replay = _review(result)
    calls = 0

    def counted(reference):
        nonlocal calls
        calls += 1
        return (
            resolver.reconstruct_schema_aware_post_execution_replay_review(
                reference
            )
        )

    replay_dir = root / "R19J-GOVERNED-TERMINATION"
    capture = termination.terminate_reviewed_operation(
        governed_termination_id="R19J-GOVERNED-TERMINATION",
        post_execution_replay_review_artifact=review,
        post_execution_replay_review_replay_reference=review_replay,
        terminated_by="AIGOL_GOVERNANCE",
        terminated_at="2026-07-26T00:00:00Z",
        replay_dir=replay_dir,
        replay_review_reconstructor=counted,
    )
    reconstructed = termination.reconstruct_governed_termination_replay(
        replay_dir,
        replay_review_reconstructor=counted,
    )

    assert calls == 2
    assert capture["termination_status"] == termination.TERMINATED
    assert reconstructed["termination_status"] == termination.TERMINATED
    assert reconstructed["post_execution_replay_reviewed"] is True
    assert reconstructed["terminated"] is True
    assert reconstructed["governance_mutated"] is False
    assert reconstructed["replay_mutated"] is False
    assert len(list(replay_dir.glob("*.json"))) == 4


def test_unsupported_reconstructor_fails_closed_without_termination(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, "R19J-UNSUPPORTED")
    result = InMemoryAdapter(root).transport(
        state,
        decision.MUTATION_APPROVED,
    )
    review, review_replay = _review(result)

    def unsupported(_reference):
        raise FailClosedRuntimeError(
            "unsupported immutable Authorization lineage"
        )

    capture = termination.terminate_reviewed_operation(
        governed_termination_id="R19J-UNSUPPORTED-TERMINATION",
        post_execution_replay_review_artifact=review,
        post_execution_replay_review_replay_reference=review_replay,
        terminated_by="AIGOL_GOVERNANCE",
        terminated_at="2026-07-26T00:00:00Z",
        replay_dir=root / "R19J-UNSUPPORTED-TERMINATION",
        replay_review_reconstructor=unsupported,
    )

    assert capture["termination_status"] == termination.FAILED_CLOSED
    assert capture["governed_termination_artifact"] is None
    assert capture["terminated"] is False
    assert "unsupported immutable Authorization lineage" in (
        capture["failure_reason"]
    )


def test_invalid_reconstructor_is_normalized_to_fail_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, "R19J-INVALID")
    result = InMemoryAdapter(root).transport(
        state,
        decision.MUTATION_APPROVED,
    )
    review, review_replay = _review(result)

    capture = termination.terminate_reviewed_operation(
        governed_termination_id="R19J-INVALID-TERMINATION",
        post_execution_replay_review_artifact=review,
        post_execution_replay_review_replay_reference=review_replay,
        terminated_by="AIGOL_GOVERNANCE",
        terminated_at="2026-07-26T00:00:00Z",
        replay_dir=root / "R19J-INVALID-TERMINATION",
        replay_review_reconstructor=None,  # type: ignore[arg-type]
    )

    assert capture["termination_status"] == termination.FAILED_CLOSED
    assert capture["governed_termination_artifact"] is None
    assert "reconstructor is invalid" in capture["failure_reason"]


def test_termination_dependency_is_adapter_neutral_and_invocation_scoped() -> None:
    source = inspect.getsource(termination)
    generic = resolver.replay_review.reconstruct_post_execution_replay_review

    assert (
        termination.reconstruct_post_execution_replay_review is generic
    )
    assert (
        "filesystem_replace_worker_schema_aware_authorization_lineage"
        not in source
    )
    assert "ReplayReviewReconstructor = Callable" in source
    assert "replay_review_reconstructor:" in source
    assert "registry" not in source.lower()
    assert "contextmanager" not in source
    assert "RLock" not in source
