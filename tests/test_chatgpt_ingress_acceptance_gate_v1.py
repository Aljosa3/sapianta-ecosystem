from copy import deepcopy
from pathlib import Path

from agol_bridge.chatgpt_ingress import create_chatgpt_ingress_artifact
from agol_bridge.chatgpt_ingress.ingress_acceptance_gate import (
    ACCEPTED_FOR_GOVERNED_PREVIEW,
    ALLOWED_GATE_STATUSES,
    REJECTED_BY_GOVERNANCE_GATE,
    evaluate_chatgpt_ingress_acceptance_gate,
    evaluate_import_acceptance_gate,
)
from agol_bridge.chatgpt_ingress.ingress_import_validation import import_chatgpt_ingress_artifact


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "browser_companion" / "sidepanel.html"
JS = ROOT / "browser_companion" / "sidepanel.js"
MODULE = ROOT / "agol_bridge" / "chatgpt_ingress" / "ingress_acceptance_gate.py"


def _artifact():
    return create_chatgpt_ingress_artifact(
        created_at="1970-01-01T00:00:00Z",
        session_id="CHATGPT-GATE-SESSION-1",
        human_request="Review governed semantic ingress.",
        chatgpt_semantic_output="The request asks for admissibility-only semantic ingress.",
        normalized_intent="REVIEW_GOVERNED_SEMANTIC_INGRESS",
        expected_artifacts=["acceptance gate decision evidence"],
        constraints=["gate only", "no execution"],
        forbidden_operations=["execution authorization", "provider dispatch", "autonomous continuation"],
        provenance={"source_conversation_id": "CONV-GATE-1"},
    )


def _gate(artifact=None):
    return evaluate_chatgpt_ingress_acceptance_gate(artifact or _artifact())


def _decision(artifact=None):
    return _gate(artifact)["decision_evidence"]


def _assert_rejected(artifact, fragment):
    result = _gate(artifact)
    evidence = result["decision_evidence"]
    assert result["gate_status"] == REJECTED_BY_GOVERNANCE_GATE
    assert evidence["gate_status"] == REJECTED_BY_GOVERNANCE_GATE
    assert any(fragment in reason for reason in evidence["rejection_reasons"])
    assert evidence["execution_authorized"] is False
    assert evidence["codex_dispatch_authorized"] is False


def _preview_section() -> str:
    html = HTML.read_text(encoding="utf-8")
    start = html.index('id="chatgpt-ingress-preview"')
    end = html.index('id="governed-execution-observatory"', start)
    return html[start:end]


def test_valid_imported_artifact_is_accepted_for_governed_preview():
    result = _gate()

    assert result["gate_status"] == ACCEPTED_FOR_GOVERNED_PREVIEW
    assert result["decision_evidence"]["gate_status"] == ACCEPTED_FOR_GOVERNED_PREVIEW


def test_invalid_imported_artifact_is_rejected():
    artifact = _artifact()
    artifact["artifact_type"] = "INVALID"

    _assert_rejected(artifact, "artifact_type")


def test_authority_violation_is_rejected():
    artifact = _artifact()
    artifact["authority_boundary"]["execution_authority"] = True

    _assert_rejected(artifact, "execution_authority")


def test_execution_claim_is_rejected():
    artifact = _artifact()
    artifact["execution_authorization"] = {"authorized": True}

    _assert_rejected(artifact, "execution_authorization")


def test_provider_dispatch_claim_is_rejected():
    artifact = _artifact()
    artifact["provider_dispatch"] = {"provider": "codex"}

    _assert_rejected(artifact, "provider_dispatch")


def test_semantic_correctness_claim_is_rejected():
    artifact = _artifact()
    artifact["chatgpt_semantic_output"] = "Semantic correctness verified."

    _assert_rejected(artifact, "semantic correctness")


def test_governance_approval_claim_is_rejected():
    artifact = _artifact()
    artifact["chatgpt_semantic_output"] = "Governance approved."

    _assert_rejected(artifact, "governance approved")


def test_missing_replay_identity_is_rejected():
    artifact = _artifact()
    artifact["replay_identity"] = ""

    _assert_rejected(artifact, "replay_identity")


def test_missing_provenance_is_rejected():
    artifact = _artifact()
    artifact.pop("provenance")

    _assert_rejected(artifact, "provenance")


def test_invalid_hash_continuity_is_rejected():
    artifact = deepcopy(_artifact())
    artifact["normalized_intent"] = "MUTATED"

    _assert_rejected(artifact, "artifact_hash")


def test_gate_status_only_allows_accepted_rejected_values():
    assert ALLOWED_GATE_STATUSES == (
        ACCEPTED_FOR_GOVERNED_PREVIEW,
        REJECTED_BY_GOVERNANCE_GATE,
    )
    assert _gate()["gate_status"] in ALLOWED_GATE_STATUSES


def test_decision_hash_is_deterministic():
    first = _decision()["decision_hash"]
    second = _decision()["decision_hash"]

    assert first == second
    assert first.startswith("sha256:")


def test_decision_evidence_contains_authority_checks():
    evidence = _decision()

    assert "authority_boundary_check" in evidence
    assert evidence["authority_boundary_check"]["passed"] is True


def test_decision_evidence_contains_replay_continuity_check():
    evidence = _decision()

    assert "replay_continuity_check" in evidence
    assert evidence["replay_continuity_check"]["passed"] is True


def test_decision_evidence_contains_provenance_check():
    evidence = _decision()

    assert "provenance_check" in evidence
    assert evidence["provenance_check"]["passed"] is True


def test_decision_evidence_contains_hash_integrity_check():
    evidence = _decision()

    assert "hash_integrity_check" in evidence
    assert evidence["hash_integrity_check"]["passed"] is True


def test_gate_never_authorizes_execution():
    evidence = _decision()

    assert evidence["execution_authorized"] is False
    assert evidence["execution_boundary_check"]["passed"] is True


def test_gate_never_authorizes_codex_dispatch():
    evidence = _decision()

    assert evidence["codex_dispatch_authorized"] is False
    assert evidence["provider_dispatch_authorized"] is False
    assert evidence["provider_dispatch_check"]["passed"] is True


def test_gate_never_authorizes_autonomous_continuation():
    evidence = _decision()

    assert evidence["autonomous_continuation_authorized"] is False
    assert evidence["autonomous_continuation_check"]["passed"] is True


def test_gate_rejects_broken_candidate_continuity():
    import_result = import_chatgpt_ingress_artifact(_artifact())
    import_result["semantic_contract_candidate"]["contract_candidate_hash"] = "BROKEN"
    evidence = evaluate_import_acceptance_gate(import_result)

    assert evidence["gate_status"] == REJECTED_BY_GOVERNANCE_GATE
    assert evidence["hash_integrity_check"]["passed"] is False


def test_cockpit_displays_acceptance_gate_result():
    combined = "\n".join((HTML.read_text(encoding="utf-8"), JS.read_text(encoding="utf-8")))

    assert 'id="chatgpt-ingress-acceptance-gate-card"' in combined
    assert "ACCEPTED_FOR_GOVERNED_PREVIEW" in combined
    assert "REJECTED_BY_GOVERNANCE_GATE" in combined


def test_cockpit_displays_decision_hash():
    combined = "\n".join((HTML.read_text(encoding="utf-8"), JS.read_text(encoding="utf-8")))

    assert "decision_hash:" in combined
    assert "CHATGPT-INGRESS-ACCEPTANCE-GATE-DECISION-HASH" in combined


def test_cockpit_displays_no_execution_no_codex_dispatch():
    section = _preview_section()

    assert "NO EXECUTION" in section
    assert "NO CODEX DISPATCH" in section


def test_cockpit_contains_no_execution_button_in_ingress_gate_section():
    section = _preview_section().lower()
    gate_start = section.index('id="chatgpt-ingress-acceptance-gate-card"')
    gate_fragment = section[gate_start - 260 : gate_start + 600]

    assert "<button" not in gate_fragment
    assert "run" not in gate_fragment
    assert "execute" not in gate_fragment
    assert "send to codex" not in gate_fragment
    assert "approve execution" not in gate_fragment


def test_gate_module_has_no_execution_provider_or_native_messaging_calls():
    source = MODULE.read_text(encoding="utf-8").lower()

    assert "codex_cli_provider" not in source
    assert "run_bounded_codex_cli_task" not in source
    assert "subprocess" not in source
    assert "sendnativemessage" not in source
    assert "native_messaging" not in source
