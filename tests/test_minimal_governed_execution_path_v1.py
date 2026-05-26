"""Tests for MINIMAL_GOVERNED_EXECUTION_PATH_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect

import pytest

from aigol.runtime.minimal_governed_execution_path import (
    EXECUTED,
    REJECTED,
    MinimalGovernedExecutionPathResult,
    execute_minimal_governed_path,
    reconstruct_minimal_governed_execution_lineage,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-26T00:07:00+00:00"


def _llm_input(**overrides) -> dict:
    payload = {
        "proposal_id": "LLM-EXECUTION-PROPOSAL-1",
        "natural_language_input": "Propose bounded runtime metadata inspection.",
        "proposal_type": "CONTRACT_PROPOSAL",
        "requested_capabilities": ["metadata_inspection_provider"],
        "proposed_contract_reference": "contract:CONTRACT-EXECUTION-1",
        "created_at": CREATED_AT,
    }
    payload.update(overrides)
    return payload


def _execute(**overrides):
    payload = {
        "execution_id": "EXECUTION-1",
        "llm_proposal_input": _llm_input(),
        "created_at": CREATED_AT,
    }
    payload.update(overrides)
    return execute_minimal_governed_path(**payload)


def test_valid_end_to_end_governed_execution() -> None:
    result = _execute()
    execution = result["execution_result"]

    assert execution.execution_status == EXECUTED
    assert execution.provider == "metadata_inspection_provider"
    assert execution.provider_operation == "inspect_runtime"
    assert result["translation"].translation_status == "TRANSLATED"
    assert result["review"].review_status == "REVIEWED"
    assert result["authorization"].status == "AUTHORIZED"
    assert result["routing"].status == "ROUTED"
    assert result["provider_evidence"]["operation"] == "inspect_runtime"
    assert result["session_lineage"]["operation_count"] == 1


def test_malformed_proposal_rejection() -> None:
    payload = _llm_input()
    payload.pop("natural_language_input")
    result = _execute(llm_proposal_input=payload)

    assert result["execution_result"].execution_status == REJECTED
    assert result["execution_result"].execution_reason == "minimal governed execution path failed closed"
    assert result["provider_evidence"] is None


def test_unauthorized_capability_rejection() -> None:
    result = _execute(llm_proposal_input=_llm_input(requested_capabilities=["readonly_http_get_provider"]))

    assert result["execution_result"].execution_status == REJECTED
    assert result["provider_evidence"] is None
    assert result["session"] is None


def test_invalid_lineage_rejection() -> None:
    result = _execute(llm_proposal_input=_llm_input(proposed_contract_reference="CONTRACT-EXECUTION-1"))

    assert result["execution_result"].execution_status == REJECTED
    assert result["execution_result"].execution_reason == "minimal governed execution path failed closed"


def test_replay_visible_execution_evidence() -> None:
    first = _execute()["execution_result"].to_dict()
    second = MinimalGovernedExecutionPathResult.from_dict(first).to_dict()

    assert first == second
    without_hash = deepcopy(first)
    evidence_hash = without_hash.pop("evidence_hash")
    assert evidence_hash == replay_hash(without_hash)


def test_deterministic_execution_ordering() -> None:
    executions = [
        _execute(execution_id="EXECUTION-1", created_at="2026-05-26T00:07:00+00:00")["execution_result"],
        _execute(
            execution_id="EXECUTION-2",
            llm_proposal_input=_llm_input(
                proposal_id="LLM-EXECUTION-PROPOSAL-2",
                proposed_contract_reference="contract:CONTRACT-EXECUTION-2",
                created_at="2026-05-26T00:07:01+00:00",
            ),
            created_at="2026-05-26T00:07:01+00:00",
        )["execution_result"],
    ]

    first = reconstruct_minimal_governed_execution_lineage([execution.to_dict() for execution in executions])
    second = reconstruct_minimal_governed_execution_lineage([execution.to_dict() for execution in executions])

    assert first == second
    assert first["execution_count"] == 2
    assert first["append_only_valid"] is True
    assert first["lineage_hash"].startswith("sha256:")


def test_governance_authority_separation() -> None:
    result = _execute()
    execution = result["execution_result"].to_dict()
    provider_evidence = result["provider_evidence"]

    assert execution["governance_authority_separated"] is True
    assert "authorization_id" not in provider_evidence
    assert "routing_id" not in provider_evidence
    assert result["review"].review_status == "REVIEWED"


def test_fail_closed_execution_validation() -> None:
    artifact = _execute()["execution_result"].to_dict()
    artifact["execution_status"] = REJECTED

    with pytest.raises(FailClosedRuntimeError, match="evidence hash mismatch"):
        MinimalGovernedExecutionPathResult.from_dict(artifact)


def test_duplicate_execution_lineage_rejected() -> None:
    executions = [
        _execute(execution_id="EXECUTION-1", created_at="2026-05-26T00:07:00+00:00")["execution_result"],
        _execute(execution_id="EXECUTION-1", created_at="2026-05-26T00:07:01+00:00")["execution_result"],
    ]

    with pytest.raises(FailClosedRuntimeError, match="duplicate"):
        reconstruct_minimal_governed_execution_lineage(executions)


def test_out_of_order_execution_lineage_rejected() -> None:
    executions = [
        _execute(execution_id="EXECUTION-1", created_at="2026-05-26T00:07:02+00:00")["execution_result"],
        _execute(execution_id="EXECUTION-2", created_at="2026-05-26T00:07:01+00:00")["execution_result"],
    ]

    with pytest.raises(FailClosedRuntimeError, match="ordering"):
        reconstruct_minimal_governed_execution_lineage(executions)


def test_no_orchestration_or_unauthorized_execution_surface() -> None:
    import aigol.runtime.minimal_governed_execution_path as execution_path

    source = inspect.getsource(execution_path)

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
    assert "readonly_http_get_provider" not in source
    assert "readonly_filesystem_provider" not in source
    assert "open(" not in source
    assert "Path(" not in source
