"""Platform Core deterministic root-cause trace binding.

The binding composes existing replay, observation, runtime projection, and
governance evidence. It does not mutate replay, invoke providers, execute
workers, or create improvement proposals.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.replay_observation_layer import replay_observation_artifact
from aigol.runtime.transport.serialization import load_json, replay_hash


PLATFORM_CORE_ROOT_CAUSE_TRACE_VERSION = "G18_09_PLATFORM_CORE_ROOT_CAUSE_TRACE_BINDING_V1"
ROOT_CAUSE_TRACE_READY = "ROOT_CAUSE_TRACE_READY"
ROOT_CAUSE_TRACE_FAILED_CLOSED = "ROOT_CAUSE_TRACE_FAILED_CLOSED"
UNKNOWN = "UNKNOWN"

REPLAY_CERTIFICATION_RELATIVE_PATH = (
    "governed_bridge_certified_development_continuation",
    "worker_lifecycle_continuation",
    "replay_certification",
    "000_replay_certification_artifact_recorded.json",
)

CAUSAL_PREDECESSOR_RELATIVE_PATHS = (
    (
        "governed_bridge_certified_development_continuation",
        "worker_lifecycle_continuation",
        "universal_provider_worker",
        "001_universal_provider_worker_result_recorded.json",
    ),
    (
        "governed_bridge_certified_development_continuation",
        "worker_lifecycle_continuation",
        "universal_provider_worker",
        "selected_provider_openai",
        "002_openai_external_worker_result_recorded.json",
    ),
    (
        "governed_bridge_certified_development_continuation",
        "worker_lifecycle_continuation",
        "worker_invocation",
        "003_invocation_result_recorded.json",
    ),
    ("turn_completion", "000_turn_completed.json"),
)

GOVERNANCE_RELATIVE_PATHS = (
    (
        "governed_bridge_certified_development_continuation",
        "execution_authorization",
        "003_authorization_result_recorded.json",
    ),
    ("source_router", "000_source_of_truth_router_selected.json"),
)

REQUEST_RELATIVE_PATHS = (
    ("multiline_prompt_capture", "000_multiline_prompt_captured.json"),
    ("universal_intake", "000_universal_intake_recorded.json"),
    ("source_router", "000_source_of_truth_router_selected.json"),
)


def trace_platform_core_root_cause(
    *,
    observed_field: str | None = None,
    observed_value: Any = None,
    failure_reason: str | None = None,
    artifact_reference: str | Path | None = None,
    replay_reference: str | Path | None = None,
    runtime_result: dict[str, Any] | None = None,
    user_visible_result: dict[str, Any] | None = None,
    created_at: str = "2026-07-11T00:00:00Z",
) -> dict[str, Any]:
    """Trace an observed result backward to replay-backed causal evidence."""

    try:
        observation = _observed_result(
            observed_field=observed_field,
            observed_value=observed_value,
            failure_reason=failure_reason,
            artifact_reference=artifact_reference,
            replay_reference=replay_reference,
            runtime_result=runtime_result,
            user_visible_result=user_visible_result,
        )
        replay_root = _resolve_replay_root(
            replay_reference=replay_reference,
            artifact_reference=artifact_reference,
            runtime_result=runtime_result,
            user_visible_result=user_visible_result,
        )
        if replay_root is None:
            raise FailClosedRuntimeError("root-cause trace failed closed: replay reference could not be resolved")
        artifact_paths = _json_artifact_paths(replay_root)
        if not artifact_paths:
            raise FailClosedRuntimeError("root-cause trace failed closed: replay contains no JSON artifacts")
        wrappers = [_safe_load_wrapper(path) for path in artifact_paths]
        projection_evidence = _runtime_projection_evidence(runtime_result, user_visible_result)
        primary = _primary_evidence(
            observation=observation,
            replay_root=replay_root,
            wrappers=wrappers,
            artifact_reference=artifact_reference,
            projection_evidence=projection_evidence,
            created_at=created_at,
        )
        governance = _governance_decision(replay_root)
        request = _originating_request(replay_root)
        missing = _missing_evidence(
            observation=observation,
            replay_root=replay_root,
            projection_evidence=projection_evidence,
        )
        contradictions = _contradictory_evidence(observation=observation, wrappers=wrappers)
        result = {
            "artifact_type": "PLATFORM_CORE_ROOT_CAUSE_TRACE_ARTIFACT_V1",
            "runtime_version": PLATFORM_CORE_ROOT_CAUSE_TRACE_VERSION,
            "trace_status": ROOT_CAUSE_TRACE_READY,
            "created_at": _require_string(created_at, "created_at"),
            "observed_result": observation,
            "replay_reference": str(replay_root),
            "producing_component": primary["producing_component"],
            "source_artifact": primary["source_artifact"],
            "source_projection": primary["source_projection"],
            "runtime_stage": primary["runtime_stage"],
            "governance_decision": governance,
            "originating_request": request,
            "causal_predecessors": _causal_predecessors(replay_root, created_at=created_at),
            "replay_sources_inspected": [str(path) for path in artifact_paths],
            "replay_source_count": len(artifact_paths),
            "missing_evidence": missing,
            "contradictory_evidence": contradictions,
            "root_cause_explanation": _explanation(
                observation=observation,
                primary=primary,
                missing=missing,
                contradictions=contradictions,
            ),
            "deterministic": True,
            "replay_backed": True,
            "platform_core_authority": True,
            "human_interface_authority": False,
            "human_interface_owns_replay_traversal": False,
            "provider_invoked": False,
            "worker_invoked": False,
            "governance_modified": False,
            "replay_modified": False,
            "improvement_intent_created": False,
            "fail_closed": False,
        }
        result["trace_hash"] = replay_hash(result)
        return result
    except Exception as exc:
        result = _failed_trace(
            observed_field=observed_field,
            observed_value=observed_value,
            failure_reason=failure_reason,
            artifact_reference=artifact_reference,
            replay_reference=replay_reference,
            runtime_result=runtime_result,
            created_at=created_at,
            failure=_failure_reason(exc),
        )
        result["trace_hash"] = replay_hash(result)
        return result


def _observed_result(
    *,
    observed_field: str | None,
    observed_value: Any,
    failure_reason: str | None,
    artifact_reference: str | Path | None,
    replay_reference: str | Path | None,
    runtime_result: dict[str, Any] | None,
    user_visible_result: dict[str, Any] | None,
) -> dict[str, Any]:
    field = observed_field if isinstance(observed_field, str) and observed_field.strip() else ""
    value = observed_value
    if field and value is None:
        for source in (runtime_result, user_visible_result):
            if isinstance(source, dict) and field in source:
                value = deepcopy(source[field])
                break
    if not field and isinstance(failure_reason, str) and failure_reason.strip():
        field = "failure_reason"
        value = failure_reason.strip()
    if not field and artifact_reference is not None:
        field = "artifact_reference"
        value = str(artifact_reference)
    if not field and replay_reference is not None:
        field = "replay_reference"
        value = str(replay_reference)
    if not field:
        raise FailClosedRuntimeError("root-cause trace failed closed: observed result is required")
    return {
        "field": field,
        "value": deepcopy(value),
        "failure_reason": failure_reason if isinstance(failure_reason, str) and failure_reason.strip() else None,
        "input_sources": {
            "runtime_result_supplied": isinstance(runtime_result, dict),
            "user_visible_result_supplied": isinstance(user_visible_result, dict),
            "artifact_reference_supplied": artifact_reference is not None,
            "replay_reference_supplied": replay_reference is not None,
        },
    }


def _resolve_replay_root(
    *,
    replay_reference: str | Path | None,
    artifact_reference: str | Path | None,
    runtime_result: dict[str, Any] | None,
    user_visible_result: dict[str, Any] | None,
) -> Path | None:
    candidates: list[Path] = []
    for value in (replay_reference, artifact_reference):
        if isinstance(value, str | Path) and str(value).strip():
            candidates.append(Path(value))
    for source in (runtime_result, user_visible_result):
        if not isinstance(source, dict):
            continue
        for key in (
            "runtime_replay_reference",
            "replay_reference",
            "conversation_replay_reference",
            "project_workspace_replay_reference",
        ):
            value = source.get(key)
            if isinstance(value, str) and value.strip():
                candidates.append(Path(value))
        evidence = source.get("runtime_status_projection_evidence")
        if isinstance(evidence, dict):
            for key in ("turn_replay_root", "worker_lifecycle_replay_root"):
                value = evidence.get(key)
                if isinstance(value, str) and value.strip():
                    candidates.append(Path(value))
    for candidate in candidates:
        root = _nearest_replay_root(candidate)
        if root is not None:
            return root
    return None


def _nearest_replay_root(path: Path) -> Path | None:
    current = path if path.suffix == "" else path.parent
    for candidate in (current, *current.parents):
        if candidate.name.startswith("TURN-"):
            return candidate
        if _looks_like_turn_root(candidate):
            return candidate
    if current.exists() and current.is_dir():
        return current
    return None


def _looks_like_turn_root(path: Path) -> bool:
    return (
        path.exists()
        and path.is_dir()
        and (
            (path / "turn_completion").exists()
            or (path / "source_router").exists()
            or (path / "governed_bridge_certified_development_continuation").exists()
        )
    )


def _json_artifact_paths(replay_root: Path) -> list[Path]:
    if replay_root.is_file():
        return [replay_root]
    if not replay_root.exists() or not replay_root.is_dir():
        return []
    return sorted(path for path in replay_root.rglob("*.json") if path.is_file())


def _safe_load_wrapper(path: Path) -> dict[str, Any]:
    try:
        wrapper = load_json(path)
    except Exception as exc:
        return {"_path": str(path), "_load_error": _failure_reason(exc)}
    wrapper["_path"] = str(path)
    wrapper["_wrapper_hash_valid"] = _wrapper_hash_valid(wrapper)
    artifact = wrapper.get("artifact")
    if isinstance(artifact, dict):
        wrapper["_artifact_hash_valid"] = _artifact_hash_valid(artifact)
    else:
        wrapper["_artifact_hash_valid"] = None
    return wrapper


def _runtime_projection_evidence(*sources: dict[str, Any] | None) -> dict[str, Any]:
    for source in sources:
        if isinstance(source, dict) and isinstance(source.get("runtime_status_projection_evidence"), dict):
            return deepcopy(source["runtime_status_projection_evidence"])
    return {}


def _primary_evidence(
    *,
    observation: dict[str, Any],
    replay_root: Path,
    wrappers: list[dict[str, Any]],
    artifact_reference: str | Path | None,
    projection_evidence: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    if observation["field"] == "replay_certification_reached" and observation.get("value") is False:
        return _replay_certification_not_reached_evidence(
            replay_root=replay_root,
            projection_evidence=projection_evidence,
            created_at=created_at,
        )
    if artifact_reference is not None:
        wrapper = _safe_load_wrapper(Path(artifact_reference))
        return _evidence_from_wrapper(
            wrapper,
            created_at=created_at,
            source_projection={},
            producing_component="ARTIFACT_REFERENCE_RESOLUTION",
        )
    match = _find_matching_wrapper(observation=observation, wrappers=wrappers)
    if match is not None:
        return _evidence_from_wrapper(
            match,
            created_at=created_at,
            source_projection={},
            producing_component=_component_from_wrapper(match),
        )
    return {
        "producing_component": "PLATFORM_CORE_ROOT_CAUSE_TRACE_RESOLVER",
        "source_artifact": {},
        "source_projection": {
            "projection_status": "NO_DIRECT_ARTIFACT_MATCH",
            "projection_evidence": deepcopy(projection_evidence),
        },
        "runtime_stage": {
            "stage": "UNRESOLVED",
            "originating_component": UNKNOWN,
            "observation_category": UNKNOWN,
            "source_replay_step": None,
            "source_replay_index": None,
        },
    }


def _replay_certification_not_reached_evidence(
    *,
    replay_root: Path,
    projection_evidence: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    certification_path = replay_root.joinpath(*REPLAY_CERTIFICATION_RELATIVE_PATH)
    attempted_paths = sorted(replay_root.rglob("*replay_certification*.json")) if replay_root.exists() else []
    predecessor = _first_existing_wrapper(replay_root, CAUSAL_PREDECESSOR_RELATIVE_PATHS)
    source_artifact = _artifact_summary(predecessor) if predecessor else {}
    source_projection = {
        "projection_component": "HUMAN_INTERFACE_RUNTIME_STATUS_PROJECTION",
        "projection_field": "replay_certification_reached",
        "projection_value": False,
        "replay_certification_expected_artifact": str(certification_path),
        "replay_certification_artifact_exists": certification_path.exists(),
        "replay_certification_attempted": bool(attempted_paths),
        "replay_certification_status": (
            "REPLAY_CERTIFICATION_ARTIFACT_PRESENT"
            if certification_path.exists()
            else "REPLAY_CERTIFICATION_NOT_REACHED"
        ),
        "runtime_status_projection_evidence": deepcopy(projection_evidence),
    }
    if predecessor:
        stage = _runtime_stage_from_wrapper(predecessor, created_at=created_at)
    else:
        stage = {
            "stage": "REPLAY_CERTIFICATION",
            "originating_component": "REPLAY_CERTIFICATION_RUNTIME",
            "observation_category": "CERTIFICATION",
            "source_replay_step": None,
            "source_replay_index": None,
        }
    return {
        "producing_component": "HUMAN_INTERFACE_RUNTIME_STATUS_PROJECTION",
        "source_artifact": source_artifact,
        "source_projection": source_projection,
        "runtime_stage": stage,
    }


def _find_matching_wrapper(
    *,
    observation: dict[str, Any],
    wrappers: list[dict[str, Any]],
) -> dict[str, Any] | None:
    field = observation["field"]
    value = observation.get("value")
    for wrapper in wrappers:
        artifact = wrapper.get("artifact")
        if isinstance(artifact, dict) and artifact.get(field) == value:
            return wrapper
    failure = observation.get("failure_reason")
    if isinstance(failure, str) and failure.strip():
        for wrapper in wrappers:
            artifact = wrapper.get("artifact")
            if isinstance(artifact, dict) and artifact.get("failure_reason") == failure:
                return wrapper
    return None


def _evidence_from_wrapper(
    wrapper: dict[str, Any],
    *,
    created_at: str,
    source_projection: dict[str, Any],
    producing_component: str,
) -> dict[str, Any]:
    return {
        "producing_component": producing_component,
        "source_artifact": _artifact_summary(wrapper),
        "source_projection": deepcopy(source_projection),
        "runtime_stage": _runtime_stage_from_wrapper(wrapper, created_at=created_at),
    }


def _artifact_summary(wrapper: dict[str, Any]) -> dict[str, Any]:
    artifact = wrapper.get("artifact")
    artifact = artifact if isinstance(artifact, dict) else {}
    return {
        "path": wrapper.get("_path"),
        "event_type": wrapper.get("event_type") or artifact.get("event_type"),
        "replay_index": wrapper.get("replay_index"),
        "replay_step": wrapper.get("replay_step"),
        "replay_hash": wrapper.get("replay_hash"),
        "replay_hash_valid": wrapper.get("_wrapper_hash_valid"),
        "artifact_type": artifact.get("artifact_type"),
        "artifact_hash": artifact.get("artifact_hash"),
        "artifact_hash_valid": wrapper.get("_artifact_hash_valid"),
        "runtime_version": artifact.get("runtime_version"),
        "status": _first_present(
            artifact,
            (
                "status",
                "certification_status",
                "execution_status",
                "universal_provider_worker_status",
                "provider_worker_status",
                "invocation_status",
                "authorization_status",
                "selection_status",
            ),
        ),
        "failure_reason": artifact.get("failure_reason"),
    }


def _runtime_stage_from_wrapper(wrapper: dict[str, Any], *, created_at: str) -> dict[str, Any]:
    try:
        observation = replay_observation_artifact(
            replay_identifier="PLATFORM-CORE-ROOT-CAUSE-TRACE",
            source_replay_artifact={key: value for key, value in wrapper.items() if not key.startswith("_")},
            observed_at=created_at,
            sequence=0,
        )
        return {
            "stage": observation.get("execution_stage"),
            "originating_component": observation.get("originating_component"),
            "observation_category": observation.get("observation_category"),
            "severity": observation.get("severity"),
            "deterministic_message": observation.get("deterministic_message"),
            "source_replay_step": observation.get("source_replay_step"),
            "source_replay_index": observation.get("source_replay_index"),
            "source_artifact_hash": observation.get("source_artifact_hash"),
            "source_replay_hash": observation.get("source_replay_hash"),
        }
    except Exception:
        artifact = wrapper.get("artifact")
        artifact = artifact if isinstance(artifact, dict) else {}
        return {
            "stage": _stage_from_path_or_artifact(wrapper.get("_path"), artifact),
            "originating_component": _component_from_wrapper(wrapper),
            "observation_category": _category_from_artifact(artifact),
            "source_replay_step": wrapper.get("replay_step"),
            "source_replay_index": wrapper.get("replay_index"),
        }


def _component_from_wrapper(wrapper: dict[str, Any]) -> str:
    artifact = wrapper.get("artifact")
    artifact = artifact if isinstance(artifact, dict) else {}
    path = str(wrapper.get("_path") or "").lower()
    artifact_type = str(artifact.get("artifact_type") or "").upper()
    runtime_version = str(artifact.get("runtime_version") or "").upper()
    if "replay_certification" in path or "CERTIFICATION" in artifact_type:
        return "REPLAY_CERTIFICATION_RUNTIME"
    if "universal_provider_worker" in path or "UNIVERSAL_PROVIDER_WORKER" in artifact_type:
        return "UNIVERSAL_PROVIDER_WORKER_RUNTIME"
    if "selected_provider" in path or "PROVIDER" in artifact_type or "PROVIDER" in runtime_version:
        return "PROVIDER_PLATFORM"
    if "worker_" in path or "WORKER" in artifact_type or "WORKER" in runtime_version:
        return "WORKER_PLATFORM"
    if "execution_authorization" in path or "AUTHORIZATION" in artifact_type:
        return "GOVERNANCE_AUTHORIZATION"
    if "source_router" in path:
        return "SOURCE_OF_TRUTH_ROUTER"
    if "multiline_prompt_capture" in path or "PROMPT" in artifact_type:
        return "ORIGINATING_REQUEST_CAPTURE"
    return UNKNOWN


def _stage_from_path_or_artifact(path_value: Any, artifact: dict[str, Any]) -> str:
    path = str(path_value or "").lower()
    artifact_type = str(artifact.get("artifact_type") or "").upper()
    if "replay_certification" in path or "CERTIFICATION" in artifact_type:
        return "REPLAY_CERTIFICATION"
    if "universal_resource_selection" in path:
        return "UNIVERSAL_RESOURCE_SELECTION"
    if "universal_provider_worker" in path:
        return "UNIVERSAL_PROVIDER_WORKER"
    if "selected_provider" in path:
        return "SELECTED_PROVIDER"
    if "worker_invocation" in path:
        return "WORKER_INVOCATION"
    if "execution_authorization" in path:
        return "GOVERNANCE_AUTHORIZATION"
    if "source_router" in path:
        return "SOURCE_ROUTING"
    if "multiline_prompt_capture" in path:
        return "ORIGINATING_REQUEST_CAPTURE"
    return UNKNOWN


def _category_from_artifact(artifact: dict[str, Any]) -> str:
    artifact_type = str(artifact.get("artifact_type") or "").upper()
    if "CERTIFICATION" in artifact_type:
        return "CERTIFICATION"
    if "PROVIDER" in artifact_type:
        return "PROVIDER"
    if "WORKER" in artifact_type:
        return "WORKER"
    if "AUTHORIZATION" in artifact_type or "GOVERNANCE" in artifact_type:
        return "GOVERNANCE"
    return "FAILURE" if artifact.get("failure_reason") else UNKNOWN


def _governance_decision(replay_root: Path) -> dict[str, Any]:
    wrappers = _existing_wrappers(replay_root, GOVERNANCE_RELATIVE_PATHS)
    if not wrappers:
        return {"decision_found": False, "missing_reason": "No governance decision artifact found."}
    primary = wrappers[0]
    artifact = primary.get("artifact")
    artifact = artifact if isinstance(artifact, dict) else {}
    return {
        "decision_found": True,
        "path": primary.get("_path"),
        "artifact_type": artifact.get("artifact_type"),
        "artifact_hash": artifact.get("artifact_hash"),
        "status": _first_present(
            artifact,
            ("authorization_status", "routing_status", "selection_status", "current_lifecycle_state"),
        ),
        "decision_reference": _first_present(
            artifact,
            (
                "authorization_decision_reference",
                "routing_decision_reference",
                "router_id",
                "decision_id",
            ),
        ),
        "authority_preserved": artifact.get("governance_mutated") is False
        or artifact.get("authority") is False
        or artifact.get("execution_authority") is False,
    }


def _originating_request(replay_root: Path) -> dict[str, Any]:
    wrappers = _existing_wrappers(replay_root, REQUEST_RELATIVE_PATHS)
    if not wrappers:
        return {"request_found": False, "missing_reason": "No originating request artifact found."}
    primary = wrappers[0]
    artifact = primary.get("artifact")
    artifact = artifact if isinstance(artifact, dict) else {}
    return {
        "request_found": True,
        "path": primary.get("_path"),
        "artifact_type": artifact.get("artifact_type"),
        "artifact_hash": artifact.get("artifact_hash"),
        "prompt_id": artifact.get("prompt_id") or artifact.get("human_prompt_reference"),
        "human_prompt_hash": artifact.get("human_prompt_hash") or artifact.get("assembled_prompt_hash"),
        "session_id": artifact.get("session_id"),
        "turn_id": artifact.get("turn_id"),
    }


def _causal_predecessors(replay_root: Path, *, created_at: str) -> list[dict[str, Any]]:
    predecessors = []
    for wrapper in _existing_wrappers(replay_root, CAUSAL_PREDECESSOR_RELATIVE_PATHS):
        predecessors.append(
            {
                "source_artifact": _artifact_summary(wrapper),
                "runtime_stage": _runtime_stage_from_wrapper(wrapper, created_at=created_at),
            }
        )
    return predecessors


def _existing_wrappers(
    replay_root: Path,
    relative_paths: tuple[tuple[str, ...], ...],
) -> list[dict[str, Any]]:
    wrappers: list[dict[str, Any]] = []
    for relative in relative_paths:
        path = replay_root.joinpath(*relative)
        if path.exists() and path.is_file():
            wrappers.append(_safe_load_wrapper(path))
    return wrappers


def _first_existing_wrapper(
    replay_root: Path,
    relative_paths: tuple[tuple[str, ...], ...],
) -> dict[str, Any] | None:
    wrappers = _existing_wrappers(replay_root, relative_paths)
    return wrappers[0] if wrappers else None


def _missing_evidence(
    *,
    observation: dict[str, Any],
    replay_root: Path,
    projection_evidence: dict[str, Any],
) -> list[dict[str, Any]]:
    missing: list[dict[str, Any]] = []
    if observation["field"] == "replay_certification_reached" and observation.get("value") is False:
        certification_path = replay_root.joinpath(*REPLAY_CERTIFICATION_RELATIVE_PATH)
        if not certification_path.exists():
            missing.append(
                {
                    "evidence": "replay_certification_artifact",
                    "expected_path": str(certification_path),
                    "status": "MISSING",
                    "reason": "Replay certification artifact is absent from the current turn replay tree.",
                }
            )
        if not projection_evidence:
            missing.append(
                {
                    "evidence": "runtime_status_projection_evidence",
                    "expected_path": None,
                    "status": "NOT_SUPPLIED",
                    "reason": "Runtime projection evidence was not supplied with the trace input.",
                }
            )
    return missing


def _contradictory_evidence(
    *,
    observation: dict[str, Any],
    wrappers: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    contradictions: list[dict[str, Any]] = []
    if observation["field"] == "replay_certification_reached" and observation.get("value") is False:
        for wrapper in wrappers:
            artifact = wrapper.get("artifact")
            if not isinstance(artifact, dict):
                continue
            if artifact.get("certification_status") == "REPLAY_CERTIFICATION_COMPLETED":
                contradictions.append(
                    {
                        "path": wrapper.get("_path"),
                        "field": "certification_status",
                        "value": "REPLAY_CERTIFICATION_COMPLETED",
                        "reason": "Completed replay certification contradicts observed false projection.",
                    }
                )
    return contradictions


def _explanation(
    *,
    observation: dict[str, Any],
    primary: dict[str, Any],
    missing: list[dict[str, Any]],
    contradictions: list[dict[str, Any]],
) -> str:
    if observation["field"] == "replay_certification_reached" and observation.get("value") is False:
        status = primary["source_projection"].get("replay_certification_status", "REPLAY_CERTIFICATION_NOT_REACHED")
        source = primary["source_artifact"]
        reason = source.get("failure_reason") or "no completed replay certification artifact was found"
        return (
            "replay_certification_reached is false because Platform Core trace did not find a completed "
            f"replay certification artifact for the current turn. Certification status is {status}. "
            f"The nearest causal predecessor is {source.get('artifact_type', UNKNOWN)} with status "
            f"{source.get('status', UNKNOWN)} and reason: {reason}."
        )
    source = primary["source_artifact"]
    if source:
        return (
            f"{observation['field']} was traced to {source.get('artifact_type', UNKNOWN)} at "
            f"{source.get('path', UNKNOWN)} with status {source.get('status', UNKNOWN)}."
        )
    if missing:
        return f"{observation['field']} could not be fully traced because required evidence is missing."
    if contradictions:
        return f"{observation['field']} has contradictory replay evidence and must be treated fail-closed."
    return f"{observation['field']} was resolved by Platform Core root-cause trace without a direct artifact match."


def _failed_trace(
    *,
    observed_field: str | None,
    observed_value: Any,
    failure_reason: str | None,
    artifact_reference: str | Path | None,
    replay_reference: str | Path | None,
    runtime_result: dict[str, Any] | None,
    created_at: str,
    failure: str,
) -> dict[str, Any]:
    return {
        "artifact_type": "PLATFORM_CORE_ROOT_CAUSE_TRACE_ARTIFACT_V1",
        "runtime_version": PLATFORM_CORE_ROOT_CAUSE_TRACE_VERSION,
        "trace_status": ROOT_CAUSE_TRACE_FAILED_CLOSED,
        "created_at": created_at,
        "observed_result": {
            "field": observed_field,
            "value": deepcopy(observed_value),
            "failure_reason": failure_reason,
        },
        "replay_reference": str(replay_reference) if replay_reference is not None else None,
        "artifact_reference": str(artifact_reference) if artifact_reference is not None else None,
        "runtime_result_supplied": isinstance(runtime_result, dict),
        "root_cause_explanation": "Root-cause trace failed closed because required replay evidence could not be resolved.",
        "missing_evidence": [{"evidence": "trace_input_or_replay", "status": "MISSING", "reason": failure}],
        "contradictory_evidence": [],
        "deterministic": True,
        "replay_backed": False,
        "platform_core_authority": True,
        "human_interface_authority": False,
        "human_interface_owns_replay_traversal": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
        "improvement_intent_created": False,
        "fail_closed": True,
        "failure_reason": failure,
    }


def _wrapper_hash_valid(wrapper: dict[str, Any]) -> bool | None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        return None
    expected = deepcopy(wrapper)
    expected.pop("replay_hash", None)
    expected.pop("_path", None)
    expected.pop("_wrapper_hash_valid", None)
    expected.pop("_artifact_hash_valid", None)
    return actual == replay_hash(expected)


def _artifact_hash_valid(artifact: dict[str, Any]) -> bool | None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        return None
    expected = deepcopy(artifact)
    expected.pop("artifact_hash", None)
    return actual == replay_hash(expected)


def _first_present(artifact: dict[str, Any], fields: tuple[str, ...]) -> Any:
    for field in fields:
        value = artifact.get(field)
        if value is not None:
            return value
    return None


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"root-cause trace requires {field_name}")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    return str(exc) if isinstance(exc, FailClosedRuntimeError) else "root-cause trace failed closed"


__all__ = [
    "PLATFORM_CORE_ROOT_CAUSE_TRACE_VERSION",
    "ROOT_CAUSE_TRACE_FAILED_CLOSED",
    "ROOT_CAUSE_TRACE_READY",
    "trace_platform_core_root_cause",
]
