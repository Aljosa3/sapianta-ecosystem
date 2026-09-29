"""Focused caller-composition characterization; no materialization or authority."""
from copy import deepcopy
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
OWNER = ROOT / '.github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py'
SPEC = importlib.util.spec_from_file_location('fm_materialization_admission', OWNER)
FM = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FM)
S1_PATH = ROOT / '.github/governance/evidence/g77_256p11s1_wrong_scope_bootstrap_v1/live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json'
S0_PATH = ROOT / '.github/governance/evidence/p11_wrong_scope_non_consuming_preflight_v1/live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json'


class BeforeEffects(Exception):
    pass


@pytest.fixture
def state(monkeypatch):
    c = FM.fresh_context.load_context(S1_PATH, repository_root=ROOT)
    head = FM.git(ROOT, 'rev-parse', 'HEAD')
    tree = FM.git(ROOT, 'rev-parse', 'HEAD^{tree}')
    proof = FM.build_committed_review_transition(repository_root=ROOT, context=c, current_admission_head=head, current_admission_tree=tree)
    def stop(*args, **kwargs):
        raise BeforeEffects
    monkeypatch.setattr(FM.fresh_context, 'validate_freshness', stop)
    return c, head, tree, proof


def run(c, proofs):
    return FM.materialize_operation_state(repository_root=ROOT, context=c,
                                         context_source_path=S1_PATH,
                                         committed_review_transitions=proofs)


def test_native_authentication_precedes_guard_and_preserves_all_identities(state, monkeypatch):
    c, h, t, proof = state
    before = deepcopy(c)
    calls = []
    authenticate = FM.authenticate_review_to_current_admission
    guard = FM.authenticate_current_committed_jm_route
    def auth(**kw):
        result = authenticate(**kw)
        calls.append(('AUTHENTICATED', kw['observed_head'], kw['observed_tree']))
        return result
    def checked(root, head, tree, **kw):
        assert calls == [('AUTHENTICATED', h, t)]
        assert kw['context'] == before
        result = guard(root, head, tree, **kw)
        calls.append(('GUARD_PASS', head, tree))
        return result
    monkeypatch.setattr(FM, 'authenticate_review_to_current_admission', auth)
    monkeypatch.setattr(FM, 'authenticate_current_committed_jm_route', checked)
    with pytest.raises(BeforeEffects): run(c, [proof])
    assert calls == [('AUTHENTICATED', h, t), ('GUARD_PASS', h, t)]
    assert c == before
    assert (c['repository_head'], c['repository_tree']) != (h, t)


@pytest.mark.parametrize('kind', ['missing', 'empty', 'raw_coordinates', 'wrong_head', 'wrong_tree', 's0_proof'])
def test_unauthenticated_current_coordinates_rejected_before_guard(state, monkeypatch, kind):
    c, h, t, proof = state
    proofs = [deepcopy(proof)]
    if kind == 'missing': proofs = None
    elif kind == 'empty': proofs = []
    elif kind == 'raw_coordinates': proofs = [{'current_admission_head': h, 'current_admission_tree': t}]
    elif kind == 'wrong_head': proofs[0]['current_admission_head'] = '0' * 40
    elif kind == 'wrong_tree': proofs[0]['current_admission_tree'] = '0' * 40
    else:
        s0 = FM.fresh_context.load_context(S0_PATH, repository_root=ROOT)
        proofs = [FM.build_committed_review_transition(repository_root=ROOT, context=s0, current_admission_head=h, current_admission_tree=t)]
    def forbidden(*a, **kw): pytest.fail('guard reached before authenticated S1 admission')
    monkeypatch.setattr(FM, 'authenticate_current_committed_jm_route', forbidden)
    with pytest.raises(RuntimeError): run(c, proofs)


def test_review_base_cannot_be_passed_as_current_identity(state):
    c, _, _, _ = state
    with pytest.raises(RuntimeError, match='not the current repository identity'):
        FM.authenticate_current_committed_jm_route(ROOT, c['repository_head'], c['repository_tree'], context=c)


@pytest.mark.parametrize('field', ['review_head', 'review_tree', 'checkout_head', 'checkout_tree', 'bootstrap', 'candidate'])
def test_resealed_subject_tampering_rejected_before_guard(state, monkeypatch, field):
    c, _, _, proof = state
    c = deepcopy(c)
    if field == 'review_head': c['repository_head'] = '0' * 40
    elif field == 'review_tree': c['repository_tree'] = '0' * 40
    elif field.startswith('checkout_'): c['qemu_executable_base_seed_checkout_bindings']['checkout'][field.split('_')[1]] = '0' * 40
    elif field == 'bootstrap': c['wrapper_fc_er_che_schema_hashes']['cloud_init'] = '0' * 64
    else: c['candidate_manifest_sha256'] = '0' * 64
    c.pop('context_sha256')
    c = FM.fresh_context.seal_context(c)
    def forbidden(*a, **kw): pytest.fail('tampered S1 reached route guard')
    monkeypatch.setattr(FM, 'authenticate_current_committed_jm_route', forbidden)
    with pytest.raises((RuntimeError, ValueError, FM.subprocess.CalledProcessError)):
        run(c, [proof])


@pytest.mark.parametrize('vector', ['WRONG_SCOPE', 'WRONG_ATTEMPT', 'WRONG_INPUT', 'WRONG_CONTRACT', 'WRONG_PROVENANCE', 'FUTURE', 'EXPIRED'])
def test_existing_same_head_materializer_composition_preserved(state, monkeypatch, vector):
    _, h, t, _ = state
    c = FM.build_operation_context(repository_root=ROOT, repository_head=h, repository_tree=t,
        generation_identity=f'G77_256MC_ONE_FRESH_HUMAN_AUTHORIZED_{vector}_OPERATIONAL_COMMISSIONING_V1',
        operation_identity='G77_256MC_PREFLIGHT_001', identity_namespace_prefix='G77_256MC',
        operation_evidence_root=ROOT / f'.github/governance/evidence/g77_256mc_{vector.lower()}_test_v1/operation_state',
        transient_root=Path('/tmp/g77_256mc_not_materialized'))
    if vector == 'WRONG_SCOPE':
        with pytest.raises(BeforeEffects): run(c, None)
    else:
        # Existing current repository contains CURRENT P11; unchanged legacy guards reject it.
        with pytest.raises(RuntimeError, match='current route target does not contain committed JM P11'):
            run(c, None)
