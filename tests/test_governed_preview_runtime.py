from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from runtime.governance.preview_runtime import (
    PREVIEW_COMMAND,
    PREVIEW_LIFECYCLE,
    PRIMITIVE_ID,
    PreviewRuntimeRequest,
    build_preview_command,
    describe_preview_lifecycle,
    validate_preview_request,
)


def test_valid_localhost_preview_request_is_accepted() -> None:
    result = validate_preview_request(PreviewRuntimeRequest())

    assert result.approved is True
    assert result.escalation_required is False
    assert result.rejected is False
    assert result.command == PREVIEW_COMMAND
    assert result.server_started is False


def test_host_zero_zero_zero_zero_escalates() -> None:
    result = validate_preview_request(PreviewRuntimeRequest(host="0.0.0.0"))

    assert result.approved is False
    assert result.escalation_required is True
    assert result.command == ()
    assert "public_binding_forbidden" in result.forbidden_boundary_checks


def test_different_port_escalates() -> None:
    result = validate_preview_request(PreviewRuntimeRequest(port=8011))

    assert result.approved is False
    assert result.escalation_required is True
    assert "port change" in result.reason


def test_persistent_runtime_escalates() -> None:
    result = validate_preview_request(PreviewRuntimeRequest(persistent=True))

    assert result.approved is False
    assert result.escalation_required is True
    assert "daemon_persistence_forbidden" in result.forbidden_boundary_checks


def test_deployment_semantics_escalate() -> None:
    result = validate_preview_request(PreviewRuntimeRequest(deployment=True))

    assert result.approved is False
    assert result.escalation_required is True
    assert "deployment_forbidden" in result.forbidden_boundary_checks


def test_command_generation_is_deterministic() -> None:
    first = build_preview_command(PreviewRuntimeRequest())
    second = build_preview_command(PreviewRuntimeRequest())

    assert first == second == PREVIEW_COMMAND
    assert " ".join(first) == (
        "uvicorn sapianta_system.sapianta_product.main:app --host 127.0.0.1 --port 8010"
    )


def test_lifecycle_must_be_start_validate_stop() -> None:
    result = validate_preview_request(PreviewRuntimeRequest(lifecycle=("start", "stop")))

    assert result.approved is False
    assert result.escalation_required is True
    assert result.command == ()


def test_lifecycle_description_is_bounded_and_non_executing() -> None:
    description = describe_preview_lifecycle()

    assert description["lifecycle"] == list(PREVIEW_LIFECYCLE)
    assert description["server_started_by_helper"] is False


def test_result_hash_is_stable() -> None:
    first = validate_preview_request(PreviewRuntimeRequest())
    second = validate_preview_request(PreviewRuntimeRequest())

    assert first.deterministic_hash == second.deterministic_hash
    assert first.to_dict() == second.to_dict()


def test_replay_lineage_fields_are_present_and_stable() -> None:
    result = validate_preview_request(PreviewRuntimeRequest())
    repeated = validate_preview_request(PreviewRuntimeRequest())
    description = describe_preview_lifecycle()

    assert result.primitive_id == PRIMITIVE_ID
    assert result.request_hash == repeated.request_hash
    assert result.command_hash == repeated.command_hash
    assert result.scope_hash == repeated.scope_hash
    assert result.scope_hash == description["scope_hash"]
    assert "runtime/governance/preview_runtime.py" in result.replay_lineage
    assert "runtime/governance/capability_registry.py" in result.replay_lineage
