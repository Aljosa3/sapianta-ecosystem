from __future__ import annotations

from copy import deepcopy

import pytest

from aigol.runtime.execution_runtime import EXECUTING, start_execution
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash
from test_execution_runtime_v1 import (
    CANONICAL_CHAIN_ID,
    CREATED_AT,
    _current_assignment,
    _current_dispatch,
    _current_execution_context,
    _current_invocation,
    _current_invocation_replay,
    _metadata,
)


CERTIFIED_ROLE = "WORKER_ROLE"
CERTIFIED_CAPABILITY = "REPLACE_EXISTING_TEXT_FILE"
CERTIFIED_INVOCATION_ORIGIN = "PLATFORM_CORE_G31_INVOCATION_BINDING"


def _rehash(artifact: dict) -> None:
    artifact["artifact_hash"] = replay_hash(
        {key: value for key, value in artifact.items() if key != "artifact_hash"}
    )


def _certified_unequal_chain() -> tuple[dict, dict, dict, dict]:
    assignment = _current_assignment()
    assignment["worker_role"] = CERTIFIED_ROLE
    assignment["capability_id"] = CERTIFIED_CAPABILITY
    _rehash(assignment)
    dispatch = _current_dispatch(assignment)
    invocation = _current_invocation(dispatch)
    invocation["invoked_by"] = CERTIFIED_INVOCATION_ORIGIN
    _rehash(invocation)
    invocation_replay = _current_invocation_replay(invocation)
    return assignment, dispatch, invocation, invocation_replay


def _start(
    tmp_path,
    *,
    assignment: dict,
    dispatch: dict,
    invocation: dict,
    invocation_replay: dict,
    name: str,
) -> dict:
    return start_execution(
        execution_id=f"R15D-EXECUTION-{name}",
        invocation_artifact=invocation,
        invocation_replay=invocation_replay,
        dispatch_artifact=dispatch,
        worker_assignment_artifact=assignment,
        canonical_chain_id=CANONICAL_CHAIN_ID,
        execution_metadata=_metadata(),
        execution_context=_current_execution_context(invocation),
        started_by="AIGOL",
        started_at=CREATED_AT,
        replay_reference=f"R15D-REPLAY-{name}",
        replay_dir=tmp_path / name,
    )


def test_execution_sources_exact_capability_from_validated_assignment(
    tmp_path,
) -> None:
    assignment, dispatch, invocation, invocation_replay = (
        _certified_unequal_chain()
    )
    original_assignment = deepcopy(assignment)
    original_invocation = deepcopy(invocation)

    capture = _start(
        tmp_path,
        assignment=assignment,
        dispatch=dispatch,
        invocation=invocation,
        invocation_replay=invocation_replay,
        name="certified-capability",
    )

    execution = capture["execution_artifact"]
    assert execution["execution_status"] == EXECUTING
    assert assignment["worker_role"] == CERTIFIED_ROLE
    assert assignment["capability_id"] == CERTIFIED_CAPABILITY
    assert "capability_id" not in invocation
    assert execution["capability_id"] == CERTIFIED_CAPABILITY
    assert execution["capability_id"] != CERTIFIED_ROLE
    assert assignment == original_assignment
    assert invocation == original_invocation


def test_invocation_role_cannot_substitute_for_assignment_capability(
    tmp_path,
) -> None:
    assignment, dispatch, invocation, _ = _certified_unequal_chain()
    invocation["capability_id"] = CERTIFIED_ROLE
    _rehash(invocation)
    invocation_replay = _current_invocation_replay(invocation)
    destination = tmp_path / "role-substitution"

    with pytest.raises(FailClosedRuntimeError, match="capability mismatch"):
        _start(
            tmp_path,
            assignment=assignment,
            dispatch=dispatch,
            invocation=invocation,
            invocation_replay=invocation_replay,
            name=destination.name,
        )

    assert not destination.exists()


def test_missing_assignment_capability_fails_before_execution_replay_write(
    tmp_path,
) -> None:
    assignment = _current_assignment()
    assignment["worker_role"] = CERTIFIED_ROLE
    assignment.pop("capability_id")
    _rehash(assignment)
    dispatch = _current_dispatch(assignment)
    invocation = _current_invocation(dispatch)
    invocation["invoked_by"] = CERTIFIED_INVOCATION_ORIGIN
    _rehash(invocation)
    invocation_replay = _current_invocation_replay(invocation)
    destination = tmp_path / "missing-assignment-capability"

    with pytest.raises(FailClosedRuntimeError, match="capability_id is required"):
        _start(
            tmp_path,
            assignment=assignment,
            dispatch=dispatch,
            invocation=invocation,
            invocation_replay=invocation_replay,
            name=destination.name,
        )

    assert not destination.exists()
