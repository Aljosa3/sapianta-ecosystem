"""Tests for AIGOL_CLARIFIED_INTENT_RESOURCE_SELECTION_PPP_INTEGRATION_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.clarified_intent_resource_selection_ppp_integration_runtime import (
    CLARIFIED_PPP_INTENT_ROUTED,
    CLARIFIED_PPP_ROUTED_INTENT_ARTIFACT_V1,
    CLARIFIED_PPP_ROUTING_CLASSIFICATION_V1,
    CLARIFIED_PPP_ROUTING_EVIDENCE_V1,
    FAILED_CLOSED,
    reconstruct_clarified_intent_resource_selection_ppp_integration_replay,
    route_clarified_resource_selection_intent_to_ppp,
)
from aigol.runtime.clarified_intent_resource_selection_routing_runtime import (
    route_clarified_intent_to_resource_selection,
)
from aigol.runtime.intent_clarification_cognition_integration import (
    integrate_clarification_resolution_with_cognition,
)
from aigol.runtime.intent_clarification_dialog_runtime import run_intent_clarification_dialog
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash
from aigol.runtime.unified_resource_selection_runtime import PROVIDER_ROLE


CREATED_AT = "2026-06-03T23:45:00+00:00"
CHAIN_ID = "CHAIN-CLARIFIED-RS-PPP-000001"


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


def _resource_selection_routing_capture(tmp_path, *, response: dict | None = None):
    clarification = run_intent_clarification_dialog(
        clarification_id="CLARIFIED-RS-PPP-CLARIFICATION-000001",
        canonical_chain_id=CHAIN_ID,
        human_prompt_reference="PROMPT-CLARIFIED-RS-PPP-000001",
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
    cognition = integrate_clarification_resolution_with_cognition(
        integration_id="CLARIFIED-RS-PPP-COGNITION-000001",
        clarification_request_artifact=clarification["human_clarification_request_artifact"],
        clarification_response_artifact=clarification["human_clarification_response_artifact"],
        clarification_resolution_artifact=clarification["human_clarification_resolution_artifact"],
        confidence="DETERMINISTIC",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "cognition",
    )
    return route_clarified_intent_to_resource_selection(
        routing_id="CLARIFIED-RS-PPP-RESOURCE-SELECTION-000001",
        clarified_cognition_input_artifact=cognition["clarified_cognition_input_artifact"],
        clarification_cognition_evidence_artifact=cognition["clarification_cognition_evidence_artifact"],
        clarification_cognition_classification_artifact=cognition[
            "clarification_cognition_classification_artifact"
        ],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "resource_selection",
    )


def _ppp_capture(tmp_path, resource_routing: dict | None = None):
    resource_routing = resource_routing or _resource_selection_routing_capture(tmp_path)
    return route_clarified_resource_selection_intent_to_ppp(
        routing_id="CLARIFIED-RS-PPP-ROUTING-000001",
        clarified_resource_selection_routed_intent_artifact=resource_routing[
            "clarified_resource_selection_routed_intent_artifact"
        ],
        clarified_resource_selection_routing_evidence_artifact=resource_routing[
            "clarified_resource_selection_routing_evidence_artifact"
        ],
        clarified_resource_selection_routing_classification_artifact=resource_routing[
            "clarified_resource_selection_routing_classification_artifact"
        ],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "ppp",
    )


def test_routes_clarified_resource_selection_intent_to_ppp_input(tmp_path) -> None:
    capture = _ppp_capture(tmp_path)
    reconstructed = reconstruct_clarified_intent_resource_selection_ppp_integration_replay(
        tmp_path / "ppp"
    )
    routed = capture["clarified_ppp_routed_intent_artifact"]
    contract = routed["ppp_input_contract"]

    assert capture["routing_status"] == CLARIFIED_PPP_INTENT_ROUTED
    assert capture["clarified_ppp_routing_evidence_artifact"]["artifact_type"] == (
        CLARIFIED_PPP_ROUTING_EVIDENCE_V1
    )
    assert capture["clarified_ppp_routing_classification_artifact"]["artifact_type"] == (
        CLARIFIED_PPP_ROUTING_CLASSIFICATION_V1
    )
    assert routed["artifact_type"] == CLARIFIED_PPP_ROUTED_INTENT_ARTIFACT_V1
    assert routed["ppp_input_type"] == "STRUCTURED_PPP_INTENT"
    assert routed["selected_interpretation"] == "WORKER_FOUNDATION"
    assert routed["clarification_history"]
    assert contract["workflow_type"] == "NATIVE_DEVELOPMENT"
    assert contract["required_capability"] == "PROPOSAL_GENERATION"
    assert contract["requested_role_type"] == PROVIDER_ROLE
    assert contract["domain_id"] == "TRADING"
    assert contract["provider_necessity_classification"] == "PROVIDER_REQUIRED"
    assert contract["ppp_stage"] == "PROPOSAL_PRODUCTION"
    assert contract["intent_source_visible_to_ppp"] is False
    assert routed["intent_source_visible_to_ppp"] is False
    assert routed["source_lineage_preserved"] is True
    assert routed["resource_references"]["domain_id"] == "TRADING"
    assert routed["ppp_proposal_production_invoked"] is False
    assert routed["ppp_invoked"] is False
    assert routed["proposal_created"] is False
    assert routed["provider_invoked"] is False
    assert routed["worker_invoked"] is False
    assert routed["authorization_created"] is False
    assert routed["execution_requested"] is False
    assert routed["dispatch_requested"] is False
    assert reconstructed["routing_status"] == CLARIFIED_PPP_INTENT_ROUTED
    assert reconstructed["replay_artifact_count"] == 4


def test_direct_clarified_and_replay_derived_intents_are_ppp_equivalent(tmp_path) -> None:
    capture = _ppp_capture(tmp_path)
    contract = capture["ppp_input_contract"]

    assert set(contract) == {
        "intent_reference",
        "workflow_type",
        "required_capability",
        "requested_role_type",
        "domain_id",
        "provider_necessity_classification",
        "confidence",
        "ppp_stage",
        "intent_source_visible_to_ppp",
    }
    assert contract["intent_source_visible_to_ppp"] is False
    assert "HUMAN_CLARIFICATION" not in contract.values()
    assert "REPLAY_GAP_DETECTION" not in contract.values()
    assert "REPLAY_DERIVED_INTENT" not in contract.values()


def test_ppp_routing_fails_closed_when_clarification_unresolved(tmp_path) -> None:
    resource_routing = _resource_selection_routing_capture(
        tmp_path,
        response=_response(selected_interpretation="UNKNOWN"),
    )
    capture = _ppp_capture(tmp_path / "unresolved", resource_routing)

    assert capture["routing_status"] == FAILED_CLOSED
    assert "unresolved clarification" in capture["failure_reason"]


def test_ppp_routing_fails_closed_when_invalid_resource_selection_lineage(tmp_path) -> None:
    resource_routing = _resource_selection_routing_capture(tmp_path)
    artifact = dict(resource_routing["clarified_resource_selection_routed_intent_artifact"])
    artifact["routing_evidence_hash"] = "sha256:not-real"
    artifact.pop("artifact_hash")
    artifact["artifact_hash"] = replay_hash(artifact)
    capture = route_clarified_resource_selection_intent_to_ppp(
        routing_id="CLARIFIED-RS-PPP-LINEAGE-000001",
        clarified_resource_selection_routed_intent_artifact=artifact,
        clarified_resource_selection_routing_evidence_artifact=resource_routing[
            "clarified_resource_selection_routing_evidence_artifact"
        ],
        clarified_resource_selection_routing_classification_artifact=resource_routing[
            "clarified_resource_selection_routing_classification_artifact"
        ],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "lineage",
    )

    assert capture["routing_status"] == FAILED_CLOSED
    assert "invalid resource-selection lineage" in capture["failure_reason"]


def test_ppp_routing_fails_closed_when_invalid_cognition_lineage(tmp_path) -> None:
    resource_routing = _resource_selection_routing_capture(tmp_path)
    artifact = dict(resource_routing["clarified_resource_selection_routed_intent_artifact"])
    artifact["selected_interpretation"] = "REPORTING_PORTAL"
    artifact.pop("artifact_hash")
    artifact["artifact_hash"] = replay_hash(artifact)
    capture = route_clarified_resource_selection_intent_to_ppp(
        routing_id="CLARIFIED-RS-PPP-COGNITION-LINEAGE-000001",
        clarified_resource_selection_routed_intent_artifact=artifact,
        clarified_resource_selection_routing_evidence_artifact=resource_routing[
            "clarified_resource_selection_routing_evidence_artifact"
        ],
        clarified_resource_selection_routing_classification_artifact=resource_routing[
            "clarified_resource_selection_routing_classification_artifact"
        ],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "cognition_lineage",
    )

    assert capture["routing_status"] == FAILED_CLOSED
    assert "invalid cognition lineage" in capture["failure_reason"]


def test_ppp_routing_fails_closed_on_replay_corruption(tmp_path) -> None:
    resource_routing = _resource_selection_routing_capture(tmp_path)
    artifact = dict(resource_routing["clarified_resource_selection_routed_intent_artifact"])
    contract = dict(artifact["resource_selection_input_contract"])
    contract["intent_source_visible_to_resource_selection"] = True
    artifact["resource_selection_input_contract"] = contract
    artifact.pop("artifact_hash")
    artifact["artifact_hash"] = replay_hash(artifact)
    capture = route_clarified_resource_selection_intent_to_ppp(
        routing_id="CLARIFIED-RS-PPP-CORRUPTION-000001",
        clarified_resource_selection_routed_intent_artifact=artifact,
        clarified_resource_selection_routing_evidence_artifact=resource_routing[
            "clarified_resource_selection_routing_evidence_artifact"
        ],
        clarified_resource_selection_routing_classification_artifact=resource_routing[
            "clarified_resource_selection_routing_classification_artifact"
        ],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corruption",
    )

    assert capture["routing_status"] == FAILED_CLOSED
    assert "replay corruption" in capture["failure_reason"]


def test_ppp_routing_fails_closed_when_chain_continuity_breaks(tmp_path) -> None:
    resource_routing = _resource_selection_routing_capture(tmp_path)
    evidence = dict(resource_routing["clarified_resource_selection_routing_evidence_artifact"])
    evidence["canonical_chain_id"] = "DIFFERENT-CHAIN"
    evidence.pop("artifact_hash")
    evidence["artifact_hash"] = replay_hash(evidence)
    classification = dict(resource_routing["clarified_resource_selection_routing_classification_artifact"])
    classification["routing_evidence_hash"] = evidence["artifact_hash"]
    classification.pop("artifact_hash")
    classification["artifact_hash"] = replay_hash(classification)
    artifact = dict(resource_routing["clarified_resource_selection_routed_intent_artifact"])
    artifact["routing_evidence_hash"] = evidence["artifact_hash"]
    artifact["routing_classification_hash"] = classification["artifact_hash"]
    artifact.pop("artifact_hash")
    artifact["artifact_hash"] = replay_hash(artifact)
    capture = route_clarified_resource_selection_intent_to_ppp(
        routing_id="CLARIFIED-RS-PPP-CHAIN-000001",
        clarified_resource_selection_routed_intent_artifact=artifact,
        clarified_resource_selection_routing_evidence_artifact=evidence,
        clarified_resource_selection_routing_classification_artifact=classification,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "chain",
    )

    assert capture["routing_status"] == FAILED_CLOSED
    assert "broken chain continuity" in capture["failure_reason"]


def test_reconstruction_detects_corrupt_clarified_ppp_replay(tmp_path) -> None:
    _ppp_capture(tmp_path)
    path = tmp_path / "ppp" / "002_clarified_ppp_routed_intent_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["normalized_intent"] = "corrupted"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_clarified_intent_resource_selection_ppp_integration_replay(tmp_path / "ppp")


def test_clarified_ppp_routing_has_no_ppp_provider_worker_or_execution_invocation_imports() -> None:
    import aigol.runtime.clarified_intent_resource_selection_ppp_integration_runtime as runtime

    source = inspect.getsource(runtime)

    assert "integrate_resource_selection_with_ppp(" not in source
    assert "produce_provider_development_proposal(" not in source
    assert "run_provider_attachment(" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source
