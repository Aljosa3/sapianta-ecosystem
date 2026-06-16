"""Certification tests for OCS single-provider primary mode selection."""

from __future__ import annotations

import json

from aigol.runtime.multi_provider_cognition_runtime import create_default_cognition_provider_contract
from aigol.runtime.ocs_llm_cognition_end_to_end_runtime import (
    STATUS_COMPLETED,
    reconstruct_ocs_llm_cognition_end_to_end_replay,
    run_ocs_llm_cognition_end_to_end,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-06-16T00:00:00Z"


def _source_context() -> dict:
    artifact = {
        "artifact_type": "HUMAN_REQUEST_ARTIFACT_V1",
        "artifact_id": "HUMAN-REQUEST-SINGLE-PROVIDER-CERTIFICATION",
        "status": "REPLAY_VISIBLE",
        "summary": "Human asks for OCS cognition with one certified primary provider.",
        "replay_visible": True,
        "authority": False,
        "execution_requested": False,
        "worker_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return {"conversation_context": [artifact]}


def _single_provider_contract() -> dict:
    contract = create_default_cognition_provider_contract(provider_id="provider-a", created_at=CREATED_AT)
    contract["single_provider_only"] = True
    contract["multi_provider_cognition_scope"] = False
    contract.pop("artifact_hash", None)
    contract["artifact_hash"] = replay_hash(contract)
    return contract


def _multi_provider_contract(provider_id: str) -> dict:
    contract = create_default_cognition_provider_contract(provider_id=provider_id, created_at=CREATED_AT)
    contract["single_provider_only"] = False
    contract["multi_provider_cognition_scope"] = True
    contract.pop("artifact_hash", None)
    contract["artifact_hash"] = replay_hash(contract)
    return contract


def _transport(provider_id: str):
    def call(_payload: dict, metadata: dict) -> dict:
        assert metadata["provider_role"] == "COGNITION_PROVIDER"
        return {
            "output_text": json.dumps(
                {
                    "findings": [f"{provider_id} certified single-provider cognition finding."],
                    "assumptions": ["Provider output remains advisory."],
                    "alternatives": ["Human review remains the next boundary."],
                    "risks": ["Single-provider cognition must not claim multi-provider consensus."],
                    "uncertainties": ["No second provider was used."],
                    "confidence": "MEDIUM",
                },
                sort_keys=True,
            )
        }

    return call


def _run(tmp_path, *, contracts: list[dict], single_provider_primary_mode: bool = False):
    return run_ocs_llm_cognition_end_to_end(
        end_to_end_id="OCS-SINGLE-PROVIDER-PRIMARY-MODE-CERTIFICATION",
        human_question="What should Product 1 consider next?",
        source_context=_source_context(),
        provider_contracts=contracts,
        transport_registry={contract["provider_id"]: _transport(contract["provider_id"]) for contract in contracts},
        created_at=CREATED_AT,
        replay_dir=tmp_path / "e2e",
        source_chain_id="CHAIN-SINGLE-PROVIDER-PRIMARY-MODE-CERTIFICATION",
        source_request_reference="HUMAN-REQUEST-SINGLE-PROVIDER-CERTIFICATION",
        single_provider_primary_mode=single_provider_primary_mode,
    )


def test_contract_declared_single_provider_primary_mode_is_replay_certified(tmp_path):
    result = _run(tmp_path, contracts=[_single_provider_contract()])
    artifact = result["ocs_llm_cognition_end_to_end_artifact"]
    replay = reconstruct_ocs_llm_cognition_end_to_end_replay(tmp_path / "e2e")
    mode_replay = replay["stage_replay"]["mode_selection"]

    assert result["final_status"] == STATUS_COMPLETED
    assert artifact["selected_cognition_mode"] == "SINGLE_PROVIDER_PRIMARY"
    assert artifact["single_provider_primary_mode"] is True
    assert artifact["comparison_required"] is False
    assert artifact["comparison_performed"] is False
    assert mode_replay["selected_mode"] == "SINGLE_PROVIDER_PRIMARY"
    assert mode_replay["selection_reason"] == (
        "successful provider contract declares single-provider-only cognition scope"
    )
    assert mode_replay["requested_single_provider_primary_mode"] is False
    assert mode_replay["provider_contract_mode_flags"]["provider-a"]["single_provider_only"] is True
    assert mode_replay["provider_contract_mode_flags"]["provider-a"]["multi_provider_cognition_scope"] is False
    assert replay["stage_replay"]["cognition_comparison"]["source_cognition_artifact_count"] == 1
    assert replay["stage_replay"]["cognition_comparison"]["comparison_confidence"] == "MEDIUM"


def test_multi_provider_contracts_keep_standard_comparison_mode(tmp_path):
    result = _run(
        tmp_path,
        contracts=[
            _multi_provider_contract("provider-a"),
            _multi_provider_contract("provider-b"),
        ],
    )
    artifact = result["ocs_llm_cognition_end_to_end_artifact"]
    replay = reconstruct_ocs_llm_cognition_end_to_end_replay(tmp_path / "e2e")
    mode_replay = replay["stage_replay"]["mode_selection"]

    assert result["final_status"] == STATUS_COMPLETED
    assert artifact["selected_cognition_mode"] == "MULTI_PROVIDER_COMPARISON"
    assert artifact["single_provider_primary_mode"] is False
    assert artifact["comparison_required"] is True
    assert artifact["comparison_performed"] is True
    assert mode_replay["selected_mode"] == "MULTI_PROVIDER_COMPARISON"
    assert mode_replay["selection_reason"] == (
        "two or more successful provider cognition artifacts require standard comparison"
    )
    assert replay["stage_replay"]["cognition_comparison"]["source_cognition_artifact_count"] == 2

