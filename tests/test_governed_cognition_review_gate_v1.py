"""Tests for GOVERNED_COGNITION_REVIEW_GATE_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect

import pytest

from aigol.runtime.bounded_llm_attachment_architecture import (
    CONTRACT_PROPOSAL,
    create_bounded_cognition_proposal,
)
from aigol.runtime.governed_cognition_review_gate import (
    CRITICAL,
    HIGH,
    LOW,
    MEDIUM,
    REJECTED,
    REVIEWED,
    GovernedCognitionReviewResult,
    reconstruct_cognition_review_lineage,
    review_translated_cognition_candidate,
)
from aigol.runtime.governed_proposal_translation_layer import (
    translate_bounded_proposal,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-26T00:05:00+00:00"
TRANSLATED_AT = "2026-05-26T00:05:10+00:00"
REVIEWED_AT = "2026-05-26T00:05:20+00:00"


class ProviderExecutionSentinel:
    executed = False

    def fetch(self) -> None:
        self.executed = True
        raise AssertionError("review gate must not invoke providers")


def _proposal(**overrides):
    payload = {
        "proposal_id": "PROPOSAL-REVIEW-1",
        "proposal_type": CONTRACT_PROPOSAL,
        "proposal_summary": "proposal asks for bounded metadata inspection review",
        "requested_capabilities": ["metadata_inspection_provider"],
        "proposed_contract_reference": "contract:CONTRACT-REVIEW-1",
        "created_at": CREATED_AT,
    }
    payload.update(overrides)
    return create_bounded_cognition_proposal(**payload)


def _translation(**overrides):
    payload = {
        "translation_id": "TRANSLATION-REVIEW-1",
        "proposal": _proposal(),
        "created_at": TRANSLATED_AT,
    }
    payload.update(overrides)
    return translate_bounded_proposal(**payload)


def _review(**overrides) -> GovernedCognitionReviewResult:
    payload = {
        "review_id": "REVIEW-1",
        "translation": _translation(),
        "created_at": REVIEWED_AT,
    }
    payload.update(overrides)
    return review_translated_cognition_candidate(**payload)


def test_valid_cognition_review() -> None:
    review = _review()

    assert review.review_status == REVIEWED
    assert review.proposal_id == "PROPOSAL-REVIEW-1"
    assert review.translation_id == "TRANSLATION-REVIEW-1"
    assert review.risk_level == LOW
    assert review.evidence_hash.startswith("sha256:")


def test_malformed_lineage_rejection() -> None:
    artifact = _translation().to_dict()
    artifact.pop("translation_reason")

    review = _review(translation=artifact)

    assert review.review_status == REJECTED
    assert review.risk_level == CRITICAL
    assert review.review_reason == "cognition review validation failed closed"


def test_invalid_translation_lineage_rejection() -> None:
    artifact = _translation().to_dict()
    artifact["translation_status"] = "REJECTED"

    review = _review(translation=artifact)

    assert review.review_status == REJECTED
    assert review.risk_level == CRITICAL
    assert review.review_reason == "cognition review validation failed closed"


def test_unauthorized_capability_rejection() -> None:
    artifact = _translation().to_dict()
    candidate = artifact["translated_contract_candidate"]
    candidate["allowed_providers"] = ["shell_provider"]
    candidate["requested_operations"][0]["provider"] = "shell_provider"
    artifact["evidence_hash"] = replay_hash(
        {
            "translation_id": artifact["translation_id"],
            "proposal_id": artifact["proposal_id"],
            "translated_contract_candidate": candidate,
            "translation_status": artifact["translation_status"],
            "translation_reason": artifact["translation_reason"],
            "created_at": artifact["created_at"],
        }
    )

    review = _review(translation=artifact)

    assert review.review_status == REJECTED
    assert review.risk_level == CRITICAL


def test_deterministic_review_lineage() -> None:
    reviews = [
        _review(review_id="REVIEW-1", created_at="2026-05-26T00:05:20+00:00"),
        _review(
            review_id="REVIEW-2",
            translation=_translation(
                translation_id="TRANSLATION-REVIEW-2",
                proposal=_proposal(proposal_id="PROPOSAL-REVIEW-2", created_at="2026-05-26T00:05:01+00:00"),
                created_at="2026-05-26T00:05:11+00:00",
            ),
            created_at="2026-05-26T00:05:21+00:00",
        ),
    ]

    first = reconstruct_cognition_review_lineage([review.to_dict() for review in reviews])
    second = reconstruct_cognition_review_lineage([review.to_dict() for review in reviews])

    assert first == second
    assert first["review_count"] == 2
    assert first["append_only_valid"] is True
    assert first["lineage_hash"].startswith("sha256:")


def test_replay_visible_review_evidence() -> None:
    first = _review().to_dict()
    second = GovernedCognitionReviewResult.from_dict(first).to_dict()

    assert first == second
    without_hash = deepcopy(first)
    evidence_hash = without_hash.pop("evidence_hash")
    assert evidence_hash == replay_hash(without_hash)


def test_cognition_risk_classification() -> None:
    medium_review = _review(
        translation=_translation(
            proposal=_proposal(
                requested_capabilities=["metadata_inspection_provider", "readonly_http_get_provider"],
            )
        )
    )
    high_review = _review(
        translation=_translation(
            proposal=_proposal(
                requested_capabilities=["readonly_filesystem_provider"],
            )
        )
    )

    assert medium_review.risk_level == MEDIUM
    assert high_review.risk_level == HIGH


def test_governance_authority_separation() -> None:
    review = _review()
    lineage = reconstruct_cognition_review_lineage([review])

    assert lineage["governance_authority_separated"] is True
    assert "authorization_id" not in review.to_dict()
    assert "routing_id" not in review.to_dict()
    assert "session_id" not in review.to_dict()


def test_fail_closed_cognition_review_validation() -> None:
    artifact = _translation().to_dict()
    artifact["translated_contract_candidate"]["governance_authority_required"] = False
    artifact["evidence_hash"] = replay_hash(
        {
            "translation_id": artifact["translation_id"],
            "proposal_id": artifact["proposal_id"],
            "translated_contract_candidate": artifact["translated_contract_candidate"],
            "translation_status": artifact["translation_status"],
            "translation_reason": artifact["translation_reason"],
            "created_at": artifact["created_at"],
        }
    )

    review = _review(translation=artifact)

    assert review.review_status == REJECTED
    assert review.risk_level == CRITICAL


def test_mutated_review_evidence_rejected() -> None:
    artifact = _review().to_dict()
    artifact["risk_level"] = HIGH

    with pytest.raises(FailClosedRuntimeError, match="evidence hash mismatch"):
        GovernedCognitionReviewResult.from_dict(artifact)


def test_duplicate_review_lineage_rejected() -> None:
    reviews = [
        _review(review_id="REVIEW-1", created_at="2026-05-26T00:05:20+00:00"),
        _review(review_id="REVIEW-1", created_at="2026-05-26T00:05:21+00:00"),
    ]

    with pytest.raises(FailClosedRuntimeError, match="duplicate"):
        reconstruct_cognition_review_lineage(reviews)


def test_out_of_order_review_lineage_rejected() -> None:
    reviews = [
        _review(review_id="REVIEW-1", created_at="2026-05-26T00:05:22+00:00"),
        _review(review_id="REVIEW-2", created_at="2026-05-26T00:05:21+00:00"),
    ]

    with pytest.raises(FailClosedRuntimeError, match="ordering"):
        reconstruct_cognition_review_lineage(reviews)


def test_no_execution_authority_surface() -> None:
    import aigol.runtime.governed_cognition_review_gate as review_gate

    sentinel = ProviderExecutionSentinel()
    _review()

    source = inspect.getsource(review_gate)

    assert sentinel.executed is False
    assert "subprocess" not in source
    assert "os.system" not in source
    assert "requests" not in source
    assert "urllib" not in source
    assert "async " not in source
    assert "await " not in source
    assert "threading" not in source
    assert "multiprocessing" not in source
    assert "orchestrat" not in source.lower()
    assert "autonomous" not in source.lower()
    assert "authorize_" not in source
    assert "route_authorized" not in source
    assert "attach_to_session" not in source
    assert "create_governed_execution_contract" not in source
    assert "open(" not in source
    assert "Path(" not in source
