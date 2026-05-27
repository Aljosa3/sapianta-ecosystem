"""Operational activation evidence for the live governed runtime."""

from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any

from aigol.runtime.live_runtime_usage_validation import VALIDATED, validate_live_runtime_usage
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.real_openai_api_invocation import OPENAI_API_KEY_ENV
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


ACTIVATED = "ACTIVATED"
REJECTED = "REJECTED"
ENVIRONMENT_READY = "READY"
ENVIRONMENT_REJECTED = "REJECTED"
RUNTIME_MODE = "LIVE_GOVERNED_READONLY"

ALLOWED_ACTIVATION_STATUSES = frozenset({ACTIVATED, REJECTED})
ALLOWED_ENVIRONMENT_STATUSES = frozenset({ENVIRONMENT_READY, ENVIRONMENT_REJECTED})


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _activation_hash_input(evidence: "RealRuntimeActivationEvidence") -> dict[str, Any]:
    return {
        "activation_id": evidence.activation_id,
        "runtime_mode": evidence.runtime_mode,
        "environment_status": evidence.environment_status,
        "usage_validation_evidence_hash": evidence.usage_validation_evidence_hash,
        "activation_status": evidence.activation_status,
        "activation_reason": evidence.activation_reason,
        "created_at": evidence.created_at,
    }


@dataclass(frozen=True)
class RealRuntimeActivationEvidence:
    """Immutable replay-visible operational activation evidence."""

    activation_id: str
    runtime_mode: str
    environment_status: str
    usage_validation_evidence_hash: str
    activation_status: str
    activation_reason: str
    created_at: str
    evidence_hash: str = ""

    def __post_init__(self) -> None:
        _require_string(self.activation_id, "activation_id")
        _require_string(self.runtime_mode, "runtime_mode")
        _require_string(self.environment_status, "environment_status")
        _require_string(self.activation_reason, "activation_reason")
        _require_string(self.created_at, "created_at")
        if self.runtime_mode != RUNTIME_MODE:
            raise FailClosedRuntimeError("runtime activation mode is not allowed")
        if self.environment_status not in ALLOWED_ENVIRONMENT_STATUSES:
            raise FailClosedRuntimeError("runtime activation environment status is not allowed")
        if self.activation_status not in ALLOWED_ACTIVATION_STATUSES:
            raise FailClosedRuntimeError("runtime activation status is not allowed")
        expected_hash = replay_hash(_activation_hash_input(self))
        if self.evidence_hash and self.evidence_hash != expected_hash:
            raise FailClosedRuntimeError("real runtime activation evidence hash mismatch")
        object.__setattr__(self, "evidence_hash", self.evidence_hash or expected_hash)

    def to_dict(self) -> dict[str, Any]:
        return {
            "activation_id": self.activation_id,
            "runtime_mode": self.runtime_mode,
            "environment_status": self.environment_status,
            "usage_validation_evidence_hash": self.usage_validation_evidence_hash,
            "activation_status": self.activation_status,
            "activation_reason": self.activation_reason,
            "created_at": self.created_at,
            "evidence_hash": self.evidence_hash,
        }

    @classmethod
    def from_dict(cls, evidence: dict[str, Any]) -> "RealRuntimeActivationEvidence":
        if not isinstance(evidence, dict):
            raise FailClosedRuntimeError("real runtime activation evidence must be a JSON object")
        required = {
            "activation_id",
            "runtime_mode",
            "environment_status",
            "usage_validation_evidence_hash",
            "activation_status",
            "activation_reason",
            "created_at",
            "evidence_hash",
        }
        if set(evidence) != required:
            raise FailClosedRuntimeError("real runtime activation evidence has malformed structure")
        return cls(**evidence)


def activate_real_runtime(
    *,
    activation_id: str,
    human_prompt: str,
    created_at: str,
    timeout_seconds: int = 20,
) -> dict[str, Any]:
    """Activate one readonly governed runtime usage in the current environment."""

    try:
        _require_string(activation_id, "activation_id")
        prompt = " ".join(_require_string(human_prompt, "human_prompt").split())
        _require_string(created_at, "created_at")
        _load_activation_api_key()
        usage_validation = validate_live_runtime_usage(
            validation_id=f"{activation_id}:USAGE_VALIDATION",
            human_prompts=[prompt],
            created_at=created_at,
            timeout_seconds=timeout_seconds,
        )
        usage_evidence = usage_validation["usage_validation_evidence"]
        activation_status = ACTIVATED if usage_evidence.validation_status == VALIDATED else REJECTED
        evidence = RealRuntimeActivationEvidence(
            activation_id=activation_id,
            runtime_mode=RUNTIME_MODE,
            environment_status=ENVIRONMENT_READY,
            usage_validation_evidence_hash=usage_evidence.evidence_hash,
            activation_status=activation_status,
            activation_reason=(
                "real runtime activation completed"
                if activation_status == ACTIVATED
                else "real runtime activation failed closed"
            ),
            created_at=created_at,
        )
        return {
            "activation_evidence": evidence,
            "usage_validation": usage_validation,
            "activation_lineage": reconstruct_real_runtime_activation_lineage([evidence]),
            "governance_authority_separated": True,
        }
    except (FailClosedRuntimeError, TypeError, ValueError, KeyError):
        evidence = RealRuntimeActivationEvidence(
            activation_id=activation_id if isinstance(activation_id, str) and activation_id else "ACTIVATION-INVALID",
            runtime_mode=RUNTIME_MODE,
            environment_status=ENVIRONMENT_REJECTED,
            usage_validation_evidence_hash="",
            activation_status=REJECTED,
            activation_reason="real runtime activation failed closed",
            created_at=created_at if isinstance(created_at, str) and created_at else "1970-01-01T00:00:00+00:00",
        )
        return {
            "activation_evidence": evidence,
            "usage_validation": None,
            "activation_lineage": reconstruct_real_runtime_activation_lineage([evidence]),
            "governance_authority_separated": True,
        }


def reconstruct_real_runtime_activation_lineage(
    activations: list[RealRuntimeActivationEvidence | dict[str, Any]]
    | tuple[RealRuntimeActivationEvidence | dict[str, Any], ...],
) -> dict[str, Any]:
    if not isinstance(activations, list | tuple):
        raise FailClosedRuntimeError("real runtime activation lineage must be a list")
    reconstructed = []
    seen_activation_ids: set[str] = set()
    previous_created_at = ""
    for index, activation in enumerate(activations):
        activation_obj = RealRuntimeActivationEvidence.from_dict(activation) if isinstance(activation, dict) else activation
        if not isinstance(activation_obj, RealRuntimeActivationEvidence):
            raise FailClosedRuntimeError("real runtime activation lineage entry is invalid")
        artifact = activation_obj.to_dict()
        if artifact["activation_id"] in seen_activation_ids:
            raise FailClosedRuntimeError("real runtime activation lineage contains duplicate activation_id")
        if previous_created_at and artifact["created_at"] < previous_created_at:
            raise FailClosedRuntimeError("real runtime activation lineage ordering is not deterministic")
        canonical_serialize(artifact)
        seen_activation_ids.add(artifact["activation_id"])
        previous_created_at = artifact["created_at"]
        reconstructed.append(
            {
                "activation_index": index,
                "activation_id": artifact["activation_id"],
                "runtime_mode": artifact["runtime_mode"],
                "activation_status": artifact["activation_status"],
                "evidence_hash": artifact["evidence_hash"],
            }
        )
    lineage = {
        "activation_count": len(reconstructed),
        "activations": reconstructed,
        "append_only_valid": True,
        "lineage_valid": True,
        "governance_authority_separated": True,
    }
    lineage["lineage_hash"] = replay_hash(lineage)
    return lineage


def _load_activation_api_key() -> str:
    try:
        api_key = os.environ[OPENAI_API_KEY_ENV]
    except KeyError as exc:
        raise FailClosedRuntimeError("OPENAI_API_KEY is required for runtime activation") from exc
    return _require_string(api_key, OPENAI_API_KEY_ENV)
