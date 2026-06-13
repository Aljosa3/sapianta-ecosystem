"""Certification tests for AIGOL_COGNITION_COMPARISON_CERTIFICATION_V1."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from aigol.runtime.cognition_comparison_runtime import (
    STATUS_COMPLETED,
    reconstruct_cognition_comparison_replay,
    run_cognition_comparison_runtime,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.multi_provider_cognition_runtime import (
    create_default_cognition_provider_contract,
    run_multi_provider_cognition_runtime,
)
from aigol.runtime.ocs_context_assembly_runtime import assemble_ocs_context
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-06-13T00:00:00Z"
PROVIDERS = ("provider-a", "provider-b", "provider-c")


def _source_artifact() -> dict[str, Any]:
    artifact = {
        "artifact_type": "HUMAN_REQUEST_ARTIFACT_V1",
        "artifact_id": "HUMAN-REQUEST-COGNITION-COMPARISON-CERTIFICATION",
        "summary": "Human asks OCS to compare multiple cognition provider conclusions.",
        "replay_visible": True,
        "authority": False,
        "execution_requested": False,
        "worker_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _context(tmp_path: Path) -> dict[str, Any]:
    capture = assemble_ocs_context(
        context_assembly_id="OCS-CONTEXT-COGNITION-COMPARISON-CERTIFICATION",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "ocs_context",
        source_context={"conversation_context": [_source_artifact()]},
        source_chain_id="CHAIN-COGNITION-COMPARISON-CERTIFICATION",
        source_request_reference="HUMAN-REQUEST-COGNITION-COMPARISON-CERTIFICATION",
    )
    assert capture["fail_closed"] is False
    return capture["ocs_context_assembly_artifact"]


def _contracts() -> list[dict[str, Any]]:
    return [
        create_default_cognition_provider_contract(provider_id=provider_id, created_at=CREATED_AT)
        for provider_id in PROVIDERS
    ]


def _response_text(provider_id: str, payloads: dict[str, dict[str, Any]]) -> str:
    payload = payloads[provider_id]
    return json.dumps(
        {
            "findings": payload.get("findings", []),
            "assumptions": payload.get("assumptions", []),
            "alternatives": payload.get("alternatives", []),
            "risks": payload.get("risks", []),
            "uncertainties": payload.get("uncertainties", []),
            "confidence": payload.get("confidence", "HIGH"),
        },
        sort_keys=True,
    )


def _transports(
    payloads: dict[str, dict[str, Any]],
    *,
    failing_provider: str | None = None,
):
    transports = {}
    for provider_id in PROVIDERS:

        def call(_payload: dict[str, Any], metadata: dict[str, Any], provider_id: str = provider_id) -> dict[str, Any]:
            assert metadata["provider_role"] == "COGNITION_PROVIDER"
            if failing_provider == provider_id:
                raise FailClosedRuntimeError(f"{provider_id} missing evidence")
            return {"output_text": _response_text(provider_id, payloads)}

        transports[provider_id] = call
    return transports


def _run_comparison(
    tmp_path: Path,
    *,
    payloads: dict[str, dict[str, Any]],
    failing_provider: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    multi = run_multi_provider_cognition_runtime(
        multi_provider_cognition_bundle_id="MULTI-PROVIDER-COGNITION-COMPARISON-CERTIFICATION",
        human_request="Compare cognition provider conclusions before governance decision.",
        ocs_context_artifact=_context(tmp_path),
        provider_contracts=_contracts(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "multi_provider_cognition",
        transport_registry=_transports(payloads, failing_provider=failing_provider),
    )
    assert multi["fail_closed"] is False
    comparison = run_cognition_comparison_runtime(
        cognition_comparison_id="COGNITION-COMPARISON-CERTIFICATION",
        multi_provider_result_bundle=multi["result_bundle"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "cognition_comparison",
    )
    assert comparison["final_status"] == STATUS_COMPLETED
    return multi["result_bundle"], comparison


def _provider_findings(result_bundle: dict[str, Any]) -> list[list[str]]:
    findings = []
    for provider_result in result_bundle["provider_results"]:
        artifact = provider_result["llm_cognition_artifact"]
        findings.append([" ".join(item.lower().split()) for item in artifact["findings"]])
    return findings


def _certified_comparison_decision(result_bundle: dict[str, Any], comparison_artifact: dict[str, Any]) -> dict[str, Any]:
    all_findings = [finding for provider_findings in _provider_findings(result_bundle) for finding in provider_findings]
    counts = Counter(all_findings)
    provider_count = result_bundle["successful_provider_count"]
    full_consensus_count = sum(1 for count in counts.values() if count == provider_count)
    majority_count = sum(1 for count in counts.values() if 1 < count < provider_count)
    provider_failure = result_bundle["failed_provider_count"] > 0
    missing_information = bool(comparison_artifact["missing_information"])
    if provider_failure or missing_information:
        outcome = "INSUFFICIENT_INFORMATION"
    elif full_consensus_count > 0 and not comparison_artifact["disagreement"]:
        outcome = "CONSENSUS"
    elif majority_count > 0:
        outcome = "PARTIAL_CONSENSUS"
    else:
        outcome = "CONFLICT"
    return {
        "outcome": outcome,
        "clarification_can_be_requested": outcome in {"CONFLICT", "INSUFFICIENT_INFORMATION"},
        "full_consensus_count": full_consensus_count,
        "majority_count": majority_count,
    }


def _assert_comparison_governance_boundary(comparison: dict[str, Any]) -> None:
    artifact = comparison["cognition_comparison_artifact"]
    assert comparison["approval_created"] is False
    assert comparison["worker_invoked"] is False
    assert comparison["execution_requested"] is False
    assert comparison["dispatch_requested"] is False
    assert artifact["approval_created"] is False
    assert artifact["worker_invoked"] is False
    assert artifact["execution_requested"] is False
    assert artifact["dispatch_requested"] is False
    assert artifact["human_review_required"] is True
    assert artifact["non_authoritative"] is True
    assert all(value is False for value in artifact["authority_flags"].values())


def _assert_replay_lineage(tmp_path: Path, result_bundle: dict[str, Any], comparison: dict[str, Any]) -> None:
    replay = reconstruct_cognition_comparison_replay(tmp_path / "cognition_comparison")
    artifact = comparison["cognition_comparison_artifact"]
    assert replay["source_cognition_artifact_count"] == result_bundle["successful_provider_count"]
    assert replay["lineage_refs"]["source_cognition_artifact_hashes"] == result_bundle["cognition_artifact_hashes"]
    assert replay["lineage_refs"]["multi_provider_result_bundle_hash"] == result_bundle["artifact_hash"]
    assert artifact["lineage_refs"]["provider_identity_hashes"]
    assert Path(comparison["replay_reference"]).exists()


def test_cognition_comparison_certifies_consensus_when_all_providers_agree(tmp_path) -> None:
    payloads = {
        provider_id: {
            "findings": ["Shared conclusion: execution should remain governed by PPP."],
            "assumptions": ["Shared assumption: provider output remains advisory."],
            "alternatives": ["Continue through governance."],
            "risks": ["Premature execution would violate authority boundaries."],
            "uncertainties": ["None material."],
            "confidence": "HIGH",
        }
        for provider_id in PROVIDERS
    }
    result_bundle, comparison = _run_comparison(tmp_path, payloads=payloads)
    artifact = comparison["cognition_comparison_artifact"]
    decision = _certified_comparison_decision(result_bundle, artifact)

    assert decision["outcome"] == "CONSENSUS"
    assert artifact["agreement"][0]["provider_count"] == 3
    assert artifact["disagreement"] == []
    _assert_comparison_governance_boundary(comparison)
    _assert_replay_lineage(tmp_path, result_bundle, comparison)


def test_cognition_comparison_certifies_partial_consensus_when_majority_agrees(tmp_path) -> None:
    payloads = {
        "provider-a": {
            "findings": ["Majority conclusion: request clarification before execution."],
            "assumptions": ["Provider output remains advisory."],
            "alternatives": ["Ask a bounded question."],
            "risks": ["Ambiguity remains."],
            "uncertainties": ["Scope may be incomplete."],
            "confidence": "HIGH",
        },
        "provider-b": {
            "findings": ["Majority conclusion: request clarification before execution."],
            "assumptions": ["Provider output remains advisory."],
            "alternatives": ["Ask a bounded question."],
            "risks": ["Ambiguity remains."],
            "uncertainties": ["Scope may be incomplete."],
            "confidence": "HIGH",
        },
        "provider-c": {
            "findings": ["Minority conclusion: proceed to PPP candidate staging."],
            "assumptions": ["Provider output remains advisory."],
            "alternatives": ["Stage the candidate."],
            "risks": ["Premature staging could be confusing."],
            "uncertainties": ["Approval evidence may be incomplete."],
            "confidence": "MEDIUM",
        },
    }
    result_bundle, comparison = _run_comparison(tmp_path, payloads=payloads)
    decision = _certified_comparison_decision(result_bundle, comparison["cognition_comparison_artifact"])

    assert decision["outcome"] == "PARTIAL_CONSENSUS"
    assert decision["majority_count"] == 1
    _assert_comparison_governance_boundary(comparison)
    _assert_replay_lineage(tmp_path, result_bundle, comparison)


def test_cognition_comparison_certifies_conflict_when_providers_disagree(tmp_path) -> None:
    payloads = {
        "provider-a": {
            "findings": ["Provider A conclusion: request clarification."],
            "assumptions": ["A assumes missing scope."],
            "alternatives": ["Ask the human."],
            "risks": ["Ambiguity risk."],
            "uncertainties": ["Scope unknown."],
            "confidence": "MEDIUM",
        },
        "provider-b": {
            "findings": ["Provider B conclusion: continue to PPP candidate."],
            "assumptions": ["B assumes scope is adequate."],
            "alternatives": ["Stage a candidate."],
            "risks": ["Approval risk."],
            "uncertainties": ["Approval status unknown."],
            "confidence": "MEDIUM",
        },
        "provider-c": {
            "findings": ["Provider C conclusion: stop pending more evidence."],
            "assumptions": ["C assumes evidence is stale."],
            "alternatives": ["Gather evidence."],
            "risks": ["Evidence risk."],
            "uncertainties": ["Evidence freshness unknown."],
            "confidence": "MEDIUM",
        },
    }
    result_bundle, comparison = _run_comparison(tmp_path, payloads=payloads)
    artifact = comparison["cognition_comparison_artifact"]
    decision = _certified_comparison_decision(result_bundle, artifact)

    assert decision["outcome"] == "CONFLICT"
    assert decision["clarification_can_be_requested"] is True
    assert len(artifact["disagreement"]) == 3
    assert artifact["comparison_confidence"] == "MEDIUM"
    _assert_comparison_governance_boundary(comparison)
    _assert_replay_lineage(tmp_path, result_bundle, comparison)


def test_cognition_comparison_certifies_insufficient_information_for_missing_evidence(tmp_path) -> None:
    payloads = {
        "provider-a": {
            "findings": ["Available conclusion: evidence is incomplete."],
            "confidence": "LOW",
        },
        "provider-b": {
            "findings": ["Available conclusion: evidence is incomplete."],
            "confidence": "LOW",
        },
        "provider-c": {
            "findings": ["Unavailable due to provider failure."],
            "confidence": "UNKNOWN",
        },
    }
    result_bundle, comparison = _run_comparison(tmp_path, payloads=payloads, failing_provider="provider-c")
    artifact = comparison["cognition_comparison_artifact"]
    decision = _certified_comparison_decision(result_bundle, artifact)

    assert decision["outcome"] == "INSUFFICIENT_INFORMATION"
    assert decision["clarification_can_be_requested"] is True
    assert result_bundle["failed_provider_count"] == 1
    assert any(item["source"] == "provider_failure" for item in artifact["uncertainty"])
    assert any(item["missing"] == "complete_provider_set" for item in artifact["missing_information"])
    _assert_comparison_governance_boundary(comparison)
    _assert_replay_lineage(tmp_path, result_bundle, comparison)
