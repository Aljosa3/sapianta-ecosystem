"""Tests for AIGOL_DEVELOPMENT_CONTEXT_ASSEMBLY_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json
from pathlib import Path
import shutil

import pytest

from aigol.runtime.development_context_assembly_runtime import (
    CONTEXT_ASSEMBLED,
    DEVELOPMENT_CONTEXT_ASSEMBLY_ARTIFACT_V1,
    PROVIDER_REQUIRED_FOR_PROPOSAL,
    assemble_development_context,
    reconstruct_development_context_assembly_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.native_development_task_intake_runtime import run_native_development_task_intake
from aigol.runtime.transport.serialization import canonical_serialize


ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE_ROOT = ROOT / "governance"
CREATED_AT = "2026-06-02T15:00:00+00:00"
MILESTONE_ID = "TRADING_MARKET_EVIDENCE_NORMALIZATION_WORKER_FOUNDATION_V1"


def _intake(tmp_path) -> dict:
    capture = run_native_development_task_intake(
        intake_id="INTAKE-CONTEXT-000001",
        human_prompt_reference="PROMPT-CONTEXT-000001",
        human_prompt=(
            f"Implement {MILESTONE_ID}. Foundation only. No broker integration. "
            "No exchange integration. No order placement. No live trading."
        ),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "intake",
        session_id="SESSION-CONTEXT-000001",
        turn_id="TURN-000001",
    )
    return capture["native_development_task_intake_artifact"]


def _copy_governance_subset(tmp_path) -> Path:
    target = tmp_path / "governance_subset"
    target.mkdir()
    for source in GOVERNANCE_ROOT.iterdir():
        if source.is_file():
            shutil.copy2(source, target / source.name)
    return target


def test_development_context_assembly_builds_reconstructable_trading_context(tmp_path) -> None:
    intake = _intake(tmp_path)

    capture = assemble_development_context(
        context_assembly_id="CONTEXT-ASSEMBLY-TRADING-000001",
        development_task_intake_artifact=intake,
        governance_root=GOVERNANCE_ROOT,
        replay_dir=tmp_path / "context",
        created_at=CREATED_AT,
    )
    reconstructed = reconstruct_development_context_assembly_replay(tmp_path / "context")
    artifact = capture["development_context_assembly_artifact"]

    assert artifact["artifact_type"] == DEVELOPMENT_CONTEXT_ASSEMBLY_ARTIFACT_V1
    assert capture["context_status"] == CONTEXT_ASSEMBLED
    assert capture["requested_milestone_id"] == MILESTONE_ID
    assert capture["requested_domain"] == "TRADING"
    assert capture["requested_worker_family"] == "MARKET_EVIDENCE_NORMALIZATION"
    assert capture["missing_context"] == []
    assert capture["ambiguous_context"] == []
    assert capture["provider_necessity_classification"] == PROVIDER_REQUIRED_FOR_PROPOSAL
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False
    assert len(capture["artifact_references"]) >= 20
    assert "TRADING_DOMAIN_FOUNDATION_V1" in capture["reference_hashes"]
    assert reconstructed["context_status"] == CONTEXT_ASSEMBLED
    assert reconstructed["context_hash"] == capture["context_hash"]
    assert reconstructed["replay_artifact_count"] == 5


def test_development_context_assembly_fails_closed_when_required_context_missing(tmp_path) -> None:
    intake = _intake(tmp_path)
    governance_root = _copy_governance_subset(tmp_path)
    (governance_root / "TRADING_DOMAIN_FOUNDATION_V1.md").unlink()

    capture = assemble_development_context(
        context_assembly_id="CONTEXT-ASSEMBLY-MISSING-000001",
        development_task_intake_artifact=intake,
        governance_root=governance_root,
        replay_dir=tmp_path / "missing_context",
        created_at=CREATED_AT,
    )
    reconstructed = reconstruct_development_context_assembly_replay(tmp_path / "missing_context")

    assert capture["fail_closed"] is True
    assert capture["context_status"] == "FAILED_CLOSED_MISSING_CONTEXT"
    assert capture["missing_context"]
    assert capture["missing_context"][0]["fail_closed_impact"] is True
    assert "required context is missing" in capture["failure_reason"]
    assert reconstructed["context_status"] == "FAILED_CLOSED_MISSING_CONTEXT"


def test_development_context_assembly_fails_closed_on_expected_hash_mismatch(tmp_path) -> None:
    intake = _intake(tmp_path)

    capture = assemble_development_context(
        context_assembly_id="CONTEXT-ASSEMBLY-HASH-MISMATCH-000001",
        development_task_intake_artifact=intake,
        governance_root=GOVERNANCE_ROOT,
        replay_dir=tmp_path / "hash_mismatch",
        created_at=CREATED_AT,
        expected_reference_hashes={"TRADING_DOMAIN_FOUNDATION_V1": "sha256:not-the-real-hash"},
    )

    assert capture["fail_closed"] is True
    assert capture["context_status"] == "FAILED_CLOSED_INVALID_INTAKE"
    assert "reference hash mismatch" in capture["failure_reason"]
    assert capture["provider_invoked"] is False


def test_development_context_assembly_fails_closed_on_invalid_intake(tmp_path) -> None:
    intake = _intake(tmp_path)
    intake["intake_status"] = "FAILED_CLOSED"

    capture = assemble_development_context(
        context_assembly_id="CONTEXT-ASSEMBLY-INVALID-000001",
        development_task_intake_artifact=intake,
        governance_root=GOVERNANCE_ROOT,
        replay_dir=tmp_path / "invalid_intake",
        created_at=CREATED_AT,
    )

    assert capture["fail_closed"] is True
    assert capture["context_status"] == "FAILED_CLOSED_INVALID_INTAKE"
    assert "hash mismatch" in capture["failure_reason"]


def test_development_context_assembly_reconstruction_detects_corrupt_replay(tmp_path) -> None:
    intake = _intake(tmp_path)
    assemble_development_context(
        context_assembly_id="CONTEXT-ASSEMBLY-CORRUPT-000001",
        development_task_intake_artifact=intake,
        governance_root=GOVERNANCE_ROOT,
        replay_dir=tmp_path / "corrupt",
        created_at=CREATED_AT,
    )
    path = tmp_path / "corrupt" / "003_development_context_assembly_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["context_hash"] = "sha256:corrupted"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_development_context_assembly_replay(tmp_path / "corrupt")


def test_development_context_assembly_preserves_authority_boundaries() -> None:
    import aigol.runtime.development_context_assembly_runtime as runtime

    source = inspect.getsource(runtime)

    assert "OpenAIProviderAdapter" not in source
    assert "run_provider_attachment(" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source
