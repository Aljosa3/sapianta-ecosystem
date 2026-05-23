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
STRUCTURAL_CANDIDATE_ONLY = "STRUCTURAL_CANDIDATE_ONLY"

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


def _normalized_intent_from_text(value: str) -> str:
    normalized = []
    previous_underscore = False
    for character in str(value or "").upper():
        if "A" <= character <= "Z" or "0" <= character <= "9":
            normalized.append(character)
            previous_underscore = False
        elif not previous_underscore:
            normalized.append("_")
            previous_underscore = True
    text = "".join(normalized).strip("_")
    return text[:96] or "GOVERNED_SEMANTIC_INGRESS"


def generate_valid_chatgpt_ingress_artifact(
    *,
    human_request: str,
    semantic_intent: str,
    created_at: str = "1970-01-01T00:00:00Z",
    session_id: str | None = None,
) -> dict:
    """Generate a canonical governance-ready ingress artifact from minimal input.

    The generated artifact is structural candidate input only. It does not
    verify semantic correctness, grant governance authority, approve execution,
    dispatch providers, call Native Messaging, or continue autonomously.
    """

    request_text = str(human_request or "").strip()
    intent_text = str(semantic_intent or "").strip()
    request_hash = hash_text(request_text)
    intent_hash = hash_text(intent_text)
    generated_session_id = session_id or f"CHATGPT-INGRESS-GENERATED-{canonical_hash({'human_request_hash': request_hash, 'semantic_intent_hash': intent_hash})[7:23]}"
    artifact = create_chatgpt_ingress_artifact(
        created_at=created_at,
        session_id=generated_session_id,
        human_request=request_text,
        chatgpt_semantic_output=f"Bounded semantic ingress candidate: {intent_text}",
        normalized_intent=_normalized_intent_from_text(intent_text or request_text),
        expected_artifacts=[
            "semantic proposal candidate",
            "semantic contract candidate",
            "governance acceptance report",
        ],
        constraints=[
            "structural candidate only",
            "fail closed if required fields or hashes are invalid",
            "no execution authority",
            "provider boundary remains closed",
            "no semantic correctness verification",
            "continuation boundary remains closed",
        ],
        forbidden_operations=[
            "execution authorization",
            "provider dispatch",
            "governance approval claim",
            "semantic correctness claim",
            "autonomous continuation",
            "Native Messaging call",
            "Codex provider invocation",
        ],
        provenance={
            "generation_milestone": "VALID_CHATGPT_INGRESS_ARTIFACT_GENERATION_V1",
            "generation_mode": "DETERMINISTIC_LOCAL_CANONICAL_GENERATION",
            "minimal_operator_input": True,
            "semantic_intent": intent_text,
            "semantic_intent_hash": intent_hash,
            "semantic_correctness_verified": False,
            "governance_authority": False,
            "autonomous_continuation_authorized": False,
            "native_messaging_called": False,
            "provider_invoked": False,
        },
    )
    artifact["semantic_intent"] = intent_text
    artifact["authority_boundary"]["semantic_correctness_verified"] = False
    artifact["authority_boundary"]["autonomous_continuation_authorized"] = False
    artifact["validation_status"] = STRUCTURAL_CANDIDATE_ONLY
    artifact["hashes"]["artifact_hash"] = artifact_hash_for(artifact)
    return artifact


__all__ = [
    "ACCEPTED_AS_SEMANTIC_INPUT",
    "ARTIFACT_TYPE",
    "AUTHORITY_BOUNDARY",
    "BOUNDARY_STATEMENT",
    "SCHEMA_VERSION",
    "SOURCE",
    "STRUCTURAL_CANDIDATE_ONLY",
    "artifact_hash_for",
    "artifact_hash_input",
    "create_chatgpt_ingress_artifact",
    "generate_valid_chatgpt_ingress_artifact",
    "hash_text",
    "replay_identity_for",
]
