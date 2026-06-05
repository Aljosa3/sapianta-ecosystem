"""Tests for AIGOL_COGNITION_COMPARISON_RUNTIME_V1."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aigol.runtime.cognition_comparison_runtime import (
    CERTIFIED_CLASSIFICATION,
    COGNITION_COMPARISON_ARTIFACT_V1,
    FINAL_CLASSIFICATION,
    STATUS_COMPLETED,
    STATUS_FAILED_CLOSED,
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


CREATED_AT = "2026-06-05T00:00:00Z"


def _conversation_source() -> dict:
    artifact = {
        "artifact_type": "HUMAN_REQUEST_ARTIFACT_V1",
        "artifact_id": "HUMAN-REQUEST-COMPARISON-001",
        "status": "REPLAY_VISIBLE",
        "summary": "Human asks for comparison of multiple cognition providers.",
        "replay_visible": True,
        "authority": False,
        "execution_requested": False,
        "worker_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _context(tmp_path: Path) -> dict:
    capture = assemble_ocs_context(
        context_assembly_id="OCS-CONTEXT-COMPARISON-001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "ocs_context",
        source_context={"conversation_context": [_conversation_source()]},
        source_chain_id="CHAIN-COMPARISON-001",
        source_request_reference="HUMAN-REQUEST-COMPARISON-001",
    )
    assert capture["fail_closed"] is False
    return capture["ocs_context_assembly_artifact"]


def _contracts() -> list[dict]:
    return [
        create_default_cognition_provider_contract(provider_id="provider-a", created_at=CREATED_AT),
        create_default_cognition_provider_contract(provider_id="provider-b", created_at=CREATED_AT),
        create_default_cognition_provider_contract(provider_id="provider-c", created_at=CREATED_AT),
    ]


def _provider_text(provider_id: str) -> str:
    return json.dumps(
        {
            "findings": [
                "Shared finding: OCS context supports provider-assisted cognition.",
                f"{provider_id} provider-specific finding.",
            ],
            "assumptions": [
                "Shared assumption: provider output remains advisory.",
                f"{provider_id} assumption differs.",
            ],
            "alternatives": [f"{provider_id} alternative differs."],
            "risks": [f"{provider_id} risk differs."],
            "uncertainties": [f"{provider_id} uncertainty remains."],
            "confidence": "HIGH",
        },
        sort_keys=True,
    )


def _transports(*, failing_provider: str | None = None):
    transports = {}
    for provider_id in ("provider-a", "provider-b", "provider-c"):
        def call(_payload: dict, metadata: dict, provider_id: str = provider_id) -> dict:
            assert metadata["provider_role"] == "COGNITION_PROVIDER"
            if failing_provider == provider_id:
                raise FailClosedRuntimeError(f"{provider_id} failed closed")
            return {"output_text": _provider_text(provider_id)}

        transports[provider_id] = call
    return transports


def _multi_result(tmp_path: Path, *, failing_provider: str | None = None) -> dict:
    capture = run_multi_provider_cognition_runtime(
        multi_provider_cognition_bundle_id="MULTI-PROVIDER-COMPARISON-001",
        human_request="Compare multiple cognition providers.",
        ocs_context_artifact=_context(tmp_path),
        provider_contracts=_contracts(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "multi_provider_cognition",
        transport_registry=_transports(failing_provider=failing_provider),
    )
    assert capture["fail_closed"] is False
    return capture["result_bundle"]


def _run_comparison(tmp_path: Path, *, failing_provider: str | None = None, **overrides) -> dict:
    args = {
        "cognition_comparison_id": "COGNITION-COMPARISON-001",
        "multi_provider_result_bundle": _multi_result(tmp_path / "multi", failing_provider=failing_provider),
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / "comparison",
    }
    args.update(overrides)
    return run_cognition_comparison_runtime(**args)


def test_cognition_comparison_detects_agreement_disagreement_conflicts_and_confidence(tmp_path):
    result = _run_comparison(tmp_path)
    artifact = result["cognition_comparison_artifact"]
    replay = reconstruct_cognition_comparison_replay(tmp_path / "comparison")

    assert result["final_classification"] == FINAL_CLASSIFICATION
    assert result["classification"] == CERTIFIED_CLASSIFICATION
    assert result["final_status"] == STATUS_COMPLETED
    assert artifact["artifact_type"] == COGNITION_COMPARISON_ARTIFACT_V1
    assert artifact["comparison_confidence"] == "MEDIUM"
    assert artifact["source_result_bundle_hash"].startswith("sha256:")
    assert len(artifact["source_cognition_artifacts"]) == 3
    assert artifact["agreement"][0]["text"] == "Shared finding: OCS context supports provider-assisted cognition."
    assert len(artifact["disagreement"]) == 3
    assert len(artifact["conflicting_assumptions"]) == 3
    assert len(artifact["conflicting_risks"]) == 3
    assert len(artifact["conflicting_alternatives"]) == 3
    assert replay["comparison_confidence"] == "MEDIUM"


def test_provider_failures_become_uncertainty_and_missing_information(tmp_path):
    result = _run_comparison(tmp_path, failing_provider="provider-c")
    artifact = result["cognition_comparison_artifact"]

    assert len(artifact["source_cognition_artifacts"]) == 2
    assert any(item["source"] == "provider_failure" for item in artifact["uncertainty"])
    assert any(item["missing"] == "complete_provider_set" for item in artifact["missing_information"])
    assert artifact["comparison_confidence"] == "MEDIUM"


def test_comparison_remains_non_authoritative(tmp_path):
    result = _run_comparison(tmp_path)
    artifact = result["cognition_comparison_artifact"]

    assert artifact["non_authoritative"] is True
    assert artifact["human_review_required"] is True
    assert artifact["approval_created"] is False
    assert artifact["worker_invoked"] is False
    assert artifact["execution_requested"] is False
    assert artifact["governance_modified"] is False
    assert artifact["replay_modified"] is False
    assert all(value is False for value in artifact["authority_flags"].values())


def test_less_than_two_cognition_artifacts_fails_closed(tmp_path):
    result_bundle = _multi_result(tmp_path / "multi", failing_provider="provider-b")
    result_bundle["provider_results"] = result_bundle["provider_results"][:1]
    result_bundle["successful_provider_count"] = 1
    result_bundle["cognition_artifact_hashes"] = [result_bundle["provider_results"][0]["cognition_artifact_hash"]]
    result_bundle["result_bundle_hash"] = replay_hash(
        {
            "multi_provider_cognition_bundle_id": result_bundle["multi_provider_cognition_bundle_id"],
            "request_bundle_hash": result_bundle["request_bundle_hash"],
            "context_hash": result_bundle["context_hash"],
            "provider_count": result_bundle["provider_count"],
            "successful_provider_count": result_bundle["successful_provider_count"],
            "failed_provider_count": result_bundle["failed_provider_count"],
            "cognition_artifact_hashes": result_bundle["cognition_artifact_hashes"],
            "provider_failure_hashes": result_bundle["provider_failure_hashes"],
            "comparison_performed": result_bundle["comparison_performed"],
            "confidence_aggregation_performed": result_bundle["confidence_aggregation_performed"],
            "authority_flags": result_bundle["authority_flags"],
        }
    )
    result_bundle.pop("artifact_hash")
    result_bundle["artifact_hash"] = replay_hash(result_bundle)

    result = run_cognition_comparison_runtime(
        cognition_comparison_id="COGNITION-COMPARISON-002",
        multi_provider_result_bundle=result_bundle,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "comparison",
    )

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert "at least two cognition artifacts" in result["failure_reason"]


def test_source_bundle_with_prior_comparison_fails_closed(tmp_path):
    result_bundle = _multi_result(tmp_path / "multi")
    result_bundle["comparison_performed"] = True
    result_bundle["result_bundle_hash"] = replay_hash(
        {
            "multi_provider_cognition_bundle_id": result_bundle["multi_provider_cognition_bundle_id"],
            "request_bundle_hash": result_bundle["request_bundle_hash"],
            "context_hash": result_bundle["context_hash"],
            "provider_count": result_bundle["provider_count"],
            "successful_provider_count": result_bundle["successful_provider_count"],
            "failed_provider_count": result_bundle["failed_provider_count"],
            "cognition_artifact_hashes": result_bundle["cognition_artifact_hashes"],
            "provider_failure_hashes": result_bundle["provider_failure_hashes"],
            "comparison_performed": result_bundle["comparison_performed"],
            "confidence_aggregation_performed": result_bundle["confidence_aggregation_performed"],
            "authority_flags": result_bundle["authority_flags"],
        }
    )
    result_bundle.pop("artifact_hash")
    result_bundle["artifact_hash"] = replay_hash(result_bundle)

    result = run_cognition_comparison_runtime(
        cognition_comparison_id="COGNITION-COMPARISON-003",
        multi_provider_result_bundle=result_bundle,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "comparison",
    )

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert "already contains comparison" in result["failure_reason"]


def test_replay_tampering_is_detected(tmp_path):
    _run_comparison(tmp_path)
    path = tmp_path / "comparison" / "000_cognition_comparison_artifact.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["comparison_confidence"] = "HIGH"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="replay hash mismatch"):
        reconstruct_cognition_comparison_replay(tmp_path / "comparison")


def test_append_only_replay_collision_fails_closed(tmp_path):
    _run_comparison(tmp_path)
    result = run_cognition_comparison_runtime(
        cognition_comparison_id="COGNITION-COMPARISON-004",
        multi_provider_result_bundle=_multi_result(tmp_path / "second_multi"),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "comparison",
    )

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert "already exists" in result["failure_reason"]
