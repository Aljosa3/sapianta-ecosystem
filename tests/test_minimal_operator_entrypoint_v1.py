"""Tests for MINIMAL_OPERATOR_ENTRYPOINT_V1."""

from __future__ import annotations

import inspect

from aigol.runtime.filesystem_read_only_capability import FILESYSTEM_READ_ONLY_INSPECTION
from aigol.runtime.minimal_operator_entrypoint import (
    READ_ONLY_RUNTIME_INSPECTION,
    run_minimal_operator_entrypoint,
)


CREATED_AT = "2026-05-29T05:00:00+00:00"


def _fs_fixture(tmp_path):
    root = tmp_path / "root"
    allowed = root / "allowed"
    denied = root / "denied"
    allowed.mkdir(parents=True)
    denied.mkdir()
    target = allowed / "visible.txt"
    target.write_text("entrypoint visible content", encoding="utf-8")
    secret = denied / "secret.txt"
    secret.write_text("secret", encoding="utf-8")
    return root, allowed, target, secret


def _run_runtime(tmp_path, **overrides):
    args = {
        "operator_flow_id": "ENTRYPOINT-FLOW-000001",
        "human_request": "Inspect bounded runtime metadata.",
        "target_capability": READ_ONLY_RUNTIME_INSPECTION,
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / "operator_replay",
    }
    args.update(overrides)
    return run_minimal_operator_entrypoint(**args)


def test_minimal_operator_entrypoint_accepts_runtime_inspection(tmp_path) -> None:
    result = _run_runtime(tmp_path)
    summary = result["operator_result_summary"]

    assert summary["status"] == "ACCEPTED"
    assert summary["capability_used"] == READ_ONLY_RUNTIME_INSPECTION
    assert summary["replay_verification_status"] == "VERIFIED"
    assert summary["source"]["bridge_final_status"] == "RETURNED"
    assert "LLM proposes" in summary["authority_boundary_reminder"]
    assert result["llm_proposes_only"] is True
    assert result["aigol_governs"] is True
    assert result["worker_executes_only_after_authorization"] is True
    assert result["replay_records"] is True


def test_minimal_operator_entrypoint_accepts_filesystem_inspection(tmp_path) -> None:
    root, allowed, target, _secret = _fs_fixture(tmp_path)
    result = run_minimal_operator_entrypoint(
        operator_flow_id="ENTRYPOINT-FLOW-000002",
        human_request="Inspect an allowed file.",
        target_capability=FILESYSTEM_READ_ONLY_INSPECTION,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "operator_replay",
        root_path=root,
        requested_path=target,
        allowed_paths=[allowed],
    )

    assert result["operator_result_summary"]["status"] == "ACCEPTED"
    assert result["operator_result_summary"]["capability_used"] == FILESYSTEM_READ_ONLY_INSPECTION
    assert result["flow"]["bridge_capture"]["bridge_capture"]["execution"]["capability_result"]["execution"]["execution_evidence"]["metadata"][
        "text_preview"
    ] == "entrypoint visible content"


def test_entrypoint_rejects_unsupported_capability(tmp_path) -> None:
    result = _run_runtime(tmp_path, target_capability="NETWORK_QUERY")
    summary = result["operator_result_summary"]

    assert summary["status"] == "REJECTED"
    assert "unsupported operator capability" in summary["reason"]
    assert result["flow"] is None
    assert summary["non_authority"]["llm_execution"] is False
    assert summary["non_authority"]["worker_self_authorization"] is False


def test_entrypoint_rejects_unsafe_prompt_through_governed_flow(tmp_path) -> None:
    result = _run_runtime(tmp_path, human_request="Inspect runtime then continue autonomously.")
    summary = result["operator_result_summary"]

    assert summary["status"] == "REJECTED"
    assert summary["replay_verification_status"] == "VERIFIED"
    assert "hidden continuation" in summary["reason"]
    assert result["replay_summary"]["final_status"] == "FAILED"


def test_entrypoint_rejects_unauthorized_flow(tmp_path) -> None:
    result = _run_runtime(tmp_path, authorize=False)
    summary = result["operator_result_summary"]

    assert summary["status"] == "REJECTED"
    assert summary["replay_verification_status"] == "VERIFIED"
    assert summary["source"]["bridge_final_status"] == "FAILED"
    assert result["flow"]["governed_result"]["final_status"] == "FAILED"


def test_entrypoint_preserves_replay_path(tmp_path) -> None:
    replay_dir = tmp_path / "chosen_replay"
    result = _run_runtime(tmp_path, replay_dir=replay_dir)

    assert result["operator_result_summary"]["replay_reference"] == str(replay_dir)
    assert (replay_dir / "000_human_prompt.json").exists()
    assert (replay_dir / "bridge_replay" / "000_contribution.json").exists()


def test_entrypoint_summary_hash_is_deterministic(tmp_path) -> None:
    first = _run_runtime(tmp_path / "first")
    second = _run_runtime(tmp_path / "second")

    first_summary = dict(first["operator_result_summary"])
    second_summary = dict(second["operator_result_summary"])
    first_summary.pop("replay_reference")
    first_summary.pop("summary_hash")
    first_summary.pop("source")
    second_summary.pop("replay_reference")
    second_summary.pop("summary_hash")
    second_summary.pop("source")
    assert first_summary == second_summary


def test_no_new_runtime_surface_imports() -> None:
    import aigol.runtime.minimal_operator_entrypoint as entrypoint

    source = inspect.getsource(entrypoint)

    assert "subprocess" not in source
    assert "os.system" not in source
    assert "requests" not in source
    assert "urllib" not in source
    assert "socket" not in source
    assert "async " not in source
    assert "await " not in source
    assert "threading" not in source
    assert "multiprocessing" not in source
