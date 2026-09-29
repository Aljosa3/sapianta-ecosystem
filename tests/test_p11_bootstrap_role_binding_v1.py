"""Native bootstrap certification fixtures; no context/lifecycle/authority creation."""
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile

import pytest

ROOT = Path(__file__).resolve().parents[1]
REL = Path('.github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py')
S2 = ROOT/'.github/governance/evidence/g77_256p11s2_wrong_scope_preparation_v1/live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json'
S1 = ROOT/'.github/governance/evidence/g77_256p11s1_wrong_scope_bootstrap_v1/live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json'


def load():
    spec = importlib.util.spec_from_file_location('bootstrap_role_fm', ROOT/REL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def native(monkeypatch):
    fm = load()
    # Only the reviewed bootstrap projection is invoked, never lifecycle APIs.
    def forbidden(*args, **kwargs):
        pytest.fail('lifecycle/authority/operation API reached')
    for name in ('main', 'materialize_operation_state', 'build_operation_context',
                 'build_authority_handoff', 'write_authority_handoff'):
        monkeypatch.setattr(fm, name, forbidden)
    before = S2.read_bytes()
    with tempfile.TemporaryDirectory(prefix='p11_bootstrap_repository_proof_',
                                    dir=ROOT/'.github/governance/evidence') as directory:
        evidence = Path(directory)
        # Test output only: no operation_state directory or sealed context exists.
        kwargs = dict(repository_root=ROOT, predecessor_context_path=S2,
                      repository_head=fm.git(ROOT, 'rev-parse', 'HEAD'),
                      repository_tree=fm.git(ROOT, 'rev-parse', 'HEAD^{tree}'),
                      operation_evidence_root=evidence/'operation_state')
        yield fm, kwargs, evidence
        assert S2.read_bytes() == before
        assert not (evidence/'operation_state').exists()
        assert not (evidence/'live_binding').exists()


def test_native_s2_to_current_bootstrap(native):
    fm, kwargs, evidence = native
    result = fm.derive_successor_bootstrap(**kwargs)
    sources = fm._successor_bootstrap_sources(ROOT, kwargs['repository_head'], kwargs['repository_tree'])
    assert (ROOT/result['cloud_init_path']).read_bytes() == sources['user-data']
    assert fm.sha256_path(Path(result['seed_path'])) == result['seed_sha256']
    for name, expected in sources.items():
        assert subprocess.check_output(['isoinfo', '-i', result['seed_path'], '-R', '-x', '/'+name], stderr=subprocess.DEVNULL) == expected
    args = fm.bootstrap_guest_command_arguments(sources['user-data'].decode(), '/mnt/dp-harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py')
    assert args[0] == 'b0c9ddb850e9ed975a5cf5ad8ced1319820608dcdd86a5e358da33c423cedde7'
    assert args[2:4] == (kwargs['repository_head'], kwargs['repository_tree'])
    with pytest.raises(FileExistsError):
        fm.derive_successor_bootstrap(**kwargs)


@pytest.mark.parametrize('kind', ['adapter', 'seal', 'coordinate', 'vector', 'unknown_field'])
def test_historical_context_substitution_rejected(native, monkeypatch, kind):
    fm, kwargs, evidence = native
    old = fm.load_json_without_duplicate_keys
    def substituted(path):
        context, raw = old(path)
        if kind == 'adapter':
            context['guest_adapter_binding']['source_sha256'] = '0'*64
        elif kind == 'coordinate':
            context['preclaim_temporal_binding']['coordinate_unix_ns'] = 1000
        elif kind == 'vector':
            context['generation_identity'] = context['generation_identity'].replace('WRONG_SCOPE', 'EXPIRED')
        elif kind == 'unknown_field':
            context['historical_adapter_override'] = '0'*64
        context.pop('context_sha256')
        context = fm.fresh_context.seal_context(context)
        if kind == 'seal':
            context['context_sha256'] = '0'*64
        return context, fm.canonical_bytes(context)
    monkeypatch.setattr(fm, 'load_json_without_duplicate_keys', substituted)
    with pytest.raises(RuntimeError):
        fm.derive_successor_bootstrap(**kwargs)
    assert not (evidence/'bootstrap').exists()


def test_historical_git_adapter_tamper_rejected(native, monkeypatch):
    fm, kwargs, evidence = native
    original = fm._git_tree_entry
    base = json.loads(S2.read_bytes())['repository_head']
    def changed(root, commit, relative):
        entry = original(root, commit, relative)
        if commit == base and relative == fm.fresh_context.WRONG_SCOPE_ADAPTER_SOURCE_RELATIVE_PATH:
            entry = dict(entry, sha256='0'*64)
        return entry
    monkeypatch.setattr(fm, '_git_tree_entry', changed)
    with pytest.raises(RuntimeError, match='historical predecessor asset identity mismatch'):
        fm.derive_successor_bootstrap(**kwargs)
    assert not (evidence/'bootstrap').exists()


@pytest.mark.parametrize('kind', ['introduction', 'lineage', 'rewrite'])
def test_broken_provenance_rejected(native, monkeypatch, kind):
    fm, kwargs, evidence = native
    if kind == 'lineage':
        monkeypatch.setattr(fm, '_is_git_ancestor', lambda *args: False)
    else:
        original = fm.git
        def changed(root, *args):
            if args[0] == 'log' and '--diff-filter=A' in args and kind == 'introduction':
                return ''
            if args[0] == 'log' and '--diff-filter=A' not in args and kind == 'rewrite':
                return kwargs['repository_head']
            return original(root, *args)
        monkeypatch.setattr(fm, 'git', changed)
    with pytest.raises(RuntimeError, match='introduction|lineage|rewrit'):
        fm.derive_successor_bootstrap(**kwargs)
    assert not (evidence/'bootstrap').exists()


@pytest.mark.parametrize('field', ['repository_head', 'repository_tree'])
def test_wrong_current_coordinates_rejected(native, field):
    fm, kwargs, evidence = native
    kwargs[field] = '0'*40
    with pytest.raises(RuntimeError, match='current admitted HEAD/TREE'):
        fm.derive_successor_bootstrap(**kwargs)
    assert not (evidence/'bootstrap').exists()


def test_current_adapter_substitution_rejected(native, monkeypatch):
    fm, kwargs, evidence = native
    original = fm.sha256_path
    adapter = ROOT/fm.fresh_context.WRONG_SCOPE_ADAPTER_SOURCE_RELATIVE_PATH
    monkeypatch.setattr(fm, 'sha256_path', lambda p: '0'*64 if p == adapter else original(p))
    with pytest.raises(RuntimeError, match='WRONG_SCOPE current checkout binding mismatch'):
        fm.derive_successor_bootstrap(**kwargs)
    assert not (evidence/'bootstrap').exists()


@pytest.mark.parametrize('kind', ['specification', 'coordinate'])
def test_current_instance_substitution_rejected(native, monkeypatch, kind):
    fm, kwargs, evidence = native
    original = Path.read_bytes
    spec_path = ROOT/fm.fresh_context.WRONG_SCOPE_CURRENT_SPECIFICATION_PATH
    def altered(path):
        raw = original(path)
        if path == spec_path:
            instance = json.loads(raw)
            if kind == 'coordinate':
                instance['temporal_coordinates']['preclaim_time_unix_ns'] = 1000
            else:
                instance['schema_id'] = 'SUBSTITUTED'
            return fm.canonical_bytes(instance)
        return raw
    monkeypatch.setattr(Path, 'read_bytes', altered)
    with pytest.raises((RuntimeError, ValueError), match='CURRENT instance hash mismatch'):
        fm.derive_successor_bootstrap(**kwargs)
    assert not (evidence/'bootstrap').exists()


def test_historical_s1_remains_authenticated(native):
    fm, kwargs, evidence = native
    kwargs['predecessor_context_path'] = S1
    result = fm.derive_successor_bootstrap(**kwargs)
    assert Path(result['seed_path']).is_file()


def test_same_predecessor_output_namespace_rejected(native):
    fm, kwargs, evidence = native
    kwargs['operation_evidence_root'] = Path(json.loads(S2.read_bytes())['operation_evidence_root'])
    with pytest.raises(RuntimeError, match='candidate/predecessor binding mismatch'):
        fm.derive_successor_bootstrap(**kwargs)


def test_non_wrong_scope_selection_unchanged():
    fm = load()
    old_source = subprocess.check_output(['git', 'show', 'b7f4cb6fe10a5c58133e724c09b7e038a0414277:'+str(REL)], cwd=ROOT)
    import types
    baseline = types.ModuleType('bootstrap_role_baseline')
    baseline.__file__ = str(ROOT/REL)
    exec(compile(old_source, str(ROOT/REL), 'exec'), baseline.__dict__)
    for vector in ('WRONG_ATTEMPT', 'WRONG_INPUT', 'WRONG_CONTRACT', 'WRONG_PROVENANCE', 'FUTURE', 'EXPIRED'):
        assert fm.current_bootstrap_asset_bindings(vector) == baseline.current_bootstrap_asset_bindings(vector)
