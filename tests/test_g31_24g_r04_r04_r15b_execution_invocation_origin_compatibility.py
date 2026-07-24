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


R14B_CERTIFIED_INVOCATION_ORIGIN = "PLATFORM_CORE_G31_INVOCATION_BINDING"


def _start_current_chain(tmp_path, *, origin: str) -> tuple[dict, dict, dict]:
    assignment = _current_assignment()
    dispatch = _current_dispatch(assignment)
    invocation = _current_invocation(dispatch)
    invocation["invoked_by"] = origin
    invocation["artifact_hash"] = replay_hash(
        {key: value for key, value in invocation.items() if key != "artifact_hash"}
    )
    invocation_replay = _current_invocation_replay(invocation)
    original_invocation = deepcopy(invocation)
    capture = start_execution(
        execution_id=f"R15B-EXECUTION-{origin}",
        invocation_artifact=invocation,
        invocation_replay=invocation_replay,
        dispatch_artifact=dispatch,
        worker_assignment_artifact=assignment,
        canonical_chain_id=CANONICAL_CHAIN_ID,
        execution_metadata=_metadata(),
        execution_context=_current_execution_context(invocation),
        started_by="AIGOL",
        started_at=CREATED_AT,
        replay_reference=f"R15B-REPLAY-{origin}",
        replay_dir=tmp_path / origin,
    )
    return capture, invocation, original_invocation


def test_execution_runtime_accepts_exact_r14b_origin_without_rewriting_invocation(
    tmp_path,
) -> None:
    capture, invocation, original_invocation = _start_current_chain(
        tmp_path,
        origin=R14B_CERTIFIED_INVOCATION_ORIGIN,
    )

    execution = capture["execution_artifact"]
    assert execution["execution_status"] == EXECUTING
    assert execution["worker_invocation_reference"] == invocation[
        "worker_invocation_id"
    ]
    assert execution["worker_invocation_hash"] == invocation["artifact_hash"]
    assert invocation == original_invocation
    assert invocation["invoked_by"] == R14B_CERTIFIED_INVOCATION_ORIGIN


@pytest.mark.parametrize("origin", ("AIGOL", "AIGOL_GOVERNANCE"))
def test_execution_runtime_preserves_existing_certified_origins(
    tmp_path, origin: str
) -> None:
    capture, invocation, original_invocation = _start_current_chain(
        tmp_path,
        origin=origin,
    )

    assert capture["execution_artifact"]["execution_status"] == EXECUTING
    assert invocation == original_invocation


def test_execution_runtime_rejects_every_unrecognized_origin_before_replay_write(
    tmp_path,
) -> None:
    assignment = _current_assignment()
    dispatch = _current_dispatch(assignment)
    invocation = _current_invocation(dispatch)
    invocation["invoked_by"] = "UNRECOGNIZED_G31_INVOCATION_ORIGIN"
    invocation["artifact_hash"] = replay_hash(
        {key: value for key, value in invocation.items() if key != "artifact_hash"}
    )
    destination = tmp_path / "rejected"

    with pytest.raises(
        FailClosedRuntimeError,
        match="invocation must be AiGOL-created",
    ):
        start_execution(
            execution_id="R15B-EXECUTION-REJECTED",
            invocation_artifact=invocation,
            invocation_replay=_current_invocation_replay(invocation),
            dispatch_artifact=dispatch,
            worker_assignment_artifact=assignment,
            canonical_chain_id=CANONICAL_CHAIN_ID,
            execution_metadata=_metadata(),
            execution_context=_current_execution_context(invocation),
            started_by="AIGOL",
            started_at=CREATED_AT,
            replay_reference="R15B-REPLAY-REJECTED",
            replay_dir=destination,
        )

    assert not destination.exists()
