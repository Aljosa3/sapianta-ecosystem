"""Tests for AIGOL_OCS_COGNITION_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.ocs_cognition_runtime import (
    OCS_COGNITION_ARTIFACT_V1,
    OCS_COGNITION_COMPLETED,
    PROVIDER_REQUIRED,
    PROVIDER_UNDETERMINED,
    run_ocs_cognition,
    reconstruct_ocs_cognition_replay,
)
from aigol.runtime.ocs_context_assembly_runtime import assemble_ocs_context
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-04T13:00:00+00:00"


def _source_artifact(artifact_type: str, artifact_id: str, **extra: object) -> dict:
    artifact = {
        "artifact_type": artifact_type,
        "artifact_id": artifact_id,
        "replay_visible": True,
        "authority": False,
        **extra,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _ocs_context(tmp_path) -> dict:
    capture = assemble_ocs_context(
        context_assembly_id="OCS-CONTEXT-FOR-COGNITION-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "context",
        source_chain_id="CHAIN-OCS-000001",
        source_request_reference="PROMPT-OCS-000001",
        source_context={
            "conversation_context": [
                _source_artifact("CONVERSATION_RESPONSE_ARTIFACT_V1", "CONVERSATION-000001")
            ],
            "clarification_context": [
                _source_artifact("HUMAN_CLARIFICATION_RESOLUTION_ARTIFACT_V1", "CLARIFICATION-000001")
            ],
            "ppp_context": [
                _source_artifact(
                    "RESOURCE_PPP_INTEGRATION_ARTIFACT_V1",
                    "PPP-TRADING-MARKET_EVIDENCE_NORMALIZATION-000001",
                    ppp_resource_status="PPP_PROVIDER_PROPOSAL_READY",
                    provider_necessity_classification=PROVIDER_REQUIRED,
                )
            ],
            "approval_context": [
                _source_artifact("HUMAN_DECISION_ARTIFACT_V1", "APPROVAL-000001", decision_status="APPROVED")
            ],
            "replay_visible_operation_context": [
                _source_artifact("UNIFIED_REPLAY_RECONSTRUCTION_REPORT_V1", "REPLAY-000001", status="READY")
            ],
            "domain_context": [
                _source_artifact("DOMAIN_FOUNDATION_ARTIFACT_V1", "TRADING-DOMAIN-000001", domain_id="TRADING")
            ],
            "registry_context": [
                _source_artifact(
                    "DOMAIN_BUNDLE_RESOLUTION_ARTIFACT_V1",
                    "REGISTRY-000001",
                    domain_id="TRADING",
                    bundle_id="TRADING_EXECUTABLE_DOMAIN_BUNDLE_V1",
                    resolution_status="DOMAIN_BUNDLE_RESOLVED",
                )
            ],
        },
    )
    return capture["ocs_context_assembly_artifact"]


def test_ocs_cognition_builds_reconstructable_cognition_artifact(tmp_path) -> None:
    capture = run_ocs_cognition(
        cognition_id="OCS-COGNITION-000001",
        ocs_context_assembly_artifact=_ocs_context(tmp_path),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "cognition",
    )
    reconstructed = reconstruct_ocs_cognition_replay(tmp_path / "cognition")
    artifact = capture["ocs_cognition_artifact"]

    assert artifact["artifact_type"] == OCS_COGNITION_ARTIFACT_V1
    assert capture["cognition_status"] == OCS_COGNITION_COMPLETED
    assert capture["task_intent"]["intent"] == "PPP_HANDOFF_INTENT"
    assert capture["provider_necessity"]["necessity_classification"] == PROVIDER_REQUIRED
    assert capture["domain_candidates"] == [
        {
            "domain_id": "TRADING",
            "confidence": "HIGH",
            "evidence": ["bundle_id", "domain_id", "source_reference"],
            "authority": False,
        }
    ]
    assert capture["worker_candidates"] == [
        {
            "worker_family_id": "MARKET_EVIDENCE_NORMALIZATION",
            "confidence": "MEDIUM",
            "evidence": ["source_id"],
            "authority": False,
        }
    ]
    assert capture["ambiguity"]["is_ambiguous"] is False
    assert artifact["authority_flags"]["authorizes_execution"] is False
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False
    assert capture["dispatch_requested"] is False
    assert capture["governance_modified"] is False
    assert capture["replay_modified"] is False
    assert reconstructed["cognition_status"] == OCS_COGNITION_COMPLETED
    assert reconstructed["cognition_hash"] == capture["cognition_hash"]
    assert reconstructed["replay_artifact_count"] == 2


def test_ocs_cognition_is_deterministic_for_same_context(tmp_path) -> None:
    context = _ocs_context(tmp_path)
    first = run_ocs_cognition(
        cognition_id="OCS-COGNITION-DETERMINISTIC-000001",
        ocs_context_assembly_artifact=context,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "first",
    )
    second = run_ocs_cognition(
        cognition_id="OCS-COGNITION-DETERMINISTIC-000002",
        ocs_context_assembly_artifact=context,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "second",
    )

    assert first["cognition_hash"] == second["cognition_hash"]
    assert reconstruct_ocs_cognition_replay(tmp_path / "first")["cognition_hash"] == first["cognition_hash"]
    assert reconstruct_ocs_cognition_replay(tmp_path / "second")["cognition_hash"] == second["cognition_hash"]


def test_ocs_cognition_identifies_ambiguity_and_clarification_requirement(tmp_path) -> None:
    context = _ocs_context(tmp_path)
    extra = {
        "category": "domain_context",
        "source_id": "HEALTHCARE-DOMAIN-000001",
        "artifact_type": "DOMAIN_FOUNDATION_ARTIFACT_V1",
        "source_hash": "sha256:healthcare",
        "source_fingerprint": "sha256:healthcare-fingerprint",
        "summary": {"domain_id": "HEALTHCARE"},
        "dedupe_status": "ACCEPTED",
        "replay_visible": True,
        "authority": False,
    }
    context["accepted_inputs"].append(extra)
    context["accepted_input_count"] += 1
    for section in context["context_sections"]:
        if section["category"] == "domain_context":
            section["source_count"] += 1
            section["sources"].append(
                {
                    "source_id": extra["source_id"],
                    "artifact_type": extra["artifact_type"],
                    "source_hash": extra["source_hash"],
                    "summary": extra["summary"],
                }
            )
    _rehash_context_artifact(context)

    capture = run_ocs_cognition(
        cognition_id="OCS-COGNITION-AMBIGUOUS-000001",
        ocs_context_assembly_artifact=context,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "ambiguous",
    )

    assert capture["ambiguity"]["is_ambiguous"] is True
    assert "multiple domain candidates" in capture["ambiguity"]["ambiguity_reasons"]
    assert any(item["required"] is True for item in capture["clarification_requirements"])


def test_ocs_cognition_fails_closed_on_invalid_context_hash(tmp_path) -> None:
    context = _ocs_context(tmp_path)
    context["context_hash"] = "sha256:corrupted"
    context["artifact_hash"] = replay_hash({key: value for key, value in context.items() if key != "artifact_hash"})

    capture = run_ocs_cognition(
        cognition_id="OCS-COGNITION-INVALID-CONTEXT-000001",
        ocs_context_assembly_artifact=context,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "invalid_context",
    )

    assert capture["fail_closed"] is True
    assert capture["cognition_status"] == "FAILED_CLOSED"
    assert "hash mismatch" in capture["failure_reason"]
    assert capture["provider_necessity"]["necessity_classification"] == PROVIDER_UNDETERMINED


def test_ocs_cognition_reconstruction_detects_corrupt_replay(tmp_path) -> None:
    run_ocs_cognition(
        cognition_id="OCS-COGNITION-CORRUPT-000001",
        ocs_context_assembly_artifact=_ocs_context(tmp_path),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt",
    )
    path = tmp_path / "corrupt" / "000_ocs_cognition_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["cognition_hash"] = "sha256:corrupted"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_ocs_cognition_replay(tmp_path / "corrupt")


def test_ocs_cognition_preserves_authority_boundaries() -> None:
    import aigol.runtime.ocs_cognition_runtime as runtime

    source = inspect.getsource(runtime)

    assert "OpenAIProviderAdapter" not in source
    assert "run_provider_attachment(" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source


def _rehash_context_artifact(context: dict) -> None:
    context_hash_input = {
        "contract_reference": context["contract_reference"],
        "source_chain_id": context.get("source_chain_id"),
        "source_request_reference": context.get("source_request_reference"),
        "input_categories": context["input_categories"],
        "accepted_inputs": context["accepted_inputs"],
        "rejected_inputs": context["rejected_inputs"],
        "context_sections": context["context_sections"],
        "normalization_policy": context["normalization_policy"],
        "known_gaps": context["known_gaps"],
        "authority_flags": context["authority_flags"],
        "context_status": context["context_status"],
        "failure_reason": context["failure_reason"],
    }
    context["context_hash"] = replay_hash(context_hash_input)
    context["artifact_hash"] = replay_hash({key: value for key, value in context.items() if key != "artifact_hash"})
