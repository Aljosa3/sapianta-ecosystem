"""Human-facing operator decision support for AiGOL."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_OPERATOR_DECISION_SUPPORT_RUNTIME_V1"
FINAL_CLASSIFICATION = "AIGOL_OPERATOR_DECISION_SUPPORT_RUNTIME_STATUS"

OPERATOR_DECISION_SUPPORT_ARTIFACT_V1 = "OPERATOR_DECISION_SUPPORT_ARTIFACT_V1"
RECOMMENDATION_GENERATED = "RECOMMENDATION_GENERATED"
FAILED_CLOSED = "FAILED_CLOSED"

DOMAIN_SELECTION = "DOMAIN_SELECTION"
CAPABILITY_PRIORITIZATION = "CAPABILITY_PRIORITIZATION"
ROADMAP_PRIORITIZATION = "ROADMAP_PRIORITIZATION"
IMPLEMENTATION_SEQUENCING = "IMPLEMENTATION_SEQUENCING"
PROVIDER_COMPARISON = "PROVIDER_COMPARISON"
WORKER_COMPARISON = "WORKER_COMPARISON"

REPLAY_STEPS = (
    "operator_decision_support_recorded",
    "operator_decision_support_returned",
)


def is_operator_decision_support_prompt(human_prompt: str) -> bool:
    """Return whether a prompt asks for human-facing recommendation support."""

    try:
        return _classify_question(human_prompt) is not None
    except FailClosedRuntimeError:
        return False


def run_operator_decision_support(
    *,
    recommendation_id: str,
    prompt_id: str,
    human_prompt: str,
    canonical_chain_id: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Create a replay-visible non-authoritative recommendation artifact."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        question = _require_string(human_prompt, "human_prompt")
        category = _classify_question(question)
        if category is None:
            raise FailClosedRuntimeError("operator decision support failed closed: unsupported recommendation category")
        profile = _recommendation_profile(category, question)
        artifact = _recommendation_artifact(
            recommendation_id=recommendation_id,
            prompt_id=prompt_id,
            question=question,
            canonical_chain_id=canonical_chain_id,
            created_at=created_at,
            replay_reference=str(replay_path),
            category=category,
            profile=profile,
            failure_reason=None,
        )
        returned = _returned_artifact(artifact)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, replay_path)
    except Exception as exc:
        failure_reason = str(exc) if isinstance(exc, FailClosedRuntimeError) else "operator decision support failed closed"
        artifact = _failed_recommendation_artifact(
            recommendation_id=recommendation_id,
            prompt_id=prompt_id,
            human_prompt=human_prompt,
            canonical_chain_id=canonical_chain_id,
            created_at=created_at,
            replay_reference=str(replay_path),
            failure_reason=failure_reason,
        )
        returned = _returned_artifact(artifact)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, replay_path)


def reconstruct_operator_decision_support_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct operator decision-support replay evidence."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("operator decision support replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("operator decision support replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    recommendation = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("recommendation_reference") != recommendation["recommendation_id"]:
        raise FailClosedRuntimeError("operator decision support replay reference mismatch")
    if returned.get("recommendation_hash") != recommendation["artifact_hash"]:
        raise FailClosedRuntimeError("operator decision support replay hash mismatch")
    return {
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "recommendation_status": recommendation["recommendation_status"],
        "category": recommendation["category"],
        "recommendation": deepcopy(recommendation.get("recommendation")),
        "alternatives": deepcopy(recommendation.get("alternatives", [])),
        "risks": deepcopy(recommendation.get("risks", [])),
        "confidence": recommendation.get("confidence"),
        "human_authority": recommendation.get("human_authority"),
        "replay_visible": True,
        "lineage_bound": True,
        "replay_artifact_count": len(wrappers),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_created": False,
        "domain_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "approval_bypassed": False,
        "replay_hash": replay_hash(wrappers),
    }


def render_operator_decision_support_summary(capture: dict[str, Any]) -> str:
    artifact = capture.get("operator_decision_support_artifact") or {}
    lines = [
        "Recommendation Generated",
        f"Category: {artifact.get('category')}",
        f"Recommended: {artifact.get('recommendation')}",
        "Alternatives:",
    ]
    lines.extend(f"* {item}" for item in artifact.get("alternatives", []))
    lines.append("Risks:")
    lines.extend(f"* {item}" for item in artifact.get("risks", []))
    lines.extend(
        [
            f"Confidence: {artifact.get('confidence')}",
            "Human Decision Required: Approve / Reject / Ignore",
            f"replay_reference: {capture.get('operator_decision_support_replay_reference')}",
            f"provider_invoked: {capture.get('provider_invoked')}",
            f"worker_invoked: {capture.get('worker_invoked')}",
            f"execution_requested: {capture.get('execution_requested')}",
        ]
    )
    if artifact.get("failure_reason"):
        lines.append(f"failure_reason: {artifact['failure_reason']}")
    return "\n".join(lines)


def _classify_question(human_prompt: str) -> str | None:
    normalized = _require_string(human_prompt, "human_prompt").lower().strip().rstrip(".?!")
    if (
        "first real" in normalized
        and ("product domain" in normalized or "aigol product domain" in normalized)
    ) or ("which domain" in normalized and "product" in normalized):
        return DOMAIN_SELECTION
    if "which capability" in normalized or ("capability" in normalized and "next" in normalized):
        return CAPABILITY_PRIORITIZATION
    if "roadmap" in normalized or "prioritize" in normalized or "priority" in normalized:
        return ROADMAP_PRIORITIZATION
    if "sequence" in normalized or "sequencing" in normalized or "what should be implemented first" in normalized:
        return IMPLEMENTATION_SEQUENCING
    if "which provider" in normalized or ("provider" in normalized and "first" in normalized):
        return PROVIDER_COMPARISON
    if "which worker" in normalized or ("worker" in normalized and "compare" in normalized):
        return WORKER_COMPARISON
    return None


def _recommendation_profile(category: str, question: str) -> dict[str, Any]:
    if category == DOMAIN_SELECTION:
        return {
            "recommendation": "SAPIANTA_AI_PR_GATE",
            "alternatives": [
                "SAPIANTA_POLICY_REVIEW_GATE",
                "SAPIANTA_PROVIDER_EXECUTION_GATE",
                "SAPIANTA_COMPLIANCE_REQUIREMENT_VALIDATOR",
            ],
            "risks": [
                "Scope may drift from Product 1 if the domain becomes a general automation gateway.",
                "Repository and CI signals must be treated as evidence inputs, not execution authority.",
                "Human approval boundaries must remain explicit before any implementation handoff.",
            ],
            "confidence": "HIGH",
            "reasoning": [
                "Product 1 is AI Decision Validator, and a pull-request gate is an enterprise-readable decision-validation domain.",
                "The domain can demonstrate deterministic validation, replay evidence, and fail-closed recommendations without broker/API execution semantics.",
                "The recommendation aligns with auditability and human review while keeping runtime activation bounded.",
            ],
        }
    if category == CAPABILITY_PRIORITIZATION:
        return {
            "recommendation": "CLARIFICATION_RESPONSE_INGESTION",
            "alternatives": [
                "DOMAIN_ADAPTATION_CANDIDATE_REVIEW",
                "PROVIDER_RESPONSE_SCHEMA_HARDENING",
                "REPLAY_CHAIN_OPERATOR_SUMMARY",
            ],
            "risks": [
                "Capability work can accidentally imply approval if operator choices are not modeled as human decisions.",
                "Clarification ingestion must not create domains or implementation artifacts automatically.",
            ],
            "confidence": "MEDIUM_HIGH",
            "reasoning": [
                "Recent runtimes can ask for clarification, but follow-up operator answers are still a known gap.",
                "Closing that gap improves conversational UX while preserving human authority.",
            ],
        }
    if category == PROVIDER_COMPARISON:
        return {
            "recommendation": "OPENAI_RESPONSES_PROVIDER",
            "alternatives": [
                "LOCAL_OFFLINE_RECOMMENDATION_ONLY",
                "ANTHROPIC_MESSAGES_PROVIDER",
                "SECONDARY_PROVIDER_FOR_COMPARATIVE_REVIEW",
            ],
            "risks": [
                "Credential loading must remain governed and explicit.",
                "Provider output must remain non-authoritative and schema-normalized.",
                "Provider availability cannot become a prerequisite for replay reconstruction.",
            ],
            "confidence": "MEDIUM",
            "reasoning": [
                "The native provider execution runtime already defines OpenAI credential policy and response normalization.",
                "Attaching the already-modeled provider first reduces integration ambiguity.",
                "A deterministic fallback should remain available when credentials or approval are absent.",
            ],
        }
    if category == WORKER_COMPARISON:
        return {
            "recommendation": "VALIDATION_AND_REPLAY_REVIEW_WORKER",
            "alternatives": [
                "DOMAIN_FOUNDATION_WORKER",
                "PROVIDER_PROPOSAL_REVIEW_WORKER",
                "IMPLEMENTATION_DRY_RUN_WORKER",
            ],
            "risks": [
                "Worker comparison must not dispatch or invoke workers.",
                "Worker choice should remain bound to explicit implementation approval.",
            ],
            "confidence": "MEDIUM",
            "reasoning": [
                "Validation and replay review are closest to Product 1 and governance evidence.",
                "This worker family supports decision validation without expanding execution authority.",
            ],
        }
    if category == IMPLEMENTATION_SEQUENCING:
        return {
            "recommendation": "CLARIFICATION_RESPONSE_INGESTION_THEN_DOMAIN_ADAPTATION_REVIEW",
            "alternatives": [
                "PROVIDER_COMPARISON_BEFORE_CLARIFICATION",
                "DOMAIN_FACTORY_BEFORE_REVIEW_UX",
                "WORKER_FOUNDATION_BEFORE_OPERATOR_DECISION_SUPPORT",
            ],
            "risks": [
                "Implementation sequencing can bypass governance if recommendations are treated as approvals.",
                "Domain factory work should wait until review and clarification paths are explicit.",
            ],
            "confidence": "MEDIUM_HIGH",
            "reasoning": [
                "Clarification ingestion converts existing request artifacts into human-reviewed next steps.",
                "Domain adaptation review can then reuse clarified operator intent without creating domains automatically.",
            ],
        }
    return {
        "recommendation": "PRODUCT_1_DECISION_VALIDATOR_ROADMAP",
        "alternatives": [
            "PROVIDER_LAYER_EXPANSION",
            "WORKER_FOUNDATION_EXPANSION",
            "DOMAIN_FACTORY_EXPANSION",
        ],
        "risks": [
            "Roadmap work can over-expand beyond Product 1.",
            "Prioritization artifacts must not mutate governance or release state.",
        ],
        "confidence": "MEDIUM",
        "reasoning": [
            "Product 1 alignment should remain the primary roadmap constraint.",
            "Decision validation and replay evidence are the strongest enterprise-facing foundation.",
        ],
    }


def _recommendation_artifact(
    *,
    recommendation_id: str,
    prompt_id: str,
    question: str,
    canonical_chain_id: str,
    created_at: str,
    replay_reference: str,
    category: str,
    profile: dict[str, Any],
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": OPERATOR_DECISION_SUPPORT_ARTIFACT_V1,
        "milestone_id": MILESTONE_ID,
        "recommendation_id": _require_string(recommendation_id, "recommendation_id"),
        "prompt_id": _require_string(prompt_id, "prompt_id"),
        "question": _require_string(question, "question"),
        "question_hash": replay_hash(question),
        "canonical_chain_id": _require_string(canonical_chain_id, "canonical_chain_id"),
        "recommendation_status": RECOMMENDATION_GENERATED,
        "category": category,
        "recommendation": profile["recommendation"],
        "alternatives": list(profile["alternatives"]),
        "risks": list(profile["risks"]),
        "confidence": profile["confidence"],
        "reasoning": list(profile["reasoning"]),
        "llm_analysis_candidate": {
            "candidate_role": "NON_AUTHORITATIVE_ANALYSIS_CANDIDATE",
            "provider_invoked": False,
            "can_analyze": True,
            "can_compare": True,
            "can_recommend": True,
            "can_explain": True,
            "can_authorize": False,
            "can_execute": False,
            "can_approve": False,
            "can_mutate_governance": False,
            "can_mutate_replay": False,
            "can_create_domains": False,
        },
        "human_authority": "APPROVE_REJECT_IGNORE",
        "replay_references": {
            "canonical_chain_id": _require_string(canonical_chain_id, "canonical_chain_id"),
            "replay_reference": _require_string(replay_reference, "replay_reference"),
        },
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": replay_reference,
        "replay_visible": True,
        "lineage_bound": True,
        **_authority_flags(),
        "failure_reason": failure_reason,
    }
    artifact["recommendation_hash"] = replay_hash(_recommendation_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_recommendation_artifact(
    *,
    recommendation_id: str,
    prompt_id: str,
    human_prompt: Any,
    canonical_chain_id: str,
    created_at: str,
    replay_reference: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": OPERATOR_DECISION_SUPPORT_ARTIFACT_V1,
        "milestone_id": MILESTONE_ID,
        "recommendation_id": recommendation_id if isinstance(recommendation_id, str) else None,
        "prompt_id": prompt_id if isinstance(prompt_id, str) else None,
        "question": human_prompt if isinstance(human_prompt, str) else None,
        "question_hash": replay_hash(human_prompt) if isinstance(human_prompt, str) else None,
        "canonical_chain_id": canonical_chain_id if isinstance(canonical_chain_id, str) else None,
        "recommendation_status": FAILED_CLOSED,
        "category": None,
        "recommendation": None,
        "alternatives": [],
        "risks": [],
        "confidence": "NONE",
        "reasoning": [],
        "llm_analysis_candidate": {
            "candidate_role": "UNAVAILABLE",
            "provider_invoked": False,
            "can_authorize": False,
            "can_execute": False,
            "can_approve": False,
            "can_mutate_governance": False,
            "can_mutate_replay": False,
            "can_create_domains": False,
        },
        "human_authority": "APPROVE_REJECT_IGNORE",
        "replay_references": {"replay_reference": replay_reference},
        "created_at": created_at if isinstance(created_at, str) else "",
        "replay_reference": replay_reference,
        "replay_visible": True,
        "lineage_bound": True,
        **_authority_flags(),
        "failure_reason": failure_reason,
    }
    artifact["recommendation_hash"] = replay_hash(_recommendation_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(recommendation: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(recommendation)
    artifact = {
        "event_type": "OPERATOR_DECISION_SUPPORT_RETURNED",
        "milestone_id": MILESTONE_ID,
        "recommendation_reference": recommendation["recommendation_id"],
        "recommendation_hash": recommendation["artifact_hash"],
        "recommendation_status": recommendation["recommendation_status"],
        "category": recommendation["category"],
        "human_authority": recommendation["human_authority"],
        "replay_visible": True,
        **_authority_flags(),
        "failure_reason": recommendation["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(recommendation: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "command": "aigol decision-support recommend",
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "response_status": returned["recommendation_status"],
        "response_source": "OPERATOR_DECISION_SUPPORT_RUNTIME",
        "recommendation_status": returned["recommendation_status"],
        "category": returned["category"],
        "operator_decision_support_artifact": deepcopy(recommendation),
        "operator_decision_support_returned": deepcopy(returned),
        "operator_decision_support_replay_reference": str(replay_path),
        "conversation_replay_reference": str(replay_path),
        "canonical_chain_id": recommendation.get("canonical_chain_id"),
        "current_chain_id": recommendation.get("canonical_chain_id"),
        "latest_chain_id": recommendation.get("canonical_chain_id"),
        "response_text": "",
        "fail_closed": returned["recommendation_status"] == FAILED_CLOSED,
        "failure_reason": returned.get("failure_reason"),
        **_authority_flags(),
    }
    capture["response_text"] = render_operator_decision_support_summary(capture)
    capture["operator_decision_support_hash"] = replay_hash(capture)
    return capture


def _recommendation_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "recommendation_id": artifact.get("recommendation_id"),
        "question_hash": artifact.get("question_hash"),
        "category": artifact.get("category"),
        "recommendation": artifact.get("recommendation"),
        "alternatives": artifact.get("alternatives", []),
        "risks": artifact.get("risks", []),
        "confidence": artifact.get("confidence"),
        "reasoning": artifact.get("reasoning", []),
    }


def _authority_flags() -> dict[str, bool]:
    return {
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_created": False,
        "domain_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "approval_bypassed": False,
    }


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("operator decision support replay step ordering mismatch")
    _verify_artifact_hash(artifact)
    wrapper = {"replay_index": index, "replay_step": step, "artifact": deepcopy(artifact)}
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    try:
        path = replay_dir / f"{index:03d}_{step}.json"
        if not path.exists():
            _persist_step(replay_dir, index, step, artifact)
    except FailClosedRuntimeError:
        return


def _ensure_replay_available(replay_dir: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_dir / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("operator decision support failed closed: replay already exists")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("operator decision support artifact hash is required")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("operator decision support artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("operator decision support replay hash is required")
    expected_input = deepcopy(wrapper)
    expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("operator decision support replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()
