"""Live ACLI integration for passive hardening evidence capture."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.acli_hardening_runtime import (
    ACLI_HARDENING_RUNTIME_VERSION,
    record_acli_hardening_interaction,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


ACLI_HARDENING_INTEGRATION_RUNTIME_VERSION = "ACLI_HARDENING_INTEGRATION_RUNTIME_V1"
ACLI_HARDENING_METRICS_ARTIFACT_V1 = "ACLI_HARDENING_METRICS_ARTIFACT_V1"
ACLI_HARDENING_INTEGRATION_EVENT_V1 = "ACLI_HARDENING_INTEGRATION_EVENT_V1"

METRICS_DIRNAME = "acli_hardening_metrics"
METRICS_FILENAME = "latest_metrics.json"
SUMMARY_HEADING = "Hardening"

AUTHORITY_FLAGS = {
    "authorizes_execution": False,
    "authorizes_dispatch": False,
    "authorizes_worker_invocation": False,
    "authorizes_provider_invocation": False,
    "authorizes_governance_mutation": False,
    "authorizes_replay_mutation": False,
    "authorizes_lifecycle_modification": False,
    "creates_approval": False,
    "creates_improvement_proposal": False,
}


def record_completed_acli_interaction_hardening(
    *,
    session_id: str,
    turn_id: str,
    prompt_id: str,
    turn_summary: dict[str, Any],
    completion_capture: dict[str, Any],
    session_root: str | Path,
    turn_root: str | Path,
    created_at: str,
) -> dict[str, Any]:
    """Capture hardening evidence after a successful ACLI turn completion."""

    session_path = Path(session_root)
    turn_path = Path(turn_root)
    hardening_id = f"{prompt_id}:ACLI-HARDENING"
    interaction_id = f"{session_id}:{turn_id}:ACLI-INTERACTION"
    completed_interaction = _completed_interaction_payload(
        session_id=session_id,
        turn_id=turn_id,
        prompt_id=prompt_id,
        turn_summary=turn_summary,
        completion_capture=completion_capture,
        created_at=created_at,
    )
    prior_state = load_acli_hardening_metrics_state(session_path)
    capture = record_acli_hardening_interaction(
        hardening_id=hardening_id,
        interaction_id=interaction_id,
        completed_interaction=completed_interaction,
        prior_hardening_state=prior_state,
        replay_dir=turn_path / "acli_hardening",
        created_at=created_at,
    )
    metrics = persist_acli_hardening_metrics_state(
        session_root=session_path,
        hardening_capture=capture,
        created_at=created_at,
    )
    integration_event = _integration_event(
        session_id=session_id,
        turn_id=turn_id,
        prompt_id=prompt_id,
        hardening_capture=capture,
        metrics=metrics,
        created_at=created_at,
    )
    _persist_integration_event(turn_path / "acli_hardening_integration", integration_event)
    result = {
        "runtime_version": ACLI_HARDENING_INTEGRATION_RUNTIME_VERSION,
        "integration_status": "HARDENING_CAPTURE_RECORDED",
        "hardening_capture": deepcopy(capture),
        "hardening_metrics": deepcopy(metrics),
        "hardening_replay_reference": capture["hardening_replay_reference"],
        "hardening_metrics_reference": str(_metrics_path(session_path)),
        "operator_summary": render_acli_hardening_operator_summary(capture),
        "read_only": True,
        "replay_visible": True,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "workflow_modified": False,
        "approval_created": False,
        "execution_authorized": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "improvement_proposal_created": False,
    }
    result["integration_capture_hash"] = replay_hash(result)
    return result


def load_acli_hardening_metrics_state(session_root: str | Path) -> dict[str, Any] | None:
    """Load persisted hardening metrics for a session, if present."""

    path = _metrics_path(Path(session_root))
    if not path.exists():
        return None
    artifact = load_json(path)
    _verify_artifact_hash(artifact)
    if artifact.get("artifact_type") != ACLI_HARDENING_METRICS_ARTIFACT_V1:
        raise FailClosedRuntimeError("ACLI hardening metrics artifact type mismatch")
    _verify_authority_flags(artifact)
    return {
        "hardening_statistics": deepcopy(artifact["hardening_statistics"]),
        "scenario_coverage": deepcopy(artifact["scenario_coverage"]),
        "discovered_issues": deepcopy(artifact["discovered_issues"]),
        "unresolved_issues": deepcopy(artifact["unresolved_issues"]),
        "regression_history": deepcopy(artifact["regression_history"]),
    }


def persist_acli_hardening_metrics_state(
    *,
    session_root: str | Path,
    hardening_capture: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    """Persist continuously updated hardening metrics for an ACLI session."""

    session_path = Path(session_root)
    artifact = {
        "artifact_type": ACLI_HARDENING_METRICS_ARTIFACT_V1,
        "runtime_version": ACLI_HARDENING_INTEGRATION_RUNTIME_VERSION,
        "source_hardening_runtime_version": ACLI_HARDENING_RUNTIME_VERSION,
        "session_root": str(session_path),
        "latest_hardening_id": hardening_capture["hardening_id"],
        "latest_interaction_id": hardening_capture["interaction_id"],
        "latest_hardening_replay_reference": hardening_capture["hardening_replay_reference"],
        "latest_result": hardening_capture["result"],
        "hardening_statistics": deepcopy(hardening_capture["hardening_statistics"]),
        "scenario_coverage": deepcopy(hardening_capture["scenario_coverage"]),
        "discovered_issues": deepcopy(hardening_capture["discovered_issues"]),
        "unresolved_issues": deepcopy(hardening_capture["unresolved_issues"]),
        "regression_history": deepcopy(hardening_capture["regression_history"]),
        "dashboards": deepcopy(hardening_capture["dashboards"]),
        "production_readiness": deepcopy(hardening_capture["production_readiness"]),
        "future_compatibility": {
            "platform_quality_runtime_v1_ready_input": True,
            "platform_improvement_runtime_v1_ready_input": True,
            "quality_decision_made": False,
            "improvement_proposal_created": False,
        },
        "updated_at": _require_string(created_at, "created_at"),
        "read_only": True,
        "replay_visible": True,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "approval_created": False,
        "execution_authorized": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "deterministic_rules_modified": False,
        "improvement_proposal_created": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    path = _metrics_path(session_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_canonical_line(artifact), encoding="utf-8")
    snapshot_path = path.parent / f"{hardening_capture['interaction_id'].replace(':', '_')}_metrics_snapshot.json"
    if not snapshot_path.exists():
        write_json_immutable(snapshot_path, artifact)
    return deepcopy(artifact)


def render_acli_hardening_operator_summary(capture: dict[str, Any]) -> str:
    """Render a compact non-interrupting hardening summary."""

    scenarios = capture.get("hardening_scenarios") or []
    scenario = "Unknown"
    if scenarios:
        scenario = str(scenarios[0].get("name") or scenarios[0].get("scenario_id") or scenario)
    replay_recorded = "Recorded" if capture.get("source_replay_reference") else "Not recorded"
    new_scenario = any((capture.get("hardening_artifact") or {}).get("new_hardening_scenario") for _ in [0])
    coverage_delta = "+1 Scenario" if new_scenario else "Updated"
    return "\n".join(
        [
            "",
            SUMMARY_HEADING,
            "",
            f"Scenario: {scenario}",
            f"Coverage: {coverage_delta}",
            f"Replay: {replay_recorded}",
            "Operator feedback: Optional",
        ]
    )


def _completed_interaction_payload(
    *,
    session_id: str,
    turn_id: str,
    prompt_id: str,
    turn_summary: dict[str, Any],
    completion_capture: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    turn = _require_mapping(turn_summary, "turn_summary")
    completion = _require_mapping(completion_capture, "completion_capture")
    payload = deepcopy(turn)
    payload.update(
        {
            "session_id": _require_string(session_id, "session_id"),
            "turn_id": _require_string(turn_id, "turn_id"),
            "prompt_id": _require_string(prompt_id, "prompt_id"),
            "created_at": _require_string(created_at, "created_at"),
            "completion_status": completion.get("result_delivered_artifact", {}).get("status"),
            "turn_completed": True,
            "result_delivered": True,
            "turn_completion_replay_reference": completion.get("turn_completion_replay_reference"),
            "turn_completion_hash": completion.get("turn_completion_hash"),
            "completion_capture_hash": replay_hash(completion),
            "hardening_capture_reason": "COMPLETED_ACLI_INTERACTION",
            "platform_core_generation": "GENERATION_1",
        }
    )
    if payload.get("replay_reference") is None and payload.get("conversation_replay_reference"):
        payload["replay_reference"] = payload["conversation_replay_reference"]
    return payload


def _integration_event(
    *,
    session_id: str,
    turn_id: str,
    prompt_id: str,
    hardening_capture: dict[str, Any],
    metrics: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": ACLI_HARDENING_INTEGRATION_EVENT_V1,
        "runtime_version": ACLI_HARDENING_INTEGRATION_RUNTIME_VERSION,
        "session_id": session_id,
        "turn_id": turn_id,
        "prompt_id": prompt_id,
        "hardening_id": hardening_capture["hardening_id"],
        "hardening_replay_reference": hardening_capture["hardening_replay_reference"],
        "metrics_reference": metrics["session_root"],
        "result": hardening_capture["result"],
        "created_at": created_at,
        "read_only": True,
        "replay_visible": True,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "workflow_modified": False,
        "approval_created": False,
        "execution_authorized": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "improvement_proposal_created": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _persist_integration_event(replay_dir: Path, artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact)
    wrapper = {
        "replay_index": 0,
        "replay_step": "acli_hardening_integration_recorded",
        "event_type": ACLI_HARDENING_INTEGRATION_RUNTIME_VERSION,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / "000_acli_hardening_integration_recorded.json", wrapper)


def _metrics_path(session_root: Path) -> Path:
    return session_root / METRICS_DIRNAME / METRICS_FILENAME


def _canonical_line(artifact: dict[str, Any]) -> str:
    from aigol.runtime.transport.serialization import canonical_serialize

    return canonical_serialize(artifact) + "\n"


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str) or not actual:
        raise FailClosedRuntimeError("ACLI hardening integration artifact hash is required")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash", None)
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("ACLI hardening integration artifact hash mismatch")


def _verify_authority_flags(artifact: dict[str, Any]) -> None:
    if artifact.get("authority_flags") != AUTHORITY_FLAGS:
        raise FailClosedRuntimeError("ACLI hardening integration authority flags mismatch")
    for key in (
        "approval_created",
        "execution_authorized",
        "worker_invoked",
        "provider_invoked",
        "governance_mutated",
        "replay_mutated",
        "improvement_proposal_created",
    ):
        if artifact.get(key) is not False:
            raise FailClosedRuntimeError("ACLI hardening integration attempted authority")


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"{label} must be a JSON object")
    replay_hash(value)
    return deepcopy(value)


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{label} is required")
    return value.strip()


__all__ = [
    "ACLI_HARDENING_INTEGRATION_RUNTIME_VERSION",
    "ACLI_HARDENING_METRICS_ARTIFACT_V1",
    "record_completed_acli_interaction_hardening",
    "load_acli_hardening_metrics_state",
    "persist_acli_hardening_metrics_state",
    "render_acli_hardening_operator_summary",
]
