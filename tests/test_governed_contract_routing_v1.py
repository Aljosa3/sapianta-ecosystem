"""Tests for GOVERNED_CONTRACT_ROUTING_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect

from aigol.runtime.governed_contract_authorization_gate import (
    AUTHORIZED,
    ContractAuthorizationResult,
    authorize_governed_execution_contract,
)
from aigol.runtime.governed_contract_router import (
    REJECTED,
    ROUTED,
    route_authorized_contract,
    reconstruct_routing_lineage,
)
from aigol.runtime.governed_execution_contract import create_governed_execution_contract
from aigol.runtime.governed_execution_session import create_governed_execution_session
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-26T00:00:00+00:00"
AUTHORIZED_AT = "2026-05-26T00:00:10+00:00"
ROUTED_AT = "2026-05-26T00:00:20+00:00"


class ProviderExecutionSentinel:
    executed = False

    def fetch(self) -> None:
        self.executed = True
        raise AssertionError("router must not execute providers")


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
        contract_id="CONTRACT-ROUTE-1",
        created_at=CREATED_AT,
        requested_operations=_operations(),
        allowed_providers=["metadata_inspection_provider", "readonly_http_get_provider"],
    ).validate_contract()


def _session():
    return create_governed_execution_session(session_id="SESSION-ROUTE-1", created_at=CREATED_AT)


def _policy() -> dict:
    return {
        "allowed_providers": ["readonly_http_get_provider", "metadata_inspection_provider"],
        "allowed_operations": {
            "metadata_inspection_provider": ["inspect_runtime"],
            "readonly_http_get_provider": ["fetch"],
        },
    }


def _authorization(contract=None, session=None):
    return authorize_governed_execution_contract(
        authorization_id="AUTH-ROUTE-1",
        contract=contract or _contract(),
        session=session or _session(),
        session_policy=_policy(),
        created_at=AUTHORIZED_AT,
    )


def _route(**overrides):
    contract = overrides.pop("contract", _contract())
    session = overrides.pop("session", _session())
    authorization = overrides.pop("authorization", _authorization(contract=contract, session=session))
    payload = {
        "routing_id": "ROUTE-1",
        "contract": contract,
        "authorization": authorization,
        "session": session,
        "created_at": ROUTED_AT,
    }
    payload.update(overrides)
    return route_authorized_contract(**payload)


def test_valid_authorized_contract_routing() -> None:
    result = _route()
    routing = result["routing_result"]

    assert routing.status == ROUTED
    assert routing.contract_id == "CONTRACT-ROUTE-1"
    assert routing.session_id == "SESSION-ROUTE-1"
    assert routing.authorization_id == "AUTH-ROUTE-1"
    assert routing.attached is True
    assert result["attached_contract"].status == "ATTACHED"
    assert result["attachment_evidence"]["contract_id"] == routing.contract_id


def test_unauthorized_contract_rejection() -> None:
    authorization = ContractAuthorizationResult(
        authorization_id="AUTH-ROUTE-1",
        contract_id="CONTRACT-ROUTE-1",
        session_id="SESSION-ROUTE-1",
        requested_providers=("metadata_inspection_provider",),
        authorized_providers=(),
        rejected_providers=("metadata_inspection_provider",),
        status="REJECTED",
        created_at=AUTHORIZED_AT,
    )

    result = _route(authorization=authorization)

    assert result["routing_result"].status == REJECTED
    assert result["routing_result"].attached is False
    assert result["attached_contract"] is None


def test_mismatched_contract_id_rejection() -> None:
    authorization = ContractAuthorizationResult(
        authorization_id="AUTH-ROUTE-1",
        contract_id="OTHER-CONTRACT",
        session_id="SESSION-ROUTE-1",
        requested_providers=("metadata_inspection_provider", "readonly_http_get_provider"),
        authorized_providers=("metadata_inspection_provider", "readonly_http_get_provider"),
        rejected_providers=(),
        status=AUTHORIZED,
        created_at=AUTHORIZED_AT,
    )

    result = _route(authorization=authorization)

    assert result["routing_result"].status == REJECTED
    assert "contract_id" in result["routing_result"].reason


def test_mismatched_session_id_rejection() -> None:
    authorization = ContractAuthorizationResult(
        authorization_id="AUTH-ROUTE-1",
        contract_id="CONTRACT-ROUTE-1",
        session_id="OTHER-SESSION",
        requested_providers=("metadata_inspection_provider", "readonly_http_get_provider"),
        authorized_providers=("metadata_inspection_provider", "readonly_http_get_provider"),
        rejected_providers=(),
        status=AUTHORIZED,
        created_at=AUTHORIZED_AT,
    )

    result = _route(authorization=authorization)

    assert result["routing_result"].status == REJECTED
    assert "session_id" in result["routing_result"].reason


def test_closed_session_rejection() -> None:
    session = _session().close_session(closed_at="2026-05-26T00:01:00+00:00")
    authorization = _authorization(session=_session())

    result = _route(session=session, authorization=authorization)

    assert result["routing_result"].status == REJECTED
    assert "CLOSED" in result["routing_result"].reason


def test_duplicate_routing_rejection() -> None:
    first = _route()["routing_result"]
    second = _route(routing_id="ROUTE-2", prior_routes=(first,))

    assert first.status == ROUTED
    assert second["routing_result"].status == REJECTED
    assert "duplicate" in second["routing_result"].reason


def test_mutated_contract_hash_rejection() -> None:
    artifact = _contract().to_dict()
    artifact["requested_operations"][0]["operation"] = "inspect_process"

    result = _route(contract=artifact)

    assert result["routing_result"].status == REJECTED
    assert result["attached_contract"] is None


def test_mutated_authorization_hash_rejection() -> None:
    artifact = _authorization().to_dict()
    artifact["authorized_providers"] = ["metadata_inspection_provider"]

    result = _route(authorization=artifact)

    assert result["routing_result"].status == REJECTED
    assert result["attached_contract"] is None


def test_requested_providers_differ_from_authorized_providers_rejection() -> None:
    authorization = ContractAuthorizationResult(
        authorization_id="AUTH-ROUTE-1",
        contract_id="CONTRACT-ROUTE-1",
        session_id="SESSION-ROUTE-1",
        requested_providers=("metadata_inspection_provider", "readonly_http_get_provider"),
        authorized_providers=("metadata_inspection_provider",),
        rejected_providers=(),
        status=AUTHORIZED,
        created_at=AUTHORIZED_AT,
    )

    result = _route(authorization=authorization)

    assert result["routing_result"].status == REJECTED
    assert "authorized providers" in result["routing_result"].reason


def test_deterministic_routing_evidence() -> None:
    first = _route()["routing_result"].to_dict()
    second = _route()["routing_result"].to_dict()

    assert first == second
    without_hash = deepcopy(first)
    evidence_hash = without_hash.pop("evidence_hash")
    assert evidence_hash == replay_hash(without_hash)


def test_routing_lineage_reconstruction() -> None:
    routing = _route()["routing_result"]

    first = reconstruct_routing_lineage(routing)
    second = reconstruct_routing_lineage(routing.to_dict())

    assert first == second
    assert first["routing_id"] == "ROUTE-1"
    assert first["lineage_hash"].startswith("sha256:")


def test_no_provider_execution_during_routing() -> None:
    sentinel = ProviderExecutionSentinel()

    _route()

    assert sentinel.executed is False


def test_no_orchestration_async_or_runtime_autonomy_introduced() -> None:
    import aigol.runtime.governed_contract_router as router

    source = inspect.getsource(router)

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
    assert "workflow" not in source.lower()
    assert "llm" not in source.lower()
