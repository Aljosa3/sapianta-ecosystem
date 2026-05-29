"""Tests for HUMAN_PROMPT_TO_GOVERNED_READONLY_RESULT_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.filesystem_read_only_capability import FILESYSTEM_READ_ONLY_INSPECTION
from aigol.runtime.human_prompt_to_governed_readonly_result import (
    OPERATOR_COMPLETED,
    OPERATOR_FAILED,
    READ_ONLY_RUNTIME_INSPECTION,
    reconstruct_human_prompt_governed_result_replay,
    run_human_prompt_to_governed_readonly_result,
)
from aigol.runtime.models import FailClosedRuntimeError


CREATED_AT = "2026-05-29T04:00:00+00:00"


def _fs_fixture(tmp_path):
    root = tmp_path / "root"
    allowed = root / "allowed"
    denied = root / "denied"
    allowed.mkdir(parents=True)
    denied.mkdir()
    target = allowed / "visible.txt"
    target.write_text("operator visible content", encoding="utf-8")
    secret = denied / "secret.txt"
    secret.write_text("secret", encoding="utf-8")
    return root, allowed, target, secret


def _run_runtime(tmp_path, **overrides):
    args = {
        "operator_flow_id": "OPERATOR-FLOW-000001",
        "human_prompt": "Inspect bounded runtime metadata.",
        "target_capability": READ_ONLY_RUNTIME_INSPECTION,
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / "operator_replay",
    }
    args.update(overrides)
    return run_human_prompt_to_governed_readonly_result(**args)


def test_human_prompt_to_runtime_readonly_result_completes(tmp_path) -> None:
    capture = _run_runtime(tmp_path)
    replay = reconstruct_human_prompt_governed_result_replay(tmp_path / "operator_replay")

    assert capture["governed_result"]["final_status"] == OPERATOR_COMPLETED
    assert capture["governed_result"]["llm_proposes_only"] is True
    assert capture["governed_result"]["aigol_governs"] is True
    assert capture["governed_result"]["worker_executes_only_after_authorization"] is True
    assert replay["final_status"] == OPERATOR_COMPLETED
    assert replay["bridge_replay"]["target_capability"] == READ_ONLY_RUNTIME_INSPECTION
    assert replay["bridge_replay"]["final_status"] == "RETURNED"


def test_human_prompt_to_filesystem_readonly_result_completes(tmp_path) -> None:
    root, allowed, target, _secret = _fs_fixture(tmp_path)
    capture = run_human_prompt_to_governed_readonly_result(
        operator_flow_id="OPERATOR-FLOW-000002",
        human_prompt="Inspect an allowed file.",
        target_capability=FILESYSTEM_READ_ONLY_INSPECTION,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "operator_replay",
        root_path=root,
        requested_path=target,
        allowed_paths=[allowed],
    )

    bridge_execution = capture["bridge_capture"]["bridge_capture"]["execution"]
    capability_execution = bridge_execution["capability_result"]["execution"]
    assert capture["governed_result"]["final_status"] == OPERATOR_COMPLETED
    assert capability_execution["execution_evidence"]["metadata"]["text_preview"] == "operator visible content"
    assert capture["governed_result"]["filesystem_mutation"] is False


def test_flow_records_untrusted_proposal_and_governed_authorization(tmp_path) -> None:
    capture = _run_runtime(tmp_path)

    proposal = capture["cognition_proposal"]
    bridge = capture["bridge_capture"]["bridge_capture"]
    assert proposal["untrusted_proposal_input"] is True
    assert proposal["llm_execution_authority"] is False
    assert proposal["llm_authorization_authority"] is False
    assert bridge["authorization"]["cognition_self_authorized"] is False
    assert bridge["return"]["authorized"] is True


def test_unauthorized_flow_fails_closed(tmp_path) -> None:
    capture = _run_runtime(tmp_path, authorize=False)
    replay = reconstruct_human_prompt_governed_result_replay(tmp_path / "operator_replay")

    assert capture["governed_result"]["final_status"] == OPERATOR_FAILED
    assert capture["bridge_capture"]["bridge_final_status"] == "FAILED"
    assert replay["final_status"] == OPERATOR_FAILED


def test_unsupported_capability_fails_closed_with_replay(tmp_path) -> None:
    capture = _run_runtime(tmp_path, target_capability="NETWORK_QUERY")
    replay = reconstruct_human_prompt_governed_result_replay(tmp_path / "operator_replay")

    assert capture["governed_result"]["final_status"] == OPERATOR_FAILED
    assert "unsupported read-only capability" in capture["governed_result"]["failure_reason"]
    assert replay["final_status"] == OPERATOR_FAILED


def test_unsafe_human_prompt_fails_closed(tmp_path) -> None:
    capture = _run_runtime(tmp_path, human_prompt="Inspect runtime then continue autonomously.")

    assert capture["governed_result"]["final_status"] == OPERATOR_FAILED
    assert "hidden continuation" in capture["governed_result"]["failure_reason"]


def test_filesystem_forbidden_path_fails_closed(tmp_path) -> None:
    root, allowed, _target, secret = _fs_fixture(tmp_path)
    capture = run_human_prompt_to_governed_readonly_result(
        operator_flow_id="OPERATOR-FLOW-000003",
        human_prompt="Inspect an allowed file.",
        target_capability=FILESYSTEM_READ_ONLY_INSPECTION,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "operator_replay",
        root_path=root,
        requested_path=secret,
        allowed_paths=[allowed],
    )

    assert capture["governed_result"]["final_status"] == OPERATOR_FAILED
    assert capture["bridge_capture"]["bridge_final_status"] == "FAILED"


def test_operator_replay_is_append_only(tmp_path) -> None:
    _run_runtime(tmp_path)

    capture = _run_runtime(tmp_path)

    assert capture["governed_result"]["final_status"] == OPERATOR_FAILED
    assert "already exists" in capture["governed_result"]["failure_reason"]


def test_operator_replay_discontinuity_detected(tmp_path) -> None:
    _run_runtime(tmp_path)
    artifact_path = tmp_path / "operator_replay" / "003_governed_result.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    artifact["artifact"]["filesystem_mutation"] = True
    artifact_path.write_text(json.dumps(artifact, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_human_prompt_governed_result_replay(tmp_path / "operator_replay")


def test_no_new_runtime_surface_imports() -> None:
    import aigol.runtime.human_prompt_to_governed_readonly_result as flow

    source = inspect.getsource(flow)

    assert "subprocess" not in source
    assert "os.system" not in source
    assert "requests" not in source
    assert "urllib" not in source
    assert "socket" not in source
    assert "async " not in source
    assert "await " not in source
    assert "threading" not in source
    assert "multiprocessing" not in source
