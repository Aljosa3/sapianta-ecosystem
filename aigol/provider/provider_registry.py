"""Metadata-only provider registry for AiGOL."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import re
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


DETACHED = "DETACHED"
ATTACHED = "ATTACHED"
AVAILABLE = "AVAILABLE"
UNAVAILABLE = "UNAVAILABLE"
VALID_PROVIDER_STATUSES = frozenset({DETACHED, ATTACHED, AVAILABLE, UNAVAILABLE})

PROVEN_AVAILABLE = "PROVEN_AVAILABLE"
PROVEN_UNAVAILABLE = "PROVEN_UNAVAILABLE"
UNKNOWN_OR_NOT_ESTABLISHED = "UNKNOWN_OR_NOT_ESTABLISHED"
VALID_CAPABILITY_STATES = frozenset(
    {PROVEN_AVAILABLE, PROVEN_UNAVAILABLE, UNKNOWN_OR_NOT_ESTABLISHED}
)

VALID = "VALID"
EXPIRED = "EXPIRED"
NOT_APPLICABLE = "NOT_APPLICABLE"
UNKNOWN_VALIDITY = "UNKNOWN"
VALID_VALIDITY_STATES = frozenset({VALID, EXPIRED, NOT_APPLICABLE, UNKNOWN_VALIDITY})

QUOTA_AVAILABLE = "AVAILABLE"
QUOTA_UNAVAILABLE = "UNAVAILABLE"
QUOTA_UNKNOWN = "UNKNOWN"
QUOTA_NOT_APPLICABLE = "NOT_APPLICABLE"
VALID_QUOTA_STATES = frozenset(
    {QUOTA_AVAILABLE, QUOTA_UNAVAILABLE, QUOTA_UNKNOWN, QUOTA_NOT_APPLICABLE}
)

ELIGIBLE = "ELIGIBLE"
INELIGIBLE = "INELIGIBLE"
CAPABILITY_UNKNOWN = "UNKNOWN"
HUMAN_ACTION_REQUIRED = "HUMAN_ACTION_REQUIRED"

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REPLAY_HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
SECRET_MARKERS = (
    "bearer ",
    "api_key=",
    "api-key=",
    "apikey=",
    "authorization:",
    "session_cookie=",
    "password=",
    "password:",
    "token=",
    "token:",
    "secret=",
    "secret:",
)


@dataclass(frozen=True)
class ProviderMetadata:
    provider_id: str
    provider_type: str
    provider_version: str
    provider_status: str
    domain: str = "unspecified"
    capability: str = "proposal_generation"
    resource_type: str = "provider"

    def to_dict(self) -> dict[str, Any]:
        provider = {
            "provider_id": _normalize_identifier(self.provider_id, "provider_id"),
            "provider_type": _normalize_token(self.provider_type, "provider_type"),
            "provider_version": _require_string(self.provider_version, "provider_version"),
            "provider_status": _normalize_token(self.provider_status, "provider_status"),
            "domain": _normalize_metadata(self.domain, "domain"),
            "capability": _normalize_metadata(self.capability, "capability"),
            "resource_type": _normalize_metadata(self.resource_type, "resource_type"),
            "execution_capable": False,
            "dispatch_capable": False,
            "authority": False,
        }
        if provider["provider_status"] not in VALID_PROVIDER_STATUSES:
            raise FailClosedRuntimeError("provider status is invalid")
        provider["provider_identity_hash"] = replay_hash(provider)
        return provider


@dataclass(frozen=True)
class ExternalProviderCapabilityFact:
    """One identity- and scope-bound external provider capability fact."""

    provider_id: str
    account_or_workspace_id: str
    access_path: str
    worker_identity: str
    capability: str
    authorized_scope: str
    verification_state: str
    validity_state: str
    evidence_source: str
    quota_state: str = QUOTA_NOT_APPLICABLE
    evidence_sha256: str | None = None
    human_owner_or_authority_reference: str = "NOT_ESTABLISHED"

    def to_dict(self) -> dict[str, Any]:
        fact = {
            "provider_id": _normalize_identifier(self.provider_id, "provider_id"),
            "account_or_workspace_id": _normalize_identifier(
                self.account_or_workspace_id, "account_or_workspace_id"
            ),
            "access_path": _normalize_token(self.access_path, "access_path"),
            "worker_identity": _normalize_identifier(self.worker_identity, "worker_identity"),
            "capability": _normalize_token(self.capability, "capability"),
            "authorized_scope": _normalize_identifier(self.authorized_scope, "authorized_scope"),
            "verification_state": _normalize_token(
                self.verification_state, "verification_state"
            ),
            "validity_state": _normalize_token(self.validity_state, "validity_state"),
            "evidence_source": _secret_free_reference(self.evidence_source, "evidence_source"),
            "evidence_sha256": _optional_sha256(self.evidence_sha256),
            "quota_state": _normalize_token(self.quota_state, "quota_state"),
            "human_owner_or_authority_reference": _secret_free_reference(
                self.human_owner_or_authority_reference,
                "human_owner_or_authority_reference",
            ),
            "provider_capability_authority": False,
            "human_authority": False,
            "p11_authority": False,
            "execution_authority": False,
            "dispatch_authority": False,
            "transferable_between_accounts": False,
            "transferable_between_workspaces": False,
            "transferable_between_access_paths": False,
            "secret_material_present": False,
        }
        _validate_capability_fact_fields(fact)
        fact["capability_fact_hash"] = replay_hash(fact)
        return fact


@dataclass(frozen=True)
class ExternalCapabilityRequirement:
    """Consumer policy describing one required external capability."""

    consumer_id: str
    task_id: str
    aigol_role: str
    operation_class: str
    required_capability: str
    authorized_scope: str
    requires_available_quota: bool = False

    def to_dict(self) -> dict[str, Any]:
        requirement = {
            "consumer_id": _normalize_identifier(self.consumer_id, "consumer_id"),
            "task_id": _normalize_identifier(self.task_id, "task_id"),
            "aigol_role": _normalize_token(self.aigol_role, "aigol_role"),
            "operation_class": _normalize_token(self.operation_class, "operation_class"),
            "required_capability": _normalize_token(
                self.required_capability, "required_capability"
            ),
            "authorized_scope": _normalize_identifier(
                self.authorized_scope, "authorized_scope"
            ),
            "requires_available_quota": _require_bool(
                self.requires_available_quota, "requires_available_quota"
            ),
            "provider_fact_owned_by_consumer": False,
            "execution_authority_requested": False,
        }
        requirement["requirement_hash"] = replay_hash(requirement)
        return requirement


@dataclass(frozen=True)
class ExternalCapabilityQuery:
    """Exact provider identity plus consumer-specific requirement."""

    provider_id: str
    account_or_workspace_id: str
    access_path: str
    worker_identity: str
    requirement: ExternalCapabilityRequirement

    def to_dict(self) -> dict[str, Any]:
        query = {
            "provider_id": _normalize_identifier(self.provider_id, "provider_id"),
            "account_or_workspace_id": _normalize_identifier(
                self.account_or_workspace_id, "account_or_workspace_id"
            ),
            "access_path": _normalize_token(self.access_path, "access_path"),
            "worker_identity": _normalize_identifier(self.worker_identity, "worker_identity"),
            "requirement": self.requirement.to_dict(),
        }
        query["query_hash"] = replay_hash(query)
        return query


class ProviderRegistry:
    """Deterministic metadata registry. It does not dispatch or execute providers."""

    def __init__(self) -> None:
        self._providers: dict[str, dict[str, Any]] = {}
        self._capability_facts: dict[tuple[str, ...], dict[str, Any]] = {}

    def register_provider(self, metadata: ProviderMetadata | dict[str, Any]) -> dict[str, Any]:
        provider = _metadata_to_dict(metadata)
        provider_id = provider["provider_id"]
        if provider_id in self._providers:
            raise FailClosedRuntimeError("provider is already registered")
        self._providers[provider_id] = deepcopy(provider)
        return deepcopy(provider)

    def lookup_provider(self, provider_id: str) -> dict[str, Any]:
        normalized = _normalize_identifier(provider_id, "provider_id")
        provider = self._providers.get(normalized)
        if provider is None:
            raise FailClosedRuntimeError("provider is unknown")
        _validate_provider_metadata(provider)
        return deepcopy(provider)

    def provider_metadata(self) -> list[dict[str, Any]]:
        return [deepcopy(provider) for provider in self._providers.values()]

    def register_capability_fact(
        self,
        fact: ExternalProviderCapabilityFact | dict[str, Any],
    ) -> dict[str, Any]:
        """Register one exact, non-transferable provider capability fact."""

        capability_fact = _capability_fact_to_dict(fact)
        self.lookup_provider(capability_fact["provider_id"])
        fact_key = _capability_fact_key(capability_fact)
        if fact_key in self._capability_facts:
            raise FailClosedRuntimeError("provider capability fact is already registered")
        self._capability_facts[fact_key] = deepcopy(capability_fact)
        return deepcopy(capability_fact)

    def lookup_capability_fact(
        self,
        *,
        provider_id: str,
        account_or_workspace_id: str,
        access_path: str,
        worker_identity: str,
        capability: str,
        authorized_scope: str,
    ) -> dict[str, Any]:
        """Return only an exact identity-, path-, capability-, and scope-bound fact."""

        fact_key = (
            _normalize_identifier(provider_id, "provider_id"),
            _normalize_identifier(
                account_or_workspace_id, "account_or_workspace_id"
            ),
            _normalize_token(access_path, "access_path"),
            _normalize_identifier(worker_identity, "worker_identity"),
            _normalize_token(capability, "capability"),
            _normalize_identifier(authorized_scope, "authorized_scope"),
        )
        capability_fact = self._capability_facts.get(fact_key)
        if capability_fact is None:
            raise FailClosedRuntimeError("provider capability fact is unknown")
        _validate_capability_fact(capability_fact)
        return deepcopy(capability_fact)

    def capability_facts(self) -> list[dict[str, Any]]:
        """Return the canonical fact set in deterministic key order."""

        return [
            deepcopy(self._capability_facts[key])
            for key in sorted(self._capability_facts)
        ]

    def resolve_external_capability(
        self,
        query: ExternalCapabilityQuery | dict[str, Any],
    ) -> dict[str, Any]:
        """Resolve eligibility without selecting, dispatching, or granting authority."""

        capability_query = _capability_query_to_dict(query)
        requirement = capability_query["requirement"]
        provider_id = capability_query["provider_id"]

        try:
            provider = self.lookup_provider(provider_id)
        except FailClosedRuntimeError:
            return _capability_resolution(
                capability_query,
                capability_fact=None,
                state=CAPABILITY_UNKNOWN,
                reason="PROVIDER_NOT_ESTABLISHED",
                human_action_required=True,
            )

        fact_key = (
            provider_id,
            capability_query["account_or_workspace_id"],
            capability_query["access_path"],
            capability_query["worker_identity"],
            requirement["required_capability"],
            requirement["authorized_scope"],
        )
        capability_fact = self._capability_facts.get(fact_key)
        if capability_fact is None:
            return _capability_resolution(
                capability_query,
                capability_fact=None,
                state=CAPABILITY_UNKNOWN,
                reason="CAPABILITY_FACT_NOT_ESTABLISHED_FOR_EXACT_IDENTITY_AND_SCOPE",
                human_action_required=True,
            )

        _validate_capability_fact(capability_fact)
        if provider["provider_status"] != AVAILABLE:
            return _capability_resolution(
                capability_query,
                capability_fact=capability_fact,
                state=INELIGIBLE,
                reason="PROVIDER_NOT_AVAILABLE",
                human_action_required=True,
            )
        if capability_fact["verification_state"] == UNKNOWN_OR_NOT_ESTABLISHED:
            return _capability_resolution(
                capability_query,
                capability_fact=capability_fact,
                state=CAPABILITY_UNKNOWN,
                reason="CAPABILITY_UNKNOWN_OR_NOT_ESTABLISHED",
                human_action_required=True,
            )
        if capability_fact["verification_state"] == PROVEN_UNAVAILABLE:
            return _capability_resolution(
                capability_query,
                capability_fact=capability_fact,
                state=INELIGIBLE,
                reason="CAPABILITY_PROVEN_UNAVAILABLE",
                human_action_required=True,
            )
        if capability_fact["validity_state"] != VALID:
            return _capability_resolution(
                capability_query,
                capability_fact=capability_fact,
                state=INELIGIBLE,
                reason="CAPABILITY_EVIDENCE_NOT_VALID",
                human_action_required=True,
            )
        if (
            requirement["requires_available_quota"]
            and capability_fact["quota_state"] != QUOTA_AVAILABLE
        ):
            return _capability_resolution(
                capability_query,
                capability_fact=capability_fact,
                state=INELIGIBLE,
                reason="REQUIRED_QUOTA_NOT_PROVEN_AVAILABLE",
                human_action_required=True,
            )
        return _capability_resolution(
            capability_query,
            capability_fact=capability_fact,
            state=ELIGIBLE,
            reason="REQUIRED_EXTERNAL_CAPABILITY_PROVEN_AVAILABLE",
            human_action_required=False,
        )


def _metadata_to_dict(metadata: ProviderMetadata | dict[str, Any]) -> dict[str, Any]:
    provider = metadata.to_dict() if isinstance(metadata, ProviderMetadata) else _canonicalize_metadata_dict(metadata)
    _validate_provider_metadata(provider)
    return provider


def _canonicalize_metadata_dict(metadata: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(metadata, dict):
        raise FailClosedRuntimeError("provider metadata must be a JSON object")
    provider = deepcopy(metadata)
    existing_hash = provider.pop("provider_identity_hash", None)
    provider["provider_id"] = _normalize_identifier(provider.get("provider_id"), "provider_id")
    provider["provider_type"] = _normalize_token(provider.get("provider_type"), "provider_type")
    provider["provider_version"] = _require_string(provider.get("provider_version"), "provider_version")
    provider["provider_status"] = _normalize_token(provider.get("provider_status"), "provider_status")
    provider["domain"] = _normalize_metadata(provider.get("domain", "unspecified"), "domain")
    provider["capability"] = _normalize_metadata(provider.get("capability", "proposal_generation"), "capability")
    provider["resource_type"] = _normalize_metadata(provider.get("resource_type", "provider"), "resource_type")
    provider["execution_capable"] = provider.get("execution_capable", False)
    provider["dispatch_capable"] = provider.get("dispatch_capable", False)
    provider["authority"] = provider.get("authority", False)
    provider["provider_identity_hash"] = replay_hash(provider)
    if existing_hash is not None and existing_hash != provider["provider_identity_hash"]:
        raise FailClosedRuntimeError("provider identity hash mismatch")
    return provider


def _validate_provider_metadata(provider: dict[str, Any]) -> None:
    if not isinstance(provider, dict):
        raise FailClosedRuntimeError("provider metadata must be a JSON object")
    if provider.get("execution_capable") is not False:
        raise FailClosedRuntimeError("provider metadata cannot be execution capable")
    if provider.get("dispatch_capable") is not False:
        raise FailClosedRuntimeError("provider metadata cannot dispatch")
    if provider.get("authority") is not False:
        raise FailClosedRuntimeError("provider metadata cannot carry authority")
    _normalize_identifier(provider.get("provider_id"), "provider_id")
    _normalize_token(provider.get("provider_type"), "provider_type")
    _require_string(provider.get("provider_version"), "provider_version")
    _normalize_metadata(provider.get("domain", "unspecified"), "domain")
    _normalize_metadata(provider.get("capability", "proposal_generation"), "capability")
    _normalize_metadata(provider.get("resource_type", "provider"), "resource_type")
    status = _normalize_token(provider.get("provider_status"), "provider_status")
    if status not in VALID_PROVIDER_STATUSES:
        raise FailClosedRuntimeError("provider status is invalid")
    actual_hash = _require_string(provider.get("provider_identity_hash"), "provider_identity_hash")
    expected_input = deepcopy(provider)
    expected_input.pop("provider_identity_hash")
    if actual_hash != replay_hash(expected_input):
        raise FailClosedRuntimeError("provider identity hash mismatch")


def _capability_fact_to_dict(
    fact: ExternalProviderCapabilityFact | dict[str, Any],
) -> dict[str, Any]:
    if isinstance(fact, ExternalProviderCapabilityFact):
        capability_fact = fact.to_dict()
    elif isinstance(fact, dict):
        supplied = deepcopy(fact)
        existing_hash = supplied.pop("capability_fact_hash", None)
        allowed_fields = {
            "provider_id",
            "account_or_workspace_id",
            "access_path",
            "worker_identity",
            "capability",
            "authorized_scope",
            "verification_state",
            "validity_state",
            "evidence_source",
            "quota_state",
            "evidence_sha256",
            "human_owner_or_authority_reference",
            "provider_capability_authority",
            "human_authority",
            "p11_authority",
            "execution_authority",
            "dispatch_authority",
            "transferable_between_accounts",
            "transferable_between_workspaces",
            "transferable_between_access_paths",
            "secret_material_present",
        }
        if set(supplied) - allowed_fields:
            raise FailClosedRuntimeError("provider capability fact has unknown fields")
        capability_fact = {
            "provider_id": _normalize_identifier(
                supplied.get("provider_id"), "provider_id"
            ),
            "account_or_workspace_id": _normalize_identifier(
                supplied.get("account_or_workspace_id"),
                "account_or_workspace_id",
            ),
            "access_path": _normalize_token(
                supplied.get("access_path"), "access_path"
            ),
            "worker_identity": _normalize_identifier(
                supplied.get("worker_identity"), "worker_identity"
            ),
            "capability": _normalize_token(
                supplied.get("capability"), "capability"
            ),
            "authorized_scope": _normalize_identifier(
                supplied.get("authorized_scope"), "authorized_scope"
            ),
            "verification_state": _normalize_token(
                supplied.get("verification_state"), "verification_state"
            ),
            "validity_state": _normalize_token(
                supplied.get("validity_state"), "validity_state"
            ),
            "evidence_source": _secret_free_reference(
                supplied.get("evidence_source"), "evidence_source"
            ),
            "evidence_sha256": _optional_sha256(
                supplied.get("evidence_sha256")
            ),
            "quota_state": _normalize_token(
                supplied.get("quota_state", QUOTA_NOT_APPLICABLE),
                "quota_state",
            ),
            "human_owner_or_authority_reference": _secret_free_reference(
                supplied.get(
                    "human_owner_or_authority_reference", "NOT_ESTABLISHED"
                ),
                "human_owner_or_authority_reference",
            ),
            "provider_capability_authority": supplied.get(
                "provider_capability_authority", False
            ),
            "human_authority": supplied.get("human_authority", False),
            "p11_authority": supplied.get("p11_authority", False),
            "execution_authority": supplied.get("execution_authority", False),
            "dispatch_authority": supplied.get("dispatch_authority", False),
            "transferable_between_accounts": supplied.get(
                "transferable_between_accounts", False
            ),
            "transferable_between_workspaces": supplied.get(
                "transferable_between_workspaces", False
            ),
            "transferable_between_access_paths": supplied.get(
                "transferable_between_access_paths", False
            ),
            "secret_material_present": supplied.get("secret_material_present", False),
        }
        _validate_capability_fact_fields(capability_fact)
        capability_fact["capability_fact_hash"] = replay_hash(capability_fact)
        if existing_hash is not None and existing_hash != capability_fact["capability_fact_hash"]:
            raise FailClosedRuntimeError("provider capability fact hash mismatch")
    else:
        raise FailClosedRuntimeError("provider capability fact must be a JSON object")
    _validate_capability_fact(capability_fact)
    return capability_fact


def _validate_capability_fact(fact: dict[str, Any]) -> None:
    if not isinstance(fact, dict):
        raise FailClosedRuntimeError("provider capability fact must be a JSON object")
    _validate_capability_fact_fields(fact)
    actual_hash = _require_replay_hash(
        fact.get("capability_fact_hash"), "capability_fact_hash"
    )
    expected_input = deepcopy(fact)
    expected_input.pop("capability_fact_hash")
    if actual_hash != replay_hash(expected_input):
        raise FailClosedRuntimeError("provider capability fact hash mismatch")


def _validate_capability_fact_fields(fact: dict[str, Any]) -> None:
    _normalize_identifier(fact.get("provider_id"), "provider_id")
    _normalize_identifier(
        fact.get("account_or_workspace_id"), "account_or_workspace_id"
    )
    _normalize_token(fact.get("access_path"), "access_path")
    _normalize_identifier(fact.get("worker_identity"), "worker_identity")
    _normalize_token(fact.get("capability"), "capability")
    _normalize_identifier(fact.get("authorized_scope"), "authorized_scope")
    verification_state = _normalize_token(
        fact.get("verification_state"), "verification_state"
    )
    validity_state = _normalize_token(fact.get("validity_state"), "validity_state")
    quota_state = _normalize_token(fact.get("quota_state"), "quota_state")
    if verification_state not in VALID_CAPABILITY_STATES:
        raise FailClosedRuntimeError("provider capability state is invalid")
    if validity_state not in VALID_VALIDITY_STATES:
        raise FailClosedRuntimeError("provider capability validity is invalid")
    if quota_state not in VALID_QUOTA_STATES:
        raise FailClosedRuntimeError("provider capability quota state is invalid")
    evidence_sha256 = _optional_sha256(fact.get("evidence_sha256"))
    _secret_free_reference(fact.get("evidence_source"), "evidence_source")
    _secret_free_reference(
        fact.get("human_owner_or_authority_reference"),
        "human_owner_or_authority_reference",
    )
    if verification_state in {PROVEN_AVAILABLE, PROVEN_UNAVAILABLE}:
        if evidence_sha256 is None:
            raise FailClosedRuntimeError(
                "proven provider capability state requires evidence SHA-256"
            )
        if validity_state != VALID:
            raise FailClosedRuntimeError(
                "proven provider capability state requires valid evidence"
            )
    for field_name in (
        "provider_capability_authority",
        "human_authority",
        "p11_authority",
        "execution_authority",
        "dispatch_authority",
        "transferable_between_accounts",
        "transferable_between_workspaces",
        "transferable_between_access_paths",
        "secret_material_present",
    ):
        if _require_bool(fact.get(field_name), field_name) is not False:
            raise FailClosedRuntimeError(
                f"provider capability fact cannot set {field_name}"
            )
    _reject_secret_material(fact)


def _capability_fact_key(fact: dict[str, Any]) -> tuple[str, ...]:
    return (
        fact["provider_id"],
        fact["account_or_workspace_id"],
        fact["access_path"],
        fact["worker_identity"],
        fact["capability"],
        fact["authorized_scope"],
    )


def _capability_query_to_dict(
    query: ExternalCapabilityQuery | dict[str, Any],
) -> dict[str, Any]:
    if isinstance(query, ExternalCapabilityQuery):
        return query.to_dict()
    if not isinstance(query, dict):
        raise FailClosedRuntimeError("external capability query must be a JSON object")
    supplied = deepcopy(query)
    existing_hash = supplied.pop("query_hash", None)
    if set(supplied) != {
        "provider_id",
        "account_or_workspace_id",
        "access_path",
        "worker_identity",
        "requirement",
    }:
        raise FailClosedRuntimeError("external capability query fields are invalid")
    capability_query = {
        "provider_id": _normalize_identifier(
            supplied.get("provider_id"), "provider_id"
        ),
        "account_or_workspace_id": _normalize_identifier(
            supplied.get("account_or_workspace_id"), "account_or_workspace_id"
        ),
        "access_path": _normalize_token(supplied.get("access_path"), "access_path"),
        "worker_identity": _normalize_identifier(
            supplied.get("worker_identity"), "worker_identity"
        ),
        "requirement": _capability_requirement_to_dict(supplied.get("requirement")),
    }
    capability_query["query_hash"] = replay_hash(capability_query)
    if existing_hash is not None and existing_hash != capability_query["query_hash"]:
        raise FailClosedRuntimeError("external capability query hash mismatch")
    return capability_query


def _capability_requirement_to_dict(
    requirement: ExternalCapabilityRequirement | dict[str, Any] | Any,
) -> dict[str, Any]:
    if isinstance(requirement, ExternalCapabilityRequirement):
        return requirement.to_dict()
    if not isinstance(requirement, dict):
        raise FailClosedRuntimeError("external capability requirement must be a JSON object")
    supplied = deepcopy(requirement)
    existing_hash = supplied.pop("requirement_hash", None)
    allowed_fields = {
        "consumer_id",
        "task_id",
        "aigol_role",
        "operation_class",
        "required_capability",
        "authorized_scope",
        "requires_available_quota",
        "provider_fact_owned_by_consumer",
        "execution_authority_requested",
    }
    if set(supplied) - allowed_fields:
        raise FailClosedRuntimeError("external capability requirement has unknown fields")
    canonical = {
        "consumer_id": _normalize_identifier(supplied.get("consumer_id"), "consumer_id"),
        "task_id": _normalize_identifier(supplied.get("task_id"), "task_id"),
        "aigol_role": _normalize_token(supplied.get("aigol_role"), "aigol_role"),
        "operation_class": _normalize_token(
            supplied.get("operation_class"), "operation_class"
        ),
        "required_capability": _normalize_token(
            supplied.get("required_capability"), "required_capability"
        ),
        "authorized_scope": _normalize_identifier(
            supplied.get("authorized_scope"), "authorized_scope"
        ),
        "requires_available_quota": _require_bool(
            supplied.get("requires_available_quota", False),
            "requires_available_quota",
        ),
        "provider_fact_owned_by_consumer": _require_bool(
            supplied.get("provider_fact_owned_by_consumer", False),
            "provider_fact_owned_by_consumer",
        ),
        "execution_authority_requested": _require_bool(
            supplied.get("execution_authority_requested", False),
            "execution_authority_requested",
        ),
    }
    if canonical["provider_fact_owned_by_consumer"]:
        raise FailClosedRuntimeError("consumer cannot own canonical provider facts")
    if canonical["execution_authority_requested"]:
        raise FailClosedRuntimeError("capability query cannot request execution authority")
    canonical["requirement_hash"] = replay_hash(canonical)
    if existing_hash is not None and existing_hash != canonical["requirement_hash"]:
        raise FailClosedRuntimeError("external capability requirement hash mismatch")
    return canonical


def _capability_resolution(
    query: dict[str, Any],
    *,
    capability_fact: dict[str, Any] | None,
    state: str,
    reason: str,
    human_action_required: bool,
) -> dict[str, Any]:
    if state not in {ELIGIBLE, INELIGIBLE, CAPABILITY_UNKNOWN}:
        raise FailClosedRuntimeError("external capability resolution state is invalid")
    resolution = {
        "query_hash": query["query_hash"],
        "requirement_hash": query["requirement"]["requirement_hash"],
        "capability_fact_hash": (
            capability_fact["capability_fact_hash"]
            if capability_fact is not None
            else None
        ),
        "resolution_state": state,
        "reason": reason,
        "required_external_capability_detected": True,
        "provider_capability_available": (
            capability_fact is not None
            and capability_fact["verification_state"] == PROVEN_AVAILABLE
            and capability_fact["validity_state"] == VALID
        ),
        "worker_eligible": state == ELIGIBLE,
        "human_action_required": human_action_required,
        "action_state": (
            HUMAN_ACTION_REQUIRED if human_action_required else "NO_HUMAN_ACTION_REQUIRED"
        ),
        "worker_selected": False,
        "human_authority_granted": False,
        "p11_authority_granted": False,
        "execution_authority_granted": False,
        "dispatch_performed": False,
        "provider_invoked": False,
        "execution_requested": False,
        "automatic_continuation": False,
    }
    resolution["resolution_hash"] = replay_hash(resolution)
    return resolution


def _secret_free_reference(value: Any, field_name: str) -> str:
    reference = _require_string(value, field_name).strip()
    if _contains_secret_marker(reference):
        raise FailClosedRuntimeError(f"{field_name} contains secret-like material")
    return reference


def _reject_secret_material(value: Any) -> None:
    if isinstance(value, dict):
        for nested in value.values():
            _reject_secret_material(nested)
    elif isinstance(value, (list, tuple)):
        for nested in value:
            _reject_secret_material(nested)
    elif isinstance(value, str):
        if _contains_secret_marker(value):
            raise FailClosedRuntimeError("provider capability fact contains secret-like material")


def _contains_secret_marker(value: str) -> bool:
    lowered = value.lower()
    return lowered.startswith("sk-") or any(
        marker in lowered for marker in SECRET_MARKERS
    )


def _optional_sha256(value: Any) -> str | None:
    if value is None:
        return None
    return _require_sha256(value, "evidence_sha256")


def _require_sha256(value: Any, field_name: str) -> str:
    digest = _require_string(value, field_name).strip()
    if SHA256_RE.fullmatch(digest) is None:
        raise FailClosedRuntimeError(f"{field_name} must be a lowercase SHA-256")
    return digest


def _require_replay_hash(value: Any, field_name: str) -> str:
    digest = _require_string(value, field_name).strip()
    if REPLAY_HASH_RE.fullmatch(digest) is None:
        raise FailClosedRuntimeError(f"{field_name} must be a replay SHA-256")
    return digest


def _require_bool(value: Any, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise FailClosedRuntimeError(f"{field_name} must be a boolean")
    return value


def _normalize_identifier(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).strip()


def _normalize_token(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).strip().upper().replace("-", "_")


def _normalize_metadata(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).strip().lower().replace("-", "_").replace(" ", "_")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
