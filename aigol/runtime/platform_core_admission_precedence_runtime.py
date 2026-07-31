"""Versioned Platform Core admission precedence for certified capability requests.

The runtime classifies only the admission destination.  It does not select or
invoke a capability, create canonical input evidence, authorize execution, or
change active-workspace continuation semantics.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.certified_capability_invocation_binding_runtime import (
    certified_capability_invocation_adapters,
    certified_capability_semantic_descriptors,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_certification_registry import (
    platform_capability_certification_registry,
)
from aigol.runtime.platform_project_objective_inference import (
    interpret_request_clause_roles,
)
from aigol.runtime.transport.serialization import (
    load_json,
    replay_hash,
    write_json_immutable,
)


PLATFORM_CORE_ADMISSION_PRECEDENCE_VERSION = (
    "G54_09_PLATFORM_CORE_ADMISSION_PRECEDENCE_RUNTIME_V1"
)
PLATFORM_CORE_ADMISSION_PRECEDENCE_ARTIFACT_V1 = (
    "PLATFORM_CORE_ADMISSION_PRECEDENCE_ARTIFACT_V1"
)

EXPLICIT_CERTIFIED_CAPABILITY_REQUEST_ADMITTED = (
    "EXPLICIT_CERTIFIED_CAPABILITY_REQUEST_ADMITTED"
)
GENERIC_GOVERNED_DEVELOPMENT_ADMISSION = (
    "GENERIC_GOVERNED_DEVELOPMENT_ADMISSION"
)
CAPABILITY_ADMISSION_CLARIFICATION_REQUIRED = (
    "CAPABILITY_ADMISSION_CLARIFICATION_REQUIRED"
)

ADMISSION_STATUSES = frozenset(
    {
        EXPLICIT_CERTIFIED_CAPABILITY_REQUEST_ADMITTED,
        GENERIC_GOVERNED_DEVELOPMENT_ADMISSION,
        CAPABILITY_ADMISSION_CLARIFICATION_REQUIRED,
    }
)

BOUNDARY_FLAGS = {
    "platform_core_authority": True,
    "human_interface_authority": False,
    "capability_selection_performed": False,
    "capability_invoked": False,
    "execution_authorized": False,
    "worker_invoked": False,
    "provider_invoked": False,
    "canonical_artifact_inferred_from_text": False,
    "active_workspace_state_modified": False,
    "replay_visible": True,
}

_OUTPUT_CONSTRAINT_PREFIXES = (
    "return ",
    "output ",
    "respond ",
    "show ",
    "present ",
    "provide ",
    "emit ",
)


def determine_platform_core_admission_precedence(
    *,
    request: str,
    explicit_canonical_artifacts: list[dict[str, Any]]
    | tuple[dict[str, Any], ...] = (),
    active_workspace_objective: Any = None,
    replay_reference: str | Path,
) -> dict[str, Any]:
    """Record whether explicit certified capability evidence preempts fallback."""

    prompt = _require_string(request, "request")
    reference = Path(replay_reference)
    clause_roles = interpret_request_clause_roles(prompt)
    operative_clauses, output_constraints = _admission_clauses(clause_roles)
    artifact_evidence, invalid_artifact_count = _canonical_artifact_evidence(
        explicit_canonical_artifacts
    )
    semantic_candidates = _semantic_candidates(
        operative_clauses=operative_clauses,
        artifact_evidence=artifact_evidence,
    )
    compatible_candidates = [
        item
        for item in semantic_candidates
        if item["compatible_authenticated_artifact_types"]
    ]
    (
        status,
        candidate_identifier,
        clarification_reason,
        work_type_override,
        active_workspace_fallback_allowed,
    ) = _admission_outcome(
        semantic_candidates=semantic_candidates,
        compatible_candidates=compatible_candidates,
        invalid_artifact_count=invalid_artifact_count,
    )

    decision_identity = {
        "source_request_hash": replay_hash(prompt),
        "operative_action_clauses": operative_clauses,
        "output_constraint_clauses": output_constraints,
        "canonical_artifact_evidence": artifact_evidence,
        "invalid_canonical_artifact_count": invalid_artifact_count,
        "semantic_candidates": semantic_candidates,
        "compatible_candidate_identifiers": [
            item["capability_identifier"] for item in compatible_candidates
        ],
        "admission_status": status,
        "admission_candidate_identifier": candidate_identifier,
        "admission_work_type_override": work_type_override,
        "clarification_reason": clarification_reason,
        "active_workspace_continuation_available": bool(
            isinstance(active_workspace_objective, str)
            and active_workspace_objective.strip()
        ),
        "active_workspace_fallback_allowed": active_workspace_fallback_allowed,
    }
    artifact = {
        "artifact_type": PLATFORM_CORE_ADMISSION_PRECEDENCE_ARTIFACT_V1,
        "runtime_version": PLATFORM_CORE_ADMISSION_PRECEDENCE_VERSION,
        "admission_authority": "PLATFORM_CORE",
        "source_request": prompt,
        **decision_identity,
        "admission_decision_hash": replay_hash(decision_identity),
        "operative_request_preserved_exactly": (
            status == EXPLICIT_CERTIFIED_CAPABILITY_REQUEST_ADMITTED
        ),
        "output_constraints_preserved": bool(output_constraints),
        "generic_continuation_preserved": (
            status == GENERIC_GOVERNED_DEVELOPMENT_ADMISSION
        ),
        "clarification_required": (
            status == CAPABILITY_ADMISSION_CLARIFICATION_REQUIRED
        ),
        **BOUNDARY_FLAGS,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    validate_platform_core_admission_precedence(artifact)
    write_json_immutable(reference, artifact)
    return deepcopy(artifact)


def validate_platform_core_admission_precedence(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Fail closed unless one admission decision preserves all owner boundaries."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(
            "Platform Core admission precedence artifact must be an object"
        )
    candidate = deepcopy(artifact)
    if candidate.get("artifact_type") != (
        PLATFORM_CORE_ADMISSION_PRECEDENCE_ARTIFACT_V1
    ):
        raise FailClosedRuntimeError(
            "Platform Core admission precedence artifact type mismatch"
        )
    if candidate.get("runtime_version") != PLATFORM_CORE_ADMISSION_PRECEDENCE_VERSION:
        raise FailClosedRuntimeError(
            "Platform Core admission precedence runtime version mismatch"
        )
    if candidate.get("admission_authority") != "PLATFORM_CORE":
        raise FailClosedRuntimeError(
            "Platform Core admission precedence authority invalid"
        )
    supplied_hash = candidate.pop("artifact_hash", None)
    if supplied_hash != replay_hash(candidate):
        raise FailClosedRuntimeError(
            "Platform Core admission precedence artifact hash mismatch"
        )
    candidate["artifact_hash"] = supplied_hash
    if candidate.get("admission_status") not in ADMISSION_STATUSES:
        raise FailClosedRuntimeError(
            "Platform Core admission precedence status invalid"
        )
    for field, expected in BOUNDARY_FLAGS.items():
        if candidate.get(field) is not expected:
            raise FailClosedRuntimeError(
                "Platform Core admission precedence authority boundary invalid"
            )
    source_request = _require_string(
        candidate.get("source_request"), "source_request"
    )
    if candidate.get("source_request_hash") != replay_hash(source_request):
        raise FailClosedRuntimeError(
            "Platform Core admission precedence source request hash mismatch"
        )
    expected_operative, expected_output = _admission_clauses(
        interpret_request_clause_roles(source_request)
    )
    if (
        candidate.get("operative_action_clauses") != expected_operative
        or candidate.get("output_constraint_clauses") != expected_output
        or candidate.get("output_constraints_preserved") is not bool(
            expected_output
        )
    ):
        raise FailClosedRuntimeError(
            "Platform Core admission precedence clause evidence mismatch"
        )
    artifact_evidence = candidate.get("canonical_artifact_evidence")
    invalid_artifact_count = candidate.get("invalid_canonical_artifact_count")
    if (
        not isinstance(artifact_evidence, list)
        or not isinstance(invalid_artifact_count, int)
        or isinstance(invalid_artifact_count, bool)
        or invalid_artifact_count < 0
    ):
        raise FailClosedRuntimeError(
            "Platform Core admission precedence artifact evidence invalid"
        )
    normalized_artifact_evidence: list[dict[str, str]] = []
    for item in artifact_evidence:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("artifact_type"), str)
            or not item["artifact_type"].strip()
            or not isinstance(item.get("artifact_hash"), str)
            or not item["artifact_hash"].strip()
        ):
            raise FailClosedRuntimeError(
                "Platform Core admission precedence artifact evidence invalid"
            )
        normalized_artifact_evidence.append(
            {
                "artifact_type": item["artifact_type"],
                "artifact_hash": item["artifact_hash"],
            }
        )
    normalized_artifact_evidence.sort(
        key=lambda item: f"{item['artifact_type']}:{item['artifact_hash']}"
    )
    if artifact_evidence != normalized_artifact_evidence or len(
        {
            f"{item['artifact_type']}:{item['artifact_hash']}"
            for item in normalized_artifact_evidence
        }
    ) != len(normalized_artifact_evidence):
        raise FailClosedRuntimeError(
            "Platform Core admission precedence artifact evidence invalid"
        )
    expected_semantic_candidates = _semantic_candidates(
        operative_clauses=expected_operative,
        artifact_evidence=normalized_artifact_evidence,
    )
    expected_compatible = [
        item
        for item in expected_semantic_candidates
        if item["compatible_authenticated_artifact_types"]
    ]
    expected_compatible_identifiers = [
        item["capability_identifier"] for item in expected_compatible
    ]
    (
        expected_status,
        expected_identifier,
        expected_reason,
        expected_work_type,
        expected_active_fallback,
    ) = _admission_outcome(
        semantic_candidates=expected_semantic_candidates,
        compatible_candidates=expected_compatible,
        invalid_artifact_count=invalid_artifact_count,
    )
    if (
        candidate.get("semantic_candidates") != expected_semantic_candidates
        or candidate.get("compatible_candidate_identifiers")
        != expected_compatible_identifiers
        or candidate.get("admission_status") != expected_status
        or candidate.get("admission_candidate_identifier")
        != expected_identifier
        or candidate.get("clarification_reason") != expected_reason
        or candidate.get("admission_work_type_override")
        != expected_work_type
        or candidate.get("active_workspace_fallback_allowed")
        is not expected_active_fallback
    ):
        raise FailClosedRuntimeError(
            "Platform Core admission precedence semantic reduction mismatch"
        )
    decision_identity = {
        field: candidate.get(field)
        for field in (
            "source_request_hash",
            "operative_action_clauses",
            "output_constraint_clauses",
            "canonical_artifact_evidence",
            "invalid_canonical_artifact_count",
            "semantic_candidates",
            "compatible_candidate_identifiers",
            "admission_status",
            "admission_candidate_identifier",
            "admission_work_type_override",
            "clarification_reason",
            "active_workspace_continuation_available",
            "active_workspace_fallback_allowed",
        )
    }
    if candidate.get("admission_decision_hash") != replay_hash(decision_identity):
        raise FailClosedRuntimeError(
            "Platform Core admission precedence decision hash mismatch"
        )
    status = candidate["admission_status"]
    if status == EXPLICIT_CERTIFIED_CAPABILITY_REQUEST_ADMITTED:
        if (
            not isinstance(candidate.get("admission_candidate_identifier"), str)
            or candidate.get("admission_work_type_override") != "ANALYSIS"
            or candidate.get("active_workspace_fallback_allowed") is not False
            or candidate.get("operative_request_preserved_exactly") is not True
            or candidate.get("clarification_required") is not False
        ):
            raise FailClosedRuntimeError(
                "explicit capability admission evidence incomplete"
            )
    elif status == CAPABILITY_ADMISSION_CLARIFICATION_REQUIRED:
        if (
            candidate.get("admission_candidate_identifier") is not None
            or candidate.get("active_workspace_fallback_allowed") is not False
            or candidate.get("clarification_required") is not True
        ):
            raise FailClosedRuntimeError(
                "capability admission clarification evidence invalid"
            )
    elif (
        candidate.get("active_workspace_fallback_allowed") is not True
        or candidate.get("generic_continuation_preserved") is not True
        or candidate.get("clarification_required") is not False
    ):
        raise FailClosedRuntimeError(
            "generic development admission evidence invalid"
        )
    return candidate


def reconstruct_platform_core_admission_precedence(
    replay_reference: str | Path,
) -> dict[str, Any]:
    """Reconstruct one immutable admission decision from its exact reference."""

    return validate_platform_core_admission_precedence(
        load_json(Path(replay_reference))
    )


def _admission_clauses(
    clause_roles: dict[str, Any],
) -> tuple[list[str], list[str]]:
    operative: list[str] = []
    output: list[str] = []
    for item in clause_roles.get("clauses") or []:
        if not isinstance(item, dict) or item.get("requested_action") is not True:
            continue
        text = str(item.get("text") or "").strip()
        lowered = str(item.get("normalized_text") or "").strip()
        if not text or item.get("quoted_runtime_evidence") is True:
            continue
        if lowered.startswith(_OUTPUT_CONSTRAINT_PREFIXES):
            output.append(text)
        else:
            operative.append(text)
    return operative, output


def _canonical_artifact_evidence(
    artifacts: list[dict[str, Any]] | tuple[dict[str, Any], ...],
) -> tuple[list[dict[str, str]], int]:
    evidence: dict[str, dict[str, str]] = {}
    invalid_count = 0
    for item in artifacts:
        if not isinstance(item, dict):
            invalid_count += 1
            continue
        artifact_type = item.get("artifact_type")
        artifact_hash = item.get("artifact_hash")
        body = deepcopy(item)
        body.pop("artifact_hash", None)
        if (
            not isinstance(artifact_type, str)
            or not artifact_type.strip()
            or not isinstance(artifact_hash, str)
            or artifact_hash != replay_hash(body)
        ):
            invalid_count += 1
            continue
        key = f"{artifact_type}:{artifact_hash}"
        evidence[key] = {
            "artifact_type": artifact_type,
            "artifact_hash": artifact_hash,
        }
    return [evidence[key] for key in sorted(evidence)], invalid_count


def _semantic_candidates(
    *,
    operative_clauses: list[str],
    artifact_evidence: list[dict[str, str]],
) -> list[dict[str, Any]]:
    descriptors = certified_capability_semantic_descriptors()
    adapters = certified_capability_invocation_adapters()
    registry = platform_capability_certification_registry()
    available_types = {
        item["artifact_type"] for item in artifact_evidence
    }
    records: list[dict[str, Any]] = []
    for capability_identifier in sorted(descriptors):
        descriptor = descriptors[capability_identifier]
        adapter = adapters.get(capability_identifier)
        certification = registry.get(capability_identifier)
        matched_clauses: list[str] = []
        matched_actions: set[str] = set()
        matched_subjects: set[str] = set()
        for clause in operative_clauses:
            lowered = " ".join(clause.lower().split())
            actions = {
                str(action)
                for action in descriptor["supported_actions"]
                if _contains_term(lowered, str(action).lower())
            }
            subjects = {
                str(subject)
                for subject in descriptor["supported_subjects"]
                if str(subject).lower() in lowered
            }
            if actions and subjects:
                matched_clauses.append(clause)
                matched_actions.update(actions)
                matched_subjects.update(subjects)
        if not matched_clauses:
            continue
        accepted_types = set(
            descriptor["accepted_canonical_input_artifact_types"]
        )
        compatible_types = sorted(available_types.intersection(accepted_types))
        currently_certified = bool(
            isinstance(certification, dict)
            and certification.get("certification_status")
            in {"CERTIFIED", "VERIFIED"}
            and certification.get("superseded_by") is None
        )
        if not currently_certified or not isinstance(adapter, dict):
            continue
        records.append(
            {
                "capability_identifier": capability_identifier,
                "matched_operative_clauses": matched_clauses,
                "matched_actions": sorted(matched_actions),
                "matched_subjects": sorted(matched_subjects),
                "accepted_canonical_input_artifact_types": sorted(
                    accepted_types
                ),
                "compatible_authenticated_artifact_types": compatible_types,
                "certification_record_hash": certification.get(
                    "certification_record_hash"
                ),
                "adapter_metadata_hash": adapter.get("adapter_metadata_hash"),
                "semantic_descriptor_hash": descriptor.get(
                    "semantic_descriptor_hash"
                ),
            }
        )
    return records


def _admission_outcome(
    *,
    semantic_candidates: list[dict[str, Any]],
    compatible_candidates: list[dict[str, Any]],
    invalid_artifact_count: int,
) -> tuple[str, str | None, str | None, str | None, bool]:
    if len(semantic_candidates) == 1 and len(compatible_candidates) == 1:
        return (
            EXPLICIT_CERTIFIED_CAPABILITY_REQUEST_ADMITTED,
            str(compatible_candidates[0]["capability_identifier"]),
            None,
            "ANALYSIS",
            False,
        )
    if semantic_candidates:
        clarification_reason = (
            "MULTIPLE_EXPLICIT_CERTIFIED_CAPABILITY_REQUESTS"
            if len(semantic_candidates) > 1
            else "AUTHENTICATED_CANONICAL_CAPABILITY_INPUT_REQUIRED"
        )
        if invalid_artifact_count:
            clarification_reason = "INVALID_CANONICAL_CAPABILITY_INPUT_EVIDENCE"
        return (
            CAPABILITY_ADMISSION_CLARIFICATION_REQUIRED,
            None,
            clarification_reason,
            None,
            False,
        )
    return (
        GENERIC_GOVERNED_DEVELOPMENT_ADMISSION,
        None,
        None,
        None,
        True,
    )


def _contains_term(text: str, term: str) -> bool:
    normalized = " ".join(text.split())
    if " " in term:
        return term in normalized
    return any(part.strip(".,:;!?()[]{}") == term for part in normalized.split())


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


__all__ = [
    "CAPABILITY_ADMISSION_CLARIFICATION_REQUIRED",
    "EXPLICIT_CERTIFIED_CAPABILITY_REQUEST_ADMITTED",
    "GENERIC_GOVERNED_DEVELOPMENT_ADMISSION",
    "PLATFORM_CORE_ADMISSION_PRECEDENCE_ARTIFACT_V1",
    "PLATFORM_CORE_ADMISSION_PRECEDENCE_VERSION",
    "determine_platform_core_admission_precedence",
    "reconstruct_platform_core_admission_precedence",
    "validate_platform_core_admission_precedence",
]
