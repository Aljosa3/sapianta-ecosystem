"""Multi-provider cognition runtime without comparison."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Callable

from aigol.runtime.cognition_artifact_runtime import (
    LLM_COGNITION_ARTIFACT_V1,
    run_cognition_artifact_runtime,
)
from aigol.runtime.llm_cognition_provider_runtime import (
    COGNITION_PROVIDER_ROLE,
    LLM_COGNITION_PROVIDER_REQUEST_ARTIFACT_V1,
    LLM_COGNITION_PROVIDER_RESPONSE_ARTIFACT_V1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.ocs_context_assembly_runtime import (
    OCS_CONTEXT_ASSEMBLED,
    OCS_CONTEXT_ASSEMBLY_ARTIFACT_V1,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_MULTI_PROVIDER_COGNITION_RUNTIME_V1"
FINAL_CLASSIFICATION = "AIGOL_MULTI_PROVIDER_COGNITION_RUNTIME_STATUS"
CERTIFIED_CLASSIFICATION = "CERTIFIED_MULTI_PROVIDER_COGNITION_RUNTIME"

MULTI_PROVIDER_COGNITION_REQUEST_BUNDLE_V1 = "MULTI_PROVIDER_COGNITION_REQUEST_BUNDLE_V1"
MULTI_PROVIDER_COGNITION_RESULT_BUNDLE_V1 = "MULTI_PROVIDER_COGNITION_RESULT_BUNDLE_V1"
PROVIDER_COGNITION_FAILURE_ARTIFACT_V1 = "PROVIDER_COGNITION_FAILURE_ARTIFACT_V1"

STATUS_COMPLETED = "COMPLETED"
STATUS_FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "multi_provider_cognition_request_bundle",
    "multi_provider_cognition_result_bundle",
)

AUTHORITY_FLAGS = {
    "provider_authority": False,
    "approval_authority": False,
    "execution_authority": False,
    "worker_authority": False,
    "governance_authority": False,
    "replay_authority": False,
}

ProviderTransport = Callable[[dict[str, Any], dict[str, Any]], Any]


def run_multi_provider_cognition_runtime(
    *,
    multi_provider_cognition_bundle_id: str,
    human_request: str,
    ocs_context_artifact: dict[str, Any],
    provider_contracts: list[dict[str, Any]],
    created_at: str,
    replay_dir: str | Path,
    transport_registry: dict[str, ProviderTransport],
) -> dict[str, Any]:
    """Invoke multiple approved cognition providers under one OCS context."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        context = _validate_ocs_context_artifact(ocs_context_artifact)
        contracts = _normalize_provider_contract_inputs(provider_contracts)
        valid_contracts: list[dict[str, Any]] = []
        request_artifacts: list[dict[str, Any]] = []
        initial_provider_failures: list[dict[str, Any]] = []
        for contract in contracts:
            provider_id = contract["provider_id"]
            try:
                valid_contract = _validate_provider_contract(contract)
                valid_contracts.append(valid_contract)
                request_artifacts.append(
                    _create_provider_request_artifact(
                        multi_provider_cognition_bundle_id=multi_provider_cognition_bundle_id,
                        human_request=human_request,
                        ocs_context_artifact=context,
                        provider_contract=valid_contract,
                        created_at=created_at,
                    )
                )
            except Exception as exc:
                initial_provider_failures.append(
                    _provider_failure_artifact(
                        multi_provider_cognition_bundle_id=multi_provider_cognition_bundle_id,
                        provider_id=provider_id,
                        context_hash=context["context_hash"],
                        provider_contract_hash=contract.get("artifact_hash"),
                        request_artifact_hash=None,
                        failed_stage="PROVIDER_CONTRACT_VALIDATION",
                        failure_reason=str(exc)
                        if isinstance(exc, FailClosedRuntimeError)
                        else "provider contract validation failed closed",
                        created_at=created_at,
                    )
                )
        request_bundle = _create_request_bundle(
            multi_provider_cognition_bundle_id=multi_provider_cognition_bundle_id,
            human_request=human_request,
            ocs_context_artifact=context,
            provider_contracts=contracts,
            provider_request_artifacts=request_artifacts,
            created_at=created_at,
        )
        _persist_step(replay_path, 0, REPLAY_STEPS[0], request_bundle)
        result_bundle = _process_provider_requests(
            multi_provider_cognition_bundle_id=multi_provider_cognition_bundle_id,
            request_bundle=request_bundle,
            ocs_context_artifact=context,
            provider_contracts=valid_contracts,
            provider_request_artifacts=request_artifacts,
            initial_provider_failures=initial_provider_failures,
            created_at=created_at,
            replay_path=replay_path,
            transport_registry=transport_registry,
        )
        _persist_step(replay_path, 1, REPLAY_STEPS[1], result_bundle)
        return _capture(
            final_status=STATUS_COMPLETED,
            request_bundle=request_bundle,
            result_bundle=result_bundle,
            replay_path=replay_path,
            failure_reason="",
        )
    except Exception as exc:
        failure_reason = str(exc) if isinstance(exc, FailClosedRuntimeError) else "multi-provider cognition failed closed"
        failure_bundle = _top_level_failure_bundle(
            multi_provider_cognition_bundle_id=(
                multi_provider_cognition_bundle_id
                if _is_nonempty_string(multi_provider_cognition_bundle_id)
                else "MULTI-PROVIDER-COGNITION-INVALID"
            ),
            created_at=created_at if _is_nonempty_string(created_at) else "1970-01-01T00:00:00Z",
            failure_reason=failure_reason,
        )
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], failure_bundle)
        return _capture(
            final_status=STATUS_FAILED_CLOSED,
            request_bundle=None,
            result_bundle=failure_bundle,
            replay_path=replay_path,
            failure_reason=failure_reason,
        )


def create_default_cognition_provider_contract(
    *,
    provider_id: str,
    provider_label: str | None = None,
    provider_schema_id: str = "mock.cognition.v1",
    created_at: str = "1970-01-01T00:00:00Z",
) -> dict[str, Any]:
    """Create an approved cognition-provider contract for deterministic tests."""

    provider = _normalize_provider_id(provider_id)
    artifact = {
        "artifact_type": "MULTI_PROVIDER_COGNITION_PROVIDER_CONTRACT_V1",
        "contract_reference": "AIGOL_LLM_COGNITION_PROVIDER_CONTRACT_V1",
        "provider_id": provider,
        "provider_role": COGNITION_PROVIDER_ROLE,
        "provider_approved": True,
        "provider_schema_id": _require_string(provider_schema_id, "provider_schema_id"),
        "provider_identity": {
            "provider_id": provider,
            "provider_label": provider_label or provider.upper(),
            "provider_kind": "external_llm",
        },
        "authority_model": deepcopy(AUTHORITY_FLAGS),
        "allowed_outputs": [
            "findings",
            "assumptions",
            "alternatives",
            "risks",
            "uncertainties",
            "confidence statements",
            "clarification candidates",
        ],
        "single_provider_only": False,
        "multi_provider_cognition_scope": True,
        "replay_visible": True,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def reconstruct_multi_provider_cognition_replay(replay_dir: str | Path) -> dict[str, Any]:
    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("multi-provider cognition replay ordering mismatch")
        _verify_replay_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("multi-provider cognition replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "multi-provider cognition replay artifact")
        wrappers.append(wrapper)
    request_bundle = wrappers[0]["artifact"]
    result_bundle = wrappers[1]["artifact"]
    if result_bundle.get("request_bundle_hash") != request_bundle["artifact_hash"]:
        raise FailClosedRuntimeError("multi-provider cognition request bundle hash mismatch")
    for request_artifact in request_bundle.get("provider_request_artifacts", []):
        _verify_artifact_hash(request_artifact, "provider request artifact")
    for result in result_bundle.get("provider_results", []):
        _verify_provider_success_result(result)
    for failure in result_bundle.get("provider_failures", []):
        _verify_artifact_hash(failure, "provider cognition failure artifact")
    return {
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "classification": result_bundle.get("classification"),
        "final_status": result_bundle.get("bundle_status"),
        "multi_provider_cognition_bundle_id": result_bundle.get("multi_provider_cognition_bundle_id"),
        "context_hash": result_bundle.get("context_hash"),
        "provider_count": result_bundle.get("provider_count"),
        "successful_provider_count": result_bundle.get("successful_provider_count"),
        "failed_provider_count": result_bundle.get("failed_provider_count"),
        "cognition_artifact_hashes": deepcopy(result_bundle.get("cognition_artifact_hashes", [])),
        "provider_failure_hashes": deepcopy(result_bundle.get("provider_failure_hashes", [])),
        "comparison_performed": result_bundle.get("comparison_performed") is True,
        "confidence_aggregation_performed": result_bundle.get("confidence_aggregation_performed") is True,
        "replay_visible": True,
        "append_only_valid": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def render_multi_provider_cognition_summary(result: dict[str, Any]) -> str:
    bundle = result.get("result_bundle") or {}
    return "\n".join(
        [
            "AIGOL MULTI-PROVIDER COGNITION RUNTIME",
            f"status: {result.get('final_status')}",
            f"classification: {result.get('classification')}",
            f"bundle_id: {result.get('multi_provider_cognition_bundle_id')}",
            f"provider_count: {bundle.get('provider_count')}",
            f"successful_provider_count: {bundle.get('successful_provider_count')}",
            f"failed_provider_count: {bundle.get('failed_provider_count')}",
            f"comparison_performed: {bundle.get('comparison_performed')}",
            f"replay_reference: {result.get('replay_reference')}",
            f"fail_closed: {result.get('fail_closed')}",
            f"failure_reason: {result.get('failure_reason') or ''}",
        ]
    )


def _process_provider_requests(
    *,
    multi_provider_cognition_bundle_id: str,
    request_bundle: dict[str, Any],
    ocs_context_artifact: dict[str, Any],
    provider_contracts: list[dict[str, Any]],
    provider_request_artifacts: list[dict[str, Any]],
    initial_provider_failures: list[dict[str, Any]],
    created_at: str,
    replay_path: Path,
    transport_registry: dict[str, ProviderTransport],
) -> dict[str, Any]:
    provider_results: list[dict[str, Any]] = []
    provider_failures: list[dict[str, Any]] = deepcopy(initial_provider_failures)
    contract_by_id = {contract["provider_id"]: contract for contract in provider_contracts}
    for request_artifact in provider_request_artifacts:
        provider_id = request_artifact["provider_id"]
        try:
            response_artifact = _invoke_provider_request(
                request_artifact=request_artifact,
                provider_contract=contract_by_id[provider_id],
                transport_registry=transport_registry,
            )
            artifact_capture = run_cognition_artifact_runtime(
                cognition_artifact_id=f"{multi_provider_cognition_bundle_id}:{provider_id}:LLM_COGNITION_ARTIFACT",
                ocs_context_artifact=ocs_context_artifact,
                provider_request_artifact=request_artifact,
                provider_response_artifact=response_artifact,
                created_at=created_at,
                replay_dir=replay_path / "providers" / provider_id / "cognition_artifact",
            )
            if artifact_capture["fail_closed"] is True:
                raise FailClosedRuntimeError(artifact_capture["failure_reason"])
            cognition_artifact = artifact_capture["llm_cognition_artifact"]
            provider_results.append(
                _provider_success_result(
                    provider_id=provider_id,
                    request_artifact=request_artifact,
                    response_artifact=response_artifact,
                    cognition_artifact=cognition_artifact,
                    cognition_replay_reference=artifact_capture["replay_reference"],
                )
            )
        except Exception as exc:
            provider_failures.append(
                _provider_failure_artifact(
                    multi_provider_cognition_bundle_id=multi_provider_cognition_bundle_id,
                    provider_id=provider_id,
                    context_hash=ocs_context_artifact["context_hash"],
                    provider_contract_hash=contract_by_id.get(provider_id, {}).get("artifact_hash"),
                    request_artifact_hash=request_artifact.get("artifact_hash"),
                    failed_stage="PROVIDER_COGNITION_PROCESSING",
                    failure_reason=str(exc)
                    if isinstance(exc, FailClosedRuntimeError)
                    else "provider cognition processing failed closed",
                    created_at=created_at,
                )
            )
    return _create_result_bundle(
        multi_provider_cognition_bundle_id=multi_provider_cognition_bundle_id,
        request_bundle=request_bundle,
        ocs_context_artifact=ocs_context_artifact,
        provider_results=provider_results,
        provider_failures=provider_failures,
        created_at=created_at,
    )


def _create_provider_request_artifact(
    *,
    multi_provider_cognition_bundle_id: str,
    human_request: str,
    ocs_context_artifact: dict[str, Any],
    provider_contract: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    provider_id = provider_contract["provider_id"]
    prompt = _provider_prompt(human_request=human_request, context=ocs_context_artifact, provider_id=provider_id)
    artifact = {
        "artifact_type": LLM_COGNITION_PROVIDER_REQUEST_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "multi_provider_cognition_bundle_id": _require_string(
            multi_provider_cognition_bundle_id, "multi_provider_cognition_bundle_id"
        ),
        "cognition_provider_request_id": f"{multi_provider_cognition_bundle_id}:{provider_id}:REQUEST",
        "provider_id": provider_id,
        "provider_role": COGNITION_PROVIDER_ROLE,
        "provider_schema_id": provider_contract["provider_schema_id"],
        "provider_identity": deepcopy(provider_contract["provider_identity"]),
        "request": {
            "human_request": _require_string(human_request, "human_request"),
            "human_request_hash": replay_hash(human_request),
            "input": prompt,
            "input_hash": replay_hash(prompt),
            "streaming": False,
            "tool_use": False,
            "function_calling": False,
            "automatic_retries": False,
        },
        "ocs_context_reference": {
            "context_assembly_id": ocs_context_artifact["context_assembly_id"],
            "context_hash": ocs_context_artifact["context_hash"],
            "context_artifact_hash": ocs_context_artifact["artifact_hash"],
            "context_status": ocs_context_artifact["context_status"],
        },
        "provider_contract_hash": provider_contract["artifact_hash"],
        "lineage_refs": {
            "human_request_hash": replay_hash(human_request),
            "ocs_context_hash": ocs_context_artifact["context_hash"],
            "ocs_context_artifact_hash": ocs_context_artifact["artifact_hash"],
            "provider_contract_hash": provider_contract["artifact_hash"],
        },
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["request_hash"] = replay_hash(
        {
            "multi_provider_cognition_bundle_id": artifact["multi_provider_cognition_bundle_id"],
            "cognition_provider_request_id": artifact["cognition_provider_request_id"],
            "provider_id": artifact["provider_id"],
            "provider_role": artifact["provider_role"],
            "provider_schema_id": artifact["provider_schema_id"],
            "provider_identity": artifact["provider_identity"],
            "request": artifact["request"],
            "ocs_context_reference": artifact["ocs_context_reference"],
            "provider_contract_hash": artifact["provider_contract_hash"],
            "lineage_refs": artifact["lineage_refs"],
            "authority_flags": artifact["authority_flags"],
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _invoke_provider_request(
    *,
    request_artifact: dict[str, Any],
    provider_contract: dict[str, Any],
    transport_registry: dict[str, ProviderTransport],
) -> dict[str, Any]:
    provider_id = request_artifact["provider_id"]
    transport = transport_registry.get(provider_id)
    if transport is None:
        raise FailClosedRuntimeError("provider transport is not registered")
    payload = {
        "provider_id": provider_id,
        "input": request_artifact["request"]["input"],
        "stream": False,
    }
    metadata = {
        "provider_id": provider_id,
        "provider_role": COGNITION_PROVIDER_ROLE,
        "provider_identity": deepcopy(provider_contract["provider_identity"]),
        "provider_schema_id": provider_contract["provider_schema_id"],
    }
    raw_response = _json_safe(transport(deepcopy(payload), deepcopy(metadata)))
    response_text = _extract_response_text(raw_response)
    artifact = {
        "artifact_type": LLM_COGNITION_PROVIDER_RESPONSE_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "multi_provider_cognition_bundle_id": request_artifact["multi_provider_cognition_bundle_id"],
        "cognition_provider_request_id": request_artifact["cognition_provider_request_id"],
        "provider_id": provider_id,
        "provider_role": COGNITION_PROVIDER_ROLE,
        "provider_schema_id": request_artifact["provider_schema_id"],
        "provider_identity": deepcopy(request_artifact["provider_identity"]),
        "provider_metadata": {
            "provider_schema_id": request_artifact["provider_schema_id"],
            "provider_id": provider_id,
            "streaming": False,
            "tool_use": False,
            "function_calling": False,
            "automatic_retries": False,
            "failure_isolated": True,
        },
        "provider_request_hash": request_artifact["artifact_hash"],
        "request_hash": request_artifact["request_hash"],
        "ocs_context_hash": request_artifact["ocs_context_reference"]["context_hash"],
        "raw_response": raw_response,
        "raw_response_hash": replay_hash(raw_response),
        "response_text": response_text,
        "response_text_hash": replay_hash(response_text),
        "response_status": "CAPTURED",
        "untrusted_provider_output": True,
        "non_authoritative": True,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "lineage_refs": {
            "llm_cognition_provider_request_hash": request_artifact["artifact_hash"],
            "request_hash": request_artifact["request_hash"],
            "ocs_context_hash": request_artifact["ocs_context_reference"]["context_hash"],
            "ocs_context_artifact_hash": request_artifact["ocs_context_reference"]["context_artifact_hash"],
            "provider_contract_hash": request_artifact["provider_contract_hash"],
        },
        "replay_visible": True,
        "provider_invoked": True,
        "worker_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    artifact["response_hash"] = replay_hash(
        {
            "cognition_provider_request_id": artifact["cognition_provider_request_id"],
            "provider_id": artifact["provider_id"],
            "provider_role": artifact["provider_role"],
            "provider_schema_id": artifact["provider_schema_id"],
            "provider_identity": artifact["provider_identity"],
            "provider_metadata": artifact["provider_metadata"],
            "provider_request_hash": artifact["provider_request_hash"],
            "request_hash": artifact["request_hash"],
            "ocs_context_hash": artifact["ocs_context_hash"],
            "raw_response_hash": artifact["raw_response_hash"],
            "response_text_hash": artifact["response_text_hash"],
            "response_status": artifact["response_status"],
            "untrusted_provider_output": artifact["untrusted_provider_output"],
            "non_authoritative": artifact["non_authoritative"],
            "authority_flags": artifact["authority_flags"],
            "lineage_refs": artifact["lineage_refs"],
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _create_request_bundle(
    *,
    multi_provider_cognition_bundle_id: str,
    human_request: str,
    ocs_context_artifact: dict[str, Any],
    provider_contracts: list[dict[str, Any]],
    provider_request_artifacts: list[dict[str, Any]],
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": MULTI_PROVIDER_COGNITION_REQUEST_BUNDLE_V1,
        "runtime_version": MILESTONE_ID,
        "classification": CERTIFIED_CLASSIFICATION,
        "multi_provider_cognition_bundle_id": _require_string(
            multi_provider_cognition_bundle_id, "multi_provider_cognition_bundle_id"
        ),
        "human_request": _require_string(human_request, "human_request"),
        "human_request_hash": replay_hash(human_request),
        "context_hash": ocs_context_artifact["context_hash"],
        "ocs_context_artifact_hash": ocs_context_artifact["artifact_hash"],
        "provider_count": len(provider_contracts),
        "provider_contract_hashes": [contract["artifact_hash"] for contract in provider_contracts],
        "provider_request_artifact_hashes": [request["artifact_hash"] for request in provider_request_artifacts],
        "provider_request_artifacts": deepcopy(provider_request_artifacts),
        "deterministic_provider_order": [contract["provider_id"] for contract in provider_contracts],
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "replay_visible": True,
        "comparison_performed": False,
        "confidence_aggregation_performed": False,
        "worker_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["bundle_hash"] = replay_hash(
        {
            "multi_provider_cognition_bundle_id": artifact["multi_provider_cognition_bundle_id"],
            "human_request_hash": artifact["human_request_hash"],
            "context_hash": artifact["context_hash"],
            "provider_contract_hashes": artifact["provider_contract_hashes"],
            "provider_request_artifact_hashes": artifact["provider_request_artifact_hashes"],
            "deterministic_provider_order": artifact["deterministic_provider_order"],
            "authority_flags": artifact["authority_flags"],
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _create_result_bundle(
    *,
    multi_provider_cognition_bundle_id: str,
    request_bundle: dict[str, Any],
    ocs_context_artifact: dict[str, Any],
    provider_results: list[dict[str, Any]],
    provider_failures: list[dict[str, Any]],
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": MULTI_PROVIDER_COGNITION_RESULT_BUNDLE_V1,
        "runtime_version": MILESTONE_ID,
        "classification": CERTIFIED_CLASSIFICATION,
        "bundle_status": STATUS_COMPLETED,
        "multi_provider_cognition_bundle_id": multi_provider_cognition_bundle_id,
        "request_bundle_hash": request_bundle["artifact_hash"],
        "context_hash": ocs_context_artifact["context_hash"],
        "provider_count": request_bundle["provider_count"],
        "successful_provider_count": len(provider_results),
        "failed_provider_count": len(provider_failures),
        "provider_results": deepcopy(provider_results),
        "provider_failures": deepcopy(provider_failures),
        "cognition_artifact_hashes": [result["cognition_artifact_hash"] for result in provider_results],
        "provider_failure_hashes": [failure["artifact_hash"] for failure in provider_failures],
        "failure_isolated": True,
        "comparison_performed": False,
        "confidence_aggregation_performed": False,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "replay_visible": True,
        "worker_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["result_bundle_hash"] = replay_hash(
        {
            "multi_provider_cognition_bundle_id": artifact["multi_provider_cognition_bundle_id"],
            "request_bundle_hash": artifact["request_bundle_hash"],
            "context_hash": artifact["context_hash"],
            "provider_count": artifact["provider_count"],
            "successful_provider_count": artifact["successful_provider_count"],
            "failed_provider_count": artifact["failed_provider_count"],
            "cognition_artifact_hashes": artifact["cognition_artifact_hashes"],
            "provider_failure_hashes": artifact["provider_failure_hashes"],
            "comparison_performed": artifact["comparison_performed"],
            "confidence_aggregation_performed": artifact["confidence_aggregation_performed"],
            "authority_flags": artifact["authority_flags"],
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _provider_success_result(
    *,
    provider_id: str,
    request_artifact: dict[str, Any],
    response_artifact: dict[str, Any],
    cognition_artifact: dict[str, Any],
    cognition_replay_reference: str,
) -> dict[str, Any]:
    if cognition_artifact.get("artifact_type") != LLM_COGNITION_ARTIFACT_V1:
        raise FailClosedRuntimeError("provider cognition artifact is invalid")
    _verify_artifact_hash(cognition_artifact, "provider cognition artifact")
    return {
        "provider_id": provider_id,
        "provider_status": STATUS_COMPLETED,
        "provider_request_artifact": deepcopy(request_artifact),
        "provider_response_artifact": deepcopy(response_artifact),
        "llm_cognition_artifact": deepcopy(cognition_artifact),
        "provider_request_artifact_hash": request_artifact["artifact_hash"],
        "provider_response_artifact_hash": response_artifact["artifact_hash"],
        "cognition_artifact_hash": cognition_artifact["artifact_hash"],
        "cognition_replay_reference": cognition_replay_reference,
        "comparison_performed": False,
        "confidence_aggregation_performed": False,
    }


def _provider_failure_artifact(
    *,
    multi_provider_cognition_bundle_id: str,
    provider_id: str,
    context_hash: str,
    provider_contract_hash: str | None,
    request_artifact_hash: str | None,
    failed_stage: str,
    failure_reason: str,
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": PROVIDER_COGNITION_FAILURE_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "multi_provider_cognition_bundle_id": multi_provider_cognition_bundle_id,
        "provider_id": provider_id,
        "provider_status": STATUS_FAILED_CLOSED,
        "context_hash": context_hash,
        "provider_contract_hash": provider_contract_hash,
        "request_artifact_hash": request_artifact_hash,
        "failed_stage": failed_stage,
        "failure_reason": failure_reason,
        "failure_isolated": True,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _top_level_failure_bundle(*, multi_provider_cognition_bundle_id: str, created_at: str, failure_reason: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": MULTI_PROVIDER_COGNITION_RESULT_BUNDLE_V1,
        "runtime_version": MILESTONE_ID,
        "classification": CERTIFIED_CLASSIFICATION,
        "bundle_status": STATUS_FAILED_CLOSED,
        "multi_provider_cognition_bundle_id": multi_provider_cognition_bundle_id,
        "request_bundle_hash": None,
        "context_hash": None,
        "provider_count": 0,
        "successful_provider_count": 0,
        "failed_provider_count": 0,
        "provider_results": [],
        "provider_failures": [],
        "cognition_artifact_hashes": [],
        "provider_failure_hashes": [],
        "failure_reason": failure_reason,
        "failure_isolated": False,
        "comparison_performed": False,
        "confidence_aggregation_performed": False,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "replay_visible": True,
        "worker_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "created_at": created_at,
    }
    artifact["result_bundle_hash"] = replay_hash(
        {
            "multi_provider_cognition_bundle_id": artifact["multi_provider_cognition_bundle_id"],
            "request_bundle_hash": artifact["request_bundle_hash"],
            "context_hash": artifact["context_hash"],
            "provider_count": artifact["provider_count"],
            "successful_provider_count": artifact["successful_provider_count"],
            "failed_provider_count": artifact["failed_provider_count"],
            "cognition_artifact_hashes": artifact["cognition_artifact_hashes"],
            "provider_failure_hashes": artifact["provider_failure_hashes"],
            "comparison_performed": artifact["comparison_performed"],
            "confidence_aggregation_performed": artifact["confidence_aggregation_performed"],
            "authority_flags": artifact["authority_flags"],
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    *,
    final_status: str,
    request_bundle: dict[str, Any] | None,
    result_bundle: dict[str, Any],
    replay_path: Path,
    failure_reason: str,
) -> dict[str, Any]:
    result = {
        "command": "aigol multi-provider cognition run",
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "classification": CERTIFIED_CLASSIFICATION,
        "final_status": final_status,
        "multi_provider_cognition_bundle_id": result_bundle.get("multi_provider_cognition_bundle_id"),
        "request_bundle": deepcopy(request_bundle),
        "result_bundle": deepcopy(result_bundle),
        "provider_results": deepcopy(result_bundle.get("provider_results", [])),
        "provider_failures": deepcopy(result_bundle.get("provider_failures", [])),
        "successful_provider_count": result_bundle.get("successful_provider_count"),
        "failed_provider_count": result_bundle.get("failed_provider_count"),
        "comparison_performed": result_bundle.get("comparison_performed") is True,
        "confidence_aggregation_performed": result_bundle.get("confidence_aggregation_performed") is True,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "replay_reference": str(replay_path),
        "worker_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "fail_closed": final_status != STATUS_COMPLETED,
        "failure_reason": failure_reason,
    }
    result["multi_provider_cognition_runtime_hash"] = replay_hash(result)
    return result


def _normalize_provider_contract_inputs(provider_contracts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(provider_contracts, list) or not provider_contracts:
        raise FailClosedRuntimeError("at least one cognition provider contract is required")
    contracts: list[dict[str, Any]] = []
    for contract in provider_contracts:
        if not isinstance(contract, dict):
            raise FailClosedRuntimeError("provider contract must be a JSON object")
        _verify_artifact_hash(contract, "provider contract")
        normalized = deepcopy(contract)
        normalized["provider_id"] = _normalize_provider_id(normalized.get("provider_id"))
        contracts.append(normalized)
    provider_ids = [contract["provider_id"] for contract in contracts]
    if len(provider_ids) != len(set(provider_ids)):
        raise FailClosedRuntimeError("duplicate cognition provider ids are not allowed")
    return sorted(contracts, key=lambda contract: contract["provider_id"])


def _validate_provider_contract(contract: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(contract, dict):
        raise FailClosedRuntimeError("provider contract must be a JSON object")
    _verify_artifact_hash(contract, "provider contract")
    if contract.get("provider_role") != COGNITION_PROVIDER_ROLE:
        raise FailClosedRuntimeError("provider role is not COGNITION_PROVIDER")
    if contract.get("provider_approved") is not True:
        raise FailClosedRuntimeError("provider is not approved")
    provider_id = _normalize_provider_id(contract.get("provider_id"))
    if not _is_nonempty_string(contract.get("provider_schema_id")):
        raise FailClosedRuntimeError("provider schema id is required")
    identity = contract.get("provider_identity")
    if not isinstance(identity, dict) or identity.get("provider_id") != provider_id:
        raise FailClosedRuntimeError("provider identity is invalid")
    _validate_authority_flags(contract.get("authority_model"))
    if contract.get("replay_visible") is not True:
        raise FailClosedRuntimeError("provider contract is not replay-visible")
    return deepcopy(contract)


def _validate_ocs_context_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("OCS context artifact must be a JSON object")
    if artifact.get("artifact_type") != OCS_CONTEXT_ASSEMBLY_ARTIFACT_V1:
        raise FailClosedRuntimeError("invalid OCS context assembly artifact")
    if artifact.get("context_status") != OCS_CONTEXT_ASSEMBLED:
        raise FailClosedRuntimeError("OCS context must be assembled")
    if artifact.get("replay_visible") is not True:
        raise FailClosedRuntimeError("OCS context artifact is not replay-visible")
    _verify_artifact_hash(artifact, "OCS context artifact")
    _reject_prohibited_flags(artifact, "OCS context artifact")
    return deepcopy(artifact)


def _validate_authority_flags(flags: Any) -> None:
    if not isinstance(flags, dict):
        raise FailClosedRuntimeError("provider authority flags are missing")
    for flag, expected in AUTHORITY_FLAGS.items():
        if flags.get(flag) is not expected:
            raise FailClosedRuntimeError(f"provider authority flag must be false: {flag}")


def _verify_provider_success_result(result: dict[str, Any]) -> None:
    for key in ("provider_request_artifact", "provider_response_artifact", "llm_cognition_artifact"):
        if not isinstance(result.get(key), dict):
            raise FailClosedRuntimeError("provider success result missing nested artifact")
        _verify_artifact_hash(result[key], key)
    cognition = result["llm_cognition_artifact"]
    if cognition.get("artifact_type") != LLM_COGNITION_ARTIFACT_V1:
        raise FailClosedRuntimeError("provider success result cognition artifact type mismatch")
    if cognition["lineage_refs"]["llm_cognition_provider_request_hash"] != result["provider_request_artifact_hash"]:
        raise FailClosedRuntimeError("provider success result request lineage mismatch")
    if cognition["lineage_refs"]["llm_cognition_provider_response_hash"] != result["provider_response_artifact_hash"]:
        raise FailClosedRuntimeError("provider success result response lineage mismatch")


def _provider_prompt(*, human_request: str, context: dict[str, Any], provider_id: str) -> str:
    prompt = {
        "instruction": (
            "You are one isolated AiGOL COGNITION_PROVIDER in a multi-provider bundle. "
            "Return only non-authoritative cognition support. Do not compare providers."
        ),
        "provider_id": provider_id,
        "human_request": human_request,
        "ocs_context_reference": {
            "context_assembly_id": context["context_assembly_id"],
            "context_hash": context["context_hash"],
            "context_sections": context["context_sections"],
            "known_gaps": context["known_gaps"],
        },
        "allowed_outputs": ["findings", "assumptions", "alternatives", "risks", "uncertainties", "confidence"],
    }
    return json.dumps(prompt, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _extract_response_text(raw_response: Any) -> str:
    if isinstance(raw_response, str):
        return _require_string(raw_response, "provider_response_text")
    if not isinstance(raw_response, dict):
        raise FailClosedRuntimeError("provider response must be a JSON object or string")
    for key in ("output_text", "text", "response_text"):
        if isinstance(raw_response.get(key), str):
            return _require_string(raw_response[key], "provider_response_text")
    raise FailClosedRuntimeError("provider response did not include response text")


def _reject_prohibited_flags(artifact: dict[str, Any], label: str) -> None:
    for flag in (
        "approval_created",
        "execution_requested",
        "dispatch_requested",
        "worker_invoked",
        "domain_created",
        "governance_modified",
        "replay_modified",
    ):
        if artifact.get(flag) is True:
            raise FailClosedRuntimeError(f"{label} carries prohibited authority flag: {flag}")
    flags = artifact.get("authority_flags")
    if isinstance(flags, dict):
        for flag, value in flags.items():
            if value is True:
                raise FailClosedRuntimeError(f"{label} carries prohibited authority flag: {flag}")


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("multi-provider cognition replay step ordering mismatch")
    _verify_artifact_hash(artifact, "multi-provider cognition replay artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    try:
        _persist_step(replay_dir, index, step, artifact)
    except FailClosedRuntimeError:
        pass


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} must be a JSON object")
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError(f"{label} artifact hash is required")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} artifact hash mismatch")


def _verify_replay_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("multi-provider cognition replay hash is required")
    expected_input = deepcopy(wrapper)
    expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("multi-provider cognition replay hash mismatch")


def _json_safe(value: Any) -> Any:
    try:
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    except (TypeError, ValueError) as exc:
        raise FailClosedRuntimeError("provider response must be JSON serializable") from exc
    return deepcopy(value)


def _normalize_provider_id(value: Any) -> str:
    provider_id = _require_string(value, "provider_id").lower()
    allowed = "abcdefghijklmnopqrstuvwxyz0123456789_-"
    if any(character not in allowed for character in provider_id):
        raise FailClosedRuntimeError("provider_id contains unsupported characters")
    return provider_id


def _require_string(value: Any, field_name: str) -> str:
    if not _is_nonempty_string(value):
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
