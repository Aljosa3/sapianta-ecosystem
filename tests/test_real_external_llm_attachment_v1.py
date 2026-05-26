"""Tests for REAL_EXTERNAL_LLM_ATTACHMENT_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect

import pytest

from aigol.runtime.bounded_llm_attachment_architecture import BoundedCognitionProposal
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.real_external_llm_attachment import (
    attach_external_llm_response,
    external_model_response_hash,
    reconstruct_external_llm_proposal_lineage,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-26T00:11:00+00:00"


class ProviderExecutionSentinel:
    executed = False

    def fetch(self) -> None:
        self.executed = True
        raise AssertionError("external LLM attachment must not invoke providers")


def _proposal_payload(**overrides) -> dict:
    payload = {
        "proposal_id": "EXTERNAL-LLM-PROPOSAL-1",
        "natural_language_input": "  Propose bounded runtime metadata inspection. ",
        "proposal_type": "CONTRACT_PROPOSAL",
        "requested_capabilities": ["metadata_inspection_provider"],
        "proposed_contract_reference": "contract:EXTERNAL-LLM-CONTRACT-1",
        "created_at": CREATED_AT,
    }
    payload.update(overrides)
    return payload


def _response(**overrides) -> dict:
    payload = {
        "model_response_id": "MODEL-RESPONSE-1",
        "model_provider": "external_llm_provider",
        "model_name": "bounded-proposal-model",
        "proposal_payload": _proposal_payload(),
        "created_at": CREATED_AT,
    }
    payload.update(overrides)
    payload["response_hash"] = external_model_response_hash(payload)
    return payload


def test_valid_external_proposal_normalization() -> None:
    proposal = attach_external_llm_response(_response())

    assert proposal.proposal_id == "EXTERNAL-LLM-PROPOSAL-1"
    assert proposal.proposal_summary == "Propose bounded runtime metadata inspection."
    assert proposal.requested_capabilities == ("metadata_inspection_provider",)
    assert proposal.evidence_hash.startswith("sha256:")


def test_malformed_model_output_rejection() -> None:
    response = _response()
    response.pop("proposal_payload")

    with pytest.raises(FailClosedRuntimeError, match="malformed"):
        attach_external_llm_response(response)


def test_unauthorized_capability_rejection() -> None:
    response = _response(proposal_payload=_proposal_payload(requested_capabilities=["shell_provider"]))

    with pytest.raises(FailClosedRuntimeError, match="unauthorized capability"):
        attach_external_llm_response(response)


def test_response_hash_mismatch_rejection() -> None:
    response = _response()
    response["proposal_payload"]["natural_language_input"] = "changed"

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        attach_external_llm_response(response)


def test_deterministic_proposal_lineage() -> None:
    proposals = [
        attach_external_llm_response(_response(model_response_id="MODEL-RESPONSE-1")),
        attach_external_llm_response(
            _response(
                model_response_id="MODEL-RESPONSE-2",
                proposal_payload=_proposal_payload(
                    proposal_id="EXTERNAL-LLM-PROPOSAL-2",
                    proposed_contract_reference="contract:EXTERNAL-LLM-CONTRACT-2",
                    created_at="2026-05-26T00:11:01+00:00",
                ),
                created_at="2026-05-26T00:11:01+00:00",
            )
        ),
    ]

    first = reconstruct_external_llm_proposal_lineage([proposal.to_dict() for proposal in proposals])
    second = reconstruct_external_llm_proposal_lineage([proposal.to_dict() for proposal in proposals])

    assert first == second
    assert first["proposal_count"] == 2
    assert first["llm_boundary"] == "external_response_proposal_only"
    assert first["lineage_hash"].startswith("sha256:")


def test_replay_visible_cognition_evidence() -> None:
    first = attach_external_llm_response(_response()).to_dict()
    second = BoundedCognitionProposal.from_dict(first).to_dict()

    assert first == second
    without_hash = deepcopy(first)
    evidence_hash = without_hash.pop("evidence_hash")
    assert evidence_hash == replay_hash(without_hash)


def test_governance_authority_separation() -> None:
    proposal = attach_external_llm_response(_response())
    lineage = reconstruct_external_llm_proposal_lineage([proposal])

    assert lineage["governance_authority_separated"] is True
    assert "authorization_id" not in proposal.to_dict()
    assert "routing_id" not in proposal.to_dict()
    assert "session_id" not in proposal.to_dict()


def test_fail_closed_normalization_validation() -> None:
    response = _response(proposal_payload=_proposal_payload(proposed_contract_reference="EXTERNAL-LLM-CONTRACT-1"))

    with pytest.raises(FailClosedRuntimeError, match="contract translation"):
        attach_external_llm_response(response)


def test_no_execution_authority_surface() -> None:
    import aigol.runtime.real_external_llm_attachment as attachment

    sentinel = ProviderExecutionSentinel()
    attach_external_llm_response(_response())

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
    assert "create_governed_execution_contract" not in source
    assert "open(" not in source
    assert "Path(" not in source
