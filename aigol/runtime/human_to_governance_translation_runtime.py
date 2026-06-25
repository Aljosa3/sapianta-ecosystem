"""Deterministic Human -> Governance translation runtime."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.universal_translation_artifact_schema import (
    GOVERNANCE_ONLY,
    HIGH,
    HUMAN_TO_GOVERNANCE,
    LOW,
    MATERIAL_AMBIGUITY,
    MEDIUM,
    NO_AMBIGUITY,
    UNSAFE_AMBIGUITY,
    create_universal_translation_artifact,
    validate_universal_translation_artifact,
)


RUNTIME_VERSION = "HUMAN_TO_GOVERNANCE_TRANSLATION_RUNTIME_V1"
REPLAY_STEP = "human_to_governance_translation_recorded"

CREATE_ACTION = "CREATE"
UPDATE_ACTION = "UPDATE"
IMPLEMENT_ACTION = "IMPLEMENT"
REVIEW_ACTION = "REVIEW"
UNKNOWN_ACTION = "UNKNOWN_ACTION"

DOMAIN_DEVELOPMENT = "DEVELOPMENT"
DOMAIN_SECURITY = "SECURITY"
DOMAIN_COMPLIANCE = "COMPLIANCE"
DOMAIN_GOVERNANCE = "GOVERNANCE"
DOMAIN_UNKNOWN = "UNKNOWN_DOMAIN"

ARTIFACT_RE = re.compile(r"\b[A-Z][A-Z0-9]+(?:_[A-Z0-9]+)+_V\d+\b")
PATH_RE = re.compile(r"\b(?:docs|aigol|tests|runtime|sapianta_bridge)/[A-Za-z0-9_./-]+\b")


def translate_human_to_governance(
    *,
    translation_request_id: str,
    human_request: str,
    created_at: str,
    replay_dir: str | Path,
    session_context: dict[str, Any] | None = None,
    operator_context: str = "HUMAN_OPERATOR",
    available_products: list[str] | None = None,
    available_domains: list[str] | None = None,
    available_workflows: list[str] | None = None,
) -> dict[str, Any]:
    """Translate a natural-language request into a governance intent artifact."""

    replay_path = Path(replay_dir)
    request = _require_string(human_request, "human_request")
    normalized = _normalize_request(request)
    action = _detect_action(normalized)
    domain = _detect_domain(normalized)
    entities = _extract_entities(request)
    ambiguity = _detect_ambiguity(
        normalized=normalized,
        action=action,
        domain=domain,
        entities=entities,
    )
    confidence = _confidence_for(ambiguity["ambiguity_status"], action, domain)
    intent_family = _intent_family(action, domain)
    workflow_candidate = _workflow_candidate(action, domain)
    normalized_intent = {
        "normalized_text": normalized,
        "intent_family": intent_family,
        "requested_actions": [] if action == UNKNOWN_ACTION else [action],
        "domain_candidate": domain,
        "entities": deepcopy(entities),
        "confidence": confidence,
        "translation_runtime": RUNTIME_VERSION,
    }
    governance_payload = {
        "governance_intent_status": "TRANSLATION_CANDIDATE",
        "domain_candidate": domain,
        "workflow_candidate": workflow_candidate,
        "intent_family": intent_family,
        "requested_actions": [] if action == UNKNOWN_ACTION else [action],
        "approval_required": action in {CREATE_ACTION, UPDATE_ACTION, IMPLEMENT_ACTION},
        "execution_requested": action in {CREATE_ACTION, UPDATE_ACTION, IMPLEMENT_ACTION},
        "provider_relevance": "NOT_REQUIRED",
        "worker_relevance": "POSSIBLE_AFTER_APPROVAL" if action in {CREATE_ACTION, UPDATE_ACTION, IMPLEMENT_ACTION} else "NONE",
        "entities": deepcopy(entities),
        "clarification_required": ambiguity["clarification_required"],
        "clarification_questions": list(ambiguity["clarification_questions"]),
        "authority_granted": False,
        "provider_invoked": False,
        "workflow_executed": False,
        "governance_mutated": False,
    }
    artifact = create_universal_translation_artifact(
        translation_id=f"{translation_request_id}:HUMAN-TO-GOVERNANCE",
        translation_request={
            "translation_request_id": _require_string(translation_request_id, "translation_request_id"),
            "operator_context": _require_string(operator_context, "operator_context"),
            "available_products": _string_list(available_products),
            "available_domains": _string_list(available_domains),
            "available_workflows": _string_list(available_workflows),
            "created_at": _require_string(created_at, "created_at"),
        },
        source_direction=HUMAN_TO_GOVERNANCE,
        source_payload={
            "human_request": request,
            "human_request_hash": replay_hash(request),
            "session_context": _mapping_or_empty(session_context, "session_context"),
        },
        normalized_intent=normalized_intent,
        translated_governance_payload=governance_payload,
        ambiguity_flags=ambiguity,
        confidence=confidence,
        provider_metadata={
            "provider_used": False,
            "provider_count": 0,
            "providers": [],
            "comparison_used": False,
        },
        deterministic_fallback_status={
            "fallback_used": True,
            "fallback_reason": "DETERMINISTIC_TRANSLATION_RUNTIME",
            "deterministic_rule_ids": _rule_ids_for(action, domain, ambiguity["ambiguity_status"]),
        },
        replay_reference=str(replay_path),
        created_at=created_at,
    )
    wrapper = {
        "replay_index": 0,
        "replay_step": REPLAY_STEP,
        "event_type": RUNTIME_VERSION,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"000_{REPLAY_STEP}.json", wrapper)
    return {
        "runtime_version": RUNTIME_VERSION,
        "translation_status": "TRANSLATED",
        "translation_artifact": deepcopy(artifact),
        "translation_replay_reference": str(replay_path),
        "governance_intent_candidate": deepcopy(governance_payload),
        "normalized_intent": deepcopy(normalized_intent),
        "ambiguity_flags": deepcopy(ambiguity),
        "confidence": confidence,
        "provider_invoked": False,
        "workflow_executed": False,
        "governance_mutated": False,
        "replay_visible": True,
    }


def reconstruct_human_to_governance_translation_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct deterministic Human -> Governance translation replay evidence."""

    replay_path = Path(replay_dir)
    wrapper = load_json(replay_path / f"000_{REPLAY_STEP}.json")
    if wrapper.get("replay_index") != 0 or wrapper.get("replay_step") != REPLAY_STEP:
        raise FailClosedRuntimeError("human-to-governance translation replay ordering mismatch")
    _verify_wrapper_hash(wrapper)
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("human-to-governance translation artifact must be a JSON object")
    validated = validate_universal_translation_artifact(artifact)
    if validated["source_direction"] != HUMAN_TO_GOVERNANCE:
        raise FailClosedRuntimeError("human-to-governance translation replay direction mismatch")
    payload = validated["translated_governance_payload"]
    return {
        "runtime_version": RUNTIME_VERSION,
        "translation_id": validated["translation_id"],
        "translation_artifact": deepcopy(validated),
        "governance_intent_candidate": deepcopy(payload),
        "normalized_intent": deepcopy(validated["normalized_intent"]),
        "ambiguity_flags": deepcopy(validated["ambiguity_flags"]),
        "confidence": validated["confidence"],
        "artifact_hash": validated["artifact_hash"],
        "replay_hash": wrapper["replay_hash"],
        "provider_invoked": False,
        "workflow_executed": False,
        "governance_mutated": False,
        "replay_visible": True,
    }


def _normalize_request(value: str) -> str:
    return " ".join(value.strip().lower().split())


def _detect_action(normalized: str) -> str:
    if any(_contains_term(normalized, term) for term in ("create", "add", "draft", "write", "generate")):
        return CREATE_ACTION
    if any(_contains_term(normalized, term) for term in ("update", "modify", "change", "revise")):
        return UPDATE_ACTION
    if any(_contains_term(normalized, term) for term in ("implement", "build", "fix")):
        return IMPLEMENT_ACTION
    if any(_contains_term(normalized, term) for term in ("review", "inspect", "audit", "explain")):
        return REVIEW_ACTION
    return UNKNOWN_ACTION


def _detect_domain(normalized: str) -> str:
    if any(_contains_term(normalized, term) for term in ("security", "incident", "threat", "vulnerability")):
        return DOMAIN_SECURITY
    if any(_contains_term(normalized, term) for term in ("compliance", "control", "audit", "regulation")):
        return DOMAIN_COMPLIANCE
    if any(_contains_term(normalized, term) for term in ("governance", "artifact", "workflow")):
        return DOMAIN_GOVERNANCE
    if any(_contains_term(normalized, term) for term in ("replay", "validation", "worker", "runtime", "implementation")):
        return DOMAIN_DEVELOPMENT
    return DOMAIN_UNKNOWN


def _extract_entities(human_request: str) -> dict[str, Any]:
    return {
        "artifact_identifiers": sorted(set(ARTIFACT_RE.findall(human_request))),
        "target_paths": sorted(set(PATH_RE.findall(human_request))),
    }


def _detect_ambiguity(
    *,
    normalized: str,
    action: str,
    domain: str,
    entities: dict[str, Any],
) -> dict[str, Any]:
    questions: list[str] = []
    status = NO_AMBIGUITY
    if any(phrase in normalized for phrase in ("skip approval", "bypass approval", "without approval")):
        return {
            "ambiguity_status": UNSAFE_AMBIGUITY,
            "clarification_required": True,
            "clarification_questions": ["Approval cannot be bypassed. Restate the request without bypassing approval."],
        }
    if action == UNKNOWN_ACTION:
        status = MATERIAL_AMBIGUITY
        questions.append("What action should ACLI take?")
    if domain == DOMAIN_UNKNOWN:
        status = MATERIAL_AMBIGUITY
        questions.append("Which domain should this request use?")
    if action in {CREATE_ACTION, UPDATE_ACTION} and not entities["artifact_identifiers"] and not entities["target_paths"]:
        status = MATERIAL_AMBIGUITY
        questions.append("Which artifact or target path should ACLI use?")
    return {
        "ambiguity_status": status,
        "clarification_required": status != NO_AMBIGUITY,
        "clarification_questions": questions,
    }


def _confidence_for(ambiguity_status: str, action: str, domain: str) -> str:
    if ambiguity_status == UNSAFE_AMBIGUITY:
        return LOW
    if ambiguity_status == MATERIAL_AMBIGUITY:
        return LOW
    if action != UNKNOWN_ACTION and domain != DOMAIN_UNKNOWN:
        return HIGH
    return MEDIUM


def _intent_family(action: str, domain: str) -> str:
    if action == UNKNOWN_ACTION or domain == DOMAIN_UNKNOWN:
        return "CLARIFICATION_REQUIRED"
    return f"{domain}_{action}_INTENT"


def _workflow_candidate(action: str, domain: str) -> str:
    if action == UNKNOWN_ACTION or domain == DOMAIN_UNKNOWN:
        return "HUMAN_INTENT_CLARIFICATION_INTAKE"
    if domain in {DOMAIN_DEVELOPMENT, DOMAIN_GOVERNANCE}:
        return "GOVERNED_DEVELOPMENT_WORKFLOW"
    return f"{domain}_GOVERNED_WORKFLOW"


def _rule_ids_for(action: str, domain: str, ambiguity_status: str) -> list[str]:
    rule_ids = ["NORMALIZE_TEXT_V1", "DETERMINISTIC_ACTION_DETECTION_V1", "DETERMINISTIC_DOMAIN_DETECTION_V1"]
    if action != UNKNOWN_ACTION:
        rule_ids.append(f"ACTION_{action}_V1")
    if domain != DOMAIN_UNKNOWN:
        rule_ids.append(f"DOMAIN_{domain}_V1")
    if ambiguity_status != NO_AMBIGUITY:
        rule_ids.append(f"AMBIGUITY_{ambiguity_status}_V1")
    return rule_ids


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash", None)
    if not isinstance(actual, str) or replay_hash(expected) != actual:
        raise FailClosedRuntimeError("human-to-governance translation replay hash mismatch")


def _contains_term(normalized: str, term: str) -> bool:
    return re.search(rf"\b{re.escape(term)}\b", normalized) is not None


def _string_list(values: list[str] | None) -> list[str]:
    if values is None:
        return []
    if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
        raise FailClosedRuntimeError("translation context lists must contain strings")
    return [item.strip() for item in values if item.strip()]


def _mapping_or_empty(value: dict[str, Any] | None, field_name: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"{field_name} must be a JSON object")
    return deepcopy(value)


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()
