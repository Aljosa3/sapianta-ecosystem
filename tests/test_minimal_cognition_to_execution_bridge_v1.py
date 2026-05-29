"""Tests for MINIMAL_COGNITION_TO_EXECUTION_BRIDGE_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.filesystem_read_only_capability import FILESYSTEM_READ_ONLY_INSPECTION
from aigol.runtime.minimal_cognition_to_execution_bridge import (
    EXECUTED,
    FAILED,
    READ_ONLY_RUNTIME_INSPECTION,
    RETURNED,
    execute_cognition_to_execution_bridge,
    reconstruct_cognition_execution_bridge_replay,
)
from aigol.runtime.models import FailClosedRuntimeError


CREATED_AT = "2026-05-29T03:00:00+00:00"


def _runtime_output(tmp_path, **overrides) -> dict:
    output = {
        "contribution_id": "COGNITION-CONTRIBUTION-000001",
        "human_prompt": "Inspect bounded runtime metadata.",
        "target_capability": READ_ONLY_RUNTIME_INSPECTION,
        "intent": "inspect runtime metadata",
        "created_at": CREATED_AT,
        "arguments": {
            "capability_replay_dir": str(tmp_path / "capability"),
        },
    }
    output.update(overrides)
    return output


def _filesystem_output(tmp_path, root, allowed, target, **overrides) -> dict:
    output = {
        "contribution_id": "COGNITION-CONTRIBUTION-000002",
        "human_prompt": "Inspect an allowed file.",
        "target_capability": FILESYSTEM_READ_ONLY_INSPECTION,
        "intent": "inspect allowed file",
        "created_at": CREATED_AT,
        "arguments": {
            "capability_replay_dir": str(tmp_path / "capability"),
            "root_path": str(root),
            "requested_path": str(target),
            "allowed_paths": [str(allowed)],
        },
    }
    output.update(overrides)
    return output


def _fs_fixture(tmp_path):
    root = tmp_path / "root"
    allowed = root / "allowed"
    denied = root / "denied"
    allowed.mkdir(parents=True)
    denied.mkdir()
    target = allowed / "visible.txt"
    target.write_text("bridge visible content", encoding="utf-8")
    secret = denied / "secret.txt"
    secret.write_text("secret", encoding="utf-8")
    return root, allowed, target, secret


def _run(tmp_path, output: dict, *, authorize=True) -> dict:
    return execute_cognition_to_execution_bridge(
        bridge_id="BRIDGE-000001",
        execution_id="BRIDGE-EXECUTION-000001",
        request_id="BRIDGE-REQUEST-000001",
        cognition_output=output,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "bridge",
        authorize=authorize,
    )


def test_runtime_inspection_bridge_executes_read_only_capability(tmp_path) -> None:
    capture = _run(tmp_path, _runtime_output(tmp_path))
    replay = reconstruct_cognition_execution_bridge_replay(tmp_path / "bridge")

    assert capture["return"]["state"] == RETURNED
    assert capture["execution"]["state"] == EXECUTED
    assert capture["execution"]["target_capability"] == READ_ONLY_RUNTIME_INSPECTION
    assert capture["execution"]["read_only"] is True
    assert replay["final_status"] == RETURNED
    assert replay["authorized"] is True


def test_filesystem_inspection_bridge_executes_allowed_path(tmp_path) -> None:
    root, allowed, target, _secret = _fs_fixture(tmp_path)
    capture = _run(tmp_path, _filesystem_output(tmp_path, root, allowed, target))

    capability_execution = capture["execution"]["capability_result"]["execution"]
    assert capture["return"]["state"] == RETURNED
    assert capture["execution"]["target_capability"] == FILESYSTEM_READ_ONLY_INSPECTION
    assert capability_execution["execution_evidence"]["metadata"]["text_preview"] == "bridge visible content"


def test_cognition_output_is_untrusted_not_authority(tmp_path) -> None:
    capture = _run(tmp_path, _runtime_output(tmp_path))

    assert capture["contribution"]["untrusted_execution_request_input"] is True
    assert capture["contribution"]["cognition_authority"] is False
    assert capture["authorization"]["cognition_self_authorized"] is False
    assert capture["return"]["cognition_authority"] is False


def test_missing_capability_target_fails_closed(tmp_path) -> None:
    output = _runtime_output(tmp_path)
    output.pop("target_capability")
    capture = _run(tmp_path, output)

    assert capture["return"]["state"] == FAILED
    assert "malformed cognition output" in capture["return"]["failure_reason"]


def test_unsupported_capability_fails_closed(tmp_path) -> None:
    output = _runtime_output(tmp_path, target_capability="NETWORK_QUERY")
    capture = _run(tmp_path, output)

    assert capture["return"]["state"] == FAILED
    assert "unsupported capability" in capture["return"]["failure_reason"]


def test_unauthorized_request_fails_closed(tmp_path) -> None:
    capture = _run(tmp_path, _runtime_output(tmp_path), authorize=False)
    replay = reconstruct_cognition_execution_bridge_replay(tmp_path / "bridge")

    assert capture["return"]["state"] == FAILED
    assert "unauthorized" in capture["return"]["failure_reason"]
    assert replay["final_status"] == FAILED


def test_boundary_violation_from_filesystem_capability_fails_closed(tmp_path) -> None:
    root, allowed, _target, secret = _fs_fixture(tmp_path)
    output = _filesystem_output(tmp_path, root, allowed, secret)
    capture = _run(tmp_path, output)

    assert capture["return"]["state"] == FAILED
    assert "capability execution failed closed" in capture["return"]["failure_reason"]


def test_malformed_cognition_output_fails_closed(tmp_path) -> None:
    output = _runtime_output(tmp_path)
    output["unexpected"] = "field"
    capture = _run(tmp_path, output)

    assert capture["return"]["state"] == FAILED
    assert "malformed cognition output" in capture["return"]["failure_reason"]


def test_hidden_continuation_attempt_fails_closed(tmp_path) -> None:
    output = _runtime_output(tmp_path, intent="inspect runtime then continue autonomously")
    capture = _run(tmp_path, output)

    assert capture["return"]["state"] == FAILED
    assert "hidden continuation" in capture["return"]["failure_reason"]


def test_forbidden_intent_fails_closed(tmp_path) -> None:
    output = _runtime_output(tmp_path, intent="write runtime metadata")
    capture = _run(tmp_path, output)

    assert capture["return"]["state"] == FAILED
    assert "unsupported capability intent" in capture["return"]["failure_reason"]


def test_replay_discontinuity_detected(tmp_path) -> None:
    _run(tmp_path, _runtime_output(tmp_path))
    artifact_path = tmp_path / "bridge" / "004_execution.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    artifact["artifact"]["read_only"] = False
    artifact_path.write_text(json.dumps(artifact, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_cognition_execution_bridge_replay(tmp_path / "bridge")


def test_bridge_replay_ordering_corruption_detected(tmp_path) -> None:
    _run(tmp_path, _runtime_output(tmp_path))
    artifact_path = tmp_path / "bridge" / "003_authorization.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    artifact["replay_step"] = "execution"
    artifact_path.write_text(json.dumps(artifact, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_cognition_execution_bridge_replay(tmp_path / "bridge")


def test_no_expansion_runtime_imports() -> None:
    import aigol.runtime.minimal_cognition_to_execution_bridge as bridge

    source = inspect.getsource(bridge)

    assert "subprocess" not in source
    assert "os.system" not in source
    assert "requests" not in source
    assert "urllib" not in source
    assert "socket" not in source
    assert "async " not in source
    assert "await " not in source
    assert "threading" not in source
    assert "multiprocessing" not in source
