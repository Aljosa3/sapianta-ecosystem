"""Tests for AIGOL_FIRST_GOVERNED_DOMAIN_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.first_governed_domain_runtime import (
    ACTIVE,
    AIGOL_FIRST_GOVERNED_DOMAIN_RUNTIME_VERSION,
    CREATED,
    DOMAIN_ACTIVATED,
    DOMAIN_CREATED,
    DOMAIN_EXECUTED,
    DOMAIN_RETIRED,
    DOMAIN_SUSPENDED,
    DOMAIN_VALIDATED,
    EXECUTING,
    FIRST_GOVERNED_DOMAIN_ID,
    RETIRED,
    SUSPENDED,
    VALIDATED,
    reconstruct_first_governed_domain_replay,
    run_first_governed_domain_lifecycle,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-05T00:00:00+00:00"


def _run(tmp_path, **overrides) -> dict:
    args = {
        "replay_dir": tmp_path / "first_domain",
        "actor_id": "AIGOL_GOVERNANCE",
        "timestamp": CREATED_AT,
    }
    args.update(overrides)
    return run_first_governed_domain_lifecycle(**args)


def test_first_governed_domain_runs_complete_lifecycle(tmp_path) -> None:
    capture = _run(tmp_path)
    reconstructed = reconstruct_first_governed_domain_replay(tmp_path / "first_domain")
    artifact = capture["first_governed_domain_artifact"]
    execution = capture["execution_example_artifact"]

    assert artifact["runtime_version"] == AIGOL_FIRST_GOVERNED_DOMAIN_RUNTIME_VERSION
    assert artifact["domain_id"] == FIRST_GOVERNED_DOMAIN_ID
    assert artifact["lifecycle_state"] == RETIRED
    assert artifact["lifecycle_event"] == DOMAIN_RETIRED
    assert execution["decision_result"] == "REQUIRES_HUMAN_REVIEW"
    assert execution["boundary_result"] == "EXTERNAL_EXECUTION_NOT_AUTHORIZED"
    assert execution["external_execution_performed"] is False
    assert reconstructed["lifecycle_state"] == RETIRED
    assert reconstructed["lifecycle_events"] == [
        DOMAIN_CREATED,
        DOMAIN_VALIDATED,
        DOMAIN_ACTIVATED,
        DOMAIN_EXECUTED,
        DOMAIN_SUSPENDED,
        DOMAIN_RETIRED,
    ]
    assert reconstructed["replay_artifact_count"] == 6
    assert reconstructed["provider_invoked"] is False
    assert reconstructed["worker_invoked"] is False
    assert reconstructed["external_execution_performed"] is False
    assert reconstructed["governance_mutated"] is False


def test_first_governed_domain_integrates_certified_domain_runtime(tmp_path) -> None:
    capture = _run(tmp_path)
    base_replay = tmp_path / "first_domain" / "certified_domain_runtime_integration"

    assert capture["base_domain_runtime_version"] == "AIGOL_DOMAIN_RUNTIME_V1"
    assert (base_replay / "000_domain_created.json").exists()
    assert (base_replay / "001_domain_validated.json").exists()
    assert (base_replay / "002_domain_activated.json").exists()


def test_first_governed_domain_persists_required_replay_events(tmp_path) -> None:
    _run(tmp_path)
    expected = [
        ("000_domain_created.json", DOMAIN_CREATED, CREATED),
        ("001_domain_validated.json", DOMAIN_VALIDATED, VALIDATED),
        ("002_domain_activated.json", DOMAIN_ACTIVATED, ACTIVE),
        ("003_domain_executed.json", DOMAIN_EXECUTED, EXECUTING),
        ("004_domain_suspended.json", DOMAIN_SUSPENDED, SUSPENDED),
        ("005_domain_retired.json", DOMAIN_RETIRED, RETIRED),
    ]

    for filename, event, state in expected:
        wrapper = json.loads((tmp_path / "first_domain" / filename).read_text(encoding="utf-8"))
        assert wrapper["event_type"] == event
        assert wrapper["artifact"]["lifecycle_state"] == state
        assert wrapper["artifact"]["lifecycle_event"] == event


def test_first_governed_domain_rejects_invalid_execution_input(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="decision_id is required"):
        _run(
            tmp_path,
            execution_input={
                "decision_type": "ENTERPRISE_AI_ACTION_REVIEW",
                "requested_action": "approve generated recommendation",
                "risk_signals": ["requires_human_review"],
            },
        )


def test_first_governed_domain_detects_execution_replay_hash_break(tmp_path) -> None:
    _run(tmp_path)
    path = tmp_path / "first_domain" / "003_domain_executed.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["execution_example"]["decision_result"] = "APPROVED"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_first_governed_domain_replay(tmp_path / "first_domain")


def test_first_governed_domain_detects_lineage_break(tmp_path) -> None:
    _run(tmp_path)
    path = tmp_path / "first_domain" / "004_domain_suspended.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    artifact = wrapper["artifact"]
    artifact["previous_lifecycle_state"] = ACTIVE
    artifact.pop("chain_hash")
    artifact["chain_hash"] = replay_hash(
        {
            "domain_id": artifact["domain_id"],
            "domain_replay_id": artifact["domain_replay_id"],
            "previous_artifact_hash": artifact["previous_artifact_hash"],
            "lifecycle_state": artifact["lifecycle_state"],
            "lifecycle_event": artifact["lifecycle_event"],
        }
    )
    artifact.pop("artifact_hash")
    artifact["artifact_hash"] = replay_hash(artifact)
    wrapper.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="lineage continuity mismatch"):
        reconstruct_first_governed_domain_replay(tmp_path / "first_domain")


def test_first_governed_domain_runtime_has_no_provider_worker_or_external_execution() -> None:
    import aigol.runtime.first_governed_domain_runtime as first_domain_runtime

    source = inspect.getsource(first_domain_runtime)

    assert "OpenAIProviderAdapter" not in source
    assert "run_provider_attachment(" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "start_execution(" not in source
    assert "external_execution_performed\": True" not in source
