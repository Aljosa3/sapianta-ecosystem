"""Deterministic, read-only validation for canonical condensation proposals."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from aigol.runtime.canonical_governed_development_condensation_runtime import (
    CANONICAL_CONDENSATION_ARTIFACT_V1,
    CANONICAL_CONDENSATION_PROPOSAL_METHOD,
    CANONICAL_CONDENSATION_RULESET_ID,
    G31_CODEX_SYNTHESIS_MAXIMUM_CHARACTER_COUNT,
    G31_CODEX_SYNTHESIS_PREFIX,
    G31_CODEX_SYNTHESIS_PREFIX_CONTRACT_V1,
    LIST_SEMANTIC_COMMITMENT_FIELDS,
    NO_AUTHORITY_EFFECT,
    SCALAR_SEMANTIC_COMMITMENT_FIELDS,
    SEMANTIC_COMMITMENT_FIELDS,
    content_sha256,
    validate_canonical_condensation_artifact,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


CANONICAL_CONDENSATION_VALIDATION_RESULT_V1 = (
    "CANONICAL_GOVERNED_DEVELOPMENT_CONDENSATION_VALIDATION_RESULT_V1"
)
CANONICAL_CONDENSATION_VALIDATOR_VERSION = "1.0.0"
CANONICAL_CONDENSATION_VALIDATION_PASS = "PASS"
CANONICAL_CONDENSATION_VALIDATION_FAIL = "FAIL"

FAILURE_CODE_ORDER = (
    "MISSING_SOURCE_LINEAGE",
    "SOURCE_HASH_MISMATCH",
    "INCOMPLETE_CLARIFICATION",
    "INVALID_SCHEMA",
    "MATERIAL_REQUIREMENT_UNMAPPED",
    "MATERIAL_REQUIREMENT_LOSS",
    "AMBIGUOUS_CONDENSED_OBJECTIVE",
    "UNSUPPORTED_PROPOSAL_METHOD",
    "EXCESSIVE_CANONICAL_REQUEST_LENGTH",
    "REPLAY_IDENTITY_MISMATCH",
    "UNAPPROVED_CONDENSATION",
    "VALIDATOR_DISAGREEMENT",
)

VALIDATION_AUTHORITY_BOUNDARIES = {
    "read_only": True,
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
    "certification_performed": False,
    "replay_visible": True,
}

_EXPECTED_CONTEXT_FIELDS = frozenset(
    {
        "project_id",
        "workspace_id",
        "session_id",
        "invocation_id",
        "chain_id",
        "original_request_sha256",
        "completed_objective_sha256",
    }
)


def validate_canonical_condensation_proposal(
    proposal: Any,
    *,
    expected_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return one deterministic PASS/FAIL artifact.

    PASS means eligible for a later human review only. It never means approved,
    G31-admissible, authorized, executable, or certified.
    """

    observed = _canonical_observation(proposal)
    result = _validation_without_self_verification(
        observed,
        expected_context=expected_context,
    )
    validate_canonical_condensation_validation_result(
        result,
        proposal=observed,
    )
    return deepcopy(result)


def validate_canonical_condensation_validation_result(
    validation_result: dict[str, Any],
    *,
    proposal: dict[str, Any],
) -> dict[str, Any]:
    """Verify a supplied validation artifact against deterministic re-evaluation."""

    if not isinstance(validation_result, dict):
        raise FailClosedRuntimeError("canonical condensation validation result required")
    candidate = deepcopy(validation_result)
    if candidate.get("artifact_type") != CANONICAL_CONDENSATION_VALIDATION_RESULT_V1:
        raise FailClosedRuntimeError("canonical condensation validation type mismatch")
    if candidate.get("validator_version") != CANONICAL_CONDENSATION_VALIDATOR_VERSION:
        raise FailClosedRuntimeError("canonical condensation validator version mismatch")
    for field, expected in VALIDATION_AUTHORITY_BOUNDARIES.items():
        if candidate.get(field) != expected:
            raise FailClosedRuntimeError(
                f"canonical condensation validation authority mismatch: {field}"
            )
    identity_seed = deepcopy(candidate)
    actual_id = identity_seed.pop("validation_id", None)
    actual_hash = identity_seed.pop("validation_hash", None)
    expected_hash = replay_hash(identity_seed)
    expected_id = (
        "CANONICAL-CONDENSATION-VALIDATION-"
        f"{expected_hash.removeprefix('sha256:')[:24]}"
    )
    if actual_hash != expected_hash or actual_id != expected_id:
        raise FailClosedRuntimeError("canonical condensation validation identity mismatch")
    context = candidate.get("expected_context")
    expected = _validation_without_self_verification(
        proposal,
        expected_context=context,
    )
    if candidate != expected:
        raise FailClosedRuntimeError(
            "canonical condensation validation deterministic reconstruction mismatch"
        )
    return candidate


def _validation_without_self_verification(
    proposal: dict[str, Any],
    *,
    expected_context: dict[str, Any] | None,
) -> dict[str, Any]:
    """Reproduce validation without recursively invoking the public verifier."""

    observed = _canonical_observation(proposal)
    context = _canonical_expected_context(expected_context)
    failures = _evaluate_proposal(observed, context)
    status = (
        CANONICAL_CONDENSATION_VALIDATION_PASS
        if not failures
        else CANONICAL_CONDENSATION_VALIDATION_FAIL
    )
    checks = [
        {
            "failure_code": code,
            "passed": code not in failures,
            "detail": _check_detail(code, code not in failures),
        }
        for code in FAILURE_CODE_ORDER
        if code != "UNAPPROVED_CONDENSATION"
    ]
    source_lineage = (
        deepcopy(observed.get("source_lineage"))
        if isinstance(observed.get("source_lineage"), dict)
        else {}
    )
    body = observed.get("proposed_synthesis_body")
    projection = observed.get("proposed_projection")
    result = {
        "artifact_type": CANONICAL_CONDENSATION_VALIDATION_RESULT_V1,
        "schema_version": "1.0.0",
        "validator_version": CANONICAL_CONDENSATION_VALIDATOR_VERSION,
        "validation_authority": (
            "DETERMINISTIC_GOVERNED_DEVELOPMENT_CONDENSATION_VALIDATOR"
        ),
        "authority_effect": "NONE",
        "validation_status": status,
        "fail_closed": bool(failures),
        "failure_codes": failures,
        "checks": checks,
        "condensation_id": observed.get("condensation_id"),
        "condensation_hash": observed.get("condensation_hash"),
        "observed_proposal_hash": replay_hash(observed),
        "source_bundle_hash": source_lineage.get("source_bundle_hash"),
        "original_request_sha256": (
            source_lineage.get("original_request") or {}
        ).get("original_request_sha256"),
        "clarification_evidence_hashes": deepcopy(
            source_lineage.get("clarification_evidence_hashes") or []
        ),
        "completed_objective_sha256": (
            source_lineage.get("completed_objective") or {}
        ).get("completed_objective_sha256"),
        "project_workspace_hash": (
            source_lineage.get("project_workspace") or {}
        ).get("project_workspace_hash"),
        "session_id": source_lineage.get("session_id"),
        "invocation_id": source_lineage.get("invocation_id"),
        "chain_id": source_lineage.get("chain_id"),
        "expected_context": context,
        "projection_prefix": observed.get("projection_prefix"),
        "projection_prefix_sha256": observed.get("projection_prefix_sha256"),
        "proposed_synthesis_body": body if isinstance(body, str) else None,
        "proposed_synthesis_body_code_point_count": (
            len(body) if isinstance(body, str) else None
        ),
        "proposed_synthesis_body_sha256": (
            _safe_content_hash(body) if isinstance(body, str) else None
        ),
        "proposed_projection": projection if isinstance(projection, str) else None,
        "proposed_projection_code_point_count": (
            len(projection) if isinstance(projection, str) else None
        ),
        "proposed_projection_sha256": (
            _safe_content_hash(projection) if isinstance(projection, str) else None
        ),
        "maximum_projection_code_point_count": (
            G31_CODEX_SYNTHESIS_MAXIMUM_CHARACTER_COUNT
        ),
        "character_counting_contract": "PYTHON_UNICODE_CODE_POINTS",
        "approval_required": True,
        "ready_for_human_review": status
        == CANONICAL_CONDENSATION_VALIDATION_PASS,
        "ready_for_g31": False,
        **deepcopy(VALIDATION_AUTHORITY_BOUNDARIES),
    }
    identity_seed = deepcopy(result)
    validation_hash = replay_hash(identity_seed)
    result["validation_id"] = (
        "CANONICAL-CONDENSATION-VALIDATION-"
        f"{validation_hash.removeprefix('sha256:')[:24]}"
    )
    result["validation_hash"] = validation_hash
    return result


def _evaluate_proposal(
    proposal: dict[str, Any],
    expected_context: dict[str, Any],
) -> list[str]:
    failures: set[str] = set()
    if not proposal or proposal.get("artifact_type") != CANONICAL_CONDENSATION_ARTIFACT_V1:
        failures.add("INVALID_SCHEMA")
        failures.add("MISSING_SOURCE_LINEAGE")
        return _ordered_failures(failures)

    try:
        validate_canonical_condensation_artifact(proposal)
    except FailClosedRuntimeError as exc:
        if "identity mismatch" in str(exc):
            failures.add("REPLAY_IDENTITY_MISMATCH")
        else:
            failures.add("INVALID_SCHEMA")

    lineage = proposal.get("source_lineage")
    if not isinstance(lineage, dict):
        failures.add("MISSING_SOURCE_LINEAGE")
    else:
        _evaluate_source_lineage(lineage, expected_context, failures)

    commitments = proposal.get("semantic_commitments")
    if not _semantic_commitments_valid(commitments):
        failures.add("INVALID_SCHEMA")

    requirements = proposal.get("source_requirements")
    mappings = proposal.get("requirement_map")
    _evaluate_requirement_fidelity(
        requirements=requirements,
        mappings=mappings,
        commitments=commitments,
        body=proposal.get("proposed_synthesis_body"),
        failures=failures,
    )

    ambiguities = proposal.get("unresolved_ambiguities")
    if not isinstance(ambiguities, list):
        failures.add("INVALID_SCHEMA")
    elif ambiguities:
        failures.add("AMBIGUOUS_CONDENSED_OBJECTIVE")

    if not _proposal_method_valid(proposal):
        failures.add("UNSUPPORTED_PROPOSAL_METHOD")

    _evaluate_exact_projection(proposal, failures)
    return _ordered_failures(failures)


def _evaluate_source_lineage(
    lineage: dict[str, Any],
    expected_context: dict[str, Any],
    failures: set[str],
) -> None:
    original = lineage.get("original_request")
    objective = lineage.get("completed_objective")
    project = lineage.get("project_workspace")
    clarifications = lineage.get("clarification_evidence")
    clarification_hashes = lineage.get("clarification_evidence_hashes")
    clarification_resolution = lineage.get("clarification_resolution")
    required_lineage_fields = {
        "original_request",
        "clarification_complete",
        "clarification_evidence",
        "clarification_evidence_hashes",
        "clarification_resolution",
        "completed_objective",
        "project_workspace",
        "session_id",
        "invocation_id",
        "chain_id",
        "source_bundle_hash",
    }
    if not all(
        (
            set(lineage) == required_lineage_fields,
            isinstance(original, dict),
            set(original or ())
            == {
                "original_request_id",
                "original_request",
                "original_request_sha256",
            },
            isinstance(objective, dict),
            set(objective or ())
            == {
                "completed_objective_id",
                "completed_objective",
                "completed_objective_sha256",
                "source_original_request_sha256",
                "source_clarification_evidence_hashes",
            },
            isinstance(project, dict),
            set(project or ())
            == {
                "project_id",
                "workspace_id",
                "project_workspace_hash",
            },
            isinstance(clarifications, list),
            isinstance(clarification_hashes, list),
            isinstance(clarification_resolution, dict),
            isinstance(lineage.get("session_id"), str),
            lineage.get("session_id"),
            isinstance(lineage.get("source_bundle_hash"), str),
        )
    ):
        failures.add("MISSING_SOURCE_LINEAGE")
        return
    try:
        original_hash = content_sha256(original.get("original_request"))
        objective_hash = content_sha256(objective.get("completed_objective"))
        expected_clarifications = []
        for item in clarifications:
            if not isinstance(item, dict):
                raise FailClosedRuntimeError("clarification evidence invalid")
            canonical = deepcopy(item)
            actual = canonical.pop("clarification_evidence_hash", None)
            if (
                content_sha256(canonical.get("question"))
                != canonical.get("question_sha256")
                or content_sha256(canonical.get("answer"))
                != canonical.get("answer_sha256")
                or replay_hash(canonical) != actual
            ):
                failures.add("SOURCE_HASH_MISMATCH")
            expected_clarifications.append(actual)
            if item.get("resolved") is not True:
                failures.add("INCOMPLETE_CLARIFICATION")
        resolution_seed = deepcopy(clarification_resolution)
        resolution_hash = resolution_seed.pop(
            "clarification_resolution_hash",
            None,
        )
        expected_resolution_status = (
            "COMPLETE_WITH_EVIDENCE"
            if lineage.get("clarification_complete") is True and clarifications
            else "COMPLETE_NO_CLARIFICATION_REQUIRED"
            if lineage.get("clarification_complete") is True
            else "INCOMPLETE"
        )
        if any(
            (
                clarification_resolution.get("resolution_status")
                != expected_resolution_status,
                clarification_resolution.get("clarification_evidence_count")
                != len(clarifications),
                resolution_hash != replay_hash(resolution_seed),
            )
        ):
            failures.add("SOURCE_HASH_MISMATCH")
        source_seed = deepcopy(lineage)
        actual_bundle_hash = source_seed.pop("source_bundle_hash", None)
        project_seed = {
            "project_id": project.get("project_id"),
            "workspace_id": project.get("workspace_id"),
        }
        if any(
            (
                original_hash != original.get("original_request_sha256"),
                objective_hash != objective.get("completed_objective_sha256"),
                objective.get("source_original_request_sha256") != original_hash,
                objective.get("source_clarification_evidence_hashes")
                != expected_clarifications,
                clarification_hashes != expected_clarifications,
                project.get("project_workspace_hash") != replay_hash(project_seed),
                actual_bundle_hash != replay_hash(source_seed),
            )
        ):
            failures.add("SOURCE_HASH_MISMATCH")
        if lineage.get("clarification_complete") is not True:
            failures.add("INCOMPLETE_CLARIFICATION")
        _evaluate_expected_context(
            lineage=lineage,
            original_hash=original_hash,
            objective_hash=objective_hash,
            expected_context=expected_context,
            failures=failures,
        )
    except (FailClosedRuntimeError, TypeError, AttributeError):
        failures.add("SOURCE_HASH_MISMATCH")


def _evaluate_expected_context(
    *,
    lineage: dict[str, Any],
    original_hash: str,
    objective_hash: str,
    expected_context: dict[str, Any],
    failures: set[str],
) -> None:
    if not expected_context:
        return
    project = lineage["project_workspace"]
    actual = {
        "project_id": project.get("project_id"),
        "workspace_id": project.get("workspace_id"),
        "session_id": lineage.get("session_id"),
        "invocation_id": lineage.get("invocation_id"),
        "chain_id": lineage.get("chain_id"),
        "original_request_sha256": original_hash,
        "completed_objective_sha256": objective_hash,
    }
    if any(actual.get(field) != value for field, value in expected_context.items()):
        failures.add("SOURCE_HASH_MISMATCH")


def _evaluate_requirement_fidelity(
    *,
    requirements: Any,
    mappings: Any,
    commitments: Any,
    body: Any,
    failures: set[str],
) -> None:
    if not isinstance(requirements, list) or not isinstance(mappings, list):
        failures.add("INVALID_SCHEMA")
        failures.add("MATERIAL_REQUIREMENT_UNMAPPED")
        return
    sources = {
        item.get("requirement_id"): item
        for item in requirements
        if isinstance(item, dict) and isinstance(item.get("requirement_id"), str)
    }
    mapped = {
        item.get("requirement_id"): item
        for item in mappings
        if isinstance(item, dict) and isinstance(item.get("requirement_id"), str)
    }
    if not sources or set(sources) != set(mapped) or len(sources) != len(requirements):
        failures.add("MATERIAL_REQUIREMENT_UNMAPPED")
    if len(mapped) != len(mappings):
        failures.add("MATERIAL_REQUIREMENT_UNMAPPED")
    if not isinstance(body, str):
        failures.add("INVALID_SCHEMA")
        failures.add("MATERIAL_REQUIREMENT_LOSS")
        return
    for requirement_id, source in sources.items():
        mapping = mapped.get(requirement_id)
        if not isinstance(mapping, dict):
            continue
        source_text = source.get("source_text")
        representation = mapping.get("exact_condensed_representation")
        target = mapping.get("target_semantic_field")
        try:
            source_hash = content_sha256(source_text)
            representation_hash = content_sha256(representation)
        except FailClosedRuntimeError:
            failures.add("MATERIAL_REQUIREMENT_LOSS")
            continue
        if any(
            (
                source.get("source_requirement_sha256") != source_hash,
                mapping.get("source_requirement_sha256") != source_hash,
                mapping.get("exact_condensed_representation_sha256")
                != representation_hash,
                target != source.get("requirement_type"),
                target not in SEMANTIC_COMMITMENT_FIELDS,
                representation not in body,
                not _commitment_contains(commitments, target, representation),
            )
        ):
            failures.add("MATERIAL_REQUIREMENT_LOSS")


def _semantic_commitments_valid(commitments: Any) -> bool:
    if not isinstance(commitments, dict):
        return False
    if frozenset(commitments) != frozenset(SEMANTIC_COMMITMENT_FIELDS):
        return False
    for field in SCALAR_SEMANTIC_COMMITMENT_FIELDS:
        value = commitments.get(field)
        if not isinstance(value, str) or not value:
            return False
    for field in LIST_SEMANTIC_COMMITMENT_FIELDS:
        value = commitments.get(field)
        if (
            not isinstance(value, list)
            or not value
            or any(not isinstance(item, str) or not item for item in value)
            or len(value) != len(set(value))
        ):
            return False
    return True


def _commitment_contains(commitments: Any, field: Any, representation: str) -> bool:
    if not isinstance(commitments, dict) or field not in commitments:
        return False
    value = commitments[field]
    if field in SCALAR_SEMANTIC_COMMITMENT_FIELDS:
        return value == representation
    return isinstance(value, list) and representation in value


def _proposal_method_valid(proposal: dict[str, Any]) -> bool:
    if proposal.get("proposal_method") != CANONICAL_CONDENSATION_PROPOSAL_METHOD:
        return False
    evidence = proposal.get("proposal_method_evidence")
    if not isinstance(evidence, dict):
        return False
    seed = deepcopy(evidence)
    actual_hash = seed.pop("ruleset_hash", None)
    return bool(
        evidence.get("ruleset_id") == CANONICAL_CONDENSATION_RULESET_ID
        and evidence.get("proposal_is_selected_input") is True
        and evidence.get("automatic_retry_allowed") is False
        and evidence.get("semantic_inference_allowed") is False
        and evidence.get("constraint_discard_allowed") is False
        and actual_hash == replay_hash(seed)
    )


def _evaluate_exact_projection(
    proposal: dict[str, Any],
    failures: set[str],
) -> None:
    body = proposal.get("proposed_synthesis_body")
    prefix = proposal.get("projection_prefix")
    projection = proposal.get("proposed_projection")
    if not all(isinstance(value, str) for value in (body, prefix, projection)):
        failures.add("INVALID_SCHEMA")
        return
    try:
        body_hash = content_sha256(body)
        prefix_hash = content_sha256(prefix)
        projection_hash = content_sha256(projection)
    except FailClosedRuntimeError:
        failures.add("INVALID_SCHEMA")
        return
    expected_projection = f"{G31_CODEX_SYNTHESIS_PREFIX}{body}"
    if any(
        (
            prefix != G31_CODEX_SYNTHESIS_PREFIX,
            proposal.get("projection_prefix_contract_id")
            != G31_CODEX_SYNTHESIS_PREFIX_CONTRACT_V1,
            proposal.get("projection_prefix_code_point_count") != len(prefix),
            proposal.get("projection_prefix_utf8_byte_count")
            != len(prefix.encode("utf-8")),
            proposal.get("projection_prefix_sha256") != prefix_hash,
            proposal.get("proposed_synthesis_body_code_point_count") != len(body),
            proposal.get("proposed_synthesis_body_utf8_byte_count")
            != len(body.encode("utf-8")),
            proposal.get("proposed_synthesis_body_sha256") != body_hash,
            projection != expected_projection,
            proposal.get("proposed_projection_code_point_count")
            != len(projection),
            proposal.get("proposed_projection_utf8_byte_count")
            != len(projection.encode("utf-8")),
            proposal.get("proposed_projection_sha256") != projection_hash,
            proposal.get("maximum_projection_code_point_count")
            != G31_CODEX_SYNTHESIS_MAXIMUM_CHARACTER_COUNT,
            proposal.get("character_counting_contract")
            != "PYTHON_UNICODE_CODE_POINTS",
        )
    ):
        failures.add("VALIDATOR_DISAGREEMENT")
    if not body or body != body.strip():
        failures.add("INVALID_SCHEMA")
    if len(expected_projection) > G31_CODEX_SYNTHESIS_MAXIMUM_CHARACTER_COUNT:
        failures.add("EXCESSIVE_CANONICAL_REQUEST_LENGTH")


def _canonical_observation(proposal: Any) -> dict[str, Any]:
    if isinstance(proposal, dict):
        return deepcopy(proposal)
    return {
        "artifact_type": None,
        "invalid_observation_type": type(proposal).__name__,
    }


def _canonical_expected_context(
    expected_context: dict[str, Any] | None,
) -> dict[str, Any]:
    if expected_context is None:
        return {}
    if not isinstance(expected_context, dict):
        raise FailClosedRuntimeError("expected condensation context must be an object")
    if not set(expected_context).issubset(_EXPECTED_CONTEXT_FIELDS):
        raise FailClosedRuntimeError("expected condensation context field set mismatch")
    result = deepcopy(expected_context)
    for field in ("project_id", "workspace_id", "session_id"):
        if field in result and (
            not isinstance(result[field], str) or not result[field].strip()
        ):
            raise FailClosedRuntimeError(
                f"expected condensation context {field} is invalid"
            )
    for field in ("invocation_id", "chain_id"):
        if field in result and result[field] is not None and (
            not isinstance(result[field], str) or not result[field].strip()
        ):
            raise FailClosedRuntimeError(
                f"expected condensation context {field} is invalid"
            )
    return result


def _safe_content_hash(value: str) -> str | None:
    try:
        return content_sha256(value)
    except FailClosedRuntimeError:
        return None


def _ordered_failures(failures: set[str]) -> list[str]:
    return [code for code in FAILURE_CODE_ORDER if code in failures]


def _check_detail(code: str, passed: bool) -> str:
    return (
        f"{code} not observed"
        if passed
        else f"{code} observed; proposal is fail-closed"
    )
