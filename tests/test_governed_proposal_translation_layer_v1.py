"""Tests for GOVERNED_PROPOSAL_TRANSLATION_LAYER_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect

import pytest

from aigol.runtime.bounded_llm_attachment_architecture import (
    CONTRACT_PROPOSAL,
    GOVERNANCE_QUERY,
    ROUTING_PROPOSAL,
    create_bounded_cognition_proposal,
)
from aigol.runtime.governed_proposal_translation_layer import (
    REJECTED,
    TRANSLATED,
    GovernedProposalTranslationResult,
    reconstruct_translation_lineage,
    translate_bounded_proposal,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-26T00:04:00+00:00"
TRANSLATED_AT = "2026-05-26T00:04:10+00:00"


class ProviderExecutionSentinel:
    executed = False

    def fetch(self) -> None:
        self.executed = True
        raise AssertionError("translation layer must not invoke providers")


def _proposal(**overrides):
    payload = {
        "proposal_id": "PROPOSAL-TRANSLATE-1",
        "proposal_type": CONTRACT_PROPOSAL,
        "proposal_summary": "proposal asks for bounded metadata inspection candidate",
        "requested_capabilities": ["metadata_inspection_provider"],
        "proposed_contract_reference": "contract:CONTRACT-CANDIDATE-1",
        "created_at": CREATED_AT,
    }
    payload.update(overrides)
    return create_bounded_cognition_proposal(**payload)


def _translation(**overrides) -> GovernedProposalTranslationResult:
    payload = {
        "translation_id": "TRANSLATION-1",
        "proposal": _proposal(),
        "created_at": TRANSLATED_AT,
    }
    payload.update(overrides)
    return translate_bounded_proposal(**payload)


def test_valid_proposal_translation() -> None:
    translation = _translation()
    candidate = translation.to_dict()["translated_contract_candidate"]

    assert translation.translation_status == TRANSLATED
    assert translation.proposal_id == "PROPOSAL-TRANSLATE-1"
    assert candidate["candidate_type"] == "GOVERNED_EXECUTION_CONTRACT_CANDIDATE"
    assert candidate["allowed_providers"] == ["metadata_inspection_provider"]
    assert candidate["governance_authority_required"] is True
    assert translation.evidence_hash.startswith("sha256:")


def test_routing_proposal_translation_candidate() -> None:
    proposal = _proposal(
        proposal_id="PROPOSAL-ROUTE-1",
        proposal_type=ROUTING_PROPOSAL,
        requested_capabilities=["metadata_inspection_provider", "readonly_http_get_provider"],
        proposed_contract_reference="contract:CONTRACT-CANDIDATE-ROUTE-1",
    )

    translation = _translation(proposal=proposal)
    candidate = translation.to_dict()["translated_contract_candidate"]

    assert translation.translation_status == TRANSLATED
    assert candidate["source_proposal_type"] == ROUTING_PROPOSAL
    assert candidate["allowed_providers"] == ["metadata_inspection_provider", "readonly_http_get_provider"]


def test_malformed_proposal_rejection() -> None:
    artifact = _proposal().to_dict()
    artifact.pop("proposal_summary")
    translation = _translation(proposal=artifact)

    assert translation.translation_status == REJECTED
    assert translation.translation_reason == "translation validation failed closed"


def test_unauthorized_capability_rejection() -> None:
    artifact = _proposal().to_dict()
    artifact["requested_capabilities"] = ["shell_provider"]
    translation = _translation(proposal=artifact)

    assert translation.translation_status == REJECTED
    assert translation.translation_reason == "translation validation failed closed"


def test_governance_query_translation_rejected() -> None:
    proposal = _proposal(
        proposal_id="PROPOSAL-QUERY-1",
        proposal_type=GOVERNANCE_QUERY,
        requested_capabilities=["governance_query"],
        proposed_contract_reference="",
    )

    translation = _translation(proposal=proposal)

    assert translation.translation_status == REJECTED
    assert "do not translate" in translation.translation_reason


def test_deterministic_translation_lineage() -> None:
    translations = [
        _translation(translation_id="TRANSLATION-1", created_at="2026-05-26T00:04:10+00:00"),
        _translation(
            translation_id="TRANSLATION-2",
            proposal=_proposal(proposal_id="PROPOSAL-TRANSLATE-2", created_at="2026-05-26T00:04:01+00:00"),
            created_at="2026-05-26T00:04:11+00:00",
        ),
    ]

    first = reconstruct_translation_lineage([translation.to_dict() for translation in translations])
    second = reconstruct_translation_lineage([translation.to_dict() for translation in translations])

    assert first == second
    assert first["translation_count"] == 2
    assert first["append_only_valid"] is True
    assert first["lineage_hash"].startswith("sha256:")


def test_replay_visible_translation_evidence() -> None:
    first = _translation().to_dict()
    second = GovernedProposalTranslationResult.from_dict(first).to_dict()

    assert first == second
    without_hash = deepcopy(first)
    evidence_hash = without_hash.pop("evidence_hash")
    assert evidence_hash == replay_hash(without_hash)


def test_governance_authority_separation() -> None:
    translation = _translation()
    candidate = translation.to_dict()["translated_contract_candidate"]
    lineage = reconstruct_translation_lineage([translation])

    assert lineage["governance_authority_separated"] is True
    assert candidate["governance_authority_required"] is True
    assert "authorization_id" not in candidate
    assert "routing_id" not in candidate
    assert "session_id" not in candidate


def test_fail_closed_translation_validation() -> None:
    artifact = _proposal().to_dict()
    artifact["proposed_contract_reference"] = "contract:CHANGED"

    translation = _translation(proposal=artifact)

    assert translation.translation_status == REJECTED
    assert translation.translation_reason == "translation validation failed closed"


def test_mutated_translation_evidence_rejected() -> None:
    artifact = _translation().to_dict()
    artifact["translation_status"] = REJECTED

    with pytest.raises(FailClosedRuntimeError, match="evidence hash mismatch"):
        GovernedProposalTranslationResult.from_dict(artifact)


def test_duplicate_translation_lineage_rejected() -> None:
    translations = [
        _translation(translation_id="TRANSLATION-1", created_at="2026-05-26T00:04:10+00:00"),
        _translation(translation_id="TRANSLATION-1", created_at="2026-05-26T00:04:11+00:00"),
    ]

    with pytest.raises(FailClosedRuntimeError, match="duplicate"):
        reconstruct_translation_lineage(translations)


def test_out_of_order_translation_lineage_rejected() -> None:
    translations = [
        _translation(translation_id="TRANSLATION-1", created_at="2026-05-26T00:04:12+00:00"),
        _translation(translation_id="TRANSLATION-2", created_at="2026-05-26T00:04:11+00:00"),
    ]

    with pytest.raises(FailClosedRuntimeError, match="ordering"):
        reconstruct_translation_lineage(translations)


def test_no_execution_authority_surface() -> None:
    import aigol.runtime.governed_proposal_translation_layer as translation_layer

    sentinel = ProviderExecutionSentinel()
    _translation()

    source = inspect.getsource(translation_layer)

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
