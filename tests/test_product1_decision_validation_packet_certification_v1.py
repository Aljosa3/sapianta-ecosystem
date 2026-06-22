"""Tests for AIGOL_PRODUCT1_DECISION_VALIDATION_PACKET_CERTIFICATION_V1."""

from __future__ import annotations

from pathlib import Path

from aigol.runtime.product1_decision_validation_packet_certification_v1 import (
    MILESTONE_ID,
    reconstruct_product1_decision_validation_packet_certification_v1,
    run_product1_decision_validation_packet_certification_v1,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash, write_json_immutable


def test_decision_validation_packet_certifies_from_replay_visible_evidence(tmp_path):
    product1_root, multi_root = _source_roots(tmp_path)

    result = run_product1_decision_validation_packet_certification_v1(
        runtime_root=tmp_path / "packet_cert",
        product1_cert_root=product1_root,
        multi_provider_cert_root=multi_root,
    )

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_verdict"] == "PRODUCT1_DECISION_VALIDATION_PACKET_CERTIFIED"
    assert all(result["assertions"].values())

    packet = load_json(Path(result["generated_packet_path"]))
    assert packet["artifact_type"] == "PRODUCT1_DECISION_VALIDATION_PACKET_ARTIFACT_V1"
    assert packet["decision_summary"]["why_result_was_produced"]
    assert len(packet["evidence_summary"]["evidence_items"]) >= 8
    assert packet["provider_participation_summary"]["providers_participated"] is True
    assert packet["worker_participation_summary"]["workers_participated"] is True
    assert packet["approval_summary"]["approval_recorded"] is True
    assert packet["authorization_summary"]["authorization_issued"] is True
    assert packet["independent_verification_workflow"]["requires_provider_trust"] is False


def test_decision_validation_packet_preserves_no_authority_transfer(tmp_path):
    product1_root, multi_root = _source_roots(tmp_path)
    result = run_product1_decision_validation_packet_certification_v1(
        runtime_root=tmp_path / "packet_cert",
        product1_cert_root=product1_root,
        multi_provider_cert_root=multi_root,
    )
    packet = load_json(Path(result["generated_packet_path"]))

    assert packet["boundary_guarantees"]["human_authority_preserved"] is True
    assert packet["boundary_guarantees"]["provider_authority"] is False
    assert packet["boundary_guarantees"]["worker_authority"] is False
    assert all(
        provider["provider_authority"] is False
        for provider in packet["provider_participation_summary"]["providers"]
    )
    assert all(worker["worker_authority"] is False for worker in packet["worker_participation_summary"]["workers"])


def test_decision_validation_packet_reconstructs(tmp_path):
    product1_root, multi_root = _source_roots(tmp_path)
    result = run_product1_decision_validation_packet_certification_v1(
        runtime_root=tmp_path / "packet_cert",
        product1_cert_root=product1_root,
        multi_provider_cert_root=multi_root,
    )

    reconstruction = reconstruct_product1_decision_validation_packet_certification_v1(result["cert_root"])

    assert reconstruction["replay_reconstructed"] is True
    assert reconstruction["final_verdict"] == "PRODUCT1_DECISION_VALIDATION_PACKET_CERTIFIED"
    assert reconstruction["replay_package"]["evidence_traceable"] is True


def test_decision_validation_packet_is_secret_free(tmp_path):
    product1_root, multi_root = _source_roots(tmp_path)
    result = run_product1_decision_validation_packet_certification_v1(
        runtime_root=tmp_path / "packet_cert",
        product1_cert_root=product1_root,
        multi_provider_cert_root=multi_root,
    )
    serialized = ""
    for path in sorted(Path(result["cert_root"]).rglob("*.json")):
        serialized += canonical_serialize(load_json(path))

    assert "sk-" not in serialized
    assert "Bearer " not in serialized
    assert "OPENAI_API_KEY=" not in serialized
    assert "ANTHROPIC_API_KEY=" not in serialized


def _source_roots(tmp_path: Path) -> tuple[Path, Path]:
    product1_root = tmp_path / "product1" / "CERT-000001"
    multi_root = tmp_path / "multi" / "CERT-000001"
    scenario_replay = product1_root / "component_runs" / "worker" / "CERT-000001" / "scenarios" / "ALS-001" / "replay"
    _write_replay_artifact(
        scenario_replay / "002_intent_resolution_recorded.json",
        "intent_resolution_recorded",
        2,
        {
            "artifact_type": "ACLI_LIVE_SESSION_INTENT_RESOLUTION_ARTIFACT_V1",
            "intent_resolved": True,
            "clarification_generated": False,
            "workflow_selected": True,
            "selected_workflow": "LIVE_ACLI_FILE_CREATION_WORKFLOW",
        },
    )
    _write_replay_artifact(
        scenario_replay / "003_execution_summary_recorded.json",
        "execution_summary_recorded",
        3,
        {
            "artifact_type": "ACLI_LIVE_SESSION_EXECUTION_SUMMARY_ARTIFACT_V1",
            "execution_summary_generated": True,
        },
    )
    _write_replay_artifact(
        scenario_replay / "004_human_approval_recorded.json",
        "human_approval_recorded",
        4,
        {
            "artifact_type": "ACLI_LIVE_SESSION_HUMAN_APPROVAL_ARTIFACT_V1",
            "human_approval_required": True,
            "human_approval_recorded": True,
            "approved_for_execution": True,
        },
    )
    _write_replay_artifact(
        scenario_replay / "005_authorization_recorded.json",
        "authorization_recorded",
        5,
        {
            "artifact_type": "ACLI_LIVE_SESSION_AUTHORIZATION_ARTIFACT_V1",
            "authorization_issued": True,
            "authorized_worker_type": "FILE_CREATION_WORKER",
        },
    )
    _write_replay_artifact(
        scenario_replay / "006_worker_handoff_recorded.json",
        "worker_handoff_recorded",
        6,
        {
            "artifact_type": "ACLI_LIVE_SESSION_WORKER_HANDOFF_ARTIFACT_V1",
            "worker_handoff_package_generated": True,
        },
    )
    _write_replay_artifact(
        scenario_replay / "007_worker_execution_recorded.json",
        "worker_execution_recorded",
        7,
        {
            "artifact_type": "ACLI_LIVE_SESSION_WORKER_EXECUTION_ARTIFACT_V1",
            "worker_invoked": True,
        },
    )
    _write_replay_artifact(
        scenario_replay / "008_side_effect_verification_recorded.json",
        "side_effect_verification_recorded",
        8,
        {
            "artifact_type": "ACLI_LIVE_SESSION_SIDE_EFFECT_VERIFICATION_ARTIFACT_V1",
            "side_effect_verification_performed": True,
            "verification_passed": True,
        },
    )
    _write_json(
        product1_root / "evidence_package" / "000_product1_end_to_end_evidence_package.json",
        {
            "artifact_type": "PRODUCT1_END_TO_END_EVIDENCE_PACKAGE_V1",
            "scenario_results": [
                {
                    "scenario_id": "P1-E2E-001",
                    "scenario_verdict": "CERTIFIED",
                    "coverage": "direct_execution",
                    "human_prompt_hash": replay_hash("Create a proof note."),
                    "observed": {
                        "source_reference": str(scenario_replay),
                        "worker_invoked": True,
                        "side_effect_present": True,
                    },
                }
            ],
        },
    )
    _write_json(
        product1_root / "replay_package" / "000_product1_end_to_end_replay_package.json",
        {"artifact_type": "PRODUCT1_END_TO_END_REPLAY_PACKAGE_V1", "replay_reconstructed": True},
    )
    _write_json(
        product1_root / "audit_review" / "000_product1_end_to_end_audit_review.json",
        {
            "artifact_type": "PRODUCT1_END_TO_END_AUDIT_REVIEW_ARTIFACT_V1",
            "audit_findings": ["Synthetic Product 1 audit review reconstructed the evidence chain."],
        },
    )
    _write_json(
        product1_root / "certification_report" / "000_product1_end_to_end_certification_report.json",
        {
            "artifact_type": "PRODUCT1_END_TO_END_CERTIFICATION_REPORT_V1",
            "final_verdict": "AIGOL_PRODUCT1_END_TO_END_CERTIFIED",
        },
    )
    for provider_id in ("openai", "claude"):
        _write_json(
            multi_root
            / "provider_governance_replay"
            / provider_id
            / "participation"
            / "000_cognition_participation.json",
            {
                "artifact_type": "COGNITION_PARTICIPATION_ARTIFACT_V1",
                "provider_id": provider_id,
                "participation_location": "OCS_LLM_COGNITION",
                "response_used": True,
                "provider_authority": False,
                "worker_invoked_after": False,
                "human_confirmation_required": True,
            },
        )
        _write_json(
            multi_root / "provider_governance_replay" / provider_id / "usage" / "000_provider_usage_metric.json",
            {
                "artifact_type": "PROVIDER_USAGE_METRIC_ARTIFACT_V1",
                "provider_id": provider_id,
                "success_count": 1,
                "failure_count": 0,
                "cost_tracking": {"estimated_usd": "hook-present"},
            },
        )
    return product1_root, multi_root


def _write_replay_artifact(path: Path, step: str, index: int, artifact: dict) -> None:
    artifact = dict(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    payload = {
        "replay_index": index,
        "replay_step": step,
        "artifact": artifact,
    }
    payload["replay_hash"] = replay_hash(payload)
    write_json_immutable(path, payload)


def _write_json(path: Path, payload: dict) -> None:
    payload = dict(payload)
    payload["artifact_hash"] = replay_hash(payload)
    write_json_immutable(path, payload)
