from copy import deepcopy

from agol_bridge.chatgpt_ingress import (
    ACCEPTED_AS_SEMANTIC_INPUT,
    ARTIFACT_TYPE,
    BOUNDARY_STATEMENT,
    REJECTED,
    create_chatgpt_ingress_artifact,
    validate_chatgpt_ingress_artifact,
)


def _artifact():
    return create_chatgpt_ingress_artifact(
        created_at="1970-01-01T00:00:00Z",
        session_id="CHATGPT-INGRESS-SESSION-1",
        human_request="Review the governed transport plan.",
        chatgpt_semantic_output="The request asks for an audit-only governed transport review.",
        normalized_intent="REVIEW_GOVERNED_TRANSPORT_PLAN",
        expected_artifacts=["audit summary"],
        constraints=["preserve governance boundaries"],
        forbidden_operations=["execution authorization", "provider dispatch"],
        provenance={"source_conversation_id": "CONV-1"},
    )


def _assert_rejected(artifact, field_fragment):
    validation = validate_chatgpt_ingress_artifact(artifact)
    assert validation["valid"] is False
    assert validation["status"] == REJECTED
    assert any(field_fragment in error["field"] or field_fragment in error["error"] for error in validation["errors"])


def test_valid_artifact_is_accepted_as_semantic_input():
    artifact = _artifact()
    validation = validate_chatgpt_ingress_artifact(artifact)

    assert artifact["artifact_type"] == ARTIFACT_TYPE
    assert validation["valid"] is True
    assert validation["status"] == ACCEPTED_AS_SEMANTIC_INPUT
    assert artifact["authority_boundary"]["boundary_statement"] == BOUNDARY_STATEMENT


def test_missing_required_field_is_rejected():
    artifact = _artifact()
    artifact.pop("human_request")

    _assert_rejected(artifact, "human_request")


def test_wrong_artifact_type_is_rejected():
    artifact = _artifact()
    artifact["artifact_type"] = "WRONG"

    _assert_rejected(artifact, "artifact_type")


def test_any_authority_flag_set_to_true_is_rejected():
    for flag in (
        "chatgpt_authority",
        "execution_authority",
        "governance_authority",
        "approval_authority",
        "provider_dispatch_authority",
        "autonomous_continuation_authority",
    ):
        artifact = _artifact()
        artifact["authority_boundary"][flag] = True
        _assert_rejected(artifact, flag)


def test_missing_boundary_statement_is_rejected():
    artifact = _artifact()
    artifact["authority_boundary"]["boundary_statement"] = ""

    _assert_rejected(artifact, "boundary_statement")


def test_provider_dispatch_field_is_rejected():
    artifact = _artifact()
    artifact["provider_dispatch"] = {"provider": "codex"}

    _assert_rejected(artifact, "provider_dispatch")


def test_execution_authorization_field_is_rejected():
    artifact = _artifact()
    artifact["execution_authorization"] = {"authorized": True}

    _assert_rejected(artifact, "execution_authorization")


def test_autonomous_continuation_field_is_rejected():
    artifact = _artifact()
    artifact["autonomous_continuation"] = True

    _assert_rejected(artifact, "autonomous_continuation")


def test_semantic_correctness_claim_is_rejected():
    artifact = _artifact()
    artifact["chatgpt_semantic_output"] = "This is semantically correct and ready."

    _assert_rejected(artifact, "semantic correctness")


def test_replay_identity_is_deterministic():
    first = _artifact()
    second = _artifact()

    assert first["replay_identity"] == second["replay_identity"]


def test_artifact_hash_is_deterministic():
    first = _artifact()
    second = _artifact()

    assert first["hashes"]["artifact_hash"] == second["hashes"]["artifact_hash"]


def test_mutated_artifact_hash_fails_validation():
    artifact = _artifact()
    mutated = deepcopy(artifact)
    mutated["normalized_intent"] = "MUTATED"

    _assert_rejected(mutated, "artifact_hash")


def test_provenance_missing_is_rejected():
    artifact = _artifact()
    artifact.pop("provenance")

    _assert_rejected(artifact, "provenance")


def test_validation_status_only_allows_accepted_or_rejected():
    artifact = _artifact()
    artifact["validation_status"] = "PENDING"

    _assert_rejected(artifact, "validation_status")

    rejected = _artifact()
    rejected["validation_status"] = REJECTED
    _assert_rejected(rejected, "validation_status")
