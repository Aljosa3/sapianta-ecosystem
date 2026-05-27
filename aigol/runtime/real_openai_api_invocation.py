"""Real OpenAI Responses API invocation for bounded proposal normalization."""

from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any

from aigol.runtime.live_openai_runtime_connector import (
    NORMALIZED,
    OPENAI_MODEL_IDENTIFIER,
    OPENAI_PROVIDER,
    invoke_live_openai_runtime_connector,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


INVOKED = "INVOKED"
REJECTED = "REJECTED"
OPENAI_API_KEY_ENV = "OPENAI_API_KEY"
DEFAULT_TIMEOUT_SECONDS = 20
ALLOWED_INVOCATION_STATUSES = frozenset({INVOKED, REJECTED})


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _invocation_hash_input(evidence: "RealOpenAIAPIInvocationEvidence") -> dict[str, Any]:
    return {
        "invocation_id": evidence.invocation_id,
        "api_provider": evidence.api_provider,
        "model_identifier": evidence.model_identifier,
        "api_key_env": evidence.api_key_env,
        "timeout_seconds": evidence.timeout_seconds,
        "connector_evidence_hash": evidence.connector_evidence_hash,
        "invocation_status": evidence.invocation_status,
        "reason": evidence.reason,
        "created_at": evidence.created_at,
    }


@dataclass(frozen=True)
class RealOpenAIAPIInvocationEvidence:
    """Immutable replay-visible real OpenAI API invocation evidence."""

    invocation_id: str
    api_provider: str
    model_identifier: str
    api_key_env: str
    timeout_seconds: int
    connector_evidence_hash: str
    invocation_status: str
    reason: str
    created_at: str
    evidence_hash: str = ""

    def __post_init__(self) -> None:
        _require_string(self.invocation_id, "invocation_id")
        _require_string(self.api_provider, "api_provider")
        _require_string(self.model_identifier, "model_identifier")
        _require_string(self.api_key_env, "api_key_env")
        _require_string(self.reason, "reason")
        _require_string(self.created_at, "created_at")
        if self.api_provider != OPENAI_PROVIDER:
            raise FailClosedRuntimeError("real OpenAI API provider is not allowed")
        if self.model_identifier != OPENAI_MODEL_IDENTIFIER:
            raise FailClosedRuntimeError("real OpenAI API model identifier is not allowed")
        if self.api_key_env != OPENAI_API_KEY_ENV:
            raise FailClosedRuntimeError("real OpenAI API key environment variable is not allowed")
        if not isinstance(self.timeout_seconds, int) or self.timeout_seconds < 1 or self.timeout_seconds > 30:
            raise FailClosedRuntimeError("real OpenAI API timeout is outside the bounded range")
        if self.invocation_status not in ALLOWED_INVOCATION_STATUSES:
            raise FailClosedRuntimeError("real OpenAI API invocation status is not allowed")
        expected_hash = replay_hash(_invocation_hash_input(self))
        if self.evidence_hash and self.evidence_hash != expected_hash:
            raise FailClosedRuntimeError("real OpenAI API invocation evidence hash mismatch")
        object.__setattr__(self, "evidence_hash", self.evidence_hash or expected_hash)

    def to_dict(self) -> dict[str, Any]:
        return {
            "invocation_id": self.invocation_id,
            "api_provider": self.api_provider,
            "model_identifier": self.model_identifier,
            "api_key_env": self.api_key_env,
            "timeout_seconds": self.timeout_seconds,
            "connector_evidence_hash": self.connector_evidence_hash,
            "invocation_status": self.invocation_status,
            "reason": self.reason,
            "created_at": self.created_at,
            "evidence_hash": self.evidence_hash,
        }

    @classmethod
    def from_dict(cls, evidence: dict[str, Any]) -> "RealOpenAIAPIInvocationEvidence":
        if not isinstance(evidence, dict):
            raise FailClosedRuntimeError("real OpenAI API invocation evidence must be a JSON object")
        required = {
            "invocation_id",
            "api_provider",
            "model_identifier",
            "api_key_env",
            "timeout_seconds",
            "connector_evidence_hash",
            "invocation_status",
            "reason",
            "created_at",
            "evidence_hash",
        }
        if set(evidence) != required:
            raise FailClosedRuntimeError("real OpenAI API invocation evidence has malformed structure")
        return cls(**evidence)


def invoke_real_openai_api(
    *,
    invocation_id: str,
    human_request: str,
    created_at: str,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Invoke the OpenAI Responses API once and normalize output through governance."""

    try:
        _require_string(invocation_id, "invocation_id")
        normalized_human_request = " ".join(_require_string(human_request, "human_request").split())
        _require_string(created_at, "created_at")
        timeout = _normalize_timeout(timeout_seconds)
        api_key = _load_api_key()

        def openai_call(normalized_request: dict[str, Any]) -> Any:
            return _call_openai_responses_api(
                normalized_request=normalized_request,
                api_key=api_key,
                timeout_seconds=timeout,
            )

        connector = invoke_live_openai_runtime_connector(
            inference_id=f"{invocation_id}:OPENAI",
            prompt=normalized_human_request,
            openai_call=openai_call,
            created_at=created_at,
        )
        connector_evidence = connector["connector_evidence"]
        invocation_status = INVOKED if connector_evidence.connector_status == NORMALIZED else REJECTED
        reason = (
            "real OpenAI API inference normalized into bounded proposal evidence"
            if invocation_status == INVOKED
            else "real OpenAI API inference failed closed"
        )
        evidence = RealOpenAIAPIInvocationEvidence(
            invocation_id=invocation_id,
            api_provider=OPENAI_PROVIDER,
            model_identifier=OPENAI_MODEL_IDENTIFIER,
            api_key_env=OPENAI_API_KEY_ENV,
            timeout_seconds=timeout,
            connector_evidence_hash=connector_evidence.evidence_hash,
            invocation_status=invocation_status,
            reason=reason,
            created_at=created_at,
        )
        return {
            "invocation_evidence": evidence,
            "connector": connector,
            "proposal": connector["proposal"],
            "proposal_lineage": connector["proposal_lineage"],
            "governance_authority_separated": True,
        }
    except (FailClosedRuntimeError, TypeError, ValueError, KeyError, ImportError):
        evidence = RealOpenAIAPIInvocationEvidence(
            invocation_id=invocation_id if isinstance(invocation_id, str) and invocation_id else "OPENAI-INVOCATION-INVALID",
            api_provider=OPENAI_PROVIDER,
            model_identifier=OPENAI_MODEL_IDENTIFIER,
            api_key_env=OPENAI_API_KEY_ENV,
            timeout_seconds=timeout_seconds if isinstance(timeout_seconds, int) and 1 <= timeout_seconds <= 30 else DEFAULT_TIMEOUT_SECONDS,
            connector_evidence_hash="",
            invocation_status=REJECTED,
            reason="real OpenAI API invocation failed closed",
            created_at=created_at if isinstance(created_at, str) and created_at else "1970-01-01T00:00:00+00:00",
        )
        return {
            "invocation_evidence": evidence,
            "connector": None,
            "proposal": None,
            "proposal_lineage": None,
            "governance_authority_separated": True,
        }


def reconstruct_real_openai_api_invocation_lineage(
    evidence: list[RealOpenAIAPIInvocationEvidence | dict[str, Any]]
    | tuple[RealOpenAIAPIInvocationEvidence | dict[str, Any], ...],
) -> dict[str, Any]:
    if not isinstance(evidence, list | tuple):
        raise FailClosedRuntimeError("real OpenAI API invocation lineage must be a list")
    reconstructed = []
    seen_invocation_ids: set[str] = set()
    previous_created_at = ""
    for index, item in enumerate(evidence):
        evidence_obj = RealOpenAIAPIInvocationEvidence.from_dict(item) if isinstance(item, dict) else item
        if not isinstance(evidence_obj, RealOpenAIAPIInvocationEvidence):
            raise FailClosedRuntimeError("real OpenAI API invocation lineage entry is invalid")
        artifact = evidence_obj.to_dict()
        if artifact["invocation_id"] in seen_invocation_ids:
            raise FailClosedRuntimeError("real OpenAI API invocation lineage contains duplicate invocation_id")
        if previous_created_at and artifact["created_at"] < previous_created_at:
            raise FailClosedRuntimeError("real OpenAI API invocation lineage ordering is not deterministic")
        canonical_serialize(artifact)
        seen_invocation_ids.add(artifact["invocation_id"])
        previous_created_at = artifact["created_at"]
        reconstructed.append(
            {
                "invocation_index": index,
                "invocation_id": artifact["invocation_id"],
                "api_provider": artifact["api_provider"],
                "model_identifier": artifact["model_identifier"],
                "invocation_status": artifact["invocation_status"],
                "evidence_hash": artifact["evidence_hash"],
            }
        )
    lineage = {
        "invocation_count": len(reconstructed),
        "openai_api_invocations": reconstructed,
        "append_only_valid": True,
        "lineage_valid": True,
        "governance_authority_separated": True,
    }
    lineage["lineage_hash"] = replay_hash(lineage)
    return lineage


def _normalize_timeout(timeout_seconds: int) -> int:
    if not isinstance(timeout_seconds, int) or timeout_seconds < 1 or timeout_seconds > 30:
        raise FailClosedRuntimeError("real OpenAI API timeout is outside the bounded range")
    return timeout_seconds


def _load_api_key() -> str:
    try:
        api_key = os.environ[OPENAI_API_KEY_ENV]
    except KeyError as exc:
        raise FailClosedRuntimeError("OPENAI_API_KEY is required for real OpenAI API invocation") from exc
    return _require_string(api_key, OPENAI_API_KEY_ENV)


def _call_openai_responses_api(
    *,
    normalized_request: dict[str, Any],
    api_key: str,
    timeout_seconds: int,
) -> Any:
    from openai import OpenAI

    if not isinstance(normalized_request, dict):
        raise FailClosedRuntimeError("normalized OpenAI request must be a JSON object")
    client = OpenAI(api_key=api_key, timeout=timeout_seconds, max_retries=0)
    return client.responses.create(
        model=OPENAI_MODEL_IDENTIFIER,
        input=_bounded_openai_input(normalized_request),
    )


def _bounded_openai_input(normalized_request: dict[str, Any]) -> str:
    human_request = _require_string(normalized_request.get("input"), "input")
    return (
        "Return only compact JSON for bounded_cognition_proposal_v1 with exactly these keys: "
        "proposal_id, natural_language_input, proposal_type, requested_capabilities, "
        "proposed_contract_reference, created_at. "
        "proposal_type must be CONTRACT_PROPOSAL. "
        "requested_capabilities must be [\"metadata_inspection_provider\"]. "
        "proposed_contract_reference must begin with contract:. "
        f"Human request: {human_request}"
    )
