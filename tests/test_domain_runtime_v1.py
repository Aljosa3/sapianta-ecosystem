"""Tests for AIGOL_DOMAIN_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.domain_runtime import (
    ACTIVE,
    AIGOL_DOMAIN_RUNTIME_VERSION,
    CREATED,
    DOMAIN_ACTIVATED,
    DOMAIN_CREATED,
    DOMAIN_RETIRED,
    DOMAIN_SUSPENDED,
    DOMAIN_VALIDATED,
    RETIRED,
    SUSPENDED,
    VALIDATED,
    activate_domain,
    create_domain,
    reconstruct_domain_lifecycle_replay,
    retire_domain,
    suspend_domain,
    validate_domain,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-05T00:00:00+00:00"


def _create(tmp_path, **overrides) -> dict:
    args = {
        "domain_id": "TRADING",
        "display_name": "Trading",
        "domain_version": "1.0.0",
        "capabilities": ["READONLY_SIGNAL_REVIEW", "RISK_BOUNDARY_VALIDATION"],
        "governance_scope": "Product 1 bounded domain lifecycle governance",
        "governance_policy_refs": [
            "docs/governance/CONSTITUTIONAL_INVARIANTS.md",
            "docs/governance/GOVERNANCE_LINEAGE_MODEL.md",
        ],
        "actor_id": "AIGOL",
        "timestamp": CREATED_AT,
        "replay_reference": "REPLAY-DOMAIN-TRADING-CREATED",
        "replay_dir": tmp_path / "domain",
        "known_gaps": ["No broker/API execution authority."],
    }
    args.update(overrides)
    return create_domain(**args)


def _validate(tmp_path, domain_capture: dict) -> dict:
    return validate_domain(
        domain_artifact=domain_capture["domain_artifact"],
        actor_id="AIGOL",
        timestamp=CREATED_AT,
        replay_reference="REPLAY-DOMAIN-TRADING-VALIDATED",
        replay_dir=tmp_path / "domain",
    )


def _activate(tmp_path, domain_capture: dict) -> dict:
    return activate_domain(
        domain_artifact=domain_capture["domain_artifact"],
        actor_id="AIGOL",
        timestamp=CREATED_AT,
        replay_reference="REPLAY-DOMAIN-TRADING-ACTIVE",
        replay_dir=tmp_path / "domain",
    )


def _suspend(tmp_path, domain_capture: dict) -> dict:
    return suspend_domain(
        domain_artifact=domain_capture["domain_artifact"],
        actor_id="AIGOL",
        timestamp=CREATED_AT,
        replay_reference="REPLAY-DOMAIN-TRADING-SUSPENDED",
        replay_dir=tmp_path / "domain",
        reason="Operator suspended domain for lifecycle verification.",
    )


def _retire(tmp_path, domain_capture: dict) -> dict:
    return retire_domain(
        domain_artifact=domain_capture["domain_artifact"],
        actor_id="AIGOL",
        timestamp=CREATED_AT,
        replay_reference="REPLAY-DOMAIN-TRADING-RETIRED",
        replay_dir=tmp_path / "domain",
        reason="Operator retired domain after lifecycle verification.",
    )


def _full_lifecycle(tmp_path) -> dict:
    created = _create(tmp_path)
    validated = _validate(tmp_path, created)
    active = _activate(tmp_path, validated)
    suspended = _suspend(tmp_path, active)
    return _retire(tmp_path, suspended)


def test_domain_runtime_creates_validates_activates_suspends_and_retires(tmp_path) -> None:
    final_capture = _full_lifecycle(tmp_path)
    final_artifact = final_capture["domain_artifact"]
    reconstructed = reconstruct_domain_lifecycle_replay(tmp_path / "domain")

    assert final_artifact["runtime_version"] == AIGOL_DOMAIN_RUNTIME_VERSION
    assert final_artifact["lifecycle_state"] == RETIRED
    assert final_artifact["lifecycle_event"] == DOMAIN_RETIRED
    assert final_artifact["provider_invoked"] is False
    assert final_artifact["worker_invoked"] is False
    assert final_artifact["dispatch_requested"] is False
    assert final_artifact["execution_performed"] is False
    assert final_artifact["governance_mutated"] is False
    assert reconstructed["domain_id"] == "TRADING"
    assert reconstructed["lifecycle_state"] == RETIRED
    assert reconstructed["lifecycle_events"] == [
        DOMAIN_CREATED,
        DOMAIN_VALIDATED,
        DOMAIN_ACTIVATED,
        DOMAIN_SUSPENDED,
        DOMAIN_RETIRED,
    ]
    assert reconstructed["replay_artifact_count"] == 5
    assert reconstructed["certification_ready"] is True


def test_domain_runtime_persists_replay_events(tmp_path) -> None:
    _full_lifecycle(tmp_path)

    expected = [
        ("000_domain_created.json", DOMAIN_CREATED),
        ("001_domain_validated.json", DOMAIN_VALIDATED),
        ("002_domain_activated.json", DOMAIN_ACTIVATED),
        ("003_domain_suspended.json", DOMAIN_SUSPENDED),
        ("004_domain_retired.json", DOMAIN_RETIRED),
    ]
    for filename, event in expected:
        wrapper = json.loads((tmp_path / "domain" / filename).read_text(encoding="utf-8"))
        assert wrapper["event_type"] == event
        assert wrapper["artifact"]["lifecycle_event"] == event


def test_domain_runtime_rejects_activation_before_validation(tmp_path) -> None:
    created = _create(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="unauthorized lifecycle transition"):
        _activate(tmp_path, created)


def test_domain_runtime_rejects_duplicate_capability_declaration(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="duplicate capability declaration"):
        _create(tmp_path, capabilities=["READONLY_SIGNAL_REVIEW", "READONLY_SIGNAL_REVIEW"])


def test_domain_runtime_rejects_missing_governance_binding(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="governance_policy_refs are required"):
        _create(tmp_path, governance_policy_refs=[])


def test_domain_runtime_detects_replay_hash_break(tmp_path) -> None:
    _full_lifecycle(tmp_path)
    path = tmp_path / "domain" / "002_domain_activated.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["lifecycle_state"] = SUSPENDED
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_domain_lifecycle_replay(tmp_path / "domain")


def test_domain_runtime_detects_lineage_break(tmp_path) -> None:
    _full_lifecycle(tmp_path)
    path = tmp_path / "domain" / "003_domain_suspended.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["previous_lifecycle_state"] = CREATED
    artifact = wrapper["artifact"]
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
        reconstruct_domain_lifecycle_replay(tmp_path / "domain")


def test_domain_runtime_reconstructs_state_sequence(tmp_path) -> None:
    created = _create(tmp_path)
    validated = _validate(tmp_path, created)
    active = _activate(tmp_path, validated)
    suspended = _suspend(tmp_path, active)
    retired = _retire(tmp_path, suspended)

    assert created["domain_lifecycle_state"] == CREATED
    assert validated["domain_lifecycle_state"] == VALIDATED
    assert active["domain_lifecycle_state"] == ACTIVE
    assert suspended["domain_lifecycle_state"] == SUSPENDED
    assert retired["domain_lifecycle_state"] == RETIRED
    assert created["domain_replay_id"] == retired["domain_replay_id"]


def test_domain_runtime_has_no_provider_worker_dispatch_or_execution_authority() -> None:
    import aigol.runtime.domain_runtime as domain_runtime

    source = inspect.getsource(domain_runtime)

    assert "OpenAIProviderAdapter" not in source
    assert "run_provider_attachment(" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source
