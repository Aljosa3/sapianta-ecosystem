"""Tests for AIGOL_CONVERSATION_TO_IMPLEMENTATION_HANDOFF_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from aigol.runtime.conversation_to_implementation_handoff_runtime import (
    IMPLEMENTATION_HANDOFF_ARTIFACT_V1,
    IMPLEMENTATION_HANDOFF_CREATED,
    create_conversation_to_implementation_handoff,
    reconstruct_conversation_to_implementation_handoff_replay,
)
from aigol.runtime.development_context_assembly_runtime import assemble_development_context
from aigol.runtime.development_proposal_contract_runtime import (
    DEVELOPMENT_PROPOSAL_ARTIFACT_V1,
    validate_development_proposal_contract,
)
from aigol.runtime.domain_and_worker_resolution_registry import resolve_domain_worker_milestone
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.native_development_task_intake_runtime import run_native_development_task_intake
from aigol.runtime.provider_necessity_policy_runtime import classify_provider_necessity
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE_ROOT = ROOT / "governance"
CREATED_AT = "2026-06-02T20:00:00+00:00"
MILESTONE_ID = "TRADING_MARKET_EVIDENCE_NORMALIZATION_WORKER_FOUNDATION_V1"


def _evidence_chain(tmp_path) -> tuple[dict, dict, dict, dict, dict]:
    intake_capture = run_native_development_task_intake(
        intake_id="INTAKE-HANDOFF-000001",
        human_prompt_reference="PROMPT-HANDOFF-000001",
        human_prompt=(
            f"Implement {MILESTONE_ID}. Foundation only. No broker integration. "
            "No exchange integration. No order placement. No live trading."
        ),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "intake",
    )
    context_capture = assemble_development_context(
        context_assembly_id="CONTEXT-HANDOFF-000001",
        development_task_intake_artifact=intake_capture["native_development_task_intake_artifact"],
        governance_root=GOVERNANCE_ROOT,
        replay_dir=tmp_path / "context",
        created_at=CREATED_AT,
    )
    registry_capture = resolve_domain_worker_milestone(
        resolution_id="REGISTRY-HANDOFF-000001",
        domain_id="TRADING",
        worker_family_id="MARKET_EVIDENCE_NORMALIZATION",
        milestone_type="WORKER_FOUNDATION",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "registry",
    )
    provider_policy_capture = classify_provider_necessity(
        policy_decision_id="PROVIDER-POLICY-HANDOFF-000001",
        workflow_type="NATIVE_DEVELOPMENT",
        task_kind="WORKER_FOUNDATION",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "provider_policy",
    )
    context = context_capture["development_context_assembly_artifact"]
    registry = registry_capture["domain_worker_resolution_artifact"]
    proposal = _proposal(context, registry)
    contract_capture = validate_development_proposal_contract(
        contract_validation_id="CONTRACT-HANDOFF-000001",
        proposal_artifact=proposal,
        context_assembly_artifact=context,
        registry_resolution_artifact=registry,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "contract",
    )
    return (
        proposal,
        contract_capture["development_proposal_contract_validation_artifact"],
        context,
        registry,
        provider_policy_capture["provider_necessity_policy_artifact"],
    )


def _proposal(context: dict, registry: dict, *, overrides: dict | None = None) -> dict:
    proposal = {
        "artifact_type": DEVELOPMENT_PROPOSAL_ARTIFACT_V1,
        "proposal_id": "PROPOSAL-HANDOFF-000001",
        "task_reference": context["development_task_intake_reference"],
        "context_reference": context["context_assembly_id"],
        "context_hash": context["context_hash"],
        "domain_reference": registry["domain_id"],
        "worker_reference": registry["worker_family_id"],
        "milestone_reference": registry["milestone_type"],
        "proposal_summary": "Define a foundation-only Market Evidence Normalization Worker.",
        "proposed_outputs": [
            "governance/TRADING_MARKET_EVIDENCE_NORMALIZATION_WORKER_FOUNDATION_V1.md",
            "governance/TRADING_MARKET_EVIDENCE_NORMALIZATION_WORKER_CERTIFICATION.json",
        ],
        "constraints_acknowledged": [
            "NO_BROKER_INTEGRATION",
            "NO_EXCHANGE_INTEGRATION",
            "NO_ORDER_PLACEMENT",
            "NO_LIVE_TRADING",
        ],
        "assumptions": [
            "Trading Domain context is certified.",
        ],
        "known_gaps": [
            "Implementation remains separate from handoff.",
        ],
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
    if overrides:
        proposal.update(overrides)
    proposal["artifact_hash"] = replay_hash(proposal)
    return proposal


def test_conversation_to_implementation_handoff_creates_replay_visible_packet(tmp_path) -> None:
    proposal, validation, context, registry, provider_policy = _evidence_chain(tmp_path)

    capture = create_conversation_to_implementation_handoff(
        handoff_id="HANDOFF-000001",
        proposal_artifact=proposal,
        proposal_contract_validation_artifact=validation,
        context_assembly_artifact=context,
        registry_resolution_artifact=registry,
        provider_necessity_policy_artifact=provider_policy,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "handoff",
    )
    reconstructed = reconstruct_conversation_to_implementation_handoff_replay(tmp_path / "handoff")
    artifact = capture["implementation_handoff_artifact"]

    assert artifact["artifact_type"] == IMPLEMENTATION_HANDOFF_ARTIFACT_V1
    assert capture["handoff_status"] == IMPLEMENTATION_HANDOFF_CREATED
    assert capture["task_reference"] == proposal["task_reference"]
    assert capture["proposal_reference"] == proposal["proposal_id"]
    assert capture["proposal_hash"] == proposal["artifact_hash"]
    assert capture["context_hash"] == context["context_hash"]
    assert capture["domain_reference"] == "TRADING"
    assert capture["worker_reference"] == "MARKET_EVIDENCE_NORMALIZATION"
    assert capture["milestone_reference"] == "WORKER_FOUNDATION"
    assert capture["output_targets"] == proposal["proposed_outputs"]
    assert capture["validation_references"]["proposal_contract_validation_reference"] == validation["contract_validation_id"]
    assert capture["implementation_authorized"] is False
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False
    assert reconstructed["handoff_status"] == IMPLEMENTATION_HANDOFF_CREATED
    assert reconstructed["replay_artifact_count"] == 2


def test_handoff_fails_closed_when_proposal_validation_failed(tmp_path) -> None:
    proposal, validation, context, registry, provider_policy = _evidence_chain(tmp_path)
    validation["validation_status"] = "FAILED_CLOSED"
    validation["artifact_hash"] = replay_hash({key: value for key, value in validation.items() if key != "artifact_hash"})

    capture = create_conversation_to_implementation_handoff(
        handoff_id="HANDOFF-FAILED-VALIDATION-000001",
        proposal_artifact=proposal,
        proposal_contract_validation_artifact=validation,
        context_assembly_artifact=context,
        registry_resolution_artifact=registry,
        provider_necessity_policy_artifact=provider_policy,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "failed_validation",
    )

    assert capture["fail_closed"] is True
    assert "proposal validation failed" in capture["failure_reason"]


def test_handoff_fails_closed_when_references_are_missing(tmp_path) -> None:
    proposal, validation, context, registry, provider_policy = _evidence_chain(tmp_path)
    proposal["context_reference"] = "UNKNOWN_CONTEXT"
    proposal["artifact_hash"] = replay_hash({key: value for key, value in proposal.items() if key != "artifact_hash"})
    validation["proposal_hash"] = proposal["artifact_hash"]
    validation["artifact_hash"] = replay_hash({key: value for key, value in validation.items() if key != "artifact_hash"})

    capture = create_conversation_to_implementation_handoff(
        handoff_id="HANDOFF-MISSING-REFERENCE-000001",
        proposal_artifact=proposal,
        proposal_contract_validation_artifact=validation,
        context_assembly_artifact=context,
        registry_resolution_artifact=registry,
        provider_necessity_policy_artifact=provider_policy,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "missing_reference",
    )

    assert capture["fail_closed"] is True
    assert "references are missing" in capture["failure_reason"]


def test_handoff_fails_closed_on_hash_mismatch(tmp_path) -> None:
    proposal, validation, context, registry, provider_policy = _evidence_chain(tmp_path)
    validation["proposal_hash"] = "sha256:wrong"
    validation["artifact_hash"] = replay_hash({key: value for key, value in validation.items() if key != "artifact_hash"})

    capture = create_conversation_to_implementation_handoff(
        handoff_id="HANDOFF-HASH-MISMATCH-000001",
        proposal_artifact=proposal,
        proposal_contract_validation_artifact=validation,
        context_assembly_artifact=context,
        registry_resolution_artifact=registry,
        provider_necessity_policy_artifact=provider_policy,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "hash_mismatch",
    )

    assert capture["fail_closed"] is True
    assert "hashes mismatch" in capture["failure_reason"]


def test_handoff_fails_closed_on_authority_violation(tmp_path) -> None:
    proposal, validation, context, registry, provider_policy = _evidence_chain(tmp_path)
    proposal["dispatch_authority"] = True
    proposal["artifact_hash"] = replay_hash({key: value for key, value in proposal.items() if key != "artifact_hash"})

    capture = create_conversation_to_implementation_handoff(
        handoff_id="HANDOFF-AUTHORITY-000001",
        proposal_artifact=proposal,
        proposal_contract_validation_artifact=validation,
        context_assembly_artifact=context,
        registry_resolution_artifact=registry,
        provider_necessity_policy_artifact=provider_policy,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "authority",
    )

    assert capture["fail_closed"] is True
    assert "authority violation" in capture["failure_reason"]
    assert capture["dispatch_requested"] is False
    assert capture["execution_requested"] is False


def test_handoff_reconstruction_detects_corrupt_replay(tmp_path) -> None:
    proposal, validation, context, registry, provider_policy = _evidence_chain(tmp_path)
    create_conversation_to_implementation_handoff(
        handoff_id="HANDOFF-CORRUPT-000001",
        proposal_artifact=proposal,
        proposal_contract_validation_artifact=validation,
        context_assembly_artifact=context,
        registry_resolution_artifact=registry,
        provider_necessity_policy_artifact=provider_policy,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt",
    )
    path = tmp_path / "corrupt" / "000_implementation_handoff_created.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["proposal_hash"] = "sha256:corrupted"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_conversation_to_implementation_handoff_replay(tmp_path / "corrupt")


def test_handoff_runtime_has_no_provider_worker_or_execution_imports() -> None:
    import aigol.runtime.conversation_to_implementation_handoff_runtime as runtime

    source = inspect.getsource(runtime)

    assert "OpenAIProviderAdapter" not in source
    assert "run_provider_attachment(" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source
