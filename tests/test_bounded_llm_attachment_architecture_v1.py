"""Tests for BOUNDED_LLM_ATTACHMENT_ARCHITECTURE_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect

import pytest

from aigol.runtime.bounded_llm_attachment_architecture import (
    CONTRACT_PROPOSAL,
    GOVERNANCE_QUERY,
    ROUTING_PROPOSAL,
    BoundedCognitionProposal,
    create_bounded_cognition_proposal,
    reconstruct_cognition_lineage,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-26T00:03:00+00:00"


class ProviderExecutionSentinel:
    executed = False

    def fetch(self) -> None:
        self.executed = True
        raise AssertionError("cognition attachment must not invoke providers")


def _proposal(**overrides) -> BoundedCognitionProposal:
    payload = {
        "proposal_id": "PROPOSAL-1",
        "proposal_type": CONTRACT_PROPOSAL,
        "proposal_summary": "proposal requests bounded metadata inspection contract review",
        "requested_capabilities": ["metadata_inspection_provider"],
        "proposed_contract_reference": "contract:CONTRACT-PROPOSAL-1",
        "created_at": CREATED_AT,
    }
    payload.update(overrides)
    return create_bounded_cognition_proposal(**payload)


def test_valid_proposal_creation() -> None:
    proposal = _proposal()

    assert proposal.proposal_id == "PROPOSAL-1"
    assert proposal.proposal_type == CONTRACT_PROPOSAL
    assert proposal.requested_capabilities == ("metadata_inspection_provider",)
    assert proposal.proposed_contract_reference == "contract:CONTRACT-PROPOSAL-1"
    assert proposal.evidence_hash.startswith("sha256:")


def test_valid_governance_query_creation() -> None:
    proposal = _proposal(
        proposal_id="PROPOSAL-QUERY-1",
        proposal_type=GOVERNANCE_QUERY,
        requested_capabilities=["governance_query"],
        proposed_contract_reference="",
    )

    assert proposal.proposal_type == GOVERNANCE_QUERY
    assert proposal.requested_capabilities == ("governance_query",)
    assert proposal.proposed_contract_reference == ""


def test_malformed_proposal_rejection() -> None:
    artifact = _proposal().to_dict()
    artifact.pop("proposal_summary")

    with pytest.raises(FailClosedRuntimeError, match="malformed"):
        BoundedCognitionProposal.from_dict(artifact)


def test_unknown_proposal_type_rejection() -> None:
    with pytest.raises(FailClosedRuntimeError, match="unknown proposal type"):
        _proposal(proposal_type="EXECUTION_PROPOSAL")


def test_unauthorized_capability_proposal_rejection() -> None:
    with pytest.raises(FailClosedRuntimeError, match="unauthorized capability"):
        _proposal(requested_capabilities=["shell_provider"])


def test_invalid_contract_translation_boundary_rejection() -> None:
    with pytest.raises(FailClosedRuntimeError, match="contract translation"):
        _proposal(proposed_contract_reference="CONTRACT-PROPOSAL-1")


def test_cannot_mix_governance_query_with_contract_proposal() -> None:
    with pytest.raises(FailClosedRuntimeError, match="governance_query"):
        _proposal(requested_capabilities=["governance_query"])


def test_deterministic_proposal_lineage() -> None:
    proposals = [
        _proposal(proposal_id="PROPOSAL-1", created_at="2026-05-26T00:03:00+00:00"),
        _proposal(
            proposal_id="PROPOSAL-2",
            proposal_type=ROUTING_PROPOSAL,
            requested_capabilities=["metadata_inspection_provider", "readonly_http_get_provider"],
            proposed_contract_reference="contract:CONTRACT-PROPOSAL-2",
            created_at="2026-05-26T00:03:01+00:00",
        ),
    ]

    first = reconstruct_cognition_lineage([proposal.to_dict() for proposal in proposals])
    second = reconstruct_cognition_lineage([proposal.to_dict() for proposal in proposals])

    assert first == second
    assert first["proposal_count"] == 2
    assert first["append_only_valid"] is True
    assert first["lineage_hash"].startswith("sha256:")


def test_replay_visible_cognition_evidence() -> None:
    first = _proposal().to_dict()
    second = BoundedCognitionProposal.from_dict(first).to_dict()

    assert first == second
    without_hash = deepcopy(first)
    evidence_hash = without_hash.pop("evidence_hash")
    assert evidence_hash == replay_hash(without_hash)


def test_governance_authority_separation() -> None:
    proposal = _proposal()
    lineage = reconstruct_cognition_lineage([proposal])

    assert lineage["governance_authority_separated"] is True
    assert "authorization_id" not in proposal.to_dict()
    assert "routing_id" not in proposal.to_dict()
    assert "session_id" not in proposal.to_dict()


def test_fail_closed_cognition_boundary_validation() -> None:
    artifact = _proposal().to_dict()
    artifact["requested_capabilities"] = ["readonly_filesystem_provider"]

    with pytest.raises(FailClosedRuntimeError, match="evidence hash mismatch"):
        BoundedCognitionProposal.from_dict(artifact)


def test_immutable_proposal_evidence() -> None:
    proposal = _proposal()
    before = proposal.to_dict()

    with pytest.raises(AttributeError):
        proposal.proposal_type = ROUTING_PROPOSAL

    assert proposal.to_dict() == before


def test_duplicate_cognition_lineage_rejected() -> None:
    proposals = [
        _proposal(proposal_id="PROPOSAL-1", created_at="2026-05-26T00:03:00+00:00"),
        _proposal(proposal_id="PROPOSAL-1", created_at="2026-05-26T00:03:01+00:00"),
    ]

    with pytest.raises(FailClosedRuntimeError, match="duplicate"):
        reconstruct_cognition_lineage(proposals)


def test_out_of_order_cognition_lineage_rejected() -> None:
    proposals = [
        _proposal(proposal_id="PROPOSAL-1", created_at="2026-05-26T00:03:02+00:00"),
        _proposal(proposal_id="PROPOSAL-2", created_at="2026-05-26T00:03:01+00:00"),
    ]

    with pytest.raises(FailClosedRuntimeError, match="ordering"):
        reconstruct_cognition_lineage(proposals)


def test_no_execution_authority_surface() -> None:
    import aigol.runtime.bounded_llm_attachment_architecture as attachment

    sentinel = ProviderExecutionSentinel()
    _proposal()

    source = inspect.getsource(attachment)

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
    assert "open(" not in source
    assert "Path(" not in source
