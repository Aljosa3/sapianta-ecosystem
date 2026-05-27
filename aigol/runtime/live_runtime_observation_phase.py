"""Replay-visible live runtime observation artifacts."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from aigol.runtime.live_semantic_pressure_validation import (
    AMBIGUITY_PRESSURE,
    CONTAINED,
    HIDDEN_AUTHORITY_DRIFT,
    INVALIDATED,
    REJECTED,
    LiveSemanticPressureValidationEvidence,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


OBSERVED = "OBSERVED"
REJECTED_STATUS = "REJECTED"

COGNITION_DRIFT = "COGNITION_DRIFT"
AMBIGUITY_TELEMETRY = "AMBIGUITY_TELEMETRY"
REPLAY_CONTINUITY = "REPLAY_CONTINUITY"
GOVERNANCE_PRESSURE = "GOVERNANCE_PRESSURE"

ALLOWED_OBSERVATION_STATUSES = frozenset({OBSERVED, REJECTED_STATUS})
ALLOWED_OBSERVATION_TYPES = frozenset(
    {
        COGNITION_DRIFT,
        AMBIGUITY_TELEMETRY,
        REPLAY_CONTINUITY,
        GOVERNANCE_PRESSURE,
    }
)


def _immutable(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({key: _immutable(value[key]) for key in sorted(value)})
    if isinstance(value, list | tuple):
        return tuple(_immutable(item) for item in value)
    return deepcopy(value)


def _plain(value: Any) -> Any:
    if isinstance(value, MappingProxyType):
        return {key: _plain(value[key]) for key in value}
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    return deepcopy(value)


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _observation_hash_input(observation: "LiveRuntimeObservationArtifact") -> dict[str, Any]:
    return {
        "observation_id": observation.observation_id,
        "source_reference": observation.source_reference,
        "observation_type": observation.observation_type,
        "observation_status": observation.observation_status,
        "telemetry": _plain(observation.telemetry),
        "reason": observation.reason,
        "created_at": observation.created_at,
    }


@dataclass(frozen=True)
class LiveRuntimeObservationArtifact:
    """Immutable replay-visible runtime observation evidence."""

    observation_id: str
    source_reference: str
    observation_type: str
    observation_status: str
    telemetry: MappingProxyType
    reason: str
    created_at: str
    evidence_hash: str = ""

    def __post_init__(self) -> None:
        _require_string(self.observation_id, "observation_id")
        _require_string(self.source_reference, "source_reference")
        _require_string(self.observation_type, "observation_type")
        _require_string(self.reason, "reason")
        _require_string(self.created_at, "created_at")
        if self.observation_type not in ALLOWED_OBSERVATION_TYPES:
            raise FailClosedRuntimeError("observation type is not allowed")
        if self.observation_status not in ALLOWED_OBSERVATION_STATUSES:
            raise FailClosedRuntimeError("observation status is not allowed")
        if not isinstance(self.telemetry, dict | MappingProxyType):
            raise FailClosedRuntimeError("telemetry must be a JSON object")
        telemetry = _immutable(_plain(self.telemetry))
        canonical_serialize(_plain(telemetry))
        object.__setattr__(self, "telemetry", telemetry)
        expected_hash = replay_hash(_observation_hash_input(self))
        if self.evidence_hash and self.evidence_hash != expected_hash:
            raise FailClosedRuntimeError("runtime observation evidence hash mismatch")
        object.__setattr__(self, "evidence_hash", self.evidence_hash or expected_hash)

    def to_dict(self) -> dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "source_reference": self.source_reference,
            "observation_type": self.observation_type,
            "observation_status": self.observation_status,
            "telemetry": _plain(self.telemetry),
            "reason": self.reason,
            "created_at": self.created_at,
            "evidence_hash": self.evidence_hash,
        }

    @classmethod
    def from_dict(cls, observation: dict[str, Any]) -> "LiveRuntimeObservationArtifact":
        if not isinstance(observation, dict):
            raise FailClosedRuntimeError("runtime observation must be a JSON object")
        required = {
            "observation_id",
            "source_reference",
            "observation_type",
            "observation_status",
            "telemetry",
            "reason",
            "created_at",
            "evidence_hash",
        }
        if set(observation) != required:
            raise FailClosedRuntimeError("runtime observation has malformed structure")
        return cls(**observation)


def observe_cognition_drift(
    *,
    observation_id: str,
    pressure_evidence: LiveSemanticPressureValidationEvidence | dict[str, Any],
    created_at: str,
) -> LiveRuntimeObservationArtifact:
    """Classify drift signals from existing semantic pressure evidence."""

    try:
        pressure = _coerce_pressure(pressure_evidence)
        drift_detected = pressure.pressure_type == HIDDEN_AUTHORITY_DRIFT or pressure.containment_status == INVALIDATED
        return LiveRuntimeObservationArtifact(
            observation_id=observation_id,
            source_reference=pressure.validation_id,
            observation_type=COGNITION_DRIFT,
            observation_status=OBSERVED,
            telemetry={
                "drift_detected": drift_detected,
                "pressure_type": pressure.pressure_type,
                "containment_status": pressure.containment_status,
                "source_evidence_hash": pressure.evidence_hash,
            },
            reason="cognition drift observation recorded",
            created_at=created_at,
        )
    except (FailClosedRuntimeError, TypeError, ValueError, KeyError):
        return _rejected_observation(observation_id, COGNITION_DRIFT, created_at)


def observe_ambiguity_telemetry(
    *,
    observation_id: str,
    pressure_evidence: LiveSemanticPressureValidationEvidence | dict[str, Any],
    created_at: str,
) -> LiveRuntimeObservationArtifact:
    """Record ambiguity telemetry from existing semantic pressure evidence."""

    try:
        pressure = _coerce_pressure(pressure_evidence)
        return LiveRuntimeObservationArtifact(
            observation_id=observation_id,
            source_reference=pressure.validation_id,
            observation_type=AMBIGUITY_TELEMETRY,
            observation_status=OBSERVED,
            telemetry={
                "ambiguity_detected": pressure.pressure_type == AMBIGUITY_PRESSURE,
                "ambiguity_rejected": pressure.pressure_type == AMBIGUITY_PRESSURE and pressure.containment_status == REJECTED,
                "containment_status": pressure.containment_status,
                "source_evidence_hash": pressure.evidence_hash,
            },
            reason="ambiguity telemetry recorded",
            created_at=created_at,
        )
    except (FailClosedRuntimeError, TypeError, ValueError, KeyError):
        return _rejected_observation(observation_id, AMBIGUITY_TELEMETRY, created_at)


def observe_replay_continuity(
    *,
    observation_id: str,
    lineage_evidence: dict[str, Any],
    created_at: str,
) -> LiveRuntimeObservationArtifact:
    """Record replay continuity from an existing lineage artifact."""

    try:
        if not isinstance(lineage_evidence, dict):
            raise FailClosedRuntimeError("lineage_evidence must be a JSON object")
        canonical_serialize(lineage_evidence)
        source_reference = _require_string(str(lineage_evidence.get("lineage_hash", "")), "lineage_hash")
        replay_continuous = (
            lineage_evidence.get("append_only_valid") is True
            and lineage_evidence.get("lineage_valid") is True
            and isinstance(lineage_evidence.get("lineage_hash"), str)
        )
        return LiveRuntimeObservationArtifact(
            observation_id=observation_id,
            source_reference=source_reference,
            observation_type=REPLAY_CONTINUITY,
            observation_status=OBSERVED,
            telemetry={
                "replay_continuous": replay_continuous,
                "append_only_valid": lineage_evidence.get("append_only_valid") is True,
                "lineage_valid": lineage_evidence.get("lineage_valid") is True,
                "lineage_hash": lineage_evidence["lineage_hash"],
            },
            reason="replay continuity telemetry recorded",
            created_at=created_at,
        )
    except (FailClosedRuntimeError, TypeError, ValueError, KeyError):
        return _rejected_observation(observation_id, REPLAY_CONTINUITY, created_at)


def observe_governance_pressure(
    *,
    observation_id: str,
    pressure_evidence: list[LiveSemanticPressureValidationEvidence | dict[str, Any]]
    | tuple[LiveSemanticPressureValidationEvidence | dict[str, Any], ...],
    created_at: str,
) -> LiveRuntimeObservationArtifact:
    """Record bounded governance pressure counts from existing pressure evidence."""

    try:
        if not isinstance(pressure_evidence, list | tuple):
            raise FailClosedRuntimeError("pressure_evidence must be a list")
        pressures = [_coerce_pressure(item) for item in pressure_evidence]
        rejected_count = sum(1 for item in pressures if item.containment_status == REJECTED)
        invalidated_count = sum(1 for item in pressures if item.containment_status == INVALIDATED)
        contained_count = sum(1 for item in pressures if item.containment_status == CONTAINED)
        source_reference = replay_hash([item.to_dict() for item in pressures])
        return LiveRuntimeObservationArtifact(
            observation_id=observation_id,
            source_reference=source_reference,
            observation_type=GOVERNANCE_PRESSURE,
            observation_status=OBSERVED,
            telemetry={
                "pressure_count": len(pressures),
                "rejected_count": rejected_count,
                "invalidated_count": invalidated_count,
                "contained_count": contained_count,
                "source_evidence_hashes": [item.evidence_hash for item in pressures],
            },
            reason="governance pressure telemetry recorded",
            created_at=created_at,
        )
    except (FailClosedRuntimeError, TypeError, ValueError, KeyError):
        return _rejected_observation(observation_id, GOVERNANCE_PRESSURE, created_at)


def reconstruct_live_runtime_observation_lineage(
    observations: list[LiveRuntimeObservationArtifact | dict[str, Any]]
    | tuple[LiveRuntimeObservationArtifact | dict[str, Any], ...],
) -> dict[str, Any]:
    if not isinstance(observations, list | tuple):
        raise FailClosedRuntimeError("runtime observation lineage must be a list")
    reconstructed = []
    seen_observation_ids: set[str] = set()
    previous_created_at = ""
    for index, item in enumerate(observations):
        observation = LiveRuntimeObservationArtifact.from_dict(item) if isinstance(item, dict) else item
        if not isinstance(observation, LiveRuntimeObservationArtifact):
            raise FailClosedRuntimeError("runtime observation lineage entry is invalid")
        artifact = observation.to_dict()
        if artifact["observation_id"] in seen_observation_ids:
            raise FailClosedRuntimeError("runtime observation lineage contains duplicate observation_id")
        if previous_created_at and artifact["created_at"] < previous_created_at:
            raise FailClosedRuntimeError("runtime observation lineage ordering is not deterministic")
        canonical_serialize(artifact)
        seen_observation_ids.add(artifact["observation_id"])
        previous_created_at = artifact["created_at"]
        reconstructed.append(
            {
                "observation_index": index,
                "observation_id": artifact["observation_id"],
                "source_reference": artifact["source_reference"],
                "observation_type": artifact["observation_type"],
                "observation_status": artifact["observation_status"],
                "evidence_hash": artifact["evidence_hash"],
            }
        )
    lineage = {
        "observation_count": len(reconstructed),
        "observations": reconstructed,
        "append_only_valid": True,
        "lineage_valid": True,
        "governance_authority_separated": True,
    }
    lineage["lineage_hash"] = replay_hash(lineage)
    return lineage


def _coerce_pressure(
    pressure_evidence: LiveSemanticPressureValidationEvidence | dict[str, Any],
) -> LiveSemanticPressureValidationEvidence:
    pressure = (
        LiveSemanticPressureValidationEvidence.from_dict(pressure_evidence)
        if isinstance(pressure_evidence, dict)
        else pressure_evidence
    )
    if not isinstance(pressure, LiveSemanticPressureValidationEvidence):
        raise FailClosedRuntimeError("pressure evidence entry is invalid")
    return pressure


def _rejected_observation(observation_id: Any, observation_type: str, created_at: Any) -> LiveRuntimeObservationArtifact:
    return LiveRuntimeObservationArtifact(
        observation_id=observation_id if isinstance(observation_id, str) and observation_id else "OBSERVATION-INVALID",
        source_reference="SOURCE-INVALID",
        observation_type=observation_type,
        observation_status=REJECTED_STATUS,
        telemetry={},
        reason="runtime observation failed closed",
        created_at=created_at if isinstance(created_at, str) and created_at else "1970-01-01T00:00:00+00:00",
    )
