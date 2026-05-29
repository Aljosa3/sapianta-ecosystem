"""Tests for GOVERNED_RESULT_SUMMARY_V1."""

from __future__ import annotations

import inspect

import pytest

from aigol.runtime.governed_result_summary import (
    ACCEPTED,
    REJECTED,
    create_governed_failure_summary,
    create_governed_result_summary,
    render_governed_result_summary,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


def _governed_result(**overrides):
    result = {
        "operator_flow_id": "SUMMARY-FLOW-000001",
        "final_status": "COMPLETED",
        "target_capability": "READ_ONLY_RUNTIME_INSPECTION",
        "governed_return": "human prompt completed through governed read-only result",
        "artifact_hash": "sha256:governed",
    }
    result.update(overrides)
    return result


def _replay_summary(**overrides):
    summary = {
        "append_only_valid": True,
        "replay_artifact_count": 4,
        "replay_hash": "sha256:replay",
        "bridge_replay": {"final_status": "RETURNED"},
    }
    summary.update(overrides)
    return summary


def test_governed_result_summary_contains_required_operator_fields(tmp_path) -> None:
    summary = create_governed_result_summary(
        operator_flow_id="SUMMARY-FLOW-000001",
        human_request="Inspect runtime metadata.",
        capability_used="READ_ONLY_RUNTIME_INSPECTION",
        replay_reference=tmp_path / "replay",
        governed_result=_governed_result(),
        replay_summary=_replay_summary(),
    )

    assert summary["status"] == ACCEPTED
    assert summary["reason"] == "human prompt completed through governed read-only result"
    assert summary["capability_used"] == "READ_ONLY_RUNTIME_INSPECTION"
    assert summary["replay_reference"] == str(tmp_path / "replay")
    assert summary["replay_verification_status"] == "VERIFIED"
    assert "LLM proposes" in summary["authority_boundary_reminder"]
    assert "operator replay artifacts=4" in summary["evidence_summary"]
    assert summary["recommended_next_action"] == "Use the governed result and retain the replay reference for audit."


def test_governed_rejection_summary_recommends_bounded_retry(tmp_path) -> None:
    summary = create_governed_result_summary(
        operator_flow_id="SUMMARY-FLOW-000001",
        human_request="Inspect runtime metadata.",
        capability_used="READ_ONLY_RUNTIME_INSPECTION",
        replay_reference=tmp_path / "replay",
        governed_result=_governed_result(final_status="FAILED", failure_reason="hidden continuation attempt detected"),
        replay_summary=_replay_summary(bridge_replay={"final_status": "FAILED"}),
    )

    assert summary["status"] == REJECTED
    assert summary["reason"] == "hidden continuation attempt detected"
    assert summary["recommended_next_action"] == "Remove continuation language and retry as a single bounded request."


def test_failure_summary_handles_pre_replay_rejection(tmp_path) -> None:
    summary = create_governed_failure_summary(
        operator_flow_id="SUMMARY-FLOW-000002",
        human_request="Inspect runtime metadata.",
        capability_used="NETWORK_QUERY",
        replay_reference=tmp_path / "replay",
        failure_reason="unsupported operator capability",
    )

    assert summary["status"] == REJECTED
    assert summary["replay_verification_status"] == "UNVERIFIED"
    assert summary["source"]["replay_artifact_count"] == 0
    assert "unsupported operator capability" in summary["reason"]


def test_rendered_summary_is_stable_and_human_readable(tmp_path) -> None:
    summary = create_governed_result_summary(
        operator_flow_id="SUMMARY-FLOW-000001",
        human_request="Inspect runtime metadata.",
        capability_used="READ_ONLY_RUNTIME_INSPECTION",
        replay_reference=tmp_path / "replay",
        governed_result=_governed_result(),
        replay_summary=_replay_summary(),
    )
    rendered = render_governed_result_summary(summary)

    assert "Status: ACCEPTED" in rendered
    assert "Capability Used: READ_ONLY_RUNTIME_INSPECTION" in rendered
    assert "Replay Verification Status: VERIFIED" in rendered
    assert "Recommended Next Action:" in rendered


def test_summary_hash_is_deterministic(tmp_path) -> None:
    summary = create_governed_result_summary(
        operator_flow_id="SUMMARY-FLOW-000001",
        human_request="  Inspect runtime metadata. ",
        capability_used="READ_ONLY_RUNTIME_INSPECTION",
        replay_reference=tmp_path / "replay",
        governed_result=_governed_result(),
        replay_summary=_replay_summary(),
    )
    without_hash = dict(summary)
    summary_hash = without_hash.pop("summary_hash")

    assert summary_hash == replay_hash(without_hash)


def test_render_rejects_tampered_summary(tmp_path) -> None:
    summary = create_governed_result_summary(
        operator_flow_id="SUMMARY-FLOW-000001",
        human_request="Inspect runtime metadata.",
        capability_used="READ_ONLY_RUNTIME_INSPECTION",
        replay_reference=tmp_path / "replay",
        governed_result=_governed_result(),
        replay_summary=_replay_summary(),
    )
    summary["status"] = REJECTED

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        render_governed_result_summary(summary)


def test_no_new_runtime_surface_imports() -> None:
    import aigol.runtime.governed_result_summary as summary

    source = inspect.getsource(summary)

    assert "subprocess" not in source
    assert "os.system" not in source
    assert "requests" not in source
    assert "urllib" not in source
    assert "socket" not in source
    assert "async " not in source
    assert "await " not in source
    assert "threading" not in source
    assert "multiprocessing" not in source
