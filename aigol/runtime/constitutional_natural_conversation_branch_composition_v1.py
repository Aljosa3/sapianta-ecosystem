"""Constitutional Natural Conversation branch composition for B7.

The composition preserves exact G60 control precedence, selects one bounded
G61 proposal branch only for an admissible ordinary turn, and hands an
admissible candidate to the existing G59 Proposal Commit owner.  It does not
invoke Canonical Human Entry, add semantics to HIC, create an Objective, enter
Platform Core, execute work, compose G64 completion, persist branch Replay,
observe through CRO, or cut over a production consumer.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

from aigol.provider.provider_adapter import ProviderAdapter
from aigol.provider.provider_registry import ProviderRegistry
from aigol.runtime import conversation_interpreter_epp_assistance_runtime_v1 as epp_v1
from aigol.runtime import human_interface_conversation_runtime_v2 as hir_v2
from aigol.runtime import platform_core_conversation_interpreter_proposal_runtime_v2 as proposal_v2
from aigol.runtime import platform_core_conversation_proposal_commit_runtime_v2 as commit_v2
from aigol.runtime import platform_core_conversation_state_machine_runtime_v2 as machine_v2
from aigol.runtime import platform_core_conversation_working_memory_runtime_v2 as cwm_v2
from aigol.runtime.constitutional_production_workflow_branch_contract_v1 import (
    NO_PRODUCTION_ROUTE_CREATION,
    NO_SEMANTIC_CAPABILITY,
    NO_WORKFLOW_EXECUTION,
    TRANSPORT_ONLY,
    CanonicalProductionWorkflowBranchModelV1,
    validate_canonical_production_workflow_branch_model_v1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CONSTITUTIONAL_NATURAL_CONVERSATION_BRANCH_COMPOSITION_V1 = (
    "CONSTITUTIONAL_NATURAL_CONVERSATION_BRANCH_COMPOSITION_V1"
)
CONSTITUTIONAL_NATURAL_CONVERSATION_SELECTION_CONTRACT_V1 = (
    "CONSTITUTIONAL_NATURAL_CONVERSATION_SELECTION_CONTRACT_V1"
)
CONSTITUTIONAL_NATURAL_CONVERSATION_SELECTION_RESULT_V1 = (
    "CONSTITUTIONAL_NATURAL_CONVERSATION_SELECTION_RESULT_V1"
)
CONSTITUTIONAL_NATURAL_CONVERSATION_COMPOSITION_RESULT_V1 = (
    "CONSTITUTIONAL_NATURAL_CONVERSATION_COMPOSITION_RESULT_V1"
)

CLOSED_PROTOCOL_CONTROL_BRANCH = "CLOSED_PROTOCOL_CONTROL_BRANCH"
NATURAL_CONVERSATION_EPP_BRANCH = "NATURAL_CONVERSATION_EPP_BRANCH"
CONVERSATION_CLARIFICATION_BRANCH = "CONVERSATION_CLARIFICATION_BRANCH"

DELEGATED_TO_CLOSED_PROTOCOL = "DELEGATED_TO_CLOSED_PROTOCOL"
NATURAL_CONVERSATION_SELECTED = "NATURAL_CONVERSATION_SELECTED"
SELECTION_FAILED_CLOSED = "SELECTION_FAILED_CLOSED"
NATURAL_CONVERSATION_COMMITTED = "NATURAL_CONVERSATION_COMMITTED"
CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"

G59_CONVERSATION_SELECTION_OWNER = "G59_CONVERSATION_SELECTION_OWNER"
G61_EPP_PROPOSAL_OWNER = "G61_EPP_PROPOSAL_OWNER"
G59_PROPOSAL_VALIDATION_OWNER = "G59_PROPOSAL_VALIDATION_OWNER"
G59_PROPOSAL_COMMIT_OWNER = "G59_PROPOSAL_COMMIT_OWNER"
G60_CLOSED_PROTOCOL_CONTROL_OWNER = "G60_CLOSED_PROTOCOL_CONTROL_OWNER"
G59_CONVERSATION_CLARIFICATION_OWNER = "G59_CONVERSATION_CLARIFICATION_OWNER"

_NATURAL_HANDOFF_OWNER_ORDER = (
    G59_CONVERSATION_SELECTION_OWNER,
    G61_EPP_PROPOSAL_OWNER,
    G59_PROPOSAL_VALIDATION_OWNER,
    G59_PROPOSAL_COMMIT_OWNER,
)
_REQUIRED_ADMISSIBILITY_FACTS = frozenset(
    {
        "canonical_entry_admitted",
        "human_intent_precedence_resolved",
        "continuation_requirement_satisfied",
        "conversation_state_bound",
        "natural_conversation_authorized",
        "external_data_processing_authorized",
    }
)
_REQUIRED_EVIDENCE_IDENTITIES = frozenset(
    {
        "canonical_entry_evidence_identity",
        "human_intent_precedence_identity",
        "continuation_evidence_identity",
        "conversation_state_identity",
    }
)
_REQUIRED_OBJECTIVE_SLOT_CLASSES = frozenset(
    {
        cwm_v2.OPERATIVE_ACTION,
        cwm_v2.OPERATIVE_SUBJECT,
        cwm_v2.DESIRED_OUTCOME,
        cwm_v2.WORK_TYPE,
    }
)
_EPP_FORBIDDEN_TRUE_FIELDS = (
    "semantic_cwm_mutated",
    "proposal_commit_performed",
    "conversation_transition_applied",
    "objective_created",
    "objective_commitment_created",
    "platform_core_invoked",
    "development_governance_invoked",
    "capability_selection_invoked",
    "authorization_created",
    "worker_invoked",
    "execution_invoked",
    "provider_content_replay_written",
)
_COMPOSITION_BOUNDARIES = {
    "canonical_entry_invoked": False,
    "hic_semantic_capability_added": False,
    "production_path_created": False,
    "objective_created": False,
    "objective_commitment_created": False,
    "platform_core_invoked": False,
    "development_governance_invoked": False,
    "authorization_created": False,
    "worker_invoked": False,
    "execution_invoked": False,
    "g64_completion_invoked": False,
    "branch_replay_written": False,
    "cro_observation_performed": False,
    "production_cutover_performed": False,
}


def _fail(message: str) -> None:
    raise FailClosedRuntimeError(message)


def _text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        _fail(f"Natural Conversation {field_name} is absent or malformed")
    return value


def _closed_mapping(
    value: Any,
    expected_fields: frozenset[str],
    field_name: str,
) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != expected_fields:
        _fail(f"Natural Conversation {field_name} is malformed")
    return dict(value)


def _profile(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail("Natural Conversation binding profile is malformed")
    required = epp_v1.create_conversation_interpreter_epp_selection_and_binding_profile_v1(
        interpreter_identity=value.get("interpreter_identity"),
        interpreter_version=value.get("interpreter_version"),
        resource_id=value.get("epp_resource_id"),
        provider_id=value.get("provider_id"),
        provider_version=value.get("provider_version"),
        model_id=value.get("model_id"),
        model_configuration_version=value.get("model_configuration_version"),
        credential_reference_id=value.get("credential_reference_id"),
        timeout_seconds=value.get("timeout_seconds"),
        maximum_input_bytes=value.get("maximum_input_bytes"),
        maximum_output_bytes=value.get("maximum_output_bytes"),
    )
    if value != required:
        _fail("Natural Conversation binding profile is not canonical")
    if (
        required["external_data_processing"] is not True
        or required["authority_profile"] != "PROVIDER_PROPOSAL_ONLY"
        or any(
            required[field] is not False
            for field in (
                "semantic_authority",
                "objective_authority",
                "commit_authority",
                "execution_authority",
                "worker_authority",
            )
        )
    ):
        _fail("Natural Conversation profile exceeds proposal-only authority")
    return required


def create_constitutional_natural_conversation_selection_contract_v1(
    *,
    workflow_model: CanonicalProductionWorkflowBranchModelV1 | Mapping[str, Any],
    binding_profile: dict[str, Any],
) -> dict[str, Any]:
    """Create one closed selection and owner-handoff contract."""

    model = validate_canonical_production_workflow_branch_model_v1(workflow_model)
    profile = _profile(binding_profile)
    body = {
        "contract_version": (
            CONSTITUTIONAL_NATURAL_CONVERSATION_SELECTION_CONTRACT_V1
        ),
        "workflow_model_identity": model.model_identity,
        "canonical_entry_identity": model.canonical_entry_identity,
        "che_definition_count": model.che_definition_count,
        "production_hic_family_count": model.production_hic_family_count,
        "production_owner_chain_count": model.production_owner_chain_count,
        "production_path_count": model.production_path_count,
        "parallel_production_path_count": model.parallel_production_path_count,
        "hic_responsibility": model.hic_responsibility,
        "hic_semantic_capability": model.hic_semantic_capability,
        "workflow_execution_capability": model.workflow_execution_capability,
        "production_route_creation_capability": (
            model.production_route_creation_capability
        ),
        "selection_owner": G59_CONVERSATION_SELECTION_OWNER,
        "closed_protocol_owner": G60_CLOSED_PROTOCOL_CONTROL_OWNER,
        "proposal_owner": G61_EPP_PROPOSAL_OWNER,
        "proposal_validation_owner": G59_PROPOSAL_VALIDATION_OWNER,
        "proposal_commit_owner": G59_PROPOSAL_COMMIT_OWNER,
        "failure_owner": G59_CONVERSATION_CLARIFICATION_OWNER,
        "branch_precedence": [
            CLOSED_PROTOCOL_CONTROL_BRANCH,
            NATURAL_CONVERSATION_EPP_BRANCH,
            CONVERSATION_CLARIFICATION_BRANCH,
        ],
        "eligible_control_disposition": hir_v2.NON_PROTOCOL_TURN,
        "binding_profile_digest": profile["profile_digest"],
        "natural_handoff_owner_order": list(_NATURAL_HANDOFF_OWNER_ORDER),
        "required_objective_slot_classes": sorted(
            _REQUIRED_OBJECTIVE_SLOT_CLASSES
        ),
        "failure_disposition": CLARIFICATION_REQUIRED,
        "automatic_retry": False,
        "provider_substitution": False,
        "natural_language_confirmation_allowed": False,
        "natural_language_commitment_allowed": False,
        "natural_language_authorization_allowed": False,
    }
    return {
        "contract_identity": "natural-conversation-selection-sha256:"
        + replay_hash(body).split(":", 1)[1],
        **body,
    }


def validate_constitutional_natural_conversation_selection_contract_v1(
    value: Any,
    *,
    workflow_model: CanonicalProductionWorkflowBranchModelV1 | Mapping[str, Any],
    binding_profile: dict[str, Any],
) -> dict[str, Any]:
    expected = create_constitutional_natural_conversation_selection_contract_v1(
        workflow_model=workflow_model,
        binding_profile=binding_profile,
    )
    if not isinstance(value, dict) or value != expected:
        _fail("Natural Conversation selection contract is invalid")
    canonical_serialize(value)
    return deepcopy(value)


def _admissibility_facts(value: Any) -> dict[str, bool]:
    facts = _closed_mapping(
        value,
        _REQUIRED_ADMISSIBILITY_FACTS,
        "admissibility facts",
    )
    if any(not isinstance(item, bool) for item in facts.values()):
        _fail("Natural Conversation admissibility facts are not Boolean")
    return {key: facts[key] for key in sorted(facts)}


def _evidence_identities(value: Any) -> dict[str, str]:
    evidence = _closed_mapping(
        value,
        _REQUIRED_EVIDENCE_IDENTITIES,
        "admissibility evidence",
    )
    return {key: _text(evidence[key], key) for key in sorted(evidence)}


def _selection_result(
    *,
    contract: dict[str, Any],
    state: dict[str, Any],
    source_turn: dict[str, Any],
    control_disposition: str,
    admissibility_facts: dict[str, bool],
    evidence_identities: dict[str, str],
    selection_status: str,
    selected_branch: str,
    selected_owner: str,
    failure_code: str | None,
) -> dict[str, Any]:
    result = {
        "result_type": CONSTITUTIONAL_NATURAL_CONVERSATION_SELECTION_RESULT_V1,
        "contract_identity": contract["contract_identity"],
        "workflow_model_identity": contract["workflow_model_identity"],
        "selection_status": selection_status,
        "selected_branch": selected_branch,
        "selected_owner": selected_owner,
        "failure_code": failure_code,
        "control_disposition": control_disposition,
        "conversation_identity": state["envelope"]["conversation_identity"],
        "source_turn_identity": source_turn["source_turn_identity"],
        "source_turn_digest": source_turn["source_turn_digest"],
        "expected_cwm_revision": state["revision"],
        "expected_semantic_revision": state["semantic_revision"],
        "admissibility_facts": admissibility_facts,
        "evidence_identities": evidence_identities,
        "provider_invoked": False,
        "proposal_commit_invoked": False,
        "authority_granted": False,
    }
    result["selection_identity"] = "natural-conversation-branch-sha256:" + (
        replay_hash(result).split(":", 1)[1]
    )
    result["selection_hash"] = replay_hash(result)
    return result


def validate_constitutional_natural_conversation_selection_result_v1(
    value: Any,
) -> dict[str, Any]:
    fields = frozenset(
        {
            "result_type",
            "contract_identity",
            "workflow_model_identity",
            "selection_status",
            "selected_branch",
            "selected_owner",
            "failure_code",
            "control_disposition",
            "conversation_identity",
            "source_turn_identity",
            "source_turn_digest",
            "expected_cwm_revision",
            "expected_semantic_revision",
            "admissibility_facts",
            "evidence_identities",
            "provider_invoked",
            "proposal_commit_invoked",
            "authority_granted",
            "selection_identity",
            "selection_hash",
        }
    )
    candidate = _closed_mapping(value, fields, "selection result")
    if candidate["result_type"] != (
        CONSTITUTIONAL_NATURAL_CONVERSATION_SELECTION_RESULT_V1
    ):
        _fail("Natural Conversation selection result type is invalid")
    facts = _admissibility_facts(candidate["admissibility_facts"])
    evidence = _evidence_identities(candidate["evidence_identities"])
    if facts != candidate["admissibility_facts"] or evidence != candidate[
        "evidence_identities"
    ]:
        _fail("Natural Conversation selection facts are not canonical")
    body = deepcopy(candidate)
    actual_hash = body.pop("selection_hash")
    if actual_hash != replay_hash(body):
        _fail("Natural Conversation selection result hash is invalid")
    identity_body = deepcopy(body)
    actual_identity = identity_body.pop("selection_identity")
    expected_identity = "natural-conversation-branch-sha256:" + (
        replay_hash(identity_body).split(":", 1)[1]
    )
    if actual_identity != expected_identity:
        _fail("Natural Conversation selection identity is invalid")
    if any(
        candidate[field] is not False
        for field in (
            "provider_invoked",
            "proposal_commit_invoked",
            "authority_granted",
        )
    ):
        _fail("Natural Conversation branch selection acquired authority")
    expected_tuple = {
        DELEGATED_TO_CLOSED_PROTOCOL: (
            CLOSED_PROTOCOL_CONTROL_BRANCH,
            G60_CLOSED_PROTOCOL_CONTROL_OWNER,
            None,
        ),
        NATURAL_CONVERSATION_SELECTED: (
            NATURAL_CONVERSATION_EPP_BRANCH,
            G61_EPP_PROPOSAL_OWNER,
            None,
        ),
        SELECTION_FAILED_CLOSED: (
            CONVERSATION_CLARIFICATION_BRANCH,
            G59_CONVERSATION_CLARIFICATION_OWNER,
            "BRANCH_NOT_ADMISSIBLE",
        ),
    }.get(candidate["selection_status"])
    if expected_tuple != (
        candidate["selected_branch"],
        candidate["selected_owner"],
        candidate["failure_code"],
    ):
        _fail("Natural Conversation selection disposition is invalid")
    canonical_serialize(candidate)
    return deepcopy(candidate)


def select_constitutional_natural_conversation_branch_v1(
    *,
    current_state: dict[str, Any],
    source_turn_text: str,
    selection_contract: dict[str, Any],
    workflow_model: CanonicalProductionWorkflowBranchModelV1 | Mapping[str, Any],
    binding_profile: dict[str, Any],
    admissibility_facts: Mapping[str, bool],
    evidence_identities: Mapping[str, str],
) -> dict[str, Any]:
    """Select one branch without invoking a provider or committing semantics."""

    model = validate_canonical_production_workflow_branch_model_v1(workflow_model)
    if (
        model.che_definition_count != 1
        or model.production_hic_family_count != 1
        or model.production_owner_chain_count != 1
        or model.production_path_count != 1
        or model.parallel_production_path_count != 0
        or model.hic_responsibility != TRANSPORT_ONLY
        or model.hic_semantic_capability != NO_SEMANTIC_CAPABILITY
        or model.workflow_execution_capability != NO_WORKFLOW_EXECUTION
        or model.production_route_creation_capability
        != NO_PRODUCTION_ROUTE_CREATION
    ):
        _fail("Natural Conversation workflow invariants are invalid")
    contract = validate_constitutional_natural_conversation_selection_contract_v1(
        selection_contract,
        workflow_model=model,
        binding_profile=binding_profile,
    )
    state = machine_v2.validate_conversation_state_machine_state_v2(current_state)
    turn = _text(source_turn_text, "source turn")
    facts = _admissibility_facts(admissibility_facts)
    evidence = _evidence_identities(evidence_identities)
    control = hir_v2.classify_hir_conversation_turn_v2(turn)
    source_turn = proposal_v2.create_source_turn_binding_v2(
        conversation_identity=state["envelope"]["conversation_identity"],
        session_identity_hash=state["envelope"]["session_identity_hash"],
        expected_cwm_revision=state["revision"],
        source_turn_text=turn,
    )
    if control != hir_v2.NON_PROTOCOL_TURN:
        result = _selection_result(
            contract=contract,
            state=state,
            source_turn=source_turn,
            control_disposition=control,
            admissibility_facts=facts,
            evidence_identities=evidence,
            selection_status=DELEGATED_TO_CLOSED_PROTOCOL,
            selected_branch=CLOSED_PROTOCOL_CONTROL_BRANCH,
            selected_owner=G60_CLOSED_PROTOCOL_CONTROL_OWNER,
            failure_code=None,
        )
    elif (
        not all(facts.values())
        or state["envelope"]["availability_state"] != cwm_v2.ACTIVE
        or state["envelope"]["conversation_phase"]
        not in {cwm_v2.COLLECTING, cwm_v2.CLARIFYING, cwm_v2.CANDIDATE_REVIEW}
    ):
        result = _selection_result(
            contract=contract,
            state=state,
            source_turn=source_turn,
            control_disposition=control,
            admissibility_facts=facts,
            evidence_identities=evidence,
            selection_status=SELECTION_FAILED_CLOSED,
            selected_branch=CONVERSATION_CLARIFICATION_BRANCH,
            selected_owner=G59_CONVERSATION_CLARIFICATION_OWNER,
            failure_code="BRANCH_NOT_ADMISSIBLE",
        )
    else:
        result = _selection_result(
            contract=contract,
            state=state,
            source_turn=source_turn,
            control_disposition=control,
            admissibility_facts=facts,
            evidence_identities=evidence,
            selection_status=NATURAL_CONVERSATION_SELECTED,
            selected_branch=NATURAL_CONVERSATION_EPP_BRANCH,
            selected_owner=G61_EPP_PROPOSAL_OWNER,
            failure_code=None,
        )
    return validate_constitutional_natural_conversation_selection_result_v1(
        result
    )


def _validate_epp_result(value: Any, profile: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail("Natural Conversation G61 result is malformed")
    candidate = deepcopy(value)
    actual_hash = candidate.pop("result_hash", None)
    if actual_hash != replay_hash(candidate):
        _fail("Natural Conversation G61 result hash is invalid")
    candidate["result_hash"] = actual_hash
    if (
        candidate.get("result_type") != epp_v1.CONVERSATION_INTERPRETER_EPP_RESULT_V1
        or candidate.get("binding_profile_hash") != profile["profile_digest"]
        or any(candidate.get(field) is not False for field in _EPP_FORBIDDEN_TRUE_FIELDS)
    ):
        _fail("Natural Conversation G61 owner boundary is invalid")
    return candidate


def _candidate_covers_required_objective_slots(
    state: dict[str, Any], candidate_operation_set: dict[str, Any]
) -> bool:
    current_classes = {
        slot["slot_class"]
        for slot in state["semantic_memory"]["semantic_slots"]
        if slot["status"] not in {cwm_v2.CONFLICTED, cwm_v2.STALE}
    }
    candidate_classes = {
        operation["slot_class"]
        for operation in candidate_operation_set["candidate_operations"]
        if operation["candidate_operation_type"]
        in {
            commit_v2.CREATE_CANDIDATE,
            commit_v2.REVISE_CANDIDATE,
            commit_v2.EQUIVALENCE_CANDIDATE,
        }
    }
    return _REQUIRED_OBJECTIVE_SLOT_CLASSES.issubset(
        current_classes | candidate_classes
    )


def _composition_result(
    *,
    selection: dict[str, Any],
    composition_status: str,
    failure_code: str | None,
    assistance_result_hash: str | None,
    candidate_operation_set_id: str | None,
    commit: dict[str, Any] | None,
) -> dict[str, Any]:
    if composition_status == DELEGATED_TO_CLOSED_PROTOCOL:
        handoff = [G60_CLOSED_PROTOCOL_CONTROL_OWNER]
    elif composition_status == NATURAL_CONVERSATION_COMMITTED:
        handoff = list(_NATURAL_HANDOFF_OWNER_ORDER)
    else:
        handoff = [G59_CONVERSATION_CLARIFICATION_OWNER]
    result = {
        "result_type": CONSTITUTIONAL_NATURAL_CONVERSATION_COMPOSITION_RESULT_V1,
        "runtime_version": CONSTITUTIONAL_NATURAL_CONVERSATION_BRANCH_COMPOSITION_V1,
        "composition_status": composition_status,
        "failure_code": failure_code,
        "selection_result": deepcopy(selection),
        "owner_handoff_order": handoff,
        "assistance_result_hash": assistance_result_hash,
        "candidate_operation_set_id": candidate_operation_set_id,
        "commit_identity": commit.get("commit_identity") if commit else None,
        "commit_disposition": commit.get("disposition") if commit else None,
        "commit_receipt_checksum": (
            commit.get("receipt_checksum") if commit else None
        ),
        "committed_global_revision": (
            commit.get("committed_global_revision") if commit else None
        ),
        "committed_semantic_revision": (
            commit.get("committed_semantic_revision") if commit else None
        ),
        "semantic_cwm_mutated_by_g59_commit": (
            commit.get("semantic_cwm_mutated") is True if commit else False
        ),
        "composition_owner_mutated_semantics": False,
        **deepcopy(_COMPOSITION_BOUNDARIES),
    }
    result["result_hash"] = replay_hash(result)
    return result


def validate_constitutional_natural_conversation_composition_result_v1(
    value: Any,
) -> dict[str, Any]:
    expected_fields = frozenset(
        {
            "result_type",
            "runtime_version",
            "composition_status",
            "failure_code",
            "selection_result",
            "owner_handoff_order",
            "assistance_result_hash",
            "candidate_operation_set_id",
            "commit_identity",
            "commit_disposition",
            "commit_receipt_checksum",
            "committed_global_revision",
            "committed_semantic_revision",
            "semantic_cwm_mutated_by_g59_commit",
            "composition_owner_mutated_semantics",
            *tuple(_COMPOSITION_BOUNDARIES),
            "result_hash",
        }
    )
    candidate = _closed_mapping(value, expected_fields, "composition result")
    if (
        candidate["result_type"]
        != CONSTITUTIONAL_NATURAL_CONVERSATION_COMPOSITION_RESULT_V1
        or candidate["runtime_version"]
        != CONSTITUTIONAL_NATURAL_CONVERSATION_BRANCH_COMPOSITION_V1
    ):
        _fail("Natural Conversation composition result type is invalid")
    validate_constitutional_natural_conversation_selection_result_v1(
        candidate["selection_result"]
    )
    body = deepcopy(candidate)
    actual_hash = body.pop("result_hash")
    if actual_hash != replay_hash(body):
        _fail("Natural Conversation composition result hash is invalid")
    if candidate["composition_owner_mutated_semantics"] is not False or any(
        candidate[field] is not False for field in _COMPOSITION_BOUNDARIES
    ):
        _fail("Natural Conversation composition acquired forbidden authority")
    if candidate["composition_status"] == NATURAL_CONVERSATION_COMMITTED:
        if (
            candidate["owner_handoff_order"]
            != list(_NATURAL_HANDOFF_OWNER_ORDER)
            or candidate["failure_code"] is not None
            or candidate["commit_disposition"]
            not in {commit_v2.COMMITTED, commit_v2.ALREADY_COMMITTED}
            or not all(
                isinstance(candidate[field], str) and candidate[field]
                for field in (
                    "assistance_result_hash",
                    "candidate_operation_set_id",
                    "commit_identity",
                    "commit_receipt_checksum",
                )
            )
        ):
            _fail("Natural Conversation committed result is incomplete")
    elif candidate["composition_status"] == DELEGATED_TO_CLOSED_PROTOCOL:
        if (
            candidate["owner_handoff_order"]
            != [G60_CLOSED_PROTOCOL_CONTROL_OWNER]
            or candidate["selection_result"]["selection_status"]
            != DELEGATED_TO_CLOSED_PROTOCOL
            or any(
                candidate[field] is not None
                for field in (
                    "failure_code",
                    "assistance_result_hash",
                    "candidate_operation_set_id",
                    "commit_identity",
                    "commit_disposition",
                    "commit_receipt_checksum",
                    "committed_global_revision",
                    "committed_semantic_revision",
                )
            )
            or candidate["semantic_cwm_mutated_by_g59_commit"] is not False
        ):
            _fail("Natural Conversation protocol delegation is invalid")
    elif candidate["composition_status"] == CLARIFICATION_REQUIRED:
        if (
            candidate["owner_handoff_order"]
            != [G59_CONVERSATION_CLARIFICATION_OWNER]
            or not isinstance(candidate["failure_code"], str)
            or not candidate["failure_code"]
            or any(
                candidate[field] is not None
                for field in (
                    "candidate_operation_set_id",
                    "commit_identity",
                    "commit_disposition",
                    "commit_receipt_checksum",
                    "committed_global_revision",
                    "committed_semantic_revision",
                )
            )
            or candidate["semantic_cwm_mutated_by_g59_commit"] is not False
        ):
            _fail("Natural Conversation clarification result is invalid")
    else:
        _fail("Natural Conversation composition disposition is invalid")
    canonical_serialize(candidate)
    return deepcopy(candidate)


def compose_constitutional_natural_conversation_branch_v1(
    *,
    runtime_root: str | Path,
    workspace_identity: str | Path,
    session_identity: str,
    current_state: dict[str, Any],
    source_turn_text: str,
    observed_at: str,
    selection_contract: dict[str, Any],
    workflow_model: CanonicalProductionWorkflowBranchModelV1 | Mapping[str, Any],
    binding_profile: dict[str, Any],
    admissibility_facts: Mapping[str, bool],
    evidence_identities: Mapping[str, str],
    interpreter_registry: list[dict[str, Any]],
    provider_registry: ProviderRegistry,
    provider_adapter: ProviderAdapter,
    selection_replay_dir: str | Path,
) -> dict[str, Any]:
    """Compose G59 selection -> G61 proposal -> G59 validation/commit."""

    state = machine_v2.validate_conversation_state_machine_state_v2(current_state)
    profile = _profile(binding_profile)
    selection = select_constitutional_natural_conversation_branch_v1(
        current_state=state,
        source_turn_text=source_turn_text,
        selection_contract=selection_contract,
        workflow_model=workflow_model,
        binding_profile=profile,
        admissibility_facts=admissibility_facts,
        evidence_identities=evidence_identities,
    )
    if selection["selection_status"] == DELEGATED_TO_CLOSED_PROTOCOL:
        return validate_constitutional_natural_conversation_composition_result_v1(
            _composition_result(
                selection=selection,
                composition_status=DELEGATED_TO_CLOSED_PROTOCOL,
                failure_code=None,
                assistance_result_hash=None,
                candidate_operation_set_id=None,
                commit=None,
            )
        )
    if selection["selection_status"] == SELECTION_FAILED_CLOSED:
        return validate_constitutional_natural_conversation_composition_result_v1(
            _composition_result(
                selection=selection,
                composition_status=CLARIFICATION_REQUIRED,
                failure_code=selection["failure_code"],
                assistance_result_hash=None,
                candidate_operation_set_id=None,
                commit=None,
            )
        )
    workspace = cwm_v2._normalize_workspace_identity(workspace_identity)
    session = _text(session_identity, "session identity")
    envelope = state["envelope"]
    persisted_state = cwm_v2.recover_conversation_working_memory_state_v2(
        runtime_root=runtime_root,
        workspace_identity=workspace,
        session_identity=session,
        observed_at=observed_at,
    )
    if (
        envelope["workspace_identity"] != workspace
        or envelope["session_identity"] != session
        or persisted_state is None
        or persisted_state != state
    ):
        return validate_constitutional_natural_conversation_composition_result_v1(
            _composition_result(
                selection=selection,
                composition_status=CLARIFICATION_REQUIRED,
                failure_code="CONVERSATION_STATE_BINDING_STALE",
                assistance_result_hash=None,
                candidate_operation_set_id=None,
                commit=None,
            )
        )
    assistance: dict[str, Any] | None = None
    try:
        assistance = _validate_epp_result(
            epp_v1.run_conversation_interpreter_epp_assistance_v1(
                current_state=state,
                source_turn_text=source_turn_text,
                observed_at=observed_at,
                binding_profile=profile,
                interpreter_registry=interpreter_registry,
                provider_registry=provider_registry,
                provider_adapter=provider_adapter,
                selection_replay_dir=selection_replay_dir,
            ),
            profile,
        )
        if assistance["adapter_status"] != epp_v1.NORMALIZED_AND_VALIDATED:
            _fail(assistance.get("failure_code") or "G61_PROPOSAL_REJECTED")
        candidate_set = proposal_v2.validate_candidate_operation_set_v2(
            assistance["candidate_operation_set"]
        )
        if (
            candidate_set["validation_disposition"] != proposal_v2.ADMISSIBLE
            or candidate_set["clarification_required"] is not False
            or candidate_set["reduction_allowed"] is not True
        ):
            _fail("G59_CANDIDATE_NOT_ADMISSIBLE")
        if not _candidate_covers_required_objective_slots(state, candidate_set):
            _fail("REQUIRED_OBJECTIVE_SLOT_COVERAGE_INCOMPLETE")
        commit = commit_v2.commit_proposal_candidate_operations_v2(
            runtime_root=runtime_root,
            workspace_identity=workspace_identity,
            session_identity=session,
            candidate_operation_set=candidate_set,
            expected_revision=state["revision"],
            committed_at=observed_at,
        )
        if (
            commit["disposition"] not in {commit_v2.COMMITTED, commit_v2.ALREADY_COMMITTED}
            or commit["candidate_operation_set_id"]
            != candidate_set["candidate_operation_set_id"]
            or commit["objective_created"] is not False
            or commit["objective_commitment_invoked"] is not False
            or commit["platform_core_invoked"] is not False
            or commit["authorization_invoked"] is not False
            or commit["worker_invoked"] is not False
            or commit["execution_invoked"] is not False
            or commit["replay_written"] is not False
        ):
            _fail("G59_PROPOSAL_COMMIT_BOUNDARY_INVALID")
        committed_classes = {
            slot["slot_class"]
            for slot in commit["state"]["semantic_memory"]["semantic_slots"]
            if slot["status"] not in {cwm_v2.CONFLICTED, cwm_v2.STALE}
        }
        if not _REQUIRED_OBJECTIVE_SLOT_CLASSES.issubset(committed_classes):
            _fail("G59_COMMITTED_OBJECTIVE_SLOT_COVERAGE_INCOMPLETE")
        return validate_constitutional_natural_conversation_composition_result_v1(
            _composition_result(
                selection=selection,
                composition_status=NATURAL_CONVERSATION_COMMITTED,
                failure_code=None,
                assistance_result_hash=assistance["result_hash"],
                candidate_operation_set_id=candidate_set[
                    "candidate_operation_set_id"
                ],
                commit=commit,
            )
        )
    except Exception as exc:
        failure_code = (
            exc.reason_code
            if isinstance(exc, commit_v2.ProposalCommitError)
            else str(exc)
        )
        return validate_constitutional_natural_conversation_composition_result_v1(
            _composition_result(
                selection=selection,
                composition_status=CLARIFICATION_REQUIRED,
                failure_code=_text(failure_code, "failure code"),
                assistance_result_hash=(
                    assistance.get("result_hash")
                    if isinstance(assistance, dict)
                    else None
                ),
                candidate_operation_set_id=None,
                commit=None,
            )
        )


__all__ = [
    "CLARIFICATION_REQUIRED",
    "CLOSED_PROTOCOL_CONTROL_BRANCH",
    "CONSTITUTIONAL_NATURAL_CONVERSATION_BRANCH_COMPOSITION_V1",
    "CONSTITUTIONAL_NATURAL_CONVERSATION_COMPOSITION_RESULT_V1",
    "CONSTITUTIONAL_NATURAL_CONVERSATION_SELECTION_CONTRACT_V1",
    "CONVERSATION_CLARIFICATION_BRANCH",
    "DELEGATED_TO_CLOSED_PROTOCOL",
    "NATURAL_CONVERSATION_COMMITTED",
    "NATURAL_CONVERSATION_EPP_BRANCH",
    "NATURAL_CONVERSATION_SELECTED",
    "SELECTION_FAILED_CLOSED",
    "compose_constitutional_natural_conversation_branch_v1",
    "create_constitutional_natural_conversation_selection_contract_v1",
    "select_constitutional_natural_conversation_branch_v1",
    "validate_constitutional_natural_conversation_composition_result_v1",
    "validate_constitutional_natural_conversation_selection_contract_v1",
    "validate_constitutional_natural_conversation_selection_result_v1",
]
