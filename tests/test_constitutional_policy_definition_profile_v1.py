"""Focused Step-49 profile, CHE, and cross-domain separation proof."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from aigol.runtime.canonical_hic_conformance_runtime_v1 import (
    CLIA_CONFORMANCE_PROFILE_V1,
    create_canonical_hic_human_authority_act_request_v1,
    create_canonical_hic_text_request_v1,
)
from aigol.runtime.canonical_human_authority_act_contract_v1 import (
    APPROVAL,
    CANCEL,
    CANONICAL_HUMAN_AUTHORITY_ACT_CONTRACT_VERSION,
    HUMAN_AUTHORITY_OWNER,
    REJECT,
    REWORK,
    CanonicalHumanAuthorityActV1,
    canonical_human_authority_payload_digest_v1,
)
from aigol.runtime.canonical_human_entry_contract_v1 import (
    ACTIVE_CONTINUATION,
    ELIGIBLE_SOURCE_ACTOR,
    REFERENCE_NOT_CREATED,
    TERMINAL_CONTINUATION,
)
from aigol.runtime.constitutional_human_ratification_contract_v1 import (
    CONSTITUTIONAL_AMENDMENT_RATIFICATION_SCOPE,
    constitutional_ratification_payload_v1,
    validate_constitutional_human_ratification_artifact_v1,
)
from aigol.runtime.constitutional_policy_definition_profile_v1 import (
    ADMISSION_ARTIFACT_AND_EFFECTIVE_STATE,
    ADMISSION_AUTHORITY,
    APPROVE_EXACT_POLICY_DEFINITION,
    CERTIFICATION_ARTIFACT,
    DECLINE,
    EXIT_WITHOUT_EFFECT,
    INDEPENDENT_CERTIFIER,
    MODIFY_AND_RESUBMIT,
    RECOGNITION_ONLY_PREDICATE,
    STEP46_POLICY_DEFINITION_ARTIFACT_TYPE,
    STEP46_POLICY_DEFINITION_AUTHORITY_CLASS,
    STEP46_POLICY_DEFINITION_FIELDS,
    STEP46_POLICY_DEFINITION_NO_EFFECT_STATUS,
    STEP46_POLICY_DEFINITION_OUTPUT,
    STEP46_POLICY_DEFINITION_OWNER,
    STEP46_POLICY_DEFINITION_OWNER_STATUS,
    STEP46_POLICY_DEFINITION_PRESENTATION_COMMAND,
    STEP46_POLICY_DEFINITION_PROFILE_VERSION,
    STEP46_POLICY_DEFINITION_RECORDED_NOT_CERTIFIED,
    STEP46_POLICY_DEFINITION_RECORDED_STATUS,
    STEP46_POLICY_DEFINITION_SCOPE,
    STEP46_POLICY_DEFINITION_TARGET,
    STEP46_POLICY_OUTCOME_BY_AUTHORITY_KIND,
    compose_step46_policy_definition_result_v1,
    deserialize_step46_policy_definition_decision_v1,
    present_step46_policy_definition_boundary_v1,
    serialize_step46_policy_definition_decision_v1,
    submit_step46_policy_definition_decision_v1,
    validate_step46_policy_definition_decision_artifact_v1,
    validate_step46_policy_definition_payload_v1,
)
from aigol.runtime.governed_implementation_request_runtime import (
    APPROVED,
    HUMAN_APPROVAL_ARTIFACT_V1,
    _validate_human_approval,
)
from aigol.runtime.g76_revision_4_ratification_owner_composition_v1 import (
    G76_REVISION_4_PRESENTATION_COMMAND,
    compose_g76_revision_4_human_ratification_v1,
    materialize_g76_revision_4_ratification_package_v1,
    present_g76_revision_4_ratification_boundary_v1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-09-19T12:00:00Z"
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _policy_payload() -> dict[str, str]:
    return {
        ADMISSION_AUTHORITY: "HUMAN_CONSTITUTIONAL_ADMISSION_AUTHORITY",
        RECOGNITION_ONLY_PREDICATE: (
            "Recognize only an exact independently certified admission artifact."
        ),
        ADMISSION_ARTIFACT_AND_EFFECTIVE_STATE: (
            "STEP46_ADMISSION_ARTIFACT_V1 in EFFECTIVE_CERTIFIED state"
        ),
        INDEPENDENT_CERTIFIER: "INDEPENDENT_CONSTITUTIONAL_CERTIFIER",
        CERTIFICATION_ARTIFACT: "STEP46_POLICY_CERTIFICATION_ARTIFACT_V1",
    }


def _presentation_request(runtime_root: Path, *, number: int = 1):
    return create_canonical_hic_text_request_v1(
        profile=CLIA_CONFORMANCE_PROFILE_V1,
        actor_identity="STEP49-SYNTHETIC-HUMAN",
        session_identity="STEP49-SYNTHETIC-SESSION",
        workspace_identity=str(REPOSITORY_ROOT),
        runtime_scope_identity=str(runtime_root),
        request_identity=f"STEP49-PRESENTATION-REQUEST-{number}",
        source_act_identity=f"STEP49-PRESENTATION-ACT-{number}",
        order_identity=f"STEP49-PRESENTATION-ORDER-{number}",
        idempotency_identity=f"STEP49-PRESENTATION-IDEMPOTENCY-{number}",
        exact_text=STEP46_POLICY_DEFINITION_PRESENTATION_COMMAND,
        created_at=CREATED_AT,
    )


def _presentation(runtime_root: Path, *, target_revision: int = 1):
    request = _presentation_request(runtime_root)
    response = present_step46_policy_definition_boundary_v1(
        request=request,
        target_revision=target_revision,
    )
    continuation = response.continuation_envelope
    assert continuation is not None
    return request, response, continuation


def _act_and_request(
    continuation,
    *,
    authority_kind: str = APPROVAL,
    payload=None,
    act_identity: str = "STEP49-SYNTHETIC-HUMAN-ACT",
    request_identity: str = "STEP49-SYNTHETIC-HUMAN-REQUEST",
    order_identity: str = "STEP49-SYNTHETIC-HUMAN-ORDER",
    idempotency_identity: str = "STEP49-SYNTHETIC-HUMAN-IDEMPOTENCY",
    target_identity: str = STEP46_POLICY_DEFINITION_TARGET,
    target_revision: int | None = None,
    expected_owner: str = STEP46_POLICY_DEFINITION_OWNER,
    authority_scope: str = STEP46_POLICY_DEFINITION_SCOPE,
    profile_authority_class: str = STEP46_POLICY_DEFINITION_AUTHORITY_CLASS,
):
    exact_payload = _policy_payload() if payload is None else payload
    act = CanonicalHumanAuthorityActV1(
        contract_version=CANONICAL_HUMAN_AUTHORITY_ACT_CONTRACT_VERSION,
        authority_act_identity=act_identity,
        authority_kind=authority_kind,
        interaction_identity=continuation.interaction_identity,
        conversation_identity=continuation.conversation_identity,
        session_identity=continuation.session_identity,
        actor_identity=continuation.actor_identity,
        request_identity=request_identity,
        continuation_identity=continuation.continuation_identity,
        target_identity=target_identity,
        target_revision=(
            continuation.expected_owner_revision
            if target_revision is None
            else target_revision
        ),
        producing_owner=HUMAN_AUTHORITY_OWNER,
        expected_owner=expected_owner,
        authority_scope=authority_scope,
        payload=exact_payload,
        payload_digest=canonical_human_authority_payload_digest_v1(
            exact_payload
        ),
        metadata={
            "profile_contract_version": (
                STEP46_POLICY_DEFINITION_PROFILE_VERSION
            ),
            "profile_authority_class": profile_authority_class,
            "test_fixture": "SYNTHETIC_NON_AUTHORITATIVE",
        },
    )
    request = create_canonical_hic_human_authority_act_request_v1(
        profile=CLIA_CONFORMANCE_PROFILE_V1,
        human_authority_act=act,
        continuation=continuation,
        request_identity=request_identity,
        order_identity=order_identity,
        idempotency_identity=idempotency_identity,
        created_at=CREATED_AT,
    )
    return act, request


def _artifact(runtime_root: Path):
    _, _, continuation = _presentation(runtime_root)
    act, request = _act_and_request(continuation)
    artifact = compose_step46_policy_definition_result_v1(
        human_authority_act=act,
        che_request=request,
        che_continuation=continuation,
    )
    assert artifact is not None
    return artifact


def test_owner_presentation_is_exact_human_bound_and_contains_no_defaults(
    tmp_path: Path,
) -> None:
    _, response, continuation = _presentation(tmp_path)

    binding = response.owner_transition.payload_constraints[
        "canonical_authority_act_binding"
    ]
    assert response.owner_status == STEP46_POLICY_DEFINITION_OWNER_STATUS
    assert response.owner_transition.producing_owner == (
        STEP46_POLICY_DEFINITION_OWNER
    )
    assert response.owner_transition.exact_human_act_required is True
    assert response.owner_transition.permitted_controls == (
        APPROVAL,
        REWORK,
        REJECT,
        CANCEL,
    )
    assert binding["profile_authority_class"] == (
        STEP46_POLICY_DEFINITION_AUTHORITY_CLASS
    )
    assert binding["authority_scope"] == STEP46_POLICY_DEFINITION_SCOPE
    assert binding["target_identity"] == STEP46_POLICY_DEFINITION_TARGET
    assert response.owner_transition.payload_constraints[
        "required_policy_fields"
    ] == STEP46_POLICY_DEFINITION_FIELDS
    assert response.owner_transition.payload_constraints[
        "substantive_policy_defaults"
    ] is False
    assert continuation.continuation_state == ACTIVE_CONTINUATION


def test_non_human_actor_cannot_enter_profile(tmp_path: Path) -> None:
    request = replace(
        _presentation_request(tmp_path),
        actor_class=ELIGIBLE_SOURCE_ACTOR,
    )

    with pytest.raises(FailClosedRuntimeError, match="Human actor"):
        present_step46_policy_definition_boundary_v1(
            request=request,
            target_revision=1,
        )


def test_approved_artifact_is_immutable_deterministic_canonical_and_pre_g70(
    tmp_path: Path,
) -> None:
    artifact = _artifact(tmp_path)
    restored = deserialize_step46_policy_definition_decision_v1(
        serialize_step46_policy_definition_decision_v1(artifact)
    )

    assert restored == artifact
    assert artifact.artifact_type == STEP46_POLICY_DEFINITION_ARTIFACT_TYPE
    assert artifact.decision_state == (
        STEP46_POLICY_DEFINITION_RECORDED_NOT_CERTIFIED
    )
    assert artifact.profile_authority_class == (
        STEP46_POLICY_DEFINITION_AUTHORITY_CLASS
    )
    assert artifact.profile_output == STEP46_POLICY_DEFINITION_OUTPUT
    assert set(artifact.policy_definition) == set(STEP46_POLICY_DEFINITION_FIELDS)
    assert artifact.constitutional_effect_created is False
    assert artifact.g70_handoff_created is False
    assert artifact.production_connection_created is False
    with pytest.raises(FrozenInstanceError):
        artifact.target_revision = 2  # type: ignore[misc]
    with pytest.raises(TypeError):
        artifact.policy_definition[ADMISSION_AUTHORITY] = "OTHER"  # type: ignore[index]


@pytest.mark.parametrize(
    ("authority_kind", "expected_outcome", "artifact_created"),
    (
        (APPROVAL, APPROVE_EXACT_POLICY_DEFINITION, True),
        (REWORK, MODIFY_AND_RESUBMIT, False),
        (REJECT, DECLINE, False),
        (CANCEL, EXIT_WITHOUT_EFFECT, False),
    ),
)
def test_existing_human_outcomes_are_reused_with_exact_effects(
    tmp_path: Path,
    authority_kind: str,
    expected_outcome: str,
    artifact_created: bool,
) -> None:
    _, _, continuation = _presentation(tmp_path)
    act, request = _act_and_request(
        continuation,
        authority_kind=authority_kind,
    )

    artifact = compose_step46_policy_definition_result_v1(
        human_authority_act=act,
        che_request=request,
        che_continuation=continuation,
    )

    assert STEP46_POLICY_OUTCOME_BY_AUTHORITY_KIND[authority_kind] == (
        expected_outcome
    )
    assert (artifact is not None) is artifact_created


@pytest.mark.parametrize("authority_kind", (APPROVAL, REWORK, REJECT, CANCEL))
def test_profile_round_trip_uses_existing_che_and_ends_before_g70(
    tmp_path: Path, authority_kind: str
) -> None:
    _, _, continuation = _presentation(tmp_path)
    act, request = _act_and_request(
        continuation,
        authority_kind=authority_kind,
    )

    response = submit_step46_policy_definition_decision_v1(
        request=request,
        continuation=continuation,
    )

    assert response.owner_status == (
        STEP46_POLICY_DEFINITION_RECORDED_STATUS
        if authority_kind == APPROVAL
        else STEP46_POLICY_DEFINITION_NO_EFFECT_STATUS
    )
    assert response.owner_transition.producing_owner == (
        STEP46_POLICY_DEFINITION_OWNER
    )
    assert response.owner_transition.permitted_controls == ()
    assert response.owner_transition.certification_reference_status == (
        REFERENCE_NOT_CREATED
    )
    assert response.continuation_envelope is not None
    assert response.continuation_envelope.continuation_state == (
        TERMINAL_CONTINUATION
    )


def test_consumed_continuation_and_replayed_authority_act_fail_closed(
    tmp_path: Path,
) -> None:
    _, _, continuation = _presentation(tmp_path)
    act, request = _act_and_request(continuation)
    submit_step46_policy_definition_decision_v1(
        request=request,
        continuation=continuation,
    )

    replay_request = replace(
        request,
        request_identity="STEP49-REPLAY-REQUEST",
        order_identity="STEP49-REPLAY-ORDER",
        idempotency_identity="STEP49-REPLAY-IDEMPOTENCY",
    )
    replay_act = replace(
        act,
        request_identity=replay_request.request_identity,
    )
    replay_request = replace(
        replay_request,
        source_payload=replay_act.to_dict(),
    )
    with pytest.raises(FailClosedRuntimeError, match="duplicate|stale|consumed"):
        submit_step46_policy_definition_decision_v1(
            request=replay_request,
            continuation=continuation,
        )


@pytest.mark.parametrize(
    ("field", "value", "message"),
    (
        ("authority_kind", "AUTHORIZATION", "outcome"),
        ("target_identity", "TASK-APPROVAL-TARGET", "target"),
        ("target_revision", 2, "revision"),
        ("expected_owner", "TASK_EXECUTION_OWNER", "owner"),
        ("authority_scope", "TASK_APPROVAL", "scope"),
        ("profile_authority_class", "TASK_APPROVAL", "authority class"),
    ),
)
def test_wrong_kind_target_revision_owner_scope_or_authority_class_fails_closed(
    tmp_path: Path, field: str, value, message: str
) -> None:
    _, _, continuation = _presentation(tmp_path)
    kwargs = {field: value}
    act, request = _act_and_request(continuation, **kwargs)

    with pytest.raises(FailClosedRuntimeError, match=message):
        compose_step46_policy_definition_result_v1(
            human_authority_act=act,
            che_request=request,
            che_continuation=continuation,
        )


@pytest.mark.parametrize(
    "payload",
    (
        {},
        {
            ADMISSION_AUTHORITY: "Human authority",
            RECOGNITION_ONLY_PREDICATE: "Exact recognition predicate",
            ADMISSION_ARTIFACT_AND_EFFECTIVE_STATE: "Effective artifact",
            INDEPENDENT_CERTIFIER: "Independent certifier",
        },
        {
            **_policy_payload(),
            CERTIFICATION_ARTIFACT: "UNKNOWN",
        },
        {
            **_policy_payload(),
            ADMISSION_AUTHORITY: " ",
        },
    ),
)
def test_missing_ambiguous_or_defaulted_policy_content_fails_closed(payload) -> None:
    with pytest.raises(FailClosedRuntimeError):
        validate_step46_policy_definition_payload_v1(payload)


def test_wrong_payload_and_artifact_digests_fail_closed(tmp_path: Path) -> None:
    _, _, continuation = _presentation(tmp_path)
    act, request = _act_and_request(continuation)
    with pytest.raises(FailClosedRuntimeError, match="payload digest"):
        replace(act, payload_digest="sha256:" + ("0" * 64))

    artifact = compose_step46_policy_definition_result_v1(
        human_authority_act=act,
        che_request=request,
        che_continuation=continuation,
    )
    assert artifact is not None
    with pytest.raises(FailClosedRuntimeError, match="identity"):
        validate_step46_policy_definition_decision_artifact_v1(
            replace(artifact, artifact_digest="sha256:" + ("0" * 64))
        )


def test_ai_or_caller_policy_without_human_act_fails_closed(
    tmp_path: Path,
) -> None:
    _, _, continuation = _presentation(tmp_path)
    _, request = _act_and_request(continuation)

    with pytest.raises(FailClosedRuntimeError):
        compose_step46_policy_definition_result_v1(
            human_authority_act=_policy_payload(),
            che_request=request,
            che_continuation=continuation,
        )


def test_task_approval_artifact_cannot_satisfy_step46_profile(
    tmp_path: Path,
) -> None:
    _, _, continuation = _presentation(tmp_path)
    task_approval = {
        "artifact_type": HUMAN_APPROVAL_ARTIFACT_V1,
        "approval_id": "SYNTHETIC-TASK-APPROVAL",
        "approval_status": APPROVED,
        "approval_granted": True,
        "source_ppp_candidate": "SYNTHETIC-PPP",
        "source_ppp_candidate_hash": "sha256:" + ("1" * 64),
        "approval_scope": "CREATE_IMPLEMENTATION_REQUEST_ONLY",
        "implementation_execution_allowed": False,
        "approved_by": "SYNTHETIC-HUMAN",
        "approved_at": CREATED_AT,
        "replay_visible": True,
    }
    task_approval["artifact_hash"] = replay_hash(task_approval)
    _, request = _act_and_request(continuation)

    with pytest.raises(FailClosedRuntimeError):
        compose_step46_policy_definition_result_v1(
            human_authority_act=task_approval,
            che_request=request,
            che_continuation=continuation,
        )


def test_step46_artifact_cannot_satisfy_task_approval(tmp_path: Path) -> None:
    artifact = _artifact(tmp_path)
    candidate = {
        "ppp_candidate_id": "SYNTHETIC-PPP",
        "artifact_hash": "sha256:" + ("1" * 64),
    }

    with pytest.raises(FailClosedRuntimeError):
        _validate_human_approval(artifact.to_dict(), candidate)


def test_step46_artifact_cannot_directly_satisfy_g70_04(
    tmp_path: Path,
) -> None:
    artifact = _artifact(tmp_path)

    with pytest.raises(FailClosedRuntimeError):
        validate_constitutional_human_ratification_artifact_v1(
            artifact.to_dict()
        )


def test_g70_04_ratification_artifact_cannot_satisfy_step46_profile(
    tmp_path: Path,
) -> None:
    package = materialize_g76_revision_4_ratification_package_v1(
        REPOSITORY_ROOT
    )
    presentation_request = create_canonical_hic_text_request_v1(
        profile=CLIA_CONFORMANCE_PROFILE_V1,
        actor_identity="STEP49-SYNTHETIC-G70-HUMAN",
        session_identity="STEP49-SYNTHETIC-G70-SESSION",
        workspace_identity=str(REPOSITORY_ROOT),
        runtime_scope_identity=str(tmp_path / "g70-runtime"),
        request_identity="STEP49-SYNTHETIC-G70-PRESENTATION-REQUEST",
        source_act_identity="STEP49-SYNTHETIC-G70-PRESENTATION-ACT",
        order_identity="STEP49-SYNTHETIC-G70-PRESENTATION-ORDER",
        idempotency_identity="STEP49-SYNTHETIC-G70-PRESENTATION-IDEMPOTENCY",
        exact_text=G76_REVISION_4_PRESENTATION_COMMAND,
        created_at=CREATED_AT,
    )
    presentation = present_g76_revision_4_ratification_boundary_v1(
        package=package,
        request=presentation_request,
    )
    continuation = presentation.continuation_envelope
    assert continuation is not None
    payload = constitutional_ratification_payload_v1(package.impact_assessment)
    act = CanonicalHumanAuthorityActV1(
        contract_version=CANONICAL_HUMAN_AUTHORITY_ACT_CONTRACT_VERSION,
        authority_act_identity="STEP49-SYNTHETIC-G70-HUMAN-ACT",
        authority_kind=APPROVAL,
        interaction_identity=continuation.interaction_identity,
        conversation_identity=continuation.conversation_identity,
        session_identity=continuation.session_identity,
        actor_identity=continuation.actor_identity,
        request_identity="STEP49-SYNTHETIC-G70-HUMAN-REQUEST",
        continuation_identity=continuation.continuation_identity,
        target_identity=package.impact_assessment.assessment_identity,
        target_revision=4,
        producing_owner=HUMAN_AUTHORITY_OWNER,
        expected_owner=STEP46_POLICY_DEFINITION_OWNER,
        authority_scope=CONSTITUTIONAL_AMENDMENT_RATIFICATION_SCOPE,
        payload=payload,
        payload_digest=canonical_human_authority_payload_digest_v1(payload),
        metadata={"test_fixture": "SYNTHETIC_NON_AUTHORITATIVE"},
    )
    request = create_canonical_hic_human_authority_act_request_v1(
        profile=CLIA_CONFORMANCE_PROFILE_V1,
        human_authority_act=act,
        continuation=continuation,
        request_identity=act.request_identity,
        order_identity="STEP49-SYNTHETIC-G70-HUMAN-ORDER",
        idempotency_identity="STEP49-SYNTHETIC-G70-HUMAN-IDEMPOTENCY",
        created_at=CREATED_AT,
    )
    ratification = compose_g76_revision_4_human_ratification_v1(
        package=package,
        human_authority_act=act,
        che_request=request,
        che_continuation=continuation,
    )

    with pytest.raises(FailClosedRuntimeError):
        validate_step46_policy_definition_decision_artifact_v1(ratification)


def test_profile_cannot_select_or_widen_its_authority(tmp_path: Path) -> None:
    artifact = _artifact(tmp_path)
    raw = artifact.to_dict()
    raw["profile_authority_class"] = "GENERAL_CONSTITUTIONAL_AUTHORITY"
    raw["authority_scope"] = "GENERAL_CONSTITUTIONAL_POLICY"
    raw["target_identity"] = "ANY_CONSTITUTIONAL_TARGET"

    with pytest.raises(FailClosedRuntimeError):
        validate_step46_policy_definition_decision_artifact_v1(raw)


def test_repository_profile_contains_no_task_or_g70_upcast_entrypoint() -> None:
    source = (
        REPOSITORY_ROOT
        / "aigol/runtime/constitutional_policy_definition_profile_v1.py"
    ).read_text(encoding="utf-8")

    assert "create_governed_implementation_request" not in source
    assert "create_constitutional_human_ratification_v1" not in source
    assert "G70_04" not in source
    assert "production_connection_created: bool = False" in source
