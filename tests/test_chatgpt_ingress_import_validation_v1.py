from copy import deepcopy
from pathlib import Path

from agol_bridge.chatgpt_ingress import create_chatgpt_ingress_artifact
from agol_bridge.chatgpt_ingress.ingress_import_validation import (
    ACCEPTED_FOR_STRUCTURAL_IMPORT,
    REJECTED,
    import_chatgpt_ingress_artifact,
)


MODULE = Path("agol_bridge/chatgpt_ingress/ingress_import_validation.py")


def _artifact():
    return create_chatgpt_ingress_artifact(
        created_at="1970-01-01T00:00:00Z",
        session_id="CHATGPT-IMPORT-SESSION-1",
        human_request="Review semantic ingress continuity.",
        chatgpt_semantic_output="The request asks for structural ingress continuity only.",
        normalized_intent="REVIEW_SEMANTIC_INGRESS_CONTINUITY",
        expected_artifacts=["structural import report"],
        constraints=["import only", "no execution"],
        forbidden_operations=["execution authorization", "provider dispatch", "autonomous continuation"],
        provenance={"source_conversation_id": "CONV-IMPORT-1"},
    )


def _imported():
    return import_chatgpt_ingress_artifact(_artifact())


def _assert_rejected(artifact, fragment):
    result = import_chatgpt_ingress_artifact(artifact)
    assert result["status"] == REJECTED
    assert result["governance_acceptance_report"]["status"] == REJECTED
    errors = result["ingress_validation"]["errors"]
    assert any(fragment in error["field"] or fragment in error["error"] for error in errors)
    assert result["execution_performed"] is False
    assert result["codex_dispatch_performed"] is False


def test_valid_ingress_artifact_imports_successfully():
    result = _imported()

    assert result["status"] == ACCEPTED_FOR_STRUCTURAL_IMPORT
    assert result["governance_acceptance_report"]["status"] == ACCEPTED_FOR_STRUCTURAL_IMPORT
    assert result["import_only"] is True
    assert result["execution_performed"] is False


def test_invalid_ingress_artifact_rejected():
    artifact = _artifact()
    artifact["artifact_type"] = "INVALID"

    _assert_rejected(artifact, "artifact_type")


def test_proposal_candidate_generated_deterministically():
    first = _imported()["semantic_proposal_candidate"]
    second = _imported()["semantic_proposal_candidate"]

    assert first == second
    assert first["proposal_candidate_only"] is True
    assert first["execution_authority"] is False
    assert first["governance_authority"] is False
    assert first["codex_dispatch_allowed"] is False
    assert first["autonomous_continuation_allowed"] is False


def test_contract_candidate_generated_deterministically():
    first = _imported()["semantic_contract_candidate"]
    second = _imported()["semantic_contract_candidate"]

    assert first == second
    assert first["contract_candidate_only"] is True
    assert first["semantic_correctness_verified"] is False
    assert first["governance_approved"] is False
    assert first["execution_authorized"] is False
    assert first["provider_dispatch_authorized"] is False


def test_governance_report_generated_deterministically():
    first = _imported()["governance_acceptance_report"]
    second = _imported()["governance_acceptance_report"]

    assert first == second
    assert first["import_only"] is True
    assert first["semantic_correctness_verified"] is False


def test_replay_identity_preserved():
    artifact = _artifact()
    result = import_chatgpt_ingress_artifact(artifact)

    assert result["semantic_proposal_candidate"]["replay_identity"] == artifact["replay_identity"]
    assert result["semantic_contract_candidate"]["replay_identity"] == artifact["replay_identity"]
    assert result["governance_acceptance_report"]["replay_identity"] == artifact["replay_identity"]


def test_ingress_hash_preserved():
    artifact = _artifact()
    ingress_hash = artifact["hashes"]["artifact_hash"]
    result = import_chatgpt_ingress_artifact(artifact)

    assert result["semantic_proposal_candidate"]["hashes"]["ingress_artifact_hash"] == ingress_hash
    assert result["governance_acceptance_report"]["preserved_hashes"]["ingress_artifact_hash"] == ingress_hash


def test_proposal_candidate_hash_deterministic():
    first = _imported()["semantic_proposal_candidate"]["proposal_candidate_hash"]
    second = _imported()["semantic_proposal_candidate"]["proposal_candidate_hash"]

    assert first == second
    assert first.startswith("sha256:")


def test_contract_candidate_hash_deterministic():
    first = _imported()["semantic_contract_candidate"]["contract_candidate_hash"]
    second = _imported()["semantic_contract_candidate"]["contract_candidate_hash"]

    assert first == second
    assert first.startswith("sha256:")


def test_governance_report_hash_deterministic():
    first = _imported()["governance_acceptance_report"]["governance_report_hash"]
    second = _imported()["governance_acceptance_report"]["governance_report_hash"]

    assert first == second
    assert first.startswith("sha256:")


def test_execution_authorization_claim_rejected():
    artifact = _artifact()
    artifact["execution_authorization"] = {"authorized": True}

    _assert_rejected(artifact, "execution_authorization")


def test_provider_dispatch_claim_rejected():
    artifact = _artifact()
    artifact["provider_dispatch"] = {"provider": "codex"}

    _assert_rejected(artifact, "provider_dispatch")


def test_semantic_correctness_claim_rejected():
    artifact = _artifact()
    artifact["chatgpt_semantic_output"] = "Semantic correctness verified."

    _assert_rejected(artifact, "semantic correctness")


def test_governance_approval_claim_rejected():
    artifact = _artifact()
    artifact["chatgpt_semantic_output"] = "Governance approved."

    _assert_rejected(artifact, "governance approved")


def test_codex_dispatch_never_occurs():
    result = _imported()
    source = MODULE.read_text(encoding="utf-8").lower()

    assert result["codex_dispatch_performed"] is False
    assert result["governance_acceptance_report"]["codex_dispatch_performed"] is False
    assert "codex_cli_provider" not in source
    assert "run_bounded_codex_cli_task" not in source
    assert "subprocess" not in source


def test_import_pipeline_remains_structural_only():
    result = _imported()
    proposal = result["semantic_proposal_candidate"]
    contract = result["semantic_contract_candidate"]
    report = result["governance_acceptance_report"]

    assert proposal["classification"] == "STRUCTURAL_ONLY"
    assert contract["classification"] == "STRUCTURAL_ONLY"
    assert report["structural_continuity"]["downstream_runtime_connected"] is False
    assert report["structural_continuity"]["provider_invoked"] is False
    assert report["structural_continuity"]["governance_mutated"] is False


def test_mutated_hash_rejected_by_import_pipeline():
    artifact = deepcopy(_artifact())
    artifact["normalized_intent"] = "MUTATED"

    _assert_rejected(artifact, "artifact_hash")
