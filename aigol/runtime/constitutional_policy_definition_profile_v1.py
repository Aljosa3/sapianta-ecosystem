"""Exact non-production Step-46 constitutional policy-definition profile.

The profile binds one independently issued Human Authority act to the existing
Canonical Human Entry (CHE) mechanics.  It records an approved, pre-G70 policy
definition artifact, or a no-effect Human outcome.  It never selects policy
content, creates Human authority, ratifies an amendment, or connects to
production.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
import json
from types import MappingProxyType
from typing import Any, Mapping

from aigol.runtime.canonical_human_authority_act_contract_v1 import (
    APPROVAL,
    CANCEL,
    HUMAN_AUTHORITY_OWNER,
    REJECT,
    REWORK,
    CanonicalHumanAuthorityActV1,
    bind_canonical_human_authority_act_to_che_v1,
    canonical_human_authority_act_from_request_v1,
)
from aigol.runtime.canonical_human_entry_contract_v1 import (
    ACTIVE_CONTINUATION,
    HUMAN_ACTOR,
    CanonicalContinuationEnvelopeV1,
    CanonicalHumanEntryRequestEnvelopeV1,
    validate_canonical_che_continuation_envelope_v1,
    validate_canonical_che_request_envelope_v1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


STEP46_POLICY_DEFINITION_PROFILE_VERSION = (
    "STEP46_CONSTITUTIONAL_POLICY_DEFINITION_PROFILE_V1"
)
STEP46_POLICY_DEFINITION_ARTIFACT_TYPE = (
    "STEP46_CONSTITUTIONAL_POLICY_DEFINITION_DECISION_ARTIFACT_V1"
)
STEP46_POLICY_DEFINITION_SERIALIZATION_VERSION = (
    "STEP46_CONSTITUTIONAL_POLICY_DEFINITION_SERIALIZATION_V1"
)
STEP46_POLICY_DEFINITION_AUTHORITY_CLASS = (
    "STEP46_CONSTITUTIONAL_POLICY_DEFINITION"
)
STEP46_POLICY_DEFINITION_SCOPE = "STEP46_CONSTITUTIONAL_POLICY_DEFINITION"
STEP46_POLICY_DEFINITION_TARGET = (
    "STEP46_PRE_SOFTWARE_ADMISSION_AUTHORITY_POLICY"
)
STEP46_POLICY_DEFINITION_OWNER = "CONSTITUTIONAL_GOVERNANCE_OWNER"
STEP46_POLICY_DEFINITION_OUTPUT = "PRE_G70"
STEP46_POLICY_DEFINITION_RECORDED_NOT_CERTIFIED = (
    "HUMAN_POLICY_DEFINITION_RECORDED_NOT_CERTIFIED"
)

STEP46_POLICY_DEFINITION_PRESENTATION_COMMAND = (
    "PRESENT_STEP46_CONSTITUTIONAL_POLICY_DEFINITION_PROFILE_V1"
)
STEP46_POLICY_DEFINITION_OWNER_STATUS = (
    "STEP46_POLICY_DEFINITION_AWAITING_HUMAN_DECISION"
)
STEP46_POLICY_DEFINITION_RECORDED_STATUS = (
    "STEP46_POLICY_DEFINITION_RECORDED_NOT_CERTIFIED"
)
STEP46_POLICY_DEFINITION_NO_EFFECT_STATUS = (
    "STEP46_POLICY_DEFINITION_HUMAN_OUTCOME_NO_EFFECT"
)
STEP46_POLICY_DEFINITION_OWNER_STATE_PREFIX = (
    "STEP46-POLICY-DEFINITION-OWNER-STATE-"
)

ADMISSION_AUTHORITY = "ADMISSION_AUTHORITY"
RECOGNITION_ONLY_PREDICATE = "RECOGNITION_ONLY_PREDICATE"
ADMISSION_ARTIFACT_AND_EFFECTIVE_STATE = (
    "ADMISSION_ARTIFACT_AND_EFFECTIVE_STATE"
)
INDEPENDENT_CERTIFIER = "INDEPENDENT_CERTIFIER"
CERTIFICATION_ARTIFACT = "CERTIFICATION_ARTIFACT"

STEP46_POLICY_DEFINITION_FIELDS = (
    ADMISSION_AUTHORITY,
    RECOGNITION_ONLY_PREDICATE,
    ADMISSION_ARTIFACT_AND_EFFECTIVE_STATE,
    INDEPENDENT_CERTIFIER,
    CERTIFICATION_ARTIFACT,
)

APPROVE_EXACT_POLICY_DEFINITION = "APPROVE_EXACT_POLICY_DEFINITION"
MODIFY_AND_RESUBMIT = "MODIFY_AND_RESUBMIT"
DECLINE = "DECLINE"
EXIT_WITHOUT_EFFECT = "EXIT_WITHOUT_EFFECT"

STEP46_POLICY_OUTCOME_BY_AUTHORITY_KIND = MappingProxyType(
    {
        APPROVAL: APPROVE_EXACT_POLICY_DEFINITION,
        REWORK: MODIFY_AND_RESUBMIT,
        REJECT: DECLINE,
        CANCEL: EXIT_WITHOUT_EFFECT,
    }
)

_FORBIDDEN_POLICY_VALUE_MARKERS = frozenset(
    {
        "AI_SELECTED_DEFAULT",
        "AUTO",
        "CALLER_SELECTED_DEFAULT",
        "DEFAULT",
        "INFER",
        "TBD",
        "UNKNOWN",
        "UNSPECIFIED",
    }
)

_DECISION_ARTIFACT_FIELDS = frozenset(
    {
        "profile_contract_version",
        "artifact_type",
        "serialization_version",
        "decision_identity",
        "artifact_digest",
        "decision_state",
        "profile_authority_class",
        "authority_scope",
        "target_identity",
        "target_revision",
        "profile_output",
        "policy_definition",
        "policy_payload_digest",
        "human_authority_act",
        "che_request",
        "che_continuation",
        "human_actor_identity",
        "recorded_at",
        "constitutional_effect_created",
        "g70_handoff_created",
        "production_connection_created",
    }
)


def _require_text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _require_revision(value: Any) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise FailClosedRuntimeError(
            "Step46 policy-definition target revision is invalid"
        )
    return value


def _plain_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _plain_json(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_plain_json(item) for item in value]
    return deepcopy(value)


def _immutable_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) for key in value):
            raise FailClosedRuntimeError(
                "Step46 policy-definition object keys must be strings"
            )
        return MappingProxyType(
            {key: _immutable_json(value[key]) for key in sorted(value)}
        )
    if isinstance(value, (list, tuple)):
        return tuple(_immutable_json(item) for item in value)
    immutable = deepcopy(value)
    canonical_serialize(immutable)
    return immutable


def _is_explicit_policy_value(value: Any) -> bool:
    if value is None or isinstance(value, bool):
        return False
    if isinstance(value, str):
        return bool(value.strip()) and (
            value.strip().upper() not in _FORBIDDEN_POLICY_VALUE_MARKERS
        )
    if isinstance(value, Mapping):
        return bool(value) and all(
            isinstance(key, str)
            and bool(key.strip())
            and _is_explicit_policy_value(item)
            for key, item in value.items()
        )
    if isinstance(value, (list, tuple)):
        return bool(value) and all(_is_explicit_policy_value(item) for item in value)
    return isinstance(value, (int, float))


def validate_step46_policy_definition_payload_v1(
    value: Any,
) -> Mapping[str, Any]:
    """Validate the exact five Human-supplied fields without deriving values."""

    if not isinstance(value, Mapping) or set(value) != set(
        STEP46_POLICY_DEFINITION_FIELDS
    ):
        raise FailClosedRuntimeError(
            "Step46 policy-definition payload field set is invalid"
        )
    if any(not _is_explicit_policy_value(value[field]) for field in value):
        raise FailClosedRuntimeError(
            "Step46 policy-definition payload requires explicit Human values"
        )
    payload = _immutable_json(value)
    canonical_serialize(_plain_json(payload))
    return payload


def step46_policy_definition_payload_digest_v1(value: Any) -> str:
    payload = validate_step46_policy_definition_payload_v1(value)
    return replay_hash({"policy_definition": _plain_json(payload)})


def step46_policy_definition_owner_state_identity_v1(
    target_revision: int,
) -> str:
    revision = _require_revision(target_revision)
    digest = replay_hash(
        {
            "profile_contract_version": STEP46_POLICY_DEFINITION_PROFILE_VERSION,
            "owner": STEP46_POLICY_DEFINITION_OWNER,
            "authority_class": STEP46_POLICY_DEFINITION_AUTHORITY_CLASS,
            "scope": STEP46_POLICY_DEFINITION_SCOPE,
            "target": STEP46_POLICY_DEFINITION_TARGET,
            "target_revision": revision,
        }
    ).removeprefix("sha256:")
    return STEP46_POLICY_DEFINITION_OWNER_STATE_PREFIX + digest


@dataclass(frozen=True, slots=True)
class Step46ConstitutionalPolicyDefinitionDecisionArtifactV1:
    """One approved Human policy definition, recorded before G70."""

    profile_contract_version: str
    artifact_type: str
    serialization_version: str
    decision_identity: str
    artifact_digest: str
    decision_state: str
    profile_authority_class: str
    authority_scope: str
    target_identity: str
    target_revision: int
    profile_output: str
    policy_definition: Mapping[str, Any]
    policy_payload_digest: str
    human_authority_act: CanonicalHumanAuthorityActV1
    che_request: CanonicalHumanEntryRequestEnvelopeV1
    che_continuation: CanonicalContinuationEnvelopeV1
    human_actor_identity: str
    recorded_at: str
    constitutional_effect_created: bool = False
    g70_handoff_created: bool = False
    production_connection_created: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "policy_definition",
            validate_step46_policy_definition_payload_v1(self.policy_definition),
        )

    def identity_payload(self) -> dict[str, Any]:
        return {
            "profile_contract_version": self.profile_contract_version,
            "artifact_type": self.artifact_type,
            "serialization_version": self.serialization_version,
            "decision_state": self.decision_state,
            "profile_authority_class": self.profile_authority_class,
            "authority_scope": self.authority_scope,
            "target_identity": self.target_identity,
            "target_revision": self.target_revision,
            "profile_output": self.profile_output,
            "policy_definition": _plain_json(self.policy_definition),
            "policy_payload_digest": self.policy_payload_digest,
            "human_authority_act": self.human_authority_act.to_dict(),
            "che_request": self.che_request.to_dict(),
            "che_continuation": self.che_continuation.to_dict(),
            "human_actor_identity": self.human_actor_identity,
            "recorded_at": self.recorded_at,
            "constitutional_effect_created": self.constitutional_effect_created,
            "g70_handoff_created": self.g70_handoff_created,
            "production_connection_created": self.production_connection_created,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_identity": self.decision_identity,
            "artifact_digest": self.artifact_digest,
            **self.identity_payload(),
        }

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any]
    ) -> "Step46ConstitutionalPolicyDefinitionDecisionArtifactV1":
        if not isinstance(value, Mapping) or set(value) != _DECISION_ARTIFACT_FIELDS:
            raise FailClosedRuntimeError(
                "Step46 policy-definition decision artifact structure is invalid"
            )
        return cls(
            profile_contract_version=value["profile_contract_version"],
            artifact_type=value["artifact_type"],
            serialization_version=value["serialization_version"],
            decision_identity=value["decision_identity"],
            artifact_digest=value["artifact_digest"],
            decision_state=value["decision_state"],
            profile_authority_class=value["profile_authority_class"],
            authority_scope=value["authority_scope"],
            target_identity=value["target_identity"],
            target_revision=value["target_revision"],
            profile_output=value["profile_output"],
            policy_definition=value["policy_definition"],
            policy_payload_digest=value["policy_payload_digest"],
            human_authority_act=CanonicalHumanAuthorityActV1.from_dict(
                value["human_authority_act"]
            ),
            che_request=CanonicalHumanEntryRequestEnvelopeV1.from_dict(
                value["che_request"]
            ),
            che_continuation=CanonicalContinuationEnvelopeV1.from_dict(
                value["che_continuation"]
            ),
            human_actor_identity=value["human_actor_identity"],
            recorded_at=value["recorded_at"],
            constitutional_effect_created=value["constitutional_effect_created"],
            g70_handoff_created=value["g70_handoff_created"],
            production_connection_created=value["production_connection_created"],
        )


def _validate_profile_metadata(act: CanonicalHumanAuthorityActV1) -> None:
    metadata = act.to_dict()["metadata"]
    if (
        metadata.get("profile_contract_version")
        != STEP46_POLICY_DEFINITION_PROFILE_VERSION
        or metadata.get("profile_authority_class")
        != STEP46_POLICY_DEFINITION_AUTHORITY_CLASS
    ):
        raise FailClosedRuntimeError(
            "Step46 policy-definition authority class binding is invalid"
        )


def validate_step46_policy_definition_che_owner_binding_v1(
    request_value: CanonicalHumanEntryRequestEnvelopeV1 | Mapping[str, Any],
    continuation_value: CanonicalContinuationEnvelopeV1 | Mapping[str, Any],
    act_value: CanonicalHumanAuthorityActV1 | Mapping[str, Any],
) -> CanonicalHumanAuthorityActV1:
    """Bind one allowed Human outcome to the fixed Step-46 owner profile."""

    request = validate_canonical_che_request_envelope_v1(request_value)
    continuation = validate_canonical_che_continuation_envelope_v1(
        continuation_value
    )
    act = (
        act_value
        if isinstance(act_value, CanonicalHumanAuthorityActV1)
        else CanonicalHumanAuthorityActV1.from_dict(dict(act_value))
    )
    if request.actor_class != HUMAN_ACTOR:
        raise FailClosedRuntimeError(
            "Step46 policy-definition decision requires a Human actor"
        )
    if act.authority_kind not in STEP46_POLICY_OUTCOME_BY_AUTHORITY_KIND:
        raise FailClosedRuntimeError(
            "Step46 policy-definition Human outcome is invalid"
        )
    expected_state = step46_policy_definition_owner_state_identity_v1(
        continuation.expected_owner_revision
    )
    if (
        continuation.continuation_state != ACTIVE_CONTINUATION
        or continuation.conversation_identity != expected_state
        or continuation.expected_owner_state_identity != expected_state
    ):
        raise FailClosedRuntimeError(
            "Step46 policy-definition CHE owner state is invalid"
        )
    bound = bind_canonical_human_authority_act_to_che_v1(
        act,
        request,
        continuation,
        expected_authority_kind=act.authority_kind,
        expected_target_identity=STEP46_POLICY_DEFINITION_TARGET,
        expected_target_revision=continuation.expected_owner_revision,
        expected_producing_owner=HUMAN_AUTHORITY_OWNER,
        expected_owner=STEP46_POLICY_DEFINITION_OWNER,
        expected_authority_scope=STEP46_POLICY_DEFINITION_SCOPE,
    )
    _validate_profile_metadata(bound)
    validate_step46_policy_definition_payload_v1(bound.to_dict()["payload"])
    return bound


def compose_step46_policy_definition_result_v1(
    *,
    human_authority_act: CanonicalHumanAuthorityActV1 | Mapping[str, Any],
    che_request: CanonicalHumanEntryRequestEnvelopeV1 | Mapping[str, Any],
    che_continuation: CanonicalContinuationEnvelopeV1 | Mapping[str, Any],
) -> Step46ConstitutionalPolicyDefinitionDecisionArtifactV1 | None:
    """Validate one Human outcome; create an artifact only for APPROVAL."""

    request = validate_canonical_che_request_envelope_v1(che_request)
    continuation = validate_canonical_che_continuation_envelope_v1(
        che_continuation
    )
    request_act = canonical_human_authority_act_from_request_v1(request)
    supplied_act = (
        human_authority_act
        if isinstance(human_authority_act, CanonicalHumanAuthorityActV1)
        else CanonicalHumanAuthorityActV1.from_dict(dict(human_authority_act))
    )
    if request_act is None or request_act.to_dict() != supplied_act.to_dict():
        raise FailClosedRuntimeError(
            "Step46 policy-definition requires the exact structured Human act"
        )
    act = validate_step46_policy_definition_che_owner_binding_v1(
        request, continuation, supplied_act
    )
    if act.authority_kind != APPROVAL:
        return None

    policy_definition = validate_step46_policy_definition_payload_v1(
        act.to_dict()["payload"]
    )
    provisional = Step46ConstitutionalPolicyDefinitionDecisionArtifactV1(
        profile_contract_version=STEP46_POLICY_DEFINITION_PROFILE_VERSION,
        artifact_type=STEP46_POLICY_DEFINITION_ARTIFACT_TYPE,
        serialization_version=STEP46_POLICY_DEFINITION_SERIALIZATION_VERSION,
        decision_identity="PENDING-STEP46-POLICY-DEFINITION",
        artifact_digest="sha256:" + ("0" * 64),
        decision_state=STEP46_POLICY_DEFINITION_RECORDED_NOT_CERTIFIED,
        profile_authority_class=STEP46_POLICY_DEFINITION_AUTHORITY_CLASS,
        authority_scope=STEP46_POLICY_DEFINITION_SCOPE,
        target_identity=STEP46_POLICY_DEFINITION_TARGET,
        target_revision=act.target_revision,
        profile_output=STEP46_POLICY_DEFINITION_OUTPUT,
        policy_definition=policy_definition,
        policy_payload_digest=step46_policy_definition_payload_digest_v1(
            policy_definition
        ),
        human_authority_act=act,
        che_request=request,
        che_continuation=continuation,
        human_actor_identity=act.actor_identity,
        recorded_at=request.created_at,
    )
    identity_payload = provisional.identity_payload()
    artifact = replace(
        provisional,
        decision_identity=(
            "STEP46-POLICY-DEFINITION-"
            + replay_hash(identity_payload).removeprefix("sha256:")
        ),
        artifact_digest=replay_hash(identity_payload),
    )
    return validate_step46_policy_definition_decision_artifact_v1(artifact)


def validate_step46_policy_definition_decision_artifact_v1(
    value: Step46ConstitutionalPolicyDefinitionDecisionArtifactV1
    | Mapping[str, Any],
) -> Step46ConstitutionalPolicyDefinitionDecisionArtifactV1:
    """Fail closed unless an approved artifact preserves every exact binding."""

    artifact = (
        value
        if isinstance(value, Step46ConstitutionalPolicyDefinitionDecisionArtifactV1)
        else Step46ConstitutionalPolicyDefinitionDecisionArtifactV1.from_dict(value)
    )
    constants = (
        artifact.profile_contract_version,
        artifact.artifact_type,
        artifact.serialization_version,
        artifact.decision_state,
        artifact.profile_authority_class,
        artifact.authority_scope,
        artifact.target_identity,
        artifact.profile_output,
    )
    if constants != (
        STEP46_POLICY_DEFINITION_PROFILE_VERSION,
        STEP46_POLICY_DEFINITION_ARTIFACT_TYPE,
        STEP46_POLICY_DEFINITION_SERIALIZATION_VERSION,
        STEP46_POLICY_DEFINITION_RECORDED_NOT_CERTIFIED,
        STEP46_POLICY_DEFINITION_AUTHORITY_CLASS,
        STEP46_POLICY_DEFINITION_SCOPE,
        STEP46_POLICY_DEFINITION_TARGET,
        STEP46_POLICY_DEFINITION_OUTPUT,
    ):
        raise FailClosedRuntimeError(
            "Step46 policy-definition decision constants are invalid"
        )
    _require_revision(artifact.target_revision)
    act = validate_step46_policy_definition_che_owner_binding_v1(
        artifact.che_request,
        artifact.che_continuation,
        artifact.human_authority_act,
    )
    if act.authority_kind != APPROVAL:
        raise FailClosedRuntimeError(
            "Step46 approved policy artifact requires Human APPROVAL"
        )
    policy_definition = validate_step46_policy_definition_payload_v1(
        artifact.policy_definition
    )
    if (
        _plain_json(policy_definition) != act.to_dict()["payload"]
        or artifact.policy_payload_digest
        != step46_policy_definition_payload_digest_v1(policy_definition)
        or artifact.target_revision != act.target_revision
        or artifact.human_actor_identity != act.actor_identity
        or artifact.recorded_at != artifact.che_request.created_at
    ):
        raise FailClosedRuntimeError(
            "Step46 policy-definition decision binding is invalid"
        )
    if any(
        (
            artifact.constitutional_effect_created,
            artifact.g70_handoff_created,
            artifact.production_connection_created,
        )
    ):
        raise FailClosedRuntimeError(
            "Step46 policy-definition artifact exceeded the pre-G70 boundary"
        )
    expected_identity = (
        "STEP46-POLICY-DEFINITION-"
        + replay_hash(artifact.identity_payload()).removeprefix("sha256:")
    )
    expected_digest = replay_hash(artifact.identity_payload())
    if (
        artifact.decision_identity != expected_identity
        or artifact.artifact_digest != expected_digest
    ):
        raise FailClosedRuntimeError(
            "Step46 policy-definition decision identity is invalid"
        )
    canonical_serialize(artifact.to_dict())
    return artifact


def serialize_step46_policy_definition_decision_v1(
    value: Step46ConstitutionalPolicyDefinitionDecisionArtifactV1
    | Mapping[str, Any],
) -> str:
    artifact = validate_step46_policy_definition_decision_artifact_v1(value)
    return canonical_serialize(artifact.to_dict())


def deserialize_step46_policy_definition_decision_v1(
    serialized: str | bytes,
) -> Step46ConstitutionalPolicyDefinitionDecisionArtifactV1:
    if isinstance(serialized, bytes):
        try:
            source = serialized.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise FailClosedRuntimeError(
                "Step46 policy-definition serialization is not UTF-8"
            ) from exc
    elif isinstance(serialized, str):
        source = serialized
    else:
        raise FailClosedRuntimeError(
            "Step46 policy-definition serialization is malformed"
        )
    try:
        decoded = json.loads(source)
    except json.JSONDecodeError as exc:
        raise FailClosedRuntimeError(
            "Step46 policy-definition serialization is not valid JSON"
        ) from exc
    artifact = validate_step46_policy_definition_decision_artifact_v1(decoded)
    if canonical_serialize(artifact.to_dict()) != source:
        raise FailClosedRuntimeError(
            "Step46 policy-definition serialization is not canonical"
        )
    return artifact


def step46_policy_definition_owner_result_v1(
    target_revision: int,
) -> dict[str, Any]:
    """Return the owner presentation without selecting any policy value."""

    revision = _require_revision(target_revision)
    state_identity = step46_policy_definition_owner_state_identity_v1(revision)
    return {
        "step46_policy_definition_owner_presentation": {
            "profile_contract_version": STEP46_POLICY_DEFINITION_PROFILE_VERSION,
            "owner_status": STEP46_POLICY_DEFINITION_OWNER_STATUS,
            "producing_owner": STEP46_POLICY_DEFINITION_OWNER,
            "conversation_identity": state_identity,
            "owner_state_identity": state_identity,
            "target_revision": revision,
            "target_identity": STEP46_POLICY_DEFINITION_TARGET,
            "profile_authority_class": STEP46_POLICY_DEFINITION_AUTHORITY_CLASS,
            "authority_scope": STEP46_POLICY_DEFINITION_SCOPE,
            "required_policy_fields": list(STEP46_POLICY_DEFINITION_FIELDS),
            "permitted_authority_kinds": list(
                STEP46_POLICY_OUTCOME_BY_AUTHORITY_KIND
            ),
            "profile_output": STEP46_POLICY_DEFINITION_OUTPUT,
        },
        "human_visible_completion_result": (
            "The exact Step46 policy-definition profile is ready for an "
            "independent Human decision. No policy value has been selected, "
            "no constitutional effect exists, and the output remains pre-G70."
        ),
    }


def present_step46_policy_definition_boundary_v1(
    *,
    request: CanonicalHumanEntryRequestEnvelopeV1 | Mapping[str, Any],
    target_revision: int,
):
    """Use the sole CHE to issue the owner-bound Step-46 presentation."""

    canonical_request = validate_canonical_che_request_envelope_v1(request)
    if canonical_request.actor_class != HUMAN_ACTOR:
        raise FailClosedRuntimeError(
            "Step46 policy-definition presentation requires a Human actor"
        )
    if (
        canonical_request.source_modality != "TEXT"
        or canonical_request.to_dict()["source_payload"]
        != STEP46_POLICY_DEFINITION_PRESENTATION_COMMAND
    ):
        raise FailClosedRuntimeError(
            "Step46 policy-definition presentation command is invalid"
        )
    revision = _require_revision(target_revision)
    from aigol.runtime.human_interface_runtime_entry_service import (
        _execute_canonical_che_request_v1,
    )

    return _execute_canonical_che_request_v1(
        canonical_request,
        lambda _request: step46_policy_definition_owner_result_v1(revision),
        bind_continuation=True,
    )


def submit_step46_policy_definition_decision_v1(
    *,
    request: CanonicalHumanEntryRequestEnvelopeV1 | Mapping[str, Any],
    continuation: CanonicalContinuationEnvelopeV1 | Mapping[str, Any],
):
    """Consume, but never create, one exact Human Step-46 decision act."""

    canonical_request = validate_canonical_che_request_envelope_v1(request)
    canonical_continuation = validate_canonical_che_continuation_envelope_v1(
        continuation
    )
    act = canonical_human_authority_act_from_request_v1(canonical_request)
    if act is None:
        raise FailClosedRuntimeError(
            "Step46 policy-definition submission requires Human Authority Act"
        )
    from aigol.runtime.human_interface_runtime_entry_service import (
        _execute_canonical_che_request_v1,
    )

    def owner_executor(
        _request: CanonicalHumanEntryRequestEnvelopeV1,
    ) -> dict[str, Any]:
        artifact = compose_step46_policy_definition_result_v1(
            human_authority_act=act,
            che_request=canonical_request,
            che_continuation=canonical_continuation,
        )
        outcome = STEP46_POLICY_OUTCOME_BY_AUTHORITY_KIND[act.authority_kind]
        state_identity = step46_policy_definition_owner_state_identity_v1(
            act.target_revision
        )
        status = (
            STEP46_POLICY_DEFINITION_RECORDED_STATUS
            if artifact is not None
            else STEP46_POLICY_DEFINITION_NO_EFFECT_STATUS
        )
        return {
            "step46_policy_definition_owner_result": {
                "profile_contract_version": (
                    STEP46_POLICY_DEFINITION_PROFILE_VERSION
                ),
                "owner_status": status,
                "producing_owner": STEP46_POLICY_DEFINITION_OWNER,
                "conversation_identity": state_identity,
                "owner_state_identity": state_identity,
                "owner_revision": act.target_revision,
                "authority_kind": act.authority_kind,
                "profile_outcome": outcome,
                "authority_act_identity": act.authority_act_identity,
                "decision_artifact": (
                    artifact.to_dict() if artifact is not None else None
                ),
                "constitutional_effect_created": False,
                "g70_handoff_created": False,
                "production_connection_created": False,
            },
            "human_visible_completion_result": (
                "The Human Step46 policy definition was recorded and remains "
                "pre-G70 and not certified."
                if artifact is not None
                else "The Human Step46 outcome created no approved policy "
                "artifact and no constitutional effect."
            ),
        }

    return _execute_canonical_che_request_v1(
        canonical_request,
        owner_executor,
        continuation_envelope=canonical_continuation,
        bind_continuation=True,
        authority_act=act,
    )


__all__ = [
    "ADMISSION_ARTIFACT_AND_EFFECTIVE_STATE",
    "ADMISSION_AUTHORITY",
    "APPROVE_EXACT_POLICY_DEFINITION",
    "CERTIFICATION_ARTIFACT",
    "DECLINE",
    "EXIT_WITHOUT_EFFECT",
    "INDEPENDENT_CERTIFIER",
    "MODIFY_AND_RESUBMIT",
    "RECOGNITION_ONLY_PREDICATE",
    "STEP46_POLICY_DEFINITION_ARTIFACT_TYPE",
    "STEP46_POLICY_DEFINITION_AUTHORITY_CLASS",
    "STEP46_POLICY_DEFINITION_FIELDS",
    "STEP46_POLICY_DEFINITION_NO_EFFECT_STATUS",
    "STEP46_POLICY_DEFINITION_OUTPUT",
    "STEP46_POLICY_DEFINITION_OWNER",
    "STEP46_POLICY_DEFINITION_OWNER_STATE_PREFIX",
    "STEP46_POLICY_DEFINITION_OWNER_STATUS",
    "STEP46_POLICY_DEFINITION_PRESENTATION_COMMAND",
    "STEP46_POLICY_DEFINITION_PROFILE_VERSION",
    "STEP46_POLICY_DEFINITION_RECORDED_NOT_CERTIFIED",
    "STEP46_POLICY_DEFINITION_RECORDED_STATUS",
    "STEP46_POLICY_DEFINITION_SCOPE",
    "STEP46_POLICY_DEFINITION_TARGET",
    "STEP46_POLICY_OUTCOME_BY_AUTHORITY_KIND",
    "Step46ConstitutionalPolicyDefinitionDecisionArtifactV1",
    "compose_step46_policy_definition_result_v1",
    "deserialize_step46_policy_definition_decision_v1",
    "present_step46_policy_definition_boundary_v1",
    "serialize_step46_policy_definition_decision_v1",
    "step46_policy_definition_owner_result_v1",
    "step46_policy_definition_owner_state_identity_v1",
    "step46_policy_definition_payload_digest_v1",
    "submit_step46_policy_definition_decision_v1",
    "validate_step46_policy_definition_che_owner_binding_v1",
    "validate_step46_policy_definition_decision_artifact_v1",
    "validate_step46_policy_definition_payload_v1",
]
