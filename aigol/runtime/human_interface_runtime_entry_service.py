"""Canonical Human Interface Runtime Entry Service.

The service is the shared Platform Core entry boundary for human interfaces.
Interfaces collect human input and approval, then delegate the composed request
here. The service restores Platform Core project context, resolves development
intent, and enters the certified governed conversation runtime through an
injected runner supplied by the embedding interface.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from copy import deepcopy
from dataclasses import replace
import os
from pathlib import Path
import tempfile
from typing import Any

from aigol.runtime import codex_replacement_acceptance_prerequisite_binding_runtime as replacement_prerequisites
from aigol.runtime import codex_satisfied_outcome_disposable_validation_binding_runtime as disposable_validation
from aigol.runtime import codex_task_outcome_human_review_runtime as codex_task_review
from aigol.runtime import codex_transport_to_worker_result_capture_binding_runtime as codex_result
from aigol.runtime import codex_worker_activation_binding_runtime as worker_activation
from aigol.runtime import codex_worker_result_to_semantic_validation_binding_runtime as codex_validation
from aigol.runtime import (
    canonical_governed_development_condensation_g31_input_binding_runtime
    as condensation_input_binding,
)
from aigol.runtime import (
    canonical_governed_development_condensation_human_decision_runtime
    as condensation_decision,
)
from aigol.runtime import (
    canonical_governed_development_condensation_human_review_runtime
    as condensation_review,
)
from aigol.runtime import (
    canonical_governed_development_condensation_replay as condensation_replay,
)
from aigol.runtime import (
    canonical_governed_development_condensation_runtime as condensation_proposal,
)
from aigol.runtime import (
    canonical_governed_development_condensation_validation_runtime
    as condensation_validation,
)
from aigol.runtime import execution_runtime
from aigol.runtime import (
    filesystem_replace_worker_output_to_result_capture_binding_runtime
    as filesystem_result_capture,
)
from aigol.runtime import (
    filesystem_replace_worker_result_capture_to_result_validation_binding_runtime
    as filesystem_result_validation,
)
from aigol.runtime import (
    filesystem_replace_worker_schema_aware_authorization_lineage_resolver_runtime
    as filesystem_post_execution_review,
)
from aigol.runtime import (
    filesystem_replace_worker_selection_lineage_resolver_runtime
    as filesystem_selection_lineage,
)
from aigol.runtime import generated_content_acceptance_runtime as generated_acceptance
from aigol.runtime import governed_termination_runtime as governed_termination
from aigol.runtime import (
    governed_termination_to_final_execution_certification_binding_runtime
    as final_execution_certification,
)
from aigol.runtime import governed_worker_execution_runtime as governed_execution
from aigol.runtime import human_decision_runtime as human_decision
from aigol.runtime import platform_core_existing_file_governance as existing_file_governance
from aigol.runtime import platform_core_existing_file_mutation_candidate as existing_file_candidate
from aigol.runtime import worker_assignment_runtime as worker_assignment
from aigol.runtime import worker_dispatch_runtime as worker_dispatch
from aigol.runtime import worker_invocation_request_runtime as worker_request
from aigol.runtime import worker_invocation_runtime as worker_invocation
from aigol.runtime import worker_invocation_to_execution_candidate_bridge_runtime as worker_candidate
from aigol.runtime.confirmed_grounded_execution_authorization_binding import (
    authorize_confirmed_grounded_execution_decision,
    render_authorized_grounded_worker_selection,
    select_authorized_grounded_worker,
)
from aigol.runtime.canonical_human_entry_contract_v1 import (
    ACTIVE_CONTINUATION,
    ADVANCED,
    CANONICAL_CHE_CONTINUATION_CONTRACT_VERSION,
    CANONICAL_CHE_OWNER_TRANSITION_CONTRACT_VERSION,
    CANONICAL_CHE_REQUEST_CONTRACT_VERSION,
    CANONICAL_CHE_RESPONSE_CONTRACT_VERSION,
    DELIVERY_COMMITTED_NOT_ADVANCED,
    DELIVERY_COMMITTED_RESPONSE_FOUND,
    DELIVERY_ENTERED_NOT_ADVANCED,
    DELIVERY_NOT_APPLICABLE,
    DELIVERY_NOT_FOUND,
    DELIVERY_OUTCOME_UNKNOWN,
    DELIVERY_RESOLUTION_DISPOSITION,
    DELIVERY_RESPONSE_COMMITTED_ACKNOWLEDGEMENT_UNKNOWN,
    HUMAN_ACTOR,
    INFORMATIONAL_DISPOSITION,
    INFORMATIONAL_RESPONSE,
    LEGACY_CANONICAL_CHE_RESPONSE_CONTRACT_VERSION,
    MANUAL_REVIEW_REQUIRED,
    NO_RECOVERY_REQUIRED,
    NOT_ADVANCED,
    NOT_APPLICABLE,
    NOT_RETRYABLE,
    PENDING_DISPOSITION,
    PENDING_RESPONSE,
    QUERY_DELIVERY_STATUS,
    REFERENCE_CREATED,
    REFERENCE_NOT_CREATED,
    REFERENCE_NOT_APPLICABLE,
    REFUSED_ADVANCEMENT,
    REFUSED_DISPOSITION,
    REFUSAL_RESPONSE,
    RESUBMIT_EXACT_REQUEST,
    RESUBMIT_PERMITTED_CONTROL,
    RETRYABLE,
    TERMINAL_ADVANCEMENT,
    TERMINAL_CONTINUATION,
    TERMINAL_DISPOSITION,
    TERMINAL_RESPONSE,
    USE_RESOLVED_RESPONSE,
    CanonicalContinuationEnvelopeV1,
    CanonicalHumanEntryDeliveryResolutionQueryV1,
    CanonicalHumanEntryOwnerTransitionV1,
    CanonicalHumanEntryRequestEnvelopeV1,
    CanonicalHumanEntryResponseEnvelopeV1,
    canonical_che_delivery_resolution_query_from_request_v1,
    canonical_che_request_source_act_digest_v1,
    validate_canonical_che_continuation_envelope_v1,
    validate_canonical_che_request_envelope_v1,
    validate_canonical_che_response_envelope_v1,
)
from aigol.runtime.canonical_human_authority_act_contract_v1 import (
    AUTHORIZATION,
    CLARIFICATION_RESPONSE,
    COMMITMENT,
    CONFIRMATION,
    HUMAN_AUTHORITY_OWNER,
    CanonicalHumanAuthorityActV1,
    bind_canonical_human_authority_act_to_che_v1,
    canonical_human_authority_act_from_request_v1,
    validate_canonical_human_authority_act_v1,
)
from aigol.runtime.authority_provenance import (
    BOUNDED_EVIDENCE_REDUCTION_POLICY_AUTHORIZATION,
)
from aigol.runtime.profile_a_authority_process_boundary import (
    request_profile_a_bounded_evidence_reduction_decision_v1,
    request_profile_a_owner_state_issuance_v1,
)
from aigol.runtime.canonical_che_evidence_correlation_contract_v1 import (
    CANONICAL_CHE_EVIDENCE_CORRELATION_CONTRACT_VERSION,
    DELIVERY_OUTCOME_UNKNOWN as CORRELATION_DELIVERY_OUTCOME_UNKNOWN,
    NOT_APPLICABLE as CORRELATION_NOT_APPLICABLE,
    RECORDED as CORRELATION_RECORDED,
    REFERENCE_CREATED as CORRELATION_REFERENCE_CREATED,
    REFERENCE_NOT_CREATED as CORRELATION_REFERENCE_NOT_CREATED,
    UNAVAILABLE_PRE_WRITE,
    CanonicalCHEEvidenceCorrelationV1,
    canonical_che_response_evidence_digest_v1,
    create_canonical_che_evidence_correlation_v1,
    persist_canonical_che_evidence_correlation_v1,
    validate_canonical_che_evidence_correlation_v1,
)
from aigol.runtime.canonical_opaque_reference_contract_v1 import (
    AVAILABLE as REFERENCE_AVAILABLE,
    CanonicalOpaqueReferenceSetV1,
    canonical_opaque_reference_set_from_request_v1,
    canonical_opaque_reference_source_payload_from_request_v1,
    validate_canonical_opaque_reference_set_v1,
)
from aigol.runtime.execution_authorization_runtime import render_execution_authorization_summary
from aigol.runtime.grounded_execution_authorization_human_decision_binding import (
    EXECUTION_DECISION_APPROVED,
    EXECUTION_DECISION_REJECTED,
    bind_distinct_human_execution_decision,
    render_distinct_human_execution_decision,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_project_services import (
    latest_platform_core_workspace_state,
    prepare_unified_human_interface_project_context,
    record_unified_human_interface_workspace_state,
    replay_backed_uhi_clarification_state,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash
from aigol.workers import filesystem_replace_worker


CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_SERVICE_VERSION = (
    "G14_30_CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_SERVICE_V1"
)
CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_BOUND = (
    "CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_BOUND"
)
CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_PARTIALLY_BOUND = (
    "CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_PARTIALLY_BOUND"
)
CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_NOT_REQUIRED = (
    "CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_NOT_REQUIRED"
)
G31_APPLICATION_TRANSITION_VERSION = (
    "G31_COMMON_HUMAN_INTERFACE_APPLICATION_TRANSITION_V1"
)
CANONICAL_CONDENSATION_ENTRY_INTEGRATION_VERSION = (
    "G35_13_CANONICAL_CONDENSATION_ENTRY_INTEGRATION_V1"
)
G31_CANONICAL_CONDENSATION_DECISION = "G31_CANONICAL_CONDENSATION_DECISION"
G31_EXECUTION_DECISION = "G31_EXECUTION_DECISION"
G31_WORKER_ACTIVATION_DECISION = "G31_WORKER_ACTIVATION_DECISION"
G31_TASK_OUTCOME_DECISION = "G31_TASK_OUTCOME_DECISION"
G31_DISPOSABLE_VALIDATION_DECISION = "G31_DISPOSABLE_VALIDATION_DECISION"
G31_CONTENT_ACCEPTANCE_DECISION = "G31_CONTENT_ACCEPTANCE_DECISION"
G31_MUTATION_DECISION = "G31_MUTATION_DECISION"
G31_APPROVE = "APPROVE"
G31_REJECT = "REJECT"
G31_TASK_OUTCOME_SATISFIED = "TASK_OUTCOME_SATISFIED"
G31_TASK_OUTCOME_UNSATISFIED = "TASK_OUTCOME_UNSATISFIED"
G31_REWORK_REQUESTED = "REWORK_REQUESTED"
G31_CONTENT_ACCEPTED = "ACCEPTED"
G31_CONTENT_REJECTED = "REJECTED"
G31_MUTATION_APPROVED = "APPROVED"
G31_MUTATION_REJECTED = "REJECTED"

CANONICAL_CHE_CONTINUATION_BINDING_VERSION = (
    "G69_05_CANONICAL_CHE_CONTINUATION_BINDING_V2"
)
_CONTINUATION_AVAILABLE = "AVAILABLE"
_CONTINUATION_CONSUMED = "CONSUMED"
_CONTINUATION_BINDING_FIELDS = frozenset(
    {
        "binding_version",
        "envelope",
        "interface_identity",
        "adapter_identity",
        "workspace_identity",
        "runtime_scope_identity",
        "consumption_state",
        "consumed_by_request_identity",
        "consumed_by_idempotency_identity",
        "binding_hash",
    }
)

CANONICAL_CHE_DELIVERY_RESOLUTION_RECORD_VERSION = (
    "G69_11_CANONICAL_CHE_DELIVERY_RESOLUTION_RECORD_V3"
)
_G69_07_CANONICAL_CHE_DELIVERY_RESOLUTION_RECORD_VERSION = (
    "G69_07_CANONICAL_CHE_DELIVERY_RESOLUTION_RECORD_V2"
)
_LEGACY_CANONICAL_CHE_DELIVERY_RESOLUTION_RECORD_VERSION = (
    "G69_05_CANONICAL_CHE_DELIVERY_RESOLUTION_RECORD_V1"
)
_DELIVERY_RECORD_OUTCOME_UNKNOWN = DELIVERY_OUTCOME_UNKNOWN
_DELIVERY_RECORD_ENTERED_NOT_ADVANCED = DELIVERY_ENTERED_NOT_ADVANCED
_DELIVERY_RECORD_COMMITTED = (
    DELIVERY_RESPONSE_COMMITTED_ACKNOWLEDGEMENT_UNKNOWN
)
_DELIVERY_RESOLUTION_RECORD_FIELDS = frozenset(
    {
        "record_version",
        "request_identity",
        "source_act_digest",
        "request_binding_hash",
        "idempotency_identity",
        "actor_identity",
        "session_identity",
        "workspace_identity",
        "runtime_scope_identity",
        "interaction_identity",
        "authority_act_identity",
        "authority_act_digest",
        "producing_owner",
        "owner_state_identity",
        "owner_revision_before",
        "owner_revision_after",
        "advancement_outcome",
        "response_identity",
        "serialized_response",
        "response_hash",
        "delivery_state",
        "evidence_references",
        "evidence_correlation",
        "record_hash",
    }
)
_LEGACY_DELIVERY_RESOLUTION_RECORD_FIELDS = (
    _DELIVERY_RESOLUTION_RECORD_FIELDS
    - {"authority_act_identity", "authority_act_digest", "evidence_correlation"}
)
_G69_07_DELIVERY_RESOLUTION_RECORD_FIELDS = (
    _DELIVERY_RESOLUTION_RECORD_FIELDS - {"evidence_correlation"}
)
_G69_05_WITH_G69_11_CORRELATION_FIELDS = (
    _DELIVERY_RESOLUTION_RECORD_FIELDS
    - {"authority_act_identity", "authority_act_digest"}
)


GovernedRuntimeRunner = Callable[..., dict[str, Any]]


def run_human_interface_runtime_entry(
    *,
    interface_name: str | None = None,
    session_id: str | None = None,
    human_requests: list[str] | None = None,
    created_at: str | None = None,
    runtime_root: str | Path | None = None,
    workspace: str | Path | None = None,
    governed_runtime_runner: GovernedRuntimeRunner,
    presentation: dict[str, Any] | None = None,
    operator_context: str = "CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY",
    explicit_canonical_artifacts: list[dict[str, Any]] | tuple[dict[str, Any], ...] = (),
    explicit_canonical_artifact_references: list[Any] | tuple[Any, ...] = (),
    approved_implementation_turn_binding: dict[str, Any] | None = None,
    approved_development_composition_plan_hash: str | None = None,
    approved_durable_governed_work_hash: str | None = None,
    approved_proposal_preview_hash: str | None = None,
    approved_approval_request_hash: str | None = None,
    g31_application_state: dict[str, Any] | None = None,
    g31_human_action: str | None = None,
    g31_human_actor_id: str = "HUMAN_OPERATOR",
    g31_worker_process_runner: Callable[..., Any] | None = None,
    g31_synthesis_preflight_prompt: str | None = None,
    canonical_condensation_proposal_inputs: dict[str, Any] | None = None,
    worker_capability_completion_capture: dict[str, Any] | None = None,
    request_envelope: CanonicalHumanEntryRequestEnvelopeV1 | dict[str, Any] | None = None,
    continuation_envelope: CanonicalContinuationEnvelopeV1 | dict[str, Any] | None = None,
) -> dict[str, Any] | CanonicalHumanEntryResponseEnvelopeV1:
    """Enter CHE through the canonical envelope or its legacy boundary adapter."""

    if request_envelope is not None:
        if any(
            value is not None
            for value in (
                interface_name,
                session_id,
                human_requests,
                created_at,
                runtime_root,
                workspace,
                presentation,
                approved_implementation_turn_binding,
                approved_development_composition_plan_hash,
                approved_durable_governed_work_hash,
                approved_proposal_preview_hash,
                approved_approval_request_hash,
                g31_application_state,
                g31_human_action,
                g31_synthesis_preflight_prompt,
                canonical_condensation_proposal_inputs,
                worker_capability_completion_capture,
            )
        ) or explicit_canonical_artifacts or explicit_canonical_artifact_references:
            raise FailClosedRuntimeError(
                "canonical CHE request envelope cannot be mixed with legacy inputs"
            )
        if (
            operator_context != "CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY"
            or g31_human_actor_id != "HUMAN_OPERATOR"
            or g31_worker_process_runner is not None
        ):
            raise FailClosedRuntimeError(
                "canonical CHE request envelope cannot select a legacy workflow"
            )
        canonical_request = validate_canonical_che_request_envelope_v1(
            request_envelope
        )
        resolution_query = canonical_che_delivery_resolution_query_from_request_v1(
            canonical_request
        )
        if resolution_query is not None:
            if continuation_envelope is not None:
                raise FailClosedRuntimeError(
                    "CHE delivery resolution query cannot carry a continuation"
                )
            return _resolve_canonical_che_delivery_v1(
                canonical_request, resolution_query
            )
        authority_act = canonical_human_authority_act_from_request_v1(
            canonical_request
        )
        if authority_act is not None and continuation_envelope is None:
            raise FailClosedRuntimeError(
                "Human Authority Act requires a CHE continuation"
            )
        reference_set = canonical_opaque_reference_set_from_request_v1(
            canonical_request, continuation_envelope
        )
        return _execute_canonical_che_request_v1(
            canonical_request,
            lambda request: _run_human_interface_runtime_entry_owner_execution_v1(
                interface_name=request.interface_identity,
                session_id=request.session_identity,
                human_requests=[
                    _canonical_che_authority_payload_text_v1(
                        request, authority_act, reference_set
                    )
                ],
                created_at=request.created_at,
                runtime_root=request.runtime_scope_identity,
                workspace=request.workspace_identity,
                governed_runtime_runner=governed_runtime_runner,
                presentation=(
                    {
                        "canonical_opaque_reference_set": (
                            reference_set.to_dict()
                        )
                    }
                    if reference_set is not None
                    else None
                ),
                g31_human_actor_id=request.actor_identity,
            ),
            continuation_envelope=continuation_envelope,
            bind_continuation=True,
            authority_act=authority_act,
            reference_set=reference_set,
        )

    if continuation_envelope is not None:
        raise FailClosedRuntimeError(
            "CHE continuation envelope requires a canonical request envelope"
        )

    legacy_request = _legacy_canonical_che_request_envelope_v1(
        interface_name=interface_name,
        session_id=session_id,
        human_requests=human_requests,
        created_at=created_at,
        runtime_root=runtime_root,
        workspace=workspace,
        presentation=presentation,
        actor_identity=g31_human_actor_id,
    )
    captured_owner_result: dict[str, Any] = {}

    def legacy_owner_execution(
        _request: CanonicalHumanEntryRequestEnvelopeV1,
    ) -> dict[str, Any]:
        result = _run_human_interface_runtime_entry_owner_execution_v1(
            interface_name=_require_string(interface_name, "interface_name"),
            session_id=_require_string(session_id, "session_id"),
            human_requests=_require_legacy_human_requests(human_requests),
            created_at=_require_string(created_at, "created_at"),
            runtime_root=_require_legacy_path(runtime_root, "runtime_root"),
            workspace=_require_legacy_path(workspace, "workspace"),
            governed_runtime_runner=governed_runtime_runner,
            presentation=presentation,
            operator_context=operator_context,
            explicit_canonical_artifacts=explicit_canonical_artifacts,
            explicit_canonical_artifact_references=(
                explicit_canonical_artifact_references
            ),
            approved_implementation_turn_binding=approved_implementation_turn_binding,
            approved_development_composition_plan_hash=(
                approved_development_composition_plan_hash
            ),
            approved_durable_governed_work_hash=approved_durable_governed_work_hash,
            approved_proposal_preview_hash=approved_proposal_preview_hash,
            approved_approval_request_hash=approved_approval_request_hash,
            g31_application_state=g31_application_state,
            g31_human_action=g31_human_action,
            g31_human_actor_id=g31_human_actor_id,
            g31_worker_process_runner=g31_worker_process_runner,
            g31_synthesis_preflight_prompt=g31_synthesis_preflight_prompt,
            canonical_condensation_proposal_inputs=(
                canonical_condensation_proposal_inputs
            ),
            worker_capability_completion_capture=worker_capability_completion_capture,
        )
        captured_owner_result.update(result)
        return result

    _execute_canonical_che_request_v1(
        legacy_request,
        legacy_owner_execution,
        bind_continuation=False,
    )
    return captured_owner_result


def _execute_canonical_che_request_v1(
    request: CanonicalHumanEntryRequestEnvelopeV1,
    owner_executor: Callable[
        [CanonicalHumanEntryRequestEnvelopeV1], dict[str, Any]
    ],
    *,
    continuation_envelope: CanonicalContinuationEnvelopeV1 | dict[str, Any] | None = None,
    bind_continuation: bool = True,
    authority_act: CanonicalHumanAuthorityActV1 | None = None,
    reference_set: CanonicalOpaqueReferenceSetV1 | None = None,
) -> CanonicalHumanEntryResponseEnvelopeV1:
    canonical_request = validate_canonical_che_request_envelope_v1(request)
    canonical_authority_act = (
        validate_canonical_human_authority_act_v1(authority_act)
        if authority_act is not None
        else None
    )
    supplied_reference_set = (
        validate_canonical_opaque_reference_set_v1(reference_set)
        if reference_set is not None
        else None
    )
    request_reference_set = canonical_opaque_reference_set_from_request_v1(
        canonical_request, continuation_envelope
    )
    if supplied_reference_set != request_reference_set:
        raise FailClosedRuntimeError(
            "CHE opaque Reference Request binding is inconsistent"
        )
    canonical_reference_set = request_reference_set
    if not bind_continuation:
        owner_result = owner_executor(canonical_request)
        if not isinstance(owner_result, dict):
            raise FailClosedRuntimeError(
                "canonical CHE owner execution returned a malformed result"
            )
        response = _canonical_che_response_from_owner_result(
            canonical_request,
            owner_result,
            prior_continuation=None,
            strict_owner_projection=False,
        )
        compatibility_record = {
            "actor_identity": canonical_request.actor_identity,
            "session_identity": canonical_request.session_identity,
            "workspace_identity": canonical_request.workspace_identity,
            "runtime_scope_identity": canonical_request.runtime_scope_identity,
            "idempotency_identity": canonical_request.idempotency_identity,
        }
        response, correlation = _canonical_che_bind_evidence_correlation_v1(
            request=canonical_request,
            delivery_record=compatibility_record,
            response=response,
            prior_continuation=None,
            authority_act=None,
            reference_set=None,
        )
        persist_canonical_che_evidence_correlation_v1(correlation)
        return response

    scope_lock = (
        _acquire_canonical_che_continuation_scope_v1(canonical_request)
        if bind_continuation
        else None
    )
    try:
        supplied_continuation = (
            validate_canonical_che_continuation_envelope_v1(continuation_envelope)
            if continuation_envelope is not None
            else None
        )
        existing_delivery = _existing_canonical_che_delivery_record_v1(
            canonical_request
        )
        if existing_delivery is not None:
            _validate_canonical_che_delivery_request_binding_v1(
                existing_delivery,
                canonical_request,
                supplied_continuation,
            )
            if existing_delivery["delivery_state"] == _DELIVERY_RECORD_COMMITTED:
                if canonical_authority_act is not None:
                    _persist_profile_a_owner_state_authorization_if_applicable_v1(
                        request=canonical_request,
                        continuation=supplied_continuation,
                        authority_act=canonical_authority_act,
                        correlation=existing_delivery["evidence_correlation"],
                    )
                return _response_from_canonical_che_delivery_record_v1(
                    existing_delivery
                )
            return _canonical_che_delivery_resolution_response_v1(
                canonical_request,
                existing_delivery,
                status=existing_delivery["delivery_state"],
            )

        if canonical_authority_act is not None:
            if supplied_continuation is None:
                raise FailClosedRuntimeError(
                    "Human Authority Act requires a CHE continuation"
                )
            if supplied_continuation.continuation_state == TERMINAL_CONTINUATION:
                raise FailClosedRuntimeError(
                    "Human Authority Act cannot target a terminal continuation"
                )
            _assert_canonical_che_authority_act_not_duplicate_v1(
                canonical_request, canonical_authority_act
            )
            _validate_canonical_che_authority_owner_binding_v1(
                canonical_request,
                supplied_continuation,
                canonical_authority_act,
            )

        if canonical_reference_set is not None:
            _assert_canonical_che_reference_retry_lineage_v1(
                canonical_request, canonical_reference_set
            )

        delivery_record = _begin_canonical_che_delivery_record_v1(
            canonical_request,
            supplied_continuation,
            authority_act=canonical_authority_act,
        )
        if canonical_reference_set is not None:
            unavailable_reference = next(
                (
                    reference
                    for reference in canonical_reference_set.references
                    if reference.availability_status != REFERENCE_AVAILABLE
                ),
                None,
            )
            if unavailable_reference is not None:
                response = _canonical_che_reference_rejection_response_v1(
                    canonical_request,
                    canonical_reference_set,
                    unavailable_reference,
                    supplied_continuation,
                )
                response, correlation = _canonical_che_bind_evidence_correlation_v1(
                    request=canonical_request,
                    delivery_record=delivery_record,
                    response=response,
                    prior_continuation=supplied_continuation,
                    authority_act=canonical_authority_act,
                    reference_set=canonical_reference_set,
                )
                _commit_canonical_che_delivery_response_v1(
                    delivery_record, response, correlation
                )
                return response
        try:
            prior_continuation = _prepare_canonical_che_continuation_v1(
                canonical_request,
                supplied_continuation,
                authority_act=canonical_authority_act,
            )
            _validate_canonical_che_expected_owner_revision_v1(
                canonical_request, prior_continuation
            )
        except Exception:
            correlation = _canonical_che_evidence_correlation_v1(
                request=canonical_request,
                delivery_record=delivery_record,
                response=None,
                continuation=supplied_continuation,
                authority_act=canonical_authority_act,
                reference_set=canonical_reference_set,
                delivery_status=DELIVERY_ENTERED_NOT_ADVANCED,
                evidence_status=UNAVAILABLE_PRE_WRITE,
            )
            _mark_canonical_che_delivery_not_advanced_v1(
                delivery_record, correlation
            )
            persist_canonical_che_evidence_correlation_v1(correlation)
            raise
        try:
            owner_result = owner_executor(canonical_request)
            if not isinstance(owner_result, dict):
                raise FailClosedRuntimeError(
                    "canonical CHE owner execution returned a malformed result"
                )
            response = _canonical_che_response_from_owner_result(
                canonical_request,
                owner_result,
                prior_continuation=prior_continuation,
                strict_owner_projection=True,
            )
        except Exception:
            correlation = _canonical_che_evidence_correlation_v1(
                request=canonical_request,
                delivery_record=delivery_record,
                response=None,
                continuation=prior_continuation,
                authority_act=canonical_authority_act,
                reference_set=canonical_reference_set,
                delivery_status=DELIVERY_OUTCOME_UNKNOWN,
                evidence_status=CORRELATION_DELIVERY_OUTCOME_UNKNOWN,
            )
            updated = dict(delivery_record)
            updated["evidence_correlation"] = correlation.to_dict()
            updated["record_hash"] = _canonical_che_delivery_record_hash_v1(
                updated
            )
            path = _canonical_che_delivery_record_path_v1(
                runtime_scope_identity=updated["runtime_scope_identity"],
                actor_identity=updated["actor_identity"],
                session_identity=updated["session_identity"],
                workspace_identity=updated["workspace_identity"],
                idempotency_identity=updated["idempotency_identity"],
            )
            _write_canonical_che_delivery_record_v1(path, updated)
            persist_canonical_che_evidence_correlation_v1(correlation)
            raise
        if canonical_reference_set is not None:
            response = _canonical_che_bind_reference_projection_v1(
                canonical_request, response, canonical_reference_set
            )
        issued_continuation = _issue_canonical_che_continuation_v1(
            canonical_request,
            response,
            owner_result,
            prior_continuation=prior_continuation,
        )
        final_response = replace(
            response,
            continuation_envelope=issued_continuation,
            owner_projection=None,
            presentation=None,
            common_failure=None,
        )
        final_response, correlation = _canonical_che_bind_evidence_correlation_v1(
            request=canonical_request,
            delivery_record=delivery_record,
            response=final_response,
            prior_continuation=prior_continuation,
            authority_act=canonical_authority_act,
            reference_set=canonical_reference_set,
        )
        if final_response.continuation_envelope is not None:
            _persist_canonical_che_continuation_v1(
                canonical_request, final_response.continuation_envelope
            )
        _commit_canonical_che_delivery_response_v1(
            delivery_record, final_response, correlation
        )
        if canonical_authority_act is not None:
            _persist_profile_a_owner_state_authorization_if_applicable_v1(
                request=canonical_request,
                continuation=prior_continuation,
                authority_act=canonical_authority_act,
                correlation=correlation,
            )
        return final_response
    finally:
        if scope_lock is not None:
            _release_canonical_che_continuation_scope_v1(scope_lock)


def _run_human_interface_runtime_entry_owner_execution_v1(
    *,
    interface_name: str,
    session_id: str,
    human_requests: list[str],
    created_at: str,
    runtime_root: str | Path,
    workspace: str | Path,
    governed_runtime_runner: GovernedRuntimeRunner,
    presentation: dict[str, Any] | None = None,
    operator_context: str = "CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY",
    explicit_canonical_artifacts: list[dict[str, Any]] | tuple[dict[str, Any], ...] = (),
    explicit_canonical_artifact_references: list[Any] | tuple[Any, ...] = (),
    approved_implementation_turn_binding: dict[str, Any] | None = None,
    approved_development_composition_plan_hash: str | None = None,
    approved_durable_governed_work_hash: str | None = None,
    approved_proposal_preview_hash: str | None = None,
    approved_approval_request_hash: str | None = None,
    g31_application_state: dict[str, Any] | None = None,
    g31_human_action: str | None = None,
    g31_human_actor_id: str = "HUMAN_OPERATOR",
    g31_worker_process_runner: Callable[..., Any] | None = None,
    g31_synthesis_preflight_prompt: str | None = None,
    canonical_condensation_proposal_inputs: dict[str, Any] | None = None,
    worker_capability_completion_capture: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute established owner behavior after canonical request validation."""

    interface = _require_string(interface_name, "interface_name")
    session = _require_string(session_id, "session_id")
    created = _require_string(created_at, "created_at")
    root = Path(runtime_root)
    workspace_text = str(Path(workspace))
    if worker_capability_completion_capture is not None:
        from aigol.runtime.platform_change_normalization_worker_completion_adapter import (
            present_platform_change_normalization_worker_completion,
        )

        completion = present_platform_change_normalization_worker_completion(
            worker_capability_completion_capture
        )
        return {
            "canonical_runtime_entry_service_version": (
                CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_SERVICE_VERSION
            ),
            "canonical_runtime_entry_interface": interface,
            "canonical_runtime_entry_session_id": session,
            "canonical_runtime_entry_workspace": workspace_text,
            "canonical_runtime_entry_status": CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_BOUND,
            "runtime_binding_status": CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_BOUND,
            "runtime_entered": False,
            "human_interface_completion_returned": True,
            "worker_capability_completion": completion,
            "human_visible_completion_result": deepcopy(
                completion["human_visible_result"]
            ),
            "governance_authorization_reached": None,
            "provider_invocation_reached": False,
            "worker_execution_reached": True,
            "replay_certification_reached": False,
            "human_interface_runtime_entry_orchestrates": False,
            "human_interface_resolves_artifacts": False,
            "human_interface_validates_artifacts": False,
            "human_interface_selects_artifacts": False,
            "human_interface_influences_semantic_selection": False,
            "platform_core_runtime_delegated": True,
            "manual_chatgpt_codex_transfer_required": False,
        }
    if g31_synthesis_preflight_prompt is not None:
        prompt = _require_string(
            g31_synthesis_preflight_prompt, "g31_synthesis_preflight_prompt"
        )
        condensation_required = (
            len(worker_activation.CODEX_SYNTHESIS_PREFIX + prompt)
            > worker_activation.CODEX_SYNTHESIS_MAXIMUM_CHARACTER_COUNT
        )
        if condensation_required:
            if canonical_condensation_proposal_inputs is None:
                preflight = worker_activation.preflight_codex_worker_synthesis(
                    prompt
                )
                return _g31_application_result(
                    {
                        "canonical_condensation_entry_integration_version": (
                            CANONICAL_CONDENSATION_ENTRY_INTEGRATION_VERSION
                        ),
                        "canonical_condensation_entry_status": (
                            "CANONICAL_CONDENSATION_PROPOSAL_INPUT_REQUIRED_"
                            "FAILED_CLOSED"
                        ),
                        "canonical_condensation_required": True,
                        "canonical_condensation_direct_input_over_bound": True,
                        "codex_synthesis_preflight_capture": preflight,
                    },
                    interface_name=interface,
                    presentations=(
                        worker_activation.render_codex_worker_synthesis_preflight(
                            preflight
                        ),
                        "Canonical condensation is required before this exact "
                        "over-bound request can reach a later G31 preflight.",
                    ),
                )
            return _begin_canonical_condensation_entry_transition(
                interface_name=interface,
                session=session,
                root=root,
                workspace_path=workspace_text,
                created=created,
                original_request=prompt,
                reviewed_by=_require_string(
                    g31_human_actor_id, "g31_human_actor_id"
                ),
                proposal_inputs=canonical_condensation_proposal_inputs,
            )
        if canonical_condensation_proposal_inputs is not None:
            raise FailClosedRuntimeError(
                "direct exact G31 input cannot contain condensation proposal inputs"
            )
        preflight = worker_activation.preflight_codex_worker_synthesis(
            prompt
        )
        return _g31_application_result(
            {"codex_synthesis_preflight_capture": preflight},
            interface_name=interface,
            presentations=(
                worker_activation.render_codex_worker_synthesis_preflight(preflight),
            ),
        )
    if g31_application_state is not None:
        return _continue_g31_application_transition(
            interface_name=interface,
            session=session,
            root=root,
            workspace_path=workspace_text,
            created=created,
            application_state=g31_application_state,
            human_action=g31_human_action,
            human_actor_id=g31_human_actor_id,
            worker_process_runner=g31_worker_process_runner,
        )
    requests = [_require_string(request, "human_request") for request in human_requests]

    result = deepcopy(presentation) if isinstance(presentation, dict) else {}
    constitutional_execution_spine_completion = None
    committed_objective_record = result.pop(
        "g60_02_committed_objective_record", None
    )
    approved_identity_consumption = None
    authenticated_scope_binding = None
    scope_binding_candidates = [
        artifact
        for artifact in explicit_canonical_artifacts
        if isinstance(artifact, dict)
        and artifact.get("artifact_type") == "REUSE_PROOF_G47_SCOPE_BINDING_V1"
    ]
    if len(scope_binding_candidates) > 1:
        raise FailClosedRuntimeError(
            "exactly one Reuse Proof/G47 scope binding may be transported"
        )
    if scope_binding_candidates:
        from aigol.runtime.constitutional_reuse_proof_production_gate import (
            validate_reuse_proof_g47_scope_binding,
        )

        authenticated_scope_binding = validate_reuse_proof_g47_scope_binding(
            scope_binding_candidates[0]
        )
        if not isinstance(approved_implementation_turn_binding, dict):
            raise FailClosedRuntimeError(
                "Reuse Proof/G47 scope binding requires an approved implementation turn"
            )
        bound_turn = authenticated_scope_binding["g47_operational_record"].get(
            "implementation_turn_binding"
        )
        if (
            not isinstance(bound_turn, dict)
            or bound_turn.get("artifact_hash")
            != approved_implementation_turn_binding.get("artifact_hash")
        ):
            raise FailClosedRuntimeError(
                "Reuse Proof/G47 scope binding implementation-turn lineage mismatch"
            )
    if approved_implementation_turn_binding is not None:
        from aigol.runtime.platform_implementation_turn_durable_work_binding import (
            consume_approved_implementation_turn_binding,
        )

        approved_identity_consumption = consume_approved_implementation_turn_binding(
            binding_artifact=approved_implementation_turn_binding,
            development_composition_plan_hash=_require_string(
                approved_development_composition_plan_hash,
                "approved_development_composition_plan_hash",
            ),
            durable_governed_work_hash=_require_string(
                approved_durable_governed_work_hash,
                "approved_durable_governed_work_hash",
            ),
            proposal_preview_hash=_require_string(
                approved_proposal_preview_hash,
                "approved_proposal_preview_hash",
            ),
            approval_request_hash=_require_string(
                approved_approval_request_hash,
                "approved_approval_request_hash",
            ),
            created_at=created,
            replay_dir=_require_string(
                approved_implementation_turn_binding.get("replay_reference"),
                "approved_implementation_turn_replay_reference",
            ),
        )
        project_contexts = []
        intent_resolutions = [
            {
                "runtime_binding_admissible": True,
                "canonical_runtime_prompt": requests[0],
                "work_type": "IMPLEMENTATION",
                "canonical_implementation_turn_binding": deepcopy(
                    approved_implementation_turn_binding
                ),
                "canonical_implementation_turn_binding_hash": (
                    approved_implementation_turn_binding.get("artifact_hash")
                ),
                "approved_identity_consumption": deepcopy(
                    approved_identity_consumption
                ),
            }
        ]
    elif committed_objective_record is not None:
        if operator_context != "G60_02_COMMITTED_OBJECTIVE_HANDOFF":
            raise FailClosedRuntimeError(
                "committed Objective transport requires the exact G60-02 context"
            )
        if len(requests) != 1:
            raise FailClosedRuntimeError(
                "committed Objective transport requires exactly one request"
            )
        from aigol.runtime.human_interface_conversation_execution_integration_v2 import (
            validate_committed_objective_admission_transport_v2,
        )

        validate_committed_objective_admission_transport_v2(
            committed_objective_record,
            platform_core_prompt=requests[0],
        )
        context = prepare_unified_human_interface_project_context(
            interface_name=interface,
            session_id=session,
            message=requests[0],
            runtime_root=root,
            workspace=workspace_text,
            created_at=created,
            explicit_canonical_artifacts=explicit_canonical_artifacts,
            explicit_canonical_artifact_references=(
                explicit_canonical_artifact_references
            ),
        )
        production_conversation_bindings = []
        project_contexts = [context]
        intent_resolutions = [context["development_intent_resolution"]]
    elif len(requests) == 1 and requests[0].strip().startswith("/authorize "):
        from aigol.runtime.human_interface_conversation_execution_integration_v2 import (
            authorize_pending_committed_objective_execution_v2,
        )

        constitutional_execution_spine_completion = (
            authorize_pending_committed_objective_execution_v2(
                runtime_root=(
                    root / session / "canonical_typed_semantic_admission"
                ),
                session_id=session,
                explicit_authorization_action=requests[0],
                human_actor=g31_human_actor_id,
                authorized_at=created,
            )
        )
        prepared = constitutional_execution_spine_completion["prepared"]
        context = prepared["platform_core_project_context"]
        production_conversation_bindings = []
        project_contexts = [context]
        intent_resolutions = [context["development_intent_resolution"]]
    else:
        from aigol.runtime.production_conversation_flow_binding import (
            compose_production_conversation_flow_binding_v1,
        )

        production_conversation_bindings = []
        project_contexts = []
        for request in requests:
            prior_workspace_state = latest_platform_core_workspace_state(
                root / session
            )
            production_binding = compose_production_conversation_flow_binding_v1(
                interface_identity=interface,
                session_identity=session,
                request_text=request,
                runtime_root=root,
                workspace_identity=workspace_text,
                created_at=created,
                prior_workspace_state=prior_workspace_state,
            )
            commitment = production_binding.get("objective_commitment")
            if isinstance(commitment, dict):
                from aigol.runtime.human_interface_conversation_execution_integration_v2 import (
                    prepare_committed_objective_execution_v2,
                )

                prepared = prepare_committed_objective_execution_v2(
                    commitment_record=commitment["commitment_record"],
                    explicit_canonical_artifacts=[
                        deepcopy(item) for item in explicit_canonical_artifacts
                    ],
                    explicit_canonical_artifact_references=(
                        explicit_canonical_artifact_references
                    ),
                    runtime_root=(
                        root / session / "canonical_typed_semantic_admission"
                    ),
                    workspace=workspace_text,
                    session_id=session,
                    human_actor=g31_human_actor_id,
                    created_at=created,
                )
                context = prepared["hir_admission"].get(
                    "platform_core_project_services_context"
                )
                if not isinstance(context, dict):
                    raise FailClosedRuntimeError(
                        "committed Objective admission context is absent"
                    )
                production_binding["g60_02_admission_handoff"] = prepared
                production_binding["g60_02_execution_preparation"] = prepared
            else:
                context = prepare_unified_human_interface_project_context(
                    interface_name=interface,
                    session_id=session,
                    message=request,
                    runtime_root=root,
                    workspace=workspace_text,
                    created_at=created,
                    explicit_canonical_artifacts=explicit_canonical_artifacts,
                    explicit_canonical_artifact_references=(
                        explicit_canonical_artifact_references
                    ),
                    human_intent_precedence_decision=production_binding[
                        "human_intent_precedence_decision"
                    ],
                    production_conversation_flow_binding=production_binding[
                        "production_conversation_flow_binding"
                    ],
                )
            production_binding["project_services_invoked"] = True
            production_binding["project_services_context_hash"] = context.get(
                "artifact_hash"
            )
            if isinstance(
                context.get("owner_bound_clarification_envelope"), dict
            ):
                production_binding["owner_bound_clarification_envelope"] = deepcopy(
                    context["owner_bound_clarification_envelope"]
                )
            production_conversation_bindings.append(production_binding)
            project_contexts.append(context)
        intent_resolutions = [
            context["development_intent_resolution"]
            for context in project_contexts
            if isinstance(context.get("development_intent_resolution"), dict)
        ]
    runtime_prompts = [
        str(resolution.get("canonical_runtime_prompt") or request)
        for request, resolution in zip(requests, intent_resolutions)
        if resolution.get("runtime_binding_admissible") is True
        and operator_context != "AICLI_NEW_TURN_PRE_APPROVAL"
    ]
    read_only_work_results = [
        context.get("governed_read_only_work_result")
        for context in project_contexts
        if isinstance(context.get("governed_read_only_work_result"), dict)
    ]

    result.update(
        {
            "canonical_runtime_entry_service_version": (
                CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_SERVICE_VERSION
            ),
            "canonical_runtime_entry_interface": interface,
            "canonical_runtime_entry_session_id": session,
            "canonical_runtime_entry_workspace": workspace_text,
            "platform_core_project_services_contexts": project_contexts,
            "platform_core_project_services_context": project_contexts[-1] if project_contexts else None,
            "reuse_proof_g47_scope_binding": deepcopy(
                authenticated_scope_binding
            ),
            "reuse_proof_g47_scope_binding_hash": (
                authenticated_scope_binding.get("artifact_hash")
                if isinstance(authenticated_scope_binding, dict)
                else None
            ),
            "production_conversation_bindings": (
                production_conversation_bindings
                if approved_implementation_turn_binding is None
                else []
            ),
            "production_conversation_binding": (
                production_conversation_bindings[-1]
                if approved_implementation_turn_binding is None
                and production_conversation_bindings
                else None
            ),
            "production_conversation_flow_binding": (
                production_conversation_bindings[-1][
                    "production_conversation_flow_binding"
                ]
                if approved_implementation_turn_binding is None
                and production_conversation_bindings
                else None
            ),
            "human_intent_precedence_decision": (
                production_conversation_bindings[-1][
                    "human_intent_precedence_decision"
                ]
                if approved_implementation_turn_binding is None
                and production_conversation_bindings
                else None
            ),
            "owner_bound_clarification_envelope": (
                production_conversation_bindings[-1].get(
                    "owner_bound_clarification_envelope"
                )
                if approved_implementation_turn_binding is None
                and production_conversation_bindings
                else None
            ),
            "canonical_typed_semantic_composition": (
                production_conversation_bindings[-1].get(
                    "canonical_typed_semantic_composition"
                )
                if approved_implementation_turn_binding is None
                and production_conversation_bindings
                else None
            ),
            "committed_objective_admission": (
                production_conversation_bindings[-1].get(
                    "g60_02_admission_handoff"
                )
                if approved_implementation_turn_binding is None
                and production_conversation_bindings
                else None
            ),
            "committed_objective_execution_preparation": (
                production_conversation_bindings[-1].get(
                    "g60_02_execution_preparation"
                )
                if approved_implementation_turn_binding is None
                and production_conversation_bindings
                else None
            ),
            "constitutional_execution_spine_completion": (
                constitutional_execution_spine_completion
            ),
            "canonical_presentation_flow_binding_hash": (
                production_conversation_bindings[-1][
                    "production_conversation_flow_binding"
                ]["artifact_hash"]
                if approved_implementation_turn_binding is None
                and production_conversation_bindings
                else None
            ),
            "canonical_presentation_response_mode": (
                (
                    project_contexts[-1].get("human_conversation_experience")
                    or {}
                ).get("response_mode")
                if project_contexts
                else None
            ),
            "development_intent_resolutions": intent_resolutions,
            "development_intent_resolution": intent_resolutions[-1] if intent_resolutions else None,
            "approved_implementation_turn_binding": deepcopy(
                approved_implementation_turn_binding
            ),
            "approved_identity_consumption": deepcopy(approved_identity_consumption),
            "approved_identity_consumption_hash": (
                approved_identity_consumption.get("artifact_hash")
                if isinstance(approved_identity_consumption, dict)
                else None
            ),
            "approved_durable_work_identity_consumed": isinstance(
                approved_identity_consumption, dict
            ),
            "runtime_prompts": runtime_prompts,
            "read_only_work_results": read_only_work_results,
            "governed_read_only_work_result": (
                read_only_work_results[-1] if read_only_work_results else None
            ),
            "read_only_runtime_entered": bool(read_only_work_results),
            "read_only_work_binding_status": (
                read_only_work_results[-1].get("binding_status")
                if read_only_work_results
                else None
            ),
            "human_interface_runtime_entry_service_used": True,
            "human_interface_runtime_entry_orchestrates": False,
            "human_interface_resolves_artifacts": False,
            "human_interface_validates_artifacts": False,
            "human_interface_selects_artifacts": False,
            "human_interface_influences_semantic_selection": False,
            "platform_core_project_services_delegated": True,
            "production_conversation_binding_orchestrated": bool(
                approved_implementation_turn_binding is None
                and production_conversation_bindings
            ),
            "production_conversation_new_owner_created": False,
            "platform_core_runtime_delegated": True,
            "manual_chatgpt_codex_transfer_required": False,
        }
    )

    if not runtime_prompts:
        result.update(
            {
                "canonical_runtime_entry_status": (
                    CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_NOT_REQUIRED
                ),
                "runtime_binding_status": CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_NOT_REQUIRED,
                "runtime_entered": False,
                "runtime_turn_count": 0,
                "runtime_failed_turns": 0,
                "governance_authorization_reached": None,
                "provider_invocation_reached": None,
                "worker_execution_reached": None,
                "replay_certification_reached": None,
            }
        )
        workspace_state = record_unified_human_interface_workspace_state(
            interface_name=interface,
            session_id=session,
            runtime_root=root,
            workspace=workspace_text,
            created_at=created,
            completion=result,
            turn_results=[],
            pending_clarification=_owner_bound_pending_clarification(
                project_contexts[-1] if project_contexts else None,
                requests[-1] if requests else None,
            ),
            pending_summary=None,
        )
        result["project_workspace_replay_reference"] = workspace_state["replay_reference"]
        result["project_workspace_hash"] = workspace_state["artifact_hash"]
        return result

    conversation_args = argparse.Namespace(
        session_id=session,
        created_at=created,
        runtime_root=str(root),
        workspace=workspace_text,
        operator_context=operator_context,
        auto_continue=True,
        enable_llm_assisted_explanation=False,
        llm_explanation_provider_id="UNSPECIFIED_EXPLANATION_PROVIDER",
        approved_implementation_turn_binding_hash=(
            approved_implementation_turn_binding.get("artifact_hash")
            if isinstance(approved_implementation_turn_binding, dict)
            else None
        ),
        approved_identity_consumption_hash=(
            approved_identity_consumption.get("artifact_hash")
            if isinstance(approved_identity_consumption, dict)
            else None
        ),
        approved_durable_governed_work_id=(
            approved_implementation_turn_binding.get("durable_governed_work_id")
            if isinstance(approved_implementation_turn_binding, dict)
            else None
        ),
        approved_durable_governed_work_hash=(
            approved_implementation_turn_binding.get("durable_governed_work_hash")
            if isinstance(approved_implementation_turn_binding, dict)
            else None
        ),
        approved_proposal_preview_hash=(
            approved_implementation_turn_binding.get("proposal_preview_hash")
            if isinstance(approved_implementation_turn_binding, dict)
            else None
        ),
        approved_approval_request_hash=(
            approved_implementation_turn_binding.get("approval_request_hash")
            if isinstance(approved_implementation_turn_binding, dict)
            else None
        ),
        approved_implementation_turn_binding=deepcopy(
            approved_implementation_turn_binding
        ),
        approved_identity_consumption=deepcopy(approved_identity_consumption),
    )
    conversation_output: list[str] = []
    conversation_result = governed_runtime_runner(
        conversation_args,
        input_func=_input_sequence([*runtime_prompts, "exit"]),
        output_func=conversation_output.append,
    )
    latest_turn = _latest_turn(conversation_result)
    runtime_projection = _runtime_status_projection(conversation_result, latest_turn)
    runtime_bound = _runtime_bound(conversation_result, runtime_projection)
    canonical_status = (
        CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_BOUND
        if runtime_bound
        else CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_PARTIALLY_BOUND
    )
    result.update(
        {
            "canonical_runtime_entry_status": canonical_status,
            "runtime_binding_status": canonical_status,
            "runtime_entered": True,
            "runtime_command": conversation_result.get("command"),
            "runtime_root": conversation_result.get("runtime_root"),
            "runtime_turn_count": conversation_result.get("turn_count"),
            "runtime_failed_turns": conversation_result.get("failed_turns"),
            "runtime_exit_reason": conversation_result.get("exit_reason"),
            "runtime_response_source": latest_turn.get("response_source"),
            "runtime_response_status": latest_turn.get("response_status"),
            "auto_continue_enabled": conversation_result.get("auto_continue_enabled") is True,
            "approved_identity_transport_to_canonical_continuation": isinstance(
                approved_identity_consumption, dict
            ),
            "auto_continue_stop_reason": conversation_result.get("auto_continue_stop_reason"),
            "manual_chatgpt_codex_transfer_required": not runtime_bound,
            "execution_summary_presented": bool(latest_turn.get("execution_summary_reference")),
            "human_confirmation_presented": bool(latest_turn.get("human_confirmation_reference")),
            "governance_authorization_reached": runtime_projection[
                "governance_authorization_reached"
            ],
            "provider_invocation_reached": runtime_projection["provider_invocation_reached"],
            "worker_execution_reached": runtime_projection["worker_execution_reached"],
            "replay_certification_reached": runtime_projection["replay_certification_reached"],
            "runtime_status_projection_source": runtime_projection["projection_source"],
            "runtime_status_projection_evidence": runtime_projection["projection_evidence"],
            "execution_plan_generated": latest_turn.get("execution_preparation_status") == "EXECUTION_READY",
            "execution_plan_status": latest_turn.get("execution_preparation_status"),
            "worker_assignment_status": latest_turn.get("worker_assignment_status"),
            "worker_dispatch_status": latest_turn.get("worker_dispatch_status"),
            "worker_invocation_status": latest_turn.get("worker_invocation_status"),
            "worker_execution_candidate_reached": latest_turn.get("worker_execution_candidate_reached") is True,
            "external_task_package_reached": latest_turn.get("external_task_package_reached") is True,
            "openai_provider_reached": latest_turn.get("openai_provider_reached") is True,
            "universal_provider_runtime_reached": runtime_projection["universal_provider_runtime_reached"],
            "smart_provider_selection_reached": runtime_projection["smart_provider_selection_reached"],
            "universal_provider_worker_status": latest_turn.get("universal_provider_worker_status"),
            "universal_provider_worker_replay_reference": latest_turn.get(
                "universal_provider_worker_replay_reference"
            ),
            "selected_provider_resource_id": latest_turn.get("selected_provider_resource_id"),
            "smart_provider_selection_executed": latest_turn.get("smart_provider_selection_executed"),
            "result_validation_status": latest_turn.get("result_validation_status"),
            "replay_certification_status": latest_turn.get("replay_certification_status"),
            "replay_certification_replay_reference": latest_turn.get("replay_certification_replay_reference"),
            "execution_summary_reference": latest_turn.get("execution_summary_reference"),
            "human_confirmation_reference": latest_turn.get("human_confirmation_reference"),
            "runtime_replay_reference": latest_turn.get("replay_reference")
            or latest_turn.get("conversation_replay_reference"),
            "approved_worker_payload_binding_status": latest_turn.get(
                "approved_worker_payload_binding_status"
            ),
            "approved_worker_payload_binding_hash": latest_turn.get(
                "approved_worker_payload_binding_hash"
            ),
            "approved_ppp_task_package_hash": latest_turn.get(
                "approved_ppp_task_package_hash"
            ),
            "approved_implementation_request_hash": latest_turn.get(
                "approved_implementation_request_hash"
            ),
            "approved_worker_implementation_payload_hash": latest_turn.get(
                "approved_worker_implementation_payload_hash"
            ),
            "approved_worker_payload_dispatch_blocked": latest_turn.get(
                "approved_worker_payload_dispatch_blocked"
            )
            is True,
            "approved_worker_payload_failure_reason": latest_turn.get(
                "approved_worker_payload_failure_reason"
            )
            if latest_turn.get("approved_worker_payload_binding_hash")
            else None,
            "repository_scope_grounding_status": latest_turn.get(
                "repository_scope_grounding_status"
            ),
            "repository_scope_grounding_hash": latest_turn.get(
                "repository_scope_grounding_hash"
            ),
            "repository_cognition_snapshot_hash": latest_turn.get(
                "repository_cognition_snapshot_hash"
            ),
            "grounded_repository_targets": deepcopy(
                latest_turn.get("grounded_repository_targets") or []
            ),
            "grounded_focused_test_targets": deepcopy(
                latest_turn.get("grounded_focused_test_targets") or []
            ),
            "grounded_worker_request_hash": latest_turn.get(
                "grounded_worker_request_hash"
            ),
            "repository_scope_dispatch_blocked": latest_turn.get(
                "repository_scope_dispatch_blocked"
            )
            is True,
            "authorization_review_status": latest_turn.get(
                "authorization_review_status"
            ),
            "authorization_review_hash": latest_turn.get(
                "authorization_review_hash"
            ),
            "authorization_review_artifact": deepcopy(
                latest_turn.get("authorization_review_artifact")
            )
            if isinstance(latest_turn.get("authorization_review_artifact"), dict)
            else None,
            "authorization_scope_hash": latest_turn.get(
                "authorization_scope_hash"
            ),
            "execution_summary_hash": latest_turn.get(
                "execution_summary_hash"
            ),
            "distinct_human_execution_authorization_required": latest_turn.get(
                "distinct_human_execution_authorization_required"
            )
            is True,
            "human_confirmation_required": latest_turn.get(
                "human_confirmation_required"
            )
            is True,
            "execution_authorization_required": latest_turn.get(
                "execution_authorization_required"
            )
            is True,
            "proposal_approval_is_execution_authorization": latest_turn.get(
                "proposal_approval_is_execution_authorization"
            )
            is True,
            "execution_authorized": latest_turn.get("execution_authorized") is True,
            "worker_selected": latest_turn.get("worker_selected") is True,
            "authorization_dispatch_blocked": latest_turn.get(
                "authorization_dispatch_blocked"
            )
            is True,
            "conversation_output_tail": conversation_output[-12:],
            "governance_authority_preserved": True,
            "provider_platform_preserved": True,
            "worker_execution_authority_preserved": True,
            "replay_authority_preserved": True,
        }
    )
    workspace_state = record_unified_human_interface_workspace_state(
        interface_name=interface,
        session_id=session,
        runtime_root=root,
        workspace=workspace_text,
        created_at=created,
        completion=result,
        turn_results=[result],
        pending_clarification=None,
        pending_summary=None,
    )
    result["project_workspace_replay_reference"] = workspace_state["replay_reference"]
    result["project_workspace_hash"] = workspace_state["artifact_hash"]
    review = result.get("authorization_review_artifact")
    if isinstance(review, dict) and review.get("authorization_review_status") == (
        "GROUNDED_WORKER_REQUEST_EXECUTION_AUTHORIZATION_REVIEW_REQUIRED"
    ):
        return _g31_application_result(
            result,
            interface_name=interface,
            pending_action=_pending_action(
                G31_EXECUTION_DECISION,
                ("APPROVE", "REJECT"),
                review,
            ),
            presentations=(
                "Development proposal approval is complete. A distinct execution "
                "decision is now pending. No execution is authorized yet.",
            ),
        )
    return _g31_application_result(result, interface_name=interface)


def _begin_canonical_condensation_entry_transition(
    *,
    interface_name: str,
    session: str,
    root: Path,
    workspace_path: str,
    created: str,
    original_request: str,
    reviewed_by: str,
    proposal_inputs: dict[str, Any],
) -> dict[str, Any]:
    """Prepare one over-bound request for an explicit semantic decision."""

    if not isinstance(proposal_inputs, dict):
        raise FailClosedRuntimeError(
            "canonical condensation proposal inputs must be an object"
        )
    required_fields = {
        "original_request_id",
        "clarification_evidence",
        "clarification_complete",
        "completed_objective_id",
        "completed_objective",
        "project_id",
        "semantic_commitments",
        "source_requirements",
        "requirement_mappings",
        "proposed_synthesis_body",
    }
    optional_fields = {
        "invocation_id",
        "chain_id",
        "unresolved_ambiguities",
        "proposal_method",
        "proposal_method_evidence",
    }
    supplied_fields = set(proposal_inputs)
    missing = sorted(required_fields - supplied_fields)
    unexpected = sorted(supplied_fields - required_fields - optional_fields)
    if missing or unexpected:
        raise FailClosedRuntimeError(
            "canonical condensation proposal input field mismatch: "
            f"missing={missing}, unexpected={unexpected}"
        )

    proposal = condensation_proposal.create_canonical_condensation_proposal(
        original_request_id=proposal_inputs["original_request_id"],
        original_request=original_request,
        clarification_evidence=proposal_inputs["clarification_evidence"],
        clarification_complete=proposal_inputs["clarification_complete"],
        completed_objective_id=proposal_inputs["completed_objective_id"],
        completed_objective=proposal_inputs["completed_objective"],
        project_id=proposal_inputs["project_id"],
        workspace_id=workspace_path,
        session_id=session,
        invocation_id=proposal_inputs.get("invocation_id"),
        chain_id=proposal_inputs.get("chain_id"),
        semantic_commitments=proposal_inputs["semantic_commitments"],
        source_requirements=proposal_inputs["source_requirements"],
        requirement_mappings=proposal_inputs["requirement_mappings"],
        proposed_synthesis_body=proposal_inputs["proposed_synthesis_body"],
        unresolved_ambiguities=proposal_inputs.get("unresolved_ambiguities", ()),
        proposal_method=proposal_inputs.get(
            "proposal_method",
            condensation_proposal.CANONICAL_CONDENSATION_PROPOSAL_METHOD,
        ),
        proposal_method_evidence=proposal_inputs.get("proposal_method_evidence"),
    )
    validation = condensation_validation.validate_canonical_condensation_proposal(
        proposal,
        expected_context={
            "project_id": proposal_inputs["project_id"],
            "workspace_id": workspace_path,
            "session_id": session,
            "invocation_id": proposal_inputs.get("invocation_id"),
            "chain_id": proposal_inputs.get("chain_id"),
            "original_request_sha256": condensation_proposal.content_sha256(
                original_request
            ),
            "completed_objective_sha256": condensation_proposal.content_sha256(
                proposal_inputs["completed_objective"]
            ),
        },
    )
    phase1_replay_dir = (
        root
        / session
        / (
            "CANONICAL-CONDENSATION-PHASE1-"
            f"{proposal['condensation_hash'].removeprefix('sha256:')[:24]}"
        )
    )
    phase1_capture = (
        condensation_replay.record_canonical_condensation_phase1_replay(
            proposal=proposal,
            validation_result=validation,
            recorded_at=created,
            replay_dir=phase1_replay_dir,
        )
    )
    state = {
        "canonical_condensation_entry_integration_version": (
            CANONICAL_CONDENSATION_ENTRY_INTEGRATION_VERSION
        ),
        "canonical_condensation_entry_status": (
            "CANONICAL_CONDENSATION_VALIDATION_FAILED_CLOSED"
            if validation["validation_status"]
            != condensation_validation.CANONICAL_CONDENSATION_VALIDATION_PASS
            else "CANONICAL_CONDENSATION_HUMAN_REVIEW_REQUIRED"
        ),
        "canonical_condensation_required": True,
        "canonical_condensation_direct_input_over_bound": True,
        "canonical_condensation_original_request": original_request,
        "canonical_condensation_proposal_capture": proposal,
        "canonical_condensation_validation_capture": validation,
        "canonical_condensation_phase1_replay_capture": phase1_capture,
        "canonical_condensation_phase1_replay_reference": str(
            phase1_replay_dir
        ),
        "canonical_condensation_human_review_capture": None,
        "canonical_condensation_human_decision_capture": None,
        "canonical_condensation_g31_input_binding_capture": None,
        "canonical_condensation_preflight_continuity_capture": None,
        "codex_synthesis_preflight_capture": None,
        "semantic_representation_approved": False,
        "execution_authorized": False,
        "worker_selected": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "repository_mutated": False,
    }
    if (
        validation["validation_status"]
        != condensation_validation.CANONICAL_CONDENSATION_VALIDATION_PASS
    ):
        return _g31_application_result(
            state,
            interface_name=interface_name,
            presentations=(
                "Canonical condensation validation failed closed. No human "
                "approval, G31 preflight, Worker, Provider, or mutation occurred.",
            ),
        )

    review = condensation_review.create_canonical_condensation_human_review(
        proposal=proposal,
        validation_result=validation,
        phase1_replay_dir=phase1_replay_dir,
        reviewed_by=reviewed_by,
        presented_at=created,
    )
    state["canonical_condensation_human_review_capture"] = review
    return _g31_application_result(
        state,
        interface_name=interface_name,
        pending_action=_pending_action(
            G31_CANONICAL_CONDENSATION_DECISION,
            (G31_APPROVE, G31_REJECT),
            review,
        ),
        presentations=(
            condensation_review.render_canonical_condensation_human_review(
                review,
                phase1_replay_dir=phase1_replay_dir,
            ),
        ),
    )


def _continue_canonical_condensation_entry_transition(
    *,
    interface_name: str,
    session: str,
    root: Path,
    workspace_path: str,
    created: str,
    state: dict[str, Any],
    review: dict[str, Any],
    action: str,
    actor: str,
) -> tuple[dict[str, Any], list[str]]:
    """Bind an explicit review decision and invoke only the unchanged preflight."""

    if state.get("canonical_condensation_human_review_capture") != review:
        raise FailClosedRuntimeError(
            "canonical condensation pending review state mismatch"
        )
    phase1_reference = review.get("phase1_replay_reference")
    if not isinstance(phase1_reference, dict):
        raise FailClosedRuntimeError(
            "canonical condensation Phase 1 Replay reference is required"
        )
    phase1_replay_dir = Path(
        _require_string(
            phase1_reference.get("replay_location"),
            "canonical_condensation_phase1_replay_location",
        )
    )
    proposal = review.get("condensation_proposal")
    if not isinstance(proposal, dict):
        raise FailClosedRuntimeError(
            "canonical condensation review proposal is required"
        )
    source_request = review.get("source_request")
    if (
        not isinstance(source_request, dict)
        or state.get("canonical_condensation_proposal_capture") != proposal
        or state.get("canonical_condensation_validation_capture")
        != review.get("deterministic_validation_result")
        or state.get("canonical_condensation_phase1_replay_reference")
        != str(phase1_replay_dir)
        or state.get("canonical_condensation_original_request")
        != source_request.get("original_request")
    ):
        raise FailClosedRuntimeError(
            "canonical condensation retained entry evidence mismatch"
        )
    lineage = proposal.get("source_lineage")
    project_workspace = (
        lineage.get("project_workspace") if isinstance(lineage, dict) else None
    )
    if (
        not isinstance(project_workspace, dict)
        or lineage.get("session_id") != session
        or project_workspace.get("workspace_id") != workspace_path
    ):
        raise FailClosedRuntimeError(
            "canonical condensation entry context lineage mismatch"
        )

    decision = condensation_decision.create_canonical_condensation_human_decision(
        review=review,
        phase1_replay_dir=phase1_replay_dir,
        decision=action,
        decided_by=actor,
        decided_at=created,
    )
    phase2_replay_dir = (
        root
        / session
        / (
            "CANONICAL-CONDENSATION-PHASE2-"
            f"{decision['human_decision_hash'].removeprefix('sha256:')[:24]}"
        )
    )
    phase2_capture = (
        condensation_replay.record_canonical_condensation_review_decision_replay(
            phase1_replay_dir=phase1_replay_dir,
            review=review,
            decision=decision,
            recorded_at=created,
            replay_dir=phase2_replay_dir,
        )
    )
    state.update(
        {
            "canonical_condensation_human_decision_capture": decision,
            "canonical_condensation_phase2_replay_capture": phase2_capture,
            "canonical_condensation_phase2_replay_reference": str(
                phase2_replay_dir
            ),
            "semantic_representation_approved": action == G31_APPROVE,
        }
    )
    if action == G31_REJECT:
        state["canonical_condensation_entry_status"] = (
            "CANONICAL_CONDENSATION_REJECTED"
        )
        return state, [
            "Canonical condensation rejected. No G31 preflight, Worker, "
            "Provider, authorization, or mutation occurred."
        ]

    binding = (
        condensation_input_binding.create_canonical_condensation_g31_input_binding(
            approved_replay_dir=phase2_replay_dir
        )
    )
    preflight = worker_activation.preflight_codex_worker_synthesis(
        binding["g31_function_argument"]
    )
    continuity = _canonical_condensation_preflight_continuity(
        binding=binding,
        preflight=preflight,
    )
    state.update(
        {
            "canonical_condensation_entry_status": (
                "CANONICAL_CONDENSATION_G31_PREFLIGHT_READY"
                if preflight["synthesis_preflight_status"]
                == "SYNTHESIS_PREFLIGHT_READY"
                else "CANONICAL_CONDENSATION_G31_PREFLIGHT_FAILED_CLOSED"
            ),
            "canonical_condensation_g31_input_binding_capture": binding,
            "canonical_condensation_preflight_continuity_capture": continuity,
            "codex_synthesis_preflight_capture": preflight,
        }
    )
    return state, [
        "Canonical condensation was explicitly approved and bound through the "
        "certified dedicated G31 input-binding runtime.",
        worker_activation.render_codex_worker_synthesis_preflight(preflight),
    ]


def _canonical_condensation_preflight_continuity(
    *,
    binding: dict[str, Any],
    preflight: dict[str, Any],
) -> dict[str, Any]:
    """Prove the unchanged G31 capture consumed exact Model D values."""

    expected = binding.get("preflight_input_tuple")
    if not isinstance(expected, dict):
        raise FailClosedRuntimeError(
            "canonical condensation preflight input tuple is required"
        )
    expected_argument = expected.get("g31_function_argument")
    expected_final = expected.get("g31_final_measured_request")
    if not isinstance(expected_argument, dict) or not isinstance(
        expected_final, dict
    ):
        raise FailClosedRuntimeError(
            "canonical condensation preflight value commitments are required"
        )
    checks = {
        "raw_request_equal": preflight.get("raw_request")
        == expected_argument.get("value")
        == binding.get("g31_function_argument"),
        "canonical_prefix_equal": preflight.get("canonical_prefix")
        == binding.get("approved_projection_prefix"),
        "final_request_equal": preflight.get("final_synthesized_request")
        == expected_final.get("value")
        == binding.get("g31_final_measured_request"),
        "raw_character_count_equal": preflight.get("raw_character_count")
        == expected_argument.get("code_point_count"),
        "prefix_character_count_equal": preflight.get("prefix_character_count")
        == binding.get("approved_projection_prefix_commitment", {}).get(
            "code_point_count"
        ),
        "final_character_count_equal": preflight.get("final_character_count")
        == expected_final.get("code_point_count"),
        "maximum_character_count_equal": preflight.get(
            "maximum_character_count"
        )
        == binding.get(
            "maximum_g31_final_measured_request_code_point_count"
        ),
        "character_counting_contract_equal": preflight.get(
            "character_counting_contract"
        )
        == expected_final.get("character_counting_contract"),
        "final_request_sha256_equal": preflight.get(
            "final_synthesized_request_sha256"
        )
        == expected_final.get("sha256"),
    }
    if not all(checks.values()):
        raise FailClosedRuntimeError(
            "canonical condensation to unchanged G31 preflight continuity mismatch"
        )
    artifact = {
        "artifact_type": (
            "CANONICAL_CONDENSATION_G31_PREFLIGHT_CONTINUITY_CAPTURE_V1"
        ),
        "integration_version": CANONICAL_CONDENSATION_ENTRY_INTEGRATION_VERSION,
        "binding_id": binding.get("binding_id"),
        "binding_hash": binding.get("binding_hash"),
        "preflight_hash": preflight.get("synthesis_preflight_hash"),
        "preflight_input_tuple_hash": binding.get("preflight_input_tuple_hash"),
        "checks": checks,
        "all_equal": True,
        "g31_preflight_invoked": True,
        "g31_preflight_behavior_modified": False,
        "authorization_created": False,
        "execution_authorized": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "repository_mutated": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _continue_g31_application_transition(
    *,
    interface_name: str,
    session: str,
    root: Path,
    workspace_path: str,
    created: str,
    application_state: dict[str, Any],
    human_action: str | None,
    human_actor_id: str,
    worker_process_runner: Callable[..., Any] | None,
) -> dict[str, Any]:
    """Continue one G31 application action through canonical low-level owners."""

    if not isinstance(application_state, dict):
        raise FailClosedRuntimeError("G31 application state must be a dict")
    pending = application_state.get("g31_pending_action")
    if human_action is None and not isinstance(pending, dict):
        review = application_state.get("authorization_review_artifact")
        if not isinstance(review, dict) or review.get("authorization_review_status") != (
            "GROUNDED_WORKER_REQUEST_EXECUTION_AUTHORIZATION_REVIEW_REQUIRED"
        ):
            raise FailClosedRuntimeError(
                "G31 application initialization requires the canonical execution review"
            )
        return _g31_application_result(
            application_state,
            interface_name=interface_name,
            pending_action=_pending_action(
                G31_EXECUTION_DECISION, (G31_APPROVE, G31_REJECT), review
            ),
            presentations=(
                "Development proposal approval is complete. A distinct execution "
                "decision is now pending. No execution is authorized yet.",
            ),
        )
    actor = _require_string(human_actor_id, "g31_human_actor_id")
    action = _require_string(human_action, "g31_human_action")
    if not isinstance(pending, dict):
        raise FailClosedRuntimeError("G31 canonical pending action is required")
    action_type = _require_string(pending.get("action_type"), "g31_pending_action_type")
    valid_values = pending.get("valid_values")
    if not isinstance(valid_values, list) or action not in valid_values:
        raise FailClosedRuntimeError(
            f"G31 action {action!r} is invalid for {action_type}"
        )
    context = pending.get("context")
    if not isinstance(context, dict):
        raise FailClosedRuntimeError("G31 canonical pending context is required")

    state = deepcopy(application_state)
    presentations: list[str] = []
    next_pending: dict[str, Any] | None = None

    if action_type == G31_CANONICAL_CONDENSATION_DECISION:
        state, presentations = _continue_canonical_condensation_entry_transition(
            interface_name=interface_name,
            session=session,
            root=root,
            workspace_path=workspace_path,
            created=created,
            state=state,
            review=context,
            action=action,
            actor=actor,
        )

    elif action_type == G31_EXECUTION_DECISION:
        state = _record_g31_execution_decision(
            pending_execution_review=context,
            decision=action,
            session=session,
            root=root,
            workspace_path=workspace_path,
            created=created,
            runtime_result=state,
            actor=actor,
        )
        presentations.append(
            render_distinct_human_execution_decision(
                state["execution_human_decision_result"]
            )
        )
        if action == "APPROVE" and state.get("governed_worker_execution_capture"):
            presentations.extend(_render_g31_execution_progress(state))
            review = worker_activation.prepare_codex_worker_activation_review(
                governed_execution_capture=state["governed_worker_execution_capture"],
                execution_candidate_capture=state["worker_execution_candidate_capture"],
                session_root=root / session,
                workspace=workspace_path,
                created_at=created,
                synthesis_preflight_capture=state.get("codex_synthesis_preflight_capture"),
            )
            state["codex_worker_activation_review_capture"] = review
            state["codex_worker_activation_synthesis_preflight_capture"] = deepcopy(
                review["synthesis_preflight_capture"]
            )
            presentations.append(worker_activation.render_codex_worker_activation_review(review))
            next_pending = _pending_action(
                G31_WORKER_ACTIVATION_DECISION, ("APPROVE", "REJECT"), review
            )

    elif action_type == G31_WORKER_ACTIVATION_DECISION:
        if action == "REJECT":
            state.update(
                {
                    "worker_activation_decision_rejected": True,
                    "third_human_decision_recorded": True,
                    "worker_process_activation_allowed": False,
                    "worker_process_started": False,
                    "provider_invoked": False,
                    "semantic_worker_result_captured": False,
                    "repository_mutated": False,
                }
            )
            presentations.append(
                "Bounded CODEX Worker process activation rejected; no process started."
            )
        else:
            state = _record_g31_worker_activation_decision(
                pending_activation_review=context,
                session=session,
                root=root,
                workspace_path=workspace_path,
                created=created,
                runtime_result=state,
                runner=worker_process_runner,
                actor=actor,
            )
            presentations.extend(
                (
                    worker_activation.render_codex_worker_activation_result(
                        state["codex_worker_activation_capture"]
                    ),
                    codex_result.render_codex_worker_result_capture(
                        state["codex_worker_result_capture_binding_capture"]
                    ),
                    codex_validation.render_codex_worker_semantic_validation(
                        state["codex_worker_semantic_validation_binding_capture"]
                    ),
                )
            )
            validation = state["codex_worker_semantic_validation_binding_capture"]
            if validation.get("g31_semantic_validation_status") == codex_validation.SUCCESS:
                state = _prepare_g31_task_outcome_review(
                    session=session,
                    root=root,
                    workspace_path=workspace_path,
                    created=created,
                    runtime_result=state,
                )
                review = state["codex_task_outcome_review_capture"]
                presentations.extend(
                    (
                        codex_task_review.render_codex_task_outcome_review(review),
                        _render_task_outcome_review_lineage(review),
                        "Exact-byte task-outcome decision pending. No decision accepts "
                        "or applies the patch.",
                    )
                )
                next_pending = _pending_action(
                    G31_TASK_OUTCOME_DECISION,
                    (
                        codex_task_review.TASK_OUTCOME_SATISFIED,
                        codex_task_review.TASK_OUTCOME_UNSATISFIED,
                        codex_task_review.REWORK_REQUESTED,
                    ),
                    review,
                )
            else:
                state["task_outcome_review_blocked"] = True
                state["task_outcome_review_blocker"] = (
                    "G31 governance validation did not return RESULT_VALIDATED"
                )
                presentations.append(
                    "Task-outcome review was not requested because G31 governance "
                    "validation did not return RESULT_VALIDATED."
                )

    elif action_type == G31_TASK_OUTCOME_DECISION:
        state = _record_g31_task_outcome_decision(
            pending_task_outcome_review=context,
            task_outcome_decision=action,
            session=session,
            root=root,
            workspace_path=workspace_path,
            created=created,
            runtime_result=state,
            actor=actor,
        )
        presentations.append(
            codex_task_review.render_codex_task_outcome_decision(
                state["codex_task_outcome_human_decision_capture"]
            )
        )
        if action == codex_task_review.TASK_OUTCOME_SATISFIED:
            try:
                state = _prepare_g31_disposable_patch_validation_review(
                    session=session,
                    root=root,
                    workspace_path=workspace_path,
                    created=created,
                    runtime_result=state,
                )
            except FailClosedRuntimeError as exc:
                state["disposable_patch_validation_review_blocked"] = True
                state["disposable_patch_validation_review_blocker"] = str(exc)
                presentations.append(
                    f"Disposable patch-validation review failed closed: {exc}"
                )
            else:
                review = state["disposable_patch_validation_review_capture"]
                presentations.extend(
                    (
                        disposable_validation.render_disposable_patch_validation_review(
                            review, state["codex_task_outcome_review_capture"]
                        ),
                        "Disposable-only validation decision pending. No patch or test has run.",
                    )
                )
                next_pending = _pending_action(
                    G31_DISPOSABLE_VALIDATION_DECISION,
                    (human_decision.APPROVE, human_decision.REJECT),
                    review,
                )

    elif action_type == G31_DISPOSABLE_VALIDATION_DECISION:
        state = _record_g31_disposable_patch_validation_decision(
            pending_review=context,
            decision=action,
            session=session,
            root=root,
            workspace_path=workspace_path,
            created=created,
            runtime_result=state,
            actor=actor,
        )
        presentations.append(
            human_decision.render_human_decision_summary(
                state["disposable_patch_validation_human_decision_capture"]
            )
        )
        if action == human_decision.APPROVE:
            state = _execute_g31_disposable_patch_validation(
                session=session,
                root=root,
                workspace_path=workspace_path,
                created=created,
                runtime_result=state,
                actor=actor,
            )
            outcome = state["disposable_patch_validation_outcome_capture"]
            presentations.append(
                disposable_validation.render_disposable_patch_validation_outcome(outcome)
            )
            if outcome["outcome_artifact"]["execution_status"] == disposable_validation.COMPLETED:
                state = _bind_g31_replacement_acceptance_prerequisites(
                    session=session,
                    root=root,
                    workspace_path=workspace_path,
                    created=created,
                    runtime_result=state,
                )
                presentations.append(
                    replacement_prerequisites.render_codex_replacement_acceptance_prerequisites(
                        state["codex_replacement_acceptance_prerequisite_binding_capture"],
                        state["codex_replacement_acceptance_prerequisite_binding_reconstruction"],
                    )
                )
                binding = state[
                    "codex_replacement_acceptance_prerequisite_binding_capture"
                ]["binding_artifact"]
                content_context = human_decision.prepare_content_acceptance_decision_context(
                    context_id=f"G31-CONTENT-ACCEPTANCE-{binding['artifact_hash'][-16:]}",
                    binding_capture=state[
                        "codex_replacement_acceptance_prerequisite_binding_capture"
                    ],
                    human_actor_id=actor,
                    presented_at=created,
                    session_root=root / session,
                    replay_dir=root / session
                    / f"CONTENT-ACCEPTANCE-DECISION-{binding['artifact_hash'][-16:]}",
                )
                state["human_content_acceptance_context_capture"] = content_context
                presentations.append(
                    human_decision.render_content_acceptance_decision_context(content_context)
                )
                next_pending = _pending_action(
                    G31_CONTENT_ACCEPTANCE_DECISION,
                    (human_decision.ACCEPTED, human_decision.REJECTED),
                    content_context,
                )

    elif action_type == G31_CONTENT_ACCEPTANCE_DECISION:
        state, next_pending, content_presentations = _record_g31_content_decision(
            context_capture=context,
            outcome=action,
            session=session,
            root=root,
            workspace_path=workspace_path,
            created=created,
            runtime_result=state,
            actor=actor,
        )
        presentations.extend(content_presentations)

    elif action_type == G31_MUTATION_DECISION:
        state = _record_g31_mutation_decision(
            context_capture=context,
            outcome=action,
            session=session,
            root=root,
            workspace_path=workspace_path,
            created=created,
            runtime_result=state,
            actor=actor,
        )
        presentations.append(
            human_decision.render_existing_file_mutation_decision(
                state["human_mutation_decision_capture"]
            )
        )
        if action == human_decision.MUTATION_APPROVED:
            state = _authorize_g31_mutation_decision(
                session=session,
                root=root,
                workspace_path=workspace_path,
                created=created,
                runtime_result=state,
            )
            authorization = state[
                "mutation_authorization_actor_replay_reconstruction"
            ]
            request = state["authenticated_replacement_request"]
            request_replay = state[
                "authenticated_replacement_request_reconstruction"
            ]
            consumption = state["authorization_consumption_reconstruction"]
            presentations.append(
                "\n".join(
                    (
                        "Canonical Existing-File Mutation Authorization",
                        f"Authorization ID: {authorization['authorization_id']}",
                        f"Authorization Status: {authorization['authorization_status']}",
                        "Canonical Authorization Actor: "
                        f"{authorization['canonical_authorization_actor']}",
                        f"Target Path: {authorization['target_path']}",
                        "Authorization Replay Recorded: True",
                        "Authorization Consumed: True",
                        "Authenticated Replacement Request",
                        f"Request ID: {request['request_id']}",
                        f"Request Hash: {request['request_hash']}",
                        f"Request Replay Hash: {request_replay['replay_hash']}",
                        "Replacement Request Created: True",
                        "Single-Use Consumption Identity: "
                        f"{consumption['consumption_identity']}",
                        "Authorization Consumption Reached: True",
                        "Worker Selection Reached: True",
                        "Worker Invocation Request Created: "
                        f"{state['worker_invocation_request_created']}",
                        "Worker Assignment Reached: True",
                        "Worker Dispatch Reached: True",
                        "Worker Invocation Reached: True",
                        "Worker Execution Handoff Reached: True",
                        f"Execution Status: {state['worker_execution_status']}",
                        "Filesystem Replace Worker Executed: True",
                        "Filesystem Replace Worker Result Captured: True",
                        "Filesystem Replace Worker Result Validated: True",
                        "Filesystem Replace Worker Replay Reviewed: True",
                        "Repository Mutated: True",
                    )
                )
            )
            presentations.append(
                render_authorized_grounded_worker_selection(
                    state["consumed_replacement_worker_selection_capture"]
                ).strip()
            )
            presentations.append(
                worker_request.render_worker_invocation_request_summary(
                    state["worker_invocation_request_capture"]
                ).strip()
            )
            presentations.append(
                worker_assignment.render_worker_assignment_summary(
                    state["worker_assignment_capture"]
                ).strip()
            )
            presentations.append(
                worker_dispatch.render_worker_dispatch_summary(
                    state["worker_dispatch_capture"]
                ).strip()
            )
            presentations.append(
                worker_invocation.render_worker_invocation_summary(
                    state["worker_invocation_capture"]
                ).strip()
            )
            presentations.append(
                "\n".join(
                    (
                        "Worker Execution Handoff",
                        f"Execution ID: {state['worker_execution_id']}",
                        f"Execution Status: {state['worker_execution_status']}",
                        "Execution Replay Reference: "
                        f"{state['worker_execution_replay_reference']}",
                        "Execution start evidence has been recorded.",
                        "The certified Filesystem Replace Worker has executed.",
                        "Authorization consumption was not repeated.",
                        "Worker Replay continued from the certified consumption event.",
                        "The authentic Worker output has been captured.",
                        "The captured Worker result has been validated for "
                        "governance policy and lineage.",
                        "The validated execution Replay has completed "
                        "post-execution integrity review.",
                        "Task outcome satisfaction has not been evaluated.",
                        "No Provider has been invoked.",
                        "No command has executed.",
                        "No result acceptance has occurred.",
                        "Final Execution certification has completed through "
                        "the unchanged Certification owner.",
                        "The authenticated repository target has been modified.",
                    )
                )
            )
    else:
        raise FailClosedRuntimeError(f"unsupported G31 pending action: {action_type}")

    return _g31_application_result(
        state,
        interface_name=interface_name,
        pending_action=next_pending,
        presentations=presentations,
    )


def _pending_action(
    action_type: str,
    valid_values: tuple[str, ...],
    context: dict[str, Any],
) -> dict[str, Any]:
    return {
        "action_type": action_type,
        "valid_values": list(valid_values),
        "context": deepcopy(context),
    }


def _g31_application_result(
    state: dict[str, Any],
    *,
    interface_name: str,
    pending_action: dict[str, Any] | None = None,
    presentations: tuple[str, ...] | list[str] = (),
) -> dict[str, Any]:
    result = deepcopy(state)
    result.update(
        {
            "g31_application_transition_version": G31_APPLICATION_TRANSITION_VERSION,
            "g31_application_state_authority": "CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY",
            "g31_application_sequenced_by_common_entry": True,
            "g31_application_interface_transport": interface_name,
            "g31_pending_action": deepcopy(pending_action),
            "g31_canonical_presentations": list(presentations),
        }
    )
    return result


def _owner_bound_pending_clarification(
    project_context: dict[str, Any] | None,
    request: str | None,
) -> dict[str, Any] | None:
    """Project an existing common envelope onto the existing workspace surface."""

    if not isinstance(project_context, dict):
        return None
    conversation = project_context.get("human_conversation_experience")
    envelope = project_context.get("owner_bound_clarification_envelope")
    if not isinstance(conversation, dict) or not isinstance(envelope, dict):
        return None
    if conversation.get("response_mode") != "CLARIFICATION":
        return None
    questions = conversation.get("clarification_questions")
    return {
        "original_message": request,
        "clarification_required": True,
        "clarification_authority": "PLATFORM_CORE",
        "conversation_response_mode": conversation.get("response_mode"),
        "user_headline": conversation.get("user_headline"),
        "user_explanation": conversation.get("user_explanation"),
        "requested_work_type": conversation.get("requested_work_type"),
        "work_type": conversation.get("work_type"),
        "prepared_work_type": conversation.get("prepared_work_type"),
        "work_type_source": conversation.get("work_type_source"),
        "work_type_source_text": conversation.get("work_type_source_text"),
        "mutation_allowed": conversation.get("mutation_allowed"),
        "runtime_implementation": conversation.get("runtime_implementation"),
        "work_type_change_allowed": conversation.get("work_type_change_allowed"),
        "work_type_conflict_detected": conversation.get(
            "work_type_conflict_detected"
        ),
        "work_type_conflict_reason": conversation.get("work_type_conflict_reason"),
        "clarification_questions": (
            [str(question) for question in questions]
            if isinstance(questions, list)
            else []
        ),
        "owner_bound_clarification_envelope": deepcopy(envelope),
        "operational_clarification_envelope": None,
        "artifact_attachment_retry_state": deepcopy(
            conversation.get("artifact_attachment_retry_state")
        )
        if isinstance(conversation.get("artifact_attachment_retry_state"), dict)
        else None,
    }


def _render_g31_execution_progress(state: dict[str, Any]) -> list[str]:
    lines = [render_execution_authorization_summary(state["execution_authorization_capture"])]
    lines.append(
        render_authorized_grounded_worker_selection(
            state["authorized_worker_selection_capture"]
        )
    )
    renderers = (
        ("worker_invocation_request_capture", worker_request.render_worker_invocation_request_summary),
        ("worker_assignment_capture", worker_assignment.render_worker_assignment_summary),
        ("worker_dispatch_capture", worker_dispatch.render_worker_dispatch_summary),
        ("worker_invocation_capture", worker_invocation.render_worker_invocation_summary),
        ("worker_execution_candidate_capture", worker_candidate.render_worker_execution_candidate_summary),
        ("governed_worker_execution_capture", governed_execution.render_governed_worker_execution_summary),
    )
    for field, renderer in renderers:
        if state.get(field):
            lines.append(renderer(state[field]))
    return lines


def _record_g31_execution_decision(
    *,
    pending_execution_review: dict[str, Any],
    decision: str,
    session: str,
    root: Path,
    workspace_path: str,
    created: str,
    runtime_result: dict[str, Any],
    actor: str,
) -> dict[str, Any]:
    review_hash = _require_string(
        pending_execution_review.get("artifact_hash"), "authorization_review_hash"
    )
    decision_result = bind_distinct_human_execution_decision(
        authorization_review_artifact=pending_execution_review,
        human_decision=decision,
        session_id=session,
        decided_by=actor,
        decided_at=created,
        workspace=workspace_path,
        session_root=root / session,
        replay_dir=root / session / f"EXECUTION-DECISION-{review_hash[-16:]}",
    )
    confirmation = decision_result.get("human_confirmation_artifact") or {}
    merged = deepcopy(runtime_result)
    merged.update(
        {
            "execution_human_decision_result": decision_result,
            "execution_human_decision_status": decision_result.get("decision_status"),
            "execution_human_decision_hash": decision_result.get("artifact_hash"),
            "execution_summary_human_confirmation": decision_result.get(
                "execution_summary_human_confirmation"
            )
            is True,
            "execution_decision_rejected": decision_result.get("decision_status")
            == EXECUTION_DECISION_REJECTED,
            "human_confirmation_reference": confirmation.get("confirmation_id"),
            "human_confirmation_hash": decision_result.get("human_confirmation_hash"),
            "runtime_replay_reference": decision_result.get("replay_reference"),
            "execution_authorized": False,
            "worker_selected": False,
            "authorization_dispatch_blocked": True,
        }
    )
    if decision_result.get("decision_status") != EXECUTION_DECISION_APPROVED:
        return merged

    authorization = authorize_confirmed_grounded_execution_decision(
        human_execution_decision_artifact=decision_result,
        workspace=workspace_path,
        session_root=root / session,
        replay_dir=root
        / session
        / f"EXECUTION-AUTHORIZATION-{decision_result['artifact_hash'][-16:]}",
    )
    merged.update(
        {
            "execution_authorization_capture": authorization,
            "execution_authorization_status": authorization.get("authorization_status"),
            "execution_authorized": authorization.get("execution_authorized") is True,
            "authorization_dispatch_blocked": True,
            "runtime_replay_reference": authorization.get(
                "execution_authorization_replay_reference"
            ),
        }
    )
    if authorization.get("execution_authorized") is not True:
        return merged

    selection = select_authorized_grounded_worker(
        execution_authorization_capture=authorization,
        session_root=root / session,
        replay_dir=root
        / session
        / (
            "WORKER-SELECTION-"
            f"{authorization['execution_authorization_artifact']['artifact_hash'][-16:]}"
        ),
    )
    merged.update(
        {
            "authorized_worker_selection_capture": selection,
            "worker_selection_status": selection.get("selection_status"),
            "selected_resource_id": selection.get("selected_resource_id"),
            "selected_role_type": selection.get("selected_role_type"),
            "worker_selected": selection.get("worker_selected") is True,
            "worker_assigned": False,
            "worker_dispatched": False,
            "runtime_replay_reference": selection.get(
                "resource_selection_replay_reference"
            ),
        }
    )
    if selection.get("worker_selected") is not True:
        return merged

    selection_artifact = selection["resource_selection_artifact"]
    invocation_request = worker_request.create_worker_invocation_request(
        invocation_request_id=f"{selection_artifact['selection_id']}:INVOCATION-REQUEST",
        execution_authorization_replay_reference=authorization[
            "execution_authorization_replay_reference"
        ],
        resource_selection_replay_reference=selection[
            "resource_selection_replay_reference"
        ],
        requested_by="PLATFORM_CORE_G31_ASSIGNMENT_BINDING",
        requested_at=created,
        replay_dir=root
        / session
        / f"WORKER-REQUEST-{selection_artifact['artifact_hash'][-16:]}",
    )
    merged.update(
        {
            "worker_invocation_request_capture": invocation_request,
            "worker_invocation_request_status": invocation_request.get("request_status"),
            "worker_invocation_request_created": invocation_request.get("request_status")
            == worker_request.WORKER_INVOCATION_REQUEST_CREATED,
            "runtime_replay_reference": invocation_request.get(
                "worker_invocation_request_replay_reference"
            ),
        }
    )
    if invocation_request.get("request_status") != worker_request.WORKER_INVOCATION_REQUEST_CREATED:
        return merged

    request_artifact = invocation_request["worker_invocation_request_artifact"]
    assignment = worker_assignment.assign_worker_from_invocation_request(
        worker_assignment_id=f"{selection_artifact['selection_id']}:ASSIGNMENT",
        worker_invocation_request_artifact=request_artifact,
        worker_invocation_request_replay_reference=invocation_request[
            "worker_invocation_request_replay_reference"
        ],
        worker_registry_artifacts=worker_assignment.default_worker_registry_for_request(
            request_artifact, created_at=created
        ),
        assigned_by="PLATFORM_CORE_G31_ASSIGNMENT_BINDING",
        assigned_at=created,
        replay_dir=root
        / session
        / f"WORKER-ASSIGNMENT-{request_artifact['artifact_hash'][-16:]}",
    )
    merged.update(
        {
            "worker_assignment_capture": assignment,
            "worker_assignment_status": assignment.get("assignment_status"),
            "worker_assigned": assignment.get("assignment_status")
            == worker_assignment.WORKER_ASSIGNED,
            "worker_dispatched": False,
            "provider_invoked": False,
            "worker_invoked": False,
            "command_executed": False,
            "repository_mutated": False,
            "runtime_replay_reference": assignment.get(
                "worker_assignment_replay_reference"
            ),
        }
    )
    if assignment.get("assignment_status") != worker_assignment.WORKER_ASSIGNED:
        return merged

    assignment_artifact = assignment["worker_assignment_artifact"]
    dispatch = worker_dispatch.dispatch_assigned_worker(
        worker_dispatch_id=f"{assignment_artifact['worker_assignment_id']}:DISPATCH",
        worker_assignment_artifact=assignment_artifact,
        worker_assignment_replay_reference=assignment[
            "worker_assignment_replay_reference"
        ],
        dispatched_by="AIGOL_GOVERNANCE",
        dispatched_at=created,
        replay_dir=root
        / session
        / f"WORKER-DISPATCH-{assignment_artifact['artifact_hash'][-16:]}",
    )
    merged.update(
        {
            "worker_dispatch_capture": dispatch,
            "worker_dispatch_status": dispatch.get("dispatch_status"),
            "worker_dispatched": dispatch.get("dispatch_status")
            == worker_dispatch.WORKER_DISPATCHED,
            "authorization_dispatch_blocked": dispatch.get("dispatch_status")
            != worker_dispatch.WORKER_DISPATCHED,
            "provider_invoked": False,
            "worker_invoked": False,
            "command_executed": False,
            "repository_mutated": False,
            "runtime_replay_reference": dispatch.get(
                "worker_dispatch_replay_reference"
            ),
        }
    )
    if dispatch.get("dispatch_status") != worker_dispatch.WORKER_DISPATCHED:
        return merged

    dispatch_artifact = dispatch["worker_dispatch_artifact"]
    invocation = worker_invocation.invoke_dispatched_worker(
        worker_invocation_id=f"{dispatch_artifact['worker_dispatch_id']}:INVOCATION",
        worker_dispatch_artifact=dispatch_artifact,
        worker_dispatch_replay_reference=dispatch["worker_dispatch_replay_reference"],
        invoked_by="AIGOL_GOVERNANCE",
        invoked_at=created,
        replay_dir=root
        / session
        / f"WORKER-INVOCATION-{dispatch_artifact['artifact_hash'][-16:]}",
    )
    merged.update(
        {
            "worker_invocation_capture": invocation,
            "worker_invocation_status": invocation.get("invocation_status"),
            "worker_invoked": invocation.get("invocation_status")
            == worker_invocation.WORKER_INVOKED,
            "provider_invoked": False,
            "execution_started": False,
            "command_executed": False,
            "result_created": False,
            "repository_mutated": False,
            "runtime_replay_reference": invocation.get(
                "worker_invocation_replay_reference"
            ),
        }
    )
    if invocation.get("invocation_status") != worker_invocation.WORKER_INVOKED:
        return merged

    invocation_artifact = invocation["worker_invocation_artifact"]
    candidate = worker_candidate.project_g31_invocation_to_execution_candidate(
        worker_invocation_artifact=invocation_artifact,
        worker_invocation_replay_reference=invocation[
            "worker_invocation_replay_reference"
        ],
        session_root=root / session,
        requested_by="PLATFORM_CORE_G31_CANDIDATE_BINDING",
        created_at=created,
        replay_dir=root
        / session
        / f"WORKER-EXECUTION-CANDIDATE-{invocation_artifact['artifact_hash'][-16:]}",
    )
    merged.update(
        {
            "worker_execution_candidate_capture": candidate,
            "execution_candidate_created": candidate.get(
                "worker_execution_candidate_generated"
            )
            is True,
            "provider_invoked": False,
            "worker_process_started": False,
            "execution_started": False,
            "command_executed": False,
            "result_created": False,
            "repository_mutated": False,
            "runtime_replay_reference": candidate.get(
                "worker_execution_candidate_replay_reference"
            ),
        }
    )
    if candidate.get("worker_execution_candidate_generated") is not True:
        return merged

    execution = governed_execution.project_g31_candidate_to_governed_execution(
        execution_candidate_capture=candidate,
        session_root=root / session,
        executed_by="PLATFORM_CORE_G31_GOVERNED_EXECUTION_BINDING",
        executed_at=created,
        replay_dir=root
        / session
        / (
            "GOVERNED-WORKER-EXECUTION-"
            f"{candidate['worker_execution_candidate_artifact']['artifact_hash'][-16:]}"
        ),
    )
    merged.update(
        {
            "governed_worker_execution_capture": execution,
            "governed_execution_evidence_created": execution.get(
                "worker_execution_completed"
            )
            is True,
            "provider_invoked": False,
            "worker_process_started": False,
            "execution_started": False,
            "command_executed": False,
            "worker_output_created": False,
            "result_created": False,
            "repository_mutated": False,
            "runtime_replay_reference": execution.get(
                "worker_execution_replay_reference"
            ),
        }
    )
    return merged


def _record_g31_worker_activation_decision(
    *,
    pending_activation_review: dict[str, Any],
    session: str,
    root: Path,
    workspace_path: str,
    created: str,
    runtime_result: dict[str, Any],
    runner: Callable[..., Any] | None,
    actor: str,
) -> dict[str, Any]:
    merged = deepcopy(runtime_result)
    review = pending_activation_review["activation_review_artifact"]
    capture = worker_activation.activate_bounded_codex_worker(
        activation_review_artifact=review,
        governed_execution_capture=merged["governed_worker_execution_capture"],
        execution_candidate_capture=merged["worker_execution_candidate_capture"],
        human_decision="APPROVE",
        decided_by=actor,
        decided_at=created,
        session_root=root / session,
        workspace=workspace_path,
        replay_dir=root
        / session
        / f"CODEX-WORKER-ACTIVATION-{review['artifact_hash'][-16:]}",
        runner=runner,
    )
    merged.update(
        {
            "codex_worker_activation_capture": capture,
            "runtime_replay_reference": capture["activation_replay_reference"],
            **{
                field: capture[field]
                for field in worker_activation.ACTIVATION_TRUTH_FIELDS
            },
        }
    )
    result = codex_result.capture_successful_codex_worker_result(
        activation_capture=capture,
        governed_execution_capture=merged["governed_worker_execution_capture"],
        execution_candidate_capture=merged["worker_execution_candidate_capture"],
        session_root=root / session,
        workspace=workspace_path,
        captured_at=created,
        replay_dir=root
        / session
        / (
            "CODEX-WORKER-RESULT-CAPTURE-"
            f"{capture['codex_transport_receipt']['receipt_id'][-16:]}"
        ),
    )
    merged["codex_worker_result_capture_binding_capture"] = result
    merged.update({field: result[field] for field in codex_result.RESULT_TRUTH_FIELDS})
    validation = codex_validation.validate_captured_codex_worker_result(
        result_capture_binding_capture=result,
        activation_capture=capture,
        governed_execution_capture=merged["governed_worker_execution_capture"],
        execution_candidate_capture=merged["worker_execution_candidate_capture"],
        session_root=root / session,
        workspace=workspace_path,
        validated_at=created,
        replay_dir=root
        / session
        / f"CODEX-WORKER-RESULT-VALIDATION-{result.get('worker_output_hash', '')[-16:]}",
    )
    merged["codex_worker_semantic_validation_binding_capture"] = validation
    merged.update(
        {field: validation[field] for field in codex_validation.VALIDATION_TRUTH_FIELDS}
    )
    return merged


def _prepare_g31_task_outcome_review(
    *,
    session: str,
    root: Path,
    workspace_path: str,
    created: str,
    runtime_result: dict[str, Any],
) -> dict[str, Any]:
    merged = deepcopy(runtime_result)
    validation = merged["codex_worker_semantic_validation_binding_capture"]
    validation_artifact = validation.get("worker_result_validation_artifact") or {}
    review = codex_task_review.prepare_codex_task_outcome_review(
        result_capture_binding_capture=merged[
            "codex_worker_result_capture_binding_capture"
        ],
        validation_binding_capture=validation,
        activation_capture=merged["codex_worker_activation_capture"],
        governed_execution_capture=merged["governed_worker_execution_capture"],
        execution_candidate_capture=merged["worker_execution_candidate_capture"],
        session_root=root / session,
        workspace=workspace_path,
        prepared_at=created,
        replay_dir=root
        / session
        / (
            "CODEX-TASK-OUTCOME-REVIEW-"
            f"{validation_artifact.get('artifact_hash', '')[-16:]}"
        ),
    )
    reconstruction = codex_task_review.reconstruct_codex_task_outcome_review(
        review_capture=review,
        result_capture_binding_capture=merged[
            "codex_worker_result_capture_binding_capture"
        ],
        validation_binding_capture=validation,
        activation_capture=merged["codex_worker_activation_capture"],
        governed_execution_capture=merged["governed_worker_execution_capture"],
        execution_candidate_capture=merged["worker_execution_candidate_capture"],
        session_root=root / session,
        workspace=workspace_path,
    )
    merged.update(
        {
            "codex_task_outcome_review_capture": review,
            "codex_task_outcome_review_reconstruction": reconstruction,
            "task_outcome_review_status": review["review_status"],
            "task_outcome_review_replay_created": True,
            "task_outcome_review_count": 1,
            "human_task_outcome_decision_recorded": False,
        }
    )
    return merged


def _record_g31_task_outcome_decision(
    *,
    pending_task_outcome_review: dict[str, Any],
    task_outcome_decision: str,
    session: str,
    root: Path,
    workspace_path: str,
    created: str,
    runtime_result: dict[str, Any],
    actor: str,
) -> dict[str, Any]:
    merged = deepcopy(runtime_result)
    review_packet = pending_task_outcome_review["task_outcome_review_packet_artifact"]
    decision = codex_task_review.record_codex_task_outcome_human_decision(
        review_capture=pending_task_outcome_review,
        task_outcome_decision=task_outcome_decision,
        decision_reason=(
            "Human operator selected the explicit task-outcome decision after "
            "canonical presentation of the exact captured Worker output and lineage."
        ),
        decided_by=actor,
        decided_at=created,
        result_capture_binding_capture=merged[
            "codex_worker_result_capture_binding_capture"
        ],
        validation_binding_capture=merged[
            "codex_worker_semantic_validation_binding_capture"
        ],
        activation_capture=merged["codex_worker_activation_capture"],
        governed_execution_capture=merged["governed_worker_execution_capture"],
        execution_candidate_capture=merged["worker_execution_candidate_capture"],
        session_root=root / session,
        workspace=workspace_path,
        human_decision_replay_dir=root
        / session
        / (
            "CODEX-TASK-OUTCOME-HUMAN-DECISION-"
            f"{review_packet['artifact_hash'][-16:]}"
        ),
    )
    reconstruction = codex_task_review.reconstruct_codex_task_outcome_human_decision(
        decision_capture=decision,
        review_capture=pending_task_outcome_review,
        result_capture_binding_capture=merged[
            "codex_worker_result_capture_binding_capture"
        ],
        validation_binding_capture=merged[
            "codex_worker_semantic_validation_binding_capture"
        ],
        activation_capture=merged["codex_worker_activation_capture"],
        governed_execution_capture=merged["governed_worker_execution_capture"],
        execution_candidate_capture=merged["worker_execution_candidate_capture"],
        session_root=root / session,
        workspace=workspace_path,
    )
    merged.update(
        {
            "codex_task_outcome_human_decision_capture": decision,
            "codex_task_outcome_human_decision_reconstruction": reconstruction,
            "task_outcome_review_status": task_outcome_decision,
            "task_outcome_review_replay_created": True,
            "task_outcome_review_count": 1,
            "human_task_outcome_decision_recorded": True,
            **{
                field: decision[field]
                for field in (
                    "task_outcome_satisfaction_evaluated",
                    "task_outcome_satisfied",
                    "rework_requested",
                    "result_accepted",
                    "repository_mutation_authorized",
                    "repository_mutated",
                    "automatic_retry_performed",
                    "additional_worker_process_started",
                    "commit_created",
                    "deployed",
                    "released",
                )
            },
        }
    )
    return merged


def _g31_disposable_lineage(
    state: dict[str, Any], *, session_root: Path, workspace_path: str
) -> dict[str, Any]:
    return {
        "task_outcome_decision_capture": state[
            "codex_task_outcome_human_decision_capture"
        ],
        "review_capture": state["codex_task_outcome_review_capture"],
        "result_capture_binding_capture": state[
            "codex_worker_result_capture_binding_capture"
        ],
        "validation_binding_capture": state[
            "codex_worker_semantic_validation_binding_capture"
        ],
        "activation_capture": state["codex_worker_activation_capture"],
        "governed_execution_capture": state["governed_worker_execution_capture"],
        "execution_candidate_capture": state["worker_execution_candidate_capture"],
        "session_root": session_root,
        "source_workspace": workspace_path,
    }


def _prepare_g31_disposable_patch_validation_review(
    *,
    session: str,
    root: Path,
    workspace_path: str,
    created: str,
    runtime_result: dict[str, Any],
) -> dict[str, Any]:
    merged = deepcopy(runtime_result)
    decision = merged["codex_task_outcome_human_decision_capture"]
    identity = decision["human_decision_capture"]["human_decision_artifact"][
        "artifact_hash"
    ][-16:]
    lineage = _g31_disposable_lineage(
        merged, session_root=root / session, workspace_path=workspace_path
    )
    review = disposable_validation.prepare_disposable_patch_validation_review(
        disposable_workspace=root / session / f"DISPOSABLE-PATCH-VALIDATION-{identity}",
        prepared_at=created,
        replay_dir=root
        / session
        / f"DISPOSABLE-PATCH-VALIDATION-REVIEW-{identity}",
        **lineage,
    )
    reconstruction = disposable_validation.reconstruct_disposable_patch_validation_review(
        review_binding_capture=review, **lineage
    )
    merged.update(
        {
            "disposable_patch_validation_review_capture": review,
            "disposable_patch_validation_review_reconstruction": reconstruction,
            "disposable_patch_validation_review_pending": True,
            "disposable_patch_validation_decision_recorded": False,
            "disposable_patch_validation_executed": False,
            "ready_for_acceptance": False,
            "result_accepted": False,
            "mutation_authorized": False,
            "main_repository_mutated": False,
        }
    )
    return merged


def _record_g31_disposable_patch_validation_decision(
    *,
    pending_review: dict[str, Any],
    decision: str,
    session: str,
    root: Path,
    workspace_path: str,
    created: str,
    runtime_result: dict[str, Any],
    actor: str,
) -> dict[str, Any]:
    merged = deepcopy(runtime_result)
    plan = pending_review["disposable_patch_validation_plan_artifact"]
    lineage = _g31_disposable_lineage(
        merged, session_root=root / session, workspace_path=workspace_path
    )
    capture = disposable_validation.record_disposable_patch_validation_human_decision(
        review_binding_capture=pending_review,
        decision=decision,
        decision_reason=(
            "Human operator selected the explicit disposable validation decision "
            "through the canonical Human Interface application entry."
        ),
        decided_by=actor,
        decided_at=created,
        human_decision_replay_dir=root
        / session
        / (
            "DISPOSABLE-PATCH-VALIDATION-HUMAN-DECISION-"
            f"{plan['artifact_hash'][-16:]}"
        ),
        **lineage,
    )
    merged.update(
        {
            "disposable_patch_validation_human_decision_capture": capture,
            "disposable_patch_validation_human_decision_reconstruction": (
                human_decision.reconstruct_human_decision_replay(
                    capture["human_decision_replay_reference"]
                )
            ),
            "disposable_patch_validation_review_pending": False,
            "disposable_patch_validation_decision_recorded": True,
            "disposable_patch_validation_executed": False,
            "ready_for_acceptance": False,
            "result_accepted": False,
            "mutation_authorized": False,
            "main_repository_mutated": False,
        }
    )
    return merged


def _execute_g31_disposable_patch_validation(
    *,
    session: str,
    root: Path,
    workspace_path: str,
    created: str,
    runtime_result: dict[str, Any],
    actor: str,
) -> dict[str, Any]:
    merged = deepcopy(runtime_result)
    review = merged["disposable_patch_validation_review_capture"]
    plan = review["disposable_patch_validation_plan_artifact"]
    lineage = _g31_disposable_lineage(
        merged, session_root=root / session, workspace_path=workspace_path
    )
    from aigol.runtime.constitutional_reuse_proof_production_gate import (
        validate_reuse_proof_g47_scope_binding,
    )

    reuse_scope_binding = validate_reuse_proof_g47_scope_binding(
        merged.get("reuse_proof_g47_scope_binding")
        or review.get("reuse_proof_g47_scope_binding")
    )
    outcome = disposable_validation.execute_disposable_patch_validation(
        review_binding_capture=review,
        application_decision_capture=merged[
            "disposable_patch_validation_human_decision_capture"
        ],
        executed_by=actor,
        executed_at=created,
        replay_dir=root
        / session
        / f"DISPOSABLE-PATCH-VALIDATION-OUTCOME-{plan['artifact_hash'][-16:]}",
        reuse_proof_g47_scope_binding=reuse_scope_binding,
        **lineage,
    )
    reconstruction = disposable_validation.reconstruct_disposable_patch_validation_outcome(
        outcome_capture=outcome,
        review_binding_capture=review,
        application_decision_capture=merged[
            "disposable_patch_validation_human_decision_capture"
        ],
        **lineage,
    )
    artifact = outcome["outcome_artifact"]
    merged.update(
        {
            "disposable_patch_validation_outcome_capture": outcome,
            "disposable_patch_validation_outcome_reconstruction": reconstruction,
            "disposable_patch_validation_approved": True,
            "disposable_patch_validation_executed": artifact[
                "disposable_patch_application_attempted"
            ],
            "disposable_patch_application_succeeded": artifact[
                "disposable_patch_applied"
            ]
            and artifact["content_validation_passed"],
            "focused_validation_executed": artifact[
                "grounded_test_execution_performed"
            ],
            "focused_validation_succeeded": artifact[
                "grounded_test_validation_passed"
            ],
            "ready_for_acceptance": False,
            "result_accepted": False,
            "mutation_authorized": False,
            "main_repository_mutated": False,
        }
    )
    merged.update(
        {
            key: outcome[key]
            for key in (
                "disposable_patch_applied",
                "content_validation_performed",
                "content_validation_passed",
                "grounded_test_execution_performed",
                "grounded_test_validation_passed",
                "ready_for_generated_content_acceptance",
                "repository_mutation_authorized",
                "failure_reason",
            )
        }
    )
    return merged


def _bind_g31_replacement_acceptance_prerequisites(
    *,
    session: str,
    root: Path,
    workspace_path: str,
    created: str,
    runtime_result: dict[str, Any],
) -> dict[str, Any]:
    merged = deepcopy(runtime_result)
    outcome = merged["disposable_patch_validation_outcome_capture"]
    outcome_hash = outcome["outcome_artifact"]["artifact_hash"]
    capture = replacement_prerequisites.bind_codex_replacement_acceptance_prerequisites(
        disposable_validation_outcome_capture=outcome,
        disposable_validation_review_capture=merged[
            "disposable_patch_validation_review_capture"
        ],
        application_decision_capture=merged[
            "disposable_patch_validation_human_decision_capture"
        ],
        task_outcome_decision_capture=merged[
            "codex_task_outcome_human_decision_capture"
        ],
        task_outcome_review_capture=merged["codex_task_outcome_review_capture"],
        result_capture_binding_capture=merged[
            "codex_worker_result_capture_binding_capture"
        ],
        governance_validation_binding_capture=merged[
            "codex_worker_semantic_validation_binding_capture"
        ],
        activation_capture=merged["codex_worker_activation_capture"],
        governed_execution_capture=merged["governed_worker_execution_capture"],
        execution_candidate_capture=merged["worker_execution_candidate_capture"],
        session_root=root / session,
        source_workspace=workspace_path,
        created_at=created,
        replay_dir=root
        / session
        / f"G31-REPLACEMENT-ACCEPTANCE-PREREQUISITES-{outcome_hash[-16:]}",
    )
    reconstruction = replacement_prerequisites.reconstruct_codex_replacement_acceptance_prerequisite_binding(
        binding_capture=capture, session_root=root / session
    )
    merged["codex_replacement_acceptance_prerequisite_binding_capture"] = capture
    merged[
        "codex_replacement_acceptance_prerequisite_binding_reconstruction"
    ] = reconstruction
    merged.update(
        {
            key: capture[key]
            for key in (
                "replacement_manifest_created",
                "acceptance_prerequisites_satisfied",
                "ready_for_acceptance",
                "result_accepted",
                "mutation_authorized",
                "main_repository_mutated",
            )
        }
    )
    return merged


def _record_g31_content_decision(
    *,
    context_capture: dict[str, Any],
    outcome: str,
    session: str,
    root: Path,
    workspace_path: str,
    created: str,
    runtime_result: dict[str, Any],
    actor: str,
) -> tuple[dict[str, Any], dict[str, Any] | None, list[str]]:
    merged = deepcopy(runtime_result)
    binding = merged["codex_replacement_acceptance_prerequisite_binding_capture"]
    capture = human_decision.record_content_acceptance_decision(
        context_capture=context_capture,
        binding_capture=binding,
        decision_outcome=outcome,
        decided_by=actor,
        decided_at=created,
        session_root=root / session,
    )
    reconstruction = human_decision.reconstruct_content_acceptance_decision_replay(
        decision_capture=capture,
        binding_capture=binding,
        session_root=root / session,
    )
    merged.update(
        {
            "human_content_acceptance_decision_capture": capture,
            "human_content_acceptance_decision_reconstruction": reconstruction,
            "result_accepted": False,
            "mutation_authorized": False,
            "main_repository_mutated": False,
        }
    )
    presentations = [human_decision.render_content_acceptance_decision(capture)]
    if outcome != human_decision.ACCEPTED:
        return merged, None, presentations

    artifact = capture["human_decision_artifact"]
    suffix = artifact["artifact_hash"][-16:]
    accepted = generated_acceptance.accept_generated_content_from_content_acceptance_decision(
        acceptance_id=f"G31-GENERATED-CONTENT-ACCEPTANCE-{suffix}",
        decision_capture=capture,
        binding_capture=binding,
        created_at=created,
        session_root=root / session,
        replay_dir=root / session / f"GENERATED-CONTENT-ACCEPTANCE-{suffix}",
    )
    accepted_reconstruction = generated_acceptance.reconstruct_generated_content_acceptance_from_decision_replay(
        acceptance_capture=accepted,
        decision_capture=capture,
        binding_capture=binding,
        session_root=root / session,
    )
    activation_binding = worker_activation.reconstruct_codex_worker_activation_binding(
        activation_capture=merged["codex_worker_activation_capture"],
        governed_execution_capture=merged["governed_worker_execution_capture"],
        execution_candidate_capture=merged["worker_execution_candidate_capture"],
        session_root=root / session,
        workspace=workspace_path,
    )
    grounding = activation_binding["lineage"]["grounding"]
    candidate = existing_file_candidate.create_g31_accepted_existing_file_mutation_candidate(
        candidate_id=f"G31-EXISTING-FILE-CANDIDATE-{suffix}",
        acceptance_capture=accepted,
        decision_capture=capture,
        binding_capture=binding,
        repository_grounding_artifact=grounding,
        session_root=root / session,
        created_by=actor,
        created_at=created,
        replay_dir=root / session / f"EXISTING-FILE-CANDIDATE-{suffix}",
    )
    candidate_reconstruction = existing_file_candidate.reconstruct_g31_accepted_existing_file_mutation_candidate_replay(
        candidate_capture=candidate,
        acceptance_capture=accepted,
        decision_capture=capture,
        binding_capture=binding,
        repository_grounding_artifact=grounding,
        session_root=root / session,
    )
    candidate_hash = candidate["existing_file_mutation_candidate_artifact"]["artifact_hash"]
    mutation_context = human_decision.prepare_existing_file_mutation_decision_context(
        context_id=f"G31-MUTATION-DECISION-{candidate_hash[-16:]}",
        candidate_capture=candidate,
        acceptance_capture=accepted,
        content_decision_capture=capture,
        binding_capture=binding,
        repository_grounding_artifact=grounding,
        human_actor_id=actor,
        presented_at=created,
        session_root=root / session,
        replay_dir=root / session / f"G31-MUTATION-DECISION-{candidate_hash[-16:]}",
    )
    merged.update(
        {
            "generated_content_acceptance_capture": accepted,
            "generated_content_acceptance_reconstruction": accepted_reconstruction,
            "existing_file_mutation_candidate_capture": candidate,
            "existing_file_mutation_candidate_reconstruction": candidate_reconstruction,
            "existing_file_mutation_candidate_created": True,
            "human_mutation_decision_context_capture": mutation_context,
            "codex_worker_activation_binding_reconstruction": activation_binding,
            "repository_grounding_artifact": deepcopy(grounding),
            "human_mutation_decision_actor": actor,
            "human_mutation_decision_recorded": False,
            "result_accepted": True,
            "mutation_authorized": False,
            "authorization_actor_bound": False,
            "authorization_replay_recorded": False,
            "authorization_consumed": False,
            "replace_request_created": False,
            "worker_invoked": False,
            "provider_invoked": False,
            "command_executed": False,
            "repository_mutated": False,
            "main_repository_mutated": False,
        }
    )
    presentations.extend(
        (
            generated_acceptance.render_generated_content_acceptance_from_decision(
                accepted, binding
            ),
            existing_file_candidate.render_g31_accepted_existing_file_mutation_candidate(
                candidate
            ),
            human_decision.render_existing_file_mutation_decision_context(mutation_context),
            "Enter exact APPROVED or REJECTED.",
        )
    )
    return (
        merged,
        _pending_action(
            G31_MUTATION_DECISION,
            (human_decision.MUTATION_APPROVED, human_decision.REJECTED),
            mutation_context,
        ),
        presentations,
    )


def _record_g31_mutation_decision(
    *,
    context_capture: dict[str, Any],
    outcome: str,
    session: str,
    root: Path,
    workspace_path: str,
    created: str,
    runtime_result: dict[str, Any],
    actor: str,
) -> dict[str, Any]:
    merged = deepcopy(runtime_result)
    grounding = merged.get("repository_grounding_artifact")
    if not isinstance(grounding, dict):
        raise FailClosedRuntimeError("canonical repository grounding is required")
    capture = human_decision.record_existing_file_mutation_decision(
        context_capture=context_capture,
        candidate_capture=merged["existing_file_mutation_candidate_capture"],
        acceptance_capture=merged["generated_content_acceptance_capture"],
        content_decision_capture=merged["human_content_acceptance_decision_capture"],
        binding_capture=merged["codex_replacement_acceptance_prerequisite_binding_capture"],
        repository_grounding_artifact=grounding,
        decision_outcome=outcome,
        decided_by=actor,
        decided_at=created,
        session_root=root / session,
    )
    reconstruction = human_decision.reconstruct_existing_file_mutation_decision_replay(
        decision_capture=capture,
        candidate_capture=merged["existing_file_mutation_candidate_capture"],
        acceptance_capture=merged["generated_content_acceptance_capture"],
        content_decision_capture=merged["human_content_acceptance_decision_capture"],
        binding_capture=merged["codex_replacement_acceptance_prerequisite_binding_capture"],
        repository_grounding_artifact=grounding,
        session_root=root / session,
    )
    merged.update(
        {
            "human_mutation_decision_context_capture": context_capture,
            "human_mutation_decision_capture": capture,
            "human_mutation_decision_reconstruction": reconstruction,
            "repository_grounding_artifact": deepcopy(grounding),
            "human_mutation_decision_actor": actor,
            "human_mutation_decision_recorded": True,
            "mutation_decision_recorded": True,
            "mutation_decision_approved": outcome == human_decision.MUTATION_APPROVED,
            "mutation_authorized": False,
            "authorization_actor_bound": False,
            "authorization_replay_recorded": False,
            "authorization_consumed": False,
            "replace_request_created": False,
            "worker_invoked": False,
            "provider_invoked": False,
            "command_executed": False,
            "repository_mutated": False,
            "main_repository_mutated": False,
        }
    )
    return merged


def _authorize_g31_mutation_decision(
    *,
    session: str,
    root: Path,
    workspace_path: str,
    created: str,
    runtime_result: dict[str, Any],
) -> dict[str, Any]:
    """Sequence exact reconstructed APPROVED V3 evidence through existing owners."""

    merged = deepcopy(runtime_result)
    decision = merged.get("human_mutation_decision_capture") or {}
    artifact = decision.get("human_mutation_decision_artifact") or {}
    session_root = root / session
    evidence = {
        "candidate_capture": merged["existing_file_mutation_candidate_capture"],
        "candidate_reconstruction": merged[
            "existing_file_mutation_candidate_reconstruction"
        ],
        "mutation_decision_capture": decision,
        "mutation_decision_reconstruction": merged[
            "human_mutation_decision_reconstruction"
        ],
        "acceptance_capture": merged["generated_content_acceptance_capture"],
        "content_decision_capture": merged[
            "human_content_acceptance_decision_capture"
        ],
        "binding_capture": merged[
            "codex_replacement_acceptance_prerequisite_binding_capture"
        ],
        "repository_grounding_artifact": merged["repository_grounding_artifact"],
        "activation_capture": merged["codex_worker_activation_capture"],
        "activation_binding": merged[
            "codex_worker_activation_binding_reconstruction"
        ],
        "governed_execution_capture": merged["governed_worker_execution_capture"],
        "execution_candidate_capture": merged["worker_execution_candidate_capture"],
        "session_root": session_root,
        "workspace": workspace_path,
    }
    authorization = existing_file_governance.authorize_g31_approved_existing_file_mutation(
        authorization_id=(
            "G31-MUTATION-AUTHORIZATION-" + artifact["artifact_hash"][-16:]
        ),
        authorization_timestamp=created,
        **evidence,
    )
    authorization_reconstruction = (
        existing_file_governance.reconstruct_g31_existing_file_mutation_authorization_binding(
            authorization_capture=authorization,
            **evidence,
        )
    )
    actor_replay = existing_file_governance.bind_g31_mutation_authorization_actor_and_replay(
        authorization_capture=authorization,
        **evidence,
    )
    actor_replay_reconstruction = (
        existing_file_governance.reconstruct_g31_mutation_authorization_actor_and_replay(
            actor_replay_capture=actor_replay,
            authorization_capture=authorization,
            **evidence,
        )
    )
    request = existing_file_governance.create_g31_authenticated_replace_request(
        actor_replay_capture=actor_replay,
        authorization_capture=authorization,
        **evidence,
    )
    request_reconstruction = (
        filesystem_replace_worker.record_authenticated_replace_request_v2(request)
    )
    consumption_reconstruction = (
        filesystem_replace_worker.consume_authenticated_replace_authorization_v2(
            request
        )
    )
    selection = existing_file_governance.bind_consumed_g31_authenticated_replace_worker_selection(
        authenticated_request=request,
        authorization_reconstruction=actor_replay_reconstruction,
        consumption_reconstruction=consumption_reconstruction,
        replay_dir=session_root
        / f"FILESYSTEM-REPLACE-WORKER-SELECTION-{request['request_hash'][-16:]}",
    )
    selection_artifact = selection["resource_selection_artifact"]
    invocation_request_replay_dir = (
        session_root
        / f"WORKER-REQUEST-{selection_artifact['artifact_hash'][-16:]}"
    )

    def resolve_filesystem_worker_selection_lineage() -> dict[str, Any]:
        return (
            filesystem_selection_lineage
            .resolve_authenticated_replacement_worker_selection_lineage(
                authenticated_request=request,
                consumption_reconstruction=consumption_reconstruction,
                resource_selection_capture=selection,
                worker_selection_certification_reference=str(
                    existing_file_governance.R08B_CERTIFICATION_PATH
                ),
                anchor=invocation_request_replay_dir,
            )
        )

    invocation_request = (
        worker_request.create_worker_invocation_request_from_selection_lineage(
            invocation_request_id=(
                f"{selection_artifact['selection_id']}:INVOCATION-REQUEST"
            ),
            worker_selection_lineage_resolver=(
                resolve_filesystem_worker_selection_lineage
            ),
            requested_by="PLATFORM_CORE_G31_INVOCATION_REQUEST_COMPATIBILITY",
            requested_at=created,
            replay_dir=invocation_request_replay_dir,
        )
    )
    invocation_request_artifact = invocation_request[
        "worker_invocation_request_artifact"
    ]
    assignment = worker_assignment.assign_worker_from_invocation_request(
        worker_assignment_id=f"{selection_artifact['selection_id']}:ASSIGNMENT",
        worker_invocation_request_artifact=invocation_request_artifact,
        worker_invocation_request_replay_reference=invocation_request[
            "worker_invocation_request_replay_reference"
        ],
        worker_registry_artifacts=worker_assignment.default_worker_registry_for_request(
            invocation_request_artifact,
            created_at=created,
        ),
        assigned_by="PLATFORM_CORE_G31_ASSIGNMENT_BINDING",
        assigned_at=created,
        replay_dir=session_root
        / f"WORKER-ASSIGNMENT-{invocation_request_artifact['artifact_hash'][-16:]}",
    )
    if assignment.get("assignment_status") != worker_assignment.WORKER_ASSIGNED:
        raise FailClosedRuntimeError(
            "G31 mutation continuation failed closed: Worker assignment failed"
        )
    assignment_reconstruction = (
        worker_assignment.reconstruct_worker_assignment_runtime_replay(
            assignment["worker_assignment_replay_reference"]
        )
    )
    if not all(
        (
            assignment_reconstruction.get("assignment_status")
            == worker_assignment.WORKER_ASSIGNED,
            assignment_reconstruction.get("worker_assignment_id")
            == assignment.get("worker_assignment_reference"),
            assignment_reconstruction.get("worker_id")
            == selection.get("selected_resource_id"),
            assignment_reconstruction.get("canonical_chain_id")
            == invocation_request_artifact.get("chain_id"),
            assignment_reconstruction.get("worker_invocation_request_reference")
            == invocation_request_artifact.get("worker_invocation_request_id"),
            assignment_reconstruction.get("worker_assigned") is True,
            assignment_reconstruction.get("worker_dispatched") is False,
            assignment_reconstruction.get("worker_invoked") is False,
            assignment_reconstruction.get("execution_started") is False,
            assignment_reconstruction.get("governance_mutated") is False,
            assignment_reconstruction.get("replay_mutated") is False,
        )
    ):
        raise FailClosedRuntimeError(
            "G31 mutation continuation failed closed: Worker assignment Replay mismatch"
        )
    assignment_artifact = assignment["worker_assignment_artifact"]
    dispatch = worker_dispatch.dispatch_assigned_worker(
        worker_dispatch_id=f"{assignment_artifact['worker_assignment_id']}:DISPATCH",
        worker_assignment_artifact=assignment_artifact,
        worker_assignment_replay_reference=assignment[
            "worker_assignment_replay_reference"
        ],
        dispatched_by="PLATFORM_CORE_G31_DISPATCH_BINDING",
        dispatched_at=created,
        replay_dir=session_root
        / f"WORKER-DISPATCH-{assignment_artifact['artifact_hash'][-16:]}",
    )
    if dispatch.get("dispatch_status") != worker_dispatch.WORKER_DISPATCHED:
        raise FailClosedRuntimeError(
            "G31 mutation continuation failed closed: Worker dispatch failed"
        )
    dispatch_reconstruction = worker_dispatch.reconstruct_worker_dispatch_replay(
        dispatch["worker_dispatch_replay_reference"]
    )
    dispatch_artifact = dispatch["worker_dispatch_artifact"]
    if not all(
        (
            dispatch_reconstruction.get("dispatch_status")
            == worker_dispatch.WORKER_DISPATCHED,
            dispatch_reconstruction.get("worker_dispatch_id")
            == dispatch.get("worker_dispatch_reference"),
            dispatch_reconstruction.get("worker_assignment_reference")
            == assignment_artifact.get("worker_assignment_id"),
            dispatch_artifact.get("worker_assignment_hash")
            == assignment_artifact.get("artifact_hash"),
            dispatch_reconstruction.get("worker_id")
            == selection.get("selected_resource_id"),
            dispatch_reconstruction.get("chain_id")
            == invocation_request_artifact.get("chain_id"),
            dispatch_reconstruction.get("worker_invocation_request_reference")
            == invocation_request_artifact.get("worker_invocation_request_id"),
            dispatch_reconstruction.get("worker_assigned") is True,
            dispatch_reconstruction.get("worker_dispatched") is True,
            dispatch_reconstruction.get("dispatch_requested") is True,
            dispatch_reconstruction.get("worker_invoked") is False,
            dispatch_reconstruction.get("execution_started") is False,
            dispatch_reconstruction.get("result_created") is False,
            dispatch_reconstruction.get("governance_mutated") is False,
            dispatch_reconstruction.get("replay_mutated") is False,
        )
    ):
        raise FailClosedRuntimeError(
            "G31 mutation continuation failed closed: Worker dispatch Replay mismatch"
        )
    invocation = worker_invocation.invoke_dispatched_worker(
        worker_invocation_id=(
            f"{dispatch_artifact['worker_dispatch_id']}:INVOCATION"
        ),
        worker_dispatch_artifact=dispatch_artifact,
        worker_dispatch_replay_reference=dispatch[
            "worker_dispatch_replay_reference"
        ],
        invoked_by="PLATFORM_CORE_G31_INVOCATION_BINDING",
        invoked_at=created,
        replay_dir=session_root
        / f"WORKER-INVOCATION-{dispatch_artifact['artifact_hash'][-16:]}",
    )
    if invocation.get("invocation_status") != worker_invocation.WORKER_INVOKED:
        raise FailClosedRuntimeError(
            "G31 mutation continuation failed closed: Worker invocation failed"
        )
    invocation_reconstruction = (
        worker_invocation.reconstruct_worker_invocation_replay(
            invocation["worker_invocation_replay_reference"]
        )
    )
    invocation_artifact = invocation["worker_invocation_artifact"]
    if not all(
        (
            invocation_reconstruction.get("invocation_status")
            == worker_invocation.WORKER_INVOKED,
            invocation_reconstruction.get("worker_invocation_id")
            == invocation.get("worker_invocation_reference"),
            invocation_reconstruction.get("worker_dispatch_reference")
            == dispatch_artifact.get("worker_dispatch_id"),
            invocation_artifact.get("worker_dispatch_hash")
            == dispatch_artifact.get("artifact_hash"),
            invocation_reconstruction.get("worker_assignment_reference")
            == assignment_artifact.get("worker_assignment_id"),
            invocation_reconstruction.get("worker_invocation_request_reference")
            == invocation_request_artifact.get("worker_invocation_request_id"),
            invocation_reconstruction.get("authorization_reference")
            == invocation_request_artifact.get("authorization_reference"),
            invocation_reconstruction.get("execution_packet_reference")
            == invocation_request_artifact.get("execution_packet_reference"),
            invocation_reconstruction.get("worker_id")
            == selection.get("selected_resource_id"),
            invocation_reconstruction.get("chain_id")
            == invocation_request_artifact.get("chain_id"),
            invocation_reconstruction.get("worker_assigned") is True,
            invocation_reconstruction.get("worker_dispatched") is True,
            invocation_reconstruction.get("dispatch_requested") is True,
            invocation_reconstruction.get("worker_invoked") is True,
            invocation_reconstruction.get("execution_started") is False,
            invocation_reconstruction.get("result_created") is False,
            invocation_reconstruction.get("result_validated") is False,
            invocation_reconstruction.get("post_execution_replay_reviewed")
            is False,
            invocation_reconstruction.get("terminated") is False,
            invocation_reconstruction.get("governance_mutated") is False,
            invocation_reconstruction.get("replay_mutated") is False,
        )
    ):
        raise FailClosedRuntimeError(
            "G31 mutation continuation failed closed: Worker invocation Replay mismatch"
        )
    execution_replay_dir = (
        session_root
        / f"WORKER-EXECUTION-{invocation_artifact['artifact_hash'][-16:]}"
    )
    execution = execution_runtime.start_execution(
        execution_id=f"{invocation_artifact['worker_invocation_id']}:EXECUTION",
        invocation_artifact=invocation_artifact,
        invocation_replay=invocation["invocation_result_artifact"],
        dispatch_artifact=dispatch_artifact,
        worker_assignment_artifact=assignment_artifact,
        canonical_chain_id=invocation_artifact["chain_id"],
        execution_metadata={
            "execution_mode": "START_ONLY",
            "runtime_boundary": "INVOKED_TO_EXECUTING",
            "result_handling": "OUT_OF_SCOPE",
        },
        execution_context={
            "worker_reference": invocation_artifact["worker_id"],
            "request_type": "WORKER_INVOCATION_REQUEST",
            "capability_id": assignment_artifact["capability_id"],
            "allowed_effects": ["RECORD_EXECUTION_START"],
        },
        started_by="AIGOL",
        started_at=created,
        replay_reference=str(execution_replay_dir),
        replay_dir=execution_replay_dir,
    )
    execution_artifact = execution.get("execution_artifact")
    if (
        not isinstance(execution_artifact, dict)
        or execution_artifact.get("execution_status") != execution_runtime.EXECUTING
    ):
        raise FailClosedRuntimeError(
            "G31 mutation continuation failed closed: Worker execution failed"
        )
    execution_reconstruction = execution_runtime.reconstruct_execution_replay(
        execution_replay_dir
    )
    if not all(
        (
            execution_artifact.get("execution_status")
            == execution_runtime.EXECUTING,
            execution_artifact.get("worker_invocation_reference")
            == invocation_artifact.get("worker_invocation_id"),
            execution_artifact.get("worker_invocation_hash")
            == invocation_artifact.get("artifact_hash"),
            execution_artifact.get("worker_invocation_replay_hash")
            == invocation["invocation_result_artifact"].get("artifact_hash"),
            execution_artifact.get("dispatch_reference")
            == dispatch_artifact.get("worker_dispatch_id"),
            execution_artifact.get("dispatch_hash")
            == dispatch_artifact.get("artifact_hash"),
            execution_artifact.get("worker_assignment_reference")
            == assignment_artifact.get("worker_assignment_id"),
            execution_artifact.get("worker_assignment_hash")
            == assignment_artifact.get("artifact_hash"),
            execution_artifact.get("worker_reference")
            == invocation_artifact.get("worker_id"),
            execution_artifact.get("worker_hash")
            == invocation_artifact.get("worker_hash"),
            execution_artifact.get("execution_request_reference")
            == invocation_request_artifact.get("worker_invocation_request_id"),
            execution_artifact.get("readiness_reference")
            == invocation_request_artifact.get("execution_packet_reference"),
            execution_artifact.get("canonical_chain_id")
            == invocation_request_artifact.get("chain_id"),
            execution_artifact.get("capability_id")
            == assignment_artifact.get("capability_id"),
            execution_artifact.get("started_by") == "AIGOL",
            execution_artifact.get("execution_started") is True,
            execution_artifact.get("provider_authority") is False,
            execution_artifact.get("worker_self_started") is False,
            execution_artifact.get("completion_recorded") is False,
            execution_artifact.get("result_certified") is False,
            execution_artifact.get("governance_mutated") is False,
            execution_artifact.get("replay_mutated") is False,
            execution_reconstruction.get("execution_status")
            == execution_runtime.EXECUTING,
            execution_reconstruction.get("execution_id")
            == execution_artifact.get("execution_id"),
            execution_reconstruction.get("worker_invocation_reference")
            == invocation_artifact.get("worker_invocation_id"),
            execution_reconstruction.get("dispatch_reference")
            == dispatch_artifact.get("worker_dispatch_id"),
            execution_reconstruction.get("worker_assignment_reference")
            == assignment_artifact.get("worker_assignment_id"),
            execution_reconstruction.get("worker_reference")
            == invocation_artifact.get("worker_id"),
            execution_reconstruction.get("execution_request_reference")
            == invocation_request_artifact.get("worker_invocation_request_id"),
            execution_reconstruction.get("canonical_chain_id")
            == invocation_request_artifact.get("chain_id"),
            execution_reconstruction.get("provider_authority") is False,
            execution_reconstruction.get("completion_recorded") is False,
            execution_reconstruction.get("result_certified") is False,
            execution_reconstruction.get("governance_mutated") is False,
            execution_reconstruction.get("replay_mutated") is False,
            execution_reconstruction.get("replay_artifact_count") == 2,
        )
    ):
        raise FailClosedRuntimeError(
            "G31 mutation continuation failed closed: Worker execution Replay mismatch"
        )
    filesystem_execution = (
        filesystem_replace_worker.execute_consumed_authenticated_replace_v2(
            authenticated_request=request,
            consumption_reconstruction=consumption_reconstruction,
            worker_invocation_request_artifact=invocation_request_artifact,
            worker_assignment_artifact=assignment_artifact,
            execution_artifact=execution_artifact,
            execution_reconstruction=execution_reconstruction,
        )
    )
    filesystem_reconstruction = (
        filesystem_replace_worker.reconstruct_authenticated_replace_replay_v2(
            request
        )
    )
    if not all(
        (
            filesystem_execution.get("execution_status") == "COMPLETED",
            filesystem_execution.get("request_id") == request.get("request_id"),
            filesystem_execution.get("request_hash") == request.get("request_hash"),
            filesystem_execution.get("authorization_id")
            == request.get("authorization_id"),
            filesystem_execution.get("authorization_hash")
            == request.get("authorization_hash"),
            filesystem_execution.get("authorization_consumed") is True,
            filesystem_execution.get("worker_invoked") is True,
            filesystem_execution.get("provider_invoked") is False,
            filesystem_execution.get("command_executed") is False,
            filesystem_execution.get("repository_mutated") is True,
            filesystem_execution.get("main_repository_mutated") is True,
            filesystem_execution.get("restoration_performed") is False,
            filesystem_execution.get("recovery_required") is False,
            filesystem_execution.get("mutation_terminated") is False,
            filesystem_reconstruction.get("request_id") == request.get("request_id"),
            filesystem_reconstruction.get("request_hash")
            == request.get("request_hash"),
            filesystem_reconstruction.get("authorization_id")
            == request.get("authorization_id"),
            filesystem_reconstruction.get("event_keys")
            == [
                "request",
                "consumption",
                "journal",
                "started",
                "atomic",
                "result",
                "completion",
            ],
            filesystem_reconstruction.get("latest_event") == "MUTATION_COMPLETED",
            filesystem_reconstruction.get("replay_artifact_count") == 7,
            filesystem_execution.get("replay_hash")
            == filesystem_reconstruction.get("replay_hash"),
        )
    ):
        raise FailClosedRuntimeError(
            "G31 mutation continuation failed closed: Filesystem Replace Worker failed"
        )
    result_capture_replay_dir = (
        session_root
        / f"WORKER-RESULT-CAPTURE-{execution_artifact['artifact_hash'][-16:]}"
    )
    filesystem_result = (
        filesystem_result_capture.capture_completed_filesystem_replace_worker_result(
            authenticated_request=request,
            filesystem_worker_capture=filesystem_execution,
            filesystem_worker_reconstruction=filesystem_reconstruction,
            worker_invocation_artifact=invocation_artifact,
            worker_invocation_replay_reference=invocation[
                "worker_invocation_replay_reference"
            ],
            worker_assignment_artifact=assignment_artifact,
            execution_artifact=execution_artifact,
            execution_replay=execution["execution_replay"],
            execution_reconstruction=execution_reconstruction,
            execution_replay_reference=str(execution_replay_dir),
            captured_at=created,
            replay_dir=result_capture_replay_dir,
        )
    )
    if (
        filesystem_result.get("g31_filesystem_result_capture_status")
        != filesystem_result_capture.SUCCESS
    ):
        raise FailClosedRuntimeError(
            "G31 mutation continuation failed closed: Filesystem Replace Worker "
            f"Result Capture failed: {filesystem_result.get('failure_reason')}"
        )
    filesystem_result_reconstruction = (
        filesystem_result_capture.reconstruct_filesystem_replace_worker_result_capture_binding(
            binding_capture=filesystem_result,
            authenticated_request=request,
            filesystem_worker_capture=filesystem_execution,
            filesystem_worker_reconstruction=filesystem_reconstruction,
            worker_invocation_artifact=invocation_artifact,
            worker_invocation_replay_reference=invocation[
                "worker_invocation_replay_reference"
            ],
            worker_assignment_artifact=assignment_artifact,
            execution_artifact=execution_artifact,
            execution_replay=execution["execution_replay"],
            execution_reconstruction=execution_reconstruction,
            execution_replay_reference=str(execution_replay_dir),
        )
    )
    if not all(
        (
            filesystem_result_reconstruction.get(
                "g31_filesystem_result_capture_status"
            )
            == filesystem_result_capture.SUCCESS,
            filesystem_result_reconstruction.get("execution_reference")
            == execution_artifact.get("execution_id"),
            filesystem_result_reconstruction.get(
                "filesystem_replace_worker_capture_hash"
            )
            == filesystem_execution.get("capture_hash"),
            filesystem_result_reconstruction.get(
                "filesystem_replace_worker_replay_hash"
            )
            == filesystem_reconstruction.get("replay_hash"),
            filesystem_result_reconstruction.get("worker_result_captured")
            is True,
            filesystem_result_reconstruction.get("result_created") is True,
            filesystem_result_reconstruction.get("result_validated") is False,
            filesystem_result_reconstruction.get(
                "post_execution_replay_reviewed"
            )
            is False,
            filesystem_result_reconstruction.get("execution_certified")
            is False,
            filesystem_result_reconstruction.get("provider_invoked") is False,
            filesystem_result_reconstruction.get("command_executed") is False,
            filesystem_result_reconstruction.get("repository_mutated") is True,
            filesystem_result_reconstruction.get("governance_mutated") is False,
            filesystem_result_reconstruction.get("replay_mutated") is False,
            filesystem_result_reconstruction.get("replay_artifact_count") == 4,
        )
    ):
        raise FailClosedRuntimeError(
            "G31 mutation continuation failed closed: Filesystem Replace Worker "
            "Result Capture reconstruction mismatch"
        )
    result_validation_replay_dir = (
        session_root
        / (
            "WORKER-RESULT-VALIDATION-"
            f"{filesystem_result['worker_result_capture_artifact']['artifact_hash'][-16:]}"
        )
    )
    filesystem_validation = (
        filesystem_result_validation.validate_captured_filesystem_replace_worker_result(
            result_capture_binding_capture=filesystem_result,
            authenticated_request=request,
            filesystem_worker_capture=filesystem_execution,
            filesystem_worker_reconstruction=filesystem_reconstruction,
            worker_invocation_artifact=invocation_artifact,
            worker_invocation_replay_reference=invocation[
                "worker_invocation_replay_reference"
            ],
            worker_assignment_artifact=assignment_artifact,
            execution_artifact=execution_artifact,
            execution_replay=execution["execution_replay"],
            execution_reconstruction=execution_reconstruction,
            execution_replay_reference=str(execution_replay_dir),
            validated_at=created,
            replay_dir=result_validation_replay_dir,
        )
    )
    if (
        filesystem_validation.get("g31_filesystem_result_validation_status")
        != filesystem_result_validation.SUCCESS
    ):
        raise FailClosedRuntimeError(
            "G31 mutation continuation failed closed: Filesystem Replace Worker "
            f"Result Validation failed: {filesystem_validation.get('failure_reason')}"
        )
    filesystem_validation_reconstruction = (
        filesystem_result_validation.reconstruct_filesystem_replace_worker_result_validation_binding(
            validation_binding_capture=filesystem_validation,
            result_capture_binding_capture=filesystem_result,
            authenticated_request=request,
            filesystem_worker_capture=filesystem_execution,
            filesystem_worker_reconstruction=filesystem_reconstruction,
            worker_invocation_artifact=invocation_artifact,
            worker_invocation_replay_reference=invocation[
                "worker_invocation_replay_reference"
            ],
            worker_assignment_artifact=assignment_artifact,
            execution_artifact=execution_artifact,
            execution_replay=execution["execution_replay"],
            execution_reconstruction=execution_reconstruction,
            execution_replay_reference=str(execution_replay_dir),
        )
    )
    if not all(
        (
            filesystem_validation_reconstruction.get(
                "g31_filesystem_result_validation_status"
            )
            == filesystem_result_validation.SUCCESS,
            filesystem_validation_reconstruction.get("validation_status")
            == filesystem_result_validation.result_validation.RESULT_VALIDATED,
            filesystem_validation_reconstruction.get(
                "worker_result_capture_reference"
            )
            == filesystem_result["worker_result_capture_artifact"].get(
                "worker_result_capture_id"
            ),
            filesystem_validation_reconstruction.get("worker_output_hash")
            == filesystem_result.get("filesystem_replace_worker_output_hash"),
            filesystem_validation_reconstruction.get(
                "filesystem_replace_worker_capture_hash"
            )
            == filesystem_execution.get("capture_hash"),
            filesystem_validation_reconstruction.get(
                "filesystem_replace_worker_replay_hash"
            )
            == filesystem_reconstruction.get("replay_hash"),
            filesystem_validation_reconstruction.get("worker_result_captured")
            is True,
            filesystem_validation_reconstruction.get("result_created") is True,
            filesystem_validation_reconstruction.get("result_validated") is True,
            filesystem_validation_reconstruction.get(
                "task_outcome_satisfaction_evaluated"
            )
            is False,
            filesystem_validation_reconstruction.get("result_accepted") is False,
            filesystem_validation_reconstruction.get(
                "post_execution_replay_reviewed"
            )
            is False,
            filesystem_validation_reconstruction.get("execution_certified")
            is False,
            filesystem_validation_reconstruction.get("provider_invoked") is False,
            filesystem_validation_reconstruction.get("command_executed") is False,
            filesystem_validation_reconstruction.get("repository_mutated") is True,
            filesystem_validation_reconstruction.get("governance_mutated")
            is False,
            filesystem_validation_reconstruction.get("replay_mutated") is False,
            filesystem_validation_reconstruction.get("replay_artifact_count") == 4,
        )
    ):
        raise FailClosedRuntimeError(
            "G31 mutation continuation failed closed: Filesystem Replace Worker "
            "Result Validation reconstruction mismatch"
        )
    post_execution_review_replay_dir = (
        session_root
        / (
            "POST-EXECUTION-REPLAY-REVIEW-"
            f"{filesystem_validation['worker_result_validation_artifact']['artifact_hash'][-16:]}"
        )
    )
    filesystem_review = (
        filesystem_post_execution_review.review_validated_filesystem_replace_worker_result(
            validation_binding_capture=filesystem_validation,
            result_capture_binding_capture=filesystem_result,
            authenticated_request=request,
            filesystem_worker_capture=filesystem_execution,
            filesystem_worker_reconstruction=filesystem_reconstruction,
            worker_invocation_artifact=invocation_artifact,
            worker_invocation_replay_reference=invocation[
                "worker_invocation_replay_reference"
            ],
            worker_assignment_artifact=assignment_artifact,
            execution_artifact=execution_artifact,
            execution_replay=execution["execution_replay"],
            execution_reconstruction=execution_reconstruction,
            execution_replay_reference=str(execution_replay_dir),
            reviewed_at=created,
            replay_dir=post_execution_review_replay_dir,
        )
    )
    if (
        filesystem_review.get(
            "g31_filesystem_post_execution_replay_review_status"
        )
        != filesystem_post_execution_review.SUCCESS
    ):
        raise FailClosedRuntimeError(
            "G31 mutation continuation failed closed: Filesystem Replace Worker "
            "Post-Execution Replay Review failed: "
            f"{filesystem_review.get('failure_reason')}"
        )
    filesystem_review_reconstruction = (
        filesystem_post_execution_review.reconstruct_filesystem_replace_worker_post_execution_replay_review_binding(
            review_binding_capture=filesystem_review,
            validation_binding_capture=filesystem_validation,
            result_capture_binding_capture=filesystem_result,
            authenticated_request=request,
            filesystem_worker_capture=filesystem_execution,
            filesystem_worker_reconstruction=filesystem_reconstruction,
            worker_invocation_artifact=invocation_artifact,
            worker_invocation_replay_reference=invocation[
                "worker_invocation_replay_reference"
            ],
            worker_assignment_artifact=assignment_artifact,
            execution_artifact=execution_artifact,
            execution_replay=execution["execution_replay"],
            execution_reconstruction=execution_reconstruction,
            execution_replay_reference=str(execution_replay_dir),
        )
    )
    if not all(
        (
            filesystem_review_reconstruction.get(
                "g31_filesystem_post_execution_replay_review_status"
            )
            == filesystem_post_execution_review.SUCCESS,
            filesystem_review_reconstruction.get("review_status")
            == filesystem_post_execution_review.replay_review.REVIEW_COMPLETED,
            filesystem_review_reconstruction.get(
                "worker_result_validation_reference"
            )
            == filesystem_validation[
                "worker_result_validation_artifact"
            ].get("worker_result_validation_id"),
            filesystem_review_reconstruction.get(
                "worker_result_validation_hash"
            )
            == filesystem_validation[
                "worker_result_validation_artifact"
            ].get("artifact_hash"),
            filesystem_review_reconstruction.get(
                "authorization_commitment_kind"
            )
            == filesystem_post_execution_review.RECORD_HASH_COMMITMENT,
            filesystem_review_reconstruction.get(
                "authorization_commitment"
            )
            == request.get("authorization_hash"),
            filesystem_review_reconstruction.get("worker_output_hash")
            == filesystem_result.get("filesystem_replace_worker_output_hash"),
            filesystem_review_reconstruction.get(
                "filesystem_replace_worker_capture_hash"
            )
            == filesystem_execution.get("capture_hash"),
            filesystem_review_reconstruction.get(
                "filesystem_replace_worker_replay_hash"
            )
            == filesystem_reconstruction.get("replay_hash"),
            filesystem_review_reconstruction.get("worker_result_captured")
            is True,
            filesystem_review_reconstruction.get("result_created") is True,
            filesystem_review_reconstruction.get("result_validated") is True,
            filesystem_review_reconstruction.get(
                "task_outcome_satisfaction_evaluated"
            )
            is False,
            filesystem_review_reconstruction.get("result_accepted") is False,
            filesystem_review_reconstruction.get(
                "post_execution_replay_reviewed"
            )
            is True,
            filesystem_review_reconstruction.get("execution_certified")
            is False,
            filesystem_review_reconstruction.get("provider_invoked") is False,
            filesystem_review_reconstruction.get("command_executed") is False,
            filesystem_review_reconstruction.get("repository_mutated") is True,
            filesystem_review_reconstruction.get("governance_mutated")
            is False,
            filesystem_review_reconstruction.get("replay_mutated") is False,
            filesystem_review_reconstruction.get("replay_artifact_count") == 4,
        )
    ):
        raise FailClosedRuntimeError(
            "G31 mutation continuation failed closed: Filesystem Replace Worker "
            "Post-Execution Replay Review reconstruction mismatch"
        )
    governed_termination_replay_dir = (
        session_root
        / (
            "GOVERNED-TERMINATION-"
            f"{filesystem_review['post_execution_replay_review_artifact']['artifact_hash'][-16:]}"
        )
    )
    filesystem_replay_review_reconstructor = (
        filesystem_post_execution_review.reconstruct_schema_aware_post_execution_replay_review
    )
    filesystem_termination = governed_termination.terminate_reviewed_operation(
        governed_termination_id=(
            f"{filesystem_review['post_execution_replay_review_reference']}:"
            "GOVERNED-TERMINATION"
        ),
        post_execution_replay_review_artifact=filesystem_review[
            "post_execution_replay_review_artifact"
        ],
        post_execution_replay_review_replay_reference=filesystem_review[
            "post_execution_replay_review_replay_reference"
        ],
        terminated_by="AIGOL_GOVERNANCE",
        terminated_at=created,
        replay_dir=governed_termination_replay_dir,
        replay_review_reconstructor=filesystem_replay_review_reconstructor,
    )
    if (
        filesystem_termination.get("termination_status")
        != governed_termination.TERMINATED
    ):
        raise FailClosedRuntimeError(
            "G31 mutation continuation failed closed: Filesystem Replace Worker "
            f"Governed Termination failed: {filesystem_termination.get('failure_reason')}"
        )
    filesystem_termination_reconstruction = (
        governed_termination.reconstruct_governed_termination_replay(
            governed_termination_replay_dir,
            replay_review_reconstructor=filesystem_replay_review_reconstructor,
        )
    )
    if not all(
        (
            filesystem_termination_reconstruction.get("termination_status")
            == governed_termination.TERMINATED,
            filesystem_termination_reconstruction.get(
                "post_execution_replay_review_reference"
            )
            == filesystem_review["post_execution_replay_review_reference"],
            filesystem_termination_reconstruction.get(
                "worker_result_validation_reference"
            )
            == filesystem_validation[
                "worker_result_validation_artifact"
            ].get("worker_result_validation_id"),
            filesystem_termination_reconstruction.get("execution_reference")
            == execution_artifact.get("execution_id"),
            filesystem_termination_reconstruction.get("worker_id")
            == invocation_artifact.get("worker_id"),
            filesystem_termination_reconstruction.get("terminated") is True,
            filesystem_termination_reconstruction.get(
                "post_execution_replay_reviewed"
            )
            is True,
            filesystem_termination_reconstruction.get("governance_mutated")
            is False,
            filesystem_termination_reconstruction.get("replay_mutated") is False,
            filesystem_termination_reconstruction.get("replay_artifact_count")
            == 4,
        )
    ):
        raise FailClosedRuntimeError(
            "G31 mutation continuation failed closed: Filesystem Replace Worker "
            "Governed Termination reconstruction mismatch"
        )
    final_execution_certification_replay_dir = (
        session_root
        / (
            "FINAL-EXECUTION-CERTIFICATION-"
            f"{filesystem_termination['governed_termination_artifact']['artifact_hash'][-16:]}"
        )
    )

    def reconstruct_filesystem_governed_termination(
        replay_reference: str | Path,
    ) -> dict[str, Any]:
        return governed_termination.reconstruct_governed_termination_replay(
            replay_reference,
            replay_review_reconstructor=filesystem_replay_review_reconstructor,
        )

    filesystem_certification = (
        final_execution_certification.certify_governed_termination(
            binding_id=(
                f"{filesystem_termination['governed_termination_reference']}:"
                "FINAL-EXECUTION-CERTIFICATION"
            ),
            terminal_capture=filesystem_termination,
            termination_replay_reference=filesystem_termination[
                "governed_termination_replay_reference"
            ],
            termination_reconstructor=(
                reconstruct_filesystem_governed_termination
            ),
            certified_by="AIGOL_GOVERNANCE",
            certified_at=created,
            replay_dir=final_execution_certification_replay_dir,
        )
    )
    if (
        filesystem_certification.get("binding_status")
        != final_execution_certification.SUCCESS
    ):
        raise FailClosedRuntimeError(
            "G31 mutation continuation failed closed: Filesystem Replace Worker "
            "Final Execution Certification failed: "
            f"{filesystem_certification.get('failure_reason')}"
        )
    merged.update(
        {
            "mutation_authorization_capture": authorization,
            "mutation_authorization_reconstruction": authorization_reconstruction,
            "mutation_authorization_actor_replay_capture": actor_replay,
            "mutation_authorization_actor_replay_reconstruction": (
                actor_replay_reconstruction
            ),
            "mutation_authorization_id": actor_replay_reconstruction[
                "authorization_id"
            ],
            "mutation_authorization_hash": actor_replay_reconstruction[
                "authorization_hash"
            ],
            "authenticated_replacement_request": request,
            "authenticated_replacement_request_reconstruction": (
                request_reconstruction
            ),
            "authenticated_replacement_request_id": request["request_id"],
            "authenticated_replacement_request_hash": request["request_hash"],
            "authenticated_replacement_request_replay_reference": (
                request_reconstruction["request_replay_reference"]
            ),
            "authenticated_replacement_request_replay_hash": (
                request_reconstruction["replay_hash"]
            ),
            "authorization_consumption_reconstruction": consumption_reconstruction,
            "authorization_consumption_identity": consumption_reconstruction[
                "consumption_identity"
            ],
            "authorization_consumption_replay_reference": (
                consumption_reconstruction["request_replay_reference"]
            ),
            "authorization_consumption_replay_hash": consumption_reconstruction[
                "replay_hash"
            ],
            "consumed_replacement_worker_selection_capture": selection,
            "consumed_replacement_worker_selection_reconstruction": selection[
                "certified_selection_reconstruction"
            ],
            "consumed_replacement_selection_context": selection[
                "consumed_replacement_selection_context"
            ],
            "consumed_replacement_selection_context_hash": selection[
                "consumed_replacement_selection_context_hash"
            ],
            "worker_selection_status": selection["selection_status"],
            "selected_resource_id": selection["selected_resource_id"],
            "selected_role_type": selection["selected_role_type"],
            "worker_selected": selection["worker_selected"],
            "worker_invocation_request_capture": invocation_request,
            "worker_invocation_request_status": invocation_request[
                "request_status"
            ],
            "worker_invocation_request_created": invocation_request[
                "request_status"
            ] == worker_request.WORKER_INVOCATION_REQUEST_CREATED,
            "worker_assignment_capture": assignment,
            "worker_assignment_reconstruction": assignment_reconstruction,
            "worker_assignment_status": assignment["assignment_status"],
            "worker_assignment_id": assignment["worker_assignment_reference"],
            "worker_assignment_replay_reference": assignment[
                "worker_assignment_replay_reference"
            ],
            "worker_assignment_replay_hash": assignment_reconstruction[
                "replay_hash"
            ],
            "assigned_worker_id": assignment["worker_id"],
            "worker_dispatch_capture": dispatch,
            "worker_dispatch_reconstruction": dispatch_reconstruction,
            "worker_dispatch_status": dispatch["dispatch_status"],
            "worker_dispatch_id": dispatch["worker_dispatch_reference"],
            "worker_dispatch_replay_reference": dispatch[
                "worker_dispatch_replay_reference"
            ],
            "worker_dispatch_replay_hash": dispatch_reconstruction["replay_hash"],
            "worker_invocation_capture": invocation,
            "worker_invocation_reconstruction": invocation_reconstruction,
            "worker_invocation_status": invocation["invocation_status"],
            "worker_invocation_id": invocation["worker_invocation_reference"],
            "worker_invocation_replay_reference": invocation[
                "worker_invocation_replay_reference"
            ],
            "worker_invocation_replay_hash": invocation_reconstruction[
                "replay_hash"
            ],
            "worker_execution_capture": execution,
            "worker_execution_reconstruction": execution_reconstruction,
            "worker_execution_status": execution_artifact["execution_status"],
            "worker_execution_id": execution_artifact["execution_id"],
            "worker_execution_replay_reference": str(execution_replay_dir),
            "worker_execution_replay_hash": execution_reconstruction[
                "replay_hash"
            ],
            "filesystem_replace_worker_capture": filesystem_execution,
            "filesystem_replace_worker_reconstruction": filesystem_reconstruction,
            "filesystem_replace_worker_status": filesystem_execution[
                "execution_status"
            ],
            "filesystem_replace_worker_replay_reference": (
                filesystem_reconstruction["request_replay_reference"]
            ),
            "filesystem_replace_worker_replay_hash": filesystem_reconstruction[
                "replay_hash"
            ],
            "filesystem_replace_worker_result_capture": filesystem_result,
            "filesystem_replace_worker_result_capture_reconstruction": (
                filesystem_result_reconstruction
            ),
            "filesystem_replace_worker_result_capture_status": (
                filesystem_result["g31_filesystem_result_capture_status"]
            ),
            "filesystem_replace_worker_output_artifact": filesystem_result[
                "filesystem_replace_worker_output_artifact"
            ],
            "filesystem_replace_worker_output_hash": filesystem_result[
                "filesystem_replace_worker_output_hash"
            ],
            "filesystem_replace_worker_result_capture_replay_reference": (
                filesystem_result["worker_result_capture_replay_reference"]
            ),
            "filesystem_replace_worker_result_capture_replay_hash": (
                filesystem_result_reconstruction["replay_hash"]
            ),
            "filesystem_replace_worker_result_validation": filesystem_validation,
            "filesystem_replace_worker_result_validation_reconstruction": (
                filesystem_validation_reconstruction
            ),
            "filesystem_replace_worker_result_validation_status": (
                filesystem_validation[
                    "g31_filesystem_result_validation_status"
                ]
            ),
            "filesystem_replace_worker_result_validation_replay_reference": (
                filesystem_validation[
                    "worker_result_validation_replay_reference"
                ]
            ),
            "filesystem_replace_worker_result_validation_replay_hash": (
                filesystem_validation_reconstruction["replay_hash"]
            ),
            "filesystem_replace_worker_post_execution_replay_review": (
                filesystem_review
            ),
            "filesystem_replace_worker_post_execution_replay_review_reconstruction": (
                filesystem_review_reconstruction
            ),
            "filesystem_replace_worker_post_execution_replay_review_status": (
                filesystem_review[
                    "g31_filesystem_post_execution_replay_review_status"
                ]
            ),
            "filesystem_replace_worker_post_execution_replay_review_reference": (
                filesystem_review[
                    "post_execution_replay_review_reference"
                ]
            ),
            "filesystem_replace_worker_post_execution_replay_review_replay_reference": (
                filesystem_review[
                    "post_execution_replay_review_replay_reference"
                ]
            ),
            "filesystem_replace_worker_post_execution_replay_review_replay_hash": (
                filesystem_review_reconstruction["replay_hash"]
            ),
            "filesystem_replace_worker_authorization_lineage_schema": (
                filesystem_review_reconstruction[
                    "authorization_lineage_schema"
                ]
            ),
            "filesystem_replace_worker_authorization_commitment_kind": (
                filesystem_review_reconstruction[
                    "authorization_commitment_kind"
                ]
            ),
            "filesystem_replace_worker_governed_termination": (
                filesystem_termination
            ),
            "filesystem_replace_worker_governed_termination_reconstruction": (
                filesystem_termination_reconstruction
            ),
            "filesystem_replace_worker_governed_termination_status": (
                filesystem_termination["termination_status"]
            ),
            "filesystem_replace_worker_governed_termination_reference": (
                filesystem_termination["governed_termination_reference"]
            ),
            "filesystem_replace_worker_governed_termination_replay_reference": (
                filesystem_termination[
                    "governed_termination_replay_reference"
                ]
            ),
            "filesystem_replace_worker_governed_termination_replay_hash": (
                filesystem_termination_reconstruction["replay_hash"]
            ),
            "filesystem_replace_worker_final_execution_certification": (
                filesystem_certification
            ),
            "filesystem_replace_worker_final_execution_certification_status": (
                filesystem_certification["binding_status"]
            ),
            "filesystem_replace_worker_final_execution_certification_reference": (
                filesystem_certification[
                    "final_execution_certification_reference"
                ]
            ),
            "filesystem_replace_worker_final_execution_certification_hash": (
                filesystem_certification[
                    "final_execution_certification_hash"
                ]
            ),
            "filesystem_replace_worker_final_execution_certification_replay_reference": (
                filesystem_certification[
                    "final_execution_certification_replay_reference"
                ]
            ),
            "filesystem_replace_worker_final_execution_certification_replay_hash": (
                filesystem_certification[
                    "final_execution_certification_replay_hash"
                ]
            ),
            "filesystem_replace_worker_final_execution_certification_projection": (
                filesystem_certification[
                    "result_validation_compatibility_projection"
                ]
            ),
            "filesystem_replace_worker_final_execution_certification_projection_hash": (
                filesystem_certification[
                    "result_validation_compatibility_projection_hash"
                ]
            ),
            "worker_assigned": True,
            "worker_dispatched": True,
            "dispatch_requested": True,
            "provider_invoked": False,
            "worker_invoked": True,
            "execution_started": True,
            "execution_requested": True,
            "worker_execution_performed": True,
            "worker_result_captured": True,
            "result_created": True,
            "result_validated": True,
            "post_execution_replay_reviewed": True,
            "terminated": True,
            "execution_certified": True,
            "command_executed": False,
            "target_opened": True,
            "repository_mutated": True,
            "main_repository_mutated": True,
            "restoration_started": False,
            "rollback_started": False,
            "recovery_started": False,
            "governance_mutated": False,
            "replay_mutated": False,
            "runtime_replay_reference": str(execution_replay_dir),
        }
    )
    for field in (
        "mutation_authorized",
        "authorization_actor_bound",
        "authorization_replay_recorded",
        "authorization_consumed",
        "replace_request_created",
        "provider_invoked",
        "command_executed",
        "repository_mutated",
        "main_repository_mutated",
    ):
        merged[field] = actor_replay_reconstruction[field]
    merged["replace_request_created"] = True
    merged["authorization_consumed"] = True
    merged["repository_mutated"] = filesystem_execution["repository_mutated"]
    merged["main_repository_mutated"] = filesystem_execution[
        "main_repository_mutated"
    ]
    return merged


def _render_task_outcome_review_lineage(review: dict[str, Any]) -> str:
    """Render exact review identities without acquiring authority."""

    packet = review["task_outcome_review_packet_artifact"]
    capture = packet["capture_binding"]
    capture_artifact = capture["artifact"]
    validation = packet["governance_validation_binding"]
    validation_artifact = validation["artifact"]
    return "\n".join(
        (
            "Exact Task-Outcome Review Lineage",
            f"Capture Identity: {capture_artifact['worker_result_capture_id']}",
            f"Capture Artifact Hash: {capture_artifact['artifact_hash']}",
            f"Capture Replay Hash: {capture['replay_hash']}",
            f"Governance Validation Identity: {validation_artifact['worker_result_validation_id']}",
            f"Governance Validation Artifact Hash: {validation_artifact['artifact_hash']}",
            f"Governance Validation Status: {validation['status']}",
            f"Governance Validation Meaning: {validation['canonical_meaning']}",
            f"Patch Applied: {packet['patch_applied']}",
            "Tests Run Against Applied Patch: "
            f"{packet['tests_run_against_applied_patch']}",
        )
    )


def _input_sequence(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        try:
            return next(iterator)
        except StopIteration:
            return "exit"

    return read


def _latest_turn(conversation_result: dict[str, Any]) -> dict[str, Any]:
    turns = conversation_result.get("turns")
    if not isinstance(turns, list):
        return {}
    for turn in reversed(turns):
        if isinstance(turn, dict):
            return turn
    return {}


def _runtime_bound(conversation_result: dict[str, Any], projection: dict[str, Any]) -> bool:
    return (
        conversation_result.get("failed_turns") == 0
        and projection.get("provider_invocation_reached") is True
        and projection.get("worker_execution_reached") is True
        and projection.get("replay_certification_reached") is True
    )


def _runtime_status_projection(
    conversation_result: dict[str, Any],
    latest_turn: dict[str, Any],
) -> dict[str, Any]:
    """Project certified runtime status from latest-turn fields and replay evidence."""

    turn_replay_root = _discover_turn_replay_root(latest_turn)
    worker_lifecycle_root = (
        turn_replay_root
        / "governed_bridge_certified_development_continuation"
        / "worker_lifecycle_continuation"
        if turn_replay_root is not None
        else None
    )
    execution_authorization_artifact = _read_replay_artifact_path(
        turn_replay_root
        / "governed_bridge_certified_development_continuation"
        / "execution_authorization"
        / "002_authorization_artifact_recorded.json"
        if turn_replay_root is not None
        else None
    )
    worker_invocation_artifact = _read_replay_artifact_path(
        worker_lifecycle_root / "worker_invocation" / "003_invocation_result_recorded.json"
        if worker_lifecycle_root is not None
        else None
    )
    universal_worker_binding_artifact = _read_replay_artifact_path(
        worker_lifecycle_root
        / "universal_provider_worker"
        / "000_universal_provider_worker_binding_recorded.json"
        if worker_lifecycle_root is not None
        else None
    )
    universal_worker_artifact = _read_replay_artifact(
        latest_turn.get("universal_provider_worker_replay_reference"),
        "001_universal_provider_worker_result_recorded.json",
    ) or _read_replay_artifact_path(
        worker_lifecycle_root
        / "universal_provider_worker"
        / "001_universal_provider_worker_result_recorded.json"
        if worker_lifecycle_root is not None
        else None
    )
    resource_selection_artifact = _read_replay_artifact_path(
        worker_lifecycle_root
        / "universal_provider_worker"
        / "universal_resource_selection"
        / "001_resource_selection_returned.json"
        if worker_lifecycle_root is not None
        else None
    )
    selected_provider_artifact = _read_replay_artifact_path(
        worker_lifecycle_root
        / "universal_provider_worker"
        / "selected_provider_openai"
        / "001_openai_provider_adapter_recorded.json"
        if worker_lifecycle_root is not None
        else None
    )
    openai_worker_result_artifact = _read_replay_artifact_path(
        worker_lifecycle_root
        / "universal_provider_worker"
        / "selected_provider_openai"
        / "002_openai_external_worker_result_recorded.json"
        if worker_lifecycle_root is not None
        else None
    )
    certified_provider_attachment_artifact = _read_replay_artifact_path(
        worker_lifecycle_root
        / "universal_provider_worker"
        / "selected_provider_openai"
        / "certified_provider_attachment"
        / "002_certified_provider_attachment_recorded.json"
        if worker_lifecycle_root is not None
        else None
    )
    replay_certification_artifact = _read_replay_artifact(
        latest_turn.get("replay_certification_replay_reference"),
        "000_replay_certification_artifact_recorded.json",
    ) or _read_replay_artifact_path(
        worker_lifecycle_root / "replay_certification" / "000_replay_certification_artifact_recorded.json"
        if worker_lifecycle_root is not None
        else None
    )

    universal_provider_completed = (
        latest_turn.get("universal_provider_worker_status") == "UNIVERSAL_PROVIDER_WORKER_COMPLETED"
        or universal_worker_artifact.get("universal_provider_worker_status")
        == "UNIVERSAL_PROVIDER_WORKER_COMPLETED"
        or universal_worker_binding_artifact.get("binding_status") == "UNIVERSAL_PROVIDER_WORKER_COMPLETED"
    )
    smart_selection_reached = (
        latest_turn.get("smart_provider_selection_executed") is True
        or latest_turn.get("smart_provider_selection_reached") is True
        or universal_worker_artifact.get("smart_selection_executed") is True
        or universal_worker_binding_artifact.get("smart_selection_executed") is True
        or resource_selection_artifact.get("selection_status") == "RESOURCE_SELECTION_SUCCEEDED"
    )
    universal_provider_reached = (
        latest_turn.get("universal_provider_runtime_reached") is True
        or universal_provider_completed
        or bool(universal_worker_artifact)
        or bool(universal_worker_binding_artifact)
        or bool(resource_selection_artifact)
        or bool(selected_provider_artifact)
    )
    provider_invocation_reached = (
        latest_turn.get("openai_provider_reached") is True
        or latest_turn.get("provider_invoked") is True
        or latest_turn.get("provider_invocation_reached") is True
        or universal_provider_reached
        or universal_worker_artifact.get("provider_invocation_delegated") is True
        or universal_worker_artifact.get("certified_provider_attachment_reused") is True
        or selected_provider_artifact.get("provider_invoked_inside_adapter") is True
        or bool(openai_worker_result_artifact)
        or bool(certified_provider_attachment_artifact)
    )
    worker_execution_reached = (
        latest_turn.get("worker_invoked") is True
        or latest_turn.get("worker_invocation_reached") is True
        or latest_turn.get("worker_execution_candidate_reached") is True
        or latest_turn.get("external_task_package_reached") is True
        or latest_turn.get("worker_invocation_status") == "WORKER_INVOKED"
        or worker_invocation_artifact.get("worker_invoked") is True
        or worker_invocation_artifact.get("invocation_status") == "WORKER_INVOKED"
        or universal_provider_completed
    )
    replay_certification_reached = (
        latest_turn.get("replay_certification_reached") is True
        or latest_turn.get("replay_certification_status") == "REPLAY_CERTIFICATION_COMPLETED"
        or replay_certification_artifact.get("certification_status") == "REPLAY_CERTIFICATION_COMPLETED"
    )
    latest_turn_authorization_status = latest_turn.get("execution_authorization_status")
    execution_authorization_artifact_recognized = (
        execution_authorization_artifact.get("artifact_type")
        == "EXECUTION_AUTHORIZATION_ARTIFACT_V1"
    )
    authorization_status = (
        latest_turn_authorization_status
        if latest_turn_authorization_status is not None
        else (
            execution_authorization_artifact.get("authorization_status")
            if execution_authorization_artifact_recognized
            else None
        )
    )
    governance_authorization_reached = authorization_status == "EXECUTION_AUTHORIZED"
    projection_evidence = {
        "latest_turn_used": bool(latest_turn),
        "turn_replay_discovery_used": turn_replay_root is not None,
        "turn_replay_root": str(turn_replay_root) if turn_replay_root is not None else None,
        "worker_lifecycle_replay_root": (
            str(worker_lifecycle_root) if worker_lifecycle_root is not None else None
        ),
        "execution_authorization_replay_inspected": bool(execution_authorization_artifact),
        "execution_authorization_artifact_recognized": (
            execution_authorization_artifact_recognized
        ),
        "execution_authorization_status": authorization_status,
        "execution_authorization_status_source": (
            "LATEST_TURN"
            if latest_turn_authorization_status is not None
            else (
                "EXECUTION_AUTHORIZATION_REPLAY"
                if execution_authorization_artifact_recognized
                else "NOT_AVAILABLE"
            )
        ),
        "worker_invocation_replay_inspected": bool(worker_invocation_artifact),
        "universal_provider_worker_binding_replay_inspected": bool(universal_worker_binding_artifact),
        "universal_provider_worker_replay_inspected": bool(universal_worker_artifact),
        "resource_selection_replay_inspected": bool(resource_selection_artifact),
        "selected_provider_replay_inspected": bool(selected_provider_artifact),
        "openai_worker_result_replay_inspected": bool(openai_worker_result_artifact),
        "certified_provider_attachment_replay_inspected": bool(certified_provider_attachment_artifact),
        "replay_certification_replay_inspected": bool(replay_certification_artifact),
        "conversation_failed_turns": conversation_result.get("failed_turns"),
        "worker_invocation_status": (
            latest_turn.get("worker_invocation_status")
            or worker_invocation_artifact.get("invocation_status")
        ),
        "universal_provider_worker_binding_status": universal_worker_binding_artifact.get("binding_status"),
        "universal_provider_worker_status": (
            latest_turn.get("universal_provider_worker_status")
            or universal_worker_artifact.get("universal_provider_worker_status")
        ),
        "selected_provider_resource_id": (
            latest_turn.get("selected_provider_resource_id")
            or universal_worker_artifact.get("selected_resource_id")
            or universal_worker_binding_artifact.get("selected_resource_id")
            or resource_selection_artifact.get("selected_resource_id")
        ),
        "resource_selection_status": resource_selection_artifact.get("selection_status"),
        "selected_provider_status": selected_provider_artifact.get("provider_status"),
        "certified_provider_attachment_status": certified_provider_attachment_artifact.get("provider_status"),
        "replay_certification_status": (
            latest_turn.get("replay_certification_status")
            or replay_certification_artifact.get("certification_status")
        ),
    }
    return {
        "governance_authorization_reached": governance_authorization_reached,
        "provider_invocation_reached": provider_invocation_reached,
        "worker_execution_reached": worker_execution_reached,
        "replay_certification_reached": replay_certification_reached,
        "universal_provider_runtime_reached": universal_provider_reached,
        "smart_provider_selection_reached": smart_selection_reached,
        "projection_source": "LATEST_TURN_AND_REPLAY_EVIDENCE",
        "projection_evidence": projection_evidence,
    }


def _read_replay_artifact(replay_reference: Any, filename: str) -> dict[str, Any]:
    if not isinstance(replay_reference, str) or not replay_reference.strip():
        return {}
    return _read_replay_artifact_path(Path(replay_reference) / filename)


def _read_replay_artifact_path(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    if not path.exists() or not path.is_file():
        return {}
    try:
        with path.open(encoding="utf-8") as handle:
            wrapper = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}
    artifact = wrapper.get("artifact") if isinstance(wrapper, dict) else None
    return deepcopy(artifact) if isinstance(artifact, dict) else {}


def _discover_turn_replay_root(latest_turn: dict[str, Any]) -> Path | None:
    for candidate in _turn_replay_candidates(latest_turn):
        discovered = _nearest_turn_replay_root(candidate)
        if discovered is not None:
            return discovered
    return None


def _turn_replay_candidates(latest_turn: dict[str, Any]) -> list[Path]:
    candidates: list[Path] = []
    for field_name in (
        "replay_reference",
        "conversation_replay_reference",
        "runtime_replay_reference",
        "universal_provider_worker_replay_reference",
        "replay_certification_replay_reference",
        "execution_summary_reference",
        "human_confirmation_reference",
    ):
        value = latest_turn.get(field_name)
        if isinstance(value, str) and value.strip():
            candidates.append(Path(value))
    return candidates


def _nearest_turn_replay_root(path: Path) -> Path | None:
    current = path if path.suffix == "" else path.parent
    search_path = [current, *current.parents]
    for candidate in search_path:
        if candidate.name.startswith("TURN-"):
            return candidate
        if _looks_like_turn_replay_root(candidate):
            return candidate
    return None


def _looks_like_turn_replay_root(path: Path) -> bool:
    return (
        path.exists()
        and path.is_dir()
        and (
            (path / "governed_bridge_certified_development_continuation").exists()
            or (path / "source_router").exists()
            or (path / "turn_completion").exists()
        )
    )


def _canonical_che_delivery_store_v1(runtime_scope_identity: str) -> Path:
    return Path(runtime_scope_identity) / "canonical_human_entry_delivery_resolution_v1"


def _canonical_che_delivery_record_path_v1(
    *,
    runtime_scope_identity: str,
    actor_identity: str,
    session_identity: str,
    workspace_identity: str,
    idempotency_identity: str,
) -> Path:
    digest = replay_hash(
        {
            "actor_identity": actor_identity,
            "session_identity": session_identity,
            "workspace_identity": workspace_identity,
            "runtime_scope_identity": runtime_scope_identity,
            "idempotency_identity": idempotency_identity,
        }
    ).removeprefix("sha256:")
    return _canonical_che_delivery_store_v1(runtime_scope_identity) / (
        f"record-{digest}.json"
    )


def _canonical_che_delivery_request_binding_hash_v1(
    request: CanonicalHumanEntryRequestEnvelopeV1,
    continuation: CanonicalContinuationEnvelopeV1 | None,
) -> str:
    return replay_hash(
        {
            "request_identity": request.request_identity,
            "source_act_digest": canonical_che_request_source_act_digest_v1(
                request
            ),
            "order_identity": request.order_identity,
            "idempotency_identity": request.idempotency_identity,
            "actor_identity": request.actor_identity,
            "session_identity": request.session_identity,
            "workspace_identity": request.workspace_identity,
            "runtime_scope_identity": request.runtime_scope_identity,
            "interaction_identity": (
                continuation.interaction_identity
                if continuation is not None
                else NOT_APPLICABLE
            ),
            "continuation_identity": (
                continuation.continuation_identity
                if continuation is not None
                else NOT_APPLICABLE
            ),
        }
    )


def _canonical_che_delivery_record_identity_v1(record: dict[str, Any]) -> str:
    return "CHE-DELIVERY-RECORD-" + replay_hash(
        {
            "actor_identity": record["actor_identity"],
            "session_identity": record["session_identity"],
            "workspace_identity": record["workspace_identity"],
            "runtime_scope_identity": record["runtime_scope_identity"],
            "idempotency_identity": record["idempotency_identity"],
        }
    ).removeprefix("sha256:")


def _canonical_che_reference_correlations_v1(
    reference_set: CanonicalOpaqueReferenceSetV1 | None,
) -> tuple[dict[str, Any], ...]:
    if reference_set is None:
        return ()
    return tuple(
        {
            "reference_identity": reference.reference_identity,
            "ordered_position": reference.ordered_position,
            "provenance_identity": reference.provenance_identity,
            "content_owner_identity": reference.content_owner_identity,
            "custody_owner_identity": reference.custody_owner_identity,
            "validation_owner_identity": reference.validation_owner_identity,
            "availability_status": reference.availability_status,
            "integrity_algorithm": reference.integrity_algorithm,
            "integrity_reference": reference.integrity_reference,
            "validation_evidence_identity": reference.validation_evidence_identity,
            "validation_evidence_digest": reference.validation_evidence_digest,
            "retry_of_reference_set_digest": (
                reference_set.retry_of_reference_set_digest or NOT_APPLICABLE
            ),
        }
        for reference in reference_set.references
    )


def _canonical_che_evidence_correlation_v1(
    *,
    request: CanonicalHumanEntryRequestEnvelopeV1,
    delivery_record: dict[str, Any],
    response: CanonicalHumanEntryResponseEnvelopeV1 | None,
    continuation: CanonicalContinuationEnvelopeV1 | None,
    authority_act: CanonicalHumanAuthorityActV1 | None,
    reference_set: CanonicalOpaqueReferenceSetV1 | None,
    delivery_status: str,
    evidence_status: str,
) -> CanonicalCHEEvidenceCorrelationV1:
    absent = CORRELATION_NOT_APPLICABLE
    transition = response.owner_transition if response is not None else None
    projection = response.owner_projection if response is not None else None
    presentation = response.presentation if response is not None else None
    failure = response.common_failure if response is not None else None
    active_continuation = continuation or (
        response.continuation_envelope if response is not None else None
    )
    interaction_identity = (
        active_continuation.interaction_identity
        if active_continuation is not None
        else absent
    )
    conversation_identity = (
        active_continuation.conversation_identity
        if active_continuation is not None
        else (
            transition.owner_state_identity
            if transition is not None
            else absent
        )
    )
    replay_references = response.replay_references if response is not None else ()
    certification_references = (
        response.certification_references if response is not None else ()
    )
    return create_canonical_che_evidence_correlation_v1(
        contract_version=CANONICAL_CHE_EVIDENCE_CORRELATION_CONTRACT_VERSION,
        interaction_identity=interaction_identity,
        conversation_identity=conversation_identity,
        session_identity=request.session_identity,
        workspace_identity=request.workspace_identity,
        runtime_scope_identity=request.runtime_scope_identity,
        actor_identity=request.actor_identity,
        source_channel_identity=request.interface_identity,
        adapter_identity=request.adapter_identity,
        request_identity=request.request_identity,
        che_entry_identity="CHE-ENTRY-" + request.request_identity,
        source_act_identity=request.source_act_identity,
        source_act_digest=canonical_che_request_source_act_digest_v1(request),
        order_identity=request.order_identity,
        idempotency_identity=request.idempotency_identity,
        continuation_identity=(
            active_continuation.continuation_identity
            if active_continuation is not None
            else absent
        ),
        continuation_sequence=(
            active_continuation.continuation_sequence
            if active_continuation is not None
            else absent
        ),
        authority_act_identity=(
            authority_act.authority_act_identity if authority_act else absent
        ),
        authority_kind=(authority_act.authority_kind if authority_act else absent),
        authority_requesting_owner_identity=(
            authority_act.expected_owner if authority_act else absent
        ),
        authority_target_identity=(
            authority_act.target_identity if authority_act else absent
        ),
        authority_target_revision=(
            authority_act.target_revision if authority_act else absent
        ),
        authority_payload_digest=(
            authority_act.payload_digest if authority_act else absent
        ),
        authority_result_identity=absent,
        opaque_reference_set_identity=(
            reference_set.reference_set_identity if reference_set else absent
        ),
        ordered_reference_set_digest=(
            reference_set.ordered_reference_set_digest if reference_set else absent
        ),
        opaque_reference_correlations=(
            _canonical_che_reference_correlations_v1(reference_set)
        ),
        producing_owner_identity=(
            transition.producing_owner if transition is not None else absent
        ),
        owner_state_identity=(
            transition.owner_state_identity if transition is not None else absent
        ),
        owner_revision_before=(
            transition.owner_revision_before if transition is not None else absent
        ),
        owner_revision_after=(
            transition.owner_revision_after if transition is not None else absent
        ),
        owner_advancement=(
            transition.advancement_outcome if transition is not None else absent
        ),
        owner_disposition=(
            transition.response_disposition if transition is not None else absent
        ),
        next_act_identity=(
            (transition.next_act_identity or absent) if transition else absent
        ),
        refusal_identity=(
            (transition.refusal_identity or absent) if transition else absent
        ),
        terminal_identity=(
            (transition.terminal_identity or absent) if transition else absent
        ),
        owner_projection_identity=(
            projection.projection_identity if projection is not None else absent
        ),
        failure_identity=(
            failure.failure_identity if failure is not None else absent
        ),
        presentation_identity=(
            presentation.presentation_identity if presentation is not None else absent
        ),
        response_identity=(response.response_identity if response else absent),
        response_digest=(
            canonical_che_response_evidence_digest_v1(response)
            if response is not None
            else absent
        ),
        delivery_record_identity=_canonical_che_delivery_record_identity_v1(
            delivery_record
        ),
        delivery_status=delivery_status,
        duplicate_resolution="ORIGINAL_DELIVERY",
        acknowledgement_state=(
            "UNKNOWN" if response is not None else absent
        ),
        replay_references=replay_references,
        replay_status=(
            CORRELATION_REFERENCE_CREATED
            if replay_references
            else CORRELATION_REFERENCE_NOT_CREATED
        ),
        certification_references=certification_references,
        certification_status=(
            CORRELATION_REFERENCE_CREATED
            if certification_references
            else CORRELATION_REFERENCE_NOT_CREATED
        ),
        evidence_status=evidence_status,
        metadata={},
    )


def _canonical_che_bind_evidence_correlation_v1(
    *,
    request: CanonicalHumanEntryRequestEnvelopeV1,
    delivery_record: dict[str, Any],
    response: CanonicalHumanEntryResponseEnvelopeV1,
    prior_continuation: CanonicalContinuationEnvelopeV1 | None,
    authority_act: CanonicalHumanAuthorityActV1 | None,
    reference_set: CanonicalOpaqueReferenceSetV1 | None,
    delivery_status: str = DELIVERY_RESPONSE_COMMITTED_ACKNOWLEDGEMENT_UNKNOWN,
) -> tuple[
    CanonicalHumanEntryResponseEnvelopeV1,
    CanonicalCHEEvidenceCorrelationV1,
]:
    correlation = _canonical_che_evidence_correlation_v1(
        request=request,
        delivery_record=delivery_record,
        response=response,
        continuation=prior_continuation,
        authority_act=authority_act,
        reference_set=reference_set,
        delivery_status=delivery_status,
        evidence_status=CORRELATION_RECORDED,
    )
    continuation = response.continuation_envelope
    if continuation is not None and continuation != prior_continuation:
        continuation = replace(
            continuation, correlation_identity=correlation.correlation_identity
        )
    bound_response = replace(
        response,
        correlation_identity=correlation.correlation_identity,
        continuation_envelope=continuation,
        owner_projection=None,
        presentation=None,
        common_failure=None,
    )
    rebound = _canonical_che_evidence_correlation_v1(
        request=request,
        delivery_record=delivery_record,
        response=bound_response,
        continuation=prior_continuation,
        authority_act=authority_act,
        reference_set=reference_set,
        delivery_status=delivery_status,
        evidence_status=CORRELATION_RECORDED,
    )
    if rebound.correlation_identity != correlation.correlation_identity:
        raise FailClosedRuntimeError("CHE evidence correlation is unstable")
    return bound_response, rebound


def _canonical_che_delivery_record_hash_v1(record: dict[str, Any]) -> str:
    return replay_hash(
        {key: value for key, value in record.items() if key != "record_hash"}
    )


def _write_canonical_che_delivery_record_v1(
    path: Path, record: dict[str, Any]
) -> None:
    if set(record) != _DELIVERY_RESOLUTION_RECORD_FIELDS:
        raise FailClosedRuntimeError("CHE delivery record structure is invalid")
    serialized = canonical_serialize(record) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_name = ""
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=".che-delivery-",
            suffix=".tmp",
            dir=path.parent,
            text=True,
        )
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(serialized)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except OSError as exc:
        raise FailClosedRuntimeError("CHE delivery record write failed") from exc
    finally:
        if temporary_name and Path(temporary_name).exists():
            Path(temporary_name).unlink()


def _read_canonical_che_delivery_record_v1(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FailClosedRuntimeError("CHE delivery record is unreadable") from exc
    if not isinstance(value, dict):
        raise FailClosedRuntimeError("CHE delivery record structure is invalid")
    if (
        set(value) == _LEGACY_DELIVERY_RESOLUTION_RECORD_FIELDS
        and value.get("record_version")
        == _LEGACY_CANONICAL_CHE_DELIVERY_RESOLUTION_RECORD_VERSION
    ):
        if value.get("record_hash") != _canonical_che_delivery_record_hash_v1(
            value
        ):
            raise FailClosedRuntimeError(
                "CHE delivery record integrity is invalid"
            )
        value = {
            **value,
            "record_version": CANONICAL_CHE_DELIVERY_RESOLUTION_RECORD_VERSION,
            "authority_act_identity": NOT_APPLICABLE,
            "authority_act_digest": NOT_APPLICABLE,
            "evidence_correlation": None,
        }
        value["record_hash"] = _canonical_che_delivery_record_hash_v1(value)
    elif (
        set(value) == _G69_05_WITH_G69_11_CORRELATION_FIELDS
        and value.get("record_version")
        == _LEGACY_CANONICAL_CHE_DELIVERY_RESOLUTION_RECORD_VERSION
    ):
        if value.get("record_hash") != _canonical_che_delivery_record_hash_v1(
            value
        ):
            raise FailClosedRuntimeError(
                "CHE delivery record integrity is invalid"
            )
        value = {
            **value,
            "record_version": CANONICAL_CHE_DELIVERY_RESOLUTION_RECORD_VERSION,
            "authority_act_identity": NOT_APPLICABLE,
            "authority_act_digest": NOT_APPLICABLE,
        }
        value["record_hash"] = _canonical_che_delivery_record_hash_v1(value)
    elif (
        set(value) == _G69_07_DELIVERY_RESOLUTION_RECORD_FIELDS
        and value.get("record_version")
        == _G69_07_CANONICAL_CHE_DELIVERY_RESOLUTION_RECORD_VERSION
    ):
        if value.get("record_hash") != _canonical_che_delivery_record_hash_v1(
            value
        ):
            raise FailClosedRuntimeError(
                "CHE delivery record integrity is invalid"
            )
        value = {
            **value,
            "record_version": CANONICAL_CHE_DELIVERY_RESOLUTION_RECORD_VERSION,
            "evidence_correlation": None,
        }
        value["record_hash"] = _canonical_che_delivery_record_hash_v1(value)
    if set(value) != _DELIVERY_RESOLUTION_RECORD_FIELDS:
        raise FailClosedRuntimeError("CHE delivery record structure is invalid")
    if value["record_version"] != CANONICAL_CHE_DELIVERY_RESOLUTION_RECORD_VERSION:
        raise FailClosedRuntimeError("CHE delivery record version is invalid")
    if value["delivery_state"] not in {
        _DELIVERY_RECORD_OUTCOME_UNKNOWN,
        _DELIVERY_RECORD_ENTERED_NOT_ADVANCED,
        _DELIVERY_RECORD_COMMITTED,
    }:
        raise FailClosedRuntimeError("CHE delivery record state is invalid")
    if not isinstance(value["evidence_references"], list) or any(
        not isinstance(item, str) or not item
        for item in value["evidence_references"]
    ):
        raise FailClosedRuntimeError("CHE delivery evidence references are invalid")
    if value["record_hash"] != _canonical_che_delivery_record_hash_v1(value):
        raise FailClosedRuntimeError("CHE delivery record integrity is invalid")
    correlation_value = value["evidence_correlation"]
    if correlation_value is not None:
        correlation = validate_canonical_che_evidence_correlation_v1(
            correlation_value
        )
        if correlation.delivery_record_identity != (
            _canonical_che_delivery_record_identity_v1(value)
        ):
            raise FailClosedRuntimeError(
                "CHE delivery evidence correlation binding is invalid"
            )
        if value["delivery_state"] == _DELIVERY_RECORD_COMMITTED and (
            correlation.response_identity != value["response_identity"]
        ):
            raise FailClosedRuntimeError(
                "CHE delivery Response correlation binding is invalid"
            )
    if value["delivery_state"] == _DELIVERY_RECORD_COMMITTED:
        if not isinstance(value["serialized_response"], str):
            raise FailClosedRuntimeError("CHE committed delivery response is absent")
        try:
            response_value = json.loads(value["serialized_response"])
        except json.JSONDecodeError as exc:
            raise FailClosedRuntimeError(
                "CHE committed delivery response is invalid"
            ) from exc
        response = validate_canonical_che_response_envelope_v1(response_value)
        response_hash_value = (
            replay_hash(response_value)
            if response_value.get("contract_version")
            == LEGACY_CANONICAL_CHE_RESPONSE_CONTRACT_VERSION
            else replay_hash(response.to_dict())
        )
        if response.response_identity != value["response_identity"] or (
            response_hash_value != value["response_hash"]
        ):
            raise FailClosedRuntimeError(
                "CHE committed delivery response integrity is invalid"
            )
    return value


def _existing_canonical_che_delivery_record_v1(
    request: CanonicalHumanEntryRequestEnvelopeV1,
) -> dict[str, Any] | None:
    path = _canonical_che_delivery_record_path_v1(
        runtime_scope_identity=request.runtime_scope_identity,
        actor_identity=request.actor_identity,
        session_identity=request.session_identity,
        workspace_identity=request.workspace_identity,
        idempotency_identity=request.idempotency_identity,
    )
    return _read_canonical_che_delivery_record_v1(path) if path.is_file() else None


def _assert_canonical_che_authority_act_not_duplicate_v1(
    request: CanonicalHumanEntryRequestEnvelopeV1,
    authority_act: CanonicalHumanAuthorityActV1,
) -> None:
    """Reject reuse of one authority identity before any owner invocation."""

    store = _canonical_che_delivery_store_v1(request.runtime_scope_identity)
    if not store.exists():
        return
    for path in sorted(store.glob("record-*.json")):
        record = _read_canonical_che_delivery_record_v1(path)
        if record["authority_act_identity"] == (
            authority_act.authority_act_identity
        ):
            raise FailClosedRuntimeError("Human Authority Act is duplicate")


def _validate_canonical_che_delivery_request_binding_v1(
    record: dict[str, Any],
    request: CanonicalHumanEntryRequestEnvelopeV1,
    continuation: CanonicalContinuationEnvelopeV1 | None,
) -> None:
    authority_act = canonical_human_authority_act_from_request_v1(request)
    expected = {
        "request_identity": request.request_identity,
        "source_act_digest": canonical_che_request_source_act_digest_v1(request),
        "request_binding_hash": _canonical_che_delivery_request_binding_hash_v1(
            request, continuation
        ),
        "idempotency_identity": request.idempotency_identity,
        "actor_identity": request.actor_identity,
        "session_identity": request.session_identity,
        "workspace_identity": request.workspace_identity,
        "runtime_scope_identity": request.runtime_scope_identity,
        "authority_act_identity": (
            authority_act.authority_act_identity
            if authority_act is not None
            else NOT_APPLICABLE
        ),
        "authority_act_digest": (
            replay_hash(authority_act.to_dict())
            if authority_act is not None
            else NOT_APPLICABLE
        ),
    }
    if any(record[key] != value for key, value in expected.items()):
        raise FailClosedRuntimeError(
            "CHE idempotency identity-content conflict"
        )
    if continuation is not None and record["interaction_identity"] not in {
        continuation.interaction_identity,
        NOT_APPLICABLE,
    }:
        raise FailClosedRuntimeError(
            "CHE idempotency interaction identity conflict"
        )


def _begin_canonical_che_delivery_record_v1(
    request: CanonicalHumanEntryRequestEnvelopeV1,
    continuation: CanonicalContinuationEnvelopeV1 | None,
    *,
    authority_act: CanonicalHumanAuthorityActV1 | None = None,
) -> dict[str, Any]:
    record = {
        "record_version": CANONICAL_CHE_DELIVERY_RESOLUTION_RECORD_VERSION,
        "request_identity": request.request_identity,
        "source_act_digest": canonical_che_request_source_act_digest_v1(request),
        "request_binding_hash": _canonical_che_delivery_request_binding_hash_v1(
            request, continuation
        ),
        "idempotency_identity": request.idempotency_identity,
        "actor_identity": request.actor_identity,
        "session_identity": request.session_identity,
        "workspace_identity": request.workspace_identity,
        "runtime_scope_identity": request.runtime_scope_identity,
        "interaction_identity": (
            continuation.interaction_identity
            if continuation is not None
            else NOT_APPLICABLE
        ),
        "authority_act_identity": (
            authority_act.authority_act_identity
            if authority_act is not None
            else NOT_APPLICABLE
        ),
        "authority_act_digest": (
            replay_hash(authority_act.to_dict())
            if authority_act is not None
            else NOT_APPLICABLE
        ),
        "producing_owner": NOT_APPLICABLE,
        "owner_state_identity": NOT_APPLICABLE,
        "owner_revision_before": NOT_APPLICABLE,
        "owner_revision_after": NOT_APPLICABLE,
        "advancement_outcome": DELIVERY_OUTCOME_UNKNOWN,
        "response_identity": None,
        "serialized_response": None,
        "response_hash": None,
        "delivery_state": _DELIVERY_RECORD_OUTCOME_UNKNOWN,
        "evidence_references": [],
        "evidence_correlation": None,
        "record_hash": "",
    }
    record["record_hash"] = _canonical_che_delivery_record_hash_v1(record)
    path = _canonical_che_delivery_record_path_v1(
        runtime_scope_identity=request.runtime_scope_identity,
        actor_identity=request.actor_identity,
        session_identity=request.session_identity,
        workspace_identity=request.workspace_identity,
        idempotency_identity=request.idempotency_identity,
    )
    if path.exists():
        raise FailClosedRuntimeError("CHE delivery record identity conflicts")
    _write_canonical_che_delivery_record_v1(path, record)
    return record


def _mark_canonical_che_delivery_not_advanced_v1(
    record: dict[str, Any],
    correlation: CanonicalCHEEvidenceCorrelationV1 | None = None,
) -> None:
    updated = dict(record)
    updated["advancement_outcome"] = NOT_ADVANCED
    updated["delivery_state"] = _DELIVERY_RECORD_ENTERED_NOT_ADVANCED
    if correlation is not None:
        updated["evidence_correlation"] = correlation.to_dict()
    updated["record_hash"] = _canonical_che_delivery_record_hash_v1(updated)
    path = _canonical_che_delivery_record_path_v1(
        runtime_scope_identity=updated["runtime_scope_identity"],
        actor_identity=updated["actor_identity"],
        session_identity=updated["session_identity"],
        workspace_identity=updated["workspace_identity"],
        idempotency_identity=updated["idempotency_identity"],
    )
    _write_canonical_che_delivery_record_v1(path, updated)


def _commit_canonical_che_delivery_response_v1(
    record: dict[str, Any],
    response: CanonicalHumanEntryResponseEnvelopeV1,
    correlation: CanonicalCHEEvidenceCorrelationV1,
) -> None:
    canonical_response = validate_canonical_che_response_envelope_v1(response)
    transition = canonical_response.owner_transition
    canonical_correlation = validate_canonical_che_evidence_correlation_v1(
        correlation
    )
    if canonical_response.correlation_identity != (
        canonical_correlation.correlation_identity
    ):
        raise FailClosedRuntimeError(
            "CHE Response evidence correlation binding is invalid"
        )
    serialized_response = canonical_serialize(canonical_response.to_dict())
    updated = dict(record)
    updated.update(
        {
            "interaction_identity": (
                canonical_response.continuation_envelope.interaction_identity
                if canonical_response.continuation_envelope is not None
                else record["interaction_identity"]
            ),
            "producing_owner": transition.producing_owner,
            "owner_state_identity": transition.owner_state_identity,
            "owner_revision_before": transition.owner_revision_before,
            "owner_revision_after": transition.owner_revision_after,
            "advancement_outcome": transition.advancement_outcome,
            "response_identity": canonical_response.response_identity,
            "serialized_response": serialized_response,
            "response_hash": replay_hash(canonical_response.to_dict()),
            "delivery_state": _DELIVERY_RECORD_COMMITTED,
            "evidence_references": list(canonical_response.evidence_references),
            "evidence_correlation": canonical_correlation.to_dict(),
        }
    )
    updated["record_hash"] = _canonical_che_delivery_record_hash_v1(updated)
    path = _canonical_che_delivery_record_path_v1(
        runtime_scope_identity=updated["runtime_scope_identity"],
        actor_identity=updated["actor_identity"],
        session_identity=updated["session_identity"],
        workspace_identity=updated["workspace_identity"],
        idempotency_identity=updated["idempotency_identity"],
    )
    _write_canonical_che_delivery_record_v1(path, updated)
    persist_canonical_che_evidence_correlation_v1(canonical_correlation)


def _response_from_canonical_che_delivery_record_v1(
    record: dict[str, Any],
) -> CanonicalHumanEntryResponseEnvelopeV1:
    validated = _read_canonical_che_delivery_record_v1(
        _canonical_che_delivery_record_path_v1(
            runtime_scope_identity=record["runtime_scope_identity"],
            actor_identity=record["actor_identity"],
            session_identity=record["session_identity"],
            workspace_identity=record["workspace_identity"],
            idempotency_identity=record["idempotency_identity"],
        )
    )
    if validated["delivery_state"] != _DELIVERY_RECORD_COMMITTED:
        raise FailClosedRuntimeError("CHE delivery Response is not committed")
    return CanonicalHumanEntryResponseEnvelopeV1.from_dict(
        json.loads(validated["serialized_response"])
    )


def _resolve_canonical_che_delivery_v1(
    request: CanonicalHumanEntryRequestEnvelopeV1,
    query: CanonicalHumanEntryDeliveryResolutionQueryV1,
) -> CanonicalHumanEntryResponseEnvelopeV1:
    path = _canonical_che_delivery_record_path_v1(
        runtime_scope_identity=request.runtime_scope_identity,
        actor_identity=request.actor_identity,
        session_identity=request.session_identity,
        workspace_identity=request.workspace_identity,
        idempotency_identity=query.target_idempotency_identity,
    )
    if not path.is_file():
        return _canonical_che_delivery_resolution_response_v1(
            request, None, status=DELIVERY_NOT_FOUND
        )
    record = _read_canonical_che_delivery_record_v1(path)
    if (
        record["request_identity"] != query.target_request_identity
        or record["source_act_digest"] != query.target_source_act_digest
        or record["interaction_identity"] != query.target_interaction_identity
    ):
        raise FailClosedRuntimeError("CHE delivery resolution query conflict")
    if record["delivery_state"] == _DELIVERY_RECORD_COMMITTED:
        status = (
            DELIVERY_COMMITTED_NOT_ADVANCED
            if record["advancement_outcome"]
            in {NOT_ADVANCED, REFUSED_ADVANCEMENT}
            else DELIVERY_COMMITTED_RESPONSE_FOUND
        )
    else:
        status = record["delivery_state"]
    return _canonical_che_delivery_resolution_response_v1(
        request, record, status=status
    )


def _canonical_che_delivery_resolution_response_v1(
    request: CanonicalHumanEntryRequestEnvelopeV1,
    record: dict[str, Any] | None,
    *,
    status: str,
) -> CanonicalHumanEntryResponseEnvelopeV1:
    if status not in {
        DELIVERY_NOT_FOUND,
        DELIVERY_OUTCOME_UNKNOWN,
        DELIVERY_ENTERED_NOT_ADVANCED,
        DELIVERY_COMMITTED_RESPONSE_FOUND,
        DELIVERY_COMMITTED_NOT_ADVANCED,
    }:
        raise FailClosedRuntimeError("CHE delivery resolution status is unsupported")
    prior_response = None
    if record is not None and record["delivery_state"] == _DELIVERY_RECORD_COMMITTED:
        prior_response = _response_from_canonical_che_delivery_record_v1(record)
    evidence = tuple(record["evidence_references"]) if record is not None else ()
    replay_references = prior_response.replay_references if prior_response else ()
    certification_references = (
        prior_response.certification_references if prior_response else ()
    )
    if status == DELIVERY_NOT_FOUND:
        advancement = NOT_ADVANCED
        retryability = RETRYABLE
        recovery = RESUBMIT_EXACT_REQUEST
    elif status in {
        DELIVERY_COMMITTED_RESPONSE_FOUND,
        DELIVERY_COMMITTED_NOT_ADVANCED,
    }:
        advancement = record["advancement_outcome"]
        retryability = NOT_RETRYABLE
        recovery = USE_RESOLVED_RESPONSE
    elif status == DELIVERY_ENTERED_NOT_ADVANCED:
        advancement = NOT_ADVANCED
        retryability = NOT_RETRYABLE
        recovery = MANUAL_REVIEW_REQUIRED
    else:
        advancement = DELIVERY_OUTCOME_UNKNOWN
        retryability = NOT_RETRYABLE
        recovery = QUERY_DELIVERY_STATUS
    transition = CanonicalHumanEntryOwnerTransitionV1(
        contract_version=CANONICAL_CHE_OWNER_TRANSITION_CONTRACT_VERSION,
        producing_owner="CANONICAL_HUMAN_ENTRY_TRANSPORT",
        owner_state_identity=(
            record["owner_state_identity"] if record is not None else NOT_APPLICABLE
        ),
        owner_revision_before=(
            record["owner_revision_before"] if record is not None else NOT_APPLICABLE
        ),
        owner_revision_after=(
            record["owner_revision_after"] if record is not None else NOT_APPLICABLE
        ),
        response_disposition=DELIVERY_RESOLUTION_DISPOSITION,
        advancement_outcome=advancement,
        next_act_identity=None,
        next_act_kind=None,
        next_act_target_identity=None,
        next_act_target_digest=None,
        next_act_expected_owner_revision=NOT_APPLICABLE,
        permitted_controls=(),
        payload_constraints={},
        exact_human_act_required=False,
        cancellation_permitted=False,
        interruption_permitted=False,
        refusal_identity=None,
        refusal_type=NOT_APPLICABLE,
        refusal_status=NOT_APPLICABLE,
        terminal_identity=None,
        terminal_type=NOT_APPLICABLE,
        terminal_status=NOT_APPLICABLE,
        retryability=retryability,
        recovery_requirement=recovery,
        delivery_resolution_status=status,
        resolved_response_identity=(
            record["response_identity"] if prior_response is not None else None
        ),
        resolved_response_hash=(
            record["response_hash"] if prior_response is not None else None
        ),
        replay_reference_status=(
            REFERENCE_CREATED if replay_references else REFERENCE_NOT_CREATED
        ),
        certification_reference_status=(
            REFERENCE_CREATED if certification_references else REFERENCE_NOT_CREATED
        ),
    )
    identity_seed = {
        "request_identity": request.request_identity,
        "target_request_identity": (
            record["request_identity"] if record is not None else NOT_APPLICABLE
        ),
        "delivery_resolution_status": status,
        "resolved_response_identity": transition.resolved_response_identity,
    }
    digest = replay_hash(identity_seed).removeprefix("sha256:")
    response = CanonicalHumanEntryResponseEnvelopeV1(
        contract_version=CANONICAL_CHE_RESPONSE_CONTRACT_VERSION,
        response_identity=f"CHE-DELIVERY-RESOLUTION-{digest}",
        request_identity=request.request_identity,
        response_type=INFORMATIONAL_RESPONSE,
        producing_owner=transition.producing_owner,
        owner_status=status,
        advancement_state=advancement,
        presentation_payload=(f"Canonical delivery resolution: {status}",),
        presentation_metadata={
            "content_format": "ORDERED_TEXT_SEGMENTS",
            "language": "und",
            "projection_owner": "CANONICAL_HUMAN_ENTRY_TRANSPORT",
        },
        correlation_identity=f"CHE-DELIVERY-CORRELATION-{digest}",
        evidence_references=evidence,
        replay_references=replay_references,
        certification_references=certification_references,
        owner_transition=transition,
        continuation_envelope=None,
    )
    correlation_record = record or {
        "actor_identity": request.actor_identity,
        "session_identity": request.session_identity,
        "workspace_identity": request.workspace_identity,
        "runtime_scope_identity": request.runtime_scope_identity,
        "idempotency_identity": request.idempotency_identity,
    }
    response, correlation = _canonical_che_bind_evidence_correlation_v1(
        request=request,
        delivery_record=correlation_record,
        response=response,
        prior_continuation=None,
        authority_act=None,
        reference_set=None,
        delivery_status=status,
    )
    persist_canonical_che_evidence_correlation_v1(correlation)
    return response


def _validate_canonical_che_expected_owner_revision_v1(
    request: CanonicalHumanEntryRequestEnvelopeV1,
    continuation: CanonicalContinuationEnvelopeV1 | None,
) -> None:
    if continuation is None:
        return
    workspace_state = latest_platform_core_workspace_state(
        Path(request.runtime_scope_identity) / request.session_identity
    )
    restored = replay_backed_uhi_clarification_state(workspace_state)
    envelope = (
        restored.get("owner_bound_clarification_envelope")
        if isinstance(restored, dict)
        else None
    )
    if not isinstance(envelope, dict):
        raise FailClosedRuntimeError(
            "CHE expected owner revision evidence is unavailable"
        )
    if envelope.get("conversation_identity") != (
        continuation.expected_owner_state_identity
    ):
        raise FailClosedRuntimeError("CHE expected owner state is stale")
    if envelope.get("expected_revision") != continuation.expected_owner_revision:
        raise FailClosedRuntimeError("CHE expected owner revision is stale")


def _canonical_che_authority_kind_for_owner_reply_v1(
    permitted_reply_kind: Any,
) -> str:
    """Project an exact certified owner reply contract to the closed act kind."""

    mapping = {
        "OWNER_BOUND_REPLY": CLARIFICATION_RESPONSE,
        "CONVERSATION_SEMANTIC_INPUT_OR_EXACT_COMMIT_ACT": (
            CLARIFICATION_RESPONSE
        ),
        "EXACT_HUMAN_CANDIDATE_CONFIRMATION_ACT": CONFIRMATION,
        "EXACT_HUMAN_OBJECTIVE_COMMIT_ACT": COMMITMENT,
        BOUNDED_EVIDENCE_REDUCTION_POLICY_AUTHORIZATION: AUTHORIZATION,
    }
    if permitted_reply_kind not in mapping:
        raise FailClosedRuntimeError(
            "CHE owner reply contract has no canonical authority kind"
        )
    return mapping[permitted_reply_kind]


def _persist_profile_a_owner_state_authorization_if_applicable_v1(
    *,
    request: CanonicalHumanEntryRequestEnvelopeV1,
    continuation: CanonicalContinuationEnvelopeV1 | None,
    authority_act: CanonicalHumanAuthorityActV1,
    correlation: CanonicalCHEEvidenceCorrelationV1 | dict[str, Any],
) -> None:
    """Extend only the committed CHE owner-state path for Profile A C1."""

    payload = authority_act.to_dict()["payload"]
    if (
        authority_act.authority_kind != AUTHORIZATION
        or authority_act.authority_scope
        != "BOUNDED_EVIDENCE_REDUCTION_POLICY"
        or not isinstance(payload, dict)
        or payload.get("command")
        != "AUTHORIZE_BOUNDED_EVIDENCE_REDUCTION_POLICY"
    ):
        return
    if continuation is None:
        raise FailClosedRuntimeError(
            "Profile A owner-state authorization requires CHE continuation"
        )
    request_profile_a_owner_state_issuance_v1(
        request=request,
        continuation=continuation,
        authority_act=authority_act,
        correlation=correlation,
    )


def request_profile_a_bounded_evidence_reduction_from_canonical_entry_v1(
    *,
    request_identity: str,
    decision_inputs: dict[str, Any],
) -> dict[str, Any]:
    """Use the one OS-authenticated authority-process decision path."""

    return request_profile_a_bounded_evidence_reduction_decision_v1(
        request_identity=request_identity,
        decision_inputs=decision_inputs,
    )


def _validate_canonical_che_authority_owner_binding_v1(
    request: CanonicalHumanEntryRequestEnvelopeV1,
    continuation: CanonicalContinuationEnvelopeV1,
    authority_act: CanonicalHumanAuthorityActV1,
) -> CanonicalHumanAuthorityActV1:
    """Authenticate act bindings against current owner-issued evidence."""

    workspace_state = latest_platform_core_workspace_state(
        Path(request.runtime_scope_identity) / request.session_identity
    )
    restored = replay_backed_uhi_clarification_state(workspace_state)
    envelope = (
        restored.get("owner_bound_clarification_envelope")
        if isinstance(restored, dict)
        else None
    )
    if not isinstance(envelope, dict):
        raise FailClosedRuntimeError(
            "Human Authority Act owner binding evidence is unavailable"
        )
    for field_name in (
        "clarification_identity",
        "originating_owner",
        "subject_identity",
        "permitted_reply_kind",
    ):
        if not isinstance(envelope.get(field_name), str) or not envelope[field_name]:
            raise FailClosedRuntimeError(
                "Human Authority Act owner binding evidence is invalid"
            )
    if (
        envelope.get("conversation_identity")
        != continuation.expected_owner_state_identity
        or envelope.get("conversation_identity")
        != continuation.conversation_identity
    ):
        raise FailClosedRuntimeError(
            "Human Authority Act owner state binding is invalid"
        )
    expected_revision = envelope.get("expected_revision")
    if not isinstance(expected_revision, int) or isinstance(
        expected_revision, bool
    ):
        raise FailClosedRuntimeError(
            "Human Authority Act owner revision evidence is invalid"
        )
    return bind_canonical_human_authority_act_to_che_v1(
        authority_act,
        request,
        continuation,
        expected_authority_kind=(
            _canonical_che_authority_kind_for_owner_reply_v1(
                envelope["permitted_reply_kind"]
            )
        ),
        expected_target_identity=envelope["clarification_identity"],
        expected_target_revision=expected_revision,
        expected_producing_owner=HUMAN_AUTHORITY_OWNER,
        expected_owner=envelope["originating_owner"],
        expected_authority_scope=envelope["subject_identity"],
    )


def _acquire_canonical_che_continuation_scope_v1(
    request: CanonicalHumanEntryRequestEnvelopeV1,
) -> Path:
    """Serialize one actor/session/workspace continuation transition."""

    store = _canonical_che_continuation_store_v1(request.runtime_scope_identity)
    store.mkdir(parents=True, exist_ok=True)
    digest = replay_hash(
        {
            "actor_identity": request.actor_identity,
            "session_identity": request.session_identity,
            "workspace_identity": request.workspace_identity,
            "runtime_scope_identity": request.runtime_scope_identity,
        }
    ).removeprefix("sha256:")
    lock_path = store / f"scope-{digest}.lock"
    try:
        descriptor = os.open(
            lock_path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
        )
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(request.request_identity + "\n")
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise FailClosedRuntimeError(
            "CHE continuation transition is already in progress"
        ) from exc
    except OSError as exc:
        raise FailClosedRuntimeError(
            "CHE continuation transition could not be claimed"
        ) from exc
    return lock_path


def _release_canonical_che_continuation_scope_v1(lock_path: Path) -> None:
    try:
        lock_path.unlink()
    except OSError as exc:
        raise FailClosedRuntimeError(
            "CHE continuation transition claim could not be released"
        ) from exc


def _prepare_canonical_che_continuation_v1(
    request: CanonicalHumanEntryRequestEnvelopeV1,
    continuation_envelope: CanonicalContinuationEnvelopeV1 | dict[str, Any] | None,
    *,
    authority_act: CanonicalHumanAuthorityActV1 | None = None,
) -> CanonicalContinuationEnvelopeV1 | None:
    """Validate and single-use claim an opaque continuation before owner entry."""

    if continuation_envelope is None:
        active = _active_canonical_che_continuations_v1(request)
        if active:
            raise FailClosedRuntimeError(
                "CHE continuation is required for the existing interaction"
            )
        return None

    continuation = validate_canonical_che_continuation_envelope_v1(
        continuation_envelope
    )
    if continuation.continuation_state == TERMINAL_CONTINUATION:
        raise FailClosedRuntimeError("CHE terminal continuation cannot be resumed")

    path = _canonical_che_continuation_binding_path(
        request.runtime_scope_identity,
        continuation.continuation_identity,
    )
    if not path.is_file():
        raise FailClosedRuntimeError("CHE continuation is unknown")
    record = _read_canonical_che_continuation_binding_v1(path)
    recorded = CanonicalContinuationEnvelopeV1.from_dict(record["envelope"])

    if continuation.session_identity != recorded.session_identity:
        raise FailClosedRuntimeError("CHE continuation session is mismatched")
    if continuation.actor_identity != recorded.actor_identity:
        raise FailClosedRuntimeError("CHE continuation actor is mismatched")
    if continuation.interaction_identity != recorded.interaction_identity:
        raise FailClosedRuntimeError("CHE continuation interaction is mismatched")
    if continuation.workspace_identity != recorded.workspace_identity:
        raise FailClosedRuntimeError("CHE continuation workspace is mismatched")
    if continuation.runtime_scope_identity != recorded.runtime_scope_identity:
        raise FailClosedRuntimeError("CHE continuation runtime scope is mismatched")
    if continuation.conversation_identity != recorded.conversation_identity:
        raise FailClosedRuntimeError("CHE continuation Conversation is mismatched")
    if continuation.continuation_sequence != recorded.continuation_sequence:
        raise FailClosedRuntimeError("CHE continuation sequence is non-monotonic")
    if (
        continuation.previous_response_identity
        != recorded.previous_response_identity
    ):
        raise FailClosedRuntimeError(
            "CHE continuation previous response is invalid"
        )
    if continuation.request_identity != recorded.request_identity:
        raise FailClosedRuntimeError("CHE continuation previous request is invalid")
    if continuation.correlation_identity != recorded.correlation_identity:
        raise FailClosedRuntimeError("CHE continuation correlation is invalid")
    if continuation.to_dict() != recorded.to_dict():
        raise FailClosedRuntimeError("CHE continuation binding is invalid")

    if record["consumption_state"] == _CONTINUATION_CONSUMED:
        if (
            record["consumed_by_request_identity"] == request.request_identity
            and record["consumed_by_idempotency_identity"]
            == request.idempotency_identity
        ):
            raise FailClosedRuntimeError("CHE continuation is a duplicate")
        raise FailClosedRuntimeError("CHE continuation is stale")
    if record["consumption_state"] != _CONTINUATION_AVAILABLE:
        raise FailClosedRuntimeError("CHE continuation binding state is invalid")

    if request.session_identity != continuation.session_identity:
        raise FailClosedRuntimeError("CHE continuation request session is mismatched")
    if request.actor_identity != continuation.actor_identity:
        raise FailClosedRuntimeError("CHE continuation request actor is mismatched")
    if request.workspace_identity != continuation.workspace_identity:
        raise FailClosedRuntimeError("CHE continuation request workspace is mismatched")
    if request.runtime_scope_identity != continuation.runtime_scope_identity:
        raise FailClosedRuntimeError(
            "CHE continuation request runtime scope is mismatched"
        )
    if authority_act is None:
        if request.source_act_identity != continuation.expected_next_act_identity:
            raise FailClosedRuntimeError(
                "CHE continuation next act identity is invalid"
            )
    elif request.source_act_identity != authority_act.authority_act_identity:
        raise FailClosedRuntimeError(
            "Human Authority Act request identity binding is invalid"
        )
    if request.request_identity == continuation.request_identity:
        raise FailClosedRuntimeError("CHE continuation request identity was reused")
    if request.order_identity == continuation.previous_order_identity:
        raise FailClosedRuntimeError("CHE continuation order identity was reused")
    if request.idempotency_identity == continuation.previous_idempotency_identity:
        raise FailClosedRuntimeError(
            "CHE continuation idempotency identity was reused"
        )

    claimed = dict(record)
    claimed["consumption_state"] = _CONTINUATION_CONSUMED
    claimed["consumed_by_request_identity"] = request.request_identity
    claimed["consumed_by_idempotency_identity"] = request.idempotency_identity
    claimed["binding_hash"] = _canonical_che_continuation_binding_hash_v1(
        claimed
    )
    _write_canonical_che_continuation_binding_v1(path, claimed)
    return continuation


def _issue_canonical_che_continuation_v1(
    request: CanonicalHumanEntryRequestEnvelopeV1,
    response: CanonicalHumanEntryResponseEnvelopeV1,
    owner_result: dict[str, Any],
    *,
    prior_continuation: CanonicalContinuationEnvelopeV1 | None,
) -> CanonicalContinuationEnvelopeV1:
    """Issue one opaque next-turn binding without carrying owner state."""

    conversation_identity = _canonical_che_conversation_identity(owner_result)
    transition = response.owner_transition
    if transition.owner_state_identity != conversation_identity:
        raise FailClosedRuntimeError(
            "CHE owner transition state identity is inconsistent"
        )
    if (
        prior_continuation is not None
        and conversation_identity != prior_continuation.conversation_identity
    ):
        raise FailClosedRuntimeError(
            "CHE restored a mismatched constitutional interaction"
        )
    if prior_continuation is None:
        interaction_digest = replay_hash(
            {
                "actor_identity": request.actor_identity,
                "session_identity": request.session_identity,
                "workspace_identity": request.workspace_identity,
                "runtime_scope_identity": request.runtime_scope_identity,
                "request_identity": request.request_identity,
                "conversation_identity": conversation_identity,
            }
        ).removeprefix("sha256:")
        interaction_identity = f"CHE-INTERACTION-{interaction_digest}"
        sequence = 1
    else:
        interaction_identity = prior_continuation.interaction_identity
        sequence = prior_continuation.continuation_sequence + 1

    state = (
        TERMINAL_CONTINUATION
        if response.response_type == TERMINAL_RESPONSE
        else ACTIVE_CONTINUATION
    )
    expected_next_act_identity = (
        transition.terminal_identity
        if state == TERMINAL_CONTINUATION
        else transition.next_act_identity
    )
    if not isinstance(expected_next_act_identity, str):
        raise FailClosedRuntimeError(
            "CHE owner transition does not provide the expected next act"
        )
    identity_seed = {
        "contract_version": CANONICAL_CHE_CONTINUATION_CONTRACT_VERSION,
        "interaction_identity": interaction_identity,
        "conversation_identity": conversation_identity,
        "session_identity": request.session_identity,
        "actor_identity": request.actor_identity,
        "workspace_identity": request.workspace_identity,
        "runtime_scope_identity": request.runtime_scope_identity,
        "request_identity": request.request_identity,
        "previous_response_identity": response.response_identity,
        "previous_order_identity": request.order_identity,
        "previous_idempotency_identity": request.idempotency_identity,
        "continuation_sequence": sequence,
        "expected_next_act_identity": expected_next_act_identity,
        "expected_owner_state_identity": transition.owner_state_identity,
        "expected_owner_revision": transition.owner_revision_after,
        "continuation_state": state,
        "correlation_identity": NOT_APPLICABLE,
    }
    continuation_digest = replay_hash(identity_seed).removeprefix("sha256:")
    continuation = CanonicalContinuationEnvelopeV1(
        contract_version=CANONICAL_CHE_CONTINUATION_CONTRACT_VERSION,
        continuation_identity=f"CHE-CONTINUATION-{continuation_digest}",
        interaction_identity=interaction_identity,
        conversation_identity=conversation_identity,
        session_identity=request.session_identity,
        actor_identity=request.actor_identity,
        workspace_identity=request.workspace_identity,
        runtime_scope_identity=request.runtime_scope_identity,
        request_identity=request.request_identity,
        previous_response_identity=response.response_identity,
        previous_order_identity=request.order_identity,
        previous_idempotency_identity=request.idempotency_identity,
        continuation_sequence=sequence,
        expected_next_act_identity=expected_next_act_identity,
        expected_owner_state_identity=transition.owner_state_identity,
        expected_owner_revision=transition.owner_revision_after,
        continuation_state=state,
        correlation_identity=NOT_APPLICABLE,
        metadata={},
    )
    return continuation


def _persist_canonical_che_continuation_v1(
    request: CanonicalHumanEntryRequestEnvelopeV1,
    continuation: CanonicalContinuationEnvelopeV1,
) -> None:
    record = {
        "binding_version": CANONICAL_CHE_CONTINUATION_BINDING_VERSION,
        "envelope": continuation.to_dict(),
        "interface_identity": request.interface_identity,
        "adapter_identity": request.adapter_identity,
        "workspace_identity": request.workspace_identity,
        "runtime_scope_identity": request.runtime_scope_identity,
        "consumption_state": _CONTINUATION_AVAILABLE,
        "consumed_by_request_identity": None,
        "consumed_by_idempotency_identity": None,
        "binding_hash": "",
    }
    record["binding_hash"] = _canonical_che_continuation_binding_hash_v1(record)
    path = _canonical_che_continuation_binding_path(
        request.runtime_scope_identity,
        continuation.continuation_identity,
    )
    if path.exists():
        existing = _read_canonical_che_continuation_binding_v1(path)
        if existing != record:
            raise FailClosedRuntimeError("CHE continuation identity conflicts")
    else:
        _write_canonical_che_continuation_binding_v1(path, record)


def _canonical_che_conversation_identity(owner_result: dict[str, Any]) -> str:
    identities: set[str] = set()

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "conversation_identity" and isinstance(item, str) and item:
                    identities.add(item)
                else:
                    visit(item)
        elif isinstance(value, (list, tuple)):
            for item in value:
                visit(item)

    visit(owner_result)
    if len(identities) != 1:
        raise FailClosedRuntimeError(
            "CHE owner response does not identify one Conversation"
        )
    return next(iter(identities))


def _active_canonical_che_continuations_v1(
    request: CanonicalHumanEntryRequestEnvelopeV1,
) -> list[CanonicalContinuationEnvelopeV1]:
    store = _canonical_che_continuation_store_v1(request.runtime_scope_identity)
    if not store.exists():
        return []
    active: list[CanonicalContinuationEnvelopeV1] = []
    for path in sorted(store.glob("binding-*.json")):
        record = _read_canonical_che_continuation_binding_v1(path)
        if record["consumption_state"] != _CONTINUATION_AVAILABLE:
            continue
        continuation = CanonicalContinuationEnvelopeV1.from_dict(record["envelope"])
        if continuation.continuation_state != ACTIVE_CONTINUATION:
            continue
        if (
            continuation.session_identity == request.session_identity
            and continuation.actor_identity == request.actor_identity
            and continuation.workspace_identity == request.workspace_identity
            and continuation.runtime_scope_identity == request.runtime_scope_identity
        ):
            active.append(continuation)
    return active


def _canonical_che_continuation_store_v1(runtime_scope_identity: str) -> Path:
    return Path(runtime_scope_identity) / "canonical_human_entry_continuations_v1"


def _canonical_che_continuation_binding_path(
    runtime_scope_identity: str,
    continuation_identity: str,
) -> Path:
    digest = replay_hash(
        {"continuation_identity": continuation_identity}
    ).removeprefix("sha256:")
    return _canonical_che_continuation_store_v1(runtime_scope_identity) / (
        f"binding-{digest}.json"
    )


def _canonical_che_continuation_binding_hash_v1(record: dict[str, Any]) -> str:
    content = {key: value for key, value in record.items() if key != "binding_hash"}
    return replay_hash(content)


def _read_canonical_che_continuation_binding_v1(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FailClosedRuntimeError("CHE continuation binding is unreadable") from exc
    if not isinstance(value, dict) or set(value) != _CONTINUATION_BINDING_FIELDS:
        raise FailClosedRuntimeError("CHE continuation binding structure is invalid")
    if value["binding_version"] != CANONICAL_CHE_CONTINUATION_BINDING_VERSION:
        raise FailClosedRuntimeError("CHE continuation binding version is invalid")
    if value["consumption_state"] not in {
        _CONTINUATION_AVAILABLE,
        _CONTINUATION_CONSUMED,
    }:
        raise FailClosedRuntimeError("CHE continuation binding state is invalid")
    CanonicalContinuationEnvelopeV1.from_dict(value["envelope"])
    if value["binding_hash"] != _canonical_che_continuation_binding_hash_v1(value):
        raise FailClosedRuntimeError("CHE continuation binding integrity is invalid")
    return value


def _write_canonical_che_continuation_binding_v1(
    path: Path,
    record: dict[str, Any],
) -> None:
    if set(record) != _CONTINUATION_BINDING_FIELDS:
        raise FailClosedRuntimeError("CHE continuation binding structure is invalid")
    serialized = canonical_serialize(record) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_name = ""
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=".che-continuation-",
            suffix=".tmp",
            dir=path.parent,
            text=True,
        )
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(serialized)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except OSError as exc:
        raise FailClosedRuntimeError("CHE continuation binding write failed") from exc
    finally:
        if temporary_name and Path(temporary_name).exists():
            Path(temporary_name).unlink()


def _legacy_canonical_che_request_envelope_v1(
    *,
    interface_name: str | None,
    session_id: str | None,
    human_requests: list[str] | None,
    created_at: str | None,
    runtime_root: str | Path | None,
    workspace: str | Path | None,
    presentation: dict[str, Any] | None,
    actor_identity: str,
) -> CanonicalHumanEntryRequestEnvelopeV1:
    """Translate only legacy transport fields at the CHE compatibility edge."""

    interface = _require_string(interface_name, "interface_name")
    session = _require_string(session_id, "session_id")
    requests = _require_legacy_human_requests(human_requests)
    created = _require_string(created_at, "created_at")
    root = str(_require_legacy_path(runtime_root, "runtime_root"))
    workspace_text = str(_require_legacy_path(workspace, "workspace"))
    adapter = None
    if isinstance(presentation, dict):
        candidate = presentation.get("clia_adapter_identity")
        if isinstance(candidate, str) and candidate.strip():
            adapter = candidate
    adapter_identity = adapter or f"LEGACY-COMPATIBILITY::{interface}"
    source_payload: Any = requests[0] if len(requests) == 1 else list(requests)
    identity_seed = {
        "interface_identity": interface,
        "adapter_identity": adapter_identity,
        "actor_identity": actor_identity,
        "session_identity": session,
        "workspace_identity": workspace_text,
        "runtime_scope_identity": root,
        "source_payload": source_payload,
        "created_at": created,
    }
    digest = replay_hash(identity_seed).removeprefix("sha256:")
    return CanonicalHumanEntryRequestEnvelopeV1(
        contract_version=CANONICAL_CHE_REQUEST_CONTRACT_VERSION,
        interface_identity=interface,
        adapter_identity=adapter_identity,
        actor_identity=_require_string(actor_identity, "g31_human_actor_id"),
        actor_class=HUMAN_ACTOR,
        session_identity=session,
        workspace_identity=workspace_text,
        runtime_scope_identity=root,
        request_identity=f"CHE-LEGACY-REQUEST-{digest}",
        source_act_identity=f"CHE-LEGACY-SOURCE-ACT-{digest}",
        order_identity=f"CHE-LEGACY-ORDER-{digest}",
        idempotency_identity=f"CHE-LEGACY-IDEMPOTENCY-{digest}",
        source_payload=source_payload,
        source_encoding="UTF-8",
        source_modality="TEXT" if len(requests) == 1 else "TRANSPORT_COLLECTION",
        declared_capabilities=("LEGACY_ARGUMENT_TRANSLATION",),
        metadata={"transport_compatibility_mode": "LEGACY_CHE_ARGUMENTS"},
        created_at=created,
    )


def _require_legacy_human_requests(value: Any) -> list[str]:
    if not isinstance(value, list):
        raise ValueError("human_requests must be a list")
    return value


def _require_legacy_path(value: Any, field_name: str) -> str | Path:
    if not isinstance(value, (str, Path)):
        raise ValueError(f"{field_name} is required")
    return value


def _canonical_che_source_text(
    request: CanonicalHumanEntryRequestEnvelopeV1,
) -> str:
    source_payload = request.to_dict()["source_payload"]
    return (
        source_payload
        if isinstance(source_payload, str)
        else canonical_serialize(source_payload)
    )


def _canonical_che_authority_payload_text_v1(
    request: CanonicalHumanEntryRequestEnvelopeV1,
    authority_act: CanonicalHumanAuthorityActV1 | None,
    reference_set: CanonicalOpaqueReferenceSetV1 | None = None,
) -> str:
    """Forward the exact act payload through the temporary owner adapter."""

    if authority_act is None:
        if reference_set is not None:
            payload = canonical_opaque_reference_source_payload_from_request_v1(
                request
            )
            return (
                payload
                if isinstance(payload, str)
                else canonical_serialize(payload)
            )
        return _canonical_che_source_text(request)
    payload = authority_act.to_dict()["payload"]
    return payload if isinstance(payload, str) else canonical_serialize(payload)


def _canonical_che_reference_projection_v1(
    request: CanonicalHumanEntryRequestEnvelopeV1,
    reference_set: CanonicalOpaqueReferenceSetV1,
) -> dict[str, Any]:
    """Project validated identity/order/status facts without referenced content."""

    return {
        "contract_version": reference_set.contract_version,
        "request_identity": request.request_identity,
        "source_act_identity": reference_set.source_act_identity,
        "order_identity": reference_set.order_identity,
        "interaction_identity": reference_set.interaction_identity,
        "reference_set_identity": reference_set.reference_set_identity,
        "ordered_reference_set_digest": (
            reference_set.ordered_reference_set_digest
        ),
        "ordered_reference_identities": [
            reference.reference_identity
            for reference in reference_set.references
        ],
        "ordered_positions": [
            reference.ordered_position
            for reference in reference_set.references
        ],
        "availability_statuses": [
            reference.availability_status
            for reference in reference_set.references
        ],
        "validation_owner_identities": [
            reference.validation_owner_identity
            for reference in reference_set.references
        ],
        "validation_evidence_identities": [
            reference.validation_evidence_identity
            for reference in reference_set.references
        ],
        "validation_evidence_digests": [
            reference.validation_evidence_digest
            for reference in reference_set.references
        ],
        "retry_of_source_act_identity": (
            reference_set.retry_of_source_act_identity
        ),
        "retry_of_order_identity": reference_set.retry_of_order_identity,
        "retry_of_reference_set_digest": (
            reference_set.retry_of_reference_set_digest
        ),
    }


def _assert_canonical_che_reference_retry_lineage_v1(
    request: CanonicalHumanEntryRequestEnvelopeV1,
    reference_set: CanonicalOpaqueReferenceSetV1,
) -> None:
    """Require exact lineage for a corrected set and prohibit silent overwrite."""

    store = _canonical_che_delivery_store_v1(request.runtime_scope_identity)
    if not store.exists():
        if reference_set.retry_of_reference_set_digest is not None:
            raise FailClosedRuntimeError(
                "opaque Reference retry lineage has no prior rejection"
            )
        return
    prior_projections: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for path in sorted(store.glob("record-*.json")):
        record = _read_canonical_che_delivery_record_v1(path)
        if record["delivery_state"] != _DELIVERY_RECORD_COMMITTED:
            continue
        response = _response_from_canonical_che_delivery_record_v1(record)
        metadata = response.to_dict()["presentation_metadata"]
        projection = metadata.get("opaque_reference_validation")
        if not isinstance(projection, dict):
            continue
        statuses = projection.get("availability_statuses")
        if (
            not isinstance(statuses, list)
            or not statuses
            or any(not isinstance(status, str) for status in statuses)
        ):
            raise FailClosedRuntimeError(
                "committed opaque Reference projection is malformed"
            )
        if (
            record["actor_identity"] == request.actor_identity
            and record["session_identity"] == request.session_identity
            and record["workspace_identity"] == request.workspace_identity
        ):
            prior_projections.append((record, projection))

    same_digest_rejection = any(
        projection.get("ordered_reference_set_digest")
        == reference_set.ordered_reference_set_digest
        and any(
            status != REFERENCE_AVAILABLE
            for status in projection["availability_statuses"]
        )
        for _, projection in prior_projections
    )
    if (
        same_digest_rejection
        and reference_set.retry_of_reference_set_digest is None
    ):
        raise FailClosedRuntimeError(
            "rejected opaque Reference set requires explicit corrected retry lineage"
        )

    if reference_set.retry_of_reference_set_digest is None:
        return
    matching = [
        (record, projection)
        for record, projection in prior_projections
        if projection.get("source_act_identity")
        == reference_set.retry_of_source_act_identity
        and projection.get("order_identity")
        == reference_set.retry_of_order_identity
        and projection.get("ordered_reference_set_digest")
        == reference_set.retry_of_reference_set_digest
    ]
    if len(matching) != 1:
        raise FailClosedRuntimeError(
            "opaque Reference retry lineage is absent or ambiguous"
        )
    prior_record, prior_projection = matching[0]
    if prior_record["interaction_identity"] != reference_set.interaction_identity:
        raise FailClosedRuntimeError(
            "opaque Reference retry interaction lineage is invalid"
        )
    statuses = prior_projection.get("availability_statuses")
    if not isinstance(statuses, list) or not any(
        status != REFERENCE_AVAILABLE for status in statuses
    ):
        raise FailClosedRuntimeError(
            "opaque Reference retry must target a non-advancing rejection"
        )


def _canonical_che_reference_rejection_response_v1(
    request: CanonicalHumanEntryRequestEnvelopeV1,
    reference_set: CanonicalOpaqueReferenceSetV1,
    failed_reference: Any,
    continuation: CanonicalContinuationEnvelopeV1 | None,
) -> CanonicalHumanEntryResponseEnvelopeV1:
    projection = _canonical_che_reference_projection_v1(
        request, reference_set
    )
    transition = CanonicalHumanEntryOwnerTransitionV1(
        contract_version=CANONICAL_CHE_OWNER_TRANSITION_CONTRACT_VERSION,
        producing_owner=failed_reference.validation_owner_identity,
        owner_state_identity=(
            continuation.expected_owner_state_identity
            if continuation is not None
            else NOT_APPLICABLE
        ),
        owner_revision_before=(
            continuation.expected_owner_revision
            if continuation is not None
            else NOT_APPLICABLE
        ),
        owner_revision_after=(
            continuation.expected_owner_revision
            if continuation is not None
            else NOT_APPLICABLE
        ),
        response_disposition=INFORMATIONAL_DISPOSITION,
        advancement_outcome=NOT_ADVANCED,
        next_act_identity=None,
        next_act_kind=None,
        next_act_target_identity=None,
        next_act_target_digest=None,
        next_act_expected_owner_revision=NOT_APPLICABLE,
        permitted_controls=(),
        payload_constraints={
            "failed_reference_identity": failed_reference.reference_identity,
            "availability_status": failed_reference.availability_status,
            "retryability": failed_reference.retryability,
            "correction_requirement": failed_reference.correction_requirement,
            "new_source_act_order_and_reference_set_required": (
                failed_reference.retryability == RETRYABLE
            ),
        },
        exact_human_act_required=False,
        cancellation_permitted=False,
        interruption_permitted=False,
        refusal_identity=None,
        refusal_type=NOT_APPLICABLE,
        refusal_status=NOT_APPLICABLE,
        terminal_identity=None,
        terminal_type=NOT_APPLICABLE,
        terminal_status=NOT_APPLICABLE,
        retryability=failed_reference.retryability,
        recovery_requirement=(
            RESUBMIT_PERMITTED_CONTROL
            if failed_reference.retryability == RETRYABLE
            else MANUAL_REVIEW_REQUIRED
        ),
        delivery_resolution_status=DELIVERY_NOT_APPLICABLE,
        resolved_response_identity=None,
        resolved_response_hash=None,
        replay_reference_status=REFERENCE_NOT_APPLICABLE,
        certification_reference_status=REFERENCE_NOT_APPLICABLE,
    )
    seed = {
        "request_identity": request.request_identity,
        "projection": projection,
        "failed_reference_identity": failed_reference.reference_identity,
        "transition": transition.to_dict(),
    }
    digest = replay_hash(seed).removeprefix("sha256:")
    return CanonicalHumanEntryResponseEnvelopeV1(
        contract_version=CANONICAL_CHE_RESPONSE_CONTRACT_VERSION,
        response_identity=f"CHE-OPAQUE-REFERENCE-RESPONSE-{digest}",
        request_identity=request.request_identity,
        response_type=INFORMATIONAL_RESPONSE,
        producing_owner=failed_reference.validation_owner_identity,
        owner_status=(
            "OPAQUE_REFERENCE_" + failed_reference.availability_status
        ),
        advancement_state=NOT_ADVANCED,
        presentation_payload=(
            "Opaque Reference validation did not advance the owner.",
            "Reference: " + failed_reference.reference_identity,
            "Availability: " + failed_reference.availability_status,
            "Correction: " + failed_reference.correction_requirement,
        ),
        presentation_metadata={
            "content_format": "ORDERED_TEXT_SEGMENTS",
            "language": "und",
            "projection_owner": "CANONICAL_HUMAN_ENTRY_TRANSPORT",
            "opaque_reference_validation": projection,
        },
        correlation_identity=f"CHE-OPAQUE-REFERENCE-CORRELATION-{digest}",
        evidence_references=(
            failed_reference.validation_evidence_identity,
            failed_reference.validation_evidence_digest,
        ),
        replay_references=(),
        certification_references=(),
        owner_transition=transition,
        continuation_envelope=continuation,
    )


def _canonical_che_bind_reference_projection_v1(
    request: CanonicalHumanEntryRequestEnvelopeV1,
    response: CanonicalHumanEntryResponseEnvelopeV1,
    reference_set: CanonicalOpaqueReferenceSetV1,
) -> CanonicalHumanEntryResponseEnvelopeV1:
    projection = _canonical_che_reference_projection_v1(
        request, reference_set
    )
    metadata = response.to_dict()["presentation_metadata"]
    metadata["opaque_reference_validation"] = projection
    reference_evidence: list[str] = list(response.evidence_references)
    for reference in reference_set.references:
        reference_evidence.extend(
            (
                reference.validation_evidence_identity,
                reference.validation_evidence_digest,
            )
        )
    return replace(
        response,
        presentation_metadata=metadata,
        evidence_references=tuple(dict.fromkeys(reference_evidence)),
        owner_projection=None,
        presentation=None,
        common_failure=None,
    )


def _canonical_che_response_from_owner_result(
    request: CanonicalHumanEntryRequestEnvelopeV1,
    owner_result: dict[str, Any],
    *,
    prior_continuation: CanonicalContinuationEnvelopeV1 | None,
    strict_owner_projection: bool,
) -> CanonicalHumanEntryResponseEnvelopeV1:
    """Project one owner result without exposing owner-internal structures."""

    evidence_references, replay_references, certification_references = (
        _canonical_che_owner_references(owner_result)
    )
    if strict_owner_projection:
        transition, owner_status = _canonical_che_conversation_owner_projection_v1(
            request,
            owner_result,
            prior_continuation=prior_continuation,
            replay_references=replay_references,
            certification_references=certification_references,
        )
    else:
        owner_status = _canonical_che_owner_status(owner_result)
        transition = CanonicalHumanEntryOwnerTransitionV1(
            contract_version=CANONICAL_CHE_OWNER_TRANSITION_CONTRACT_VERSION,
            producing_owner="LEGACY_CHE_BOUNDARY_COMPATIBILITY",
            owner_state_identity=NOT_APPLICABLE,
            owner_revision_before=NOT_APPLICABLE,
            owner_revision_after=NOT_APPLICABLE,
            response_disposition=INFORMATIONAL_DISPOSITION,
            advancement_outcome=NOT_ADVANCED,
            next_act_identity=None,
            next_act_kind=None,
            next_act_target_identity=None,
            next_act_target_digest=None,
            next_act_expected_owner_revision=NOT_APPLICABLE,
            permitted_controls=(),
            payload_constraints={},
            exact_human_act_required=False,
            cancellation_permitted=False,
            interruption_permitted=False,
            refusal_identity=None,
            refusal_type=NOT_APPLICABLE,
            refusal_status=NOT_APPLICABLE,
            terminal_identity=None,
            terminal_type=NOT_APPLICABLE,
            terminal_status=NOT_APPLICABLE,
            retryability=NOT_APPLICABLE,
            recovery_requirement=NOT_APPLICABLE,
            delivery_resolution_status=DELIVERY_NOT_APPLICABLE,
            resolved_response_identity=None,
            resolved_response_hash=None,
            replay_reference_status=(
                REFERENCE_CREATED if replay_references else REFERENCE_NOT_APPLICABLE
            ),
            certification_reference_status=(
                REFERENCE_CREATED
                if certification_references
                else REFERENCE_NOT_APPLICABLE
            ),
        )
    presentations = _canonical_che_presentations(owner_result, owner_status)
    correlation_seed = {
        "contract_version": CANONICAL_CHE_RESPONSE_CONTRACT_VERSION,
        "request_identity": request.request_identity,
        "source_act_identity": request.source_act_identity,
        "order_identity": request.order_identity,
        "idempotency_identity": request.idempotency_identity,
        "owner_status": owner_status,
        "presentation_payload": presentations,
        "evidence_references": evidence_references,
        "replay_references": replay_references,
        "certification_references": certification_references,
        "owner_transition": transition.to_dict(),
    }
    correlation_digest = replay_hash(correlation_seed).removeprefix("sha256:")
    response_identity = f"CHE-RESPONSE-{correlation_digest}"
    correlation_identity = (
        f"CHE-CORRELATION-{request.request_identity}-{correlation_digest[:16]}"
    )
    response_type = {
        PENDING_DISPOSITION: PENDING_RESPONSE,
        INFORMATIONAL_DISPOSITION: INFORMATIONAL_RESPONSE,
        REFUSED_DISPOSITION: REFUSAL_RESPONSE,
        TERMINAL_DISPOSITION: TERMINAL_RESPONSE,
    }[transition.response_disposition]
    return CanonicalHumanEntryResponseEnvelopeV1(
        contract_version=CANONICAL_CHE_RESPONSE_CONTRACT_VERSION,
        response_identity=response_identity,
        request_identity=request.request_identity,
        response_type=response_type,
        producing_owner=transition.producing_owner,
        owner_status=owner_status,
        advancement_state=transition.advancement_outcome,
        presentation_payload=presentations,
        presentation_metadata={
            "content_format": "ORDERED_TEXT_SEGMENTS",
            "language": "und",
            "projection_owner": "CANONICAL_HUMAN_ENTRY_TRANSPORT",
        },
        correlation_identity=correlation_identity,
        evidence_references=evidence_references,
        replay_references=replay_references,
        certification_references=certification_references,
        owner_transition=transition,
    )


def _canonical_che_conversation_owner_projection_v1(
    request: CanonicalHumanEntryRequestEnvelopeV1,
    owner_result: dict[str, Any],
    *,
    prior_continuation: CanonicalContinuationEnvelopeV1 | None,
    replay_references: tuple[str, ...],
    certification_references: tuple[str, ...],
) -> tuple[CanonicalHumanEntryOwnerTransitionV1, str]:
    """Project only authenticated G66/Project Services owner result shapes."""

    capture = owner_result.get("production_conversation_binding")
    if not isinstance(capture, dict):
        raise FailClosedRuntimeError(
            "CHE owner result has no supported Conversation projection"
        )
    state = capture.get("conversation_state")
    if not isinstance(state, dict):
        raise FailClosedRuntimeError(
            "CHE Conversation owner state projection is malformed"
        )
    conversation_identity = capture.get("conversation_identity")
    revision_after = state.get("revision")
    if not isinstance(conversation_identity, str) or not conversation_identity:
        raise FailClosedRuntimeError("CHE Conversation identity is absent")
    if (
        not isinstance(revision_after, int)
        or isinstance(revision_after, bool)
        or revision_after < 0
    ):
        raise FailClosedRuntimeError("CHE Conversation revision is invalid")
    revision_before = (
        prior_continuation.expected_owner_revision
        if prior_continuation is not None
        else 0
    )
    if not isinstance(revision_before, int) or revision_after < revision_before:
        raise FailClosedRuntimeError("CHE Conversation revision regressed")
    if prior_continuation is not None and (
        prior_continuation.expected_owner_state_identity != conversation_identity
    ):
        raise FailClosedRuntimeError("CHE Conversation state identity is stale")

    clarification = owner_result.get("owner_bound_clarification_envelope")
    if isinstance(clarification, dict):
        return _canonical_che_pending_or_refused_conversation_projection_v1(
            request=request,
            capture=capture,
            clarification=clarification,
            conversation_identity=conversation_identity,
            revision_before=revision_before,
            revision_after=revision_after,
            prior_continuation=prior_continuation,
            replay_references=replay_references,
            certification_references=certification_references,
        )

    context = owner_result.get("platform_core_project_services_context")
    experience = (
        context.get("human_conversation_experience")
        if isinstance(context, dict)
        else None
    )
    read_only_result = owner_result.get("governed_read_only_work_result")
    if isinstance(experience, dict) and (
        experience.get("response_mode") == "READ_ONLY_RESULT"
        or isinstance(read_only_result, dict)
    ):
        terminal_digest = replay_hash(
            {
                "request_identity": request.request_identity,
                "conversation_identity": conversation_identity,
                "revision_after": revision_after,
                "response_mode": experience.get("response_mode"),
                "read_only_result_hash": (
                    read_only_result.get("artifact_hash")
                    if isinstance(read_only_result, dict)
                    else None
                ),
            }
        ).removeprefix("sha256:")
        transition = CanonicalHumanEntryOwnerTransitionV1(
            contract_version=CANONICAL_CHE_OWNER_TRANSITION_CONTRACT_VERSION,
            producing_owner="PLATFORM_CORE_PROJECT_SERVICES",
            owner_state_identity=conversation_identity,
            owner_revision_before=revision_before,
            owner_revision_after=revision_after,
            response_disposition=TERMINAL_DISPOSITION,
            advancement_outcome=TERMINAL_ADVANCEMENT,
            next_act_identity=None,
            next_act_kind=None,
            next_act_target_identity=None,
            next_act_target_digest=None,
            next_act_expected_owner_revision=NOT_APPLICABLE,
            permitted_controls=(),
            payload_constraints={},
            exact_human_act_required=False,
            cancellation_permitted=False,
            interruption_permitted=False,
            refusal_identity=None,
            refusal_type=NOT_APPLICABLE,
            refusal_status=NOT_APPLICABLE,
            terminal_identity=f"CHE-TERMINAL-{terminal_digest}",
            terminal_type="READ_ONLY_RESULT_COMPLETE",
            terminal_status="TERMINAL_COMPLETE",
            retryability=NOT_RETRYABLE,
            recovery_requirement=NO_RECOVERY_REQUIRED,
            delivery_resolution_status=DELIVERY_NOT_APPLICABLE,
            resolved_response_identity=None,
            resolved_response_hash=None,
            replay_reference_status=(
                REFERENCE_CREATED if replay_references else REFERENCE_NOT_CREATED
            ),
            certification_reference_status=(
                REFERENCE_CREATED
                if certification_references
                else REFERENCE_NOT_CREATED
            ),
        )
        return transition, "READ_ONLY_RESULT_COMPLETE"
    raise FailClosedRuntimeError("CHE owner result shape is unsupported")


def _canonical_che_pending_or_refused_conversation_projection_v1(
    *,
    request: CanonicalHumanEntryRequestEnvelopeV1,
    capture: dict[str, Any],
    clarification: dict[str, Any],
    conversation_identity: str,
    revision_before: int,
    revision_after: int,
    prior_continuation: CanonicalContinuationEnvelopeV1 | None,
    replay_references: tuple[str, ...],
    certification_references: tuple[str, ...],
) -> tuple[CanonicalHumanEntryOwnerTransitionV1, str]:
    required = clarification.get("required_field_or_evidence_codes")
    if (
        clarification.get("conversation_identity") != conversation_identity
        or clarification.get("expected_revision") != revision_after
        or not isinstance(clarification.get("clarification_identity"), str)
        or not isinstance(clarification.get("originating_owner"), str)
        or not isinstance(clarification.get("permitted_reply_kind"), str)
        or not isinstance(clarification.get("subject_identity"), str)
        or not isinstance(clarification.get("originating_artifact_hash"), str)
        or not isinstance(clarification.get("reason_code"), str)
        or not isinstance(required, list)
        or not required
        or any(not isinstance(item, str) or not item for item in required)
    ):
        raise FailClosedRuntimeError(
            "CHE owner-bound next-act projection is malformed"
        )
    advanced = revision_after > revision_before
    refused = prior_continuation is not None and not advanced
    refusal_identity = None
    if refused:
        refusal_identity = "CHE-REFUSAL-" + replay_hash(
            {
                "request_identity": request.request_identity,
                "conversation_identity": conversation_identity,
                "revision": revision_after,
                "clarification_identity": clarification["clarification_identity"],
            }
        ).removeprefix("sha256:")
    transition = CanonicalHumanEntryOwnerTransitionV1(
        contract_version=CANONICAL_CHE_OWNER_TRANSITION_CONTRACT_VERSION,
        producing_owner=clarification["originating_owner"],
        owner_state_identity=conversation_identity,
        owner_revision_before=revision_before,
        owner_revision_after=revision_after,
        response_disposition=(
            REFUSED_DISPOSITION if refused else PENDING_DISPOSITION
        ),
        advancement_outcome=(
            REFUSED_ADVANCEMENT if refused else ADVANCED
        ),
        next_act_identity=clarification["clarification_identity"],
        next_act_kind=clarification["permitted_reply_kind"],
        next_act_target_identity=clarification["subject_identity"],
        next_act_target_digest=clarification["originating_artifact_hash"],
        next_act_expected_owner_revision=revision_after,
        permitted_controls=tuple(required),
        payload_constraints={
            "permitted_reply_kind": clarification["permitted_reply_kind"],
            "required_control_count": len(required),
            "canonical_authority_act_binding": {
                "authority_kind": (
                    _canonical_che_authority_kind_for_owner_reply_v1(
                        clarification["permitted_reply_kind"]
                    )
                ),
                "target_identity": clarification["clarification_identity"],
                "target_revision": revision_after,
                "producing_owner": HUMAN_AUTHORITY_OWNER,
                "expected_owner": clarification["originating_owner"],
                "authority_scope": clarification["subject_identity"],
            },
        },
        exact_human_act_required=True,
        cancellation_permitted=False,
        interruption_permitted=False,
        refusal_identity=refusal_identity,
        refusal_type="OWNER_INPUT_NOT_ADMITTED" if refused else NOT_APPLICABLE,
        refusal_status="STABLE_REFUSAL" if refused else NOT_APPLICABLE,
        terminal_identity=None,
        terminal_type=NOT_APPLICABLE,
        terminal_status=NOT_APPLICABLE,
        retryability=RETRYABLE if refused else NOT_APPLICABLE,
        recovery_requirement=(
            RESUBMIT_PERMITTED_CONTROL if refused else NOT_APPLICABLE
        ),
        delivery_resolution_status=DELIVERY_NOT_APPLICABLE,
        resolved_response_identity=None,
        resolved_response_hash=None,
        replay_reference_status=(
            REFERENCE_CREATED if replay_references else REFERENCE_NOT_CREATED
        ),
        certification_reference_status=(
            REFERENCE_CREATED
            if certification_references
            else REFERENCE_NOT_CREATED
        ),
    )
    return transition, clarification["reason_code"]


def _canonical_che_owner_status(owner_result: dict[str, Any]) -> str:
    for field_name in (
        "canonical_runtime_entry_status",
        "runtime_binding_status",
        "canonical_condensation_entry_status",
        "g31_semantic_validation_status",
    ):
        value = owner_result.get(field_name)
        if isinstance(value, str) and value.strip():
            return value
    return "OWNER_RESPONSE_AVAILABLE"


def _canonical_che_presentations(
    owner_result: dict[str, Any], owner_status: str
) -> tuple[str, ...]:
    presentations: list[str] = []
    g31_presentations = owner_result.get("g31_canonical_presentations")
    if isinstance(g31_presentations, list):
        presentations.extend(
            item for item in g31_presentations if isinstance(item, str) and item
        )
    context = owner_result.get("platform_core_project_services_context")
    if isinstance(context, dict):
        conversation = context.get("human_conversation_experience")
        if isinstance(conversation, dict):
            for field_name in ("user_headline", "user_explanation"):
                value = conversation.get(field_name)
                if isinstance(value, str) and value:
                    presentations.append(value)
            questions = conversation.get("clarification_questions")
            if isinstance(questions, list):
                presentations.extend(
                    item for item in questions if isinstance(item, str) and item
                )
    completion = owner_result.get("human_visible_completion_result")
    if completion is not None:
        presentations.append(
            completion if isinstance(completion, str) else canonical_serialize(completion)
        )
    output_tail = owner_result.get("conversation_output_tail")
    if isinstance(output_tail, list):
        presentations.extend(
            item for item in output_tail if isinstance(item, str) and item
        )
    if not presentations:
        presentations.append(f"Canonical Human Entry owner status: {owner_status}")
    return tuple(dict.fromkeys(presentations))


def _canonical_che_owner_references(
    owner_result: dict[str, Any],
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    evidence: set[str] = set()
    replay: set[str] = set()
    certification: set[str] = set()

    def visit(value: Any, field_name: str = "") -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                visit(item, str(key))
            return
        if isinstance(value, (list, tuple)):
            for item in value:
                visit(item, field_name)
            return
        if not isinstance(value, str) or not value:
            return
        normalized = field_name.lower()
        if "certification" in normalized and "reference" in normalized:
            certification.add(value)
        elif "replay_reference" in normalized:
            replay.add(value)
        elif normalized.endswith("_hash") or normalized == "artifact_hash":
            evidence.add(value)

    visit(owner_result)
    return tuple(sorted(evidence)), tuple(sorted(replay)), tuple(sorted(certification))


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required")
    return value.strip()
