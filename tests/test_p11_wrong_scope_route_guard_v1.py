"""Focused repository-only guard tests: no authority issuance or VM entry."""
import ast
from copy import deepcopy
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / '.github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py'
spec = importlib.util.spec_from_file_location('route_guard_fm', PATH)
FM = importlib.util.module_from_spec(spec)
spec.loader.exec_module(FM)


def context(vector='WRONG_SCOPE'):
    head = FM.git(ROOT, 'rev-parse', 'HEAD')
    tree = FM.git(ROOT, 'rev-parse', 'HEAD^{tree}')
    return FM.build_operation_context(
        repository_root=ROOT, repository_head=head, repository_tree=tree,
        generation_identity=f'G77_256GUARD_ONE_FRESH_HUMAN_AUTHORIZED_{vector}_OPERATIONAL_COMMISSIONING_V1',
        operation_identity='G77_256GUARD_REPOSITORY_PROOF_001',
        identity_namespace_prefix='G77_256GUARD',
        operation_evidence_root=ROOT / f'.github/governance/evidence/g77_256guard_{vector.lower()}_proof_v1/operation_state',
        transient_root=Path('/tmp/g77_256guard_repository_proof'),
    )


def guard(c, **kw):
    return FM.authenticate_current_committed_jm_route(ROOT, c['repository_head'], c['repository_tree'], context=c, **kw)


def substitute_committed(monkeypatch, data):
    original = subprocess.check_output
    def checked(argv, *a, **kw):
        if argv[:2] == ['git', 'show'] and argv[2].endswith(':' + FM.P11_CONSUMER_RELATIVE):
            return data
        return original(argv, *a, **kw)
    monkeypatch.setattr(FM.subprocess, 'check_output', checked)


def test_same_native_guard_selector_and_consumer():
    c = context()
    assert guard(c) is None
    assert FM.governed_checkout_identity(ROOT, 'WRONG_SCOPE', c['repository_head'], c['repository_tree']) == (c['repository_head'], c['repository_tree'])
    committed = subprocess.check_output(['git', 'show', c['repository_head'] + ':' + FM.P11_CONSUMER_RELATIVE], cwd=ROOT)
    assert hashlib.sha256(committed).hexdigest() == FM.WRONG_SCOPE_CURRENT_CONSUMER_SHA256
    sys.path.insert(0, str(ROOT / 'tests'))
    from p11_da_operational_consumer_v1 import authenticate_preclaim_temporal_binding
    assert authenticate_preclaim_temporal_binding(c)[0]['coordinate_unix_ns'] == 500


@pytest.mark.parametrize('kind', ['legacy', 'arbitrary'])
def test_wrong_scope_rejects_wrong_committed_consumer(monkeypatch, kind):
    c = context()
    data = subprocess.check_output(['git', 'show', '9a8f8b15:tests/p11_da_operational_consumer_v1.py'], cwd=ROOT) if kind == 'legacy' else b'arbitrary'
    substitute_committed(monkeypatch, data)
    with pytest.raises(RuntimeError, match='binding mismatch'): guard(c)


@pytest.mark.parametrize('vector', sorted(FM.fresh_context.SUPPORTED_VECTORS - {'WRONG_SCOPE'}) if hasattr(FM.fresh_context, 'SUPPORTED_VECTORS') else ['WRONG_ATTEMPT','WRONG_INPUT','WRONG_CONTRACT','WRONG_PROVENANCE','FUTURE','EXPIRED'])
def test_other_vectors_retain_legacy_guard(monkeypatch, vector):
    c = context(vector)
    with pytest.raises(RuntimeError, match='committed JM P11'): guard(c)
    legacy = subprocess.check_output(['git', 'show', '9a8f8b15:tests/p11_da_operational_consumer_v1.py'], cwd=ROOT)
    assert hashlib.sha256(legacy).hexdigest() == FM.COMMITTED_JM_P11_SHA256
    substitute_committed(monkeypatch, legacy)
    assert guard(c) is None


def test_no_context_is_not_wrong_scope_opt_in():
    c = context()
    with pytest.raises(RuntimeError, match='committed JM P11'):
        FM.authenticate_current_committed_jm_route(ROOT, c['repository_head'], c['repository_tree'])


@pytest.mark.parametrize('mutation', ['unsealed', 'temporal', 'vector', 'wrapper'])
def test_context_mismatch_rejected(mutation):
    c = deepcopy(context())
    if mutation == 'unsealed': c['operation_identity'] += '_CHANGED'
    elif mutation == 'temporal': c['preclaim_temporal_binding']['coordinate_unix_ns'] = 1000
    elif mutation == 'vector': c['generation_identity'] = c['generation_identity'].replace('WRONG_SCOPE', 'EXPIRED')
    else: c['guest_adapter_binding']['source_sha256'] = '0' * 64
    if mutation != 'unsealed':
        c.pop('context_sha256'); c = FM.fresh_context.seal_context(c)
    with pytest.raises((RuntimeError, ValueError)): guard(c)


@pytest.mark.parametrize('field', ['head','tree'])
def test_head_tree_mismatch(field):
    c = context()
    with pytest.raises(RuntimeError, match='repository identity'):
        FM.authenticate_current_committed_jm_route(ROOT, '0'*40 if field=='head' else c['repository_head'], '0'*40 if field=='tree' else c['repository_tree'], context=c)


def test_working_consumer_tamper(monkeypatch):
    c = context(); original = FM.sha256_path
    monkeypatch.setattr(FM, 'sha256_path', lambda p: '0'*64 if Path(p)==ROOT/FM.P11_CONSUMER_RELATIVE else original(p))
    with pytest.raises(RuntimeError, match='binding mismatch'): guard(c)


def test_expired_stable_checkout_unchanged():
    c = context('EXPIRED')
    assert FM.governed_checkout_identity(ROOT, 'EXPIRED', c['repository_head'], c['repository_tree']) == (FM.EXPIRED_CHECKOUT_HEAD, FM.EXPIRED_CHECKOUT_TREE)


@pytest.mark.parametrize('caller', ['materialize_operation_state','authority_free_static_readiness'])
def test_both_native_call_sites_pass_context_before_effects(monkeypatch, caller):
    c = context()
    class StopBeforeEffects(Exception): pass
    seen=[]
    def sentinel(*a, **kw):
        seen.append(kw['context']); raise StopBeforeEffects
    monkeypatch.setattr(FM, 'authenticate_current_committed_jm_route', sentinel)
    with pytest.raises(StopBeforeEffects):
        if caller == 'materialize_operation_state':
            FM.materialize_operation_state(repository_root=ROOT,context=c,context_source_path=Path('/does-not-exist'))
        else:
            FM.authority_free_static_readiness(repository_root=ROOT,context=c,observed_head=c['repository_head'],observed_tree=c['repository_tree'],repository_clean=True,observed_asset_sha256={})
    assert seen == [c]


def test_selector_and_consumer_semantics_unchanged():
    before = subprocess.check_output(['git','show','ea643f0:'+str(PATH.relative_to(ROOT))],cwd=ROOT,text=True)
    def selector(s):
        return ast.dump(next(n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef) and n.name=='governed_checkout_identity'),include_attributes=False)
    assert selector(before)==selector(PATH.read_text())
    old = subprocess.check_output(['git','show','ea643f0:'+FM.P11_CONSUMER_RELATIVE],cwd=ROOT)
    assert old==(ROOT/FM.P11_CONSUMER_RELATIVE).read_bytes()
