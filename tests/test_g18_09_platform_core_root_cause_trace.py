from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from aigol.runtime.platform_core_root_cause_trace import (
    ROOT_CAUSE_TRACE_FAILED_CLOSED,
    ROOT_CAUSE_TRACE_READY,
    trace_platform_core_root_cause,
)
from aigol.runtime.platform_capability_certification_registry import is_platform_capability_certified
from aigol.runtime.transport.serialization import replay_hash, write_json_immutable


CREATED_AT = "2026-07-11T00:00:00Z"


def test_trace_from_projected_boolean_result(tmp_path: Path) -> None:
    turn_root = _turn_replay(tmp_path)
    runtime_result = {
        "replay_certification_reached": False,
        "runtime_replay_reference": str(turn_root),
        "runtime_status_projection_evidence": {
            "turn_replay_discovery_used": True,
            "turn_replay_root": str(turn_root),
            "replay_certification_replay_inspected": False,
        },
    }

    trace = trace_platform_core_root_cause(
        observed_field="replay_certification_reached",
        observed_value=False,
        replay_reference=turn_root,
        runtime_result=runtime_result,
        created_at=CREATED_AT,
    )

    assert trace["trace_status"] == ROOT_CAUSE_TRACE_READY
    assert trace["producing_component"] == "HUMAN_INTERFACE_RUNTIME_STATUS_PROJECTION"
    assert trace["source_projection"]["replay_certification_attempted"] is False
    assert trace["source_projection"]["replay_certification_artifact_exists"] is False
    assert trace["missing_evidence"][0]["evidence"] == "replay_certification_artifact"
    assert trace["causal_predecessors"][0]["source_artifact"]["failure_reason"] == "OpenAI provider unavailable"
    assert trace["human_interface_authority"] is False


def test_trace_from_failure_reason(tmp_path: Path) -> None:
    turn_root = _turn_replay(tmp_path)

    trace = trace_platform_core_root_cause(
        failure_reason="OpenAI provider unavailable",
        replay_reference=turn_root,
        created_at=CREATED_AT,
    )

    assert trace["trace_status"] == ROOT_CAUSE_TRACE_READY
    assert trace["observed_result"]["field"] == "failure_reason"
    assert trace["source_artifact"]["failure_reason"] == "OpenAI provider unavailable"
    assert trace["source_artifact"]["artifact_hash"].startswith("sha256:")
    assert trace["runtime_stage"]["source_replay_step"]


def test_trace_from_replay_reference(tmp_path: Path) -> None:
    turn_root = _turn_replay(tmp_path)

    trace = trace_platform_core_root_cause(
        replay_reference=turn_root,
        created_at=CREATED_AT,
    )

    assert trace["trace_status"] == ROOT_CAUSE_TRACE_READY
    assert trace["observed_result"]["field"] == "replay_reference"
    assert trace["replay_source_count"] >= 4
    assert trace["replay_backed"] is True


def test_missing_evidence_fails_closed(tmp_path: Path) -> None:
    trace = trace_platform_core_root_cause(
        observed_field="replay_certification_reached",
        observed_value=False,
        replay_reference=tmp_path / "missing-turn",
        created_at=CREATED_AT,
    )

    assert trace["trace_status"] == ROOT_CAUSE_TRACE_FAILED_CLOSED
    assert trace["fail_closed"] is True
    assert trace["replay_backed"] is False
    assert trace["missing_evidence"][0]["evidence"] == "trace_input_or_replay"


def test_turn_000024_replay_certification_trace() -> None:
    turn_root = Path(".runtime/aicli/AICLI-REFERENCE-SESSION/TURN-000024")
    if not turn_root.exists():
        pytest.skip("TURN-000024 replay evidence is not present in this checkout")

    trace = trace_platform_core_root_cause(
        observed_field="replay_certification_reached",
        observed_value=False,
        replay_reference=turn_root,
        created_at=CREATED_AT,
    )

    assert trace["trace_status"] == ROOT_CAUSE_TRACE_READY
    assert trace["source_projection"]["replay_certification_attempted"] is False
    assert trace["source_projection"]["replay_certification_artifact_exists"] is False
    assert trace["source_projection"]["replay_certification_status"] == "REPLAY_CERTIFICATION_NOT_REACHED"
    assert trace["causal_predecessors"][0]["source_artifact"]["artifact_type"] == (
        "UNIVERSAL_PROVIDER_WORKER_RESULT_ARTIFACT_V1"
    )
    assert trace["causal_predecessors"][0]["source_artifact"]["status"] == "FAILED_CLOSED"
    assert trace["causal_predecessors"][0]["source_artifact"]["failure_reason"] == "OpenAI provider unavailable"
    assert "did not find a completed replay certification artifact" in trace["root_cause_explanation"]


def test_human_interface_neutrality(tmp_path: Path) -> None:
    turn_root = _turn_replay(tmp_path)

    trace = trace_platform_core_root_cause(
        observed_field="replay_certification_reached",
        observed_value=False,
        replay_reference=turn_root,
        created_at=CREATED_AT,
    )

    assert trace["platform_core_authority"] is True
    assert trace["human_interface_authority"] is False
    assert trace["human_interface_owns_replay_traversal"] is False
    assert trace["provider_invoked"] is False
    assert trace["worker_invoked"] is False
    assert trace["governance_modified"] is False
    assert trace["replay_modified"] is False
    assert trace["improvement_intent_created"] is False
    assert is_platform_capability_certified("DETERMINISTIC_ROOT_CAUSE_TRACE_BINDING") is True


def _turn_replay(tmp_path: Path) -> Path:
    turn_root = tmp_path / "AICLI-REFERENCE-SESSION" / "TURN-000024"
    _write_wrapper(
        turn_root / "multiline_prompt_capture" / "000_multiline_prompt_captured.json",
        0,
        "multiline_prompt_captured",
        {
            "artifact_type": "MULTILINE_PROMPT_CAPTURED_ARTIFACT_V1",
            "prompt_id": "AICLI-REFERENCE-SESSION:TURN-000024",
            "assembled_prompt_hash": replay_hash("Implement root-cause trace."),
            "session_id": "AICLI-REFERENCE-SESSION",
            "turn_id": "TURN-000024",
            "replay_visible": True,
        },
    )
    _write_wrapper(
        turn_root / "source_router" / "000_source_of_truth_router_selected.json",
        0,
        "source_of_truth_router_selected",
        {
            "artifact_type": "SOURCE_OF_TRUTH_ROUTER_SELECTION_ARTIFACT_V1",
            "routing_status": "SELECTED",
            "router_id": "AICLI-REFERENCE-SESSION:TURN-000024:SOURCE_ROUTER",
            "selected_source": "SELF_RESOLUTION",
            "authority": False,
            "replay_visible": True,
        },
    )
    _write_wrapper(
        turn_root
        / "governed_bridge_certified_development_continuation"
        / "execution_authorization"
        / "003_authorization_result_recorded.json",
        3,
        "authorization_result_recorded",
        {
            "artifact_type": "EXECUTION_AUTHORIZATION_RESULT_ARTIFACT_V1",
            "authorization_status": "EXECUTION_AUTHORIZED",
            "authorization_decision_reference": "AICLI-REFERENCE-SESSION:TURN-000024:AUTHORIZATION",
            "governance_mutated": False,
            "replay_visible": True,
        },
    )
    _write_wrapper(
        turn_root
        / "governed_bridge_certified_development_continuation"
        / "worker_lifecycle_continuation"
        / "worker_invocation"
        / "003_invocation_result_recorded.json",
        3,
        "invocation_result_recorded",
        {
            "artifact_type": "WORKER_INVOCATION_RESULT_ARTIFACT_V1",
            "runtime_version": "AIGOL_WORKER_INVOCATION_RUNTIME_V1",
            "invocation_status": "WORKER_INVOKED",
            "worker_invoked": True,
            "failure_reason": None,
            "replay_visible": True,
        },
    )
    _write_wrapper(
        turn_root
        / "governed_bridge_certified_development_continuation"
        / "worker_lifecycle_continuation"
        / "universal_provider_worker"
        / "001_universal_provider_worker_result_recorded.json",
        1,
        "universal_provider_worker_result_recorded",
        {
            "artifact_type": "UNIVERSAL_PROVIDER_WORKER_RESULT_ARTIFACT_V1",
            "runtime_version": "G18_03_UNIVERSAL_PROVIDER_WORKER_RUNTIME_V1",
            "universal_provider_worker_status": "FAILED_CLOSED",
            "provider_worker_status": "FAILED_CLOSED",
            "provider_invocation_delegated": True,
            "certified_provider_attachment_reused": True,
            "replay_lineage_preserved": False,
            "failure_reason": "OpenAI provider unavailable",
            "replay_visible": True,
        },
    )
    _write_wrapper(
        turn_root / "turn_completion" / "000_turn_completed.json",
        0,
        "turn_completed",
        {
            "artifact_type": "TURN_COMPLETED_ARTIFACT_V1",
            "status": "FAILED_CLOSED",
            "result_delivered": False,
            "replay_visible": True,
        },
    )
    return turn_root


def _write_wrapper(path: Path, index: int, step: str, artifact: dict) -> None:
    payload = deepcopy(artifact)
    payload["artifact_hash"] = replay_hash(payload)
    wrapper = {
        "event_type": step.upper(),
        "replay_index": index,
        "replay_step": step,
        "artifact": payload,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(path, wrapper)
