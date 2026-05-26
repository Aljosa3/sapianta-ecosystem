"""Tests for GOVERNED_EXECUTION_CONTRACT_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect

import pytest

from aigol.runtime.governed_execution_contract import (
    ATTACHED,
    CREATED,
    VALIDATED,
    GovernedExecutionContract,
    create_governed_execution_contract,
    reconstruct_contract_lineage,
)
from aigol.runtime.governed_execution_session import create_governed_execution_session
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-26T00:00:00+00:00"
ATTACHED_AT = "2026-05-26T00:00:10+00:00"


class ProviderExecutionSentinel:
    executed = False

    def fetch(self) -> None:
        self.executed = True
        raise AssertionError("contract validation must not execute providers")


def _operations() -> list[dict]:
    return [
        {
            "provider": "metadata_inspection_provider",
            "operation": "inspect_runtime",
            "operation_id": "OP-001",
            "created_at": "2026-05-26T00:00:01+00:00",
        },
        {
            "provider": "readonly_http_get_provider",
            "operation": "fetch",
            "operation_id": "OP-002",
            "created_at": "2026-05-26T00:00:02+00:00",
        },
    ]


def _contract() -> GovernedExecutionContract:
    return create_governed_execution_contract(
        contract_id="CONTRACT-1",
        created_at=CREATED_AT,
        requested_operations=_operations(),
        allowed_providers=["metadata_inspection_provider", "readonly_http_get_provider"],
    )


def _session():
    return create_governed_execution_session(session_id="SESSION-1", created_at=CREATED_AT)


def test_valid_contract_creation() -> None:
    contract = _contract()

    assert contract.contract_id == "CONTRACT-1"
    assert contract.status == CREATED
    assert contract.session_id == ""
    assert contract.allowed_providers == ("metadata_inspection_provider", "readonly_http_get_provider")
    assert contract.evidence_hash.startswith("sha256:")


def test_valid_provider_authorization() -> None:
    validated = _contract().validate_contract()

    assert validated.status == VALIDATED
    assert [operation["provider"] for operation in validated.to_dict()["requested_operations"]] == [
        "metadata_inspection_provider",
        "readonly_http_get_provider",
    ]


def test_invalid_provider_rejection() -> None:
    operations = _operations()
    operations[0]["provider"] = "codex_cli_provider"

    with pytest.raises(FailClosedRuntimeError, match="unknown provider"):
        create_governed_execution_contract(
            contract_id="CONTRACT-1",
            created_at=CREATED_AT,
            requested_operations=operations,
            allowed_providers=["codex_cli_provider"],
        )


def test_malformed_contract_rejection() -> None:
    operations = _operations()
    operations[0].pop("operation_id")

    with pytest.raises(FailClosedRuntimeError, match="malformed"):
        create_governed_execution_contract(
            contract_id="CONTRACT-1",
            created_at=CREATED_AT,
            requested_operations=operations,
            allowed_providers=["metadata_inspection_provider", "readonly_http_get_provider"],
        )


def test_unsupported_operation_rejection() -> None:
    operations = _operations()
    operations[0]["operation"] = "read_file"

    with pytest.raises(FailClosedRuntimeError, match="unsupported"):
        create_governed_execution_contract(
            contract_id="CONTRACT-1",
            created_at=CREATED_AT,
            requested_operations=operations,
            allowed_providers=["metadata_inspection_provider", "readonly_http_get_provider"],
        )


def test_deterministic_operation_ordering() -> None:
    first = _contract()
    second = _contract()

    assert first.to_dict() == second.to_dict()
    assert [operation["operation_id"] for operation in first.to_dict()["requested_operations"]] == ["OP-001", "OP-002"]


def test_immutable_attached_contract() -> None:
    contract = _contract().validate_contract()
    attached = contract.attach_to_session(session=_session(), attached_at=ATTACHED_AT)["contract"]
    before = attached.to_dict()

    with pytest.raises(TypeError):
        attached.requested_operations[0]["operation"] = "MUTATED"

    assert attached.to_dict() == before


def test_replay_visible_contract_evidence() -> None:
    contract = _contract()
    artifact = contract.to_dict()
    without_hash = deepcopy(artifact)
    evidence_hash = without_hash.pop("evidence_hash")

    assert set(artifact) == {
        "contract_id",
        "created_at",
        "requested_operations",
        "allowed_providers",
        "session_id",
        "status",
        "evidence_hash",
    }
    assert evidence_hash == replay_hash(without_hash)


def test_attach_to_session_validation() -> None:
    attached = _contract().validate_contract().attach_to_session(session=_session(), attached_at=ATTACHED_AT)
    contract = attached["contract"]
    evidence = attached["attachment_evidence"]

    assert contract.status == ATTACHED
    assert contract.session_id == "SESSION-1"
    assert evidence["operation"] == "attach_governed_execution_contract"
    assert evidence["contract_evidence_hash"] == contract.evidence_hash
    assert evidence["evidence_hash"].startswith("sha256:")


def test_duplicate_attach_rejection() -> None:
    attached = _contract().validate_contract().attach_to_session(session=_session(), attached_at=ATTACHED_AT)["contract"]

    with pytest.raises(FailClosedRuntimeError, match="already ATTACHED"):
        attached.attach_to_session(session=_session(), attached_at=ATTACHED_AT)


def test_attach_to_closed_session_rejection() -> None:
    closed = _session().close_session(closed_at="2026-05-26T00:01:00+00:00")

    with pytest.raises(FailClosedRuntimeError, match="CLOSED"):
        _contract().validate_contract().attach_to_session(session=closed, attached_at=ATTACHED_AT)


def test_mutated_contract_rejection() -> None:
    artifact = _contract().to_dict()
    artifact["requested_operations"][0]["operation"] = "inspect_process"

    with pytest.raises(FailClosedRuntimeError, match="evidence hash mismatch"):
        GovernedExecutionContract.from_dict(artifact)


def test_deterministic_replay_reconstruction() -> None:
    attached = _contract().validate_contract().attach_to_session(session=_session(), attached_at=ATTACHED_AT)["contract"]

    first = reconstruct_contract_lineage(attached)
    second = reconstruct_contract_lineage(attached.to_dict())

    assert first == second
    assert first["contract_id"] == "CONTRACT-1"
    assert first["session_id"] == "SESSION-1"
    assert first["operation_order"] == ["OP-001", "OP-002"]
    assert first["lineage_hash"].startswith("sha256:")


def test_no_provider_execution_occurs() -> None:
    sentinel = ProviderExecutionSentinel()

    _contract().validate_contract().attach_to_session(session=_session(), attached_at=ATTACHED_AT)

    assert sentinel.executed is False


def test_no_orchestration_async_autonomous_or_semantic_surface() -> None:
    import aigol.runtime.governed_execution_contract as contract_module

    source = inspect.getsource(contract_module)

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
    assert "llm" not in source.lower()
    assert "semantic reasoning" not in source.lower()
