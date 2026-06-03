"""Governed provider proposal repair and retry runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.provider.provider_adapter import ProviderAdapter
from aigol.provider.provider_registry import ProviderRegistry
from aigol.provider.provider_runtime import run_provider_attachment
from aigol.runtime.development_context_assembly_runtime import (
    CONTEXT_ASSEMBLED,
    DEVELOPMENT_CONTEXT_ASSEMBLY_ARTIFACT_V1,
)
from aigol.runtime.development_proposal_contract_runtime import (
    DEVELOPMENT_PROPOSAL_ARTIFACT_V1,
    DEVELOPMENT_PROPOSAL_CONTRACT_VALIDATED,
    validate_development_proposal_contract,
)
from aigol.runtime.domain_and_worker_resolution_registry import (
    DOMAIN_WORKER_RESOLUTION_ARTIFACT_V1,
    RESOLUTION_SUCCEEDED,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_necessity_policy_runtime import (
    PROVIDER_NECESSITY_CLASSIFIED,
    PROVIDER_NECESSITY_POLICY_ARTIFACT_V1,
    PROVIDER_PROHIBITED,
    PROVIDER_REQUIRED,
)
from aigol.runtime.provider_proposal_production_runtime import (
    PROVIDER_RESPONSE_ARTIFACT_V1,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_PROVIDER_PROPOSAL_REPAIR_AND_RETRY_RUNTIME_VERSION = (
    "AIGOL_PROVIDER_PROPOSAL_REPAIR_AND_RETRY_RUNTIME_V1"
)
PROVIDER_REPAIR_REQUEST_V1 = "PROVIDER_REPAIR_REQUEST_V1"
PROVIDER_RETRY_RESPONSE_V1 = "PROVIDER_RETRY_RESPONSE_V1"
CORRECTED_DEVELOPMENT_PROPOSAL_V1 = "CORRECTED_DEVELOPMENT_PROPOSAL_V1"
RETRY_STATUS_ARTIFACT_V1 = "RETRY_STATUS_ARTIFACT_V1"
HUMAN_CLARIFICATION_REQUIRED_ARTIFACT_V1 = "HUMAN_CLARIFICATION_REQUIRED_ARTIFACT_V1"
HUMAN_APPROVAL_REQUIRED_ARTIFACT_V1 = "HUMAN_APPROVAL_REQUIRED_ARTIFACT_V1"

MAX_PROVIDER_RETRIES = 3
AUTO_RETRY = "AUTO_RETRY"
RETRY_SUCCEEDED = "RETRY_SUCCEEDED"
HUMAN_CLARIFICATION_REQUIRED = "HUMAN_CLARIFICATION_REQUIRED"
HUMAN_APPROVAL_REQUIRED = "HUMAN_APPROVAL_REQUIRED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "provider_repair_request_created",
    "provider_retry_response_captured",
    "retry_status_recorded",
    "provider_repair_retry_returned",
)

AMBIGUITY_MARKERS = (
    "ambiguous intent",
    "intent is ambiguous",
    "domain resolution is ambiguous",
    "worker resolution is ambiguous",
    "context remains incomplete",
    "provider confidence is insufficient",
    "ambiguous requested scope",
    "ambiguous domain",
    "ambiguous worker",
)

RETRYABLE_MARKERS = (
    "missing references",
    "missing fields",
    "proposal is incomplete",
    "invalid schema",
    "invalid artifact links",
    "replay-visible integrity",
    "contract violation",
    "proposal references unknown entities",
    "hash mismatch",
)

HIGH_RISK_DOMAINS = ("TRADING", "HEALTHCARE", "LEGAL", "CRITICAL_INFRASTRUCTURE", "PUBLIC_SERVICES")

FORBIDDEN_AUTHORITY_FIELDS = (
    "authorization_decision",
    "governance_decision",
    "execution_request",
    "dispatch_request",
    "worker_command",
    "provider_command",
    "worker_instruction",
    "memory_mutation",
    "replay_mutation",
    "execution_authority",
    "dispatch_authority",
    "governance_authority",
    "replay_authority",
    "provider_authority",
    "execution_requested",
    "dispatch_requested",
    "worker_created",
    "domain_created",
    "governance_modified",
    "replay_modified",
)


def repair_and_retry_provider_development_proposal(
    *,
    repair_id: str,
    rejected_proposal_artifact: dict[str, Any],
    validation_failure_evidence: dict[str, Any],
    provider_response_artifact: dict[str, Any],
    context_assembly_artifact: dict[str, Any],
    registry_resolution_artifact: dict[str, Any],
    provider_necessity_policy_artifact: dict[str, Any],
    canonical_chain_id: str,
    provider_id: str,
    created_at: str,
    registry: ProviderRegistry,
    adapter: ProviderAdapter,
    replay_dir: str | Path,
    max_provider_retries: int = MAX_PROVIDER_RETRIES,
) -> dict[str, Any]:
    """Repair rejected proposal evidence through bounded provider retries."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        proposal = deepcopy(rejected_proposal_artifact)
        validation = deepcopy(validation_failure_evidence)
        original_response = deepcopy(provider_response_artifact)
        context = deepcopy(context_assembly_artifact)
        resolution = deepcopy(registry_resolution_artifact)
        policy = deepcopy(provider_necessity_policy_artifact)
        _validate_rejected_proposal(proposal)
        _validate_failure_evidence(validation)
        _validate_original_response(original_response)
        _validate_context(context)
        _validate_resolution(resolution)
        _validate_provider_policy(policy)
        retry_limit = _validate_retry_limit(max_provider_retries)
        failure_reason = _failure_from_validation(validation)
        repair_policy = _repair_policy(failure_reason=failure_reason)
        request = _repair_request_artifact(
            repair_id=repair_id,
            provider_id=provider_id,
            proposal=proposal,
            validation=validation,
            original_response=original_response,
            context=context,
            resolution=resolution,
            policy=policy,
            canonical_chain_id=canonical_chain_id,
            repair_policy=repair_policy,
            max_provider_retries=retry_limit,
            created_at=created_at,
        )
        _persist_step(replay_path, 0, REPLAY_STEPS[0], request)
        if repair_policy == HUMAN_CLARIFICATION_REQUIRED:
            clarification = _human_clarification_artifact(
                repair_id=repair_id,
                request=request,
                reason=failure_reason,
                created_at=created_at,
            )
            retry_response = _retry_response_artifact(
                repair_id=repair_id,
                request=request,
                retry_history=[],
                corrected_proposal=None,
                escalation_artifact=clarification,
                created_at=created_at,
                failure_reason=None,
            )
            status = _retry_status_artifact(
                repair_id=repair_id,
                request=request,
                retry_response=retry_response,
                corrected_proposal=None,
                status=HUMAN_CLARIFICATION_REQUIRED,
                retry_count=0,
                retry_history=[],
                clarification_artifact=clarification,
                approval_artifact=None,
                created_at=created_at,
                failure_reason=None,
            )
        else:
            retry_response, corrected_proposal, validation_capture, retry_history = _run_retries(
                repair_id=repair_id,
                provider_id=provider_id,
                request=request,
                context=context,
                resolution=resolution,
                registry=registry,
                adapter=adapter,
                created_at=created_at,
                replay_path=replay_path,
                retry_limit=retry_limit,
            )
            if corrected_proposal is None:
                raise FailClosedRuntimeError(
                    "provider proposal repair failed closed: invalid proposal repeatedly returned"
                )
            approval = None
            status_value = RETRY_SUCCEEDED
            if _is_high_risk_domain(resolution["domain_id"]):
                approval = _human_approval_artifact(
                    repair_id=repair_id,
                    request=request,
                    corrected_proposal=corrected_proposal,
                    validation_capture=validation_capture,
                    created_at=created_at,
                )
                status_value = HUMAN_APPROVAL_REQUIRED
            status = _retry_status_artifact(
                repair_id=repair_id,
                request=request,
                retry_response=retry_response,
                corrected_proposal=corrected_proposal,
                status=status_value,
                retry_count=len(retry_history),
                retry_history=retry_history,
                clarification_artifact=None,
                approval_artifact=approval,
                created_at=created_at,
                failure_reason=None,
            )
        _persist_step(replay_path, 1, REPLAY_STEPS[1], retry_response)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], status)
        returned = _returned_artifact(status)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], returned)
        return _capture(request, retry_response, status, returned, replay_path)
    except Exception as exc:
        request = locals().get("request")
        retry_response = locals().get("retry_response")
        status = _failed_status_artifact(
            repair_id=repair_id,
            provider_id=provider_id,
            request=request if isinstance(request, dict) else None,
            retry_response=retry_response if isinstance(retry_response, dict) else None,
            canonical_chain_id=canonical_chain_id,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        retry_response = retry_response if isinstance(retry_response, dict) else _failed_retry_response(repair_id, created_at)
        returned = _returned_artifact(status)
        _persist_failure_sequence(replay_path, request, retry_response, status, returned)
        return _capture(
            request if isinstance(request, dict) else None,
            retry_response,
            status,
            returned,
            replay_path,
        )


def reconstruct_provider_proposal_repair_and_retry_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct provider proposal repair and retry replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("provider proposal repair retry replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("provider proposal repair retry replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "provider proposal repair retry artifact")
        wrappers.append(wrapper)
    request = wrappers[0]["artifact"]
    retry_response = wrappers[1]["artifact"]
    status = wrappers[2]["artifact"]
    returned = wrappers[3]["artifact"]
    if retry_response.get("repair_request_hash") != request["artifact_hash"]:
        raise FailClosedRuntimeError("provider proposal repair retry request hash mismatch")
    if status.get("repair_request_hash") != request["artifact_hash"]:
        raise FailClosedRuntimeError("provider proposal repair retry status request hash mismatch")
    if status.get("retry_response_hash") != retry_response["artifact_hash"]:
        raise FailClosedRuntimeError("provider proposal repair retry response hash mismatch")
    if returned.get("retry_status_reference") != status["retry_status_id"]:
        raise FailClosedRuntimeError("provider proposal repair retry returned reference mismatch")
    if returned.get("retry_status_hash") != status["artifact_hash"]:
        raise FailClosedRuntimeError("provider proposal repair retry returned hash mismatch")
    return {
        "repair_id": status["repair_id"],
        "retry_status": status["retry_status"],
        "retry_count": status["retry_count"],
        "retry_history": deepcopy(status["retry_history"]),
        "corrected_proposal_hash": status["corrected_proposal_hash"],
        "clarification_required": status["clarification_required"],
        "approval_required": status["approval_required"],
        "canonical_chain_id": status["canonical_chain_id"],
        "failure_reason": status["failure_reason"],
        "proposal_only": True,
        "provider_authority": False,
        "worker_created": False,
        "domain_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _run_retries(
    *,
    repair_id: str,
    provider_id: str,
    request: dict[str, Any],
    context: dict[str, Any],
    resolution: dict[str, Any],
    registry: ProviderRegistry,
    adapter: ProviderAdapter,
    created_at: str,
    replay_path: Path,
    retry_limit: int,
) -> tuple[dict[str, Any], dict[str, Any] | None, dict[str, Any] | None, list[dict[str, Any]]]:
    retry_history: list[dict[str, Any]] = []
    corrected_proposal = None
    validation_capture = None
    if retry_limit <= 0:
        raise FailClosedRuntimeError("provider proposal repair failed closed: retry limit exceeded")
    for attempt in range(1, retry_limit + 1):
        provider_capture = run_provider_attachment(
            provider_id=provider_id,
            request=_retry_request_payload(request, attempt),
            proposal_id=f"{repair_id}:RETRY-{attempt:03d}:PROVIDER-ENVELOPE",
            timestamp=created_at,
            registry=registry,
            adapter=adapter,
            replay_dir=replay_path / f"provider_retry_{attempt:03d}",
        )
        try:
            proposal = _proposal_from_provider_capture(
                repair_id=repair_id,
                attempt=attempt,
                provider_capture=provider_capture,
                context=context,
                resolution=resolution,
            )
            validation = validate_development_proposal_contract(
                contract_validation_id=f"{repair_id}:RETRY-{attempt:03d}:CONTRACT-VALIDATION",
                proposal_artifact=proposal,
                context_assembly_artifact=context,
                registry_resolution_artifact=resolution,
                created_at=created_at,
                replay_dir=replay_path / f"retry_contract_validation_{attempt:03d}",
            )
            retry_history.append(
                _retry_history_item(
                    attempt=attempt,
                    provider_capture=provider_capture,
                    proposal=proposal,
                    validation_capture=validation,
                )
            )
            if validation.get("validation_status") == DEVELOPMENT_PROPOSAL_CONTRACT_VALIDATED:
                corrected_proposal = proposal
                validation_capture = validation
                break
        except Exception as exc:
            reason = _failure_reason(exc)
            retry_history.append(
                {
                    "attempt": attempt,
                    "provider_request_hash": _provider_request_hash(provider_capture),
                    "provider_response_hash": _provider_response_hash(provider_capture),
                    "proposal_hash": None,
                    "validation_status": FAILED_CLOSED,
                    "retry_reason": reason,
                }
            )
            if "authority violation" in reason or "provider is unavailable" in reason:
                raise
    retry_response = _retry_response_artifact(
        repair_id=repair_id,
        request=request,
        retry_history=retry_history,
        corrected_proposal=corrected_proposal,
        escalation_artifact=None,
        created_at=created_at,
        failure_reason=None if corrected_proposal else "invalid proposal repeatedly returned",
    )
    return retry_response, corrected_proposal, validation_capture, retry_history


def _validate_rejected_proposal(proposal: dict[str, Any]) -> None:
    if proposal.get("artifact_type") != DEVELOPMENT_PROPOSAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("provider proposal repair failed closed: invalid proposal artifact")
    if "artifact_hash" in proposal:
        _verify_artifact_hash(proposal, "rejected development proposal")
    _assert_no_authority(proposal)


def _validate_failure_evidence(validation: dict[str, Any]) -> None:
    if not isinstance(validation, dict):
        raise FailClosedRuntimeError("provider proposal repair failed closed: validation failure evidence missing")
    if validation.get("validation_status") == DEVELOPMENT_PROPOSAL_CONTRACT_VALIDATED:
        raise FailClosedRuntimeError("provider proposal repair failed closed: proposal is not rejected")
    if "artifact_hash" in validation:
        _verify_artifact_hash(validation, "validation failure evidence")


def _validate_original_response(response: dict[str, Any]) -> None:
    if response.get("artifact_type") != PROVIDER_RESPONSE_ARTIFACT_V1:
        raise FailClosedRuntimeError("provider proposal repair failed closed: invalid provider response artifact")
    _verify_artifact_hash(response, "provider response artifact")
    _assert_no_authority(response)


def _validate_context(context: dict[str, Any]) -> None:
    if context.get("artifact_type") != DEVELOPMENT_CONTEXT_ASSEMBLY_ARTIFACT_V1:
        raise FailClosedRuntimeError("provider proposal repair failed closed: invalid context artifact")
    _verify_artifact_hash(context, "development context assembly")
    if context.get("context_status") != CONTEXT_ASSEMBLED:
        raise FailClosedRuntimeError("provider proposal repair failed closed: context remains incomplete")


def _validate_resolution(resolution: dict[str, Any]) -> None:
    if resolution.get("artifact_type") != DOMAIN_WORKER_RESOLUTION_ARTIFACT_V1:
        raise FailClosedRuntimeError("provider proposal repair failed closed: invalid registry resolution")
    _verify_artifact_hash(resolution, "domain worker resolution")
    if resolution.get("resolution_status") != RESOLUTION_SUCCEEDED:
        raise FailClosedRuntimeError("provider proposal repair failed closed: domain or worker resolution failed")


def _validate_provider_policy(policy: dict[str, Any]) -> None:
    if policy.get("artifact_type") != PROVIDER_NECESSITY_POLICY_ARTIFACT_V1:
        raise FailClosedRuntimeError("provider proposal repair failed closed: invalid provider necessity evidence")
    _verify_artifact_hash(policy, "provider necessity policy")
    if policy.get("policy_status") != PROVIDER_NECESSITY_CLASSIFIED:
        raise FailClosedRuntimeError("provider proposal repair failed closed: provider necessity unclassified")
    if policy.get("necessity_classification") == PROVIDER_PROHIBITED:
        raise FailClosedRuntimeError("provider proposal repair failed closed: provider prohibited by policy")
    if policy.get("necessity_classification") != PROVIDER_REQUIRED:
        raise FailClosedRuntimeError("provider proposal repair failed closed: provider retry is not required by policy")


def _validate_retry_limit(value: int) -> int:
    if not isinstance(value, int) or value < 0 or value > MAX_PROVIDER_RETRIES:
        raise FailClosedRuntimeError("provider proposal repair failed closed: retry limit exceeded")
    return value


def _failure_from_validation(validation: dict[str, Any]) -> str:
    for key in ("failure_reason", "validation_reason", "reason"):
        value = validation.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "proposal validation failed"


def _repair_policy(*, failure_reason: str) -> str:
    lowered = failure_reason.lower()
    if any(marker in lowered for marker in AMBIGUITY_MARKERS):
        return HUMAN_CLARIFICATION_REQUIRED
    if any(marker in lowered for marker in RETRYABLE_MARKERS):
        return AUTO_RETRY
    return AUTO_RETRY


def _repair_request_artifact(
    *,
    repair_id: str,
    provider_id: str,
    proposal: dict[str, Any],
    validation: dict[str, Any],
    original_response: dict[str, Any],
    context: dict[str, Any],
    resolution: dict[str, Any],
    policy: dict[str, Any],
    canonical_chain_id: str,
    repair_policy: str,
    max_provider_retries: int,
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": PROVIDER_REPAIR_REQUEST_V1,
        "runtime_version": AIGOL_PROVIDER_PROPOSAL_REPAIR_AND_RETRY_RUNTIME_VERSION,
        "repair_id": _require_string(repair_id, "repair_id"),
        "provider_id": _require_string(provider_id, "provider_id"),
        "canonical_chain_id": _require_string(canonical_chain_id, "canonical_chain_id"),
        "repair_policy": repair_policy,
        "max_provider_retries": max_provider_retries,
        "rejected_proposal_reference": proposal.get("proposal_id"),
        "rejected_proposal_hash": proposal.get("artifact_hash"),
        "validation_failure_reference": validation.get("contract_validation_id"),
        "validation_failure_hash": validation.get("artifact_hash"),
        "validation_failure_reason": _failure_from_validation(validation),
        "provider_response_reference": original_response.get("production_id"),
        "provider_response_hash": original_response.get("artifact_hash"),
        "context_reference": context.get("context_assembly_id"),
        "context_hash": context.get("context_hash"),
        "domain_reference": resolution.get("domain_id"),
        "worker_reference": resolution.get("worker_family_id"),
        "milestone_reference": resolution.get("milestone_type"),
        "provider_necessity_reference": policy.get("policy_decision_id"),
        "provider_necessity_hash": policy.get("artifact_hash"),
        "retry_instructions": [
            "Return a corrected DEVELOPMENT_PROPOSAL_ARTIFACT_V1-compatible proposal payload.",
            "Correct only validation failures listed in the repair request.",
            "Do not authorize, govern, dispatch, execute, mutate replay, mutate governance, create workers, or create domains.",
        ],
        "created_at": _require_string(created_at, "created_at"),
        "proposal_only": True,
        "provider_authority": False,
        "worker_created": False,
        "domain_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "replay_visible": True,
    }
    artifact["provider_request_hash"] = replay_hash(
        {
            "repair_id": artifact["repair_id"],
            "rejected_proposal_hash": artifact["rejected_proposal_hash"],
            "validation_failure_hash": artifact["validation_failure_hash"],
            "context_hash": artifact["context_hash"],
            "repair_policy": artifact["repair_policy"],
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _retry_request_payload(request: dict[str, Any], attempt: int) -> dict[str, Any]:
    payload = deepcopy(request)
    payload["retry_attempt"] = attempt
    payload["retry_mode"] = AUTO_RETRY
    return payload


def _proposal_from_provider_capture(
    *,
    repair_id: str,
    attempt: int,
    provider_capture: dict[str, Any],
    context: dict[str, Any],
    resolution: dict[str, Any],
) -> dict[str, Any]:
    envelope = provider_capture.get("provider_proposal_envelope")
    returned = provider_capture.get("provider_proposal_returned")
    if not isinstance(envelope, dict) or not isinstance(returned, dict):
        raise FailClosedRuntimeError("provider proposal repair failed closed: provider response invalid")
    if returned.get("failure_reason"):
        raise FailClosedRuntimeError(returned["failure_reason"])
    response = envelope.get("response")
    if not isinstance(response, dict):
        raise FailClosedRuntimeError("provider proposal repair failed closed: provider response invalid")
    _assert_no_authority(response)
    outputs = _require_nonempty_string_list(response.get("proposed_outputs"), "proposed_outputs")
    if len(set(outputs)) != len(outputs):
        raise FailClosedRuntimeError("provider proposal repair failed closed: ambiguous provider result detected")
    proposal = {
        "artifact_type": DEVELOPMENT_PROPOSAL_ARTIFACT_V1,
        "proposal_id": f"{repair_id}:CORRECTED-DEVELOPMENT-PROPOSAL-{attempt:03d}",
        "corrected_artifact_type": CORRECTED_DEVELOPMENT_PROPOSAL_V1,
        "task_reference": context.get("development_task_intake_reference"),
        "context_reference": context.get("context_assembly_id"),
        "context_hash": context.get("context_hash"),
        "domain_reference": resolution.get("domain_id"),
        "worker_reference": resolution.get("worker_family_id"),
        "milestone_reference": resolution.get("milestone_type"),
        "proposal_summary": _require_string(response.get("proposal_summary"), "proposal_summary"),
        "proposed_outputs": outputs,
        "constraints_acknowledged": _require_string_list(
            response.get("constraints_acknowledged"), "constraints_acknowledged"
        ),
        "assumptions": _require_string_list(response.get("assumptions"), "assumptions"),
        "known_gaps": _require_string_list(response.get("known_gaps"), "known_gaps"),
        "proposal_only": True,
        "execution_authority": False,
        "dispatch_authority": False,
        "governance_authority": False,
        "replay_authority": False,
        "provider_authority": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "worker_created": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    proposal["artifact_hash"] = replay_hash(proposal)
    return proposal


def _retry_history_item(
    *,
    attempt: int,
    provider_capture: dict[str, Any],
    proposal: dict[str, Any],
    validation_capture: dict[str, Any],
) -> dict[str, Any]:
    return {
        "attempt": attempt,
        "provider_request_hash": _provider_request_hash(provider_capture),
        "provider_response_hash": _provider_response_hash(provider_capture),
        "proposal_hash": proposal.get("artifact_hash"),
        "validation_status": validation_capture.get("validation_status"),
        "retry_reason": validation_capture.get("failure_reason"),
    }


def _provider_request_hash(provider_capture: dict[str, Any]) -> str | None:
    created = provider_capture.get("provider_proposal_created") if isinstance(provider_capture, dict) else None
    if isinstance(created, dict):
        return created.get("artifact_hash")
    return None


def _provider_response_hash(provider_capture: dict[str, Any]) -> str | None:
    returned = provider_capture.get("provider_proposal_returned") if isinstance(provider_capture, dict) else None
    if isinstance(returned, dict):
        return returned.get("artifact_hash")
    return None


def _retry_response_artifact(
    *,
    repair_id: str,
    request: dict[str, Any],
    retry_history: list[dict[str, Any]],
    corrected_proposal: dict[str, Any] | None,
    escalation_artifact: dict[str, Any] | None,
    created_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": PROVIDER_RETRY_RESPONSE_V1,
        "runtime_version": AIGOL_PROVIDER_PROPOSAL_REPAIR_AND_RETRY_RUNTIME_VERSION,
        "repair_id": _require_string(repair_id, "repair_id"),
        "repair_request_hash": request.get("artifact_hash"),
        "retry_count": len(retry_history),
        "retry_history": deepcopy(retry_history),
        "corrected_proposal_reference": corrected_proposal.get("proposal_id") if corrected_proposal else None,
        "corrected_proposal_hash": corrected_proposal.get("artifact_hash") if corrected_proposal else None,
        "escalation_reference": escalation_artifact.get("artifact_type") if escalation_artifact else None,
        "escalation_hash": escalation_artifact.get("artifact_hash") if escalation_artifact else None,
        "created_at": _require_string(created_at, "created_at"),
        "proposal_only": True,
        "provider_authority": False,
        "worker_created": False,
        "domain_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _retry_status_artifact(
    *,
    repair_id: str,
    request: dict[str, Any],
    retry_response: dict[str, Any],
    corrected_proposal: dict[str, Any] | None,
    status: str,
    retry_count: int,
    retry_history: list[dict[str, Any]],
    clarification_artifact: dict[str, Any] | None,
    approval_artifact: dict[str, Any] | None,
    created_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": RETRY_STATUS_ARTIFACT_V1,
        "runtime_version": AIGOL_PROVIDER_PROPOSAL_REPAIR_AND_RETRY_RUNTIME_VERSION,
        "retry_status_id": f"{_require_string(repair_id, 'repair_id')}:RETRY-STATUS",
        "repair_id": repair_id,
        "retry_status": status,
        "repair_request_hash": request.get("artifact_hash"),
        "retry_response_hash": retry_response.get("artifact_hash"),
        "retry_count": retry_count,
        "retry_history": deepcopy(retry_history),
        "corrected_proposal_reference": corrected_proposal.get("proposal_id") if corrected_proposal else None,
        "corrected_proposal_hash": corrected_proposal.get("artifact_hash") if corrected_proposal else None,
        "clarification_required": clarification_artifact is not None,
        "clarification_request_hash": clarification_artifact.get("artifact_hash") if clarification_artifact else None,
        "human_clarification_required_artifact": deepcopy(clarification_artifact),
        "approval_required": approval_artifact is not None,
        "approval_request_hash": approval_artifact.get("artifact_hash") if approval_artifact else None,
        "human_approval_required_artifact": deepcopy(approval_artifact),
        "canonical_chain_id": request.get("canonical_chain_id"),
        "created_at": _require_string(created_at, "created_at"),
        "proposal_only": True,
        "provider_authority": False,
        "worker_created": False,
        "domain_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_status_artifact(
    *,
    repair_id: str,
    provider_id: str,
    request: dict[str, Any] | None,
    retry_response: dict[str, Any] | None,
    canonical_chain_id: str,
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": RETRY_STATUS_ARTIFACT_V1,
        "runtime_version": AIGOL_PROVIDER_PROPOSAL_REPAIR_AND_RETRY_RUNTIME_VERSION,
        "retry_status_id": f"{repair_id}:RETRY-STATUS" if isinstance(repair_id, str) else "INVALID_REPAIR_ID:RETRY-STATUS",
        "repair_id": repair_id if isinstance(repair_id, str) else "INVALID_REPAIR_ID",
        "provider_id": provider_id if isinstance(provider_id, str) else "INVALID_PROVIDER_ID",
        "retry_status": FAILED_CLOSED,
        "repair_request_hash": request.get("artifact_hash") if request else None,
        "retry_response_hash": retry_response.get("artifact_hash") if retry_response else None,
        "retry_count": len(retry_response.get("retry_history", [])) if retry_response else 0,
        "retry_history": deepcopy(retry_response.get("retry_history", [])) if retry_response else [],
        "corrected_proposal_reference": None,
        "corrected_proposal_hash": None,
        "clarification_required": False,
        "clarification_request_hash": None,
        "human_clarification_required_artifact": None,
        "approval_required": False,
        "approval_request_hash": None,
        "human_approval_required_artifact": None,
        "canonical_chain_id": canonical_chain_id if isinstance(canonical_chain_id, str) else None,
        "created_at": created_at if isinstance(created_at, str) else "INVALID_TIMESTAMP",
        "proposal_only": True,
        "provider_authority": False,
        "worker_created": False,
        "domain_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _human_clarification_artifact(
    *,
    repair_id: str,
    request: dict[str, Any],
    reason: str,
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": HUMAN_CLARIFICATION_REQUIRED_ARTIFACT_V1,
        "repair_id": repair_id,
        "repair_request_hash": request["artifact_hash"],
        "clarification_reason": reason,
        "clarification_prompt": "Human clarification is required before provider retry can continue.",
        "created_at": created_at,
        "proposal_only": True,
        "provider_authority": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _human_approval_artifact(
    *,
    repair_id: str,
    request: dict[str, Any],
    corrected_proposal: dict[str, Any],
    validation_capture: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": HUMAN_APPROVAL_REQUIRED_ARTIFACT_V1,
        "repair_id": repair_id,
        "repair_request_hash": request["artifact_hash"],
        "corrected_proposal_reference": corrected_proposal["proposal_id"],
        "corrected_proposal_hash": corrected_proposal["artifact_hash"],
        "validation_status": validation_capture.get("validation_status"),
        "approval_reason": "High-risk domain requires human approval before continuing.",
        "created_at": created_at,
        "proposal_only": True,
        "provider_authority": False,
        "implementation_authorized": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_retry_response(repair_id: str, created_at: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": PROVIDER_RETRY_RESPONSE_V1,
        "runtime_version": AIGOL_PROVIDER_PROPOSAL_REPAIR_AND_RETRY_RUNTIME_VERSION,
        "repair_id": repair_id if isinstance(repair_id, str) else "INVALID_REPAIR_ID",
        "repair_request_hash": None,
        "retry_count": 0,
        "retry_history": [],
        "corrected_proposal_reference": None,
        "corrected_proposal_hash": None,
        "escalation_reference": None,
        "escalation_hash": None,
        "created_at": created_at if isinstance(created_at, str) else "INVALID_TIMESTAMP",
        "proposal_only": True,
        "provider_authority": False,
        "worker_created": False,
        "domain_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "replay_visible": True,
        "failure_reason": "provider retry failed closed",
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(status: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(status, "provider proposal repair retry status")
    artifact = {
        "event_type": "PROVIDER_PROPOSAL_REPAIR_RETRY_RETURNED",
        "retry_status_reference": status["retry_status_id"],
        "retry_status_hash": status["artifact_hash"],
        "repair_id": status["repair_id"],
        "retry_status": status["retry_status"],
        "retry_count": status["retry_count"],
        "corrected_proposal_hash": status["corrected_proposal_hash"],
        "clarification_required": status["clarification_required"],
        "human_clarification_required_artifact": deepcopy(status.get("human_clarification_required_artifact")),
        "approval_required": status["approval_required"],
        "human_approval_required_artifact": deepcopy(status.get("human_approval_required_artifact")),
        "canonical_chain_id": status["canonical_chain_id"],
        "proposal_only": True,
        "provider_authority": False,
        "worker_created": False,
        "domain_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "failure_reason": status["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    request: dict[str, Any] | None,
    retry_response: dict[str, Any],
    status: dict[str, Any],
    returned: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "provider_repair_request": deepcopy(request),
        "provider_retry_response": deepcopy(retry_response),
        "retry_status_artifact": deepcopy(status),
        "provider_repair_retry_replay": deepcopy(returned),
        "provider_repair_retry_replay_reference": str(replay_path),
        "repair_id": status["repair_id"],
        "retry_status": status["retry_status"],
        "retry_count": status["retry_count"],
        "retry_history": deepcopy(status["retry_history"]),
        "corrected_proposal_hash": status["corrected_proposal_hash"],
        "clarification_required": status["clarification_required"],
        "approval_required": status["approval_required"],
        "canonical_chain_id": status["canonical_chain_id"],
        "fail_closed": status["retry_status"] == FAILED_CLOSED,
        "failure_reason": status["failure_reason"],
        "proposal_only": True,
        "provider_authority": False,
        "worker_created": False,
        "domain_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
    }
    capture["provider_proposal_repair_retry_capture_hash"] = replay_hash(capture)
    return capture


def _is_high_risk_domain(domain_id: str) -> bool:
    return domain_id.upper() in HIGH_RISK_DOMAINS


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("provider proposal repair retry replay step ordering mismatch")
    _verify_artifact_hash(artifact, "provider proposal repair retry artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "event_type": step.upper(),
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_sequence(
    replay_path: Path,
    request: Any,
    retry_response: dict[str, Any],
    status: dict[str, Any],
    returned: dict[str, Any],
) -> None:
    fallback_request = request if isinstance(request, dict) else _failure_step_artifact("PROVIDER_REPAIR_REQUEST_FAILED")
    _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], fallback_request)
    _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], retry_response)
    _persist_failure_if_possible(replay_path, 2, REPLAY_STEPS[2], status)
    _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], returned)


def _persist_failure_if_possible(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    try:
        _persist_step(replay_dir, index, step, artifact)
    except FailClosedRuntimeError:
        pass


def _failure_step_artifact(event_type: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": event_type,
        "runtime_version": AIGOL_PROVIDER_PROPOSAL_REPAIR_AND_RETRY_RUNTIME_VERSION,
        "event_type": FAILED_CLOSED,
        "replay_visible": True,
        "artifact_hash": "",
    }
    artifact["artifact_hash"] = replay_hash({key: value for key, value in artifact.items() if key != "artifact_hash"})
    return artifact


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} must be a JSON object")
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError(f"{label} hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("provider proposal repair retry replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("provider proposal repair retry replay hash mismatch")


def _assert_no_authority(value: Any) -> None:
    if isinstance(value, dict):
        for field in FORBIDDEN_AUTHORITY_FIELDS:
            if value.get(field) is True:
                raise FailClosedRuntimeError("provider proposal repair failed closed: authority violation detected")
        for nested in value.values():
            _assert_no_authority(nested)
    elif isinstance(value, list):
        for nested in value:
            _assert_no_authority(nested)


def _require_nonempty_string_list(value: Any, field_name: str) -> list[str]:
    items = _require_string_list(value, field_name)
    if not items:
        raise FailClosedRuntimeError(f"{field_name} is required")
    return items


def _require_string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list):
        raise FailClosedRuntimeError(f"{field_name} is required")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise FailClosedRuntimeError(f"{field_name} must contain strings")
    return list(value)


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "provider proposal repair failed closed"
