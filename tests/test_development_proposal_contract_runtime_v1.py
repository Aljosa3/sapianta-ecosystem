"""Tests for AIGOL_DEVELOPMENT_PROPOSAL_CONTRACT_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from aigol.runtime.development_context_assembly_runtime import assemble_development_context
from aigol.runtime.development_proposal_contract_runtime import (
    DEVELOPMENT_PROPOSAL_ARTIFACT_V1,
    DEVELOPMENT_PROPOSAL_CONTRACT_VALIDATED,
    validate_development_proposal_contract,
    reconstruct_development_proposal_contract_replay,
)
from aigol.runtime.domain_and_worker_resolution_registry import resolve_domain_worker_milestone
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.native_development_task_intake_runtime import run_native_development_task_intake
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE_ROOT = ROOT / "governance"
CREATED_AT = "2026-06-02T19:00:00+00:00"
MILESTONE_ID = "TRADING_MARKET_EVIDENCE_NORMALIZATION_WORKER_FOUNDATION_V1"


def _fixtures(tmp_path) -> tuple[dict, dict, dict]:
    intake_capture = run_native_development_task_intake(
        intake_id="INTAKE-PROPOSAL-CONTRACT-000001",
        human_prompt_reference="PROMPT-PROPOSAL-CONTRACT-000001",
        human_prompt=(
            f"Implement {MILESTONE_ID}. Foundation only. No broker integration. "
            "No exchange integration. No order placement. No live trading."
        ),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "intake",
    )
    context_capture = assemble_development_context(
        context_assembly_id="CONTEXT-PROPOSAL-CONTRACT-000001",
        development_task_intake_artifact=intake_capture["native_development_task_intake_artifact"],
        governance_root=GOVERNANCE_ROOT,
        replay_dir=tmp_path / "context",
        created_at=CREATED_AT,
    )
    registry_capture = resolve_domain_worker_milestone(
        resolution_id="REGISTRY-PROPOSAL-CONTRACT-000001",
        domain_id="TRADING",
        worker_family_id="MARKET_EVIDENCE_NORMALIZATION",
        milestone_type="WORKER_FOUNDATION",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "registry",
    )
    return (
        context_capture["development_context_assembly_artifact"],
        registry_capture["domain_worker_resolution_artifact"],
        intake_capture["native_development_task_intake_artifact"],
    )


def _proposal(context: dict, registry: dict, *, overrides: dict | None = None) -> dict:
    proposal = {
        "artifact_type": DEVELOPMENT_PROPOSAL_ARTIFACT_V1,
        "proposal_id": "PROPOSAL-CONTRACT-000001",
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
            "Worker foundation does not implement live runtime behavior.",
        ],
        "known_gaps": [
            "Implementation handoff remains governed and separate.",
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


def test_development_proposal_contract_validates_complete_proposal(tmp_path) -> None:
    context, registry, _intake = _fixtures(tmp_path)
    proposal = _proposal(context, registry)

    capture = validate_development_proposal_contract(
        contract_validation_id="CONTRACT-VALIDATION-000001",
        proposal_artifact=proposal,
        context_assembly_artifact=context,
        registry_resolution_artifact=registry,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "contract",
    )
    reconstructed = reconstruct_development_proposal_contract_replay(tmp_path / "contract")

    assert capture["validation_status"] == DEVELOPMENT_PROPOSAL_CONTRACT_VALIDATED
    assert capture["proposal_id"] == proposal["proposal_id"]
    assert capture["proposal_hash"] == proposal["artifact_hash"]
    assert capture["context_hash"] == context["context_hash"]
    assert capture["domain_reference"] == "TRADING"
    assert capture["worker_reference"] == "MARKET_EVIDENCE_NORMALIZATION"
    assert capture["milestone_reference"] == "WORKER_FOUNDATION"
    assert capture["proposal_only"] is True
    assert capture["provider_invoked"] is False
    assert capture["worker_created"] is False
    assert capture["execution_requested"] is False
    assert reconstructed["validation_status"] == DEVELOPMENT_PROPOSAL_CONTRACT_VALIDATED
    assert reconstructed["replay_artifact_count"] == 2


def test_development_proposal_contract_fails_closed_on_incomplete_proposal(tmp_path) -> None:
    context, registry, _intake = _fixtures(tmp_path)
    proposal = _proposal(context, registry)
    proposal.pop("proposed_outputs")

    capture = validate_development_proposal_contract(
        contract_validation_id="CONTRACT-INCOMPLETE-000001",
        proposal_artifact=proposal,
        context_assembly_artifact=context,
        registry_resolution_artifact=registry,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "incomplete",
    )

    assert capture["fail_closed"] is True
    assert "proposal is incomplete" in capture["failure_reason"]


def test_development_proposal_contract_fails_closed_on_ambiguous_outputs(tmp_path) -> None:
    context, registry, _intake = _fixtures(tmp_path)
    proposal = _proposal(
        context,
        registry,
        overrides={
            "proposed_outputs": [
                "governance/TRADING_MARKET_EVIDENCE_NORMALIZATION_WORKER_FOUNDATION_V1.md",
                "governance/TRADING_MARKET_EVIDENCE_NORMALIZATION_WORKER_FOUNDATION_V1.md",
            ]
        },
    )

    capture = validate_development_proposal_contract(
        contract_validation_id="CONTRACT-AMBIGUOUS-000001",
        proposal_artifact=proposal,
        context_assembly_artifact=context,
        registry_resolution_artifact=registry,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "ambiguous",
    )

    assert capture["fail_closed"] is True
    assert "proposal is ambiguous" in capture["failure_reason"]


def test_development_proposal_contract_fails_closed_on_unknown_reference(tmp_path) -> None:
    context, registry, _intake = _fixtures(tmp_path)
    proposal = _proposal(context, registry, overrides={"worker_reference": "RISK_ANALYSIS"})

    capture = validate_development_proposal_contract(
        contract_validation_id="CONTRACT-UNKNOWN-000001",
        proposal_artifact=proposal,
        context_assembly_artifact=context,
        registry_resolution_artifact=registry,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "unknown",
    )

    assert capture["fail_closed"] is True
    assert "unknown entities" in capture["failure_reason"]


def test_development_proposal_contract_fails_closed_on_authority_violation(tmp_path) -> None:
    context, registry, _intake = _fixtures(tmp_path)
    proposal = _proposal(context, registry, overrides={"execution_authority": True})

    capture = validate_development_proposal_contract(
        contract_validation_id="CONTRACT-AUTHORITY-000001",
        proposal_artifact=proposal,
        context_assembly_artifact=context,
        registry_resolution_artifact=registry,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "authority",
    )

    assert capture["fail_closed"] is True
    assert "authority boundary" in capture["failure_reason"]
    assert capture["execution_requested"] is False
    assert capture["worker_created"] is False


def test_development_proposal_contract_reconstruction_detects_corrupt_replay(tmp_path) -> None:
    context, registry, _intake = _fixtures(tmp_path)
    proposal = _proposal(context, registry)
    validate_development_proposal_contract(
        contract_validation_id="CONTRACT-CORRUPT-000001",
        proposal_artifact=proposal,
        context_assembly_artifact=context,
        registry_resolution_artifact=registry,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt",
    )
    path = tmp_path / "corrupt" / "000_development_proposal_contract_validated.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["proposal_hash"] = "sha256:corrupted"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_development_proposal_contract_replay(tmp_path / "corrupt")


def test_development_proposal_contract_has_no_provider_worker_or_execution_imports() -> None:
    import aigol.runtime.development_proposal_contract_runtime as runtime

    source = inspect.getsource(runtime)

    assert "OpenAIProviderAdapter" not in source
    assert "run_provider_attachment(" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source
