"""Tests for GOVERNED_RETURN_INTERPRETATION_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect

import pytest

from aigol.runtime.governed_return_interpretation import (
    ACCEPTED,
    REJECTED,
    GovernedReturnInterpretationArtifact,
    interpret_governed_execution_return,
    reconstruct_governed_return_lineage,
)
from aigol.runtime.minimal_governed_execution_path import execute_minimal_governed_path
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.production_isolation_foundation import validate_production_isolation
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-26T00:10:00+00:00"


def _llm_input(**overrides) -> dict:
    payload = {
        "proposal_id": "RETURN-PROPOSAL-1",
        "natural_language_input": "Propose bounded runtime metadata inspection.",
        "proposal_type": "CONTRACT_PROPOSAL",
        "requested_capabilities": ["metadata_inspection_provider"],
        "proposed_contract_reference": "contract:RETURN-CONTRACT-1",
        "created_at": CREATED_AT,
    }
    payload.update(overrides)
    return payload


def _execution(**overrides):
    payload = {
        "execution_id": "RETURN-EXECUTION-1",
        "llm_proposal_input": _llm_input(),
        "created_at": CREATED_AT,
    }
    payload.update(overrides)
    return execute_minimal_governed_path(**payload)


def _isolation(execution_result):
    return validate_production_isolation(
        isolation_id="RETURN-ISOLATION-1",
        execution_result=execution_result,
        quota_policy={
            "max_provider_invocations": 1,
            "allowed_provider": "metadata_inspection_provider",
            "allowed_operation": "inspect_runtime",
        },
        isolation_metadata={
            "isolation_mode": "LOCAL_READONLY_SINGLE_PROVIDER",
            "provider_state_mutation_allowed": False,
            "runtime_state_mutation_allowed": False,
            "network_mutation_allowed": False,
            "replay_durability": "APPEND_ONLY_HASHED_EVIDENCE",
            "governance_authority_separated": True,
        },
        created_at=CREATED_AT,
    )


def _return(**overrides) -> GovernedReturnInterpretationArtifact:
    execution = _execution()
    payload = {
        "return_id": "RETURN-1",
        "execution_result": execution["execution_result"],
        "provider_evidence": execution["provider_evidence"],
        "session_lineage": execution["session_lineage"],
        "isolation_evidence": _isolation(execution["execution_result"]),
        "created_at": CREATED_AT,
    }
    payload.update(overrides)
    return interpret_governed_execution_return(**payload)


def test_valid_governed_return_normalization() -> None:
    artifact = _return()

    assert artifact.return_status == ACCEPTED
    assert artifact.provider_reference == "metadata_inspection_provider.inspect_runtime"
    assert "operation=inspect_runtime" in artifact.normalized_return_summary
    assert "metadata_keys=" in artifact.normalized_return_summary


def test_malformed_execution_evidence_rejection() -> None:
    execution = _execution()
    malformed = execution["execution_result"].to_dict()
    malformed.pop("provider")

    artifact = _return(execution_result=malformed)

    assert artifact.return_status == REJECTED
    assert artifact.normalized_return_summary == "governed return interpretation failed closed"


def test_invalid_lineage_rejection() -> None:
    execution = _execution()
    lineage = deepcopy(execution["session_lineage"])
    lineage["replay_valid"] = False

    artifact = _return(session_lineage=lineage)

    assert artifact.return_status == REJECTED


def test_unauthorized_provider_return_rejection() -> None:
    execution = _execution()
    provider_evidence = deepcopy(execution["provider_evidence"])
    provider_evidence["operation"] = "inspect_process"

    artifact = _return(provider_evidence=provider_evidence)

    assert artifact.return_status == REJECTED


def test_deterministic_return_ordering() -> None:
    returns = [
        _return(return_id="RETURN-1", created_at="2026-05-26T00:10:00+00:00"),
        _return(return_id="RETURN-2", created_at="2026-05-26T00:10:01+00:00"),
    ]

    first = reconstruct_governed_return_lineage([item.to_dict() for item in returns])
    second = reconstruct_governed_return_lineage([item.to_dict() for item in returns])

    assert first == second
    assert first["return_count"] == 2
    assert first["append_only_valid"] is True


def test_replay_visible_return_evidence() -> None:
    first = _return().to_dict()
    second = GovernedReturnInterpretationArtifact.from_dict(first).to_dict()

    assert first == second
    without_hash = deepcopy(first)
    evidence_hash = without_hash.pop("evidence_hash")
    assert evidence_hash == replay_hash(without_hash)


def test_append_only_return_lineage() -> None:
    returns = [
        _return(return_id="RETURN-1", created_at="2026-05-26T00:10:00+00:00"),
        _return(return_id="RETURN-2", created_at="2026-05-26T00:10:01+00:00"),
    ]

    lineage = reconstruct_governed_return_lineage(returns)

    assert lineage["append_only_valid"] is True
    assert lineage["governance_authority_separated"] is True
    assert lineage["lineage_hash"].startswith("sha256:")


def test_mutated_return_evidence_rejected() -> None:
    artifact = _return().to_dict()
    artifact["return_status"] = REJECTED

    with pytest.raises(FailClosedRuntimeError, match="evidence hash mismatch"):
        GovernedReturnInterpretationArtifact.from_dict(artifact)


def test_duplicate_return_lineage_rejected() -> None:
    artifact = _return()

    with pytest.raises(FailClosedRuntimeError, match="duplicate"):
        reconstruct_governed_return_lineage([artifact, artifact])


def test_no_provider_execution_or_orchestration_surface() -> None:
    import aigol.runtime.governed_return_interpretation as interpretation

    source = inspect.getsource(interpretation)

    assert "subprocess" not in source
    assert "os.system" not in source
    assert "async " not in source
    assert "await " not in source
    assert "threading" not in source
    assert "multiprocessing" not in source
    assert "orchestrat" not in source.lower()
    assert "autonomous" not in source.lower()
    assert "retry" not in source.lower()
    assert "inspect_runtime()" not in source
    assert "MetadataInspectionProvider" not in source
    assert "open(" not in source
    assert "Path(" not in source
