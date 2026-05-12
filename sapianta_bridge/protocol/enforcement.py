"""Mandatory governance enforcement gate for bridge protocol artifacts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .lifecycle import validate_transition
from .schemas import PROTOCOL_VERSION, SUPPORTED_ARTIFACTS
from .validator import ValidationResult, validate_artifact


ARTIFACT_DISPLAY_NAMES = {
    "task.json": "task",
    "result.json": "result",
    "analysis_context.json": "analysis_context",
    "next_task_proposal.json": "next_task_proposal",
}


@dataclass(frozen=True)
class EnforcementResult:
    allowed_to_continue: bool
    artifact_type: str
    protocol_version: str | None
    required_state: str
    reasons: tuple[dict[str, str], ...]

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "allowed_to_continue": self.allowed_to_continue,
            "artifact_type": self.artifact_type,
            "required_state": self.required_state,
            "reasons": list(self.reasons),
        }
        if self.protocol_version is not None:
            result["protocol_version"] = self.protocol_version
        return result


def _error(field: str, reason: str) -> dict[str, str]:
    return {"field": field, "reason": reason}


def _display_type(artifact_type: str) -> str:
    return ARTIFACT_DISPLAY_NAMES.get(artifact_type, "unknown")


def classify_artifact(artifact: Any, path: str | Path | None = None) -> str | None:
    """Classify supported protocol artifacts deterministically."""
    if path is not None:
        name = Path(path).name
        if name in SUPPORTED_ARTIFACTS:
            return name

    if not isinstance(artifact, dict):
        return None

    if "result_id" in artifact:
        return "result.json"
    if "analysis_context_id" in artifact:
        return "analysis_context.json"
    if "proposal_id" in artifact:
        return "next_task_proposal.json"
    if "task_type" in artifact or "validation_required" in artifact:
        return "task.json"
    return None


def load_json_artifact(path: str | Path) -> tuple[Any | None, tuple[dict[str, str], ...]]:
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        return None, (_error("artifact_path", f"unable to read artifact: {exc}"),)
    try:
        return json.loads(raw), ()
    except json.JSONDecodeError:
        return None, (_error("json", "invalid JSON"),)


def enforce_artifact(
    artifact: Any,
    *,
    artifact_type: str | None = None,
    path: str | Path | None = None,
    current_state: str | None = None,
    next_state: str | None = None,
    evidence: Any = None,
) -> EnforcementResult:
    detected_type = artifact_type or classify_artifact(artifact, path)
    if detected_type not in SUPPORTED_ARTIFACTS:
        return EnforcementResult(
            False,
            "unknown",
            artifact.get("protocol_version") if isinstance(artifact, dict) else None,
            "QUARANTINED",
            (_error("artifact_type", "unsupported or unknown artifact type"),),
        )

    validation = validate_artifact(artifact, detected_type)
    if not validation.valid:
        return EnforcementResult(
            False,
            _display_type(detected_type),
            artifact.get("protocol_version") if isinstance(artifact, dict) else None,
            "QUARANTINED",
            validation.errors,
        )

    reasons: list[dict[str, str]] = []
    if current_state is not None or next_state is not None:
        if current_state is None:
            reasons.append(_error("current_state", "missing lifecycle state"))
        if next_state is None:
            reasons.append(_error("next_state", "missing lifecycle state"))
        if not reasons:
            transition = validate_transition(current_state, next_state, evidence=evidence)
            if not transition.valid:
                reasons.extend(transition.errors)
        if reasons:
            return EnforcementResult(
                False,
                _display_type(detected_type),
                artifact.get("protocol_version"),
                "QUARANTINED",
                tuple(reasons),
            )

    return EnforcementResult(
        True,
        _display_type(detected_type),
        PROTOCOL_VERSION,
        next_state or "VALIDATED",
        (),
    )


def enforce_artifact_path(
    path: str | Path,
    *,
    current_state: str | None = None,
    next_state: str | None = None,
    evidence: Any = None,
) -> EnforcementResult:
    artifact, errors = load_json_artifact(path)
    if errors:
        return EnforcementResult(False, "unknown", None, "QUARANTINED", errors)
    return enforce_artifact(
        artifact,
        path=path,
        current_state=current_state,
        next_state=next_state,
        evidence=evidence,
    )


def cli_validation_output(enforcement: EnforcementResult) -> dict[str, Any]:
    if enforcement.allowed_to_continue:
        return {
            "valid": True,
            "artifact_type": enforcement.artifact_type,
            "protocol_version": enforcement.protocol_version,
            "state": enforcement.required_state,
        }
    return {
        "valid": False,
        "artifact_type": enforcement.artifact_type,
        "errors": list(enforcement.reasons),
        "recommended_state": "QUARANTINED",
    }
