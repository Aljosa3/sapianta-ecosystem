"""Tests for MINIMAL_REAL_RUNTIME_DEMO_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect
import json

from aigol.runtime.minimal_real_runtime_demo import (
    COMPLETED,
    REJECTED,
    MinimalRealRuntimeDemoEvidence,
    reconstruct_minimal_real_runtime_demo_lineage,
    run_minimal_real_runtime_demo,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-27T00:16:00+00:00"


class MutationSentinel:
    mutated = False

    def mutate(self) -> None:
        self.mutated = True
        raise AssertionError("minimal real runtime demo must not mutate external state")


def _model_output(**overrides) -> dict:
    output = {
        "proposal_id": "DEMO-PROPOSAL-1",
        "natural_language_input": "Propose bounded runtime metadata inspection.",
        "proposal_type": "CONTRACT_PROPOSAL",
        "requested_capabilities": ["metadata_inspection_provider"],
        "proposed_contract_reference": "contract:DEMO-CONTRACT-1",
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


def _run(output: dict | str | None = None, *, demo_id: str = "DEMO-1", created_at: str = CREATED_AT) -> dict:
    response = _openai_response(output)

    def openai_call(normalized_request: dict) -> dict:
        assert normalized_request["provider"] == "openai"
        assert normalized_request["model"] == "gpt-5.5"
        assert normalized_request["allowed_provider"] == "metadata_inspection_provider"
        assert normalized_request["allowed_operation"] == "inspect_runtime"
        return deepcopy(response)

    return run_minimal_real_runtime_demo(
        demo_id=demo_id,
        human_request="  Inspect runtime metadata.  ",
        openai_call=openai_call,
        created_at=created_at,
    )


def test_valid_demo_runtime_flow() -> None:
    result = _run()
    demo = result["demo_evidence"]

    assert demo.demo_status == COMPLETED
    assert result["connector"]["connector_evidence"].connector_status == "NORMALIZED"
    assert result["execution"]["execution_result"].execution_status == "EXECUTED"
    assert result["execution"]["provider_evidence"]["operation"] == "inspect_runtime"
    assert result["isolation"].isolation_status == "ISOLATED"
    assert result["governed_return"].return_status == "ACCEPTED"
    assert result["return_display"].startswith("operation=inspect_runtime")
    assert result["governance_authority_separated"] is True


def test_malformed_proposal_rejection() -> None:
    result = _run("not-json")

    assert result["demo_evidence"].demo_status == REJECTED
    assert result["demo_evidence"].demo_reason == "OpenAI proposal normalization rejected"
    assert result["execution"] is None
    assert result["governed_return"] is None


def test_unauthorized_capability_rejection() -> None:
    result = _run(_model_output(requested_capabilities=["readonly_http_get_provider"]))

    assert result["demo_evidence"].demo_status == REJECTED
    assert result["connector"]["connector_evidence"].connector_status == "REJECTED"
    assert result["execution"] is None


def test_replay_continuity() -> None:
    first = _run(demo_id="DEMO-1", created_at="2026-05-27T00:16:00+00:00")["demo_evidence"]
    second = _run(
        _model_output(
            proposal_id="DEMO-PROPOSAL-2",
            proposed_contract_reference="contract:DEMO-CONTRACT-2",
        ),
        demo_id="DEMO-2",
        created_at="2026-05-27T00:16:01+00:00",
    )["demo_evidence"]

    lineage_a = reconstruct_minimal_real_runtime_demo_lineage([first.to_dict(), second.to_dict()])
    lineage_b = reconstruct_minimal_real_runtime_demo_lineage([first.to_dict(), second.to_dict()])

    assert lineage_a == lineage_b
    assert lineage_a["demo_count"] == 2
    assert lineage_a["append_only_valid"] is True
    assert lineage_a["governance_authority_separated"] is True


def test_deterministic_evidence_generation() -> None:
    artifact = _run()["demo_evidence"].to_dict()
    reconstructed = MinimalRealRuntimeDemoEvidence.from_dict(artifact).to_dict()

    assert artifact == reconstructed
    without_hash = deepcopy(artifact)
    evidence_hash = without_hash.pop("evidence_hash")
    assert evidence_hash == replay_hash(without_hash)


def test_fail_closed_execution_behavior() -> None:
    result = _run(_model_output(proposed_contract_reference="DEMO-CONTRACT-1"))

    assert result["demo_evidence"].demo_status == REJECTED
    assert result["demo_evidence"].connector_evidence_hash.startswith("sha256:")
    assert result["execution"] is None


def test_no_unbounded_runtime_surface() -> None:
    import aigol.runtime.minimal_real_runtime_demo as demo

    sentinel = MutationSentinel()
    _run()

    source = inspect.getsource(demo)

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
