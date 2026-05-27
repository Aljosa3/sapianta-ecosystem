"""Tests for LIVE_EXTERNAL_LLM_PROVIDER_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect

from aigol.runtime.bounded_llm_attachment_architecture import BoundedCognitionProposal
from aigol.runtime.live_external_llm_provider import (
    INFERRED,
    REJECTED,
    LiveExternalLLMInferenceEvidence,
    invoke_live_external_llm_provider,
    reconstruct_live_external_llm_inference_lineage,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-27T00:12:00+00:00"


class ProviderExecutionSentinel:
    executed = False

    def fetch(self) -> None:
        self.executed = True
        raise AssertionError("live external LLM provider must not invoke runtime providers")


def _model_output(**overrides) -> dict:
    output = {
        "proposal_id": "LIVE-LLM-PROPOSAL-1",
        "natural_language_input": "  Propose bounded runtime metadata inspection. ",
        "proposal_type": "CONTRACT_PROPOSAL",
        "requested_capabilities": ["metadata_inspection_provider"],
        "proposed_contract_reference": "contract:LIVE-LLM-CONTRACT-1",
        "created_at": CREATED_AT,
    }
    output.update(overrides)
    return output


def _invoke(output: dict | None = None, *, inference_id: str = "LIVE-INFERENCE-1", prompt: str = "Inspect runtime metadata") -> dict:
    model_output = _model_output() if output is None else output

    def infer(normalized_request: dict) -> dict:
        assert normalized_request == {
            "inference_id": inference_id,
            "model_provider": "external_llm_provider",
            "model_name": "bounded-proposal-model",
            "prompt": "Inspect runtime metadata",
            "allowed_provider": "metadata_inspection_provider",
            "allowed_operation": "inspect_runtime",
            "output_schema": "bounded_cognition_proposal_v1",
            "created_at": CREATED_AT,
        }
        return deepcopy(model_output)

    return invoke_live_external_llm_provider(
        inference_id=inference_id,
        prompt=prompt,
        inference_callable=infer,
        created_at=CREATED_AT,
    )


def test_valid_live_inference_normalization() -> None:
    result = _invoke()
    evidence = result["inference_evidence"]
    proposal = result["proposal"]

    assert isinstance(evidence, LiveExternalLLMInferenceEvidence)
    assert evidence.inference_status == INFERRED
    assert evidence.model_provider == "external_llm_provider"
    assert evidence.model_name == "bounded-proposal-model"
    assert evidence.response_hash.startswith("sha256:")
    assert isinstance(proposal, BoundedCognitionProposal)
    assert proposal.proposal_id == "LIVE-LLM-PROPOSAL-1"
    assert proposal.requested_capabilities == ("metadata_inspection_provider",)
    assert result["proposal_lineage"]["llm_boundary"] == "external_response_proposal_only"


def test_malformed_response_rejection() -> None:
    output = _model_output()
    output.pop("natural_language_input")

    result = _invoke(output)

    assert result["inference_evidence"].inference_status == REJECTED
    assert result["external_model_response"] is None
    assert result["proposal"] is None
    assert result["proposal_lineage"] is None


def test_unauthorized_capability_rejection() -> None:
    result = _invoke(_model_output(requested_capabilities=["readonly_http_get_provider"]))

    assert result["inference_evidence"].inference_status == REJECTED
    assert result["proposal"] is None


def test_deterministic_proposal_lineage() -> None:
    first = _invoke()["inference_evidence"]
    second = invoke_live_external_llm_provider(
        inference_id="LIVE-INFERENCE-2",
        prompt="Inspect runtime metadata",
        inference_callable=lambda normalized_request: _model_output(
            proposal_id="LIVE-LLM-PROPOSAL-2",
            proposed_contract_reference="contract:LIVE-LLM-CONTRACT-2",
        ),
        created_at="2026-05-27T00:12:01+00:00",
    )["inference_evidence"]

    lineage_a = reconstruct_live_external_llm_inference_lineage([first.to_dict(), second.to_dict()])
    lineage_b = reconstruct_live_external_llm_inference_lineage([first.to_dict(), second.to_dict()])

    assert lineage_a == lineage_b
    assert lineage_a["inference_count"] == 2
    assert lineage_a["append_only_valid"] is True
    assert lineage_a["llm_boundary"] == "live_external_inference_proposal_only"
    assert lineage_a["lineage_hash"].startswith("sha256:")


def test_replay_visible_inference_evidence() -> None:
    artifact = _invoke()["inference_evidence"].to_dict()
    reconstructed = LiveExternalLLMInferenceEvidence.from_dict(artifact).to_dict()

    assert artifact == reconstructed
    without_hash = deepcopy(artifact)
    evidence_hash = without_hash.pop("evidence_hash")
    assert evidence_hash == replay_hash(without_hash)


def test_governance_authority_separation() -> None:
    result = _invoke()
    proposal = result["proposal"].to_dict()
    evidence = result["inference_evidence"]
    lineage = reconstruct_live_external_llm_inference_lineage([evidence])

    assert result["governance_authority_separated"] is True
    assert lineage["governance_authority_separated"] is True
    assert "authorization_id" not in proposal
    assert "routing_id" not in proposal
    assert "session_id" not in proposal


def test_fail_closed_normalization_validation() -> None:
    result = _invoke(_model_output(proposed_contract_reference="LIVE-LLM-CONTRACT-1"))

    assert result["inference_evidence"].inference_status == REJECTED
    assert result["inference_evidence"].reason == "live external inference normalization failed closed"


def test_no_execution_authority_surface() -> None:
    import aigol.runtime.live_external_llm_provider as provider

    sentinel = ProviderExecutionSentinel()
    _invoke()

    source = inspect.getsource(provider)

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
