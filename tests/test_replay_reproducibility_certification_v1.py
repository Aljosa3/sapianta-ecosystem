"""Tests for AIGOL_REPLAY_REPRODUCIBILITY_CERTIFICATION_V1."""

from __future__ import annotations

from pathlib import Path

import pytest

from aigol.runtime.replay_reproducibility_certification_v1 import (
    MILESTONE_ID,
    run_replay_reproducibility_certification_v1,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json


SOURCE_ROOTS = {
    "product1_cert_root": Path("runtime/product1_end_to_end_certification_v1/CERT-000001"),
    "worker_selection_cert_root": Path("runtime/worker_selection_certification_v1/CERT-000001"),
    "llm_worker_cert_root": Path("runtime/llm_worker_execution_certification_v1/CERT-000001"),
    "multi_provider_cert_root": Path("runtime/multi_provider_operational_readiness_certification_v1/CERT-000001"),
    "audit_review_cert_root": Path("runtime/product1_audit_review_certification_v1/CERT-000001"),
}


def _require_sources() -> None:
    missing = [str(path) for path in SOURCE_ROOTS.values() if not path.exists()]
    if missing:
        pytest.skip("certified replay source roots are not present: " + ", ".join(missing))


def test_replay_reproducibility_certifies_governed_path(tmp_path):
    _require_sources()
    result = run_replay_reproducibility_certification_v1(
        replay_base=tmp_path / "replay_repro",
        **SOURCE_ROOTS,
    )

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_verdict"] == "REPLAY_REPRODUCIBILITY_CERTIFIED"
    assert all(result["assertions"].values())


def test_replay_reproducibility_report_answers_reviewer_question(tmp_path):
    _require_sources()
    result = run_replay_reproducibility_certification_v1(
        replay_base=tmp_path / "replay_repro",
        **SOURCE_ROOTS,
    )
    report = load_json(Path(result["reproducibility_report_path"]))

    assert report["answer"] is True
    assert report["approval_chain"]["human_approval_recorded"] is True
    assert report["authorization_chain"]["authorization_issued"] is True
    assert report["validation_chain"]["product1_verification_passed"] is True
    assert report["hidden_authority_source_exists"] is False


def test_replay_reproducibility_replay_package_reconstructs(tmp_path):
    _require_sources()
    result = run_replay_reproducibility_certification_v1(
        replay_base=tmp_path / "replay_repro",
        **SOURCE_ROOTS,
    )
    replay = load_json(Path(result["replay_package_path"]))

    assert replay["replay_reconstructed"] is True
    assert set(replay["source_roots"]) == {
        "product1",
        "worker_selection",
        "llm_worker",
        "multi_provider",
        "audit_review",
    }


def test_replay_reproducibility_evidence_is_secret_free(tmp_path):
    _require_sources()
    result = run_replay_reproducibility_certification_v1(
        replay_base=tmp_path / "replay_repro",
        **SOURCE_ROOTS,
    )
    serialized = ""
    for path in sorted(Path(result["cert_root"]).rglob("*.json")):
        serialized += canonical_serialize(load_json(path))

    assert "sk-" not in serialized
    assert "Bearer " not in serialized
    assert "OPENAI_API_KEY=" not in serialized
    assert "ANTHROPIC_API_KEY=" not in serialized
