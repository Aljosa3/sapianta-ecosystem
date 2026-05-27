"""Tests for LIVE_OPENAI_RUNTIME_CONNECTOR_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect
import json

from aigol.runtime.bounded_llm_attachment_architecture import BoundedCognitionProposal
from aigol.runtime.live_openai_runtime_connector import (
    NORMALIZED,
    OPENAI_MODEL_IDENTIFIER,
    OPENAI_PROVIDER,
    REJECTED,
    LiveOpenAIRuntimeConnectorEvidence,
    invoke_live_openai_runtime_connector,
    reconstruct_live_openai_runtime_lineage,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-27T00:14:00+00:00"


class ProviderExecutionSentinel:
    executed = False

    def fetch(self) -> None:
        self.executed = True
        raise AssertionError("OpenAI connector must not invoke runtime providers")


def _model_output(**overrides) -> dict:
    output = {
        "proposal_id": "OPENAI-PROPOSAL-1",
        "natural_language_input": "  Propose bounded runtime metadata inspection. ",
        "proposal_type": "CONTRACT_PROPOSAL",
        "requested_capabilities": ["metadata_inspection_provider"],
        "proposed_contract_reference": "contract:OPENAI-CONTRACT-1",
        "created_at": CREATED_AT,
    }
    output.update(overrides)
    return output


def _openai_response(output: dict | str | None = None) -> dict:
    if output is None:
        output = _model_output()
    if isinstance(output, dict):
        output = json.dumps(output, sort_keys=True, separators=(",", ":"))
    return {"output_text": output}


def _invoke(
    output: dict | str | None = None,
    *,
    inference_id: str = "OPENAI-INFERENCE-1",
    prompt: str = "Inspect runtime metadata",
    created_at: str = CREATED_AT,
) -> dict:
    openai_response = _openai_response(output)

    def openai_call(normalized_request: dict) -> dict:
        assert normalized_request == {
            "inference_id": inference_id,
            "provider": OPENAI_PROVIDER,
            "model": OPENAI_MODEL_IDENTIFIER,
            "input": "Inspect runtime metadata",
            "allowed_provider": "metadata_inspection_provider",
            "allowed_operation": "inspect_runtime",
            "output_schema": "bounded_cognition_proposal_v1",
            "created_at": created_at,
        }
        return deepcopy(openai_response)

    return invoke_live_openai_runtime_connector(
        inference_id=inference_id,
        prompt=prompt,
        openai_call=openai_call,
        created_at=created_at,
    )


def test_valid_live_openai_inference_normalization() -> None:
    result = _invoke()
    evidence = result["connector_evidence"]
    proposal = result["proposal"]

    assert isinstance(evidence, LiveOpenAIRuntimeConnectorEvidence)
    assert evidence.connector_status == NORMALIZED
    assert evidence.openai_provider == OPENAI_PROVIDER
    assert evidence.model_identifier == OPENAI_MODEL_IDENTIFIER
    assert evidence.response_hash.startswith("sha256:")
    assert isinstance(proposal, BoundedCognitionProposal)
    assert proposal.proposal_id == "OPENAI-PROPOSAL-1"
    assert proposal.requested_capabilities == ("metadata_inspection_provider",)
    assert result["proposal_lineage"]["llm_boundary"] == "external_response_proposal_only"


def test_malformed_response_rejection() -> None:
    result = _invoke("not-json")

    assert result["connector_evidence"].connector_status == REJECTED
    assert result["external_model_response"] is None
    assert result["proposal"] is None
    assert result["proposal_lineage"] is None


def test_unauthorized_capability_rejection() -> None:
    result = _invoke(_model_output(requested_capabilities=["readonly_http_get_provider"]))

    assert result["connector_evidence"].connector_status == REJECTED
    assert result["proposal"] is None


def test_deterministic_proposal_lineage() -> None:
    first = _invoke()["connector_evidence"]
    second = _invoke(
        _model_output(
            proposal_id="OPENAI-PROPOSAL-2",
            proposed_contract_reference="contract:OPENAI-CONTRACT-2",
        ),
        inference_id="OPENAI-INFERENCE-2",
        created_at="2026-05-27T00:14:01+00:00",
    )["connector_evidence"]

    lineage_a = reconstruct_live_openai_runtime_lineage([first.to_dict(), second.to_dict()])
    lineage_b = reconstruct_live_openai_runtime_lineage([first.to_dict(), second.to_dict()])

    assert lineage_a == lineage_b
    assert lineage_a["inference_count"] == 2
    assert lineage_a["append_only_valid"] is True
    assert lineage_a["llm_boundary"] == "openai_inference_proposal_only"
    assert lineage_a["lineage_hash"].startswith("sha256:")


def test_replay_visible_inference_evidence() -> None:
    artifact = _invoke()["connector_evidence"].to_dict()
    reconstructed = LiveOpenAIRuntimeConnectorEvidence.from_dict(artifact).to_dict()

    assert artifact == reconstructed
    without_hash = deepcopy(artifact)
    evidence_hash = without_hash.pop("evidence_hash")
    assert evidence_hash == replay_hash(without_hash)


def test_governance_authority_separation() -> None:
    result = _invoke()
    proposal = result["proposal"].to_dict()
    evidence = result["connector_evidence"]
    lineage = reconstruct_live_openai_runtime_lineage([evidence])

    assert result["governance_authority_separated"] is True
    assert lineage["governance_authority_separated"] is True
    assert "authorization_id" not in proposal
    assert "routing_id" not in proposal
    assert "session_id" not in proposal


def test_fail_closed_normalization_validation() -> None:
    result = _invoke(_model_output(proposed_contract_reference="OPENAI-CONTRACT-1"))

    assert result["connector_evidence"].connector_status == REJECTED
    assert result["connector_evidence"].reason == "OpenAI inference normalization failed closed"


def test_no_execution_authority_surface() -> None:
    import aigol.runtime.live_openai_runtime_connector as connector

    sentinel = ProviderExecutionSentinel()
    _invoke()

    source = inspect.getsource(connector)

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
    assert "execute_minimal_governed_path" not in source
