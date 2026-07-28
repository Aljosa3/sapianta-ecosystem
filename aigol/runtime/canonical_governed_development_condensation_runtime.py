"""Dormant canonical governed-development condensation proposal artifacts.

This module constructs immutable, non-authoritative proposal evidence only.
It is not imported by G31, AiCLI, the Human Interface runtime entry, Worker
activation, Authorization, a Provider, or an execution gate.
"""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


CANONICAL_CONDENSATION_ARTIFACT_V1 = (
    "CANONICAL_GOVERNED_DEVELOPMENT_CONDENSATION_ARTIFACT_V1"
)
CANONICAL_CONDENSATION_SCHEMA_V1 = (
    "CANONICAL_GOVERNED_DEVELOPMENT_CONDENSATION_SCHEMA_V1"
)
CANONICAL_CONDENSATION_SCHEMA_VERSION = "1.0.0"
CANONICAL_CONDENSATION_ARTIFACT_VERSION = "1.0.0"
CANONICAL_CONDENSATION_CREATION_AUTHORITY = (
    "GOVERNED_DEVELOPMENT_CONDENSATION_OWNER"
)
CANONICAL_CONDENSATION_VALIDATION_AUTHORITY = (
    "DETERMINISTIC_GOVERNED_DEVELOPMENT_CONDENSATION_VALIDATOR"
)
CANONICAL_CONDENSATION_PROPOSAL_METHOD = "DETERMINISTIC_RULES"
CANONICAL_CONDENSATION_RULESET_ID = (
    "CANONICAL_GOVERNED_DEVELOPMENT_CONDENSATION_RULESET_V1"
)
G31_CODEX_SYNTHESIS_PREFIX_CONTRACT_V1 = "G31_CODEX_SYNTHESIS_PREFIX_V1"
G31_CODEX_SYNTHESIS_PREFIX = "runtime validation: "
G31_CODEX_SYNTHESIS_MAXIMUM_CHARACTER_COUNT = 240

SEMANTIC_COMMITMENT_FIELDS = (
    "requested_capability",
    "user_visible_outcome",
    "allowed_operations",
    "prohibited_operations",
    "architectural_placement",
    "acceptance_conditions",
    "testing_validation_requirements",
    "explicit_exclusions",
    "safety_governance_constraints",
)
SCALAR_SEMANTIC_COMMITMENT_FIELDS = frozenset(
    {
        "requested_capability",
        "user_visible_outcome",
        "architectural_placement",
    }
)
LIST_SEMANTIC_COMMITMENT_FIELDS = frozenset(SEMANTIC_COMMITMENT_FIELDS) - (
    SCALAR_SEMANTIC_COMMITMENT_FIELDS
)

NO_AUTHORITY_EFFECT = {
    "approval_created": False,
    "authorization_created": False,
    "execution_authorized": False,
    "worker_selected": False,
    "worker_assigned": False,
    "worker_dispatched": False,
    "worker_invoked": False,
    "provider_invoked": False,
    "execution_gate_reached": False,
    "repository_mutated": False,
    "g31_input_binding_created": False,
    "g31_preflight_invoked": False,
    "replay_visible": True,
}

_ARTIFACT_FIELDS = frozenset(
    {
        "artifact_type",
        "schema_id",
        "schema_version",
        "artifact_version",
        "condensation_id",
        "condensation_hash",
        "creation_authority",
        "validation_authority",
        "authority_effect",
        "source_lineage",
        "semantic_commitments",
        "source_requirements",
        "requirement_map",
        "proposal_method",
        "proposal_method_evidence",
        "unresolved_ambiguities",
        "projection_prefix_contract_id",
        "projection_prefix",
        "projection_prefix_code_point_count",
        "projection_prefix_utf8_byte_count",
        "projection_prefix_sha256",
        "proposed_synthesis_body",
        "proposed_synthesis_body_code_point_count",
        "proposed_synthesis_body_utf8_byte_count",
        "proposed_synthesis_body_sha256",
        "proposed_projection",
        "proposed_projection_code_point_count",
        "proposed_projection_utf8_byte_count",
        "proposed_projection_sha256",
        "maximum_projection_code_point_count",
        "character_counting_contract",
        "approval_required",
        "ready_for_human_review",
        "ready_for_g31",
        *NO_AUTHORITY_EFFECT.keys(),
    }
)


def create_canonical_condensation_proposal(
    *,
    original_request_id: str,
    original_request: str,
    clarification_evidence: list[dict[str, Any]],
    clarification_complete: bool,
    completed_objective_id: str,
    completed_objective: str,
    project_id: str,
    workspace_id: str,
    session_id: str,
    invocation_id: str | None,
    chain_id: str | None,
    semantic_commitments: dict[str, Any],
    source_requirements: list[dict[str, Any]],
    requirement_mappings: list[dict[str, Any]],
    proposed_synthesis_body: str,
    unresolved_ambiguities: list[str] | tuple[str, ...] = (),
    proposal_method: str = CANONICAL_CONDENSATION_PROPOSAL_METHOD,
    proposal_method_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create one deterministic, non-authoritative condensation proposal.

    The function records a selected proposal; it does not infer, approve, or
    authorize that proposal. Semantic admissibility is decided only by the
    separate deterministic validator.
    """

    original_id = _required_text(original_request_id, "original_request_id")
    original = _exact_nonempty_text(original_request, "original_request")
    objective_id = _required_text(completed_objective_id, "completed_objective_id")
    objective = _exact_nonempty_text(completed_objective, "completed_objective")
    project = _required_text(project_id, "project_id")
    workspace = _required_text(workspace_id, "workspace_id")
    session = _required_text(session_id, "session_id")
    invocation = _optional_identifier(invocation_id, "invocation_id")
    chain = _optional_identifier(chain_id, "chain_id")
    body = _exact_nonempty_text(
        proposed_synthesis_body,
        "proposed_synthesis_body",
    )
    clarification = _canonical_clarification_evidence(clarification_evidence)
    commitments = _canonical_semantic_commitments(semantic_commitments)
    requirements = _canonical_source_requirements(source_requirements)
    mappings = _canonical_requirement_mappings(
        requirement_mappings,
        source_requirements=requirements,
    )
    ambiguities = _string_list(
        unresolved_ambiguities,
        "unresolved_ambiguities",
        allow_empty=True,
    )
    method = _required_text(proposal_method, "proposal_method")
    method_evidence = _proposal_method_evidence(
        method,
        proposal_method_evidence,
    )

    original_sha = content_sha256(original)
    clarification_hashes = [item["clarification_evidence_hash"] for item in clarification]
    objective_sha = content_sha256(objective)
    project_workspace_identity = {
        "project_id": project,
        "workspace_id": workspace,
    }
    clarification_resolution = {
        "resolution_status": (
            "COMPLETE_WITH_EVIDENCE"
            if clarification_complete and clarification
            else "COMPLETE_NO_CLARIFICATION_REQUIRED"
            if clarification_complete
            else "INCOMPLETE"
        ),
        "clarification_evidence_count": len(clarification),
    }
    clarification_resolution["clarification_resolution_hash"] = replay_hash(
        clarification_resolution
    )
    source_lineage = {
        "original_request": {
            "original_request_id": original_id,
            "original_request": original,
            "original_request_sha256": original_sha,
        },
        "clarification_complete": clarification_complete
        if isinstance(clarification_complete, bool)
        else False,
        "clarification_evidence": clarification,
        "clarification_evidence_hashes": clarification_hashes,
        "clarification_resolution": clarification_resolution,
        "completed_objective": {
            "completed_objective_id": objective_id,
            "completed_objective": objective,
            "completed_objective_sha256": objective_sha,
            "source_original_request_sha256": original_sha,
            "source_clarification_evidence_hashes": clarification_hashes,
        },
        "project_workspace": {
            **project_workspace_identity,
            "project_workspace_hash": replay_hash(project_workspace_identity),
        },
        "session_id": session,
        "invocation_id": invocation,
        "chain_id": chain,
    }
    source_lineage["source_bundle_hash"] = replay_hash(source_lineage)

    projection = f"{G31_CODEX_SYNTHESIS_PREFIX}{body}"
    artifact = {
        "artifact_type": CANONICAL_CONDENSATION_ARTIFACT_V1,
        "schema_id": CANONICAL_CONDENSATION_SCHEMA_V1,
        "schema_version": CANONICAL_CONDENSATION_SCHEMA_VERSION,
        "artifact_version": CANONICAL_CONDENSATION_ARTIFACT_VERSION,
        "creation_authority": CANONICAL_CONDENSATION_CREATION_AUTHORITY,
        "validation_authority": CANONICAL_CONDENSATION_VALIDATION_AUTHORITY,
        "authority_effect": "NONE",
        "source_lineage": source_lineage,
        "semantic_commitments": commitments,
        "source_requirements": requirements,
        "requirement_map": mappings,
        "proposal_method": method,
        "proposal_method_evidence": method_evidence,
        "unresolved_ambiguities": ambiguities,
        "projection_prefix_contract_id": G31_CODEX_SYNTHESIS_PREFIX_CONTRACT_V1,
        "projection_prefix": G31_CODEX_SYNTHESIS_PREFIX,
        "projection_prefix_code_point_count": len(G31_CODEX_SYNTHESIS_PREFIX),
        "projection_prefix_utf8_byte_count": len(
            G31_CODEX_SYNTHESIS_PREFIX.encode("utf-8")
        ),
        "projection_prefix_sha256": content_sha256(G31_CODEX_SYNTHESIS_PREFIX),
        "proposed_synthesis_body": body,
        "proposed_synthesis_body_code_point_count": len(body),
        "proposed_synthesis_body_utf8_byte_count": len(body.encode("utf-8")),
        "proposed_synthesis_body_sha256": content_sha256(body),
        "proposed_projection": projection,
        "proposed_projection_code_point_count": len(projection),
        "proposed_projection_utf8_byte_count": len(projection.encode("utf-8")),
        "proposed_projection_sha256": content_sha256(projection),
        "maximum_projection_code_point_count": (
            G31_CODEX_SYNTHESIS_MAXIMUM_CHARACTER_COUNT
        ),
        "character_counting_contract": "PYTHON_UNICODE_CODE_POINTS",
        "approval_required": True,
        "ready_for_human_review": False,
        "ready_for_g31": False,
        **deepcopy(NO_AUTHORITY_EFFECT),
    }
    identity_seed = deepcopy(artifact)
    condensation_hash = replay_hash(identity_seed)
    artifact["condensation_id"] = (
        f"CANONICAL-CONDENSATION-{condensation_hash.removeprefix('sha256:')[:24]}"
    )
    artifact["condensation_hash"] = condensation_hash
    validate_canonical_condensation_artifact(artifact)
    return deepcopy(artifact)


def validate_canonical_condensation_artifact(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Verify structural and deterministic identity integrity only."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("canonical condensation proposal must be an object")
    candidate = deepcopy(artifact)
    if frozenset(candidate) != _ARTIFACT_FIELDS:
        raise FailClosedRuntimeError("canonical condensation proposal field set mismatch")
    constants = {
        "artifact_type": CANONICAL_CONDENSATION_ARTIFACT_V1,
        "schema_id": CANONICAL_CONDENSATION_SCHEMA_V1,
        "schema_version": CANONICAL_CONDENSATION_SCHEMA_VERSION,
        "artifact_version": CANONICAL_CONDENSATION_ARTIFACT_VERSION,
        "creation_authority": CANONICAL_CONDENSATION_CREATION_AUTHORITY,
        "validation_authority": CANONICAL_CONDENSATION_VALIDATION_AUTHORITY,
        "authority_effect": "NONE",
        "approval_required": True,
        "ready_for_human_review": False,
        "ready_for_g31": False,
        "projection_prefix_contract_id": G31_CODEX_SYNTHESIS_PREFIX_CONTRACT_V1,
        "maximum_projection_code_point_count": (
            G31_CODEX_SYNTHESIS_MAXIMUM_CHARACTER_COUNT
        ),
        "character_counting_contract": "PYTHON_UNICODE_CODE_POINTS",
        **NO_AUTHORITY_EFFECT,
    }
    for field, expected in constants.items():
        if candidate.get(field) != expected:
            raise FailClosedRuntimeError(
                f"canonical condensation proposal boundary mismatch: {field}"
            )
    identity_seed = deepcopy(candidate)
    actual_id = identity_seed.pop("condensation_id", None)
    actual_hash = identity_seed.pop("condensation_hash", None)
    expected_hash = replay_hash(identity_seed)
    expected_id = (
        f"CANONICAL-CONDENSATION-{expected_hash.removeprefix('sha256:')[:24]}"
    )
    if actual_hash != expected_hash or actual_id != expected_id:
        raise FailClosedRuntimeError("canonical condensation proposal identity mismatch")
    return candidate


def content_sha256(value: str) -> str:
    """Hash the strict UTF-8 bytes of one exact string."""

    if not isinstance(value, str):
        raise FailClosedRuntimeError("canonical condensation content must be text")
    try:
        encoded = value.encode("utf-8", errors="strict")
    except UnicodeEncodeError as exc:
        raise FailClosedRuntimeError(
            "canonical condensation content must be strict UTF-8 encodable"
        ) from exc
    return sha256(encoded).hexdigest()


def _canonical_clarification_evidence(
    evidence: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not isinstance(evidence, list):
        raise FailClosedRuntimeError("clarification_evidence must be a list")
    result = []
    seen: set[str] = set()
    for item in evidence:
        if not isinstance(item, dict):
            raise FailClosedRuntimeError("clarification evidence item must be an object")
        question_id = _required_text(item.get("question_id"), "question_id")
        answer_id = _required_text(item.get("answer_id"), "answer_id")
        evidence_id = f"{question_id}:{answer_id}"
        if evidence_id in seen:
            raise FailClosedRuntimeError("clarification evidence is duplicated")
        seen.add(evidence_id)
        question = _exact_nonempty_text(item.get("question"), "question")
        answer = _exact_nonempty_text(item.get("answer"), "answer")
        canonical = {
            "question_id": question_id,
            "question": question,
            "question_sha256": content_sha256(question),
            "answer_id": answer_id,
            "answer": answer,
            "answer_sha256": content_sha256(answer),
            "resolved": item.get("resolved") is True,
        }
        canonical["clarification_evidence_hash"] = replay_hash(canonical)
        result.append(canonical)
    return result


def _canonical_semantic_commitments(
    commitments: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(commitments, dict):
        raise FailClosedRuntimeError("semantic_commitments must be an object")
    if frozenset(commitments) != frozenset(SEMANTIC_COMMITMENT_FIELDS):
        raise FailClosedRuntimeError("semantic commitments field set mismatch")
    result: dict[str, Any] = {}
    for field in SEMANTIC_COMMITMENT_FIELDS:
        value = commitments[field]
        if field in SCALAR_SEMANTIC_COMMITMENT_FIELDS:
            result[field] = _exact_nonempty_text(value, field)
        else:
            result[field] = _string_list(value, field, allow_empty=True)
    return result


def _canonical_source_requirements(
    requirements: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not isinstance(requirements, list):
        raise FailClosedRuntimeError("source_requirements must be a list")
    result = []
    seen: set[str] = set()
    for item in requirements:
        if not isinstance(item, dict):
            raise FailClosedRuntimeError("source requirement must be an object")
        requirement_id = _required_text(item.get("requirement_id"), "requirement_id")
        if requirement_id in seen:
            raise FailClosedRuntimeError("source requirement ID is duplicated")
        seen.add(requirement_id)
        requirement_type = _required_text(
            item.get("requirement_type"),
            "requirement_type",
        )
        if requirement_type not in SEMANTIC_COMMITMENT_FIELDS:
            raise FailClosedRuntimeError("source requirement type is unsupported")
        source_text = _exact_nonempty_text(item.get("source_text"), "source_text")
        result.append(
            {
                "requirement_id": requirement_id,
                "requirement_type": requirement_type,
                "source_text": source_text,
                "source_requirement_sha256": content_sha256(source_text),
            }
        )
    return result


def _canonical_requirement_mappings(
    mappings: list[dict[str, Any]],
    *,
    source_requirements: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not isinstance(mappings, list):
        raise FailClosedRuntimeError("requirement_mappings must be a list")
    sources = {
        item["requirement_id"]: item
        for item in source_requirements
    }
    result = []
    seen: set[str] = set()
    for item in mappings:
        if not isinstance(item, dict):
            raise FailClosedRuntimeError("requirement mapping must be an object")
        requirement_id = _required_text(item.get("requirement_id"), "requirement_id")
        if requirement_id in seen:
            raise FailClosedRuntimeError("requirement mapping is duplicated")
        seen.add(requirement_id)
        target_field = _required_text(item.get("target_field"), "target_field")
        representation = _exact_nonempty_text(
            item.get("exact_condensed_representation"),
            "exact_condensed_representation",
        )
        source = sources.get(requirement_id)
        result.append(
            {
                "requirement_id": requirement_id,
                "source_requirement_sha256": (
                    source["source_requirement_sha256"] if source else None
                ),
                "target_semantic_field": target_field,
                "exact_condensed_representation": representation,
                "exact_condensed_representation_sha256": content_sha256(
                    representation
                ),
            }
        )
    return result


def _proposal_method_evidence(
    method: str,
    supplied: dict[str, Any] | None,
) -> dict[str, Any]:
    if method == CANONICAL_CONDENSATION_PROPOSAL_METHOD:
        ruleset = {
            "ruleset_id": CANONICAL_CONDENSATION_RULESET_ID,
            "proposal_is_selected_input": True,
            "automatic_retry_allowed": False,
            "semantic_inference_allowed": False,
            "constraint_discard_allowed": False,
        }
        ruleset["ruleset_hash"] = replay_hash(ruleset)
        return ruleset
    if not isinstance(supplied, dict):
        return {"unsupported_method_observed": method}
    return deepcopy(supplied)


def _string_list(
    value: Any,
    field: str,
    *,
    allow_empty: bool,
) -> list[str]:
    if not isinstance(value, (list, tuple)):
        raise FailClosedRuntimeError(f"{field} must be a list")
    result = [_exact_nonempty_text(item, field) for item in value]
    if not allow_empty and not result:
        raise FailClosedRuntimeError(f"{field} must not be empty")
    if len(result) != len(set(result)):
        raise FailClosedRuntimeError(f"{field} contains duplicate values")
    return result


def _required_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field} is required")
    return value.strip()


def _exact_nonempty_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise FailClosedRuntimeError(f"{field} is required")
    content_sha256(value)
    return value


def _optional_identifier(value: Any, field: str) -> str | None:
    if value is None:
        return None
    return _required_text(value, field)
