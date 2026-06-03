"""Tests for AIGOL_CLARIFIED_INTENT_RESOURCE_SELECTION_ROUTING_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.clarified_intent_resource_selection_routing_runtime import (
    CLARIFIED_RESOURCE_SELECTION_INTENT_ROUTED,
    CLARIFIED_RESOURCE_SELECTION_ROUTED_INTENT_V1,
    CLARIFIED_RESOURCE_SELECTION_ROUTING_CLASSIFICATION_V1,
    CLARIFIED_RESOURCE_SELECTION_ROUTING_EVIDENCE_V1,
    FAILED_CLOSED,
    reconstruct_clarified_intent_resource_selection_routing_replay,
    route_clarified_intent_to_resource_selection,
)
from aigol.runtime.intent_clarification_cognition_integration import (
    integrate_clarification_resolution_with_cognition,
)
from aigol.runtime.intent_clarification_dialog_runtime import run_intent_clarification_dialog
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash
from aigol.runtime.unified_resource_selection_runtime import PROVIDER_ROLE


CREATED_AT = "2026-06-03T23:00:00+00:00"
CHAIN_ID = "CHAIN-CLARIFIED-RESOURCE-SELECTION-000001"


def _candidates() -> list[dict]:
    return [
        {
            "interpretation_id": "WORKER_FOUNDATION",
            "label": "Create a Trading Risk Analysis worker foundation.",
            "domain_id": "TRADING",
            "worker_family_id": "RISK_ANALYSIS",
            "milestone_type": "WORKER_FOUNDATION",
            "capability_id": "ANALYSIS",
            "resource_category": "WORKER",
            "output_scope": "GOVERNANCE_FOUNDATION",
            "resume_stage": "COGNITION",
        },
        {
            "interpretation_id": "REPORTING_PORTAL",
            "label": "Create a Marketing reporting portal foundation.",
            "domain_id": "MARKETING",
            "worker_family_id": None,
            "milestone_type": "PORTAL_FOUNDATION",
            "capability_id": "REPORTING",
            "resource_category": "DOMAIN_RUNTIME",
            "output_scope": "PORTAL_FOUNDATION",
            "resume_stage": "TASK_INTAKE",
        },
    ]


def _response(**overrides) -> dict:
    response = {
        "selected_interpretation": "WORKER_FOUNDATION",
        "selected_domain_id": "TRADING",
        "selected_worker_family_id": "RISK_ANALYSIS",
        "selected_milestone_type": "WORKER_FOUNDATION",
        "selected_output_scope": "GOVERNANCE_FOUNDATION",
        "human_response_text": "Use Trading Risk Analysis worker foundation.",
        "resume_stage": "COGNITION",
    }
    response.update(overrides)
    return response


def _clarified_capture(tmp_path, *, response: dict | None = None, confidence: str = "DETERMINISTIC"):
    clarification = run_intent_clarification_dialog(
        clarification_id="CLARIFIED-RS-CLARIFICATION-000001",
        canonical_chain_id=CHAIN_ID,
        human_prompt_reference="PROMPT-CLARIFIED-RS-000001",
        human_prompt="Add analysis.",
        ambiguity_categories=["INTENT_AMBIGUITY", "WORKER_AMBIGUITY", "CAPABILITY_AMBIGUITY"],
        candidate_interpretations=_candidates(),
        human_response=response or _response(),
        clarification_history=[
            {
                "clarification_request_reference": "PRIOR-REQUEST",
                "clarification_response_reference": "PRIOR-RESPONSE",
                "resolution_status": "ADDITIONAL_CLARIFICATION_REQUIRED",
            }
        ],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "clarification",
    )
    return integrate_clarification_resolution_with_cognition(
        integration_id="CLARIFIED-RS-COGNITION-000001",
        clarification_request_artifact=clarification["human_clarification_request_artifact"],
        clarification_response_artifact=clarification["human_clarification_response_artifact"],
        clarification_resolution_artifact=clarification["human_clarification_resolution_artifact"],
        confidence=confidence,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "cognition",
    )


def test_routes_clarified_cognition_input_to_resource_selection_requirements(tmp_path) -> None:
    clarified = _clarified_capture(tmp_path)
    capture = route_clarified_intent_to_resource_selection(
        routing_id="CLARIFIED-RS-ROUTING-000001",
        clarified_cognition_input_artifact=clarified["clarified_cognition_input_artifact"],
        clarification_cognition_evidence_artifact=clarified["clarification_cognition_evidence_artifact"],
        clarification_cognition_classification_artifact=clarified[
            "clarification_cognition_classification_artifact"
        ],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "resource_selection",
    )
    reconstructed = reconstruct_clarified_intent_resource_selection_routing_replay(
        tmp_path / "resource_selection"
    )
    routed = capture["clarified_resource_selection_routed_intent_artifact"]
    contract = routed["resource_selection_input_contract"]

    assert capture["routing_status"] == CLARIFIED_RESOURCE_SELECTION_INTENT_ROUTED
    assert capture["clarified_resource_selection_routing_evidence_artifact"]["artifact_type"] == (
        CLARIFIED_RESOURCE_SELECTION_ROUTING_EVIDENCE_V1
    )
    assert capture["clarified_resource_selection_routing_classification_artifact"]["artifact_type"] == (
        CLARIFIED_RESOURCE_SELECTION_ROUTING_CLASSIFICATION_V1
    )
    assert routed["artifact_type"] == CLARIFIED_RESOURCE_SELECTION_ROUTED_INTENT_V1
    assert routed["selected_interpretation"] == "WORKER_FOUNDATION"
    assert routed["clarification_history"]
    assert contract["workflow_type"] == "NATIVE_DEVELOPMENT"
    assert contract["required_capability"] == "PROPOSAL_GENERATION"
    assert contract["requested_role_type"] == PROVIDER_ROLE
    assert contract["domain_id"] == "TRADING"
    assert contract["worker_family_id"] == "RISK_ANALYSIS"
    assert contract["milestone_type"] == "WORKER_FOUNDATION"
    assert contract["intent_source_visible_to_resource_selection"] is False
    assert routed["resource_selection_invoked"] is False
    assert routed["ppp_invoked"] is False
    assert routed["provider_invoked"] is False
    assert routed["worker_invoked"] is False
    assert routed["execution_requested"] is False
    assert routed["dispatch_requested"] is False
    assert reconstructed["routing_status"] == CLARIFIED_RESOURCE_SELECTION_INTENT_ROUTED
    assert reconstructed["replay_artifact_count"] == 4


def test_direct_and_clarified_intent_are_resource_selection_equivalent(tmp_path) -> None:
    clarified = _clarified_capture(tmp_path)
    capture = route_clarified_intent_to_resource_selection(
        routing_id="CLARIFIED-RS-EQUIVALENCE-000001",
        clarified_cognition_input_artifact=clarified["clarified_cognition_input_artifact"],
        clarification_cognition_evidence_artifact=clarified["clarification_cognition_evidence_artifact"],
        clarification_cognition_classification_artifact=clarified[
            "clarification_cognition_classification_artifact"
        ],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "equivalence",
    )
    contract = capture["resource_selection_input_contract"]

    assert set(contract) == {
        "intent_reference",
        "workflow_type",
        "required_capability",
        "requested_role_type",
        "domain_id",
        "worker_family_id",
        "milestone_type",
        "provider_necessity_classification",
        "confidence",
        "intent_source_visible_to_resource_selection",
    }
    assert contract["intent_source_visible_to_resource_selection"] is False
    assert "HUMAN_CLARIFICATION" not in contract.values()


def test_routing_fails_closed_when_clarification_unresolved(tmp_path) -> None:
    clarified = _clarified_capture(tmp_path, response=_response(selected_interpretation="UNKNOWN"))
    capture = route_clarified_intent_to_resource_selection(
        routing_id="CLARIFIED-RS-UNRESOLVED-000001",
        clarified_cognition_input_artifact=clarified["clarified_cognition_input_artifact"],
        clarification_cognition_evidence_artifact=clarified["clarification_cognition_evidence_artifact"],
        clarification_cognition_classification_artifact=clarified[
            "clarification_cognition_classification_artifact"
        ],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "unresolved",
    )

    assert capture["routing_status"] == FAILED_CLOSED
    assert "clarification unresolved" in capture["failure_reason"]


def test_routing_fails_closed_when_cognition_integration_invalid(tmp_path) -> None:
    clarified = _clarified_capture(tmp_path)
    artifact = dict(clarified["clarified_cognition_input_artifact"])
    artifact["integration_status"] = FAILED_CLOSED
    artifact["failure_reason"] = "manual invalid integration"
    artifact.pop("artifact_hash")
    artifact["artifact_hash"] = replay_hash(artifact)

    capture = route_clarified_intent_to_resource_selection(
        routing_id="CLARIFIED-RS-INVALID-000001",
        clarified_cognition_input_artifact=artifact,
        clarification_cognition_evidence_artifact=clarified["clarification_cognition_evidence_artifact"],
        clarification_cognition_classification_artifact=clarified[
            "clarification_cognition_classification_artifact"
        ],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "invalid",
    )

    assert capture["routing_status"] == FAILED_CLOSED
    assert "cognition integration invalid" in capture["failure_reason"]


def test_routing_fails_closed_on_replay_corruption(tmp_path) -> None:
    clarified = _clarified_capture(tmp_path)
    artifact = dict(clarified["clarified_cognition_input_artifact"])
    artifact["evidence_hash"] = "sha256:not-real"
    artifact.pop("artifact_hash")
    artifact["artifact_hash"] = replay_hash(artifact)

    capture = route_clarified_intent_to_resource_selection(
        routing_id="CLARIFIED-RS-CORRUPTION-000001",
        clarified_cognition_input_artifact=artifact,
        clarification_cognition_evidence_artifact=clarified["clarification_cognition_evidence_artifact"],
        clarification_cognition_classification_artifact=clarified[
            "clarification_cognition_classification_artifact"
        ],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corruption",
    )

    assert capture["routing_status"] == FAILED_CLOSED
    assert "replay corruption" in capture["failure_reason"]


def test_routing_fails_closed_when_confidence_insufficient(tmp_path) -> None:
    clarified = _clarified_capture(tmp_path, confidence="MEDIUM")
    capture = route_clarified_intent_to_resource_selection(
        routing_id="CLARIFIED-RS-CONFIDENCE-000001",
        clarified_cognition_input_artifact=clarified["clarified_cognition_input_artifact"],
        clarification_cognition_evidence_artifact=clarified["clarification_cognition_evidence_artifact"],
        clarification_cognition_classification_artifact=clarified[
            "clarification_cognition_classification_artifact"
        ],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "confidence",
    )

    assert capture["routing_status"] == FAILED_CLOSED
    assert "confidence insufficient" in capture["failure_reason"]


def test_routing_fails_closed_when_selected_interpretation_is_ambiguous(tmp_path) -> None:
    clarified = _clarified_capture(tmp_path)
    artifact = dict(clarified["clarified_cognition_input_artifact"])
    artifact["selected_interpretation"] = "DIFFERENT"
    artifact.pop("artifact_hash")
    artifact["artifact_hash"] = replay_hash(artifact)

    capture = route_clarified_intent_to_resource_selection(
        routing_id="CLARIFIED-RS-AMBIGUOUS-000001",
        clarified_cognition_input_artifact=artifact,
        clarification_cognition_evidence_artifact=clarified["clarification_cognition_evidence_artifact"],
        clarification_cognition_classification_artifact=clarified[
            "clarification_cognition_classification_artifact"
        ],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "ambiguous",
    )

    assert capture["routing_status"] == FAILED_CLOSED
    assert "ambiguous selected interpretation" in capture["failure_reason"]


def test_routing_fails_closed_on_chain_continuity_failure(tmp_path) -> None:
    clarified = _clarified_capture(tmp_path)
    evidence = dict(clarified["clarification_cognition_evidence_artifact"])
    evidence["canonical_chain_id"] = "DIFFERENT-CHAIN"
    evidence.pop("artifact_hash")
    evidence["artifact_hash"] = replay_hash(evidence)
    classification = dict(clarified["clarification_cognition_classification_artifact"])
    classification["integration_evidence_hash"] = evidence["artifact_hash"]
    classification.pop("artifact_hash")
    classification["artifact_hash"] = replay_hash(classification)
    artifact = dict(clarified["clarified_cognition_input_artifact"])
    artifact["evidence_hash"] = evidence["artifact_hash"]
    artifact["classification_hash"] = classification["artifact_hash"]
    artifact.pop("artifact_hash")
    artifact["artifact_hash"] = replay_hash(artifact)

    capture = route_clarified_intent_to_resource_selection(
        routing_id="CLARIFIED-RS-CHAIN-000001",
        clarified_cognition_input_artifact=artifact,
        clarification_cognition_evidence_artifact=evidence,
        clarification_cognition_classification_artifact=classification,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "chain",
    )

    assert capture["routing_status"] == FAILED_CLOSED
    assert "invalid chain continuity" in capture["failure_reason"]


def test_reconstruction_detects_corrupt_clarified_resource_selection_replay(tmp_path) -> None:
    clarified = _clarified_capture(tmp_path)
    route_clarified_intent_to_resource_selection(
        routing_id="CLARIFIED-RS-CORRUPT-REPLAY-000001",
        clarified_cognition_input_artifact=clarified["clarified_cognition_input_artifact"],
        clarification_cognition_evidence_artifact=clarified["clarification_cognition_evidence_artifact"],
        clarification_cognition_classification_artifact=clarified[
            "clarification_cognition_classification_artifact"
        ],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt_replay",
    )
    path = tmp_path / "corrupt_replay" / "002_clarified_resource_selection_routed_intent_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["normalized_intent"] = "corrupted"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_clarified_intent_resource_selection_routing_replay(tmp_path / "corrupt_replay")


def test_clarified_intent_resource_selection_routing_has_no_resource_ppp_provider_worker_or_execution_invocations() -> None:
    import aigol.runtime.clarified_intent_resource_selection_routing_runtime as runtime

    source = inspect.getsource(runtime)

    assert "select_unified_resource(" not in source
    assert "integrate_resource_selection_with_ppp(" not in source
    assert "produce_provider_development_proposal(" not in source
    assert "run_provider_attachment(" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source
