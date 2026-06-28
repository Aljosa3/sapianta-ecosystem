"""Deterministic clarification-first intake for normal human intent."""

from __future__ import annotations

from copy import deepcopy
import re
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


HUMAN_INTENT_CLARIFICATION_INTAKE = "HUMAN_INTENT_CLARIFICATION_INTAKE"
HUMAN_INTENT_CLARIFICATION_INTAKE_ARTIFACT_V1 = "HUMAN_INTENT_CLARIFICATION_INTAKE_ARTIFACT_V1"

BUSINESS_GOAL_INTENT = "BUSINESS_GOAL_INTENT"
PROBLEM_STATEMENT_INTENT = "PROBLEM_STATEMENT_INTENT"
AUTOMATION_INTENT = "AUTOMATION_INTENT"
COMPLIANCE_INTENT = "COMPLIANCE_INTENT"
AMBIGUOUS_INTENT = "AMBIGUOUS_INTENT"
GENERAL_IMPROVEMENT_INTENT = "GENERAL_IMPROVEMENT_INTENT"
CONTINUATION_INTENT = "CONTINUATION_INTENT"
BOUNDED_FILE_WRITE_PROOF_INTENT = "BOUNDED_FILE_WRITE_PROOF_INTENT"
DEVELOPMENT_INTENT = "DEVELOPMENT_INTENT"

CREATE_DOMAIN_COMPLIANCE_CLARIFICATION_TARGET = "CREATE_DOMAIN_COMPLIANCE_CLARIFICATION"
OCS_LLM_COGNITION_TARGET = "OCS_LLM_COGNITION"
BOUNDED_FILE_WRITE_WORKER_USER_SESSION_TARGET = "BOUNDED_FILE_WRITE_WORKER_USER_SESSION"
GOVERNED_DEVELOPMENT_WORKFLOW_TARGET = "GOVERNED_DEVELOPMENT_WORKFLOW"
UBTR_CONSUMER_MIGRATION_BATCH_02_HIRR_V1 = "UBTR_CONSUMER_MIGRATION_BATCH_02_HIRR_V1"
PLATFORM_SEMANTIC_GAP_CLOSURE_G2_03_HIRR_REMAINING_INTAKE_FAMILIES_V1 = (
    "PLATFORM_SEMANTIC_GAP_CLOSURE_G2_03_HIRR_REMAINING_INTAKE_FAMILIES_V1"
)


def classify_human_intent_for_clarification_from_canonical_semantic_artifact(
    *,
    canonical_semantic_artifact: dict[str, Any],
    previous_compatibility_intake: dict[str, Any],
) -> dict[str, Any]:
    """Resolve HIRR intake from CSA only when compatibility parity is deterministic."""

    artifact = _require_mapping(canonical_semantic_artifact, "canonical_semantic_artifact")
    compatibility = _require_mapping(previous_compatibility_intake, "previous_compatibility_intake")
    if _csa_supports_ambiguous_hirr_intake(artifact):
        if not _compatibility_supports_ambiguous_hirr_intake(compatibility):
            return _csa_no_match("COMPATIBILITY_HIRR_PARITY_NOT_SUPPORTED")
        migration_batch_id = UBTR_CONSUMER_MIGRATION_BATCH_02_HIRR_V1
        parity_evidence = _hirr_parity_evidence(
            artifact,
            compatibility,
            migration_batch_id=migration_batch_id,
            parity_scope="AMBIGUOUS_INTENT_CLARIFICATION_INTAKE",
        )
    elif _csa_supports_remaining_hirr_intake_family(artifact):
        if not _compatibility_supports_remaining_hirr_intake_family(artifact, compatibility):
            return _csa_no_match("COMPATIBILITY_HIRR_REMAINING_FAMILY_PARITY_NOT_SUPPORTED")
        migration_batch_id = PLATFORM_SEMANTIC_GAP_CLOSURE_G2_03_HIRR_REMAINING_INTAKE_FAMILIES_V1
        parity_evidence = _hirr_parity_evidence(
            artifact,
            compatibility,
            migration_batch_id=migration_batch_id,
            parity_scope="HIRR_REMAINING_INTAKE_FAMILY",
        )
    else:
        return _csa_no_match("CSA_HIRR_PARITY_NOT_SUPPORTED")
    intake = deepcopy(compatibility)
    intake.update(
        {
            "semantic_routing_source": "CANONICAL_SEMANTIC_ARTIFACT",
            "routing_source": "CANONICAL_SEMANTIC_ARTIFACT",
            "migration_batch_id": migration_batch_id,
            "canonical_semantic_artifact_reference": artifact["replay_identity"]["semantic_replay_reference"],
            "canonical_semantic_artifact_hash": artifact["artifact_hash"],
            "previous_compatibility_interpretation": _compatibility_interpretation(compatibility),
            "semantic_parity_evidence": parity_evidence,
            "semantic_authority": True,
        }
    )
    return intake


def classify_development_intent_for_governed_routing(human_prompt: str) -> dict[str, Any]:
    """Resolve concrete development intents for governed development workflow routing."""

    prompt = _require_string(human_prompt, "human_prompt")
    normalized = prompt.lower().strip().rstrip(".?!")
    result = _development_intent(normalized)
    if result is None:
        return {
            "artifact_type": HUMAN_INTENT_CLARIFICATION_INTAKE_ARTIFACT_V1,
            "intake_matched": False,
            "workflow_id": None,
            "intent_family": None,
            "intent_confidence": "NONE",
            "intent_signals": [],
            "clarification_required": False,
            "clarification_questions": [],
            "expected_workflow_targets": [],
            "routing_decision": "DEVELOPMENT_INTENT_NO_MATCH_CONTINUE_TO_EXISTING_ROUTER",
            "provider_invoked": False,
            "worker_invoked": False,
            "authorization_created": False,
            "execution_requested": False,
            "approval_bypassed": False,
            "governance_mutated": False,
            "replay_mutated": False,
            "failure_reason": None,
        }
    return {
        "artifact_type": HUMAN_INTENT_CLARIFICATION_INTAKE_ARTIFACT_V1,
        "intake_matched": True,
        "workflow_id": GOVERNED_DEVELOPMENT_WORKFLOW_TARGET,
        "intent_family": DEVELOPMENT_INTENT,
        "intent_confidence": result["confidence"],
        "intent_signals": result["signals"],
        "clarification_required": False,
        "clarification_questions": [],
        "expected_workflow_targets": [GOVERNED_DEVELOPMENT_WORKFLOW_TARGET],
        "routing_decision": "DEVELOPMENT_INTENT_RESOLVED_TO_GOVERNED_DEVELOPMENT_WORKFLOW",
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_bypassed": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "failure_reason": None,
    }


def classify_human_intent_for_clarification(human_prompt: str, *, include_unknown: bool = True) -> dict[str, Any]:
    """Classify normal human intent into deterministic clarification-first families."""

    prompt = _require_string(human_prompt, "human_prompt")
    normalized = prompt.lower().strip().rstrip(".?!")
    checks = (
        _continuation_intent,
        _bounded_file_write_proof_intent,
        _general_improvement_intent,
        _compliance_intent,
        _automation_intent,
        _problem_statement_intent,
        _business_goal_intent,
        _ambiguous_intent,
    )
    for check in checks:
        result = check(normalized)
        if result is not None:
            return _intake_result(
                intent_family=result["intent_family"],
                confidence=result["confidence"],
                signals=result["signals"],
            )
    if include_unknown:
        return _intake_result(
            intent_family=AMBIGUOUS_INTENT,
            confidence="LOW",
            signals=["unknown-human-intent"],
        )
    return {
        "artifact_type": HUMAN_INTENT_CLARIFICATION_INTAKE_ARTIFACT_V1,
        "intake_matched": False,
        "workflow_id": None,
        "intent_family": None,
        "intent_confidence": "NONE",
        "intent_signals": [],
        "clarification_required": False,
        "clarification_questions": [],
        "expected_workflow_targets": [],
        "routing_decision": "HUMAN_INTENT_NO_MATCH_CONTINUE_TO_EXISTING_ROUTER",
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_bypassed": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "failure_reason": None,
    }


def _csa_no_match(reason: str) -> dict[str, Any]:
    return {
        "artifact_type": HUMAN_INTENT_CLARIFICATION_INTAKE_ARTIFACT_V1,
        "intake_matched": False,
        "workflow_id": None,
        "intent_family": None,
        "intent_confidence": "NONE",
        "intent_signals": [],
        "clarification_required": False,
        "clarification_questions": [],
        "expected_workflow_targets": [],
        "routing_decision": "CSA_HIRR_INTAKE_NO_MATCH_CONTINUE_TO_COMPATIBILITY",
        "semantic_routing_source": "COMPATIBILITY_FALLBACK",
        "migration_batch_id": None,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_bypassed": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "failure_reason": reason,
    }


def _csa_supports_ambiguous_hirr_intake(artifact: dict[str, Any]) -> bool:
    workflow_identity = _require_mapping(artifact.get("workflow_identity"), "workflow_identity")
    semantic_identity = _require_mapping(artifact.get("semantic_identity"), "semantic_identity")
    clarification_state = _require_mapping(artifact.get("clarification_state"), "clarification_state")
    ambiguity = _require_mapping(artifact.get("ambiguity"), "ambiguity")
    confidence = _require_mapping(artifact.get("confidence"), "confidence")
    replay_identity = _require_mapping(artifact.get("replay_identity"), "replay_identity")
    _require_string(artifact.get("artifact_hash"), "artifact_hash")
    _require_string(replay_identity.get("semantic_replay_reference"), "semantic_replay_reference")
    return (
        workflow_identity.get("workflow_id") == HUMAN_INTENT_CLARIFICATION_INTAKE
        and semantic_identity.get("intent_family") == "CLARIFICATION_REQUIRED"
        and semantic_identity.get("domain") == "UNKNOWN_DOMAIN"
        and semantic_identity.get("requested_actions") == []
        and clarification_state.get("clarification_required") is True
        and ambiguity.get("ambiguity_status") == "MATERIAL_AMBIGUITY"
        and confidence.get("semantic_confidence") == "LOW"
    )


def _compatibility_supports_ambiguous_hirr_intake(intake: dict[str, Any]) -> bool:
    return (
        intake.get("artifact_type") == HUMAN_INTENT_CLARIFICATION_INTAKE_ARTIFACT_V1
        and intake.get("intake_matched") is True
        and intake.get("workflow_id") == HUMAN_INTENT_CLARIFICATION_INTAKE
        and intake.get("intent_family") == AMBIGUOUS_INTENT
        and intake.get("intent_confidence") == "LOW"
        and intake.get("clarification_required") is True
        and intake.get("routing_decision") == "HUMAN_INTENT_CLARIFICATION_REQUIRED"
    )


def _csa_supports_remaining_hirr_intake_family(artifact: dict[str, Any]) -> bool:
    workflow_identity = _require_mapping(artifact.get("workflow_identity"), "workflow_identity")
    semantic_identity = _require_mapping(artifact.get("semantic_identity"), "semantic_identity")
    clarification_state = _require_mapping(artifact.get("clarification_state"), "clarification_state")
    ambiguity = _require_mapping(artifact.get("ambiguity"), "ambiguity")
    confidence = _require_mapping(artifact.get("confidence"), "confidence")
    replay_identity = _require_mapping(artifact.get("replay_identity"), "replay_identity")
    _require_string(artifact.get("artifact_hash"), "artifact_hash")
    _require_string(replay_identity.get("semantic_replay_reference"), "semantic_replay_reference")
    intent_family = semantic_identity.get("intent_family")
    return (
        workflow_identity.get("workflow_id") == HUMAN_INTENT_CLARIFICATION_INTAKE
        and intent_family in _remaining_hirr_intake_families()
        and semantic_identity.get("domain") == "UNKNOWN_DOMAIN"
        and semantic_identity.get("requested_actions") == []
        and clarification_state.get("clarification_required") is True
        and ambiguity.get("ambiguity_status") == "MATERIAL_AMBIGUITY"
        and confidence.get("semantic_confidence") in {"LOW", "MEDIUM"}
    )


def _compatibility_supports_remaining_hirr_intake_family(
    artifact: dict[str, Any],
    intake: dict[str, Any],
) -> bool:
    csa_family = artifact["semantic_identity"]["intent_family"]
    csa_confidence = artifact["confidence"]["semantic_confidence"]
    return (
        intake.get("artifact_type") == HUMAN_INTENT_CLARIFICATION_INTAKE_ARTIFACT_V1
        and intake.get("intake_matched") is True
        and intake.get("workflow_id") == HUMAN_INTENT_CLARIFICATION_INTAKE
        and intake.get("intent_family") == csa_family
        and intake.get("intent_family") in _remaining_hirr_intake_families()
        and intake.get("intent_confidence") == csa_confidence
        and intake.get("clarification_required") is True
        and intake.get("routing_decision") == "HUMAN_INTENT_CLARIFICATION_REQUIRED"
    )


def _remaining_hirr_intake_families() -> set[str]:
    return {
        BUSINESS_GOAL_INTENT,
        PROBLEM_STATEMENT_INTENT,
        AUTOMATION_INTENT,
        COMPLIANCE_INTENT,
        GENERAL_IMPROVEMENT_INTENT,
        CONTINUATION_INTENT,
        BOUNDED_FILE_WRITE_PROOF_INTENT,
    }


def _compatibility_interpretation(intake: dict[str, Any]) -> dict[str, Any]:
    return {
        "source": "LOCAL_HIRR_COMPATIBILITY_MARKERS",
        "workflow_id": intake.get("workflow_id"),
        "intent_family": intake.get("intent_family"),
        "intent_confidence": intake.get("intent_confidence"),
        "intent_signals": list(intake.get("intent_signals") or []),
        "clarification_required": intake.get("clarification_required") is True,
        "expected_workflow_targets": list(intake.get("expected_workflow_targets") or []),
        "routing_decision": intake.get("routing_decision"),
    }


def _hirr_parity_evidence(
    artifact: dict[str, Any],
    intake: dict[str, Any],
    *,
    migration_batch_id: str,
    parity_scope: str,
) -> dict[str, Any]:
    evidence = {
        "migration_batch_id": migration_batch_id,
        "parity_status": "CSA_COMPATIBILITY_PARITY_PROVEN",
        "parity_scope": parity_scope,
        "csa_workflow_id": artifact["workflow_identity"]["workflow_id"],
        "csa_intent_family": artifact["semantic_identity"]["intent_family"],
        "csa_clarification_required": artifact["clarification_state"]["clarification_required"] is True,
        "csa_ambiguity_status": artifact["ambiguity"]["ambiguity_status"],
        "csa_semantic_confidence": artifact["confidence"]["semantic_confidence"],
        "compatibility_workflow_id": intake.get("workflow_id"),
        "compatibility_intent_family": intake.get("intent_family"),
        "compatibility_clarification_required": intake.get("clarification_required") is True,
        "compatibility_confidence": intake.get("intent_confidence"),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_bypassed": False,
    }
    evidence["parity_hash"] = replay_hash(evidence)
    return evidence


def _intake_result(*, intent_family: str, confidence: str, signals: list[str]) -> dict[str, Any]:
    expected_targets = _expected_workflow_targets(intent_family)
    return {
        "artifact_type": HUMAN_INTENT_CLARIFICATION_INTAKE_ARTIFACT_V1,
        "intake_matched": True,
        "workflow_id": HUMAN_INTENT_CLARIFICATION_INTAKE,
        "intent_family": intent_family,
        "intent_confidence": confidence,
        "intent_signals": list(signals),
        "clarification_required": True,
        "clarification_questions": _clarification_questions(intent_family),
        "expected_workflow_targets": expected_targets,
        "routing_decision": "HUMAN_INTENT_CLARIFICATION_REQUIRED",
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_bypassed": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "failure_reason": None,
    }


def _business_goal_intent(normalized: str) -> dict[str, Any] | None:
    signals = _matched_terms(
        normalized,
        (
            "build a tool",
            "build a system",
            "start using ai",
            "start a project",
            "internal service",
            "trust ai",
            "ai recommendations",
            "ai decisions",
            "ai suggestions",
            "zgraditi sistem",
            "kakovost",
            "skladnost",
        ),
    )
    if len(signals) >= 2 or (_has_word(normalized, "ai") and any(term in normalized for term in ("trust", "safe", "quality"))):
        return {"intent_family": BUSINESS_GOAL_INTENT, "confidence": "MEDIUM", "signals": signals or ["ai-goal"]}
    return None


def _general_improvement_intent(normalized: str) -> dict[str, Any] | None:
    if _has_workflow_or_control_signals(normalized):
        return None
    ai_scoped_signals = _matched_terms(
        normalized,
        (
            "improve how",
            "processes safer",
            "improve trust",
            "suggest how",
            "reduce risk",
            "where should we start",
            "first step",
            "plan a better",
            "recommend improvements",
            "easier to explain",
        ),
    )
    standalone_advisory_signals = _matched_terms(
        normalized,
        (
            "kaj bi bilo najbolje",
            "kaj je najbolje",
            "najbolje narediti naprej",
            "kaj naj naredim naprej",
            "naslednji korak",
            "najboljsi naslednji korak",
            "najboljši naslednji korak",
            "izboljsal sistem",
            "izboljšal sistem",
        ),
    )
    if standalone_advisory_signals:
        return {
            "intent_family": GENERAL_IMPROVEMENT_INTENT,
            "confidence": "MEDIUM",
            "signals": standalone_advisory_signals,
        }
    if ai_scoped_signals and _has_word(normalized, "ai"):
        return {"intent_family": GENERAL_IMPROVEMENT_INTENT, "confidence": "MEDIUM", "signals": ai_scoped_signals}
    return None


def _continuation_intent(normalized: str) -> dict[str, Any] | None:
    continuation_terms = (
        "nadaljuj",
        "continue",
        "continue this",
        "continue the project",
        "go on",
        "resume",
        "proceed",
    )
    signals = [term for term in continuation_terms if normalized == term]
    if not signals and normalized in {"continue project", "resume the project", "resume project"}:
        signals = [normalized]
    if signals:
        return {"intent_family": CONTINUATION_INTENT, "confidence": "LOW", "signals": signals}
    return None


def _bounded_file_write_proof_intent(normalized: str) -> dict[str, Any] | None:
    signals = _matched_terms(
        normalized,
        (
            "proof note",
            "evidence note",
            "evidence file",
            "proof file",
            "majhno datoteko",
            "majhna datoteka",
            "malo datoteko",
            "dokaz",
            "dokazni zapis",
            "tekstovno datoteko",
            "write a small proof",
            "create a small proof",
            "make a small proof",
            "create a tiny proof",
            "did something safely",
            "system really did something safely",
        ),
    )
    if signals:
        return {"intent_family": BOUNDED_FILE_WRITE_PROOF_INTENT, "confidence": "MEDIUM", "signals": signals}
    return None


def _problem_statement_intent(normalized: str) -> dict[str, Any] | None:
    signals = _matched_terms(
        normalized,
        (
            "contradict",
            "inconsistent",
            "cannot explain",
            "do not know",
            "risky ai",
            "hard to compare",
            "without review",
            "miss problems",
            "unreliable",
            "quality problem",
        ),
    )
    if signals and (_has_word(normalized, "ai") or _has_word(normalized, "automated") or _has_word(normalized, "chatbot")):
        return {"intent_family": PROBLEM_STATEMENT_INTENT, "confidence": "MEDIUM", "signals": signals}
    return None


def _automation_intent(normalized: str) -> dict[str, Any] | None:
    signals = _matched_terms(
        normalized,
        (
            "automate",
            "automated check",
            "flag",
            "workflow that reviews",
            "screen",
            "collect evidence",
            "missing justification",
            "stops bad",
        ),
    )
    if signals and (_has_word(normalized, "ai") or _has_word(normalized, "model")):
        return {"intent_family": AUTOMATION_INTENT, "confidence": "MEDIUM", "signals": signals}
    return None


def _compliance_intent(normalized: str) -> dict[str, Any] | None:
    signals = _matched_terms(
        normalized,
        (
            "auditor",
            "auditors",
            "audit",
            "regulator",
            "regulators",
            "proof",
            "prove",
            "records",
            "company rules",
            "internal rules",
            "controlled",
            "compliance",
            "skladnost",
        ),
    )
    if signals and (
        _has_word(normalized, "ai")
        or _has_word(normalized, "decision")
        or _has_word(normalized, "decisions")
        or _has_word(normalized, "output")
        or _has_word(normalized, "outputs")
    ):
        return {"intent_family": COMPLIANCE_INTENT, "confidence": "MEDIUM", "signals": signals}
    return None


def _ambiguous_intent(normalized: str) -> dict[str, Any] | None:
    ambiguous_phrases = (
        "i need help with ai",
        "build something for my business",
        "we need better decisions",
        "make this safer",
        "help us get started",
        "intelligent system",
        "improve our process",
        "what should we do next",
        "system that checks things",
        "help me improve the system",
        "build something useful for my company",
        "make the platform better",
    )
    signals = _matched_terms(normalized, ambiguous_phrases)
    if signals:
        return {"intent_family": AMBIGUOUS_INTENT, "confidence": "LOW", "signals": signals}
    return None


def _development_intent(normalized: str) -> dict[str, Any] | None:
    action_signals = _matched_terms(normalized, ("add", "implement", "create", "build", "update", "extend"))
    if not action_signals:
        return None
    development_subjects = (
        ("replay", "validation"),
        ("replay", "validator"),
        ("replay", "evidence"),
        ("worker", "authorization"),
        ("worker", "auth"),
        ("comparison", "runtime"),
        ("audit", "export"),
        ("governance", "artifact"),
        ("certification", "artifact"),
        ("runtime", "wiring"),
        ("execution", "bridge"),
        ("validation", "runner"),
        ("approval", "capture"),
        ("proposal", "generation"),
        ("repository", "mutation"),
    )
    signals: list[str] = []
    for required_terms in development_subjects:
        if all(_contains_term(normalized, term) for term in required_terms):
            signals.extend(action_signals)
            signals.extend(required_terms)
            return {
                "intent_family": DEVELOPMENT_INTENT,
                "confidence": "HIGH",
                "signals": sorted(set(signals)),
            }
    return None


def _clarification_questions(intent_family: str) -> list[str]:
    questions = {
        BUSINESS_GOAL_INTENT: [
            "What kind of AI output or decision should be reviewed first?",
            "Who is affected by the decision?",
            "Is the immediate goal planning, evidence design, or a governed implementation request?",
        ],
        PROBLEM_STATEMENT_INTENT: [
            "What problem should the first governed workflow address?",
            "Which team or process is affected?",
            "What evidence would show the problem is controlled?",
        ],
        AUTOMATION_INTENT: [
            "What should be checked automatically?",
            "What should happen when a check fails?",
            "Should this start as a proposal, an evidence model, or an execution request after approval?",
        ],
        COMPLIANCE_INTENT: [
            "What compliance or audit evidence is needed?",
            "Which AI decision or output is in scope?",
            "Is this for internal review, external audit preparation, or controlled workflow design?",
        ],
        GENERAL_IMPROVEMENT_INTENT: [
            "What AI use or process should the advisory guidance focus on?",
            "Is the immediate need planning, risk reduction, or workflow design?",
            "Should this remain advisory, or should it become a governed workflow proposal?",
        ],
        CONTINUATION_INTENT: [
            "What should AiGOL continue?",
            "Which prior replay-visible session, decision, or artifact should be used as context?",
            "Should this remain clarification-only, advisory, or move to a governed workflow after approval?",
        ],
        BOUNDED_FILE_WRITE_PROOF_INTENT: [
            "Should AiGOL create one small proof file with fixed evidence text?",
            "Should this use the certified file-write worker path only after approval?",
            "Should replay evidence be recorded for the bounded file-write action?",
        ],
        AMBIGUOUS_INTENT: [
            "What are you trying to improve or control?",
            "Does this involve AI outputs, human approval, compliance evidence, or operational decisions?",
            "Should we start with planning, clarification, or a governed workflow proposal?",
        ],
    }
    return list(questions[intent_family])


def _expected_workflow_targets(intent_family: str) -> list[str]:
    if intent_family == GENERAL_IMPROVEMENT_INTENT:
        return [OCS_LLM_COGNITION_TARGET]
    if intent_family == BOUNDED_FILE_WRITE_PROOF_INTENT:
        return [BOUNDED_FILE_WRITE_WORKER_USER_SESSION_TARGET]
    return [CREATE_DOMAIN_COMPLIANCE_CLARIFICATION_TARGET]


def _has_workflow_or_control_signals(normalized: str) -> bool:
    return any(
        signal in normalized
        for signal in (
            "human approval",
            "collect evidence",
            "before staff use",
            "before action",
            "workflow",
            "controlled",
            "audit evidence",
        )
    )


def _matched_terms(normalized: str, terms: tuple[str, ...]) -> list[str]:
    return [term for term in terms if _contains_term(normalized, term)]


def _contains_term(normalized: str, term: str) -> bool:
    if " " in term:
        return term in normalized
    return _has_word(normalized, term)


def _has_word(normalized: str, word: str) -> bool:
    return re.search(rf"\b{re.escape(word)}\b", normalized) is not None


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _require_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"{field_name} must be a JSON object")
    return deepcopy(value)
