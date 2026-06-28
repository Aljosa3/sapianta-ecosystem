"""Deterministic human execution-intent detection helpers."""

from __future__ import annotations

import re
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


GENERIC_GOVERNED_DOMAIN_CREATION = "GENERIC_GOVERNED_DOMAIN_CREATION"
GENERIC_GOVERNED_ARTIFACT_CREATION = "GENERIC_GOVERNED_ARTIFACT_CREATION"
GENERIC_GOVERNED_EXECUTION_REQUEST = "GENERIC_GOVERNED_EXECUTION_REQUEST"
NO_EXECUTION_INTENT = "NO_EXECUTION_INTENT"
PLATFORM_SEMANTIC_GAP_CLOSURE_G2_05_EXECUTION_INTENT_AND_AUTHORIZATION_ENTRY_SEMANTICS_V1 = (
    "PLATFORM_SEMANTIC_GAP_CLOSURE_G2_05_EXECUTION_INTENT_AND_AUTHORIZATION_ENTRY_SEMANTICS_V1"
)
EXECUTION_INTENT_SEMANTIC_COMPARISON_ARTIFACT_V1 = "EXECUTION_INTENT_SEMANTIC_COMPARISON_ARTIFACT_V1"

_CREATION_TERMS = ("create", "new", "add", "build", "make", "define", "draft", "prepare", "write", "generate")
_NAMING_MARKERS = ("called", "named")
_EXECUTION_TERMS = ("execute", "run", "trigger", "start", "invoke", "apply")
_GOVERNANCE_ARTIFACT_TERMS = ("governed", "governance", "certification")
_ARTIFACT_KIND_TERMS = ("artifact", "doc", "document", "markdown", "specification")


def detect_human_execution_intent(
    human_prompt: str,
    *,
    canonical_semantic_capture: dict[str, Any] | None = None,
    replay_reference: str | None = None,
    detection_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Detect generic governed execution intent without granting execution authority."""

    prompt = _require_string(human_prompt, "human_prompt")
    normalized = prompt.lower().strip().rstrip(".?!")
    matched_terms: list[str] = []

    if _is_generic_governed_domain_creation(normalized):
        matched_terms = _matched_terms(normalized, (*_CREATION_TERMS, "governed", "domain", *_NAMING_MARKERS))
        return _attach_semantic_evidence(
            {
            "intent_detected": True,
            "intent_class": GENERIC_GOVERNED_DOMAIN_CREATION,
            "confidence": "HIGH",
            "target_kind": "DOMAIN",
            "target_name": _extract_named_target(prompt),
            "matched_terms": matched_terms,
            "requires_clarification": True,
            "execution_authority_granted": False,
            "routing_action": "GOVERNED_UNKNOWN_DOMAIN_CLARIFICATION",
            },
            canonical_semantic_capture=canonical_semantic_capture,
            replay_reference=replay_reference,
            detection_id=detection_id,
            created_at=created_at,
        )

    if _is_generic_governed_artifact_creation(normalized):
        matched_terms = _matched_terms(
            normalized,
            (*_CREATION_TERMS, *_GOVERNANCE_ARTIFACT_TERMS, *_ARTIFACT_KIND_TERMS, *_NAMING_MARKERS),
        )
        return _attach_semantic_evidence(
            {
            "intent_detected": True,
            "intent_class": GENERIC_GOVERNED_ARTIFACT_CREATION,
            "confidence": "MEDIUM",
            "target_kind": "ARTIFACT",
            "target_name": _extract_named_target(prompt),
            "matched_terms": matched_terms,
            "requires_clarification": True,
            "execution_authority_granted": False,
            "routing_action": "ROUTE_TO_GOVERNED_DEVELOPMENT_WORKFLOW",
            },
            canonical_semantic_capture=canonical_semantic_capture,
            replay_reference=replay_reference,
            detection_id=detection_id,
            created_at=created_at,
        )

    if _is_generic_governed_execution_request(normalized):
        matched_terms = _matched_terms(
            normalized,
            (*_EXECUTION_TERMS, "governed", "execution", "workflow", "chain"),
        )
        return _attach_semantic_evidence(
            {
            "intent_detected": True,
            "intent_class": GENERIC_GOVERNED_EXECUTION_REQUEST,
            "confidence": "MEDIUM",
            "target_kind": "EXECUTION",
            "target_name": None,
            "matched_terms": matched_terms,
            "requires_clarification": True,
            "execution_authority_granted": False,
            "routing_action": "FAIL_CLOSED_NO_CERTIFIED_GENERIC_EXECUTION_ENTRYPOINT",
            },
            canonical_semantic_capture=canonical_semantic_capture,
            replay_reference=replay_reference,
            detection_id=detection_id,
            created_at=created_at,
        )

    return _attach_semantic_evidence(
        {
        "intent_detected": False,
        "intent_class": NO_EXECUTION_INTENT,
        "confidence": "LOW",
        "target_kind": None,
        "target_name": None,
        "matched_terms": [],
        "requires_clarification": False,
        "execution_authority_granted": False,
        "routing_action": None,
        },
        canonical_semantic_capture=canonical_semantic_capture,
        replay_reference=replay_reference,
        detection_id=detection_id,
        created_at=created_at,
    )


def _attach_semantic_evidence(
    compatibility: dict[str, Any],
    *,
    canonical_semantic_capture: dict[str, Any] | None,
    replay_reference: str | None,
    detection_id: str | None,
    created_at: str | None,
) -> dict[str, Any]:
    csa = _csa_execution_intent_interpretation(canonical_semantic_capture)
    compatibility_interpretation = _compatibility_execution_intent_interpretation(compatibility)
    csa_decision = _csa_execution_intent_decision(csa)
    differences = _semantic_differences(
        compatibility_interpretation=compatibility_interpretation,
        csa_interpretation=csa,
        csa_decision=csa_decision,
    )
    if csa["available"] is not True:
        parity_status = "CSA_UNAVAILABLE"
        equivalence = "NOT_EVALUATED"
    elif differences:
        parity_status = "CSA_COMPATIBILITY_DIVERGENT"
        equivalence = "NOT_EQUIVALENT"
    else:
        parity_status = "CSA_COMPATIBILITY_EQUIVALENT"
        equivalence = "EQUIVALENT"
    comparison = {
        "artifact_type": EXECUTION_INTENT_SEMANTIC_COMPARISON_ARTIFACT_V1,
        "comparison_id": f"{detection_id or 'EXECUTION-INTENT'}:SEMANTIC-COMPARISON",
        "migration_batch_id": (
            PLATFORM_SEMANTIC_GAP_CLOSURE_G2_05_EXECUTION_INTENT_AND_AUTHORIZATION_ENTRY_SEMANTICS_V1
        ),
        "comparison_mode": "CSA_PRIMARY_WHEN_EXECUTION_INTENT_PARITY_PROVEN",
        "canonical_semantic_artifact_reference": csa["canonical_semantic_artifact_reference"],
        "canonical_semantic_artifact_hash": csa["canonical_semantic_artifact_hash"],
        "compatibility_interpretation_hash": replay_hash(compatibility_interpretation),
        "csa_interpretation_hash": replay_hash(csa),
        "compatibility_semantic_interpretation": compatibility_interpretation,
        "csa_semantic_interpretation": csa,
        "semantic_equivalence_result": equivalence,
        "semantic_differences": differences,
        "confidence_comparison": {
            "csa_confidence": csa.get("semantic_confidence"),
            "compatibility_confidence": compatibility_interpretation.get("confidence"),
            "confidence_equivalent": csa.get("semantic_confidence") == compatibility_interpretation.get("confidence"),
        },
        "parity_status": parity_status,
        "replay_lineage": {
            "replay_reference": replay_reference,
            "comparison_source": "CSA_VS_HUMAN_EXECUTION_INTENT_COMPATIBILITY_DETECTOR",
        },
        "non_authoritative_outside_certified_scope": True,
        "authorization_influence": False,
        "approval_influence": False,
        "execution_influence": False,
        "provider_selection_influence": False,
        "worker_influence": False,
        "lifecycle_influence": False,
        "created_at": created_at,
        "replay_visible": True,
        "execution_authority_granted": False,
        "approval_authority_granted": False,
        "authorization_created": False,
        "execution_requested_by_detector": False,
        "provider_invoked": False,
        "worker_invoked": False,
    }
    comparison["artifact_hash"] = replay_hash(comparison)
    parity_proven = parity_status == "CSA_COMPATIBILITY_EQUIVALENT" and compatibility["intent_class"] in {
        GENERIC_GOVERNED_ARTIFACT_CREATION,
        NO_EXECUTION_INTENT,
    }
    result = dict(compatibility)
    result.update(
        {
            "semantic_execution_intent_source": "CANONICAL_SEMANTIC_ARTIFACT"
            if parity_proven
            else "COMPATIBILITY_FALLBACK",
            "migration_batch_id": (
                PLATFORM_SEMANTIC_GAP_CLOSURE_G2_05_EXECUTION_INTENT_AND_AUTHORIZATION_ENTRY_SEMANTICS_V1
            ),
            "canonical_semantic_artifact_reference": csa["canonical_semantic_artifact_reference"],
            "canonical_semantic_artifact_hash": csa["canonical_semantic_artifact_hash"],
            "previous_compatibility_interpretation": compatibility_interpretation,
            "semantic_comparison_artifact": comparison,
            "semantic_comparison_hash": comparison["artifact_hash"],
            "semantic_equivalence_result": comparison["semantic_equivalence_result"],
            "semantic_comparison_parity_status": comparison["parity_status"],
            "semantic_parity_evidence": _parity_evidence(
                compatibility_interpretation=compatibility_interpretation,
                csa_decision=csa_decision,
                comparison=comparison,
                parity_proven=parity_proven,
            ),
            "compatibility_fallback_available": True,
            "compatibility_fallback_authoritative": not parity_proven,
        }
    )
    return result


def _compatibility_execution_intent_interpretation(compatibility: dict[str, Any]) -> dict[str, Any]:
    return {
        "source": "HUMAN_EXECUTION_INTENT_COMPATIBILITY_DETECTOR",
        "available": True,
        "intent_detected": compatibility.get("intent_detected") is True,
        "intent_class": compatibility.get("intent_class"),
        "confidence": compatibility.get("confidence"),
        "target_kind": compatibility.get("target_kind"),
        "target_name": compatibility.get("target_name"),
        "requires_clarification": compatibility.get("requires_clarification") is True,
        "execution_authority_granted": False,
        "routing_action": compatibility.get("routing_action"),
    }


def _csa_execution_intent_interpretation(canonical_semantic_capture: dict[str, Any] | None) -> dict[str, Any]:
    artifact = (
        canonical_semantic_capture.get("semantic_artifact")
        if isinstance(canonical_semantic_capture, dict)
        else None
    )
    if not isinstance(artifact, dict):
        return {
            "source": "CANONICAL_SEMANTIC_ARTIFACT",
            "available": False,
            "canonical_semantic_artifact_reference": None,
            "canonical_semantic_artifact_hash": None,
            "intent_class": None,
            "semantic_confidence": None,
            "domain": None,
            "requested_actions": [],
            "approval_required": None,
            "execution_requested": None,
            "worker_relevance": None,
            "provider_invoked": None,
            "worker_invoked": None,
            "execution_authority_granted": False,
            "authorization_created": False,
            "routing_action": None,
        }
    semantic_identity = artifact.get("semantic_identity") or {}
    confidence = artifact.get("confidence") or {}
    approval_state = artifact.get("approval_state") or {}
    execution_intent = artifact.get("execution_intent") or {}
    provider_projection = artifact.get("provider_projection") or {}
    worker_projection = artifact.get("worker_projection") or {}
    return {
        "source": "CANONICAL_SEMANTIC_ARTIFACT",
        "available": True,
        "canonical_semantic_artifact_reference": canonical_semantic_capture.get("semantic_replay_reference"),
        "canonical_semantic_artifact_hash": artifact.get("artifact_hash"),
        "intent_class": None,
        "semantic_confidence": confidence.get("semantic_confidence"),
        "domain": semantic_identity.get("domain"),
        "requested_actions": list(semantic_identity.get("requested_actions") or []),
        "approval_required": approval_state.get("approval_required") is True,
        "execution_requested": execution_intent.get("execution_requested") is True,
        "worker_relevance": execution_intent.get("worker_relevance"),
        "provider_invoked": provider_projection.get("provider_invoked") is True,
        "worker_invoked": worker_projection.get("worker_invoked") is True,
        "execution_authority_granted": False,
        "authorization_created": False,
        "routing_action": None,
    }


def _csa_execution_intent_decision(csa: dict[str, Any]) -> dict[str, Any] | None:
    if csa.get("available") is not True:
        return None
    actions = {action for action in csa.get("requested_actions", []) if isinstance(action, str)}
    if (
        csa.get("domain") == "GOVERNANCE"
        and "CREATE" in actions
        and csa.get("approval_required") is True
        and csa.get("execution_requested") is True
        and csa.get("worker_relevance") == "POSSIBLE_AFTER_APPROVAL"
    ):
        return {
            "intent_detected": True,
            "intent_class": GENERIC_GOVERNED_ARTIFACT_CREATION,
            "confidence": csa.get("semantic_confidence"),
            "target_kind": "ARTIFACT",
            "target_name": None,
            "requires_clarification": True,
            "execution_authority_granted": False,
            "routing_action": "ROUTE_TO_GOVERNED_DEVELOPMENT_WORKFLOW",
        }
    if (
        not actions
        and csa.get("approval_required") is False
        and csa.get("execution_requested") is False
        and csa.get("worker_relevance") == "NONE"
    ):
        return {
            "intent_detected": False,
            "intent_class": NO_EXECUTION_INTENT,
            "confidence": "LOW",
            "target_kind": None,
            "target_name": None,
            "requires_clarification": False,
            "execution_authority_granted": False,
            "routing_action": None,
        }
    return None


def _semantic_differences(
    *,
    compatibility_interpretation: dict[str, Any],
    csa_interpretation: dict[str, Any],
    csa_decision: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    if csa_interpretation.get("available") is not True or not isinstance(csa_decision, dict):
        return []
    differences: list[dict[str, Any]] = []
    for field in (
        "intent_detected",
        "intent_class",
        "target_kind",
        "requires_clarification",
        "execution_authority_granted",
        "routing_action",
    ):
        if compatibility_interpretation.get(field) != csa_decision.get(field):
            differences.append(
                {
                    "field": field,
                    "csa_value": csa_decision.get(field),
                    "compatibility_value": compatibility_interpretation.get(field),
                }
            )
    return differences


def _parity_evidence(
    *,
    compatibility_interpretation: dict[str, Any],
    csa_decision: dict[str, Any] | None,
    comparison: dict[str, Any],
    parity_proven: bool,
) -> dict[str, Any]:
    evidence = {
        "migration_batch_id": (
            PLATFORM_SEMANTIC_GAP_CLOSURE_G2_05_EXECUTION_INTENT_AND_AUTHORIZATION_ENTRY_SEMANTICS_V1
        ),
        "parity_status": "CSA_COMPATIBILITY_PARITY_PROVEN"
        if parity_proven
        else comparison["parity_status"],
        "parity_scope": "EXECUTION_INTENT_AND_AUTHORIZATION_ENTRY_SEMANTICS",
        "compatibility_intent_class": compatibility_interpretation.get("intent_class"),
        "csa_intent_class": csa_decision.get("intent_class") if isinstance(csa_decision, dict) else None,
        "semantic_comparison_hash": comparison["artifact_hash"],
        "execution_authority_granted": False,
        "approval_authority_granted": False,
        "authorization_created": False,
        "execution_requested_by_detector": False,
        "compatibility_fallback_authoritative": not parity_proven,
    }
    evidence["parity_hash"] = replay_hash(evidence)
    return evidence


def _is_generic_governed_domain_creation(normalized: str) -> bool:
    return (
        "domain" in normalized
        and any(term in normalized for term in _CREATION_TERMS)
        and ("governed" in normalized or any(marker in normalized for marker in _NAMING_MARKERS))
    )


def _is_generic_governed_artifact_creation(normalized: str) -> bool:
    return (
        any(subject in normalized for subject in _GOVERNANCE_ARTIFACT_TERMS)
        and any(kind in normalized for kind in _ARTIFACT_KIND_TERMS)
        and any(term in normalized for term in _CREATION_TERMS)
    )


def _is_generic_governed_execution_request(normalized: str) -> bool:
    has_execution_subject = (
        "governed execution" in normalized
        or "execution workflow" in normalized
        or "execution chain" in normalized
        or "governed workflow" in normalized
    )
    return has_execution_subject and any(term in normalized for term in _EXECUTION_TERMS)


def _extract_named_target(prompt: str) -> str | None:
    patterns = (
        r"\b(?:called|named)\s+([A-Za-z][A-Za-z0-9_-]*)\b",
        r"\bdomain\s+(?:called|named)\s+([A-Za-z][A-Za-z0-9_-]*)\b",
        r"\bartifact\s+(?:called|named)\s+([A-Za-z][A-Za-z0-9_-]*)\b",
    )
    for pattern in patterns:
        match = re.search(pattern, prompt)
        if match:
            return match.group(1)
    return None


def _matched_terms(normalized: str, terms: tuple[str, ...]) -> list[str]:
    return [term for term in terms if term in normalized]


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()
