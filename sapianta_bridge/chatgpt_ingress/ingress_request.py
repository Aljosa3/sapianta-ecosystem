"""ChatGPT ingress request model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .ingress_session import IngressSession, stable_hash


@dataclass(frozen=True)
class IngressRequest:
    session: dict[str, Any]
    original_natural_language: str
    normalized_request: str
    semantic_metadata: dict[str, Any]
    governance_classification_refs: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "session": self.session,
            "original_natural_language": self.original_natural_language,
            "normalized_request": self.normalized_request,
            "semantic_metadata": self.semantic_metadata,
            "governance_classification_refs": self.governance_classification_refs,
            "original_text_sha256": stable_hash({"text": self.original_natural_language}),
            "hidden_prompt_rewrite": False,
            "execution_authority_granted": False,
        }


def create_ingress_request(
    *,
    session: IngressSession | dict[str, Any],
    raw_text: str,
) -> IngressRequest:
    session_value = session.to_dict() if isinstance(session, IngressSession) else session
    return IngressRequest(
        session=session_value,
        original_natural_language=raw_text,
        normalized_request=" ".join(raw_text.strip().split()),
        semantic_metadata={
            "source": "CHATGPT_INTERACTION",
            "semantic_request_hash": stable_hash({"text": raw_text}),
        },
        governance_classification_refs={
            "intent_rules": "INTENT_CLASSIFICATION_RULES.json",
            "admissibility_rules": "ADMISSIBILITY_RULES.json",
            "authority_rules": "AUTHORITY_MAPPING_RULES.json",
            "workspace_rules": "WORKSPACE_MAPPING_RULES.json",
        },
    )


def validate_ingress_request(request: Any) -> dict[str, Any]:
    value = request.to_dict() if isinstance(request, IngressRequest) else request
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "ingress_request", "reason": "request must be an object"}]}
    for field in ("original_natural_language", "normalized_request"):
        if not isinstance(value.get(field), str) or not value.get(field, "").strip():
            errors.append({"field": field, "reason": "request text field must be non-empty"})
    if value.get("hidden_prompt_rewrite") is not False:
        errors.append({"field": "hidden_prompt_rewrite", "reason": "hidden prompt rewriting is forbidden"})
    if value.get("execution_authority_granted") is not False:
        errors.append({"field": "execution_authority_granted", "reason": "ingress cannot grant execution authority"})
    expected_hash = stable_hash({"text": value.get("original_natural_language", "")})
    if value.get("original_text_sha256") not in (None, expected_hash):
        errors.append({"field": "original_text_sha256", "reason": "original text hash mismatch"})
    if not isinstance(value.get("session"), dict):
        errors.append({"field": "session", "reason": "session must be embedded"})
    return {"valid": not errors, "errors": errors, "replay_safe": not errors}
