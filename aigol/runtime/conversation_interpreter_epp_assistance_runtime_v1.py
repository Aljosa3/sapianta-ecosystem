"""Thin, non-authoritative Conversation Interpreter adapter to existing EPP.

The adapter selects an existing provider, translates one bounded conversation
turn into the existing ProviderAdapter contract, normalizes the returned text
into a G59-04 proposal, and invokes the deterministic proposal validator.  It
does not commit candidates, mutate CWM, create Objectives, or enter execution.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from aigol.provider.provider_adapter import ProviderAdapter
from aigol.provider.provider_proposal_envelope import validate_provider_proposal_envelope
from aigol.provider.provider_registry import AVAILABLE, ProviderRegistry
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash
from aigol.runtime import platform_core_conversation_interpreter_proposal_runtime_v2 as proposal_v2
from aigol.runtime import platform_core_conversation_working_memory_runtime_v2 as cwm_v2
from aigol.runtime.provider_necessity_policy_runtime import PROVIDER_REQUIRED
from aigol.runtime.unified_resource_selection_runtime import (
    FAILED_CLOSED as RESOURCE_SELECTION_FAILED,
    HYBRID_PROVIDER_WORKER,
    PROVIDER,
    PROVIDER_ROLE,
    RESOURCE_SELECTION_SUCCEEDED,
    select_unified_resource,
)


CONVERSATION_INTERPRETER_EPP_ASSISTANCE_RUNTIME_V1 = (
    "CONVERSATION_INTERPRETER_EPP_ASSISTANCE_RUNTIME_V1"
)
CONVERSATION_INTERPRETER_EPP_SELECTION_AND_BINDING_PROFILE_V1 = (
    "CONVERSATION_INTERPRETER_EPP_SELECTION_AND_BINDING_PROFILE_V1"
)
CONVERSATION_INTERPRETER_EPP_REQUEST_V1 = "CONVERSATION_INTERPRETER_EPP_REQUEST_V1"
CONVERSATION_INTERPRETER_EPP_RESPONSE_V1 = "CONVERSATION_INTERPRETER_EPP_RESPONSE_V1"
CONVERSATION_INTERPRETER_EPP_RESULT_V1 = "CONVERSATION_INTERPRETER_EPP_RESULT_V1"

NORMALIZED_AND_VALIDATED = "NORMALIZED_AND_VALIDATED"
VALIDATION_REJECTED = "VALIDATION_REJECTED"
FAILED_CLOSED = "FAILED_CLOSED"

MAX_PROVIDER_RESPONSE_CHARACTERS = 65_536
MAX_PROVIDER_OPERATIONS = 32
MAX_PROVIDER_EVIDENCE_REFERENCES = 32

_RESPONSE_FIELDS = frozenset(
    {
        "response_schema_version",
        "operations",
        "evidence_references",
        "advisory_confidence",
        "ambiguity_operation_indexes",
        "conflict_operation_indexes",
    }
)
_OPERATION_FIELDS = frozenset(
    {
        "operation_type",
        "slot_class",
        "slot_role",
        "cardinality_key",
        "surface_value",
        "canonical_value",
        "source_spans",
        "target_slot_id",
        "depends_on_slot_ids",
        "evidence_reference_keys",
        "clarification_reason",
    }
)
_EVIDENCE_FIELDS = frozenset(
    {"reference_key", "reference_kind", "reference_digest", "verification_status"}
)
_SPAN_FIELDS = frozenset({"start_offset", "end_offset"})
_CONFIDENCE_FIELDS = frozenset(
    {"scale_id", "reported_value", "limitations", "authority_effect"}
)
_BOUNDARY_FLAGS = {
    "semantic_cwm_mutated": False,
    "proposal_commit_performed": False,
    "conversation_transition_applied": False,
    "objective_created": False,
    "objective_commitment_created": False,
    "platform_core_invoked": False,
    "development_governance_invoked": False,
    "capability_selection_invoked": False,
    "authorization_created": False,
    "worker_invoked": False,
    "execution_invoked": False,
    "provider_content_replay_written": False,
}


def create_conversation_interpreter_epp_selection_and_binding_profile_v1(
    *,
    interpreter_identity: str,
    interpreter_version: str,
    resource_id: str,
    provider_id: str,
    provider_version: str,
    model_id: str,
    model_configuration_version: str = "V1",
    credential_reference_id: str = "provider-composition-owned",
    timeout_seconds: int = 30,
    maximum_input_bytes: int = 65_536,
    maximum_output_bytes: int = 65_536,
) -> dict[str, Any]:
    """Create one immutable binding; this is not a provider or model registry."""

    profile = {
        "profile_type": CONVERSATION_INTERPRETER_EPP_SELECTION_AND_BINDING_PROFILE_V1,
        "profile_version": "V1",
        "interpreter_identity": _string(interpreter_identity, "interpreter_identity"),
        "interpreter_class": proposal_v2.EXTERNAL_LANGUAGE_MODEL,
        "interpreter_version": _string(interpreter_version, "interpreter_version"),
        "proposal_schema_version": (
            proposal_v2.PLATFORM_CORE_CONVERSATION_INTERPRETER_PROPOSAL_SCHEMA_V1
        ),
        "epp_resource_id": _string(resource_id, "resource_id").upper(),
        "provider_id": _string(provider_id, "provider_id"),
        "provider_version": _string(provider_version, "provider_version"),
        "model_id": _string(model_id, "model_id"),
        "model_configuration_version": _string(
            model_configuration_version, "model_configuration_version"
        ),
        "credential_reference_id": _string(
            credential_reference_id, "credential_reference_id"
        ),
        "workflow_type": "CONVERSATION_INTERPRETATION",
        "provider_capability": "PROPOSAL_GENERATION",
        "provider_role": PROVIDER_ROLE,
        "domain_scope": "GOVERNANCE",
        "provider_necessity_classification": PROVIDER_REQUIRED,
        "minimum_trust_level": "STANDARD",
        "timeout_seconds": _positive_integer(timeout_seconds, "timeout_seconds"),
        "maximum_input_bytes": _positive_integer(
            maximum_input_bytes, "maximum_input_bytes"
        ),
        "maximum_output_bytes": _positive_integer(
            maximum_output_bytes, "maximum_output_bytes"
        ),
        "external_data_processing": True,
        "streaming": False,
        "tools": False,
        "function_calling": False,
        "automatic_retries": False,
        "substitution": False,
        "memory": False,
        "authority_profile": "PROVIDER_PROPOSAL_ONLY",
        "semantic_authority": False,
        "objective_authority": False,
        "commit_authority": False,
        "execution_authority": False,
        "worker_authority": False,
    }
    profile["profile_digest"] = replay_hash(profile)
    return profile


def run_conversation_interpreter_epp_assistance_v1(
    *,
    current_state: dict[str, Any],
    source_turn_text: str,
    observed_at: str,
    binding_profile: dict[str, Any],
    interpreter_registry: list[dict[str, Any]],
    provider_registry: ProviderRegistry,
    provider_adapter: ProviderAdapter,
    selection_replay_dir: str | Path,
) -> dict[str, Any]:
    """Return a validated candidate or a stable fail-closed result."""

    profile_hash = (
        binding_profile.get("profile_digest")
        if isinstance(binding_profile, dict)
        else None
    )
    selection_capture: dict[str, Any] | None = None
    request: dict[str, Any] | None = None
    provider_invoked = False
    provider_response_received = False
    try:
        profile = _validate_profile(binding_profile)
        state = cwm_v2.validate_conversation_working_memory_state_v2(current_state)
        turn = _string(source_turn_text, "source_turn_text")
        if len(turn) > proposal_v2.MAX_SOURCE_TURN_CHARACTERS:
            raise FailClosedRuntimeError("source turn exceeds interpreter bound")
        _validate_provider_binding(profile, provider_registry, provider_adapter)

        request = create_conversation_interpreter_epp_request_v1(
            current_state=state, source_turn_text=turn, binding_profile=profile
        )
        selection_id = "conversation-epp-selection-sha256:" + replay_hash(
            {
                "profile_digest": profile["profile_digest"],
                "request_integrity": request["request_integrity"],
            }
        ).split(":", 1)[1]
        selection_capture = select_unified_resource(
            selection_id=selection_id,
            workflow_type=profile["workflow_type"],
            required_capability=profile["provider_capability"],
            requested_role_type=profile["provider_role"],
            domain_id=profile["domain_scope"],
            created_at=observed_at,
            replay_dir=selection_replay_dir,
            provider_necessity_classification=profile[
                "provider_necessity_classification"
            ],
            worker_authorization_required=False,
            min_trust_level=profile["minimum_trust_level"],
            preferred_resource_id=profile["epp_resource_id"],
            context_assembly_output=None,
        )
        _validate_selection(profile, selection_capture)

        provider_invoked = True
        provider_envelope = provider_adapter.generate_proposal(
            {"prompt": request["prompt"], "request": request},
            proposal_id=request["provider_proposal_id"],
            timestamp=observed_at,
        )
        provider_response_received = True
        envelope = validate_provider_proposal_envelope(provider_envelope)
        _validate_provider_envelope(profile, request, envelope)
        proposal = adapt_epp_response_to_interpreter_proposal_v1(
            current_state=state,
            source_turn_text=turn,
            binding_profile=profile,
            interpreter_request=request,
            epp_response=envelope,
        )
        validation = proposal_v2.assess_conversation_interpreter_proposal_v2(
            proposal,
            current_state=state,
            source_turn_text=turn,
            observed_at=observed_at,
            interpreter_registry=interpreter_registry,
        )
        status = (
            VALIDATION_REJECTED
            if validation["validation_disposition"] == proposal_v2.REJECTED
            else NORMALIZED_AND_VALIDATED
        )
        return _result(
            status=status,
            failure_code=None,
            profile_hash=profile["profile_digest"],
            selection_capture=selection_capture,
            request=request,
            provider_envelope_hash=envelope["proposal_hash"],
            proposal=proposal,
            validation=validation,
            provider_invoked=True,
        )
    except Exception as exc:
        if _exception_is_timeout(exc):
            failure_code = "PROVIDER_TIMEOUT"
        else:
            failure_code = _failure_code(
                exc,
                provider_invoked,
                provider_response_received,
                selection_capture,
            )
    return _result(
        status=FAILED_CLOSED,
        failure_code=failure_code,
        profile_hash=profile_hash,
        selection_capture=selection_capture,
        request=request,
        provider_envelope_hash=None,
        proposal=None,
        validation=None,
        provider_invoked=provider_invoked,
    )


def create_conversation_interpreter_epp_request_v1(
    *,
    current_state: dict[str, Any],
    source_turn_text: str,
    binding_profile: dict[str, Any],
) -> dict[str, Any]:
    """Build a bounded immutable request capsule without runtime state handles."""

    state = cwm_v2.validate_conversation_working_memory_state_v2(current_state)
    profile = _validate_profile(binding_profile)
    envelope = state["envelope"]
    binding = proposal_v2.create_source_turn_binding_v2(
        conversation_identity=envelope["conversation_identity"],
        session_identity_hash=envelope["session_identity_hash"],
        expected_cwm_revision=state["revision"],
        source_turn_text=source_turn_text,
    )
    semantic_snapshot = [
        {
            "slot_id": item["slot_id"],
            "slot_class": item["slot_class"],
            "slot_role": item["slot_role"],
            "cardinality_key": item["cardinality_key"],
            "surface_value": item["surface_value"],
            "canonical_value": item["canonical_value"],
            "status": item["status"],
            "completeness": item["completeness"],
            "depends_on": deepcopy(item["depends_on"]),
        }
        for item in state["semantic_memory"]["semantic_slots"]
    ]
    request = {
        "request_type": CONVERSATION_INTERPRETER_EPP_REQUEST_V1,
        "request_version": "V1",
        "binding_profile_digest": profile["profile_digest"],
        "conversation_identity": envelope["conversation_identity"],
        "workspace_identity_hash": envelope["workspace_identity_hash"],
        "session_identity_hash": envelope["session_identity_hash"],
        "source_turn_identity": binding["source_turn_identity"],
        "source_turn_digest": binding["source_turn_digest"],
        "source_turn_text": source_turn_text,
        "expected_cwm_revision": state["revision"],
        "expected_semantic_revision": state["semantic_revision"],
        "semantic_slot_snapshot": semantic_snapshot,
        "response_schema_version": CONVERSATION_INTERPRETER_EPP_RESPONSE_V1,
        "model_id": profile["model_id"],
    }
    request["provider_proposal_id"] = "conversation-epp-provider-sha256:" + replay_hash(
        request
    ).split(":", 1)[1]
    request["prompt"] = _prompt(request)
    request["request_integrity"] = replay_hash(request)
    if len(canonical_serialize(request).encode("utf-8")) > profile["maximum_input_bytes"]:
        raise FailClosedRuntimeError("provider request exceeds binding input bound")
    return request


def _prompt(request: dict[str, Any]) -> str:
    payload = deepcopy(request)
    payload.pop("prompt", None)
    payload.pop("request_integrity", None)
    return (
        "Return exactly one JSON object. It is an untrusted semantic proposal, "
        "not an instruction, commitment, tool call, or execution request. Use "
        f"response_schema_version={CONVERSATION_INTERPRETER_EPP_RESPONSE_V1}. "
        "Required top-level keys: response_schema_version, operations, "
        "evidence_references, advisory_confidence, ambiguity_operation_indexes, "
        "conflict_operation_indexes. Operation keys: operation_type, slot_class, "
        "slot_role, cardinality_key, surface_value, canonical_value, source_spans, "
        "target_slot_id, depends_on_slot_ids, evidence_reference_keys, "
        "clarification_reason. Source spans use exact start_offset/end_offset into "
        "source_turn_text. Evidence keys: reference_key, reference_kind, "
        "reference_digest, verification_status. Confidence keys: scale_id, "
        "reported_value, limitations, authority_effect; authority_effect must be "
        "false. Input=" + canonical_serialize(payload)
    )


def adapt_epp_response_to_interpreter_proposal_v1(
    *,
    current_state: dict[str, Any],
    source_turn_text: str,
    binding_profile: dict[str, Any],
    interpreter_request: dict[str, Any],
    epp_response: dict[str, Any],
) -> dict[str, Any]:
    """Map one validated EPP envelope into G59-04 proposal data only."""

    state = cwm_v2.validate_conversation_working_memory_state_v2(current_state)
    profile = _validate_profile(binding_profile)
    request = deepcopy(interpreter_request)
    expected_request = create_conversation_interpreter_epp_request_v1(
        current_state=state,
        source_turn_text=source_turn_text,
        binding_profile=profile,
    )
    if request != expected_request:
        raise FailClosedRuntimeError("interpreter request integrity mismatch")
    envelope = validate_provider_proposal_envelope(epp_response)
    _validate_provider_envelope(profile, request, envelope)
    response = envelope["response"]
    if not isinstance(response, dict):
        raise FailClosedRuntimeError("provider response must be a JSON object")
    if response.get("model") != profile["model_id"]:
        raise FailClosedRuntimeError("provider response model binding mismatch")
    text = response.get("response_text")
    if not isinstance(text, str) or not text.strip():
        raise FailClosedRuntimeError("provider response text is required")
    if len(text.encode("utf-8")) > min(
        MAX_PROVIDER_RESPONSE_CHARACTERS, profile["maximum_output_bytes"]
    ):
        raise FailClosedRuntimeError("provider response exceeds adapter bound")
    raw = json.loads(text)
    _closed(raw, _RESPONSE_FIELDS, "provider normalized response")
    if raw["response_schema_version"] != CONVERSATION_INTERPRETER_EPP_RESPONSE_V1:
        raise FailClosedRuntimeError("provider response schema is invalid")
    raw_evidence = _list(
        raw["evidence_references"],
        "evidence_references",
        MAX_PROVIDER_EVIDENCE_REFERENCES,
    )
    evidence: list[dict[str, Any]] = []
    evidence_ids: dict[str, str] = {}
    for item in raw_evidence:
        _closed(item, _EVIDENCE_FIELDS, "evidence reference")
        key = _string(item["reference_key"], "reference_key")
        if key in evidence_ids:
            raise FailClosedRuntimeError("duplicate evidence reference key")
        normalized = proposal_v2.create_evidence_reference_v2(
            reference_kind=item["reference_kind"],
            reference_digest=item["reference_digest"],
            verification_status=item["verification_status"],
        )
        evidence_ids[key] = normalized["reference_id"]
        evidence.append(normalized)

    raw_operations = _list(raw["operations"], "operations", MAX_PROVIDER_OPERATIONS)
    operations: list[dict[str, Any]] = []
    for item in raw_operations:
        _closed(item, _OPERATION_FIELDS, "operation")
        spans = []
        for span in _list(
            item["source_spans"], "source_spans", proposal_v2.MAX_SOURCE_SPANS
        ):
            _closed(span, _SPAN_FIELDS, "source span")
            spans.append(
                proposal_v2.create_source_span_v2(
                    source_turn_text,
                    start_offset=span["start_offset"],
                    end_offset=span["end_offset"],
                )
            )
        keys = _string_list(
            item["evidence_reference_keys"], "evidence_reference_keys"
        )
        if any(key not in evidence_ids for key in keys):
            raise FailClosedRuntimeError("operation evidence key is unknown")
        operations.append(
            proposal_v2.create_proposed_semantic_operation_v2(
                conversation_identity=state["envelope"]["conversation_identity"],
                operation_type=item["operation_type"],
                slot_class=item["slot_class"],
                slot_role=item["slot_role"],
                cardinality_key=item["cardinality_key"],
                surface_value=item["surface_value"],
                canonical_value=item["canonical_value"],
                source_spans=spans,
                target_slot_id=item["target_slot_id"],
                depends_on_slot_ids=_string_list(
                    item["depends_on_slot_ids"], "depends_on_slot_ids"
                ),
                evidence_reference_ids=[evidence_ids[key] for key in keys],
                clarification_reason=item["clarification_reason"],
            )
        )
    ambiguity_ids = _operation_ids_from_indexes(
        raw["ambiguity_operation_indexes"], operations, "ambiguity"
    )
    conflict_ids = _operation_ids_from_indexes(
        raw["conflict_operation_indexes"], operations, "conflict"
    )
    _closed(raw["advisory_confidence"], _CONFIDENCE_FIELDS, "advisory_confidence")
    return proposal_v2.create_conversation_interpreter_proposal_v2(
        interpreter_identity=profile["interpreter_identity"],
        interpreter_class=profile["interpreter_class"],
        interpreter_version=profile["interpreter_version"],
        conversation_identity=request["conversation_identity"],
        workspace_identity_hash=request["workspace_identity_hash"],
        session_identity_hash=request["session_identity_hash"],
        source_turn_identity=request["source_turn_identity"],
        source_turn_digest=request["source_turn_digest"],
        expected_cwm_revision=request["expected_cwm_revision"],
        expected_semantic_revision=request["expected_semantic_revision"],
        proposed_semantic_operations=operations,
        evidence_references=evidence,
        advisory_confidence=raw["advisory_confidence"],
        ambiguity_declaration={
            "declared": bool(ambiguity_ids),
            "operation_ids": ambiguity_ids,
        },
        conflict_declaration={
            "declared": bool(conflict_ids),
            "operation_ids": conflict_ids,
        },
    )


def _validate_profile(profile: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(profile, dict):
        raise FailClosedRuntimeError("binding profile must be a JSON object")
    candidate = deepcopy(profile)
    actual = candidate.pop("profile_digest", None)
    if candidate.get("profile_type") != (
        CONVERSATION_INTERPRETER_EPP_SELECTION_AND_BINDING_PROFILE_V1
    ):
        raise FailClosedRuntimeError("binding profile type is invalid")
    required = create_conversation_interpreter_epp_selection_and_binding_profile_v1(
        interpreter_identity=candidate.get("interpreter_identity"),
        interpreter_version=candidate.get("interpreter_version"),
        resource_id=candidate.get("epp_resource_id"),
        provider_id=candidate.get("provider_id"),
        provider_version=candidate.get("provider_version"),
        model_id=candidate.get("model_id"),
        model_configuration_version=candidate.get("model_configuration_version"),
        credential_reference_id=candidate.get("credential_reference_id"),
        timeout_seconds=candidate.get("timeout_seconds"),
        maximum_input_bytes=candidate.get("maximum_input_bytes"),
        maximum_output_bytes=candidate.get("maximum_output_bytes"),
    )
    if profile != required or actual != required["profile_digest"]:
        raise FailClosedRuntimeError("binding profile is not canonical")
    return required


def _validate_provider_binding(
    profile: dict[str, Any], registry: ProviderRegistry, adapter: ProviderAdapter
) -> None:
    metadata = registry.lookup_provider(profile["provider_id"])
    if metadata["provider_status"] != AVAILABLE:
        raise FailClosedRuntimeError("bound provider is not available")
    if metadata["provider_version"] != profile["provider_version"]:
        raise FailClosedRuntimeError("provider registry version mismatch")
    if metadata["capability"] != profile["provider_capability"].lower():
        raise FailClosedRuntimeError("provider registry capability mismatch")
    if (
        adapter.provider_id != profile["provider_id"]
        or adapter.provider_version != profile["provider_version"]
    ):
        raise FailClosedRuntimeError("provider adapter identity mismatch")
    adapter_model = getattr(adapter, "model", profile["model_id"])
    if adapter_model != profile["model_id"]:
        raise FailClosedRuntimeError("provider adapter model binding mismatch")
    adapter_timeout = getattr(adapter, "timeout_seconds", profile["timeout_seconds"])
    if adapter_timeout != profile["timeout_seconds"]:
        raise FailClosedRuntimeError("provider adapter timeout binding mismatch")


def _validate_selection(profile: dict[str, Any], capture: dict[str, Any]) -> None:
    if capture.get("selection_status") in {RESOURCE_SELECTION_FAILED, None}:
        raise FailClosedRuntimeError("existing resource selection failed closed")
    artifact = capture.get("resource_selection_artifact")
    if not isinstance(artifact, dict) or artifact.get("selection_status") != (
        RESOURCE_SELECTION_SUCCEEDED
    ):
        raise FailClosedRuntimeError("existing resource selection did not succeed")
    if artifact.get("selected_resource_id") != profile["epp_resource_id"]:
        raise FailClosedRuntimeError("selected resource binding mismatch")
    if artifact.get("selected_resource_category") not in {
        PROVIDER,
        HYBRID_PROVIDER_WORKER,
    }:
        raise FailClosedRuntimeError("selected resource category is not provider-capable")
    if artifact.get("selected_resource_version") != profile["provider_version"]:
        raise FailClosedRuntimeError("selected resource version mismatch")
    if artifact.get("selected_role_type") != PROVIDER_ROLE or artifact.get(
        "selected_authority_profile"
    ) != profile["authority_profile"]:
        raise FailClosedRuntimeError("selected provider authority binding mismatch")
    for flag in (
        "worker_invoked",
        "execution_requested",
        "dispatch_requested",
        "authorization_created",
    ):
        if artifact.get(flag) is not False:
            raise FailClosedRuntimeError("resource selection crossed an authority boundary")


def _validate_provider_envelope(
    profile: dict[str, Any], request: dict[str, Any], envelope: dict[str, Any]
) -> None:
    if envelope["proposal_id"] != request["provider_proposal_id"]:
        raise FailClosedRuntimeError("provider proposal identity mismatch")
    if (
        envelope["provider_id"] != profile["provider_id"]
        or envelope["provider_version"] != profile["provider_version"]
    ):
        raise FailClosedRuntimeError("provider proposal binding mismatch")
    expected_request = {"prompt": request["prompt"], "request": request}
    if not _contains_exact_request_binding(envelope["request"], expected_request):
        raise FailClosedRuntimeError("provider proposal request binding mismatch")


def _contains_exact_request_binding(value: Any, expected: dict[str, Any]) -> bool:
    if value == expected:
        return True
    if isinstance(value, dict):
        return any(
            _contains_exact_request_binding(nested, expected)
            for nested in value.values()
        )
    if isinstance(value, list):
        return any(_contains_exact_request_binding(nested, expected) for nested in value)
    return False


def _operation_ids_from_indexes(
    value: Any, operations: list[dict[str, Any]], name: str
) -> list[str]:
    if not isinstance(value, list) or len(value) > len(operations):
        raise FailClosedRuntimeError(f"{name} operation indexes are invalid")
    if any(
        not isinstance(index, int)
        or isinstance(index, bool)
        or index < 0
        or index >= len(operations)
        for index in value
    ):
        raise FailClosedRuntimeError(f"{name} operation index is invalid")
    if value != sorted(set(value)):
        raise FailClosedRuntimeError(f"{name} operation indexes are not canonical")
    return sorted(operations[index]["operation_id"] for index in value)


def _result(
    *,
    status: str,
    failure_code: str | None,
    profile_hash: str | None,
    selection_capture: dict[str, Any] | None,
    request: dict[str, Any] | None,
    provider_envelope_hash: str | None,
    proposal: dict[str, Any] | None,
    validation: dict[str, Any] | None,
    provider_invoked: bool,
) -> dict[str, Any]:
    artifact = (
        selection_capture.get("resource_selection_artifact")
        if isinstance(selection_capture, dict)
        else None
    )
    result = {
        "result_type": CONVERSATION_INTERPRETER_EPP_RESULT_V1,
        "runtime_version": CONVERSATION_INTERPRETER_EPP_ASSISTANCE_RUNTIME_V1,
        "adapter_status": status,
        "failure_code": failure_code,
        "binding_profile_hash": profile_hash,
        "selection_capture_hash": (
            selection_capture.get("resource_selection_capture_hash")
            if isinstance(selection_capture, dict)
            else None
        ),
        "selection_artifact_hash": (
            artifact.get("artifact_hash") if isinstance(artifact, dict) else None
        ),
        "selection_replay_reference": (
            selection_capture.get("resource_selection_replay_reference")
            if isinstance(selection_capture, dict)
            else None
        ),
        "selected_resource_id": (
            artifact.get("selected_resource_id")
            if isinstance(artifact, dict)
            else None
        ),
        "selected_provider_role": (
            artifact.get("selected_role_type")
            if isinstance(artifact, dict)
            else None
        ),
        "request_integrity": request.get("request_integrity") if isinstance(request, dict) else None,
        "provider_proposal_hash": provider_envelope_hash,
        "normalized_proposal": deepcopy(proposal),
        "validation_result": deepcopy(validation),
        "candidate_operation_set": (
            deepcopy(validation.get("candidate_operation_set"))
            if isinstance(validation, dict)
            else None
        ),
        "provider_invoked": provider_invoked,
        **deepcopy(_BOUNDARY_FLAGS),
    }
    result["integrity_binding"] = replay_hash(
        {
            "binding_profile_hash": result["binding_profile_hash"],
            "selection_artifact_hash": result["selection_artifact_hash"],
            "request_integrity": result["request_integrity"],
            "provider_proposal_hash": result["provider_proposal_hash"],
            "normalized_proposal_integrity": (
                proposal.get("integrity_checksum")
                if isinstance(proposal, dict)
                else None
            ),
            "validation_disposition": (
                validation.get("validation_disposition")
                if isinstance(validation, dict)
                else None
            ),
        }
    )
    result["result_hash"] = replay_hash(result)
    return result


def _failure_code(
    exc: Exception,
    provider_invoked: bool,
    provider_response_received: bool,
    selection_capture: dict[str, Any] | None,
) -> str:
    if isinstance(selection_capture, dict) and selection_capture.get(
        "selection_status"
    ) == RESOURCE_SELECTION_FAILED:
        return "RESOURCE_SELECTION_FAILED"
    text = str(exc).lower()
    if provider_invoked and "timeout" in text:
        return "PROVIDER_TIMEOUT"
    if provider_invoked and not provider_response_received:
        return "PROVIDER_FAILURE"
    if provider_invoked:
        return "PROVIDER_RESPONSE_REJECTED"
    return "ADAPTER_INPUT_REJECTED"


def _exception_is_timeout(exc: Exception) -> bool:
    current: BaseException | None = exc
    visited: set[int] = set()
    while current is not None and id(current) not in visited:
        visited.add(id(current))
        if isinstance(current, TimeoutError) or "timeout" in str(current).lower():
            return True
        current = current.__cause__ or current.__context__
    return False


def _closed(value: Any, fields: frozenset[str], name: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        raise FailClosedRuntimeError(f"{name} fields are invalid")
    return value


def _list(value: Any, name: str, maximum: int) -> list[Any]:
    if not isinstance(value, list) or len(value) > maximum:
        raise FailClosedRuntimeError(f"{name} is invalid")
    return value


def _string_list(value: Any, name: str) -> list[str]:
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item for item in value
    ):
        raise FailClosedRuntimeError(f"{name} is invalid")
    if value != sorted(set(value)):
        raise FailClosedRuntimeError(f"{name} is not canonical")
    return value


def _string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{name} is required")
    return value


def _positive_integer(value: Any, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise FailClosedRuntimeError(f"{name} must be a positive integer")
    return value


__all__ = [
    "CONVERSATION_INTERPRETER_EPP_ASSISTANCE_RUNTIME_V1",
    "CONVERSATION_INTERPRETER_EPP_SELECTION_AND_BINDING_PROFILE_V1",
    "CONVERSATION_INTERPRETER_EPP_REQUEST_V1",
    "CONVERSATION_INTERPRETER_EPP_RESPONSE_V1",
    "CONVERSATION_INTERPRETER_EPP_RESULT_V1",
    "NORMALIZED_AND_VALIDATED",
    "VALIDATION_REJECTED",
    "FAILED_CLOSED",
    "create_conversation_interpreter_epp_selection_and_binding_profile_v1",
    "create_conversation_interpreter_epp_request_v1",
    "adapt_epp_response_to_interpreter_proposal_v1",
    "run_conversation_interpreter_epp_assistance_v1",
]
