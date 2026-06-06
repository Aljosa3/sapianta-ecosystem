"""Tests for AIGOL_MULTI_PROVIDER_COGNITION_RUNTIME_V1."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.multi_provider_cognition_runtime import (
    CERTIFIED_CLASSIFICATION,
    FINAL_CLASSIFICATION,
    LLM_COGNITION_ARTIFACT_V1,
    MULTI_PROVIDER_COGNITION_REQUEST_BUNDLE_V1,
    MULTI_PROVIDER_COGNITION_RESULT_BUNDLE_V1,
    PROVIDER_COGNITION_FAILURE_ARTIFACT_V1,
    STATUS_COMPLETED,
    create_default_cognition_provider_contract,
    reconstruct_multi_provider_cognition_replay,
    run_multi_provider_cognition_runtime,
)
from aigol.runtime.ocs_context_assembly_runtime import assemble_ocs_context
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-06-05T00:00:00Z"


def _conversation_source() -> dict:
    artifact = {
        "artifact_type": "HUMAN_REQUEST_ARTIFACT_V1",
        "artifact_id": "HUMAN-REQUEST-MULTI-PROVIDER-001",
        "status": "REPLAY_VISIBLE",
        "summary": "Human asks for multiple isolated cognition providers.",
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
        context_assembly_id="OCS-CONTEXT-MULTI-PROVIDER-001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "ocs_context",
        source_context={"conversation_context": [_conversation_source()]},
        source_chain_id="CHAIN-MULTI-PROVIDER-001",
        source_request_reference="HUMAN-REQUEST-MULTI-PROVIDER-001",
    )
    assert capture["fail_closed"] is False
    return capture["ocs_context_assembly_artifact"]


def _contracts() -> list[dict]:
    return [
        create_default_cognition_provider_contract(provider_id="provider-a", provider_label="Provider A", created_at=CREATED_AT),
        create_default_cognition_provider_contract(provider_id="provider-b", provider_label="Provider B", created_at=CREATED_AT),
        create_default_cognition_provider_contract(provider_id="provider-c", provider_label="Provider C", created_at=CREATED_AT),
    ]


def _provider_text(provider_id: str) -> str:
    return json.dumps(
        {
            "findings": [f"{provider_id} produced an isolated cognition finding."],
            "assumptions": [f"{provider_id} remains non-authoritative."],
            "alternatives": [f"{provider_id} suggests human review before downstream use."],
            "risks": [f"{provider_id} output is provider-specific."],
            "uncertainties": ["No comparison is performed in this milestone."],
            "confidence": "MEDIUM",
        },
        sort_keys=True,
    )


def _transports(*, failing_provider: str | None = None):
    transports = {}
    for provider_id in ("provider-a", "provider-b", "provider-c"):
        def call(_payload: dict, metadata: dict, provider_id: str = provider_id) -> dict:
            assert metadata["provider_role"] == "COGNITION_PROVIDER"
            assert metadata["provider_id"] == provider_id
            if failing_provider == provider_id:
                raise FailClosedRuntimeError(f"{provider_id} unavailable")
            return {"output_text": _provider_text(provider_id)}

        transports[provider_id] = call
    return transports


def _run(tmp_path: Path, **overrides):
    args = {
        "multi_provider_cognition_bundle_id": "MULTI-PROVIDER-COGNITION-001",
        "human_request": "Ask multiple cognition providers for isolated analysis.",
        "ocs_context_artifact": _context(tmp_path),
        "provider_contracts": _contracts(),
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / "multi_provider_cognition",
        "transport_registry": _transports(),
    }
    args.update(overrides)
    return run_multi_provider_cognition_runtime(**args)


def test_multiple_approved_providers_produce_independent_cognition_artifacts(tmp_path):
    result = _run(tmp_path)
    replay = reconstruct_multi_provider_cognition_replay(tmp_path / "multi_provider_cognition")

    assert result["final_classification"] == FINAL_CLASSIFICATION
    assert result["classification"] == CERTIFIED_CLASSIFICATION
    assert result["final_status"] == STATUS_COMPLETED
    assert result["request_bundle"]["artifact_type"] == MULTI_PROVIDER_COGNITION_REQUEST_BUNDLE_V1
    assert result["result_bundle"]["artifact_type"] == MULTI_PROVIDER_COGNITION_RESULT_BUNDLE_V1
    assert result["successful_provider_count"] == 3
    assert result["failed_provider_count"] == 0
    assert result["comparison_performed"] is False
    assert result["confidence_aggregation_performed"] is False
    assert len(result["provider_results"]) == 3
    assert replay["successful_provider_count"] == 3
    assert replay["failed_provider_count"] == 0
    for provider_result in result["provider_results"]:
        cognition_artifact = provider_result["llm_cognition_artifact"]
        assert cognition_artifact["artifact_type"] == LLM_COGNITION_ARTIFACT_V1
        assert cognition_artifact["canonical_provider_assisted_cognition_output"] is True
        assert cognition_artifact["context_hash"] == result["result_bundle"]["context_hash"]
        assert provider_result["comparison_performed"] is False


def test_openai_responses_api_nested_output_text_produces_cognition_artifact(tmp_path):
    def openai_shape_transport(_payload: dict, metadata: dict) -> dict:
        assert metadata["provider_role"] == "COGNITION_PROVIDER"
        return {
            "id": "response-openai-shape",
            "object": "response",
            "output": [
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": _provider_text(metadata["provider_id"]),
                            "annotations": [],
                        }
                    ],
                }
            ],
        }

    transports = _transports()
    transports["provider-a"] = openai_shape_transport
    result = _run(tmp_path, transport_registry=transports)

    assert result["final_status"] == STATUS_COMPLETED
    assert result["successful_provider_count"] == 3
    provider_a = next(item for item in result["provider_results"] if item["provider_id"] == "provider-a")
    response = provider_a["provider_response_artifact"]
    cognition_artifact = provider_a["llm_cognition_artifact"]
    assert response["response_text"] == _provider_text("provider-a")
    assert response["provider_invoked"] is True
    assert cognition_artifact["artifact_type"] == LLM_COGNITION_ARTIFACT_V1
    assert cognition_artifact["canonical_provider_assisted_cognition_output"] is True


def test_provider_failure_is_isolated_and_remaining_providers_continue(tmp_path):
    result = _run(tmp_path, transport_registry=_transports(failing_provider="provider-b"))

    assert result["final_status"] == STATUS_COMPLETED
    assert result["successful_provider_count"] == 2
    assert result["failed_provider_count"] == 1
    assert len(result["provider_results"]) == 2
    assert len(result["provider_failures"]) == 1
    failure = result["provider_failures"][0]
    assert failure["artifact_type"] == PROVIDER_COGNITION_FAILURE_ARTIFACT_V1
    assert failure["provider_id"] == "provider-b"
    assert failure["failure_isolated"] is True
    assert "provider-b unavailable" in failure["failure_reason"]


def test_unapproved_provider_contract_becomes_isolated_failure(tmp_path):
    contracts = _contracts()
    contracts[1]["provider_approved"] = False
    contracts[1].pop("artifact_hash")
    contracts[1]["artifact_hash"] = replay_hash(contracts[1])

    result = _run(tmp_path, provider_contracts=contracts)

    assert result["final_status"] == STATUS_COMPLETED
    assert result["successful_provider_count"] == 2
    assert result["failed_provider_count"] == 1
    assert result["provider_failures"][0]["provider_id"] == "provider-b"
    assert "provider is not approved" in result["provider_failures"][0]["failure_reason"]


def test_no_downstream_authority_or_comparison_is_created(tmp_path):
    result = _run(tmp_path)
    bundle = result["result_bundle"]

    assert bundle["comparison_performed"] is False
    assert bundle["confidence_aggregation_performed"] is False
    assert bundle["worker_invoked"] is False
    assert bundle["approval_created"] is False
    assert bundle["execution_requested"] is False
    assert bundle["governance_modified"] is False
    assert bundle["replay_modified"] is False
    assert all(value is False for value in bundle["authority_flags"].values())


def test_replay_reconstructs_request_result_artifacts_and_failures(tmp_path):
    _run(tmp_path, transport_registry=_transports(failing_provider="provider-c"))
    replay = reconstruct_multi_provider_cognition_replay(tmp_path / "multi_provider_cognition")

    assert replay["provider_count"] == 3
    assert replay["successful_provider_count"] == 2
    assert replay["failed_provider_count"] == 1
    assert len(replay["cognition_artifact_hashes"]) == 2
    assert len(replay["provider_failure_hashes"]) == 1
    assert replay["comparison_performed"] is False


def test_replay_tampering_is_detected(tmp_path):
    _run(tmp_path)
    path = tmp_path / "multi_provider_cognition" / "001_multi_provider_cognition_result_bundle.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["successful_provider_count"] = 99
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="replay hash mismatch"):
        reconstruct_multi_provider_cognition_replay(tmp_path / "multi_provider_cognition")


def test_append_only_replay_collision_fails_closed(tmp_path):
    _run(tmp_path)
    result = _run(
        tmp_path / "second_context",
        replay_dir=tmp_path / "multi_provider_cognition",
    )

    assert result["final_status"] == "FAILED_CLOSED"
    assert "already exists" in result["failure_reason"]
