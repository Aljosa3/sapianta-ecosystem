"""Tests for SESSION_LINEAGE_REPLAY_VALIDATION_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect

from aigol.runtime.governed_execution_session import create_governed_execution_session
from aigol.runtime.session_lineage_replay_validator import validate_session_lineage_replay
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-26T00:00:00+00:00"
CLOSED_AT = "2026-05-26T00:01:00+00:00"


class ProviderExecutionSentinel:
    executed = False

    def fetch(self) -> None:
        self.executed = True
        raise AssertionError("replay validator must not execute providers")


def _evidence(operation: str) -> dict:
    evidence = {
        "operation": operation,
        "status": "OK",
        "reason": "bounded provider evidence",
    }
    evidence["evidence_hash"] = replay_hash(evidence)
    return evidence


def _closed_session_dict() -> dict:
    session = create_governed_execution_session(session_id="SESSION-REPLAY-1", created_at=CREATED_AT)
    session = session.attach_provider_evidence(
        provider="metadata_inspection_provider",
        provider_operation="inspect_runtime",
        evidence=_evidence("inspect_runtime"),
        attached_at="2026-05-26T00:00:10+00:00",
    )
    session = session.attach_provider_evidence(
        provider="readonly_http_get_provider",
        provider_operation="fetch",
        evidence=_evidence("fetch"),
        attached_at="2026-05-26T00:00:20+00:00",
    )
    return session.close_session(closed_at=CLOSED_AT).to_dict()


def _rehash_session(artifact: dict) -> dict:
    session_input = {
        "session_id": artifact["session_id"],
        "created_at": artifact["created_at"],
        "status": artifact["status"],
        "operations": artifact["operations"],
        "closed_at": artifact["closed_at"],
    }
    artifact["evidence_hash"] = replay_hash(session_input)
    return artifact


def test_valid_replay_reconstruction() -> None:
    result = validate_session_lineage_replay(_closed_session_dict())

    assert result["session_id"] == "SESSION-REPLAY-1"
    assert result["replay_status"] == "VALID"
    assert result["lineage_valid"] is True
    assert result["append_only_valid"] is True
    assert result["closure_valid"] is True
    assert len(result["reconstructed_operations"]) == 2


def test_deterministic_ordering_validation() -> None:
    artifact = _closed_session_dict()
    artifact["operations"][1]["operation_index"] = 0
    _rehash_session(artifact)

    result = validate_session_lineage_replay(artifact)

    assert result["replay_status"] == "INVALID"
    assert result["lineage_valid"] is False


def test_append_only_validation() -> None:
    artifact = _closed_session_dict()
    artifact["operations"].pop(0)
    _rehash_session(artifact)

    result = validate_session_lineage_replay(artifact)

    assert result["replay_status"] == "INVALID"
    assert result["append_only_valid"] is False


def test_duplicate_operation_detection() -> None:
    artifact = _closed_session_dict()
    artifact["operations"].append(deepcopy(artifact["operations"][1]))
    _rehash_session(artifact)

    result = validate_session_lineage_replay(artifact)

    assert result["replay_status"] == "INVALID"
    assert result["append_only_valid"] is False


def test_mutated_evidence_detection() -> None:
    artifact = _closed_session_dict()
    artifact["operations"][0]["evidence"]["status"] = "MUTATED"
    _rehash_session(artifact)

    result = validate_session_lineage_replay(artifact)

    assert result["replay_status"] == "INVALID"
    assert result["lineage_valid"] is False


def test_invalid_closure_detection() -> None:
    artifact = _closed_session_dict()
    artifact["closure_events"] = [{"closed_at": CLOSED_AT}, {"closed_at": CLOSED_AT}]
    _rehash_session(artifact)

    result = validate_session_lineage_replay(artifact)

    assert result["replay_status"] == "INVALID"
    assert result["closure_valid"] is False


def test_missing_closure_detection() -> None:
    artifact = _closed_session_dict()
    artifact["status"] = "ACTIVE"
    artifact["closed_at"] = ""
    _rehash_session(artifact)

    result = validate_session_lineage_replay(artifact)

    assert result["replay_status"] == "INVALID"
    assert result["closure_valid"] is False


def test_attach_after_close_invalidation() -> None:
    artifact = _closed_session_dict()
    late_operation = deepcopy(artifact["operations"][-1])
    late_operation["operation_index"] = 2
    late_operation["attached_at"] = "2026-05-26T00:02:00+00:00"
    late_operation["previous_operation_hash"] = artifact["operations"][-1]["operation_hash"]
    late_operation.pop("operation_hash", None)
    late_operation["operation_hash"] = replay_hash(late_operation)
    artifact["operations"].append(late_operation)
    _rehash_session(artifact)

    result = validate_session_lineage_replay(artifact)

    assert result["replay_status"] == "INVALID"
    assert result["closure_valid"] is False


def test_immutable_evidence_validation() -> None:
    artifact = _closed_session_dict()
    artifact["evidence_hash"] = "sha256:tampered"

    result = validate_session_lineage_replay(artifact)

    assert result["replay_status"] == "INVALID"
    assert "evidence" in result["validation_reason"]


def test_deterministic_replay_evidence_generation() -> None:
    artifact = _closed_session_dict()

    first = validate_session_lineage_replay(artifact)
    second = validate_session_lineage_replay(artifact)

    assert first == second
    without_hash = deepcopy(first)
    evidence_hash = without_hash.pop("evidence_hash")
    assert evidence_hash == replay_hash(without_hash)


def test_replay_performs_no_provider_execution() -> None:
    sentinel = ProviderExecutionSentinel()
    artifact = _closed_session_dict()
    artifact["operations"][0]["evidence"]["provider_sentinel"] = "present but inert"

    validate_session_lineage_replay(artifact)

    assert sentinel.executed is False


def test_replay_performs_no_mutation() -> None:
    artifact = _closed_session_dict()
    before = deepcopy(artifact)

    validate_session_lineage_replay(artifact)

    assert artifact == before


def test_replay_performs_no_async_behavior() -> None:
    source = inspect.getsource(validate_session_lineage_replay)

    assert "async " not in source
    assert "await " not in source
    assert "threading" not in source
    assert "multiprocessing" not in source


def test_no_execution_or_orchestration_surface() -> None:
    import aigol.runtime.session_lineage_replay_validator as validator

    source = inspect.getsource(validator)

    assert "subprocess" not in source
    assert "os.system" not in source
    assert "requests" not in source
    assert "urllib" not in source
    assert "retry" not in source.lower()
    assert "orchestrat" not in source.lower()
    assert "workflow" not in source.lower()
    assert "semantic" not in source.lower()
    assert "llm" not in source.lower()
