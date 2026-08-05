from __future__ import annotations

from copy import deepcopy
import ast
import json
from pathlib import Path

import pytest

from aigol.provider.provider_proposal_envelope import (
    create_provider_proposal_envelope,
)
from aigol.provider.provider_registry import (
    AVAILABLE,
    ProviderMetadata,
    ProviderRegistry,
)
from aigol.runtime import conversation_interpreter_epp_assistance_runtime_v1 as epp_v1
from aigol.runtime import human_interface_conversation_runtime_v2 as hir_v2
from aigol.runtime import platform_core_conversation_interpreter_proposal_runtime_v2 as proposal_v2
from aigol.runtime import platform_core_conversation_working_memory_runtime_v2 as cwm_v2
from aigol.runtime.constitutional_natural_conversation_branch_composition_v1 import (
    CLARIFICATION_REQUIRED,
    DELEGATED_TO_CLOSED_PROTOCOL,
    NATURAL_CONVERSATION_COMMITTED,
    NATURAL_CONVERSATION_SELECTED,
    SELECTION_FAILED_CLOSED,
    compose_constitutional_natural_conversation_branch_v1,
    create_constitutional_natural_conversation_selection_contract_v1,
    select_constitutional_natural_conversation_branch_v1,
    validate_constitutional_natural_conversation_composition_result_v1,
    validate_constitutional_natural_conversation_selection_contract_v1,
    validate_constitutional_natural_conversation_selection_result_v1,
)
from aigol.runtime.constitutional_production_workflow_branch_contract_v1 import (
    create_canonical_production_workflow_branch_model_v1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


WORKSPACE = "/workspace/sapianta"
SESSION = "G69-16-NATURAL-CONVERSATION"
CREATED_AT = "2026-08-05T12:00:00Z"
OBSERVED_AT = "2026-08-05T12:01:00Z"
INTERPRETER = "constitutional-natural-conversation-epp-v1"
PROVIDER_ID = "openai"
PROVIDER_VERSION = "openai-responses-v1"
MODEL_ID = "gpt-test"
SOURCE_TURN = (
    "Implement the audit report as implementation so governance evidence is complete"
)
MODULE = Path(
    "aigol/runtime/constitutional_natural_conversation_branch_composition_v1.py"
)


def _participants():
    return [
        {
            "participant_role": cwm_v2.HUMAN_ORIGINATOR,
            "asserted_identity": "local-human",
            "identity_source": cwm_v2.LOCAL_ASSERTION,
            "binding_disposition": cwm_v2.ASSERTED_NOT_AUTHENTICATED,
            "first_bound_revision": 0,
            "last_confirmed_revision": 0,
        }
    ]


def _state(tmp_path: Path):
    return cwm_v2.create_conversation_working_memory_state_v2(
        runtime_root=tmp_path / "cwm",
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        created_at=CREATED_AT,
        ttl_seconds=3600,
        participants=_participants(),
    )


def _profile():
    return epp_v1.create_conversation_interpreter_epp_selection_and_binding_profile_v1(
        interpreter_identity=INTERPRETER,
        interpreter_version="1.0.0",
        resource_id="OPENAI",
        provider_id=PROVIDER_ID,
        provider_version=PROVIDER_VERSION,
        model_id=MODEL_ID,
    )


def _provider_registry():
    registry = ProviderRegistry()
    registry.register_provider(
        ProviderMetadata(
            provider_id=PROVIDER_ID,
            provider_type="llm",
            provider_version=PROVIDER_VERSION,
            provider_status=AVAILABLE,
            domain="governance",
            capability="proposal_generation",
        )
    )
    return registry


def _interpreter_registry():
    return [
        {
            "interpreter_identity": INTERPRETER,
            "interpreter_class": proposal_v2.EXTERNAL_LANGUAGE_MODEL,
            "interpreter_version": "1.0.0",
            "enabled": True,
        }
    ]


def _operation(
    text,
    slot_class,
    slot_role,
    cardinality_key,
    surface,
    canonical,
    *,
    operation_type=proposal_v2.PROPOSE_SLOT_CREATION,
    target_slot_id=None,
):
    start = text.index(surface)
    return {
        "operation_type": operation_type,
        "slot_class": slot_class,
        "slot_role": slot_role,
        "cardinality_key": cardinality_key,
        "surface_value": surface,
        "canonical_value": canonical,
        "source_spans": [
            {"start_offset": start, "end_offset": start + len(surface)}
        ],
        "target_slot_id": target_slot_id,
        "depends_on_slot_ids": [],
        "evidence_reference_keys": ["turn"],
        "clarification_reason": None,
    }


def _four_slot_response(text=SOURCE_TURN):
    return {
        "response_schema_version": epp_v1.CONVERSATION_INTERPRETER_EPP_RESPONSE_V1,
        "operations": [
            _operation(
                text,
                cwm_v2.OPERATIVE_ACTION,
                cwm_v2.PRIMARY,
                cwm_v2.PRIMARY,
                "Implement",
                "Implement",
            ),
            _operation(
                text,
                cwm_v2.OPERATIVE_SUBJECT,
                cwm_v2.PRIMARY,
                cwm_v2.PRIMARY,
                "audit report",
                "audit report",
            ),
            _operation(
                text,
                cwm_v2.DESIRED_OUTCOME,
                cwm_v2.PRIMARY,
                cwm_v2.PRIMARY,
                "governance evidence is complete",
                "governance evidence is complete",
            ),
            _operation(
                text,
                cwm_v2.WORK_TYPE,
                "IMPLEMENTATION",
                cwm_v2.PRIMARY,
                "implementation",
                "IMPLEMENTATION",
            ),
        ],
        "evidence_references": [
            {
                "reference_key": "turn",
                "reference_kind": "SOURCE_TURN",
                "reference_digest": cwm_v2._checksum(text),
                "verification_status": "SOURCE_BOUND",
            }
        ],
        "advisory_confidence": {
            "scale_id": "PROVIDER_REPORTED_V1",
            "reported_value": "HIGH",
            "limitations": ["NON_AUTHORITATIVE"],
            "authority_effect": False,
        },
        "ambiguity_operation_indexes": [],
        "conflict_operation_indexes": [],
    }


class FakeProviderAdapter:
    provider_id = PROVIDER_ID
    provider_version = PROVIDER_VERSION
    model = MODEL_ID

    def __init__(self, response=None):
        self.response = response or _four_slot_response()
        self.calls = []

    def generate_proposal(self, request, *, proposal_id, timestamp):
        self.calls.append(deepcopy(request))
        return create_provider_proposal_envelope(
            proposal_id=proposal_id,
            provider_id=self.provider_id,
            provider_version=self.provider_version,
            request=request,
            response={
                "provider": self.provider_id,
                "provider_version": self.provider_version,
                "model": self.model,
                "response_text": json.dumps(self.response, sort_keys=True),
                "raw_response_hash": replay_hash(self.response),
            },
            timestamp=timestamp,
        )


class TimeoutProviderAdapter(FakeProviderAdapter):
    def generate_proposal(self, request, *, proposal_id, timestamp):
        self.calls.append(deepcopy(request))
        try:
            raise TimeoutError("provider timeout")
        except TimeoutError as exc:
            raise FailClosedRuntimeError("provider unavailable") from exc


def _facts(**overrides):
    value = {
        "canonical_entry_admitted": True,
        "human_intent_precedence_resolved": True,
        "continuation_requirement_satisfied": True,
        "conversation_state_bound": True,
        "natural_conversation_authorized": True,
        "external_data_processing_authorized": True,
    }
    value.update(overrides)
    return value


def _evidence():
    return {
        "canonical_entry_evidence_identity": "CHE-EVIDENCE-G69-16",
        "human_intent_precedence_identity": "PRECEDENCE-G69-16",
        "continuation_evidence_identity": "CONTINUATION-SATISFIED-G69-16",
        "conversation_state_identity": "CONVERSATION-STATE-G69-16",
    }


def _context(tmp_path):
    model = create_canonical_production_workflow_branch_model_v1()
    profile = _profile()
    contract = create_constitutional_natural_conversation_selection_contract_v1(
        workflow_model=model,
        binding_profile=profile,
    )
    return model, profile, contract, _state(tmp_path)


def _compose(tmp_path, *, provider=None, source=SOURCE_TURN, facts=None, state=None):
    model, profile, contract, created_state = _context(tmp_path)
    return compose_constitutional_natural_conversation_branch_v1(
        runtime_root=tmp_path / "cwm",
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        current_state=state or created_state,
        source_turn_text=source,
        observed_at=OBSERVED_AT,
        selection_contract=contract,
        workflow_model=model,
        binding_profile=profile,
        admissibility_facts=facts or _facts(),
        evidence_identities=_evidence(),
        interpreter_registry=_interpreter_registry(),
        provider_registry=_provider_registry(),
        provider_adapter=provider or FakeProviderAdapter(),
        selection_replay_dir=tmp_path / "selection",
    )


def test_selection_contract_binds_g69_15_and_preserves_one_transport_lineage():
    model = create_canonical_production_workflow_branch_model_v1()
    profile = _profile()
    contract = create_constitutional_natural_conversation_selection_contract_v1(
        workflow_model=model,
        binding_profile=profile,
    )

    assert contract["workflow_model_identity"] == model.model_identity
    assert contract["che_definition_count"] == 1
    assert contract["production_hic_family_count"] == 1
    assert contract["production_owner_chain_count"] == 1
    assert contract["production_path_count"] == 1
    assert contract["parallel_production_path_count"] == 0
    assert contract["hic_responsibility"] == "TRANSPORT_ONLY"
    assert contract["hic_semantic_capability"] == "NO_SEMANTIC_CAPABILITY"
    assert contract["natural_language_confirmation_allowed"] is False
    assert contract["natural_language_commitment_allowed"] is False
    assert contract["natural_language_authorization_allowed"] is False
    assert (
        validate_constitutional_natural_conversation_selection_contract_v1(
            contract,
            workflow_model=model,
            binding_profile=profile,
        )
        == contract
    )


def test_selection_contract_tamper_fails_closed():
    model = create_canonical_production_workflow_branch_model_v1()
    profile = _profile()
    contract = create_constitutional_natural_conversation_selection_contract_v1(
        workflow_model=model,
        binding_profile=profile,
    )
    contract["production_path_count"] = 2

    with pytest.raises(FailClosedRuntimeError, match="selection contract"):
        validate_constitutional_natural_conversation_selection_contract_v1(
            contract,
            workflow_model=model,
            binding_profile=profile,
        )


def test_ordinary_turn_selection_is_deterministic_and_non_authoritative(tmp_path):
    model, profile, contract, state = _context(tmp_path)
    values = [
        select_constitutional_natural_conversation_branch_v1(
            current_state=state,
            source_turn_text=SOURCE_TURN,
            selection_contract=contract,
            workflow_model=model,
            binding_profile=profile,
            admissibility_facts=_facts(),
            evidence_identities=_evidence(),
        )
        for _ in range(2)
    ]

    assert values[0] == values[1]
    assert values[0]["selection_status"] == NATURAL_CONVERSATION_SELECTED
    assert values[0]["provider_invoked"] is False
    assert values[0]["proposal_commit_invoked"] is False
    assert values[0]["authority_granted"] is False
    assert (
        validate_constitutional_natural_conversation_selection_result_v1(
            values[0]
        )
        == values[0]
    )


@pytest.mark.parametrize(
    "source",
    (
        "action: implement",
        "subject: audit report",
        "outcome: complete evidence",
        "work-type: IMPLEMENTATION",
        "/confirm candidate-sha256:abc",
        "/commit objective-sha256:abc",
    ),
)
def test_exact_g60_controls_delegate_without_provider_or_commit(tmp_path, source):
    provider = FakeProviderAdapter()
    result = _compose(tmp_path, provider=provider, source=source)

    assert result["composition_status"] == DELEGATED_TO_CLOSED_PROTOCOL
    assert result["semantic_cwm_mutated_by_g59_commit"] is False
    assert provider.calls == []
    recovered = cwm_v2.recover_conversation_working_memory_state_v2(
        runtime_root=tmp_path / "cwm",
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        observed_at=OBSERVED_AT,
    )
    assert recovered["revision"] == 0


def test_inadmissible_ordinary_turn_fails_before_provider(tmp_path):
    provider = FakeProviderAdapter()
    result = _compose(
        tmp_path,
        provider=provider,
        facts=_facts(external_data_processing_authorized=False),
    )

    assert result["composition_status"] == CLARIFICATION_REQUIRED
    assert (
        result["selection_result"]["selection_status"]
        == SELECTION_FAILED_CLOSED
    )
    assert result["failure_code"] == "BRANCH_NOT_ADMISSIBLE"
    assert provider.calls == []


def test_one_unrestricted_turn_commits_all_four_slots_through_g59(tmp_path):
    provider = FakeProviderAdapter()
    result = _compose(tmp_path, provider=provider)

    assert result["composition_status"] == NATURAL_CONVERSATION_COMMITTED, result
    assert result["semantic_cwm_mutated_by_g59_commit"] is True
    assert result["composition_owner_mutated_semantics"] is False
    assert result["objective_created"] is False
    assert result["objective_commitment_created"] is False
    assert result["platform_core_invoked"] is False
    assert result["authorization_created"] is False
    assert result["worker_invoked"] is False
    assert result["execution_invoked"] is False
    assert result["g64_completion_invoked"] is False
    assert result["branch_replay_written"] is False
    assert result["cro_observation_performed"] is False
    assert result["production_cutover_performed"] is False
    assert len(provider.calls) == 1
    recovered = cwm_v2.recover_conversation_working_memory_state_v2(
        runtime_root=tmp_path / "cwm",
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        observed_at=OBSERVED_AT,
    )
    assert recovered["revision"] == 1
    assert {
        slot["slot_class"] for slot in recovered["semantic_memory"]["semantic_slots"]
    } == {
        cwm_v2.OPERATIVE_ACTION,
        cwm_v2.OPERATIVE_SUBJECT,
        cwm_v2.DESIRED_OUTCOME,
        cwm_v2.WORK_TYPE,
    }
    assert all(
        slot["status"] == cwm_v2.PROPOSED
        for slot in recovered["semantic_memory"]["semantic_slots"]
    )


def test_unrestricted_correction_conflict_returns_to_exact_human_resolution(
    tmp_path,
):
    model, profile, contract, _initial = _context(tmp_path)
    typed = hir_v2.admit_hir_semantic_turn_v2(
        runtime_root=tmp_path / "cwm",
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        source_turn_text="action: implement",
        observed_at=OBSERVED_AT,
    )
    current = typed["state"]
    existing_action = next(
        slot
        for slot in current["semantic_memory"]["semantic_slots"]
        if slot["slot_class"] == cwm_v2.OPERATIVE_ACTION
    )
    source = (
        "Review the audit report as review so governance evidence is accurate"
    )
    response = {
        "response_schema_version": epp_v1.CONVERSATION_INTERPRETER_EPP_RESPONSE_V1,
        "operations": [
            _operation(
                source,
                cwm_v2.OPERATIVE_ACTION,
                cwm_v2.PRIMARY,
                cwm_v2.PRIMARY,
                "Review",
                "Review",
                operation_type=proposal_v2.PROPOSE_SLOT_REVISION,
                target_slot_id=existing_action["slot_id"],
            ),
            _operation(
                source,
                cwm_v2.OPERATIVE_SUBJECT,
                cwm_v2.PRIMARY,
                cwm_v2.PRIMARY,
                "audit report",
                "audit report",
            ),
            _operation(
                source,
                cwm_v2.DESIRED_OUTCOME,
                cwm_v2.PRIMARY,
                cwm_v2.PRIMARY,
                "governance evidence is accurate",
                "governance evidence is accurate",
            ),
            _operation(
                source,
                cwm_v2.WORK_TYPE,
                "REVIEW",
                cwm_v2.PRIMARY,
                "review",
                "REVIEW",
            ),
        ],
        "evidence_references": [
            {
                "reference_key": "turn",
                "reference_kind": "SOURCE_TURN",
                "reference_digest": cwm_v2._checksum(source),
                "verification_status": "SOURCE_BOUND",
            }
        ],
        "advisory_confidence": {
            "scale_id": "PROVIDER_REPORTED_V1",
            "reported_value": "HIGH",
            "limitations": ["NON_AUTHORITATIVE"],
            "authority_effect": False,
        },
        "ambiguity_operation_indexes": [],
        "conflict_operation_indexes": [],
    }

    result = compose_constitutional_natural_conversation_branch_v1(
        runtime_root=tmp_path / "cwm",
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        current_state=current,
        source_turn_text=source,
        observed_at="2026-08-05T12:02:00Z",
        selection_contract=contract,
        workflow_model=model,
        binding_profile=profile,
        admissibility_facts=_facts(),
        evidence_identities=_evidence(),
        interpreter_registry=_interpreter_registry(),
        provider_registry=_provider_registry(),
        provider_adapter=FakeProviderAdapter(response),
        selection_replay_dir=tmp_path / "selection",
    )

    assert result["composition_status"] == CLARIFICATION_REQUIRED
    assert result["failure_code"] == "SEMANTIC_CONFLICT"
    assert result["semantic_cwm_mutated_by_g59_commit"] is False
    recovered = cwm_v2.recover_conversation_working_memory_state_v2(
        runtime_root=tmp_path / "cwm",
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        observed_at="2026-08-05T12:02:00Z",
    )
    action = next(
        slot
        for slot in recovered["semantic_memory"]["semantic_slots"]
        if slot["slot_class"] == cwm_v2.OPERATIVE_ACTION
    )
    assert action["canonical_value"] == "implement"
    assert action["status"] == cwm_v2.ASSERTED
    assert result["objective_commitment_created"] is False


def test_provider_timeout_returns_clarification_without_commit(tmp_path):
    provider = TimeoutProviderAdapter()
    result = _compose(tmp_path, provider=provider)

    assert result["composition_status"] == CLARIFICATION_REQUIRED
    assert "PROVIDER_TIMEOUT" in result["failure_code"]
    assert result["semantic_cwm_mutated_by_g59_commit"] is False
    assert len(provider.calls) == 1
    recovered = cwm_v2.recover_conversation_working_memory_state_v2(
        runtime_root=tmp_path / "cwm",
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        observed_at=OBSERVED_AT,
    )
    assert recovered["revision"] == 0


def test_incomplete_slot_coverage_returns_clarification_without_commit(tmp_path):
    response = _four_slot_response()
    response["operations"] = response["operations"][:1]
    provider = FakeProviderAdapter(response)

    result = _compose(tmp_path, provider=provider)

    assert result["composition_status"] == CLARIFICATION_REQUIRED
    assert "REQUIRED_OBJECTIVE_SLOT_COVERAGE_INCOMPLETE" in result["failure_code"]
    assert result["semantic_cwm_mutated_by_g59_commit"] is False


def test_ambiguity_returns_clarification_without_commit(tmp_path):
    response = _four_slot_response()
    response["ambiguity_operation_indexes"] = [0]
    provider = FakeProviderAdapter(response)

    result = _compose(tmp_path, provider=provider)

    assert result["composition_status"] == CLARIFICATION_REQUIRED
    assert result["semantic_cwm_mutated_by_g59_commit"] is False


def test_stale_persisted_state_fails_before_provider_or_commit(tmp_path):
    model, profile, contract, stale_state = _context(tmp_path)
    typed = hir_v2.admit_hir_semantic_turn_v2(
        runtime_root=tmp_path / "cwm",
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        source_turn_text="action: preserve",
        observed_at=OBSERVED_AT,
    )
    assert typed["state"]["revision"] > stale_state["revision"]
    provider = FakeProviderAdapter()

    result = compose_constitutional_natural_conversation_branch_v1(
        runtime_root=tmp_path / "cwm",
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        current_state=stale_state,
        source_turn_text=SOURCE_TURN,
        observed_at=OBSERVED_AT,
        selection_contract=contract,
        workflow_model=model,
        binding_profile=profile,
        admissibility_facts=_facts(),
        evidence_identities=_evidence(),
        interpreter_registry=_interpreter_registry(),
        provider_registry=_provider_registry(),
        provider_adapter=provider,
        selection_replay_dir=tmp_path / "selection",
    )

    assert result["composition_status"] == CLARIFICATION_REQUIRED
    assert result["semantic_cwm_mutated_by_g59_commit"] is False
    assert result["failure_code"] == "CONVERSATION_STATE_BINDING_STALE"
    assert provider.calls == []


def test_composition_result_tamper_fails_closed(tmp_path):
    result = _compose(tmp_path)
    result["production_cutover_performed"] = True

    with pytest.raises(FailClosedRuntimeError):
        validate_constitutional_natural_conversation_composition_result_v1(
            result
        )


def test_composition_has_no_historical_b8_b9_or_b10_dependency():
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imports.update(
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    )

    assert not any(
        token in imported
        for imported in imports
        for token in (
            "human_to_governance",
            "canonical_semantic_artifact",
            "provider_assisted_conversation",
            "prompt_to_conversation",
            "g64",
            "replay_review",
            "cro",
            "cutover",
            "worker",
            "authorization",
            "execution",
        )
    )
