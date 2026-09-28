"""Native FM successor selection; no authority objects or VM execution."""
from copy import deepcopy
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import types

import pytest

ROOT = Path(__file__).resolve().parents[1]
OWNER = ROOT / '.github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py'
spec = importlib.util.spec_from_file_location('successor_bootstrap_fm', OWNER)
FM = importlib.util.module_from_spec(spec)
spec.loader.exec_module(FM)
S0_PATH = ROOT / '.github/governance/evidence/p11_wrong_scope_non_consuming_preflight_v1/live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json'
S0 = FM.fresh_context.load_context(S0_PATH, repository_root=ROOT)
BASELINE = '3abd864a6c780993dca8d0a11375949c4507d19d'


def arguments(directory, vector='WRONG_SCOPE'):
    return dict(repository_root=ROOT, repository_head=S0['repository_head'],
                repository_tree=S0['repository_tree'],
                generation_identity=f'G77_256BT_ONE_FRESH_HUMAN_AUTHORIZED_{vector}_OPERATIONAL_COMMISSIONING_V1',
                operation_identity='G77_256BT_PREFLIGHT_001', identity_namespace_prefix='G77_256BT',
                operation_evidence_root=directory / 'operation_state',
                transient_root=Path('/tmp/g77_256bt_unused'), predecessor_context_path=S0_PATH)


@pytest.fixture
def directory():
    with tempfile.TemporaryDirectory(prefix='g77_256bt_wrong_scope_test_', suffix='_v1',
                                     dir=ROOT / '.github/governance/evidence') as p:
        yield Path(p)


@pytest.fixture
def successor(directory):
    c = FM.build_operation_context(**arguments(directory))
    return c


def reseal(c):
    c = deepcopy(c)
    c.pop('context_sha256')
    return FM.fresh_context.seal_context(c)


def test_native_candidate_bound_derivation_and_seal(successor):
    FM.fresh_context.validate_context(successor, repository_root=ROOT)
    FM.validate_immutable_context_bindings(ROOT, successor)
    b = FM.bootstrap_asset_bindings(successor)
    actual = FM.bootstrap_guest_command_arguments((ROOT / b['cloud_init_path']).read_text(), successor['guest_adapter_binding']['bootstrap_guest_path'])
    assert actual[0] == successor['guest_adapter_binding']['source_sha256']
    assert actual[2:4] == (S0['repository_head'], S0['repository_tree'])
    assert b['seed_sha256'] == FM.sha256_path(Path(b['seed_path']))
    assert successor['context_sha256'] != S0['context_sha256']
    assert FM.sha256_path(S0_PATH) == 'b5eebee7e37c8c0c2ccc64482d64cd0becc7906462e89b792ce6f1320848fa4f'


@pytest.mark.parametrize('field,value', [
    ('adapter', '035c3c02cfb4cee26c6af2501b85a547d0376c80c4df376b7a40a8671277136f'),
    ('head', '0' * 40), ('tree', '0' * 40), ('candidate', '0' * 64),
    ('cloud_hash', '0' * 64), ('seed_hash', '0' * 64), ('seed_path', '/tmp/arbitrary-seed.img'),
])
def test_candidate_context_disagreement_rejected(successor, field, value):
    c = deepcopy(successor)
    if field == 'adapter': c['guest_adapter_binding']['source_sha256'] = value
    elif field in ('head', 'tree'): c['qemu_executable_base_seed_checkout_bindings']['checkout'][field] = value
    elif field == 'candidate': c['candidate_manifest_sha256'] = value
    elif field == 'cloud_hash': c['wrapper_fc_er_che_schema_hashes']['cloud_init'] = value
    elif field == 'seed_hash': c['qemu_executable_base_seed_checkout_bindings']['seed']['sha256'] = value
    else: c['qemu_executable_base_seed_checkout_bindings']['seed']['path'] = value
    c = reseal(c)
    with pytest.raises((RuntimeError, ValueError)):
        FM.validate_immutable_context_bindings(ROOT, c)


@pytest.mark.parametrize('asset', ['cloud', 'seed_content', 'seed_metadata'])
def test_tampered_assets_rejected(successor, asset):
    b = FM.bootstrap_asset_bindings(successor)
    p = ROOT / b['cloud_init_path'] if asset == 'cloud' else Path(b['seed_path'])
    original = p.read_bytes()
    try:
        if asset == 'seed_metadata': changed = original + b'tampered'
        else:
            token = successor['guest_adapter_binding']['source_sha256'].encode()
            assert token in original
            changed = original.replace(token, b'0' * 64)
        p.write_bytes(changed)
        with pytest.raises(RuntimeError): FM.validate_immutable_context_bindings(ROOT, successor)
    finally: p.write_bytes(original)


@pytest.mark.parametrize('vector', ['WRONG_ATTEMPT', 'WRONG_INPUT', 'WRONG_CONTRACT', 'WRONG_PROVENANCE', 'FUTURE', 'EXPIRED', 'UNKNOWN'])
def test_other_vectors_cannot_request_successor_binding(directory, vector):
    with pytest.raises((RuntimeError, ValueError)):
        FM.build_operation_context(**arguments(directory, vector))
    assert not (directory / 'bootstrap').exists()


@pytest.mark.parametrize('field', ['repository_head', 'repository_tree'])
def test_caller_checkout_override_rejected_before_derivation(directory, field):
    kw = arguments(directory)
    kw[field] = '0' * 40
    with pytest.raises(RuntimeError, match='candidate/predecessor'):
        FM.build_operation_context(**kw)
    assert not (directory / 'bootstrap').exists()


def test_arbitrary_candidate_and_hash_api_rejected(directory):
    kw = arguments(directory)
    p = directory / 'untrusted_candidate.json'
    p.write_text('{}')
    with pytest.raises(RuntimeError, match='manifest identity'):
        FM.build_operation_context(**kw, candidate_source_path=p)
    with pytest.raises(TypeError):
        FM.build_operation_context(**kw, adapter_sha256='0' * 64)
    assert not (directory / 'bootstrap').exists()


def test_unauthenticated_predecessor_rejected(directory):
    c = deepcopy(S0)
    c['operation_identity'] += '_UNAUTHENTICATED'
    c['preclaim_temporal_binding']['operation_identity'] = c['operation_identity']
    p = directory / 'untrusted_context.json'
    p.write_bytes(FM.canonical_bytes(reseal(c)))
    kw = arguments(directory)
    kw['predecessor_context_path'] = p
    with pytest.raises(RuntimeError): FM.build_operation_context(**kw)
    assert not (directory / 'bootstrap').exists()


def test_no_overwrite_of_existing_derivation(successor, directory):
    b = FM.bootstrap_asset_bindings(successor)
    before = Path(b['seed_path']).read_bytes()
    with pytest.raises(FileExistsError): FM.build_operation_context(**arguments(directory))
    assert Path(b['seed_path']).read_bytes() == before


def test_all_existing_vector_and_legacy_selections_byte_identical(directory):
    previous = types.ModuleType('baseline_fm')
    previous.__file__ = str(OWNER)
    exec(compile(subprocess.check_output(['git', 'show', BASELINE + ':' + str(OWNER.relative_to(ROOT))], cwd=ROOT), str(OWNER), 'exec'), previous.__dict__)
    for vector in ['WRONG_ATTEMPT', 'WRONG_INPUT', 'WRONG_CONTRACT', 'WRONG_PROVENANCE', 'FUTURE', 'EXPIRED', 'WRONG_SCOPE']:
        assert FM.current_bootstrap_asset_bindings(vector) == previous.current_bootstrap_asset_bindings(vector)
        kw = arguments(directory, vector)
        kw.pop('predecessor_context_path')
        assert FM.build_operation_context(**kw) == previous.build_operation_context(**kw)
    assert FM.bootstrap_asset_bindings({}) == previous.bootstrap_asset_bindings({})
    assert FM.bootstrap_asset_bindings(S0) == previous.bootstrap_asset_bindings(S0)
    FM.validate_immutable_context_bindings(ROOT, S0)
