"""Tests for the G4-05 live ACLI governed development session entrypoint."""

from __future__ import annotations

import json

import pytest

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.runtime.g4_first_executable_governed_self_development_session import (
    G4_SELF_DEVELOPMENT_SESSION_VERSION,
)
from aigol.runtime.g4_live_acli_governed_development_session_entrypoint import (
    G4_LIVE_ACLI_SESSION_ENTRYPOINT_VERSION,
    LIVE_ACLI_ROUTED_TO_G4_04,
    LIVE_ACLI_SESSION_RECORDED,
    reconstruct_g4_live_acli_governed_development_session_entrypoint_replay,
    run_g4_live_acli_governed_development_session_entrypoint,
)
from aigol.runtime.models import FailClosedRuntimeError


CREATED_AT = "2026-06-30T00:00:00Z"
LIVE_REQUEST = "Add replay evidence for the live ACLI governed development session."


def _run(tmp_path, *, operator_response: str = "confirm") -> dict:
    return run_g4_live_acli_governed_development_session_entrypoint(
        session_id="G4-05-LIVE-SESSION-001",
        operator_request=LIVE_REQUEST,
        operator_response=operator_response,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "g4_05_live",
    )


def test_g4_05_live_acli_routes_real_request_into_g4_04_without_mutation(tmp_path) -> None:
    capture = _run(tmp_path)
    summary = capture["summary_artifact"]

    assert capture["command"] == "aigol g4-live-session"
    assert capture["runtime_version"] == G4_LIVE_ACLI_SESSION_ENTRYPOINT_VERSION
    assert capture["session_status"] == LIVE_ACLI_SESSION_RECORDED
    assert capture["routing_status"] == LIVE_ACLI_ROUTED_TO_G4_04
    assert capture["target_runtime"] == G4_SELF_DEVELOPMENT_SESSION_VERSION
    assert capture["canonical_response_class"] == "CONFIRMATION"
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["approval_created"] is False
    assert capture["authorization_created"] is False
    assert capture["execution_authorized"] is False
    assert capture["repository_mutated"] is False
    assert capture["deployment_performed"] is False
    assert capture["copy_paste_workflow_used"] is False
    assert summary["replay_evidence"]["g4_04_replay_hash"].startswith("sha256:")
    assert summary["governance_evidence"]["mutation_boundary_preserved"] is True


def test_g4_05_replay_reconstructs_live_entrypoint_and_g4_04_route(tmp_path) -> None:
    _run(tmp_path, operator_response="continue")

    replay = reconstruct_g4_live_acli_governed_development_session_entrypoint_replay(tmp_path / "g4_05_live")

    assert replay["runtime_version"] == G4_LIVE_ACLI_SESSION_ENTRYPOINT_VERSION
    assert replay["command"] == "aigol g4-live-session"
    assert replay["session_status"] == LIVE_ACLI_SESSION_RECORDED
    assert replay["routing_status"] == LIVE_ACLI_ROUTED_TO_G4_04
    assert replay["target_runtime"] == G4_SELF_DEVELOPMENT_SESSION_VERSION
    assert replay["canonical_response_class"] == "CONTINUATION"
    assert replay["replay_artifact_count"] == 5
    assert replay["g4_04_replay_artifact_count"] == 6
    assert replay["provider_invoked"] is False
    assert replay["worker_invoked"] is False
    assert replay["approval_created"] is False
    assert replay["authorization_created"] is False
    assert replay["repository_mutated"] is False
    assert replay["deployment_performed"] is False
    assert replay["copy_paste_workflow_used"] is False
    assert replay["replay_hash"].startswith("sha256:")


@pytest.mark.parametrize(
    ("operator_response", "expected_class"),
    [
        ("please clarify", "CLARIFICATION"),
        ("modify scope", "MODIFICATION"),
        ("reject", "REJECTION"),
    ],
)
def test_g4_05_live_acli_preserves_uhcl_response_mapping(
    tmp_path,
    operator_response: str,
    expected_class: str,
) -> None:
    capture = run_g4_live_acli_governed_development_session_entrypoint(
        session_id=f"G4-05-LIVE-{expected_class}",
        operator_request=LIVE_REQUEST,
        operator_response=operator_response,
        created_at=CREATED_AT,
        replay_dir=tmp_path / expected_class.lower(),
    )

    assert capture["canonical_response_class"] == expected_class
    assert capture["execution_intent_status"] == "BLOCKED_PENDING_GOVERNANCE"
    assert capture["repository_mutated"] is False


def test_g4_05_rejects_unmapped_live_human_response(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="does not map"):
        _run(tmp_path, operator_response="sounds interesting")


def test_g4_05_replay_tampering_fails_closed(tmp_path) -> None:
    _run(tmp_path)
    path = tmp_path / "g4_05_live" / "004_live_session_evidence_recorded.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["artifact"]["repository_mutated"] = True
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="replay hash mismatch"):
        reconstruct_g4_live_acli_governed_development_session_entrypoint_replay(tmp_path / "g4_05_live")


def test_g4_05_cli_command_routes_to_live_entrypoint(tmp_path) -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "g4-live-session",
            "--session-id",
            "G4-05-CLI-SESSION-001",
            "--request",
            LIVE_REQUEST,
            "--response",
            "confirm",
            "--runtime-root",
            str(tmp_path / "cli_runtime"),
            "--created-at",
            CREATED_AT,
        ]
    )
    result = run_command(args)
    rendered = render_command_result(result)

    assert result["command"] == "aigol g4-live-session"
    assert result["routing_status"] == LIVE_ACLI_ROUTED_TO_G4_04
    assert result["repository_mutated"] is False
    assert "AIGOL G4 LIVE SESSION" in rendered
    assert "target_runtime: G4_FIRST_EXECUTABLE_GOVERNED_SELF_DEVELOPMENT_SESSION_V1" in rendered
