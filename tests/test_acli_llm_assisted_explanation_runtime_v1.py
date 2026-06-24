"""Tests for ACLI_LLM_ASSISTED_EXPLANATION_PROTOTYPE_V1."""

from __future__ import annotations

import pytest

from aigol.runtime.acli_llm_assisted_explanation_runtime import (
    DETERMINISTIC_FALLBACK_USED,
    PROVIDER_EXPLANATION_USED,
    authoritative_state_from_acli_proposal_capture,
    create_acli_llm_assisted_explanation,
    reconstruct_acli_llm_assisted_explanation_replay,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-06-24T00:00:00Z"


def _proposal_capture() -> dict:
    proposal_artifact = {
        "artifact_type": "GOVERNED_DEVELOPMENT_PROPOSAL_ARTIFACT_V1",
        "proposal_id": "PROPOSAL-001",
        "governance_artifact_proposal": {
            "artifact_title": "ACLI_USAGE_GUIDELINES_V1",
            "target_path": "docs/governance/ACLI_USAGE_GUIDELINES_V1.md",
        },
    }
    proposal_artifact["artifact_hash"] = replay_hash(proposal_artifact)
    capture = {
        "artifact_type": "ACLI_GOVERNED_DEVELOPMENT_BRIDGE_PROPOSAL_CAPTURE_V1",
        "bridge_id": "BRIDGE-001",
        "workflow_id": "GOVERNED_DEVELOPMENT_WORKFLOW",
        "bridge_status": "APPROVAL_REQUIRED",
        "proposal_artifact": proposal_artifact,
        "proposal_naming_decision": {
            "requested_artifact_identifier": "ACLI_USAGE_GUIDELINES_V1",
            "selected_artifact_identifier": "ACLI_USAGE_GUIDELINES_V1",
            "selected_target_path": "docs/governance/ACLI_USAGE_GUIDELINES_V1.md",
        },
        "target_paths": [
            "docs/governance/ACLI_USAGE_GUIDELINES_V1.md",
            "aigol/runtime/acli_governed_development_example.py",
        ],
        "replay_reference": "/tmp/replay/proposal",
        "approval_required": True,
        "approval_bypassed": False,
        "mutation_performed": False,
        "worker_invoked": False,
        "validation_executed": False,
    }
    capture["artifact_hash"] = replay_hash(capture)
    return capture


def _authoritative_state() -> dict:
    return authoritative_state_from_acli_proposal_capture(
        state_id="STATE-001",
        proposal_capture=_proposal_capture(),
        approval_state="APPROVAL_REQUIRED",
        replay_references=["/tmp/replay/routing", "/tmp/replay/explanation"],
        created_at=CREATED_AT,
    )


def _provider_response(request: dict) -> dict:
    state = request["authoritative_state"]
    return {
        "explanation_text": (
            "This proposal creates ACLI_USAGE_GUIDELINES_V1 and waits for human approval before any mutation."
        ),
        "preserved_artifact_identifiers": list(state["artifact_identifiers"]),
        "preserved_target_paths": list(state["target_paths"]),
        "preserved_approval_state": state["approval_state"],
        "preserved_replay_references": list(state["replay_references"]),
        "advisory_only": True,
        "authority_granted": False,
    }


def test_provider_assisted_explanation_is_generated_and_replayed(tmp_path) -> None:
    capture = create_acli_llm_assisted_explanation(
        explanation_id="EXPLANATION-001",
        authoritative_state=_authoritative_state(),
        deterministic_explanation="Deterministic explanation remains available.",
        provider=_provider_response,
        provider_id="TEST_EXPLANATION_PROVIDER",
        replay_dir=tmp_path / "llm_explanation",
        created_at=CREATED_AT,
    )

    artifact = capture["llm_assisted_explanation_artifact"]

    assert capture["explanation_status"] == PROVIDER_EXPLANATION_USED
    assert artifact["advisory_only"] is True
    assert artifact["authority_granted"] is False
    assert artifact["provider_authority"] is False
    assert artifact["approval_authority"] is False
    assert artifact["execution_authority"] is False
    assert artifact["explanation_request_artifact"]["authoritative_state"]["artifact_identifiers"] == [
        "ACLI_USAGE_GUIDELINES_V1"
    ]
    assert artifact["explanation_response_artifact"]["preserved_target_paths"] == [
        "docs/governance/ACLI_USAGE_GUIDELINES_V1.md",
        "aigol/runtime/acli_governed_development_example.py",
    ]

    replay = reconstruct_acli_llm_assisted_explanation_replay(
        capture["llm_assisted_explanation_replay_reference"]
    )
    assert replay["explanation_status"] == PROVIDER_EXPLANATION_USED
    assert replay["provider_explanation_used"] is True
    assert replay["authority_granted"] is False


def test_provider_unavailable_falls_back_to_deterministic_explanation(tmp_path) -> None:
    def unavailable(_request: dict) -> dict:
        raise RuntimeError("provider unavailable")

    capture = create_acli_llm_assisted_explanation(
        explanation_id="EXPLANATION-002",
        authoritative_state=_authoritative_state(),
        deterministic_explanation="Deterministic fallback explanation.",
        provider=unavailable,
        provider_id="UNAVAILABLE_PROVIDER",
        replay_dir=tmp_path / "fallback_explanation",
        created_at=CREATED_AT,
    )

    artifact = capture["llm_assisted_explanation_artifact"]

    assert capture["explanation_status"] == DETERMINISTIC_FALLBACK_USED
    assert capture["operator_explanation"] == "Deterministic fallback explanation."
    assert artifact["deterministic_fallback_used"] is True
    assert artifact["provider_explanation_used"] is False
    assert "EXPLANATION_PROVIDER_UNAVAILABLE" in artifact["fallback_reason"]
    assert artifact["authority_granted"] is False

    replay = reconstruct_acli_llm_assisted_explanation_replay(
        capture["llm_assisted_explanation_replay_reference"]
    )
    assert replay["deterministic_fallback_used"] is True


@pytest.mark.parametrize(
    "bad_response",
    [
        {
            "explanation_text": "Wrong artifact.",
            "preserved_artifact_identifiers": ["WRONG_ARTIFACT"],
            "preserved_target_paths": [
                "docs/governance/ACLI_USAGE_GUIDELINES_V1.md",
                "aigol/runtime/acli_governed_development_example.py",
            ],
            "preserved_approval_state": "APPROVAL_REQUIRED",
            "preserved_replay_references": ["/tmp/replay/routing", "/tmp/replay/explanation", "/tmp/replay/proposal"],
            "advisory_only": True,
            "authority_granted": False,
        },
        {
            "explanation_text": "Claims authority.",
            "preserved_artifact_identifiers": ["ACLI_USAGE_GUIDELINES_V1"],
            "preserved_target_paths": [
                "docs/governance/ACLI_USAGE_GUIDELINES_V1.md",
                "aigol/runtime/acli_governed_development_example.py",
            ],
            "preserved_approval_state": "APPROVAL_REQUIRED",
            "preserved_replay_references": ["/tmp/replay/routing", "/tmp/replay/explanation", "/tmp/replay/proposal"],
            "advisory_only": True,
            "authority_granted": True,
        },
    ],
)
def test_provider_fidelity_or_authority_violation_falls_back(tmp_path, bad_response: dict) -> None:
    capture = create_acli_llm_assisted_explanation(
        explanation_id="EXPLANATION-003",
        authoritative_state=_authoritative_state(),
        deterministic_explanation="Fallback after invalid provider response.",
        provider=lambda _request: bad_response,
        provider_id="BAD_PROVIDER",
        replay_dir=tmp_path / "bad_provider",
        created_at=CREATED_AT,
    )

    artifact = capture["llm_assisted_explanation_artifact"]

    assert capture["explanation_status"] == DETERMINISTIC_FALLBACK_USED
    assert artifact["deterministic_fallback_used"] is True
    assert artifact["authority_granted"] is False
    assert artifact["explanation_response_artifact"]["preserved_artifact_identifiers"] == [
        "ACLI_USAGE_GUIDELINES_V1"
    ]
    assert artifact["explanation_response_artifact"]["preserved_approval_state"] == "APPROVAL_REQUIRED"


def test_authoritative_state_preserves_artifact_fidelity() -> None:
    state = _authoritative_state()

    assert state["artifact_identifiers"] == ["ACLI_USAGE_GUIDELINES_V1"]
    assert state["target_paths"] == [
        "docs/governance/ACLI_USAGE_GUIDELINES_V1.md",
        "aigol/runtime/acli_governed_development_example.py",
    ]
    assert state["approval_state"] == "APPROVAL_REQUIRED"
    assert state["replay_references"] == [
        "/tmp/replay/routing",
        "/tmp/replay/explanation",
        "/tmp/replay/proposal",
    ]
    assert state["artifact_hash"] == replay_hash({k: v for k, v in state.items() if k != "artifact_hash"})
