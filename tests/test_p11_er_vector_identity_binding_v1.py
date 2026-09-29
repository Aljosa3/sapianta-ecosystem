"""Exercise the native ER identity gate; no operation, authority or VM invocation."""
import ast
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
E = Path('.github/governance/evidence')
ER = E/'g77_256er_p11_operational_v1/harness/G77_256ER_P11_OPERATIONAL_HARNESS_V1.py'
FM = E/'g77_256fm_wrong_attempt_preboot_v1/launcher/sapianta_fresh_operation_context_v1.py'
LAUNCH = E/'g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py'
LG = E/'g77_256lg_wrong_scope_existing_route_admission_v1/adapter/G77_256LG_WRONG_SCOPE_VECTOR_ADAPTER_V1.py'
P11 = Path('tests/p11_da_operational_consumer_v1.py')
JM = '4126dd5ad78fffb259625ca1033bb1d5419cc245'
PREFIX = 'G77_256ERIDENTITY'
VECTORS = ('WRONG_ATTEMPT','WRONG_INPUT','WRONG_CONTRACT','WRONG_PROVENANCE','FUTURE','EXPIRED')

def load(path, name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module

def git(root,*args):
    return subprocess.check_output(['git',*args],cwd=root,text=True).strip()

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

@pytest.fixture
def gate(tmp_path,monkeypatch):
    owner=load(ROOT/FM,'identity_owner')
    launcher=load(ROOT/LAUNCH,'identity_launcher')
    checkout=tmp_path/'checkout'
    paths={ER,FM,LG,P11,Path(launcher.CANDIDATE),Path(owner.WRONG_SCOPE_CURRENT_SPECIFICATION_PATH),Path(owner.PRECLAIM_TEMPORAL_SPECIFICATION_PATH)}
    instance=json.loads((ROOT/owner.WRONG_SCOPE_CURRENT_SPECIFICATION_PATH).read_bytes())
    paths.update(map(Path,instance['sources']))
    for vector in (*VECTORS,'WRONG_SCOPE'):
        paths.add(Path(owner.adapter_source_relative_path(f'{PREFIX}_ONE_FRESH_HUMAN_AUTHORIZED_{vector}_OPERATIONAL_COMMISSIONING_V1')))
    for relative in paths:
        target=checkout/relative;target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes((ROOT/relative).read_bytes())
    git(checkout,'init','-q')
    git(checkout,'add','.')
    git(checkout,'-c','user.name=RepositoryProof','-c','user.email=proof@invalid','-c','core.hooksPath=/dev/null','commit','-qm','non-operational identity fixture')
    er=load(checkout/ER,'identity_er')
    context_path=tmp_path/'context.json'
    monkeypatch.setattr(er,'CHECKOUT',checkout)
    monkeypatch.setattr(er,'P11_CONSUMER_PATH',checkout/P11)
    monkeypatch.setattr(er,'FRESH_OPERATION_CONTEXT_OWNER_PATH',checkout/FM)
    monkeypatch.setattr(er,'FRESH_OPERATION_CONTEXT_PATH',context_path)
    # Operational entry points are never admissible in these proofs.
    def forbidden(*args,**kwargs):
        pytest.fail('operational surface reached')
    for name in ('main','append_record','write_canonical','write_canonical_atomic'):
        monkeypatch.setattr(er,name,forbidden)
    def make(vector='WRONG_SCOPE',operation='001'):
        head=git(checkout,'rev-parse','HEAD');tree=git(checkout,'rev-parse','HEAD^{tree}')
        generation=f'{PREFIX}_ONE_FRESH_HUMAN_AUTHORIZED_{vector}_OPERATIONAL_COMMISSIONING_V1'
        hashes={key:'0'*64 for key in ('wrapper','fc_fk_adapter','er_harness','canonical_che','raw_evidence_schema','canonicalizer','cloud_init','fresh_operation_context_owner')}
        hashes['wrapper']=digest(checkout/owner.adapter_source_relative_path(generation))
        hashes['er_harness']=digest(checkout/ER)
        hashes['fresh_operation_context_owner']=digest(checkout/FM)
        bindings={key:{'path':str(tmp_path/key),'sha256':'0'*64} for key in ('qemu_executable','base','seed')}
        bindings['checkout']={'path':str(tmp_path/'transient/checkout'),'head':head,'tree':tree,'detached':True,'clean':True,'read_only_mount':True}
        return owner.build_context(repository_root=checkout,repository_head=head,repository_tree=tree,generation_identity=generation,operation_identity=f'{PREFIX}_REPOSITORY_PROOF_{operation}',identity_namespace_prefix=PREFIX,operation_evidence_root=tmp_path/'evidence',transient_root=tmp_path/'transient',candidate_manifest_sha256='0'*64,wrapper_fc_er_che_schema_hashes=hashes,qemu_executable_base_seed_checkout_bindings=bindings)
    def write(context,reseal=False):
        value=deepcopy(context)
        if reseal:
            value.pop('context_sha256',None);value=owner.seal_context(value)
        context_path.write_bytes(owner.canonical_bytes(value))
        return value
    return er,owner,launcher,checkout,make,write

def test_exact_current_and_active_hash_closure(gate):
    er,owner,launcher,checkout,make,write=gate
    context=write(make())
    assert er.load_authenticated_fresh_operation_context()==context
    assert context['preclaim_temporal_binding']['coordinate_unix_ns']==500
    assert digest(checkout/P11)==er.WRONG_SCOPE_CURRENT_P11_SHA256==launcher.WRONG_SCOPE_CURRENT_CONSUMER_SHA256
    assert digest(checkout/ER)==launcher.ER_HARNESS_SHA256
    lg=load(checkout/LG,'identity_lg')
    assert lg.ER_HARNESS_SHA256==digest(checkout/ER)
    assert digest(checkout/LG)==launcher.WRONG_SCOPE_ADMISSION_ADAPTER_SHA256
    specialized=lg.specialize_er_harness(checkout)
    specialized.CHECKOUT=checkout;specialized.P11_CONSUMER_PATH=checkout/P11
    specialized.FRESH_OPERATION_CONTEXT_OWNER_PATH=checkout/FM
    specialized.FRESH_OPERATION_CONTEXT_PATH=er.FRESH_OPERATION_CONTEXT_PATH
    assert specialized.load_authenticated_fresh_operation_context()==context
    head=git(checkout,'rev-parse','HEAD');tree=git(checkout,'rev-parse','HEAD^{tree}')
    assert launcher.governed_checkout_identity(checkout,'WRONG_SCOPE',head,tree)==(head,tree)

@pytest.mark.parametrize('kind',('old_jm','tampered'))
def test_wrong_scope_rejects_wrong_consumer(gate,kind):
    er,owner,launcher,checkout,make,write=gate
    write(make())
    raw=subprocess.check_output(['git','show',f'{JM}:{P11}'],cwd=ROOT) if kind=='old_jm' else (checkout/P11).read_bytes()+b'\n# tamper\n'
    (checkout/P11).write_bytes(raw)
    with pytest.raises(RuntimeError,match='runtime P11'):
        er.load_authenticated_fresh_operation_context()

@pytest.mark.parametrize('kind',('spec_file','spec_binding','coordinate','context_seal','context_operation','checkout','harness','caller_hash','generation'))
def test_fail_closed_before_identity_acceptance(gate,kind):
    er,owner,launcher,checkout,make,write=gate
    context=make();reseal=True
    if kind=='spec_file':
        (checkout/owner.WRONG_SCOPE_CURRENT_SPECIFICATION_PATH).write_text('{}\n')
    elif kind=='spec_binding':context['preclaim_temporal_binding']['vector_specification_sha256']='0'*64
    elif kind=='coordinate':context['preclaim_temporal_binding']['coordinate_unix_ns']=1000
    elif kind=='context_seal':context['context_sha256']='0'*64;reseal=False
    elif kind=='context_operation':context['operation_identity']=PREFIX+'_REPOSITORY_PROOF_002'
    elif kind=='checkout':context['qemu_executable_base_seed_checkout_bindings']['checkout']['tree']='0'*40
    elif kind=='harness':context['wrapper_fc_er_che_schema_hashes']['er_harness']='0'*64
    elif kind=='caller_hash':context['expected_p11_sha256']=er.WRONG_SCOPE_CURRENT_P11_SHA256
    elif kind=='generation':context['generation_identity']=context['generation_identity'].replace('WRONG_SCOPE','FUTURE')
    write(context,reseal)
    with pytest.raises((RuntimeError, ValueError), match="mismatch|differs from policy output|fields missing|not canonically derived"):
        er.load_authenticated_fresh_operation_context()

@pytest.mark.parametrize('vector',VECTORS)
def test_other_vector_exact_jm_only(gate,vector):
    er,owner,launcher,checkout,make,write=gate
    write(make(vector))
    with pytest.raises(RuntimeError,match='runtime P11'):er.load_authenticated_fresh_operation_context()
    (checkout/P11).write_bytes(subprocess.check_output(['git','show',f'{JM}:{P11}'],cwd=ROOT))
    assert digest(checkout/P11)==er.COMMITTED_JM_P11_SHA256
    assert er.load_authenticated_fresh_operation_context()['preclaim_temporal_binding']['coordinate_unix_ns']==1000

def test_context_immutable_after_authentication(gate):
    er,owner,launcher,checkout,make,write=gate
    write(make());er.load_authenticated_fresh_operation_context()
    write(make(operation='002'))
    with pytest.raises(RuntimeError,match='changed after authentication'):er.load_authenticated_fresh_operation_context()

def test_same_r_committed_bytes_through_native_validator(gate):
    er,owner,launcher,checkout,make,write=gate
    # Recompute R independently, using Git-authenticated consumer and gate bytes,
    # actual owner.load_context and actual ER gate, not a test-result inference.
    for relative in (ER,FM,P11):
        committed=subprocess.check_output(['git','show',f'HEAD:{relative}'],cwd=checkout)
        assert committed==(checkout/relative).read_bytes()
    head=git(checkout,'rev-parse','HEAD');tree=git(checkout,'rev-parse','HEAD^{tree}')
    context=launcher.build_operation_context(repository_root=checkout,repository_head=head,repository_tree=tree,generation_identity=f'{PREFIX}_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_SCOPE_OPERATIONAL_COMMISSIONING_V1',operation_identity=f'{PREFIX}_REPOSITORY_PROOF_001',identity_namespace_prefix=PREFIX,operation_evidence_root=checkout.parent/'evidence',transient_root=checkout.parent/'transient')
    launcher.validate_immutable_context_bindings(checkout,context)
    write(context);result=er.load_authenticated_fresh_operation_context()
    assert result==context and digest(checkout/P11)==launcher.WRONG_SCOPE_CURRENT_CONSUMER_SHA256
    if os.environ.get('P11_SAME_R_EVIDENCE'):
        for relative in (ER,FM,LG,LAUNCH,P11):
            assert subprocess.check_output(['git','show',f'HEAD:{relative}'],cwd=ROOT)==(ROOT/relative).read_bytes()
        record={'schema_id':'P11_ER_VECTOR_IDENTITY_SAME_R_V1','result':'SATISFIED','scope':'REPOSITORY_NON_OPERATIONAL','owner':'EXISTING_FM_CONTEXT_CUSTODY','validator':'ER.load_authenticated_fresh_operation_context','source_head':git(ROOT,'rev-parse','HEAD'),'source_tree':git(ROOT,'rev-parse','HEAD^{tree}'),'consumer_sha256':digest(checkout/P11),'er_sha256':digest(checkout/ER),'context_sha256':context['context_sha256'],'fixture_head':git(checkout,'rev-parse','HEAD'),'fixture_tree':git(checkout,'rev-parse','HEAD^{tree}'),'operational_attempt_count':0,'e05_credit':'12/18','bindings':{str(p):digest(ROOT/p) for p in (ER,FM,LG,LAUNCH,P11)}}
        Path(os.environ['P11_SAME_R_EVIDENCE']).write_text(json.dumps(record,sort_keys=True,separators=(',',':'))+'\n')

def test_no_new_identity_api_or_route():
    source=(ROOT/ER).read_text();tree=ast.parse(source)
    gate=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='load_authenticated_fresh_operation_context')
    assert not gate.args.args and not gate.args.kwonlyargs and gate.args.kwarg is None
    assert source.count('def load_authenticated_fresh_operation_context(')==1
    assert (ROOT/LAUNCH).read_text().count('result = subprocess.run(argv, check=False)')==1
    assert 'PRESERVED_ER_HARNESS_SHA256' in (ROOT/LAUNCH).read_text()

@pytest.mark.parametrize('vector',VECTORS)
def test_fm_preserves_other_vector_er_binding(vector,tmp_path):
    launcher=load(ROOT/LAUNCH,'identity_preserved_launcher')
    context=launcher.build_operation_context(repository_root=ROOT,repository_head=git(ROOT,'rev-parse','HEAD'),repository_tree=git(ROOT,'rev-parse','HEAD^{tree}'),generation_identity=f'{PREFIX}_ONE_FRESH_HUMAN_AUTHORIZED_{vector}_OPERATIONAL_COMMISSIONING_V1',operation_identity=f'{PREFIX}_REPOSITORY_PROOF_001',identity_namespace_prefix=PREFIX,operation_evidence_root=tmp_path/'evidence',transient_root=tmp_path/'transient')
    assert context['wrapper_fc_er_che_schema_hashes']['er_harness']=='c6539d1cc60940b1999956965bff43923a270598a982cd19f976eadec0a93152'
    launcher.validate_immutable_context_bindings(ROOT,context)
