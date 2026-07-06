"""Deterministic Replay Observation Layer for Generation 15.

The layer interprets existing replay evidence and records normalized
observations. It does not mutate source replay, invoke providers, execute
workers, or create improvement proposals.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


REPLAY_OBSERVATION_LAYER_VERSION = "G15_01_REPLAY_OBSERVATION_LAYER_V1"
REPLAY_OBSERVATION_LAYER_ARTIFACT_V1 = "REPLAY_OBSERVATION_LAYER_ARTIFACT_V1"
REPLAY_OBSERVATION_ARTIFACT_V1 = "REPLAY_OBSERVATION_ARTIFACT_V1"
REPLAY_OBSERVATION_LAYER_RECORDED = "REPLAY_OBSERVATION_LAYER_RECORDED"

SUCCESS = "SUCCESS"
FAILURE = "FAILURE"
WARNING = "WARNING"
VALIDATION = "VALIDATION"
GOVERNANCE = "GOVERNANCE"
PROVIDER = "PROVIDER"
WORKER = "WORKER"
CERTIFICATION = "CERTIFICATION"

INFO = "INFO"
ERROR = "ERROR"

OBSERVATION_CATEGORIES = frozenset(
    {
        SUCCESS,
        FAILURE,
        WARNING,
        VALIDATION,
        GOVERNANCE,
        PROVIDER,
        WORKER,
        CERTIFICATION,
    }
)
OBSERVATION_SEVERITIES = frozenset({INFO, WARNING, ERROR})


def generate_replay_observation_layer(
    *,
    replay_identifier: str,
    source_replay_artifacts: list[dict[str, Any]],
    observed_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Generate and persist deterministic observations for replay evidence."""

    replay_path = Path(replay_dir)
    _ensure_observation_replay_available(replay_path)
    artifact = replay_observation_layer_artifact(
        replay_identifier=replay_identifier,
        source_replay_artifacts=source_replay_artifacts,
        observed_at=observed_at,
        replay_reference=str(replay_path),
    )
    wrapper = {
        "event_type": REPLAY_OBSERVATION_LAYER_RECORDED,
        "replay_index": 0,
        "replay_step": "replay_observation_layer_recorded",
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / "000_replay_observation_layer_recorded.json", wrapper)
    return _capture(artifact, replay_path)


def replay_observation_layer_artifact(
    *,
    replay_identifier: str,
    source_replay_artifacts: list[dict[str, Any]],
    observed_at: str,
    replay_reference: str,
) -> dict[str, Any]:
    """Build a replay observation layer artifact without filesystem writes."""

    replay_id = _require_string(replay_identifier, "replay_identifier")
    observed = _require_string(observed_at, "observed_at")
    if not isinstance(source_replay_artifacts, list) or not source_replay_artifacts:
        raise FailClosedRuntimeError("replay observation failed closed: source replay artifacts required")
    observations = [
        replay_observation_artifact(
            replay_identifier=replay_id,
            source_replay_artifact=artifact,
            observed_at=observed,
            sequence=index,
        )
        for index, artifact in enumerate(source_replay_artifacts)
    ]
    category_counts = _category_counts(observations)
    severity_counts = _severity_counts(observations)
    layer = {
        "artifact_type": REPLAY_OBSERVATION_LAYER_ARTIFACT_V1,
        "runtime_version": REPLAY_OBSERVATION_LAYER_VERSION,
        "replay_identifier": replay_id,
        "observed_at": observed,
        "observation_count": len(observations),
        "observations": observations,
        "category_counts": category_counts,
        "severity_counts": severity_counts,
        "source_replay_hashes": [_source_replay_hash(artifact) for artifact in source_replay_artifacts],
        "source_artifact_hashes": [_source_artifact_hash(artifact) for artifact in source_replay_artifacts],
        "observation_generation_authority": "PLATFORM_CORE",
        "read_only_interpretation": True,
        "source_replay_modified": False,
        "governance_modified": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "improvement_proposal_created": False,
        "autonomous_decision_created": False,
        "human_interface_authority": False,
        "provider_platform_modified": False,
        "replay_visible": True,
        "replay_reference": _require_string(replay_reference, "replay_reference"),
    }
    layer["artifact_hash"] = replay_hash(layer)
    return layer


def replay_observation_artifact(
    *,
    replay_identifier: str,
    source_replay_artifact: dict[str, Any],
    observed_at: str,
    sequence: int,
) -> dict[str, Any]:
    """Normalize one replay artifact into one deterministic observation."""

    if not isinstance(sequence, int) or sequence < 0:
        raise FailClosedRuntimeError("replay observation failed closed: sequence is invalid")
    source = _source_artifact(source_replay_artifact)
    category = _observation_category(source_replay_artifact, source)
    severity = _observation_severity(source_replay_artifact, source)
    observation = {
        "artifact_type": REPLAY_OBSERVATION_ARTIFACT_V1,
        "runtime_version": REPLAY_OBSERVATION_LAYER_VERSION,
        "observation_id": f"{_require_string(replay_identifier, 'replay_identifier')}:OBSERVATION-{sequence + 1:06d}",
        "replay_identifier": _require_string(replay_identifier, "replay_identifier"),
        "timestamp": _require_string(observed_at, "observed_at"),
        "execution_stage": _execution_stage(source_replay_artifact, source),
        "observation_category": category,
        "severity": severity,
        "originating_component": _originating_component(source_replay_artifact, source, category),
        "deterministic_message": _deterministic_message(category, severity, source),
        "related_artifact_identifiers": _related_artifact_identifiers(source),
        "source_replay_step": source_replay_artifact.get("replay_step")
        if isinstance(source_replay_artifact.get("replay_step"), str)
        else None,
        "source_replay_index": source_replay_artifact.get("replay_index")
        if isinstance(source_replay_artifact.get("replay_index"), int)
        else None,
        "source_event_type": _optional_string(source_replay_artifact.get("event_type") or source.get("event_type")),
        "source_artifact_type": _optional_string(source.get("artifact_type")),
        "source_artifact_hash": _source_artifact_hash(source_replay_artifact),
        "source_replay_hash": _source_replay_hash(source_replay_artifact),
        "read_only_interpretation": True,
        "source_replay_modified": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "improvement_proposal_created": False,
        "autonomous_decision_created": False,
    }
    _validate_observation(observation)
    observation["artifact_hash"] = replay_hash(observation)
    return observation


def observe_replay_directory(
    *,
    replay_identifier: str,
    source_replay_dir: str | Path,
    observed_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Read JSON replay wrappers from a directory and persist observations."""

    source_path = Path(source_replay_dir)
    if not source_path.exists() or not source_path.is_dir():
        raise FailClosedRuntimeError("replay observation failed closed: source replay directory missing")
    artifacts = [load_json(path) for path in sorted(source_path.glob("*.json"))]
    return generate_replay_observation_layer(
        replay_identifier=replay_identifier,
        source_replay_artifacts=artifacts,
        observed_at=observed_at,
        replay_dir=replay_dir,
    )


def reconstruct_replay_observation_layer(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate a persisted replay observation layer."""

    wrapper = load_json(Path(replay_dir) / "000_replay_observation_layer_recorded.json")
    _verify_wrapper_hash(wrapper)
    if wrapper.get("replay_index") != 0 or wrapper.get("replay_step") != "replay_observation_layer_recorded":
        raise FailClosedRuntimeError("replay observation failed closed: replay ordering mismatch")
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("replay observation failed closed: artifact must be object")
    _verify_artifact_hash(artifact)
    observations = artifact.get("observations")
    if not isinstance(observations, list) or not observations:
        raise FailClosedRuntimeError("replay observation failed closed: observations required")
    for observation in observations:
        if not isinstance(observation, dict):
            raise FailClosedRuntimeError("replay observation failed closed: observation must be object")
        _validate_observation(observation)
        _verify_artifact_hash(observation)
    return {
        "runtime_version": artifact["runtime_version"],
        "replay_identifier": artifact["replay_identifier"],
        "observation_count": artifact["observation_count"],
        "category_counts": deepcopy(artifact["category_counts"]),
        "severity_counts": deepcopy(artifact["severity_counts"]),
        "observation_generation_authority": artifact["observation_generation_authority"],
        "read_only_interpretation": artifact["read_only_interpretation"],
        "source_replay_modified": artifact["source_replay_modified"],
        "provider_invoked": artifact["provider_invoked"],
        "worker_invoked": artifact["worker_invoked"],
        "improvement_proposal_created": artifact["improvement_proposal_created"],
        "autonomous_decision_created": artifact["autonomous_decision_created"],
        "replay_visible": artifact["replay_visible"],
        "replay_hash": replay_hash(wrapper),
    }


def _capture(artifact: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "runtime_version": REPLAY_OBSERVATION_LAYER_VERSION,
        "replay_identifier": artifact["replay_identifier"],
        "observation_layer_status": REPLAY_OBSERVATION_LAYER_RECORDED,
        "replay_observation_layer_artifact": deepcopy(artifact),
        "replay_observation_layer_replay_reference": str(replay_path),
        "observation_count": artifact["observation_count"],
        "category_counts": deepcopy(artifact["category_counts"]),
        "severity_counts": deepcopy(artifact["severity_counts"]),
        "read_only_interpretation": True,
        "source_replay_modified": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "improvement_proposal_created": False,
        "autonomous_decision_created": False,
    }
    capture["replay_observation_layer_capture_hash"] = replay_hash(capture)
    return capture


def _source_artifact(wrapper_or_artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(wrapper_or_artifact, dict):
        raise FailClosedRuntimeError("replay observation failed closed: source artifact must be object")
    artifact = wrapper_or_artifact.get("artifact")
    if isinstance(artifact, dict):
        return artifact
    return wrapper_or_artifact


def _observation_category(wrapper: dict[str, Any], artifact: dict[str, Any]) -> str:
    if _is_certification_artifact(artifact):
        return CERTIFICATION
    if _is_validation_artifact(artifact):
        return VALIDATION
    if _is_provider_artifact(artifact):
        return PROVIDER
    if _is_worker_artifact(artifact):
        return WORKER
    if _is_governance_artifact(artifact):
        return GOVERNANCE
    if _is_failure(wrapper, artifact):
        return FAILURE
    if _is_warning(artifact):
        return WARNING
    return SUCCESS


def _observation_severity(wrapper: dict[str, Any], artifact: dict[str, Any]) -> str:
    if _is_failure(wrapper, artifact):
        return ERROR
    if _is_warning(artifact):
        return WARNING
    return INFO


def _execution_stage(wrapper: dict[str, Any], artifact: dict[str, Any]) -> str:
    for key in ("replay_step", "execution_stage", "stage", "failure_stage"):
        value = wrapper.get(key) if key == "replay_step" else artifact.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip().upper()
    artifact_type = artifact.get("artifact_type")
    if isinstance(artifact_type, str) and artifact_type.strip():
        return artifact_type.strip().upper()
    event_type = wrapper.get("event_type") or artifact.get("event_type")
    if isinstance(event_type, str) and event_type.strip():
        return event_type.strip().upper()
    return "UNKNOWN_REPLAY_STAGE"


def _originating_component(wrapper: dict[str, Any], artifact: dict[str, Any], category: str) -> str:
    if category == PROVIDER:
        return "PROVIDER_PLATFORM"
    if category == WORKER:
        return "WORKER_PLATFORM"
    if category == VALIDATION:
        return "RESULT_VALIDATION"
    if category == CERTIFICATION:
        return "REPLAY_CERTIFICATION"
    if category == GOVERNANCE:
        return "GOVERNANCE"
    component = artifact.get("originating_component") or artifact.get("component") or wrapper.get("component")
    if isinstance(component, str) and component.strip():
        return component.strip().upper()
    return "PLATFORM_CORE"


def _deterministic_message(category: str, severity: str, artifact: dict[str, Any]) -> str:
    failure = artifact.get("failure_reason")
    if severity == ERROR and isinstance(failure, str) and failure.strip():
        return f"{category} evidence failed closed: {failure.strip()}"
    if category == VALIDATION:
        return f"Validation evidence recorded with status {_status_value(artifact, 'validation_status')}."
    if category == CERTIFICATION:
        return f"Certification evidence recorded with status {_status_value(artifact, 'certification_status')}."
    if category == PROVIDER:
        return f"Provider evidence recorded with status {_status_value(artifact, 'provider_status')}."
    if category == WORKER:
        return f"Worker evidence recorded with status {_status_value(artifact, 'execution_status')}."
    if category == GOVERNANCE:
        return "Governance evidence recorded."
    if category == WARNING:
        return "Replay evidence recorded with warning severity."
    if category == FAILURE:
        return "Replay evidence failed closed."
    return "Replay evidence recorded successfully."


def _related_artifact_identifiers(artifact: dict[str, Any]) -> list[str]:
    identifiers: list[str] = []
    for key in sorted(artifact):
        if not key.endswith("_id") and key not in {
            "replay_reference",
            "proposal_id",
            "provider_id",
            "result_validation_id",
            "replay_certification_id",
            "worker_execution_id",
            "authorization_id",
        }:
            continue
        value = artifact.get(key)
        if isinstance(value, str) and value.strip():
            identifiers.append(f"{key}:{value.strip()}")
    return identifiers


def _is_provider_artifact(artifact: dict[str, Any]) -> bool:
    text = _artifact_text(artifact)
    return "PROVIDER" in text or "provider_invoked" in artifact or "provider_status" in artifact


def _is_worker_artifact(artifact: dict[str, Any]) -> bool:
    text = _artifact_text(artifact)
    return "WORKER" in text or "worker_invoked" in artifact or "worker_execution_id" in artifact


def _is_validation_artifact(artifact: dict[str, Any]) -> bool:
    text = _artifact_text(artifact)
    return "VALIDATION" in text or "validation_status" in artifact or "result_validation_id" in artifact


def _is_certification_artifact(artifact: dict[str, Any]) -> bool:
    text = _artifact_text(artifact)
    return "CERTIFICATION" in text or "certification_status" in artifact or "replay_certification_id" in artifact


def _is_governance_artifact(artifact: dict[str, Any]) -> bool:
    text = _artifact_text(artifact)
    return "GOVERNANCE" in text or "governance_authority" in artifact or "governance_modified" in artifact


def _is_failure(wrapper: dict[str, Any], artifact: dict[str, Any]) -> bool:
    values = [
        wrapper.get("event_type"),
        artifact.get("event_type"),
        artifact.get("certification_status"),
        artifact.get("validation_status"),
        artifact.get("execution_status"),
        artifact.get("provider_status"),
        artifact.get("status"),
        artifact.get("failure_reason"),
    ]
    return any(isinstance(value, str) and ("FAILED_CLOSED" in value.upper() or "FAIL" in value.upper()) for value in values)


def _is_warning(artifact: dict[str, Any]) -> bool:
    values = [artifact.get("readiness_status"), artifact.get("warning_status"), artifact.get("severity")]
    return any(isinstance(value, str) and ("WARNING" in value.upper() or "NOT_READY" in value.upper()) for value in values)


def _artifact_text(artifact: dict[str, Any]) -> str:
    values = [artifact.get("artifact_type"), artifact.get("runtime_version"), artifact.get("event_type")]
    return " ".join(value.upper() for value in values if isinstance(value, str))


def _status_value(artifact: dict[str, Any], key: str) -> str:
    value = artifact.get(key)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return "UNSPECIFIED"


def _source_artifact_hash(wrapper_or_artifact: dict[str, Any]) -> str | None:
    artifact = _source_artifact(wrapper_or_artifact)
    value = artifact.get("artifact_hash")
    if isinstance(value, str) and value.startswith("sha256:"):
        return value
    return None


def _source_replay_hash(wrapper_or_artifact: dict[str, Any]) -> str:
    value = wrapper_or_artifact.get("replay_hash")
    if isinstance(value, str) and value.startswith("sha256:"):
        return value
    return replay_hash(wrapper_or_artifact)


def _category_counts(observations: list[dict[str, Any]]) -> dict[str, int]:
    return {category: sum(1 for item in observations if item["observation_category"] == category) for category in sorted(OBSERVATION_CATEGORIES)}


def _severity_counts(observations: list[dict[str, Any]]) -> dict[str, int]:
    return {severity: sum(1 for item in observations if item["severity"] == severity) for severity in sorted(OBSERVATION_SEVERITIES)}


def _validate_observation(observation: dict[str, Any]) -> None:
    if observation.get("observation_category") not in OBSERVATION_CATEGORIES:
        raise FailClosedRuntimeError("replay observation failed closed: invalid observation category")
    if observation.get("severity") not in OBSERVATION_SEVERITIES:
        raise FailClosedRuntimeError("replay observation failed closed: invalid observation severity")
    for field in (
        "artifact_type",
        "runtime_version",
        "observation_id",
        "replay_identifier",
        "timestamp",
        "execution_stage",
        "originating_component",
        "deterministic_message",
    ):
        _require_string(observation.get(field), field)
    if observation.get("read_only_interpretation") is not True:
        raise FailClosedRuntimeError("replay observation failed closed: observations must be read-only")
    for field in (
        "source_replay_modified",
        "provider_invoked",
        "worker_invoked",
        "improvement_proposal_created",
        "autonomous_decision_created",
    ):
        if observation.get(field) is not False:
            raise FailClosedRuntimeError(f"replay observation failed closed: {field} must be false")
    if not isinstance(observation.get("related_artifact_identifiers"), list):
        raise FailClosedRuntimeError("replay observation failed closed: related identifiers must be a list")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str) or not actual.startswith("sha256:"):
        raise FailClosedRuntimeError("replay observation failed closed: replay hash required")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("replay observation failed closed: replay hash mismatch")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str) or not actual.startswith("sha256:"):
        raise FailClosedRuntimeError("replay observation failed closed: artifact hash required")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("replay observation failed closed: artifact hash mismatch")


def _ensure_observation_replay_available(replay_path: Path) -> None:
    if (replay_path / "000_replay_observation_layer_recorded.json").exists():
        raise FailClosedRuntimeError("replay observation failed closed: replay already exists")


def _optional_string(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"replay observation failed closed: {field_name} is required")
    return value.strip()
