from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from runtime.governance.capability_models import CapabilityDecision
from runtime.governance.capability_registry import (
    LOCALHOST_PREVIEW_RUNTIME_V1,
    evaluate_capability_request,
    get_capability_registry,
)


def valid_request():
    scope = LOCALHOST_PREVIEW_RUNTIME_V1.allowed_scope
    return {
        "capability_id": LOCALHOST_PREVIEW_RUNTIME_V1.capability_id,
        "host": scope.host,
        "port": scope.port,
        "runtime": scope.runtime,
        "lifecycle": scope.lifecycle,
        "temporary": scope.temporary,
        "visual_validation": scope.visual_validation,
    }


def test_localhost_preview_capability_is_registered() -> None:
    registry = get_capability_registry()

    assert "LOCALHOST_PREVIEW_RUNTIME_V1" in registry
    capability = registry["LOCALHOST_PREVIEW_RUNTIME_V1"]
    assert capability["allowed_scope"]["host"] == "127.0.0.1"
    assert capability["allowed_scope"]["runtime"] == "uvicorn"
    assert capability["allowed_scope"]["lifecycle"] == ["start", "validate", "stop"]


def test_matching_localhost_preview_scope_is_approved() -> None:
    evaluation = evaluate_capability_request(**valid_request())

    assert evaluation.decision is CapabilityDecision.APPROVED
    assert evaluation.scope_locked is True
    assert evaluation.replay_visible is True
    assert evaluation.escalation_required is False


def test_host_change_requires_escalation() -> None:
    request = valid_request()
    request["host"] = "0.0.0.0"

    evaluation = evaluate_capability_request(**request)

    assert evaluation.decision is CapabilityDecision.ESCALATED
    assert "host change" in evaluation.reason
    assert evaluation.escalation_required is True


def test_port_change_requires_escalation() -> None:
    request = valid_request()
    request["port"] = request["port"] + 1

    evaluation = evaluate_capability_request(**request)

    assert evaluation.decision is CapabilityDecision.ESCALATED
    assert "port change" in evaluation.reason


def test_deployment_semantics_require_escalation() -> None:
    evaluation = evaluate_capability_request(**valid_request(), deployment=True)

    assert evaluation.decision is CapabilityDecision.ESCALATED
    assert "deployment" in evaluation.reason


def test_revoked_capability_is_rejected() -> None:
    evaluation = evaluate_capability_request(**valid_request(), revoked=True)

    assert evaluation.decision is CapabilityDecision.REJECTED
    assert evaluation.reason == "capability revoked"


def test_evaluation_hash_is_replay_stable() -> None:
    first = evaluate_capability_request(**valid_request())
    second = evaluate_capability_request(**valid_request())

    assert first.deterministic_hash == second.deterministic_hash
    assert first.to_dict() == second.to_dict()

