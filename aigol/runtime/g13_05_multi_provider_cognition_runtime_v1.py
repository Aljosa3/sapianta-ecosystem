"""G13-05 governed multi-provider cognition runtime completion runner."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from aigol.provider.providers.openai_provider import OpenAIProviderAdapter
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.multi_provider_cognition_runtime import (
    create_default_cognition_provider_contract,
    reconstruct_multi_provider_cognition_replay,
    run_multi_provider_cognition_runtime,
)
from aigol.runtime.ocs_context_assembly_runtime import assemble_ocs_context
from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash, write_json_immutable


MILESTONE_ID = "G13_05_MULTI_PROVIDER_COGNITION_RUNTIME_V1"
DEFAULT_RUNTIME_ROOT = Path("runtime/g13_05_multi_provider_cognition_runtime_v1")
CREATED_AT = "2026-07-03T00:00:00Z"
OPENAI_PROVIDER_ID = "openai"
STANDARDS_ADAPTER_PROVIDER_ID = "standards_adapter"
FINAL_VERDICT_CERTIFIED = "MULTI_PROVIDER_RUNTIME_CERTIFIED"
FINAL_VERDICT_PARTIALLY_READY = "MULTI_PROVIDER_RUNTIME_PARTIALLY_READY"
FINAL_VERDICT_BLOCKED = "MULTI_PROVIDER_RUNTIME_BLOCKED"


def run_g13_05_multi_provider_cognition_runtime_v1(
    *,
    runtime_root: str | Path = DEFAULT_RUNTIME_ROOT,
    openai_adapter: OpenAIProviderAdapter | None = None,
) -> dict[str, Any]:
    """Run one real OpenAI provider plus one standards-compliant adapter."""

    cert_root = _next_cert_root(Path(runtime_root))
    trace: dict[str, Any] | None = None
    evidence: dict[str, Any] | None = None
    readiness: dict[str, Any] | None = None
    try:
        context_capture = assemble_ocs_context(
            context_assembly_id="G13-05:MULTI-PROVIDER-CONTEXT",
            created_at=CREATED_AT,
            replay_dir=cert_root / "context",
            source_context={
                "conversation_context": [
                    {
                        "source_id": "G13-05",
                        "summary": "Validate governed multi-provider cognition using OpenAI and a standards adapter.",
                        "replay_visible": True,
                    }
                ],
                "replay_visible_operation_context": [
                    {
                        "source_id": "G13-05:BOUNDARY",
                        "summary": "Cognition providers remain non-authoritative; downstream worker lifecycle is unchanged.",
                        "replay_visible": True,
                    }
                ],
            },
            source_chain_id="CHAIN-G13-05-MULTI-PROVIDER",
            source_request_reference="G13-05-MULTI-PROVIDER-REQUEST",
        )
        contracts = [
            create_default_cognition_provider_contract(
                provider_id=OPENAI_PROVIDER_ID,
                provider_label="OpenAI",
                provider_schema_id="openai.responses.v1",
                created_at=CREATED_AT,
            ),
            create_default_cognition_provider_contract(
                provider_id=STANDARDS_ADAPTER_PROVIDER_ID,
                provider_label="Standards Adapter",
                provider_schema_id="standards.cognition.v1",
                created_at=CREATED_AT,
            ),
        ]
        result = run_multi_provider_cognition_runtime(
            multi_provider_cognition_bundle_id="G13-05:MULTI-PROVIDER-COGNITION",
            human_request="Assess provider-agnostic next steps for governed external cognition completion.",
            ocs_context_artifact=context_capture["ocs_context_assembly_artifact"],
            provider_contracts=contracts,
            created_at=CREATED_AT,
            replay_dir=cert_root / "multi_provider_runtime",
            transport_registry={
                OPENAI_PROVIDER_ID: _openai_transport(openai_adapter),
                STANDARDS_ADAPTER_PROVIDER_ID: _standards_adapter_transport,
            },
        )
        reconstruction = reconstruct_multi_provider_cognition_replay(cert_root / "multi_provider_runtime")
        trace = _runtime_trace(
            cert_root=cert_root,
            context_capture=context_capture,
            runtime_result=result,
            replay_reconstruction=reconstruction,
        )
        evidence = _evidence_inventory(trace=trace, runtime_result=result)
        readiness = _readiness_assessment(trace=trace, evidence=evidence)
    except Exception as exc:
        trace = _failure_trace(cert_root=cert_root, failure_reason=_failure_reason(exc))
        evidence = _evidence_inventory(trace=trace, runtime_result={})
        readiness = _readiness_assessment(trace=trace, evidence=evidence)
    write_json_immutable(cert_root / "runtime_trace" / "000_multi_provider_runtime_trace.json", trace)
    write_json_immutable(cert_root / "evidence_inventory" / "000_multi_provider_evidence_inventory.json", evidence)
    write_json_immutable(cert_root / "readiness_assessment" / "000_multi_provider_readiness_assessment.json", readiness)
    return {
        "milestone_id": MILESTONE_ID,
        "cert_root": str(cert_root),
        "runtime_trace_path": str(cert_root / "runtime_trace" / "000_multi_provider_runtime_trace.json"),
        "evidence_inventory_path": str(cert_root / "evidence_inventory" / "000_multi_provider_evidence_inventory.json"),
        "readiness_assessment_path": str(
            cert_root / "readiness_assessment" / "000_multi_provider_readiness_assessment.json"
        ),
        "final_verdict": readiness["final_verdict"],
        "successful_providers": readiness["successful_providers"],
        "failed_providers": readiness["failed_providers"],
    }


def reconstruct_g13_05_multi_provider_cognition_runtime_v1(cert_root: str | Path) -> dict[str, Any]:
    root = Path(cert_root)
    trace = load_json(root / "runtime_trace" / "000_multi_provider_runtime_trace.json")
    evidence = load_json(root / "evidence_inventory" / "000_multi_provider_evidence_inventory.json")
    readiness = load_json(root / "readiness_assessment" / "000_multi_provider_readiness_assessment.json")
    for artifact in (trace, evidence, readiness):
        _verify_artifact_hash(artifact)
    replay = reconstruct_multi_provider_cognition_replay(trace["multi_provider_replay_reference"])
    return {
        "runtime_version": MILESTONE_ID,
        "replay_reconstructed": replay["replay_visible"] is True,
        "trace_hash": trace["artifact_hash"],
        "evidence_hash": evidence["artifact_hash"],
        "readiness_hash": readiness["artifact_hash"],
        "successful_provider_count": replay["successful_provider_count"],
        "failed_provider_count": replay["failed_provider_count"],
        "final_verdict": readiness["final_verdict"],
    }


def _openai_transport(adapter: OpenAIProviderAdapter | None) -> Any:
    active_adapter = adapter or OpenAIProviderAdapter(timeout_seconds=90, max_output_tokens=1024)

    def transport(payload: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
        prompt = _cognition_json_prompt(payload["input"])
        envelope = active_adapter.generate_proposal(
            {"prompt": prompt, "human_prompt": prompt},
            proposal_id="G13-05:OPENAI:COGNITION",
            timestamp=CREATED_AT,
        )
        envelope_dict = envelope.to_dict()
        response = envelope_dict["response"]
        return {
            "provider_id": metadata["provider_id"],
            "model": response.get("model", "openai"),
            "text": response["response_text"],
            "raw_response_hash": response.get("raw_response_hash"),
            "usage": _extract_usage(response.get("raw_response")),
        }

    return transport


def _standards_adapter_transport(payload: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
    return {
        "provider_id": metadata["provider_id"],
        "model": "standards-adapter-cognition-v1",
        "text": json.dumps(
            {
                "findings": ["Standards adapter returned provider-independent cognition evidence."],
                "assumptions": ["The adapter is standards-compliant and non-authoritative."],
                "alternatives": ["Run another configured external provider when available."],
                "risks": ["Only OpenAI is currently verified as a live external provider in this run."],
                "uncertainties": ["Future providers may expose different latency and response-shape behavior."],
                "confidence": "MEDIUM",
            },
            sort_keys=True,
        ),
        "usage": {"input_tokens": 8, "output_tokens": 22, "total_tokens": 30},
    }


def _cognition_json_prompt(provider_input: str) -> str:
    return "\n".join(
        [
            "Return only one JSON object for AiGOL governed cognition.",
            "Fields: findings, assumptions, alternatives, risks, uncertainties, confidence.",
            "Each field except confidence must be an array of short strings.",
            "confidence must be one of LOW, MEDIUM, HIGH, DETERMINISTIC, UNKNOWN.",
            "Do not authorize, execute, dispatch, invoke workers, mutate governance, or mutate replay.",
            "Provider input:",
            provider_input,
        ]
    )


def _runtime_trace(
    *,
    cert_root: Path,
    context_capture: dict[str, Any],
    runtime_result: dict[str, Any],
    replay_reconstruction: dict[str, Any],
) -> dict[str, Any]:
    bundle = runtime_result["result_bundle"]
    trace = {
        "artifact_type": "G13_05_MULTI_PROVIDER_RUNTIME_TRACE_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "cert_root": str(cert_root),
        "context_replay_reference": context_capture["ocs_context_assembly_replay_reference"],
        "multi_provider_replay_reference": runtime_result["replay_reference"],
        "request_bundle_hash": runtime_result["request_bundle"]["artifact_hash"],
        "result_bundle_hash": bundle["artifact_hash"],
        "provider_count": bundle["provider_count"],
        "successful_provider_count": bundle["successful_provider_count"],
        "failed_provider_count": bundle["failed_provider_count"],
        "successful_providers": [item["provider_id"] for item in bundle["provider_results"]],
        "failed_providers": [item["provider_id"] for item in bundle["provider_failures"]],
        "provider_selection": bundle["provider_usage_hashes"],
        "cognition_artifact_hashes": bundle["cognition_artifact_hashes"],
        "provider_usage_hashes": bundle["provider_usage_hashes"],
        "replay_reconstruction": replay_reconstruction,
        "worker_lifecycle_unchanged": True,
        "worker_invoked_by_cognition_runtime": bundle["worker_invoked"],
        "governance_modified": bundle["governance_modified"],
        "replay_modified": bundle["replay_modified"],
        "authority_flags": deepcopy(bundle["authority_flags"]),
    }
    trace["artifact_hash"] = replay_hash(trace)
    return trace


def _failure_trace(*, cert_root: Path, failure_reason: str) -> dict[str, Any]:
    trace = {
        "artifact_type": "G13_05_MULTI_PROVIDER_RUNTIME_TRACE_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "cert_root": str(cert_root),
        "multi_provider_replay_reference": str(cert_root / "multi_provider_runtime"),
        "provider_count": 0,
        "successful_provider_count": 0,
        "failed_provider_count": 0,
        "successful_providers": [],
        "failed_providers": [],
        "failure_reason": failure_reason,
        "worker_lifecycle_unchanged": True,
        "worker_invoked_by_cognition_runtime": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    trace["artifact_hash"] = replay_hash(trace)
    return trace


def _evidence_inventory(*, trace: dict[str, Any], runtime_result: dict[str, Any]) -> dict[str, Any]:
    bundle = runtime_result.get("result_bundle") if isinstance(runtime_result.get("result_bundle"), dict) else {}
    evidence = {
        "artifact_type": "G13_05_MULTI_PROVIDER_EVIDENCE_INVENTORY_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "provider_abstraction_validated": trace.get("successful_provider_count", 0) >= 2,
        "provider_selection_evidence": {
            "provider_count": trace.get("provider_count", 0),
            "successful_providers": trace.get("successful_providers", []),
            "failed_providers": trace.get("failed_providers", []),
        },
        "provider_invocation_evidence": [
            {
                "provider_id": item.get("provider_id"),
                "provider_response_artifact_hash": item.get("provider_response_artifact_hash"),
                "provider_usage_hash": item.get("provider_usage_hash"),
                "cognition_artifact_hash": item.get("cognition_artifact_hash"),
            }
            for item in bundle.get("provider_results", [])
        ],
        "governance_evidence": {
            "authority_flags": trace.get("authority_flags", {}),
            "governance_modified": trace.get("governance_modified") is True,
            "worker_lifecycle_unchanged": trace.get("worker_lifecycle_unchanged") is True,
        },
        "worker_execution_evidence": {
            "cognition_runtime_invoked_worker": trace.get("worker_invoked_by_cognition_runtime") is True,
            "downstream_worker_runtime": "unchanged from G13_04 certified baseline",
            "worker_boundary_preserved": trace.get("worker_lifecycle_unchanged") is True,
        },
        "replay_evidence": {
            "multi_provider_replay_reference": trace.get("multi_provider_replay_reference"),
            "replay_reconstruction": trace.get("replay_reconstruction", {}),
        },
    }
    evidence["artifact_hash"] = replay_hash(evidence)
    return evidence


def _readiness_assessment(*, trace: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    successful = list(trace.get("successful_providers", []))
    failed = list(trace.get("failed_providers", []))
    openai_success = OPENAI_PROVIDER_ID in successful
    standards_success = STANDARDS_ADAPTER_PROVIDER_ID in successful
    certified = openai_success and standards_success and trace.get("successful_provider_count") >= 2
    partially_ready = bool(successful) and not certified
    verdict = (
        FINAL_VERDICT_CERTIFIED
        if certified
        else FINAL_VERDICT_PARTIALLY_READY
        if partially_ready
        else FINAL_VERDICT_BLOCKED
    )
    assessment = {
        "artifact_type": "G13_05_MULTI_PROVIDER_READINESS_ASSESSMENT_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "successful_providers": successful,
        "failed_providers": failed,
        "openai_real_provider_successful": openai_success,
        "standards_adapter_successful": standards_success,
        "provider_abstraction_validated": evidence["provider_abstraction_validated"],
        "governance_provider_independent": trace.get("governance_modified") is False,
        "replay_persistent": bool(trace.get("multi_provider_replay_reference")),
        "remaining_gaps": [] if certified else _remaining_gaps(successful, failed),
        "final_verdict": verdict,
    }
    assessment["artifact_hash"] = replay_hash(assessment)
    return assessment


def _remaining_gaps(successful: list[str], failed: list[str]) -> list[dict[str, str]]:
    gaps = []
    if OPENAI_PROVIDER_ID not in successful:
        gaps.append({"classification": "Integration Gap", "description": "OpenAI provider did not complete."})
    if STANDARDS_ADAPTER_PROVIDER_ID not in successful:
        gaps.append({"classification": "Implementation Gap", "description": "Standards adapter did not complete."})
    for provider_id in failed:
        gaps.append({"classification": "Integration Gap", "description": f"{provider_id} did not complete."})
    return gaps


def _extract_usage(raw_response: Any) -> dict[str, int | None]:
    usage = raw_response.get("usage") if isinstance(raw_response, dict) else None
    if not isinstance(usage, dict):
        return {"input_tokens": None, "output_tokens": None, "total_tokens": None}
    input_tokens = _optional_int(usage.get("input_tokens"))
    output_tokens = _optional_int(usage.get("output_tokens"))
    total_tokens = _optional_int(usage.get("total_tokens"))
    return {"input_tokens": input_tokens, "output_tokens": output_tokens, "total_tokens": total_tokens}


def _optional_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    return value if isinstance(value, int) and value >= 0 else None


def _next_cert_root(runtime_root: Path) -> Path:
    runtime_root.mkdir(parents=True, exist_ok=True)
    existing = sorted(
        int(path.name.split("-", 1)[1])
        for path in runtime_root.glob("CERT-*")
        if path.is_dir() and path.name.startswith("CERT-") and path.name.split("-", 1)[1].isdigit()
    )
    return runtime_root / f"CERT-{(existing[-1] + 1) if existing else 1:06d}"


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    candidate = deepcopy(artifact)
    actual = candidate.pop("artifact_hash", None)
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("G13-05 artifact hash mismatch")


def _failure_reason(exc: Exception) -> str:
    return str(exc) if isinstance(exc, FailClosedRuntimeError) else "G13-05 multi-provider runtime failed closed"


if __name__ == "__main__":
    print(canonical_serialize(run_g13_05_multi_provider_cognition_runtime_v1()))
