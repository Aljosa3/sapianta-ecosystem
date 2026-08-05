from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, replace
from hashlib import sha256
from pathlib import Path

import pytest

from aigol.runtime.constitutional_production_workflow_branch_contract_v1 import (
    CANONICAL_PRODUCTION_WORKFLOW_BRANCH_CONTRACT_VERSION,
    CANONICAL_WORKFLOW_BRANCH_ORDER,
    CERTIFIED_REUSE,
    CONSTITUTIONAL_COMPLETION,
    CONTENT_OR_REPOSITORY_MUTATION,
    GOVERNED_ACTION,
    GOVERNED_DEVELOPMENT,
    HUMAN_RETURN,
    NON_MUTATING_CAPABILITY,
    READ_ONLY,
    CanonicalProductionWorkflowBranchModelV1,
    CanonicalWorkflowBranchProvenanceV1,
    CanonicalWorkflowEvidenceReferenceV1,
    bind_canonical_workflow_branch_provenance_v1,
    create_canonical_production_workflow_branch_model_v1,
    validate_canonical_production_workflow_branch_model_v1,
    validate_canonical_workflow_branch_journey_v1,
    validate_canonical_workflow_branch_provenance_v1,
)
from aigol.runtime.models import FailClosedRuntimeError


MODULE = Path(
    "aigol/runtime/constitutional_production_workflow_branch_contract_v1.py"
)
OBSERVED_AT = "2026-08-05T10:00:00Z"


def _model() -> CanonicalProductionWorkflowBranchModelV1:
    return create_canonical_production_workflow_branch_model_v1()


def _definition(model, branch_kind):
    return next(
        item for item in model.branch_definitions if item.branch_kind == branch_kind
    )


def _evidence(model, branch_kind):
    definition = _definition(model, branch_kind)
    return tuple(
        CanonicalWorkflowEvidenceReferenceV1(
            evidence_role=item.evidence_role,
            producing_owner=item.producing_owner,
            artifact_identity=f"{branch_kind}-{item.evidence_role}",
            artifact_digest="sha256:"
            + sha256(
                f"{branch_kind}:{item.evidence_role}".encode("utf-8")
            ).hexdigest(),
        )
        for item in definition.required_evidence
    )


def _bind(model, branch_kind, sequence, previous=None):
    definition = _definition(model, branch_kind)
    return bind_canonical_workflow_branch_provenance_v1(
        model=model,
        source_request_identity="request-G69-15",
        source_interaction_identity="interaction-G69-15",
        branch_sequence=sequence,
        branch_kind=branch_kind,
        predecessor_branch_kind=None if previous is None else previous.branch_kind,
        previous_provenance_identity=(
            None if previous is None else previous.provenance_identity
        ),
        predicate_facts={
            definition.predicate.fact_name: definition.predicate.expected_value
        },
        evidence_references=_evidence(model, branch_kind),
        observed_at=OBSERVED_AT,
    )


def _journey(branch_kinds):
    model = _model()
    provenances = []
    for sequence, branch_kind in enumerate(branch_kinds, start=1):
        provenances.append(
            _bind(
                model,
                branch_kind,
                sequence,
                None if not provenances else provenances[-1],
            )
        )
    return model, tuple(provenances)


def test_model_is_complete_closed_and_preserves_one_production_lineage():
    model = validate_canonical_production_workflow_branch_model_v1(_model())

    assert model.contract_version == (
        CANONICAL_PRODUCTION_WORKFLOW_BRANCH_CONTRACT_VERSION
    )
    assert tuple(item.branch_kind for item in model.branch_definitions) == (
        CANONICAL_WORKFLOW_BRANCH_ORDER
    )
    assert model.che_definition_count == 1
    assert model.production_hic_family_count == 1
    assert model.production_owner_chain_count == 1
    assert model.production_path_count == 1
    assert model.parallel_production_path_count == 0
    assert model.hic_responsibility == "TRANSPORT_ONLY"
    assert model.hic_semantic_capability == "NO_SEMANTIC_CAPABILITY"
    assert model.workflow_execution_capability == "NO_WORKFLOW_EXECUTION"
    assert (
        model.production_route_creation_capability
        == "NO_PRODUCTION_ROUTE_CREATION"
    )


def test_model_identity_is_deterministic_and_round_trips():
    first = _model()
    second = _model()

    assert first == second
    assert first.model_identity == second.model_identity
    assert (
        validate_canonical_production_workflow_branch_model_v1(first.to_dict())
        == first
    )


@pytest.mark.parametrize("branch_kind", CANONICAL_WORKFLOW_BRANCH_ORDER)
def test_each_branch_binds_exact_predicate_and_owner_provenance(branch_kind):
    model = _model()
    definition = _definition(model, branch_kind)
    predecessor = (
        None
        if not definition.allowed_predecessor_branches
        else CanonicalWorkflowBranchProvenanceV1(
            contract_version=CANONICAL_PRODUCTION_WORKFLOW_BRANCH_CONTRACT_VERSION,
            provenance_identity="preceding-owner-evidence",
            model_identity=model.model_identity,
            source_request_identity="request-G69-15",
            source_interaction_identity="interaction-G69-15",
            branch_sequence=1,
            branch_kind=definition.allowed_predecessor_branches[0],
            predecessor_branch_kind=None,
            previous_provenance_identity=None,
            predicate_facts={"fixture": "bounded"},
            evidence_references=(),
            observed_at=OBSERVED_AT,
        )
    )

    provenance = _bind(model, branch_kind, 1 if predecessor is None else 2, predecessor)

    assert (
        validate_canonical_workflow_branch_provenance_v1(
            model=model,
            value=provenance.to_dict(),
        )
        == provenance
    )


@pytest.mark.parametrize(
    "branch_kinds",
    (
        (READ_ONLY, HUMAN_RETURN),
        (
            GOVERNED_ACTION,
            CERTIFIED_REUSE,
            NON_MUTATING_CAPABILITY,
            HUMAN_RETURN,
        ),
        (
            GOVERNED_ACTION,
            GOVERNED_DEVELOPMENT,
            NON_MUTATING_CAPABILITY,
            HUMAN_RETURN,
        ),
        (
            GOVERNED_ACTION,
            CERTIFIED_REUSE,
            CONTENT_OR_REPOSITORY_MUTATION,
            HUMAN_RETURN,
        ),
        (
            GOVERNED_ACTION,
            GOVERNED_DEVELOPMENT,
            CONTENT_OR_REPOSITORY_MUTATION,
            CONSTITUTIONAL_COMPLETION,
            HUMAN_RETURN,
        ),
    ),
)
def test_certified_constitutional_journeys_close_at_human_return(branch_kinds):
    model, provenances = _journey(branch_kinds)

    assert validate_canonical_workflow_branch_journey_v1(
        model=model,
        provenances=provenances,
    ) == provenances


def test_predicate_mismatch_fails_closed():
    model = _model()

    with pytest.raises(
        FailClosedRuntimeError,
        match="predicate facts do not match",
    ):
        bind_canonical_workflow_branch_provenance_v1(
            model=model,
            source_request_identity="request-G69-15",
            source_interaction_identity="interaction-G69-15",
            branch_sequence=1,
            branch_kind=READ_ONLY,
            predecessor_branch_kind=None,
            previous_provenance_identity=None,
            predicate_facts={"route_class": GOVERNED_ACTION},
            evidence_references=_evidence(model, READ_ONLY),
            observed_at=OBSERVED_AT,
        )


def test_missing_or_wrong_owner_evidence_fails_closed():
    model = _model()
    definition = _definition(model, READ_ONLY)
    facts = {definition.predicate.fact_name: definition.predicate.expected_value}

    with pytest.raises(FailClosedRuntimeError, match="owner evidence"):
        bind_canonical_workflow_branch_provenance_v1(
            model=model,
            source_request_identity="request-G69-15",
            source_interaction_identity="interaction-G69-15",
            branch_sequence=1,
            branch_kind=READ_ONLY,
            predecessor_branch_kind=None,
            previous_provenance_identity=None,
            predicate_facts=facts,
            evidence_references=_evidence(model, READ_ONLY)[:-1],
            observed_at=OBSERVED_AT,
        )

    with pytest.raises(FailClosedRuntimeError, match="owner evidence or sequence"):
        bind_canonical_workflow_branch_provenance_v1(
            model=model,
            source_request_identity="request-G69-15",
            source_interaction_identity="interaction-G69-15",
            branch_sequence=1,
            branch_kind=READ_ONLY,
            predecessor_branch_kind=None,
            previous_provenance_identity=None,
            predicate_facts=facts,
            evidence_references=tuple(reversed(_evidence(model, READ_ONLY))),
            observed_at=OBSERVED_AT,
        )

    wrong_owner = replace(
        _evidence(model, READ_ONLY)[0],
        producing_owner="UNAUTHORIZED_OWNER",
    )
    with pytest.raises(FailClosedRuntimeError, match="owner evidence"):
        bind_canonical_workflow_branch_provenance_v1(
            model=model,
            source_request_identity="request-G69-15",
            source_interaction_identity="interaction-G69-15",
            branch_sequence=1,
            branch_kind=READ_ONLY,
            predecessor_branch_kind=None,
            previous_provenance_identity=None,
            predicate_facts=facts,
            evidence_references=(wrong_owner, *_evidence(model, READ_ONLY)[1:]),
            observed_at=OBSERVED_AT,
        )


def test_unpermitted_predecessor_and_incomplete_journey_fail_closed():
    model = _model()
    initial = _bind(model, GOVERNED_ACTION, 1)
    definition = _definition(model, NON_MUTATING_CAPABILITY)

    with pytest.raises(FailClosedRuntimeError, match="predecessor is not permitted"):
        bind_canonical_workflow_branch_provenance_v1(
            model=model,
            source_request_identity="request-G69-15",
            source_interaction_identity="interaction-G69-15",
            branch_sequence=2,
            branch_kind=NON_MUTATING_CAPABILITY,
            predecessor_branch_kind=GOVERNED_ACTION,
            previous_provenance_identity=initial.provenance_identity,
            predicate_facts={
                definition.predicate.fact_name: definition.predicate.expected_value
            },
            evidence_references=_evidence(model, NON_MUTATING_CAPABILITY),
            observed_at=OBSERVED_AT,
        )

    with pytest.raises(FailClosedRuntimeError, match="does not terminate"):
        validate_canonical_workflow_branch_journey_v1(
            model=model,
            provenances=(initial,),
        )


def test_constitutional_completion_requires_governed_development_lineage():
    model, provenances = _journey(
        (
            GOVERNED_ACTION,
            CERTIFIED_REUSE,
            CONTENT_OR_REPOSITORY_MUTATION,
            CONSTITUTIONAL_COMPLETION,
            HUMAN_RETURN,
        )
    )

    with pytest.raises(
        FailClosedRuntimeError,
        match="lacks governed-development lineage",
    ):
        validate_canonical_workflow_branch_journey_v1(
            model=model,
            provenances=provenances,
        )


def test_tampered_model_and_provenance_identity_fail_closed():
    model = _model()
    with pytest.raises(FailClosedRuntimeError, match="production invariants"):
        validate_canonical_production_workflow_branch_model_v1(
            replace(model, production_path_count=2)
        )

    provenance = _bind(model, READ_ONLY, 1)
    with pytest.raises(FailClosedRuntimeError, match="identity is invalid"):
        validate_canonical_workflow_branch_provenance_v1(
            model=model,
            value=replace(provenance, provenance_identity="tampered"),
        )


def test_models_and_predicate_fact_maps_are_immutable():
    model = _model()
    provenance = _bind(model, READ_ONLY, 1)

    with pytest.raises(FrozenInstanceError):
        model.production_path_count = 2
    with pytest.raises(TypeError):
        provenance.predicate_facts["route_class"] = GOVERNED_ACTION


def test_contract_has_no_production_or_historical_runtime_dependency():
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    imported_modules = set()
    function_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            function_names.add(node.name)

    assert imported_modules == {
        "__future__",
        "dataclasses",
        "hashlib",
        "json",
        "types",
        "typing",
        "aigol.runtime.models",
    }
    assert not any(
        name.startswith(prefix)
        for name in function_names
        for prefix in ("route_", "select_", "execute_", "persist_", "mutate_")
    )
