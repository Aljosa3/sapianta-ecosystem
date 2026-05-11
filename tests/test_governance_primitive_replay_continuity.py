from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from runtime.governance.preview_runtime import (
    PreviewRuntimeRequest,
    describe_preview_lifecycle,
    validate_preview_request,
)
from runtime.governance.primitive_replay import CANONICAL_REPLAY_FIELDS
from runtime.governance.test_execution import (
    GovernedTestExecutionRequest,
    describe_test_execution_scope,
    validate_test_execution_request,
)


def test_preview_and_test_primitives_share_canonical_replay_fields() -> None:
    preview = validate_preview_request(PreviewRuntimeRequest()).to_dict()
    test = validate_test_execution_request(GovernedTestExecutionRequest()).to_dict()

    for field in CANONICAL_REPLAY_FIELDS:
        assert field in preview
        assert field in test


def test_scope_descriptions_share_lineage_and_scope_hash() -> None:
    preview = describe_preview_lifecycle()
    test = describe_test_execution_scope()

    assert "replay_lineage" in preview
    assert "replay_lineage" in test
    assert "scope_hash" in preview
    assert "scope_hash" in test
    assert preview["scope_hash"] != test["scope_hash"]


def test_non_execution_markers_remain_distinct_and_visible() -> None:
    preview = validate_preview_request(PreviewRuntimeRequest()).to_dict()
    test = validate_test_execution_request(GovernedTestExecutionRequest()).to_dict()

    assert preview["server_started"] is False
    assert test["executed"] is False


def test_test_execution_request_hash_uses_full_request_payload() -> None:
    runner_change = validate_test_execution_request(
        GovernedTestExecutionRequest(runner="python")
    )
    target_change = validate_test_execution_request(
        GovernedTestExecutionRequest(test_target="tests/test_governed_capability_memory.py")
    )

    assert runner_change.request_hash != target_change.request_hash
    assert runner_change.command == ()
    assert target_change.command == ()
