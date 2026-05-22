"""Deterministic ChatGPT ingress artifact construction.

The artifact is future ChatGPT semantic transport input only. It performs no
LLM calls, provider calls, approval, dispatch, orchestration, or execution.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

ARTIFACT_TYPE = "CHATGPT_INGRESS_ARTIFACT_V1"
SCHEMA_VERSION = "1.0"
SOURCE = "chatgpt"
BOUNDARY_STATEMENT = "ChatGPT output is semantic input only and cannot authorize execution."
ACCEPTED_AS_SEMANTIC_INPUT = "ACCEPTED_AS_SEMANTIC_INPUT"

AUTHORITY_BOUNDARY = {
    "chatgpt_authority": False,
    "execution_authority": False,
    "governance_authority": False,
    "approval_authority": False,
    "provider_dispatch_authority": False,
    "autonomous_continuation_authority": False,
    "boundary_statement": BOUNDARY_STATEMENT,
}


def _canonical_copy(value: Any) -> Any:
    return deepcopy(value)


def hash_text(value: str) -> str:
    """Hash text through the same canonical JSON hashing used by AGOL transport."""

    return canonical_hash(str(value or ""))


def replay_identity_for(
    *,
    session_id: str,
    human_request_hash: str,
    semantic_output_hash: str,
    schema_version: str = SCHEMA_VERSION,
) -> str:
    seed = {
        "human_request_hash": human_request_hash,
        "schema_version": schema_version,
        "semantic_output_hash": semantic_output_hash,
        "session_id": str(session_id or "").strip(),
    }
    return f"CHATGPT-INGRESS-REPLAY-{canonical_hash(seed)[7:31]}"


def artifact_hash_input(artifact: dict) -> dict:
    artifact_copy = _canonical_copy(artifact)
    hashes = artifact_copy.get("hashes")
    if isinstance(hashes, dict):
        hashes.pop("artifact_hash", None)
    return artifact_copy


def artifact_hash_for(artifact: dict) -> str:
    return canonical_hash(artifact_hash_input(artifact))


def create_chatgpt_ingress_artifact(
    *,
    created_at: str,
    session_id: str,
    human_request: str,
    chatgpt_semantic_output: str,
    normalized_intent: str,
    expected_artifacts: list[str] | None = None,
    constraints: list[str] | None = None,
    forbidden_operations: list[str] | None = None,
    provenance: dict[str, Any] | None = None,
) -> dict:
    """Create a canonical, non-authoritative ChatGPT ingress artifact."""

    request_text = str(human_request or "").strip()
    semantic_output = str(chatgpt_semantic_output or "").strip()
    human_request_hash = hash_text(request_text)
    semantic_output_hash = hash_text(semantic_output)
    replay_identity = replay_identity_for(
        session_id=session_id,
        human_request_hash=human_request_hash,
        semantic_output_hash=semantic_output_hash,
    )
    artifact = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "source": SOURCE,
        "created_at": str(created_at or "").strip(),
        "session_id": str(session_id or "").strip(),
        "human_request": request_text,
        "chatgpt_semantic_output": semantic_output,
        "normalized_intent": str(normalized_intent or "").strip(),
        "expected_artifacts": list(expected_artifacts or []),
        "constraints": list(constraints or []),
        "forbidden_operations": list(forbidden_operations or []),
        "authority_boundary": _canonical_copy(AUTHORITY_BOUNDARY),
        "provenance": {
            "chatgpt_api_invoked_by_artifact": False,
            "live_adapter_present": False,
            "aigol_governance_required": True,
            "execution_authority": False,
            "provider_dispatch_authority": False,
            **_canonical_copy(provenance or {}),
        },
        "replay_identity": replay_identity,
        "hashes": {
            "human_request_hash": human_request_hash,
            "semantic_output_hash": semantic_output_hash,
        },
        "validation_status": ACCEPTED_AS_SEMANTIC_INPUT,
    }
    artifact["hashes"]["artifact_hash"] = artifact_hash_for(artifact)
    return artifact


__all__ = [
    "ACCEPTED_AS_SEMANTIC_INPUT",
    "ARTIFACT_TYPE",
    "AUTHORITY_BOUNDARY",
    "BOUNDARY_STATEMENT",
    "SCHEMA_VERSION",
    "SOURCE",
    "artifact_hash_for",
    "artifact_hash_input",
    "create_chatgpt_ingress_artifact",
    "hash_text",
    "replay_identity_for",
]
