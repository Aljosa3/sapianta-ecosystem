"""Tests for AIGOL_LLM_WORKER_EXECUTION_CERTIFICATION_V1."""

from __future__ import annotations

from pathlib import Path

from aigol.runtime.llm_worker_execution_certification_v1 import (
    MILESTONE_ID,
    reconstruct_llm_worker_execution_replay,
    run_llm_worker_execution_certification_v1,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json


def test_llm_worker_execution_certifies_governed_translation(tmp_path):
    result = run_llm_worker_execution_certification_v1(replay_base=tmp_path / "llm_worker")

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_verdict"] == "LLM_WORKER_EXECUTION_CERTIFIED"
    assert all(result["assertions"].values())

    root = Path(result["cert_root"])
    assert (root / "coverage_report" / "000_llm_worker_execution_coverage_report.json").exists()
    assert (root / "evidence_package" / "000_llm_worker_execution_evidence_package.json").exists()
    assert (root / "replay_package" / "000_llm_worker_execution_replay_package.json").exists()
    assert (root / "certification_report" / "000_llm_worker_execution_certification_report.json").exists()


def test_llm_worker_execution_preserves_authority_boundaries(tmp_path):
    result = run_llm_worker_execution_certification_v1(replay_base=tmp_path / "llm_worker")
    root = Path(result["cert_root"])
    authority = load_json(root / "worker_replay" / "LWE-001" / "008_llm_worker_authority_boundary.json")

    assert authority["human_authority_preserved"] is True
    assert authority["governance_authority_preserved"] is True
    assert authority["worker_authority"] is False
    assert authority["llm_worker_authority"] is False
    assert authority["provider_authority"] is False
    assert authority["authority_transfer_detected"] is False


def test_llm_worker_execution_replay_reconstructs(tmp_path):
    result = run_llm_worker_execution_certification_v1(replay_base=tmp_path / "llm_worker")
    reconstruction = reconstruct_llm_worker_execution_replay(result["cert_root"])

    assert reconstruction["replay_reconstructed"] is True
    assert reconstruction["approval_recorded"] is True
    assert reconstruction["authorization_issued"] is True
    assert reconstruction["contract_enforced"] is True
    assert reconstruction["validation_result"] == "PASS"


def test_llm_worker_execution_evidence_is_secret_free(tmp_path):
    result = run_llm_worker_execution_certification_v1(replay_base=tmp_path / "llm_worker")
    serialized = ""
    for path in sorted(Path(result["cert_root"]).rglob("*.json")):
        serialized += canonical_serialize(load_json(path))

    assert "sk-" not in serialized
    assert "Bearer " not in serialized
    assert "OPENAI_API_KEY=" not in serialized
    assert "ANTHROPIC_API_KEY=" not in serialized
