"""Replay-derived learning runtime for Universal Translation artifacts."""

from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from pathlib import Path
import re
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.universal_translation_artifact_schema import (
    GOVERNANCE_TO_HUMAN,
    HUMAN_TO_GOVERNANCE,
    validate_universal_translation_artifact,
)


RUNTIME_VERSION = "REPLAY_DERIVED_TRANSLATION_LEARNING_RUNTIME_V1"
REPLAY_STEP = "replay_derived_translation_learning_recorded"

LEARNING_ARTIFACT_TYPE = "REPLAY_DERIVED_TRANSLATION_LEARNING_ARTIFACT_V1"
IMPROVEMENT_PROPOSAL_TYPE = "TRANSLATION_DETERMINISTIC_RULE_IMPROVEMENT_PROPOSAL_V1"

PROMOTION_CANDIDATES_IDENTIFIED = "PROMOTION_CANDIDATES_IDENTIFIED"
NO_PROMOTION_CANDIDATES = "NO_PROMOTION_CANDIDATES"

ARTIFACT_TOKEN_RE = re.compile(r"\b[A-Z][A-Z0-9]+(?:_[A-Z0-9]+)+_V\d+\b")
PATH_TOKEN_RE = re.compile(r"\b(?:docs|aigol|tests|runtime|sapianta_bridge)/[A-Za-z0-9_./-]+\b")
WORD_RE = re.compile(r"[a-z0-9_./-]+")


def analyze_replay_derived_translation_learning(
    *,
    learning_id: str,
    translation_artifacts: list[dict[str, Any]],
    replay_dir: str | Path,
    created_at: str,
    replay_history: list[dict[str, Any]] | None = None,
    provider_explanations: list[dict[str, Any]] | None = None,
    deterministic_translations: list[dict[str, Any]] | None = None,
    human_confirmations: list[dict[str, Any]] | None = None,
    clarification_history: list[dict[str, Any]] | None = None,
    err_evidence: dict[str, Any] | None = None,
    promotion_policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Analyze replayed translations and emit proposal-only deterministic rule candidates."""

    replay_path = Path(replay_dir)
    policy = _normalized_policy(promotion_policy)
    err = _optional_mapping(err_evidence, "err_evidence")
    artifacts = _collect_translation_artifacts(
        translation_artifacts=translation_artifacts,
        replay_history=replay_history,
        deterministic_translations=deterministic_translations,
    )
    provider_summary = _summarize_optional_evidence(provider_explanations, "provider_explanations")
    clarification_summary = _summarize_optional_evidence(clarification_history, "clarification_history")
    confirmations = _normalized_confirmations(human_confirmations)
    clusters = _cluster_translation_patterns(artifacts, confirmations, clarification_history or [], policy)
    proposals = [
        _improvement_proposal(
            learning_id=learning_id,
            cluster=cluster,
            policy=policy,
            created_at=created_at,
        )
        for cluster in clusters
        if cluster["promotion_candidate"] is True
    ]
    status = PROMOTION_CANDIDATES_IDENTIFIED if proposals else NO_PROMOTION_CANDIDATES
    artifact = {
        "artifact_type": LEARNING_ARTIFACT_TYPE,
        "runtime_version": RUNTIME_VERSION,
        "learning_id": _require_string(learning_id, "learning_id"),
        "learning_status": status,
        "promotion_policy": deepcopy(policy),
        "translation_artifact_count": len(artifacts),
        "translation_artifact_hashes": [item["artifact_hash"] for item in artifacts],
        "pattern_clusters": deepcopy(clusters),
        "improvement_proposals": deepcopy(proposals),
        "proposal_count": len(proposals),
        "provider_evidence_summary": provider_summary,
        "clarification_history_summary": clarification_summary,
        "human_confirmation_summary": _confirmation_summary(confirmations),
        "err_evidence": deepcopy(err),
        "err_evidence_hash": replay_hash(err) if err else None,
        "ppp_integration": {
            "proposal_pipeline": "PPP",
            "route_required": True,
            "human_approval_required": True,
            "implementation_authorized": False,
        },
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": str(replay_path),
        "replay_visible": True,
        "proposal_only": True,
        "authority_granted": False,
        "runtime_behavior_modified": False,
        "deterministic_rules_modified": False,
        "approval_granted": False,
        "execution_requested": False,
        "worker_invoked": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
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
        "learning_status": status,
        "learning_artifact": deepcopy(artifact),
        "improvement_proposals": deepcopy(proposals),
        "pattern_clusters": deepcopy(clusters),
        "proposal_count": len(proposals),
        "replay_reference": str(replay_path),
        "proposal_only": True,
        "authority_granted": False,
        "runtime_behavior_modified": False,
        "deterministic_rules_modified": False,
        "approval_granted": False,
        "execution_requested": False,
        "governance_mutated": False,
        "replay_visible": True,
    }


def reconstruct_replay_derived_translation_learning_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct replay-derived translation learning evidence."""

    replay_path = Path(replay_dir)
    wrapper = load_json(replay_path / f"000_{REPLAY_STEP}.json")
    if wrapper.get("replay_index") != 0 or wrapper.get("replay_step") != REPLAY_STEP:
        raise FailClosedRuntimeError("replay-derived translation learning replay ordering mismatch")
    _verify_wrapper_hash(wrapper)
    artifact = _require_mapping(wrapper.get("artifact"), "learning_artifact")
    _verify_artifact_hash(artifact)
    if artifact.get("artifact_type") != LEARNING_ARTIFACT_TYPE:
        raise FailClosedRuntimeError("replay-derived translation learning artifact type mismatch")
    _validate_learning_authority(artifact)
    for proposal in artifact["improvement_proposals"]:
        _verify_artifact_hash(proposal)
        if proposal.get("artifact_type") != IMPROVEMENT_PROPOSAL_TYPE:
            raise FailClosedRuntimeError("translation learning proposal artifact type mismatch")
        _validate_proposal_authority(proposal)
    return {
        "runtime_version": RUNTIME_VERSION,
        "learning_status": artifact["learning_status"],
        "learning_artifact": deepcopy(artifact),
        "improvement_proposals": deepcopy(artifact["improvement_proposals"]),
        "pattern_clusters": deepcopy(artifact["pattern_clusters"]),
        "proposal_count": artifact["proposal_count"],
        "replay_hash": wrapper["replay_hash"],
        "proposal_only": True,
        "authority_granted": False,
        "runtime_behavior_modified": False,
        "deterministic_rules_modified": False,
        "approval_granted": False,
        "execution_requested": False,
        "governance_mutated": False,
        "replay_visible": True,
    }


def _collect_translation_artifacts(
    *,
    translation_artifacts: list[dict[str, Any]],
    replay_history: list[dict[str, Any]] | None,
    deterministic_translations: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for source in (translation_artifacts, deterministic_translations or []):
        _require_list(source, "translation_artifacts")
        candidates.extend(source)
    for item in replay_history or []:
        if not isinstance(item, dict):
            raise FailClosedRuntimeError("replay_history entries must be JSON objects")
        if item.get("artifact_type") == "UNIVERSAL_TRANSLATION_ARTIFACT_V1":
            candidates.append(item)
        elif isinstance(item.get("artifact"), dict):
            candidates.append(item["artifact"])
    if not candidates:
        raise FailClosedRuntimeError("translation learning requires at least one translation artifact")
    validated: list[dict[str, Any]] = []
    seen: set[str] = set()
    for candidate in candidates:
        artifact = validate_universal_translation_artifact(candidate)
        if artifact["artifact_hash"] in seen:
            continue
        seen.add(artifact["artifact_hash"])
        validated.append(artifact)
    return validated


def _cluster_translation_patterns(
    artifacts: list[dict[str, Any]],
    confirmations: list[dict[str, Any]],
    clarification_history: list[dict[str, Any]],
    policy: dict[str, Any],
) -> list[dict[str, Any]]:
    buckets: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for artifact in artifacts:
        buckets[(artifact["source_direction"], _mapping_signature(artifact))].append(artifact)
    clusters = []
    for index, ((direction, mapping_signature), items) in enumerate(sorted(buckets.items()), start=1):
        expressions = sorted({_expression_for(item) for item in items if _expression_for(item)})
        canonical_expression = _canonical_expression(expressions)
        confirmation_count = _confirmation_count(items, confirmations)
        clarification_count = _clarification_count(items, clarification_history)
        occurrence_count = len(items)
        unique_expression_count = len(expressions)
        stability_ratio = 1.0
        promotion_confidence = _promotion_confidence(
            occurrence_count=occurrence_count,
            confirmation_count=confirmation_count,
            unique_expression_count=unique_expression_count,
            clarification_count=clarification_count,
            stability_ratio=stability_ratio,
            policy=policy,
        )
        candidate = (
            occurrence_count >= policy["minimum_occurrences"]
            and confirmation_count >= policy["minimum_human_confirmations"]
            and unique_expression_count >= policy["minimum_equivalent_expressions"]
            and promotion_confidence >= policy["minimum_promotion_confidence"]
        )
        clusters.append(
            {
                "cluster_id": f"TRANSLATION-PATTERN-{index:03d}",
                "source_direction": direction,
                "mapping_signature": mapping_signature,
                "canonical_expression": canonical_expression,
                "equivalent_expressions": expressions,
                "translation_artifact_hashes": [item["artifact_hash"] for item in items],
                "occurrence_count": occurrence_count,
                "unique_expression_count": unique_expression_count,
                "human_confirmation_count": confirmation_count,
                "clarification_count": clarification_count,
                "stable_governance_mapping": True,
                "mapping_stability_ratio": stability_ratio,
                "promotion_confidence": promotion_confidence,
                "promotion_candidate": candidate,
                "candidate_reason": _candidate_reason(candidate, promotion_confidence, policy),
                "proposed_rule_kind": _rule_kind(direction),
            }
        )
    return clusters


def _improvement_proposal(
    *,
    learning_id: str,
    cluster: dict[str, Any],
    policy: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    proposal = {
        "artifact_type": IMPROVEMENT_PROPOSAL_TYPE,
        "proposal_id": f"{learning_id}:{cluster['cluster_id']}:IMPROVEMENT-PROPOSAL",
        "proposal_status": "PROPOSED",
        "proposal_kind": "DETERMINISTIC_TRANSLATION_RULE_CANDIDATE",
        "source_runtime": RUNTIME_VERSION,
        "source_cluster_id": cluster["cluster_id"],
        "source_direction": cluster["source_direction"],
        "canonical_expression": cluster["canonical_expression"],
        "equivalent_expressions": list(cluster["equivalent_expressions"]),
        "mapping_signature": cluster["mapping_signature"],
        "proposed_rule_kind": cluster["proposed_rule_kind"],
        "promotion_confidence": cluster["promotion_confidence"],
        "supporting_translation_artifact_hashes": list(cluster["translation_artifact_hashes"]),
        "minimum_policy_used": deepcopy(policy),
        "proposal_text": (
            "Promote the repeated replay-observed translation pattern into a deterministic "
            "translation rule candidate after PPP routing, governance review, and explicit human approval."
        ),
        "ppp_route_required": True,
        "human_approval_required": True,
        "implementation_authorized": False,
        "deterministic_rule_modified": False,
        "runtime_behavior_modified": False,
        "authority_granted": False,
        "approval_granted": False,
        "execution_requested": False,
        "worker_invoked": False,
        "governance_mutated": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    proposal["artifact_hash"] = replay_hash(proposal)
    return proposal


def _mapping_signature(artifact: dict[str, Any]) -> str:
    if artifact["source_direction"] == HUMAN_TO_GOVERNANCE:
        payload = artifact["translated_governance_payload"]
    elif artifact["source_direction"] == GOVERNANCE_TO_HUMAN:
        payload = artifact["human_readable_payload"]
    else:
        raise FailClosedRuntimeError("translation learning source direction unsupported")
    stable_payload = _stable_mapping_payload(payload)
    return replay_hash(stable_payload)


def _stable_mapping_payload(payload: dict[str, Any]) -> dict[str, Any]:
    ignored = {
        "rendered_explanation",
        "authoritative_state_references",
        "source_runtime_state_reference",
        "created_at",
    }
    return {key: deepcopy(value) for key, value in sorted(payload.items()) if key not in ignored}


def _expression_for(artifact: dict[str, Any]) -> str:
    if artifact["source_direction"] == HUMAN_TO_GOVERNANCE:
        source = artifact["source_payload"]
        raw = source.get("human_request") or source.get("human_prompt")
        if isinstance(raw, str) and raw.strip():
            return _normalize_expression(raw)
        normalized = artifact["normalized_intent"].get("normalized_text")
        return _normalize_expression(normalized) if isinstance(normalized, str) else ""
    payload = artifact["human_readable_payload"]
    raw = payload.get("summary") or payload.get("operator_action_required")
    return _normalize_expression(raw) if isinstance(raw, str) else ""


def _normalize_expression(value: str) -> str:
    normalized = ARTIFACT_TOKEN_RE.sub("<ARTIFACT_ID>", value.strip().lower())
    normalized = PATH_TOKEN_RE.sub("<TARGET_PATH>", normalized)
    return " ".join(WORD_RE.findall(normalized))


def _canonical_expression(expressions: list[str]) -> str:
    if not expressions:
        return "NO_CANONICAL_EXPRESSION"
    return sorted(expressions, key=lambda item: (len(item), item))[0]


def _confirmation_count(items: list[dict[str, Any]], confirmations: list[dict[str, Any]]) -> int:
    hashes = {item["artifact_hash"] for item in items}
    mapping_signatures = {_mapping_signature(item) for item in items}
    count = 0
    for confirmation in confirmations:
        if confirmation["confirmed"] is not True:
            continue
        if confirmation.get("translation_artifact_hash") in hashes:
            count += 1
        elif confirmation.get("mapping_signature") in mapping_signatures:
            count += 1
    return count


def _clarification_count(items: list[dict[str, Any]], clarification_history: list[dict[str, Any]]) -> int:
    hashes = {item["artifact_hash"] for item in items}
    count = 0
    for clarification in clarification_history:
        if not isinstance(clarification, dict):
            raise FailClosedRuntimeError("clarification_history entries must be JSON objects")
        if clarification.get("translation_artifact_hash") in hashes:
            count += 1
    return count


def _promotion_confidence(
    *,
    occurrence_count: int,
    confirmation_count: int,
    unique_expression_count: int,
    clarification_count: int,
    stability_ratio: float,
    policy: dict[str, Any],
) -> float:
    occurrence_score = min(1.0, occurrence_count / policy["minimum_occurrences"])
    confirmation_score = min(1.0, confirmation_count / policy["minimum_human_confirmations"])
    expression_score = min(1.0, unique_expression_count / policy["minimum_equivalent_expressions"])
    clarification_penalty = min(0.3, clarification_count * 0.1)
    score = (occurrence_score * 0.3) + (confirmation_score * 0.3) + (expression_score * 0.2) + (stability_ratio * 0.2)
    return round(max(0.0, score - clarification_penalty), 4)


def _candidate_reason(candidate: bool, confidence: float, policy: dict[str, Any]) -> str:
    if candidate:
        return "Pattern is repeated, confirmed by humans, stable, and suitable for PPP proposal review."
    return (
        "Pattern is not eligible for promotion proposal under current policy "
        f"(confidence={confidence}, required={policy['minimum_promotion_confidence']})."
    )


def _rule_kind(direction: str) -> str:
    if direction == HUMAN_TO_GOVERNANCE:
        return "HUMAN_TO_GOVERNANCE_DETERMINISTIC_RULE"
    if direction == GOVERNANCE_TO_HUMAN:
        return "GOVERNANCE_TO_HUMAN_DETERMINISTIC_RULE"
    raise FailClosedRuntimeError("translation learning rule direction unsupported")


def _normalized_policy(policy: dict[str, Any] | None) -> dict[str, Any]:
    value = _optional_mapping(policy, "promotion_policy")
    return {
        "minimum_occurrences": _positive_int(value.get("minimum_occurrences", 3), "minimum_occurrences"),
        "minimum_human_confirmations": _positive_int(
            value.get("minimum_human_confirmations", 1),
            "minimum_human_confirmations",
        ),
        "minimum_equivalent_expressions": _positive_int(
            value.get("minimum_equivalent_expressions", 2),
            "minimum_equivalent_expressions",
        ),
        "minimum_promotion_confidence": _confidence_float(value.get("minimum_promotion_confidence", 0.8)),
    }


def _normalized_confirmations(confirmations: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    if confirmations is None:
        return []
    _require_list(confirmations, "human_confirmations")
    normalized = []
    for confirmation in confirmations:
        item = _require_mapping(confirmation, "human_confirmation")
        normalized.append(
            {
                "confirmation_id": _optional_string(item.get("confirmation_id")),
                "confirmed": item.get("confirmed") is True,
                "translation_artifact_hash": _optional_string(item.get("translation_artifact_hash")),
                "mapping_signature": _optional_string(item.get("mapping_signature")),
                "confirmed_by": _optional_string(item.get("confirmed_by")),
            }
        )
    return normalized


def _confirmation_summary(confirmations: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "confirmation_count": len(confirmations),
        "positive_confirmation_count": sum(1 for item in confirmations if item["confirmed"] is True),
        "confirmation_hash": replay_hash(confirmations),
    }


def _summarize_optional_evidence(values: list[dict[str, Any]] | None, field_name: str) -> dict[str, Any]:
    if values is None:
        values = []
    _require_list(values, field_name)
    for item in values:
        _require_mapping(item, field_name)
    return {
        "evidence_count": len(values),
        "evidence_hash": replay_hash(values),
    }


def _validate_learning_authority(artifact: dict[str, Any]) -> None:
    for field in (
        "authority_granted",
        "runtime_behavior_modified",
        "deterministic_rules_modified",
        "approval_granted",
        "execution_requested",
        "worker_invoked",
        "governance_mutated",
        "replay_mutated",
    ):
        if artifact.get(field) is True:
            raise FailClosedRuntimeError("translation learning artifact cannot grant authority")


def _validate_proposal_authority(proposal: dict[str, Any]) -> None:
    for field in (
        "implementation_authorized",
        "deterministic_rule_modified",
        "runtime_behavior_modified",
        "authority_granted",
        "approval_granted",
        "execution_requested",
        "worker_invoked",
        "governance_mutated",
    ):
        if proposal.get(field) is True:
            raise FailClosedRuntimeError("translation learning proposal cannot grant authority")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash", None)
    if not isinstance(actual, str) or replay_hash(expected) != actual:
        raise FailClosedRuntimeError("replay-derived translation learning replay hash mismatch")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash", None)
    if not isinstance(actual, str) or replay_hash(expected) != actual:
        raise FailClosedRuntimeError("replay-derived translation learning artifact hash mismatch")


def _require_list(value: Any, field_name: str) -> None:
    if not isinstance(value, list):
        raise FailClosedRuntimeError(f"{field_name} must be a list")


def _require_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"{field_name} must be a JSON object")
    return deepcopy(value)


def _optional_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"{field_name} must be a JSON object")
    return deepcopy(value)


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _optional_string(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _positive_int(value: Any, field_name: str) -> int:
    if not isinstance(value, int) or value < 1:
        raise FailClosedRuntimeError(f"{field_name} must be a positive integer")
    return value


def _confidence_float(value: Any) -> float:
    if not isinstance(value, int | float) or value < 0 or value > 1:
        raise FailClosedRuntimeError("minimum_promotion_confidence must be between 0 and 1")
    return float(value)
