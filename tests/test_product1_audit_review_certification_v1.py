"""Tests for AIGOL_PRODUCT1_AUDIT_REVIEW_CERTIFICATION_V1."""

from __future__ import annotations

from pathlib import Path

from aigol.runtime.product1_audit_review_certification_v1 import (
    MILESTONE_ID,
    reconstruct_product1_audit_review_certification_v1,
    run_product1_audit_review_certification_v1,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json
from test_product1_decision_validation_packet_certification_v1 import _source_roots


def test_product1_audit_review_certifies_non_developer_review(tmp_path):
    product1_root, multi_root = _source_roots(tmp_path)

    result = run_product1_audit_review_certification_v1(
        runtime_root=tmp_path / "audit_review_cert",
        product1_cert_root=product1_root,
        multi_provider_cert_root=multi_root,
    )

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_verdict"] == "PRODUCT1_AUDIT_REVIEW_CERTIFIED"
    assert all(result["assertions"].values())

    audit = load_json(Path(result["audit_review_package_path"]))
    assert audit["decision_overview"]["audit_status"] == "PASS"
    assert audit["trust_verification"]["trust_result"] == "VALIDATED_WITHOUT_PROVIDER_TRUST"
    assert audit["review_conclusion"]["reviewer_can_validate_decision"] is True
    assert audit["review_conclusion"]["non_developer_usable"] is True


def test_product1_audit_review_contains_navigation_and_checkpoints(tmp_path):
    product1_root, multi_root = _source_roots(tmp_path)
    result = run_product1_audit_review_certification_v1(
        runtime_root=tmp_path / "audit_review_cert",
        product1_cert_root=product1_root,
        multi_provider_cert_root=multi_root,
    )
    audit = load_json(Path(result["audit_review_package_path"]))

    assert "Decision Overview" in audit["navigation"]["sections"]
    assert "Validation Packet" in audit["navigation"]["sections"]
    assert "Approval And Authorization" in audit["navigation"]["sections"]
    assert "Escalation" in audit["navigation"]["sections"]
    assert len(audit["checkpoint_results"]) >= 10
    assert all(item["status"] == "PASS" for item in audit["checkpoint_results"])


def test_product1_audit_review_reconstructs(tmp_path):
    product1_root, multi_root = _source_roots(tmp_path)
    result = run_product1_audit_review_certification_v1(
        runtime_root=tmp_path / "audit_review_cert",
        product1_cert_root=product1_root,
        multi_provider_cert_root=multi_root,
    )

    reconstruction = reconstruct_product1_audit_review_certification_v1(result["cert_root"])

    assert reconstruction["replay_reconstructed"] is True
    assert reconstruction["final_verdict"] == "PRODUCT1_AUDIT_REVIEW_CERTIFIED"
    assert reconstruction["replay_package"]["reviewer_workflow_traceable"] is True


def test_product1_audit_review_is_secret_free(tmp_path):
    product1_root, multi_root = _source_roots(tmp_path)
    result = run_product1_audit_review_certification_v1(
        runtime_root=tmp_path / "audit_review_cert",
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
