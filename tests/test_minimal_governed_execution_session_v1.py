"""Tests for MINIMAL_GOVERNED_EXECUTION_SESSION_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect

import pytest

from aigol.runtime.governed_execution_session import (
    ACTIVE,
    CLOSED,
    CREATED,
    GovernedExecutionSession,
    create_governed_execution_session,
    reconstruct_session_lineage,
)
from aigol.runtime.models import FailClosedRuntimeError


CREATED_AT = "2026-05-26T00:00:00+00:00"
CLOSED_AT = "2026-05-26T00:01:00+00:00"


def _evidence(operation: str) -> dict:
    return {
        "operation": operation,
        "status": "OK",
        "reason": "bounded provider evidence",
        "evidence_hash": f"sha256:{operation}",
    }


def _session() -> GovernedExecutionSession:
    return create_governed_execution_session(session_id="SESSION-1", created_at=CREATED_AT)


def test_session_creation() -> None:
    session = _session()

    assert session.session_id == "SESSION-1"
    assert session.created_at == CREATED_AT
    assert session.status == CREATED
    assert session.operations == ()
    assert session.closed_at == ""
    assert session.evidence_hash.startswith("sha256:")


def test_operation_attachment() -> None:
    session = _session().attach_provider_evidence(
        provider="metadata_inspection_provider",
        provider_operation="inspect_runtime",
        evidence=_evidence("inspect_runtime"),
        attached_at="2026-05-26T00:00:10+00:00",
    )

    operation = session.to_dict()["operations"][0]
    assert session.status == ACTIVE
    assert operation["operation_index"] == 0
    assert operation["provider"] == "metadata_inspection_provider"
    assert operation["provider_operation"] == "inspect_runtime"
    assert operation["previous_operation_hash"] == ""
    assert operation["operation_hash"].startswith("sha256:")


def test_deterministic_operation_ordering() -> None:
    session = _session()
    session = session.attach_provider_evidence(
        provider="readonly_filesystem_provider",
        provider_operation="inspect_metadata",
        evidence=_evidence("inspect_metadata"),
        attached_at="2026-05-26T00:00:10+00:00",
    )
    session = session.attach_provider_evidence(
        provider="readonly_http_get_provider",
        provider_operation="fetch",
        evidence=_evidence("fetch"),
        attached_at="2026-05-26T00:00:20+00:00",
    )

    operations = session.to_dict()["operations"]
    assert [operation["operation_index"] for operation in operations] == [0, 1]
    assert operations[1]["previous_operation_hash"] == operations[0]["operation_hash"]


def test_replay_lineage_reconstruction() -> None:
    session = _session().attach_provider_evidence(
        provider="metadata_inspection_provider",
        provider_operation="inspect_process",
        evidence=_evidence("inspect_process"),
        attached_at="2026-05-26T00:00:10+00:00",
    )
    closed = session.close_session(closed_at=CLOSED_AT)

    lineage = reconstruct_session_lineage(closed)

    assert lineage["session_id"] == "SESSION-1"
    assert lineage["status"] == CLOSED
    assert lineage["operation_count"] == 1
    assert lineage["closed_at"] == CLOSED_AT
    assert lineage["operation_hash_chain"] == [closed.to_dict()["operations"][0]["operation_hash"]]
    assert lineage["replay_valid"] is True


def test_invalid_transition_rejection() -> None:
    failed = GovernedExecutionSession(session_id="SESSION-1", created_at=CREATED_AT, status="FAILED")

    with pytest.raises(FailClosedRuntimeError, match="FAILED"):
        failed.attach_provider_evidence(
            provider="metadata_inspection_provider",
            provider_operation="inspect_runtime",
            evidence=_evidence("inspect_runtime"),
            attached_at="2026-05-26T00:00:10+00:00",
        )
    with pytest.raises(FailClosedRuntimeError, match="FAILED"):
        failed.close_session(closed_at=CLOSED_AT)


def test_duplicate_closure_rejection() -> None:
    closed = _session().close_session(closed_at=CLOSED_AT)

    with pytest.raises(FailClosedRuntimeError, match="already CLOSED"):
        closed.close_session(closed_at=CLOSED_AT)


def test_attach_after_close_rejection() -> None:
    closed = _session().close_session(closed_at=CLOSED_AT)

    with pytest.raises(FailClosedRuntimeError, match="after CLOSED"):
        closed.attach_provider_evidence(
            provider="metadata_inspection_provider",
            provider_operation="inspect_environment",
            evidence=_evidence("inspect_environment"),
            attached_at="2026-05-26T00:00:10+00:00",
        )


def test_fail_closed_invalid_states() -> None:
    with pytest.raises(FailClosedRuntimeError, match="session status"):
        GovernedExecutionSession(session_id="SESSION-1", created_at=CREATED_AT, status="RUNNING")
    with pytest.raises(FailClosedRuntimeError, match="closed_at"):
        GovernedExecutionSession(session_id="SESSION-1", created_at=CREATED_AT, status=CLOSED)
    with pytest.raises(FailClosedRuntimeError, match="closed_at"):
        GovernedExecutionSession(session_id="SESSION-1", created_at=CREATED_AT, status=CREATED, closed_at=CLOSED_AT)


def test_operation_evidence_immutable_after_attach() -> None:
    evidence = _evidence("inspect_runtime")
    session = _session().attach_provider_evidence(
        provider="metadata_inspection_provider",
        provider_operation="inspect_runtime",
        evidence=evidence,
        attached_at="2026-05-26T00:00:10+00:00",
    )
    before = deepcopy(session.to_dict())

    evidence["status"] = "MUTATED"
    with pytest.raises(TypeError):
        session.operations[0]["evidence"]["status"] = "MUTATED"

    assert session.to_dict() == before


def test_disallowed_provider_fails_closed() -> None:
    with pytest.raises(FailClosedRuntimeError, match="provider is not allowed"):
        _session().attach_provider_evidence(
            provider="codex_cli_provider",
            provider_operation="execute",
            evidence=_evidence("execute"),
            attached_at="2026-05-26T00:00:10+00:00",
        )


def test_disallowed_provider_operation_fails_closed() -> None:
    with pytest.raises(FailClosedRuntimeError, match="provider_operation is not allowed"):
        _session().attach_provider_evidence(
            provider="metadata_inspection_provider",
            provider_operation="read_file",
            evidence=_evidence("read_file"),
            attached_at="2026-05-26T00:00:10+00:00",
        )


def test_no_orchestration_autonomous_async_or_concurrent_surface() -> None:
    public_methods = {
        name
        for name, value in inspect.getmembers(GovernedExecutionSession, predicate=inspect.isfunction)
        if not name.startswith("_")
    }
    source = inspect.getsource(GovernedExecutionSession)

    assert public_methods == {"attach_provider_evidence", "close_session", "to_dict"}
    assert "retry" not in source.lower()
    assert "orchestrat" not in source.lower()
    assert "autonomous" not in source.lower()
    assert "async " not in source
    assert "threading" not in source
    assert "multiprocessing" not in source
    assert "schedule" not in source.lower()
    assert "delegate" not in source.lower()
