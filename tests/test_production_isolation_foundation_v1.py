"""Tests for PRODUCTION_ISOLATION_FOUNDATION_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect

import pytest

from aigol.runtime.minimal_governed_execution_path import execute_minimal_governed_path
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.production_isolation_foundation import (
    ISOLATED,
    REJECTED,
    ProductionIsolationEvidence,
    reconstruct_production_isolation_lineage,
    validate_production_isolation,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-26T00:09:00+00:00"


def _llm_input(**overrides) -> dict:
    payload = {
        "proposal_id": "ISOLATION-PROPOSAL-1",
        "natural_language_input": "Propose bounded runtime metadata inspection.",
        "proposal_type": "CONTRACT_PROPOSAL",
        "requested_capabilities": ["metadata_inspection_provider"],
        "proposed_contract_reference": "contract:ISOLATION-CONTRACT-1",
        "created_at": CREATED_AT,
    }
    payload.update(overrides)
    return payload


def _execution(**overrides):
    payload = {
        "execution_id": "ISOLATION-EXECUTION-1",
        "llm_proposal_input": _llm_input(),
        "created_at": CREATED_AT,
    }
    payload.update(overrides)
    return execute_minimal_governed_path(**payload)["execution_result"]


def _quota(**overrides) -> dict:
    payload = {
        "max_provider_invocations": 1,
        "allowed_provider": "metadata_inspection_provider",
        "allowed_operation": "inspect_runtime",
    }
    payload.update(overrides)
    return payload


def _metadata(**overrides) -> dict:
    payload = {
        "isolation_mode": "LOCAL_READONLY_SINGLE_PROVIDER",
        "provider_state_mutation_allowed": False,
        "runtime_state_mutation_allowed": False,
        "network_mutation_allowed": False,
        "replay_durability": "APPEND_ONLY_HASHED_EVIDENCE",
        "governance_authority_separated": True,
    }
    payload.update(overrides)
    return payload


def _isolation(**overrides) -> ProductionIsolationEvidence:
    payload = {
        "isolation_id": "ISOLATION-1",
        "execution_result": _execution(),
        "quota_policy": _quota(),
        "isolation_metadata": _metadata(),
        "created_at": CREATED_AT,
    }
    payload.update(overrides)
    return validate_production_isolation(**payload)


def test_quota_enforcement() -> None:
    isolation = _isolation()

    assert isolation.isolation_status == ISOLATED
    assert isolation.quota_policy["max_provider_invocations"] == 1
    assert isolation.quota_policy["allowed_provider"] == "metadata_inspection_provider"


def test_isolation_metadata_validation() -> None:
    isolation = _isolation()

    assert isolation.isolation_metadata["isolation_mode"] == "LOCAL_READONLY_SINGLE_PROVIDER"
    assert isolation.isolation_metadata["provider_state_mutation_allowed"] is False
    assert isolation.isolation_metadata["governance_authority_separated"] is True


def test_replay_durability_continuity() -> None:
    execution = _execution()
    isolation = _isolation(execution_result=execution)

    expected = replay_hash(
        {
            "execution_evidence_hash": execution.evidence_hash,
            "provider_evidence_hash": execution.provider_evidence_hash,
            "session_lineage_hash": execution.session_lineage_hash,
            "isolation_metadata": isolation.to_dict()["isolation_metadata"],
        }
    )

    assert isolation.replay_durability_hash == expected


def test_fail_closed_quota_violations() -> None:
    isolation = _isolation(quota_policy=_quota(max_provider_invocations=2))

    assert isolation.isolation_status == REJECTED
    assert isolation.reason == "production isolation validation failed closed"


def test_deterministic_isolation_evidence() -> None:
    first = _isolation().to_dict()
    second = ProductionIsolationEvidence.from_dict(first).to_dict()

    assert first == second
    without_hash = deepcopy(first)
    evidence_hash = without_hash.pop("evidence_hash")
    assert evidence_hash == replay_hash(without_hash)


def test_append_only_replay_durability() -> None:
    isolations = [
        _isolation(isolation_id="ISOLATION-1", created_at="2026-05-26T00:09:00+00:00"),
        _isolation(
            isolation_id="ISOLATION-2",
            execution_result=_execution(
                execution_id="ISOLATION-EXECUTION-2",
                llm_proposal_input=_llm_input(
                    proposal_id="ISOLATION-PROPOSAL-2",
                    proposed_contract_reference="contract:ISOLATION-CONTRACT-2",
                    created_at="2026-05-26T00:09:01+00:00",
                ),
                created_at="2026-05-26T00:09:01+00:00",
            ),
            created_at="2026-05-26T00:09:01+00:00",
        ),
    ]

    lineage = reconstruct_production_isolation_lineage(isolations)

    assert lineage["isolation_count"] == 2
    assert lineage["append_only_valid"] is True
    assert lineage["lineage_hash"].startswith("sha256:")


def test_bounded_execution_containment() -> None:
    isolation = _isolation()

    assert isolation.isolation_status == ISOLATED
    assert isolation.isolation_metadata["network_mutation_allowed"] is False
    assert isolation.isolation_metadata["runtime_state_mutation_allowed"] is False


def test_fail_closed_isolation_inconsistency() -> None:
    isolation = _isolation(isolation_metadata=_metadata(runtime_state_mutation_allowed=True))

    assert isolation.isolation_status == REJECTED


def test_mutated_isolation_evidence_rejected() -> None:
    artifact = _isolation().to_dict()
    artifact["isolation_status"] = REJECTED

    with pytest.raises(FailClosedRuntimeError, match="evidence hash mismatch"):
        ProductionIsolationEvidence.from_dict(artifact)


def test_duplicate_isolation_lineage_rejected() -> None:
    isolation = _isolation()

    with pytest.raises(FailClosedRuntimeError, match="duplicate"):
        reconstruct_production_isolation_lineage([isolation, isolation])


def test_no_disallowed_production_runtime_surface() -> None:
    import aigol.runtime.production_isolation_foundation as isolation

    source = inspect.getsource(isolation)

    assert "subprocess" not in source
    assert "os.system" not in source
    assert "async " not in source
    assert "await " not in source
    assert "threading" not in source
    assert "multiprocessing" not in source
    assert "kubernetes" not in source.lower()
    assert "docker" not in source.lower()
    assert "swarm" not in source.lower()
    assert "orchestrat" not in source.lower()
    assert "autonomous" not in source.lower()
    assert "retry" not in source.lower()
    assert "open(" not in source
    assert "Path(" not in source
