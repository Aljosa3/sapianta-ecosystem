"""Minimal deterministic intent classifier for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


CLASSIFIER_VERSION = "INTENT_CLASSIFIER_V1"
PLATFORM_SEMANTIC_GAP_CLOSURE_G2_13_PROVIDER_ASSISTED_AND_LEGACY_CLASSIFIER_CLOSURE_V1 = (
    "PLATFORM_SEMANTIC_GAP_CLOSURE_G2_13_PROVIDER_ASSISTED_AND_LEGACY_CLASSIFIER_CLOSURE_V1"
)

CONVERSATION = "CONVERSATION"
CONSTITUTIONAL_MEMORY_CONSULTATION = "CONSTITUTIONAL_MEMORY_CONSULTATION"
PROVIDER_PROPOSAL = "PROVIDER_PROPOSAL"
EXECUTION_REQUEST = "EXECUTION_REQUEST"
FAILED_CLOSED = "FAILED_CLOSED"
CLASSIFIED = "CLASSIFIED"

VALID_DESTINATIONS = frozenset(
    {
        CONVERSATION,
        CONSTITUTIONAL_MEMORY_CONSULTATION,
        PROVIDER_PROPOSAL,
        EXECUTION_REQUEST,
    }
)

REPLAY_STEPS = ("intent_classification_artifact", "intent_classification_replay")

DESTINATION_RULES: dict[str, tuple[str, ...]] = {
    CONVERSATION: (
        "explain",
        "clarify",
        "discuss",
        "summarize",
        "what is aigol",
        "how does aigol",
        "architecture discussion",
    ),
    CONSTITUTIONAL_MEMORY_CONSULTATION: (
        "constitutional memory",
        "governance artifact",
        "governance document",
        "citation",
        "cite",
        "freeze manifest",
        "certification",
        "what does the constitution say",
    ),
    PROVIDER_PROPOSAL: (
        "provider proposal",
        "external llm",
        "openai proposal",
        "ask openai",
        "ask provider",
        "llm proposal",
        "proposal source",
    ),
    EXECUTION_REQUEST: (
        "inspect runtime",
        "runtime status",
        "read file",
        "list directory",
        "filesystem inspection",
        "read-only inspection",
        "execution request",
    ),
}


def classify_intent(
    *,
    artifact_id: str,
    human_request_reference: str,
    human_prompt: str,
    classification_timestamp: str,
    replay_reference: str,
    replay_dir: str | Path,
    normalized_request_reference: str | None = None,
    canonical_semantic_lineage: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Classify a human prompt into one non-authoritative intent artifact."""

    replay_path = Path(replay_dir)
    try:
        prompt = _normalize_text(human_prompt, "human_prompt")
        destination, reason = _classify_prompt(prompt)
        artifact = _classification_artifact(
            artifact_id=artifact_id,
            human_request_reference=human_request_reference,
            human_prompt=prompt,
            classification_destination=destination,
            classification_reason=reason,
            classification_timestamp=classification_timestamp,
            replay_reference=replay_reference,
            normalized_request_reference=normalized_request_reference,
            classification_status=CLASSIFIED,
            ambiguity_status="UNAMBIGUOUS",
            failure_reason=None,
            canonical_semantic_lineage=canonical_semantic_lineage,
        )
        _persist_step(replay_path, 0, REPLAY_STEPS[0], artifact)
        replay = _classification_replay(artifact)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], replay)
        return _capture(artifact, replay)
    except Exception as exc:
        artifact = _failed_artifact(
            artifact_id=artifact_id,
            human_request_reference=human_request_reference,
            human_prompt=human_prompt,
            classification_timestamp=classification_timestamp,
            replay_reference=replay_reference,
            normalized_request_reference=normalized_request_reference,
            failure_reason=_failure_reason(exc),
            canonical_semantic_lineage=canonical_semantic_lineage,
        )
        _persist_failure_if_possible(replay_path, artifact)
        replay = _classification_replay(artifact)
        _persist_failure_replay_if_possible(replay_path, replay)
        return _capture(artifact, replay)


def reconstruct_intent_classification_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate intent classification replay evidence."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("intent classification replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("intent classification replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)

    classification_artifact = wrappers[0]["artifact"]
    replay_artifact = wrappers[1]["artifact"]
    if replay_artifact.get("artifact_reference") != classification_artifact["artifact_id"]:
        raise FailClosedRuntimeError("intent classification replay artifact reference mismatch")
    if replay_artifact.get("classification_artifact_hash") != classification_artifact["artifact_hash"]:
        raise FailClosedRuntimeError("intent classification replay artifact hash mismatch")
    _validate_classification_artifact(classification_artifact)
    return {
        "artifact_id": classification_artifact["artifact_id"],
        "human_request_reference": classification_artifact["human_request_reference"],
        "classification_destination": classification_artifact["classification_destination"],
        "classification_status": classification_artifact["classification_status"],
        "ambiguity_status": classification_artifact["ambiguity_status"],
        "classifier_version": classification_artifact["classifier_version"],
        "legacy_classifier_status": classification_artifact.get("legacy_classifier_status"),
        "canonical_semantic_artifact_reference": classification_artifact.get("canonical_semantic_artifact_reference"),
        "canonical_semantic_artifact_hash": classification_artifact.get("canonical_semantic_artifact_hash"),
        "semantic_comparison_hash": classification_artifact.get("semantic_comparison_hash"),
        "semantic_comparison_parity_status": classification_artifact.get("semantic_comparison_parity_status"),
        "fallback_status": classification_artifact.get("fallback_status"),
        "migration_batch_id": classification_artifact.get("migration_batch_id"),
        "replay_visible": True,
        "non_authoritative": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _classify_prompt(prompt: str) -> tuple[str, str]:
    lowered = prompt.lower()
    matches: list[tuple[str, str]] = []
    for destination, terms in DESTINATION_RULES.items():
        for term in terms:
            if term in lowered:
                matches.append((destination, term))
                break
    if not matches:
        raise FailClosedRuntimeError("intent classification failed closed: unknown intent")
    destinations = {destination for destination, _term in matches}
    if len(destinations) > 1:
        raise FailClosedRuntimeError("intent classification failed closed: ambiguous intent")
    destination, term = matches[0]
    if destination not in VALID_DESTINATIONS:
        raise FailClosedRuntimeError("intent classification failed closed: invalid destination")
    return destination, f"matched deterministic intent marker: {term}"


def _legacy_classifier_closure_evidence(
    *,
    classification_destination: str | None,
    classification_reason: str,
    canonical_semantic_lineage: dict[str, Any] | None,
    failure_reason: str | None,
) -> dict[str, Any]:
    lineage = _normalize_canonical_semantic_lineage(canonical_semantic_lineage)
    compatibility = {
        "source": "LEGACY_INTENT_CLASSIFIER_V1",
        "classification_destination": classification_destination,
        "classification_reason": classification_reason,
        "classifier_version": CLASSIFIER_VERSION,
        "classification_status": CLASSIFIED if classification_destination else FAILED_CLOSED,
        "failure_reason": failure_reason,
        "authority_granted": False,
    }
    csa_destination = _csa_destination(lineage)
    csa_interpretation = {
        "source": "CANONICAL_SEMANTIC_ARTIFACT",
        "canonical_semantic_artifact_reference": lineage["canonical_semantic_artifact_reference"],
        "canonical_semantic_artifact_hash": lineage["canonical_semantic_artifact_hash"],
        "classification_destination": csa_destination,
        "workflow_id": lineage["workflow_id"],
        "semantic_identity": deepcopy(lineage["semantic_identity"]),
        "authority_granted": False,
    }
    csa_available = lineage["canonical_semantic_artifact_hash"] is not None
    parity_proven = csa_available and csa_destination == classification_destination
    if parity_proven:
        legacy_status = "CSA_PARITY_MIGRATED_LEGACY_COMPATIBILITY_VISIBLE"
        parity_status = "CSA_COMPATIBILITY_LEGACY_CLASSIFIER_PARITY_PROVEN"
        fallback_status = "LEGACY_COMPATIBILITY_VISIBLE_NOT_AUTHORITATIVE"
        differences: list[str] = []
    elif csa_available:
        legacy_status = "LEGACY_COMPATIBILITY_FALLBACK_ACTIVE"
        parity_status = "CSA_COMPATIBILITY_LEGACY_CLASSIFIER_DIVERGENT"
        fallback_status = "LEGACY_COMPATIBILITY_FALLBACK_AUTHORITATIVE"
        differences = ["CSA destination does not match legacy classifier destination."]
    else:
        legacy_status = "LEGACY_COMPATIBILITY_ONLY_CSA_UNAVAILABLE"
        parity_status = "CSA_LINEAGE_UNAVAILABLE_LEGACY_COMPATIBILITY_AUTHORITATIVE"
        fallback_status = "LEGACY_COMPATIBILITY_FALLBACK_AUTHORITATIVE"
        differences = ["CSA lineage unavailable for legacy classifier closure."]
    comparison = {
        "artifact_type": "LEGACY_CLASSIFIER_SEMANTIC_COMPARISON_ARTIFACT_V1",
        "migration_batch_id": PLATFORM_SEMANTIC_GAP_CLOSURE_G2_13_PROVIDER_ASSISTED_AND_LEGACY_CLASSIFIER_CLOSURE_V1,
        "legacy_classifier_status": legacy_status,
        "canonical_semantic_artifact_reference": lineage["canonical_semantic_artifact_reference"],
        "canonical_semantic_artifact_hash": lineage["canonical_semantic_artifact_hash"],
        "previous_compatibility_interpretation": deepcopy(compatibility),
        "canonical_semantic_interpretation": deepcopy(csa_interpretation),
        "semantic_equivalence_result": "EQUIVALENT" if parity_proven else "NOT_EQUIVALENT_OR_NOT_EVALUATED",
        "semantic_differences": differences,
        "parity_status": parity_status,
        "fallback_status": fallback_status,
        "non_authoritative": True,
        "routing_influence": False,
        "authority_granted": False,
        "approval_authority_granted": False,
        "execution_authority_granted": False,
        "provider_authority_granted": False,
        "worker_authority_granted": False,
        "replay_visible": True,
    }
    comparison["semantic_comparison_hash"] = replay_hash(
        {
            "compatibility": compatibility,
            "csa": csa_interpretation,
            "parity_status": parity_status,
        }
    )
    parity_evidence = {
        "parity_status": parity_status,
        "parity_scope": "LEGACY_INTENT_CLASSIFIER_DESTINATION",
        "legacy_classifier_status": legacy_status,
        "compatibility_interpretation_recorded": True,
        "compatibility_fallback_available": True,
        "semantic_comparison_hash": comparison["semantic_comparison_hash"],
        "migration_batch_id": PLATFORM_SEMANTIC_GAP_CLOSURE_G2_13_PROVIDER_ASSISTED_AND_LEGACY_CLASSIFIER_CLOSURE_V1,
        "historical_replay_reinterpreted": False,
        "authority_granted": False,
    }
    parity_evidence["parity_hash"] = replay_hash(parity_evidence)
    comparison["semantic_parity_evidence"] = deepcopy(parity_evidence)
    comparison["artifact_hash"] = replay_hash(comparison)
    return {
        "legacy_classifier_status": legacy_status,
        "provider_assisted_classifier_status": "NOT_APPLICABLE",
        "canonical_semantic_artifact_reference": lineage["canonical_semantic_artifact_reference"],
        "canonical_semantic_artifact_hash": lineage["canonical_semantic_artifact_hash"],
        "previous_compatibility_interpretation": compatibility,
        "semantic_comparison_artifact": comparison,
        "semantic_comparison_hash": comparison["artifact_hash"],
        "semantic_comparison_parity_status": parity_status,
        "semantic_parity_evidence": parity_evidence,
        "migration_batch_id": PLATFORM_SEMANTIC_GAP_CLOSURE_G2_13_PROVIDER_ASSISTED_AND_LEGACY_CLASSIFIER_CLOSURE_V1,
        "fallback_status": fallback_status,
        "replay_lineage": {
            "canonical_semantic_artifact_reference": lineage["canonical_semantic_artifact_reference"],
            "canonical_semantic_artifact_hash": lineage["canonical_semantic_artifact_hash"],
        },
    }


def _csa_destination(lineage: dict[str, Any]) -> str | None:
    workflow_id = lineage["workflow_id"]
    if not workflow_id:
        return None
    if workflow_id in VALID_DESTINATIONS:
        return workflow_id
    semantic = lineage["semantic_identity"]
    requested_actions = {item.upper() for item in semantic.get("requested_actions", [])}
    if "CONVERSATION" in requested_actions:
        return CONVERSATION
    if "CONSTITUTIONAL_MEMORY_CONSULTATION" in requested_actions:
        return CONSTITUTIONAL_MEMORY_CONSULTATION
    if "PROVIDER_PROPOSAL" in requested_actions:
        return PROVIDER_PROPOSAL
    if "EXECUTION_REQUEST" in requested_actions:
        return EXECUTION_REQUEST
    return None


def _normalize_canonical_semantic_lineage(source: dict[str, Any] | None) -> dict[str, Any]:
    source = source if isinstance(source, dict) else {}
    semantic_identity = source.get("semantic_identity") if isinstance(source.get("semantic_identity"), dict) else {}
    workflow_identity = source.get("workflow_identity") if isinstance(source.get("workflow_identity"), dict) else {}
    replay_identity = source.get("replay_identity") if isinstance(source.get("replay_identity"), dict) else {}
    reference = (
        source.get("canonical_semantic_artifact_reference")
        or source.get("semantic_replay_reference")
        or replay_identity.get("semantic_replay_reference")
    )
    artifact_hash = (
        source.get("canonical_semantic_artifact_hash")
        or source.get("semantic_artifact_hash")
        or source.get("artifact_hash")
    )
    workflow_id = source.get("workflow_id") or source.get("workflow_candidate") or workflow_identity.get("workflow_id")
    return {
        "canonical_semantic_artifact_reference": reference if isinstance(reference, str) else None,
        "canonical_semantic_artifact_hash": artifact_hash
        if isinstance(artifact_hash, str) and artifact_hash.startswith("sha256:")
        else None,
        "workflow_id": workflow_id if isinstance(workflow_id, str) and workflow_id.strip() else None,
        "semantic_identity": {
            "intent_family": semantic_identity.get("intent_family") if isinstance(semantic_identity.get("intent_family"), str) else None,
            "domain": semantic_identity.get("domain") if isinstance(semantic_identity.get("domain"), str) else None,
            "requested_actions": _string_list(semantic_identity.get("requested_actions")),
        },
    }


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [item.strip() for item in value if isinstance(item, str) and item.strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _classification_artifact(
    *,
    artifact_id: str,
    human_request_reference: str,
    human_prompt: str,
    classification_destination: str,
    classification_reason: str,
    classification_timestamp: str,
    replay_reference: str,
    normalized_request_reference: str | None,
    classification_status: str,
    ambiguity_status: str,
    failure_reason: str | None,
    canonical_semantic_lineage: dict[str, Any] | None,
) -> dict[str, Any]:
    if classification_destination not in VALID_DESTINATIONS:
        raise FailClosedRuntimeError("intent classification failed closed: invalid destination")
    closure = _legacy_classifier_closure_evidence(
        classification_destination=classification_destination,
        classification_reason=classification_reason,
        canonical_semantic_lineage=canonical_semantic_lineage,
        failure_reason=failure_reason,
    )
    artifact = {
        "artifact_id": _require_string(artifact_id, "artifact_id"),
        "artifact_type": "INTENT_CLASSIFICATION_ARTIFACT",
        "human_request_reference": _require_string(human_request_reference, "human_request_reference"),
        "human_prompt_hash": replay_hash({"human_prompt": _normalize_text(human_prompt, "human_prompt")}),
        "normalized_request_reference": normalized_request_reference,
        "classification_destination": classification_destination,
        "classification_reason": _require_string(classification_reason, "classification_reason"),
        "classifier_version": CLASSIFIER_VERSION,
        "classification_timestamp": _require_string(classification_timestamp, "classification_timestamp"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "ambiguity_status": ambiguity_status,
        "classification_status": classification_status,
        "failure_reason": failure_reason,
        **closure,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_classification_artifact(artifact)
    return artifact


def _failed_artifact(
    *,
    artifact_id: Any,
    human_request_reference: Any,
    human_prompt: Any,
    classification_timestamp: Any,
    replay_reference: Any,
    normalized_request_reference: str | None,
    failure_reason: str,
    canonical_semantic_lineage: dict[str, Any] | None,
) -> dict[str, Any]:
    prompt = human_prompt if isinstance(human_prompt, str) and human_prompt.strip() else "INVALID_PROMPT"
    closure = _legacy_classifier_closure_evidence(
        classification_destination=None,
        classification_reason="classification failed closed",
        canonical_semantic_lineage=canonical_semantic_lineage,
        failure_reason=failure_reason,
    )
    artifact = {
        "artifact_id": artifact_id if isinstance(artifact_id, str) and artifact_id.strip() else "INVALID_ARTIFACT_ID",
        "artifact_type": "INTENT_CLASSIFICATION_ARTIFACT",
        "human_request_reference": (
            human_request_reference
            if isinstance(human_request_reference, str) and human_request_reference.strip()
            else "INVALID_HUMAN_REQUEST_REFERENCE"
        ),
        "human_prompt_hash": replay_hash({"human_prompt": " ".join(prompt.split())}),
        "normalized_request_reference": normalized_request_reference,
        "classification_destination": None,
        "classification_reason": "classification failed closed",
        "classifier_version": CLASSIFIER_VERSION,
        "classification_timestamp": (
            classification_timestamp
            if isinstance(classification_timestamp, str) and classification_timestamp.strip()
            else "INVALID_TIMESTAMP"
        ),
        "replay_reference": replay_reference if isinstance(replay_reference, str) and replay_reference.strip() else "INVALID_REPLAY_REFERENCE",
        "ambiguity_status": "FAILED_CLOSED",
        "classification_status": FAILED_CLOSED,
        "failure_reason": failure_reason,
        **closure,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _classification_replay(artifact: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(artifact)
    replay = {
        "replay_id": f"{artifact['artifact_id']}:REPLAY",
        "artifact_reference": artifact["artifact_id"],
        "human_request_reference": artifact["human_request_reference"],
        "destination": artifact["classification_destination"],
        "classifier_version": artifact["classifier_version"],
        "classification_status": artifact["classification_status"],
        "ambiguity_status": artifact["ambiguity_status"],
        "classification_artifact_hash": artifact["artifact_hash"],
        "legacy_classifier_status": artifact.get("legacy_classifier_status"),
        "canonical_semantic_artifact_reference": artifact.get("canonical_semantic_artifact_reference"),
        "canonical_semantic_artifact_hash": artifact.get("canonical_semantic_artifact_hash"),
        "semantic_comparison_hash": artifact.get("semantic_comparison_hash"),
        "semantic_comparison_parity_status": artifact.get("semantic_comparison_parity_status"),
        "fallback_status": artifact.get("fallback_status"),
        "migration_batch_id": artifact.get("migration_batch_id"),
        "replay_reference": artifact["replay_reference"],
        "replay_visibility": "MANDATORY",
        "non_authoritative": True,
    }
    replay["artifact_hash"] = replay_hash(replay)
    return replay


def _capture(artifact: dict[str, Any], replay: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "intent_classification_artifact": deepcopy(artifact),
        "intent_classification_replay": deepcopy(replay),
        "legacy_classifier_status": artifact.get("legacy_classifier_status"),
        "canonical_semantic_artifact_hash": artifact.get("canonical_semantic_artifact_hash"),
        "semantic_comparison_hash": artifact.get("semantic_comparison_hash"),
        "semantic_comparison_parity_status": artifact.get("semantic_comparison_parity_status"),
        "fallback_status": artifact.get("fallback_status"),
        "migration_batch_id": artifact.get("migration_batch_id"),
    }
    capture["intent_classifier_capture_hash"] = replay_hash(capture)
    return capture


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("intent classification replay step ordering mismatch")
    _verify_artifact_hash(artifact)
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, artifact: dict[str, Any]) -> None:
    path = replay_dir / f"000_{REPLAY_STEPS[0]}.json"
    if not path.exists():
        try:
            _persist_step(replay_dir, 0, REPLAY_STEPS[0], artifact)
        except FailClosedRuntimeError:
            return


def _persist_failure_replay_if_possible(replay_dir: Path, replay: dict[str, Any]) -> None:
    path = replay_dir / f"001_{REPLAY_STEPS[1]}.json"
    if not path.exists():
        try:
            _persist_step(replay_dir, 1, REPLAY_STEPS[1], replay)
        except FailClosedRuntimeError:
            return


def _validate_classification_artifact(artifact: dict[str, Any]) -> None:
    status = artifact.get("classification_status")
    destination = artifact.get("classification_destination")
    if status == CLASSIFIED and destination not in VALID_DESTINATIONS:
        raise FailClosedRuntimeError("intent classification failed closed: invalid destination")
    if status == FAILED_CLOSED and destination is not None:
        raise FailClosedRuntimeError("intent classification failed closed: failed artifact cannot carry destination")
    if status not in {CLASSIFIED, FAILED_CLOSED}:
        raise FailClosedRuntimeError("intent classification failed closed: invalid status")
    forbidden = {
        "authorization_decision",
        "governance_decision",
        "execution_request",
        "provider_command",
        "worker_command",
        "memory_retrieval_result",
        "proposal_artifact",
        "correction_instruction",
    }
    present = forbidden.intersection(artifact)
    if present:
        raise FailClosedRuntimeError("intent classification failed closed: authority-bearing artifact")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("intent classification artifact must be a JSON object")
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError("intent classification artifact hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("intent classification artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("intent classification replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("intent classification replay hash mismatch")


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "intent classification failed closed"


def _normalize_text(value: Any, field_name: str) -> str:
    raw = _require_string(value, field_name)
    normalized = " ".join(raw.split())
    if not normalized:
        raise FailClosedRuntimeError(f"{field_name} is required")
    return normalized


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
