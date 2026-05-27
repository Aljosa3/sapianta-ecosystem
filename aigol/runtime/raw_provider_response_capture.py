"""Provider-agnostic raw response capture before bounded proposal normalization."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


NORMALIZED = "NORMALIZED"
REJECTED = "REJECTED"
ABSENT = "ABSENT"

ALLOWED_NORMALIZATION_STATUSES = frozenset({NORMALIZED, REJECTED, ABSENT})


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _raw_response_hash_input(evidence: "RawProviderResponseEvidence") -> dict[str, Any]:
    return {
        "raw_response_id": evidence.raw_response_id,
        "provider_name": evidence.provider_name,
        "model_name": evidence.model_name,
        "raw_response_present": evidence.raw_response_present,
        "raw_response_hash": evidence.raw_response_hash,
        "normalization_status": evidence.normalization_status,
        "normalization_reason": evidence.normalization_reason,
        "created_at": evidence.created_at,
    }


@dataclass(frozen=True)
class RawProviderResponseEvidence:
    """Immutable replay-visible raw provider response evidence.

    Provider-agnostic: stores the raw textual response any provider adapter
    received, the deterministic hash of that text, and the normalization
    outcome attempted by the adapter. AiGOL core does not consume the raw
    text directly; only normalized BoundedCognitionProposal evidence may
    be promoted past this boundary.
    """

    raw_response_id: str
    provider_name: str
    model_name: str
    raw_response_present: bool
    raw_response_text: str
    raw_response_hash: str
    normalization_status: str
    normalization_reason: str
    created_at: str
    evidence_hash: str = ""

    def __post_init__(self) -> None:
        _require_string(self.raw_response_id, "raw_response_id")
        _require_string(self.provider_name, "provider_name")
        _require_string(self.model_name, "model_name")
        _require_string(self.normalization_reason, "normalization_reason")
        _require_string(self.created_at, "created_at")
        if not isinstance(self.raw_response_present, bool):
            raise FailClosedRuntimeError("raw_response_present must be boolean")
        if self.normalization_status not in ALLOWED_NORMALIZATION_STATUSES:
            raise FailClosedRuntimeError("raw provider response normalization status is not allowed")
        if not isinstance(self.raw_response_text, str):
            raise FailClosedRuntimeError("raw_response_text must be a string")
        if not isinstance(self.raw_response_hash, str):
            raise FailClosedRuntimeError("raw_response_hash must be a string")
        if self.raw_response_present:
            if not self.raw_response_text:
                raise FailClosedRuntimeError("raw_response_text is required when raw_response_present is true")
            expected_text_hash = replay_hash(self.raw_response_text)
            if self.raw_response_hash != expected_text_hash:
                raise FailClosedRuntimeError("raw_response_hash does not match raw_response_text")
        else:
            if self.raw_response_text != "" or self.raw_response_hash != "":
                raise FailClosedRuntimeError("raw_response_text and raw_response_hash must be empty when absent")
        expected_hash = replay_hash(_raw_response_hash_input(self))
        if self.evidence_hash and self.evidence_hash != expected_hash:
            raise FailClosedRuntimeError("raw provider response evidence hash mismatch")
        object.__setattr__(self, "evidence_hash", self.evidence_hash or expected_hash)

    def to_dict(self) -> dict[str, Any]:
        return {
            "raw_response_id": self.raw_response_id,
            "provider_name": self.provider_name,
            "model_name": self.model_name,
            "raw_response_present": self.raw_response_present,
            "raw_response_text": self.raw_response_text,
            "raw_response_hash": self.raw_response_hash,
            "normalization_status": self.normalization_status,
            "normalization_reason": self.normalization_reason,
            "created_at": self.created_at,
            "evidence_hash": self.evidence_hash,
        }

    @classmethod
    def from_dict(cls, evidence: dict[str, Any]) -> "RawProviderResponseEvidence":
        if not isinstance(evidence, dict):
            raise FailClosedRuntimeError("raw provider response evidence must be a JSON object")
        required = {
            "raw_response_id",
            "provider_name",
            "model_name",
            "raw_response_present",
            "raw_response_text",
            "raw_response_hash",
            "normalization_status",
            "normalization_reason",
            "created_at",
            "evidence_hash",
        }
        if set(evidence) != required:
            raise FailClosedRuntimeError("raw provider response evidence has malformed structure")
        return cls(**evidence)


def capture_raw_provider_response(
    *,
    raw_response_id: str,
    provider_name: str,
    model_name: str,
    raw_response_text: str | None,
    normalization_status: str,
    normalization_reason: str,
    created_at: str,
) -> RawProviderResponseEvidence:
    """Construct provider-agnostic raw response evidence from adapter output."""

    _require_string(raw_response_id, "raw_response_id")
    _require_string(provider_name, "provider_name")
    _require_string(model_name, "model_name")
    _require_string(normalization_reason, "normalization_reason")
    _require_string(created_at, "created_at")
    if normalization_status not in ALLOWED_NORMALIZATION_STATUSES:
        raise FailClosedRuntimeError("raw provider response normalization status is not allowed")
    if raw_response_text is None or raw_response_text == "":
        present = False
        text = ""
        text_hash = ""
    else:
        if not isinstance(raw_response_text, str):
            raise FailClosedRuntimeError("raw_response_text must be a string")
        present = True
        text = raw_response_text
        text_hash = replay_hash(text)
    return RawProviderResponseEvidence(
        raw_response_id=raw_response_id,
        provider_name=provider_name,
        model_name=model_name,
        raw_response_present=present,
        raw_response_text=text,
        raw_response_hash=text_hash,
        normalization_status=normalization_status,
        normalization_reason=normalization_reason,
        created_at=created_at,
    )


def reconstruct_raw_provider_response_lineage(
    evidence: list[RawProviderResponseEvidence | dict[str, Any]]
    | tuple[RawProviderResponseEvidence | dict[str, Any], ...],
) -> dict[str, Any]:
    if not isinstance(evidence, list | tuple):
        raise FailClosedRuntimeError("raw provider response lineage must be a list")
    reconstructed = []
    seen_response_ids: set[str] = set()
    previous_created_at = ""
    for index, item in enumerate(evidence):
        evidence_obj = (
            RawProviderResponseEvidence.from_dict(item) if isinstance(item, dict) else item
        )
        if not isinstance(evidence_obj, RawProviderResponseEvidence):
            raise FailClosedRuntimeError("raw provider response lineage entry is invalid")
        artifact = evidence_obj.to_dict()
        if artifact["raw_response_id"] in seen_response_ids:
            raise FailClosedRuntimeError("raw provider response lineage contains duplicate raw_response_id")
        if previous_created_at and artifact["created_at"] < previous_created_at:
            raise FailClosedRuntimeError("raw provider response lineage ordering is not deterministic")
        canonical_serialize(artifact)
        seen_response_ids.add(artifact["raw_response_id"])
        previous_created_at = artifact["created_at"]
        reconstructed.append(
            {
                "raw_response_index": index,
                "raw_response_id": artifact["raw_response_id"],
                "provider_name": artifact["provider_name"],
                "model_name": artifact["model_name"],
                "raw_response_present": artifact["raw_response_present"],
                "normalization_status": artifact["normalization_status"],
                "evidence_hash": artifact["evidence_hash"],
            }
        )
    lineage = {
        "raw_response_count": len(reconstructed),
        "raw_provider_responses": reconstructed,
        "append_only_valid": True,
        "lineage_valid": True,
        "governance_authority_separated": True,
        "llm_boundary": "raw_response_pre_normalization_only",
    }
    lineage["lineage_hash"] = replay_hash(lineage)
    return lineage
