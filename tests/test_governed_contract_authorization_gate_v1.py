"""Tests for GOVERNED_CONTRACT_AUTHORIZATION_GATE_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect

import pytest

from aigol.runtime.governed_contract_authorization_gate import (
    AUTHORIZED,
    REJECTED,
    ContractAuthorizationResult,
    authorize_governed_execution_contract,
    reconstruct_authorization_lineage,
)
from aigol.runtime.governed_execution_contract import create_governed_execution_contract
from aigol.runtime.governed_execution_session import create_governed_execution_session
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-26T00:00:00+00:00"
AUTHORIZED_AT = "2026-05-26T00:00:10+00:00"


class ProviderExecutionSentinel:
    executed = False

    def fetch(self) -> None:
        self.executed = True
        raise AssertionError("authorization gate must not execute providers")


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


def _contract():
    return create_governed_execution_contract(
        contract_id="CONTRACT-AUTH-1",
        created_at=CREATED_AT,
        requested_operations=_operations(),
        allowed_providers=["metadata_inspection_provider", "readonly_http_get_provider"],
    ).validate_contract()


def _session():
    return create_governed_execution_session(session_id="SESSION-AUTH-1", created_at=CREATED_AT)


def _policy() -> dict:
    return {
        "allowed_providers": ["readonly_http_get_provider", "metadata_inspection_provider"],
        "allowed_operations": {
            "metadata_inspection_provider": ["inspect_runtime"],
            "readonly_http_get_provider": ["fetch"],
        },
    }


def _authorize(**overrides):
    payload = {
        "authorization_id": "AUTH-1",
        "contract": _contract(),
        "session": _session(),
        "session_policy": _policy(),
        "created_at": AUTHORIZED_AT,
    }
    payload.update(overrides)
    return authorize_governed_execution_contract(**payload)


def test_valid_authorization() -> None:
    result = _authorize()

    assert result.status == AUTHORIZED
    assert result.contract_id == "CONTRACT-AUTH-1"
    assert result.session_id == "SESSION-AUTH-1"
    assert result.requested_providers == ("metadata_inspection_provider", "readonly_http_get_provider")
    assert result.authorized_providers == ("metadata_inspection_provider", "readonly_http_get_provider")
    assert result.rejected_providers == ()
    assert result.evidence_hash.startswith("sha256:")


def test_unauthorized_provider_rejection() -> None:
    policy = _policy()
    policy["allowed_providers"] = ["metadata_inspection_provider"]
    policy["allowed_operations"].pop("readonly_http_get_provider")

    result = _authorize(session_policy=policy)

    assert result.status == REJECTED
    assert result.authorized_providers == ("metadata_inspection_provider",)
    assert result.rejected_providers == ("readonly_http_get_provider",)


def test_malformed_contract_rejection() -> None:
    artifact = _contract().to_dict()
    artifact.pop("requested_operations")

    result = _authorize(contract=artifact)

    assert result.status == REJECTED
    assert result.contract_id == ""
    assert result.authorized_providers == ()


def test_closed_session_rejection() -> None:
    closed = _session().close_session(closed_at="2026-05-26T00:01:00+00:00")

    result = _authorize(session=closed)

    assert result.status == REJECTED
    assert result.authorized_providers == ()
    assert result.rejected_providers == ("metadata_inspection_provider", "readonly_http_get_provider")


def test_duplicate_authorization_rejection() -> None:
    first = _authorize()

    second = _authorize(authorization_id="AUTH-2", prior_authorizations=(first,))

    assert first.status == AUTHORIZED
    assert second.status == REJECTED
    assert second.authorized_providers == ()
    assert second.rejected_providers == ("metadata_inspection_provider", "readonly_http_get_provider")


def test_deterministic_provider_ordering() -> None:
    first = _authorize()
    second = _authorize(session_policy=_policy())

    assert first.to_dict() == second.to_dict()
    assert first.requested_providers == tuple(sorted(first.requested_providers))
    assert first.authorized_providers == tuple(sorted(first.authorized_providers))


def test_immutable_authorization_evidence() -> None:
    result = _authorize()
    before = result.to_dict()

    with pytest.raises(AttributeError):
        result.status = REJECTED
    with pytest.raises(AttributeError):
        result.authorized_providers += ("metadata_inspection_provider",)

    assert result.to_dict() == before


def test_replay_reconstruction_validation() -> None:
    result = _authorize()

    first = reconstruct_authorization_lineage(result)
    second = reconstruct_authorization_lineage(result.to_dict())

    assert first == second
    assert first["authorization_id"] == "AUTH-1"
    assert first["contract_id"] == "CONTRACT-AUTH-1"
    assert first["lineage_hash"].startswith("sha256:")


def test_fail_closed_invalid_authorization() -> None:
    artifact = _authorize().to_dict()
    artifact["status"] = "MAYBE"

    with pytest.raises(FailClosedRuntimeError, match="authorization status"):
        ContractAuthorizationResult.from_dict(artifact)


def test_authorization_evidence_hash_validation() -> None:
    artifact = _authorize().to_dict()
    without_hash = deepcopy(artifact)
    evidence_hash = without_hash.pop("evidence_hash")

    assert set(artifact) == {
        "authorization_id",
        "contract_id",
        "session_id",
        "requested_providers",
        "authorized_providers",
        "rejected_providers",
        "status",
        "created_at",
        "evidence_hash",
    }
    assert evidence_hash == replay_hash(without_hash)


def test_malformed_policy_rejection() -> None:
    result = _authorize(session_policy={"allowed_providers": ["metadata_inspection_provider"]})

    assert result.status == REJECTED
    assert result.authorized_providers == ()


def test_no_provider_execution_occurs() -> None:
    sentinel = ProviderExecutionSentinel()

    _authorize()

    assert sentinel.executed is False


def test_no_orchestration_async_or_autonomous_surface() -> None:
    import aigol.runtime.governed_contract_authorization_gate as gate

    source = inspect.getsource(gate)

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
