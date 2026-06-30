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
        "provider_name": "OpenAI GPT-5.5",
        "provider_tier": "Tier 2",
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
    assert artifact["provider_name"] == "OpenAI GPT-5.5"
    assert artifact["provider_role"] == "Explanation Provider"
    assert artifact["provider_tier"] == "Tier 2"
    assert artifact["provider_status"] == PROVIDER_EXPLANATION_USED
    assert artifact["explanation_confidence"] == "HIGH"
    assert artifact["explanation_completeness"] == "COMPLETE"
    assert artifact["render_mode"] == "PROVIDER_ASSISTED"
    assert artifact["escalation_level"] == "TIER_2"
    assert artifact["uhcl_wrapper_wiring"]["uhcl_consumed"] is True
    assert artifact["uhcl_wrapper_wiring"]["provider_invoked_by_wiring"] is False
    assert artifact["uhcl_wrapper_wiring"]["new_communication_semantics_introduced"] is False
    assert "EXPLANATION TRANSPARENCY" in artifact["rendered_operator_view"]
    assert "OpenAI GPT-5.5" in artifact["rendered_operator_view"]
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
    assert replay["provider_name"] == "OpenAI GPT-5.5"
    assert replay["explanation_confidence"] == "HIGH"
    assert replay["explanation_completeness"] == "COMPLETE"
    assert replay["render_mode"] == "PROVIDER_ASSISTED"
    assert replay["uhcl_wrapper_wiring"]["uhcl_consumed"] is True
    assert replay["explanation_transparency_artifact"]["explanation_pipeline"][1]["status"] == "USED"


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
    assert artifact["provider_status"] == "UNAVAILABLE"
    assert artifact["explanation_confidence"] == "GOVERNANCE_ONLY"
    assert artifact["explanation_completeness"] == "FALLBACK"
    assert artifact["render_mode"] == "DETERMINISTIC_FALLBACK"
    assert "EXPLANATION TRANSPARENCY" in artifact["rendered_operator_view"]
    assert "Fallback" in artifact["rendered_operator_view"]
    assert artifact["authority_granted"] is False

    replay = reconstruct_acli_llm_assisted_explanation_replay(
        capture["llm_assisted_explanation_replay_reference"]
    )
    assert replay["deterministic_fallback_used"] is True
    assert replay["fallback_reason"].startswith("EXPLANATION_PROVIDER_UNAVAILABLE")


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
    assert artifact["explanation_confidence"] == "GOVERNANCE_ONLY"
    assert artifact["explanation_completeness"] == "FALLBACK"
    assert artifact["rendered_operator_view_hash"].startswith("sha256:")


def test_provider_malformed_response_falls_back_with_transparency(tmp_path) -> None:
    capture = create_acli_llm_assisted_explanation(
        explanation_id="EXPLANATION-004",
        authoritative_state=_authoritative_state(),
        deterministic_explanation="Fallback after malformed provider response.",
        provider=lambda _request: "malformed",
        provider_id="MALFORMED_PROVIDER",
        replay_dir=tmp_path / "malformed_provider",
        created_at=CREATED_AT,
    )

    artifact = capture["llm_assisted_explanation_artifact"]

    assert capture["explanation_status"] == DETERMINISTIC_FALLBACK_USED
    assert artifact["provider_status"] == "MALFORMED_RESPONSE"
    assert artifact["fallback_reason"] == "EXPLANATION_PROVIDER_RESPONSE_MALFORMED"
    assert artifact["explanation_completeness"] == "FALLBACK"
    assert "Malformed Response" in artifact["rendered_operator_view"]


def test_future_provider_tier_transparency_is_preserved(tmp_path) -> None:
    def tier_three_provider(request: dict) -> dict:
        state = request["authoritative_state"]
        return {
            "explanation_text": "Tier 3 explanation preserves authoritative ACLI state.",
            "provider_name": "Comparison Explanation Provider",
            "provider_tier": "Tier 3",
            "preserved_artifact_identifiers": list(state["artifact_identifiers"]),
            "preserved_target_paths": list(state["target_paths"]),
            "preserved_approval_state": state["approval_state"],
            "preserved_replay_references": list(state["replay_references"]),
            "advisory_only": True,
            "authority_granted": False,
        }

    capture = create_acli_llm_assisted_explanation(
        explanation_id="EXPLANATION-005",
        authoritative_state=_authoritative_state(),
        deterministic_explanation="Deterministic explanation remains available.",
        provider=tier_three_provider,
        provider_id="COMPARISON_PROVIDER",
        replay_dir=tmp_path / "tier_three_provider",
        created_at=CREATED_AT,
    )

    artifact = capture["llm_assisted_explanation_artifact"]

    assert artifact["explanation_status"] == PROVIDER_EXPLANATION_USED
    assert artifact["provider_name"] == "Comparison Explanation Provider"
    assert artifact["provider_tier"] == "Tier 3"
    assert artifact["escalation_level"] == "TIER_3"
    assert "Tier 3" in artifact["rendered_operator_view"]


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
