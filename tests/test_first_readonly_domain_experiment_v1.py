"""Tests for FIRST_READONLY_DOMAIN_EXPERIMENT_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect
import json

from aigol.runtime.first_readonly_domain_experiment import (
    DOMAIN_NAME,
    DOMAIN_SURFACE,
    EXPERIMENT_COMPLETED,
    EXPERIMENT_REJECTED,
    ReadonlyDomainExperimentEvidence,
    reconstruct_readonly_domain_experiment_lineage,
    run_governance_runtime_inspector_experiment,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-27T00:17:00+00:00"


class MutationSentinel:
    mutated = False

    def mutate(self) -> None:
        self.mutated = True
        raise AssertionError("readonly domain experiment must not mutate external state")


def _model_output(**overrides) -> dict:
    output = {
        "proposal_id": "DOMAIN-PROPOSAL-1",
        "natural_language_input": "Inspect governance runtime metadata.",
        "proposal_type": "CONTRACT_PROPOSAL",
        "requested_capabilities": ["metadata_inspection_provider"],
        "proposed_contract_reference": "contract:DOMAIN-CONTRACT-1",
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


def _run(output: dict | str | None = None, *, experiment_id: str = "DOMAIN-EXPERIMENT-1", created_at: str = CREATED_AT) -> dict:
    response = _openai_response(output)

    def openai_call(normalized_request: dict) -> dict:
        assert normalized_request["provider"] == "openai"
        assert normalized_request["allowed_provider"] == "metadata_inspection_provider"
        assert normalized_request["allowed_operation"] == "inspect_runtime"
        return deepcopy(response)

    return run_governance_runtime_inspector_experiment(
        experiment_id=experiment_id,
        human_request="  inspect runtime status  ",
        openai_call=openai_call,
        created_at=created_at,
    )


def test_valid_readonly_domain_execution() -> None:
    result = _run()
    evidence = result["experiment_evidence"]

    assert evidence.experiment_status == EXPERIMENT_COMPLETED
    assert evidence.domain_name == DOMAIN_NAME
    assert evidence.domain_surface == DOMAIN_SURFACE
    assert result["demo"]["demo_evidence"].demo_status == "COMPLETED"
    assert result["demo"]["execution"]["provider_evidence"]["operation"] == "inspect_runtime"
    assert result["domain_return"].startswith("operation=inspect_runtime")
    assert result["governance_authority_separated"] is True


def test_malformed_cognition_rejection() -> None:
    result = _run("not-json")

    assert result["experiment_evidence"].experiment_status == EXPERIMENT_REJECTED
    assert result["experiment_evidence"].experiment_reason == "readonly domain experiment rejected by governed runtime"
    assert result["demo"]["execution"] is None


def test_unauthorized_capability_rejection() -> None:
    result = _run(_model_output(requested_capabilities=["readonly_http_get_provider"]))

    assert result["experiment_evidence"].experiment_status == EXPERIMENT_REJECTED
    assert result["demo"]["connector"]["connector_evidence"].connector_status == "REJECTED"
    assert result["demo"]["execution"] is None


def test_replay_continuity_preservation() -> None:
    first = _run(experiment_id="DOMAIN-EXPERIMENT-1", created_at="2026-05-27T00:17:00+00:00")["experiment_evidence"]
    second = _run(
        _model_output(
            proposal_id="DOMAIN-PROPOSAL-2",
            proposed_contract_reference="contract:DOMAIN-CONTRACT-2",
        ),
        experiment_id="DOMAIN-EXPERIMENT-2",
        created_at="2026-05-27T00:17:01+00:00",
    )["experiment_evidence"]

    lineage_a = reconstruct_readonly_domain_experiment_lineage([first.to_dict(), second.to_dict()])
    lineage_b = reconstruct_readonly_domain_experiment_lineage([first.to_dict(), second.to_dict()])

    assert lineage_a == lineage_b
    assert lineage_a["experiment_count"] == 2
    assert lineage_a["append_only_valid"] is True
    assert lineage_a["governance_authority_separated"] is True


def test_deterministic_evidence_generation() -> None:
    artifact = _run()["experiment_evidence"].to_dict()
    reconstructed = ReadonlyDomainExperimentEvidence.from_dict(artifact).to_dict()

    assert artifact == reconstructed
    without_hash = deepcopy(artifact)
    evidence_hash = without_hash.pop("evidence_hash")
    assert evidence_hash == replay_hash(without_hash)


def test_fail_closed_execution_behavior() -> None:
    result = _run(_model_output(proposed_contract_reference="DOMAIN-CONTRACT-1"))

    assert result["experiment_evidence"].experiment_status == EXPERIMENT_REJECTED
    assert result["demo"]["execution"] is None


def test_no_unbounded_domain_surface() -> None:
    import aigol.runtime.first_readonly_domain_experiment as experiment

    sentinel = MutationSentinel()
    _run()

    source = inspect.getsource(experiment)

    assert sentinel.mutated is False
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
    assert "retry" not in source.lower()
    assert "open(" not in source
    assert "Path(" not in source
