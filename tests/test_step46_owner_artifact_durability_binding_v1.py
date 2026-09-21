"""Step62 complete Step46 owner-artifact durability proof."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aigol.runtime import constitutional_policy_definition_profile_v1 as profile
from aigol.runtime import human_interface_runtime_entry_service as che_service
from aigol.runtime.canonical_che_evidence_correlation_contract_v1 import (
    canonical_che_evidence_correlation_record_path_v1,
    read_canonical_che_evidence_correlation_v1,
)
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
    CanonicalHumanAuthorityActV1,
    canonical_human_authority_payload_digest_v1,
)
from aigol.runtime.canonical_human_entry_contract_v1 import (
    TERMINAL_CONTINUATION,
    TERMINAL_RESPONSE,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize


CREATED_AT = "2026-09-21T12:00:00Z"
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _policy_payload() -> dict[str, str]:
    return {
        profile.ADMISSION_AUTHORITY: "HUMAN_CONSTITUTIONAL_ADMISSION_AUTHORITY",
        profile.RECOGNITION_ONLY_PREDICATE: (
            "Recognize only an exact independently certified admission artifact."
        ),
        profile.ADMISSION_ARTIFACT_AND_EFFECTIVE_STATE: (
            "STEP46_ADMISSION_ARTIFACT_V1 in EFFECTIVE_CERTIFIED state"
        ),
        profile.INDEPENDENT_CERTIFIER: "INDEPENDENT_CONSTITUTIONAL_CERTIFIER",
        profile.CERTIFICATION_ARTIFACT: (
            "STEP46_POLICY_CERTIFICATION_ARTIFACT_V1"
        ),
    }


def _prepared_step46(
    runtime_root: Path,
    *,
    authority_kind: str = APPROVAL,
):
    presentation_request = create_canonical_hic_text_request_v1(
        profile=CLIA_CONFORMANCE_PROFILE_V1,
        actor_identity="STEP62-SYNTHETIC-HUMAN",
        session_identity="STEP62-SYNTHETIC-SESSION",
        workspace_identity=str(REPOSITORY_ROOT),
        runtime_scope_identity=str(runtime_root),
        request_identity="STEP62-PRESENTATION-REQUEST",
        source_act_identity="STEP62-PRESENTATION-ACT",
        order_identity="STEP62-PRESENTATION-ORDER",
        idempotency_identity="STEP62-PRESENTATION-IDEMPOTENCY",
        exact_text=profile.STEP46_POLICY_DEFINITION_PRESENTATION_COMMAND,
        created_at=CREATED_AT,
    )
    presentation = profile.present_step46_policy_definition_boundary_v1(
        request=presentation_request,
        target_revision=1,
    )
    continuation = presentation.continuation_envelope
    assert continuation is not None
    payload = _policy_payload()
    act = CanonicalHumanAuthorityActV1(
        contract_version=CANONICAL_HUMAN_AUTHORITY_ACT_CONTRACT_VERSION,
        authority_act_identity="STEP62-SYNTHETIC-HUMAN-ACT",
        authority_kind=authority_kind,
        interaction_identity=continuation.interaction_identity,
        conversation_identity=continuation.conversation_identity,
        session_identity=continuation.session_identity,
        actor_identity=continuation.actor_identity,
        request_identity="STEP62-HUMAN-REQUEST",
        continuation_identity=continuation.continuation_identity,
        target_identity=profile.STEP46_POLICY_DEFINITION_TARGET,
        target_revision=continuation.expected_owner_revision,
        producing_owner=HUMAN_AUTHORITY_OWNER,
        expected_owner=profile.STEP46_POLICY_DEFINITION_OWNER,
        authority_scope=profile.STEP46_POLICY_DEFINITION_SCOPE,
        payload=payload,
        payload_digest=canonical_human_authority_payload_digest_v1(payload),
        metadata={
            "profile_contract_version": (
                profile.STEP46_POLICY_DEFINITION_PROFILE_VERSION
            ),
            "profile_authority_class": (
                profile.STEP46_POLICY_DEFINITION_AUTHORITY_CLASS
            ),
            "test_fixture": "SYNTHETIC_NON_AUTHORITATIVE",
        },
    )
    request = create_canonical_hic_human_authority_act_request_v1(
        profile=CLIA_CONFORMANCE_PROFILE_V1,
        human_authority_act=act,
        continuation=continuation,
        request_identity=act.request_identity,
        order_identity="STEP62-HUMAN-ORDER",
        idempotency_identity="STEP62-HUMAN-IDEMPOTENCY",
        created_at=CREATED_AT,
    )
    artifact = profile.compose_step46_policy_definition_result_v1(
        human_authority_act=act,
        che_request=request,
        che_continuation=continuation,
    )
    return act, request, continuation, artifact


def _correlation(runtime_root: Path, response):
    path = canonical_che_evidence_correlation_record_path_v1(
        str(runtime_root), response.correlation_identity
    )
    return read_canonical_che_evidence_correlation_v1(path)


def _delivery_record(request) -> dict:
    path = che_service._canonical_che_delivery_record_path_v1(
        runtime_scope_identity=request.runtime_scope_identity,
        actor_identity=request.actor_identity,
        session_identity=request.session_identity,
        workspace_identity=request.workspace_identity,
        idempotency_identity=request.idempotency_identity,
    )
    return json.loads(path.read_text(encoding="utf-8"))


def _continuation_record(runtime_root: Path, continuation) -> dict:
    path = che_service._canonical_che_continuation_binding_path(
        str(runtime_root), continuation.continuation_identity
    )
    return json.loads(path.read_text(encoding="utf-8"))


def test_success_persists_exact_complete_canonical_correlation_bound_artifact(
    tmp_path: Path,
) -> None:
    _, request, continuation, expected_artifact = _prepared_step46(tmp_path)
    assert expected_artifact is not None

    response = profile.submit_step46_policy_definition_decision_v1(
        request=request,
        continuation=continuation,
    )
    correlation = _correlation(tmp_path, response)
    path = profile.step46_owner_artifact_evidence_path_v1(
        str(tmp_path), expected_artifact.decision_identity
    )
    record = json.loads(path.read_text(encoding="utf-8"))
    restored = profile.read_step46_owner_artifact_evidence_v1(
        runtime_scope_identity=str(tmp_path),
        decision_identity=expected_artifact.decision_identity,
        correlation=correlation,
    )

    assert restored == expected_artifact
    assert record["owner"] == profile.STEP46_POLICY_DEFINITION_OWNER
    assert record["decision_identity"] == expected_artifact.decision_identity
    assert record["artifact_digest"] == expected_artifact.artifact_digest
    assert record["correlation_identity"] == response.correlation_identity
    assert record["canonical_artifact"] == (
        profile.serialize_step46_policy_definition_decision_v1(expected_artifact)
    )
    assert len(restored.to_dict()) == 21
    assert response.response_type == TERMINAL_RESPONSE
    assert response.continuation_envelope is not None
    assert response.continuation_envelope.continuation_state == TERMINAL_CONTINUATION


def test_owner_artifact_persistence_precedes_continuation_and_delivery_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, request, continuation, _ = _prepared_step46(tmp_path)
    events: list[str] = []
    original_persist = profile.persist_step46_owner_artifact_evidence_v1
    original_continuation = che_service._persist_canonical_che_continuation_v1
    original_commit = che_service._commit_canonical_che_delivery_response_v1

    def persist(**kwargs):
        events.append("owner_artifact")
        return original_persist(**kwargs)

    def persist_continuation(*args, **kwargs):
        events.append("terminal_continuation")
        return original_continuation(*args, **kwargs)

    def commit(*args, **kwargs):
        events.append("terminal_delivery")
        return original_commit(*args, **kwargs)

    monkeypatch.setattr(profile, "persist_step46_owner_artifact_evidence_v1", persist)
    monkeypatch.setattr(
        che_service,
        "_persist_canonical_che_continuation_v1",
        persist_continuation,
    )
    monkeypatch.setattr(
        che_service, "_commit_canonical_che_delivery_response_v1", commit
    )

    profile.submit_step46_policy_definition_decision_v1(
        request=request, continuation=continuation
    )

    assert events == [
        "owner_artifact",
        "terminal_continuation",
        "terminal_delivery",
    ]


def test_identical_persistence_and_delivery_replay_are_read_only_idempotent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, request, continuation, artifact = _prepared_step46(tmp_path)
    assert artifact is not None
    calls = 0
    original_compose = profile.compose_step46_policy_definition_result_v1

    def compose(**kwargs):
        nonlocal calls
        calls += 1
        return original_compose(**kwargs)

    monkeypatch.setattr(profile, "compose_step46_policy_definition_result_v1", compose)
    first = profile.submit_step46_policy_definition_decision_v1(
        request=request, continuation=continuation
    )
    correlation = _correlation(tmp_path, first)
    first_binding = _continuation_record(tmp_path, continuation)
    first_path = profile.persist_step46_owner_artifact_evidence_v1(
        artifact=artifact, correlation=correlation
    )
    second_path = profile.persist_step46_owner_artifact_evidence_v1(
        artifact=artifact, correlation=correlation
    )
    second = profile.submit_step46_policy_definition_decision_v1(
        request=request, continuation=continuation
    )

    assert calls == 1
    assert first_path == second_path
    assert second.to_dict() == first.to_dict()
    assert _continuation_record(tmp_path, continuation) == first_binding


def test_divergent_record_for_same_decision_identity_fails_closed(
    tmp_path: Path,
) -> None:
    _, request, continuation, artifact = _prepared_step46(tmp_path)
    assert artifact is not None
    response = profile.submit_step46_policy_definition_decision_v1(
        request=request, continuation=continuation
    )
    correlation = _correlation(tmp_path, response)
    path = profile.step46_owner_artifact_evidence_path_v1(
        str(tmp_path), artifact.decision_identity
    )
    record = json.loads(path.read_text(encoding="utf-8"))
    record["correlation_identity"] = "CHE-CORRELATION-DIVERGENT"
    record["record_integrity_digest"] = (
        profile._step46_owner_artifact_record_integrity_digest_v1(record)
    )
    path.write_text(canonical_serialize(record) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="binding|conflict"):
        profile.persist_step46_owner_artifact_evidence_v1(
            artifact=artifact, correlation=correlation
        )


def test_write_failure_prevents_terminal_receipt_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, request, continuation, _ = _prepared_step46(tmp_path)

    def fail_link(*_args, **_kwargs):
        raise OSError("synthetic write failure")

    monkeypatch.setattr(profile.os, "link", fail_link)
    with pytest.raises(FailClosedRuntimeError, match="write failed"):
        profile.submit_step46_policy_definition_decision_v1(
            request=request, continuation=continuation
        )

    assert _delivery_record(request)["delivery_state"] != (
        che_service._DELIVERY_RECORD_COMMITTED
    )


def test_readback_failure_prevents_terminal_receipt_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, request, continuation, _ = _prepared_step46(tmp_path)

    def fail_readback(*_args, **_kwargs):
        raise FailClosedRuntimeError("synthetic read-back failure")

    monkeypatch.setattr(
        profile, "_read_step46_owner_artifact_evidence_record_v1", fail_readback
    )
    with pytest.raises(FailClosedRuntimeError, match="read-back"):
        profile.submit_step46_policy_definition_decision_v1(
            request=request, continuation=continuation
        )

    assert _delivery_record(request)["delivery_state"] != (
        che_service._DELIVERY_RECORD_COMMITTED
    )


def test_post_artifact_failure_leaves_evidence_only_orphan_and_no_retry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, request, continuation, artifact = _prepared_step46(tmp_path)
    assert artifact is not None
    calls = 0
    original_compose = profile.compose_step46_policy_definition_result_v1

    def compose(**kwargs):
        nonlocal calls
        calls += 1
        return original_compose(**kwargs)

    def fail_terminal_continuation(*_args, **_kwargs):
        raise FailClosedRuntimeError("synthetic post-artifact crash")

    monkeypatch.setattr(profile, "compose_step46_policy_definition_result_v1", compose)
    monkeypatch.setattr(
        che_service,
        "_persist_canonical_che_continuation_v1",
        fail_terminal_continuation,
    )
    with pytest.raises(FailClosedRuntimeError, match="post-artifact"):
        profile.submit_step46_policy_definition_decision_v1(
            request=request, continuation=continuation
        )

    assert profile.step46_owner_artifact_evidence_path_v1(
        str(tmp_path), artifact.decision_identity
    ).is_file()
    assert _delivery_record(request)["delivery_state"] != (
        che_service._DELIVERY_RECORD_COMMITTED
    )

    resolution = profile.submit_step46_policy_definition_decision_v1(
        request=request, continuation=continuation
    )
    assert calls == 1
    assert resolution.response_type != TERMINAL_RESPONSE
    assert _delivery_record(request)["delivery_state"] != (
        che_service._DELIVERY_RECORD_COMMITTED
    )


def test_corrupt_or_missing_durable_artifact_blocks_receipt_reauthentication(
    tmp_path: Path,
) -> None:
    _, request, continuation, artifact = _prepared_step46(tmp_path)
    assert artifact is not None
    profile.submit_step46_policy_definition_decision_v1(
        request=request, continuation=continuation
    )
    path = profile.step46_owner_artifact_evidence_path_v1(
        str(tmp_path), artifact.decision_identity
    )
    path.write_text("{}\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="record is invalid"):
        profile.submit_step46_policy_definition_decision_v1(
            request=request, continuation=continuation
        )


def test_wrong_runtime_scope_correlation_fails_existing_artifact_validation(
    tmp_path: Path,
) -> None:
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    _, first_request, first_continuation, first_artifact = _prepared_step46(
        first_root
    )
    _, second_request, second_continuation, _ = _prepared_step46(second_root)
    assert first_artifact is not None
    profile.submit_step46_policy_definition_decision_v1(
        request=first_request, continuation=first_continuation
    )
    second_response = profile.submit_step46_policy_definition_decision_v1(
        request=second_request, continuation=second_continuation
    )
    second_correlation = _correlation(second_root, second_response)

    with pytest.raises(FailClosedRuntimeError, match="correlation binding"):
        profile.persist_step46_owner_artifact_evidence_v1(
            artifact=first_artifact,
            correlation=second_correlation,
        )


def test_no_effect_and_public_consumer_schemas_remain_unchanged(
    tmp_path: Path,
) -> None:
    approval_root = tmp_path / "approval"
    _, request, continuation, artifact = _prepared_step46(approval_root)
    assert artifact is not None
    response = profile.submit_step46_policy_definition_decision_v1(
        request=request, continuation=continuation
    )
    public_bytes = canonical_serialize(response.to_dict())
    delivery = _delivery_record(request)

    assert "decision_artifact" not in public_bytes
    assert artifact.artifact_digest not in public_bytes
    assert set(delivery) == che_service._DELIVERY_RESOLUTION_RECORD_FIELDS
    assert set(response.continuation_envelope.to_dict()) == {
        "contract_version",
        "continuation_identity",
        "interaction_identity",
        "conversation_identity",
        "session_identity",
        "actor_identity",
        "workspace_identity",
        "runtime_scope_identity",
        "request_identity",
        "previous_response_identity",
        "previous_order_identity",
        "previous_idempotency_identity",
        "continuation_sequence",
        "expected_next_act_identity",
        "expected_owner_state_identity",
        "expected_owner_revision",
        "continuation_state",
        "correlation_identity",
        "metadata",
    }

    no_effect_root = tmp_path / "no-effect"
    _, no_effect_request, no_effect_continuation, no_effect_artifact = (
        _prepared_step46(no_effect_root, authority_kind=CANCEL)
    )
    assert no_effect_artifact is None
    profile.submit_step46_policy_definition_decision_v1(
        request=no_effect_request,
        continuation=no_effect_continuation,
    )
    assert not (
        no_effect_root / profile.STEP46_OWNER_ARTIFACT_EVIDENCE_DIRECTORY
    ).exists()
