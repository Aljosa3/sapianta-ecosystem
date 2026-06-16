"""First real provider runtime validation for AIGOL_FIRST_REAL_PROVIDER_RUNTIME_IMPLEMENTATION_V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.cognition_artifact_runtime import (
    LLM_COGNITION_ARTIFACT_V1,
    run_cognition_artifact_runtime,
)
from aigol.runtime.external_resource_registry_runtime import (
    COGNITION_PROVIDER,
    OPENAI_PROVIDER_ID,
    real_provider_err_v1_registry,
    select_resource_for_capability,
)
from aigol.runtime.llm_cognition_provider_runtime import (
    LLM_COGNITION_PROVIDER_REQUEST_ARTIFACT_V1,
    LLM_COGNITION_PROVIDER_RESPONSE_ARTIFACT_V1,
    create_default_openai_cognition_provider_contract,
    run_llm_cognition_provider_runtime,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.ocs_context_assembly_runtime import assemble_ocs_context
from aigol.runtime.transport.serialization import replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_FIRST_REAL_PROVIDER_RUNTIME_IMPLEMENTATION_V1"
CANONICAL_CONTRACT_REFERENCE = "AIGOL_CANONICAL_PROVIDER_CONTRACT_V1"
CANONICAL_COGNITION_PROVIDER_CONTRACT_V1 = "CANONICAL_COGNITION_PROVIDER_CONTRACT_V1"
CANONICAL_COGNITION_PROVIDER_INPUT_V1 = "CANONICAL_COGNITION_PROVIDER_INPUT_V1"
CANONICAL_COGNITION_PROVIDER_OUTPUT_V1 = "CANONICAL_COGNITION_PROVIDER_OUTPUT_V1"
FIRST_REAL_PROVIDER_RUNTIME_VALIDATION_ARTIFACT_V1 = "FIRST_REAL_PROVIDER_RUNTIME_VALIDATION_ARTIFACT_V1"

STATUS_COMPLETED = "COMPLETED"
STATUS_FAILED_CLOSED = "FAILED_CLOSED"

OPENAI_RESPONSES_SCHEMA = "openai.responses.v1"
OPENAI_CAPABILITIES = ("reasoning", "planning", "summarization", "analysis", "generation")
ALLOWED_OUTPUTS = (
    "findings",
    "assumptions",
    "alternatives",
    "risks",
    "uncertainties",
    "confidence",
    "clarification_questions",
    "recommended_next_milestone",
)
PROHIBITED_OUTPUTS = (
    "approvals",
    "authorizations",
    "governance mutations",
    "replay mutations",
    "worker invocation",
    "execution authorization",
    "dispatch instruction",
    "domain creation authorization",
    "implementation authorization",
    "credential disclosure",
    "secret handling",
)
AUTHORITY_FLAGS = {
    "provider_authority": False,
    "approval_authority": False,
    "execution_authority": False,
    "worker_authority": False,
    "governance_authority": False,
    "replay_authority": False,
    "dispatch_authority": False,
    "authorization_authority": False,
}

DEFAULT_DETERMINISTIC_RESPONSE_TEXT = (
    '{"findings":["OpenAI deterministic validation response was captured as non-authoritative cognition."],'
    '"assumptions":["The transport was a deterministic local stub."],'
    '"alternatives":["Use live validation only after separate governed approval."],'
    '"risks":["Provider output remains untrusted until normalized and reviewed."],'
    '"uncertainties":["Live provider availability was not tested."],'
    '"confidence":"HIGH"}'
)


def run_first_real_provider_runtime_validation(
    *,
    validation_id: str,
    human_request: str,
    source_context: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
    err_registry: dict[str, Any] | None = None,
    deterministic_response_text: str = DEFAULT_DETERMINISTIC_RESPONSE_TEXT,
    human_approved: bool = True,
    approved_by: str = "human.operator",
    model: str = "gpt-5.1",
    credential_env: str = "AIGOL_OPENAI_API_KEY",
) -> dict[str, Any]:
    """Validate ERR -> canonical contract -> LLM runtime -> cognition artifact with a stub response."""

    replay_path = Path(replay_dir)
    validation = _require_string(validation_id, "validation_id")
    try:
        context_capture = assemble_ocs_context(
            context_assembly_id=f"{validation}:OCS_CONTEXT",
            created_at=created_at,
            replay_dir=replay_path / "ocs_context",
            source_context=source_context,
            source_chain_id=f"{validation}:SOURCE_CHAIN",
            source_request_reference=f"{validation}:HUMAN_REQUEST",
        )
        _require_stage_success(context_capture, "OCS context assembly")
        context_artifact = context_capture["ocs_context_assembly_artifact"]

        err_selection = select_resource_for_capability(
            selection_id=f"{validation}:ERR_OPENAI_SELECTION",
            required_capability="reasoning",
            replay_dir=replay_path / "err_openai_selection",
            created_at=created_at,
            registry=deepcopy(err_registry) if err_registry is not None else real_provider_err_v1_registry(),
            resource_type=COGNITION_PROVIDER,
            human_intent=human_request,
            hirr_output={
                "runtime": MILESTONE_ID,
                "required_capability": "reasoning",
                "resource_type": COGNITION_PROVIDER,
            },
        )
        if err_selection["selected_resource_id"] != OPENAI_PROVIDER_ID:
            raise FailClosedRuntimeError("first real provider validation requires ERR-selected openai")

        source_contract = create_default_openai_cognition_provider_contract(created_at=created_at)
        canonical_contract = adapt_openai_contract_to_canonical(
            source_contract=source_contract,
            capabilities=OPENAI_CAPABILITIES,
            created_at=created_at,
        )

        llm_capture = run_llm_cognition_provider_runtime(
            cognition_provider_request_id=f"{validation}:OPENAI_COGNITION_PROVIDER_REQUEST",
            human_request=human_request,
            ocs_context_artifact=context_artifact,
            provider_contract=source_contract,
            created_at=created_at,
            replay_dir=replay_path / "llm_cognition_provider",
            human_approved=human_approved,
            approved_by=approved_by,
            provider_id=OPENAI_PROVIDER_ID,
            model=model,
            credential_env=credential_env,
            transport=_deterministic_transport(deterministic_response_text),
        )
        _require_stage_success(llm_capture, "LLM cognition provider runtime")

        canonical_input = adapt_provider_request_to_canonical_input(
            request_artifact=llm_capture["llm_cognition_provider_request_artifact"],
            canonical_contract=canonical_contract,
            created_at=created_at,
        )
        canonical_output = adapt_provider_response_to_canonical_output(
            response_artifact=llm_capture["llm_cognition_provider_response_artifact"],
            canonical_input=canonical_input,
            canonical_contract=canonical_contract,
            created_at=created_at,
        )

        cognition_capture = run_cognition_artifact_runtime(
            cognition_artifact_id=f"{validation}:OPENAI_LLM_COGNITION_ARTIFACT",
            ocs_context_artifact=context_artifact,
            provider_request_artifact=llm_capture["llm_cognition_provider_request_artifact"],
            provider_response_artifact=llm_capture["llm_cognition_provider_response_artifact"],
            created_at=created_at,
            replay_dir=replay_path / "llm_cognition_artifact",
        )
        _require_stage_success(cognition_capture, "LLM cognition artifact runtime")

        validation_artifact = _validation_artifact(
            validation_id=validation,
            final_status=STATUS_COMPLETED,
            created_at=created_at,
            err_selection=err_selection,
            canonical_contract=canonical_contract,
            canonical_input=canonical_input,
            canonical_output=canonical_output,
            llm_capture=llm_capture,
            cognition_capture=cognition_capture,
            failure_reason="",
        )
        _persist_validation_artifact(replay_path, validation_artifact)
        return _capture(
            validation_artifact=validation_artifact,
            replay_path=replay_path,
            err_selection=err_selection,
            canonical_contract=canonical_contract,
            canonical_input=canonical_input,
            canonical_output=canonical_output,
            llm_capture=llm_capture,
            cognition_capture=cognition_capture,
        )
    except Exception as exc:
        failure_reason = str(exc) if isinstance(exc, FailClosedRuntimeError) else "first real provider validation failed closed"
        failure_artifact = _failure_artifact(
            validation_id=validation,
            created_at=created_at if isinstance(created_at, str) and created_at.strip() else "1970-01-01T00:00:00Z",
            failure_reason=failure_reason,
        )
        _persist_validation_artifact(replay_path, failure_artifact)
        return _capture(
            validation_artifact=failure_artifact,
            replay_path=replay_path,
            err_selection=None,
            canonical_contract=None,
            canonical_input=None,
            canonical_output=None,
            llm_capture=None,
            cognition_capture=None,
        )


def adapt_openai_contract_to_canonical(
    *,
    source_contract: dict[str, Any],
    capabilities: tuple[str, ...] | list[str],
    created_at: str,
) -> dict[str, Any]:
    """Convert the existing OpenAI contract dialect into a canonical contract view."""

    _verify_artifact_hash(source_contract, "source provider contract")
    if source_contract.get("provider_id") != OPENAI_PROVIDER_ID:
        raise FailClosedRuntimeError("canonical OpenAI adapter requires provider_id openai")
    if source_contract.get("provider_role") != COGNITION_PROVIDER:
        raise FailClosedRuntimeError("canonical OpenAI adapter requires COGNITION_PROVIDER role")
    if source_contract.get("provider_schema_id") != OPENAI_RESPONSES_SCHEMA:
        raise FailClosedRuntimeError("canonical OpenAI adapter requires openai.responses.v1 schema")
    artifact = {
        "artifact_type": CANONICAL_COGNITION_PROVIDER_CONTRACT_V1,
        "contract_reference": CANONICAL_CONTRACT_REFERENCE,
        "provider_id": OPENAI_PROVIDER_ID,
        "provider_role": COGNITION_PROVIDER,
        "provider_schema_id": OPENAI_RESPONSES_SCHEMA,
        "provider_identity": {
            "provider_id": OPENAI_PROVIDER_ID,
            "provider_kind": "external_llm",
            "provider_label": "OpenAI",
            "model_family": "openai.responses",
        },
        "capabilities": _normalize_capabilities(capabilities),
        "provider_approved": source_contract.get("provider_approved") is True,
        "allowed_outputs": list(ALLOWED_OUTPUTS),
        "prohibited_outputs": list(PROHIBITED_OUTPUTS),
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "replay_visible": True,
        "source_contract_artifact_type": source_contract.get("artifact_type"),
        "source_contract_hash": source_contract["artifact_hash"],
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["contract_hash"] = replay_hash(_contract_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def adapt_provider_request_to_canonical_input(
    *,
    request_artifact: dict[str, Any],
    canonical_contract: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    """Convert an LLM cognition provider request into canonical input evidence."""

    _verify_artifact_hash(request_artifact, "source provider request")
    _verify_artifact_hash(canonical_contract, "canonical provider contract")
    if request_artifact.get("artifact_type") != LLM_COGNITION_PROVIDER_REQUEST_ARTIFACT_V1:
        raise FailClosedRuntimeError("canonical input adapter requires LLM cognition provider request artifact")
    if request_artifact.get("provider_invoked") is not False:
        raise FailClosedRuntimeError("canonical input adapter requires provider_invoked false")
    if request_artifact.get("provider_id") != canonical_contract["provider_id"]:
        raise FailClosedRuntimeError("canonical input adapter provider mismatch")
    if request_artifact.get("provider_contract_hash") != canonical_contract["source_contract_hash"]:
        raise FailClosedRuntimeError("canonical input adapter source contract hash mismatch")
    artifact = {
        "artifact_type": CANONICAL_COGNITION_PROVIDER_INPUT_V1,
        "contract_reference": CANONICAL_CONTRACT_REFERENCE,
        "provider_input_id": request_artifact["cognition_provider_request_id"],
        "provider_id": request_artifact["provider_id"],
        "provider_role": request_artifact["provider_role"],
        "provider_schema_id": request_artifact["provider_schema_id"],
        "provider_identity": deepcopy(request_artifact["provider_identity"]),
        "request": deepcopy(request_artifact["request"]),
        "ocs_context_reference": deepcopy(request_artifact["ocs_context_reference"]),
        "provider_contract_hash": canonical_contract["artifact_hash"],
        "source_provider_contract_hash": request_artifact["provider_contract_hash"],
        "lineage_refs": deepcopy(request_artifact["lineage_refs"]),
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "source_input_artifact_hash": request_artifact["artifact_hash"],
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["input_hash"] = replay_hash(_input_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def adapt_provider_response_to_canonical_output(
    *,
    response_artifact: dict[str, Any],
    canonical_input: dict[str, Any],
    canonical_contract: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    """Convert an LLM cognition provider response into canonical output evidence."""

    _verify_artifact_hash(response_artifact, "source provider response")
    _verify_artifact_hash(canonical_input, "canonical provider input")
    _verify_artifact_hash(canonical_contract, "canonical provider contract")
    if response_artifact.get("artifact_type") != LLM_COGNITION_PROVIDER_RESPONSE_ARTIFACT_V1:
        raise FailClosedRuntimeError("canonical output adapter requires LLM cognition provider response artifact")
    if response_artifact.get("provider_request_hash") != canonical_input["source_input_artifact_hash"]:
        raise FailClosedRuntimeError("canonical output adapter source input hash mismatch")
    if response_artifact.get("provider_id") != canonical_contract["provider_id"]:
        raise FailClosedRuntimeError("canonical output adapter provider mismatch")
    _reject_authority_flags(response_artifact.get("authority_flags"))
    artifact = {
        "artifact_type": CANONICAL_COGNITION_PROVIDER_OUTPUT_V1,
        "contract_reference": CANONICAL_CONTRACT_REFERENCE,
        "provider_output_id": f"{response_artifact['cognition_provider_request_id']}:CANONICAL_OUTPUT",
        "provider_input_id": response_artifact["cognition_provider_request_id"],
        "provider_id": response_artifact["provider_id"],
        "provider_role": response_artifact["provider_role"],
        "provider_schema_id": response_artifact["provider_schema_id"],
        "provider_identity": deepcopy(response_artifact["provider_identity"]),
        "provider_metadata": deepcopy(response_artifact["provider_metadata"]),
        "provider_contract_hash": canonical_contract["artifact_hash"],
        "provider_input_hash": canonical_input["artifact_hash"],
        "source_provider_input_hash": response_artifact["provider_request_hash"],
        "request_hash": response_artifact["request_hash"],
        "ocs_context_hash": response_artifact["ocs_context_hash"],
        "raw_response": deepcopy(response_artifact["raw_response"]),
        "raw_response_hash": response_artifact["raw_response_hash"],
        "response_text": response_artifact["response_text"],
        "response_text_hash": response_artifact["response_text_hash"],
        "response_status": response_artifact["response_status"],
        "untrusted_provider_output": True,
        "non_authoritative": True,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "lineage_refs": deepcopy(response_artifact["lineage_refs"]),
        "replay_visible": True,
        "provider_invoked": response_artifact.get("provider_invoked") is True,
        "worker_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "source_output_artifact_hash": response_artifact["artifact_hash"],
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["output_hash"] = replay_hash(_output_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _deterministic_transport(response_text: str):
    response = _require_string(response_text, "deterministic_response_text")

    def call(payload: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
        if payload.get("stream") is not False:
            raise FailClosedRuntimeError("deterministic provider validation requires stream false")
        if metadata.get("provider_id") != OPENAI_PROVIDER_ID:
            raise FailClosedRuntimeError("deterministic provider validation requires openai metadata")
        return {
            "id": "deterministic-openai-validation-response",
            "model": payload.get("model", "gpt-5.1"),
            "output_text": response,
            "deterministic_stub": True,
            "real_openai_called": False,
            "usage": {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
            },
        }

    return call


def _validation_artifact(
    *,
    validation_id: str,
    final_status: str,
    created_at: str,
    err_selection: dict[str, Any],
    canonical_contract: dict[str, Any],
    canonical_input: dict[str, Any],
    canonical_output: dict[str, Any],
    llm_capture: dict[str, Any],
    cognition_capture: dict[str, Any],
    failure_reason: str,
) -> dict[str, Any]:
    cognition_artifact = cognition_capture["llm_cognition_artifact"]
    if cognition_artifact.get("artifact_type") != LLM_COGNITION_ARTIFACT_V1:
        raise FailClosedRuntimeError("first real provider validation requires LLM_COGNITION_ARTIFACT_V1")
    artifact = {
        "artifact_type": FIRST_REAL_PROVIDER_RUNTIME_VALIDATION_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "validation_id": validation_id,
        "final_status": final_status,
        "selected_provider_id": err_selection["selected_resource_id"],
        "err_selection_hash": err_selection["err_selection_evidence_artifact"]["artifact_hash"],
        "canonical_contract_hash": canonical_contract["artifact_hash"],
        "canonical_input_hash": canonical_input["artifact_hash"],
        "canonical_output_hash": canonical_output["artifact_hash"],
        "llm_provider_request_hash": llm_capture["llm_cognition_provider_request_artifact"]["artifact_hash"],
        "llm_provider_response_hash": llm_capture["llm_cognition_provider_response_artifact"]["artifact_hash"],
        "llm_provider_replay_binding_hash": llm_capture["replay_binding"]["artifact_hash"],
        "llm_cognition_artifact_hash": cognition_artifact["artifact_hash"],
        "deterministic_mock_provider_response": True,
        "real_openai_called": False,
        "provider_invoked": llm_capture["provider_invoked"] is True,
        "worker_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failure_artifact(*, validation_id: str, created_at: str, failure_reason: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": FIRST_REAL_PROVIDER_RUNTIME_VALIDATION_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "validation_id": validation_id,
        "final_status": STATUS_FAILED_CLOSED,
        "selected_provider_id": None,
        "deterministic_mock_provider_response": True,
        "real_openai_called": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
        "created_at": created_at,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    *,
    validation_artifact: dict[str, Any],
    replay_path: Path,
    err_selection: dict[str, Any] | None,
    canonical_contract: dict[str, Any] | None,
    canonical_input: dict[str, Any] | None,
    canonical_output: dict[str, Any] | None,
    llm_capture: dict[str, Any] | None,
    cognition_capture: dict[str, Any] | None,
) -> dict[str, Any]:
    final_status = validation_artifact["final_status"]
    capture = {
        "milestone_id": MILESTONE_ID,
        "final_status": final_status,
        "validation_id": validation_artifact["validation_id"],
        "selected_provider_id": validation_artifact.get("selected_provider_id"),
        "first_real_provider_runtime_validation_artifact": deepcopy(validation_artifact),
        "err_selection_capture": deepcopy(err_selection),
        "canonical_provider_contract": deepcopy(canonical_contract),
        "canonical_provider_input": deepcopy(canonical_input),
        "canonical_provider_output": deepcopy(canonical_output),
        "llm_cognition_provider_capture": deepcopy(llm_capture),
        "llm_cognition_artifact_capture": deepcopy(cognition_capture),
        "deterministic_mock_provider_response": validation_artifact["deterministic_mock_provider_response"],
        "real_openai_called": False,
        "provider_invoked": validation_artifact["provider_invoked"] is True,
        "worker_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "fail_closed": final_status != STATUS_COMPLETED,
        "failure_reason": validation_artifact.get("failure_reason", ""),
        "replay_reference": str(replay_path),
    }
    capture["runtime_hash"] = replay_hash(capture)
    return capture


def _persist_validation_artifact(replay_path: Path, artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact, "first real provider validation artifact")
    wrapper = {
        "replay_index": 0,
        "replay_step": "first_real_provider_runtime_validation",
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / "000_first_real_provider_runtime_validation.json", wrapper)


def _require_stage_success(capture: dict[str, Any], stage: str) -> None:
    if not isinstance(capture, dict) or capture.get("fail_closed") is True:
        reason = capture.get("failure_reason") if isinstance(capture, dict) else ""
        raise FailClosedRuntimeError(f"{stage} failed closed: {reason}")
    status = capture.get("final_status")
    if status is not None and status != STATUS_COMPLETED:
        raise FailClosedRuntimeError(f"{stage} failed closed: {capture.get('failure_reason', '')}")


def _contract_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "contract_reference": artifact["contract_reference"],
        "provider_id": artifact["provider_id"],
        "provider_role": artifact["provider_role"],
        "provider_schema_id": artifact["provider_schema_id"],
        "provider_identity": artifact["provider_identity"],
        "capabilities": artifact["capabilities"],
        "provider_approved": artifact["provider_approved"],
        "allowed_outputs": artifact["allowed_outputs"],
        "prohibited_outputs": artifact["prohibited_outputs"],
        "authority_flags": artifact["authority_flags"],
        "source_contract_hash": artifact["source_contract_hash"],
    }


def _input_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "provider_input_id": artifact["provider_input_id"],
        "provider_id": artifact["provider_id"],
        "provider_role": artifact["provider_role"],
        "provider_schema_id": artifact["provider_schema_id"],
        "provider_identity": artifact["provider_identity"],
        "request": artifact["request"],
        "ocs_context_reference": artifact["ocs_context_reference"],
        "provider_contract_hash": artifact["provider_contract_hash"],
        "source_provider_contract_hash": artifact["source_provider_contract_hash"],
        "lineage_refs": artifact["lineage_refs"],
        "authority_flags": artifact["authority_flags"],
        "source_input_artifact_hash": artifact["source_input_artifact_hash"],
    }


def _output_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "provider_output_id": artifact["provider_output_id"],
        "provider_input_id": artifact["provider_input_id"],
        "provider_id": artifact["provider_id"],
        "provider_role": artifact["provider_role"],
        "provider_schema_id": artifact["provider_schema_id"],
        "provider_identity": artifact["provider_identity"],
        "provider_metadata": artifact["provider_metadata"],
        "provider_contract_hash": artifact["provider_contract_hash"],
        "provider_input_hash": artifact["provider_input_hash"],
        "source_provider_input_hash": artifact["source_provider_input_hash"],
        "request_hash": artifact["request_hash"],
        "ocs_context_hash": artifact["ocs_context_hash"],
        "raw_response_hash": artifact["raw_response_hash"],
        "response_text_hash": artifact["response_text_hash"],
        "response_status": artifact["response_status"],
        "untrusted_provider_output": artifact["untrusted_provider_output"],
        "non_authoritative": artifact["non_authoritative"],
        "authority_flags": artifact["authority_flags"],
        "lineage_refs": artifact["lineage_refs"],
        "source_output_artifact_hash": artifact["source_output_artifact_hash"],
    }


def _normalize_capabilities(capabilities: tuple[str, ...] | list[str]) -> list[str]:
    if not isinstance(capabilities, (tuple, list)) or not capabilities:
        raise FailClosedRuntimeError("canonical provider capabilities are required")
    normalized = [_require_string(item, "capability") for item in capabilities]
    if len(set(normalized)) != len(normalized):
        raise FailClosedRuntimeError("canonical provider capabilities must be unique")
    return normalized


def _reject_authority_flags(flags: Any) -> None:
    if not isinstance(flags, dict):
        raise FailClosedRuntimeError("authority flags are required")
    for flag, expected in AUTHORITY_FLAGS.items():
        if flags.get(flag, False) is not expected:
            raise FailClosedRuntimeError(f"authority flag must remain false: {flag}")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} must be a JSON object")
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError(f"{label} artifact_hash is required")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} artifact hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
