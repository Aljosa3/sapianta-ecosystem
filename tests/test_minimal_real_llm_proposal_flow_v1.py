"""Tests for MINIMAL_REAL_LLM_PROPOSAL_FLOW_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect

import pytest

from aigol.runtime.bounded_llm_attachment_architecture import BoundedCognitionProposal
from aigol.runtime.minimal_real_llm_proposal_flow import (
    normalize_real_llm_proposal_input,
    reconstruct_real_llm_proposal_lineage,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-26T00:06:00+00:00"


class ProviderExecutionSentinel:
    executed = False

    def fetch(self) -> None:
        self.executed = True
        raise AssertionError("LLM proposal flow must not invoke providers")


def _llm_input(**overrides) -> dict:
    payload = {
        "proposal_id": "LLM-PROPOSAL-1",
        "natural_language_input": "  Propose   bounded metadata inspection   for governance review. ",
        "proposal_type": "CONTRACT_PROPOSAL",
        "requested_capabilities": ["metadata_inspection_provider"],
        "proposed_contract_reference": "contract:LLM-CONTRACT-CANDIDATE-1",
        "created_at": CREATED_AT,
    }
    payload.update(overrides)
    return payload


def test_valid_bounded_proposal_normalization() -> None:
    proposal = normalize_real_llm_proposal_input(_llm_input())

    assert proposal.proposal_id == "LLM-PROPOSAL-1"
    assert proposal.proposal_summary == "Propose bounded metadata inspection for governance review."
    assert proposal.requested_capabilities == ("metadata_inspection_provider",)
    assert proposal.evidence_hash.startswith("sha256:")


def test_malformed_proposal_rejection() -> None:
    payload = _llm_input()
    payload.pop("natural_language_input")

    with pytest.raises(FailClosedRuntimeError, match="malformed"):
        normalize_real_llm_proposal_input(payload)


def test_unauthorized_capability_proposal_rejection() -> None:
    with pytest.raises(FailClosedRuntimeError, match="unauthorized capability"):
        normalize_real_llm_proposal_input(_llm_input(requested_capabilities=["shell_provider"]))


def test_deterministic_proposal_lineage() -> None:
    proposals = [
        normalize_real_llm_proposal_input(_llm_input(proposal_id="LLM-PROPOSAL-1", created_at="2026-05-26T00:06:00+00:00")),
        normalize_real_llm_proposal_input(_llm_input(proposal_id="LLM-PROPOSAL-2", created_at="2026-05-26T00:06:01+00:00")),
    ]

    first = reconstruct_real_llm_proposal_lineage([proposal.to_dict() for proposal in proposals])
    second = reconstruct_real_llm_proposal_lineage([proposal.to_dict() for proposal in proposals])

    assert first == second
    assert first["proposal_count"] == 2
    assert first["llm_boundary"] == "proposal_only"
    assert first["lineage_hash"].startswith("sha256:")


def test_replay_visible_llm_proposal_evidence() -> None:
    first = normalize_real_llm_proposal_input(_llm_input()).to_dict()
    second = BoundedCognitionProposal.from_dict(first).to_dict()

    assert first == second
    without_hash = deepcopy(first)
    evidence_hash = without_hash.pop("evidence_hash")
    assert evidence_hash == replay_hash(without_hash)


def test_governance_authority_separation() -> None:
    proposal = normalize_real_llm_proposal_input(_llm_input())
    lineage = reconstruct_real_llm_proposal_lineage([proposal])

    assert lineage["governance_authority_separated"] is True
    assert "authorization_id" not in proposal.to_dict()
    assert "routing_id" not in proposal.to_dict()
    assert "session_id" not in proposal.to_dict()


def test_fail_closed_proposal_normalization_validation() -> None:
    with pytest.raises(FailClosedRuntimeError, match="ordering"):
        normalize_real_llm_proposal_input(
            _llm_input(
                requested_capabilities=["readonly_http_get_provider", "metadata_inspection_provider"],
            )
        )


def test_mutated_llm_proposal_evidence_rejected() -> None:
    artifact = normalize_real_llm_proposal_input(_llm_input()).to_dict()
    artifact["proposal_summary"] = "changed"

    with pytest.raises(FailClosedRuntimeError, match="evidence hash mismatch"):
        BoundedCognitionProposal.from_dict(artifact)


def test_no_execution_authority_surface() -> None:
    import aigol.runtime.minimal_real_llm_proposal_flow as llm_flow

    sentinel = ProviderExecutionSentinel()
    normalize_real_llm_proposal_input(_llm_input())

    source = inspect.getsource(llm_flow)

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
