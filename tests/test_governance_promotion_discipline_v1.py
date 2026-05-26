"""Tests for GOVERNANCE_PROMOTION_DISCIPLINE_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect

import pytest

from aigol.runtime.governance_promotion_discipline import (
    BLOCKED,
    ELIGIBLE,
    GovernancePromotionResult,
    evaluate_governance_promotion,
    reconstruct_promotion_lineage,
)
from aigol.runtime.governance_resilience_certification_gate import (
    certify_governance_resilience,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.synthetic_cognition_pressure_simulator import (
    generate_ambiguous_contract,
    generate_authority_drift_attempt,
    generate_long_chain_entropy_sequence,
    generate_provider_escalation_attempt,
    generate_replay_corruption_attempt,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-26T00:02:00+00:00"


class ProviderExecutionSentinel:
    executed = False

    def fetch(self) -> None:
        self.executed = True
        raise AssertionError("promotion discipline must not invoke providers")


def _evidence() -> list[dict]:
    return [
        generate_ambiguous_contract(simulation_id="SIM-1", created_at="2026-05-26T00:00:00+00:00").to_dict(),
        generate_authority_drift_attempt(simulation_id="SIM-2", created_at="2026-05-26T00:00:01+00:00").to_dict(),
        generate_long_chain_entropy_sequence(simulation_id="SIM-3", created_at="2026-05-26T00:00:02+00:00", length=4).to_dict(),
        generate_provider_escalation_attempt(simulation_id="SIM-4", created_at="2026-05-26T00:00:03+00:00").to_dict(),
        generate_replay_corruption_attempt(simulation_id="SIM-5", created_at="2026-05-26T00:00:04+00:00").to_dict(),
    ]


def _certification(**overrides):
    payload = {
        "certification_id": "CERT-PROMOTION-1",
        "related_change_id": "CHANGE-PROMOTION-1",
        "resilience_suite_version": "SYNTHETIC_COGNITION_PRESSURE_SIMULATOR_V1",
        "resilience_evidence": _evidence(),
        "created_at": "2026-05-26T00:01:00+00:00",
    }
    payload.update(overrides)
    return certify_governance_resilience(**payload)


def _promotion(**overrides) -> GovernancePromotionResult:
    payload = {
        "promotion_id": "PROMOTION-1",
        "related_change_id": "CHANGE-PROMOTION-1",
        "certification": _certification(),
        "created_at": CREATED_AT,
    }
    payload.update(overrides)
    return evaluate_governance_promotion(**payload)


def test_valid_promotion_eligibility() -> None:
    promotion = _promotion()

    assert promotion.promotion_status == ELIGIBLE
    assert promotion.related_change_id == "CHANGE-PROMOTION-1"
    assert promotion.certification_id == "CERT-PROMOTION-1"
    assert promotion.evidence_hash.startswith("sha256:")


def test_missing_certification_rejection() -> None:
    promotion = _promotion(certification=None)

    assert promotion.promotion_status == BLOCKED
    assert promotion.certification_id == ""
    assert promotion.promotion_reason == "missing certification"


def test_invalid_certification_rejection() -> None:
    rejected_certification = _certification(resilience_evidence=_evidence()[:-1])
    promotion = _promotion(certification=rejected_certification)

    assert promotion.promotion_status == BLOCKED
    assert promotion.certification_id == "CERT-PROMOTION-1"
    assert promotion.promotion_reason == "certification status is not CERTIFIED"


def test_malformed_promotion_rejection() -> None:
    promotion = evaluate_governance_promotion(
        promotion_id="",
        related_change_id="CHANGE-PROMOTION-1",
        certification=_certification(),
        created_at=CREATED_AT,
    )

    assert promotion.promotion_status == BLOCKED
    assert promotion.promotion_id == "PROMOTION-INVALID"
    assert promotion.promotion_reason == "promotion validation failed closed"


def test_mismatched_change_rejection() -> None:
    promotion = _promotion(related_change_id="OTHER-CHANGE")

    assert promotion.promotion_status == BLOCKED
    assert "related_change_id" in promotion.promotion_reason


def test_malformed_promotion_artifact_rejected() -> None:
    artifact = _promotion().to_dict()
    artifact.pop("promotion_reason")

    with pytest.raises(FailClosedRuntimeError, match="malformed"):
        GovernancePromotionResult.from_dict(artifact)


def test_deterministic_promotion_evidence() -> None:
    first = _promotion().to_dict()
    second = _promotion().to_dict()

    assert first == second
    without_hash = deepcopy(first)
    evidence_hash = without_hash.pop("evidence_hash")
    assert evidence_hash == replay_hash(without_hash)


def test_append_only_promotion_lineage() -> None:
    promotions = [
        _promotion(promotion_id="PROMOTION-1", created_at="2026-05-26T00:02:00+00:00"),
        _promotion(promotion_id="PROMOTION-2", created_at="2026-05-26T00:02:01+00:00"),
    ]

    lineage = reconstruct_promotion_lineage(promotions)

    assert lineage["promotion_count"] == 2
    assert lineage["append_only_valid"] is True
    assert lineage["promotions"][0]["promotion_index"] == 0
    assert lineage["promotions"][1]["promotion_index"] == 1


def test_replay_visible_promotion_reconstruction() -> None:
    promotion = _promotion()

    first = reconstruct_promotion_lineage([promotion.to_dict()])
    second = reconstruct_promotion_lineage([promotion.to_dict()])

    assert first == second
    assert first["lineage_hash"].startswith("sha256:")


def test_fail_closed_promotion_blocking_on_mutated_certification() -> None:
    artifact = _certification().to_dict()
    artifact["certification_status"] = "REJECTED"
    promotion = _promotion(certification=artifact)

    assert promotion.promotion_status == BLOCKED
    assert promotion.promotion_reason == "promotion validation failed closed"


def test_mutated_promotion_evidence_rejected() -> None:
    artifact = _promotion().to_dict()
    artifact["promotion_status"] = BLOCKED

    with pytest.raises(FailClosedRuntimeError, match="evidence hash mismatch"):
        GovernancePromotionResult.from_dict(artifact)


def test_duplicate_promotion_lineage_rejected() -> None:
    promotions = [
        _promotion(promotion_id="PROMOTION-1", created_at="2026-05-26T00:02:00+00:00"),
        _promotion(promotion_id="PROMOTION-1", created_at="2026-05-26T00:02:01+00:00"),
    ]

    with pytest.raises(FailClosedRuntimeError, match="duplicate"):
        reconstruct_promotion_lineage(promotions)


def test_out_of_order_promotion_lineage_rejected() -> None:
    promotions = [
        _promotion(promotion_id="PROMOTION-1", created_at="2026-05-26T00:02:02+00:00"),
        _promotion(promotion_id="PROMOTION-2", created_at="2026-05-26T00:02:01+00:00"),
    ]

    with pytest.raises(FailClosedRuntimeError, match="ordering"):
        reconstruct_promotion_lineage(promotions)


def test_no_execution_or_runtime_governance_surface() -> None:
    import aigol.runtime.governance_promotion_discipline as promotion_discipline

    sentinel = ProviderExecutionSentinel()
    _promotion()

    source = inspect.getsource(promotion_discipline)

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
    assert "llm" not in source.lower()
    assert "open(" not in source
    assert "Path(" not in source
