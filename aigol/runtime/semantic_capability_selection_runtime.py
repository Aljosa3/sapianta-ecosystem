"""Deterministic, non-invoking semantic selection for certified capabilities."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
from typing import Any

from aigol.runtime.certified_capability_invocation_binding_runtime import (
    PLATFORM_CHANGE_IMPACT_ANALYSIS,
    PLATFORM_CHANGE_NORMALIZATION,
    PLATFORM_VALIDATION_PLANNING,
    certified_capability_invocation_adapters,
    certified_capability_semantic_descriptors,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_certification_registry import (
    CERTIFIED_STATES,
    PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY_VERSION,
    platform_capability_certification_registry,
)
from aigol.runtime.platform_project_objective_inference import (
    OBJECTIVE_SUFFICIENT,
    validate_platform_project_objective,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


SEMANTIC_CAPABILITY_SELECTION_RUNTIME_VERSION = (
    "G29_02_CANONICAL_SEMANTIC_CAPABILITY_SELECTION_BINDING_V1"
)
SEMANTIC_CAPABILITY_SELECTION_ARTIFACT_V1 = "SEMANTIC_CAPABILITY_SELECTION_ARTIFACT_V1"
SEMANTIC_CAPABILITY_CLARIFICATION_ARTIFACT_V1 = (
    "SEMANTIC_CAPABILITY_CLARIFICATION_ARTIFACT_V1"
)

CAPABILITY_SELECTED = "CAPABILITY_SELECTED"
CAPABILITY_CLARIFICATION_REQUIRED = "CAPABILITY_CLARIFICATION_REQUIRED"
NO_ADMISSIBLE_CAPABILITY = "NO_ADMISSIBLE_CAPABILITY"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "project_objective_source_recorded",
    "invocation_eligible_candidates_recorded",
    "semantic_scoring_evidence_recorded",
    "selection_classification_recorded",
    "semantic_capability_selection_recorded",
    "semantic_capability_selection_returned",
)

BOUNDARY_FLAGS = {
    "platform_core_authority": True,
    "human_interface_authority": False,
    "selection_treated_as_authorization": False,
    "authorizes_execution": False,
    "capability_invoked": False,
    "worker_invoked": False,
    "provider_invoked": False,
    "repository_mutated": False,
    "dynamic_import_used": False,
    "implementation_owner_inspected": False,
    "new_capability_registry_created": False,
    "platform_knowledge_semantics_modified": False,
    "g28_invocation_binding_modified": False,
}

SUPPORTED_CAPABILITIES = (
    PLATFORM_CHANGE_IMPACT_ANALYSIS,
    PLATFORM_CHANGE_NORMALIZATION,
    PLATFORM_VALIDATION_PLANNING,
)


def semantic_capability_selection_fingerprints() -> dict[str, str]:
    """Return deterministic fingerprints callers bind into selection input."""

    adapters = certified_capability_invocation_adapters()
    descriptors = certified_capability_semantic_descriptors()
    return {
        "adapter_metadata_fingerprint": replay_hash(adapters),
        "semantic_descriptor_fingerprint": replay_hash(descriptors),
    }


def select_semantic_capability(
    *,
    selection_id: str,
    session_id: str,
    project_objective_artifact: dict[str, Any],
    project_objective_reference: str,
    project_objective_hash: str,
    certification_registry_state: dict[str, dict[str, Any]],
    certification_registry_fingerprint: str,
    invocation_adapter_metadata: dict[str, dict[str, Any]],
    invocation_adapter_metadata_fingerprint: str,
    available_input_artifact_types: list[str] | tuple[str, ...],
    replay_dir: str | Path,
    candidate_discovery_evidence: dict[str, Any] | None = None,
    candidate_discovery_reference: str | None = None,
    candidate_discovery_hash: str | None = None,
    created_at: str = "2026-07-13T00:00:00Z",
) -> dict[str, Any]:
    """Select one G28-eligible capability or produce one clarification.

    This function records selection evidence only. It cannot invoke an adapter.
    """

    path = Path(replay_dir)
    objective: dict[str, Any] = {}
    try:
        _ensure_replay_available(path)
        identifier = _require_string(selection_id, "selection_id")
        session = _require_string(session_id, "session_id")
        objective_reference = _require_string(
            project_objective_reference, "project_objective_reference"
        )
        objective_hash = _require_hash(project_objective_hash, "project_objective_hash")
        timestamp = _require_string(created_at, "created_at")
        objective = validate_platform_project_objective(project_objective_artifact)
        if objective["artifact_hash"] != objective_hash:
            raise FailClosedRuntimeError(
                "semantic capability selection failed closed: objective hash mismatch"
            )
        if objective.get("objective_status") != OBJECTIVE_SUFFICIENT:
            raise FailClosedRuntimeError(
                "semantic capability selection failed closed: objective is not sufficient"
            )
        if objective.get("objective_sufficient") is not True:
            raise FailClosedRuntimeError(
                "semantic capability selection failed closed: objective sufficiency invalid"
            )
        discovery = _validated_candidate_discovery(
            objective=objective,
            evidence=candidate_discovery_evidence,
            reference=candidate_discovery_reference,
            expected_hash=candidate_discovery_hash,
        )
        registry = _validated_registry_state(
            certification_registry_state,
            certification_registry_fingerprint,
        )
        adapters = _validated_adapter_metadata(
            invocation_adapter_metadata,
            invocation_adapter_metadata_fingerprint,
        )
        descriptors = _validated_semantic_descriptors()
        input_types = _normalized_input_types(available_input_artifact_types)

        candidates = _score_candidates(
            objective=objective,
            registry=registry,
            adapters=adapters,
            descriptors=descriptors,
            available_input_types=input_types,
        )
        decision = _selection_decision(candidates)
        clarification = _clarification_artifact(
            selection_id=identifier,
            objective=objective,
            candidates=candidates,
            decision=decision,
        )

        source_record = _artifact(
            "SEMANTIC_CAPABILITY_PROJECT_OBJECTIVE_SOURCE_ARTIFACT_V1",
            {
                "selection_id": identifier,
                "session_id": session,
                "project_objective_reference": objective_reference,
                "project_objective_hash": objective_hash,
                "project_objective_artifact": objective,
                "candidate_discovery_reference": discovery["reference"],
                "candidate_discovery_hash": discovery["hash"],
                "candidate_discovery_evidence": discovery["evidence"],
            },
        )
        candidate_record = _artifact(
            "SEMANTIC_CAPABILITY_INVOCATION_ELIGIBLE_CANDIDATES_ARTIFACT_V1",
            {
                "selection_id": identifier,
                "objective_source_hash": source_record["artifact_hash"],
                "certification_registry_version": (
                    PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY_VERSION
                ),
                "certification_registry_fingerprint": certification_registry_fingerprint,
                "certification_registry_state": registry,
                "invocation_adapter_metadata_fingerprint": (
                    invocation_adapter_metadata_fingerprint
                ),
                "invocation_adapter_metadata": adapters,
                "semantic_descriptor_fingerprint": replay_hash(descriptors),
                "semantic_descriptors": descriptors,
                "available_input_artifact_types": input_types,
                "ordered_candidates": candidates,
            },
        )
        scoring_record = _artifact(
            "SEMANTIC_CAPABILITY_SCORING_EVIDENCE_ARTIFACT_V1",
            {
                "selection_id": identifier,
                "candidate_set_hash": candidate_record["artifact_hash"],
                "scoring_algorithm": _scoring_algorithm(),
                "normalized_objective_evidence": _objective_text(objective),
                "ordered_candidate_scores": [
                    {
                        "capability_identifier": item["capability_identifier"],
                        "score": item["score"],
                        "admissible": item["admissible"],
                        "positive_match_evidence": item["positive_match_evidence"],
                        "exclusion_evidence": item["exclusion_evidence"],
                        "unresolved_semantic_slots": item["unresolved_semantic_slots"],
                    }
                    for item in candidates
                ],
            },
        )
        classification_record = _artifact(
            "SEMANTIC_CAPABILITY_SELECTION_CLASSIFICATION_ARTIFACT_V1",
            {
                "selection_id": identifier,
                "scoring_evidence_hash": scoring_record["artifact_hash"],
                **decision,
                "clarification_artifact_hash": (
                    clarification.get("artifact_hash") if clarification else None
                ),
            },
        )
        selection = _selection_artifact(
            selection_id=identifier,
            session_id=session,
            created_at=timestamp,
            objective_reference=objective_reference,
            objective_hash=objective_hash,
            discovery=discovery,
            registry_fingerprint=certification_registry_fingerprint,
            adapter_fingerprint=invocation_adapter_metadata_fingerprint,
            descriptor_fingerprint=replay_hash(descriptors),
            candidates=candidates,
            decision=decision,
            clarification=clarification,
            source_hash=source_record["artifact_hash"],
            candidate_hash=candidate_record["artifact_hash"],
            scoring_hash=scoring_record["artifact_hash"],
            classification_hash=classification_record["artifact_hash"],
        )
        returned = _returned_artifact(selection)
        artifacts = (
            source_record,
            candidate_record,
            scoring_record,
            classification_record,
            selection,
            returned,
        )
        for index, (step, artifact) in enumerate(zip(REPLAY_STEPS, artifacts, strict=True)):
            _persist_step(path, index, step, artifact)
        return _capture(selection, returned, clarification, path)
    except Exception as exc:
        reason = str(exc) or exc.__class__.__name__
        result = _failed_selection_artifact(
            selection_id=selection_id,
            session_id=session_id,
            created_at=created_at,
            objective_reference=project_objective_reference,
            objective_hash=(
                objective.get("artifact_hash")
                if isinstance(objective, dict)
                else project_objective_hash
            ),
            failure_reason=reason,
        )
        returned = _returned_artifact(result)
        _persist_failure_if_possible(path, result, returned)
        return _capture(result, returned, None, path)


def validate_semantic_capability_selection_artifact(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Validate one canonical selection artifact without invoking anything."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("semantic capability selection artifact must be an object")
    if artifact.get("artifact_type") != SEMANTIC_CAPABILITY_SELECTION_ARTIFACT_V1:
        raise FailClosedRuntimeError("semantic capability selection artifact type mismatch")
    if artifact.get("runtime_version") != SEMANTIC_CAPABILITY_SELECTION_RUNTIME_VERSION:
        raise FailClosedRuntimeError("semantic capability selection runtime version mismatch")
    _verify_artifact_hash(artifact, "semantic capability selection artifact")
    status = artifact.get("selection_status")
    if status not in {
        CAPABILITY_SELECTED,
        CAPABILITY_CLARIFICATION_REQUIRED,
        NO_ADMISSIBLE_CAPABILITY,
        FAILED_CLOSED,
    }:
        raise FailClosedRuntimeError("semantic capability selection status invalid")
    for field, expected in BOUNDARY_FLAGS.items():
        if artifact.get(field) is not expected:
            raise FailClosedRuntimeError("semantic capability selection boundary invalid")
    selected = artifact.get("selected_capability_identifier")
    if status == CAPABILITY_SELECTED:
        if selected not in SUPPORTED_CAPABILITIES:
            raise FailClosedRuntimeError("selected capability is not invocation eligible")
        if artifact.get("invocation_eligible") is not True:
            raise FailClosedRuntimeError("selected capability invocation eligibility missing")
        if artifact.get("clarification_required") is not False:
            raise FailClosedRuntimeError("selected capability cannot require clarification")
        if artifact.get("ready_for_g28_invocation") is not True:
            raise FailClosedRuntimeError("selected capability is not ready for G28")
        candidates = artifact.get("ordered_candidate_records")
        if not isinstance(candidates, list):
            raise FailClosedRuntimeError("semantic capability candidate records missing")
        selected_records = [
            item
            for item in candidates
            if isinstance(item, dict)
            and item.get("capability_identifier") == selected
            and item.get("admissible") is True
        ]
        if len(selected_records) != 1:
            raise FailClosedRuntimeError("selected capability candidate evidence invalid")
        selected_record = selected_records[0]
        if artifact.get("required_canonical_input_artifact_types") != selected_record.get(
            "accepted_canonical_input_artifact_types"
        ):
            raise FailClosedRuntimeError("selected capability input artifact handoff mismatch")
        if artifact.get("required_canonical_input_fields") != selected_record.get(
            "required_canonical_input_fields"
        ):
            raise FailClosedRuntimeError("selected capability input field handoff mismatch")
    else:
        if selected is not None or artifact.get("ready_for_g28_invocation") is not False:
            raise FailClosedRuntimeError("non-selected result cannot identify a capability")
    if status in {CAPABILITY_CLARIFICATION_REQUIRED, NO_ADMISSIBLE_CAPABILITY}:
        clarification = artifact.get("clarification_artifact")
        if not isinstance(clarification, dict):
            raise FailClosedRuntimeError("semantic capability clarification missing")
        _verify_artifact_hash(clarification, "semantic capability clarification")
        if clarification.get("asks_exactly_one_question") is not True:
            raise FailClosedRuntimeError("semantic capability clarification must ask one question")
        if artifact.get("clarification_artifact_hash") != clarification["artifact_hash"]:
            raise FailClosedRuntimeError("semantic capability clarification linkage mismatch")
    return deepcopy(artifact)


def reconstruct_semantic_capability_selection_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and reproduce a complete semantic selection Replay."""

    path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    artifacts: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("semantic capability selection replay ordering mismatch")
        _verify_named_hash(wrapper, "replay_hash", "semantic capability replay hash mismatch")
        artifact = wrapper.get("artifact")
        _verify_artifact_hash(artifact, "semantic capability replay artifact")
        wrappers.append(wrapper)
        artifacts.append(artifact)

    source, candidate_set, scoring, classification, selection, returned = artifacts
    objective = validate_platform_project_objective(source.get("project_objective_artifact"))
    if source.get("project_objective_hash") != objective["artifact_hash"]:
        raise FailClosedRuntimeError("semantic capability replay objective lineage mismatch")
    if candidate_set.get("objective_source_hash") != source["artifact_hash"]:
        raise FailClosedRuntimeError("semantic capability replay candidate lineage mismatch")
    registry = _validated_registry_state(
        candidate_set.get("certification_registry_state"),
        candidate_set.get("certification_registry_fingerprint"),
    )
    adapters = _validated_adapter_metadata(
        candidate_set.get("invocation_adapter_metadata"),
        candidate_set.get("invocation_adapter_metadata_fingerprint"),
    )
    descriptors = candidate_set.get("semantic_descriptors")
    if not isinstance(descriptors, dict) or replay_hash(descriptors) != candidate_set.get(
        "semantic_descriptor_fingerprint"
    ):
        raise FailClosedRuntimeError("semantic capability replay descriptor fingerprint mismatch")
    if descriptors != _validated_semantic_descriptors():
        raise FailClosedRuntimeError("semantic capability replay descriptor drift")
    reproduced = _score_candidates(
        objective=objective,
        registry=registry,
        adapters=adapters,
        descriptors=descriptors,
        available_input_types=_normalized_input_types(
            candidate_set.get("available_input_artifact_types")
        ),
    )
    if reproduced != candidate_set.get("ordered_candidates"):
        raise FailClosedRuntimeError("semantic capability replay candidate scores mismatch")
    if scoring.get("candidate_set_hash") != candidate_set["artifact_hash"]:
        raise FailClosedRuntimeError("semantic capability replay scoring lineage mismatch")
    expected_scores = [
        {
            "capability_identifier": item["capability_identifier"],
            "score": item["score"],
            "admissible": item["admissible"],
            "positive_match_evidence": item["positive_match_evidence"],
            "exclusion_evidence": item["exclusion_evidence"],
            "unresolved_semantic_slots": item["unresolved_semantic_slots"],
        }
        for item in reproduced
    ]
    if scoring.get("ordered_candidate_scores") != expected_scores:
        raise FailClosedRuntimeError("semantic capability replay scoring evidence mismatch")
    decision = _selection_decision(reproduced)
    for field, value in decision.items():
        if classification.get(field) != value:
            raise FailClosedRuntimeError("semantic capability replay classification mismatch")
    validated = validate_semantic_capability_selection_artifact(selection)
    selection_links = {
        "project_objective_hash": objective["artifact_hash"],
        "candidate_discovery_reference": source.get("candidate_discovery_reference"),
        "candidate_discovery_hash": source.get("candidate_discovery_hash"),
        "certification_registry_fingerprint": candidate_set.get(
            "certification_registry_fingerprint"
        ),
        "invocation_adapter_metadata_fingerprint": candidate_set.get(
            "invocation_adapter_metadata_fingerprint"
        ),
        "semantic_descriptor_fingerprint": candidate_set.get(
            "semantic_descriptor_fingerprint"
        ),
        "objective_source_record_hash": source["artifact_hash"],
        "candidate_set_record_hash": candidate_set["artifact_hash"],
        "scoring_evidence_record_hash": scoring["artifact_hash"],
        "classification_record_hash": classification["artifact_hash"],
        "ordered_candidate_records": reproduced,
        "selected_capability_identifier": decision["selected_capability_identifier"],
        "selection_status": decision["selection_status"],
        "unique_highest_score": decision["unique_highest_score"],
        "clarification_required": decision["clarification_required"],
        "fail_closed_reason": decision["fail_closed_reason"],
    }
    for field, expected in selection_links.items():
        if validated.get(field) != expected:
            raise FailClosedRuntimeError(
                "semantic capability replay selection evidence mismatch"
            )
    if validated.get("classification_record_hash") != classification["artifact_hash"]:
        raise FailClosedRuntimeError("semantic capability replay selection lineage mismatch")
    clarification = validated.get("clarification_artifact")
    clarification_hash = clarification.get("artifact_hash") if isinstance(clarification, dict) else None
    if classification.get("clarification_artifact_hash") != clarification_hash:
        raise FailClosedRuntimeError("semantic capability replay clarification linkage mismatch")
    if returned.get("selection_artifact_hash") != selection["artifact_hash"]:
        raise FailClosedRuntimeError("semantic capability replay return linkage mismatch")
    if returned.get("selection_status") != selection["selection_status"]:
        raise FailClosedRuntimeError("semantic capability replay return status mismatch")
    if returned.get("selected_capability_identifier") != selection.get(
        "selected_capability_identifier"
    ):
        raise FailClosedRuntimeError("semantic capability replay return capability mismatch")
    if returned.get("capability_invoked") is not False:
        raise FailClosedRuntimeError("semantic capability replay recorded unauthorized invocation")
    return {
        "selection_id": selection["selection_id"],
        "session_id": selection["session_id"],
        "selection_status": selection["selection_status"],
        "selected_capability_identifier": selection["selected_capability_identifier"],
        "ready_for_g28_invocation": selection["ready_for_g28_invocation"],
        "clarification_required": selection["clarification_required"],
        "artifact_hash": selection["artifact_hash"],
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
        **deepcopy(BOUNDARY_FLAGS),
    }


def _validated_candidate_discovery(
    *,
    objective: dict[str, Any],
    evidence: Any,
    reference: Any,
    expected_hash: Any,
) -> dict[str, Any]:
    if evidence is None:
        if reference is not None or expected_hash is not None:
            raise FailClosedRuntimeError(
                "semantic capability selection failed closed: incomplete candidate discovery lineage"
            )
        return {"evidence": None, "reference": None, "hash": None}
    if not isinstance(evidence, dict):
        raise FailClosedRuntimeError(
            "semantic capability selection failed closed: candidate discovery must be an object"
        )
    if evidence.get("artifact_type") != "PLATFORM_CORE_CANDIDATE_CAPABILITY_DISCOVERY_ARTIFACT_V1":
        raise FailClosedRuntimeError(
            "semantic capability selection failed closed: candidate discovery identity mismatch"
        )
    _verify_artifact_hash(evidence, "semantic capability candidate discovery")
    discovery_hash = _require_hash(expected_hash, "candidate_discovery_hash")
    if evidence["artifact_hash"] != discovery_hash:
        raise FailClosedRuntimeError(
            "semantic capability selection failed closed: candidate discovery hash mismatch"
        )
    discovery_reference = _require_string(reference, "candidate_discovery_reference")
    if evidence.get("candidate_capabilities") != objective.get("candidate_capabilities"):
        raise FailClosedRuntimeError(
            "semantic capability selection failed closed: candidate discovery lineage mismatch"
        )
    if evidence.get("human_interface_authority") is not False or evidence.get("replay_visible") is not True:
        raise FailClosedRuntimeError(
            "semantic capability selection failed closed: candidate discovery boundary invalid"
        )
    return {
        "evidence": deepcopy(evidence),
        "reference": discovery_reference,
        "hash": discovery_hash,
    }


def _validated_registry_state(state: Any, fingerprint: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(state, dict) or not state:
        raise FailClosedRuntimeError(
            "semantic capability selection failed closed: certification registry state required"
        )
    expected = _require_hash(fingerprint, "certification_registry_fingerprint")
    if replay_hash(state) != expected:
        raise FailClosedRuntimeError(
            "semantic capability selection failed closed: certification registry fingerprint mismatch"
        )
    if replay_hash(state) != replay_hash(platform_capability_certification_registry()):
        raise FailClosedRuntimeError(
            "semantic capability selection failed closed: certification registry state drift"
        )
    validated: dict[str, dict[str, Any]] = {}
    for capability_id in sorted(state):
        record = state[capability_id]
        if not isinstance(record, dict):
            raise FailClosedRuntimeError(
                "semantic capability selection failed closed: registry record invalid"
            )
        if record.get("capability_identifier") != capability_id:
            raise FailClosedRuntimeError(
                "semantic capability selection failed closed: registry identity mismatch"
            )
        _verify_named_hash(
            record,
            "certification_record_hash",
            "semantic capability selection failed closed: certification record hash mismatch",
        )
        if record.get("governance_metadata_only") is not True:
            raise FailClosedRuntimeError(
                "semantic capability selection failed closed: registry authority invalid"
            )
        if record.get("runtime_execution_authority") is not False:
            raise FailClosedRuntimeError(
                "semantic capability selection failed closed: registry execution authority invalid"
            )
        validated[capability_id] = deepcopy(record)
    return validated


def _validated_adapter_metadata(state: Any, fingerprint: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(state, dict) or not state:
        raise FailClosedRuntimeError(
            "semantic capability selection failed closed: G28 adapter metadata required"
        )
    expected = _require_hash(fingerprint, "invocation_adapter_metadata_fingerprint")
    if replay_hash(state) != expected:
        raise FailClosedRuntimeError(
            "semantic capability selection failed closed: G28 adapter fingerprint mismatch"
        )
    current = certified_capability_invocation_adapters()
    if state != current:
        raise FailClosedRuntimeError(
            "semantic capability selection failed closed: G28 adapter metadata drift"
        )
    for capability_id, metadata in sorted(state.items()):
        if metadata.get("capability_identifier") != capability_id:
            raise FailClosedRuntimeError(
                "semantic capability selection failed closed: G28 adapter identity mismatch"
            )
        _verify_named_hash(
            metadata,
            "adapter_metadata_hash",
            "semantic capability selection failed closed: G28 adapter metadata hash mismatch",
        )
        if metadata.get("dynamic_import_allowed") is not False:
            raise FailClosedRuntimeError(
                "semantic capability selection failed closed: dynamic adapter is forbidden"
            )
    return deepcopy(state)


def _validated_semantic_descriptors() -> dict[str, dict[str, Any]]:
    descriptors = certified_capability_semantic_descriptors()
    if tuple(sorted(descriptors)) != tuple(sorted(SUPPORTED_CAPABILITIES)):
        raise FailClosedRuntimeError(
            "semantic capability selection failed closed: semantic descriptor scope invalid"
        )
    for capability_id, descriptor in sorted(descriptors.items()):
        if descriptor.get("capability_identifier") != capability_id:
            raise FailClosedRuntimeError(
                "semantic capability selection failed closed: semantic descriptor identity mismatch"
            )
        _verify_named_hash(
            descriptor,
            "semantic_descriptor_hash",
            "semantic capability selection failed closed: semantic descriptor hash mismatch",
        )
    return descriptors


def _score_candidates(
    *,
    objective: dict[str, Any],
    registry: dict[str, dict[str, Any]],
    adapters: dict[str, dict[str, Any]],
    descriptors: dict[str, dict[str, Any]],
    available_input_types: list[str],
) -> list[dict[str, Any]]:
    text = _objective_text(objective)
    work_type = str(objective.get("requested_work_type") or "")
    records: list[dict[str, Any]] = []
    for capability_id in sorted(descriptors):
        descriptor = descriptors[capability_id]
        registry_record = registry.get(capability_id)
        adapter = adapters.get(capability_id)
        objective_terms = _matched_terms(text, descriptor["objective_terms"])
        actions = _matched_terms(text, descriptor["supported_actions"])
        subjects = _matched_terms(text, descriptor["supported_subjects"])
        outcomes = _matched_terms(text, descriptor["expected_outcomes"])
        exclusions = _matched_terms(text, descriptor["excluded_meanings"])
        accepted_inputs = sorted(
            str(item) for item in descriptor["accepted_canonical_input_artifact_types"]
        )
        matched_inputs = sorted(set(available_input_types).intersection(accepted_inputs))
        exact_identifier = capability_id.lower().replace("_", " ") in text
        unresolved: list[str] = []
        if not actions and not objective_terms and not exact_identifier:
            unresolved.append("capability_action")
        if not subjects and not objective_terms and not exact_identifier:
            unresolved.append("capability_subject")
        if not matched_inputs:
            unresolved.append("input_artifact_family")
        exclusion_evidence: list[str] = []
        if registry_record is None:
            exclusion_evidence.append("CAPABILITY_NOT_IN_CERTIFICATION_REGISTRY")
        elif registry_record.get("certification_status") not in CERTIFIED_STATES:
            exclusion_evidence.append("CAPABILITY_NOT_CURRENTLY_CERTIFIED")
        elif registry_record.get("superseded_by") is not None:
            exclusion_evidence.append("CAPABILITY_SUPERSEDED")
        if adapter is None:
            exclusion_evidence.append("G28_INVOCATION_ADAPTER_NOT_AVAILABLE")
        if work_type not in descriptor["supported_work_types"]:
            exclusion_evidence.append("REQUESTED_WORK_TYPE_INCOMPATIBLE")
        if exclusions:
            exclusion_evidence.append("EXCLUDED_MEANING_MATCHED")
        score = (
            (120 if exact_identifier else 0)
            + min(120, 60 * len(objective_terms))
            + min(70, 35 * len(actions))
            + min(50, 25 * len(subjects))
            + min(40, 20 * len(outcomes))
            + (80 if matched_inputs else 0)
        )
        positive = {
            "exact_identifier_match": exact_identifier,
            "objective_term_matches": objective_terms,
            "action_matches": actions,
            "subject_matches": subjects,
            "outcome_matches": outcomes,
            "available_accepted_input_artifact_types": matched_inputs,
            "work_type_match": work_type in descriptor["supported_work_types"],
            "certified": bool(
                registry_record
                and registry_record.get("certification_status") in CERTIFIED_STATES
                and registry_record.get("superseded_by") is None
            ),
            "g28_adapter_available": adapter is not None,
        }
        admissible = not exclusion_evidence and not unresolved and score > 0
        records.append(
            {
                "capability_identifier": capability_id,
                "score": score,
                "admissible": admissible,
                "invocation_eligible": admissible,
                "positive_match_evidence": positive,
                "exclusion_evidence": exclusion_evidence,
                "required_semantic_slots": list(descriptor["required_semantic_slots"]),
                "unresolved_semantic_slots": unresolved,
                "accepted_canonical_input_artifact_types": accepted_inputs,
                "required_canonical_input_fields": list(
                    descriptor["required_canonical_input_fields"]
                ),
                "clarification_label": descriptor["clarification_label"],
                "certification_record_hash": (
                    registry_record.get("certification_record_hash")
                    if registry_record
                    else None
                ),
                "adapter_metadata_hash": (
                    adapter.get("adapter_metadata_hash") if adapter else None
                ),
                "semantic_descriptor_hash": descriptor["semantic_descriptor_hash"],
            }
        )
    return sorted(records, key=lambda item: (-int(item["score"]), item["capability_identifier"]))


def _selection_decision(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    admissible = [item for item in candidates if item["admissible"] is True]
    if not admissible:
        any_base_eligible = any(
            item["positive_match_evidence"]["certified"]
            and item["positive_match_evidence"]["g28_adapter_available"]
            for item in candidates
        )
        return {
            "selection_status": (
                CAPABILITY_CLARIFICATION_REQUIRED
                if any_base_eligible
                else NO_ADMISSIBLE_CAPABILITY
            ),
            "selected_capability_identifier": None,
            "unique_highest_score": False,
            "clarification_required": True,
            "fail_closed_reason": "NO_SEMANTICALLY_ADMISSIBLE_CAPABILITY",
        }
    highest = int(admissible[0]["score"])
    tied = [item for item in admissible if int(item["score"]) == highest]
    if len(tied) != 1:
        return {
            "selection_status": CAPABILITY_CLARIFICATION_REQUIRED,
            "selected_capability_identifier": None,
            "unique_highest_score": False,
            "clarification_required": True,
            "fail_closed_reason": "MULTIPLE_CAPABILITIES_SHARE_HIGHEST_SCORE",
        }
    return {
        "selection_status": CAPABILITY_SELECTED,
        "selected_capability_identifier": tied[0]["capability_identifier"],
        "unique_highest_score": True,
        "clarification_required": False,
        "fail_closed_reason": None,
    }


def _clarification_artifact(
    *,
    selection_id: str,
    objective: dict[str, Any],
    candidates: list[dict[str, Any]],
    decision: dict[str, Any],
) -> dict[str, Any] | None:
    if decision["clarification_required"] is not True:
        return None
    admissible = [item for item in candidates if item["admissible"] is True]
    if len(admissible) > 1:
        labels = [item["clarification_label"] for item in admissible[:2]]
        question = f"Should Platform Core {labels[0]} or {labels[1]}?"
        missing_slot = "capability_target_choice"
    elif any("input_artifact_family" in item["unresolved_semantic_slots"] for item in candidates):
        question = (
            "Are you supplying a described implementation change, an existing normalized "
            "change artifact, or an existing platform change impact artifact?"
        )
        missing_slot = "input_artifact_family"
    else:
        question = (
            "Should Platform Core normalize a change, analyze an existing normalized change, "
            "or create a validation plan from an impact analysis?"
        )
        missing_slot = "capability_target_choice"
    return _artifact(
        SEMANTIC_CAPABILITY_CLARIFICATION_ARTIFACT_V1,
        {
            "selection_id": selection_id,
            "project_objective_hash": objective["artifact_hash"],
            "clarification_authority": "PLATFORM_CORE",
            "planning_mode": "DETERMINISTIC_SEMANTIC_PLANNING",
            "selected_missing_slot": missing_slot,
            "clarification_questions": [question],
            "clarification_question_count": 1,
            "asks_exactly_one_question": True,
            "platform_core_owns_clarification_semantics": True,
            "llm_reasoning_used": False,
            "probabilistic_routing_used": False,
            "candidate_identifiers": [item["capability_identifier"] for item in candidates],
            "clarification_reason": decision["fail_closed_reason"],
        },
    )


def _selection_artifact(
    *,
    selection_id: str,
    session_id: str,
    created_at: str,
    objective_reference: str,
    objective_hash: str,
    discovery: dict[str, Any],
    registry_fingerprint: str,
    adapter_fingerprint: str,
    descriptor_fingerprint: str,
    candidates: list[dict[str, Any]],
    decision: dict[str, Any],
    clarification: dict[str, Any] | None,
    source_hash: str,
    candidate_hash: str,
    scoring_hash: str,
    classification_hash: str,
) -> dict[str, Any]:
    selected = decision["selected_capability_identifier"]
    selected_record = next(
        (item for item in candidates if item["capability_identifier"] == selected),
        None,
    )
    artifact = {
        "artifact_type": SEMANTIC_CAPABILITY_SELECTION_ARTIFACT_V1,
        "runtime_version": SEMANTIC_CAPABILITY_SELECTION_RUNTIME_VERSION,
        "selection_id": selection_id,
        "session_id": session_id,
        "created_at": created_at,
        "project_objective_reference": objective_reference,
        "project_objective_hash": objective_hash,
        "candidate_discovery_reference": discovery["reference"],
        "candidate_discovery_hash": discovery["hash"],
        "certification_registry_fingerprint": registry_fingerprint,
        "invocation_adapter_metadata_fingerprint": adapter_fingerprint,
        "semantic_descriptor_fingerprint": descriptor_fingerprint,
        "objective_source_record_hash": source_hash,
        "candidate_set_record_hash": candidate_hash,
        "scoring_evidence_record_hash": scoring_hash,
        "classification_record_hash": classification_hash,
        "ordered_candidate_records": deepcopy(candidates),
        "selected_capability_identifier": selected,
        "selection_status": decision["selection_status"],
        "unique_highest_score": decision["unique_highest_score"],
        "clarification_required": decision["clarification_required"],
        "clarification_artifact_reference": (
            clarification.get("selection_id") if clarification else None
        ),
        "clarification_artifact_hash": (
            clarification.get("artifact_hash") if clarification else None
        ),
        "clarification_artifact": deepcopy(clarification),
        "invocation_eligible": selected_record is not None,
        "required_canonical_input_artifact_types": (
            selected_record["accepted_canonical_input_artifact_types"]
            if selected_record
            else []
        ),
        "required_canonical_input_fields": (
            selected_record["required_canonical_input_fields"]
            if selected_record
            else []
        ),
        "ready_for_g28_invocation": selected_record is not None,
        "fail_closed_reason": decision["fail_closed_reason"],
        "replay_visible": True,
        **deepcopy(BOUNDARY_FLAGS),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return validate_semantic_capability_selection_artifact(artifact)


def _failed_selection_artifact(
    *,
    selection_id: Any,
    session_id: Any,
    created_at: Any,
    objective_reference: Any,
    objective_hash: Any,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": SEMANTIC_CAPABILITY_SELECTION_ARTIFACT_V1,
        "runtime_version": SEMANTIC_CAPABILITY_SELECTION_RUNTIME_VERSION,
        "selection_id": _safe_string(selection_id),
        "session_id": _safe_string(session_id),
        "created_at": _safe_string(created_at),
        "project_objective_reference": _safe_string(objective_reference),
        "project_objective_hash": _safe_hash(objective_hash),
        "candidate_discovery_reference": None,
        "candidate_discovery_hash": None,
        "certification_registry_fingerprint": None,
        "invocation_adapter_metadata_fingerprint": None,
        "semantic_descriptor_fingerprint": None,
        "objective_source_record_hash": None,
        "candidate_set_record_hash": None,
        "scoring_evidence_record_hash": None,
        "classification_record_hash": None,
        "ordered_candidate_records": [],
        "selected_capability_identifier": None,
        "selection_status": FAILED_CLOSED,
        "unique_highest_score": False,
        "clarification_required": False,
        "clarification_artifact_reference": None,
        "clarification_artifact_hash": None,
        "clarification_artifact": None,
        "invocation_eligible": False,
        "required_canonical_input_artifact_types": [],
        "required_canonical_input_fields": [],
        "ready_for_g28_invocation": False,
        "fail_closed_reason": failure_reason,
        "replay_visible": True,
        **deepcopy(BOUNDARY_FLAGS),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return validate_semantic_capability_selection_artifact(artifact)


def _returned_artifact(selection: dict[str, Any]) -> dict[str, Any]:
    return _artifact(
        "SEMANTIC_CAPABILITY_SELECTION_RETURNED_ARTIFACT_V1",
        {
            "selection_id": selection["selection_id"],
            "selection_artifact_hash": selection["artifact_hash"],
            "selection_status": selection["selection_status"],
            "selected_capability_identifier": selection["selected_capability_identifier"],
            "ready_for_g28_invocation": selection["ready_for_g28_invocation"],
            "capability_invoked": False,
            "selection_treated_as_authorization": False,
            "failure_reason": selection["fail_closed_reason"],
        },
    )


def _capture(
    selection: dict[str, Any],
    returned: dict[str, Any],
    clarification: dict[str, Any] | None,
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "runtime_version": SEMANTIC_CAPABILITY_SELECTION_RUNTIME_VERSION,
        "selection_id": selection["selection_id"],
        "session_id": selection["session_id"],
        "selection_status": selection["selection_status"],
        "selected_capability_identifier": selection["selected_capability_identifier"],
        "semantic_capability_selection_artifact": deepcopy(selection),
        "semantic_capability_clarification_artifact": deepcopy(clarification),
        "semantic_capability_selection_returned_artifact": deepcopy(returned),
        "selection_replay_reference": str(replay_path),
        "ready_for_g28_invocation": selection["ready_for_g28_invocation"],
        "fail_closed": selection["selection_status"] in {
            FAILED_CLOSED,
            CAPABILITY_CLARIFICATION_REQUIRED,
            NO_ADMISSIBLE_CAPABILITY,
        },
        "failure_reason": selection["fail_closed_reason"],
        **deepcopy(BOUNDARY_FLAGS),
    }
    capture["capture_hash"] = replay_hash(capture)
    return capture


def _objective_text(objective: dict[str, Any]) -> str:
    values = [
        objective.get("source_request"),
        objective.get("canonical_project_objective"),
        objective.get("objective_subject"),
        " ".join(str(item) for item in objective.get("requested_outcomes", [])),
    ]
    return _normalize_text(" ".join(str(value or "") for value in values))


def _normalize_text(value: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value.lower()).split())


def _matched_terms(text: str, terms: Any) -> list[str]:
    matches: list[str] = []
    padded = f" {text} "
    for term in sorted(str(item) for item in terms):
        normalized = _normalize_text(term)
        if normalized and f" {normalized} " in padded:
            matches.append(term)
    return matches


def _normalized_input_types(values: Any) -> list[str]:
    if not isinstance(values, (list, tuple)):
        raise FailClosedRuntimeError(
            "semantic capability selection failed closed: input artifact types must be ordered"
        )
    normalized = []
    for value in values:
        token = _require_string(value, "available_input_artifact_type").upper()
        if token not in normalized:
            normalized.append(token)
    return sorted(normalized)


def _scoring_algorithm() -> dict[str, Any]:
    return {
        "algorithm_identifier": "G29_02_EXPLICIT_SEMANTIC_SCORE_V1",
        "exact_identifier_match": 120,
        "objective_term_match": 60,
        "objective_term_cap": 120,
        "supported_action_match": 35,
        "supported_action_cap": 70,
        "supported_subject_match": 25,
        "supported_subject_cap": 50,
        "expected_outcome_match": 20,
        "expected_outcome_cap": 40,
        "accepted_input_artifact_available": 80,
        "alphabetical_tie_resolution_allowed": False,
        "unique_highest_score_required": True,
    }


def _artifact(artifact_type: str, fields: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "artifact_type": artifact_type,
        "runtime_version": SEMANTIC_CAPABILITY_SELECTION_RUNTIME_VERSION,
        **deepcopy(fields),
        "replay_visible": True,
        "human_interface_authority": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "repository_mutated": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _persist_step(path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    wrapper = {"replay_index": index, "replay_step": step, "artifact": deepcopy(artifact)}
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(path / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(
    path: Path, selection: dict[str, Any], returned: dict[str, Any]
) -> None:
    try:
        _persist_step(path, 4, REPLAY_STEPS[4], selection)
        _persist_step(path, 5, REPLAY_STEPS[5], returned)
    except Exception:
        return


def _ensure_replay_available(path: Path) -> None:
    if path.exists() and any(path.iterdir()):
        raise FailClosedRuntimeError(
            "semantic capability selection failed closed: replay directory is not empty"
        )


def _verify_artifact_hash(artifact: Any, label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} must be an object")
    _verify_named_hash(artifact, "artifact_hash", f"{label} hash mismatch")


def _verify_named_hash(artifact: dict[str, Any], field: str, message: str) -> None:
    actual = _require_hash(artifact.get(field), field)
    body = deepcopy(artifact)
    body.pop(field, None)
    if replay_hash(body) != actual:
        raise FailClosedRuntimeError(message)


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"semantic capability selection requires {field}")
    return value.strip()


def _require_hash(value: Any, field: str) -> str:
    token = _require_string(value, field)
    if not token.startswith("sha256:"):
        raise FailClosedRuntimeError(f"semantic capability selection requires valid {field}")
    return token


def _safe_string(value: Any) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else "INVALID"


def _safe_hash(value: Any) -> str | None:
    return value if isinstance(value, str) and value.startswith("sha256:") else None


__all__ = [
    "CAPABILITY_CLARIFICATION_REQUIRED",
    "CAPABILITY_SELECTED",
    "FAILED_CLOSED",
    "NO_ADMISSIBLE_CAPABILITY",
    "SEMANTIC_CAPABILITY_CLARIFICATION_ARTIFACT_V1",
    "SEMANTIC_CAPABILITY_SELECTION_ARTIFACT_V1",
    "SEMANTIC_CAPABILITY_SELECTION_RUNTIME_VERSION",
    "reconstruct_semantic_capability_selection_replay",
    "select_semantic_capability",
    "semantic_capability_selection_fingerprints",
    "validate_semantic_capability_selection_artifact",
]
