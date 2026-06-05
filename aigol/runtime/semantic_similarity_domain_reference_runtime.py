"""Semantic similarity and domain reference resolution for AiGOL."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_SEMANTIC_SIMILARITY_AND_DOMAIN_REFERENCE_RUNTIME_V1"
FINAL_CLASSIFICATION = "AIGOL_SEMANTIC_SIMILARITY_AND_DOMAIN_REFERENCE_RUNTIME_STATUS"

DOMAIN_REFERENCE_ARTIFACT_V1 = "DOMAIN_REFERENCE_ARTIFACT_V1"
SEMANTIC_SIMILARITY_ARTIFACT_V1 = "SEMANTIC_SIMILARITY_ARTIFACT_V1"
DOMAIN_ADAPTATION_CANDIDATE_ARTIFACT_V1 = "DOMAIN_ADAPTATION_CANDIDATE_ARTIFACT_V1"

DOMAIN_REFERENCE_RESOLVED = "DOMAIN_REFERENCE_RESOLVED"
SEMANTIC_SIMILARITY_RESOLVED = "SEMANTIC_SIMILARITY_RESOLVED"
DOMAIN_ADAPTATION_CANDIDATE_CREATED = "DOMAIN_ADAPTATION_CANDIDATE_CREATED"
CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"
FAILED_CLOSED = "FAILED_CLOSED"

DOMAIN_ADAPTATION = "DOMAIN_ADAPTATION"

SIMILARITY_MARKERS = (
    "similar to",
    "based on",
    "derived from",
    "version of",
    "adaptation of",
    "same as but",
    "as a basis",
)

DOMAIN_REFERENCE_REGISTRY = (
    {
        "domain_id": "TRADING",
        "aliases": ("trading", "trading domain"),
        "capability_identities": ("DECISION_VALIDATION", "EVIDENCE_NORMALIZATION", "RISK_ANALYSIS"),
        "runtime_identities": ("TRADING_DOMAIN_FOUNDATION_V1", "TRADING_DOMAIN_DECISION_VALIDATION_MODEL_V1"),
        "reference_status": "CERTIFIED_REFERENCE",
    },
    {
        "domain_id": "HEALTHCARE",
        "aliases": ("healthcare", "healthcare domain"),
        "capability_identities": ("REGULATORY_CONTEXT", "DOMAIN_FOUNDATION"),
        "runtime_identities": ("HEALTHCARE_DOMAIN_FOUNDATION_V1", "HEALTHCARE_DOMAIN_RUNTIME_V1"),
        "reference_status": "REGISTERED_REFERENCE",
    },
    {
        "domain_id": "COMPLIANCE",
        "aliases": ("compliance", "compliance domain", "regulatory compliance"),
        "capability_identities": ("REGULATORY_REQUIREMENT_VALIDATION", "COMPLIANCE_EVIDENCE_REVIEW"),
        "runtime_identities": ("AIGOL_UNKNOWN_DOMAIN_AND_CLARIFICATION_UX_V1",),
        "reference_status": "CLARIFICATION_BACKED_REFERENCE",
    },
)

REPLAY_STEPS = (
    "domain_reference_recorded",
    "semantic_similarity_recorded",
    "domain_adaptation_candidate_recorded",
    "domain_reference_resolution_returned",
)


def is_domain_reference_adaptation_prompt(human_prompt: str) -> bool:
    """Return whether a prompt asks for domain-reference adaptation."""

    try:
        return _analyze_prompt(human_prompt)["eligible"] is True
    except FailClosedRuntimeError:
        return False


def run_semantic_similarity_domain_reference_resolution(
    *,
    resolution_id: str,
    prompt_id: str,
    human_prompt: str,
    canonical_chain_id: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Resolve semantic domain references and persist replay-visible artifacts."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        analysis = _analyze_prompt(human_prompt)
        if analysis["eligible"] is not True:
            raise FailClosedRuntimeError("semantic similarity domain reference failed closed: prompt is not eligible")
        domain_reference = _domain_reference_artifact(
            resolution_id=resolution_id,
            prompt_id=prompt_id,
            human_prompt=human_prompt,
            canonical_chain_id=canonical_chain_id,
            created_at=created_at,
            replay_reference=str(replay_path),
            analysis=analysis,
        )
        similarity = _semantic_similarity_artifact(
            resolution_id=resolution_id,
            domain_reference=domain_reference,
            analysis=analysis,
            created_at=created_at,
            replay_reference=str(replay_path),
        )
        candidate = _domain_adaptation_candidate_artifact(
            resolution_id=resolution_id,
            domain_reference=domain_reference,
            similarity=similarity,
            analysis=analysis,
            created_at=created_at,
            replay_reference=str(replay_path),
        )
        returned = _returned_artifact(domain_reference, similarity, candidate)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], domain_reference)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], similarity)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], candidate)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], returned)
        return _capture(domain_reference, similarity, candidate, returned, replay_path)
    except Exception as exc:
        failure_reason = str(exc) if isinstance(exc, FailClosedRuntimeError) else "semantic similarity domain reference failed closed"
        domain_reference = _failed_domain_reference_artifact(
            resolution_id=resolution_id,
            prompt_id=prompt_id,
            human_prompt=human_prompt,
            canonical_chain_id=canonical_chain_id,
            created_at=created_at,
            replay_reference=str(replay_path),
            failure_reason=failure_reason,
        )
        similarity = _failed_similarity_artifact(
            resolution_id=resolution_id,
            domain_reference=domain_reference,
            created_at=created_at,
            replay_reference=str(replay_path),
            failure_reason=failure_reason,
        )
        candidate = _failed_candidate_artifact(
            resolution_id=resolution_id,
            domain_reference=domain_reference,
            similarity=similarity,
            created_at=created_at,
            replay_reference=str(replay_path),
            failure_reason=failure_reason,
        )
        returned = _returned_artifact(domain_reference, similarity, candidate)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], domain_reference)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], similarity)
        _persist_failure_if_possible(replay_path, 2, REPLAY_STEPS[2], candidate)
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], returned)
        return _capture(domain_reference, similarity, candidate, returned, replay_path)


def reconstruct_semantic_similarity_domain_reference_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct semantic similarity and domain reference replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("semantic similarity domain reference replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("semantic similarity domain reference artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    reference = wrappers[0]["artifact"]
    similarity = wrappers[1]["artifact"]
    candidate = wrappers[2]["artifact"]
    returned = wrappers[3]["artifact"]
    if similarity.get("domain_reference_hash") != reference["artifact_hash"]:
        raise FailClosedRuntimeError("semantic similarity domain reference hash mismatch")
    if candidate.get("semantic_similarity_hash") != similarity["artifact_hash"]:
        raise FailClosedRuntimeError("domain adaptation candidate similarity hash mismatch")
    if returned.get("domain_adaptation_candidate_hash") != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("domain adaptation returned hash mismatch")
    return {
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "resolution_status": returned["resolution_status"],
        "source_domain": candidate.get("source_domain"),
        "target_domain": candidate.get("target_domain"),
        "operation": candidate.get("operation"),
        "missing_information": deepcopy(candidate.get("missing_information", [])),
        "replay_visible": True,
        "lineage_bound": True,
        "replay_artifact_count": len(wrappers),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "domain_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "approval_bypassed": False,
        "replay_hash": replay_hash(wrappers),
    }


def render_domain_reference_resolution_summary(capture: dict[str, Any]) -> str:
    candidate = capture.get("domain_adaptation_candidate_artifact") or {}
    lines = [
        f"Reference Domain: {candidate.get('source_domain')}",
        f"Target Domain: {candidate.get('target_domain')}",
        f"Operation: {candidate.get('operation')}",
        f"resolution_status: {capture.get('resolution_status')}",
    ]
    if candidate.get("missing_information"):
        lines.append("missing_information:")
        lines.extend(f"* {item}" for item in candidate["missing_information"])
    lines.extend(
        [
            f"replay_reference: {capture.get('semantic_similarity_domain_reference_replay_reference')}",
            f"provider_invoked: {capture.get('provider_invoked')}",
            f"worker_invoked: {capture.get('worker_invoked')}",
            f"execution_requested: {capture.get('execution_requested')}",
        ]
    )
    return "\n".join(lines)


def _analyze_prompt(human_prompt: str) -> dict[str, Any]:
    prompt = _require_string(human_prompt, "human_prompt")
    normalized = prompt.lower().strip().rstrip(".?!")
    marker = _similarity_marker(normalized)
    if marker is None:
        return {"eligible": False}
    source = _source_domain(normalized)
    if source is None:
        raise FailClosedRuntimeError("semantic similarity domain reference failed closed: missing reference domain")
    target = _target_domain(normalized, source["domain_id"])
    missing = []
    if target is None:
        missing.append("target domain")
    status = CLARIFICATION_REQUIRED if missing else DOMAIN_ADAPTATION_CANDIDATE_CREATED
    return {
        "eligible": True,
        "source_domain": source,
        "target_domain": target,
        "similarity_marker": marker,
        "operation": DOMAIN_ADAPTATION,
        "adaptation_intent": _adaptation_intent(normalized, source["domain_id"], target),
        "similarity_reasoning": _similarity_reasoning(marker, source["domain_id"], target),
        "missing_information": missing,
        "candidate_status": status,
    }


def _similarity_marker(normalized: str) -> str | None:
    for marker in SIMILARITY_MARKERS:
        if marker in normalized:
            return marker
    return None


def _source_domain(normalized: str) -> dict[str, Any] | None:
    for domain in DOMAIN_REFERENCE_REGISTRY:
        for alias in domain["aliases"]:
            if alias in normalized:
                if _is_target_only_occurrence(normalized, alias):
                    continue
                return deepcopy(domain)
    return None


def _target_domain(normalized: str, source_domain_id: str) -> str | None:
    explicit = (
        (r"focused on ([a-z ]+)", 1),
        (r"for a ([a-z ]+?) domain", 1),
        (r"for ([a-z ]+?) domain", 1),
        (r"create a ([a-z ]+?) version", 1),
        (r"use .+ as a basis for a ([a-z ]+?) domain", 1),
        (r"use .+ as a basis for ([a-z ]+?) domain", 1),
    )
    for pattern, group in explicit:
        match = re.search(pattern, normalized)
        if match:
            candidate = _normalize_domain_id(match.group(group))
            if candidate and candidate != source_domain_id:
                return candidate
    for domain in DOMAIN_REFERENCE_REGISTRY:
        domain_id = domain["domain_id"]
        if domain_id == source_domain_id:
            continue
        for alias in domain["aliases"]:
            if alias in normalized:
                return domain_id
    return None


def _is_target_only_occurrence(normalized: str, alias: str) -> bool:
    return normalized.startswith(f"create a {alias} version") or normalized.startswith(f"create an {alias} version")


def _normalize_domain_id(value: str) -> str | None:
    words = [word for word in re.split(r"[^a-z0-9]+", value.lower()) if word and word not in {"new", "the"}]
    if not words:
        return None
    return "_".join(words).upper()


def _adaptation_intent(normalized: str, source_domain: str, target_domain: str | None) -> str:
    if target_domain:
        return f"Adapt {source_domain} domain semantics for {target_domain}."
    return f"Adapt {source_domain} domain semantics for an operator-specified target domain."


def _similarity_reasoning(marker: str, source_domain: str, target_domain: str | None) -> list[str]:
    reasoning = [
        f"Detected semantic similarity marker: {marker}.",
        f"Resolved reference domain identity: {source_domain}.",
    ]
    if target_domain:
        reasoning.append(f"Resolved target domain identity: {target_domain}.")
    else:
        reasoning.append("Target domain is missing and requires clarification.")
    reasoning.append("Candidate is non-authoritative and requires downstream governed approval before implementation.")
    return reasoning


def _domain_reference_artifact(
    *,
    resolution_id: str,
    prompt_id: str,
    human_prompt: str,
    canonical_chain_id: str,
    created_at: str,
    replay_reference: str,
    analysis: dict[str, Any],
) -> dict[str, Any]:
    source = analysis["source_domain"]
    artifact = {
        "artifact_type": DOMAIN_REFERENCE_ARTIFACT_V1,
        "milestone_id": MILESTONE_ID,
        "domain_reference_id": f"{_require_string(resolution_id, 'resolution_id')}:DOMAIN-REFERENCE",
        "prompt_id": _require_string(prompt_id, "prompt_id"),
        "human_prompt_hash": replay_hash(_require_string(human_prompt, "human_prompt")),
        "canonical_chain_id": _require_string(canonical_chain_id, "canonical_chain_id"),
        "reference_status": DOMAIN_REFERENCE_RESOLVED,
        "referenced_domain_identity": source["domain_id"],
        "referenced_capability_identities": list(source["capability_identities"]),
        "referenced_runtime_identities": list(source["runtime_identities"]),
        "reference_registry_status": source["reference_status"],
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        **_authority_flags(),
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _semantic_similarity_artifact(
    *,
    resolution_id: str,
    domain_reference: dict[str, Any],
    analysis: dict[str, Any],
    created_at: str,
    replay_reference: str,
) -> dict[str, Any]:
    _verify_artifact_hash(domain_reference)
    artifact = {
        "artifact_type": SEMANTIC_SIMILARITY_ARTIFACT_V1,
        "milestone_id": MILESTONE_ID,
        "semantic_similarity_id": f"{_require_string(resolution_id, 'resolution_id')}:SEMANTIC-SIMILARITY",
        "domain_reference_hash": domain_reference["artifact_hash"],
        "similarity_status": SEMANTIC_SIMILARITY_RESOLVED,
        "similarity_marker": analysis["similarity_marker"],
        "operation": analysis["operation"],
        "similarity_reasoning": list(analysis["similarity_reasoning"]),
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        **_authority_flags(),
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _domain_adaptation_candidate_artifact(
    *,
    resolution_id: str,
    domain_reference: dict[str, Any],
    similarity: dict[str, Any],
    analysis: dict[str, Any],
    created_at: str,
    replay_reference: str,
) -> dict[str, Any]:
    _verify_artifact_hash(domain_reference)
    _verify_artifact_hash(similarity)
    artifact = {
        "artifact_type": DOMAIN_ADAPTATION_CANDIDATE_ARTIFACT_V1,
        "milestone_id": MILESTONE_ID,
        "domain_adaptation_candidate_id": f"{_require_string(resolution_id, 'resolution_id')}:DOMAIN-ADAPTATION-CANDIDATE",
        "domain_reference_hash": domain_reference["artifact_hash"],
        "semantic_similarity_hash": similarity["artifact_hash"],
        "candidate_status": analysis["candidate_status"],
        "source_domain": analysis["source_domain"]["domain_id"],
        "target_domain": analysis["target_domain"],
        "operation": analysis["operation"],
        "adaptation_intent": analysis["adaptation_intent"],
        "similarity_reasoning": list(analysis["similarity_reasoning"]),
        "continuity_references": {
            "domain_reference_id": domain_reference["domain_reference_id"],
            "semantic_similarity_id": similarity["semantic_similarity_id"],
            "canonical_chain_id": domain_reference["canonical_chain_id"],
        },
        "missing_information": list(analysis["missing_information"]),
        "clarification_required": bool(analysis["missing_information"]),
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "lineage_bound": True,
        **_authority_flags(),
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(reference: dict[str, Any], similarity: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(reference)
    _verify_artifact_hash(similarity)
    _verify_artifact_hash(candidate)
    artifact = {
        "event_type": "SEMANTIC_SIMILARITY_DOMAIN_REFERENCE_RETURNED",
        "milestone_id": MILESTONE_ID,
        "domain_reference_hash": reference["artifact_hash"],
        "semantic_similarity_hash": similarity["artifact_hash"],
        "domain_adaptation_candidate_hash": candidate["artifact_hash"],
        "resolution_status": candidate["candidate_status"],
        "source_domain": candidate["source_domain"],
        "target_domain": candidate["target_domain"],
        "operation": candidate["operation"],
        "replay_visible": True,
        **_authority_flags(),
        "failure_reason": candidate["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_domain_reference_artifact(
    *,
    resolution_id: str,
    prompt_id: str,
    human_prompt: Any,
    canonical_chain_id: str,
    created_at: str,
    replay_reference: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": DOMAIN_REFERENCE_ARTIFACT_V1,
        "milestone_id": MILESTONE_ID,
        "domain_reference_id": f"{resolution_id}:DOMAIN-REFERENCE",
        "prompt_id": prompt_id if isinstance(prompt_id, str) else None,
        "human_prompt_hash": replay_hash(human_prompt) if isinstance(human_prompt, str) else None,
        "canonical_chain_id": canonical_chain_id if isinstance(canonical_chain_id, str) else None,
        "reference_status": FAILED_CLOSED,
        "referenced_domain_identity": None,
        "referenced_capability_identities": [],
        "referenced_runtime_identities": [],
        "reference_registry_status": None,
        "created_at": created_at if isinstance(created_at, str) else "",
        "replay_reference": replay_reference,
        "replay_visible": True,
        **_authority_flags(),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_similarity_artifact(
    *,
    resolution_id: str,
    domain_reference: dict[str, Any],
    created_at: str,
    replay_reference: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": SEMANTIC_SIMILARITY_ARTIFACT_V1,
        "milestone_id": MILESTONE_ID,
        "semantic_similarity_id": f"{resolution_id}:SEMANTIC-SIMILARITY",
        "domain_reference_hash": domain_reference["artifact_hash"],
        "similarity_status": FAILED_CLOSED,
        "similarity_marker": None,
        "operation": None,
        "similarity_reasoning": [],
        "created_at": created_at if isinstance(created_at, str) else "",
        "replay_reference": replay_reference,
        "replay_visible": True,
        **_authority_flags(),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_candidate_artifact(
    *,
    resolution_id: str,
    domain_reference: dict[str, Any],
    similarity: dict[str, Any],
    created_at: str,
    replay_reference: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": DOMAIN_ADAPTATION_CANDIDATE_ARTIFACT_V1,
        "milestone_id": MILESTONE_ID,
        "domain_adaptation_candidate_id": f"{resolution_id}:DOMAIN-ADAPTATION-CANDIDATE",
        "domain_reference_hash": domain_reference["artifact_hash"],
        "semantic_similarity_hash": similarity["artifact_hash"],
        "candidate_status": FAILED_CLOSED,
        "source_domain": None,
        "target_domain": None,
        "operation": None,
        "adaptation_intent": None,
        "similarity_reasoning": [],
        "continuity_references": {},
        "missing_information": [],
        "clarification_required": False,
        "created_at": created_at if isinstance(created_at, str) else "",
        "replay_reference": replay_reference,
        "replay_visible": True,
        "lineage_bound": True,
        **_authority_flags(),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    reference: dict[str, Any],
    similarity: dict[str, Any],
    candidate: dict[str, Any],
    returned: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "command": "aigol conversation",
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "response_status": returned["resolution_status"],
        "response_source": "SEMANTIC_SIMILARITY_DOMAIN_REFERENCE_RUNTIME",
        "resolution_status": returned["resolution_status"],
        "domain_reference_artifact": deepcopy(reference),
        "semantic_similarity_artifact": deepcopy(similarity),
        "domain_adaptation_candidate_artifact": deepcopy(candidate),
        "domain_reference_returned": deepcopy(returned),
        "semantic_similarity_domain_reference_replay_reference": str(replay_path),
        "conversation_replay_reference": str(replay_path),
        "canonical_chain_id": reference.get("canonical_chain_id"),
        "current_chain_id": reference.get("canonical_chain_id"),
        "latest_chain_id": reference.get("canonical_chain_id"),
        "response_text": "",
        "fail_closed": returned["resolution_status"] == FAILED_CLOSED,
        "failure_reason": returned.get("failure_reason"),
        **_authority_flags(),
    }
    capture["response_text"] = render_domain_reference_resolution_summary(capture)
    capture["semantic_similarity_domain_reference_hash"] = replay_hash(capture)
    return capture


def _authority_flags() -> dict[str, bool]:
    return {
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "domain_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "approval_bypassed": False,
    }


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("semantic similarity domain reference replay step ordering mismatch")
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
            raise FailClosedRuntimeError("semantic similarity domain reference failed closed: replay already exists")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("semantic similarity domain reference artifact hash is required")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("semantic similarity domain reference artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("semantic similarity domain reference replay hash is required")
    expected_input = deepcopy(wrapper)
    expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("semantic similarity domain reference replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()
