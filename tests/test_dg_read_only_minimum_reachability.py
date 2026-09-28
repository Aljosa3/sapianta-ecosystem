"""Accepted READ_ONLY intake uses the canonical DG lifecycle without execution."""
from dataclasses import asdict, replace
import json
from pathlib import Path

import pytest

from aigol.runtime import constitutional_development_governance_operational_integration as integration
from aigol.runtime import constitutional_development_governance_orchestration as dg
from aigol.runtime.transport.serialization import replay_hash

SUBJECT = Path(__file__).parent / 'fixtures/dg_read_only_subject.json'
CREATED_AT = '2026-09-28T00:00:00Z'


def recovered_subject():
    data = json.loads(SUBJECT.read_text())
    intake = dg.DevelopmentGovernanceTaskIntake(**{
        k: tuple(v) if isinstance(v, list) else v
        for k, v in data['task_intake'].items()
    })
    assert replay_hash(asdict(intake)) == 'sha256:1ba00d57675cfc173237907fcb2c298ee35a5db5ae42b99c424c2c0d826cac32'
    assert replay_hash(data['request']) == intake.request_identity
    return data['request'], intake


def supported_subject():
    _, intake = recovered_subject()
    request = 'Explain platform knowledge'
    return request, replace(
        intake, request_identity=replay_hash(request), objective=request,
        intake_id=integration._identity('DG-INTAKE', replay_hash(request)),
        bounded_scope=('PLATFORM_KNOWLEDGE',),
    )


def invoke(tmp_path, request, intake, **kwargs):
    return integration.integrate_constitutional_development_governance(
        request=request, task_intake=intake, workspace=tmp_path,
        created_at=CREATED_AT, **kwargs,
    )


def forbid(*args, **kwargs):
    pytest.fail('READ_ONLY reached an unauthorized downstream operation')


@pytest.fixture(autouse=True)
def prohibit_operations(monkeypatch):
    for name in (
        'compose_governance_eligible_implementation_turn_durable_work_binding',
        '_persist_record', 'prepare_implementation_turn_capability_coverage',
        'validate_reuse_proof_production_admission',
    ):
        monkeypatch.setattr(integration, name, forbid)


def test_exact_subject_reaches_evidence_and_terminates_before_cdd(tmp_path, monkeypatch):
    request, intake = recovered_subject()
    before = asdict(intake)
    calls = []
    discover = integration.discover_platform_capability_composition_coverage
    validate = integration._validate_evidence_reference

    def acquire(**kwargs):
        assert kwargs['query'] == intake.objective
        result = discover(**kwargs)
        calls.append(result)
        return result

    validated = []
    def check(item, **kwargs):
        validate(item, **kwargs)
        validated.append(item.source_reference)

    monkeypatch.setattr(integration, 'discover_platform_capability_composition_coverage', acquire)
    monkeypatch.setattr(integration, '_validate_evidence_reference', check)
    monkeypatch.setattr(integration, 'DevelopmentGovernanceCDDClassification', forbid)
    monkeypatch.setattr(integration, 'orchestrate_constitutional_development_governance', forbid)
    with pytest.raises(dg.DevelopmentGovernanceRuntimeError, match='TERMINATE_WITHOUT_CDD'):
        invoke(tmp_path, request, intake)
    assert len(calls) == 1
    assert calls[0]['coverage_status'] == 'CAPABILITY_COMPOSITION_COVERAGE_FAILED_CLOSED'
    assert validated
    assert asdict(intake) == before
    assert list(tmp_path.iterdir()) == []


def test_supported_subject_uses_existing_cdd_bundle_and_validators(tmp_path, monkeypatch):
    request, intake = supported_subject()
    captured = {}
    orchestrate = integration.orchestrate_constitutional_development_governance
    def capture(**kwargs):
        captured.update(kwargs)
        return orchestrate(**kwargs)
    monkeypatch.setattr(integration, 'orchestrate_constitutional_development_governance', capture)
    result = invoke(tmp_path, request, intake)
    assert captured['task_intake'] is intake
    cdd = captured['cdd_classification']
    assert cdd.intake_id == intake.intake_id
    assert cdd.action_mode == intake.action_mode == 'READ_ONLY'
    assert cdd.affected_scope == intake.bounded_scope
    assert cdd.baseline_reference == intake.active_baseline_reference
    assert cdd.primary_work_class == 'CAPABILITY'
    assert cdd.authority_impact == 'NONE'
    assert cdd.mutation_layer == 'NOT_APPLICABLE'
    assert cdd.realization_impact == 'NONE'
    assert captured['need_assessment'].outcome == 'NO_IMPLEMENTATION_REQUIRED'
    assert captured['governance_disposition'].governance_disposition == 'READ_ONLY_WORK_MAY_CONTINUE'
    assert captured['planning_eligibility'].planning_eligible is False
    stages = tuple(captured[name] for name in (
        'task_intake', 'cdd_classification', 'evidence_snapshot',
        'need_assessment', 'governance_disposition', 'planning_eligibility',
    ))
    bundle = orchestrate(**captured)
    reconstructed = dg.reconstruct_constitutional_development_governance_bundle(
        bundle=bundle, stage_outputs=stages,
    )
    assert result == asdict(reconstructed)
    assert invoke(tmp_path, request, intake) == result
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize('field,value,match', [
    ('request_identity', 'sha256:' + '0'*64, 'request mismatch'),
    ('action_mode', 'REPOSITORY_MUTATION_REQUESTED', 'must be READ_ONLY'),
    ('active_baseline_reference', 'OTHER_BASELINE', 'baseline mismatch'),
    ('bounded_scope', ('OTHER_SCOPE',), 'TERMINATE_WITHOUT_CDD'),
    ('clarification_requirements', ('CLARIFY',), 'TERMINATE_WITHOUT_CDD'),
])
def test_binding_and_ambiguity_fail_closed(tmp_path, field, value, match):
    request, intake = supported_subject()
    with pytest.raises(dg.DevelopmentGovernanceRuntimeError, match=match):
        invoke(tmp_path, request, replace(intake, **{field: value}))


@pytest.mark.parametrize('field,value', [
    ('content_hash', 'sha256:' + '0'*64),
    ('canonical_owner', 'UNAUTHORIZED_OWNER'),
    ('source_reference', 'AGENTS.md'),
    ('supersession_state', 'SUPERSEDED'),
    ('compatibility_scope', 'OTHER_BASELINE'),
    ('certification_status', 'UNKNOWN'),
])
@pytest.mark.parametrize('supported', [True, False])
def test_authoritative_source_corruption_fails_before_cdd(tmp_path, monkeypatch, field, value, supported):
    request, intake = supported_subject() if supported else recovered_subject()
    original = integration._evidence_reference
    def corrupt(**kwargs):
        return replace(original(**kwargs), **{field: value})
    monkeypatch.setattr(integration, '_evidence_reference', corrupt)
    monkeypatch.setattr(integration, 'DevelopmentGovernanceCDDClassification', forbid)
    with pytest.raises(dg.DevelopmentGovernanceRuntimeError) as caught:
        invoke(tmp_path, request, intake)
    assert 'TERMINATE_WITHOUT_CDD' not in str(caught.value)


@pytest.mark.parametrize('field,value', [
    ('project_objective_artifact', {}), ('knowledge_reuse_artifact', {}),
    ('workspace_state', {}), ('replay_dir', '.'), ('reuse_proof_admission', {}),
])
def test_operational_inputs_cannot_use_read_only_entry(tmp_path, field, value):
    request, intake = supported_subject()
    with pytest.raises(dg.DevelopmentGovernanceRuntimeError, match='operational inputs'):
        invoke(tmp_path, request, intake, **{field: value})


def test_missing_authoritative_source_fails_before_cdd(tmp_path, monkeypatch):
    request, intake = recovered_subject()
    original = Path.read_bytes
    def unavailable(path):
        if path.name == 'G20_03_PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_RUNTIME_IMPLEMENTATION.md':
            raise FileNotFoundError('authoritative source unavailable')
        return original(path)
    monkeypatch.setattr(Path, 'read_bytes', unavailable)
    monkeypatch.setattr(integration, 'DevelopmentGovernanceCDDClassification', forbid)
    with pytest.raises((FileNotFoundError, dg.DevelopmentGovernanceRuntimeError)):
        invoke(tmp_path, request, intake)


def test_downstream_binding_tamper_is_rejected(tmp_path, monkeypatch):
    request, intake = supported_subject()
    original = integration._compose_stage_outputs
    def tamper(**kwargs):
        stages = list(original(**kwargs))
        stages[1] = replace(stages[1], intake_id='UNRELATED_INTAKE')
        return tuple(stages)
    monkeypatch.setattr(integration, '_compose_stage_outputs', tamper)
    with pytest.raises(dg.DevelopmentGovernanceRuntimeError, match='does not bind'):
        invoke(tmp_path, request, intake)
