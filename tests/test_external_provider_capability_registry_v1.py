from dataclasses import fields

import pytest

from aigol.provider.provider_registry import (
    AVAILABLE,
    CAPABILITY_UNKNOWN,
    ELIGIBLE,
    INELIGIBLE,
    PROVEN_AVAILABLE,
    PROVEN_UNAVAILABLE,
    QUOTA_AVAILABLE,
    QUOTA_UNKNOWN,
    UNKNOWN_OR_NOT_ESTABLISHED,
    VALID,
    ExternalCapabilityQuery,
    ExternalCapabilityRequirement,
    ExternalProviderCapabilityFact,
    ProviderMetadata,
    ProviderRegistry,
)
from aigol.runtime.models import FailClosedRuntimeError


EVIDENCE_SHA256 = "a" * 64


def _registry(
    *, provider_id: str = "external-provider-a", capability: str = "trusted_access"
) -> ProviderRegistry:
    registry = ProviderRegistry()
    registry.register_provider(
        ProviderMetadata(
            provider_id=provider_id,
            provider_type="external",
            provider_version="v1",
            provider_status=AVAILABLE,
            capability=capability,
        )
    )
    return registry


def _fact(
    *,
    provider_id: str = "external-provider-a",
    account_or_workspace_id: str = "workspace-a",
    access_path: str = "codex",
    worker_identity: str = "worker-a",
    capability: str = "trusted_access",
    authorized_scope: str = "repository:sapianta",
    verification_state: str = PROVEN_AVAILABLE,
    quota_state: str = QUOTA_AVAILABLE,
    evidence_sha256: str | None = EVIDENCE_SHA256,
    evidence_source: str = "repository-evidence:g77-256fg",
) -> ExternalProviderCapabilityFact:
    return ExternalProviderCapabilityFact(
        provider_id=provider_id,
        account_or_workspace_id=account_or_workspace_id,
        access_path=access_path,
        worker_identity=worker_identity,
        capability=capability,
        authorized_scope=authorized_scope,
        verification_state=verification_state,
        validity_state=VALID,
        evidence_source=evidence_source,
        evidence_sha256=evidence_sha256,
        quota_state=quota_state,
        human_owner_or_authority_reference="human-owner-reference-only",
    )


def _query(
    *,
    consumer_id: str = "worker-selection",
    task_id: str = "task-a",
    aigol_role: str = "implementation_worker",
    operation_class: str = "repository_change",
    provider_id: str = "external-provider-a",
    account_or_workspace_id: str = "workspace-a",
    access_path: str = "codex",
    worker_identity: str = "worker-a",
    required_capability: str = "trusted_access",
    authorized_scope: str = "repository:sapianta",
    requires_available_quota: bool = False,
) -> ExternalCapabilityQuery:
    return ExternalCapabilityQuery(
        provider_id=provider_id,
        account_or_workspace_id=account_or_workspace_id,
        access_path=access_path,
        worker_identity=worker_identity,
        requirement=ExternalCapabilityRequirement(
            consumer_id=consumer_id,
            task_id=task_id,
            aigol_role=aigol_role,
            operation_class=operation_class,
            required_capability=required_capability,
            authorized_scope=authorized_scope,
            requires_available_quota=requires_available_quota,
        ),
    )


def test_proven_available_fact_only_establishes_worker_eligibility() -> None:
    registry = _registry()
    registered = registry.register_capability_fact(_fact())

    resolution = registry.resolve_external_capability(_query())

    assert resolution["resolution_state"] == ELIGIBLE
    assert resolution["provider_capability_available"] is True
    assert resolution["worker_eligible"] is True
    assert resolution["capability_fact_hash"] == registered["capability_fact_hash"]
    assert resolution["human_action_required"] is False
    assert resolution["worker_selected"] is False
    assert resolution["human_authority_granted"] is False
    assert resolution["p11_authority_granted"] is False
    assert resolution["execution_authority_granted"] is False
    assert resolution["dispatch_performed"] is False
    assert resolution["provider_invoked"] is False
    assert resolution["execution_requested"] is False
    assert resolution["automatic_continuation"] is False


@pytest.mark.parametrize(
    ("verification_state", "expected_state"),
    [
        (UNKNOWN_OR_NOT_ESTABLISHED, CAPABILITY_UNKNOWN),
        (PROVEN_UNAVAILABLE, INELIGIBLE),
    ],
)
def test_unknown_and_unavailable_capability_fail_closed(
    verification_state: str, expected_state: str
) -> None:
    registry = _registry()
    evidence_sha256 = (
        None if verification_state == UNKNOWN_OR_NOT_ESTABLISHED else EVIDENCE_SHA256
    )
    registry.register_capability_fact(
        _fact(
            verification_state=verification_state,
            evidence_sha256=evidence_sha256,
        )
    )

    resolution = registry.resolve_external_capability(_query())

    assert resolution["resolution_state"] == expected_state
    assert resolution["provider_capability_available"] is False
    assert resolution["worker_eligible"] is False
    assert resolution["human_action_required"] is True


@pytest.mark.parametrize("verification_state", [PROVEN_AVAILABLE, PROVEN_UNAVAILABLE])
def test_proven_capability_state_requires_evidence(
    verification_state: str,
) -> None:
    registry = _registry()

    with pytest.raises(
        FailClosedRuntimeError,
        match="proven provider capability state requires evidence SHA-256",
    ):
        registry.register_capability_fact(
            _fact(
                verification_state=verification_state,
                evidence_sha256=None,
            )
        )


def test_account_identity_does_not_transfer() -> None:
    registry = _registry()
    registry.register_capability_fact(_fact(account_or_workspace_id="account-a"))

    resolution = registry.resolve_external_capability(
        _query(account_or_workspace_id="account-b")
    )

    assert resolution["resolution_state"] == CAPABILITY_UNKNOWN
    assert resolution["capability_fact_hash"] is None
    assert resolution["worker_eligible"] is False


def test_workspace_identity_does_not_transfer() -> None:
    registry = _registry()
    registry.register_capability_fact(_fact(account_or_workspace_id="workspace-a"))

    resolution = registry.resolve_external_capability(
        _query(account_or_workspace_id="workspace-b")
    )

    assert resolution["resolution_state"] == CAPABILITY_UNKNOWN
    assert resolution["capability_fact_hash"] is None


@pytest.mark.parametrize(
    ("fact_path", "query_path"), [("codex", "api"), ("api", "codex")]
)
def test_access_path_capability_does_not_transfer(
    fact_path: str, query_path: str
) -> None:
    registry = _registry()
    registry.register_capability_fact(_fact(access_path=fact_path))

    resolution = registry.resolve_external_capability(_query(access_path=query_path))

    assert resolution["resolution_state"] == CAPABILITY_UNKNOWN
    assert resolution["capability_fact_hash"] is None


def test_p11_or_human_authority_cannot_be_supplied_by_a_capability_query() -> None:
    registry = _registry()

    resolution = registry.resolve_external_capability(_query())

    assert resolution["resolution_state"] == CAPABILITY_UNKNOWN
    assert "p11_authority" not in _query().to_dict()
    assert "human_authority" not in _query().to_dict()
    assert resolution["human_authority_granted"] is False
    assert resolution["p11_authority_granted"] is False


def test_one_fact_supports_multiple_roles_and_consumer_policies() -> None:
    registry = _registry()
    registered = registry.register_capability_fact(
        _fact(quota_state=QUOTA_UNKNOWN)
    )

    worker_selection = registry.resolve_external_capability(
        _query(consumer_id="worker-selection", requires_available_quota=False)
    )
    api_routing = registry.resolve_external_capability(
        _query(
            consumer_id="api-routing",
            task_id="task-b",
            aigol_role="api_router",
            operation_class="external_api_routing",
            requires_available_quota=True,
        )
    )

    assert len(registry.capability_facts()) == 1
    assert worker_selection["capability_fact_hash"] == registered["capability_fact_hash"]
    assert api_routing["capability_fact_hash"] == registered["capability_fact_hash"]
    assert worker_selection["provider_capability_available"] is True
    assert api_routing["provider_capability_available"] is True
    assert worker_selection["resolution_state"] == ELIGIBLE
    assert api_routing["resolution_state"] == INELIGIBLE


def test_consumer_cannot_own_or_mutate_provider_fact_state() -> None:
    registry = _registry()
    fact = registry.register_capability_fact(_fact())
    serialized_query = _query().to_dict()
    serialized_query["requirement"]["provider_fact_owned_by_consumer"] = True
    serialized_query.pop("query_hash")
    serialized_query["requirement"].pop("requirement_hash")

    with pytest.raises(
        FailClosedRuntimeError, match="consumer cannot own canonical provider facts"
    ):
        registry.resolve_external_capability(serialized_query)

    assert registry.capability_facts() == [fact]


def test_secret_like_material_is_rejected() -> None:
    registry = _registry()

    with pytest.raises(FailClosedRuntimeError, match="secret-like material"):
        registry.register_capability_fact(
            _fact(evidence_source="authorization: bearer redacted-but-secret-like")
        )


def test_trusted_access_is_not_a_global_boolean_or_transferable_field() -> None:
    fact_fields = {field.name for field in fields(ExternalProviderCapabilityFact)}
    canonical = _fact().to_dict()

    assert "trusted_access" not in fact_fields
    assert "provider_id" in fact_fields
    assert "account_or_workspace_id" in fact_fields
    assert "access_path" in fact_fields
    assert "worker_identity" in fact_fields
    assert "authorized_scope" in fact_fields
    assert canonical["transferable_between_accounts"] is False
    assert canonical["transferable_between_workspaces"] is False
    assert canonical["transferable_between_access_paths"] is False


def test_new_provider_and_capability_use_the_same_generic_contract() -> None:
    registry = _registry(
        provider_id="future-provider-b", capability="regional_availability"
    )
    registered = registry.register_capability_fact(
        _fact(
            provider_id="future-provider-b",
            capability="regional_availability",
        )
    )

    resolution = registry.resolve_external_capability(
        _query(
            provider_id="future-provider-b",
            required_capability="regional_availability",
        )
    )

    assert resolution["resolution_state"] == ELIGIBLE
    assert resolution["capability_fact_hash"] == registered["capability_fact_hash"]


def test_duplicate_fact_and_unknown_provider_fail_closed() -> None:
    registry = _registry()
    registry.register_capability_fact(_fact())

    with pytest.raises(FailClosedRuntimeError, match="already registered"):
        registry.register_capability_fact(_fact())

    with pytest.raises(FailClosedRuntimeError, match="provider is unknown"):
        registry.register_capability_fact(_fact(provider_id="unknown-provider"))
